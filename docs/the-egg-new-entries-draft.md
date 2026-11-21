# The Egg: draft dictionary rows for review

Drafted on 2026-11-21 from Haru's answers in
`docs/the-egg-dictionary-audit.md`. These are **113 proposed new rows** for
`data/hokkien_hanri_dict.tsv`. Nothing has been added yet.

The codes match the audit. Reply in the same way, for example
"M14: english angry; resentful" or "D4 v".

## How the columns were filled

- **hanri, reading:** from Haru's answers. Readings are converted to TSV tone
  digits: ˆ=1, ˋ=2, ˊ=4, ˉ=5, and no digit for tone 3. Non-final syllables keep
  their sandhi tone; the final syllable is in citation tone.
- **simplified:** made automatically with the project's OpenCC `tw2s`
  converter. It is `〃` when unchanged, and blank when the headword has no
  Hanri (D2).
- **mandarin_trad / mandarin_simp / english:** **drafted by Claude, for Haru to
  review.** `〃` follows the schema: mandarin_trad 〃 = the headword, and
  mandarin_simp 〃 = mandarin_trad.

## Please check these first

These glosses are the least certain:

- **D4 專工.** "specially, on purpose" (sutian 7145).
- **D10 霧샇샇.** "confused".
- **M14 激心.** Drafted as "infuriating, frustrated". It might rather mean
  heartbreaking or exasperating.
- **M20 心目.** "mind's eye".
- **M52 伸輪.** Drafted as "stretch". Check the headword.
- **M55 淡薄.** "a little".
- **M60 臭奶呆.** "lisp or heavy accent".
- **M69 根本.** Both the adverb ("at all") and the noun ("root").
- **M72 臭酸步.** "cliché, hackneyed trick".
- **M94 成做.** "become, act as".
- **U3 按.** "from; how (as in 按怎)".

Two notes on specific rows:

- **R3 變** is a second 變 row, read 빌, next to the existing 볜 row.
- **D7 流目滓** keeps this headword. Its Mandarin gloss is 流眼淚.

## Draft rows

