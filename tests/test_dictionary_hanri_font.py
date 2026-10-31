"""The requested glyph has an isolated fallback without changing other Hanri."""

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HanriFallbackTests(unittest.TestCase):
    def test_ime_fonts_preload_without_swap_flash(self):
        import re
        css = (ROOT/'shared/web-ime-menu.css').read_text(encoding='utf-8')
        for name in ('tli-menu-hanri-v1.woff2', 'tangliengim-content-hanri-v2.woff2'):
            face = next(face for face in re.findall(r'@font-face\s*\{[^}]+\}', css) if name in face)
            self.assertIn('font-display: block;', face)
            for page in ('apps/ime/index.html', 'apps/dictionary/index.html'):
                html = (ROOT/page).read_text(encoding='utf-8')
                self.assertIn(f'<link rel="preload" href="/assets/fonts/{name}" as="font" type="font/woff2" crossorigin>', html)

    def test_portable_tc_content_and_unified_menu_faces_are_bundled(self):
        css = (ROOT/'apps/content-site/site.css').read_text(encoding='utf-8')
        for weight in (400, 700):
            name = f'tli-content-tc-{weight}-v1.woff2'
            self.assertIn(name, css)
            self.assertGreater((ROOT/'assets/fonts'/name).stat().st_size, 1000)
        for path in ('apps/content-site/site.css', 'shared/web-ime-menu.css'):
            self.assertIn('TLI Menu Hanri', (ROOT/path).read_text(encoding='utf-8'))
        for extension in ('ttf', 'woff2'):
            self.assertGreater((ROOT/f'assets/fonts/tli-menu-hanri-v1.{extension}').stat().st_size, 1000)
        pad = (ROOT/'desktop/Hokkien Tangliengim IME Pad.py').read_text(encoding='utf-8')
        self.assertIn("'tli-menu-hanri-v1.ttf'", pad)
        self.assertIn("self.pick_font(['TLI Menu Hanri']", pad)

    def test_v321_and_rare_bmp_glyphs_use_shared_noto_subsets(self):
        for file in ('shared/web-ime-menu.css', 'apps/content-site/site.css'):
            css = (ROOT / file).read_text(encoding='utf-8')
            for point in ('U+3701', 'U+216B8', 'U+4180', 'U+4B55', 'U+6455', 'U+28468', 'U+8FCC'):
                self.assertIn(point, css)
            for script in ('tc', 'sc'):
                name = f'tli-hanri-v321-{script}.woff2'
                self.assertIn(name, css)
                self.assertGreater((ROOT / 'assets/fonts' / name).stat().st_size, 100)

    def test_shared_fallback_is_bundled_and_character_scoped(self):
        css = (ROOT / 'shared/web-ime-menu.css').read_text(encoding='utf-8')
        self.assertIn('unicode-range: U+24EAA;', css)
        self.assertIn('/assets/fonts/tangliengim-hanri-fallback-v1.woff2', css)
        self.assertIn('/assets/fonts/tangliengim-content-hanri-v2.woff2', css)
        self.assertIn('U+2C9B0', css)
        self.assertTrue((ROOT / 'assets/fonts/tangliengim-content-hanri-v2.ttf').is_file())
        for extension in ('ttf', 'woff2'):
            self.assertGreater((ROOT / f'assets/fonts/tangliengim-hanri-fallback-v1.{extension}').stat().st_size, 100)
        self.assertIn('SIL OPEN FONT LICENSE Version 1.1', (ROOT / 'assets/fonts/OFL.txt').read_text())

    def test_classic_tags_only_the_requested_character(self):
        spec = importlib.util.spec_from_file_location('hanri_font_pad_check', ROOT / 'desktop/Hokkien Tangliengim IME Pad.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        self.assertEqual(module.SC_FONT_HANRI_CHARS, {'㩼', '摕', '䆀', '䭕'})
        self.assertEqual(module.FALLBACK_FONT_HANRI_CHARS, {'𤺪', '𠢕', '𣍐', '𨘗', '𬦰'})
        self.assertEqual(module.TC_PATCH_HANRI_CHARS, {'㜁', '𡚸', '𨑨', '迌'})

        class Text:
            def __init__(self):
                self.tags = []
            def tag_configure(self, *args, **kwargs):
                pass
            def tag_remove(self, *args):
                pass
            def tag_raise(self, *args):
                pass
            def tag_add(self, name, start, end):
                self.tags.append((name, start, end))

        pad = module.HokkienIMEPad.__new__(module.HokkienIMEPad)
        pad.text = Text()
        for name in ('hanri_font', 'extension_b_hanri_font', 'sc_hanri_font', 'fallback_hanri_font', 'tone_font'):
            setattr(pad, name, ('font', 17))
        pad.apply_main_text_tone_font('甲𤺪㩼乙')
        self.assertEqual([t for t in pad.text.tags if t[0] == 'fallback_hanri_char'],
                         [('fallback_hanri_char', '1.0+1c', '1.0+2c')])
        self.assertEqual([t for t in pad.text.tags if t[0] == 'sc_hanri_char'],
                         [('sc_hanri_char', '1.0+2c', '1.0+3c')])


if __name__ == '__main__':
    unittest.main()
