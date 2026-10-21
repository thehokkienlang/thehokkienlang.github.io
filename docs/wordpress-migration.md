# English WordPress migration

The English import now contains 79 records: Home, About, four learning guides,
Lyrics Translation, Tale of the Lychee Mirror, 70 songs, and the English
presentation of The Egg. The completed song URL form supplies all 70 public
song paths. WordPress is read only throughout this workflow.

## Deferred work

- The Traditional Chinese presentation of The Egg (WordPress ID 7647) is deferred.
- Traditional and Simplified Chinese presentations will be migrated later.
- Imported source is preserved; its v3.1 compliance review is still pending.
  Apply approved v3.2 linguistic changes after the migration and v3.1 review.

The Songs and Read indexes now link to the imported GitHub pages. Links in the
first batch have also been updated. Chinese presentation links remain on
WordPress. No WordPress redirects or deletions have been performed.

## Choose song URLs

Open `migration/song-url-form.html` in a browser. It works directly from disk.
There are three columns: the old WordPress link, an editable new GitHub link,
and a separate displayed page title. Titles whose chosen URL slug consists
entirely of Hanri are prefilled; mixed Hangul titles are left blank for manual
entry. Page titles retain spaces, punctuation and tone marks. Both editable
columns support the shared Hangul IME. URL choices and displayed titles are
saved separately in browser storage, preserving earlier saved links.
Type only the title, for example `生份에릐`; the form supplies `/songs/` and the
final slash. Previously saved full links still load correctly. Use the standardised mixed
Hanri-Hangul title, omit apostrophes/tone marks, and distinguish duplicate titles
with an artist name. WordPress IDs remain internal provenance only.

The form preserves edits in browser storage where available and can download
`song-urls.json` or a three-column CSV. The JSON adds a `display_title` field;
older two-field downloads still load without clearing entered page titles.
Download the form to keep a portable copy;
loading the JSON restores it. Blank rows are allowed. Invalid, reserved, and
duplicate destinations are flagged before download. Copy the reviewed completed
JSON to `migration/song-urls.json` when preparing a song batch. The user's
completed form was accepted for all 70 songs on 2026-10-21. Later URL changes
need explicit redirects from the already published paths.

The title fields use the same Hangul composer and Hanri candidate controller as
the dictionary and IME. Enable Hangul keyboard is on by default and can be turned
off for Latin titles. Shared scripts load directly from the checkout. The local
`migration/song-ime-data.js` snapshot is generated from the canonical runtime
dictionary when the form or site is built, so candidates work from `file://`
without a server. This generated file is ignored by Git and is never deployed.

## Sources and media

`content/` contains editable content records separated into pages, guides,
literature, songs, and stories. Each record has its public route, language, original URL, source
revision/hash, orthography review status, and HTML body. Original public HTML
snapshots are retained under `migration/wordpress-source/`. The final batch
was fetched fresh from WordPress after the user confirmed it was ready.

`migration/wordpress-map.json` records the exact imported scope and deferred work.
`migration/wordpress-media.json` maps copied WordPress media to stable local files.
Existing `/assets/` audio remains at its current path. Wikimedia pronunciation
examples and the original external links remain external. No assets are deleted.

`tools/import_wordpress.py --download-media` reads the public WordPress API and
can create the initial records. It refuses to overwrite editorial records.
Source refreshes must be reviewed separately. The normal site build is offline
and never contacts or edits WordPress.

`tools/import_wordpress_final.py --song-urls PATH --download-media` imports the
approved final batch. It validates complete source coverage, unique title-based
destinations, and reserved paths before importing. It refuses to overwrite
existing song/story records. User-approved URLs are preserved in the migration
map, and existing content receives link updates without recalculating readings.

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

Manual review: compare lyrics, story paragraphs, ruby layout, YouTube/SoundCloud
playback, guide tables/audio, and illustrations with the WordPress sources.
Chinese-language links should still reach WordPress. Original source links are
retained at each page's foot. Source preservation is verified separately from
the pending full v3.1 editorial audit and subsequent v3.2 work.

## Completion tree

```text
thehokkienlang.github.io/
|-- /                                  Imported: English Home
|-- /about/                            Imported: English About
|-- /learn/                            Imported: four English guides
|   |-- introduction/
|   |-- spelling/
|   |-- tone-sandhi/
|   `-- romanisation/
|-- /songs/                            Imported: 70 approved title URLs
|   `-- translation-notes/             Imported: Lyrics Translation
|-- /read/
|   |-- stories/the-egg/               Imported: English presentation
|   `-- literature/lychee-mirror/      Imported: Tale of the Lychee Mirror
|-- /dictionary/                       Existing shared dictionary
`-- /ime/                              Existing shared IME

Remaining work
|-- Chinese presentations              13 source records, including Chinese Egg
|-- Complete v3.1 editorial audit       Separate from source-preservation checks
|-- Apply approved v3.2 changes         After migration
|-- Content Editor                     Not yet built
|-- TLI rebranding                     Not yet completed
`-- English-Hokkien translator         Not yet built
```

Imported records: 79 of the 92 published WordPress items. Original WordPress
content is retained. GitHub publication/deployment status is recorded separately
from this source inventory. The existing Dictionary Editor remains available;
the Content Editor listed above is a separate future authoring tool.
