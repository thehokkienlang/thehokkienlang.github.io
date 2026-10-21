"""Import approved song URLs and the English Egg story, leaving WordPress intact."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

from import_wordpress import ImportedHTML, SITE, fetch_export, source_key, write_json, write_song_ime_data

ROOT = Path(__file__).resolve().parents[1]


def approved_song_routes(rows, posts):
    songs = {source_key(post["URL"]): post for post in posts if post["type"] == "post" and post["ID"] not in {865, 7647}}
    if len(rows) != len(songs):
        raise ValueError(f"Expected {len(songs)} song URL rows, received {len(rows)}")
    seen_sources, seen_routes, result = set(), set(), []
    for row in rows:
        if set(row) != {"old_url", "new_url"}:
            raise ValueError("Each song row must have only old_url and new_url")
        key = source_key(row["old_url"])
        if key not in songs or key in seen_sources:
            raise ValueError(f"Unknown or repeated source: {row['old_url']}")
        seen_sources.add(key)
        parsed = urlsplit(row["new_url"].strip())
        if parsed.scheme and (parsed.scheme != "https" or parsed.netloc != urlsplit(SITE).netloc):
            raise ValueError(f"Destination must be on the GitHub website: {row['new_url']}")
        if parsed.netloc and parsed.netloc != urlsplit(SITE).netloc or parsed.query or parsed.fragment:
            raise ValueError(f"Invalid destination: {row['new_url']}")
        route = unicodedata.normalize("NFC", unquote(parsed.path))
        if not re.fullmatch(r"/songs/[^/]+/", route):
            raise ValueError(f"Expected /songs/title/: {row['new_url']}")
        title = route[7:-1]
        if title in {".", ".."} or title.casefold() == "translation-notes" or title.isdigit() or re.search(r"[\s'’‘`ˆˋˊˉˇꞈˎˏˍ\\?#%\x00-\x1f]", title):
            raise ValueError(f"Invalid song title in URL: {row['new_url']}")
        if route.casefold() in seen_routes:
            raise ValueError(f"Duplicate song URL: {route}")
        seen_routes.add(route.casefold())
        result.append((songs[key], route, row["old_url"]))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path)
    parser.add_argument("--song-urls", type=Path, required=True)
    parser.add_argument("--download-media", action="store_true")
    parser.add_argument("--existing-site", type=Path)
    args = parser.parse_args()
    exported = json.loads(args.export.read_text(encoding="utf-8-sig")) if args.export else fetch_export()
    posts = exported["posts"]
    by_id = {post["ID"]: post for post in posts}
    chosen = json.loads(args.song_urls.read_text(encoding="utf-8-sig"))
    songs = approved_song_routes(chosen, posts)
    manifest_path = ROOT / "migration/wordpress-map.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing_ids = {item["sourceId"] for item in manifest["records"]}
    new_specs = [(post, "songs", f'song-{post["ID"]}', route, route[7:-1]) for post, route, _ in songs]
    new_specs.append((by_id[865], "stories", "the-egg", "/read/stories/the-egg/", "The Egg"))
    duplicates = existing_ids & {post["ID"] for post, *_ in new_specs}
    if duplicates:
        raise ValueError(f"These sources are already imported; refusing to overwrite them: {sorted(duplicates)}")
    routes = {source_key(item["sourceUrl"]): item["route"] for item in manifest["records"]}
    for post, _, _, route, _ in new_specs:
        routes[source_key(post["URL"])] = route
    for post, route, old_url in songs:
        routes[source_key(old_url)] = route
    if len(set(routes.values())) != len(manifest["records"]) + len(new_specs):
        raise ValueError("A destination is assigned to more than one imported record")
    media_path = ROOT / "migration/wordpress-media.json"
    media = json.loads(media_path.read_text(encoding="utf-8"))
    pending = []
    for post, folder, identity, route, title in new_specs:
        path = ROOT / "content" / folder / (identity + ".json")
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite {path}")
        original = post["content"]
        body = ImportedHTML(post["URL"], routes, media, ROOT, args.download_media, args.existing_site).render(original)
        record = {
            "id": identity, "type": folder, "language": "en", "title": title,
            "originalTitle": html.unescape(post["title"]), "route": route,
            "sourceUrl": post["URL"], "sourceId": post["ID"], "sourceModified": post["modified"],
            "sourceSha256": hashlib.sha256(original.encode()).hexdigest(),
            "orthography": {"target": "3.1", "review": "source-preserved", "v32Changes": "deferred"},
            "body": body,
        }
        pending.append((path, record, post))
    for path, record, post in pending:
        write_json(path, record)
        write_json(ROOT / "migration/wordpress-source" / f'{post["ID"]}.json', {key: post[key] for key in ("ID", "URL", "title", "type", "date", "modified", "content")})
        manifest["records"].append({"sourceUrl": post["URL"], "sourceId": post["ID"], "route": record["route"], "file": path.relative_to(ROOT).as_posix()})
        print(f'Imported {record["route"]}', flush=True)
    # Update links in the first batch without replacing its edited readings or body text.
    for item in manifest["records"]:
        if item["sourceId"] not in existing_ids:
            continue
        path = ROOT / item["file"]
        record = json.loads(path.read_text(encoding="utf-8"))
        record["body"] = ImportedHTML(record["sourceUrl"], routes, media, ROOT, args.download_media, args.existing_site).render(record["body"])
        write_json(path, record)
    canonical_rows = [{"old_url": old, "new_url": route} for _, route, old in songs]
    write_json(ROOT / "migration/song-urls.json", canonical_rows)
    titles = {old: html.unescape(post["title"]) for post, _, old in songs}
    write_json(ROOT / "migration/song-titles.json", titles)
    payload = json.dumps([{**row, "title": titles[row["old_url"]]} for row in canonical_rows], ensure_ascii=False).replace("<", "\\u003c")
    template = (ROOT / "apps/content-site/song-url-form.html").read_text(encoding="utf-8")
    (ROOT / "migration/song-url-form.html").write_text(template.replace("__SONG_ROWS__", payload), encoding="utf-8")
    write_song_ime_data(ROOT)
    write_json(media_path, media)
    manifest["completedEnglishAt"] = datetime.now(timezone.utc).isoformat()
    manifest["deferred"] = {"songs": 0, "theEgg": [7647], "chinesePresentations": "later"}
    manifest["importedSongs"] = len(songs)
    manifest["status"] = "English source import complete; visual/editorial review and v3.2 work remain separate."
    write_json(manifest_path, manifest)
    print(f"Imported {len(songs)} songs and the English Egg story; {len(manifest['records'])} English records total.")


if __name__ == "__main__":
    main()
