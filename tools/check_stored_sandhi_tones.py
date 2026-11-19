"""Stored readings keep Taipei sandhi digits: no stored open syllable that is joined to the next one
carries tone 4 (docs/sandhi-toggle-plan.md).

Singapore sandhi is derived from the Taipei digits (an open sandhi tone 1 becomes 4), never stored. A
reading such as 정4래5 would be a Singapore reading written into the data, so this check fails on it.
It reads the dictionary's reading column (not its correction aliases) and the lyric text of every
song source. A syllable before
a space, a separator or the end of the reading is a citation syllable, where tone 4 is correct.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "desktop"))

from tangliengim_engine import is_checked_final_before_tone  # noqa: E402


def is_hangul(char: str) -> bool:
    code = ord(char)
    return 0xAC00 <= code <= 0xD7A3 or 0x1100 <= code <= 0x11FF or 0x3130 <= code <= 0x318F or 0xA960 <= code <= 0xA97F


def non_final_open_tone4(reading: str) -> list[int]:
    """Positions of a '4' that follows an open syllable and is directly followed by another syllable."""
    found = []
    for index, char in enumerate(reading):
        if char != "4" or index == 0 or not is_hangul(reading[index - 1]):
            continue
        if index + 1 >= len(reading) or not is_hangul(reading[index + 1]):
            continue  # citation position: a space, separator or the end follows
        if not is_checked_final_before_tone(reading, index):
            found.append(index)
    return found


def dictionary_problems() -> list[str]:
    problems = []
    with open(ROOT / "data" / "hokkien_hanri_dict.tsv", encoding="utf-8", newline="") as handle:
        rows = csv.reader(handle, delimiter="\t")
        header = next(rows)
        column, kind = header.index("reading"), header.index("entry_type")
        for number, row in enumerate(rows, start=2):
            # A correction alias is a mistyped form (marked with *) that points at the real reading.
            if len(row) > kind and row[kind] == "correction_alias":
                continue
            if len(row) > column and row[column] and not row[0].startswith("#"):
                if non_final_open_tone4(row[column]):
                    problems.append(f"dictionary row {number}: {row[column]}")
    return problems


def song_problems() -> list[str]:
    problems = []
    for path in sorted((ROOT / "content" / "songs").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        editor = record.get("songEditor") if isinstance(record.get("songEditor"), dict) else {}
        for position, item in enumerate(editor.get("lyrics") or [], start=1):
            text = item.get("text", "") if isinstance(item, dict) else ""
            if non_final_open_tone4(text):
                problems.append(f"{path.name} lyric {position}: {text}")
    return problems


def main() -> int:
    problems = dictionary_problems() + song_problems()
    if problems:
        print("Stored readings must use Taipei sandhi digits; a non-final open syllable with tone 4 is a")
        print("Singapore reading. Fix it with the Taipei digit (1), or report it for review:")
        for problem in problems[:40]:
            print("  " + problem)
        if len(problems) > 40:
            print(f"  ... and {len(problems) - 40} more")
        return 1
    print("OK: no stored reading has a tone 4 on an open syllable joined to the next syllable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
