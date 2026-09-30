"""Validate the Tangliengim dictionary TSV structure without changing it."""

from __future__ import annotations

import argparse
import csv
import io
import unicodedata
from pathlib import Path

from dictionary_schema import (
    DICTIONARY_COLUMNS,
    ENTRY_ID_REGISTRY_COLUMNS,
    canonical_entry_headword,
    entry_id_matches_headword,
    valid_entry_id,
)
from tangliengim_collation import ENTRY_TYPE_ORDER, out_of_order_pairs


EXPECTED_HEADER = list(DICTIONARY_COLUMNS)
ENTRY_TYPES = set(ENTRY_TYPE_ORDER)
DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "hokkien_hanri_dict.tsv"
DEFAULT_REGISTRY_PATH = DEFAULT_PATH.with_name("dictionary_entry_id_registry.tsv")


def validate_registry(path: Path, active_ids: dict[str, str]) -> list[str]:
    errors: list[str] = []
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return [f"cannot read ID registry {path}: {exc}"]
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append("ID registry: UTF-8 BOM is not allowed")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return errors + [f"ID registry is not valid UTF-8: {exc}"]
    crlf_count = raw.count(b"\r\n")
    if raw.count(b"\r") != crlf_count or raw.count(b"\n") != crlf_count:
        errors.append("ID registry must use CRLF line endings")
    if raw and not raw.endswith(b"\r\n"):
        errors.append("ID registry must end with a CRLF newline")

    registry: dict[str, tuple[str, str]] = {}
    try:
        rows = csv.reader(io.StringIO(text, newline=""), delimiter="\t", strict=True)
        header = next(rows, None)
        if header != list(ENTRY_ID_REGISTRY_COLUMNS):
            return errors + [f"ID registry header must be exactly: {' / '.join(ENTRY_ID_REGISTRY_COLUMNS)}"]
        for row in rows:
            line_number = rows.line_num
            if len(row) != len(ENTRY_ID_REGISTRY_COLUMNS):
                errors.append(f"ID registry line {line_number}: expected 3 fields, found {len(row)}")
                continue
            entry_id, headword, redirect = row
            if any(cell != cell.strip() for cell in row):
                errors.append(f"ID registry line {line_number}: surrounding whitespace")
            if any(unicodedata.normalize("NFC", cell) != cell for cell in row):
                errors.append(f"ID registry line {line_number}: value is not NFC-normalized")
            if entry_id in registry:
                errors.append(f"ID registry line {line_number}: duplicate entry_id {entry_id!r}")
                continue
            if not valid_entry_id(entry_id):
                errors.append(f"ID registry line {line_number}: invalid entry_id {entry_id!r}")
            if not headword or canonical_entry_headword(headword) != headword:
                errors.append(f"ID registry line {line_number}: canonical_headword is invalid")
            if headword and not entry_id_matches_headword(entry_id, headword):
                errors.append(f"ID registry line {line_number}: entry_id does not match canonical_headword")
            if redirect:
                errors.append(f"ID registry line {line_number}: redirects are not used before ID release")
            if redirect == entry_id:
                errors.append(f"ID registry line {line_number}: entry_id cannot redirect to itself")
            registry[entry_id] = (headword, redirect)
    except (csv.Error, StopIteration) as exc:
        return errors + [f"invalid ID registry structure: {exc}"]

    for entry_id, (headword, redirect) in registry.items():
        if redirect and redirect not in registry:
            errors.append(f"ID registry: redirect target {redirect!r} for {entry_id!r} is missing")
    for entry_id in registry:
        visited: set[str] = set()
        cursor = entry_id
        while cursor in registry and registry[cursor][1]:
            if cursor in visited:
                errors.append(f"ID registry: redirect cycle includes {entry_id!r}")
                break
            visited.add(cursor)
            cursor = registry[cursor][1]

    for entry_id, headword in active_ids.items():
        row = registry.get(entry_id)
        if row is None:
            errors.append(f"ID registry: active entry_id {entry_id!r} is missing")
        elif row != (headword, ""):
            errors.append(f"ID registry: active entry_id {entry_id!r} has mismatched metadata or redirect")
    return errors


