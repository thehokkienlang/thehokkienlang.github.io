"""Tone 2 is written ˋ (above the syllable) or ˎ (inline), never as a backtick."""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

RUBY_TEXT = re.compile(r"<rt\b[^>]*>(.*?)</rt>", re.S)


class ToneTwoMarkTests(unittest.TestCase):
    def test_content_ruby_readings_never_use_backtick(self):
        offenders = []
        for path in sorted((ROOT / "content").rglob("*.json")):
            text = path.read_text(encoding="utf-8")
            count = sum(reading.count("`") for reading in RUBY_TEXT.findall(text))
            if count:
                offenders.append(f"{path.relative_to(ROOT)}: {count}")
        self.assertEqual(offenders, [], "use ˋ for tone 2 in ruby readings")

    def test_harmonisation_ruby_writes_upper_tone_two(self):
        from content_harmonisation import UPPER, reading_ruby
        self.assertNotIn("`", "".join(str(value) for value in UPPER.values()))
        for typed in ("디`", "디ˋ", "디ˎ"):
            ruby = reading_ruby("佇", typed, False)
            self.assertIn(">디ˋ</rt>", ruby, typed)
            self.assertNotIn("`", ruby)

    def test_tone_marker_annotation_style_writes_upper_tone_two(self):
        source = (ROOT / "desktop/hokkien_tone_marker_gui.py").read_text(encoding="utf-8")
        table = re.search(r"ANNOTATION_DIGIT_TO_SYMBOL = str\.maketrans\(\{(.*?)\}\)", source, re.S).group(1)
        self.assertEqual(dict(re.findall(r"'(\d)': '(.)'", table)), {"1": "ˆ", "2": "ˋ", "4": "ˊ", "5": "ˉ"})


if __name__ == "__main__":
    unittest.main()
