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

## Conjoining Hangul for content pages

`tangliengim-conjoining-hangul-{regular,bold}-v1.woff2` supply the Hangul
conjoining-jamo blocks U+1100–11FF, U+A960–A97F and U+D7B0–D7FF. The content
site and its title readings use this family before device fonts. Ordinary
precomposed Hangul, Hanri, Latin and tone marks keep their existing fonts.
The fonts are served locally; no Google Fonts connection is needed.

The subset retains the `ljmo`, `vjmo`, `tjmo` and contextual shaping tables,
including the substituted glyphs they require. Merely supplying isolated
jamo glyphs would not fix composition. Both regular and bold are supplied
for lyric bodies and headings. The original Unicode lyrics are unchanged.
`ᄁᅷ` already has an initial consonant and needs no filler; `ᅟᅷ` uses the
choseong filler because it has no initial. Adding a filler inside `ᄁᅷ`
breaks the existing cluster instead of repairing it.

- Upstream: [Noto Sans KR, Google Fonts](https://github.com/google/fonts/tree/b38c5c93af322c45f633e17ac440ec1e6c94d489/ofl/notosanskr).
- Input: `NotoSansKR[wght].ttf`, SHA-256 `194018e6b2b293a7964f037b25c0249ce1418bc9ab3c971060a03aa57861e252`.
- License: SIL Open Font License 1.1, copied unchanged to `OFL-NotoSansKR.txt`.
- Modified 2026-10-22: subset conjoining jamo, instantiate weights 400/700,
  remove hints, rename to **Tangliengim Conjoining Hangul**, encode as WOFF2.
  Original copyright and license records are retained.

Optional reproduction (not a build or runtime dependency):

```sh
python -m pip install 'fonttools[woff]'
python tools/subset_hangul_fallback.py /path/to/NotoSansKR.ttf
```
