"""Content preservation and scope checks for the first English migration batch."""

import hashlib
import json
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_content import build_content
from import_wordpress import ImportedHTML, PAGES


class Readings(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.values = []

    def handle_starttag(self, tag, attrs):
        if tag == "rt":
            self.depth += 1
            self.values.append("")

    def handle_endtag(self, tag):
        if tag == "rt":
            self.depth = max(0, self.depth - 1)

    def handle_data(self, value):
        if self.depth:
            self.values[-1] += value


class MigrationTests(unittest.TestCase):
    def test_all_imported_pronunciations_match_the_original(self):
        manifest = json.loads((ROOT / "migration/wordpress-map.json").read_text(encoding="utf-8"))
        self.assertEqual({item["sourceId"] for item in manifest["records"]}, set(PAGES))
        for item in manifest["records"]:
            with self.subTest(item=item["sourceId"]):
                original = json.loads((ROOT / "migration/wordpress-source" / f'{item["sourceId"]}.json').read_text(encoding="utf-8"))
                imported = json.loads((ROOT / item["file"]).read_text(encoding="utf-8"))
                before, after = Readings(), Readings()
                before.feed(original["content"])
                after.feed(imported["body"])
                self.assertEqual(before.values, after.values)
                self.assertEqual(hashlib.sha256(original["content"].encode()).hexdigest(), imported["sourceSha256"])
                self.assertEqual(imported["orthography"]["review"], "pending")

    def test_build_does_not_publish_deferred_sources_or_chinese_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            routes = build_content(ROOT, Path(directory))
            self.assertEqual(len(routes), len(PAGES) + 3)
            self.assertFalse(any("the-egg" in route or route.startswith("/zh-") for route in routes))
            self.assertEqual([route for route in routes if route.startswith("/songs/")], ["/songs/", "/songs/translation-notes/"])
            songs = (Path(directory) / "songs/index.html").read_text(encoding="utf-8")
            self.assertIn("https://hokkienlang.wordpress.com/2026/", songs)

    def test_import_rewrites_known_links_but_keeps_pending_targets_on_wordpress(self):
        parser = ImportedHTML("https://hokkienlang.wordpress.com/about/", {("hokkienlang.wordpress.com", "/tangliengim"): "/learn/introduction/"}, {}, ROOT, False)
        result = parser.render('<a href="/tangliengim/#tones">Guide</a><a href="/2025/song/">Song</a><script>bad()</script><ruby>㩼<rt>ᄋᅷˉ-</rt></ruby>')
        self.assertIn('href="/learn/introduction/#tones"', result)
        self.assertIn('href="https://hokkienlang.wordpress.com/2025/song/"', result)
        self.assertNotIn("bad()", result)
        self.assertIn("ᄋᅷˉ-", result)

    def test_song_form_has_exactly_two_fields_and_no_assigned_urls(self):
        rows = json.loads((ROOT / "migration/song-urls.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), len({row["old_url"] for row in rows}))
        self.assertTrue(all(set(row) == {"old_url", "new_url"} for row in rows))
        form = (ROOT / "migration/song-url-form.html").read_text(encoding="utf-8")
        self.assertNotIn("__SONG_ROWS__", form)
        self.assertNotIn("the-egg/", form)


if __name__ == "__main__":
    unittest.main()
