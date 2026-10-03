"""Script-preserving Simplified lookup aliases, using pinned OpenCC dictionaries."""

from functools import lru_cache
import re

if __package__:
    from .vendor.opencc import OpenCC
else:
    from vendor.opencc import OpenCC


HANRI_PATTERN = re.compile(
    "[\u3007\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
    "\U00020000-\U0002ee5f\U0002f800-\U0002fa1f\U00030000-\U0003347f]"
)
HANRI_RUNS = re.compile(HANRI_PATTERN.pattern + "+")


def contains_hanri(value: str) -> bool:
    return bool(HANRI_PATTERN.search(value))


def non_hanri_text(value: str) -> str:
    return HANRI_PATTERN.sub("", value)


@lru_cache(maxsize=2)
def converter(config: str = "tw2s"):
    return OpenCC(config)


def simplified_headword(value: str) -> str:
    """Convert only Hanri runs; all non-Hanri code points remain exact."""
    if not contains_hanri(value):
        return ""
    return HANRI_RUNS.sub(lambda match: converter().convert(match.group()), value)


def simplified_field_errors(headword: str, simplified: str) -> list[str]:
    if not contains_hanri(headword):
        return ["simplified must be empty for a headword without Hanri"] if simplified else []
    if not simplified:
        return ["simplified is required for a headword containing Hanri"]
    if not contains_hanri(simplified):
        return ["simplified must retain Hanri characters"]
    if non_hanri_text(headword) != non_hanri_text(simplified):
        return ["simplified must preserve all non-Hanri characters exactly"]
    # Conversion must preserve the non-Hanri boundaries, not just their sequence.
    source = [(i, c) for i, c in enumerate(headword) if not contains_hanri(c)]
    target = [(i, c) for i, c in enumerate(simplified) if not contains_hanri(c)]
    if source != target:
        return ["simplified must preserve the positions of non-Hanri spans"]
    return []


def review_case(headword: str, chosen: str) -> tuple[list[str], str] | None:
    """Ignore secondary glyphs and Traditional 著 alternatives to Simplified 着."""
    alternatives = []
    reasons = []
    standard = HANRI_RUNS.sub(lambda match: converter('t2s').convert(match.group()), headword)
    if standard.replace('著', '着') == chosen:
        return None
    if standard != chosen:
        reasons.append("Taiwan-variant conversion differs from plain t2s beyond accepted Traditional alternatives")
        if standard not in alternatives:
            alternatives.append(standard)
    if not reasons:
        return None
    return alternatives, "; ".join(reasons)
