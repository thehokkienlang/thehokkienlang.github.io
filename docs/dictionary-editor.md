# Tangliengim Dictionary Editor

Launch `python "desktop/Tangliengim Dictionary Editor.py"` or use **Dictionary
editor** in the Local IME toolbar. This is a local desktop tool; `/editor/` is
served by the localhost bridge, not GitHub Pages.

Publishing requires Node.js for the JavaScript release checks. The editor looks
on PATH, in standard Windows Node.js locations, and in the available Codex runtime.
For a custom installation, set `TANGLIENGIM_NODE` to the full executable path.
The resolved directory is passed to all release-check subprocesses. If no runtime
is available, publishing stops with instructions while keeping local entries saved.

## Daily editing

1. Search/select an entry to edit it, or choose **New entry**.
2. Enter a headword and Hangul reading. The Hangul keyboard checkbox controls
   the existing shared composer in those two fields. Tone symbols are accepted
   and stored as citation digits, following the existing writer normalization.
3. Add English, Traditional Mandarin and existing categories as appropriate.
   Simplified forms are generated using the existing OpenCC rules. Unknown
   translations remain blank. Additional fields expose the stored values.
4. **Preview** uses the desktop pronunciation engines for Lomari and recorded
   audio. Missing recordings are identified before publishing.
5. **Save locally** validates the complete proposed data, assigns new IDs,
   updates category/reference labels where applicable, and applies canonical
   sorting. Identical rows are skipped. Another reading or sense for an existing
   headword requires confirmation. Existing IDs are preserved; changing the
   identity headword requires creating a new record.
6. Local runtime data refreshes in a background job. Returning to the IME window
   refreshes candidates without clearing its typed text.

**Batch import** accepts tab-separated headword, reading, English and Traditional
Mandarin (the last two may be omitted). A named header may specify the existing
dictionary columns, including `entry_id` for deliberate updates. Review/edit the
table before saving. Maximum: 500 entries per batch. A validation failure saves
none of that batch. Exact duplicates are skipped, never deleted from existing
source data. No translation is automatically invented.

## Publishing

**Publish updates** fetches `origin/main` and uses the local HEAD as the common
base. It refuses an unrelated unpublished local commit or staged changes, so
those must first be handled with GitHub Desktop. Unstaged unrelated code is not
included in the data commit.

Records are reconciled by stable ID, then by individual field. Independent
changes are combined. For conflicting fields, select Local or GitHub in the
comparison dialog. Concurrent new entries receiving the same previously unused
ID are preserved by allocating a fresh local ID and updating its category,
priority and redirect references. The merged dictionary must pass validation.

The full release gate runs in an isolated temporary checkout. Only canonical
dictionary/registry/category/priority/redirect data is committed. There is no
force-push. A racing remote update or a new local save stops publishing and
requests a retry. Saved local work remains available.

After pushing, the local checkout fast-forwards to GitHub. Its old dictionary
changes are retained as a named Git stash recovery copy. If unrelated local
changes prevent the fast-forward, the editor reports that publication succeeded
but local checkout update needs attention, and retains the stash. Do not keep
publishing until that checkout state has been resolved.

Publishing and deployment are separate. The editor checks the Pages workflow
for the published commit through an authenticated `gh` command when available,
or GitHub's public API for public repositories. If status is unavailable
(including API rate limits or private repositories without CLI authentication),
it asks you to check GitHub Actions. It never assumes the website updated merely
because the push succeeded.

## Recovery and concurrent use

An OS file lock serializes saves across processes. The form revision prevents
an old editor window from overwriting newer source changes. Reload explicitly
after copying any unsaved form content you wish to retain.

`.dictionary-editor/` is ignored by Git and contains only local operational
state: the current interrupted-save journal, a last-save recovery backup, the
release-check log and publication status. Atomic file replacements and a
journal make dictionary/registry/reference writes recoverable together. The
next editor operation finishes an interrupted save only if those files still
match the transaction's before/after content; unexpected external changes halt
recovery for review instead of being overwritten.

Do not manually edit generated JSON. The editor reuses the current TSV schema,
sorting, ID allocation, priority and category rules; the production contract
remains `docs/dictionary-tsv-schema.md`.
