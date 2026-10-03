"""Shared structural rules for the canonical Tangliengim dictionary TSV."""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import quote


DICTIONARY_COLUMNS = (
    "reading",
    "hanri",
    "priority",
    "corrected",
    "english",
    "entry_type",
    "entry_id",
    "simplified",
)

ENTRY_ID_REGISTRY_COLUMNS = (
    "entry_id",
    "canonical_headword",
    "redirect_entry_id",
)

# These are historical display annotations, not part of a dictionary headword.
INLINE_HEADWORD_TONE_MARKS = frozenset("ˆˋ`ˊˉꞈˎˏˍ")
ENTRY_ID_PATTERN = re.compile(
    r"(?:U\+[0-9A-F]{4,6})(?:_U\+[0-9A-F]{4,6})*_(?:0[0-9]|[1-9][0-9]+)\Z"
)
LEGACY_ENTRY_ID_PATTERN = re.compile(r"tlg-[0-9a-f]{32}\Z")


def canonical_entry_headword(value: str) -> str:
    """Return the NFC display headword used as the entry identity namespace."""
    visible = "".join(
        char for char in str(value or "")
        if char not in INLINE_HEADWORD_TONE_MARKS
    )
    return unicodedata.normalize("NFC", visible)


def entry_id_base(headword: str) -> str:
    """Encode one canonical headword as uppercase Unicode code-point labels."""
    canonical = canonical_entry_headword(headword)
    if not canonical:
        raise ValueError("entry_id headword cannot be empty")
    return "_".join(f"U+{ord(char):04X}" for char in canonical)


def make_entry_id(headword: str, suffix: int) -> str:
    if suffix < 0:
        raise ValueError("entry_id suffix cannot be negative")
    return f"{entry_id_base(headword)}_{suffix:02d}"


def next_entry_id(headword: str, historical_ids) -> str:
    """Return the next suffix after every active, retired, or aliased ID."""
    base = entry_id_base(headword)
    suffixes = [
        parsed[1]
        for value in historical_ids
        if (parsed := split_entry_id(value)) is not None and parsed[0] == base
    ]
    return make_entry_id(headword, max(suffixes, default=-1) + 1)


def split_entry_id(value: str) -> tuple[str, int] | None:
    text = str(value or "")
    if not ENTRY_ID_PATTERN.fullmatch(text):
        return None
    base, suffix = text.rsplit("_", 1)
    for label in base.split("_"):
        codepoint = int(label[2:], 16)
        if codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
            return None
    return base, int(suffix)


def entry_identity(value: str) -> tuple[str, int]:
    """Decode the one stored identity into its headword and ordinal."""
    parsed = split_entry_id(value)
    if parsed is None:
        raise ValueError(f"Invalid dictionary entry_id: {value!r}")
    base, ordinal = parsed
    headword = "".join(chr(int(label[2:], 16)) for label in base.split("_"))
    if entry_id_base(headword) != base:
        raise ValueError(f"Noncanonical dictionary entry_id: {value!r}")
    return headword, ordinal


def entry_public_path(value: str) -> str:
    """Derive a future public path from an entry ID; this does not add routing."""
    headword, ordinal = entry_identity(value)
    prefix = f"/dictionary/{quote(headword, safe='')}/"
    return prefix if ordinal == 0 else f"{prefix}{ordinal:02d}/"


def valid_entry_id(value: str) -> bool:
    return split_entry_id(value) is not None


def valid_legacy_entry_id(value: str) -> bool:
    return bool(LEGACY_ENTRY_ID_PATTERN.fullmatch(str(value or "")))


def entry_id_matches_headword(entry_id: str, headword: str) -> bool:
    parsed = split_entry_id(entry_id)
    return parsed is not None and parsed[0] == entry_id_base(headword)
