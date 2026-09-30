# Tools

Build and validation scripts for the dictionary and web IME.

`organize_audio_files.py` groups `public/audio` into initial-consonant folders using the desktop IME's own Lomari/Hangul audio filename mapping.

`build_dictionary_json.py` converts the canonical TSV into shared web JSON.

`sort_dictionary_tsv.py` applies the reusable Tangliengim syllabic collation on demand; `validate_dictionary_tsv.py` reports unsorted rows as a maintenance notice.

`assign_dictionary_entry_ids.py` performs the six/seven-column migration to Unicode-derived IDs. Before public release, it does not register old `tlg-...` IDs as redirects and reports no change after migration.

`migrate_dictionary_entry_ids_zero_based.py` performed the one-time Task 6e shift from `_01` to `_00`. Do not rerun that historical migration. `assign_dictionary_entry_ids.py` and the Local writer allocate `_00` to a new headword and use the next suffix currently recorded in the registry for additional entries.

`build_site.py` regenerates that JSON and builds both interfaces into `_site`.
It versions browser assets by their contents so updates do not reuse stale code.

`check_site.py` checks built routes, shared paths, TSV consistency, and audio files.

`check_web_apps.cjs` checks shared composition, dictionary loading, and sandhi audio selection.

`capture_legacy_parity.py` imports the active desktop reference IME read-only
and captures selected output into a committed parity fixture. See
`docs/shared-engine-migration.md` for the migration boundary and refresh command.
