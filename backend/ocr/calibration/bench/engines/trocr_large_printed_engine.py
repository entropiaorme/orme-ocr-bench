"""TrOCR-large-printed adapter via HuggingFace transformers.

Re-bench of the TrOCR family using ``microsoft/trocr-large-printed`` (~1.4 GB
FP32 weights, MIT). An earlier ``trocr-base-printed`` benchmark was disqualified by a
narrow-crop hallucination failure mode (e.g. "DEXTERITY" -> "DEXTERITY - 1
DAYS WITH"). Two changes attempt to fix it here:

1. Right-pad each crop with white to a 16:1 aspect ratio before handing it to
   the processor. Wider context lets the decoder commit to a stop earlier.
2. Greedy decode with ``num_beams=1, early_stopping=True, length_penalty=1.0``
   instead of the more generous defaults the base variant inherited.

Confidence is the mean of per-step softmax probabilities for the generated
tokens (no calibrated per-character confidence is exposed by TrOCR).
"""

from __future__ import annotations

import math

import cv2
import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine, torch_device

_MODEL_ID = "microsoft/trocr-large-printed"


class TrOCRLargePrintedEngine(OCREngine):
    name = "trocr_large_printed"

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
        self.device = torch_device()
        # fp32: this 1.4 GB model fits on a 4 GB card without halving, and its
        # white-pad preprocessing path mixes dtypes under fp16. Keep it simple.
        self._dtype = torch.float32
        self._processor = TrOCRProcessor.from_pretrained(_MODEL_ID)
        self._model = VisionEncoderDecoderModel.from_pretrained(
            _MODEL_ID, low_cpu_mem_usage=False
        )
        self._model.to(self.device)
        self._model.eval()

    def warm_up(self) -> None:
        dummy = np.full((48, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    @staticmethod
    def _pad_to_aspect(crop_bgr: np.ndarray, ratio: float = 16.0) -> np.ndarray:
        h, w = crop_bgr.shape[:2]
        target_w = max(w, int(round(h * ratio)))
        pad_w = target_w - w
        if pad_w <= 0:
            return crop_bgr
        return cv2.copyMakeBorder(
            crop_bgr, 0, 0, 0, pad_w, cv2.BORDER_CONSTANT, value=(255, 255, 255)
        )

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        from PIL import Image

        padded = self._pad_to_aspect(crop_bgr, ratio=16.0)
        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pixel_values = self._processor(images=pil, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(self.device, dtype=self._dtype)
        self._mark_model_start()
        with self._torch.no_grad():
            out = self._model.generate(
                pixel_values,
                num_beams=1,
                early_stopping=True,
                length_penalty=1.0,
                return_dict_in_generate=True,
                output_scores=True,
                max_new_tokens=64,
            )
        ids = out.sequences[0]
        text = self._processor.batch_decode(
            out.sequences, skip_special_tokens=True,
        )[0]

        if out.scores:
            log_probs: list[float] = []
            for step_idx, logits in enumerate(out.scores):
                tok_id = int(ids[step_idx + 1].item())
                probs = self._torch.softmax(logits[0], dim=-1)
                p = float(probs[tok_id].item())
                log_probs.append(math.log(p + 1e-10))
            confidence = math.exp(sum(log_probs) / len(log_probs)) if log_probs else 0.0
        else:
            confidence = 0.0

        return text, confidence


ENGINE = TrOCRLargePrintedEngine
