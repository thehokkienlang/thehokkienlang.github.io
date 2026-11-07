"""Tangliengim pronunciation engine: Hangul readings, tone sandhi, Lomari and audio.

This is the GUI-free core of the desktop IME, moved verbatim out of
"Hokkien Tangliengim IME Pad.py" so the web build can use it without Tkinter.
The IME Pad loads this file from beside itself and re-exports these names.
The Hangul here spells Hokkien (Tangliengim), not Korean.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import os
import re
import sys
import unicodedata
from pathlib import Path


def bundled_resource_path(name: str) -> Path:
    """Return a resource path in source runs or PyInstaller one-file bundles."""
    bundle_dir = getattr(sys, '_MEIPASS', None)
    if bundle_dir:
        return Path(bundle_dir) / name
    return Path(__file__).resolve().with_name(name)


def source_repo_root() -> Path:
    """Return the repo root when running from the source tree."""
    script_dir = Path(__file__).resolve().parent
    if script_dir.name.lower() == 'desktop':
        return script_dir.parent
    return script_dir


def repo_data_path(name: str) -> Path:
    return source_repo_root() / 'data' / name


def github_repo_path_candidates() -> list[Path]:
    """Return likely local checkouts of the website repository."""
    env_path = os.environ.get('HOKKIEN_GITHUB_REPO_PATH')
    candidates = [source_repo_root(), Path.home() / 'Documents' / 'GitHub' / 'thehokkienlang.github.io']
    if env_path:
        candidates.insert(0, Path(env_path))

    unique: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key not in seen:
            unique.append(path)
            seen.add(key)
    return unique


def dictionary_schema_api():
    module = sys.modules.get('dictionary_schema')
    if module is not None:
        return module
    for repo in github_repo_path_candidates():
        directory = repo / 'tools'
        if (directory / 'dictionary_schema.py').is_file():
            if str(directory) not in sys.path:
                sys.path.insert(0, str(directory))
            import dictionary_schema
            return dictionary_schema
    raise FileNotFoundError('Shared dictionary schema not found')


def dictionary_ranking_api():
    dictionary_schema_api()
    import dictionary_ranking
    return dictionary_ranking


def hanri_tsv_path_candidates() -> list[Path]:
    """Use the repository dictionary, never a separate adjacent TSV copy."""
    env_path = os.environ.get('HOKKIEN_HANRI_DICT_PATH')
    if env_path:
        return [Path(env_path)]
    env_repo = os.environ.get('HOKKIEN_GITHUB_REPO_PATH')
    if env_repo:
        return [Path(env_repo) / 'data' / HANRI_TSV_FILENAME]
    if Path(__file__).resolve().parent.name.lower() == 'desktop':
        return [repo_data_path(HANRI_TSV_FILENAME)]
    return [Path.home() / 'Documents' / 'GitHub' / 'thehokkienlang.github.io' / 'data' / HANRI_TSV_FILENAME]


TONE_MARKER_MODULE_PATH = Path(
    os.environ.get(
        'HOKKIEN_TONE_MARKER_PATH',
        str(bundled_resource_path('hokkien_tone_marker_gui.py')),
    )
)


L_TABLE = [chr(codepoint) for codepoint in range(0x1100, 0x1113)]


V_TABLE = [chr(codepoint) for codepoint in range(0x1161, 0x1176)]


T_TABLE = [''] + [chr(codepoint) for codepoint in range(0x11A8, 0x11C3)]


L_INDEX = {ch: i for i, ch in enumerate(L_TABLE)}


V_INDEX = {ch: i for i, ch in enumerate(V_TABLE)}


T_INDEX = {ch: i for i, ch in enumerate(T_TABLE)}


# Compatibility consonants/medials from a standard Korean keyboard.
KEY_TO_JAMO = {
    'r': 'ㄱ', 'R': 'ㄲ', 's': 'ㄴ', 'e': 'ㄷ', 'E': 'ㄸ', 'f': 'ㄹ',
    'a': 'ㅁ', 'q': 'ㅂ', 'Q': 'ㅃ', 't': 'ㅅ', 'd': 'ㅇ',
    'w': 'ㅈ', 'W': 'ㅉ', 'c': 'ㅊ', 'z': 'ㅋ', 'x': 'ㅌ', 'v': 'ㅍ', 'g': 'ㅎ', 'G': 'ㆆ',
    'k': 'ㅏ', 'o': 'ㅐ', 'i': 'ㅑ', 'j': 'ㅓ', 'p': 'ㅔ', 'P': 'ㅖ',
    'u': 'ㅕ', 'h': 'ㅗ', 'y': 'ㅛ', 'n': 'ㅜ', 'b': 'ㅠ', 'm': 'ㅡ', 'l': 'ㅣ',
}


# Shift should not insert Latin capitals. Preserve uppercase keys that have
# real IME values; every other shifted letter is treated as its lowercase key.
SHIFT_PRESERVED_KEYS = {'R', 'E', 'Q', 'W', 'P', 'G'}


def normalize_keyboard_char(char: str) -> str:
    if len(char) == 1 and char.isalpha() and char.upper() == char and char not in SHIFT_PRESERVED_KEYS:
        return char.lower()
    return char


COMPAT_TO_L = {
    'ㄱ': 'ᄀ', 'ㄲ': 'ᄁ', 'ㄴ': 'ᄂ', 'ㄷ': 'ᄃ', 'ㄸ': 'ᄄ', 'ㄹ': 'ᄅ',
    'ㅁ': 'ᄆ', 'ㅂ': 'ᄇ', 'ㅃ': 'ᄈ', 'ㅅ': 'ᄉ', 'ㅇ': 'ᄋ',
    'ㅈ': 'ᄌ', 'ㅉ': 'ᄍ', 'ㅊ': 'ᄎ', 'ㅋ': 'ᄏ', 'ㅌ': 'ᄐ', 'ㅍ': 'ᄑ', 'ㅎ': 'ᄒ',
    'ㆆ': 'ᅙ',
}


COMPAT_TO_V = {
    'ㅏ': 'ᅡ', 'ㅐ': 'ᅢ', 'ㅑ': 'ᅣ', 'ㅓ': 'ᅥ', 'ㅔ': 'ᅦ',
    'ㅕ': 'ᅧ', 'ㅖ': 'ᅨ', 'ㅗ': 'ᅩ', 'ㅛ': 'ᅭ', 'ㅜ': 'ᅮ', 'ㅠ': 'ᅲ',
    'ㅡ': 'ᅳ', 'ㅣ': 'ᅵ', 'ㅢ': 'ᅴ',
}


# ㅅ and ㅊ are onset-only. Final ㅈ is temporary after ㅏ/ㅑ.
COMPAT_TO_T = {
    'ㄱ': 'ᆨ', 'ㄴ': 'ᆫ', 'ㄷ': 'ᆮ', 'ㄹ': 'ᆯ', 'ㅁ': 'ᆷ',
    'ㅂ': 'ᆸ', 'ㅇ': 'ᆼ', 'ㅈ': 'ᆽ',
    'ㅎ': 'ᇂ',
}


# Display standalone Hangul letters as compatibility jamo, matching normal Korean IME behavior.
L_TO_COMPAT = {v: k for k, v in COMPAT_TO_L.items()}


V_TO_COMPAT = {v: k for k, v in COMPAT_TO_V.items()}


# Compatibility forms for standalone compound vowels.
# Example: h+k should display/commit as ㅘ, not the medial jamo ᅪ.
V_TO_COMPAT.update({
    'ᅪ': 'ㅘ',
    'ᅫ': 'ㅙ',
    'ᅬ': 'ㅚ',
    'ᅰ': 'ㅞ',
    'ᅱ': 'ㅟ',
    'ᅴ': 'ㅢ',
})


T_TO_COMPAT = {v: k for k, v in COMPAT_TO_T.items()}


# Compatibility forms for the Hokkien-allowed final clusters.
T_TO_COMPAT.update({
    'ᆶ': 'ㅀ',
})


V_COMBINE = {
    ('ᅩ', 'ᅡ'): 'ᅪ', ('ᅩ', 'ᅢ'): 'ᅫ', ('ᅩ', 'ᅵ'): 'ᅬ',
    ('ᅮ', 'ᅦ'): 'ᅰ', ('ᅮ', 'ᅵ'): 'ᅱ',
    ('ᅳ', 'ᅵ'): 'ᅴ',
}


SPECIAL_MEDIALS = {'ᅷ', 'ᆤ', 'ힻ'}


FINAL_J_SHORTCUT_MEDIALS = {'ᅡ': 'ᅷ', 'ᅣ': 'ᆤ'}


HANGUL_CHOSEONG_FILLER = '\u115F'


EXTRA_INITIALS = {'ᅙ'}


HOKKIEN_SEQUENCE_MAP = {}


# Extra Hokkien initial shortcut.
HOKKIEN_SEQUENCE_MAP.update({
    # Standalone special medial: m+p -> ᅟힻ.
    # There is no compatibility-jamo form for this Hokkien vowel, so use a
    # leading Hangul choseong filler instead of bare ힻ.
    'mp': '\u115Fힻ',
    'kn': '\u115Fᅷ',
    'in': '\u115Fᆤ',
    'mdk': 'ᅙᅡ',
})


# Hanri dictionary entries are stored internally as:
#     base_reading_without_tones -> [{'reading': tone_marked_reading, 'hanri': str, 'row': int}, ...]
# Tones are written directly inside the reading column in the TSV.  Example:
#     랑4    人
#     랑5    弄
# The IME also lets plain 랑 show both candidates, while 랑4 filters to 人 only.
FALLBACK_HANRI_DICT = {
    '가ᄉᅷ': [{'reading': '가ᄉᅷ', 'hanri': '咳嗽', 'row': 0}],
    '띤': [{'reading': '띤', 'hanri': '人', 'row': 0}],
    '띤심': [{'reading': '띤심', 'hanri': '人參', 'row': 0}],
    '띤솅': [{'reading': '띤솅', 'hanri': '人生', 'row': 0}],
    '띤수': [{'reading': '띤수', 'hanri': '人事', 'row': 0}],
    '겅': [
        {'reading': '겅2', 'hanri': '講', 'row': 0, 'form': '本'},
        {'reading': '겅1', 'hanri': '講', 'row': 0, 'form': '變'},
    ],
    '랑': [
        {'reading': '랑4', 'hanri': '人', 'row': 0},
        {'reading': '랑5', 'hanri': '弄', 'row': 0},
    ],
    '세개': [{'reading': '세2개', 'hanri': '世界', 'row': 0}],
    '짇띧': [{'reading': '짇띧', 'hanri': '一日', 'row': 0}],
    '활히': [{'reading': '활5히2', 'hanri': '歡喜', 'row': 0}],
}


HANRI_TSV_FILENAME = 'hokkien_hanri_dict.tsv'


HANRI_DICT_SOURCE = 'built-in fallback'


TONE_DIGITS = set('12345')


# Invisible marker used before an Arabic numeral inserted with Alt+digit.
# The visible text still looks like an ordinary digit, but audio/Lomari can
# distinguish it from a tone digit directly attached to Hangul.
LITERAL_DIGIT_MARK = '​'


ARABIC_NUMERAL_DIGITS = set('0123456789')


LITERAL_DIGIT_DEFAULT_PRONUNCIATIONS = {
    '0': '컹',
    '1': '짇1',
    '2': '띠5',
    '3': '살1',
    '4': '시',
    '5': '꺼5',
    '6': '락1',
    '7': '칟',
    '8': '뵣',
    '9': 'ᄀᅷ2',
}


LITERAL_DIGIT_CONTEXT_PRONUNCIATIONS = {
    ('2', '箍'): '능5',
    ('2', '个'): '능5',
    ('2', '人'): '능5',
}


# Built-in two-digit number patterns before numeric/classifier context characters.
# These are context selectors only: 10號 matches the pronunciation for 10,
# consumes only the Arabic numerals, then leaves the following context character
# to be read normally.
LITERAL_TWO_DIGIT_DATE_NUMBER_TENS = {
    '1': '잡1',
    '2': '띠5잡1',
    '3': '살5잡1',
    '4': '시2잡1',
    '5': '꺼잡1',
    '6': '락잡1',
    '7': '칟1잡1',
    '8': '뵣1잡1',
    '9': 'ᄀᅷ1잡1',
}


LITERAL_TWO_DIGIT_DATE_NUMBER_CONTEXTS = {'號', '日', '月', '歲', '點', '分', '秒', '樓', '層', '章', '節'}


# Before these context characters, digit 1 is pronounced as citation-tone 읻;
# the normal sandhi engine may still change it to 읻1 when connected.
LITERAL_CONTEXTUAL_ONE_READING = '읻'


# Invisible internal tone markers.  They allow the IME to remember tones even
# when the displayed output has no visible mark, especially tone 3.
INTERNAL_TONE_MARKS = {
    '1': '\u2060',
    '2': '\u2061',
    '3': '\u2062',
    '4': '\u2063',
    '5': '\u2064',
}


INTERNAL_TONE_MARK_TO_DIGIT = {v: k for k, v in INTERNAL_TONE_MARKS.items()}


INTERNAL_TONE_MARK_CHARS = set(INTERNAL_TONE_MARK_TO_DIGIT)


NONSTANDARD_READING_MARK = '*'


def reading_is_marked_nonstandard(reading: str) -> bool:
    """True when a TSV reading ends in * to mark a non-standard spelling."""
    return str(reading).strip().endswith(NONSTANDARD_READING_MARK)


def strip_nonstandard_reading_mark(reading: str) -> str:
    """Remove a rightmost TSV non-standard marker without touching content."""
    text = str(reading).strip()
    if text.endswith(NONSTANDARD_READING_MARK):
        return text[:-1].rstrip()
    return text


def strip_reading_tones(reading: str) -> str:
    """Remove tone digits 1-5 and TSV non-standard marker from a reading.

    The TSV writes tones directly in the reading, e.g. 세2개 / 활5히2 / 랑4.
    A rightmost * marks a wrong/non-standard spelling and is ignored for lookup.
    The base reading is used for plain input and pure-Hangul alternatives.
    """
    reading = strip_nonstandard_reading_mark(reading)
    return ''.join(
        ch for ch in reading.strip()
        if (
            ch not in TONE_DIGITS
            and ch not in INTERNAL_TONE_MARK_CHARS
            and ch != NONSTANDARD_READING_MARK
            and ch != LITERAL_DIGIT_MARK
        )
    )


def reading_has_tones(reading: str) -> bool:
    return any((ch in TONE_DIGITS) or (ch in INTERNAL_TONE_MARK_CHARS) for ch in str(reading) if ch != LITERAL_DIGIT_MARK)


def last_non_tone_char(text: str) -> str:
    """Return the final non-tone character used for suffix lookup bucketing."""
    for ch in reversed(str(text or '')):
        if ch not in TONE_DIGITS:
            return ch
    return ''


TONE_DIGIT_TO_SYMBOL = str.maketrans({
    '1': 'ˆ',
    '2': 'ˋ',
    '3': '',
    '4': 'ˊ',
    '5': 'ˉ',
    **{ord(mark): '' for mark in INTERNAL_TONE_MARK_CHARS},
})


def display_reading_tones(reading: str) -> str:
    """Convert internal tone digits to display tone symbols for candidate menus.

    Examples:
        랑4 -> 랑ˊ
        세2개 -> 세ˋ개
        활5히2 -> 활ˉ히ˋ
        tone 3 is removed/unmarked.
    """
    return strip_nonstandard_reading_mark(reading).translate(TONE_DIGIT_TO_SYMBOL)


TONE_SYMBOL_TO_DIGIT = str.maketrans({
    # Primary Hangul tone marks.
    'ˆ': '1',
    'ˋ': '2',
    '`': '2',
    'ˊ': '4',
    'ˉ': '5',

    # Alternative tone marks used by the tone-marker/converter output.
    'ꞈ': '1',
    'ˎ': '2',
    'ˏ': '4',
    'ˍ': '5',

    **{ord(mark): digit for mark, digit in INTERNAL_TONE_MARK_TO_DIGIT.items()},
})


TONE_SYMBOLS = set('ˆˋ`ˊˉꞈˎˏˍ') | INTERNAL_TONE_MARK_CHARS


def normalize_tone_symbols_to_digits(text: str) -> str:
    """Convert typed/display tone symbols back to internal digit tones."""
    return text.translate(TONE_SYMBOL_TO_DIGIT)


def remove_apostrophes_for_lookup(text: str) -> str:
    """Remove apostrophe separators for looser dictionary lookup.

    This lets an input such as 쟣바ᄅᆤ match a TSV reading such as
    쟣바2’ᄅᆤ2.  The committed candidates still keep the TSV spelling,
    including the apostrophe.
    """
    return str(text).replace("'", '').replace('’', '')


def has_relaxable_apostrophe(text: str) -> bool:
    """True when apostrophe can be ignored for lookup.

    Internal apostrophes are separators and may be omitted by the user, e.g.
    쟣바ᄅᆤ can match TSV 쟣바’ᄅᆤ.  A leading apostrophe is meaningful,
    so 래 should not match a TSV reading such as ’래.
    """
    text = str(text)
    for i, ch in enumerate(text):
        if ch in {"'", '’'} and 0 < i < len(text) - 1:
            return True
    return False


def is_hangulish_for_tone(ch: str) -> bool:
    """True for Hangul/Jamo characters that may carry a following tone."""
    return (
        ('\uAC00' <= ch <= '\uD7A3')
        or ('\u1100' <= ch <= '\u11FF')
        or ('\u3130' <= ch <= '\u318F')
        or ch in SPECIAL_MEDIALS
        or ch in EXTRA_INITIALS
    )


def can_attach_tone_to_text(text: str, index: int) -> bool:
    """True if a tone at text[index + 1] may attach to text[index]."""
    if index < 0 or index >= len(text):
        return False
    ch = text[index]
    if '\uAC00' <= ch <= '\uD7A3':
        return True
    if ch in T_INDEX and ch != '':
        j = index - 1
        while j >= 0 and text[j] in T_INDEX and text[j] != '':
            j -= 1
        return j >= 1 and (text[j] in V_INDEX or text[j] in SPECIAL_MEDIALS) and (text[j - 1] in L_INDEX or text[j - 1] in EXTRA_INITIALS)
    if ch in V_INDEX or ch in SPECIAL_MEDIALS:
        return index >= 1 and (text[index - 1] in L_INDEX or text[index - 1] in EXTRA_INITIALS or text[index - 1] == HANGUL_CHOSEONG_FILLER)
    return False


def can_attach_tone_to_output_chars(chars: list[str]) -> bool:
    return bool(chars) and can_attach_tone_to_text(''.join(chars), len(chars) - 1)


def is_hanri_char(ch: str) -> bool:
    """True for CJK/Hanri characters."""
    if not ch:
        return False
    code = ord(ch)
    return (
        0x3400 <= code <= 0x4DBF      # CJK Extension A
        or 0x4E00 <= code <= 0x9FFF   # CJK Unified Ideographs
        or 0xF900 <= code <= 0xFAFF   # CJK Compatibility Ideographs
        or 0x20000 <= code <= 0x2A6DF # CJK Extension B
        or 0x2A700 <= code <= 0x2B73F # CJK Extension C
        or 0x2B740 <= code <= 0x2B81F # CJK Extension D
        or 0x2B820 <= code <= 0x2CEAF # CJK Extension E/F
        or 0x2CEB0 <= code <= 0x2EBEF # CJK Extension F/G/H area
        or 0x30000 <= code <= 0x3134F # CJK Extension G/H
    )


def is_hangul_or_hanri_char(ch: str) -> bool:
    """True if a character counts as Hangul/Hokkien-Hangul or Hanri."""
    return is_hangulish_for_tone(ch) or is_hanri_char(ch)


def field_has_hanri(text: str) -> bool:
    """True if a TSV field contains at least one real Hanri/CJK character."""
    return any(is_hanri_char(ch) for ch in str(text))


def split_hanri_hangul_bracket_inner(inner: str) -> tuple[str, str] | None:
    """Parse an explicit [Hanri + Hangul reading] annotation."""
    text = str(inner or '').strip()
    if not text or not is_hanri_char(text[0]):
        return None

    split_at = 0
    while split_at < len(text) and is_hanri_char(text[split_at]):
        split_at += 1

    hanri = text[:split_at].strip()
    reading = text[split_at:].strip()
    if not hanri or not reading:
        return None

    meaningful_reading_chars = [
        ch for ch in normalize_tone_symbols_to_digits(reading)
        if not ch.isspace() and ch not in TONE_DIGITS and ch not in INTERNAL_TONE_MARK_CHARS
    ]
    if not meaningful_reading_chars or not all(
        is_hangulish_for_tone(ch)
        or ch in {"'", '’', '‘', '-', '–', '—'}
        for ch in meaningful_reading_chars
    ):
        return None

    return hanri, reading


def format_text_tones_for_output(text: str, show_tones: bool = True, keep_literal_digit_markers: bool = False) -> str:
    """Format tone digits/symbols in Hangul output.

    Tone input remains internal as digits 1-5.  This function is used when
    copying output: digits after Hangul become tone symbols if show_tones=True,
    or are removed if show_tones=False.  Hanri/Chinese characters are left
    alone, so Hanri candidates never receive tone marks.

    Alt+digit inserts an invisible LITERAL_DIGIT_MARK before the digit.  For
    normal display/copy this marker is removed while the digit remains literal;
    for audio/Lomari processing it can be kept so the parser knows the digit is
    not a tone marker.
    """
    out: list[str] = []
    literal_next_digit = False

    for ch in str(text):
        if ch == LITERAL_DIGIT_MARK:
            literal_next_digit = True
            if keep_literal_digit_markers:
                out.append(ch)
            continue

        if literal_next_digit and ch in ARABIC_NUMERAL_DIGITS:
            out.append(ch)
            literal_next_digit = False
            continue
        literal_next_digit = False

        if (ch in TONE_DIGITS or ch in TONE_SYMBOLS) and can_attach_tone_to_output_chars(out):
            if show_tones:
                if ch in TONE_DIGITS:
                    out.append(display_reading_tones(ch))
                elif ch in INTERNAL_TONE_MARK_CHARS:
                    # Internal hidden tone markers are never copied visibly.
                    # Tone 3 remains unmarked.
                    out.append(display_reading_tones(INTERNAL_TONE_MARK_TO_DIGIT[ch]))
                elif ch == '`':
                    out.append('ˋ')
                else:
                    out.append(ch)
            # show_tones=False: skip the tone entirely.
        else:
            out.append(ch)
    return ''.join(out)


# Hokkien tone sandhi cycles used to generate sandhi candidates automatically.
#
# General open/non-checked syllables:
#   Citation → sandhi: 1→5→3→2→1 and 4→3.
#
# Checked syllables ending in ㄱ ㄷ ㅂ ㅎ ㅀ use a separate entering-tone pattern:
#   Citation → sandhi: 1→3 and 3→1.
# Pronunciation-equivalent finals follow the same class for tone sandhi:
#   final ㅈ behaves like ㄷ; final ㅊ behaves like ㅎ.
#
# The tables live in shared/tli-sandhi.json, shared with the tone marker and the
# browser engine, so there is one copy to edit.
def load_sandhi_spec() -> dict:
    """Read shared/tli-sandhi.json (or the copy bundled beside this file)."""
    here = Path(__file__).resolve().parent
    bundle_dir = getattr(sys, '_MEIPASS', None)
    candidates = [here.parent / 'shared' / 'tli-sandhi.json', here / 'tli-sandhi.json']
    if bundle_dir:
        candidates.insert(0, Path(bundle_dir) / 'tli-sandhi.json')
    for path in candidates:
        if path.is_file():
            return json.loads(path.read_text(encoding='utf-8'))
    raise FileNotFoundError('Missing the tone-sandhi spec shared/tli-sandhi.json')


SANDHI_SPEC = load_sandhi_spec()
TONE_SANDHI_MAP = dict(SANDHI_SPEC['citationToSandhi']['open'])
CHECKED_TONE_SANDHI_MAP = dict(SANDHI_SPEC['citationToSandhi']['checked'])
CHECKED_FINALS_FOR_SANDHI = set(SANDHI_SPEC['checkedFinals'])
SANDHI_EQUIVALENT_FINALS = dict(SANDHI_SPEC['sandhiEquivalentFinals'])


def canonicalize_sandhi_final_jamo(final: str) -> str:
    """Return the final-jamo class used by tone sandhi.

    Final ㅈ is normalized to a special medial before tone processing; it is
    not treated as a pronunciation-equivalent coda.
    """
    return SANDHI_EQUIVALENT_FINALS.get(final, final)


def contains_hangul_reading_unit(reading: str) -> bool:
    """True if a TSV reading contains Hangul/Jamo that can carry tone.

    Earlier versions only treated precomposed Hangul syllables such as 기/혱헉
    as unmarked citation tone 3.  Hokkien-specific readings can also be written
    directly as jamo clusters, e.g. ᄀᅷ / 到, so those must also be treated as
    citation forms and displayed with (本).
    """
    return any(is_hangulish_for_tone(ch) for ch in str(reading))


def is_only_compatibility_jamo_reading(reading: str) -> bool:
    """True if the reading column is made only of compatibility jamo.

    Pure compatibility-jamo spellings such as ㅋㅂㅋㅃ are usually sound
    effects or literal jamo strings, not normal syllabic readings.  They should
    still be searchable, but they should not be labelled 本/變 and should not
    receive an automatic sandhi candidate.
    """
    meaningful_chars = []
    for ch in normalize_tone_symbols_to_digits(str(reading).strip()):
        if ch.isspace() or ch in TONE_DIGITS or ch in INTERNAL_TONE_MARK_CHARS:
            continue
        meaningful_chars.append(ch)

    return bool(meaningful_chars) and all('\u3130' <= ch <= '\u318F' for ch in meaningful_chars)


def infer_default_form(reading: str) -> str:
    """Return the automatically inferred 本/變 display label for TSV rows.

    Every normal Hanri reading is treated as a citation form (本).  If no tone
    digit is written, the final character is interpreted as citation tone 3.
    Multi-syllable untoned entries such as 혱헉 / 幸福 and jamo-cluster entries
    such as ᄀᅷ / 到 still display (本) and can generate a sandhi form.

    Exception: if the reading column contains only compatibility jamo such as
    ㅋㅂㅋㅃ, it is treated as a literal jamo string, so no 本/變 label is shown.
    """
    if is_only_compatibility_jamo_reading(reading):
        return ''
    if reading_has_tones(reading):
        return '本'
    if contains_hangul_reading_unit(reading):
        return '本'
    return ''


def last_tone_digit_index(reading: str) -> int | None:
    """Return the index of the last tone digit in a reading, if any."""
    for i in range(len(reading) - 1, -1, -1):
        if reading[i] in TONE_DIGITS:
            return i
    return None


def final_jamo_before_tone(reading: str, tone_index: int) -> str:
    """Return the final jamo of the syllable immediately before a tone digit.

    This works before decompose_precomposed_syllable() is defined, because the
    Hanri TSV is loaded early during module startup.  It supports both ordinary
    precomposed Hangul syllables such as 각/갇/갑/갛/갏 and jamo-cluster forms
    where the final jongseong appears directly before the tone digit.
    """
    if tone_index <= 0:
        return ''

    ch = reading[tone_index - 1]

    # Jamo-cluster readings may end directly in a jongseong jamo before the tone.
    if ch in T_INDEX:
        return ch

    # Ordinary precomposed Hangul syllable.
    if '\uAC00' <= ch <= '\uD7A3':
        final_index = (ord(ch) - 0xAC00) % 28
        return T_TABLE[final_index]

    return ''


def is_checked_final_before_tone(reading: str, tone_index: int) -> bool:
    """True if the syllable before the tone uses the checked-tone class.

    Besides written ㄱ/ㄷ/ㅂ/ㅎ/ㅀ, pronunciation-equivalent final ㅈ and ㅊ
    are handled as ㄷ and ㅎ respectively.
    """
    final = canonicalize_sandhi_final_jamo(final_jamo_before_tone(reading, tone_index))
    return final in CHECKED_FINALS_FOR_SANDHI


def final_hangul_unit_needs_implicit_tone(reading: str) -> tuple[int, str] | None:
    """Return (tone_insert_index, implicit_reading) if final unit has no tone.

    TSV readings may record earlier syllable tones while leaving the final
    syllable unmarked because tone 3 is written without a visible mark.

    Example:
        세2개   -> final 개 is implicit citation tone 3, so sandhi is 세2개2
        활5히2  -> final 히 already has explicit tone 2, so no implicit tone
    """
    last_hangul_index = None
    for i in range(len(reading) - 1, -1, -1):
        if is_hangulish_for_tone(reading[i]):
            last_hangul_index = i
            break

    if last_hangul_index is None:
        return None

    # If a tone digit appears after the final Hangul/Jamo unit, the final tone
    # is already explicit.
    for ch in reading[last_hangul_index + 1:]:
        if ch in TONE_DIGITS or ch in INTERNAL_TONE_MARK_CHARS:
            return None
        if is_hangulish_for_tone(ch):
            return None

    tone_insert_index = last_hangul_index + 1
    implicit_reading = reading[:tone_insert_index] + '3' + reading[tone_insert_index:]
    return tone_insert_index, implicit_reading


def is_apostrophe_boundary_after_tone(reading: str, tone_index: int) -> bool:
    """True if this tone belongs to a Hangul/Hanri unit before an apostrophe.

    Project rule: when Hangul/Hanri is immediately followed by ' or ’, that
    pre-apostrophe unit is citation-final and must not receive an automatically
    generated sandhi (變) tone.

    TSV readings normally write tone digits after the Hangul unit and before
    the apostrophe, e.g. 등1’래.  In that case the digit at tone_index is
    directly followed by the apostrophe.
    """
    if tone_index <= 0 or tone_index + 1 >= len(reading):
        return False
    return (
        reading[tone_index + 1] in {"'", '’'}
        and is_hangulish_for_tone(reading[tone_index - 1])
    )


def is_post_apostrophe_tone(reading: str, tone_index: int) -> bool:
    """True if the tone belongs to a post-apostrophe Hangul/Jamo segment.

    Project rule: forms such as ’ᄅᆤˋ are citation-like attached forms and
    should never create an automatic sandhi (變) candidate.  This is handled
    generally: if the syllable carrying the tone is in the same word segment
    after an apostrophe, the IME does not generate a sandhi variant for it.

    Examples blocked from auto-sandhi:
        ’ᄅᆤ2
        쟣바2’ᄅᆤ2
        食飽’ᄅᆤ2
    """
    if tone_index <= 0:
        return False

    i = tone_index - 1
    saw_hangul_or_hanri = False
    while i >= 0:
        ch = reading[i]
        if ch in {"'", '’'}:
            return saw_hangul_or_hanri
        if ch.isspace():
            return False
        if is_hangul_or_hanri_char(ch):
            saw_hangul_or_hanri = True
        i -= 1
    return False


def citation_to_sandhi_reading(reading: str) -> str | None:
    """Generate the sandhi form for the final syllable of a TSV reading.

    TSV readings are citation forms.  The final syllable may have an explicit
    tone digit, or it may be unmarked tone 3 even when earlier syllables have
    written tones.

    Examples:
        겅2    -> 겅1
        랑4    -> 랑3  (displayed as 랑)
        활5히2 -> 활5히1
        세개   -> 세개2
        세2개  -> 세2개2
    """
    if is_only_compatibility_jamo_reading(reading):
        return None

    implicit_final = final_hangul_unit_needs_implicit_tone(reading)
    if implicit_final is not None:
        idx, implicit_reading = implicit_final
        citation_tone = '3'

        # Apostrophe-attached forms remain citation-like and should not create
        # automatic 變 forms.
        if (
            is_apostrophe_boundary_after_tone(implicit_reading, idx)
            or is_post_apostrophe_tone(implicit_reading, idx)
        ):
            return None

        if is_checked_final_before_tone(implicit_reading, idx):
            sandhi_tone = CHECKED_TONE_SANDHI_MAP.get(citation_tone)
        else:
            sandhi_tone = TONE_SANDHI_MAP.get(citation_tone)

        if sandhi_tone and sandhi_tone != citation_tone:
            return reading[:idx] + sandhi_tone + reading[idx:]
        return None

    idx = last_tone_digit_index(reading)
    if idx is None:
        return None

    # A tone attached to a Hangul/Hanri unit immediately before an apostrophe
    # should remain citation-final, so do not generate a 變 candidate.
    # Likewise, a tone inside a post-apostrophe attached form such as ’ᄅᆤˋ
    # should not create an automatic 變 candidate.
    # Examples blocked:
    #   등1’래      -> no 등5’래
    #   ’ᄅᆤ2       -> no ’ᄅᆤ1
    #   쟣바2’ᄅᆤ2  -> no 쟣바2’ᄅᆤ1
    if is_apostrophe_boundary_after_tone(reading, idx) or is_post_apostrophe_tone(reading, idx):
        return None

    citation_tone = reading[idx]
    if is_checked_final_before_tone(reading, idx):
        sandhi_tone = CHECKED_TONE_SANDHI_MAP.get(citation_tone)
    else:
        sandhi_tone = TONE_SANDHI_MAP.get(citation_tone)

    if not sandhi_tone or sandhi_tone == citation_tone:
        return None
    return reading[:idx] + sandhi_tone + reading[idx + 1:]


def _fallback_hanri_dict() -> dict[str, list[dict]]:
    return {
        reading: [dict(entry) for entry in entries]
        for reading, entries in FALLBACK_HANRI_DICT.items()
    }


def load_hanri_dict(tsv_path: Path | None = None) -> dict[str, list[dict]]:
    """
    Load Hanri candidates from a TSV file.

    Require the nine named columns in tools.dictionary_schema.DICTIONARY_COLUMNS.
    See docs/dictionary-tsv-schema.md; ranking overrides live in a separate TSV.

    If reading ends in *, it is treated as a wrong/non-standard spelling.
    The corrected column can then store the standard Hangul spelling shown on
    the right-hand side of the candidate menu.

    TSV readings are assumed to be citation tone (本), and the program
    automatically generates the corresponding sandhi tone (變).

    Tones are written directly in the reading column, not in a separate tone
    column. Optional gloss/search fields may be blank, but every source record
    requires its structural entry_type and permanent entry_id.

    The program stores these under their tone-stripped base readings.  Therefore
    plain 랑 shows the TSV citation candidates, while 랑4 shows only citation 人 and generated 랑3/랑 can show the sandhi form when typed explicitly.
    """
    global HANRI_DICT_SOURCE

    if tsv_path is None:
        tsv_path = hanri_tsv_path_candidates()[0]

    if not tsv_path.exists():
        HANRI_DICT_SOURCE = 'built-in fallback; TSV not found'
        return _fallback_hanri_dict()

    entries: dict[str, list[dict]] = {}

    try:
        with tsv_path.open('r', encoding='utf-8-sig', newline='') as f:
            rows = list(csv.reader(f, delimiter='\t'))

        rows = [row for row in rows if any(cell.strip() for cell in row)]
        if not rows:
            raise ValueError('TSV has no valid rows.')

        header = dictionary_schema_api().require_dictionary_header(rows[0])
        data_rows = rows[1:]
        reading_col = header.index('reading')
        hanri_col = header.index('hanri')
        corrected_col = header.index('corrected')
        entry_type_col = header.index('entry_type')
        entry_id_col = header.index('entry_id')
        row_offset = 2

        for offset, row in enumerate(data_rows, start=row_offset):
            reading_cell = row[reading_col].strip() if len(row) > reading_col else ''
            hanri = row[hanri_col].strip() if len(row) > hanri_col else ''
            corrected_cell = row[corrected_col].strip() if corrected_col is not None and len(row) > corrected_col else ''
            entry_type = row[entry_type_col].strip() if entry_type_col is not None and len(row) > entry_type_col else ''
            entry_id = row[entry_id_col].strip() if entry_id_col is not None and len(row) > entry_id_col else ''
            metadata = dictionary_schema_api().resolve_dictionary_record(
                dict(zip(header, row))
            )

            if not reading_cell or not hanri:
                continue

            is_nonstandard = reading_is_marked_nonstandard(reading_cell)
            reading_raw = strip_nonstandard_reading_mark(reading_cell)
            corrected = normalize_tone_symbols_to_digits(strip_nonstandard_reading_mark(corrected_cell)) if corrected_cell else ''

            # Arabic-numeral pronunciation rows are read by
            # load_literal_digit_pronunciations().  They should not become Hanri
            # candidates or ordinary reading entries.
            if reading_raw and reading_raw[0] in ARABIC_NUMERAL_DIGITS and corrected:
                continue

            base_reading = strip_reading_tones(reading_raw)
            form = infer_default_form(reading_raw)

            if not base_reading:
                continue

            citation_entry = {
                'reading': reading_raw,
                'hanri': hanri,
                'raw': metadata,
                'row': offset,
                'form': form,
                'auto_sandhi': False,
                'nonstandard': is_nonstandard,
                'corrected': corrected,
                'entry_type': entry_type,
                'entry_id': entry_id,
                'simplified': metadata.get('simplified', ''),
                'mandarin_trad': metadata.get('mandarin_trad', ''),
                'mandarin_simp': metadata.get('mandarin_simp', ''),
            }
            entries.setdefault(base_reading, []).append(citation_entry)

            # Auto-generate sandhi form from citation-toned TSV rows.
            # Example: TSV only needs 겅2 講; the IME also recognises 겅1
            # and labels it as 變.  Generated sandhi entries are labelled 變 automatically.
            if form == '本':
                sandhi_reading = citation_to_sandhi_reading(reading_raw)
                if sandhi_reading and sandhi_reading != reading_raw:
                    sandhi_base = strip_reading_tones(sandhi_reading)
                    corrected_sandhi = citation_to_sandhi_reading(corrected) if corrected else ''
                    if not corrected_sandhi:
                        corrected_sandhi = corrected
                    if sandhi_base:
                        entries.setdefault(sandhi_base, []).append({
                            'reading': sandhi_reading,
                            'citation_reading': reading_raw,
                            'hanri': hanri,
                            'raw': metadata,
                            'row': offset,
                            'form': '變',
                            'auto_sandhi': True,
                            'nonstandard': is_nonstandard,
                            'corrected': corrected_sandhi,
                            'entry_type': entry_type,
                            'entry_id': f'{entry_id}-sandhi' if entry_id else '',
                            'simplified': metadata.get('simplified', ''),
                            'mandarin_trad': metadata.get('mandarin_trad', ''),
                            'mandarin_simp': metadata.get('mandarin_simp', ''),
                        })

        ranking = dictionary_ranking_api()
        aliases = dictionary_schema_api().load_headword_aliases(tsv_path, ranking.read_records(tsv_path))
        for values in entries.values():
            for entry in values:
                if not entry.get('auto_sandhi'):
                    entry['headwordAliases'] = [key for key, target in aliases.items() if target == entry['entry_id']]
        ranking.annotate_entries([e for values in entries.values() for e in values],
                                 tsv_path.with_name('dictionary_priority.tsv'), ranking.read_records(tsv_path))
        loaded: dict[str, list[dict]] = {}
        for reading, rows_for_reading in entries.items():
            seen = set()
            candidates = []
            for entry in ranking.rank_entries(rows_for_reading, reading):
                key = (entry['hanri'], entry.get('reading', ''), entry.get('form', ''), entry.get('corrected', ''))
                if key not in seen:
                    candidates.append(entry)
                    seen.add(key)
            if candidates:
                loaded[reading] = candidates

        if loaded:
            total = sum(len(v) for v in loaded.values())
            HANRI_DICT_SOURCE = f'{tsv_path.name}: {total} Hanri entries / {len(loaded)} readings'
            return {reading:loaded[reading] for reading in sorted(loaded,key=lambda key:(ranking.reading_sort_key(key),key))}

        HANRI_DICT_SOURCE = 'built-in fallback; TSV had no valid entries'
        return _fallback_hanri_dict()

    except dictionary_ranking_api().InvalidStaticPriority:
        raise
    except Exception as exc:
        HANRI_DICT_SOURCE = f'built-in fallback; could not load TSV ({exc})'
        return _fallback_hanri_dict()


HANRI_DICT = load_hanri_dict()


def numeric_key_digit_prefix_len(key: str) -> int:
    """Return how many leading Arabic digits a numeric TSV key has."""
    count = 0
    for ch in str(key):
        if ch in ARABIC_NUMERAL_DIGITS:
            count += 1
        else:
            break
    return count


def load_literal_digit_pronunciations(
    tsv_path: Path | None = None,
) -> tuple[dict[str, str], dict[tuple[str, str], str], list[tuple[str, str, int]]]:
    """Load Arabic-numeral pronunciation overrides from the normal Hanri TSV.

    Rows are written in the same TSV as ordinary entries, using corrected as the
    hidden Hangul pronunciation:
        named lexical fields (no ranking columns)
        1        1      1         짇1
        2        2      1         띠5
        2箍      2箍    1         능5
        10號     10號   1         잡1

    Numeric keys are matched longest-first.  If a key has trailing context such
    as 2箍 or 10號, the context only chooses the pronunciation; the parser
    consumes the numeric part and then continues with 箍/號 normally.
    Built-in fallback patterns also cover 10-99 before the numeric context
    characters in LITERAL_TWO_DIGIT_DATE_NUMBER_CONTEXTS, so those do not
    have to be listed one by one in the TSV.
    """
    defaults = dict(LITERAL_DIGIT_DEFAULT_PRONUNCIATIONS)
    contexts = dict(LITERAL_DIGIT_CONTEXT_PRONUNCIATIONS)
    pattern_map: dict[str, str] = {}

    # Built-in fallback patterns.  TSV rows below can overwrite these.
    for digit, reading in defaults.items():
        pattern_map[digit] = reading
    for (digit, following), reading in contexts.items():
        pattern_map[digit + following] = reading
    for following in LITERAL_TWO_DIGIT_DATE_NUMBER_CONTEXTS:
        pattern_map['1' + following] = LITERAL_CONTEXTUAL_ONE_READING

    # Hardcoded date/number-label pattern requested for the context set:
    #   10-19 -> 잡1 + ones
    #   20-29 -> 띠5잡1 + ones
    #   30    -> 살5잡1, 40 -> 시2잡1, etc.
    # x=0 is silent after 十, so 10 is 잡1, 20 is 띠5잡1, ...
    for tens_digit, tens_reading in LITERAL_TWO_DIGIT_DATE_NUMBER_TENS.items():
        for ones_digit in ARABIC_NUMERAL_DIGITS:
            if ones_digit == '0':
                ones_reading = ''
            elif ones_digit == '1':
                ones_reading = LITERAL_CONTEXTUAL_ONE_READING
            else:
                ones_reading = defaults.get(ones_digit, ones_digit)
            number_key = tens_digit + ones_digit
            number_reading = tens_reading + ones_reading
            for following in LITERAL_TWO_DIGIT_DATE_NUMBER_CONTEXTS:
                pattern_map[number_key + following] = number_reading

    if tsv_path is None:
        tsv_path = hanri_tsv_path_candidates()[0]

    if not tsv_path.exists():
        patterns = sorted(
            ((key, reading, numeric_key_digit_prefix_len(key)) for key, reading in pattern_map.items()),
            key=lambda item: (len(item[0]), item[2]), 
            reverse=True,
        )
        return defaults, contexts, patterns

    try:
        with tsv_path.open('r', encoding='utf-8-sig', newline='') as f:
            rows = list(csv.reader(f, delimiter='\t'))
    except Exception:
        patterns = sorted(
            ((key, reading, numeric_key_digit_prefix_len(key)) for key, reading in pattern_map.items()),
            key=lambda item: (len(item[0]), item[2]),
            reverse=True,
        )
        return defaults, contexts, patterns

    rows = [row for row in rows if any(cell.strip() for cell in row)]
    if not rows:
        patterns = sorted(
            ((key, reading, numeric_key_digit_prefix_len(key)) for key, reading in pattern_map.items()),
            key=lambda item: (len(item[0]), item[2]),
            reverse=True,
        )
        return defaults, contexts, patterns

    try:
        header = dictionary_schema_api().require_dictionary_header(rows[0])
    except ValueError:
        patterns = sorted(
            ((key, reading, numeric_key_digit_prefix_len(key)) for key, reading in pattern_map.items()),
            key=lambda item: (len(item[0]), item[2]),
            reverse=True,
        )
        return defaults, contexts, patterns

    data_rows = rows[1:]
    reading_col = header.index('reading')
    corrected_col = header.index('corrected')
    for row in data_rows:
        reading_cell = row[reading_col].strip() if len(row) > reading_col else ''
        corrected_cell = row[corrected_col].strip() if len(row) > corrected_col else ''
        if not reading_cell or not corrected_cell:
            continue

        reading_key = strip_nonstandard_reading_mark(reading_cell)
        corrected = normalize_tone_symbols_to_digits(strip_nonstandard_reading_mark(corrected_cell))
        if not corrected:
            continue

        digit_prefix_len = numeric_key_digit_prefix_len(reading_key)
        if digit_prefix_len <= 0:
            continue

        pattern_map[reading_key] = corrected
        if len(reading_key) == 1 and reading_key in ARABIC_NUMERAL_DIGITS:
            defaults[reading_key] = corrected
        elif digit_prefix_len == 1 and len(reading_key) == 2:
            contexts[(reading_key[0], reading_key[1])] = corrected

    patterns = sorted(
        ((key, reading, numeric_key_digit_prefix_len(key)) for key, reading in pattern_map.items()),
        key=lambda item: (len(item[0]), item[2]),
        reverse=True,
    )
    return defaults, contexts, patterns


DIGIT_PRONUNCIATIONS, DIGIT_CONTEXT_PRONUNCIATIONS, DIGIT_PRONUNCIATION_PATTERNS = load_literal_digit_pronunciations()


def literal_digit_reading(digit: str, following_char: str = '') -> str:
    """Return hidden Hangul reading for one Arabic numeral."""
    digit = str(digit)
    following_char = str(following_char or '')[:1]
    return DIGIT_CONTEXT_PRONUNCIATIONS.get(
        (digit, following_char),
        DIGIT_PRONUNCIATIONS.get(digit, digit),
    )


def literal_digit_token_at(text: str, index: int) -> tuple[str, int] | None:
    """Return (digit, end_index) for a literal Arabic numeral at index."""
    if index < 0 or index >= len(text):
        return None
    ch = text[index]
    if ch == LITERAL_DIGIT_MARK and index + 1 < len(text) and text[index + 1] in ARABIC_NUMERAL_DIGITS:
        return text[index + 1], index + 2
    if ch in ARABIC_NUMERAL_DIGITS:
        return ch, index + 1
    return None


def literal_digit_sequence_at(text: str, index: int) -> tuple[str, int] | None:
    """Return (visible_digits, end_index) for a run of literal Arabic digits.

    The visible digits may be stored plainly (pasted text) or as Alt+digit
    markers, where the internal marker precedes the visible numeral.
    """
    if index < 0 or index >= len(text):
        return None

    digits: list[str] = []
    i = index
    while i < len(text):
        ch = text[i]
        if ch == LITERAL_DIGIT_MARK and i + 1 < len(text) and text[i + 1] in ARABIC_NUMERAL_DIGITS:
            digits.append(text[i + 1])
            i += 2
            continue
        if ch in ARABIC_NUMERAL_DIGITS:
            digits.append(ch)
            i += 1
            continue
        break

    if not digits:
        return None
    return ''.join(digits), i


def literal_digit_source_end_after_count(text: str, index: int, count: int) -> int | None:
    """Return source index after consuming count literal digits."""
    if count <= 0:
        return index

    seen = 0
    i = index
    while i < len(text) and seen < count:
        ch = text[i]
        if ch == LITERAL_DIGIT_MARK and i + 1 < len(text) and text[i + 1] in ARABIC_NUMERAL_DIGITS:
            i += 2
            seen += 1
            continue
        if ch in ARABIC_NUMERAL_DIGITS:
            i += 1
            seen += 1
            continue
        return None
    return i if seen == count else None


def literal_number_reading_at(text: str, index: int) -> tuple[str, int] | None:
    """Return (hidden_reading, end_index) for a numeric TSV pronunciation.

    Longest TSV pattern wins.  Pure numeric keys consume that many digits.
    Contextual keys such as 2人 or 10號 check the following context but consume
    only the Arabic numeral part, so the following Hanri character is still read
    normally after the number.
    """
    digit_run = literal_digit_sequence_at(text, index)
    if digit_run is None:
        return None
    digits, _run_end = digit_run

    for key, reading, digit_count in DIGIT_PRONUNCIATION_PATTERNS:
        numeric_part = key[:digit_count]
        suffix = key[digit_count:]
        if not numeric_part or not digits.startswith(numeric_part):
            continue
        digit_end = literal_digit_source_end_after_count(text, index, digit_count)
        if digit_end is None:
            continue
        if suffix and not text.startswith(suffix, digit_end):
            continue
        return reading, digit_end

    first = literal_digit_token_at(text, index)
    if first is None:
        return None
    digit, digit_end = first
    following_char = text[digit_end] if digit_end < len(text) else ''
    return literal_digit_reading(digit, following_char), digit_end


def decompose_precomposed_syllable(ch: str) -> tuple[str, str, str] | None:
    """Return (initial, medial, final) for a normal Hangul syllable."""
    if not ('\uAC00' <= ch <= '\uD7A3'):
        return None
    idx = ord(ch) - 0xAC00
    initial = L_TABLE[idx // 588]
    medial = V_TABLE[(idx % 588) // 28]
    final = T_TABLE[idx % 28]
    return initial, medial, final


def medial_typing_components(medial: str) -> list[str]:
    """Return the simple vowel components used to type a medial.

    This lets the predictive menu stay open while the user is midway through
    a compound-vowel syllable.  Example: 쀄 is typed as ㅃ + ㅜ + ㅔ, so the
    intermediate display 쟣바뿌 should still be recognised as a prefix for
    쟣바’쀄.
    """
    reverse_v = {v: k for k, v in V_COMBINE.items()}
    if medial in reverse_v:
        first, second = reverse_v[medial]
        return [first, second]
    if medial in V_INDEX:
        return [medial]
    return []


def precomposed_syllable_typing_prefixes(ch: str) -> set[str]:
    """Return normal IME midway displays for one precomposed syllable.

    For a dictionary syllable like 쀄, this returns ㅃ and 뿌.  For a checked
    syllable like 힐, this returns ㅎ and 히.  These prefixes are used only for
    prediction, not for committed output.
    """
    decomposed = decompose_precomposed_syllable(ch)
    if decomposed is None:
        return set()

    initial, medial, final = decomposed
    result: set[str] = set()

    compat_initial = L_TO_COMPAT.get(initial)
    if compat_initial:
        result.add(compat_initial)

    components = medial_typing_components(medial)
    if components:
        # The first vowel component is the most important midway state for
        # compound vowels: ㅃ+ㅜ -> 뿌 before ㅃ+ㅜ+ㅔ -> 쀄.
        first_medial = components[0]
        result.add(compose_syllable(initial, first_medial, ''))

        # If the syllable has a final consonant, the no-final syllable is also
        # a midway state: 히 before 힐.
        if final:
            result.add(compose_syllable(initial, medial, ''))

    return {item for item in result if item and item != ch}


def raw_keyboard_prefix_display(raw_prefix: str) -> str:
    """Display state after typing a raw keyboard prefix normally.

    This is used for Hokkien shortcut readings.  Example: the final dictionary
    unit ᄅힻ is typed by f+m+p; before p is pressed, the visible state is 르.
    Therefore forms midway through raw shortcuts can keep their menu alive.
    """
    output = ''
    initial = ''
    medial = ''
    final = ''

    def buffer_text() -> str:
        if initial and medial:
            return compose_syllable(initial, medial, final)
        if initial:
            return L_TO_COMPAT.get(initial, initial)
        if medial:
            return V_TO_COMPAT.get(medial, medial)
        if final:
            return T_TO_COMPAT.get(final, final)
        return ''

    def commit() -> None:
        nonlocal output, initial, medial, final
        if initial or medial or final:
            output += buffer_text()
            initial = medial = final = ''

    for raw_ch in raw_prefix:
        raw_ch = normalize_keyboard_char(raw_ch)
        compat = KEY_TO_JAMO.get(raw_ch)
        if not compat:
            commit()
            output += raw_ch
            continue

        if compat in COMPAT_TO_V:
            v = COMPAT_TO_V[compat]
            if not initial and not medial and not final:
                medial = v
            elif initial and not medial:
                medial = v
            elif initial and medial and not final:
                candidate = V_COMBINE.get((medial, v))
                if candidate:
                    medial = candidate
                else:
                    commit()
                    medial = v
            else:
                commit()
                medial = v
            continue

        if compat in COMPAT_TO_L:
            # Mirror the ㅡ+ㅇ -> ㆆ convenience used by the main composer.
            if (not initial) and medial == 'ᅳ' and not final and compat == 'ㅇ':
                medial = ''
                initial = 'ᅙ'
                continue

            new_initial = COMPAT_TO_L[compat]
            if not initial and not medial and not final:
                initial = new_initial
            elif initial and not medial:
                commit()
                initial = new_initial
            elif (
                initial and medial and not final and compat in COMPAT_TO_T
                and (compat != 'ㅈ' or medial in FINAL_J_SHORTCUT_MEDIALS)
            ):
                final = COMPAT_TO_T[compat]
            else:
                commit()
                initial = new_initial
            continue

        commit()
        output += compat

    return output + buffer_text()


def hokkien_shortcut_midway_prefixes(units: list[tuple[str, str]], use_tones: bool) -> set[str]:
    """Return midway displays for Hokkien raw-key shortcut clusters.

    If a TSV reading contains the final mapped cluster ᄅᆤ, the menu should also
    recognise the normal halfway typing state 랴.  This is generated from the
    same HOKKIEN_SEQUENCE_MAP used by the composer, so it stays systematic.
    """
    result: set[str] = set()
    chars = [c for c, _t in units]

    for i in range(len(units)):
        remaining = ''.join(chars[i:])
        previous = ''.join(c + (t if use_tones else '') for c, t in units[:i])

        for raw_seq, mapped in HOKKIEN_SEQUENCE_MAP.items():
            if not remaining.startswith(mapped):
                continue

            for end in range(1, len(raw_seq)):
                display = raw_keyboard_prefix_display(raw_seq[:end])
                if display:
                    result.add(previous + display)

    return result


def hanri_reading_prefixes(reading: str) -> set[str]:
    """Predictive prefixes generated generally from a TSV reading.

    Tones may be embedded in the reading, e.g. 세2개 or 활5히2.
    Prefixes are generated in two ways:
        - tone-stripped base form: 세ㄱ, 섹
        - tone-written form: 세2ㄱ
    """
    prefixes: set[str] = set()

    def split_units(text: str) -> list[tuple[str, str]]:
        units: list[tuple[str, str]] = []
        i = 0
        while i < len(text):
            ch = text[i]
            tones = ''
            j = i + 1
            while j < len(text) and text[j] in TONE_DIGITS:
                tones += text[j]
                j += 1
            units.append((ch, tones))
            i = j
        return units

    for use_tones in (False, True):
        units = split_units(reading)

        # Midway states for Hokkien raw-key shortcut clusters, generated
        # from HOKKIEN_SEQUENCE_MAP.
        prefixes.update(hokkien_shortcut_midway_prefixes(units, use_tones))

        # Absorbed-initial prefixes for readings where the next syllable is
        # written as jamo, optionally after an apostrophe separator.  This is
        # the same general idea as 세ㄱ -> 섹, but it also works for mixed
        # forms such as 쟣바’ᄅᆤ: while the user is midway through typing the
        # following ᄅ-syllable, their IME may temporarily show 쟣발.
        for i, (ch, tones) in enumerate(units):
            if i == 0 or not (ch in L_INDEX or ch in EXTRA_INITIALS):
                continue

            prev_i = i - 1
            boundary = ''
            if units[prev_i][0] in {"'", '’'}:
                boundary = units[prev_i][0] + (units[prev_i][1] if use_tones else '')
                prev_i -= 1

            if prev_i < 0:
                continue

            prev_ch, prev_tones = units[prev_i]
            prev_decomposed = decompose_precomposed_syllable(prev_ch)
            compat_initial = L_TO_COMPAT.get(ch)
            if (
                prev_decomposed is not None
                and compat_initial
                and compat_initial in COMPAT_TO_T
            ):
                prev_initial, prev_medial, prev_final = prev_decomposed
                if prev_final == '':
                    before_prev = ''.join(c + (t if use_tones else '') for c, t in units[:prev_i])
                    absorbed_previous = before_prev + compose_syllable(prev_initial, prev_medial, COMPAT_TO_T[compat_initial])
                    prefixes.add(absorbed_previous)
                    # Also keep a boundary-preserving form for users who type
                    # the separator before the next initial.
                    if boundary:
                        prefixes.add(before_prev + prev_ch + (prev_tones if use_tones else '') + boundary + L_TO_COMPAT.get(ch, ch))

        # General progressive prefixes.  This keeps the candidate menu stable
        # while typing through mixed jamo/precomposed readings.  For example,
        # if the dictionary contains ᄎᅷ힐ㄹ, the menu can stay visible at
        # ᄎᅷ히, ᄎᅷ힐, and ᄎᅷ힐ㄹ instead of disappearing at the completed
        # intermediate syllable ᄎᅷ힐.  Single-character prefixes are still
        # ignored so bare initials such as ㄸ do not trigger menus too early.
        for end in range(2, len(units)):
            prefix = ''.join(c + (t if use_tones else '') for c, t in units[:end])
            if len(strip_reading_tones(prefix)) >= 2:
                prefixes.add(prefix)

        for i, (ch, tones) in enumerate(units):
            if i == 0:
                continue

            decomposed = decompose_precomposed_syllable(ch)
            if decomposed is None:
                continue

            initial, medial, final = decomposed
            previous = ''.join(c + (t if use_tones else '') for c, t in units[:i])

            for partial in precomposed_syllable_typing_prefixes(ch):
                prefixes.add(previous + partial)

            compat_initial = L_TO_COMPAT.get(initial)

            if compat_initial and compat_initial in COMPAT_TO_T and i > 0:
                prev_ch, prev_tones = units[i - 1]
                prev_decomposed = decompose_precomposed_syllable(prev_ch)
                if prev_decomposed is not None:
                    prev_initial, prev_medial, prev_final = prev_decomposed
                    if prev_final == '' and not use_tones:
                        absorbed_previous = (
                            ''.join(c for c, _t in units[:i - 1])
                            + compose_syllable(prev_initial, prev_medial, COMPAT_TO_T[compat_initial])
                        )
                        prefixes.add(absorbed_previous)

            if final:
                partial_syllable = compose_syllable(initial, medial, '')
                prefixes.add(previous + partial_syllable)

    return {p for p in prefixes if p and p != reading and p != strip_reading_tones(reading)}


def build_hanri_prefix_index(hanri_dict: dict[str, list[dict]]) -> dict[str, list[tuple[str, dict]]]:
    """Map predictive typed prefixes to (base reading, Hanri entry) candidates.

    The index also keeps complete readings of length 2 or more as stable
    predictive keys.  Exact matches are still handled first in
    find_hanri_candidate(), but this prevents the menu from disappearing at
    the moment an absorbed-final prefix becomes a completed syllable.

    Example:
        주재 can be reached through the typing state 줒 -> 주재.
        If 줒 shows a menu, 주재 should keep showing it instead of closing.
    """
    index: dict[str, list[tuple[str, dict]]] = {}

    def add_index(prefix: str, item: tuple[str, dict]) -> None:
        if not prefix:
            return
        # Avoid very early popups from bare one-character readings/initials.
        if len(strip_reading_tones(prefix)) < 2:
            return
        index.setdefault(prefix, [])
        if item not in index[prefix]:
            index[prefix].append(item)

    for base_reading, hanri_entries in hanri_dict.items():
        for entry in hanri_entries:
            # Build prediction prefixes for both plain and tone-written readings.
            # Example: 세2개 gives 세ㄱ/섹 and also 세2ㄱ.
            item = (base_reading, entry)
            for source_reading in {base_reading, entry.get('reading', base_reading)}:
                add_index(source_reading, item)
                add_index(strip_reading_tones(source_reading), item)
                for prefix in hanri_reading_prefixes(source_reading):
                    add_index(prefix, item)
    return index


def build_hanri_prefix_lookup_buckets(prefix_index: dict[str, list[tuple[str, dict]]]) -> dict[str, list[str]]:
    """Bucket predictive prefixes by possible final lookup character."""
    buckets: dict[str, list[str]] = {}
    for prefix in prefix_index:
        if not prefix:
            continue
        bucket_keys = {prefix[-1]}
        if has_relaxable_apostrophe(prefix):
            loose = remove_apostrophes_for_lookup(prefix)
            if loose:
                bucket_keys.add(loose[-1])
        for key in bucket_keys:
            buckets.setdefault(key, []).append(prefix)
    return buckets


def compose_syllable(initial: str, medial: str, final: str = '') -> str:
    """Compose a normal Unicode Hangul syllable, or return a jamo cluster if needed."""
    if initial in L_INDEX and medial in V_INDEX and final in T_INDEX:
        code = 0xAC00 + (L_INDEX[initial] * 21 + V_INDEX[medial]) * 28 + T_INDEX[final]
        return chr(code)
    return initial + medial + final


# Build the predictive Hanri prefix index only after compose_syllable() exists.
HANRI_PREFIX_INDEX = build_hanri_prefix_index(HANRI_DICT)


HANRI_PREFIX_LOOKUP_BUCKETS = build_hanri_prefix_lookup_buckets(HANRI_PREFIX_INDEX)


def build_hanri_candidate_tests(hanri_dict: dict) -> tuple[list[tuple[str, str, list[dict]]], list[tuple[str, list[dict]]]]:
    """Precompute candidate suffix tests so keypress lookup does not rebuild them."""
    exact_tests: list[tuple[str, str, list[dict]]] = []
    for base_reading, entries in hanri_dict.items():
        exact_tests.append((base_reading, base_reading, entries))
        for entry in entries:
            for alias in entry.get('headwordAliases', []):
                exact_tests.append((alias, base_reading, [entry]))
            written = entry.get('reading', base_reading)
            if written != base_reading:
                exact_tests.append((written, base_reading, entries))

    seen_tests = set()
    unique_exact_tests: list[tuple[str, str, list[dict]]] = []
    for typed_form, base_reading, entries in exact_tests:
        key = (typed_form, base_reading)
        if key not in seen_tests:
            unique_exact_tests.append((typed_form, base_reading, entries))
            seen_tests.add(key)

    seen_base_tests = set()
    base_tests: list[tuple[str, list[dict]]] = []
    for base_reading, entries in hanri_dict.items():
        if base_reading not in seen_base_tests:
            base_tests.append((base_reading, entries))
            seen_base_tests.add(base_reading)

    return unique_exact_tests, base_tests


def build_hanri_candidate_test_buckets(
    exact_tests: list[tuple[str, str, list[dict]]],
    base_tests: list[tuple[str, list[dict]]],
) -> tuple[dict[str, list[tuple[str, str, list[dict]]]], dict[str, list[tuple[str, list[dict]]]]]:
    """Bucket candidate suffix tests by the only final character that can match."""
    exact_buckets: dict[str, list[tuple[str, str, list[dict]]]] = {}
    base_buckets: dict[str, list[tuple[str, list[dict]]]] = {}

    for typed_form, base_reading, entries in exact_tests:
        key = str(typed_form or '')[-1:]
        if key:
            exact_buckets.setdefault(key, []).append((typed_form, base_reading, entries))

    for base_reading, entries in base_tests:
        key = last_non_tone_char(base_reading)
        if key:
            base_buckets.setdefault(key, []).append((base_reading, entries))

    return exact_buckets, base_buckets


HANRI_EXACT_CANDIDATE_TESTS, HANRI_BASE_CANDIDATE_TESTS = build_hanri_candidate_tests(HANRI_DICT)


HANRI_EXACT_CANDIDATE_BUCKETS, HANRI_BASE_CANDIDATE_BUCKETS = build_hanri_candidate_test_buckets(
    HANRI_EXACT_CANDIDATE_TESTS,
    HANRI_BASE_CANDIDATE_TESTS,
)


def reload_hanri_resources() -> None:
    """Reload TSV-backed dictionaries and every derived lookup index."""
    global HANRI_DICT, HANRI_PREFIX_INDEX, HANRI_PREFIX_LOOKUP_BUCKETS
    global HANRI_EXACT_CANDIDATE_TESTS, HANRI_BASE_CANDIDATE_TESTS
    global HANRI_EXACT_CANDIDATE_BUCKETS, HANRI_BASE_CANDIDATE_BUCKETS
    global DIGIT_PRONUNCIATIONS, DIGIT_CONTEXT_PRONUNCIATIONS, DIGIT_PRONUNCIATION_PATTERNS
    global AUDIO_HANRI_INDEX, MIXED_AUDIO_HANRI_INDEX, AUDIO_HANRI_SEGMENT_INDEX
    global AUDIO_READING_INDEX, AUDIO_READING_INDEX_BY_FIRST

    HANRI_DICT = load_hanri_dict()
    HANRI_PREFIX_INDEX = build_hanri_prefix_index(HANRI_DICT)
    HANRI_PREFIX_LOOKUP_BUCKETS = build_hanri_prefix_lookup_buckets(HANRI_PREFIX_INDEX)
    HANRI_EXACT_CANDIDATE_TESTS, HANRI_BASE_CANDIDATE_TESTS = build_hanri_candidate_tests(HANRI_DICT)
    HANRI_EXACT_CANDIDATE_BUCKETS, HANRI_BASE_CANDIDATE_BUCKETS = build_hanri_candidate_test_buckets(
        HANRI_EXACT_CANDIDATE_TESTS,
        HANRI_BASE_CANDIDATE_TESTS,
    )
    DIGIT_PRONUNCIATIONS, DIGIT_CONTEXT_PRONUNCIATIONS, DIGIT_PRONUNCIATION_PATTERNS = load_literal_digit_pronunciations()
    AUDIO_HANRI_INDEX = build_audio_hanri_index(HANRI_DICT)
    MIXED_AUDIO_HANRI_INDEX = build_mixed_audio_hanri_index(AUDIO_HANRI_INDEX)
    AUDIO_HANRI_SEGMENT_INDEX = build_audio_hanri_segment_index(HANRI_DICT)
    AUDIO_READING_INDEX = build_audio_reading_index(HANRI_DICT)
    AUDIO_READING_INDEX_BY_FIRST = build_audio_reading_index_by_first(AUDIO_READING_INDEX)


AUDIO_FILE_EXTENSIONS = ('.wav', '.wave')


AUDIO_MULTI_SYLLABLE_SPEED_FACTOR = 1.10


AUDIO_TONE4_SPEED_FACTOR = 1.03


# English-cluster ㅡ-helper syllables keep their consonant onset, then get
# clipped to a short natural lead-in.  This avoids the rushed sound caused by
# globally speeding them up, while still preventing a full extra ㅡ vowel.
AUDIO_ENGLISH_CLUSTER_SPEED_FACTOR = 1.0


AUDIO_PHRASE_BOUNDARY_PUNCTUATION = set(',，.。!?！？:：;；-－—\n\r')


AUDIO_IGNORED_PUNCTUATION = set(""" 	
'’‘\"“”.,，。!?！？;；:：、()（）[]【】{}《》〈〉…—-_/\\|·・~～""")


