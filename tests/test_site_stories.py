"""The Egg's title, shared recording and source-derived Simplified presentation."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from story_presentations import STORY_MARKER, SimplifiedHTML, assemble_story, egg_presentation, shared_soundcloud, simplified_egg, soundcloud_source


class StoryPresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.traditional_source = json.loads((ROOT / 'content/zh-hant/stories/the-egg.json').read_text(encoding='utf-8'))
        cls.english_source = json.loads((ROOT / 'content/stories/the-egg.json').read_text(encoding='utf-8'))
        cls.traditional = assemble_story(cls.traditional_source, ROOT)
        cls.english = assemble_story(cls.english_source, ROOT)

    def test_all_presentations_reuse_the_working_recording_and_promote_title(self):
        src = soundcloud_source(self.traditional['body'])
        self.assertIn('2352652016', src)
        for record in (self.traditional, self.english, simplified_egg(self.traditional)):
            heading, body = egg_presentation(record, src)
            self.assertEqual(heading, '<ruby class="hanri-title">卵<rt>능ˉ</rt></ruby>')
            self.assertEqual(soundcloud_source(body), src)
            self.assertNotIn('<h2 class="wp-block-heading">', body)
            self.assertEqual(body.count('class="story-subtitle"'), 1)
        self.assertIn('2325470030', self.english['body'])  # Original audit evidence stays intact.

    def test_simplification_preserves_markup_readings_links_and_non_hanri(self):
        parser = SimplifiedHTML()
        parser.feed('<p title="現在" data-url="/繁體/">現在，原著，<ruby>學生<rt>학솅ˆ</rt></ruby>'
                    '’에 a̰i &amp; <a href="https://example.test/繁體">老師</a>'
                    '<code>漢字</code><!--原文--><script>const x="繁體";</script></p>')
        self.assertEqual(''.join(parser.parts),
                         '<p title="現在" data-url="/繁體/">现在，原著，<ruby>學生<rt>학솅ˆ</rt></ruby>'
                         '’에 a̰i &amp; <a href="https://example.test/繁體">老师</a>'
                         '<code>漢字</code><!--原文--><script>const x="繁體";</script></p>')

    def test_hokkien_prose_and_explicit_language_spans_stay_traditional(self):
        source = '<p style="font-family:Sans-serif;text-indent: 2em">這个學生’에 <ruby>老師<rt>러ˉ시</rt></ruby>。</p>'
        parser = SimplifiedHTML()
        parser.feed(source + '<p>老師說：<span lang="nan">這个學生</span>。</p>')
        self.assertEqual(''.join(parser.parts), source + '<p>老师说：<span lang="nan">這个學生</span>。</p>')

    def test_real_story_paragraphs_are_preserved_exactly(self):
        from content_harmonisation import SourceHTML

        def paragraphs(body):
            result = []
            def walk(node):
                if node.tag == 'p' and 'indent-2em' in node.attrs.get('class', '').split():
                    result.append(body[node.start:node.end])
                for child in node.children:
                    walk(child)
            walk(SourceHTML(body).root)
            return result

        original = paragraphs(self.traditional['body'])
        self.assertGreater(len(original), 50)
        self.assertEqual(original, paragraphs(simplified_egg(self.traditional)['body']))

    def test_simplified_is_derived_without_mutating_the_source(self):
        before = json.dumps(self.traditional, ensure_ascii=False)
        derived = simplified_egg(self.traditional)
        self.assertEqual(json.dumps(self.traditional, ensure_ascii=False), before)
        self.assertEqual(derived['route'], '/zh-hans/read/stories/the-egg/')
        self.assertEqual(derived['sourceSha256'], self.traditional['sourceSha256'])
        self.assertEqual(soundcloud_source(derived['body']), soundcloud_source(self.traditional['body']))

    def test_missing_or_ambiguous_players_are_not_silently_replaced(self):
        with self.assertRaises(ValueError):
            soundcloud_source('<p>No player</p>')
        with self.assertRaises(ValueError):
            shared_soundcloud('<iframe src="https://w.soundcloud.com/player/"></iframe>' * 2, 'https://w.soundcloud.com/player/')

    def test_the_story_is_stored_once_and_shared_by_both_languages(self):
        for source in (self.traditional_source, self.english_source):
            self.assertEqual(source['body'].count(STORY_MARKER), 1)
            self.assertNotIn('indent-2em', source['body'])

        def story(record):
            body = record['body']
            return body[body.index('<hr'):body.rindex('<hr')]
        self.assertEqual(story(self.traditional), story(self.english))
        for record in (self.traditional, self.english):
            self.assertNotIn(STORY_MARKER, record['body'])
            self.assertEqual(len(re.findall(r'<p class="indent-2em">', record['body'])), 68)
            self.assertEqual(record['body'].count('is-style-dots'), 3)

    def test_records_without_the_marker_are_unchanged(self):
        record = {'route': '/x/', 'body': '<p>Plain</p>'}
        self.assertIs(assemble_story(record, ROOT), record)
        with self.assertRaises(ValueError):
            assemble_story({'route': '/x/', 'body': STORY_MARKER * 2}, ROOT)


if __name__ == '__main__':
    unittest.main()
