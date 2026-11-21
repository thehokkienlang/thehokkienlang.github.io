# The Egg: gloss-link dictionary audit

Written 2026-11-21 for item 11 of `docs/the-egg-formatting-plan.md`. Before
gloss links can point to the site's own dictionary, every linked term needs an
entry in `data/hokkien_hanri_dict.tsv`.

**This is a report only. Nothing in the dictionary was changed.** New entries
need Haru's review and must go through the Dictionary Update SOP in
`AGENTS.md`. The Dictionary Editor is preferred.

## Method

1. Took every `a.gloss-link` in `content/stories/the-egg.story.html`, plus the
   footnotes in both language files.
2. Recorded the Hanri base text, the ruby reading, the Lomari `title` and the
   link target.
3. Matched the headword against the TSV `hanri` column, ignoring tone marks.
4. Where the headword exists, compared the Hangul syllables without tones.
   Tones were not compared: the story shows sandhi tones in context, while the
   TSV stores citation tones.

Also checked: `dictionary_redirects.tsv`, `dictionary_defunct.tsv`, and whether
the link target is itself in the dictionary when it differs from the displayed
word.

## Codes

Haru answered R, D and M on 2026-11-21; the last column of each table
records the answer. M items that Haru did not mention are accepted as shown
in the citation-tone column ("v (as shown)"). U items were answered the same way.

Reply with a code and an answer, for example "R1: 홛 is right" or
"M12: citation reading …, gloss truck". The codes are R (reading differs), D (decision
needed), M (missing word) and U (missing word with no link).

## Citation tones (how the column was made)

The "Final syllable in citation tone" column turns the story's reading into
the dictionary's convention: non-final syllables keep their sandhi tone, and
the final syllable takes its citation tone.

- **Word that ends a tone group** (followed by a space, punctuation or the end):
  the final syllable is already in citation tone, so the reading is unchanged.
- **Word joined to the next word:** the final syllable is reversed through
  `shared/tli-sandhi.json` (sandhiToCitation):
  - open syllables: ˉ→ˆ, ˆ→ˋ, ˋ→(no mark)
  - checked syllables: (no mark)↔ˆ
- **(?) marks an ambiguous result.** An unmarked joined open syllable can come
  from citation ˉ or ˊ, so both are shown.

This is an automatic guess. It agreed with the dictionary for about 94% of the
Hanri words that are already in it. Treat it as a starting point for Haru's
reading, not as data.

## Summary

| | Words | Links |
|---|---:|---:|
| Linked words (unique Hanri) | 268 | 371 |
| In the dictionary, same syllables | 157 | |
| In the dictionary, **different syllables** | 4 | |
| **Not in the dictionary** | 107 | |

None of the missing words is a redirect or a defunct entry.

Link hosts: Wiktionary 278 (unique word and reading pairs), 教育部臺灣台語常用詞辭典
(sutian) 3, zh.wikipedia 2, zh.wiktionary 1.

## 1. In the dictionary, but with a different reading

The story's reading may be right and the dictionary may need a second reading
row, or the other way round.

| Code | Word | Story ruby | Final syllable in citation tone | Lomari | Dictionary | Haru (2026-11-21) |
|---|---|---|---|---|---|---|
| R1 | 發生 | 홛ˆ솅ˆ **and** 환ˆ솅ˆ | 환ˆ솅ˆ / 홛ˆ솅ˆ | hoât-siêng / hoân-siêng | 홛1솅1 | Story: 환ˆ솅ˆ is a typo, change it to 홛ˆ솅ˆ. Dictionary unchanged. |
| R2 | 四界 | 시ˋ게 | 시ˋ게 | sì-ke | 시2괴 | Story: change the reading to 시ˋ괴 (matches the dictionary). |
| R3 | 變 | 빌ˋ | 빌 | pìi | 볜 | Dictionary: add a new 變 row with the colloquial reading 빌. Keep 볜. |
| R4 | 坦白 | 탄ˆ볙 | 탄ˆ볙ˆ | thân-piek | 탄1벻1 | Dictionary: the correct reading is 탄ˆ볙ˆ. Change the existing 坦白 row. |

發生 is spelled two ways within the story itself. One of them is probably a
typo.

## 2. Missing words that need a decision first (10)

