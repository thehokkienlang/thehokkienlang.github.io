"""The change-scoped release gate (`check_release.py --changed`) picks the right sections."""

import sys
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_release as gate  # noqa: E402


class ScopeTests(unittest.TestCase):
    def test_website_edits(self):
        for path in ("content/songs/example.json", "apps/content-site/site.css",
                     "shared/web-site-navigation.js", "assets/images/example.webp",
                     "docs/lomari-review.json", "data/lyric-timings/song-1.json"):
            self.assertEqual(gate.profile_for_paths(["README.md", path]), "website", path)

    def test_dictionary_or_unknown_edits_take_precedence(self):
        for path in ("data/hokkien_hanri_dict.tsv", "public/data/runtime.json",
                     "apps/dictionary/app.js", "desktop/dictionary_editor.py",
                     "shared/web-ime-core.js", "tools/build_redirect_log.py", "new/input"):
            for paths in ([path], [path, "content/song.json"], ["content/song.json", path]):
                self.assertEqual(gate.profile_for_paths(paths), "dictionary", paths)

    def test_empty_and_documentation_changes(self):
        for paths in ([], ["README.md", "docs/notes.md", ".claude/settings.json"]):
            self.assertEqual(gate.profile_for_paths(paths), "none")

    def test_ci_reads_every_path_including_both_sides_of_moves(self):
        names = b"content/songs/a.json\0data/old.tsv\0"
        with patch.object(gate.subprocess, "run") as run:
            run.return_value.returncode = 0
            run.return_value.stdout = names
            paths = gate.changed_paths("base")
        self.assertEqual(paths, ["content/songs/a.json", "data/old.tsv"])
        self.assertEqual(gate.profile_for_paths(paths), "dictionary")
        self.assertIn("--no-renames", run.call_args.args[0])

    def test_website_sections(self):
        for source_only in (True, False):
            selected = {s.label for s in gate.build_sections(source_only, website=True)}
            self.assertIn("Stored readings keep Taipei sandhi digits", selected)
            self.assertIn("Website font coverage", selected)
            self.assertIn("Lomari follows the Hokkien text", selected)
            self.assertIn("JavaScript syntax: apps/content-site/site.js", selected)
            self.assertEqual("Validate published site" in selected, not source_only)
            self.assertNotIn("Build runtime dictionary data", selected)
            self.assertNotIn("Dictionary behavior and identity baseline", selected)


if __name__ == "__main__":
    unittest.main()
