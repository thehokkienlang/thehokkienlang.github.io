# Handoff from the claude.ai session — 7 Nov 2026

Context for continuing in Claude Code. Delete this file once it has been read.

## What happened

1. An audit of the site at commit `3a2ced5` was written up as a doc:
   https://claude.ai/artifact/TE1xRbc9NtQvpJHZipY9hh
   It has three parts: browsing experience, code structure, and linguistic
   data. Every finding is numbered and comes with a proposed fix.
2. Three code-only fixes were made and delivered as a patch,
   `0001-Run-font-test-in-CI-cache-gate-scripts-fold-tone-mar.patch`:
   - CI installs `requirements-dev.txt` (fontTools, brotli). The font-anchor
     test now fails in CI instead of skipping when they are missing.
   - The Dictionary and Translator lock screens load scripts with
     content-hash versions written by `tools/build_site.py`
     (`version_gate_scripts`), replacing per-visit `Date.now()`.
   - Site search treats `ˋ ˎ \`` / `ˆ ꞈ` / `ˊ ˏ` / `ˉ ˍ` as the same tone
     (`toneMarkFold` in `shared/web-site-search-variants.js`).
   The full release gate passed with these changes. No data or content was
   changed.

## First steps

- Check whether the patch is already applied (`git log -3`). If not, apply it
  on a branch with `git am`.
- Run the release gate (see CLAUDE.md) and confirm it passes on Windows.

## Next candidates (code only; ask Haru before starting)

- **Audit 1.1:** slim the 9.3 MB `public/data/hokkien-hanri-dict.json`. It
  carries a per-entry `raw` copy (1.2 MB), prebuilt `indexes` (1.4 MB) and
  `runtime.rawHangulAudio` (2.6 MB). About ten consumers and several test
  baselines read this format, so plan the change first.
- **Audit 1.3 / 2.5:** compressed audio copies; WAV masters out of git history.
- **Audit 2.1 / 2.2:** move the engine out of the Tk GUI file; keep one
  orthography spec for Python and JS.
- **Audit 1.7, 1.8, 3.10:** alt text, meta/404/sitemap, and replacing
  `lang="ko"` on Hokkien Hangul with `nan` / `nan-Hang`.

## Deferred to Haru's manual review — do not change

Everything in audit section 3: candidate tone fixes (代, 時代, 現代 final 대→대5;
溫 운2→운1; 猶 is a checked syllable, citation possibly Low), compounds 變成,
指引, 窗仔 and 運將, roughly 25 character-by-character glosses (also 交代 and
猶原), the duplicate 下 (U+4E0B_00 / _01), missing literary readings, the
Introduction-page footnote and ㅚ/ㅞ audio, the Rising-tone sandhi note, and
tone-mark code points.
