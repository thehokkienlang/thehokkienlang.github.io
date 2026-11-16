# Song categories: sound and mood

Status: approved by Haru on 2026-11-16 and implemented (steps 1 to 6, one
commit each, not yet pushed). Every sound, mood and dialect value in this plan is
**editorial data** that Haru chose. Any later change to one needs Haru's
review.

## Why

`/songs/` has 11 categories for 80 songs (`content/song-categories.json`).
They mix four different ways of sorting:

- **era:** Modern, Golden, Vintage
- **mood:** Midnight, Feel-Good, Playful, After-Dark
- **style:** Rock, Urban Ballads
- **dialect:** Teochew

So a song's place is hard to guess. Three categories are all "Classics"
(熱播金曲, 經典金曲, 夜愁金曲), and one category has a single song.

## Why not era by year

An earlier draft worked out each song's era from its release year. It was
dropped (2026-11-16) for two reasons:

- **Songs sound older or newer than their year.** 家後 (2001) and 夜市人生
  (2010) sound classic, while 向前行 (1990) and 志明佮春嬌 (1999) sound modern.
  The two styles overlap from about 1990 to 2010, so no boundary year
  separates them.
- **Years take a lot of work to verify.** Some songs have no reliable release
  year at all.

What a listener wants from "era" is the kind of sound, so the plan sorts by
that directly. **No year is stored or shown.** It can be added later without
changing anything here.

## The model

Each song gets:

| Field | Values | Meaning |
|---|---|---|
| `sound` | one id from the sound list | Which generation of music the song sounds like. Chosen by hand, never worked out from a date. |
| `moods` | 1 or 2 ids from the mood list | How the song feels. |
| `dialect` | optional, `"teochew"` | Shows a 潮汕 badge on the song. Not a category. |
| `singer` | optional text, e.g. `"江蕙"` | Who sings the recording on the page. Shown on the page when present. Each version of a song has its own singer, shown inside that version's tab. Where only one singer can show (a list row, a search result), it is the original's. |

### Sounds (new `content/song-sounds.json`)

The sound list is fixed. The labels have no year ranges, so no label can be
wrong about a song.

| id | EN | 繁 | 简 | What belongs here |
|---|---|---|---|---|
| `roots` | Roots | 傳統源聲 | 传统源声 | Folk songs and early classics (天烏烏, 望春風, 燒肉粽). |
| `classic` | Classic | 經典金曲 | 经典金曲 | The classic Hokkien pop sound, whatever the year (江蕙, 陳雷, 翁立友, 王識賢). |
| `modern` | Modern | 當代流行 | 当代流行 | Band, indie and new-style pop, from 向前行 onwards (茄子蛋, 椅子樂團, 珂拉琪). |

The test for a song is **how it sounds, not when it came out**. A new song in
the classic style is Classic. An older song that started the new style is
Modern.

### Moods (new `content/song-moods.json`)

The mood list is fixed. A new mood is a deliberate edit to this file, never
made up for one song. Each song has at most 2 moods.

The list follows the usual way music research sorts mood: by whether a song
is positive or negative, and whether it is high or low in energy. That gives
four moods. Three more were added for songs the four don't describe (Haru,
2026-11-16).

| id | EN | 繁 | 简 | Feeling |
|---|---|---|---|---|
| `upbeat` | Upbeat | 輕快 | 轻快 | Positive, high energy: fun, playful, danceable. |
| `heartfelt` | Heartfelt | 暖心 | 暖心 | Positive, low energy: warm, tender, grateful. |
| `melancholy` | Melancholy | 傷感 | 伤感 | Negative, low energy: sad, lonely, heartbroken. |
| `intense` | Intense | 激昂 | 激昂 | Negative, high energy: angry, fierce, dark. |
| `spirited` | Spirited | 勵志 | 励志 | Rousing and confident: striving, never giving up. |
| `lyrical` | Lyrical | 抒情 | 抒情 | Calm, reflective and controlled: neither clearly happy nor clearly sad. |
| `romantic` | Romantic | 浪漫 | 浪漫 | Sweet love songs that are neither sad nor family-themed. |

Each mood has an accent colour, like the categories have today.

- **Lyrical is the middle ground.** Use it when no stronger mood fits. A song
  that is clearly sad is Melancholy, even if it is slow.
