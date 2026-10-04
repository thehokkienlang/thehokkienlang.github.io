"""Mandarin metadata and source-only inheritance do not change lexical identity."""

import csv
import json
from pathlib import Path
import unittest

from tools.complete_mandarin_lookup import completed_rows, review_report
from tools.dictionary_schema import DICTIONARY_COLUMNS, is_comment_row, resolve_dictionary_record
from tools.tangliengim_collation import row_sort_key

ROOT = Path(__file__).resolve().parents[1]


class MandarinLookupTests(unittest.TestCase):
    def test_canonical_header_and_comment_columns(self):
        self.assertEqual(DICTIONARY_COLUMNS, (
            'hanri', 'simplified', 'reading', 'mandarin_trad', 'mandarin_simp',
            'english', 'corrected', 'entry_type', 'entry_id',
        ))
        self.assertTrue(is_comment_row(['# section']))
        self.assertTrue(is_comment_row(['', '', '# original reading comment']))

    def test_all_inheritance_rules_and_blank(self):
        self.assertEqual(resolve_dictionary_record(dict(hanri='世界', simplified='〃', mandarin_trad='〃', mandarin_simp='〃')),
                         dict(hanri='世界', simplified='世界', mandarin_trad='世界', mandarin_simp='世界'))
        resolved = resolve_dictionary_record(dict(hanri='家己', simplified='〃', mandarin_trad='自己', mandarin_simp='〃'))
        self.assertEqual(resolved['mandarin_simp'], '自己')
        blank = resolve_dictionary_record(dict(hanri='가', simplified='', mandarin_trad='', mandarin_simp=''))
        self.assertEqual(blank['simplified'], '')
        self.assertEqual(blank['mandarin_trad'], '')

    def test_invalid_inheritance(self):
        for record in (
            dict(hanri='〃'), dict(hanri='', simplified='〃'),
            dict(hanri='家', mandarin_trad='', mandarin_simp='〃'),
            dict(hanri='家', english='〃'), dict(hanri='家', simplified='家〃'),
            dict(hanri='家', mandarin_trad='', mandarin_simp='自己'),
        ):
            with self.assertRaises(ValueError):
                resolve_dictionary_record(record)

    def test_metadata_does_not_affect_sorting_or_identity(self):
        record = dict(hanri='家己', reading='가1기5', corrected='',
                      english='oneself', entry_type='lexical', entry_id='U+5BB6_U+5DF1_00')
        enriched = {**record, 'simplified': '〃', 'mandarin_trad': '自己', 'mandarin_simp': '〃'}
        self.assertEqual(row_sort_key(record, DICTIONARY_COLUMNS), row_sort_key(enriched, DICTIONARY_COLUMNS))
        self.assertEqual(resolve_dictionary_record(enriched)['entry_id'], record['entry_id'])

    def test_runtime_metadata_and_indexes(self):
        data = json.loads((ROOT / 'public/data/hokkien-hanri-dict.json').read_text(encoding='utf-8'))
        with (ROOT / 'data/hokkien_hanri_dict.tsv').open(encoding='utf-8', newline='') as handle:
            rows = {row['entry_id']: resolve_dictionary_record(row) for row in csv.DictReader(handle, delimiter='\t') if row['entry_id']}
        self.assertEqual(data['columns'], list(DICTIONARY_COLUMNS))
        for entry in data['entries']:
            source_id = entry['raw']['entry_id']
            if source_id not in rows:
                continue
            for name in ('simplified', 'mandarin_trad', 'mandarin_simp'):
                self.assertEqual(entry[name], rows[source_id][name])
                self.assertNotIn('〃', entry[name])
                self.assertEqual(entry['raw'][name], rows[source_id][name])
        for name in ('byMandarinTrad', 'byMandarinSimp', 'bySimplified'):
            self.assertNotIn('〃', data['indexes'][name])
        for name in ('byMandarinTrad', 'byMandarinSimp'):
            self.assertIn('U+5BB6_U+5DF1_00', data['indexes'][name]['自己'])
        self.assertIn('U+4ECA_U+4ED4_U+65E5_00', data['indexes']['byMandarinTrad']['今天'])

    def test_second_pass_searches_keep_source_identity(self):
        data = json.loads((ROOT / 'public/data/hokkien-hanri-dict.json').read_text(encoding='utf-8'))
        for trad, simp, headword in (
            ('計較', '计较', '計較'), ('繼續', '继续', '繼續'),
            ('鑰匙', '钥匙', '鎖匙'), ('去年', '去年', '舊年'),
        ):
            source_ids = {entry['id'] for entry in data['entries'] if entry['hanri'] == headword and not entry.get('autoSandhi')}
            self.assertTrue(source_ids)
            self.assertTrue(source_ids <= set(data['indexes']['byMandarinTrad'][trad]))
            self.assertTrue(source_ids <= set(data['indexes']['byMandarinSimp'][simp]))

    def test_reviewed_english_corrections_reach_runtime_and_metadata(self):
        audit = json.loads((ROOT / 'docs/english-gloss-corrections.json').read_text(encoding='utf-8'))['corrections']
        data = json.loads((ROOT / 'public/data/hokkien-hanri-dict.json').read_text(encoding='utf-8'))
        with (ROOT / 'data/hokkien_hanri_dict.tsv').open(encoding='utf-8', newline='') as handle:
            rows = {row['entry_id']: row for row in csv.DictReader(handle, delimiter='\t') if row['entry_id']}
        for change in audit:
            source_id = change['entry_id']
            self.assertEqual(rows[source_id]['english'], change['new_english'])
            self.assertEqual(rows[source_id]['hanri'], change['hanri'])
            self.assertEqual(rows[source_id]['reading'], change['reading'])
            related = [entry for entry in data['entries'] if entry['raw']['entry_id'] == source_id]
            self.assertTrue(related)
            for entry in related:
                self.assertEqual(entry['english'], change['new_english'])
                self.assertEqual(entry['raw']['english'], change['new_english'])
        kilometre = rows['U+516C_U+91CC_00']
        self.assertEqual(kilometre['english'], 'kilometre')
        self.assertEqual(kilometre['mandarin_trad'], '〃')
        self.assertEqual(kilometre['mandarin_simp'], '〃')
        self.assertIn(kilometre['entry_id'], data['indexes']['byMandarinTrad']['公里'])

    def test_completed_manual_reviews_preserve_identity_and_bound_component(self):
        report = json.loads((ROOT / 'docs/mandarin-manual-review-completion.json').read_text(encoding='utf-8'))
        with (ROOT / 'data/hokkien_hanri_dict.tsv').open(encoding='utf-8', newline='') as handle:
            rows = {row['entry_id']: row for row in csv.DictReader(handle, delimiter='\t') if row['entry_id']}
        merged_ids = {item['entry_id'] for item in report['merged']}
        remaining_ids = {item['entry_id'] for item in report['remaining']}
        self.assertTrue(merged_ids.isdisjoint(remaining_ids))
        for item in report['merged']:
            row = rows[item['entry_id']]
            self.assertEqual(row['hanri'], item['hanri'])
            self.assertEqual(row['reading'], item['reading'])
            for field, value in item['after'].items():
                self.assertEqual(row[field], value)
            resolved = resolve_dictionary_record(row)
            self.assertTrue(resolved['mandarin_trad'])
            self.assertTrue(resolved['mandarin_simp'])
        self.assertIn('U+87EE_00', remaining_ids)
        self.assertEqual(rows['U+87EE_00']['english'], '')
        self.assertEqual(rows['U+87EE_00']['mandarin_trad'], '')
        self.assertEqual(resolve_dictionary_record(rows['U+63DE_U+8170_00'])['mandarin_trad'], '彎腰')
        self.assertEqual(resolve_dictionary_record(rows['U+82A1_U+82B3_00'])['mandarin_trad'], '爆香')

    def test_second_pass_is_blank_only_and_idempotent(self):
        record = dict.fromkeys(DICTIONARY_COLUMNS, '')
        record.update(hanri='繼續', simplified='继续', reading='게2셕1', english='continue; inherit',
                      entry_type='lexical', entry_id='U+7E7C_U+7E8C_00')
        decision = {**record, 'confidence': 'MEDIUM', 'mandarin_trad': '繼續', 'reason': 'Reviewed semantic equivalent'}
        rows = [list(DICTIONARY_COLUMNS), [record[name] for name in DICTIONARY_COLUMNS]]
        updated = completed_rows(rows, [decision])
        resolved = dict(zip(DICTIONARY_COLUMNS, updated[1]))
        self.assertEqual(resolved['mandarin_trad'], '〃')
        self.assertEqual(resolved['mandarin_simp'], '继续')
        for name in DICTIONARY_COLUMNS:
            if name not in ('mandarin_trad', 'mandarin_simp'):
                self.assertEqual(record[name], resolved[name])
        self.assertEqual(completed_rows(updated, [decision]), updated)
        conflicting = [list(row) for row in updated]
        conflicting[1][DICTIONARY_COLUMNS.index('mandarin_trad')] = '接續'
        with self.assertRaises(ValueError):
            completed_rows(conflicting, [decision])
        changed_source = [list(row) for row in rows]
        changed_source[1][DICTIONARY_COLUMNS.index('reading')] = '가'
        with self.assertRaises(ValueError):
            completed_rows(changed_source, [decision])

    def test_second_pass_medium_is_populated_not_manual_review(self):
        decision = dict(line=1, entry_id='U+7E7C_U+7E8C_00', hanri='繼續', reading='게2셕1',
                        entry_type='lexical', english='continue; inherit', confidence='MEDIUM',
                        mandarin_trad='繼續', reason='Compatible whole-word sense; wording differs')
        report, counts = review_report([decision])
        self.assertEqual(counts['MEDIUM'], 1)
        self.assertEqual(counts.get('LOW', 0), 0)
        self.assertEqual(counts['new_trad_ditto'], 1)
        self.assertIn('Manual review - LOW confidence only', report)

    def test_second_pass_unresolved_and_inapplicable_stay_blank(self):
        record = dict.fromkeys(DICTIONARY_COLUMNS, '')
        record.update(hanri='蟮', reading='솬4', entry_type='lexical', entry_id='U+87EE_00')
        rows = [list(DICTIONARY_COLUMNS), [record[name] for name in DICTIONARY_COLUMNS]]
        for confidence in ('LOW', 'NOT_APPLICABLE'):
            decision = {**record, 'confidence': confidence, 'mandarin_trad': ''}
            self.assertEqual(completed_rows(rows, [decision]), rows)
        for decisions in ([{**record, 'confidence': 'HIGH', 'mandarin_trad': ''}],
                          [{**record, 'confidence': 'LOW', 'mandarin_trad': '蛇'}]):
            with self.assertRaises(ValueError):
                completed_rows(rows, decisions)


if __name__ == '__main__':
    unittest.main()
