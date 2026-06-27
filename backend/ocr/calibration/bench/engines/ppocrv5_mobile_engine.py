"""PP-OCRv5 multilingual mobile recognition adapter.

Architecture: PaddleOCR PP-OCRv5_mobile_rec — newer (v5) weights for the
same SVTR-LCNet recognition family that the existing ``ppocr`` adapter
uses with v4 weights. PaddleOCR's own evals report ~+13pt accuracy over
v4 on the multilingual benchmark.

Weights: ``bukuroo/PPOCRv5-ONNX/ppocrv5-mobile-rec.onnx`` (~16 MB) plus
the bundled ``ppocrv5_dict.txt`` (18,383 chars covering CJK, Cyrillic,
Latin, and more). Cached to ``.venv-<N>/models/`` by the agent's
download script. Runs through ONNX Runtime (DirectML provider on AMD
Windows, CPU fallback).

Confidence-scale fix: PaddleOCR's exported v5 ONNX models include
softmax in the graph, so output already sums to 1.0 across the class
dimension. The legacy ``PPocrRecReader._decode`` then applies softmax a
second time, which collapses confidences into the 0.003-0.006 range.
This adapter (and its sibling v5 adapters) use the model output as
probabilities directly — no extra softmax — so confidences land in the
expected [0, 1] range and per-cell scores are comparable across engines.

This module also hosts ``_PPocrV5Reader``, the shared inference helper
used by the four v5 adapter files. The class is intentionally local to
this engines/ directory (Agent 1 owns all four v5 adapter files, so
cross-importing between them is in-scope).
"""

from __future__ import annotations

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
        f"onnxruntime is not installed. Install `{package_name}` in the agent venv."
    ) from exc

from backend.ocr.calibration.bench.engines.base import OCREngine
from backend.ocr.calibration.bench.engines._ort_cuda import (
    ensure_cuda_libs_loaded,
    force_cpu,
)

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[5]
MODELS_DIR = REPO_ROOT / ".venv-1" / "models"

TARGET_HEIGHT = 48


def _select_providers() -> list[str]:
    ensure_cuda_libs_loaded()
    if force_cpu():
        return ["CPUExecutionProvider"]
    available = ort.get_available_providers()
    for p in ("CUDAExecutionProvider", "DmlExecutionProvider"):
        if p in available:
            return [p]
    return ["CPUExecutionProvider"]


def _batched_ctc_read(session, input_name, decode, tensors):
    """Width-bucketed batched inference for variable-width CTC recognisers.

    Padding a narrow crop out to a much wider batch-max leaks spurious
    characters into the read (the conv receptive field sees the padded tail),
    so batched results would not match serial. PP-OCR's reference path avoids
    this by grouping crops of similar width and padding only to the bucket max.
    We sort by width and cut a new bucket whenever the width grows past a small
    ratio of the bucket's min width, so intra-bucket padding stays minimal and
    batched reads track serial. Results are returned in the original order.
    """
    order = sorted(range(len(tensors)), key=lambda i: tensors[i].shape[3])
    results: dict[int, tuple] = {}
    bucket: list[int] = []

    def flush(idxs):
        if not idxs:
            return
        max_w = max(tensors[i].shape[3] for i in idxs)
        batch = np.zeros((len(idxs), 3, TARGET_HEIGHT, max_w), dtype=np.float32)
        for bi, i in enumerate(idxs):
            t = tensors[i]
            batch[bi, :, :, : t.shape[3]] = t[0]
        preds = session.run(None, {input_name: batch})[0]
        for bi, i in enumerate(idxs):
            results[i] = decode(preds[bi : bi + 1])

    bucket_min_w = None
    for i in order:
        w = tensors[i].shape[3]
        if bucket and w > bucket_min_w * 1.10:  # >10% wider: start a new bucket
            flush(bucket)
            bucket = []
        if not bucket:
            bucket_min_w = w
        bucket.append(i)
    flush(bucket)
    return [results[i] for i in range(len(tensors))]


