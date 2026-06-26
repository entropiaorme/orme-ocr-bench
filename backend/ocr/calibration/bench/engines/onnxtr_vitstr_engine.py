"""OnnxTR ViTSTR adapter.

ViTSTR-small: ViT encoder + CTC head, ONNX Runtime backend. Pure-transformer
counterpart to the CRNN baseline; useful as a same-pipeline comparison
point against PARSeq's permuted-AR head. ``symmetric_pad=True`` for the
narrow-crop failure mode.
"""

from __future__ import annotations

from backend.ocr.calibration.bench.engines._onnxtr_common import OnnxTRRecogEngine


class OnnxTRViTSTREngine(OnnxTRRecogEngine):
    name = "onnxtr_vitstr"
    ARCH = "vitstr_small"


ENGINE = OnnxTRViTSTREngine
