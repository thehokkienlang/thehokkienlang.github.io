# Tangliengim dictionary production contract

## 1. Scope

This is the authoritative current schema and maintenance reference after Exodus
IV. Migration reports describe their historical checkpoints, not competing
current schemas. This consolidation changes no lexical data, IDs, collation,
ranking formula, pronunciation or audio. IDs remain pre-release: Exodus IV does
not declare them publicly frozen.

Verified snapshot: 2,737 source records; 2,727 runtime-active source records;
2,705 generated sandhi views; 5,442 total JSON records. The ten source records
excluded from ordinary candidates are number pronunciations, not missing data.
These counts describe this checkpoint and are not schema limits.

## 2. Source-of-truth files

| File | Responsibility |
| --- | --- |
| `data/hokkien_hanri_dict.tsv` | Canonical lexical forms, readings, search metadata, source roles and stable IDs. |
| `data/dictionary_priority.tsv` | Sparse contextual static-order exceptions; not a second dictionary. |
| `data/dictionary_entry_id_registry.tsv` | ID allocation ledger, including reserved suffixes not currently in the dictionary. |
| `data/dictionary_categories.tsv` | Curated memberships of exact source records. |
| `desktop/`, `shared/`, `public/audio/` | Shared input/pronunciation implementations and original audio assets, not another lexical dictionary. |

`public/data/*.json` and `_site/` are generated. Do not edit them to correct an
entry. Local/Desktop consumes the same repository TSV/ledger; there is no second
maintained Local TSV. Browser JSON, Python lookup maps and search indexes are
derived views. Per-user learned preferences are separate runtime state.

## 3. Main dictionary schema

UTF-8 without BOM, NFC, CRLF, final newline, nine fields in this exact order:

```text
hanri simplified reading mandarin_trad mandarin_simp english corrected entry_type entry_id
```

The actual header uses tabs. Comment/section rows begin with `#` in `hanri` or
`reading`, have the same field count, and retain their positions during sorting.
No whitespace padding, malformed field counts, or blank physical records.

| Field | Meaning and blanks | Role/effects |
| --- | --- | --- |
| `hanri` | Required canonical Hokkien form; may contain Hanri, mixed scripts, pure Hangul or a numeric key. | Linguistic headword; supplies the identity namespace and display/search text; canonical tie-breaker. |
| `simplified` | Simplified-script form of that same Hokkien form; required for Hanri-containing forms, blank without Hanri; permits `〃`. | Linguistic search metadata only; not identity, ranking or pronunciation. |
| `reading` | Required Tangliengim reading/input, citation-tone digits and optional trailing correction `*`; digit key for number rows. | Linguistic input/search and pronunciation; contributes to canonical ordering, not an ID ordinal. |
| `mandarin_trad` | Optional concise Traditional Mandarin semantic equivalent; blank if unavailable/unspecified; permits `〃`. | Semantic search only, never another Hokkien headword, ID or candidate prior. |
| `mandarin_simp` | Optional Simplified form of that Mandarin equivalent; requires a corresponding Traditional value; permits `〃`. | Semantic search only; distinct from Hokkien `simplified`. |
| `english` | Optional English gloss; blank if unavailable/unspecified. | Semantic display/search only, not ranking/identity. |
| `corrected` | Hangul correction/override reading; required for correction aliases and number pronunciations, normally blank on lexical rows. | Linguistic input/pronunciation relationship; canonical tie-breaker, not independent identity. |
| `entry_type` | Required value from the four roles below. | Technical classification/ordering; not a translation or ID namespace. |
| `entry_id` | Required unique Unicode-derived source-record ID. | Authoritative identity/reference; final deterministic tie-breaker, not user-entered search text. |

Different readings, polysemy and legitimate homophones may be separate records.
Do not merge records just because display strings or readings overlap. Existing
legacy tone symbols are parsed by shared tone normalization; Exodus IV does not
rewrite their linguistic source content. New tone-bearing readings use the
existing writer normalization. Multiple semantic equivalents use `; `.

## 4. Special values and inheritance

`〃` is source storage shorthand, valid only as an entire cell in:

| Field containing `〃` | Resolved source |
| --- | --- |
| `simplified` | `hanri` |
| `mandarin_trad` | `hanri` |
| `mandarin_simp` | Already-resolved `mandarin_trad` |

The source must be nonempty. Blank is unavailable, inapplicable or intentionally
unspecified; it is never implicit inheritance. Pure-Hangul Hokkien forms normally
have blank `simplified`, not `〃`. Other fields and embedded ditto marks are invalid.

