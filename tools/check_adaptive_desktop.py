"""Focused Exodus I persistence, classic event and Web/Python parity checks."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import threading
from pathlib import Path
from types import SimpleNamespace
from urllib.request import Request, urlopen
from unittest.mock import patch

from candidate_preferences import FilePreferenceStore, lookup_key, rank_candidates, sanitize

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    reference = ROOT
    if '--reference-root' in sys.argv:
        reference = Path(sys.argv[sys.argv.index('--reference-root') + 1])
    os.environ['HOKKIEN_GITHUB_REPO_PATH'] = str(reference)
    os.environ['HOKKIEN_HANRI_DICT_PATH'] = str(reference / 'data/hokkien_hanri_dict.tsv')
    pad_path = reference / 'desktop/Hokkien Tangliengim IME Pad.py'
    if '--pad-file' in sys.argv:
        pad_path = Path(sys.argv[sys.argv.index('--pad-file') + 1])
    pad_module = load(pad_path, 'adaptive_pad_check')
    pad = pad_module.HokkienIMEPad.__new__(pad_module.HokkienIMEPad)
    pad.output_tones_on = SimpleNamespace(get=lambda: False)
    pad.input_mode = SimpleNamespace(get=lambda: 'hangul')
    pad.hanri_on = SimpleNamespace(get=lambda: True)
    pad.suppressed_hanri_contexts = set()
    pad.lomari_raw = ''
    with tempfile.TemporaryDirectory() as folder:
        prefs_path = Path(folder) / 'preferences.json'
        store = FilePreferenceStore(set(pad_module.dictionary_ranking_api().source_id(entry)
            for entries in pad_module.HANRI_DICT.values() for entry in entries), prefs_path)
        pad._candidate_preference_store = store
        menus = []
        groups = pad_module.HANRI_DICT.items() if '--events-only' not in sys.argv else []
        for key, entries in groups:
            for text in dict.fromkeys([key, *(entry['reading'] for entry in entries)]):
                pad.composer = pad_module.Composer(output=text, cursor_pos=len(text))
                menu = pad.find_hanri_candidate()
                if menu and hasattr(pad, 'adapt_candidate_menu'):
                    menu = pad.adapt_candidate_menu(menu)
                menus.append([text, {field: menu.get(field) for field in (
                    'prefix', 'suffix', 'matched_text', 'reading', 'choices', 'labels',
                    'choice_readings', 'choice_auto_sandhi')} if menu else None])
        snapshot = {'menus': len(menus), 'sha256': hashlib.sha256(
            json.dumps(menus, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()}
        baseline = ROOT / 'tests/fixtures/adaptive-static-desktop-baseline.json'
        if '--capture-static' in sys.argv:
            baseline.write_text(json.dumps(snapshot, indent=2) + '\n', encoding='utf-8')
            print(snapshot)
            return
        if '--events-only' not in sys.argv:
            assert snapshot == json.loads(baseline.read_text(encoding='utf-8')), (snapshot, 'Cold-start classic menus changed')
        assert not prefs_path.exists(), 'Menu display must not persist learning'
        cases = json.loads((ROOT / 'tests/fixtures/adaptive-ranking-cases.json').read_text(encoding='utf-8'))
        for case in cases:
            candidates = [{'entry': entry} for entry in case['entries']]
            result = rank_candidates(candidates, case['key'], {'version': 1, 'selections': case['counts']}, set(case['ids']))
            assert [item['entry']['id'] for item in result] == case['expected'], case['name']
        # Exercise actual classic commit paths without creating a GUI window.
        identity = 'U+5BB6_U+5DF1_00'
        store = FilePreferenceStore({identity}, prefs_path)
        pad._candidate_preference_store = store
        pad.composer = pad_module.Composer(output='가긔' + pad_module.INTERNAL_TONE_MARKS['2'], cursor_pos=3)
        assert pad.adapt_candidate_menu({'prefix': '', 'choices': ['家己'], 'labels': ['1  家己'],
            'choice_entries': [{'entry_id': identity}]})['lookup_key'] == '가긔2', 'Hidden classic tone metadata must normalize to the shared digit key'
        pad.push_undo_state = lambda: None
        pad.remember_hanri_instance_reading = lambda *args, **kwargs: None
        pad.sync_hanri_instance_readings = lambda: None
        pad.reset_lomari_buffer = lambda: None
        pad.close_candidate_popup = lambda: setattr(pad, 'candidate', None)
        pad.refresh_candidate_popup_text = lambda: None
        pad.render = lambda: None

        def open_menu():
            pad.candidate = {'choices': ['家己', '家己'], 'choice_readings': ['가1기', '가1기'],
                'choice_entries': [{'entry_id': identity}, {'entry_id': identity}], 'lookup_key': '가긔'}
            pad.candidate_index = 0
            pad.candidate_selection_explicit = False
            pad.composer = pad_module.Composer(output='가긔', cursor_pos=2)

        open_menu(); pad.commit_candidate()
        assert not store.load()['selections'], 'Passive classic Enter must not learn'
        open_menu(); pad.commit_candidate(0, explicit=True)
        assert store.load()['selections']['가긔'][identity] == 1
        pad.commit_candidate(0, explicit=True)
        assert store.load()['selections']['가긔'][identity] == 1
        for key, char in [('Escape', ''), ('Right', ''), ('q', 'q'), ('1', '1')]:
            open_menu(); pad.handle_candidate_key('Tab', '')
            pad.handle_candidate_key(key, char)
            assert store.load()['selections']['가긔'][identity] == 1
        open_menu()
        original_record = store.record
        def reentrant_record(key, entry_id):
            pad.commit_candidate(0, explicit=True)
            return original_record(key, entry_id)
        with patch.object(store, 'record', reentrant_record):
            pad.commit_candidate(0, explicit=True)
        assert store.load()['selections']['가긔'][identity] == 2
        open_menu(); pad.handle_candidate_key('Tab', ''); pad.handle_candidate_key('Return', '')
        assert store.load()['selections']['가긔'][identity] == 3
        assert FilePreferenceStore({identity}, prefs_path).load() == store.load()
        for _ in range(300): store.record('가긔', identity)
        assert store.load()['selections']['가긔'][identity] == 255
        assert lookup_key("'시ˋ") == '’시2'
        assert lookup_key('앚') != lookup_key('ᄋᅷ')
        for payload in (None, {'version': 99}, {'version': 1, 'selections': {'x': {'stale': 9, identity: 'bad'}}}):
            assert not sanitize(payload, {identity})['selections']
        store.reset(); assert not store.load()['selections']

        shell = load(ROOT / 'desktop/tangliengim_web_shell.py', 'adaptive_shell_check')
        with patch.dict(os.environ, {'TANGLIENGIM_CANDIDATE_PREFERENCES_PATH': str(prefs_path)}):
            ports = []
            first_socket = None
            try:
                for iteration in range(2):
                    server = shell.DesktopHttpServer(ROOT, ROOT / 'desktop/Hokkien Tangliengim IME Pad.py')
                    ports.append(server.server_port)
                    thread = threading.Thread(target=server.serve_forever, daemon=True)
                    thread.start()
                    base = f'http://127.0.0.1:{server.server_port}'
                    try:
                        if not iteration:
                            request = Request(base + '/desktop-api/candidate-preferences/record',
                                data=json.dumps({'lookupKey': '가긔', 'entryId': identity}).encode(),
                                headers={'Content-Type': 'application/json'})
                            with urlopen(request) as response: assert json.load(response)['count'] == 1
                        with urlopen(base + '/desktop-api/candidate-preferences') as response:
                            assert json.load(response)['selections']['가긔'][identity] == 1
                        with urlopen(base + '/ime/') as response:
                            html = response.read().decode()
                            assert html.index('desktop/candidate-preferences.js') < html.index('shared/web-ime-core.js')
                        with urlopen(base + '/dictionary/') as response:
                            assert 'desktop/candidate-preferences.js' in response.read().decode()
                    finally:
                        server.shutdown(); thread.join()
                        if not iteration:
                            first_socket = server  # Keep the first port reserved for a distinct second origin.
                        else:
                            server.server_close()
                assert ports[0] != ports[1], ports
            finally:
                if first_socket: first_socket.server_close()
    print(f'PASS: {snapshot["menus"]} exact cold-start classic menus; explicit/passive commits; bounded file persistence/reset; {len(cases)} shared scoring fixtures; two real localhost origins retain learning.')


if __name__ == '__main__':
    main()
