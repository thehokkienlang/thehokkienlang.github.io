# Release gate: how it works, and a plan to make it cheaper

Status: approved by Haru (2026-11-16), ready to implement. Steps 5 and 7 are
already done; steps 1 to 4 and 6 remain. Nothing here weakens a check: every
check that runs today still runs before a deploy. The plan only changes *when*,
*where* and *how noisily* checks run.

## For the implementer

- Read `AGENTS.md` first. Its rules apply, including: no linguistic or
  dictionary changes, never commit `.claude/`, and push only when Haru asks.
- Do steps 1, 2, 3, 4 and 6 in that order. Each step is **one commit**.
- Until step 4 lands, check each step with the current full gate:
  `python -X utf8 tools/check_release.py`. After step 4, use
  `check_release.py --changed`, as `AGENTS.md` says.
- Every step has a **Done when** line. A step is finished only when that line
  is true and the full gate passes.
- Never delete, skip or loosen a check to make a step pass. If a step can't be
  done without that, stop and report to Haru.
- When all steps are done, update the "Status" line above and the table in
  section 3 with the times you measured.

## 1. How it works today

### `tools/check_release.py`: the gate

A single script runs about 50 sections one after another, stopping at the
first failure.

- **Source checks (always run):**
  - syntax of 21 Python and 26 JavaScript files
  - dictionary TSV schema, sort order and redirect log
  - dictionary counts, collation and audio tests
  - identity baseline and stable-ID references
  - the browser-free engine
  - static and adaptive ranking for both Web and Desktop
  - adaptive safeguards
  - desktop shell bridge, editor readings and editor lifetime
  - Simplified normalisation and Lomari sync
  - compound glosses (a warning only)
  - audio waveform parity
  - desktop parity
- **`--source-only`:** rebuilds only the dictionary JSON, and runs the Web IME
  checks against the source files.
- **Full (no flag):** rebuilds the whole site (`build_site.py`), then also
  validates the published site, the compressed audio copies and the built Web
  apps.

### `.github/workflows/pages.yml`: the gate on GitHub

It runs on every push to `main`, on pull requests and on manual dispatch. Four
jobs:

| Job | Runner | What it runs | Last run |
|---|---|---|---|
| `regression` | Windows | `check_release.py --source-only` | 2 m 36 s |
| `linux-regression` | Ubuntu | the same command again (side check; `continue-on-error`, nothing waits for it) | 2 m 42 s |
| `build` | Ubuntu, after `regression` | `build_site.py`, the `test_site_*` / migration / song-title tests, `check_site.py`, `compressed_audio.py`, `check_web_apps.cjs` | 2 m 30 s |
| `deploy` | Ubuntu, after `build`, not for PRs | publishes `_site`, retrying once after 10 minutes if Pages stalls | 19 s |

Between `regression` and `build`, GitHub runs **everything the full local gate
runs** before anything is deployed. A failing check stops the deploy, although
the bad commit is already on `main`.

### `AGENTS.md`: instructions for agents

- `AGENTS.md` is read by Codex and other agents that follow that convention.
  Claude Code reads `CLAUDE.md` instead and does not load `AGENTS.md` by
  itself.
- `AGENTS.md` holds the **dictionary update procedure**:
  1. validate and sort the TSV
  2. rebuild the dictionary JSON
  3. review the change, then recapture the three baselines together
  4. run `check_release.py --source-only` to completion, rerunning until it
     passes
  5. run Git checks
  6. stage project files only
  7. push and watch the deploy
- Its "Baseline rule" says a baseline failure means a stale snapshot to review,
  never a check to weaken.
- It does **not** say which gate to run for changes that aren't dictionary
  changes. In practice agents run the full gate for everything, including
  documentation-only and CSS-only changes.

### Measured cost (this machine, 2026-11-16, full gate, nothing else running)

Total: **3 m 40 s**. Six sections take 81% of that:

| Section | Time |
|---|---|
| Compressed audio copies (decodes all 3,369 Opus files) | 54 s |
| Dictionary collation and audio portability tests | 47 s |
| Build published site | 38 s |
| Static Desktop ranking | 15 s |
| Validate published site | 13 s |
| Adaptive Local/Desktop learning | 12 s |
| The other ~45 sections together | 41 s |

Earlier runs in this session took over 10 minutes because other sessions were
building at the same time on the same machine.

### Where the usage actually goes

The repository is public, so GitHub Actions minutes are free. The real cost is
**agent usage** (Claude, Codex), which comes from:

1. **Running the gate when it isn't needed:**
   - for documentation-only or CSS-only changes
   - again after it has already passed and nothing has changed
   - as a full gate before a push, even though GitHub reruns all of it before
     deploying anyway
2. **Waiting:**
   - a foreground run that hits the 10-minute tool limit is moved to the
     background, then waited on and read back
   - every wait and re-read costs a turn
3. **Output:** a passing run prints about 180 lines. A failure buried in that
   output gets read in full.
