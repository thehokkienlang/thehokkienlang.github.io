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
from story_presentations import EGG_ROUTE, assemble_story, egg_presentation, simplified_egg, soundcloud_source
from lyric_timing import decorate_lyrics
from image_descriptions import describe_images
from page_meta import description as page_description, meta_tags

# Header, in order: a (label, destinations) pair is a dropdown; an (href, label) pair is a link.
NAV_GROUPS = (
    ("Learn", (("/learn/introduction/", "Introduction"), ("/learn/tone-sandhi/", "Tone sandhi"), ("/learn/spelling/", "Spelling"), ("/learn/romanisation/", "Romanisation"))),
    ("/songs/", "Songs"),
    ("/read/", "Read"),
    ("Tools", (("/dictionary/", "Dictionary"), ("/ime/", "Hokkien IME"), ("/translate/", "Translator"))),
)
NAV = (("/about/", "About"), ("/search/", "Search"))
IME_SCRIPTS = ('<script src="/shared/web-hangul-ime.js" defer></script>'
               '<script src="/shared/web-ime-core.js" defer></script>')
# The shared search box, song matcher and matching rule; they run before site.js, which wires the filter.
SONG_SEARCH_SCRIPTS = ('<script src="/shared/web-site-search-variants.js" defer></script>'
                       '<script src="/shared/web-search-box.js" defer></script>'
                       '<script src="/shared/web-song-search.js" defer></script>')
LYRIC_SCRIPTS = ('<script src="/shared/web-lyric-player.js" defer></script>'
                 '<script src="/shared/web-lyric-sync.js" defer></script>')
TITLE_READING = re.compile(r'class="[^"]*\btitle-reading\b[^"]*"[^>]*>(.*?)</(?:h1|h2|a|span)>', re.S)
HANGUL = re.compile(r"[\u1100-\u11ff\u3130-\u318f\ua960-\ua97f\uac00-\ud7a3\ud7b0-\ud7ff]")
SONG_FILTER_TEXT = {
    "en": {"filterBy": "Filter by", "sound": "Sound", "mood": "Mood", "all": "All", "empty": "No songs match.", "count": "{n} songs",
           "clear": "Clear filters", "teochew": "Teochew", "mandarin": "Mandarin"},
    "zh-Hant": {"filterBy": "篩選條件", "sound": "曲風", "mood": "心情", "all": "全部", "empty": "沒有符合的歌曲。", "count": "{n} 首歌曲",
                "clear": "清除篩選", "teochew": "潮汕", "mandarin": "華語"},
    "zh-Hans": {"filterBy": "筛选条件", "sound": "曲风", "mood": "心情", "all": "全部", "empty": "没有符合的歌曲。", "count": "{n} 首歌曲",
                "clear": "清除筛选", "teochew": "潮汕", "mandarin": "华语"},
}
# The badge colours of a song's dialect (plan: the old Voice of Teochew category's).
DIALECT_BADGE = {
    "teochew": {"accent": "#3f718b", "tint": "#cdeef5", "tintEnd": "#dbe5ff"},
    "mandarin": {"accent": "#78618b", "tint": "#eee0f5", "tintEnd": "#e4e7fa"},
}


CLASSIFICATION_CACHE = {}


def song_classification(root):
    """The fixed sound and mood lists and each song page's sound, moods and dialect.

    Returns (sounds, moods, by_route). `sounds` and `moods` are the lists in content/song-sounds.json and
    content/song-moods.json; `by_route` maps a song page's route to its file's sound, moods and dialect.
    Read once per build (build_content clears the cache), because every song page asks for it.
    """
    if root not in CLASSIFICATION_CACHE:
        CLASSIFICATION_CACHE[root] = _read_song_classification(root)
    return CLASSIFICATION_CACHE[root]


