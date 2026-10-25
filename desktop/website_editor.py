"""Controller and launcher for the private Tangliengim website editor."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import uuid
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from website_editor_service import WebsiteEditorError, WebsiteEditorService


class WebsiteEditorController:
    def __init__(self, server):
        self.server = server
        self.service = WebsiteEditorService(server.repo_root)
        self.lock = threading.RLock()
        self.jobs = {}
        self.active_job = None
        self.last_validation = None

    def start_job(self, kind, operation):
        with self.lock:
            if self.active_job:
                raise WebsiteEditorError("Another website-editor operation is running. Please wait.", code="busy")
            identity = uuid.uuid4().hex
            job = {"id": identity, "kind": kind, "status": "running", "message": "Starting...", "log": ""}
            self.jobs[identity] = job
            self.active_job = identity

        def progress(message, line=None):
            with self.lock:
                job["message"] = message
                if line:
                    job["log"] = (job["log"] + line + "\n")[-120_000:]

        def worker():
            try:
                result = operation(progress)
                with self.lock:
                    job.update(status="done", result=result, message=result.get("message", "Complete"))
            except Exception as error:
                with self.lock:
                    job.update(status="failed", message=str(error), code=getattr(error, "code", "error"),
                               details=getattr(error, "details", None))
            finally:
                with self.lock:
                    self.active_job = None
                    while len(self.jobs) > 20:
                        self.jobs.pop(next(iter(self.jobs)))
        threading.Thread(target=worker, name="TangliengimWebsiteEditorJob", daemon=True).start()
        return {"ok": True, "job": identity}

    def validate(self, kind, progress):
        command = self.service.validation_command(kind)
        labels = {"dictionary": "Validating dictionary data", "source": "Running source release checks",
                  "site": "Building and validating the complete website"}
        progress(labels[kind])
        env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
        process = subprocess.Popen(
            command, cwd=self.service.repo, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            encoding="utf-8", errors="replace", bufsize=1,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        for line in process.stdout:
            clean = line.rstrip()
            if clean:
                progress(clean, clean)
        code = process.wait()
        process.stdout.close()
        if code:
            raise WebsiteEditorError(f"Validation failed with exit code {code}. Review the log below.", code="validation")
        fingerprint = self.service.working_fingerprint()
        with self.lock:
            self.last_validation = {"kind": kind, "fingerprint": fingerprint}
        return {"ok": True, "kind": kind, "fingerprint": fingerprint,
                "message": "Validation passed. The current files are ready for review and commit."}

    def dispatch(self, action, payload):
        if action == "summary":
            with self.lock:
                validation = self.last_validation
            return {**self.service.summary(), "validation": validation, "activeJob": self.active_job}
        if action == "pages":
            return {"ok": True, "pages": self.service.pages()}
        if action == "page":
            return self.service.page(payload.get("file"))
        if action == "validate-page":
            title, body = self.service.validate_page_fields(payload.get("title"), payload.get("body"))
            return {"ok": True, "title": title, "body": body, "message": "Draft fields are valid and ready to preview."}
        if action == "save-page":
            return self.service.save_page(payload.get("file"), payload.get("revision"),
                                          payload.get("title"), payload.get("body"))
        if action == "tables":
            return self.service.table_snapshot()
        if action == "save-categories":
            return self.service.save_categories(payload.get("revision"), payload.get("labels"), payload.get("memberships"))
        if action == "save-priorities":
            return self.service.save_priorities(payload.get("revision"), payload.get("rows"))
        if action == "save-references":
            return self.service.save_references(payload.get("revision"), payload.get("rows"))
        if action == "changes":
            return self.service.changes()
        if action == "validate":
            return self.start_job("validate", lambda progress: self.validate(payload.get("kind", "site"), progress))
        if action == "commit":
            with self.lock:
                validation = self.last_validation
            if not validation:
                raise WebsiteEditorError("Run Validation before committing.")
            return self.service.commit(payload.get("message"), payload.get("paths"), validation["fingerprint"])
        if action == "push":
            return self.start_job("push", lambda progress: self._push(progress))
        if action == "job":
            with self.lock:
                job = self.jobs.get(payload.get("id"))
                if not job:
                    raise WebsiteEditorError("This background operation has expired. Reload the editor.")
                return {"ok": True, **job}
        raise WebsiteEditorError("Unknown website-editor operation.")

    def _push(self, progress):
        progress("Pushing the current branch to GitHub")
        return self.service.push()


def main():
    from tangliengim_web_shell import DesktopHttpServer
    parser = argparse.ArgumentParser(description="Tangliengim local website editor")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    server = DesktopHttpServer(repo, repo / "desktop/Hokkien Tangliengim IME Pad.py")
    url = f"http://127.0.0.1:{server.server_port}/website-editor/"
    print("Tangliengim Website Editor: " + url, flush=True)
    if not args.no_browser:
        threading.Timer(.35, lambda: webbrowser.open_new(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
