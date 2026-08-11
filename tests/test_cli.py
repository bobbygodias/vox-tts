from contextlib import redirect_stdout
from io import StringIO
import json
import unittest

from vox_tts.cli import main
from vox_tts.doctor import doctor_report


class CliTests(unittest.TestCase):
    def test_backends_command_returns_two_descriptors(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            result = main(["backends"])
        payload = json.loads(output.getvalue())
        self.assertEqual(result, 0)
        self.assertEqual({item["id"] for item in payload}, {"f5-ptbr", "xtts-v2"})

    def test_doctor_is_diagnostic_not_a_readiness_claim(self) -> None:
        report = doctor_report()
        self.assertIn("ready_for_live_synthesis", report)
        self.assertIn("backends", report)
        self.assertIn("torch", report)


if __name__ == "__main__":
    unittest.main()

