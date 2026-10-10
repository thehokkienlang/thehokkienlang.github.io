"""Production readers reject obsolete layouts; builds retain source identity."""

import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.dictionary_schema import DICTIONARY_COLUMNS, PRE_MANDARIN_COLUMNS, require_dictionary_header
from tools.dictionary_ranking import read_records

ROOT = Path(__file__).resolve().parents[1]


class ProductionContractTests(unittest.TestCase):
    def test_exact_header_only(self):
        self.assertEqual(require_dictionary_header(list(DICTIONARY_COLUMNS)), DICTIONARY_COLUMNS)
        for header in (None, PRE_MANDARIN_COLUMNS, DICTIONARY_COLUMNS[:-1],
                       tuple(reversed(DICTIONARY_COLUMNS)), (*DICTIONARY_COLUMNS, 'priority')):
            with self.subTest(header=header), self.assertRaises(ValueError):
                require_dictionary_header(header)

    def test_named_reader_rejects_field_count_and_legacy_layout(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'dictionary.tsv'
            valid = ['家', '〃', '가1', '〃', '〃', 'house', '', 'lexical', 'U+5BB6_00']
            for row in (valid[:-1], valid + ['extra']):
                with target.open('w', encoding='utf-8', newline='') as stream:
                    writer = csv.writer(stream, delimiter='\t', lineterminator='\r\n')
                    writer.writerows([DICTIONARY_COLUMNS, row])
                with self.assertRaisesRegex(ValueError, 'expected 9 fields'):
                    read_records(target)
            target.write_text('reading\thanri\tpriority\r\n가1\t家\t1\r\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Dictionary header'):
                read_records(target)

    def test_local_editor_helpers_do_not_guess_headerless_positions(self):
        spec = importlib.util.spec_from_file_location('exodus_contract_gui', ROOT / 'desktop/hokkien_tone_marker_gui.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'dictionary.tsv'
            target.write_text('가1\t家\t1\r\n', encoding='utf-8')
            with patch.object(module, 'hanri_tsv_candidates', return_value=[target]):
                with self.assertRaisesRegex(ValueError, 'Dictionary header'):
                    module.hanri_reading_entry_exists('家', '가1')
                with self.assertRaisesRegex(ValueError, 'Dictionary header'):
                    module.existing_hanri_readings('家')
                with self.assertRaisesRegex(ValueError, 'Dictionary header'):
                    module.load_hanri_reading_index()

    def test_canonical_check_is_read_only(self):
        original = (ROOT / 'data/hokkien_hanri_dict.tsv').read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'dictionary.tsv'
            target.write_bytes(original)
            registry = target.with_name('dictionary_entry_id_registry.tsv')
            registry.write_bytes((ROOT / 'data/dictionary_entry_id_registry.tsv').read_bytes())
            command = [sys.executable, '-X', 'utf8', str(ROOT / 'tools/sort_dictionary_tsv.py'), str(target), '--check']
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(target.read_bytes(), original)
            rows = list(csv.reader(original.decode('utf-8').splitlines(), delimiter='\t'))
            rows[1], rows[-1] = rows[-1], rows[1]
            with target.open('w', encoding='utf-8', newline='') as stream:
                csv.writer(stream, delimiter='\t', lineterminator='\r\n').writerows(rows)
            unsorted = target.read_bytes()
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('not canonical', result.stdout + result.stderr)
            self.assertEqual(target.read_bytes(), unsorted)

    def test_source_runtime_and_generated_identity_contract(self):
        source = {row['entry_id']: row for row in read_records(ROOT / 'data/hokkien_hanri_dict.tsv')}
        data = json.loads((ROOT / 'public/data/hokkien-hanri-dict.json').read_text(encoding='utf-8'))
        self.assertEqual(data['schemaVersion'], 10)
        self.assertEqual(data['columns'], list(DICTIONARY_COLUMNS))
        originals = {entry['id']: entry for entry in data['entries'] if not entry.get('autoSandhi')}
        self.assertEqual(set(originals), set(source))
        for identity, row in source.items():
            self.assertEqual(originals[identity]['active'], row['entry_type'] != 'number_pronunciation')
        for entry in data['entries']:
            self.assertIn(entry['raw']['entry_id'], source)
            if entry.get('autoSandhi'):
                self.assertEqual(entry['id'], entry['raw']['entry_id'] + '-sandhi')


if __name__ == '__main__':
    unittest.main()
