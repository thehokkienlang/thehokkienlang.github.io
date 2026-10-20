"""Entry saves and reconciliation must preserve meanings, identities and work."""
import json
import hashlib
import io
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "desktop"))
import dictionary_editor_service as editor
from dictionary_editor_service import DictionaryEditorService, EditorError, MAIN, REGISTRY, CATEGORIES, read_table, table_bytes
from dictionary_editor_publish import merge_sources, DictionaryPublisher, git, BASELINE
import dictionary_editor_publish as publishing
from dictionary_schema import DICTIONARY_COLUMNS, ENTRY_ID_REGISTRY_COLUMNS
from dictionary_references import CATEGORY_COLUMNS
from sort_dictionary_tsv import sort_tsv
from validate_dictionary_tsv import validate
from node_runtime import node_environment


def entry(hanri="家", reading="가1", english="home", identity="U+5BB6_00"):
    return dict.fromkeys(DICTIONARY_COLUMNS, "") | dict(hanri=hanri, simplified="〃", reading=reading,
                                                       english=english, entry_type="lexical", entry_id=identity)


def fixture(root):
    data = root / "data"
    data.mkdir(parents=True)
    files = {
        MAIN: table_bytes(DICTIONARY_COLUMNS, [entry()]),
        REGISTRY: table_bytes(ENTRY_ID_REGISTRY_COLUMNS, [dict(entry_id="U+5BB6_00", canonical_headword="家", redirect_entry_id="")]),
        CATEGORIES: table_bytes(CATEGORY_COLUMNS, [dict(category="home", label="Home", entry="家", entry_id="U+5BB6_00")]),
        "dictionary_priority.tsv": b"lookup_key\tentry\tentry_id\trank\r\n",
        "dictionary_redirects.tsv": b"kind\tsource\tsource_reading\ttarget_entry_id\treason\tsources\tdate\r\n",
    }
    for name, raw in files.items():
        (data / name).write_bytes(raw)
    return files


