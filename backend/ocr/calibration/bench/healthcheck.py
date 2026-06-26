"""Pre-bench health check across all discoverable engines.

For each engine the orchestrator would spawn at bench time, this verifies
the per-engine venv has the right deps installed and the adapter wires
correctly: import the module, call ``ENGINE()``, run ``warm_up`` and a
single ``read_text(...)`` call against a small white dummy crop. Catches
broken venvs in ~30 seconds per engine instead of 5 hours into the
bench run.

Two modes (single file, both modes):

- Probe mode — runs in the engine's agent venv, exits 0 if the engine
  imports / instantiates / warms / reads cleanly. Prints one JSON line
  to stdout::

      python -m backend.ocr.calibration.bench.healthcheck --probe --engine <key>

- Sweep mode — runs in any venv (the orchestrator's), iterates all
  discoverable engines via the venv mapping in
  ``calibration/bench/engine_venvs.json``, spawning a probe subprocess
  per engine. Writes ``calibration/bench/healthcheck.json`` and exits
  non-zero if any engine fails::

      python -m backend.ocr.calibration.bench.healthcheck --sweep
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

import numpy as np

import cv2

from backend.ocr.calibration.bench.common import BENCH_DIR, CROPS_DIR, WORKTREE_ROOT
from backend.ocr.calibration.bench.runner import discover_engine_keys, load_engine

PROBE_TIMEOUT_S = 300
HEALTHCHECK_PATH = BENCH_DIR / "healthcheck.json"

# Smoke-test crop: skill page 1 row 0 name cell. Visually reads "Agility"
# (verified against ground_truth.json for skill page 1 row 0). Picked
# because: (a) a name cell is the typical case for the bench, (b) it's
# universally on the corpus, (c) a working engine should return a string
# close to "Agility" so the user can eyeball each row's plausibility,
# (d) numerics are uniformly easy per earlier findings so they don't
# discriminate between healthy and broken engines as well.
PROBE_CROP_PATH = CROPS_DIR / "skill" / "page-01" / "row-00-name.png"
PROBE_EXPECTED = "Agility"


def _load_probe_crop() -> np.ndarray:
    """Load the canonical smoke-test crop, falling back to a blank
    canvas if the corpus isn't captured yet."""
    if PROBE_CROP_PATH.exists():
        crop = cv2.imread(str(PROBE_CROP_PATH), cv2.IMREAD_COLOR)
        if crop is not None:
            return crop
    # Fallback: if corpus hasn't been captured yet, the smoke degrades
    # to a "does the engine pipeline run?" check rather than a "can it
    # read?" check. Marked in the result so the user knows.
    return np.full((20, 100, 3), 255, dtype=np.uint8)


def probe_one(key: str) -> dict:
    """Import + instantiate + warm_up + read_text on a real corpus crop
    (skill page 1 row 0 name = 'Agility'). Returns a dict capturing
    either success (text + conf + expected) or failure (error type +
    truncated traceback)."""
    try:
        engine = load_engine(key)
        engine.warm_up()
        crop = _load_probe_crop()
        text, conf = engine.read_text(crop)
        return {
            "engine": key,
            "ok": True,
            "text": str(text),
            "conf": float(conf),
            "expected": PROBE_EXPECTED,
            "probe_crop": str(PROBE_CROP_PATH.relative_to(WORKTREE_ROOT))
            if PROBE_CROP_PATH.exists() else "<blank fallback>",
        }
    except Exception as exc:
        return {
            "engine": key,
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback_tail": traceback.format_exc()[-800:],
        }


def _short_repr(s: str, n: int = 22) -> str:
    """ASCII-safe repr-style truncation for terminal output (CJK / unicode
    can confuse Windows console encoding)."""
    r = ascii(s)
    return r if len(r) <= n else r[: n - 3] + "...'"


