# Hokkien Tangliengim

The shared source repository for the Tangliengim dictionary, web IME, desktop IME,
pronunciation data, and audio.

- [Dictionary](https://thehokkienlang.github.io/dictionary/)
- [Web IME Pad](https://thehokkienlang.github.io/ime/)

The root website hosts the English home page. Traditional Chinese pages live at
`/zh-hant/` and Simplified Chinese pages at `/zh-hans/`. Learning pages, literature,
70 songs, the dictionary and IME are built together by one GitHub Pages workflow.
All 13 authored Chinese presentations, including the Traditional Chinese Egg,
have been imported. All original WordPress pages are retained.

## Source layout

```text
apps/dictionary/       Dictionary interface, published at /dictionary/
apps/ime/              Standalone web IME, published at /ime/
apps/content-site/     Shared multilingual shell and local song URL form template
content/               Imported pages, learning guides, and literature
migration/             Original snapshots, link map, media map, and song URL form
shared/                Browser keyboard composer and shared IME controller
data/                  Canonical hokkien_hanri_dict.tsv
public/audio/          Shared recordings grouped by initial consonant
public/data/           Generated dictionary JSON (not edited by hand)
desktop/               Python desktop IME and tone/HTML engine
assets/                Existing site assets and dictionary logo
tools/                 Data builders, validation, and maintenance tools
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

## Build and preview

Use Python 3.10 or later with Tkinter available, and Node.js for validation.
On Ubuntu, install `python3-tk` alongside Python.

```sh
python tools/check_release.py
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000/dictionary/` or `http://localhost:8000/ime/`.
The English home page is at `http://localhost:8000/`.
Preview the built `_site`; the source `apps/` folders are not the public URLs.
No Python source or raw TSV is copied into the published site.

The full release gate validates source/schema, canonical order, IDs/references,
static/adaptive ranking and integration, and rebuilds/checks the site. For portable
source-only CI checks use `python tools/check_release.py --source-only`.
See [the production data contract](docs/dictionary-tsv-schema.md) for the complete
maintenance workflow, and [Exodus IV readiness](docs/exodus-iv-readiness.md) for
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

See [the WordPress migration](docs/wordpress-migration.md) for the imported
scope, language routes, and the three-column song URL form at
`migration/song-url-form.html`. WordPress is not modified by importing or building.

Copyright 2026 Zhen Dong Woo. All rights reserved.
