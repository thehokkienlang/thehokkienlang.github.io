# Plan: replace 𨘗 with 嚉 for motion tuì/uì

Drafted 2026-11-21 against commit `df360bf` (main). **Executed 2026-11-22** with
the defaults in [section 7](#7-decisions-for-haru), except D9, which Haru
declined: the guide does not mention the Cantonese meaning of 嚉. The decisions
are listed in section 7. Also changed beyond the plan: `tools/dictionary_schema.py`
now accepts supplementary-plane Hanri in headword redirects, and
`data/dictionary_priority.tsv` gains a 뒤 row that keeps 對 first (D8).

## 1. What the repository does now

The claim to check was that 𨘗 covers source, route, direction and goal. **It
covers source only.** Direction and goal are written 對, and route has no entry
or content anywhere.

### Dictionary (`data/hokkien_hanri_dict.tsv`)

| Line | hanri | reading | english | entry_id |
|---|---|---|---|---|
| 706 | 𨘗 | 뒤 | from; source or origin (tui reading) | `U+28617_01` |
| 1919 | 𨘗 | 위 | from; source or origin | `U+28617_00` |
| 705 | 對 | 뒤 | correct; toward; pair | `U+5C0D_00` |
| 1918 | 對 | 위 | toward; to (regional ui reading) | `U+5C0D_01` |

The v3.2 harmonisation states the split directly: "source 𨘗 from destination 對"
(`docs/history/harmonisation-3.2.md`, line 35). It was confirmed as
"source 𨘗 위3/뒤3, and destination 對 위3"
(`docs/history/harmonisation-3.2-dictionary.md`, line 49).

### Content

All seven 𨘗 tokens in content are source uses, of place or time:

| File | Text | Sense |
|---|---|---|
| `content/songs/song-11143.json` | 𨘗위ˋ-打開始 | source: time ("from the start") |
| `content/songs/song-50.json` (×2) | 𨘗뒤ˋ-少年 | source: time ("from youth") |
| `content/songs/song-9973.json` | 𨘗뒤ˋ-底來 | source: place ("from where") |
| `content/stories/the-egg.story.html` | 𨘗위ˋ-底位 來? | source: place |
| `content/stories/the-egg.story.html` | 𨘗위ˋ-一个所在 來 | source: place |

There is **one destination use** in content, and it is written 對:

| File | Text | Sense |
|---|---|---|
| `content/songs/song-7884.json` | 欲對위ˋ-底去? | goal ("where are you going") |

The other **83 tokens of 對 뒤, in 22 files**, are all non-motion uses. They
stay 對. They fall into three groups:

- addressee or target: 對꽈 坦白, 對릐 真心, 對伊 講, 對你 好
- topic: 對愛情, 對家己的人生
- static facing: 對面吹, 對面沯

The tool that assigns these characters is `tools/content_harmonisation.py`,
lines 268–275:

- 위 before 什物 → 為 (purpose)
- 위 after 欲 → 對 (`user:2026-10-25-destination`)
- every other 위 → 𨘗 (`4.5/57`)
- 뒤 before 少年 or 底來 → 𨘗 (`4.5/57-source-reading-tui`)

## 2. Target convention

**嚉 tuì (variant uì)** is the Southern Min preposition of movement. It covers
the source, route, direction and goal of a movement. **對 tuì** keeps every use
it shares with Mandarin and Cantonese 對.

| Sense | English | Example | Hanri |
|---|---|---|---|
| Source: place | from | 嚉基隆來 | 嚉 |
| Source: time | from, since | 嚉今仔日起, 嚉打開始 | 嚉 |
| Source: person (transfer) | from (someone) | 伊嚉我提錢 | 嚉 |
| Route | via, through, along | 嚉這條路行, 嚉窗仔入來 | 嚉 |
| Direction | towards, this/that way | 嚉遮來, 嚉遐行 | 嚉 |
| Goal (after a verb, or with 欲…去) | to | 行嚉車頭去, 欲嚉底去 | 嚉 |
| Facing (static) | facing | 對面, 對門口坐 | 對 |
| Addressee, target | to (a person) | 對伊講, 對我真好 | 對 |
| Topic | about, regarding | 對籃球無興趣 | 對 |
| Pair, correct, check | pair; right; check | 一對, 有對, 對數 | 對 |

Two tests give the same answer:

1. Does something move from, through or towards X? If so, write 嚉.
2. Would Mandarin need 從, 經 or 往 here instead of 對? If so, write 嚉.

The reading does not decide the character. Both characters are read tuì, and uì
is a variant of the same word.

### Why 嚉

- **Rendering.** U+5689 is in the core Unicode block, so ordinary fonts cover
  it.
  - Unicode sources: GB (GE-2523), HKSCS (H-8BBF), CNS 11643 plane 3
    (T3-5449) and Vietnam.
  - It belongs to IICore (tagged C and H) and encodes in GBK and Big5-HKSCS.
  - It is present in all Noto Sans CJK faces.
  - 𨘗 (U+28617) is a Vietnamese Chữ Nôm character in Extension B, with a single
    Vietnamese source (V0-4559, read *đuổi*). That is why the site needs the
    custom `tli-u28617` font, and why the character breaks outside the site.
- **Design.** The 口 radical marks a colloquial function word, as in 噉. The
  對 component gives the sound and links the character to the 本字.
- **Known clash.** Unihan glosses U+5689 as Cantonese "to swell" (deoi3). The
  word is rare. Not mentioned in the guide (D9).

## 3. Dictionary changes

Follow the Dictionary Update SOP in `AGENTS.md`, preferably through the
Dictionary Editor. It allocates IDs, sorts the file and recaptures baselines.

### 3.1 New rows

The registry has no U+5689 IDs yet, so the editor should allocate `_00` and
`_01`.

| hanri | simplified | reading | mandarin_trad | mandarin_simp | english | corrected | entry_type | entry_id |
|---|---|---|---|---|---|---|---|---|
| 嚉 | 〃 | 뒤 | 從; 經; 往 | 从; 经; 往 | from; via, along; towards, to (of movement) | | lexical | `U+5689_00` |
| 嚉 | 〃 | 위 | 從; 經; 往 | 从; 经; 往 | from; via, along; towards, to (of movement; ui variant) | | lexical | `U+5689_01` |

- `simplified` is 〃 because 嚉 has no separate simplified form. Confirm this
  with the OpenCC `tw2s` converter, as for the Egg draft rows.
- Both English glosses fit the existing length range; the longest current gloss
  is 62 characters.

### 3.2 Changed row

| entry_id | Field | Now | Proposed |
|---|---|---|---|
| `U+5C0D_00` 對 뒤 | english | correct; toward; pair | correct; pair; facing; to (someone); regarding |

### 3.3 Retired rows

Move these rows to `data/dictionary_defunct.tsv` with the editor's **Make
defunct**. Their IDs stay reserved in the registry.

| entry_id | Row | replacement_entry_id |
|---|---|---|
| `U+28617_00` | 𨘗 위 | `U+5689_01` |
| `U+28617_01` | 𨘗 뒤 | `U+5689_00` |
| `U+5C0D_01` | 對 위 "toward; to" | `U+5689_01` (see decision D3) |

### 3.4 Headword redirect

Add a `headword` row to `data/dictionary_redirects.tsv`. This keeps
`/dictionary/𨘗/` links and old typed input working.

| kind | source | source_reading | target_entry_id | reason | sources | date |
|---|---|---|---|---|---|---|
| headword | 𨘗 | 뒤 | `U+5689_00` | Motion tuì/uì now written 嚉 (renders in standard fonts; 𨘗 is an Ext-B Nôm character). | docs/tui-motion-hanri-plan.md | 2026-11-21 |

Then run `python tools/build_redirect_log.py`. Whether a second row is needed
for 위 depends on how the redirect checker treats a headword with two readings.
Test it with `--check`.

### 3.5 Where the full definition lives

The TSV has no usage-note column, and its glosses are short. The sense table in
section 2 therefore needs a home of its own. There are two options:

1. **Recommended for now:** add a "嚉 and 對" section to the spelling guide
   (`content/guides/spelling.json`, with its `zh-hant` and `zh-hans`
   counterparts). It should contain the sense table, the two tests, the uì
   variant and the Cantonese note. Link to it from the 嚉 dictionary page if the
   page template allows links.
2. **Later:** add an optional `note` column to the TSV schema, which would
   follow the schema-change process in `docs/dictionary-tsv-schema.md`. That is
   a larger change, and other entries such as 為/對/嚉 or 共/가 would benefit from
   it too.

## 4. Content changes

All edits replace the Hanri base only. Readings, tone marks and ruby stay as
written.

| File | Change | Count |
|---|---|---|
| `content/songs/song-11143.json` | 𨘗 → 嚉 | 1 |
| `content/songs/song-50.json` | 𨘗 → 嚉 | 2 |
| `content/songs/song-9973.json` | 𨘗 → 嚉 | 1 |
| `content/stories/the-egg.story.html` | 𨘗 → 嚉 | 2 (the `zh-hant` version has no 𨘗) |
| `content/songs/song-7884.json` | 對 → 嚉 in 欲對위ˋ-底去 | 1 (D4) |

The song JSON files hold the text twice, as line `text` and as rendered `body`.
Change both.

**Audit step.** Some motion tuì/uì may still be written in Hangul (위, 뒤) and
never received Hanri. Search for 위 or 뒤 followed by a place word, 遮/遐, 底,
or 來/去/起/過, list the hits for review, and convert only the approved ones.

## 5. Code, fonts and tests

### 5.1 Harmonisation tool (`tools/content_harmonisation.py`, lines 268–275)

- Replace the `𨘗` outputs with `嚉`.
- Change the destination rule (위 after 欲) from `對` to `嚉`.
- Give the changed rules a new label, for example
  `user:2026-11-21-motion-tui`, so later audits can trace them.

### 5.2 Fonts

| Item | Action |
|---|---|
| `tli-content-tc-{400,700}-v1.woff2` | **Must regenerate.** Neither face contains 嚉 now (checked: 1,739 glyphs each). Run `python tools/subset_site_hanri.py NotoSansTC-VF.ttf --menu-source PlangothicP1-Regular.ttf` after the content and TSV edits. The script collects characters from content and the TSV, so it picks up 嚉 and drops 𨘗. |
| `tli-menu-hanri-v1.{woff2,ttf}` | Regenerated by the same command. It has no 嚉 now. |
| `tli-u28617-{400,700}-v1.woff2` | Remove the `@font-face` rules in `apps/content-site/site.css` (lines 59–60) and `shared/web-ime-menu.css` (lines 57–70). Then retire or delete the files (D7). |
| `TLI Menu Hanri` range in `site.css`, line 54 | The `U+20000-28616, U+28618-2EBEF` carve-out can return to `U+20000-2EBEF`. |
| `tangliengim-content-hanri-v2.{woff2,ttf}` and `tools/subset_content_fallbacks.py` | **Leave unchanged.** The extra 𨘗 glyph does no harm and keeps old typed text and the redirect rendering. |
| `assets/fonts/README.md` | Rewrite the "Custom U+28617 Hanri glyph" section (lines 29–39) as a retirement note. Update lines 19 and 158. |
| Desktop Pad | Check that 嚉 renders in the classic Windows Pad with its normal Hanri font. Leave 𨘗 in `FALLBACK_FONT_HANRI_CHARS` (line 149) for old text, or remove it together with the test in 5.3. |

### 5.3 Tests

| File | Change |
|---|---|
| `tests/test_site_harmonisation.py:73` | `'>𨘗<'` → `'>嚉<'` |
| `tests/test_dictionary_harmonisation_v32.py:56` | `('𨘗','위')`, `('𨘗','뒤')`, `('對','위')` → `('嚉','위')`, `('嚉','뒤')`. Line 62 (`is_cjk_char('𨘗')`) can stay as a supplementary-plane check. |
| `tests/test_dictionary_hanri_font.py:70` | Update only if 𨘗 leaves `FALLBACK_FONT_HANRI_CHARS`. |
| `tests/check_hanri_rendering.cjs:10` | Replace `𨘗` with `嚉`, or add it, so the new character is rendering-tested. |
| `tests/fixtures/dictionary-baseline.json`, `tests/fixtures/static-reading-defaults.json` | Recapture through SOP step 6 after reviewing the diff. Do not hand-edit. |

### 5.4 Candidate order

`data/dictionary_priority.tsv` has no rows for 對 or 𨘗, so 뒤 and 위 menus fall
back to the default ordering. After the change, 뒤 offers 對 and 嚉, and 위
offers only 嚉 if D3 retires 對 위. Decide whether 嚉 should outrank 對 under 뒤
(D8). Then recapture both static ranking snapshots.

## 6. Order of work and checks

1. Haru answers section 7.
2. **Dictionary.** Make the editor changes in 3.1–3.3 and add the redirect in
   3.4. Then:
   - run `python -X utf8 tools/validate_dictionary_tsv.py`
   - run `python -X utf8 tools/sort_dictionary_tsv.py --check`
   - run `python -X utf8 tools/build_dictionary_json.py`
   - review the generated diff, then run the three captures (SOP step 6)
3. **Content and tool.** Make the edits in section 4 and 5.1, and do the
   Hangul audit.
4. **Fonts.** Regenerate the subsets (5.2), clean up the CSS and update the
   font README.
5. **Tests and docs.** Update the tests (5.3), then the spelling guide (3.5) and
   the TLI manual §4.5/57, which lives outside the repository.
6. **Release gate.** Run `python -X utf8 tools/check_release.py --source-only`
   until it passes, then `git diff --check`.
7. **Visual check.** Open the four songs, the Egg and `/dictionary/嚉/`. Check
   the 𨘗 redirect and the IME menus for 뒤 and 위. Do this on Windows, Android
   and iOS, with the TLI fonts blocked once, to confirm that system fonts render
   嚉.

## 7. Decisions for Haru

| # | Decision | Default in this plan |
|---|---|---|
| D1 | Approve the two 嚉 rows and their glosses and Mandarin equivalents (3.1). | as drafted |
| D2 | Approve the new 對 `U+5C0D_00` gloss (3.2). | as drafted |
| D3 | 對 위 (`U+5C0D_01`): retire it in favour of 嚉 위, or keep a 위 reading for non-motion 對 (e.g. 對伊講 read uì)? | retire |
| D4 | Convert song-7884's 欲對底去 to 嚉. | yes |
| D5 | Do the time and transfer senses (嚉今仔日起, 伊嚉我提錢) belong under 嚉? | yes |
| D6 | Where the full definition goes: the spelling-guide section now, a TSV `note` column later? | guide now |
| D7 | Delete the `tli-u28617` font files, or keep them as an archived prototype. | keep, unused |
| D8 | Should 嚉 rank above 對 in the 뒤 menu? | no; 對 stays first, since non-motion uses are more frequent in content (83 vs 7) |
| D9 | Mention the Cantonese meaning of 嚉 ("to swell") in the guide. | **no** (Haru, 2026-11-22) |
