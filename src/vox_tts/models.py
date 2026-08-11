from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class ValidationError(ValueError):
    """Raised when a VOX domain object is invalid."""


def _required_string(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{key} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class BackendDescriptor:
    id: str
    display_name: str
    runtime_license: str
    model_license: str
    model_id: str
    noncommercial: bool
    terms_acceptance_required: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "runtime_license": self.runtime_license,
            "model_license": self.model_license,
            "model_id": self.model_id,
            "noncommercial": self.noncommercial,
            "terms_acceptance_required": self.terms_acceptance_required,
        }


@dataclass(frozen=True, slots=True)
class BackendHealth:
    id: str
    installed: bool
    ready: bool
    detail: str

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "installed": self.installed,
            "ready": self.ready,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class VoiceProfile:
    schema_version: str
    id: str
    display_name: str
    locale: str
    status: str
    origin_policy: str
    target: Mapping[str, str]
    backend_bindings: tuple[Mapping[str, Any], ...]

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "VoiceProfile":
        target = data.get("target")
        if not isinstance(target, Mapping):
            raise ValidationError("target must be an object")

        required_target_keys = ("age_impression", "pitch", "texture", "pace", "use_case")
        normalized_target = {key: _required_string(target, key) for key in required_target_keys}

        bindings = data.get("backend_bindings", [])
        if not isinstance(bindings, list) or not all(isinstance(item, Mapping) for item in bindings):
            raise ValidationError("backend_bindings must be a list of objects")

        locale = _required_string(data, "locale")
        if locale != "pt-BR":
            raise ValidationError("initial VOX profiles must use locale pt-BR")

        return cls(
            schema_version=_required_string(data, "schema_version"),
            id=_required_string(data, "id"),
            display_name=_required_string(data, "display_name"),
            locale=locale,
            status=_required_string(data, "status"),
            origin_policy=_required_string(data, "origin_policy"),
            target=normalized_target,
            backend_bindings=tuple(dict(item) for item in bindings),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "display_name": self.display_name,
            "locale": self.locale,
            "status": self.status,
            "origin_policy": self.origin_policy,
            "target": dict(self.target),
            "backend_bindings": [dict(item) for item in self.backend_bindings],
        }


@dataclass(frozen=True, slots=True)
class SynthesisRequest:
    text: str
    profile_id: str
    backend_id: str
    language: str = "pt-BR"

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValidationError("text must not be blank")
        if not self.profile_id.strip():
            raise ValidationError("profile_id must not be blank")
        if not self.backend_id.strip():
            raise ValidationError("backend_id must not be blank")
        if self.language != "pt-BR":
            raise ValidationError("the initial VOX runtime only accepts pt-BR")

