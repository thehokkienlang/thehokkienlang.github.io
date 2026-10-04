"""Build web-ready dictionary JSON from data/hokkien_hanri_dict.tsv."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from dictionary_schema import (
    DICTIONARY_COLUMNS,
    canonical_entry_headword,
    entry_id_matches_headword,
    valid_entry_id,
    resolve_dictionary_record,
    is_comment_record,
)
from validate_dictionary_tsv import validate_registry
from simplified_lookup import simplified_field_errors
from dictionary_ranking import annotate_entries, canonical_key, read_records


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TSV_PATH = REPO_ROOT / "data" / "hokkien_hanri_dict.tsv"
DEFAULT_REGISTRY_PATH = REPO_ROOT / "data" / "dictionary_entry_id_registry.tsv"
DEFAULT_CATEGORY_PATH = REPO_ROOT / "data" / "dictionary_categories.tsv"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "public" / "data" / "hokkien-hanri-dict.json"
DEFAULT_AUDIO_ROOT = REPO_ROOT / "public" / "audio"
TONE_MARKER_PATH = REPO_ROOT / "desktop" / "hokkien_tone_marker_gui.py"
IME_PATH = REPO_ROOT / "desktop" / "Hokkien Tangliengim IME Pad.py"

SCHEMA_VERSION = 10

ENTRY_TYPES = frozenset({
    "lexical", "correction_alias", "hangul_override", "number_pronunciation",
})


def load_tone_marker_module():
    spec = importlib.util.spec_from_file_location("tangliengim_tone_marker", TONE_MARKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load tone marker module from {TONE_MARKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_ime_module():
    spec = importlib.util.spec_from_file_location("tangliengim_ime", IME_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load IME module from {IME_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_audio_filename_case(audio_root: Path) -> None:
    mismatches = sorted(
        path.relative_to(audio_root).as_posix()
        for path in audio_root.rglob("*")
        if path.is_file() and path.suffix.lower() == ".wav" and path.name != path.name.lower()
    )
    if mismatches:
        raise ValueError("WAV filenames must be lowercase for portable audio lookup: " + ", ".join(mismatches))


def normalize_for_search(value: str) -> str:
    """Lowercase and remove combining marks/punctuation for broad lookup keys."""
    decomposed = unicodedata.normalize("NFKD", str(value or ""))
    plain = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return re.sub(r"[^0-9A-Za-z\u1100-\u11FF\u3130-\u318F\u3400-\u4DBF\u4E00-\u9FFF\U00020000-\U0002EBEF]+", "", plain).lower()


def normalized_reading(tone_marker, value: str) -> str:
    return tone_marker.normalize_tone_symbols_to_digits(
        tone_marker.strip_nonstandard_reading_mark(str(value or "").strip())
    )


def strip_inline_hanri_tone_marks(tone_marker, value: str) -> str:
    """Keep legacy inline tone glyphs out of candidate/headword text."""
    tone_symbols = getattr(tone_marker, "TONE_SYMBOLS", set())
    return "".join(char for char in str(value or "") if char not in tone_symbols)


def row_kind(tone_marker, hanri: str) -> str:
    if tone_marker.field_is_plain_cjk_key(hanri):
        return "plain_hanri"
    if tone_marker.field_is_mixed_hanri_key(hanri):
        return "mixed_hanri"
    if tone_marker.hangul_override_key(hanri):
        return "hangul_override"
    if str(hanri or "").strip().isdigit():
        return "numeric_override"
    return "other"


def expected_entry_type(reading: str, corrected: str, kind: str) -> str | None:
    """Recognize existing TSV roles without changing their runtime interpretation."""
    if reading and reading[0].isdigit() and corrected:
        return "number_pronunciation"
    if reading.endswith("*") and corrected:
        return "correction_alias"
    if kind == "hangul_override":
        return "hangul_override"
    if kind in {"plain_hanri", "mixed_hanri"}:
        return "lexical"
    return None


def reading_to_lomari(tone_marker, reading: str) -> str:
    if not reading:
        return ""
    try:
        return tone_marker.auto_lomari_from_hangul(reading)
    except Exception:
        return ""


def web_path(path: Path) -> str:
    return "/" + path.relative_to(REPO_ROOT).as_posix()


def audio_for_reading(ime, audio_root: Path, reading: str, audio_mode: str | None = None) -> dict[str, Any]:
    segments: list[dict[str, Any]] = []
    files: list[str] = []
    missing: list[str] = []
    seen_files: set[str] = set()
    seen_missing: set[str] = set()

    if not reading:
        return {"segments": segments, "files": files, "missing": missing}

    try:
        mode = audio_mode or getattr(ime, "AUDIO_MODE_TAIPEI", "taipei")
        audio_units, unknown_hanri = ime.visible_text_to_audio_segments(reading, mode)
    except Exception:
        return {"segments": segments, "files": files, "missing": [reading]}

    raw_segments: list[dict[str, Any]] = []
    for unit, tone, trim_start, trim_end, english_cluster_reduction in audio_units:
        try:
            if ime.is_silent_audio_unit(unit, tone):
                continue
            paths, labels = ime.resolve_audio_files_for_unit(audio_root, unit, tone)
        except Exception:
            paths, labels = [], [f"{unit}{tone}"]

        fallback_parts = ime.split_untoned_hangul_units(unit) if len(paths) > 1 else []
        for idx, path in enumerate(paths):
            try:
                url = web_path(path)
            except ValueError:
                url = str(path).replace("\\", "/")
            if url not in seen_files:
                files.append(url)
                seen_files.add(url)

            segment_unit = fallback_parts[idx] if idx < len(fallback_parts) else unit
            segment_tone = str(tone if (not fallback_parts or idx == len(paths) - 1) else "3")
            raw_segments.append({
                "file": url,
                "unit": segment_unit,
                "tone": segment_tone,
                "trimStart": bool(trim_start or idx > 0),
                "trimEnd": bool(trim_end or idx < len(paths) - 1),
                "shortOverlapFinal": bool(ime.audio_unit_has_short_overlap_final(segment_unit)),
                "englishClusterHelper": bool(english_cluster_reduction),
            })

        for label in labels:
            if label and label not in seen_missing:
                missing.append(label)
                seen_missing.add(label)

    for item in unknown_hanri:
        label = str(item)
        if label and label not in seen_missing:
            missing.append(label)
            seen_missing.add(label)

    speed_all_segments = len(raw_segments) > 1
    for idx, segment in enumerate(raw_segments):
        speed = 1.0
        if speed_all_segments:
            if segment["englishClusterHelper"]:
                speed = float(ime.AUDIO_ENGLISH_CLUSTER_SPEED_FACTOR)
            elif str(segment["tone"]) == "4":
                speed = float(ime.AUDIO_TONE4_SPEED_FACTOR)
            else:
                speed = float(ime.AUDIO_MULTI_SYLLABLE_SPEED_FACTOR)
        segment["speed"] = speed
        segments.append(segment)

    return {"segments": segments, "files": files, "missing": missing}


def audio_for_unit_tone(ime, audio_root: Path, unit: str, tone: str) -> dict[str, Any]:
    """Resolve one raw audio key without visible-text or TSV interpretation."""
    unit = str(unit or "")
    tone = str(tone or "3")
    if not unit or ime.is_silent_audio_unit(unit, tone):
        return {"segments": [], "files": [], "missing": []}

    try:
        paths, missing = ime.resolve_audio_files_for_unit(audio_root, unit, tone)
    except Exception:
        paths, missing = [], [f"{unit}{tone}"]

    fallback_parts = ime.split_untoned_hangul_units(unit) if len(paths) > 1 else []
    segments: list[dict[str, Any]] = []
    files: list[str] = []
    for index, path in enumerate(paths):
        try:
            url = web_path(path)
        except ValueError:
            url = str(path).replace("\\", "/")
        if url not in files:
            files.append(url)

        segment_unit = fallback_parts[index] if index < len(fallback_parts) else unit
        segment_tone = tone if (not fallback_parts or index == len(paths) - 1) else "3"
        segments.append({
            "file": url,
            "unit": segment_unit,
            "tone": segment_tone,
            "trimStart": index > 0,
            "trimEnd": index < len(paths) - 1,
            "shortOverlapFinal": bool(ime.audio_unit_has_short_overlap_final(segment_unit)),
            "englishClusterHelper": False,
            "speed": (
                float(ime.AUDIO_TONE4_SPEED_FACTOR)
                if len(paths) > 1 and segment_tone == "4"
                else float(ime.AUDIO_MULTI_SYLLABLE_SPEED_FACTOR)
                if len(paths) > 1
                else 1.0
            ),
        })

    return {"segments": segments, "files": files, "missing": list(dict.fromkeys(missing))}


def with_singapore_audio_when_needed(ime, audio_root: Path, reading: str) -> dict[str, Any]:
    audio = audio_for_reading(ime, audio_root, reading, getattr(ime, "AUDIO_MODE_TAIPEI", "taipei"))
    singapore_audio = audio_for_reading(
        ime,
        audio_root,
        reading,
        getattr(ime, "AUDIO_MODE_SINGAPORE", "singapore"),
    )
    if singapore_audio != audio:
        audio["singapore"] = singapore_audio
    return audio


def recorded_keyboard_units(ime, audio_root: Path) -> set[str]:
    """Return keyboard-producible Hangul units backed by a real audio file."""
    available_names = set(ime.audio_file_index(audio_root))
    keyboard_units: set[str] = set()
    for mapped_text in ime.LOMARI_SYLLABLE_MAP.values():
        try:
            keyboard_units.update(
                unit
                for unit, _tone in ime.split_audio_reading_units(mapped_text)
                if unit
            )
        except Exception:
            continue

    recorded_units: set[str] = set()
    for unit in keyboard_units:
        for tone in "12345":
            lookup_tone = ime.audio_lookup_tone_for_unit(unit, tone)
            if any(
                candidate in available_names
                for lookup_unit in ime.audio_lookup_units(unit)
                for candidate in ime.audio_filename_candidates(lookup_unit, lookup_tone)
            ):
                recorded_units.add(unit)
                break

    # Publish every ㅗ+ㅇ spelling as an input alias of the canonical ㅓ+ㅇ
    # recording. This adds metadata keys only; it never duplicates WAV assets.
    for unit in tuple(recorded_units):
        components = ime.audio_unit_initial_medial_final(unit)
        if components is None or components[1:] != ('ᅥ', 'ᆼ'):
            continue
        initial, _medial, final = components
        recorded_units.add(ime.compose_syllable(initial, 'ᅩ', final))
    return recorded_units


def append_index(index: dict[str, list[str]], key: str, entry_id: str) -> None:
    key = str(key or "")
    if key:
        index.setdefault(key, []).append(entry_id)


def load_categories(path: Path) -> tuple[dict[str, str], dict[str, list[str]]]:
    labels: dict[str, str] = {}
    memberships: dict[str, list[str]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"category", "label", "hanri"}
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"Category TSV is missing required column(s): {', '.join(missing)}")

        for row_number, row in enumerate(reader, start=2):
            category = str(row.get("category") or "").strip()
            label = str(row.get("label") or "").strip()
            hanri = str(row.get("hanri") or "").strip()
            if not category and not label and not hanri:
                continue
            if not category or not label or not hanri:
                raise ValueError(f"Incomplete category row {row_number}")
            if category in labels and labels[category] != label:
                raise ValueError(f"Conflicting labels for category {category!r}")
            key = (category, hanri)
            if key in seen:
                raise ValueError(f"Duplicate category membership at row {row_number}: {category} / {hanri}")
            seen.add(key)
            labels[category] = label
            memberships[hanri].append(category)

    return labels, memberships


def build_dictionary(
    tsv_path: Path,
    audio_root: Path = DEFAULT_AUDIO_ROOT,
    category_path: Path = DEFAULT_CATEGORY_PATH,
    registry_path: Path | None = None,
) -> dict[str, Any]:
    validate_audio_filename_case(audio_root)
    tone_marker = load_tone_marker_module()
    ime = load_ime_module()
    source_bytes = tsv_path.read_bytes()
    registry_path = registry_path or tsv_path.with_name("dictionary_entry_id_registry.tsv")
    category_labels, category_memberships = load_categories(category_path)

    entries: list[dict[str, Any]] = []
    skipped_rows: list[dict[str, Any]] = []
    duplicate_keys: list[dict[str, Any]] = []
    correction_aliases: list[dict[str, Any]] = []
    effective_pairs: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    runtime_units: set[str] = set()
    counts: Counter[str] = Counter()

    with tsv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fieldnames = [str(name or "").strip() for name in (reader.fieldnames or [])]
        required = set(DICTIONARY_COLUMNS)
        missing = sorted(required - set(fieldnames))
        if missing:
            raise ValueError(f"TSV is missing required column(s): {', '.join(missing)}")

        seen_entry_ids: set[str] = set()
        for row_number, row in enumerate(reader, start=2):
            raw_reading = str(row.get("reading") or "").strip()
            raw_hanri = str(row.get("hanri") or "").strip()
            hanri = strip_inline_hanri_tone_marks(tone_marker, raw_hanri)
            corrected_raw = str(row.get("corrected") or "").strip()
            english = str(row.get("english") or "").strip()
            entry_type = str(row.get("entry_type") or "").strip()
            entry_id = str(row.get("entry_id") or "").strip()

            if not raw_reading and not hanri and not corrected_raw:
                counts["blank_rows"] += 1
                continue

            if is_comment_record(row):
                skipped_rows.append({
                    "row": row_number,
                    "reason": "comment",
                    "text": raw_reading if raw_reading.startswith("#") else raw_hanri,
                })
                counts["comment_rows"] += 1
                continue

            row = resolve_dictionary_record(row)
            simplified = row["simplified"]
            mandarin_trad = row["mandarin_trad"]
            mandarin_simp = row["mandarin_simp"]
            errors = simplified_field_errors(raw_hanri, simplified)
            if errors:
                raise ValueError(f"TSV row {row_number}: {'; '.join(errors)}")
            reading = normalized_reading(tone_marker, raw_reading)
            corrected = normalized_reading(tone_marker, corrected_raw) if corrected_raw else ""
            effective_reading = corrected or reading
            try:
                runtime_units.update(
                    unit
                    for unit, _tone in ime.split_audio_reading_units(effective_reading)
                    if unit
                )
            except Exception:
                pass
            kind = row_kind(tone_marker, hanri)
            expected_type = expected_entry_type(raw_reading, corrected_raw, kind)
            if entry_type not in ENTRY_TYPES or entry_type != expected_type:
                raise ValueError(
                    f"TSV row {row_number}: entry_type {entry_type!r} does not match "
                    f"the existing row role {expected_type!r}"
                )
            if not valid_entry_id(entry_id):
                raise ValueError(f"TSV row {row_number}: invalid entry_id {entry_id!r}")
            if not entry_id_matches_headword(entry_id, raw_hanri):
                raise ValueError(
                    f"TSV row {row_number}: entry_id does not match canonical headword "
                    f"{canonical_entry_headword(raw_hanri)!r}"
                )
            if entry_id in seen_entry_ids:
                raise ValueError(f"TSV row {row_number}: duplicate entry_id {entry_id!r}")
            seen_entry_ids.add(entry_id)
            active = bool(hanri and effective_reading)
            skip_reason = ""

            if reading and reading[0].isdigit() and corrected:
                active = False
                skip_reason = "numeric reading with corrected override is skipped by desktop loader"

            lomari = reading_to_lomari(tone_marker, effective_reading)
            reading_base = tone_marker.strip_reading_tones(effective_reading)
            audio = with_singapore_audio_when_needed(ime, audio_root, effective_reading)
            entry = {
                "id": entry_id,
                "row": row_number,
                "kind": kind,
                "entryType": entry_type,
                "active": active,
                "hanri": hanri,
                "simplified": simplified,
                "mandarin_trad": mandarin_trad,
                "mandarin_simp": mandarin_simp,
                "reading": effective_reading,
                "readingBase": reading_base,
                "lomari": lomari,
                "lomariKey": normalize_for_search(lomari),
                "english": english,
                "englishKey": normalize_for_search(english),
                "categories": list(category_memberships.get(raw_hanri, [])),
                "audio": audio,
                "form": ime.infer_default_form(effective_reading),
                "raw": {
                    "reading": raw_reading,
                    "hanri": raw_hanri,
                    "corrected": corrected_raw,
                    "english": english,
                    "entry_type": entry_type,
                    "entry_id": entry_id,
                    "simplified": simplified,
                    "mandarin_trad": mandarin_trad,
                    "mandarin_simp": mandarin_simp,
                },
            }
            if corrected:
                entry["correctedFrom"] = reading
            if skip_reason:
                entry["skipReason"] = skip_reason

            if active:
                effective_pairs[(hanri, effective_reading)].append(entry)

            entries.append(entry)
            counts[f"kind_{kind}"] += 1
            counts["active_entries" if active else "inactive_entries"] += 1
            if corrected:
                counts["corrected_entries"] += 1

    registry_errors = validate_registry(
        registry_path,
        {
            entry["id"]: canonical_entry_headword(entry["raw"]["hanri"])
            for entry in entries
        },
    )
    if registry_errors:
        raise ValueError("Invalid entry ID registry: " + "; ".join(registry_errors))

    for (hanri, reading), group in effective_pairs.items():
        group.sort(key=canonical_key)
        canonical = []
        aliases_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for entry in group:
            if entry.get("correctedFrom") and entry["raw"]["reading"].endswith("*"):
                aliases_by_source[entry["correctedFrom"]].append(entry)
            else:
                canonical.append(entry)

        for duplicate in canonical[1:]:
            duplicate_keys.append({
                "firstId": canonical[0]["id"],
                "duplicateId": duplicate["id"],
                "hanri": hanri,
                "reading": reading,
                "reason": "repeated_effective_reading",
            })
        for source_reading, aliases in aliases_by_source.items():
            for alias in aliases:
                correction_aliases.append({
                    "aliasId": alias["id"],
                    "canonicalId": canonical[0]["id"] if canonical else None,
                    "hanri": hanri,
                    "sourceReading": source_reading,
                    "reading": reading,
                })
            for duplicate in aliases[1:]:
                duplicate_keys.append({
                    "firstId": aliases[0]["id"],
                    "duplicateId": duplicate["id"],
                    "hanri": hanri,
                    "reading": reading,
                    "reason": "repeated_correction_alias",
                })

    duplicate_keys.sort(key=lambda item: item['duplicateId'])
    correction_aliases.sort(key=lambda item: item['aliasId'])

    # The desktop IME exposes a generated sandhi candidate beside every
    # citation reading. These rows are runtime-only: they participate in IME
    # candidate selection but never appear as separate dictionary entries.
    auto_sandhi_entries: list[dict[str, Any]] = []
    for entry in entries:
        if not entry["active"] or entry["form"] != "本":
            continue
        sandhi_reading = ime.citation_to_sandhi_reading(entry["reading"])
        if not sandhi_reading or sandhi_reading == entry["reading"]:
            continue
        auto_sandhi_entries.append({
            **entry,
            "id": f'{entry["id"]}-sandhi',
            "row": entry["row"],
            "reading": sandhi_reading,
            "readingBase": tone_marker.strip_reading_tones(sandhi_reading),
            "lomari": reading_to_lomari(tone_marker, sandhi_reading),
            "lomariKey": normalize_for_search(reading_to_lomari(tone_marker, sandhi_reading)),
            "form": "變",
            "autoSandhi": True,
            "citationReading": entry["reading"],
            # Dictionary cards deliberately never see this metadata row.
            "categories": [],
            "audio": {"segments": [], "files": [], "missing": []},
        })
    entries.extend(auto_sandhi_entries)
    counts["auto_sandhi_entries"] = len(auto_sandhi_entries)

    # Raw Hangul input is not limited to readings already present in the TSV.
    # Include every keyboard syllable with a recording so Web and Local audio
    # stay available for standalone input such as 엏3 -> orh3.wav.
    runtime_units.update(recorded_keyboard_units(ime, audio_root))

    priority_path = tsv_path.with_name('dictionary_priority.tsv')
    annotate_entries(entries, priority_path, read_records(tsv_path))
    entries.sort(key=lambda item: (canonical_key(item), bool(item.get('autoSandhi'))))

    known_headwords = {
        entry["raw"]["hanri"] for entry in entries if entry["raw"]["hanri"]
    }
    unknown_headwords = sorted(set(category_memberships) - known_headwords)
    if unknown_headwords:
        raise ValueError(f"Category TSV contains unknown headword(s): {', '.join(unknown_headwords)}")

    category_groups: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for entry in entries:
        if not entry["active"] or entry.get("correctedFrom") or entry.get("autoSandhi"):
            continue
        for category in entry["categories"]:
            category_groups[category].add((entry["hanri"], entry["reading"]))

    indexes: dict[str, dict[str, list[str]]] = {
        "byHanri": {},
        "bySimplified": {},
        "byMandarinTrad": {},
        "byMandarinSimp": {},
        "byReading": {},
        "byReadingBase": {},
        "byLomari": {},
        "byLomariKey": {},
        "byFirstHanriChar": {},
    }

    for entry in entries:
        if not entry["active"]:
            continue
        entry_id = entry["id"]
        append_index(indexes["byHanri"], entry["hanri"], entry_id)
        if entry["simplified"]:
            append_index(indexes["bySimplified"], entry["simplified"], entry_id)
            visible_alias = canonical_entry_headword(entry["simplified"])
            if visible_alias != entry["simplified"]:
                append_index(indexes["bySimplified"], visible_alias, entry_id)
        for name, index_name in (("mandarin_trad", "byMandarinTrad"), ("mandarin_simp", "byMandarinSimp")):
            for value in entry[name].split(";"):
                if value.strip():
                    append_index(indexes[index_name], value.strip(), entry_id)
        append_index(indexes["byReading"], entry["reading"], entry_id)
        append_index(indexes["byReadingBase"], entry["readingBase"], entry_id)
        append_index(indexes["byLomari"], entry["lomari"], entry_id)
        append_index(indexes["byLomariKey"], entry["lomariKey"], entry_id)
        if entry["hanri"]:
            append_index(indexes["byFirstHanriChar"], entry["hanri"][0], entry_id)

    runtime_unit_roman = {
        unit: reading_to_lomari(tone_marker, unit)
        for unit in sorted(runtime_units)
    }
    runtime_raw_hangul_audio = {
        f"{unit}{tone}": audio_for_unit_tone(ime, audio_root, unit, tone)
        for unit in sorted(runtime_units)
        for tone in "12345"
    }
    for unit in sorted(runtime_units):
        canonical_unit = ime.canonicalize_audio_unit(unit)
        if canonical_unit == unit or canonical_unit not in runtime_units:
            continue
        for tone in "12345":
            runtime_raw_hangul_audio[f"{unit}{tone}"] = runtime_raw_hangul_audio[f"{canonical_unit}{tone}"]
    jamo_pronunciations = dict(getattr(ime, "JAMO_PRONUNCIATION_READINGS", {}))
    runtime_jamo_lomari = {
        unit: reading_to_lomari(tone_marker, pronunciation)
        for unit, pronunciation in sorted(jamo_pronunciations.items())
    }
    runtime_jamo_audio = {
        unit: with_singapore_audio_when_needed(ime, audio_root, unit)
        for unit in sorted(jamo_pronunciations)
    }

    return {
        "schemaVersion": SCHEMA_VERSION,
        "source": str(tsv_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "sourceBytes": len(source_bytes),
        "sourceSha256": file_sha256(tsv_path),
        "idRegistrySource": str(registry_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "idRegistrySourceSha256": file_sha256(registry_path),
        "categorySource": str(category_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "categorySourceSha256": file_sha256(category_path),
        "columns": list(DICTIONARY_COLUMNS),
        "prioritySource": str(priority_path.relative_to(REPO_ROOT)).replace('\\', '/'),
        "prioritySourceSha256": file_sha256(priority_path),
        "sort": "entry_type, Tangliengim reading, headword, corrected reading, entry_id; generated variants follow source",
        "counts": dict(sorted(counts.items())),
        "skippedRows": skipped_rows,
        "duplicateEffectiveReadings": duplicate_keys,
        "correctionAliases": correction_aliases,
        "categories": [
            {
                "id": category,
                "label": label,
                "entryCount": len(category_groups.get(category, set())),
            }
            for category, label in category_labels.items()
        ],
        "entries": entries,
        "indexes": indexes,
        "runtime": {
            "unitRoman": runtime_unit_roman,
            "rawHangulAudio": runtime_raw_hangul_audio,
            "jamoLomari": runtime_jamo_lomari,
            "jamoAudio": runtime_jamo_audio,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_TSV_PATH)
    parser.add_argument("--categories", type=Path, default=DEFAULT_CATEGORY_PATH)
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--audio-root", type=Path, default=DEFAULT_AUDIO_ROOT)
    parser.add_argument("--check", action="store_true", help="validate only; do not write output")
    args = parser.parse_args()

    data = build_dictionary(args.input, args.audio_root, args.categories, args.registry)
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=False) + "\n"

    if args.check:
        print(f"ok: {len(data['entries'])} entries, {data['counts'].get('active_entries', 0)} active")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.is_file() and args.output.read_text(encoding="utf-8") == encoded:
        print(f"unchanged {args.output.relative_to(REPO_ROOT)}")
    else:
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
        print(f"wrote {args.output.relative_to(REPO_ROOT)} ({len(encoded.encode('utf-8'))} bytes)")
    print(f"entries: {len(data['entries'])}; active: {data['counts'].get('active_entries', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
