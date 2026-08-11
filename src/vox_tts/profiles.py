from __future__ import annotations

import json
from pathlib import Path

from .models import ValidationError, VoiceProfile


class ProfileCatalogError(RuntimeError):
    """Raised when a profile catalog cannot be loaded safely."""


def load_profile(path: Path) -> VoiceProfile:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProfileCatalogError(f"cannot read profile {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise ProfileCatalogError(f"profile {path} must contain a JSON object")

    try:
        return VoiceProfile.from_mapping(payload)
    except ValidationError as exc:
        raise ProfileCatalogError(f"invalid profile {path}: {exc}") from exc


def load_catalog(directory: Path) -> tuple[VoiceProfile, ...]:
    if not directory.is_dir():
        raise ProfileCatalogError(f"profile directory does not exist: {directory}")

    profiles = tuple(load_profile(path) for path in sorted(directory.glob("*.json")))
    if not profiles:
        raise ProfileCatalogError(f"no JSON profiles found in {directory}")

    ids = [profile.id for profile in profiles]
    if len(ids) != len(set(ids)):
        raise ProfileCatalogError("profile IDs must be unique")
    return profiles

