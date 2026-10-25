# Harmonisation 3.2

Mixed-script spelling audit completed on 2026-10-25 against the supplied
*Tangliengim Orthography v3.2*, especially sections 4.1-4.5, with the
apostrophe-domain rules in section 3.5 and Appendix C.4.

Reference SHA-256:
`b33f0c71f643e3654b19e9c48cd0e285097c7d7cbcfbb8b255bb070761ed3c64`.
The reference is the 59-page PDF supplied by the author, not a generated
dictionary or a transcription inferred from the website.

## Scope And Coverage

- All 90 published authored records were inventoried, across English,
  Traditional Chinese, and Simplified Chinese presentations.
- The 70 displayed song titles were checked separately from their hidden
  pronunciation headers. Existing title spellings already use the permitted
  pronouns, neutral domains, foreign names, and expressive transcriptions.
- 1,883 reviewed base-script edits affect 70 reading pages. The remaining
  active records require no running-text spelling edits within this scope.
- The two archived records, original WordPress snapshots, and WordPress
  itself are unchanged. Every published URL and displayed title is preserved.
- The dictionary, IME candidates, audio files, and pronunciation algorithms
  are unchanged. Teaching examples and explicitly phonetic tables remain
  phonetic rather than being converted into mixed-script prose.
- Teochew and Mandarin song presentations are outside a Hokkien-specific
  orthography migration. Foreign-language quotations and source transcriptions
  are not assigned Hokkien readings.

## Rules Applied

Hanri is the default in mixed prose. Examples include 無, 有, 毋, 會, 𣍐,
是, 也, 就, 著, 咧, 嘛, 較, 予, 佇, 攏, 慐, 㩼, and 爾爾. Context
distinguishes relational 共 from disposal/object-marking 가, 覓 after 看
from prohibitive 매, and source 𨘗 from destination 對 or purposive 為.

Core personal pronouns, free deictics, grammatical 애/매, question-marker
감, 곻, and disposal 가 retain Hangul. Independent 제 and 헤 are not
rewritten merely because the following text contains a noun. The manual
distinguishes these from bound 這/彼 and their 짇/힏 readings.

Visible Hangul bases carrying only tone ruby are still base text for audit
purposes. Their tones move into the new Hanri reading ruby. Existing reading
ruby is not reinterpreted. The authored contextual reading is preserved rather
than regenerated from a default citation reading. New connected readings use
the existing trailing-hyphen convention.

An apostrophe domain extends across formatting tags until the next whitespace
or punctuation boundary. Its Hangul is excluded from conversion. Encoded
apostrophes and explicit line breaks are covered by regression tests.

## Author Decisions

| Form | Decision |
| --- | --- |
| Sung 꾼 | Retain the sung reading, including independent lyric uses |
| 뻐, 샹, 안니, 간나 | Retain Hangul pending future Hanri decisions |
| 똬 | 偌 |
| 일아 | 嬰仔 |
| 촿 | 掣 |
| 텧, 간다 | Retain Hangul for future review |
| 에당, 다버/자뻐, 오로, 霧샇샇 | Retain for future spelling review |
| 쉬, 好캉, 안좔, 완來왇去 | 媠, 好康, 按怎, 彎來斡去 |
| 핳 in 真正핳徦欲死 | 哈, not 合 |
| 벻 in 心意來벻上天 | 𬦰 |
| 偌니 | 偌邇 |
| 뽀대뽀지 | 無代無誌 |
| 뽀내제 全部是 | 無奈제 全部是; retain independent 제 |
| Happy's destination 欲위底去 | 對; preserve the authored reading |
| The Egg's 應該是도2 一个小學’에 老師 | 底 “which”, not 就; existing dictionary reading 도2 |
| Temporal 這마 | 這馬; dictionary citation reading 짇1마2, confirmed by the author |

Native interjections and sung sound-symbolic refrains remain phonetic, not
guessed from homophonous Hanri. Japanese 仕上げ (시아껳), taxi (덱시),
motorbike (오도빼), and the other existing foreign transcriptions are protected
as whole words so that an internal 시, 빼, or 뻐 is not converted separately.

Temporal 這마 now uses 這馬, preserving each authored contextual reading as
ruby. The capability element 당 remains for review rather than being guessed
as an unrelated lexical 當. These decisions are classified in the audit ledger.

The alternate verse of 望春風 contains one bare 阮 with no ruby reading and
an omitted Lomari syllable. Its parallel verse provides the sung 꾼 reading;
the prescribed Hangul pronoun is restored using that evidence. This is the
only newly supplied reading, and it has an explicit regression exception.

These retention decisions document the author's current editorial policy;
they do not claim that additional Hanri assignments have already been made
in the v3.2 manual. This is a mixed-script content audit, not a change to
the dictionary schema, tone engine, or every phonetic teaching example.

## Provenance And Verification

`harmonisation-3.2-audit.json` contains each record's before/after body hashes
and exact, non-overlapping edits with the governing rule or author decision.
Every edit is reversible. The migration-preservation test reconstructs the
pre-harmonisation text before comparing its text, readings, media counts,
and original-source hash with the unchanged WordPress archive. It does not
disable the original preservation check or accept arbitrary future rewrites.

The content fallback font adds the rare characters 𠢕, 𨑨, 𨘗, and 𬦰 using
the existing licensed sans-serif source. Other Hanri retain the existing
Noto Sans TC convention; 㩼 retains its explicit Noto Sans SC exception.

```sh
python -X utf8 tools/harmonise_content_v32.py --check
python -X utf8 -m unittest discover -s tests -p 'test_site_*.py'
python -X utf8 -m unittest discover -s tests -p test_wordpress_migration.py
python -X utf8 tools/build_site.py
python -X utf8 tools/check_site.py
```

The optional Chromium/WebKit rendering check remains
`tools/check_content_rendering.py`. New source edits require an explicit
review of the ledger, not an automatic replacement of the reviewed baseline.

## Dictionary Follow-Up

The author subsequently requested matching dictionary/IME updates and removal
of superseded pure-Hangul entries. That separate, reviewed data migration is
documented in [Dictionary Sync](harmonisation-3.2-dictionary.md). It supersedes
the original content-only checkpoint's statement that dictionary data was
unchanged; the pronunciation algorithms and audio recordings remain unchanged.
