# Genesis 3.1 Consolidation

This checkpoint completes Genesis 3.1C against the current working-tree TSV
and the published *Tangliengim Orthography v3.1*, especially sections 4.1-4.5.
It is the data reference for Tasks I-IV; none of those tasks is implemented.
IDs remain pre-release. This checkpoint does not freeze public identifiers or
establish backwards-compatibility obligations.

## Completeness and approved decisions

No additional unambiguous existing-row migration was found. The earlier
approved changes are already present:

| Headword | Reading | Active ID | Decision |
| --- | --- | --- | --- |
| 徦 | 갛 | `U+5FA6_00` | Replaces the old `가2 / 가ˋ` override; lexical entry |
| 哪裡 | 나1리2 | `U+54EA_U+88E1_00` | Retained; English is `where` |
| 底 | 되2 | `U+5E95_00` | Approved base reading |
| 底 | 도2 | `U+5E95_01` | Additional reading; no third row was invented |
| 就 | 쥬5 | `U+5C31_00` | Distinct literary reading retained |
| 這 | 짇 | `U+9019_00` | Legitimate reading retained |
| 彼 | 힏 | `U+5F7C_00` | Legitimate reading retained |
| 제ˋ | 제2 | `U+C81C_00` | Separate Hangul override retained |
| 헤ˋ | 헤2 | `U+D5E4_00` | Separate Hangul override retained |

The current 慐, 遮邇, 遐邇, 底, 車輦, 目滓, 䭕, and 㩼 forms were checked.
Lexical 著 remains distinct from aspectual Hangul overrides, including ’됴
and phrase-final ’둏. No blind character replacement was applied.

Manual review remains separate from migration completeness:

- The blank-gloss `뎋` override needs function/regional confirmation. The
  manual allows regional *teh* beside standard *leh*; pronunciation alone
  does not establish an erroneous entry. It is unchanged.
- A dedicated Singapore aspectual `’ᄃᆤ` row is absent. Whether to add it is
  a dictionary-coverage decision, not a justified rewrite of lexical 牢.
  Other absent standalone grammatical forms likewise were not invented.

## Identity and row preservation

There are 2,749 source rows and exactly 2,749 unique active registry IDs.
Every Unicode ID matches the normalized canonical headword. Registry redirect
cells are empty. Earlier cleanup removed 2,749 unpublished `tlg-...` mappings
and the unpublished `U+AC00_00` redirect; no such records were restored.
`_00` denotes a real base entry, not a synthetic headword group.

Source types: 65 `hangul_override`, 2,664 `lexical`, 10 `correction_alias`, and
10 `number_pronunciation`. The build produces 5,466 runtime entries, including
2,717 generated sandhi variants; 2,739 source entries are active and the 10
correction-alias source rows are inactive. No source rows were lost.

## Exhaustive regression comparison

The pre-rebuild JSON reproduces the old format-4 baseline exactly. Comparison
with the rebuilt JSON was performed using ID correspondence, rather than
mistaking array-position changes for lexical changes.

| Difference | Classification and explanation |
| --- | --- |
| Old 가 override becomes 徦 / 갛 | Expected v3.1 effect: headword, reading, kind/type, Lomari and citation audio follow the approved lexical change; its generated sandhi variant follows the new citation reading |
| 到 and 教 citation audio | Expected v3.1 data dependency: their unchanged unmarked `가` readings now resolve Tone 3 instead of inheriting Tone 2 from the removed `가2` override; no audio algorithm changed |
| 哪裡 English fields | Expected approved data correction: blank becomes `where`, including the generated sandhi variant |
| Three source IDs and three generated IDs | Expected ID effect: 가 becomes 徦; the two approved 底 suffix assignments exchange; generated `-sandhi` IDs follow their source IDs |
| 105 source-row positions / 200 runtime-row positions | Expected canonical-order effect from moving the former Hangul override into the lexical 徦 position; surviving candidate relative order is unchanged |
| Two reading-key candidate lists and two visible menus | Expected v3.1 effect: 徦 leaves the 가 menu and enters the 갛 menu; all other menu contents/order match after identity/position correspondence |
| 16 lookup-index buckets | Expected v3.1 effect: the same moved entry changes Hanri, reading, reading-base, Lomari and first-character index membership; no unrelated index memberships differ |
| Counts and source hashes/byte length | Expected type/data/registry provenance effects; active count and generated-sandhi count are unchanged |
| Categories, runtime rules, skipped rows | Exactly unchanged |

All semantic differences are covered above; there are no unexplained
regressions. Audio assets, shared playback code, tone rules, sandhi mechanics,
and Lomari mechanics were not edited. Data-dependent pronunciation changes
are explicitly distinguished from algorithm changes.

`tests/fixtures/dictionary-baseline.json` now records the reviewed v3.1 state:
2,241 candidate keys, 5,466 runtime entries, and their permanent identities.
Generated JSON and `_site` remain build products, not independently edited
dictionary sources.

## Integration verification

- Seven-field TSV validation, NFC/CRLF checks, canonical sorting, and exact
  active-ID registry agreement pass. `.gitattributes` preserves the two
  canonical TSV files byte-for-byte across Windows and Linux checkouts.
- Sixteen focused collation/schema/ID tests pass, including approved v3.1
  assignments and rejection of unpublished legacy redirects.
- Sorting and ID assignment on copies of the current TSV are byte-idempotent.
- Source and built Web IME/Dictionary bootstraps and shared-engine checks pass.
- Desktop shell serving, local HTML/TSV bridge, and existing desktop parity
  fixtures pass. All 16 audio waveform parity cases pass unchanged.
- The active Local IME TSV and registry were synchronized byte-for-byte.
  Its loaders now preserve ID/type metadata; its existing parity cases and
  徦 lookup pass. Local-only UI differences and the legacy backup were not
  overwritten.
- Full `python -X utf8 tools/check_release.py` validates the rebuilt site and
  both applications. This checkpoint does not substitute automated checks
  for new physical-device or listening tests.

The remaining work starts with Task I, then Task II, Task III, and Task IV.
