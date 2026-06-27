"""PP-OCR English recognition model wrapper.

Runs recognition-only (no detection, no classification) for already-cropped
text regions such as the repair window cost. Uses ONNX Runtime with GPU
execution provider (DirectML on Windows, CUDA on Linux).

Anti-stutter ONNX session configuration disables thread pool spin-waiting
so the recognizer does not peg idle cores between reads.
"""

import logging
import platform
from pathlib import Path

import cv2
import numpy as np

try:
    import onnxruntime as ort
except ModuleNotFoundError as exc:
    package_name = "onnxruntime-directml" if platform.system() == "Windows" else "onnxruntime"
    raise ModuleNotFoundError(
        f"onnxruntime is not installed. Install `{package_name}` in the backend environment."
    ) from exc

log = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).parent.parent / "assets"
DEFAULT_MODEL = ASSETS_DIR / "models" / "rec.onnx"
DEFAULT_DICT = ASSETS_DIR / "models" / "dict.txt"

# Preprocessing
TARGET_HEIGHT = 48  # model's fixed input height


def _preload_cuda_libs() -> None:
    """Load pip-wheel CUDA libraries so ONNX Runtime can see them.

    On Linux + NVIDIA the CUDA runtime is supplied by the ``nvidia-*-cu12``
    pip wheels under ``site-packages/nvidia/`` rather than a system toolkit;
    ONNX Runtime >= 1.21 exposes ``preload_dlls()`` to load them without any
    ``LD_LIBRARY_PATH`` setup. No-op on the CPU and DirectML wheels (which do
    not expose the function) and exception-safe so CPU fallback is never lost.
    """
    preload = getattr(ort, "preload_dlls", None)
    if preload is None:
        return
    try:
        preload()
    except Exception:
        pass


def _select_onnx_providers() -> list[str]:
    """Pick the best available ONNX Runtime execution provider.

    Priority: CUDA (Linux/NVIDIA) > DirectML (Windows/AMD) > CPU.
    """
    _preload_cuda_libs()
    available = ort.get_available_providers()
    for provider in ["CUDAExecutionProvider", "DmlExecutionProvider"]:
        if provider in available:
            return [provider]
    return ["CPUExecutionProvider"]


