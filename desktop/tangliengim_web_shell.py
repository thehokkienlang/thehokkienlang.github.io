"""Run the shared Web IME with local-only desktop extensions.

The visible interface and IME engine come directly from the GitHub checkout.
HTML export uses a persistent export-only service through a small localhost
bridge. TSV syncing reuses the local Git workflow. Neither needs to construct
the classic editor or fork the shared browser engine.
"""

from __future__ import annotations

import json
import mimetypes
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
import uuid
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from candidate_preferences import FilePreferenceStore, active_ids_from_tsv
from dictionary_editor_service import EditorError

HTML_RESPONSE_TIMEOUT_SECONDS = 30


PREFERENCE_SCRIPT = r"""
(() => {
  let pending = Promise.resolve();
  const session = "__PREFERENCE_SESSION__";
  let selectionIndex = 0;
  async function request(action, payload) {
    const response = await fetch('/desktop-api/candidate-preferences' + action, {
      method: payload ? 'POST' : 'GET', cache: 'no-store',
      keepalive: Boolean(payload),
      headers: { 'Content-Type': 'application/json' },
      ...(payload ? { body: JSON.stringify(payload) } : {}),
    });
    if (!response.ok) throw new Error('Preference storage unavailable');
    return response.json();
  }
  function enqueue(action, payload) {
    pending = pending.catch(() => {}).then(() => request(action, payload));
    return pending;
  }
  window.TangliengimCandidatePreferenceBackend = {
    load: () => request('', null),
    record: (lookupKey, entryId) => enqueue('/record', { lookupKey, entryId, selectionId: `${session}:${++selectionIndex}` }),
    reset: () => enqueue('/reset', {}),
  };
})();
"""


