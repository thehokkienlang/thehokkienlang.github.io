# Harmonisation 3.2 Dictionary Sync

Follow-up to the [mixed-script website audit](harmonisation-3.2.md),
reviewed with the author on 2026-10-25.

## Source Changes

- Added 27 missing headwords or readings and replaced eight obsolete headwords.
- Allocated 35 new source IDs; the active TSV grows from 2,778 to 2,805 rows.
- Removed the eight superseded rows from the active TSV and stored their full
  original records in `dictionary_defunct.tsv`, linked to their replacements.
- Existing valid Hanri readings remain. Existing 𨑨迌 and 按怎 entries were
  not duplicated or split into invented independent component readings.
- The same canonical TSV and rebuilt runtime JSON serve the dictionary,
  shared web IME, and local desktop readers. No independent Local TSV was created.

## Replacements

| Previous active headword | Replacement |
| --- | --- |
| 뾔ˉ | 𣍐 |
| 뾔당 | 𣍐당 |
| 음시ˉ | 毋是 |
| 캏 | 較 |
| 허ˉ | 予 |
| 뾔打限 | 𣍐打限 |
| 뾔要緊 | 𣍐要緊 |
| 음著 | 毋著 |

Five previous headwords were purely Hangul; three were mixed-script forms.
Their former IDs remain reserved, while categories and priority/correction
references follow the native editor's replacement rules.

Disposal/object-marking 가 remains Hangul, with its gloss narrowed to that
function. Relational 共 / 가5 is a separate lexical entry. Likewise, prohibitive
매 and interjection 아 are not removed merely because 覓 and 仔 exist. The
retained pronouns and native forms, and foreign transcriptions such as 가야,
remain unchanged.

## Reading Decisions

Citation readings come from existing source records, the v3.2 manual, or explicit
author confirmation. They are not copied blindly from sentence sandhi. Low tone
3 remains unmarked in the source spelling, following existing TSV conventions.
Multi-syllable entries preserve their normal word-internal tone spelling and
the final citation tone.

The author confirmed 偌 똬5, 嬰 일1, 彎 완1, 哈 핳3, 𬦰 벻3,
運將 운2쟝3, source 𨘗 위3/뒤3, and destination 對 위3. New compounds
include 嬰仔, 爾爾, 好康, 偌邇, 無奈, 無代無誌, and 彎來斡去.

The Egg's `應該是도2 一个小學’에 老師` uses **底**, meaning “which”,
not 就. Both language presentations and their source-recovery ledger are
corrected without changing the pronunciation. The existing 底 / 도2 entry
is reused. 就 retains 쥬5 and gains the prescribed colloquial 됴5; no 도2
reading is added to 就.

## Verification

The native `DictionaryEditorService` performed one validated transaction,
including ID allocation, canonical sorting, Simplified-field conversion,
reference updates, and recoverable retirement. All nine-column, UTF-8/NFC,
CRLF, registry, and archive requirements are preserved.

The reviewed source changes are recorded in `harmonisation-3.2-dictionary.json`,
including before/after data hashes, new records and retired replacements.
All new source entries resolve to existing audio; no recordings were invented.
Surviving runtime entries keep their previous readings and audio. Only the
disposal 가 record and its derived view change gloss/search metadata.

The Python tone engine now recognises CJK Extensions B-F, matching the shared
Web engine. This is needed for 𬦰 (Extension E); it is not a one-character
classification exception. No tone-sandhi or romanisation algorithm changes.
Dictionary results and web candidates reuse the existing character-scoped
rare-Hanri web font. The classic Pad privately loads its matching TTF for
the same six supplementary characters; normal Hanri retain Noto Sans TC.

Release snapshots are refreshed through the editor's existing publication
sequence after reviewing the exact dictionary-data differences. They record
the approved additions and retirements rather than ignoring regression failures.