class PPocrRecReader:
    """Reads text from BGR image regions using PP-OCR.

    Uses the English PP-OCR recognition model via the best available GPU
    provider (CUDA on Linux, DirectML on Windows, CPU fallback).
    """

    def __init__(
        self,
        model_path: Path | None = None,
        dict_path: Path | None = None,
    ):
        model_path = model_path or DEFAULT_MODEL
        dict_path = dict_path or DEFAULT_DICT

        if not model_path.is_file() or not dict_path.is_file():
            missing = []
            if not model_path.is_file():
                missing.append(str(model_path))
            if not dict_path.is_file():
                missing.append(str(dict_path))
            raise FileNotFoundError(
                "PP-OCR model assets are missing. Expected files: "
                + ", ".join(missing)
                + ". Populate backend/assets/models in this checkout."
            )

        # Load character dictionary
        self._chars = ["blank"]  # index 0 = CTC blank
        with open(dict_path, encoding="utf-8") as f:
            for line in f:
                ch = line.strip()
                if ch:
                    self._chars.append(ch)
        self._chars.append(" ")  # space is the last entry

        # ONNX session — GPU preferred, anti-stutter config
        so = ort.SessionOptions()
        so.add_session_config_entry("session.intra_op.allow_spinning", "0")
        so.add_session_config_entry("session.inter_op.allow_spinning", "0")
        so.add_session_config_entry("session.force_spinning_stop", "1")
        so.intra_op_num_threads = 1
        so.inter_op_num_threads = 1
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        so.enable_cpu_mem_arena = False
        so.enable_mem_pattern = False
        so.enable_mem_reuse = False
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        providers = _select_onnx_providers()
        self._session = ort.InferenceSession(
            str(model_path), so,
            providers=providers,
        )
        self._input_name = self._session.get_inputs()[0].name

        provider = self._session.get_providers()[0]
        self.provider = provider
        log.info(
            "PP-OCR rec loaded: %s (%d chars, provider=%s)",
            model_path.name, len(self._chars), provider,
        )

    def warm_up(self) -> None:
        """Run dummy inferences to pre-allocate GPU buffers."""
        for w in [200, 400, 600]:
            dummy = np.zeros((1, 3, TARGET_HEIGHT, w), dtype=np.float32)
            self._session.run(None, {self._input_name: dummy})
        log.info("PP-OCR rec warmed up")

    def read_text(self, region_bgr: np.ndarray) -> tuple[str, float]:
        """Read text from a BGR tool name region.

        Returns (text, confidence) or ("", 0.0) if nothing detected.
        """
        tensor = self._preprocess(region_bgr)
        output = self._session.run(None, {self._input_name: tensor})
        return self._decode(output[0])

    def read_batch(self, crops_bgr: list[np.ndarray]) -> list[tuple[str, float]]:
        """Width-bucketed batched recognition (see ppocrv5's _batched_ctc_read):
        group similar-width crops so padding stays minimal and batched reads
        track serial, rather than a single max-width pad that leaks into narrow
        crops."""
        from backend.ocr.calibration.bench.engines.ppocrv5_mobile_engine import (
            _batched_ctc_read,
        )

        return _batched_ctc_read(
            self._session, self._input_name, self._decode,
            [self._preprocess(c) for c in crops_bgr],
        )

    # ------------------------------------------------------------------
    # Preprocessing
    # ------------------------------------------------------------------

    @staticmethod
    def _preprocess(bgr: np.ndarray) -> np.ndarray:
        """Upscale to 48px height, contrast-stretch, normalize to [-1,1]."""
        h, w = bgr.shape[:2]
        scale = TARGET_HEIGHT / h
        new_w = max(1, int(w * scale))
        resized = cv2.resize(
            bgr, (new_w, TARGET_HEIGHT), interpolation=cv2.INTER_LINEAR,
        )

        # Contrast stretch (percentile-based)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        p2, p98 = np.percentile(gray, [2, 98])
        stretched = np.clip(
            (gray.astype(np.float32) - p2) / (p98 - p2 + 1e-6) * 255,
            0, 255,
        ).astype(np.uint8)
        bgr_out = cv2.cvtColor(stretched, cv2.COLOR_GRAY2BGR)

        # Normalize to [-1, 1], NCHW
        tensor = bgr_out.astype(np.float32) / 255.0
        tensor = (tensor - 0.5) / 0.5
        return tensor.transpose(2, 0, 1)[np.newaxis, ...]

    # ------------------------------------------------------------------
    # CTC decoding
    # ------------------------------------------------------------------

    def _decode(self, preds: np.ndarray) -> tuple[str, float]:
        """CTC greedy decode: argmax, collapse repeats, remove blanks."""
        logits = preds[0]  # (T, num_classes)

        # Softmax for confidence
        exp = np.exp(logits - logits.max(axis=1, keepdims=True))
        probs = exp / exp.sum(axis=1, keepdims=True)

        indices = logits.argmax(axis=1)
        chars: list[str] = []
        confs: list[float] = []
        prev = -1
        for t, idx in enumerate(indices):
            idx = int(idx)
            if idx != 0 and idx != prev:
                if idx < len(self._chars):
                    chars.append(self._chars[idx])
                    confs.append(float(probs[t, idx]))
            prev = idx

        text = "".join(chars)
        # Use geometric mean of per-character confidences.
        # min() is too harsh — a single low-confidence character tanks the
        # whole score.  Geometric mean reflects overall quality better.
        if confs:
            log_mean = sum(np.log(c + 1e-10) for c in confs) / len(confs)
            confidence = float(np.exp(log_mean))
        else:
            confidence = 0.0
        return text, confidence