def _read_song_classification(root):
    sounds = json.loads((root / "content/song-sounds.json").read_text(encoding="utf-8"))
    moods = json.loads((root / "content/song-moods.json").read_text(encoding="utf-8"))
    by_route = {}
    for path in sorted((root / "content/songs").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if "sound" in record:
            by_route[record["route"]] = {"sound": record["sound"], "moods": record.get("moods", []),
                                         "dialect": record.get("dialect", "")}
    return sounds, moods, by_route
# Every label a public search box shows, in one place: SEARCH_TEXT[box][language]. Python writes
# these into the markup, so no script keeps its own copy.
SEARCH_TEXT = {
    # The Songs sub-header's box: on /songs/ it drives the page's filter, on a song page it opens a
    # dropdown of matching songs.
    # The dictionary's box (its page is one page shown in three languages, switched when it loads).
    "dictionary": {
        "en": {"label": "Search", "keyboard": "Enable Hangul keyboard", "clear": "Clear search",
               "candidates": "Hanri candidates", "placeholder": "Type 漢字, 한글, Lomari, or English..."},
        "zh-Hant": {"label": "搜尋", "keyboard": "啟用諺文鍵盤", "clear": "清除搜尋",
                    "candidates": "漢字候選詞", "placeholder": "輸入漢字、諺文、羅馬字或英文…"},
        "zh-Hans": {"label": "搜索", "keyboard": "启用谚文键盘", "clear": "清除搜索",
                    "candidates": "汉字候选词", "placeholder": "输入汉字、谚文、罗马字或英文…"},
    },
    # The /search/ page's box.
    "site": {
        "en": {"label": "Search the website", "keyboard": "Enable Hangul keyboard", "clear": "Clear search",
               "candidates": "Hanri candidates", "placeholder": "Search pages, songs, and stories..."},
        "zh-Hant": {"label": "搜尋網站", "keyboard": "啟用諺文鍵盤", "clear": "清除搜尋",
                    "candidates": "漢字候選詞", "placeholder": "搜尋頁面、歌曲與故事…"},
        "zh-Hans": {"label": "搜索网站", "keyboard": "启用谚文键盘", "clear": "清除搜索",
                    "candidates": "汉字候选词", "placeholder": "搜索页面、歌曲与故事…"},
    },
    "songs": {
        "en": {"label": "Search songs", "keyboard": "Enable Hangul keyboard", "clear": "Clear search",
               "candidates": "Hanri candidates", "placeholder": "Search songs…",
               "more": "See all {n} results", "empty": "No songs found."},
        "zh-Hant": {"label": "搜尋歌曲", "keyboard": "啟用諺文鍵盤", "clear": "清除搜尋",
                    "candidates": "漢字候選詞", "placeholder": "搜尋歌曲…",
                    "more": "查看全部 {n} 筆結果", "empty": "找不到歌曲。"},
        "zh-Hans": {"label": "搜索歌曲", "keyboard": "启用谚文键盘", "clear": "清除搜索",
                    "candidates": "汉字候选词", "placeholder": "搜索歌曲…",
                    "more": "查看全部 {n} 条结果", "empty": "找不到歌曲。"},
    },
}


def search_box_html(box_id, language, variant, labels, results="none", more_href="", ids=None, autofocus=False):
    """The markup of every public search box; TliSearchBox (shared/web-search-box.js) attaches to it.

    The input is `<box_id>Input`, its clear button `<box_id>Clear` and its candidate menu
    `<box_id>Candidates`; `ids` overrides any of them (keys input, clear, candidates) or gives the
    keyboard switch an id (key toggle), so a page's existing ids stay. `variant` is "full"
    (a page's main search) or "compact" (the Songs sub-header box: its label is for screen readers
    only and the keyboard switch sits inside the input). results="dropdown" adds a results list.
    """
    words = {key: html.escape(value, quote=True) for key, value in SEARCH_TEXT[labels][language].items()}
    ids = {"input": f"{box_id}Input", "clear": f"{box_id}Clear", "candidates": f"{box_id}Candidates", **(ids or {})}
    toggle = (
        (f'<button id="{ids["toggle"]}" ' if "toggle" in ids else '<button ') + 'class="hangul-keyboard-toggle" type="button" aria-pressed="false"'
        + (f' aria-label="{words["keyboard"]}" title="{words["keyboard"]}"' if variant == "compact" else "") + '>'
        f'<span class="toggle-label{" visually-hidden" if variant == "compact" else ""}">{words["keyboard"]}</span>'
        '<span class="toggle-switch" aria-hidden="true"><span class="toggle-knob"></span></span></button>'
    )
    hidden_class = ' class="visually-hidden"' if variant == "compact" else ""
    label = f'<label for="{ids["input"]}"{hidden_class}>{words["label"]}</label>'
    # A song page is one page shown in three languages, switched when it loads, so the box carries
    # every language's labels and TliSearchBox applies the page's.
    all_labels = html.escape(json.dumps(SEARCH_TEXT[labels], ensure_ascii=False, separators=(",", ":")), quote=True)
    attributes = f' data-labels="{all_labels}"'
    dropdown = ""
    if results == "dropdown":
        attributes += (f' data-more-label="{words["more"]}" data-empty-label="{words["empty"]}" '
                       f'data-more-href="{html.escape(more_href, quote=True)}"')
        dropdown = (f'<div id="{box_id}Results" class="tli-search-dropdown" role="listbox" '
                    f'aria-label="{words["label"]}" hidden></div>')
    # In the compact variant the label is for screen readers and the switch sits inside the input's
    # box; elsewhere the label and the switch head the box.
    heading = "" if variant == "compact" else f'<div class="tli-search-heading">{label}{toggle}</div>'
    return (
        f'<div class="tli-search tli-search--{variant}" data-tli-search{attributes}>'
        + heading +
        '<div class="tli-search-input-wrap">'
        + (label if variant == "compact" else "") +
        f'<input id="{ids["input"]}" class="tli-search-input" type="text" inputmode="search" enterkeyhint="search" '
        f'autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="{words["placeholder"]}"'
        + (" autofocus" if autofocus else "")
        + (f' role="combobox" aria-expanded="false" aria-controls="{box_id}Results" aria-autocomplete="list"'
           if results == "dropdown" else "") + '>'
        f'<button id="{ids["clear"]}" class="tli-search-clear" type="button" aria-label="{words["clear"]}" hidden>&times;</button>'
        + (toggle if variant == "compact" else "") +
        f'<div id="{ids["candidates"]}" class="hanri-candidate-menu" role="listbox" '
        f'aria-label="{words["candidates"]}" hidden></div></div>'
        + dropdown + '</div>'
    )


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


# The Learn path, in reading order. "start" guides are lessons to read in order; "reference"
# guides are for looking things up. Each has one sentence saying what the reader gets from it.
LEARN_PATH = (
    ("/learn/introduction/", "start", {
        "en": "Meet the letters, the five tones and your first everyday phrases, with audio.",
        "zh-Hant": "認識字母、五個聲調和第一批日常用語，附發音。",
        "zh-Hans": "认识字母、五个声调和第一批日常用语，附发音。"}),
    ("/learn/tone-sandhi/", "start", {
        "en": "How a syllable’s tone changes inside a phrase, step by step, with examples you can play.",
        "zh-Hant": "聲調在詞句中如何變化，配合可播放的例子逐步說明。",
        "zh-Hans": "声调在词句中如何变化，配合可播放的例子逐步说明。"}),
    ("/learn/spelling/", "reference", {
        "en": "The conventions behind TLI spellings across regional varieties and for foreign words.",
        "zh-Hant": "東寧音在各地腔調與外來語上的拼寫慣例。",
        "zh-Hans": "东宁音在各地腔调与外来语上的拼写惯例。"}),
    ("/learn/romanisation/", "reference", {
        "en": "How Lomari, TLI’s Latin spelling, compares with POJ and Tâi-lô.",
        "zh-Hant": "東寧音羅馬字（Lomari）與白話字、台羅的對照。",
        "zh-Hans": "东宁音罗马字（Lomari）与白话字、台罗的对照。"}),
)
LEARN_TEXT = {
    "en": {"start": "Start here", "start_note": "New to TLI? Read these two in order.",
           "reference": "Reference", "reference_note": "Look things up here when you need the detail. Beginners can skip these.",
           "next": "Next", "song": "Now try reading a song", "all": "All Learn pages"},
    "zh-Hant": {"start": "從這裡開始", "start_note": "初次接觸東寧音？請依序閱讀這兩篇。",
                "reference": "參考資料", "reference_note": "需要查詢細節時再看，初學者可以先跳過。",
                "next": "下一篇", "song": "接著試讀一首歌", "all": "所有學習頁面"},
    "zh-Hans": {"start": "从这里开始", "start_note": "初次接触东宁音？请依序阅读这两篇。",
                "reference": "参考资料", "reference_note": "需要查询细节时再看，初学者可以先跳过。",
                "next": "下一篇", "song": "接着试读一首歌", "all": "所有学习页面"},
}


def learn_title(item):
    return html.escape(item["title"].replace("Tangliengim", "TLI"))


def learn_index(guides, language):
    """The Learn landing page: a numbered path to read in order, then the reference guides."""
    words = LEARN_TEXT[language]
    by_route = {base_route(item["route"]): item for item in guides}
    groups = []
    for track in ("start", "reference"):
        rows = []
        for path, item_track, summary in LEARN_PATH:
            if item_track == track and path in by_route:
                item = by_route[path]
                rows.append(f'<li><a class="title-reading" href="{html.escape(item["route"], quote=True)}">{learn_title(item)}</a>'
                            f'<p>{html.escape(summary[language])}</p></li>')
        if rows:
            tag = "ol" if track == "start" else "ul"
            groups.append(f'<section class="learn-track learn-track-{track}"><h2>{words[track]}</h2>'
                          f'<p class="learn-track-note">{words[track + "_note"]}</p>'
                          f'<{tag} class="learn-path">{"".join(rows)}</{tag}></section>')
    # A guide missing from LEARN_PATH still gets listed, so a new page is never unreachable.
    known = {path for path, _track, _summary in LEARN_PATH}
    extra = [item for item in guides if base_route(item["route"]) not in known]
    if extra:
        groups.append('<ul class="page-list">' + "".join(
            f'<li><a class="title-reading" href="{html.escape(item["route"], quote=True)}">{learn_title(item)}</a></li>' for item in extra) + "</ul>")
    return "".join(groups)


def learn_next_link(route, language, records):
    """A link at the foot of a guide to the next page on the Learn path."""
    words = LEARN_TEXT[language]
    order = [path for path, _track, _summary in LEARN_PATH]
    current = base_route(route)
    if current not in order:
        return ""
    by_route = {base_route(item["route"]): item for item in records if item["type"] == "guides" and item["language"] == language}
    tracks = {path: track for path, track, _summary in LEARN_PATH}
    following = next((path for path in order[order.index(current) + 1:] if tracks[path] == tracks[current] and path in by_route), None)
    if following:
        target, label = by_route[following]["route"], learn_title(by_route[following])
        lead = words["next"]
    elif tracks[current] == "start":
        target, label, lead = language_url("/songs/", language) or "/songs/", words["song"], words["next"]
    else:
        target, label, lead = language_url("/learn/", language) or "/learn/", words["all"], ""
    lead_html = f'<span class="learn-next-lead">{lead}</span>' if lead else ""
    return (f'<nav class="learn-next" aria-label="{words["next"]}"><a href="{html.escape(target, quote=True)}">'
            f'{lead_html}<span class="learn-next-title">{label}</span></a></nav>')


# The sandhi setting in the header's language menu (docs/sandhi-toggle-plan.md). The same words are in
# shared/web-sandhi-preference.js; a test checks the two agree.
SANDHI_NAV_LABELS = {
    "en": {"sandhi": "Tone pattern", "change": "", "term": "tone sandhi", "taipei": "Taipei", "singapore": "Singapore",
           "note": "Changes how {term} sounds and is marked."},
    "zh-Hant": {"sandhi": "聲調形式", "change": "", "term": "變調", "taipei": "臺北", "singapore": "新加坡",
                "note": "改變{term}的讀音與標示方式。"},
    "zh-Hans": {"sandhi": "声调形式", "change": "", "term": "变调", "taipei": "台北", "singapore": "新加坡",
                "note": "改变{term}的读音与标示方式。"},
}


def sandhi_setting(language):
    words = SANDHI_NAV_LABELS[language]
    guide = language_url("/learn/tone-sandhi/", language)
    term = f'<a class="site-sandhi-guide" href="{guide}">{words["term"]}</a>'
    note = words["note"].format(term=term)
    return ('<div class="site-sandhi" role="group" aria-label="' + words["sandhi"] + '">'
            f'<span class="site-sandhi-label">{(words["sandhi"] + " " + words["change"]).strip()}</span>'
            '<span class="site-sandhi-choices">'
            f'<button type="button" class="site-sandhi-choice" data-sandhi-choice="taipei" aria-pressed="false">{words["taipei"]}</button>'
            f'<button type="button" class="site-sandhi-choice" data-sandhi-choice="singapore" aria-pressed="false">{words["singapore"]}</button>'
            f'</span><p class="site-sandhi-note">{note}</p></div>')


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
                 f'<div class="site-nav-panel">{"".join(choices)}{sandhi_setting(language)}</div></details>')
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
            # The Singapore clips go beside the Taipei ones, only where they differ.
            singapore = ((entry.get("audio") or {}).get("singapore") or {}).get("segments") or []
            return play_button(language, segments, singapore)
    return ""


