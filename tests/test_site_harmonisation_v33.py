"""Protect the reviewed v3.3 Hanri assignments and their authored readings."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from content_harmonisation import apply_edits, atoms_for, digest
from dictionary_editor_service import read_table
from harmonise_content_v33 import now_edits, propose, restore


def record(body):
    return {"type": "stories", "route": "/read/stories/the-egg/", "body": body}


class V33Tests(unittest.TestCase):
    def test_question_marker_keeps_its_reading(self):
        body = "<p><ruby>감<rt>ꞈ</rt></ruby>會</p>"
        after = apply_edits(body, propose(record(body)))
        self.assertIn(">噉<", after)
        self.assertIn(">감ˆ-<", after)

    def test_neutral_domain_is_unchanged(self):
        body = "<p>꽈’감</p>"
        self.assertFalse(propose(record(body)))

    def test_only_the_dal_reading_of_now_changes(self):
        body = "<p><ruby>今仔<rt>달ˉ아ˆ</rt></ruby> <ruby>今仔日<rt>긴ˉ아ˆ띧ˆ</rt></ruby></p>"
        self.assertEqual(apply_edits(body, now_edits(body)),
                         "<p><ruby>𦤾仔<rt>달ˉ아ˆ</rt></ruby> <ruby>今仔日<rt>긴ˉ아ˆ띧ˆ</rt></ruby></p>")

    def test_pages_are_reversible_and_urls_unchanged(self):
        ledger = json.loads((ROOT / "docs/history/harmonisation-3.3-audit.json").read_text(encoding="utf-8"))
        for file, entry in ledger["records"].items():
            with self.subTest(file=file):
                current = json.loads((ROOT / file).read_text(encoding="utf-8"))
                self.assertEqual(current["route"], entry["route"])
                # A page still exactly as audited can be reversed. One changed since (re-authored in
                # the Song Editor, or given newer page markup) cannot, so it is checked for what the
                # audit protects instead: every Hanri the audit wrote is still there. All pages must
                # stay free of the old spellings (below).
                if digest(current["body"]) == entry["afterSha256"]:
                    self.assertEqual(restore(current["body"], entry) != current["body"], bool(entry["edits"]))
                elif current.get("orthography", {}).get("review") != "structured-song-editor":
                    for edit in entry["edits"]:
                        self.assertIn(edit["after"], current["body"])
                self.assertFalse(propose(current))
                self.assertFalse(now_edits(current["body"]))

    def test_dictionary_uses_the_new_hanri(self):
        rows = read_table((ROOT / "data/hokkien_hanri_dict.tsv").read_bytes())[1]
        active = {row["entry_id"]: row for row in rows}
        for retired in ("U+AC10_00", "U+5230_U+4ECA_00", "U+4ECA_U+4ED4_00"):
            self.assertNotIn(retired, active)
        for identity, hanri, reading in (("U+5649_00", "噉", "감2"), ("U+2693E_00", "𦤾", "달1"),
                                         ("U+5230_U+2693E_00", "到𦤾", "ᄀᅷ2달1"), ("U+2693E_U+4ED4_00", "𦤾仔", "달5아2")):
            self.assertEqual((active[identity]["hanri"], active[identity]["reading"]), (hanri, reading))


if __name__ == "__main__":
    unittest.main()
