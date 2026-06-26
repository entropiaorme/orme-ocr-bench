"""OnnxTR MASTER adapter.

MASTER: self-attention transformer recogniser (multi-aspect non-local
attention), ONNX Runtime backend. Heavier transformer architecture than
ViTSTR/VIPTR; rounds out the OnnxTR family. ``symmetric_pad=True`` for the
narrow-crop failure mode.
"""

from __future__ import annotations

from backend.ocr.calibration.bench.engines._onnxtr_common import OnnxTRRecogEngine


class OnnxTRMasterEngine(OnnxTRRecogEngine):
    name = "onnxtr_master"
    ARCH = "master"


ENGINE = OnnxTRMasterEngine
