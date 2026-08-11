import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from vox_tts.model_manifest import (
    ModelManifest,
    ModelManifestError,
    load_model_manifest,
    verify_model_directory,
)


ROOT = Path(__file__).resolve().parents[1]


def _manifest_payload(checkpoint: bytes, vocab: bytes) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "id": "test-model",
        "backend_id": "f5-ptbr",
        "model_id": "example/test",
        "license": {
            "spdx": "CC-BY-NC-4.0",
            "url": "https://creativecommons.org/licenses/by-nc/4.0/",
            "noncommercial": True,
        },
        "runtime": {
            "package": "f5-tts",
            "version": "1.1.22",
            "source_commit": "a" * 40,
            "distribution": {
                "filename": "f5_tts-1.1.22-py3-none-any.whl",
                "url": "https://files.pythonhosted.org/packages/test/f5_tts.whl",
                "sha256": "c" * 64,
            },
        },
        "architecture": {
            "candidate": "F5TTS_Base",
            "status": "requires-runtime-smoke-test",
        },
        "artifacts": [
            {
                "role": "checkpoint",
                "filename": "model.safetensors",
                "source_url": "https://huggingface.co/example/test/resolve/rev/model.safetensors",
                "source_revision": "b" * 40,
                "size_bytes": len(checkpoint),
                "sha256": hashlib.sha256(checkpoint).hexdigest(),
            },
            {
                "role": "vocabulary",
                "filename": "vocab.txt",
                "source_url": "https://huggingface.co/example/test/resolve/rev/vocab.txt",
                "source_revision": "b" * 40,
                "size_bytes": len(vocab),
                "sha256": hashlib.sha256(vocab).hexdigest(),
            },
        ],
    }


class ModelManifestTests(unittest.TestCase):
    def test_repository_manifest_is_valid_and_pinned(self) -> None:
        manifest = load_model_manifest(ROOT / "manifests/models/f5-ptbr.json")
        self.assertEqual(manifest.runtime_version, "1.1.22")
        self.assertEqual(
            manifest.runtime_distribution_sha256,
            "f0505dfb5463645caa526bace346ed1c89bcc9acb9ef42fdffd56c2c4c0a09d1",
        )
        self.assertEqual(len(manifest.artifacts), 2)
        self.assertTrue(all(len(item.sha256) == 64 for item in manifest.artifacts))

    def test_verification_accepts_exact_files(self) -> None:
        checkpoint = b"checkpoint"
        vocab = b"vocabulary"
        manifest = ModelManifest.from_mapping(_manifest_payload(checkpoint, vocab))
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "model.safetensors").write_bytes(checkpoint)
            (directory / "vocab.txt").write_bytes(vocab)
            report = verify_model_directory(manifest, directory)

        self.assertTrue(report["ready_for_runtime_smoke_test"])
        self.assertEqual(
            {item["status"] for item in report["artifacts"]}, {"verified"}
        )

    def test_verification_reports_size_mismatch_without_hashing(self) -> None:
        checkpoint = b"checkpoint"
        vocab = b"vocabulary"
        manifest = ModelManifest.from_mapping(_manifest_payload(checkpoint, vocab))
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "model.safetensors").write_bytes(b"wrong")
            (directory / "vocab.txt").write_bytes(vocab)
            report = verify_model_directory(manifest, directory)

        self.assertFalse(report["ready_for_runtime_smoke_test"])
        checkpoint_result = report["artifacts"][0]
        self.assertEqual(checkpoint_result["status"], "size_mismatch")
        self.assertNotIn("actual_sha256", checkpoint_result)

    def test_manifest_rejects_path_traversal(self) -> None:
        payload = _manifest_payload(b"checkpoint", b"vocabulary")
        payload["artifacts"][0]["filename"] = "../model.safetensors"
        with self.assertRaisesRegex(ModelManifestError, "safe basename"):
            ModelManifest.from_mapping(payload)

    def test_verification_rejects_symbolic_links(self) -> None:
        checkpoint = b"checkpoint"
        vocab = b"vocabulary"
        manifest = ModelManifest.from_mapping(_manifest_payload(checkpoint, vocab))
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            external = directory / "external.bin"
            external.write_bytes(checkpoint)
            (directory / "model.safetensors").symlink_to(external)
            (directory / "vocab.txt").write_bytes(vocab)
            report = verify_model_directory(manifest, directory)

        self.assertEqual(report["artifacts"][0]["status"], "unsafe_symlink")
        self.assertFalse(report["ready_for_runtime_smoke_test"])

    def test_invalid_json_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaisesRegex(ModelManifestError, "cannot read"):
                load_model_manifest(path)


if __name__ == "__main__":
    unittest.main()
