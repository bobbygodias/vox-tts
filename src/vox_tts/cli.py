from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .backends import backend_descriptors
from .backends.f5_ptbr import F5PlanError, create_f5_plan
from .doctor import doctor_report
from .model_manifest import ModelManifestError, load_model_manifest, verify_model_directory
from .profiles import ProfileCatalogError, load_catalog


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vox", description="VOX local TTS control plane")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="inspect the local runtime without downloading models")

    profiles = subparsers.add_parser("profiles", help="validate and list voice profile manifests")
    profiles.add_argument("--directory", type=Path, default=Path("profiles"))

    subparsers.add_parser("backends", help="list registered backend descriptors")

    f5_plan = subparsers.add_parser(
        "f5-plan", help="validate and redact a planned F5 pt-BR synthesis without running it"
    )
    f5_plan.add_argument("--text-file", type=Path, required=True)
    f5_plan.add_argument("--reference", type=Path, required=True)
    f5_plan.add_argument("--reference-text-file", type=Path, required=True)
    f5_plan.add_argument("--checkpoint", type=Path, required=True)
    f5_plan.add_argument("--vocab", type=Path, required=True)
    f5_plan.add_argument("--model-name", required=True)
    f5_plan.add_argument("--output", type=Path, required=True)
    f5_plan.add_argument("--device", choices=("cpu", "cuda", "mps"), default="cpu")
    f5_plan.add_argument("--confirm-voice-rights", action="store_true")
    f5_plan.add_argument("--confirm-noncommercial-use", action="store_true")

    model_verify = subparsers.add_parser(
        "model-verify", help="verify local model files against a pinned manifest"
    )
    model_verify.add_argument("--manifest", type=Path, required=True)
    model_verify.add_argument("--directory", type=Path, required=True)
    return parser


def _emit(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "doctor":
        _emit(doctor_report())
        return 0
    if args.command == "backends":
        _emit([descriptor.as_dict() for descriptor in backend_descriptors()])
        return 0
    if args.command == "profiles":
        try:
            profiles = load_catalog(args.directory)
        except ProfileCatalogError as exc:
            _emit({"error": str(exc)})
            return 2
        _emit([profile.as_dict() for profile in profiles])
        return 0
    if args.command == "f5-plan":
        try:
            plan = create_f5_plan(
                text_file=args.text_file,
                reference_audio=args.reference,
                reference_text_file=args.reference_text_file,
                checkpoint=args.checkpoint,
                vocab=args.vocab,
                model_name=args.model_name,
                output=args.output,
                device=args.device,
                confirm_voice_rights=args.confirm_voice_rights,
                confirm_noncommercial_use=args.confirm_noncommercial_use,
            )
        except (F5PlanError, OSError) as exc:
            _emit({"error": str(exc)})
            return 2
        _emit(plan.as_dict())
        return 0 if plan.ready_to_execute else 3
    if args.command == "model-verify":
        try:
            manifest = load_model_manifest(args.manifest)
            report = verify_model_directory(manifest, args.directory)
        except (ModelManifestError, OSError) as exc:
            _emit({"error": str(exc)})
            return 2
        _emit(report)
        return 0 if report["ready_for_runtime_smoke_test"] else 3

    raise AssertionError(f"unhandled command: {args.command}")
