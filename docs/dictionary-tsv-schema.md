# Dictionary TSV schema

`data/hokkien_hanri_dict.tsv` is UTF-8, NFC-normalized, CRLF-terminated TSV with eight columns in this order:

| Column | Meaning |
| --- | --- |
| `reading` | Input Hangul reading, including tone digits and an optional trailing `*` for a nonstandard spelling. |
| `hanri` | Hanri headword or a Hangul-only override key. |
| `priority` | Positive integer static candidate priority; lower values rank earlier. |
| `corrected` | Target Hangul reading for a `*` correction alias, or a hidden pronunciation for a numeric key. |
| `english` | Optional English gloss. |
| `entry_type` | Required semantic row role, defined below. |
| `entry_id` | Unicode-derived identity for this source row, in the form `U+XXXX[_U+XXXX...]_NN`. IDs are still pre-release. |
| `simplified` | Simplified Chinese lookup alias. Required when `hanri` contains Hanri; empty for pure Hangul, numeric, or other headwords without Hanri. |

`hanri` remains the canonical display and identity source. `simplified` is search
metadata only: it does not change IDs, priorities, candidates, pronunciation, or
canonical TSV ordering. Mixed aliases preserve every non-Hanri code point
(Hangul, tone symbols, punctuation, digits, Latin text, and symbols) exactly.
Identical Traditional/Simplified spellings are stored explicitly on Hanri rows.
Unmapped rare Hanri are retained. The sorter also excludes `simplified` from its
final digest tie-breaker.

The Local writer generates this field using the pinned, vendored OpenCC `tw2s`
converter; it requires no extra installation. Phrase conversion applies only to
contiguous Hanri spans. Existing manually reviewed aliases are preserved when
IDs are allocated or the TSV is sorted. Review the populated choices in
[`simplified-lookup-review.md`](simplified-lookup-review.md). Unlikely secondary glyphs
and Traditional 著 alternatives to Simplified 着 are not review cases.
The generated JSON (schema 8) retains the alias on each existing entry and adds
`indexes.bySimplified`; Dictionary searches score it like canonical Hanri and
continue displaying the canonical headword. No additional lexical rows are made.

`entry_id` belongs to a real dictionary row, not its current position. Ordinary editing and sorting do not renumber IDs. An approved pre-release identity migration may change an ID directly. The base encodes every NFC-normalized Unicode code point in the identity headword with uppercase hexadecimal notation. The first entry for a headword receives `_00`, the first additional entry `_01`, and so on without a two-digit maximum. For example, the base `行` entry uses `U+884C_00`, while `食飽` uses `U+98DF_U+98FD_00`. `_00` is a real TSV entry, never a synthetic headword group.

The identity headword is the stored `hanri` value after removing the nine legacy inline tone glyphs and normalizing to NFC. This is the same headword users see: Hangul-only overrides use Hangul code points, mixed entries retain their literal script sequence, number pronunciations use their digit, and the `리1호2*` correction alias identifies by its displayed `릐호` headword. Stored/displayed text is not rewritten during ID generation.

Existing IDs survive changes to gloss, priority, type, and physical order. Before public release, an approved canonical-headword or ordinal change updates the TSV ID and registry directly; unpublished former IDs need no alias, redirect, or tombstone. The future public path is derived from the same stored ID through `entry_public_path`: `U+5BB6_U+5DF1_00` maps to `/dictionary/家己/`, while `U+5BB6_U+5DF1_01` maps to `/dictionary/家己/01/`. URLs are percent-encoded in code; these examples show their decoded form. There is no separate URL ordinal field. Dictionary entry-page routing is not implemented yet.

`data/dictionary_entry_id_registry.tsv` is the allocation ledger. It has `entry_id`, `canonical_headword`, and a reserved `redirect_entry_id` column, which stays empty before public ID release. The current registry contains active Unicode IDs only: the old `tlg-...` development IDs and unpublished migration redirects have been removed. Normal new-entry allocation uses the next suffix already recorded for that headword. Approved pre-release migrations may revise IDs and remove obsolete registry records directly. After public IDs are frozen, redirects and retired suffixes can be retained for compatibility. New Local IME entries reserve the next suffix directly in the repository registry before appending the repository TSV row. Sync TSV commits and pushes both repository files, without transferring separate copies.

