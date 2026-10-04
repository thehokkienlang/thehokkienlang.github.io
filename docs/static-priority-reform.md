# Pre-Exodus static priority reform

Completed 2026-10-04. No adaptive ranking, commit or push is included.

## Migration results

The original dictionary had 2,745 rows: 2,607 stored priority 1 and 138 stored
another value. Lower numeric values ranked first; source row broke ties. Numeric
costs also affected Hanri polyphonic reading/segmentation. Generated variants
inherited source priority and the existing class/fallback rules.

All 2,745 global numeric cells were removed. Of 77 reading groups with unequal
priority tiers, 23 already followed the desired canonical order without pins.
The remaining 54 groups required 78 explicit pins; 20 Hanri contexts needed one
default-reading/segmentation pin each. Thus the verified reform initially used
98 override rows across 74 contexts. There were zero changed tied-order groups
and zero unexplained differences: existing tied source order happened to agree
with canonical order. No exceptions were manufactured to preserve row ties.

Before the later lexical cleanup, all source IDs, row order, lexical/search
fields, runtime audio/Lomari data and candidate membership were unchanged.
Parity covered 2,239 candidate groups, 3,110 Hanri contexts and 61 Hangul defaults.
Python audio/HTML matched Web for 3,085 plain Hanri contexts. Twenty-five mixed
contexts were checked against each platform's original baseline; 15 pre-existing
Python HTML/audio legacy-format differences were preserved, not silently fixed.

The complete original comparisons are in `static-priority-migration.json`.

## Final architecture

The main TSV header, with tabs between fields, is:

```text
hanri simplified reading mandarin_trad mandarin_simp english corrected entry_type entry_id
```

The sparse exception file `data/dictionary_priority.tsv` has exactly:

```text
lookup_key entry entry_id rank
```

Default source comparison is: entry class (Hangul override, lexical, correction
alias, numeral pronunciation), Task 5c Tangliengim source-reading collation,
canonical headword code points, corrected-reading code points, then permanent
entry_id. Generated variants follow their source identity with existing tone
eligibility; toneless/generated fallbacks retain their existing last-place rule.
Hanri segmentation prefers coverage, fewer segments and longer first segments
before canonical comparison, unless an eligible contextual pin applies.

Within a complete eligible group, each listed source ID occupies its positive
1-based absolute slot. Unlisted entries fill empty slots in default relative
order. Ranks need not be contiguous. Tone filtering preserves the already-ranked
complete group's relative order. Labels are checked against canonical TSV rows;
runtime identity is entry_id. Malformed schema, duplicate pairs, conflicting slots,
out-of-range ranks, inactive/unknown IDs and ineligible references are rejected.
No rank is silently clamped or repaired. Derived canonicalKey/staticRanks/staticOrder
metadata is generated, not a second independently maintained ranking system.

Web consumes Python-generated collation/override metadata. Python consumers reuse
the same ranking module. Source-row diagnostics do not contribute to ordering;
even reading-group traversal and audio lookup ties are deterministic. Reversing
the actual TSV preserves all tested Local candidates, lookup traversal and audio
defaults. Writers emit nine columns and require no priority for a new entry.
Sync TSV also includes the sparse override file when changed.

## Subsequent approved duplicate cleanup

The user then requested removal of Hangul overrides duplicated by v3.1 Hanri.
Eight overrides were removed; `시5` was replaced with lexical `是 / 시5`, assigned
`U+662F_00`. No development redirects/tombstones were created. Other genuine
homophones and local-only grammatical/pronunciation overrides were retained.

The final dictionary has 2,737 rows: 2,666 lexical, 52 Hangul override, nine
correction alias and ten numeral pronunciation. Existing surviving IDs and
lexical/search values are unchanged. The nine old IDs were removed from the
active registry; the four previously inactive reserved IDs remain untouched.
Moving the copula into the lexical class required canonical re-sorting, without
changing the relative order of surviving records.

One obsolete `쉬` pin disappeared, leaving 97 override rows across 73 contexts,
referencing 92 distinct active IDs. This cleanup intentionally changes nine
Python unmarked-Hangul lookup keys. Sixteen derived runtime entries stop inheriting
the removed global `시5` copula override; for example, unmarked `시` in 四-related
readings uses Tone 3, while actual 是 retains Tone 5. No audio files, scheduling,
rates, sandhi algorithms or Lomari algorithms were changed. These data-driven
differences are explicitly recorded in `hangul-override-cleanup.json`.

The final regression fixture was refreshed only after this independent review.
All 13 remaining Mandarin review cases and their decisions are untouched.

## Verification and scope

- TSV/identity/sparse-priority validation: passed; nine-column main TSV.
- Canonical sorter: canonical and byte-idempotent after the approved cleanup.
- Dictionary build: 5,442 runtime entries, 2,727 active source entries.
- Focused dictionary tests: 42 passed.
- Source and built Web behavior, candidate ranking, Simplified/Mandarin lookup,
  ditto inheritance, keyboard composition, tone/sandhi and audio checks: passed.
- Python reversed-source/default checks and selectively merged Local consumers:
  passed; 3,111 Web contexts, 3,086 cross-platform plain Hanri contexts.
- Local HTML/TSV localhost bridge, 16 waveform parity cases and legacy parity:
  passed. The legacy backup and existing Local-only differences are preserved.
- Generated site validates with 1,507 referenced recordings; no source WAV edited.

No Exodus I-IV, N/X research or audio polishing was performed.

## Files changed by this task

- Dictionary data: `data/hokkien_hanri_dict.tsv`,
  `data/dictionary_priority.tsv`, `data/dictionary_entry_id_registry.tsv`,
  `public/data/hokkien-hanri-dict.json`.
- Runtime consumers: `shared/web-ime-core.js`, `apps/dictionary/app.js`,
  `desktop/Hokkien Tangliengim IME Pad.py`, `desktop/hokkien_tone_marker_gui.py`,
  `desktop/tangliengim_web_shell.py`.
- Central schema/build: `tools/dictionary_schema.py`,
  `tools/dictionary_ranking.py`, `tools/tangliengim_collation.py`,
  `tools/build_dictionary_json.py`, `tools/build_site.py`,
  `tools/validate_dictionary_tsv.py`.
- Writers: `tools/assign_dictionary_entry_ids.py`, `tools/enrich_tsv_english.mjs`.
- Verification: `tools/check_dictionary_baseline.cjs`,
  `tools/check_static_ranking.cjs`, `tools/check_static_desktop.py`,
  `tools/check_web_apps.cjs`, `tools/check_desktop_shell.py`,
  `tools/check_site.py`, `tools/check_release.py`.
- Tests/fixtures: `tests/test_dictionary_ranking.py`,
  `tests/test_dictionary_collation.py`, `tests/test_dictionary_simplified.py`,
  `tests/test_dictionary_mandarin.py`, `tests/fixtures/dictionary-baseline.json`,
  `tests/fixtures/static-reading-defaults.json`.
- Documentation: this report, `docs/static-priority-migration.json`,
  `docs/hangul-override-cleanup.json`, `docs/candidate-ranking-model.md`,
  `docs/dictionary-tsv-schema.md`, `docs/roadmap.md`,
  `docs/mandarin-lookup-implementation.md`, `tools/README.md`.
- Active Local folder: selectively merged `Hokkien Tangliengim IME Pad.py`
  and `hokkien_tone_marker_gui.py`. Legacy backup is untouched.

READY FOR EXODUS. Proceed next with Exodus I - adaptive ranking.
