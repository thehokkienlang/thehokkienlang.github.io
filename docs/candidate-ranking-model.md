# Candidate ranking model (static foundation for Exodus I)

The Pre-Exodus static reform is implemented. Adaptive learning is not.

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

## Future Exodus I

Adaptive preferences will layer on this completed static order, keyed by permanent
entry_id. Bounded boosts must be calibrated in contextual static-position units,
not the removed numeric-priority points. User data must never rewrite either TSV
or generated JSON. Only explicit candidate commits can learn; display, typing,
Tab/arrow navigation and generated fallbacks cannot. Aliases keep separate
identities. Exodus I/II will implement and test bounds, persistence, resets and
deterministic ties. Desktop's changing localhost origin requires a local preference
store or bridge, rather than assuming browser storage persists across launches.

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
