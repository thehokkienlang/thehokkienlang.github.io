# The Egg: formatting plan

Routes: `/read/stories/the-egg/`, `/zh-hant/read/stories/the-egg/`, and
`/zh-hans/…`. The zh-hans page is generated from zh-hant.

## Done (commits af829c6 and e0b9843, 2026-11-21)

- **Shared story.** The Hokkien story is stored once, in
  `content/stories/the-egg.story.html`.
  - The language files `content/stories/the-egg.json` and
    `content/zh-hant/stories/the-egg.json` hold only their header (title,
    image, credits, player) and their footnotes.
  - Each language file marks where the story goes with
    `<!-- story:the-egg -->`.
  - `tools/story_presentations.py` (`STORY_MARKER`) fills in the story.
  - Editing is described in `docs/website-editor.md`. Edit the story in the
    `.story.html` file.
- **Header.** It is the same in both languages: the image, then
  `p.story-credits`. Neither language has a disclaimer (Haru's decision).
- **Cleanup.** Removed:
  - empty paragraphs
  - the WordPress language buttons and the image's `data-*` attributes
  - inline font styles, `color: black` (now `.story-initial`), and the inline
    Noto Sans SC span around 㩼
  - the three hand-positioned rubies
- **Lomari.** The single Lomari line in paragraph 1 was removed, so the story
  has no Lomari.
- **Scene breaks.** `hr.is-style-dots` now renders as centred dots.
- **Footnotes.** Inline styles are removed and the markers are small and
  raised (`site.css` around lines 291–297). Footnote 2's label is now
  `<ruby>揆一<rt>귀읻</rt></ruby>`.
- **Rubies.** The nine bare Hanzi now have ruby: 但 ×2, 行, 用, 所以, 家己,
  來 ×2 and 一个.

## Still open (discuss with Haru first)

- **11. Gloss links.** Should gloss links point to the site's own dictionary
  or to Wiktionary? After that:
  - 36 links lack `gloss-link-nowrap`
  - repeated words are linked unevenly

  Before pointing links at the site's dictionary, the linked terms must be
  added to it. `docs/the-egg-dictionary-audit.md` lists them: 107 of 268
  linked words are missing, and 4 have a different reading.
- **12. Line-break spans.** 19 hand-placed
  `<span style="text-indent:0;display:inline-block">` spans stop punctuation
  wrapping onto a new line. Keep them, or replace them with a CSS rule? This
  is a typographic choice.
- **Lomari for the whole story.** Add Lomari under every paragraph (possibly
  with a show/hide toggle), or leave the story without it.

## Proposed feature: highlight the text as the audio plays

Highlight the story as the recording plays, as lyrics do on song pages
(`docs/lyric-timing.md`). Song timing uses YouTube, but The Egg uses
SoundCloud. Decide:

- **Clock.** Read the play position from the SoundCloud Widget API
  (`getPosition`, `seekTo`, play/pause events), or move the recording to
  self-hosted `<audio>`. Self-hosting also fixes the white player box; see
  `docs/site-display-fixes-plan.md`, item 2.
- **Unit.** Paragraph or sentence. Sentences need sentence markup in
  `the-egg.story.html`.
- **Timing tool.** The Website Editor's Lyric timing screen handles only songs
  on YouTube. It needs stories and a SoundCloud or audio clock.
- **One timing file.** The story is shared and all three pages play the
  zh-hant recording, so one timing sidecar can serve every language.
- **Reading UX.**
  - auto-scroll for long prose
  - click a sentence to seek
  - how the highlight looks with ruby

## Site-level problems found in the review

These are planned in `docs/site-display-fixes-plan.md`.
