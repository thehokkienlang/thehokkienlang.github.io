"""Move source song-header readings into the approved mixed-script title."""

from __future__ import annotations

import html
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from functools import cache
from html.parser import HTMLParser

from build_dictionary_json import load_tone_marker_module
from tangliengim_collation import TONE_TO_DIGIT

UPPER_TONES = str.maketrans({"1": "ˆ", "2": "ˋ", "3": "", "4": "ˊ", "5": "ˉ"})
VOID = {"br", "img", "hr", "wbr"}


@cache
def phonetics():
    return sys.modules.get("tangliengim_tone_marker") or load_tone_marker_module()


@dataclass
class Node:
    tag: str
    children: list = field(default_factory=list)

    def reading(self):
        if self.tag == "ruby":
            base = "".join(child if isinstance(child, str) else child.reading()
                           for child in self.children if not isinstance(child, Node) or child.tag not in {"rt", "rp"})
            annotation = "".join(child.reading() for child in self.children
                                 if isinstance(child, Node) and child.tag == "rt")
            return annotation if reading_units(annotation) else base + annotation
        return "".join(child if isinstance(child, str) else child.reading()
                       for child in self.children if not isinstance(child, Node) or child.tag != "rp")


class FirstHeading(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.line_starts = [0] + [match.end() for match in re.finditer("\n", body)]
        self.root = None
        self.stack = []
        self.start = self.end = None
        self.feed(body)

    def source_offset(self):
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if self.end is not None:
            return
        if not self.stack:
            if tag not in {"h1", "h2", "h3"}:
                return
            self.root = Node(tag)
            self.stack = [self.root]
            self.start = self.source_offset()
            return
        node = Node(tag)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1].tag == tag:
            self.stack.pop()
            if not self.stack:
                self.end = self.source_offset() + len(f"</{tag}>")

    def handle_data(self, data):
        if self.stack:
            self.stack[-1].children.append(data)


def reading_units(text):
    units = []
    index = 0
    while index < len(text):
        unit = phonetics().hangul_reading_unit_at(text, index)
        if unit:
            value, index = unit
            units.append(value.translate(TONE_TO_DIGIT).translate(UPPER_TONES))
        else:
            index += 1
    return units


def title_units(title):
    units = []
    index = 0
    while index < len(title):
        if phonetics().is_cjk_char(title[index]):
            units.append((index, index + 1, title[index], True))
            index += 1
        elif unit := phonetics().hangul_reading_unit_at(title, index):
            value, end = unit
            units.append((index, end, value, False))
            index = end
        else:
            index += 1
    return units


def bare_unit(value):
    return unicodedata.normalize("NFC", value.translate(TONE_TO_DIGIT).rstrip("12345"))


def ruby(base, readings, system="hangul"):
    css = "hanri-title" + (" bopomofo-title" if system == "bopomofo" else "")
    readings = list(dict.fromkeys(readings))
    return f'<ruby class="{css}">{html.escape(base)}<rt>{html.escape(" / ".join(readings))}</rt></ruby>'


def song_title(record):
    title, body = record["title"], record["body"]
    if annotations := record.get("titleRuby"):
        if "".join(item["base"] for item in annotations) != title:
            raise ValueError(f'Explicit title ruby does not match {record["id"]}')
        return "".join(ruby(item["base"], [item["reading"]], item.get("system", "hangul"))
                       for item in annotations), body

    heading = FirstHeading(body)
    reading = heading.root.reading().strip() if heading.root else ""
    if heading.end is None or not reading_units(reading):
        raise ValueError(f'No title reading available for {record["id"]}')
    variants = [part.strip(" )）") for part in re.split(r"[（(]", reading) if part.strip(" )）")]
    if "titleReadingVariant" in record:
        selected = record["titleReadingVariant"]
        if not isinstance(selected, int) or not 0 <= selected < len(variants):
            raise ValueError(f'Invalid title reading selection for {record["id"]}')
        variants = [variants[selected]]
    units = title_units(title)
    aligned = []
    for variant in variants:
        readings = reading_units(variant)
        skipped = 0
        # A Latin source prefix such as Happy!!! is already Hangul in the new title.
        if len(readings) < len(units) and re.match(r"[A-Za-z]", variant):
            skipped = next((index for index, unit in enumerate(units) if unit[3]), 0)
        if len(readings) != len(units) - skipped:
            raise ValueError(f'Title/header syllable count differs for {record["id"]}: {variant}')
        for (_, _, base, is_hanri), spoken in zip(units[skipped:], readings):
            if not is_hanri and bare_unit(base) != bare_unit(spoken):
                raise ValueError(f'Title/header Hangul differs for {record["id"]}: {base} / {spoken}')
        aligned.append(dict(zip((unit[0] for unit in units[skipped:]), readings)))

    result = []
    index = 0
    while index < len(title):
        if not phonetics().is_cjk_char(title[index]):
            result.append(html.escape(title[index]))
            index += 1
            continue
        result.append(ruby(title[index], [readings[index] for readings in aligned]))
        index += 1
    return "".join(result), body[:heading.start] + body[heading.end:]
