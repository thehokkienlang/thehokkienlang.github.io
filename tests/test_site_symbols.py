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
            for family in ("sans", "symbols"):
                filename = f"tli-noto-{family}-{weight}-v2.woff2"
                self.assertIn(filename, css)
                self.assertTrue((ROOT / "assets/fonts" / filename).read_bytes().startswith(b"wOF2"))
        self.assertNotIn("font-weight: 100 500", css)
        self.assertNotIn("font-weight: 600 900", css)

    def test_tone_renderer_uses_positionable_spans_not_ruby_internals(self):
        core = (ROOT / "shared/web-ime-core.js").read_text(encoding="utf-8")
        renderer = core.split("function tonedHangulNode", 1)[1].split("function renderToneMarkedReading", 1)[0]
        self.assertNotIn('createElement("ruby")', renderer)
        self.assertNotIn('createElement("rt")', renderer)
        self.assertIn('rt.className = "tone-mark"', renderer)

    def test_script_fonts_are_not_replaced_by_latin_font(self):
        css = (ROOT / "shared/web-punctuation.css").read_text(encoding="utf-8")
        self.assertNotIn("U+AC00", css)
        self.assertNotIn("U+4E00", css)
        styles = (ROOT / "shared/web-site-navigation.css").read_text(encoding="utf-8")
        self.assertIn('font-family: "TLI Noto Sans", "Noto Sans", Arial, sans-serif;', styles)
        self.assertIn("font-style: normal;", styles)

    def test_tone_wrappers_do_not_add_width_to_hangul(self):
        for relative in ("shared/web-title-reading.css", "apps/dictionary/styles.css", "apps/ime/styles.css"):
            css = (ROOT / relative).read_text(encoding="utf-8")
            rule = css.split(".hangul-tone {", 1)[1].split("}", 1)[0]
            self.assertIn("min-width: 0;", rule)
            self.assertNotIn("min-width: 1em;", rule)


if __name__ == "__main__":
    unittest.main()
