"""Florence-2-large adapter for the OCR bench.

Microsoft Florence-2-large (~0.77B params, MIT) — the headline VLM tier of
the Florence-2 family. Same task-prompt interface as the base variant; we
invoke the ``<OCR>`` task and read off the transcription.

Notes:
- Uses ``trust_remote_code=True``; Florence ships custom modelling code on
  the HF hub. Loaded from ``microsoft/Florence-2-large``.
- Florence is pretrained on document-scale inputs; we upscale 4x with
  Lanczos before inference to bring tiny game-UI cells closer to the
  training distribution.
- Confidence is the mean softmax probability across generated tokens.
- CPU-only on this bench machine (AMD/Windows, no CUDA path for PyTorch).
- Inference is noticeably slower than the base variant; expect ~25-40 min
  wall time across the 594-cell corpus.
"""

from __future__ import annotations

import cv2
import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine, torch_device

_MODEL_ID = "microsoft/Florence-2-large"
_TASK = "<OCR>"
_UPSCALE = 4


class Florence2LargeEngine(OCREngine):
    name = "florence2_large"

    def __init__(self) -> None:
        try:
            import torch
            from PIL import Image  # noqa: F401  (used in read_text)
            from transformers import AutoModelForCausalLM, AutoProcessor
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "transformers / torch / Pillow not installed. "
                "pip install torch transformers pillow einops"
            ) from exc

        self._torch = torch
        self.device = torch_device()
        # On CUDA use fp16 to halve activation/weight memory (matters on small
        # cards); CPU stays fp32 (no fp16 CPU kernels for this path).
        self._dtype = torch.float16 if self.device == "cuda" else torch.float32
        self._processor = AutoProcessor.from_pretrained(
            _MODEL_ID, trust_remote_code=True
        )
        # ``attn_implementation="eager"`` works around a known incompat between
        # Florence-2's vendored modelling code and transformers >=4.55, where
        # the SDPA dispatch path checks ``_supports_sdpa`` on the model — an
        # attribute Florence's class doesn't define. Eager attention sidesteps
        # the dispatch entirely.
        self._model = AutoModelForCausalLM.from_pretrained(
            _MODEL_ID, trust_remote_code=True, attn_implementation="eager",
            torch_dtype=self._dtype,
        )
        self._model.to(self.device)
        self._model.eval()

    def warm_up(self) -> None:
        dummy = np.full((48, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        from PIL import Image

        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        if _UPSCALE != 1:
            pil = pil.resize(
                (pil.width * _UPSCALE, pil.height * _UPSCALE), Image.LANCZOS
            )

        inputs = self._processor(text=_TASK, images=pil, return_tensors="pt")
        input_ids = inputs["input_ids"].to(self.device)
        pixel_values = inputs["pixel_values"].to(self.device, dtype=self._dtype)
        with self._torch.no_grad():
            out = self._model.generate(
                input_ids=input_ids,
                pixel_values=pixel_values,
                max_new_tokens=64,
                num_beams=1,
                do_sample=False,
                return_dict_in_generate=True,
                output_scores=True,
            )

        generated_text = self._processor.batch_decode(
            out.sequences, skip_special_tokens=False
        )[0]
        parsed = self._processor.post_process_generation(
            generated_text, task=_TASK, image_size=(pil.width, pil.height)
        )
        text = parsed.get(_TASK, "") if isinstance(parsed, dict) else ""
        if not isinstance(text, str):
            text = str(text)
        text = text.strip()

        if out.scores:
            ids = out.sequences[0]
            probs_list: list[float] = []
            for step_idx, logits in enumerate(out.scores):
                tok_id = int(ids[step_idx + 1].item())
                probs = self._torch.softmax(logits[0], dim=-1)
                probs_list.append(float(probs[tok_id].item()))
            confidence = sum(probs_list) / len(probs_list) if probs_list else 0.0
        else:
            confidence = 0.0

        return text, confidence


ENGINE = Florence2LargeEngine
