"""One-time reviewed dictionary sync for the author's v3.3 Hanri assignments."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from dictionary_editor_service import DictionaryEditorService, MAIN, read_table
from dictionary_editor_publish import changed_lookup_sources

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/history/harmonisation-3.3-dictionary.json"
REPLACEMENTS = {
    "U+AC10_00": ("噉", "감2"),
    "U+5230_U+4ECA_00": ("到𦤾", "ᄀᅷ2달1"),
    "U+4ECA_U+4ED4_00": ("𦤾仔", "달5아2"),
}
ADDITIONS = [
    {"hanri": "𦤾", "reading": "달1", "mandarin_trad": "現在; 剛剛", "mandarin_simp": "现在; 刚刚", "english": "now; just now"},
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
    after, saved, skipped = service.prepare(before, changes, allow_alternative=True)
    report = {"date": "2026-11-08", "decision": "Author-confirmed Hanri spellings from Orthography v3.3 section 4.5",
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
    print(json.dumps({key: report[key] for key in ("saved", "retiredIds", "skipped")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
