"""Exact dictionary-record references, separate from linguistic lookup keys."""
from __future__ import annotations

import csv
import unicodedata
from collections import defaultdict
from pathlib import Path

try:
    from .dictionary_schema import valid_entry_id
except ImportError:
    from dictionary_schema import valid_entry_id

CATEGORY_COLUMNS = ('category', 'label', 'entry', 'entry_id')


def record_index(records: list[dict]) -> dict[str, dict]:
    result = {}
    for record in records:
        identity = record.get('entry_id', '')
        if not valid_entry_id(identity):
            raise ValueError(f'Invalid structural entry_id: {identity!r}')
        if identity in result:
            raise ValueError(f'Duplicate structural entry_id: {identity!r}')
        result[identity] = record
    return result


def require_record(records: dict[str, dict], identity: str) -> dict:
    if not isinstance(identity, str) or not valid_entry_id(identity):
        raise ValueError(f'Invalid structural entry_id: {identity!r}')
    record = records.get(identity)
    if (record is None or record.get('entry_type') == 'number_pronunciation'
            or not record.get('hanri') or not (record.get('corrected') or record.get('reading'))):
        raise ValueError(f'Unknown or inactive structural entry_id: {identity!r}')
    return record


def load_categories(path: Path, records: list[dict]) -> tuple[dict[str, str], dict[str, list[str]]]:
    """IDs are authoritative; companion headwords are checked, never searched."""
    index = record_index(records)
    labels = {}
    memberships = defaultdict(list)
    seen = set()
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t', restkey='_extra', restval=None, strict=True)
        if tuple(reader.fieldnames or ()) != CATEGORY_COLUMNS:
            raise ValueError(f'{path.name}: header must be {CATEGORY_COLUMNS}')
        for line, row in enumerate(reader, 2):
            error = f'{path.name}:{line}'
            if '_extra' in row or any(row.get(name) is None for name in CATEGORY_COLUMNS):
                raise ValueError(f'{error}: expected four fields')
            if any(not value or value != value.strip() or unicodedata.normalize('NFC', value) != value
                   for value in row.values()):
                raise ValueError(f'{error}: fields must be nonempty, NFC and without surrounding whitespace')
            category, label, entry, identity = (row[name] for name in CATEGORY_COLUMNS)
            target = require_record(index, identity)
            if entry != target['hanri']:
                raise ValueError(f'{error}: stale entry label for {identity}; expected {target["hanri"]!r}')
            if category in labels and labels[category] != label:
                raise ValueError(f'{error}: conflicting category label for {category!r}')
            relationship = (category, identity)
            if relationship in seen:
                raise ValueError(f'{error}: duplicate category membership: {category} / {identity}')
            seen.add(relationship)
            labels[category] = label
            memberships[identity].append(category)
    return labels, dict(memberships)
