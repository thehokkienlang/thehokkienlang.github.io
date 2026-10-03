"""Focused checks for the canonical TSV filing order."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

from tools.tangliengim_collation import (
    ENTRY_TYPE_ORDER, FINAL_ORDER, INITIAL_ORDER, VOWEL_ORDER, out_of_order_pairs, reading_sort_key, row_sort_key,
)
from tools.dictionary_schema import (
    DICTIONARY_COLUMNS,
    ENTRY_ID_REGISTRY_COLUMNS,
    canonical_entry_headword,
    entry_public_path,
    entry_id_matches_headword,
    make_entry_id,
    next_entry_id,
)


ROOT = Path(__file__).resolve().parents[1]
COLUMNS = list(DICTIONARY_COLUMNS)


def current_rows(rows):
    from tools.simplified_lookup import simplified_headword
    return [row + [simplified_headword(row[1])] if len(row) == 7 else row for row in rows]


def test_id(headword: str, number: int = 0) -> str:
    return make_entry_id(headword, number)


def write_registry(tsv_path: Path, rows: list[list[str]]) -> None:
    registry = tsv_path.with_name("dictionary_entry_id_registry.tsv")
    with registry.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\r\n")
        writer.writerow(ENTRY_ID_REGISTRY_COLUMNS)
        for row in rows:
            writer.writerow([row[6], canonical_entry_headword(row[1]), ""])


class CollationTests(unittest.TestCase):
    def test_initials_and_syllable_boundary(self) -> None:
        self.assertEqual(len(INITIAL_ORDER), 19)
        self.assertEqual(len(set(INITIAL_ORDER)), 19)
        self.assertEqual(INITIAL_ORDER[5:7], ("ᄅ", "ᄆ"))
        readings = [initial + "ᅡ" for initial in INITIAL_ORDER]
        self.assertEqual(sorted(reversed(readings), key=reading_sort_key), readings)
        self.assertLess(reading_sort_key("기"), reading_sort_key("나"))
        self.assertLess(reading_sort_key("가기"), reading_sort_key("가나"))
        self.assertLess(reading_sort_key("가"), reading_sort_key("가나"))
        self.assertEqual(reading_sort_key("가")[0], reading_sort_key("가")[0])

    def test_every_vowel_slot_including_special_vowels(self) -> None:
        self.assertEqual(VOWEL_ORDER, (
            "ᅡ", "ᅷ", "ᅢ", "ᅣ", "ᆤ", "ᅥ", "ᅦ", "ᅧ", "ᅨ", "ᅩ", "ᅪ",
            "ᅫ", "ᅬ", "ᅭ", "ᅮ", "ᅰ", "ᅱ", "ᅲ", "ᅳ", "ힻ", "ᅴ", "ᅵ",
        ))
        readings = [
            "가", "ᄀᅷ", "개", "갸", "ᄀᆤ", "거", "게", "겨", "계",
            "고", "과", "괘", "괴", "교", "구", "궤", "귀", "규",
            "그", "ᄀힻ", "긔", "기",
        ]
        self.assertEqual(sorted(reversed(readings), key=reading_sort_key), readings)
        self.assertLess(reading_sort_key("ᅟᅷ"), reading_sort_key("애"))
        self.assertLess(reading_sort_key("ᅟᆤ"), reading_sort_key("어"))
        self.assertLess(reading_sort_key("ᅟힻ"), reading_sort_key("의"))
        self.assertEqual(reading_sort_key("ᅟᅷ")[0], reading_sort_key("ᅷ")[0])
        self.assertEqual(reading_sort_key("ᅟᆤ")[0], reading_sort_key("ᆤ")[0])
        self.assertEqual(reading_sort_key("ᅟힻ")[0], reading_sort_key("ힻ")[0])

    def test_coda_inventory_and_order(self) -> None:
        self.assertEqual(FINAL_ORDER, ("", "ᆨ", "ᆫ", "ᆮ", "ᆯ", "ᆶ", "ᆷ", "ᆸ", "ᆼ", "ᇂ"))
        readings = ["가" + final for final in FINAL_ORDER]
        self.assertEqual(sorted(reversed(readings), key=reading_sort_key), readings)
        self.assertLess(reading_sort_key("가"), reading_sort_key("각"))
        self.assertLess(reading_sort_key("갈"), reading_sort_key("갏"))
        self.assertLess(reading_sort_key("갏"), reading_sort_key("감"))
        self.assertNotIn("ᆺ", FINAL_ORDER)
        self.assertNotIn("ᆾ", FINAL_ORDER)

    def test_tone_and_apostrophe_distinctions(self) -> None:
        readings = ["가1", "가2", "가", "가4", "가5"]
        self.assertEqual(sorted(reversed(readings), key=reading_sort_key), readings)
        self.assertEqual(reading_sort_key("가ˆ")[1], reading_sort_key("가1")[1])
        self.assertEqual(reading_sort_key("가")[0], reading_sort_key("’가")[0])

    def test_explicit_type_grouping(self) -> None:
        rows = [
            dict(zip(COLUMNS, ["가", "家", "1", "", "", "lexical", test_id("家")])),
            dict(zip(COLUMNS, ["가", "가", "1", "", "", "hangul_override", test_id("가")])),
            dict(zip(COLUMNS, ["가*", "家", "1", "가1", "", "correction_alias", test_id("家", 1)])),
            dict(zip(COLUMNS, ["1", "1", "1", "짇1", "", "number_pronunciation", test_id("1")])),
        ]
        self.assertEqual(
            [row["entry_type"] for row in sorted(reversed(rows), key=lambda row: row_sort_key(row, COLUMNS))],
            list(ENTRY_TYPE_ORDER),
        )

    def test_command_preserves_rows_and_is_idempotent(self) -> None:
        rows = [
            ["나", "那", "1", "", "", "lexical", test_id("那")],
            ["1", "1", "1", "짇1", "", "number_pronunciation", test_id("1")],
            ["가*", "加", "1", "가1", "", "correction_alias", test_id("加", 1)],
            ["가", "가", "1", "", "", "hangul_override", test_id("가")],
            ["가", "加", "1", "", "", "lexical", test_id("加")],
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dictionary.tsv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\r\n")
                writer.writerow(COLUMNS)
                writer.writerow(["# preserved comment"])
                writer.writerows(current_rows(rows))
            write_registry(path, rows)

            validator = subprocess.run(
                [sys.executable, str(ROOT / "tools/validate_dictionary_tsv.py"), str(path)],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
            self.assertIn("Maintenance notice", validator.stdout)
            command = [sys.executable, str(ROOT / "tools/sort_dictionary_tsv.py"), str(path)]
            subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True)
            once = path.read_bytes()
            subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True)
            self.assertEqual(path.read_bytes(), once)
            with path.open(encoding="utf-8", newline="") as handle:
                ordered = list(csv.reader(handle, delimiter="\t"))
            self.assertEqual(ordered[1], ["# preserved comment"])
            self.assertEqual(Counter(map(tuple, ordered[2:])), Counter(map(tuple, current_rows(rows))))
            self.assertEqual([row[5] for row in ordered[2:]], list(ENTRY_TYPE_ORDER[:1]) + ["lexical", "lexical", "correction_alias", "number_pronunciation"])

    def test_complete_dictionary_uses_syllabic_keys(self) -> None:
        with (ROOT / "data/hokkien_hanri_dict.tsv").open(encoding="utf-8", newline="") as handle:
            rows = [row for row in csv.DictReader(handle, delimiter="\t") if not row["reading"].startswith("#")]
        self.assertEqual(len(rows), 2748)
        self.assertEqual(Counter(row["entry_type"] for row in rows), {
            "hangul_override": 64, "lexical": 2665,
            "correction_alias": 9, "number_pronunciation": 10,
        })
        self.assertEqual(out_of_order_pairs(rows, COLUMNS), 0)
        entry_ids = [row["entry_id"] for row in rows]
        self.assertEqual(len(set(entry_ids)), len(entry_ids))
        self.assertTrue(all(entry_id_matches_headword(row["entry_id"], row["hanri"]) for row in rows))
        bases = {value.rsplit("_", 1)[0] for value in entry_ids}
        self.assertTrue(all(f"{base}_00" in entry_ids for base in bases))
        self.assertFalse(any(row["entry_id"] == "U+B990_U+D638_01" for row in rows))
        for row in rows:
            if row["entry_type"] != "number_pronunciation":
                self.assertTrue(all(token[0] == 0 for token in reading_sort_key(row["reading"])[0]), row["reading"])

    def test_invalid_tsv_is_not_rewritten(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.tsv"
            path.write_bytes(("\t".join(COLUMNS) + f"\r\n가\t家\tbad\t\t\tlexical\t{test_id('家')}\r\n").encode("utf-8"))
            original = path.read_bytes()
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/sort_dictionary_tsv.py"), str(path)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(path.read_bytes(), original)

    def test_genesis_31_approved_forms_and_active_registry(self) -> None:
        with (ROOT / "data/hokkien_hanri_dict.tsv").open(encoding="utf-8", newline="") as handle:
            rows = [row for row in csv.DictReader(handle, delimiter="\t") if not row["reading"].startswith("#")]
        by_id = {row["entry_id"]: row for row in rows}
        for entry_id, reading, headword, entry_type in (
            ("U+4F6E_00", "갛", "佮", "lexical"),
            ("U+5FA6_00", "갛", "徦", "lexical"),
            ("U+5E95_00", "되2", "底", "lexical"),
            ("U+5E95_01", "도2", "底", "lexical"),
            ("U+9019_00", "짇", "這", "lexical"),
            ("U+5F7C_00", "힏", "彼", "lexical"),
            ("U+5C31_00", "쥬5", "就", "lexical"),
            ("U+C81C_00", "제2", "제ˋ", "hangul_override"),
            ("U+D5E4_00", "헤2", "헤ˋ", "hangul_override"),
        ):
            row = by_id[entry_id]
            self.assertEqual((row["reading"], row["hanri"], row["entry_type"]), (reading, headword, entry_type))
        self.assertNotIn("U+AC00_00", by_id)
        self.assertEqual(by_id["U+54EA_U+88E1_00"]["english"], "where")
        with (ROOT / "data/dictionary_entry_id_registry.tsv").open(encoding="utf-8", newline="") as handle:
            registry = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual({row["entry_id"] for row in registry}, set(by_id) | {"U+B990_U+D638_01"})
        for record in registry:
            self.assertEqual(record["redirect_entry_id"], "")
            if record["entry_id"] in by_id:
                self.assertEqual(record["canonical_headword"], canonical_entry_headword(by_id[record["entry_id"]]["hanri"]))

    def test_entry_id_migration_is_idempotent(self) -> None:
        legacy_columns = COLUMNS[:6]
        legacy_rows = [
            ["가", "家", "1", "", "home", "lexical"],
            ["나", "那", "1", "", "", "lexical"],
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "legacy.tsv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\r\n")
                writer.writerow(legacy_columns)
                writer.writerows(legacy_rows)
            command = [sys.executable, str(ROOT / "tools/assign_dictionary_entry_ids.py"), str(path)]
            subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True)
            once = path.read_bytes()
            registry_once = path.with_name("dictionary_entry_id_registry.tsv").read_bytes()
            subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True)
            self.assertEqual(path.read_bytes(), once)
            self.assertEqual(path.with_name("dictionary_entry_id_registry.tsv").read_bytes(), registry_once)
            with path.open(encoding="utf-8", newline="") as handle:
                migrated = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual([{key: row[key] for key in legacy_columns} for row in migrated], [
                dict(zip(legacy_columns, row)) for row in legacy_rows
            ])
            self.assertEqual(len({row["entry_id"] for row in migrated}), 2)
            self.assertEqual([row["entry_id"] for row in migrated], [test_id("家"), test_id("那")])

    def test_validator_rejects_duplicate_entry_ids(self) -> None:
        rows = [
            ["가", "家", "1", "", "home", "lexical", test_id("家")],
            ["나", "那", "1", "", "", "lexical", test_id("家")],
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "duplicate-id.tsv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\r\n")
                writer.writerow(COLUMNS)
                writer.writerows(current_rows(rows))
            write_registry(path, rows[:1])
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/validate_dictionary_tsv.py"), str(path)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate entry_id", result.stdout)

    def test_unicode_entry_id_format_and_normalization(self) -> None:
        self.assertEqual(test_id("行"), "U+884C_00")
        self.assertEqual(test_id("食飽"), "U+98DF_U+98FD_00")
        self.assertEqual(test_id("食飽", 100), "U+98DF_U+98FD_100")
        self.assertEqual(test_id("𤆬뻐"), "U+241AC_U+BED0_00")
        self.assertEqual(test_id("가ˋ"), test_id("가"))
        self.assertEqual(test_id("가\u0301"), test_id(unicodedata.normalize("NFC", "가\u0301")))
        self.assertEqual(
            next_entry_id("行", [test_id("行"), test_id("行", 2)]),
            test_id("行", 3),
        )
        self.assertEqual(next_entry_id("家己", []), test_id("家己"))
        self.assertEqual(unquote(entry_public_path(test_id("家己"))), "/dictionary/家己/")
        self.assertEqual(unquote(entry_public_path(test_id("家己", 1))), "/dictionary/家己/01/")
        self.assertEqual(unquote(entry_public_path(test_id("家己", 100))), "/dictionary/家己/100/")

    def test_zero_based_migration_preserves_rows_and_retired_suffixes(self) -> None:
        old_ids = [make_entry_id("行", ordinal) for ordinal in (1, 2, 3)]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dictionary.tsv"
            registry_path = path.with_name("dictionary_entry_id_registry.tsv")
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\r\n")
                writer.writerow(COLUMNS)
                writer.writerows(current_rows([
                    ["걀4", "行", "1", "", "go", "lexical", old_ids[0]],
                    ["행4", "行", "2", "", "walk", "lexical", old_ids[2]],
                ]))
            with registry_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\r\n")
                writer.writerow(ENTRY_ID_REGISTRY_COLUMNS)
                for old_id in old_ids:
                    writer.writerow([old_id, "行", ""])
            command = [sys.executable, str(ROOT / "tools/migrate_dictionary_entry_ids_zero_based.py"), str(path)]
            subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True)
            with path.open(encoding="utf-8", newline="") as handle:
                migrated = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual([row["entry_id"] for row in migrated], [test_id("行"), test_id("行", 2)])
            self.assertEqual([row["english"] for row in migrated], ["go", "walk"])
            with registry_path.open(encoding="utf-8", newline="") as handle:
                registry = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual([row["entry_id"] for row in registry[:3]], [test_id("行", i) for i in (0, 1, 2)])
            self.assertEqual(len(registry), 3)
            self.assertEqual(next_entry_id("行", (row["entry_id"] for row in registry)), test_id("行", 3))
            once = (path.read_bytes(), registry_path.read_bytes())
            subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True)
            self.assertEqual((path.read_bytes(), registry_path.read_bytes()), once)

    def test_existing_unicode_ids_require_the_registry(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dictionary.tsv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\r\n")
                writer.writerow(COLUMNS)
                writer.writerow(["가", "家", "1", "", "home", "lexical", test_id("家"), "家"])
            original = path.read_bytes()
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/assign_dictionary_entry_ids.py"), str(path)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("registry is required", result.stderr)
            self.assertEqual(path.read_bytes(), original)

    def test_migration_does_not_register_unpublished_legacy_ids(self) -> None:
        legacy_id = "tlg-00000000000000000000000000000001"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dictionary.tsv"
            row = ["가", "家", "1", "", "home", "lexical", legacy_id]
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\r\n")
                writer.writerow(COLUMNS)
                writer.writerows(current_rows([row]))
            subprocess.run(
                [sys.executable, str(ROOT / "tools/assign_dictionary_entry_ids.py"), str(path)],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
            with path.with_name("dictionary_entry_id_registry.tsv").open(encoding="utf-8", newline="") as handle:
                registry = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(registry, [{
                "entry_id": test_id("家"),
                "canonical_headword": "家",
                "redirect_entry_id": "",
            }])

    def test_registry_rejects_pre_release_redirects(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dictionary.tsv"
            row = ["가", "家", "1", "", "home", "lexical", test_id("家")]
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\r\n")
                writer.writerow(COLUMNS)
                writer.writerows(current_rows([row]))
            registry_path = path.with_name("dictionary_entry_id_registry.tsv")
            with registry_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\r\n")
                writer.writerow(ENTRY_ID_REGISTRY_COLUMNS)
                writer.writerow([test_id("家"), "家", ""])
                writer.writerow(["tlg-00000000000000000000000000000001", "家", test_id("家")])
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/validate_dictionary_tsv.py"), str(path)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid entry_id", result.stdout)
            self.assertIn("redirects are not used before ID release", result.stdout)


if __name__ == "__main__":
    unittest.main()
