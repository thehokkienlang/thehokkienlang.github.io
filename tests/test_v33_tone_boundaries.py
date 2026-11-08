"""Focused v3.3 tone-domain regressions without dictionary/fixture dependencies."""
import sys
from contextlib import ExitStack
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'desktop'))
import tangliengim_engine as engine
import hokkien_tone_marker_gui as gui


class ToneBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name, value in [
            ('AUDIO_READING_INDEX', [('’ᄅᆤ', '’ᄅᆤ2'), ('’뽀', '’뽀4')]),
            ('AUDIO_READING_INDEX_BY_FIRST', {}), ('AUDIO_HANRI_INDEX', []),
            ('MIXED_AUDIO_HANRI_INDEX', []), ('AUDIO_HANRI_SEGMENT_INDEX', []),
        ]:
            self.stack.enter_context(patch.object(engine, name, value))
        self.stack.enter_context(patch.object(gui, 'load_hanri_reading_index', return_value={}))
        self.stack.enter_context(patch.object(gui, '_HANGUL_OVERRIDE_INDEX', {'나': '나2', '’ᄅᆤ': '’ᄅᆤ2', '’뽀': '’뽀4'}))
        self.stack.enter_context(patch.object(gui, '_HANGUL_OVERRIDE_KEYS', ['’ᄅᆤ', '’뽀', '나']))

    def tones(self, text, mode='taipei'):
        segments, missing = engine.visible_text_to_audio_segments(text, mode)
        self.assertEqual(missing, [])
        return [s[1] for s in segments]

    def test_single_continuations_and_repeated_boundaries(self):
        for mark in ['-', '—', '…', '——', '……', '———', '………']:
            single = len(mark) == 1
            with self.subTest(mark=mark):
                self.assertEqual(self.tones('가' + mark), ['2' if single else '3'])
                self.assertEqual(self.tones('[甲가]' + mark), ['2' if single else '3'])
                self.assertEqual(gui.is_followed_by_hanri('甲' + mark, 0), single)
                self.assertEqual(gui.sandhi_raw_hangul_before_explicit_hyphen('가' + mark),
                                 ('가2' if single else '가') + mark)
                for index in range(1, len(mark) + 1):
                    self.assertEqual(engine.is_tone_continuation_at('가' + mark, index), single)

    def test_audio_trim_policy_is_unchanged(self):
        for mark in ['—', '——', '…', '……']:
            segments, _ = engine.visible_text_to_audio_segments('가1' + mark + '가2')
            expected = [(False, False), (False, False)] if '—' in mark else [(False, True), (True, False)]
            self.assertEqual([s[2:4] for s in segments], expected)

    def test_neutral_domain_ends_at_space_or_punctuation(self):
        for apostrophe in ["'", '’']:
            self.assertEqual(self.tones('가1' + apostrophe + '가2가4'), ['1', '3', '3'])
            self.assertEqual(self.tones('가1' + apostrophe + '가2가4', 'singapore'), ['1', '3', '3'])
            for boundary in [' ', ',', '，', '.', '/', '(', '‘', '-', '—', '——', '…', '……']:
                with self.subTest(apostrophe=apostrophe, boundary=boundary):
                    text = '가1' + apostrophe + '가2' + boundary + '가2'
                    self.assertEqual(self.tones(text), ['1', '3', '2'])
                    neutral = gui.apply_hangul_overrides_from_tsv(text)
                    self.assertEqual(self.tones(neutral), ['1', '3', '2'])
                    self.assertEqual(neutral, '가1' + apostrophe + '가3' + boundary + '가2')
                    self.assertEqual(gui.sandhi_raw_hangul_before_explicit_hyphen(neutral), neutral)
                    reading = '’가2' + boundary + '가2'
                    self.assertFalse(engine.is_post_apostrophe_tone(reading, len(reading) - 1))
                    self.assertEqual(gui.apply_hangul_overrides_from_tsv('가1' + apostrophe + '나' + boundary + '나'),
                                     '가1' + apostrophe + '나3' + boundary + '나2')

    def test_explicit_attached_exceptions(self):
        for unit, tone in [('ᄅᆤ', '2'), ('뽀', '4')]:
            self.assertEqual(self.tones('가1’' + unit + '가2'), ['1', tone, '3'])
            self.assertTrue(engine.is_post_apostrophe_tone('’' + unit + tone, len(unit) + 1))
            self.assertTrue(engine.is_explicit_apostrophe_tone_override('’' + unit, '’' + unit + tone))
            self.assertEqual(gui.apply_hangul_overrides_from_tsv('가1’' + unit), '가1’' + unit + tone)

    def test_opening_single_quote_is_a_boundary_not_apostrophe(self):
        self.assertEqual(self.tones('가1‘가2'), ['1', '2'])
        self.assertEqual(gui.apply_hangul_overrides_from_tsv('가1‘나'), '가1‘나2')
        self.assertFalse(engine.contains_apostrophe_boundary('가1‘가2'))
        self.assertFalse(engine.is_explicit_apostrophe_tone_override('‘뽀', '뽀4'))
        self.assertFalse(engine.is_post_apostrophe_tone('‘가2', 2))
        self.assertEqual(gui.visible_source_for_lomari_next_line('‘가2'), '‘가ˋ')


if __name__ == '__main__':
    unittest.main()
