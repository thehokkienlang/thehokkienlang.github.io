"""Build portable TC content faces, retaining the existing rare-glyph fallbacks."""
import argparse
import tempfile
from pathlib import Path

from subset_content_fallbacks import subset_font


def main():
    from fontTools.ttLib import TTFont
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--menu-source', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    text = ''.join(path.read_text(encoding='utf-8') for path in (root/'content').rglob('*.json'))
    points = {ord(char) for char in text if 0x3400 <= ord(char) <= 0x9FFF or 0x20000 <= ord(char) <= 0x2EBEF}
    with TTFont(args.source) as font:
        points &= font.getBestCmap().keys()
    for weight in (400, 700):
        subset_font(args.source, points | {32}, f'TLI Content TC {weight}',
                    root/f'assets/fonts/tli-content-tc-{weight}-v1.woff2', {'wght': weight})
    if args.menu_source:
        text += (root/'data/hokkien_hanri_dict.tsv').read_text(encoding='utf-8')
        menu_points = {ord(char) for char in text if 0x3400 <= ord(char) <= 0x9FFF or 0x20000 <= ord(char) <= 0x2EBEF}
        with TTFont(args.source) as font:
            tc_points = menu_points & font.getBestCmap().keys()
        with TTFont(args.menu_source) as font:
            extra_points = (menu_points - tc_points) & font.getBestCmap().keys()
        assert ord('𣍐') in extra_points
        output = root/'assets/fonts/tli-menu-hanri-v1.woff2'
        from fontTools.merge import Merger
        with tempfile.TemporaryDirectory() as folder:
            sources = []
            for i, (source, points, axes) in enumerate(((args.source, tc_points, {'wght':400}), (args.menu_source, extra_points, None))):
                path = Path(folder)/f'{i}.woff2'
                subset_font(source, points, f'TLI Menu Part {i}', path, axes)
                with TTFont(path) as font:
                    font.flavor = None
                    for tag in ('vhea', 'vmtx', 'VORG'):
                        if tag in font:
                            del font[tag]
                    font['OS/2'].version = 5
                    font['OS/2'].usLowerOpticalPointSize = 0
                    font['OS/2'].usUpperOpticalPointSize = 3276.75
                    font.save(path.with_suffix('.ttf'))
                sources.append(str(path.with_suffix('.ttf')))
            font = Merger().merge(sources)
            for record in font['name'].names:
                if record.nameID in (1, 3, 4, 6, 16, 18):
                    record.string = ('TLIMenuHanri' if record.nameID == 6 else 'TLI Menu Hanri').encode(record.getEncoding())
            assert all(ord(c) in font.getBestCmap() for c in '天愛情𣍐透迌𨑨')
            font.save(output.with_suffix('.ttf'))
            font.flavor = 'woff2'
            font.save(output)


if __name__ == '__main__':
    main()
