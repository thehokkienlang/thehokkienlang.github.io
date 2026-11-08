"""Keep every Lomari line tied to the Hokkien (Hanri-Hangul) text above it (audit B7).

A lyric's Lomari line is derived from the Hangul readings of the line above it,
with the same converter the IME and the desktop exporter use
(auto_lomari_from_hangul). The home page's song buttons take their Lomari from
the song's own title reading (song_title_readings.song_lomari), as the song pages do.

The release gate runs --check: a line whose stored Lomari differs from its
Hangul fails, unless it is listed in docs/lomari-review.json, the lines waiting
for Haru's review. After editing Hangul, run --fix to rewrite the Lomari lines
from it. Lines under review are never rewritten.

    python tools/lomari_sync.py                      # same as --check
    python tools/lomari_sync.py --fix                # rewrite drifted Lomari from the Hangul
    python tools/lomari_sync.py --write-review       # record today's differences for review

Not tied: Mandarin lines (no Hangul, or bopomofo readings) and 荔鏡記, whose
Lomari uses an older nasal convention (left for later by decision).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from song_title_readings import phonetics, song_lomari  # noqa: E402

CONTENT = ROOT / "content"
REVIEW = ROOT / "docs" / "lomari-review.json"
EXCLUDED = {"content/literature/lychee-mirror.json"}
NL, CRLF = "\n", "\r\n"
HOME = "content/pages/home.json"

# A lyric line and the Lomari line under it, inside one paragraph (or song button).
# Lines B4 could not move to classes keep their inline styles and are matched too.
LYRIC = re.compile(
    r'(<span (?:class="lyric-line(?: lyric-muted)?"|style="display: ?block;\s*font-size:[^"]*")>)'
    r'((?:(?!</p>).)*?)'
    r'(</span>\s*<span (?:class="lyric-lomari(?: lyric-lomari-ink)?"|style="[^"]*font-family: ?Calibri[^"]*")>)'
    r'((?:(?!</p>|<span\b).)*?)(</span>)', re.S | re.I)
RUBY = re.compile(r"<ruby\b[^>]*>(.*?)</ruby>", re.S)
RT = re.compile(r"<rt\b[^>]*>(.*?)</rt>", re.S)
FOOTNOTE = re.compile(r'<a\b[^>]*href="#_ftn[^"]*"[^>]*>.*?</a>', re.S)
TONE_ONLY = re.compile(r"^[\sˆˋˊˉˇˍˎˏˬꞈ`]+$")
HANGUL = re.compile(r"[ᄀ-ᇿ㄰-㆏가-힣ꥠ-꥿ힰ-퟿]")
BOPOMOFO = re.compile(r"[㄀-ㄯㆠ-ㆿ]")
HREF = re.compile(r'href="([^"]+)"')


def _plain(markup: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", markup))).strip()


def hangul_source(line_markup: str) -> str:
    """The Hokkien line as typed: each ruby's reading, or a tone-only ruby's syllable and mark."""
    def ruby(match: re.Match) -> str:
        inner = match.group(1)
        reading = "".join(RT.findall(inner))
        base = re.sub(r"<[^>]+>", "", RT.sub("", inner))
        return base + reading if TONE_ONLY.match(reading) else reading
    return _plain(RUBY.sub(ruby, FOOTNOTE.sub("", line_markup)))


def derive(source: str) -> str:
    grey = source.startswith("(") and source.endswith(")")
    core = source[1:-1] if grey else source
    value = phonetics().auto_lomari_from_hangul(core).replace("-’", "’")
    value = unicodedata.normalize("NFC", value)
    return f"({value})" if grey else value


def comparable(text: str) -> str:
    text = unicodedata.normalize("NFC", text).replace("…", "...")
    return text[:1].lower() + text[1:]


def same(stored: str, derived: str) -> bool:
    return comparable(stored) == comparable(derived)


def title_same(stored: str, derived: str) -> bool:
    """Song buttons may capitalise any word, as titles do."""
    return comparable(stored).lower() == comparable(derived).lower()


def tied(source: str) -> bool:
    return bool(HANGUL.search(source)) and not BOPOMOFO.search(source)


def content_pages(root: Path = ROOT):
    for path in sorted((root / "content").rglob("*.json")):
        name = path.relative_to(root).as_posix()
        if name in EXCLUDED:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("body"), str):
            yield name, path, data


def song_records(root: Path = ROOT):
    by_link = {}
    for path in sorted((root / "content" / "songs").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        for link in (record.get("sourceUrl"), record.get("route")):
            if link:
                by_link[unquote(link).rstrip("/").lower()] = record
    return by_link


def lines(name: str, body: str, songs: dict):
    """Yield (match, kind, source, derived) for each Lomari line tied to Hokkien text."""
    for match in LYRIC.finditer(body):
        line = match.group(2)
        if name == HOME:
            start = body.rfind("<a ", 0, match.start())
            href = HREF.search(body, start, match.start()) if start != -1 else None
            record = songs.get(unquote(href.group(1)).rstrip("/").lower()) if href else None
            if record is None:
                continue
            yield match, "title", f'{record["id"]}: {_plain(line)}', song_lomari(record)
            continue
        source = hangul_source(line)
        if tied(source):
            yield match, "lyric", source, derive(source)


def follows(kind: str, stored: str, derived: str) -> bool:
    return same(stored, derived) or (kind == "title" and title_same(stored, derived))


def differences(root: Path = ROOT, songs=None):
    songs = songs if songs is not None else song_records(root)
    found = []
    for name, _path, data in content_pages(root):
        for match, kind, source, derived in lines(name, data["body"], songs):
            stored = _plain(match.group(4))
            if not follows(kind, stored, derived):
                found.append({"page": name, "kind": kind, "hokkien": source, "stored": stored, "derived": derived})
    return found


def key(item: dict) -> tuple:
    return item["page"], item["hokkien"], item["stored"]


def load_review(root: Path = ROOT) -> list[dict]:
    path = root / REVIEW.relative_to(ROOT)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))["lines"]


def review_keys(root: Path = ROOT) -> set:
    return {key(item) for item in load_review(root)}


def write_review(items: list[dict]) -> None:
    unique = {key(item): item for item in items}
    payload = {
        "about": ("Lomari lines that differ from the Hangul above them, waiting for Haru's review. "
                  "'derived' is what the IME converter gives for the Hangul. Fix either the Hangul or "
                  "the Lomari in content/, then run python tools/lomari_sync.py --write-review."),
        "lines": [unique[k] for k in sorted(unique)],
    }
    REVIEW.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + NL, encoding="utf-8", newline=NL)


def sync_body(name: str, body: str, songs: dict, under_review: set) -> tuple[str, int]:
    """Rewrite every Lomari line in one page body from its Hokkien text; lines under review stay."""
    pieces, last, changed = [], 0, 0
    for match, kind, source, derived in lines(name, body, songs):
        stored = _plain(match.group(4))
        if follows(kind, stored, derived) or (name, source, stored) in under_review:
            continue
        derived = unicodedata.normalize("NFC", derived)
        if kind == "title":
            derived = derived[:1].upper() + derived[1:]
        text = html.escape(derived, quote=False).replace("--", "&#045;&#045;")
        old = match.group(4)
        new = re.sub(r"^(\s*).*?(\s*)$", lambda m: m.group(1) + text + m.group(2), old, flags=re.S)
        pieces += [body[last:match.start(4)], new]
        last = match.end(4)
        changed += 1
    return "".join(pieces) + body[last:], changed


def write_page(path: Path, data: dict) -> None:
    raw = path.read_bytes().decode("utf-8")
    newline = CRLF if CRLF in raw else NL
    text = json.dumps(data, ensure_ascii=False, indent=2) + NL
    path.write_bytes(text.replace(NL, newline).encode("utf-8"))


def fix(under_review: set, root: Path = ROOT, only=None) -> dict[str, int]:
    """Rewrite drifted Lomari lines from their Hangul. Returns {page: lines rewritten}."""
    songs = song_records(root)
    changed = {}
    for name, path, data in content_pages(root):
        if only is not None and name not in only:
            continue
        body, count = sync_body(name, data["body"], songs, under_review)
        if count:
            data["body"] = body
            write_page(path, data)
            changed[name] = count
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="fail when a Lomari line has drifted (default)")
    group.add_argument("--fix", action="store_true", help="rewrite drifted Lomari lines from their Hangul")
    group.add_argument("--write-review", action="store_true", help="record every current difference for review")
    args = parser.parse_args()

    if args.write_review:
        found = differences()
        write_review(found)
        print(f"Recorded {len(found)} Lomari lines for review in {REVIEW.relative_to(ROOT).as_posix()}.")
        return 0

    review = load_review()
    under_review = {key(item) for item in review}
    if args.fix:
        changed = fix(under_review)
        print(f"Rewrote {sum(changed.values())} Lomari lines from their Hangul; "
              f"{len(review)} lines under review left as they are.")
        return 0

    found = differences()
    found_keys = {key(item) for item in found}
    drifted = [item for item in found if key(item) not in under_review]
    resolved = [item for item in review if key(item) not in found_keys]
    for item in drifted:
        print(f'DRIFT {item["page"]}: {item["hokkien"]}\n  stored  {item["stored"]}\n  derived {item["derived"]}')
    for item in resolved:
        print(f'RESOLVED {item["page"]}: {item["hokkien"]} (remove it from the review list)')
    if drifted or resolved:
        print("Lomari is out of step with the Hokkien text. Run python tools/lomari_sync.py --fix after a Hangul "
              "edit, or --write-review once Haru has reviewed the remaining lines.")
        return 1
    print(f"OK: every tied Lomari line follows its Hokkien text; {len(review)} lines wait for review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
