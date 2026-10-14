# Empty definition follow-up, 14 October 2026

Reviewed 24 entry rows with empty English or Mandarin fields. Filled two rows (six fields); preserved 22 rows for the reasons below. The comment row at line 2 is excluded. Physical TSV line numbers refer to this commit; stable IDs are in the JSON manifest.

## Filled: direct dictionary attestation

| Line | Entry | Reading | English | Mandarin Traditional | Mandarin Simplified |
| --- | --- | --- | --- | --- | --- |
| 2389 | 悿 | 턈2 | tired; exhausted; severe (in degree) | 疲累; 慘重; 嚴重 | 疲累; 惨重; 严重 |

[MOE 忝](https://sutian.moe.edu.tw/zh-hant/su/3879/) explicitly lists 悿 as an alternate spelling. This supports both fatigue and severity; the character, reading and entry identity are preserved.

## Filled: explicit user definition of a bound character

| Line | Entry | English | Mandarin Traditional | Mandarin Simplified |
| --- | --- | --- | --- | --- |
| 1309 | 蟮 | bound character (used in 蟮蟲); not a standalone word | 僅用於複詞的字（如蟮蟲），不單獨成詞 | 仅用于复词的字（如蟮虫），不单独成词 |

The user explicitly requested this annotation on 14 October 2026. This identifies the character’s bound status without assigning the whole compound’s gecko meaning to a standalone word.

## Unchanged: grouped by reason

### Grammatical function unconfirmed

| Line | Entry | Reading | Reason |
| --- | --- | --- | --- |
| 14 | 뎋 | 뎋 | Input override/attached form; needs a usage sentence identifying its grammatical function before adding English or Mandarin. |
| 15 | ’됴 | ’됴 | Input override/attached form; needs a usage sentence identifying its grammatical function before adding English or Mandarin. |
| 16 | ’둏 | ’둏 | Input override/attached form; needs a usage sentence identifying its grammatical function before adding English or Mandarin. |
| 19 | ’래 | ’래 | Input override/attached form; needs a usage sentence identifying its grammatical function before adding English or Mandarin. |
| 51 | ’킈 | ’킈 | Input override/attached form; needs a usage sentence identifying its grammatical function before adding English or Mandarin. |

### Conflicting sense

| Line | Entry | Reading | Reason |
| --- | --- | --- | --- |
| 215 | 挭 | 곙5 | Existing block/choke gloss conflicts with the MOE support/prop sense for alternate 挭 under 楗; confirm the intended sense and reading before translating. |

### Uncertain referent

| Line | Entry | Reading | Reason |
| --- | --- | --- | --- |
| 354 | 獄城 | 꼑샬4 | Prison, an infernal city, or a particular religious name is not established by the component gloss. |
| 930 | 北陰酆都 | 박1임5헝5더1 | Religious references attest a related deity title; this shortened entry does not identify whether a deity/title or place is intended. |

### Multiple senses

| Line | Entry | Reading | Reason |
| --- | --- | --- | --- |
| 411 | 兩角 | 능각 | MOE attests the currency use, but 角 also means corner/horn; a usage example is needed to choose the intended sense. |
| 1487 | 心狂 | 심5겅4 | Existing mind losing gloss does not distinguish panic/agitation, anger, or mental derangement; compound examples do not settle this standalone entry. |

### Insufficient whole word evidence

| Line | Entry | Reading | Reason |
| --- | --- | --- | --- |
| 698 | 人願 | 띤꽌5 | Existing person/people gloss does not establish the whole expression; an intended meaning or sentence is needed. |

### Food identity

| Line | Entry | Reading | Reason |
| --- | --- | --- | --- |
| 1173 | 米粉粿 | 삐1훈1궤2 | Existing bee hoon kueh label leaves rice-flour food versus wheat-flour mee hoon kueh unresolved; confirm the dish. |

### Input only numeral

| Line | Entry | Reading | Reason |
| --- | --- | --- | --- |
| 2732 | 0 | 0 | Pronunciation-routing row for a digit; intentionally not a lexical translation entry. |
| 2733 | 1 | 1 | Pronunciation-routing row for a digit; intentionally not a lexical translation entry. |
| 2734 | 2 | 2 | Pronunciation-routing row for a digit; intentionally not a lexical translation entry. |
| 2735 | 3 | 3 | Pronunciation-routing row for a digit; intentionally not a lexical translation entry. |
| 2736 | 4 | 4 | Pronunciation-routing row for a digit; intentionally not a lexical translation entry. |
| 2737 | 5 | 5 | Pronunciation-routing row for a digit; intentionally not a lexical translation entry. |
| 2738 | 6 | 6 | Pronunciation-routing row for a digit; intentionally not a lexical translation entry. |
| 2739 | 7 | 7 | Pronunciation-routing row for a digit; intentionally not a lexical translation entry. |
| 2740 | 8 | 8 | Pronunciation-routing row for a digit; intentionally not a lexical translation entry. |
| 2741 | 9 | 9 | Pronunciation-routing row for a digit; intentionally not a lexical translation entry. |

## Additional references

- [楗 / alternate 挭](https://sutian.moe.edu.tw/zh-hant/su/9570/): supports propping/support, which does not authenticate the existing block/choke gloss.
- [角](https://sutian.moe.edu.tw/zh-hant/su/3386/) and [currency example 兩角](https://sutian.moe.edu.tw/zh-hant/su/12962/): evidence for a possible currency meaning, without deciding the intended row sense.
- [酆都大帝, National Museum of Taiwan History](https://dict.th.gov.tw/detailPage.aspx?Ca=283&ID=1217): related deity/place context, without assigning a referent to the abbreviated entry.

## Validation

All existing release checks passed: 57 dictionary tests; candidate identity/order and ranking; Desktop parity; audio PCM parity; built site and both Web applications. A truncated WAV in the temporary build output was detected by the site check; the tracked source matched GitHub and a clean rebuild passed the asset checks. No source audio changed. GitHub performs the Linux/Windows release gate again before deploying.

Historical review documents retain their original decisions; this dated report is the current blank-field inventory.
