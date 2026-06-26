"""PP-OCR adapter: thin wrapper around the existing PPocrRecReader."""

from __future__ import annotations

import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine
from backend.ocr.ppocr_rec_reader import PPocrRecReader


class PPOCREngine(OCREngine):
    name = "ppocr"

    def __init__(self) -> None:
        self._reader = PPocrRecReader()

    def warm_up(self) -> None:
        self._reader.warm_up()

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        return self._reader.read_text(crop_bgr)


ENGINE = PPOCREngine