def validate(path: Path, registry_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]

    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append("UTF-8 BOM is not allowed")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return errors + [f"file is not valid UTF-8: {exc}"]

    crlf_count = raw.count(b"\r\n")
    if raw.count(b"\r") != crlf_count:
        errors.append("file contains a bare CR; use CRLF line endings")
    if raw.count(b"\n") != crlf_count:
        errors.append("file contains a bare LF; use CRLF line endings")
    if raw and not raw.endswith(b"\r\n"):
        errors.append("file must end with a CRLF newline")

    try:
        rows = csv.reader(io.StringIO(text, newline=""), delimiter="\t", strict=True)
        header = next(rows, None)
        if header != EXPECTED_HEADER:
            errors.append(f"header must be exactly: {' / '.join(EXPECTED_HEADER)}")
            return errors

        entry_count = 0
        data_rows: list[dict[str, str]] = []
        entry_ids: set[str] = set()
        active_ids: dict[str, str] = {}
        for row in rows:
            line_number = rows.line_num
            if not row:
                errors.append(f"line {line_number}: blank row")
                continue
            if row[0].startswith("#"):
                continue
            if len(row) != len(EXPECTED_HEADER):
                errors.append(f"line {line_number}: expected 7 fields, found {len(row)}")
                continue
            entry_count += 1
            data_rows.append(dict(zip(EXPECTED_HEADER, row)))
            for column, cell in enumerate(row, 1):
                if cell != cell.strip():
                    errors.append(f"line {line_number}, field {column}: surrounding whitespace")
                if unicodedata.normalize("NFC", cell) != cell:
                    errors.append(f"line {line_number}, field {column}: value is not NFC-normalized")
            if not row[0]:
                errors.append(f"line {line_number}: reading is empty")
            if not row[1]:
                errors.append(f"line {line_number}: hanri is empty")
            if not row[2].isascii() or not row[2].isdigit() or int(row[2]) < 1:
                errors.append(f"line {line_number}: priority must be a positive integer")
            entry_type = row[5]
            entry_id = row[6]
            if not valid_entry_id(entry_id):
                errors.append(f"line {line_number}: invalid entry_id {entry_id!r}")
            elif entry_id in entry_ids:
                errors.append(f"line {line_number}: duplicate entry_id {entry_id!r}")
            else:
                entry_ids.add(entry_id)
                headword = canonical_entry_headword(row[1])
                active_ids[entry_id] = headword
                if not entry_id_matches_headword(entry_id, headword):
                    errors.append(
                        f"line {line_number}: entry_id does not match canonical headword {headword!r}"
                    )
            if entry_type not in ENTRY_TYPES:
                errors.append(f"line {line_number}: invalid entry_type {entry_type!r}")
            elif row[0][0:1].isdigit() and row[3] and entry_type != "number_pronunciation":
                errors.append(f"line {line_number}: numeric pronunciation must use number_pronunciation")
            elif row[0].endswith("*") and row[3] and entry_type != "correction_alias":
                errors.append(f"line {line_number}: corrected * reading must use correction_alias")
            elif entry_type == "number_pronunciation" and not (row[0][0:1].isdigit() and row[3]):
                errors.append(f"line {line_number}: number_pronunciation needs a numeric reading and corrected value")
            elif entry_type == "correction_alias" and not (row[0].endswith("*") and row[3]):
                errors.append(f"line {line_number}: correction_alias needs a * reading and corrected value")
    except (csv.Error, StopIteration) as exc:
        errors.append(f"invalid TSV structure: {exc}")
        return errors

    errors.extend(validate_registry(registry_path or path.with_name("dictionary_entry_id_registry.tsv"), active_ids))
    if not errors:
        print(f"Valid: {entry_count} entries, seven fields, unique stable IDs, UTF-8/NFC, CRLF line endings")
        inversions = out_of_order_pairs(data_rows, EXPECTED_HEADER)
        if inversions:
            print(f"Maintenance notice: TSV is not in canonical Tangliengim order "
                  f"({inversions} adjacent inversions). Run tools/sort_dictionary_tsv.py when ready.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_PATH)
    parser.add_argument("--registry", type=Path)
    args = parser.parse_args()
    errors = validate(args.path, args.registry)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Invalid: {len(errors)} issue(s)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
