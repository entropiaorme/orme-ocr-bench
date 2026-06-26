"""OnnxTR CRNN-MobileNet-V3 (small) adapter.

Light CRNN baseline: MobileNet-V3-small backbone + CTC head, served via
ONNX Runtime. EasyOCR-class architecture but trained inside the docTR
pipeline with better weights. Runs on DirectML where available
(AMD/Windows), CPU otherwise. ``symmetric_pad=True`` to mitigate the
narrow-crop failure mode on tight single-line cells.
"""

from __future__ import annotations

from backend.ocr.calibration.bench.engines._onnxtr_common import OnnxTRRecogEngine


class OnnxTRCrnnMobileEngine(OnnxTRRecogEngine):
    name = "onnxtr_crnn_mobile"
    ARCH = "crnn_mobilenet_v3_small"


ENGINE = OnnxTRCrnnMobileEngine
