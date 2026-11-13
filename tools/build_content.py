"""Render authored English and Chinese content into the Pages artifact."""

from __future__ import annotations

import html
import json
import re
import shutil
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

from song_title_readings import song_lomari, song_sort_reading, song_title
from tangliengim_collation import reading_sort_key
from import_wordpress import ImportedHTML, source_key
from site_languages import LANGUAGES, LANGUAGE_NAMES, PREFIXES, base_route, language_for_route, language_url, text
from site_search import document as search_document, hanri_fold_map, lyric_lines
from simplified_lookup import simplified_headword
from story_presentations import EGG_ROUTE, egg_presentation, simplified_egg, soundcloud_source
from lyric_timing import decorate_lyrics
from image_descriptions import describe_images
from page_meta import description as page_description, meta_tags

# Header, in order: a (label, destinations) pair is a dropdown; an (href, label) pair is a link.
NAV_GROUPS = (
    ("Learn", (("/learn/introduction/", "Introduction"), ("/learn/spelling/", "Spelling"), ("/learn/tone-sandhi/", "Tone sandhi"), ("/learn/romanisation/", "Romanisation"))),
    ("/songs/", "Songs"),
    ("/read/", "Read"),
    ("Tools", (("/dictionary/", "Dictionary"), ("/ime/", "Hokkien IME"), ("/translate/", "Translator"))),
)
NAV = (("/about/", "About"), ("/search/", "Search"))
IME_SCRIPTS = ('<script src="/shared/web-hangul-ime.js" defer></script>'
               '<script src="/shared/web-ime-core.js" defer></script>')
LYRIC_SCRIPTS = ('<script src="/shared/web-lyric-player.js" defer></script>'
                 '<script src="/shared/web-lyric-sync.js" defer></script>')
TITLE_READING = re.compile(r'class="[^"]*\btitle-reading\b[^"]*"[^>]*>(.*?)</(?:h1|h2|a|span)>', re.S)
HANGUL = re.compile(r"[\u1100-\u11ff\u3130-\u318f\ua960-\ua97f\uac00-\ud7a3\ud7b0-\ud7ff]")
SONG_FILTER_TEXT = {
    "en": {"placeholder": "Filter songs by Hanri, Hangul or Lomari", "categories": "Song categories", "all": "All",
           "empty": "No songs match.", "count": "{n} songs"},
    "zh-Hant": {"placeholder": "以漢字、諺文或羅馬字篩選歌曲", "categories": "歌曲分類", "all": "全部",
                "empty": "沒有符合的歌曲。", "count": "{n} 首歌曲"},
    "zh-Hans": {"placeholder": "以汉字、谚文或罗马字筛选歌曲", "categories": "歌曲分类", "all": "全部",
                "empty": "没有符合的歌曲。", "count": "{n} 首歌曲"},
}
# Tools that open only for invited visitors behind a password (audit A4).
INVITE_ONLY = frozenset({"/dictionary/", "/translate/"})


def invite_only_note(href, language):
    if href not in INVITE_ONLY:
        return ""
    return f' <span class="invite-only-note">{html.escape(text("Invite only", language))}</span>'

# Keep nasal words and stacked marks in one shaping run and one Latin font.
# Restrict this to text nodes; URLs, attributes and authored source stay intact.
NASAL_WORD = re.compile(r'[A-Za-z\u00c0-\u02ff\u1e00-\u1eff\u25cc][A-Za-z\u00c0-\u02ff\u1e00-\u1eff\u0300-\u036f]*')


def nasal_font_text(value):
    def word(match):
        value = match.group()
        if '\u0330' not in unicodedata.normalize('NFD', value):
            return value
        return '<span class="nasal-grapheme">' + unicodedata.normalize('NFC', value) + '</span>'
    return NASAL_WORD.sub(word, value)


def song_script_heading(body):
    return re.sub(
        r'<h([23])\b[^>]*>\s*漢諺混寫\s+Hanri-Hangul mixed script\s*</h\1>',
        '<h3 class="wp-block-heading song-script-heading" data-site-text="Hanri-Hangul mixed script">Hanri-Hangul mixed script</h3>',
        body,
    )


SONG_FOOTNOTE = re.compile(r"\(中\)\s*((?:(?!\(en\)|</td>).)*?)\s*<br\s*/?>\s*\(en\)\s*((?:(?!</td>).)*?)(\s*</td>)", re.S)


def simplified_markup(markup):
    return "".join(part if part.startswith("<") else (simplified_headword(part) or part)
                   for part in re.split(r"(<[^>]+>)", markup))


def split_song_notes(body):
    """Footnotes are written "(中) ... (en) ..."; each language's page shows only its own."""
    return SONG_FOOTNOTE.sub(lambda match: (
        f'<span data-content-lang="zh-Hant">{match[1]}</span>'
        f'<span data-content-lang="zh-Hans">{simplified_markup(match[1])}</span>'
        f'<span data-content-lang="en">{match[2]}</span>{match[3]}'), body)


def song_version(record):
    value = record.get("songVersion")
    return value if isinstance(value, dict) else {}


def song_version_tabs(versions):
    if len(versions) == 1:
        return versions[0][1]
    buttons, panels = [], []
    for index, (record, body) in enumerate(versions):
        version = song_version(record)
        key = re.sub(r"[^a-z0-9_-]+", "-", str(version.get("key") or index + 1).lower()).strip("-")
        tab_id = f"song-version-tab-{key}"
        panel_id = f"song-version-panel-{key}"
        label = str(version.get("label") or f"Version {index + 1}")
        selected = index == 0
        buttons.append(
            f'<button type="button" role="tab" id="{tab_id}" aria-controls="{panel_id}" '
            f'aria-selected="{str(selected).lower()}" tabindex="{0 if selected else -1}" '
            f'data-song-version-key="{html.escape(key, quote=True)}" data-site-text="{html.escape(label, quote=True)}">'
            f'{html.escape(label)}</button>'
        )
        panels.append(
            f'<section class="song-version-panel" role="tabpanel" id="{panel_id}" '
            f'aria-labelledby="{tab_id}"{"" if selected else " hidden"}>{body}</section>'
        )
    return (
        '<div class="song-version-tabs" data-song-version-tabs>'
        f'<div class="song-version-tablist" role="tablist" aria-label="Song versions">{"".join(buttons)}</div>'
        f'{"".join(panels)}</div>'
    )


