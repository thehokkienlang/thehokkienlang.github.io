"""Import authored Chinese presentations and retain read-only WordPress snapshots."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path

from import_wordpress import ImportedHTML, fetch_export, source_key, write_json
from site_languages import CHINESE_PAGES, LANGUAGES, PREFIXES

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path)
    parser.add_argument("--download-media", action="store_true")
    args = parser.parse_args()
    exported = json.loads(args.export.read_text(encoding="utf-8-sig")) if args.export else fetch_export()
    posts = {post["ID"]: post for post in exported["posts"]}
    manifest_path = ROOT / "migration/wordpress-map.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing_ids = {item["sourceId"] for item in manifest["records"]}
    if existing_ids.intersection(spec[0] for spec in CHINESE_PAGES):
        raise ValueError("Chinese sources already imported; refusing to overwrite editorial records")
    missing = {spec[0] for spec in CHINESE_PAGES} - posts.keys()
    if missing:
        raise ValueError(f"Missing Chinese source pages: {sorted(missing)}")
    routes = {source_key(item["sourceUrl"]): item["route"] for item in manifest["records"]}
    for identity, language, _, _, base, _ in CHINESE_PAGES:
        routes[source_key(posts[identity]["URL"])] = PREFIXES[language] + base
    media_path = ROOT / "migration/wordpress-media.json"
    media = json.loads(media_path.read_text(encoding="utf-8"))
    pending = []
    for identity, language, kind, slug, base, title in CHINESE_PAGES:
        post = posts[identity]
        folder = PREFIXES[language].lstrip("/")
        path = ROOT / "content" / folder / kind / (slug + ".json")
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite {path}")
        record = {
            "id": slug, "type": kind, "language": language, "title": title,
            "originalTitle": html.unescape(post["title"]), "route": PREFIXES[language] + base,
            "sourceUrl": post["URL"], "sourceId": identity, "sourceModified": post["modified"],
            "sourceSha256": hashlib.sha256(post["content"].encode()).hexdigest(),
            "orthography": {"target": "3.1", "review": "source-preserved", "v32Changes": "deferred"},
            "body": ImportedHTML(post["URL"], routes, media, ROOT, args.download_media).render(post["content"]),
        }
        pending.append((path, record, post))
    for path, record, post in pending:
        write_json(path, record)
        write_json(ROOT / "migration/wordpress-source" / f'{post["ID"]}.json', {
            key: post[key] for key in ("ID", "URL", "title", "type", "date", "modified", "content")
        })
        manifest["records"].append({"sourceUrl": post["URL"], "sourceId": post["ID"], "route": record["route"], "file": path.relative_to(ROOT).as_posix()})
        print(f'Imported {record["route"]}', flush=True)
    manifest["languages"] = list(LANGUAGES)
    manifest["completedChineseAt"] = datetime.now(timezone.utc).isoformat()
    manifest["deferred"] = {"songs": 0, "theEgg": [], "chinesePresentations": 0}
    manifest["status"] = "English and authored Chinese source imports complete; v3.1 editorial review and v3.2 changes remain pending."
    write_json(media_path, media)
    write_json(manifest_path, manifest)
    print(f"Imported {len(pending)} Chinese presentations; WordPress unchanged.")


if __name__ == "__main__":
    main()
