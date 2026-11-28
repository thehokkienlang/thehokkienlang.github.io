"""Measure phrase conversion against songs and stories, for Haru's review.

Step 6 of docs/ime-phrase-conversion-plan.md. Every ruby pairs the written Hanri (or
Hangul) with its reading. This drops the Hanri, types the readings back as a user would,
and compares the IME's first offer with what the text says. It uses the desktop engine,
whose phrase rules the shared cases keep identical to the web and Android keyboards.
Nothing in the content or the dictionary is changed.

    python -X utf8 tools/sample_phrase_conversion.py                  # print the summary
    python -X utf8 tools/sample_phrase_conversion.py --write FILE     # write the report
"""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "desktop"))

import tangliengim_engine as engine  # noqa: E402
from lomari_sync import BOPOMOFO, FOOTNOTE, HANGUL, LYRIC, RT, RUBY, TONE_ONLY, content_pages  # noqa: E402

STORY = ("The Egg", ROOT / "content/stories/the-egg.story.html")
PARAGRAPH = re.compile(r"<p\b[^>]*>(.*?)</p>", re.S)
TAG = re.compile(r"<[^>]+>")
INDEX = engine.phrase_reading_index(engine.HANRI_DICT)


def clean(text: str) -> str:
    return unicodedata.normalize("NFC", html.unescape(TAG.sub("", text))).replace("'", "’")


def reading_units(reading: str) -> list[str]:
    """The syllables of a reading with their tone digits; hyphens and spaces only group them."""
    text = engine.normalize_tone_symbols_to_digits(reading.replace("-", "").replace(" ", ""))
    units, index = [], 0
    while index < len(text):
        end, syllable = engine.phrase_unit_at(text, index)
        if not syllable:
            return []
        if text[end:end + 1] and text[end] in engine.TONE_DIGITS:
            end += 1
        units.append(text[index:end])
        index = end
    return units


def line_pieces(markup: str):
    """Yield ('syllables', [...]), ('space', None) or ('break', mark) for one line of text.

    A syllable is (typed unit, written character or None, word number, whole written word).
    The written character is None where a word's Hanri do not pair one to one with its syllables.
    """
    markup = FOOTNOTE.sub("", markup)
    position, word = 0, 0
    for match in [*RUBY.finditer(markup), None]:
        plain = clean(markup[position:match.start() if match else len(markup)])
        index = 0
        while index < len(plain):
            end, syllable = engine.phrase_unit_at(plain, index)
            if syllable:
                if end < len(plain) and plain[end] in engine.TONE_SYMBOLS:
                    end += 1
                unit = engine.normalize_tone_symbols_to_digits(plain[index:end])
                written = engine.strip_reading_tones(unit)
                word += 1
                yield "syllables", [(unit, written, word, written)]
            elif plain[index].isspace():
                yield "space", None
            else:
                yield "break", plain[index]
            index = end
        if match is None:
            return
        position = match.end()
        inner = match.group(1)
        reading = clean("".join(RT.findall(inner))).strip()
        base = clean(RT.sub("", inner)).strip()
        word += 1
        if TONE_ONLY.match(reading) if reading else True:
            # A Hangul syllable written with its tone mark above it.
            units = reading_units(base + reading)
            written = [engine.strip_reading_tones(unit) for unit in units]
        else:
            units = reading_units(reading.strip("’"))
            if reading.startswith("’") and units:
                yield "break", "’"
                base = base.lstrip("’")
            written = list(base) if len(base) == len(units) else [None] * len(units)
        if not units:
            yield "break", base
            continue
        yield "syllables", [(unit, char, word, base) for unit, char in zip(units, written)]


def runs(markup: str, join_spaces: bool):
    """Yield (after an apostrophe, directly after it, syllables) for each run a user would type.

    From an apostrophe to the next space everything is typed in Hangul, so that space is
    typed even in continuous typing. Punctuation ends a run but not that stretch.
    """
    current, attached, directly = [], False, False
    for kind, value in line_pieces(markup):
        if kind == "syllables":
            current.extend(value)
            continue
        if kind == "space" and join_spaces and not attached:
            continue
        if current:
            yield attached, directly, current
            current = []
        if kind == "space":
            attached = directly = False
        elif value == "’":
            attached = directly = True
        else:
            directly = False
    if current:
        yield attached, directly, current


