"""Protect reviewed script choices, authored readings, and source provenance."""

import json
import sys
import unittest
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from content_harmonisation import apply_edits, atoms_for, digest, propose, restore_body
from harmonise_content_v32 import active_records, verify
from song_title_readings import reading_units
from tangliengim_collation import TONE_TO_DIGIT


def record(body):
    return {"body": body, "type": "stories", "route": "/read/stories/the-egg/"}


def readings(value):
    result = []
    for atom in atoms_for(value):
        if atom.kind in {"hangul", "ruby"}:
            result.extend(unicodedata.normalize("NFC", unit.translate(TONE_TO_DIGIT))
                          for unit in reading_units(atom.reading))
    return result


class HarmonisationTests(unittest.TestCase):
    def convert(self, body):
        edits, _ = propose(record(body))
        return apply_edits(body, edits)

    def test_neutral_domain_crosses_tags_but_ends_at_boundary(self):
        source = '<p>等’<b>짇</b>에, 뽀우</p>'
        result = self.convert(source)
        self.assertIn('等’<b>짇</b>에, ', result)
        self.assertIn('>無<', result)
        self.assertIn('>有<', result)

    def test_existing_ruby_is_not_reinterpreted(self):
        source = '<p><ruby>物<rt>밓ˆ</rt></ruby> 뽀</p>'
        self.assertIn('<ruby>物<rt>밓ˆ</rt></ruby>', self.convert(source))

    def test_entity_apostrophe_and_explicit_line_break(self):
        result = self.convert('<p>等&#8217;짇에<br>뽀</p>')
        self.assertIn('等&#8217;짇에<br>', result)
        self.assertIn('>無<', result)

    def test_tone_wrapper_moves_to_reading_without_recalculating(self):
        source = '<p><ruby style="position: relative">뽀<rt style="font-size:120%">ˏ</rt></ruby>好</p>'
        result = self.convert(source)
        self.assertIn('>無<', result)
        self.assertIn('>뽀ˊ-</rt>', result)
        self.assertEqual(readings(record(source)), readings(record(result)))

    def test_contexts_and_protected_compounds(self):
        result = self.convert('<p>去시아껳 덱시 오도빼 看매 애매 안니 간나 샹 뻐</p>')
        self.assertIn('시아껳 덱시 오도빼', result)
        self.assertIn('>覓<', result)
        self.assertIn(' 애매 안니 간나 샹 뻐', result)

    def test_user_spellings_and_compound_members_are_all_converted(self):
        result = self.convert('<p>일아 촿 똬니 真正핳徦欲死 來벻上天</p>')
        for hanri in ('嬰', '仔', '掣', '偌', '邇', '哈', '𬦰'):
            self.assertIn('>'+hanri+'<', result)

    def test_source_and_destination_are_not_confused(self):
        result = self.convert('<p>위什物 위一个所在 欲위底去 뒤少年</p>')
        self.assertIn('>為<', result)
        self.assertIn('>𨘗<', result)
        self.assertIn('>對<', result)

    def test_which_is_not_regional_then(self):
        result = self.convert('<p>應該是도ˋ 一个小學’에 老師</p>')
        self.assertIn('>底<', result)
        self.assertNotIn('>就<', result)

    def test_free_and_bound_demonstratives_differ(self):
        result = self.convert('<p>제 是꽈 짇兩世人 헤 是꽈 힏縛著’에 鐵鏈</p>')
        self.assertIn('제 是꽈 ', result)
        self.assertIn('>這<', result)
        self.assertIn(' 헤 是꽈 ', result)
        self.assertIn('>彼<', result)
        self.assertEqual(self.convert('<p>제兩世人 헤縛著</p>'), '<p>제兩世人 헤縛著</p>')

    def test_reversible_ledger_rejects_unreviewed_changes(self):
        before = '<p>뽀우</p>'
        edits, _ = propose(record(before))
        after = apply_edits(before, edits)
        entry = {'beforeSha256': digest(before), 'afterSha256': digest(after), 'edits': edits}
        self.assertEqual(restore_body(after, entry), before)
        with self.assertRaises(ValueError):
            restore_body(after+'!', entry)

    def test_all_authored_languages_and_readings_survive(self):
        path = ROOT / 'docs/harmonisation-3.2-audit.json'
        if not path.exists():
            self.skipTest('Run the reviewed content migration first')
        ledger = json.loads(path.read_text(encoding='utf-8'))
        active = {item['file'] for item, _ in active_records(ROOT)}
        self.assertEqual(set(ledger['records']), active)
        self.assertEqual(verify(ROOT, ledger), len(active))
        for file, entry in ledger['records'].items():
            with self.subTest(file=file):
                current = json.loads((ROOT / file).read_text(encoding='utf-8'))
                before = {**current, 'body': restore_body(current['body'], entry)}
                if current['id'] == 'song-727':
                    # The parallel source verse supplies the missing alternate-verse pronoun reading.
                    self.assertEqual(before['body'].count('阮'), 1)
                    before['body'] = before['body'].replace('阮', '꾼`', 1)
                self.assertEqual(readings(before), readings(current))
                self.assertEqual(current['orthography']['target'], '3.2')


if __name__ == '__main__':
    unittest.main()
