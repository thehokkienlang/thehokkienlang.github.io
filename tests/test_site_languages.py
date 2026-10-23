"""Language equivalence, shared routes, and Chinese publication boundaries."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_content import build_content, introduce_tli, navigation_links, home_launch, home_showcase, remove_leading_language_switcher
from site_languages import LANGUAGES, base_route, language_for_route, language_url


class SiteLanguageTests(unittest.TestCase):
    def test_tli_first_mention_expands_once(self):
        self.assertEqual(introduce_tli("Use Tangliengim, then Tangliengim."), "Use Tangliengim (TLI), then TLI.")
        self.assertEqual(introduce_tli("Use TLI."), "Use TLI.")

    def test_legacy_language_switcher_is_removed_without_touching_page_actions(self):
        legacy = '''\n<div class="wp-block-buttons is-layout-flex">
<div class="wp-block-button"><a href="https://hokkienlang.wordpress.com/zh-tw/">繁體中文</a></div>
<div class="wp-block-button"><a href="https://hokkienlang.wordpress.com/zh-cn/">简体中文</a></div>
</div>\n<p>Article</p>'''
        self.assertEqual(remove_leading_language_switcher(legacy), '<p>Article</p>')
        local = '''<div class="wp-block-buttons"><div class="wp-block-button"><a href="/zh-hans/">简体中文</a></div><div class="wp-block-button"><a href="/">English</a></div></div><p>文章</p>'''
        self.assertEqual(remove_leading_language_switcher(local), '<p>文章</p>')
        action = '<div class="wp-block-buttons"><div class="wp-block-button"><a href="/learn/">Learn</a></div></div>'
        self.assertEqual(remove_leading_language_switcher(action), action)

    def test_home_paths_keep_language_without_exposing_a_gated_search(self):
        from html.parser import HTMLParser

        class Tags(HTMLParser):
            def __init__(self):
                super().__init__()
                self.tags = []

            def handle_starttag(self, tag, attrs):
                self.tags.append((tag, dict(attrs)))

        for language in LANGUAGES:
            parser = Tags()
            parser.feed(home_launch(language))
            self.assertFalse(any(tag == "form" for tag, _ in parser.tags))
            self.assertFalse(any(tag == "input" for tag, _ in parser.tags))
            links = [attrs["href"] for tag, attrs in parser.tags if tag == "a"]
            self.assertIn(language_url("/ime/", language), links)
            self.assertIn(language_url("/dictionary/", language), links)
            self.assertIn(language_url("/songs/", language), links)
            self.assertIn(language_url("/read/", language), links)

    def test_home_showcase_curates_four_destinations_in_each_language(self):
        for language in LANGUAGES:
            body = home_showcase(language)
            self.assertEqual(body.count('class="home-feature '), 4)
            self.assertIn(language_url("/learn/introduction/", language), body)
            self.assertIn(language_url("/learn/tone-sandhi/", language), body)
            self.assertIn(language_url("/read/literature/lychee-mirror/", language), body)
            self.assertIn(language_url("/songs/", language), body)
            self.assertNotIn("hokkienlang.wordpress.com", body)

    def test_equivalent_pages_and_unavailable_translation(self):
        for language, prefix in (("en", ""), ("zh-Hant", "/zh-hant"), ("zh-Hans", "/zh-hans")):
            route = prefix + "/learn/spelling/"
            self.assertEqual(language_for_route(route), language)
            self.assertEqual(base_route(route), "/learn/spelling/")
            self.assertEqual(language_url(route, "zh-Hant"), "/zh-hant/learn/spelling/")
        self.assertIsNone(language_url("/read/stories/the-egg/", "zh-Hans"))
        self.assertEqual(language_url("/ime/", "zh-Hans"), "/ime/?lang=zh-Hans")
        self.assertEqual(language_url("/songs/example/", "zh-Hant"), "/songs/example/?lang=zh-Hant")

    def test_menu_translations_and_shared_destinations(self):
        nav = navigation_links("/zh-hant/learn/spelling/", variants=False)
        self.assertIn('href="/zh-hant/learn/spelling/" aria-current="page"', nav)
        self.assertIn('href="/dictionary/?lang=zh-Hant"', nav)
        self.assertIn('>學習</summary>', nav)
        self.assertIn('data-language-choice="en"', nav)
        self.assertIn('href="/zh-hans/learn/spelling/"', nav)
        egg = navigation_links("/zh-hant/read/stories/the-egg/", variants=False)
        self.assertNotIn('data-language-choice="zh-Hans"', egg)
        self.assertIn('>卵（繁體中文）</a>', navigation_links("/zh-hans/", variants=False))

    def test_build_rewrites_language_links_and_reuses_all_song_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            routes = build_content(ROOT, output)
            for language, folder in (("zh-Hant", "zh-hant"), ("zh-Hans", "zh-hans")):
                home = (output / folder / "index.html").read_text(encoding="utf-8")
                self.assertIn(f'<html lang="{language}">', home)
                article = home.split('<article class="imported-content">', 1)[1].split("</article>", 1)[0]
                self.assertNotIn('href="https://hokkienlang.wordpress.com/zh-', article)
                self.assertIn('class="home-showcase"', article)
                self.assertNotIn('class="wp-block-buttons', article)
                self.assertNotIn('class="source-link"', home)
                songs = (output / folder / "songs/index.html").read_text(encoding="utf-8")
                choices = json.loads((ROOT / "migration/song-urls.json").read_text(encoding="utf-8"))
                for row in choices:
                    self.assertIn(f'href="{row["new_url"]}?lang={language}"', songs)
                    self.assertNotIn(f'/{folder}{row["new_url"]}', routes)
            manifest = json.loads((output / "content-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["languages"], list(LANGUAGES))
            self.assertEqual(len([page for page in manifest["pages"] if page["language"] == "zh-Hant"]), 7)
            self.assertEqual(len([page for page in manifest["pages"] if page["language"] == "zh-Hans"]), 6)
            introduction = (output / "learn/introduction/index.html").read_text(encoding="utf-8")
            self.assertIn("Introduction to Tangliengim (TLI)", introduction)
            article = introduction.split('<article class="imported-content">', 1)[1].split("</article>", 1)[0]
            self.assertNotIn("Tangliengim", article)


if __name__ == "__main__":
    unittest.main()
