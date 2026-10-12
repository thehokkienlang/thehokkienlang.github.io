# Hanri glyph fallback

`tangliengim-hanri-fallback-v1.woff2` and its TTF companion contain U+24EAA
(`𤺪`) and a technical space mapping required by Windows. CSS/tags apply it only
to `𤺪`; all other characters retain their existing fonts. The Web IME,
Dictionary input/menu/headword and Local shared web shell use the same WOFF2.
The Windows classic Pad privately loads the TTF into its own process and tags
only the selected character; it does not install fonts or edit the registry.

The glyph is from **Plangothic P1**, official release **V2.9.5795**,
`PlangothicP1-Regular.ttf`. Plangothic supplements Source Han Sans, making it a
closer sans-serif match to Noto Sans TC than Ming/Song-style fallback fonts.

- Source/release: https://github.com/Fitzgerald-Porthmouth-Koenigsegg/Plangothic_Project/releases/tag/V2.9.5795
- Font license: SIL Open Font License 1.1, included unmodified in `OFL.txt`.
- Copyright/attribution from the original font is retained in both font files.
- Modified 2026-10-12: subset to U+24EAA, renamed to **Tangliengim Hanri Fallback**
  to avoid upstream reserved font names, converted to WOFF2 for Web use.

Reproduction is optional maintenance, not a runtime/build dependency:

```sh
python -m pip install 'fonttools[woff]'
python tools/subset_hanri_fallback.py /path/to/PlangothicP1-Regular.ttf
```

The shared CSS `unicode-range` limits the fallback to this glyph. Keep the same
family name in the source-maintenance script and classic font tag. Original font
files are not checked in; the small derived files and license are sufficient for
ordinary site/Local operation, including without external font services.
