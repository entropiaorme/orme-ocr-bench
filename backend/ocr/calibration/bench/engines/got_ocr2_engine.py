"""GOT-OCR 2.0 adapter via HuggingFace transformers.

Uses ``stepfun-ai/GOT-OCR-2.0-hf`` (~580M decoder params, ~1.4 GB safetensors).
Apache 2.0 on the HF mirror; the original repo's licence is research-only —
both should be reviewed before any downstream redistribution.

GOT-OCR 2.0 is an end-to-end "OCR-2.0" model: ViT encoder + Qwen-style decoder
that emits the recognised text as a generation. It supports plain OCR over the
whole image; we use the plain mode here since each bench input is a tightly
cropped single-line cell, so the region-prompted ``ocr_box`` mode adds no
information. ``trust_remote_code`` is not required (the model has been merged
into transformers as ``GotOcr2ForConditionalGeneration``, available since
transformers >=4.50).

Confidence: geometric mean of per-step max-softmax probabilities for the
generated tokens (mirrors the trocr adapter).

Bench note: CPU-only on this machine (RX 6750 XT + Windows; no CUDA / no
viable PyTorch GPU path). Expect ~20-30 minutes wall time for the 594-cell
sweep.
"""

from __future__ import annotations

import math

import cv2
import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine, torch_device

_MODEL_ID = "stepfun-ai/GOT-OCR-2.0-hf"


class GotOcr2Engine(OCREngine):
    name = "got_ocr2"

    def __init__(self) -> None:
        try:
            import torch
            from PIL import Image  # noqa: F401  (used in read_text)
            from transformers import AutoProcessor, GotOcr2ForConditionalGeneration
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "transformers / torch / Pillow not installed. "
                "pip install torch transformers Pillow"
            ) from exc

        self._torch = torch
        self.device = torch_device()
        self._dtype = torch.float16 if self.device == "cuda" else torch.float32
        self._processor = AutoProcessor.from_pretrained(_MODEL_ID)
        self._model = GotOcr2ForConditionalGeneration.from_pretrained(
            _MODEL_ID,
            torch_dtype=self._dtype,
            low_cpu_mem_usage=True,
        )
        self._model.to(self.device)
        self._model.eval()

    def warm_up(self) -> None:
        dummy = np.full((32, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    # GOT-OCR2 is an OCR-purpose model whose serial autoregressive decode is
    # its pathological worst case; batched generate is how it is actually
    # deployed, so a true batched path is provided.
    supports_batch = True

    def read_batch(self, crops_bgr: list[np.ndarray]) -> list[tuple[str, float]]:
        from PIL import Image

        pils = [Image.fromarray(cv2.cvtColor(c, cv2.COLOR_BGR2RGB)) for c in crops_bgr]
        inputs = self._processor(images=pils, return_tensors="pt")
        input_len = inputs["input_ids"].shape[1] if "input_ids" in inputs else 0
        inputs = inputs.to(self.device)
        self._mark_model_start()
        with self._torch.no_grad():
            out = self._model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=256,
                return_dict_in_generate=True,
            )
        results: list[tuple[str, float]] = []
        for i in range(out.sequences.shape[0]):
            gen_ids = out.sequences[i][input_len:] if input_len else out.sequences[i]
            text = self._processor.decode(gen_ids, skip_special_tokens=True).strip()
            # Batched per-token confidence with padding is unreliable; the
            # batched track reports text + throughput, not per-cell confidence.
            results.append((text, 0.0))
        while len(results) < len(crops_bgr):
            results.append(("", 0.0))
        return results

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        from PIL import Image

        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        inputs = self._processor(images=pil, return_tensors="pt")
        input_len = inputs["input_ids"].shape[1] if "input_ids" in inputs else 0
        inputs = inputs.to(self.device)

        with self._torch.no_grad():
            out = self._model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=256,
                return_dict_in_generate=True,
                output_scores=True,
            )

        seq = out.sequences[0]
        gen_ids = seq[input_len:] if input_len else seq
        text = self._processor.decode(gen_ids, skip_special_tokens=True).strip()

        if out.scores:
            log_probs: list[float] = []
            for step_idx, logits in enumerate(out.scores):
                tok_id = int(gen_ids[step_idx].item()) if step_idx < gen_ids.shape[0] else None
                if tok_id is None:
                    continue
                probs = self._torch.softmax(logits[0], dim=-1)
                p = float(probs[tok_id].item())
                log_probs.append(math.log(p + 1e-10))
            confidence = math.exp(sum(log_probs) / len(log_probs)) if log_probs else 0.0
        else:
            confidence = 0.0

        return text, confidence


ENGINE = GotOcr2Engine
