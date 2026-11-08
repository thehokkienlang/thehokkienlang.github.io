"""Hokkien Hangul must be tagged nan / nan-Hang, never Korean (ko)."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
KOREAN_TAG = re.compile(r'''\blang\s*=\s*["']?ko(?:-[A-Za-z]+)?["']?[\s>/]|:lang\(\s*ko|\[lang[|^~$*]?=["']?ko|ko-KR|\.lang\s*=\s*["']ko''')
SUFFIXES = {'.html', '.js', '.css', '.cjs', '.mjs', '.py'}


def scan(paths):
    hits = []
    for path in paths:
        text = path.read_text(encoding='utf-8', errors='ignore')
        for number, line in enumerate(text.splitlines(), 1):
            if KOREAN_TAG.search(line):
                hits.append(f'{path.relative_to(ROOT)}:{number}')
    return hits


class LanguageTagTests(unittest.TestCase):
    def test_sources_do_not_tag_hokkien_as_korean(self):
        paths = [p for folder in ('apps', 'shared') for p in (ROOT / folder).rglob('*') if p.suffix in SUFFIXES and p.is_file()]
        paths.append(ROOT / 'tools' / 'build_content.py')
        self.assertEqual(scan(paths), [])

    def test_built_site_does_not_tag_hokkien_as_korean(self):
        site = ROOT / '_site'
        if not site.is_dir():
            self.skipTest('No _site build present.')
        self.assertEqual(scan(site.rglob('*.html')), [])

    def test_hangul_inputs_use_nan_hang(self):
        for page in ('apps/ime/index.html', 'apps/translate/index.html'):
            self.assertIn('lang="nan-Hang"', (ROOT / page).read_text(encoding='utf-8'), page)
        self.assertIn('<rt lang="nan-Hang">', (ROOT / 'tools/build_content.py').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
