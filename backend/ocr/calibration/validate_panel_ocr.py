"""One-shot validation of the local OCR pipeline against a live EU panel.

Run as:
    .venv/Scripts/python.exe -m backend.ocr.calibration.validate_panel_ocr skill
    .venv/Scripts/python.exe -m backend.ocr.calibration.validate_panel_ocr profession
    .venv/Scripts/python.exe -m backend.ocr.calibration.validate_panel_ocr both

Counts down 10s, captures the panel via ``*_region()`` plus mss, slices into
per-cell BGR crops using ``backend/data/panel_geometry.json``, runs PP-OCR on
each cell (skipping bar cells), fuzzy-matches name cells against the canonical
vocab snapshots in ``backend/data/snapshot/``, and regex-parses numeric cells.

Prints per-row recognised text, top-3 fuzzy candidates, and parsed numerics so
the user can eyeball whether OCR is producing sensible output. Also prints a
detailed timing and resource breakdown (per-step latency, per-cell-type OCR
distribution, RSS / heap deltas) so we get a full "how it works" picture before
committing to a full implementation.

If ``calibration/validate/ground_truth.json`` exists at the worktree root, the
script additionally compares per-cell OCR output against the ground truth and
emits a qualitative scorecard categorising each cell as PASS / RECOVERED /
RECOVERABLE / UNRECOVERABLE. Failed cell crops are written to
``calibration/validate/snippets/<panel>/<canonical>-<cell>.png`` for visual
inspection. PASS cells are not written (those are perfect by definition).

In addition to stdout, writes a structured JSON report to
``calibration/validate/result.json`` at the worktree root (overwritten each
run) so the user can share the run with the agent verbatim for review.

This is a calibration-only tool: no app integration, no feature flag.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator

import cv2
import mss
import numpy as np
from rapidfuzz import fuzz, process

from backend.ocr.ppocr_rec_reader import PPocrRecReader
from backend.services.scan_presets import profession_region, skill_region

try:
    import psutil

    _PROC = psutil.Process()
except ModuleNotFoundError:
    _PROC = None

GEOMETRY_PATH = Path(__file__).resolve().parents[2] / "data" / "panel_geometry.json"
SNAPSHOT_DIR = Path(__file__).resolve().parents[2] / "data" / "snapshot"
VALIDATE_DIR = Path(__file__).resolve().parents[3] / "calibration" / "validate"
RESULT_PATH = VALIDATE_DIR / "result.json"
GROUND_TRUTH_PATH = VALIDATE_DIR / "ground_truth.json"
SNIPPETS_DIR = VALIDATE_DIR / "snippets"

COUNTDOWN_SECONDS = 10
TOP_N = 3
SCORER = fuzz.WRatio  # general-purpose default; the scoring step picks the canon scorer
SCORER_NAME = "WRatio"
PERCENT_TOLERANCE = 0.05  # game shows one decimal; allow tiny float-roundtrip slack

LEVEL_RE = re.compile(r"\d+")
RANK_LEVEL_RE = re.compile(r"(\d+)\s*$")
PERCENT_RE = re.compile(r"(\d+(?:\.\d)?)\s*%?")
FILENAME_UNSAFE_RE = re.compile(r'[<>:"/\\|?*]')

_REGION_FNS: dict[str, Callable[[], tuple[list[int], list[int]] | None]] = {
    "skill": skill_region,
    "profession": profession_region,
}


# --- Timing & resource utilities ------------------------------------------------


@contextmanager
def timed_ms() -> Iterator[list[float]]:
    """Yield a one-element list; on exit element 0 is elapsed milliseconds."""
    t0 = time.perf_counter_ns()
    out: list[float] = []
    try:
        yield out
    finally:
        out.append((time.perf_counter_ns() - t0) / 1e6)


def rss_mb() -> float | None:
    if _PROC is None:
        return None
    return _PROC.memory_info().rss / 1024 / 1024


def heap_mb() -> tuple[float, float]:
    cur, peak = tracemalloc.get_traced_memory()
    return cur / 1024 / 1024, peak / 1024 / 1024


def fmt_mb(value: float | None) -> str:
    return f"{value:.1f} MB" if value is not None else "n/a"


def fmt_delta_mb(before: float | None, after: float | None) -> str:
    if before is None or after is None:
        return "n/a"
    return f"{after - before:+.1f} MB"


def stats(values: list[float]) -> str:
    if not values:
        return "(no samples)"
    arr = np.array(values)
    return (
        f"n={len(values):2d} total={arr.sum():6.1f}ms "
        f"mean={arr.mean():5.1f} p50={np.median(arr):5.1f} "
        f"p95={np.percentile(arr, 95):5.1f} max={arr.max():5.1f}"
    )


# --- Geometry & vocab ----------------------------------------------------------


def load_geometry(panel_key: str) -> dict:
    if not GEOMETRY_PATH.exists():
        raise SystemExit(f"No calibration file at {GEOMETRY_PATH}.")
    data = json.loads(GEOMETRY_PATH.read_text(encoding="utf-8"))
    if panel_key not in data:
        raise SystemExit(f"No '{panel_key}' entry in {GEOMETRY_PATH}.")
    return data[panel_key]


def load_vocab(panel_key: str) -> list[str]:
    fname = "skills.json" if panel_key == "skill" else "professions.json"
    path = SNAPSHOT_DIR / fname
    data = json.loads(path.read_text(encoding="utf-8"))
    return [entry["name"] for entry in data]


# --- Capture & slicing ---------------------------------------------------------


def countdown(panel_key: str) -> None:
    print(f"\n--- {panel_key.upper()} PANEL ---")
    print(f"Make the {panel_key} panel visible.")
    for s in range(COUNTDOWN_SECONDS, 0, -1):
        print(f"  {s}...")
        time.sleep(1)
    print("CAPTURING")


def capture_panel_bgr(panel_key: str) -> np.ndarray:
    """Capture the panel as a BGR ndarray, no PNG round-trip."""
    region = _REGION_FNS[panel_key]()
    if region is None:
        raise SystemExit(
            f"EU window not found or {panel_key} region uncomputable. Start EU first."
        )
    tl, br = region
    monitor = {
        "left": tl[0],
        "top": tl[1],
        "width": br[0] - tl[0],
        "height": br[1] - tl[1],
    }
    with mss.mss() as sct:
        shot = sct.grab(monitor)
        arr = np.frombuffer(shot.bgra, dtype=np.uint8).reshape(
            shot.height, shot.width, 4,
        )
        return arr[:, :, :3].copy()


def slice_cells(
    panel_bgr: np.ndarray, geom: dict,
) -> dict[tuple[int, str], np.ndarray]:
    n_rows: int = geom["n_rows"]
    cells: dict[str, dict] = geom["cells"]
    out: dict[tuple[int, str], np.ndarray] = {}
    for r in range(n_rows):
        for cell_name, cell in cells.items():
            first = cell["first_y_top"]
            last = cell["last_y_top"]
            y_top = (
                round(first + r * (last - first) / (n_rows - 1))
                if n_rows > 1
                else first
            )
            y_bot = y_top + cell["height"]
            crop = panel_bgr[y_top:y_bot, cell["x_left"]:cell["x_right"]]
            out[(r, cell_name)] = crop
    return out


# --- Per-cell parsing ----------------------------------------------------------


def fuzzy_top(query: str, vocab: list[str]) -> list[tuple[str, float]]:
    results = process.extract(query, vocab, scorer=SCORER, limit=TOP_N)
    return [(canon, float(score)) for canon, score, _ in results]


def parse_level(text: str) -> int | None:
    m = LEVEL_RE.search(text)
    return int(m.group()) if m else None


def parse_rank_level(text: str) -> int | None:
    m = RANK_LEVEL_RE.search(text)
    return int(m.group(1)) if m else None


def parse_percent(text: str) -> float | None:
    m = PERCENT_RE.search(text)
    return float(m.group(1)) if m else None


# --- Per-panel pipeline --------------------------------------------------------


@dataclass
class PanelTimings:
    capture_ms: float = 0.0
    slice_ms: float = 0.0
    panel_width: int = 0
    panel_height: int = 0
    ocr_per_cell_type_ms: dict[str, list[float]] = field(default_factory=dict)
    fuzzy_ms: list[float] = field(default_factory=list)
    parse_ms: list[float] = field(default_factory=list)
    pipeline_wall_ms: float = 0.0
    rss_before_mb: float | None = None
    rss_after_mb: float | None = None
    heap_current_mb: float = 0.0
    heap_peak_mb: float = 0.0
    n_rows: int = 0
    cell_names: list[str] = field(default_factory=list)
    rows: list[dict] = field(default_factory=list)


def _ms_distribution(values: list[float]) -> dict | None:
    if not values:
        return None
    arr = np.array(values)
    return {
        "n": len(values),
        "total_ms": float(arr.sum()),
        "mean_ms": float(arr.mean()),
        "p50_ms": float(np.median(arr)),
        "p95_ms": float(np.percentile(arr, 95)),
        "max_ms": float(arr.max()),
        "samples_ms": [float(v) for v in values],
    }


def panel_to_json(timings: PanelTimings) -> dict:
    return {
        "panel_width": timings.panel_width,
        "panel_height": timings.panel_height,
        "n_rows": timings.n_rows,
        "cell_names": timings.cell_names,
        "capture_ms": timings.capture_ms,
        "slice_ms": timings.slice_ms,
        "pipeline_wall_ms": timings.pipeline_wall_ms,
        "rss_before_mb": timings.rss_before_mb,
        "rss_after_mb": timings.rss_after_mb,
        "rss_delta_mb": (
            timings.rss_after_mb - timings.rss_before_mb
            if timings.rss_after_mb is not None and timings.rss_before_mb is not None
            else None
        ),
        "heap_current_mb": timings.heap_current_mb,
        "heap_peak_mb": timings.heap_peak_mb,
        "ocr_per_cell_type": {
            cn: _ms_distribution(times)
            for cn, times in timings.ocr_per_cell_type_ms.items()
            if times
        },
        "fuzzy": _ms_distribution(timings.fuzzy_ms),
        "regex": _ms_distribution(timings.parse_ms),
        "rows": timings.rows,
    }


def run_panel(
    panel_key: str, reader: PPocrRecReader, vocab: list[str],
) -> tuple[PanelTimings, dict[tuple[int, str], np.ndarray]]:
    geom = load_geometry(panel_key)
    countdown(panel_key)

    timings = PanelTimings()
    timings.rss_before_mb = rss_mb()
    pipeline_t0 = time.perf_counter_ns()

    with timed_ms() as t:
        panel_bgr = capture_panel_bgr(panel_key)
    timings.capture_ms = t[0]
    timings.panel_height = panel_bgr.shape[0]
    timings.panel_width = panel_bgr.shape[1]
    print(
        f"\nCaptured {timings.panel_width}x{timings.panel_height} BGR "
        f"in {timings.capture_ms:.1f} ms"
    )

    with timed_ms() as t:
        crops = slice_cells(panel_bgr, geom)
    timings.slice_ms = t[0]
    print(f"Sliced {len(crops)} cells in {timings.slice_ms:.2f} ms\n")

    n_rows = geom["n_rows"]
    cell_names = list(geom["cells"].keys())
    timings.n_rows = n_rows
    timings.cell_names = cell_names

    for r in range(n_rows):
        print(f"row {r:02d}:")
        row_record: dict = {"row": r, "cells": {}}
        for cell_name in cell_names:
            crop = crops[(r, cell_name)]
            timings.ocr_per_cell_type_ms.setdefault(cell_name, [])

            if cell_name == "bar":
                row_record["cells"][cell_name] = {"skipped": True}
                print(f"  {cell_name:11s} <skipped: bar reading deferred>")
                continue

            with timed_ms() as t:
                text, conf = reader.read_text(crop)
            ocr_ms = t[0]
            timings.ocr_per_cell_type_ms[cell_name].append(ocr_ms)

            text_disp = repr(text)
            if len(text_disp) > 30:
                text_disp = text_disp[:27] + "...'"

            cell_record: dict = {
                "ocr_text": text,
                "ocr_conf": conf,
                "ocr_ms": ocr_ms,
            }

            if cell_name == "name":
                with timed_ms() as t:
                    cands = fuzzy_top(text, vocab)
                timings.fuzzy_ms.append(t[0])
                cell_record["fuzzy_ms"] = t[0]
                cell_record["fuzzy_top"] = [
                    {"canonical": c, "score": s} for c, s in cands
                ]
                cand_str = ", ".join(f"{c!r} ({s:.1f})" for c, s in cands)
                print(
                    f"  {cell_name:11s} ocr={text_disp:32s} conf={conf:.3f} "
                    f"ocr={ocr_ms:5.1f}ms fuzzy={t[0]:.2f}ms"
                )
                print(f"              top-{TOP_N}: {cand_str}")
            elif cell_name == "level":
                with timed_ms() as t:
                    parsed = parse_level(text)
                timings.parse_ms.append(t[0])
                cell_record["parse_ms"] = t[0]
                cell_record["parsed"] = parsed
                print(
                    f"  {cell_name:11s} ocr={text_disp:32s} conf={conf:.3f} "
                    f"ocr={ocr_ms:5.1f}ms | int={parsed}"
                )
            elif cell_name == "rank_level":
                with timed_ms() as t:
                    parsed = parse_rank_level(text)
                timings.parse_ms.append(t[0])
                cell_record["parse_ms"] = t[0]
                cell_record["parsed_level"] = parsed
                print(
                    f"  {cell_name:11s} ocr={text_disp:32s} conf={conf:.3f} "
                    f"ocr={ocr_ms:5.1f}ms | level={parsed}"
                )
            elif cell_name == "percent":
                with timed_ms() as t:
                    parsed = parse_percent(text)
                timings.parse_ms.append(t[0])
                cell_record["parse_ms"] = t[0]
                cell_record["parsed_percent"] = parsed
                print(
                    f"  {cell_name:11s} ocr={text_disp:32s} conf={conf:.3f} "
                    f"ocr={ocr_ms:5.1f}ms | pct={parsed}"
                )
            else:
                cell_record["note"] = "no parser for cell type"
                print(
                    f"  {cell_name:11s} ocr={text_disp:32s} conf={conf:.3f} "
                    f"ocr={ocr_ms:5.1f}ms | <no parser>"
                )

            row_record["cells"][cell_name] = cell_record
        timings.rows.append(row_record)

    timings.pipeline_wall_ms = (time.perf_counter_ns() - pipeline_t0) / 1e6
    timings.rss_after_mb = rss_mb()
    timings.heap_current_mb, timings.heap_peak_mb = heap_mb()

    print(f"\n=== {panel_key.upper()} TIMING & RESOURCES ===")
    print(f"  capture:   {timings.capture_ms:6.2f} ms")
    print(f"  slice:     {timings.slice_ms:6.2f} ms")
    for cn, times in timings.ocr_per_cell_type_ms.items():
        if times:
            print(f"  ocr[{cn:11s}] {stats(times)}")
    if timings.fuzzy_ms:
        print(f"  fuzzy        {stats(timings.fuzzy_ms)}")
    if timings.parse_ms:
        print(f"  regex        {stats(timings.parse_ms)}")
    print(f"  pipeline wall (countdown excluded): {timings.pipeline_wall_ms:.1f} ms")
    print(
        f"  RSS:       before={fmt_mb(timings.rss_before_mb)} "
        f"after={fmt_mb(timings.rss_after_mb)} "
        f"delta={fmt_delta_mb(timings.rss_before_mb, timings.rss_after_mb)}"
    )
    print(
        f"  Heap:      current={timings.heap_current_mb:.1f} MB "
        f"peak={timings.heap_peak_mb:.1f} MB"
    )

    return timings, crops


# --- Qualitative evaluation against ground truth -------------------------------


# Cell suffix used in snippet filenames. The user-facing convention treats the
# profession ``rank_level`` cell as a "level" cell (it carries the level number
# the pipeline cares about) and the ``percent`` cell as "progress".
_FILENAME_CELL_SUFFIX = {
    "name": "name",
    "level": "level",
    "rank_level": "level",
    "percent": "progress",
}


def _safe_filename(s: str) -> str:
    """Convert a canonical name to a filesystem-friendly basename component."""
    s = re.sub(r"\s+", "_", s.strip())
    s = FILENAME_UNSAFE_RE.sub("", s)
    return s or "_unnamed"


def load_ground_truth() -> dict | None:
    if not GROUND_TRUTH_PATH.exists():
        return None
    return json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))


def _evaluate_name(cell_record: dict, expected: str) -> dict:
    """Compare a name cell. PASS / RECOVERED (fuzzy top-1) / RECOVERABLE / UNRECOVERABLE."""
    ocr_text = cell_record["ocr_text"]
    fuzzy_top = cell_record.get("fuzzy_top", [])
    candidates = [c["canonical"] for c in fuzzy_top]
    if ocr_text == expected:
        return {"status": "PASS", "expected": expected, "got": ocr_text}
    if candidates and candidates[0] == expected:
        return {
            "status": "RECOVERED",
            "expected": expected,
            "got": ocr_text,
            "fuzzy_rank": 1,
            "fuzzy_score": fuzzy_top[0]["score"],
            "detail": "fuzzy top-1 matched canonical",
        }
    if expected in candidates:
        rank = candidates.index(expected) + 1
        return {
            "status": "RECOVERABLE",
            "expected": expected,
            "got": ocr_text,
            "fuzzy_rank": rank,
            "fuzzy_score": fuzzy_top[rank - 1]["score"],
            "detail": f"canonical present at fuzzy rank {rank}",
        }
    return {
        "status": "UNRECOVERABLE",
        "expected": expected,
        "got": ocr_text,
        "fuzzy_top": candidates,
        "detail": f"canonical not in fuzzy top-{len(candidates)}",
    }


def _evaluate_int(cell_record: dict, parsed_field: str, expected: int) -> dict:
    parsed = cell_record.get(parsed_field)
    if parsed == expected:
        return {"status": "PASS", "expected": expected, "got": parsed}
    return {
        "status": "UNRECOVERABLE",
        "expected": expected,
        "got": parsed,
        "ocr_text": cell_record["ocr_text"],
        "detail": f"parsed {parsed!r} from OCR text {cell_record['ocr_text']!r}",
    }


def _evaluate_percent(cell_record: dict, expected: float) -> dict:
    parsed = cell_record.get("parsed_percent")
    if parsed is not None and abs(parsed - expected) <= PERCENT_TOLERANCE:
        return {"status": "PASS", "expected": expected, "got": parsed}
    return {
        "status": "UNRECOVERABLE",
        "expected": expected,
        "got": parsed,
        "ocr_text": cell_record["ocr_text"],
        "detail": f"parsed {parsed!r} from OCR text {cell_record['ocr_text']!r}",
    }


def evaluate_panel(
    panel_key: str,
    timings: PanelTimings,
    crops: dict[tuple[int, str], np.ndarray],
    ground_truth_panel: dict,
) -> dict:
    """Compare per-cell OCR against ground truth, save non-PASS snippets,
    print scorecard, return evaluation block for the JSON report."""
    gt_rows = ground_truth_panel["rows"]
    if len(gt_rows) != timings.n_rows:
        print(
            f"\nWARNING: ground truth has {len(gt_rows)} rows but {panel_key} "
            f"panel captured {timings.n_rows} rows. Comparing the overlap only."
        )

    snippets_panel_dir = SNIPPETS_DIR / panel_key
    if snippets_panel_dir.exists():
        shutil.rmtree(snippets_panel_dir)
    snippets_panel_dir.mkdir(parents=True, exist_ok=True)

    cell_evals: list[dict] = []
    snippets_written: list[str] = []

    n_compare = min(len(gt_rows), len(timings.rows))
    for r in range(n_compare):
        ocr_row = timings.rows[r]
        gt_row = gt_rows[r]
        canonical = gt_row.get("name") or "_unknown"
        canonical_safe = _safe_filename(canonical)

        for cell_name, cell_record in ocr_row["cells"].items():
            if cell_record.get("skipped"):
                continue

            if cell_name == "name":
                eval_result = _evaluate_name(cell_record, gt_row["name"])
            elif cell_name == "level":
                eval_result = _evaluate_int(cell_record, "parsed", gt_row["level"])
            elif cell_name == "rank_level":
                eval_result = _evaluate_int(
                    cell_record, "parsed_level", gt_row["level"],
                )
            elif cell_name == "percent":
                eval_result = _evaluate_percent(cell_record, gt_row["percent"])
            else:
                continue

            eval_result["row"] = r
            eval_result["cell"] = cell_name
            eval_result["canonical"] = canonical
            cell_evals.append(eval_result)

            # Write a snippet for any non-PASS cell so the user can inspect
            # what went wrong. PASS cells were perfect — no need to clutter
            # the snippets dir.
            if eval_result["status"] != "PASS":
                suffix = _FILENAME_CELL_SUFFIX.get(cell_name, cell_name)
                fname = f"{canonical_safe}-{suffix}.png"
                path = snippets_panel_dir / fname
                cv2.imwrite(str(path), crops[(r, cell_name)])
                eval_result["snippet"] = str(path.relative_to(VALIDATE_DIR))
                snippets_written.append(fname)

    counts = {"PASS": 0, "RECOVERED": 0, "RECOVERABLE": 0, "UNRECOVERABLE": 0}
    for ev in cell_evals:
        counts[ev["status"]] += 1
    total = len(cell_evals)

    def pct(n: int) -> str:
        return f"{n / total * 100:5.1f}%" if total else "  n/a"

    print(f"\n=== {panel_key.upper()} SCORECARD ===")
    print(f"  Cells evaluated:  {total} (rows × non-bar cells)")
    print(f"  PASS:             {counts['PASS']:3d} ({pct(counts['PASS'])})")
    print(f"  RECOVERED:        {counts['RECOVERED']:3d} ({pct(counts['RECOVERED'])})  "
          f"-- fuzzy top-1 matched")
    print(f"  RECOVERABLE:      {counts['RECOVERABLE']:3d} ({pct(counts['RECOVERABLE'])})  "
          f"-- canonical was in fuzzy top-{TOP_N}")
    print(f"  UNRECOVERABLE:    {counts['UNRECOVERABLE']:3d} ({pct(counts['UNRECOVERABLE'])})")
    if total:
        eff = counts["PASS"] + counts["RECOVERED"]
        bes = eff + counts["RECOVERABLE"]
        print(f"  Effective accuracy (PASS + RECOVERED):       {eff}/{total} "
              f"= {eff / total * 100:.1f}%")
        print(f"  Best-effort accuracy (+ RECOVERABLE):        {bes}/{total} "
              f"= {bes / total * 100:.1f}%")

    failures = [ev for ev in cell_evals if ev["status"] != "PASS"]
    if failures:
        print(f"\n  Failures ({len(failures)}):")
        for ev in failures:
            head = (
                f"    row {ev['row']:02d} / {ev['cell']:11s} [{ev['status']:14s}] "
                f"expected={ev['expected']!r}"
            )
            if ev["status"] == "RECOVERED":
                print(
                    f"{head}  ocr={ev['got']!r}  fuzzy_top1='{ev['expected']}' "
                    f"({ev['fuzzy_score']:.1f})"
                )
            elif ev["status"] == "RECOVERABLE":
                print(
                    f"{head}  ocr={ev['got']!r}  fuzzy_rank={ev['fuzzy_rank']} "
                    f"(score {ev['fuzzy_score']:.1f})"
                )
            else:
                print(f"{head}  got={ev.get('got')!r}  ({ev.get('detail', '')})")

    if snippets_written:
        print(
            f"\n  Wrote {len(snippets_written)} non-PASS snippet(s) to "
            f"{snippets_panel_dir.relative_to(VALIDATE_DIR.parent.parent)}/"
        )

    return {
        "counts": counts,
        "total": total,
        "effective_accuracy": (
            (counts["PASS"] + counts["RECOVERED"]) / total if total else None
        ),
        "best_effort_accuracy": (
            (counts["PASS"] + counts["RECOVERED"] + counts["RECOVERABLE"]) / total
            if total
            else None
        ),
        "cells": cell_evals,
        "snippets_dir": str(snippets_panel_dir.relative_to(VALIDATE_DIR.parent.parent)),
    }


# --- Init phase ----------------------------------------------------------------


@dataclass
class InitTimings:
    reader_load_ms: float = 0.0
    warmup_ms: float = 0.0
    vocab_load_ms: float = 0.0
    rss_init_mb: float | None = None
    rss_after_load_mb: float | None = None
    rss_after_warmup_mb: float | None = None


def init(panels: list[str]) -> tuple[PPocrRecReader, dict[str, list[str]], InitTimings]:
    timings = InitTimings()
    timings.rss_init_mb = rss_mb()

    print("=== INIT ===")
    print(
        f"  psutil: {'available' if _PROC is not None else 'NOT installed (RSS unavailable; pip install psutil)'}"
    )
    print(f"  init RSS: {fmt_mb(timings.rss_init_mb)}")

    with timed_ms() as t:
        reader = PPocrRecReader()
    timings.reader_load_ms = t[0]
    timings.rss_after_load_mb = rss_mb()
    print(
        f"  PP-OCR load: {timings.reader_load_ms:.1f} ms "
        f"(RSS now {fmt_mb(timings.rss_after_load_mb)}, "
        f"delta {fmt_delta_mb(timings.rss_init_mb, timings.rss_after_load_mb)})"
    )

    with timed_ms() as t:
        reader.warm_up()
    timings.warmup_ms = t[0]
    timings.rss_after_warmup_mb = rss_mb()
    print(
        f"  warm-up (3 dummy passes): {timings.warmup_ms:.1f} ms "
        f"(RSS now {fmt_mb(timings.rss_after_warmup_mb)}, "
        f"delta {fmt_delta_mb(timings.rss_after_load_mb, timings.rss_after_warmup_mb)})"
    )

    vocabs: dict[str, list[str]] = {}
    with timed_ms() as t:
        for p in panels:
            vocabs[p] = load_vocab(p)
    timings.vocab_load_ms = t[0]
    sizes = ", ".join(f"{p}={len(v)}" for p, v in vocabs.items())
    print(f"  vocab load ({sizes}): {timings.vocab_load_ms:.2f} ms")

    return reader, vocabs, timings


# --- Main ----------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the local OCR pipeline against a live EU panel.",
    )
    parser.add_argument(
        "panel",
        choices=["skill", "profession", "both"],
        help="Panel(s) to validate.",
    )
    args = parser.parse_args()

    panels = ["skill", "profession"] if args.panel == "both" else [args.panel]

    ground_truth = load_ground_truth()
    if ground_truth is not None:
        print(f"Ground truth loaded from {GROUND_TRUTH_PATH.name}; will score panels.")
    else:
        print(
            f"No ground_truth.json at {GROUND_TRUTH_PATH}; running OCR + perf only "
            f"(scorecard skipped)."
        )

    tracemalloc.start()
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    overall_t0 = time.perf_counter_ns()

    reader, vocabs, init_timings = init(panels)

    panel_timings: dict[str, PanelTimings] = {}
    panel_evaluations: dict[str, dict] = {}
    for p in panels:
        timings, crops = run_panel(p, reader, vocabs[p])
        panel_timings[p] = timings
        if ground_truth is not None and p in ground_truth:
            panel_evaluations[p] = evaluate_panel(p, timings, crops, ground_truth[p])

    overall_ms = (time.perf_counter_ns() - overall_t0) / 1e6
    overall_ms_excl_countdowns = overall_ms - COUNTDOWN_SECONDS * 1000.0 * len(panels)
    final_rss = rss_mb()
    final_heap_cur, final_heap_peak = heap_mb()

    print("\n=== OVERALL ===")
    print(
        f"  init total: "
        f"{init_timings.reader_load_ms + init_timings.warmup_ms + init_timings.vocab_load_ms:.1f} ms "
        f"(load={init_timings.reader_load_ms:.1f}, warmup={init_timings.warmup_ms:.1f}, "
        f"vocab={init_timings.vocab_load_ms:.2f})"
    )
    for p, t in panel_timings.items():
        print(
            f"  {p}: pipeline wall {t.pipeline_wall_ms:.1f} ms "
            f"(capture {t.capture_ms:.1f}, slice {t.slice_ms:.2f}, "
            f"ocr-sum "
            f"{sum(sum(v) for v in t.ocr_per_cell_type_ms.values()):.1f})"
        )
    print(
        f"  total wall (init + panels, countdowns excluded): "
        f"{overall_ms_excl_countdowns:.1f} ms "
        f"(raw incl. countdowns: {overall_ms:.0f} ms)"
    )
    print(f"  final RSS: {fmt_mb(final_rss)}")
    print(
        f"  final heap: current={final_heap_cur:.1f} MB peak={final_heap_peak:.1f} MB"
    )

    if panel_evaluations:
        agg_counts = {"PASS": 0, "RECOVERED": 0, "RECOVERABLE": 0, "UNRECOVERABLE": 0}
        agg_total = 0
        for ev_panel in panel_evaluations.values():
            agg_total += ev_panel["total"]
            for k in agg_counts:
                agg_counts[k] += ev_panel["counts"][k]
        if agg_total:
            eff = agg_counts["PASS"] + agg_counts["RECOVERED"]
            bes = eff + agg_counts["RECOVERABLE"]
            print(
                f"\n  combined scorecard: PASS {agg_counts['PASS']} / "
                f"RECOVERED {agg_counts['RECOVERED']} / "
                f"RECOVERABLE {agg_counts['RECOVERABLE']} / "
                f"UNRECOVERABLE {agg_counts['UNRECOVERABLE']} "
                f"(of {agg_total})"
            )
            print(
                f"  effective accuracy: {eff}/{agg_total} = {eff / agg_total * 100:.1f}%  "
                f"|  best-effort: {bes}/{agg_total} = {bes / agg_total * 100:.1f}%"
            )

    report = {
        "version": 1,
        "started_at": started_at,
        "scorer": SCORER_NAME,
        "countdown_seconds": COUNTDOWN_SECONDS,
        "have_psutil": _PROC is not None,
        "init": {
            "rss_init_mb": init_timings.rss_init_mb,
            "reader_load_ms": init_timings.reader_load_ms,
            "rss_after_load_mb": init_timings.rss_after_load_mb,
            "warmup_ms": init_timings.warmup_ms,
            "rss_after_warmup_mb": init_timings.rss_after_warmup_mb,
            "vocab_load_ms": init_timings.vocab_load_ms,
            "vocab_sizes": {p: len(vocabs[p]) for p in panels},
        },
        "panels": {p: panel_to_json(panel_timings[p]) for p in panels},
        "evaluation": (panel_evaluations or None),
        "overall": {
            "total_wall_ms_incl_countdowns": overall_ms,
            "total_wall_ms_excl_countdowns": overall_ms_excl_countdowns,
            "final_rss_mb": final_rss,
            "final_heap_current_mb": final_heap_cur,
            "final_heap_peak_mb": final_heap_peak,
        },
    }

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nWrote JSON report to {RESULT_PATH}")

    tracemalloc.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
