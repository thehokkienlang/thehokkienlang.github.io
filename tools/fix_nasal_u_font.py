"""Correct Noto Sans's above-mark anchor for U+1E75 (u with tilde below)."""
from copy import deepcopy
from pathlib import Path


def fix_nasal_u_anchor(font):
    cmap = font.getBestCmap()
    plain, nasal, macron = (cmap[code] for code in (0x75, 0x1E75, 0x304))
    changed = 0
    for lookup in font['GPOS'].table.LookupList.Lookup:
        for table in lookup.SubTable:
            if not hasattr(table, 'BaseCoverage'):
                continue
            if not {plain, nasal} <= set(table.BaseCoverage.glyphs) or macron not in table.MarkCoverage.glyphs:
                continue
            mark_class = table.MarkArray.MarkRecord[table.MarkCoverage.glyphs.index(macron)].Class
            base = table.BaseArray.BaseRecord[table.BaseCoverage.glyphs.index(plain)]
            target = table.BaseArray.BaseRecord[table.BaseCoverage.glyphs.index(nasal)]
            # A below-letter nasal mark must not reserve space above the letter.
            target.BaseAnchor[mark_class] = deepcopy(base.BaseAnchor[mark_class])
            changed += 1
    if changed != 1:
        raise ValueError(f'Expected one nasal-u anchor table, found {changed}')


def main():
    from fontTools.ttLib import TTFont
    directory = Path(__file__).resolve().parents[1] / 'assets/fonts'
    for weight in ('regular', 'bold'):
        with TTFont(directory / f'tli-noto-sans-{weight}-v2.woff2', recalcTimestamp=False) as font:
            fix_nasal_u_anchor(font)
            for record in font['name'].names:
                if record.nameID in (3, 6):
                    record.string = record.toUnicode().replace('v2', 'v3').encode(record.getEncoding())
            output = directory / f'tli-noto-sans-{weight}-v3.woff2'
            font.save(output)
            print(output.name)


if __name__ == '__main__':
    main()
