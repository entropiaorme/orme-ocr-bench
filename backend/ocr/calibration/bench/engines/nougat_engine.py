"""Nougat adapter via HuggingFace transformers.

Nougat (``facebook/nougat-base``, CC-BY-NC-4.0) is Meta AI's academic-
document OCR: a Swin-style encoder + mBART decoder trained on arXiv-style
PDFs to emit Markdown / LaTeX. License is non-commercial, but this bench
is research, not deployment.

Like Donut, Nougat is included as a **wrong-domain control**. It expects
page-scale academic-paper input and produces structured output (headings,
math, etc.); cropped game-UI cells are out of distribution on every axis.
The failure shape (likely empty output, math hallucination, or document
scaffolding) is itself the research signal.

Cell crops are upscaled to ~960 px wide before inference for the same
reason as the Donut adapter.

Confidence is the mean per-step softmax probability of the generated
tokens, mirroring the TrOCR adapter.
"""

from __future__ import annotations

import math
import re

import cv2
import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine, torch_device

_MODEL_ID = "facebook/nougat-base"
_TARGET_WIDTH = 960


class NougatEngine(OCREngine):
    name = "nougat"

    def __init__(self) -> None:
        try:
            import torch
            from PIL import Image  # noqa: F401
            from transformers import NougatProcessor, VisionEncoderDecoderModel
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "transformers / torch / Pillow not installed. "
                "pip install torch transformers Pillow sentencepiece"
            ) from exc

        self._torch = torch
        self.device = torch_device()
        self._processor = NougatProcessor.from_pretrained(_MODEL_ID)
        self._model = VisionEncoderDecoderModel.from_pretrained(
            _MODEL_ID, low_cpu_mem_usage=False
        )
        self._model.to(self.device)
        self._model.eval()

    def warm_up(self) -> None:
        dummy = np.full((48, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    @staticmethod
    def _upscale(crop_bgr: np.ndarray, target_w: int = _TARGET_WIDTH) -> np.ndarray:
        h, w = crop_bgr.shape[:2]
        if w >= target_w:
            return crop_bgr
        scale = target_w / float(w)
        new_w = target_w
        new_h = max(1, int(round(h * scale)))
        return cv2.resize(crop_bgr, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        from PIL import Image

        upscaled = self._upscale(crop_bgr)
        rgb = cv2.cvtColor(upscaled, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pixel_values = self._processor(images=pil, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(self.device)

        with self._torch.no_grad():
            out = self._model.generate(
                pixel_values,
                min_length=1,
                max_new_tokens=128,
                num_beams=1,
                early_stopping=True,
                length_penalty=1.0,
                bad_words_ids=[[self._processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
                output_scores=True,
            )

        ids = out.sequences[0]
        raw = self._processor.batch_decode(out.sequences, skip_special_tokens=True)[0]
        text = self._processor.post_process_generation(raw, fix_markdown=False) \
            if hasattr(self._processor, "post_process_generation") else raw
        # Flatten any markdown / math scaffolding to a plain string for the bench.
        text = re.sub(r"\s+", " ", text).strip()

        if out.scores:
            log_probs: list[float] = []
            for step_idx, logits in enumerate(out.scores):
                # Nougat starts decode from BOS at sequences[0]; first generated
                # token is sequences[1]. Same offset as TrOCR.
                tok_pos = step_idx + 1
                if tok_pos >= ids.shape[0]:
                    break
                tok_id = int(ids[tok_pos].item())
                probs = self._torch.softmax(logits[0], dim=-1)
                p = float(probs[tok_id].item())
                log_probs.append(math.log(p + 1e-10))
            confidence = math.exp(sum(log_probs) / len(log_probs)) if log_probs else 0.0
        else:
            confidence = 0.0

        return text, confidence


ENGINE = NougatEngine
