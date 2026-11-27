"""Run the shared-engine release gate on Windows, Linux, or macOS."""

from __future__ import annotations

import argparse
import ast
import difflib
import json
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
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
    "shared/web-sandhi-preference.js",
    "shared/web-sandhi-display.js",
    "shared/web-theme.js",
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
    "tools/check_lyric_timings.py",
    "tools/check_compound_glosses.py",
    "tools/check_stored_sandhi_tones.py",
    "tools/compressed_audio.py",
    "tools/dictionary_editor_publish.py",
    "desktop/Hokkien Tangliengim IME Pad.py",
    "desktop/hokkien_tone_marker_gui.py",
    "desktop/tangliengim_engine.py",
    "desktop/tangliengim_web_shell.py",
)


class Section:
    """One named step of the gate: either a subprocess command or a Python function."""

    def __init__(self, label, command=None, function=None, stage=2):
        self.label = label
        self.stage = stage
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
        try:
            return True, self.function() + chr(10)
        except BaseException:  # report any failure with its traceback
            return False, traceback.format_exc()


def check_python_syntax() -> str:
    for relative in PYTHON_FILES:
        path = ROOT / relative
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return f"OK: {len(PYTHON_FILES)} Python sources parsed."


def check_legacy_parity() -> str:
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
    return "OK: desktop behaviour matches the checked-in parity baseline."


def run_stage(batch: list[Section], jobs: int) -> list[tuple[bool, str, float]]:
    """Run one stage's sections, `jobs` at a time, returning results in the original order."""

    def timed(section: Section) -> tuple[bool, str, float]:
        started = time.perf_counter()
        passed, output = section.execute()
        return passed, output, time.perf_counter() - started

    if jobs == 1 or len(batch) == 1:
        results = []
        for section in batch:
            results.append(timed(section))
            if not results[-1][0]:
                break  # serial mode stops at the first failure, as before
        return results
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        return list(pool.map(timed, batch))


def build_sections(source_only: bool, website: bool = False) -> list[Section]:
    """Every section of the gate, in the order it runs."""
    py = [sys.executable, "-X", "utf8"]
    # Stages run in order; the sections inside one stage may run in parallel.
    #   0 early source checks, 1 build, 2 independent checks, 3-5 site tests, 6 checks of the built site.
    # The site tests rewrite files under _site, so each runs alone (as in CI, where they
    # run one after another) and before the checks that validate the built site.
    sections = [Section("Python syntax", function=check_python_syntax, stage=0)]
    for relative in JAVASCRIPT_FILES:
        sections.append(Section(f"JavaScript syntax: {relative}", ["node", "--check", relative], stage=0))

    def add(label, *command, stage=2):
        sections.append(Section(label, list(command), stage=stage))

    add("Release gate scope tests", *py, "-m", "unittest", "discover", "-s", "tests",
        "-p", "test_check_release_scope.py", stage=0)
    add("Lyric timings match song lyrics", *py, "tools/check_lyric_timings.py", stage=0)
    add("Dictionary TSV schema", *py, "tools/validate_dictionary_tsv.py", stage=0)
    add("Canonical source order (read-only)", *py, "tools/sort_dictionary_tsv.py", "--check", stage=0)
    add("Redirect log coverage and jamo order", *py, "tools/build_redirect_log.py", "--check", stage=0)
    if source_only:
        add("Build runtime dictionary data", *py, "tools/build_dictionary_json.py", stage=1)
    else:
        add("Build published site", *py, "tools/build_site.py", stage=1)
    add("Dictionary counts", *py, "tools/dictionary_counts.py")
    add("Dictionary collation and audio portability", *py, "-m", "unittest", "discover",
        "-s", "tests", "-p", "test_dictionary_*.py")
    add("Dictionary behavior and identity baseline", "node", "tools/check_dictionary_baseline.cjs")
    add("Stable-ID structural references", "node", "tools/check_entry_references.cjs")
    add("Stored readings keep Taipei sandhi digits", *py, "tools/check_stored_sandhi_tones.py")
    if source_only:
        add("Shared Web IME behaviour", "node", "tools/check_web_apps.cjs", "--source")
    add("Browser-free engine (mobile keyboard source)", "node", "tests/check_engine_headless.cjs")
    add("Sandhi preference", "node", "tests/check_sandhi_preference.cjs")
    add("Sandhi display on song pages", "node", "tests/check_sandhi_display.cjs")
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
        add("Validate published site", *py, "tools/check_site.py", stage=6)
        add("Compressed audio copies", *py, "tools/compressed_audio.py", stage=6)
        add("Validate built Web applications", "node", "tools/check_web_apps.cjs", stage=6)
    if not source_only:
        sections.append(Section("Site, migration and song-title tests", [
            *py, "-m", "unittest", "discover", "-s", "tests", "-p", "test_wordpress_migration.py"], stage=3))
        sections.append(Section("Song-title reading tests", [
            *py, "-m", "unittest", "discover", "-s", "tests", "-p", "test_song_title_readings.py"], stage=4))
        sections.append(Section("Site tests", [
            *py, "-m", "unittest", "discover", "-s", "tests", "-p", "test_site_*.py"], stage=5))
    if website:
        sections = [section for section in sections if website_section(section)]
        # This file also checks content-site CSS. The full profile already
        # discovers it as part of test_dictionary_*.py.
        add("Website font coverage", *py, "-m", "unittest", "discover", "-s", "tests",
            "-p", "test_dictionary_hanri_font.py")
    return sections


