"""Per-engine bench runner.

Invoked as a subprocess by the orchestrator. Loads one engine, walks the
multi-page manifest, runs OCR on each cell crop, and writes a JSON result
file at ``calibration/bench/results/<engine>.json``.

Doing this in a subprocess gives clean perf isolation between engines:
torch, onnxruntime, and tesseract don't interfere with each others'
warmup state, GPU memory, or thread pools.

Output schema (mirrors the manifest's panel/page/row/cell shape so the
orchestrator can join 1:1 against ground truth)::

    {
      "engine": "<name>",
      "init": {load_ms, warmup_ms, rss_*},
      "panels": {
        "<panel_key>": {
          "n_rows": N,
          "cell_names": [...],
          "pages": [
            {
              "page_index": N,
              "rows": [
                {
                  "row": R,
                  "cells": {
                    "<cell_name>": {ocr_text, ocr_conf, ocr_ms}
                  }
                }
              ],
              "panel_wall_ms": ...
            }
          ],
          "ocr_per_cell_type": {...}
        }
      },
      "overall": {subprocess_wall_ms, final_rss_mb, heap_*}
    }

Usage (typically called by benchmark_panel_ocr.py, not directly)::

    python -m backend.ocr.calibration.bench.runner --engine ppocr
"""

from __future__ import annotations

import argparse
import importlib
import json
import time
import tracemalloc
from pathlib import Path

import cv2

from backend.ocr.calibration.bench.common import (
    CROPS_DIR,
    MANIFEST_PATH,
    heap_mb,
    ms_distribution,
    results_dir,
    rss_mb,
    timed_ms,
)
from backend.ocr.calibration.bench.engines.base import OCREngine

ENGINES_PKG = "backend.ocr.calibration.bench.engines"
ENGINES_DIR = Path(__file__).resolve().parent / "engines"


def discover_engine_keys() -> list[str]:
    """Walk ``engines/*_engine.py`` and return engine keys (filename stem
    minus the ``_engine`` suffix), without importing the modules.

    Filename convention: each engine adapter lives at
    ``engines/<key>_engine.py`` and exports a top-level ``ENGINE``
    attribute pointing at the engine class. Discovery is filename-driven
    so multiple parallel sessions can drop new adapters into ``engines/``
    without ever touching this module.
    """
    keys = []
    for path in sorted(ENGINES_DIR.glob("*_engine.py")):
        stem = path.stem
        if stem.startswith("_") or stem == "base":
            continue
        if not stem.endswith("_engine"):
            continue
        keys.append(stem[: -len("_engine")])
    return keys


def _fmt_eta(seconds: float) -> str:
    if seconds < 0 or seconds != seconds:  # NaN guard
        return "?"
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        return f"{seconds / 60:.1f}m"
    return f"{seconds / 3600:.1f}h"


