"""Content preservation and scope checks for the authored WordPress presentations."""

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
from site_languages import CHINESE_PAGES, LANGUAGES


# Approved source edits are scoped to specific pages and ruby indices.
APPROVED_COPY_EDITS = {
    3082: (("HokkienLang is a space", "TheHokkienLang is a space"),),
    1258: (("welcome to HokkienLang.", "welcome to TheHokkienLang."),),
    6645: (("당ˉ롕임ˆ-", "당ˉ롕임ˆ"),),
}
APPROVED_RUBY_EDITS = {6645: {2: ("당ˉ롕임ˆ-", "당ˉ롕임ˆ")}}


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


class SongLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = {}
        self.href = None
        self.parts = []
        self.in_reading = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.parts = []
        elif tag == "rt":
            self.in_reading = True

    def handle_endtag(self, tag):
        if tag == "rt":
            self.in_reading = False
        elif tag == "a" and self.href is not None:
            self.links[self.href] = "".join(self.parts)
            self.href = None

    def handle_data(self, text):
        if self.href is not None and not self.in_reading:
            self.parts.append(text)


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
                expected_readings = before.values.copy()
                for index, (old, new) in APPROVED_RUBY_EDITS.get(item["sourceId"], {}).items():
                    self.assertEqual(expected_readings[index], old)
                    expected_readings[index] = new
                self.assertEqual(expected_readings, after.values)
                expected_text = " ".join("".join(before.text).split())
                for old, new in APPROVED_COPY_EDITS.get(item["sourceId"], ()):
                    self.assertEqual(expected_text.count(old), 1)
                    expected_text = expected_text.replace(old, new, 1)
                self.assertEqual(expected_text, " ".join("".join(after.text).split()))
                self.assertEqual(before.media, after.media)
                self.assertEqual(hashlib.sha256(original["content"].encode()).hexdigest(), imported["sourceSha256"])
                self.assertIn(imported["orthography"]["review"], {"pending", "source-preserved"})

    def test_build_publishes_authored_languages_and_keeps_unpublished_content_out(self):
        manifest = json.loads((ROOT / "migration/wordpress-map.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            routes = build_content(ROOT, Path(directory))
            self.assertEqual(len(routes), len(manifest["records"]) - 1 + 3 * len(LANGUAGES))
            self.assertEqual(set(manifest["languages"]), set(LANGUAGES))
            self.assertTrue({spec[0] for spec in CHINESE_PAGES}.issubset({item["sourceId"] for item in manifest["records"]}))
            self.assertIn("/zh-hant/read/stories/the-egg/", routes)
            self.assertNotIn("/zh-hans/read/stories/the-egg/", routes)
            self.assertNotIn("/songs/translation-notes/", routes)
            self.assertFalse((Path(directory) / "songs/translation-notes/index.html").exists())
            songs = (Path(directory) / "songs/index.html").read_text(encoding="utf-8")
            choices = json.loads((ROOT / "migration/song-urls.json").read_text(encoding="utf-8"))
            if manifest["deferred"]["songs"] == 0:
                self.assertTrue(all(row["new_url"] in routes for row in choices))
                self.assertIn("/read/stories/the-egg/", routes)
                self.assertNotIn("https://hokkienlang.wordpress.com/2026/", songs)
                labels = SongLinks()
                labels.feed(songs)
                for row in choices:
                    self.assertEqual(labels.links[row["new_url"]], row["display_title"])

    def test_import_rewrites_known_links_but_keeps_pending_targets_on_wordpress(self):
        parser = ImportedHTML("https://hokkienlang.wordpress.com/about/", {("hokkienlang.wordpress.com", "/tangliengim"): "/learn/introduction/"}, {}, ROOT, False)
        result = parser.render('<a href="/tangliengim/#tones">Guide</a><a href="/2025/song/">Song</a><script>bad()</script><ruby>㩼<rt>ᄋᅷˉ-</rt></ruby>')
        self.assertIn('href="/learn/introduction/#tones"', result)
        self.assertIn('href="https://hokkienlang.wordpress.com/2025/song/"', result)
        self.assertNotIn("bad()", result)
        self.assertIn("ᄋᅷˉ-", result)

    def test_song_form_retains_link_fields_and_separate_page_titles(self):
        rows = json.loads((ROOT / "migration/song-urls.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), len({row["old_url"] for row in rows}))
        self.assertTrue(all({"old_url", "new_url"} <= set(row) <= {"old_url", "new_url", "display_title"} for row in rows))
        form = (ROOT / "migration/song-url-form.html").read_text(encoding="utf-8")
        self.assertNotIn("__SONG_ROWS__", form)
        self.assertNotIn("the-egg/", form)
        self.assertIn('scope="col">Page title', form)

    def test_approved_routes_reject_collisions_and_missing_destinations(self):
        posts = [{"ID": 1, "type": "post", "URL": "https://hokkienlang.wordpress.com/song-a/"}, {"ID": 2, "type": "post", "URL": "https://hokkienlang.wordpress.com/song-b/"}]
        rows = [{"old_url": post["URL"], "new_url": "/songs/가/"} for post in posts]
        with self.assertRaises(ValueError):
            approved_song_routes(rows, posts)
        rows[1]["new_url"] = ""
        with self.assertRaises(ValueError):
            approved_song_routes(rows, posts)
        rows[1]["new_url"] = "/songs/𣍐散/"
        rows[1]["display_title"] = "𣍐散，同行！"
        self.assertEqual(approved_song_routes(rows, posts)[1][1], "/songs/𣍐散/")

    def test_approved_display_titles_do_not_replace_routes_or_original_titles(self):
        manifest = json.loads((ROOT / "migration/wordpress-map.json").read_text(encoding="utf-8"))
        records = {item["route"]: item for item in manifest["records"]}
        rows = json.loads((ROOT / "migration/song-urls.json").read_text(encoding="utf-8"))
        for row in rows:
            if "display_title" not in row:
                continue
            with self.subTest(route=row["new_url"]):
                content = json.loads((ROOT / records[row["new_url"]]["file"]).read_text(encoding="utf-8"))
                source = json.loads((ROOT / "migration/wordpress-source" / f'{content["sourceId"]}.json').read_text(encoding="utf-8"))
                self.assertEqual(content["title"], row["display_title"])
                self.assertEqual(content["route"], row["new_url"])
                self.assertEqual(content["originalTitle"], source["title"])


if __name__ == "__main__":
    unittest.main()