# Treat unfamiliar inputs as dictionary-sensitive. Shared engines, fonts, audio
# masters and the tools that build dictionary data serve more than one app.
def website_path(path: str) -> bool:
    return (path.startswith(("content/", "migration/", "data/lyric-timings/",
                             "apps/content-site/", "apps/search/",
                             "assets/images/", "assets/article_images/", "assets/icons/",
                             "assets/content/", "assets/audio/", "assets/js/",
                             "desktop/website_editor_ui/", "desktop/youtube_companion/"))
            or path.startswith(("shared/web-site-", "shared/web-lyric-", "shared/web-song-",
                                "assets/tangliengim-"))
            or path in {"shared/site-brand.html", "shared/web-title-reading.css",
                        "docs/lomari-review.json", "favicon.ico", "tools/build_content.py",
                        "tools/site_languages.py", "tools/site_search.py", "tools/lyric_timing.py",
                        "tools/check_lyric_timings.py",
                        "tools/song_title_readings.py", "tools/lomari_sync.py", "tools/check_site.py",
                        "tests/test_wordpress_migration.py", "tests/test_song_title_readings.py"}
            or (path.startswith("tests/test_site_") and path.endswith(".py")))


def profile_for_paths(paths) -> str:
    profile = "none"
    for path in paths:
        if (path in {"README.md", "CLAUDE.md", "AGENTS.md"} or path.startswith(".claude/")
                or (path.startswith("docs/") and path.endswith(".md"))):
            continue
        if not website_path(path):
            return "dictionary"
        profile = "website"
    return profile


WEBSITE_SECTIONS = {
    "Python syntax", "Release gate scope tests", "Build published site", "Validate published site",
    "Stored readings keep Taipei sandhi digits", "Lomari follows the Hokkien text",
    "Sandhi display on song pages", "Site, migration and song-title tests",
    "Lyric timings match song lyrics",
    "Song-title reading tests", "Site tests", "Validate built Web applications",
}


def website_section(section: Section) -> bool:
    prefix = "JavaScript syntax: "
    if section.label.startswith(prefix):
        return website_path(section.label[len(prefix):])
    return section.label in WEBSITE_SECTIONS


def changed_paths(base: str | None = None) -> list[str] | None:
    """Compare a CI base to the checkout, or inspect all unpublished local edits."""
    def git(*args: str) -> list[str] | None:
        result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
        if result.returncode:
            return None
        return [os.fsdecode(path) for path in result.stdout.split(b"\0") if path]

    # Count both sides of moves, including a dictionary file moved into content/.
    diff = ("diff", "--no-renames", "--name-only", "-z")
    if base is not None:
        return git(*diff, base, "HEAD", "--")
    outputs = [git(*diff, "--cached", "HEAD", "--"), git(*diff, "--"),
               git("ls-files", "-z", "--others", "--exclude-standard"),
               git(*diff, "origin/main...HEAD", "--")]
    if any(output is None for output in outputs):
        return None
    return sorted({path for output in outputs for path in output})


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
    parser.add_argument(
        "--serial",
        action="store_true",
        help="Run one section at a time, in order (for debugging).",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=4,
        metavar="N",
        help="Run up to N independent sections at once (default 4).",
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--changed", action="store_true", help="Select a profile for local edits.")
    selection.add_argument("--base", metavar="COMMIT", help="Select a profile for COMMIT to HEAD.")
    selection.add_argument("--website", action="store_true", help="Run the website-only profile.")
    args = parser.parse_args()

    try:
        _, env = node_environment()
    except FileNotFoundError as error:
        print(str(error), file=sys.stderr)
        return 1
    os.environ.update(env)

    profile = "website" if args.website else "dictionary"
    if args.changed or args.base is not None:
        paths = changed_paths(args.base)
        if paths is None:
            print("Git comparison unavailable. Using the full dictionary profile.")
        else:
            profile = profile_for_paths(paths)
    if profile == "none":
        print("Nothing to check for these changes.")
        return 0
    print(f"Release check profile: {profile}", flush=True)
    sections = build_sections(args.source_only, website=profile == "website")
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

    jobs = 1 if args.serial else max(1, args.jobs)
    for stage in sorted({section.stage for section in sections}):
        batch = [section for section in sections if section.stage == stage]
        results = run_stage(batch, jobs)
        failed = False
        for section, (passed, output, seconds) in zip(batch, results):
            if args.quiet and passed:
                print(f"OK  {section.label}  {seconds:.1f}s", flush=True)
                continue
            print(f"\n== {section.label} ==", flush=True)
            sys.stdout.write(output)
            if passed:
                print(f"OK  {section.label}  {seconds:.1f}s", flush=True)
            else:
                print(f"\nFAILED: {section.label}  ({seconds:.1f}s)", flush=True)
                failed = True
        if failed:
            return 1

    print("\nOK: Tangliengim release gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
