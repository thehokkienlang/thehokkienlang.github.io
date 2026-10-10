# Candidate ranking model (Exodus I and II)

The current complete data contract is [the production schema](dictionary-tsv-schema.md).
This document supplies the detailed, unchanged ranking and persistence semantics.

The Pre-Exodus static reform and Exodus I local adaptive layer are implemented.
Adaptive ordering is confined to candidate menus, never dictionary search,
default-reading selection, segmentation, HTML pronunciation, Lomari or audio.

## Identity and default order

The main dictionary has nine lexical/search/identity columns, with no ranking
values or flags. Physical row position is diagnostic, never ranking state.
Source entries compare by entry type (Hangul override, lexical, correction alias,
number pronunciation), canonical Tangliengim SOURCE reading (initial, vowel,
final, next syllable, then tones), canonical headword code points, corrected
reading code points, and finally entry_id. Python collation produces canonicalKey
for Web consumption; Web does not implement competing linguistic collation.
Dictionary search keeps relevance first, then the canonical comparator.

Generated sandhi variants follow their source identity within a reading group
and retain existing tone eligibility. They can occur between other real rows,
as before, but never precede their own source when both are eligible. Generated
toneless fallbacks remain last. Manual overrides can reorder eligible real TSV
classes, as the previous numeric system permitted; they cannot change eligibility.

## Sparse contextual override file

data/dictionary_priority.tsv is UTF-8/NFC, CRLF-terminated, with exactly:

```text
lookup_key entry entry_id rank
```

The actual header uses tabs. entry_id is authoritative. entry is a human-readable
label that must equal the referenced TSV headword; runtime never identifies by it.
rank is a positive 1-based absolute slot, not a global weight or user counter.

lookup_key follows existing input normalization, stored in readable NFC: NFKD
letters/numbers only, then NFC and lowercase. Reading keys first remove tone digits,
legacy tone symbols and correction markers. Hanri keys identify a headword or the
remaining Hanri run. The same ID can have different ranks in different contexts.

Build the normal list, pin listed identities at their requested absolute slots,
then fill empty slots with unlisted candidates in default relative order.
A lone rank-2 pin for D produces A,D,B,C from A,B,C,D. Ranks need not be contiguous.
Duplicate pairs, conflicting slots, out-of-range ranks, unknown/generated IDs,
ineligible references and stale labels are errors, never silently repaired.
No override means normal order. The file is sorted by lookup_key, then rank.

The complete reading group is ranked before existing tone filters. Compiled
staticOrder metadata preserves its relative order in filtered Web subsets.
staticRanks contains validated exceptions for contextual Hanri resolution.
These runtime fields are derived, not additional human-maintained ranking sources.

## Reading defaults and segmentation

The same override mechanism handles polyphonic readings and Hanri segmentation.
Without an override, segmentation prefers greater coverage, fewer segments, a
longer first segment, then canonical order. Context pins choose matching entries;
unmatched-character coverage protection remains. Old summed numeric costs are
removed. Meaningful old choices are explicit contextual exceptions, not hidden
global weights or source-row ties. Python audio/HTML and Web use these semantics.

## Implemented adaptive model

Preferences identify `lookup_key + entry_id`. The adaptive lookup key is the
actual unresolved replacement span, including explicit tones. Normalize straight
apostrophes to `’`, legacy tone symbols to digits, and Unicode to NFC; do NOT
remove punctuation, tone digits, correction/alias distinctions or normalize
unselected final-ㅈ shorthand into its candidate target. Thus `앚`, `아ㅜ`, and
`ᄋᅷ` have independent learned contexts even when they offer the same entries.
Equivalent decomposed/precomposed Unicode and apostrophe glyphs share a context.
Web keys use typedCandidateForm before candidate replacement/punctuation expansion,
so explicit hidden tone metadata is included without storing surrounding sentences.
Classic keys use the actual composer span after the candidate prefix, with its
existing tone normalizer converting invisible internal tone metadata to digits.
Its local-only
Lomari input mode uses `lomari:` plus the unresolved raw Lomari input, rather than
sharing statistics between different spellings converted to the same Hangul.

After static/manual ranking and eligibility/deduplication, retain each candidate's
zero-based index in the complete menu (before the Web display limit). The score is:

```text
adaptive_score = static_index * 2 - selection_count
MAX_SELECTION_COUNT = 255
```

Lower scores come first; original static index breaks ties. Only explicit choices
increment the context/active source ID count by one, capped at 255. No timestamps,
decay, recency weighting, legacy-priority migration, accounts, telemetry or cloud
sync are involved. Three choices can promote a second candidate above an unlearned
first candidate; two choices merely tie and retain static order. Learned preference
may overtake the human-curated manual static favorite within comparable candidates.
Separate IDs, including correction aliases and homophones, never share counts.

