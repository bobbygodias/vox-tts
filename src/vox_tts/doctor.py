from __future__ import annotations

import importlib.util
import platform
import shutil
import sys
from pathlib import Path

from .backends import backend_health


def _torch_report() -> dict[str, object]:
    if importlib.util.find_spec("torch") is None:
        return {"installed": False}
    try:
        import torch

        return {
            "installed": True,
            "version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        }
    except Exception as exc:  # pragma: no cover - depends on local binary runtime
        return {"installed": True, "import_error": str(exc)}


def doctor_report(path: Path | None = None) -> dict[str, object]:
    target = path or Path.cwd()
    disk = shutil.disk_usage(target)
    torch = _torch_report()
    recommended_device = "cuda" if torch.get("cuda_available") else "cpu"
    health = [item.as_dict() for item in backend_health()]
    return {
        "vox_version": "0.1.0",
        "python": platform.python_version(),
        "python_supported": sys.version_info >= (3, 12),
        "platform": platform.platform(),
        "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"),
        "disk_free_gib": round(disk.free / (1024**3), 2),
        "torch": torch,
        "recommended_device": recommended_device,
        "backends": health,
        "ready_for_live_synthesis": any(item["ready"] for item in health),
    }

