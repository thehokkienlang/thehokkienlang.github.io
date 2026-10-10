"""Canonical static ordering and sparse contextual absolute-rank overrides."""

from __future__ import annotations

import csv
import unicodedata
from pathlib import Path

try:
    from .dictionary_schema import DICTIONARY_COLUMNS, canonical_entry_headword, is_comment_record, require_dictionary_header
    from .tangliengim_collation import TYPE_RANK, reading_sort_key
except ImportError:
    from dictionary_schema import DICTIONARY_COLUMNS, canonical_entry_headword, is_comment_record, require_dictionary_header
    from tangliengim_collation import TYPE_RANK, reading_sort_key

PRIORITY_COLUMNS = ("lookup_key", "entry", "entry_id", "rank")
TONE_DIGITS = str.maketrans({'ˆ':'1', 'ꞈ':'1', 'ˋ':'2', '`':'2', 'ˎ':'2', 'ˊ':'4', 'ˏ':'4', 'ˉ':'5', 'ˍ':'5'})


def lookup_key(value: str) -> str:
    text = unicodedata.normalize('NFKD', str(value))
    return unicodedata.normalize('NFC', ''.join(c for c in text if unicodedata.category(c)[0] in 'LN')).lower()


def reading_base(value: str) -> str:
    return lookup_key(''.join(c for c in str(value).translate(TONE_DIGITS) if c not in '12345*'))


def source_record(entry: dict) -> dict:
    return entry.get('raw', entry)


def source_id(entry: dict) -> str:
    return source_record(entry).get('entry_id') or entry.get('entry_id', entry.get('id', '')).removesuffix('-sandhi')


def canonical_key(entry: dict) -> tuple:
    row = source_record(entry)
    return (TYPE_RANK.get(row.get('entry_type', entry.get('entryType', 'lexical')), 1),
            reading_sort_key(row.get('reading', entry.get('reading', ''))),
            tuple(map(ord, canonical_entry_headword(row.get('hanri', entry.get('hanri', ''))))),
            tuple(map(ord, row.get('corrected', ''))), source_id(entry))


def generated(entry: dict) -> bool:
    return bool(entry.get('autoSandhi') or entry.get('auto_sandhi'))


def rank_entries(entries: list[dict], key: str, overrides: dict | None = None, *, presorted: bool = False) -> list[dict]:
    """Rank source identities first; generated variants follow their source."""
    ordered = list(entries) if presorted else sorted(entries, key=lambda e: (canonical_key(e), generated(e)))
    normalized = lookup_key(key)
    if overrides is None and not presorted and any(normalized in e.get('staticOrder',{}) for e in ordered):
        return sorted(ordered,key=lambda e:(e.get('staticOrder',{}).get(normalized,10**9),canonical_key(e),generated(e)))
    representatives = {}
    for entry in ordered:
        representatives.setdefault(source_id(entry), entry)
    ids = list(representatives)
    specified = (overrides or {}).get(lookup_key(key), {})
    if overrides is None:
        specified = {source_id(e): e.get('staticRanks', {}).get(lookup_key(key)) for e in ordered}
    # Eligibility/tone filtering may hide a source. Apply absolute positions to
    # the full group before filtering in callers; absent identities never enter it.
    specified = {i:r for i,r in specified.items() if i in representatives and r is not None}
    slots = [None] * len(ids)
    for identity, rank in sorted(specified.items(), key=lambda x:x[1]):
        if not isinstance(rank,int) or rank < 1 or rank > len(ids):
            raise InvalidStaticPriority(f'{normalized}: absolute rank {rank!r} is outside the complete candidate group')
        position = rank - 1
        if slots[position] is not None:
            raise InvalidStaticPriority(f'{normalized}: conflicting absolute rank {rank}')
        slots[position] = identity
    remaining = iter(i for i in ids if i not in specified)
    final = [next(remaining) if i is None else i for i in slots]
    positions = {identity:index for index,identity in enumerate(final)}
    return sorted(ordered, key=lambda e:(positions[source_id(e)], generated(e)))


def reading_groups(records: list[dict]) -> dict[str, list[dict]]:
    groups = {}
    for row in records:
        if row['entry_type'] == 'number_pronunciation':
            continue
        for value in (row['reading'], row.get('corrected') or row['reading']):
            key = reading_base(value)
            if key:
                group = groups.setdefault(key, [])
                if row not in group:
                    group.append(row)
    return groups


def headword_entries(records: list[dict], key: str) -> list[dict]:
    key = lookup_key(key)
    matching = [r for r in records if r.get('entry_type') != 'number_pronunciation'
            and key.startswith(lookup_key(canonical_entry_headword(r['hanri'])))
            and lookup_key(canonical_entry_headword(r['hanri']))]
    def hanri(c):
        return 0x3400<=ord(c)<=0x9fff or 0x20000<=ord(c)<=0x2ebef
    mixed = [r for r in matching if any(hanri(c) for c in canonical_entry_headword(r['hanri'])) and
             not all(hanri(c) for c in canonical_entry_headword(r['hanri']))]
    if mixed:
        return mixed
    if not all(hanri(c) for c in key):
        return matching
    words = {lookup_key(canonical_entry_headword(r['hanri'])) for r in records
             if r.get('entry_type') != 'number_pronunciation' and all(hanri(c) for c in r['hanri'])}
    coverage = {len(key):0}
    for pos in range(len(key)-1,-1,-1):
        coverage[pos] = min([1+coverage[pos+1]]+[coverage[pos+len(w)] for w in words if key.startswith(w,pos)])
    return [r for r in matching if coverage[len(lookup_key(canonical_entry_headword(r['hanri'])))]==coverage[0]]