DESKTOP_SCRIPT = r"""
(() => {
  if (document.querySelector("#desktopHtmlButton")) return;
  try { window.resizeTo(920, 800); } catch {}
  const actions = document.querySelector(".toolbar-actions");
  if (!actions) return;
  const editorToken = "__EDITOR_TOKEN__";

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
    .desktop-html-confirmation {
      width: min(520px, calc(100vw - 40px)); max-height: calc(100dvh - 40px);
      padding: 20px; border: 1px solid #bfd0e4; border-radius: 8px;
      color: #202124; background: #fff; overflow: auto;
      font: 16px Calibri, "Noto Sans KR", "Segoe UI", sans-serif;
    }
    .desktop-html-confirmation::backdrop { background: rgba(15, 23, 42, .28); }
    .desktop-html-confirmation h2 { margin: 0 0 12px; font-size: 1.05rem; }
    .desktop-html-confirmation p { margin: 0 0 18px; white-space: pre-wrap; overflow-wrap: anywhere; }
    .desktop-html-confirmation-actions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }
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

  const editorButton = document.createElement("a");
  editorButton.id = "desktopDictionaryEditor";
  editorButton.className = "desktop-action-button";
  editorButton.textContent = "Dictionary editor";
  editorButton.href = "/editor/";
  editorButton.target = "_blank";
  editorButton.style.cssText = "display:inline-flex;align-items:center;text-decoration:none";
  actions.append(htmlStyle, htmlButton, syncButton, editorButton);

  async function request(path, payload = {}, timeoutMs = 0) {
    const abort = new AbortController();
    const timer = timeoutMs ? setTimeout(() => abort.abort(), timeoutMs) : null;
    try {
      const response = await fetch(path, {
        method: "POST", signal: abort.signal,
        headers: { "Content-Type": "application/json", "X-Tangliengim-Editor": editorToken },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || `HTTP ${response.status}`);
      return result;
    } catch (error) {
      if (error.name === "AbortError") throw new Error("HTML converter did not respond. Please try again.");
      throw error;
    } finally {
      if (timer !== null) clearTimeout(timer);
    }
  }

  function confirmHtml(prompt) {
    return new Promise((resolve, reject) => {
      const dialog = document.createElement("dialog");
      dialog.className = "desktop-html-confirmation";
      dialog.setAttribute("aria-labelledby", "htmlConfirmationTitle");
      const title = document.createElement("h2");
      title.id = "htmlConfirmationTitle";
      title.textContent = prompt.title;
      const message = document.createElement("p");
      message.textContent = prompt.message;
      const buttons = document.createElement("div");
      buttons.className = "desktop-html-confirmation-actions";
      let answered = false;
      const finish = value => {
        if (answered) return;
        answered = true;
        if (dialog.open) dialog.close();
        dialog.remove();
        resolve(value);
      };
      for (const option of prompt.options) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "desktop-action-button";
        button.textContent = option.label;
        button.addEventListener("click", () => finish(option.value));
        buttons.append(button);
      }
      dialog.addEventListener("cancel", event => { event.preventDefault(); finish(prompt.cancelValue); });
      dialog.addEventListener("close", () => finish(prompt.cancelValue));
      dialog.append(title, message, buttons);
      document.body.append(dialog);
      try { dialog.showModal(); } catch (error) { dialog.remove(); reject(error); }
    });
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

  let pendingHtmlConfirmation = null;
  async function refreshDictionaryJob(id) {
    try {
      while (true) {
        const job = await request("/desktop-api/editor/job", { id });
        if (job.status === "failed") throw new Error(job.message);
        if (job.status === "done") { await loadDictionary(); return; }
        await new Promise(resolve => setTimeout(resolve, 1500));
      }
    } catch (error) { showToast("Reading saved; dictionary refresh needs attention: " + error.message); }
  }
  let dictionaryGeneration = null;
  window.addEventListener("focus", async () => {
    try {
      const response = await fetch("/desktop-api/status", { cache: "no-store" });
      const status = await response.json();
      if (dictionaryGeneration !== status.dictionaryGeneration) {
        dictionaryGeneration = status.dictionaryGeneration;
        await loadDictionary();
      }
      await refreshStatus();
    } catch {}
  });
  window.addEventListener("pagehide", () => {
    if (pendingHtmlConfirmation) navigator.sendBeacon("/desktop-api/html-cancel", new Blob([
      JSON.stringify({ id: pendingHtmlConfirmation }),
    ], { type: "application/json" }));
  });

  htmlButton.addEventListener("click", async () => {
    if (!imeText.value.trim()) {
      showToast("No text to copy");
      return;
    }
    htmlButton.disabled = true;
    showToast("Preparing HTML...");
    try {
      let result = await request("/desktop-api/copy-html", {
        text: imeText.value,
        style: htmlStyle.value,
        rememberedReadings: imeController.getRememberedHanriReadings(imeText.value),
        rememberedHangulReadings: imeController.getRememberedHangulReadings(imeText.value),
      }, 45000);
      while (result.confirmation) {
        showToast("Confirm the reading to finish copying HTML");
        pendingHtmlConfirmation = result.confirmation.id;
        const value = await confirmHtml(result.confirmation);
        pendingHtmlConfirmation = null;
        result = await request("/desktop-api/html-confirmation", {
          id: result.confirmation.id, value,
        }, 45000);
      }
      syncButton.disabled = !result.tsvPending;
      showToast(result.message || "Copied HTML");
      if (result.refreshJob) refreshDictionaryJob(result.refreshJob);
    } catch (error) {
      showToast(`Could not copy HTML: ${error.message}`);
    } finally {
      if (pendingHtmlConfirmation) {
        request("/desktop-api/html-cancel", { id: pendingHtmlConfirmation }, 5000).catch(() => {});
        pendingHtmlConfirmation = null;
      }
      htmlButton.disabled = false;
      imeText.focus();
    }
  });

  syncButton.addEventListener("click", async () => {
    syncButton.disabled = true;
    showToast("Syncing TSV...");
    try {
      const result = await request("/desktop-api/sync-tsv");
      window.open("/editor/?job=" + encodeURIComponent(result.job), "tangliengim-dictionary-editor");
      showToast("Publishing entries; see dictionary editor for progress");
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
    elif path.startswith("/editor/"):
        suffix = path.removeprefix("/editor/") or "index.html"
        if suffix not in {"index.html", "editor.css", "editor.js"}:
            return None
        relative = Path("desktop") / "dictionary_editor_ui" / suffix
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
        if self.headers.get('Host') not in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}:
            self.send_error(403)
            return
        if path == '/desktop-api/candidate-preferences':
            self._send_json(self.server.load_candidate_preferences())
            return
        if path == '/desktop/candidate-preferences.js':
            script = PREFERENCE_SCRIPT.replace('__PREFERENCE_SESSION__', uuid.uuid4().hex)
            self._send_bytes(script.encode('utf-8'), 'text/javascript; charset=utf-8')
            return
        if path in {"", "/"}:
            self._redirect("/ime/?desktop=1")
            return
        if path == "/ime":
            self._redirect("/ime/?desktop=1")
            return
        if path == "/dictionary":
            self._redirect("/dictionary/")
            return
        if path == "/editor":
            self._redirect("/editor/")
            return
        if path == "/desktop/desktop-shell.js":
            script = DESKTOP_SCRIPT.replace('__EDITOR_TOKEN__', self.server.editor_token)
            self._send_bytes(script.encode("utf-8"), "text/javascript; charset=utf-8")
            return
        if path == "/desktop-api/status":
            self._send_json({"ok": True, "tsvPending": self.server.tsv_sync_pending(),
                             "dictionaryGeneration": self.server.editor.generation})
            return

        target = _safe_repo_file(self.server.repo_root, self.path)
        if target is None:
            self.send_error(404)
            return
        data = target.read_bytes()
        if target == self.server.repo_root / 'desktop/dictionary_editor_ui/index.html':
            data = data.replace(b'__EDITOR_TOKEN__', self.server.editor_token.encode())
        if target in [self.server.repo_root / 'apps' / app / 'index.html' for app in ('ime', 'dictionary')]:
            html = data.decode('utf-8').replace(
                '</head>',
                '    <script src="/desktop/candidate-preferences.js"></script>\n  </head>',
            )
            data = html.encode('utf-8')
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
            host = self.headers.get('Host')
            if host not in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}:
                raise EditorError('Invalid local host.', code='forbidden')
            origin = self.headers.get('Origin')
            if (origin and origin != f'http://{host}') or self.headers.get('Sec-Fetch-Site') == 'cross-site':
                raise EditorError('Only the local desktop interface may change the dictionary.', code='forbidden')
            payload = self._read_json()
            if path.startswith('/desktop-api/editor/'):
                if self.headers.get('X-Tangliengim-Editor') != self.server.editor_token:
                    raise EditorError('Editor session expired. Reload this page.', code='forbidden')
                result = self.server.editor.dispatch(path.removeprefix('/desktop-api/editor/'), payload)
            elif path == "/desktop-api/copy-html":
                result = self.server.copy_html(payload)
            elif path == "/desktop-api/html-confirmation":
                result = self.server.confirm_html(payload)
            elif path == "/desktop-api/html-cancel":
                result = self.server.cancel_html(payload)
            elif path == '/desktop-api/candidate-preferences/record':
                result = self.server.record_candidate_preference(payload)
            elif path == '/desktop-api/candidate-preferences/reset':
                with self.server.bridge_lock:
                    self.server.candidate_preferences.reset()
                    result = {'ok': True, 'preferences': self.server.candidate_preferences.load()}
            elif path == "/desktop-api/sync-tsv":
                result = self.server.sync_tsv()
            elif path == "/desktop-api/open-classic":
                self.server.open_classic_tools()
                result = {"ok": True}
            else:
                self.send_error(404)
                return
            self._send_json(result)
        except EditorError as exc:
            self._send_json({"ok": False, "error": str(exc), "code": exc.code, "details": exc.details},
                            status=403 if exc.code == 'forbidden' else 409 if exc.code in {'stale', 'conflict'} else 400)
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=500)


class DesktopHttpServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, repo_root: Path, classic_script: Path):
        super().__init__(("127.0.0.1", 0), DesktopRequestHandler)
        self.repo_root = repo_root.resolve()
        self.classic_script = classic_script.resolve()
        self.classic_process: subprocess.Popen | None = None
        self.bridge_lock = threading.RLock()
        self.html_bridge_process = None
        self.html_bridge_responses = None
        self.html_bridge_errors = None
        self.html_confirmation_id = None
        self.candidate_preferences = FilePreferenceStore(active_ids_from_tsv(self.local_tsv_path()))
        self.preference_receipts = OrderedDict()
        from dictionary_editor import DictionaryEditorController
        self.editor_token = uuid.uuid4().hex
        self.editor = DictionaryEditorController(self)

    def load_candidate_preferences(self) -> dict:
        with self.bridge_lock:
            current = active_ids_from_tsv(self.local_tsv_path())
            self.candidate_preferences.active_ids = current
            return self.candidate_preferences.load()

    def record_candidate_preference(self, payload: dict) -> dict:
        key, identity = payload.get('lookupKey'), payload.get('entryId')
        operation = payload.get('selectionId')
        if operation is not None and (not isinstance(operation, str) or not operation or len(operation) > 128):
            raise ValueError('Invalid selection operation')
        with self.bridge_lock:
            self.load_candidate_preferences()
            if operation in self.preference_receipts:
                previous_key, previous_id, count = self.preference_receipts[operation]
                if (key, identity) != (previous_key, previous_id):
                    raise ValueError('Selection operation reused for a different candidate')
            else:
                count = self.candidate_preferences.record(key, identity)
                if operation is not None:
                    self.preference_receipts[operation] = (key, identity, count)
                    # Receipts are temporary event deduplication, not learned history.
                    if len(self.preference_receipts) > 512:
                        self.preference_receipts.popitem(last=False)
            return {'ok': True, 'count': count, 'preferences': self.candidate_preferences.load()}

    def local_tsv_path(self) -> Path:
        return self.repo_root / "data" / "hokkien_hanri_dict.tsv"

    def tsv_sync_pending(self) -> bool:
        if not (self.repo_root / ".git").exists():
            return False
        paths = ["data/hokkien_hanri_dict.tsv", "data/dictionary_entry_id_registry.tsv", "data/dictionary_priority.tsv", "data/dictionary_redirects.tsv", "data/dictionary_categories.tsv"]
        command = ["git", "-c", f"safe.directory={self.repo_root.as_posix()}", "-C", str(self.repo_root)]
        options = {
            "capture_output": True, "text": True, "encoding": "utf-8",
            "errors": "replace", "check": False,
            "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
            "env": {**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        }
        try:
            status = subprocess.run([*command, "status", "--porcelain", "--", *paths], **options)
            if status.returncode != 0:
                return False
            if status.stdout.strip():
                return True
            ahead = subprocess.run([*command, "diff", "--quiet", "origin/main..HEAD", "--", *paths], **options)
            return ahead.returncode == 1
        except OSError:
            return False

    def bridge_interpreter(self) -> Path:
        interpreter = Path(sys.executable)
        if interpreter.name.lower() == "pythonw.exe":
            console_python = interpreter.with_name("python.exe")
            if console_python.is_file():
                return console_python
        return interpreter

    def bridge_environment(self) -> dict:
        env = os.environ.copy()
        env["HOKKIEN_GITHUB_REPO_PATH"] = str(self.repo_root)
        env["HOKKIEN_HANRI_DICT_PATH"] = str(self.local_tsv_path())
        # subprocess encoding controls only the parent; set the child's pipes too.
        env["PYTHONIOENCODING"] = "utf-8"
        return env

    def run_bridge(self, flag: str, payload: dict | None = None) -> dict:
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
        with self.bridge_lock:
            result = subprocess.run(
                [str(self.bridge_interpreter()), str(self.classic_script), flag],
                input=json.dumps(payload or {}, ensure_ascii=False),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(self.classic_script.parent),
                env=self.bridge_environment(),
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

    def start_html_bridge(self) -> None:
        with self.bridge_lock:
            if self.html_bridge_process is not None and self.html_bridge_process.poll() is None:
                return
            self.close_html_bridge()
            errors = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
            try:
                process = subprocess.Popen(
                    [str(self.bridge_interpreter()), str(self.classic_script), "--desktop-html-worker"],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors,
                    text=True, encoding="utf-8", errors="replace", bufsize=1,
                    cwd=str(self.classic_script.parent), env=self.bridge_environment(),
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
                )
            except Exception:
                errors.close()
                raise
            responses = queue.Queue()
            self.html_bridge_process = process
            self.html_bridge_responses = responses
            self.html_bridge_errors = errors

            def read_responses():
                try:
                    for line in process.stdout:
                        try:
                            response = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if isinstance(response, dict):
                            responses.put(response)
                finally:
                    responses.put(None)

            threading.Thread(target=read_responses, name="TangliengimHtmlBridge", daemon=True).start()

    def close_html_bridge(self) -> None:
        self.html_confirmation_id = None
        process = self.html_bridge_process
        self.html_bridge_process = None
        if process is not None:
            try:
                process.stdin.close()
            except OSError:
                pass
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            process.stdout.close()
        if self.html_bridge_errors is not None:
            self.html_bridge_errors.close()
            self.html_bridge_errors = None
        self.html_bridge_responses = None

    def server_close(self) -> None:
        try:
            self.close_html_bridge()
        finally:
            super().server_close()

    def run_html_bridge(self, payload: dict, *, confirmation_id: str | None = None) -> dict:
        with self.bridge_lock:
            self.start_html_bridge()
            if confirmation_id is not None:
                if confirmation_id != self.html_confirmation_id:
                    raise RuntimeError("This HTML confirmation has expired. Please copy again.")
                self.html_confirmation_id = None
            elif self.html_confirmation_id is not None:
                raise RuntimeError("Finish the open HTML confirmation before copying again.")
            try:
                self.html_bridge_process.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
                self.html_bridge_process.stdin.flush()
                response = self.html_bridge_responses.get(timeout=HTML_RESPONSE_TIMEOUT_SECONDS)
            except (OSError, queue.Empty) as exc:
                self.close_html_bridge()
                raise RuntimeError("HTML converter stopped or timed out") from exc
            if response is None:
                self.html_bridge_errors.seek(0)
                detail = self.html_bridge_errors.read().strip()
                self.close_html_bridge()
                raise RuntimeError(detail or "HTML converter exited without a response")
            if not response.get("ok"):
                raise RuntimeError(str(response.get("error") or "HTML conversion failed"))
            if response.get("confirmation"):
                self.html_confirmation_id = uuid.uuid4().hex
                response['confirmation']['id'] = self.html_confirmation_id
            return response

    def copy_html(self, payload: dict) -> dict:
        text = str(payload.get("text") or "")
        style = str(payload.get("style") or "plain")
        valid_styles = {"plain", "lomari_ruby_below", "lomari_next_line", "song", "novel", "novel_first", "title"}
        if not text.strip():
            raise ValueError("No text to copy")
        if style not in valid_styles:
            raise ValueError("Unknown HTML mode")
        response = self.run_html_bridge(payload)
        response["tsvPending"] = self.tsv_sync_pending()
        if not response.get('confirmation'):
            response['refreshJob'] = self.editor.refresh_if_changed()
        return response

    def confirm_html(self, payload: dict) -> dict:
        identity = payload.get('id')
        if not isinstance(identity, str) or not identity:
            raise ValueError('Missing HTML confirmation ID')
        response = self.run_html_bridge({'value': payload.get('value')}, confirmation_id=identity)
        response['tsvPending'] = self.tsv_sync_pending()
        if not response.get('confirmation'):
            response['refreshJob'] = self.editor.refresh_if_changed()
        return response

    def cancel_html(self, payload: dict) -> dict:
        with self.bridge_lock:
            if self.html_confirmation_id and payload.get('id') == self.html_confirmation_id:
                self.close_html_bridge()
        return {'ok': True}

    def sync_tsv(self) -> dict:
        return self.editor.dispatch('publish', {})

    def open_classic_tools(self) -> None:
        if self.classic_process is not None and self.classic_process.poll() is None:
            return
        interpreter = Path(sys.executable)
        pythonw = interpreter.with_name("pythonw.exe")
        if os.name == "nt" and pythonw.is_file():
            interpreter = pythonw
        env = os.environ.copy()
        env["HOKKIEN_IME_PYTHONW_LAUNCHED"] = "1"
        env["HOKKIEN_GITHUB_REPO_PATH"] = str(self.repo_root)
        env["HOKKIEN_HANRI_DICT_PATH"] = str(self.local_tsv_path())
        self.classic_process = subprocess.Popen(
            [str(interpreter), str(self.classic_script), "--classic-ui"],
            cwd=str(self.classic_script.parent),
            env=env,
            close_fds=True,
        )


def _fallback_browser_host(url: str, *, editor: bool = False) -> None:
    import tkinter as tk

    webbrowser.open_new(url)
    root = tk.Tk()
    root.title("Tangliengim Dictionary Editor" if editor else "Hokkien Tangliengim IME Pad")
    root.geometry("340x92")
    root.resizable(False, False)
    tk.Label(root, text="The dictionary editor is open in your browser." if editor else "The IME is open in your browser.", padx=18, pady=12).pack()
    tk.Button(root, text="Close editor" if editor else "Close IME", command=root.destroy).pack()
    root.mainloop()


def run_desktop_shell(repo_root: Path, classic_script: Path, *, editor: bool = False) -> None:
    repo_root = repo_root.resolve()
    required = [repo_root / "desktop/dictionary_editor_ui/index.html"] if editor else [
        repo_root / "apps" / "ime" / "index.html",
        repo_root / "shared" / "web-ime-core.js",
        repo_root / "public" / "data" / "hokkien-hanri-dict.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing shared web files: " + ", ".join(missing))

    server = DesktopHttpServer(repo_root, classic_script)
    if not editor:
        server.start_html_bridge()
    thread = threading.Thread(target=server.serve_forever, name="TangliengimDesktopServer", daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}" + ("/editor/" if editor else "/ime/?desktop=1")
    try:
        edge = find_edge()
        if edge is None:
            _fallback_browser_host(url, editor=editor)
            return
        profile = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Tangliengim" / ("DictionaryEditorProfile" if editor else "DesktopProfile")
        profile.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()
        process = subprocess.Popen(
            [
                str(edge),
                f"--app={url}",
                f"--user-data-dir={profile}",
                "--window-size=1200,860" if editor else "--window-size=920,800",
                "--no-first-run",
                "--disable-features=msEdgeFirstRunExperience",
            ],
            close_fds=True,
        )
        process.wait()
        if time.monotonic() - started < 2:
            _fallback_browser_host(url, editor=editor)
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