| Code | hanri | simplified | reading | mandarin_trad | mandarin_simp | english |
|---|---|---|---|---|---|---|
| R3 | 變 | 变 | 빌 | 〃 | 变 | change; become; turn into (colloquial reading) |
| D1 | 揆一 | 〃 | 귀읻 | 〃 | 〃 | Frederick Coyett, last Dutch governor of Formosa |
| D2 | 힏ᄅힻ |  | 힏ᄅힻ1 | 希特勒 | 〃 | Hitler |
| D3 | 痛疼 | 〃 | 탕2턀 | 疼痛 | 〃 | pain; ache |
| D4 | 專工 | 专工 | 좐5강1 | 特地; 專門 | 特地; 专门 | specially; on purpose |
| D5 | 一粒 | 〃 | 짇럅 | 一顆 | 一颗 | one (small round object) |
| D6 | 台 | 〃 | 대4 | 輛; 台 | 辆; 台 | classifier for vehicles and machines |
| D7 | 流目滓 | 〃 | ᄅᅷ빡새2 | 流眼淚 | 流眼泪 | shed tears; cry |
| D8 | 鬆一口氣 | 松一口气 | 상5짇ᄏᅷ1퀴 | 〃 | 松一口气 | breathe a sigh of relief |
| D9 | 等’짇에 | 〃 | 단2’짇에 | 等一下 | 〃 | wait a moment; in a moment |
| D10 | 霧샇샇 | 雾샇샇 | 뿌샇1샇 | 一頭霧水 | 一头雾水 | confused; bewildered |
| M1 | 過身 | 过身 | 궤2신1 | 過世 | 过世 | pass away; die |
| M2 | 進前 | 进前 | 진2졩4 | 之前; 以前 | 〃 | before; previously |
| M3 | 行路 | 〃 | 걀러5 | 走路 | 〃 | walk; go on foot |
| M4 | 車禍 | 车祸 | 챠5호5 | 〃 | 车祸 | traffic accident; car crash |
| M5 | 致命 | 〃 | 디2뼹5 | 〃 | 〃 | fatal; deadly |
| M6 | 救護員 | 救护员 | 규2허완4 | 〃 | 救护员 | paramedic; ambulance worker |
| M7 | 盡力 | 尽力 | 진롁1 | 〃 | 尽力 | do one's best; make every effort |
| M8 | 救 | 〃 | 규 | 〃 | 〃 | save; rescue |
| M9 | 實在 | 实在 | 싣재5 | 〃 | 实在 | really; truly; indeed |
| M10 | 照實 | 照实 | ᄌᆤ2싣1 | 〃 | 照实 | truthfully; honestly; as it is |
| M11 | 彼陣 | 彼阵 | 힏1준5 | 那時 | 那时 | at that time; then |
| M12 | 貨車 | 货车 | 훼2챠1 | 〃 | 货车 | truck; lorry |
| M13 | 拍遨 | 〃 | 팧1꼬4 | 打滑 | 〃 | skid; slip |
| M14 | 激心 | 〃 | 곅1심1 | 令人氣憤; 嘔氣 | 令人气愤; 呕气 | infuriating; frustrated; annoyed |
| M15 | 來世 | 来世 | 래세 | 〃 | 来世 | next life; afterlife |
| M16 | 差不多 | 〃 | 차5붇1도1 | 〃 | 〃 | about; almost; more or less |
| M17 | 反應 | 反应 | 환1옝 | 〃 | 反应 | reaction; response; react |
| M18 | 頭一 | 头一 | ᄐᅷ짇1 | 第一 | 〃 | first |
| M19 | 著迷 | 着迷 | 둏뻬4 | 〃 | 着迷 | be fascinated by; be obsessed with |
| M20 | 心目 | 〃 | 심5뻑1 | 〃 | 〃 | mind's eye; view; regard |
| M21 | 擔心 | 担心 | 담5심1 | 〃 | 担心 | worry; be anxious |
| M22 | 完美 | 〃 | 완삐2 | 〃 | 〃 | perfect; flawless |
| M23 | 表面 | 〃 | ᄇᆤ1삔5 | 〃 | 〃 | surface; outward appearance |
| M24 | 婚姻 | 〃 | 훈5인1 | 〃 | 〃 | marriage |
| M25 | 愈來愈 | 愈来愈 | 뚜1래뚜2 | 越來越 | 越来越 | more and more; increasingly |
| M26 | 愧疚 | 〃 | 퀴2규 | 〃 | 〃 | guilt; remorse; feel guilty |
| M27 | 天堂 | 〃 | 톈5덩4 | 〃 | 〃 | heaven; paradise |
| M28 | 輪迴轉世 | 轮回转世 | 룬훼좐1세 | 〃 | 轮回转世 | reincarnation; the cycle of rebirth |
| M29 | 印度教 | 〃 | 인2더ᄀᅷ | 〃 | 〃 | Hinduism |
| M30 | 宗教 | 〃 | 정5ᄀᅷ | 〃 | 〃 | religion |
| M31 | 虛空 | 虚空 | 희5컹1 | 〃 | 虚空 | void; emptiness; the empty sky |
| M32 | 轉世 | 转世 | 좐1세 | 〃 | 转世 | reincarnate; be reborn |
| M33 | 白紙 | 白纸 | 벻좌2 | 〃 | 白纸 | blank paper; white paper |
| M34 | 內心 | 内心 | 뤠심1 | 〃 | 内心 | inner heart; one's inner self |
| M35 | 知識 | 知识 | 디2셱 | 〃 | 知识 | knowledge |
| M36 | 經驗 | 经验 | 곙5꺔5 | 〃 | 经验 | experience |
| M37 | 停頓 | 停顿 | 톙둔 | 〃 | 停顿 | pause; halt |
| M38 | 腳步 | 脚步 | 카5버5 | 〃 | 脚步 | footstep; step; pace |
| M39 | 握 | 〃 | 악 | 〃 | 〃 | hold; grip; grasp |
| M40 | 肩頭 | 肩头 | 곙5ᄐᅷ4 | 肩膀 | 〃 | shoulder |
| M41 | 想像 | 〃 | 셩1셩5 | 〃 | 〃 | imagine; imagination |
| M42 | 宏偉 | 宏伟 | 헝위2 | 〃 | 宏伟 | grand; magnificent |
| M43 | 龐大 | 庞大 | 팡대5 | 〃 | 庞大 | huge; enormous |
| M44 | 人類 | 人类 | 띤뤼5 | 〃 | 人类 | humankind; human beings |
| M45 | 心智 | 〃 | 심5디 | 〃 | 〃 | mind; intellect |
| M46 | 承載 | 承载 | 솅재 | 〃 | 承载 | bear; carry; hold |
| M47 | 部分 | 〃 | 버훈5 | 〃 | 〃 | part; portion; section |
| M48 | 手指 | 〃 | 츄1재2 | 〃 | 〃 | finger |
| M49 | 摸 | 〃 | 뻥1 | 〃 | 〃 | touch; feel; stroke |
| M50 | 載具 | 载具 | 재2구5 | 〃 | 载具 | vehicle; vessel (that carries something) |
| M51 | 得著 | 得着 | 딛1둏1 | 得到 | 〃 | obtain; get; gain |
| M52 | 伸輪 | 伸轮 | 춘5룬4 | 伸懶腰 | 伸懒腰 | stretch (one's body) |
| M53 | 浩大 | 〃 | 헐대5 | 〃 | 〃 | vast; immense |
| M54 | 意識 | 意识 | 이2셱 | 〃 | 意识 | consciousness; awareness |
| M55 | 淡薄 | 〃 | 담봏 | 一點點; 稍微 | 一点点; 稍微 | a little; slightly |
| M56 | 而且 | 〃 | 띠챨2 | 〃 | 〃 | moreover; and also |
| M57 | 無數 | 无数 | 뿌서 | 〃 | 无数 | countless; innumerable |
| M58 | 西元 | 〃 | 세5꽌4 | 〃 | 〃 | Common Era; AD |
| M59 | 農村 | 农村 | 렁춘1 | 〃 | 农村 | farming village; rural area |
| M60 | 臭奶呆 | 〃 | ᄎᅷ2니5대1 | 口齒不清; 大舌頭 | 口齿不清; 大舌头 | speak with a lisp or a heavy accent; inarticulate |
| M61 | 技術 | 技术 | 기5숟1 | 〃 | 技术 | technology; technique; skill |
| M62 | 解釋 | 解释 | 개1셱 | 〃 | 解释 | explain; explanation |
| M63 | 另外 | 〃 | 롕꽈5 | 〃 | 〃 | besides; in addition; other |
| M64 | 樣 | 样 | 율5 | 〃 | 样 | kind; sort; appearance |
| M65 | 理解 | 〃 | 리1개2 | 〃 | 〃 | understand; comprehend |
| M66 | 時空 | 时空 | 시컹1 | 〃 | 时空 | spacetime; time and space |
| M67 | 拄著 | 拄着 | 두1둏1 | 遇到; 碰到 | 〃 | meet; run into; encounter |
| M68 | 知覺 | 知觉 | 디5각 | 〃 | 知觉 | perception; senses; consciousness |
| M69 | 根本 | 〃 | 군분2 | 〃 | 〃 | at all; basically; root |
| M70 | 注意 | 〃 | 주2이 | 〃 | 〃 | pay attention; notice |
| M71 | 為著 | 为着 | 위둏1 | 為了 | 为了 | for; for the sake of; because of |
| M72 | 臭酸步 | 〃 | ᄎᅷ2승5버5 | 老套 | 〃 | cliché; hackneyed trick |
| M73 | 疑問 | 疑问 | 끼뿐5 | 〃 | 疑问 | doubt; question |
| M74 | 合理 | 〃 | 합리2 | 〃 | 〃 | reasonable; logical |
| M75 | 創造 | 创造 | 청2조5 | 〃 | 创造 | create; make |
| M76 | 原因 | 〃 | 꽌인1 | 〃 | 〃 | reason; cause |
| M77 | 成長 | 成长 | 솅뎡2 | 〃 | 成长 | grow; growth; develop |
| M78 | 最終 | 最终 | 줴2졍1 | 〃 | 最终 | final; ultimate; in the end |
| M79 | 智者 | 〃 | 디2쟈2 | 〃 | 〃 | wise person; sage |
| M80 | 別 | 别 | 받1 | 別的 | 别的 | other; another |
| M81 | 總算 | 总算 | 정1승 | 〃 | 总算 | finally; at last |
| M82 | 明白 | 〃 | 뼹벻1 | 〃 | 〃 | understand; clear |
| M83 | 尻脊 | 〃 | 카5쟣 | 背部 | 〃 | back (of the body) |
| M84 | 恭喜 | 〃 | 경5히2 | 〃 | 〃 | congratulations |
| M85 | 補 | 补 | 버2 | 〃 | 补 | make up for; mend; supplement |
| M86 | 害死 | 〃 | 해시2 | 〃 | 〃 | kill; cause the death of |
| M87 | 百萬 | 百万 | 밯1빤5 | 〃 | 百万 | million |
| M88 | 耶穌 | 耶稣 | 야서1 | 〃 | 耶稣 | Jesus |
| M89 | 跟綴 | 跟缀 | 군5뒈 | 跟隨 | 跟随 | follow |
| M90 | 逐擺 | 逐摆 | 닥배2 | 每次 | 〃 | every time; each time |
| M91 | 加害 | 〃 | 가5해5 | 〃 | 〃 | harm; injure; assault |
| M92 | 一件 | 〃 | 짇걀5 | 〃 | 〃 | one (item, matter or garment) |
| M93 | 善行 | 〃 | 셴혱4 | 〃 | 〃 | good deed; act of kindness |
| M94 | 成做 | 〃 | 쟐죄 | 當作; 成為 | 当作; 成为 | become; turn into; act as |
| M95 | 面目 | 〃 | 삔뻑1 | 〃 | 〃 | face; appearance; true nature |
| M96 | 同類 | 同类 | 덩뤼5 | 〃 | 同类 | one's own kind; the same kind |
| M97 | 胎兒 | 胎儿 | 태5띠4 | 〃 | 胎儿 | fetus |
| U1 | 抑是 | 〃 | 앟시5 | 或是 | 〃 | or; or else |
| U2 | 一口氣 | 一口气 | 짇ᄏᅷ1퀴 | 〃 | 一口气 | one breath; in one go |
| U3 | 按 | 〃 | 안2 | 從; 如何 | 从; 如何 | from; how (as in 按怎) |
| U4 | 怎 | 〃 | 좔2 | 〃 | 〃 | how; why (as in 怎樣) |
| U6 | 為’둏 | 为’둏 | 위5’둏 | 為了 | 为了 | for; for the sake of (variant of 為著) |

## After review

1. Add the approved rows with the Dictionary Editor. It allocates the IDs and
   sorts the file.
2. Follow the Dictionary Update SOP in `AGENTS.md`: validate, sort, build,
   review, capture the three baselines, then `--source-only`.
3. Apply the story fixes listed in the audit: R1, R2, M11, U5.
4. Rerun the audit. Item 11 (pointing gloss links at the site's dictionary)
   can then start.
