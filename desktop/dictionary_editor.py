"""Local editor controller and background jobs for the shared desktop server."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import threading
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from dictionary_editor_service import DictionaryEditorService, EditorError, DATA_FILES, MAIN, REGISTRY, CATEGORIES, fingerprint
from dictionary_editor_publish import DictionaryPublisher


class DictionaryEditorController:
    def __init__(self, server):
        self.server = server
        self.service = DictionaryEditorService(server.repo_root)
        self.lock = threading.RLock()
        self.jobs = {}
        self.active_job = None
        self.preview_module = None
        self.generation = 0
        self.source_signature = self.signature()

    def signature(self):
        from dictionary_editor_service import DATA_FILES
        return tuple((name, path.stat().st_mtime_ns, path.stat().st_size)
                     for name in DATA_FILES if (path := self.service.data / name).exists())

    def refresh_if_changed(self):
        if self.signature() == self.source_signature:
            return None
        with self.lock:
            if self.active_job:
                return self.active_job
            return self.start_job("refresh", self.refresh_runtime)["job"]

    def start_job(self, kind, operation):
        with self.lock:
            if self.server.restarting:
                raise EditorError("Restart in progress. Your form is retained.", code="busy")
            if self.active_job:
                raise EditorError("Another dictionary operation is running. Please wait.", code="busy")
            identity = uuid.uuid4().hex
            job = {"id": identity, "kind": kind, "status": "running", "message": "Starting..."}
            self.jobs[identity] = job
            self.active_job = identity

        def progress(message):
            with self.lock:
                job["message"] = message

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
        threading.Thread(target=worker, name="TangliengimDictionaryJob", daemon=False).start()
        return {"ok": True, "job": identity}

    def refresh_runtime(self, progress):
        while True:
            progress("Saved locally; refreshing IME candidates")
            with self.service.locked():
                snapshot = self.service.files()
                source = self.service.state / 'runtime-source' / 'data'
                source.mkdir(parents=True, exist_ok=True)
                for name, raw in snapshot.items():
                    (source / name).write_bytes(raw)
                # Do not leave a removed optional file from an earlier snapshot.
                for name in DATA_FILES:
                    if name not in snapshot:
                        (source / name).unlink(missing_ok=True)
                output = self.service.state / "runtime.json"
            interpreter = str(self.server.bridge_interpreter())
            env = self.server.bridge_environment()
            env['HOKKIEN_HANRI_DICT_PATH'] = str(source / MAIN)
            result = subprocess.run([interpreter, "-X", "utf8", "tools/build_dictionary_json.py",
                                     "--input", str(source / MAIN), "--categories", str(source / CATEGORIES),
                                     "--registry", str(source / REGISTRY), "--output", str(output)],
                                    cwd=self.service.repo, env=env,
                                    stdin=subprocess.DEVNULL, capture_output=True, encoding="utf-8", errors="replace", timeout=60,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if result.returncode:
                raise EditorError("Entries were saved, but the IME refresh failed: " + (result.stderr or result.stdout)[-4000:])
            payload = json.loads(output.read_text(encoding='utf-8'))
            for field, name in (('source', MAIN), ('idRegistrySource', REGISTRY), ('categorySource', CATEGORIES), ('prioritySource', 'dictionary_priority.tsv')):
                payload[field] = 'data/' + name
            output.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
            with self.service.locked():
                if fingerprint(self.service.files()) != fingerprint(snapshot):
                    continue
                os.replace(output, self.service.repo / "public" / "data" / "hokkien-hanri-dict.json")
                self.generation += 1
                self.source_signature = self.signature()
                break
        # The export service caches the TSV; restart lazily after a source change.
        with self.server.bridge_lock:
            if self.server.html_confirmation_id is None:
                self.server.close_html_bridge()
        return {"ok": True, "message": "Saved locally; IME candidates refreshed.", "generation": self.generation}

    def dispatch(self, action, payload):
        if action == "restart":
            return self.server.restart_desktop()
        if action == 'open':
            return self.server.open_dictionary_editor(payload.get('job'))
        if action == "snapshot":
            return {**self.service.snapshot(), "activeJob": self.active_job, "generation": self.generation,
                    "tsvPending": self.server.local_entries_pending(),
                    "hasPublication": (self.service.state / 'publication.json').exists()}
        if action == "job":
            with self.lock:
                job = self.jobs.get(payload.get("id"))
                if job is None:
                    raise EditorError("Operation expired. Reload the editor.")
                return {"ok": True, **job}
        if action == "import":
            return {"ok": True, "entries": self.service.import_rows(payload.get("text"))}
        if action == "simplify":
            return {"ok": True, **self.service.simplified_fields(payload)}
        if action == "preview":
            entry = payload.get('entry', {})
            record = self.service.normalize(entry, previous=self.service.existing_entry(entry.get('entry_id')) if isinstance(entry, dict) else None)
            with self.lock:
                if self.preview_module is None:
                    script = self.service.repo / "desktop" / "hokkien_tone_marker_gui.py"
                    spec = importlib.util.spec_from_file_location("dictionary_editor_tone_preview", script)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[spec.name] = module
                    spec.loader.exec_module(module)
                    self.preview_module = module
                roman = self.preview_module.auto_lomari_from_hangul(record["corrected"] or record["reading"])
            # The real pronunciation engine determines unit/tone boundaries.
            from build_dictionary_json import load_ime_module, audio_for_reading
            with self.lock:
                if not hasattr(self, "preview_ime"):
                    self.preview_ime = load_ime_module()
                playback = audio_for_reading(self.preview_ime, self.service.repo / "public/audio", record["corrected"] or record["reading"])
            return {"ok": True, "entry": record, "lomari": roman, "audio": playback}
        if action in ("save", "retire"):
            with self.lock:
                if self.server.restarting:
                    raise EditorError("Restart in progress. Your form is retained.", code="busy")
                if self.active_job and self.jobs[self.active_job]['kind'] != 'refresh':
                    raise EditorError("A dictionary operation is running. Your form is retained.", code="busy")
                if action == "retire":
                    result = self.service.make_defunct(payload.get('entry_id'), revision=payload.get('revision'))
                else:
                    result = self.service.save(payload.get("entries"), revision=payload.get("revision"),
                                               allow_alternative=payload.get("allowAlternative") is True)
                job = {"job": self.active_job} if self.active_job else self.start_job("refresh", self.refresh_runtime)
            return {**result, "job": job["job"]}
        if action == "refresh":
            return self.start_job("refresh", self.refresh_runtime)
        if action == "publish":
            def publish(progress):
                result = DictionaryPublisher(self.service, progress).publish(payload.get("resolutions"))
                self.refresh_runtime(progress)
                return result
            with self.lock:
                if self.server.restarting:
                    raise EditorError("Restart in progress. Your form is retained.", code="busy")
                if self.active_job:
                    raise EditorError("Another dictionary operation is running. Your form is retained.", code="busy")
                saved = {}
                if payload.get('entries') is not None:
                    saved = self.service.save(payload['entries'], revision=payload.get('revision'),
                                              allow_alternative=payload.get('allowAlternative') is True)
                return {**saved, **self.start_job("publish", publish)}
        if action == "deployment":
            return {"ok": True, **DictionaryPublisher(self.service).deployment_status()}
        raise EditorError("Unknown dictionary operation.")


def main():
    import argparse
    from tangliengim_web_shell import DesktopHttpServer, run_desktop_shell
    parser = argparse.ArgumentParser(description="Tangliengim Dictionary Editor")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    if not args.no_browser:
        run_desktop_shell(repo, repo / "desktop/Hokkien Tangliengim IME Pad.py", editor=True)
        return
    server = DesktopHttpServer(repo, repo / "desktop/Hokkien Tangliengim IME Pad.py")
    url = f"http://127.0.0.1:{server.server_port}/editor/"
    print("Tangliengim Dictionary Editor: " + url, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