| Code | Word | Story | Final syllable in citation tone | Link goes to | Question | Haru (2026-11-21) |
|---|---|---|---|---|---|---|
| D1 | 揆一 | 귀읻 (footnote 2) | 귀읻 / 귀읻ˆ | zh.wikipedia | Proper name (Coyett). Add to the dictionary, or keep linking to Wikipedia? | Add 揆一 with the reading 귀읻. |
| D2 | 힏ᄅힻ | tone ꞈ, "Hitler" | ꞈ | zh.wiktionary "Hitler" | Proper name and loanword. Add, or keep an external link? | Add 힏ᄅힻ with the reading 힏ᄅힻˆ. |
| D3 | 痛疼 | 탕ˋ턀 | 탕ˋ턀 | sutian 14334 | Missing. The sutian link could serve as the source for a new entry. | Add 痛疼 (탕ˋ턀). |
| D4 | 專工 | 좐ˉ강ˉ | 좐ˉ강ˆ | sutian 7145 | Missing (as above). | Add 專工 (좐ˉ강ˆ). |
| D5 | 一粒 | 짇럅ˆ- | 짇럅 | Wiktionary 粒 | **粒 is in the dictionary.** Link to 粒 rather than add 一粒? | Add 一粒 (짇럅). |
| D6 | 台 | 대 / 대ˊ | 대ˉ / 대ˊ (?) / 대ˊ | Wiktionary 臺 | 台 exists only inside longer words (台北, 月台). Add 台, or use 臺? | Add 台 with the reading 대ˊ. |
| D7 | 流目滓 | ᄅᅷ빡새ˋ | ᄅᅷ빡새ˋ | Wiktionary 流目屎 | Is the headword 流目滓 or 流目屎? | Add 流目滓 (ᄅᅷ빡새ˋ). Ignore Wiktionary's 流目屎. |
| D8 | 鬆一口氣 | 상ˉ-짇ᄏᅷˆ퀴 | 상ˉ-짇ᄏᅷˆ퀴 | Wiktionary 鬆口氣 | Add the idiom, or 鬆口氣, or both? | Add 鬆一口氣 only. |
| D9 | 等’짇에 | 단ˋ | 단ˋ | Wiktionary 等一下 | The link text is a mixed-script phrase. Add 等一下, or link only 等? | Add 等’짇에 with the reading 단2’짇에 (confirmed). |
| D10 | 霧샇샇 | 뿌ꞈ… | 뿌ꞈ | Wiktionary 霧煞煞 | Is the headword 霧샇샇 (mixed script) or 霧煞煞? | Add 霧샇샇 in mixed script for now; its Hanri needs more research. Reading 뿌샇1샇 (confirmed). |

## 3. Missing words (97)

These are readings as shown in the story. Most carry **sandhi** tones, so they
are not ready to paste into the TSV `reading` column, which needs citation
digits. Haru must give the citation reading for each new row.

Some of these appear only inside longer dictionary entries: 樣 (怎樣, 模樣),
別 (別人, 離別) and 百萬 (一百萬).

