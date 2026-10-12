# Rare Hanri display and deployment repair

## Rendering and editing

`𤺪` (U+24EAA) is absent from the installed Noto Sans TC/SC/KR/HK/JP and
Noto Serif CJK font maps. Plangothic P1 includes it and shares the Source Han
Sans design family. The licensed, renamed subset is bundled locally rather
than depending on an external font service or requiring a font installation.

The shared CSS applies it only to U+24EAA. Normal Hanri still uses Noto Sans TC;
`㩼` keeps its Noto Sans SC handling. The active Local shared shell uses the
same browser font. The Windows classic Pad privately loads the TTF and tags
only this character in the input and candidate menu. The glyph has no new
dictionary reading or entry ID merely because its display font changed.

The shared composer also treated UTF-16 halves as independent cursor/deletion
units. It now crosses/deletes complete supplementary characters and expands
partial selections to their boundaries. This applies to rare Hanri and emoji,
not a hardcoded input string. Caret measurement reads a full code point too.
Existing Hangul/jamo composition and tone annotations remain unchanged.

Source/license/reproduction: [`assets/fonts/README.md`](../assets/fonts/README.md).

## Failed deployment

Run [38253116214](https://github.com/thehokkienlang/thehokkienlang.github.io/actions/runs/38253116214)
failed because the user-added `悿 / 턈2 / U+60BF_00` row was appended after the
number-pronunciation section. The canonical sorter restores its proper location
without changing any row contents or IDs. All 2,738 current rows are retained.

Downstream checks also assumed the dictionary size/default-key set could never
grow. The two fixed-size tests now compare exact source IDs, source counts/type
counts and Hanri coverage with generated records. The historical pronunciation
floor still checks every previous default, while allowing new reading keys;
the reverse-row checks protect the complete current default maps.

Before refreshing the three dictionary/cold-start snapshots, a read-only audit
proved that the only new runtime identities are the approved `U+60BF_00` and
its generated `-sandhi` view. All 5,442 previous runtime records, old candidate
relationships, categories, audio/tone/Lomari runtime metadata and previous
reading contexts remain intact. The new reading group adds three Web/classic
cold-start cases. This is an explicit addition review, not a blind baseline reset.

## Verification

- 57 dictionary tests, including scoped-font and supplementary-character tests.
- Desktop and Android-emulated browser font inspection: U+24EAA uses the custom
  fallback; normal Hanri and `㩼` retain their old fonts. Editing/copy tests pass.
- Windows process-only classic font loader successfully exposes the new family.
- Source/schema, canonical ordering, static/adaptive ranking, safeguards,
  Local/Desktop bridge, 16 waveform cases and existing legacy parity pass.
- Built site contains 5,444 runtime records and 1,508 referenced recordings.
- Main TSV field contents/IDs, registry, categories, priorities and WAV payloads
  are preserved. Only source-row ordering and reviewed addition snapshots change.

No legacy-backup file, pronunciation policy, adaptive formula or audio asset is
modified by this repair. Future lexical edits still require sorting, validation,
build and an explicit review of affected regression snapshots before release.
