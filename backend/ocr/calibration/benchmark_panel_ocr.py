"""OCR benchmark orchestrator.

Compares N candidate OCR engines against the same captured panel corpus
(skill: 12 pages, profession: 14 pages), scores each against the
multi-page ground truth, and emits a side-by-side composite report.

Each engine runs in its own subprocess via
``backend.ocr.calibration.bench.runner`` for clean perf isolation
(torch / onnxruntime / tesseract don't interfere with each others'
warmup state, GPU memory, or thread pools).

Three-tier scoring per cell (PASS / RECOVERED / UNRECOVERABLE) on
``kind=data`` rows only; ``kind=summary`` (Average) and ``kind=empty``
rows are recorded by engines but excluded from accuracy denominators.

Usage::

    # 1) Capture the corpus from the live EU client (one-time per bench run)
    python -m backend.ocr.calibration.bench.capture both

    # 2) Produce ground truth (sibling Claude Code instance or other VLM)
    #    -> writes calibration/bench/ground_truth.json

    # 3) Orchestrate engines, score, and emit composite + per-engine results
    python -m backend.ocr.calibration.benchmark_panel_ocr
    python -m backend.ocr.calibration.benchmark_panel_ocr --engines easyocr,ppocr
    python -m backend.ocr.calibration.benchmark_panel_ocr --skip-existing
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

from backend.ocr.calibration.bench.common import (
    BENCH_DIR,
    MANIFEST_PATH,
    WORKTREE_ROOT,
    composite_path,
    results_dir,
    evaluate_int,
    evaluate_name,
    evaluate_percent,
    index_ground_truth,
    load_ground_truth,
    load_vocab,
    parse_level,
    parse_percent,
    parse_rank_level,
    tag_failure_mode,
)
from backend.ocr.calibration.bench.runner import discover_engine_keys

RUNNER_MODULE = "backend.ocr.calibration.bench.runner"
ENGINE_VENVS_PATH = BENCH_DIR / "engine_venvs.json"

# --- Tier presets ----------------------------------------------------------
#
# Curated engine subsets for different run tracks. The user runs from
# fastest tier upward, with --skip-existing carrying earlier-tier results
# forward. Precise membership is a research-design choice, edited here
# deliberately (not in JSON) since each tier reflects a structural claim
# about the engine's compute path.

# Engines verified to run via DirectML on AMD/Windows — ONNX Runtime route
# with the DML execution provider. PaddleOCR family (Agent 1) uses the
# same onnxruntime-directml backend the existing ppocr adapter does;
# Agent 2's OnnxTR family explicitly swapped to onnxruntime-directml at
# install time and confirmed DmlExecutionProvider is the active provider.
TIER_GPU = [
    "ppocr",
    "ppocrv5_mobile",
    "ppocrv5_en_mobile",
    "ppocrv5_latin_mobile",
    "ppocrv5_server",
    "rapidocr",
    "onnxtr_crnn_mobile",
    "onnxtr_parseq",
    "onnxtr_vitstr",
    "onnxtr_viptr",
    "onnxtr_sar",
    "onnxtr_master",
]

# Fast track: GPU set + the CPU engines that are still genuinely quick
# (under ~90s subprocess wall) and headline-relevant per the engine
# survey. openocr_svtrv2 is the strongest CTC candidate on the
# shortlist; tesseract + easyocr are the classic baselines.
TIER_FAST = TIER_GPU + [
    "openocr_svtrv2",
    "tesseract",
    "easyocr",
]

# Ship-decision tier for v0.1.0: the 5+2 shortlist that survives the
# combined license / deployment / healthcheck filter. Five primary
# candidates (ship-clean Apache 2.0, deploy-tractable model size, sub-
# 10s init, exact or near-exact read on the smoke crop) plus the two
# classic baselines kept for comparison (already cached so --skip-
# existing carries them through for free). The winner of this tier is the
# v0.1.0 ship pick. The exhaustive bench across all 28 engines
# is parked for a Linux+AMD or NVIDIA box post-v0.1.0.
TIER_SHIP = [
    # Primary candidates
    "openocr_svtrv2",
    "ppocrv5_en_mobile",
    "ppocrv5_latin_mobile",
    "rapidocr",
    "onnxtr_parseq",
    # Free baselines (already cached)
    "ppocr",
    "easyocr",
]

# Slow tier: PyTorch + transformers VLMs and the MMOCR family. These run
# CPU-only on AMD/Windows (DirectML+PyTorch isn't viable for the venv
# Python versions in use here) and are the overnight cook.
TIER_VLM = [
    "trocr",
    "trocr_large_printed",
    "donut",
    "nougat",
    "mmocr_abinet",
    "mmocr_robustscanner",
    "mmocr_satrn",
    "florence2_base",
    "florence2_large",
    "surya",
    "got_ocr2",
    "kosmos25",
    "dots_ocr",
]

TIER_PRESETS: dict[str, list[str]] = {
    "ship": TIER_SHIP,
    "gpu": TIER_GPU,
    "fast": TIER_FAST,
    "vlm": TIER_VLM,
}


def load_engine_runtime_config() -> tuple[dict[str, str], dict[str, str]]:
    """Read calibration/bench/engine_venvs.json and return
    ``(python_overrides, global_env)``. Python overrides map engine key to
    absolute interpreter path; global_env is merged into every spawned
    subprocess's environment (used for HF_HOME, etc).
    """
    if not ENGINE_VENVS_PATH.exists():
        return {}, {}
    data = json.loads(ENGINE_VENVS_PATH.read_text(encoding="utf-8"))
    overrides: dict[str, str] = {}
    for engine, raw in (data.get("engines") or {}).items():
        path = Path(raw)
        if not path.is_absolute():
            # Make absolute against the repo root, but do NOT resolve symlinks:
            # a POSIX venv's bin/python is a symlink back to the base
            # interpreter, and dereferencing it (Path.resolve) would run the
            # engine under the base environment instead of the venv, losing all
            # the venv's installed deps (ModuleNotFoundError: cv2, etc).
            path = Path(os.path.normpath(WORKTREE_ROOT / path))
        overrides[engine] = str(path)
    global_env_raw = data.get("global_env") or {}
    global_env = {
        k: str(v) for k, v in global_env_raw.items() if not k.startswith("_")
    }
    return overrides, global_env


def run_engine_subprocess(
    engine: str,
    python_overrides: dict[str, str],
    global_env: dict[str, str],
    progress: tuple[int, int] | None = None,
    results_subdir: str | None = None,
) -> dict:
    py = python_overrides.get(engine, sys.executable)
    counter = ""
    if progress is not None:
        idx, total = progress
        counter = f" [engine {idx}/{total}]"
    print(
        f"\n=== Launching {engine}{counter} subprocess "
        f"(python={Path(py).parent.parent.name}) ===",
        flush=True,
    )
    t0 = time.perf_counter_ns()
    if not Path(py).exists():
        print(
            f"=== {engine} skipped: python interpreter not found at {py} ===",
            flush=True,
        )
        return {
            "engine": engine,
            "subprocess_wall_ms": 0.0,
            "exit_code": 127,
            "skipped": True,
            "skip_reason": f"missing interpreter {py}",
        }
    sub_env = os.environ.copy()
    sub_env.update(global_env)
    cmd = [py, "-m", RUNNER_MODULE, "--engine", engine]
    if results_subdir:
        cmd += ["--results-subdir", results_subdir]
    proc = subprocess.run(
        cmd,
        check=False,
        cwd=str(WORKTREE_ROOT),
        env=sub_env,
    )
    wall_ms = (time.perf_counter_ns() - t0) / 1e6
    print(
        f"=== {engine} subprocess exit={proc.returncode} "
        f"wall={wall_ms:.1f}ms ===",
        flush=True,
    )
    return {
        "engine": engine,
        "subprocess_wall_ms": wall_ms,
        "exit_code": proc.returncode,
        "python": py,
    }


def _score_data_cell(
    cell_name: str,
    ocr_text: str,
    gt_row: dict,
    vocab: list[str],
) -> dict | None:
    """Run the cell-type-specific scorer; return None if there's no expected
    value to score against (numeric ground truth missing)."""
    if cell_name == "name":
        return evaluate_name(ocr_text, gt_row.get("name", ""), vocab)
    if cell_name == "level":
        parsed = parse_level(ocr_text)
        expected = parse_level(gt_row.get("level"))
        if expected is None:
            return None
        return evaluate_int(ocr_text, parsed, expected)
    if cell_name == "rank_level":
        parsed = parse_rank_level(ocr_text)
        expected = parse_rank_level(gt_row.get("rank_level"))
        if expected is None:
            return None
        return evaluate_int(ocr_text, parsed, expected)
    if cell_name == "percent":
        parsed = parse_percent(ocr_text)
        expected = parse_percent(gt_row.get("percent"))
        if expected is None:
            return None
        return evaluate_percent(ocr_text, parsed, expected)
    return None


def score_engine(
    engine_result: dict,
    gt_index: dict[tuple[str, int, int], dict],
    vocabs: dict[str, list[str]],
) -> dict:
    """Apply parsing + three-tier scoring against ground truth.

    Returns a dict keyed by panel with cell-level evaluation lists
    plus per-panel rollups. Only ``kind=data`` rows count toward
    accuracy; ``summary`` and ``empty`` rows are recorded separately.
    """
    panels_eval: dict[str, dict] = {}
    for panel_key, panel_data in engine_result["panels"].items():
        vocab = vocabs.get(panel_key, [])
        cells: list[dict] = []
        non_data_cells: list[dict] = []
        ocr_ms_values: list[float] = []
        per_cell_type_counts: dict[str, dict[str, int]] = defaultdict(
            lambda: {"PASS": 0, "RECOVERED": 0, "UNRECOVERABLE": 0},
        )
        per_cell_type_totals: dict[str, int] = defaultdict(int)

        for page in panel_data.get("pages", []):
            page_idx = page["page_index"]
            for ocr_row in page["rows"]:
                r = ocr_row["row"]
                gt_row = gt_index.get((panel_key, page_idx, r))
                kind = (gt_row or {}).get("kind", "data")
                for cn, cr in ocr_row["cells"].items():
                    base = {
                        "panel": panel_key,
                        "page_index": page_idx,
                        "row": r,
                        "cell": cn,
                        "kind": kind,
                        "ocr_text": cr.get("ocr_text"),
                        "ocr_conf": cr.get("ocr_conf"),
                        "ocr_ms": cr.get("ocr_ms"),
                    }
                    ocr_ms_values.append(cr.get("ocr_ms") or 0.0)
                    if kind != "data":
                        # Record but don't grade. Carry expected text
                        # so a later analysis can ask "what did the
                        # engine read on Average rows?" without the
                        # bench scoring it.
                        base["expected_raw"] = (gt_row or {}).get(cn)
                        non_data_cells.append(base)
                        continue

                    ev = _score_data_cell(
                        cn, cr.get("ocr_text") or "", gt_row or {}, vocab,
                    )
                    if ev is None:
                        # No expected value to grade; treat as non-data.
                        base["expected_raw"] = (gt_row or {}).get(cn)
                        non_data_cells.append(base)
                        continue
                    if ev["status"] != "PASS":
                        ev["failure_mode"] = tag_failure_mode(
                            cr.get("ocr_text") or "",
                            str((gt_row or {}).get(cn) or ""),
                        )
                    cell_eval = {**base, **ev}
                    cells.append(cell_eval)
                    per_cell_type_counts[cn][ev["status"]] += 1
                    per_cell_type_totals[cn] += 1

        counts = {"PASS": 0, "RECOVERED": 0, "UNRECOVERABLE": 0}
        for ev in cells:
            counts[ev["status"]] += 1
        total = len(cells)
        panels_eval[panel_key] = {
            "counts": counts,
            "total": total,
            "effective_accuracy": (
                (counts["PASS"] + counts["RECOVERED"]) / total
                if total else None
            ),
            "by_cell_type": {
                cn: {
                    "counts": dict(per_cell_type_counts[cn]),
                    "total": per_cell_type_totals[cn],
                    "effective_accuracy": (
                        (per_cell_type_counts[cn]["PASS"]
                         + per_cell_type_counts[cn]["RECOVERED"])
                        / per_cell_type_totals[cn]
                    ) if per_cell_type_totals[cn] else None,
                }
                for cn in per_cell_type_totals
            },
            "by_failure_mode": _failure_mode_breakdown(cells),
            "cells": cells,
            "non_data_cells": non_data_cells,
            "panel_wall_ms": panel_data.get("panel_wall_ms"),
            "ocr_per_cell_type": panel_data.get("ocr_per_cell_type"),
            "rss_after_panel_mb": panel_data.get("rss_after_panel_mb"),
        }
    return panels_eval


def _failure_mode_breakdown(cells: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {
        "hallucinate": 0, "drop": 0, "substitute": 0, "reject": 0,
    }
    for c in cells:
        if c["status"] == "PASS":
            continue
        mode = c.get("failure_mode")
        if mode in out:
            out[mode] += 1
    return out


def aggregate_engine_metrics(engine_result: dict, panels_eval: dict) -> dict:
    """Roll up engine totals across panels."""
    agg = {"PASS": 0, "RECOVERED": 0, "UNRECOVERABLE": 0}
    total = 0
    all_ocr_ms: list[float] = []
    all_failure_modes: dict[str, int] = {
        "hallucinate": 0, "drop": 0, "substitute": 0, "reject": 0,
    }
    by_cell_type_agg: dict[str, dict] = {}
    non_data_count = 0
    for panel_key, ev in panels_eval.items():
        total += ev["total"]
        for k in agg:
            agg[k] += ev["counts"][k]
        for cell in ev["cells"]:
            all_ocr_ms.append(cell.get("ocr_ms") or 0.0)
        for k, v in ev["by_failure_mode"].items():
            all_failure_modes[k] = all_failure_modes.get(k, 0) + v
        for cn, ct in ev["by_cell_type"].items():
            slot = by_cell_type_agg.setdefault(
                cn,
                {"counts": {"PASS": 0, "RECOVERED": 0, "UNRECOVERABLE": 0},
                 "total": 0},
            )
            for status, cnt in ct["counts"].items():
                slot["counts"][status] = slot["counts"].get(status, 0) + cnt
            slot["total"] += ct["total"]
        non_data_count += len(ev.get("non_data_cells", []))
    for cn, slot in by_cell_type_agg.items():
        t = slot["total"]
        slot["effective_accuracy"] = (
            (slot["counts"]["PASS"] + slot["counts"]["RECOVERED"]) / t
            if t else None
        )

    eff = agg["PASS"] + agg["RECOVERED"]
    arr = np.array(all_ocr_ms) if all_ocr_ms else np.zeros(0)
    return {
        "counts": agg,
        "total": total,
        "non_data_cells": non_data_count,
        "effective_accuracy": eff / total if total else None,
        "by_cell_type": by_cell_type_agg,
        "by_failure_mode": all_failure_modes,
        "ocr_total_ms": float(arr.sum()) if arr.size else 0.0,
        "ocr_mean_ms": float(arr.mean()) if arr.size else 0.0,
        "ocr_p95_ms": float(np.percentile(arr, 95)) if arr.size else 0.0,
        "ocr_max_ms": float(arr.max()) if arr.size else 0.0,
        "init_load_ms": engine_result["init"]["load_ms"],
        "init_warmup_ms": engine_result["init"]["warmup_ms"],
        "rss_init_mb": engine_result["init"]["rss_init_mb"],
        "rss_after_warmup_mb": engine_result["init"]["rss_after_warmup_mb"],
        # Optional: present on results produced after the device-aware
        # harness change; legacy result JSONs omit them (default below).
        "device": engine_result["init"].get("device", "cpu"),
        "provider": engine_result["init"].get("provider"),
        "final_rss_mb": engine_result["overall"]["final_rss_mb"],
        "subprocess_wall_ms": engine_result["overall"]["subprocess_wall_ms"],
        # Latency-instrumentation fields (present after the timer-split / VRAM /
        # batched-mode changes; older results omit them, hence .get).
        "peak_vram_mb": engine_result["overall"].get("peak_vram_mb"),
        "timing_split": engine_result["overall"].get("timing_split"),
        "mode": engine_result.get("mode", "serial"),
        "batch_size": engine_result.get("batch_size", 1),
        "throughput_cells_per_s": engine_result["overall"].get("throughput_cells_per_s"),
        "mean_ms_per_cell_batched": engine_result["overall"].get("mean_ms_per_cell_batched"),
    }


# --- Reporting ---------------------------------------------------------------


def print_composite_table(per_engine: dict[str, dict]) -> None:
    print("\n=== COMPOSITE BENCHMARK ===\n")
    cols = list(per_engine.keys())
    width = 14

    def row(label: str, values: list[str]) -> None:
        head = f"{label:30s}"
        cells = "".join(f" {v:>{width}s}" for v in values)
        print(head + cells)

    row("metric", cols)
    print("-" * (30 + (width + 1) * len(cols)))

    fields = [
        ("PASS",                 lambda m: f"{m['counts']['PASS']:d}/{m['total']:d}"),
        ("RECOVERED",            lambda m: f"{m['counts']['RECOVERED']:d}"),
        ("UNRECOVERABLE",        lambda m: f"{m['counts']['UNRECOVERABLE']:d}"),
        ("Effective accuracy",   lambda m: f"{(m['effective_accuracy'] or 0) * 100:.1f}%"),
        ("Hallucinate",          lambda m: f"{m['by_failure_mode'].get('hallucinate', 0):d}"),
        ("Drop",                 lambda m: f"{m['by_failure_mode'].get('drop', 0):d}"),
        ("Substitute",           lambda m: f"{m['by_failure_mode'].get('substitute', 0):d}"),
        ("Reject",               lambda m: f"{m['by_failure_mode'].get('reject', 0):d}"),
        ("Init load (ms)",       lambda m: f"{m['init_load_ms']:.0f}"),
        ("Init warmup (ms)",     lambda m: f"{m['init_warmup_ms']:.0f}"),
        ("RSS post-warmup (MB)", lambda m: f"{(m['rss_after_warmup_mb'] or 0):.0f}"),
        ("Final RSS (MB)",       lambda m: f"{(m['final_rss_mb'] or 0):.0f}"),
        ("Per-cell mean (ms)",   lambda m: f"{m['ocr_mean_ms']:.1f}"),
        ("Per-cell p95 (ms)",    lambda m: f"{m['ocr_p95_ms']:.1f}"),
        ("Per-cell max (ms)",    lambda m: f"{m['ocr_max_ms']:.1f}"),
        ("OCR total (s)",        lambda m: f"{m['ocr_total_ms']/1000:.1f}"),
        ("Subprocess wall (s)",  lambda m: f"{m['subprocess_wall_ms']/1000:.1f}"),
    ]
    for label, fmt in fields:
        row(label, [fmt(per_engine[c]) for c in cols])
    print()


def print_per_cell_type_table(per_engine: dict[str, dict]) -> None:
    print("\n=== PER-CELL-TYPE EFFECTIVE ACCURACY ===\n")
    cols = list(per_engine.keys())
    width = 14
    cell_types: list[str] = []
    for m in per_engine.values():
        for cn in m["by_cell_type"]:
            if cn not in cell_types:
                cell_types.append(cn)

    head = f"{'cell':30s}" + "".join(f" {c:>{width}s}" for c in cols)
    print(head)
    print("-" * len(head))
    for cn in cell_types:
        cells_out = []
        for c in cols:
            slot = per_engine[c]["by_cell_type"].get(cn)
            if slot is None:
                cells_out.append("--")
                continue
            acc = (slot["effective_accuracy"] or 0) * 100
            cells_out.append(f"{acc:5.1f}%  ({slot['counts']['PASS']}+{slot['counts']['RECOVERED']}/{slot['total']})")
        print(f"{cn:30s}" + "".join(f" {v:>{width}s}" for v in cells_out))


def print_failures(per_engine: dict[str, dict], cap_per_engine: int = 30) -> None:
    for engine, m in per_engine.items():
        failures = []
        for panel_key, ev in m["panels_eval"].items():
            for cell in ev["cells"]:
                if cell["status"] != "PASS":
                    failures.append((panel_key, cell))
        if not failures:
            continue
        print(f"\n--- {engine.upper()} failures ({len(failures)}) ---")
        for panel_key, cell in failures[:cap_per_engine]:
            head = (
                f"  {panel_key} p{cell['page_index']:02d} r{cell['row']:02d} "
                f"{cell['cell']:11s} [{cell['status']:13s}]"
                f" mode={cell.get('failure_mode', '-'):10s}"
                f" expected={cell.get('expected')!r}"
            )
            if cell["status"] == "RECOVERED":
                print(
                    f"{head} ocr={cell.get('got')!r} "
                    f"fuzzy_score={cell.get('fuzzy_score', 0):.1f}",
                )
            else:
                print(
                    f"{head} ocr={cell.get('got') or cell.get('ocr_text')!r}",
                )
        if len(failures) > cap_per_engine:
            print(f"  ... +{len(failures) - cap_per_engine} more")


# --- Persistence -------------------------------------------------------------


def _persist_summary(
    engines: list[str],
    subprocess_meta: dict,
    per_engine: dict[str, dict],
    overall_ms: float,
    out_path: Path,
) -> None:
    """Write a slim composite summary; full per-cell detail lives in
    ``calibration/bench/results/<engine>.json``."""
    persist = {
        "engines": engines,
        "subprocess_meta": subprocess_meta,
        "per_engine_summary": {
            e: {
                k: v
                for k, v in m.items()
                if k != "panels_eval"
            }
            | {
                "panels_eval": {
                    p: {
                        kk: vv
                        for kk, vv in pe.items()
                        if kk not in ("cells", "non_data_cells")
                    }
                    for p, pe in m["panels_eval"].items()
                }
            }
            for e, m in per_engine.items()
        },
        "orchestration_wall_ms": overall_ms,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(persist, indent=2), encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the OCR benchmark across N engines and emit a composite report.",
    )
    available = discover_engine_keys()
    parser.add_argument(
        "--engines",
        default=None,
        help=(
            "Comma-separated subset of engines. Mutually exclusive with "
            "--tier; if neither is given, all discoverable engines run. "
            f"Currently discoverable: {','.join(available)}"
        ),
    )
    parser.add_argument(
        "--tier",
        choices=sorted(TIER_PRESETS.keys()),
        default=None,
        help=(
            "Run a curated tier preset. `ship` = v0.1.0 ship-decision "
            "shortlist (5 candidates + 2 baselines, ~30-45 min wall), "
            "`gpu` = DirectML-routed engines, "
            "`fast` = gpu + cheap CPU baselines, "
            "`vlm` = the slow PyTorch/transformers tier. Mutually "
            "exclusive with --engines."
        ),
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip an engine if its result file already exists in calibration/bench/results/.",
    )
    parser.add_argument(
        "--results-subdir",
        default=None,
        help=(
            "Read/write results under results/<subdir>/ instead of bare "
            "results/. Use one subdir per execution-provider track (e.g. "
            "'cuda' for the unconstrained NVIDIA breadth run, 'directml' "
            "for the in-domain Windows run) so the two leaderboards coexist."
        ),
    )
    args = parser.parse_args()
    out_dir = results_dir(args.results_subdir)
    comp_path = composite_path(args.results_subdir)

    if args.engines and args.tier:
        raise SystemExit("--engines and --tier are mutually exclusive.")
    if args.tier:
        engines = list(TIER_PRESETS[args.tier])
    elif args.engines:
        engines = [e.strip() for e in args.engines.split(",") if e.strip()]
    else:
        engines = list(available)
    unknown = [e for e in engines if e not in available]
    if unknown:
        raise SystemExit(
            f"Unknown engine(s) {unknown}. Discoverable: {available}",
        )

    if not MANIFEST_PATH.exists():
        raise SystemExit(
            f"No manifest at {MANIFEST_PATH}. Run capture first:\n"
            f"  python -m backend.ocr.calibration.bench.capture both",
        )

    ground_truth = load_ground_truth()
    if ground_truth is None:
        raise SystemExit(
            "No ground truth at calibration/bench/ground_truth.json. "
            "Produce one first.",
        )
    gt_index = index_ground_truth(ground_truth)
    panel_keys = list(ground_truth.get("panels", {}).keys())
    vocabs = {p: load_vocab(p) for p in panel_keys}

    BENCH_DIR.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    python_overrides, global_env = load_engine_runtime_config()
    if global_env:
        print(
            "Global env additions for subprocesses: "
            + ", ".join(f"{k}={v}" for k, v in global_env.items()),
            flush=True,
        )
    overall_t0 = time.perf_counter_ns()
    subprocess_meta: dict[str, dict] = {}
    n_total = len(engines)
    for idx, engine in enumerate(engines, 1):
        result_path = out_dir / f"{engine}.json"
        if args.skip_existing and result_path.exists():
            print(
                f"\n[engine {idx}/{n_total}] {engine}: result exists, "
                f"skipping (--skip-existing)",
                flush=True,
            )
            subprocess_meta[engine] = {
                "engine": engine,
                "subprocess_wall_ms": 0.0,
                "exit_code": 0,
                "skipped": True,
            }
            continue
        meta = run_engine_subprocess(
            engine, python_overrides, global_env,
            progress=(idx, n_total),
            results_subdir=args.results_subdir,
        )
        subprocess_meta[engine] = meta
        if meta["exit_code"] != 0:
            print(
                f"\nNOTE: {engine} subprocess exited non-zero "
                f"({meta['exit_code']}). Continuing with remaining engines; "
                f"{engine} will be skipped from scoring. Inspect its "
                f"subprocess output above for the failure reason.",
                flush=True,
            )

    per_engine: dict[str, dict] = {}
    for engine in engines:
        result_path = out_dir / f"{engine}.json"
        if not result_path.exists():
            print(f"\n[{engine}] no result file; skipping scoring")
            continue
        if subprocess_meta[engine]["exit_code"] != 0:
            print(
                f"\n[{engine}] subprocess exited non-zero "
                f"({subprocess_meta[engine]['exit_code']}); skipping scoring",
            )
            continue
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if result.get("status") == "failed":
            print(
                f"\n[{engine}] did not complete "
                f"({result.get('skip_reason', 'failed')[:120]}); "
                f"recorded, skipped from scoring",
            )
            continue
        panels_eval = score_engine(result, gt_index, vocabs)
        agg = aggregate_engine_metrics(result, panels_eval)
        agg["panels_eval"] = panels_eval
        agg["raw_init"] = result["init"]
        agg["raw_overall"] = result["overall"]
        per_engine[engine] = agg

    overall_ms = (time.perf_counter_ns() - overall_t0) / 1e6

    if not per_engine:
        print("\nNo successful engine results to compare.")
        return 1

    print_composite_table(per_engine)
    print_per_cell_type_table(per_engine)
    print_failures(per_engine)
    print(f"\nTotal orchestration wall: {overall_ms / 1000:.1f} s")

    _persist_summary(engines, subprocess_meta, per_engine, overall_ms, comp_path)
    print(f"\nWrote composite summary: {comp_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
