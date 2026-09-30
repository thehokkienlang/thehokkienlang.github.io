# Public Data

`hokkien-hanri-dict.json` is generated from `data/hokkien_hanri_dict.tsv`.

Rebuild it from the repository root:

```powershell
python tools/build_dictionary_json.py
```

The JSON keeps each permanent Unicode-derived TSV `entry_id` as its source entry `id`, records the adjacent permanent-ID registry hash, and includes raw TSV values, explicit `entryType`, effective readings, structural `kind` labels, and lookup indexes for Hanri, Hangul readings, and Lomari. Generated sandhi entries derive their runtime IDs from the source ID but are not TSV rows.