AUDIO_MODE_TAIPEI = 'taipei'


AUDIO_MODE_SINGAPORE = 'singapore'


def singapore_tone1_audio_replacement(
    next_unit: str,
    next_tone: str,
    next_has_explicit_separator_after: bool = False,
) -> str:
    """Return Singapore-mode replacement for non-final non-checked tone 1 audio.

    This affects audio-file selection only.  A current tone 1 syllable is
    replaced only if the current syllable itself is NOT checked-final and is
    directly connected to the following syllable with no intervening separator.

    If the following syllable is citation-final, Singapore mode now uses rising
    tone 4 consistently, regardless of that final syllable's tone/final class.
    Inside a consecutive sandhi chain, the existing dynamic rule still applies
    right-to-left, so a changed tone can compound into the syllable before it.

    If the following syllable itself is immediately followed by an explicit
    separator such as a space, apostrophe, comma, period, bracket, slash, etc.,
    that following syllable is treated as citation-final for this decision.
    Example: 總統 and 總督 both use 정4 before the final syllable, while
    米粉粿 remains 삐5훈4궤2.

        next citation-final any tone/final    -> tone 4 audio
        next dynamic normal tone 3/5          -> tone 4 audio
        next dynamic normal tone 1/2/4        -> tone 5 audio
        next checked tone 1                   -> tone 4 audio
        next checked tone 3                   -> tone 5 audio

    Checked means pronounced with final ㄱ/ㄷ/ㅀ/ㅂ/ㅎ.
    Pronunciation-equivalent finals are handled through audio_unit_has_short_overlap_final(),
    so ㅈ behaves like ㄷ and ㅊ behaves like ㅎ for this decision.
    If the following category is outside the specified set, keep tone 1.
    """
    next_tone = str(next_tone or '3')
    if next_has_explicit_separator_after:
        return '4'

    next_is_checked = audio_unit_has_short_overlap_final(next_unit)

    if next_is_checked:
        if next_tone == '1':
            return '4'
        if next_tone == '3':
            return '5'
        return '1'

    if next_tone in {'3', '5'}:
        return '4'
    if next_tone in {'1', '2', '4'}:
        return '5'
    return '1'


