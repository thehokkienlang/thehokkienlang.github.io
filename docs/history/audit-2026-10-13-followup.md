# Definition and audio follow-up, 13 October 2026

Only tasks 2 and 3 were continued. Tasks 1 (v3.1 migration), 4 (WordPress) and 5 (new validation work) remain paused. The existing release gate was resumed for the authorized deployment of tasks 2 and 3. No headwords, readings, IDs, ranking, categories or WAV files were changed.

## Definitions

41 source records across 39 headwords now use whole-word English glosses. These are focused editorial corrections, not an exhaustive semantic validation of the dictionary. Two readings of 清醒 and the canonical/correction-alias records of 明仔載 are kept consistent.

歲頭 is **age / 年齡 / 年龄**, not “beginning of the year”. The earlier audit recommendation incorrectly trusted its Mandarin metadata. The [MOE entry](https://sutian.moe.edu.tw/zh-hant/su/9677/) establishes its sense. [明仔載](https://sutian.moe.edu.tw/zh-hant/su/4208/) means tomorrow; [稀微](https://sutian.moe.edu.tw/zh-hant/su/8803/) means lonely/desolate. Other edits remove component-level noise from ordinary shared Chinese expressions while retaining their existing Mandarin lookup. Exact before/after values and evidential basis are in [the definition manifest](audit-2026-10-13-definitions.json).

| Headword | Previous English | Corrected English |
| --- | --- | --- |
| 代表 | generation; replace; surface; express | represent; representative |
| 日常 | day; sun; usual; constant | daily; everyday |
| 能力 | ability; can; strength; power | ability; capability |
| 表演 | surface; express; perform; develop | perform; performance |
| 平安 | flat; ordinary; peace; safe | safe; peaceful |
| 保證 | protect; keep; prove; certificate | guarantee; assure |
| 面對 | face; surface; correct; toward; pair | face; confront |
| 明仔載 | bright; clear; diminutive suffix | tomorrow |
| 消息 | disappear; remove; rest; breath | news; information |
| 消遣 | disappear; remove; send; dispatch | pass the time; recreation |
| 設計 | set up; design; plan; count | design; plan |
| 事實 | matter; affair; real; solid | fact; reality |
| 辭職 | resign; words; job; duty | resign from a job |
| 鉛筆 | lead; pencil; pen; brush | pencil |
| 政治 | government; politics; govern; treat | politics |
| 情話 | feeling; affection; speech; language | words of affection |
| 造成 | make; create; become; accomplish | cause; bring about |
| 全世界 | whole; all; world; generation | the whole world |
| 絕望 | cut off; despair; hope; look | despair; lose hope |
| 石頭 | head | stone; rock |
| 自由自在 | self; from; reason; exist; at | free and at ease |
| 尊嚴 | honorable; respect; strict; solemn | dignity |
| 初戀 | beginning; first; love; long for | first love |
| 清醒 | clear; pure; wake; sober | awake; clear-headed; sober |
| 笑容 | laugh; smile; appearance; contain | smile |
| 春雨 | rain | spring rain |
| 出現 | go out; produce; present; appear | appear; emerge |
| 輕鬆 | light; easy; loose; relaxed | relaxed; easy |
| 態度 | state; attitude; degree; measure | attitude |
| 體驗 | body; form; verify; experience | experience; experience firsthand |
| 體諒 | body; form; forgive; understand | understand; make allowances for |
| 湯匙 | soup; hot water; spoon; key | spoon |
| 博物館 | thing; hall; shop; institution | museum |
| 脾氣 | spleen; temper; air; energy | temper; disposition |
| 發現 | send out; develop; present; appear | discover; notice |
| 懷疑 | harbor; miss; doubt; suspect | doubt; suspect |
| 負責任 | carry; betray; responsibility; blame; duty | take responsibility; be responsible |
| 歲頭 | head | age |
| 稀微 | rare; thin; slight; subtle | lonely; desolate |

### Meaning review still needed

- 舒佮: the current English and Mandarin fields suggest “comfortable”, while [Wiktionary’s Southern Min entry](https://en.wiktionary.org/wiki/舒合) associates the alternative spelling 舒佮 with “to like”. Please confirm the intended local sense before changing it.
- The 13 unresolved cases in [the existing review queue](mandarin-lookup-review.md#manual-review---low-confidence-only) remain untouched, including 뎋, attached particles, 獄城, 兩角, 人願, 北陰酆都, 米粉粿, 蟮 and 心狂.
- Numerous other compound glosses still contain component-level noise. This pass is intentionally limited to the clear corrections listed above; it does not certify the remaining glosses.

## Audio repair

The old grouped-syllable resolver dropped recorded neighbours when one part was missing, then tried a whole-chunk filename alias. Some aliases represented only the first syllable and could incorrectly report complete playback.

The resolver now returns each available recording with its correct syllable and tone, plus precise missing keys. Both classic Desktop playback and the Web JSON builder consume those tuples. Existing syllable splitting and tone rules remain unchanged.

Available audio is recovered in five readings: 獄城、孽鏡台、月台、月老、錢銀. Three previously hidden failures are now reported correctly: 地獄、無間地獄、十殿閻君. They formerly used a first-syllable recording as if it represented the whole group. Eight source audio objects change in total.

The corrected inventory flags **24 entries and 17 distinct syllable/tone recordings**. These files were not found under any supported filename alias. Confirm any uncertain source pronunciation before recording. No substitute pronunciation, synthesis or wrong-tone recording has been used.

| Missing key | Suggested WAV filename | Affected entries |
| --- | --- | --- |
| 꺔3 | `giam3.wav` | 十殿閻君 |
| 꺔4 | `giam4.wav` | 尊嚴 |
| 꺔5 | `giam5.wav` | 體驗 |
| 꺕1 | `giap1.wav` | 出業 |
| 꼉2 | `giong2.wav` | 久仰 |
| 꼑1 | `giek1.wav` | 地獄、無間地獄 |
| 꼑3 | `giek3.wav` | 獄城 |
| 꼗1 | `giet1.wav` | 妖孽 |
| 꼗3 | `giet3.wav` | 孽鏡台、孽緣 |
| 꽏3 | `goat3.wav` | 月台、月老、花容月貌 |
| 끤4 | `gin4.wav` | 銀 |
| 따2 | `ra2.wav` | 菝仔、一點仔、姼仔 |
| 땀3 | `ram3.wav` | 一暗 |
| 열4 | `yorl4.wav` | 楊 |
| 질1 | `jil1.wav` | 水晶 |
| 질3 | `jil3.wav` | 錢銀 |
| 질4 | `jil4.wav` | 本錢、錢 |

Machine-readable details: [audio inventory](audit-2026-10-13-audio.json). This inventory covers the current source entries, not every possible sentence or keyboard syllable.

## Verification and release status

- Focused checks cover missing-first, missing-last, both-missing and fully recorded groups, including correct per-part tone metadata in Web output.
- Existing audio/metadata tests: 13 passed. Existing PCM checks: 16 reference waveforms matched.
- Runtime data rebuilt successfully: 5,446 objects; all source IDs, headwords, readings, categories and row order preserved. Only 41 source definition records and eight source audio objects differ in the checked fields.
- Deployment validation: the complete existing release gate passed, including 57 dictionary tests, static/adaptive ranking, Desktop parity, 16 PCM waveform references and both built Web applications. The dictionary snapshot was refreshed after reviewing the intended definition/audio changes; all 2,240 candidate keys and visible candidate orders remain identical. No new tests or WordPress content were changed. Tasks 1, 4 and new validation work in task 5 remain paused.

Historical one-time migration reports retain their original wording; use this dated follow-up as the current correction record.