`家己 / 〃 / 自己 / 〃` resolves to Hokkien `家己` and Mandarin `自己` in both
scripts. `世界 / 〃 / 〃 / 〃` resolves all three lookup fields to `世界`.
`tools/dictionary_schema.py` resolves these rules centrally for builders and
Python loaders. Runtime fields, including generated `raw` metadata, contain
resolved strings; indexes never contain `〃`. Frontends do not translate it.

The Simplified-Hokkien converter processes contiguous Hanri spans with the pinned
vendored OpenCC `tw2s` subset, preserving non-Hanri content exactly. If the entire
nonempty result equals the headword, store `〃`. This is script conversion, not
Mandarin translation. Uncertain meanings remain blank and in the review report;
validation must not invent translations.

## 5. Entry types

| Type | Current count | Runtime treatment |
| --- | ---: | --- |
| `hangul_override` | 52 | Pure-Hangul input/default-reading overrides, including applicable apostrophe prefixes; active and searchable in the existing Hangul path. |
| `lexical` | 2,666 | Ordinary Hanri or mixed Hanri-Hangul lexical records; active search/candidate sources. |
| `correction_alias` | 9 | Nonstandard `reading` ending in `*` with `corrected`; active correction lookup, not an extra displayed canonical lexical result. Includes the existing Hangul-only alias. |
| `number_pronunciation` | 10 | Digit input keys with corrected pronunciations; retained in JSON as inactive ordinary entries and loaded separately by the number-pronunciation engine. |

Every type requires an ID. JSON `kind` is a separate display/runtime structural
classification (`plain_hanri`, `mixed_hanri`, `hangul_override`, `numeric_override`),
not another source taxonomy. Generated candidates inherit their source role.
An unfamiliar row requiring a new role needs review, not an invented classification.

## 6. Stable entry IDs and permanence

`U+XXXX[_U+XXXX...]_NN` encodes the canonical identity headword: stored `hanri`
with the existing nine inline tone annotations removed, then NFC-normalized.
Each code point is uppercase hexadecimal, at least four digits. The ordinal
has at least two digits, with no maximum of 99.

`_00` is a real base entry, not a container. `_01`, `_02`, etc. are distinct
additional records. IDs survive sorting and edits to glosses/search metadata;
normal builds/sorts never allocate or renumber them. New allocation uses the
next suffix after every ID already reserved for that headword, not source position
or only surviving rows. Deleted suffixes are not automatically reused, and a
deleted `_00` does not cause surviving entries to be renumbered.

The ledger header is `entry_id canonical_headword redirect_entry_id` (tabs).
Currently it contains 2,741 assignments: 2,737 current records and four
registry-only reservations (`U+B098_00`, `U+B3C4_U+C704_00`, `U+B990_U+D638_00`,
`U+B990_U+D638_01`). Every current ID must agree with its ledger headword.
All redirect cells are empty; no active `tlg-...` identifiers remain.

Before explicit public freeze, approved identity migrations can update IDs and
ledger directly without preserving unpublished history. This is not permission
to casually renumber normal edits. After explicit freeze/public release, IDs
must remain permanent; compatibility for changed/deleted public identifiers
requires an explicitly approved policy/implementation. The reserved redirect
column is not a currently supported public routing mechanism. Do not invent
redirects or declare a freeze during ordinary maintenance.

One shared identity parser drives IDs and future URLs:
`U+5BB6_U+5DF1_00` maps to `/dictionary/家己/`; `_01` maps to
`/dictionary/家己/01/`. `entry_public_path` percent-encodes the headword and derives
the ordinal from the ID. There is no separate URL number or stored URL field.
Human-readable entry routing is not implemented. `/00/` is not the intended
canonical base URL. Existing dictionaries must retain their allocation ledger;
writers refuse to reconstruct a missing ledger from surviving rows.

## 7. Canonical sorting

`tools/tangliengim_collation.py` and `tools/sort_dictionary_tsv.py` file records by
`hangul_override`, `lexical`, `correction_alias`, `number_pronunciation`, then
reading, stored Hanri code points, corrected reading, stable ID.

Reading comparison is initial, vowel, final, next syllable; tones break ties
after the whole syllabic spelling, then exact normalized spelling. Inventories:

- Initial: `ㄱ ㄲ ㄴ ㄷ ㄸ ㄹ ㅁ ㅂ ㅃ ㅅ ㅇ ㅈ ㅉ ㅊ ㅋ ㅌ ㅍ ㅎ ㆆ`.
- Vowel: `ㅏ ᅟᅷ ㅐ ㅑ ᅟᆤ ㅓ ㅔ ㅕ ㅖ ㅗ ㅘ ㅙ ㅚ ㅛ ㅜ ㅞ ㅟ ㅠ ㅡ ᅟힻ ㅢ ㅣ`.
- Final: open first, then `ㄱ ㄴ ㄷ ㄹ ㅀ ㅁ ㅂ ㅇ ㅎ`.

