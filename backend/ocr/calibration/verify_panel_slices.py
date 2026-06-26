"""Capture the live panel and slice it per the calibrated geometry, writing
the per-row by per-cell-type slices to disk for visual verification.

Run as:
    .venv/Scripts/python.exe -m backend.ocr.calibration.verify_panel_slices skill
    .venv/Scripts/python.exe -m backend.ocr.calibration.verify_panel_slices profession

Counts down 5s ("Get the game ready"), screenshots the panel via the matching
``*_region()`` plus mss, slices into N_rows by N_cells images using
``backend/data/panel_geometry.json``, and writes them to
``calibration/slices/<panel>/`` at the worktree root.

The user inspects the slices to confirm row and cell alignment. If alignment
is wrong, recalibrate via ``measure_panel_geometry``.
"""

from __future__ import annotations

import argparse
import io
import json
import shutil
import time
from pathlib import Path
from typing import Callable

import mss
import mss.tools
from PIL import Image

from backend.services.scan_presets import profession_region, skill_region

GEOMETRY_PATH = Path(__file__).resolve().parents[2] / "data" / "panel_geometry.json"
SLICES_DIR = Path(__file__).resolve().parents[3] / "calibration" / "slices"

COUNTDOWN_SECONDS = 5

_REGION_FNS: dict[str, Callable[[], tuple[list[int], list[int]] | None]] = {
    "skill": skill_region,
    "profession": profession_region,
}


def _load_geometry(panel_key: str) -> dict:
    if not GEOMETRY_PATH.exists():
        raise SystemExit(
            f"No calibration file at {GEOMETRY_PATH}. "
            f"Run measure_panel_geometry {panel_key} first."
        )
    data = json.loads(GEOMETRY_PATH.read_text(encoding="utf-8"))
    if panel_key not in data:
        raise SystemExit(
            f"No '{panel_key}' entry in {GEOMETRY_PATH}. "
            f"Run measure_panel_geometry {panel_key} first."
        )
    return data[panel_key]


def _countdown(panel_key: str) -> None:
    print(f"Get the game ready: capturing the {panel_key} panel.")
    print("Make sure the panel is visible on the page you want to verify.")
    for s in range(COUNTDOWN_SECONDS, 0, -1):
        print(f"  {s}...")
        time.sleep(1)
    print("CAPTURE")


def _capture_panel(panel_key: str) -> bytes:
    region_fn = _REGION_FNS[panel_key]
    region = region_fn()
    if region is None:
        raise SystemExit(
            f"EU window not found or {panel_key} region uncomputable: start EU first"
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
        return mss.tools.to_png(shot.rgb, shot.size)


def _slice_and_save(geom: dict, panel_key: str) -> None:
    png_bytes = _capture_panel(panel_key)
    img = Image.open(io.BytesIO(png_bytes))

    n_rows = geom["n_rows"]
    cells = geom["cells"]

    out_dir = SLICES_DIR / panel_key
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    img.save(out_dir / "panel.png")

    for r in range(n_rows):
        for cell_name, cell in cells.items():
            first = cell["first_y_top"]
            last = cell["last_y_top"]
            # Linear interpolation between first and last row, per cell type.
            y_top = (
                round(first + r * (last - first) / (n_rows - 1))
                if n_rows > 1
                else first
            )
            y_bot = y_top + cell["height"]
            crop = img.crop((cell["x_left"], y_top, cell["x_right"], y_bot))
            crop.save(out_dir / f"row-{r:02d}-{cell_name}.png")

    total = n_rows * len(cells)
    print(f"\nWrote panel.png plus {total} slices to {out_dir}/")
    print("Open the directory and verify each row and cell type aligns with the panel content.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify panel grid geometry by slicing a live capture."
    )
    parser.add_argument(
        "panel",
        choices=["skill", "profession"],
        help="Panel to verify.",
    )
    args = parser.parse_args()

    geom = _load_geometry(args.panel)
    _countdown(args.panel)
    _slice_and_save(geom, args.panel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
