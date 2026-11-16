"""Run the shared-engine release gate on Windows, Linux, or macOS."""

from __future__ import annotations

import argparse
import ast
import contextlib
import difflib
import io
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

from capture_legacy_parity import capture
from node_runtime import node_environment


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
JAVASCRIPT_FILES = (
    "apps/content-site/site.js",
    "apps/search/search.js",
    "shared/web-site-language.js",
    "shared/web-site-navigation.js",
    "desktop/desktop_restart.js",
    "desktop/editor_lifetime.js",
    "desktop/dictionary_editor_ui/editor.js",
    "desktop/website_editor_ui/website-editor.js",
    "desktop/website_editor_ui/song-editor.js",
    "desktop/website_editor_ui/vendor/pinyin-pro.js",
    "desktop/website_editor_ui/lyric-timing.js",
    "desktop/website_editor_ui/lyric-companion.js",
    "desktop/youtube_companion/background.js",
    "desktop/youtube_companion/editor.js",
    "desktop/youtube_companion/youtube.js",
    "shared/web-lyric-player.js",
    "shared/web-lyric-sync.js",
    "shared/web-access-gate.js",
    "apps/dictionary/gate.js",
    "apps/translate/gate.js",
    "apps/dictionary/app.js",
    "apps/ime/ime.js",
    "shared/web-ime-core.js",
    "shared/web-hangul-ime.js",
    "shared/web-phonetic-output.js",
    "shared/web-audio-player.js",
)
PYTHON_FILES = (
    "tools/build_content.py",
    "tools/site_search.py",
    "tools/site_languages.py",
    "tools/import_wordpress_chinese.py",
    "tools/import_wordpress.py",
    "tools/node_runtime.py",
    "desktop/dictionary_editor.py",
    "desktop/website_editor.py",
    "desktop/Tangliengim Dictionary Editor.py",
    "desktop/Tangliengim Website Editor.py",
    "desktop/Tangliengim Editors.pyw",
    "tools/dictionary_editor_service.py",
    "tools/website_editor_service.py",
    "tools/lyric_timing.py",
    "tools/check_compound_glosses.py",
    "tools/compressed_audio.py",
    "tools/dictionary_editor_publish.py",
    "desktop/Hokkien Tangliengim IME Pad.py",
    "desktop/hokkien_tone_marker_gui.py",
    "desktop/tangliengim_engine.py",
    "desktop/tangliengim_web_shell.py",
)