LISTEN_TOKEN = re.compile(r'(?:<p[^>]*>\s*)?\[\[tli-listen (\S+) (\S+)\]\](?:\s*</p>)?')


def expand_listen_tokens(root, language, body):
    """Turn "[[tli-listen 心內 심5래5]]" in a guide into that dictionary entry's play button.

    A guide example plays the dictionary's own recording instead of a separate audio file, so it
    follows the dictionary (and the Taipei/Singapore preference). A token with no matching entry
    that has audio is an error, never a silent gap.
    """
    def button(match):
        result = listen_button(root, language, match[1], match[2])
        if not result:
            raise ValueError(f"No dictionary audio for {match[1]} {match[2]} (a [[tli-listen]] token in a guide)")
        return f'<p class="tli-listen-slot">{result}</p>'
    return LISTEN_TOKEN.sub(button, body)


def play_button(language, segments, singapore=None):
    clips = html.escape(json.dumps(segments, ensure_ascii=False, separators=(",", ":")), quote=True)
    singapore_clips = ""
    if singapore and singapore != segments:
        singapore_clips = (' data-tli-audio-singapore="'
                           + html.escape(json.dumps(singapore, ensure_ascii=False, separators=(",", ":")), quote=True) + '"')
    return (f'<button type="button" class="tli-listen" data-tli-audio="{clips}"{singapore_clips}>'
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
        ("02", hear, hear_note, "/songs/", hear_link),
        ("03", read, read_note, "/read/", read_link),
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
        '<section class="home-feature home-feature-songs"><div class="home-feature-heading">'
        f'<span class="home-feature-meta">{html.escape(labels["songs_meta"])}</span>'
        f'<h2>{html.escape(labels["songs_title"])}</h2><p>{html.escape(labels["songs_copy"])}</p>'
        f'{link("/songs/", labels["songs_link"])}</div>{songs}</section>'
        '<section class="home-feature home-feature-literature">'
        '<div class="home-feature-heading">'
        f'<span class="home-feature-meta">{html.escape(labels["read_meta"])}</span>'
        f'<h2>{html.escape(labels["read_title"])}</h2><p>{html.escape(labels["read_copy"])}</p></div>{literature}</section></section>'
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
            "filters": "Filter search results",
            "results": "Search results",
            "pages": "Search result pages",
            "noscript": "JavaScript is required for website search.",
        },
        "zh-Hant": {
            "filters": "篩選搜尋結果",
            "results": "搜尋結果",
            "pages": "搜尋結果頁面",
            "noscript": "網站搜尋需要啟用 JavaScript。",
        },
        "zh-Hans": {
            "filters": "筛选搜索结果",
            "results": "搜索结果",
            "pages": "搜索结果页面",
            "noscript": "网站搜索需要启用 JavaScript。",
        },
    }[language]
    return (
        '<section class="site-search">'
        '<form id="siteSearchForm" class="site-search-form" role="search">'
        + search_box_html("siteSearch", language, "full", "site", ids={"toggle": "hangulKeyboardToggle"}) +
        f'<div id="siteSearchFilters" class="site-search-filters" role="group" '
        f'aria-label="{html.escape(labels["filters"], quote=True)}"></div></form>'
        '<p id="siteSearchSummary" class="site-search-summary" aria-live="polite"></p>'
        f'<section id="siteSearchResults" class="site-search-results" '
        f'aria-label="{html.escape(labels["results"], quote=True)}"></section>'
        f'<nav id="siteSearchPagination" class="site-search-pagination" '
        f'aria-label="{html.escape(labels["pages"], quote=True)}" hidden></nav>'
        f'<noscript><p>{html.escape(labels["noscript"])}</p></noscript></section>'
    )


