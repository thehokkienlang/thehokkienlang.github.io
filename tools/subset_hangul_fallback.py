"""Subset Noto Sans KR syllables and conjoining-jamo shaping tables."""
import argparse
from pathlib import Path

FAMILY = 'Tangliengim Hangul'
CODEPOINTS = ({0x20, 0x200C, 0x200D} | set(range(0x1100, 0x1200)) |
              set(range(0xA960, 0xA980)) | set(range(0xAC00, 0xD7A4)) |
              set(range(0xD7B0, 0xD800)))


def main():
    from fontTools import subset
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/fonts')
    args = parser.parse_args()
    font = TTFont(args.source, recalcTimestamp=False)
    options = subset.Options()
    options.layout_features = ['*']  # Includes ljmo/vjmo/tjmo and contextual glyph closure.
    options.name_IDs = ['*']
    options.name_languages = ['*']
    options.hinting = False
    job = subset.Subsetter(options=options)
    job.populate(unicodes=CODEPOINTS)
    job.subset(font)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for weight, style in ((400, 'Regular'), (700, 'Bold')):
        instance = instantiateVariableFont(font, {'wght': weight}, inplace=False)
        names = {1: FAMILY, 2: style, 3: FAMILY + ' ' + style + ' v2', 4: FAMILY + ' ' + style,
                 6: 'TangliengimHangul-' + style, 16: FAMILY, 17: style, 18: FAMILY + ' ' + style}
        for record in instance['name'].names:
            if record.nameID in names:
                record.string = names[record.nameID].encode(record.getEncoding())
        for name_id, value in names.items():
            instance['name'].setName(value, name_id, 3, 1, 0x409)
        instance['name'].setName('Noto Sans KR subset with precomposed Hangul and conjoining shaping; renamed for Tangliengim. SIL OFL 1.1.', 10, 3, 1, 0x409)
        instance.flavor = 'woff2'
        target = args.output_dir / f'tangliengim-hangul-{style.lower()}-v2.woff2'
        instance.save(target)
        print(target.name, target.stat().st_size)

if __name__ == '__main__':
    main()
