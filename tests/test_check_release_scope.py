"""The change-scoped release gate (`check_release.py --changed`) picks the right sections."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_release as gate  # noqa: E402


class ScopeTests(unittest.TestCase):
    def test_docs_only_changes_need_no_checks(self):
        paths = ["docs/README.md", "README.md", "AGENTS.md", "CLAUDE.md", ".claude/settings.json"]
        self.assertEqual(gate.scope_for_paths(paths), (gate.NO_CHECKS, set()))

    def test_no_changes_need_no_checks(self):
        self.assertEqual(gate.scope_for_paths([]), (gate.NO_CHECKS, set()))

    def test_css_change_runs_the_site_sections(self):
        kind, tags = gate.scope_for_paths(["apps/content-site/site.css", "shared/web-site-navigation.css"])
        self.assertEqual(kind, gate.TAGGED)
        self.assertEqual(tags, {"build", "site"})

    def test_script_change_runs_web_checks(self):
        kind, tags = gate.scope_for_paths(["shared/web-ime-core.js"])
        self.assertEqual(kind, gate.TAGGED)
        self.assertTrue({"js", "web", "build", "site", "webapps"} <= tags)

    def test_content_change_runs_the_site_sections(self):
        kind, tags = gate.scope_for_paths(["content/songs/song-1.json"])
        self.assertEqual(kind, gate.TAGGED)
        self.assertTrue({"build", "site"} <= tags)

    def test_dictionary_change_runs_the_full_source_gate(self):
        for path in ("data/hokkien_hanri_dict.tsv", "public/data/hokkien-hanri-dict.json",
                     "tools/dictionary_editor_service.py"):
            self.assertEqual(gate.scope_for_paths([path]), (gate.SOURCE_GATE, set()), path)

    def test_desktop_change_runs_desktop_checks(self):
        kind, tags = gate.scope_for_paths(["desktop/tangliengim_engine.py"])
        self.assertEqual(kind, gate.TAGGED)
        self.assertTrue({"desktop", "web"} <= tags)

    def test_audio_change_runs_audio_sections(self):
        kind, tags = gate.scope_for_paths(["public/audio/ㄱ/ka.wav"])
        self.assertEqual(kind, gate.TAGGED)
        self.assertTrue({"audio", "build"} <= tags)

    def test_unknown_path_runs_the_full_gate(self):
        for path in ("tools/check_release.py", ".github/workflows/pages.yml", "some/new/place.txt"):
            self.assertEqual(gate.scope_for_paths([path]), (gate.FULL_GATE, set()), path)

    def test_one_unknown_path_makes_a_mixed_change_full(self):
        self.assertEqual(gate.scope_for_paths(["docs/a.md", "package.json"]), (gate.FULL_GATE, set()))

    def test_dictionary_and_site_changes_together_run_the_full_gate(self):
        kind, _ = gate.scope_for_paths(["data/hokkien_hanri_dict.tsv", "apps/content-site/site.css"])
        self.assertEqual(kind, gate.FULL_GATE)


class SectionTagTests(unittest.TestCase):
    def test_every_section_has_tags(self):
        for source_only in (True, False):
            for section in gate.build_sections(source_only):
                self.assertTrue(section.tags, f"{section.label!r} needs an entry in SECTION_TAGS")


if __name__ == "__main__":
    unittest.main()
