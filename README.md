# Tangliengim (TLI, 東寧音)

Source repository for [thehokkienlang.github.io](https://thehokkienlang.github.io/),
the home of **Tangliengim**, a Hangul-based writing system for **Hokkien**. The
Hangul here spells Hokkien, not Korean: readings follow TLI tones, tone sandhi and
Lomari romanisation.

## What is here

- **Dictionary** (invite only): about 2,900 entries with Hanri (漢字 and Hangul mixed script), Hangul readings, Lomari, English and Mandarin glosses, categories and audio.
- **[Web IME Pad](https://thehokkienlang.github.io/ime/)**: type Hokkien in TLI Hangul in the browser. A **Translator** preview (invite only) builds on the same data.
- **Learning guides**: introduction, romanisation, spelling and tone sandhi.
- **[Songs](https://thehokkienlang.github.io/songs/)**: 81 songs with synced, followable lyrics, Hanri-Hangul, Lomari and translations, plus stories (The Egg) and literature.
- **[Site search](https://thehokkienlang.github.io/search/)** across the dictionary, songs and pages, with one shared search box.
- **Desktop IME and local editors** (dictionary, website, song) for maintainers; never part of the public site.
- **[TLI Keyboard for Android](android/README.md)**: a system keyboard that reuses the website's IME code.

The site is published in English at the root, Traditional Chinese at `/zh-hant/` and
Simplified Chinese at `/zh-hans/`, all built together by one GitHub Pages workflow.
The original WordPress pages are retained.

## Source layout

```text
apps/dictionary/       Dictionary interface, published at /dictionary/
apps/ime/              Standalone web IME, published at /ime/
apps/translate/        Translator preview, published at /translate/
apps/search/           Site search page and styles
apps/content-site/     Shared multilingual shell, site CSS/JS and page template
content/               Pages, guides, songs, stories and literature (EN, zh-hant, zh-hans)
android/               TLI Keyboard for Android (not part of the site build)
migration/             Original snapshots, link map, media map, and song URL form
shared/                Browser keyboard composer, search box and shared IME controller
data/                  Canonical hokkien_hanri_dict.tsv and its priority, category and registry files
public/audio/          Shared recordings grouped by initial consonant
public/data/           Generated dictionary JSON (not edited by hand)
desktop/               Python desktop IME, tone/HTML engine and local editors
assets/                Site assets, fonts and dictionary logo
docs/                  Current references; finished work is in docs/history/
tools/                 Data builders, validation, and maintenance tools
tests/                 Automated tests
```

Both web interfaces use `/shared/`, `/public/data/`, and `/public/audio/`.
The browser composer mirrors the desktop IME's input rules, while the web data
builder uses the desktop pronunciation engine as the source of truth for Lomari,
raw Hangul audio, and Taipei/Singapore audio metadata.

## Edit dictionary entries

Edit `data/hokkien_hanri_dict.tsv` in this repository, locally or on GitHub.
Every deployment regenerates JSON from that TSV, the desktop engine, and audio.
The active Local IME reads and saves new readings directly in this same repository TSV and its ID registry. Its Sync TSV button publishes repository changes; no separate Local IME dictionary copy is maintained. Manual TSV edits still require rebuilding generated JSON before the shared web interface reflects them.
Each row has an explicit `entry_type` and a pre-release Unicode-derived `entry_id`; see [the TSV schema](docs/dictionary-tsv-schema.md).
Do not edit generated JSON or maintain a second TSV in the archived dictionary
repository. Historical local desktop installations are separate from this checkout.

## Dictionary Editor

Open **Dictionary editor** in the Local IME toolbar, or launch it directly:

```sh
python "desktop/Tangliengim Dictionary Editor.py"
```

The local editor provides searchable entries, a Hangul-enabled entry form,
English/Mandarin fields, categories, pronunciation preview and editable batch
paste. **Save locally** validates, allocates IDs and sorts automatically.
**Publish updates** reconciles GitHub changes by entry ID, runs the release
checks, and publishes a data-only commit. Conflicting fields require a choice;
failed publishing leaves saved local entries intact. The editor is served only
by the desktop localhost server and is never copied into the public website.

See [editor workflow and recovery](docs/dictionary-editor.md).

## Local Website and Song Editors

Launch the private localhost CMS from the repository root:

```sh
npm run editor
```

Windows users without npm on `PATH` can double-click `Open Website Editor.cmd`,
or run `python "desktop/Tangliengim Website Editor.py"`.

It edits canonical website pages and dictionary data, and opens the structured
[Song Editor](docs/song-editor.md) for lyrics, timing and readings, previews page HTML with
the website's real styles, runs the existing build and validation tools, shows
readable Git diffs, and keeps Save, Commit, and Push as separate actions. It
binds to localhost and is not included in the public site build. See the
[website editor guide](docs/website-editor.md).

## Build and preview

Use Python 3.10 or later and Node.js for validation. The site build uses the
GUI-free pronunciation engine (`desktop/tangliengim_engine.py`) and needs no
Tkinter; the full release gate also exercises the desktop IME, so install
Tkinter for it (on Ubuntu, `python3-tk`). Tone-sandhi tables live once, in
`shared/tli-sandhi.json`.

```sh
python -X utf8 tools/check_release.py
python -m http.server 8000 --directory _site
```

The English home page is at `http://localhost:8000/`; the apps are under
`/dictionary/`, `/ime/` and `/translate/`.
Preview the built `_site`; the source `apps/` folders are not the public URLs.
No Python source or raw TSV is copied into the published site.

The full release gate validates source/schema, canonical order, IDs/references,
static/adaptive ranking and integration, and rebuilds/checks the site. For portable
source-only CI checks use `python tools/check_release.py --source-only`.
See [the production data contract](docs/dictionary-tsv-schema.md) for the complete
maintenance workflow, and [Exodus IV readiness](docs/history/exodus-iv-readiness.md) for
the final consolidation audit. Generated JSON and personal preference files are
not independent dictionary sources.

The desktop application can be launched from this checkout with:

```sh
python "desktop/Hokkien Tangliengim IME Pad.py"
```

It opens the same Web IME code from `apps/ime/` and `shared/` in a desktop app
window. HTML export modes and guarded TSV syncing are added to that interface
only while it is running as the desktop shell; they are not published on the
website. Use `--classic-ui` to open the complete legacy-style interface as a
fallback.

## Branches and releases

`main` is the production branch. Use short-lived task branches such as
`web/ime-mobile-input`, `desktop/html-export`, or `data/english-glosses`, then merge
and delete them. Pull requests run the same build and checks without deployment.
Use tags such as `desktop-v1.3.0` for desktop releases.

The former `thehokkienlang/dictionary` repository is retained as a historical
archive. Its history was merged here; active edits and publishing happen here.
Existing root-site assets are preserved at their original `/assets/` paths.

See [the WordPress migration](docs/history/wordpress-migration.md) for the imported
scope, language routes, and the three-column song URL form at
`migration/song-url-form.html`. WordPress is not modified by importing or building.

Copyright 2026 Zhen Dong Woo. All rights reserved.
