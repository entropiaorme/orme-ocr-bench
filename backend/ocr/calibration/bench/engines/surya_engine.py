"""Surya OCR adapter for the OCR bench.

datalab-to/surya recognition pipeline. We bypass the layout/detection step
and run ``RecognitionPredictor`` directly on each pre-cropped cell.

LICENCE FLAG — NOT SHIPPABLE IN THE PUBLIC APP:
    Surya is dual-licensed: GPL-3.0 for code and CC-BY-NC-SA-4.0 for the
    pretrained weights. The non-commercial weights licence makes this engine
    research-only for the bench; it cannot be bundled into the shipped app.
    The bench includes it for breadth so the
    research output captures a "ran, here's how it scored" entry on the
    Surya recogniser line, alongside an explicit "not shippable" tag.

Notes:
- ``RecognitionPredictor`` requires a ``FoundationPredictor`` instance
  (mandatory in recent surya releases).
- Surya lazy-downloads model weights from HF on first instantiation; the
  initial run pays a substantial download cost.
- Confidence: surya emits per-line confidences (0..1) we surface directly.
- CPU-only on this bench machine (AMD/Windows, no CUDA path).
"""

from __future__ import annotations

import os

import cv2
import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine, torch_device


class SuryaEngine(OCREngine):
    name = "surya"

    def __init__(self) -> None:
        try:
            from PIL import Image  # noqa: F401
            from surya.foundation import FoundationPredictor
            from surya.recognition import RecognitionPredictor
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "surya-ocr not installed. pip install surya-ocr"
            ) from exc

        # Surya selects its torch device from the TORCH_DEVICE env var (it
        # otherwise auto-detects). Pin it to CUDA when this host has it so the
        # predictors load on GPU; surya owns tensor placement internally.
        self.device = torch_device()
        if self.device == "cuda":
            os.environ.setdefault("TORCH_DEVICE", "cuda")
        self._foundation = FoundationPredictor()
        self._recognizer = RecognitionPredictor(self._foundation)

    def warm_up(self) -> None:
        dummy = np.full((48, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        from PIL import Image

        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)

        predictions = self._recognizer([pil])
        if not predictions:
            return "", 0.0

        first = predictions[0]
        text, conf = _extract_text_conf(first)
        return text, conf


def _extract_text_conf(pred) -> tuple[str, float]:
    """Defensively pull text + confidence out of a surya prediction.

    Surya's return shape has changed across versions: older releases yielded
    an ``OCRResult`` with a ``text_lines`` list of ``TextLine`` objects;
    newer releases may yield a dict-like with ``text`` / ``confidence`` keys
    or a list of such dicts. We try the known shapes in order.
    """

    # Shape A: OCRResult-style with .text_lines
    text_lines = getattr(pred, "text_lines", None)
    if text_lines:
        texts = []
        confs = []
        for tl in text_lines:
            t = getattr(tl, "text", None)
            if t is None and isinstance(tl, dict):
                t = tl.get("text", "")
            c = getattr(tl, "confidence", None)
            if c is None and isinstance(tl, dict):
                c = tl.get("confidence", 0.0)
            texts.append(t or "")
            try:
                confs.append(float(c) if c is not None else 0.0)
            except (TypeError, ValueError):
                confs.append(0.0)
        if texts:
            return " ".join(t.strip() for t in texts).strip(), (
                sum(confs) / len(confs) if confs else 0.0
            )

    # Shape B: dict-like with text/confidence on the prediction itself
    if isinstance(pred, dict):
        t = pred.get("text", "")
        c = pred.get("confidence", 0.0)
        try:
            return str(t).strip(), float(c)
        except (TypeError, ValueError):
            return str(t).strip(), 0.0

    # Shape C: list of dicts (one per detected line)
    if isinstance(pred, list):
        texts = []
        confs = []
        for entry in pred:
            if isinstance(entry, dict):
                texts.append(str(entry.get("text", "")))
                try:
                    confs.append(float(entry.get("confidence", 0.0)))
                except (TypeError, ValueError):
                    confs.append(0.0)
        if texts:
            return " ".join(t.strip() for t in texts).strip(), (
                sum(confs) / len(confs) if confs else 0.0
            )

    # Shape D: object with .text / .confidence attributes
    t_attr = getattr(pred, "text", None)
    c_attr = getattr(pred, "confidence", None)
    if t_attr is not None:
        try:
            conf = float(c_attr) if c_attr is not None else 0.0
        except (TypeError, ValueError):
            conf = 0.0
        return str(t_attr).strip(), conf

    return "", 0.0


ENGINE = SuryaEngine
