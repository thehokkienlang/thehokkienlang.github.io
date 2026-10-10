"""Exodus II shared scoring, atomic file failures, processes, and bridge receipts."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import nullcontext
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from candidate_preferences import FilePreferenceStore, adaptive_score, rank_candidates, sanitize
from check_adaptive_desktop import load

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / 'tests/fixtures/adaptive-safeguard-cases.json').read_text(encoding='utf-8'))
IDS = set(FIXTURE['ids'])


def ranked(entries, payload, key='x'):
    return [c['entry']['id'] for c in rank_candidates([{'entry': e} for e in entries], key, payload, IDS)]


def worker(path, count, interrupt=False):
    store = FilePreferenceStore(IDS, Path(path))
    if interrupt:
        def interrupted_replace(*args):
            Path(path + '.ready').touch()
            time.sleep(60)
        with patch('candidate_preferences.os.replace', interrupted_replace):
            store.record('x', 'A')
    else:
        for _ in range(count):
            store.record('x', 'A')


def shared_cases():
    empty = {'version': 1, 'selections': {}}
    for payload in FIXTURE['malformed']:
        assert sanitize(payload, IDS) == empty
    assert sanitize(FIXTURE['mixed'], IDS) == FIXTURE['sanitized']
    assert sanitize(FIXTURE['integral_numbers'], IDS) == FIXTURE['integral_expected']
    assert sanitize({'version': 1, 'selections': {'x': {'A': 10 ** 400}}}, IDS) == empty
    assert sanitize({'version': 1, 'selections': {'x': {'A': float('nan'), 'B': float('inf'), 'C': True}}}, IDS) == empty
    entries = [{'id': identity} for identity in FIXTURE['ids']]
    for position in range(1, len(entries)):
        previous = position
        for count in range(256):
            counts = {entries[position]['id']: count}
            payload = {'version': 1, 'selections': {'x': counts}}
            result = ranked(entries, payload)
            current = result.index(entries[position]['id'])
            assert current <= previous
            previous = current
            expected = [e['id'] for i, e in sorted(enumerate(entries),
                key=lambda item: (adaptive_score(item[0], counts.get(item[1]['id'], 0)), item[0]))]
            assert result == expected
    for case in FIXTURE['mutation']:
        assert ranked(case['entries'], {'version': 1, 'selections': {'x': {'B': 3, 'stale': 255}}}) == case['expected'], case['name']
    seed = FIXTURE['seed']
    for _ in range(FIXTURE['adversarial_cases']):
        counts = {}
        for identity in FIXTURE['ids']:
            seed = (seed * 1664525 + 1013904223) & 0xffffffff
            counts[identity] = seed % 256
        payload = {'version': 1, 'selections': {'x': counts}}
        expected = [e['id'] for i, e in sorted(enumerate(entries),
            key=lambda item: (adaptive_score(item[0], counts[item[1]['id']]), item[0]))]
        assert ranked(entries, payload) == expected
        assert ranked(entries, {'selections': {'x': dict(reversed(list(counts.items())))}, 'version': 1}) == expected


def files(folder):
    path = folder / 'nested' / 'preferences.json'
    store = FilePreferenceStore(IDS, path)
    assert not store.load()['selections'] and not path.exists()
    for raw in (b'', b'{broken', b'null', b'[]', b'42', b'{"version":999}',
                b'[' * 3000 + b'0' + b']' * 3000, json.dumps(FIXTURE['mixed']).encode()):
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(raw)
        expected = FIXTURE['sanitized'] if raw.startswith(b'{"version": 1') else {'version': 1, 'selections': {}}
        assert FilePreferenceStore(IDS, path).load() == expected
    store.reset()
    for context in FIXTURE['contexts']:
        assert store.record(context, 'A') == 1
    assert store.record('', 'A') == 0
    assert store.record('unknown', 'stale') == 0
    assert store.record('unknown', []) == 0
    assert store.load()['selections']['시']['A'] == 1
    assert not store.load()['selections'].get('unknown')
    snapshot = store.load(); snapshot['selections']['시']['A'] = -100
    assert store.load()['selections']['시']['A'] == 1
    store.reset()
    store.record('x', 'A')
    original = path.read_bytes()
    with patch('candidate_preferences.os.replace', side_effect=PermissionError('write denied')):
        assert store.record('x', 'B') == 1
        assert store.load()['selections']['x']['B'] == 1
        assert path.read_bytes() == original
    other = FilePreferenceStore(IDS, path)
    other.record('x', 'C')
    assert store.record('x', 'B') == 2
    assert other.load()['selections']['x'] == {'A': 1, 'B': 2, 'C': 1}
    with patch.object(Path, 'read_bytes', side_effect=PermissionError('read denied')):
        assert store.record('x', 'B') == 3
        assert store.load()['selections']['x']['B'] == 3
    assert other.load()['selections']['x']['B'] == 2, 'Unreadable state must not be overwritten'
    assert store.record('x', 'B') == 4
    for failure in ('fsync', 'replace'):
        original = path.read_bytes()
        with patch('candidate_preferences.os.' + failure, side_effect=OSError('failure')):
            store.record('x', 'D')
            assert path.read_bytes() == original
    with patch('candidate_preferences.json.dumps', side_effect=ValueError('serialize')):
        store.record('x', 'D')
    assert store.record('x', 'D') == 4
    with patch.object(store, '_file_lock', return_value=nullcontext(False)):
        original = path.read_bytes()
        assert store.record('x', 'D') == 5
        assert path.read_bytes() == original, 'Lock failure must never authorize an unlocked write'
    assert store.record('x', 'D') == 6
    with patch('candidate_preferences.os.replace', side_effect=OSError('failure')):
        for _ in range(300): store.record('x', 'E')
    assert store.record('x', 'E') == 255
    assert other.load()['selections']['x']['E'] == 255
    with patch('candidate_preferences.os.replace', side_effect=OSError('failure')):
        store.reset()
        assert not store.load()['selections']
    store.reset()
    assert not FilePreferenceStore(IDS, path).load()['selections']
    other.record('x', 'A'); assert store.load()['selections']['x']['A'] == 1
    other.reset(); assert not store.load()['selections']
    assert not list(path.parent.glob(path.name + '.*')) or list(path.parent.glob(path.name + '.*')) == [path.with_name(path.name + '.lock')]
    return path


def processes(path):
    store = FilePreferenceStore(IDS, path);store.reset()
    command = [sys.executable, '-B', '-X', 'utf8', str(Path(__file__).resolve()), '--worker', str(path), '25']
    children = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(3)]
    errors = []
    try:
        while any(child.poll() is None for child in children):
            try:
                payload = json.loads(path.read_text(encoding='utf-8'))
                assert payload['version'] == 1
            except PermissionError:
                pass  # Windows may briefly hold a replacement handle, never partial JSON.
            time.sleep(0.005)
        for child in children:
            output, error = child.communicate(timeout=20)
            if child.returncode: errors.append((output, error))
        assert not errors, errors
        assert store.load()['selections']['x']['A'] == 75, 'Locked process updates must preserve all increments'
    finally:
        for child in children:
            if child.poll() is None: child.kill();child.wait()
    original = path.read_bytes()
    child = subprocess.Popen(command[:-1] + ['1', '--interrupt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 20
        while not Path(str(path) + '.ready').exists():
            assert child.poll() is None, child.communicate()
            assert time.monotonic() < deadline, 'Interrupted-write worker did not reach replacement'
            time.sleep(0.01)
        child.kill();child.communicate(timeout=20)
        assert path.read_bytes() == original, 'Interrupted writes may not truncate the only valid file'
        assert store.record('x', 'A') == 76, 'Process death must release the OS lock'
    finally:
        if child.poll() is None: child.kill();child.communicate()


def bridge(folder):
    os.environ['HOKKIEN_GITHUB_REPO_PATH'] = str(ROOT)
    os.environ['HOKKIEN_HANRI_DICT_PATH'] = str(ROOT / 'data/hokkien_hanri_dict.tsv')
    shell = load(ROOT / 'desktop/tangliengim_web_shell.py', 'safeguard_shell')
    from urllib.request import Request, urlopen
    with patch.dict(os.environ, {'TANGLIENGIM_CANDIDATE_PREFERENCES_PATH': str(folder / 'bridge.json')}):
        server = shell.DesktopHttpServer(ROOT, ROOT / 'desktop/Hokkien Tangliengim IME Pad.py')
        thread = threading.Thread(target=server.serve_forever, daemon=True);thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        def post(payload, endpoint='record'):
            request = Request(base + '/desktop-api/candidate-preferences/' + endpoint,
                data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
            with urlopen(request, timeout=10) as response: return json.load(response)
        try:
            choice = {'lookupKey': '가긔', 'entryId': 'U+5BB6_U+5DF1_00', 'selectionId': 'session:1'}
            assert post(choice)['count'] == 1
            assert post(choice)['count'] == 1
            with ThreadPoolExecutor(max_workers=4) as pool:
                assert all(reply['count'] == 1 for reply in pool.map(post, [choice] * 8))
            assert post({**choice, 'selectionId': 'session:2'})['count'] == 2
            post(choice)
            assert server.candidate_preferences.load()['selections']['가긔'][choice['entryId']] == 2
            with urlopen(base + '/desktop/candidate-preferences.js', timeout=10) as response:
                script = response.read().decode()
                assert '__PREFERENCE_SESSION__' not in script and 'selectionId:' in script
            post({}, 'reset')
            assert not server.candidate_preferences.load()['selections']
            with patch.object(shell, 'active_ids_from_tsv', return_value=set()):
                assert post({**choice, 'selectionId': 'session:3'})['count'] == 0
                assert not server.candidate_preferences.load()['selections']
        finally:
            server.shutdown();thread.join();server.server_close()


def main():
    watched = list((ROOT / 'data').glob('*.tsv')) + list((ROOT / 'tests/fixtures').glob('*baseline*.json')) + [ROOT / 'public/data/hokkien-hanri-dict.json']
    hashes = {p: hashlib.sha256(p.read_bytes()).digest() for p in watched}
    shared_cases()
    with tempfile.TemporaryDirectory(prefix='tangliengim-exodus-ii-') as temporary:
        folder = Path(temporary)
        path = files(folder)
        processes(path)
        bridge(folder)
    assert hashes == {p: hashlib.sha256(p.read_bytes()).digest() for p in watched}, 'Safeguards must not mutate source data or baselines'
    print('PASS: Exodus II Python/Web shared fixtures, 1,024 monotonic counts, 160 seeded rankings; malformed stores, failed/atomic/interrupted writes, three concurrent processes, reset/restart and bridge duplicate receipts; source invariants unchanged.')


if __name__ == '__main__':
    if '--worker' in sys.argv:
        at = sys.argv.index('--worker');worker(sys.argv[at+1], int(sys.argv[at+2]), '--interrupt' in sys.argv)
    else:
        main()
