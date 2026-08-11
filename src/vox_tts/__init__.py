"""VOX — backend-neutral Brazilian Portuguese TTS core."""

from .models import BackendDescriptor, BackendHealth, SynthesisRequest, VoiceProfile

__all__ = [
    "BackendDescriptor",
    "BackendHealth",
    "SynthesisRequest",
    "VoiceProfile",
]

__version__ = "0.1.0"