Display filler `ᅟ` is not a vowel identity; special vowels use `ᅷ`, `ᆤ`, `ힻ`
internally. Unknown retained legacy characters receive deterministic fallback
positions, not rewritten spelling. Sorting preserves row contents and comment
positions, and is byte-idempotent. Search metadata and glosses are excluded.
Source position is neither identity nor ranking state. The validator may issue
an unsorted maintenance notice, but the release gate requires canonical order
with the read-only sorter `--check`.

## 8. Static candidate priority

`data/dictionary_priority.tsv` has four tab-separated fields:
`lookup_key entry entry_id rank`. Its 97 current rows are sparse manual
exceptions. `lookup_key` is a normalized context, `entry_id` identifies one
eligible source, `entry` must match its stored Hanri as a checked informational
label, and `rank` is a positive one-based absolute slot in the complete group.
Unspecified sources fill remaining slots in deterministic canonical order.
Filtering does not reinterpret these full-group slots.

Shared `tools/dictionary_ranking.py` validates eligibility, ID/label integrity,
duplicate context/ID relationships, conflicting slots and out-of-range ranks.
Source identities precede their own generated variants; anonymous/toneless
fallbacks remain subject to the existing class boundaries. Row order never
supplies hidden priority. Default pronunciation, segmentation, search, Lomari
and audio use static rules, not personal learning.

## 9. Adaptive per-user ranking

Within protected eligible candidate classes, identity is normalized lookup
context plus source `entry_id`. The established lower-is-better score is:

```text
static_index * 2 - selection_count
```

Counts saturate at 255, with no decay. Existing deterministic static order
breaks ties. Only explicit eligible selection learns: menu display, default
commit, navigation, dismissal, anonymous/generated fallback and dictionary
search do not train a source. Explicit source-backed sandhi selections train
their existing source ID. Generated views retain existing source/variant
constraints; distinct source IDs do not share statistics accidentally.

Web storage: `tangliengim.candidatePreferences.v1` in localStorage. Local/Desktop
and classic Pad share a stable per-user file via `tools/candidate_preferences.py`:
on Windows `%LOCALAPPDATA%/Tangliengim/candidate-preferences-v1.json`, on other
platforms the corresponding user data root. A localhost port change does not
discard Desktop preferences. The version-1 payload contains `selections` keyed
by context and ID. Malformed/stale data and storage failures fail safely;
atomic writes, concurrent updates, resets and duplicate commit receipts are
covered by Exodus II. Clear preferences to restore cold-start order without
editing any source file. Never commit/sync this per-user state to the dictionary.
See [ranking detail](candidate-ranking-model.md) for the exact learning triggers.

## 10. Structural references and categories

Anything meaning "this exact dictionary record" uses `entry_id`. Human-readable
labels may accompany it but cannot substitute for identity. Categories have
`category label entry entry_id`: one row is one explicit active source membership.
The current 178 memberships are food 103 and place-names 75; the latter includes
one correction alias, yielding 74 visible lexical results. Historically 174
headword memberships expanded into these 178 exact relationships. Distinct
readings need separate rows; adding a same-headword record does not add it to a
category automatically. Reject unknown/inactive IDs, stale labels and duplicates.

Correction relationships contain source alias/canonical IDs; ambiguous targets
fail rather than taking the first. Selected readings retain source ID plus
variant and committed-text span snapshots through menu recovery/HTML bridges;
unknown IDs do not fall back to headword guesses. Custom pronunciation snapshots
may remain anonymous. Search keys, display text, orthographic/grammatical literals,
reading transformations, punctuation, recorded content and input-span matching
remain legitimate strings. Stable identity does not mean "remove all Hanri
strings from code". See [the historical reference audit](exodus-iii-reference-migration.md).

## 11. Generated/runtime data and versioning

`tools/build_dictionary_json.py` produces `public/data/hokkien-hanri-dict.json`
from the main TSV, ledger, priority/category files, shared Python pronunciation
engine and audio inventory. Source IDs stay intact. Generated sandhi views use
runtime `id = source entry_id + '-sandhi'`; `raw.entry_id` stays the permanent
source ID. These views have no allocated ledger/TSV records. Fallback candidates
are transient, not independently permanent dictionary entries.

Ten number source objects remain `active: false` because digit/corrected
pronunciations are handled separately, leaving 2,727 active sources. Adding 2,705
active sandhi views to all 2,737 source objects yields 5,442 JSON entries.
Generated `raw` metadata is resolved, not a source TSV copy for manual editing.
`runtime` contains shared pronunciation/audio lookup metadata. Build metadata
records source checksums; `build_site.py` rebuilds data, versions assets by
content and constructs `_site` for `/ime/` and `/dictionary/` together.

