# Tools

Build and validation scripts for the dictionary and web IME.

`organize_audio_files.py` groups `public/audio` into initial-consonant folders using the desktop IME's own Lomari/Hangul audio filename mapping.

`build_dictionary_json.py` converts the canonical TSV into shared web JSON.

`build_site.py` regenerates that JSON and builds both interfaces into `_site`.
It versions browser assets by their contents so updates do not reuse stale code.

`check_site.py` checks built routes, shared paths, TSV consistency, and audio files.

`check_web_apps.cjs` checks shared composition, dictionary loading, and sandhi audio selection.
