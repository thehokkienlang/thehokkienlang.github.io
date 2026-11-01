# Sentence-synchronised lyrics: local pilot

The pilot is **生份’에 릐ˋ**, `content/songs/song-11533.json`, tied to its existing
YouTube video `HNYkSBkQ33Y`. No source lyric paragraphs, ruby readings, dictionary
rows, or harmonisation audits are modified. Generated lyric paragraphs receive
IDs; `data/lyric-timings/song-11533.json` contains timings and lyric fingerprints.

## Open and time a song

1. Launch the local Website Editor with `npm run editor`, or run
   `python desktop/website_editor.py` from the repository.
2. Open **Website Pages**, select the song, and choose **Lyric timing**.
3. Choose a song with the **Song** menu, then use **Open YouTube window**.
   Select the sentence, press **Mark start** as singing
   begins, then **Mark end** when it finishes. The next sentence is selected
   automatically unless that option is unchecked. Times can also be entered in
   seconds with decimals, cleared, or adjusted manually. **Go to start** seeks
   the video to the selected sentence.
4. Use **Highlight preview** to inspect the selected real lyric block; this is
   a visual demonstration, not a claim that the sentence is currently sung.
5. **Save timings locally** saves only the sidecar. It never commits or pushes.
   Leave status as **Draft** during timing. **Reviewed** requires every sentence
   to have a complete, ordered, non-overlapping start/end pair.

## Recordings that prohibit embedding

The local editor uses a companion YouTube watch window, not an embedded player.
Use **Companion setup** in the editor to install the local Edge extension from
`desktop/youtube_companion` once, then reload the editor in the same Edge profile.
Click **Open YouTube window** and press Play in the normal watch window. The local
extension sends that video's clock to the editor for marking and seeking; it
never downloads or rehosts video, and never bypasses embedding restrictions.
Marking pauses during advertisements and lost connections. Setup details,
permissions, limitations, and checks are in `desktop/youtube_companion/README.md`.
The companion is for the local editor only: it does not fix restricted embeds
on the public website. Real timing still needs listening/review.

## Preview and publication

Build with `python tools/build_site.py`. Timed draft cues are active on public
song pages by the project owner's decision; the status is not a publication gate.
Incomplete or estimated draft timing is not a claim of listening verification.

The public player polls YouTube's actual clock, including when paused so seeks
are reflected. It never guesses elapsed time or initiates playback by itself.
Clicking a timed lyric seeks and starts playback. Highlighting holds through gaps
until the next timed sentence, and clears when playback ends. A pale teal
background and accent change no lyric/ruby dimensions. **Follow lyrics** scrolling
is opt-in and mobile-only; reduced-motion preferences disable smooth scrolling. Player failure leaves
the original readable lyric blocks intact. Native full-screen playback cannot
show the surrounding website lyrics; inline playback is needed to see them.

Changes to video identity, lyric order, or lyric readings invalidate timing
fingerprints instead of silently moving cues to different sentences. Repeated
verses have separate occurrence IDs. Concurrent edits to either the source page
or its timing sidecar are rejected by the local editor's revision checks.

The timing UI uses the existing localhost-only, token-protected CMS API and is
excluded from public builds. Review changes, validate, and commit/push separately
in the CMS after approving the recording alignment and visual preview.

## Checks

- `python -m unittest discover -s tests -p test_site_lyric_timing.py`
- `node tests/check_lyric_clock.cjs`
- `python tools/build_site.py`

The automated tests use synthetic cue times for boundaries, gaps, pauses,
backward seeks and draft visibility. They do not certify real musical alignment.
Real YouTube playback, timing precision, native mobile fullscreen, and a physical
iPhone/Android device need manual verification before publication.
