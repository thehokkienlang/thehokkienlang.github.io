"""Local-only content, reference, validation, and Git services for the website CMS."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

from assign_dictionary_entry_ids import _atomic_write
from dictionary_editor_service import EditorError, MAIN, read_table, table_bytes
from dictionary_ranking import PRIORITY_COLUMNS, load_priority, read_records
from dictionary_references import CATEGORY_COLUMNS, load_categories

REDIRECT_COLUMNS = ("kind", "source", "source_reading", "target_entry_id", "reason", "sources", "date")
GENERATED_PREFIXES = ("_site/", "public/data/")
CONTENT_ROOT = "content"


class WebsiteEditorError(EditorError):
    def __init__(self, message, *, code="validation", details=None):
        super().__init__(message, code=code, details=details)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(repo: Path, *arguments: str, timeout=180, check=True) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(key, None)
    env["GIT_TERMINAL_PROMPT"] = "0"
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments], cwd=repo, env=env,
        stdin=subprocess.DEVNULL, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if check and result.returncode:
        raise WebsiteEditorError((result.stderr or result.stdout).strip() or "Git operation failed.", code="git")
    return result


class WebsiteEditorService:
    def __init__(self, repo: Path):
        self.repo = Path(repo).resolve()
        self.content = self.repo / CONTENT_ROOT
        self.data = self.repo / "data"

    def _inside(self, root: Path, relative: str, *, suffix=None) -> Path:
        if not isinstance(relative, str) or not relative or "\0" in relative:
            raise WebsiteEditorError("Invalid repository path.")
        rel = Path(relative.replace("\\", "/"))
        if rel.is_absolute() or ".." in rel.parts:
            raise WebsiteEditorError("The editor may only access repository source files.", code="forbidden")
        target = (self.repo / rel).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as error:
            raise WebsiteEditorError("The editor may only access approved source files.", code="forbidden") from error
        if suffix and target.suffix.lower() != suffix:
            raise WebsiteEditorError("Unsupported source-file type.")
        return target

    def page_path(self, relative: str) -> Path:
        target = self._inside(self.content, relative, suffix=".json")
        if target.name == "song-categories.json":
            raise WebsiteEditorError("Song categories use their structured editor.", code="forbidden")
        return target

    @staticmethod
    def _load_json(path: Path) -> tuple[bytes, dict]:
        raw = path.read_bytes()
        try:
            record = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise WebsiteEditorError(f"{path.name} is not valid UTF-8 JSON: {error}") from error
        if not isinstance(record, dict):
            raise WebsiteEditorError(f"{path.name} must contain one JSON object.")
        return raw, record

    def pages(self) -> list[dict]:
        pages = []
        for path in sorted(self.content.rglob("*.json")):
            if path.name == "song-categories.json":
                continue
            try:
                raw, record = self._load_json(path)
            except WebsiteEditorError:
                continue
            relative = path.relative_to(self.repo).as_posix()
            pages.append({
                "file": relative, "revision": digest(raw), "id": record.get("id", path.stem),
                "title": record.get("title", path.stem), "route": record.get("route", ""),
                "type": record.get("type", path.parent.name), "language": record.get("language", "en"),
                "archived": bool(record.get("archived")),
            })
        return pages

    def page(self, relative: str) -> dict:
        path = self.page_path(relative)
        if not path.is_file():
            raise WebsiteEditorError("This page no longer exists. Reload the page list.", code="stale")
        raw, record = self._load_json(path)
        return {"ok": True, "file": path.relative_to(self.repo).as_posix(), "revision": digest(raw), "page": record}

    @staticmethod
    def validate_page_fields(title, body):
        if not isinstance(title, str) or not title.strip():
            raise WebsiteEditorError("Page title is required.")
        if not isinstance(body, str):
            raise WebsiteEditorError("Page content must be text.")
        if any(char in title for char in "\t\r\n\0") or "\0" in body:
            raise WebsiteEditorError("Remove control characters from the page fields.")
        if len(body.encode("utf-8")) > 2_000_000:
            raise WebsiteEditorError("This page is too large for the local editor.")
        return unicodedata.normalize("NFC", title.strip()), unicodedata.normalize("NFC", body)

    def save_page(self, relative: str, revision: str, title: str, body: str) -> dict:
        path = self.page_path(relative)
        raw, record = self._load_json(path)
        if revision != digest(raw):
            raise WebsiteEditorError(
                "This page changed outside the editor. Reload it before saving; your draft is still in the form.",
                code="stale",
            )
        title, body = self.validate_page_fields(title, body)
        record["title"] = title
        record["body"] = body
        output = (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        if output != raw:
            _atomic_write(path, output)
        return {"ok": True, "revision": digest(output), "message": f"Saved {title} locally.", "page": record}

    def entries(self) -> tuple[list[dict], dict[str, dict]]:
        records = read_records(self.data / MAIN)
        compact = [{"entry_id": row["entry_id"], "hanri": row["hanri"],
                    "reading": row["corrected"] or row["reading"], "english": row["english"]}
                   for row in records]
        return compact, {row["entry_id"]: row for row in records}

    def table_snapshot(self) -> dict:
        entries, by_id = self.entries()
        categories_path = self.data / "dictionary_categories.tsv"
        category_raw = categories_path.read_bytes()
        category_header, category_rows = read_table(category_raw)
        labels, memberships = load_categories(categories_path, list(by_id.values()))
        priorities_path = self.data / "dictionary_priority.tsv"
        priority_raw = priorities_path.read_bytes()
        priority_header, priorities = read_table(priority_raw)
        load_priority(priorities_path, list(by_id.values()))
        redirects_path = self.data / "dictionary_redirects.tsv"
        redirect_raw = redirects_path.read_bytes()
        redirect_header, redirects = read_table(redirect_raw)
        return {
            "ok": True, "entries": entries,
            "categories": {
                "revision": digest(category_raw),
                "labels": [{"category": key, "label": value,
                            "count": sum(key in values for values in memberships.values())}
                           for key, value in labels.items()],
                "memberships": [{**row, "reading": by_id[row["entry_id"]]["corrected"] or by_id[row["entry_id"]]["reading"]}
                                for row in category_rows],
                "columns": category_header,
            },
            "priorities": {"revision": digest(priority_raw), "rows": priorities, "columns": priority_header},
            "references": {"revision": digest(redirect_raw), "rows": redirects, "columns": redirect_header},
        }

    @staticmethod
    def _plain(value, field, *, required=False):
        if not isinstance(value, str) or any(char in value for char in "\t\r\n\0"):
            raise WebsiteEditorError(f"{field}: use plain text without tabs or line breaks.")
        value = unicodedata.normalize("NFC", value.strip())
        if required and not value:
            raise WebsiteEditorError(f"{field} is required.")
        return value

    def _replace_table(self, name: str, revision: str, columns, rows: list[dict], validate):
        path = self.data / name
        before = path.read_bytes()
        if revision != digest(before):
            raise WebsiteEditorError(
                f"{name} changed outside the editor. Reload before saving; your edits remain on screen.", code="stale")
        output = table_bytes(columns, rows)
        with tempfile.TemporaryDirectory(prefix="tli-cms-") as folder:
            candidate = Path(folder) / name
            candidate.write_bytes(output)
            validate(candidate)
        if output != before:
            _atomic_write(path, output)
        return {"ok": True, "revision": digest(output), "message": f"Saved {name} locally."}

    def save_categories(self, revision: str, labels, memberships) -> dict:
        entries, by_id = self.entries()
        if not isinstance(labels, list) or not isinstance(memberships, list):
            raise WebsiteEditorError("Category data must be a list.")
        label_map = {}
        for row in labels:
            key = self._plain(row.get("category"), "Category key", required=True)
            label = self._plain(row.get("label"), "Category label", required=True)
            if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", key):
                raise WebsiteEditorError("Category keys use lowercase letters, numbers, hyphens, and underscores.")
            if key in label_map and label_map[key] != label:
                raise WebsiteEditorError(f"Conflicting labels for category {key}.")
            label_map[key] = label
        seen, rows = set(), []
        used_categories = set()
        for member in memberships:
            key = self._plain(member.get("category"), "Category", required=True)
            identity = self._plain(member.get("entry_id"), "Entry ID", required=True)
            if key not in label_map or identity not in by_id:
                raise WebsiteEditorError("A category membership refers to a missing category or entry.")
            if (key, identity) in seen:
                continue
            seen.add((key, identity))
            used_categories.add(key)
            rows.append({"category": key, "label": label_map[key],
                         "entry": by_id[identity]["hanri"], "entry_id": identity})
        unused = sorted(set(label_map) - used_categories)
        if unused:
            raise WebsiteEditorError(
                "Each category needs at least one entry before it can be saved: " + ", ".join(unused))
        rows.sort(key=lambda row: (row["category"], row["entry_id"]))
        return self._replace_table("dictionary_categories.tsv", revision, CATEGORY_COLUMNS, rows,
                                   lambda path: load_categories(path, list(by_id.values())))

    def save_priorities(self, revision: str, rows) -> dict:
        entries, by_id = self.entries()
        if not isinstance(rows, list):
            raise WebsiteEditorError("Priority data must be a list.")
        output = []
        for row in rows:
            identity = self._plain(row.get("entry_id"), "Entry ID", required=True)
            if identity not in by_id:
                raise WebsiteEditorError(f"Unknown active entry: {identity}")
            rank = str(row.get("rank", "")).strip()
            if not rank.isascii() or not rank.isdigit() or int(rank) < 1:
                raise WebsiteEditorError("Static priority rank must be a positive integer.")
            output.append({"lookup_key": self._plain(row.get("lookup_key"), "Lookup key", required=True),
                           "entry": by_id[identity]["hanri"], "entry_id": identity, "rank": rank})
        output.sort(key=lambda row: (row["lookup_key"], int(row["rank"]), row["entry_id"]))
        return self._replace_table("dictionary_priority.tsv", revision, PRIORITY_COLUMNS, output,
                                   lambda path: load_priority(path, list(by_id.values())))

    def save_references(self, revision: str, rows) -> dict:
        _, by_id = self.entries()
        if not isinstance(rows, list):
            raise WebsiteEditorError("Reference data must be a list.")
        output = []
        for row in rows:
            normalized = {column: self._plain(row.get(column), column, required=column in {"kind", "source", "target_entry_id"})
                          for column in REDIRECT_COLUMNS}
            if normalized["kind"] not in {"headword", "reading"}:
                raise WebsiteEditorError("Reference kind must be headword or reading.")
            if normalized["target_entry_id"] not in by_id:
                raise WebsiteEditorError(f"Unknown active target entry: {normalized['target_entry_id']}")
            output.append(normalized)
        return self._replace_table("dictionary_redirects.tsv", revision, REDIRECT_COLUMNS, output,
                                   lambda path: self._validate_references(path, by_id))

    @staticmethod
    def _validate_references(path: Path, by_id: dict):
        header, rows = read_table(path.read_bytes())
        if tuple(header) != REDIRECT_COLUMNS:
            raise WebsiteEditorError("Reference table has the wrong columns.")
        seen = set()
        for row in rows:
            key = (row["kind"], row["source"], row["source_reading"])
            if key in seen:
                raise WebsiteEditorError("Duplicate dictionary reference: " + " / ".join(key))
            seen.add(key)
            if row["target_entry_id"] not in by_id:
                raise WebsiteEditorError("Reference points to an inactive entry.")

    def _status_records(self):
        raw = git(self.repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout
        tokens = raw.split("\0")
        records, index = [], 0
        while index < len(tokens) and tokens[index]:
            token = tokens[index]
            status, path = token[:2], token[3:]
            index += 1
            if status[0] in "RC" and index < len(tokens) and tokens[index]:
                old = tokens[index]
                index += 1
            else:
                old = ""
            records.append((status, path.replace("\\", "/"), old.replace("\\", "/")))
        return records

    def changes(self) -> dict:
        files = []
        for status, relative, old in self._status_records():
            target = self._inside(self.repo, relative)
            generated = relative.startswith(GENERATED_PREFIXES)
            if status == "??":
                if target.is_file() and target.stat().st_size <= 250_000:
                    content = target.read_text(encoding="utf-8", errors="replace")
                    patch = f"--- /dev/null\n+++ b/{relative}\n" + "\n".join("+" + line for line in content.splitlines())
                else:
                    patch = "Untracked binary or large file."
            else:
                patch = git(self.repo, "diff", "--no-ext-diff", "--unified=3", "HEAD", "--", relative,
                            check=False).stdout
            files.append({"status": status, "path": relative, "oldPath": old, "generated": generated,
                          "diff": patch[-300_000:]})
        branch = git(self.repo, "status", "--short", "--branch").stdout.splitlines()
        return {"ok": True, "files": files, "branch": branch[0] if branch else "",
                "fingerprint": self.working_fingerprint()}

    def working_fingerprint(self) -> str:
        state = hashlib.sha256()
        for status, relative, old in self._status_records():
            state.update(f"{status}\0{relative}\0{old}\0".encode("utf-8"))
            target = self._inside(self.repo, relative)
            if target.is_file():
                state.update(hashlib.sha256(target.read_bytes()).digest())
        return state.hexdigest()

    def summary(self) -> dict:
        pages = self.pages()
        entries, _ = self.entries()
        changes = self.changes()
        return {"ok": True, "pages": len(pages), "songs": sum(page["type"] == "songs" for page in pages),
                "entries": len(entries), "changes": len(changes["files"]), "branch": changes["branch"],
                "generatedProtected": list(GENERATED_PREFIXES)}

    def commit(self, message: str, paths: list[str], validated_fingerprint: str) -> dict:
        message = self._plain(message, "Commit message", required=True)
        current = self.changes()
        if validated_fingerprint != current["fingerprint"]:
            raise WebsiteEditorError("Files changed since validation. Validate the current changes before committing.", code="stale")
        allowed = {item["path"] for item in current["files"]}
        if not isinstance(paths, list) or not paths:
            raise WebsiteEditorError("Select at least one reviewed file to commit.")
        selected = []
        for relative in paths:
            self._inside(self.repo, relative)
            if relative not in allowed:
                raise WebsiteEditorError(f"{relative} is no longer an uncommitted change. Reload Changes.", code="stale")
            selected.append(relative)
        staged = {path for path in git(self.repo, "diff", "--cached", "--name-only", "-z").stdout.split("\0") if path}
        unrelated = sorted(staged - set(selected))
        if unrelated:
            raise WebsiteEditorError(
                "Git already has staged files that are not selected here. Commit or unstage them first: "
                + ", ".join(unrelated), code="git")
        git(self.repo, "add", "--", *selected)
        if not git(self.repo, "diff", "--cached", "--quiet", check=False).returncode:
            raise WebsiteEditorError("The selected files have no commit-ready changes.")
        git(self.repo, "commit", "-m", message, timeout=300)
        commit = git(self.repo, "rev-parse", "HEAD").stdout.strip()
        return {"ok": True, "commit": commit, "message": f"Committed {len(selected)} reviewed files locally."}

    def push(self) -> dict:
        branch = git(self.repo, "branch", "--show-current").stdout.strip()
        if not branch:
            raise WebsiteEditorError("The repository is not on a branch. Open it in GitHub Desktop first.", code="git")
        git(self.repo, "push", "origin", branch, timeout=300)
        commit = git(self.repo, "rev-parse", "HEAD").stdout.strip()
        return {"ok": True, "commit": commit, "message": f"Pushed {branch} to GitHub using existing Git authentication."}

    def validation_command(self, kind: str) -> list[str]:
        python = str(Path(sys.executable).with_name("python.exe") if Path(sys.executable).name.lower() == "pythonw.exe" else sys.executable)
        commands = {
            "dictionary": [python, "-X", "utf8", "tools/validate_dictionary_tsv.py"],
            "site": [python, "-X", "utf8", "tools/check_release.py"],
            "source": [python, "-X", "utf8", "tools/check_release.py", "--source-only"],
        }
        if kind not in commands:
            raise WebsiteEditorError("Unknown validation suite.")
        return commands[kind]
