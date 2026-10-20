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
   Entry type is detected automatically and displayed read-only there: numeric
   input with a corrected pronunciation takes precedence, then a `*` reading
   with a corrected reading, then Hanri/mixed words or pure-Hangul overrides.
   New entries, preview and batch imports use the same rules. Existing types are
   retained for ordinary gloss edits; changes to the headword, reading or corrected
   reading trigger reclassification. Defunct is a separate status.
4. **Preview** uses the desktop pronunciation engines for Lomari and recorded
   audio. Missing recordings are identified before publishing.
5. **Save locally** validates the complete proposed data, assigns new IDs,
   updates category/reference labels where applicable, and applies canonical
   sorting. Identical rows are skipped. Another reading or sense for an existing
   headword requires confirmation. Editing the identity headword automatically
   saves a replacement with a new ID and marks the previous record defunct.
   Its original ID stays reserved. Categories and explicit references follow
   the replacement; candidate preference history is not transferred.
6. Local runtime data refreshes in a background job. Returning to the IME window
   refreshes candidates without clearing its typed text.

New entries and headword replacements appear first in the editor with a blue
highlight. Recent-entry highlighting persists in this browser across reloads;
the source TSV retains its canonical order. Ordinary edits to meanings or
readings do not mark an existing entry as newly created.

The default **All entries** view includes defunct records, greyed out and labelled
**Defunct**. Select one to inspect its previous values. The status filter can also
show only active or only defunct entries. Defunct entries are read-only and are
stored in `data/dictionary_defunct.tsv`, with their original
nine fields and `replacement_entry_id`. The replacement link is editor history,
not a public URL redirect. Defunct records are excluded from runtime dictionaries,
IME candidates and script-normalization suggestions. The editor saves and
publishes the archive together with the active dictionary and ID registry.

To retire an entry without replacing its headword, select it and click
**Make defunct**, then confirm. The original saved record stays visible in grey
and its ID stays reserved. Its `replacement_entry_id` is blank. Linked reading
corrections are also retired; active category, priority and correction references
are removed or adjusted. Use **Publish updates** to apply the change to GitHub.

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

Publication preparation runs in an isolated temporary checkout. The publisher first
builds the unchanged remote dictionary and verifies its existing dictionary snapshot.
If that fails, publication stops before any snapshot can be refreshed. After applying
the merged entries, it validates and sorts the dictionary, regenerates the dictionary
and Web/Desktop menu snapshots, builds the website, and checks dictionary references
and generated site files. Each stage appears in the editor's publication status and
has a five-minute timeout. The full developer regression suite runs in GitHub Actions
after pushing rather than blocking the editor before its push. A failed GitHub check
prevents website deployment and is reported separately from a successful push.
The data and generated snapshots are committed together. Fixed linguistic and
behavior fixtures are not refreshed. There is no
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
