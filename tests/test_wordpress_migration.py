"""Content preservation and scope checks for the first English migration batch."""

import hashlib
import json
import sys
import tempfile
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_content import build_content
from import_wordpress import ImportedHTML, PAGES
from import_wordpress_final import approved_song_routes


class Readings(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.values = []
        self.text = []
        self.media = Counter()

    def handle_starttag(self, tag, attrs):
        if tag in {"iframe", "audio", "img"}:
            self.media[tag] += 1
        if tag == "rt":
            self.depth += 1
            self.values.append("")

    def handle_endtag(self, tag):
        if tag == "rt":
            self.depth = max(0, self.depth - 1)

    def handle_data(self, value):
        self.text.append(value)
        if self.depth:
            self.values[-1] += value


class MigrationTests(unittest.TestCase):
    def test_all_imported_pronunciations_match_the_original(self):
        manifest = json.loads((ROOT / "migration/wordpress-map.json").read_text(encoding="utf-8"))
        self.assertTrue(set(PAGES).issubset({item["sourceId"] for item in manifest["records"]}))
        for item in manifest["records"]:
            with self.subTest(item=item["sourceId"]):
                original = json.loads((ROOT / "migration/wordpress-source" / f'{item["sourceId"]}.json').read_text(encoding="utf-8"))
                imported = json.loads((ROOT / item["file"]).read_text(encoding="utf-8"))
                before, after = Readings(), Readings()
                before.feed(original["content"])
                after.feed(imported["body"])
                self.assertEqual(before.values, after.values)
                self.assertEqual(" ".join("".join(before.text).split()), " ".join("".join(after.text).split()))
                self.assertEqual(before.media, after.media)
                self.assertEqual(hashlib.sha256(original["content"].encode()).hexdigest(), imported["sourceSha256"])
                self.assertIn(imported["orthography"]["review"], {"pending", "source-preserved"})

    def test_build_publishes_approved_sources_and_keeps_chinese_pages_deferred(self):
        manifest = json.loads((ROOT / "migration/wordpress-map.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            routes = build_content(ROOT, Path(directory))
            self.assertEqual(len(routes), len(manifest["records"]) + 3)
            self.assertFalse(any(route.startswith("/zh-") for route in routes))
            self.assertNotIn(7647, {item["sourceId"] for item in manifest["records"]})
            songs = (Path(directory) / "songs/index.html").read_text(encoding="utf-8")
            choices = json.loads((ROOT / "migration/song-urls.json").read_text(encoding="utf-8"))
            if manifest["deferred"]["songs"] == 0:
                self.assertTrue(all(row["new_url"] in routes for row in choices))
                self.assertIn("/read/stories/the-egg/", routes)
                self.assertNotIn("https://hokkienlang.wordpress.com/2026/", songs)

    def test_import_rewrites_known_links_but_keeps_pending_targets_on_wordpress(self):
        parser = ImportedHTML("https://hokkienlang.wordpress.com/about/", {("hokkienlang.wordpress.com", "/tangliengim"): "/learn/introduction/"}, {}, ROOT, False)
        result = parser.render('<a href="/tangliengim/#tones">Guide</a><a href="/2025/song/">Song</a><script>bad()</script><ruby>㩼<rt>ᄋᅷˉ-</rt></ruby>')
        self.assertIn('href="/learn/introduction/#tones"', result)
        self.assertIn('href="https://hokkienlang.wordpress.com/2025/song/"', result)
        self.assertNotIn("bad()", result)
        self.assertIn("ᄋᅷˉ-", result)

    def test_song_form_has_exactly_two_fields(self):
        rows = json.loads((ROOT / "migration/song-urls.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), len({row["old_url"] for row in rows}))
        self.assertTrue(all(set(row) == {"old_url", "new_url"} for row in rows))
        form = (ROOT / "migration/song-url-form.html").read_text(encoding="utf-8")
        self.assertNotIn("__SONG_ROWS__", form)
        self.assertNotIn("the-egg/", form)

    def test_approved_routes_reject_collisions_and_missing_destinations(self):
        posts = [{"ID": 1, "type": "post", "URL": "https://hokkienlang.wordpress.com/song-a/"}, {"ID": 2, "type": "post", "URL": "https://hokkienlang.wordpress.com/song-b/"}]
        rows = [{"old_url": post["URL"], "new_url": "/songs/가/"} for post in posts]
        with self.assertRaises(ValueError):
            approved_song_routes(rows, posts)
        rows[1]["new_url"] = ""
        with self.assertRaises(ValueError):
            approved_song_routes(rows, posts)
        rows[1]["new_url"] = "/songs/𣍐散/"
        self.assertEqual(approved_song_routes(rows, posts)[1][1], "/songs/𣍐散/")


if __name__ == "__main__":
    unittest.main()
