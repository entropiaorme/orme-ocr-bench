"""OpenOCR / SVTRv2-mobile adapter.

OpenOCR (Topdu/OpenOCR, ICCV 2025) ships SVTRv2 — a CTC recogniser with a
visual-transformer encoder and Multi-Size Resizing baked in for irregular
text. Apache 2.0. The PyPI package ``openocr-python`` exposes the
recognition-only path via ``OpenRecognizer``; we use ``mode='mobile'`` with
``backend='onnx'`` to avoid pulling in PyTorch and to run inference through
ONNX Runtime. The auto-download fetches ``openocr_rec_model.onnx`` from
ModelScope on first construction.

GPU: openocr-python 0.1.5's own ONNX GPU path is broken (it wraps the
provider list in a stray one-tuple that ONNX Runtime rejects, so
``use_gpu='true'`` throws an EP error and silently falls back to CPU). We do
what the live app does (``backend/services/local_ocr.py``): construct the
recogniser with ``use_gpu='false'`` to skip that buggy path, then replace its
``onnx_rec_engine`` with our own session that auto-picks the best available
provider (CUDA here on NVIDIA; DirectML / CPU elsewhere) with a one-shot CPU
fallback. ``self.provider`` records what the session actually loaded on for
the leaderboard's Device column.

SVTRv2's MSR handles narrow / variable-width crops out-of-the-box, so we
pass the BGR ndarray straight through without padding. Confidence is the
recogniser's per-line score (CTC-derived softmax aggregate).
"""

from __future__ import annotations

import numpy as np

from backend.ocr.calibration.bench.engines.base import OCREngine
from backend.ocr.calibration.bench.engines._ort_cuda import ensure_cuda_libs_loaded


def _preferred_providers() -> list[str]:
    """Best available ONNX Runtime provider, CUDA preferred for this bench.

    Order: CUDA (NVIDIA breadth run) > DirectML (Windows) > CPU. Filtered to
    what the runtime actually exposes.
    """
    import onnxruntime as ort

    ensure_cuda_libs_loaded()
    available = set(ort.get_available_providers())
    order = ["CUDAExecutionProvider", "DmlExecutionProvider", "CPUExecutionProvider"]
    return [p for p in order if p in available] or ["CPUExecutionProvider"]


class OpenOCRSVTRv2Engine(OCREngine):
    name = "openocr_svtrv2"

    def __init__(self) -> None:
        try:
            from openocr.tools.infer_e2e import OpenRecognizer
            from openocr.tools.infer.onnx_engine import ONNXEngine
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "openocr-python not installed. pip install openocr-python"
            ) from exc
        import onnxruntime as ort

        # use_gpu='false' downloads the model and builds a working CPU
        # ONNXEngine while dodging the upstream broken GPU provider list.
        rec = OpenRecognizer(mode="mobile", backend="onnx", use_gpu="false")

        # The upstream CPU engine holds a valid session over the resolved
        # model path; rebuild that session with our preferred providers.
        # ONNXEngine stores no model path, so recover it: prefer the private
        # attr ORT records on the session, else re-resolve via the package's
        # own download helper (idempotent once cached).
        upstream = rec.onnx_rec_engine
        model_path = getattr(upstream.onnx_session, "_model_path", None)
        if not model_path:
            from openocr.tools.infer_rec import (
                MODEL_NAME_REC_ONNX,
                DOWNLOAD_URL_REC_ONNX,
                check_and_download_model,
            )

            model_path = check_and_download_model(
                MODEL_NAME_REC_ONNX, DOWNLOAD_URL_REC_ONNX
            )

        preferred = _preferred_providers()
        try:
            session = ort.InferenceSession(model_path, providers=preferred)
        except Exception:
            if preferred != ["CPUExecutionProvider"]:
                session = ort.InferenceSession(
                    model_path, providers=["CPUExecutionProvider"]
                )
            else:
                raise

        # Reuse the upstream engine's run()/feed logic; just swap its session
        # (and the input/output names derived from it) for our provider pick.
        upstream.onnx_session = session
        upstream.input_name = upstream.get_input_name(session)
        upstream.output_name = upstream.get_output_name(session)

        self._rec = rec
        self.provider = session.get_providers()[0]
        self.device = "cuda" if self.provider == "CUDAExecutionProvider" else (
            "directml" if self.provider == "DmlExecutionProvider" else "cpu"
        )

    def warm_up(self) -> None:
        dummy = np.full((48, 200, 3), 255, dtype=np.uint8)
        self.read_text(dummy)

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        return self.read_batch([crop_bgr])[0]

    # OpenRecognizer natively batches via img_numpy_list + batch_num.
    supports_batch = True

    def read_batch(self, crops_bgr: list[np.ndarray]) -> list[tuple[str, float]]:
        self._mark_model_start()
        results = self._rec(img_numpy_list=list(crops_bgr), batch_num=len(crops_bgr))
        out: list[tuple[str, float]] = []
        for r in (results or []):
            out.append((
                str(r.get("text", "") or ""),
                float(r.get("score", 0.0) or 0.0),
            ))
        while len(out) < len(crops_bgr):
            out.append(("", 0.0))
        return out


ENGINE = OpenOCRSVTRv2Engine