class Section:
    """One named step of the gate: either a subprocess command or a Python function."""

    def __init__(self, label, command=None, function=None):
        self.label = label
        self.command = command
        self.function = function

    def execute(self) -> tuple[bool, str]:
        """Run the section, returning (passed, combined output). Never prints."""
        if self.command is not None:
            result = subprocess.run(
                self.command,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            return result.returncode == 0, result.stdout
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                self.function()
        except BaseException:  # report any failure with its traceback
            buffer.write(traceback.format_exc())
            return False, buffer.getvalue()
        return True, buffer.getvalue()


def check_python_syntax() -> None:
    for relative in PYTHON_FILES:
        path = ROOT / relative
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    print(f"OK: {len(PYTHON_FILES)} Python sources parsed.")


def check_legacy_parity() -> None:
    cases = json.loads((FIXTURES / "legacy-ime-parity-cases.json").read_text(encoding="utf-8"))
    expected_path = FIXTURES / "legacy-ime-parity-reference.json"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    os.environ["HOKKIEN_HANRI_DICT_PATH"] = str(ROOT / "data" / "hokkien_hanri_dict.tsv")
    actual = capture(ROOT / "desktop", cases)
    if actual != expected:
        before = json.dumps(expected, ensure_ascii=False, indent=2).splitlines()
        after = json.dumps(actual, ensure_ascii=False, indent=2).splitlines()
        difference = "\n".join(
            difflib.unified_diff(before, after, fromfile="checked-in reference", tofile="current desktop")
        )
        raise AssertionError(f"Desktop parity fixture changed:\n{difference}")
    print("OK: desktop behaviour matches the checked-in parity baseline.")


def build_sections(source_only: bool) -> list[Section]:
    """Every section of the gate, in the order it runs."""
    py = [sys.executable, "-X", "utf8"]
    sections = [Section("Python syntax", function=check_python_syntax)]
    for relative in JAVASCRIPT_FILES:
        sections.append(Section(f"JavaScript syntax: {relative}", ["node", "--check", relative]))

    def add(label, *command):
        sections.append(Section(label, list(command)))

    add("Dictionary TSV schema", *py, "tools/validate_dictionary_tsv.py")
    add("Canonical source order (read-only)", *py, "tools/sort_dictionary_tsv.py", "--check")
    add("Redirect log coverage and jamo order", *py, "tools/build_redirect_log.py", "--check")
    if source_only:
        add("Build runtime dictionary data", *py, "tools/build_dictionary_json.py")
    else:
        add("Build published site", *py, "tools/build_site.py")
    add("Dictionary counts", *py, "tools/dictionary_counts.py")
    add("Dictionary collation and audio portability", *py, "-m", "unittest", "discover",
        "-s", "tests", "-p", "test_dictionary_*.py")
    add("Dictionary behavior and identity baseline", "node", "tools/check_dictionary_baseline.cjs")
    add("Stable-ID structural references", "node", "tools/check_entry_references.cjs")
    if source_only:
        add("Shared Web IME behaviour", "node", "tools/check_web_apps.cjs", "--source")
    add("Browser-free engine (mobile keyboard source)", "node", "tests/check_engine_headless.cjs")
    add("Static priority and reading defaults", "node", "tools/check_static_ranking.cjs")
    add("Static Desktop ranking and row independence", *py, "tools/check_static_desktop.py")
    add("Adaptive Web candidate learning", "node", "tools/check_adaptive_ranking.cjs")
    add("Adaptive Local/Desktop candidate learning", *py, "tools/check_adaptive_desktop.py")
    add("Adaptive Web safeguards", "node", "tools/check_adaptive_safeguards.cjs")
    add("Adaptive Local/Desktop safeguards", *py, "tools/check_adaptive_safeguards.py")
    add("Desktop shell bridge", *py, "tools/check_desktop_shell.py")
    add("Dictionary editor automatic readings", "node", "tests/check_dictionary_editor_reading.cjs")
    add("Editor browser lifetime", *py, "-m", "unittest", "discover",
        "-s", "tests", "-p", "test_desktop_editor_lifetime.py")
    add("Simplified Hokkien normalization suggestions", "node", "tools/check_simplified_normalization.cjs")
    add("Lomari follows the Hokkien text", *py, "tools/lomari_sync.py", "--check")
    add("Compound gloss review (warning only)", *py, "tools/check_compound_glosses.py")
    add("Audio waveform parity", *py, "tools/check_audio_pcm.py")
    sections.append(Section("Desktop parity baseline", function=check_legacy_parity))
    if not source_only:
        add("Validate published site", *py, "tools/check_site.py")
        add("Compressed audio copies", *py, "tools/compressed_audio.py")
        add("Validate built Web applications", "node", "tools/check_web_apps.cjs")
    return sections


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="Run portable source checks without rebuilding the published site.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print one OK line per passing section, and the full output of a failing one.",
    )
    parser.add_argument(
        "--from",
        dest="start_from",
        metavar="SECTION",
        help="Start at this section label (an exact label, or a unique prefix) and skip the earlier ones.",
    )
    args = parser.parse_args()

    try:
        _, env = node_environment()
    except FileNotFoundError as error:
        print(str(error), file=sys.stderr)
        return 1
    os.environ.update(env)

    sections = build_sections(args.source_only)
    if args.start_from:
        wanted = args.start_from.casefold()
        labels = [section.label for section in sections]
        matches = [i for i, label in enumerate(labels) if label.casefold() == wanted]
        if not matches:
            matches = [i for i, label in enumerate(labels) if label.casefold().startswith(wanted)]
        if len(matches) != 1:
            problem = "ambiguous" if matches else "unknown"
            print(f"{problem} section label for --from: {args.start_from!r}. Valid labels:", file=sys.stderr)
            for label in labels:
                print(f"  {label}", file=sys.stderr)
            return 2
        sections = sections[matches[0]:]

    for section in sections:
        started = time.perf_counter()
        passed, output = section.execute()
        seconds = time.perf_counter() - started
        if args.quiet and passed:
            print(f"OK  {section.label}  {seconds:.1f}s", flush=True)
            continue
        print(f"\n== {section.label} ==", flush=True)
        sys.stdout.write(output)
        if not passed:
            print(f"\nFAILED: {section.label}  ({seconds:.1f}s)", flush=True)
            return 1
        if args.quiet:
            print(f"OK  {section.label}  {seconds:.1f}s", flush=True)

    print("\nOK: Tangliengim release gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
