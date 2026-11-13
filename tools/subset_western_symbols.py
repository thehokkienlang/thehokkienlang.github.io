"""Build self-hosted Noto Sans Latin, punctuation and TLI tone-mark subsets."""

import argparse
from pathlib import Path

from subset_content_fallbacks import subset_font

TONE_2, TONE_4 = 0x02CB, 0x02CA  # ˋ, ˊ
# Version of each output family; the symbols font is v3 since its tone 4 mark is redrawn.
VERSIONS = {"tli-noto-sans": "v2", "tli-noto-symbols": "v3"}


# How much wider (bottom) and narrower (top) the tone 4 stroke is than tone 2's, so its ink
# "settles" toward the bottom of the stroke.
TONE_4_WEIGHT = {"bottom": 1.0, "top": 1.0}  # 1.0 keeps tone 2's own stroke, simply flipped


def tone_4_from_tone_2(font, bottom=TONE_4_WEIGHT["bottom"], top=TONE_4_WEIGHT["top"]):
    """Redraw the tone 4 mark from tone 2: mirrored left to right, turned 180°, ink settled low.

    Mirroring and turning flip ˋ upside down within its own box, so tone 4 rises ↗ with tone 2's
    shape, width and spacing. The stroke is then widened toward its bottom and narrowed toward
    its top (about the line through the middle of its two ends), so it is not top-heavy.
    """
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen

    cmap = font.getBestCmap()
    tone_2, tone_4 = cmap[TONE_2], cmap[TONE_4]
    glyph = font["glyf"][tone_2]
    glyph.recalcBounds(font["glyf"])
    y_min, y_max = glyph.yMin, glyph.yMax
    flipped = DecomposingRecordingPen(font.getGlyphSet())
    font.getGlyphSet()[tone_2].draw(TransformPen(flipped, (1, 0, 0, -1, 0, y_min + y_max)))

    points = [point for _op, args in flipped.value for point in args if point]
    def middle(edge_y):
        xs = [x for x, y in points if abs(y - edge_y) < 1]
        return (min(xs) + max(xs)) / 2
    bottom_middle, top_middle = middle(y_min), middle(y_max)

    def settle(point):
        x, y = point
        t = (y - y_min) / (y_max - y_min)
        centre = bottom_middle + (top_middle - bottom_middle) * t
        return round(centre + (x - centre) * (bottom + (top - bottom) * t)), round(y)

    pen = TTGlyphPen(font.getGlyphSet())
    for op, args in flipped.value:
        getattr(pen, op)(*[settle(point) if point else point for point in args])
    font["glyf"][tone_4] = pen.glyph()
    font["hmtx"][tone_4] = font["hmtx"][tone_2]


def main():
    from fontTools.ttLib import TTFont

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("regular", type=Path)
    parser.add_argument("bold", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "assets/fonts")
    args = parser.parse_args()
    required = {ord(character) for character in "'\".,;:!?\u2019\u02c6\u02cb\u02ca\u02c9\u02c7\u02cd\u02ce\u02cf\ua788"}
    requested = set(range(0x20, 0x370)) | set(range(0x1E00, 0x1F00)) | set(range(0x2000, 0x2070)) | {0x25CC, 0xA788}
    symbols = (set(range(0x21, 0x30)) | set(range(0x3A, 0x41)) | set(range(0x5B, 0x61)) |
               set(range(0x7B, 0x7F)) | set(range(0x2C6, 0x2D0)) | set(range(0x2010, 0x2028)) |
               set(range(0x2030, 0x205F)) | {0xA1, 0xA7, 0xAB, 0xB6, 0xB7, 0xBB, 0xBF, 0x2EC, 0xA788})
    for weight, source in (("regular", args.regular), ("bold", args.bold)):
        with TTFont(source) as font:
            available = set(font.getBestCmap())
        if not required <= available:
            raise ValueError(f"{source} is missing punctuation or tone glyphs")
        for filename, family, points in (("tli-noto-sans", "TLI Noto Sans", requested),
                                          ("tli-noto-symbols", "TLI Noto Symbols", symbols)):
            version = VERSIONS[filename]
            output = args.output_dir / f"{filename}-{weight}-{version}.woff2"
            subset_font(source, points & available, family, output)
            with TTFont(output, recalcTimestamp=False) as font:
                style = "Regular" if weight == "regular" else "Bold"
                names = {2: style, 3: f"{family} {style} {version}", 4: f"{family} {style}",
                         6: f"{family.replace(' ', '')}-{style}-{version}", 17: style, 18: f"{family} {style}"}
                for record in font["name"].names:
                    if record.nameID in names:
                        record.string = names[record.nameID].encode(record.getEncoding())
                if filename == "tli-noto-symbols":
                    tone_4_from_tone_2(font)
                font.save(output)


if __name__ == "__main__":
    main()
