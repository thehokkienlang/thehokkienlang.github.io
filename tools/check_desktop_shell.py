"""Verify that the desktop shell serves the canonical Web IME checkout."""

from __future__ import annotations

import csv
import importlib.util
import os
import sys
import tempfile
import threading
from pathlib import Path
from urllib.request import urlopen
from unittest.mock import patch


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
            rows = list(csv.reader(stream, delimiter="\t"))
        assert rows == [["뎩1걱", "德國", "1", ""]], rows


def main() -> None:
    shell = load_shell()
    check_hidden_tones_in_bracketed_tsv_input()
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
        assert "window.resizeTo(800, 600)" in desktop_script
        with urlopen(base + "/desktop-api/status", timeout=5) as response:
            status = response.read().decode("utf-8")
        assert '"ok": true' in status
        assert '"tsvPending": false' in status
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
    assert '"--window-size=800,600"' in shell_source
    print("OK: desktop shell serves the shared Web IME with local HTML and TSV extensions.")


if __name__ == "__main__":
    main()
