"""Build deterministic, text-only search documents from published content."""

from __future__ import annotations

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
