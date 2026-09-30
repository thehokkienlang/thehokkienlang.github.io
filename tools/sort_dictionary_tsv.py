"""Sort the Tangliengim TSV in canonical reading order on demand."""

from __future__ import annotations

import argparse
import csv
import io
import os
import tempfile
from collections import Counter
from pathlib import Path

from tangliengim_collation import row_sort_key
from validate_dictionary_tsv import DEFAULT_PATH, EXPECTED_HEADER, validate


def _serialize(rows: list[list[str]]) -> bytes:
    output = io.StringIO(newline="")
    csv.writer(output, delimiter="\t", lineterminator="\r\n").writerows(rows)
    return output.getvalue().encode("utf-8")


def sort_tsv(path: Path) -> int:
    errors = validate(path)
    if errors:
        raise ValueError("Refusing to sort an invalid TSV: " + "; ".join(errors))

    original = path.read_bytes()
    rows = list(csv.reader(io.StringIO(original.decode("utf-8"), newline=""), delimiter="\t", strict=True))
    if rows[0] != EXPECTED_HEADER or _serialize(rows) != original:
        raise ValueError("TSV cannot be rewritten byte-for-byte except for row order")

    positions = [index for index, row in enumerate(rows) if index and not row[0].startswith("#")]
    items = [(index, rows[index]) for index in positions]
    ordered = sorted(
        items,
        key=lambda item: row_sort_key(dict(zip(EXPECTED_HEADER, item[1])), EXPECTED_HEADER),
    )
    result = [row[:] for row in rows]
    for position, (_old_position, row) in zip(positions, ordered):
        result[position] = row

    assert Counter(map(tuple, result[1:])) == Counter(map(tuple, rows[1:]))
    moved = sum(position != old_position for position, (old_position, _row) in zip(positions, ordered))
    encoded = _serialize(result)
    if encoded == original:
        print(f"Already canonical: {len(positions)} entries; no file change")
        return 0

    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", prefix=f".{path.name}.", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()

    print(f"Sorted {len(positions)} entries; {moved} rows changed physical position")
    return moved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_PATH)
    args = parser.parse_args()
    sort_tsv(args.path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
