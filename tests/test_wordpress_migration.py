"""Content preservation and scope checks for the authored WordPress presentations."""

import hashlib
import json
import sys
import tempfile
import unittest
import unicodedata
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_content import build_content, nasal_font_text, song_script_heading
from import_wordpress import ImportedHTML, PAGES
from import_wordpress_final import approved_song_routes
from site_languages import CHINESE_PAGES, LANGUAGES
from content_harmonisation import restore_body


# Approved source edits are scoped to specific pages and ruby indices.
APPROVED_COPY_EDITS = {
    3082: (
        ("HokkienLang is a space", "TheHokkienLang is a space"),
        (" (pronounced Tung-LEE-eng-im)", ""),
    ),
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
        self.in_lomari = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.parts = []
        elif tag == "rt":
            self.in_reading = True
        elif tag == "span" and "song-entry-lomari" in dict(attrs).get("class", "").split():
            self.in_lomari = True

    def handle_endtag(self, tag):
        if tag == "rt":
            self.in_reading = False
        elif tag == "span" and self.in_lomari:
            self.in_lomari = False
        elif tag == "a" and self.href is not None:
            self.links[self.href] = "".join(self.parts)
            self.href = None

    def handle_data(self, text):
        if self.href is not None and not self.in_reading and not self.in_lomari:
            self.parts.append(text)


class MigrationTests(unittest.TestCase):
    def test_all_imported_pronunciations_match_the_original(self):
        manifest = json.loads((ROOT / "migration/wordpress-map.json").read_text(encoding="utf-8"))
        audit_path = ROOT / "docs/harmonisation-3.2-audit.json"
        audit = json.loads(audit_path.read_text(encoding="utf-8"))["records"] if audit_path.exists() else {}
        self.assertTrue(set(PAGES).issubset({item["sourceId"] for item in manifest["records"]}))
        for item in manifest["records"]:
            with self.subTest(item=item["sourceId"]):
                original = json.loads((ROOT / "migration/wordpress-source" / f'{item["sourceId"]}.json').read_text(encoding="utf-8"))
                imported = json.loads((ROOT / item["file"]).read_text(encoding="utf-8"))
                before, after = Readings(), Readings()
                before.feed(original["content"])
                # Reverse only the hash-verified, reviewed edits before checking the archive.
                body = restore_body(imported["body"], audit[item["file"]]) if item["file"] in audit else imported["body"]
                after.feed(body)
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
                self.assertIn(imported["orthography"]["review"], {"pending", "source-preserved", "mixed-script-audited"})

    def test_build_publishes_authored_languages_and_keeps_unpublished_content_out(self):
        manifest = json.loads((ROOT / "migration/wordpress-map.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            routes = build_content(ROOT, Path(directory))
            # The Simplified Egg is derived from the audited Traditional source.
            self.assertEqual(len(routes), len(manifest["records"]) - 2 + 4 * len(LANGUAGES) + 1)
            self.assertEqual(set(manifest["languages"]), set(LANGUAGES))
            self.assertTrue({spec[0] for spec in CHINESE_PAGES}.issubset({item["sourceId"] for item in manifest["records"]}))
            self.assertIn("/zh-hant/read/stories/the-egg/", routes)
            self.assertIn("/zh-hans/read/stories/the-egg/", routes)
            self.assertNotIn("/songs/translation-notes/", routes)
            self.assertFalse((Path(directory) / "songs/translation-notes/index.html").exists())
            self.assertNotIn("/read/literature/lychee-mirror/", routes)
            self.assertFalse((Path(directory) / "read/literature/lychee-mirror/index.html").exists())
            for prefix in ("", "zh-hant", "zh-hans"):
                homepage = (Path(directory) / prefix / "index.html").read_text(encoding="utf-8")
                self.assertNotIn("lychee-mirror", homepage)
                pool = homepage.split('<template data-home-song-pool>', 1)[1].split('</template>', 1)[0]
                self.assertEqual(pool.count('<a '), 69)
                self.assertNotIn("月下煮茶", pool)
                self.assertEqual(pool.count('class="title-reading home-song-title"'), 69)
                self.assertIn('class="hanri-title"', pool)
            songs = (Path(directory) / "songs/index.html").read_text(encoding="utf-8")
            choices = json.loads((ROOT / "migration/song-urls.json").read_text(encoding="utf-8"))
            categories = json.loads((ROOT / "content/song-categories.json").read_text(encoding="utf-8"))
            self.assertTrue(all({"accent", "tint", "tintEnd"} <= set(category) for category in categories))
            self.assertEqual(songs.count('class="song-category"'), len(categories))
            self.assertEqual(songs.count("--category-tint-end:"), len(categories))
            self.assertEqual(songs.count('class="song-entry-lomari"'), len(choices))
            self.assertNotIn("song-entry--ruby-only", songs)
            self.assertGreater(songs.count('class="hanri-title"'), len(choices))
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



class ContentFontTests(unittest.TestCase):
    def test_stacked_nasal_marks_keep_exact_visible_text(self):
        value = '◌̰ a̰ â̰ ḭ́ oà̰ á̰ 𣍐 勿會 ᄁᅷ'
        rendered = nasal_font_text(value)
        self.assertEqual(rendered.count('class="nasal-grapheme"'), 6)
        for group in ['◌̰', 'â̰', 'ḭ́', 'oà̰', 'á̰']:
            self.assertIn('>' + unicodedata.normalize('NFC', group) + '</span>', rendered)
        text = Readings()
        text.feed(rendered)
        self.assertEqual(unicodedata.normalize('NFC', ''.join(text.text)), unicodedata.normalize('NFC', value))
        self.assertTrue(rendered.endswith('𣍐 勿會 ᄁᅷ'))

    def test_other_tones_keep_existing_font_selection(self):
        value = 'á â ā 漢字 ᄁᅷ ABC'
        self.assertEqual(nasal_font_text(value), value)

    def test_whole_nasal_word_uses_one_font_and_composed_upper_tone(self):
        self.assertEqual(nasal_font_text('siṵ̄'), '<span class="nasal-grapheme">' + unicodedata.normalize('NFC', 'siṵ̄') + '</span>')

    def test_song_heading_is_localizable_and_has_scoped_spacing_class(self):
        source = '<h3 class="wp-block-heading">漢諺混寫 Hanri-Hangul mixed script</h3><p>歌詞</p>'
        rendered = song_script_heading(source)
        self.assertIn('song-script-heading', rendered)
        self.assertIn('data-site-text="Hanri-Hangul mixed script"', rendered)
        self.assertNotIn('漢諺混寫 Hanri-Hangul', rendered)
        self.assertTrue(rendered.endswith('<p>歌詞</p>'))


if __name__ == "__main__":
    unittest.main()