SONGS_LABELS = {"en": "Songs", "zh-Hant": "歌曲", "zh-Hans": "歌曲"}


def language_spans(labels):
    """A name written in all three languages; a song page shows the one for its language."""
    return "".join(f'<span data-content-lang="{code}">{html.escape(labels.get(code, labels["en"]))}</span>'
                   for code in LANGUAGES)


def singer_labels(singer):
    # Keep authored names intact; localise their script only for display.
    traditional = singer.replace("陈佳", "陳佳")
    simplified = simplified_headword(traditional) or traditional
    return {"en": traditional, "zh-Hant": traditional, "zh-Hans": simplified}


def singer_html(singer, class_name, language="en"):
    if not singer:
        return ""
    labels = singer_labels(singer)
    return (f'<span class="{class_name}" '
            f'data-singer-traditional="{html.escape(labels["en"], quote=True)}" '
            f'data-singer-simplified="{html.escape(labels["zh-Hans"], quote=True)}">'
            f'{html.escape(labels[language])}</span>')


def song_meta_html(root, singer, route):
    """Under a song's title: its singer, its mood chips (each a link to that mood on /songs/) and the
    dialect badge. `route` is the song page's route; a version tab passes its own version's singer."""
    _, moods, classification = song_classification(root)
    found = classification.get(base_route(route))
    parts = []
    if singer:
        parts.append(singer_html(singer, "song-singer"))
    if found:
        by_id = {item["id"]: item for item in moods}
        for mood_id in found["moods"]:
            mood = by_id[mood_id]
            parts.append(
                f'<a class="song-mood" href="/songs/?mood={html.escape(mood_id, quote=True)}" '
                f'style="--category-accent:{html.escape(mood["accent"], quote=True)};'
                f'--category-tint:{html.escape(mood["tint"], quote=True)}">{language_spans(mood["labels"])}</a>')
        badge = DIALECT_BADGE.get(found["dialect"])
        if badge:
            labels = {code: SONG_FILTER_TEXT[code][found["dialect"]] for code in LANGUAGES}
            parts.append(
                f'<span class="song-dialect-badge" style="--category-accent:{badge["accent"]};'
                f'--category-tint:{badge["tint"]};--category-tint-end:{badge["tintEnd"]}">{language_spans(labels)}</span>')
    return f'<div class="song-meta">{"".join(parts)}</div>' if parts else ""


