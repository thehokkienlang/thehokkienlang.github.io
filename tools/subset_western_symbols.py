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
    for weight, source in (("regular", args.regular), ("bold", args.bold)):
        with TTFont(source) as font:
            available = set(font.getBestCmap())
        if not required <= available:
            raise ValueError(f"{source} is missing punctuation or tone glyphs")
        subset_font(source, requested & available, "TLI Noto Sans", args.output_dir / f"tli-noto-sans-{weight}-v1.woff2")


if __name__ == "__main__":
    main()
