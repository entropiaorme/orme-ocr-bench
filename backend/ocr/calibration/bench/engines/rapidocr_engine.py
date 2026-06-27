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
from backend.ocr.calibration.bench.engines._ort_cuda import ensure_cuda_libs_loaded

try:
    from rapidocr_onnxruntime import RapidOCR
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "rapidocr-onnxruntime is not installed in this venv."
    ) from exc


class RapidOCREngine(OCREngine):
    name = "rapidocr"

    def __init__(self) -> None:
        # Make the pip-wheel CUDA libs visible before RapidOCR builds its
        # session (it reads onnxruntime's available providers at construction).
        ensure_cuda_libs_loaded()
        # rapidocr-onnxruntime takes flat ``rec_use_cuda`` kwargs (the Rec
        # branch of its config). Judge GPU availability by the ONNX Runtime
        # providers (this venv has no torch), not torch.cuda. It honours the
        # request only when a CUDA onnxruntime is actually present, else stays
        # on CPU; pass it only on a CUDA host.
        import onnxruntime as ort

        want_cuda = "CUDAExecutionProvider" in ort.get_available_providers()
        self._engine = RapidOCR(rec_use_cuda=True) if want_cuda else RapidOCR()
        # API: the recogniser is ``text_rec`` (older releases: text_recognizer).
        self._recognizer = getattr(
            self._engine, "text_rec", None
        ) or self._engine.text_recognizer
        self.provider = self._detect_provider()
        self.device = (
            "cuda" if self.provider == "CUDAExecutionProvider"
            else "directml" if self.provider == "DmlExecutionProvider"
            else "cpu"
        )

    def _detect_provider(self) -> str | None:
        """Best-effort read of the recogniser's active ONNX provider.

        rapidocr wraps the ORT session: ``text_rec.session`` is an
        ``OrtInferSession`` whose ``.session`` is the real InferenceSession.
        """
        rec = self._recognizer
        for path in (
            ("session", "session"),  # OrtInferSession -> InferenceSession
            ("session",),
            ("_session",),
            ("onnx_session",),
        ):
            obj = rec
            for attr in path:
                obj = getattr(obj, attr, None)
                if obj is None:
                    break
            get = getattr(obj, "get_providers", None)
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
        return self.read_batch([crop_bgr])[0]

    # RapidOCR's text recogniser natively accepts a list of crops as one batch.
    supports_batch = True

    def read_batch(self, crops_bgr: list[np.ndarray]) -> list[tuple[str, float]]:
        self._mark_model_start()
        results, _elapsed_ms = self._recognizer(list(crops_bgr))
        out: list[tuple[str, float]] = []
        for item in (results or []):
            text, conf = (item[0], item[1]) if item else ("", 0.0)
            try:
                conf_f = float(conf)
            except (TypeError, ValueError):
                conf_f = 0.0
            out.append((str(text or ""), conf_f))
        while len(out) < len(crops_bgr):
            out.append(("", 0.0))
        return out


ENGINE = RapidOCREngine
