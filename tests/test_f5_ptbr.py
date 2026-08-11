import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import wave

from vox_tts.backends.f5_ptbr import F5PlanError, create_f5_plan


class F5PlanTests(unittest.TestCase):
    def _fixture(self, root: Path) -> dict[str, Path]:
        text = root / "text.txt"
        text.write_text("Olá, mundo 2!", encoding="utf-8")
        transcript = root / "reference.txt"
        transcript.write_text("Esta é a referência.", encoding="utf-8")
        checkpoint = root / "model.safetensors"
        checkpoint.write_bytes(b"fake-checkpoint")
        vocab = root / "vocab.txt"
        vocab.write_text("a\nb\nc\n", encoding="utf-8")
        reference = root / "reference.wav"
        with wave.open(str(reference), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(16_000)
            audio.writeframes(b"\x00\x00" * 16_000)
        return {
            "text_file": text,
            "reference_audio": reference,
            "reference_text_file": transcript,
            "checkpoint": checkpoint,
            "vocab": vocab,
            "output": root / "out.wav",
        }

    def test_consent_and_noncommercial_confirmation_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self._fixture(Path(temporary))
            with self.assertRaisesRegex(F5PlanError, "voice-rights"):
                create_f5_plan(model_name="F5TTS_Base", **paths)
            with self.assertRaisesRegex(F5PlanError, "noncommercial-use"):
                create_f5_plan(
                    model_name="F5TTS_Base", confirm_voice_rights=True, **paths
                )

    @patch("vox_tts.backends.f5_ptbr.shutil.which", return_value="/usr/bin/tool")
    def test_safe_view_redacts_private_inputs(self, _which: object) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self._fixture(Path(temporary))
            plan = create_f5_plan(
                model_name="F5TTS_Base",
                confirm_voice_rights=True,
                confirm_noncommercial_use=True,
                **paths,
            )
            payload = plan.as_dict()
            encoded = json.dumps(payload, ensure_ascii=False)

            self.assertTrue(payload["runtime"]["ready_to_execute"])
            self.assertNotIn("Olá, mundo", encoded)
            self.assertNotIn(str(paths["reference_audio"]), encoded)
            self.assertIn("<REFERENCE_AUDIO>", encoded)
            self.assertIn("--ckpt_file", plan.argv)
            self.assertIn("olá, mundo 2!", plan.argv)
            self.assertIn("Generation text contains digits", " ".join(plan.warnings))

    @patch("vox_tts.backends.f5_ptbr.shutil.which", return_value=None)
    def test_missing_runtime_is_a_blocker_not_a_download(self, _which: object) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self._fixture(Path(temporary))
            plan = create_f5_plan(
                model_name="F5TTS_Base",
                confirm_voice_rights=True,
                confirm_noncommercial_use=True,
                **paths,
            )
            self.assertFalse(plan.ready_to_execute)
            self.assertEqual(len(plan.blockers), 2)


if __name__ == "__main__":
    unittest.main()