| Code | Word | Reading in story | Final syllable in citation tone | Lomari | Uses | Links to | Haru (2026-11-21) |
|---|---|---|---|---|---|---|---|
| M1 | 過身 | 궤ˋ신ˉ | 궤ˋ신ˆ | kuè-sīn | 1 | Wiktionary | v (as shown) |
| M2 | 進前 | 진ˋ졩ˊ | 진ˋ졩ˊ | jìn-jiéng | 1 | Wiktionary | v (as shown) |
| M3 | 行路 | 걀러ˉ | 걀러ˉ | kia̰-lōr | 1 | Wiktionary | v (as shown) |
| M4 | 車禍 | 챠ˉ호ˉ | 챠ˉ호ˉ | chiā-hō | 1 | Wiktionary | v (as shown) |
| M5 | 致命 | 디ˋ뼹ˉ | 디ˋ뼹ˉ | tì-biēng | 1 | Wiktionary | v (as shown) |
| M6 | 救護員 | 규ˋ허완ˊ | 규ˋ허완ˊ | kiù-hor-oán | 1 | Wiktionary | v (as shown) |
| M7 | 盡力 | 진롁ˆ | 진롁ˆ | jin-liêk | 1 | Wiktionary | v (as shown) |
| M8 | 救 | 규 | 규 | kiu | 1 | Wiktionary | v (as shown) |
| M9 | 實在 | 싣재 / 싣재ˉ | 싣재ˉ / 싣재ˉ / 싣재ˊ (?) | sit-jai / sit-jāi | 2 | Wiktionary | v 싣재ˉ |
| M10 | 照實 | ᄌᆤˋ싣 | ᄌᆤˋ싣ˆ | jiàu-sit | 1 | Wiktionary | v (as shown) |
| M11 | 彼陣 | 힏ˆ-준ˉ | 힏ˆ-준ˉ | hît-jūn | 1 | Wiktionary | v 힏ˆ준ˉ. Story: remove the "-" from 힏ˆ-준ˉ. |
| M12 | 貨車 | 훼ˋ챠ˆ | 훼ˋ챠ˆ | huè-chiâ | 1 | Wiktionary | v (as shown) |
| M13 | 拍遨 | 팧ˆ꼬ˊ | 팧ˆ꼬ˊ (?) | phâh-gó | 1 | Wiktionary | v 팧ˆ꼬ˊ |
| M14 | 激心 | 곅ˆ심ˆ | 곅ˆ심ˆ | kiêk-sîm | 1 | Wiktionary | v (as shown) |
| M15 | 來世 | 래세 | 래세 | lai-se | 1 | Wiktionary | v (as shown) |
| M16 | 差不多 | 차ˉ붇ˆ도ˆ | 차ˉ붇ˆ도ˆ | chā-pût-tô | 1 | Wiktionary | v (as shown) |
| M17 | 反應 | 환ˆ옝 | 환ˆ옝 | hoân-yeng | 1 | Wiktionary | v (as shown) |
| M18 | 頭一 | ᄐᅷ짇 | ᄐᅷ짇ˆ | thau-jit | 1 | Wiktionary | v (as shown) |
| M19 | 著迷 | 둏뻬ˊ | 둏뻬ˊ | tioh-bé | 1 | Wiktionary | v (as shown) |
| M20 | 心目 | 심ˉ뻑 | 심ˉ뻑ˆ | sīm-bork | 1 | Wiktionary | v (as shown) |
| M21 | 擔心 | 담ˉ심ˆ | 담ˉ심ˆ | tām-sîm | 1 | Wiktionary | v (as shown) |
| M22 | 完美 | 완삐ˋ | 완삐ˋ | oan-bì | 1 | Wiktionary | v (as shown) |
| M23 | 表面 | ᄇᆤˆ삔 | ᄇᆤˆ삔ˉ / ᄇᆤˆ삔ˊ (?) | piâu-bin | 1 | Wiktionary | v ᄇᆤˆ삔ˉ |
| M24 | 婚姻 | 훈ˉ인ˆ | 훈ˉ인ˆ | hūn-în | 1 | Wiktionary | v (as shown) |
| M25 | 愈來愈 | 뚜ˆ래뚜ˆ- | 뚜ˆ래뚜ˋ | rû-lai-rû | 1 | Wiktionary | v (as shown) |
| M26 | 愧疚 | 퀴ˋ규 | 퀴ˋ규 | khùi-kiu | 1 | Wiktionary | v (as shown) |
| M27 | 天堂 | 톈ˉ덩ˊ | 톈ˉ덩ˊ | thiēn-tóng | 1 | Wiktionary | v (as shown) |
| M28 | 輪迴轉世 | 룬훼좐ˆ세 | 룬훼좐ˆ세 | lun-hue-joân-se | 1 | Wiktionary | v (as shown) |
| M29 | 印度教 | 인ˋ더ᄀᅷ | 인ˋ더ᄀᅷ | ìn-tor-kau | 1 | Wiktionary | v (as shown) |
| M30 | 宗教 | 정ˉᄀᅷ | 정ˉᄀᅷ | jōng-kau | 1 | Wiktionary | v (as shown) |
| M31 | 虛空 | 희ˉ컹ˉ | 희ˉ컹ˆ | hī-khōng | 1 | Wiktionary | v (as shown) |
| M32 | 轉世 | 좐ˆ세 | 좐ˆ세 | joân-se | 3 | Wiktionary | v (as shown) |
| M33 | 白紙 | 벻좌ˋ | 벻좌ˋ | peh-joà | 1 | Wiktionary | v (as shown) |
| M34 | 內心 | 뤠심ˉ | 뤠심ˆ | lue-sīm | 1 | Wiktionary | v (as shown) |
| M35 | 知識 | 디ˋ셱 | 디ˋ셱 | tì-siek | 1 | Wiktionary | v (as shown) |
| M36 | 經驗 | 곙ˉ꺔ˉ | 곙ˉ꺔ˉ | kiēng-giām | 2 | Wiktionary | v (as shown) |
| M37 | 停頓 | 톙둔ˋ | 톙둔 | thieng-tùn | 1 | Wiktionary | v (as shown) |
| M38 | 腳步 | 카ˉ버ˉ | 카ˉ버ˉ | khā-pōr | 1 | Wiktionary | v (as shown) |
| M39 | 握 | 악 | 악 | ak | 1 | Wiktionary | v (as shown) |
| M40 | 肩頭 | 곙ˉᄐᅷˊ | 곙ˉᄐᅷˊ | kiēng-tháu | 1 | Wiktionary | v (as shown) |
| M41 | 想像 | 셩ˆ셩ˉ | 셩ˆ셩ˉ | siông-siōng | 1 | Wiktionary | v (as shown) |
| M42 | 宏偉 | 헝위ˋ | 헝위ˋ | hong-wì | 1 | Wiktionary | v (as shown) |
| M43 | 龐大 | 팡대ˉ | 팡대ˉ | phang-tāi | 1 | Wiktionary | v (as shown) |
| M44 | 人類 | 띤뤼ˉ | 띤뤼ˉ | rin-lūi | 3 | Wiktionary | v (as shown) |
| M45 | 心智 | 심ˉ디 | 심ˉ디 | sīm-ti | 1 | Wiktionary | v (as shown) |
| M46 | 承載 | 솅재ˋ | 솅재 | sieng-jài | 1 | Wiktionary | v (as shown) |
| M47 | 部分 | 버훈ˉ | 버훈ˉ | por-hūn | 1 | Wiktionary | v (as shown) |
| M48 | 手指 | 츄ˆ재ˋ | 츄ˆ재ˋ | chiû-jài | 1 | Wiktionary | v (as shown) |
| M49 | 摸 | 뻥ˉ | 뻥ˆ | bōng | 1 | Wiktionary | v (as shown) |
| M50 | 載具 | 재ˋ구 | 재ˋ구ˉ / 재ˋ구ˊ (?) | jài-ku | 1 | Wiktionary | v 재ˋ구ˉ |
| M51 | 得著 | 딛ˆ-둏- | 딛ˆ-둏ˆ | tît-tioh | 1 | Wiktionary | v (as shown) |
| M52 | 伸輪 | 춘ˉ룬ˊ | 춘ˉ룬ˊ | chūn-lún | 1 | Wiktionary | v (as shown) |
| M53 | 浩大 | 헐대ˉ | 헐대ˉ | horr-tāi | 1 | Wiktionary | v (as shown) |
| M54 | 意識 | 이ˋ셱 | 이ˋ셱 | ì-siek | 1 | Wiktionary | v (as shown) |
| M55 | 淡薄 | 담봏 | 담봏 | tam-poh | 1 | Wiktionary | v (as shown) |
| M56 | 而且 | 띠챨ˆ- | 띠챨ˋ | ri-chiâa | 1 | Wiktionary | v (as shown) |
| M57 | 無數 | 뿌서ˋ | 뿌서 | bu-sòr | 1 | Wiktionary | v (as shown) |
| M58 | 西元 | 세ˉ꽌ˊ | 세ˉ꽌ˊ | sē-goán | 1 | Wiktionary | v (as shown) |
| M59 | 農村 | 렁춘ˆ | 렁춘ˆ | long-chûn | 1 | Wiktionary | v (as shown) |
| M60 | 臭奶呆 | ᄎᅷˋ니ˉ대ˆ | ᄎᅷˋ니ˉ대ˆ | chàu-nī-tâi | 1 | Wiktionary | v (as shown) |
| M61 | 技術 | 기ˉ숟 | 기ˉ숟ˆ | kī-sut | 1 | Wiktionary | v (as shown) |
| M62 | 解釋 | 개ˆ셱 | 개ˆ셱 | kâi-siek | 1 | Wiktionary | v (as shown) |
| M63 | 另外 | 롕꽈 | 롕꽈ˉ / 롕꽈ˊ (?) | lieng-goa | 1 | Wiktionary | v 롕꽈ˉ |
| M64 | 樣 | 율ˉ | 율ˉ | yūu | 1 | Wiktionary | v (as shown) |
| M65 | 理解 | 리ˆ개ˋ | 리ˆ개ˋ | lî-kài | 1 | Wiktionary | v (as shown) |
| M66 | 時空 | 시컹ˆ | 시컹ˆ | si-không | 2 | Wiktionary | v (as shown) |
| M67 | 拄著 | 두ˆ-둏- | 두ˆ-둏ˆ | tû-tioh | 1 | Wiktionary | v (as shown) |
| M68 | 知覺 | 디ˉ각 | 디ˉ각 | tī-kak | 1 | Wiktionary | v (as shown) |
| M69 | 根本 | 군분ˋ | 군분ˋ | kun-pùn | 1 | Wiktionary | v (as shown) |
| M70 | 注意 | 주ˋ이ˋ | 주ˋ이 | jù-ì | 1 | Wiktionary | v (as shown) |
| M71 | 為著 | 위둏- | 위둏ˆ | wi-tioh | 1 | Wiktionary | v (as shown) |
| M72 | 臭酸步 | ᄎᅷˋ승ˉ버ˉ | ᄎᅷˋ승ˉ버ˉ | chàu-sn̄g-pōr | 1 | Wiktionary | v (as shown) |
| M73 | 疑問 | 끼뿐ˉ | 끼뿐ˉ | gi-būn | 1 | Wiktionary | v (as shown) |
| M74 | 合理 | 합리ˋ | 합리ˋ | hap-lì | 1 | Wiktionary | v (as shown) |
| M75 | 創造 | 청ˋ조 / 청ˋ조ˉ | 청ˋ조ˉ / 청ˋ조ˉ / 청ˋ조ˊ (?) | chòng-jo / chòng-jō | 2 | Wiktionary | v 청ˋ조ˉ |
| M76 | 原因 | 꽌인ˆ | 꽌인ˆ | goan-în | 1 | Wiktionary | v (as shown) |
| M77 | 成長 | 솅뎡ˋ | 솅뎡ˋ | sieng-tiòng | 3 | Wiktionary | v (as shown) |
| M78 | 最終 | 줴ˋ졍ˆ | 줴ˋ졍ˆ | juè-jiông | 1 | Wiktionary | v (as shown) |
| M79 | 智者 | 디ˋ쟈ˋ | 디ˋ쟈ˋ | tì-jià | 1 | Wiktionary | v (as shown) |
| M80 | 別 | 받 | 받ˆ | pat | 1 | Wiktionary | v (as shown) |
| M81 | 總算 | 정ˆ승ˋ | 정ˆ승 | jông-sǹg | 1 | Wiktionary | v (as shown) |
| M82 | 明白 | 뼹벻ˆ | 뼹벻ˆ | bieng-pêh | 1 | Wiktionary | v (as shown) |
| M83 | 尻脊 | 카ˉ쟣 | 카ˉ쟣 | khā-jiah | 1 | Wiktionary | v (as shown) |
| M84 | 恭喜 | 경ˉ히ˋ | 경ˉ히ˋ | kiōng-hì | 1 | Wiktionary | v (as shown) |
| M85 | 補 | 버ˆ- | 버ˋ | pôr | 1 | Wiktionary | v (as shown) |
| M86 | 害死 | 해시ˋ | 해시ˋ | hai-sì | 1 | Wiktionary | v (as shown) |
| M87 | 百萬 | 밯ˆ빤 | 밯ˆ빤ˉ / 밯ˆ빤ˊ (?) | pâh-ban | 1 | Wiktionary | v 밯ˆ빤ˉ |
| M88 | 耶穌 | 야서ˆ | 야서ˆ | ya-sôr | 1 | Wiktionary | v (as shown) |
| M89 | 跟綴 | 군ˉ뒈ˋ | 군ˉ뒈 | kūn-tuè | 1 | Wiktionary | v (as shown) |
| M90 | 逐擺 | 닥배ˋ | 닥배ˋ | tak-pài | 1 | Wiktionary | v (as shown) |
| M91 | 加害 | 가ˉ해 | 가ˉ해ˉ / 가ˉ해ˊ (?) | kā-hai | 1 | Wiktionary | v 가ˉ해ˉ |
| M92 | 一件 | 짇걀 | 짇걀ˉ / 짇걀ˊ (?) | jit-kiaa | 1 | Wiktionary | v 짇걀ˉ |
| M93 | 善行 | 셴혱ˊ | 셴혱ˊ | sien-hiéng | 1 | Wiktionary | v (as shown) |
| M94 | 成做 | 쟐죄ˋ | 쟐죄 | jiaa-joè | 1 | Wiktionary | v (as shown) |
| M95 | 面目 | 삔뻑ˆ | 삔뻑ˆ | bin-bôrk | 1 | Wiktionary | v (as shown) |
| M96 | 同類 | 덩뤼ˉ | 덩뤼ˉ | tong-lūi | 1 | Wiktionary | v (as shown) |
| M97 | 胎兒 | 태ˉ띠ˊ | 태ˉ띠ˊ | thāi-rí | 1 | Wiktionary | v (as shown) |

