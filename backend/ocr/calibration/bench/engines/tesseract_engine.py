"""Tesseract adapter via pytesseract.

Tesseract is CPU-only and configured here for single-line text (PSM 7) since
every bench cell is a single-line crop. Per-cell confidence is the mean of
per-word confidences reported by Tesseract (Tesseract reports word-level
conf in [0, 100]; we normalise to [0, 1] for ergonomic display).

Requires the Tesseract binary on PATH (or an explicit path via env var
``TESSERACT_CMD``). On Windows, install via:
    winget install --id tesseract-ocr.tesseract
"""

from __future__ import annotations

import os
import shutil

import cv2
import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine


class TesseractEngine(OCREngine):
    name = "tesseract"

    def __init__(self) -> None:
        try:
            import pytesseract
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "pytesseract not installed. pip install pytesseract"
            ) from exc

        self._pyt = pytesseract

        cmd = os.environ.get("TESSERACT_CMD")
        if cmd:
            pytesseract.pytesseract.tesseract_cmd = cmd
        elif shutil.which("tesseract") is None:
            # Common Windows install path.
            default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.isfile(default):
                pytesseract.pytesseract.tesseract_cmd = default
            else:
                raise RuntimeError(
                    "Tesseract binary not found on PATH or at "
                    rf"C:\Program Files\Tesseract-OCR\tesseract.exe. "
                    "Install via 'winget install --id tesseract-ocr.tesseract' "
                    "or set TESSERACT_CMD."
                )

        # Confirm we can actually invoke it.
        version = pytesseract.get_tesseract_version()
        self._version = str(version)

    def warm_up(self) -> None:
        # Tesseract has no persistent session to warm; first call pays the
        # process spawn each time. Issue one dummy call so the version load /
        # data dir read isn't counted against the first real cell.
        dummy = np.full((48, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        # PSM 7 = treat image as a single text line.
        # We use image_to_data to get word-level confidences for an aggregate
        # confidence score consistent with what other engines produce.
        data = self._pyt.image_to_data(
            rgb,
            config="--psm 7",
            output_type=self._pyt.Output.DICT,
        )
        words = []
        confs: list[float] = []
        for w, c in zip(data.get("text", []), data.get("conf", [])):
            w = (w or "").strip()
            if not w:
                continue
            words.append(w)
            try:
                ci = float(c)
                if ci >= 0:
                    confs.append(ci)
            except (TypeError, ValueError):
                continue
        text = " ".join(words).strip()
        confidence = (sum(confs) / len(confs) / 100.0) if confs else 0.0
        return text, confidence


ENGINE = TesseractEngine