def entry_audio_reading(entry: dict, base_reading: str = '') -> str:
    """Return the Hangul reading that should drive recorded audio playback."""
    corrected = entry.get('corrected', '')
    if entry.get('nonstandard') and corrected:
        return corrected
    return entry.get('reading', base_reading) or base_reading


def build_audio_hanri_index(hanri_dict: dict[str, list[dict]]) -> list[tuple[str, str]]:
    """Resolve visible headwords using the shared contextual static order."""
    groups: dict[str,list[dict]] = {}
    for base,entries in hanri_dict.items():
        for entry in entries:
            hanri = str(entry.get('hanri',''))
            if not field_has_hanri(hanri):
                continue
            for key in {hanri,format_text_tones_for_output(hanri,True),format_text_tones_for_output(hanri,False)}:
                groups.setdefault(key,[]).append(entry)
    ranking = dictionary_ranking_api()
    return [(key,entry_audio_reading(ranking.rank_entries(groups[key],key)[0]))
            for key in sorted(groups,key=lambda key:(-len(key),key))]


def is_audio_hangul_only_override_field(text: str) -> bool:
    """True when a TSV hanri field is a Hangul-only audio override.

    Unlike the candidate-menu helper, this deliberately allows a leading
    connector apostrophe.  Rows such as:
        ’꽈    ’꽈
    mean the attached form ’꽈 is an explicit pronunciation override, so
    typed 等’꽈 should use 꽈3 instead of falling through to the bare 꽈2 row.
    Apostrophes are separators/attachment marks, not pronunciation units.
    """
    meaningful_chars = []
    for ch in normalize_tone_symbols_to_digits(str(text).strip()):
        if (
            ch.isspace()
            or ch in TONE_DIGITS
            or ch in INTERNAL_TONE_MARK_CHARS
            or ch in {"'", '’', '‘'}
        ):
            continue
        meaningful_chars.append(ch)

    return bool(meaningful_chars) and all(is_hangulish_for_tone(ch) for ch in meaningful_chars)


