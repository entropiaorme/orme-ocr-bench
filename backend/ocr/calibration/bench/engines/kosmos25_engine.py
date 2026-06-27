"""Kosmos-2.5 adapter via HuggingFace transformers.

Uses ``microsoft/kosmos-2.5`` (~1.3B params, MIT licence). Document-level
multimodal model designed for full-page layout + markdown reading. Cropped
single-line cells are firmly out of distribution for it; we still bench it
because the deep-research scope covers the full breadth of multimodal OCR
contenders, and "did not work on tiny cells" is itself a documented research
output.

The model card explicitly warns: "there is a risk of hallucination during the
generation process, and it CAN NOT guarantee the accuracy of all OCR/Markdown
results." Expect failures, especially on very narrow numeric crops.

Preprocessing: each crop is upscaled 4x with cv2 INTER_CUBIC before inference,
since Kosmos's image encoder operates over much larger native resolutions and
underpopulated patches are a documented failure mode.

Confidence: geometric mean of per-step max-softmax probabilities for the
generated tokens, mirroring the trocr/got_ocr2 adapters.

Bench note: CPU-only on this machine (RX 6750 XT + Windows; no CUDA / no
viable PyTorch GPU path). Expect ~30-60 minutes wall time for the 594-cell
sweep; if it overruns the 2-hour cap, the partial result on disk is the
research output (recorded via notes.md).
"""

from __future__ import annotations

import math

import cv2
import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine, torch_device

_MODEL_ID = "microsoft/kosmos-2.5"
_PROMPT = "<ocr>"
_UPSCALE = 4


class Kosmos25Engine(OCREngine):
    name = "kosmos25"

    def __init__(self) -> None:
        try:
            import torch
            from PIL import Image  # noqa: F401
            from transformers import AutoProcessor, Kosmos2_5ForConditionalGeneration
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "transformers / torch / Pillow not installed. "
                "pip install torch transformers Pillow"
            ) from exc

        self._torch = torch
        self.device = torch_device()
        # Kosmos-2.5 prefers bfloat16 on GPU (the model card's GPU path);
        # CPU has no bf16 kernels for it, so fall back to fp32 there.
        self._dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
        self._processor = AutoProcessor.from_pretrained(_MODEL_ID)
        self._model = Kosmos2_5ForConditionalGeneration.from_pretrained(
            _MODEL_ID,
            torch_dtype=self._dtype,
            low_cpu_mem_usage=True,
        )
        self._model.to(self.device)
        self._model.eval()

    def warm_up(self) -> None:
        dummy = np.full((48, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        from PIL import Image

        h, w = crop_bgr.shape[:2]
        upscaled = cv2.resize(
            crop_bgr,
            (max(1, w * _UPSCALE), max(1, h * _UPSCALE)),
            interpolation=cv2.INTER_CUBIC,
        )
        rgb = cv2.cvtColor(upscaled, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)

        inputs = self._processor(text=_PROMPT, images=pil, return_tensors="pt")
        # Drop the height/width sidecars Kosmos adds; the generator doesn't
        # accept them as kwargs.
        inputs.pop("height", None)
        inputs.pop("width", None)
        if "flattened_patches" in inputs:
            inputs["flattened_patches"] = inputs["flattened_patches"].to(self._dtype)

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
        text = self._processor.batch_decode(
            gen_ids.unsqueeze(0), skip_special_tokens=True,
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

        return text, confidence


ENGINE = Kosmos25Engine
