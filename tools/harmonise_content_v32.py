"""Audit, apply, or verify the reviewed Harmonisation 3.2 content migration."""

import argparse
import json
from collections import Counter
from pathlib import Path

from content_harmonisation import apply_edits, digest, propose, restore_body

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "docs/harmonisation-3.2-audit.json"
ARCHIVED = {"/songs/translation-notes/", "/read/literature/lychee-mirror/"}


def active_records(root):
    manifest = json.loads((root / "migration/wordpress-map.json").read_text(encoding="utf-8"))
    for item in manifest["records"]:
        if item["route"] not in ARCHIVED:
            yield item, json.loads((root / item["file"]).read_text(encoding="utf-8"))


def audit(root):
    records = {}
    totals, retained_totals = Counter(), Counter()
    for item, record in active_records(root):
        edits, retained = propose(record)
        after = apply_edits(record["body"], edits)
        retained_counts = Counter((row["base"], row["reason"]) for row in retained)
        cases = {}
        for row in retained:
            cases.setdefault((row["base"], row["reason"]), row["context"])
        records[item["file"]] = {
            "id": record["id"], "file": item["file"], "route": record["route"], "sourceId": record["sourceId"],
            "beforeSha256": digest(record["body"]), "afterSha256": digest(after),
            "edits": edits,
            "retained": [{"base": base, "reason": reason, "count": count,
                          "example": cases[base, reason]} for (base, reason), count in retained_counts.items()],
        }
        totals.update((edit["base"], edit["hanri"], edit["rule"]) for edit in edits)
        retained_totals.update(retained_counts)
    return {
        "project": "Harmonisation 3.2", "date": "2026-10-25", "version": 1,
        "reference": "Tangliengim_Orthography_v3.2.pdf, sections 4.1-4.5; Appendix C.4",
        "referenceSha256": "b33f0c71f643e3654b19e9c48cd0e285097c7d7cbcfbb8b255bb070761ed3c64",
        "scope": "Authored mixed-script reading text; existing readings and published URLs are preserved.",
        "exclusions": ["ruby pronunciation annotations", "apostrophised neutral-tone domains",
                       "phonetic teaching/reference material", "dictionary and IME pronunciation data",
                       "foreign transcriptions and names", "Teochew and Mandarin lyrics", "archived WordPress originals"],
        "changes": [{"base": base, "hanri": hanri, "rule": rule, "count": count}
                    for (base, hanri, rule), count in totals.most_common()],
        "retained": [{"base": base, "reason": reason, "count": count}
                     for (base, reason), count in retained_totals.most_common()],
        "records": records,
    }


def verify(root, ledger):
    checked = 0
    for key, entry in ledger["records"].items():
        record = json.loads((root / entry["file"]).read_text(encoding="utf-8"))
        if record["id"] != entry["id"] or record["route"] != entry["route"]:
            raise ValueError(f"Content identity or URL changed: {key}")
        restored = restore_body(record["body"], entry)
        if apply_edits(restored, entry["edits"]) != record["body"]:
            raise ValueError(f"Cannot replay reviewed edits: {key}")
        if propose(record)[0]:
            raise ValueError(f"Unapplied mandatory spelling edits remain: {key}")
        checked += 1
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        ledger = json.loads(args.output.read_text(encoding="utf-8"))
        print(f"Verified {verify(args.root, ledger)} reviewed records; source recovery and URL identity match.")
        return
    if args.apply and args.output.exists():
        raise ValueError("Refusing to replace an existing reviewed migration ledger")
    ledger = audit(args.root)
    if args.apply:
        for item, record in active_records(args.root):
            reviewed = ledger["records"][item["file"]]
            record["body"] = apply_edits(record["body"], reviewed["edits"])
            record["orthography"] = {"target": "3.2", "review": "mixed-script-audited",
                                     "scope": "section-4 mixed-script spellings",
                                     "v32Changes": "applied" if reviewed["edits"] else "not-required",
                                     "audit": "docs/harmonisation-3.2-audit.json"}
            (args.root / item["file"]).write_text(json.dumps(record, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(ledger, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("Reviewed records:", len(ledger["records"]))
    print("Edited records:", sum(bool(row["edits"]) for row in ledger["records"].values()))
    print("Changes:", sum(row["count"] for row in ledger["changes"]))
    for row in ledger["changes"]:
        print(row["base"], "->", row["hanri"], row["count"], row["rule"])
    print("Needs review:")
    print([row for row in ledger["retained"] if row["reason"] == "needs-review"])


if __name__ == "__main__":
    main()
