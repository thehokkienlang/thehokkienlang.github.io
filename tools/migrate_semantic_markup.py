"""Move hand-positioned WordPress markup to semantic HTML and shared CSS (audit B4).

Rewrites the page bodies in content/ so that:

- every <ruby> and <rt> is plain semantic markup: inline styles are dropped and
  only title, lang and class attributes are kept. Readings and standalone tone
  marks are positioned by shared/web-ruby.css (site.js turns them into
  .tli-reading-ruby and .tli-tone-ruby boxes);
- the lyric line and Lomari line spans use the lyric-line / lyric-lomari classes;
- table cells' inline colours, sizes and alignment become cell-* classes.

Only markup changes. The check run with every migration confirms that each
page's visible text, and every ruby's base, reading and title, are unchanged.
Run it again at any time: already-migrated markup is left as it is.

    python tools/migrate_semantic_markup.py           # rewrite content/
    python tools/migrate_semantic_markup.py --check   # report what would change
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

RUBY_OPEN = re.compile(r"<ruby\b([^>]*)>", re.I)
RT_OPEN = re.compile(r"<rt\b([^>]*)>", re.I)
KEPT_ATTRIBUTES = re.compile(r'\s(title|lang|class)="[^"]*"', re.I)
STYLED_TAG = re.compile(r'<(span|td|th|p|a)\b([^>]*?)\sstyle="([^"]*)"([^>]*)>', re.I)

LYRIC_CLASSES = (
    ({"display": "block", "font-size": "1em"}, "lyric-line"),
    ({"display": "block", "font-size": "1em", "color": "gray"}, "lyric-line lyric-muted"),
    ({"display": "block", "font-size": "0.7em", "color": "gray", "margin-top": "-5px", "font-family": "calibri"}, "lyric-lomari"),
    ({"display": "block", "font-size": "0.7em", "margin-top": "-5px", "font-family": "calibri"}, "lyric-lomari lyric-lomari-ink"),
)
# Paragraphs, spans and links: whole-signature matches. "" drops a style the site
# overrides anyway (site.css forces its own font stack over Sans-serif).
TEXT_CLASSES = (
    ({"font-family": "sans-serif, noto sans"}, ""),
    ({"font-family": "sans-serif, noto sans", "text-indent": "2em"}, "indent-2em"),
    ({"color": "var(--wp--preset--color--primary)", "text-decoration": "underline dotted", "cursor": "help"}, "gloss-link"),
    ({"color": "var(--wp--preset--color--primary)", "text-decoration": "underline dotted", "cursor": "help",
      "white-space": "nowrap"}, "gloss-link gloss-link-nowrap"),
)
# Table-cell utilities: every declaration must map, or the cell keeps its inline style.
CELL_CLASSES = {
    ("background-color", "#18375d"): "cell-navy", ("background-color", "#d6c9fe"): "cell-lavender",
    ("background-color", "#fadbd8"): "cell-rose", ("background-color", "#fdf2e9"): "cell-peach",
    ("background-color", "#fef5e7"): "cell-sand", ("background-color", "#fef9e7"): "cell-cream",
    ("background-color", "#ffffff"): "cell-white", ("color", "#e0feca"): "cell-text-mint",
    ("font-size", "0.8em"): "cell-fs-80", ("font-size", "80%"): "cell-fs-80",
    ("font-size", "0.9em"): "cell-fs-90", ("font-size", "90%"): "cell-fs-90",
    ("font-size", "1.1em"): "cell-fs-110", ("font-size", "120%"): "cell-fs-120",
    ("font-size", "220%"): "cell-fs-220", ("font-weight", "bold"): "cell-bold",
    ("height", "8em"): "cell-h-8em", ("text-align", "center"): "cell-center", ("width", "25%"): "cell-w-25",
    # Overridden by the site's font stack anyway (site.css), so it maps to no class.
    ("font-family", "sans-serif, noto sans"): "",
}


def declarations(style: str) -> dict[str, str]:
    result = {}
    for item in style.split(";"):
        key, _, value = item.partition(":")
        if key.strip():
            result[key.strip().lower()] = re.sub(r"\s+", " ", value.strip().lower())
    return result


def _kept(attributes: str) -> str:
    return "".join(match.group(0) for match in KEPT_ATTRIBUTES.finditer(attributes))


def _with_class(before: str, after: str, classes: str) -> str:
    attributes = before + after
    existing = re.search(r'\sclass="([^"]*)"', attributes)
    if existing:
        merged = " ".join(dict.fromkeys(existing.group(1).split() + classes.split()))
        return attributes[:existing.start()] + f' class="{merged}"' + attributes[existing.end():]
    return f' class="{classes}"' + attributes


# Ruby declarations the shared CSS already provides or overrides (positioning, fonts).
RUBY_POSITIONAL = {"position", "white-space", "font-family", "vertical-align", "line-height", "text-indent",
                   "isolation", "display"}
# Ruby declarations that carry meaning: the teaching boxes on the tone-sandhi pages.
RUBY_CLASSES = (
    ({("background", "#ffffff"), ("border", "1px solid #e3e3e3")}, "ruby-box-white"),
    ({("background", "#d6c9fe")}, "ruby-box-lavender"),
    ({("top", "-0.14em")}, "ruby-nudge-up"),
)


def _ruby_open(match: re.Match) -> str:
    attributes = match.group(1)
    style = re.search(r'\sstyle="([^"]*)"', attributes)
    meaningful = {(key, value) for key, value in declarations(style.group(1) if style else "").items()
                  if key not in RUBY_POSITIONAL}
    classes = []
    for signature, name in RUBY_CLASSES:
        if signature <= meaningful:
            classes.append(name)
            meaningful -= signature
    kept = _kept(attributes)
    if classes:
        kept = _with_class(kept, "", " ".join(classes))
    if meaningful:  # anything unrecognised stays inline rather than being lost
        kept += ' style="' + ";".join(f"{key}: {value}" for key, value in sorted(meaningful)) + '"'
    return f"<ruby{kept}>"


def migrate_body(body: str) -> str:
    body = RUBY_OPEN.sub(_ruby_open, body)
    body = RT_OPEN.sub(lambda match: f"<rt{_kept(match.group(1))}>", body)

    def styled(match: re.Match) -> str:
        tag, before, style, after = match.groups()
        decl = declarations(style)
        if tag.lower() in ("span", "p", "a"):
            for signature, classes in (LYRIC_CLASSES if tag.lower() == "span" else ()) + TEXT_CLASSES:
                if decl == signature:
                    return f"<{tag}{_with_class(before, after, classes)}>" if classes else f"<{tag}{before}{after}>"
            return match.group(0)
        if "background-color" not in decl or not all((key, value) in CELL_CLASSES for key, value in decl.items()):
            return match.group(0)
        classes = " ".join(dict.fromkeys(c for key, value in decl.items() if (c := CELL_CLASSES[(key, value)])))
        return f"<{tag}{_with_class(before, after, classes)}>" if classes else f"<{tag}{before}{after}>"

    return STYLED_TAG.sub(styled, body)


# ----- verification: only markup may change -----
_RUBY = re.compile(r"<ruby\b[^>]*>(.*?)</ruby>", re.S | re.I)
_RT = re.compile(r"<rt\b[^>]*>(.*?)</rt>", re.S | re.I)
_TITLE = re.compile(r'<ruby\b[^>]*\stitle="([^"]*)"', re.I)


def _text(markup: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", markup))


def ruby_units(body: str) -> list[tuple[str, str, str]]:
    units = []
    for match in _RUBY.finditer(body):
        title = _TITLE.match(match.group(0))
        units.append((_text(_RT.sub("", match.group(1))), "|".join(_text(r) for r in _RT.findall(match.group(1))),
                      title.group(1) if title else ""))
    return units


def assert_same_content(before: str, after: str, name: str) -> None:
    if _text(before) != _text(after):
        raise AssertionError(f"{name}: visible text changed")
    if ruby_units(before) != ruby_units(after):
        raise AssertionError(f"{name}: a ruby's base, reading or title changed")


def content_files():
    for path in sorted(CONTENT.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("body"), str):
            yield path, data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="report pages that would change; write nothing")
    args = parser.parse_args()
    changed = []
    for path, data in content_files():
        body = migrate_body(data["body"])
        if body == data["body"]:
            continue
        assert_same_content(data["body"], body, path.relative_to(ROOT).as_posix())
        changed.append(path)
        if not args.check:
            raw = path.read_bytes().decode("utf-8")
            newline = "\r\n" if "\r\n" in raw else "\n"
            data["body"] = body
            text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            path.write_bytes(text.replace("\n", newline).encode("utf-8"))
    verb = "would change" if args.check else "migrated"
    print(f"{verb} {len(changed)} pages; visible text and every ruby's base, reading and title unchanged.")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
