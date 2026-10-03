"""Canonical Tangliengim filing order for dictionary readings and TSV rows."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence


ENTRY_TYPE_ORDER = (
    "hangul_override", "lexical", "correction_alias", "number_pronunciation",
)

# Choseong values written separately so adjacent conjoining jamo stay readable.
INITIAL_ORDER = (
    "ᄀ",  # ㄱ
    "ᄁ",  # ㄲ
    "ᄂ",  # ㄴ
    "ᄃ",  # ㄷ
    "ᄄ",  # ㄸ
    "ᄅ",  # ㄹ
    "ᄆ",  # ㅁ
    "ᄇ",  # ㅂ
    "ᄈ",  # ㅃ
    "ᄉ",  # ㅅ
    "ᄋ",  # ㅇ
    "ᄌ",  # ㅈ
    "ᄍ",  # ㅉ
    "ᄎ",  # ㅊ
    "ᄏ",  # ㅋ
    "ᄐ",  # ㅌ
    "ᄑ",  # ㅍ
    "ᄒ",  # ㅎ
    "ᅙ",  # ㆆ
)

# Jungseong values in Tangliengim order; comments show compatibility forms.
VOWEL_ORDER = (
    "ᅡ",  # ㅏ
    "ᅷ",  # ᅟᅷ
    "ᅢ",  # ㅐ
    "ᅣ",  # ㅑ
    "ᆤ",  # ᅟᆤ
    "ᅥ",  # ㅓ
    "ᅦ",  # ㅔ
    "ᅧ",  # ㅕ
    "ᅨ",  # ㅖ
    "ᅩ",  # ㅗ
    "ᅪ",  # ㅘ
    "ᅫ",  # ㅙ
    "ᅬ",  # ㅚ
    "ᅭ",  # ㅛ
    "ᅮ",  # ㅜ
    "ᅰ",  # ㅞ
    "ᅱ",  # ㅟ
    "ᅲ",  # ㅠ
    "ᅳ",  # ㅡ
    "ힻ",  # ᅟힻ
    "ᅴ",  # ㅢ
    "ᅵ",  # ㅣ
)

# Jongseong order follows Tangliengim finals; open syllables sort first.
FINAL_ORDER = (
    "",     # open syllable
    "ᆨ",    # ㄱ
    "ᆫ",    # ㄴ
    "ᆮ",    # ㄷ
    "ᆯ",    # ㄹ
    "ᆶ",    # ㅀ
    "ᆷ",    # ㅁ
    "ᆸ",    # ㅂ
    "ᆼ",    # ㅇ
    "ᇂ",    # ㅎ
)

TYPE_RANK = {value: index for index, value in enumerate(ENTRY_TYPE_ORDER)}
INITIAL_RANK = {value: index for index, value in enumerate(INITIAL_ORDER)}
VOWEL_RANK = {value: index for index, value in enumerate(VOWEL_ORDER)}
FINAL_RANK = {value: index for index, value in enumerate(FINAL_ORDER)}
TONE_TO_DIGIT = str.maketrans({
    "ˆ": "1", "ꞈ": "1", "ˋ": "2", "`": "2", "ˎ": "2",
    "ˊ": "4", "ˏ": "4", "ˉ": "5", "ˍ": "5",
})


def _rank(value: str, ranks: dict[str, int]) -> tuple[int, int]:
    return (ranks[value], 0) if value in ranks else (len(ranks), ord(value) if value else 0)


def _syllable(initial: str, vowel: str, final: str) -> tuple:
    return (0, _rank(initial, INITIAL_RANK), _rank(vowel, VOWEL_RANK), _rank(final, FINAL_RANK))


def reading_sort_key(reading: str) -> tuple:
    """Compare syllables first, then their tones and exact written form."""
    normalized = reading.rstrip("*").translate(TONE_TO_DIGIT)
    syllables: list[tuple] = []
    tones: list[int] = []
    index = 0
    while index < len(normalized):
        char = normalized[index]
        if char in {"'", "’"}:
            index += 1
            continue
        if char in "12345" and syllables and syllables[-1][0] == 0:
            tones[-1] = int(char)
            index += 1
            continue

        code = ord(char)
        if 0xAC00 <= code <= 0xD7A3:
            position = code - 0xAC00
            initial = chr(0x1100 + position // 588)
            vowel = chr(0x1161 + position % 588 // 28)
            final_index = position % 28
            final = chr(0x11A7 + final_index) if final_index else ""
            syllables.append(_syllable(initial, vowel, final))
            tones.append(3)
            index += 1
            continue

        if char in INITIAL_RANK or char == "ᅟ":
            if index + 1 < len(normalized) and normalized[index + 1] in VOWEL_RANK:
                initial = "ᄋ" if char == "ᅟ" else char
                vowel = normalized[index + 1]
                index += 2
                final = ""
                if index < len(normalized) and 0x11A8 <= ord(normalized[index]) <= 0x11FF:
                    final = normalized[index]
                    index += 1
                syllables.append(_syllable(initial, vowel, final))
                tones.append(3)
                continue

        if char in VOWEL_RANK:
            syllables.append(_syllable("ᄋ", char, ""))
            tones.append(3)
        else:
            # Numeric keys and unrecognized legacy characters follow syllables.
            syllables.append((1, code))
            tones.append(0)
        index += 1

    return (tuple(syllables), tuple(tones), tuple(ord(char) for char in normalized))


def row_sort_key(row: Mapping[str, str], columns: Sequence[str]) -> tuple:
    entry_type = row["entry_type"]
    if entry_type not in TYPE_RANK:
        raise ValueError(f"Unknown entry_type: {entry_type!r}")
    exact_row = "\t".join(row[column] for column in columns if column != "simplified").encode("utf-8")
    return (
        TYPE_RANK[entry_type],
        reading_sort_key(row["reading"]),
        tuple(map(ord, row["hanri"])),
        tuple(map(ord, row["corrected"])),
        int(row["priority"]),
        hashlib.sha256(exact_row).digest(),
    )


def sorted_data_rows(rows: Sequence[Mapping[str, str]], columns: Sequence[str]) -> list[Mapping[str, str]]:
    return sorted(rows, key=lambda row: row_sort_key(row, columns))


def out_of_order_pairs(rows: Sequence[Mapping[str, str]], columns: Sequence[str]) -> int:
    keys = [row_sort_key(row, columns) for row in rows]
    return sum(left > right for left, right in zip(keys, keys[1:]))
