# Structured song editor

The local Song Editor is available from **Tangliengim Editors**. It writes a
structured `songEditor` source block and generates the public song HTML from
that data. Ruby readings and Lomari therefore use the same converter as the
Local IME; authors do not edit lyric HTML.

Each lyric row accepts TLI mixed text and can be moved, removed, or marked
**Grey out**. Grey rows are parenthesized and use the muted lyric treatment
established by `金包銀`. Verse breaks remain separate structured rows.

**Save locally** updates the song JSON, song category, canonical song URL list,
and content manifest without committing. **Publish to GitHub** saves first,
runs the complete website validation, commits only the song's canonical source
files, and pushes with the existing Git credentials.

Only songs created by this editor reopen as structured records. Older songs are
left in their existing HTML form because reconstructing citation tones and
authoring choices from rendered ruby would be lossy.
