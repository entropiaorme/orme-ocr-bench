"""Reporting / analysis for the OCR benchmark sweep.

Reads every per-engine result JSON in ``calibration/bench/results/`` plus
the ground truth, re-scores via the orchestrator's three-tier evaluator,
and emits research-paper-style markdown artefacts under
``calibration/bench/report/``:

- ``leaderboard.md`` — composite ranked table (eff acc + counts + perf).
- ``per_cell_type.md`` — accuracy split by name / level / rank_level / percent.
- ``failure_modes.md`` — hallucinate / drop / substitute / reject per engine.
- ``failure_overlap.md`` — for each cell, how many engines fail on it
  (ensembling-relevant: are failures intrinsically hard or
  engine-specific?).
- ``per_engine/<engine>.md`` — per-engine deep dive (failure samples,
  confidence histogram, perf).

Idempotent: run any time, regenerates all outputs from whatever result
files are present. No subprocess spawning; pure analysis. Safe to run
mid-bench-run to inspect partial results.

Usage::

    python -m backend.ocr.calibration.bench.report
    python -m backend.ocr.calibration.bench.report --engines ppocr,easyocr
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from backend.ocr.calibration.bench.common import (
    BENCH_DIR,
    index_ground_truth,
    load_ground_truth,
    load_vocab,
    results_dir,
)
from backend.ocr.calibration.benchmark_panel_ocr import (
    aggregate_engine_metrics,
    score_engine,
)

REPORT_DIR = BENCH_DIR / "report"


def _load_results(src_dir: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in sorted(src_dir.glob("*.json")):
        engine = path.stem
        if engine == "composite":  # the run's composite summary, not an engine
            continue
        try:
            out[engine] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  skip {engine}: {exc}")
    return out


def _score_all(
    raw_results: dict[str, dict],
    gt_index: dict,
    vocabs: dict[str, list[str]],
) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for engine, raw in raw_results.items():
        try:
            panels_eval = score_engine(raw, gt_index, vocabs)
            agg = aggregate_engine_metrics(raw, panels_eval)
            agg["panels_eval"] = panels_eval
            out[engine] = agg
        except Exception as exc:
            print(f"  score-fail {engine}: {exc}")
    return out


# --- Markdown rendering ------------------------------------------------------


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a list-of-lists as a Markdown pipe table."""
    out = ["| " + " | ".join(headers) + " |"]
    out.append("| " + " | ".join("---" for _ in headers) + " |")
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def _pct(num: float | None) -> str:
    if num is None:
        return "—"
    return f"{num * 100:.1f}%"


def _ms(num: float | None) -> str:
    if num is None:
        return "—"
    return f"{num:.0f}"


def _mb(num: float | None) -> str:
    if num is None:
        return "—"
    return f"{num:.0f}"


_PROVIDER_SHORT = {
    "CUDAExecutionProvider": "CUDA",
    "TensorrtExecutionProvider": "TensorRT",
    "DmlExecutionProvider": "DirectML",
    "CPUExecutionProvider": "CPU",
}


def _device_label(m: dict) -> str:
    """Compact device cell for the leaderboard.

    Prefers the precise ONNX Runtime provider when present (e.g. CUDA,
    DirectML), else the torch-style device string ("cuda"/"cpu"). Legacy
    results without device info fall back to a dash.
    """
    provider = m.get("provider")
    if provider:
        return _PROVIDER_SHORT.get(provider, provider)
    device = m.get("device")
    if device:
        return device.upper() if device == "cpu" else device
    return "—"


# --- Reports -----------------------------------------------------------------


def render_leaderboard(scored: dict[str, dict]) -> str:
    rows = sorted(
        scored.items(),
        key=lambda kv: kv[1].get("effective_accuracy") or 0.0,
        reverse=True,
    )
    headers = [
        "Rank", "Engine", "Eff Acc", "PASS", "REC", "FAIL", "Total",
        "Device", "Mean ms/cell", "Init load (ms)", "RSS warm (MB)", "Wall (s)",
    ]
    table_rows = []
    for i, (engine, m) in enumerate(rows, 1):
        c = m["counts"]
        table_rows.append([
            i,
            f"`{engine}`",
            _pct(m.get("effective_accuracy")),
            c.get("PASS", 0),
            c.get("RECOVERED", 0),
            c.get("UNRECOVERABLE", 0),
            m.get("total", 0),
            _device_label(m),
            f"{m.get('ocr_mean_ms', 0):.1f}",
            _ms(m.get("init_load_ms")),
            _mb(m.get("rss_after_warmup_mb")),
            f"{m.get('subprocess_wall_ms', 0) / 1000:.1f}",
        ])

    body = [
        "# OCR engine leaderboard",
        "",
        "**Corpus:** 12 skill pages + 14 profession pages, 594 graded "
        "data cells (4 cell types: skill name + level; profession name "
        "+ rank_level + percent). Ground truth produced via Frontier-VLM "
        "transcription with screen-verbatim canonical names where "
        "snapshot vocab disagrees.",
        "",
        "**Scoring:** three-tier per cell — PASS (exact match after "
        "strip), RECOVERED (rapidfuzz top-1 against canonical vocab "
        "matches the expected canonical, name cells only), "
        "UNRECOVERABLE (neither). Numeric cells (level / rank_level / "
        "percent) collapse to PASS / UNRECOVERABLE; rapidfuzz isn't "
        "applicable to integers.",
        "",
        "**Effective accuracy** = (PASS + RECOVERED) / total_data_cells. "
        "Non-data rows (`kind=summary` Average rows + `kind=empty` "
        "trailing blanks) are recorded by the engines but excluded "
        "from the denominator.",
        "",
        f"**Engines reported:** {len(rows)} of 28 candidates (others "
        "may be missing if their result JSON hasn't landed yet).",
        "",
        _md_table(headers, table_rows),
    ]
    return "\n".join(body) + "\n"


