# Mandarin lookup second-pass review

## Method

Reviewed the 1,698 formerly unresolved lexical/input entries and 10 non-lexical numeral rows. Existing populated Mandarin pairs were preserved.

Primary reference: [English Wiktionary](https://en.wiktionary.org/), accessed 2026-10-04. Public MediaWiki revisions were checked for all 1,594 unique unresolved Hanri-only expressions (1,392 pages available; 202 missing). Existing Hokkien readings, English, entry types and related lexical context were also reviewed. No reference archive is a runtime dependency.

Chinese etymology/pronunciation blocks were considered separately: Mandarin pronunciation in one block does not authenticate a Min-only sense in another. Dialect-only labels were not used as Mandarin attestation. Literary/regional Mandarin meanings remain eligible. Traditional/Simplified pointer pages or missing evidence were handled with lexical context, not automatically classified LOW.

HIGH means a reviewed compatible shared Mandarin sense. MEDIUM includes clear Hokkien-to-Mandarin equivalents and shared expressions with coverage gaps, register differences, or noisy component-generated English. Those are populated and optional spot-checks, not failures. A compatible relevant sense is sufficient; unrelated secondary senses and exact English phrasing are not gates.

The versioned manifest records reviewed decisions by existing entry_id, guarded by headword, reading, type and English. It is a one-time audit, not a general rule copying arbitrary future Hanri into Mandarin. Source links and revision IDs document the checked pages; missing/redirect-only coverage does not imply Mandarin attestation. Wiktionary text is not copied into the TSV.

Mandarin Simplified uses the existing pinned OpenCC t2s converter. This completion tool changes only the two Mandarin columns. Separately, user-authorized English corrections and completed manual reviews are recorded with exact old/new values and references in [english-gloss-corrections.json](english-gloss-corrections.json). Completed review-sheet merges are logged in [mandarin-manual-review-completion.json](mandarin-manual-review-completion.json). The reviewed manifest guards the current English values. Hokkien simplified, IDs, order, Hanri/readings, correction aliases and priorities remain unchanged.

## Counts

| Metric | Rows |
| --- | ---: |
| MEDIUM | 935 |
| LOW | 13 |
| HIGH | 750 |
| NOT_APPLICABLE | 10 |
| examined | 1708 |
| new_trad_ditto | 1190 |
| new_trad_explicit | 495 |
| new_simp_ditto | 835 |
| new_simp_explicit | 850 |

## Automatically resolved - HIGH confidence

750 entries.

| line | entry_id | hanri | mandarin_trad | source | revision |
| --- | --- | --- | --- | --- | --- |
| 72 | U+52A0_U+6771_00 | 加東 | 加東 | [Wiktionary](https://en.wiktionary.org/wiki/加東) | 87969265 |
| 75 | U+99D5_U+99DB_00 | 駕駛 | 駕駛 | [Wiktionary](https://en.wiktionary.org/wiki/駕駛) | 92711890 |
| 78 | U+89BA_00 | 覺 | 覺 | [Wiktionary](https://en.wiktionary.org/wiki/覺) | 90067045 |
| 81 | U+89BA_U+9192_00 | 覺醒 | 覺醒 | [Wiktionary](https://en.wiktionary.org/wiki/覺醒) | 84623557 |
| 84 | U+7C21_U+55AE_00 | 簡單 | 簡單 | [Wiktionary](https://en.wiktionary.org/wiki/簡單) | 92420384 |
| 87 | U+7518_00 | 甘 | 甘 | [Wiktionary](https://en.wiktionary.org/wiki/甘) | 92541698 |
| 88 | U+611F_00 | 感 | 感 | [Wiktionary](https://en.wiktionary.org/wiki/感) | 92161263 |
| 89 | U+542B_00 | 含 | 含 | [Wiktionary](https://en.wiktionary.org/wiki/含) | 92638624 |
| 94 | U+611F_U+60C5_00 | 感情 | 感情 | [Wiktionary](https://en.wiktionary.org/wiki/感情) | 92161259 |
| 95 | U+5DE5_00 | 工 | 工 | [Wiktionary](https://en.wiktionary.org/wiki/工) | 92678585 |
| 101 | U+6E2F_U+7063_00 | 港灣 | 港灣 | [Wiktionary](https://en.wiktionary.org/wiki/港灣) | 87608775 |
| 116 | U+4EA4_U+4EE3_00 | 交代 | 交代 | [Wiktionary](https://en.wiktionary.org/wiki/交代) | 92137544 |
| 132 | U+4ECB_U+7D39_00 | 介紹 | 介紹 | [Wiktionary](https://en.wiktionary.org/wiki/介紹) | 88999625 |
| 133 | U+89E3_U+8AAA_00 | 解說 | 解說 | [Wiktionary](https://en.wiktionary.org/wiki/解說) | 92518204 |
| 147 | U+517C_00 | 兼 | 兼 | [Wiktionary](https://en.wiktionary.org/wiki/兼) | 93296483 |
| 150 | U+9E79_U+9165_U+96DE_00 | 鹹酥雞 | 鹹酥雞 | [Wiktionary](https://en.wiktionary.org/wiki/鹹酥雞) | 88986117 |
| 152 | U+8B19_U+865B_00 | 謙虛 | 謙虛 | [Wiktionary](https://en.wiktionary.org/wiki/謙虛) | 84948471 |
| 157 | U+7CCA_00 | 糊 | 糊 | [Wiktionary](https://en.wiktionary.org/wiki/糊) | 92815748 |
| 179 | U+529F_U+5FB7_00 | 功德 | 功德 | [Wiktionary](https://en.wiktionary.org/wiki/功德) | 90753144 |
| 180 | U+516C_U+91CC_00 | 公里 | 公里 | [Wiktionary](https://en.wiktionary.org/wiki/公里) | 92042991 |
| 182 | U+5149_U+660E_00 | 光明 | 光明 | [Wiktionary](https://en.wiktionary.org/wiki/光明) | 86472024 |
| 185 | U+5149_U+9670_00 | 光陰 | 光陰 | [Wiktionary](https://en.wiktionary.org/wiki/光陰) | 92262185 |
| 195 | U+5AC1_00 | 嫁 | 嫁 | [Wiktionary](https://en.wiktionary.org/wiki/嫁) | 92712042 |
| 197 | U+8A08_U+8F03_00 | 計較 | 計較 | [Wiktionary](https://en.wiktionary.org/wiki/計較) | 90313410 |
| 199 | U+7E7C_U+7E8C_00 | 繼續 | 繼續 | [Wiktionary](https://en.wiktionary.org/wiki/繼續) | 92084359 |
| 202 | U+5287_00 | 劇 | 劇 | [Wiktionary](https://en.wiktionary.org/wiki/劇) | 92160389 |
| 205 | U+5171_00 | 共 | 共 | [Wiktionary](https://en.wiktionary.org/wiki/共) | 92310443 |
| 206 | U+62F1_U+624B_00 | 拱手 | 拱手 | [Wiktionary](https://en.wiktionary.org/wiki/拱手) | 91115545 |
| 208 | U+6FC0_00 | 激 | 激 | [Wiktionary](https://en.wiktionary.org/wiki/激) | 92777702 |
| 211 | U+5065_00 | 健 | 健 | [Wiktionary](https://en.wiktionary.org/wiki/健) | 92983679 |
| 214 | U+5805_U+6301_00 | 堅持 | 堅持 | [Wiktionary](https://en.wiktionary.org/wiki/堅持) | 91831027 |
| 215 | U+5065_U+5EB7_00 | 健康 | 健康 | [Wiktionary](https://en.wiktionary.org/wiki/健康) | 92198514 |
| 216 | U+5091_00 | 傑 | 傑 | [Wiktionary](https://en.wiktionary.org/wiki/傑) | 92199937 |
| 222 | U+5883_00 | 境 | 境 | [Wiktionary](https://en.wiktionary.org/wiki/境) | 92303359 |
| 225 | U+66F4_U+52A0_00 | 更加 | 更加 | [Wiktionary](https://en.wiktionary.org/wiki/更加) | 91707684 |
| 226 | U+7D93_U+904E_00 | 經過 | 經過 | [Wiktionary](https://en.wiktionary.org/wiki/經過) | 90507540 |
| 231 | U+500B_00 | 個 | 個 | [Wiktionary](https://en.wiktionary.org/wiki/個) | 92487995 |
| 240 | U+5BE1_00 | 寡 | 寡 | [Wiktionary](https://en.wiktionary.org/wiki/寡) | 92720704 |
| 242 | U+6B4C_U+8FF7_00 | 歌迷 | 歌迷 | [Wiktionary](https://en.wiktionary.org/wiki/歌迷) | 78641850 |
| 244 | U+6B4C_U+5531_00 | 歌唱 | 歌唱 | [Wiktionary](https://en.wiktionary.org/wiki/歌唱) | 92161728 |
| 247 | U+9928_00 | 館 | 館 | [Wiktionary](https://en.wiktionary.org/wiki/館) | 92202190 |
| 250 | U+6C7A_U+5B9A_00 | 決定 | 決定 | [Wiktionary](https://en.wiktionary.org/wiki/決定) | 92135399 |
| 258 | U+602A_00 | 怪 | 怪 | [Wiktionary](https://en.wiktionary.org/wiki/怪) | 92200463 |
| 268 | U+53EB_00 | 叫 | 叫 | [Wiktionary](https://en.wiktionary.org/wiki/叫) | 93357205 |
| 270 | U+4E45_00 | 久 | 久 | [Wiktionary](https://en.wiktionary.org/wiki/久) | 92691386 |
| 273 | U+4E45_U+9577_00 | 久長 | 久長 | [Wiktionary](https://en.wiktionary.org/wiki/久長) | 78464143 |
| 276 | U+541B_U+738B_00 | 君王 | 君王 | [Wiktionary](https://en.wiktionary.org/wiki/君王) | 78611119 |
| 287 | U+904E_U+5BA2_00 | 過客 | 過客 | [Wiktionary](https://en.wiktionary.org/wiki/過客) | 91417214 |
| 288 | U+904E_U+53BB_00 | 過去 | 過去 | [Wiktionary](https://en.wiktionary.org/wiki/過去) | 92285740 |
| 296 | U+898F_U+5F8B_00 | 規律 | 規律 | [Wiktionary](https://en.wiktionary.org/wiki/規律) | 92237408 |
| 298 | U+6B78_U+5C6C_00 | 歸屬 | 歸屬 | [Wiktionary](https://en.wiktionary.org/wiki/歸屬) | 87444923 |
| 299 | U+6B78_U+5BBF_00 | 歸宿 | 歸宿 | [Wiktionary](https://en.wiktionary.org/wiki/歸宿) | 78642233 |
| 303 | U+4E45_U+4EF0_00 | 久仰 | 久仰 | [Wiktionary](https://en.wiktionary.org/wiki/久仰) | 89611354 |
| 304 | U+6C42_U+795E_00 | 求神 | 求神 | [Wiktionary](https://en.wiktionary.org/wiki/求神) | 73610361 |
| 307 | U+625B_00 | 扛 | 扛 | [Wiktionary](https://en.wiktionary.org/wiki/扛) | 92200521 |
| 308 | U+5EE3_U+6771_00 | 廣東 | 廣東 | [Wiktionary](https://en.wiktionary.org/wiki/廣東) | 90403162 |
| 310 | U+5EE3_U+6771_U+8A71_00 | 廣東話 | 廣東話 | [Wiktionary](https://en.wiktionary.org/wiki/廣東話) | 81441671 |
| 317 | U+7948_U+6C42_00 | 祈求 | 祈求 | [Wiktionary](https://en.wiktionary.org/wiki/祈求) | 77834522 |
| 321 | U+7D00_U+5FF5_00 | 紀念 | 紀念 | [Wiktionary](https://en.wiktionary.org/wiki/紀念) | 84087181 |
| 327 | U+6A5F_U+6703_00 | 機會 | 機會 | [Wiktionary](https://en.wiktionary.org/wiki/機會) | 92751037 |
| 328 | U+4ECA_00 | 今 | 今 | [Wiktionary](https://en.wiktionary.org/wiki/今) | 92199524 |
| 329 | U+7DCA_00 | 緊 | 緊 | [Wiktionary](https://en.wiktionary.org/wiki/緊) | 92201359 |
| 330 | U+4ECA_U+5E74_00 | 今年 | 今年 | [Wiktionary](https://en.wiktionary.org/wiki/今年) | 92160104 |
| 336 | U+898B_U+9762_00 | 見面 | 見面 | [Wiktionary](https://en.wiktionary.org/wiki/見面) | 86772765 |
| 341 | U+91D1_U+9580_00 | 金門 | 金門 | [Wiktionary](https://en.wiktionary.org/wiki/金門) | 92752107 |
| 342 | U+4ECA_U+751F_00 | 今生 | 今生 | [Wiktionary](https://en.wiktionary.org/wiki/今生) | 92160108 |
| 353 | U+4E94_U+767E_00 | 五百 | 五百 | [Wiktionary](https://en.wiktionary.org/wiki/五百) | 86478634 |
| 371 | U+9D5D_U+8089_00 | 鵝肉 | 鵝肉 | [Wiktionary](https://en.wiktionary.org/wiki/鵝肉) | 78692541 |
| 375 | U+9858_00 | 願 | 願 | [Wiktionary](https://en.wiktionary.org/wiki/願) | 92163340 |
| 382 | U+725B_00 | 牛 | 牛 | [Wiktionary](https://en.wiktionary.org/wiki/牛) | 92691725 |
| 384 | U+725B_U+5976_00 | 牛奶 | 牛奶 | [Wiktionary](https://en.wiktionary.org/wiki/牛奶) | 84361749 |
| 386 | U+725B_U+5976_01 | 牛奶 | 牛奶 | [Wiktionary](https://en.wiktionary.org/wiki/牛奶) | 84361749 |
| 388 | U+725B_U+8ECA_U+6C34_00 | 牛車水 | 牛車水 | [Wiktionary](https://en.wiktionary.org/wiki/牛車水) | 87998134 |
| 389 | U+9280_00 | 銀 | 銀 | [Wiktionary](https://en.wiktionary.org/wiki/銀) | 92676255 |
| 394 | U+9280_01 | 銀 | 銀 | [Wiktionary](https://en.wiktionary.org/wiki/銀) | 92676255 |
| 397 | U+5B9C_U+862D_00 | 宜蘭 | 宜蘭 | [Wiktionary](https://en.wiktionary.org/wiki/宜蘭) | 87998328 |
| 398 | U+8B70_U+8AD6_00 | 議論 | 議論 | [Wiktionary](https://en.wiktionary.org/wiki/議論) | 92135872 |
| 400 | U+54EA_00 | 哪 | 哪 | [Wiktionary](https://en.wiktionary.org/wiki/哪) | 87590234 |
| 402 | U+82E5_00 | 若 | 若 | [Wiktionary](https://en.wiktionary.org/wiki/若) | 89762568 |
| 404 | U+5357_U+7121_00 | 南無 | 南無 | [Wiktionary](https://en.wiktionary.org/wiki/南無) | 92305469 |
| 407 | U+5948_00 | 奈 | 奈 | [Wiktionary](https://en.wiktionary.org/wiki/奈) | 91794359 |
| 409 | U+5948_U+4F55_00 | 奈何 | 奈何 | [Wiktionary](https://en.wiktionary.org/wiki/奈何) | 86467134 |
| 410 | U+5A18_00 | 娘 | 娘 | [Wiktionary](https://en.wiktionary.org/wiki/娘) | 92459779 |
| 413 | U+721B_00 | 爛 | 爛 | [Wiktionary](https://en.wiktionary.org/wiki/爛) | 92037368 |
| 414 | U+5A18_01 | 娘 | 娘 | [Wiktionary](https://en.wiktionary.org/wiki/娘) | 92459779 |
| 415 | U+8B93_00 | 讓 | 讓 | [Wiktionary](https://en.wiktionary.org/wiki/讓) | 91424718 |
| 435 | U+9010_00 | 逐 | 逐 | [Wiktionary](https://en.wiktionary.org/wiki/逐) | 92201929 |
| 441 | U+7B49_00 | 等 | 等 | [Wiktionary](https://en.wiktionary.org/wiki/等) | 92678428 |
| 442 | U+64F2_00 | 擲 | 擲 | [Wiktionary](https://en.wiktionary.org/wiki/擲) | 91962074 |
| 445 | U+4F46_U+9858_00 | 但願 | 但願 | [Wiktionary](https://en.wiktionary.org/wiki/但願) | 63190816 |
| 447 | U+9054_00 | 達 | 達 | [Wiktionary](https://en.wiktionary.org/wiki/達) | 92699992 |
| 450 | U+81BD_00 | 膽 | 膽 | [Wiktionary](https://en.wiktionary.org/wiki/膽) | 92382355 |
| 451 | U+6253_U+626E_00 | 打扮 | 打扮 | [Wiktionary](https://en.wiktionary.org/wiki/打扮) | 78631237 |
| 455 | U+6DE1_00 | 淡 | 淡 | [Wiktionary](https://en.wiktionary.org/wiki/淡) | 93358056 |
| 457 | U+803D_U+8AA4_00 | 耽誤 | 耽誤 | [Wiktionary](https://en.wiktionary.org/wiki/耽誤) | 82793058 |
| 458 | U+6DE1_U+6C34_00 | 淡水 | 淡水 | [Wiktionary](https://en.wiktionary.org/wiki/淡水) | 90781395 |
| 459 | U+6DE1_U+6C34_U+6CB3_00 | 淡水河 | 淡水河 | [Wiktionary](https://en.wiktionary.org/wiki/淡水河) | 88250894 |
| 463 | U+7576_00 | 當 | 當 | [Wiktionary](https://en.wiktionary.org/wiki/當) | 92645416 |
| 464 | U+51CD_00 | 凍 | 凍 | [Wiktionary](https://en.wiktionary.org/wiki/凍) | 93384863 |
| 465 | U+7576_01 | 當 | 當 | [Wiktionary](https://en.wiktionary.org/wiki/當) | 92645416 |
| 466 | U+52D5_00 | 動 | 動 | [Wiktionary](https://en.wiktionary.org/wiki/動) | 91206709 |
| 475 | U+7576_U+6642_00 | 當時 | 當時 | [Wiktionary](https://en.wiktionary.org/wiki/當時) | 88989004 |
| 477 | U+540C_U+5B78_00 | 同學 | 同學 | [Wiktionary](https://en.wiktionary.org/wiki/同學) | 91706307 |
| 478 | U+540C_U+5B89_00 | 同安 | 同安 | [Wiktionary](https://en.wiktionary.org/wiki/同安) | 92752091 |
| 481 | U+7B54_U+61C9_00 | 答應 | 答應 | [Wiktionary](https://en.wiktionary.org/wiki/答應) | 88305421 |
| 482 | U+515C_00 | 兜 | 兜 | [Wiktionary](https://en.wiktionary.org/wiki/兜) | 92199955 |
| 484 | U+6295_00 | 投 | 投 | [Wiktionary](https://en.wiktionary.org/wiki/投) | 92810921 |
| 490 | U+8C46_U+82B1_00 | 豆花 | 豆花 | [Wiktionary](https://en.wiktionary.org/wiki/豆花) | 91913948 |
| 493 | U+5446_00 | 呆 | 呆 | [Wiktionary](https://en.wiktionary.org/wiki/呆) | 88077599 |
| 510 | U+9F0E_00 | 鼎 | 鼎 | [Wiktionary](https://en.wiktionary.org/wiki/鼎) | 92535995 |
| 511 | U+5B9A_00 | 定 | 定 | [Wiktionary](https://en.wiktionary.org/wiki/定) | 92811261 |
| 514 | U+9EDE_00 | 點 | 點 | [Wiktionary](https://en.wiktionary.org/wiki/點) | 92965588 |
| 519 | U+9EDE_U+9EDE_U+6EF4_U+6EF4_00 | 點點滴滴 | 點點滴滴 | [Wiktionary](https://en.wiktionary.org/wiki/點點滴滴) | 78694171 |
| 520 | U+9EDE_U+9418_00 | 點鐘 | 點鐘 | [Wiktionary](https://en.wiktionary.org/wiki/點鐘) | 87961715 |
| 521 | U+606C_U+975C_00 | 恬靜 | 恬靜 | [Wiktionary](https://en.wiktionary.org/wiki/恬靜) | 92431594 |
| 522 | U+689D_00 | 條 | 條 | [Wiktionary](https://en.wiktionary.org/wiki/條) | 91675380 |
| 526 | U+671D_U+9BAE_00 | 朝鮮 | 朝鮮 | [Wiktionary](https://en.wiktionary.org/wiki/朝鮮) | 91682184 |
| 527 | U+90FD_00 | 都 | 都 | [Wiktionary](https://en.wiktionary.org/wiki/都) | 92731497 |
| 529 | U+90FD_01 | 都 | 都 | [Wiktionary](https://en.wiktionary.org/wiki/都) | 92731497 |
| 530 | U+5EA6_U+904E_00 | 度過 | 度過 | [Wiktionary](https://en.wiktionary.org/wiki/度過) | 73998156 |
| 531 | U+90FD_U+5E02_00 | 都市 | 都市 | [Wiktionary](https://en.wiktionary.org/wiki/都市) | 92163014 |
| 532 | U+8CED_U+6C23_00 | 賭氣 | 賭氣 | [Wiktionary](https://en.wiktionary.org/wiki/賭氣) | 87305312 |
| 535 | U+6BD2_U+6DB2_00 | 毒液 | 毒液 | [Wiktionary](https://en.wiktionary.org/wiki/毒液) | 84419229 |
| 536 | U+4E3C_00 | 丼 | 丼 | [Wiktionary](https://en.wiktionary.org/wiki/丼) | 92294395 |
| 538 | U+7576_02 | 當 | 當 | [Wiktionary](https://en.wiktionary.org/wiki/當) | 92645416 |
| 539 | U+68DF_00 | 棟 | 棟 | [Wiktionary](https://en.wiktionary.org/wiki/棟) | 93387357 |
| 540 | U+7576_03 | 當 | 當 | [Wiktionary](https://en.wiktionary.org/wiki/當) | 92645416 |
| 542 | U+7576_U+7136_00 | 當然 | 當然 | [Wiktionary](https://en.wiktionary.org/wiki/當然) | 81570301 |
| 544 | U+7576_U+6642_01 | 當時 | 當時 | [Wiktionary](https://en.wiktionary.org/wiki/當時) | 88989004 |
| 546 | U+7576_U+505A_00 | 當做 | 當做 | [Wiktionary](https://en.wiktionary.org/wiki/當做) | 82111051 |
| 547 | U+7576_U+521D_00 | 當初 | 當初 | [Wiktionary](https://en.wiktionary.org/wiki/當初) | 83043102 |
| 554 | U+5730_U+7344_00 | 地獄 | 地獄 | [Wiktionary](https://en.wiktionary.org/wiki/地獄) | 93357275 |
| 555 | U+77ED_U+77ED_00 | 短短 | 短短 | [Wiktionary](https://en.wiktionary.org/wiki/短短) | 62320239 |
| 557 | U+7B2C_U+4E09_00 | 第三 | 第三 | [Wiktionary](https://en.wiktionary.org/wiki/第三) | 86157832 |
| 560 | U+7B2C_U+4E00_U+540D_00 | 第一名 | 第一名 | [Wiktionary](https://en.wiktionary.org/wiki/第一名) | 78659373 |
| 562 | U+5730_U+4E0B_00 | 地下 | 地下 | [Wiktionary](https://en.wiktionary.org/wiki/地下) | 92255754 |
| 563 | U+9577_U+6CF0_00 | 長泰 | 長泰 | [Wiktionary](https://en.wiktionary.org/wiki/長泰) | 91757353 |
| 568 | U+4E2D_U+5C71_00 | 中山 | 中山 | [Wiktionary](https://en.wiktionary.org/wiki/中山) | 92982273 |
| 569 | U+91CD_U+65B0_00 | 重新 | 重新 | [Wiktionary](https://en.wiktionary.org/wiki/重新) | 84872291 |
| 571 | U+4E2D_U+5B78_00 | 中學 | 中學 | [Wiktionary](https://en.wiktionary.org/wiki/中學) | 91543586 |
| 572 | U+4E2D_U+592E_00 | 中央 | 中央 | [Wiktionary](https://en.wiktionary.org/wiki/中央) | 92160026 |
| 573 | U+4E2D_U+79CB_00 | 中秋 | 中秋 | [Wiktionary](https://en.wiktionary.org/wiki/中秋) | 84756420 |
| 574 | U+4E2D_U+79CB_U+7BC0_00 | 中秋節 | 中秋節 | [Wiktionary](https://en.wiktionary.org/wiki/中秋節) | 91080254 |
| 575 | U+4E2D_U+83EF_00 | 中華 | 中華 | [Wiktionary](https://en.wiktionary.org/wiki/中華) | 92469501 |
| 576 | U+5F97_00 | 得 | 得 | [Wiktionary](https://en.wiktionary.org/wiki/得) | 92491310 |
| 591 | U+7B49_01 | 等 | 等 | [Wiktionary](https://en.wiktionary.org/wiki/等) | 92678428 |
| 593 | U+5B9A_01 | 定 | 定 | [Wiktionary](https://en.wiktionary.org/wiki/定) | 92811261 |
| 595 | U+71C8_U+5149_00 | 燈光 | 燈光 | [Wiktionary](https://en.wiktionary.org/wiki/燈光) | 78649357 |
| 605 | U+5012_00 | 倒 | 倒 | [Wiktionary](https://en.wiktionary.org/wiki/倒) | 92933399 |
| 607 | U+9053_U+5FB7_00 | 道德 | 道德 | [Wiktionary](https://en.wiktionary.org/wiki/道德) | 91979424 |
| 608 | U+5012_U+8F49_00 | 倒轉 | 倒轉 | [Wiktionary](https://en.wiktionary.org/wiki/倒轉) | 87136298 |
| 611 | U+591A_U+8B1D_00 | 多謝 | 多謝 | [Wiktionary](https://en.wiktionary.org/wiki/多謝) | 90011103 |
| 618 | U+5927_U+8857_U+5C0F_U+5DF7_00 | 大街小巷 | 大街小巷 | [Wiktionary](https://en.wiktionary.org/wiki/大街小巷) | 68662513 |
| 623 | U+5927_U+5DF4_U+7AAF_00 | 大巴窯 | 大巴窯 | [Wiktionary](https://en.wiktionary.org/wiki/大巴窯) | 87971317 |
| 624 | U+5927_U+8072_00 | 大聲 | 大聲 | [Wiktionary](https://en.wiktionary.org/wiki/大聲) | 92674365 |
| 632 | U+5927_U+96E8_00 | 大雨 | 大雨 | [Wiktionary](https://en.wiktionary.org/wiki/大雨) | 92238550 |
| 633 | U+50B3_U+8AAA_00 | 傳說 | 傳說 | [Wiktionary](https://en.wiktionary.org/wiki/傳說) | 84547750 |
| 634 | U+55AE_00 | 單 | 單 | [Wiktionary](https://en.wiktionary.org/wiki/單) | 92448367 |
| 637 | U+5F48_U+7434_00 | 彈琴 | 彈琴 | [Wiktionary](https://en.wiktionary.org/wiki/彈琴) | 84548028 |
| 639 | U+984C_00 | 題 | 題 | [Wiktionary](https://en.wiktionary.org/wiki/題) | 92529780 |
| 642 | U+6F6E_U+5DDE_00 | 潮州 | 潮州 | [Wiktionary](https://en.wiktionary.org/wiki/潮州) | 88383899 |
| 644 | U+8457_00 | 著 | 著 | [Wiktionary](https://en.wiktionary.org/wiki/著) | 92763119 |
| 651 | U+5C0D_00 | 對 | 對 | [Wiktionary](https://en.wiktionary.org/wiki/對) | 93282653 |
| 654 | U+7A3B_U+8349_00 | 稻草 | 稻草 | [Wiktionary](https://en.wiktionary.org/wiki/稻草) | 88110378 |
| 656 | U+5F35_00 | 張 | 張 | [Wiktionary](https://en.wiktionary.org/wiki/張) | 93139667 |
| 657 | U+9577_U+6CF0_01 | 長泰 | 長泰 | [Wiktionary](https://en.wiktionary.org/wiki/長泰) | 91757353 |
| 658 | U+7576_04 | 當 | 當 | [Wiktionary](https://en.wiktionary.org/wiki/當) | 92645416 |
| 659 | U+8F49_00 | 轉 | 轉 | [Wiktionary](https://en.wiktionary.org/wiki/轉) | 92089221 |
| 660 | U+7576_05 | 當 | 當 | [Wiktionary](https://en.wiktionary.org/wiki/當) | 92645416 |
| 661 | U+5510_00 | 唐 | 唐 | [Wiktionary](https://en.wiktionary.org/wiki/唐) | 92160583 |
| 673 | U+77ED_U+77ED_01 | 短短 | 短短 | [Wiktionary](https://en.wiktionary.org/wiki/短短) | 62320239 |
| 682 | U+5F97_01 | 得 | 得 | [Wiktionary](https://en.wiktionary.org/wiki/得) | 92491310 |
| 688 | U+6EF4_U+6EF4_00 | 滴滴 | 滴滴 | [Wiktionary](https://en.wiktionary.org/wiki/滴滴) | 90402329 |
| 692 | U+71B1_U+60C5_00 | 熱情 | 熱情 | [Wiktionary](https://en.wiktionary.org/wiki/熱情) | 92161980 |
| 695 | U+5982_00 | 如 | 如 | [Wiktionary](https://en.wiktionary.org/wiki/如) | 92917064 |
| 697 | U+5982_U+6B64_00 | 如此 | 如此 | [Wiktionary](https://en.wiktionary.org/wiki/如此) | 83176848 |
| 698 | U+5982_U+4F55_00 | 如何 | 如何 | [Wiktionary](https://en.wiktionary.org/wiki/如何) | 92270953 |
| 708 | U+8A8D_U+540C_00 | 認同 | 認同 | [Wiktionary](https://en.wiktionary.org/wiki/認同) | 86635971 |
| 712 | U+4EBA_U+58EB_00 | 人士 | 人士 | [Wiktionary](https://en.wiktionary.org/wiki/人士) | 92160081 |
| 714 | U+4EBA_U+60C5_00 | 人情 | 人情 | [Wiktionary](https://en.wiktionary.org/wiki/人情) | 92737763 |
| 718 | U+65E5_U+65E5_U+591C_U+591C_00 | 日日夜夜 | 日日夜夜 | [Wiktionary](https://en.wiktionary.org/wiki/日日夜夜) | 74106761 |
| 721 | U+65E5_U+5E38_00 | 日常 | 日常 | [Wiktionary](https://en.wiktionary.org/wiki/日常) | 92293270 |
| 726 | U+5FCD_U+5FC3_00 | 忍心 | 忍心 | [Wiktionary](https://en.wiktionary.org/wiki/忍心) | 72652339 |
| 737 | U+96E3_U+904E_00 | 難過 | 難過 | [Wiktionary](https://en.wiktionary.org/wiki/難過) | 91332321 |
| 738 | U+96E3_U+904E_01 | 難過 | 難過 | [Wiktionary](https://en.wiktionary.org/wiki/難過) | 91332321 |
| 739 | U+96E3_U+5FD8_00 | 難忘 | 難忘 | [Wiktionary](https://en.wiktionary.org/wiki/難忘) | 91623579 |
| 740 | U+96E3_U+514D_00 | 難免 | 難免 | [Wiktionary](https://en.wiktionary.org/wiki/難免) | 85026282 |
| 743 | U+7537_00 | 男 | 男 | [Wiktionary](https://en.wiktionary.org/wiki/男) | 92739176 |
| 746 | U+5357_U+5B89_00 | 南安 | 南安 | [Wiktionary](https://en.wiktionary.org/wiki/南安) | 92026585 |
| 747 | U+5357_U+6D0B_00 | 南洋 | 南洋 | [Wiktionary](https://en.wiktionary.org/wiki/南洋) | 92198842 |
| 751 | U+5F04_00 | 弄 | 弄 | [Wiktionary](https://en.wiktionary.org/wiki/弄) | 92546755 |
| 752 | U+4EBA_U+5BB6_00 | 人家 | 人家 | [Wiktionary](https://en.wiktionary.org/wiki/人家) | 91555437 |
| 755 | U+5289_00 | 劉 | 劉 | [Wiktionary](https://en.wiktionary.org/wiki/劉) | 91532081 |
| 756 | U+6A13_00 | 樓 | 樓 | [Wiktionary](https://en.wiktionary.org/wiki/樓) | 93381128 |
| 764 | U+8001_U+767E_U+59D3_00 | 老百姓 | 老百姓 | [Wiktionary](https://en.wiktionary.org/wiki/老百姓) | 91146951 |
| 775 | U+4F86_U+5230_00 | 來到 | 來到 | [Wiktionary](https://en.wiktionary.org/wiki/來到) | 81475014 |
| 781 | U+5FF5_00 | 念 | 念 | [Wiktionary](https://en.wiktionary.org/wiki/念) | 92917773 |
| 785 | U+651D_00 | 攝 | 攝 | [Wiktionary](https://en.wiktionary.org/wiki/攝) | 88197617 |
| 788 | U+804A_00 | 聊 | 聊 | [Wiktionary](https://en.wiktionary.org/wiki/聊) | 92742491 |
| 791 | U+6EF7_00 | 滷 | 滷 | [Wiktionary](https://en.wiktionary.org/wiki/滷) | 91971423 |
| 792 | U+9B6F_00 | 魯 | 魯 | [Wiktionary](https://en.wiktionary.org/wiki/魯) | 92709474 |
| 793 | U+8DEF_00 | 路 | 路 | [Wiktionary](https://en.wiktionary.org/wiki/路) | 92730569 |
| 796 | U+52AA_U+529B_00 | 努力 | 努力 | [Wiktionary](https://en.wiktionary.org/wiki/努力) | 92136053 |
| 798 | U+6EF7_U+8089_00 | 滷肉 | 滷肉 | [Wiktionary](https://en.wiktionary.org/wiki/滷肉) | 89826518 |
| 799 | U+6EF7_U+8089_U+98EF_00 | 滷肉飯 | 滷肉飯 | [Wiktionary](https://en.wiktionary.org/wiki/滷肉飯) | 87976558 |
| 805 | U+9E7F_U+6E2F_00 | 鹿港 | 鹿港 | [Wiktionary](https://en.wiktionary.org/wiki/鹿港) | 87964310 |
| 807 | U+70D9_U+5370_00 | 烙印 | 烙印 | [Wiktionary](https://en.wiktionary.org/wiki/烙印) | 93358538 |
| 810 | U+6D6A_00 | 浪 | 浪 | [Wiktionary](https://en.wiktionary.org/wiki/浪) | 92200932 |
| 811 | U+90CE_U+541B_00 | 郎君 | 郎君 | [Wiktionary](https://en.wiktionary.org/wiki/郎君) | 87968188 |
| 817 | U+79AE_00 | 禮 | 禮 | [Wiktionary](https://en.wiktionary.org/wiki/禮) | 92201231 |
| 820 | U+79AE_U+62DC_00 | 禮拜 | 禮拜 | [Wiktionary](https://en.wiktionary.org/wiki/禮拜) | 92764509 |
| 824 | U+72FC_U+72FD_00 | 狼狽 | 狼狽 | [Wiktionary](https://en.wiktionary.org/wiki/狼狽) | 87223971 |
| 826 | U+826F_U+7DE3_00 | 良緣 | 良緣 | [Wiktionary](https://en.wiktionary.org/wiki/良緣) | 90522581 |
| 827 | U+9F8D_U+6D77_00 | 龍海 | 龍海 | [Wiktionary](https://en.wiktionary.org/wiki/龍海) | 87981399 |
| 830 | U+6190_00 | 憐 | 憐 | [Wiktionary](https://en.wiktionary.org/wiki/憐) | 89940696 |
| 835 | U+5BE7_00 | 寧 | 寧 | [Wiktionary](https://en.wiktionary.org/wiki/寧) | 92200337 |
| 838 | U+80FD_U+529B_00 | 能力 | 能力 | [Wiktionary](https://en.wiktionary.org/wiki/能力) | 92252358 |
| 842 | U+9748_U+9B42_00 | 靈魂 | 靈魂 | [Wiktionary](https://en.wiktionary.org/wiki/靈魂) | 91478240 |
| 845 | U+7F85_U+99AC_U+5B57_00 | 羅馬字 | 羅馬字 | [Wiktionary](https://en.wiktionary.org/wiki/羅馬字) | 88211532 |
| 846 | U+56C9_U+55E6_00 | 囉嗦 | 囉嗦 | [Wiktionary](https://en.wiktionary.org/wiki/囉嗦) | 90092432 |
| 847 | U+52DE_U+82E6_00 | 勞苦 | 勞苦 | [Wiktionary](https://en.wiktionary.org/wiki/勞苦) | 78607754 |
| 848 | U+843D_00 | 落 | 落 | [Wiktionary](https://en.wiktionary.org/wiki/落) | 92297728 |
| 850 | U+843D_U+5C71_00 | 落山 | 落山 | [Wiktionary](https://en.wiktionary.org/wiki/落山) | 85413764 |
| 858 | U+4E82_00 | 亂 | 亂 | [Wiktionary](https://en.wiktionary.org/wiki/亂) | 93318265 |
| 861 | U+6200_U+611B_00 | 戀愛 | 戀愛 | [Wiktionary](https://en.wiktionary.org/wiki/戀愛) | 93369748 |
| 864 | U+65C5_U+9014_00 | 旅途 | 旅途 | [Wiktionary](https://en.wiktionary.org/wiki/旅途) | 90961232 |
| 866 | U+65C5_U+5BA2_00 | 旅客 | 旅客 | [Wiktionary](https://en.wiktionary.org/wiki/旅客) | 90961198 |
| 871 | U+7559_U+6200_00 | 留戀 | 留戀 | [Wiktionary](https://en.wiktionary.org/wiki/留戀) | 90036894 |
| 872 | U+6D41_U+8F49_00 | 流轉 | 流轉 | [Wiktionary](https://en.wiktionary.org/wiki/流轉) | 90604730 |
| 874 | U+6D41_U+884C_00 | 流行 | 流行 | [Wiktionary](https://en.wiktionary.org/wiki/流行) | 92135781 |
| 875 | U+674E_00 | 李 | 李 | [Wiktionary](https://en.wiktionary.org/wiki/李) | 92200726 |
| 877 | U+96E2_00 | 離 | 離 | [Wiktionary](https://en.wiktionary.org/wiki/離) | 92202131 |
| 878 | U+7406_U+5DE5_00 | 理工 | 理工 | [Wiktionary](https://en.wiktionary.org/wiki/理工) | 78651631 |
| 881 | U+7406_U+7531_00 | 理由 | 理由 | [Wiktionary](https://en.wiktionary.org/wiki/理由) | 92289426 |
| 885 | U+6797_00 | 林 | 林 | [Wiktionary](https://en.wiktionary.org/wiki/林) | 92200737 |
| 886 | U+98F2_U+8336_00 | 飲茶 | 飲茶 | [Wiktionary](https://en.wiktionary.org/wiki/飲茶) | 92261585 |
| 890 | U+98F2_U+9152_00 | 飲酒 | 飲酒 | [Wiktionary](https://en.wiktionary.org/wiki/飲酒) | 92163288 |
| 891 | U+6797_U+539D_U+6E2F_00 | 林厝港 | 林厝港 | [Wiktionary](https://en.wiktionary.org/wiki/林厝港) | 85835132 |
| 896 | U+99AC_U+4F86_U+897F_U+4E9E_U+4EBA_00 | 馬來西亞人 | 馬來西亞人 | [Wiktionary](https://en.wiktionary.org/wiki/馬來西亞人) | 90019306 |
| 897 | U+5ABD_U+7956_00 | 媽祖 | 媽祖 | [Wiktionary](https://en.wiktionary.org/wiki/媽祖) | 92380961 |
| 898 | U+540D_00 | 名 | 名 | [Wiktionary](https://en.wiktionary.org/wiki/名) | 92722448 |
| 909 | U+6EFF_U+9762_00 | 滿面 | 滿面 | [Wiktionary](https://en.wiktionary.org/wiki/滿面) | 78647223 |
| 910 | U+9EBB_U+6CB9_U+96DE_00 | 麻油雞 | 麻油雞 | [Wiktionary](https://en.wiktionary.org/wiki/麻油雞) | 92366964 |
| 916 | U+6BCF_U+65E5_00 | 每日 | 每日 | [Wiktionary](https://en.wiktionary.org/wiki/每日) | 84283523 |
| 917 | U+6885_U+82B1_00 | 梅花 | 梅花 | [Wiktionary](https://en.wiktionary.org/wiki/梅花) | 88030440 |
| 918 | U+6BDB_00 | 毛 | 毛 | [Wiktionary](https://en.wiktionary.org/wiki/毛) | 92722443 |
| 925 | U+9EB5_U+7DDA_00 | 麵線 | 麵線 | [Wiktionary](https://en.wiktionary.org/wiki/麵線) | 91806237 |
| 929 | U+7269_U+4EF6_00 | 物件 | 物件 | [Wiktionary](https://en.wiktionary.org/wiki/物件) | 92162119 |
| 930 | U+98FD_00 | 飽 | 飽 | [Wiktionary](https://en.wiktionary.org/wiki/飽) | 91978666 |
| 936 | U+5317_U+4EAC_00 | 北京 | 北京 | [Wiktionary](https://en.wiktionary.org/wiki/北京) | 92485826 |
| 940 | U+73ED_00 | 班 | 班 | [Wiktionary](https://en.wiktionary.org/wiki/班) | 92201089 |
| 948 | U+623F_U+9593_00 | 房間 | 房間 | [Wiktionary](https://en.wiktionary.org/wiki/房間) | 91707300 |
| 953 | U+767E_U+5E74_00 | 百年 | 百年 | [Wiktionary](https://en.wiktionary.org/wiki/百年) | 91749324 |
| 956 | U+5305_00 | 包 | 包 | [Wiktionary](https://en.wiktionary.org/wiki/包) | 92200035 |
| 957 | U+64FA_00 | 擺 | 擺 | [Wiktionary](https://en.wiktionary.org/wiki/擺) | 90519652 |
| 958 | U+62DC_00 | 拜 | 拜 | [Wiktionary](https://en.wiktionary.org/wiki/拜) | 92200553 |
| 962 | U+62DC_U+62DC_00 | 拜拜 | 拜拜 | [Wiktionary](https://en.wiktionary.org/wiki/拜拜) | 90348051 |
| 966 | U+9905_00 | 餅 | 餅 | [Wiktionary](https://en.wiktionary.org/wiki/餅) | 92202187 |
| 971 | U+8868_U+6F14_00 | 表演 | 表演 | [Wiktionary](https://en.wiktionary.org/wiki/表演) | 84213082 |
| 974 | U+5E03_U+888B_00 | 布袋 | 布袋 | [Wiktionary](https://en.wiktionary.org/wiki/布袋) | 92161043 |
| 978 | U+5F77_U+5FA8_00 | 彷徨 | 彷徨 | [Wiktionary](https://en.wiktionary.org/wiki/彷徨) | 92161144 |
| 985 | U+767D_U+99AC_00 | 白馬 | 白馬 | [Wiktionary](https://en.wiktionary.org/wiki/白馬) | 87994390 |
| 987 | U+767D_U+8272_00 | 白色 | 白色 | [Wiktionary](https://en.wiktionary.org/wiki/白色) | 92224350 |
| 992 | U+903C_00 | 逼 | 逼 | [Wiktionary](https://en.wiktionary.org/wiki/逼) | 91974836 |
| 994 | U+8B8A_U+5366_00 | 變卦 | 變卦 | [Wiktionary](https://en.wiktionary.org/wiki/變卦) | 75585606 |
| 995 | U+4FBF_U+7576_00 | 便當 | 便當 | [Wiktionary](https://en.wiktionary.org/wiki/便當) | 89961497 |
| 997 | U+8B8A_U+6210_00 | 變成 | 變成 | [Wiktionary](https://en.wiktionary.org/wiki/變成) | 90092660 |
| 1001 | U+5175_00 | 兵 | 兵 | [Wiktionary](https://en.wiktionary.org/wiki/兵) | 92199960 |
| 1005 | U+5E73_U+5E73_U+5B89_U+5B89_00 | 平平安安 | 平平安安 | [Wiktionary](https://en.wiktionary.org/wiki/平平安安) | 81339027 |
| 1008 | U+5E73_U+5B89_00 | 平安 | 平安 | [Wiktionary](https://en.wiktionary.org/wiki/平安) | 92293142 |
| 1014 | U+5A46_00 | 婆 | 婆 | [Wiktionary](https://en.wiktionary.org/wiki/婆) | 92200298 |
| 1022 | U+4FDD_U+8B49_00 | 保證 | 保證 | [Wiktionary](https://en.wiktionary.org/wiki/保證) | 91957169 |
| 1026 | U+642C_00 | 搬 | 搬 | [Wiktionary](https://en.wiktionary.org/wiki/搬) | 87582189 |
| 1037 | U+516B_U+5B57_00 | 八字 | 八字 | [Wiktionary](https://en.wiktionary.org/wiki/八字) | 87991401 |
| 1038 | U+516B_U+767E_00 | 八百 | 八百 | [Wiktionary](https://en.wiktionary.org/wiki/八百) | 92278833 |
| 1042 | U+5206_00 | 分 | 分 | [Wiktionary](https://en.wiktionary.org/wiki/分) | 92695569 |
| 1043 | U+672C_00 | 本 | 本 | [Wiktionary](https://en.wiktionary.org/wiki/本) | 92741679 |
| 1049 | U+4E0D_U+77E5_U+4E0D_U+89BA_00 | 不知不覺 | 不知不覺 | [Wiktionary](https://en.wiktionary.org/wiki/不知不覺) | 75675928 |
| 1051 | U+4E0D_U+6B63_00 | 不正 | 不正 | [Wiktionary](https://en.wiktionary.org/wiki/不正) | 92271478 |
| 1056 | U+4F69_U+528D_00 | 佩劍 | 佩劍 | [Wiktionary](https://en.wiktionary.org/wiki/佩劍) | 88133527 |
| 1061 | U+80CC_U+5F8C_00 | 背後 | 背後 | [Wiktionary](https://en.wiktionary.org/wiki/背後) | 92263085 |
| 1063 | U+62D4_00 | 拔 | 拔 | [Wiktionary](https://en.wiktionary.org/wiki/拔) | 92968085 |
| 1065 | U+98EF_00 | 飯 | 飯 | [Wiktionary](https://en.wiktionary.org/wiki/飯) | 92731972 |
| 1069 | U+79D8_U+5BC6_00 | 秘密 | 秘密 | [Wiktionary](https://en.wiktionary.org/wiki/秘密) | 93122814 |
| 1073 | U+79D8_U+65B9_00 | 秘方 | 秘方 | [Wiktionary](https://en.wiktionary.org/wiki/秘方) | 85491365 |
| 1075 | U+5C4F_U+6771_00 | 屏東 | 屏東 | [Wiktionary](https://en.wiktionary.org/wiki/屏東) | 87998335 |
| 1077 | U+7B46_00 | 筆 | 筆 | [Wiktionary](https://en.wiktionary.org/wiki/筆) | 93143322 |
| 1087 | U+95A9_00 | 閩 | 閩 | [Wiktionary](https://en.wiktionary.org/wiki/閩) | 90534094 |
| 1093 | U+95A9_U+5357_00 | 閩南 | 閩南 | [Wiktionary](https://en.wiktionary.org/wiki/閩南) | 91699519 |
| 1094 | U+95A9_U+5357_U+8A9E_00 | 閩南語 | 閩南語 | [Wiktionary](https://en.wiktionary.org/wiki/閩南語) | 92090711 |
| 1102 | U+671B_00 | 望 | 望 | [Wiktionary](https://en.wiktionary.org/wiki/望) | 92512175 |
| 1107 | U+832B_U+832B_00 | 茫茫 | 茫茫 | [Wiktionary](https://en.wiktionary.org/wiki/茫茫) | 88410852 |
| 1109 | U+5922_U+9192_00 | 夢醒 | 夢醒 | [Wiktionary](https://en.wiktionary.org/wiki/夢醒) | 78569743 |
| 1111 | U+8089_U+4E7E_00 | 肉乾 | 肉乾 | [Wiktionary](https://en.wiktionary.org/wiki/肉乾) | 81554460 |
| 1112 | U+8089_U+9AA8_U+8336_00 | 肉骨茶 | 肉骨茶 | [Wiktionary](https://en.wiktionary.org/wiki/肉骨茶) | 91953891 |
| 1116 | U+8089_U+9AD4_00 | 肉體 | 肉體 | [Wiktionary](https://en.wiktionary.org/wiki/肉體) | 92391766 |
| 1117 | U+6A21_U+6A23_00 | 模樣 | 模樣 | [Wiktionary](https://en.wiktionary.org/wiki/模樣) | 81583380 |
| 1118 | U+76EE_U+7684_00 | 目的 | 目的 | [Wiktionary](https://en.wiktionary.org/wiki/目的) | 92293556 |
| 1119 | U+76EE_U+524D_00 | 目前 | 目前 | [Wiktionary](https://en.wiktionary.org/wiki/目前) | 88673373 |
| 1122 | U+4EA1_U+9B42_00 | 亡魂 | 亡魂 | [Wiktionary](https://en.wiktionary.org/wiki/亡魂) | 89875851 |
| 1124 | U+8FF7_00 | 迷 | 迷 | [Wiktionary](https://en.wiktionary.org/wiki/迷) | 92201925 |
| 1128 | U+8FF7_U+6200_00 | 迷戀 | 迷戀 | [Wiktionary](https://en.wiktionary.org/wiki/迷戀) | 84548723 |
| 1130 | U+6B32_00 | 欲 | 欲 | [Wiktionary](https://en.wiktionary.org/wiki/欲) | 92200862 |
| 1131 | U+514D_00 | 免 | 免 | [Wiktionary](https://en.wiktionary.org/wiki/免) | 92160260 |
| 1138 | U+660E_U+660E_00 | 明明 | 明明 | [Wiktionary](https://en.wiktionary.org/wiki/明明) | 84420825 |
| 1139 | U+660E_U+738B_00 | 明王 | 明王 | [Wiktionary](https://en.wiktionary.org/wiki/明王) | 92250635 |
| 1148 | U+8CB7_U+8CE3_00 | 買賣 | 買賣 | [Wiktionary](https://en.wiktionary.org/wiki/買賣) | 89388440 |
| 1150 | U+8CB7_U+7968_00 | 買票 | 買票 | [Wiktionary](https://en.wiktionary.org/wiki/買票) | 81407344 |
| 1154 | U+7121_00 | 無 | 無 | [Wiktionary](https://en.wiktionary.org/wiki/無) | 92392709 |
| 1158 | U+6587_00 | 文 | 文 | [Wiktionary](https://en.wiktionary.org/wiki/文) | 93357409 |
| 1160 | U+6587_U+5B57_00 | 文字 | 文字 | [Wiktionary](https://en.wiktionary.org/wiki/文字) | 91801127 |
| 1163 | U+6587_U+5316_00 | 文化 | 文化 | [Wiktionary](https://en.wiktionary.org/wiki/文化) | 92161421 |
| 1164 | U+5C3E_00 | 尾 | 尾 | [Wiktionary](https://en.wiktionary.org/wiki/尾) | 92724478 |
| 1167 | U+7F8E_00 | 美 | 美 | [Wiktionary](https://en.wiktionary.org/wiki/美) | 92529984 |
| 1168 | U+5473_00 | 味 | 味 | [Wiktionary](https://en.wiktionary.org/wiki/味) | 92521691 |
| 1169 | U+5FAE_00 | 微 | 微 | [Wiktionary](https://en.wiktionary.org/wiki/微) | 91623590 |
| 1172 | U+7F8E_U+5FB7_00 | 美德 | 美德 | [Wiktionary](https://en.wiktionary.org/wiki/美德) | 89935658 |
| 1178 | U+7C73_U+9152_00 | 米酒 | 米酒 | [Wiktionary](https://en.wiktionary.org/wiki/米酒) | 87977434 |
| 1181 | U+7C73_U+7C89_00 | 米粉 | 米粉 | [Wiktionary](https://en.wiktionary.org/wiki/米粉) | 92016710 |
| 1186 | U+9762_00 | 面 | 面 | [Wiktionary](https://en.wiktionary.org/wiki/面) | 92937046 |
| 1187 | U+6C11_U+570B_00 | 民國 | 民國 | [Wiktionary](https://en.wiktionary.org/wiki/民國) | 91049107 |
| 1189 | U+9762_U+5C0D_00 | 面對 | 面對 | [Wiktionary](https://en.wiktionary.org/wiki/面對) | 73998645 |
| 1192 | U+9762_U+8272_00 | 面色 | 面色 | [Wiktionary](https://en.wiktionary.org/wiki/面色) | 91145347 |
| 1217 | U+9B06_00 | 鬆 | 鬆 | [Wiktionary](https://en.wiktionary.org/wiki/鬆) | 89782466 |
| 1224 | U+99DB_00 | 駛 | 駛 | [Wiktionary](https://en.wiktionary.org/wiki/駛) | 91639999 |
| 1245 | U+9583_U+720D_00 | 閃爍 | 閃爍 | [Wiktionary](https://en.wiktionary.org/wiki/閃爍) | 81428456 |
| 1249 | U+96D9_U+624B_00 | 雙手 | 雙手 | [Wiktionary](https://en.wiktionary.org/wiki/雙手) | 78685813 |
| 1255 | U+5C11_U+5E74_00 | 少年 | 少年 | [Wiktionary](https://en.wiktionary.org/wiki/少年) | 92203418 |
| 1259 | U+6D88_U+606F_00 | 消息 | 消息 | [Wiktionary](https://en.wiktionary.org/wiki/消息) | 91482534 |
| 1262 | U+9165_00 | 酥 | 酥 | [Wiktionary](https://en.wiktionary.org/wiki/酥) | 88179838 |
| 1267 | U+675F_U+7E1B_00 | 束縛 | 束縛 | [Wiktionary](https://en.wiktionary.org/wiki/束縛) | 92138611 |
| 1270 | U+55AA_00 | 喪 | 喪 | [Wiktionary](https://en.wiktionary.org/wiki/喪) | 92200160 |
| 1274 | U+4E16_U+9593_00 | 世間 | 世間 | [Wiktionary](https://en.wiktionary.org/wiki/世間) | 92090240 |
| 1276 | U+4E16_U+4E8B_00 | 世事 | 世事 | [Wiktionary](https://en.wiktionary.org/wiki/世事) | 92160014 |
| 1278 | U+897F_U+6D0B_00 | 西洋 | 西洋 | [Wiktionary](https://en.wiktionary.org/wiki/西洋) | 92441322 |
| 1284 | U+6027_U+547D_00 | 性命 | 性命 | [Wiktionary](https://en.wiktionary.org/wiki/性命) | 89627694 |
| 1285 | U+751F_U+6B7B_00 | 生死 | 生死 | [Wiktionary](https://en.wiktionary.org/wiki/生死) | 88328802 |
| 1290 | U+5C6C_U+65BC_00 | 屬於 | 屬於 | [Wiktionary](https://en.wiktionary.org/wiki/屬於) | 86409899 |
| 1293 | U+50B7_00 | 傷 | 傷 | [Wiktionary](https://en.wiktionary.org/wiki/傷) | 92690381 |
| 1294 | U+76F8_00 | 相 | 相 | [Wiktionary](https://en.wiktionary.org/wiki/相) | 92368480 |
| 1295 | U+76F8_01 | 相 | 相 | [Wiktionary](https://en.wiktionary.org/wiki/相) | 92368480 |
| 1296 | U+5E38_00 | 常 | 常 | [Wiktionary](https://en.wiktionary.org/wiki/常) | 92200403 |
| 1298 | U+4E0A_U+7B2C_00 | 上第 | 上第 | [Wiktionary](https://en.wiktionary.org/wiki/上第) | 60786655 |
| 1303 | U+50B7_U+5FC3_00 | 傷心 | 傷心 | [Wiktionary](https://en.wiktionary.org/wiki/傷心) | 80133125 |
| 1306 | U+76F8_U+4F9D_U+70BA_U+547D_00 | 相依為命 | 相依為命 | [Wiktionary](https://en.wiktionary.org/wiki/相依為命) | 80515527 |
| 1308 | U+50B7_U+5BB3_00 | 傷害 | 傷害 | [Wiktionary](https://en.wiktionary.org/wiki/傷害) | 88009795 |
| 1310 | U+4E0A_U+597D_00 | 上好 | 上好 | [Wiktionary](https://en.wiktionary.org/wiki/上好) | 78816705 |
| 1311 | U+50B7_U+75D5_00 | 傷痕 | 傷痕 | [Wiktionary](https://en.wiktionary.org/wiki/傷痕) | 92236939 |
| 1313 | U+719F_00 | 熟 | 熟 | [Wiktionary](https://en.wiktionary.org/wiki/熟) | 91975029 |
| 1317 | U+78A9_U+58EB_00 | 碩士 | 碩士 | [Wiktionary](https://en.wiktionary.org/wiki/碩士) | 87302391 |
| 1319 | U+4ED9_U+5973_00 | 仙女 | 仙女 | [Wiktionary](https://en.wiktionary.org/wiki/仙女) | 92510633 |
| 1320 | U+5148_U+751F_00 | 先生 | 先生 | [Wiktionary](https://en.wiktionary.org/wiki/先生) | 92453378 |
| 1322 | U+8A2D_U+8A08_00 | 設計 | 設計 | [Wiktionary](https://en.wiktionary.org/wiki/設計) | 92136179 |
| 1328 | U+751F_U+6A5F_00 | 生機 | 生機 | [Wiktionary](https://en.wiktionary.org/wiki/生機) | 78652510 |
| 1332 | U+6210_U+5C31_00 | 成就 | 成就 | [Wiktionary](https://en.wiktionary.org/wiki/成就) | 92468149 |
| 1336 | U+75E7_00 | 痧 | 痧 | [Wiktionary](https://en.wiktionary.org/wiki/痧) | 87573907 |
| 1341 | U+9078_U+64C7_00 | 選擇 | 選擇 | [Wiktionary](https://en.wiktionary.org/wiki/選擇) | 90950752 |
| 1353 | U+6C55_U+982D_00 | 汕頭 | 汕頭 | [Wiktionary](https://en.wiktionary.org/wiki/汕頭) | 88382826 |
| 1356 | U+7D30_00 | 細 | 細 | [Wiktionary](https://en.wiktionary.org/wiki/細) | 92676063 |
| 1358 | U+7D30_U+81A9_00 | 細膩 | 細膩 | [Wiktionary](https://en.wiktionary.org/wiki/細膩) | 90452014 |
| 1362 | U+71D2_00 | 燒 | 燒 | [Wiktionary](https://en.wiktionary.org/wiki/燒) | 92965543 |
| 1363 | U+76F8_02 | 相 | 相 | [Wiktionary](https://en.wiktionary.org/wiki/相) | 92368480 |
| 1367 | U+5C0F_U+5F1F_00 | 小弟 | 小弟 | [Wiktionary](https://en.wiktionary.org/wiki/小弟) | 92050490 |
| 1368 | U+5C0F_U+8DEF_00 | 小路 | 小路 | [Wiktionary](https://en.wiktionary.org/wiki/小路) | 92160960 |
| 1369 | U+5C0F_U+59B9_00 | 小妹 | 小妹 | [Wiktionary](https://en.wiktionary.org/wiki/小妹) | 92050477 |
| 1371 | U+5C0F_U+59B9_01 | 小妹 | 小妹 | [Wiktionary](https://en.wiktionary.org/wiki/小妹) | 92050477 |
| 1372 | U+76F8_U+9001_00 | 相送 | 相送 | [Wiktionary](https://en.wiktionary.org/wiki/相送) | 67025267 |
| 1374 | U+5C0F_U+5FC3_00 | 小心 | 小心 | [Wiktionary](https://en.wiktionary.org/wiki/小心) | 84327255 |
| 1378 | U+5C0F_U+8239_00 | 小船 | 小船 | [Wiktionary](https://en.wiktionary.org/wiki/小船) | 87501249 |
| 1387 | U+601D_00 | 思 | 思 | [Wiktionary](https://en.wiktionary.org/wiki/思) | 92220359 |
| 1390 | U+99DB_01 | 駛 | 駛 | [Wiktionary](https://en.wiktionary.org/wiki/駛) | 91639999 |
| 1392 | U+58EB_00 | 士 | 士 | [Wiktionary](https://en.wiktionary.org/wiki/士) | 92199551 |
| 1403 | U+601D_U+8003_00 | 思考 | 思考 | [Wiktionary](https://en.wiktionary.org/wiki/思考) | 93318601 |
| 1405 | U+56DB_U+65B9_00 | 四方 | 四方 | [Wiktionary](https://en.wiktionary.org/wiki/四方) | 88613989 |
| 1406 | U+5B6B_00 | 孫 | 孫 | [Wiktionary](https://en.wiktionary.org/wiki/孫) | 92638851 |
| 1407 | U+9806_00 | 順 | 順 | [Wiktionary](https://en.wiktionary.org/wiki/順) | 92202166 |
| 1409 | U+9806_U+5229_00 | 順利 | 順利 | [Wiktionary](https://en.wiktionary.org/wiki/順利) | 73990490 |
| 1412 | U+8853_00 | 術 | 術 | [Wiktionary](https://en.wiktionary.org/wiki/術) | 92201679 |
| 1413 | U+8870_00 | 衰 | 衰 | [Wiktionary](https://en.wiktionary.org/wiki/衰) | 87610770 |
| 1418 | U+96A8_00 | 隨 | 隨 | [Wiktionary](https://en.wiktionary.org/wiki/隨) | 89469144 |
| 1425 | U+53D7_U+7F6A_00 | 受罪 | 受罪 | [Wiktionary](https://en.wiktionary.org/wiki/受罪) | 78210307 |
| 1429 | U+50B7_01 | 傷 | 傷 | [Wiktionary](https://en.wiktionary.org/wiki/傷) | 92690381 |
| 1434 | U+76F8_U+601D_00 | 相思 | 相思 | [Wiktionary](https://en.wiktionary.org/wiki/相思) | 80127356 |
| 1435 | U+60F3_U+8D77_00 | 想起 | 想起 | [Wiktionary](https://en.wiktionary.org/wiki/想起) | 92139457 |
| 1438 | U+800D_00 | 耍 | 耍 | [Wiktionary](https://en.wiktionary.org/wiki/耍) | 92417069 |
| 1445 | U+65BD_00 | 施 | 施 | [Wiktionary](https://en.wiktionary.org/wiki/施) | 92544719 |
| 1446 | U+7D72_00 | 絲 | 絲 | [Wiktionary](https://en.wiktionary.org/wiki/絲) | 92201350 |
| 1448 | U+6B7B_00 | 死 | 死 | [Wiktionary](https://en.wiktionary.org/wiki/死) | 93380252 |
| 1453 | U+6642_U+6A5F_00 | 時機 | 時機 | [Wiktionary](https://en.wiktionary.org/wiki/時機) | 92161495 |
| 1458 | U+6642_U+6642_U+523B_U+523B_00 | 時時刻刻 | 時時刻刻 | [Wiktionary](https://en.wiktionary.org/wiki/時時刻刻) | 85990846 |
| 1462 | U+8FAD_U+8077_00 | 辭職 | 辭職 | [Wiktionary](https://en.wiktionary.org/wiki/辭職) | 90321503 |
| 1472 | U+65B0_U+7AF9_00 | 新竹 | 新竹 | [Wiktionary](https://en.wiktionary.org/wiki/新竹) | 90783886 |
| 1475 | U+795E_U+660E_00 | 神明 | 神明 | [Wiktionary](https://en.wiktionary.org/wiki/神明) | 92241903 |
| 1478 | U+8EAB_U+5F8C_00 | 身後 | 身後 | [Wiktionary](https://en.wiktionary.org/wiki/身後) | 92163034 |
| 1479 | U+8F9B_U+82E6_00 | 辛苦 | 辛苦 | [Wiktionary](https://en.wiktionary.org/wiki/辛苦) | 92162923 |
| 1484 | U+5931_00 | 失 | 失 | [Wiktionary](https://en.wiktionary.org/wiki/失) | 92687913 |
| 1488 | U+5931_U+7720_00 | 失眠 | 失眠 | [Wiktionary](https://en.wiktionary.org/wiki/失眠) | 90863430 |
| 1492 | U+6027_U+547D_01 | 性命 | 性命 | [Wiktionary](https://en.wiktionary.org/wiki/性命) | 89627694 |
| 1501 | U+5FC3_U+8072_00 | 心聲 | 心聲 | [Wiktionary](https://en.wiktionary.org/wiki/心聲) | 78627406 |
| 1502 | U+5FC3_U+9178_00 | 心酸 | 心酸 | [Wiktionary](https://en.wiktionary.org/wiki/心酸) | 74007871 |
| 1503 | U+5FC3_U+5B89_00 | 心安 | 心安 | [Wiktionary](https://en.wiktionary.org/wiki/心安) | 73629812 |
| 1505 | U+5FC3_U+610F_00 | 心意 | 心意 | [Wiktionary](https://en.wiktionary.org/wiki/心意) | 92234485 |
| 1506 | U+5FC3_U+60C5_00 | 心情 | 心情 | [Wiktionary](https://en.wiktionary.org/wiki/心情) | 92423802 |
| 1507 | U+5FC3_U+60C5_01 | 心情 | 心情 | [Wiktionary](https://en.wiktionary.org/wiki/心情) | 92423802 |
| 1508 | U+5FC3_U+982D_00 | 心頭 | 心頭 | [Wiktionary](https://en.wiktionary.org/wiki/心頭) | 78627471 |
| 1509 | U+5FC3_U+75BC_00 | 心疼 | 心疼 | [Wiktionary](https://en.wiktionary.org/wiki/心疼) | 77764237 |
| 1512 | U+5FC3_U+865B_00 | 心虛 | 心虛 | [Wiktionary](https://en.wiktionary.org/wiki/心虛) | 61690821 |
| 1522 | U+963F_U+5ABD_00 | 阿媽 | 阿媽 | [Wiktionary](https://en.wiktionary.org/wiki/阿媽) | 92708668 |
| 1523 | U+963F_U+5A46_00 | 阿婆 | 阿婆 | [Wiktionary](https://en.wiktionary.org/wiki/阿婆) | 92256292 |
| 1526 | U+963F_U+59E8_00 | 阿姨 | 阿姨 | [Wiktionary](https://en.wiktionary.org/wiki/阿姨) | 90893778 |
| 1528 | U+963F_U+53D4_00 | 阿叔 | 阿叔 | [Wiktionary](https://en.wiktionary.org/wiki/阿叔) | 91974983 |
| 1532 | U+6C83_00 | 沃 | 沃 | [Wiktionary](https://en.wiktionary.org/wiki/沃) | 91146083 |
| 1534 | U+5B89_00 | 安 | 安 | [Wiktionary](https://en.wiktionary.org/wiki/安) | 93017121 |
| 1537 | U+5B89_U+5FC3_00 | 安心 | 安心 | [Wiktionary](https://en.wiktionary.org/wiki/安心) | 92199444 |
| 1541 | U+5B89_U+6EAA_00 | 安溪 | 安溪 | [Wiktionary](https://en.wiktionary.org/wiki/安溪) | 92020569 |
| 1555 | U+7D05_U+8C46_U+6E6F_00 | 紅豆湯 | 紅豆湯 | [Wiktionary](https://en.wiktionary.org/wiki/紅豆湯) | 85536732 |
| 1559 | U+7D05_U+6BDB_U+6A4B_00 | 紅毛橋 | 紅毛橋 | [Wiktionary](https://en.wiktionary.org/wiki/紅毛橋) | 78661098 |
| 1564 | U+7D05_U+5C71_00 | 紅山 | 紅山 | [Wiktionary](https://en.wiktionary.org/wiki/紅山) | 87984166 |
| 1566 | U+7D05_U+87F3_00 | 紅蟳 | 紅蟳 | [Wiktionary](https://en.wiktionary.org/wiki/紅蟳) | 88300209 |
| 1567 | U+7D05_U+82B1_00 | 紅花 | 紅花 | [Wiktionary](https://en.wiktionary.org/wiki/紅花) | 92290669 |
| 1571 | U+5F8C_U+6E2F_00 | 後港 | 後港 | [Wiktionary](https://en.wiktionary.org/wiki/後港) | 76644626 |
| 1581 | U+91CE_00 | 野 | 野 | [Wiktionary](https://en.wiktionary.org/wiki/野) | 92917761 |
| 1584 | U+91CE_U+9CE5_00 | 野鳥 | 野鳥 | [Wiktionary](https://en.wiktionary.org/wiki/野鳥) | 81843284 |
| 1600 | U+5996_U+5B7D_00 | 妖孽 | 妖孽 | [Wiktionary](https://en.wiktionary.org/wiki/妖孽) | 81032516 |
| 1601 | U+592D_U+58FD_00 | 夭壽 | 夭壽 | [Wiktionary](https://en.wiktionary.org/wiki/夭壽) | 78617355 |
| 1605 | U+80E1_00 | 胡 | 胡 | [Wiktionary](https://en.wiktionary.org/wiki/胡) | 92678608 |
| 1618 | U+6E56_U+6C34_00 | 湖水 | 湖水 | [Wiktionary](https://en.wiktionary.org/wiki/湖水) | 90122829 |
| 1621 | U+5F80_00 | 往 | 往 | [Wiktionary](https://en.wiktionary.org/wiki/往) | 92200442 |
| 1622 | U+738B_00 | 王 | 王 | [Wiktionary](https://en.wiktionary.org/wiki/王) | 92201087 |
| 1624 | U+5F80_U+5F80_00 | 往往 | 往往 | [Wiktionary](https://en.wiktionary.org/wiki/往往) | 91019593 |
| 1628 | U+4E0B_00 | 下 | 下 | [Wiktionary](https://en.wiktionary.org/wiki/下) | 92720610 |
| 1629 | U+4E0B_01 | 下 | 下 | [Wiktionary](https://en.wiktionary.org/wiki/下) | 92720610 |
| 1630 | U+6328_00 | 挨 | 挨 | [Wiktionary](https://en.wiktionary.org/wiki/挨) | 88896042 |
| 1631 | U+5EC8_U+9580_00 | 廈門 | 廈門 | [Wiktionary](https://en.wiktionary.org/wiki/廈門) | 92682967 |
| 1634 | U+7D04_U+675F_00 | 約束 | 約束 | [Wiktionary](https://en.wiktionary.org/wiki/約束) | 92135330 |
| 1635 | U+7D04_U+6703_00 | 約會 | 約會 | [Wiktionary](https://en.wiktionary.org/wiki/約會) | 89999327 |
| 1636 | U+694A_00 | 楊 | 楊 | [Wiktionary](https://en.wiktionary.org/wiki/楊) | 92547702 |
| 1644 | U+7DE3_00 | 緣 | 緣 | [Wiktionary](https://en.wiktionary.org/wiki/緣) | 92367755 |
| 1648 | U+925B_U+7B46_00 | 鉛筆 | 鉛筆 | [Wiktionary](https://en.wiktionary.org/wiki/鉛筆) | 92163178 |
| 1653 | U+61C9_U+8A72_00 | 應該 | 應該 | [Wiktionary](https://en.wiktionary.org/wiki/應該) | 88464947 |
| 1655 | U+82F1_U+8A9E_00 | 英語 | 英語 | [Wiktionary](https://en.wiktionary.org/wiki/英語) | 92162631 |
| 1659 | U+6C38_U+6625_00 | 永春 | 永春 | [Wiktionary](https://en.wiktionary.org/wiki/永春) | 92113260 |
| 1666 | U+6028_00 | 怨 | 怨 | [Wiktionary](https://en.wiktionary.org/wiki/怨) | 92200461 |
| 1670 | U+5B8C_U+6210_00 | 完成 | 完成 | [Wiktionary](https://en.wiktionary.org/wiki/完成) | 92136229 |
| 1673 | U+5B8C_U+5168_00 | 完全 | 完全 | [Wiktionary](https://en.wiktionary.org/wiki/完全) | 92282830 |
| 1679 | U+6028_U+6068_00 | 怨恨 | 怨恨 | [Wiktionary](https://en.wiktionary.org/wiki/怨恨) | 91346020 |
| 1682 | U+8D8A_U+5357_U+4EBA_00 | 越南人 | 越南人 | [Wiktionary](https://en.wiktionary.org/wiki/越南人) | 89963049 |
| 1690 | U+7897_U+7CBF_00 | 碗粿 | 碗粿 | [Wiktionary](https://en.wiktionary.org/wiki/碗粿) | 90474223 |
| 1692 | U+6D3B_U+52D5_00 | 活動 | 活動 | [Wiktionary](https://en.wiktionary.org/wiki/活動) | 92135436 |
| 1697 | U+81C6_00 | 臆 | 臆 | [Wiktionary](https://en.wiktionary.org/wiki/臆) | 92201460 |
| 1699 | U+5B87_U+5B99_00 | 宇宙 | 宇宙 | [Wiktionary](https://en.wiktionary.org/wiki/宇宙) | 92428730 |
| 1704 | U+6EAB_00 | 溫 | 溫 | [Wiktionary](https://en.wiktionary.org/wiki/溫) | 90294530 |
| 1709 | U+904B_U+52D5_00 | 運動 | 運動 | [Wiktionary](https://en.wiktionary.org/wiki/運動) | 92778367 |
| 1710 | U+6EAB_U+67D4_00 | 溫柔 | 溫柔 | [Wiktionary](https://en.wiktionary.org/wiki/溫柔) | 81416661 |
| 1714 | U+6069_U+611B_00 | 恩愛 | 恩愛 | [Wiktionary](https://en.wiktionary.org/wiki/恩愛) | 88203635 |
| 1715 | U+6EAB_U+5B58_00 | 溫存 | 溫存 | [Wiktionary](https://en.wiktionary.org/wiki/溫存) | 86674548 |
| 1718 | U+5283_00 | 劃 | 劃 | [Wiktionary](https://en.wiktionary.org/wiki/劃) | 93378394 |
| 1721 | U+5049_U+5927_00 | 偉大 | 偉大 | [Wiktionary](https://en.wiktionary.org/wiki/偉大) | 92198511 |
| 1727 | U+59D4_U+5C48_00 | 委屈 | 委屈 | [Wiktionary](https://en.wiktionary.org/wiki/委屈) | 91345507 |
| 1728 | U+907A_U+61BE_00 | 遺憾 | 遺憾 | [Wiktionary](https://en.wiktionary.org/wiki/遺憾) | 88328250 |
| 1746 | U+6709_U+60C5_00 | 有情 | 有情 | [Wiktionary](https://en.wiktionary.org/wiki/有情) | 78637581 |
| 1750 | U+694A_01 | 楊 | 楊 | [Wiktionary](https://en.wiktionary.org/wiki/楊) | 92547702 |
| 1754 | U+9EC3_00 | 黃 | 黃 | [Wiktionary](https://en.wiktionary.org/wiki/黃) | 92541845 |
| 1767 | U+4EE5_U+5F8C_00 | 以後 | 以後 | [Wiktionary](https://en.wiktionary.org/wiki/以後) | 91812023 |
| 1769 | U+4F9D_U+501A_00 | 依倚 | 依倚 | [Wiktionary](https://en.wiktionary.org/wiki/依倚) | 89099671 |
| 1774 | U+5370_U+5EA6_U+4EBA_00 | 印度人 | 印度人 | [Wiktionary](https://en.wiktionary.org/wiki/印度人) | 84738131 |
| 1781 | U+4E00_U+751F_00 | 一生 | 一生 | [Wiktionary](https://en.wiktionary.org/wiki/一生) | 88203547 |
| 1783 | U+5713_00 | 圓 | 圓 | [Wiktionary](https://en.wiktionary.org/wiki/圓) | 92645376 |
| 1787 | U+9670_U+98A8_00 | 陰風 | 陰風 | [Wiktionary](https://en.wiktionary.org/wiki/陰風) | 78685213 |
| 1791 | U+65E9_U+8D77_00 | 早起 | 早起 | [Wiktionary](https://en.wiktionary.org/wiki/早起) | 92079524 |
| 1793 | U+66FE_00 | 曾 | 曾 | [Wiktionary](https://en.wiktionary.org/wiki/曾) | 92200704 |
| 1797 | U+7BC0_00 | 節 | 節 | [Wiktionary](https://en.wiktionary.org/wiki/節) | 92694789 |
| 1805 | U+7CBD_00 | 粽 | 粽 | [Wiktionary](https://en.wiktionary.org/wiki/粽) | 92201326 |
| 1812 | U+5728_00 | 在 | 在 | [Wiktionary](https://en.wiktionary.org/wiki/在) | 92701669 |
| 1813 | U+518D_U+898B_00 | 再見 | 再見 | [Wiktionary](https://en.wiktionary.org/wiki/再見) | 92160306 |
| 1814 | U+683D_U+57F9_00 | 栽培 | 栽培 | [Wiktionary](https://en.wiktionary.org/wiki/栽培) | 92395698 |
| 1822 | U+60C5_00 | 情 | 情 | [Wiktionary](https://en.wiktionary.org/wiki/情) | 92737764 |
| 1823 | U+8AA0_00 | 誠 | 誠 | [Wiktionary](https://en.wiktionary.org/wiki/誠) | 92162824 |
| 1827 | U+66AB_U+6642_00 | 暫時 | 暫時 | [Wiktionary](https://en.wiktionary.org/wiki/暫時) | 86462161 |
| 1832 | U+63A5_U+53D7_00 | 接受 | 接受 | [Wiktionary](https://en.wiktionary.org/wiki/接受) | 90336303 |
| 1833 | U+6F33_U+5DDE_00 | 漳州 | 漳州 | [Wiktionary](https://en.wiktionary.org/wiki/漳州) | 92113391 |
| 1835 | U+624D_00 | 才 | 才 | [Wiktionary](https://en.wiktionary.org/wiki/才) | 92200519 |
| 1837 | U+96BB_00 | 隻 | 隻 | [Wiktionary](https://en.wiktionary.org/wiki/隻) | 91974948 |
| 1850 | U+7167_U+9867_00 | 照顧 | 照顧 | [Wiktionary](https://en.wiktionary.org/wiki/照顧) | 92162073 |
| 1859 | U+8E64_00 | 蹤 | 蹤 | [Wiktionary](https://en.wiktionary.org/wiki/蹤) | 92201857 |
| 1860 | U+7E3D_00 | 總 | 總 | [Wiktionary](https://en.wiktionary.org/wiki/總) | 91718366 |
| 1864 | U+9F4B_00 | 齋 | 齋 | [Wiktionary](https://en.wiktionary.org/wiki/齋) | 92202306 |
| 1866 | U+796D_00 | 祭 | 祭 | [Wiktionary](https://en.wiktionary.org/wiki/祭) | 92201224 |
| 1871 | U+795D_00 | 祝 | 祝 | [Wiktionary](https://en.wiktionary.org/wiki/祝) | 92201220 |
| 1872 | U+8DB3_00 | 足 | 足 | [Wiktionary](https://en.wiktionary.org/wiki/足) | 93378193 |
| 1874 | U+795D_U+798F_00 | 祝福 | 祝福 | [Wiktionary](https://en.wiktionary.org/wiki/祝福) | 92137966 |
| 1880 | U+7D42_U+9EDE_00 | 終點 | 終點 | [Wiktionary](https://en.wiktionary.org/wiki/終點) | 85020044 |
| 1884 | U+5F70_U+5316_00 | 彰化 | 彰化 | [Wiktionary](https://en.wiktionary.org/wiki/彰化) | 88211325 |
| 1887 | U+714E_00 | 煎 | 煎 | [Wiktionary](https://en.wiktionary.org/wiki/煎) | 90293501 |
| 1891 | U+6298_U+78E8_00 | 折磨 | 折磨 | [Wiktionary](https://en.wiktionary.org/wiki/折磨) | 77806496 |
| 1895 | U+60C5_01 | 情 | 情 | [Wiktionary](https://en.wiktionary.org/wiki/情) | 92737764 |
| 1896 | U+66FE_01 | 曾 | 曾 | [Wiktionary](https://en.wiktionary.org/wiki/曾) | 92200704 |
| 1897 | U+66FE_U+7D93_00 | 曾經 | 曾經 | [Wiktionary](https://en.wiktionary.org/wiki/曾經) | 73991377 |
| 1899 | U+653F_U+6CBB_00 | 政治 | 政治 | [Wiktionary](https://en.wiktionary.org/wiki/政治) | 92293137 |
| 1900 | U+524D_U+8DEF_00 | 前路 | 前路 | [Wiktionary](https://en.wiktionary.org/wiki/前路) | 90522585 |
| 1904 | U+60C5_U+610F_00 | 情意 | 情意 | [Wiktionary](https://en.wiktionary.org/wiki/情意) | 84463772 |
| 1910 | U+5EA7_00 | 座 | 座 | [Wiktionary](https://en.wiktionary.org/wiki/座) | 92368189 |
| 1911 | U+505A_U+5DE5_00 | 做工 | 做工 | [Wiktionary](https://en.wiktionary.org/wiki/做工) | 80949463 |
| 1918 | U+901D_00 | 逝 | 逝 | [Wiktionary](https://en.wiktionary.org/wiki/逝) | 92162998 |
| 1923 | U+5168_U+90E8_00 | 全部 | 全部 | [Wiktionary](https://en.wiktionary.org/wiki/全部) | 92198587 |
| 1924 | U+5168_U+4E16_U+754C_00 | 全世界 | 全世界 | [Wiktionary](https://en.wiktionary.org/wiki/全世界) | 90825441 |
| 1927 | U+6CC9_U+5DDE_00 | 泉州 | 泉州 | [Wiktionary](https://en.wiktionary.org/wiki/泉州) | 93296116 |
| 1928 | U+7D55_U+671B_00 | 絕望 | 絕望 | [Wiktionary](https://en.wiktionary.org/wiki/絕望) | 91071695 |
| 1930 | U+600E_U+6A23_00 | 怎樣 | 怎樣 | [Wiktionary](https://en.wiktionary.org/wiki/怎樣) | 91062677 |
| 1933 | U+9F4A_00 | 齊 | 齊 | [Wiktionary](https://en.wiktionary.org/wiki/齊) | 92718402 |
| 1935 | U+505A_U+5DE5_01 | 做工 | 做工 | [Wiktionary](https://en.wiktionary.org/wiki/做工) | 80949463 |
| 1936 | U+505A_U+5B98_00 | 做官 | 做官 | [Wiktionary](https://en.wiktionary.org/wiki/做官) | 92051824 |
| 1938 | U+505A_U+4EBA_00 | 做人 | 做人 | [Wiktionary](https://en.wiktionary.org/wiki/做人) | 91089697 |
| 1941 | U+505A_U+4F34_00 | 做伴 | 做伴 | [Wiktionary](https://en.wiktionary.org/wiki/做伴) | 89500048 |
| 1943 | U+62DB_00 | 招 | 招 | [Wiktionary](https://en.wiktionary.org/wiki/招) | 92200552 |
| 1948 | U+77F3_U+7345_00 | 石獅 | 石獅 | [Wiktionary](https://en.wiktionary.org/wiki/石獅) | 89152256 |
| 1955 | U+6CE8_00 | 注 | 注 | [Wiktionary](https://en.wiktionary.org/wiki/注) | 92161846 |
| 1961 | U+81EA_U+5DF1_00 | 自己 | 自己 | [Wiktionary](https://en.wiktionary.org/wiki/自己) | 92736895 |
| 1963 | U+5B50_U+5F1F_00 | 子弟 | 子弟 | [Wiktionary](https://en.wiktionary.org/wiki/子弟) | 92742096 |
| 1966 | U+6CE8_U+5165_00 | 注入 | 注入 | [Wiktionary](https://en.wiktionary.org/wiki/注入) | 92276672 |
| 1970 | U+5B50_U+6C11_00 | 子民 | 子民 | [Wiktionary](https://en.wiktionary.org/wiki/子民) | 86833328 |
| 1974 | U+81EA_U+5728_00 | 自在 | 自在 | [Wiktionary](https://en.wiktionary.org/wiki/自在) | 90092338 |
| 1976 | U+81EA_U+4F5C_U+591A_U+60C5_00 | 自作多情 | 自作多情 | [Wiktionary](https://en.wiktionary.org/wiki/自作多情) | 60798650 |
| 1981 | U+9663_00 | 陣 | 陣 | [Wiktionary](https://en.wiktionary.org/wiki/陣) | 92202110 |
| 1982 | U+5C0A_U+56B4_00 | 尊嚴 | 尊嚴 | [Wiktionary](https://en.wiktionary.org/wiki/尊嚴) | 90956257 |
| 1983 | U+6E96_U+5099_00 | 準備 | 準備 | [Wiktionary](https://en.wiktionary.org/wiki/準備) | 92135372 |
| 1991 | U+9189_00 | 醉 | 醉 | [Wiktionary](https://en.wiktionary.org/wiki/醉) | 92638585 |
| 1994 | U+5B88_00 | 守 | 守 | [Wiktionary](https://en.wiktionary.org/wiki/守) | 92708653 |
| 1998 | U+9152_U+4ED9_00 | 酒仙 | 酒仙 | [Wiktionary](https://en.wiktionary.org/wiki/酒仙) | 86460786 |
| 1999 | U+5DDE_U+5E9C_00 | 州府 | 州府 | [Wiktionary](https://en.wiktionary.org/wiki/州府) | 90247469 |
| 2001 | U+6F33_U+6D66_00 | 漳浦 | 漳浦 | [Wiktionary](https://en.wiktionary.org/wiki/漳浦) | 91770190 |
| 2002 | U+5B50_U+5F1F_01 | 子弟 | 子弟 | [Wiktionary](https://en.wiktionary.org/wiki/子弟) | 92742096 |
| 2003 | U+599D_00 | 妝 | 妝 | [Wiktionary](https://en.wiktionary.org/wiki/妝) | 87573136 |
| 2005 | U+947D_U+5B54_00 | 鑽孔 | 鑽孔 | [Wiktionary](https://en.wiktionary.org/wiki/鑽孔) | 84081998 |
| 2009 | U+6307_00 | 指 | 指 | [Wiktionary](https://en.wiktionary.org/wiki/指) | 92536843 |
| 2016 | U+53EA_U+8981_00 | 只要 | 只要 | [Wiktionary](https://en.wiktionary.org/wiki/只要) | 78478683 |
| 2017 | U+6307_U+5F15_00 | 指引 | 指引 | [Wiktionary](https://en.wiktionary.org/wiki/指引) | 77437774 |
| 2018 | U+5FD7_U+6C23_00 | 志氣 | 志氣 | [Wiktionary](https://en.wiktionary.org/wiki/志氣) | 87332469 |
| 2020 | U+9707_00 | 震 | 震 | [Wiktionary](https://en.wiktionary.org/wiki/震) | 92089012 |
| 2022 | U+6649_U+6C5F_00 | 晉江 | 晉江 | [Wiktionary](https://en.wiktionary.org/wiki/晉江) | 87986695 |
| 2024 | U+771F_U+5FC3_00 | 真心 | 真心 | [Wiktionary](https://en.wiktionary.org/wiki/真心) | 90816730 |
| 2037 | U+4E00_U+9EDE_00 | 一點 | 一點 | [Wiktionary](https://en.wiktionary.org/wiki/一點) | 80122719 |
| 2045 | U+4E00_U+65E5_00 | 一日 | 一日 | [Wiktionary](https://en.wiktionary.org/wiki/一日) | 93357449 |
| 2047 | U+4E00_U+8DEF_00 | 一路 | 一路 | [Wiktionary](https://en.wiktionary.org/wiki/一路) | 88146187 |
| 2050 | U+4E00_U+6B65_00 | 一步 | 一步 | [Wiktionary](https://en.wiktionary.org/wiki/一步) | 78597900 |
| 2059 | U+4E00_U+9762_00 | 一面 | 一面 | [Wiktionary](https://en.wiktionary.org/wiki/一面) | 84731664 |
| 2060 | U+4E00_U+8072_00 | 一聲 | 一聲 | [Wiktionary](https://en.wiktionary.org/wiki/一聲) | 78597944 |
| 2062 | U+4E00_U+6642_00 | 一時 | 一時 | [Wiktionary](https://en.wiktionary.org/wiki/一時) | 92159953 |
| 2071 | U+4E00_U+7A2E_00 | 一種 | 一種 | [Wiktionary](https://en.wiktionary.org/wiki/一種) | 92159960 |
| 2084 | U+659F_U+914C_00 | 斟酌 | 斟酌 | [Wiktionary](https://en.wiktionary.org/wiki/斟酌) | 86628775 |
| 2087 | U+7092_00 | 炒 | 炒 | [Wiktionary](https://en.wiktionary.org/wiki/炒) | 92440779 |
| 2089 | U+5435_U+9B27_00 | 吵鬧 | 吵鬧 | [Wiktionary](https://en.wiktionary.org/wiki/吵鬧) | 84116666 |
| 2093 | U+5435_U+5435_U+9B27_U+9B27_00 | 吵吵鬧鬧 | 吵吵鬧鬧 | [Wiktionary](https://en.wiktionary.org/wiki/吵吵鬧鬧) | 76612817 |
| 2098 | U+85CF_00 | 藏 | 藏 | [Wiktionary](https://en.wiktionary.org/wiki/藏) | 93388003 |
| 2102 | U+5435_U+9B27_01 | 吵鬧 | 吵鬧 | [Wiktionary](https://en.wiktionary.org/wiki/吵鬧) | 84116666 |
| 2105 | U+5F69_00 | 彩 | 彩 | [Wiktionary](https://en.wiktionary.org/wiki/彩) | 92161149 |
| 2108 | U+83DC_U+5E02_00 | 菜市 | 菜市 | [Wiktionary](https://en.wiktionary.org/wiki/菜市) | 78669637 |
| 2113 | U+8ECA_U+7AD9_00 | 車站 | 車站 | [Wiktionary](https://en.wiktionary.org/wiki/車站) | 87965680 |
| 2116 | U+665F_00 | 晟 | 晟 | [Wiktionary](https://en.wiktionary.org/wiki/晟) | 92200667 |
| 2117 | U+8ACB_U+554F_00 | 請問 | 請問 | [Wiktionary](https://en.wiktionary.org/wiki/請問) | 84549650 |
| 2119 | U+7C64_00 | 籤 | 籤 | [Wiktionary](https://en.wiktionary.org/wiki/籤) | 91802429 |
| 2123 | U+521D_00 | 初 | 初 | [Wiktionary](https://en.wiktionary.org/wiki/初) | 92199988 |
| 2127 | U+521D_U+6200_00 | 初戀 | 初戀 | [Wiktionary](https://en.wiktionary.org/wiki/初戀) | 92793812 |
| 2136 | U+9752_U+8272_00 | 青色 | 青色 | [Wiktionary](https://en.wiktionary.org/wiki/青色) | 89858213 |
| 2137 | U+751F_U+751F_00 | 生生 | 生生 | [Wiktionary](https://en.wiktionary.org/wiki/生生) | 78652602 |
| 2141 | U+6C96_00 | 沖 | 沖 | [Wiktionary](https://en.wiktionary.org/wiki/沖) | 90925169 |
| 2142 | U+885D_00 | 衝 | 衝 | [Wiktionary](https://en.wiktionary.org/wiki/衝) | 89579978 |
| 2143 | U+8594_U+8587_00 | 薔薇 | 薔薇 | [Wiktionary](https://en.wiktionary.org/wiki/薔薇) | 92264967 |
| 2145 | U+5343_U+91D1_00 | 千金 | 千金 | [Wiktionary](https://en.wiktionary.org/wiki/千金) | 92198817 |
| 2151 | U+5207_U+65B7_00 | 切斷 | 切斷 | [Wiktionary](https://en.wiktionary.org/wiki/切斷) | 91381784 |
| 2158 | U+6E05_U+9192_00 | 清醒 | 清醒 | [Wiktionary](https://en.wiktionary.org/wiki/清醒) | 78814374 |
| 2159 | U+6E05_U+695A_00 | 清楚 | 清楚 | [Wiktionary](https://en.wiktionary.org/wiki/清楚) | 91637552 |
| 2161 | U+6E05_U+9192_01 | 清醒 | 清醒 | [Wiktionary](https://en.wiktionary.org/wiki/清醒) | 78814374 |
| 2166 | U+6E05_U+83EF_00 | 清華 | 清華 | [Wiktionary](https://en.wiktionary.org/wiki/清華) | 92681062 |
| 2169 | U+8521_U+539D_U+6E2F_00 | 蔡厝港 | 蔡厝港 | [Wiktionary](https://en.wiktionary.org/wiki/蔡厝港) | 75694055 |
| 2173 | U+521D_U+4E00_U+5341_U+4E94_00 | 初一十五 | 初一十五 | [Wiktionary](https://en.wiktionary.org/wiki/初一十五) | 83079220 |
| 2176 | U+7B11_U+5BB9_00 | 笑容 | 笑容 | [Wiktionary](https://en.wiktionary.org/wiki/笑容) | 92749824 |
| 2187 | U+6625_U+590F_U+79CB_U+51AC_00 | 春夏秋冬 | 春夏秋冬 | [Wiktionary](https://en.wiktionary.org/wiki/春夏秋冬) | 92423723 |
| 2188 | U+6625_U+96E8_00 | 春雨 | 春雨 | [Wiktionary](https://en.wiktionary.org/wiki/春雨) | 92272321 |
| 2194 | U+51FA_U+529B_00 | 出力 | 出力 | [Wiktionary](https://en.wiktionary.org/wiki/出力) | 92759940 |
| 2200 | U+51FA_U+73FE_00 | 出現 | 出現 | [Wiktionary](https://en.wiktionary.org/wiki/出現) | 92135605 |
| 2203 | U+50AC_00 | 催 | 催 | [Wiktionary](https://en.wiktionary.org/wiki/催) | 92199938 |
| 2211 | U+624B_U+5DFE_00 | 手巾 | 手巾 | [Wiktionary](https://en.wiktionary.org/wiki/手巾) | 92290512 |
| 2216 | U+6A39_U+6728_00 | 樹木 | 樹木 | [Wiktionary](https://en.wiktionary.org/wiki/樹木) | 89542351 |
| 2223 | U+75F4_00 | 痴 | 痴 | [Wiktionary](https://en.wiktionary.org/wiki/痴) | 92162150 |
| 2228 | U+523A_U+6FC0_00 | 刺激 | 刺激 | [Wiktionary](https://en.wiktionary.org/wiki/刺激) | 92138720 |
| 2232 | U+75F4_U+60C5_00 | 痴情 | 痴情 | [Wiktionary](https://en.wiktionary.org/wiki/痴情) | 92263603 |
| 2237 | U+89AA_U+53CB_00 | 親友 | 親友 | [Wiktionary](https://en.wiktionary.org/wiki/親友) | 92162889 |
| 2238 | U+89AA_U+60C5_00 | 親情 | 親情 | [Wiktionary](https://en.wiktionary.org/wiki/親情) | 86403989 |
| 2239 | U+89AA_U+60C5_01 | 親情 | 親情 | [Wiktionary](https://en.wiktionary.org/wiki/親情) | 86403989 |
| 2247 | U+4E03_U+65E9_U+516B_U+65E9_00 | 七早八早 | 七早八早 | [Wiktionary](https://en.wiktionary.org/wiki/七早八早) | 82590586 |
| 2255 | U+6DF1_U+5751_00 | 深坑 | 深坑 | [Wiktionary](https://en.wiktionary.org/wiki/深坑) | 87966593 |
| 2268 | U+727D_00 | 牽 | 牽 | [Wiktionary](https://en.wiktionary.org/wiki/牽) | 92644942 |
| 2269 | U+582A_00 | 堪 | 堪 | [Wiktionary](https://en.wiktionary.org/wiki/堪) | 91585643 |
| 2274 | U+574E_U+5777_00 | 坎坷 | 坎坷 | [Wiktionary](https://en.wiktionary.org/wiki/坎坷) | 89218314 |
| 2278 | U+7A7A_U+865B_00 | 空虛 | 空虛 | [Wiktionary](https://en.wiktionary.org/wiki/空虛) | 89925814 |
| 2288 | U+6B20_U+50B5_00 | 欠債 | 欠債 | [Wiktionary](https://en.wiktionary.org/wiki/欠債) | 87485030 |
| 2289 | U+5DE7_00 | 巧 | 巧 | [Wiktionary](https://en.wiktionary.org/wiki/巧) | 92917745 |
| 2291 | U+9846_00 | 顆 | 顆 | [Wiktionary](https://en.wiktionary.org/wiki/顆) | 92717143 |
| 2292 | U+82E6_00 | 苦 | 苦 | [Wiktionary](https://en.wiktionary.org/wiki/苦) | 93386203 |
| 2294 | U+82E6_U+6F80_00 | 苦澀 | 苦澀 | [Wiktionary](https://en.wiktionary.org/wiki/苦澀) | 69576002 |
| 2296 | U+82E6_U+695A_00 | 苦楚 | 苦楚 | [Wiktionary](https://en.wiktionary.org/wiki/苦楚) | 88203591 |
| 2297 | U+82E6_U+52F8_00 | 苦勸 | 苦勸 | [Wiktionary](https://en.wiktionary.org/wiki/苦勸) | 71080729 |
| 2307 | U+8003_00 | 考 | 考 | [Wiktionary](https://en.wiktionary.org/wiki/考) | 91916145 |
| 2308 | U+9760_00 | 靠 | 靠 | [Wiktionary](https://en.wiktionary.org/wiki/靠) | 92743165 |
| 2309 | U+53EF_U+6190_00 | 可憐 | 可憐 | [Wiktionary](https://en.wiktionary.org/wiki/可憐) | 92270942 |
| 2310 | U+53EF_U+80FD_00 | 可能 | 可能 | [Wiktionary](https://en.wiktionary.org/wiki/可能) | 92160515 |
| 2312 | U+53EF_U+60DC_00 | 可惜 | 可惜 | [Wiktionary](https://en.wiktionary.org/wiki/可惜) | 92296311 |
| 2314 | U+53EF_U+4EE5_00 | 可以 | 可以 | [Wiktionary](https://en.wiktionary.org/wiki/可以) | 92757323 |
| 2318 | U+6B3E_00 | 款 | 款 | [Wiktionary](https://en.wiktionary.org/wiki/款) | 92200863 |
| 2319 | U+770B_00 | 看 | 看 | [Wiktionary](https://en.wiktionary.org/wiki/看) | 92643982 |
| 2320 | U+770B_U+9867_00 | 看顧 | 看顧 | [Wiktionary](https://en.wiktionary.org/wiki/看顧) | 89761793 |
| 2323 | U+770B_U+7834_00 | 看破 | 看破 | [Wiktionary](https://en.wiktionary.org/wiki/看破) | 92139623 |
| 2325 | U+5FEB_00 | 快 | 快 | [Wiktionary](https://en.wiktionary.org/wiki/快) | 92694754 |
| 2328 | U+8EC0_00 | 軀 | 軀 | [Wiktionary](https://en.wiktionary.org/wiki/軀) | 92930105 |
| 2330 | U+56F0_U+96E3_00 | 困難 | 困難 | [Wiktionary](https://en.wiktionary.org/wiki/困難) | 90950751 |
| 2333 | U+6C23_00 | 氣 | 氣 | [Wiktionary](https://en.wiktionary.org/wiki/氣) | 92715933 |
| 2334 | U+6C23_U+529B_00 | 氣力 | 氣力 | [Wiktionary](https://en.wiktionary.org/wiki/氣力) | 91749431 |
| 2335 | U+958B_U+9580_00 | 開門 | 開門 | [Wiktionary](https://en.wiktionary.org/wiki/開門) | 92286532 |
| 2337 | U+958B_U+8ECA_00 | 開車 | 開車 | [Wiktionary](https://en.wiktionary.org/wiki/開車) | 85011357 |
| 2339 | U+958B_U+82B1_00 | 開花 | 開花 | [Wiktionary](https://en.wiktionary.org/wiki/開花) | 92261245 |
| 2340 | U+5FEB_U+6D3B_00 | 快活 | 快活 | [Wiktionary](https://en.wiktionary.org/wiki/快活) | 92958326 |
| 2343 | U+8D77_00 | 起 | 起 | [Wiktionary](https://en.wiktionary.org/wiki/起) | 92737700 |
| 2344 | U+6C23_01 | 氣 | 氣 | [Wiktionary](https://en.wiktionary.org/wiki/氣) | 92715933 |
| 2346 | U+6C23_U+5473_00 | 氣味 | 氣味 | [Wiktionary](https://en.wiktionary.org/wiki/氣味) | 91676297 |
| 2348 | U+8D77_U+8EAB_00 | 起身 | 起身 | [Wiktionary](https://en.wiktionary.org/wiki/起身) | 92737620 |
| 2351 | U+8F15_U+9B06_00 | 輕鬆 | 輕鬆 | [Wiktionary](https://en.wiktionary.org/wiki/輕鬆) | 90320998 |
| 2357 | U+7434_00 | 琴 | 琴 | [Wiktionary](https://en.wiktionary.org/wiki/琴) | 92201099 |
| 2360 | U+8B80_U+66F8_00 | 讀書 | 讀書 | [Wiktionary](https://en.wiktionary.org/wiki/讀書) | 91350480 |
| 2366 | U+901A_00 | 通 | 通 | [Wiktionary](https://en.wiktionary.org/wiki/通) | 92693582 |
| 2367 | U+87F2_00 | 蟲 | 蟲 | [Wiktionary](https://en.wiktionary.org/wiki/蟲) | 92645339 |
| 2368 | U+7A97_U+5916_00 | 窗外 | 窗外 | [Wiktionary](https://en.wiktionary.org/wiki/窗外) | 91192537 |
| 2371 | U+900F_00 | 透 | 透 | [Wiktionary](https://en.wiktionary.org/wiki/透) | 92201930 |
| 2374 | U+982D_U+8166_00 | 頭腦 | 頭腦 | [Wiktionary](https://en.wiktionary.org/wiki/頭腦) | 84522653 |
| 2385 | U+6CF0_U+570B_U+4EBA_00 | 泰國人 | 泰國人 | [Wiktionary](https://en.wiktionary.org/wiki/泰國人) | 89809503 |
| 2386 | U+614B_U+5EA6_00 | 態度 | 態度 | [Wiktionary](https://en.wiktionary.org/wiki/態度) | 92294700 |
| 2387 | U+807D_00 | 聽 | 聽 | [Wiktionary](https://en.wiktionary.org/wiki/聽) | 93295880 |
| 2388 | U+75BC_00 | 疼 | 疼 | [Wiktionary](https://en.wiktionary.org/wiki/疼) | 89918966 |
| 2395 | U+75BC_U+75DB_00 | 疼痛 | 疼痛 | [Wiktionary](https://en.wiktionary.org/wiki/疼痛) | 89713126 |
| 2396 | U+62C6_00 | 拆 | 拆 | [Wiktionary](https://en.wiktionary.org/wiki/拆) | 92200544 |
| 2404 | U+901A_01 | 通 | 通 | [Wiktionary](https://en.wiktionary.org/wiki/通) | 92693582 |
| 2407 | U+9AD4_U+9A57_00 | 體驗 | 體驗 | [Wiktionary](https://en.wiktionary.org/wiki/體驗) | 89339777 |
| 2412 | U+66A2_00 | 暢 | 暢 | [Wiktionary](https://en.wiktionary.org/wiki/暢) | 91356109 |
| 2414 | U+5929_U+4E0A_00 | 天上 | 天上 | [Wiktionary](https://en.wiktionary.org/wiki/天上) | 90125226 |
| 2419 | U+8A0E_U+50B5_00 | 討債 | 討債 | [Wiktionary](https://en.wiktionary.org/wiki/討債) | 90747496 |
| 2420 | U+6843_U+5712_00 | 桃園 | 桃園 | [Wiktionary](https://en.wiktionary.org/wiki/桃園) | 91557570 |
| 2423 | U+50B3_00 | 傳 | 傳 | [Wiktionary](https://en.wiktionary.org/wiki/傳) | 91766312 |
| 2424 | U+6524_00 | 攤 | 攤 | [Wiktionary](https://en.wiktionary.org/wiki/攤) | 87582978 |
| 2427 | U+6311_00 | 挑 | 挑 | [Wiktionary](https://en.wiktionary.org/wiki/挑) | 92716677 |
| 2430 | U+62BD_00 | 抽 | 抽 | [Wiktionary](https://en.wiktionary.org/wiki/抽) | 92983102 |
| 2431 | U+6E6F_00 | 湯 | 湯 | [Wiktionary](https://en.wiktionary.org/wiki/湯) | 92917032 |
| 2434 | U+6E6F_U+5319_00 | 湯匙 | 湯匙 | [Wiktionary](https://en.wiktionary.org/wiki/湯匙) | 91705348 |
| 2437 | U+5929_U+5149_00 | 天光 | 天光 | [Wiktionary](https://en.wiktionary.org/wiki/天光) | 91984471 |
| 2439 | U+5929_U+908A_00 | 天邊 | 天邊 | [Wiktionary](https://en.wiktionary.org/wiki/天邊) | 78617587 |
| 2440 | U+5929_U+8272_00 | 天色 | 天色 | [Wiktionary](https://en.wiktionary.org/wiki/天色) | 92468743 |
| 2447 | U+9435_U+93C8_00 | 鐵鏈 | 鐵鏈 | [Wiktionary](https://en.wiktionary.org/wiki/鐵鏈) | 85041913 |
| 2449 | U+66DD_00 | 曝 | 曝 | [Wiktionary](https://en.wiktionary.org/wiki/曝) | 92468990 |
| 2451 | U+5945_00 | 奅 | 奅 | [Wiktionary](https://en.wiktionary.org/wiki/奅) | 87572785 |
| 2453 | U+6367_00 | 捧 | 捧 | [Wiktionary](https://en.wiktionary.org/wiki/捧) | 87581367 |
| 2455 | U+62CD_00 | 拍 | 拍 | [Wiktionary](https://en.wiktionary.org/wiki/拍) | 92454689 |
| 2473 | U+98C4_U+98C4_00 | 飄飄 | 飄飄 | [Wiktionary](https://en.wiktionary.org/wiki/飄飄) | 91828692 |
| 2475 | U+666E_00 | 普 | 普 | [Wiktionary](https://en.wiktionary.org/wiki/普) | 91102839 |
| 2476 | U+8B5C_00 | 譜 | 譜 | [Wiktionary](https://en.wiktionary.org/wiki/譜) | 92162854 |
| 2480 | U+535A_U+58EB_00 | 博士 | 博士 | [Wiktionary](https://en.wiktionary.org/wiki/博士) | 92160459 |
| 2485 | U+9A19_U+5B50_00 | 騙子 | 騙子 | [Wiktionary](https://en.wiktionary.org/wiki/騙子) | 85013041 |
| 2487 | U+6487_00 | 撇 | 撇 | [Wiktionary](https://en.wiktionary.org/wiki/撇) | 89367085 |
| 2500 | U+6D6E_U+6C89_00 | 浮沉 | 浮沉 | [Wiktionary](https://en.wiktionary.org/wiki/浮沉) | 74086960 |
| 2501 | U+6F58_00 | 潘 | 潘 | [Wiktionary](https://en.wiktionary.org/wiki/潘) | 90526292 |
| 2502 | U+6279_00 | 批 | 批 | [Wiktionary](https://en.wiktionary.org/wiki/批) | 90939793 |
| 2503 | U+914D_00 | 配 | 配 | [Wiktionary](https://en.wiktionary.org/wiki/配) | 92201983 |
| 2506 | U+76AE_U+819A_00 | 皮膚 | 皮膚 | [Wiktionary](https://en.wiktionary.org/wiki/皮膚) | 92162189 |
| 2508 | U+813E_U+6C23_00 | 脾氣 | 脾氣 | [Wiktionary](https://en.wiktionary.org/wiki/脾氣) | 90913788 |
| 2510 | U+7247_00 | 片 | 片 | [Wiktionary](https://en.wiktionary.org/wiki/片) | 93182973 |
| 2516 | U+5B78_U+58EB_00 | 學士 | 學士 | [Wiktionary](https://en.wiktionary.org/wiki/學士) | 90294444 |
| 2517 | U+6F22_00 | 漢 | 漢 | [Wiktionary](https://en.wiktionary.org/wiki/漢) | 92924834 |
| 2520 | U+97D3_U+570B_U+4EBA_00 | 韓國人 | 韓國人 | [Wiktionary](https://en.wiktionary.org/wiki/韓國人) | 87159820 |
| 2523 | U+86B6_00 | 蚶 | 蚶 | [Wiktionary](https://en.wiktionary.org/wiki/蚶) | 87589827 |
| 2528 | U+822A_00 | 航 | 航 | [Wiktionary](https://en.wiktionary.org/wiki/航) | 91490109 |
| 2529 | U+9805_00 | 項 | 項 | [Wiktionary](https://en.wiktionary.org/wiki/項) | 92163191 |
| 2531 | U+964D_U+4F0F_00 | 降伏 | 降伏 | [Wiktionary](https://en.wiktionary.org/wiki/降伏) | 92139078 |
| 2532 | U+543C_00 | 吼 | 吼 | [Wiktionary](https://en.wiktionary.org/wiki/吼) | 91979196 |
| 2539 | U+6D77_U+4E0A_00 | 海上 | 海上 | [Wiktionary](https://en.wiktionary.org/wiki/海上) | 89579499 |
| 2546 | U+5144_U+5F1F_00 | 兄弟 | 兄弟 | [Wiktionary](https://en.wiktionary.org/wiki/兄弟) | 92291115 |
| 2550 | U+5ACC_00 | 嫌 | 嫌 | [Wiktionary](https://en.wiktionary.org/wiki/嫌) | 92960179 |
| 2556 | U+66C9_00 | 曉 | 曉 | [Wiktionary](https://en.wiktionary.org/wiki/曉) | 92200686 |
| 2566 | U+798F_00 | 福 | 福 | [Wiktionary](https://en.wiktionary.org/wiki/福) | 92201230 |
| 2567 | U+798F_U+5EFA_00 | 福建 | 福建 | [Wiktionary](https://en.wiktionary.org/wiki/福建) | 92722065 |
| 2568 | U+798F_U+5EFA_U+4EBA_00 | 福建人 | 福建人 | [Wiktionary](https://en.wiktionary.org/wiki/福建人) | 91957859 |
| 2571 | U+8907_U+88FD_00 | 複製 | 複製 | [Wiktionary](https://en.wiktionary.org/wiki/複製) | 92262103 |
| 2574 | U+98A8_U+666F_00 | 風景 | 風景 | [Wiktionary](https://en.wiktionary.org/wiki/風景) | 92163274 |
| 2579 | U+98A8_U+971C_00 | 風霜 | 風霜 | [Wiktionary](https://en.wiktionary.org/wiki/風霜) | 83208415 |
| 2582 | U+98A8_U+5439_00 | 風吹 | 風吹 | [Wiktionary](https://en.wiktionary.org/wiki/風吹) | 92936599 |
| 2588 | U+4E0B_U+843D_U+4E0D_U+660E_00 | 下落不明 | 下落不明 | [Wiktionary](https://en.wiktionary.org/wiki/下落不明) | 60794483 |
| 2590 | U+5411_00 | 向 | 向 | [Wiktionary](https://en.wiktionary.org/wiki/向) | 92644169 |
| 2597 | U+73FE_U+5BE6_00 | 現實 | 現實 | [Wiktionary](https://en.wiktionary.org/wiki/現實) | 88576888 |
| 2598 | U+8208_00 | 興 | 興 | [Wiktionary](https://en.wiktionary.org/wiki/興) | 92201473 |
| 2599 | U+8861_00 | 衡 | 衡 | [Wiktionary](https://en.wiktionary.org/wiki/衡) | 92507628 |
| 2600 | U+5E78_00 | 幸 | 幸 | [Wiktionary](https://en.wiktionary.org/wiki/幸) | 92161080 |
| 2602 | U+5F62_U+5F71_00 | 形影 | 形影 | [Wiktionary](https://en.wiktionary.org/wiki/形影) | 90065959 |
| 2604 | U+884C_U+8E64_00 | 行蹤 | 行蹤 | [Wiktionary](https://en.wiktionary.org/wiki/行蹤) | 78673177 |
| 2605 | U+8208_U+8DA3_00 | 興趣 | 興趣 | [Wiktionary](https://en.wiktionary.org/wiki/興趣) | 92281912 |
| 2607 | U+5E78_U+798F_00 | 幸福 | 幸福 | [Wiktionary](https://en.wiktionary.org/wiki/幸福) | 92161075 |
| 2612 | U+865F_00 | 號 | 號 | [Wiktionary](https://en.wiktionary.org/wiki/號) | 92201606 |
| 2618 | U+597D_U+5922_00 | 好夢 | 好夢 | [Wiktionary](https://en.wiktionary.org/wiki/好夢) | 78618287 |
| 2620 | U+4F55_U+6642_00 | 何時 | 何時 | [Wiktionary](https://en.wiktionary.org/wiki/何時) | 92289301 |
| 2625 | U+4F55_U+8655_00 | 何處 | 何處 | [Wiktionary](https://en.wiktionary.org/wiki/何處) | 84203332 |
| 2626 | U+597D_U+770B_00 | 好看 | 好看 | [Wiktionary](https://en.wiktionary.org/wiki/好看) | 92943179 |
| 2629 | U+597D_U+597D_00 | 好好 | 好好 | [Wiktionary](https://en.wiktionary.org/wiki/好好) | 82790530 |
| 2630 | U+83EF_00 | 華 | 華 | [Wiktionary](https://en.wiktionary.org/wiki/華) | 92720692 |
| 2631 | U+83EF_U+8A9E_00 | 華語 | 華語 | [Wiktionary](https://en.wiktionary.org/wiki/華語) | 92968282 |
| 2633 | U+53CD_00 | 反 | 反 | [Wiktionary](https://en.wiktionary.org/wiki/反) | 92067086 |
| 2636 | U+74B0_00 | 環 | 環 | [Wiktionary](https://en.wiktionary.org/wiki/環) | 92490116 |
| 2637 | U+7E41_00 | 繁 | 繁 | [Wiktionary](https://en.wiktionary.org/wiki/繁) | 92707353 |
| 2640 | U+7169_U+60F1_00 | 煩惱 | 煩惱 | [Wiktionary](https://en.wiktionary.org/wiki/煩惱) | 89830031 |
| 2643 | U+51E1_U+4E8B_00 | 凡事 | 凡事 | [Wiktionary](https://en.wiktionary.org/wiki/凡事) | 63190801 |
| 2644 | U+5E7B_U+5316_00 | 幻化 | 幻化 | [Wiktionary](https://en.wiktionary.org/wiki/幻化) | 79026955 |
| 2645 | U+7E41_U+83EF_00 | 繁華 | 繁華 | [Wiktionary](https://en.wiktionary.org/wiki/繁華) | 92251970 |
| 2649 | U+6CD5_U+5EA6_00 | 法度 | 法度 | [Wiktionary](https://en.wiktionary.org/wiki/法度) | 92269386 |
| 2650 | U+767C_U+5C55_00 | 發展 | 發展 | [Wiktionary](https://en.wiktionary.org/wiki/發展) | 90038244 |
| 2654 | U+6B61_00 | 歡 | 歡 | [Wiktionary](https://en.wiktionary.org/wiki/歡) | 90752772 |
| 2656 | U+634D_00 | 捍 | 捍 | [Wiktionary](https://en.wiktionary.org/wiki/捍) | 88869897 |
| 2660 | U+61F7_U+7591_00 | 懷疑 | 懷疑 | [Wiktionary](https://en.wiktionary.org/wiki/懷疑) | 92737835 |
| 2662 | U+5F8C_U+679C_00 | 後果 | 後果 | [Wiktionary](https://en.wiktionary.org/wiki/後果) | 90816450 |
| 2666 | U+4ED8_00 | 付 | 付 | [Wiktionary](https://en.wiktionary.org/wiki/付) | 92199877 |
| 2669 | U+5206_01 | 分 | 分 | [Wiktionary](https://en.wiktionary.org/wiki/分) | 92695569 |
| 2671 | U+7C89_00 | 粉 | 粉 | [Wiktionary](https://en.wiktionary.org/wiki/粉) | 92691439 |
| 2672 | U+596E_00 | 奮 | 奮 | [Wiktionary](https://en.wiktionary.org/wiki/奮) | 92200270 |
| 2673 | U+75D5_00 | 痕 | 痕 | [Wiktionary](https://en.wiktionary.org/wiki/痕) | 92915475 |
| 2676 | U+5206_02 | 分 | 分 | [Wiktionary](https://en.wiktionary.org/wiki/分) | 92695569 |
| 2678 | U+660F_00 | 昏 | 昏 | [Wiktionary](https://en.wiktionary.org/wiki/昏) | 92957810 |
| 2682 | U+75D5_U+8DE1_00 | 痕跡 | 痕跡 | [Wiktionary](https://en.wiktionary.org/wiki/痕跡) | 92162154 |
| 2683 | U+5206_U+96E2_00 | 分離 | 分離 | [Wiktionary](https://en.wiktionary.org/wiki/分離) | 92138145 |
| 2684 | U+96F2_U+6797_00 | 雲林 | 雲林 | [Wiktionary](https://en.wiktionary.org/wiki/雲林) | 87981182 |
| 2686 | U+96F2_U+7159_00 | 雲煙 | 雲煙 | [Wiktionary](https://en.wiktionary.org/wiki/雲煙) | 85993668 |
| 2689 | U+96F2_U+6D77_00 | 雲海 | 雲海 | [Wiktionary](https://en.wiktionary.org/wiki/雲海) | 86462833 |
| 2690 | U+7D1B_U+98DB_00 | 紛飛 | 紛飛 | [Wiktionary](https://en.wiktionary.org/wiki/紛飛) | 89315055 |
| 2691 | U+5FFD_00 | 忽 | 忽 | [Wiktionary](https://en.wiktionary.org/wiki/忽) | 92200455 |
| 2695 | U+6B72_00 | 歲 | 歲 | [Wiktionary](https://en.wiktionary.org/wiki/歲) | 93157124 |
| 2699 | U+82B1_U+854A_00 | 花蕊 | 花蕊 | [Wiktionary](https://en.wiktionary.org/wiki/花蕊) | 87989204 |
| 2700 | U+706B_U+71D2_00 | 火燒 | 火燒 | [Wiktionary](https://en.wiktionary.org/wiki/火燒) | 92091122 |
| 2705 | U+56DE_U+982D_00 | 回頭 | 回頭 | [Wiktionary](https://en.wiktionary.org/wiki/回頭) | 90824802 |
| 2707 | U+82B1_U+5712_00 | 花園 | 花園 | [Wiktionary](https://en.wiktionary.org/wiki/花園) | 92437210 |
| 2710 | U+98DB_U+6A5F_01 | 飛機 | 飛機 | [Wiktionary](https://en.wiktionary.org/wiki/飛機) | 89965738 |
| 2711 | U+60E0_U+5B89_00 | 惠安 | 惠安 | [Wiktionary](https://en.wiktionary.org/wiki/惠安) | 91981615 |
| 2714 | U+9060_U+9060_00 | 遠遠 | 遠遠 | [Wiktionary](https://en.wiktionary.org/wiki/遠遠) | 60787213 |
| 2716 | U+559C_00 | 喜 | 喜 | [Wiktionary](https://en.wiktionary.org/wiki/喜) | 91334485 |
| 2718 | U+6232_U+5F04_00 | 戲弄 | 戲弄 | [Wiktionary](https://en.wiktionary.org/wiki/戲弄) | 73600636 |
| 2719 | U+5E0C_U+671B_00 | 希望 | 希望 | [Wiktionary](https://en.wiktionary.org/wiki/希望) | 92136174 |
| 2721 | U+72A7_U+7272_00 | 犧牲 | 犧牲 | [Wiktionary](https://en.wiktionary.org/wiki/犧牲) | 89373668 |
| 2736 | U+50B3_U+8AAA_01 | 傳說 | 傳說 | [Wiktionary](https://en.wiktionary.org/wiki/傳說) | 84547750 |

## Automatically resolved - MEDIUM confidence (optional spot-check)

935 entries.

| line | entry_id | hanri | reading | english | mandarin_trad | reason | source | revision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | U+AC00_U+C57C_00 | 가ˉ야ˆ | 가5야1 | kaya | 咖椰醬 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 4 | U+AC00_U+C57C_U+B610_U+B514_00 | 가ˉ야ˉ또디ˆ | 가5야5또디1 | kaya bread; kaya roti | 咖椰麵包 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 6 | U+AC10_00 | 감ˋ | 감2 | (question marker) | 是否 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 20 | U+2019_U+1105_U+11A4_00 | ’ᄅᆤˋ | ’ᄅᆤ2 | perfective aspect marker | 了 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 25 | U+B9E4_00 | 매 | 매 | shouldn't; don't want | 不要; 不應該 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 26 | U+B9E4_U+B85C_00 | 매ˉ로ˆ | 매5로1 | Milo | 美祿 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 27 | U+BA54_U+B07C_00 | 메ˉ끼ˆ | 메5끼1 | Maggi (noodles) | 美極麵 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 35 | U+C26C_00 | 쉬ˋ | 쉬2 | nice | 好; 漂亮 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 40 | U+C560_00 | 애 | 애 | should; want | 應該; 想要 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 49 | U+C7E3_00 | 쟣 | 쟣 | then | 才 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 50 | U+C7E3_U+B2C8_00 | 쟣ˆ니ˉ | 쟣1니5 | this; so | 這麼 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 53 | U+CC7B_U+CC7B_00 | 챻ˆ챻 | 챻1챻 | cha-cha | 恰恰舞 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 98 | U+4EDD_00 | 仝 | 강5 | same; together | 仝 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/仝) | 92199879 |
| 99 | U+6E2F_U+5898_00 | 港墘 | 강1길4 | harbor; Hong Kong; edge; side | 港邊 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 100 | U+6C5F_U+5C71_U+6613_U+6539_00 | 江山易改 | 강5산5이개2 | mountain; change | 江山易改 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 102 | U+4EDD_U+6B3E_00 | 仝款 | 강콴2 | same; alike | 一樣 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/仝款) | 78850105 |
| 104 | U+5FA6_00 | 徦 | 갛 | to the extent | 得 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://language.moe.gov.tw/files/people_files/700iongji_1031222_1.pdf) |  |
| 106 | U+4F6E_U+610F_00 | 佮意 | 갛1이 | like; be fond of | 喜歡 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/佮意) | 78463355 |
| 107 | U+80DB_U+810A_00 | 胛脊 | 갛1쟣 | shoulder blade; spine | 肩胛骨; 脊背 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/胛脊) | 68503985 |
| 118 | U+4E5D_U+767E_00 | 九百 | ᄀᅷ1밯 | nine hundred | 九百 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/九百) | 88050756 |
| 124 | U+539A_U+8A71_00 | 厚話 | ᄀᅷ웨5 | speech; language | 多話 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/厚話) | 76855052 |
| 126 | U+72E1_U+5236_00 | 狡制 | ᄀᅷ1제 | fussy; contrary; awkward | 刁鑽; 古怪; 彆扭 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://itaigi.tw/k/古怪/) |  |
| 141 | U+884C_U+8E0F_00 | 行踏 | 걀닿1 | walk around; tread | 走動; 踩踏 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/行踏) | 80940007 |
| 144 | U+9A5A_U+4EBA_U+5077_00 | 驚人偷 | 걀5랑ᄐᅷ1 | afraid of thieves | 怕被偷 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 145 | U+56DD_U+5B6B_00 | 囝孫 | 걀1순1 | child | 子孫 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/囝孫) | 85495254 |
| 151 | U+9E79_U+9178_U+82E6_U+6F80_00 | 鹹酸苦澀 | 걈승5커1샵 | salty, sour, bitter and astringent; hardships | 鹹酸苦澀 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 153 | U+52AB_00 | 劫 | 걉 | robbery; calamity | 劫 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/劫) | 92720826 |
| 164 | U+53E4_U+65E9_00 | 古早 | 거1자2 | long ago; olden days | 很久以前; 古時候 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/古早) | 92022622 |
| 165 | U+53E4_U+9310_00 | 古錐 | 거1쥐1 | cute; adorable | 可愛 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/古錐) | 84973732 |
| 171 | U+570B_U+7ACB_00 | 國立 | 걱1립1 | a national institution | 國立 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/國立) | 87988286 |
| 172 | U+570B_U+59D3_U+723A_00 | 國姓爺 | 걱1솅2야4 | country | 國姓爺 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/國姓爺) | 89619424 |
| 187 | U+8B1B_U+6CD5_00 | 講法 | 겅1홛 | speak; say | 講法 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/講法) | 84041637 |
| 188 | U+5EE3_U+5E9C_00 | 廣府 | 겅1후2 | Canton (Guangzhou) | 廣府 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/廣府) | 78759450 |
| 189 | U+5EE3_U+5E9C_U+4EBA_00 | 廣府人 | 겅1후1랑4 | Cantonese people | 廣府人 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/廣府人) | 78625715 |
| 190 | U+5EE3_U+5E9C_U+8A71_00 | 廣府話 | 겅1후1웨5 | Cantonese speech | 廣府話 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/廣府話) | 78625716 |
| 198 | U+5BB6_U+5A46_00 | 家婆 | 게5보4 | to be busybody | 多管閒事 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/家婆) | 79035879 |
| 201 | U+5BB6_U+8CC4_00 | 家賄 | 게5훼2 | family property | 家產 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/家賄) | 83685969 |
| 207 | U+62F1_U+8D77_U+624B_00 | 拱起手 | 경1키1츄2 | rise; start; hand | 拱起手 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 209 | U+6FC0_U+6150_U+6150_00 | 激慐慐 | 곅1껑껑5 | stunned; flustered | 驚慌; 發愣 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 213 | U+5805_U+5B9A_00 | 堅定 | 곈5뎽5 | fixed; certain; decide | 堅定 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/堅定) | 74009404 |
| 217 | U+6770_00 | 杰 | 곋1 | outstanding | 杰 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/杰) | 81763759 |
| 218 | U+7D50_U+5C40_00 | 結局 | 곋1격1 | outcome; ending | 結局 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/結局) | 86468627 |
| 219 | U+7D50_U+679C_00 | 結果 | 곋1고2 | tie; knot | 結果 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/結果) | 86462943 |
| 221 | U+7D93_00 | 經 | 곙1 | scripture; classic; pass through | 經 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/經) | 92201356 |
| 227 | U+7D93_U+6B77_00 | 經歷 | 곙5롁1 | scripture; classic; pass through | 經歷 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/經歷) | 85144951 |
| 228 | U+666F_U+8272_00 | 景色 | 곙1셱 | color | 景色 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/景色) | 92235036 |
| 229 | U+7D93_U+6FDF_00 | 經濟 | 곙5제 | economy; finance; economics | 經濟 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/經濟) | 91570815 |
| 234 | U+679C_U+7136_00 | 果然 | 고1뗸4 | so; thus | 果然 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/果然) | 84407152 |
| 236 | U+544A_U+8FAD_00 | 告辭 | 고2시4 | bid farewell | 告辭 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/告辭) | 76227483 |
| 241 | U+6B4C_U+58C7_00 | 歌壇 | 과5돨4 | song | 歌壇 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/歌壇) | 78641826 |
| 243 | U+639B_U+610F_00 | 掛意 | 과2이 | worry; be concerned | 掛意 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/掛意) | 74191420 |
| 248 | U+89C0_U+4E16_U+97F3_00 | 觀世音 | 관5세2임1 | world; generation; sound | 觀世音 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/觀世音) | 90339159 |
| 249 | U+95DC_U+4FC2_00 | 關係 | 관5헤5 | close | 關係 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/關係) | 91967805 |
| 255 | U+83C5_U+8292_00 | 菅芒 | 괄5빵4 | silvergrass; miscanthus grass | 芒草 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://sutian.moe.edu.tw/zh-hant/su/8911/) |  |
| 256 | U+5BD2_U+5929_00 | 寒天 | 괄틸1 | cold day | 寒天 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/寒天) | 92243969 |
| 259 | U+4E56_U+56DD_00 | 乖囝 | 괘5걀2 | child | 乖孩子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 272 | U+820A_U+5E74_00 | 舊年 | 구니4 | year | 去年 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/舊年) | 86629000 |
| 274 | U+820A_U+65E9_00 | 舊早 | 구자2 | early; morning | 從前 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/舊早) | 86592469 |
| 277 | U+541B_U+5B50_00 | 君子 | 군5주2 | lord; ruler; child; son | 君子 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/君子) | 91478907 |
| 280 | U+5014_U+5F37_00 | 倔強 | 굳경5 | strong | 倔強 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/倔強) | 91767445 |
| 281 | U+7CBF_00 | 粿 | 궤2 | kueh | 粿 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/粿) | 91697401 |
| 283 | U+904E_U+766E_00 | 過癮 | 궤2꼔 | pass; exceed | 過癮 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/過癮) | 91678363 |
| 286 | U+679C_U+5B50_00 | 果子 | 궤1즤2 | child; son | 水果 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/果子) | 92047735 |
| 294 | U+898F_U+5DE5_00 | 規工 | 귀5강1 | work | 整天 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/規工) | 90036694 |
| 319 | U+8A18_U+6301_00 | 記持 | 기2디4 | record; remember | 記憶 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/記持) | 72615482 |
| 325 | U+5176_U+4ED6_00 | 其他 | 기탈1 | that; its | 其他 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/其他) | 89844204 |
| 326 | U+671F_U+5F85_00 | 期待 | 기태5 | anticipate | 期待 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/期待) | 92304594 |
| 332 | U+4ECA_U+669D_00 | 今暝 | 긴5미4 | night | 今晚 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/今暝) | 92924639 |
| 334 | U+4ECA_U+591C_00 | 今夜 | 긴5야5 | night | 今夜 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/今夜) | 92160101 |
| 337 | U+9E7C_U+7CBD_00 | 鹼粽 | 길5장 | alkaline rice dumpling | 鹼粽 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/鹼粽) | 90824887 |
| 339 | U+5997_00 | 妗 | 김5 | aunt | 舅母 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/妗) | 90362602 |
| 340 | U+91D1_U+91D1_00 | 金金 | 김5김1 | wide-eyed; with eyes wide open | 睜大眼睛 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://sutian.moe.edu.tw/und-hani/su/4565/) |  |
| 343 | U+4ECA_U+751F_U+4ECA_U+4E16_00 | 今生今世 | 김5솅5김5세 | this whole life | 今生今世 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/今生今世) | 84204425 |
| 346 | U+773C_U+795E_00 | 眼神 | 깐1신4 | look in one's eyes | 眼神 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/眼神) | 78655625 |
| 347 | U+773C_U+524D_00 | 眼前 | 깐1졩4 | before one's eyes; in front | 眼前 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/眼前) | 78655539 |
| 348 | U+592F_U+67B7_00 | 夯枷 | 꺄게4 | carry; lift; cangue; shackle | 戴枷 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/夯枷) | 85081954 |
| 349 | U+6511_00 | 攑 | 꺟1 | lift; grab | 舉; 拿 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/攑) | 92359440 |
| 350 | U+6511_U+982D_00 | 攑頭 | 꺟ᄐᅷ4 | lift up one’s head | 抬頭 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/攑頭) | 85495128 |
| 352 | U+4E94_U+9EDE_U+534A_00 | 五點半 | 꺼댬1봘 | five thirty | 五點半 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 355 | U+6150_00 | 慐 | 껑5 | foolish; stunned | 呆; 迷糊 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/慐) | 87579539 |
| 356 | U+6150_U+56DD_00 | 慐囝 | 껑걀2 | child | 傻孩子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 357 | U+6150_U+6150_00 | 慐慐 | 껑껑5 | foolish; dazed | 迷糊 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 358 | U+6150_U+4EBA_00 | 慐人 | 껑랑4 | foolish person | 傻子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 359 | U+6150_U+795E_00 | 慐神 | 껑신4 | absent-minded; dazed | 恍惚; 發呆 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 362 | U+85DD_U+8853_00 | 藝術 | 께숟1 | arts | 藝術 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/藝術) | 91488161 |
| 366 | U+766E_U+982D_00 | 癮頭 | 꼔2ᄐᅷ4 | silly head; fool | 傻子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/癮頭) | 92386543 |
| 367 | U+5B7D_U+93E1_U+53F0_00 | 孽鏡台 | 꼗걀2대4 | evil; sin; mirror; platform; Taiwan | 孽鏡台 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 368 | U+5B7D_U+7DE3_00 | 孽緣 | 꼗옌4 | evil; sin; fate; connection | 孽緣 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/孽緣) | 88137090 |
| 369 | U+51DD_U+5FC3_00 | 凝心 | 꼥심1 | emotionally suppressed | 情緒壓抑 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 374 | U+5916_U+53E3_00 | 外口 | 꽈ᄏᅷ2 | outside; exterior | 外面 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/外口) | 83197441 |
| 379 | U+6708_U+53F0_00 | 月台 | 꽏대4 | train platform | 月台 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/月台) | 46387006 |
| 385 | U+725B_U+4E3C_00 | 牛丼 | 꾸덤4 | gyudon | 牛丼 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/牛丼) | 92291088 |
| 391 | U+6708_U+5A18_00 | 月娘 | 뀋뉴4 | moon | 月亮 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/月娘) | 89172265 |
| 393 | U+6708_U+5713_00 | 月圓 | 뀋일4 | full moon | 月圓 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/月圓) | 84475524 |
| 399 | U+7FA9_U+9806_00 | 義順 | 끼순5 | Yishun | 義順 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 401 | U+903D_00 | 逽 | 나2 | as; like; as if; while | 像; 如同; 一邊 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/逽) | 89107849 |
| 405 | U+56A8_U+5589_00 | 嚨喉 | 나ᄋᅷ4 | throat | 喉嚨 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/嚨喉) | 83911082 |
| 406 | U+82E5_U+6E96_00 | 若準 | 나준2 | if; suppose | 如果; 假如 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/若準) | 78463612 |
| 408 | U+8354_U+93E1_U+8A18_00 | 荔鏡記 | 내곙2기 | record; remember | 荔鏡記 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 412 | U+9CE5_U+9F20_00 | 鳥鼠 | ᄂᆤ1츼2 | rat; mouse | 老鼠 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/鳥鼠) | 91454526 |
| 421 | U+5169_U+500B_U+6708_00 | 兩個月 | 능고2뀋1 | two months | 兩個月 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 422 | U+5375_U+4EC1_00 | 卵仁 | 능띤4 | egg | 蛋黃 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/卵仁) | 78608890 |
| 423 | U+5169_U+65E5_00 | 兩日 | 능띧1 | two days | 兩日 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 424 | U+5169_U+4EBA_00 | 兩人 | 능랑4 | two people | 兩人 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 425 | U+5169_U+767E_U+7B8D_00 | 兩百箍 | 능밯1커1 | two hundred dollars | 兩百元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 426 | U+5169_U+842C_U+7B8D_00 | 兩萬箍 | 능빤커1 | twenty thousand dollars | 兩萬元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 427 | U+5169_U+4E2A_00 | 兩个 | 능에4 | two; two items | 兩個 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 428 | U+8EDF_U+4B55_00 | 軟䭕 | 능1쟐2 | soft | 軟 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/軟䭕) | 92387880 |
| 429 | U+5169_U+5343_U+7B8D_00 | 兩千箍 | 능촁5커1 | two thousand dollars | 兩千元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 431 | U+62C8_00 | 拈 | 니1 | pick up with fingers | 拈 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/拈) | 87580729 |
| 434 | U+7126_U+CEE5_U+CEE5_00 | 焦컥ˆ컥 | 다5컥1컥 | burnt; scorched | 焦黑 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 436 | U+9010_U+5DE5_00 | 逐工 | 닥강1 | work | 每天 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/逐工) | 74124837 |
| 437 | U+9010_U+5BB6_00 | 逐家 | 닥게1 | everyone | 大家 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/逐家) | 89956370 |
| 438 | U+89F8_U+7E8F_00 | 觸纏 | 닥1딜4 | difficult to deal with; troublesome; pester | 難纏; 糾纏 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/觸纏) | 84378882 |
| 439 | U+9010_U+65E5_00 | 逐日 | 닥띧1 | every day | 每天 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/逐日) | 83601667 |
| 440 | U+89F8_U+820C_00 | 觸舌 | 닥1짛1 | click the tongue (in admiration) | 咂舌 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/觸舌) | 82793928 |
| 452 | U+4ECA_U+4ED4_00 | 今仔 | 달5아2 | just; just now | 剛剛 | Reading 달5아2 matches taⁿ-á (just now), not kin-á (today); removed the suffix-only gloss. | [Wiktionary](https://en.wiktionary.org/wiki/今仔) | 84392652 |
| 453 | U+6FB9_00 | 澹 | 담4 | wet; damp | 濕; 潮濕 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/澹) | 87590878 |
| 456 | U+6FB9_U+7CCA_U+7CCA_00 | 澹糊糊 | 담거거4 | mushy; sticky | 濕黏 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/澹糊糊) | 84384830 |
| 460 | U+81BD_U+5BD2_00 | 膽寒 | 담1한4 | fearful; chilled with fear | 膽寒 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/膽寒) | 46081674 |
| 472 | U+6771_U+5BE7_00 | 東寧 | 당5롕4 | east | 東寧 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/東寧) | 90308662 |
| 473 | U+6771_U+5BE7_U+97F3_00 | 東寧音 | 당5롕임1 | Tangliengim | 東寧音 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 474 | U+6771_U+897F_U+5357_U+5317_00 | 東西南北 | 당5새5람박 | all directions (lit. east-west-south-north) | 東西南北 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/東西南北) | 92272620 |
| 479 | U+540C_U+9F4A_00 | 同齊 | 당죄4 | together; neat | 一起 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/同齊) | 92080293 |
| 483 | U+9B25_00 | 鬥 | ᄃᅷ | join; put together | 鬥 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/鬥) | 87315324 |
| 487 | U+9B25_U+9663_00 | 鬥陣 | ᄃᅷ2딘5 | together; accompany | 一起 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/鬥陣) | 78462772 |
| 488 | U+8C46_U+7CBD_00 | 豆粽 | ᄃᅷ장 | bean rice dumpling | 豆粽 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 491 | U+8C46_U+82B1_U+6C34_00 | 豆花水 | ᄃᅷ훼5쥐2 | soybean drink | 豆漿 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/豆花水) | 92429572 |
| 492 | U+6C93_U+6C93_U+4ED4_00 | 沓沓仔 | ᄃᅷᇂᄃᅷᇂ아2 | slowly | 慢慢地 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/沓沓仔) | 88961329 |
| 496 | U+53F0_U+4E2D_00 | 台中 | 대뎡1 | Taichung | 台中 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/台中) | 89529354 |
| 500 | U+53F0_U+5317_U+8ECA_U+7AD9_00 | 台北車站 | 대박1챠5잠5 | Taipei Main Station | 台北車站 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 501 | U+53F0_U+5317_U+8ECA_U+982D_00 | 台北車頭 | 대박1챠5ᄐᅷ4 | Taipei station | 臺北車站 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 502 | U+53F0_U+5317_U+5E02_00 | 台北市 | 대박1치5 | Taipei City | 台北市 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 503 | U+53F0_U+5317_U+5E02_U+653F_U+5E9C_00 | 台北市政府 | 대박1치졩2후2 | Taipei City Government | 台北市政府 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 504 | U+4EE3_U+8868_00 | 代表 | 대ᄇᆤ2 | generation; replace; surface; express | 代表 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/代表) | 92491807 |
| 505 | U+53F0_U+7063_00 | 台灣 | 대완4 | Taiwan | 台灣 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/台灣) | 44825027 |
| 506 | U+53F0_U+7063_U+4EBA_00 | 台灣人 | 대완랑4 | Taiwanese person | 台灣人 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/台灣人) | 46540019 |
| 507 | U+53F0_U+7063_U+8A71_00 | 台灣話 | 대완웨5 | Taiwanese language | 台灣話 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/台灣話) | 46540021 |
| 508 | U+4EE3_U+8A8C_00 | 代誌 | 대지 | matter; affair | 事情 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/代誌) | 91749493 |
| 509 | U+5927_U+9435_U+570D_U+5C71_00 | 大鐵圍山 | 대팋1위솰1 | big; great; mountain | 大鐵圍山 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 512 | U+5B9A_U+5B9A_00 | 定定 | 댤댤5 | often; regularly | 常常 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/定定) | 82519157 |
| 513 | U+5B9A_U+8457_00 | 定著 | 댤둏1 | definitely; fixed | 一定 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/定著) | 91738672 |
| 515 | U+8E2E_00 | 踮 | 댬 | stand on tiptoe; stay | 踮腳; 停留 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/踮) | 91716498 |
| 516 | U+5E97_00 | 店 | 댬5 | coffee shop | 店 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/店) | 92200416 |
| 518 | U+606C_U+606C_00 | 恬恬 | 댬댬5 | quietly; silently | 靜靜地 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/恬恬) | 92432700 |
| 524 | U+689D_U+4EF6_00 | 條件 | ᄃᆤ걀5 | strip | 條件 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/條件) | 92520157 |
| 525 | U+7262_U+7262_00 | 牢牢 | ᄃᆤᄃᆤ4 | firmly; tightly | 牢牢 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/牢牢) | 80125506 |
| 534 | U+7368_U+591C_00 | 獨夜 | 덕야5 | lonely night | 獨夜 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 541 | U+64CB_U+606C_00 | 擋恬 | 덩2댬5 | stop; come to a halt | 停下 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 548 | U+7576_U+958B_00 | 當開 | 덩5캐1 | be in bloom | 正在開花 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 553 | U+7B2C_00 | 第 | 데5 | ordinal prefix | 第 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/第) | 89939125 |
| 559 | U+7B2C_U+4E00_U+7B49_00 | 第一等 | 데읻1뎽2 | first-class | 第一等 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 561 | U+5E95_U+8932_00 | 底褲 | 데1커 | underwear | 底褲 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/底褲) | 89014525 |
| 567 | U+4E2D_U+665D_00 | 中晝 | 뎡5ᄃᅷ | middle; in | 中午 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/中晝) | 78599311 |
| 582 | U+96FB_U+53F0_00 | 電台 | 뎬대4 | radio station | 電台 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/電台) | 46589488 |
| 583 | U+96FB_U+52D5_00 | 電動 | 뎬덩5 | electricity | 電動 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/電動) | 88293647 |
| 588 | U+96FB_U+98A8_00 | 電風 | 뎬헝1 | electric fan | 電風扇 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/電風) | 78686827 |
| 589 | U+96FB_U+706B_00 | 電火 | 뎬훼2 | electric light | 電燈 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/電火) | 91705969 |
| 594 | U+9802_U+61F8_00 | 頂懸 | 뎽1괠4 | very high; up high | 高 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/頂懸) | 78687848 |
| 596 | U+9802_U+79AE_U+62DC_00 | 頂禮拜 | 뎽1레1배 | last week | 上星期 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/頂禮拜) | 78467840 |
| 597 | U+9802_U+4E16_00 | 頂世 | 뎽1시 | top; world; generation | 上一代 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/頂世) | 78687828 |
| 598 | U+9802_U+4E16_U+4EBA_00 | 頂世人 | 뎽1시2랑4 | previous generation | 上一代 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/頂世人) | 78687829 |
| 599 | U+71C8_U+4E0B_00 | 燈下 | 뎽5에5 | under the lamp | 燈下 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 600 | U+9802_U+771F_00 | 頂真 | 뎽1진1 | serious; earnest | 認真 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/頂真) | 83289299 |
| 604 | U+5E95_01 | 底 | 도2 | where; which | 哪裡; 哪個 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/底) | 92544956 |
| 609 | U+5E95_U+843D_00 | 底落 | 도1롷1 | where | 哪裡 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/底落) | 78570012 |
| 612 | U+5E95_U+4F4D_00 | 底位 | 도1위5 | where | 哪裡 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 614 | U+5012_U+624B_00 | 倒手 | 도2츄2 | left hand | 左手 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/倒手) | 88048806 |
| 616 | U+8E5B_00 | 蹛 | 돠 | stay; live at | 住; 居住 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/蹛) | 87575199 |
| 619 | U+5927_U+689D_00 | 大條 | 돠ᄃᆤ4 | big; out of hand | 嚴重 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/大條) | 80182073 |
| 620 | U+5927_U+5927_00 | 大大 | 돠돠5 | big; great | 大大 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/大大) | 84952116 |
| 621 | U+5927_U+5806_00 | 大堆 | 돠뒤1 | big; great | 一大堆 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 625 | U+5927_U+7D30_U+8072_00 | 大細聲 | 돠쇠2샬1 | loud and soft; volume | 音量 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/大細聲) | 82407824 |
| 627 | U+5927_U+6B09_00 | 大欉 | 돠장4 | big; great | 大株 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 628 | U+5927_U+539D_00 | 大厝 | 돠추 | big; great; house | 大房子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/大厝) | 78616529 |
| 629 | U+5927_U+817F_00 | 大腿 | 돠튀2 | big; great | 大腿 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/大腿) | 92252200 |
| 630 | U+5927_U+6F22_00 | 大漢 | 돠한 | big; great | 長大; 大個子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/大漢) | 89398066 |
| 631 | U+5927_U+6D77_00 | 大海 | 돠해2 | wide sea | 大海 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/大海) | 86777679 |
| 638 | U+5E95_00 | 底 | 되2 | where; which | 哪裡; 哪個 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/底) | 92544956 |
| 641 | U+6F6E_U+6C55_U+8A71_00 | 潮汕話 | 됴솰2웨5 | Chaoshan language | 潮汕話 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/潮汕話) | 87966907 |
| 643 | U+6F6E_U+5DDE_U+8A71_00 | 潮州話 | 됴쥬5웨5 | Teochew language | 潮州話 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/潮州話) | 92511894 |
| 645 | U+8457_U+75E7_00 | 著痧 | 둏솨1 | get heatstroke | 中暑 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/著痧) | 79121635 |
| 646 | U+62C4_00 | 拄 | 두2 | just; prop up | 剛好; 支撐 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/拄) | 88239511 |
| 648 | U+7DB4_00 | 綴 | 뒈 | follow; attach | 跟隨; 連接 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/綴) | 92746813 |
| 649 | U+7DB4_U+4EBA_U+8D70_00 | 綴人走 | 뒈2랑ᄌᅷ2 | follow someone away | 跟人走 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/綴人走) | 78571633 |
| 653 | U+5C0D_U+9762_00 | 對面 | 뒤2삔5 | opposite side | 對面 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/對面) | 85423974 |
| 665 | U+5510_U+4EBA_U+8A71_00 | 唐人話 | 등랑웨5 | Chinese speech | 漢語 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/唐人話) | 81611949 |
| 666 | U+8F49_U+2019_U+B798_00 | 轉’래 | 등2’래 | turn; transfer; return | 回來 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 667 | U+8F49_U+8E05_00 | 轉踅 | 등1셓1 | turn around | 轉身 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/轉踅) | 88398262 |
| 670 | U+7576_U+958B_01 | 當開 | 등5캐1 | be in bloom | 正在開花 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 671 | U+8F49_U+2019_U+D088_00 | 轉’킈 | 등2’킈 | turn; transfer; return | 回去 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 676 | U+8C6C_U+8DE4_00 | 豬跤 | 듸5카1 | pig | 豬腳 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/豬跤) | 87315593 |
| 679 | U+5E95_U+4EBA_00 | 底人 | 디랑4 | who | 誰 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/底人) | 91827500 |
| 680 | U+5E95_U+6642_00 | 底時 | 디시4 | when | 什麼時候 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/底時) | 88989156 |
| 681 | U+632F_U+52D5_00 | 振動 | 딘1당5 | shake; revive; move; action | 振動 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/振動) | 92138909 |
| 685 | U+751C_U+7CBF_00 | 甜粿 | 딜5궤2 | sweet rice cake | 甜粿 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/甜粿) | 91751408 |
| 691 | U+71B1_U+6200_00 | 熱戀 | 뗻롼4 | hot | 熱戀 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/熱戀) | 73624323 |
| 704 | U+4E8C_U+5341_U+7B8D_00 | 二十箍 | 띠잡커1 | twenty dollars | 二十元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 706 | U+4EBA_U+683C_00 | 人格 | 띤겧 | person; people | 人格 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/人格) | 92203746 |
| 715 | U+8A8D_U+771F_00 | 認真 | 띤진1 | true; really | 認真 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/認真) | 84971528 |
| 722 | U+65E5_U+2019_U+C2DC_00 | 日’시 | 띧1’시 | day; sun | 白天 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 728 | U+5165_U+5175_00 | 入兵 | 띱볭1 | enlist; enter military service | 入伍 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/入兵) | 82737516 |
| 732 | U+516D_U+767E_00 | 六百 | 락밯 | six hundred | 六百 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/六百) | 88050734 |
| 734 | U+843D_U+6F06_00 | 落漆 | 락1찯 | paint peeling off; make a fool of oneself | 掉漆; 出糗 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/落漆) | 78571913 |
| 735 | U+843D_U+82B1_00 | 落花 | 락1훼1 | falling flowers | 落花 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/落花) | 78670040 |
| 753 | U+4EBA_U+5BA2_00 | 人客 | 랑켛 | guest; customer | 客人 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/人客) | 91701122 |
| 760 | U+8001_U+7334_00 | 老猴 | ᄅᅷᄀᅷ4 | old monkey | 老猴 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/老猴) | 92079925 |
| 761 | U+6A13_U+9802_00 | 樓頂 | ᄅᅷ뎽2 | upstairs | 樓頂 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/樓頂) | 91749496 |
| 762 | U+9B27_U+71B1_00 | 鬧熱 | ᄅᅷ뗻1 | hot | 熱鬧 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/鬧熱) | 84116409 |
| 766 | U+8001_U+5E2B_00 | 老師 | ᄅᅷ수1 | old | 老師 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/老師) | 92968637 |
| 769 | U+8001_U+CEE5_U+CEE5_00 | 老컥ˆ컥 | ᄅᅷ컥1컥 | old | 很老 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 770 | U+6F0F_U+6C23_00 | 漏氣 | ᄅᅷ2퀴 | lose face; be embarrassing | 丟臉 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/漏氣) | 87330221 |
| 772 | U+6D41_U+8840_00 | 流血 | ᄅᅷ휗 | flow | 流血 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/流血) | 92780327 |
| 776 | U+5167_U+5E95_00 | 內底 | 래되2 | inside | 裡面 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/內底) | 89033831 |
| 777 | U+5167_U+9762_00 | 內面 | 래삔5 | inside; face; surface | 裡面 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/內面) | 78604361 |
| 779 | U+4F86_U+53BB_00 | 來去 | 래킈 | to go | 去 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/來去) | 90765090 |
| 782 | U+5FF5_U+7D93_00 | 念經 | 럄곙1 | chant scripture | 念經 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/念經) | 89452392 |
| 783 | U+9023_U+97AD_00 | 連鞭 | 럄미1 | immediately; at once | 馬上; 立即 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/連鞭) | 90084790 |
| 786 | U+63A0_00 | 掠 | 럏1 | catch; seize | 掠 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/掠) | 92200576 |
| 787 | U+4E86_00 | 了 | ᄅᆤ2 | completed; finished | 了 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/了) | 92686034 |
| 790 | U+4E86_U+5F8C_00 | 了後 | ᄅᆤ1ᄋᅷ5 | after; afterwards | 之後 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/了後) | 89378462 |
| 795 | U+9732_U+87BA_00 | 露螺 | 러레4 | Rolex (watch) | 勞力士 | Preserved your explicit Rolex sense rather than replacing it with the other snail sense. | [Wiktionary](https://en.wiktionary.org/wiki/露螺) | 92924239 |
| 801 | U+8DEF_U+7528_00 | 路用 | 러영5 | useful | 用處 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/路用) | 87560701 |
| 802 | U+8DEF_U+7528_01 | 路用 | 러옝5 | useful | 用處 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/路用) | 87560701 |
| 809 | U+6335_00 | 挵 | 렁 | hit; knock | 撞; 敲 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/挵) | 89886960 |
| 812 | U+6D6A_U+6F2B_00 | 浪漫 | 렁빤5 | wave; wander | 浪漫 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/浪漫) | 92287345 |
| 813 | U+6AF3_U+4ED4_00 | 櫳仔 | 렁아2 | prison; jail | 監牢 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/櫳仔) | 78641531 |
| 814 | U+B801_U+7E3D_00 | 렁ˆ總 | 렁1정2 | total; general; always | 全部 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 815 | U+6D6A_U+5B50_00 | 浪子 | 렁주2 | wanderer; prodigal | 浪子 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/浪子) | 92368358 |
| 816 | U+6335_U+7834_00 | 挵破 | 렁2퐈 | to break | 撞破 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/挵破) | 88391569 |
| 818 | U+7281_U+7281_00 | 犁犁 | 레레4 | plow | 犁地 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 822 | U+5169_U+5149_00 | 兩光 | 령1겅1 | half-baked; unreliable | 兩光 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/兩光) | 78428640 |
| 823 | U+826F_U+541B_00 | 良君 | 령군1 | a good husband | 良君 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 829 | U+852B_00 | 蔫 | 롄1 | withered | 蔫 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/蔫) | 89201817 |
| 839 | U+51B7_U+51B7_00 | 冷冷 | 롕1롕2 | cold | 冷冷 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 840 | U+51B7_U+6696_00 | 冷暖 | 롕1롼2 | cold | 冷暖 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/冷暖) | 91062764 |
| 843 | U+60F1_00 | 惱 | 로2 | annoyed; trouble | 惱 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/惱) | 88210613 |
| 844 | U+52DE_U+788C_00 | 勞碌 | 로럭1 | labor; toil; busy; stone roller | 勞碌 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/勞碌) | 80128591 |
| 849 | U+843D_U+4F86_00 | 落來 | 롷래4 | come down | 下來 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/落來) | 83050030 |
| 851 | U+843D_U+8ECA_00 | 落車 | 롷챠1 | to alight | 下車 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/落車) | 87839230 |
| 852 | U+843D_U+5857_00 | 落塗 | 롷터4 | fall; drop | 落地 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/落塗) | 91001843 |
| 853 | U+843D_U+5857_U+6642_00 | 落塗時 | 롷터시4 | when landing; on reaching the ground | 落地時 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 855 | U+843D_U+8449_00 | 落葉 | 롷훃1 | fall; drop | 落葉 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/落葉) | 92283899 |
| 862 | U+6200_U+60C5_00 | 戀情 | 롼졩4 | romance; love affair | 戀情 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/戀情) | 85428436 |
| 863 | U+4E82_U+7D1B_U+7D1B_00 | 亂紛紛 | 롼훈훈5 | chaotic; random | 亂紛紛 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 865 | U+5973_U+5152_00 | 女兒 | 루1띠4 | child; son | 女兒 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/女兒) | 89745987 |
| 870 | U+6D41_U+9023_00 | 流連 | 류롄4 | flow | 流連 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/流連) | 90036893 |
| 873 | U+6D41_U+661F_00 | 流星 | 류칠1 | flow | 流星 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/流星) | 92161866 |
| 879 | U+96E2_U+5225_00 | 離別 | 리볟1 | other; different | 離別 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/離別) | 92139477 |
| 882 | U+96E2_U+958B_00 | 離開 | 리퀴1 | open | 離開 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/離開) | 85112161 |
| 883 | U+73B2_U+746F_00 | 玲瑯 | 린5렁1 | tinkling; delicate; gem sound; bright | 叮噹; 明亮 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 887 | U+6797_U+7530_00 | 林田 | 림뎬4 | Japanese surname Hayashida | 林田 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/林田) | 82566241 |
| 888 | U+98F2_U+2019_U+B877_U+D088_00 | 飲’롷킈 | 림1’롷킈 | drink | 喝下去 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 892 | U+98F2_U+6E6F_00 | 飲湯 | 림5틍1 | drink soup | 飲湯 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/飲湯) | 78689177 |
| 902 | U+669D_00 | 暝 | 메4 | night | 暝 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/暝) | 92700273 |
| 904 | U+BA54_U+B07C_U+9EB5_00 | 메ˉ끼ˉ麵 | 메5끼5미5 | noodles | 美極麵 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 906 | U+669D_U+2019_U+C2DC_00 | 暝’시 | 메4’시 | night | 晚上 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 912 | U+7CDC_00 | 糜 | 뭬4 | porridge | 糜 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/糜) | 91721608 |
| 915 | U+6BCF_U+5DE5_00 | 每工 | 뮈1강1 | every day | 每天 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/每工) | 78467140 |
| 921 | U+669D_01 | 暝 | 미4 | night | 暝 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/暝) | 92700273 |
| 923 | U+9EB5_U+56DD_00 | 麵囝 | 미걀2 | small noodles | 細麵 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/麵囝) | 78693299 |
| 924 | U+9EB5_U+8584_00 | 麵薄 | 미봏1 | thin noodles | 薄麵 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/麵薄) | 87975251 |
| 926 | U+9EB5_U+7DDA_U+7CCA_00 | 麵線糊 | 미솰2거4 | mee sua paste | 麵線糊 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/麵線糊) | 92046375 |
| 927 | U+669D_U+2019_U+C2DC_01 | 暝’시 | 미4’시 | night | 晚上 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 931 | U+98FD_U+98FD_00 | 飽飽 | 바1바2 | full | 飽飽 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 932 | U+5DF4_U+524E_00 | 巴剎 | 바5삳 | market | 巴剎 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/巴剎) | 91725221 |
| 937 | U+8179_U+809A_00 | 腹肚 | 박1더2 | belly | 腹肚 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/腹肚) | 87980605 |
| 938 | U+8179_U+5167_00 | 腹內 | 박1래5 | inside the belly | 腹內 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/腹內) | 88208453 |
| 941 | U+8FA6_U+516C_U+4F19_00 | 辦公伙 | 반겅5훼2 | playing house | 扮家家酒 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 943 | U+83DD_00 | 菝 | 받1 | guava | 番石榴; 芭樂 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/菝) | 88210742 |
| 945 | U+83DD_U+4ED4_00 | 菝仔 | 받아2 | guava | 番石榴; 芭樂 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/菝仔) | 90959950 |
| 947 | U+653E_U+5DE5_00 | 放工 | 방2강1 | finish work | 下班 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/放工) | 93365279 |
| 949 | U+653E_U+6352_00 | 放捒 | 방2삭 | put; release | 放開; 放棄 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/放捒) | 86462127 |
| 950 | U+653E_U+5C4E_00 | 放屎 | 방2새2 | defecate | 大便 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/放屎) | 81412602 |
| 955 | U+767E_U+7B8D_00 | 百箍 | 밯1커1 | hundred dollars | 百元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 959 | U+62DC_U+4E94_00 | 拜五 | 배2꺼5 | five | 星期五 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/拜五) | 83902869 |
| 960 | U+62DC_U+4E8C_00 | 拜二 | 배2띠5 | two | 星期二 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/拜二) | 83902810 |
| 961 | U+62DC_U+516D_00 | 拜六 | 배2락1 | six | 星期六 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/拜六) | 83902884 |
| 963 | U+62DC_U+4E09_00 | 拜三 | 배2살1 | three | 星期三 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/拜三) | 84548096 |
| 964 | U+62DC_U+56DB_00 | 拜四 | 배2시 | four | 星期四 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/拜四) | 91758124 |
| 965 | U+62DC_U+4E00_00 | 拜一 | 배2읻 | one | 星期一 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/拜一) | 85677121 |
| 967 | U+62DA_00 | 拚 | 뱔 | struggle; fight; work hard | 拚 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/拚) | 87580839 |
| 968 | U+6452_U+6383_00 | 摒掃 | 뱔2ᄉᅷ | sweep | 打掃 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/摒掃) | 84393448 |
| 970 | U+6F02_U+7DFB_00 | 漂緻 | ᄇᆤ5디 | fine; delicate | 精緻 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 975 | U+90E8_U+9580_00 | 部門 | 버믕4 | door | 部門 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/部門) | 87393883 |
| 977 | U+78C5_U+7A7A_00 | 磅空 | 벙캉1 | tunnel | 隧道 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/磅空) | 90457006 |
| 981 | U+7238_U+6BCD_00 | 爸母 | 베뿌2 | parents; father and mother | 父母 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/爸母) | 90514534 |
| 983 | U+64D8_00 | 擘 | 벻 | split; break open | 掰開 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/擘) | 92437289 |
| 986 | U+767E_U+59D3_00 | 百姓 | 벻1셀 | hundred | 百姓 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/百姓) | 92162161 |
| 988 | U+767E_U+59D3_01 | 百姓 | 벻1실 | hundred | 百姓 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/百姓) | 92162161 |
| 989 | U+767D_U+8CCA_00 | 白賊 | 벻찯1 | white | 謊話 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/白賊) | 92386595 |
| 991 | U+767D_U+7CD6_U+7CBF_00 | 白糖粿 | 벻틍궤2 | white sugar rice cake | 白糖粿 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 996 | U+4FBF_U+6240_00 | 便所 | 볜서2 | convenient; place; that which | 便所 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/便所) | 92700049 |
| 998 | U+8B8A_U+505A_00 | 變做 | 볜2죄 | become; turn into | 變成 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1004 | U+723F_00 | 爿 | 볭4 | side; half | 爿 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/爿) | 91819299 |
| 1010 | U+5175_U+8932_00 | 兵褲 | 볭5커 | soldier | 軍褲 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1011 | U+5175_U+982D_00 | 兵頭 | 볭5ᄐᅷ4 | soldier; head | 軍官 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1016 | U+4FDD_U+91CD_00 | 保重 | 보1뎡5 | heavy; again | 保重 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/保重) | 84008170 |
| 1017 | U+5761_U+5E95_00 | 坡底 | 보5되2 | downtown | 市中心 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/坡底) | 83685214 |
| 1019 | U+73BB_U+7483_U+676F_00 | 玻璃杯 | 보5레붸1 | glass cup | 玻璃杯 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/玻璃杯) | 87305366 |
| 1020 | U+4FDD_U+5E87_00 | 保庇 | 보1비 | protect; keep; shelter | 保佑 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/保庇) | 85537011 |
| 1021 | U+5BF6_U+60DC_00 | 寶惜 | 보1숗 | treasure; cherish | 珍惜 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/寶惜) | 78466735 |
| 1025 | U+8584_U+60C5_U+90CE_00 | 薄情郎 | 봏졩렁4 | thin; feeling; affection | 薄情郎 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1029 | U+534A_U+669D_00 | 半暝 | 봘2메4 | midnight | 半夜 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/半暝) | 88657351 |
| 1030 | U+534A_U+669D_01 | 半暝 | 봘2미4 | midnight | 半夜 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/半暝) | 88657351 |
| 1031 | U+8DCB_00 | 跋 | 봫1 | divine by moon blocks | 擲筊 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/跋) | 90960044 |
| 1032 | U+64A5_00 | 撥 | 봫 | push aside; allocate | 撥 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/撥) | 92532599 |
| 1033 | U+8DCB_U+7B4A_00 | 跋筊 | 봫ᄀᆤ2 | divine by moon blocks | 擲筊 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/跋筊) | 76778643 |
| 1034 | U+8DCB_U+676F_00 | 跋杯 | 봫붸1 | cast divination blocks | 擲筊 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/跋杯) | 91696865 |
| 1036 | U+516B_U+9EDE_U+6A94_00 | 八點檔 | 뵣1댬1덩2 | eight; point; dot | 八點檔 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/八點檔) | 81346623 |
| 1040 | U+516B_U+5343_00 | 八千 | 뵣1촁1 | eight; thousand | 八千 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/八千) | 91090266 |
| 1041 | U+516B_U+5206_00 | 八分 | 뵣1훈5 | eight parts; eighty percent | 八分 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/八分) | 78604548 |
| 1045 | U+672C_U+6027_U+96E3_U+79FB_00 | 本性難移 | 분1솅2란이4 | one's nature is hard to change | 本性難移 | Transparent whole-expression idiom; root/book/classifier describes only 本. The corrected meaning makes the Mandarin equivalent clear. |  |  |
| 1046 | U+7CDE_U+6383_00 | 糞掃 | 분2소 | sweep | 垃圾 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/糞掃) | 87496855 |
| 1058 | U+98DB_U+9F8D_00 | 飛龍 | 붸5롕4 | flying dragon | 飛龍 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/飛龍) | 87966189 |
| 1059 | U+80CC_U+5F71_00 | 背影 | 붸얄2 | shadow; image | 背影 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/背影) | 78665649 |
| 1067 | U+60B2_U+5287_00 | 悲劇 | 비5격1 | sad; drama; severe | 悲劇 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/悲劇) | 92161229 |
| 1071 | U+60B2_U+50B7_00 | 悲傷 | 비5셩1 | hurt; wound | 悲傷 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/悲傷) | 92137601 |
| 1072 | U+9589_U+601D_00 | 閉思 | 비2수 | shy | 害羞 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/閉思) | 85567107 |
| 1076 | U+8CA7_U+60F0_00 | 貧惰 | 빈돨5 | poor; lazy | 懶惰 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/貧惰) | 91701340 |
| 1081 | U+76EE_U+93E1_00 | 目鏡 | 빡걀 | eye | 眼鏡 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/目鏡) | 92386636 |
| 1083 | U+76EE_U+7709_00 | 目眉 | 빡빼4 | eye | 眉毛 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/目眉) | 84561832 |
| 1090 | U+95A9_U+8A9E_00 | 閩語 | 빤꾸2 | Min language | 閩語 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/閩語) | 91699410 |
| 1091 | U+95A9_U+6771_00 | 閩東 | 빤당1 | Mindong | 閩東 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/閩東) | 87982100 |
| 1092 | U+95A9_U+6771_U+8A9E_00 | 閩東語 | 빤당5꾸2 | Mindong language | 閩東語 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/閩東語) | 90951669 |
| 1095 | U+6162_U+6162_00 | 慢慢 | 빤빤5 | slow | 慢慢 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/慢慢) | 78736889 |
| 1096 | U+66FC_U+714E_U+7CBF_00 | 曼煎粿 | 빤졘5궤2 | apam balik | 曼煎糕 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/曼煎粿) | 91469111 |
| 1097 | U+842C_U+7B8D_00 | 萬箍 | 빤커1 | ten thousand dollars | 萬元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1098 | U+633D_U+56DE_00 | 挽回 | 빤1훼4 | return | 挽回 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/挽回) | 92279796 |
| 1099 | U+634C_00 | 捌 | 빧 | know; recognize | 知道; 認識 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/捌) | 92481222 |
| 1100 | U+832B_00 | 茫 | 빵4 | hazy; confused | 茫 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/茫) | 92201511 |
| 1104 | U+824B_U+823A_00 | 艋舺 | 빵1갛 | Monga; Bangka | 艋舺 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/艋舺) | 87994894 |
| 1106 | U+7DB2_U+8DEF_00 | 網路 | 빵러5 | road | 網路 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/網路) | 89309508 |
| 1113 | U+8089_U+7CBD_00 | 肉粽 | 빻1장 | meat rice dumpling | 肉粽 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/肉粽) | 91953913 |
| 1114 | U+8089_U+811E_00 | 肉脞 | 빻1초 | minced meat | 肉末 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/肉脞) | 90247268 |
| 1115 | U+8089_U+811E_U+9EB5_00 | 肉脞麵 | 빻1초2미5 | minced meat noodles | 肉末麵 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/肉脞麵) | 90247364 |
| 1120 | U+832B_01 | 茫 | 뻥4 | hazy; confused | 茫 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/茫) | 92201511 |
| 1121 | U+832B_U+9727_00 | 茫霧 | 뻥뿌5 | hazy; confused | 霧濛濛 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1126 | U+8FF7_U+984C_00 | 迷題 | 뻬되4 | riddle; puzzle | 謎題 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 1129 | U+8FF7_U+9B42_00 | 迷魂 | 뻬훈4 | enchant; lose one's soul | 迷魂 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/迷魂) | 78679910 |
| 1132 | U+52C9_U+5F37_00 | 勉強 | 뼨1경2 | strong | 勉強 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/勉強) | 92135163 |
| 1137 | U+540D_U+5229_00 | 名利 | 뼹리5 | name; reputation; benefit; profit | 名利 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/名利) | 79423007 |
| 1140 | U+660E_U+77E5_00 | 明知 | 뼹재1 | know clearly | 明知 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/明知) | 89138046 |
| 1141 | U+BF40_U+5F71_00 | 뽀影 | 뽀얄2 | not real; not legitimate | 不是真的 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1142 | U+BF40_U+8981_U+7DCA_00 | 뽀要緊 | 뽀ᄋᆤ2긴2 | not important; not urgent | 不要緊 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1143 | U+BF40_U+63D2_00 | 뽀插 | 뽀찹 | do not insert; not inserted | 不要插入 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1144 | U+BF40_U+5F69_U+5DE5_00 | 뽀彩工 | 뽀채1강1 | pointless; meaningless | 沒意思 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 1149 | U+BF94_U+8981_U+7DCA_00 | 뾔要緊 | 뾔ᄋᆤ2긴2 | won't be important; won't be urgent | 不會重要; 不會緊急 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1151 | U+8CE3_U+7968_00 | 賣票 | 뾔표 | sell tickets | 賣票 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1155 | U+7121_U+9593_U+5730_U+7344_00 | 無間地獄 | 뿌간5데꼑1 | not have; no; earth; place | 無間地獄 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/無間地獄) | 83128643 |
| 1157 | U+821E_U+53F0_00 | 舞台 | 뿌1대4 | dance; platform; Taiwan | 舞台 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/舞台) | 92289811 |
| 1159 | U+554F_U+984C_00 | 問題 | 뿐되4 | ask | 問題 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/問題) | 92160589 |
| 1161 | U+6587_U+79AE_00 | 文禮 | 뿐레2 | Boon Lay | 文禮 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1162 | U+6587_U+6587_U+4ED4_U+7B11_00 | 文文仔笑 | 뿐뿐아1쵸 | smile gently | 微笑 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/文文仔笑) | 78534010 |
| 1175 | U+7F8E_U+5922_00 | 美夢 | 삐1빵5 | beautiful dream | 美夢 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/美夢) | 78663524 |
| 1177 | U+7F8E_U+4E16_U+754C_00 | 美世界 | 삐1세2개 | Beauty World | 美世界 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1179 | U+7C73_U+9152_U+982D_00 | 米酒頭 | 삐1쥬1ᄐᅷ4 | rice; alcohol; wine; head | 米酒頭 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1180 | U+7C73_U+9152_U+982D_U+4ED4_00 | 米酒頭仔 | 삐1쥬1ᄐᅷ아2 | rice; alcohol; wine; head; diminutive suffix | 米酒頭 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1183 | U+7C73_U+7C89_U+6E6F_00 | 米粉湯 | 삐1훈1틍1 | rice vermicelli soup | 米粉湯 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1188 | U+9762_U+5E95_U+76AE_00 | 面底皮 | 삔되1풰4 | face; surface; where; which | 臉皮 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1190 | U+7720_U+5922_00 | 眠夢 | 삔빵5 | dream | 夢 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/眠夢) | 84392600 |
| 1191 | U+9762_U+8089_00 | 面肉 | 삔빻 | face flesh | 臉頰 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/面肉) | 78687367 |
| 1194 | U+660E_U+4ED4_U+8F09_00 | 明仔載 | 삔아1재 | bright; clear; diminutive suffix | 明天 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/明仔載) | 89936657 |
| 1195 | U+9762_U+518A_00 | 面冊 | 삔쳏 | face; surface | 臉書 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/面冊) | 92360361 |
| 1196 | U+7720_U+5E8A_00 | 眠床 | 삔층4 | sleep; bed | 床 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/眠床) | 92047234 |
| 1198 | U+8995_00 | 覕 | 삫 | hide; conceal | 躲藏 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/覕) | 91979216 |
| 1199 | U+8995_U+76F8_U+63E3_00 | 覕相揣 | 삫1쇼5췌5 | hide-and-seek | 捉迷藏 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/覕相揣) | 80243819 |
| 1201 | U+5C71_U+76DF_U+6D77_U+8A93_00 | 山盟海誓 | 산5뼹해1세 | mountain; sea | 山盟海誓 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/山盟海誓) | 63457136 |
| 1206 | U+4E09_U+500B_U+6708_00 | 三個月 | 살5고2뀋1 | three months | 三個月 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1208 | U+76F8_U+898B_U+6B61_00 | 相見歡 | 살5길2활1 | happy reunion; joy of meeting | 相見歡 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1209 | U+4E09_U+51AC_00 | 三冬 | 살5당1 | three years | 三冬 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/三冬) | 75585760 |
| 1210 | U+4E09_U+9EDE_U+9418_00 | 三點鐘 | 살5댬1졩1 | three o'clock | 三點鐘 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1211 | U+4E09_U+65E5_00 | 三日 | 살5띧1 | three days | 三日 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/三日) | 92198219 |
| 1212 | U+4E09_U+767E_00 | 三百 | 살5밯 | three hundred | 三百 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/三百) | 88229207 |
| 1215 | U+4E09_U+5206_00 | 三分 | 살5훈1 | three minutes; three cents | 三分 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/三分) | 84229327 |
| 1219 | U+7160_00 | 煠 | 샇1 | boil; blanch | 煮; 汆燙 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/煠) | 88657426 |
| 1225 | U+897F_U+5317_U+96E8_00 | 西北雨 | 새5박1허5 | sudden afternoon shower | 午後雷陣雨 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/西北雨) | 84478997 |
| 1226 | U+99DB_U+8ECA_00 | 駛車 | 새1챠1 | drive | 駛車 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/駛車) | 85394888 |
| 1229 | U+8B1D_U+7F6A_00 | 謝罪 | 샤줴 | apologize; atone | 謝罪 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/謝罪) | 92136242 |
| 1230 | U+5BEB_U+6279_00 | 寫批 | 샤1풰1 | write a letter | 寫信 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/寫批) | 91682926 |
| 1231 | U+5BEB_U+597D_00 | 寫好 | 샤1호2 | good | 寫好 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1232 | U+793E_U+6703_00 | 社會 | 샤훼5 | society; community | 社會 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/社會) | 90038506 |
| 1236 | U+5565_U+7269_00 | 啥物 | 샬1밓1 | what; something | 什麼 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/啥物) | 92696786 |
| 1237 | U+8072_U+8072_00 | 聲聲 | 샬5샬1 | sound; voice | 聲聲 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1241 | U+4010_00 | 䀐 | 샴1 | look; glance | 看; 瞥 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/䀐) | 87575923 |
| 1243 | U+9583_U+9583_U+720D_00 | 閃閃爍 | 샴1샴1싷 | sparkling; flickering | 閃爍 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1244 | U+9583_U+9583_U+720D_U+720D_00 | 閃閃爍爍 | 샴1샴1싷1싷 | sparkling; flickering | 閃閃爍爍 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1248 | U+96D9_U+4EBA_00 | 雙人 | 샹5랑4 | two people; pair | 雙人 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/雙人) | 73608908 |
| 1252 | U+75DF_00 | 痟 | ᄉᆤ2 | crazy | 瘋 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/痟) | 83798839 |
| 1256 | U+5C11_U+5E74_U+5BB6_00 | 少年家 | ᄉᆤ2롄게1 | young person | 年輕人 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/少年家) | 91701689 |
| 1257 | U+5C11_U+5E74_U+4EBA_00 | 少年人 | ᄉᆤ2롄랑4 | year; person; people | 年輕人 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/少年人) | 89745734 |
| 1258 | U+6D88_U+5931_00 | 消失 | ᄉᆤ5싣 | lose; mistake | 消失 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/消失) | 92161898 |
| 1260 | U+6D88_U+9063_00 | 消遣 | ᄉᆤ5켼2 | disappear; remove; send; dispatch | 消遣 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/消遣) | 85767909 |
| 1261 | U+75DF_U+8CAA_00 | 痟貪 | ᄉᆤ1탐1 | crazy | 貪心 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/痟貪) | 90796917 |
| 1268 | U+68EE_U+5984_00 | 森妄 | 섬5뻥5 | arrogant | 傲慢 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/森妄) | 84828564 |
| 1269 | U+723D_00 | 爽 | 성2 | comfortable; refreshed | 爽 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/爽) | 91974660 |
| 1271 | U+55AA_U+81BD_00 | 喪膽 | 성2달2 | terrified | 喪膽 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/喪膽) | 74750851 |
| 1277 | U+897F_U+65BD_00 | 西施 | 세5시1 | west | 西施 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/西施) | 89295738 |
| 1279 | U+4E16_U+5B97_00 | 世宗 | 세2정1 | world; generation | 世宗 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/世宗) | 87965863 |
| 1280 | U+4E16_U+60C5_00 | 世情 | 세2졩4 | worldly affairs; human feelings | 世情 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/世情) | 85641523 |
| 1286 | U+8E05_00 | 踅 | 셓1 | wander | 轉; 逛 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/踅) | 92525684 |
| 1292 | U+60F3_U+6B32_00 | 想欲 | 셜뼇 | want to | 想要 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/想欲) | 84392928 |
| 1299 | U+50B7_U+60B2_00 | 傷悲 | 셩5비1 | hurt; wound | 傷悲 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/傷悲) | 74033594 |
| 1300 | U+8A73_U+7D30_00 | 詳細 | 셩쇠 | small; fine | 詳細 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/詳細) | 92162809 |
| 1301 | U+76F8_U+96A8_00 | 相隨 | 셩5쉬4 | follow together | 相隨 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/相隨) | 73596033 |
| 1304 | U+7FD4_U+5B89_00 | 翔安 | 셩안1 | peace; safe | 翔安 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/翔安) | 87974765 |
| 1305 | U+4E0A_U+611B_00 | 上愛 | 셩애 | love most; favourite | 最愛 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 1309 | U+76F8_U+9022_00 | 相逢 | 셩5헝4 | mutual; appearance | 相逢 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/相逢) | 91571149 |
| 1312 | U+76F8_U+6703_00 | 相會 | 셩5훼5 | mutual; appearance; can; meeting | 相會 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/相會) | 61493883 |
| 1314 | U+8272_00 | 色 | 셱 | colour | 色 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/色) | 92691395 |
| 1316 | U+719F_U+4F3C_00 | 熟似 | 셱새5 | know; be acquainted with | 認識 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/熟似) | 92051916 |
| 1321 | U+87EE_U+87F2_00 | 蟮蟲 | 셴탕4 | house lizard | 壁虎 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/蟮蟲) | 80881993 |
| 1326 | U+76DB_U+6E2F_00 | 盛港 | 솅강2 | Sengkang | 盛港 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1329 | U+751F_U+7406_00 | 生理 | 솅5리2 | business; livelihood | 生意; 生計 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/生理) | 92250320 |
| 1334 | U+9396_U+5319_00 | 鎖匙 | 소1시4 | lock; spoon; key | 鑰匙 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/鎖匙) | 89107476 |
| 1337 | U+7D32_00 | 紲 | 솨 | continue; connect | 繼續; 連接 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/紲) | 92361420 |
| 1338 | U+7D32_U+4F86_00 | 紲來 | 솨2래4 | come | 接下來 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1342 | U+65CB_U+9C21_U+9F13_00 | 旋鰡鼓 | 솬5류5거2 | Pond loach | 泥鰍 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/旋鰡鼓) | 78635684 |
| 1343 | U+8A15_U+524A_00 | 訕削 | 솬샿 | mock; tease; cut; pare | 嘲笑; 諷刺 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1351 | U+5C71_U+9F9C_00 | 山龜 | 솰5구1 | bumpkin | 土包子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/山龜) | 84001648 |
| 1352 | U+5C71_U+9802_00 | 山頂 | 솰5뎽2 | mountaintop | 山頂 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/山頂) | 92161005 |
| 1354 | U+715E_00 | 煞 | 쇃 | stop; finish; unexpectedly | 停; 結束; 竟然 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/煞) | 92677644 |
| 1357 | U+7D30_U+56DD_00 | 細囝 | 쇠2걀2 | small; fine; child | 小孩 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/細囝) | 78661562 |
| 1359 | U+7D30_U+8072_00 | 細聲 | 쇠2샬1 | soft voice; quietly | 小聲 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/細聲) | 82356759 |
| 1360 | U+7D30_U+7D30_00 | 細細 | 쇠2쇠 | small; finely | 細細 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/細細) | 92237236 |
| 1361 | U+7D30_U+6F22_00 | 細漢 | 쇠2한 | small; young | 小; 年幼 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/細漢) | 89351387 |
| 1365 | U+76F8_U+4EDD_00 | 相仝 | 쇼5강5 | same | 一樣 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/相仝) | 90845182 |
| 1366 | U+76F8_U+8B93_00 | 相讓 | 쇼5뉴5 | give way to each other | 相讓 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/相讓) | 61492732 |
| 1370 | U+71D2_U+8089_U+7CBD_00 | 燒肉粽 | 쇼5빻1장 | hot rice dumpling | 熱粽子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1373 | U+71D2_U+71D2_00 | 燒燒 | 쇼5쇼1 | hot; warm | 熱 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/燒燒) | 78534843 |
| 1376 | U+76F8_U+501A_00 | 相倚 | 쇼5와2 | mutual; appearance | 相互依靠 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/相倚) | 87391420 |
| 1377 | U+5C0F_U+59D0_00 | 小姐 | 쇼1쟈2 | small | 小姐 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/小姐) | 91691762 |
| 1379 | U+71D2_U+9152_U+8766_00 | 燒酒蝦 | 쇼5쥬1헤4 | drunken shrimp | 燒酒蝦 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1381 | U+76F8_U+4F28_00 | 相伨 | 쇼5틴5 | support each other; help one another | 相挺; 互助 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 1382 | U+76F8_U+62CD_00 | 相拍 | 쇼5팧 | fight | 打架 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/相拍) | 91978919 |
| 1384 | U+5C0F_U+96E8_U+5098_00 | 小雨傘 | 쇼1허솰 | small umbrella | 小雨傘 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/小雨傘) | 78622106 |
| 1386 | U+60DC_U+5225_00 | 惜別 | 숗1볟1 | farewell reluctantly | 惜別 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/惜別) | 86476107 |
| 1393 | U+8212_U+4F6E_00 | 舒佮 | 수5갛 | comfortable; stretch; and; with | 舒服 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1394 | U+4E8B_U+5230_U+5982_U+4ECA_00 | 事到如今 | 수ᄀᅷ2뚜김1 | matter; affair; arrive; reach; as | 事到如今 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/事到如今) | 84385193 |
| 1395 | U+4F7F_U+7136_00 | 使然 | 수1뗸4 | caused by; result of | 使然 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/使然) | 58934723 |
| 1396 | U+8F38_U+5165_U+6CD5_00 | 輸入法 | 수5띱홛 | enter | 輸入法 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/輸入法) | 78679319 |
| 1397 | U+8F38_U+4EBA_00 | 輸人 | 수5랑4 | lose to others; be inferior | 不如人 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1399 | U+601D_U+6200_00 | 思戀 | 수5롼4 | miss; yearn for | 思戀 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/思戀) | 84322659 |
| 1400 | U+4E8B_U+5BE6_00 | 事實 | 수싣1 | matter; affair; real; solid | 事實 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/事實) | 91756441 |
| 1401 | U+8F38_U+8D0F_00 | 輸贏 | 수5얄4 | win or lose; outcome | 輸贏 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/輸贏) | 92232906 |
| 1404 | U+56DB_U+914D_00 | 四配 | 수2풰 | matching; compatible; suitable | 相配; 合適 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/四配) | 92052244 |
| 1408 | U+5B6B_U+4E2D_U+5C71_00 | 孫中山 | 순5뎡5산1 | Sun Yat-sen | 孫中山 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1410 | U+9806_U+9806_00 | 順順 | 순순5 | smoothly | 順利地 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1411 | U+7D14_U+60C5_00 | 純情 | 순졩4 | pure feelings | 純情 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/純情) | 92162435 |
| 1419 | U+96D6_U+7136_00 | 雖然 | 쉬5뗸4 | so; thus | 雖然 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/雖然) | 86603880 |
| 1420 | U+5AA0_U+5AA0_00 | 媠媠 | 쉬1쉬2 | beautiful | 漂亮 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1421 | U+96A8_U+7DE3_00 | 隨緣 | 쉬옌4 | let fate decide; go with fate | 隨緣 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/隨緣) | 85176189 |
| 1427 | U+53D7_U+6C23_00 | 受氣 | 슈키 | angry | 生氣 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/受氣) | 89552195 |
| 1431 | U+50B7_U+904E_00 | 傷過 | 슐5궤 | hurt; wound; pass; exceed | 太; 過於 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/傷過) | 78465358 |
| 1432 | U+60F3_U+6B32_01 | 想欲 | 슐뼇 | want to | 想要 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/想欲) | 84392928 |
| 1433 | U+60F3_U+6B32_02 | 想欲 | 슐뾯 | want to | 想要 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/想欲) | 84392928 |
| 1440 | U+9178_U+751C_U+82E6_U+6F80_00 | 酸甜苦澀 | 승5딜5커1샵 | sour, sweet, bitter and astringent; joys and hardships | 酸甜苦澀 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1443 | U+5E8F_U+5927_00 | 序大 | 싀돠5 | an elder | 長輩 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/序大) | 92292889 |
| 1444 | U+5E8F_U+5927_U+4EBA_00 | 序大人 | 싀돠랑4 | an elder | 長輩 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/序大人) | 92276970 |
| 1452 | U+56DB_U+754C_00 | 四界 | 시2괴 | four | 到處 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/四界) | 87964955 |
| 1455 | U+4E16_U+4EBA_00 | 世人 | 시2랑4 | people of the world | 世人 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/世人) | 86469561 |
| 1456 | U+56DB_U+767E_00 | 四百 | 시2밯 | four hundred | 四百 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/四百) | 88050729 |
| 1457 | U+6B7B_U+6B7B_00 | 死死 | 시1시2 | firmly; tightly; resolutely | 死死 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/死死) | 60880541 |
| 1461 | U+6642_U+9663_00 | 時陣 | 시준5 | time; occasion | 時候 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/時陣) | 91749480 |
| 1463 | U+8FAD_U+982D_U+8DEF_00 | 辭頭路 | 시ᄐᅷ러5 | head; road | 辭職 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/辭頭路) | 90321619 |
| 1470 | U+8EAB_U+61F8_00 | 身懸 | 신5괘4 | tall | 高個子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/身懸) | 89852088 |
| 1471 | U+8EAB_U+8457_00 | 身著 | 신5뎍1 | wearing | 穿著 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1474 | U+8EAB_U+908A_00 | 身邊 | 신5빌1 | beside; around | 身邊 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/身邊) | 80124818 |
| 1481 | U+795E_U+901A_00 | 神通 | 신텅1 | supernatural power | 神通 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/神通) | 92250392 |
| 1485 | U+5931_U+843D_00 | 失落 | 싣1롷1 | lost; disappointed | 失落 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/失落) | 92118655 |
| 1487 | U+5931_U+671B_00 | 失望 | 싣1뻥5 | disappointment | 失望 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/失望) | 92137672 |
| 1489 | U+5931_U+5FD7_00 | 失志 | 싣1지 | lose faith | 灰心 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/失志) | 87305715 |
| 1495 | U+5FC3_U+72C2_U+706B_U+8457_00 | 心狂火著 | 심5겅훼1돟1 | to lose temper and feel rage | 大發雷霆 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/心狂火著) | 91979875 |
| 1498 | U+5FC3_U+5167_00 | 心內 | 심5래5 | in one's heart | 心內 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/心內) | 88895774 |
| 1500 | U+4EC0_U+7269_00 | 什物 | 심1밓1 | what | 什麼 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/什物) | 91063902 |
| 1511 | U+5BE9_U+5224_00 | 審判 | 심1퐐 | judge; examine; decide | 審判 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/審判) | 92160929 |
| 1513 | U+963F_00 | 阿 | 아1 | prefix used in terms of address, especially endearingly | 阿 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/阿) | 92638563 |
| 1515 | U+4ED4_00 | 仔 | 아2 | diminutive suffix | 兒; 子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/仔) | 91557219 |
| 1519 | U+963F_U+8205_00 | 阿舅 | 아5구5 | maternal uncle | 舅舅 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/阿舅) | 90893789 |
| 1520 | U+963F_U+5997_00 | 阿妗 | 아5김5 | prefix for names; aunt | 舅母 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/阿妗) | 90893791 |
| 1521 | U+963F_U+5A18_00 | 阿娘 | 아5냐4 | mother | 母親 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/阿娘) | 91819075 |
| 1524 | U+963F_U+6BCD_00 | 阿母 | 아5뿌2 | mother | 母親 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/阿母) | 91740118 |
| 1525 | U+963F_U+4FEE_U+7F85_00 | 阿修羅 | 아5슈5로4 | prefix for names; repair; cultivate; net; gather | 阿修羅 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/阿修羅) | 92291425 |
| 1527 | U+963F_U+7956_00 | 阿祖 | 아5저2 | great-grandparent | 曾祖父母 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/阿祖) | 90556650 |
| 1529 | U+963F_U+59CA_00 | 阿姊 | 아5지2 | older sister | 阿姊 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/阿姊) | 91150021 |
| 1531 | U+963F_U+5144_00 | 阿兄 | 아5햘1 | older brother | 哥哥 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/阿兄) | 90893721 |
| 1533 | U+6C83_U+6FB9_00 | 沃澹 | 악1담4 | wet | 弄濕 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/沃澹) | 78465653 |
| 1538 | U+5B89_U+6170_00 | 安慰 | 안5위5 | peace; safe | 安慰 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/安慰) | 89296473 |
| 1539 | U+6309_U+600E_00 | 按怎 | 안1좔2 | press; according to; how | 怎麼 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/按怎) | 91767698 |
| 1540 | U+6309_U+600E_U+6A23_00 | 按怎樣 | 안1좔1율5 | press; according to; how; appearance; manner | 怎麼樣 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/按怎樣) | 62586840 |
| 1542 | U+63DE_U+8170_00 | 揞腰 | 알2요1 | stoop; bend over; bow slightly | 彎腰 | The attested àⁿ-io sense is bend over; 插腰 described a different action. | [Wiktionary](https://en.wiktionary.org/wiki/揞腰) | 78465743 |
| 1544 | U+9837_U+9838_00 | 頷頸 | 암군2 | neck | 頸項 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/頷頸) | 87991258 |
| 1545 | U+6697_U+669D_00 | 暗暝 | 암2메4 | night | 晚上 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/暗暝) | 91976732 |
| 1546 | U+6697_U+669D_01 | 暗暝 | 암2미4 | night | 晚上 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/暗暝) | 91976732 |
| 1547 | U+6697_U+8D96_U+8D96_00 | 暗趖趖 | 암2소소4 | very dark | 漆黑 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/暗趖趖) | 78570546 |
| 1548 | U+6697_U+6642_00 | 暗時 | 암2시4 | nighttime | 晚上 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/暗時) | 83572189 |
| 1549 | U+6697_U+5B89_00 | 暗安 | 암2안1 | good night | 晚安 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/暗安) | 78636848 |
| 1550 | U+6697_U+5D01_00 | 暗崁 | 암2캄 | conceal; hide away | 藏; 隱藏 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/暗崁) | 91661184 |
| 1551 | U+7FC1_00 | 翁 | 앙1 | old man; father-in-law | 翁 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/翁) | 92490910 |
| 1553 | U+7D05_U+9F9C_U+7CBF_00 | 紅龜粿 | 앙구5궤2 | Ang ku kueh; red tortoise cake | 紅龜粿 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/紅龜粿) | 91529425 |
| 1557 | U+7D05_U+767B_U+8A18_00 | 紅登記 | 앙뎽5기 | National Registration Identity Card (NRIC) (Singapore Citizen) | 新加坡公民身份證 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1558 | U+7D05_U+6BDB_00 | 紅毛 | 앙머4 | Western; Caucasian | 紅毛 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/紅毛) | 91771633 |
| 1560 | U+7D05_U+6BDB_U+4EBA_00 | 紅毛人 | 앙머랑4 | Westerner; Caucasian | 紅毛人 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/紅毛人) | 92232836 |
| 1561 | U+7D05_U+6BDB_U+8A71_00 | 紅毛話 | 앙머웨5 | Caucasian speech; English | 英語 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/紅毛話) | 91686932 |
| 1562 | U+7FC1_U+5A7F_00 | 翁婿 | 앙5새 | husband | 丈夫 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/翁婿) | 90557488 |
| 1563 | U+7D05_U+8272_00 | 紅色 | 앙셱 | red colour | 紅色 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/紅色) | 92476950 |
| 1565 | U+7D05_U+71D2_00 | 紅燒 | 앙쇼1 | braised in soy sauce | 紅燒 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/紅燒) | 91618072 |
| 1569 | U+9D28_U+8089_00 | 鴨肉 | 앟1빻 | duck meat | 鴨肉 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1572 | U+5F8C_U+79AE_U+62DC_00 | 後禮拜 | ᄋᅷ레1배 | next week | 下星期 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1573 | U+5F8C_U+64FA_00 | 後擺 | ᄋᅷ배2 | next time; later | 下次; 以後 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/後擺) | 82606386 |
| 1574 | U+5F8C_U+58C1_00 | 後壁 | ᄋᅷ뱧 | after; behind | 後面 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/後壁) | 91768019 |
| 1575 | U+5F8C_U+5C3E_00 | 後尾 | ᄋᅷ붸2 | behind; later | 後面; 以後 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/後尾) | 88296968 |
| 1576 | U+5F8C_U+4E16_U+4EBA_00 | 後世人 | ᄋᅷ시2랑4 | future generations; descendants | 後世人 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/後世人) | 78626597 |
| 1579 | U+54C0_U+6028_00 | 哀怨 | 애5완5 | resent; complain | 哀怨 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/哀怨) | 91664548 |
| 1583 | U+591C_U+90FD_U+5E02_00 | 夜都市 | 야더치5 | night city | 夜都市 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1585 | U+591C_U+53C9_00 | 夜叉 | 야체1 | night | 夜叉 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/夜叉) | 92250585 |
| 1587 | U+591C_U+5FEB_U+8ECA_00 | 夜快車 | 야쾌2챠1 | night express train | 夜快車 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1590 | U+8D0F_U+7B4A_00 | 贏筊 | 얄ᄀᆤ2 | win; divination blocks | 賭贏 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1595 | U+7336_U+672A_00 | 猶未 | 얗1쀄5 | not yet | 還沒 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/猶未) | 88657334 |
| 1597 | U+67B5_U+9B3C_00 | 枵鬼 | ᄋᆤ5귀2 | hungry person; glutton | 餓鬼 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/枵鬼) | 85012456 |
| 1609 | U+70CF_U+767D_00 | 烏白 | 어5벻1 | wrongly; randomly | 胡亂 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/烏白) | 90065393 |
| 1610 | U+70CF_U+767D_U+8B1B_00 | 烏白講 | 어5벻겅2 | talk nonsense | 胡說 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/烏白講) | 81546946 |
| 1611 | U+70CF_U+767D_U+7121_U+5E38_00 | 烏白無常 | 어5벻뿌셩4 | Black and White Impermanence (underworld deities) | 黑白無常 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/黑白無常) |  |
| 1612 | U+70CF_U+7D17_00 | 烏紗 | 어5세1 | official's hat; official position (figurative) | 烏紗 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/烏紗) | 78648440 |
| 1613 | U+70CF_U+8272_00 | 烏色 | 어5셱1 | black | 黑色 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/烏色) | 82356211 |
| 1614 | U+70CF_U+9D09_00 | 烏鴉 | 어5아1 | black | 烏鴉 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/烏鴉) | 91732810 |
| 1615 | U+70CF_U+6697_00 | 烏暗 | 어5암 | dark | 黑暗 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/烏暗) | 84199630 |
| 1616 | U+70CF_U+70CF_00 | 烏烏 | 어5어1 | black | 黑 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1617 | U+70CF_U+9670_00 | 烏陰 | 어5임1 | dark; gloomy | 陰暗 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/烏陰) | 86576238 |
| 1619 | U+6E56_U+6C34_U+9762_00 | 湖水面 | 어쥐1삔5 | water; face; surface | 湖水面 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1620 | U+60E1_U+9B3C_00 | 惡鬼 | 억1귀2 | ghost | 惡鬼 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/惡鬼) | 82458861 |
| 1627 | U+4E2A_00 | 个 | 에4 | individual; classifier | 個 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/个) | 91045166 |
| 1632 | U+4E0B_U+6661_00 | 下晡 | 에버1 | below; under | 下午 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/下晡) | 86593314 |
| 1633 | U+4E0B_U+660F_00 | 下昏 | 에흥1 | dusk; evening | 傍晚 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/下昏) | 81469475 |
| 1640 | U+52C7_U+5065_00 | 勇健 | 영1걀5 | brave | 健壯 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/勇健) | 78607439 |
| 1641 | U+7528_U+5FC3_00 | 用心 | 영심1 | to be mindful | 用心 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/用心) | 92138906 |
| 1645 | U+7DE3_U+6295_00 | 緣投 | 옌ᄃᅷ4 | handsome | 英俊 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/緣投) | 91949114 |
| 1646 | U+5EF6_U+5E73_00 | 延平 | 옌볭4 | flat; ordinary | 延平 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/延平) | 87975656 |
| 1647 | U+5EF6_U+5E73_U+738B_00 | 延平王 | 옌볭엉4 | flat; ordinary; king | 延平王 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1649 | U+80ED_U+8102_U+6C34_U+7C89_00 | 胭脂水粉 | 옌5지5쥐1훈2 | water; flour; powder | 胭脂水粉 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1650 | U+7DE3_U+4EFD_00 | 緣份 | 옌훈5 | fate; connection | 緣份 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/緣份) | 49935045 |
| 1656 | U+82F1_U+6587_00 | 英文 | 옝5뿐4 | writing; literature | 英文 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/英文) | 87610103 |
| 1657 | U+4E0B_U+660F_U+6697_00 | 下昏暗 | 옝5암 | dusk; evening | 傍晚 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/下昏暗) | 91467183 |
| 1662 | U+86B5_U+4ED4_00 | 蚵仔 | 오아2 | diminutive suffix | 牡蠣 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/蚵仔) | 91777723 |
| 1668 | U+51A4_U+5BB6_00 | 冤家 | 완5게1 | quarrel; argue; bicker | 吵架; 爭吵 | The oan-ke reading matches the Hokkien quarrel sense, not Mandarin enemy/sweetheart. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/冤家) | 92486629 |
| 1669 | U+6028_U+547D_00 | 怨命 | 완2먀5 | resent life | 怨命運 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/怨命) | 91062866 |
| 1671 | U+51A4_U+4EC7_00 | 冤仇 | 완5슈4 | wronged; injustice; enemy; hatred | 冤仇 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/冤仇) | 84547799 |
| 1672 | U+6028_U+5C24_00 | 怨尤 | 완2유4 | resent; complain | 怨尤 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1675 | U+6028_U+5606_00 | 怨嘆 | 완2탄 | to sigh; to lament | 嘆息; 埋怨 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/怨嘆) | 83530510 |
| 1677 | U+96F2_U+541E_U+9EB5_00 | 雲吞麵 | 완탄5미5 | wonton noodles | 雲吞麵 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/雲吞麵) | 87971082 |
| 1678 | U+6028_U+5929_00 | 怨天 | 완2틸1 | resent | 怨天 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1680 | U+65A1_00 | 斡 | 왇1 | turn; manage | 斡 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/斡) | 84074921 |
| 1683 | U+65A1_U+982D_00 | 斡頭 | 왇ᄐᅷ4 | head | 回頭 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/斡頭) | 81412611 |
| 1684 | U+65A1_U+982D_U+884C_00 | 斡頭行 | 왇ᄐᅷ걀4 | turn around and walk | 轉身走 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1685 | U+65A1_U+982D_U+8D70_00 | 斡頭走 | 왇ᄐᅷᄌᅷ2 | head; run; leave | 轉身跑; 轉身離開 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1689 | U+664F_U+5230_00 | 晏到 | 왈2ᄀᅷ | arrive late | 遲到 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/晏到) | 92767744 |
| 1695 | U+8170_U+61F8_00 | 腰懸 | 요5괠4 | tall | 高個子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1700 | U+C6B0_U+6642_00 | 우時 | 우시4 | sometimes | 有時候 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1701 | U+C6B0_U+5F71_00 | 우影 | 우얄2 | real; tangible | 是真的 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1702 | U+C6B0_U+5F71_U+2019_U+BF40_00 | 우影’뽀ˊ | 우얄2’뽀4 | is it for real | 是真的嗎 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1707 | U+96B1_U+75C0_U+6A4B_00 | 隱痀橋 | 운1구5교4 | arched bridge | 拱橋 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 1708 | U+904B_U+9014_00 | 運途 | 운더4 | luck; transport | 運氣 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/運途) | 78680568 |
| 1712 | U+904B_U+547D_00 | 運命 | 운먀5 | fate; destiny | 命運 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/運命) | 92295051 |
| 1713 | U+6EAB_U+6587_U+723E_U+96C5_00 | 溫文爾雅 | 운5뿐니1ᅙᅡ2 | writing; literature | 溫文爾雅 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/溫文爾雅) | 62086417 |
| 1716 | U+9B31_U+5352_00 | 鬱卒 | 욷1줃 | depressed; frustrated | 鬱悶 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/鬱卒) | 79289055 |
| 1723 | U+70BA_U+4EC0_U+7269_00 | 為什物 | 위심1밓1 | why | 為什麼 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/為什物) | 78563035 |
| 1725 | U+70BA_U+600E_U+6A23_00 | 為怎樣 | 위좔1율5 | for; because of | 為什麼 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1726 | U+70BA_U+6B62_00 | 為止 | 위지2 | for; because of | 為止 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/為止) | 80125039 |
| 1737 | U+6CB9_U+57A2_U+57A2_00 | 油垢垢 | 유ᄀᅷ2ᄀᅷ | very greasy | 油垢垢 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1738 | U+6CB9_U+57A2_U+5473_00 | 油垢味 | 유ᄀᅷ2삐5 | greasy taste | 油垢味 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1739 | U+7336_U+539F_00 | 猶原 | 유5꽌4 | still; as if; original; source | 仍然 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/猶原) | 91716374 |
| 1741 | U+6CB9_U+6C60_00 | 油池 | 유디4 | Yew Tee | 油池 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1742 | U+5C24_U+4EBA_00 | 尤人 | 유띤4 | resent | 尤人 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1744 | U+5E7C_U+9EB5_00 | 幼麵 | 유2미5 | thin noodles | 細麵 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/幼麵) | 78625194 |
| 1745 | U+6182_U+50B7_00 | 憂傷 | 유5셩1 | sorrowful | 憂傷 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/憂傷) | 91725626 |
| 1747 | U+6709_U+60C5_U+773E_U+751F_00 | 有情眾生 | 유1졩졍2솅1 | sentient beings (Buddhism) | 有情眾生 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 1748 | U+6182_U+6101_00 | 憂愁 | 유5츄4 | worry; sorrow | 憂愁 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/憂愁) | 92283904 |
| 1749 | U+6709_U+5B5D_00 | 有孝 | 유1ᄒᅷ | filial | 孝順 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/有孝) | 92013806 |
| 1753 | U+C74C_U+8457_00 | 음著 | 음둏1 | not right; wrong | 不對 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1755 | U+5411_U+671B_00 | 向望 | 응2빵5 | hope; look forward to | 希望 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/向望) | 84409541 |
| 1756 | U+9EC3_U+8272_00 | 黃色 | 응셱 | yellow colour | 黃色 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/黃色) | 87975400 |
| 1765 | U+6905_U+689D_00 | 椅條 | 이1ᄅᆤ4 | chair | 長椅 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/椅條) | 88210392 |
| 1768 | U+610F_U+611B_00 | 意愛 | 이2애 | romantic intention | 愛意 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/意愛) | 92757699 |
| 1770 | U+7570_U+9109_00 | 異鄉 | 이형1 | different; strange; hometown; countryside | 異鄉 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/異鄉) | 86851625 |
| 1780 | U+4E00_U+822C_00 | 一般 | 읻1봘1 | normal; ordinary | 一般 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/一般) | 92198202 |
| 1789 | U+65E9_U+9813_00 | 早頓 | 자1등 | early; morning | 早餐 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/早頓) | 92750312 |
| 1790 | U+6628_U+6697_00 | 昨暗 | 자5암 | dark | 昨晚 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/昨暗) | 88031694 |
| 1792 | U+6628_U+660F_00 | 昨昏 | 자5흥1 | yesterday evening | 昨晚 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/昨昏) | 90047657 |
| 1801 | U+5341_U+5E74_00 | 十年 | 잡니4 | ten years | 十年 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/十年) | 86189781 |
| 1802 | U+5341_U+6BBF_U+95BB_U+541B_00 | 十殿閻君 | 잡뎬꺔군1 | ten; lord; ruler | 十殿閻君 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1803 | U+5341_U+842C_00 | 十萬 | 잡빤5 | one hundred thousand | 十萬 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/十萬) | 87194654 |
| 1804 | U+5341_U+7B8D_00 | 十箍 | 잡커1 | ten dollars | 十元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1807 | U+8D70_U+63E3_00 | 走揣 | ᄌᅷ1췌5 | search everywhere; go looking for | 四處尋找 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/走揣) | 92746605 |
| 1808 | U+7076_U+8DE4_00 | 灶跤 | ᄌᅷ2카1 | stove; foot | 廚房 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/灶跤) | 84878943 |
| 1809 | U+8D70_U+53BB_00 | 走去 | ᄌᅷ1킈 | run over to; run to | 跑去 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/走去) | 78463987 |
| 1815 | U+5728_U+4E16_00 | 在世 | 재세 | to be in this world | 在世 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/在世) | 86462044 |
| 1816 | U+5728_U+5BA4_00 | 在室 | 재셱 | virgin | 處女; 處男 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 1817 | U+77E5_U+5F71_00 | 知影 | 재5얄2 | know | 知道 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/知影) | 91749703 |
| 1820 | U+4B55_00 | 䭕 | 쟐2 | bland | 淡; 沒味道 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/䭕) | 87584787 |
| 1824 | U+6B63_U+624B_00 | 正手 | 쟐2츄2 | right hand | 右手 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/正手) | 88642511 |
| 1825 | U+8AA0_U+597D_00 | 誠好 | 쟐호2 | good | 很好 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1829 | U+5C16_U+982D_00 | 尖頭 | 쟘5ᄐᅷ4 | pointed head | 尖頭 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1830 | U+5C16_U+982D_U+B610_U+B514_00 | 尖頭또디ˆ | 쟘5ᄐᅷ또디1 | baguette | 法棍 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 1836 | U+906E_00 | 遮 | 쟣 | this much; so | 這麼 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/遮) | 92201960 |
| 1838 | U+906E_U+9087_00 | 遮邇 | 쟣1니5 | this much; to this extent | 這麼 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1839 | U+98DF_U+529B_00 | 食力 | 쟣랃1 | strenuous; exhausting; in trouble (colloquial) | 糟了; 吃力 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/食力; https://en.wiktionary.org/wiki/jialat) |  |
| 1842 | U+98DF_U+98FD_U+2019_U+1105_U+11A4_00 | 食飽’ᄅᆤˋ | 쟣바2’ᄅᆤ2 | eat until full; satiated | 吃飽了 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1843 | U+98DF_U+98FD_U+2019_U+C004_00 | 食飽’쀄 | 쟣바2’쀄 | are (you) full? (used as a greeting) | 吃飽了嗎 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1847 | U+98DF_U+98A8_00 | 食風 | 쟣헝1 | relax; take a vacation | 休閒; 兜風 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/食風) | 84449621 |
| 1851 | U+7167_U+8B1B_00 | 照講 | ᄌᆤ2겅2 | to say as it is | 照實說 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/照講) | 78571089 |
| 1852 | U+7167_U+6B65_U+884C_00 | 照步行 | ᄌᆤ2버걀4 | according to; shine; step; walk; go | 按步行走 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1854 | U+7167_U+8D77_U+5DE5_00 | 照起工 | ᄌᆤ2키1강1 | as usual; according to work | 照常 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1857 | U+52A9_U+9663_00 | 助陣 | 저딘5 | period; formation | 助陣 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/助陣) | 44580233 |
| 1858 | U+7956_U+50B3_00 | 祖傳 | 저1퇀4 | ancestor | 祖傳 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/祖傳) | 84643463 |
| 1873 | U+8DB3_U+82B3_00 | 足芳 | 젹1팡1 | very fragrant | 很香 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1879 | U+7D42_U+6B78_00 | 終歸 | 졍5귀1 | end; finally; return; belong to | 終歸 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/終歸) | 84228917 |
| 1881 | U+5C07_U+4F86_00 | 將來 | 졍5래4 | come | 將來 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/將來) | 93136964 |
| 1882 | U+773E_U+751F_00 | 眾生 | 졍2솅1 | life; give birth | 眾生 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/眾生) | 91831070 |
| 1883 | U+773E_U+795E_00 | 眾神 | 졍2신4 | deity; spirit | 眾神 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/眾神) | 74191056 |
| 1885 | U+7AE0_U+6CD5_00 | 章法 | 졍5홛 | method; order | 章法 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/章法) | 82114793 |
| 1889 | U+524D_U+7A0B_00 | 前程 | 졘뎽4 | before; front | 前程 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/前程) | 91049108 |
| 1890 | U+524D_U+9032_00 | 前進 | 졘진 | before; front | 前進 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/前進) | 92136165 |
| 1901 | U+60C5_U+8DEF_00 | 情路 | 졩러5 | road of love; romantic path | 情路 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1903 | U+60C5_U+8A71_00 | 情話 | 졩웨5 | feeling; affection; speech; language | 情話 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/情話) | 78628549 |
| 1905 | U+60C5_U+6279_00 | 情批 | 졩풰1 | love letter | 情書 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/情批) | 92639448 |
| 1906 | U+60C5_U+6D77_00 | 情海 | 졩해2 | sea of love | 情海 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1908 | U+60C5_U+4EFD_00 | 情份 | 졩훈5 | feeling; affection | 情份 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1912 | U+505A_U+5175_00 | 做兵 | 조2볭1 | serve as a soldier | 當兵 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/做兵) | 86783496 |
| 1913 | U+9020_U+6210_00 | 造成 | 조솅4 | make; create; become; accomplish | 造成 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/造成) | 92138708 |
| 1914 | U+505A_U+4F19_00 | 做伙 | 조2훼2 | together | 一起 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/做伙) | 83681464 |
| 1919 | U+7D19_U+5B57_00 | 紙字 | 좌1띠5 | written words | 文字 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/紙字) | 84989961 |
| 1922 | U+8F49_U+8F2A_U+8056_U+738B_00 | 轉輪聖王 | 좐1룬솅2엉4 | turn; return; king | 轉輪聖王 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1925 | U+6CC9_U+6F33_00 | 泉漳 | 좐쟝1 | Quanzhou and Zhangzhou; Quanzhang | 泉漳 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1926 | U+6CC9_U+6F33_U+8A71_00 | 泉漳話 | 좐쟝5웨5 | Quanzhou-Zhangzhou speech; Hokkien | 泉漳話 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1929 | U+7D55_U+60C5_00 | 絕情 | 좓졩4 | feeling; affection | 絕情 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/絕情) | 91071683 |
| 1931 | U+7E12_00 | 縒 | 좧1 | difference; error; deviate from the intended form | 偏差; 偏誤 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/縒) | 78662694 |
| 1934 | U+3A7C_00 | 㩼 | 죄5 | many; much | 多 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/㩼) | 89974868 |
| 1937 | U+505A_U+9663_00 | 做陣 | 죄2딘5 | together | 一起 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/做陣) | 78603140 |
| 1939 | U+505A_U+843D_00 | 做落 | 죄2롷1 | do; make; fall; drop | 做下去 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1942 | U+505A_U+4F19_01 | 做伙 | 죄2훼2 | do; make | 一起 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/做伙) | 83681464 |
| 1945 | U+7167_U+93E1_00 | 照鏡 | 죠2걀 | according to; shine | 照鏡 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/照鏡) | 91930997 |
| 1949 | U+77F3_U+982D_00 | 石頭 | 죻ᄐᅷ4 | head | 石頭 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/石頭) | 90522015 |
| 1958 | U+81EA_U+5F37_U+865F_00 | 自強號 | 주경호5 | Tze-Chiang Express | 自強號 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1959 | U+4E3B_U+898B_00 | 主見 | 주1곈 | opinion; independent view | 主見 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/主見) | 78599622 |
| 1960 | U+4E3B_U+5B98_00 | 主官 | 주1괄1 | main; master; official | 主官 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1962 | U+8A3B_U+5B9A_00 | 註定 | 주2댤5 | destined | 注定 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/註定) | 87269658 |
| 1964 | U+8A3B_U+5B9A_01 | 註定 | 주2뎽5 | destined | 注定 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/註定) | 87269658 |
| 1968 | U+73E0_U+6DDA_00 | 珠淚 | 주5뤼5 | pearl | 眼淚 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/珠淚) | 91062795 |
| 1969 | U+6ECB_U+5473_00 | 滋味 | 주5삐5 | flavour | 滋味 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/滋味) | 88668558 |
| 1972 | U+81EA_U+7531_00 | 自由 | 주유4 | self; from; reason | 自由 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/自由) | 92295025 |
| 1973 | U+81EA_U+7531_U+81EA_U+5728_00 | 自由自在 | 주유주재5 | self; from; reason; exist; at | 自由自在 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/自由自在) | 92269012 |
| 1986 | U+9663_U+9663_00 | 陣陣 | 준준5 | waves of; bursts of | 陣陣 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/陣陣) | 60792131 |
| 1992 | U+9189_U+832B_U+832B_00 | 醉茫茫 | 쥐2빵빵4 | very drunk | 醉茫茫 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 1993 | U+6C34_U+6676_00 | 水晶 | 쥐1질1 | water | 水晶 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/水晶) | 92292267 |
| 1995 | U+9152_00 | 酒 | 쥬2 | alcohol; wine | 酒 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/酒) | 92678377 |
| 1997 | U+9152_U+91CF_00 | 酒量 | 쥬1령5 | drinking capacity | 酒量 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/酒量) | 88203607 |
| 2011 | U+8A8C_00 | 誌 | 지 | record; journal | 誌 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/誌) | 90369444 |
| 2012 | U+6307_U+9EDE_00 | 指點 | 지1댬2 | point out; give guidance | 指點 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/指點) | 84188829 |
| 2014 | U+53EA_U+4E0D_U+904E_00 | 只不過 | 지1붇1고 | pass; exceed | 只不過 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/只不過) | 91404112 |
| 2023 | U+9707_U+6771_00 | 震東 | 진2덩1 | Zhen Dong (creator of Tangliengim) | 震東 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2027 | U+771F_U+771F_U+5047_U+5047_00 | 真真假假 | 진5진5게1게2 | truth and falsehood | 真真假假 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/真真假假) | 60788507 |
| 2030 | U+4E00_U+5DE5_00 | 一工 | 짇강1 | one day | 一天 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2031 | U+4E00_U+4E2A_00 | 一个 | 짇고 | one; one item | 一個 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/一个) | 83692126 |
| 2032 | U+4E00_U+500B_U+6708_00 | 一個月 | 짇고2뀋1 | one month | 一個月 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2033 | U+4E00_U+5BE1_00 | 一寡 | 짇과2 | a little; a few | 一點; 一些 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/一寡) | 88436275 |
| 2034 | U+4E00_U+53E5_00 | 一句 | 짇구 | one | 一句 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/一句) | 78597801 |
| 2035 | U+4E00_U+652F_00 | 一支 | 짇기1 | one stick; one item | 一支 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2036 | U+4E00_U+679D_00 | 一枝 | 짇기1 | one branch | 一枝 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/一枝) | 83920239 |
| 2039 | U+4E00_U+689D_00 | 一條 | 짇ᄃᆤ4 | one strip; one long item | 一條 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/一條) | 71650829 |
| 2040 | U+4E00_U+68DF_00 | 一棟 | 짇덩 | classifier for buildings | 一棟 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2041 | U+4E00_U+6BB5_00 | 一段 | 짇돨5 | one | 一段 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/一段) | 89382932 |
| 2042 | U+4E00_U+5F35_00 | 一張 | 짇듈1 | one | 一張 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/一張) | 46377306 |
| 2043 | U+4E00_U+5834_00 | 一場 | 짇듈4 | one; field; place | 一場 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2044 | U+4E00_U+6EF4_00 | 一滴 | 짇딯 | one drop | 一滴 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2048 | U+4E00_U+767E_U+7B8D_00 | 一百箍 | 짇밯1커1 | one hundred dollars | 一百元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2049 | U+4E00_U+64FA_00 | 一擺 | 짇배2 | one | 一次 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/一擺) | 89373107 |
| 2052 | U+4E00_U+672C_00 | 一本 | 짇분2 | one book; one volume | 一本 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/一本) | 92244838 |
| 2053 | U+4E00_U+676F_00 | 一杯 | 짇붸1 | one cup | 一杯 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/一杯) | 92198191 |
| 2055 | U+4E00_U+842C_U+7B8D_00 | 一萬箍 | 짇빤커1 | ten thousand dollars | 一萬元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2056 | U+4E00_U+5E55_00 | 一幕 | 짇뻐5 | a scene | 一幕 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/一幕) | 63133301 |
| 2057 | U+4E00_U+79D2_00 | 一秒 | 짇뾰2 | one second | 一秒 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2058 | U+4E00_U+5C3E_00 | 一尾 | 짇쀄2 | classifier for fish | 一尾 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2061 | U+4E00_U+7D72_00 | 一絲 | 짇시1 | one | 一絲 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/一絲) | 84383909 |
| 2063 | U+4E00_U+4E16_U+4EBA_00 | 一世人 | 짇시2랑4 | a lifetime | 一輩子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/一世人) | 90484643 |
| 2064 | U+4E00_U+6697_00 | 一暗 | 짇암 | one night | 一夜 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2065 | U+9019_U+4E2A_00 | 這个 | 짇1에4 | this | 這個 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2066 | U+4E00_U+4E2A_01 | 一个 | 짇에4 | one; one item | 一個 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/一个) | 83692126 |
| 2067 | U+4E00_U+4E2A_U+4EBA_00 | 一个人 | 짇에랑4 | one person | 一個人 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/一个人) | 46428613 |
| 2068 | U+4E00_U+7AD9_00 | 一站 | 짇잠5 | a station | 一站 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2069 | U+4E00_U+6B09_00 | 一欉 | 짇장4 | one | 一株 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2070 | U+4E00_U+96BB_00 | 一隻 | 짇쟣 | one | 一隻 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2072 | U+9019_U+9663_00 | 這陣 | 짇1준5 | this time; this moment | 現在 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/這陣) | 91975146 |
| 2073 | U+4E00_U+9663_00 | 一陣 | 짇준5 | a while; for a moment | 一陣 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/一陣) | 78597999 |
| 2074 | U+4E00_U+5343_U+7B8D_00 | 一千箍 | 짇촁5커1 | one thousand dollars | 一千元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2075 | U+4E00_U+540B_00 | 一吋 | 짇춘 | one | 一吋 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2076 | U+4E00_U+51FA_00 | 一出 | 짇춛 | one | 一出 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2077 | U+4E00_U+5599_00 | 一喙 | 짇취 | one mouthful | 一口 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2078 | U+4E00_U+7B8D_00 | 一箍 | 짇커1 | one; dollar; ring | 一元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2079 | U+4E00_U+6524_00 | 一攤 | 짇퇄1 | one | 一攤 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2080 | U+4E00_U+5206_00 | 一分 | 짇훈1 | one point; one cent; one minute | 一分 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/一分) | 92198180 |
| 2082 | U+9322_U+9280_00 | 錢銀 | 질꾼4 | money | 錢 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/錢銀) | 84359913 |
| 2083 | U+87F3_00 | 蟳 | 짐4 | crab | 螃蟹 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/蟳) | 92201667 |
| 2088 | U+7092_U+7CBF_U+689D_00 | 炒粿條 | 차1궤1ᄃᆤ4 | fried kway teow | 炒粿條 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/炒粿條) | 87998712 |
| 2091 | U+7092_U+7C73_U+7C89_00 | 炒米粉 | 차1삐1훈2 | fried bee hoon | 炒米粉 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2092 | U+53C9_U+71D2_00 | 叉燒 | 차5슈1 | char siew | 叉燒 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/叉燒) | 92417200 |
| 2099 | U+63D2_U+8349_00 | 插草 | 챃1ᄎᅷ2 | camouflage (military) | 迷彩; 偽裝 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 2103 | U+81ED_U+81ED_00 | 臭臭 | ᄎᅷ2ᄎᅷ | smelly | 臭臭 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/臭臭) | 81397000 |
| 2104 | U+81ED_U+8033_U+807E_00 | 臭耳聾 | ᄎᅷ2힐랑4 | deaf | 耳聾 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/臭耳聾) | 91755485 |
| 2110 | U+83DC_U+982D_U+7CBF_00 | 菜頭粿 | 채2ᄐᅷ궤2 | fried carrot cake | 蘿蔔糕 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/菜頭粿) | 89392446 |
| 2112 | U+8ECA_U+8F26_00 | 車輦 | 챠5롄2 | wheels | 車輪 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/車輦) | 85011354 |
| 2114 | U+8ECA_U+982D_00 | 車頭 | 챠5ᄐᅷ4 | station | 車站 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/車頭) | 91683017 |
| 2118 | U+665F_U+990A_00 | 晟養 | 챨영2 | raise; bring up | 養大 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 2120 | U+7C64_U+8A69_00 | 籤詩 | 챰5시1 | divination poem | 籤詩 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/籤詩) | 89875868 |
| 2121 | U+64A8_00 | 撨 | ᄎᆤ4 | adjust; arrange | 調整; 安排 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/撨) | 91442892 |
| 2122 | U+6084_U+6084_00 | 悄悄 | ᄎᆤ5ᄎᆤ1 | quietly | 悄悄 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/悄悄) | 92281395 |
| 2126 | U+7C97_U+9B6F_00 | 粗魯 | 처5러2 | unruly | 粗魯 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/粗魯) | 85134988 |
| 2128 | U+521D_U+6B65_00 | 初步 | 처5버5 | step | 初步 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/初步) | 77762094 |
| 2130 | U+5275_U+6CBB_00 | 創治 | 청2디5 | bully; tease; play tricks on | 捉弄; 欺負 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/創治) | 91087548 |
| 2131 | U+6EC4_U+6851_00 | 滄桑 | 청5성1 | dark blue; vast; mulberry | 滄桑 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/滄桑) | 92218216 |
| 2132 | U+5275_U+7A7A_00 | 創空 | 청2캉1 | make a hole; open a wound | 打洞 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/創空) | 88657287 |
| 2138 | U+9752_U+888D_00 | 青袍 | 첼5ᄑᅷ | a green/blue Chinese long shirt | 青袍 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/青袍) | 78687189 |
| 2139 | U+751F_U+4EFD_00 | 生份 | 첼5훈5 | estranged | 疏遠 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/生份) | 84548375 |
| 2146 | U+5343_U+767E_00 | 千百 | 쳰5밯 | hundreds and thousands | 千百 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/千百) | 74153700 |
| 2147 | U+5343_U+5C71_U+842C_U+6C34_00 | 千山萬水 | 쳰5산5빤쉬2 | long journey; countless mountains and rivers | 千山萬水 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/千山萬水) | 92707655 |
| 2148 | U+5343_U+5343_U+842C_U+842C_00 | 千千萬萬 | 쳰5쳰5빤빤5 | thousand; ten thousand | 千千萬萬 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/千千萬萬) | 60797392 |
| 2149 | U+5343_U+932F_U+842C_U+932F_00 | 千錯萬錯 | 쳰5초2빤초 | entirely wrong; full of mistakes | 千錯萬錯 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2150 | U+6DFA_U+62D6_00 | 淺拖 | 쳰1톼1 | slippers | 拖鞋 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/淺拖) | 91961378 |
| 2156 | U+5343_U+5E74_00 | 千年 | 촁5니4 | thousand years | 千年 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/千年) | 92198810 |
| 2162 | U+5343_U+7B8D_00 | 千箍 | 촁5커1 | thousand; dollar; ring | 千元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2163 | U+6E05_U+6C23_00 | 清氣 | 촁5키 | clean | 乾淨 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/清氣) | 92083001 |
| 2164 | U+6E05_U+82B3_00 | 清芳 | 촁5팡1 | fragrant | 清香 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/清芳) | 78646187 |
| 2165 | U+6E05_U+98A8_00 | 清風 | 촁5헝1 | clear wind | 清風 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/清風) | 78646244 |
| 2171 | U+521D_01 | 初 | 최1 | prefix for days 1 to 10 of a Chinese calendar month | 初 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/初) | 92199988 |
| 2172 | U+521D_U+4E00_00 | 初一 | 최5읻 | day 1 of a Chinese calendar month | 初一 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/初一) | 87996570 |
| 2175 | U+7B11_U+6587_U+6587_00 | 笑文文 | 쵸2뿐뿐4 | smile gently | 微笑 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2177 | U+7B11_U+8A7C_00 | 笑詼 | 쵸2퀘1 | laugh; smile; joke; humorous | 笑話 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/笑詼) | 87461294 |
| 2183 | U+8DA3_U+5473_00 | 趣味 | 추2삐5 | interesting; fun | 趣味 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/趣味) | 92248557 |
| 2185 | U+8CF0_00 | 賰 | 춘1 | left over; surplus | 剩 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/賰) | 84383524 |
| 2189 | U+6625_U+98A8_00 | 春風 | 춘5헝1 | wind | 春風 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/春風) | 93038556 |
| 2191 | U+51FA_U+5AC1_00 | 出嫁 | 춛1게 | marry out | 出嫁 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/出嫁) | 92759608 |
| 2192 | U+51FA_U+696D_00 | 出業 | 춛1꺕1 | graduate | 畢業 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/出業) | 92049093 |
| 2193 | U+51FA_U+65E5_00 | 出日 | 춛1띧1 | sunrise | 日出 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2195 | U+51FA_U+9580_00 | 出門 | 춛1믕4 | door | 出門 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/出門) | 92760292 |
| 2198 | U+51FA_U+53E3_00 | 出口 | 춛1ᄏᅷ2 | mouth | 出口 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/出口) | 92297230 |
| 2199 | U+51FA_U+982D_U+5929_00 | 出頭天 | 춛1ᄐᅷ틸1 | one's breakthrough | 出頭天 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/出頭天) | 92092167 |
| 2202 | U+63E3_00 | 揣 | 췌5 | look for; guess | 找; 猜 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/揣) | 87581913 |
| 2205 | U+5599_U+7126_00 | 喙焦 | 취2다1 | thirsty; dry-mouthed | 口渴 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/喙焦) | 80919507 |
| 2206 | U+5599_U+8123_00 | 喙脣 | 취2둔4 | mouth; beak; lip | 嘴唇 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/喙脣) | 81047906 |
| 2207 | U+5599_U+908A_00 | 喙邊 | 취2빌1 | side | 嘴邊 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/喙邊) | 87261085 |
| 2208 | U+5599_U+820C_00 | 喙舌 | 취2짛1 | tongue | 舌頭 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/喙舌) | 92112967 |
| 2214 | U+6A39_U+9802_00 | 樹頂 | 츄뎽2 | treetop | 樹頂 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/樹頂) | 89551824 |
| 2215 | U+624B_U+5167_00 | 手內 | 츄1래5 | in hand; at hand | 手內 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2218 | U+6A39_U+7BAC_00 | 樹箬 | 츄훃1 | tree; bamboo leaf | 樹葉 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/樹箬) | 90783208 |
| 2221 | U+5531_U+6B4C_00 | 唱歌 | 츌2과1 | sing song | 唱歌 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/唱歌) | 92135547 |
| 2229 | U+5E02_U+9577_00 | 市長 | 치뎔2 | city mayor | 市長 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/市長) | 89886473 |
| 2230 | U+5E02_U+9577_01 | 市長 | 치듈2 | city mayor | 市長 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/市長) | 89886473 |
| 2233 | U+60BD_U+6158_00 | 悽慘 | 치5참2 | sad; miserable; tragic | 悽慘 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/悽慘) | 84869254 |
| 2234 | U+8A66_U+770B_U+8993_00 | 試看覓 | 치2콸2매5 | look; watch | 試試看 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2236 | U+89AA_U+611B_00 | 親愛 | 친5애 | relative; close; love; want | 親愛 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/親愛) | 92238499 |
| 2240 | U+51CA_U+5F69_00 | 凊彩 | 친2채2 | any; whichever; casual; careless | 隨便 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/凊彩) | 89443767 |
| 2241 | U+89AA_U+50CF_00 | 親像 | 친5츌5 | like; resemble | 像 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/親像) | 88398260 |
| 2244 | U+62ED_U+6C57_00 | 拭汗 | 칟1괄5 | sweat | 拭汗 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2245 | U+4E03_U+767E_00 | 七百 | 칟1밯 | seven hundred | 七百 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/七百) | 89842802 |
| 2246 | U+59FC_U+4ED4_00 | 姼仔 | 칟1아2 | girlfriend (colloquial) | 馬子 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/姼仔) | 78618755 |
| 2249 | U+4E03_U+5206_00 | 七分 | 칟1훈1 | seven parts; seventy percent | 七分 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2252 | U+9192_U+2019_U+B798_00 | 醒’래 | 칠2’래 | wake up | 醒來 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2259 | U+8DE4_U+8E0F_U+5BE6_U+5730_00 | 跤踏實地 | 카5닿싣데5 | to be realistic and reliable | 腳踏實地 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/跤踏實地) | 91503304 |
| 2261 | U+6572_U+96FB_U+8A71_00 | 敲電話 | 카2뎬웨5 | electricity; speech; language | 打電話 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/敲電話) | 93318616 |
| 2264 | U+5C3B_U+5DDD_00 | 尻川 | 카5층1 | buttocks | 屁股 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/尻川) | 92728269 |
| 2270 | U+5D01_00 | 崁 | 캄 | cliff; ridge | 崁 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/崁) | 87576054 |
| 2271 | U+574E_U+574E_U+523B_U+523B_00 | 坎坎刻刻 | 캄1캄1켹1켹 | pit; uneven; carve; moment | 坎坷 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2272 | U+574E_U+574E_U+5777_U+5777_00 | 坎坎坷坷 | 캄1캄1켿켿1 | pit; uneven; rough | 坎坎坷坷 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2273 | U+574E_U+6B39_00 | 坎欹 | 캄1캬1 | pit; uneven; tilted; leaning | 傾斜; 不平 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2276 | U+7A7A_U+5599_U+8584_U+820C_00 | 空喙薄舌 | 캉5취2봏짛1 | sharp-tongued; talkative | 尖嘴薄舌; 多嘴 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2281 | U+54ED_U+7238_00 | 哭爸 | ᄏᅷ2베5 | cry father; whine | 抱怨 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/哭爸) | 92696805 |
| 2282 | U+54ED_U+7238_U+54ED_U+6BCD_00 | 哭爸哭母 | ᄏᅷ2베ᄏᅷ2뿌2 | whine; complain | 抱怨 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/哭爸哭母) | 85098460 |
| 2284 | U+958B_U+59CB_00 | 開始 | 캐5시2 | open | 開始 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/開始) | 92135388 |
| 2290 | U+7B8D_00 | 箍 | 커1 | dollar | 元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/箍) | 92201298 |
| 2295 | U+82E6_U+8877_00 | 苦衷 | 커1졍1 | bitter; suffering; inner feeling | 苦衷 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/苦衷) | 80730764 |
| 2298 | U+60BE_00 | 悾 | 컹1 | foolish; empty-headed | 傻 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/悾) | 87579099 |
| 2302 | U+6050_U+9A5A_00 | 恐驚 | 켱1걀1 | scared | 害怕 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/恐驚) | 89612249 |
| 2304 | U+514B_U+8667_00 | 克虧 | 켹1퀴1 | overcome; restrain; loss; owe | 吃虧 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/克虧) | 78532238 |
| 2305 | U+82A1_U+82B3_00 | 芡芳 | 켼2팡1 | fry aromatics to release their fragrance | 爆香 | MOE defines frying aromatics to release fragrance (爆香), not starch thickening (勾芡). | [Wiktionary](https://pedia.cloud.edu.tw/Entry/Detail/?search=芡芳&title=芡芳) |  |
| 2311 | U+53EF_U+6BD4_00 | 可比 | 코1비2 | compare | 可比 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/可比) | 90796111 |
| 2315 | U+9760_U+7AD9_00 | 靠站 | 코2잠5 | arrive at a stop; pull into a station | 靠站 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2316 | U+9760_U+5CB8_00 | 靠岸 | 코2활5 | come ashore; dock | 靠岸 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/靠岸) | 87391305 |
| 2322 | U+770B_U+8993_00 | 看覓 | 콸2매5 | look; watch | 看看 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/看覓) | 91760681 |
| 2329 | U+774F_00 | 睏 | 쿤 | sleep | 睡覺 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/睏) | 91978916 |
| 2331 | U+774F_U+2019_U+D088_00 | 睏’킈 | 쿤’킈 | fall asleep | 睡著 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2336 | U+958B_U+5F80_00 | 開往 | 퀴5엉2 | depart for; bound for | 開往 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2338 | U+958B_U+5599_00 | 開喙 | 퀴5취 | open | 開口 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/開喙) | 84378880 |
| 2341 | U+56E5_00 | 囥 | 킁 | hide; store away | 藏; 收起 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/囥) | 92765541 |
| 2345 | U+8D77_U+884C_00 | 起行 | 키1걀4 | to go; to begin a journey | 起行 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/起行) | 83479767 |
| 2347 | U+8D77_U+75DF_00 | 起痟 | 키1ᄉᆤ2 | to be crazy | 發瘋 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/起痟) | 83483247 |
| 2349 | U+6C23_U+8EAB_U+60F1_U+547D_00 | 氣身惱命 | 키2신5로1먀5 | furious; extremely angry | 氣憤; 怒不可遏 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://sutian.moe.edu.tw/zh-hant/su/6171/) |  |
| 2352 | U+8F15_U+8072_00 | 輕聲 | 킨5샬1 | soft; low in volume | 輕聲 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/輕聲) | 87996794 |
| 2353 | U+52E4_U+5109_00 | 勤儉 | 킨캼5 | diligent; frugal; economical | 勤儉 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/勤儉) | 87383702 |
| 2354 | U+8F15_U+53EF_00 | 輕可 | 킨5코2 | alright | 還好 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/輕可) | 78961270 |
| 2355 | U+8F15_U+8F15_00 | 輕輕 | 킨5킨1 | light; easy | 輕輕 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/輕輕) | 91640565 |
| 2358 | U+4ED6_U+9109_00 | 他鄉 | 타5형1 | he; other; hometown; countryside | 他鄉 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/他鄉) | 80125609 |
| 2361 | U+8B80_U+518A_00 | 讀冊 | 탁쳏 | read book; study | 讀書 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/讀冊) | 91350476 |
| 2363 | U+5766_U+767D_00 | 坦白 | 탄1벻1 | white | 坦白 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/坦白) | 91082051 |
| 2364 | U+63A2_U+807D_00 | 探聽 | 탐2턀1 | listen; hear | 探聽 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/探聽) | 80778516 |
| 2369 | U+7A97_U+4ED4_00 | 窗仔 | 탕아2 | diminutive suffix | 窗戶 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/窗仔) | 91716708 |
| 2375 | U+5077_U+62C8_00 | 偷拈 | ᄐᅷ5니1 | steal; pilfer | 偷 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2376 | U+982D_U+8DEF_00 | 頭路 | ᄐᅷ러5 | job; work | 工作 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/頭路) | 91978882 |
| 2377 | U+982D_U+6BDB_00 | 頭毛 | ᄐᅷ믕4 | hair | 頭髮 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/頭毛) | 91405775 |
| 2378 | U+982D_U+524D_00 | 頭前 | ᄐᅷ졩4 | in front; ahead | 前面 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/頭前) | 87326106 |
| 2379 | U+982D_U+5599_00 | 頭喙 | ᄐᅷ취 | headcount | 人頭 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/頭喙) | 85576299 |
| 2381 | U+5077_U+807D_00 | 偷聽 | ᄐᅷ5턀1 | eavedrop | 偷聽 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/偷聽) | 89137039 |
| 2389 | U+807D_U+8B1B_00 | 聽講 | 턀5겅2 | hearsay | 聽講 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/聽講) | 82346777 |
| 2391 | U+807D_U+4EBA_U+8B1B_00 | 聽人講 | 턀5랑겅2 | hearsay | 聽人講 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2392 | U+807D_U+4EBA_U+5531_00 | 聽人唱 | 턀5랑츌 | listen to people sing | 聽人唱 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2394 | U+75BC_U+5FC3_00 | 疼心 | 턀2심1 | heartache | 心痛 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/疼心) | 78653606 |
| 2398 | U+6311_U+5DE5_00 | 挑工 | ᄐᆤ5강1 | specially; deliberately; on purpose | 專門; 特意 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://zh.wiktionary.org/zh-hant/刁工) |  |
| 2399 | U+8DF3_U+2019_U+B877_U+D088_00 | 跳’롷킈 | ᄐᆤ’롷킈 | jump down | 跳下去 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2402 | U+5410_U+6C99_00 | 吐沙 | 터2솨1 | purge sand | 吐沙 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2403 | U+5857_U+8DE4_00 | 塗跤 | 터카1 | earth; smear; foot | 地上 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/塗跤) | 91749522 |
| 2408 | U+9AD4_U+8AD2_00 | 體諒 | 테1령5 | body; form; forgive; understand | 體諒 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/體諒) | 85424287 |
| 2410 | U+9000_U+4E0B_00 | 退下 | 테2하5 | below; under | 退下 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/退下) | 44600869 |
| 2411 | U+9AD4_U+6703_00 | 體會 | 테1훼5 | can; meeting | 體會 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/體會) | 78690697 |
| 2415 | U+985B_U+8E31_00 | 顛踱 | 톈5톻1 | to mess around | 吊兒郎當; 不正經 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/顛踱) | 79087528 |
| 2416 | U+5929_U+4EFD_00 | 天份 | 톈5훈5 | sky; day | 天份 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/天份) | 51377094 |
| 2418 | U+4EAD_U+4ED4_U+8DE4_00 | 亭仔跤 | 톙아1카1 | diminutive suffix | 騎樓 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/亭仔跤) | 87971043 |
| 2422 | U+62D6_U+4ED4_00 | 拖仔 | 톼5아2 | slippers | 拖鞋 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/拖仔) | 82317699 |
| 2429 | U+69CC_U+69CC_00 | 槌槌 | 튀튀4 | stupid; foolish | 笨笨 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/槌槌) | 78467739 |
| 2433 | U+7CD6_U+7518_U+871C_U+751C_00 | 糖甘蜜甜 | 틍감5삗딜1 | sweet as sugar and honey | 甜如蜜 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2438 | U+5929_U+9802_00 | 天頂 | 틸5뎽2 | sky; above | 天空 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/天頂) | 91976248 |
| 2441 | U+5929_U+6416_U+5730_U+52D5_00 | 天搖地動 | 틸5요데당5 | sky; day; earth; place | 天搖地動 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2442 | U+5929_U+661F_00 | 天星 | 틸5칠1 | stars | 星星 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/天星) | 91819639 |
| 2444 | U+725A_U+817F_00 | 牚腿 | 틸2튀2 | have stiff, sore legs (from exertion) | 腿痠; 腿僵硬 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/牚腿) | 84397707 |
| 2446 | U+9435_U+6AE5_00 | 鐵櫥 | 팋1두4 | metal cabinet | 鐵櫃 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2448 | U+62CB_U+62CB_U+8D70_00 | 拋拋走 | 파5파5ᄌᅷ2 | run; leave | 到處跑 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/拋拋走) | 86695055 |
| 2450 | U+66DD_U+65E5_00 | 曝日 | 팍띧1 | sunbathe; expose to the sun | 曝日 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/曝日) | 83917821 |
| 2454 | U+82B3_U+5473_00 | 芳味 | 팡5삐5 | fragrance; flavor | 香味 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/芳味) | 90910934 |
| 2456 | U+62CD_U+62DA_00 | 拍拚 | 팧1뱔 | strive; work hard | 努力 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/拍拚) | 84385530 |
| 2457 | U+62CD_U+7B97_00 | 拍算 | 팧1승 | plan; calculate | 打算 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/拍算) | 81492125 |
| 2458 | U+62CD_U+62DB_U+547C_00 | 拍招呼 | 팧1죠5허1 | hit; beat | 打招呼 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/拍招呼) | 78465737 |
| 2459 | U+62CD_U+958B_00 | 拍開 | 팧1퀴1 | to open | 拍開 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2465 | U+6B79_U+884C_00 | 歹行 | 팰1걀4 | bad; walk; go | 難走 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2466 | U+6B79_U+904E_00 | 歹過 | 팰1궤 | bad; pass; exceed | 難過 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2472 | U+98C4_U+6D6A_00 | 飄浪 | ᄑᆤ5렁5 | wander; drift | 飄浪 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2474 | U+98C4_U+6487_00 | 飄撇 | ᄑᆤ5폗 | stylish; charming; carefree | 瀟灑 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/飄撇) | 90351008 |
| 2479 | U+535A_U+7269_U+9928_00 | 博物館 | 퍽1뿓관2 | thing; hall; shop; institution | 博物館 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/博物館) | 92386974 |
| 2481 | U+81A8_U+98A8_00 | 膨風 | 펑2헝1 | feel bloated; brag | 腹脹; 吹牛 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/膨風) | 82388054 |
| 2482 | U+78A7_U+5C71_00 | 碧山 | 폑1산1 | mountain | 碧山 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/碧山) | 87992388 |
| 2484 | U+9A19_U+4EBA_00 | 騙人 | 폔2랑4 | deceive people | 騙人 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/騙人) | 85013035 |
| 2486 | U+504F_U+504F_00 | 偏偏 | 폔5폔1 | partial; one-sided | 偏偏 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/偏偏) | 89222538 |
| 2488 | U+6487_U+6B65_00 | 撇步 | 폗1버5 | step | 訣竅 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/撇步) | 84392693 |
| 2491 | U+6CE2_U+6D6A_00 | 波浪 | 포5렁5 | waves | 波浪 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/波浪) | 92234990 |
| 2492 | U+6CE2_U+7D0B_00 | 波紋 | 포5뿐4 | wave; pattern; line | 波紋 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/波紋) | 92254236 |
| 2494 | U+7834_U+8179_00 | 破腹 | 퐈2박 | rip open abdomen; to speak from one's heart | 剖腹; 說心裡話 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/破腹) | 78467127 |
| 2495 | U+7834_U+75C5_00 | 破病 | 퐈2벨5 | illness | 生病 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/破病) | 86651552 |
| 2496 | U+7834_U+75C5_01 | 破病 | 퐈2빌5 | illness | 生病 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/破病) | 86651552 |
| 2505 | U+88AB_U+55AE_00 | 被單 | 풰돨1 | single; alone | 被單 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/被單) | 84548644 |
| 2509 | U+54C1_00 | 品 | 핀2 | goods; quality | 品 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/品) | 92200133 |
| 2513 | U+9F3B_U+7A7A_00 | 鼻空 | 필캉1 | nostril | 鼻孔 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/鼻空) | 84561869 |
| 2514 | U+4E0B_U+8AB2_00 | 下課 | 하코 | after class | 下課 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/下課) | 84040401 |
| 2524 | U+8B40_00 | 譀 | 함 | boast; exaggerate | 吹牛; 誇大 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/譀) | 87572452 |
| 2525 | U+548C_00 | 和 | 함5 | and; with; harmony | 和 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/和) | 93364375 |
| 2526 | U+8B40_U+53EB_00 | 譀叫 | 함2교 | shout; call | 叫喊 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 2527 | U+86B6_U+4ED4_00 | 蚶仔 | 함5아2 | diminutive suffix | 蚶 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/蚶仔) | 90458024 |
| 2530 | U+80A8_U+5976_00 | 肨奶 | 항2롕1 | plump (of a baby) | 胖乎乎 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/肨奶) | 79172190 |
| 2533 | U+5F8C_U+751F_00 | 後生 | ᄒᅷ셀1 | son | 兒子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/後生) | 89914150 |
| 2534 | U+5F8C_U+751F_01 | 後生 | ᄒᅷ실1 | son | 兒子 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/後生) | 89914150 |
| 2538 | U+6D77_U+89D2_00 | 海角 | 해1각 | sea | 海角 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/海角) | 92262198 |
| 2540 | U+6D77_U+6E67_00 | 海湧 | 해1옝2 | sea wave | 海浪 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/海湧) | 88381739 |
| 2542 | U+6D77_U+6D77_00 | 海海 | 해1해2 | nothing out of the ordinary | 平常 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/海海) | 84392962 |
| 2544 | U+6D77_U+5CB8_00 | 海岸 | 해1활5 | sea coast | 海岸 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/海岸) | 92161879 |
| 2547 | U+5144_U+5F1F_U+59CA_U+59B9_00 | 兄弟姊妹 | 햘5디지1뭬5 | siblings | 兄弟姊妹 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/兄弟姊妹) | 82701550 |
| 2548 | U+5144_U+5F1F_U+59CA_U+59B9_01 | 兄弟姊妹 | 햘5디지1뻬5 | siblings | 兄弟姊妹 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/兄弟姊妹) | 82701550 |
| 2549 | U+859F_00 | 薟 | 햠1 | spicy | 辣 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/薟) | 87977972 |
| 2551 | U+859F_U+6912_00 | 薟椒 | 햠5죠1 | chilli | 辣椒 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/薟椒) | 78670666 |
| 2553 | U+97FF_U+8D77_00 | 響起 | 향1키2 | start (of a sound or music) | 響起 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2554 | U+9050_00 | 遐 | 햫 | that much; so | 那麼 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/遐) | 91716173 |
| 2555 | U+9050_U+9087_00 | 遐邇 | 햫1니5 | that much; to that extent | 那麼 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/遐邇) | 74015803 |
| 2557 | U+56C2_U+4FF3_00 | 囂俳 | ᄒᆤ5배1 | arrogant | 傲慢 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/囂俳) | 90826661 |
| 2569 | U+798F_U+5EFA_U+9EB5_00 | 福建麵 | 헉1곈2미5 | Hokkien mee | 福建麵 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/福建麵) | 91955050 |
| 2570 | U+798F_U+5EFA_U+8A71_00 | 福建話 | 헉1곈2웨5 | Hokkien speech | 福建話 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/福建話) | 92286533 |
| 2575 | U+653E_U+8569_00 | 放蕩 | 헝2덩5 | put; release | 放蕩 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/放蕩) | 86458089 |
| 2577 | U+98A8_U+4E2D_00 | 風中 | 헝5뎡1 | in the wind | 風中 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2580 | U+98A8_U+6E67_00 | 風湧 | 헝5옝2 | wind and wave | 風浪 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/風湧) | 88382007 |
| 2583 | U+98A8_U+98B1_00 | 風颱 | 헝5태1 | wind | 颱風 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/風颱) | 92481406 |
| 2585 | U+98A8_U+98A8_U+96E8_U+96E8_00 | 風風雨雨 | 헝5헝5우1우2 | wind and rain | 風風雨雨 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/風風雨雨) | 60794514 |
| 2589 | U+90C1_00 | 郁 | 혁 | luxuriant; anxious | 郁 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/郁) | 87979696 |
| 2592 | U+5411_U+524D_U+884C_00 | 向前行 | 형2졘걀4 | to strive; to move forward | 向前行 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2593 | U+96C4_U+96C4_00 | 雄雄 | 형형4 | suddenly | 突然 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/雄雄) | 78536889 |
| 2595 | U+73FE_U+4EE3_00 | 現代 | 혠대 | present era | 現代 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/現代) | 92475817 |
| 2596 | U+73FE_U+8EAB_00 | 現身 | 혠신1 | body | 現身 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/現身) | 63032605 |
| 2606 | U+80F8_U+574E_00 | 胸坎 | 혱5캄2 | chest; pit; uneven | 胸口 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/胸坎) | 91353487 |
| 2610 | U+548C_01 | 和 | 호4 | harmony | 和 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/和) | 93364375 |
| 2614 | U+597D_U+984D_00 | 好額 | 호1꺟1 | rich | 有錢 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/好額) | 78618361 |
| 2615 | U+597D_U+8336_00 | 好茶 | 호1데4 | good tea | 好茶 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2616 | U+597D_U+547D_00 | 好命 | 호1먀5 | good life | 好命 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/好命) | 85744940 |
| 2617 | U+4F55_U+5FC5_00 | 何必 | 호빋 | why must it be | 何必 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/何必) | 91785798 |
| 2619 | U+597D_U+52E2_00 | 好勢 | 호1세 | good | 好 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/好勢) | 83043494 |
| 2623 | U+597D_U+6C34_00 | 好水 | 호1쥐2 | good water | 好水 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 2624 | U+597D_U+8ECA_00 | 好車 | 호1챠1 | good car | 好車 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2628 | U+597D_U+6F22_00 | 好漢 | 호1한 | good man | 好漢 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/好漢) | 87267123 |
| 2632 | U+82B1_U+5BB9_U+6708_U+8C8C_00 | 花容月貌 | 화5영꽏ᄆᅷ5 | moon; month | 花容月貌 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/花容月貌) | 90968721 |
| 2635 | U+7169_00 | 煩 | 환4 | annoyed; troublesome | 煩 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/煩) | 92917787 |
| 2641 | U+53CD_U+80CC_00 | 反背 | 환1붸5 | betray; go against | 反叛 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. | [Wiktionary](https://en.wiktionary.org/wiki/反背) | 81031455 |
| 2642 | U+51E1_U+52E2_00 | 凡勢 | 환세 | ordinary; all; force; situation | 也許 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/凡勢) | 73631538 |
| 2646 | U+7E41_U+82B1_00 | 繁花 | 환훼1 | blooming flowers | 繁花 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/繁花) | 91593271 |
| 2651 | U+6CD5_U+5BF6_00 | 法寶 | 홛1보2 | treasured method; magic weapon | 法寶 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/法寶) | 84066649 |
| 2653 | U+767C_U+73FE_00 | 發現 | 홛1혠5 | send out; develop; present; appear | 發現 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/發現) | 84962250 |
| 2657 | U+634D_U+8ECA_00 | 捍車 | 활챠1 | vehicle | 攔車 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/捍車) | 86844285 |
| 2658 | U+6B61_U+6B61_U+559C_U+559C_00 | 歡歡喜喜 | 활5활5히1히2 | happily; cheerfully | 歡歡喜喜 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2661 | U+6A6B_U+76F4_00 | 橫直 | 홸딛1 | straight | 反正 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/橫直) | 91760014 |
| 2663 | U+5F8C_U+6094_00 | 後悔 | 효훼2 | after; behind | 後悔 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/後悔) | 92135295 |
| 2664 | U+6B47_U+774F_00 | 歇睏 | 훃1쿤 | to rest | 休息 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/歇睏) | 91978907 |
| 2665 | U+70CC_00 | 烌 | 후1 | dust; ash | 灰塵; 灰燼 | Corrected the whole-word sense; removed unrelated component-character meanings. The corrected meaning makes the Mandarin equivalent clear. | [Wiktionary](https://en.wiktionary.org/wiki/烌) | 87591722 |
| 2667 | U+99D9_U+99AC_00 | 駙馬 | 후마2 | horse | 駙馬 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/駙馬) | 82264656 |
| 2668 | U+8CA0_U+8CAC_U+4EFB_00 | 負責任 | 후졕1띰5 | carry; betray; responsibility; blame; duty | 負責任 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/負責任) | 82102325 |
| 2670 | U+85B0_00 | 薰 | 훈1 | fragrant; smoke | 香; 煙 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/薰) | 92065153 |
| 2679 | U+7C89_U+7CBF_00 | 粉粿 | 훈1궤2 | flour; powder; rice cake | 粉粿 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/粉粿) | 84919125 |
| 2681 | U+96F2_U+4E2D_00 | 雲中 | 훈뎡1 | in the clouds | 雲中 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2685 | U+72E0_U+5FC3_00 | 狠心 | 훈심1 | ruthless | 狠心 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/狠心) | 78650751 |
| 2687 | U+96F2_U+904A_U+56DB_U+6D77_00 | 雲遊四海 | 훈유수2해2 | sail the seven seas | 雲遊四海 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2697 | U+706B_U+8457_00 | 火著 | 훼1돟1 | on fire | 著火 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2698 | U+56DE_U+79AE_00 | 回禮 | 훼레2 | return a courtesy | 回禮 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/回禮) | 90824052 |
| 2701 | U+706B_U+738B_U+723A_00 | 火王爺 | 훼1엉야4 | Fire King (deity) | 火王爺 | User-reviewed lexical sense; whole-word gloss checked and Simplified metadata derived with pinned OpenCC. |  |  |
| 2702 | U+82B1_U+96E8_00 | 花雨 | 훼5우2 | rain | 花雨 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2704 | U+6B72_U+982D_00 | 歲頭 | 훼2ᄐᅷ4 | head | 年初 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/歲頭) | 91687139 |
| 2706 | U+56DE_U+822A_00 | 回航 | 훼항4 | return | 回航 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2720 | U+7A00_U+5FAE_00 | 稀微 | 히5삐4 | rare; thin; slight; subtle | 孤寂 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/稀微) | 86700530 |
| 2723 | U+5F7C_U+4E2A_00 | 彼个 | 힏1에4 | that | 那個 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/彼个) | 48945795 |
| 2725 | U+8033_U+7A7A_00 | 耳空 | 힐캉1 | ear | 耳孔 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/耳空) | 84543606 |
| 2726 | U+7FD5_00 | 翕 | 힙 | close; gather | 翕 | Reviewed shared Mandarin lexical expression; compatible relevant sense. Component-only secondary English glosses do not require all-sense identity. | [Wiktionary](https://en.wiktionary.org/wiki/翕) | 92682396 |
| 2730 | U+4E8C_U+5341_U+7B8D_01 | 二十箍 | 능잡커1* | twenty dollars | 二十元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2731 | U+5169_U+5343_U+7B8D_01 | 兩千箍 | 능쳰5커1* | two thousand dollars | 兩千元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2732 | U+660E_U+4ED4_U+8F09_01 | 明仔載 | 먀4재* | bright; clear; diminutive suffix | 明天 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/明仔載) | 89936657 |
| 2734 | U+4E00_U+5343_U+7B8D_01 | 一千箍 | 짇쳰5커1* | one thousand dollars | 一千元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2735 | U+5343_U+7B8D_01 | 千箍 | 쳰5커1* | thousand; dollar; ring | 千元 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. Reference coverage unavailable; correspondence is clear from lexical context. |  |  |
| 2737 | U+8CA7_U+60F0_01 | 貧惰 | 핀돨5* | poor; lazy | 懶惰 | Reviewed whole-word Hokkien meaning; natural Mandarin equivalent differs from the source form. | [Wiktionary](https://en.wiktionary.org/wiki/貧惰) | 91701340 |

## Manual review - LOW confidence only

13 entries.

| line | entry_id | hanri | reading | english | mandarin_trad | reason | source | revision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 14 | U+B38B_00 | 뎋 | 뎋 |  |  | Need a usage example identifying the aspect/continuation function; no gloss guessed. |  |  |
| 15 | U+2019_U+B434_00 | ’됴 | ’됴 |  |  | Need a usage example identifying this attached grammatical form. |  |  |
| 16 | U+2019_U+B44F_00 | ’둏 | ’둏 |  |  | Need a usage example identifying this attached grammatical form. |  |  |
| 19 | U+2019_U+B798_00 | ’래 | ’래 |  |  | Need a usage example distinguishing attached directional/aspectual use. |  |  |
| 57 | U+2019_U+D088_00 | ’킈 | ’킈 |  |  | Need a usage example distinguishing attached directional/aspectual use. |  |  |
| 224 | U+632D_00 | 挭 | 곙5 | block; choke |  | Reading 곙5 may involve supporting/propping or obstruction. Please give a sentence; block/choke alone is not enough. | [Wiktionary](https://en.wiktionary.org/wiki/挭) | 92200565 |
| 363 | U+7344_U+57CE_00 | 獄城 | 꼑샬4 | prison; hell; city; wall |  | Please identify prison, an infernal city, or a specific religious name; component glosses do not establish the referent. |  |  |
| 420 | U+5169_U+89D2_00 | 兩角 | 능각 | two; both |  | Please clarify currency (two jiao), two corners, or another sense; two/both does not settle this. |  |  |
| 707 | U+4EBA_U+9858_00 | 人願 | 띤꽌5 | person; people |  | Your Mandarin ditto is retained, but the whole-word English meaning is still unspecified. Please explain 人願. |  |  |
| 939 | U+5317_U+9670_U+9146_U+90FD_00 | 北陰酆都 | 박1임5헝5더1 | north; yin; cloudy; hidden; all |  | Your Mandarin ditto is retained. Please clarify whether this denotes a place or an abbreviated deity/title. |  |  |
| 1182 | U+7C73_U+7C89_U+7CBF_00 | 米粉粿 | 삐1훈1궤2 | bee hoon kueh |  | Please clarify whether bee hoon kueh is a rice-flour cake/noodle dish or mee hoon kueh (wheat-flour noodle soup). Do not change the headword without confirmation. |  |  |
| 1318 | U+87EE_00 | 蟮 | 셴5 |  |  | User clarified: 蟮 has no standalone lexical meaning; gecko belongs to 蟮蟲. Decide whether to retain a bound component or add/change to the full headword before assigning semantic glosses. Not merged as gecko. | [Wiktionary](https://en.wiktionary.org/wiki/蟮) | 84323641 |
| 1494 | U+5FC3_U+72C2_00 | 心狂 | 심5겅4 | mind losing |  | Your Mandarin ditto is retained. Please distinguish panic/agitation, mental derangement, or another intended sense. |  |  |

## Not applicable

10 entries.

| line | entry_id | hanri | reading | english | mandarin_trad | reason | source | revision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2738 | U+0030_00 | 0 | 0 |  |  | Input-only numeral pronunciation; not a lexical Mandarin translation. |  |  |
| 2739 | U+0031_00 | 1 | 1 |  |  | Input-only numeral pronunciation; not a lexical Mandarin translation. |  |  |
| 2740 | U+0032_00 | 2 | 2 |  |  | Input-only numeral pronunciation; not a lexical Mandarin translation. |  |  |
| 2741 | U+0033_00 | 3 | 3 |  |  | Input-only numeral pronunciation; not a lexical Mandarin translation. |  |  |
| 2742 | U+0034_00 | 4 | 4 |  |  | Input-only numeral pronunciation; not a lexical Mandarin translation. |  |  |
| 2743 | U+0035_00 | 5 | 5 |  |  | Input-only numeral pronunciation; not a lexical Mandarin translation. |  |  |
| 2744 | U+0036_00 | 6 | 6 |  |  | Input-only numeral pronunciation; not a lexical Mandarin translation. |  |  |
| 2745 | U+0037_00 | 7 | 7 |  |  | Input-only numeral pronunciation; not a lexical Mandarin translation. |  |  |
| 2746 | U+0038_00 | 8 | 8 |  |  | Input-only numeral pronunciation; not a lexical Mandarin translation. |  |  |
| 2747 | U+0039_00 | 9 | 9 |  |  | Input-only numeral pronunciation; not a lexical Mandarin translation. |  |  |
