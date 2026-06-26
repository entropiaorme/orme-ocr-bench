"""Donut adapter via HuggingFace transformers.

Donut (``naver-clova-ix/donut-base``, MIT) is an OCR-free document-
understanding transformer: a Swin encoder + BART decoder trained to read
*whole document images* and emit structured tokens. It is included in the
bench as a deliberate **wrong-domain control**: the corpus is per-cell
crops of game-UI text, which is twice removed from Donut's training
distribution (cell-level rather than page-level, game UI rather than
scanned documents). The expectation is that it performs poorly; the
*shape* of the failure (refusal, hallucination of document scaffolding,
empty output) is itself the research signal.

Donut needs ``trust_remote_code=True`` for some processor versions; its
preprocessor is page-scale, so cropped cells are upscaled to ~960 px wide
with cubic interpolation before inference to push the input back toward
in-distribution scale.

Confidence is the mean per-step softmax probability of the generated
tokens, mirroring the TrOCR adapter.
"""

from __future__ import annotations

import math
import re

import cv2
import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine

_MODEL_ID = "naver-clova-ix/donut-base"
_TARGET_WIDTH = 960
_TASK_PROMPT = "<s_synthdog>"


class DonutEngine(OCREngine):
    name = "donut"

    def __init__(self) -> None:
        try:
            import torch
            from PIL import Image  # noqa: F401
            from transformers import DonutProcessor, VisionEncoderDecoderModel
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "transformers / torch / Pillow not installed. "
                "pip install torch transformers Pillow sentencepiece"
            ) from exc

        self._torch = torch
        self._processor = DonutProcessor.from_pretrained(_MODEL_ID)
        self._model = VisionEncoderDecoderModel.from_pretrained(
            _MODEL_ID, low_cpu_mem_usage=False
        )
        self._model.to("cpu")
        self._model.eval()

        tokenizer = self._processor.tokenizer
        prompt_ids = tokenizer(_TASK_PROMPT, add_special_tokens=False).input_ids
        if not prompt_ids:
            prompt_ids = [tokenizer.bos_token_id]
        self._decoder_input_ids = torch.tensor([prompt_ids], dtype=torch.long)

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

        with self._torch.no_grad():
            out = self._model.generate(
                pixel_values,
                decoder_input_ids=self._decoder_input_ids,
                max_new_tokens=64,
                num_beams=1,
                early_stopping=True,
                length_penalty=1.0,
                pad_token_id=self._processor.tokenizer.pad_token_id,
                eos_token_id=self._processor.tokenizer.eos_token_id,
                return_dict_in_generate=True,
                output_scores=True,
            )

        ids = out.sequences[0]
        raw = self._processor.batch_decode(out.sequences, skip_special_tokens=False)[0]
        # Strip donut-style task / structural tokens; what remains is the
        # closest thing to "the text Donut thought was on the page".
        text = re.sub(r"<.*?>", "", raw)
        text = self._processor.tokenizer.decode(
            self._processor.tokenizer(text, add_special_tokens=False).input_ids,
            skip_special_tokens=True,
        ).strip()

        if out.scores:
            log_probs: list[float] = []
            prompt_len = self._decoder_input_ids.shape[1]
            for step_idx, logits in enumerate(out.scores):
                tok_pos = prompt_len + step_idx
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


ENGINE = DonutEngine
