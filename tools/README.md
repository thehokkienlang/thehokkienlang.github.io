# Tools

Build and validation scripts for the dictionary and web IME.

`organize_audio_files.py` groups `public/audio` into initial-consonant folders using the desktop IME's own Lomari/Hangul audio filename mapping.

`build_dictionary_json.py` converts the canonical TSV into shared web JSON.

`sort_dictionary_tsv.py` applies the reusable Tangliengim syllabic collation on demand; `validate_dictionary_tsv.py` reports unsorted rows as a maintenance notice.

`assign_dictionary_entry_ids.py` supports historical six/seven/eight-column inputs and the current nine-column schema. Historical ranking values are not written into the current lexical schema. It preserves Simplified/Mandarin metadata, canonical IDs, and reserved suffixes. Before public release, it does not register old `tlg-...` IDs as redirects and reports no change after migration.

`dictionary_ranking.py` defines the shared canonical comparator and validates/compiles sparse absolute-rank exceptions from `data/dictionary_priority.tsv`. The main dictionary has no ranking fields. New rows automatically use deterministic order; only deliberate contextual exceptions belong in the priority file. `check_static_ranking.cjs` protects Web ranking and all recorded reading defaults. `check_static_desktop.py` exercises real Python readers against those defaults and a physically reversed temporary TSV.

`dictionary_schema.py` defines the canonical column order and resolves source-only `〃` inheritance centrally. `populate_mandarin_lookup.py` performed the conservative semantic Mandarin migration using explicit Hokkien equivalents and CC-CEDICT sense confirmation; `--fill-missing` only fills blank Mandarin metadata. Uncertain rows are listed in `docs/mandarin-lookup-review.md`. Neither metadata field participates in canonical collation or IME ranking.

`complete_mandarin_lookup.py` applies the separately reviewed Wiktionary-led second-pass manifest in `docs/mandarin-second-pass-decisions.json`. It fills blank Mandarin pairs only, guards each decision by permanent ID and original lexical fields, refuses conflicting populated values, and is byte-idempotent. HIGH/MEDIUM decisions are populated; LOW and non-lexical N/A stay blank. This historical migration is not a translator for new rows and does not require live network access. The review report separates optional MEDIUM spot-checks from genuine LOW manual review.

`populate_simplified_lookup.py` performed the one-time Simplified lookup-column migration, keeping all previous cells and row order intact. It refuses to overwrite an existing Simplified column. `simplified_lookup.py` is the shared script-preserving converter used by that migration and the Local writer, backed by the pinned OpenCC subset in `tools/vendor/opencc`.

`migrate_dictionary_entry_ids_zero_based.py` performed the one-time Task 6e shift from `_01` to `_00`. Do not rerun that historical migration. `assign_dictionary_entry_ids.py` and the Local writer allocate `_00` to a new headword and use the next suffix currently recorded in the registry for additional entries.

`build_site.py` regenerates that JSON and builds both interfaces into `_site`.
It versions browser assets by their contents so updates do not reuse stale code.

`check_site.py` checks built routes, shared paths, TSV consistency, and audio files.

`check_web_apps.cjs` checks shared composition, dictionary loading, and sandhi audio selection.

`capture_legacy_parity.py` imports the active desktop reference IME read-only
and captures selected output into a committed parity fixture. See
`docs/shared-engine-migration.md` for the migration boundary and refresh command.
