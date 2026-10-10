"""Local-only candidate learning, independent of static dictionary resolution."""
from __future__ import annotations

import csv
import errno
import json
import math
import os
import tempfile
import threading
import time
import unicodedata
from contextlib import contextmanager
from pathlib import Path

try:
    from .dictionary_ranking import TONE_DIGITS, source_id
except ImportError:
    from dictionary_ranking import TONE_DIGITS, source_id

MAX_SELECTION_COUNT = 255
SCHEMA_VERSION = 1
_LOCK = threading.RLock()
LOCK_WAIT_SECONDS = 0.25


def lookup_key(value: str) -> str:
    return unicodedata.normalize('NFC', str(value).replace("'", '’').translate(TONE_DIGITS))


def adaptive_score(static_index: int, selection_count: int) -> int:
    return static_index * 2 - selection_count


def preference_path() -> Path:
    override = os.environ.get('TANGLIENGIM_CANDIDATE_PREFERENCES_PATH')
    if override:
        return Path(override)
    if os.name == 'nt':
        root = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData' / 'Local')))
    else:
        root = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local' / 'share')))
    return root / 'Tangliengim' / 'candidate-preferences-v1.json'


def active_ids_from_tsv(path: Path) -> set[str]:
    try:
        with path.open(encoding='utf-8', newline='') as stream:
            return {row['entry_id'] for row in csv.DictReader(stream, delimiter='\t')
                    if row.get('entry_id') and not any(row.get(k, '').startswith('#') for k in ('hanri', 'reading'))}
    except (OSError, KeyError, UnicodeError):
        return set()


def sanitize(payload, active_ids: set[str]) -> dict:
    result = {'version': SCHEMA_VERSION, 'selections': {}}
    if (not isinstance(payload, dict) or isinstance(payload.get('version'), bool)
            or not isinstance(payload.get('version'), (int, float)) or payload['version'] != SCHEMA_VERSION):
        return result
    if not isinstance(payload.get('selections'), dict):
        return result
    for key, values in payload['selections'].items():
        if not isinstance(key, str) or not key or key != lookup_key(key) or not isinstance(values, dict):
            continue
        valid = {}
        for identity, count in values.items():
            if identity not in active_ids or isinstance(count, bool) or not isinstance(count, (int, float)):
                continue
            # JSON has one numeric type; match Web Number.isInteger, including 1.0.
            try:
                integer = math.isfinite(count) and count > 0 and count == int(count)
            except (OverflowError, ValueError):
                integer = False
            if integer:
                valid[identity] = int(min(count, MAX_SELECTION_COUNT))
        if valid:
            result['selections'][key] = valid
    return result


def rank_candidates(candidates: list[dict], key: str, payload: dict, active_ids: set[str]) -> list[dict]:
    """Adapt contiguous comparable runs; fixed choices/class boundaries stay put."""
    counts = sanitize(payload, active_ids)['selections'].get(lookup_key(key), {})
    result = list(candidates)

    def kind(candidate):
        entry = candidate['entry']
        if entry.get('generatedCandidate') or source_id(entry) not in active_ids:
            return None
        return 'generated' if entry.get('autoSandhi') or entry.get('auto_sandhi') else 'source'

    start = 0
    while start < len(result):
        category = kind(result[start])
        if category is None:
            start += 1
            continue
        end = start + 1
        while end < len(result) and kind(result[end]) == category:
            end += 1
        ordered = sorted(enumerate(result[start:end], start),
                         key=lambda item: (adaptive_score(item[0], counts.get(source_id(item[1]['entry']), 0)), item[0]))
        result[start:end] = [candidate for _, candidate in ordered]
        start = end
    return result


