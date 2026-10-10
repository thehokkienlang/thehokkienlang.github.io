# Exodus III: stable-ID reference migration

Historical Exodus III report; its future-phase statements apply to that checkpoint.
Current architecture and completed Exodus IV: [production schema](dictionary-tsv-schema.md).

## Scope and prerequisites

Exodus I/II and the original full release gate passed before this migration.
Static priority and learned preferences already use exact source `entry_id`.
Neither architecture, its scoring rules nor preference storage is changed here.
Exodus IV remains future work. No commit or push is part of this task.

The actual input has 2,737 source rows, including ten number-pronunciation rows:
2,727 runtime-active source records and 5,442 generated runtime entries. The
request's historical 2,745 active-entry count is not the current checkout count.
This migration preserves the current actual records rather than inventing rows.
The main TSV, registry, sparse priorities, Mandarin review data and WAV files
are unchanged, including source order and every active ID.

## Identity-bearing mechanisms migrated (classification A)

| Mechanism | Old reference | New reference |
| --- | --- | --- |
| Category source and builder | Raw headword membership | Explicit source `entry_id`, checked informational `entry` label |
| Web menu selection recovery | Headword plus reading | Source ID plus generated-sandhi variant, within the same replacement span |
| Web remembered-candidate recovery | Reading equality | Source ID plus variant; anonymous output can match only another anonymous output |
| Classic popup reuse/reselection | Display labels/readings and candidate position | Source ID plus variant; position remains transient UI state |
| Selected-reading annotation chain | Source object reduced to text-only pronunciation | Web Hanri/Hangul serializers, classic remembered Hanri spans and Desktop bridge retain the source ID |

Selected pronunciation and committed-text spans remain content snapshots. An
ID is retained alongside them, not used to rewrite already committed user text.
The Desktop bridge validates each supplied ID against the complete source TSV,
not the deduplicated classic menu. Unknown, malformed or inactive IDs fail
clearly; there is no text-based substitute. Literal/custom pronunciation spans
have no record ID and remain supported. No legacy persisted text-keyed record
preferences were found, so no speculative user-data migration was added.

## Category migration

The source header is now `category`, `label`, `entry`, `entry_id`.
There were 174 raw-headword memberships. The old builder deliberately applied
each membership to every matching source record. The migration expands that
existing membership set into 178 explicit record relationships, not arbitrary
`_00` choices. Source category order and labels are retained.

| Category | Explicit source memberships | Existing visible-entry count |
| --- | ---: | ---: |
| food | 103 | 103 |
| place-names | 75 | 74 |

The extra place-names membership is an already-included correction alias that
the dictionary does not display as an additional lexical result.

The four multi-record families are independently referenced:

- 牛奶: `U+725B_U+5976_00`, `U+725B_U+5976_01`.
- 奶: `U+5976_00`, `U+5976_01`.
- 長泰: `U+9577_U+6CF0_00`, `U+9577_U+6CF0_01`.
- 新加坡: `U+65B0_U+52A0_U+5761_00`, `U+65B0_U+52A0_U+5761_01`.

Repository context resolves all four families; none needs manual review.
Categories now enumerate current records. A new record with an existing
headword is not automatically curated into a category: add its ID explicitly
if desired. This avoids silently inventing future membership.

`entry` is the exact stored source `hanri`, including any existing mixed-script
tone notation. It is informational but checked: a stale label is an error, not
a fallback key. No lexical spelling cleanup is part of this migration.

## Existing ID-based relationships retained

- The nine generated correction relationships already contain `aliasId` and
  `canonicalId`. Reading correction remains a linguistic input transformation.
  The builder now rejects multiple possible canonical targets instead of
  picking the first. A missing target remains explicitly `null`, never guessed;
  there are no missing targets in the current data.
- Sparse priority `lookup_key + entry_id` remains authoritative. Its `entry`
  companion label is already validated; no string-based substitute was found.
- Adaptive `lookup_key + entry_id`, variant/fallback constraints, selection
  triggers and preference format are unchanged.
- Runtime `id` values ending in `-sandhi` describe generated views of a source;
  `raw.entry_id` remains the permanent identity. Variant flags are transient,
  not a new permanent composite identity.
- Registry and headword/ordinal URL helpers already resolve the same identity.
  No URL work, redirects, ID allocation or ID migration was necessary.
