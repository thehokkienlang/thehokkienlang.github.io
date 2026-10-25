"""One-time reviewed dictionary sync for the author's v3.2.1 Hanri assignments."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from dictionary_editor_service import DictionaryEditorService, MAIN, read_table
from dictionary_editor_publish import changed_lookup_sources

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/harmonisation-3.2.1-dictionary.json"
REPLACEMENTS = {
    "U+BED0_00": ("𡚸", "뻐2"),
    "U+C5D0_U+B2F9_00": ("會當", "에당"),
    "U+C790_U+BED0_00": ("㜁𡚸", "자5뻐2"),
    "U+23350_U+B2F9_00": ("𣍐當", "뾔당"),
}
ADDITIONS = [
    {"hanri": "呵咾", "reading": "오5로2", "mandarin_trad": "稱讚", "english": "praise"},
    {"hanri": "丈夫", "reading": "다5버1", "mandarin_trad": "男人", "english": "man; male"},
    {"hanri": "摕", "reading": "텧1", "mandarin_trad": "拿; 持", "english": "take; hold"},
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if REPORT.exists():
        raise ValueError("The reviewed dictionary sync has already been applied")
    service = DictionaryEditorService(ROOT)
    before = service.files()
    rows = {row["entry_id"]: row for row in read_table(before[MAIN])[1] if row.get("entry_id")}
    changes = [{**rows[identity], "hanri": word, "reading": reading, "simplified": "", "entry_type": "lexical"}
               for identity, (word, reading) in REPLACEMENTS.items()]
    changes.extend(ADDITIONS)
    # Reuse the existing low citation-tone 當 rather than creating a duplicate.
    assert any(row["hanri"] == "當" and row["reading"] == "당" for row in rows.values())
    after, saved, skipped = service.prepare(before, changes, allow_alternative=True)
    report = {"date": "2026-10-25", "decision": "Author-confirmed Hanri spellings; starred forms belong to manual v3.2.1",
              "manualV321": ["丈夫", "㜁𡚸", "𡚸", "摕"],
              "beforeFiles": {name: hashlib.sha256(raw).hexdigest() for name, raw in before.items()},
              "afterFiles": {name: hashlib.sha256(raw).hexdigest() for name, raw in after.items()},
              "saved": saved, "retiredIds": list(REPLACEMENTS), "skipped": skipped,
              "changedIds": changed_lookup_sources(before, after)}
    new_rows = {row["entry_id"]: row for row in read_table(after[MAIN])[1] if row.get("entry_id")}
    for identity, row in rows.items():
        if identity not in REPLACEMENTS:
            assert new_rows[identity] == row, "Unrelated dictionary entry changed: " + identity
    if args.apply:
        with service.locked():
            if service.files() != before:
                raise ValueError("Dictionary changed during review; rerun the sync")
            service.commit_files(before, after)
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
