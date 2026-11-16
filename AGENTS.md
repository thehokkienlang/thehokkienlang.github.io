# TheHokkienLang / Tangliengim: instructions for agents

This is the one instruction file for every agent working in this repository.
Codex reads it directly. Claude Code reads it through `CLAUDE.md`, which imports
it. Put new rules here, never in `CLAUDE.md`.

This repository holds the website, dictionary, IME and translator for
**Tangliengim (TLI, 東寧音)**, a Hangul-based writing system for **Hokkien**. It
is published at https://thehokkienlang.github.io/.

## Read this first

- **The Hangul in this project spells Hokkien, not Korean.** Never read,
  romanise, segment, sort or voice it as Korean. Readings follow TLI tones,
  tone sandhi and Lomari, defined by the pronunciation engine in `desktop/`.
- **No linguistic or dictionary-data changes without Haru's manual review.**
  This covers readings, tones, glosses, Hanri choices, orthography, tone marks
  and song or story text. Report suspected problems; don't edit them.
- This checkout (`C:\Users\Asus\Documents\GitHub\thehokkienlang.github.io`) is
  authoritative. These folders are reference only:
  - `Documents\Tangliengim`
  - the old `Hokkien Hangul IME` folder
  - the OneDrive `Hokkien Hangul Project` folder
- Commit or push only when asked. Pushing to `main` deploys the site.

## Push descriptions

When describing a push, preserve song titles exactly as written in the
repository. Never replace them with Pinyin or literal English translations.

## Layout

- `apps/`: public apps (`content-site/`, `dictionary/`, `ime/`, `search/`,
  `translate/`).
- `content/`: pages, guides, songs and stories (EN, `zh-hant/`, `zh-hans/`).
- `data/hokkien_hanri_dict.tsv`: the only dictionary source. Beside it are the
  priority, category, registry, redirect and defunct TSVs.
- `desktop/`: the Python IME and editors.
  - The GUI-free pronunciation engine is `tangliengim_engine.py`; the IME Pad
    re-exports it.
  - Tone-sandhi tables live in `shared/tli-sandhi.json` only. The browser copy
    in `web-ime-core.js` is test-locked to it.
- `shared/`: browser logic and styles.
- `tools/`: build and release checks. `tests/`: automated tests.
- Generated, never edit by hand: `_site/`, `public/data/*.json`.

## Build and checks (Windows)

```
python -m pip install -r requirements-dev.txt
python -X utf8 tools/check_release.py --source-only
python -X utf8 tools/check_release.py
```

- The build uses the GUI-free engine and needs no Tkinter.
- The full release gate also runs the desktop IME, which needs Tkinter. The
  standard Windows Python installer includes it.
- Release checks need Node.js on PATH.
- A PyInstaller build of the desktop IME must bundle `tangliengim_engine.py` and
  `shared/tli-sandhi.json` beside `hokkien_tone_marker_gui.py`.

## Release gate routine

GitHub is the full release gate: `.github/workflows/pages.yml` runs every check
before it deploys, and nothing is published unless they all pass. Locally, run
only what the change can affect, then push and let GitHub run the rest. (Haru's
decision, 2026-11-16: option B in `docs/release-gate-optimisation-plan.md`.)

- **Dictionary changes** (TSVs, dictionary tools, `public/data/`): always run
  the full source gate locally, following the Dictionary Update SOP below.
- **Documentation only** (`docs/`, `README.md`, `AGENTS.md`, `CLAUDE.md`): no
  checks are needed.
- **Everything else:** run `python -X utf8 tools/check_release.py --changed --quiet`.
  It lists the changed files (staged, unstaged, untracked, and commits not yet
  on `origin/main`), runs only the sections they can affect, and falls back to
  the full gate for any path it doesn't recognise. `--quiet` prints one line
  per passing section and the full output of a failing one.
- After a failure, fix it, then restart at the failed section with
  `--from "<section label>"` (an unknown label lists the valid ones).
- Other flags: `--serial` (one section at a time, for debugging), `--jobs N`,
  and `--no-cache` on `tools/compressed_audio.py` to decode every copy again.
- Run long checks in the background with their output in a file. Read only the
  result line, or the failing section if there is one.
- Never rerun a check that passed when nothing has changed since.
- After pushing, check the workflow run once (for example `gh run watch`).
  Don't poll it repeatedly. If it fails, fix the commit forward; never
  republish the same failing commit without diagnosis.

## Dictionary data rules

- The TSVs are UTF-8, NFC and **CRLF**, with 9 columns in a fixed order
  (`docs/dictionary-tsv-schema.md`).
- Prefer the Dictionary Editor. It validates rows, allocates IDs, sorts, and
  recaptures test baselines when publishing.
- After any TSV edit, run `python tools/sort_dictionary_tsv.py`, then the
  release gate.

## Dictionary Update SOP

Follow this procedure whenever a task changes `data/hokkien_hanri_dict.tsv` or
any related dictionary identity, ranking, category, redirect or registry file.
Do not commit or push a partial dictionary update.

1. **Inspect before changing anything.** Run `git status --short` and preserve
   all unrelated user or agent work. Confirm which dictionary rows and stable
   IDs are meant to change.
2. **Wait for local editor saves.** If the Dictionary Editor has an active
   refresh job, wait for it to finish before rebuilding or staging files.
3. **Validate source structure and ordering.** Run:
   - `python -X utf8 tools/validate_dictionary_tsv.py`
   - `python -X utf8 tools/sort_dictionary_tsv.py --check`
4. **Rebuild generated dictionary data.** Run
   `python -X utf8 tools/build_dictionary_json.py`. Include every changed
   generated dictionary file required by Git.
5. **Review semantic changes before capturing expectations.** Check:
   - entry counts and IDs
   - candidate order and lookup metadata
   - generated or runtime audio changes

   Do not update snapshots merely to silence a failure.
6. **Update all three reviewed expectations when the lexical change is
   intentional.** After reviewing the generated diff, run:
   - `node tools/check_dictionary_baseline.cjs --capture`
   - `node tools/check_adaptive_ranking.cjs --capture-static`
   - `python -X utf8 tools/check_adaptive_desktop.py --capture-static`

   These snapshots protect, in order: dictionary semantics, Web cold-start
   menus, and Local/Desktop cold-start menus. Updating only one or two of them
   commonly causes deployment failure.
7. **Run the exact GitHub source gate to completion.** Run
   `python -X utf8 tools/check_release.py --source-only`. Do not stop after the
   first successful section. Repair every reported stale generated file or
   expectation, then rerun the whole command until it exits successfully.
8. **Perform final Git checks.** Run `git diff --check` and
   `git status --short`. Verify that the TSV, registry, generated JSON and
   sidecars, and reviewed fixtures agree, and that no unintended IDs or rows
   changed.
9. **Stage project files, not local agent metadata.** Never commit any of
   these:
   - `.claude/`
   - nested agent worktrees
   - temporary launch configurations
   - caches and build scratch directories
   - machine-specific absolute paths

   Include project edits made by any collaborating agent.
10. **Commit, push and verify the deployment.** Push the current branch and
    check the GitHub Pages workflow. If the deployment fails, fix the actual
    failing expectation or generated artifact.

### Baseline rule

After an intentional dictionary edit, an expectation failure usually means the
generated dictionary or one of the three reviewed snapshots is stale. It does
**not** mean the check should be removed or weakened. Capture a new
expectation only after confirming that the observed lexical, identity and
candidate-order changes are intended.

## Local editors

- `npm run editor` or `Open Website Editor.cmd` opens the editor hub on a
  localhost port picked at launch.
- Local editors are never part of the public build.