4. **Reruns after a fix:** the whole gate runs again, even when only one
   section failed.

## 2. The plan

Steps are ordered by how much each saves for how little risk. Each step is its
own commit. Steps 5 and 7 are done.

### Step 1: quiet output (`--quiet`, default for agents)

- `check_release.py --quiet` prints only:
  - a one-line `OK  <section>  <seconds>` per section
  - the **full output of a failing section**
  - the final result line
- A passing run drops from about 180 lines to about 50. A `--summary` mode
  could go further, printing only the final line and any warnings.
- Add `--from <section>`, so that after a fix the gate restarts at the failed
  section instead of from the top. The last full or CI run still covers
  everything earlier.
- Keep the current behaviour when no flag is given. GitHub's logs stay as they
  are.
- **Saves:** most of the tokens read on every run. **Risk:** none; the checks
  are the same.
- **Done when:**
  - `--quiet` on a passing tree prints one line per section plus the result
    line.
  - When a section is forced to fail (for example, a temporary syntax error in
    a scratch copy), `--quiet` prints that section's full output.
  - `--from "<section label>"` starts at that section, and an unknown label
    exits with an error that lists the valid labels.

### Step 2: run independent sections in parallel

- The sections mostly only read files. Group them as:
  - **Must run first:** syntax checks, TSV schema, sort, redirect log.
  - **Builds next:** `build_dictionary_json.py` / `build_site.py`.
  - **Then in parallel** (4 at a time):
    - dictionary tests
    - Web checks (`check_*.cjs`)
    - Desktop checks (`check_*_desktop.py`, safeguards, shell bridge)
    - audio checks
  - **Last:** checks of the built site, in parallel with each other.
- Each section's output goes to its own buffer and is printed in order, so the
  logs read the same as now.
- **Expected:** about 3 m 40 s → 1 m 30 s locally. CI's Windows job shrinks
  too.
- **Risk:** a hidden dependency between sections (for example, two sections
  writing the same temporary file). Check by running the parallel gate
  alongside the serial one on a few commits before switching.
- Add `--serial` to force today's one-at-a-time order, for debugging.
- **Done when:**
  - The parallel gate passes three times in a row on a clean tree.
  - A forced failure in one parallel section is reported with its full output
    and makes the gate exit non-zero.
  - The measured total time is recorded in section 3.

### Step 3: make the two slowest checks incremental

1. **Compressed audio (54 s).** `compressed_audio.py` decodes every Opus copy
   to compare it with its WAV.
   - Record each verified pair (WAV hash + Opus hash + encoder settings) in the
     existing audio cache folder.
   - On the next run, decode only pairs that are new or changed.
   - CI starts from an empty cache, so it still checks every file.
   - **Expected:** 54 s → a few seconds locally.
2. **Dictionary collation and audio tests (47 s).**
   - Profile first: Python here lacks `unittest --durations`, so time each test
     class.
   - The likely cost is reading or hashing every WAV. If so, cache the same
     way, keyed on file size and modification time, with a full-check
     fallback.
- **Risk:** low. A cache hit only happens for files that are byte-for-byte the
  same as the last verified pair.
- Keep the verification cache outside `_site/` and outside Git (add it to
  `.gitignore` if needed). Add `--no-cache` to force a full check.
- **Done when:**
  - A second run of `compressed_audio.py` takes a few seconds.
  - Changing one Opus copy in a scratch `_site` makes that file fail on the
    next run.
  - The dictionary tests are faster, or the profile shows where the time goes
    and why it can't be cut. Record that finding here.

### Step 4: change-scoped local gate (`--changed`)

`check_release.py --changed` collects the changed files:

- staged and unstaged changes
- untracked files (excluding `.claude/`)
- commits not yet on `origin/main`

It then runs only the sections those files can affect:

| Files changed | Sections that run |
|---|---|
| `docs/**`, `*.md` (except published content), `AGENTS.md`, `CLAUDE.md` | none ("nothing to check") |
| `apps/**/*.css`, `shared/*.css` | build site, validate published site |
| `apps/**`, `shared/*.js` | JS syntax, Web IME checks, build site, validate published site, built Web apps |
| `content/**`, `migration/**` | build site, `test_site_*`, migration and song-title tests, validate published site |
| `data/*.tsv`, `tools/*dictionary*`, `public/data/**` | the full source gate (dictionary SOP) |
| `desktop/**`, `shared/tli-sandhi.json` | Desktop checks, parity, engine, adaptive and static ranking |
| `public/audio/**` | audio sections |
| `tools/check_release.py`, `.github/**`, anything not listed | the full gate |

- Anything the table doesn't cover falls back to the full gate, so a gap makes
  the gate slower, never weaker.
- The mapping lives in `check_release.py` beside the section list, so adding a
  section means choosing its paths at the same time.
- It prints which files led to which sections, so the choice can be checked.
- **Saves:** most local runs. Documentation and CSS changes become seconds
  instead of minutes.
