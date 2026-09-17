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

The first fixture group covers shared text, Lomari, and audio behaviour. Jamo
composition needs controller-level fixtures because converter functions alone
do not model the IME rule that a digit after a standalone jamo remains literal.

## Implementation Order

1. Capture legacy fixtures.
2. Move TSV indexing and longest-match lookup into the shared engine.
3. Move Hangul composition and candidates.
4. Move tone, Lomari, Taipei/Singapore sandhi, and audio plans.
5. Make Web IME and Dictionary consume the engine.
6. Bundle that same Web interface and engine into the active desktop shell.
7. Keep desktop HTML modes and TSV sync as local extensions that consume shared engine analysis.
