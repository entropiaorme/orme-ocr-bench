"""OnnxTR VIPTR adapter.

VIPTR-tiny: lightweight visual-permuted transformer for text recognition,
ONNX Runtime backend. Smaller-footprint transformer alternative to
ViTSTR/PARSeq. ``symmetric_pad=True`` for the narrow-crop failure mode.
"""

from __future__ import annotations

from backend.ocr.calibration.bench.engines._onnxtr_common import OnnxTRRecogEngine


class OnnxTRVIPTREngine(OnnxTRRecogEngine):
    name = "onnxtr_viptr"
    ARCH = "viptr_tiny"


ENGINE = OnnxTRVIPTREngine