def site_brand(root, language="en"):
    template = (root / "shared/site-brand.html").read_text(encoding="utf-8")
    return template.replace("__HOME__", PREFIXES[language] + "/").strip()


def navigation_links(route, language=None, variants=True):
    language = language or language_for_route(route)

    def link(href, label):
        destination = language_url(href, language) or language_url(href, "zh-Hant")
        current = ' aria-current="page"' if base_route(route) == href or href != "/" and base_route(route).startswith(href) else ""
        if href == "/search/":
            accessible_label = html.escape(text(label, language), quote=True)
            return (
                f'<a class="site-search-link" href="{html.escape(destination, quote=True)}" '
                f'title="{accessible_label}" aria-label="{accessible_label}"{current}>'
                '<span class="site-search-icon" aria-hidden="true"></span>'
                f'<span class="visually-hidden">{accessible_label}</span></a>'
            )
        return f'<a href="{html.escape(destination, quote=True)}"{current}>{html.escape(text(label, language))}{invite_only_note(href, language)}</a>'

    items = []
    current_route = base_route(route)
    for label, destinations in NAV_GROUPS:
        if isinstance(destinations, str):  # a top-level link: (href, label)
            items.append(link(label, destinations))
            continue
        active = " is-current" if any(
            current_route == path or current_route.startswith(path) for path, _title in destinations
        ) else ""
        children = "".join(link(path, title) for path, title in destinations)
        items.append(
            '<details class="site-nav-dropdown" name="site-navigation">'
            f'<summary class="site-nav-trigger{active}">{text(label, language)}</summary>'
            f'<div class="site-nav-panel">{children}</div></details>'
        )
    items.extend(link(href, label) for href, label in NAV)
    choices = []
    for code in LANGUAGES:
        destination = language_url(route, code)
        if destination is not None:
            current = ' aria-current="page"' if code == language else ""
            choices.append(f'<a href="{html.escape(destination, quote=True)}" lang="{code}" hreflang="{code}" data-language-choice="{code}"{current}>{LANGUAGE_NAMES[code]}</a>')
    language_title = {"en": "Language", "zh-Hant": "語言", "zh-Hans": "语言"}[language]
    items.append('<details class="site-nav-dropdown site-language-dropdown" name="site-navigation">'
                 f'<summary class="site-nav-trigger" title="{language_title}"><span class="site-language-icon" aria-hidden="true"></span>{LANGUAGE_NAMES[language]}</summary>'
                 f'<div class="site-nav-panel">{"".join(choices)}</div></details>')
    if variants:
        for code in LANGUAGES:
            if code != language:
                items.append(f'<template data-navigation-language="{code}">{navigation_links(route, code, variants=False)}</template>')
    return "".join(items)


LISTEN_LABEL = {"en": "Listen", "zh-Hant": "聆聽", "zh-Hans": "收听"}
_runtime_entries = {}


def listen_button(root, language, hanri, reading):
    """A play button carrying the dictionary's audio clips for one exact entry.

    Embedding the clip list means the homepage plays a word without downloading
    the whole dictionary. Without built data or a matching entry there is no button.
    """
    path = Path(root) / "public/data/hokkien-hanri-dict.json"
    if path not in _runtime_entries:
        _runtime_entries[path] = json.loads(path.read_text(encoding="utf-8"))["entries"] if path.is_file() else []
    for entry in _runtime_entries[path]:
        segments = (entry.get("audio") or {}).get("segments") or []
        if entry.get("hanri") == hanri and entry.get("reading") == reading and segments:
            return play_button(language, segments)
    return ""


def play_button(language, segments):
    clips = html.escape(json.dumps(segments, ensure_ascii=False, separators=(",", ":")), quote=True)
    return (f'<button type="button" class="tli-listen" data-tli-audio="{clips}">'
            f'<span class="tli-listen-icon" aria-hidden="true"></span><span>{LISTEN_LABEL[language]}</span></button>')


# The one real Korean word on the site, for comparison with Hokkien. Recorded by a Korean
# speaker; it never goes through the Hokkien audio planner.
KOREAN_CLIP = [{"file": "/assets/audio/ko-haksaeng.mp3", "trimStart": False, "trimEnd": False, "speed": 1,
                "shortOverlapFinal": False, "englishClusterHelper": False}]
KOREAN_CLIP_SOURCE = "https://commons.wikimedia.org/wiki/File:Ko-%ED%95%99%EC%83%9D.ogg"
KOREAN_CLIP_LICENCE = "https://creativecommons.org/licenses/by-sa/4.0/"
KOREAN_CLIP_LABEL = {"en": "Audio", "zh-Hant": "錄音", "zh-Hans": "录音"}


def korean_clip_credit(language):
    separator = ": " if language == "en" else "："
    comma = ", " if language == "en" else "，"
    return (f'<p class="home-compare-credit">{KOREAN_CLIP_LABEL[language]}{separator}'
            f'<a href="{KOREAN_CLIP_SOURCE}">HappyMidnight</a>{comma}'
            f'<a href="{KOREAN_CLIP_LICENCE}">CC BY-SA 4.0</a></p>')


