# The Egg: open work

**Pages:**

- `/read/stories/the-egg/`
- `/zh-hant/read/stories/the-egg/`
- `/zh-hans/…`, which is generated from zh-hant

**Where the content is:**

- The Hokkien story is stored once, in `content/stories/the-egg.story.html`.
- The language files `content/stories/the-egg.json` and
  `content/zh-hant/stories/the-egg.json` hold only the header and footnotes.
- Editing the story is described in `docs/website-editor.md`.

The formatting clean-up and the dictionary audit are done. All 268 linked words
and 77 unlinked ruby words are in the dictionary (commits af829c6, e0b9843,
1128ddf).

## Open (discuss with Haru first)

- **11. Gloss links.**
  - Point the 371 links at the site's own dictionary instead of Wiktionary,
    sutian and Wikipedia? Every linked term is now in the dictionary.
  - 36 links lack `gloss-link-nowrap`.
  - Repeated words are linked unevenly.
- **12. Line-break spans.** 19 hand-placed
  `<span style="text-indent:0;display:inline-block">` spans stop punctuation
  wrapping onto a new line. Keep them, or replace them with a CSS rule?
- **Lomari.** Add Lomari under every paragraph (possibly with a show/hide
  toggle), or leave the story without it.

## Proposed feature: highlight the text as the audio plays

Highlight the story as the recording plays, as lyrics do on song pages
(`docs/lyric-timing.md`). Song timing uses YouTube, but The Egg uses
SoundCloud. Decide:

- **Clock.** The SoundCloud Widget API (`getPosition`, `seekTo`, play/pause
  events), or self-hosted `<audio>`. Self-hosting also fixes the white player
  box (`docs/site-display-fixes-plan.md`, item 2).
- **Unit.** Paragraph or sentence. Sentences need sentence markup in
  `the-egg.story.html`.
- **Timing tool.** The Website Editor's Lyric timing screen handles only songs
  on YouTube.
- **One timing file.** All three pages share the story and the zh-hant
  recording, so one sidecar can serve every language.
- **Reading UX.** Auto-scroll, click a sentence to seek, and how the highlight
  looks with ruby.

Site-level problems found in the review are in
`docs/site-display-fixes-plan.md`.
