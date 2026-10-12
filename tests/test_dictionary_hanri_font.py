"""The requested glyph has an isolated fallback without changing other Hanri."""

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HanriFallbackTests(unittest.TestCase):
    def test_shared_fallback_is_bundled_and_character_scoped(self):
        css = (ROOT / 'shared/web-ime-menu.css').read_text(encoding='utf-8')
        self.assertIn('unicode-range: U+24EAA;', css)
        self.assertIn('/assets/fonts/tangliengim-hanri-fallback-v1.woff2', css)
        for extension in ('ttf', 'woff2'):
            self.assertGreater((ROOT / f'assets/fonts/tangliengim-hanri-fallback-v1.{extension}').stat().st_size, 100)
        self.assertIn('SIL OPEN FONT LICENSE Version 1.1', (ROOT / 'assets/fonts/OFL.txt').read_text())

    def test_classic_tags_only_the_requested_character(self):
        spec = importlib.util.spec_from_file_location('hanri_font_pad_check', ROOT / 'desktop/Hokkien Tangliengim IME Pad.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        self.assertEqual(module.SC_FONT_HANRI_CHARS, {'㩼'})
        self.assertEqual(module.FALLBACK_FONT_HANRI_CHARS, {'𤺪'})

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
