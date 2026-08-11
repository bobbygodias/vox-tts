from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .backends import backend_descriptors
from .doctor import doctor_report
from .profiles import ProfileCatalogError, load_catalog


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vox", description="VOX local TTS control plane")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="inspect the local runtime without downloading models")

    profiles = subparsers.add_parser("profiles", help="validate and list voice profile manifests")
    profiles.add_argument("--directory", type=Path, default=Path("profiles"))

    subparsers.add_parser("backends", help="list registered backend descriptors")
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

    raise AssertionError(f"unhandled command: {args.command}")

