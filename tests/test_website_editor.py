"""Safety and source contracts for the private localhost website editor."""
from __future__ import annotations

import json
import shutil
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

    def test_song_renderer_generates_grey_parentheses_ruby_and_lomari(self):
        service = WebsiteEditorService(ROOT)
        result = service.render_song_draft({
            "title": "릐호", "titleSource": "릐호",
            "videoUrl": "https://youtu.be/HNYkSBkQ33Y", "category": "modern",
            "lyrics": [{"kind": "line", "text": "릐호", "grey": True}],
        })
        self.assertEqual(result["route"], "/songs/릐호/")
        self.assertIn('font-size: 1em;color:gray', result["body"])
        self.assertIn("(li", result["body"])
        self.assertIn("호)", result["body"])
        self.assertIn("youtube.com/embed/HNYkSBkQ33Y", result["body"])

    def test_structured_song_save_updates_all_canonical_registries(self):
        with tempfile.TemporaryDirectory() as folder:
            initial, _ = self.fixture(folder)
            repo = initial.repo
            (repo / "desktop").mkdir()
            (repo / "data").mkdir()
            (repo / "content/songs").mkdir(parents=True)
            (repo / "migration").mkdir()
            shutil.copy2(ROOT / "desktop/hokkien_tone_marker_gui.py", repo / "desktop/hokkien_tone_marker_gui.py")
            shutil.copy2(ROOT / "data/hokkien_hanri_dict.tsv", repo / "data/hokkien_hanri_dict.tsv")
            (repo / "content/song-categories.json").write_text(json.dumps([{
                "id": "modern", "labels": {"en": "Modern"}, "routes": [],
            }]), encoding="utf-8")
            (repo / "migration/song-urls.json").write_text("[]\n", encoding="utf-8")
            (repo / "migration/wordpress-map.json").write_text(json.dumps({"records": []}), encoding="utf-8")
            service = WebsiteEditorService(repo)
            snapshot = service.song_editor_snapshot()
            saved = service.save_song("", "", snapshot["categoryRevision"], snapshot["urlRevision"],
                                      snapshot["manifestRevision"], {
                "title": "릐호", "titleSource": "릐호", "videoUrl": "HNYkSBkQ33Y", "category": "modern",
                "lyrics": [{"kind": "line", "text": "릐호", "grey": False}],
            })
            record = json.loads((repo / saved["file"]).read_text(encoding="utf-8"))
            self.assertEqual(record["route"], "/songs/릐호/")
            self.assertEqual(record["songEditor"]["lyrics"][0]["text"], "릐호")
            self.assertIn(record["route"], json.loads((repo / "content/song-categories.json").read_text())[0]["routes"])
            self.assertEqual(json.loads((repo / "migration/song-urls.json").read_text())[0]["new_url"], record["route"])
            self.assertEqual(json.loads((repo / "migration/wordpress-map.json").read_text())["records"][0]["file"], saved["file"])


if __name__ == "__main__":
    unittest.main()
