"""Run the shared Web IME as a local desktop app window.

The browser UI and IME engine are served directly from the GitHub checkout.
Desktop-only HTML and TSV tools remain available through the classic Tkinter
window while their bridge is migrated.
"""

from __future__ import annotations

import json
import mimetypes
import os
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


DESKTOP_SCRIPT = r"""
(() => {
  if (document.querySelector("#desktopToolsButton")) return;
  const header = document.querySelector(".ime-header");
  const dictionaryLink = header?.querySelector(".dictionary-link");
  if (!header || !dictionaryLink) return;

  const actions = document.createElement("div");
  actions.style.display = "flex";
  actions.style.alignItems = "center";
  actions.style.gap = "8px";
  dictionaryLink.replaceWith(actions);
  actions.append(dictionaryLink);

  const button = document.createElement("button");
  button.id = "desktopToolsButton";
  button.className = "dictionary-link";
  button.type = "button";
  button.textContent = "Desktop tools";
  button.addEventListener("click", async () => {
    button.disabled = true;
    try {
      const response = await fetch("/desktop-api/open-classic", { method: "POST" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
    } finally {
      window.setTimeout(() => { button.disabled = false; }, 500);
    }
  });
  actions.append(button);
})();
""".strip()


def _edge_candidates() -> list[Path]:
    candidates: list[Path] = []
    resolved = shutil.which("msedge")
    if resolved:
        candidates.append(Path(resolved))
    for variable in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA"):
        root = os.environ.get(variable)
        if root:
            candidates.append(Path(root) / "Microsoft" / "Edge" / "Application" / "msedge.exe")
    return candidates


def find_edge() -> Path | None:
    return next((path for path in _edge_candidates() if path.is_file()), None)


def _safe_repo_file(repo_root: Path, request_path: str) -> Path | None:
    path = unquote(urlsplit(request_path).path)
    if ".." in Path(path).parts:
        return None
    if path in {"", "/"}:
        return None
    if path == "/favicon.ico":
        relative = Path("favicon.ico")
    elif path.startswith("/ime/"):
        suffix = path.removeprefix("/ime/") or "index.html"
        relative = Path("apps") / "ime" / suffix
    elif path.startswith("/dictionary/"):
        suffix = path.removeprefix("/dictionary/") or "index.html"
        relative = Path("apps") / "dictionary" / suffix
    elif path.startswith(("/shared/", "/public/", "/assets/")):
        relative = Path(path.lstrip("/"))
    else:
        return None

    target = (repo_root / relative).resolve()
    try:
        target.relative_to(repo_root.resolve())
    except ValueError:
        return None
    return target if target.is_file() else None


class DesktopRequestHandler(BaseHTTPRequestHandler):
    server: "DesktopHttpServer"

    def log_message(self, _format: str, *_args) -> None:
        return

    def _send_bytes(self, data: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def _redirect(self, location: str) -> None:
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlsplit(self.path).path
        if path in {"", "/"}:
            self._redirect("/ime/?desktop=1")
            return
        if path == "/ime":
            self._redirect("/ime/?desktop=1")
            return
        if path == "/dictionary":
            self._redirect("/dictionary/")
            return
        if path == "/desktop/desktop-shell.js":
            self._send_bytes(DESKTOP_SCRIPT.encode("utf-8"), "text/javascript; charset=utf-8")
            return

        target = _safe_repo_file(self.server.repo_root, self.path)
        if target is None:
            self.send_error(404)
            return
        data = target.read_bytes()
        if target == self.server.repo_root / "apps" / "ime" / "index.html":
            html = data.decode("utf-8")
            html = html.replace(
                "</body>",
                '    <script src="/desktop/desktop-shell.js"></script>\n  </body>',
            )
            data = html.encode("utf-8")
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or target.suffix in {".js", ".json", ".svg"}:
            content_type += "; charset=utf-8"
        self._send_bytes(data, content_type)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if urlsplit(self.path).path != "/desktop-api/open-classic":
            self.send_error(404)
            return
        try:
            self.server.open_classic_tools()
            payload = json.dumps({"ok": True}).encode("utf-8")
            self._send_bytes(payload, "application/json; charset=utf-8")
        except Exception as exc:
            payload = json.dumps({"ok": False, "error": str(exc)}).encode("utf-8")
            self._send_bytes(payload, "application/json; charset=utf-8", status=500)


class DesktopHttpServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, repo_root: Path, classic_script: Path):
        super().__init__(("127.0.0.1", 0), DesktopRequestHandler)
        self.repo_root = repo_root.resolve()
        self.classic_script = classic_script.resolve()
        self.classic_process: subprocess.Popen | None = None

    def open_classic_tools(self) -> None:
        if self.classic_process is not None and self.classic_process.poll() is None:
            return
        interpreter = Path(sys.executable)
        pythonw = interpreter.with_name("pythonw.exe")
        if os.name == "nt" and pythonw.is_file():
            interpreter = pythonw
        env = os.environ.copy()
        env["HOKKIEN_IME_PYTHONW_LAUNCHED"] = "1"
        self.classic_process = subprocess.Popen(
            [str(interpreter), str(self.classic_script), "--classic-ui"],
            cwd=str(self.classic_script.parent),
            env=env,
            close_fds=True,
        )


def _fallback_browser_host(url: str) -> None:
    import tkinter as tk

    webbrowser.open_new(url)
    root = tk.Tk()
    root.title("Hokkien Tangliengim IME Pad")
    root.geometry("340x92")
    root.resizable(False, False)
    tk.Label(root, text="The IME is open in your browser.", padx=18, pady=12).pack()
    tk.Button(root, text="Close IME", command=root.destroy).pack()
    root.mainloop()


def run_desktop_shell(repo_root: Path, classic_script: Path) -> None:
    repo_root = repo_root.resolve()
    required = [
        repo_root / "apps" / "ime" / "index.html",
        repo_root / "shared" / "web-ime-core.js",
        repo_root / "public" / "data" / "hokkien-hanri-dict.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing shared web files: " + ", ".join(missing))

    server = DesktopHttpServer(repo_root, classic_script)
    thread = threading.Thread(target=server.serve_forever, name="TangliengimDesktopServer", daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/ime/?desktop=1"
    try:
        edge = find_edge()
        if edge is None:
            _fallback_browser_host(url)
            return
        profile = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Tangliengim" / "DesktopProfile"
        profile.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()
        process = subprocess.Popen(
            [
                str(edge),
                f"--app={url}",
                f"--user-data-dir={profile}",
                "--no-first-run",
                "--disable-features=msEdgeFirstRunExperience",
            ],
            close_fds=True,
        )
        process.wait()
        if time.monotonic() - started < 2:
            _fallback_browser_host(url)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    classic_script = Path(__file__).resolve().with_name("Hokkien Tangliengim IME Pad.py")
    run_desktop_shell(repo_root, classic_script)


if __name__ == "__main__":
    main()
