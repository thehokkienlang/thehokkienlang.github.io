"""Render authored English and Chinese content into the Pages artifact."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

from song_title_readings import song_lomari, song_sort_reading, song_title
from tangliengim_collation import reading_sort_key
from import_wordpress import ImportedHTML, source_key
from site_languages import LANGUAGES, LANGUAGE_NAMES, PREFIXES, base_route, language_for_route, language_url, text

NAV = (("/", "Home"), ("/learn/", "Learn"), ("/songs/", "Songs"), ("/read/", "Read"), ("/dictionary/", "Dictionary"), ("/ime/", "IME"), ("/about/", "About"))
NAV_SECTIONS = {
    "/learn/": (("/learn/introduction/", "Introduction"), ("/learn/spelling/", "Spelling"), ("/learn/tone-sandhi/", "Tone sandhi"), ("/learn/romanisation/", "Romanisation")),
    "/read/": (("/read/stories/the-egg/", "The Egg"), ("/read/literature/lychee-mirror/", "Tale of the Lychee Mirror")),
}

# Render the whole grapheme in one font, including any stacked tone marks.
# Restrict this to text nodes; URLs, attributes and authored source stay intact.
NASAL_GRAPHEME = re.compile(r'[A-Za-z\u00c0-\u02ff\u1e00-\u1eff\u25cc][\u0300-\u036f]*\u0330[\u0300-\u036f]*')


def nasal_font_text(value):
    return NASAL_GRAPHEME.sub(lambda match: '<span class="nasal-grapheme">' + match.group() + '</span>', value)


def navigation_links(route, language=None, variants=True):
    language = language or language_for_route(route)

    def link(href, label):
        destination = language_url(href, language) or language_url(href, "zh-Hant")
        current = ' aria-current="page"' if base_route(route) == href or href != "/" and base_route(route).startswith(href) else ""
        return f'<a href="{html.escape(destination, quote=True)}"{current}>{html.escape(text(label, language))}</a>'

    items = []
    for href, label in NAV:
        if href in NAV_SECTIONS:
            active = " is-current" if base_route(route).startswith(href) else ""
            children = "".join(link(path, title) for path, title in NAV_SECTIONS[href])
            items.append(
                '<details class="site-nav-dropdown" name="site-navigation">'
                f'<summary class="site-nav-trigger{active}">{text(label, language)}</summary>'
                f'<div class="site-nav-panel">{children}</div></details>'
            )
        else:
            items.append(link(href, label))
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


def home_launch(language):
    labels = {
        "en": (
            "Learn TLI", "Understand the script, spelling, and tone sandhi.", "Start with the introduction",
            "Read Hokkien", "Stories and literature with pronunciation kept close to the text.", "Browse reading",
            "Hear the language", "Songs with Hangul readings and Lomari.", "Explore songs", "Writing tools", "student",
        ),
        "zh-Hant": (
            "學習東寧音", "了解文字、拼寫與變調。", "從使用說明開始",
            "閱讀閩南語", "讓故事與文學的讀音緊貼原文。", "瀏覽讀物",
            "聆聽語言", "附有諺文讀音與羅馬字的歌曲。", "探索歌曲", "書寫工具", "學生",
        ),
        "zh-Hans": (
            "学习东宁音", "了解文字、拼写与变调。", "从使用说明开始",
            "阅读闽南语", "让故事与文学的读音紧贴原文。", "浏览读物",
            "聆听语言", "附有谚文读音与罗马字的歌曲。", "探索歌曲", "书写工具", "学生",
        ),
    }
    learn, learn_note, learn_link, read, read_note, read_link, hear, hear_note, hear_link, tools, student = labels[language]

    def destination(path, label, class_name=""):
        url = language_url(path, language) or language_url(path, "zh-Hant")
        class_attr = f' class="{class_name}"' if class_name else ""
        return f'<a{class_attr} href="{html.escape(url, quote=True)}"><span>{html.escape(label)}</span><span aria-hidden="true">&#8594;</span></a>'

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
    return (
        '<section class="home-launch">'
        '<aside class="home-specimen" aria-label="Tangliengim writing specimen">'
        '<ruby><span lang="zh-Hant">學生</span><rt lang="ko">학솅ˆ</rt></ruby>'
        f'<span class="home-specimen-lomari">hak-siêng</span><span class="home-specimen-meaning">{html.escape(student)}</span></aside>'
        f'<div class="home-paths">{path_html}</div>'
        f'<div class="home-tools"><h2>{html.escape(tools)}</h2><div>{destination("/ime/", text("Open IME", language))}{destination("/dictionary/", text("Dictionary", language))}</div></div>'
        '</section>'
    )


def home_showcase(language):
    labels = {
        "en": {
            "label": "Explore TheHokkienLang",
            "learn_meta": "01 · Learn",
            "learn_title": "Learn TLI",
            "learn_copy": "Begin with the script, then move through spelling, romanisation, and tone.",
            "learn_link": "Start learning",
            "tone_meta": "02 · Listen closely",
            "tone_title": "Guide to Hokkien tone sandhi",
            "tone_copy": "Follow the sound changes that give a Hokkien phrase its rhythm, and see how TLI records what is heard.",
            "tone_link": "Read the tone-sandhi guide",
            "read_meta": "03 · Read",
            "read_title": "Literature works",
            "read_copy": "Meet Hokkien on the page through short fiction and dramatic literature, with pronunciation kept close to the text.",
            "egg_kind": "Short story",
            "egg_title": "The Egg",
            "egg_note": "A philosophical story presented in Hokkien.",
            "mirror_kind": "Classical literature",
            "mirror_title": "Tale of the Lychee Mirror",
            "mirror_note": "A Hokkien dramatic tradition in a reading edition.",
            "songs_meta": "04 · Hear",
            "songs_title": "Songs",
            "songs_copy": "From timeless classics to newer voices, explore lyrics with Hanri-Hangul readings and Lomari.",
            "songs_link": "Browse the songbook",
            "selection": "From the songbook",
        },
        "zh-Hant": {
            "label": "探索 TheHokkienLang",
            "learn_meta": "01 · 學習",
            "learn_title": "學習東寧音",
            "learn_copy": "從文字系統開始，再逐步認識拼寫、羅馬字與聲調。",
            "learn_link": "開始學習",
            "tone_meta": "02 · 細聽",
            "tone_title": "閩南語變調解析",
            "tone_copy": "了解變調如何構成閩南語詞句的節奏，以及東寧音如何記錄實際讀音。",
            "tone_link": "閱讀變調指南",
            "read_meta": "03 · 閱讀",
            "read_title": "文學讀物",
            "read_copy": "透過短篇小說與戲曲文學閱讀閩南語，讓讀音緊貼原文。",
            "egg_kind": "短篇小說",
            "egg_title": "《卵》",
            "egg_note": "以閩南語呈現的哲思故事。",
            "mirror_kind": "古典文學",
            "mirror_title": "《荔鏡記》",
            "mirror_note": "閩南戲曲傳統的閱讀版本。",
            "songs_meta": "04 · 聆聽",
            "songs_title": "歌曲",
            "songs_copy": "從歷久不衰的經典到新世代聲音，閱讀附有漢諺讀音與羅馬字的歌詞。",
            "songs_link": "瀏覽歌本",
            "selection": "歌本選讀",
        },
        "zh-Hans": {
            "label": "探索 TheHokkienLang",
            "learn_meta": "01 · 学习",
            "learn_title": "学习东宁音",
            "learn_copy": "从文字系统开始，再逐步认识拼写、罗马字与声调。",
            "learn_link": "开始学习",
            "tone_meta": "02 · 细听",
            "tone_title": "闽南语变调解析",
            "tone_copy": "了解变调如何构成闽南语词句的节奏，以及东宁音如何记录实际读音。",
            "tone_link": "阅读变调指南",
            "read_meta": "03 · 阅读",
            "read_title": "文学读物",
            "read_copy": "通过短篇小说与戏曲文学阅读闽南语，让读音紧贴原文。",
            "egg_kind": "短篇小说",
            "egg_title": "《卵》",
            "egg_note": "以闽南语呈现的哲思故事。",
            "mirror_kind": "古典文学",
            "mirror_title": "《荔镜记》",
            "mirror_note": "闽南戏曲传统的阅读版本。",
            "songs_meta": "04 · 聆听",
            "songs_title": "歌曲",
            "songs_copy": "从历久不衰的经典到新世代声音，阅读附有汉谚读音与罗马字的歌词。",
            "songs_link": "浏览歌本",
            "selection": "歌本选读",
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
        f'<a class="home-literature-work" href="{html.escape(language_url("/read/literature/lychee-mirror/", language), quote=True)}">'
        '<img src="/assets/content/wordpress/c9a8f25fedf3-naikiengki.png" alt="">'
        f'<span class="home-work-kind">{html.escape(labels["mirror_kind"])}</span>'
        f'<h3><ruby>荔鏡記<rt>내곙`기</rt></ruby> <span>{html.escape(labels["mirror_title"])}</span></h3>'
        f'<p>{html.escape(labels["mirror_note"])}</p></a></div>'
    )
    songs = (
        '<div class="home-songbook">'
        f'<span class="home-songbook-label">{html.escape(labels["selection"])}</span>'
        f'<a href="{html.escape(language_url("/songs/望春風/", language), quote=True)}"><span>望春風</span><small>Bang-chūn-hông</small></a>'
        f'<a href="{html.escape(language_url("/songs/金包銀/", language), quote=True)}"><span>金包銀</span><small>Kîm pāu-gín</small></a>'
        f'<a href="{html.escape(language_url("/songs/月下煮茶/", language), quote=True)}"><span>月下煮茶</span><small>Gueh-é j́-tê</small></a>'
        '</div>'
    )
    return (
        f'<section class="home-showcase" aria-label="{html.escape(labels["label"], quote=True)}">'
        '<div class="home-feature-pair">'
        '<article class="home-feature home-feature-learn">'
        f'<span class="home-feature-meta">{html.escape(labels["learn_meta"])}</span>'
        f'<h2>{html.escape(labels["learn_title"])}</h2><p>{html.escape(labels["learn_copy"])}</p>'
        f'{link("/learn/introduction/", labels["learn_link"])}</article>'
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


def curate_home_body(body, language):
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
    return introduction.rstrip() + home_showcase(language)


LEADING_LANGUAGE_SWITCHER = re.compile(
    r'^\s*<div class="wp-block-buttons[^"]*">\s*'
    r'(?:<div class="wp-block-button[^"]*">.*?</div>\s*)+</div>\s*',
    re.DOTALL,
)


def remove_leading_language_switcher(body):
    match = LEADING_LANGUAGE_SWITCHER.match(body)
    if match:
        targets = re.findall(r'href="([^"]+)"', match.group(0))
        language_roots = {"/", "/zh-hant/", "/zh-hans/", "https://hokkienlang.wordpress.com/zh-tw/", "https://hokkienlang.wordpress.com/zh-cn/"}
        if len(targets) >= 2 and all(target in language_roots for target in targets):
            return body[match.end():]
    return body


def introduce_tli(text):
    before, name, after = text.partition("Tangliengim")
    if not name:
        return text
    return before + "Tangliengim (TLI)" + after.replace("Tangliengim", "TLI")


def document(root, title, route, body, content_type="index", source_url=None, heading_html=None):
    language = language_for_route(route)
    navigation = navigation_links(route)
    source = f'<p class="source-link"><a data-site-text="Original WordPress page" href="{html.escape(source_url, quote=True)}">{text("Original WordPress page", language)}</a></p>' if source_url and base_route(route) != "/" else ""
    home_headings = {"en": "A written voice for Hokkien.", "zh-Hant": "閩南語的書寫之聲。", "zh-Hans": "闽南语的书写之声。"}
    home_introductions = {
        "en": "Tangliengim (TLI) brings pronunciation, tone, and meaning into one readable system.",
        "zh-Hant": "東寧音把發音、聲調與意義結合在一套易讀的系統中。",
        "zh-Hans": "东宁音把发音、声调与意义结合在一套易读的系统中。",
    }
    home_kickers = {"en": "Hokkien language · writing · culture", "zh-Hant": "閩南語 · 文字 · 文化", "zh-Hans": "闽南语 · 文字 · 文化"}
    heading = home_headings[language] if base_route(route) == "/" else title
    if language == "en" and base_route(route) != "/" and heading_html is None:
        heading = introduce_tli(heading)
    introduction = f'<p class="site-introduction">{home_introductions[language]}</p>' if base_route(route) == "/" else ""
    eyebrow = f'<p class="home-kicker">{home_kickers[language]}</p>' if base_route(route) == "/" else ""
    alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="https://thehokkienlang.github.io{html.escape(destination, quote=True)}">' for code in LANGUAGES if (destination := language_url(route, code)) is not None)
    template = (root / "apps/content-site/page.html").read_text(encoding="utf-8")
    section = base_route(route).strip("/").split("/")[0] or "home"
    values = {"LANG": language, "HOME": PREFIXES[language] + "/", "SKIP": text("Skip to content", language), "ALTERNATES": alternates, "TITLE": html.escape(title), "HEADING": heading_html if heading_html is not None else html.escape(heading), "INTRODUCTION": introduction, "EYEBROW": eyebrow, "ROUTE": html.escape(route, quote=True), "NAV": navigation, "BODY": body, "TYPE": content_type, "SOURCE": source, "SECTION": html.escape(section), "LAUNCH": home_launch(language) if section == "home" else ""}
    # One pass prevents source content resembling a placeholder from becoming executable template markup.
    return re.sub(r"__([A-Z]+)__", lambda match: values[match[1]], template)


def build_content(root: Path, output: Path):
    content = root / "content"
    if not content.exists():
        return []
    unpublished_routes = {"/songs/translation-notes/"}
    manifest = json.loads((root / "migration/wordpress-map.json").read_text(encoding="utf-8"))
    records = [
        json.loads((root / item["file"]).read_text(encoding="utf-8"))
        for item in manifest["records"]
        if item["route"] not in unpublished_routes
    ]
    source_routes = {source_key(item["sourceUrl"]): item["route"] for item in records}
    media = json.loads((root / "migration/wordpress-media.json").read_text(encoding="utf-8"))

    class PresentationHTML(ImportedHTML):
        def __init__(self, record):
            super().__init__(record["sourceUrl"], source_routes, media, root, False)
            self.language = record["language"]
            self.tli_introduced = self.language != "en" or "Tangliengim" in record["title"] or base_route(record["route"]) == "/"

        def rewrite(self, value, media=False):
            result = super().rewrite(value, media)
            if not media and self.language != "en" and result and result.startswith(("/songs/", "/dictionary/", "/ime/", "/read/literature/")) and "?" not in result:
                path, marker, fragment = result.partition("#")
                result = (language_url(path, self.language) or path) + (marker + fragment if marker else "")
            return result

        def handle_data(self, data):
            data = re.sub(r"(?<!The)\bHokkienLang\b", "TheHokkienLang", data)
            if self.language == "en" and "Tangliengim" in data:
                if self.tli_introduced:
                    data = data.replace("Tangliengim", "TLI")
                else:
                    data = introduce_tli(data)
                    self.tli_introduced = True
            super().handle_data(nasal_font_text(data))

    paths = set()
    for record in records:
        route = record["route"]
        target = output / route.lstrip("/") / "index.html"
        if not route.startswith("/") or not route.endswith("/") or not target.resolve().is_relative_to(output.resolve()) or route in paths:
            raise ValueError(f"Invalid or duplicate content route: {route}")
        paths.add(route)
        target.parent.mkdir(parents=True, exist_ok=True)
        heading_html, body = song_title(record) if record["type"] == "songs" else (None, record["body"])
        body = PresentationHTML(record).render(remove_leading_language_switcher(body))
        if base_route(route) == "/":
            body = curate_home_body(body, record["language"])
        target.write_text(document(root, record["title"], route, body, record["type"], record["sourceUrl"], heading_html), encoding="utf-8")
    def listing(items):
        return '<ul class="page-list">' + "".join(f'<li><a class="title-reading" href="{html.escape(item["route"], quote=True)}">{html.escape(item["title"].replace("Tangliengim", "TLI"))}</a></li>' for item in items) + "</ul>"
    song_rows = json.loads((root / "migration/song-urls.json").read_text(encoding="utf-8"))
    song_categories = json.loads((root / "content/song-categories.json").read_text(encoding="utf-8"))
    songs_by_route = {item["route"]: item for item in records if item["type"] == "songs"}
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
        outside_ruby = html.unescape(re.sub(r"<ruby\b.*?</ruby>", "", label, flags=re.DOTALL))
        sort_reading = song_sort_reading(imported)
        song_items[route] = {
            "label": label,
            "lomari": song_lomari(imported),
            "ruby_only": not any(character.isalnum() for character in outside_ruby),
            "sort": (not bool(sort_reading), reading_sort_key(sort_reading)),
        }

    def song_index(language):
        sections = []
        for category in song_categories:
            items = sorted(category["routes"], key=lambda route: (song_items[route]["sort"], route))
            links = []
            for route in items:
                destination = language_url(route, language) or route
                item = song_items[route]
                entry_class = "title-reading song-entry" + (" song-entry--ruby-only" if item["ruby_only"] else "")
                links.append(
                    f'<li><a class="{entry_class}" '
                    f'href="{html.escape(destination, quote=True)}">'
                    f'<span class="song-entry-title">{item["label"]}</span>'
                    f'<span class="song-entry-lomari">{html.escape(item["lomari"])}</span>'
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
        return '<div class="song-catalogue">' + "".join(sections) + '</div>'
    sections = {}
    languages = manifest.get("languages", ["en"])
    for language in languages:
        prefix = PREFIXES[language]
        guides = [item for item in records if item["type"] == "guides" and item["language"] == language and base_route(item["route"]).startswith("/learn/")]
        story_language = "zh-Hant" if language == "zh-Hans" else language
        stories = [{**item, "title": text("The Egg", language)} for item in records if item["type"] == "stories" and item["language"] == story_language]
        literature = [{**item, "route": language_url(item["route"], language), "title": text("Tale of the Lychee Mirror", language)} for item in records if item["type"] == "literature"]
        sections[prefix + "/learn/"] = (text("Learn Tangliengim", language), listing(guides))
        sections[prefix + "/read/"] = (text("Read in Hokkien", language), f'<h2>{text("Literature", language)}</h2>' + listing(literature) + f'<h2>{text("Stories", language)}</h2>' + listing(stories))
        sections[prefix + "/songs/"] = (text("Songs", language), song_index(language))
    for route, (title, body) in sections.items():
        target = output / route.lstrip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document(root, title, route, body), encoding="utf-8")
        paths.add(route)
    target = output / "assets/content-site"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("site.css", "site.js"):
        shutil.copy2(root / "apps/content-site" / name, target / name)
    (output / "content-manifest.json").write_text(json.dumps({"language": "en", "languages": languages, "routes": sorted(paths), "pages": [{key: item[key] for key in ("title", "route", "language", "type", "sourceId", "sourceUrl", "orthography")} for item in records], "deferred": manifest["deferred"]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return sorted(paths)
