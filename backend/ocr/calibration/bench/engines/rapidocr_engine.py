"""RapidOCR adapter (rec-only path).

Architecture: RapidOCR is a third-party packaging of the PP-OCR family
that ships its own bundled ONNX weights and its own inference loop, so
even though it shares architectural lineage with the ``ppocr`` /
``ppocrv5_*`` adapters here, the runtime stack is meaningfully
different (its own preprocess, its own session config, its own decode).
Bench-wise it stands as a separate engine — useful for measuring the
overhead/benefit of the packaging layer relative to direct ONNX
Runtime calls.

Detection is bypassed entirely: the bench feeds tightly-cropped
single-line cells, so we call RapidOCR's ``text_recognizer`` directly
on each crop. RapidOCR returns a ``(list_of_(text, conf), elapsed_ms)``
tuple — for a single-image input we take the first entry.

Weights: bundled with the ``rapidocr-onnxruntime`` pip package (the
default v3 English-Chinese recogniser as of the version installed in
``.venv-1/``). No external download required.
"""

from __future__ import annotations

import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine

try:
    from rapidocr_onnxruntime import RapidOCR
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "rapidocr-onnxruntime is not installed in this venv."
    ) from exc


class RapidOCREngine(OCREngine):
    name = "rapidocr"

    def __init__(self) -> None:
        # Construct the full pipeline so RapidOCR's own session config /
        # provider selection runs; we then call only the recognizer. Request
        # CUDA so the breadth run uses GPU where available; RapidOCR ignores
        # the flag and stays on CPU if onnxruntime-gpu / CUDA isn't present.
        try:
            self._engine = RapidOCR(
                config={
                    "Global": {"use_cuda": True},
                    "Rec": {"use_cuda": True},
                }
            )
        except Exception:
            # Older/newer RapidOCR signatures differ; fall back to defaults.
            self._engine = RapidOCR()
        self._recognizer = self._engine.text_recognizer
        self.provider = self._detect_provider()
        self.device = (
            "cuda" if self.provider == "CUDAExecutionProvider"
            else "directml" if self.provider == "DmlExecutionProvider"
            else "cpu"
        )

    def _detect_provider(self) -> str | None:
        """Best-effort read of the recogniser's active ONNX provider."""
        for attr in ("session", "_session", "onnx_session"):
            sess = getattr(self._recognizer, attr, None)
            get = getattr(sess, "get_providers", None)
            if callable(get):
                provs = get()
                if provs:
                    return provs[0]
        return None

    def warm_up(self) -> None:
        # A few dummy passes at typical bench widths to pre-allocate
        # the recognizer's session buffers.
        for w in (160, 320, 640):
            dummy = np.zeros((48, w, 3), dtype=np.uint8)
            self._recognizer([dummy])

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        results, _elapsed_ms = self._recognizer([crop_bgr])
        if not results:
            return "", 0.0
        text, conf = results[0]
        try:
            conf_f = float(conf)
        except (TypeError, ValueError):
            conf_f = 0.0
        return str(text or ""), conf_f


ENGINE = RapidOCREngine
