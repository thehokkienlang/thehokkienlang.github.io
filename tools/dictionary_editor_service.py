"""Validated, recoverable dictionary editing shared by the editor and Local IME."""
from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import os
import tempfile
import threading
import time
import unicodedata
from contextlib import contextmanager, redirect_stdout
from pathlib import Path

from assign_dictionary_entry_ids import _atomic_write, _serialize, assign_ids
from dictionary_schema import (
    DICTIONARY_COLUMNS, DEFUNCT_COLUMNS, ENTRY_ID_REGISTRY_COLUMNS, canonical_entry_headword,
    is_comment_record, resolve_dictionary_record, inherited_storage,
)
from simplified_lookup import contains_hanri, simplified_headword
from sort_dictionary_tsv import sort_tsv
from validate_dictionary_tsv import validate
from dictionary_ranking import lookup_key, reading_groups, headword_entries, load_priority, rank_entries

MAIN = "hokkien_hanri_dict.tsv"
REGISTRY = "dictionary_entry_id_registry.tsv"
CATEGORIES = "dictionary_categories.tsv"
DEFUNCT = "dictionary_defunct.tsv"
DATA_FILES = (MAIN, REGISTRY, "dictionary_priority.tsv", CATEGORIES, "dictionary_redirects.tsv", DEFUNCT)
TONE_DIGITS = str.maketrans(dict(zip("ˆˋ`ˊˉꞈˎˏˍ", "122451245")))
_THREAD_LOCK = threading.RLock()


class EditorError(ValueError):
    def __init__(self, message, *, code="validation", details=None):
        super().__init__(message)
        self.code, self.details = code, details


def read_table(raw: bytes) -> tuple[list[str], list[dict]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""), delimiter="\t", strict=True)
    records = list(reader)
    if not reader.fieldnames or any(None in row or None in row.values() for row in records):
        raise EditorError("Malformed TSV fields. Repair the source before editing.")
    return reader.fieldnames, records


def table_bytes(header, records) -> bytes:
    return _serialize([list(header)] + [[row.get(key, "") for key in header] for row in records])


