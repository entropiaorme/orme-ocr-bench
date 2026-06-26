"""OnnxTR SAR (Show, Attend, Read) adapter.

SAR-ResNet31: attention-based autoregressive recogniser with a ResNet-31
backbone, ONNX Runtime backend. Older AR architecture predating PARSeq;
useful as an ablation point on attention-AR vs permuted-AR.
``symmetric_pad=True`` for the narrow-crop failure mode.
"""

from __future__ import annotations

from backend.ocr.calibration.bench.engines._onnxtr_common import OnnxTRRecogEngine


class OnnxTRSAREngine(OnnxTRRecogEngine):
    name = "onnxtr_sar"
    ARCH = "sar_resnet31"


ENGINE = OnnxTRSAREngine
