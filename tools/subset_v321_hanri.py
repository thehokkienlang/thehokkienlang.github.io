"""Build character-scoped Noto fallbacks for the v3.2.1 Hanri assignments."""
import argparse
from pathlib import Path
from subset_content_fallbacks import subset_font


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tc_source', type=Path)
    parser.add_argument('sc_source', type=Path)
    args = parser.parse_args()
    output = Path(__file__).resolve().parents[1] / 'assets/fonts'
    for weight, suffix in ((400, ''), (700, '-bold')):
        subset_font(args.tc_source, {0x20, 0x3701, 0x216B8, 0x28468, 0x8FCC}, 'TLI Hanri v321 TC' + suffix,
                    output / f'tli-hanri-v321-tc{suffix}.woff2', {'wght': weight})
        subset_font(args.sc_source, {0x20, 0x6455, 0x4180, 0x4B55}, 'TLI Hanri v321 SC' + suffix,
                    output / f'tli-hanri-v321-sc{suffix}.woff2', {'wght': weight})
    from fontTools.ttLib import TTFont
    font = TTFont(output / 'tli-hanri-v321-tc.woff2')
    font.flavor = None
    font.save(output / 'tli-hanri-v321-tc.ttf')


if __name__ == '__main__':
    main()
