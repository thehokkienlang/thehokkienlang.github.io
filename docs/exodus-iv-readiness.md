# Exodus IV final consolidation

The authoritative current reference is [the production contract](dictionary-tsv-schema.md).
This report records the Exodus IV audit and verification, not a second schema.
No commit, push, ID freeze, linguistic cleanup or new feature phase is included.

## 1. Prerequisites and actual data

Before any edits, the complete installed release gate passed: sparse static
ranking, Exodus I learning, Exodus II safeguards and Exodus III exact-record
references are present. No missing foundation was concealed by this cleanup.

| Measure | Verified current value |
| --- | ---: |
| Source dictionary records | 2,737 |
| Runtime-active source records | 2,727 |
| Inactive number-pronunciation sources | 10 |
| Generated sandhi views | 2,705 |
| Total generated JSON records | 5,442 |
| Registry assignments | 2,741 (2,737 current plus four reserved) |
| Static priority exceptions | 97 across 73 contexts |
| Explicit category memberships | 178 |
| Repository WAV files | 3,352 |

The ten digit rows have corrected Hangul pronunciations and are consumed by the
number loader, not normal candidates. They remain genuine identified source
rows and inactive objects in JSON. The active/source difference is intentional.

## 2. Final contracts (report items 3-12)

Main TSV header remains exactly:

```text
hanri simplified reading mandarin_trad mandarin_simp english corrected entry_type entry_id
```

- Sources: main TSV owns lexical/search data; sparse priority owns static
  exceptions; the ledger owns allocation; categories own exact memberships.
  Original audio and shared engines remain pronunciation inputs. Generated JSON
  and `_site` are derivative; learned preferences are per-user runtime state.
- Roles: lexical 2,666; hangul_override 52; correction_alias 9;
  number_pronunciation 10. No new type is invented.
- Ditto: simplified inherits hanri; mandarin_trad inherits hanri;
  mandarin_simp inherits resolved mandarin_trad. Blank remains unspecified;
  runtime/search contain resolved strings, never a searchable `〃`.
- Identity: existing Unicode headword plus permanent ordinal, minimum two
  digits, `_00` a real record; no row-derived identity, no renumbering, no URLs
  stored independently. IDs are still pre-release and no public freeze is declared.
- Static order: sparse `lookup_key entry entry_id rank`, positive absolute
  slots in full contexts, checked labels, canonical filling of unspecified slots.
- Adaptive order: normalized context plus source ID; `static_index * 2 - count`,
  cap 255, no decay, explicit eligible selection only, protected class boundaries.
  Browser key and stable per-user Desktop store remain unchanged.
- Structural references: exact IDs for relationships, strings for linguistic
  lookup/display/content. Categories are `category label entry entry_id`; 174
  historical memberships became 178 exact IDs, still food 103/place-names 75.
- Runtime: JSON schema 10, source IDs retained, generated `-sandhi` views
  retain `raw.entry_id`; transient fallbacks get no new permanent IDs.
- Search: Hanri, Hokkien Simplified, Hangul/reading/Lomari, both Mandarin
  scripts and English retrieve existing identified records. Personal candidate
  preference does not alter pronunciation/default reading or search ranking.

## 3. Compatibility audit (report items 13-14)

Removed only unsupported production parsing:

- Headerless positional parsing in Local duplicate/existing-reading helpers.
- Unreachable headerless metadata branches in classic Pad/converter loaders.
- Permissive partial/reordered header acceptance in production builder/ranking
  readers and Python loaders. They use one shared exact-header guard; the named
  record reader rejects missing/extra fields before ranking/build consumption.
- Numeric loading no longer reads an obsolete partial schema; existing numeric
  defaults still handle missing/invalid files without inventing dictionary rows.

Intentionally retained:

- Explicit historical six/seven/eight-column ID import, including old `tlg-...`
  recognition, because supported migration tests/CLI contracts depend on it.
  It does not keep obsolete identifiers active or create unpublished redirects.
- Historical zero-base/Simplified/Mandarin migration tools and fixtures; these
  are opt-in historical tools, not production fallback schemas or translators.
- Existing classic missing/invalid-file diagnostic fallback and numeric defaults.
- Linguistic strings, output deduplication and legacy tone normalization: not
  fragile record identity or obsolete column-layout compatibility.

## 4. Documentation/version/workflow (report items 15-17)

Expanded the existing schema document rather than creating a competing schema.
README/tools guide now point to it and use the full release gate as the normal
workflow. The roadmap records Exodus IV complete. Genesis, static priority,
Simplified and Exodus III reports are clearly historical without changing their
past decisions/counts. The shared-engine history points to the current contract.

