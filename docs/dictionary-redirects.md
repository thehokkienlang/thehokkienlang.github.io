# Dictionary and IME redirect log

Generated from [dictionary_redirects.tsv](../data/dictionary_redirects.tsv). Do not edit this Markdown file directly.

Sorted by the original reading using the existing Tangliengim jamo collation (syllables, then tones). Headword links and nonstandard-reading corrections use the existing dictionary/IME lookup and candidate paths. “Unknown” dates and missing historical rationales are deliberately not inferred.

| Original spelling / input | Original reading | Correct spelling | Correct reading | Type | Reason | Sources | Date | Target ID |
|---|---|---|---|---|---|---|---|---|
| 능잡1 | 능잡1 | 二十 | 띠잡1 | reading | Existing nonstandard reading correction; original rationale not recorded. | data/hokkien_hanri_dict.tsv | unknown | U+4E8C_U+5341_00 |
| 능잡커1 | 능잡커1 | 二十箍 | 띠잡커1 | reading | Existing nonstandard reading correction; original rationale not recorded. | data/hokkien_hanri_dict.tsv | unknown | U+4E8C_U+5341_U+7B8D_00 |
| 능쳰5커1 | 능쳰5커1 | 兩千箍 | 능촁5커1 | reading | Existing nonstandard reading correction; original rationale not recorded. | data/hokkien_hanri_dict.tsv | unknown | U+5169_U+5343_U+7B8D_00 |
| 먀4재 | 먀4재 | 明仔載 | 삔아1재 | reading | Existing nonstandard reading correction; original rationale not recorded. | data/hokkien_hanri_dict.tsv | unknown | U+660E_U+4ED4_U+8F09_00 |
| 米粉粿 | 삐1훈1궤2 | 麵粉粿 | 미훈1궤2 | headword | Wheat-flour dish: 麵粉粿, not rice-flour 米粉粿. | https://en.wiktionary.org/wiki/麵粉粿 https://www.zaobao.com.sg/lifestyle/food/story20240216-1468240 | 2026-10-14 | U+9EB5_U+7C89_U+7CBF_00 |
| 삐1훈1궤2 | 삐1훈1궤2 | 麵粉粿 | 미훈1궤2 | reading | Preserve old bi-hun-kue input; correct to mi-hun-kue. | https://en.wiktionary.org/wiki/麵粉粿 https://www.zaobao.com.sg/lifestyle/food/story20240216-1468240 | 2026-10-14 | U+9EB5_U+7C89_U+7CBF_00 |
| 신5가5포1 | 신5가5포1 | 新加坡 | 신5가5보1 | reading | Existing nonstandard reading correction; original rationale not recorded. | data/hokkien_hanri_dict.tsv | unknown | U+65B0_U+52A0_U+5761_00 |
| 짇쳰5커1 | 짇쳰5커1 | 一千箍 | 짇촁5커1 | reading | Existing nonstandard reading correction; original rationale not recorded. | data/hokkien_hanri_dict.tsv | unknown | U+4E00_U+5343_U+7B8D_00 |
| 쳰5커1 | 쳰5커1 | 千箍 | 촁5커1 | reading | Existing nonstandard reading correction; original rationale not recorded. | data/hokkien_hanri_dict.tsv | unknown | U+5343_U+7B8D_00 |
| 퇀솯 | 퇀솯 | 傳說 | 돤솯 | reading | Existing nonstandard reading correction; original rationale not recorded. | data/hokkien_hanri_dict.tsv | unknown | U+50B3_U+8AAA_00 |
| 핀돨5 | 핀돨5 | 貧惰 | 빈돨5 | reading | Existing nonstandard reading correction; original rationale not recorded. | data/hokkien_hanri_dict.tsv | unknown | U+8CA7_U+60F0_00 |

## Updating redirects

1. For a reading correction, add the existing `correction_alias` row in the dictionary TSV and a corresponding log row. For a headword correction, add a `headword` row here pointing to an existing lexical entry ID.
2. Record the reason, sources, and decision date. The corrected spelling and reading are resolved from the target entry, so they cannot drift.
3. Run `python tools/build_redirect_log.py` to sort the TSV and regenerate this log. The release gate runs `--check` and rejects stale logs, missing reading corrections, or invalid targets.
