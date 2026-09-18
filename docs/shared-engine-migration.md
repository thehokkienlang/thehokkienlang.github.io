# Shared Engine Migration

## Ownership

- GitHub owns the shared Tangliengim engine, TSV, audio data, Web IME, Dictionary, shared styling, and parity tests.
- The active desktop application owns HTML modes, TSV editing and GitHub sync, native clipboard/filesystem access, and packaging.
- `C:\Users\Asus\Documents\Hokkien Programs\Hokkien Hangul IME\Hokkien Tangliengim IME Pad.py` is an untouched legacy backup and is never modified.
- `C:\Users\Asus\Documents\Hokkien Programs\Hokkien Hangul IME\Hokkien Tangliengim IME Pad GitHub Synced Ver\Hokkien Tangliengim IME Pad.py` is the current desktop reference for parity checks. It remains the home of local-only HTML modes and TSV sync until those extensions are explicitly migrated.

## Migration Rule

Do not add new pronunciation, sandhi, candidate, or audio rules directly to a Web or desktop UI. Add them to the shared engine and cover them with a desktop parity fixture first.

## Parity Fixtures

`tests/fixtures/legacy-ime-parity-cases.json` lists inputs to capture.

To refresh the reference fixture from the active desktop reference:

```powershell
python -X utf8 tools/capture_legacy_parity.py `
  --reference-root "C:\Users\Asus\Documents\Hokkien Programs\Hokkien Hangul IME\Hokkien Tangliengim IME Pad GitHub Synced Ver"
```

The command imports the desktop files read-only and writes
`tests/fixtures/legacy-ime-parity-reference.json` in this repository. Review
that output before committing it; a changed fixture means either the current
desktop TSV changed or a case was deliberately revised. The legacy backup is
available only to investigate a regression, not as the default fixture source.

The fixtures cover shared text, Lomari, audio, Hangul composition, and Hanri
candidate selection. Composition cases exercise special Hokkien vowels,
backspacing, and tone attachment. Candidate cases make explicitly typed tones
strict while allowing omitted earlier tones, just as the desktop menu does.

## Progress

Completed:

1. Capture desktop parity fixtures.
2. Move TSV indexing, priority Hanri segmentation, exact readings, and longest Hangul-override lookup into `shared/web-ime-core.js`.
3. Make both the Web IME and Dictionary consume that one dictionary index for their Hangul candidate menus.
4. Move the first common audio rules: citation-to-Taipei sandhi and Singapore tone-1 replacement.
5. Match desktop Hangul composition and tone-aware candidate filtering in the shared Web engine, including generated runtime sandhi candidates that stay hidden from dictionary cards.
6. Move the shared Lomari renderer and audio-plan decisions into `shared/web-phonetic-output.js`.
7. Preserve a selected Hanri reading for that occurrence across surrounding edits, and use it consistently for segmentation, Lomari, and audio until the Hanri itself is deleted.
8. Share candidate-popup positioning and the complete browser audio decode, trim, overlap, crossfade, and playback engine between the Dictionary and Web IME.

Next:

1. Bundle the Web interface and shared engine in the active desktop shell while retaining local HTML modes and TSV sync as extensions.
2. Run the cross-platform regression suite and prepare a release baseline.