def build_audio_hanri_segment_index(hanri_dict: dict[str, list[dict]]) -> list[dict]:
    records = {}
    for entries in hanri_dict.values():
        for entry in entries:
            if not entry.get('auto_sandhi') and field_is_plain_hanri_key(entry.get('hanri','')):
                records.setdefault(dictionary_ranking_api().source_id(entry),entry)
    return sorted(records.values(),key=dictionary_ranking_api().canonical_key)


def audio_hanri_run_end(text: str, index: int) -> int:
    end = index
    while end < len(text) and is_hanri_char(text[end]):
        end += 1
    return end


def static_audio_hanri_match(text: str, index: int) -> tuple[str, str] | None:
    if index >= len(text) or not is_hanri_char(text[index]):
        return None
    match = dictionary_ranking_api().segment_match(text,index,AUDIO_HANRI_SEGMENT_INDEX,audio_hanri_run_end(text,index))
    return (match['hanri'],entry_audio_reading(match)) if match else None


def build_audio_reading_index(hanri_dict: dict[str, list[dict]]) -> list[tuple[str, str]]:
    """Map visible Hangul spellings to tone-written readings for audio.

    Important rule for raw unmarked Hangul:
        Unmarked Hangul typed by the user is tone 3 by default and is already
        treated as the surface/sandhi value.  It must not be re-sandhied just
        because another syllable follows.

    Therefore ordinary Hanri rows such as:
        시4    時
        시     時
    must NOT make plain typed 시 play as 시4 or sandhi as 시2.

    Exception:
        If the TSV hanri column itself is Hangul-only, it is being used as an
        explicit Hangul-to-Hangul pronunciation entry.  In that case its
        unmarked visible form may map to the TSV's tone-written reading, e.g.:
        쉬2    쉬ˋ
    lets typed 쉬 play as 쉬2, and that TSV-owned unit can still undergo normal
    connected-speech sandhi when appropriate.

    Apostrophe-attached Hangul-only rows are also explicit overrides. Example:
        ’꽈    ’꽈
    lets typed 等’꽈 use 꽈3 from the exact attached TSV row, instead of the
    separate bare 꽈2 entry.
    """
    items: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(key: str, reading: str) -> None:
        key = str(key)
        reading = str(reading)
        if key and reading and (key, reading) not in seen:
            items.append((key, reading))
            seen.add((key, reading))

    def add_exact_toned_forms(source: str, reading: str) -> None:
        """Add only tone-explicit spellings for source -> reading.

        These are safe because the user explicitly typed/committed the tone.
        We deliberately do not add tone-stripped keys here.  Tone 3 is visually
        unmarked, so its display form is not added as a dictionary key; plain
        unmarked Hangul must remain raw tone 3 instead of a TSV match.
        """
        source = str(source)
        if not source or not reading_has_tones(normalize_tone_symbols_to_digits(source)):
            return

        source_digits = normalize_tone_symbols_to_digits(source)
        bare = strip_reading_tones(source_digits)
        add(source, reading)
        add(source_digits, reading)

        visible = display_reading_tones(source_digits)
        if visible != bare:
            add(visible, reading)

        formatted = format_text_tones_for_output(source_digits, True)
        if formatted != bare:
            add(formatted, reading)

    def add_unmarked_override_forms(source: str, reading: str) -> None:
        """Add tone-free keys that are allowed to override raw tone-3 default."""
        source = str(source)
        if not source:
            return
        add(source, reading)
        add(strip_reading_tones(source), reading)
        add(display_reading_tones(source), reading)
        add(format_text_tones_for_output(source, True), reading)
        add(format_text_tones_for_output(source, False), reading)

    for base_reading, entries in sorted(hanri_dict.items(), key=lambda item: (
        dictionary_ranking_api().canonical_key(item[1][0]), item[0],
    )):
        for entry in entries:
            reading = entry_audio_reading(entry, base_reading)
            written = str(entry.get('reading', base_reading) or base_reading)
            hanri_raw = str(entry.get('hanri', ''))
            hanri_is_hangul_only = is_audio_hangul_only_override_field(hanri_raw) and not field_has_hanri(hanri_raw)

            # 1) Exact tone-written/readable forms always work.
            #    Example: typed 시4 / 시ˊ should use 시4 audio.
            for source in {written, reading}:
                add_exact_toned_forms(source, reading)

            # 2) Do NOT add tone-free keys for ordinary Hanri TSV rows,
            #    even if their reading column is unmarked.  Plain typed Hangul
            #    is treated as already-sandhied tone 3 unless a Hangul-only
            #    hanri-column override below explicitly says otherwise.
            #
            #    Example: 시 / 時 must not make plain 시 become dictionary-owned
            #    and then sandhi as 시2 in 시뎋....  Only actual Hanri 時 uses
            #    the TSV reading.

            # 3) Hangul-only hanri fields are explicit pronunciation overrides.
            #    This is the only case where an unmarked typed Hangul form may
            #    inherit a tone from a TSV row with explicit tones.
            #    Example: 쉬2    쉬ˋ  means typed 쉬 should play 쉬2.
            if hanri_is_hangul_only:
                add_unmarked_override_forms(hanri_raw, reading)

            # 4) Non-standard spelling rows still allow the wrong visible spelling
            #    to route to the corrected audio reading, but only for that exact
            #    dictionary-marked spelling.
            if entry.get('nonstandard') and entry.get('corrected'):
                add_unmarked_override_forms(written, reading)

    return sorted(
        items,
        key=lambda item: (-len(strip_reading_tones(item[0])), -int(reading_has_tones(item[0])), item[0]),
    )


def contains_apostrophe_boundary(text: str) -> bool:
    """True if a lookup key/reading contains an apostrophe boundary.

    Audio/Lomari parsing must see apostrophes as real boundaries.  If a long
    TSV key such as 飲’롷킈 is matched before the parser reaches the apostrophe,
    the pre-apostrophe syllable can be treated as connected speech in Singapore
    mode.  Skipping such long keys lets the parser first match 飲, then handle
    ’ as a citation-final boundary.
    """
    return any(ch in str(text) for ch in {"'", '’', '‘'})


def field_is_plain_hanri_key(text: str) -> bool:
    value = str(text or '').strip()
    return bool(value) and all(is_hanri_char(ch) for ch in value)


