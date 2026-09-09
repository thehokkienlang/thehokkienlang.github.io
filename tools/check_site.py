"""Check the combined Pages artifact before it is published."""

import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.urls.extend(attrs[key] for key in ("src", "href") if attrs.get(key))
        if tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])


def local_file(url):
    path = SITE / unquote(urlsplit(url).path).lstrip("/")
    if path.is_dir():
        path /= "index.html"
    assert path.resolve().is_relative_to(SITE.resolve()), f"Path outside the site: {url}"
    assert path.is_file(), f"Missing published file: {url}"
    return path


def main():
    script_sets = []
    for route in ("/", "/dictionary/", "/ime/"):
        parser = References()
        parser.feed(local_file(route).read_text(encoding="utf-8"))
        for reference in parser.urls:
            url = urlsplit(reference)
            if not url.scheme and not url.netloc:
                local_file(urljoin(route, reference))
        if route != "/":
            shared = [src for src in parser.scripts if src.startswith("/shared/")]
            assert len(shared) == 2, f"Shared composer/controller missing in {route}"
            script_sets.append(shared)
    assert script_sets[0] == script_sets[1], "Apps load different shared code versions"

    data = json.loads(local_file("/public/data/hokkien-hanri-dict.json").read_text(encoding="utf-8"))
    assert data["schemaVersion"] == 2
    categories = {item["id"]: item for item in data["categories"]}
    assert set(categories) == {"food", "place-names"}
    assert all(item["entryCount"] > 0 for item in categories.values())
    assert any("food" in entry["categories"] for entry in data["entries"])
    assert any("place-names" in entry["categories"] for entry in data["entries"])
    digest = hashlib.sha256((ROOT / "data/hokkien_hanri_dict.tsv").read_bytes()).hexdigest()
    assert data["sourceSha256"] == digest, "Published JSON is out of sync with the TSV"
    category_digest = hashlib.sha256((ROOT / "data/dictionary_categories.tsv").read_bytes()).hexdigest()
    assert data["categorySourceSha256"] == category_digest, "Published JSON is out of sync with category data"
    assert data["entries"], "Empty dictionary"
    audio_paths = set()
    for entry in data["entries"]:
        audio = entry["audio"]
        for variant in (audio, audio.get("singapore", {})):
            audio_paths.update(variant.get("files", []))
            audio_paths.update(segment["file"] for segment in variant.get("segments", []))
    for url in audio_paths:
        assert url.startswith("/public/audio/"), f"Non-shared audio URL: {url}"
        local_file(url)
    for source_folder in ("assets", "public/audio"):
        for source in (ROOT / source_folder).rglob("*"):
            if source.is_file() and source.name != "_hokkien_ime_playback.wav":
                published = SITE / source.relative_to(ROOT)
                assert published.is_file(), f"Lost asset: {source}"
                assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(published.read_bytes()).digest(), f"Changed asset: {source}"
    assert not (SITE / "desktop").exists()
    assert not (SITE / "data").exists()
    assert not (SITE / ".git").exists()
    print(f"OK: both routes, identical shared scripts, {len(data['entries'])} TSV entries, {len(audio_paths)} referenced recordings, preserved assets.")


if __name__ == "__main__":
    main()
