# Shared IME Release Baseline

Established on 2026-09-19 after the shared-engine migration.

## Canonical ownership

- GitHub owns the common dictionary data, Hangul composition, Hanri candidates, Lomari rendering, sandhi planning, audio planning/playback, candidate popup behaviour, and Web UI.
- The desktop shell serves those canonical files directly from the checkout.
- Desktop-only HTML modes and guarded TSV syncing are exposed through localhost bridge endpoints and continue to use the mature Python implementation.
- `--classic-ui` remains an operational fallback.
- The legacy desktop file outside `Hokkien Tangliengim IME Pad GitHub Synced Ver` remains untouched.

## Baseline inventory

- 5,413 generated runtime dictionary entries
- 2,713 active TSV rows
- 1,440 referenced audio recordings
- Public applications: `/ime/` and `/dictionary/`

## Release gate

Run the complete local gate from the repository root:

```powershell
python -X utf8 tools/check_release.py
```

The source-only form is used by the Windows and Linux CI matrix:

```powershell
python -X utf8 tools/check_release.py --source-only
```

The gate checks Python and JavaScript syntax, shared Web behaviour, desktop-shell routing, the checked-in legacy parity fixture, the generated site, routes, dictionary data, and audio references.
