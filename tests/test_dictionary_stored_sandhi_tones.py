"""Stored readings keep Taipei sandhi digits (docs/sandhi-toggle-plan.md)."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_stored_sandhi_tones as check  # noqa: E402


class StoredSandhiToneTests(unittest.TestCase):
    def test_an_open_syllable_joined_to_the_next_with_tone_4_is_flagged(self):
        self.assertEqual(check.non_final_open_tone4("정4래5"), [1])
        self.assertEqual(check.non_final_open_tone4("삐4훈4궤2"), [1, 3])

    def test_citation_positions_are_not_flagged(self):
        for reading in ("정4", "심5래5", "정4 래5", "정4,래5", "정4’래5", "정4*", ""):
            self.assertEqual(check.non_final_open_tone4(reading), [], reading)

    def test_checked_syllables_are_not_flagged(self):
        # A checked syllable (final ㄱ, ㄷ, ㅂ, ㅎ) keeps its own tone before another syllable.
        self.assertEqual(check.non_final_open_tone4("뎩4호1"), [])

    def test_other_tones_are_never_flagged(self):
        self.assertEqual(check.non_final_open_tone4("정1래5정2래3"), [])

    def test_the_stored_dictionary_and_songs_pass(self):
        self.assertEqual(check.dictionary_problems(), [])
        self.assertEqual(check.song_problems(), [])


if __name__ == "__main__":
    unittest.main()