def render_per_cell_type(scored: dict[str, dict]) -> str:
    cell_types = ["name", "level", "rank_level", "percent"]
    rows = sorted(
        scored.items(),
        key=lambda kv: kv[1].get("effective_accuracy") or 0.0,
        reverse=True,
    )
    headers = ["Engine"] + cell_types + ["Notes"]
    table_rows = []
    for engine, m in rows:
        bct = m.get("by_cell_type", {})
        cells = []
        for cn in cell_types:
            slot = bct.get(cn)
            if not slot:
                cells.append("—")
                continue
            acc = slot.get("effective_accuracy")
            cells.append(_pct(acc))
        # Identify each engine's strongest cell type (signal for ensembling)
        scores = [
            (cn, (bct.get(cn, {}) or {}).get("effective_accuracy") or 0.0)
            for cn in cell_types
        ]
        best = max(scores, key=lambda x: x[1]) if scores else (None, 0)
        worst = min(scores, key=lambda x: x[1]) if scores else (None, 0)
        notes = (
            f"strongest: `{best[0]}` ({_pct(best[1])}) · "
            f"weakest: `{worst[0]}` ({_pct(worst[1])})"
        )
        table_rows.append([f"`{engine}`"] + cells + [notes])

    body = [
        "# Per-cell-type effective accuracy",
        "",
        "Splits effective accuracy by cell type. Useful for spotting "
        "engines that win on names but lose on numerics (or vice "
        "versa) — a strong signal that ensembling could beat any "
        "single-engine pick.",
        "",
        _md_table(headers, table_rows),
    ]
    return "\n".join(body) + "\n"


def render_failure_modes(scored: dict[str, dict]) -> str:
    rows = sorted(
        scored.items(),
        key=lambda kv: kv[1].get("effective_accuracy") or 0.0,
        reverse=True,
    )
    headers = [
        "Engine", "Hallucinate", "Drop", "Substitute", "Reject", "Total fail",
    ]
    table_rows = []
    for engine, m in rows:
        fm = m.get("by_failure_mode", {})
        total_fail = m["counts"].get("UNRECOVERABLE", 0)
        table_rows.append([
            f"`{engine}`",
            fm.get("hallucinate", 0),
            fm.get("drop", 0),
            fm.get("substitute", 0),
            fm.get("reject", 0),
            total_fail,
        ])
    body = [
        "# Failure-mode breakdown",
        "",
        "Heuristic classification of non-PASS cells (UNRECOVERABLE only "
        "— RECOVERED is excluded since fuzzy already saved those):",
        "",
        "- **Hallucinate**: OCR text materially longer than expected "
        "(insertion-heavy)",
        "- **Drop**: OCR text materially shorter than expected (deletion-heavy)",
        "- **Substitute**: similar length to expected, character mismatch",
        "- **Reject**: OCR returned blank / whitespace",
        "",
        "The classifier is length-based with a blank special-case; it's "
        "directional, not precise. Useful for attributing failure "
        "patterns to architectural causes (e.g. small-input "
        "hallucination on autoregressive decoders, drop on CRNN "
        "with insufficient receptive field).",
        "",
        _md_table(headers, table_rows),
    ]
    return "\n".join(body) + "\n"


