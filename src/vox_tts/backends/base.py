from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..models import BackendDescriptor, BackendHealth, SynthesisRequest


class SynthesisBackend(Protocol):
    descriptor: BackendDescriptor

    def doctor(self) -> BackendHealth:
        """Return installation and readiness without downloading a model."""

    def synthesize(self, request: SynthesisRequest, output: Path) -> Path:
        """Synthesize one request or raise a backend-specific error."""

