import unittest

from vox_tts.models import SynthesisRequest, ValidationError, VoiceProfile


class ModelTests(unittest.TestCase):
    def test_voice_profile_requires_pt_br(self) -> None:
        with self.assertRaises(ValidationError):
            VoiceProfile.from_mapping(
                {
                    "schema_version": "0.1",
                    "id": "invalid",
                    "display_name": "Invalid",
                    "locale": "en-US",
                    "status": "design",
                    "origin_policy": "synthetic",
                    "target": {
                        "age_impression": "adult",
                        "pitch": "medium",
                        "texture": "neutral",
                        "pace": "medium",
                        "use_case": "test",
                    },
                    "backend_bindings": [],
                }
            )

    def test_synthesis_request_rejects_blank_text(self) -> None:
        with self.assertRaises(ValidationError):
            SynthesisRequest(text="  ", profile_id="profile", backend_id="backend")


if __name__ == "__main__":
    unittest.main()