def load_engine(name: str) -> OCREngine:
    """Import ``engines/<name>_engine.py`` and instantiate its ``ENGINE`` class.

    The module must export a top-level ``ENGINE`` attribute (the class to
    instantiate). The class itself must subclass :class:`OCREngine`.
    """
    module_name = f"{ENGINES_PKG}.{name}_engine"
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        available = discover_engine_keys()
        raise SystemExit(
            f"Could not import '{module_name}': {exc}\n"
            f"Expected adapter at engines/{name}_engine.py.\n"
            f"Currently discoverable: {available}"
        ) from exc
    cls = getattr(module, "ENGINE", None)
    if cls is None:
        raise SystemExit(
            f"Engine module '{module_name}' must export a top-level "
            f"`ENGINE` attribute pointing at the engine class.",
        )
    if not (isinstance(cls, type) and issubclass(cls, OCREngine)):
        raise SystemExit(
            f"`ENGINE` in '{module_name}' must be a class subclassing "
            f"OCREngine; got {cls!r}.",
        )
    return cls()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one engine over the saved bench corpus.",
    )
    parser.add_argument(
        "--engine",
        required=True,
        help=(
            "Engine key (filename stem of engines/<key>_engine.py). "
            "Currently discoverable: " + ",".join(discover_engine_keys())
        ),
    )
    parser.add_argument(
        "--results-subdir",
        default=None,
        help=(
            "Write the result JSON to results/<subdir>/ instead of bare "
            "results/. Use one subdir per execution-provider track (e.g. "
            "'cuda', 'directml') so leaderboards from different hosts coexist."
        ),
    )
    args = parser.parse_args()
    out_dir = results_dir(args.results_subdir)

    if not MANIFEST_PATH.exists():
        raise SystemExit(
            f"No manifest at {MANIFEST_PATH}. Run capture first: "
            f"python -m backend.ocr.calibration.bench.capture both"
        )

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.engine}.json"

    tracemalloc.start()
    rss_init = rss_mb()
    overall_t0 = time.perf_counter_ns()

    def _write_failed(stage: str, exc: BaseException) -> None:
        """Record an engine that couldn't run as a structured failure result.

        An out-of-memory or load error is a legitimate, reportable outcome
        (e.g. a model that doesn't fit this GPU): write a result JSON with
        ``status="failed"`` + a reason so the leaderboard can list it as
        "ran, did not complete" rather than the run silently crashing. The
        scorer skips failed-status results.
        """
        is_oom = isinstance(exc, MemoryError) or "out of memory" in str(exc).lower()
        reason = f"{type(exc).__name__} during {stage}: {exc}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({
            "engine": args.engine,
            "status": "failed",
            "failure_stage": stage,
            "oom": is_oom,
            "skip_reason": reason[:2000],
            "init": {"device": locals().get("device", "cpu"),
                     "provider": locals().get("provider")},
        }, indent=2), encoding="utf-8")
        print(f"[{args.engine}] FAILED at {stage}: {reason[:300]}", flush=True)

    print(f"[{args.engine}] loading...", flush=True)
    try:
        with timed_ms() as t:
            engine = load_engine(args.engine)
    except Exception as exc:  # OOM at load, missing weights, etc.
        _write_failed("load", exc)
        tracemalloc.stop()
        return 0
    load_ms = t[0]
    rss_after_load = rss_mb()
    device = getattr(engine, "device", "cpu")
    provider = getattr(engine, "provider", None)
    print(
        f"[{args.engine}] loaded in {load_ms:.1f} ms "
        f"(RSS {rss_after_load:.1f} MB, device={device}"
        + (f", provider={provider}" if provider else "")
        + ")", flush=True,
    )

    print(f"[{args.engine}] warming up...", flush=True)
    try:
        with timed_ms() as t:
            engine.warm_up()
    except Exception as exc:  # OOM on first inference is the common case
        _write_failed("warmup", exc)
        tracemalloc.stop()
        return 0
    warmup_ms = t[0]
    rss_after_warmup = rss_mb()
    print(f"[{args.engine}] warmed up in {warmup_ms:.1f} ms", flush=True)

    panels_out: dict = {}
    panel_keys = list(manifest["panels"].keys())
    grand_total_cells = sum(
        sum(len(p["cells"]) for p in panel["pages"])
        for panel in manifest["panels"].values()
    )
    cells_done = 0
    engine_t0 = time.perf_counter_ns()

    for panel_idx, panel_key in enumerate(panel_keys, 1):
        panel_meta = manifest["panels"][panel_key]
        pages_meta = panel_meta.get("pages", [])
        n_pages = len(pages_meta)
        panel_total_cells = sum(len(p["cells"]) for p in pages_meta)
        print(
            f"[{args.engine}] panel {panel_idx}/{len(panel_keys)} "
            f"{panel_key}: {n_pages} pages, {panel_total_cells} cells",
            flush=True,
        )
        per_cell_type_ms: dict[str, list[float]] = {}
        pages_out: list[dict] = []
        panel_t0 = time.perf_counter_ns()

        for page_idx, page_meta in enumerate(pages_meta, 1):
            page_t0 = time.perf_counter_ns()
            rows: dict[int, dict] = {}
            n_cells_in_page = len(page_meta["cells"])
            for cell_idx, cell_meta in enumerate(page_meta["cells"], 1):
                r = cell_meta["row"]
                cn = cell_meta["cell"]
                crop_path = CROPS_DIR / cell_meta["path"]
                crop = cv2.imread(str(crop_path), cv2.IMREAD_COLOR)
                if crop is None:
                    raise SystemExit(f"Failed to read crop {crop_path}")

                with timed_ms() as t:
                    text, conf = engine.read_text(crop)
                ocr_ms = t[0]
                per_cell_type_ms.setdefault(cn, []).append(ocr_ms)

                rows.setdefault(r, {"row": r, "cells": {}})
                rows[r]["cells"][cn] = {
                    "ocr_text": text,
                    "ocr_conf": conf,
                    "ocr_ms": ocr_ms,
                }

                cells_done += 1
                # Per-cell carriage-return progress. Updates always
                # (cheap; each \r overwrites the previous line). The
                # final cell of the page falls through to the page-end
                # summary below which prints with a leading \n.
                engine_elapsed = (time.perf_counter_ns() - engine_t0) / 1e9
                rate = cells_done / engine_elapsed if engine_elapsed > 0 else 0
                eta = (
                    (grand_total_cells - cells_done) / rate if rate > 0 else 0
                )
                pct = cells_done / grand_total_cells * 100
                print(
                    f"\r[{args.engine}] {panel_key} p{page_idx:02d}/{n_pages} "
                    f"cell {cell_idx:02d}/{n_cells_in_page}  "
                    f"total {cells_done}/{grand_total_cells} "
                    f"({pct:5.1f}%, {rate:5.1f}/s, eta {_fmt_eta(eta)})  ",
                    end="",
                    flush=True,
                )

            page_wall_ms = (time.perf_counter_ns() - page_t0) / 1e6
            print(
                f"\r[{args.engine}] {panel_key} p{page_idx:02d}/{n_pages} "
                f"done in {page_wall_ms / 1000:.1f}s "
                f"({n_cells_in_page} cells)" + " " * 20,
                flush=True,
            )

            page_record: dict = {
                "page_index": page_meta["page_index"],
                "rows": [rows[r] for r in sorted(rows)],
                "panel_wall_ms": page_wall_ms,
            }
            for k in ("category", "category_page"):
                if k in page_meta:
                    page_record[k] = page_meta[k]
            pages_out.append(page_record)

        panel_wall_ms = (time.perf_counter_ns() - panel_t0) / 1e6
        panels_out[panel_key] = {
            "n_rows": panel_meta["n_rows"],
            "cell_names": panel_meta["cell_names"],
            "pages": pages_out,
            "panel_wall_ms": panel_wall_ms,
            "ocr_per_cell_type": {
                cn: ms_distribution(times) for cn, times in per_cell_type_ms.items()
            },
            "rss_after_panel_mb": rss_mb(),
        }
        print(
            f"[{args.engine}] panel {panel_idx}/{len(panel_keys)} "
            f"{panel_key} done: {panel_wall_ms / 1000:.1f}s "
            f"({panel_total_cells} cells)",
            flush=True,
        )

    overall_ms = (time.perf_counter_ns() - overall_t0) / 1e6
    final_rss = rss_mb()
    cur_heap, peak_heap = heap_mb()

    result = {
        "engine": args.engine,
        "init": {
            "rss_init_mb": rss_init,
            "load_ms": load_ms,
            "rss_after_load_mb": rss_after_load,
            "warmup_ms": warmup_ms,
            "rss_after_warmup_mb": rss_after_warmup,
            "device": device,
            "provider": provider,
        },
        "panels": panels_out,
        "overall": {
            "subprocess_wall_ms": overall_ms,
            "final_rss_mb": final_rss,
            "heap_current_mb": cur_heap,
            "heap_peak_mb": peak_heap,
        },
    }
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"[{args.engine}] wrote {out_path}", flush=True)
    tracemalloc.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
