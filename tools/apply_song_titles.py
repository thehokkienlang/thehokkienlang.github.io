"""Apply a completed display-title form without changing published song URLs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from import_wordpress import source_key, write_json

ROOT = Path(__file__).resolve().parents[1]


def apply_titles(root, form_path):
    rows = json.loads(form_path.read_text(encoding="utf-8-sig"))
    manifest = json.loads((root / "migration/wordpress-map.json").read_text(encoding="utf-8"))
    records = {}
    for item in manifest["records"]:
        if not item["file"].startswith("content/songs/"):
            continue
        path = root / item["file"]
        records[source_key(item["sourceUrl"])] = (path, json.loads(path.read_text(encoding="utf-8")))
    if not isinstance(rows, list) or len(rows) != len(records):
        raise ValueError(f"Expected exactly {len(records)} completed song rows")
    canonical = json.loads((root / "migration/song-urls.json").read_text(encoding="utf-8"))
    canonical_by_source = {source_key(row["old_url"]): row for row in canonical}
    seen, changes = set(), []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"old_url", "new_url", "display_title"}:
            raise ValueError("Each row must contain old_url, new_url, and display_title")
        key = source_key(row["old_url"])
        if key in seen or key not in records or key not in canonical_by_source:
            raise ValueError(f"Unknown or duplicate song source: {row['old_url']}")
        seen.add(key)
        path, record = records[key]
        if row["new_url"] != record["route"] or row["new_url"] != canonical_by_source[key]["new_url"]:
            raise ValueError(f"Published URL changes require a separate redirect update: {row['new_url']}")
        if not isinstance(row["display_title"], str) or not row["display_title"].strip():
            raise ValueError(f"Missing displayed title for {row['old_url']}")
        record["title"] = row["display_title"]
        canonical_by_source[key]["display_title"] = row["display_title"]
        changes.append((path, record))
    # Validate the complete batch before writing any editorial records.
    for path, record in changes:
        write_json(path, record)
    write_json(root / "migration/song-urls.json", canonical)
    source_titles = json.loads((root / "migration/song-titles.json").read_text(encoding="utf-8"))
    payload = json.dumps([{**row, "title": source_titles[row["old_url"]]} for row in canonical], ensure_ascii=False).replace("<", "\\u003c")
    template = (root / "apps/content-site/song-url-form.html").read_text(encoding="utf-8")
    (root / "migration/song-url-form.html").write_text(template.replace("__SONG_ROWS__", payload), encoding="utf-8")
    return len(changes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("form", type=Path)
    args = parser.parse_args()
    print(f"Applied {apply_titles(ROOT, args.form)} display titles; all URLs preserved.")


if __name__ == "__main__":
    main()
