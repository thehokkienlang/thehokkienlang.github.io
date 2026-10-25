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
- Song category ordering in `content/song-categories.json` remains source-only
  for now; dictionary categories are fully editable.
- Git conflict resolution remains in GitHub Desktop. The CMS detects stale files
  and refuses unsafe overwrites rather than trying to merge authored HTML.
- Image and audio asset upload/management is deferred. Existing asset paths can
  still be used in page HTML.