def sources():
    """Yield (title, line markup) for every Hokkien lyric line and story paragraph."""
    for name, _path, data in content_pages(ROOT):
        if "/songs/" not in name:
            continue
        for match in LYRIC.finditer(data["body"]):
            line = match.group(2)
            text = clean(line)
            if "<ruby" in line and not BOPOMOFO.search(text) and HANGUL.search(text):
                yield data["title"], line
    title, path = STORY
    for match in PARAGRAPH.finditer(path.read_text(encoding="utf-8")):
        if "<ruby" in match.group(1):
            yield title, match.group(1)


def written_slice(syllables: list, start: int, end: int) -> str | None:
    """What the text writes for syllables[start:end], when that can be told."""
    part = syllables[start:end]
    if all(item[1] is not None for item in part):
        return "".join(item[1] for item in part)
    whole_left = start == 0 or syllables[start - 1][2] != part[0][2]
    whole_right = end == len(syllables) or syllables[end][2] != part[-1][2]
    if whole_left and whole_right:
        return "".join({item[2]: item[3] for item in part}.values())
    return None


def comparable(text: str) -> str:
    return unicodedata.normalize("NFC", text).replace("’", "")


def offer_after_apostrophe(typed: list[str], directly: bool) -> str:
    """What the IME's first choice writes for a run typed after an apostrophe: Hangul only."""
    text = "".join(typed)
    match = engine.menu_suffix_match(INDEX, text, "’" if directly else "’,")
    if match and match["words"]:
        text = text[:match["start"]] + engine.phrase_entry_output(match["words"][0])
    return engine.strip_reading_tones(text)


def offer(typed: list[str]):
    """The IME's phrase for a typed run, or None, and the word menu at its end."""
    suffix = engine.menu_suffix_match(INDEX, "".join(typed))
    converted = (engine.phrase_syllable_count("".join(typed)[suffix["start"]:])
                 if suffix and suffix["words"] else 0)
    return engine.phrase_for_run(typed, engine.phrase_span_lookup(INDEX, typed), converted), suffix


def measure(join_spaces: bool, toned: bool) -> dict:
    totals = Counter()
    wrong = Counter()
    samples = []
    for title, markup in sources():
        for attached, directly, syllables in runs(markup, join_spaces):
            typed = [item[0] if toned else engine.strip_reading_tones(item[0]) for item in syllables]
            original = written_slice(syllables, 0, len(syllables))
            if original is None:
                original = "".join({item[2]: item[3] for item in syllables}.values())
            if attached:
                totals["after apostrophe"] += 1
                totals["after apostrophe matches"] += (
                    comparable(offer_after_apostrophe(typed, directly)) == comparable(original))
                continue
            if len(syllables) < 2:
                totals["one syllable"] += 1
                continue
            if len(syllables) > engine.PHRASE_SYLLABLE_LIMIT:
                totals["over 16 syllables"] += 1
                continue
            result, suffix = offer(typed)
            if not result:
                if suffix and suffix["words"] and suffix["start"] == 0:
                    first = engine.phrase_entry_output(suffix["words"][0])
                    totals["whole run is one word"] += 1
                    totals["whole word matches"] += comparable(first) == comparable(original)
                else:
                    totals["no phrase"] += 1
                continue
            outputs, offset = [], 0
            for segment in result["segments"]:
                start, end, entry = segment["start_unit"], segment["end_unit"], segment["entry"]
                output = (engine.phrase_entry_output(entry) if entry
                          else engine.strip_reading_tones("".join(typed[start:end])))
                outputs.append(output)
                expected = written_slice(syllables, start, end)
                if expected is None:
                    continue
                totals["words compared"] += 1
                totals["syllables compared"] += end - start
                if comparable(expected) == comparable(output):
                    totals["words match"] += 1
                    totals["syllables match"] += end - start
                else:
                    spoken = engine.strip_reading_tones("".join(typed[start:end]))
                    wrong[(spoken, expected, output)] += 1
            phrase = "".join(outputs)
            matches = comparable(phrase) == comparable(original)
            totals["phrases offered"] += 1
            totals["phrases match"] += matches
            samples.append((title, tuple(typed), original, phrase, matches))
    return {"totals": totals, "wrong": wrong, "samples": samples}


