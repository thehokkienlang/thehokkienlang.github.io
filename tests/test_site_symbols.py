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

    def test_song_nasal_words_and_nested_script_headings_use_shared_styles(self):
        css = (ROOT / "apps/content-site/site.css").read_text(encoding="utf-8")
        nasal = css.split(".nasal-grapheme {", 1)[1].split("}", 1)[0]
        self.assertIn('font-family: "Tangliengim Nasal Latin"', nasal)
        self.assertIn('font-feature-settings: "mark", "mkmk";', nasal)
        self.assertIn(".content-songs .imported-content .song-script-heading { margin-top: 8px;", css)
        self.assertNotIn(".content-songs .imported-content > .song-script-heading", css)

    def test_pronunciation_ruby_uses_one_relative_geometry(self):
        css = (ROOT / "shared/web-ruby.css").read_text(encoding="utf-8")
        self.assertIn("--tli-ruby-size: 0.5em;", css)
        self.assertIn("--tli-ruby-overlap: 0.15em;", css)
        self.assertIn(".entry-headword-ruby > .entry-headword-reading", css)
        self.assertNotIn("px", css)
        self.assertNotIn(".tli-tone-ruby", css)
        for path in ("apps/content-site/site.css", "apps/dictionary/styles.css", "shared/web-title-reading.css"):
            styles = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn('@import url("/shared/web-ruby.css");', styles)
            self.assertNotIn("bottom: calc(100% -", styles)
        script = (ROOT / "apps/content-site/site.js").read_text(encoding="utf-8")
        self.assertIn('toneOnly ? "tli-tone-ruby" : "tli-reading-ruby"', script)


if __name__ == "__main__":
    unittest.main()
