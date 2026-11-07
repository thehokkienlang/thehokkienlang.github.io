"""Shared font assets keep branding, Western punctuation and TLI tones consistent."""

from pathlib import Path
import os
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SiteSymbolsTests(unittest.TestCase):
    def test_nasal_u_above_anchor_matches_plain_u(self):
        try:
            from fontTools.ttLib import TTFont
            import brotli  # noqa: F401  (WOFF2 decoding)
        except ImportError:
            if os.environ.get('CI'):
                self.fail('CI must install requirements-dev.txt: fontTools and brotli are needed for font-anchor inspection.')
            self.skipTest('FontTools and brotli are needed for font-anchor inspection (pip install -r requirements-dev.txt).')
        for weight in ('regular', 'bold'):
            with TTFont(ROOT / 'assets/fonts' / f'tli-noto-sans-{weight}-v3.woff2') as font:
                cmap = font.getBestCmap()
                checked = 0
                for lookup in font['GPOS'].table.LookupList.Lookup:
                    for table in lookup.SubTable:
                        if not hasattr(table, 'BaseCoverage') or cmap[0x1E75] not in table.BaseCoverage.glyphs:
                            continue
                        if cmap[0x304] not in table.MarkCoverage.glyphs:
                            continue
                        mark_class = table.MarkArray.MarkRecord[table.MarkCoverage.glyphs.index(cmap[0x304])].Class
                        anchors = [table.BaseArray.BaseRecord[table.BaseCoverage.glyphs.index(cmap[code])].BaseAnchor[mark_class] for code in (0x75, 0x1E75)]
                        self.assertEqual((anchors[0].XCoordinate, anchors[0].YCoordinate), (anchors[1].XCoordinate, anchors[1].YCoordinate))
                        checked += 1
                self.assertEqual(checked, 1)

    def test_self_hosted_regular_and_bold_faces_include_tone_ranges(self):
        css = (ROOT / "shared/web-punctuation.css").read_text(encoding="utf-8")
        self.assertNotIn('local("Calibri")', css)
        self.assertIn("U+02C6-02CF", css)
        self.assertIn("U+A788", css)
        for weight in ("regular", "bold"):
            for family in ("sans", "symbols"):
                version = 3 if family == "sans" else 2
                filename = f"tli-noto-{family}-{weight}-v{version}.woff2"
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
        self.assertIn('font-family: "TLI Noto Sans", sans-serif;', nasal)
        self.assertIn('font-feature-settings: "mark", "mkmk";', nasal)
        self.assertIn(".content-songs .imported-content .song-script-heading { margin-top: 8px;", css)
        self.assertNotIn(".content-songs .imported-content > .song-script-heading", css)

    def test_pronunciation_ruby_uses_one_relative_geometry(self):
        css = (ROOT / "shared/web-ruby.css").read_text(encoding="utf-8")
        self.assertIn("--tli-ruby-size: 0.55em;", css)
        self.assertIn("--tli-ruby-size: 0.37em;", css)
        self.assertIn("--tli-ruby-overlap: 0.05em;", css)
        self.assertIn("--tli-ruby-block-space: calc(var(--tli-ruby-size) * 1.1);", css)
        self.assertIn(".entry-headword-ruby > .entry-headword-reading", css)
        self.assertNotIn("px", css)
        self.assertNotIn(".tli-tone-ruby", css)
        for path in ("apps/content-site/site.css", "apps/dictionary/styles.css", "shared/web-title-reading.css"):
            styles = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn('@import url("/shared/web-ruby.css");', styles)
            self.assertNotIn("bottom: calc(100% -", styles)
        script = (ROOT / "apps/content-site/site.js").read_text(encoding="utf-8")
        self.assertIn('toneOnly ? "tli-tone-ruby" : "tli-reading-ruby"', script)
        self.assertIn('node.textContent.replace(/-/gu, "")', script)

    def test_homepage_story_subtitle_does_not_shrink_ruby_or_hanri(self):
        css = (ROOT / "apps/content-site/site.css").read_text(encoding="utf-8")
        self.assertIn('.home-literature-work h3 > span:not(.tli-ruby)', css)
        self.assertNotIn('.home-literature-work h3 span {', css)
        self.assertIn('margin: calc(var(--tli-ruby-block-space) + 0.1em) 0 4px;', css)


if __name__ == "__main__":
    unittest.main()
