# Plan: phrase conversion in the IME, and apostrophe forms in menus

Drafted 2026-11-28 against commit `50cb543` (main). All decisions answered by Haru
on 2026-11-28 (section 9). **Not executed.**

Two changes, released together:

1. **Phrase conversion.** Typing 킈쟣븡 offers **去食飯** first, not 킈食飯. The
   IME converts the whole typed run into a sequence of dictionary words, not
   only the longest word that ends at the cursor. This happens in the web IME,
   the Android keyboard and the desktop Pad.
2. **Apostrophe forms.** Typing 이 offers **이** first, not **’이**. The
   apostrophe (’) forms stay in the menu but are never the first choice.

Phrase conversion is not next-word prediction ([section 10](#10-later-phases)).

## 1. What the IME does now

### 1.1 Web and Android

`findCandidates()` in `shared/web-ime-core.js` (line 2380) builds every
candidate menu for the web IME, the translator and the Android keyboard:

1. `activeCandidateRange()` (line 2337) takes the run of IME characters before
   the cursor. That run can include Hanri that was already converted.
2. The loop tries each ending of the run, from longest to shortest:
   킈쟣븡, then 쟣븡, then 븡.
3. It looks each ending up in `candidatesByReading`, filters by typed tones
   (`filterCandidateEntries`, line 734) and stops at the first ending that
   matches.
4. The adaptive layer (`preferences.rank`, line 590) reorders the result, and
   the menu is cut to `candidateLimit`.

킈쟣븡 is not a reading, but 쟣븡 (食飯, `U+98DF_U+98EF_00`) is. The menu
therefore replaces only 쟣븡, and 킈 is never looked up, although 去 킈
(`U+53BB_00`) exists.

`commitCandidateSelection()` (line 2593) writes one replacement and remembers
one reading span: `rememberHanriReading` for Hanri, `rememberHangulReading` for
Hangul. Those spans drive tone overlays, ruby, Lomari and audio afterwards.

On Android, Space and Enter commit the raw buffer (`commitBuffer` in
`android/keyboard/keyboard.js`, line 153) and ignore the candidate strip. Only
tapping a candidate converts.

### 1.2 Desktop Pad

`find_hanri_candidate()` in `desktop/Hokkien Tangliengim IME Pad.py` builds the
desktop menu from precomputed suffix tests: `build_hanri_candidate_tests`, line
1650 of `desktop/tangliengim_engine.py`. It also stops at the longest matching
suffix, so 킈쟣븡 gives 킈食飯 there too. The desktop menu puts the typed Hangul
first and the Hanri after it. For 킈 it shows `킈, 去`.

## 2. Target behaviour

### 2.1 Phrase conversion

- When the whole run is **not** a dictionary reading, the IME finds the best
  way to split it into dictionary words. If that split has two or more words,
  the IME offers it as one **phrase candidate** at the top of the menu.
- The existing candidates stay below it, unchanged and in the same order.
- When the whole run **is** a reading, nothing changes and no phrase is offered
  (D1).
- Choosing the phrase writes every word at once and remembers each word's
  reading separately, exactly as if each had been chosen alone.
- On Android, Space and Enter convert to the top candidate, then type the space
  or line break (D5).

| Typed | Menu today | Menu after |
|---|---|---|
| 킈쟣븡 | 食飯 (on 쟣븡), 쟣븡 … | **去食飯**, 食飯 (on 쟣븡), 쟣븡 … |
| 쟣븡 | 食飯, 쟣븡 … | unchanged |
| 킈 | ’킈, 去, 킈 | 去, ’킈, 킈 (section 3) |

### 2.2 Apostrophe forms

An apostrophe form (a headword starting with ’) is never the first candidate in
a fresh menu. It takes the second slot, directly after the first plain choice.
See section 3.

## 3. Apostrophe forms: push down, do not remove

### 3.1 What the menus show now

There are ten `hangul_override` entries whose headword starts with ’. These are
fresh web and Android menus, with nothing learned, taken from the current
`main`:

| Typed | Menu now (first four) | ’ form first? |
|---|---|---|
| 이 | **’이**, 이 (이5), 衣, 醫 | yes |
| 킈 | **’킈**, 去, 킈 | yes |
| 래 | **’래**, 來, 內, 래 | yes |
| 됴 | **’됴**, 就, 됴 | yes |
| 둏 | **’둏**, 著, 둏 | yes |
| 뽀 | **’뽀**, 無, 뽀 | yes |
| ᄅᆤ | **’ᄅᆤ**, 了, 聊, ᄅᆤ | yes |
| 꽈 | 꽈 (꽈2), ’꽈, 外, 꽈 | no |
| 릐 | 릐 (릐2), ’릐, 릐 | no |
| 에 | 會, ’에, 个, 挨 | no |

The ’ forms come first because the canonical order sorts `hangul_override`
entries before lexical ones.

In a fresh menu, 꽈 and 릐 already put the plain form first. A device that shows
’꽈 or ’릐 first has most likely *learned* it from earlier taps: three taps on a
second-slot candidate move it to the top (`docs/candidate-ranking-model.md`).
Section 3.4 covers this.

The desktop Pad shows no ’ forms in these menus (for 이 it offers `이, 衣, 醫,
…`), so the problem is on the web and Android only.

### 3.2 Recommendation: push down

Keep the ’ entries and move them to the second slot. Do not remove them.

- **They are real written forms.** Content uses them often: ’에 1,367 times,
  ’릐 122, ’됴 84, ’래 56, ’꽈 54, ’킈 33, ’둏 28, ’이 10, ’뽀 7. Removing them
  would leave no way to type these forms from the menu.
- **Removing them is a dictionary change.** It would retire ten stable IDs and
  change search, Lomari and audio for those forms. Ranking changes only the
  menu order.
- **Second place keeps them quick to reach.** 去 then ’킈 needs one Tab or ↓.
  Last place would bury ’이 under 衣, 醫, 已, 意 and 姨.

### 3.3 How: pins in `data/dictionary_priority.tsv`

The priority file is the existing, reviewed way to change menu order. The web
IME, Android and the desktop Pad all read it, and pins are validated by the
build. A rank-2 pin for the ’ entry moves it to slot 2 and keeps everything
else in its current relative order.

Add these rows (UTF-8, NFC, CRLF, sorted by lookup key, then rank):

| lookup_key | entry | entry_id | rank |
|---|---|---|---|
| 꽈 | ’꽈 | `U+2019_U+AF48_00` | 2 |
| 됴 | ’됴 | `U+2019_U+B434_00` | 2 |
| 둏 | ’둏 | `U+2019_U+B44F_00` | 2 |
| 래 | ’래 | `U+2019_U+B798_00` | 2 |
| ᄅᆤ | ’ᄅᆤˋ | `U+2019_U+1105_U+11A4_00` | 2 |
| 릐 | ’릐 | `U+2019_U+B990_00` | 2 |
| 뽀 | ’뽀ˊ | `U+2019_U+BF40_00` | 2 |
| 이 | ’이 | `U+2019_U+C774_00` | 2 |
| 킈 | ’킈 | `U+2019_U+D088_00` | 2 |

- 꽈 and 릐 are already in this order. Their rows lock it, so a future change
  to the canonical order cannot bring the ’ forms back to the top.
- 에 already has rows (會 1, 挨 4), and ’에 is already second. Leave it.
- Check that a pin on the toneless key also orders the tone-typed menus. For
  example, 이5 typed with its tone filters out ’이 anyway. The pin must not
  raise an "ineligible reference" error there.

Expected menus after the change:

| Typed | After |
|---|---|
| 이 | 이 (이5), ’이, 衣, 醫, 已, 意, 姨, 이 |
| 킈 | 去, ’킈, 킈 |
| 래 | 來, ’래, 內, 래 |
| 됴 | 就, ’됴, 됴 |
| 둏 | 著, ’둏, 둏 |
| 뽀 | 無, ’뽀, 뽀 |
| ᄅᆤ | 了, ’ᄅᆤ, 聊, ᄅᆤ |

This also fixes phrase conversion. The phrase lattice takes each span's first
entry, so without these pins 킈쟣븡 would give **’킈食飯**.

**Found while executing: pins also reach Hangul default readings.** The web
engine picks one Hangul-only entry per apostrophe-free key to give written
Hangul its tones, Lomari and audio, and that choice read the same pins. 이 (이5)
and ’이 share a key, so the 이 pin alone would have made written ’이 read as
이5. `defaultHangulOverride()` in `shared/web-ime-core.js` now keeps the
dictionary's canonical order for such a pair, so pins order menus only. All
default lookups match the build without the pins. No other pin was affected.

### 3.4 Learned preferences

A pin changes the static order only. A device that has learned ’꽈 keeps
offering it first until the learning is cleared or the user taps 꽈 often
enough to outweigh it. The IME pages offer no way to clear learned choices
today. Options, in order of preference:

1. **Recommended:** add a "Reset learned choices" button to the IME settings
   (web and Android). It calls the existing `preferences.reset()`
   (`shared/web-ime-core.js`, line 646).
2. Leave learning as it is and let users retrain by tapping 꽈.

The plan includes option 1, as a small separate commit.

### 3.5 Guard

Add a release check: in every fresh web menu, no candidate whose headword
starts with ’ is first, unless a priority row puts it there deliberately. Add it
to `tools/check_adaptive_ranking.cjs`, which already builds every fresh menu. A
new ’ entry added later then fails the gate until it gets a pin.

## 4. The phrase algorithm

### 4.1 Which part of the run

The phrase lattice uses only the **trailing Hangul-only stretch** of the
active range: everything after the last Hanri character or remembered span.
Hanri that is already written is never re-segmented or changed. For example,
if 去食飯 is committed and 欲킈 is typed after it, the lattice sees only the
Hangul after the last Hanri.

The stretch is split into syllable units with `readingUnitAt()`, the same
helper `typedCandidateForm()` uses, so tone marks or digits stay attached to
their syllable.

Cap the stretch at 16 syllables (D6). Above that, no phrase candidate is
offered.

### 4.2 Lattice

For each pair of syllable positions *i < j*, the span *i…j* is an **edge** when:

- its normalised reading base is a key in `candidatesByReading`, and
- `filterCandidateEntries(typedForm(i, j), entries)` is not empty. Typed tones
  must be compatible, and toneless typing excludes generated sandhi variants,
  as today.

The edge's word is the **first** entry of that filtered list after static
ranking, priority pins included. That is the entry today's menu would put first
for that span typed alone. Adaptive counts are *not* used inside the lattice,
which keeps the rule in `docs/candidate-ranking-model.md`: "Adaptive ordering
is confined to candidate menus, never … segmentation."

Every single syllable also has a **fallback edge** that leaves it as typed
Hangul.

### 4.3 Scoring (D2)

Dynamic programming over positions finds the path with the lowest cost. Costs
compare as tuples, left to right:

1. **Unconverted syllables**: fallback edges, counted in syllables.
2. **Number of words**: fewer is better, so 去 + 食飯 beats 去 + 食 + 飯.
3. **Sum of static slots**: each edge adds its word's 0-based slot in the
   static menu for that span. This is always 0 in this phase, because the
   lattice takes the first entry. It is kept so phase 2 can add frequency
   without changing the shape.
4. **Tie-break**: prefer the path whose *last* word is longest. Then compare
   the words from left to right with `compareCanonicalEntries`, so the result
   is deterministic.

Hangul-override entries (`kind: "hangul_override"`) count as converted words.
They are dictionary choices to write the word in Hangul, and the phrase writes
them in Hangul.

### 4.4 When to offer the phrase (D1)

Offer the phrase candidate only when **all** of these hold:

- the full stretch has no direct dictionary match;
- the best path has two or more edges, and at least one is a dictionary word;
- the phrase converts **more** syllables than the top suffix candidate does.
  This avoids offering 킈食飯 twice, once as a phrase and once as today's
  suffix candidate.

**Added while executing: stored spellings with other tones.** "No direct
dictionary match" means that the dictionary does not store the run's spelling at
all, not only that no entry passes the typed tones. The two differ only for
correction aliases: 능잡3 (stored as 능잡1*, 二十) had no tone-compatible entry,
so 兩十 was offered above 二十. The static desktop snapshot caught this.

**Added while executing: words joined by an apostrophe.** A menu reads only
what follows the last apostrophe, so typing 림1’롷킈 (飲’롷킈, "drink") made
롷킈 look like a run of its own and offered 落去. The static web snapshot caught
this for 飲’롷킈 and 跳’롷킈. No phrase is now offered when the text joined
across the apostrophe is itself a dictionary reading
(`isApostropheJoinedWord`), which is D1 applied to the whole typed word. Both
static snapshots stay unchanged by phrase conversion.

### 4.5 One definition for both engines

The algorithm runs in JavaScript (web, Android) and Python (desktop). To keep
the two identical, a shared fixture `tests/fixtures/phrase-conversion-cases.json`
lists typed runs and the expected segments (entry IDs and spans). Both engines'
tests read it, so a change to one engine that is not made to the other fails
the gate.

## 5. Code changes

### 5.1 Web engine (`TangliengimEngine` in `shared/web-ime-core.js`)

Add `segmentReadingRun(units, lookup)`. It is a pure function:

- `units` is a list of syllable strings with their typed forms.
- `lookup(i, j)` returns the ranked, tone-filtered entries for that span, or
  none.
- It returns `{ cost, segments: [{ startUnit, endUnit, entry | null }] }`.

Export it and add it to the engine's return list. It is browser-free, so
`tests/check_engine_headless.cjs` covers it.

### 5.2 Web controller (`TextImeController`)

- In `findCandidates()`, before the suffix loop:
  - compute the Hangul-only stretch;
  - call `segmentReadingRun` with a `lookup` built on `candidatesByReading`,
    `typedCandidateForm` and `filterCandidateEntries`;
  - if section 4.4 allows it, build one phrase candidate:

    ```js
    {
      entry: {
        hanri: "去食飯",          // segment outputs joined
        reading: "킈 쟣븡5",      // segment readings, space-separated, for the menu's reading line
        kind: "phrase",
        generatedCandidate: true,
      },
      segments: [{ start, end, entry }],   // absolute text offsets
      start, end: range.end, length,
    }
    ```

  - Put it first, ahead of the suffix candidates.
- `preferences.rank` already treats `generatedCandidate` as a fixed slot
  (`classify` returns null), so the phrase stays first and adaptive reordering
  of the rest is unchanged.
- In `commitCandidateSelection()`, add a `kind === "phrase"` branch:
  - build the new text from the segments, right to left so offsets stay valid;
  - call `rememberHanriReading` or `rememberHangulReading` per segment, with
    the same arguments as the single-word branches;
  - do **not** call `preferences.record` for the phrase or its words (D4).
- In `renderCandidates()` (around line 2529), show the phrase's Hanri on the
  main line and the space-separated reading on the reading line.

### 5.3 Android keyboard (D5)

- In `android/keyboard/keyboard.js`, Space and Enter first apply the strip's
  first candidate, then commit the buffer with the space or line break:
  - if `controller.activeCandidates.length`, call
    `controller.applyCandidate(controller.activeCandidates[0], false)`, then
    `commitBuffer(null, " ")` (or `commitBuffer()` for Enter);
  - `explicit` is `false`, so this conversion teaches nothing, like a passive
    Enter on the web.
- If the strip is empty, Space and Enter behave as today.
- To keep Hangul, tap the Hangul candidate in the strip before Space. Words the
  dictionary writes in Hangul (꽈, 릐, 이 after section 3) are Hangul in the
  top candidate already.
- Check the strip width for long phrases in `android/keyboard/keyboard.css`.

### 5.4 Desktop Pad (D3)

- Add `segment_reading_run(units, lookup)` to `desktop/tangliengim_engine.py`.
  It is the GUI-free engine, which the Pad re-exports, and it follows the same
  rules as section 4.
- In `find_hanri_candidate()` (`desktop/Hokkien Tangliengim IME Pad.py`), when
  section 4.4 allows it, add the phrase as the **first** choice. The typed
  Hangul and the existing choices follow, so the order matches the web.
- Accepting the phrase writes each segment and records each segment's reading,
  in the same way the Pad records a single Hanri choice. It does not record a
  learned preference (D4).
- In the Pad, Enter accepts the highlighted choice (`handle_candidate_key`,
  around line 7309), so with the phrase first, Enter converts to the phrase.
- **Space converts too (D8).** Today Space keeps the Hangul as typed (line 7321,
  `cancel_candidate_keep_hangul()`). Change that branch so that, when a
  candidate menu is open, Space first commits the **first** choice (not the
  highlighted one), as Android does, then inserts the space. With no menu open,
  Space only types a space, as today. Like Android, this commit is passive and
  records no learned preference.
  - Keep the Lomari pronoun handling
    (`maybe_commit_lomari_pronoun_li_before_delimiter`) working before the
    space, and keep the undo step.
  - Update the comment above the branch, which today says Space must not
    accept the candidate.
  - Escape and → (Right) still dismiss the menu and keep the Hangul, so there
    is still a key for "keep as typed".
- On the Pad, the typed Hangul is today the first choice in most menus (for 킈:
  `킈, 去`). If Space took that first choice, it would change nothing. The Pad's
  first choice therefore has to be the same as the web's: the phrase when there
  is one, otherwise the web's first candidate (去 for 킈). Check this against
  the shared fixture. If the Pad's typed-Hangul slot has to stay first for
  single words, Space takes the first **non-Hangul** choice instead. Decide
  which while implementing, and record the result here.
- A PyInstaller build must still bundle `tangliengim_engine.py` (`AGENTS.md`).

**Decided while executing.** The typed Hangul stays first in the Pad's menu, so
its menus for single words are unchanged. Space does not take "the first
non-Hangul choice", which would turn 꽈 into 外 and break D5 and D8. It works
out the **web's first candidate** (`first_conversion()`): the phrase, otherwise
the word the web menu would put first, learned choices included. That is Hangul
only where the dictionary writes Hangul. On 7,710 of 7,716 single-word
spellings it writes what the web writes. The other six use the vowel ힻ
(U+D7BB, 短): the web's candidate range does not include that character, an
older gap.

The Pad also remembers words chosen in Hangul, so a later phrase or Space does
not split them again, as on the web. The on-screen keyboard guide's Space
converts like the physical key.

**Changed while executing, for Haru to confirm (limits D5 and D8).** Space on
the Pad, and Space and Enter on Android, **keep the text as typed** when the
conversion would attach to a typed apostrophe: it directly follows ’ without
writing its own, or it ends a dictionary word joined by ’. A menu reads only
what follows the apostrophe, so converting would turn ’킈 into ’去, 꽈’에 into
꽈’會 (’에 appears 1,367 times in content) and 림1’롷킈 into 림’롷去. The menus
are unchanged, and picking a candidate still converts. The cost: Space also
keeps a phrase typed straight after an apostrophe (감샤’킈쟣븡).

## 6. Tests

| File | Change |
|---|---|
| `tests/fixtures/phrase-conversion-cases.json` (new) | Shared cases: typed run → expected segments (entry IDs, spans), or "no phrase". |
| `tests/check_phrase_conversion.cjs` (new) | Runs the shared cases against `segmentReadingRun`, plus controller tests below. Register in `tools/check_release.py` beside "Browser-free engine (mobile keyboard source)". |
| `tests/test_phrase_conversion.py` (new) | Runs the shared cases against `segment_reading_run`, plus a Pad menu test like `tools/check_adaptive_desktop.py` does. |
| `tests/check_engine_headless.cjs` | `segmentReadingRun` runs with no browser and matches the browser core. |
| `tools/check_web_apps.cjs` | On `/ime/`: type 킈쟣븡, the first candidate is 去食飯, Enter writes it, and the tone overlay is right. |
| `tools/check_adaptive_ranking.cjs` | Add the apostrophe guard (3.5). |
| Android keyboard page | A headless test of `keyboard.js` that Space after 킈쟣븡 commits `去食飯 `, and with an empty strip commits the raw text. |

Cases for the shared fixture and controller tests:

1. 킈쟣븡 → 去 + 食飯; the menu still has 食飯 on 쟣븡.
2. 쟣븡 alone → no phrase, menu identical to today.
3. 감샤 → no phrase (感謝 is a word), menu identical to today (D1).
4. 킈감샤 → 去 + 感謝, not 去 + 甘 + 寫.
5. A typed tone that rules out one word changes the split, or drops the phrase.
6. A Hangul-override word inside the run comes out in Hangul.
7. An unknown syllable in the middle stays Hangul, and the rest converts.
8. Existing Hanri before the stretch is untouched after committing.
9. Committing the phrase leaves one remembered span per word with the right
   reading; Backspace and re-typing behave as for single words.
10. No preference is recorded for a phrase commit, and showing the menu learns
    nothing.
11. A 17-syllable run offers no phrase.

### Snapshots

- **Phrase conversion** never changes a menu for a run that is a single word
  (section 4.4). `tools/check_adaptive_ranking.cjs` and
  `tools/check_adaptive_desktop.py` only type single words, so phrase
  conversion should leave both static snapshots unchanged. If one changes
  because of phrase code, treat it as a bug in the 4.4 condition.
- **The apostrophe pins** (section 3) do change menus: 이, 킈, 래, 됴, 둏, 뽀
  and ᄅᆤ, with and without their tones, on the web. Review that diff against
  the table in 3.3. Check whether the desktop snapshot changes at all, since
  the desktop does not show these forms. Then recapture all three expectations
  under the Dictionary Update SOP, step 6.

## 7. Order of work

Each step is a separate commit, so it can be reviewed and reverted on its own.

1. **Apostrophe pins (section 3).** Follow the Dictionary Update SOP:
   - add the priority rows;
   - run `validate_dictionary_tsv.py`, `sort_dictionary_tsv.py --check` and
     `build_dictionary_json.py`;
   - review the menu diff, then recapture the three baselines;
   - add the guard (3.5).
2. **Reset learned choices (3.4).** Add the button on the web IME and the
   Android keyboard.
3. **Web engine and controller (5.1, 5.2)**, with the shared fixture and the
   JavaScript tests.
4. **Desktop Pad (5.4)**, with the Python tests on the same fixture.
5. **Android Space and Enter (5.3)**, with its test.
6. Haru reviews the default phrase for a sample of sentences from songs and
   stories. A small script strips the Hanri from lyric lines, re-types the
   readings and compares the phrase with the original. This also measures how
   often phrase conversion picks the right Hanri.

## 8. Checks and release

1. After each step, run `python -X utf8 tools/check_release.py --changed --quiet`.
   Steps 1 and 3–5 touch the dictionary or shared engines, so they select the
   full profile. The desktop checks need Tkinter.
2. Before pushing, run `python -X utf8 tools/check_release.py --source-only`
   to completion, then `git diff --check`.
3. Push to `main` and check the Pages run once.
4. **Android 0.6.** In the same push or the next one:
   - set `versionName` to `"0.6"` and `versionCode` to `24` in
     `android/app/build.gradle`;
   - set `android/published-version.txt` to `0.6`;
   - check the "Build Android Keyboard" run, the `android-v0.6` release and the
     version on `/ime/`.
5. **Desktop.** Rebuild the Windows Pad (PyInstaller, bundling
   `tangliengim_engine.py` and `shared/tli-sandhi.json`) and test 킈쟣븡 and the
   apostrophe menus on Windows.

## 9. Decisions (answered 2026-11-28)

| # | Question | Answer |
|---|---|---|
| D1 | When the whole run is already a word, should a split phrase be offered too? | **No.** |
| D2 | Which split wins? | **Fewest Hangul left, then fewest words**, as drafted. |
| D3 | Does the desktop Pad get phrase conversion now? | **Yes**, at the same time, so all IMEs agree. |
| D4 | Does accepting a phrase count as picking each of its words? | **No**, for now. |
| D5 | On Android, do Space and Enter convert to the top candidate? | **Yes.** |
| D6 | How long can a typed run be and still get a phrase? | **16 syllables.** |
| D7 | Apostrophe forms: remove, or push down? | **Push down to slot 2.** Haru left the choice to the plan; section 3 gives the reasons. |
| D8 | Desktop Pad: should Space also convert to the top candidate, as on Android? | **Yes**, convert rather than keep the Hangul. |

Choices made in this plan (from D7, and the details Haru left open):

| # | Choice | Where |
|---|---|---|
| P1 | Keep the ten ’ entries; do not retire their IDs. | 3.2 |
| P2 | Each ’ form goes to slot 2, right after the first plain choice, not to the bottom. | 3.2, 3.3 |
| P3 | Use rank-2 rows in `data/dictionary_priority.tsv`, not a new rule in the engine code. | 3.3 |
| P4 | Add pins for 꽈 and 릐 too, although their order is already right, to lock it. | 3.3 |
| P5 | Leave 에 as it is (會 1, ’에 2, from existing rows). | 3.3 |
| P6 | Add a "Reset learned choices" button on the web IME and Android, for devices that learned ’꽈 or ’릐. | 3.4 |
| P7 | Add a release check that fails if a ’ form is first in a fresh menu without a priority row. | 3.5 |
| P8 | Android and desktop Space take the **first** candidate, not the highlighted one. Desktop Enter keeps taking the highlighted one. | 5.3, 5.4 |
| P9 | Space and Enter conversions are passive and teach nothing. | 5.3, 5.4 |
| P10 | Phrase conversion and the apostrophe fix ship together, with the apostrophe pins first, as Android 0.6 and a new desktop build. | 7, 8 |

The examples behind each decision:

### D1. A phrase next to a whole word: no

Typing **감샤** offers **感謝** "thank", as today. The split 감 + 샤 would give
甘 + 寫 (**甘寫**), which means nothing, so no phrase is offered when the whole
run is a word. Every single-word menu stays exactly as it is.

### D2. Which split wins: fewest Hangul left, then fewest words

- **킈감샤** → **去感謝** (2 words) beats 去甘寫 (3 words). Both convert
  everything, so the one with fewer, longer words wins.
- **킈쟣븡** → 去 + 食飯 beats 去 + 食 + 飯. The text is the same, but 食飯 is
  stored as one word with its own reading, so tone marks, Lomari and audio
  treat it as one word.
- If one syllable is in no dictionary entry, every other syllable still
  converts, and only that one stays in Hangul.

### D3. Desktop Pad: yes, at the same time

After the release, typing **킈쟣븡** gives **去食飯** first on the web IME, the
translator, the Android keyboard and the Windows Pad. The shared fixture
(4.5) keeps the engines in step.

### D4. Learning from phrases: no, for now

쟣 alone offers 食, 才, 遮, 隻. Accepting 去食飯 does not move 食 or 食飯 up in
any single-word menu. Learning still comes only from clicks and arrow-key
choices on single words, as today. Learned phrases are phase 3.

### D5. Android Space and Enter: convert to the top candidate

Type **킈쟣븡**, then press Space: the app receives `去食飯 `. To keep Hangul,
tap the Hangul candidate first. Typing **꽈** and Space gives `꽈 `, because
꽈 is first in its menu. The conversion is passive, so it teaches nothing.

### D6. Length cap: 16 syllables

A 12-syllable line typed in one go gets a phrase for the whole line. A
20-syllable line gets no phrase. Its menu behaves as today, converting the last
word.

### D7. Apostrophe forms: push down

Typing **이** gives **이**, then ’이, then 衣, 醫 …; typing **킈** gives **去**,
then ’킈. The ’ forms stay one Tab or ↓ away. Content uses them hundreds of
times, so removing them would lose a real written form (section 3.2).

### D8. Desktop Space: convert

On the Windows Pad today, Space after 킈쟣븡 types a space and keeps
`킈쟣븡` in Hangul. After the change, it types `去食飯 `, as on Android. To keep
the Hangul, press Escape or → before the space. All three IMEs then behave the
same way on Space (section 5.4).

## 10. Later phases

- **Phase 2, corpus frequency.** The songs and stories pair each Hanri word
  with its reading. A build step (`tools/build_dictionary_json.py` or a
  sidecar) counts each entry ID's occurrences and the common pairs of
  neighbouring words. Section 4.3, cost 3, then uses those counts. The corpus
  is small (85 songs), so the counts only break ties between same-sounding
  words. They never override `dictionary_priority.tsv`. This changes candidate
  order, so it follows the Dictionary Update SOP and needs a reviewed snapshot
  recapture.
- **Phase 3, learned phrases.** Remember accepted phrases (reading sequence →
  entry IDs) in the preference store, behind the same backend and reset as
  today. A phrase the user accepted once comes first next time. This is where
  D4 can be revisited.
- **Phase 4, next-word prediction.** After a commit, suggest likely next words
  from the word-pair counts. This is a separate feature with its own menu
  state.
