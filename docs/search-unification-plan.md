# Search box unification plan

Status: in progress. Steps 1 (shared layer and `/songs/`) and 2 (Songs sub-header
and song-page dropdown) are done; see "Order of work" for the rest. Nothing in this plan changes readings, tones,
Hanri or song text. How tone marks match was decided by Haru; see "Tone
matching".

## Why

The site has three public search boxes. They already share the typing engine
(`createTextImeController` in `shared/web-ime-core.js`), but everything around
it is built three times:

| | Site search `/search/` | Dictionary | Songs filter `/songs/` |
|---|---|---|---|
| Markup | `search_page()` in `tools/build_content.py` | hand-written `apps/dictionary/dictionary-view.html` | `song_filter()` in `tools/build_content.py`, then rebuilt at runtime in `apps/content-site/site.js` |
| Keyboard switch, candidate menu, clear button | its own | its own | its own (and no clear button) |
| Labels in EN / 繁 / 简 | Python | `siteText()` | written into `site.js` |
| Text matching | `shared/web-site-search-variants.js` | its own | its own `fold()` in `site.js` |
| Hanri variant table | read from `public/data/site-search-index.json` | dictionary data | written inline into the `/songs/` HTML (about 130 KB on every load) |
| CSS | `.site-search-*` | `.search-panel`, `.search-*` | `.song-filter-*` |

A fix to, say, how the candidate menu behaves on phones currently has to be
made three times. Adding a search box to every song page would make that four.

## The shared layer

### 1. `shared/web-search-box.js`: the one box

`TliSearchBox.mount(root, options)` builds, or attaches to, these parts:

- the label
- the "Enable Hangul keyboard" switch
- the input
- the × clear button
- the Hanri candidate menu and its positioning
- the IME controller

It returns `{ input, value(), setValue(q), clear(), focus() }` and calls
`options.onChange(query)` as the visitor types.

Options:

- `variant`: `"full"` (a page's main search) or `"compact"` (the Songs
  sub-header box).
- `labels`: a key into the shared label table (below).
- `dictionaryIndex` / `entries`: where the IME gets its Hanri candidates.
- `queryParam`: reads `?q=` on load and keeps the URL updated with
  `history.replaceState` as the visitor types.
- `keyboardMode`: `"switch"` (on/off) or `"modes"` (the dictionary's
  Lomari / Hanri-Hangul choice).
- `results`: `"none"` (the page draws its own results) or `"dropdown"` (the box
  shows a results list under itself; used on song pages).

### 2. Matching rules: extend `shared/web-site-search-variants.js`

The file keeps its name, because tests import it.

