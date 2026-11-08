"""Translator tone marks sit above their own syllable (audit A10)."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from node_runtime import node_environment


class TranslateToneOverlayTests(unittest.TestCase):
    def test_overlay_marks_are_positioned_over_syllables(self):
        node, env = node_environment()
        subprocess.run([node, str(ROOT / "tests/check_translate_tone_overlay.cjs")], env=env, check=True)


if __name__ == "__main__":
    unittest.main()
