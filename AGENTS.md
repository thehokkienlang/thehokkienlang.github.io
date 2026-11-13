# Tangliengim Repository Agent Instructions

## Push Descriptions

When describing a push, preserve song titles exactly as written in the repository. Never replace them with Pinyin or literal English translations.

## Dictionary Update SOP

Follow this procedure whenever a task changes `data/hokkien_hanri_dict.tsv` or any related dictionary identity, ranking, category, redirect, or registry file. Do not commit or push a partial dictionary update.

1. **Inspect before changing anything.** Run `git status --short` and preserve all unrelated user/agent work. Confirm which dictionary rows and stable IDs are intended to change.
2. **Wait for local editor saves.** If the Dictionary Editor has an active refresh job, wait for it to finish before rebuilding or staging files.
3. **Validate source structure and ordering.** Run:
   - `python -X utf8 tools/validate_dictionary_tsv.py`
   - `python -X utf8 tools/sort_dictionary_tsv.py --check`
4. **Rebuild generated dictionary data.** Run `python -X utf8 tools/build_dictionary_json.py`. Include every changed generated dictionary file required by Git.
5. **Review semantic changes before capturing expectations.** Check entry counts, IDs, candidate order, lookup metadata, and generated/runtime audio changes. Do not update snapshots merely to silence a failure.
6. **Update all three reviewed expectations when the lexical change is intentional.** After reviewing the generated diff, run:
   - `node tools/check_dictionary_baseline.cjs --capture`
   - `node tools/check_adaptive_ranking.cjs --capture-static`
   - `python -X utf8 tools/check_adaptive_desktop.py --capture-static`
   These snapshots protect dictionary semantics, Web cold-start menus, and Local/Desktop cold-start menus respectively; updating only one or two commonly causes deployment failure.
7. **Run the exact GitHub source gate to completion.** Run `python -X utf8 tools/check_release.py --source-only`. Do not stop after the first successful section. Repair every reported stale generated file or expectation, then rerun the whole command until it exits successfully.
8. **Perform final Git checks.** Run `git diff --check` and `git status --short`. Verify that the TSV, registry, generated JSON/sidecars, and reviewed fixtures agree and that no unintended IDs or rows changed.
9. **Stage project files, not local agent metadata.** Do not commit `.claude/`, nested agent worktrees, temporary launch configurations, caches, build scratch directories, or machine-specific absolute paths. Include project edits made by any collaborating agent.
10. **Commit, push, and verify deployment.** Push the current branch, monitor the GitHub Pages workflow, and fix the actual failing expectation or generated artifact if deployment fails. Never repeatedly republish the same failing commit without diagnosis.

### Baseline rule

An expectation failure after an intentional dictionary edit usually means the generated dictionary or one of the three reviewed snapshots is stale. It does **not** mean the check should be removed or weakened. Capture a new expectation only after confirming that the observed lexical, identity, and candidate-order changes are intended.
