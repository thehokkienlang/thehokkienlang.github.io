"""Lomari lines stay tied to the Hokkien text above them (audit B7)."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import lomari_sync  # noqa: E402

LINE = ('<p>\n  <span class="lyric-line">\n    <ruby>薰<rt>훈ˆ</rt></ruby> <ruby>一支<rt>짇기ˆ</rt></ruby> '
        '<ruby>咧<rt>렣ˆ-</rt></ruby><ruby>點<rt>댬ˋ</rt></ruby>\n  </span>\n'
        '  <span class="lyric-lomari">\n    hûn jit-kî lêh-tiàm\n  </span>\n</p>')


class LomariSyncTests(unittest.TestCase):
    def test_lomari_is_derived_from_the_hangul_readings(self):
        match, kind, source, derived = next(lomari_sync.lines("content/songs/x.json", LINE, {}))
        self.assertEqual((kind, source), ("lyric", "훈ˆ 짇기ˆ 렣ˆ-댬ˋ"))
        self.assertEqual(derived, "hûn jit-kî lêh-tiàm")

    def test_tone_only_ruby_and_footnote_links(self):
        line = ('<ruby>請<rt>챨ˆ-</rt></ruby><ruby>릐<rt>ˎ</rt></ruby>'
                '<a href="#_ftn1" id="_ftnref1"><strong>¹</strong></a>')
        self.assertEqual(lomari_sync.hangul_source(line), "챨ˆ-릐ˎ")

    def test_mandarin_lines_are_not_tied(self):
        self.assertFalse(lomari_sync.tied("你有我 我有你"))
        self.assertFalse(lomari_sync.tied("ㄨㄛˇ ㄞˋ ㄋㄧˇ"))
        self.assertTrue(lomari_sync.tied("훈ˆ"))

    def test_a_hangul_edit_without_its_lomari_is_drift_and_fix_follows_it(self):
        with tempfile.TemporaryDirectory() as folder:
            content = Path(folder) / "content"
            (content / "songs").mkdir(parents=True)
            page = content / "songs" / "song-1.json"
            edited = LINE.replace("훈ˆ", "훈ˉ")  # the reading changes, the Lomari does not
            page.write_text(json.dumps({"title": "t", "body": edited}, ensure_ascii=False), encoding="utf-8")
            repo = Path(folder)
            drift = lomari_sync.differences(repo)
            self.assertEqual([(d["stored"], d["derived"]) for d in drift],
                             [("hûn jit-kî lêh-tiàm", "hūn jit-kî lêh-tiàm")])
            # Lines under review are never rewritten.
            self.assertEqual(lomari_sync.fix({lomari_sync.key(drift[0])}, repo), {})
            self.assertEqual(lomari_sync.fix(set(), repo), {"content/songs/song-1.json": 1})
            self.assertEqual(lomari_sync.differences(repo), [])
            body = json.loads(page.read_text(encoding="utf-8"))["body"]
            self.assertIn('<span class="lyric-lomari">\n    hūn jit-kî lêh-tiàm\n  </span>', body)

    def test_home_song_buttons_follow_the_song_title_reading(self):
        songs = lomari_sync.song_records()
        body = json.loads((ROOT / "content/pages/home.json").read_text(encoding="utf-8"))["body"]
        titles = [item for item in lomari_sync.lines("content/pages/home.json", body, songs)]
        self.assertGreater(len(titles), 30)
        self.assertTrue(all(kind == "title" for _match, kind, _source, _derived in titles))

    def test_site_content_has_no_unreviewed_drift(self):
        review = {lomari_sync.key(item) for item in lomari_sync.load_review()}
        found = {lomari_sync.key(item) for item in lomari_sync.differences()}
        self.assertEqual(found - review, set(), "Lomari drifted from its Hangul: run tools/lomari_sync.py --fix")
        self.assertEqual(review - found, set(), "Reviewed lines are resolved: run tools/lomari_sync.py --write-review")


if __name__ == "__main__":
    unittest.main()