def percent(part: int, whole: int) -> str:
    return f"{100 * part / whole:.1f}%" if whole else "n/a"


def summary_rows(results: dict) -> list[str]:
    header = ["| Measure | " + " | ".join(results) + " |", "|---|" + "---|" * len(results)]

    def row(label, value):
        return f"| {label} | " + " | ".join(value(result["totals"]) for result in results.values()) + " |"

    return header + [
        row("Runs that got a phrase", lambda t: str(t["phrases offered"])),
        row("Phrase identical to the text", lambda t: percent(t["phrases match"], t["phrases offered"])),
        row("Words in phrases that match", lambda t: percent(t["words match"], t["words compared"])),
        row("Syllables in phrases that match", lambda t: percent(t["syllables match"], t["syllables compared"])),
        row("Runs that are one word (no phrase)", lambda t: str(t["whole run is one word"])),
        row("…first choice identical to the text",
            lambda t: percent(t["whole word matches"], t["whole run is one word"])),
        row("Other runs without a phrase", lambda t: str(t["no phrase"])),
        row("Runs over 16 syllables", lambda t: str(t["over 16 syllables"])),
        row("Runs between an apostrophe and a space (Hangul only)", lambda t: str(t["after apostrophe"])),
        row("…first choice identical to the text",
            lambda t: percent(t["after apostrophe matches"], t["after apostrophe"])),
    ]


def pick(samples: list, matches: bool, count: int) -> list:
    """A fixed spread of samples, at most one per title."""
    chosen = {}
    def order(sample) -> str:
        key = "|".join((sample[0], " ".join(sample[1]), sample[2]))
        return hashlib.sha256(key.encode()).hexdigest()

    for sample in sorted(samples, key=order):
        if sample[4] == matches and 3 <= len(sample[1]) <= 8:
            chosen.setdefault(sample[0], sample)
    return list(chosen.values())[:count]


def report() -> str:
    results = {
        "Group by group, no tones": measure(join_spaces=False, toned=False),
        "Continuous, no tones": measure(join_spaces=True, toned=False),
        "Continuous, with tones": measure(join_spaces=True, toned=True),
    }
    main = results["Continuous, no tones"]
    lines = [
        "# Phrase conversion: sample for Haru's review",
        "",
        "Step 6 of [the plan](ime-phrase-conversion-plan.md). Generated by",
        "`tools/sample_phrase_conversion.py` from the songs and The Egg. The script drops the",
        "Hanri, types the readings back and compares the IME's first offer with the text.",
        "No content or dictionary data was changed.",
        "",
        "**How to read it.** *Group by group* presses Space where the text has a space.",
        "*Continuous* types straight through to the next punctuation mark or apostrophe, which",
        "asks much more of the splitting. A difference is not always an IME error: the text may",
        "choose to write a word in Hangul, or use a Hanri the dictionary ranks second.",
        "Every character from an apostrophe to the next space is offered in Hangul only,",
        "so those runs are counted apart from phrases.",
        "",
        "## Summary",
        "",
        *summary_rows(results),
        "",
        "## Most frequent differences",
        "",
        "Words inside phrases (continuous, no tones) where the first choice is not what the",
        "text writes. Changing an order means a reviewed row in `data/dictionary_priority.tsv`.",
        "",
        "| Typed | Text writes | Phrase chose | Times |",
        "|---|---|---|---|",
        *[f"| {typed} | {expected} | {chosen} | {count} |"
          for (typed, expected, chosen), count in
          sorted(main["wrong"].items(), key=lambda item: (-item[1], item[0]))[:60]],
    ]
    for matches, heading in ((False, "Sample phrases that differ"), (True, "Sample phrases that match")):
        lines += ["", f"## {heading}", "",
                  "| From | Typed | Text writes | Phrase |", "|---|---|---|---|",
                  # The syllables were typed straight through, so no space joins them.
                  *[f"| {title} | {''.join(typed)} | {original} | {phrase} |"
                    for title, typed, original, phrase, _ in pick(main["samples"], matches, 30 if not matches else 12)]]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", type=Path, help="write the report to this file")
    args = parser.parse_args()
    text = report()
    if args.write:
        args.write.write_text(text, encoding="utf-8", newline="\n")
        print(f"Wrote {args.write}")
    print(text.split("## Most frequent differences")[0].split("## Summary")[1].strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
