"""Verify that the desktop shell serves the canonical Web IME checkout."""

from __future__ import annotations

import importlib.util
import os
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


def main() -> None:
    shell = load_shell()
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
