"""Simplified aliases must preserve canonical identity, text, and ordering."""

import csv
from pathlib import Path
import unittest

from tools.dictionary_schema import DICTIONARY_COLUMNS
from tools.simplified_lookup import contains_hanri, non_hanri_text, review_case, simplified_field_errors, simplified_headword
from tools.tangliengim_collation import row_sort_key


ROOT = Path(__file__).resolve().parents[1]


class SimplifiedLookupTests(unittest.TestCase):
    def test_common_and_contextual_conversion(self):
        for original, expected in (
            ('臺灣', '台湾'), ('德國', '德国'), ('頭髮', '头发'),
            ('發展', '发展'), ('著作', '著作'), ('身著', '身着'),
            ('乾燥', '干燥'), ('乾坤', '乾坤'),
        ):
            self.assertEqual(simplified_headword(original), expected)

    def test_mixed_scripts_and_obscure_characters(self):
        source = '𤆬臺灣’ᄋᅷˆ뽀ˊ-!?3a😀㩼䭕'
        target = '𤆬台湾’ᄋᅷˆ뽀ˊ-!?3a😀㩼䭕'
        self.assertEqual(simplified_headword(source), target)
        self.assertEqual(non_hanri_text(source), non_hanri_text(target))
        self.assertEqual(simplified_field_errors(source, target), [])
        self.assertTrue(simplified_field_errors(source, target.replace('뽀', '보')))
        self.assertEqual(simplified_headword('ᄋᅷˆ뽀ˊ'), '')
        self.assertEqual(simplified_headword('123'), '')

    def test_review_ignores_secondary_glyphs_and_traditional_alternatives(self):
        chosen = simplified_headword('肉乾')
        review = review_case('肉乾', chosen)
        self.assertEqual(chosen, '肉干')
        self.assertIsNone(review)
        for headword in ('甘願', '開', '麵線', '買票', '彷徨'):
            self.assertIsNone(review_case(headword, simplified_headword(headword)))
        for headword in ('定著', '著', '著痧', '身著', '心狂火著', '음著', '火著'):
            self.assertIsNone(review_case(headword, simplified_headword(headword)))

    def test_every_source_row_and_sort_key(self):
        with (ROOT / 'data/hokkien_hanri_dict.tsv').open(encoding='utf-8', newline='') as stream:
            rows = [row for row in csv.DictReader(stream, delimiter='\t') if not row['reading'].startswith('#')]
        self.assertEqual(len(rows), 2745)
        self.assertEqual(sum(contains_hanri(row['hanri']) for row in rows), 2674)
        for row in rows:
            self.assertEqual(simplified_field_errors(row['hanri'], row['simplified']), [], row['entry_id'])
            changed = {**row, 'simplified': 'arbitrary lookup metadata'}
            self.assertEqual(row_sort_key(row, DICTIONARY_COLUMNS), row_sort_key(changed, DICTIONARY_COLUMNS))

    def test_missing_and_unnecessary_aliases(self):
        self.assertTrue(simplified_field_errors('臺灣', ''))
        self.assertTrue(simplified_field_errors('가', '가'))
        self.assertTrue(simplified_field_errors('臺가灣', '台灣가'))


if __name__ == '__main__':
    unittest.main()