JSON already has centralized `schemaVersion = 10`; preserve it because Exodus IV
does not change the generated structure. The main TSV exact-header contract is
defined by `DICTIONARY_COLUMNS`, not a new per-row version column. Preference
version 1 is independent from dictionary schema 10. A clean build needs source
data, Python with Tkinter, Node and audio assets, not old generated JSON.

## 12. Search indexes and consumers

Hanri, Hokkien Simplified, Hangul/reading (including existing Lomari matching),
Mandarin Traditional, Mandarin Simplified and English find existing records.
Strings are lookup values, not record IDs. Search ranking/relevance is distinct
from adaptive candidate ranking. Output displays the canonical Hokkien entry
and retains its source identity; semantic metadata creates no new records.
Browser apps consume generated indexes, Python loaders use the same named
columns/resolver, and the Local web shell serves shared browser code with local
HTML/TSV extensions. The supported classic Pad reads the same repository data.

## 13. Validation and release checks

`validate_dictionary_tsv.py` checks header/arity, UTF-8/NFC/CRLF, whitespace,
required values, inheritance, script metadata, entry roles/IDs, ledger agreement,
sparse priority and category references. The builder additionally verifies
runtime role classification and correction targets. These focused checks share
schema/reference helpers; there is no competing frontend ditto parser.

Normal full gate: `python tools/check_release.py`. It checks syntax, source
validation and read-only canonical order, rebuilds the site, runs dictionary
tests/baseline, stable references, static/reversed-row ordering, adaptive learning
and safeguards, Desktop bridge, PCM/legacy parity, site integrity and built Web
apps. Each full gate runs Web integration once against the built site; source-only
mode runs it once against rebuilt source data. No baseline is refreshed silently.

Portable/CI source gate: `python tools/check_release.py --source-only` rebuilds
runtime JSON but not `_site`. CI separately checks its actual built site.
Optional deep audits include exhaustive WAV coverage/duration analysis, live
mobile-device composition checks, linguistic review and deliberate baseline
capture after approved semantic changes. They are not automatic lexical repairs.

## 14. Production editing workflow

1. Edit the repository main TSV, never generated JSON. Preserve existing IDs.
   Local "add reading" writes all nine fields, reserves a new ID in the ledger,
   converts only Hokkien Simplified, and leaves unknown gloss/Mandarin cells blank.
2. For manual new rows, leave `entry_id` blank temporarily and run
   `python tools/assign_dictionary_entry_ids.py`. It allocates the next reserved
   suffix and synchronizes the ledger; normal allocation does not regenerate IDs.
3. Edit only deliberate static exceptions in `dictionary_priority.tsv`, and add
   exact category memberships in `dictionary_categories.tsv`. Keep their checked
   informational labels synchronized after approved headword changes.
4. Run `python tools/sort_dictionary_tsv.py` as a separate maintenance action;
   Local appends do not implicitly reorder the dictionary.
5. Run `python tools/check_release.py` to validate and rebuild everything.
   Investigate failures instead of hand-editing JSON or refreshing baselines.
6. Inspect the diff, then commit/push only when requested. Local Sync TSV publishes
   repository dictionary/ledger/priority changes; it does not transfer a second
   Local TSV or publish personal preference statistics.

Normal additions require no ranking points, URL fields, personal scores or
duplicate Unicode identity metadata. Keep linguistic uncertainty in the existing
review workflow, not TODO/question-mark translations in source cells.

## 15. Compatibility policy and architecture summary

Production readers require the exact current named header. Headerless positional
Local editor parsing and unreachable headerless metadata branches were removed.
Intentional six/seven/eight-column import support remains isolated in
`assign_dictionary_entry_ids.py` and covered by migration tests. Its old
`tlg-...` recognition is import-only, not an active identity/redirect system.
The Task 6e zero-base and Simplified/Mandarin migration tools remain explicit
historical tools, not runtime loaders or automatic new-entry translators.
The small missing/invalid-file classic fallback and built-in numeric defaults
remain diagnostic/offline resilience, not supported old production schemas.

```text
SOURCE DICTIONARY -> lexical/search data + stable source IDs
STATIC PRIORITY -> sparse human-curated contextual overrides
STRUCTURAL REFERENCES -> exact stable source IDs
BUILD -> validated generated/runtime dictionary and shared site
SEARCH -> linguistic strings resolve to stable records
USER ADAPTATION -> local (lookup context, entry_id) state over static ranking
```

For the final verification/checkpoint, see [Exodus IV readiness](exodus-iv-readiness.md).
