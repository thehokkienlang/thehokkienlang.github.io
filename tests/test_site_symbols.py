"""Shared font assets keep branding, Western punctuation and TLI tones consistent."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SiteSymbolsTests(unittest.TestCase):
    def test_self_hosted_regular_and_bold_faces_include_tone_ranges(self):
        css = (ROOT / "shared/web-punctuation.css").read_text(encoding="utf-8")
        self.assertNotIn('local("Calibri")', css)
        self.assertIn("U+02C6-02CF", css)
        self.assertIn("U+A788", css)
        for weight in ("regular", "bold"):
            filename = f"tli-noto-sans-{weight}-v1.woff2"
            self.assertIn(filename, css)
            self.assertTrue((ROOT / "assets/fonts" / filename).read_bytes().startswith(b"wOF2"))

    def test_script_fonts_are_not_replaced_by_latin_font(self):
        css = (ROOT / "shared/web-punctuation.css").read_text(encoding="utf-8")
        self.assertNotIn("U+AC00", css)
        self.assertNotIn("U+4E00", css)
        styles = (ROOT / "shared/web-site-navigation.css").read_text(encoding="utf-8")
        self.assertIn('font-family: "TLI Noto Sans", "Noto Sans", Arial, sans-serif;', styles)
        self.assertIn("font-style: normal;", styles)


if __name__ == "__main__":
    unittest.main()