class NodeRuntimeTests(unittest.TestCase):
    def test_node_on_path_is_propagated_to_child_processes(self):
        with tempfile.TemporaryDirectory() as folder:
            executable = Path(folder) / 'node.exe'
            executable.touch()
            with patch('node_runtime.shutil.which', return_value=str(executable)):
                node, env = node_environment({'PATH': 'existing-path'})
            self.assertEqual(node, str(executable.resolve()))
            self.assertEqual(env['TANGLIENGIM_NODE'], node)
            self.assertEqual(env['PATH'], str(executable.resolve().parent) + os.pathsep + 'existing-path')

    def test_desktop_without_node_on_path_finds_bundled_runtime(self):
        with tempfile.TemporaryDirectory() as folder:
            executable = Path(folder) / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
            executable.parent.mkdir(parents=True)
            executable.touch()
            with patch('node_runtime.shutil.which', return_value=None):
                node, env = node_environment({'USERPROFILE': folder, 'PATH': ''})
            self.assertEqual(node, str(executable.resolve()))
            self.assertEqual(env['PATH'].split(os.pathsep)[0], str(executable.resolve().parent))

    def test_explicit_missing_runtime_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(FileNotFoundError, 'Install Node.js LTS'):
                node_environment({'TANGLIENGIM_NODE': str(Path(folder) / 'missing.exe')})

    def test_publisher_reports_missing_node_before_git_operations(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            fixture(repo)
            publisher = DictionaryPublisher(DictionaryEditorService(repo))
            with (patch.object(publishing, 'node_environment', side_effect=FileNotFoundError('Install Node.js LTS')),
                  patch.object(publishing, 'git') as run_git):
                with self.assertRaises(EditorError) as caught:
                    publisher.publish()
                self.assertEqual(caught.exception.code, 'dependency')
                run_git.assert_not_called()


class SaveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        fixture(self.root)
        self.service = DictionaryEditorService(self.root)

    def test_add_sorts_allocates_and_updates_categories(self):
        result = self.service.save([dict(hanri="新", reading="신ˆ", english="new", categories=["home"])])
        self.assertEqual(result["saved"][0]["entry_id"], "U+65B0_00")
        self.assertEqual(result["saved"][0]["reading"], "신1")
        self.assertEqual(result["saved"][0]["simplified"], "〃")
        self.assertEqual(validate(self.root / "data" / MAIN), [])
        self.assertEqual(sort_tsv(self.root / "data" / MAIN, check=True), 0)
        self.assertEqual(self.service.snapshot()["entries"][1]["categories"], ["home"])

    def test_exact_duplicate_is_skipped_and_alternative_needs_confirmation(self):
        result = self.service.save([entry() | {"entry_id": ""}])
        self.assertEqual(result["saved"], [])
        self.assertEqual(result["skipped"], ["U+5BB6_00"])
        before = self.service.files()
        with self.assertRaises(EditorError) as caught:
            self.service.save([dict(hanri="家", reading="ᄀᅷ1")])
        self.assertEqual(caught.exception.code, "alternative")
        self.assertEqual(self.service.files(), before)
        result = self.service.save([dict(hanri="家", reading="ᄀᅷ1")], allow_alternative=True)
        self.assertEqual(result["saved"][0]["entry_id"], "U+5BB6_01")

    def test_edit_keeps_id_and_other_fields(self):
        record = self.service.snapshot()["entries"][0]
        record["english"] = "house; home"
        result = self.service.save([record])
        self.assertEqual(result["saved"][0]["entry_id"], "U+5BB6_00")
        self.assertEqual(result["saved"][0]["english"], "house; home")

    def test_identity_change_rejected(self):
        record = entry() | {"hanri": "新"}
        with self.assertRaisesRegex(EditorError, "identity headword"):
            self.service.save([record])

    def test_stale_form_does_not_overwrite_new_entry(self):
        snapshot = self.service.snapshot()
        self.service.save([dict(hanri="新", reading="신1")])
        with self.assertRaises(EditorError) as caught:
            self.service.save([entry() | {"english": "changed"}], revision=snapshot["revision"])
        self.assertEqual(caught.exception.code, "stale")
        self.assertEqual(len(self.service.snapshot()["entries"]), 2)

    def test_invalid_batch_writes_nothing(self):
        before = self.service.files()
        with self.assertRaises(EditorError):
            self.service.save([dict(hanri="新", reading="신1"), dict(hanri="空", reading="")])
        self.assertEqual(before, self.service.files())

    def test_duplicate_inside_batch_has_allocated_id(self):
        row = dict(hanri="新", reading="신1")
        result = self.service.save([row, row])
        self.assertEqual(len(result["saved"]), 1)
        self.assertEqual(result["skipped"], ["U+65B0_00"])

    def test_paste_columns_and_metadata_blanks(self):
        result = self.service.import_rows("新\t신1\tnew\t新\n")
        self.assertEqual(result[0]["english"], "new")
        self.assertEqual(result[0]["mandarin_trad"], "新")
        blank = self.service.import_rows("新\t신1")[0]
        self.assertEqual(blank["english"], "")
        self.assertEqual(blank["mandarin_trad"], "")
        with self.assertRaises(EditorError):
            self.service.import_rows("hanri\treading\tunknown\n新\t신1\tx")

    def test_reserved_ids_not_reused(self):
        registry = self.root / "data" / REGISTRY
        registry.write_bytes(registry.read_bytes() + "U+65B0_04\t新\t\r\n".encode())
        result = self.service.save([dict(hanri="新", reading="신1")])
        self.assertEqual(result["saved"][0]["entry_id"], "U+65B0_05")

    def test_partial_update_and_batch_import_preserve_existing_metadata(self):
        self.service.save([{"entry_id": "U+5BB6_00", "english": "house; home"}])
        row = self.service.snapshot()["entries"][0]
        self.assertEqual(row["reading"], "가1")
        self.assertEqual(row["categories"], ["home"])
        imported = self.service.import_rows("entry_id\thanri\treading\nU+5BB6_00\t家\t가2")
        self.assertEqual(imported[0]["english"], "house; home")

    def test_empty_isolated_dictionary_supported(self):
        target = self.root / "other" / "new_readings.tsv"
        service = DictionaryEditorService.for_tsv(target)
        result = service.save([dict(hanri="德國", reading="뎩1걱")])
        self.assertTrue(target.exists())
        self.assertEqual(result["saved"][0]["simplified"], "德国")

    def test_missing_existing_registry_is_not_reconstructed(self):
        (self.root / "data" / REGISTRY).unlink()
        with self.assertRaises(EditorError):
            self.service.save([dict(hanri="新", reading="신1")])

    def test_interrupted_multi_file_save_recovers(self):
        original = editor._atomic_write
        failed = False
        def interrupted(path, raw):
            nonlocal failed
            if path == self.root / "data" / REGISTRY and not failed:
                failed = True
                raise OSError("simulated interrupted save")
            original(path, raw)
        with patch.object(editor, "_atomic_write", side_effect=interrupted):
            with self.assertRaises(OSError):
                self.service.save([dict(hanri="新", reading="신1")])
        snapshot = self.service.snapshot()
        self.assertEqual(len(snapshot["entries"]), 2)
        self.assertEqual(validate(self.root / "data" / MAIN), [])

    def test_concurrent_saves_do_not_drop_entries(self):
        errors = []
        def save(reading):
            try:
                self.service.save([dict(hanri="新", reading=reading)], allow_alternative=True)
            except Exception as error:
                errors.append(error)
        threads = [threading.Thread(target=save, args=(f"신{tone}",)) for tone in (1, 2, 4, 5)]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        self.assertEqual(errors, [])
        self.assertEqual(len(self.service.snapshot()["entries"]), 5)


class MergeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = fixture(Path(self.temp.name))

    def changed(self, source, **changes):
        result = dict(source)
        header, rows = read_table(result[MAIN])
        rows[0].update(changes)
        result[MAIN] = table_bytes(header, rows)
        return result

    def test_independent_fields_merge_without_conflict(self):
        local = self.changed(self.base, english="house")
        remote = self.changed(self.base, mandarin_trad="房子", mandarin_simp="房子")
        merged, _ = merge_sources(self.base, local, remote)
        row = read_table(merged[MAIN])[1][0]
        self.assertEqual(row["english"], "house")
        self.assertEqual(row["mandarin_trad"], "房子")

    def test_conflicting_gloss_requires_explicit_resolution(self):
        local = self.changed(self.base, english="house")
        remote = self.changed(self.base, english="family")
        with self.assertRaises(EditorError) as caught:
            merge_sources(self.base, local, remote)
        self.assertEqual(caught.exception.code, "conflict")
        conflict = caught.exception.details[0]
        merged, _ = merge_sources(self.base, local, remote, {conflict["token"]: "local"})
        self.assertEqual(read_table(merged[MAIN])[1][0]["english"], "house")

    def test_concurrent_id_collision_keeps_both_and_category_references(self):
        local, remote = dict(self.base), dict(self.base)
        for source, reading in ((local, "신1"), (remote, "신2")):
            header, rows = read_table(source[MAIN])
            rows.append(entry("新", reading, "new", "U+65B0_00"))
            source[MAIN] = table_bytes(header, rows)
            header, rows = read_table(source[REGISTRY])
            rows.append(dict(entry_id="U+65B0_00", canonical_headword="新", redirect_entry_id=""))
            source[REGISTRY] = table_bytes(header, rows)
        header, rows = read_table(local[CATEGORIES])
        rows.append(dict(category="home", label="Home", entry="新", entry_id="U+65B0_00"))
        local[CATEGORIES] = table_bytes(header, rows)
        merged, mapping = merge_sources(self.base, local, remote)
        self.assertEqual(mapping, {"U+65B0_00": "U+65B0_01"})
        self.assertEqual(len(read_table(merged[MAIN])[1]), 3)
        self.assertEqual(read_table(merged[CATEGORIES])[1][-1]["entry_id"], "U+65B0_01")

    def test_new_entry_cannot_reuse_a_concurrently_retired_id(self):
        local, remote = dict(self.base), dict(self.base)
        header, rows = read_table(local[MAIN])
        rows.append(entry("新", "신1", "new", "U+65B0_00"))
        local[MAIN] = table_bytes(header, rows)
        for source in (local, remote):
            header, rows = read_table(source[REGISTRY])
            rows.append(dict(entry_id="U+65B0_00", canonical_headword="新", redirect_entry_id=""))
            source[REGISTRY] = table_bytes(header, rows)
        merged, mapping = merge_sources(self.base, local, remote)
        self.assertEqual(mapping["U+65B0_00"], "U+65B0_01")
        self.assertEqual(len(read_table(merged[REGISTRY])[1]), 3)


class HttpTests(unittest.TestCase):
    def test_publish_saves_current_edits_before_starting_job(self):
        from tangliengim_web_shell import DesktopHttpServer
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder).resolve()
            fixture(repo)
            server = DesktopHttpServer(repo, ROOT / 'desktop/Hokkien Tangliengim IME Pad.py')
            try:
                snapshot = server.editor.service.snapshot()
                record = snapshot['entries'][0] | {'english': 'house; home'}
                def start(kind, operation):
                    self.assertEqual(kind, 'publish')
                    self.assertEqual(server.editor.service.snapshot()['entries'][0]['english'], 'house; home')
                    return {'ok': True, 'job': 'publishing'}
                with patch.object(server.editor, 'start_job', side_effect=start):
                    result = server.editor.dispatch('publish', {'entries': [record], 'revision': snapshot['revision']})
                self.assertEqual(result['saved'][0]['entry_id'], record['entry_id'])
                self.assertEqual(result['job'], 'publishing')
            finally:
                server.server_close()

    def test_publish_invalid_edits_do_not_start_job_or_change_data(self):
        from tangliengim_web_shell import DesktopHttpServer
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder).resolve()
            fixture(repo)
            server = DesktopHttpServer(repo, ROOT / 'desktop/Hokkien Tangliengim IME Pad.py')
            try:
                before = server.editor.service.files()
                with patch.object(server.editor, 'start_job') as start:
                    with self.assertRaises(EditorError):
                        server.editor.dispatch('publish', {'entries': [dict(hanri='test', reading='')]})
                    start.assert_not_called()
                self.assertEqual(server.editor.service.files(), before)
            finally:
                server.server_close()

    def test_editor_is_local_only_and_requires_session_token(self):
        from tangliengim_web_shell import DesktopHttpServer, _safe_repo_file
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder).resolve()
            fixture(repo)
            server = DesktopHttpServer(repo, ROOT / "desktop/Hokkien Tangliengim IME Pad.py")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            url = f"http://127.0.0.1:{server.server_port}/desktop-api/editor/snapshot"
            try:
                request = Request(url, b"{}", {"Content-Type": "application/json"})
                with self.assertRaises(HTTPError) as caught: urlopen(request)
                self.assertEqual(caught.exception.code, 403)
                request.add_header("X-Tangliengim-Editor", server.editor_token)
                self.assertEqual(len(json.load(urlopen(request))["entries"]), 1)
                request.add_header("Origin", "https://unrelated.example")
                with self.assertRaises(HTTPError) as caught: urlopen(request)
                self.assertEqual(caught.exception.code, 403)
                self.assertIsNone(_safe_repo_file(ROOT, "/editor/../hokkien_tone_marker_gui.py"))
                self.assertIsNone(_safe_repo_file(ROOT, "/.dictionary-editor/transaction.json"))
            finally:
                server.shutdown(); server.server_close(); thread.join(timeout=2)

    def test_runtime_refresh_uses_a_snapshot_and_retries_new_saves(self):
        from tangliengim_web_shell import DesktopHttpServer
        import dictionary_editor as controller_module
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder).resolve()
            fixture(repo)
            (repo / 'public/data').mkdir(parents=True)
            server = DesktopHttpServer(repo, ROOT / 'desktop/Hokkien Tangliengim IME Pad.py')
            calls = []
            def build(command, **kwargs):
                source = Path(command[command.index('--input') + 1])
                output = Path(command[command.index('--output') + 1])
                calls.append(len(read_table(source.read_bytes())[1]))
                if len(calls) == 1:
                    server.editor.service.save([dict(hanri='新', reading='신1')])
                output.write_text(json.dumps({'sourceSha256': 'fixture'}), encoding='utf-8')
                return subprocess.CompletedProcess(command, 0, '', '')
            try:
                with patch.object(controller_module.subprocess, 'run', side_effect=build):
                    result = server.editor.refresh_runtime(lambda _: None)
                self.assertEqual(calls, [1, 2])
                self.assertEqual(result['generation'], 1)
                generated = json.loads((repo / 'public/data/hokkien-hanri-dict.json').read_text(encoding='utf-8'))
                self.assertEqual(generated['source'], 'data/' + MAIN)
            finally:
                server.server_close()

    def test_saving_can_continue_during_background_refresh(self):
        from tangliengim_web_shell import DesktopHttpServer
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder).resolve()
            fixture(repo)
            server = DesktopHttpServer(repo, ROOT / 'desktop/Hokkien Tangliengim IME Pad.py')
            try:
                server.editor.active_job = 'refreshing'
                server.editor.jobs['refreshing'] = {'kind': 'refresh', 'status': 'running'}
                result = server.editor.dispatch('save', {'entries': [dict(hanri='新', reading='신1')]})
                self.assertEqual(result['job'], 'refreshing')
                self.assertEqual(len(server.editor.service.snapshot()['entries']), 2)
            finally:
                server.server_close()


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        folder = Path(self.temp.name).resolve()
        self.remote = folder / "remote.git"
        self.repo = folder / "local"
        self.repo.mkdir()
        subprocess.run(["git", "init", "--bare", "--initial-branch=main", str(self.remote)], check=True, capture_output=True)
        fixture(self.repo)
        (self.repo / ".gitignore").write_text(".dictionary-editor/\npublic/\n")
        (self.repo / "README.md").write_text("original code\n")
        (self.repo / "tools").mkdir()
        (self.repo / "tools/check_release.py").write_text("print('fixture release checks passed')\n")
        (self.repo / 'tools/build_dictionary_json.py').write_text(
            "from pathlib import Path\n"
            "out = Path('public/data/hokkien-hanri-dict.json')\n"
            "out.parent.mkdir(parents=True, exist_ok=True)\n"
            "out.write_bytes(Path('data/hokkien_hanri_dict.tsv').read_bytes())\n"
        )
        (self.repo / 'tools/check_dictionary_baseline.cjs').write_text(
            "const fs = require('fs'), crypto = require('crypto'), assert = require('assert');\n"
            "const hash = crypto.createHash('sha256').update(fs.readFileSync('public/data/hokkien-hanri-dict.json')).digest('hex');\n"
            "const baseline = 'tests/fixtures/dictionary-baseline.json';\n"
            "if (process.argv.includes('--capture')) fs.writeFileSync(baseline, hash);\n"
            "else assert.equal(fs.readFileSync(baseline, 'utf8'), hash, 'Existing baseline mismatch');\n"
        )
        (self.repo / BASELINE).parent.mkdir(parents=True)
        self.capture_fixture_baseline(self.repo)
        git(self.repo, "init", "--initial-branch=main")
        git(self.repo, "config", "user.name", "Dictionary editor test")
        git(self.repo, "config", "user.email", "editor@example.invalid")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-m", "Initial")
        git(self.repo, "remote", "add", "origin", str(self.remote))
        git(self.repo, "push", "-u", "origin", "main")
        self.service = DictionaryEditorService(self.repo)

    def capture_fixture_baseline(self, repo):
        (repo / BASELINE).write_text(hashlib.sha256((repo / 'data' / MAIN).read_bytes()).hexdigest())

    def remote_edit(self):
        clone = self.repo.parent / "other"
        git(self.repo, "clone", str(self.remote), str(clone))
        git(clone, "config", "user.name", "Other editor")
        git(clone, "config", "user.email", "other@example.invalid")
        service = DictionaryEditorService(clone)
        record = service.snapshot()["entries"][0]
        record["mandarin_trad"] = "房子"
        service.save([record])
        self.capture_fixture_baseline(clone)
        git(clone, "add", "data", BASELINE)
        git(clone, "commit", "-m", "Remote semantic edit")
        git(clone, "push", "origin", "main")

    def test_publish_merges_remote_and_keeps_unrelated_local_code(self):
        self.remote_edit()
        self.service.save([dict(hanri="新", reading="신1", english="new")])
        (self.repo / "README.md").write_text("unpublished local code\n")
        result = DictionaryPublisher(self.service).publish()
        self.assertTrue(result["ok"])
        self.assertEqual(git(self.repo, "rev-parse", "HEAD").stdout, git(self.repo, "rev-parse", "origin/main").stdout)
        self.assertEqual((self.repo / "README.md").read_text(), "unpublished local code\n")
        self.assertEqual(git(self.repo, "show", "origin/main:README.md").stdout, "original code\n")
        entries = self.service.snapshot()["entries"]
        self.assertEqual(len(entries), 2)
        self.assertEqual(next(row for row in entries if row["hanri"] == "家")["mandarin_trad"], "房子")
        self.assertEqual(git(self.repo, "status", "--porcelain", "--", "data").stdout.strip(), "")
        self.assertEqual((self.repo / BASELINE).read_text(), hashlib.sha256((self.repo / 'data' / MAIN).read_bytes()).hexdigest())

    def test_existing_baseline_failure_blocks_recapture_and_publish(self):
        (self.repo / BASELINE).write_text('broken baseline')
        git(self.repo, 'add', BASELINE)
        git(self.repo, 'commit', '-m', 'Broken original baseline')
        git(self.repo, 'push', 'origin', 'main')
        before = git(self.repo, 'rev-parse', 'origin/main').stdout
        self.service.save([dict(hanri='新', reading='신1')])
        with self.assertRaisesRegex(EditorError, 'Existing baseline mismatch'):
            DictionaryPublisher(self.service).publish()
        self.assertEqual(git(self.repo, 'rev-parse', 'origin/main').stdout, before)
        self.assertEqual((self.repo / BASELINE).read_text(), 'broken baseline')
        self.assertEqual(len(self.service.snapshot()['entries']), 2)

    def test_failed_checks_keep_local_entries_and_remote_unchanged(self):
        (self.repo / "tools/check_release.py").write_text("raise SystemExit('test validation failure')\n")
        git(self.repo, "add", "tools")
        git(self.repo, "commit", "-m", "Failing test gate")
        git(self.repo, "push", "origin", "main")
        self.service.save([dict(hanri="新", reading="신1")])
        before = git(self.repo, "rev-parse", "origin/main").stdout
        with self.assertRaisesRegex(EditorError, "Release checks failed"):
            DictionaryPublisher(self.service).publish()
        self.assertEqual(len(self.service.snapshot()["entries"]), 2)
        self.assertEqual(git(self.repo, "rev-parse", "origin/main").stdout, before)

    def test_unpublished_commits_are_not_pushed_as_a_side_effect(self):
        (self.repo / "README.md").write_text("local commit\n")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-m", "Unpublished code")
        with self.assertRaisesRegex(EditorError, "unpublished commits"):
            DictionaryPublisher(self.service).publish()

    @unittest.skipUnless(os.name == 'nt', 'Windows GUI interpreter regression')
    def test_gui_publish_preserves_nested_validation_errors(self):
        gui_python = Path(sys.executable).with_name('pythonw.exe')
        self.assertTrue(gui_python.is_file())
        (self.repo / 'tools/check_release.py').write_text(
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            "print('Validation interpreter: ' + Path(sys.executable).name, flush=True)\n"
            "subprocess.run([sys.executable, '-c', \"import sys; sys.stderr.write('nested validation failure\\\\n'); sys.exit(1)\"], check=True)\n"
        )
        git(self.repo, 'add', 'tools')
        git(self.repo, 'commit', '-m', 'Nested failing check')
        git(self.repo, 'push', 'origin', 'main')
        before = git(self.repo, 'rev-parse', 'origin/main').stdout
        self.service.save([dict(hanri='新', reading='신1')])
        with patch.object(publishing.sys, 'executable', str(gui_python)):
            with self.assertRaisesRegex(EditorError, 'nested validation failure'):
                DictionaryPublisher(self.service).publish()
        log = (self.service.state / 'publish-checks.log').read_text(encoding='utf-8')
        self.assertIn('Validation interpreter: python.exe', log)
        self.assertEqual(git(self.repo, 'rev-parse', 'origin/main').stdout, before)
        self.assertEqual(len(self.service.snapshot()['entries']), 2)

    def test_entry_saved_during_checks_requires_retry(self):
        self.service.save([dict(hanri="新", reading="신1")])
        def progress(message):
            if message.startswith("Running dictionary"):
                self.service.save([dict(hanri="新", reading="신2")], allow_alternative=True)
        with self.assertRaises(EditorError) as caught:
            DictionaryPublisher(self.service, progress).publish()
        self.assertEqual(caught.exception.code, "stale")
        self.assertEqual(len(self.service.snapshot()["entries"]), 3)

    def test_public_deployment_status_works_without_github_cli(self):
        self.service.state.mkdir(parents=True)
        (self.service.state / 'publication.json').write_text(json.dumps({'commit': 'a' * 40, 'status': 'published'}))
        payload = {'workflow_runs': [{'head_branch': 'main', 'path': '.github/workflows/pages.yml',
                                     'conclusion': 'success', 'status': 'completed', 'html_url': 'https://github.com/example/site/actions/runs/1'}]}
        with (patch.object(publishing.shutil, 'which', return_value=None),
              patch.object(publishing, 'git', return_value=subprocess.CompletedProcess([], 0, 'https://github.com/example/site.git\n', '')),
              patch.object(publishing, 'urlopen', return_value=io.BytesIO(json.dumps(payload).encode()))):
            result = DictionaryPublisher(self.service).deployment_status()
        self.assertEqual(result['status'], 'deployed')


if __name__ == "__main__":
    unittest.main()
