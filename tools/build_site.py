"""Build both public interfaces and their shared resources into _site/."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from build_dictionary_json import DEFAULT_OUTPUT_PATH, main as build_dictionary_json

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"
ASSET_ATTRIBUTE = re.compile(r'(?P<prefix>\b(?:src|href)=")(?P<url>[^"#]+)(?P<suffix>")')


def version_assets(html_path: Path) -> None:
    page_url = "/" + html_path.relative_to(OUTPUT).as_posix()

    def replace(match: re.Match) -> str:
        value = match.group("url")
        url = urlsplit(value)
        if url.scheme or url.netloc or not url.path.endswith((".js", ".css", ".svg", ".ico")):
            return match.group(0)
        asset = OUTPUT / unquote(urljoin(page_url, url.path)).lstrip("/")
        if not asset.is_file():
            raise FileNotFoundError(f"Missing asset in {page_url}: {value}")
        digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
        return f'{match.group("prefix")}{url.path}?v={digest}{match.group("suffix")}'

    html_path.write_text(ASSET_ATTRIBUTE.sub(replace, html_path.read_text(encoding="utf-8")), encoding="utf-8")


def main() -> int:
    # Generate data from the exact TSV and pronunciation code being deployed.
    build_dictionary_json()
    if OUTPUT.is_symlink() or OUTPUT.resolve().parent != ROOT.resolve():
        raise RuntimeError("Build output must be the repository's own _site directory.")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    for filename in ("index.html", "favicon.ico", ".nojekyll"):
        shutil.copy2(ROOT / filename, OUTPUT / filename)
    for folder in ("assets", "shared"):
        shutil.copytree(ROOT / folder, OUTPUT / folder)
    for app in ("dictionary", "ime"):
        shutil.copytree(ROOT / "apps" / app, OUTPUT / app)
    shutil.copytree(ROOT / "public" / "audio", OUTPUT / "public" / "audio",
                    ignore=shutil.ignore_patterns("_hokkien_ime_playback.wav"))
    (OUTPUT / "public" / "data").mkdir(parents=True)
    shutil.copy2(DEFAULT_OUTPUT_PATH, OUTPUT / "public" / "data" / DEFAULT_OUTPUT_PATH.name)
    for html_path in (OUTPUT / "index.html", OUTPUT / "dictionary" / "index.html", OUTPUT / "ime" / "index.html"):
        version_assets(html_path)
    data = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))
    manifest = {
        "routes": ["/dictionary/", "/ime/"],
        "sourceSha256": data["sourceSha256"],
        "entries": len(data["entries"]),
        "shared": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((OUTPUT / "shared").glob("*.js"))
        },
    }
    (OUTPUT / "build-info.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Built /dictionary/ and /ime/ with shared code, dictionary data, and audio.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
