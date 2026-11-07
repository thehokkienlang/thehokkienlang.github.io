"""Alt text, a sandhi text version, share metadata, sitemap, robots.txt and 404 (audits A7, A8)."""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
sys.path.insert(0, str(ROOT / "tools"))
import image_descriptions
import page_meta
from site_languages import LANGUAGES


def built(path):
    target = SITE / path
    if not target.is_file():
        raise unittest.SkipTest("needs a built site")
    return target.read_text(encoding="utf-8")


class ImageDescriptionTests(unittest.TestCase):
    def test_every_described_image_has_all_three_languages(self):
        for name, descriptions in image_descriptions.ALT_TEXT.items():
            self.assertEqual(set(descriptions), set(LANGUAGES), name)
            self.assertTrue(all(value.strip() for value in descriptions.values()), name)
            self.assertTrue((ROOT / "assets/content/wordpress" / name).is_file(), name)

    def test_empty_and_missing_alt_are_filled_and_authored_alt_is_kept(self):
        body = ('<img src="/assets/content/wordpress/458d8131d783-vowels-illustration.png" alt="">'
                '<img src="/assets/content/wordpress/850da4c77295-hn_hangul_jamo_au_bold.png">'
                '<img src="/assets/content/wordpress/49dd7a39f410-korean-keyboard.png" alt="Already described">')
        out = image_descriptions.describe_images(body, "en")
        self.assertIn('alt="Illustration of the vowel letters ㅏ, ㅗ and ㅓ"', out)
        self.assertIn('alt="The vowel letter ᅷ (au)"', out)
        self.assertIn('alt="Already described"', out)

    def test_text_version_follows_the_diagram_figure_once(self):
        body = ('<figure><img src="/assets/content/wordpress/ffbe2a8272c7-taipei-sandhi.png" alt=""></figure><p>after</p>')
        out = image_descriptions.describe_images(body, "en")
        self.assertEqual(out.count("diagram-text-version"), 1)
        self.assertLess(out.index("</figure>"), out.index("diagram-text-version"))
        self.assertLess(out.index("diagram-text-version"), out.index("<p>after</p>"))

    def test_text_version_matches_the_sandhi_spec(self):
        import json
        spec = json.loads((ROOT / "shared/tli-sandhi.json").read_text(encoding="utf-8"))["citationToSandhi"]["open"]
        names = {"1": "High", "2": "Falling", "3": "Low", "4": "Rising", "5": "Mid"}
        rows = {tone: after for tone, _example, after in image_descriptions._SANDHI_ROWS["en"]}
        for citation, sandhi in spec.items():
            self.assertEqual(rows[names[citation]], names[sandhi], citation)

    def test_built_pages_have_no_undescribed_content_images(self):
        if not SITE.is_dir():
            self.skipTest("needs a built site")
        for page in SITE.rglob("*.html"):
            for tag in re.findall(r"<img\b[^>]*>", page.read_text(encoding="utf-8", errors="ignore")):
                if "site-logo" in tag:
                    continue
                self.assertRegex(tag, r'\balt="[^"]+"', f"{page.relative_to(SITE)}: {tag[:90]}")
        for path in ("learn/tone-sandhi/index.html", "zh-hant/learn/tone-sandhi/index.html", "zh-hans/learn/tone-sandhi/index.html"):
            self.assertEqual(built(path).count('class="diagram-text-version"'), 1, path)


class DiscoveryTests(unittest.TestCase):
    def test_content_pages_have_description_and_share_tags(self):
        for path in ("index.html", "zh-hant/index.html", "learn/tone-sandhi/index.html", "songs/index.html", "about/index.html"):
            page = built(path)
            for tag in ('name="description"', 'property="og:title"', 'property="og:description"',
                        'property="og:url"', 'property="og:image"', 'name="twitter:card"'):
                self.assertIn(tag, page, f"{path}: {tag}")
        self.assertIn('property="og:locale" content="zh_TW"', built("zh-hant/index.html"))

    def test_app_pages_have_one_description_each(self):
        for app in ("dictionary", "ime", "translate"):
            page = built(f"{app}/index.html")
            self.assertEqual(page.count('name="description"'), 1, app)
            self.assertIn(f'property="og:url" content="{page_meta.SITE}/{app}/"', page, app)

    def test_sitemap_lists_public_pages_but_not_the_gated_tools(self):
        sitemap = built("sitemap.xml")
        for route in ("/", "/zh-hant/", "/learn/tone-sandhi/", "/songs/", "/ime/"):
            self.assertIn(f"<loc>{page_meta.SITE}{route}</loc>", sitemap, route)
        for route in ("/dictionary/", "/translate/", "/404/"):
            self.assertNotIn(f"<loc>{page_meta.SITE}{route}</loc>", sitemap, route)
        self.assertIn(f"Sitemap: {page_meta.SITE}/sitemap.xml", built("robots.txt"))

    def test_404_page_is_styled_and_not_indexed(self):
        page = built("404.html")
        self.assertIn('<meta name="robots" content="noindex">', page)
        self.assertNotIn('rel="canonical"', page)
        self.assertIn("Page not found", page)
        self.assertIn('href="/search/"', page)


if __name__ == "__main__":
    unittest.main()