def render_failure_overlap(scored: dict[str, dict]) -> str:
    """Across engines, count how many engines fail on each cell.

    Cells where many engines fail are 'intrinsically hard' (likely a
    crop/font/layout issue, not a model issue). Cells where only one
    engine fails are 'engine-specific weakness' (ensembling can
    recover them by deferring to a different engine).
    """
    cell_failures: dict[tuple, list[tuple[str, dict]]] = defaultdict(list)
    cell_total: dict[tuple, int] = {}
    n_engines_with_data = 0
    for engine, m in scored.items():
        if "panels_eval" not in m:
            continue
        n_engines_with_data += 1
        for panel_key, ev in m["panels_eval"].items():
            for cell in ev["cells"]:
                key = (
                    panel_key, cell["page_index"], cell["row"], cell["cell"],
                )
                cell_total[key] = cell_total.get(key, 0) + 1
                if cell["status"] != "PASS":
                    cell_failures[key].append((engine, cell))

    overlap_dist: dict[int, int] = defaultdict(int)
    for key, total in cell_total.items():
        n_failed = len(cell_failures.get(key, []))
        overlap_dist[n_failed] += 1

    bar_max = max(overlap_dist.values()) if overlap_dist else 1
    bar_width = 40
    headers = ["# engines failing", "# cells", "share", "bar"]
    bar_rows = []
    for n in sorted(overlap_dist.keys()):
        cnt = overlap_dist[n]
        share = cnt / sum(overlap_dist.values())
        bar = "█" * round(cnt / bar_max * bar_width)
        bar_rows.append([n, cnt, _pct(share), bar])

    # Hard cells (failed by ≥ ceil(N/2) engines)
    threshold = max(1, (n_engines_with_data + 1) // 2)
    hard_cells = [
        (key, fails)
        for key, fails in cell_failures.items()
        if len(fails) >= threshold
    ]
    hard_cells.sort(key=lambda x: -len(x[1]))

    hard_rows = []
    for (panel, page, row, cell), fails in hard_cells[:30]:
        first_fail = fails[0][1]
        expected = first_fail.get("expected", "")
        ocr_samples = ", ".join(
            f"`{repr((f[1].get('got') or f[1].get('ocr_text') or ''))[:40]}`"
            for f in fails[:3]
        )
        hard_rows.append([
            f"{panel} p{page:02d}.r{row:02d}.{cell}",
            len(fails),
            f"`{expected}`",
            ocr_samples,
        ])

    body = [
        "# Failure-cell overlap analysis",
        "",
        f"Engines reporting cells: **{n_engines_with_data}** of "
        f"{len(scored)} engines.",
        "",
        "## Distribution of cell failure across engines",
        "",
        "How many engines fail on each cell? If the distribution skews "
        "toward 'few engines fail' (heavy 0-failures bin), failures are "
        "engine-specific and ensembling helps. If it skews toward "
        "'many engines fail' (heavy high-N-failures tail), some cells "
        "are intrinsically hard and ensembling won't save them.",
        "",
        _md_table(headers, bar_rows),
        "",
        f"## Hardest cells (failed by ≥ {threshold} engines)",
        "",
        f"Top 30 by # failing engines.",
        "",
        _md_table(
            ["Cell", "# fail", "Expected", "Sample OCR (top-3 engines)"],
            hard_rows,
        ),
    ]
    return "\n".join(body) + "\n"


def render_per_engine(engine: str, scored: dict) -> str:
    m = scored
    c = m["counts"]
    fm = m["by_failure_mode"]

    # Pull sample failures
    samples = []
    for panel_key, ev in m.get("panels_eval", {}).items():
        for cell in ev.get("cells", []):
            if cell["status"] != "PASS":
                samples.append((panel_key, cell))
    samples.sort(key=lambda x: x[1].get("ocr_conf") or 0.0)

    sample_rows = []
    for panel, cell in samples[:20]:
        sample_rows.append([
            f"{panel} p{cell.get('page_index'):02d}.r{cell.get('row'):02d}",
            f"`{cell.get('cell')}`",
            cell.get("status", "")[:13],
            cell.get("failure_mode", "—"),
            f"`{cell.get('expected')!r}`",
            f"`{(cell.get('got') or cell.get('ocr_text') or '')!r}`",
            f"{cell.get('ocr_conf', 0):.3f}"
            if cell.get("ocr_conf") is not None else "—",
        ])

    # Confidence distribution buckets
    confs = [
        cell.get("ocr_conf") or 0.0
        for ev in m.get("panels_eval", {}).values()
        for cell in ev.get("cells", [])
        if cell.get("ocr_conf") is not None
    ]
    if confs:
        arr = np.array(confs)
        conf_summary = (
            f"min={arr.min():.3f}  p25={np.percentile(arr, 25):.3f}  "
            f"median={np.median(arr):.3f}  p75={np.percentile(arr, 75):.3f}  "
            f"max={arr.max():.3f}  mean={arr.mean():.3f}"
        )
    else:
        conf_summary = "(no confidence values recorded)"

    body = [
        f"# `{engine}` deep dive",
        "",
        "## Headline",
        "",
        f"- Effective accuracy: **{_pct(m.get('effective_accuracy'))}** "
        f"({c.get('PASS', 0)} PASS + {c.get('RECOVERED', 0)} RECOVERED "
        f"of {m.get('total', 0)} data cells)",
        f"- Failure modes: hallucinate={fm.get('hallucinate', 0)}, "
        f"drop={fm.get('drop', 0)}, substitute={fm.get('substitute', 0)}, "
        f"reject={fm.get('reject', 0)}",
        f"- Per-cell mean: **{m.get('ocr_mean_ms', 0):.1f} ms** "
        f"(p95 {m.get('ocr_p95_ms', 0):.1f} ms, max {m.get('ocr_max_ms', 0):.1f} ms)",
        f"- Init: load {_ms(m.get('init_load_ms'))} ms + "
        f"warmup {_ms(m.get('init_warmup_ms'))} ms",
        f"- RSS: warmup {_mb(m.get('rss_after_warmup_mb'))} MB, "
        f"final {_mb(m.get('final_rss_mb'))} MB",
        f"- Subprocess wall: "
        f"**{m.get('subprocess_wall_ms', 0) / 1000:.1f} s**",
        "",
        "## Confidence distribution",
        "",
        conf_summary,
        "",
        "## Per-cell-type effective accuracy",
        "",
    ]
    bct = m.get("by_cell_type", {})
    bct_rows = []
    for cn in ["name", "level", "rank_level", "percent"]:
        slot = bct.get(cn)
        if not slot:
            bct_rows.append([f"`{cn}`", "—", "—", "—"])
            continue
        bct_rows.append([
            f"`{cn}`",
            _pct(slot.get("effective_accuracy")),
            f"{slot['counts'].get('PASS', 0)}+{slot['counts'].get('RECOVERED', 0)}",
            slot.get("total", 0),
        ])
    body.append(_md_table(["Cell type", "Eff acc", "PASS+REC", "Total"], bct_rows))
    body += [
        "",
        "## Failure samples (lowest 20 by confidence)",
        "",
    ]
    if sample_rows:
        body.append(_md_table(
            ["Cell", "Field", "Status", "Mode", "Expected", "OCR", "Conf"],
            sample_rows,
        ))
    else:
        body.append("*No failures (or no confidence data) to sample.*")

    return "\n".join(body) + "\n"


# --- Driver ------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--engines",
        default=None,
        help="Restrict report to a comma-separated subset.",
    )
    parser.add_argument(
        "--results-subdir",
        default=None,
        help=(
            "Render the report for one execution-provider track: read "
            "results/<subdir>/ and write report/<subdir>/. Omit for the "
            "legacy bare results/ -> report/ set."
        ),
    )
    args = parser.parse_args()

    src_dir = results_dir(args.results_subdir)
    report_dir = REPORT_DIR / args.results_subdir if args.results_subdir else REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "per_engine").mkdir(exist_ok=True)

    print(f"Loading results from {src_dir}")
    raw = _load_results(src_dir)
    if args.engines:
        wanted = {e.strip() for e in args.engines.split(",") if e.strip()}
        raw = {k: v for k, v in raw.items() if k in wanted}
    print(f"  found {len(raw)} engine result file(s)")

    gt = load_ground_truth()
    if gt is None:
        raise SystemExit("No ground truth at calibration/bench/ground_truth.json")
    gt_index = index_ground_truth(gt)
    panel_keys = list(gt.get("panels", {}).keys())
    vocabs = {p: load_vocab(p) for p in panel_keys}

    print("Scoring all engine results...")
    scored = _score_all(raw, gt_index, vocabs)
    print(f"  scored {len(scored)} engine(s)")

    print("Rendering reports...")
    (report_dir / "leaderboard.md").write_text(
        render_leaderboard(scored), encoding="utf-8",
    )
    (report_dir / "per_cell_type.md").write_text(
        render_per_cell_type(scored), encoding="utf-8",
    )
    (report_dir / "failure_modes.md").write_text(
        render_failure_modes(scored), encoding="utf-8",
    )
    (report_dir / "failure_overlap.md").write_text(
        render_failure_overlap(scored), encoding="utf-8",
    )
    for engine, m in scored.items():
        (report_dir / "per_engine" / f"{engine}.md").write_text(
            render_per_engine(engine, m), encoding="utf-8",
        )

    print(f"\nReports under: {report_dir}")
    print(f"  leaderboard.md       (composite ranked table)")
    print(f"  per_cell_type.md     (accuracy by name/level/rank_level/percent)")
    print(f"  failure_modes.md     (hallucinate/drop/substitute/reject per engine)")
    print(f"  failure_overlap.md   (which cells fail across engines — ensembling signal)")
    print(f"  per_engine/<eng>.md  ({len(scored)} per-engine deep dives)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