- **Done when:**
  - Tests in `tests/` cover the mapping: a docs-only change gives no sections,
    a CSS change gives the site sections, a TSV change gives the full source
    gate, and an unknown path gives the full gate.
  - The "Release gate routine" in `AGENTS.md` is updated:
    - use `check_release.py --changed --quiet` by default
    - after a fix, use `--from <section>`
    - remove the "once it exists" wording

### Step 5: decide where the full gate must run (done: option B)

Haru chose **B** on 2026-11-16. It is in effect now through `AGENTS.md`.

Before this, agents ran the full gate locally *and* GitHub ran it again before
deploying. The two options were:

- **A. Keep local full gate before every push** (today's safety level). With
  steps 1 to 3 it costs about 1 to 1.5 minutes instead of 4.
- **B. Local `--changed` gate, GitHub as the full gate.** Agents push after the
  scoped checks pass, and GitHub runs everything before deploying.
  - A miss is still never deployed: `deploy` waits on `regression` and `build`.
  - The cost of a miss: a failing commit sits on `main` until it is fixed
    forward.
  - **Exception:** dictionary changes always run the full source gate locally,
    as `AGENTS.md` already requires.

B was chosen because GitHub already runs every check before anything is
deployed.

### Step 6: trim the workflow

1. **Skip the workflow for changes that can't affect the site:**
   `paths-ignore` for `docs/**`, `AGENTS.md`, `CLAUDE.md`, `README.md` and
   `.claude/**`.
   - Check first that none of these files are copied into `_site`.
2. **Run the Linux side check weekly** (decided by Haru, 2026-11-16).
   - Add `schedule: - cron: "0 3 * * 1"` (Mondays 03:00 UTC) to `on:`.
   - Give `linux-regression` the condition
     `if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'`.
     It then no longer runs on pushes and pull requests, but can still be run
     by hand with "Run workflow".
   - Give `regression` the condition `if: github.event_name != 'schedule'`, so
     a scheduled run doesn't build or deploy anything. `build` and `deploy`
     wait on it, so they are skipped as well. Check that they show as skipped,
     not failed.
   - Keep `continue-on-error: true` and the apt retries. Update the comment
     above the job to say it runs weekly.
   - Nothing waits for this job, and it repeats the Windows job, so running it
     on every push gained nothing.
3. **Cache pip and npm** (`setup-python` with `cache: pip`, `setup-node` with
   `cache: npm`), and cache the Opus encode folder between runs. The cache key
   is the hash of the WAVs plus the encoder settings, so only new recordings
   are encoded.
4. **Leave `deploy` and its stall retry unchanged.**

- **Saves:** faster deploys and less to watch.
- **Risk:** item 1 must not skip anything that is published. That is checked
  before the change.
- **Done when:**
  - `grep` over the build tools shows that no ignored path is copied into
    `_site`. If one is, leave it out of `paths-ignore` and note it here.
  - After the push, the next workflow run shows `linux-regression` as skipped.
  - A manual "Run workflow" runs the Linux job.
  - The second push after caching shows cache hits in the setup steps.

### Step 7: write the rules down for every agent (done)

Done on 2026-11-16. `AGENTS.md` is now the single instruction file, and
`CLAUDE.md` only imports it with `@AGENTS.md`. The "Release gate routine"
section in `AGENTS.md` holds these rules. Step 4 updates it once `--changed`
exists. The rules:

- Which gate to run:
  - `--changed --quiet` by default
  - the full source gate for dictionary changes
  - the full gate only when the scoped gate says so
- Run the gate in the background with its output in a file, and read only the
  result line, or the failing section if there is one.
- Never rerun a gate that passed when nothing has changed since.
- After a failure, fix it, then use `--from <section>`. Run one full pass
  before pushing only when option A applies.
- After pushing, check the workflow once with `gh run watch`, or have the app
  watch it, instead of polling repeatedly.

## 3. Expected result

| | Today | After the plan |
|---|---|---|
| Docs-only change | full gate, about 4 min, plus a GitHub run | no gate, and no GitHub run |
| CSS or content change | full gate, about 4 min | scoped gate, about 40 s |
| Dictionary change | full gate, about 4 min | full source gate, about 1 min (parallel, cached audio) |
| Output read on a pass | about 180 lines | about 50 lines, or 1 with `--summary` |
| GitHub, normal push | about 5.5 min, 4 jobs | about 3 min, 3 jobs |

## 4. Decisions

1. **Step 5: option B** (decided by Haru, 2026-11-16).
   - The local check is scoped to the change, and GitHub is the full gate.
   - Dictionary changes still run the full source gate locally.
   - The routine is in `AGENTS.md` under "Release gate routine". `CLAUDE.md`
     now imports `AGENTS.md`, so Claude and Codex read the same rules
     (step 7).
2. **Step 6.2: run the Linux side check weekly** (decided by Haru,
   2026-11-16), and keep the manual "Run workflow" option.

No decisions are open. Report anything new to Haru instead of deciding it.
