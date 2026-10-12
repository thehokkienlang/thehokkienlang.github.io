"""Optional font maintenance: create the licensed single-character Hanri fallback."""

import argparse
from pathlib import Path

FAMILY = 'Tangliengim Hanri Fallback'
CODEPOINTS = (0x20, 0x24EAA)  # Retain the BMP space mapping for Windows font loading.


def main():
    from fontTools import subset
    from fontTools.ttLib import TTFont

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Official PlangothicP1-Regular.ttf, release V2.9.5795')
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/fonts')
    args = parser.parse_args()
    font = TTFont(args.source, recalcTimestamp=False)
    if not set(CODEPOINTS) <= font.getBestCmap().keys():
        raise ValueError('Source font does not cover the required Hanri')
    options = subset.Options()
    options.name_IDs = ['*']
    options.name_languages = ['*']
    options.name_legacy = True
    options.hinting = False
    job = subset.Subsetter(options=options)
    job.populate(unicodes=CODEPOINTS)
    job.subset(font)
    names = {1: FAMILY, 2: 'Regular', 3: FAMILY + ' V2.9.5795 subset',
             4: FAMILY + ' Regular', 6: 'TangliengimHanriFallback-Regular',
             16: FAMILY, 17: 'Regular', 18: FAMILY + ' Regular'}
    for record in font['name'].names:
        if record.nameID in names:
            record.string = names[record.nameID].encode(record.getEncoding())
    for name_id, value in names.items():
        font['name'].setName(value, name_id, 3, 1, 0x409)
    font['name'].setName('Plangothic P1 subset and renamed for Tangliengim on 2026-10-12; '
                         'U+24EAA only. Licensed under SIL Open Font License 1.1.', 10, 3, 1, 0x409)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for flavor, extension in ((None, 'ttf'), ('woff2', 'woff2')):
        font.flavor = flavor
        target = args.output_dir / f'tangliengim-hanri-fallback-v1.{extension}'
        font.save(target)
        print(f'{target.name}: {target.stat().st_size} bytes')


if __name__ == '__main__':
    main()