def home_launch(language, listen=""):
    labels = {
        "en": (
            "Learn TLI", "Understand the script, spelling, and tone sandhi.", "Start with the introduction",
            "Read Hokkien", "Stories and literature with pronunciation kept close to the text.", "Browse reading",
            "Hear the language", "Songs with Hangul readings and Lomari.", "Explore songs", "Writing tools", "sound",
        ),
        "zh-Hant": (
            "學習東寧音", "了解文字、拼寫與變調。", "從使用說明開始",
            "閱讀閩南語", "讓故事與文學的讀音緊貼原文。", "瀏覽讀物",
            "收聽閩南歌曲", "附有諺文讀音與羅馬字的歌曲。", "探索歌曲", "書寫工具", "聲音",
        ),
        "zh-Hans": (
            "学习东宁音", "了解文字、拼写与变调。", "从使用说明开始",
            "阅读闽南语", "让故事与文学的读音紧贴原文。", "浏览读物",
            "收听闽南歌曲", "附有谚文读音与罗马字的歌曲。", "探索歌曲", "书写工具", "声音",
        ),
    }
    learn, learn_note, learn_link, read, read_note, read_link, hear, hear_note, hear_link, tools, student = labels[language]

    def destination(path, label, class_name=""):
        url = language_url(path, language) or language_url(path, "zh-Hant")
        class_attr = f' class="{class_name}"' if class_name else ""
        return f'<a{class_attr} href="{html.escape(url, quote=True)}"><span>{html.escape(label)}{invite_only_note(path, language)}</span><span aria-hidden="true">&#8594;</span></a>'

    paths = (
        ("01", learn, learn_note, "/learn/introduction/", learn_link),
        ("02", read, read_note, "/read/", read_link),
        ("03", hear, hear_note, "/songs/", hear_link),
    )
    path_html = "".join(
        '<article class="home-path">'
        f'<span class="home-path-number">{number}</span><h2>{html.escape(title)}</h2>'
        f'<p>{html.escape(note)}</p>{destination(path, label)}</article>'
        for number, title, note, path, label in paths
    )
    specimen_meaning = f'<span class="home-specimen-meaning">{html.escape(student)}</span>' if language == "en" else ""
    return (
        '<section class="home-launch">'
        '<aside class="home-specimen" aria-label="Tangliengim writing specimen">'
        '<ruby><span lang="zh-Hant">聲音</span><rt lang="nan-Hang">샬ˉ임ˆ</rt></ruby>'
        f'<span class="home-specimen-lomari">siā̰-îm</span>'
        f'{specimen_meaning}{listen}</aside>'
        f'<div class="home-paths">{path_html}</div>'
        f'<div class="home-tools"><h2>{html.escape(tools)}</h2><div>{destination("/ime/", text("Open IME", language))}{destination("/dictionary/", text("Dictionary", language))}</div></div>'
        '</section>'
    )


def home_showcase(language, song_records=()):
    labels = {
        "en": {
            "label": "Explore TheHokkienLang",
            "tone_meta": "Listen closely",
            "tone_title": "Guide to Hokkien tone sandhi",
            "tone_copy": "Follow the sound changes that give a Hokkien phrase its rhythm, and see how TLI records what is heard.",
            "tone_link": "Read the tone-sandhi guide",
            "read_meta": "Read",
            "read_title": "Literature works",
            "read_copy": "Meet Hokkien on the page through short fiction and dramatic literature, with pronunciation kept close to the text.",
            "egg_kind": "Short story",
            "egg_title": "The Egg",
            "egg_note": "A philosophical story presented in Hokkien.",
            "mirror_kind": "Classical literature",
            "mirror_title": "Tale of the Lychee Mirror",
            "mirror_note": "A Hokkien dramatic tradition in a reading edition.",
            "songs_meta": "Hear",
            "songs_title": "Songs",
            "songs_copy": "From timeless classics to newer voices, explore lyrics with Hanri-Hangul readings and Lomari.",
            "songs_link": "Browse the songbook",
            "selection": "From the songbook",
        },
        "zh-Hant": {
            "label": "探索 TheHokkienLang",
            "tone_meta": "細聽",
            "tone_title": "閩南語變調解析",
            "tone_copy": "了解變調如何構成閩南語詞句的節奏，以及東寧音如何記錄實際讀音。",
            "tone_link": "閱讀變調指南",
            "read_meta": "閱讀",
            "read_title": "文學讀物",
            "read_copy": "透過短篇小說與戲曲文學閱讀閩南語，讓讀音緊貼原文。",
            "egg_kind": "短篇小說",
            "egg_title": "《卵》",
            "egg_note": "以閩南語呈現的哲思故事。",
            "mirror_kind": "古典文學",
            "mirror_title": "《荔鏡記》",
            "mirror_note": "閩南戲曲傳統的閱讀版本。",
            "songs_meta": "聆聽",
            "songs_title": "歌曲",
            "songs_copy": "從歷久不衰的經典到新世代聲音，閱讀附有漢諺讀音與羅馬字的歌詞。",
            "songs_link": "瀏覽歌單",
            "selection": "歌單精選",
        },
        "zh-Hans": {
            "label": "探索 TheHokkienLang",
            "tone_meta": "细听",
            "tone_title": "闽南语变调解析",
            "tone_copy": "了解变调如何构成闽南语词句的节奏，以及东宁音如何记录实际读音。",
            "tone_link": "阅读变调指南",
            "read_meta": "阅读",
            "read_title": "文学读物",
            "read_copy": "通过短篇小说与戏曲文学阅读闽南语，让读音紧贴原文。",
            "egg_kind": "短篇小说",
            "egg_title": "《卵》",
            "egg_note": "以闽南语呈现的哲思故事。",
            "mirror_kind": "古典文学",
            "mirror_title": "《荔镜记》",
            "mirror_note": "闽南戏曲传统的阅读版本。",
            "songs_meta": "聆听",
            "songs_title": "歌曲",
            "songs_copy": "从历久不衰的经典到新世代声音，阅读附有汉谚读音与罗马字的歌词。",
            "songs_link": "浏览歌单",
            "selection": "歌单精选",
        },
    }[language]

    def link(path, label, class_name="home-feature-link"):
        destination = language_url(path, language) or language_url(path, "zh-Hant")
        return (
            f'<a class="{class_name}" href="{html.escape(destination, quote=True)}">'
            f'<span>{html.escape(label)}</span><span aria-hidden="true">&#8594;</span></a>'
        )

    literature = (
        '<div class="home-literature-grid">'
        f'<a class="home-literature-work" href="{html.escape(language_url("/read/stories/the-egg/", language) or language_url("/read/stories/the-egg/", "zh-Hant"), quote=True)}">'
        '<img src="/assets/content/wordpress/a544aeacfa20-the-egg.png" alt="">'
        f'<span class="home-work-kind">{html.escape(labels["egg_kind"])}</span>'
        f'<h3><ruby>卵<rt>능ˉ</rt></ruby> <span>{html.escape(labels["egg_title"])}</span></h3>'
        f'<p>{html.escape(labels["egg_note"])}</p></a>'
        '</div>'
    )
    eligible_songs = [record for record in song_records if base_route(record["route"]) != "/songs/月下煮茶/"]
    song_links = [
        f'<a href="{html.escape(language_url(record["route"], language) or record["route"], quote=True)}">'
        f'<span class="title-reading home-song-title">{song_title(record)[0]}</span><small>{html.escape(song_lomari(record))}</small></a>'
        for record in eligible_songs
    ]
    songs = (
        '<div class="home-songbook">'
        f'<span class="home-songbook-label">{html.escape(labels["selection"])}</span>'
        f'<div data-home-song-picks>{"".join(song_links[:3])}</div>'
        f'<template data-home-song-pool>{"".join(song_links)}</template>'
        '</div>'
    )
    return (
        f'<section class="home-showcase" aria-label="{html.escape(labels["label"], quote=True)}">'
        '<div class="home-feature-pair">'
        '<article class="home-feature home-feature-tone">'
        f'<span class="home-feature-meta">{html.escape(labels["tone_meta"])}</span>'
        f'<h2>{html.escape(labels["tone_title"])}</h2><p>{html.escape(labels["tone_copy"])}</p>'
        f'{link("/learn/tone-sandhi/", labels["tone_link"])}</article></div>'
        '<section class="home-feature home-feature-literature">'
        '<div class="home-feature-heading">'
        f'<span class="home-feature-meta">{html.escape(labels["read_meta"])}</span>'
        f'<h2>{html.escape(labels["read_title"])}</h2><p>{html.escape(labels["read_copy"])}</p></div>{literature}</section>'
        '<section class="home-feature home-feature-songs"><div class="home-feature-heading">'
        f'<span class="home-feature-meta">{html.escape(labels["songs_meta"])}</span>'
        f'<h2>{html.escape(labels["songs_title"])}</h2><p>{html.escape(labels["songs_copy"])}</p>'
        f'{link("/songs/", labels["songs_link"])}</div>{songs}</section></section>'
    )


