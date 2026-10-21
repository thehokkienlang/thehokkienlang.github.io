"""Keep generated audio lookup portable across fresh checkouts."""

import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_dictionary_json import (
    DEFAULT_AUDIO_ROOT,
    load_ime_module,
    validate_audio_filename_case,
    with_singapore_audio_when_needed,
)


class DictionaryReadingAudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ime = load_ime_module()

    def test_resolved_word_tones_override_standalone_syllable_defaults(self) -> None:
        for reading, ending in (("란고", "ko3.wav"), ("란궤", "kue3.wav")):
            with self.subTest(reading=reading):
                audio = with_singapore_audio_when_needed(
                    self.ime, DEFAULT_AUDIO_ROOT, reading, hanri="難過"
                )
                for variant in (audio, audio.get("singapore", audio)):
                    self.assertEqual([s["tone"] for s in variant["segments"]], ["3", "3"])
                    self.assertTrue(variant["files"][0].endswith("/lan3.wav"))
                    self.assertTrue(variant["files"][1].endswith("/" + ending))

    def test_explicit_word_tones_are_preserved(self) -> None:
        audio = with_singapore_audio_when_needed(
            self.ime, DEFAULT_AUDIO_ROOT, "칟1토4", hanri="佚佗"
        )
        self.assertEqual([s["tone"] for s in audio["segments"]], ["1", "4"])


class AudioFilenameTests(unittest.TestCase):
    def test_lowercase_filenames_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ㅇ"
            path.mkdir()
            (path / "il1.wav").touch()
            validate_audio_filename_case(Path(directory))

    def test_mixed_case_filenames_are_rejected_with_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ㅇ"
            path.mkdir()
            (path / "Il1.wav").touch()
            with self.assertRaisesRegex(ValueError, "ㅇ/Il1.wav"):
                validate_audio_filename_case(Path(directory))


if __name__ == "__main__":
    unittest.main()
