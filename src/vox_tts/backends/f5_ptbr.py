from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import shutil
from typing import Sequence
import wave


MODEL_LICENSE = "CC BY-NC 4.0"
MODEL_LICENSE_URL = "https://creativecommons.org/licenses/by-nc/4.0/"
MODEL_ID = "firstpixel/F5-TTS-pt-br"
REFERENCE_AUDIO_SUFFIXES = frozenset({".flac", ".m4a", ".mp3", ".ogg", ".wav"})
CHECKPOINT_SUFFIXES = frozenset({".pt", ".safetensors"})


class F5PlanError(ValueError):
    """Raised when a safe F5 synthesis plan cannot be created."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_file(path: Path, label: str, suffixes: frozenset[str] | None = None) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise F5PlanError(f"{label} does not exist or is not a file: {path}")
    if suffixes is not None and resolved.suffix.lower() not in suffixes:
        expected = ", ".join(sorted(suffixes))
        raise F5PlanError(f"{label} must use one of these suffixes: {expected}")
    return resolved


def _read_required_text(path: Path, label: str) -> tuple[Path, str]:
    resolved = _require_file(path, label)
    try:
        value = resolved.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError as exc:
        raise F5PlanError(f"{label} must be UTF-8 text") from exc
    if not value:
        raise F5PlanError(f"{label} must not be blank")
    return resolved, value


def _wav_duration_seconds(path: Path) -> float | None:
    if path.suffix.lower() != ".wav":
        return None
    try:
        with wave.open(str(path), "rb") as audio:
            frame_rate = audio.getframerate()
            return audio.getnframes() / frame_rate if frame_rate else None
    except (EOFError, wave.Error):
        return None


@dataclass(frozen=True, slots=True)
class F5SynthesisPlan:
    model_name: str
    device: str
    output_name: str
    text_sha256: str
    text_characters: int
    reference_audio_sha256: str
    reference_audio_bytes: int
    reference_text_sha256: str
    reference_text_characters: int
    checkpoint_sha256: str
    checkpoint_bytes: int
    vocab_sha256: str
    vocab_bytes: int
    reference_duration_seconds: float | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    argv: tuple[str, ...]

    @property
    def ready_to_execute(self) -> bool:
        return not self.blockers

    def as_dict(self) -> dict[str, object]:
        """Return an audit-safe view without raw text or private input paths."""
        return {
            "schema_version": "1.0",
            "backend_id": "f5-ptbr",
            "model": {
                "id": MODEL_ID,
                "architecture": self.model_name,
                "license": MODEL_LICENSE,
                "license_url": MODEL_LICENSE_URL,
                "checkpoint_sha256": self.checkpoint_sha256,
                "checkpoint_bytes": self.checkpoint_bytes,
                "vocab_sha256": self.vocab_sha256,
                "vocab_bytes": self.vocab_bytes,
            },
            "request": {
                "language": "pt-BR",
                "text_sha256": self.text_sha256,
                "text_characters": self.text_characters,
                "reference_audio_sha256": self.reference_audio_sha256,
                "reference_audio_bytes": self.reference_audio_bytes,
                "reference_text_sha256": self.reference_text_sha256,
                "reference_text_characters": self.reference_text_characters,
                "reference_duration_seconds": self.reference_duration_seconds,
                "output_name": self.output_name,
            },
            "runtime": {
                "device": self.device,
                "ready_to_execute": self.ready_to_execute,
                "blockers": list(self.blockers),
                "command_preview": _redacted_argv(self.argv),
            },
            "warnings": list(self.warnings),
        }


def _redacted_argv(argv: Sequence[str]) -> list[str]:
    private_values = {
        "--ckpt_file": "<CHECKPOINT>",
        "--vocab_file": "<VOCAB>",
        "--ref_audio": "<REFERENCE_AUDIO>",
        "--ref_text": "<REFERENCE_TEXT>",
        "--gen_text": "<GENERATION_TEXT>",
        "--output_dir": "<OUTPUT_DIRECTORY>",
    }
    redacted: list[str] = []
    replace_next: str | None = None
    for item in argv:
        if replace_next is not None:
            redacted.append(replace_next)
            replace_next = None
        else:
            redacted.append(item)
            replace_next = private_values.get(item)
    return redacted


def create_f5_plan(
    *,
    text_file: Path,
    reference_audio: Path,
    reference_text_file: Path,
    checkpoint: Path,
    vocab: Path,
    model_name: str,
    output: Path,
    device: str = "cpu",
    confirm_voice_rights: bool = False,
    confirm_noncommercial_use: bool = False,
) -> F5SynthesisPlan:
    if not confirm_voice_rights:
        raise F5PlanError("voice-rights confirmation is required")
    if not confirm_noncommercial_use:
        raise F5PlanError(
            "noncommercial-use confirmation is required for firstpixel/F5-TTS-pt-br"
        )
    if not model_name.strip():
        raise F5PlanError("model_name must not be blank; it is never inferred from a checkpoint")
    if device not in {"cpu", "cuda", "mps"}:
        raise F5PlanError("device must be one of: cpu, cuda, mps")

    text_path, original_text = _read_required_text(text_file, "generation text file")
    reference_text_path, reference_text = _read_required_text(
        reference_text_file, "reference transcript file"
    )
    reference_path = _require_file(reference_audio, "reference audio", REFERENCE_AUDIO_SUFFIXES)
    checkpoint_path = _require_file(checkpoint, "checkpoint", CHECKPOINT_SUFFIXES)
    vocab_path = _require_file(vocab, "vocabulary", frozenset({".txt"}))

    output_path = output.expanduser().resolve()
    if output_path.suffix.lower() != ".wav":
        raise F5PlanError("output must use the .wav suffix")
    if not output_path.parent.is_dir():
        raise F5PlanError(f"output directory does not exist: {output_path.parent}")

    normalized_text = original_text.lower()
    normalized_reference_text = reference_text.lower()
    duration = _wav_duration_seconds(reference_path)
    if duration is not None and duration >= 12:
        raise F5PlanError("reference WAV must be shorter than 12 seconds")

    blockers: list[str] = []
    if shutil.which("f5-tts_infer-cli") is None:
        blockers.append("f5-tts_infer-cli was not found on PATH")
    if shutil.which("ffmpeg") is None:
        blockers.append("ffmpeg was not found on PATH")

    warnings = [
        "Model architecture is explicit and must match the downloaded checkpoint.",
        "The pt-BR checkpoint is CC BY-NC 4.0 and is not cleared for commercial use.",
        "Reference audio should end with about one second of silence.",
    ]
    if duration is None:
        warnings.append(
            "Reference duration could not be verified; confirm it is shorter than 12 seconds."
        )
    if normalized_text != original_text or normalized_reference_text != reference_text:
        warnings.append("Text was lowercased for the pt-BR checkpoint.")
    if re.search(r"\d", normalized_text):
        warnings.append("Generation text contains digits; write numbers out before synthesis.")

    argv = (
        "f5-tts_infer-cli",
        "--model",
        model_name.strip(),
        "--ckpt_file",
        str(checkpoint_path),
        "--vocab_file",
        str(vocab_path),
        "--ref_audio",
        str(reference_path),
        "--ref_text",
        normalized_reference_text,
        "--gen_text",
        normalized_text,
        "--output_dir",
        str(output_path.parent),
        "--output_file",
        output_path.name,
        "--device",
        device,
        "--vocoder_name",
        "vocos",
        "--nfe_step",
        "32",
        "--cfg_strength",
        "2.0",
        "--sway_sampling_coef",
        "-1.0",
        "--speed",
        "1.0",
        "--cross_fade_duration",
        "0.15",
    )

    return F5SynthesisPlan(
        model_name=model_name.strip(),
        device=device,
        output_name=output_path.name,
        text_sha256=_sha256(text_path),
        text_characters=len(original_text),
        reference_audio_sha256=_sha256(reference_path),
        reference_audio_bytes=reference_path.stat().st_size,
        reference_text_sha256=_sha256(reference_text_path),
        reference_text_characters=len(reference_text),
        checkpoint_sha256=_sha256(checkpoint_path),
        checkpoint_bytes=checkpoint_path.stat().st_size,
        vocab_sha256=_sha256(vocab_path),
        vocab_bytes=vocab_path.stat().st_size,
        reference_duration_seconds=duration,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
        argv=argv,
    )
