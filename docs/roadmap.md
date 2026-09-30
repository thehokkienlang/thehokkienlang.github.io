# Remaining Dictionary Tasks

The next work is planned in this order. Genesis 3.1 prepares and validates the
v3.1 data migration; Tasks I–IV follow it. Roman-numeral task labels are
distinct from the completed historical Arabic-numbered tasks.

## Genesis 3.1

1. **Task Genesis 3.1A — v3.1 migration audit**
   **Model:** GPT-6 Sol, Medium. Compare the current TSV with the published
   v3.1 manual. Identify every affected entry, classify each as safe automatic
   migration, already compliant, or needs manual review, and produce an exact
   migration manifest including expected `entry_id` changes. No edits during
   this audit.
2. **Task Genesis 3.1B — apply v3.1 data migration**
   **Model:** GPT-6 Sol, High. Apply only approved, unambiguous manifest
   changes; update Hanri/Hangul forms and Unicode-derived IDs where canonical
   headwords change; synchronize the pre-release ID registry without redirects.
   Preserve `entry_type` unless the changed headword changes the row's role.
   Run the canonical TSV sorter. Leave ambiguous cases
   untouched and report them.
3. **Task Genesis 3.1C — rebuild, regression and integration**
   **Model:** GPT-6 Sol, Medium. Rebuild generated JSON, run TSV validation and
   release checks, test Web/Local/Desktop lookup, and compare pre/post
   candidate behaviour. Update the regression baseline so v3.1 is the new
   reference state for Tasks I–IV. Make no new linguistic decisions; fix only
   implementation regressions caused by the migration.

## Post-migration work

Genesis 3.1 consolidation is recorded in
[`genesis-3.1-consolidation.md`](genesis-3.1-consolidation.md). Its reviewed
v3.1 regression snapshot is the starting reference for Tasks I–IV, which
remain unimplemented.

1. **Task I — Adaptive ranking**
   Track explicit candidate selections by stable `entry_id` and use locally
   persisted preferences to adjust ordering. Do not modify the TSV.
2. **Task II — Ranking safeguards/tests**
   Verify fresh-user ordering, gradual promotion, persistence, identity
   isolation, and fallback-candidate constraints.
3. **Task III — Stable-ID reference migration**
   Migrate category and other internal references to stable IDs, preserving
   aliases and existing runtime behaviour.
4. **Task IV — Final schema/documentation**
   Finalize the schema description, editing rules, and supporting documentation
   after the data model has settled.

The candidate-ranking design for Task I is documented in
[`candidate-ranking-model.md`](candidate-ranking-model.md).
