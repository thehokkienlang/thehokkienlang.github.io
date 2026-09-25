"""Run the shared Web IME with local-only desktop extensions.

The visible interface and IME engine come directly from the GitHub checkout.
HTML export and TSV syncing call the mature Tkinter implementation through a
small localhost bridge, so those desktop-only capabilities do not fork the
shared browser engine.
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
  if (document.querySelector("#desktopHtmlButton")) return;
  try { window.resizeTo(800, 600); } catch {}
  const actions = document.querySelector(".toolbar-actions");
  if (!actions) return;

  const style = document.createElement("style");
  style.textContent = `
    .desktop-html-style,
    .desktop-action-button {
      height: 38px;
      border: 1px solid #bfd0e4;
      border-radius: 6px;
      background: #fff;
      color: #31516f;
      font: 700 0.88rem Calibri, "Segoe UI", sans-serif;
    }
    .desktop-html-style { max-width: 174px; padding: 0 28px 0 9px; }
    .desktop-action-button { padding: 0 11px; cursor: pointer; }
    .desktop-action-button:hover:not(:disabled) { border-color: rgba(15,118,110,.5); color: #0b5f58; }
    .desktop-action-button:disabled { cursor: default; opacity: .48; }
    @media (max-width: 650px) {
      .desktop-html-style { max-width: 142px; }
      .desktop-action-button { padding-inline: 8px; }
    }
  `;
  document.head.append(style);

  const htmlStyle = document.createElement("select");
  htmlStyle.id = "desktopHtmlStyle";
  htmlStyle.className = "desktop-html-style";
  htmlStyle.setAttribute("aria-label", "HTML mode");
  const modes = [
    ["plain", "Plain inline"],
    ["lomari_ruby_below", "Lomari ruby below"],
    ["lomari_next_line", "Mandarin + Lomari"],
    ["song", "Lyrics"],
    ["novel", "Novel paragraph"],
    ["novel_first", "Novel first line"],
    ["title", "Title"],
  ];
  for (const [value, label] of modes) htmlStyle.add(new Option(label, value));
  htmlStyle.value = localStorage.getItem("tangliengim-html-style") || "plain";
  htmlStyle.addEventListener("change", () => localStorage.setItem("tangliengim-html-style", htmlStyle.value));

  const htmlButton = document.createElement("button");
  htmlButton.id = "desktopHtmlButton";
  htmlButton.className = "desktop-action-button";
  htmlButton.type = "button";
  htmlButton.textContent = "HTML";
  htmlButton.title = "Copy current text as HTML";

  const syncButton = document.createElement("button");
  syncButton.id = "desktopSyncButton";
  syncButton.className = "desktop-action-button";
  syncButton.type = "button";
  syncButton.textContent = "Sync TSV";
  syncButton.disabled = true;

  actions.append(htmlStyle, htmlButton, syncButton);

  async function request(path, payload = {}) {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
    return result;
  }

  async function refreshStatus() {
    try {
      const response = await fetch("/desktop-api/status", { cache: "no-store" });
      const result = await response.json();
      syncButton.disabled = !result.tsvPending;
    } catch {
      syncButton.disabled = true;
    }
  }

  htmlButton.addEventListener("click", async () => {
    if (!imeText.value.trim()) {
      showToast("No text to copy");
      return;
    }
    htmlButton.disabled = true;
    showToast("Preparing HTML...");
    try {
      const result = await request("/desktop-api/copy-html", {
        text: imeText.value,
        style: htmlStyle.value,
        rememberedReadings: imeController.getRememberedHanriReadings(imeText.value),
        rememberedHangulReadings: imeController.getRememberedHangulReadings(imeText.value),
      });
      syncButton.disabled = !result.tsvPending;
      showToast(result.message || "Copied HTML");
    } catch (error) {
      showToast(`Could not copy HTML: ${error.message}`);
    } finally {
      htmlButton.disabled = false;
      imeText.focus();
    }
  });

  syncButton.addEventListener("click", async () => {
    syncButton.disabled = true;
    showToast("Syncing TSV...");
    try {
      const result = await request("/desktop-api/sync-tsv");
      showToast(result.message || "TSV synced");
    } catch (error) {
      showToast(`Could not sync TSV: ${error.message}`);
    } finally {
      await refreshStatus();
      imeText.focus();
    }
  });

  window.TangliengimDesktopExtensions = { refreshStatus };
  refreshStatus();
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

    def _send_json(self, payload: dict, status: int = 200) -> None:
        self._send_bytes(
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            "application/json; charset=utf-8",
            status=status,
        )

    def _read_json(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Invalid request length") from exc
        if length < 0 or length > 4 * 1024 * 1024:
            raise ValueError("Request is too large")
        raw = self.rfile.read(length) if length else b"{}"
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Expected a JSON object")
        return payload

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
        if path == "/desktop-api/status":
            self._send_json({"ok": True, "tsvPending": self.server.tsv_sync_pending()})
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
        path = urlsplit(self.path).path
        try:
            payload = self._read_json()
            if path == "/desktop-api/copy-html":
                result = self.server.copy_html(payload)
            elif path == "/desktop-api/sync-tsv":
                result = self.server.sync_tsv()
            elif path == "/desktop-api/open-classic":
                self.server.open_classic_tools()
                result = {"ok": True}
            else:
                self.send_error(404)
                return
            self._send_json(result)
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=500)


class DesktopHttpServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, repo_root: Path, classic_script: Path):
        super().__init__(("127.0.0.1", 0), DesktopRequestHandler)
        self.repo_root = repo_root.resolve()
        self.classic_script = classic_script.resolve()
        self.classic_process: subprocess.Popen | None = None
        self.bridge_lock = threading.Lock()

    def local_tsv_path(self) -> Path:
        beside_classic = self.classic_script.with_name("hokkien_hanri_dict.tsv")
        if beside_classic.is_file():
            return beside_classic
        return self.repo_root / "data" / "hokkien_hanri_dict.tsv"

    def tsv_sync_pending(self) -> bool:
        source = self.local_tsv_path()
        destination = self.repo_root / "data" / "hokkien_hanri_dict.tsv"
        if not source.is_file() or not destination.is_file():
            return False
        return source.resolve() != destination.resolve() and source.read_bytes() != destination.read_bytes()

    def bridge_interpreter(self) -> Path:
        interpreter = Path(sys.executable)
        if interpreter.name.lower() == "pythonw.exe":
            console_python = interpreter.with_name("python.exe")
            if console_python.is_file():
                return console_python
        return interpreter

    def run_bridge(self, flag: str, payload: dict | None = None) -> dict:
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
        env = os.environ.copy()
        env["HOKKIEN_GITHUB_REPO_PATH"] = str(self.repo_root)
        # subprocess encoding controls only the parent; set the child's pipes too.
        env["PYTHONIOENCODING"] = "utf-8"
        with self.bridge_lock:
            result = subprocess.run(
                [str(self.bridge_interpreter()), str(self.classic_script), flag],
                input=json.dumps(payload or {}, ensure_ascii=False),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(self.classic_script.parent),
                env=env,
                timeout=3600,
                creationflags=creationflags,
                check=False,
            )
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        response = None
        for line in reversed(lines):
            try:
                candidate = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(candidate, dict):
                response = candidate
                break
        if result.returncode != 0 or not response:
            detail = result.stderr.strip() or result.stdout.strip() or f"Bridge exited with {result.returncode}"
            raise RuntimeError(detail)
        if not response.get("ok"):
            raise RuntimeError(str(response.get("error") or "Desktop bridge failed"))
        return response

    def copy_html(self, payload: dict) -> dict:
        text = str(payload.get("text") or "")
        style = str(payload.get("style") or "plain")
        valid_styles = {"plain", "lomari_ruby_below", "lomari_next_line", "song", "novel", "novel_first", "title"}
        if not text.strip():
            raise ValueError("No text to copy")
        if style not in valid_styles:
            raise ValueError("Unknown HTML mode")
        response = self.run_bridge("--desktop-html-bridge", payload)
        response["tsvPending"] = self.tsv_sync_pending()
        return response

    def sync_tsv(self) -> dict:
        response = self.run_bridge("--desktop-sync-bridge")
        response["tsvPending"] = self.tsv_sync_pending()
        return response

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
                "--window-size=800,600",
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
