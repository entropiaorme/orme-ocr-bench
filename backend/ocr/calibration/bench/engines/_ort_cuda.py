"""Make pip-installed CUDA runtime libraries visible to ONNX Runtime.

On Linux + NVIDIA hosts the cleanest CUDA posture is to install no system
CUDA toolkit at all and instead let the ``nvidia-*-cu12`` pip wheels carry
the runtime libraries inside the venv (see SETUP.md). ONNX Runtime does not
find those libraries on its own: they live under ``site-packages/nvidia/``,
which is not on the loader path. ONNX Runtime >= 1.21 exposes
``preload_dlls()`` to load them programmatically, which removes the need for
any ``LD_LIBRARY_PATH`` plumbing.

This helper calls ``preload_dlls()`` once, before the first
``get_available_providers()`` or ``InferenceSession`` in the process. It is a
no-op on the CPU ``onnxruntime`` wheel and on Windows ``onnxruntime-directml``
(neither exposes the function), so every ORT-based adapter can call it
unconditionally regardless of host.
"""

from __future__ import annotations

import os

_done = False


def force_cpu() -> bool:
    """True when the bench is asked to run on CPU regardless of available GPUs.

    Set ``OCR_BENCH_DEVICE=cpu`` in the environment to pin every ONNX-based
    adapter to ``CPUExecutionProvider`` even on a host whose ONNX Runtime build
    also exposes DirectML or CUDA. This is what produces the CPU latency track
    on a GPU host without building a second, CPU-only set of venvs: the same
    ``onnxruntime-directml`` / ``onnxruntime-gpu`` wheel carries the CPU
    provider, so the only thing that differs between the GPU and CPU tracks is
    this knob. Any value other than ``cpu`` (case-insensitive) is ignored.
    """
    return os.environ.get("OCR_BENCH_DEVICE", "").strip().lower() == "cpu"


def ensure_cuda_libs_loaded() -> None:
    """Preload the pip-wheel CUDA libraries if this ORT build supports it.

    Idempotent and exception-safe: a failure here must never stop an engine
    from falling back to CPU. Call it before any provider query or session
    construction.
    """
    global _done
    if _done:
        return
    _done = True
    try:
        import onnxruntime as ort
    except ModuleNotFoundError:
        return
    preload = getattr(ort, "preload_dlls", None)
    if preload is None:
        return
    try:
        preload()
    except Exception:
        # Best effort: if preload fails, ORT still loads via whatever is on
        # the system loader path (or falls back to CPU). Never fatal.
        pass