## 4. Ruby words with no gloss link that are also missing (6)

These don't block item 11, but they are gaps in the same story:

- U1: 抑是 (앟시, used 5 times) → citation 앟시 / 앟시ˉ / 앟시ˊ (?) — **Haru:** v 앟시ˉ
- U2: 一口氣 (짇ᄏᅷˆ퀴) → citation 짇ᄏᅷˆ퀴 — **Haru:** v (as shown)
- U3: 按 (안ˆ-) → citation 안ˋ — **Haru:** v (as shown)
- U4: 怎 (좔ˆ-) → citation 좔ˋ — **Haru:** v (as shown)
- U5: 為둏 (위둏) → citation 위둏ˆ — **Haru:** Story: write it 為著 (no new row; 為著 is in section 3).
- U6: 為’둏 (위ˉ) → citation 위ˆ — **Haru:** Add 為’둏 with the reading 위ˉ’둏.

The last two look like spelling variants of 為著. Check them against 為著 (위둏-),
which is also missing (section 3).

Of the 78 ruby-annotated Hanri words in the story with no link, 72 are already
in the dictionary.

## Actions from Haru's answers (2026-11-21)

### Story text (`content/stories/the-egg.story.html`)

- R1: in 發生, change 환ˆ솅ˆ to 홛ˆ솅ˆ.
- R2: in 四界, change 시ˋ게 to 시ˋ괴.
- M11: in 彼陣, change 힏ˆ-준ˉ to 힏ˆ준ˉ.
- U5: change the 為둏 spelling to 為著, keeping the ruby reading.

