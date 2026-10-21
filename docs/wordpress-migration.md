# English WordPress migration

The first batch imports eight pages into the shared GitHub Pages build: Home,
About, Introduction, Spelling, Tone Sandhi, Romanisation, Lyrics Translation,
and Tale of the Lychee Mirror. WordPress is read only throughout this workflow.

## Deferred work

- All 70 song posts are the final batch. Their text is still being edited; fetch
  their latest source only when that work is complete.
- Both presentations of The Egg are also deferred while revision is in progress.
- Traditional and Simplified Chinese presentations will be migrated later.
- Imported source is preserved; its v3.1 compliance review is still pending.
  Apply approved v3.2 linguistic changes after the migration and v3.1 review.

The Songs index and relevant reading links point to the current WordPress pages
until those records are migrated. They do not point to invented GitHub URLs.

## Choose song URLs

Open `migration/song-url-form.html` in a browser. It works directly from disk.
There are two columns: the old WordPress link and an editable new GitHub link.
Type only the title, for example `生份에릐`; the form supplies `/songs/` and the
final slash. Previously saved full links still load correctly. Use the standardised mixed
Hanri-Hangul title, omit apostrophes/tone marks, and distinguish duplicate titles
with an artist name. WordPress IDs remain internal provenance only.

The form preserves edits in browser storage where available and can download
`song-urls.json` or a two-column CSV. Download the form to keep a portable copy;
loading the JSON restores it. Blank rows are allowed. Invalid, reserved, and
duplicate destinations are flagged before download. Copy the reviewed completed
JSON to `migration/song-urls.json` when preparing the final song batch. Filling
the form alone does not publish any songs.

## Sources and media

`content/` contains editable content records separated into pages, guides, and
literature. Each record has its public route, language, original URL, source
revision/hash, orthography review status, and HTML body. Original public HTML
snapshots are retained under `migration/wordpress-source/`. No original song or
Egg body is included in this first batch.

`migration/wordpress-map.json` records the exact imported scope and deferred work.
`migration/wordpress-media.json` maps copied WordPress media to stable local files.
Existing `/assets/` audio remains at its current path. Wikimedia pronunciation
examples and the original external links remain external. No assets are deleted.

`tools/import_wordpress.py --download-media` reads the public WordPress API and
can create the initial records. It refuses to overwrite editorial records.
Source refreshes must be reviewed separately. The normal site build is offline
and never contacts or edits WordPress.

`tools/build_content.py` renders the records through the shared English shell,
with Learn, Songs, and Read indexes. `tools/build_site.py` includes the output in
the same artifact as the dictionary and IME. Migration exports, source archives,
and the local URL form are not copied into the published artifact.

Selecting text in a content page prepares Dictionary and Open IME links for that
text. This uses the existing shared keyboard/pronunciation engines. Imported
readings remain stored HTML and are not recalculated when the dictionary changes.

## Verification

Run the focused import checks and the existing build validation:

```sh
python -X utf8 -m unittest discover -s tests -p test_wordpress_migration.py
python -X utf8 tools/build_site.py
python -X utf8 tools/check_site.py
node tools/check_web_apps.cjs
```

Manual review: compare each guide's tables, ruby and audio with its WordPress
source; review literature paragraphs and illustrations; confirm Chinese-language,
song, and Egg links still reach WordPress; and exercise the form's edit, download,
and restore actions. Original source links are retained at each page's foot.
