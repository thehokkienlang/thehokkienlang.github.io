"""One-time Task 6e migration from _01-based to _00-based entry IDs."""

from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path

from assign_dictionary_entry_ids import _atomic_write, _serialize
from dictionary_schema import DICTIONARY_COLUMNS, ENTRY_ID_REGISTRY_COLUMNS, split_entry_id, is_comment_row
from validate_dictionary_tsv import DEFAULT_PATH, validate


def _read_rows(path: Path) -> tuple[bytes, list[list[str]]]:
    original = path.read_bytes()
    rows = list(csv.reader(io.StringIO(original.decode("utf-8"), newline=""), delimiter="\t", strict=True))
    if _serialize(rows) != original:
        raise ValueError(f"Refusing to rewrite noncanonical TSV formatting: {path}")
    return original, rows


def migrate(path: Path, registry_path: Path | None = None) -> int:
    registry_path = registry_path or path.with_name("dictionary_entry_id_registry.tsv")
    errors = validate(path, registry_path)
    if errors:
        raise ValueError("Refusing to migrate invalid dictionary data: " + "; ".join(errors))

    old_tsv, rows = _read_rows(path)
    old_registry, registry_rows = _read_rows(registry_path)
    if tuple(rows[0]) != DICTIONARY_COLUMNS or tuple(registry_rows[0]) != ENTRY_ID_REGISTRY_COLUMNS:
        raise ValueError("Dictionary or registry header changed")

    unicode_ids = [row[0] for row in registry_rows[1:] if split_entry_id(row[0]) is not None]
    bases: dict[str, set[int]] = {}
    for entry_id in unicode_ids:
        base, ordinal = split_entry_id(entry_id)
        bases.setdefault(base, set()).add(ordinal)
    if not bases:
        raise ValueError("Registry has no Unicode entry IDs")
    has_base = [0 in suffixes for suffixes in bases.values()]
    if all(has_base):
        print(f"Already zero-based: {len(unicode_ids)} Unicode entry IDs; no file change")
        return 0
    if any(has_base) or any(1 not in suffixes for suffixes in bases.values()):
        raise ValueError("Mixed or incomplete ordinal scheme; refusing automatic migration")

    replacements = {
        entry_id: f"{base}_{ordinal - 1:02d}"
        for entry_id in unicode_ids
        for base, ordinal in [split_entry_id(entry_id)]
    }
    if len(set(replacements.values())) != len(replacements):
        raise ValueError("Ordinal migration would create duplicate IDs")

    migrated = [row[:] for row in rows]
    migrated_count = 0
    for index, row in enumerate(migrated[1:], start=1):
        if row and not is_comment_row(row):
            id_column = DICTIONARY_COLUMNS.index("entry_id")
            if row[id_column] not in replacements:
                raise ValueError(f"TSV row {index + 1} has no registry identity")
            row[id_column] = replacements[row[id_column]]
            migrated_count += 1

    migrated_registry = [row[:] for row in registry_rows]
    for row in migrated_registry[1:]:
        row[0] = replacements.get(row[0], row[0])
        row[2] = replacements.get(row[2], row[2])

    new_tsv = _serialize(migrated)
    new_registry = _serialize(migrated_registry)
    try:
        _atomic_write(registry_path, new_registry)
        _atomic_write(path, new_tsv)
        errors = validate(path, registry_path)
        if errors:
            raise ValueError("Migrated dictionary failed validation: " + "; ".join(errors))
    except Exception:
        _atomic_write(registry_path, old_registry)
        _atomic_write(path, old_tsv)
        raise

    print(f"Migrated {migrated_count} TSV entries and {len(unicode_ids)} registry IDs to _00-based ordinals")
    return migrated_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_PATH)
    parser.add_argument("--registry", type=Path)
    args = parser.parse_args()
    migrate(args.path, args.registry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
