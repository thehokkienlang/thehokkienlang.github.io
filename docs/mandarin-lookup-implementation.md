# Mandarin lookup metadata migration

This is a historical metadata-migration report. The later Pre-Exodus reform
removed the lexical `priority` column. See `dictionary-tsv-schema.md` and
`candidate-ranking-model.md` for the current nine-column schema and sparse overrides.

## Headers

Original header (eight tab-separated columns):

```text
reading hanri priority corrected english entry_type entry_id simplified
```

Final header (ten tab-separated columns):

```text
hanri simplified reading mandarin_trad mandarin_simp english corrected entry_type entry_id priority
```

## Initial Population (Historical)

| Metric | Source rows |
| --- | ---: |
| Dictionary records | 2,745 |
| Nonempty `mandarin_trad` | 1,037 |
| Nonempty `mandarin_simp` | 1,037 |
| `〃` in `simplified` | 1,446 |
| `〃` in `mandarin_trad` | 895 |
| `〃` in `mandarin_simp` | 595 |
| Mandarin manual review, left blank | 1,698 |
| Input-only numeral rows, not applicable | 10 |

These are initial-migration counts, not a rule requiring every future entry to have
Mandarin metadata. The original review list was superseded by the second pass
described below; it is not the current list of unresolved entries.

Population combines explicit Hokkien semantic equivalents with conservative
CC-CEDICT confirmation of shared written words. Every existing English sense must
match a complete reference sense or one of its explicitly separated synonyms.
No character-by-character translation or arbitrary English reverse-dictionary
choice is used. The reference comparison removes parenthetical annotations,
English articles/infinitive markers and hyphen-spacing differences; it does not
guess unconfirmed meanings. For instance, `家己` has Mandarin `自己`, `目滓` has
`眼淚 / 眼泪`, and `家後` has `妻子`.

Existing source glosses sometimes appear to list meanings of component characters
instead of a compound, e.g. `公里 = male`, `結局 = tie; knot`, and
`機會 = machine; opportunity; can; meeting`. These initially remained blank in
Mandarin pending review. Specialised, ambiguous and missing meanings were also
listed. A failed conservative reference match is a review item, not proof that a
headword is invalid. The list can therefore include straightforward words whose
English phrasing differs from the reference.

