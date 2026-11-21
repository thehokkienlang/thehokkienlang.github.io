# Tangliengim Local Website Editor

The website editor is a private CMS served from the repository on localhost. It
is not copied into `_site` and is never deployed by GitHub Pages.

## Launch

From the repository root:

```sh
npm run editor
```

On this Windows checkout, where npm is not currently on `PATH`, double-click
`Open Website Editor.cmd` or run:

```sh
python "desktop/Tangliengim Website Editor.py"
```

The command starts a server bound to `127.0.0.1` and opens the editor in the
default browser. Keep the terminal open while editing; press `Ctrl+C` there to
close the local server.

## Editable sources

- **Website Pages** edits the title and HTML body in `content/**/*.json`. Routes,
  source metadata, orthography audit data, and generated pages remain untouched.
- **Dictionary** embeds the existing validated dictionary editor. Stable
  `entry_id` values remain read-only.
- **Categories / References** edits `data/dictionary_categories.tsv` and
  `data/dictionary_redirects.tsv` through human-readable entry labels. Stable
  IDs remain the stored relationship.
- **Static Priority** edits `data/dictionary_priority.tsv`, using the existing
  ranking validator to reject impossible ranks and ineligible entries.

Generated `_site/` and `public/data/` files are shown in Git review when a build
changes them, but no editor form can write to them directly.

## Save, validate, commit, and push

These are deliberately separate operations:

1. **Save** writes only the selected canonical source file. It does not run Git.
   Every form carries a source fingerprint; if another program changes the file,
   saving stops and asks for a reload while preserving the on-screen draft.
2. **Validation** runs existing repository commands. The recommended Complete
   website check runs `tools/check_release.py`, which builds and checks the real
   site. A lighter dictionary check and source-only release gate are also
   available.
3. **Changes** displays Git status and unified diffs. Select the reviewed files,
   enter a commit message, and choose **Commit selected**. The editor refuses to
   commit files that changed after the successful validation.
4. **Push commits** runs ordinary `git push` for the current branch. Git uses the
   authentication already configured by GitHub Desktop or Git; the editor never
   requests or stores a password or token.

## First-version limits

- Page content is edited as guarded HTML with a live site-styled preview. A rich
  block editor is deferred because browser reserialization could damage complex
  ruby, table, audio, and embed markup.
- The song sound and mood lists (`content/song-sounds.json`,
  `content/song-moods.json`) are fixed and source-only; a new one is a
  deliberate edit in the repository. Dictionary categories are fully editable.
- Git conflict resolution remains in GitHub Desktop. The CMS detects stale files
  and refuses unsafe overwrites rather than trying to merge authored HTML.
- Image and audio asset upload/management is deferred. Existing asset paths can
  still be used in page HTML.

## The Egg: one shared Hokkien story

The Hokkien text of The Egg (the 68 paragraphs and the three dotted breaks) is
stored once, in `content/stories/the-egg.story.html`. The English and
Traditional Chinese records (`content/stories/the-egg.json`,
`content/zh-hant/stories/the-egg.json`) keep only their own header, recording
and footnotes, and mark the story's place with `<!-- story:the-egg -->`.

- The build replaces the marker with the shared file (`assemble_story` in
  `tools/story_presentations.py`) before the Simplified page is derived and
  before search indexing, so every published page and the search index see the
  full story.
- The Website Editor lists only `*.json` files, so it shows the marker, not the
  story. Edit the story in `the-egg.story.html` directly; one edit changes all
  three languages.
- Keep the marker exactly once in each record. A test enforces this.
