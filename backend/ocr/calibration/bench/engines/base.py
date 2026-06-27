"""Abstract OCR engine interface for the bench harness."""

from __future__ import annotations

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

    @abstractmethod
    def warm_up(self) -> None:
        """Pre-allocate / pre-compile / pre-load any per-inference state."""

    @abstractmethod
    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        """Recognise text from a BGR ndarray crop. Returns (text, confidence)."""
