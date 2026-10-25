# Shared Noto Sans Symbols and Branding

## v3.2.1 Hanri glyph additions

`tli-hanri-v321-tc.woff2` contains 㜁, 𡚸, 𨑨 and 迌 from the installed Noto Sans TC;
`tli-hanri-v321-sc.woff2` supplies 摕, 䆀 and 䭕 from Noto Sans SC, since the local TC
source does not cover it. CSS applies these fonts only to those characters,
on both content pages and dictionary/IME surfaces. Ordinary Hanri remain
unchanged. 𨑨 and 迌 deliberately share the same TC outlines rather than mixing
Plangothic and Noto regional radical shapes. The classic Pad privately loads
the matching TC TTF and applies it to these four characters; SC tags cover 摕/䆀/䭕.
The matching `-bold` files supply real 700-weight outlines; regular files use
400-weight outlines. These are renamed, unhinted static subsets for reliable
cross-engine weight selection; embedded copyright and SIL
OFL 1.1 records are preserved. The Noto license is included in this directory.
Reproduce with `tools/subset_v321_hanri.py NotoSansTC-VF.ttf NotoSansSC-VF.ttf`.

`tli-noto-sans-{regular,bold}-v2.woff2` are renamed subsets of Noto Sans.
The shared brand template uses these same files on content pages, Dictionary
and IME. The punctuation face selects Western-width punctuation and the entire
TLI tone set, including U+A788, without borrowing CJK or Calibri tone glyphs.
Latin combining marks and nasalization are retained with their shaping tables.
Hanri and Hangul continue to use their script-specific fonts. Explicitly
fullwidth Chinese punctuation keeps its original glyph and semantics.

- Sources: installed `NotoSans-Regular.ttf` and `NotoSans-Bold.ttf`.
- SHA-256 (regular): `150d72c26777d9232384756ee88bfcac1b055eda0563c38ce2c6e1de21595de0`.
- SHA-256 (bold): `e34be52df70ee791393df83d5196bd29ce4b79e535c681a41270d6981e248cdf`.
- License: SIL OFL 1.1, in `OFL-NotoSans.txt`; embedded copyright retained.
- Modified 2026-10-24: glyph subset, hints removed, family renamed to
  **TLI Noto Sans**, encoded as WOFF2. No glyph outlines or widths changed.
  Version 2 gives Regular and Bold distinct internal PostScript identities and
  matching style names; CSS declares static 400/700 faces for WebKit portability.
  The punctuation aliases use `tli-noto-symbols-{regular,bold}-v2.woff2`, separate
  subsets with unique internal identities and the same Noto Sans glyph outlines.
  This avoids WebKit cache collisions between full Latin and Unicode-scoped faces.

Optional reproduction with FontTools installed:

```sh
python tools/subset_western_symbols.py /path/to/NotoSans-Regular.ttf /path/to/NotoSans-Bold.ttf
```

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

## Nasalized Latin and 𣍐 in content pages

`tangliengim-nasal-latin-v1.woff2` is a renamed Noto Sans subset with the
Latin, combining-mark and dotted-circle glyphs needed for `◌̰`, `â̰`, `ḭ́`,
and related Lomari text. It retains `ccmp`, `mark`, and `mkmk` positioning and
the variable weight axis, so regular and bold stacked marks work together.
The content renderer assigns a font to the **whole marked grapheme**, not
just U+0330: a mark and its base letter must shape in the same font. Only
nasalized graphemes receive this font; the original text and other letters'
font selection remain unchanged. Attributes and source JSON are unchanged.

- Upstream: [Noto Sans, Google Fonts](https://github.com/google/fonts/tree/8b0a1d0f5983c89bc2b93f1b5fb55f9e252744b5/ofl/notosans).
- Source: `NotoSans[wdth,wght].ttf`, SHA-256 `bfb7bb691513f12e734dc346c03a03f784912432d7e3fa8e56efcf906fe86b3d`.
- License: unchanged `OFL-NotoSans.txt` (SIL OFL 1.1).

`tangliengim-content-hanri-v2.woff2` supplies `𣍐`, `𤺪`, `𠢕`, `𨑨`, `𨘗`, and
`𬦰` to the content site. Harmonisation 3.2 adds the last four glyphs for
cross-platform rendering without relying on device fonts. It is derived from the
same Plangothic P1 V2.9.5795 release and license documented above, renamed
**Tangliengim Content Hanri v2**, and restricted to those characters by CSS.
The dictionary and classic Pad's existing single-glyph font is unchanged.

The dictionary and Web IME now reuse the v2 WOFF2 through a Unicode-scoped
fallback face for its additional glyphs. The classic Windows Pad privately
loads the matching `tangliengim-content-hanri-v2.ttf` and tags only these six
supplementary characters. The original single-glyph files remain available;
ordinary Hanri retain Noto Sans TC and 㩼 retains Noto Sans SC.

Modified 2026-10-25; the previous v1 asset is retained. Optional reproduction:

```sh
python -m pip install 'fonttools[woff]'
python tools/subset_content_fallbacks.py /path/to/NotoSans.ttf /path/to/PlangothicP1-Regular.ttf
```
