"""Warn about compounds glossed by joining their characters' own glosses (audit 3.5).

A compound such as 羅馬字 glossed "horse; character; word" repeats the meanings
of 馬 and 字 instead of saying what the word means (romanisation). This check
lists every lexical compound whose gloss parts all come from the glosses of its
own characters' single-character entries, drawn from at least two of them. It
only warns: some such glosses are correct (平安 "safe; peaceful"), so the list
is for review, never an automatic fix.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TSV = ROOT / "data" / "hokkien_hanri_dict.tsv"
HANRI = re.compile(r"[㐀-䶿一-鿿豈-﫿\U00020000-\U0003134F]")


def gloss_parts(english: str) -> set[str]:
    return {part.strip().lower() for part in english.split(";") if part.strip()}


def joined_glosses(rows: list[dict]) -> list[dict]:
    lexical = [row for row in rows if row.get("entry_type") == "lexical"]
    by_character: dict[str, set[str]] = defaultdict(set)
    for row in lexical:
        if len(row["hanri"]) == 1 and HANRI.fullmatch(row["hanri"]):
            by_character[row["hanri"]] |= gloss_parts(row["english"])
    flagged = []
    for row in lexical:
        characters = HANRI.findall(row["hanri"])
        parts = gloss_parts(row["english"])
        if len(characters) < 2 or not parts:
            continue
        own = [by_character.get(character, set()) for character in characters]
        # Joined = every part is a character's own gloss, and the parts come
        # from at least two different characters (not one character's sense).
        if parts <= set().union(*own) and not any(parts <= single for single in own):
            flagged.append(row)
    return flagged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsv", type=Path, default=DEFAULT_TSV)
    parser.add_argument("--list", action="store_true", help="print every flagged compound")
    args = parser.parse_args()
    with args.tsv.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle, delimiter="\t") if row.get("entry_type")]
    flagged = joined_glosses(rows)
    print(f"Warning: {len(flagged)} compounds are glossed only with their characters' own glosses "
          f"(review; not an error).")
    for row in flagged if args.list else flagged[:10]:
        print(f"  {row['hanri']} {row['reading']} \"{row['english']}\" {row['entry_id']}")
    if not args.list and len(flagged) > 10:
        print(f"  … and {len(flagged) - 10} more; run with --list for all.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
