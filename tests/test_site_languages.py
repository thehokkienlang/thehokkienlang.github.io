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
        self.assertIn('class="site-header-search" role="search" action="/zh-hant/search/" method="get"', nav)
        self.assertIn('id="headerSearchZhHantInput" class="tli-search-input" type="text" name="q"', nav)
        self.assertIn('class="hangul-keyboard-toggle" type="button" aria-pressed="false"', nav)
        self.assertIn('placeholder="搜尋頁面、歌曲與故事…"', nav)
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

    def test_header_has_the_sandhi_setting_in_each_language_and_every_page_loads_its_script(self):
        from build_content import SANDHI_NAV_LABELS
        script = (ROOT / "shared/web-sandhi-preference.js").read_text(encoding="utf-8")
        for language, words in SANDHI_NAV_LABELS.items():
            nav = navigation_links("/", language, variants=False)
            self.assertEqual(nav.count("data-sandhi-choice="), 2, language)
            self.assertIn('data-sandhi-choice="taipei"', nav)
            self.assertIn('data-sandhi-choice="singapore"', nav)
            self.assertIn(f'<span class="site-sandhi-label">{(words["sandhi"] + " " + words["change"]).strip()}</span>', nav)
            guide = language_url("/learn/tone-sandhi/", language)
            term = f'<a class="site-sandhi-guide" href="{guide}">{words["term"]}</a>'
            self.assertIn(words["note"].format(term=term), nav)
            # The setting sits in the language menu, after the language choices.
            self.assertLess(nav.index("data-language-choice"), nav.index("data-sandhi-choice"))
            # The words in the page header and the ones in the script are the same.
            for word in words.values():
                self.assertIn(word.format(term=words["term"]), script, f"{language}: {word!r} is missing from web-sandhi-preference.js")
        # The choices come in the Traditional and Simplified variants of the header too.
        with_variants = navigation_links("/", "en")
        self.assertEqual(with_variants.count("data-sandhi-choice="), 2 * 3)
        # The IME Pad's buttons and the Translator's menu are controls of the same preference.
        ime = (ROOT / "apps/ime/index.html").read_text(encoding="utf-8")
        self.assertIn('id="taipeiButton" class="sandhi-button active" type="button" data-sandhi-choice="taipei"', ime)
        self.assertIn('data-sandhi-choice="singapore"', ime)
        self.assertNotIn('web-sandhi-preference.js" defer', ime, "ime.js runs at the end of the body, so the preference must load first")
        translator = (ROOT / "apps/translate/index.html").read_text(encoding="utf-8")
        self.assertIn('<select id="sandhiMode" data-sandhi-select>', translator)
        for page in ("apps/content-site/page.html", "apps/dictionary/index.html", "apps/ime/index.html", "apps/translate/index.html"):
            source = (ROOT / page).read_text(encoding="utf-8")
            self.assertIn("/shared/web-sandhi-preference.js", source, page)
            self.assertLess(source.index("web-sandhi-preference.js"), source.index("web-site-language.js"), page)
        for script in ("apps/ime/ime.js", "apps/translate/translate.js"):
            self.assertIn("TliSandhiPreference", (ROOT / script).read_text(encoding="utf-8"), script)

    def test_listen_buttons_carry_singapore_clips_only_where_they_differ(self):
        from build_content import listen_button, play_button
        taipei = [{"file": "/public/audio/a/an1.wav"}]
        singapore = [{"file": "/public/audio/a/an4.wav"}]
        both = play_button("en", taipei, singapore)
        self.assertIn('data-tli-audio="[{&quot;file&quot;:&quot;/public/audio/a/an1.wav&quot;}]"', both)
        self.assertIn('data-tli-audio-singapore="[{&quot;file&quot;:&quot;/public/audio/a/an4.wav&quot;}]"', both)
        for same in (None, [], taipei):
            self.assertNotIn("data-tli-audio-singapore", play_button("en", taipei, same))
        # Entries read from the built dictionary: one that has Singapore clips and one that does not.
        entries = json.loads((ROOT / "public/data/hokkien-hanri-dict.json").read_text(encoding="utf-8"))["entries"]
        with_singapore = next(e for e in entries if (e.get("audio") or {}).get("singapore", {}).get("segments")
                              and e["audio"]["singapore"]["segments"] != e["audio"].get("segments"))
        button = listen_button(ROOT, "en", with_singapore["hanri"], with_singapore["reading"])
        self.assertIn("data-tli-audio-singapore=", button)
        # The homepage's own button (學生, a checked syllable) sounds the same in both and has no second set.
        self.assertNotIn("data-tli-audio-singapore", listen_button(ROOT, "en", "學生", "학솅1"))
        # site.js plays the clips for the preference.
        site_js = (ROOT / "apps/content-site/site.js").read_text(encoding="utf-8")
        self.assertIn("tliAudioSingapore", site_js)
        self.assertIn("TliSandhiPreference", site_js)

    def test_tone_sandhi_guide_follows_the_sandhi_preference(self):
        import image_descriptions
        from build_content import expand_listen_tokens
        for folder, language in (("content/guides", "en"), ("content/zh-hant/guides", "zh-Hant"), ("content/zh-hans/guides", "zh-Hans")):
            body = json.loads((ROOT / folder / "tone-sandhi.json").read_text(encoding="utf-8"))["body"]
            with self.subTest(language=language):
                # Both versions of the pattern diagram are there; the page shows the one for the preference.
                self.assertEqual(body.count('data-sandhi-show="taipei"'), 1)
                self.assertEqual(body.count('data-sandhi-show="singapore"'), 1)
                self.assertEqual(len(re.findall(r"singapore-sandhi(?:-sc)?\.png", body)), 1)
                # The one example whose sandhi differs between the two (水內) is replaced by 心內, which
                # sounds the same in both, so no recording needs switching.
                self.assertNotIn("쥐래", body)
                self.assertNotIn("jûi", body.replace("û", "û"))
                self.assertIn("[[tli-listen 心內 심5래5]]", body)
                playable = expand_listen_tokens(ROOT, language, body)
                self.assertNotIn("[[tli-listen", playable)
                self.assertIn('class="tli-listen" data-tli-audio=', playable)
                self.assertNotIn("data-tli-audio-singapore", playable, "心內 sounds the same in both")
        # The Singapore diagram's text version differs from the Taipei one in one row: Falling goes to Rising.
        for language in ("en", "zh-Hant", "zh-Hans"):
            rows = dict((tone, after) for tone, _example, after in image_descriptions._SANDHI_ROWS[language])
            singapore = dict((tone, after) for tone, _example, after in image_descriptions._SANDHI_ROWS_SINGAPORE[language])
            changed = {tone for tone in rows if rows[tone] != singapore[tone]}
            self.assertEqual(len(changed), 1, language)
            (falling,) = changed
            self.assertEqual(rows[falling], next(tone for tone in rows if tone.startswith(("High", "高")) and "checked" not in tone and "入" not in tone))
            self.assertEqual(singapore[falling], next(tone for tone in rows if tone.startswith(("Rising", "升"))))
        self.assertIn("singapore-sandhi.png", image_descriptions.ALT_TEXT)
        self.assertEqual(image_descriptions.TEXT_VERSIONS["singapore-sandhi-sc.png"], "singapore")
        for name in ("singapore-sandhi.png", "singapore-sandhi-sc.png"):
            self.assertTrue((ROOT / "assets/content/wordpress" / name).is_file(), name)

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
            sounds = json.loads((ROOT / "content/song-sounds.json").read_text(encoding="utf-8"))
            moods = json.loads((ROOT / "content/song-moods.json").read_text(encoding="utf-8"))
            song_count = len(json.loads((ROOT / "migration/song-urls.json").read_text(encoding="utf-8")))
            for folder in ("", "zh-hant/", "zh-hans/"):
                songs = (output / folder / "songs/index.html").read_text(encoding="utf-8")
                with self.subTest(songs=folder):
                    self.assertIn('data-song-filter', songs)
                    filter_heading = {"": "Filter by", "zh-hant/": "篩選條件", "zh-hans/": "筛选条件"}[folder]
                    self.assertIn(f'<p class="song-filter-heading">{filter_heading}</p>', songs)
                    self.assertEqual(re.findall(r'data-song-filter-sound="([^"]*)"', songs), ["", "modern", "classic", "roots"])
                    singer_name = "陈佳" if folder == "zh-hans/" else "陳佳"
                    self.assertRegex(songs, rf'<span class="song-entry-singer"[^>]*>{singer_name}</span>')
                    band_name = "椅子乐团" if folder == "zh-hans/" else "椅子樂團"
                    self.assertRegex(songs, rf'<span class="song-entry-singer"[^>]*>{band_name}</span>')
                    # The box is the shared one, and the page carries no search data of its own:
                    # the Hanri table and the lyrics come from public/data and are cached there.
                    self.assertEqual(songs.count('data-tli-search'), 4)
                    self.assertEqual(songs.count('id="songFilterInput"'), 1)
                    self.assertEqual(songs.count('class="tli-search-clear"'), 4)
                    self.assertNotIn('data-song-hanri-fold', songs)
                    self.assertNotIn('data-song-lines', songs)
                    self.assertLess(len(songs), 120_000)
                    self.assertEqual(songs.count('data-song-filter-sound='), len(sounds) + 1)
                    self.assertEqual(songs.count('data-song-filter-mood='), len(moods) + 1)
                    self.assertEqual(songs.count('<li data-song-route="'), song_count)
                    self.assertEqual(songs.count('data-song-sound="'), len(sounds))
                    self.assertIn('data-song-filter-clear', songs)
                    self.assertIn('data-song-row-mood="', songs)
                    for script in ("web-site-search-variants", "web-search-box", "web-song-search"):
                        self.assertIn(f'/shared/{script}.js', songs)
            # Lyric-only phrases and Mandarin titles are in the song search index the filter reads.
            index = json.loads((output / "public/data/song-search-index.json").read_text(encoding="utf-8"))
            by_route = {song["route"]: song for song in index["songs"]}
            self.assertEqual(len(by_route), song_count)
            self.assertTrue(any("寒天" in line[2] for line in by_route["/songs/生份에릐/"]["lines"]))
            self.assertIn("腳踏車", by_route["/songs/跤踏車/"]["mandarinSearch"])
            self.assertEqual(by_route["/songs/跤踏車/"]["mandarinTitle"], "腳踏車")
            self.assertEqual(by_route["/songs/跤踏車/"]["urls"]["zh-Hant"], language_url("/songs/跤踏車/", "zh-Hant"))
            self.assertIn(by_route["/songs/跤踏車/"]["sound"], index["sounds"])
            self.assertTrue(set(by_route["/songs/跤踏車/"]["moods"]) <= set(index["moods"]))
            self.assertEqual(by_route["/songs/跤踏車/"]["singer"], "王識賢")
            # A song with versions lists its original's singer; the Teochew song carries its badge.
            self.assertEqual(by_route["/songs/世界第一等/"]["singer"], "劉德華")
            self.assertEqual(by_route["/songs/月下煮茶/"]["dialect"], "teochew")
            for title in ("敢傻敢衝", "魚仔", "身騎白馬", "你啊你啊"):
                self.assertEqual(by_route[f"/songs/{title}/"]["dialect"], "mandarin")
                song_markup = (output / f"songs/{title}/index.html").read_text(encoding="utf-8")
                self.assertIn('class="song-dialect-badge"', song_markup)
                for label in ("Mandarin", "華語", "华语"):
                    self.assertIn(label, song_markup)
            self.assertEqual(json.loads((output / "public/data/hanri-fold.json").read_text(encoding="utf-8"))["hanriFold"]["後"], "后")
            # Each lyric match can open its song at that line: the first line of a song is line 1.
            self.assertEqual(by_route["/songs/生份에릐/"]["lines"][0][4], 1)
            # The Songs sub-header, under the main header: on every song page a breadcrumb
            # (Songs > Category) and the search box with its dropdown.
            song_page = (output / "songs/生份에릐/index.html").read_text(encoding="utf-8")
            self.assertEqual(song_page.count('class="songs-subheader"'), 1)
            self.assertLess(song_page.index("</header>"), song_page.index('class="songs-subheader"'))
            self.assertLess(song_page.index('class="songs-subheader"'), song_page.index("<main"))
            self.assertEqual(song_page.count('id="songSearchInput"'), 1)
            self.assertEqual(song_page.count('tli-search--compact'), 4)
            self.assertIn('id="songSearchResults" class="tli-search-dropdown"', song_page)
            self.assertIn('data-more-href="/songs/"', song_page)
            crumb = song_page.split('<div class="songs-breadcrumb"', 1)[1].split("</div>", 1)[0]
            self.assertIn('class="songs-breadcrumb-root" href="/songs/"', crumb)
            self.assertIn('href="/songs/?sound=', crumb)
            for name in ("Songs", "歌曲"):
                self.assertIn(name, crumb)
            # Under the title: the singer, the mood chips (links to /songs/?mood=) and, for 月下煮茶, the badge.
            self.assertRegex(song_page, '<span class="song-singer"[^>]*>椅子樂團</span>')
            self.assertIn('href="/songs/?mood=melancholy"', song_page)
            tea_page = (output / "songs/月下煮茶/index.html").read_text(encoding="utf-8")
            self.assertIn('class="song-dialect-badge"', tea_page)
            self.assertNotIn('class="song-dialect-badge"', song_page)
            # A song with versions shows each version's own singer inside its tab.
            versions_page = (output / "songs/世界第一等/index.html").read_text(encoding="utf-8")
            self.assertRegex(versions_page, '<span class="song-singer"[^>]*>劉德華</span>')
            self.assertRegex(versions_page, '<span class="song-singer"[^>]*>伍佰</span>')
            for label in ("Search songs…", "搜尋歌曲…", "搜索歌曲…", "查看全部 {n} 筆結果", "查看全部 {n} 条结果"):
                self.assertIn(label, song_page)
            for script in ("web-site-search-variants", "web-search-box", "web-song-search"):
                self.assertIn(f'/shared/{script}.js', song_page)
            # /songs/ has the same bar with just "Songs", and its box drives the page's filter. The
            # The main header has the site-wide search, never a second song-search box.
            for folder in ("", "zh-hant/", "zh-hans/"):
                index_page = (output / folder / "songs/index.html").read_text(encoding="utf-8")
                self.assertEqual(index_page.count('class="songs-subheader"'), 1)
                self.assertIn('class="songs-breadcrumb-current" aria-current="page"', index_page)
                self.assertNotIn("songs-breadcrumb-root", index_page)
                self.assertNotIn("songSearchInput", index_page)
                header = index_page.split("</header>", 1)[0]
                self.assertEqual(header.count('class="site-header-search"'), 3)
                self.assertNotIn("songSearchInput", header)
            for other in ("about/index.html", "learn/spelling/index.html", "search/index.html"):
                self.assertNotIn("songs-subheader", (output / other).read_text(encoding="utf-8"), other)
            songs = (output / "songs/index.html").read_text(encoding="utf-8")
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
