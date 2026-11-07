"""Build both public interfaces and their shared resources into _site/."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from build_dictionary_json import DEFAULT_OUTPUT_PATH, main as build_dictionary_json
from dictionary_data import PUBLISHED_SIDECARS, sidecar_path
from compressed_audio import EXTENSION as COMPRESSED_AUDIO_EXTENSION, write_compressed_copies
from build_content import document as content_document
from page_meta import NOT_FOUND_BODY, meta_tags, robots as robots_txt, sitemap as sitemap_xml
from build_content import build_content, navigation_links, site_brand
from import_wordpress import write_song_ime_data

APP_DESCRIPTIONS = {
    "dictionary": "A Hokkien dictionary in Tangliengim (TLI) with Hanri, Hangul readings, Lomari, audio and English glosses. Invite only.",
    "ime": "Type Hokkien in Tangliengim (TLI) Hangul and Hanri in your browser, with Lomari and audio.",
    "translate": "A local English and Hokkien translator preview powered by TLI. Invite only.",
}


def app_meta(page: str, app: str) -> str:
    """Description and share tags for an app page (audit A8)."""
    title = re.search(r"<title>(.*?) · TheHokkienLang</title>", page).group(1)
    page = re.sub(r'\s*<meta\s[^>]*\bname="description"[^>]*>', "", page)
    tags = meta_tags(title, f"/{app}/", APP_DESCRIPTIONS[app], "en").replace("\n  ", "\n    ")
    return page.replace("</title>", "</title>\n    " + tags, 1)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"
ASSET_ATTRIBUTE = re.compile(r'(?P<prefix>\b(?:src|href)=")(?P<url>[^"#]+)(?P<suffix>")')
CSS_IMPORT = re.compile(r'(@import\s+url\(")([^"]+)("\))')
ASSET_VERSIONS_LINE = re.compile(r"^(?P<indent>[ \t]*)const ASSET_VERSIONS = \{\};$", re.MULTILINE)
GATE_SCRIPT_SOURCE = re.compile(r'"(?P<source>[^"\s]+\.js)"')
DATA_VERSIONS_LINE = re.compile(r"^(?P<indent>[ \t]*)const DATA_VERSIONS = \{\};$", re.MULTILINE)
DATA_URL_SOURCE = re.compile(r'"(?P<url>/public/data/[^"\s?#]+\.json)"')
AUDIO_FORMAT_LINE = re.compile(r'^(?P<indent>[ \t]*)const COMPRESSED_AUDIO_EXTENSION = "";$', re.MULTILINE)
DATA_APP_SCRIPTS = ("dictionary/app.js", "ime/ime.js", "assets/search/search.js", "translate/translate.js")


def version_css_imports(css_path: Path, visited: set[Path]) -> None:
    if css_path in visited:
        return
    visited.add(css_path)
    page_url = "/" + css_path.relative_to(OUTPUT).as_posix()

    def replace(match: re.Match) -> str:
        url = urlsplit(match[2])
        if url.scheme or url.netloc:
            return match[0]
        dependency = OUTPUT / unquote(urljoin(page_url, url.path)).lstrip("/")
        if not dependency.is_file():
            raise FileNotFoundError(f"Missing CSS import in {page_url}: {match[2]}")
        version_css_imports(dependency, visited)
        digest = hashlib.sha256(dependency.read_bytes()).hexdigest()[:12]
        return f'{match[1]}{url.path}?v={digest}{match[3]}'

    css_path.write_text(CSS_IMPORT.sub(replace, css_path.read_text(encoding="utf-8")), encoding="utf-8")


def version_assets(html_path: Path) -> None:
    page_url = "/" + html_path.relative_to(OUTPUT).as_posix()

    def replace(match: re.Match) -> str:
        value = match.group("url")
        url = urlsplit(value)
        if url.scheme or url.netloc or not (url.path.endswith((".js", ".css", ".svg", ".ico")) or url.path == "/assets/tangliengim-hokkienlang-logo.png"):
            return match.group(0)
        asset = OUTPUT / unquote(urljoin(page_url, url.path)).lstrip("/")
        if not asset.is_file():
            raise FileNotFoundError(f"Missing asset in {page_url}: {value}")
        digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
        return f'{match.group("prefix")}{url.path}?v={digest}{match.group("suffix")}'

    html_path.write_text(ASSET_ATTRIBUTE.sub(replace, html_path.read_text(encoding="utf-8")), encoding="utf-8")


def version_gate_scripts(gate_path: Path) -> None:
    """Give a lock screen's dynamically loaded scripts content-hash versions.

    The gates load their app scripts after the password check, so the HTML
    attribute pass cannot see them. Each built gate gets a frozen map of the
    scripts it names to their content hashes instead of a per-visit timestamp.
    """
    text = gate_path.read_text(encoding="utf-8")
    if len(ASSET_VERSIONS_LINE.findall(text)) != 1:
        raise RuntimeError(f"{gate_path} must contain exactly one 'const ASSET_VERSIONS = {{}};' line")
    page_url = "/" + gate_path.relative_to(OUTPUT).as_posix()
    versions = {}
    for match in GATE_SCRIPT_SOURCE.finditer(text):
        source = match["source"]
        asset = OUTPUT / unquote(urljoin(page_url, source)).lstrip("/")
        if not asset.is_file():
            raise FileNotFoundError(f"Missing script in {page_url}: {source}")
        versions[source] = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
    if not versions:
        raise RuntimeError(f"{gate_path} names no scripts to version")
    frozen = json.dumps(versions, ensure_ascii=False, sort_keys=True)
    text = ASSET_VERSIONS_LINE.sub(lambda match: f"{match['indent']}const ASSET_VERSIONS = Object.freeze({frozen});", text)
    gate_path.write_text(text, encoding="utf-8")


def version_data_urls(script_path: Path) -> None:
    """Give an app's dictionary data URLs content-hash versions.

    The apps fetch their JSON from script code, so the HTML attribute pass
    cannot see it. With a version the browser may use its normal cache, and a
    new build still gets new URLs; unbuilt checkouts keep revalidating.
    """
    text = script_path.read_text(encoding="utf-8")
    if len(DATA_VERSIONS_LINE.findall(text)) != 1:
        raise RuntimeError(f"{script_path} must contain exactly one 'const DATA_VERSIONS = {{}};' line")
    versions = {}
    for match in DATA_URL_SOURCE.finditer(text):
        data = OUTPUT / match["url"].lstrip("/")
        if not data.is_file():
            raise FileNotFoundError(f"Missing data file in {script_path.name}: {match['url']}")
        versions[match["url"]] = hashlib.sha256(data.read_bytes()).hexdigest()[:12]
    if not versions:
        raise RuntimeError(f"{script_path} names no data files to version")
    frozen = json.dumps(versions, ensure_ascii=False, sort_keys=True)
    text = DATA_VERSIONS_LINE.sub(lambda match: f"{match['indent']}const DATA_VERSIONS = Object.freeze({frozen});", text)
    script_path.write_text(text, encoding="utf-8")


def enable_compressed_audio(player_path: Path, extension: str) -> None:
    """Tell the built audio player that every WAV has a compressed copy beside it."""
    text = player_path.read_text(encoding="utf-8")
    if len(AUDIO_FORMAT_LINE.findall(text)) != 1:
        raise RuntimeError(f"{player_path} must contain exactly one 'const COMPRESSED_AUDIO_EXTENSION = \"\";' line")
    text = AUDIO_FORMAT_LINE.sub(lambda match: f'{match["indent"]}const COMPRESSED_AUDIO_EXTENSION = "{extension}";', text)
    player_path.write_text(text, encoding="utf-8")


def write_discovery_files(content_routes) -> None:
    """sitemap.xml, robots.txt and the 404 page (audit A8).

    The sitemap lists the published content pages and the public IME; the
    password-gated Dictionary and Translator, and redirects from old addresses,
    are left out.
    """
    def is_redirect(route):
        page = OUTPUT / route.lstrip("/") / "index.html"
        return page.is_file() and 'http-equiv="refresh"' in page.read_text(encoding="utf-8", errors="ignore")[:400]

    pages = [route for route in content_routes if not is_redirect(route)]
    (OUTPUT / "sitemap.xml").write_text(sitemap_xml([*pages, "/ime/"]), encoding="utf-8")
    (OUTPUT / "robots.txt").write_text(robots_txt(), encoding="utf-8")
    page = content_document(ROOT, "Page not found", "/404/", NOT_FOUND_BODY)
    page = re.sub(r'\s*<link rel="(?:canonical|alternate)"[^>]*>', "", page)
    page = page.replace("<title>", '<meta name="robots" content="noindex">\n  <title>', 1)
    (OUTPUT / "404.html").write_text(page, encoding="utf-8")


def main() -> int:
    # Generate data from the exact TSV and pronunciation code being deployed.
    build_dictionary_json()
    write_song_ime_data(ROOT)
    if OUTPUT.is_symlink() or OUTPUT.resolve().parent != ROOT.resolve():
        raise RuntimeError("Build output must be the repository's own _site directory.")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    for filename in ("index.html", "favicon.ico", ".nojekyll"):
        shutil.copy2(ROOT / filename, OUTPUT / filename)
    for folder in ("assets", "shared"):
        shutil.copytree(ROOT / folder, OUTPUT / folder)
    for app in ("dictionary", "ime", "translate"):
        shutil.copytree(ROOT / "apps" / app, OUTPUT / app)
        index = OUTPUT / app / "index.html"
        index.write_text(app_meta(index.read_text(encoding="utf-8").replace("__SITE_NAVIGATION__", navigation_links(f"/{app}/")).replace("__SITE_BRAND__", site_brand(ROOT)), app), encoding="utf-8")
    shutil.copytree(ROOT / "public" / "audio", OUTPUT / "public" / "audio",
                    ignore=shutil.ignore_patterns("_hokkien_ime_playback.wav"))
    # Opus copies beside the WAV masters; the player uses them only when every
    # WAV has one (before the gate and HTML passes, which hash the player).
    if write_compressed_copies(OUTPUT / "public" / "audio"):
        enable_compressed_audio(OUTPUT / "shared" / "web-audio-player.js", COMPRESSED_AUDIO_EXTENSION)
    (OUTPUT / "public" / "data").mkdir(parents=True)
    # Lookup indexes stay build-only; browsers build their own lookups.
    for data_file in (DEFAULT_OUTPUT_PATH, *(sidecar_path(DEFAULT_OUTPUT_PATH, part) for part in PUBLISHED_SIDECARS)):
        shutil.copy2(data_file, OUTPUT / "public" / "data" / data_file.name)
    content_routes = build_content(ROOT, OUTPUT)
    write_discovery_files(content_routes)
    shutil.copytree(ROOT / "apps" / "search", OUTPUT / "assets" / "search")
    # Before the gate and HTML passes, which hash these scripts.
    for script in DATA_APP_SCRIPTS:
        version_data_urls(OUTPUT / script)
    for app in ("dictionary", "translate"):
        version_gate_scripts(OUTPUT / app / "gate.js")
    visited_css = set()
    for css_path in OUTPUT.rglob("*.css"):
        version_css_imports(css_path, visited_css)
    for html_path in OUTPUT.rglob("*.html"):
        version_assets(html_path)
    data = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))
    manifest = {
        "routes": sorted(set(["/dictionary/", "/ime/", *content_routes])),
        "sourceSha256": data["sourceSha256"],
        "headwordAliasesSourceSha256": data['headwordAliasesSourceSha256'],
        "idRegistrySourceSha256": data["idRegistrySourceSha256"],
        "categorySourceSha256": data["categorySourceSha256"],
        "prioritySourceSha256": data['prioritySourceSha256'],
        "entries": len(data["entries"]),
        "shared": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((OUTPUT / "shared").glob("*.*"))
        },
    }
    (OUTPUT / "build-info.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Built dictionary, IME, and {len(content_routes)} content routes with shared resources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
