"""Cue boundaries, lyric identity, safe local saves and build-only annotations."""
import copy
import json
import math
import sys
import tempfile
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from lyric_timing import blank_timing, decorate_lyrics, song_lines, timing_path, validate_timing
from website_editor_service import WebsiteEditorError, WebsiteEditorService
from node_runtime import node_environment


def song():
    line = '<p><span style="display: block;font-size: 1em"><ruby>字<rt>지ˆ</rt></ruby></span><span style="display: block;font-size: 0.7em">ji</span></p>'
    return {'id':'song-test', 'type':'songs', 'title':'Song', 'route':'/songs/test/',
            'body':'<h2>Title</h2><iframe src="https://www.youtube.com/embed/HNYkSBkQ33Y"></iframe>' + line + '\n' + line + '<p>Not lyrics</p>'}


class LyricTimingTests(unittest.TestCase):
    def test_browser_clock_and_highlight_states(self):
        try:
            node, env = node_environment()
        except FileNotFoundError:
            self.skipTest('Node is needed for browser clock tests.')
        subprocess.run([node, str(ROOT/'tests/check_lyric_clock.cjs')], env=env, check=True, capture_output=True)

    def test_extraction_keeps_repetitions_separate_and_ignores_ruby_in_label(self):
        video, lines = song_lines(song())
        self.assertEqual(video, 'HNYkSBkQ33Y')
        self.assertEqual([line['label'] for line in lines], ['字', '字'])
        self.assertEqual([line['id'] for line in lines], ['line-001', 'line-002'])
        for line in lines:
            self.assertEqual(song()['body'][line['startOffset']:line['endOffset']], line['html'])

    def test_validation_and_exact_video_and_line_identity(self):
        record = song()
        data = blank_timing(record)
        self.assertEqual(validate_timing(record, data), data)
        for key, value in [('videoId','xxxxxxxxxxx'), ('songId','other'), ('schemaVersion',2)]:
            bad = {**data, key:value}
            with self.assertRaises(ValueError): validate_timing(record, bad)
        changed = copy.deepcopy(record)
        changed['body'] = changed['body'].replace('지ˆ', '지ˉ')
        with self.assertRaisesRegex(ValueError, 'line changed'): validate_timing(changed, data)

    def test_ranges_missing_values_and_review_gate(self):
        record = song()
        for start, end in [(2,1), (-1,2), (1,None), (True,2), (math.nan,2), (1,math.inf)]:
            data = blank_timing(record); data['cues'][0].update(start=start, end=end)
            with self.subTest(start=start, end=end), self.assertRaises(ValueError): validate_timing(record, data)
        data = blank_timing(record); data['status'] = 'reviewed'
        with self.assertRaisesRegex(ValueError, 'every lyric'): validate_timing(record, data)
        data['cues'][0].update(start=10, end=15)
        data['cues'][1].update(start=14, end=20)
        with self.assertRaisesRegex(ValueError, 'overlapping'): validate_timing(record, data)
        data['cues'][1]['start'] = 15
        self.assertEqual(validate_timing(record, data)['status'], 'reviewed')

    def test_annotations_only_change_generated_markup(self):
        record = song(); original = copy.deepcopy(record)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertEqual(decorate_lyrics(root, record, record['body']), record['body'])
            path = timing_path(root, record); path.parent.mkdir(parents=True)
            path.write_text(json.dumps(blank_timing(record)), encoding='utf-8')
            rendered = decorate_lyrics(root, record, record['body'])
            self.assertEqual(rendered.count('data-lyric-id='), 2)
            self.assertIn('id="lyric-timing-data"', rendered)
            self.assertIn('<ruby>字<rt>지ˆ</rt></ruby>', rendered)
            self.assertEqual(record, original)

    def test_editor_revision_protects_both_sources_and_never_changes_body(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root/'content/songs/song-test.json'; source.parent.mkdir(parents=True)
            source.write_text(json.dumps(song(), ensure_ascii=False), encoding='utf-8')
            raw = source.read_bytes(); service = WebsiteEditorService(root)
            opened = service.lyric_timing('content/songs/song-test.json')
            saved = service.save_lyric_timing(opened['file'], opened['sourceRevision'], opened['revision'], opened['timing'])
            self.assertEqual(source.read_bytes(), raw)
            with self.assertRaisesRegex(WebsiteEditorError, 'outside'):
                service.save_lyric_timing(opened['file'], opened['sourceRevision'], opened['revision'], opened['timing'])
            source.write_text(source.read_text(encoding='utf-8')+'\n', encoding='utf-8')
            with self.assertRaisesRegex(WebsiteEditorError, 'outside'):
                service.save_lyric_timing(opened['file'], opened['sourceRevision'], saved['revision'], opened['timing'])
            with self.assertRaises(WebsiteEditorError): service.lyric_timing('../outside.json')
            record = json.loads(source.read_text(encoding='utf-8'))
            record['body'] = record['body'].replace('지ˆ', '지ˉ')
            source.write_text(json.dumps(record), encoding='utf-8')
            reloaded = service.lyric_timing(opened['file'])
            self.assertTrue(reloaded['warning'])
            self.assertEqual(reloaded['timing']['status'], 'draft')
            service.save_lyric_timing(reloaded['file'], reloaded['sourceRevision'], reloaded['revision'], reloaded['timing'])

    def test_published_sidecars_match_authored_lyrics(self):
        for identity, count in (('song-11533', 24), ('song-8502', 24), ('song-192', 32)):
            with self.subTest(song=identity):
                source = json.loads((ROOT/f'content/songs/{identity}.json').read_text(encoding='utf-8'))
                data = json.loads(timing_path(ROOT, source).read_text(encoding='utf-8'))
                validate_timing(source, data)
                self.assertEqual(len(data['cues']), count)
                self.assertTrue(all(cue['start'] is not None and cue['end'] is not None for cue in data['cues']))


if __name__ == '__main__': unittest.main()
