"""MMOCR SATRN adapter.

SATRN (Self-Attention Text Recognition Network, CVPRW 2020) is a
self-attention-over-CRNN recogniser. Architecturally it sits between the
older CTC-CRNN family and the fully attention-based ABINet/SAR family.
Included for architectural completeness in the benchmark sweep — it gives
us a "transformer encoder, no explicit language model" data point alongside
ABINet (LM-coupled) and RobustScanner (position-aware, no LM).

Loaded via ``mmocr.apis.MMOCRInferencer(rec="satrn")``; recogniser-only
mode (no detection) since cells are pre-cropped.

Confidence is the per-cell score returned by the recogniser
(``rec_scores[0]``), which is a softmax-aggregated character probability.
"""

from __future__ import annotations

import contextlib
import io

import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine, torch_device


class MMOCRSATRNEngine(OCREngine):
    name = "mmocr_satrn"

    def __init__(self) -> None:
        try:
            from mmocr.apis import MMOCRInferencer
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "mmocr not installed. See SETUP.md (.venv-4) for the install "
                "recipe (torch 2.0.0 + mmcv 2.0.1 + mmdet 3.1.0 + mmocr 1.0.1)."
            ) from exc

        self.device = torch_device()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self._inferencer = MMOCRInferencer(rec="satrn", device=self.device)

    def warm_up(self) -> None:
        dummy = np.full((48, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            out = self._inferencer(crop_bgr, return_vis=False)
        pred = out["predictions"][0]
        texts = pred.get("rec_texts") or [""]
        scores = pred.get("rec_scores") or [0.0]
        return texts[0], float(scores[0])


ENGINE = MMOCRSATRNEngine
