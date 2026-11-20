"""A typed non-final open tone 4 is read as Taipei's tone 1 (docs/sandhi-toggle-plan.md, step 7)."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from dictionary_editor_service import DictionaryEditorService  # noqa: E402
from typed_sandhi import typed_sandhi_to_taipei  # noqa: E402


class TypedSandhiTests(unittest.TestCase):
    def test_an_open_syllable_joined_to_the_next_reads_4_as_1(self):
        self.assertEqual(typed_sandhi_to_taipei("정4래5"), "정1래5")
        self.assertEqual(typed_sandhi_to_taipei("삐4훈4궤2"), "삐1훈1궤2")

    def test_a_mark_stays_a_mark_and_a_digit_stays_a_digit(self):
        self.assertEqual(typed_sandhi_to_taipei("정ˊ래ˉ"), "정ˆ래ˉ")
        self.assertEqual(typed_sandhi_to_taipei("정ˏ래ˍ"), "정ꞈ래ˍ")
        self.assertEqual(typed_sandhi_to_taipei("정4래ˉ"), "정1래ˉ")

    def test_citation_positions_keep_tone_4(self):
        for reading in ("정4", "심5래5", "정4 래5", "정4,래5", "정4’래5", "정4-래5", "정4*", ""):
            self.assertEqual(typed_sandhi_to_taipei(reading), reading, reading)

    def test_checked_syllables_keep_tone_4(self):
        # The checked finals of shared/tli-sandhi.json: ㄱ ㄷ ㅂ ㅎ ㅀ.
        for reading in ("뎍4호1", "뎓4호1", "뎝4호1", "뎧4호1", "뎛4호1"):
            self.assertEqual(typed_sandhi_to_taipei(reading), reading, reading)

    def test_other_tones_and_text_are_unchanged(self):
        self.assertEqual(typed_sandhi_to_taipei("정1래5정2래3"), "정1래5정2래3")
        self.assertEqual(typed_sandhi_to_taipei("歹勢 4"), "歹勢 4")

    def test_reading_it_twice_gives_the_same_result(self):
        once = typed_sandhi_to_taipei("정4래5정4래5")
        self.assertEqual(once, "정1래5정1래5")
        self.assertEqual(typed_sandhi_to_taipei(once), once)

    def test_the_dictionary_editor_stores_the_taipei_digit(self):
        stored = DictionaryEditorService.normalize({"hanri": "歹勢", "reading": "팰4세", "mandarin_trad": "〃"})
        self.assertEqual(stored["reading"], "팰1세")

    def test_the_dictionary_editor_keeps_a_correction_alias_as_typed(self):
        alias = DictionaryEditorService.normalize({"hanri": "먀4재", "reading": "먀4재*", "corrected": "먀1재"})
        self.assertEqual(alias["reading"], "먀4재*")
        self.assertEqual(alias["corrected"], "먀1재")


if __name__ == "__main__":
    unittest.main()
