"""dots.ocr adapter via HuggingFace transformers (trust_remote_code).

Uses ``rednote-hilab/dots.ocr`` (~1.7B params, ~6 GB on disk). Bespoke licence
agreement on the HF model page — read it carefully before any redistribution
or downstream packaging. The licence is **not** Apache/MIT/CC; this engine
is benched here as research output and is **not shippable by default**.

Architecturally a Qwen2.5-VL-style multimodal LLM, instruction-tuned for
document parsing. Loaded with ``trust_remote_code=True`` since the model ships
custom modelling code on the hub.

Bench note: the model card explicitly warns of "repetition/hallucination on
inputs with high character-to-pixel ratios" — which is exactly our regime
(tightly cropped UI cells, 12-19px tall). We bench the failure shape rather
than try to engineer around it.

Hardware: CPU-only on this machine (RX 6750 XT + Windows; no CUDA / no viable
PyTorch GPU path; flash-attn unavailable). Wall time expectation 60-120
minutes; if it overruns the 2-hour cap, the partial result on disk is the
research output (recorded via notes.md).

Confidence: geometric mean of per-step max-softmax probabilities for the
generated tokens.
"""

from __future__ import annotations

import math

import cv2
import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine

_MODEL_ID = "rednote-hilab/dots.ocr"
_PROMPT = (
    "Please output the text content from the image."
)


class DotsOcrEngine(OCREngine):
    name = "dots_ocr"

    def __init__(self) -> None:
        try:
            import torch
            from PIL import Image  # noqa: F401
            from transformers import AutoModelForCausalLM, AutoProcessor
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "transformers / torch / Pillow not installed. "
                "pip install torch transformers Pillow"
            ) from exc

        self._torch = torch
        self._dtype = torch.float32  # CPU path
        # trust_remote_code=True: dots.ocr ships custom modelling code on the
        # hub. The licence on that hub repo is bespoke — see module docstring.
        self._processor = AutoProcessor.from_pretrained(
            _MODEL_ID, trust_remote_code=True,
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            _MODEL_ID,
            torch_dtype=self._dtype,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        )
        self._model.eval()

    def warm_up(self) -> None:
        dummy = np.full((48, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        from PIL import Image

        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": pil},
                    {"type": "text", "text": _PROMPT},
                ],
            }
        ]

        text_prompt = self._processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
        )
        inputs = self._processor(
            text=[text_prompt],
            images=[pil],
            padding=True,
            return_tensors="pt",
        )

        input_len = inputs["input_ids"].shape[1] if "input_ids" in inputs else 0

        with self._torch.no_grad():
            out = self._model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=512,
                return_dict_in_generate=True,
                output_scores=True,
            )

        seq = out.sequences[0]
        gen_ids = seq[input_len:] if input_len else seq
        decoded = self._processor.batch_decode(
            gen_ids.unsqueeze(0),
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )[0].strip()

        if out.scores:
            log_probs: list[float] = []
            for step_idx, logits in enumerate(out.scores):
                if step_idx >= gen_ids.shape[0]:
                    break
                tok_id = int(gen_ids[step_idx].item())
                probs = self._torch.softmax(logits[0], dim=-1)
                p = float(probs[tok_id].item())
                log_probs.append(math.log(p + 1e-10))
            confidence = math.exp(sum(log_probs) / len(log_probs)) if log_probs else 0.0
        else:
            confidence = 0.0

        return decoded, confidence


ENGINE = DotsOcrEngine