class InvalidStaticPriority(ValueError):
    """A human override is invalid; never fall back to a demo dictionary."""


def _load_priority(path: Path, records: list[dict]) -> dict[str, dict[str, int]]:
    if not path.is_file():
        return {}
    raw = path.read_bytes()
    if raw.startswith(b'\xef\xbb\xbf') or raw.count(b'\n') != raw.count(b'\r\n') or not raw.endswith(b'\r\n'):
        raise ValueError(f'{path}: use UTF-8 without BOM and CRLF line endings')
    active = {r['entry_id']:r for r in records}
    reading = reading_groups(records)
    result = {}
    ranks = {}
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t', restkey='_extra', restval=None)
        if tuple(reader.fieldnames or ()) != PRIORITY_COLUMNS:
            raise ValueError(f'{path}: header must be {PRIORITY_COLUMNS}')
        for line, row in enumerate(reader, 2):
            error = f'{path.name}:{line}'
            if any(row.get(k) is None for k in PRIORITY_COLUMNS) or '_extra' in row:
                raise ValueError(f'{error}: expected four fields')
            if any(v != v.strip() or unicodedata.normalize('NFC',v)!=v for v in row.values()):
                raise ValueError(f'{error}: surrounding whitespace or non-NFC value')
            key, identity = row['lookup_key'], row['entry_id']
            if not key or key != lookup_key(key) or any(c.isspace() for c in key) or '〃' in key:
                raise ValueError(f'{error}: lookup_key must be a normalized nonempty lookup input')
            if identity not in active:
                raise ValueError(f'{error}: entry_id {identity!r} is not active')
            if row['entry'] != active[identity]['hanri']:
                raise ValueError(f'{error}: stale entry label; expected {active[identity]["hanri"]!r}')
            value = row['rank']
            if not value.isascii() or not value.isdigit() or int(value)<1:
                raise ValueError(f'{error}: rank must be a positive integer')
            group = reading.get(key) or headword_entries(records,key)
            eligible = {r['entry_id'] for r in group}
            if identity not in eligible:
                raise ValueError(f'{error}: entry is not eligible for lookup_key {key!r}')
            rank = int(value)
            if rank > len(eligible):
                raise ValueError(f'{error}: rank {rank} exceeds candidate-group size {len(eligible)}')
            if identity in result.setdefault(key, {}):
                raise ValueError(f'{error}: duplicate (lookup_key, entry_id)')
            if rank in ranks.setdefault(key,set()):
                raise ValueError(f'{error}: conflicting absolute rank {rank} for {key!r}')
            result[key][identity] = rank
            ranks[key].add(rank)
    return result


def load_priority(path: Path, records: list[dict]) -> dict[str, dict[str, int]]:
    try:
        return _load_priority(path,records)
    except (ValueError,UnicodeError,csv.Error,OSError) as exc:
        raise InvalidStaticPriority(str(exc)) from exc


def read_records(path: Path) -> list[dict]:
    with path.open(encoding='utf-8-sig',newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t', restkey='_extra', restval=None)
        require_dictionary_header(reader.fieldnames)
        records = []
        for row in reader:
            if '_extra' in row or any(row[name] is None for name in DICTIONARY_COLUMNS):
                raise ValueError(f'{path}:{reader.line_num}: expected {len(DICTIONARY_COLUMNS)} fields')
            if not is_comment_record(row):
                records.append(row)
        return records


def annotate_entries(entries: list[dict], path: Path, records: list[dict]) -> None:
    overrides = load_priority(path, records)
    by_id = {}
    for key, ranks in overrides.items():
        for identity, rank in ranks.items():
            by_id.setdefault(identity,{})[key] = rank
    for entry in entries:
        entry['canonicalKey'] = canonical_key(entry)
        entry['staticRanks'] = by_id.get(source_id(entry),{})
        entry['staticOrder'] = {}
    positions = {}
    for key, group in reading_groups(records).items():
        positions[key] = {source_id(e):i for i,e in enumerate(rank_entries(group,key,overrides))}
    for entry in entries:
        identity = source_id(entry)
        for value in (source_record(entry)['reading'],source_record(entry).get('corrected') or entry['reading']):
            key = reading_base(value)
            if identity in positions.get(key,{}):
                entry['staticOrder'][key] = positions[key][identity]


def segment_match(text: str, index: int, entries: list[dict], run_end: int | None = None) -> dict | None:
    """Prefer coverage, then fewer segments; contextual overrides select first."""
    end = len(text) if run_end is None else run_end
    memo = {}
    def best_at(position):
        if position >= end:
            return (0,0), None
        if position in memo:
            return memo[position]
        choices = []
        for entry in entries:
            word = entry['hanri']
            if word and text.startswith(word,position) and position+len(word)<=end:
                rest, _ = best_at(position+len(word))
                choices.append(((rest[0],rest[1]+1),entry))
        rest, _ = best_at(position+1)
        fallback = ((rest[0]+1,rest[1]+1),None)
        if not choices:
            memo[position] = fallback
            return fallback
        choices.sort(key=lambda item:(item[0],-len(item[1]['hanri']),canonical_key(item[1])))
        choices = [item for item in choices if item[0][0]==choices[0][0][0]]
        eligible = [e for _,e in choices]
        specified = any(lookup_key(text[position:end]) in e.get('staticRanks',{}) for e in eligible)
        if specified:
            ordered = rank_entries(eligible,text[position:end],presorted=True)
            first = ordered[0]
            selected = next(item for item in choices if item[1] is first)
        else:
            selected = choices[0]
        memo[position] = selected if selected[0][0]<=fallback[0][0] else fallback
        return memo[position]
    return best_at(index)[1]
