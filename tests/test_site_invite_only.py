"""The password-gated tools are labelled invite-only wherever they are linked (audit A4)."""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_content
from site_languages import LANGUAGES, text

NOTE = re.compile(r'<a href="(?P<href>[^"]+)"[^>]*>[^<]*<span class="invite-only-note">(?P<note>[^<]+)</span></a>')


class InviteOnlyLabelTests(unittest.TestCase):
    def test_navigation_marks_only_the_gated_tools_in_every_language(self):
        for language in LANGUAGES:
            nav = build_content.navigation_links("/", language, variants=False)
            marked = {re.sub(r"\?.*", "", match["href"]).rstrip("/").split("/")[-1]: match["note"]
                      for match in NOTE.finditer(nav)}
            self.assertEqual(set(marked), {"dictionary", "translate"}, language)
            self.assertEqual(set(marked.values()), {text("Invite only", language)}, language)

    def test_lock_screens_say_the_tools_are_for_invited_visitors(self):
        for app in ("dictionary", "translate"):
            page = (ROOT / "apps" / app / "index.html").read_text(encoding="utf-8")
            self.assertIn("currently available to invited visitors", page, app)

    def test_built_home_page_marks_the_dictionary_link(self):
        home = ROOT / "_site/index.html"
        if not home.is_file():
            self.skipTest("needs a built site")
        tools = re.search(r'<div class="home-tools">.*?</div></div>', home.read_text(encoding="utf-8"), re.S)
        self.assertIsNotNone(tools)
        self.assertIn('Dictionary <span class="invite-only-note">Invite only</span>', tools.group(0))
        self.assertNotIn("Open IME <span", tools.group(0))


if __name__ == "__main__":
    unittest.main()
