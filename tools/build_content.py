"""Render authored English and Chinese content into the Pages artifact."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

from song_title_readings import song_title, word_title
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


def document(root, title, route, body, content_type="index", source_url=None, heading_html=None):
    language = language_for_route(route)
    navigation = navigation_links(route)
    source = f'<p class="source-link"><a data-site-text="Original WordPress page" href="{html.escape(source_url, quote=True)}">{text("Original WordPress page", language)}</a></p>' if source_url else ""
    tools = f'<aside class="reading-tools" aria-label="Reading tools"><a id="lookup-link" data-site-text="Dictionary" href="{language_url("/dictionary/", language)}">{text("Dictionary", language)}</a><a id="ime-link" data-site-text="Open IME" href="{language_url("/ime/", language)}">{text("Open IME", language)}</a></aside>'
    heading = "TheHokkienLang" if base_route(route) == "/" else title
    introductions = {"en": "Explore Hokkien with", "zh-Hant": "透過以下系統探索閩南語：", "zh-Hans": "通过以下系统探索闽南语："}
    introduction = f'<p class="site-introduction">{introductions[language]} <a href="{language_url("/learn/introduction/", language)}">TLI (Tangliengim)</a>.</p>' if base_route(route) == "/" else ""
    alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="https://thehokkienlang.github.io{html.escape(destination, quote=True)}">' for code in LANGUAGES if (destination := language_url(route, code)) is not None)
    template = (root / "apps/content-site/page.html").read_text(encoding="utf-8")
    values = {"LANG": language, "HOME": PREFIXES[language] + "/", "SKIP": text("Skip to content", language), "ALTERNATES": alternates, "TITLE": html.escape(title), "HEADING": heading_html if heading_html is not None else html.escape(heading), "INTRODUCTION": introduction, "ROUTE": html.escape(route, quote=True), "NAV": navigation, "BODY": body, "TYPE": content_type, "SOURCE": source, "TOOLS": tools}
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

        def rewrite(self, value, media=False):
            result = super().rewrite(value, media)
            if not media and self.language != "en" and result and result.startswith(("/songs/", "/dictionary/", "/ime/", "/read/literature/")) and "?" not in result:
                path, marker, fragment = result.partition("#")
                result = (language_url(path, self.language) or path) + (marker + fragment if marker else "")
            return result

        def handle_data(self, data):
            super().handle_data(nasal_font_text(re.sub(r"(?<!The)\bHokkienLang\b", "TheHokkienLang", data)))

    paths = set()
    for record in records:
        route = record["route"]
        target = output / route.lstrip("/") / "index.html"
        if not route.startswith("/") or not route.endswith("/") or not target.resolve().is_relative_to(output.resolve()) or route in paths:
            raise ValueError(f"Invalid or duplicate content route: {route}")
        paths.add(route)
        target.parent.mkdir(parents=True, exist_ok=True)
        heading_html, body = song_title(record) if record["type"] == "songs" else (None, record["body"])
        body = PresentationHTML(record).render(body)
        target.write_text(document(root, record["title"], route, body, record["type"], record["sourceUrl"], heading_html), encoding="utf-8")
    def listing(items):
        return '<ul class="page-list">' + "".join(f'<li><a class="title-reading" href="{html.escape(item["route"], quote=True)}">{html.escape(item["title"])}</a></li>' for item in items) + "</ul>"
    song_rows = json.loads((root / "migration/song-urls.json").read_text(encoding="utf-8"))
    source_titles = json.loads((root / "migration/song-titles.json").read_text(encoding="utf-8"))
    songs_by_route = {item["route"]: item for item in records if item["type"] == "songs"}
    song_links = []
    for row in song_rows:
        imported = songs_by_route.get(row["new_url"])
        if imported:
            title = row.get("display_title") or imported["title"]
            label = word_title(title, imported.get("titleWordReadings", {}))
            song_links.append(f'<li><a class="title-reading" href="{html.escape(imported["route"], quote=True)}">{label}</a></li>')
        else:
            song_links.append(f'<li><a href="{html.escape(row["old_url"], quote=True)}">{html.escape(source_titles[row["old_url"]])}</a><span class="external-note">WordPress</span></li>')
    sections = {}
    languages = manifest.get("languages", ["en"])
    for language in languages:
        prefix = PREFIXES[language]
        guides = [item for item in records if item["type"] == "guides" and item["language"] == language and base_route(item["route"]).startswith("/learn/")]
        story_language = "zh-Hant" if language == "zh-Hans" else language
        stories = [{**item, "title": text("The Egg", language)} for item in records if item["type"] == "stories" and item["language"] == story_language]
        literature = [{**item, "route": language_url(item["route"], language), "title": text("Tale of the Lychee Mirror", language)} for item in records if item["type"] == "literature"]
        localized_songs = "".join(song_links)
        if language != "en":
            localized_songs = re.sub(r'href="(/songs/[^"?]+/)"', lambda match: f'href="{html.escape(language_url(match[1], language), quote=True)}"', localized_songs)
        sections[prefix + "/learn/"] = (text("Learn Tangliengim", language), listing(guides))
        sections[prefix + "/read/"] = (text("Read in Hokkien", language), f'<h2>{text("Literature", language)}</h2>' + listing(literature) + f'<h2>{text("Stories", language)}</h2>' + listing(stories))
        sections[prefix + "/songs/"] = (text("Songs", language), '<ul class="page-list song-list">' + localized_songs + "</ul>")
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