def _similar(a: str, b: str) -> bool:
    """Cheap fuzzy heuristic for healthcheck plausibility marker.
    Avoids a rapidfuzz import in the probe subprocess; uses a simple
    char-overlap ratio plus length-tolerance test."""
    if not a or not b:
        return False
    a_set = set(a.lower())
    b_set = set(b.lower())
    if not (a_set | b_set):
        return False
    overlap = len(a_set & b_set) / len(a_set | b_set)
    length_ok = abs(len(a) - len(b)) <= max(2, max(len(a), len(b)) // 3)
    return overlap >= 0.5 and length_ok


def _fmt_short(seconds: float) -> str:
    if seconds < 0 or seconds != seconds:
        return "?"
    if seconds < 60:
        return f"{seconds:.1f}s"
    if seconds < 3600:
        return f"{seconds / 60:.1f}m"
    return f"{seconds / 3600:.1f}h"


def sweep_all() -> int:
    # Imported here to avoid circular import in probe mode (which doesn't
    # need the orchestrator's runtime config).
    from backend.ocr.calibration.benchmark_panel_ocr import (
        load_engine_runtime_config,
    )

    overrides, global_env = load_engine_runtime_config()
    keys = discover_engine_keys()
    n_total = len(keys)
    print(
        f"Health-checking {n_total} engines "
        f"(timeout {PROBE_TIMEOUT_S}s each)\n",
        flush=True,
    )

    summary: list[dict] = []
    sub_env = os.environ.copy()
    sub_env.update(global_env)
    sweep_t0 = time.perf_counter_ns()

    for idx, key in enumerate(keys, 1):
        prefix = f"[{idx:02d}/{n_total}] {key:25s}"
        py = overrides.get(key, sys.executable)
        venv_name = Path(py).parent.parent.name if py else "?"
        if not Path(py).exists():
            r = {
                "engine": key,
                "ok": False,
                "error_type": "InterpreterMissing",
                "error": py,
            }
            print(
                f"  {prefix} SKIP — interpreter not at {py}",
                flush=True,
            )
            summary.append(r)
            continue

        # In-flight line: overwritten on completion with the result.
        elapsed_total = (time.perf_counter_ns() - sweep_t0) / 1e9
        print(
            f"\r  {prefix} running... ({venv_name}, "
            f"sweep elapsed {_fmt_short(elapsed_total)})",
            end="", flush=True,
        )
        engine_t0 = time.perf_counter_ns()
        try:
            proc = subprocess.run(
                [py, "-m", "backend.ocr.calibration.bench.healthcheck",
                 "--probe", "--engine", key],
                capture_output=True, text=True,
                cwd=str(WORKTREE_ROOT), env=sub_env,
                timeout=PROBE_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            r = {
                "engine": key,
                "ok": False,
                "error_type": "Timeout",
                "error": f"probe exceeded {PROBE_TIMEOUT_S}s",
            }
            print(
                f"\r  {prefix} TIMEOUT after {PROBE_TIMEOUT_S}s"
                + " " * 40,
                flush=True,
            )
            summary.append(r)
            continue
        engine_dt = (time.perf_counter_ns() - engine_t0) / 1e9
        if proc.returncode != 0 and not proc.stdout.strip():
            r = {
                "engine": key,
                "ok": False,
                "error_type": "SubprocessExit",
                "exit_code": proc.returncode,
                "stderr_tail": proc.stderr[-600:] if proc.stderr else "",
            }
            tail = (
                proc.stderr.strip().splitlines()[-1]
                if proc.stderr.strip() else "<empty>"
            )
            print(
                f"\r  {prefix} FAIL  exit={proc.returncode} "
                f"({_fmt_short(engine_dt)}): {tail[:90]}"
                + " " * 20,
                flush=True,
            )
            summary.append(r)
            continue
        try:
            line = proc.stdout.strip().splitlines()[-1]
            r = json.loads(line)
        except Exception:
            r = {
                "engine": key,
                "ok": False,
                "error_type": "StdoutParseFail",
                "stdout_tail": proc.stdout[-600:],
            }
            print(
                f"\r  {prefix} PARSE-FAIL ({_fmt_short(engine_dt)})"
                + " " * 40,
                flush=True,
            )
            summary.append(r)
            continue
        if r.get("ok"):
            got = r.get("text", "") or ""
            expected = r.get("expected", "") or ""
            # Plausibility marker: "==" if exact, "~" if near (substring or
            # rapidfuzz-friendly close), "!=" if wildly different.
            marker = "=="
            if expected and got != expected:
                if (
                    expected.lower() in got.lower()
                    or got.lower() in expected.lower()
                    or _similar(got, expected)
                ):
                    marker = " ~"
                else:
                    marker = "!="
            elif not expected:
                marker = "  "
            print(
                f"\r  {prefix} OK    ({_fmt_short(engine_dt)}) "
                f"got={_short_repr(got)} {marker} expected={_short_repr(expected)} "
                f"conf={r.get('conf', 0):.3f}"
                + " " * 10,
                flush=True,
            )
        else:
            err = (r.get("error") or "")[:90]
            print(
                f"\r  {prefix} FAIL  ({_fmt_short(engine_dt)}) "
                f"{r.get('error_type')}: {err}"
                + " " * 20,
                flush=True,
            )
        summary.append(r)

    HEALTHCHECK_PATH.parent.mkdir(parents=True, exist_ok=True)
    HEALTHCHECK_PATH.write_text(
        json.dumps(summary, indent=2), encoding="utf-8",
    )

    n_ok = sum(1 for r in summary if r.get("ok"))
    n_fail = len(summary) - n_ok
    print(f"\n=== {n_ok}/{len(summary)} OK, {n_fail} FAIL ===", flush=True)
    if n_fail:
        print("Failures:", flush=True)
        for r in summary:
            if not r.get("ok"):
                print(
                    f"  - {r['engine']}: "
                    f"{r.get('error_type')}: {(r.get('error') or '')[:200]}",
                    flush=True,
                )
    print(f"\nWrote {HEALTHCHECK_PATH}", flush=True)
    return 0 if n_fail == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--probe", action="store_true",
        help="Probe a single engine; print JSON to stdout.",
    )
    parser.add_argument(
        "--sweep", action="store_true",
        help="Sweep all engines via the venv mapping.",
    )
    parser.add_argument(
        "--engine",
        help="Engine key (required with --probe).",
    )
    args = parser.parse_args()

    if args.probe:
        if not args.engine:
            raise SystemExit("--probe requires --engine <key>")
        result = probe_one(args.engine)
        print(json.dumps(result))
        return 0 if result.get("ok") else 1
    if args.sweep:
        return sweep_all()
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
