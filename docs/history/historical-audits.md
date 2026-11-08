# Historical migration audits

The WordPress v3.1 import and v3.2/v3.2.1 reversible-ledger comparisons are
historical provenance checks, not a requirement that live content remain frozen.
Their three exact-body comparisons are opt-in; normal releases still run scope,
rendering, linguistic-rule, dictionary, route, timing, and shared-engine tests.
The original archives and audit ledgers remain unchanged.

To investigate an original migration snapshot in PowerShell, set
`$env:TLI_HISTORICAL_AUDIT = '1'` before running the migration/harmonisation tests.
Later editorial changes may intentionally differ from that snapshot; do not
rewrite historical hashes merely to approve new edits.

Lyric timing fingerprints remain strict when validating or saving timings.
If a published song has stale timing, its lyrics still publish without timing
controls and the build emits a warning naming the sidecar. Reload the timing
editor to review and save new assignments. Timings are never guessed by the build.
