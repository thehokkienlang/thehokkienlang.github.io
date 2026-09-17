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
        "schemaVersion": 1,
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