def fingerprint(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name in DATA_FILES:
        digest.update(name.encode())
        digest.update(hashlib.sha256(files.get(name, b"")).digest())
    return digest.hexdigest()


class DictionaryEditorService:
    def __init__(self, repo: Path):
        self.repo = Path(repo).resolve()
        self.data = self.repo / "data"
        self.state = self.repo / ".dictionary-editor"
        self.filename = MAIN

    def path(self, name):
        return self.data / (self.filename if name == MAIN else name)

    @classmethod
    def for_tsv(cls, path: Path):
        path = Path(path).resolve()
        if path.name != MAIN or path.parent.name != "data":
            # Test fixtures and supported isolated dictionaries use the same sibling contract.
            service = cls(path.parent.parent)
            service.data = path.parent
            service.state = path.parent / ".dictionary-editor"
            service.filename = path.name
            return service
        return cls(path.parent.parent)

    @contextmanager
    def locked(self):
        with _THREAD_LOCK:
            self.state.mkdir(parents=True, exist_ok=True)
            with (self.state / "writer.lock").open("a+b") as stream:
                stream.seek(0, os.SEEK_END)
                if not stream.tell():
                    stream.write(b"0")
                    stream.flush()
                deadline = time.monotonic() + 10
                while True:
                    try:
                        if os.name == "nt":
                            import msvcrt
                            stream.seek(0)
                            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                        else:
                            import fcntl
                            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except OSError:
                        if time.monotonic() >= deadline:
                            raise EditorError("Dictionary is busy. Your form has been kept; try saving again.", code="busy")
                        time.sleep(.05)
                try:
                    self._recover()
                    yield
                finally:
                    if os.name == "nt":
                        stream.seek(0)
                        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def files(self) -> dict[str, bytes]:
        return {name: self.path(name).read_bytes() for name in DATA_FILES if self.path(name).is_file()}

    def _recover(self):
        journal = self.state / "transaction.json"
        if not journal.exists():
            return
        pending = json.loads(journal.read_text(encoding="utf-8"))
        for name, item in pending.items():
            if name not in DATA_FILES:
                raise EditorError("Invalid recovery journal; no source files were changed.")
            current = self.path(name).read_bytes() if self.path(name).exists() else None
            before = base64.b64decode(item["before"]) if item["before"] is not None else None
            after = base64.b64decode(item["after"])
            if current not in (before, after):
                raise EditorError("An external edit conflicts with interrupted-save recovery. The backup is in " + str(self.state))
        for name, item in pending.items():
            _atomic_write(self.path(name), base64.b64decode(item["after"]))
        journal.unlink()

    def commit_files(self, before: dict[str, bytes], after: dict[str, bytes]):
        if fingerprint(self.files()) != fingerprint(before):
            raise EditorError("Dictionary changed in another window. Reload before saving.", code="stale")
        changes = {name: raw for name, raw in after.items() if before.get(name) != raw}
        if not changes:
            return
        journal = {name: {"before": base64.b64encode(before[name]).decode() if name in before else None,
                          "after": base64.b64encode(raw).decode()} for name, raw in changes.items()}
        encoded = json.dumps(journal).encode()
        _atomic_write(self.state / "last-save-backup.json", encoded)
        _atomic_write(self.state / "transaction.json", encoded)
        # A journal makes a multi-file save recoverable after process/power failure.
        self._recover()

    def snapshot(self) -> dict:
        with self.locked():
            files = self.files()
            if MAIN not in files or REGISTRY not in files:
                raise EditorError("The canonical TSV and ID registry must both exist.")
            header, records = read_table(files[MAIN])
            if tuple(header) != DICTIONARY_COLUMNS:
                raise EditorError("The dictionary does not have the current nine-column schema.")
            entries = [row for row in records if not is_comment_record(row)]
            labels, memberships = {}, {}
            if CATEGORIES in files:
                for row in read_table(files[CATEGORIES])[1]:
                    labels[row["category"]] = row["label"]
                    memberships.setdefault(row["entry_id"], []).append(row["category"])
            for row in entries:
                row["categories"] = memberships.get(row["entry_id"], [])
            defunct = read_table(files[DEFUNCT])[1] if DEFUNCT in files else []
            for row in defunct:
                row.update(defunct=True, categories=[])
            return {"ok": True, "revision": fingerprint(files), "entries": entries,
                    "defunctEntries": defunct,
                    "categories": labels, "source": str(self.data / MAIN)}

    def existing_entry(self, identity):
        if not identity or not self.path(MAIN).exists():
            return None
        return next((row for row in read_table(self.path(MAIN).read_bytes())[1]
                     if not is_comment_record(row) and row['entry_id'] == identity), None)

    @staticmethod
    def detected_type(record: dict, previous: dict | None = None) -> str:
        def inputs(row):
            return (canonical_entry_headword(row.get('hanri', '')),
                    unicodedata.normalize('NFC', row.get('reading', '').strip()).translate(TONE_DIGITS),
                    unicodedata.normalize('NFC', row.get('corrected', '').strip()).translate(TONE_DIGITS))
        if previous is not None and inputs(previous) == inputs(record):
            return previous['entry_type']
        hanri, reading, corrected = inputs(record)
        if reading[:1].isdigit() and corrected:
            return 'number_pronunciation'
        if reading.endswith('*') and corrected:
            return 'correction_alias'
        if contains_hanri(hanri):
            return 'lexical'
        if any('\u1100' <= char <= '\u11ff' or '\u3130' <= char <= '\u318f'
               or '\ua960' <= char <= '\ua97f' or '\uac00' <= char <= '\ud7ff' for char in hanri):
            return 'hangul_override'
        return ''

    def simplified_fields(self, record: dict) -> dict:
        if not isinstance(record, dict):
            raise EditorError("Each entry must be an object.")
        values = {}
        for name in ("hanri", "mandarin_trad", "reading", "corrected", "entry_id"):
            value = record.get(name, "")
            if not isinstance(value, str) or any(c in value for c in "\t\r\n\0"):
                raise EditorError(f"{name}: use plain text without tabs or line breaks.")
            values[name] = unicodedata.normalize("NFC", value.strip())
        traditional = values["hanri"] if values["mandarin_trad"] == "〃" else values["mandarin_trad"]
        return {"simplified": simplified_headword(values["hanri"]),
                "mandarin_simp": simplified_headword(traditional) or traditional,
                "entry_type": self.detected_type(values, self.existing_entry(values['entry_id']))}

    @staticmethod
    def normalize(record: dict, *, previous: dict | None = None) -> dict:
        if not isinstance(record, dict):
            raise EditorError("Each entry must be an object.")
        result = {}
        for name in DICTIONARY_COLUMNS:
            value = record.get(name, "")
            if not isinstance(value, str) or any(c in value for c in "\t\r\n\0"):
                raise EditorError(f"{name}: use plain text without tabs or line breaks.")
            result[name] = unicodedata.normalize("NFC", value.strip())
        if not result["hanri"] or not result["reading"]:
            raise EditorError("Hanri / headword and Hangul reading are required.")
        if result["hanri"].startswith("#") or result["reading"].startswith("#"):
            raise EditorError("An entry cannot be a section comment.")
        result["reading"] = result["reading"].translate(TONE_DIGITS)
        result["corrected"] = result["corrected"].translate(TONE_DIGITS)
        result['entry_type'] = DictionaryEditorService.detected_type(result, previous)
        if not result['entry_type']:
            raise EditorError('Use a Hanri or Hangul headword, or a numeric input with a corrected reading.')
        # Simplified Hokkien is script conversion; English/Mandarin are never guessed.
        if not result["simplified"]:
            result["simplified"] = inherited_storage(simplified_headword(result["hanri"]), result["hanri"])
        if result["mandarin_trad"] and not result["mandarin_simp"]:
            traditional = result["hanri"] if result["mandarin_trad"] == "〃" else result["mandarin_trad"]
            result["mandarin_simp"] = inherited_storage(simplified_headword(traditional) or traditional, traditional)
        resolve_dictionary_record(result)
        return result

    def prepare(self, before: dict[str, bytes], changes: list[dict], *, allow_alternative=False) -> tuple[dict, list, list]:
        if not isinstance(changes, list) or not changes or len(changes) > 500:
            raise EditorError("Save between 1 and 500 entries at a time.")
        header, rows = read_table(before[MAIN])
        if tuple(header) != DICTIONARY_COLUMNS or REGISTRY not in before:
            raise EditorError("The canonical dictionary schema and registry are required.")
        records = {row["entry_id"]: row for row in rows if not is_comment_record(row)}
        labels, _ = {}, None
        category_header = ["category", "label", "entry", "entry_id"]
        category_rows = read_table(before[CATEGORIES])[1] if CATEGORIES in before else []
        for row in category_rows:
            labels[row["category"]] = row["label"]
        saved, skipped, pending_categories, retired = [], [], [], []
        for change in changes:
            if not isinstance(change, dict):
                raise EditorError("Each entry must be an object.")
            previous = records.get(change.get("entry_id"))
            if previous is not None:
                change = {**previous, **change}
                if (canonical_entry_headword(previous["hanri"]) != canonical_entry_headword(change["hanri"])
                        and change.get("simplified") == previous["simplified"]):
                    change["simplified"] = ""
            record = self.normalize(change, previous=previous)
            identity = record["entry_id"]
            old = records.get(identity) if identity else None
            if identity and old is None:
                raise EditorError("This entry no longer exists. Reload the editor.", code="stale")
            replacing = old is not None and canonical_entry_headword(old["hanri"]) != canonical_entry_headword(record["hanri"])
            signature = lambda row: tuple(row.get(key, "") for key in DICTIONARY_COLUMNS if key != "entry_id")
            duplicate = next((row for row in records.values() if row is not old and signature(row) == signature(record)), None)
            if duplicate and not replacing:
                skipped.append(duplicate)
                continue
            alternatives = [row for row in records.values() if row["hanri"] == record["hanri"] and row is not old]
            if (not identity or replacing) and not duplicate and alternatives and not allow_alternative:
                raise EditorError("This headword already has entries. Confirm adding another reading or sense.",
                                  code="alternative", details=alternatives)
            if replacing:
                retired.append((old.copy(), duplicate or record))
                position = rows.index(old)
                del records[identity]
                if duplicate:
                    rows.pop(position)
                    record = duplicate
                else:
                    record["entry_id"] = ""
                    rows[position] = record
                    records[f"replacement-{identity}"] = record
            elif old:
                old.update(record)
            else:
                rows.append(record)
                records[f"new-{len(saved)}"] = record
            if "categories" in change:
                categories = change["categories"]
                if not isinstance(categories, list) or any(not isinstance(c, str) or c not in labels for c in categories):
                    raise EditorError("Choose categories from the existing category list.")
                pending_categories.append((record, sorted(set(categories))))
            saved.append(record)
        # Reading-correction rows belong to the renamed lexical target as well.
        redirects = read_table(before["dictionary_redirects.tsv"])[1] if "dictionary_redirects.tsv" in before else []
        for previous, replacement in list(retired):
            for link in redirects:
                if link["kind"] != "reading" or link["target_entry_id"] != previous["entry_id"]:
                    continue
                for alias in list(rows):
                    if (alias.get("entry_type") == "correction_alias" and alias["hanri"] == previous["hanri"]
                            and alias["reading"].rstrip("*") == link["source_reading"]):
                        updated = {**alias, "hanri": replacement["hanri"], "entry_id": "",
                                   "simplified": replacement["simplified"], "corrected": replacement["reading"]}
                        retired.append((alias.copy(), updated))
                        rows[rows.index(alias)] = updated
        with tempfile.TemporaryDirectory(prefix="tangliengim-save-") as folder:
            data = Path(folder)
            for name, raw in before.items():
                (data / name).write_bytes(raw)
            path = data / MAIN
            path.write_bytes(table_bytes(header, rows))
            with redirect_stdout(io.StringIO()):
                assign_ids(path)
            allocated = read_table(path.read_bytes())[1]
            # Allocation keeps row order, including comment rows.
            for source, assigned in zip(rows, allocated):
                source["entry_id"] = assigned.get("entry_id", "")
            replacements = {old["entry_id"]: new for old, new in retired}
            if retired:
                archived = read_table(before[DEFUNCT])[1] if DEFUNCT in before else []
                archived.extend({**old, "replacement_entry_id": new["entry_id"]} for old, new in retired)
                (data / DEFUNCT).write_bytes(table_bytes(DEFUNCT_COLUMNS, archived))
                for row in category_rows:
                    if row["entry_id"] in replacements:
                        row["entry_id"] = replacements[row["entry_id"]]["entry_id"]
            changed_ids = {row["entry_id"] for row, _ in pending_categories}
            category_rows = [row for row in category_rows if row["entry_id"] not in changed_ids]
            for record, categories in pending_categories:
                category_rows.extend(dict(category=c, label=labels[c], entry=record["hanri"], entry_id=record["entry_id"]) for c in categories)
            # Existing labels must follow edits that only change inline annotations.
            by_id = {row["entry_id"]: row for row in rows if not is_comment_record(row)}
            for row in category_rows:
                if row["entry_id"] in by_id:
                    row["entry"] = by_id[row["entry_id"]]["hanri"]
            category_rows = list({(row["category"], row["entry_id"]): row for row in category_rows}.values())
            if CATEGORIES in before or category_rows:
                (data / CATEGORIES).write_bytes(table_bytes(category_header, category_rows))
            priority_path = data / "dictionary_priority.tsv"
            if priority_path.exists():
                p_header, priorities = read_table(priority_path.read_bytes())
                existing_priority_keys = {(row['lookup_key'], row['entry_id']) for row in priorities
                                          if row['entry_id'] not in replacements}
                updated_priorities = []
                for row in priorities:
                    if row["entry_id"] in replacements:
                        previous = next(old for old, _ in retired if old["entry_id"] == row["entry_id"])
                        if row["lookup_key"] == lookup_key(canonical_entry_headword(previous["hanri"])):
                            row["lookup_key"] = lookup_key(canonical_entry_headword(replacements[row["entry_id"]]["hanri"]))
                        row["entry_id"] = replacements[row["entry_id"]]["entry_id"]
                        if (row['lookup_key'], row['entry_id']) in existing_priority_keys:
                            continue
                    if row["entry_id"] in by_id:
                        row["entry"] = by_id[row["entry_id"]]["hanri"]
                    updated_priorities.append(row)
                priority_path.write_bytes(table_bytes(p_header, updated_priorities))
            redirect_path = data / "dictionary_redirects.tsv"
            if redirect_path.exists():
                r_header, links = read_table(redirect_path.read_bytes())
                for row in links:
                    if row["target_entry_id"] in replacements:
                        row["target_entry_id"] = replacements[row["target_entry_id"]]["entry_id"]
                redirect_path.write_bytes(table_bytes(r_header, links))
            with redirect_stdout(io.StringIO()):
                sort_tsv(path)
                errors = validate(path)
            if errors:
                raise EditorError("\n".join(errors))
            after = {name: (data / name).read_bytes() for name in DATA_FILES if (data / name).exists()}
        return after, saved, [row["entry_id"] for row in skipped]

    def save(self, changes, *, revision=None, allow_alternative=False):
        with self.locked():
            before = self.files()
            if revision is not None and revision != fingerprint(before):
                raise EditorError("Dictionary changed in another window. Reload before saving; your form is retained.", code="stale")
            inputs = dict(before)
            if MAIN not in inputs and REGISTRY not in inputs:
                inputs[MAIN] = table_bytes(DICTIONARY_COLUMNS, [])
                inputs[REGISTRY] = table_bytes(ENTRY_ID_REGISTRY_COLUMNS, [])
            after, saved, skipped = self.prepare(inputs, changes, allow_alternative=allow_alternative)
            self.commit_files(before, after)
            previous_defunct = {row["entry_id"] for row in read_table(before[DEFUNCT])[1]} if DEFUNCT in before else set()
            retired = [row for row in read_table(after[DEFUNCT])[1] if row["entry_id"] not in previous_defunct] if DEFUNCT in after else []
            previous_ids = {row['entry_id'] for row in read_table(inputs[MAIN])[1] if not is_comment_record(row)}
            created = [row['entry_id'] for row in saved if row['entry_id'] not in previous_ids]
            return {"ok": True, "saved": saved, "skipped": skipped, "revision": fingerprint(after),
                    "newEntryIds": list(dict.fromkeys(created)),
                    "retired": retired,
                    "message": f"Saved {len(saved)} entries locally; marked {len(retired)} previous entries defunct; skipped {len(skipped)} identical entries."}

    def make_defunct(self, identity, *, revision=None):
        with self.locked():
            before = self.files()
            if revision is not None and revision != fingerprint(before):
                raise EditorError("Dictionary changed in another window. Reload before making this entry defunct.", code="stale")
            header, rows = read_table(before[MAIN])
            records = {row['entry_id']: row for row in rows if not is_comment_record(row)}
            if not isinstance(identity, str) or identity not in records:
                raise EditorError("This entry is no longer active. Reload the editor.", code="stale")
            retired_ids = {identity}
            redirect_header, links = read_table(before['dictionary_redirects.tsv']) if 'dictionary_redirects.tsv' in before else ([], [])
            # A correction must not keep producing a lexical entry made defunct.
            for link in links:
                if link['kind'] == 'reading' and link['target_entry_id'] == identity:
                    retired_ids.update(row['entry_id'] for row in records.values()
                                       if row['entry_type'] == 'correction_alias'
                                       and row['hanri'] == records[identity]['hanri']
                                       and row['reading'].rstrip('*') == link['source_reading'])
            retired = [dict(row, replacement_entry_id='') for row in records.values() if row['entry_id'] in retired_ids]
            after = dict(before)
            after[MAIN] = table_bytes(header, [row for row in rows if row.get('entry_id') not in retired_ids])
            archived = read_table(before[DEFUNCT])[1] if DEFUNCT in before else []
            after[DEFUNCT] = table_bytes(DEFUNCT_COLUMNS, [*archived, *retired])
            if CATEGORIES in before:
                columns, categories = read_table(before[CATEGORIES])
                after[CATEGORIES] = table_bytes(columns, [row for row in categories if row['entry_id'] not in retired_ids])
            if redirect_header:
                def obsolete(link):
                    if link['target_entry_id'] in retired_ids:
                        return True
                    target = records.get(link['target_entry_id'])
                    return link['kind'] == 'reading' and target is not None and any(
                        row['entry_type'] == 'correction_alias' and row['hanri'] == target['hanri']
                        and row['corrected'] == target['reading']
                        and row['reading'].rstrip('*') == link['source_reading'] for row in retired)
                after['dictionary_redirects.tsv'] = table_bytes(redirect_header, [link for link in links if not obsolete(link)])
            with tempfile.TemporaryDirectory(prefix='tangliengim-retire-') as folder:
                data = Path(folder)
                for name, raw in before.items():
                    (data / name).write_bytes(raw)
                priority_path = data / 'dictionary_priority.tsv'
                if priority_path.exists():
                    overrides = load_priority(priority_path, list(records.values()))
                    groups = reading_groups(list(records.values()))
                    columns, priorities = read_table(before['dictionary_priority.tsv'])
                    positions = {}
                    for key in overrides:
                        group = groups.get(key) or headword_entries(list(records.values()), key)
                        if any(row['entry_id'] in retired_ids for row in group):
                            ordered = rank_entries(group, key, overrides)
                            positions[key] = {row['entry_id']: rank for rank, row in enumerate(
                                (row for row in ordered if row['entry_id'] not in retired_ids), 1)}
                    kept = []
                    for row in priorities:
                        if row['entry_id'] in retired_ids:
                            continue
                        if row['lookup_key'] in positions:
                            row['rank'] = str(positions[row['lookup_key']][row['entry_id']])
                        kept.append(row)
                    after['dictionary_priority.tsv'] = table_bytes(columns, kept)
                for name, raw in after.items():
                    (data / name).write_bytes(raw)
                with redirect_stdout(io.StringIO()):
                    errors = validate(data / MAIN)
                if errors:
                    raise EditorError('\n'.join(errors))
            self.commit_files(before, after)
            return {'ok': True, 'retired': retired, 'revision': fingerprint(after),
                    'message': f'Marked “{records[identity]["hanri"]}” defunct locally. Ready to publish.'}

    def import_rows(self, text):
        if not isinstance(text, str) or len(text) > 2_000_000:
            raise EditorError("Paste a TSV batch smaller than 2 MB.")
        rows = list(csv.reader(io.StringIO(text, newline=""), delimiter="\t", strict=True))
        rows = [row for row in rows if any(cell.strip() for cell in row)]
        if not rows:
            raise EditorError("Paste at least one entry.")
        if "hanri" in rows[0] and "reading" in rows[0]:
            header = rows.pop(0)
            if len(set(header)) != len(header) or set(header) - set(DICTIONARY_COLUMNS):
                raise EditorError("The TSV header contains unknown or repeated columns.")
        else:
            header = ["hanri", "reading", "english", "mandarin_trad"][:len(rows[0])]
        if not 2 <= len(header) <= 9 or len(rows) > 500:
            raise EditorError("Use 2-4 columns without a header, or named TSV columns; maximum 500 entries.")
        output = []
        existing = {row["entry_id"]: row for row in self.snapshot()["entries"]} if "entry_id" in header else {}
        for number, row in enumerate(rows, 1):
            if len(row) != len(header):
                raise EditorError(f"Batch row {number}: expected {len(header)} columns.")
            record = dict(zip(header, row))
            previous = existing.get(record.get('entry_id'))
            output.append(self.normalize({**(previous or {}), **record}, previous=previous))
        return output
