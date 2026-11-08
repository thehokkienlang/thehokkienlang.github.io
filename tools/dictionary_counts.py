"""Print the dictionary's current record counts (audit B6).

The release gate runs this after building public/data, so the counts that
docs/dictionary-tsv-schema.md used to record by hand are always current.

    python tools/dictionary_counts.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RUNTIME = ROOT / "public" / "data" / "hokkien-hanri-dict.json"


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [row for row in csv.DictReader(handle, delimiter="\t") if not next(iter(row.values()), "").startswith("#")]


def counts() -> dict[str, int]:
    data = json.loads(RUNTIME.read_text(encoding="utf-8"))
    entries = data["entries"]
    sandhi = data["counts"]["auto_sandhi_entries"]
    sources = len(entries) - sandhi
    current_ids = {row["entry_id"] for row in rows(DATA / "hokkien_hanri_dict.tsv")}
    registry = rows(DATA / "dictionary_entry_id_registry.tsv")
    defunct = {row["entry_id"] for row in rows(DATA / "dictionary_defunct.tsv")}
    registered = {row["entry_id"] for row in registry}
    return {
        "source records": sources,
        "runtime-active source records": data["counts"]["active_entries"],
        "inactive source records (number pronunciations)": data["counts"]["inactive_entries"],
        "generated sandhi views": sandhi,
        "total runtime JSON records": len(entries),
        "ID registry assignments": len(registry),
        "registry IDs of current records": len(registered & current_ids),
        "registry IDs of defunct records": len(registered & defunct),
        "registry-only reservations": len(registered - current_ids - defunct),
    }


def main() -> int:
    for label, value in counts().items():
        print(f"{label}: {value:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
