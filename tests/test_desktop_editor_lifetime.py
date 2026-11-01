"""Popup lifetime follows editor pages rather than Edge process delegation."""
import io
import json
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'desktop'))
import tangliengim_web_shell as shell


class EditorLifetimeTests(unittest.TestCase):
    def test_http_heartbeat_and_page_injection(self):
        server = shell.DesktopHttpServer(ROOT, ROOT / 'desktop/Hokkien Tangliengim IME Pad.py')
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            for route in ('/editors/', '/editor/', '/website-editor/', '/website-editor/lyric-timing.html'):
                with urlopen(base + route) as response:
                    self.assertIn('/desktop/editor-lifetime.js', response.read().decode())
            with urlopen(base + '/desktop-api/session') as response:
                self.assertIsNone(json.load(response)['editorHeartbeatAge'])
            request = Request(base + '/desktop-api/editor-heartbeat', b'{}',
                              {'Content-Type': 'application/json', 'Origin': base})
            with urlopen(request) as response:
                self.assertTrue(json.load(response)['ok'])
            with urlopen(base + '/desktop-api/session') as response:
                self.assertLess(json.load(response)['editorHeartbeatAge'], 5)
            request.add_header('Origin', 'https://unrelated.example')
            with self.assertRaises(HTTPError) as error:
                urlopen(request)
            self.assertEqual(error.exception.code, 403)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def wait_with_clock(self, response):
        clock = [0]
        def sleep(seconds):
            clock[0] += seconds
        def read(*args, **kwargs):
            result = response(clock[0])
            if isinstance(result, Exception):
                raise result
            return io.StringIO(json.dumps(result))
        with patch.object(shell.time, 'monotonic', side_effect=lambda: clock[0]), \
             patch.object(shell.time, 'sleep', side_effect=sleep), \
             patch.object(shell, 'urlopen', side_effect=read):
            shell._wait_for_editor_windows('http://127.0.0.1:1234/editors/')
        return clock[0]

    def test_window_lease_survives_navigation_and_server_restart(self):
        def response(now):
            if 20 <= now < 25:
                return OSError('Restarting')
            return {'instance': 'first' if now < 20 else 'replacement',
                    'editorHeartbeatAge': 0 if now < 65 else now - 65}
        self.assertEqual(self.wait_with_clock(response), 245)

    def test_no_window_connects_reports_failure_without_browser_fallback(self):
        with self.assertRaisesRegex(RuntimeError, 'did not connect'):
            self.wait_with_clock(lambda now: {'instance': 'first', 'editorHeartbeatAge': None})


if __name__ == '__main__':
    unittest.main()