class FilePreferenceStore:
    """Web shell and classic UI share a stable per-user file, never repo data."""

    def __init__(self, active_ids: set[str], path: Path | None = None):
        self.active_ids = set(active_ids)
        self.path = path or preference_path()
        self._base = sanitize(None, self.active_ids)
        self._pending: dict[str, dict[str, int]] = {}
        self._reset_pending = False
        self._unread = object()
        self._observed_raw = self._unread

    def _refresh(self) -> bool:
        try:
            raw = self.path.read_bytes()
        except FileNotFoundError:
            raw = None
        except OSError:
            return False  # Retain memory, but never overwrite an unreadable file.
        try:
            payload = json.loads(raw.decode('utf-8')) if raw else None
        except (ValueError, UnicodeError, RecursionError):
            payload = None
        empty = (isinstance(payload, dict) and not isinstance(payload.get('version'), bool) and payload.get('version') == 1
                 and isinstance(payload.get('selections'), dict) and not payload['selections'])
        if (self._observed_raw is not self._unread and raw != self._observed_raw and
                (raw is None or empty) and not self._reset_pending):
            self._pending = {}
        self._observed_raw = raw
        self._base = sanitize(payload, self.active_ids)
        return True

    def _snapshot(self) -> dict:
        result = sanitize(None if self._reset_pending else self._base, self.active_ids)
        for key, values in self._pending.items():
            group = result['selections'].setdefault(key, {})
            for identity, count in values.items():
                if identity in self.active_ids:
                    group[identity] = min(MAX_SELECTION_COUNT, group.get(identity, 0) + count)
        return sanitize(result, self.active_ids)

    def load(self) -> dict:
        with _LOCK:
            self._refresh()
            return self._snapshot()

    @contextmanager
    def _file_lock(self):
        stream = None
        locked = False
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            stream = self.path.with_name(self.path.name + '.lock').open('a+b')
            if os.name == 'nt':
                import msvcrt
                stream.seek(0, os.SEEK_END)
                if not stream.tell():
                    stream.write(b'\0'); stream.flush()
            else:
                import fcntl
            deadline = time.monotonic() + LOCK_WAIT_SECONDS
            while True:
                try:
                    if os.name == 'nt':
                        stream.seek(0)
                        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    locked = True
                    break
                except OSError as error:
                    if error.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK) or time.monotonic() >= deadline:
                        break
                    time.sleep(0.005)
        except OSError:
            pass
        try:
            yield locked
        finally:
            if stream is not None:
                if locked:
                    try:
                        if os.name == 'nt':
                            stream.seek(0)
                            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                        else:
                            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
                    except OSError:
                        pass
                try:
                    stream.close()
                except OSError:
                    pass

    def _save(self, payload: dict) -> bool:
        temporary = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.path.parent,
                                             prefix=self.path.name + '.', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
            self._observed_raw = raw.encode('utf-8')
            return True
        except (OSError, ValueError, TypeError, RecursionError):
            return False
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass

    def record(self, key: str, identity: str) -> int:
        if not isinstance(key, str) or not isinstance(identity, str):
            return 0
        key = lookup_key(key)
        if not key or identity not in self.active_ids:
            return 0
        with _LOCK:
            with self._file_lock() as locked:
                readable = self._refresh()
                count = self._snapshot()['selections'].get(key, {}).get(identity, 0)
                if count >= MAX_SELECTION_COUNT:
                    if locked and readable and self._pending and self._save(self._snapshot()):
                        self._base = self._snapshot()
                        self._pending = {}
                        self._reset_pending = False
                    return MAX_SELECTION_COUNT
                group = self._pending.setdefault(key, {})
                group[identity] = min(MAX_SELECTION_COUNT, group.get(identity, 0) + 1)
                payload = self._snapshot()
                if locked and readable and self._save(payload):
                    self._base = payload
                    self._pending = {}
                    self._reset_pending = False
                return payload['selections'][key][identity]

    def reset(self) -> None:
        with _LOCK:
            with self._file_lock() as locked:
                self._pending = {}
                self._base = sanitize(None, self.active_ids)
                self._reset_pending = True
                if locked and self._save(self._base):
                    self._reset_pending = False

    def rank(self, candidates: list[dict], key: str) -> list[dict]:
        return rank_candidates(candidates, key, self.load(), self.active_ids)
