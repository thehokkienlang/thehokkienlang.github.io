# Scalable Pronunciation Ruby

`shared/web-ruby.css` owns pronunciation geometry for content, titles, song
lists, homepage selections, and dictionary headwords. Do not add page-specific
pixel offsets for these readings.

- Readings are 55% of the base text size, with a 1.15 reading line height.
- The base wrapper has a one-em line height, independent of paragraph spacing.
- The reading's bottom overlaps the base box by 0.15 of the reading's em.
  This compensates for the font's built-in vertical space and scales with the base text.
- Readings are horizontally centered and do not widen the underlying text.
- A block title beneath a label must reserve the annotation's height as well
  as its normal gap. The homepage story title reserves `var(--tli-ruby-size)`
  plus `0.1em` clearance (approximately 2px at its current size), without moving
  the reading relative to the Hanri.
- Bopomofo keeps a smaller 37% ratio to accommodate its longer readings, but
  uses the same relative positioning rule.

The content renderer classifies converted ruby as `tli-reading-ruby` or
`tli-tone-ruby`. Tone-only annotations above Hangul retain their separate tone
rules; they are not pronunciation readings. Legacy inline geometry remains in
authored source for recovery/export, but is overridden on the website.

Use `tools/check_content_rendering.py` with Chromium and WebKit to verify the
relative geometry, layout, and preserved text. The shared settings, rather than
individual page offsets, should be adjusted if a future typography change
requires recalibration.
