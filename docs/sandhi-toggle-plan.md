# Taipei ⇄ Singapore sandhi toggle: site-wide plan

Status: approved by Haru (2026-11-19). All eight steps are implemented. Step 7: the check that no
stored non-final open syllable has tone 4 is `tools/check_stored_sandhi_tones.py`. A typed non-final
open 4 is read as 1 by the web IME lookup (`typedSandhiToTaipei` in `shared/web-ime-core.js`), the
desktop IME Pad (`typed_sandhi_to_taipei` in `desktop/tangliengim_engine.py`, which leaves a stored
correction alias such as `먀4재*` as typed) and the Dictionary Editor (stored as 1, through
`tools/typed_sandhi.py`). The Song Editor's lyric text is left as written, because a lyric reading is
the sung tone; its IME lookup does read a typed 4 as 1. Two things are for Haru to review before
publishing: the 心內 example and the guide's new wording in all three languages, and the two Singapore
pattern diagrams (`assets/content/wordpress/singapore-sandhi*.png`).

## Decisions this plan builds on

- **Recording stays Taipei** (Haru, 2026-11-19). Dictionary readings, song
  sources and typed text keep Taipei sandhi digits, for example 歹勢 `팰1세`.
  No unified symbol (`14`) is introduced.
- **Singapore sandhi is regular:** 1→5→3→2→**4**→3. It differs from Taipei
  (2→**1**) in one step only. So a Singapore reading is always derived from the
  stored Taipei one: every open (non-checked) sandhi tone 1 becomes 4. The
  engine already does this for audio, in `desktop/tangliengim_engine.py` and
  `shared/web-ime-core.js`.
- **The toggle changes what readers hear and see, never what is stored.**

## Where sandhi reaches readers today

| Place | Audio | Shown tone marks | Toggle today |
|---|---|---|---|
| IME Pad (`apps/ime/`) | built by the audio planner | typed text | Taipei/Singapore buttons, not remembered |
| Translator (`apps/translate/`) | built by the audio planner | output text | "Audio sandhi" menu, not remembered |
| Desktop IME Pad (`desktop/`) | engine | typed text | its own setting |
| Dictionary (`apps/dictionary/`) | each entry's stored clips (`entry.audio`) | readings with Taipei marks | **none**: always Taipei, although 350 entries already carry `audio.singapore` |
| Homepage listen buttons (`play_button()` in `tools/build_content.py`) | clips baked into the page | — | **none**: Taipei clips only |
| Learn pages, such as the tone-sandhi guide | recorded MP3 phrases (`/assets/audio/*.MP3`) | Taipei marks | **none**; the guide says it follows Taipei |
| Songs | the YouTube recording | ruby marks as sung | not needed (see "Out of scope") |
| Android keyboard | no audio | typed text | not needed |

## What the toggle does

**One site-wide preference: "Sandhi: Taipei | Singapore".**

- **Where it lives:** in the header's language menu (Settings), next to the page
  language. It is also mirrored as the existing controls in the IME Pad and the
  Translator. All of them read and write the same value, so changing it in one
  place changes it everywhere.
- **Stored per visitor** in `localStorage` (`tli-sandhi`), read inside
  try/catch so a blocked store falls back to the default. It is not put in the
  URL, so shared links don't force a dialect on the person opening them.
- **Default (Haru, 2026-11-19):** Singapore for visitors in Singapore, and
  Taipei for everyone else. It applies only on a first visit, when no choice
  is stored yet; once a visitor picks, their choice wins.
  - **"In Singapore"** means the browser reports it: a language tag with region
    `SG` (`en-SG`, `zh-SG`, `ms-SG`, `ta-SG`) in `navigator.languages`, or the
    time zone `Asia/Singapore` from `Intl.DateTimeFormat().resolvedOptions()`.
  - **This adds no delay.** Both values are already in the browser and are read
    once, with no network request. No IP or location lookup is used: one would
    slow the first page and send the visitor's address to a third party.
  - The rule lives in one function, so it can change later.
- **Labels:** "Taipei / 臺北 / 台北" and "Singapore / 新加坡 / 新加坡", plus a
  one-line note in all three languages: "Changes how tone sandhi is marked.
  Stored readings use Taipei."

## Behaviour per place

### Dictionary

- **Audio:** when the preference is Singapore, play `entry.audio.singapore` if
  the entry has it, otherwise `entry.audio`. This is the same rule as
  `audioForCurrentSandhiMode()` in `shared/web-phonetic-output.js`, so it should
  reuse that function rather than copy it.
- **Shown readings (Haru, 2026-11-20: Singapore is shown site-wide):** the
  headword reading, its Lomari and what Copy gives show the derived Singapore
  marks when the preference is Singapore, so the marks never disagree with the
  audio. The stored reading stays Taipei.
- **Search:** unchanged. A Singapore speaker typing 4 on a non-final syllable
  should still find the word. That needs the typed-input normalisation below,
  which is optional and listed separately.

### IME Pad and Translator

- Their existing controls read and write the shared preference instead of
  local state, so the choice is remembered and matches the rest of the site.
- No change to the planner, which already handles both modes.

### Homepage and other listen buttons

- `play_button()` bakes the Taipei clips into the page. It should bake the
  Singapore clips beside them, in `data-tli-audio-singapore` and only when they
  differ.
- `site.js` plays the clips for the current preference.

### Learn pages

