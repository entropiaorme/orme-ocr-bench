"""OpenOCR / SVTRv2-mobile adapter.

OpenOCR (Topdu/OpenOCR, ICCV 2025) ships SVTRv2 — a CTC recogniser with a
visual-transformer encoder and Multi-Size Resizing baked in for irregular
text. Apache 2.0. The PyPI package ``openocr-python`` exposes the
recognition-only path via ``OpenRecognizer``; we use ``mode='mobile'`` with
``backend='onnx'`` to avoid pulling in PyTorch and to run inference through
ONNX Runtime (CPU on this AMD/Windows box; the package's auto-download
fetches ``openocr_rec_model.onnx`` from ModelScope on first construction).

SVTRv2's MSR handles narrow / variable-width crops out-of-the-box, so we
pass the BGR ndarray straight through without padding. Confidence is the
recogniser's per-line score (CTC-derived softmax aggregate).
"""

from __future__ import annotations

import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine


class OpenOCRSVTRv2Engine(OCREngine):
    name = "openocr_svtrv2"

    def __init__(self) -> None:
        try:
            from openocr.tools.infer_e2e import OpenRecognizer
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "openocr-python not installed. pip install openocr-python"
            ) from exc
        # mobile + onnx avoids pulling torch and routes through onnxruntime.
        # use_gpu='false' is deliberate on AMD/Windows: openocr-python's
        # GPU path hardcodes a (Tensorrt, CUDA, CPU) provider list, so
        # use_gpu='true' silently falls back to CPU here (no CUDA on
        # AMD, and DmlExecutionProvider is not in their hardcoded list).
        # Reaching DirectML would require monkey-patching openocr-python
        # or contributing an upstream patch; out of bench scope.
        self._rec = OpenRecognizer(
            mode="mobile",
            backend="onnx",
            use_gpu="false",
        )

    def warm_up(self) -> None:
        dummy = np.full((48, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        results = self._rec(img_numpy=crop_bgr)
        if not results:
            return "", 0.0
        r = results[0]
        text = str(r.get("text", "") or "")
        score = float(r.get("score", 0.0) or 0.0)
        return text, score


ENGINE = OpenOCRSVTRv2Engine
