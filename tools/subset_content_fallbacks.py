"""Optional maintenance: build licensed nasal-mark and rare-Hanri web fonts."""
import argparse
from pathlib import Path

HANRI_CODEPOINTS = {0x20, 0x20895, 0x23350, 0x24EAA, 0x28468, 0x28617, 0x2C9B0}


def subset_font(source, codepoints, family, output, axes=None):
    from fontTools import subset
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    font = TTFont(source, recalcTimestamp=False)
    if not set(codepoints) <= font.getBestCmap().keys():
        raise ValueError(f'{source} lacks requested glyphs')
    options = subset.Options()
    options.name_IDs = ['*']
    options.name_languages = ['*']
    options.layout_features = ['*']  # Keep ccmp/mark/mkmk and their glyph closure.
    options.hinting = False
    job = subset.Subsetter(options=options)
    job.populate(unicodes=codepoints)
    job.subset(font)
    if axes:
        font = instantiateVariableFont(font, axes, inplace=True)
    names = {1: family, 2: 'Regular', 3: family + ' v1', 4: family,
             6: family.replace(' ', ''), 16: family, 17: 'Regular', 18: family}
    for record in font['name'].names:
        if record.nameID in names:
            record.string = names[record.nameID].encode(record.getEncoding())
    for name_id, value in names.items():
        font['name'].setName(value, name_id, 3, 1, 0x409)
    font.flavor = 'woff2'
    output.parent.mkdir(parents=True, exist_ok=True)
    font.save(output)
    print(output.name, output.stat().st_size)


def main():
    from fontTools.ttLib import TTFont
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('latin_source', type=Path, help='NotoSans[wdth,wght].ttf')
    parser.add_argument('hanri_source', type=Path, help='PlangothicP1-Regular.ttf V2.9.5795')
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/fonts')
    args = parser.parse_args()
    available = TTFont(args.latin_source).getBestCmap().keys()
    latin = (set(range(0x20,0x370)) | set(range(0x1E00,0x1F00)) | {0x25CC}) & available
    assert {0x330,0x25CC,ord('a'),ord('i')} <= latin
    subset_font(args.latin_source, latin, 'Tangliengim Nasal Latin', args.output_dir / 'tangliengim-nasal-latin-v1.woff2', {'wdth':100})
    subset_font(args.hanri_source, HANRI_CODEPOINTS, 'Tangliengim Content Hanri v2', args.output_dir / 'tangliengim-content-hanri-v2.woff2')
    hanri = TTFont(args.output_dir / 'tangliengim-content-hanri-v2.woff2')
    hanri.flavor = None
    hanri.save(args.output_dir / 'tangliengim-content-hanri-v2.ttf')

if __name__ == '__main__':
    main()
