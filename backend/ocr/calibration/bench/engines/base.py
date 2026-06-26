"""Abstract OCR engine interface for the bench harness."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


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

    @abstractmethod
    def warm_up(self) -> None:
        """Pre-allocate / pre-compile / pre-load any per-inference state."""

    @abstractmethod
    def read_text(self, crop_bgr: np.ndarray) -> tuple[str, float]:
        """Recognise text from a BGR ndarray crop. Returns (text, confidence)."""
