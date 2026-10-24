"""Transient Windows replacement denial must not lose the final preference update."""

import errno
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from candidate_preferences import FilePreferenceStore


def windows_error(code):
    error = PermissionError(errno.EACCES, "Windows file is busy")
    error.winerror = code
    return error


class PreferenceWriteTests(unittest.TestCase):
    def test_last_record_survives_transient_windows_denial(self):
        import os

        for code in (5, 32, 33):
            with self.subTest(winerror=code), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "preferences.json"
                store = FilePreferenceStore({"A"}, path)
                replace = os.replace
                attempts = []

                def busy_once(source, target):
                    attempts.append(source)
                    if len(attempts) == 1:
                        raise windows_error(code)
                    return replace(source, target)

                with patch("candidate_preferences.os.replace", side_effect=busy_once):
                    self.assertEqual(store.record("x", "A"), 1)
                self.assertEqual(len(attempts), 2)
                self.assertFalse(store._pending)
                self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["selections"]["x"]["A"], 1)

    def test_permanent_windows_denial_has_bounded_retry_and_preserves_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "preferences.json"
            original = b'{"version":1,"selections":{}}'
            path.write_bytes(original)
            store = FilePreferenceStore({"A"}, path)
            with patch("candidate_preferences.os.replace", side_effect=windows_error(5)) as replace, \
                 patch("candidate_preferences.time.monotonic", side_effect=[0, .1, .3]), \
                 patch("candidate_preferences.time.sleep") as sleep:
                self.assertFalse(store._save({"version": 1, "selections": {"x": {"A": 1}}}))
            self.assertEqual(replace.call_count, 2)
            sleep.assert_called_once_with(.005)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_unrelated_errors_do_not_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            store = FilePreferenceStore({"A"}, Path(directory) / "preferences.json")
            with patch("candidate_preferences.os.replace", side_effect=OSError("write failed")) as replace, \
                 patch("candidate_preferences.time.sleep") as sleep:
                self.assertFalse(store._save({"version": 1, "selections": {}}))
            self.assertEqual(replace.call_count, 1)
            sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
