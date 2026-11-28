"""Phrase conversion in the desktop engine and Pad (docs/ime-phrase-conversion-plan.md).

The shared cases also run against the web engine in tests/check_phrase_conversion.cjs.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from candidate_preferences import FilePreferenceStore  # noqa: E402

FIXTURE = json.loads((ROOT / 'tests/fixtures/phrase-conversion-cases.json').read_text(encoding='utf-8'))


def load_pad():
    path = ROOT / 'desktop/Hokkien Tangliengim IME Pad.py'
    spec = importlib.util.spec_from_file_location('phrase_pad_check', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PAD = load_pad()
INDEX = PAD.phrase_reading_index(PAD.HANRI_DICT)


def units(typed: str) -> list[str]:
    result = []
    index = 0
    while index < len(typed):
        end, _syllable = PAD.phrase_unit_at(typed, index)
        if typed[end:end + 1] and typed[end] in PAD.TONE_DIGITS:
            end += 1
        result.append(typed[index:end])
        index = end
    return result


def toneless(text: str) -> str:
    return PAD.strip_reading_tones(PAD.normalize_tone_symbols_to_digits(text))


class EngineCases(unittest.TestCase):
    def test_shared_cases(self):
        for case in FIXTURE['cases']:
            with self.subTest(case['name']):
                # The engine splits only what follows the last apostrophe, as the menu does.
                typed = units(case['typed'].split('’')[-1])
                lookup = PAD.phrase_span_lookup(INDEX, typed)
                suffix = next((length for length in range(len(typed), 0, -1)
                               if lookup(len(typed) - length, len(typed))), 0)
                result = None
                if not PAD.is_apostrophe_joined_word(INDEX, case['typed']):
                    result = PAD.phrase_for_run(typed, lookup, suffix)
                found = result and [
                    [part['start_unit'], part['end_unit'], part['entry']['entry_id'] if part['entry'] else None]
                    for part in result['segments']]
                self.assertEqual(found, case['phrase'])

    def test_tie_breaks(self):
        def entry(name, order):
            return {'id': name, 'entry_id': name,
                    'raw': {'reading': chr(0xAC00 + order), 'hanri': name, 'entry_type': 'lexical', 'entry_id': name}}

        def split(count, words):
            lookup = lambda start, end: [words[start, end]] if (start, end) in words else []
            return [(part['start_unit'], part['end_unit'], part['entry'] and part['entry']['id'])
                    for part in PAD.segment_reading_run(['x'] * count, lookup)['segments']]

        self.assertEqual(split(3, {(0, 1): entry('a', 1), (1, 3): entry('bc', 2), (1, 2): entry('b', 3),
                                   (2, 3): entry('c', 4)}), [(0, 1, 'a'), (1, 3, 'bc')], 'fewest words')
        self.assertEqual(split(3, {(0, 2): entry('ab', 1), (2, 3): entry('c', 2), (0, 1): entry('a', 3),
                                   (1, 3): entry('bc', 4)}), [(0, 1, 'a'), (1, 3, 'bc')], 'longest last word')
        self.assertEqual(split(3, {(0, 2): entry('ab', 1), (1, 3): entry('bc', 0)}),
                         [(0, 1, None), (1, 3, 'bc')], 'longest last word with a syllable left over')
        self.assertEqual(split(4, {(0, 1): entry('p', 5), (1, 3): entry('q', 6), (0, 2): entry('r', 1),
                                   (2, 3): entry('s', 9), (3, 4): entry('end', 1)}),
                         [(0, 2, 'r'), (2, 3, 's'), (3, 4, 'end')], 'canonical order from the left')


class PadMenu(unittest.TestCase):
    """The classic Pad driven without a window, as tools/check_adaptive_desktop.py does."""

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.preferences = Path(folder.name) / 'preferences.json'
        pad = PAD.HokkienIMEPad.__new__(PAD.HokkienIMEPad)
        pad.output_tones_on = SimpleNamespace(get=lambda: False)
        pad.input_mode = SimpleNamespace(get=lambda: 'hangul')
        pad.ime_on = SimpleNamespace(get=lambda: True)
        pad.hanri_on = SimpleNamespace(get=lambda: True)
        pad.suppressed_hanri_contexts = set()
        pad.chosen_hangul_prefixes = []
        pad.hanri_instance_readings = []
        pad.hanri_instance_text_snapshot = ''
        pad.lomari_raw = ''
        pad.lomari_start_snapshot = None
        pad.candidate = None
        pad.candidate_index = 0
        pad.candidate_selection_explicit = False
        identities = {PAD.dictionary_ranking_api().source_id(entry)
                      for entries in PAD.HANRI_DICT.values() for entry in entries}
        pad._candidate_preference_store = FilePreferenceStore(identities, self.preferences)
        self.undo = []
        pad.push_undo_state = lambda: self.undo.append(pad.composer.text())
        pad.reset_lomari_buffer = lambda: (setattr(pad, 'lomari_raw', ''),
                                           setattr(pad, 'lomari_start_snapshot', None))
        pad.close_candidate_popup = lambda *args: setattr(pad, 'candidate', None)
        pad.refresh_candidate_popup_text = lambda: None
        pad.render = lambda: None
        self.pad = pad

    def open_menu(self, text: str, before: str = ''):
        pad = self.pad
        pad.composer = PAD.Composer(output=before + text, cursor_pos=len(before + text))
        menu = pad.find_hanri_candidate()
        pad.candidate = menu and pad.adapt_candidate_menu(menu)
        pad.candidate_index = 0
        pad.candidate_selection_explicit = False
        return pad.candidate

    def press(self, key: str, char: str = ''):
        return self.pad.handle_candidate_key(key, char)

    def space(self, typed: str) -> str:
        if self.open_menu(typed):
            self.press('space', ' ')
        else:
            self.pad.composer.insert_literal(' ')
        return self.pad.composer.text()

    def test_shared_cases_in_the_menu(self):
        for case in FIXTURE['cases']:
            with self.subTest(case['name']):
                self.pad.chosen_hangul_prefixes = []
                menu = self.open_menu(case['typed'])
                if not case['phrase']:
                    self.assertFalse(menu and menu.get('phrase'))
                    continue
                self.assertEqual(menu['choices'][0], case['text'], 'the phrase is the first choice')
                self.assertEqual([part['entry'] and part['entry']['entry_id'] for part in menu['phrase']['segments']],
                                 [identity for _start, _end, identity in case['phrase']])
                self.assertEqual(len(menu['choices']), len(menu['labels']))
                self.assertEqual(menu['choices'].count(case['text']), 1)
        self.assertFalse(self.preferences.exists(), 'Showing menus must not learn')

    def test_word_menu_is_unchanged_below_the_phrase(self):
        text = '킈쟣븡'
        menu = self.open_menu(text)
        self.pad.composer = PAD.Composer(output=text, cursor_pos=len(text))
        words = self.pad.adapt_candidate_menu(self.pad.find_word_candidate())
        self.assertEqual(menu['choices'], ['去食飯', *words['choices']])
        self.assertEqual(menu['labels'][0], '1  去食飯  킈 쟣븡ˉ')

    def test_the_hangul_tones_setting_adds_no_marks_to_a_hangul_word(self):
        self.pad.output_tones_on = SimpleNamespace(get=lambda: True)  # the Pad's default
        self.assertEqual(self.open_menu('꽈킈쟣븡')['choices'][0], '꽈去食飯')
        self.press('Return')
        self.assertEqual(self.pad.composer.text(), '꽈去食飯')
        typed = f'꽈{PAD.INTERNAL_TONE_MARKS["2"]}'
        self.pad.chosen_hangul_prefixes = []
        self.assertEqual(self.space(f'{typed}킈쟣븡'), f'{typed}去食飯 ', 'a typed tone stays')

    def test_enter_writes_each_word_and_learns_nothing(self):
        self.open_menu('킈쟣븡')
        self.press('Return')
        self.assertEqual(self.pad.composer.text(), '去食飯')
        self.assertEqual(self.pad.composer.display_cursor_pos(), 3)
        self.assertEqual(
            [(item['start'], item['end'], item['hanri'], item['reading'], item['entry_id'])
             for item in self.pad.hanri_instance_readings],
            [(0, 1, '去', '킈', 'U+53BB_00'), (1, 3, '食飯', '쟣븡5', 'U+98DF_U+98EF_00')])
        self.assertEqual(self.undo, ['킈쟣븡'])
        self.assertFalse(self.preferences.exists())

    def test_a_clicked_phrase_learns_nothing(self):
        self.open_menu('킈쟣븡')
        self.pad.commit_candidate(0, explicit=True)
        self.assertEqual(self.pad.composer.text(), '去食飯')
        self.assertFalse(self.preferences.exists())

    def test_shared_space_cases(self):
        for typed, written in FIXTURE['space']:
            with self.subTest(typed):
                self.pad.chosen_hangul_prefixes = []
                self.pad.suppressed_hanri_contexts = set()
                result = self.space(typed)
                self.assertTrue(result.endswith(' '))
                self.assertEqual(toneless(result[:-1]), written)
        self.assertFalse(self.preferences.exists(), 'Space teaches nothing')

    def test_space_takes_the_first_candidate_not_the_highlighted_one(self):
        self.open_menu('시')
        self.press('Tab')
        self.press('Tab')
        self.press('space', ' ')
        self.assertEqual(self.pad.composer.text(), '是 ')
        self.assertEqual(self.undo, ['시'], 'one undo step covers the conversion and the space')
        self.assertFalse(self.preferences.exists())

    def test_space_follows_learned_choices(self):
        self.pad.candidate_preference_store().record('래', 'U+2019_U+B798_00')
        for _ in range(3):
            self.pad.candidate_preference_store().record('래', 'U+2019_U+B798_00')
        self.assertEqual(self.space('래'), '’래 ')

    def test_escape_and_right_keep_the_hangul(self):
        for key in ('Escape', 'Right'):
            with self.subTest(key):
                self.open_menu('킈쟣븡')
                self.press(key)
                self.assertIsNone(self.pad.candidate)
                self.assertIsNone(self.press('space', ' '), 'with no menu, Space is ordinary typing')
                self.assertEqual(self.pad.composer.text(), '킈쟣븡')

    def test_written_hanri_and_chosen_hangul_are_not_split_again(self):
        self.open_menu('킈쟣븡')
        self.press('Return')
        menu = self.open_menu('킈감샤', before='去食飯')
        self.assertEqual(menu['choices'][0], '去感謝')
        self.assertEqual(menu['phrase']['start'], 3)
        self.press('Return')
        self.assertEqual(self.pad.composer.text(), '去食飯去感謝')
        self.assertEqual([item['hanri'] for item in self.pad.hanri_instance_readings],
                         ['去', '食飯', '去', '感謝'])

        # Keeping 쟣븡 in Hangul from the menu settles it.
        self.pad.suppressed_hanri_contexts = set()
        self.open_menu('쟣븡')
        self.press('Return')
        self.assertEqual(self.pad.composer.text(), '쟣븡')
        menu = self.open_menu('킈', before='쟣븡')
        self.assertFalse(menu.get('phrase'))
        self.press('space', ' ')
        self.assertEqual(self.pad.composer.text(), '쟣븡去 ')

    def test_text_after_the_cursor_stays(self):
        self.pad.composer = PAD.Composer(output='킈쟣븡。', cursor_pos=3)
        self.pad.candidate = self.pad.adapt_candidate_menu(self.pad.find_hanri_candidate())
        self.press('space', ' ')
        self.assertEqual(self.pad.composer.text(), '去食飯 。')

    def test_lomari_pronoun_is_committed_before_the_space(self):
        pad = self.pad
        pad.input_mode = SimpleNamespace(get=lambda: 'lomari')
        pad.lomari_key_style = SimpleNamespace(get=lambda: PAD.LOMARI_KEY_STYLE_STANDARD)
        pad.e_to_ye_autocorrect_on = SimpleNamespace(get=lambda: False)
        pad.composer = PAD.Composer()
        pad.lomari_start_snapshot = pad.composer_snapshot()
        pad.lomari_raw = 'li'
        pad.composer.insert_literal(PAD.convert_lomari_raw_to_hangul('li'))
        menu = pad.find_hanri_candidate()
        self.assertTrue(menu)
        pad.candidate = pad.adapt_candidate_menu(menu)
        self.press('space', ' ')
        expected = PAD.convert_lomari_raw_to_hangul('lI', lomari_key_style=PAD.LOMARI_KEY_STYLE_STANDARD)
        result = pad.composer.text()
        self.assertTrue(result.endswith(' '))
        self.assertEqual(toneless(result[:-1]), toneless(expected))
        self.assertEqual(pad.lomari_raw, '')


if __name__ == '__main__':
    unittest.main()
