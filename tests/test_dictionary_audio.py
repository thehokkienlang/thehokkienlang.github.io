"""Keep generated audio lookup portable across fresh checkouts."""

import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_dictionary_json import validate_audio_filename_case


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
