"""OnnxTR PARSeq adapter.

PARSeq (Permuted Autoregressive Sequence) recogniser, ONNX Runtime backend.
PARSeq's permuted-AR training + iterative refinement is the headline
candidate for this OnnxTR family per the deep-research notes. Bundled
checkpoint covers 62 case-sensitive alphanumerics + 32 punctuation marks,
which is sufficient for cells like "Electro Kinetic (Dmg)" and "98.1%".
``symmetric_pad=True`` to mitigate narrow-crop hallucination.
"""

from __future__ import annotations

from backend.ocr.calibration.bench.engines._onnxtr_common import OnnxTRRecogEngine


class OnnxTRParseqEngine(OnnxTRRecogEngine):
    name = "onnxtr_parseq"
    ARCH = "parseq"


ENGINE = OnnxTRParseqEngine