SAME_BLOCKS = re.compile(
    r'\s*<h3\b[^>]*>(?P<title>.*?)</h3>\s*<p\b[^>]*>(?P<lead>.*?)</p>\s*'
    r'<ul\b[^>]*>\s*<li\b[^>]*>(?P<first>.*?)</li>\s*<li\b[^>]*>(?P<second>.*?)</li>\s*</ul>\s*'
    r'<p\b[^>]*>(?P<note>.*?)</p>', re.S)


def home_compare_card(item, class_name, listen=""):
    """One side of the comparison, from a list item such as: Label: <strong>word</strong> (<em>lomari</em>)."""
    label, _, sample = re.match(r"\s*(.*?)\s*([:：])\s*(.*)$", item, re.S).groups()
    word = re.sub(r"</?span\b[^>]*>", "", re.search(r"<strong>(.*?)</strong>", sample, re.S).group(1))
    lomari = re.search(r"<em>(.*?)</em>", sample, re.S).group(1)
    return (f'<div class="home-compare-card {class_name}"><h3>{label}</h3>'
            f'<div class="home-compare-word">{word}</div>'
            f'<p class="home-compare-lomari">{lomari}</p>{listen}</div>')


def home_compare(section, language, listen=""):
    """The "same blocks, different sounds" explanation as two side-by-side cards, in the page's own words."""
    korean = play_button(language, KOREAN_CLIP) + korean_clip_credit(language)
    return (
        '<section class="home-compare"><div class="home-compare-heading">'
        f'<h2>{section["title"]}</h2><p>{section["lead"]}</p></div>'
        '<div class="home-compare-cards">'
        f'{home_compare_card(section["first"], "home-compare-korean", korean)}'
        f'{home_compare_card(section["second"], "home-compare-hokkien", listen)}'
        f'</div><p class="home-compare-note">{section["note"]}</p></section>'
    )


def curate_home_body(body, language, song_records=(), listen=""):
    marker = {"en": "Learn TLI", "zh-Hant": "學習東寧音", "zh-Hans": "学习东宁音"}[language]
    marker_position = body.find(marker)
    if marker_position == -1:
        raise ValueError(f"Homepage feature marker is missing for {language}: {marker}")
    feature_start = body.rfind("<h2", 0, marker_position)
    if feature_start == -1:
        raise ValueError(f"Homepage feature heading is missing for {language}: {marker}")
    introduction = body[:feature_start]
    introduction = re.sub(
        r'(?:\s*<div[^>]*style="[^"]*margin-bottom[^"]*"[^>]*></div>|\s*<hr[^>]*>)+\s*$',
        '',
        introduction,
        flags=re.IGNORECASE,
    )
    # What to explore comes first; the longer "Why TLI?" essay follows it.
    section = SAME_BLOCKS.search(introduction)
    compare = home_compare(section, language, listen) if section else ""
    if section:
        introduction = introduction[:section.start()] + introduction[section.end():]
    return compare + home_showcase(language, song_records) + f'<div class="home-essay">{introduction.rstrip()}</div>'


LEADING_LANGUAGE_SWITCHER = re.compile(
    r'\s*<div class="wp-block-buttons[^"]*">\s*'
    r'(?:<div class="wp-block-button[^"]*">.*?</div>\s*)+</div>\s*',
    re.DOTALL,
)