- **"Late night" and "Rock" are not moods.** One names a time of day and the
  other a style, so neither is in the list.

## How it behaves

### `/songs/`

- **Sections are sounds**, in this order: Modern, Classic, Roots. Every
  song appears exactly once.
- **Two rows of chips** above the list:
  - **Sound:** All, Roots, Classic, Modern. This narrows the list to one
    section.
  - **Mood:** All, Upbeat, Heartfelt, Melancholy, Intense, Spirited, Lyrical,
    Romantic. This shows only songs with that mood, still grouped by sound.
- **The filters combine**: Melancholy + Classic shows the classic sad songs. Search combines with both.
- **Each song row** shows the singer, if the song has one (the original's,
  for a song with versions), its mood chips and, if it has one, the 潮汕 badge.
  Clicking a mood chip on a row applies that mood filter.
- **Order within a section:** by the Hangul reading of the title, in jamo
  order (see "Song order" below). This is how each category is sorted today.
- **Links:** `?sound=…&mood=…&q=…` are all kept in the address bar, so a
  filtered list can be shared.
- **Empty result:** "No songs match", plus a "Clear filters" button.
- **Search ranking:** unchanged. Title matches come first, and the section with
  the closest match moves to the top while searching.

### Song pages

- **Sub-header breadcrumb:** `Songs › <Sound>`, linking to `/songs/?sound=…`.
- Under the title: the **singer**, if the song has one (on a page with
  version tabs, each tab shows its own version's singer), then the song's
  **mood chips** (each linking to
  `/songs/?mood=…`) and the 潮汕 badge if it has one.
- **Search dropdown:** each result shows `<singer> · <sound> · <mood>` under
  the title (the singer only if there is one),
  in place of today's category.

### Site search (`/search/`)

No change, apart from song results showing `<singer> · <sound> · <mood>` (the
singer only if there is one) where they show the category today.

## Colours and wording

**Colours** reuse today's category colours (accent, tint, tint end), so the
page keeps its look. They are easy to change later.

| New | Takes the colours of | Accent | Tint | Tint end |
|---|---|---|---|---|
| Modern (section) | Modern & Contemporary | `#247b76` | `#c9f2e6` | `#d7eaff` |
| Classic (section) | Golden Classics | `#986d2b` | `#ffe2a9` | `#f8c9a5` |
| Roots (section) | Vintage Roots | `#6b7350` | `#e8e7bd` | `#d2e9d1` |
| Upbeat | Playful Beats | `#a5546b` | `#ffd7e4` | `#ffe2c2` |
| Heartfelt | Feel-Good Favourites | `#5d7850` | `#d8f1d1` | `#f5edb8` |
| Melancholy | Midnight Musings | `#40566f` | `#d8e4f5` | `#e6dcf2` |
| Intense | Rock Anthems | `#843e45` | `#f2cbd0` | `#e2d0e5` |
| Spirited | Popular Classics | `#ad5a4d` | `#ffd8cf` | `#ffe9b9` |
| Lyrical | Urban Ballads | `#53698f` | `#d9e5ff` | `#eadcff` |
| Romantic | After-Dark Classics | `#675271` | `#e6d4ee` | `#d1dff0` |
| 潮汕 badge | Voice of Teochew | `#3f718b` | `#cdeef5` | `#dbe5ff` |

**Interface wording** (new text only; "All", "No songs match." and the song
count already exist in three languages):

| EN | 繁 | 简 |
|---|---|---|
| Sound | 曲風 | 曲风 |
| Mood | 心情 | 心情 |
| Clear filters | 清除篩選 | 清除筛选 |
| Teochew (the badge) | 潮汕 | 潮汕 |

## Old links

Map each old `?category=` id so bookmarked links still land somewhere close:

| Old id | Becomes |
|---|---|
| `modern`, `urban` | `?sound=modern` |
| `rock` | `?sound=modern&mood=intense` |
| `golden`, `popular` | `?sound=classic` |
| `after-dark` | `?sound=classic&mood=melancholy` |
| `midnight` | `?mood=melancholy` |
| `feel-good` | `?mood=heartfelt` |
| `playful` | `?mood=upbeat` |
| `vintage` | `?sound=roots` |
| `teochew` | all songs, Teochew badge visible (no filter) |

The mapping lives in one small table in `site.js`. The address bar is rewritten
to the new form with `history.replaceState`.

## Steps

Each step is one commit. Steps 1 and 2 are editorial, and nothing visible
changes until step 3.

1. **Data files.**
   - Add `content/song-sounds.json` and `content/song-moods.json` with the
     labels above.
   - Add `sound`, `moods`, `dialect` and `singer` to each song file, using the values in
     "Song data" below.
   - The 11 categories stay in use until step 3.
2. **Checks.** Extend `tools/check_site.py` so that:
   - every song has one sound and 1–2 moods from the lists (a singer is
     optional)
   - unknown sound or mood ids fail
   - the build prints the song count per sound and per mood
3. **Build and `/songs/`.**
   - `tools/build_content.py` builds the sound sections and both chip rows
     from the new data, instead of `song-categories.json`.
   - `public/data/song-search-index.json` gets `sound`, `moods`, `dialect` and
     `singer`
     in place of `category`.
   - `site.js` gets the combined sound, mood and search filtering, the
     `?sound` and `?mood` links, and the old-id mapping.
4. **Song pages and dropdown.** Add the breadcrumb sound, the singer and the
   mood chips under the title, the dropdown's `<singer> · <sound> · <mood>` line and the 潮汕 badge.
5. **Song Editor.** Replace the Category field with sound, mood (pick 1–2
   from the list), dialect and singer fields in `desktop/website_editor_ui/song-editor.js` and
   `tools/website_editor_service.py`, so new songs get them when they are
   saved. A song's saved `songEditor.category` value is dropped the next time
   it is saved.
6. **Clean-up.**
   - Remove `content/song-categories.json`. Its readers are
     `tools/build_content.py`, `tools/website_editor_service.py`,
     `tests/test_website_editor.py`, `tests/test_wordpress_migration.py` and
     `docs/website-editor.md`.
   - Update `tests/test_site_*.py` and the site checks.
   - Run the release gate per `AGENTS.md`.

Every step is checked in all three languages, at desktop and phone width.

## Song order

Sections come first (Modern, Classic, Roots). Within a section, songs are
sorted by the Hangul reading of their title, in Tangliengim jamo order:

- **Initials:** ㄱ ㄲ ㄴ ㄷ ㄸ ㄹ ㅁ ㅂ ㅃ ㅅ ㅇ ㅈ ㅉ ㅊ ㅋ ㅌ ㅍ ㅎ ㆆ
- **Vowels, within each initial:** ㅏ ᅟᅷ ㅐ ㅑ ᅟᆤ ㅓ ㅔ ㅕ ㅖ ㅗ ㅘ ㅙ ㅚ ㅛ ㅜ ㅞ ㅟ ㅠ ㅡ
  ᅟힻ ㅢ ㅣ

This is the order `tools/tangliengim_collation.py` already defines, and the
build already sorts each of today's categories with it
(`song_sort_reading` and `reading_sort_key`). Step 3 keeps that sort and
applies it within the three sound sections; no new sorting code is needed.

A song whose title has no Hokkien reading (你啊你啊 and 敢傻敢衝, which have
Mandarin titles) goes at the end of its section, as it does today.

The rule gives this order (worked out on 2026-11-16 from the titles as they
are now; the build is the authority, so the lists below are for reference):

**Modern (34):** 곻愛릐一擺, 月下煮茶, 恬恬에夢, 浪溜嗹, 浪子回頭, 蓮花空行身染愛, 메삐메삐, 門, 菝仔, 保庇, 萬千花蕊慈母悲哀, 無眠, 寫一條歌寫릐꽈爾爾, 傷心地獄芳花引魂, 水, 身騎白馬, 心花開, 愛情릐比꽈想에곻較偉大, 에흐로때디, 食飽’쀄, 總有一工, 足芳足芳, 姊妹仔, 志明佮春嬌, 一吋相思一吋淚, 這款自作多情, 請問릐감欲做꽈에ᄁힻ흐뗀, 生份에릐, 手捧一杯酒, 헤비運將情歌, 向前行, 魚仔, 你啊你啊, 敢傻敢衝

**Classic (43):** 家後, 堅持, 金包銀, 꽈問天, 台灣話, 浪子에心情, 落雨聲, 媽媽歌星, 爸囝情深, 夢中’에情話, 迷魂芳, 聲聲叫됴릐, 世界第一等, 上媠에花, 雪中花, 小雨, 小雨傘, 惜別에海岸, 隨緣, 失落에夢, 阿媽에話, 愛徦無命毋知驚, 愛릐無條件, 愛拚才會贏, 애요애요애애요, 愛情에騙子꽈問릐, 愛情一陣風, 愛情챻챻, 夜市人生, 有影뽀, 再會랗心愛에無緣에人, 情難忘, 酒後에心聲, 一人一半感情𣍐散, 春夏秋冬, 跤踏車, 靠站, 飄浪에人, 雨水꽈問릐, 風真透, 反背, 歡喜就好, 雲中月圓

**Roots (3):** 望春風, 燒肉粽, 天烏烏

## Song data

Haru chose and confirmed these values on 2026-11-16, using
`docs/song-categories-picker.html`.

- No song has a second mood so far.
- **Singer** is the value for the new `singer` field. Entries that aren't a
  singer's name ("folk song", "Singapore army song") are left out, so those
  pages show no singer.

| Song | Singer | Sound | Mood |
|---|---|---|---|
| 向前行 | 林強 | Modern | spirited |
| 浪溜嗹 | 茄子蛋 | Modern | intense |
| 敢傻敢衝 | 茄子蛋 | Modern | spirited |
| 곻愛릐一擺 | 茄子蛋 | Modern | intense |
| 헤비運將情歌 | 茄子蛋 | Modern | melancholy |
| 一吋相思一吋淚 | 麗小花 | Modern | melancholy |
| 寫一條歌寫릐꽈爾爾 | 蕭煌奇 feat. 茄子蛋 | Modern | lyrical |
| 愛情릐比꽈想에곻較偉大 | 茄子蛋 | Modern | intense |
| 魚仔 | 盧廣仲 | Modern | romantic |
| 志明佮春嬌 | 五月天 | Modern | lyrical |
| 身騎白馬 | 徐佳瑩 | Modern | intense |
| 你啊你啊 | 魏如萱 | Modern | melancholy |
| 門 | FunkyMo | Modern | lyrical |
| 에흐로때디 | 椅子樂團 | Modern | lyrical |
| 手捧一杯酒 | 椅子樂團 | Modern | lyrical |
| 메삐메삐 | 椅子樂團 | Modern | lyrical |
| 總有一工 | 理想混蛋 | Modern | heartfelt |
| 家後 | 江蕙 | Classic | heartfelt |
| 堅持 | 翁立友 | Classic | spirited |
| 꽈問天 | 翁立友 | Classic | intense |
| 小雨傘 | 洪榮宏 | Classic | upbeat |
| 愛情챻챻 | 陳小雲 | Classic | upbeat |
| 歡喜就好 | 陳雷 | Classic | upbeat |
| 愛拚才會贏 | 葉啟田 | Classic | spirited |
| 酒後에心聲 | 江蕙 | Classic | melancholy |
| 無眠 | 蘇打綠 | Modern | melancholy |
| 落雨聲 | 江蕙 | Classic | melancholy |
| 浪子回頭 | 茄子蛋 | Modern | intense |
| 阿媽에話 | 蕭煌奇 | Classic | melancholy |
| 生份에릐 | 椅子樂團 | Modern | melancholy |
| 再會랗心愛에無緣에人 | 施文彬 | Classic | melancholy |
| 跤踏車 | 王識賢 | Classic | heartfelt |
| 恬恬에夢 | 椅子樂團 | Modern | heartfelt |
| 姊妹仔 | 旺福 | Modern | lyrical |
| 心花開 | 李千娜 | Modern | heartfelt |
| 食飽’쀄 | 旺福 | Modern | upbeat |
| 水 | 李竺芯 | Modern | upbeat |
| 保庇 | 王彩樺 | Modern | upbeat |
| 足芳足芳 | 李竺芯 | Modern | upbeat |
| 애요애요애애요 | Singapore army song | Classic | upbeat |
| 愛情에騙子꽈問릐 | 陳小雲 | Classic | upbeat |
| 請問릐감欲做꽈에ᄁힻ흐뗀 | 茄子蛋 | Modern | upbeat |
| 菝仔 | FunkyMo | Modern | upbeat |
| 萬千花蕊慈母悲哀 | 珂拉琪 | Modern | intense |
| 傷心地獄芳花引魂 | 珂拉琪 | Modern | intense |
| 蓮花空行身染愛 | 珂拉琪 | Modern | intense |
| 這款自作多情 | 茄子蛋 | Modern | intense |
| 世界第一等 | 劉德華 (original); 伍佰 version | Classic | spirited |
| 小雨 | 林玉英 | Classic | lyrical |
| 隨緣 | 陳雷 | Classic | melancholy |
| 金包銀 | 蔡秋鳳 | Classic | intense |
| 台灣話 | 陳雷 | Classic | upbeat |
| 雪中花 | 王識賢 & 孫淑媚 | Classic | romantic |
| 有影뽀 | 陳雷 | Classic | upbeat |
| 風真透 | 陳雷 | Classic | upbeat |
| 爸囝情深 | 何坤 | Classic | heartfelt |
| 夜市人生 | 翁立友 | Classic | heartfelt |
| 雲中月圓 | 王識賢 & 孫淑媚 | Classic | romantic |
| 愛情一陣風 | 陳百潭 | Classic | lyrical |
| 惜別에海岸 | 江蕙 | Classic | melancholy |
| 浪子에心情 | 葉啟田 | Classic | lyrical |
| 一人一半感情𣍐散 | 小黑 (Malaysian cover) | Classic | lyrical |
| 夢中’에情話 | 阿杜 & 江蕙 | Classic | melancholy |
| 迷魂芳 | 翁立友 | Classic | melancholy |
| 情難忘 | 王識賢 | Classic | melancholy |
| 媽媽歌星 | 江蕙 | Classic | melancholy |
| 失落에夢 | 陳雷 | Classic | melancholy |
| 春夏秋冬 | 蔡小虎 | Classic | melancholy |
| 飄浪에人 | 陳雷 | Classic | melancholy |
| 聲聲叫됴릐 | 陳雷 | Classic | melancholy |
| 愛릐無條件 | 黃乙玲 | Classic | melancholy |
| 雨水꽈問릐 | 蔡秋鳳 | Classic | melancholy |
| 愛徦無命毋知驚 | 王識賢 | Classic | melancholy |
| 上媠에花 | 蕭煌奇 | Classic | melancholy |
| 靠站 | 陳雷 | Classic | melancholy |
| 反背 | 王識賢 | Classic | melancholy |
| 燒肉粽 | 郭金發 | Roots | lyrical |
| 天烏烏 | folk song | Roots | upbeat |
| 望春風 | 純純 (original); 鳳飛飛 version | Roots | melancholy |
| 月下煮茶 | 陈佳 | Modern | lyrical (dialect: teochew) |

Notes:

1. **Sounds**, of the 80 categorised songs: Roots 3, Classic 43,
   Modern 34.
2. **Moods:** Melancholy 26, Upbeat 15, Lyrical 13,
   Intense 11, Heartfelt 7, Spirited 5, Romantic 3.
3. **Songs with versions** are one page with a tab per version, so they
   appear once in the list. The page opens on the original version, and the
   song's sound, mood and singer follow the original:
   - 望春風 (`/songs/望春風/`): the original, then 鳳飛飛's version.
   - 世界第一等 (`/songs/世界第一等/`): 劉德華's original (added 2026-11-16),
     which is Classic, then 伍佰's version.

   The other version's file (`songVersion` with a different `route`) is never
   a page or a list row of its own. No change to the list is needed for this.

## Decisions (Haru, 2026-11-16)

1. **Labels:** all three sound labels and seven mood labels are approved as
   written, in English and Chinese.
2. **Section order:** Modern first, then Classic, then Roots.
3. **Order within a section:** jamo order of the title's Hangul reading (see
   "Song order").
4. **Versions:** a song with two versions is listed once and follows its
   original. 鳳飛飛's 望春風 and 伍佰's 世界第一等 get no row of their own.
5. **Song data:** every sound, mood and singer in the table above is
   confirmed.

Still open (optional, blocks nothing):

- **Second moods:** none are assigned; add them later where they fit.
