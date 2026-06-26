"""TrOCR adapter via HuggingFace transformers.

Uses ``microsoft/trocr-base-printed`` (~334 MB) — the printed-text variant,
which fits the EU panel UI text rendering better than the handwriting variant.

TrOCR is transformer-based (ViT encoder + RoBERTa decoder); inference is
expensive (often >300 ms/cell on CPU) and there is no AMD GPU acceleration
path on Windows for PyTorch out of the box, so the bench treats this as the
"upper accuracy bound at CPU cost" data point.

Confidence comes from the geometric mean of per-token softmax probabilities
during generation, mirroring PP-OCR's geometric-mean-of-character-probs
approach.
"""

from __future__ import annotations

import math

import cv2
import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine

_MODEL_ID = "microsoft/trocr-base-printed"


class TrOCREngine(OCREngine):
    name = "trocr"

    def __init__(self) -> None:
        try:
            import torch
            from PIL import Image  # noqa: F401  (used in read_text)
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "transformers / torch / Pillow not installed. "
                "pip install torch transformers Pillow"
            ) from exc

        self._torch = torch
        self._processor = TrOCRProcessor.from_pretrained(_MODEL_ID)
        self._model = VisionEncoderDecoderModel.from_pretrained(_MODEL_ID)
        self._model.eval()

    def warm_up(self) -> None:
        dummy = np.full((48, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        from PIL import Image

        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pixel_values = self._processor(images=pil, return_tensors="pt").pixel_values
        with self._torch.no_grad():
            out = self._model.generate(
                pixel_values,
                return_dict_in_generate=True,
                output_scores=True,
                max_new_tokens=64,
            )
        ids = out.sequences[0]
        text = self._processor.batch_decode(
            out.sequences, skip_special_tokens=True,
        )[0]

        # Aggregate per-token confidence as the geometric mean of per-step
        # max-softmax probabilities for the generated tokens. ``out.scores``
        # is a tuple of (1, vocab) tensors, one per generated step (excluding
        # the BOS token at position 0).
        if out.scores:
            log_probs: list[float] = []
            for step_idx, logits in enumerate(out.scores):
                # Token at sequences[step_idx + 1] corresponds to scores[step_idx].
                tok_id = int(ids[step_idx + 1].item())
                probs = self._torch.softmax(logits[0], dim=-1)
                p = float(probs[tok_id].item())
                log_probs.append(math.log(p + 1e-10))
            confidence = math.exp(sum(log_probs) / len(log_probs)) if log_probs else 0.0
        else:
            confidence = 0.0

        return text, confidence


ENGINE = TrOCREngine
