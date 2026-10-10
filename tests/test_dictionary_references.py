"""Exodus III exact-record relationships, independent of rows and labels."""
import csv
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.dictionary_references import CATEGORY_COLUMNS, load_categories, record_index, require_record
from tools.dictionary_ranking import read_records

ROOT = Path(__file__).resolve().parents[1]


class RecordReferenceTests(unittest.TestCase):
    def setUp(self):
        self.records = [dict(hanri='底', reading=reading, corrected='', entry_type='lexical',
                             entry_id=f'U+5E95_{ordinal:02}')
                        for ordinal, reading in enumerate(('되2', '도2'))]

    def categories(self, rows, header=CATEGORY_COLUMNS):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / 'dictionary_categories.tsv'
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream, delimiter='\t', lineterminator='\r\n')
            writer.writerow(header)
            writer.writerows(rows)
        return path

    def test_same_headword_and_reordered_rows_are_independent(self):
        path = self.categories([['first', 'First', '底', 'U+5E95_00'],
                                ['second', 'Second', '底', 'U+5E95_01']])
        expected = {'U+5E95_00': ['first'], 'U+5E95_01': ['second']}
        self.assertEqual(load_categories(path, self.records)[1], expected)
        self.assertEqual(load_categories(path, self.records[::-1])[1], expected)
        index = record_index(self.records[::-1])
        self.assertEqual(require_record(index, 'U+5E95_00')['reading'], '되2')
        self.assertEqual(require_record(index, 'U+5E95_01')['reading'], '도2')

    def test_id_relationship_survives_display_change_and_label_is_checked(self):
        changed = [{**self.records[0], 'hanri': 'Updated display'}, self.records[1]]
        self.assertEqual(require_record(record_index(changed), 'U+5E95_00')['hanri'], 'Updated display')
        stale = self.categories([['test', 'Test', '底', 'U+5E95_00']])
        with self.assertRaisesRegex(ValueError, 'stale entry label'):
            load_categories(stale, changed)
        updated = self.categories([['test', 'Test', 'Updated display', 'U+5E95_00']])
        self.assertEqual(load_categories(updated, changed)[1], {'U+5E95_00': ['test']})

    def test_stale_id_never_falls_back_to_matching_headword(self):
        for identity in ('U+5E95_99', '', '底', 'U+5E95_00-sandhi'):
            with self.subTest(identity=identity), self.assertRaises(ValueError):
                load_categories(self.categories([['test', 'Test', '底', identity]]), self.records)
        inactive = [{**self.records[0], 'entry_type': 'number_pronunciation'}]
        with self.assertRaisesRegex(ValueError, 'inactive'):
            require_record(record_index(inactive), 'U+5E95_00')

    def test_source_structure_and_duplicate_memberships_are_validated(self):
        row = ['test', 'Test', '底', 'U+5E95_00']
        for rows in ([row, row], [row[:-1]], [row + ['extra']],
                     [['test ', *row[1:]]], [['test', '가', *row[2:]]],
                     [row, ['test', 'Other', '底', 'U+5E95_01']]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                load_categories(self.categories(rows), self.records)
        with self.assertRaises(ValueError):
            load_categories(self.categories([row], ['category', 'label', 'hanri', 'entry_id']), self.records)
        with self.assertRaisesRegex(ValueError, 'Duplicate structural'):
            record_index([self.records[0], self.records[0]])

    def test_real_category_relationships_are_row_independent(self):
        records = read_records(ROOT / 'data/hokkien_hanri_dict.tsv')
        path = ROOT / 'data/dictionary_categories.tsv'
        expected = load_categories(path, records)
        self.assertEqual(load_categories(path, records[::-1]), expected)
        self.assertEqual(sum(map(len, expected[1].values())), 178)
        for identity in ('U+725B_U+5976_00', 'U+725B_U+5976_01', 'U+5976_00', 'U+5976_01'):
            self.assertEqual(expected[1][identity], ['food'])
        for identity in ('U+9577_U+6CF0_00', 'U+9577_U+6CF0_01',
                         'U+65B0_U+52A0_U+5761_00', 'U+65B0_U+52A0_U+5761_01'):
            self.assertEqual(expected[1][identity], ['place-names'])


class PadRecordReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environment = patch.dict(os.environ, {
            'HOKKIEN_GITHUB_REPO_PATH': str(ROOT),
            'HOKKIEN_HANRI_DICT_PATH': str(ROOT / 'data/hokkien_hanri_dict.tsv'),
        })
        cls.environment.start()
        cls.addClassCleanup(cls.environment.stop)
        path = Path(os.environ.get('HOKKIEN_REFERENCE_PAD_PATH', str(ROOT / 'desktop/Hokkien Tangliengim IME Pad.py')))
        spec = importlib.util.spec_from_file_location('reference_pad_check', path)
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def test_bridge_preserves_exact_identity_and_literal_spans(self):
        records = record_index(read_records(ROOT / 'data/hokkien_hanri_dict.tsv'))
        for identity in ('U+5E95_00', 'U+5E95_01'):
            self.assertEqual(self.module.selected_record_reference({'entryId': identity}, records),
                             {'entry_id': identity})
        self.assertEqual(self.module.selected_record_reference({'hanri': '底', 'reading': '되2'}, records), {})
        for identity in ('U+5E95_99', '', None):
            with self.subTest(identity=identity), self.assertRaises(ValueError):
                self.module.selected_record_reference({'entryId': identity, 'hanri': '底'}, records)

    def test_annotation_identity_survives_text_movement(self):
        pad = self.module.HokkienIMEPad.__new__(self.module.HokkienIMEPad)
        pad.composer = self.module.Composer(output='底', cursor_pos=1)
        pad.hanri_instance_readings = []
        pad.hanri_instance_text_snapshot = '底'
        pad.remember_hanri_instance_reading(0, '底', '도2', entry_id='U+5E95_01')
        pad.composer.output = '前底'
        pad.sync_hanri_instance_readings()
        self.assertEqual(pad.hanri_instance_readings[0]['entry_id'], 'U+5E95_01')
        self.assertEqual(pad.hanri_instance_readings[0]['start'], 1)

    def test_popup_uses_source_identity_not_labels_or_array_position(self):
        pad = self.module.HokkienIMEPad.__new__(self.module.HokkienIMEPad)
        first = dict(prefix='', suffix='', reading='가', matched_text='가', choices=['底', '底'],
                     labels=['1  same', '2  same'], choice_readings=['가', '가'],
                     choice_auto_sandhi=[False, False],
                     choice_entries=[{'entry_id': 'U+5E95_00'}, {'entry_id': 'U+5E95_01'}])
        pad.candidate = first
        pad.candidate_index = 1
        pad.candidate_selection_explicit = True
        swapped = {**first, 'choice_entries': first['choice_entries'][::-1]}
        pad.find_hanri_candidate = lambda **kwargs: swapped
        pad.adapt_candidate_menu = lambda menu: menu
        calls = []
        pad.show_candidate_popup = lambda: calls.append('shown')
        pad.maybe_show_hanri_candidates()
        self.assertEqual(calls, ['shown'])
        self.assertEqual(pad.candidate_index, 0)
        self.assertTrue(pad.candidate_selection_explicit)
        replacement = {**swapped, 'choice_entries': [{'entry_id': 'U+5E95_00'}, {'entry_id': 'U+5E95_02'}]}
        pad.find_hanri_candidate = lambda **kwargs: replacement
        pad.maybe_show_hanri_candidates()
        self.assertFalse(pad.candidate_selection_explicit)
        self.assertEqual(pad.candidate_index, 0)


if __name__ == '__main__':
    unittest.main()
