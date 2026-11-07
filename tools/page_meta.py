"""Search and share metadata for every published page (audit A8).

Each content page gets a meta description, Open Graph tags and a Twitter card.
Index pages use fixed descriptions, songs a sentence naming the song, and
other pages the opening of their own text with ruby readings left out.
The build also writes sitemap.xml, robots.txt and a 404 page.
"""

from __future__ import annotations

import html
import re
from xml.sax.saxutils import escape as xml_escape

SITE = "https://thehokkienlang.github.io"
SITE_NAME = "TheHokkienLang"
SHARE_IMAGE = SITE + "/assets/tangliengim-hokkienlang-logo.png"
LOCALES = {"en": "en", "zh-Hant": "zh_TW", "zh-Hans": "zh_CN"}
MAX_LENGTH = {"en": 160, "zh-Hant": 80, "zh-Hans": 80}

INDEX_DESCRIPTIONS = {
    "/learn/": {
        "en": "Guides to reading and writing Hokkien in Tangliengim (TLI): letters, spelling, tone sandhi and romanisation.",
        "zh-Hant": "以東寧音（TLI）讀寫閩南語的指南：字母、拼寫、變調與羅馬字。",
        "zh-Hans": "以东宁音（TLI）读写闽南语的指南：字母、拼写、变调与罗马字。",
    },
    "/songs/": {
        "en": "Hokkien songs with lyrics in Tangliengim (TLI), Hangul readings and Lomari.",
        "zh-Hant": "附東寧音諺文讀音與羅馬字歌詞的閩南語歌曲。",
        "zh-Hans": "附东宁音谚文读音与罗马字歌词的闽南语歌曲。",
    },
    "/read/": {
        "en": "Hokkien stories and literature with Tangliengim (TLI) readings.",
        "zh-Hant": "附東寧音讀音的閩南語故事與文學。",
        "zh-Hans": "附东宁音读音的闽南语故事与文学。",
    },
    "/read/stories/the-egg/": {
        "en": "A Hokkien translation of Andy Weir's The Egg, written in Tangliengim (TLI).",
        "zh-Hant": "Andy Weir《The Egg》的閩南語翻譯，以東寧音書寫。",
        "zh-Hans": "Andy Weir《The Egg》的闽南语翻译，以东宁音书写。",
    },
    "/search/": {
        "en": "Search the guides, songs and stories on TheHokkienLang.",
        "zh-Hant": "搜尋 TheHokkienLang 的指南、歌曲與故事。",
        "zh-Hans": "搜索 TheHokkienLang 的指南、歌曲与故事。",
    },
}
SONG_DESCRIPTION = {
    "en": "Lyrics of the Hokkien song {title} in Tangliengim (TLI), with Hangul readings and Lomari.",
    "zh-Hant": "閩南語歌曲《{title}》的東寧音歌詞，附諺文讀音與羅馬字。",
    "zh-Hans": "闽南语歌曲《{title}》的东宁音歌词，附谚文读音与罗马字。",
}

_SKIPPED = re.compile(r"<(rt|rp|script|style|audio|video|nav|figcaption|details|table)\b.*?</\1>", re.S | re.I)
# Block boundaries become spaces; inline tags (ruby, span, strong) join their text.
_BLOCK = re.compile(r"</?(p|div|li|ul|ol|h[1-6]|br|tr|td|th|section|article|blockquote)\b[^>]*>", re.I)
_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")
_SPACE_BEFORE_PUNCTUATION = re.compile(r"\s+([,.;:!?)，。；：！？、）」』])")


def _excerpt(body: str, language: str) -> str:
    text = _TAG.sub("", _BLOCK.sub(" ", _SKIPPED.sub(" ", body)))
    text = _SPACE_BEFORE_PUNCTUATION.sub(r"\1", _SPACE.sub(" ", html.unescape(text))).strip()
    limit = MAX_LENGTH[language]
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if language == "en" and " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:·—-") + "…"


def description(title: str, base_route: str, body: str, content_type: str, language: str, home: str) -> str:
    if base_route == "/":
        return home
    if base_route in INDEX_DESCRIPTIONS:
        return INDEX_DESCRIPTIONS[base_route][language]
    if content_type == "songs":
        return SONG_DESCRIPTION[language].format(title=title)
    return _excerpt(body, language) or title


def meta_tags(title: str, route: str, text: str, language: str, kind: str = "website") -> str:
    url = SITE + route
    full_title = SITE_NAME if route in ("/", "/zh-hant/", "/zh-hans/") else f"{title} · {SITE_NAME}"
    values = {
        "description": text,
        "og:type": kind,
        "og:site_name": SITE_NAME,
        "og:title": full_title,
        "og:description": text,
        "og:url": url,
        "og:image": SHARE_IMAGE,
        "og:image:width": "1536",
        "og:image:height": "1024",
        "og:locale": LOCALES[language],
        "twitter:card": "summary",
    }
    tags = []
    for key, value in values.items():
        attribute = "property" if key.startswith("og:") else "name"
        tags.append(f'<meta {attribute}="{key}" content="{html.escape(value, quote=True)}">')
    return "\n  ".join(tags)


def sitemap(routes: list[str]) -> str:
    entries = "".join(f"  <url><loc>{xml_escape(SITE + route)}</loc></url>\n" for route in sorted(set(routes)))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + "</urlset>\n")


def robots() -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"


NOT_FOUND_BODY = (
    '<p>This page doesn’t exist, or it has moved.</p>'
    '<p>此頁不存在，或已搬移。<br>此页不存在，或已搬移。</p>'
    '<ul class="page-list">'
    '<li><a href="/">TheHokkienLang home</a> · <a href="/zh-hant/">主頁</a> · <a href="/zh-hans/">主页</a></li>'
    '<li><a href="/search/">Search the site</a> · <a href="/zh-hant/search/">搜尋</a> · <a href="/zh-hans/search/">搜索</a></li>'
    '<li><a href="/songs/">Songs</a> · <a href="/learn/introduction/">Introduction to TLI</a></li>'
    "</ul>"
)