def build_mixed_audio_hanri_index(audio_hanri_index: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Pre-filter visible keys that mix Hangul/Jamo with Hanri."""
    return [
        (key, reading)
        for key, reading in audio_hanri_index
        if (
            key
            and field_has_hanri(key)
            and not field_is_plain_hanri_key(key)
            and not contains_apostrophe_boundary(key)
        )
    ]


def mixed_audio_hanri_match(text: str, index: int) -> tuple[str, str] | None:
    """Match TSV visible keys that mix Hangul/Jamo with Hanri, e.g. 뽀彩工."""
    source = str(text or '')
    for key, reading in MIXED_AUDIO_HANRI_INDEX:
        if source.startswith(key, index):
            return key, reading
    return None


def build_audio_reading_index_by_first(audio_reading_index: list[tuple[str, str]]) -> dict[str, list[tuple[str, str]]]:
    """Bucket audio reading overrides by first visible character."""
    buckets: dict[str, list[tuple[str, str]]] = {}
    for key, reading in audio_reading_index:
        if key:
            buckets.setdefault(str(key)[0], []).append((key, reading))
    return buckets


def mark_untoned_audio_units(reading: str, default_tone: str = '3') -> str:
    """Add an explicit default tone to Hangul/Jamo units that have no tone."""
    source = normalize_tone_symbols_to_digits(str(reading or ''))
    out: list[str] = []
    i = 0
    tone_chars = TONE_SYMBOLS.union(TONE_DIGITS).union(INTERNAL_TONE_MARK_CHARS)

    while i < len(source):
        unit_end = audio_unit_end_at(source, i)
        if unit_end is None:
            out.append(source[i])
            i += 1
            continue

        out.append(source[i:unit_end])
        i = unit_end
        has_tone = False
        while (
            i < len(source)
            and source[i] in tone_chars
            and can_attach_tone_to_text(source, i - 1)
        ):
            out.append(source[i])
            has_tone = True
            i += 1
        if not has_tone:
            out.append(default_tone)

    return ''.join(out)


def is_explicit_apostrophe_tone_override(key: str, reading: str) -> bool:
    """True for an attached TSV form such as ’ᄅᆤˋ / ’ᄅᆤ2.

    General post-apostrophe text is forced to tone 3 until the next whitespace.
    Only a TSV/audio-reading entry that itself starts with an apostrophe and
    carries an explicit tone is allowed to override that low-tone rule.
    """
    key_text = normalize_tone_symbols_to_digits(str(key or ''))
    reading_text = normalize_tone_symbols_to_digits(str(reading or ''))
    starts_attached = bool(key_text and key_text[0] in {"'", '’', '‘'})
    return bool(
        starts_attached
        and (reading_has_tones(key_text) or reading_has_tones(reading_text))
    )


AUDIO_HANRI_INDEX = build_audio_hanri_index(HANRI_DICT)


MIXED_AUDIO_HANRI_INDEX = build_mixed_audio_hanri_index(AUDIO_HANRI_INDEX)


AUDIO_HANRI_SEGMENT_INDEX = build_audio_hanri_segment_index(HANRI_DICT)


AUDIO_READING_INDEX = build_audio_reading_index(HANRI_DICT)


AUDIO_READING_INDEX_BY_FIRST = build_audio_reading_index_by_first(AUDIO_READING_INDEX)


def is_ignored_audio_punctuation(ch: str) -> bool:
    return (not ch) or ch.isspace() or ch in AUDIO_IGNORED_PUNCTUATION


def is_audio_phrase_boundary(ch: str) -> bool:
    """True for punctuation that resets audio first/last character logic.

    Apostrophes are intentionally not included: 食飽’ᄅᆤ remains one phrase for
    trimming, even though the apostrophe may still affect dictionary/sandhi
    behaviour elsewhere.
    """
    return bool(ch) and ch in AUDIO_PHRASE_BOUNDARY_PUNCTUATION


# Pronunciation-equivalent audio lookup rules.
# These rules are deliberately applied to the audio-file lookup layer only:
# the spelling shown in the IME is not changed, but files can be shared when
# the Hokkien pronunciation is identical.
# Examples:
#     갓 -> 가   ㅅ final is silent
#     짖 -> 짇   ㅈ final is pronounced as ㄷ
#     갗 -> 갛   ㅊ final is pronounced as ㅎ
#     릐 -> 리   ㅢ is pronounced like ㅣ
#     괴 -> 궤   ㅚ is pronounced like ㅞ
#     옹 -> 엉   ㅗ+ㅇ shares the canonical ong recording with ㅓ+ㅇ
#     용 -> 영   ㅛ+ㅇ shares the canonical yong recording with ㅕ+ㅇ
AUDIO_EQUIVALENT_MEDIALS = {
    'ᅴ': 'ᅵ',
    'ᅬ': 'ᅰ',
}


AUDIO_EQUIVALENT_FINALS = {
}


AUDIO_EQUIVALENT_COMPAT_VOWELS = {
    'ㅢ': 'ㅣ',
    'ㅚ': 'ㅞ',
}


AUDIO_EQUIVALENT_COMPAT_FINALS = {}


AUDIO_NG_MEDIAL_ALIASES = {
    'ᅩ': 'ᅥ',
    'ᅭ': 'ᅧ',
}


def canonicalize_audio_unit(unit: str) -> str:
    """Return the pronunciation-equivalent spelling used for audio lookup.

    This is general and structural: it decomposes Hangul syllables/jamo clusters
    and rewrites only the medial/final positions that are pronounced identically
    in this Hokkien Hangul audio system.  It does not alter the displayed IME
    text and it does not rewrite initial consonants.
    """
    text = str(unit)
    out: list[str] = []
    i = 0

    while i < len(text):
        ch = text[i]

        decomposed = decompose_precomposed_syllable(ch)
        if decomposed is not None:
            initial, medial, final = decomposed
            medial = AUDIO_EQUIVALENT_MEDIALS.get(medial, medial)
            final = AUDIO_EQUIVALENT_FINALS.get(final, final)
            if final == 'ᆼ':
                medial = AUDIO_NG_MEDIAL_ALIASES.get(medial, medial)
            out.append(compose_syllable(initial, medial, final))
            i += 1
            continue

        # Hokkien jamo cluster: initial + medial + optional final(s).
        if is_initial_jamo(ch) and i + 1 < len(text) and is_vowel_jamo(text[i + 1]):
            initial = ch
            medial = AUDIO_EQUIVALENT_MEDIALS.get(text[i + 1], text[i + 1])
            j = i + 2
            finals: list[str] = []
            while j < len(text) and text[j] in T_INDEX and text[j] != '':
                finals.append(AUDIO_EQUIVALENT_FINALS.get(text[j], text[j]))
                j += 1
            if finals == ['ᆼ']:
                medial = AUDIO_NG_MEDIAL_ALIASES.get(medial, medial)
            out.append(initial + medial + ''.join(finals))
            i = j
            continue

        # Standalone ㅢ is a vowel, not a final consonant, so it can safely be
        # mapped to standalone ㅣ.  Standalone final consonant letters are not
        # rewritten because without a syllable context ㅅ/ㅈ/ㅊ may be initials.
        if ch in AUDIO_EQUIVALENT_COMPAT_VOWELS:
            out.append(AUDIO_EQUIVALENT_COMPAT_VOWELS[ch])
            i += 1
            continue
        if ch in AUDIO_EQUIVALENT_COMPAT_FINALS:
            out.append(AUDIO_EQUIVALENT_COMPAT_FINALS[ch])
            i += 1
            continue

        out.append(ch)
        i += 1

    return ''.join(out)


AUDIO_SHORT_OVERLAP_FINALS = {'ᆨ', 'ᆮ', 'ᆶ', 'ᆸ', 'ᇂ'}


def audio_unit_final_jamo(unit: str) -> str:
    """Return the pronounced final jamo of the last Hangul/Jamo unit.

    This is structural, not example-based: precomposed Hangul and Hokkien
    jamo clusters are decomposed/canonicalised first, so pronunciation-equivalent
    spellings such as 짖 -> 짇 and 갗 -> 갛 inherit the timing class of ㄷ/ㅎ.
    The ㅀ final is deliberately kept as ᆶ so it can receive the shorter
    checked-final overlap rather than the ㄹ-final overlap.
    """
    text = canonicalize_audio_unit(str(unit))
    if not text:
        return ''

    i = 0
    last_final = ''
    while i < len(text):
        ch = text[i]
        decomposed = decompose_precomposed_syllable(ch)
        if decomposed is not None:
            _initial, _medial, final = decomposed
            last_final = final
            i += 1
            continue

        if is_initial_jamo(ch) and i + 1 < len(text) and is_vowel_jamo(text[i + 1]):
            j = i + 2
            final = ''
            while j < len(text) and text[j] in T_INDEX and text[j] != '':
                final = text[j]
                j += 1
            last_final = final
            i = j
            continue

        if ch == 'ㄹ':
            last_final = 'ᆯ'
        elif ch == 'ㄱ':
            last_final = 'ᆨ'
        elif ch == 'ㄷ':
            last_final = 'ᆮ'
        elif ch == 'ㅂ':
            last_final = 'ᆸ'
        elif ch == 'ㅎ':
            last_final = 'ᇂ'
        elif ch == 'ㅀ':
            last_final = 'ᆶ'
        i += 1

    return last_final


def audio_unit_has_short_overlap_final(unit: str) -> bool:
    """True for finals ㄱ/ㄷ/ㅀ/ㅂ/ㅎ, which use the checked-final overlap."""
    return audio_unit_final_jamo(unit) in AUDIO_SHORT_OVERLAP_FINALS


def audio_unit_initial_medial_final(unit: str) -> tuple[str, str, str] | None:
    """Return the first syllabic unit's (initial, medial, final) for audio rules."""
    text = str(unit)
    if not text:
        return None

    decomposed = decompose_precomposed_syllable(text[0])
    if decomposed is not None:
        return decomposed

    if len(text) >= 2 and is_initial_jamo(text[0]) and is_vowel_jamo(text[1]):
        final = ''
        j = 2
        while j < len(text) and text[j] in T_INDEX and text[j] != '':
            final = text[j]
            j += 1
        return text[0], text[1], final

    return None


def replace_audio_unit_initial(unit: str, new_initial: str) -> str:
    """Replace the initial of the first syllabic audio unit.

    This is audio-only.  The spelling shown in the IME and the Lomari preview
    are not changed.
    """
    text = str(unit)
    if not text:
        return text

    decomposed = decompose_precomposed_syllable(text[0])
    if decomposed is not None:
        _initial, medial, final = decomposed
        return compose_syllable(new_initial, medial, final) + text[1:]

    if len(text) >= 2 and is_initial_jamo(text[0]) and is_vowel_jamo(text[1]):
        j = 2
        while j < len(text) and text[j] in T_INDEX and text[j] != '':
            j += 1
        return new_initial + text[1:j] + text[j:]

    return text


def apply_d_final_onset_tensing_to_audio_phrase(
    phrase_units: list[tuple[str, str, bool, bool, bool]]
) -> list[tuple[str, str, bool, bool, bool]]:
    """Use ㄸ-initial audio after a directly connected ㄷ/ㅈ-final syllable.

    Examples:
        raw 짇에       -> audio units 짇 + 떼
        raw 짖에       -> audio units 짖 + 떼
        TSV 짇에4     -> audio units 짇3 + 떼4
        TSV 짖에4     -> audio units 짖3 + 떼4

    TSV readings may package several unmarked syllables plus one final tone as
    a single audio unit, e.g. 짇에4 becomes ('짇에', '4').  Before applying
    onset tensing, split only such a multi-syllable unit when it contains the
    target ㄷ/ㅈ-final + ㅇ-initial boundary.  Earlier split syllables keep
    implicit tone 3; the original tone stays on the final syllable.

    Final ㅈ belongs to the same pronunciation class as final ㄷ for this audio
    rule, matching the existing sandhi/audio equivalence rules.

    Only audio lookup units are rewritten.  The IME spelling and Lomari preview
    are unchanged.  Spaces, apostrophes, and punctuation still block the rule.
    """
    expanded: list[tuple[str, str, bool, bool, bool]] = []

    def is_d_class_final(unit: str) -> bool:
        parsed = audio_unit_initial_medial_final(unit)
        return bool(
            parsed is not None
            and canonicalize_sandhi_final_jamo(parsed[2]) == 'ᆮ'
        )

    for unit, tone, link_to_next, separator_after, eligible in phrase_units:
        parts = split_untoned_hangul_units(unit)

        has_internal_trigger = False
        if len(parts) > 1:
            for idx in range(len(parts) - 1):
                next_parsed = audio_unit_initial_medial_final(parts[idx + 1])
                if (
                    is_d_class_final(parts[idx])
                    and next_parsed is not None
                    and next_parsed[0] == 'ᄋ'
                ):
                    has_internal_trigger = True
                    break

        if not has_internal_trigger:
            expanded.append((unit, tone, link_to_next, separator_after, eligible))
            continue

        last_part_index = len(parts) - 1
        for idx, part in enumerate(parts):
            is_last_part = idx == last_part_index
            expanded.append((
                part,
                tone if is_last_part else '3',
                link_to_next if is_last_part else True,
                separator_after if is_last_part else False,
                eligible if is_last_part else False,
            ))

    result = list(expanded)

    for idx in range(len(result) - 1):
        current_unit, _current_tone, link_to_next, _separator_after, _eligible = result[idx]
        if not link_to_next:
            continue

        next_unit, next_tone, next_link, next_separator, next_eligible = result[idx + 1]
        next_parsed = audio_unit_initial_medial_final(next_unit)

        if (
            is_d_class_final(current_unit)
            and next_parsed is not None
            and next_parsed[0] == 'ᄋ'
        ):
            result[idx + 1] = (
                replace_audio_unit_initial(next_unit, 'ᄄ'),
                next_tone,
                next_link,
                next_separator,
                next_eligible,
            )

    return result


def audio_unit_is_u_syllable(unit: str, initial: str) -> bool:
    """True for a short English-cluster helper syllable like 브/스/트."""
    parsed = audio_unit_initial_medial_final(unit)
    return bool(parsed and parsed[0] == initial and parsed[1] == 'ᅳ' and parsed[2] == '')


def english_cluster_reduction_flags(
    phrase_units: list[tuple[str, str, bool, bool, bool]]
) -> list[bool]:
    """Mark ㅡ-helper syllables that should be shortened for English clusters.

    The user-facing pattern notation treats ㄹ-, ㄸ-, ㅂ-, etc. as any following
    syllable with that initial.  Only directly connected units are considered;
    spaces, apostrophes, and punctuation break the link before this function is
    called through the existing singapore_link_to_next flag.
    """
    flags = [False] * len(phrase_units)

    for idx in range(len(phrase_units) - 1):
        current, _tone, link_to_next, _separator_after, _eligible = phrase_units[idx]
        if not link_to_next:
            continue

        next_unit = phrase_units[idx + 1][0]
        next_parsed = audio_unit_initial_medial_final(next_unit)
        if next_parsed is None:
            continue
        next_initial, _next_medial, _next_final = next_parsed

        # 브ㄹ-, 쁘ㄹ-, 그ㄹ-, 끄ㄹ-, 흐ㄹ-, 스ㄹ-, 트ㄹ-
        if next_initial == 'ᄅ' and any(
            audio_unit_is_u_syllable(current, initial)
            for initial in {'ᄇ', 'ᄈ', 'ᄀ', 'ᄁ', 'ᄒ', 'ᄉ', 'ᄐ'}
        ):
            flags[idx] = True

        # 브ㄸ-, 쁘ㄸ-, 드ㄸ-, 뜨ㄸ-, 그ㄸ-, 끄ㄸ-, 흐ㄸ-
        if next_initial == 'ᄄ' and any(
            audio_unit_is_u_syllable(current, initial)
            for initial in {'ᄇ', 'ᄈ', 'ᄃ', 'ᄄ', 'ᄀ', 'ᄁ', 'ᄒ'}
        ):
            flags[idx] = True

        # 스ㅂ-, 스ㄷ-, 스ㄱ-, 스ㅁ-, 스ㄴ-
        if audio_unit_is_u_syllable(current, 'ᄉ') and next_initial in {'ᄇ', 'ᄃ', 'ᄀ', 'ᄆ', 'ᄂ'}:
            flags[idx] = True

        # 스흐 / 스트: both ㅡ-helper syllables are shortened.
        if audio_unit_is_u_syllable(current, 'ᄉ') and (
            audio_unit_is_u_syllable(next_unit, 'ᄒ')
            or audio_unit_is_u_syllable(next_unit, 'ᄐ')
        ):
            flags[idx] = True
            flags[idx + 1] = True

    return flags


def audio_lookup_units(unit: str) -> list[str]:
    """Return audio lookup spellings, canonical pronunciation first."""
    original = str(unit)
    canonical = canonicalize_audio_unit(original)
    result: list[str] = []
    for item in (
        audio_vowel_jamo_to_precomposed_unit(canonical),
        canonical,
        audio_vowel_jamo_to_precomposed_unit(original),
        original,
    ):
        if item and item not in result:
            result.append(item)
    return result


def build_jamo_pronunciation_readings() -> dict[str, str]:
    """Standalone jamo names/readings used for audio and Lomari preview."""
    readings: dict[str, str] = {}

    def add(reading: str, *letters: str) -> None:
        for letter in letters:
            if letter:
                readings[letter] = reading

    for compat, medial in COMPAT_TO_V.items():
        audio_medial = AUDIO_EQUIVALENT_MEDIALS.get(medial, medial)
        if audio_medial in V_INDEX:
            reading = compose_syllable('ᄋ', audio_medial, '') + '1'
            add(reading, compat, medial)

    for medial in V_INDEX:
        if medial:
            audio_medial = AUDIO_EQUIVALENT_MEDIALS.get(medial, medial)
            if audio_medial in V_INDEX:
                add(compose_syllable('ᄋ', audio_medial, '') + '1', medial)

    for medial in SPECIAL_MEDIALS:
        add(HANGUL_CHOSEONG_FILLER + medial + '1', medial, HANGUL_CHOSEONG_FILLER + medial)

    add('기5역1', 'ㄱ', 'ᄀ', 'ᆨ')
    add('샹5기5역1', 'ㄲ', 'ᄁ', 'ᆩ')
    add('니5운1', 'ㄴ', 'ᄂ', 'ᆫ')
    add('디5욷1', 'ㄷ', 'ᄃ', 'ᆮ')
    add('샹5디5욷1', 'ㄸ', 'ᄄ')
    add('리5일1', 'ㄹ', 'ᄅ', 'ᆯ')
    add('미5음4', 'ㅁ', 'ᄆ', 'ᆷ')
    add('비5얍1', 'ㅂ', 'ᄇ', 'ᆸ')
    add('샹5비5얍1', 'ㅃ', 'ᄈ')
    add('시5오1', 'ㅅ', 'ᄉ')
    add('이5응1', 'ㅇ', 'ᄋ', 'ᆼ')
    add('ᄐᅷ3이5응1', 'ㆆ', 'ᅙ')
    add('지5욷1', 'ㅈ', 'ᄌ')
    add('샹5지5욷1', 'ㅉ', 'ᄍ')
    add('치1웋', 'ㅊ', 'ᄎ')
    add('키1역', 'ㅋ', 'ᄏ', 'ᆿ')
    add('티1욷', 'ㅌ', 'ᄐ', 'ᇀ')
    add('피1얍', 'ㅍ', 'ᄑ', 'ᇁ')
    add('히1웋', 'ㅎ', 'ᄒ', 'ᇂ')
    add('리5일5히5웋', 'ㅀ', 'ᆶ')
    return readings


JAMO_PRONUNCIATION_READINGS = build_jamo_pronunciation_readings()


def jamo_pronunciation_reading(unit: str) -> str:
    """Return the full pronunciation reading for a standalone jamo letter."""
    return JAMO_PRONUNCIATION_READINGS.get(str(unit), '')


def audio_vowel_jamo_to_precomposed_unit(unit: str) -> str:
    """Map standalone vowel jamo to their ㅇ-initial audio syllable."""
    text = str(unit)
    if len(text) != 1:
        return ''

    ch = text[0]
    medial = ''
    if ch in COMPAT_TO_V:
        medial = COMPAT_TO_V[ch]
    elif ch in V_INDEX:
        medial = ch
    else:
        for candidate_medial, compat in V_TO_COMPAT.items():
            if compat == ch:
                medial = candidate_medial
                break

    if not medial or medial not in V_INDEX:
        return ''
    medial = AUDIO_EQUIVALENT_MEDIALS.get(medial, medial)
    return compose_syllable('ᄋ', medial, '')


def is_standalone_consonant_audio_unit(unit: str) -> bool:
    """True for consonant letters that should not request audio files."""
    text = str(unit)
    if len(text) != 1:
        return False
    ch = text[0]
    return (
        ch in COMPAT_TO_L
        or ch in COMPAT_TO_T
        or ch in set(T_TO_COMPAT.values())
        or is_initial_jamo(ch)
        or (ch in T_INDEX and ch != '')
    )


def split_untoned_hangul_units(text: str) -> list[str]:
    """Split a no-tone Hangul/Jamo chunk into likely syllable units.

    Exact tone-marked chunks such as 하이1 stay whole before this fallback is
    used.  This fallback is mainly for untoned text or for decomposing a missing
    whole-unit recording into smaller recorded units.
    """
    units: list[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if '\uAC00' <= ch <= '\uD7A3':
            units.append(ch)
            i += 1
            continue
        if ch == HANGUL_CHOSEONG_FILLER and i + 1 < len(text) and text[i + 1] in SPECIAL_MEDIALS:
            units.append(text[i:i + 2])
            i += 2
            continue
        if is_initial_jamo(ch):
            j = i + 1
            if j < len(text) and is_vowel_jamo(text[j]):
                j += 1
                # Jongseong finals are in the U+11xx table and T_INDEX.
                while j < len(text) and text[j] in T_INDEX and text[j] != '':
                    j += 1
                units.append(text[i:j])
                i = j
                continue
        if is_hangulish_for_tone(ch):
            units.append(ch)
        i += 1
    return [unit for unit in units if unit]


def audio_unit_end_at(text: str, start: int) -> int | None:
    """Return the end offset of one Hangul/Hokkien-Hangul audio unit.

    This is used before dictionary matching so an explicitly typed visible tone
    mark stays attached to the unit it follows.  It works for ordinary
    precomposed syllables and for Hokkien jamo clusters such as ᄋᅷ / ᄋᆤ / ᄋힻ.
    """
    if start < 0 or start >= len(text):
        return None

    ch = text[start]
    if '\uAC00' <= ch <= '\uD7A3':
        return start + 1

    if ch == HANGUL_CHOSEONG_FILLER and start + 1 < len(text) and text[start + 1] in SPECIAL_MEDIALS:
        return start + 2

    if is_initial_jamo(ch) and start + 1 < len(text) and is_vowel_jamo(text[start + 1]):
        end = start + 2
        while end < len(text) and text[end] in T_INDEX and text[end] != '':
            end += 1
        return end

    if is_hangulish_for_tone(ch):
        return start + 1

    return None


def split_audio_reading_units(reading: str) -> list[tuple[str, str]]:
    """Split a Hangul reading into (unit, tone_digit) audio keys.

    Examples:
        리1호2 -> [('리', '1'), ('호', '2')]
        하이1  -> [('하이', '1')]
        띤솅   -> [('띤', '3'), ('솅', '3')]
    """
    text = normalize_tone_symbols_to_digits(strip_nonstandard_reading_mark(str(reading)))
    units: list[tuple[str, str]] = []
    buf: list[str] = []

    def flush_default() -> None:
        nonlocal buf
        if not buf:
            return
        chunk = ''.join(buf)
        for unit in split_untoned_hangul_units(chunk):
            units.append((unit, '3'))
        buf = []

    for ch in text:
        if ch in TONE_DIGITS:
            if buf:
                units.append((''.join(buf), ch))
                buf = []
            continue
        if ch in INTERNAL_TONE_MARK_CHARS:
            if buf:
                units.append((''.join(buf), INTERNAL_TONE_MARK_TO_DIGIT[ch]))
                buf = []
            continue
        if is_hangulish_for_tone(ch):
            buf.append(ch)
            continue
        flush_default()

    flush_default()
    return units


def audio_sandhi_unit(unit: str, tone: str) -> tuple[str, str]:
    """Return the audio key after connected-speech tone sandhi.

    Recorded-audio playback uses citation audio for the final unit of a
    spacing-delimited run, but non-final units should use their sandhi tone.
    Example: 래4 + 쟣븡... with no space becomes 래3 + 쟣븡... for audio.
    """
    unit = str(unit)
    tone = str(tone or '3')
    if not unit or tone not in TONE_DIGITS:
        return unit, tone or '3'

    # Tone sandhi should follow the pronunciation-equivalent audio form.
    # Example: syllables ending in ㅈ use ㄷ audio, so they must also use the
    # checked-final ㄷ sandhi pattern for audio playback.
    audio_unit = canonicalize_audio_unit(unit)
    sandhi_reading = citation_to_sandhi_reading(audio_unit + tone)
    if not sandhi_reading:
        return audio_unit, tone

    sandhi_units = split_audio_reading_units(sandhi_reading)
    if len(sandhi_units) == 1:
        return sandhi_units[0]
    return unit, tone


def visible_text_to_audio_segments(text: str, audio_mode: str = AUDIO_MODE_TAIPEI) -> tuple[list[tuple[str, str, bool, bool, bool]], list[str]]:
    """Convert visible mixed text into audio segments.

    Returns (unit, tone, trim_start, trim_end, english_cluster_reduction) for each pronounceable audio unit.

    audio_mode='singapore' changes audio-file tone selection only: eligible
    tone 1 audio units are changed when the current syllable itself is not
    checked-final and the following syllable is directly connected with no space
    or punctuation in between.  Eligible tone 1 includes original/written tone 1
    and normal open tone 2 after ordinary Taipei sandhi changes it to tone 1.
    Checked-final tone 3 that becomes tone 1 through ordinary checked sandhi is
    not eligible.  The following syllable is treated as citation-final when it is
    followed by space/punctuation/apostrophe or by the end of the phrase/input.
    The IME text, TSV, and romanisation preview are not rewritten.

    Start/end trimming is based on phrase boundaries, not spaces:
        - first unit of the whole IME text, or first unit after , . ! ? : ; - —
          and their common CJK/fullwidth forms, keeps its start;
        - final unit of the whole IME text, or final unit before those same
          punctuations, keeps its end;
        - apostrophes do not reset first/last status.

    Dictionary-matched multi-syllable readings from the TSV are treated as
    already carrying their correct internal sandhi.  Therefore, if the TSV has
    an entry such as 어진덩 whose first part is already stored in sandhi form,
    playback does not sandhi 어/진 a second time.  Only the last unit of that
    matched entry may sandhi if it is directly followed by more Hangul/Hanri
    with no spacing/punctuation.

    Apostrophe rule: the final audio unit immediately before an apostrophe
    stays citation-final, even though it remains in the same phrase for
    clipping.  Earlier words before that unit still sandhi normally when they
    are followed by more Hangul/Hanri without punctuation.
    """
    source = format_text_tones_for_output(str(text), True, keep_literal_digit_markers=True)
    segments: list[tuple[str, str, bool, bool, bool]] = []
    unknown_hanri: list[str] = []
    # Each run part is (reading_text, protect_internal_sandhi, from_tsv, force_tone3).
    # Ordinary TSV words are protected internally because the TSV reading is
    # already the authoritative pronunciation for the word.  Numeric TSV/pattern
    # readings are from_tsv=True but protect_internal_sandhi=False, so compounds
    # like 12月 still sandhi across 잡+띠+月.  Raw typed Hangul is not from TSV.
    # from_tsv lets Singapore mode distinguish a word's citation tone 1 from a
    # word-internal or raw tone 1: citation tone 1 follows ordinary Taipei sandhi
    # first and must not be reprocessed by the Singapore special tone-1 rule.
    run_parts: list[tuple[str, bool, bool, bool, bool]] = []
    post_apostrophe_force_tone3 = False
    tone_chars = TONE_SYMBOLS.union(TONE_DIGITS).union(INTERNAL_TONE_MARK_CHARS)
    # Phrase units accumulate across spaces for trimming/crossfade, but the
    # Singapore tone-1 rule only applies across units that are directly connected
    # inside the same no-separator run.  Each item is:
    #     (unit, effective_tone, singapore_link_to_next, separator_after_unit, singapore_tone1_eligible)
    # where singapore_link_to_next is False after spaces or any punctuation,
    # including apostrophe.  singapore_tone1_eligible is True for raw/or already
    # word-internal tone 1.  Tone 1 created by ordinary Taipei sandhi, such as
    # open tone 2 -> tone 1 or checked tone 3 -> tone 1, is NOT reprocessed.
    # A TSV/Hanri word whose own citation tone is 1 is also excluded, so forms
    # such as 쟣희4 and separate Hanri 真 do not get accidentally reprocessed
    # as Singapore tone 1.
    phrase_units: list[tuple[str, str, bool, bool, bool]] = []

    def sandhi_final_raw_run_before_hyphen() -> None:
        nonlocal run_parts
        if not run_parts:
            return
        part_text, protect_internal_sandhi, from_tsv, force_tone3, protect_final_sandhi = run_parts[-1]
        if protect_internal_sandhi or from_tsv or force_tone3:
            return
        part_digits = normalize_tone_symbols_to_digits(part_text)
        if reading_has_tones(part_digits):
            return
        sandhi_reading = citation_to_sandhi_reading(part_digits)
        if sandhi_reading and sandhi_reading != part_text:
            run_parts[-1] = (
                sandhi_reading,
                protect_internal_sandhi,
                from_tsv,
                force_tone3,
                protect_final_sandhi,
            )

    def flush_run(force_citation: bool = False, explicit_separator_after: bool = False, continuation_after: bool = False) -> None:
        nonlocal run_parts, phrase_units
        if not run_parts:
            return

        flattened: list[tuple[str, str, bool, bool, bool]] = []
        for part_text, protect_internal_sandhi, from_tsv, force_tone3, protect_final_sandhi in run_parts:
            part_units = split_audio_reading_units(part_text)
            # Raw typed visible tone marks are intentional.  Do not rewrite them
            # with automatic audio sandhi.  TSV-matched readings are still handled
            # by the TSV protection rule below, because their tones are the
            # dictionary's authoritative pronunciation, not necessarily literal
            # user-forced tone marks.
            explicit_raw_tone = (
                (not protect_internal_sandhi)
                and (not from_tsv)
                and reading_has_tones(normalize_tone_symbols_to_digits(part_text))
            )
            # Unmarked raw Hangul typed directly in the IME is literal tone 3.
            # It must not be automatically sandhi-ed just because another Hangul
            # syllable follows.  The exception is when the visible Hangul matched
            # hokkien_hanri_dict.tsv, because a TSV reading is the authoritative
            # pronunciation and its final unit may still sandhi before a following
            # readable unit.
            raw_unmarked_hangul = bool(
                (not protect_internal_sandhi)
                and (not from_tsv)
                and (not explicit_raw_tone)
                and part_units
            )
            for part_idx, (unit, tone) in enumerate(part_units):
                if force_tone3:
                    tone = '3'
                # Protect only the internal non-final syllables of a TSV-matched
                # reading.  The final syllable remains free to sandhi if another
                # word is directly attached after it with no spacing/punctuation.
                # For unmatched raw Hangul with no tone mark, protect every unit:
                # unmarked means tone 3 regardless of position.
                protect_this_unit = bool(
                    force_tone3
                    or explicit_raw_tone
                    or raw_unmarked_hangul
                    or (
                        protect_final_sandhi
                        and part_idx == len(part_units) - 1
                    )
                    or (
                        protect_internal_sandhi
                        and part_idx < len(part_units) - 1
                    )
                )
                tsv_internal_unit = bool(protect_internal_sandhi and part_idx < len(part_units) - 1)
                tsv_final_citation_unit = bool(from_tsv and part_idx == len(part_units) - 1)
                flattened.append((unit, tone, protect_this_unit, tsv_internal_unit, tsv_final_citation_unit))

        for idx, (unit, tone, protect_sandhi, tsv_internal_unit, tsv_final_citation_unit) in enumerate(flattened):
            original_unit = unit
            original_tone = str(tone or '3')
            # In connected speech, every non-final unit in a no-space run should
            # use sandhi-tone audio, unless that unit is an internal syllable of
            # a TSV-matched reading whose sandhi is already encoded in the TSV.
            #
            # Apostrophe rule: a run immediately before an apostrophe stays in
            # citation tone for audio.  This is separate from clipping: those
            # syllables still remain in the same trimming phrase, so their audio
            # can still be start/end-clipped normally.
            if (
                (idx < len(flattened) - 1 or continuation_after)
                and not protect_sandhi
                and not force_citation
            ):
                # In Singapore audio mode, normal/open tone 1 has its own
                # context-dependent audio mapping.  Leave open tone 1 here so
                # flush_phrase() can inspect the following directly connected
                # unit; spaces and punctuation block that mapping.  Checked-final
                # tone 1 is NOT eligible for the Singapore special rule, so it
                # must still receive ordinary Taipei checked sandhi here (1 -> 3).
                # Other tones receive ordinary Taipei sandhi first.  If open
                # tone 2 becomes tone 1, that tone 1 remains as-is in Singapore.
                if not (
                    audio_mode == AUDIO_MODE_SINGAPORE
                    and str(tone) == '1'
                    and not audio_unit_has_short_overlap_final(unit)
                    and not tsv_final_citation_unit
                ):
                    unit, tone = audio_sandhi_unit(unit, tone)
            # Singapore tone-1 replacement applies only when the next
            # syllable is directly connected with no intervening space or
            # punctuation.  The last unit of every flushed run therefore cannot
            # look across the separator that caused the flush.  If that flush
            # was caused by an explicit separator, remember it so the previous
            # directly connected tone-1 syllable treats this final syllable as
            # citation-final for the dynamic Singapore decision.
            singapore_link_to_next = idx < len(flattened) - 1
            separator_after_unit = bool(explicit_separator_after and idx == len(flattened) - 1)
            singapore_tone1_eligible = bool(
                original_tone == '1'
                and not tsv_final_citation_unit
                and not (from_tsv and original_unit == '가')
            )
            phrase_units.append((unit, tone, singapore_link_to_next, separator_after_unit, singapore_tone1_eligible))
        run_parts = []

    def flush_phrase() -> None:
        nonlocal phrase_units
        if not phrase_units:
            return

        if audio_mode == AUDIO_MODE_SINGAPORE:
            # Singapore tone-1 replacement is dynamic: resolve from right to
            # left so a changed following tone can affect the tone-1 syllable
            # before it.  Links are still local: spaces, apostrophes, and other
            # punctuation break singapore_link_to_next, so the rule cannot jump
            # across separators.
            singapore_units: list[tuple[str, str, bool, bool, bool]] = [
                (unit, str(tone or '3'), singapore_link_to_next, separator_after_unit, singapore_tone1_eligible)
                for unit, tone, singapore_link_to_next, separator_after_unit, singapore_tone1_eligible in phrase_units
            ]
            for idx in range(len(singapore_units) - 2, -1, -1):
                unit, tone, singapore_link_to_next, separator_after_unit, singapore_tone1_eligible = singapore_units[idx]
                if (
                    singapore_link_to_next
                    and singapore_tone1_eligible
                    and not audio_unit_has_short_overlap_final(unit)
                ):
                    next_unit, next_tone, next_link_to_next, next_separator_after, _next_tone1_eligible = singapore_units[idx + 1]
                    next_is_citation_final = bool(next_separator_after or not next_link_to_next)
                    tone = singapore_tone1_audio_replacement(
                        next_unit,
                        next_tone,
                        next_has_explicit_separator_after=next_is_citation_final,
                    )
                    singapore_units[idx] = (unit, tone, singapore_link_to_next, separator_after_unit, singapore_tone1_eligible)
            phrase_units = singapore_units

        # Audio-only onset tensing:
        # a directly connected ㄷ-final syllable makes a following ㅇ-initial
        # syllable use its ㄸ-initial audio counterpart.
        # Example: 짇에 is looked up as 짇 + 떼.
        phrase_units = apply_d_final_onset_tensing_to_audio_phrase(phrase_units)

        english_reduction = english_cluster_reduction_flags(phrase_units)
        last_index = len(phrase_units) - 1
        for idx, (unit, tone, _singapore_link_to_next, _separator_after_unit, _singapore_tone1_eligible) in enumerate(phrase_units):
            trim_start = idx > 0
            trim_end = idx < last_index
            english_cluster_reduction = bool(idx < len(english_reduction) and english_reduction[idx])
            segments.append((unit, tone, trim_start, trim_end, english_cluster_reduction))
        phrase_units = []

    i = 0
    while i < len(source):
        tail = source[i:]
        ch = source[i]
        matched = False

        if ch == '[':
            end = source.find(']', i + 1)
            if end != -1:
                parsed = split_hanri_hangul_bracket_inner(source[i + 1:end])
                if parsed:
                    _hanri, reading = parsed
                    if (
                        end + 1 < len(source)
                        and source[end + 1] == '-'
                        and not reading_has_tones(normalize_tone_symbols_to_digits(reading))
                    ):
                        reading = citation_to_sandhi_reading(reading) or reading
                    run_parts.append((reading, True, True, post_apostrophe_force_tone3, True))
                    i = end + 1
                    continue

        # Apostrophes must be handled before dictionary matching.  The TSV may
        # contain apostrophe-prefixed attached forms such as ’에 / ’ᄅᆤ.  If we
        # let the normal dictionary matcher consume ’에 first, the run before
        # the apostrophe is never flushed as citation-final, so a preceding
        # syllable such as 쉬2 can be wrongly changed to sandhi 쉬1.
        #
        # Therefore: first flush the run before the apostrophe.  A normal flush
        # keeps only the final unit before the apostrophe citation-final, while
        # allowing earlier words to sandhi normally before following Hangul/Hanri.
        # Then, if a known apostrophe-prefixed TSV reading exists, consume that
        # attached form as the next run.  Straight apostrophe is matched against
        # curly-apostrophe TSV keys for pasted/raw text robustness.
        if ch in {"'", '’', '‘'}:
            flush_run(explicit_separator_after=True)
            normalized_tail = '’' + tail[1:]
            for key, reading in AUDIO_READING_INDEX:
                if key and key[0] in {"'", '’', '‘'} and normalized_tail.startswith('’' + key[1:]):
                    override = is_explicit_apostrophe_tone_override(key, reading)
                    run_parts.append((reading, True, True, not override, False))
                    i += len(key)
                    matched = True
                    break
            post_apostrophe_force_tone3 = True
            if matched:
                continue
            i += 1
            continue

        # If the user typed an explicit visible tone mark after a Hangul unit,
        # keep that tone attached before dictionary matching.  Otherwise a shorter
        # untoned dictionary key such as 짇 can consume the syllable first and
        # leave the following ˆ behind, causing tone 1 to be heard as tone 3.
        unit_end = audio_unit_end_at(source, i)
        if (
            unit_end is not None
            and unit_end < len(source)
            and source[unit_end] in tone_chars
            and can_attach_tone_to_text(source, unit_end - 1)
        ):
            tone_end = unit_end
            while tone_end < len(source) and source[tone_end] in tone_chars:
                tone_end += 1
            run_parts.append((source[i:tone_end], False, False, post_apostrophe_force_tone3, False))
            i = tone_end
            continue

        mixed_hanri_match = mixed_audio_hanri_match(source, i)
        if mixed_hanri_match:
            key, reading = mixed_hanri_match
            run_parts.append((mark_untoned_audio_units(reading), True, True, post_apostrophe_force_tone3, False))
            i += len(key)
            continue

        # Hanri conversion first: existing Chinese characters should pronounce
        # through the TSV reading rather than being treated as unknown text.
        hanri_match = static_audio_hanri_match(source, i)
        if hanri_match:
            key, reading = hanri_match
            run_parts.append((mark_untoned_audio_units(reading), True, True, post_apostrophe_force_tone3, False))
            i += len(key)
            continue

        # Hangul word/reading match, useful for text that is still pure Hangul.
        for key, reading in AUDIO_READING_INDEX:
            if key and tail.startswith(key):
                match_end = i + len(key)
                explicit_final_tone = reading_has_tones(normalize_tone_symbols_to_digits(key))
                reading_text = reading
                if match_end < len(source) and source[match_end] in tone_chars:
                    tone_end = match_end
                    while tone_end < len(source) and source[tone_end] in tone_chars:
                        tone_end += 1
                    reading_text = str(reading) + source[match_end:tone_end]
                    explicit_final_tone = True
                    i = tone_end
                else:
                    i += len(key)
                run_parts.append((reading_text, True, True, post_apostrophe_force_tone3, explicit_final_tone))
                matched = True
                break
        if matched:
            continue

        if ch in tone_chars and i > 0 and not can_attach_tone_to_text(source, i - 1):
            flush_run()
            i += 1
            continue

        literal_number = literal_number_reading_at(source, i)
        if literal_number is not None:
            reading, digit_end = literal_number
            # Numeric readings are dictionary-owned, but their internal syllables
            # still participate in ordinary connected-speech sandhi before the
            # following classifier/date word.
            run_parts.append((reading, False, True, post_apostrophe_force_tone3, False))
            i = digit_end
            continue

        ch = source[i]
        if ch in TONE_SYMBOLS or ch in TONE_DIGITS:
            # A visible/internal tone mark belongs to the preceding raw Hangul
            # unit.  Keep it attached before split_audio_reading_units() runs;
            # otherwise a typed form such as 자ˉ뻐 would lose the 5-tone and be
            # treated like untoned 자.
            if can_attach_tone_to_text(source, i - 1) and run_parts and not run_parts[-1][1]:
                previous_text, previous_protect, previous_from_tsv, previous_force_tone3, previous_protect_final = run_parts[-1]
                run_parts[-1] = (
                    previous_text + ch,
                    previous_protect,
                    previous_from_tsv,
                    previous_force_tone3 or post_apostrophe_force_tone3,
                    previous_protect_final,
                )
            else:
                flush_run()
        elif is_hangulish_for_tone(ch):
            # Raw Hokkien jamo clusters must stay as one audio unit.
            # Example: ᄀᅷ should look up ᄀᅷ3.wav, not separate ᄀ3 + ᅷ3.
            # The same applies to clusters with finals such as ᄀᅷᆯ.
            unit_end = audio_unit_end_at(source, i)
            if unit_end is not None and unit_end > i:
                unit_text = source[i:unit_end]
                pronunciation = jamo_pronunciation_reading(unit_text)
                if pronunciation:
                    run_parts.append((pronunciation, True, True, post_apostrophe_force_tone3, True))
                else:
                    run_parts.append((unit_text, False, False, post_apostrophe_force_tone3, False))
                i = unit_end - 1
            else:
                pronunciation = jamo_pronunciation_reading(ch)
                if pronunciation:
                    run_parts.append((pronunciation, True, True, post_apostrophe_force_tone3, True))
                else:
                    run_parts.append((ch, False, False, post_apostrophe_force_tone3, False))
        elif is_hanri_char(ch):
            flush_run()
            unknown_hanri.append(ch)
        elif is_latin_word_start(ch):
            latin_end = latin_word_end(source, i)
            flush_run(explicit_separator_after=True, continuation_after=True)
            unknown_hanri.append(f'{source[i:latin_end]} (English has no recorded audio)')
            i = latin_end - 1
        elif ch == '-':
            sandhi_final_raw_run_before_hyphen()
            flush_run(explicit_separator_after=True, continuation_after=True)
        elif is_audio_phrase_boundary(ch):
            flush_run(explicit_separator_after=True)
            flush_phrase()
            if ch.isspace():
                post_apostrophe_force_tone3 = False
        elif is_ignored_audio_punctuation(ch):
            # Apostrophes break the sandhi run and force the preceding run to
            # stay in citation tone, but they do not create a new trimming
            # phrase. Spaces simply break the sandhi run.  For Singapore audio
            # sandhi, all such explicit separators also make the previous audio
            # unit citation-final for the syllable before it.
            flush_run(force_citation=(ch in {"'", '’', '‘'}), explicit_separator_after=True)
            if ch.isspace():
                post_apostrophe_force_tone3 = False
        else:
            # Other symbols are separators for sandhi, not audio errors and not
            # first/last reset punctuation.
            flush_run(explicit_separator_after=True)
        i += 1

    flush_run()
    flush_phrase()
    return segments, unknown_hanri


_AUDIO_FILENAME_CONVERTER = None


_AUDIO_FILENAME_CONVERTER_LOAD_FAILED = False


def load_audio_filename_converter():
    """Load the Lomari converter for ASCII-safe audio filenames."""
    global _AUDIO_FILENAME_CONVERTER, _AUDIO_FILENAME_CONVERTER_LOAD_FAILED
    if _AUDIO_FILENAME_CONVERTER is not None:
        return _AUDIO_FILENAME_CONVERTER
    if _AUDIO_FILENAME_CONVERTER_LOAD_FAILED:
        return None

    path = TONE_MARKER_MODULE_PATH
    try:
        if not path.exists():
            _AUDIO_FILENAME_CONVERTER_LOAD_FAILED = True
            return None
        spec = importlib.util.spec_from_file_location('hokkien_audio_filename_converter', path)
        if spec is None or spec.loader is None:
            _AUDIO_FILENAME_CONVERTER_LOAD_FAILED = True
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        if not hasattr(module, 'auto_lomari_from_hangul'):
            _AUDIO_FILENAME_CONVERTER_LOAD_FAILED = True
            return None
        _AUDIO_FILENAME_CONVERTER = module
        return module
    except Exception:
        _AUDIO_FILENAME_CONVERTER_LOAD_FAILED = True
        return None


def audio_lomari_key_from_unit(unit: str) -> str:
    """Return the ASCII Lomari-key spelling used for audio filenames.

    Visible Lomari writes nasalisation with combining tilde-below, e.g. a̰.
    Audio files stay ASCII/cloud-safe and follow the keyboard spelling, e.g. al.
    """
    text = str(unit or '')
    if not text:
        return ''

    if len(text) >= 2 and text[0] == HANGUL_CHOSEONG_FILLER and text[1] in SPECIAL_MEDIALS:
        return LOMARI_V_TO_RIME.get(text[1], '')

    decomposed = decompose_precomposed_syllable(text[0]) if text else None
    if decomposed is not None:
        initial, medial, final = decomposed
        return cluster_to_base_lomari_for_ime(initial, medial, final)

    if len(text) >= 2 and ('\u1100' <= text[0] <= '\u1112' or text[0] == HANGUL_CHOSEONG_FILLER) and (
        '\u1161' <= text[1] <= '\u1175' or text[1] in SPECIAL_MEDIALS
    ):
        initial = text[0]
        medial = text[1]
        final = ''
        if len(text) >= 3 and '\u11A8' <= text[2] <= '\u11FF':
            final = text[2]
        return cluster_to_base_lomari_for_ime(initial, medial, final)

    if len(text) == 1 and text in COMPAT_TO_V:
        return LOMARI_V_TO_RIME.get(COMPAT_TO_V[text], '')
    if len(text) == 1 and text in COMPAT_TO_L:
        return LOMARI_L_TO_INITIAL.get(COMPAT_TO_L[text], '')
    return ''


def audio_lomari_filename_stem(unit: str, tone: str) -> str:
    """Return the ASCII Lomari-key stem used by renamed audio files."""
    key_stem = audio_lomari_key_from_unit(unit)
    if key_stem:
        return re.sub(r'[^A-Za-z0-9._-]+', '_', key_stem).strip('._-')

    converter = load_audio_filename_converter()
    lomari = ''
    if converter is not None:
        try:
            lomari = converter.auto_lomari_from_hangul(f'{unit}{tone}')
        except Exception:
            lomari = ''
    if not lomari:
        try:
            lomari = hangul_unit_to_lomari(unit)
        except Exception:
            lomari = ''
    if not lomari:
        return ''
    plain = ''.join(
        ch for ch in unicodedata.normalize('NFKD', str(lomari))
        if not unicodedata.combining(ch)
    )
    return re.sub(r'[^A-Za-z0-9._-]+', '_', plain).strip('._-')


def audio_collision_safe_filename_stem(unit: str) -> str:
    """Return the preferred lowercase-safe recorder stem.

    The normal Lomari keyboard uses U internally for ㅡ, but ㅡ is a null vowel
    in filename Lomari and contributes no letters: 즈 -> j, 승 -> sng.
    """
    parsed = audio_unit_initial_medial_final(str(unit or ''))
    if parsed is None:
        return ''
    initial, medial, final = parsed
    vowel = {'ᅳ': '', 'ᅴ': 'eui'}.get(medial)
    if vowel is None:
        return ''
    initial_stem = 'ng' if initial == 'ᅙ' else LOMARI_L_TO_INITIAL.get(initial, '')
    final_stem = LOMARI_FINAL_TO_CODA.get(final, '')
    if final == 'ᆯ':
        final_stem = 'l'
    elif final == 'ᆶ':
        final_stem = 'lh'
    return initial_stem + vowel + final_stem


def audio_lomari_filename_stem_aliases(unit: str) -> list[str]:
    """Return preferred and legacy ASCII audio stems."""
    text = str(unit or '')
    aliases: list[str] = []
    safe_stem = audio_collision_safe_filename_stem(text)
    if safe_stem:
        aliases.append(safe_stem)
    parsed = audio_unit_initial_medial_final(text)
    if parsed is not None:
        initial, medial, final = parsed
        if medial == 'ᅳ':
            initial_stem = LOMARI_L_TO_INITIAL.get(initial, '')
            final_stem = LOMARI_FINAL_TO_CODA.get(final, '')
            if final == 'ᆯ':
                final_stem = 'l'
            elif final == 'ᆶ':
                final_stem = 'lh'
            aliases.append(f'{initial_stem}eu{final_stem}')
    return list(dict.fromkeys(aliases))


def audio_filename_candidates(unit: str, tone: str) -> list[str]:
    """Likely filenames for one recorded syllable/tone."""
    unit = canonicalize_audio_unit(unit)
    symbol = display_reading_tones(tone)
    stems: list[str] = []
    collision_safe_stem = audio_collision_safe_filename_stem(unit)
    if collision_safe_stem:
        stems.extend([
            f'{collision_safe_stem}{tone}',
            f'{collision_safe_stem}_{tone}',
            f'{collision_safe_stem}_t{tone}',
            f'{collision_safe_stem}-{tone}',
        ])
    lomari_stem = audio_lomari_filename_stem(unit, tone)
    if lomari_stem:
        stems.extend([
            f'{lomari_stem}{tone}',
            f'{lomari_stem}_{tone}',
            f'{lomari_stem}_t{tone}',
            f'{lomari_stem}-{tone}',
        ])
    for alias_stem in audio_lomari_filename_stem_aliases(unit):
        stems.extend([
            f'{alias_stem}{tone}',
            f'{alias_stem}_{tone}',
            f'{alias_stem}_t{tone}',
            f'{alias_stem}-{tone}',
        ])
    stems.extend([
        f'{unit}{tone}',
        f'{unit}_{tone}',
        f'{unit}_t{tone}',
        f'{unit}-{tone}',
    ])
    if symbol:
        stems.extend([
            f'{unit}{symbol}',
            f'{unit}_{symbol}',
            f'{unit}-{symbol}',
        ])
    if tone == '3':
        stems.extend([unit, f'{unit}_3', f'{unit}_t3', f'{unit}-3'])

    result: list[str] = []
    seen: set[str] = set()
    for stem in stems:
        for ext in AUDIO_FILE_EXTENSIONS:
            name = stem + ext
            if name not in seen:
                result.append(name)
                seen.add(name)
    return result


_AUDIO_FILE_INDEX_CACHE: dict[str, dict[str, Path]] = {}


def audio_file_index(folder: Path) -> dict[str, Path]:
    """Return a cached filename index for flat or initial-folder audio layouts."""
    key = str(folder.resolve()) if folder.exists() else str(folder)
    cached = _AUDIO_FILE_INDEX_CACHE.get(key)
    if cached is not None:
        return cached

    index: dict[str, Path] = {}
    if folder.exists():
        for path in folder.rglob('*'):
            if path.is_file():
                index.setdefault(path.name, path)
    _AUDIO_FILE_INDEX_CACHE[key] = index
    return index


def find_audio_file(folder: Path, unit: str, tone: str) -> Path | None:
    lookup_tone = audio_lookup_tone_for_unit(unit, tone)
    index = audio_file_index(folder)
    for lookup_unit in audio_lookup_units(unit):
        for name in audio_filename_candidates(lookup_unit, lookup_tone):
            path = folder / name
            if path.exists() and path.is_file():
                return path
            indexed_path = index.get(name)
            if indexed_path is not None and indexed_path.exists() and indexed_path.is_file():
                return indexed_path
    return None


def audio_lookup_tone_for_unit(unit: str, tone: str) -> str:
    """Standalone vowel jamo use tone-1 syllable recordings."""
    text = str(unit)
    if (
        len(text) == 1
        and decompose_precomposed_syllable(text) is None
        and audio_vowel_jamo_to_precomposed_unit(text)
        and audio_vowel_jamo_to_precomposed_unit(text) != '으'
    ):
        return '1'
    return str(tone or '3')


def audio_missing_label_for_unit(unit: str, tone: str) -> str:
    lookup_tone = audio_lookup_tone_for_unit(unit, tone)
    lookup_unit = audio_vowel_jamo_to_precomposed_unit(unit) or str(unit)
    return f'{lookup_unit}{lookup_tone}'


def resolve_audio_parts_for_unit(folder: Path, unit: str, tone: str) -> tuple[list[tuple[Path, str, str]], list[str]]:
    """Resolve recordings without losing a partial chunk's syllables or tones.

    Earlier parts use tone 3 and the final part uses the supplied tone, as in
    the existing decomposition contract. Missing parts must not discard known
    neighbours or fall through to an alias for only the first syllable.
    """
    parts = split_untoned_hangul_units(unit)
    if len(parts) > 1:
        resolved: list[tuple[Path, str, str]] = []
        missing: list[str] = []
        for idx, part in enumerate(parts):
            part_tone = tone if idx == len(parts) - 1 else '3'
            path = find_audio_file(folder, part, part_tone)
            if path is None:
                missing.append(audio_missing_label_for_unit(part, part_tone))
            else:
                resolved.append((path, part, str(part_tone)))
        return resolved, missing

    direct = find_audio_file(folder, unit, tone)
    if direct is not None:
        return [(direct, unit, str(tone))], []

    return [], [audio_missing_label_for_unit(unit, tone)]


def is_silent_audio_unit(unit: str, tone: str) -> bool:
    """True for written units that intentionally have no Hokkien audio."""
    if str(tone or '3') not in TONE_DIGITS:
        return False
    text = str(unit)
    if jamo_pronunciation_reading(text):
        return False
    return (
        (text == '으' and str(tone or '3') != '1')
        or (audio_vowel_jamo_to_precomposed_unit(text) == '으' and str(tone or '3') != '1')
        or is_standalone_consonant_audio_unit(text)
    )


def is_vowel_jamo(ch: str) -> bool:
    return ch in V_INDEX or ch in SPECIAL_MEDIALS


def is_initial_jamo(ch: str) -> bool:
    return ch in L_INDEX or ch in EXTRA_INITIALS


# -----------------------------
# Lomari (romanisation) input mode
# -----------------------------
# Lomari mode is case-sensitive for shifted vowel input:
#   lowercase vowels/rimes create ㅇ-initial Tangliengim syllables;
#   Shift+U/I create 으/의;
#   Lomari mode produces complete syllables; bare roman initials stay literal
#   until a vowel/rime completes them.  Syllabic ng still types 응; mm types 음.
#   Shift+G creates ㆆ, and Shift+N creates ㅇ;
#   w/y are reserved for intuitive glide aliases such as we/ya/yor/yo/yu;
#   uppercase consonants fall back to lowercase.
# There is no x null-initial marker and no obsolete uor/wor compound-vowel input.
# Aspirates can be typed by Lomari digraphs kh/ph/th/ch, or by z/v/x/c shortcuts.
LOMARI_INITIAL_TO_L = {
    'kh': 'ᄏ', 'th': 'ᄐ', 'ph': 'ᄑ', 'ch': 'ᄎ', 'js': 'ᄍ',
    'k': 'ᄀ', 'g': 'ᄁ', 'n': 'ᄂ', 't': 'ᄃ', 'r': 'ᄄ', 'l': 'ᄅ',
    'm': 'ᄆ', 'p': 'ᄇ', 'b': 'ᄈ', 's': 'ᄉ', 'j': 'ᄌ', 'h': 'ᄒ',
}


LOMARI_SHORTCUT_INITIALS = {
    'z': 'ᄏ',
    'x': 'ᄐ',
    'c': 'ᄎ',
    'v': 'ᄑ',
}


LOMARI_L_TO_INITIAL = {v: k for k, v in LOMARI_INITIAL_TO_L.items()}


LOMARI_V_TO_RIME = {
    'ᅡ': 'a',
    'ᅢ': 'ai',
    'ᅣ': 'ia',
    'ᅥ': 'or',
    'ᅦ': 'e',
    'ᅧ': 'ior',
    'ᅨ': 'ie',
    'ᅩ': 'o',
    'ᅪ': 'oa',
    'ᅫ': 'oai',
    'ᅬ': 'oe',
    'ᅭ': 'io',
    'ᅮ': 'u',
    'ᅰ': 'ue',
    'ᅱ': 'ui',
    'ᅲ': 'iu',
    'ᅳ': 'U',
    'ᅴ': 'I',
    'ᅵ': 'i',
    'ힻ': 'er',
    'ᅷ': 'au',
    'ᆤ': 'iau',
}


LOMARI_FINAL_TO_CODA = {
    '': '',
    'ᆨ': 'k',
    'ᆫ': 'n',
    'ᆮ': 't',
    'ᆯ': 'l',
    'ᆷ': 'm',
    'ᆸ': 'p',
    'ᆼ': 'ng',
    'ᇂ': 'h',
    'ᆶ': 'h',
}


def lomari_glide_if_null_initial(initial: str, medial: str, rime: str) -> str:
    if initial != 'ᄋ':
        return rime
    if medial in {'ᅵ', 'ᅮ', 'ᅴ'}:
        return rime
    if rime.startswith('i'):
        return 'y' + rime[1:]
    if rime.startswith('u'):
        return 'w' + rime[1:]
    return rime


def cluster_to_base_lomari_for_ime(initial: str, medial: str, final: str) -> str:
    ini = LOMARI_L_TO_INITIAL.get(initial, '')

    if medial == 'ᅳ' and final == 'ᆫ':
        return ini + 'n'

    if medial == 'ᅥ':
        if final == 'ᆯ':
            rime = 'orl'
        elif final == 'ᆶ':
            rime = 'orlh'
        elif final == '':
            rime = 'or'
        elif final == 'ᇂ':
            rime = 'orh'
        elif final == 'ᆼ':
            rime = 'ong'
        else:
            rime = 'or' + LOMARI_FINAL_TO_CODA.get(final, '')
        return ini + lomari_glide_if_null_initial(initial, medial, rime)

    if medial == 'ᅧ':
        if final == 'ᆯ':
            rime = 'iorl'
        elif final == 'ᆶ':
            rime = 'iorlh'
        elif final == '':
            rime = 'ior'
        elif final == 'ᇂ':
            rime = 'iorh'
        elif final == 'ᆼ':
            rime = 'iong'
        else:
            rime = 'ior' + LOMARI_FINAL_TO_CODA.get(final, '')
        return ini + lomari_glide_if_null_initial(initial, medial, rime)

    if final == 'ᆯ':
        vow = LOMARI_V_TO_RIME.get(medial, '')
        rime = vow + 'l'
        return ini + lomari_glide_if_null_initial(initial, medial, rime)

    if final == 'ᆶ':
        vow = LOMARI_V_TO_RIME.get(medial, '')
        rime = vow + 'l'
        return ini + lomari_glide_if_null_initial(initial, medial, rime) + 'h'

    vow = LOMARI_V_TO_RIME.get(medial, '')
    fin = LOMARI_FINAL_TO_CODA.get(final, '')
    return ini + lomari_glide_if_null_initial(initial, medial, vow + fin)


def build_ng_initial_syllable_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    medials = [
        'ᅡ', 'ᅢ', 'ᅣ', 'ᅥ', 'ᅦ', 'ᅧ', 'ᅨ', 'ᅩ', 'ᅪ', 'ᅫ', 'ᅬ',
        'ᅭ', 'ᅮ', 'ᅰ', 'ᅱ', 'ᅲ', 'ᅳ', 'ᅴ', 'ᅵ', 'ힻ', 'ᅷ', 'ᆤ',
    ]
    finals = ['', 'ᆨ', 'ᆫ', 'ᆮ', 'ᆯ', 'ᆷ', 'ᆸ', 'ᆼ', 'ᇂ', 'ᆶ']
    for medial in medials:
        for final in finals:
            if final and medial == 'ힻ':
                continue
            rime = cluster_to_base_lomari_for_ime('ᅙ', medial, final)
            if rime:
                mapping.setdefault('ng' + rime, compose_syllable('ᅙ', medial, final))
    mapping['ngwe'] = compose_syllable('ᅙ', 'ힻ', '')
    return mapping


def build_lomari_syllable_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    initials = [
        'ᄋ', 'ᅙ', 'ᄀ', 'ᄁ', 'ᄂ', 'ᄃ', 'ᄄ', 'ᄅ', 'ᄆ', 'ᄇ', 'ᄈ', 'ᄉ',
        'ᄌ', 'ᄍ', 'ᄎ', 'ᄏ', 'ᄐ', 'ᄑ', 'ᄒ',
    ]
    medials = [
        'ᅡ', 'ᅢ', 'ᅣ', 'ᅥ', 'ᅦ', 'ᅧ', 'ᅨ', 'ᅩ', 'ᅪ', 'ᅫ', 'ᅬ',
        'ᅭ', 'ᅮ', 'ᅰ', 'ᅱ', 'ᅲ', 'ᅳ', 'ᅴ', 'ᅵ', 'ힻ', 'ᅷ', 'ᆤ',
    ]
    finals = ['', 'ᆨ', 'ᆫ', 'ᆮ', 'ᆯ', 'ᆷ', 'ᆸ', 'ᆼ', 'ᇂ', 'ᆶ']

    for initial in initials:
        if initial == 'ᅙ':
            continue
        for medial in medials:
            for final in finals:
                if final and medial == 'ힻ':
                    continue
                key = cluster_to_base_lomari_for_ime(initial, medial, final)
                if key:
                    mapping.setdefault(key, compose_syllable(initial, medial, final))

    for roman_initial, initial_jamo in LOMARI_SHORTCUT_INITIALS.items():
        canonical_initial = LOMARI_L_TO_INITIAL.get(initial_jamo, '')
        if not canonical_initial:
            continue
        for medial in medials:
            for final in finals:
                if final and medial == 'ힻ':
                    continue
                canonical_key = cluster_to_base_lomari_for_ime(initial_jamo, medial, final)
                if canonical_key and canonical_key.startswith(canonical_initial):
                    alias_key = roman_initial + canonical_key[len(canonical_initial):]
                    mapping.setdefault(alias_key, compose_syllable(initial_jamo, medial, final))

    for initial in initials:
        ini = LOMARI_L_TO_INITIAL.get(initial, '')
        if not ini:
            continue
        mapping[ini + 'n'] = compose_syllable(initial, 'ᅳ', 'ᆫ')
        mapping[ini + 'ng'] = compose_syllable(initial, 'ᅳ', 'ᆼ')

    null_vowels = {
        'a': 'ᅡ', 'ai': 'ᅢ', 'ia': 'ᅣ', 'ya': 'ᅣ', 'e': 'ᅦ',
        'ior': 'ᅧ', 'yor': 'ᅧ', 'ie': 'ᅨ', 'o': 'ᅩ', 'oa': 'ᅪ', 'oai': 'ᅫ',
        'oe': 'ᅬ', 'io': 'ᅭ', 'yo': 'ᅭ', 'u': 'ᅮ', 'ue': 'ᅰ', 'we': 'ᅰ',
        'ui': 'ᅱ', 'iu': 'ᅲ', 'yu': 'ᅲ', 'i': 'ᅵ',
        'er': 'ힻ', 'au': 'ᅷ', 'iau': 'ᆤ',
    }
    for key, medial in null_vowels.items():
        mapping[key] = compose_syllable('ᄋ', medial, '')

    mapping.update(build_ng_initial_syllable_map())

    for medial in medials:
        for final in finals:
            if not final or final in {'ᆯ', 'ᆶ'} or (final and medial == 'ힻ'):
                continue
            key = cluster_to_base_lomari_for_ime('ᄋ', medial, final)
            if key:
                syllable = compose_syllable('ᄋ', medial, final)
                mapping.setdefault(key, syllable)
                if key.startswith('y'):
                    mapping.setdefault('i' + key[1:], syllable)

    alias_syllables = {
        'ya': compose_syllable('ᄋ', 'ᅣ', ''),
        'yor': compose_syllable('ᄋ', 'ᅧ', ''),
        'yo': compose_syllable('ᄋ', 'ᅭ', ''),
        'yu': compose_syllable('ᄋ', 'ᅲ', ''),
        'we': compose_syllable('ᄋ', 'ᅰ', ''),
    }
    for roman_initial, initial_jamo in LOMARI_INITIAL_TO_L.items():
        if roman_initial == 'ng':
            continue
        compat_initial = L_TO_COMPAT.get(initial_jamo, initial_jamo)
        for alias, syllable in alias_syllables.items():
            mapping.setdefault(roman_initial + alias, compat_initial + syllable)

    for roman_initial, initial_jamo in LOMARI_SHORTCUT_INITIALS.items():
        canonical_initial = LOMARI_L_TO_INITIAL.get(initial_jamo, '')
        for suffix in ('n', 'ng'):
            canonical_key = canonical_initial + suffix
            if canonical_key in mapping:
                mapping.setdefault(roman_initial + suffix, mapping[canonical_key])
        compat_initial = L_TO_COMPAT.get(initial_jamo, initial_jamo)
        for alias, syllable in alias_syllables.items():
            mapping.setdefault(roman_initial + alias, compat_initial + syllable)

    # Bare n/m should stay literal under the Lomari-first reform.  They are
    # produced by systematic null-initial ㅡ+final generation above, so remove
    # them after the full syllable map is built.  Keep ng/mm as explicit
    # syllabic nasal exceptions.
    mapping.pop('n', None)
    mapping.pop('m', None)
    mapping['ng'] = compose_syllable('ᄋ', 'ᅳ', 'ᆼ')
    mapping['mm'] = compose_syllable('ᄋ', 'ᅳ', 'ᆷ')

    glide_initial_rimes = {
        'ia': 'ᅣ',
        'iau': 'ᆤ',
        'ior': 'ᅧ',
        'ie': 'ᅨ',
        'io': 'ᅭ',
        'iu': 'ᅲ',
        'ue': 'ᅰ',
        'ui': 'ᅱ',
    }
    for roman_initial, initial_jamo in {
        **LOMARI_INITIAL_TO_L,
        **LOMARI_SHORTCUT_INITIALS,
    }.items():
        for rime, medial in glide_initial_rimes.items():
            mapping[roman_initial + rime] = compose_syllable(initial_jamo, medial, '')

    return mapping


LOMARI_SYLLABLE_MAP = build_lomari_syllable_map()


# -----------------------------
# Read-only Hangul -> Lomari preview
# -----------------------------
# This preview deliberately does NOT use the Lomari keyboard input map.
# It follows the Hangul -> Lomari conversion logic from the tone-marker program.
PREVIEW_CHOSEONG_TO_LOMARI = {
    'ᄋ': '',
    'ᄀ': 'k', 'ᄁ': 'g',
    'ᄂ': 'n',
    'ᄃ': 't', 'ᄄ': 'r',
    'ᄅ': 'l',
    'ᄆ': 'm',
    'ᄇ': 'p', 'ᄈ': 'b',
    'ᄉ': 's',
    'ᄌ': 'j', 'ᄍ': 'js',
    'ᄎ': 'ch',
    'ᄏ': 'kh',
    'ᄐ': 'th',
    'ᄑ': 'ph',
    'ᄒ': 'h',
    'ᅙ': 'ng',
}


PREVIEW_JUNGSEONG_TO_LOMARI = {
    'ᅡ': 'a',
    'ᅢ': 'ai',
    'ᅣ': 'ia',
    'ᅥ': 'or',
    'ᅦ': 'e',
    'ᅧ': 'ior',
    'ᅨ': 'ie',
    'ᅩ': 'o',
    'ᅪ': 'oa',
    'ᅫ': 'oai',
    'ᅬ': 'oe',
    'ᅭ': 'io',
    'ᅮ': 'u',
    'ᅰ': 'ue',
    'ᅱ': 'ui',
    'ᅲ': 'iu',
    'ᅳ': '',
    'ᅴ': 'i',
    'ᅵ': 'i',
    'ힻ': 'er',
    'ᅷ': 'au',
    'ᆤ': 'iau',
}


PREVIEW_JONGSEONG_TO_LOMARI = {
    '': '',
    'ᆨ': 'k',
    'ᆫ': 'n',
    'ᆮ': 't',
    'ᆯ': 'l',
    'ᆷ': 'm',
    'ᆸ': 'p',
    'ᆼ': 'ng',
    'ᇂ': 'h',
}


PREVIEW_TONE_PRIORITY_LOMARI = ['a', 'e', 'o', 'u', 'i', 'n', 'm']


PREVIEW_NASAL_TILDE_BELOW = '\u0330'


def is_latin_word_start(ch: str) -> bool:
    return ('A' <= ch <= 'Z') or ('a' <= ch <= 'z')


def latin_word_end(text: str, index: int) -> int:
    end = index
    while end < len(text) and (
        ('A' <= text[end] <= 'Z')
        or ('a' <= text[end] <= 'z')
        or ('0' <= text[end] <= '9')
    ):
        end += 1
    return end


def preview_lomari_mark_target_index(body: str) -> int | None:
    body_lower = body.lower()
    for letter in PREVIEW_TONE_PRIORITY_LOMARI:
        idxs = [
            i for i, ch in enumerate(body_lower)
            if ch == letter and not unicodedata.combining(ch)
        ]
        if not idxs:
            continue
        return idxs[1] if letter in ('n', 'm') and len(idxs) > 1 else idxs[0]
    for idx, ch in enumerate(body):
        if ch.isalpha():
            return idx
    return None


def preview_add_combining_mark_to_lomari_target(body: str, mark: str) -> str:
    if not mark:
        return body
    idx = preview_lomari_mark_target_index(body)
    if idx is None:
        return body
    end = idx + 1
    while end < len(body) and unicodedata.combining(body[end]):
        if body[end] == mark:
            return body
        end += 1
    return body[:end] + mark + body[end:]


def preview_nasalize_lomari_rime(rime: str) -> str:
    return preview_add_combining_mark_to_lomari_target(rime, PREVIEW_NASAL_TILDE_BELOW)


def preview_double_final_vowel(rime: str) -> str:
    """Mark nasalisation on the same target letter used for tone marks."""
    return preview_nasalize_lomari_rime(rime)


def preview_glide_if_null_initial(initial: str, medial: str, rime: str) -> str:
    """Use y/w for null-initial compound vowels, matching the tone marker."""
    if initial != 'ᄋ':
        return rime
    if medial in ('ᅵ', 'ᅮ', 'ᅴ'):
        return rime
    if rime.startswith('i'):
        return 'y' + rime[1:]
    if rime.startswith('u'):
        return 'w' + rime[1:]
    return rime


def preview_special_rime_oe_yeo(medial: str, final: str) -> str | None:
    """Special ㅓ/ㅕ + final behaviour from the tone-marker program."""
    if medial == 'ᅥ':
        if final == 'ᆯ':
            return preview_nasalize_lomari_rime('or')
        if final == 'ᆶ':
            return preview_nasalize_lomari_rime('or') + 'h'
        if final == '':
            return 'or'
        if final == 'ᇂ':
            return 'orh'
        if final == 'ᆼ':
            return 'o' + PREVIEW_JONGSEONG_TO_LOMARI.get(final, '')
        return 'or' + PREVIEW_JONGSEONG_TO_LOMARI.get(final, '')

    if medial == 'ᅧ':
        if final == 'ᆯ':
            return preview_nasalize_lomari_rime('ior')
        if final == 'ᆶ':
            return preview_nasalize_lomari_rime('ior') + 'h'
        if final == '':
            return 'ior'
        if final == 'ᇂ':
            return 'iorh'
        if final == 'ᆼ':
            return 'io' + PREVIEW_JONGSEONG_TO_LOMARI.get(final, '')
        return 'ior' + PREVIEW_JONGSEONG_TO_LOMARI.get(final, '')

    return None


def preview_cluster_to_base_lomari(initial: str, medial: str, final: str = '') -> str:
    """Romanise one Hangul initial/medial/final cluster for preview output."""
    ini = PREVIEW_CHOSEONG_TO_LOMARI.get(initial, '')

    if medial == 'ᅳ' and final == 'ᆫ':
        return ini + 'n'

    rime = preview_special_rime_oe_yeo(medial, final)
    if rime is not None:
        return ini + preview_glide_if_null_initial(initial, medial, rime)

    # Romanisation preview must keep written ㅚ as Lomari oe.
    # Audio lookup may share ㅚ recordings with ㅞ, but that pronunciation
    # equivalence must not leak into the displayed/copyable Lomari line.
    if medial == 'ᅬ':
        vow = 'oe'
        l_cluster_finals_for_oe = {
            'ᆶ': 'h',  # ㅀ
            'ᆰ': 'k',
            'ᇍ': 'n',
            'ᇎ': 't',
            'ᆱ': 'm',
            'ᆲ': 'p',
            'ᆴ': 't',
        }
        if final == 'ᆯ':
            rime = preview_double_final_vowel(vow)
        elif final in l_cluster_finals_for_oe:
            rime = preview_double_final_vowel(vow) + l_cluster_finals_for_oe[final]
        else:
            rime = vow + PREVIEW_JONGSEONG_TO_LOMARI.get(final, '')
        rime = preview_glide_if_null_initial(initial, medial, rime)
        return ini + rime

    if final == 'ᆯ':
        vow = PREVIEW_JUNGSEONG_TO_LOMARI.get(medial, '')
        rime = preview_double_final_vowel(vow)
        rime = preview_glide_if_null_initial(initial, medial, rime)
        return ini + rime

    # L-final clusters: same ㄹ double-vowel behaviour, then append cluster coda.
    l_cluster_finals = {
        'ᆶ': 'h',  # ㅀ
        'ᆰ': 'k',
        'ᇍ': 'n',
        'ᇎ': 't',
        'ᆱ': 'm',
        'ᆲ': 'p',
        'ᆴ': 't',
    }
    if final in l_cluster_finals:
        vow = PREVIEW_JUNGSEONG_TO_LOMARI.get(medial, '')
        rime = preview_double_final_vowel(vow)
        rime = preview_glide_if_null_initial(initial, medial, rime)
        return ini + rime + l_cluster_finals[final]

    vow = PREVIEW_JUNGSEONG_TO_LOMARI.get(medial, '')
    fin = PREVIEW_JONGSEONG_TO_LOMARI.get(final, '')
    rime = preview_glide_if_null_initial(initial, medial, vow + fin)
    return ini + rime


def hangul_unit_to_lomari(unit: str) -> str:
    """Romanise one Hangul/Hokkien-Hangul unit for the Lomari preview."""
    text = str(unit)
    if not text:
        return ''

    if len(text) >= 2 and text[0] == HANGUL_CHOSEONG_FILLER and text[1] in SPECIAL_MEDIALS:
        return PREVIEW_JUNGSEONG_TO_LOMARI.get(text[1], text[1])

    if len(text) == 1:
        decomposed = decompose_precomposed_syllable(text)
        if decomposed is not None:
            initial, medial, final = decomposed
            return preview_cluster_to_base_lomari(initial, medial, final)

    if len(text) >= 2 and is_initial_jamo(text[0]) and is_vowel_jamo(text[1]):
        initial = text[0]
        medial = text[1]
        final_chars = [ch for ch in text[2:] if ch in T_INDEX and ch != '']
        if len(final_chars) == 1:
            return preview_cluster_to_base_lomari(initial, medial, final_chars[0])
        if not final_chars:
            return preview_cluster_to_base_lomari(initial, medial, '')

    if len(text) == 1:
        ch = text[0]
        if ch in COMPAT_TO_L:
            return PREVIEW_CHOSEONG_TO_LOMARI.get(COMPAT_TO_L[ch], ch)
        if ch in COMPAT_TO_V:
            return PREVIEW_JUNGSEONG_TO_LOMARI.get(COMPAT_TO_V[ch], ch)
        if ch in V_TO_COMPAT.values():
            for medial, compat in V_TO_COMPAT.items():
                if compat == ch:
                    return PREVIEW_JUNGSEONG_TO_LOMARI.get(medial, ch)
        if ch == 'ㅀ':
            return 'ⁿh'
        if ch in T_TO_COMPAT:
            return T_TO_COMPAT.get(ch, ch)

    # Multi-codepoint Hokkien syllables such as 하이 are kept readable by
    # falling back to their smaller Hangul units.
    parts = split_untoned_hangul_units(text)
    if parts and parts != [text]:
        return ''.join(hangul_unit_to_lomari(part) for part in parts)
    return text


# Names the IME Pad re-exports (generated when the engine was extracted).
ENGINE_NAMES = (
    'ARABIC_NUMERAL_DIGITS',
    'AUDIO_ENGLISH_CLUSTER_SPEED_FACTOR',
    'AUDIO_EQUIVALENT_COMPAT_FINALS',
    'AUDIO_EQUIVALENT_COMPAT_VOWELS',
    'AUDIO_EQUIVALENT_FINALS',
    'AUDIO_EQUIVALENT_MEDIALS',
    'AUDIO_FILE_EXTENSIONS',
    'AUDIO_HANRI_INDEX',
    'AUDIO_HANRI_SEGMENT_INDEX',
    'AUDIO_IGNORED_PUNCTUATION',
    'AUDIO_MODE_SINGAPORE',
    'AUDIO_MODE_TAIPEI',
    'AUDIO_MULTI_SYLLABLE_SPEED_FACTOR',
    'AUDIO_NG_MEDIAL_ALIASES',
    'AUDIO_PHRASE_BOUNDARY_PUNCTUATION',
    'AUDIO_READING_INDEX',
    'AUDIO_READING_INDEX_BY_FIRST',
    'AUDIO_SHORT_OVERLAP_FINALS',
    'AUDIO_TONE4_SPEED_FACTOR',
    'CHECKED_FINALS_FOR_SANDHI',
    'CHECKED_TONE_SANDHI_MAP',
    'COMPAT_TO_L',
    'COMPAT_TO_T',
    'COMPAT_TO_V',
    'DIGIT_CONTEXT_PRONUNCIATIONS',
    'DIGIT_PRONUNCIATIONS',
    'DIGIT_PRONUNCIATION_PATTERNS',
    'EXTRA_INITIALS',
    'FALLBACK_HANRI_DICT',
    'FINAL_J_SHORTCUT_MEDIALS',
    'HANGUL_CHOSEONG_FILLER',
    'HANRI_BASE_CANDIDATE_BUCKETS',
    'HANRI_BASE_CANDIDATE_TESTS',
    'HANRI_DICT',
    'HANRI_DICT_SOURCE',
    'HANRI_EXACT_CANDIDATE_BUCKETS',
    'HANRI_EXACT_CANDIDATE_TESTS',
    'HANRI_PREFIX_INDEX',
    'HANRI_PREFIX_LOOKUP_BUCKETS',
    'HANRI_TSV_FILENAME',
    'HOKKIEN_SEQUENCE_MAP',
    'INTERNAL_TONE_MARKS',
    'INTERNAL_TONE_MARK_CHARS',
    'INTERNAL_TONE_MARK_TO_DIGIT',
    'JAMO_PRONUNCIATION_READINGS',
    'KEY_TO_JAMO',
    'LITERAL_CONTEXTUAL_ONE_READING',
    'LITERAL_DIGIT_CONTEXT_PRONUNCIATIONS',
    'LITERAL_DIGIT_DEFAULT_PRONUNCIATIONS',
    'LITERAL_DIGIT_MARK',
    'LITERAL_TWO_DIGIT_DATE_NUMBER_CONTEXTS',
    'LITERAL_TWO_DIGIT_DATE_NUMBER_TENS',
    'LOMARI_FINAL_TO_CODA',
    'LOMARI_INITIAL_TO_L',
    'LOMARI_L_TO_INITIAL',
    'LOMARI_SHORTCUT_INITIALS',
    'LOMARI_SYLLABLE_MAP',
    'LOMARI_V_TO_RIME',
    'L_INDEX',
    'L_TABLE',
    'L_TO_COMPAT',
    'MIXED_AUDIO_HANRI_INDEX',
    'NONSTANDARD_READING_MARK',
    'PREVIEW_CHOSEONG_TO_LOMARI',
    'PREVIEW_JONGSEONG_TO_LOMARI',
    'PREVIEW_JUNGSEONG_TO_LOMARI',
    'PREVIEW_NASAL_TILDE_BELOW',
    'PREVIEW_TONE_PRIORITY_LOMARI',
    'SANDHI_EQUIVALENT_FINALS',
    'SHIFT_PRESERVED_KEYS',
    'SPECIAL_MEDIALS',
    'TONE_DIGITS',
    'TONE_DIGIT_TO_SYMBOL',
    'TONE_MARKER_MODULE_PATH',
    'TONE_SANDHI_MAP',
    'TONE_SYMBOLS',
    'TONE_SYMBOL_TO_DIGIT',
    'T_INDEX',
    'T_TABLE',
    'T_TO_COMPAT',
    'V_COMBINE',
    'V_INDEX',
    'V_TABLE',
    'V_TO_COMPAT',
    '_AUDIO_FILENAME_CONVERTER',
    '_AUDIO_FILENAME_CONVERTER_LOAD_FAILED',
    '_AUDIO_FILE_INDEX_CACHE',
    '_fallback_hanri_dict',
    'apply_d_final_onset_tensing_to_audio_phrase',
    'audio_collision_safe_filename_stem',
    'audio_file_index',
    'audio_filename_candidates',
    'audio_hanri_run_end',
    'audio_lomari_filename_stem',
    'audio_lomari_filename_stem_aliases',
    'audio_lomari_key_from_unit',
    'audio_lookup_tone_for_unit',
    'audio_lookup_units',
    'audio_missing_label_for_unit',
    'audio_sandhi_unit',
    'audio_unit_end_at',
    'audio_unit_final_jamo',
    'audio_unit_has_short_overlap_final',
    'audio_unit_initial_medial_final',
    'audio_unit_is_u_syllable',
    'audio_vowel_jamo_to_precomposed_unit',
    'build_audio_hanri_index',
    'build_audio_hanri_segment_index',
    'build_audio_reading_index',
    'build_audio_reading_index_by_first',
    'build_hanri_candidate_test_buckets',
    'build_hanri_candidate_tests',
    'build_hanri_prefix_index',
    'build_hanri_prefix_lookup_buckets',
    'build_jamo_pronunciation_readings',
    'build_lomari_syllable_map',
    'build_mixed_audio_hanri_index',
    'build_ng_initial_syllable_map',
    'bundled_resource_path',
    'can_attach_tone_to_output_chars',
    'can_attach_tone_to_text',
    'canonicalize_audio_unit',
    'canonicalize_sandhi_final_jamo',
    'citation_to_sandhi_reading',
    'cluster_to_base_lomari_for_ime',
    'compose_syllable',
    'contains_apostrophe_boundary',
    'contains_hangul_reading_unit',
    'decompose_precomposed_syllable',
    'dictionary_ranking_api',
    'dictionary_schema_api',
    'display_reading_tones',
    'english_cluster_reduction_flags',
    'entry_audio_reading',
    'field_has_hanri',
    'field_is_plain_hanri_key',
    'final_hangul_unit_needs_implicit_tone',
    'final_jamo_before_tone',
    'find_audio_file',
    'format_text_tones_for_output',
    'github_repo_path_candidates',
    'hangul_unit_to_lomari',
    'hanri_reading_prefixes',
    'hanri_tsv_path_candidates',
    'has_relaxable_apostrophe',
    'hokkien_shortcut_midway_prefixes',
    'infer_default_form',
    'is_apostrophe_boundary_after_tone',
    'is_audio_hangul_only_override_field',
    'is_audio_phrase_boundary',
    'is_checked_final_before_tone',
    'is_explicit_apostrophe_tone_override',
    'is_hangul_or_hanri_char',
    'is_hangulish_for_tone',
    'is_hanri_char',
    'is_ignored_audio_punctuation',
    'is_initial_jamo',
    'is_latin_word_start',
    'is_only_compatibility_jamo_reading',
    'is_post_apostrophe_tone',
    'is_silent_audio_unit',
    'is_standalone_consonant_audio_unit',
    'is_vowel_jamo',
    'jamo_pronunciation_reading',
    'last_non_tone_char',
    'last_tone_digit_index',
    'latin_word_end',
    'literal_digit_reading',
    'literal_digit_sequence_at',
    'literal_digit_source_end_after_count',
    'literal_digit_token_at',
    'literal_number_reading_at',
    'load_audio_filename_converter',
    'load_hanri_dict',
    'load_literal_digit_pronunciations',
    'lomari_glide_if_null_initial',
    'mark_untoned_audio_units',
    'medial_typing_components',
    'mixed_audio_hanri_match',
    'normalize_keyboard_char',
    'normalize_tone_symbols_to_digits',
    'numeric_key_digit_prefix_len',
    'precomposed_syllable_typing_prefixes',
    'preview_add_combining_mark_to_lomari_target',
    'preview_cluster_to_base_lomari',
    'preview_double_final_vowel',
    'preview_glide_if_null_initial',
    'preview_lomari_mark_target_index',
    'preview_nasalize_lomari_rime',
    'preview_special_rime_oe_yeo',
    'raw_keyboard_prefix_display',
    'reading_has_tones',
    'reading_is_marked_nonstandard',
    'reload_hanri_resources',
    'remove_apostrophes_for_lookup',
    'replace_audio_unit_initial',
    'repo_data_path',
    'resolve_audio_parts_for_unit',
    'singapore_tone1_audio_replacement',
    'source_repo_root',
    'split_audio_reading_units',
    'split_hanri_hangul_bracket_inner',
    'split_untoned_hangul_units',
    'static_audio_hanri_match',
    'strip_nonstandard_reading_mark',
    'strip_reading_tones',
    'visible_text_to_audio_segments',
)
