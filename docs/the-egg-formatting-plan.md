# The Egg: formatting clean-up plan

Status: approved by Haru on 2026-11-21 and ready to run. Do items 1–7 first,
in one commit. Item 8 (one shared story body) follows as its own commit.
Items 11 and 12 are deferred (see the end).

## Scope

- English: `content/stories/the-egg.json` (route `/read/stories/the-egg/`)
- Traditional Chinese: `content/zh-hant/stories/the-egg.json`
  (route `/zh-hant/read/stories/the-egg/`)
- Simplified Chinese (`/zh-hans/read/stories/the-egg/`) is generated from the
  zh-hant record. Don't create or edit a zh-hans file.
- Site CSS: `apps/content-site/site.css`

Each record keeps its story HTML in the `body` string. The story text (the
Hokkien paragraphs, `<p class="indent-2em">`) is identical in both files. Only
the header and the footnote explanations differ. **Make every change to the
story text in both files.**

## Ground rules

- Follow `AGENTS.md`. Don't change any reading, tone, gloss, Hanri choice,
  orthography or Hokkien wording, with one exception: the rubies in item 7, and
  only with the readings Haru approved.
- Edit `body` by loading the JSON, transforming the string and writing it back
  with `json.dump(..., ensure_ascii=False, indent=2)` and LF line endings.
  Check the file's current layout first and keep it byte-compatible apart from
  the body.
- Leave `sourceSha256` alone. It is the hash of the original WordPress post,
  not of `body`, and it already doesn't match the body.
- After each step, view the built page to check it (see "Verify").

## 1. Make the two headers match

Today the two headers are built differently:

- **EN:** the image comes before `<p style="font-family:serif">` with the
  credits, followed by a disclaimer paragraph
  (`<p style="font-family:Serif, Noto Sans;font-size: 80%">`).
- **zh-hant:** the image sits inside a plain `<p>`, the credits end with a
  stray `<span></span>`, and there is no disclaimer.

Target, the same in both files:

```html
<img … class="wp-image-3032" style="width:90px;height:auto;float:right">
<p class="story-credits">
    Original title: …<br>
    Written by: Andy Weir<br>
    Translation: Zhen Dong, Woo
</p>
```

- Put the image before the credits paragraph, as in EN today.
- Drop every inline `font-family`. Add the `story-credits` class to
  `site.css`.
- Remove the EN disclaimer paragraph entirely. Haru decided on 2026-11-21 that
  neither language gets a disclaimer, so don't add one to zh-hant.
- Remove the stray `<span></span>`.

## 2. Remove empty paragraphs

- zh-hant: the `<p></p>` right after the credits. On a phone it leaves a large
  gap.
- Both files: the final `<p class="wp-block-paragraph"></p>`.

## 3. The single Lomari line (paragraph 1)

Only the first paragraph has a Lomari line:

```html
<p class="indent-2em"><span class="lyric-line">…</span><span class="lyric-lomari">…</span></p>
```

None of the other 67 paragraphs has one. Unwrap that paragraph so it matches
the others:

- Keep the inner contents of `lyric-line` without the wrapper span.
- Delete the `lyric-lomari` span.

**Before you delete it**, copy the removed Lomari text into a report for Haru.
If Lomari is later added to the whole story, it can be done as one pass, for
example with `tools/lomari_sync.py` or the Website Editor.

## 4. Style the dotted scene breaks

The body has five `<hr>` elements:

- Two plain `wp-block-separator` rules frame the story: one after the audio,
  one before the footnotes.
- Three `wp-block-separator … is-style-dots` rules are scene breaks inside the
  story.

At the moment all five render as identical solid lines
(`site.css:166`, `.imported-content hr`).

Add a rule to `site.css` for `.imported-content hr.is-style-dots`:

- no border
- centred dots (`::before { content: "· · ·" }` or similar)
- muted colour and letter spacing
- margins like the plain `hr`

Make it work in light and dark themes. `the-egg.json` is the only content file
that uses `is-style-dots`, so the rule won't affect anything else.

## 5. Footnotes

### Markup

Keep the table structure. Songs use the same imported footnote table, and
`site.css:273-280` already restyles it for songs, matched by
`.content-songs .table-scroll:has(a[id^="_ftn"])`.

- Extend those rules so they also cover story pages. Check the class on the
  story page's `<body>` or `<main>` (it's probably `content-stories`). Either
  widen the selector or add a story copy.
- Don't use `--song-column` for stories. Use the story column width.
- In both bodies:
  - Remove the inline `style` attributes from `<table>` and `<td>`.
  - Remove the trailing `<br>` in the zh-hant footnote cells.
  - Remove the leading blank line in the EN footnote 2 cell.
- Remove the `<div style="clear: both;margin-bottom: 2em"></div>` after the
  table. A `clear: both` in CSS replaces it, if one is still needed.