- **Replace the one ambiguous example (Haru, 2026-11-19).** The tone-sandhi
  guide's only example where a tone 2 undergoes sandhi is 水內 쥐1래5, "in the
  water": 쥐ˋ → 쥐ꞈ, which Singapore says as 쥐ˊ. Replace it with **心內 심5래5,
  "in one's heart"**, in all three versions of the guide:
  - `content/guides/tone-sandhi.json`
  - `content/zh-hant/guides/tone-sandhi.json`
  - `content/zh-hans/guides/tone-sandhi.json`

  心 is tone 1, and 1 → 5 is the same in both dialects. The example still
  shows a noun-character taking sandhi before the postposition 內, so its
  explanation keeps the same point with 心ˆ → 心ˉ. After this, every Learn
  example sounds the same in Taipei and Singapore, so **the recorded MP3s
  never need switching.** The example's text is Haru's to review before it is
  published.
- **Its audio:** 心內 is in the dictionary (`심5래5`), so its play button can
  use the dictionary's clips, the same way `listen_button()` works, instead of
  a new recording. The old `/assets/audio/쥐래.MP3` stays in the repository,
  unused.
- **The tone-sandhi guide's pattern** (1→5→3→2→1) shows the reader's
  preference: Singapore readers see 1→5→3→2→**4**→3, and Taipei readers see
  today's diagram. The guide's line "specifically follows the Taipei tone
  sandhi pattern" changes to say both are shown, and how to switch.

### Marks everywhere (Haru, 2026-11-20)

"If there is a global switch, it should switch the site": with Singapore, the
site shows Singapore marks, not only Singapore audio.

- **IME Pad and Translator:** the tone marks over the text and the Lomari
  preview (`applySingaporeDisplay` in `shared/web-phonetic-output.js`, the same
  rule as the audio engine). The typed text itself is never changed.
- **Dictionary:** see above.
- **Songs, stories and homepage song picks:** below.
- **Learn pages stay as written.** They teach the writing system, which records
  Taipei, and the romanisation guide quotes POJ and Tâi-lô spellings that must
  not change. The tone-sandhi guide shows the Singapore pattern itself.
- **Teochew text** (`data-sandhi-fixed`) keeps its own marks.

### Songs (Haru, 2026-11-20)

- Song lyrics, song titles and the `/songs/` list show the reader's sandhi
  (`shared/web-sandhi-display.js`, tested by `tests/check_sandhi_display.cjs`).
  The pages stay baked with Taipei marks; the browser swaps them. An open
  syllable marked tone 1 that is joined to the next syllable shows tone 4
  (ˆ → ˊ, ꞈ → ˏ, Lomari â → á). "Joined" follows how the pages are written: a
  following syllable in the same reading, a trailing "-" on a lyric reading,
  what directly follows a tone-only ruby or a title reading, and a single
  hyphen in Lomari. Checked syllables keep tone 1.

## Out of scope

- **Stored data and typing.** TSV, song sources and the Android keyboard keep
  Taipei digits.

## Accept a typed 4 (part of this work, Haru 2026-11-19)

A Singapore speaker naturally types 4 where Taipei has 1. A non-final open
tone 4 never occurs in the dictionary (checked 2026-11-19: 0 cases). So IME
lookup and the editors can safely treat a typed non-final open 4 as 1, and
store 1. This is independent of the toggle and can come before or after it.

## Implementation steps

Each step is one commit, checked as `AGENTS.md` describes (`--changed --quiet`).

1. **Shared preference.**
   - Add `shared/web-sandhi-preference.js`: get, set and change events,
     storage in try/catch, the default constant, and the labels.
   - Tests for storage failing, an unknown stored value and the default.
2. **Header control.** Put the setting in the language menu
   (`shared/web-site-language.js` and `shared/web-site-navigation.*`), in all
   three languages, at desktop and phone width.
3. **IME Pad and Translator** read and write the shared preference. Their
   existing buttons and menu stay, now in sync.
4. **Dictionary audio** follows the preference through
   `audioForCurrentSandhiMode()`. Phrase readings show derived Singapore marks.
5. **Listen buttons:** bake Singapore clips where they differ, and play by
   preference.
6. **Learn pages:**
   - replace 水內 with 心內 in the three guide versions, with dictionary
     audio, for Haru to review
   - the sandhi diagram and wording switch with the preference
7. **Typed-4 normalisation:** IME lookup and the Dictionary and Song Editors
   accept a non-final open 4 as 1 and store 1. Add a check that no stored
   non-final open syllable has tone 4.
8. **Docs:** update `docs/lyric-timing.md` and other references that say
   "Taipei only", and note in `AGENTS.md` that the preference never changes
   stored data.

## Checks

- **Unit tests:** derive Singapore from Taipei for 歹勢, 歹人, 小學生 and
  火車頭, with checked syllables (學生) and 1→5 (真好) unchanged. The engine and
  the browser must give the same results; extend
  `tools/check_web_apps.cjs`'s Taipei/Singapore comparison with these words.
- **Browser:** switch on one page, then confirm the dictionary, IME Pad and
  Translator all follow, and that the choice survives a reload and a language
  change.

## Decisions (Haru, 2026-11-19)

1. **Default:** Singapore when the browser reports Singapore (language region
   or time zone, which costs no time); Taipei otherwise.
2. **Learn pages:** the one ambiguous example, 水內 쥐1래5, becomes 心內 심5래5,
   so no Learn audio needs a Singapore version.
3. **Typed-4 normalisation:** part of this work (step 7).
