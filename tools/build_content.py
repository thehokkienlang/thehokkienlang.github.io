"""Render imported English content into the existing GitHub Pages artifact."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

from song_title_readings import song_title, word_title

NAV = (("/", "Home"), ("/learn/", "Learn"), ("/songs/", "Songs"), ("/read/", "Read"), ("/dictionary/", "Dictionary"), ("/ime/", "IME"), ("/about/", "About"))
NAV_SECTIONS = {
    "/learn/": (("/learn/introduction/", "Introduction"), ("/learn/spelling/", "Spelling"), ("/learn/tone-sandhi/", "Tone sandhi"), ("/learn/romanisation/", "Romanisation")),
    "/read/": (("/read/stories/the-egg/", "The Egg"), ("/read/literature/lychee-mirror/", "Tale of the Lychee Mirror")),
}


def navigation_links(route):
    def link(href, label):
        current = ' aria-current="page"' if route == href or href != "/" and route.startswith(href) else ""
        return f'<a href="{href}"{current}>{html.escape(label)}</a>'

    items = []
    for href, label in NAV:
        if href in NAV_SECTIONS:
            active = " is-current" if route.startswith(href) else ""
            children = "".join(link(path, title) for path, title in NAV_SECTIONS[href])
            items.append(
                '<details class="site-nav-dropdown" name="site-navigation">'
                f'<summary class="site-nav-trigger{active}">{label}</summary>'
                f'<div class="site-nav-panel">{children}</div></details>'
            )
        else:
            items.append(link(href, label))
    return "".join(items)


def document(root, title, route, body, content_type="index", source_url=None, heading_html=None):
    navigation = navigation_links(route)
    source = f'<p class="source-link"><a href="{html.escape(source_url, quote=True)}">Original WordPress page</a></p>' if source_url else ""
    tools = '<aside class="reading-tools" aria-label="Reading tools"><a id="lookup-link" href="/dictionary/">Dictionary</a><a id="ime-link" href="/ime/">Open IME</a></aside>'
    heading = "TheHokkienLang" if route == "/" else title
    introduction = '<p class="site-introduction">Explore Hokkien with <a href="/learn/introduction/">TLI (Tangliengim)</a>.</p>' if route == "/" else ""
    template = (root / "apps/content-site/page.html").read_text(encoding="utf-8")
    values = {"TITLE": html.escape(title), "HEADING": heading_html if heading_html is not None else html.escape(heading), "INTRODUCTION": introduction, "ROUTE": html.escape(route, quote=True), "NAV": navigation, "BODY": body, "TYPE": content_type, "SOURCE": source, "TOOLS": tools}
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
    paths = set()
    for record in records:
        route = record["route"]
        target = output / route.lstrip("/") / "index.html"
        if not route.startswith("/") or not route.endswith("/") or not target.resolve().is_relative_to(output.resolve()) or route in paths:
            raise ValueError(f"Invalid or duplicate content route: {route}")
        paths.add(route)
        target.parent.mkdir(parents=True, exist_ok=True)
        heading_html, body = song_title(record) if record["type"] == "songs" else (None, record["body"])
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
    stories = [item for item in records if item["type"] == "stories"]
    sections = {
        "/learn/": ("Learn Tangliengim", listing([item for item in records if item["route"].startswith("/learn/")])),
        "/read/": ("Read in Hokkien", '<h2>Literature</h2>' + listing([item for item in records if item["type"] == "literature"]) + '<h2>Stories</h2>' + (listing(stories) if stories else '<p><a href="https://hokkienlang.wordpress.com/2025/01/26/the-egg/">The Egg</a> is available on WordPress.</p>')),
        "/songs/": ("Songs", '<ul class="page-list song-list">' + "".join(song_links) + "</ul>"),
    }
    for route, (title, body) in sections.items():
        target = output / route.lstrip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document(root, title, route, body), encoding="utf-8")
        paths.add(route)
    target = output / "assets/content-site"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("site.css", "site.js"):
        shutil.copy2(root / "apps/content-site" / name, target / name)
    (output / "content-manifest.json").write_text(json.dumps({"language": "en", "routes": sorted(paths), "pages": [{key: item[key] for key in ("title", "route", "type", "sourceId", "sourceUrl", "orthography")} for item in records], "deferred": manifest["deferred"]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return sorted(paths)
