"""Build deterministic, text-only search documents from published content."""

from __future__ import annotations

import html
import re
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path

from simplified_lookup import converter


SPACE = re.compile(r"\s+")


@lru_cache(maxsize=1)
def hanri_fold_map():
    """Use the pinned dictionary's character conversions as symmetric search keys."""
    directory = Path(__file__).resolve().parent / 'vendor/opencc/dictionary'
    characters = set()
    for filename in ('TSCharacters.txt', 'TWVariantsRev.txt'):
        for line in (directory / filename).read_text(encoding='utf-8').splitlines():
            key = line.split('\t', 1)[0]
            if len(key) == 1:
                characters.add(key)
    convert = converter('tw2s').convert
    return {char: value for char in sorted(characters)
            if (value := convert(char)) != char and len(value) == 1}


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "template", "noscript"}:
            self.hidden.append(tag)
        elif tag in {"br", "p", "h1", "h2", "h3", "h4", "li", "td", "th", "figcaption"}:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if self.hidden and self.hidden[-1] == tag:
            self.hidden.pop()
        elif tag in {"p", "h1", "h2", "h3", "h4", "li", "td", "th", "figcaption"}:
            self.parts.append(" ")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def visible_text(markup: str) -> str:
    parser = VisibleText()
    parser.feed(markup)
    parser.close()
    return SPACE.sub(" ", "".join(parser.parts)).strip()


class LyricText(HTMLParser):
    """Extract authored lyric and Lomari lines without indexing page chrome or notes."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines = []
        self.current = None
        self.pending_main = None
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if self.current is not None:
            self.stack.append(tag)
            if self.current["kind"] == "main" and tag in {"ruby", "rt"}:
                self.current["html"].append(f"<{tag}>")
            return
        if tag == "span":
            classes = set(dict(attrs).get("class", "").split())
            kind = "main" if "lyric-line" in classes else "lomari" if "lyric-lomari" in classes else None
            if kind:
                self.current = {"kind": kind, "search": [], "display": [], "html": []}
                self.stack = [tag]

    def handle_endtag(self, tag):
        if self.current is None:
            return
        if len(self.stack) == 1:
            search = SPACE.sub(" ", "".join(self.current["search"])).strip()
            display = SPACE.sub(" ", "".join(self.current["display"])).strip()
            if self.current["kind"] == "main":
                self.pending_main = {
                    "main": display,
                    "mainHtml": "".join(self.current["html"]).strip(),
                    "lomari": "",
                    "search": search,
                }
            elif self.pending_main:
                self.pending_main["lomari"] = display
                self.pending_main["search"] = SPACE.sub(" ", f'{self.pending_main["search"]} {search}').strip()
                self.lines.append(self.pending_main)
                self.pending_main = None
            self.current = None
            self.stack = []
            return
        if self.current["kind"] == "main" and tag in {"ruby", "rt"}:
            self.current["html"].append(f"</{tag}>")
        if tag in self.stack:
            self.stack = self.stack[:len(self.stack) - 1 - self.stack[::-1].index(tag)]

    def handle_data(self, data):
        if self.current is not None:
            self.current["search"].append(data)
            if self.current["kind"] == "main":
                self.current["html"].append(html.escape(data))
            if self.current["kind"] == "lomari" or not {"rt", "rp"} & set(self.stack):
                self.current["display"].append(data)


def lyric_lines(markup: str) -> list[dict[str, str]]:
    parser = LyricText()
    parser.feed(markup)
    parser.close()
    return parser.lines


def lyric_text(markup: str) -> str:
    return " ".join(line["search"] for line in lyric_lines(markup))


def document(identity: str, title: str, url: str, kind: str, heading: str, body: str) -> dict:
    title_reading = visible_text(heading) if heading else ""
    content = visible_text(body)
    return {
        "id": identity,
        "title": title,
        "url": url,
        "kind": kind,
        "titleSearch": SPACE.sub(" ", f"{title} {title_reading}").strip(),
        "content": content,
    }