An existing dictionary must retain its registry. Writers refuse to regenerate a missing ledger from active rows, because that could change allocations made during normal editing. A brand-new empty dictionary can create its initial registry.

The four `entry_type` values are:

| Value | Use |
| --- | --- |
| `lexical` | An ordinary entry whose `hanri` contains CJK characters, including mixed Hanri-Hangul headwords. Multiple readings of the same headword remain separate rows. |
| `correction_alias` | A nonstandard `reading` ending in `*` with a nonempty `corrected` reading. This type also covers the existing alias whose headword is Hangul-only. Its canonical reading is a separate entry. |
| `hangul_override` | A Hangul-only `hanri` key supplying an explicit reading or tone for that input. A leading typographic apostrophe is allowed. |
| `number_pronunciation` | A numeric input key beginning with an Arabic digit and a nonempty `corrected` Hangul pronunciation. The desktop number loader handles these rows separately. |

The four types describe source rows. Auto-generated sandhi candidates inherit their source row's `entryType` and derive their runtime ID from the source `entry_id`, but have no TSV row of their own. JSON `kind` remains a separate structural classification (`plain_hanri`, `mixed_hanri`, `hangul_override`, or `numeric_override`) used by the current web interfaces. `entryType` itself does not change candidate eligibility. The physical TSV order still breaks ties after priority, so manually editing or canonically sorting rows can change tied candidate/default order.

The canonical physical order groups `hangul_override`, `lexical`, `correction_alias`, then `number_pronunciation`. Within each group, readings sort syllable by syllable: initial, vowel, final, next syllable. Tone comes after the complete syllabic spelling. Hanri, corrected reading, and priority resolve later ties. A digest of the exact row resolves rows otherwise indistinguishable by those fields; English never serves as a linguistic filing key. Unsorted TSV files remain valid and work normally, but the validator prints a maintenance notice.

The initial order is `ㄱ ㄲ ㄴ ㄷ ㄸ ㄹ ㅁ ㅂ ㅃ ㅅ ㅇ ㅈ ㅉ ㅊ ㅋ ㅌ ㅍ ㅎ ㆆ`.

The vowel order is `ㅏ ᅟᅷ ㅐ ㅑ ᅟᆤ ㅓ ㅔ ㅕ ㅖ ㅗ ㅘ ㅙ ㅚ ㅛ ㅜ ㅞ ㅟ ㅠ ㅡ ᅟힻ ㅢ ㅣ`.

The sorter uses open syllables first, followed by the explicit Tangliengim final order `ㄱ ㄴ ㄷ ㄹ ㅀ ㅁ ㅂ ㅇ ㅎ`. Obsolete finals `ㅅ` and `ㅊ` are not in this table. Unrecognized legacy characters receive a deterministic fallback rank; sorting never edits their spelling.

The shared comparator lives in `tools/tangliengim_collation.py`. To sort manually, run:

```sh
python tools/sort_dictionary_tsv.py
```

The sorter retains the header, comments, every data row, UTF-8, NFC, and CRLF line endings. It does nothing when the file is already canonical. The local IME can continue appending rows; sorting is a separate maintenance action.

The initial Task 5c sort moved 2,746 of 2,749 data rows. It reordered 140 reading-key candidate lists and changed 26 tied Hanri default readings. Six menus for standard spellings now select their canonical row ahead of an equivalent correction alias; the starred alias spellings remain searchable. No row content, full candidate-list membership, priority, Hangul override winner, category, or audio/Lomari runtime data changed. Genesis 3.1 subsequently refreshed `tests/fixtures/dictionary-baseline.json` to the reviewed v3.1 state; see [the consolidation report](genesis-3.1-consolidation.md).

New rows written through the local IME include both `entry_type` and a newly reserved Unicode `entry_id`. Manual additions must also reserve the next never-used suffix in the registry; do not derive it from row position or only from currently active rows. Validate and rebuild from the repository root:

```sh
python tools/validate_dictionary_tsv.py
python tools/build_dictionary_json.py
```

If a new row does not fit one of these roles, leave its classification for review rather than labeling it `lexical` by default.