Keep dictionary JSON schemaVersion 10 and preference payload version 1: no
generated format changed. The exact central TSV header is its source contract;
no per-row version, priority, N/X, URL or speculative metadata column was added.

Maintenance: edit repository source; preserve IDs; allocate missing new IDs via
the Local writer or explicit allocator; maintain sparse priorities/categories;
sort separately; run the full gate; review the diff before authorized publishing.
Never manually edit generated JSON or sync preference statistics into source.

## 5. Release gate and reproducibility (report items 18-20)

Added a read-only `sort_dictionary_tsv.py --check` to enforce canonical source
order at release time without mutating data. Source-only gate tests rebuilt
source apps, full gate tests built apps once, removing the former duplicate Web
integration pass. Focused validators remain separate but use shared contracts.
Optional deep audio/linguistic/live-device audits are not automatic release repairs.

Both clean staging and final installed gates passed. The clean staging checkout
began without `public/data` JSON; it rebuilt from authoritative source.
Recreated JSON SHA-256 matches the pre-edit generated file exactly:
`2a37aa8158f1729596c85585b2151f377239c950f9a1d2d2ddd7bc459845252f`.
No regression baseline was refreshed. All authoritative data remains byte-identical.

## 6. Remaining work and change inventory (report items 21-22)

Non-blocking: [13 LOW Mandarin review cases](mandarin-lookup-review.md), deferred N/X research and optional
audio polish. None violates the production schema; no linguistic decisions were
made to eliminate them. Public ID freeze and human-readable entry routing are
not silently declared/implemented by completing the architecture.

Files changed in this phase:

- `tools/dictionary_schema.py`, `tools/dictionary_ranking.py`,
  `tools/build_dictionary_json.py`: exact current production header/arity.
- `desktop/Hokkien Tangliengim IME Pad.py`,
  `desktop/hokkien_tone_marker_gui.py`: remove obsolete parser branches.
- `tools/sort_dictionary_tsv.py`, `tools/check_release.py`: read-only order gate,
  one Web integration target per mode.
- `tests/test_dictionary_contract.py`: five focused contract tests.
- `docs/dictionary-tsv-schema.md`, `docs/exodus-iv-readiness.md`,
  `docs/candidate-ranking-model.md`, `docs/roadmap.md`, `README.md`, `tools/README.md`.
- Historical notices in `docs/genesis-3.1-consolidation.md`,
  `docs/static-priority-reform.md`, `docs/simplified-lookup-implementation.md`,
  `docs/exodus-iii-reference-migration.md`, `docs/shared-engine-migration.md`.
- Matching reader-only changes in the active Local Pad/converter copies;
  their unrelated code and the separate legacy backup remain intact.

Main TSV, registry, priority/category files, review data, fixtures, generated JSON,
WAVs and Web UI/logic are unchanged by this phase. Existing dirty Exodus I-III
changes are preserved rather than rewritten/reverted.

## Final verification

- The complete prerequisite gate passed before editing; final full gates passed
  in both the clean isolated source copy and installed checkout.
- 55 Python dictionary tests passed, including five new contract checks;
  historical ID-import/idempotence tests remain supported.
- Existing 2,239-key/5,442-entry baseline passed without refresh. The clean
  rebuilt JSON is byte-identical to the pre-edit output, not just semantically equal.
- 7,151 Web and 6,884 classic cold-start menus, explicit/passive learning,
  persistence/reset, reversed-source ordering and shared adaptive fixtures passed.
- Both Exodus II suites passed: 1,024 monotonic counts, 160 seeded rankings,
  malformed stores, failed/interrupted writes, concurrency, multi-tab refresh,
  exactly-once commit and bridge receipt tests.
- Exact-ID references, all six dictionary search dimensions, Web composition,
  Taipei/Singapore lookup, Desktop shell/HTML/TSV bridge and legacy parity passed.
- 16 PCM waveforms match the reference. Built-site checks passed with 5,442
  runtime entries, 1,507 referenced recordings and preserved assets.
- The installed gate included the actual active Local launcher in record-reference
  checks. A separate read-only comparison of active Local versus repository
  readers matched all 2,248 candidate keys, 2,538 Hanri lookup keys, numeric
  pronunciations, resolved metadata/IDs, writer lookup and source paths.
- All 12 source-data/fixture files and all 3,352 original WAV paths/payloads
  remained byte-identical; source ordering, IDs, translations, types, priorities,
  categories, ranking, Lomari, tone and sandhi behaviour are preserved.
- Git diff whitespace checks passed. No commit/push, baseline update, public
  ID freeze, redirected identity, linguistic migration or audio editing occurred.

EXODUS COMPLETE — NON-BLOCKING ISSUES REMAIN
