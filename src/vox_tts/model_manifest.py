from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class ModelManifestError(ValueError):
    """Raised when a model manifest or its verification request is invalid."""


def _required_string(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ModelManifestError(f"{key} must be a non-empty string")
    return value.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class ModelArtifact:
    role: str
    filename: str
    source_url: str
    source_revision: str
    size_bytes: int
    sha256: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ModelArtifact":
        filename = _required_string(data, "filename")
        candidate = Path(filename)
        if candidate.is_absolute() or candidate.name != filename or ".." in candidate.parts:
            raise ModelManifestError("artifact filename must be a safe basename")

        size_bytes = data.get("size_bytes")
        if not isinstance(size_bytes, int) or isinstance(size_bytes, bool) or size_bytes <= 0:
            raise ModelManifestError("artifact size_bytes must be a positive integer")

        checksum = _required_string(data, "sha256").lower()
        if _SHA256_PATTERN.fullmatch(checksum) is None:
            raise ModelManifestError("artifact sha256 must contain 64 hexadecimal characters")

        source_url = _required_string(data, "source_url")
        if not source_url.startswith("https://huggingface.co/"):
            raise ModelManifestError("artifact source_url must use HTTPS on huggingface.co")
        source_revision = _required_string(data, "source_revision").lower()
        if _REVISION_PATTERN.fullmatch(source_revision) is None:
            raise ModelManifestError("artifact source_revision must be a full 40-character commit")

        return cls(
            role=_required_string(data, "role"),
            filename=filename,
            source_url=source_url,
            source_revision=source_revision,
            size_bytes=size_bytes,
            sha256=checksum,
        )


@dataclass(frozen=True, slots=True)
class ModelManifest:
    schema_version: str
    id: str
    backend_id: str
    model_id: str
    model_license: str
    model_license_url: str
    noncommercial: bool
    runtime_package: str
    runtime_version: str
    runtime_source_commit: str
    runtime_distribution_filename: str
    runtime_distribution_url: str
    runtime_distribution_sha256: str
    architecture_candidate: str
    architecture_status: str
    artifacts: tuple[ModelArtifact, ...]

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ModelManifest":
        schema_version = _required_string(data, "schema_version")
        if schema_version != "1.0":
            raise ModelManifestError("unsupported model manifest schema_version")

        license_data = data.get("license")
        runtime = data.get("runtime")
        architecture = data.get("architecture")
        artifacts = data.get("artifacts")
        if not isinstance(license_data, Mapping):
            raise ModelManifestError("license must be an object")
        if not isinstance(runtime, Mapping):
            raise ModelManifestError("runtime must be an object")
        if not isinstance(architecture, Mapping):
            raise ModelManifestError("architecture must be an object")
        if not isinstance(artifacts, list) or not artifacts:
            raise ModelManifestError("artifacts must be a non-empty list")
        if not all(isinstance(item, Mapping) for item in artifacts):
            raise ModelManifestError("each artifact must be an object")

        parsed_artifacts = tuple(ModelArtifact.from_mapping(item) for item in artifacts)
        filenames = [artifact.filename for artifact in parsed_artifacts]
        roles = [artifact.role for artifact in parsed_artifacts]
        if len(filenames) != len(set(filenames)):
            raise ModelManifestError("artifact filenames must be unique")
        if len(roles) != len(set(roles)):
            raise ModelManifestError("artifact roles must be unique")

        noncommercial = license_data.get("noncommercial")
        if noncommercial is not True:
            raise ModelManifestError("the initial external model manifest must be noncommercial")

        model_license_url = _required_string(license_data, "url")
        if not model_license_url.startswith("https://"):
            raise ModelManifestError("license url must use HTTPS")
        runtime_source_commit = _required_string(runtime, "source_commit").lower()
        if _REVISION_PATTERN.fullmatch(runtime_source_commit) is None:
            raise ModelManifestError("runtime source_commit must be a full 40-character commit")
        distribution = runtime.get("distribution")
        if not isinstance(distribution, Mapping):
            raise ModelManifestError("runtime distribution must be an object")
        distribution_filename = _required_string(distribution, "filename")
        if Path(distribution_filename).name != distribution_filename:
            raise ModelManifestError("runtime distribution filename must be a safe basename")
        distribution_url = _required_string(distribution, "url")
        if not distribution_url.startswith("https://files.pythonhosted.org/"):
            raise ModelManifestError("runtime distribution must use official PyPI file hosting")
        distribution_sha256 = _required_string(distribution, "sha256").lower()
        if _SHA256_PATTERN.fullmatch(distribution_sha256) is None:
            raise ModelManifestError("runtime distribution sha256 is invalid")

        return cls(
            schema_version=schema_version,
            id=_required_string(data, "id"),
            backend_id=_required_string(data, "backend_id"),
            model_id=_required_string(data, "model_id"),
            model_license=_required_string(license_data, "spdx"),
            model_license_url=model_license_url,
            noncommercial=noncommercial,
            runtime_package=_required_string(runtime, "package"),
            runtime_version=_required_string(runtime, "version"),
            runtime_source_commit=runtime_source_commit,
            runtime_distribution_filename=distribution_filename,
            runtime_distribution_url=distribution_url,
            runtime_distribution_sha256=distribution_sha256,
            architecture_candidate=_required_string(architecture, "candidate"),
            architecture_status=_required_string(architecture, "status"),
            artifacts=parsed_artifacts,
        )


def load_model_manifest(path: Path) -> ModelManifest:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelManifestError(f"cannot read model manifest: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise ModelManifestError("model manifest must contain a JSON object")
    return ModelManifest.from_mapping(payload)


def verify_model_directory(manifest: ModelManifest, directory: Path) -> dict[str, object]:
    resolved_directory = directory.expanduser().resolve()
    if not resolved_directory.is_dir():
        raise ModelManifestError(f"model directory does not exist: {directory}")

    results: list[dict[str, object]] = []
    for artifact in manifest.artifacts:
        path = resolved_directory / artifact.filename
        if path.is_symlink():
            results.append(
                {
                    "role": artifact.role,
                    "filename": artifact.filename,
                    "status": "unsafe_symlink",
                    "expected_size_bytes": artifact.size_bytes,
                    "expected_sha256": artifact.sha256,
                }
            )
            continue
        if not path.is_file():
            results.append(
                {
                    "role": artifact.role,
                    "filename": artifact.filename,
                    "status": "missing",
                    "expected_size_bytes": artifact.size_bytes,
                    "expected_sha256": artifact.sha256,
                }
            )
            continue

        actual_size = path.stat().st_size
        if actual_size != artifact.size_bytes:
            results.append(
                {
                    "role": artifact.role,
                    "filename": artifact.filename,
                    "status": "size_mismatch",
                    "expected_size_bytes": artifact.size_bytes,
                    "actual_size_bytes": actual_size,
                    "expected_sha256": artifact.sha256,
                }
            )
            continue

        actual_checksum = _sha256(path)
        results.append(
            {
                "role": artifact.role,
                "filename": artifact.filename,
                "status": "verified" if actual_checksum == artifact.sha256 else "hash_mismatch",
                "expected_size_bytes": artifact.size_bytes,
                "actual_size_bytes": actual_size,
                "expected_sha256": artifact.sha256,
                "actual_sha256": actual_checksum,
            }
        )

    ready = all(item["status"] == "verified" for item in results)
    return {
        "schema_version": "1.0",
        "manifest_id": manifest.id,
        "backend_id": manifest.backend_id,
        "model_id": manifest.model_id,
        "license": {
            "spdx": manifest.model_license,
            "url": manifest.model_license_url,
            "noncommercial": manifest.noncommercial,
        },
        "runtime": {
            "package": manifest.runtime_package,
            "version": manifest.runtime_version,
            "source_commit": manifest.runtime_source_commit,
            "distribution": {
                "filename": manifest.runtime_distribution_filename,
                "sha256": manifest.runtime_distribution_sha256,
            },
        },
        "architecture": {
            "candidate": manifest.architecture_candidate,
            "status": manifest.architecture_status,
        },
        "artifacts": results,
        "ready_for_runtime_smoke_test": ready,
    }