def songs_subheader(root, route, language):
    """The slim bar under the main header on /songs/ and every song page: a breadcrumb on the left
    (Songs › Category) and the Songs search box on the right.

    A song page is one page shown in three languages (switched when it loads), so each name is written
    in all three and the page shows the one for its language.
    """
    named = language_spans

    on_index = base_route(route) == "/songs/"
    songs = named(SONGS_LABELS)
    if on_index:
        crumb = f'<span class="songs-breadcrumb-current" aria-current="page">{songs}</span>'
    else:
        sounds, _, classification = song_classification(root)
        found = classification.get(base_route(route))
        sound = next((item for item in sounds if found and item["id"] == found["sound"]), None)
        crumb = f'<a class="songs-breadcrumb-root" href="/songs/">{songs}</a>'
        if sound:
            crumb += (f'<span class="songs-breadcrumb-sep" aria-hidden="true">›</span>'
                      f'<a class="songs-breadcrumb-category" href="/songs/?sound={html.escape(sound["id"], quote=True)}">'
                      f'{named(sound["labels"])}</a>')
    box = search_box_html("songFilter" if on_index else "songSearch", language, "compact", "songs",
                          results="none" if on_index else "dropdown", more_href="/songs/")
    return (f'<div class="songs-subheader"><div class="songs-breadcrumb" role="navigation" aria-label="Breadcrumb">{crumb}</div>'
            f'{box}</div>')


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
    values = {"LANG": language, "HOME": PREFIXES[language] + "/", "SKIP": text("Skip to content", language), "ALTERNATES": alternates, "TITLE": html.escape(title), "HEADING": heading_markup, "INTRODUCTION": introduction, "EYEBROW": eyebrow, "ROUTE": html.escape(route, quote=True), "NAV": navigation, "BODY": body, "TYPE": content_type, "SECTION": html.escape(section), "LAUNCH": home_launch(language, listen_button(root, language, "聲音", "샬5임1")) if section == "home" else "", "PAGESTYLES": '<link rel="stylesheet" href="/shared/web-ime-menu.css"><link rel="stylesheet" href="/assets/search/styles.css">' if is_search else "", "PAGESCRIPTS": '<script src="/shared/web-site-search-variants.js" defer></script><script src="/shared/web-search-box.js" defer></script><script src="/assets/search/search.js" defer></script>' if is_search else ('<script src="/shared/web-audio-player.js" defer></script>' if section == "home" or "data-tli-audio=" in body else "")}
    # Audit A5: each page loads only the scripts it uses. The IME scripts draw tone marks in
    # Hangul titles (site.js) and run the search box; the lyric scripts run on song pages.
    launch = values["LAUNCH"]
    needs_ime = is_search or bool(HANGUL.search(values["HEADING"])) or any(
        HANGUL.search(match) for match in TITLE_READING.findall(body + launch))
    songs_section = content_type == "songs" or base_route(route) == "/songs/"
    values["IMESCRIPTS"] = (IME_SCRIPTS if needs_ime else "") + (SONG_SEARCH_SCRIPTS if songs_section else "")
    values["SUBHEADER"] = songs_subheader(root, route, language) if songs_section else ""
    values["LYRICSCRIPTS"] = LYRIC_SCRIPTS if content_type == "songs" else ""
    # A song page's accent bar under the title takes its sound's colour, as its row on /songs/ does.
    values["MAINATTRS"] = ""
    values["HEADINGATTRS"] = ""
    if content_type == "songs":
        sounds, _, classification = song_classification(root)
        found = classification.get(base_route(route))
        sound = next((item for item in sounds if found and item["id"] == found["sound"]), None)
        if sound:
            values["MAINATTRS"] = f' style="--song-accent:{html.escape(sound["accent"], quote=True)}"'
        # A song in another dialect (Teochew) has its title in that dialect: its tone marks stay as
        # written whatever the reader's Taipei/Singapore sandhi (shared/web-sandhi-display.js).
        if found and found.get("dialect"):
            values["HEADINGATTRS"] = " data-sandhi-fixed"
    values["BRAND"] = site_brand(root, language)
    values["META"] = meta_tags(title, route, page_description(
        title, base_route(route), body, content_type, language, home_introductions[language]), language)
    # One pass prevents source content resembling a placeholder from becoming executable template markup.
    return re.sub(r"__([A-Z]+)__", lambda match: values[match[1]], template)


