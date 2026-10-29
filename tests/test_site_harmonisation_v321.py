"""Protect the reviewed v3.2.1 assignments and their authored readings."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from content_harmonisation import apply_edits, atoms_for, restore_followups
from harmonise_content_v321 import SPELLINGS, propose, restore
from dictionary_editor_service import read_table


def record(body):
    return {"type": "stories", "route": "/read/stories/the-egg/", "body": body}


class PatchTests(unittest.TestCase):
    def test_all_assignments_preserve_readings(self):
        before = record('<p>오ˉ로ˋ 다ˉ버ˆ 자ˉ뻐ˋ 뻐ˋ 에당 𣍐당 텧ˆ</p>')
        edits = propose(before)
        self.assertEqual(len(edits), 7)
        self.assertEqual([edit["hanri"] for edit in edits], list(SPELLINGS.values()))
        after = apply_edits(before["body"], edits)
        self.assertEqual("".join(a.reading for a in atoms_for(before)),
                         "".join(a.reading.rstrip('-') for a in atoms_for(record(after))))

    def test_ruby_neutral_domains_and_foreign_words_unchanged(self):
        body = '<p><ruby>字<rt>뻐ˋ</rt></ruby> ’뻐 에당. 젝뻐띠 남ᄈힻ트띠</p>'
        after = apply_edits(body, propose(record(body)))
        self.assertIn('<ruby>字<rt>뻐ˋ</rt></ruby> ’뻐 ', after)
        self.assertIn(' 젝뻐띠 남ᄈힻ트띠', after)
        self.assertIn('>會當<', after)

    def test_reviewed_pages_are_reversible_and_urls_unchanged(self):
        path = ROOT / 'docs/harmonisation-3.2.1-audit.json'
        if not path.exists():
            self.skipTest('Migration has not been applied')
        for file, entry in json.loads(path.read_text(encoding='utf-8'))['records'].items():
            with self.subTest(file=file):
                current = json.loads((ROOT / file).read_text(encoding='utf-8'))
                previous = restore(current['body'], entry)
                # Reading preservation applies to the original v3.2.1 patch;
                # later author-approved corrections have their own exact hashes.
                reviewed = restore_followups(current['body'], entry)
                self.assertEqual(''.join(atom.reading.rstrip('-') for atom in atoms_for(record(previous))),
                                 ''.join(atom.reading.rstrip('-') for atom in atoms_for(record(reviewed))))
                self.assertEqual(current['route'], entry['route'])
                self.assertFalse(propose(current))

    def test_old_active_hangul_headwords_are_retired(self):
        rows = read_table((ROOT / 'data/hokkien_hanri_dict.tsv').read_bytes())[1]
        old = {'U+BED0_00', 'U+C5D0_U+B2F9_00', 'U+C790_U+BED0_00', 'U+23350_U+B2F9_00'}
        self.assertFalse(old & {row['entry_id'] for row in rows})
        for word in SPELLINGS.values():
            self.assertTrue(any(row['hanri'] == word for row in rows), word)


if __name__ == '__main__':
    unittest.main()
