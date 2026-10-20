"""Keep classic and shared Web normalization semantics on the same fixtures."""

import importlib.util
import json
import os
import random
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from simplified_normalization import SimplifiedNormalizationIndex, SimplifiedNormalizationSession

FIXTURE = json.loads((ROOT / 'tests/fixtures/simplified-normalization.json').read_text(encoding='utf-8'))


class NormalizationTests(unittest.TestCase):
    def test_shared_cases_and_row_independence(self):
        for entries in (FIXTURE['entries'], list(reversed(FIXTURE['entries']))):
            index = SimplifiedNormalizationIndex(entries)
            self.assertEqual(index.ambiguous_count, 1)
            for case in FIXTURE['cases']:
                session = SimplifiedNormalizationSession(index)
                session.update(case['text'])
                actual = [[match['source'], [t['hanri'] for t in match['targets']], match['start']]
                          for match in session.matches]
                self.assertEqual(actual, case['matches'], case['text'])
            self.assertEqual(index.match_at('负责任', 0)['targets'][0]['entryIds'],
                             ['U+8CA0_U+8CAC_U+4EFB_00', 'U+8CA0_U+8CAC_U+4EFB_01'])

    def test_incremental_edits(self):
        index = SimplifiedNormalizationIndex(FIXTURE['entries'])
        session = SimplifiedNormalizationSession(index)
        randomizer = random.Random(7351)
        text = '负责任 云云 发动'
        chars = list('负责任发动冲云面粉皮食麵뽀𤺪😀 x')
        for edit in range(800):
            start = randomizer.randrange(len(text) + 1)
            end = start + randomizer.randrange(4)
            inserted = ''.join(randomizer.choice(chars) for _ in range(randomizer.randrange(5)))
            text = text[:start] + inserted + text[end:]
            session.update(text)
            fresh = SimplifiedNormalizationSession(index)
            fresh.update(text)
            self.assertEqual(session.matches, fresh.matches, f'edit {edit}')

    def test_affected_region_only(self):
        index = SimplifiedNormalizationIndex(FIXTURE['entries'])
        session = SimplifiedNormalizationSession(index)
        session.update('x' * 20000 + '负责任' + 'x' * 20000)
        index.match_at = Mock(wraps=index.match_at)
        session.update(session.text + 'x')
        self.assertLess(index.match_at.call_count, index.max_length * 3)

    def test_replacement_and_stale_actions(self):
        session = SimplifiedNormalizationSession(SimplifiedNormalizationIndex(FIXTURE['entries']))
        session.update('ABC负责任XYZ 发动')
        match = session.matches[0]
        self.assertEqual(session.replacement(match, match['targets'][0], session.text),
                         ('ABC負責任XYZ 发动', 6))
        self.assertIsNone(session.replacement(match, match['targets'][0], 'unrelated'))
        session.update('changed')
        self.assertIsNone(session.replacement(match, match['targets'][0], session.text))
        session.update('')
        self.assertFalse(session.matches)

    def test_real_tsv_and_generated_data_agree(self):
        data_root = Path(os.environ.get('TANGLIENGIM_NORMALIZATION_REPO', str(ROOT)))
        index = SimplifiedNormalizationIndex.from_tsv(data_root / 'data/hokkien_hanri_dict.tsv')
        data = json.loads((data_root / 'public/data/hokkien-hanri-dict.json').read_text(encoding='utf-8'))
        generated = SimplifiedNormalizationIndex(data['entries'])
        self.assertEqual(index.size, generated.size)
        self.assertEqual(index.ambiguous_count, generated.ambiguous_count)
        self.assertEqual(index.trie, generated.trie)
        self.assertEqual(index.match_at('负责任', 0)['targets'], [
            {'hanri': '負責任', 'entryIds': ['U+8CA0_U+8CAC_U+4EFB_00']}])
        for matcher in (index, generated):
            session = SimplifiedNormalizationSession(matcher)
            for text, expected in (
                ('面', []),
                ('食面', [('食面', ['食麵'])]),
                ('食麵', []),
                ('面 食面 食麵', [('食面', ['食麵'])]),
                ('面', []),
            ):
                session.update(text)
                self.assertEqual([(m['source'], [t['hanri'] for t in m['targets']])
                                  for m in session.matches], expected, text)

    def test_classic_acceptance_uses_existing_undo_and_not_candidate_learning(self):
        spec = importlib.util.spec_from_file_location('normalization_classic_check',
                                                    ROOT / 'desktop/Hokkien Tangliengim IME Pad.py')
        pad = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = pad
        spec.loader.exec_module(pad)
        app = pad.HokkienIMEPad.__new__(pad.HokkienIMEPad)
        source = 'ABC负责任XYZ 发动'
        app.composer = pad.Composer(output=source, cursor_pos=len(source))
        app.hanri_instance_readings = []
        app.hanri_instance_text_snapshot = source
        app.undo_stack, app.redo_stack = [], []
        app.e_to_ye_autocorrect_on = SimpleNamespace(get=lambda: True)
        app.text = SimpleNamespace(value=source, focus_set=Mock())
        app.text.get = lambda *args: app.text.value
        app.close_candidate_popup = Mock()
        app.reset_lomari_buffer = Mock()
        app.normalization_session = SimplifiedNormalizationSession(
            SimplifiedNormalizationIndex(FIXTURE['entries']))
        app.normalization_session.update(source)
        def render():
            app.text.value = app.composer.text()
            app.normalization_session.update(app.text.value)
        app.render = render
        match = app.normalization_session.matches[0]
        self.assertTrue(app.accept_normalization_suggestion(match, match['targets'][0]))
        self.assertEqual(app.composer.text(), 'ABC負責任XYZ 发动')
        self.assertEqual(app.composer.cursor_pos, 6)
        self.assertEqual(app.undo_stack[-1][0], source)
        self.assertEqual(len(app.normalization_session.matches), 1)
        self.assertFalse(app.accept_normalization_suggestion(match, match['targets'][0]))


if __name__ == '__main__':
    unittest.main()