Click/tap (including the first candidate) trains. Tab/Up/Down navigation followed
by explicit Enter commit trains. Navigation alone, mouse hover, display, rerenders,
typing, default un-navigated Enter, cancellation and dictionary search do not train.
Keyboard intent remains tied to the same active composition across rerenders and
resets when the composition changes or is dismissed. One commit records once.
Numbers remain tone input, not candidate-selection hotkeys; no new shortcut is added.

Only unambiguous active source entry IDs are learnable. Generated sandhi variants
use their existing source ID, not fabricated `-sandhi` identities. Entries without
an identified source are immutable/nonlearnable. Adaptation sorts contiguous runs
of comparable source candidates, or contiguous runs of generated sandhi candidates.
Transitions between those classes and anonymous/fallback choices are fixed barriers.
Consequently no generated variant crosses its own source; toneless fallbacks keep
their original slots. The classic UI's existing unmarked/predictive prefix fallback
also remains fixed. This preserves the existing per-platform class constraints and
empty-history order instead of redesigning candidate classes. The static index
remains the full-menu index, not a new index within each run.

## Local persistence and reset

Compact payload (dictionary labels/readings/ranks are never duplicated):

```json
{"version":1,"selections":{"시":{"U+662F_00":3}}}
```

Web `/ime/` and the dictionary's Hangul-input candidate menus use origin/profile
localStorage under `tangliengim.candidatePreferences.v1`. Different browser profiles
or devices remain independent. Storage failures do not prevent input or menus.
The controller exposes `preferences.reset()` for programmatic fresh-user reset.

Local Web shell and classic Desktop UI share a per-user JSON file at
`%LOCALAPPDATA%/Tangliengim/candidate-preferences-v1.json` on Windows (normally
`C:/Users/Asus/AppData/Local/Tangliengim/candidate-preferences-v1.json`). Other systems
use `$XDG_DATA_HOME/Tangliengim/` or `~/.local/share/Tangliengim/`.
`TANGLIENGIM_CANDIDATE_PREFERENCES_PATH` overrides the file for isolated tests.
The shell supplies a backend BEFORE controller creation, loads it before activating
dictionary candidates, and queues explicit record/reset requests to a localhost
bridge. Counts are updated by the file store, not by overwriting a browser snapshot.
The file path has no hostname/port component, so a new serving port retains history.
Desktop never uses origin-localStorage as its learning authority. Python exposes
`FilePreferenceStore.reset()`; the Web-shell controller reset calls the same store.

Unknown versions/malformed payloads fall back to empty history. Invalid counts and
inactive/stale IDs are ignored; positive integer counts above 255 are clamped.
Browser writes/file permission failures are nonfatal, but persistence cannot be
guaranteed if the store is unavailable. Exodus II adds the safeguards below without
changing the Exodus I formula, schema, eligibility or static-ranking architecture.
Source dictionary/registry/priority TSVs and generated source data are never edited
by user learning.

`check_adaptive_ranking.cjs` and `check_adaptive_desktop.py` verify explicit/passive
events, promotion, cap, contextual isolation, reload, reset, class barriers and
common Web/Python fixtures. New cold-start menu checksum fixtures were captured
from the pre-change implementation; existing dictionary/default/audio baselines
remain unchanged. The Desktop check serves two distinct real localhost origins.

## Exodus II safeguards

Exodus I implements the adaptive feature; Exodus II hardens its state, storage and
event paths and locks them down with regression tests. It does not tune ranking.

- Scores use the current complete static menu index; deterministic ties preserve
  that index. Candidate insertion, removal and manual-order changes do not rewrite
  history. IDs that disappear are ignored, never rematched by label or reading.
- Positive integer counts are capped at 255. Invalid schemas, arrays, nulls,
  non-integer/negative/zero/string counts and stale IDs are ignored; valid siblings
  survive. Returned snapshots are detached and cannot corrupt internal state.
  JSON numbers use mathematical integer semantics in both runtimes: `1.0` is the
  same value as `1`, but `1.5`, booleans and non-finite numbers are rejected.
- Shared Web and classic commit guards reject reentrant commits and stale menu
  callbacks. Clicking the first choice still learns; passive Enter does not.
  Further typing/native input clears prior navigation intent, while a mere menu
  rerender preserves deliberate navigation. Display, hover, search, cancellation,
  composition completion, caret movement and navigation alone never train.
