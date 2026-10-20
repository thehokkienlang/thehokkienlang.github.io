"""Publish only reviewed dictionary data, preserving local work and remote edits."""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import redirect_stdout
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlsplit

from assign_dictionary_entry_ids import _atomic_write
from dictionary_editor_service import (
    DATA_FILES, MAIN, REGISTRY, CATEGORIES, DictionaryEditorService, EditorError,
    fingerprint, read_table, table_bytes,
)
from dictionary_schema import is_comment_record, next_entry_id
from sort_dictionary_tsv import sort_tsv
from validate_dictionary_tsv import validate
from node_runtime import node_environment

BASELINE = 'tests/fixtures/dictionary-baseline.json'

def git(repo, *arguments, timeout=120, check=True):
    env = os.environ.copy()
    # A desktop launcher must not accidentally target another inherited Git index.
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(key, None)
    env["GIT_TERMINAL_PROMPT"] = "0"
    result = subprocess.run(["git", "-C", str(repo), *arguments], capture_output=True,
                            env=env, encoding="utf-8", errors="replace", timeout=timeout,
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if check and result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise EditorError(detail or "Git operation failed.", code="git")
    return result


def revision_files(repo, ref):
    files = {}
    for name in DATA_FILES:
        result = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:data/{name}"], capture_output=True,
                                timeout=30, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if result.returncode == 0:
            files[name] = result.stdout
    if MAIN not in files or REGISTRY not in files:
        raise EditorError("The selected Git version does not contain the current dictionary and ID registry.")
    return files


def merge_sources(base, local, remote, resolutions=None):
    """Merge by stable identity and individual field, independently of row order."""
    resolutions = resolutions or {}
    local = dict(local)
    local_header, local_rows = read_table(local[MAIN])
    _, remote_rows = read_table(remote[MAIN])
    base_ids = {r["entry_id"] for r in read_table(base[REGISTRY])[1]}
    remote_reserved = {r["entry_id"] for r in read_table(remote[REGISTRY])[1]}
    remote_by_id = {r["entry_id"]: r for r in remote_rows if not is_comment_record(r)}
    reg_header, reg_rows = read_table(local[REGISTRY])
    reserved = {r["entry_id"] for raw in (local[REGISTRY], remote[REGISTRY]) for r in read_table(raw)[1]}
    remapped = {}
    for row in local_rows:
        identity = row.get("entry_id")
        other = remote_by_id.get(identity)
        if identity and identity not in base_ids and identity in remote_reserved and other != row:
            replacement = next_entry_id(row["hanri"], reserved)
            reserved.add(replacement)
            remapped[identity] = replacement
            row["entry_id"] = replacement
    if remapped:
        local[MAIN] = table_bytes(local_header, local_rows)
        for row in reg_rows:
            row["entry_id"] = remapped.get(row["entry_id"], row["entry_id"])
        local[REGISTRY] = table_bytes(reg_header, reg_rows)
        for name in (CATEGORIES, "dictionary_priority.tsv", "dictionary_redirects.tsv"):
            if name not in local:
                continue
            header, rows = read_table(local[name])
            for row in rows:
                for column in ("entry_id", "target_entry_id"):
                    if column in row:
                        row[column] = remapped.get(row[column], row[column])
            local[name] = table_bytes(header, rows)
    keys = {MAIN: ("entry_id",), REGISTRY: ("entry_id",), CATEGORIES: ("category", "entry_id"),
            "dictionary_priority.tsv": ("lookup_key", "entry_id"),
            "dictionary_redirects.tsv": ("kind", "source", "source_reading")}
    merged, conflicts = {}, []

    def choose(name, key, field, b, l, r):
        if l == r or r == b:
            return l
        if l == b:
            return r
        content = [name, key, field, b, l, r]
        token = hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        decision = resolutions.get(token)
        if decision in ("local", "remote"):
            return l if decision == "local" else r
        conflicts.append({"token": token, "file": name, "entry": key, "field": field,
                          "base": b, "local": l, "remote": r})
        return r

    for name in DATA_FILES:
        b_raw, l_raw, r_raw = (source.get(name) for source in (base, local, remote))
        if l_raw == r_raw or r_raw == b_raw:
            if l_raw is not None:
                merged[name] = l_raw
            continue
        if l_raw == b_raw:
            if r_raw is not None:
                merged[name] = r_raw
            continue
        existing = [raw for raw in (b_raw, l_raw, r_raw) if raw is not None]
        header = read_table(existing[0])[0]
        if any(read_table(raw)[0] != header for raw in existing):
            raise EditorError(f"{name}: GitHub uses a different schema. Update the application first.")
        tables = [read_table(raw)[1] if raw is not None else [] for raw in (b_raw, l_raw, r_raw)]
        maps = [{tuple(row[k] for k in keys[name]): row for row in rows if not is_comment_record(row)} for rows in tables]
        b_map, l_map, r_map = maps
        result = {}
        for key in dict.fromkeys([*r_map, *l_map, *b_map]):
            b, l, r = (mapping.get(key) for mapping in maps)
            if l is not None and r is not None:
                row = {column: choose(name, key, column, b.get(column) if b else None, l[column], r[column]) for column in header}
            else:
                row = choose(name, key, "entry", b, l, r)
            if row is not None:
                result[key] = row
        comments = [[row for row in rows if is_comment_record(row)] for rows in tables]
        chosen_comments = choose(name, "section comments", "comments", *comments)
        # Keep the chosen comment layout; sorting still owns only record slots.
        layout = tables[2] if chosen_comments == comments[2] else tables[1]
        output, seen = [], set()
        for row in layout:
            if is_comment_record(row):
                output.append(row)
                continue
            key = tuple(row[k] for k in keys[name])
            if key in result:
                output.append(result[key])
                seen.add(key)
        output.extend(row for key, row in result.items() if key not in seen)
        merged[name] = table_bytes(header, output)
    if conflicts:
        raise EditorError("Some fields changed differently locally and on GitHub. Choose which values to keep.",
                          code="conflict", details=conflicts)
    return merged, remapped


class DictionaryPublisher:
    def __init__(self, service: DictionaryEditorService, progress=None):
        self.service = service
        self.repo = service.repo
        self.progress = progress or (lambda message: None)

    def publish(self, resolutions=None):
        repo = self.repo
        self.progress("Checking local repository")
        try:
            _, release_env = node_environment()
        except FileNotFoundError as error:
            raise EditorError(str(error), code='dependency') from error
        if git(repo, "branch", "--show-current").stdout.strip() != "main":
            raise EditorError("Publish entries from the main checkout. Your saved entries are safe.")
        if git(repo, "diff", "--cached", "--name-only").stdout.strip():
            raise EditorError("There are staged changes in GitHub Desktop. Commit or unstage them before publishing entries.")
        self.progress("Fetching the latest GitHub version")
        git(repo, "fetch", "origin", "main")
        head = git(repo, "rev-parse", "HEAD").stdout.strip()
        target = git(repo, "rev-parse", "origin/main").stdout.strip()
        if git(repo, "merge-base", "--is-ancestor", head, target, check=False).returncode:
            raise EditorError("This checkout has unpublished commits. Publish those with GitHub Desktop first; saved dictionary entries are retained.")
        with self.service.locked():
            local = self.service.files()
        base = revision_files(repo, head)
        remote = revision_files(repo, target)
        merged, remapped = merge_sources(base, local, remote, resolutions)
        with tempfile.TemporaryDirectory(prefix="tangliengim-publish-") as folder:
            staging = Path(folder) / "checkout"
            self.progress("Preparing an isolated dictionary update")
            git(repo, "clone", "--local", "--no-hardlinks", "--single-branch", "--branch", "main", str(repo), str(staging), timeout=300)
            url = git(repo, "remote", "get-url", "origin").stdout.strip()
            git(staging, "remote", "set-url", "origin", url)
            git(staging, "fetch", "origin", "main")
            if git(staging, "rev-parse", "origin/main").stdout.strip() != target:
                raise EditorError("GitHub changed while preparing the update. Retry Publish; your entries are saved.", code="stale")
            git(staging, "checkout", "-B", "main", "origin/main")
            for setting in ("user.name", "user.email"):
                value = git(repo, "config", "--get", setting, check=False).stdout.strip()
                if value:
                    git(staging, "config", setting, value)
            log = self.service.state / "publish-checks.log"
            env = release_env.copy()
            env["HOKKIEN_GITHUB_REPO_PATH"] = str(staging)
            env["HOKKIEN_HANRI_DICT_PATH"] = str(staging / "data" / MAIN)
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUNBUFFERED"] = "1"
            interpreter = Path(sys.executable)
            # pythonw drops console streams in nested checks; keep the window hidden below.
            if interpreter.name.lower() == 'pythonw.exe':
                interpreter = interpreter.with_name('python.exe')
                if not interpreter.is_file():
                    raise EditorError('Publishing requires python.exe beside pythonw.exe. Repair the Python installation; local entries are saved.', code='dependency')
            with log.open("w", encoding="utf-8") as output:
                def check(*command):
                    result = subprocess.run(command, cwd=staging, env=env, stdout=output,
                                            stderr=subprocess.STDOUT, encoding='utf-8', timeout=1800,
                                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                    if result.returncode:
                        output.flush()
                        tail = '\n'.join(log.read_text(encoding='utf-8', errors='replace').splitlines()[-35:])
                        raise EditorError('Release checks failed. Local entries are saved.\n' + tail)

                # Prove the unchanged remote code/data matches its baseline before accepting data edits.
                self.progress('Verifying the existing dictionary baseline')
                check(str(interpreter), '-X', 'utf8', 'tools/build_dictionary_json.py')
                check(env['TANGLIENGIM_NODE'], 'tools/check_dictionary_baseline.cjs')
                for name, raw in merged.items():
                    (staging / 'data' / name).write_bytes(raw)
                with redirect_stdout(io.StringIO()):
                    errors = validate(staging / 'data' / MAIN)
                    if errors:
                        raise EditorError('\n'.join(errors))
                    sort_tsv(staging / 'data' / MAIN)
                merged = {name: (staging / 'data' / name).read_bytes() for name in merged}
                self.progress('Updating the dictionary snapshot for the saved entries')
                check(str(interpreter), '-X', 'utf8', 'tools/build_dictionary_json.py')
                check(env['TANGLIENGIM_NODE'], 'tools/check_dictionary_baseline.cjs', '--capture')
                self.progress('Running dictionary, build, and release checks')
                check(str(interpreter), '-X', 'utf8', 'tools/check_release.py')
            paths = ["data/" + name for name in DATA_FILES if name in merged]
            git(staging, "add", "--", *paths, BASELINE)
            changed = bool(git(staging, "diff", "--cached", "--name-only").stdout.strip())
            if changed:
                git(staging, "commit", "-m", "Update dictionary entries with Tangliengim Dictionary Editor")
            commit = git(staging, "rev-parse", "HEAD").stdout.strip()
            with self.service.locked():
                if fingerprint(self.service.files()) != fingerprint(local):
                    raise EditorError("New local entries were saved during validation. Retry Publish to include them.", code="stale")
                if git(repo, "rev-parse", "HEAD").stdout.strip() != head:
                    raise EditorError("The local branch changed during publishing. Retry Publish.", code="stale")
                if git(repo, "diff", "--cached", "--name-only").stdout.strip():
                    raise EditorError("Changes were staged during publishing. Unstage them before retrying.")
                if changed:
                    self.progress("Publishing validated dictionary entries")
                    git(staging, "push", "origin", "HEAD:main")
                git(repo, "fetch", "origin", "main")
                # Preserve data in a recoverable stash while fast-forwarding the checkout.
                dirty_data = git(repo, "status", "--porcelain", "--", *paths).stdout.strip()
                stash_id = None
                if dirty_data:
                    git(repo, "stash", "push", "-m", "Tangliengim editor pre-publish backup", "--", *paths)
                    stash_id = git(repo, "rev-parse", "refs/stash").stdout.strip()
                try:
                    git(repo, "merge", "--ff-only", "origin/main")
                except EditorError as error:
                    if stash_id:
                        restore = git(repo, "stash", "apply", "--index", stash_id, check=False)
                        recovery = f" Local data backup retained in stash {stash_id}."
                        if restore.returncode:
                            recovery += " Git reported conflicts restoring the checkout. Resolve these in GitHub Desktop."
                    else:
                        recovery = ""
                    raise EditorError("Published to GitHub, but the local checkout could not be updated: " + str(error) + recovery, code="published_local_pending")
                # A racing remote update may contain more than our commit. Never overwrite it.
                if git(repo, "rev-parse", "HEAD").stdout.strip() == commit:
                    self.service.commit_files(self.service.files(), merged)
                # Retain the stash as an explicit recovery copy; never auto-delete user work.
            state = {"commit": commit, "publishedAt": time.time(), "status": "published",
                     "remappedIds": remapped}
            _atomic_write(self.service.state / "publication.json", json.dumps(state).encode())
            self.progress("Published to GitHub; checking website deployment")
            return {"ok": True, **state, "message": "Published to GitHub. Website deployment is pending."}

    def deployment_status(self):
        state_path = self.service.state / "publication.json"
        if not state_path.exists():
            return {"status": "local", "message": "Saved locally"}
        state = json.loads(state_path.read_text(encoding="utf-8"))
        try:
            payload = None
            if shutil.which('gh'):
                result = subprocess.run(["gh", "api", "--method", "GET", "repos/{owner}/{repo}/actions/runs",
                                         "-f", "head_sha=" + state["commit"], "-f", "per_page=20"],
                                        cwd=self.repo, capture_output=True, encoding="utf-8", timeout=20,
                                        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                if result.returncode == 0:
                    payload = json.loads(result.stdout)
            if payload is None:
                remote = git(self.repo, 'remote', 'get-url', 'origin').stdout.strip()
                if remote.startswith('git@github.com:'):
                    slug = remote.removeprefix('git@github.com:')
                elif urlsplit(remote).hostname == 'github.com':
                    slug = urlsplit(remote).path.strip('/')
                else:
                    return {**state, "status": "published", "message": "Published; check deployment in GitHub Actions."}
                parts = slug.removesuffix('.git').split('/')
                if len(parts) != 2 or any(not part or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._' for c in part) for part in parts):
                    raise ValueError('Invalid GitHub repository name')
                request = Request('https://api.github.com/repos/' + '/'.join(parts) + '/actions/runs?head_sha=' + state['commit'] + '&per_page=20',
                                  headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'Tangliengim-Dictionary-Editor'})
                with urlopen(request, timeout=15) as response:
                    payload = json.load(response)
            runs = [run for run in payload.get("workflow_runs", [])
                    if run.get("head_branch") == "main" and ("pages" in run.get("path", "").lower())]
            if runs:
                run = runs[0]
                if run.get("conclusion") == "success":
                    return {**state, "status": "deployed", "message": "Website updated", "url": run.get("html_url")}
                if run.get("status") == "completed":
                    return {**state, "status": "deployment_failed", "message": "Published, but website deployment failed.", "url": run.get("html_url")}
        except (OSError, ValueError, subprocess.SubprocessError, EditorError):
            pass
        return {**state, "message": "Published to GitHub; website deployment is not yet confirmed."}
