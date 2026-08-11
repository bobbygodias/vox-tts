from __future__ import annotations

from importlib.util import find_spec

from ..models import BackendDescriptor, BackendHealth


_BACKENDS = (
    BackendDescriptor(
        id="f5-ptbr",
        display_name="F5-TTS pt-BR",
        runtime_license="MIT",
        model_license="CC BY-NC 4.0",
        model_id="firstpixel/F5-TTS-pt-br",
        noncommercial=True,
        terms_acceptance_required=False,
    ),
    BackendDescriptor(
        id="xtts-v2",
        display_name="XTTS v2",
        runtime_license="MPL-2.0",
        model_license="CPML",
        model_id="tts_models/multilingual/multi-dataset/xtts_v2",
        noncommercial=True,
        terms_acceptance_required=True,
    ),
)


def backend_descriptors() -> tuple[BackendDescriptor, ...]:
    return _BACKENDS


def backend_health() -> tuple[BackendHealth, ...]:
    f5_installed = find_spec("f5_tts") is not None
    xtts_installed = find_spec("TTS") is not None
    return (
        BackendHealth(
            id="f5-ptbr",
            installed=f5_installed,
            ready=False,
            detail="runtime detected; model readiness not tested" if f5_installed else "f5_tts is not installed",
        ),
        BackendHealth(
            id="xtts-v2",
            installed=xtts_installed,
            ready=False,
            detail="runtime detected; CPML acceptance and model readiness not tested"
            if xtts_installed
            else "coqui_tts is not installed",
        ),
    )