def build_content(root: Path, output: Path):
    CLASSIFICATION_CACHE.clear()  # the song files may have changed since the last build
    content = root / "content"
    if not content.exists():
        return []
    # Keep archived sources in the repository, but never publish their routes.
    unpublished_routes = {"/songs/translation-notes/", "/read/literature/lychee-mirror/"}
    manifest = json.loads((root / "migration/wordpress-map.json").read_text(encoding="utf-8"))
    records = [
        assemble_story(json.loads((root / item["file"]).read_text(encoding="utf-8")), root)
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
                # Each tab shows its own version's singer, with the song's moods and dialect badge.
                version_body = song_meta_html(root, str(version_record.get("singer", "")).strip(), route) + version_body
                rendered_versions.append((version_record, version_body))
            body = song_version_tabs(rendered_versions)
        else:
            heading_html, body = song_title(record) if record["type"] == "songs" else (None, record["body"])
        if record["type"] == "songs" and route not in versions_by_route:
            body = split_song_notes(song_script_heading(body))
        if not (record["type"] == "songs" and route in versions_by_route):
            body = PresentationHTML(record).render(remove_leading_language_switcher(body))
        if record['type'] == 'songs' and route not in versions_by_route:
            body = song_meta_html(root, str(record.get("singer", "")).strip(), route) + decorate_lyrics(root, record, body)
        if base_route(route) == "/":
            body = curate_home_body(body, record["language"], [item for item in published_records if item["type"] == "songs"],
                                    listen_button(root, record["language"], "學生", "학솅1"))
        if record["type"] == "guides":
            body = expand_listen_tokens(root, record["language"], body)
        body = describe_images(body, record["language"])
        page_body = body + learn_next_link(route, record["language"], published_records) if record["type"] == "guides" else body
        target.write_text(document(root, record["title"], route, page_body, record["type"], record["sourceUrl"], heading_html), encoding="utf-8")
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
    song_sounds, song_moods, classification = song_classification(root)
    songs_by_route = {item["route"]: item for item in published_records if item["type"] == "songs"}
    approved_routes = {row["new_url"] for row in song_rows}
    if approved_routes != set(songs_by_route) or approved_routes != set(classification):
        missing = sorted(approved_routes - set(classification))
        extra = sorted(set(classification) - approved_routes)
        raise ValueError(f"Song sounds are out of sync with the song list; missing={missing}, extra={extra}")
    sound_ids = {item["id"] for item in song_sounds}
    mood_ids = {item["id"] for item in song_moods}
    for route, found in classification.items():
        if found["sound"] not in sound_ids or not found["moods"] or not set(found["moods"]) <= mood_ids:
            raise ValueError(f"{route} has an unknown sound or mood")

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
        mandarin_titles.extend(
            record.get("mandarinAlternativeTitle", "").strip()
            for record in route_records
            if record.get("mandarinAlternativeTitle", "").strip()
        )
        mandarin_titles = list(dict.fromkeys(mandarin_titles))
        mandarin_simplified_titles = list(dict.fromkeys(
            record.get("mandarinTitleSimplified", "").strip()
            or simplified_headword(re.sub(r"\s+諺文(?:/中文)?歌詞\s*$", "", record.get("originalTitle", "").strip()))
            or re.sub(r"\s+諺文(?:/中文)?歌詞\s*$", "", record.get("originalTitle", "").strip())
            for record in route_records
            if record.get("originalTitle", "").strip()
        ))
        mandarin_simplified_titles.extend(
            record.get("mandarinAlternativeTitleSimplified", "").strip()
            or simplified_headword(record.get("mandarinAlternativeTitle", "").strip())
            for record in route_records
            if record.get("mandarinAlternativeTitle", "").strip()
        )
        mandarin_simplified_titles = list(dict.fromkeys(filter(None, mandarin_simplified_titles)))
        lines = []
        seen_lines = set()
        for record_index, record in enumerate(route_records):
            for position, line in enumerate(lyric_lines(record.get("body", "")), start=1):
                identity = (line["main"], line["mainHtml"], line["lomari"], line["search"])
                if identity not in seen_lines:
                    seen_lines.add(identity)
                    # The line's number on the song's own page (0 where a version tab, not the page,
                    # holds it), so a search result can open the song at that line.
                    lines.append({**line, "anchor": position if record_index == 0 else 0})
        song_items[route] = {
            "label": label,
            "sound": classification[route]["sound"],
            "moods": classification[route]["moods"],
            "dialect": classification[route]["dialect"],
            # A song with versions lists its original's singer (the first version).
            "singer": str(route_records[0].get("singer", "")).strip(),
            "lomari": song_lomari(imported),
            "mandarinTitle": " / ".join(mandarin_titles),
            "mandarinSearch": " ".join([original_titles, *mandarin_titles, *mandarin_simplified_titles]),
            "lines": lines,
            "sort": (not bool(sort_reading), reading_sort_key(sort_reading)),
            # Title search stays compact; structured lyric lines are indexed by the browser.
            "search": " ".join(part for part in (
                re.sub(r"<[^>]+>", " ", label), imported.get("title", ""),
                sort_reading, song_lomari(imported),
            ) if part),
        }

    sound_by_id = {item["id"]: item for item in song_sounds}
    mood_by_id = {item["id"]: item for item in song_moods}
    # Sections and sound filters run Modern, Classic, Roots.
    section_sounds = list(reversed(song_sounds))

    def label_of(item, language):
        return item["labels"].get(language, item["labels"]["en"])

    def accent_style(item):
        return (f'--category-accent:{html.escape(item["accent"], quote=True)};'
                f'--category-tint:{html.escape(item["tint"], quote=True)};'
                f'--category-tint-end:{html.escape(item["tintEnd"], quote=True)}')

    def song_index(language):
        words = SONG_FILTER_TEXT[language]
        sections = []
        for sound in section_sounds:
            routes = [route for route, item in song_items.items() if item["sound"] == sound["id"]]
            items = sorted(routes, key=lambda route: (song_items[route]["sort"], route))
            links = []
            for route in items:
                destination = language_url(route, language) or route
                item = song_items[route]
                entry_class = "title-reading song-entry"
                singer = singer_html(item["singer"], "song-entry-singer", language)
                mood_buttons = "".join(
                    f'<button type="button" class="song-row-mood" data-song-row-mood="{html.escape(mood, quote=True)}" '
                    f'style="--category-accent:{html.escape(mood_by_id[mood]["accent"], quote=True)};'
                    f'--category-tint:{html.escape(mood_by_id[mood]["tint"], quote=True)}">'
                    f'{html.escape(label_of(mood_by_id[mood], language))}</button>'
                    for mood in item["moods"])
                badge = DIALECT_BADGE.get(item["dialect"])
                badge_markup = (
                    f'<span class="song-dialect-badge" style="--category-accent:{badge["accent"]};'
                    f'--category-tint:{badge["tint"]};--category-tint-end:{badge["tintEnd"]}">{words[item["dialect"]]}</span>'
                    if badge else "")
                # Search data lives in public/data/song-search-index.json, joined to this row by route.
                links.append(
                    f'<li data-song-route="{html.escape(route, quote=True)}"'
                    f'{" data-sandhi-fixed" if item["dialect"] else ""}>'
                    f'<a class="{entry_class}" '
                    f'href="{html.escape(destination, quote=True)}">'
                    f'<span class="song-entry-title">{item["label"]}'
                    '<small class="song-entry-mandarin-match" hidden></small></span>'
                    f'<span class="song-entry-lomari">{html.escape(item["lomari"])}</span>'
                    '<span class="song-entry-match" hidden>'
                    '<span class="song-entry-match-main"></span>'
                    '<span class="song-entry-match-lomari"></span></span>'
                    f'{singer}</a>'
                    f'<div class="song-entry-tags">{mood_buttons}{badge_markup}</div></li>'
                )
            title = label_of(sound, language)
            sections.append(
                '<section class="song-category" '
                f'data-song-sound="{html.escape(sound["id"], quote=True)}" '
                f'style="{accent_style(sound)}">'
                '<header class="song-category-heading">'
                f'<h2>{html.escape(title)}</h2><span>{len(items):02d}</span></header>'
                f'<ol class="song-list">{"".join(links)}</ol></section>'
            )
        return song_filter(language) + '<div class="song-catalogue">' + "".join(sections) + '</div>'

    def song_filter(language):
        words = SONG_FILTER_TEXT[language]

        def chip_row(kind, items):
            chips = [f'<button type="button" class="song-filter-chip" data-song-filter-{kind}="" aria-pressed="true">{words["all"]}</button>']
            for item in items:
                chips.append(
                    f'<button type="button" class="song-filter-chip" data-song-filter-{kind}="{html.escape(item["id"], quote=True)}" '
                    f'aria-pressed="false" style="--category-accent:{html.escape(item["accent"], quote=True)}">'
                    f'{html.escape(label_of(item, language))}</button>')
            return (f'<div class="song-filter-group"><span class="song-filter-label">{words[kind]}</span>'
                    f'<div class="song-filter-chips" role="group" aria-label="{words[kind]}">{"".join(chips)}</div></div>')
        return (
            f'<div class="song-filter" role="search" data-song-filter '
            f'data-count-template="{html.escape(words["count"], quote=True)}">'
            f'<p class="song-filter-heading">{words["filterBy"]}</p>'
            f'{chip_row("sound", section_sounds)}{chip_row("mood", song_moods)}'
            '<p class="song-filter-summary" aria-live="polite"></p>'
            f'<p class="song-filter-empty" hidden>{words["empty"]} '
            f'<button type="button" class="song-filter-clear" data-song-filter-clear>{words["clear"]}</button></p></div>'
        )
    sections = {}
    languages = manifest.get("languages", ["en"])
    for language in languages:
        prefix = PREFIXES[language]
        guides = [item for item in published_records if item["type"] == "guides" and item["language"] == language and base_route(item["route"]).startswith("/learn/")]
        stories = [{**item, "title": text("The Egg", language)} for item in published_records if item["type"] == "stories" and item["language"] == language]
        literature = [{**item, "route": language_url(item["route"], language), "title": text("Tale of the Lychee Mirror", language)} for item in published_records if item["type"] == "literature"]
        sections[prefix + "/learn/"] = (text("Learn Tangliengim", language), learn_index(guides, language))
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
        "languages": {
            language: sorted(documents, key=lambda item: (item["kind"], item["title"], item["url"]))
            for language, documents in search_documents.items()
        },
    }
    data_target = output / "public/data/site-search-index.json"
    data_target.parent.mkdir(parents=True, exist_ok=True)
    data_target.write_text(json.dumps(search_index, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    # Shared by every search box: the Hanri variant table, and the songs' search data.
    (output / "public/data/hanri-fold.json").write_text(
        json.dumps({"schemaVersion": 1, "hanriFold": hanri_fold_map()}, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8")
    song_search_index = {
        "schemaVersion": 2,
        "sounds": {item["id"]: item["labels"] for item in song_sounds},
        "moods": {item["id"]: item["labels"] for item in song_moods},
        "songs": [
            {
                "route": route,
                "urls": {language: language_url(route, language) or route for language in languages},
                "sound": item["sound"],
                "moods": item["moods"],
                "dialect": item["dialect"],
                "singer": singer_labels(item["singer"])["en"],
                "singerLabels": singer_labels(item["singer"]),
                "label": item["label"],
                "lomari": item["lomari"],
                "search": item["search"],
                "mandarinTitle": item["mandarinTitle"],
                "mandarinSearch": item["mandarinSearch"],
                "lines": [[line["main"], line["lomari"], line["search"], line["mainHtml"], line["anchor"]] for line in item["lines"]],
            }
            for route, item in sorted(song_items.items(), key=lambda pair: (pair[1]["sort"], pair[0]))
        ],
    }
    (output / "public/data/song-search-index.json").write_text(
        json.dumps(song_search_index, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
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