- No additional curated lists, record-specific pins or see-also links were found.

## Residual audit (classifications B/C)

Eight important raw-text reference classes intentionally remain:

1. Hanri, Simplified, Mandarin, Hangul, English and Lomari search keys: user
   input matches records, which retain IDs. These are lookup, not identity.
2. Readings and correction strings: pronunciation/input transformations.
3. Dictionary card grouping and visible category counts: presentation grouping
   of equivalent output, not persisted relationships between records.
4. Web/classic candidate deduplication: equivalent output is shown once while
   the representative retains its exact source ID. Removing this would change
   cold-start menus, notably the equivalent 下 readings `_00` and `_01`.
5. Committed-text spans and explicit tones: literal user content and positions,
   alongside record IDs only when the user selected a source-backed option.
6. Orthographic/morphological checks and syllable-to-audio maps: linguistic
   forms, not dictionary-record special cases.
7. Temporary candidate indices, canonical sort keys and source line numbers:
   navigation, sorting and diagnostics; never persistent record identity.
8. Labels, documentation and regression inputs/expected display strings:
   human-readable content, not structural targets.

No unresolved classification-D structural references remain in this audit.
No IDs are synthesized from a display string when a supplied ID is invalid.

## Validation and verification

`tools/dictionary_references.py` owns exact-record resolution and category
validation. The source validator and builder both use it. It checks header,
arity, nonempty/NFC/trimmed fields, active known IDs, duplicate IDs, duplicate
memberships, consistent category labels and stale informational labels.

`tests/test_dictionary_references.py` covers controlled display changes,
reversed rows, independent same-headword `_00`/`_01`, invalid IDs, source
validation, selected-reading transport and classic popup recovery.
`tools/check_entry_references.cjs` exercises the real shared Web controller's
exact-ID recovery, variants, stale-ID omission and annotation serialization.
Both are included in the release gate.

The existing static/adaptive fixtures and dictionary baseline are not refreshed.
Generated JSON is rebuilt, not hand-edited. Its only expected semantic-neutral
change is `categorySourceSha256`, recording the new category source structure.
The gate verifies search, static/adaptive ordering, Local/Desktop bridge,
canonical collation, audio/runtime parity and the built site against the
existing reference state.

## Verification results

Final verification passed in both the isolated test copy and the installed
checkout. The installed test run uses the actual active Local launcher for the
new classic/bridge reference tests:

- 50 Python dictionary/collation/audio/reference tests, including eight new
  reference tests.
- Existing 2,239-key dictionary baseline and complete pre-migration JSON
  comparison, without baseline regeneration.
- 7,151 exact Web and 6,884 exact classic cold-start menus; learned preference
  fixtures and all Exodus II safeguard checks.
- Reversed-row static/default checks: 3,111 Hanri contexts, 61 Hangul defaults,
  3,086 Python/Web contexts and 25 established mixed-script contexts.
- Web dictionary/search, Desktop shell bridge, 16 audio waveforms and legacy
  behaviour parity.
- Built Dictionary/IME pages, 5,442 runtime entries, 1,507 referenced recordings,
  preserved assets, and the complete normal release gate.
- Main TSV, registry, sparse priority, review data and all pre-existing fixtures
  are byte-identical; every repository WAV path and payload matches the original
  unmodified test copy. JSON differs only in `categorySourceSha256`.
- Git diff whitespace checks pass. No commit, push, redirects or Exodus IV work.

## Files changed

- `data/dictionary_categories.tsv`
- `shared/web-ime-core.js`
- `desktop/Hokkien Tangliengim IME Pad.py`
- `tools/dictionary_references.py`
- `tools/build_dictionary_json.py`
- `tools/validate_dictionary_tsv.py`
- `tools/check_entry_references.cjs`
- `tools/check_release.py`
- `tests/test_dictionary_references.py`
- `docs/dictionary-tsv-schema.md`
- `docs/roadmap.md`
- `docs/exodus-iii-reference-migration.md`
- `public/data/hokkien-hanri-dict.json` (rebuilt provenance only)

The same narrow classic/bridge changes are applied to the active Local launcher
at `Hokkien Tangliengim IME Pad GitHub Synced Ver/Hokkien Tangliengim IME Pad.py`.
Its unrelated existing differences are preserved by a three-way patch merge.
The separate legacy backup launcher is untouched.
