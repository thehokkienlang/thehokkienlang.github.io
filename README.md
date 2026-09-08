# Hokkien Tangliengim

The shared source repository for the Tangliengim dictionary, web IME, desktop IME,
pronunciation data, and audio.

- [Dictionary](https://thehokkienlang.github.io/dictionary/)
- [Web IME Pad](https://thehokkienlang.github.io/ime/)

The root website redirects to the dictionary. Both interfaces are built and
published together by one GitHub Pages workflow.

## Source layout

```text
apps/dictionary/       Dictionary interface, published at /dictionary/
apps/ime/              Standalone web IME, published at /ime/
shared/                Browser keyboard composer and shared IME controller
data/                  Canonical hokkien_hanri_dict.tsv
public/audio/          Shared recordings grouped by initial consonant
public/data/           Generated dictionary JSON (not edited by hand)
desktop/               Python desktop IME and tone/HTML engine
assets/                Existing site assets and dictionary logo
tools/                 Data builders, validation, and maintenance tools
```

Both web interfaces use `/shared/`, `/public/data/`, and `/public/audio/`.
Desktop Python and browser JavaScript remain separate implementations; the web
dictionary exporter uses the desktop pronunciation engine for Lomari and audio
metadata, including Taipei and Singapore sandhi.

## Edit dictionary entries

Edit `data/hokkien_hanri_dict.tsv` in this repository, locally or on GitHub.
Every deployment regenerates JSON from that TSV, the desktop engine, and audio.
Do not edit generated JSON or maintain a second TSV in the archived dictionary
repository. Historical local desktop installations are separate from this checkout.

## Build and preview

Use Python 3.10 or later with Tkinter available, and Node.js for validation.
On Ubuntu, install `python3-tk` alongside Python.

```sh
python tools/build_site.py
python tools/check_site.py
node tools/check_web_apps.cjs
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000/dictionary/` or `http://localhost:8000/ime/`.
Preview the built `_site`; the source `apps/` folders are not the public URLs.
No Python source or raw TSV is copied into the published site.

The desktop application can be launched from this checkout with:

```sh
python "desktop/Hokkien Tangliengim IME Pad.py"
```

## Branches and releases

`main` is the production branch. Use short-lived task branches such as
`web/ime-mobile-input`, `desktop/html-export`, or `data/english-glosses`, then merge
and delete them. Pull requests run the same build and checks without deployment.
Use tags such as `desktop-v1.3.0` for desktop releases.

The former `thehokkienlang/dictionary` repository is retained as a historical
archive. Its history was merged here; active edits and publishing happen here.
Existing root-site assets are preserved at their original `/assets/` paths.

Copyright 2026 Zhen Dong Woo. All rights reserved.
