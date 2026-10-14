"""Redirects resolve through the real classic candidate and audio paths."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_dictionary_json import load_ime_module, load_tone_marker_module
from dictionary_schema import REDIRECT_COLUMNS, load_headword_aliases
from build_redirect_log import render, TSV, MARKDOWN


class RedirectTests(unittest.TestCase):
    def test_log_matches_source_and_jamo_order(self):
        tsv, markdown = render()
        self.assertEqual(TSV.read_bytes(), tsv)
        self.assertEqual(MARKDOWN.read_bytes(), markdown)

    def test_classic_candidates_and_audio(self):
        module = load_ime_module()
        pad = module.HokkienIMEPad.__new__(module.HokkienIMEPad)
        pad.output_tones_on = SimpleNamespace(get=lambda: False)
        pad.input_mode = SimpleNamespace(get=lambda: 'hangul')
        pad.hanri_on = SimpleNamespace(get=lambda: True)
        pad.suppressed_hanri_contexts = set()
        pad.lomari_raw = ''
        for value in ['米粉粿', '삐1훈1궤2', '미훈1궤2']:
            pad.composer = module.Composer(output=value, cursor_pos=len(value))
            menu = pad.find_hanri_candidate()
            self.assertIn('麵粉粿', menu['choices'])
            self.assertNotIn('米粉粿', menu['choices'])
            position = menu['choices'].index('麵粉粿')
            self.assertEqual(menu['choice_readings'][position], '미훈1궤2')
        self.assertEqual(module.static_audio_hanri_match('米粉粿', 0), ('麵粉粿', '미훈1궤2'))
        self.assertEqual(load_tone_marker_module().tsv_hanri_segment_for_run('米粉粿', 0), ('麵粉粿', '미훈1궤2'))

    def test_unknown_target_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'hokkien_hanri_dict.tsv'
            with path.with_name('dictionary_redirects.tsv').open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream, delimiter='\t')
                writer.writerow(REDIRECT_COLUMNS)
                writer.writerow(['headword','米粉粿','삐1훈1궤2','missing','test','test','unknown'])
            with self.assertRaisesRegex(ValueError, 'Invalid or ambiguous'):
                load_headword_aliases(path, [])
