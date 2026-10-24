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


if __name__ == "__main__":
    unittest.main()