### Footnote 2 label

Footnote 1's label (`팧꼬`) has ruby tone marks. Footnote 2's label is the bare
Hangul `귀읻`. In the story text, 揆一 is written
`<ruby>揆一<rt>귀읻</rt></ruby>`, with no tone marks. Leave the label as it is,
and list it in the report for Haru.

### Markers in the text

The references in the story text are `<a href="#_ftn1" id="_ftnref1">¹</a>`.
They are already superscript characters, but they render at 24px on the
baseline.

- Style `a[id^="_ftnref"]`: smaller font size, raised or `vertical-align:
  super`, accent colour, no underline, no ruby gap.
- Check that the back-links (`_ftn1` / `_ftnref1`) still jump both ways.

## 6. Remove WordPress leftovers

Do this in both files.

- **Language-switch button.** Remove the
  `<div class="wp-block-buttons …">…</div>` block. The build already strips it
  (`LEADING_LANGUAGE_SWITCHER` in `tools/build_content.py:695`), and the EN
  copy still links to the old WordPress post.
- **Image.** Strip `data-attachment-id`, `data-permalink`, `data-orig-file`,
  `data-orig-size`, `data-comments-opened`, `data-image-title`,
  `data-image-description`, `data-image-caption` and `data-large-file`. Keep
  `src`, `width`, `height`, `loading`, `class` and the float style, or move the
  float into a class. Use `alt="An egg"` in EN and `alt="蛋"` in zh-hant, or
  confirm with Haru.
- **Title.** Unwrap the span in
  `<h2 class="wp-block-heading"><span style="font-family:Sans-serif">…</span></h2>`.
- **First character.** Paragraph 1's large first character is
  `<span style="font-size: 150%;color: black">`.
  - Drop `color: black`.
  - Keep the size as a class, for example `.story-initial { font-size: 150%; }`.
  - If item 3 removes the `lyric-line` wrapper, make sure this span stays.
- **㩼 (U+3A7C).** Unwrap `<span style=";font-family: Noto Sans SC">㩼</span>`
  inside its ruby. `site.css:56` already maps U+3A7C to Noto Sans SC through
  the "TLI Hanri SC" font face. Check that the character still renders.
- **Hand-positioned rubies.** There are three
  `<ruby style="position: relative;white-space: nowrap">X<rt style="font-size: 57%;position: absolute;top: -1.2em;left: 0.25em">…</rt></ruby>`
  (the first is 噉, in paragraph ~27).
  - Replace each with a plain `<ruby>X<rt>…</rt></ruby>`, keeping the text
    inside `<rt>` exactly as it is.
  - Compare before and after screenshots. If plain ruby causes a wrapping or
    alignment problem, keep that one and note why. Check `docs/ruby-layout.md`.

## 7. Add rubies to the bare Hanzi (readings need Haru's sign-off)

Nine words in the story have no `<ruby>`. They are the same in both files.
Wrap each one as `<ruby>字<rt>reading</rt></ruby>`.

The readings depend on tone sandhi in context, so **don't guess**. The table
shows how the same words are read elsewhere in this story. The agent should
propose a reading from that and from `tangliengim_engine.py`, then have Haru
confirm each one before committing.

| ¶ | Context | Word | Readings elsewhere in the story |
|---|---------|------|---------------------------------|
| 2 | …去救’릐,【但】實在是無法度. | 但 | 단 ×2 |
| 26 | “只是逽【行】逽講話… | 行 | 걀ˊ ×3 |
| 29 | 就像릐【用】手指 去摸… | 用 | 영 ×1 |
| 39 | “【所以】제全部 攏是為著什物?” | 所以 | 서ˆ이ˆ- ×5 |
| 47 | “【但】是這世界 所有’에 人…” | 但 | 단 ×2 |
| 60 | 就是咧加害【家己】. | 家己 | 가ˉ기ˉ ×4, 가ˉ기 ×1 |
| 60 | 攏是予릐【來】感受. | 來 | 래 ×8, 래- ×1, 래ˊ ×2 |
| 61 | 用真久’에 時間【來】思考. | 來 | (as above) |
| 65 | 릐 是【一个】胎兒… | 一个 | 짇에 ×15, 짇에ˊ ×1 |

The paragraph number (¶) counts the `<p class="indent-2em">` paragraphs from 1.
Find each word by its context string, not by position. Plain `<ruby>` is
enough; adding gloss links is item 11, which is deferred.

## 8. One shared Hokkien story body (do this last, as its own commit)

**Goal:** after items 1–7, the 68 `<p class="indent-2em">` paragraphs and the
three dotted breaks are byte-identical in both files. Store them once, so a
fix to the story text is made in one place.

**Why it fits the build.** `tools/story_presentations.py` already handles The
Egg specially:

- `simplified_egg` derives zh-hans from zh-hant.
- `shared_soundcloud` uses the zh-hant player for every language.
- `egg_presentation` builds the 卵 / The Egg / 蛋 heading.

`tools/build_content.py:945-994` calls these. Extend the same pattern instead
of adding a new content system.

### Proposed layout (confirm it after reading the code)

- **New file `content/stories/the-egg.story.json`** (or `.html`) holds the
  shared Hokkien part: everything from the first story `<hr>` to the closing
  `<hr>` before the footnotes.
  - It needs no `language` or `route` fields. Make sure loaders that glob
    `content/**/*.json` skip it or understand it, or choose a path or
    extension they ignore.
- **`content/stories/the-egg.json` and `content/zh-hant/stories/the-egg.json`**
  keep only their own parts:
  - the header: image and credits
  - the footnote explanations

  Mark where the shared story goes with one placeholder, for example
  `<!-- story:the-egg -->`. Pick a marker the WordPress importers, lomari
  sync and Website Editor will leave alone.
- **`story_presentations.py`** gets a function that replaces the placeholder
  with the shared body. `build_content.py` must call it **before**
  `simplified_egg` and before search indexing (`site_search`). The zh-hans
  page and the search index must keep seeing the full story.

### Make every reader of the body still see the full text

Find every tool that reads `body` from these files and decide, for each, whether
it should read the assembled text or the shared file. Start with
`grep -rn "content/stories\|zh-hant/stories\|rglob\|glob(" tools tests`.
Known readers:

- `tools/build_content.py`, `tools/site_search.py`
- `tools/website_editor_service.py`: it scans `content/` with
  `rglob("*.json")` and saves `body` per file. Story edits must reach the
  shared file, or the editor must clearly show the placeholder.
- `tools/check_stored_sandhi_tones.py` and the other orthography checks. The
  shared body must still be scanned for non-final open tone 4 and other
  orthography problems.
- `tools/lomari_sync.py`, `tools/lyric_timing.py`, and the
  `harmonise_content_*` scripts (`tools/harmonise_content_v33.py` names the
  egg files).
- `tests/test_site_stories.py` and `tests/test_site_languages.py`, which load
  both JSON files directly.
- `tools/check_content_rendering.py`, which counts `p.indent-2em` on all
  three routes. The count must stay at 68.

### Safety

- **Before splitting**, build the site and save the three rendered egg pages:
  `/read/…`, `/zh-hant/…` and `/zh-hans/…`.
- **After splitting**, rebuild and diff the pages. The story section must be
  identical. Only intended header or footnote differences are allowed.
- **Add a test** that the placeholder appears exactly once per language file,
  and that the assembled bodies of EN and zh-hant share the same story section.
- **Run the full checks:**
  `python -X utf8 tools/check_release.py --changed --quiet`. Build tooling
  changed, so the dictionary-sensitive profile runs.
- Document the new layout in `docs/website-editor.md`, or wherever story
  editing is described.

## Verify

1. Run `python -X utf8 tools/check_release.py --changed --quiet`. This is a
   website-profile change. Run it in the background with output to a file.
2. Preview the `built-site` launch config and open both routes, plus
   `/zh-hans/read/stories/the-egg/`, at desktop width and at 375px. Check:
   - no gap where the empty `<p>` was
   - the dotted breaks are visibly different from the framing rules
   - the footnotes are tidy, and the markers are small and raised
   - 㩼 renders
   - the three formerly hand-positioned rubies look right
   - light and dark themes (header toggle)
   - no horizontal scroll at 375px
3. `tools/check_content_rendering.py` already covers the-egg (it counts
   `p.indent-2em`). The paragraph count must stay at 68.
4. Run `git diff --check`. Report to Haru:
   - the removed Lomari line
   - the footnote-2 label
   - the proposed readings for item 7

   Commit and push only when asked.

## Deferred (discuss with Haru first)

- **11. Gloss links.** 36 gloss links lack `gloss-link-nowrap`, and repeated
  words are linked unevenly. Also undecided: whether glosses should point to
  the site's own dictionary or to Wiktionary.
- **12. Line-break spans.** There are 19 hand-placed
  `<span style="text-indent:0;display:inline-block">` spans that stop
  punctuation from wrapping onto a new line. Whether to replace them with a
  CSS rule is a creative and typographic choice.

## Not in this plan (found in the review, site-level)

- The Lomari font breaks `n` with a combining accent. "tn̂g-chu" renders as
  "t g- ń chu". This affects the shared "TLI Noto Sans" font, not just this
  page.
- The heading block shows 卵 (H1) and then "The Egg" / "蛋" (H2). Confirm
  that's intended.
- The SoundCloud embed shows a white box while it loads, in dark mode.
- The EN body's SoundCloud track ID is unused. The build
  (`tools/story_presentations.py`, `shared_soundcloud`) puts the zh-hant
  player on every language.