class _PPocrV5Reader:
    """Shared PP-OCRv5 inference helper.

    Mirrors the layout of ``backend/ocr/ppocr_rec_reader.py`` (the
    read-only baseline reader) but with the double-softmax bug fixed: model output
    is treated as probabilities directly rather than re-softmaxed.

    The ONNX export from PaddleOCR's v5 release pipeline includes
    softmax in-graph and emits dynamic [N, T, C] tensors. Preprocessing
    matches the recipe encoded in the model's bundled ``inference.yml``:
    BGR input, height 48, dynamic width, normalised to [-1, 1].
    """

    def __init__(self, model_path: Path, dict_path: Path) -> None:
        if not model_path.is_file():
            raise FileNotFoundError(f"PP-OCRv5 model missing: {model_path}")
        if not dict_path.is_file():
            raise FileNotFoundError(f"PP-OCRv5 dict missing: {dict_path}")

        self._chars: list[str] = ["blank"]
        with open(dict_path, encoding="utf-8") as f:
            for line in f:
                ch = line.rstrip("\n")
                if ch != "":
                    self._chars.append(ch)
        self._chars.append(" ")

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

        self._session = ort.InferenceSession(
            str(model_path), so, providers=_select_providers(),
        )
        self._input_name = self._session.get_inputs()[0].name
        self.provider = self._session.get_providers()[0]
        self.device = (
            "cuda" if self.provider == "CUDAExecutionProvider"
            else "directml" if self.provider == "DmlExecutionProvider"
            else "cpu"
        )
        log.info(
            "PP-OCRv5 rec loaded: %s (%d chars, provider=%s, classes=%s)",
            model_path.name, len(self._chars),
            self.provider,
            self._session.get_outputs()[0].shape,
        )

    def warm_up(self) -> None:
        for w in (160, 320, 640):
            dummy = np.zeros((1, 3, TARGET_HEIGHT, w), dtype=np.float32)
            self._session.run(None, {self._input_name: dummy})

    def read_text(self, region_bgr: np.ndarray) -> tuple[str, float]:
        tensor = self._preprocess(region_bgr)
        output = self._session.run(None, {self._input_name: tensor})
        return self._decode(output[0])

    def read_batch(self, crops_bgr: list[np.ndarray]) -> list[tuple[str, float]]:
        return _batched_ctc_read(
            self._session, self._input_name, self._decode,
            [self._preprocess(c) for c in crops_bgr],
        )

    @staticmethod
    def _preprocess(bgr: np.ndarray) -> np.ndarray:
        h, w = bgr.shape[:2]
        scale = TARGET_HEIGHT / h
        new_w = max(1, int(round(w * scale)))
        resized = cv2.resize(
            bgr, (new_w, TARGET_HEIGHT), interpolation=cv2.INTER_LINEAR,
        )
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        p2, p98 = np.percentile(gray, [2, 98])
        stretched = np.clip(
            (gray.astype(np.float32) - p2) / (p98 - p2 + 1e-6) * 255.0,
            0, 255,
        ).astype(np.uint8)
        bgr_out = cv2.cvtColor(stretched, cv2.COLOR_GRAY2BGR)
        tensor = bgr_out.astype(np.float32) / 255.0
        tensor = (tensor - 0.5) / 0.5
        return tensor.transpose(2, 0, 1)[np.newaxis, ...]

    def _decode(self, preds: np.ndarray) -> tuple[str, float]:
        # preds: [1, T, C], already softmaxed in-graph (sum across C == 1).
        probs = preds[0]
        indices = probs.argmax(axis=1)
        chars: list[str] = []
        confs: list[float] = []
        prev = -1
        n_classes = len(self._chars)
        for t, idx in enumerate(indices):
            idx = int(idx)
            if idx != 0 and idx != prev:
                if idx < n_classes:
                    chars.append(self._chars[idx])
                    confs.append(float(probs[t, idx]))
            prev = idx
        text = "".join(chars)
        if confs:
            log_mean = sum(np.log(c + 1e-10) for c in confs) / len(confs)
            confidence = float(np.exp(log_mean))
        else:
            confidence = 0.0
        return text, confidence


class PPOCRv5MobileEngine(OCREngine):
    name = "ppocrv5_mobile"

    def __init__(self) -> None:
        self._reader = _PPocrV5Reader(
            MODELS_DIR / "ppocrv5_mobile.onnx",
            MODELS_DIR / "ppocrv5_multilingual_dict.txt",
        )
        self._adopt_device(self._reader)

    supports_batch = True

    def warm_up(self) -> None:
        self._reader.warm_up()

    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        return self._reader.read_text(crop_bgr)

    def read_batch(self, crops_bgr: list[np.ndarray]) -> list[tuple[str, float]]:
        self._mark_model_start()
        return self._reader.read_batch(crops_bgr)


ENGINE = PPOCRv5MobileEngine
