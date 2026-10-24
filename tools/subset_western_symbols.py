"""Build self-hosted Noto Sans Latin, punctuation and TLI tone-mark subsets."""

import argparse
from pathlib import Path

from subset_content_fallbacks import subset_font


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
            output = args.output_dir / f"{filename}-{weight}-v2.woff2"
            subset_font(source, points & available, family, output)
            with TTFont(output, recalcTimestamp=False) as font:
                style = "Regular" if weight == "regular" else "Bold"
                names = {2: style, 3: f"{family} {style} v2", 4: f"{family} {style}",
                         6: f"{family.replace(' ', '')}-{style}-v2", 17: style, 18: f"{family} {style}"}
                for record in font["name"].names:
                    if record.nameID in names:
                        record.string = names[record.nameID].encode(record.getEncoding())
                font.save(output)


if __name__ == "__main__":
    main()
