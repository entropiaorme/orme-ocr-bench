"""Abstract OCR engine interface for the bench harness."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod

import numpy as np


def torch_device() -> str:
    """Best available torch device for this host: 'cuda' if usable, else 'cpu'.

    Centralises the CUDA probe so every torch-based adapter reports the same
    device string and falls back cleanly on CPU-only / non-NVIDIA hosts. Used
    for the leaderboard's Device column and for ``.to(device)`` placement.
    """
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
    return "cpu"


class OCREngine(ABC):
    """Common interface every benched engine implements.

    Subclasses load their model in ``__init__`` (or in a separate setup hook),
    optionally pre-warm via ``warm_up``, and expose a single ``read_text``
    that takes a BGR ndarray crop and returns ``(text, confidence)``.

    Confidence is a float in [0, 1] when the engine produces a meaningful
    score; engines that don't produce one return ``1.0`` (TrOCR's case) or
    a domain-specific scaling. The bench reports raw values without
    normalising across engines (their scales are not directly comparable).
    """

    name: str  # short identifier; populated by subclass

    # Execution device / provider this engine actually loaded on, for the
    # latency leaderboard's Device column. Adapters set these in __init__
    # once they know what they got (e.g. "cuda" after .to(cuda) succeeds,
    # or the chosen ONNX Runtime provider). Defaults describe a CPU engine
    # so adapters that never set them (e.g. tesseract) report honestly.
    device: str = "cpu"
    provider: str | None = None

    def _adopt_device(self, source: object) -> None:
        """Copy ``device``/``provider`` from a sub-component (reader, session).

        Adapters that delegate inference to a helper object (e.g. the shared
        PP-OCR reader) call this so the runner sees the device the helper
        actually loaded on.
        """
        provider = getattr(source, "provider", None)
        if provider is not None:
            self.provider = provider
        device = getattr(source, "device", None)
        if device is not None:
            self.device = device

    # --- Batched inference (opt-in) ------------------------------------------
    # Engines with a genuine batched path set supports_batch=True and override
    # read_batch. There is deliberately NO loop-over-read_text fallback: a
    # looped "batch" would report misleading throughput, so engines without
    # real batching are recorded as "batched: n/a" by the runner.
    supports_batch: bool = False

    def read_batch(self, crops_bgr: list[np.ndarray]) -> list[tuple[str, float]]:
        """Recognise a batch of BGR crops in one model call. Override + set
        ``supports_batch = True`` to provide a true batched path."""
        raise NotImplementedError("this engine has no batched path")

    # --- Per-cell preprocess/model timing split (opt-in) ---------------------
    # ms/cell conflates "this adapter upscales 4x" with "this model is slow".
    # Adapters that want the split call ``self._mark_model_start()`` in
    # read_text at the boundary between preprocessing and the model call; the
    # runner then reads ``last_preprocess_ms`` / ``last_model_ms``. Engines
    # that never mark report the whole cell as model time (preprocess unknown).
    last_preprocess_ms: float | None = None
    last_model_ms: float | None = None
    _cell_t0: float | None = None

    def _begin_cell(self) -> None:
        """Runner calls this immediately before each read_text (timing anchor)."""
        self._cell_t0 = time.perf_counter()
        self.last_preprocess_ms = None
        self.last_model_ms = None

    def _mark_model_start(self) -> None:
        """Adapters call this in read_text once preprocessing is done and the
        model call is about to begin."""
        if self._cell_t0 is not None:
            self.last_preprocess_ms = (time.perf_counter() - self._cell_t0) * 1e3

    @abstractmethod
    def warm_up(self) -> None:
        """Pre-allocate / pre-compile / pre-load any per-inference state."""

    @abstractmethod
    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        """Recognise text from a BGR ndarray crop. Returns (text, confidence)."""
