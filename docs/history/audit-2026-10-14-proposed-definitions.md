# Approved definition completion and 麵粉粿 correction

All seven previously proposed lexical definitions were applied on 2026-10-14. None of these seven remains unfilled. This completes the previously identified empty Mandarin definitions on lexical rows; intentionally blank structural/override rows are unchanged.

| Entry | English definition | Mandarin definition | Evidence / uncertainty |
|---|---|---|---|
| 挭 | prop up; brace; support | 撐住; 支撐; 支助 | Medium: MOE 楗 lists 挭 as an alternative; sense matched to the recorded reading. |
| 兩角 | twenty cents; two tenths of a monetary unit | 兩角錢; 0.2元 | High for the monetary sense; amount expressed without assuming a national currency. |
| 麵粉粿 | mee hoon kueh; hand-torn wheat-flour noodles | 麵粉粿; 手撕麵片 | High: Wiktionary, MOE 麵粉粿仔 and Singapore food reporting agree on wheat flour and mī-hún-kué. |
| 北陰酆都 | Fengdu Emperor; Taoist ruler of the underworld | 北陰酆都大帝; 道教冥界主宰 | Medium: inferred shortened divine title; verify against the entry's original context. |
| 獄城 | prison fortress; infernal city | 監獄城; 地獄之城 | Medium-low: both prison and religious senses attested; original context unavailable. |
| 心狂 | frenzied; intensely agitated | 心神激動; 狂躁不安 | Medium-low: inferred from 心狂火著 / 心狂火熱; standalone sense needs native-context review. |
| 人願 | a person's wishes; human aspirations | 人的心願; 願望 | Low: compositional inference, supported by 人願 in 天隨人願; no independent Hokkien lexical confirmation. |

Simplified Mandarin equivalents were also filled. These confidence notes distinguish inferred meanings from independently established Hokkien definitions.

## Food spelling and redirects

麵粉粿 (simplified 面粉粿) is the canonical entry for the wheat-flour dish. Its reading is `미훈1궤2`, replacing the rice-based `삐1훈1궤2`. The existing nonstandard-reading correction row preserves old pronunciation input and produces 麵粉粿. A headword lookup alias also makes 米粉粿 find/offer 麵粉粿 in the dictionary and both IMEs. Selecting that candidate commits the correct characters and reading; pasted text is not silently rewritten.

The old Unicode-derived ID remains reserved. The new canonical ID is `U+9EB5_U+7C89_U+7CBF_00`; its food category membership moved with it. The correction-reading row has its own ID and uses the existing correction_alias mechanism.

The [redirect log](dictionary-redirects.md) is generated from [structured redirects](../data/dictionary_redirects.tsv), ordered with the existing Tangliengim reading collation. Runtime headword aliases and the readable log use the same source. Reading corrections are validated against the dictionary TSV; no fictional dates or rationales were assigned to historical corrections.

## Sources

- https://en.wiktionary.org/wiki/麵粉粿
- https://sutian.moe.edu.tw/und-hani/tshiau/?lui=tai_su&tsha=麵粉粿
- https://www.zaobao.com.sg/lifestyle/food/story20240216-1468240
- https://sutian.moe.edu.tw/zh-hant/su/9570/ (楗 / 挭)
- https://sutian.moe.edu.tw/zh-hant/su/3386/ (角)
- https://dict.th.gov.tw/detailPage.aspx?Ca=283&ID=1217 (北陰酆都大帝)
- https://www.shidianguji.com/zh/mid-page/7586053296806068251 (獄城)
- https://hermit.place/zh-TW/canon/x/x21n0384/juan-02/ (religious 獄城)
- https://en.wiktionary.org/wiki/心狂火著
- https://sutian.moe.edu.tw/zh-hant/su/13916/ (心狂火熱)
- https://dict.revised.moe.edu.tw/dictView.jsp?ID=53359&la=0&powerMode=0 (天隨人願)

## Verification

Focused Web and classic IME checks cover literal 米粉粿, the old reading, canonical input, committed characters/readings, dictionary search, and audio lookup. All 60 dictionary tests pass. The audio fixture changes only the first syllable of the food entry (bi to mi) in both regional modes.

The new reading exposed a classic audio segmentation gap: unmarked mi followed by tone-marked hun was combined into one unit. The plain Hanri audio path now uses the existing mark_untoned_audio_units helper already used for mixed Hanri, matching Web playback.

A local release run detected an incomplete copied khor1.wav in the temporary site output. A fresh build passed asset integrity and built-app checks; no source recording was changed. Deployment additionally requires clean Linux and Windows source checks and a fresh Pages build.
