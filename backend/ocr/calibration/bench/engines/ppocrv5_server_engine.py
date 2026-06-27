"""PP-OCRv5 multilingual server recognition adapter.

Architecture: PaddleOCR ``PP-OCRv5_server_rec`` — heavier (~84 MB)
multilingual v5 recognition model, same 18,383-char dict as the mobile
multilingual variant but a wider/deeper backbone. Expected to lead the
v5 family on hard cells at the cost of higher latency and RSS.

Weights: ``bukuroo/PPOCRv5-ONNX/ppocrv5-server-rec.onnx``. Shares the
``ppocrv5_multilingual_dict.txt`` (18,383 chars) bundled in the same
repo. Cached under ``.venv-1/models/``.

Inference loop reuses :class:`_PPocrV5Reader` from
``ppocrv5_mobile_engine`` (same v5 ONNX softmax-in-graph convention; the
double-softmax fix applies identically).
"""

from __future__ import annotations

import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine
from backend.ocr.calibration.bench.engines.ppocrv5_mobile_engine import (
    MODELS_DIR,
    _PPocrV5Reader,
)


class PPOCRv5ServerEngine(OCREngine):
    name = "ppocrv5_server"

    def __init__(self) -> None:
        self._reader = _PPocrV5Reader(
            MODELS_DIR / "ppocrv5_server.onnx",
            MODELS_DIR / "ppocrv5_multilingual_dict.txt",
        )
        self._adopt_device(self._reader)

    def warm_up(self) -> None:
        self._reader.warm_up()

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        return self._reader.read_text(crop_bgr)


ENGINE = PPOCRv5ServerEngine
