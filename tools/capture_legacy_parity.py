"""Capture deterministic reference behaviour from a desktop IME reference build.

This tool never edits the selected desktop directory. It imports its Python
files, runs the curated cases, and writes a checked-in reference JSON file for
the shared Web/Desktop engine tests.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = REPO_ROOT / "tests" / "fixtures" / "legacy-ime-parity-cases.json"
DEFAULT_OUTPUT = REPO_ROOT / "tests" / "fixtures" / "legacy-ime-parity-reference.json"


def load_module(name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def normalized_audio_segments(segments: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    return [
        {
            "unit": str(unit),
            "tone": str(tone),
            "trimStart": bool(trim_start),
            "trimEnd": bool(trim_end),
            "englishClusterHelper": bool(english_cluster_helper),
        }
        for unit, tone, trim_start, trim_end, english_cluster_helper in segments
    ]


class DesktopComposerRunner:
    """Drive the desktop composer without constructing its Tk interface."""

    def __init__(self, ime: Any) -> None:
        self.ime = ime
        self.composer = ime.Composer()
        self.key_history: list[tuple[str, tuple[Any, ...]]] = []

    def snapshot(self) -> tuple[Any, ...]:
        return (
            self.composer.output,
            self.composer.cursor_pos,
            self.composer.initial,
            self.composer.medial,
            self.composer.final,
            self.composer.e_to_ye_autocorrected,
        )

    def restore(self, snapshot: tuple[Any, ...]) -> None:
        (
            self.composer.output,
            self.composer.cursor_pos,
            self.composer.initial,
            self.composer.medial,
            self.composer.final,
            self.composer.e_to_ye_autocorrected,
        ) = snapshot
        self.composer.clamp_cursor()

    def process_standard(self, char: str) -> None:
        compat = self.ime.KEY_TO_JAMO.get(char)
        if compat is None:
            self.composer.insert_literal(char)
        elif compat in self.ime.COMPAT_TO_V:
            self.composer.add_vowel(self.ime.COMPAT_TO_V[compat])
        elif compat in self.ime.SPECIAL_MEDIALS:
            if not self.composer.has_buffer():
                self.composer.insert_literal(self.ime.HANGUL_CHOSEONG_FILLER + compat)
            else:
                self.composer.add_vowel(compat)
        elif compat in self.ime.COMPAT_TO_L:
            self.composer.add_initial(self.ime.COMPAT_TO_L[compat], source_compat=compat)
        else:
            self.composer.insert_literal(compat)

    def start_mapped_cluster(self, mapped: str) -> None:
        self.composer.commit()
        if len(mapped) >= 2 and self.ime.is_initial_jamo(mapped[0]) and self.ime.is_vowel_jamo(mapped[1]):
            self.composer.initial = mapped[0]
            self.composer.medial = mapped[1]
            self.composer.final = mapped[2] if len(mapped) >= 3 and mapped[2] in self.ime.T_INDEX else ""
            if len(mapped) > 3:
                self.composer.commit()
                self.composer.insert_literal(mapped[3:])
            return
        self.composer.insert_literal(mapped)

    def apply_tone_digit(self, digit: str) -> None:
        self.composer.commit()
        self.composer.clamp_cursor()
        pos = self.composer.cursor_pos
        if pos < 2 or self.composer.output[pos - 1] != digit:
            return
        if not self.ime.can_attach_tone_to_text(self.composer.output, pos - 2):
            return
        replacement = (
            self.ime.INTERNAL_TONE_MARKS[digit]
            if digit == "3"
            else self.ime.display_reading_tones(digit)
        )
        self.composer.output = self.composer.output[:pos - 1] + replacement + self.composer.output[pos:]
        self.composer.cursor_pos = pos - 1 + len(replacement)

    def process_char(self, raw_char: str) -> None:
        char = self.ime.normalize_keyboard_char(self.ime.normalize_typographic_apostrophes(raw_char))
        if char not in self.ime.KEY_TO_JAMO:
            self.process_standard(char)
            self.key_history = []
        else:
            before = self.snapshot()
            self.process_standard(char)
            self.key_history.append((char, before))
            max_length = max(len(sequence) for sequence in self.ime.HOKKIEN_SEQUENCE_MAP)
            if len(self.key_history) > max_length:
                self.key_history = self.key_history[-max_length:]
            raw_tail = "".join(key for key, _snapshot in self.key_history)
            for sequence, mapped in sorted(self.ime.HOKKIEN_SEQUENCE_MAP.items(), key=lambda item: -len(item[0])):
                if raw_tail.endswith(sequence):
                    self.restore(self.key_history[len(self.key_history) - len(sequence)][1])
                    self.start_mapped_cluster(mapped)
                    self.key_history = []
                    break

        if char in self.ime.TONE_DIGITS:
            self.apply_tone_digit(char)

    def visible_text(self) -> str:
        return self.composer.text().translate({ord(mark): "" for mark in self.ime.INTERNAL_TONE_MARK_CHARS})


def capture_composition_case(ime: Any, case: dict[str, Any]) -> dict[str, Any]:
    runner = DesktopComposerRunner(ime)
    for step in case.get("steps", []):
        for char in str(step.get("keys", "")):
            runner.process_char(char)
        for _ in range(int(step.get("backspace", 0))):
            runner.composer.backspace()
            runner.key_history = []
        for _ in range(int(step.get("left", 0))):
            runner.composer.move_left()
            runner.key_history = []
        for _ in range(int(step.get("right", 0))):
            runner.composer.move_right()
            runner.key_history = []
    return {"steps": case.get("steps", []), "expected": runner.visible_text()}


def capture_candidate_case(ime: Any, case: dict[str, Any]) -> dict[str, Any]:
    typed = ime.normalize_tone_symbols_to_digits(str(case["reading"]))
    base_reading = ime.strip_reading_tones(typed)
    entries = list(ime.HANRI_DICT.get(base_reading, []))

    if ime.reading_has_tones(typed):
        filtered = [
            entry for entry in entries
            if ime.typed_tones_are_compatible_with_entry(typed, entry.get("reading", base_reading))
        ]
        if not filtered:
            filtered = [
                entry for entry in entries
                if (
                    ime.strip_reading_tones(entry.get("reading", base_reading)) == base_reading
                    and not entry.get("auto_sandhi")
                )
            ]
    else:
        filtered = [entry for entry in entries if not entry.get("auto_sandhi")]

    return {
        "reading": str(case["reading"]),
        "expected": [
            {"hanri": str(entry.get("hanri", "")), "reading": str(entry.get("reading", base_reading))}
            for entry in filtered
            if ime.should_display_hanri_entry(entry, base_reading)
        ],
    }


def capture(reference_root: Path, cases: dict[str, Any]) -> dict[str, Any]:
    tone_path = reference_root / "hokkien_tone_marker_gui.py"
    ime_path = reference_root / "Hokkien Tangliengim IME Pad.py"
    if not tone_path.is_file() or not ime_path.is_file():
        raise FileNotFoundError(
            "Expected hokkien_tone_marker_gui.py and Hokkien Tangliengim IME Pad.py "
            f"inside {reference_root}"
        )

    sys.path.insert(0, str(reference_root))
    try:
        tone = load_module("hokkien_tone_marker_gui", tone_path)
        ime = load_module("legacy_tangliengim_ime", ime_path)
    finally:
        sys.path.pop(0)

    audio: list[dict[str, Any]] = []
    for case in cases.get("audio", []):
        input_text = str(case["input"])
        expected: dict[str, Any] = {}
        for mode in case.get("modes", ["taipei"]):
            mode_value = getattr(ime, f"AUDIO_MODE_{str(mode).upper()}")
            segments, unknown = ime.visible_text_to_audio_segments(input_text, mode_value)
            expected[str(mode)] = {
                "segments": normalized_audio_segments(segments),
                "unknown": [str(item) for item in unknown],
            }
        audio.append({"input": input_text, "expected": expected})

    return {
        "schemaVersion": 2,
        "audio": audio,
        "lomari": [
            {
                "reading": str(case["reading"]),
                "expected": tone.auto_lomari_from_hangul(str(case["reading"])),
            }
            for case in cases.get("lomari", [])
        ],
        "citationSandhi": [
            {
                "reading": str(case["reading"]),
                "expected": tone.citation_to_sandhi_reading(str(case["reading"])),
            }
            for case in cases.get("citationSandhi", [])
        ],
        "overrides": [
            {
                "text": str(case["text"]),
                "expected": tone.apply_hangul_overrides_from_tsv(str(case["text"])),
            }
            for case in cases.get("overrides", [])
        ],
        "composition": [capture_composition_case(ime, case) for case in cases.get("composition", [])],
        "candidates": [capture_candidate_case(ime, case) for case in cases.get("candidates", [])],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", "--legacy-root", dest="reference_root", type=Path, required=True)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    captured = capture(args.reference_root.resolve(), cases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(captured, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    try:
        output_label = args.output.relative_to(REPO_ROOT)
    except ValueError:
        output_label = args.output
    print(f"wrote {output_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
