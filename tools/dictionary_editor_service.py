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
    DICTIONARY_COLUMNS, ENTRY_ID_REGISTRY_COLUMNS, canonical_entry_headword,
    is_comment_record, resolve_dictionary_record, inherited_storage,
)
from simplified_lookup import contains_hanri, simplified_headword
from sort_dictionary_tsv import sort_tsv
from validate_dictionary_tsv import validate

MAIN = "hokkien_hanri_dict.tsv"
REGISTRY = "dictionary_entry_id_registry.tsv"
CATEGORIES = "dictionary_categories.tsv"
DATA_FILES = (MAIN, REGISTRY, "dictionary_priority.tsv", CATEGORIES, "dictionary_redirects.tsv")
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
            return {"ok": True, "revision": fingerprint(files), "entries": entries,
                    "categories": labels, "source": str(self.data / MAIN)}

    @staticmethod
    def normalize(record: dict) -> dict:
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
        if not result["entry_type"]:
            result["entry_type"] = "lexical" if contains_hanri(result["hanri"]) else "hangul_override"
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
        saved, skipped, pending_categories = [], [], []
        for change in changes:
            if not isinstance(change, dict):
                raise EditorError("Each entry must be an object.")
            previous = records.get(change.get("entry_id"))
            if previous is not None:
                change = {**previous, **change}
            record = self.normalize(change)
            identity = record["entry_id"]
            old = records.get(identity) if identity else None
            if identity and old is None:
                raise EditorError("This entry no longer exists. Reload the editor.", code="stale")
            if old and canonical_entry_headword(old["hanri"]) != canonical_entry_headword(record["hanri"]):
                raise EditorError("Changing the identity headword needs a new entry. Use New entry instead.")
            signature = lambda row: tuple(row.get(key, "") for key in DICTIONARY_COLUMNS if key != "entry_id")
            duplicate = next((row for row in records.values() if row is not old and signature(row) == signature(record)), None)
            if duplicate:
                skipped.append(duplicate)
                continue
            alternatives = [row for row in records.values() if row["hanri"] == record["hanri"] and row is not old]
            if not identity and alternatives and not allow_alternative:
                raise EditorError("This headword already has entries. Confirm adding another reading or sense.",
                                  code="alternative", details=alternatives)
            if old:
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
            changed_ids = {row["entry_id"] for row, _ in pending_categories}
            category_rows = [row for row in category_rows if row["entry_id"] not in changed_ids]
            for record, categories in pending_categories:
                category_rows.extend(dict(category=c, label=labels[c], entry=record["hanri"], entry_id=record["entry_id"]) for c in categories)
            # Existing labels must follow edits that only change inline annotations.
            by_id = {row["entry_id"]: row for row in rows if not is_comment_record(row)}
            for row in category_rows:
                if row["entry_id"] in by_id:
                    row["entry"] = by_id[row["entry_id"]]["hanri"]
            if CATEGORIES in before or category_rows:
                (data / CATEGORIES).write_bytes(table_bytes(category_header, category_rows))
            priority_path = data / "dictionary_priority.tsv"
            if priority_path.exists():
                p_header, priorities = read_table(priority_path.read_bytes())
                for row in priorities:
                    if row["entry_id"] in by_id:
                        row["entry"] = by_id[row["entry_id"]]["hanri"]
                priority_path.write_bytes(table_bytes(p_header, priorities))
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
            return {"ok": True, "saved": saved, "skipped": skipped, "revision": fingerprint(after),
                    "message": f"Saved {len(saved)} entries locally; skipped {len(skipped)} identical entries."}

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
            output.append(self.normalize({**existing.get(record.get("entry_id"), {}), **record}))
        return output
