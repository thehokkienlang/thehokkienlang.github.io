"""Language equivalence, shared routes, and Chinese publication boundaries."""

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_content import build_content, curate_home_body, split_song_notes, introduce_tli, navigation_links, home_launch, home_showcase, remove_leading_language_switcher, site_brand
from site_languages import LANGUAGES, base_route, language_for_route, language_url


class SiteLanguageTests(unittest.TestCase):
    def test_all_interfaces_share_one_brand_template(self):
        brand = site_brand(ROOT)
        self.assertIn('class="site-logo"', brand)
        self.assertIn('href="/zh-hant/"', site_brand(ROOT, "zh-Hant"))
        for app in ("dictionary", "ime"):
            source = (ROOT / "apps" / app / "index.html").read_text(encoding="utf-8")
            self.assertIn("__SITE_BRAND__", source)
            self.assertNotIn('class="site-logo"', source)
        content = (ROOT / "apps/content-site/page.html").read_text(encoding="utf-8")
        self.assertIn("__BRAND__", content)

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
        guide = legacy.replace("/zh-tw/", "/zh-tw-tangliengim/").replace("/zh-cn/", "/zh-cn-tangliengim/")
        self.assertEqual(remove_leading_language_switcher(guide), '<p>Article</p>')
        guide_local = local.replace('href="/zh-hans/"', 'href="/zh-hans/learn/introduction/"').replace('href="/"', 'href="/learn/introduction/"')
        self.assertEqual(remove_leading_language_switcher(guide_local), '<p>文章</p>')
        action = '<div class="wp-block-buttons"><div class="wp-block-button"><a href="/learn/">Learn</a></div></div>'
        self.assertEqual(remove_leading_language_switcher(action), action)
        egg = '<h2>능</h2><div class="wp-block-buttons"><div class="wp-block-button"><a href="/zh-hant/read/stories/the-egg/">繁體中文</a></div></div><p>Story</p>'
        self.assertEqual(remove_leading_language_switcher(egg), '<h2>능</h2><p>Story</p>')
        for path in ("content/stories/the-egg.json", "content/zh-hant/stories/the-egg.json"):
            source = json.loads((ROOT / path).read_text(encoding="utf-8"))
            cleaned = remove_leading_language_switcher(source["body"])
            self.assertNotIn('class="wp-block-buttons ', cleaned)
            self.assertIn('<h2 class="wp-block-heading">', cleaned)

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

    def test_home_showcase_curates_three_destinations_in_each_language(self):
        for language in LANGUAGES:
            body = home_showcase(language)
            self.assertEqual(body.count('class="home-feature '), 3)
            self.assertIn(language_url("/learn/tone-sandhi/", language), body)
            self.assertNotIn("lychee-mirror", body)
            self.assertIn("/read/stories/the-egg/", body)
            self.assertIn(language_url("/songs/", language), body)
            self.assertNotIn("hokkienlang.wordpress.com", body)

    def test_home_body_leads_with_the_comparison_and_ends_with_the_essay(self):
        body = ('<p>Intro</p><h2>Why</h2><p>Reason</p><h3>Same</h3><p>Take "student":</p>'
                '<ul><li>In Korean: <strong>학생</strong> (<em>hak-saeng</em>)</li>'
                '<li>In Hokkien: <strong><span style="x"><ruby>學生<rt>학솅ˆ</rt></ruby></span></strong> (<em>hak-siêng</em>)</li></ul>'
                '<p>Note</p><h2>Learn TLI</h2>')
        result = curate_home_body(body, "en", listen='<button>Listen</button>')
        self.assertLess(result.index('home-compare'), result.index('home-showcase'))
        self.assertLess(result.index('home-showcase'), result.index('home-essay'))
        self.assertEqual(result.count('<h3>Same</h3>'), 0)
        self.assertIn('<ruby>學生<rt>학솅ˆ</rt></ruby>', result)
        self.assertEqual(result.count('<button>Listen</button>'), 1)
        self.assertIn('/assets/audio/ko-haksaeng.mp3', result)
        self.assertIn('HappyMidnight', result)
        self.assertIn('https://creativecommons.org/licenses/by-sa/4.0/', result)
        self.assertTrue((ROOT / 'assets/audio/ko-haksaeng.mp3').is_file())
        self.assertLess(result.index('home-compare-hokkien'), result.index('<button>Listen</button>'))
        self.assertIn('<div class="home-essay"><p>Intro</p><h2>Why</h2><p>Reason</p>', result)

    def test_song_footnotes_show_one_language_per_page(self):
        cell = "<td>\n (中) 眼淚（俗字寫作「目屎」）。<br>\n (en) Tears.\n </td>"
        result = split_song_notes(cell)
        self.assertNotIn("(中)", result)
        self.assertNotIn("(en)", result)
        self.assertIn('<span data-content-lang="zh-Hant">眼淚（俗字寫作「目屎」）。</span>', result)
        self.assertIn('<span data-content-lang="zh-Hans">眼泪（俗字写作「目屎」）。</span>', result)
        self.assertIn('<span data-content-lang="en">Tears.</span>', result)

    def test_equivalent_pages_and_unavailable_translation(self):
        for language, prefix in (("en", ""), ("zh-Hant", "/zh-hant"), ("zh-Hans", "/zh-hans")):
            route = prefix + "/learn/spelling/"
            self.assertEqual(language_for_route(route), language)
            self.assertEqual(base_route(route), "/learn/spelling/")
            self.assertEqual(language_url(route, "zh-Hant"), "/zh-hant/learn/spelling/")
        self.assertEqual(language_url("/read/stories/the-egg/", "zh-Hans"), "/zh-hans/read/stories/the-egg/")
        self.assertEqual(language_url("/search/", "zh-Hans"), "/zh-hans/search/")
        self.assertEqual(language_url("/ime/", "zh-Hans"), "/ime/?lang=zh-Hans")
        self.assertEqual(language_url("/songs/example/", "zh-Hant"), "/songs/example/?lang=zh-Hant")

    def test_learn_path_orders_the_index_and_links_each_guide_onward(self):
        from build_content import learn_index, learn_next_link

        guides = [{"type": "guides", "language": "en", "route": route, "title": title} for route, title in (
            ("/learn/romanisation/", "Tangliengim romanisation"), ("/learn/spelling/", "Spelling guidelines"),
            ("/learn/tone-sandhi/", "Tone sandhi in Hokkien"), ("/learn/introduction/", "Introduction to Tangliengim"))]
        index = learn_index(guides, "en")
        positions = [index.index(f'href="{route}"') for route in (
            "/learn/introduction/", "/learn/tone-sandhi/", "/learn/spelling/", "/learn/romanisation/")]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(index.index("Start here"), index.index("Reference"))
        self.assertIn('<ol class="learn-path">', index)
        self.assertIn(">Introduction to TLI</a><p>", index)
        # Lessons lead on to the next lesson and then to the songs; reference pages stay in reference.
        self.assertIn('href="/learn/tone-sandhi/"', learn_next_link("/learn/introduction/", "en", guides))
        self.assertIn('href="/songs/"', learn_next_link("/learn/tone-sandhi/", "en", guides))
        self.assertIn('href="/learn/romanisation/"', learn_next_link("/learn/spelling/", "en", guides))
        self.assertIn('href="/learn/"', learn_next_link("/learn/romanisation/", "en", guides))
        self.assertEqual(learn_next_link("/songs/translation-notes/", "en", guides), "")
        # A guide not yet placed on the path is still listed.
        self.assertIn('href="/learn/new/"', learn_index(guides + [{**guides[0], "route": "/learn/new/"}], "en"))

    def test_menu_translations_and_shared_destinations(self):
        nav = navigation_links("/zh-hant/learn/spelling/", variants=False)
        self.assertIn('href="/zh-hant/learn/spelling/" aria-current="page"', nav)
        self.assertIn('href="/dictionary/?lang=zh-Hant"', nav)
        self.assertIn('class="site-search-link" href="/zh-hant/search/"', nav)
        self.assertIn('aria-label="搜尋"', nav)
        self.assertIn('>學習</summary>', nav)
        # Songs and Read are links of their own between Learn and Tools; there is no Explore menu.
        self.assertNotIn('>探索</summary>', nav)
        self.assertLess(nav.index('>學習</summary>'), nav.index('href="/zh-hant/songs/">歌曲</a>'))
        self.assertLess(nav.index('href="/zh-hant/songs/">歌曲</a>'), nav.index('href="/zh-hant/read/">閱讀</a>'))
        self.assertLess(nav.index('href="/zh-hant/read/">閱讀</a>'), nav.index('>工具</summary>'))
        self.assertNotIn('>主頁</a>', nav)
        self.assertIn('>閩南語輸入法</a>', nav)
        self.assertIn('>翻譯器 <span class="invite-only-note">僅限受邀</span></a>', nav)
        self.assertIn('data-language-choice="en"', nav)
        self.assertIn('href="/zh-hans/learn/spelling/"', nav)
        egg = navigation_links("/zh-hant/read/stories/the-egg/", variants=False)
        self.assertIn('data-language-choice="zh-Hans"', egg)
        self.assertIn('href="/zh-hans/read/stories/the-egg/"', egg)
        self.assertIn('href="/zh-hans/read/">阅读</a>', navigation_links("/zh-hans/", variants=False))
        self.assertIn('href="/zh-hant/read/" aria-current="page">閱讀</a>', egg)

    def test_build_rewrites_language_links_and_reuses_all_song_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            routes = build_content(ROOT, output)
            for language, folder in (("zh-Hant", "zh-hant"), ("zh-Hans", "zh-hans")):
                home = (output / folder / "index.html").read_text(encoding="utf-8")
                self.assertIn(f'<html lang="{language}">', home)
                expected_heading = {
                    "zh-Hant": '<span class="home-heading-segment">記錄著屬於</span><wbr><span class="home-heading-segment">閩南語的聲音。</span>',
                    "zh-Hans": '<span class="home-heading-segment">记录着属于</span><wbr><span class="home-heading-segment">闽南语的声音。</span>',
                }[language]
                self.assertIn(expected_heading, home)
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
            # Audit A9: the Songs page has a filter, and every song carries its search text.
            categories = json.loads((ROOT / "content/song-categories.json").read_text(encoding="utf-8"))
            for folder in ("", "zh-hant/", "zh-hans/"):
                songs = (output / folder / "songs/index.html").read_text(encoding="utf-8")
                with self.subTest(songs=folder):
                    self.assertIn('data-song-filter', songs)
                    self.assertIn('data-song-hanri-fold=', songs)
                    self.assertIn('&quot;後&quot;:&quot;后&quot;', songs)
                    self.assertEqual(songs.count('data-song-filter-category='), len(categories) + 1)
                    self.assertEqual(songs.count('<li data-song-search="'),
                                     sum(len(category["routes"]) for category in categories))
            # Lyric-only phrases are included in the catalogue filter index.
            songs = (output / "songs/index.html").read_text(encoding="utf-8")
            self.assertRegex(
                songs,
                r'data-song-lines="[^"]*寒天[^"]*"[^>]*><a[^>]+href="/songs/生份에릐/"',
            )
            self.assertRegex(
                songs,
                r'data-song-mandarin-search="[^"]*腳踏車[^"]*"[^>]*data-song-mandarin-title="腳踏車"[^>]*><a[^>]+href="/songs/跤踏車/"',
            )
            self.assertIn('class="song-entry-mandarin-match" hidden', songs)
            self.assertIn('class="song-entry-match" hidden', songs)
            # Only pages with real translated versions declare hreflang alternates.
            alternate = '<link rel="alternate" hreflang='
            song_page = (output / "songs/浪子回頭/index.html").read_text(encoding="utf-8")
            self.assertNotIn(alternate, song_page)
            about_page = (output / "about/index.html").read_text(encoding="utf-8")
            self.assertEqual(about_page.count(alternate), 3)
            self.assertIn('hreflang="zh-Hant" href="https://thehokkienlang.github.io/zh-hant/about/"', about_page)
            # Audit A5: each page loads only the scripts it uses.
            def scripts(relative):
                page = (output / relative / "index.html").read_text(encoding="utf-8")
                return {name: name in page for name in ("web-ime-core.js", "web-hangul-ime.js", "web-lyric-sync.js")}
            for relative, ime, lyric in (("about", False, False), ("learn/spelling", False, False),
                                         ("zh-hant/learn/tone-sandhi", False, False), ("search", True, False),
                                         ("songs", True, False), ("songs/浪子回頭", True, True)):
                with self.subTest(scripts=relative):
                    self.assertEqual(scripts(relative), {"web-ime-core.js": ime, "web-hangul-ime.js": ime,
                                                         "web-lyric-sync.js": lyric})
            # No published page links to the archived WordPress site.
            for page in output.rglob("index.html"):
                html_text = page.read_text(encoding="utf-8")
                links = re.findall(r'href="(https?://[^"]*wordpress\.com[^"]*)"', html_text)
                relative = page.relative_to(output).parent.as_posix() + "/"
                with self.subTest(page=relative):
                    self.assertEqual(links, [])
            manifest = json.loads((output / "content-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["languages"], list(LANGUAGES))
            self.assertEqual(len([page for page in manifest["pages"] if page["language"] == "zh-Hant"]), 7)
            self.assertEqual(len([page for page in manifest["pages"] if page["language"] == "zh-Hans"]), 7)
            derived = next(page for page in manifest['pages'] if page['route'] == '/zh-hans/read/stories/the-egg/')
            self.assertEqual(derived['derivedFrom']['route'], '/zh-hant/read/stories/the-egg/')
            for prefix, subtitle in (('', 'The Egg'), ('zh-hant/', '蛋'), ('zh-hans/', '蛋')):
                story = (output / prefix / 'read/stories/the-egg/index.html').read_text(encoding='utf-8')
                self.assertIn('<ruby class="hanri-title">卵<rt>능ˉ</rt></ruby>', story)
                self.assertIn(f'<h2 class="story-subtitle">{subtitle}</h2>', story)
                self.assertIn('2352652016', story)
                self.assertNotIn('2325470030', story)
                self.assertIn('href="/zh-hans/read/stories/the-egg/"', story)
                self.assertIn('href="/zh-hant/read/stories/the-egg/"', story)
            simplified_story = (output / 'zh-hans/read/stories/the-egg/index.html').read_text(encoding='utf-8')
            self.assertIn('荷属福尔摩沙', simplified_story)
            self.assertNotIn('荷屬福爾摩沙', simplified_story)
            self.assertIn('href="/zh-hans/read/stories/the-egg/"', (output / 'zh-hans/read/index.html').read_text(encoding='utf-8'))
            introduction = (output / "learn/introduction/index.html").read_text(encoding="utf-8")
            self.assertIn("Introduction to Tangliengim (TLI)", introduction)
            article = introduction.split('<article class="imported-content">', 1)[1].split("</article>", 1)[0]
            self.assertNotIn("Tangliengim", article)


if __name__ == "__main__":
    unittest.main()
