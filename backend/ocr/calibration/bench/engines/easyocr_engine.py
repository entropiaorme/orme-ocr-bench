"""EasyOCR adapter.

EasyOCR is PyTorch-based; on AMD/Windows it has no GPU acceleration path
(no CUDA, no native ROCm on Windows), so it runs CPU-only here. Detection +
recognition both run by default; for our pre-cropped single-line cells the
detection step finds essentially the whole crop as one box, so the cost is
dominated by recognition.

Returns the highest-scoring detection's text + confidence; if EasyOCR
detects multiple boxes (rare on tight crops), we concatenate texts and
average confidences.
"""

from __future__ import annotations

import cv2
import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine, torch_device


class EasyOCREngine(OCREngine):
    name = "easyocr"

    def __init__(self) -> None:
        try:
            import easyocr
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "easyocr not installed. pip install easyocr"
            ) from exc
        # Use CUDA when this host has it (NVIDIA breadth run); CPU otherwise
        # (AMD/Windows has no CUDA path, so EasyOCR stays CPU there).
        self.device = torch_device()
        self._reader = easyocr.Reader(
            ["en"], gpu=(self.device == "cuda"), verbose=False
        )

    def warm_up(self) -> None:
        # First call is heavily warmed by EasyOCR's model loading; do an
        # explicit dummy pass so steady-state numbers don't include any
        # remaining lazy init.
        dummy = np.full((48, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        results = self._reader.readtext(rgb, detail=1, paragraph=False)
        if not results:
            return "", 0.0
        texts = [r[1] for r in results]
        confs = [float(r[2]) for r in results]
        return " ".join(texts).strip(), sum(confs) / len(confs)


ENGINE = EasyOCREngine
