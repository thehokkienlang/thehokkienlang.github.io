"""Imported stylesheets must invalidate with their typography dependencies."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_site


class SiteAssetVersionsTests(unittest.TestCase):
    def test_font_stylesheet_changes_invalidate_parent_import(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            dependency = output / "symbols.css"
            parent = output / "site.css"
            dependency.write_text(".tone { color: black; }", encoding="utf-8")
            parent.write_text('@import url("/symbols.css");', encoding="utf-8")
            with patch.object(build_site, "OUTPUT", output):
                build_site.version_css_imports(parent, set())
                first = parent.read_text(encoding="utf-8")
                self.assertIn("/symbols.css?v=", first)
                build_site.version_css_imports(parent, set())
                self.assertEqual(first, parent.read_text(encoding="utf-8"))
                dependency.write_text(".tone { color: blue; }", encoding="utf-8")
                build_site.version_css_imports(parent, set())
                self.assertNotEqual(first, parent.read_text(encoding="utf-8"))

    def test_gate_scripts_use_content_hashes_not_visit_timestamps(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "shared").mkdir()
            (output / "dictionary").mkdir()
            shared = output / "shared" / "core.js"
            shared.write_text("one", encoding="utf-8")
            (output / "dictionary" / "app.js").write_text("app", encoding="utf-8")
            gate = output / "dictionary" / "gate.js"
            source = ('const APP_SCRIPTS = ["/shared/core.js", "app.js"];\n'
                      "const ASSET_VERSIONS = {};\n")
            gate.write_text(source, encoding="utf-8")
            with patch.object(build_site, "OUTPUT", output):
                build_site.version_gate_scripts(gate)
                first = gate.read_text(encoding="utf-8")
                self.assertIn('"/shared/core.js": "', first)
                self.assertIn('"app.js": "', first)
                self.assertNotIn("const ASSET_VERSIONS = {};", first)
                shared.write_text("two", encoding="utf-8")
                gate.write_text(source, encoding="utf-8")
                build_site.version_gate_scripts(gate)
                self.assertNotEqual(first, gate.read_text(encoding="utf-8"))

    def test_built_gates_have_versions_for_every_loaded_script(self):
        for app in ("dictionary", "translate"):
            text = (ROOT / "apps" / app / "gate.js").read_text(encoding="utf-8")
            self.assertEqual(len(build_site.ASSET_VERSIONS_LINE.findall(text)), 1, app)
            self.assertIn("ASSET_VERSIONS[source] || Date.now()", text, app)


if __name__ == "__main__":
    unittest.main()
