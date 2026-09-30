"""Assign Unicode-derived IDs and maintain the pre-release allocation registry."""

from __future__ import annotations

import argparse
import csv
import io
import os
import tempfile
from collections import defaultdict
from pathlib import Path

from dictionary_schema import (
    DICTIONARY_COLUMNS,
    ENTRY_ID_REGISTRY_COLUMNS,
    canonical_entry_headword,
    entry_id_base,
    entry_id_matches_headword,
    make_entry_id,
    valid_entry_id,
    valid_legacy_entry_id,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "data" / "hokkien_hanri_dict.tsv"
DEFAULT_REGISTRY_PATH = ROOT / "data" / "dictionary_entry_id_registry.tsv"
LEGACY_COLUMNS = DICTIONARY_COLUMNS[:-1]


def _serialize(rows: list[list[str]]) -> bytes:
    output = io.StringIO(newline="")
    csv.writer(output, delimiter="\t", lineterminator="\r\n").writerows(rows)
    return output.getvalue().encode("utf-8")


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", prefix=f".{path.name}.", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _read_registry(path: Path) -> list[list[str]]:
    if not path.exists():
        return [list(ENTRY_ID_REGISTRY_COLUMNS)]
    rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"), newline=""), delimiter="\t", strict=True))
    if not rows or tuple(rows[0]) != ENTRY_ID_REGISTRY_COLUMNS:
        raise ValueError(f"Registry header must be exactly: {' / '.join(ENTRY_ID_REGISTRY_COLUMNS)}")
    seen: set[str] = set()
    for line_number, row in enumerate(rows[1:], start=2):
        if len(row) != len(ENTRY_ID_REGISTRY_COLUMNS):
            raise ValueError(f"Registry line {line_number} has {len(row)} fields; expected 3")
        if row[0] in seen:
            raise ValueError(f"Registry line {line_number} repeats entry_id {row[0]!r}")
        if not valid_entry_id(row[0]) or row[2]:
            raise ValueError(f"Registry line {line_number} contains a pre-release alias or redirect")
        seen.add(row[0])
    return rows


def assign_ids(path: Path, registry_path: Path | None = None) -> int:
    registry_path = registry_path or path.with_name("dictionary_entry_id_registry.tsv")
    original = path.read_bytes()
    rows = list(csv.reader(io.StringIO(original.decode("utf-8"), newline=""), delimiter="\t", strict=True))
    if not rows:
        raise ValueError("TSV is empty")

    header = tuple(rows[0])
    if header not in {LEGACY_COLUMNS, DICTIONARY_COLUMNS}:
        raise ValueError("Expected the legacy six-column or current seven-column dictionary header")

    data_positions = [
        index for index, row in enumerate(rows)
        if index and row and not row[0].startswith("#")
    ]
    expected_fields = len(header)
    for position in data_positions:
        if len(rows[position]) != expected_fields:
            raise ValueError(f"Data row {position + 1} has {len(rows[position])} fields; expected {expected_fields}")
    if (
        header == DICTIONARY_COLUMNS
        and not registry_path.exists()
        and any(valid_entry_id(rows[position][6]) for position in data_positions)
    ):
        raise FileNotFoundError(
            f"Dictionary ID registry is required for existing Unicode IDs: {registry_path}"
        )

    registry_rows = _read_registry(registry_path)
    registry_by_id = {row[0]: row for row in registry_rows[1:]}
    next_suffixes: dict[str, int] = defaultdict(int)
    for row in registry_rows[1:]:
        if valid_entry_id(row[0]):
            base, suffix_text = row[0].rsplit("_", 1)
            next_suffixes[base] = max(next_suffixes[base], int(suffix_text) + 1)
    for position in data_positions:
        if header == DICTIONARY_COLUMNS and valid_entry_id(rows[position][6]):
            base, suffix_text = rows[position][6].rsplit("_", 1)
            next_suffixes[base] = max(next_suffixes[base], int(suffix_text) + 1)

    def allocate(headword: str) -> str:
        base = entry_id_base(headword)
        suffix = next_suffixes[base]
        next_suffixes[base] += 1
        return make_entry_id(headword, suffix)

    migrated = [row[:] for row in rows]
    migrated[0] = list(DICTIONARY_COLUMNS)
    assigned = 0
    active_ids: set[str] = set()

    for position in data_positions:
        row = rows[position]
        headword = canonical_entry_headword(row[1])
        old_id = row[6] if header == DICTIONARY_COLUMNS else ""
        if old_id and valid_entry_id(old_id):
            if not entry_id_matches_headword(old_id, headword):
                raise ValueError(f"Data row {position + 1}: entry_id does not match canonical headword {headword!r}")
            new_id = old_id
        elif old_id and valid_legacy_entry_id(old_id):
            new_id = allocate(headword)
            assigned += 1
        elif old_id:
            raise ValueError(f"Data row {position + 1}: invalid entry_id {old_id!r}")
        else:
            new_id = allocate(headword)
            assigned += 1

        if new_id in active_ids:
            raise ValueError(f"Duplicate assigned entry_id {new_id!r}")
        active_ids.add(new_id)
        migrated[position] = [*row[:6], new_id]

    # Ordinary allocation retains existing Unicode IDs. An approved pre-release
    # migration may revise them separately; registry-only suffixes stay reserved.
    for position in data_positions:
        entry_id = migrated[position][6]
        headword = canonical_entry_headword(migrated[position][1])
        existing = registry_by_id.get(entry_id)
        expected = [entry_id, headword, ""]
        if existing is None:
            registry_rows.append(expected)
            registry_by_id[entry_id] = expected
        elif existing != expected:
            raise ValueError(f"Registry metadata disagrees for active entry_id {entry_id!r}")

    tsv_encoded = _serialize(migrated)
    registry_encoded = _serialize(registry_rows)
    changed = tsv_encoded != original
    registry_changed = not registry_path.exists() or registry_path.read_bytes() != registry_encoded
    if changed:
        _atomic_write(path, tsv_encoded)
    if registry_changed:
        _atomic_write(registry_path, registry_encoded)

    if changed or registry_changed:
        print(
            f"Assigned/migrated {assigned} entry IDs; registered {len(registry_rows) - 1} Unicode IDs"
        )
    else:
        print(f"Already assigned: {len(data_positions)} Unicode entry IDs; no file change")
    return assigned


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_PATH)
    parser.add_argument("--registry", type=Path)
    args = parser.parse_args()
    assign_ids(args.path, args.registry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