- `normalise(text)` becomes the only place that folds case, spaces, hyphens
  and tone-mark spellings, following the site search rule (see "Tone
  matching").
- `loadHanriFold()` fetches the Hanri variant table from one shared JSON file
  and caches it, replacing the copy inlined into `/songs/`.

### 3. Python: one builder in `tools/build_content.py`

- `search_box_html(id, language, variant, labels)` writes the same markup for
  every box.
- One `SEARCH_TEXT` table holds every search label in EN / 繁 / 简. Python
  writes it into the markup, so `site.js`, `search.js` and the dictionary stop
  keeping their own copies.

### 4. CSS: one `.tli-search` block

The block goes in the shared site stylesheet, with `.tli-search--compact` for
the sub-header box and `.tli-search-dropdown` for the song-page results list.
The Songs sub-header bar itself gets its own small `.songs-subheader` block. The
three separate rule sets are deleted.

Existing element ids (`siteSearchInput`, `searchInput` and so on) stay as they
are, so current tests, links and saved `?q=` URLs keep working.

### 5. Song search index (new generated file)

A new `public/data/song-search-index.json` (one per language, or keyed by
language) is written by the build, next to `site-search-index.json`. It holds,
for each song:

- route
- title
- Mandarin titles
- category
- lyric lines, as `main` / `lomari` / `search` / line anchor

This is the data `/songs/` currently packs into `data-song-*` attributes. The
build writes it once, and both `/songs/` and the song pages read it. Like
everything in `public/data/`, it is generated and never edited by hand.

## How each search behaves afterwards

### A. Site search (`/search/`): no change for visitors

- Full box; ranked results across pages, guides, songs and stories.
- The kind filter (All / Guides / Songs / Stories) and pagination stay.
- `?q=` and `&type=` work as now.
- Only the box around the input moves onto the shared code.

### B. Dictionary: no change for visitors

- Full box with the Lomari / Hanri-Hangul mode switch (`keyboardMode: "modes"`).
- Searches the dictionary data with its own ranking, as now.
- `?q=` stays.
- Only the box around the input moves onto the shared code.

### C. Song search: one component in a Songs sub-header

The songs filter and the song-page search are one component, `TliSongSearch`.
It uses the shared box, the shared matching rules and the song search index.

It lives in a **Songs sub-header**: a slim bar directly under the main site
header, shown on `/songs/` and on every song page. The two bars show the
hierarchy:

- **Main header (every page):** searches the whole site through the 🔍 icon
  (see D). It is unchanged, so full search stays one tap away on song pages.
- **Songs sub-header (`/songs/` section only):** searches the Songs section.

The sub-header holds:

- **On the left, a breadcrumb:** `Songs › Category`. Each part links back up:
  `Songs` to `/songs/`, and the category to `/songs/?category=…`. On `/songs/`
  itself it shows just `Songs`.
- **On the right, the song search box** (`variant: "compact"`), with the
  placeholder "Search songs…" / 搜尋歌曲… / 搜索歌曲…, the keyboard switch and
  the candidate menu.

The box is in the same place on every Songs page. What changes is only where
its results go.

**On `/songs/` (`results: "none"`): behaves as it does today**

- The search box sits in the sub-header instead of above the catalogue. It
  drives the live filter of the page below it.
- The category chips, count summary and results stay on the page, where they
  are now.
- Live filtering of the catalogue as you type.
- Category chips (All plus each category) stay.
- Lyric-line matches under each song, with the matched line shown in Hangul
  and Lomari, stay.
- Mandarin title matches stay.
- The count summary and the "no songs found" message stay.
- New: the × clear button the other boxes have.
- New: reads `?q=` and `?category=` on load and keeps them in the URL as you
  type, so a filtered list can be shared or bookmarked.
- New: the Hanri variant table and song data come from the shared files, which
  makes the `/songs/` page about 130 KB lighter.

**On each song page `/songs/<song>/` (`results: "dropdown"`)**

- As you type in the sub-header box, a dropdown under it lists matching songs, using the same
  matching as `/songs/`. Each item shows:
  - the song title (with its Hangul reading where the title has one)
  - the category
  - the first matching lyric line, if the match was in the lyrics
- Clicking a song opens it. Clicking a lyric-line match opens the song at that
  line (`#line-NNN`, which song pages already have).
- Keyboard: ↑/↓ move through the list, Enter opens the highlighted item, Esc
  closes the dropdown.
- The dropdown shows the first 8 matches. Its last row, "See all N results",
  goes to `/songs/?q=…` in the current language, where the full filter takes
  over. There is no "search the whole site" row: the 🔍 icon in the main header
  is always visible for that.
- The song index is fetched the first time the box is focused, not on page
  load, so song pages don't get heavier for visitors who never search.

**On phones**

- The main header stays where it is. The sub-header is not sticky: it scrolls
  away with the page, so the two bars don't take up the screen together.
- On narrow screens the breadcrumb shortens to `‹ Songs`, leaving most of the
  width for the search box.
- The dropdown spans the screen width below the sub-header, inside the 16px
  gutters.

### D. Main header 🔍 icon: unchanged

It still links to `/search/` on every page, song pages included. The two
searches don't compete for the same spot: the main header is the whole-site
search, and the sub-header beneath it is the Songs search.

### Not included

The local Song Editor and Dictionary Editor searches. They are never
published, so tying them to the public box would add coupling for no gain.

## Order of work

Each step is its own commit, with the release gate run after it.

1. **Shared layer and `/songs/`.** *(Done.)*
   - Build the shared box, matching rules, label table, CSS and song search
     index.
   - Move the `/songs/` filter onto them.
   - Add the clear button and `?q=` / `?category=`.
   - Check `/songs/` looks and filters as before in all three languages. The
     one intended difference: queries with a tone mark now match only that
     tone.
2. **Songs sub-header and song-page dropdown.** *(Done.)*
   - Add the Songs sub-header (breadcrumb and search box) to `/songs/` and
     every song page, in all three languages.
   - On `/songs/`, move the existing filter's search box into the sub-header.
     The chips and results stay on the page.
   - On song pages, give the box `results: "dropdown"`.
   - Check desktop and phone width: the sub-header scrolls away, the breadcrumb
     shortens, and the dropdown fits the screen.
3. **Site search.** Move `/search/` onto the shared box.
4. **Dictionary.** Move the dictionary box onto the shared box. This is the
   largest step, because of its mode switch and its own app bundle.
5. **Clean-up and guard.**
   - Delete the old CSS and JS.
   - Add a check to `tools/check_site.py` that every public search box comes
     from `search_box_html`, so a separate copy can't creep back in.

## Tone matching (decided by Haru, 2026-11-15)

**Every search box follows the site search rule.** Different ways of writing
the *same* tone are equal (for example `ꞈ` and `ˆ`, using the existing
`toneMarkFold`), but different tones stay distinct.

- A query without a tone mark still finds every tone: `맘` finds `맘ˉ` and
  `맘ˆ`.
- A query with a tone mark finds only that tone: `맘ˉ` finds `맘ˉ`, not `맘ˆ`.

So `normalise()` needs no `tones` option: there is one rule. This changes the
`/songs/` filter, which today ignores tone marks completely, so searching there
with a tone mark will give fewer, more exact results. Step 1 includes checking
that change on a few real queries.
