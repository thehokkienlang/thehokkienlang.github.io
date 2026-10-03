# Simplified lookup implementation

## Results

| Measure | Rows |
| --- | ---: |
| TSV data rows | 2745 |
| Hanri-containing rows populated | 2674 |
| Pure Hangul rows left empty | 61 |
| Other non-Hanri rows left empty (number pronunciations) | 10 |
| Simplified differs from canonical headword | 1228 |
| Simplified identical to canonical headword | 1446 |
| Rows flagged for review | 0 |

The complete review list, including IDs, choices, alternatives and reasons, is in [simplified-lookup-review.md](simplified-lookup-review.md).

At the user's request, all 45 initial flags were removed: 38 unlikely secondary glyph alternatives and seven Traditional 著 alternatives to Simplified 着. Populated TSV values are unchanged.

After subsequent manual edits, the former `갛` override is a lexical `佮` entry (`U+4F6E_00`), with `佮` lookup metadata. Its registry record and canonical sort position were updated without redirects for the unpublished ID. Five manually supplied Simplified spellings using `𰑟` were preserved. Counts above reflect these edits; initial-migration invariants below describe the original column-addition pass.

## Files Changed For This Task

- `data/hokkien_hanri_dict.tsv`
- `apps/dictionary/app.js`
- `shared/web-ime-core.js` (exports the existing inline-tone stripping helper)
- `desktop/Hokkien Tangliengim IME Pad.py`
- `desktop/hokkien_tone_marker_gui.py`
- `tools/dictionary_schema.py`
- `tools/validate_dictionary_tsv.py`
- `tools/tangliengim_collation.py`
- `tools/assign_dictionary_entry_ids.py`
- `tools/build_dictionary_json.py`
- `tools/simplified_lookup.py` (new)
- `tools/populate_simplified_lookup.py` (new)
- `tools/vendor/opencc/` (pinned conversion code, dictionaries, configuration, license and provenance)
- `tools/check_desktop_shell.py`
- `tools/check_site.py`
- `tools/check_web_apps.cjs`
- `tests/test_dictionary_simplified.py` (new)
- `tests/test_dictionary_collation.py`
- `tests/fixtures/dictionary-baseline.json`
- `docs/dictionary-tsv-schema.md`
- `docs/simplified-lookup-review.md` (new)
- `docs/simplified-lookup-implementation.md` (this report)
- `tools/README.md`

Generated outputs rebuilt: `public/data/hokkien-hanri-dict.json` and the published-site build output. These are generated files, not additional dictionary sources.

The active external Local IME's `Hokkien Tangliengim IME Pad.py` and `hokkien_tone_marker_gui.py` were also updated in:

`C:/Users/Asus/Documents/Hokkien Programs/Hokkien Hangul IME/Hokkien Tangliengim IME Pad GitHub Synced Ver/`

The legacy backup was not modified. Existing unrelated working-tree changes were preserved. The ID registry was not changed by this task.

## Verification

- TSV validation: 2748 data rows, eight fields, unique IDs, UTF-8/NFC and CRLF.
- All original seven TSV field values, comment rows and row order match the pre-task snapshot exactly; registry bytes also match.
- All 5464 generated entries retain their previous data after excluding the added Simplified metadata. All previous indexes are unchanged.
- All 2240 candidate-order keys and visible-menu snapshots remain unchanged. Only the new lookup index changes the baseline's JSON-section hash; source provenance updates accordingly.
- 23 Python tests passed, including Simplified conversion, mixed-script preservation, rare Hanri, validation and sort independence.
- Source and built Web integration checks passed, including Simplified lookup to the same canonical entry ID.
- Actual external Local IME citation/sandhi loaders, HTML reading loader and temporary-file new-row writer passed.
- Desktop bridge, 16 audio waveform parity cases, legacy parity and published-site validation passed.
- Full release gate passed.

No physical Android/iOS device testing was performed; this task does not alter mobile composition.

No commit or push was made. No Exodus tasks were implemented.
