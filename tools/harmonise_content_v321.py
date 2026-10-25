"""Apply the author's seven reviewed Hanri assignments without rewriting readings."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from content_harmonisation import (
    HANGUL, PROTECTED, apply_edits, atoms_for, digest, reading_ruby, word_at,
)
from harmonise_content_v32 import active_records
from song_title_readings import phonetics

ROOT = Path(__file__).resolve().parents[1]
LEDGER = "docs/harmonisation-3.2.1-audit.json"
SPELLINGS = {
    "오로": "呵咾", "다버": "丈夫", "자뻐": "㜁𡚸", "뻐": "𡚸",
    "에당": "會當", "당": "當", "텧": "摕",
}
V321 = {"다버", "자뻐", "뻐", "텧"}


def propose(record, *, title=False):
    if record["type"] not in {"songs", "stories"} or record.get("titleRuby") or record["route"] == "/songs/月下煮茶/":
        return []
    atoms = atoms_for(record)
    protected = set()
    for index, atom in enumerate(atoms):
        for word in PROTECTED.keys() - SPELLINGS.keys():
            if end := word_at(atoms, index, word):
                protected.update(range(index, end))
    edits, consumed = [], set()
    for index, atom in enumerate(atoms):
        if index in consumed or index in protected or atom.kind != "hangul" or atom.neutral:
            continue
        if atom.block is None or atom.block.tag in {"td", "th", "figcaption"}:
            continue
        for word, hanri in SPELLINGS.items():
            end = word_at(atoms, index, word)
            if not end or any(i in protected for i in range(index, end)):
                continue
            members = atoms[index:end]
            following = atoms[end] if end < len(atoms) else None
            connected = bool(following and following.block is atom.block and following.base and
                             (HANGUL.search(following.base[0]) or phonetics().is_cjk_char(following.base[0])))
            reading = "".join(member.reading for member in members)
            edits.append({"start": atom.start, "end": members[-1].end,
                          "before": record["body"][atom.start:members[-1].end],
                          "after": hanri if title else reading_ruby(hanri, reading, connected),
                          "base": word, "hanri": hanri, "reading": reading,
                          "rule": "v3.2.1" if word in V321 else "author-approved-Hanri"})
            consumed.update(range(index, end))
            break
    return edits


def migrate(root, *, apply=False):
    ledger_path = root / LEDGER
    if apply and ledger_path.exists():
        raise ValueError("Refusing to overwrite the reviewed v3.2.1 ledger")
    records, totals = {}, Counter()
    for item, record in active_records(root):
        edits = propose(record)
        title_record = {**record, "type": "stories", "body": "<p>" + record["title"] + "</p>"}
        title_edits = propose(title_record, title=True)
        new_title = apply_edits(title_record["body"], title_edits)[3:-4]
        if not edits and not title_edits:
            continue
        after = apply_edits(record["body"], edits)
        records[item["file"]] = {"file": item["file"], "route": record["route"],
                                 "beforeSha256": digest(record["body"]), "afterSha256": digest(after),
                                 "edits": edits, "titleBefore": record["title"], "titleAfter": new_title}
        totals.update((edit["base"], edit["hanri"]) for edit in edits)
        if apply:
            record["body"], record["title"] = after, new_title
            record.setdefault("orthography", {})["v321Audit"] = LEDGER
            (root / item["file"]).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ledger = {"project": "Hanri assignments and v3.2.1 patches", "date": "2026-10-25",
              "spellings": SPELLINGS, "manualV321": sorted(V321),
              "scope": "Mixed running text and display titles; URLs, ruby readings, neutral domains and transcriptions preserved",
              "changes": [{"base": base, "hanri": hanri, "count": count} for (base, hanri), count in totals.items()],
              "records": records}
    if apply:
        ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ledger


def restore(body, entry):
    if digest(body) != entry["afterSha256"]:
        raise ValueError("Content differs from the reviewed v3.2.1 patch")
    inverse, shift = [], 0
    for edit in entry["edits"]:
        start = edit["start"] + shift
        inverse.append({"start": start, "end": start + len(edit["after"]), "before": edit["after"], "after": edit["before"]})
        shift += len(edit["after"]) - len(edit["before"])
    original = apply_edits(body, inverse)
    if digest(original) != entry["beforeSha256"]:
        raise ValueError("Cannot recover the pre-v3.2.1 text")
    return original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        ledger = json.loads((ROOT / LEDGER).read_text(encoding="utf-8"))
        for file, entry in ledger["records"].items():
            record = json.loads((ROOT / file).read_text(encoding="utf-8"))
            restore(record["body"], entry)
            if record["title"] != entry["titleAfter"] or record["route"] != entry["route"] or propose(record):
                raise ValueError("Unreviewed title, URL, or spelling: " + file)
        print("Verified", len(ledger["records"]), "reversible v3.2.1 page patches")
    else:
        ledger = migrate(ROOT, apply=args.apply)
        print(json.dumps({"pages": len(ledger["records"]), "changes": ledger["changes"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
