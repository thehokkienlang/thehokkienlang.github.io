"""Recover structured TLI authoring data from legacy generated song HTML."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser


VOID_ELEMENTS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


@dataclass
class HtmlNode:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["HtmlNode | str"] = field(default_factory=list)


class FragmentParser(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.root = HtmlNode("document")
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = HtmlNode(tag.lower(), {key.lower(): value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        if node.tag not in VOID_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack[-1].tag == tag.lower() and tag.lower() not in VOID_ELEMENTS:
            self.stack.pop()

    def handle_endtag(self, tag):
        lowered = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == lowered:
                del self.stack[index:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _is_cjk(character: str) -> bool:
    point = ord(character)
    return (
        0x3400 <= point <= 0x4DBF
        or 0x4E00 <= point <= 0x9FFF
        or 0x20000 <= point <= 0x2FA1F
        or point == 0x3007
    )


def _is_hangul(character: str) -> bool:
    point = ord(character)
    return 0x1100 <= point <= 0x11FF or 0x3130 <= point <= 0x318F or 0xAC00 <= point <= 0xD7AF


def _plain_text(node: HtmlNode, *, skip=frozenset()) -> str:
    if node.tag in skip:
        return ""
    return "".join(child if isinstance(child, str) else _plain_text(child, skip=skip) for child in node.children)


def _is_footnote_link(node: HtmlNode) -> bool:
    return node.tag == "a" and node.attrs.get("href", "").startswith("#_ftn")


def _source(node: HtmlNode) -> str:
    if node.tag in {"script", "style", "rt", "rp"} or _is_footnote_link(node):
        return ""
    if node.tag == "ruby":
        base = "".join(
            child if isinstance(child, str) else _plain_text(child, skip={"rt", "rp"})
            for child in node.children
            if isinstance(child, str) or child.tag not in {"rt", "rp"}
        )
        reading = "".join(
            _plain_text(child) for child in node.children
            if isinstance(child, HtmlNode) and child.tag == "rt"
        )
        if reading and any(_is_cjk(char) for char in base):
            return f"[{base}{reading}]"
        if reading and not any(_is_hangul(char) for char in base):
            return reading
        return base + reading
    return "".join(child if isinstance(child, str) else _source(child) for child in node.children)


def fragment_source(source: str) -> str:
    """Turn generated ruby markup back into the editor's bracketed TLI notation."""
    value = _source(FragmentParser(source).root)
    return re.sub(r"\s+", " ", value).strip()


def title_segments(source: str) -> list[dict]:
    """Represent generated title ruby as validated text/base/reading segments."""
    segments: list[dict] = []

    def append_text(value: str):
        if not value:
            return
        if segments and "text" in segments[-1]:
            segments[-1]["text"] += value
        else:
            segments.append({"text": value})

    def walk(node: HtmlNode):
        if node.tag == "ruby":
            base = "".join(
                child if isinstance(child, str) else _plain_text(child, skip={"rt", "rp"})
                for child in node.children
                if isinstance(child, str) or child.tag not in {"rt", "rp"}
            )
            reading = "".join(
                _plain_text(child) for child in node.children
                if isinstance(child, HtmlNode) and child.tag == "rt"
            )
            classes = _classes(node)
            segments.append({
                "base": base,
                "reading": reading,
                "system": "bopomofo" if "bopomofo-title" in classes else "hangul",
            })
            return
        if node.tag in {"rt", "rp", "script", "style"}:
            return
        for child in node.children:
            if isinstance(child, str):
                append_text(child)
            else:
                walk(child)

    walk(FragmentParser(source).root)
    return segments


def _classes(node: HtmlNode) -> set[str]:
    return set(node.attrs.get("class", "").split())


SIZED_LYRIC_STYLE = re.compile(r"display:\s*block;\s*font-size:\s*[\d.]+em", re.IGNORECASE)


def _is_lyric_line(node: HtmlNode) -> bool:
    """A lyric line has the lyric-line class, or an inline size on the few lines tuned by hand."""
    style = node.attrs.get("style", "")
    return "lyric-line" in _classes(node) or bool(SIZED_LYRIC_STYLE.search(style) and "calibri" not in style.lower())


def legacy_lyrics(body: str) -> list[dict]:
    """Recover lyric lines and section breaks in document order."""
    events: list[tuple[str, HtmlNode | None]] = []

    def walk(node: HtmlNode):
        if node.tag == "span" and _is_lyric_line(node):
            events.append(("line", node))
            return
        if node.tag == "br":
            events.append(("break", None))
            return
        for child in node.children:
            if isinstance(child, HtmlNode):
                walk(child)

    walk(FragmentParser(body).root)
    lyrics: list[dict] = []
    pending_break = False
    for kind, node in events:
        if kind == "break":
            if lyrics:
                pending_break = True
            continue
        if pending_break and lyrics and lyrics[-1].get("kind") != "break":
            lyrics.append({"kind": "break"})
        pending_break = False
        grey = "lyric-muted" in _classes(node)
        text = re.sub(r"\s+", " ", _source(node)).strip()
        if grey and text.startswith("(") and text.endswith(")"):
            text = text[1:-1].strip()
        if text:
            lyrics.append({"kind": "line", "text": text, "grey": grey})
    return lyrics


def legacy_suffix(body: str) -> str:
    """Preserve notes and other material that follows the final lyric paragraph."""
    lyric_paragraph = re.compile(
        r'<p\b[^>]*>(?:(?!</p>).)*'
        r'(?:class=["\'][^"\']*\blyric-line\b[^"\']*["\']|style=["\']display:\s*block;\s*font-size:\s*[\d.]+em)'
        r'(?:(?!</p>).)*</p>',
        re.IGNORECASE | re.DOTALL,
    )
    matches = list(lyric_paragraph.finditer(body))
    if not matches:
        return ""
    suffix = body[matches[-1].end():]
    suffix = re.sub(r"^(?:\s*<br\s*/?>)+", "", suffix, flags=re.IGNORECASE)
    return suffix if suffix.strip() else ""
