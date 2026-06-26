"""Calibrate panel-relative grid geometry via live hover-and-Enter.

Run as:
    .venv/Scripts/python.exe -m backend.ocr.calibration.measure_panel_geometry skill
    .venv/Scripts/python.exe -m backend.ocr.calibration.measure_panel_geometry profession --rows N

Walks a hover-and-Enter sequence outlining each calibrated cell on row 0 (first
visible row) and the last visible row. From those we derive each cell's
horizontal extents, vertical extents, and per-row anchors (first row top, last
row top). Intermediate rows are recovered at runtime by linear interpolation
between first and last endpoints, per cell type.

Per-panel cell vocabulary:
- skill: name, level, bar (12 rows; rank inferred from level via skill_ranks.json)
- profession: name, rank_level, percent, bar (variable rows; pass --rows N).
  rank_level is a wide cell holding "Expert 48" / "Impressive 35"; OCR returns
  the full string and a regex extracts the trailing integer (rank text is
  discarded). percent holds "46.2%" text (read directly; the bar is forward-
  compat fallback).

The panel rect (``width`` / ``height`` / ``*_offset``) stays in
``scan_presets.{SKILL,PROFESSION}_ANCHOR``; both calibration and capture share
that origin via ``skill_region()`` / ``profession_region()``, so panel-relative
offsets are self-consistent.

Result is written to ``backend/data/panel_geometry.json``: the persistent
grid template loaded at runtime by ``backend.services.scan_presets``.

Mirrors the hover-and-Enter mechanic of ``backend.services.repair_ocr``:
pynput global Enter listener, Win32 ``GetCursorPos`` for screen coords.
No images saved during calibration; the JSON template is the only artefact.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import sys
import threading
from pathlib import Path
from typing import Callable

from backend.services.eu_window import find_game_window, get_window_geometry
from backend.services.scan_presets import profession_region, skill_region

try:
    from pynput.keyboard import Key, Listener as KeyListener
except ImportError:
    print("pynput is required for calibration; install with: pip install pynput", file=sys.stderr)
    raise

GEOMETRY_PATH = Path(__file__).resolve().parents[2] / "data" / "panel_geometry.json"

SKILL_N_ROWS = 12
DRIFT_TOLERANCE_PX = 3

SKILL_CELLS = ("name", "level", "bar")
PROFESSION_CELLS = ("name", "rank_level", "percent", "bar")

_CELL_HINT = (
    "(Hover the corner of the CELL the text or bar occupies in the panel layout, "
    "not the corner of the visible content. Names are left-aligned; level / "
    "rank_level / percent text varies in width row-to-row, so calibrate the cell, "
    "not the text.)"
)

_CELL_LABELS = {
    "name": "NAME",
    "level": "LEVEL",
    "bar": "PROGRESS BAR",
    "rank_level": "RANK + LEVEL",
    "percent": "PERCENTAGE",
}


class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def _get_cursor_pos() -> tuple[int, int]:
    if sys.platform != "win32":
        raise OSError("Calibration is Windows-only")
    pt = _POINT()
    if not ctypes.windll.user32.GetCursorPos(ctypes.byref(pt)):
        raise OSError("GetCursorPos failed")
    return int(pt.x), int(pt.y)


def _walk_steps(steps: list[str]) -> list[tuple[int, int]]:
    """Run a hover-and-Enter sequence; return cursor positions in step order."""
    results: list[tuple[int, int]] = []
    advance = threading.Event()

    def on_press(key):
        try:
            if key == Key.enter:
                advance.set()
        except AttributeError:
            pass

    listener = KeyListener(on_press=on_press)
    listener.daemon = True
    listener.start()
    try:
        for i, instruction in enumerate(steps, 1):
            print(f"\n[{i}/{len(steps)}] {instruction}")
            advance.clear()
            advance.wait()
            x, y = _get_cursor_pos()
            results.append((x, y))
            print(f"        captured ({x}, {y})")
    finally:
        listener.stop()
    return results


def _build_steps(cell_names: tuple[str, ...], last_row_idx: int) -> list[str]:
    steps: list[str] = []
    for row_idx in (0, last_row_idx):
        row_qualifier = "(first row)" if row_idx == 0 else "(last visible row)"
        for cell in cell_names:
            label = _CELL_LABELS.get(cell, cell.upper())
            steps.append(
                f"ROW {row_idx} {row_qualifier}, {label} cell: hover TOP-LEFT corner, then press Enter"
            )
            steps.append(
                f"ROW {row_idx}, {label} cell: hover BOTTOM-RIGHT corner, then press Enter"
            )
    return steps


def _derive_cell(
    r0_tl: tuple[int, int],
    r0_br: tuple[int, int],
    rN_tl: tuple[int, int],
    rN_br: tuple[int, int],
    panel_tl: tuple[int, int],
    name: str,
    last_row_idx: int,
) -> tuple[dict, list[str]]:
    """Average row 0 and last row measurements; surface drift warnings."""

    def rel_x(x: int) -> int:
        return x - panel_tl[0]

    def rel_y(y: int) -> int:
        return y - panel_tl[1]

    r0_x_left, r0_x_right = rel_x(r0_tl[0]), rel_x(r0_br[0])
    rN_x_left, rN_x_right = rel_x(rN_tl[0]), rel_x(rN_br[0])
    r0_height = r0_br[1] - r0_tl[1]
    rN_height = rN_br[1] - rN_tl[1]

    cell = {
        "x_left": (r0_x_left + rN_x_left) // 2,
        "x_right": (r0_x_right + rN_x_right) // 2,
        "first_y_top": rel_y(r0_tl[1]),
        "last_y_top": rel_y(rN_tl[1]),
        "height": (r0_height + rN_height) // 2,
    }

    warnings: list[str] = []
    if abs(r0_x_left - rN_x_left) > DRIFT_TOLERANCE_PX:
        warnings.append(
            f"{name} x_left drifts {abs(r0_x_left - rN_x_left)}px "
            f"between row 0 and row {last_row_idx}"
        )
    if abs(r0_x_right - rN_x_right) > DRIFT_TOLERANCE_PX:
        warnings.append(
            f"{name} x_right drifts {abs(r0_x_right - rN_x_right)}px "
            f"between row 0 and row {last_row_idx}"
        )
    if abs(r0_height - rN_height) > DRIFT_TOLERANCE_PX:
        warnings.append(
            f"{name} cell height drifts {abs(r0_height - rN_height)}px "
            f"between row 0 ({r0_height}px) and row {last_row_idx} ({rN_height}px)"
        )
    return cell, warnings


def _calibrate_panel(
    panel_key: str,
    cell_names: tuple[str, ...],
    n_rows: int,
    region_fn: Callable[[], tuple[list[int], list[int]] | None],
) -> dict:
    if find_game_window() is None:
        raise SystemExit("EU window not found: start Entropia Universe first")
    geo = get_window_geometry(find_game_window())
    if geo is None:
        raise SystemExit("Could not read EU window geometry")
    region = region_fn()
    if region is None:
        raise SystemExit(f"Could not compute {panel_key} panel region from EU window")
    panel_tl, panel_br = region
    win_x, win_y, win_w, win_h = geo
    last_row_idx = n_rows - 1

    print(f"\nEU window: ({win_x}, {win_y}) {win_w}x{win_h}")
    print(f"{panel_key.title()} panel rect: TL={panel_tl} BR={panel_br}")
    print(f"\n{_CELL_HINT}\n")
    n_taps = len(cell_names) * 2 * 2
    n_rects = len(cell_names) * 2
    print(
        f"Walking {n_taps}-tap {panel_key} panel calibration "
        f"({n_rects} rectangles: {len(cell_names)} cells x 2 rows)."
    )
    print(f"Cells: {', '.join(cell_names)}.  Rows: 0 and {last_row_idx} (n_rows={n_rows}).")

    steps = _build_steps(cell_names, last_row_idx)
    pts = _walk_steps(steps)

    panel_tl_t = (panel_tl[0], panel_tl[1])
    cells_geometry: dict[str, dict] = {}
    all_warnings: list[str] = []
    n_cells = len(cell_names)

    for i, cell_name in enumerate(cell_names):
        r0_tl = pts[i * 2]
        r0_br = pts[i * 2 + 1]
        rN_tl = pts[n_cells * 2 + i * 2]
        rN_br = pts[n_cells * 2 + i * 2 + 1]
        cell, warns = _derive_cell(
            r0_tl, r0_br, rN_tl, rN_br, panel_tl_t, cell_name, last_row_idx
        )
        cells_geometry[cell_name] = cell
        all_warnings.extend(warns)

    geometry = {"n_rows": n_rows, "cells": cells_geometry}

    print(f"\nComputed {panel_key} panel geometry:")
    print(json.dumps(geometry, indent=2))

    if all_warnings:
        print(f"\nWARNINGS (drift exceeds {DRIFT_TOLERANCE_PX}px tolerance: recalibrate or accept):")
        for w in all_warnings:
            print(f"  - {w}")

    return geometry


def _write_geometry(panel_key: str, entry: dict) -> None:
    GEOMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if GEOMETRY_PATH.exists():
        try:
            data = json.loads(GEOMETRY_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
    data[panel_key] = entry
    GEOMETRY_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {GEOMETRY_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure panel grid geometry via live hover-and-Enter calibration."
    )
    parser.add_argument(
        "panel",
        choices=["skill", "profession"],
        help="Panel to calibrate.",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=None,
        help=(
            "Number of visible rows on the panel page. "
            f"Defaults to {SKILL_N_ROWS} for skill; required for profession "
            "(count visible rows on your profession panel page first)."
        ),
    )
    args = parser.parse_args()

    if args.panel == "skill":
        n_rows = args.rows if args.rows is not None else SKILL_N_ROWS
        entry = _calibrate_panel("skill", SKILL_CELLS, n_rows, skill_region)
        _write_geometry("skill", entry)
    elif args.panel == "profession":
        if args.rows is None:
            parser.error(
                "--rows is required for profession; count visible rows on the "
                "profession panel page and pass --rows N"
            )
        entry = _calibrate_panel("profession", PROFESSION_CELLS, args.rows, profession_region)
        _write_geometry("profession", entry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