- Source runs and generated-sandhi runs can reorder internally only. Unknown IDs,
  anonymous fallbacks and class transitions remain barriers, including an existing
  classic prefix fallback. Generated representations use their real source ID.

### Browser consistency and failures

Browser stores re-read the latest persisted payload before ranking or recording,
and observe storage events. Sequential operations in multiple tabs merge with the
latest state rather than overwriting it from a cached snapshot. External reset or
key deletion is observed on the next read; counts and rankings converge.

Unavailable storage, denied reads, quota/write failures and serialization failures
leave input and in-memory learning usable. Unwritten increments are retained in
memory and merged on a later successful write; an unreadable store is never
overwritten. A reset is immediate in memory, but is durable only after a successful
write. Closing the page while storage is unavailable can lose unsaved learning.

localStorage has no cross-tab atomic read-modify-write transaction. Truly overlapping
writes may lose one simultaneous increment, or race with reset. This is not an
exact cross-tab counter guarantee: payloads remain valid, later operations reread
and converge, and ordinary sequential operations do not regress cached counts.
No database migration, retry loop, decay or arbitrary history eviction is added.

### Desktop atomicity and concurrency

The shared stable per-user file is reread under a thread lock and an OS-exclusive
sibling `.lock` file for each record/reset. Separate processes serialize successful
read-modify-write operations. The lock wait is bounded at 250 ms to avoid hanging
input; contention/permissions failures retain session-local state instead of writing
without a lock. OS locks are released when a process exits, including a crash.

Writes use a unique same-directory temporary file, flush/fsync and atomic replacement.
An interrupted write never truncates the valid preference file; an orphan temporary
file can remain after a killed process and is not used as history. Read failures do
not permit a stale overwrite. Failed writes retain pending increments in memory,
which merge with the latest disk state when a later record succeeds. Reset clears
memory immediately and persists empty v1 history if available. External resets are
observed by other file-store instances on their next load/rank. No guarantee is made
for unavailable/nonlocal filesystems that do not honor locking/atomic replacement,
or durability through power failure beyond the platform's replacement guarantees.

The Web shell reloads file-backed state on focus and refreshes active IDs at bridge
reads/records. It queues operations and returns the authoritative sanitized payload.
Each selection request carries a page-session operation token (not an entry ID).
The running bridge remembers its last 512 receipts so repeated delivery of the
same operation cannot double-train. Different deliberate selections remain distinct.
This bounded in-memory receipt cache is not a permanent transaction log: duplicate
delivery after eviction/server restart is not covered. Requests are not automatically
retried; an acknowledgement lost after a write is an ambiguous delivery, not permission
to train again. Offline bridge learning is session-local and may be replaced by the
authoritative file after reconnection. Desktop history remains independent of port.

### Scope and release checks

Only qualifying explicit selections for offered, active source identities create
records; random typing, failed lookup and passive menu use do not grow the store.
Counts are bounded, but the number of legitimately used lookup contexts is not
arbitrarily capped. Preferences remain sparse and contain no dictionary text copies.
No evidence justifies an eviction policy in this phase. The public internal store
API is trusted application code, not an authorization boundary for hostile scripts.

`tools/check_adaptive_safeguards.cjs` and `tools/check_adaptive_safeguards.py` share
`tests/fixtures/adaptive-safeguard-cases.json`. They check all counts 0..255 at four
static positions, 160 deterministic seeded fixtures, malformed siblings, context
isolation, candidate mutations, storage failures, cross-tab refresh/reset, duplicate
and reentrant commits, three concurrent file writers and an interrupted write.
The release gate includes these alongside Exodus I's 7,151 Web and 6,884 classic
exact cold-start menus, reversed-source static checks, two-port persistence, Web
integration, Desktop HTML/TSV bridge and existing dictionary/audio parity baselines.
No source data or baselines are refreshed by learning or by these checks.

## Reviewed baseline

docs/static-priority-migration.json classifies preserved priority-tier effects,
preserved reading/segmentation defaults and expected equal-priority row-tie changes.
Unrelated lexical/search/identity/audio changes are rejected before baseline capture.
tools/check_static_ranking.cjs checks row independence, sparse slots and preserved
contexts. tests/fixtures/dictionary-baseline.json records the reviewed static
foundation, including compiled canonical keys and contextual override metadata.

The subsequent user-approved obsolete Hangul-override cleanup is recorded in
`hangul-override-cleanup.json`. It removes eight redundant overrides and replaces
the copula override with lexical `是 / 시5`. The final override file therefore
contains 97 rows across 73 contexts, rather than the pre-cleanup 98/74. Its
intentional dictionary/default changes were reviewed separately from ranking
parity before the final baseline refresh.
