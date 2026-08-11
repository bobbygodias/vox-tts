from pathlib import Path
import unittest

from vox_tts.profiles import load_catalog


ROOT = Path(__file__).resolve().parents[1]


class ProfileCatalogTests(unittest.TestCase):
    def test_initial_catalog_contains_four_distinct_profiles(self) -> None:
        profiles = load_catalog(ROOT / "profiles")
        self.assertEqual(len(profiles), 4)
        self.assertEqual(len({profile.id for profile in profiles}), 4)
        self.assertTrue(all(profile.locale == "pt-BR" for profile in profiles))
        self.assertTrue(all(profile.status == "design" for profile in profiles))


if __name__ == "__main__":
    unittest.main()

