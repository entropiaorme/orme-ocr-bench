"""PP-OCR adapter: thin wrapper around the existing PPocrRecReader."""

from __future__ import annotations

import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine
from backend.ocr.ppocr_rec_reader import PPocrRecReader


class PPOCREngine(OCREngine):
    name = "ppocr"

    def __init__(self) -> None:
        self._reader = PPocrRecReader()
        self.provider = getattr(self._reader, "provider", None)
        self.device = (
            "cuda" if self.provider == "CUDAExecutionProvider"
            else "directml" if self.provider == "DmlExecutionProvider"
            else "cpu"
        )

    supports_batch = True

    def warm_up(self) -> None:
        self._reader.warm_up()

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        return self._reader.read_text(crop_bgr)

    def read_batch(self, crops_bgr: list[np.ndarray]) -> list[tuple[str, float]]:
        self._mark_model_start()
        return self._reader.read_batch(crops_bgr)


ENGINE = PPOCREngine
