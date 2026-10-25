# The Egg Presentations

The Egg publishes at these equivalent routes:

- English: `/read/stories/the-egg/`
- Traditional Chinese: `/zh-hant/read/stories/the-egg/`
- Simplified Chinese: `/zh-hans/read/stories/the-egg/`

All three use **卵** with **능ˉ** as the main title's ruby. The smaller body
heading is **The Egg** in English and **蛋** in both Chinese presentations.
The title reading comes from the existing authored header, not a dictionary
guess. The existing title/ruby renderer supplies its styling.

The Traditional page's SoundCloud player is the recording source for all three
presentations (track `2352652016`). The broken English track `2325470030` is
replaced only when rendering. Original WordPress snapshots and audited body
hashes remain intact.

The Simplified page derives from the current, harmonised Traditional source on
each build, using the repository's pinned OpenCC conversion. Conversion affects
visible Hanri text, not Hangul, tone marks, Lomari, URLs, attributes, pronunciation
ruby, code, or scripts. The content manifest explicitly records `derivedFrom`;
the page is not misrepresented as a separately imported WordPress original.

Edit `content/zh-hant/stories/the-egg.json` for shared Chinese content corrections.
There is no second Simplified body to synchronise. The language menu, alternate
links, reading index and homepage point to the corresponding language route.
