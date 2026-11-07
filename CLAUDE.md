# TheHokkienLang / Tangliengim — notes for Claude

Website, dictionary, IME and translator for **Tangliengim (TLI, 東寧音)**, a
Hangul-based writing system for **Hokkien**. Published at
https://thehokkienlang.github.io/ from this repository.

## Read this first

- **The Hangul in this project spells Hokkien, not Korean.** Never read,
  romanise, segment, sort or voice it as Korean. Readings follow TLI tones,
  tone sandhi and Lomari, defined by the pronunciation engine in `desktop/`.
- **No linguistic or dictionary-data changes without Haru's manual review.**
  This covers readings, tones, glosses, Hanri choices, orthography, tone marks
  and song or story text. Report suspected problems; don't edit them.
- This checkout (`C:\Users\Asus\Documents\GitHub\thehokkienlang.github.io`) is
  authoritative. `Documents\Tangliengim`, the old `Hokkien Hangul IME` folder
  and the OneDrive `Hokkien Hangul Project` folder are reference only.
- Commit or push only when asked. Pushing to `main` deploys the site.

## Layout

- `apps/` public apps: `content-site/`, `dictionary/`, `ime/`, `search/`, `translate/`
- `content/` pages, guides, songs, stories (EN, `zh-hant/`, `zh-hans/`)
- `data/hokkien_hanri_dict.tsv` the only dictionary source, plus priority,
  category, registry, redirect and defunct TSVs
- `desktop/` Python IME and editors; the GUI-free pronunciation engine is
  `tangliengim_engine.py` (the IME Pad re-exports it); `shared/` browser logic
  and styles. Tone-sandhi tables: `shared/tli-sandhi.json` only (the browser
  mirror in `web-ime-core.js` is test-locked to it).
- `tools/` build and release checks; `tests/` automated tests
- Generated, never edit by hand: `_site/`, `public/data/*.json`

## Dictionary data rules

- The TSVs are UTF-8, NFC and **CRLF**, with 9 columns in a fixed order
  (`docs/dictionary-tsv-schema.md`). Prefer the Dictionary Editor; it validates,
  allocates IDs, sorts and recaptures test baselines when publishing.
- After any TSV edit, run `python tools/sort_dictionary_tsv.py`, then the
  release gate.

## Build and checks (Windows)

```
python -m pip install -r requirements-dev.txt
python -X utf8 tools/check_release.py --source-only
python -X utf8 tools/check_release.py
```

The build uses the GUI-free engine and needs no Tkinter; the full release gate
also runs the desktop IME, which does (the standard Windows installer
includes it). Release checks need Node.js on PATH. A PyInstaller build of the
desktop IME must bundle `tangliengim_engine.py` and `shared/tli-sandhi.json`
beside `hokkien_tone_marker_gui.py`.

## Local editors

`npm run editor` or `Open Website Editor.cmd` opens the editor hub on a
localhost port picked at launch. Local editors are never part of the public
build.
