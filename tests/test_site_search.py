"""Whole-site search publication boundaries and language-specific documents."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_content import build_content
from site_languages import LANGUAGES
from site_search import visible_text, hanri_fold_map, lyric_text


class SiteSearchTests(unittest.TestCase):
    def test_traditional_simplified_search_keys_and_browser_offsets(self):
        mapping = hanri_fold_map()
        self.assertEqual(''.join(mapping.get(char, char) for char in '學習'), '学习')
        self.assertEqual(''.join(mapping.get(char, char) for char in '学习'), '学习')
        self.assertEqual(mapping['後'], '后')
        from node_runtime import node_environment
        node, env = node_environment()
        subprocess.run([node, str(ROOT/'tests/check_site_search_variants.cjs')], env=env, check=True)

    def test_search_tone_folding_matches_content_harmonisation(self):
        import re
        from content_harmonisation import UPPER
        source = (ROOT / 'shared/web-site-search-variants.js').read_text(encoding='utf-8')
        body = re.search(r"toneMarkFold = Object\.freeze\(\{(.*?)\}\)", source).group(1)
        fold = dict(re.findall(r"'(.)': '(.)'", body))
        canonical = lambda char: fold.get(char, char)
        for source_char, target in UPPER.items():
            self.assertEqual(canonical(chr(source_char)), canonical(target), chr(source_char))

    def test_visible_text_keeps_readings_but_ignores_executable_content(self):
        source = '<h2>學生<ruby>字<rt>지ˆ</rt></ruby></h2><script>secret()</script><p>讀冊</p>'
        self.assertEqual(visible_text(source), "學生字지ˆ 讀冊")

    def test_lyric_text_keeps_main_readings_and_lomari_only(self):
        source = ('<h3>Notes</h3><p><span class="lyric-line"><ruby>寒天<rt>괄틸ˆ</rt></ruby></span>'
                  '<span class="lyric-lomari">koa̰-thḭ̂</span></p><p>Commentary</p>')
        self.assertEqual(lyric_text(source), "寒天괄틸ˆ koa̰-thḭ̂")

    def test_build_writes_localized_pages_and_content_only_index(self):
        manifest = json.loads((ROOT / "migration/wordpress-map.json").read_text(encoding="utf-8"))
        source_records = [
            json.loads((ROOT / item["file"]).read_text(encoding="utf-8"))
            for item in manifest["records"]
        ]
        expected_songs = sum(
            item["type"] == "songs" and item["route"] != "/songs/translation-notes/"
            for item in source_records
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            routes = build_content(ROOT, output)
            for prefix in ("", "zh-hant", "zh-hans"):
                page = output / prefix / "search/index.html"
                self.assertTrue(page.is_file())
                source = page.read_text(encoding="utf-8")
                self.assertIn('id="siteSearchInput"', source)
                self.assertIn('id="hangulKeyboardToggle"', source)
                self.assertIn('id="siteSearchCandidates"', source)
                self.assertIn('class="hanri-candidate-menu"', source)
                self.assertIn('aria-pressed="false"', source)
                self.assertIn('/shared/web-ime-menu.css', source)
                self.assertIn('/assets/search/search.js', source)
            self.assertIn("/search/", routes)
            self.assertIn("/zh-hant/search/", routes)
            self.assertIn("/zh-hans/search/", routes)

            index = json.loads((output / "public/data/site-search-index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["schemaVersion"], 1)
            self.assertEqual(index['hanriFold']['學'], '学')
            self.assertEqual(set(index["languages"]), set(LANGUAGES))
            allowed = {"id", "title", "url", "kind", "titleSearch", "content"}
            for language, documents in index["languages"].items():
                self.assertEqual(len([item for item in documents if item["kind"] == "song"]), expected_songs)
                self.assertEqual(len([item for item in documents if item["kind"] == "tool"]), 2)
                self.assertEqual(len({item["id"] for item in documents}), len(documents))
                self.assertTrue(all(set(item) == allowed for item in documents))
                self.assertTrue(all("translation-notes" not in item["url"] for item in documents))
                self.assertTrue(all("lychee-mirror" not in item["url"] for item in documents))
                self.assertTrue(any("능ˉ" in item["titleSearch"] for item in documents))
                dictionary = next(item for item in documents if item["id"] == f"{language}:tool:dictionary")
                self.assertEqual(dictionary["url"], "/dictionary/" + (f"?lang={language}" if language != "en" else ""))
                self.assertNotIn("entries", dictionary)


if __name__ == "__main__":
    unittest.main()
