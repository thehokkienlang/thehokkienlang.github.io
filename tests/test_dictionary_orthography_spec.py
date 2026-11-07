"""One tone-sandhi spec and one GUI-free pronunciation engine (audit B1/B2).

shared/tli-sandhi.json is the only place the Taipei tone-sandhi tables are
written down. The Python engines read it; the browser core mirrors it and this
test keeps the mirror equal. The web build loads the engine without Tkinter.
"""

import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "shared/tli-sandhi.json").read_text(encoding="utf-8"))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def js_object(source, name):
    body = re.search(rf"const {name} = Object\.freeze\(\{{(.*?)\}}\);", source).group(1)
    return dict(re.findall(r'(\d+): "(\d)"', body))


class SandhiSpecTests(unittest.TestCase):
    def test_spec_is_complete(self):
        self.assertEqual(set(SPEC["citationToSandhi"]["open"]), set("12345"))
        self.assertEqual(set(SPEC["citationToSandhi"]["checked"]), {"1", "3"})
        for direction in ("open", "checked"):
            forward = SPEC["citationToSandhi"][direction]
            for sandhi, citation in SPEC["sandhiToCitation"][direction].items():
                self.assertEqual(forward[citation], sandhi, f"{direction} reverse {sandhi}→{citation}")

    def test_python_engines_read_the_spec(self):
        engine = load("desktop/tangliengim_engine.py", "spec_check_engine")
        marker = load("desktop/hokkien_tone_marker_gui.py", "spec_check_marker")
        for module in (engine, marker):
            self.assertEqual(module.TONE_SANDHI_MAP, SPEC["citationToSandhi"]["open"])
            self.assertEqual(module.CHECKED_TONE_SANDHI_MAP, SPEC["citationToSandhi"]["checked"])
            self.assertEqual(module.CHECKED_FINALS_FOR_SANDHI, set(SPEC["checkedFinals"]))
            self.assertEqual(module.SANDHI_EQUIVALENT_FINALS, SPEC["sandhiEquivalentFinals"])
        self.assertEqual(marker.SANDHI_TO_CITATION_MAP, SPEC["sandhiToCitation"]["open"])
        self.assertEqual(marker.CHECKED_SANDHI_TO_CITATION_MAP, SPEC["sandhiToCitation"]["checked"])

    def test_browser_core_mirrors_the_spec(self):
        source = (ROOT / "shared/web-ime-core.js").read_text(encoding="utf-8")
        self.assertEqual(js_object(source, "OPEN_TAIPEI_SANDHI"), SPEC["citationToSandhi"]["open"])
        self.assertEqual(js_object(source, "CHECKED_TAIPEI_SANDHI"), SPEC["citationToSandhi"]["checked"])
        finals = re.search(r"const CHECKED_FINAL_JAMO = new Set\(\[(.*?)\]\);", source).group(1)
        self.assertEqual(set(re.findall(r'"(.)"', finals)), set(SPEC["checkedFinals"]))

    def test_no_other_copies_of_the_tables(self):
        literal = re.compile(r"(SANDHI[A-Z_]*|[A-Z_]*SANDHI)\s*=\s*(Object\.freeze\()?\{\s*['\"]?1['\"]?\s*:")
        allowed = {"shared/web-ime-core.js"}
        for path in [*ROOT.glob("desktop/*.py"), *ROOT.glob("shared/*.js"), *ROOT.glob("apps/*/*.js"), *ROOT.glob("tools/*.py")]:
            relative = path.relative_to(ROOT).as_posix()
            if relative in allowed:
                continue
            self.assertIsNone(literal.search(path.read_text(encoding="utf-8")), f"{relative} has its own sandhi table")


class EngineWithoutTkinterTests(unittest.TestCase):
    def test_engine_and_build_need_no_tkinter(self):
        script = (
            "import sys; sys.modules['tkinter'] = None\n"
            "sys.path.insert(0, 'tools')\n"
            "import build_dictionary_json as build\n"
            "engine = build.load_engine_module()\n"
            "assert engine.citation_to_sandhi_reading('가1') == '가5'\n"
            "assert 'tkinter.ttk' not in sys.modules\n"
        )
        subprocess.run([sys.executable, "-X", "utf8", "-c", script], cwd=ROOT, check=True)

    def test_ime_pad_reexports_the_engine(self):
        source = (ROOT / "desktop/Hokkien Tangliengim IME Pad.py").read_text(encoding="utf-8")
        self.assertIn("tangliengim_engine.py", source)
        self.assertNotIn("TONE_SANDHI_MAP = {", source)
        engine = (ROOT / "desktop/tangliengim_engine.py").read_text(encoding="utf-8")
        self.assertNotRegex(engine, r"^\s*(import tkinter|from tkinter)", "the engine must stay GUI-free")


if __name__ == "__main__":
    unittest.main()
