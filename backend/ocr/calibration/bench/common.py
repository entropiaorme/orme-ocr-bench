"""Shared utilities for the OCR benchmark harness.

The bench package compares multiple recognition engines against the same
captured panel crops (skill: 12 pages, profession: 14 pages), scores each
against the ground truth, and reports per-engine accuracy + perf. Each
engine runs in its own subprocess for isolation; this module holds the
cross-cutting bits (paths, regex parsers, GT loading, three-tier scorer,
failure-mode tagging, timing helpers).

Scoring is three-tier per cell (collapsed from an earlier four-tier scheme):

- PASS          : OCR text exactly matches ground truth (after strip).
- RECOVERED     : OCR text differs from GT, but rapidfuzz top-1 against
                  the canonical vocab is the expected canonical (only
                  applies to name cells; numeric cells go straight from
                  PASS to UNRECOVERABLE).
- UNRECOVERABLE : neither.

Rows in the ground truth carry a `kind` field. Only `kind=data` rows
count toward accuracy; `summary` (Average rows) and `empty` rows are
recorded by the engines but excluded from the denominator.
"""

from __future__ import annotations

import json
import re
import time
import tracemalloc
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import numpy as np

# --- Paths --------------------------------------------------------------------

# common.py lives at backend/ocr/calibration/bench/common.py:
#   parents[0] = bench/
#   parents[1] = calibration/
#   parents[2] = ocr/
#   parents[3] = backend/
#   parents[4] = worktree root
GEOMETRY_PATH = Path(__file__).resolve().parents[3] / "data" / "panel_geometry.json"
SNAPSHOT_DIR = Path(__file__).resolve().parents[3] / "data" / "snapshot"
WORKTREE_ROOT = Path(__file__).resolve().parents[4]
BENCH_DIR = WORKTREE_ROOT / "calibration" / "bench"
CROPS_DIR = BENCH_DIR / "crops"
MANIFEST_PATH = BENCH_DIR / "manifest.json"
RESULTS_DIR = BENCH_DIR / "results"
COMPOSITE_PATH = BENCH_DIR / "composite.json"
GROUND_TRUTH_PATH = BENCH_DIR / "ground_truth.json"


def results_dir(subdir: str | None = None) -> Path:
    """Directory holding per-engine result JSONs for one run track.

    The bench runs the same corpus under different execution-provider
    "tracks" (e.g. ``cuda`` for the unconstrained research breadth on an
    NVIDIA box, ``directml`` for the in-domain Windows/end-user posture).
    Each track writes to its own ``results/<subdir>/`` so leaderboards can
    coexist without filename collisions. ``subdir=None`` returns the bare
    ``results/`` directory, which holds the original (legacy) result set.
    """
    return RESULTS_DIR / subdir if subdir else RESULTS_DIR


def composite_path(subdir: str | None = None) -> Path:
    """Composite summary path for one run track (mirrors results_dir)."""
    if subdir:
        return RESULTS_DIR / subdir / "composite.json"
    return COMPOSITE_PATH


# --- Regex parsers ------------------------------------------------------------

LEVEL_RE = re.compile(r"\d+")
RANK_LEVEL_RE = re.compile(r"(\d+)\s*\.?\s*$")
PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%?")
FILENAME_UNSAFE_RE = re.compile(r'[<>:"/\\|?*]')

PERCENT_TOLERANCE = 0.05
TOP_N = 3


def parse_level(text: str | None) -> int | None:
    if not text:
        return None
    m = LEVEL_RE.search(text)
    return int(m.group()) if m else None


def parse_rank_level(text: str | None) -> int | None:
    if not text:
        return None
    # Profession rank cells render as `{rank}. {n}`. If OCR picked up a period
    # or comma (near-miss of period), trailing `o`/`O` is a misread digit zero.
    normalised = text
    if "." in text or "," in text:
        normalised = re.sub(r"[oO]+\s*$", "0", text)
    m = RANK_LEVEL_RE.search(normalised)
    return int(m.group(1)) if m else None


def parse_percent(text: str | None) -> float | None:
    if not text:
        return None
    m = PERCENT_RE.search(text)
    return float(m.group(1)) if m else None


# --- Geometry / vocab ---------------------------------------------------------


def load_geometry(panel_key: str) -> dict:
    if not GEOMETRY_PATH.exists():
        raise SystemExit(f"No calibration file at {GEOMETRY_PATH}.")
    data = json.loads(GEOMETRY_PATH.read_text(encoding="utf-8"))
    if panel_key not in data:
        raise SystemExit(f"No '{panel_key}' entry in {GEOMETRY_PATH}.")
    return data[panel_key]


def load_vocab(panel_key: str) -> list[str]:
    fname = "skills.json" if panel_key == "skill" else "professions.json"
    data = json.loads((SNAPSHOT_DIR / fname).read_text(encoding="utf-8"))
    return [entry["name"] for entry in data]


