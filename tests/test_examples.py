"""Regression checks for the public example files and bundled assets."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


class ExampleStructureTests(unittest.TestCase):
    def example_files(self):
        return sorted(path for path in EXAMPLES.rglob("*.py") if path.name != "__init__.py")

    def test_examples_are_self_contained(self):
        for path in self.example_files():
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertNotRegex(source, r"(?m)^from examples\.")
                self.assertNotRegex(source, r"(?m)^from \.")

    def test_step_maps_match_code_labels(self):
        for path in self.example_files():
            source = path.read_text(encoding="utf-8")
            map_steps = re.findall(r"STEP-(\d{2}) -", source)
            code_steps = re.findall(r"STEP-(\d{2}):", source)
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(source.count("How it works:"), 1)
                self.assertEqual(map_steps, code_steps)
                self.assertEqual(
                    map_steps, [f"{number:02d}" for number in range(1, len(map_steps) + 1)]
                )

    def test_browser_examples_explain_adaptation(self):
        for path in self.example_files():
            source = path.read_text(encoding="utf-8")
            if "from seleniumbase import Driver" not in source:
                continue
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn("To use this example on another page", source)
                self.assertIn("CAPTCHA_SUCCESS_TEXT", source)

    def test_expected_assets_exist(self):
        expected = {
            "assets/image-to-text/text-captcha.png",
            "assets/image-to-text/captcha-digits.png",
            "assets/image-to-text/captcha-math.png",
            "assets/coordinates/coordinates-captcha.png",
            "assets/coordinates/fruit-click.png",
            "assets/coordinates/traffic-lights.png",
            "assets/yandex/yandex-smartcaptcha-image.jpg",
            "assets/yandex/yandex-smartcaptcha-instructions.png",
            "assets/yandex/yandex-smartcaptcha-kaleidoscope.jpg",
        }
        self.assertFalse([relative for relative in expected if not (ROOT / relative).is_file()])


if __name__ == "__main__":
    unittest.main()
