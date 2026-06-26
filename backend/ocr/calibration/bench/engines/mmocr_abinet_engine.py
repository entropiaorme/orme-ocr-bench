"""MMOCR ABINet adapter.

ABINet (Autonomous Bidirectional Iterative Language Model coupling, CVPR 2021)
combines a vision module with an explicit autoregressive language model that
iteratively refines predictions. The LM coupling means it tends to recover
lexically-plausible English strings well — relevant for the skill-name half of
our corpus where short English tokens like "Light Armor" benefit from a
language prior.

Loaded via ``mmocr.apis.MMOCRInferencer(rec="abinet")``; the recogniser-only
mode skips detection (our crops are already tightly cropped single-line cells).

Confidence is the per-cell score returned by the recogniser
(``rec_scores[0]``), which is a softmax-aggregated character probability.
"""

from __future__ import annotations

import contextlib
import io
import os

import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine


class MMOCRABINetEngine(OCREngine):
    name = "mmocr_abinet"

    def __init__(self) -> None:
        try:
            from mmocr.apis import MMOCRInferencer
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "mmocr not installed. See agents/4/ROOM.md for the install "
                "recipe (torch 2.0.0 + mmcv 2.0.1 + mmdet 3.1.0 + mmocr 1.0.1)."
            ) from exc

        # MMOCRInferencer prints download progress and an inference banner to
        # stdout even on cached weights. Suppress so the runner's stdout stream
        # stays clean of non-JSON noise.
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self._inferencer = MMOCRInferencer(rec="abinet", device="cpu")

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


ENGINE = MMOCRABINetEngine
