# Site display fixes plan

Written 2026-11-21, after the review of The Egg
(`docs/the-egg-formatting-plan.md`). Three display problems were found there.
This plan says what each one really is and how to fix it. Only item 1 is a
site-wide bug.

| # | Problem | Scope | Status |
|---|---------|-------|--------|
| 1 | Lomari tone colouring breaks a syllabic `n`/`m` with a tone mark | every Lomari line with a varying tone on n/m | bug, fix |
| 2 | Audio player shows a white box in dark mode | The Egg only (the only SoundCloud embed) | fix or mitigate |
| 3 | The Egg shows 卵 and then "The Egg" / "蛋" as two headings | The Egg only | intentional, Haru to confirm |

No linguistic data changes. Commit and push only when asked.

## 1. Tone colouring breaks syllabic nasals (n̂ / m̂)

### Symptom

In Lomari lines, a tone-1 syllabic nasal before a single hyphen draws wrongly.

- **Old Egg page:** "tn̂g-chu" showed as "t g- ń chu". There was a blank where
  the `n` should be, and the toned `ń` was drawn further along the line.
- **Mobile:** the `ń` landed at the far right of the line.

The Egg no longer has a Lomari line, so reproduce on these songs. The source
has 5 cases:

| Page | Word |
|------|------|
| `/songs/浪溜嗹/` (`content/songs/song-4025.json`) | `nn̂g-` |
| `/songs/愛情릐比꽈想에곻較偉大/` (`song-5458.json`) | `tn̂g-` (×2) |
| `/songs/再會랗心愛에無緣에人/` (`song-5887.json`) | `nn̂g-` |

To list them again, search the `lyric-lomari` spans in `content/songs/*.json`
for `[nm]̂` followed by a single `-`.

### Cause (where to look)

**Ruled out: the fonts.** `.lyric-lomari` uses
`"TLI Western Punctuation", "TLI Noto Sans"`. The punctuation face has no
letters or combining marks; its `unicode-range` excludes them and its cmap has
none. `tli-noto-sans-regular-v3.woff2` has `n`, `m` and U+0300–0304, U+030D
and U+0330. So the `n` and its accent come from the same font.

**Leading suspect: the colouring overlay for tones that differ by sandhi.**

- `prepareLomari` in `shared/web-sandhi-display.js` (around lines 340–365)
  wraps each varying toned letter in `span.tli-lomari-tone`.
- `shared/web-site-navigation.css:283-290` then:
  - makes the real text transparent
  - draws two absolutely positioned copies (`::before` / `::after`, with
    `content: attr(data-tone-text)`) clipped above and below
    `--tli-tone-cut`
- The cut values (-0.19em, or -0.37em for capitals) were tuned for vowels with
  precomposed accents (â/á, ô/ó).
- A syllabic nasal is always decomposed: `n` + U+0302, and in Singapore mode
  `n` + U+0301.

Measure these on a reproduction page:

- Where the pseudo-elements land compared with the span. In the broken
  rendering the copy is drawn away from the letter.
- Whether the songs' `lyric-seek-base` inner span changes the containing
  block. The cue markup puts a span inside `.tli-lomari-tone`.
- Whether the clip cut is wrong for `n`, whose accent sits lower than over a
  capital and differently from over `a`/`o`.
- Taipei and Singapore modes. Both create the span; only the text differs. The
  sandhi preference is in the header menu; `TliSandhiPreference.get()` reads
  it.

**Use a visible browser pane at desktop width and at 375px.** Layout numbers
from a hidden pane are meaningless: `innerWidth` is 0 and every rect is
garbage.

### Fix options (choose after measuring)

- **A. Fix the overlay.** Position the pseudo-elements from the span's own box
  (`inset: 0` with matching `line-height` and `font`, not
  `top: 50%; line-height: 0`), and give n/m their own cut values. This is the
  preferred option if it can be done without disturbing the vowels.
- **B. Different treatment for decomposed clusters.** If a vowel's tone has no
  precomposed form, or the base is `n`/`m`, colour only the combining mark:
  wrap U+0302/U+0301 alone, with no overlay. The accent's colour still shows
  that the tone varies.

### Checks

- Add cases to the existing tests for `web-sandhi-display.js`:
  - `nn̂g-`, `tn̂g-`, an `m̂-` case if any exists
  - a capital `N̂`
  - Singapore output `ń` / `ḿ`
  Find the tests with `grep -rln "TliSandhiDisplay\|web-sandhi-display" tests tools`.
- In a visible pane, check the three songs above in both sandhi modes, in light
  and dark themes, at desktop width and at 375px. Also check that vowels still
  look right, for example `lóng-liáu` on 浪溜嗹.
- Check that selecting the text still shows the real characters
  (`.tli-text-selected`) and that copying gives `n̂` / `ń`.
- Check that the song list (`.song-entry-lomari`) and the home songbook
  (`.home-songbook small`) still look right. They use the same code.
- Run `python -X utf8 tools/check_release.py --changed --quiet`. This edits a
  shared engine file, so the full profile runs.

## 2. White SoundCloud box in dark mode (The Egg)

### What it is

Only `content/stories/the-egg.json` and `content/zh-hant/stories/the-egg.json`
embed SoundCloud. Song pages use YouTube. All three Egg pages play the zh-hant
track (`shared_soundcloud` in `tools/story_presentations.py`).

The white box is SoundCloud's own light loading screen and widget. CSS can't
restyle the inside of the iframe. Part of the white can still be removed: when
the page's `color-scheme` is dark and the embedded page's is light, browsers
paint an opaque white backdrop behind the iframe.

### Options

- **A. Small mitigation (do it now).**
  - Give `.embed-soundcloud` a themed background, rounded corners and the
    shadow that YouTube song embeds get (`site.css:246`).
  - Set `color-scheme: light` on the iframe element, so the browser doesn't
    paint its own white backdrop.
  - Consider the compact player (`visual=false`, height 166), which has much
    less white than the 400px artwork player.
- **B. Click to load.** Show a dark placeholder button ("▶ Listen") and swap in
  the iframe on click. No white flash until the reader asks for audio, and no
  third-party load before that.
- **C. Self-hosted audio (`<audio>`).** This fits the theme fully. It also
  gives the planned read-along highlighting
  (`docs/the-egg-formatting-plan.md`, "Proposed next feature") a clock that
  needs no third-party API. It needs Haru's OK to host the recording, and its
  file size and format decided.

Recommendation: do A now. Decide between B and C together with the
highlighting feature.

### Checks

- `/read/stories/the-egg/`, `/zh-hant/…` and `/zh-hans/…` in dark and light
  themes, at desktop width and at 375px: no white backdrop behind the player,
  and the player still plays.
- Run `--changed --quiet` (website profile).

## 3. Two headings on The Egg: intentional

The Egg's heading is built on purpose by `egg_presentation`
(`tools/story_presentations.py`):

- An H1 卵 with its reading, built like a song title.
- An H2 `.story-subtitle` saying "The Egg" (EN) or "蛋" (Chinese), styled at
  `site.css:102`.

The `<h2>` at the top of the body is replaced; it isn't repeated. **No fix is
needed** unless Haru wants a different design, for example a smaller subtitle
under the title rather than a heading. Ask first.

## Order

1. Item 1 (nasal tone overlay): its own commit, full checks.
2. Item 2A (SoundCloud mitigation): its own commit, website checks.
3. Items 2B/2C and 3: Haru's decision.
