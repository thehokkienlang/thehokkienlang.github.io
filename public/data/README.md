# Public Data

`hokkien-hanri-dict.json` is generated from `data/hokkien_hanri_dict.tsv`,
together with two sidecars so browsers only download what they use:

- `hokkien-hanri-dict.json`: entries, categories and metadata. Every app loads it.
- `hokkien-hanri-dict-runtime.json`: audio and Lomari maps. Only the IME and
  translator load it.
- `hokkien-hanri-dict-indexes.json`: lookup indexes for checks. It is never
  published; browsers build their own lookups.

`tools/dictionary_data.py` and `tools/dictionary_data.cjs` reassemble the
complete document for checks.

Rebuild it from the repository root:

```powershell
python tools/build_dictionary_json.py
```

The JSON keeps each permanent Unicode-derived TSV `entry_id` as its source entry `id`, records the adjacent permanent-ID registry hash, and includes raw TSV values, explicit `entryType`, effective readings, structural `kind` labels, and (in the indexes sidecar) lookup indexes for Hanri, Hangul readings, and Lomari. Generated sandhi entries derive their runtime IDs from the source ID but are not TSV rows.