### Dictionary (`data/hokkien_hanri_dict.tsv`, via the Dictionary Update SOP)

- **Change** R4: 坦白 becomes 탄1볙1 (from 탄1벻1).
- **Add** new rows:
  - R3: 變 빌, a second, colloquial row
  - D1: 揆一 귀읻
  - D2: 힏ᄅힻ 힏ᄅힻˆ
  - D3: 痛疼
  - D4: 專工
  - D5: 一粒
  - D6: 台 대ˊ
  - D7: 流目滓
  - D8: 鬆一口氣
  - D9: 等’짇에
  - D10: 霧샇샇
  - all 97 M words, with the readings in the table
- Store readings as digits. The final syllable is citation tone, and an
  unmarked final syllable is tone 3 (no digit).

### Settled on 2026-11-21

- D9: reading 단2’짇에. D10: reading 뿌샇1샇.
- U1: 앟시ˉ. U2–U4: as shown. U6: add 為’둏 (위ˉ’둏).
- U5: in the story, write 為둏 as 為著. The 為著 row comes from section 3.
- Glosses: drafted for review in `docs/the-egg-new-entries-draft.md`.

## Next steps

1. Haru decides the section 1 readings and the section 2 questions.
2. Haru supplies citation readings and glosses for the section 3 words. Add
   them with the Dictionary Editor, then follow the Dictionary Update SOP: sort,
   build, review, recapture the three baselines and run `--source-only`.
3. Rerun this audit. Item 11 (the choice of link target, and the
   `gloss-link-nowrap` consistency) can go ahead once sections 1–3 are clear.
