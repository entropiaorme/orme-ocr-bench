"""Capture phase for the OCR benchmark corpus.

Walks the full skill panel (12 pages) and the full profession panel
(15 pages across 5 categories), prompting for Enter once each panel page
is set up in-game. Per page: captures the panel via mss + the calibrated
geometry, saves the full panel PNG, slices into per-cell BGR PNGs on disk,
and appends to the manifest. Per-engine subprocess runs read crops from
this manifest so all engines see byte-identical inputs.

Restartable: re-running with the same arguments skips pages already
present in the manifest. Pass ``--force`` to wipe and start over for the
chosen panel(s).

Usage:
    python -m backend.ocr.calibration.bench.capture both
    python -m backend.ocr.calibration.bench.capture skill
    python -m backend.ocr.calibration.bench.capture profession
    python -m backend.ocr.calibration.bench.capture both --force
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import threading
import time
from pathlib import Path
from typing import Callable

import cv2
import mss
import numpy as np

from backend.ocr.calibration.bench.common import (
    CROPS_DIR,
    MANIFEST_PATH,
    load_geometry,
)
from backend.services.scan_presets import profession_region, skill_region

try:
    from pynput.keyboard import Key, Listener as KeyListener
except ImportError:
    print(
        "pynput is required for capture; install with: pip install pynput",
        file=sys.stderr,
    )
    raise

SKILL_PAGE_COUNT = 12
PROFESSION_CATEGORIES: list[tuple[int, int]] = [
    (1, 6),
    (2, 4),
    (3, 2),
    (4, 1),
    (5, 1),
]
PROFESSION_PAGE_COUNT = sum(p for _, p in PROFESSION_CATEGORIES)

POST_ENTER_DEBOUNCE_S = 0.25

_REGION_FNS: dict[str, Callable[[], tuple[list[int], list[int]] | None]] = {
    "skill": skill_region,
    "profession": profession_region,
}


def _make_enter_listener() -> tuple[threading.Event, KeyListener]:
    advance = threading.Event()

    def on_press(key) -> None:
        try:
            if key == Key.enter:
                advance.set()
        except AttributeError:
            pass

    listener = KeyListener(on_press=on_press)
    listener.daemon = True
    listener.start()
    return advance, listener


def wait_for_enter(advance: threading.Event, prompt: str) -> None:
    print(prompt, flush=True)
    advance.clear()
    advance.wait()
    time.sleep(POST_ENTER_DEBOUNCE_S)


def capture_panel_bgr(panel_key: str) -> np.ndarray:
    region = _REGION_FNS[panel_key]()
    if region is None:
        raise SystemExit(
            f"EU window not found or {panel_key} region uncomputable. "
            "Start EU first."
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


def slice_page(
    panel_bgr: np.ndarray,
    geom: dict,
    panel_key: str,
    page_index: int,
) -> tuple[Path, list[dict]]:
    """Save full panel + per-cell crops for one page; return (page_dir, cell_entries)."""
    n_rows: int = geom["n_rows"]
    cells: dict[str, dict] = geom["cells"]

    out_dir = CROPS_DIR / panel_key / f"page-{page_index:02d}"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cv2.imwrite(str(out_dir / "_panel.png"), panel_bgr)

    entries: list[dict] = []
    for r in range(n_rows):
        for cell_name, cell in cells.items():
            if cell_name == "bar":
                # Bar reading deferred; skip in the bench (consistent with the
                # validate path).
                continue
            first = cell["first_y_top"]
            last = cell["last_y_top"]
            y_top = (
                round(first + r * (last - first) / (n_rows - 1))
                if n_rows > 1
                else first
            )
            y_bot = y_top + cell["height"]
            crop = panel_bgr[y_top:y_bot, cell["x_left"]:cell["x_right"]]
            fname = f"row-{r:02d}-{cell_name}.png"
            path = out_dir / fname
            cv2.imwrite(str(path), crop)
            entries.append(
                {
                    "row": r,
                    "cell": cell_name,
                    "path": str(path.relative_to(CROPS_DIR)).replace("\\", "/"),
                    "width": int(cell["x_right"] - cell["x_left"]),
                    "height": int(cell["height"]),
                }
            )
    return out_dir, entries


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"captured_at": None, "panels": {}}


def write_manifest(manifest: dict) -> None:
    manifest["captured_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2), encoding="utf-8",
    )


def captured_pages(manifest: dict, panel_key: str) -> set[int]:
    panel = manifest["panels"].get(panel_key)
    if not panel:
        return set()
    return {p["page_index"] for p in panel.get("pages", [])}


def ensure_panel_meta(manifest: dict, panel_key: str, geom: dict) -> dict:
    cell_names = [c for c in geom["cells"].keys() if c != "bar"]
    entry = manifest["panels"].setdefault(
        panel_key,
        {"n_rows": geom["n_rows"], "cell_names": cell_names, "pages": []},
    )
    entry["n_rows"] = geom["n_rows"]
    entry["cell_names"] = cell_names
    return entry


def append_page(panel_entry: dict, page_record: dict) -> None:
    panel_entry["pages"] = [
        p for p in panel_entry["pages"]
        if p["page_index"] != page_record["page_index"]
    ]
    panel_entry["pages"].append(page_record)
    panel_entry["pages"].sort(key=lambda p: p["page_index"])


def walk_skill(
    manifest: dict, advance: threading.Event, force: bool,
) -> None:
    geom = load_geometry("skill")
    panel_entry = ensure_panel_meta(manifest, "skill", geom)
    already = set() if force else captured_pages(manifest, "skill")

    print(f"\n=== SKILL PANEL: {SKILL_PAGE_COUNT} pages ===")
    if already:
        print(f"  resuming, already captured: {sorted(already)}")

    for page in range(1, SKILL_PAGE_COUNT + 1):
        if page in already:
            continue
        wait_for_enter(
            advance,
            f"\nSkill page {page}/{SKILL_PAGE_COUNT}: open the skills panel "
            f"and navigate to page {page}, then press Enter.",
        )
        panel_bgr = capture_panel_bgr("skill")
        h, w = panel_bgr.shape[:2]
        out_dir, cells = slice_page(panel_bgr, geom, "skill", page)
        record = {
            "page_index": page,
            "panel_screenshot": str(
                (out_dir / "_panel.png").relative_to(CROPS_DIR),
            ).replace("\\", "/"),
            "panel_width": w,
            "panel_height": h,
            "cells": cells,
        }
        append_page(panel_entry, record)
        write_manifest(manifest)
        print(f"  captured skill page {page} ({len(cells)} cells)")


def walk_profession(
    manifest: dict, advance: threading.Event, force: bool,
) -> None:
    geom = load_geometry("profession")
    panel_entry = ensure_panel_meta(manifest, "profession", geom)
    already = set() if force else captured_pages(manifest, "profession")

    print(
        f"\n=== PROFESSION PANEL: {PROFESSION_PAGE_COUNT} pages "
        f"across {len(PROFESSION_CATEGORIES)} categories ==="
    )
    if already:
        print(f"  resuming, already captured: {sorted(already)}")

    page = 0
    for category, cat_pages in PROFESSION_CATEGORIES:
        for cat_page in range(1, cat_pages + 1):
            page += 1
            if page in already:
                continue
            wait_for_enter(
                advance,
                f"\nProfession Category {category}, page {cat_page}/{cat_pages} "
                f"(overall {page}/{PROFESSION_PAGE_COUNT}): open the professions "
                "panel, select the category tab, navigate to that page, then "
                "press Enter.",
            )
            panel_bgr = capture_panel_bgr("profession")
            h, w = panel_bgr.shape[:2]
            out_dir, cells = slice_page(
                panel_bgr, geom, "profession", page,
            )
            record = {
                "page_index": page,
                "category": category,
                "category_page": cat_page,
                "panel_screenshot": str(
                    (out_dir / "_panel.png").relative_to(CROPS_DIR),
                ).replace("\\", "/"),
                "panel_width": w,
                "panel_height": h,
                "cells": cells,
            }
            append_page(panel_entry, record)
            write_manifest(manifest)
            print(
                f"  captured profession page {page} "
                f"(cat {category} pg {cat_page}, {len(cells)} cells)"
            )


def expected_total(panel: str) -> int:
    if panel == "skill":
        return SKILL_PAGE_COUNT
    if panel == "profession":
        return PROFESSION_PAGE_COUNT
    return SKILL_PAGE_COUNT + PROFESSION_PAGE_COUNT


def summarise(manifest: dict, panel_arg: str) -> None:
    panels_to_check = (
        ["skill", "profession"] if panel_arg == "both" else [panel_arg]
    )
    print("\n--- Capture summary ---")
    for p in panels_to_check:
        got = len(captured_pages(manifest, p))
        want = SKILL_PAGE_COUNT if p == "skill" else PROFESSION_PAGE_COUNT
        marker = "OK " if got == want else "!! "
        print(f"  {marker}{p}: {got}/{want} pages")
    print(f"\nManifest: {MANIFEST_PATH}")
    print(f"Crops:    {CROPS_DIR}/")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Capture multi-page corpus for the OCR bench "
            "(skill: 12 pages, profession: 15 pages across 5 categories)."
        ),
    )
    parser.add_argument(
        "panel", choices=["skill", "profession", "both"],
        help="Panel(s) to capture.",
    )
    parser.add_argument(
        "--force", action="store_true",
        help=(
            "Wipe existing crops and manifest entries for the chosen panel(s) "
            "and recapture from page 1."
        ),
    )
    args = parser.parse_args()

    if args.force:
        targets = (
            ["skill", "profession"]
            if args.panel == "both"
            else [args.panel]
        )
        for t in targets:
            shutil.rmtree(CROPS_DIR / t, ignore_errors=True)

    CROPS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    if args.force:
        targets = (
            ["skill", "profession"]
            if args.panel == "both"
            else [args.panel]
        )
        for t in targets:
            manifest["panels"].pop(t, None)

    advance, listener = _make_enter_listener()
    try:
        if args.panel in ("skill", "both"):
            walk_skill(manifest, advance, args.force)
        if args.panel in ("profession", "both"):
            walk_profession(manifest, advance, args.force)
    finally:
        listener.stop()

    summarise(manifest, args.panel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
