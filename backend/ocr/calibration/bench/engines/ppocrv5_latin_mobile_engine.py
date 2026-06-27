"""PP-OCRv5 Latin-script mobile recognition adapter.

Architecture: PaddleOCR ``latin_PP-OCRv5_mobile_rec`` — v5 mobile model
trained on a 836-char Latin-script alphabet (covers Western/Central
European diacritics in addition to ASCII). ~14 MB.

Weights: ``itextresearch/itext-latin_PP-OCRv5_mobile_rec_infer/inference.onnx``.
Dict extracted from the bundled ``inference.yml`` and saved as
``ppocrv5_latin_dict.txt``. Cached under ``.venv-1/models/``.

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


class PPOCRv5LatinMobileEngine(OCREngine):
    name = "ppocrv5_latin_mobile"

    def __init__(self) -> None:
        self._reader = _PPocrV5Reader(
            MODELS_DIR / "ppocrv5_latin_mobile.onnx",
            MODELS_DIR / "ppocrv5_latin_dict.txt",
        )
        self._adopt_device(self._reader)

    def warm_up(self) -> None:
        self._reader.warm_up()

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        return self._reader.read_text(crop_bgr)


ENGINE = PPOCRv5LatinMobileEngine
