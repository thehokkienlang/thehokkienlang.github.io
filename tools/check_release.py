"""Run the shared-engine release gate on Windows, Linux, or macOS."""

from __future__ import annotations

import argparse
import ast
import difflib
import json
import os
import subprocess
import sys
from pathlib import Path

from capture_legacy_parity import capture


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
JAVASCRIPT_FILES = (
    "apps/dictionary/gate.js",
    "apps/dictionary/app.js",
    "apps/ime/ime.js",
    "shared/web-ime-core.js",
    "shared/web-hangul-ime.js",
    "shared/web-phonetic-output.js",
    "shared/web-audio-player.js",
)
PYTHON_FILES = (
    "desktop/Hokkien Tangliengim IME Pad.py",
    "desktop/hokkien_tone_marker_gui.py",
    "desktop/tangliengim_web_shell.py",
)


def run(label: str, *command: str) -> None:
    print(f"\n== {label} ==", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="Run portable source checks without rebuilding the published site.",
    )
    args = parser.parse_args()

    check_python_syntax()
    for relative in JAVASCRIPT_FILES:
        run(f"JavaScript syntax: {relative}", "node", "--check", relative)
    if args.source_only:
        run("Build runtime dictionary data", sys.executable, "-X", "utf8", "tools/build_dictionary_json.py")
    else:
        run("Build published site", sys.executable, "-X", "utf8", "tools/build_site.py")
    run("Shared Web IME behaviour", "node", "tools/check_web_apps.cjs", "--source")
    run("Desktop shell bridge", sys.executable, "-X", "utf8", "tools/check_desktop_shell.py")
    check_legacy_parity()

    if not args.source_only:
        run("Validate published site", sys.executable, "-X", "utf8", "tools/check_site.py")
        run("Validate built Web applications", "node", "tools/check_web_apps.cjs")

    print("\nOK: Tangliengim release gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
