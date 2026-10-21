"""Title annotation must retain source tones without changing song content."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from song_title_readings import song_title


class SongTitleTests(unittest.TestCase):
    def record(self, title, header):
        return {"id": "song-example", "title": title,
                "body": f'\n<h2><span>{header}</span></h2>\n<iframe src="song"></iframe><p>Lyrics remain here.</p>'}

    def test_mixed_title_keeps_authored_hangul_and_source_hanri_tones(self):
        record = self.record("生份’에 릐ˋ", '<ruby>첼<rt>ˍ</rt></ruby><ruby>훈<rt>ˍ</rt></ruby>’에 릐ˎ')
        title, body = song_title(record)
        self.assertIn('生<rt>첼ˉ</rt>', title)
        self.assertIn('份<rt>훈ˉ</rt>', title)
        self.assertTrue(title.endswith("’에 릐ˋ"))
        self.assertEqual(body, '\n\n<iframe src="song"></iframe><p>Lyrics remain here.</p>')
        self.assertIn("<h2>", record["body"])

    def test_embedded_hanri_ruby_contributes_its_reading_only(self):
        title, _ = song_title(self.record("愛拚才會贏", '애ˎ뱔 <ruby>才<rt>쟣ˆ-</rt></ruby>에얄ˏ'))
        self.assertIn('才<rt>쟣ˆ</rt>', title)
        self.assertIn('贏<rt>얄ˊ</rt>', title)
        self.assertEqual(title.count("才"), 1)

    def test_decomposed_syllable_and_alternative_readings_survive(self):
        title, _ = song_title(self.record("家後", '게ˍᄋᅷˍ'))
        self.assertIn('後<rt>ᄋᅷˉ</rt>', title)
        title, _ = song_title(self.record("月下 煮茶", '뀋에ˏ 즈ˏ데ꞈ (뀋에ˍ 주ꞈ데ˏ)'))
        self.assertIn('下<rt>에ˊ / 에ˉ</rt>', title)
        self.assertIn('煮<rt>즈ˊ / 주ˆ</rt>', title)
        record = self.record("月下 煮茶", '뀋에ˏ 즈ˏ데ꞈ (뀋에ˍ 주ꞈ데ˏ)')
        record["titleReadingVariant"] = 0
        title, _ = song_title(record)
        self.assertIn('煮<rt>즈ˊ</rt>', title)
        self.assertNotIn('주ˆ', title)
        self.assertNotIn(' / ', title)

    def test_roman_source_prefix_and_hangul_only_title_are_not_duplicated(self):
        title, _ = song_title(self.record("헤ˉ비ˆ!!! 運將 情歌", 'Happy!!! 운ˎ쟝 졩과ꞈ'))
        self.assertTrue(title.startswith("헤ˉ비ˆ!!! "))
        self.assertIn('運<rt>운ˋ</rt>', title)
        title, body = song_title(self.record("메ˉ삐ˆ", '메ˍ삐ꞈ'))
        self.assertEqual(title, "메ˉ삐ˆ")
        self.assertNotIn("<h2>", body)

    def test_mandarin_override_retains_sections_and_wrong_alignment_fails(self):
        record = self.record("敢", "漢諺混寫 Hanri-Hangul mixed script")
        record["titleRuby"] = [{"base": "敢", "reading": "ㄍㄢˇ", "system": "bopomofo"}]
        title, body = song_title(record)
        self.assertIn('敢<rt>ㄍㄢˇ</rt>', title)
        self.assertEqual(body, record["body"])
        with self.assertRaises(ValueError):
            song_title(self.record("生份", "첼"))

    def test_english_words_keep_their_spelling_with_hangul_ruby(self):
        record = self.record("Maybe Maybe", "메ˍ삐ꞈ 메ˍ삐ꞈ")
        record["titleWordReadings"] = {"Maybe": "메ˉ삐ˆ"}
        title, body = song_title(record)
        self.assertEqual(title.count('Maybe<rt>메ˉ삐ˆ</rt>'), 2)
        self.assertNotIn("<h2>", body)
        record = self.record("Happy!!! 運將 情歌", "Happy!!! 운ˎ쟝 졩과ꞈ")
        record["titleWordReadings"] = {"Happy": "헤ˉ비ˆ"}
        title, _ = song_title(record)
        self.assertIn('Happy<rt>헤ˉ비ˆ</rt>', title)
        self.assertIn('運<rt>운ˋ</rt>', title)
        self.assertIn('歌<rt>과ˆ</rt>', title)


if __name__ == "__main__":
    unittest.main()
