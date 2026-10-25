"""Safety and source contracts for the private localhost website editor."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from website_editor_service import WebsiteEditorError, WebsiteEditorService


class WebsiteEditorTests(unittest.TestCase):
    def fixture(self, folder):
        repo = Path(folder)
        page = repo / "content/pages/sample.json"
        page.parent.mkdir(parents=True)
        page.write_text(json.dumps({"id":"sample", "type":"pages", "language":"en", "title":"Sample",
                                    "route":"/sample/", "body":"<p>Before</p>"}, indent=2) + "\n", encoding="utf-8")
        (repo / "notes.txt").write_text("Before\n", encoding="utf-8")
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Editor Test"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "editor@example.invalid"], cwd=repo, check=True)
        subprocess.run(["git", "add", "content/pages/sample.json", "notes.txt"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=repo, check=True, capture_output=True)
        return WebsiteEditorService(repo), page

    def test_page_save_is_local_and_stale_safe(self):
        with tempfile.TemporaryDirectory() as folder:
            service, path = self.fixture(folder)
            opened = service.page("content/pages/sample.json")
            saved = service.save_page(opened["file"], opened["revision"], "Edited", "<p>After</p>")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["body"], "<p>After</p>")
            self.assertTrue(service.changes()["files"])
            with self.assertRaisesRegex(WebsiteEditorError, "changed outside"):
                service.save_page(opened["file"], opened["revision"], "Old draft", "<p>Unsafe</p>")
            self.assertEqual(saved["message"], "Saved Edited locally.")

    def test_page_paths_cannot_escape_content_or_edit_generated_files(self):
        with tempfile.TemporaryDirectory() as folder:
            service, _ = self.fixture(folder)
            for relative in ("../outside.json", "_site/index.json", "public/data/data.json", "content/song-categories.json"):
                with self.subTest(relative=relative), self.assertRaises(WebsiteEditorError):
                    service.page_path(relative)

    def test_commit_rejects_unselected_files_staged_outside_editor(self):
        with tempfile.TemporaryDirectory() as folder:
            service, page = self.fixture(folder)
            page.write_text(page.read_text(encoding="utf-8").replace("Before", "After"), encoding="utf-8")
            notes = Path(folder) / "notes.txt"
            notes.write_text("Changed elsewhere\n", encoding="utf-8")
            subprocess.run(["git", "add", "notes.txt"], cwd=folder, check=True)
            fingerprint = service.changes()["fingerprint"]
            with self.assertRaisesRegex(WebsiteEditorError, "staged files"):
                service.commit("Page only", ["content/pages/sample.json"], fingerprint)

    def test_real_structured_tables_resolve_to_human_entries(self):
        snapshot = WebsiteEditorService(ROOT).table_snapshot()
        self.assertGreater(len(snapshot["entries"]), 1000)
        active = {entry["entry_id"] for entry in snapshot["entries"]}
        self.assertTrue(all(row["entry_id"] in active for row in snapshot["categories"]["memberships"]))
        self.assertTrue(all(row["entry_id"] in active for row in snapshot["priorities"]["rows"]))
        self.assertTrue(all(row["target_entry_id"] in active for row in snapshot["references"]["rows"]))


if __name__ == "__main__":
    unittest.main()
