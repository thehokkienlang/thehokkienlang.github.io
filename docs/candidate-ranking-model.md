# Candidate ranking model (design for Exodus I)

This document fixes the intended ranking rules before adaptive ranking is implemented. The rules below do not change the current IME in Session 1.

## Static order

- TSV `priority` is a static default prior. Lower positive integers rank earlier. It is not a counter and must never be changed by a user's selections.
- For a fresh user, use the Task 5c canonical candidate order: `priority`, canonical TSV source row, then Hanri text. Keep the existing tone filtering, longest matching input, candidate limit, and generated fallback rules.
- Treat a correction alias as its own TSV entry. It remains available for its source spelling, but its selection history must not be combined with the canonical reading's history.

## Personal order

After the existing eligibility and tone filters, rank each selectable TSV entry by:

```
effective_score = priority - 1.25 * (1 - 2 ** (-min(selection_count, 64) / 3))
```

Sort by lower `effective_score`, then lower original `priority`, earlier source row, Hanri text, and stable `entry_id`. Counts start at zero, so a fresh user sees the canonical TSV order. One selection can move an entry within a tied priority group. About seven selections can move a priority-2 entry ahead of an unselected priority-1 entry. A priority-3 entry cannot jump ahead of an unselected priority-1 entry through learning alone.

The boost saturates below 1.25 priority points; counts stop growing at 64. There is no automatic time decay in the first implementation. A user must be able to clear learned preferences. These limits prevent an old or repeated choice from growing without bound.

## Selection event and persistence

- Count one event only when the user explicitly commits a visible TSV candidate, whether by click, tap, number key, or Enter on the highlighted candidate. Tab and arrow navigation alone do not count. Showing a menu, typing, or accepting text without choosing a candidate does not count.
- Store counts by stable `entry_id`, separately for each user/device. Never write counts into the TSV or generated dictionary JSON. Ignore IDs that no longer exist and keep a version on the preference store.
- The Web IME can use browser-local storage. The desktop shell currently starts on a random localhost port, so browser storage by origin would not persist reliably between launches. Exodus I needs a desktop-local storage bridge or an equivalent stable per-user store.
- Generated toneless fallbacks are always last and never learn. Generated sandhi candidates keep their existing eligibility and position rules but do not collect selection counts. Learning cannot bypass tone compatibility, input matching, or candidate deduplication.

Session 2 assigned every TSV source row a Unicode-derived `entry_id`. The builder publishes it as the JSON entry `id` and derives runtime sandhi IDs from it. These IDs remain pre-release during Genesis 3.1; Exodus I will use the finalized IDs. The regression baseline records both this identity layer and the canonical zero-selection order.

## Regression baseline

After regenerating `public/data/hokkien-hanri-dict.json`, run `node tools/check_dictionary_baseline.cjs` to compare semantic JSON, every reading-key candidate order, and visible menus against the post-5c fixture. The comparison resolves generated IDs to entry positions, so a stable-ID migration can pass without weakening the order check. Use `--capture` only when intentionally accepting a new baseline; ordinary TSV additions will naturally require a reviewed refresh.