def remove_leading_language_switcher(body):
    class LanguageLinks(HTMLParser):
        def __init__(self):
            super().__init__()
            self.labels = []
            self.in_link = False

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                self.labels.append("")
                self.in_link = True

        def handle_data(self, data):
            if self.in_link:
                self.labels[-1] += data

        def handle_endtag(self, tag):
            if tag == "a":
                self.in_link = False

    def remove_group(match):
        links = LanguageLinks()
        links.feed(match.group(0))
        language_labels = {"English", "繁體中文", "简体中文", "簡體中文", "中文（繁）", "中文（简）"}
        if links.labels and all(label.strip() in language_labels for label in links.labels):
            return ""
        return match.group(0)

    return LEADING_LANGUAGE_SWITCHER.sub(remove_group, body)


def introduce_tli(text):
    before, name, after = text.partition("Tangliengim")
    if not name:
        return text
    return before + "Tangliengim (TLI)" + after.replace("Tangliengim", "TLI")


def search_page(language):
    labels = {
        "en": {
            "label": "Search the website",
            "keyboard": "Enable Hangul keyboard",
            "placeholder": "Search pages, songs, and stories...",
            "clear": "Clear search",
            "candidates": "Hanri candidates",
            "filters": "Filter search results",
            "results": "Search results",
            "pages": "Search result pages",
            "noscript": "JavaScript is required for website search.",
        },
        "zh-Hant": {
            "label": "搜尋網站",
            "keyboard": "啟用諺文鍵盤",
            "placeholder": "搜尋頁面、歌曲與故事…",
            "clear": "清除搜尋",
            "candidates": "漢字候選詞",
            "filters": "篩選搜尋結果",
            "results": "搜尋結果",
            "pages": "搜尋結果頁面",
            "noscript": "網站搜尋需要啟用 JavaScript。",
        },
        "zh-Hans": {
            "label": "搜索网站",
            "keyboard": "启用谚文键盘",
            "placeholder": "搜索页面、歌曲与故事…",
            "clear": "清除搜索",
            "candidates": "汉字候选词",
            "filters": "筛选搜索结果",
            "results": "搜索结果",
            "pages": "搜索结果页面",
            "noscript": "网站搜索需要启用 JavaScript。",
        },
    }[language]
    return (
        '<section class="site-search">'
        '<form id="siteSearchForm" class="site-search-form" role="search">'
        '<div class="site-search-heading">'
        f'<label for="siteSearchInput">{html.escape(labels["label"])}</label>'
        '<button id="hangulKeyboardToggle" class="hangul-keyboard-toggle" type="button" aria-pressed="false">'
        f'<span class="toggle-label">{html.escape(labels["keyboard"])}</span>'
        '<span class="toggle-switch" aria-hidden="true"><span class="toggle-knob"></span></span>'
        '</button></div>'
        '<div class="site-search-input-wrap">'
        f'<input id="siteSearchInput" class="site-search-input" type="text" inputmode="search" enterkeyhint="search" autocomplete="off" autocapitalize="off" spellcheck="false" '
        f'placeholder="{html.escape(labels["placeholder"], quote=True)}">'
        f'<button id="siteSearchClear" class="site-search-clear" type="button" '
        f'aria-label="{html.escape(labels["clear"], quote=True)}" hidden>&times;</button>'
        f'<div id="siteSearchCandidates" class="hanri-candidate-menu" role="listbox" '
        f'aria-label="{html.escape(labels["candidates"], quote=True)}" hidden></div></div>'
        f'<div id="siteSearchFilters" class="site-search-filters" role="group" '
        f'aria-label="{html.escape(labels["filters"], quote=True)}"></div></form>'
        '<p id="siteSearchSummary" class="site-search-summary" aria-live="polite"></p>'
        f'<section id="siteSearchResults" class="site-search-results" '
        f'aria-label="{html.escape(labels["results"], quote=True)}"></section>'
        f'<nav id="siteSearchPagination" class="site-search-pagination" '
        f'aria-label="{html.escape(labels["pages"], quote=True)}" hidden></nav>'
        f'<noscript><p>{html.escape(labels["noscript"])}</p></noscript></section>'
    )


def document(root, title, route, body, content_type="index", source_url=None, heading_html=None):
    language = language_for_route(route)
    navigation = navigation_links(route)
    home_headings = {"en": "A written voice for Hokkien.", "zh-Hant": "記錄著屬於閩南語的聲音。", "zh-Hans": "记录着属于闽南语的声音。"}
    home_heading_markup = {
        "en": html.escape(home_headings["en"]),
        "zh-Hant": '<span class="home-heading-segment">記錄著屬於</span><wbr><span class="home-heading-segment">閩南語的聲音。</span>',
        "zh-Hans": '<span class="home-heading-segment">记录着属于</span><wbr><span class="home-heading-segment">闽南语的声音。</span>',
    }
    home_introductions = {
        "en": "Tangliengim (TLI) brings pronunciation, tone, and meaning into one readable system.",
        "zh-Hant": "將發音、聲調和語意融為一體的東寧音（TLI）：一看就懂、一讀就通。",
        "zh-Hans": "将发音、声调和语意融为一体的东宁音（TLI）：一看就懂、一读就通。",
    }
    home_kickers = {"en": "Hokkien language · writing · culture", "zh-Hant": "閩南語 · 文字 · 文化", "zh-Hans": "闽南语 · 文字 · 文化"}
    heading = home_headings[language] if base_route(route) == "/" else title
    if language == "en" and base_route(route) != "/" and heading_html is None:
        heading = introduce_tli(heading)
    introduction = f'<p class="site-introduction">{home_introductions[language]}</p>' if base_route(route) == "/" else ""
    eyebrow = f'<p class="home-kicker">{home_kickers[language]}</p>' if base_route(route) == "/" else ""
    alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="https://thehokkienlang.github.io{html.escape(destination, quote=True)}">' for code in LANGUAGES if (destination := language_url(route, code)) is not None)
    # A ?lang= address is the same page with a translated interface, and its canonical is
    # the English URL, so it is not an alternate version for search engines.
    if any("?" in (language_url(route, code) or "") for code in LANGUAGES):
        alternates = ""
    template = (root / "apps/content-site/page.html").read_text(encoding="utf-8")
    section = base_route(route).strip("/").split("/")[0] or "home"
    is_search = base_route(route) == "/search/"
    heading_markup = (heading_html if heading_html is not None else
                      home_heading_markup[language] if base_route(route) == "/" else html.escape(heading))
    values = {"LANG": language, "HOME": PREFIXES[language] + "/", "SKIP": text("Skip to content", language), "ALTERNATES": alternates, "TITLE": html.escape(title), "HEADING": heading_markup, "INTRODUCTION": introduction, "EYEBROW": eyebrow, "ROUTE": html.escape(route, quote=True), "NAV": navigation, "BODY": body, "TYPE": content_type, "SECTION": html.escape(section), "LAUNCH": home_launch(language, listen_button(root, language, "聲音", "샬5임1")) if section == "home" else "", "PAGESTYLES": '<link rel="stylesheet" href="/shared/web-ime-menu.css"><link rel="stylesheet" href="/assets/search/styles.css">' if is_search else "", "PAGESCRIPTS": '<script src="/shared/web-site-search-variants.js" defer></script><script src="/assets/search/search.js" defer></script>' if is_search else ('<script src="/shared/web-audio-player.js" defer></script>' if section == "home" else "")}
    # Audit A5: each page loads only the scripts it uses. The IME scripts draw tone marks in
    # Hangul titles (site.js) and run the search box; the lyric scripts run on song pages.
    launch = values["LAUNCH"]
    needs_ime = is_search or bool(HANGUL.search(values["HEADING"])) or any(
        HANGUL.search(match) for match in TITLE_READING.findall(body + launch))
    values["IMESCRIPTS"] = IME_SCRIPTS if needs_ime else ""
    values["LYRICSCRIPTS"] = LYRIC_SCRIPTS if content_type == "songs" else ""
    values["BRAND"] = site_brand(root, language)
    values["META"] = meta_tags(title, route, page_description(
        title, base_route(route), body, content_type, language, home_introductions[language]), language)
    # One pass prevents source content resembling a placeholder from becoming executable template markup.
    return re.sub(r"__([A-Z]+)__", lambda match: values[match[1]], template)


