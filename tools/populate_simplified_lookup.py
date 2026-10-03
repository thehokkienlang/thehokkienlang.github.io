"""Append/populate Simplified lookup metadata without changing existing cells/order."""

import argparse
import csv
import io
from pathlib import Path

from simplified_lookup import contains_hanri, review_case, simplified_field_errors, simplified_headword


ROOT = Path(__file__).resolve().parents[1]


def populate(path: Path, report: Path) -> dict:
    original = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"), newline=""), delimiter="\t"))
    columns = original[0]
    if "simplified" in columns:
        raise ValueError("Simplified column already exists; this migration must not overwrite manual edits")
    rows = [columns + ["simplified"]]
    reviews = []
    counts = dict(total=0, hanri=0, pure_hangul=0, other_empty=0, different=0, identical=0, review=0)
    for row in original[1:]:
        if row[0].startswith("#"):
            rows.append(row[:])
            continue
        record = dict(zip(columns, row))
        headword = record["hanri"]
        simplified = simplified_headword(headword)
        assert not simplified_field_errors(headword, simplified)
        rows.append(row + [simplified])
        counts["total"] += 1
        if contains_hanri(headword):
            counts["hanri"] += 1
            counts["different" if simplified != headword else "identical"] += 1
        elif any("\u1100" <= char <= "\u11ff" or "\u3130" <= char <= "\u318f" or "\uac00" <= char <= "\ud7ff" for char in headword):
            counts["pure_hangul"] += 1
        else:
            counts["other_empty"] += 1
        review = review_case(headword, simplified) if simplified else None
        if review:
            alternatives, reason = review
            reviews.append([record["entry_id"], headword, simplified, "; ".join(alternatives), reason])
    assert all(new[:-1] == old for old, new in zip(original[1:], rows[1:]) if not old[0].startswith("#"))
    output = io.StringIO(newline="")
    csv.writer(output, delimiter="\t", lineterminator="\r\n").writerows(rows)
    path.write_bytes(output.getvalue().encode("utf-8"))
    counts["review"] = len(reviews)
    lines = ["# Simplified lookup manual review", "", "Generated with OpenCC tw2s, opencc-python-reimplemented 0.1.7. Canonical headwords and IDs are unchanged. Every Hanri row is populated. Unlikely secondary glyphs and Traditional 著 alternatives to Simplified 着 are excluded from review.", "", "| entry_id | Canonical Hanri | Chosen Simplified | Alternatives | Reason |", "| --- | --- | --- | --- | --- |"]
    lines.extend("| " + " | ".join(cell.replace("|", "\\|") for cell in record) + " |" for record in reviews)
    lines.extend(["", "## Counts", "", *(f"- {name}: {count}" for name, count in counts.items()), ""])
    report.write_text("\n".join(lines), encoding="utf-8")
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/hokkien_hanri_dict.tsv")
    parser.add_argument("--report", type=Path, default=ROOT / "docs/simplified-lookup-review.md")
    args = parser.parse_args()
    print(populate(args.input, args.report))
