# TLI Lyric Timing Companion (local only)

This Edge/Chromium extension links a normal YouTube watch window to the local
lyric timing editor. It does not embed, proxy, download, or rehost video. Owner
embedding restrictions remain in force. It does not change the public song player.

## Install once

1. Open `edge://extensions` in Microsoft Edge.
2. Turn on **Developer mode**, then select **Load unpacked**.
3. Select this `desktop/youtube_companion` folder (not a single file).
4. Restart the local editor using your shortcut, and reload its tab in the same
   Edge profile where you installed this extension.
5. Choose a song, then **Open YouTube window**. Start playback in that window.
6. In the editor, **Mark start**, **Mark end**, and **Go to start** now use that
   window's actual player clock. The window stays separate and can be positioned
   next to the editor. Keep both windows visible while timing.

After editing extension files, use **Reload** on its extension card, reload the
editor tab, and reopen the companion window. You can disable/remove the extension
at any time. Uninstalling does not remove your saved timing files.

## Scope and safety

- Content scripts run only on the local lyric timing URL and `www.youtube.com`.
  The YouTube script stays inactive unless the editor opens a paired watch URL.
- A random 256-bit connection ID pairs one local editor tab, one YouTube tab,
  and one video. Independent editor tabs do not share a clock.
- Only playback time, duration, readiness, and player state cross the bridge.
  No editor authentication token, source lyrics, dictionary data, or files are
  read by the extension. No network requests are made by extension code.
- Session pairings live in browser session storage, not synced or permanent
  storage. Closing the editor removes its pairing. Reloading the editor creates
  a new pairing when the user opens the companion again.
- Switching songs or closing the editor closes its paired YouTube popup too.
  Other YouTube tabs, including a paired tab navigated to unrelated content,
  are not closed. The editor has a single Open YouTube window button; no playback
  mode selection is needed.
- Seeking does not automatically start playback. Marking asks for a fresh clock
  sample, rather than extrapolating a timestamp. Ads, stale clocks, closed windows,
  and navigation to a different video disable timing.
- Ads are detected from YouTube's player DOM classes. YouTube can change its page
  structure; if the bridge stops recognizing the player, update this local
  extension rather than guessing timings.
- The extension cannot overcome watch-page login, age/region restrictions,
  deleted videos, popup blockers, or browser autoplay policies. Use YouTube's
  normal controls and sign-in flow.
- The editor, setup page, and extension live under `desktop/` and are not copied
  by `tools/build_site.py`. Saving still never commits or pushes.

## Checks

`node tests/check_lyric_companion.cjs` uses simulated extension APIs and DOM state
to check pairing, isolation, fresh clock sampling, ads, seeking, popup failure,
and cleanup. `python -m unittest tests.test_site_lyric_timing` includes this check.
Real playback in Edge still needs the manual one-time installation above; mocks
do not certify YouTube availability or musical alignment.