Reference: [CC-CEDICT distributed by MDBG](https://www.mdbg.net/chinese/dictionary?page=cc-cedict),
accessed 2026-10-04, CC BY-SA 4.0. The external archive is not bundled or needed
at runtime. Mandarin Simplified is converted from the semantic Traditional value
with the existing pinned OpenCC `t2s` dictionaries. Hokkien Simplified remains its
separate, previously reviewed value.

## Second-Pass Completion

The first-pass all-English-senses match was too conservative and is not the
second-pass rule. Wiktionary was the primary external lexical reference, checked
through public MediaWiki revisions for all 1,594 unique unresolved Hanri-only
expressions (1,392 available pages and 202 missing pages). Mandarin and Min-only
etymology/pronunciation blocks were assessed separately. One compatible relevant
Mandarin sense is sufficient; exact English wording, unrelated secondary senses,
regional/literary register and missing reference coverage do not block a clear
correspondence.

| Second-pass metric | Rows |
| --- | ---: |
| Previously blank rows examined | 1,708 |
| Newly populated Mandarin pairs | 1,685 |
| New Traditional `〃` | 1,190 |
| New explicit Traditional equivalents | 495 |
| New Simplified `〃` | 835 |
| New explicit Simplified equivalents | 850 |
| HIGH, automatically populated | 750 |
| MEDIUM, populated with optional spot-check | 935 |
| LOW, genuine manual review remaining | 13 |
| Input-only numerals, not applicable | 10 |
| Total nonempty Mandarin pairs after completion | 2,722 |
| Total Hokkien `simplified` `〃` (unchanged) | 1,446 |
| Total Mandarin Traditional `〃` | 2,085 |
| Total Mandarin Simplified `〃` | 1,430 |
| User-authorized English corrections, including completed manual reviews | 85 |

Examples: `計較` stores `〃 / 计较`; `繼續` stores `〃 / 继续`.
Different lexical correspondences include `鎖匙 → 鑰匙 / 钥匙`,
`頭路 → 工作 / 〃`, `舊年 → 去年 / 〃`, and `生理 → 生意; 生計 / 生意; 生计`.
`捌` in its know/recognise sense is not Mandarin's financial numeral eight;
it receives `知道; 認識`. Existing first-pass `家己 → 自己` is untouched.

The user subsequently authorized correction of obvious English errors. The 27
initial corrections are recorded with exact old/new values, readings and source
references in [english-gloss-corrections.json](english-gloss-corrections.json).
Examples include `公里: male -> kilometre`, `古錐: ancient/awl -> cute; adorable`,
and `結局: tie; knot -> outcome; ending`. Whole-word Hokkien senses were checked,
not inferred by concatenating character glosses: `冤家` in its `oan-ke` reading
means quarrel, not Mandarin enemy/sweetheart. These corrections resolved 20 more
formerly LOW Mandarin rows; already populated Mandarin values were preserved.

The user then edited the exported 73-row manual-review TSV and authorized merging
fully corrected rows and removing them from that sheet. Sixty rows were completed
and merged by existing `entry_id`; the sheet now contains only 13 unresolved rows.
This incorporated 58 additional English updates (including the user's corrections),
bringing the English audit to 85 rows. Mandarin Simplified was derived with pinned
OpenCC; exact inheritance uses `〃`, not repeated strings. Structural fields and
Hokkien simplified were not changed. The exact pre/user/post semantic values,
reasons and sources are recorded in
[mandarin-manual-review-completion.json](mandarin-manual-review-completion.json).

Important corrections included `揞腰 -> 彎腰` (bend over, not hands on hips) and
`芡芳 -> 爆香` (fry aromatics, not thicken with starch). User clarification that
`蟮` is not a standalone gecko word was preserved: it stays unresolved, with no
gecko/壁虎 gloss merged. Any future expansion to `蟮蟲` requires a separate
canonical-headword/identity decision. Original user edits and pre-merge data were
preserved in a local snapshot before the review sheet was reduced.

Uncertain rows are now only LOW cases, such as the bound component `蟮`,
the unclear whole-word sense of `人願`, and the referent of `北陰酆都`.
`金金` and `尖頭또디ˆ` were resolved during manual completion. MEDIUM entries are
already populated and listed separately for optional review. All four categories,
English context, confidence notes, source URLs and revision IDs appear in
[mandarin-lookup-review.md](mandarin-lookup-review.md).

[mandarin-second-pass-decisions.json](mandarin-second-pass-decisions.json) freezes
the reviewed decisions by existing ID and lexical source fields.
`tools/complete_mandarin_lookup.py` applies those decisions only to blank Mandarin
metadata, refuses source changes/conflicting populated values, preserves every
other source cell and comment position, and supports byte-identical reruns. It
is a one-time migration, not a general Hanri-copying rule or network dependency.
The existing central resolver, builder, Web search and Local/Desktop loaders
needed no further production changes for this completion.

## Implementation boundaries

- `tools/dictionary_schema.py`: one canonical header and central inheritance resolver.
- `tools/build_dictionary_json.py`: schema 9, resolved runtime/raw strings and Mandarin indexes pointing to existing IDs.
- `apps/dictionary/app.js`: Traditional/Simplified Mandarin search fields, without new entries or IME candidate rules.
- `desktop/Hokkien Tangliengim IME Pad.py` and `desktop/hokkien_tone_marker_gui.py`: resolve inheritance on load; the writer uses named fields, emits ten columns and leaves new semantic fields blank.
- The separate active GitHub Synced Ver Pad/converter receive only corresponding loader/writer changes; the legacy backup is untouched.
- Validator, sorter, ID assignment/migration tooling and historical enrichment writers use named fields/current headers.
- The sorter retains its original seven-field tie-break digest and excludes lookup metadata.
- Focused tests and the baseline checker cover inheritance, blank distinction, identity, searches and additive metadata changes.

## Preservation and verification

All 2,745 data rows remain in their original physical order. Comment positions,
every `entry_id`, `entry_type`, `hanri`, reading, correction and priority are
unchanged. English changed only for the 85 individually recorded user-authorized
corrections; all other English cells remain exact. The ID registry is byte-identical
to the starting version.
All 1,228 genuinely differing Hokkien Simplified values are unchanged; the other
1,446 Hanri-containing rows now use `〃` instead of duplicate text. Non-Hanri rows
keep blank Hokkien Simplified fields.

The baseline checker compares the pre-migration generated JSON before accepting
the new metadata snapshot: lexical and identity hashes, all existing non-Mandarin
indexes, 2,239 candidate keys and visible menu lists, categories, counts, skipped
rows and the entire audio/Lomari/sandhi runtime must match. Only additive Mandarin
indexes/metadata and source schema/checksum change. During the second pass,
previously indexed Mandarin IDs must also remain in their existing relative order,
and previously populated Mandarin strings and all Hokkien Simplified strings
must remain exact. The metadata baseline is captured only after those comparisons
pass, not to mask candidate or runtime regressions. For the explicitly approved
English corrections, the expected pre-pass JSON was derived from the untouched
starting snapshot by changing only `english`, `raw.english` and `englishKey` for
the 27 audited source IDs (54 citation/auto-sandhi records). All remaining lexical
fields, indexes, identity, audio/runtime and candidate order are still compared
strictly. No unrelated baseline differences are accepted.

The manual merge was separately compared against the immediately preceding
generated JSON, with only the newly audited English values and derived search keys
changed in the expected reference. Every existing populated Mandarin value/index
and all other lexical/runtime data and candidate sequences remained protected.

No legacy-priority migration, Exodus work, new IDs, commit or push is part of this task.

Verification completed: UTF-8/NFC/CRLF and ten-field TSV validation; focused
schema/collation/identity/inheritance tests; successful shared JSON/site builds;
unchanged pre/post candidate and runtime snapshots; Traditional/Simplified Mandarin
search in the source and published Web application harnesses; Desktop bridge
loading/writing; direct loading of the separate active Local Pad/converter;
audio waveform parity; desktop legacy parity; and the complete release gate.
Population is byte-idempotent, and Git whitespace checks pass. These are automated
runtime/DOM-harness checks, not a claim of manual device-by-device UI testing.

## Second-Pass Changed Files

```text
data/hokkien_hanri_dict.tsv
docs/mandarin-lookup-review.md
docs/mandarin-lookup-implementation.md
docs/mandarin-second-pass-decisions.json
docs/english-gloss-corrections.json
docs/mandarin-manual-review-completion.json
tools/complete_mandarin_lookup.py
tools/check_dictionary_baseline.cjs
tools/check_web_apps.cjs
tools/README.md
tests/test_dictionary_mandarin.py
tests/fixtures/dictionary-baseline.json
public/data/hokkien-hanri-dict.json (generated)
```

The ignored `_site` build is also regenerated. No Local source or audio files
are modified in the second pass; the active Local consumers already read the
repository TSV. The earlier schema-migration changes listed below are preserved.

## Initial Schema-Migration Changed Files

```text
apps/dictionary/app.js
data/hokkien_hanri_dict.tsv
desktop/Hokkien Tangliengim IME Pad.py
desktop/hokkien_tone_marker_gui.py
docs/dictionary-tsv-schema.md
docs/mandarin-lookup-implementation.md
docs/mandarin-lookup-review.md
public/data/hokkien-hanri-dict.json
tests/fixtures/dictionary-baseline.json
tests/test_dictionary_collation.py
tests/test_dictionary_mandarin.py
tests/test_dictionary_simplified.py
tools/README.md
tools/assign_dictionary_entry_ids.py
tools/build_dictionary_json.py
tools/check_desktop_shell.py
tools/check_dictionary_baseline.cjs
tools/check_site.py
tools/check_web_apps.cjs
tools/dictionary_schema.py
tools/enrich_tsv_english.mjs
tools/migrate_dictionary_entry_ids_zero_based.py
tools/populate_mandarin_lookup.py
tools/populate_simplified_lookup.py
tools/sort_dictionary_tsv.py
tools/tangliengim_collation.py
tools/validate_dictionary_tsv.py
```

Outside the repository, the two corresponding files in
`C:\Users\Asus\Documents\Hokkien Programs\Hokkien Hangul IME\Hokkien Tangliengim IME Pad GitHub Synced Ver`
are updated without replacing unrelated local code or creating another TSV copy.
