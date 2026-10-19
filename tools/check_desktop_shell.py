"""Verify that the desktop shell serves the canonical Web IME checkout."""

from __future__ import annotations

import csv
import json
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from urllib.request import urlopen
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
SHELL_PATH = ROOT / "desktop" / "tangliengim_web_shell.py"
PAD_PATH = ROOT / "desktop" / "Hokkien Tangliengim IME Pad.py"


def load_shell():
    spec = importlib.util.spec_from_file_location("tangliengim_web_shell_check", SHELL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_hidden_tones_in_bracketed_tsv_input() -> None:
    spec = importlib.util.spec_from_file_location("tangliengim_pad_check", PAD_PATH)
    assert spec and spec.loader
    pad_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = pad_module
    spec.loader.exec_module(pad_module)

    source = "[德國뎩걱] 뎩"
    pad = pad_module.HokkienIMEPad.__new__(pad_module.HokkienIMEPad)
    from types import SimpleNamespace
    hints = json.loads((ROOT / 'tests/fixtures/keyboard-romanisation-hints.json').read_text(encoding='utf-8'))
    pad.input_mode = SimpleNamespace(get=lambda: 'hangul')
    for key, expected in hints.items():
        pad.keyboard_help_shifted = False
        normal = pad.keyboard_guide_romanisation_hint(key)
        pad.keyboard_help_shifted = True
        shifted = pad.keyboard_guide_romanisation_hint(key)
        assert [normal, shifted] == expected, (key, normal, shifted)
    pad.keyboard_help_shifted = False
    for key in ['1', '2', '4', '5', 'Space', 'Shift', 'Backspace', '’']:
        assert pad.keyboard_guide_romanisation_hint(key) == '', key
    for mode in ['lomari', 'bopomofo']:
        pad.input_mode = SimpleNamespace(get=lambda: mode)
        assert all(pad.keyboard_guide_romanisation_hint(key) == '' for key in hints)
    pad.input_mode = SimpleNamespace(get=lambda: 'hangul')
    pad.composer = pad_module.Composer(output=source, cursor_pos=len(source))
    pad.hanri_instance_readings = []
    pad.hanri_instance_text_snapshot = source
    pad.hangul_instance_readings = [
        {"start": 3, "end": 4, "hangul": "뎩", "reading": "뎩1"},
        {"start": 7, "end": 8, "hangul": "뎩", "reading": "뎩2"},
    ]
    tsv_input = pad.text_with_hanri_instance_readings(
        source, include_hanri=False, bracketed_hangul_only=True
    )
    assert tsv_input == "[德國뎩1걱] 뎩", tsv_input
    html_input = pad.text_with_hanri_instance_readings(source)
    assert html_input == "[德國뎩1걱] 뎩2", html_input

    gui_spec = importlib.util.spec_from_file_location(
        "tangliengim_converter_check", ROOT / "desktop" / "hokkien_tone_marker_gui.py"
    )
    assert gui_spec and gui_spec.loader
    converter = importlib.util.module_from_spec(gui_spec)
    sys.modules[gui_spec.name] = converter
    gui_spec.loader.exec_module(converter)
    with patch.dict(os.environ, {"HOKKIEN_GITHUB_REPO_PATH": str(ROOT)}):
        os.environ.pop("HOKKIEN_HANRI_DICT_PATH", None)
        expected = ROOT / "data" / "hokkien_hanri_dict.tsv"
        assert pad_module.hanri_tsv_path_candidates() == [expected]
        assert converter.hanri_tsv_candidates() == [expected]
        assert converter.hanri_tsv_path_for_write() == expected
    formatted = pad_module.format_text_tones_for_output(tsv_input)
    annotations = converter.hanri_hangul_bracket_annotations(formatted)
    assert len(annotations) == 1, annotations
    assert annotations[0]["hanri"] == "德國", annotations
    assert annotations[0]["reading"] == "뎩1걱", annotations

    pad.hangul_instance_readings = [
        {"start": 3, "end": 5, "hangul": "뎩걱", "reading": "뎩1걱"},
    ]
    assert pad.text_with_hanri_instance_readings(
        source, include_hanri=False, bracketed_hangul_only=True
    ) == "[德國뎩1걱] 뎩"

    with tempfile.TemporaryDirectory() as folder:
        target = Path(folder) / "new_readings.tsv"
        pad.ask_add_tsv_confirmation = lambda *args, **kwargs: True
        pad.mark_tsv_sync_pending = lambda: None
        with (
            patch.dict(os.environ, {"HOKKIEN_HANRI_DICT_PATH": str(target)}),
            patch.object(converter, "hanri_reading_entry_exists", return_value=False),
            patch.object(converter, "existing_hanri_readings", return_value=[]),
            patch.object(pad_module, "reload_hanri_resources"),
        ):
            assert pad.confirm_and_save_bracketed_hanri_annotations(converter, formatted)
        with target.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            assert tuple(reader.fieldnames) == converter.dictionary_schema_api().DICTIONARY_COLUMNS
            rows = list(reader)
        assert len(rows) == 1 and rows[0]['reading'] == '뎩1걱', rows
        assert rows[0]['hanri'] == '德國' and 'priority' not in rows[0], rows
        assert rows[0]['entry_id'] == 'U+5FB7_U+570B_00', rows
        assert rows[0]['simplified'] == '德国', rows
        assert rows[0]['mandarin_trad'] == rows[0]['mandarin_simp'] == '', rows
        registry = target.with_name("dictionary_entry_id_registry.tsv")
        assert registry.is_file(), registry
        with registry.open("a", encoding="utf-8", newline="") as stream:
            csv.writer(stream, delimiter="\t", lineterminator="\r\n").writerow(
                ["U+5FB7_U+570B_01", "德國", ""]
            )
        with (
            patch.dict(os.environ, {"HOKKIEN_HANRI_DICT_PATH": str(target)}),
            patch.object(converter, "hanri_reading_entry_exists", return_value=False),
        ):
            assert converter.append_hanri_reading_to_tsv("德國", "뎩2걱")
        with target.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
        assert rows[1]['entry_id'] == 'U+5FB7_U+570B_02', rows
        assert rows[1]['simplified'] == '德国', rows


def check_repository_sync_pending(shell) -> None:
    with tempfile.TemporaryDirectory() as folder:
        # Windows CI can return an 8.3 temp path; the server resolves its root.
        repo = Path(folder).resolve()
        data = repo / "data"
        data.mkdir()
        tsv = data / "hokkien_hanri_dict.tsv"
        registry = data / "dictionary_entry_id_registry.tsv"
        tsv.write_text("dictionary\n", encoding="utf-8")
        registry.write_text("registry\n", encoding="utf-8")
        def git(*args):
            return subprocess.run(
                ["git", "-c", f"safe.directory={repo.as_posix()}", "-C", str(repo), *args],
                check=True, capture_output=True,
            )
        git("init", "--initial-branch=main")
        git("config", "user.name", "TSV test")
        git("config", "user.email", "tsv-test@example.invalid")
        git("add", "data")
        git("commit", "-m", "Initial dictionary")
        git("update-ref", "refs/remotes/origin/main", "HEAD")
        classic = repo / "classic" / "pad.py"
        classic.parent.mkdir()
        classic.with_name("hokkien_hanri_dict.tsv").write_text("stale copy", encoding="utf-8")
        server = shell.DesktopHttpServer(repo, classic)
        try:
            assert server.local_tsv_path() == tsv
            assert not server.tsv_sync_pending()
            tsv.write_text("changed dictionary\n", encoding="utf-8")
            assert server.tsv_sync_pending()
            git("add", "data")
            git("commit", "-m", "New reading")
            assert server.tsv_sync_pending(), "Unpushed dictionary commits must remain pending"
            git("update-ref", "refs/remotes/origin/main", "HEAD")
            assert not server.tsv_sync_pending()
            registry.write_text("changed registry\n", encoding="utf-8")
            assert server.tsv_sync_pending(), "Registry changes must be published too"
        finally:
            server.server_close()


def check_html_worker_state() -> None:
    from types import SimpleNamespace
    pad = sys.modules['tangliengim_pad_check']
    copied, snapshots = [], []
    clipboard = copied.append
    app = SimpleNamespace(
        close=Mock(),
        set_system_clipboard_text=clipboard,
        load_tone_marker_module=lambda: SimpleNamespace(load_hanri_reading_index=lambda: {}),
    )
    def copy_html(style):
        snapshots.append((app.composer.text(), style,
                          list(app.hanri_instance_readings), list(app.hangul_instance_readings)))
        app.set_system_clipboard_text('<ruby>' + app.composer.text() + '</ruby>')
        return 'Copied HTML'
    app.copy_html = copy_html
    requests = [
        {'text': '뎩', 'style': 'plain', 'rememberedHangulReadings': [
            {'start': 0, 'end': 1, 'hangul': '뎩', 'reading': '뎩1'}]},
        None,
        {'text': '家己', 'style': 'song', 'rememberedReadings': [
            {'start': 0, 'end': 2, 'hanri': '家己', 'reading': '가1기'}]},
        {'text': '릐호', 'style': 'plain'},
    ]
    output = io.StringIO()
    with (
        patch.object(pad, 'DesktopHtmlService', return_value=app) as create,
        patch.object(pad, 'desktop_html_resource_signature', side_effect=['a', 'a', 'b', 'b']),
        patch.object(pad, 'reload_hanri_resources') as reload,
        patch.object(sys, 'stdin', io.StringIO('\n'.join(json.dumps(r) for r in requests))),
        patch.object(sys, 'stdout', output),
    ):
        pad.run_desktop_html_worker()
    replies = [json.loads(line) for line in output.getvalue().splitlines()]
    assert [r['ok'] for r in replies] == [True, False, True, True], replies
    assert snapshots[0][3][0]['reading'] == '뎩1'
    assert snapshots[1][1] == 'song' and not snapshots[1][3]
    assert snapshots[2] == ('릐호', 'plain', [], [])
    assert app.set_system_clipboard_text is clipboard
    assert copied == ['<ruby>뎩</ruby>', '<ruby>家己</ruby>', '<ruby>릐호</ruby>']
    create.assert_called_once()
    reload.assert_called_once()
    app.close.assert_called_once()


def check_export_only_html_service() -> None:
    pad = sys.modules['tangliengim_pad_check']
    styles = ['plain', 'lomari_ruby_below', 'lomari_next_line', 'song',
              'novel', 'novel_first', 'title']
    with (
        patch.object(pad.HokkienIMEPad, '__init__', side_effect=AssertionError('Classic IME constructed')),
        patch.object(pad.tk, 'Tk', side_effect=AssertionError('Unexpected Tk root')),
    ):
        service = pad.DesktopHtmlService()
        assert not isinstance(service, pad.HokkienIMEPad)
        service.composer = pad.Composer(output='릐호 家己')
        service.hanri_instance_text_snapshot = service.composer.text()
        converter = service.load_tone_marker_module()
        copied = []
        with patch.object(service, 'set_system_clipboard_text', side_effect=copied.append):
            for style in styles:
                service.copy_html(style)
                expected = converter.convert_hangul_to_html('릐호 家己', style)['html']
                assert copied[-1] == expected, style
            service.composer = pad.Composer(output='뎩')
            service.hangul_instance_readings = [
                {'start': 0, 'end': 1, 'hangul': '뎩', 'reading': '뎩1'}]
            service.copy_html('plain')
            expected = converter.convert_hangul_to_html(
                pad.format_text_tones_for_output('뎩1'), 'plain')['html']
            assert copied[-1] == expected, 'Selected tones must survive export'
        with patch.object(pad.sys, 'platform', 'win32'), patch.object(
            pad.HokkienIMEPad, 'set_windows_clipboard_unicode_text', return_value=False
        ):
            try:
                service.copy_html('plain')
                raise AssertionError('Clipboard failure was hidden')
            except RuntimeError as exc:
                assert 'clipboard' in str(exc)
        assert service.root is None
        service.close()

    # Confirmations alone may own a short-lived Tk root, including on errors.
    root = Mock()
    with patch.object(pad.tk, 'Tk', return_value=root):
        def confirmation(owner):
            assert owner.root is root
            raise ValueError('test dialog error')
        try:
            service.run_confirmation(confirmation)
        except ValueError:
            pass
    root.withdraw.assert_called_once()
    root.destroy.assert_called_once()
    assert service.root is None


def check_native_html_clipboard() -> None:
    import ctypes
    pad = sys.modules['tangliengim_pad_check']
    memory = ctypes.create_string_buffer(1024)
    user32 = Mock()
    user32.CreateWindowExW.return_value = 123
    user32.OpenClipboard.return_value = True
    user32.EmptyClipboard.return_value = True
    user32.SetClipboardData.return_value = 456
    kernel32 = Mock()
    kernel32.GlobalAlloc.return_value = 456
    kernel32.GlobalLock.return_value = ctypes.addressof(memory)
    with (
        patch.object(pad.sys, 'platform', 'win32'),
        patch.object(ctypes, 'WinDLL', side_effect=lambda name, **kwargs:
                     user32 if name == 'user32' else kernel32, create=True),
        patch.object(pad.tk, 'Tk', side_effect=AssertionError('Clipboard must not need Tk')),
    ):
        service = pad.DesktopHtmlService()
        service.set_system_clipboard_text('𤺪뎩\nHTML')
        expected = '𤺪뎩\r\nHTML\0'.encode('utf-16le')
        assert memory.raw[:len(expected)] == expected
        user32.OpenClipboard.assert_called_once_with(123)
        user32.SetClipboardData.assert_called_once_with(13, 456)
        user32.CloseClipboard.assert_called_once()
        user32.DestroyWindow.assert_called_once_with(123)
        kernel32.GlobalFree.assert_not_called()  # Ownership transferred to Windows.

        user32.reset_mock()
        user32.OpenClipboard.return_value = False
        try:
            service.set_system_clipboard_text('test')
            raise AssertionError('Clipboard contention must be reported')
        except RuntimeError:
            pass
        user32.EmptyClipboard.assert_not_called()
        user32.CloseClipboard.assert_not_called()
        user32.DestroyWindow.assert_called_once_with(123)


def check_persistent_html_bridge(shell) -> None:
    with tempfile.TemporaryDirectory() as folder:
        script = Path(folder) / 'worker.py'
        script.write_text(
            'import json, os, sys\n'
            'for line in sys.stdin:\n'
            '    payload = json.loads(line)\n'
            '    if payload.get("crash"): sys.exit(1)\n'
            '    print(json.dumps({"ok": not payload.get("fail"), "error": "test error", '
            '"payload": payload, "pid": os.getpid()}, ensure_ascii=False), flush=True)\n',
            encoding='utf-8',
        )
        server = shell.DesktopHttpServer(ROOT, script)
        try:
            server.start_html_bridge()
            first = server.copy_html({'text': '𤺪뎩', 'style': 'plain'})
            second = server.copy_html({'text': '家己', 'style': 'song'})
            assert first['pid'] == second['pid'], 'HTML requests must reuse the worker'
            assert first['payload']['text'] == '𤺪뎩'
            try:
                server.run_html_bridge({'fail': True})
                raise AssertionError('Worker errors must reach the caller')
            except RuntimeError as exc:
                assert str(exc) == 'test error'
            assert server.run_html_bridge({})['pid'] == first['pid']
            try:
                server.run_html_bridge({'crash': True})
                raise AssertionError('Worker exits must reach the caller')
            except RuntimeError:
                pass
            restarted = server.run_html_bridge({})
            assert restarted['pid'] != first['pid'], 'The next request must recover after a worker exit'
            process = server.html_bridge_process
        finally:
            server.server_close()
        assert process.poll() is not None, 'Closing the shell must stop its HTML worker'


def main() -> None:
    shell = load_shell()
    check_repository_sync_pending(shell)
    check_hidden_tones_in_bracketed_tsv_input()
    check_html_worker_state()
    check_export_only_html_service()
    check_native_html_clipboard()
    check_persistent_html_bridge(shell)
    # Exercise the real pipe boundary under a non-UTF-8 Windows-style default.
    with tempfile.TemporaryDirectory() as folder:
        bridge_script = Path(folder) / "echo_bridge.py"
        bridge_script.write_text(
            'import json, sys\n'
            'payload = json.load(sys.stdin)\n'
            'print(json.dumps({"ok": True, "payload": payload, '
            '"stdinEncoding": sys.stdin.encoding, "stdoutEncoding": sys.stdout.encoding}, '
            'ensure_ascii=False))\n',
            encoding="utf-8",
        )
        bridge_server = shell.DesktopHttpServer(ROOT, bridge_script)
        try:
            payload = {"text": "[德뎩] 𤆬ᄋᅷ’뽀ˊ", "style": "plain"}
            with patch.dict(os.environ, {"PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"}):
                response = bridge_server.run_bridge("--desktop-html-bridge", payload)
            assert response["payload"] == payload, response
            assert response["stdinEncoding"] == "utf-8", response
            assert response["stdoutEncoding"] == "utf-8", response
        finally:
            bridge_server.server_close()
    assert shell._safe_repo_file(ROOT, "/ime/") == ROOT / "apps" / "ime" / "index.html"
    assert shell._safe_repo_file(ROOT, "/shared/web-ime-core.js") == ROOT / "shared" / "web-ime-core.js"
    assert shell._safe_repo_file(ROOT, "/ime/../../README.md") is None

    server = shell.DesktopHttpServer(ROOT, PAD_PATH)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/ime/", timeout=5) as response:
            html = response.read().decode("utf-8")
        assert "/shared/web-ime-core.js" in html
        assert "/shared/web-audio-player.js" in html
        assert "/desktop/desktop-shell.js" in html
        with urlopen(base + "/desktop/desktop-shell.js", timeout=5) as response:
            desktop_script = response.read().decode("utf-8")
        assert "desktopHtmlButton" in desktop_script
        assert "desktopSyncButton" in desktop_script
        assert "/desktop-api/copy-html" in desktop_script
        assert "/desktop-api/sync-tsv" in desktop_script
        assert "window.resizeTo(920, 800)" in desktop_script
        with urlopen(base + "/desktop-api/status", timeout=5) as response:
            status = response.read().decode("utf-8")
        assert '"ok": true' in status
        assert json.loads(status)['tsvPending'] == server.tsv_sync_pending()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    pad_source = PAD_PATH.read_text(encoding="utf-8")
    assert "run_shared_web_shell" in pad_source
    assert "--classic-ui" in pad_source
    assert "--desktop-html-bridge" in pad_source
    assert "--desktop-sync-bridge" in pad_source
    assert "run_desktop_html_bridge" in pad_source
    assert "run_desktop_sync_bridge" in pad_source
    shell_source = SHELL_PATH.read_text(encoding="utf-8")
    assert '"--window-size=920,800"' in shell_source
    print("OK: desktop shell serves the shared Web IME with local HTML and TSV extensions.")


if __name__ == "__main__":
    main()