def load_ground_truth() -> dict | None:
    """Load multi-page ground truth for the bench corpus.

    Expected schema::

        {
          "panels": {
            "<panel_key>": {
              "pages": [
                {
                  "page_index": N,
                  "rows": [
                    {"row": R, "kind": "data"|"summary"|"empty",
                     "name": "...", "level": "...", ...}
                  ]
                }
              ]
            }
          }
        }
    """
    if not GROUND_TRUTH_PATH.exists():
        return None
    return json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))


def index_ground_truth(gt: dict) -> dict[tuple[str, int, int], dict]:
    """Index ground truth rows by (panel_key, page_index, row_index)."""
    out: dict[tuple[str, int, int], dict] = {}
    for panel_key, panel_data in gt.get("panels", {}).items():
        for page in panel_data.get("pages", []):
            page_idx = page["page_index"]
            for row in page["rows"]:
                out[(panel_key, page_idx, row["row"])] = row
    return out


# --- Filename sanitisation ----------------------------------------------------


def safe_filename(s: str) -> str:
    s = re.sub(r"\s+", "_", s.strip())
    s = FILENAME_UNSAFE_RE.sub("", s)
    return s or "_unnamed"


# --- Timing / resource helpers ------------------------------------------------


@contextmanager
def timed_ms() -> Iterator[list[float]]:
    t0 = time.perf_counter_ns()
    out: list[float] = []
    try:
        yield out
    finally:
        out.append((time.perf_counter_ns() - t0) / 1e6)


def ms_distribution(values: list[float]) -> dict | None:
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
    }


def rss_mb() -> float | None:
    try:
        import psutil
        return psutil.Process().memory_info().rss / 1024 / 1024
    except ModuleNotFoundError:
        return None


def heap_mb() -> tuple[float, float]:
    cur, peak = tracemalloc.get_traced_memory()
    return cur / 1024 / 1024, peak / 1024 / 1024


# --- Scoring against ground truth (three-tier) --------------------------------


def fuzzy_top(query: str, vocab: list[str], n: int = TOP_N) -> list[tuple[str, float]]:
    """Top-N fuzzy candidates using rapidfuzz.WRatio."""
    from rapidfuzz import fuzz, process

    results = process.extract(query, vocab, scorer=fuzz.WRatio, limit=n)
    return [(canon, float(score)) for canon, score, _ in results]


def _norm_name(s: str) -> str:
    """Whitespace + case insensitive name key for tolerant matching."""
    return re.sub(r"\s+", "", s or "").lower()


def evaluate_name(ocr_text: str, expected: str, vocab: list[str]) -> dict:
    cleaned = (ocr_text or "").strip()
    exp = (expected or "").strip()
    if cleaned == exp:
        return {"status": "PASS", "expected": exp, "got": cleaned}
    if cleaned and _norm_name(cleaned) == _norm_name(exp):
        return {"status": "PASS", "expected": exp, "got": cleaned}
    cands = fuzzy_top(cleaned, vocab) if cleaned else []
    candidates = [c for c, _ in cands]
    if candidates and candidates[0] == exp:
        return {
            "status": "RECOVERED",
            "expected": exp,
            "got": cleaned,
            "fuzzy_score": cands[0][1],
            "fuzzy_top": candidates,
        }
    return {
        "status": "UNRECOVERABLE",
        "expected": exp,
        "got": cleaned,
        "fuzzy_top": candidates,
    }


def evaluate_int(ocr_text: str, parsed: int | None, expected: int) -> dict:
    if parsed == expected:
        return {"status": "PASS", "expected": expected, "got": parsed}
    return {
        "status": "UNRECOVERABLE",
        "expected": expected,
        "got": parsed,
        "ocr_text": ocr_text,
    }


def evaluate_percent(ocr_text: str, parsed: float | None, expected: float) -> dict:
    if parsed is not None and abs(parsed - expected) <= PERCENT_TOLERANCE:
        return {"status": "PASS", "expected": expected, "got": parsed}
    return {
        "status": "UNRECOVERABLE",
        "expected": expected,
        "got": parsed,
        "ocr_text": ocr_text,
    }


# --- Failure-mode tagging -----------------------------------------------------


def tag_failure_mode(ocr_text: str | None, expected: str | None) -> str:
    """Classify a non-PASS cell's failure shape.

    Returns one of: ``reject`` (blank OCR), ``hallucinate`` (OCR text
    materially longer than expected), ``drop`` (materially shorter),
    ``substitute`` (similar length, character mismatch).

    Heuristic only; it's a directional aid for the failure-shape
    breakdown, not a precise classifier.
    """
    o = (ocr_text or "").strip()
    e = (expected or "").strip()
    if not o:
        return "reject"
    if not e:
        return "substitute"
    lo, le = len(o), len(e)
    if lo > le * 1.5:
        return "hallucinate"
    if lo < le * 0.5:
        return "drop"
    return "substitute"
