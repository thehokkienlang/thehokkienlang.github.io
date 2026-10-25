"""Reviewed v3.2 headwords replace obsolete spellings without deleting other senses."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_dictionary_json import load_tone_marker_module
from dictionary_editor_service import read_table
from dictionary_schema import is_comment_record
from tangliengim_collation import reading_sort_key


class DictionaryHarmonisationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {row['entry_id']: row for row in read_table((ROOT / 'data/hokkien_hanri_dict.tsv').read_bytes())[1]
                    if not is_comment_record(row)}
        cls.archived = {row['entry_id']: row for row in read_table((ROOT / 'data/dictionary_defunct.tsv').read_bytes())[1]}
        cls.report = json.loads((ROOT / 'docs/harmonisation-3.2-dictionary.json').read_text(encoding='utf-8'))

    def test_reviewed_additions_have_the_approved_readings(self):
        additions = list(self.report['added'])
        for follow_up in self.report.get('followUps', []):
            additions.extend(follow_up['added'])
        for expected in additions:
            with self.subTest(entry=expected['entry_id']):
                current = self.rows[expected['entry_id']]
                for field in ('entry_id', 'hanri', 'entry_type'):
                    self.assertEqual(current[field], expected[field])
                self.assertEqual(reading_sort_key(current['reading'])[:2], reading_sort_key(expected['reading'])[:2])

    def test_superseded_entries_are_archived_with_valid_replacements(self):
        for expected in self.report['retired']:
            with self.subTest(entry=expected['entry_id']):
                self.assertNotIn(expected['entry_id'], self.rows)
                self.assertEqual(self.archived[expected['entry_id']], expected)
                self.assertIn(expected['replacement_entry_id'], self.rows)

    def test_distinct_hangul_senses_and_foreign_transcriptions_survive(self):
        for identity, word in [('U+AC00_00', '가ˉ'), ('U+B9E4_00', '매'), ('U+C544_00', '아ˉ'),
                               ('U+AC00_U+C57C_00', '가ˉ야ˆ')]:
            self.assertEqual(self.rows[identity]['hanri'], word)
            self.assertEqual(self.rows[identity]['entry_type'], 'hangul_override')

    def test_approved_variants_do_not_replace_existing_readings(self):
        values = {(row['hanri'], row['reading']) for row in self.rows.values()}
        self.assertTrue({('就', '쥬5'), ('就', '됴5'), ('底', '도2'), ('𨘗', '위'), ('𨘗', '뒤'), ('對', '위')} <= values)
        self.assertNotIn(('就', '도2'), values)

    def test_python_hanri_recognition_includes_extension_e(self):
        marker = load_tone_marker_module()
        self.assertTrue(marker.is_cjk_char('𬦰'))
        self.assertTrue(marker.is_cjk_char('𨘗'))
        self.assertFalse(marker.is_cjk_char('A'))
        self.assertFalse(marker.is_cjk_char('벻'))


if __name__ == '__main__':
    unittest.main()