def build_content(root: Path, output: Path):
    content = root / "content"
    if not content.exists():
        return []
    # Keep archived sources in the repository, but never publish their routes.
    unpublished_routes = {"/songs/translation-notes/", "/read/literature/lychee-mirror/"}
    manifest = json.loads((root / "migration/wordpress-map.json").read_text(encoding="utf-8"))
    records = [
        json.loads((root / item["file"]).read_text(encoding="utf-8"))
        for item in manifest["records"]
        if base_route(item["route"]) not in unpublished_routes
    ]
    manifest_files = {item["file"] for item in manifest["records"]}
    for path in sorted((root / "content/songs").glob("*.json")):
        relative = path.relative_to(root).as_posix()
        if relative in manifest_files:
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        version = song_version(record)
        if record.get("type") == "songs" and version.get("groupRoute"):
            records.append(record)
    versions_by_route = {}
    for item in records:
        version = song_version(item)
        if version.get("groupRoute"):
            versions_by_route.setdefault(version["groupRoute"], []).append(item)
    for values in versions_by_route.values():
        values.sort(key=lambda item: (song_version(item).get("order", 0), item["route"]))
    source_routes = {source_key(item["sourceUrl"]): item["route"] for item in records}
    traditional_egg = next(item for item in records if item['route'] == '/zh-hant' + EGG_ROUTE)
    egg_player = soundcloud_source(traditional_egg['body'])
    records.append(simplified_egg(traditional_egg))
    # After every record exists, so derived pages such as the simplified Egg are published too.
    published_records = [
        item for item in records
        if not song_version(item) or item["route"] == song_version(item).get("groupRoute")
    ]
    media = json.loads((root / "migration/wordpress-media.json").read_text(encoding="utf-8"))

    class PresentationHTML(ImportedHTML):
        def __init__(self, record):
            super().__init__(record["sourceUrl"], source_routes, media, root, False)
            self.language = record["language"]
            self.tli_introduced = self.language != "en" or "Tangliengim" in record["title"] or base_route(record["route"]) == "/"
            # The About page explains the name itself and introduces TLI by hand.
            self.keeps_full_name = base_route(record["route"]) == "/about/"

        def rewrite(self, value, media=False):
            # Generated index pages are not imported records, so the importer would send them to WordPress.
            if not media and value and value.startswith("/") and base_route(value) in ("/songs/", "/read/"):
                return value
            result = super().rewrite(value, media)
            if not media and self.language != "en" and result and result.startswith(("/songs/", "/dictionary/", "/ime/", "/read/literature/")) and "?" not in result:
                path, marker, fragment = result.partition("#")
                result = (language_url(path, self.language) or path) + (marker + fragment if marker else "")
            return result

        def handle_data(self, data):
            data = re.sub(r"(?<!The)\bHokkienLang\b", "TheHokkienLang", data)
            if self.language == "en" and "Tangliengim" in data and not self.keeps_full_name:
                if self.tli_introduced:
                    data = data.replace("Tangliengim", "TLI")
                else:
                    data = introduce_tli(data)
                    self.tli_introduced = True
            super().handle_data(nasal_font_text(data))

    paths = set()
    search_documents = {language: [] for language in LANGUAGES}
    search_kinds = {"guides": "guide", "songs": "song", "stories": "story"}
    for record in published_records:
        route = record["route"]
        target = output / route.lstrip("/") / "index.html"
        if not route.startswith("/") or not route.endswith("/") or not target.resolve().is_relative_to(output.resolve()) or route in paths:
            raise ValueError(f"Invalid or duplicate content route: {route}")
        paths.add(route)
        target.parent.mkdir(parents=True, exist_ok=True)
        if base_route(route) == EGG_ROUTE:
            heading_html, body = egg_presentation(record, egg_player)
        elif record["type"] == "songs" and route in versions_by_route:
            heading_html, _ = song_title(record)
            rendered_versions = []
            for version_record in versions_by_route[route]:
                _, version_body = song_title(version_record)
                version_body = split_song_notes(song_script_heading(version_body))
                version_body = PresentationHTML(version_record).render(remove_leading_language_switcher(version_body))
                version_body = decorate_lyrics(root, version_record, version_body)
                rendered_versions.append((version_record, version_body))
            body = song_version_tabs(rendered_versions)
        else:
            heading_html, body = song_title(record) if record["type"] == "songs" else (None, record["body"])
        if record["type"] == "songs" and route not in versions_by_route:
            body = split_song_notes(song_script_heading(body))
        if not (record["type"] == "songs" and route in versions_by_route):
            body = PresentationHTML(record).render(remove_leading_language_switcher(body))
        if record['type'] == 'songs' and route not in versions_by_route:
            body = decorate_lyrics(root, record, body)
        if base_route(route) == "/":
            body = curate_home_body(body, record["language"], [item for item in published_records if item["type"] == "songs"],
                                    listen_button(root, record["language"], "學生", "학솅1"))
        body = describe_images(body, record["language"])
        target.write_text(document(root, record["title"], route, body, record["type"], record["sourceUrl"], heading_html), encoding="utf-8")
        indexed_languages = LANGUAGES if record["type"] == "songs" else (record["language"],)
        for indexed_language in indexed_languages:
            destination = language_url(route, indexed_language)
            if destination is None:
                continue
            title = record["title"].replace("Tangliengim", "TLI")
            if base_route(route) == EGG_ROUTE:
                title = "卵 · " + ("The Egg" if indexed_language == "en" else "蛋")
            search_documents[indexed_language].append(search_document(
                f'{indexed_language}:{record["id"]}:{base_route(route)}', title, destination,
                search_kinds.get(record["type"], "page"), heading_html or "", body,
            ))
    def listing(items):
        return '<ul class="page-list">' + "".join(f'<li><a class="title-reading" href="{html.escape(item["route"], quote=True)}">{html.escape(item["title"].replace("Tangliengim", "TLI"))}</a></li>' for item in items) + "</ul>"
    song_rows = json.loads((root / "migration/song-urls.json").read_text(encoding="utf-8"))
    song_categories = json.loads((root / "content/song-categories.json").read_text(encoding="utf-8"))
    songs_by_route = {item["route"]: item for item in published_records if item["type"] == "songs"}
    approved_routes = {row["new_url"] for row in song_rows}
    categorized_routes = [route for category in song_categories for route in category["routes"]]
    if len(categorized_routes) != len(set(categorized_routes)):
        raise ValueError("A song appears in more than one category")
    if set(categorized_routes) != approved_routes or approved_routes != set(songs_by_route):
        missing = sorted(approved_routes - set(categorized_routes))
        extra = sorted(set(categorized_routes) - approved_routes)
        raise ValueError(f"Song categories are out of sync; missing={missing}, extra={extra}")

    song_items = {}
    for route, imported in songs_by_route.items():
        label, _ = song_title(imported)
        sort_reading = song_sort_reading(imported)
        route_records = versions_by_route.get(route, [imported])
        original_title_values = list(dict.fromkeys(
            record.get("originalTitle", "").strip()
            for record in route_records
            if record.get("originalTitle", "").strip()
        ))
        original_titles = " ".join(original_title_values)
        mandarin_titles = [re.sub(r"\s+諺文(?:/中文)?歌詞\s*$", "", title) for title in original_title_values]
        mandarin_simplified_titles = list(dict.fromkeys(
            record.get("mandarinTitleSimplified", "").strip()
            or simplified_headword(re.sub(r"\s+諺文(?:/中文)?歌詞\s*$", "", record.get("originalTitle", "").strip()))
            or re.sub(r"\s+諺文(?:/中文)?歌詞\s*$", "", record.get("originalTitle", "").strip())
            for record in route_records
            if record.get("originalTitle", "").strip()
        ))
        lines = []
        seen_lines = set()
        for record in route_records:
            for line in lyric_lines(record.get("body", "")):
                identity = (line["main"], line["mainHtml"], line["lomari"], line["search"])
                if identity not in seen_lines:
                    seen_lines.add(identity)
                    lines.append(line)
        song_items[route] = {
            "label": label,
            "lomari": song_lomari(imported),
            "mandarinTitle": " / ".join(mandarin_titles),
            "mandarinSearch": " ".join([original_titles, *mandarin_simplified_titles]),
            "lines": lines,
            "sort": (not bool(sort_reading), reading_sort_key(sort_reading)),
            # Title search stays compact; structured lyric lines are indexed by the browser.
            "search": " ".join(part for part in (
                re.sub(r"<[^>]+>", " ", label), imported.get("title", ""),
                sort_reading, song_lomari(imported),
            ) if part),
        }

    def song_index(language):
        sections = []
        for category in song_categories:
            items = sorted(category["routes"], key=lambda route: (song_items[route]["sort"], route))
            links = []
            for route in items:
                destination = language_url(route, language) or route
                item = song_items[route]
                entry_class = "title-reading song-entry"
                line_data = json.dumps(
                    [[line["main"], line["lomari"], line["search"], line["mainHtml"]] for line in item["lines"]],
                    ensure_ascii=False, separators=(",", ":"),
                )
                links.append(
                    f'<li data-song-search="{html.escape(item["search"], quote=True)}" '
                    f'data-song-lines="{html.escape(line_data, quote=True)}" '
                    f'data-song-mandarin-search="{html.escape(item["mandarinSearch"], quote=True)}" '
                    f'data-song-mandarin-title="{html.escape(item["mandarinTitle"], quote=True)}">'
                    f'<a class="{entry_class}" '
                    f'href="{html.escape(destination, quote=True)}">'
                    f'<span class="song-entry-title">{item["label"]}'
                    '<small class="song-entry-mandarin-match" hidden></small></span>'
                    f'<span class="song-entry-lomari">{html.escape(item["lomari"])}</span>'
                    '<span class="song-entry-match" hidden>'
                    '<span class="song-entry-match-main"></span>'
                    '<span class="song-entry-match-lomari"></span></span>'
                    '</a></li>'
                )
            labels = category["labels"]
            title = labels.get(language, labels["en"])
            sections.append(
                '<section class="song-category" '
                f'data-song-category="{html.escape(category["id"], quote=True)}" '
                f'style="--category-accent:{html.escape(category["accent"], quote=True)};'
                f'--category-tint:{html.escape(category["tint"], quote=True)};'
                f'--category-tint-end:{html.escape(category["tintEnd"], quote=True)}">'
                '<header class="song-category-heading">'
                f'<h2>{html.escape(title)}</h2><span>{len(items):02d}</span></header>'
                f'<ol class="song-list">{"".join(links)}</ol></section>'
            )
        return song_filter(language) + '<div class="song-catalogue">' + "".join(sections) + '</div>'

    def song_filter(language):
        words = SONG_FILTER_TEXT[language]
        hanri_search_fold = json.dumps(hanri_fold_map(), ensure_ascii=False, separators=(",", ":"))
        chips = [f'<button type="button" class="song-filter-chip" data-song-filter-category="" aria-pressed="true">{words["all"]}</button>']
        for category in song_categories:
            label = category["labels"].get(language, category["labels"]["en"])
            chips.append(
                f'<button type="button" class="song-filter-chip" data-song-filter-category="{html.escape(category["id"], quote=True)}" '
                f'aria-pressed="false" style="--category-accent:{html.escape(category["accent"], quote=True)}">{html.escape(label)}</button>')
        return (
            f'<div class="song-filter" role="search" data-song-filter '
            f'data-song-hanri-fold="{html.escape(hanri_search_fold, quote=True)}" '
            f'data-count-template="{html.escape(words["count"], quote=True)}">'
            f'<input type="search" class="song-filter-input" placeholder="{words["placeholder"]}" aria-label="{words["placeholder"]}" '
            'autocomplete="off" spellcheck="false">'
            f'<div class="song-filter-chips" role="group" aria-label="{words["categories"]}">{"".join(chips)}</div>'
            '<p class="song-filter-summary" aria-live="polite"></p>'
            f'<p class="song-filter-empty" hidden>{words["empty"]}</p></div>'
        )
    sections = {}
    languages = manifest.get("languages", ["en"])
    for language in languages:
        prefix = PREFIXES[language]
        guides = [item for item in published_records if item["type"] == "guides" and item["language"] == language and base_route(item["route"]).startswith("/learn/")]
        stories = [{**item, "title": text("The Egg", language)} for item in published_records if item["type"] == "stories" and item["language"] == language]
        literature = [{**item, "route": language_url(item["route"], language), "title": text("Tale of the Lychee Mirror", language)} for item in published_records if item["type"] == "literature"]
        sections[prefix + "/learn/"] = (text("Learn Tangliengim", language), listing(guides))
        sections[prefix + "/read/"] = (text("Read in Hokkien", language), (f'<h2>{text("Literature", language)}</h2>' + listing(literature) if literature else "") + f'<h2>{text("Stories", language)}</h2>' + listing(stories))
        sections[prefix + "/songs/"] = (text("Songs", language), song_index(language))
        sections[prefix + "/search/"] = (text("Search", language), search_page(language))
    for route, (title, body) in sections.items():
        target = output / route.lstrip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document(root, title, route, body), encoding="utf-8")
        paths.add(route)
        if base_route(route) != "/search/":
            language = language_for_route(route)
            search_documents[language].append(search_document(
                f'{language}:section:{base_route(route)}', title, route, "page", "", body,
            ))
    tool_copy = {
        "en": (("Dictionary", "Search Hanri, Hangul, Lomari, and English dictionary entries."),
               ("IME Pad", "Type Hokkien with the TLI Hangul input method.")),
        "zh-Hant": (("詞典", "搜尋漢字、諺文、羅馬字與英文詞條。"),
                    ("輸入法", "使用 TLI 諺文輸入法書寫閩南語。")),
        "zh-Hans": (("词典", "搜索汉字、谚文、罗马字与英文词条。"),
                    ("输入法", "使用 TLI 谚文输入法书写闽南语。")),
    }
    for language in LANGUAGES:
        for slug, (title, description) in zip(("dictionary", "ime"), tool_copy[language]):
            search_documents[language].append(search_document(
                f"{language}:tool:{slug}", title, language_url(f"/{slug}/", language),
                "tool", "", description,
            ))
    search_index = {
        "schemaVersion": 1,
        "hanriFold": hanri_fold_map(),
        "languages": {
            language: sorted(documents, key=lambda item: (item["kind"], item["title"], item["url"]))
            for language, documents in search_documents.items()
        },
    }
    data_target = output / "public/data/site-search-index.json"
    data_target.parent.mkdir(parents=True, exist_ok=True)
    data_target.write_text(json.dumps(search_index, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    target = output / "assets/content-site"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("site.css", "site.js"):
        shutil.copy2(root / "apps/content-site" / name, target / name)
    old_song_route = '/songs/請問릐감欲做꽈에ᄁힻ흐렌/'
    new_song_route = '/songs/請問릐감欲做꽈에ᄁힻ흐뗀/'
    if old_song_route in paths or new_song_route not in paths:
        raise ValueError('Invalid song redirect routes')
    redirect = output / old_song_route.lstrip('/') / 'index.html'
    redirect.parent.mkdir(parents=True, exist_ok=True)
    destination = html.escape(new_song_route, quote=True)
    redirect.write_text('<!doctype html><meta charset="utf-8">'
        f'<meta http-equiv="refresh" content="0; url={destination}">'
        f'<link rel="canonical" href="{destination}">'
        f'<script>location.replace({json.dumps(new_song_route, ensure_ascii=True)} + location.search + location.hash)</script>'
        f'<a href="{destination}">Continue to the song</a>', encoding='utf-8')
    paths.add(old_song_route)
    (output / "content-manifest.json").write_text(json.dumps({"language": "en", "languages": languages, "routes": sorted(paths), "pages": [{**{key: item[key] for key in ("title", "route", "language", "type", "sourceId", "sourceUrl", "orthography")}, **({'derivedFrom': item['derivedFrom']} if 'derivedFrom' in item else {})} for item in published_records], "deferred": manifest["deferred"]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return sorted(paths)
