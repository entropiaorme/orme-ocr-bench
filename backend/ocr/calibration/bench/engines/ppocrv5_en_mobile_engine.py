"""PP-OCRv5 English-tuned mobile recognition adapter.

Architecture: PaddleOCR ``en_PP-OCRv5_mobile_rec`` — English-specific
v5 mobile model (~7.5 MB, 436-char alphabet). Same SVTR-LCNet recogniser
as ``ppocrv5_mobile`` but trained on an English-only character set, so
expected to be the most direct accuracy upgrade over the existing
``ppocr`` adapter on this English-only corpus.

Weights: ``itextresearch/itext-en_PP-OCRv5_mobile_rec_infer/inference.onnx``.
Dict extracted from the bundled ``inference.yml`` and saved as
``ppocrv5_en_dict.txt``. Cached under ``.venv-1/models/``.

Inference loop reuses :class:`_PPocrV5Reader` from
``ppocrv5_mobile_engine`` (same v5 ONNX shape and softmax-in-graph
convention, so the double-softmax fix and preprocessing recipe carry
over unchanged).
"""

from __future__ import annotations

import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine
from backend.ocr.calibration.bench.engines.ppocrv5_mobile_engine import (
    MODELS_DIR,
    _PPocrV5Reader,
)


class PPOCRv5EnMobileEngine(OCREngine):
    name = "ppocrv5_en_mobile"

    def __init__(self) -> None:
        self._reader = _PPocrV5Reader(
            MODELS_DIR / "ppocrv5_en_mobile.onnx",
            MODELS_DIR / "ppocrv5_en_dict.txt",
        )
        self._adopt_device(self._reader)

    def warm_up(self) -> None:
        self._reader.warm_up()

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        return self._reader.read_text(crop_bgr)


ENGINE = PPOCRv5EnMobileEngine
