"""Shared inference helper for OnnxTR recognition adapters.

Filename starts with ``_`` so the runner's ``*_engine.py`` discovery glob
ignores it (and even if it didn't, the lack of an ``_engine`` suffix would
exclude it). Six adapters in this batch share one inference loop with only
the architecture string differing.

Hardware/provider posture: the bench machine is Windows + AMD (RX 6750 XT).
We prefer ``DmlExecutionProvider`` (DirectML), falling back to CPU. The
CUDA-only ``onnxruntime-gpu`` wheel that ``onnxtr[gpu]`` pulls in does not
expose DirectML on Windows, so the install path swaps it for
``onnxruntime-directml`` (see Agent 2 ROOM.md).

Preprocessing: ``symmetric_pad=True`` is enabled for every architecture.
Tight single-line crops (especially the 25x13 percent cells) hit the
narrow-aspect failure mode otherwise; symmetric padding mitigates it the
same way it mitigates the documented TrOCR-base behaviour.
"""

from __future__ import annotations

from typing import Any

import cv2
import numpy as np
import onnxruntime as ort

from backend.ocr.calibration.bench.engines.base import OCREngine
from backend.ocr.calibration.bench.engines._ort_cuda import (
    ensure_cuda_libs_loaded,
    force_cpu,
)


def _preferred_providers() -> list[str]:
    ensure_cuda_libs_loaded()
    if force_cpu():
        return ["CPUExecutionProvider"]
    available = set(ort.get_available_providers())
    order = ["DmlExecutionProvider", "CUDAExecutionProvider", "CPUExecutionProvider"]
    return [p for p in order if p in available] or ["CPUExecutionProvider"]


class OnnxTRRecogEngine(OCREngine):
    """Base class for OnnxTR recognition-only adapters.

    Subclasses set ``name`` and ``ARCH`` (the OnnxTR architecture string,
    e.g. ``"crnn_mobilenet_v3_small"``).
    """

    ARCH: str = ""

    def __init__(self) -> None:
        try:
            from onnxtr.models import EngineConfig, recognition_predictor
        except ModuleNotFoundError as exc:  # pragma: no cover
            raise ModuleNotFoundError(
                "onnxtr not installed. pip install onnxtr onnxruntime-directml"
            ) from exc

        self._providers = _preferred_providers()
        self.provider = self._providers[0]
        self.device = (
            "cuda" if self.provider == "CUDAExecutionProvider"
            else "directml" if self.provider == "DmlExecutionProvider"
            else "cpu"
        )
        engine_cfg = EngineConfig(providers=self._providers)
        kwargs: dict[str, Any] = {
            "arch": self.ARCH,
            "symmetric_pad": True,
            "engine_cfg": engine_cfg,
        }
        self._predictor = recognition_predictor(**kwargs)

    def warm_up(self) -> None:
        dummy = np.full((32, 128, 3), 255, dtype=np.uint8)
        self._predictor([dummy])

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        return self.read_batch([crop_bgr])[0]

    # OnnxTR's recognition_predictor natively accepts a list of crops and runs
    # them as one batch, so batching is a genuine single-call path here.
    supports_batch = True

    def read_batch(self, crops_bgr: list[np.ndarray]) -> list[tuple[str, float]]:
        rgbs = [cv2.cvtColor(c, cv2.COLOR_BGR2RGB) for c in crops_bgr]
        self._mark_model_start()
        out = self._predictor(rgbs)
        results: list[tuple[str, float]] = []
        for item in out:
            text, conf = (item if item else (None, 0.0))
            if text is None:
                results.append(("", 0.0))
                continue
            try:
                conf_f = float(conf)
            except (TypeError, ValueError):
                conf_f = 0.0
            results.append((str(text), conf_f))
        # Guard against a predictor returning fewer items than inputs.
        while len(results) < len(crops_bgr):
            results.append(("", 0.0))
        return results
