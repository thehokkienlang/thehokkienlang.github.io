"""Import the first English WordPress batch without writing to WordPress."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
WP = "https://hokkienlang.wordpress.com"
SITE = "https://thehokkienlang.github.io"
API = "https://public-api.wordpress.com/rest/v1.1/sites/hokkienlang.wordpress.com/posts/"
PAGES = {
    3082: ("pages", "home", "/", "Home"),
    1258: ("pages", "about", "/about/", "About"),
    571: ("guides", "introduction", "/learn/introduction/", "Introduction to Tangliengim"),
    9583: ("guides", "spelling", "/learn/spelling/", "Spelling guidelines"),
    8714: ("guides", "tone-sandhi", "/learn/tone-sandhi/", "Tone sandhi in Hokkien"),
    10790: ("guides", "romanisation", "/learn/romanisation/", "Tangliengim romanisation"),
    433: ("guides", "lyrics-translation", "/songs/translation-notes/", "Lyrics translation"),
    7204: ("literature", "lychee-mirror", "/read/literature/lychee-mirror/", "荔鏡記 · Tale of the Lychee Mirror"),
}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
BLOCKED = {"script", "style", "object", "embed", "form", "input", "button", "link", "meta", "base"}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch_bytes(url):
    parsed = urlsplit(url)
    encoded = urlunsplit((parsed.scheme, parsed.netloc, quote(unquote(parsed.path), safe="/"), parsed.query, ""))
    with urlopen(Request(encoded, headers={"User-Agent": "TLI-WordPress-Migration/1.0"}), timeout=60) as response:
        return response.read()


def fetch_export():
    posts = []
    page = 1
    while True:
        data = json.loads(fetch_bytes(f"{API}?number=100&type=any&status=publish&page={page}"))
        posts.extend(data["posts"])
        if len(posts) >= data["found"]:
            break
        if not data["posts"]:
            raise RuntimeError("WordPress pagination ended before all published records were returned")
        page += 1
    return {"found": len(posts), "posts": posts}


def source_key(url):
    parsed = urlsplit(urljoin(WP + "/", url))
    return parsed.netloc.lower(), unquote(parsed.path).rstrip("/") or "/"


class ImportedHTML(HTMLParser):
    """Preserve reading markup; relocate links/media and remove WP-only controls."""

    def __init__(self, source_url, routes, media, root, download, existing_site=None):
        super().__init__(convert_charrefs=False)
        self.source_url, self.routes, self.media = source_url, routes, media
        self.root, self.download = root, download
        self.existing_site = existing_site or root
        self.output = []
        self.stack = []
        self.suppressed = 0

    def rewrite(self, value, media=False):
        if not value or value.startswith("#"):
            return value
        if value.startswith("/") and not value.startswith("//"):
            local_path = urlsplit(value).path
            if local_path in self.routes.values() or local_path.startswith(("/dictionary/", "/ime/")):
                return value
            if local_path.startswith("/assets/") and any((root / unquote(local_path).lstrip("/")).is_file() for root in (self.root, self.existing_site)):
                return value
        absolute = urljoin(self.source_url, value)
        parsed = urlsplit(absolute)
        if parsed.scheme not in {"https", "http", "mailto", "tel"}:
            return ""
        route = self.routes.get(source_key(absolute))
        if route and not parsed.query:
            return route + ("#" + parsed.fragment if parsed.fragment else "")
        if parsed.netloc == urlsplit(SITE).netloc:
            local = self.existing_site / unquote(parsed.path).lstrip("/")
            if local.is_file() or parsed.path.startswith(("/dictionary/", "/ime/")):
                return parsed.path + ("?" + parsed.query if parsed.query else "") + ("#" + parsed.fragment if parsed.fragment else "")
        owned = parsed.netloc in {"hokkienlang.wordpress.com", "hokkienlang.files.wordpress.com"}
        if owned and (media or "/wp-content/uploads/" in parsed.path):
            original = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
            if original not in self.media:
                name = Path(unquote(parsed.path)).name
                safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-.") or "media"
                target = "/assets/content/wordpress/" + hashlib.sha256(original.encode()).hexdigest()[:12] + "-" + safe
                self.media[original] = target
            target = self.root / self.media[original].lstrip("/")
            if not target.exists():
                if not self.download:
                    raise FileNotFoundError(f"Use --download-media to copy {original}")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(fetch_bytes(original))
            return self.media[original]
        return absolute

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        blocked = tag in BLOCKED or (tag == "iframe" and urlsplit(attributes.get("src", "")).netloc not in {"w.soundcloud.com", "www.youtube.com", "www.youtube-nocookie.com", "player.vimeo.com"})
        if tag not in VOID:
            self.stack.append((tag, blocked))
        if blocked and tag not in VOID:
            self.suppressed += 1
        if self.suppressed or blocked:
            return
        result = []
        for key, value in attrs:
            if key.startswith("on") or key.startswith("data-wp-") or key in {"srcset", "sizes", "srcdoc"}:
                continue
            if key == "href" or key == "src" or key == "poster":
                value = self.rewrite(value, media=key != "href" and tag != "iframe")
            if key == "style" and value and re.search(r"url\s*\(|expression\s*\(|javascript:", value, re.I):
                continue
            if value is None:
                result.append(key)
            else:
                result.append(f'{key}="{html.escape(value, quote=True)}"')
        if tag in {"audio", "video"} and "preload" not in attributes:
            result.append('preload="none"')
        if tag in {"img", "iframe"} and "loading" not in attributes:
            result.append('loading="lazy"')
        self.output.append("<" + tag + (" " + " ".join(result) if result else "") + ">")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        was_suppressed = self.suppressed
        # WordPress fragments may have unmatched closing tags; never let them escape the article.
        index = next((i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i][0] == tag), None)
        if index is None:
            return
        closed = self.stack[index:]
        del self.stack[index:]
        for _, blocked in closed:
            if blocked:
                self.suppressed -= 1
        if not was_suppressed:
            self.output.extend(f"</{name}>" for name, _ in reversed(closed))

    def handle_data(self, data):
        if not self.suppressed:
            self.output.append(data)

    def handle_entityref(self, name):
        self.handle_data("&" + name + ";")

    def handle_charref(self, name):
        self.handle_data("&#" + name + ";")

    def render(self, content):
        self.feed(content)
        self.close()
        self.output.extend(f"</{tag}>" for tag, blocked in reversed(self.stack) if not blocked)
        return "".join(self.output)


def write_song_ime_data(root):
    """Classic-script data works on file://, where fetch(JSON) is blocked."""
    data_path = root / "public/data/hokkien-hanri-dict.json"
    if not data_path.exists():
        return
    data = json.loads(data_path.read_text(encoding="utf-8"))
    payload = {
        "sourceSha256": data["sourceSha256"],
        "entries": [{key: value for key, value in entry.items() if key != "audio"} for entry in data["entries"]],
    }
    target = root / "migration/song-ime-data.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("window.TliSongImeData = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def make_song_form(posts, root):
    songs = [post for post in posts if post["type"] == "post" and post["ID"] not in {865, 7647}]
    path = root / "migration/song-urls.json"
    existing = {row["old_url"]: row.get("new_url", "") for row in json.loads(path.read_text(encoding="utf-8"))} if path.exists() else {}
    rows = [{"old_url": post["URL"], "new_url": existing.get(post["URL"], "")} for post in songs]
    write_json(path, rows)
    write_json(root / "migration/song-titles.json", {post["URL"]: html.unescape(post["title"]) for post in songs})
    labels = [{**row, "title": html.unescape(post["title"])} for row, post in zip(rows, songs)]
    payload = json.dumps(labels, ensure_ascii=False).replace("<", "\\u003c")
    template = (root / "apps/content-site/song-url-form.html").read_text(encoding="utf-8")
    (root / "migration/song-url-form.html").write_text(template.replace("__SONG_ROWS__", payload), encoding="utf-8")
    write_song_ime_data(root)
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path, help="Previously downloaded public API JSON")
    parser.add_argument("--download-media", action="store_true")
    parser.add_argument("--existing-site", type=Path, help="Read existing asset paths from another checkout while staging")
    args = parser.parse_args()
    exported = json.loads(args.export.read_text(encoding="utf-8-sig")) if args.export else fetch_export()
    posts = {post["ID"]: post for post in exported["posts"]}
    missing = set(PAGES) - posts.keys()
    if missing:
        raise RuntimeError(f"Missing source pages: {sorted(missing)}")
    routes = {source_key(posts[identity]["URL"]): spec[2] for identity, spec in PAGES.items()}
    media_path = ROOT / "migration/wordpress-media.json"
    media = json.loads(media_path.read_text(encoding="utf-8")) if media_path.exists() else {}
    records = []
    for identity, (folder, slug, route, title) in PAGES.items():
        post = posts[identity]
        path = ROOT / "content" / folder / (slug + ".json")
        if path.exists():
            raise RuntimeError(f"Refusing to overwrite imported/editorial content: {path}. Review source updates separately.")
        original = post["content"]
        source = {key: post[key] for key in ("ID", "URL", "title", "type", "date", "modified", "content")}
        write_json(ROOT / "migration/wordpress-source" / f"{identity}.json", source)
        transformer = ImportedHTML(post["URL"], routes, media, ROOT, args.download_media, args.existing_site)
        record = {
            "id": slug, "type": folder, "language": "en", "title": title, "route": route,
            "sourceUrl": post["URL"], "sourceId": identity, "sourceModified": post["modified"],
            "sourceSha256": hashlib.sha256(original.encode()).hexdigest(),
            "orthography": {"target": "3.1", "review": "pending", "v32Changes": "deferred"},
            "body": transformer.render(original),
        }
        write_json(path, record)
        records.append({"sourceUrl": post["URL"], "sourceId": identity, "route": route, "file": path.relative_to(ROOT).as_posix()})
        print(f"Imported {title}: {route}")
    write_json(media_path, media)
    song_count = make_song_form(list(posts.values()), ROOT)
    write_json(ROOT / "migration/wordpress-map.json", {
        "importedAt": datetime.now(timezone.utc).isoformat(), "language": "en", "records": records,
        "deferred": {"songs": song_count, "theEgg": [865, 7647], "chinesePresentations": "later"},
        "songUrls": "migration/song-urls.json", "wordpressChanges": "none",
        "compliance": "Preserved source; complete the v3.1 review before declaring compliance. v3.2 remains deferred.",
    })
    print(f"Imported {len(records)} English pages; {song_count} songs and The Egg remain on WordPress.")


if __name__ == "__main__":
    main()
