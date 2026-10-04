"""One-time, conservative Mandarin metadata migration; never guesses missing senses."""

import argparse
import csv
import gzip
import io
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from dictionary_schema import (
    DICTIONARY_COLUMNS, PRE_MANDARIN_COLUMNS, inherited_storage, is_comment_record,
)
from simplified_lookup import converter

ROOT = Path(__file__).resolve().parents[1]

# Explicit semantic equivalents, not script conversion. Disputed/component-only
# English glosses are deliberately excluded and remain in the review report.
EQUIVALENTS = {
    '家己': '自己', '鉸': '剪', '鉸刀': '剪刀', '鉸頭毛': '剪頭髮',
    '虼蚻': '蟑螂', '艱': '艱難', '艱苦': '辛苦', '甘願': '願意',
    '講': '說', '囝': '孩子', '囝兒': '孩子們', '今仔日': '今天',
    '明仔日': '明天', '轉厝': '回家', '樓跤': '樓下', '內衫': '內衣',
    '白目': '不識相; 討人厭', '兵衫': '軍服', '目': '眼睛',
    '目尾': '眼角', '目滓': '眼淚', '目睭': '眼睛', '母囝': '母親和孩子',
    '散食': '貧窮', '衫': '衣服', '衫褲': '衣服', '啥': '什麼',
    '啥人': '誰', '啥貨': '什麼', '雙跤': '雙腳', '小可仔': '一點兒',
    '阿公仔': '爺爺', '蚵仔煎': '蚵仔煎', '為啥物': '為什麼',
    '食': '吃', '食麵': '吃麵', '食飽': '吃飽', '食飯': '吃飯',
    '食屎': '吃屎', '食醋': '吃醋', '鳥仔': '小鳥', '煮食': '做飯',
    '一點仔': '一點兒', '一目': '一眼', '菜市仔': '菜市場', '穿衫': '穿衣服',
    '𤆬': '帶領; 帶', '厝': '房子', '厝內': '家裡; 妻子',
    '厝內人': '妻子; 家人', '厝邊頭尾': '鄰居; 周圍', '手機仔': '手機',
    '跤': '腳', '跤踏': '踩; 踏', '跤踏車': '自行車', '跤步': '腳步',
    '跤頭趺': '膝蓋', '徛': '站', '乞食': '乞討', '趁': '賺',
    '歹': '壞', '歹囝': '壞孩子', '歹勢': '害羞; 不好意思', '歹運': '壞運氣',
    '歹款': '不像樣; 不當行為', '歹看': '難看', '好囝': '好孩子',
    '好食': '好吃', '好歹': '好壞', '到尾仔': '最後; 終於',
    '哪裡': '哪裡', '數念': '想念',
    '佮': '和', '到今': '至今', '交陪': '陪伴', '狗屎': '狗屎',
    '蚼蟻': '螞蟻', '寄': '寄; 送', '京': '首都', '件': '件',
    '驚': '害怕', '驚驚': '害怕', '驚人': '嚇人', '驚惶': '害怕',
    '顧': '照顧', '孤孤單單': '孤單', '顧人怨': '惹人厭',
    '故意': '故意', '故鄉': '故鄉', '各人': '每個人; 大家',
    '國父': '國父', '公媽': '祖父母', '家後': '妻子', '高中': '高中',
    '懸': '高', '雞卵': '雞蛋', '街路': '街道', '雞肉': '雞肉',
    '街市': '市場', '粿條': '粿條', '幾若擺': '幾次', '規暝': '整夜',
    '規个': '整個', '光映映': '閃亮', '고ˉ비ˉ店': '咖啡店',
}

# Only short input overrides use these complete, unambiguous English senses.
# A compound with a dubious component-generated gloss cannot inherit them.
OVERRIDE_GLOSSES = {
    'coffee': '咖啡', 'with; together': '和; 一起', 'again': '再',
    'I; me': '我', 'me': '我', 'who': '誰', 'bread; roti': '麵包',
    'we; us (inclusive of the listener)': '我們', 'all': '全部', 'you': '你',
    'you; your': '你; 你的', 'bad': '壞', 'wife': '妻子', 'not': '不',
    "won't": '不會', 'cannot; will not be able to': '不能; 不會',
    'is': '是', 'ah': '啊', 'like this; like that': '這樣; 那樣',
    "’s; possessive particle; attributive particle": '的',
    'can; be able to': '能; 可以', 'is not': '不是', 'him': '他',
    'he; she; they': '他; 她; 他們', 'they; their': '他們; 他們的',
    'woman': '女人', 'here': '這裡', 'this': '這', 'that': '那',
    'anyhow': '隨便', 'to play; to have a good time': '玩; 遊玩',
    'more; even more': '更', 'there': '那裡', 'so; that much': '那麼',
    'give': '給',
    'we (inclusive of listener)': '我們', "won't; will not": '不會',
    'they, their': '他們; 他們的', 'so; that (much)': '那麼',
    'I; my; we (exclusive of listener)': '我; 我的; 我們',
}


def english_key(value):
    text = value.lower().strip()
    text = re.sub(r'\([^)]*\)', '', text).strip()
    text = re.sub(r'^(?:to |a |an |the )', '', text)
    return re.sub(r'\s+', ' ', text.replace('-', ' ')).strip(' .')


def reference_senses(path):
    senses = defaultdict(set)
    with gzip.open(path, 'rt', encoding='utf-8') as handle:
        for line in handle:
            match = re.match(r'^(\S+) \S+ \[[^]]+\] /(.*)/$', line.rstrip())
            if not match:
                continue
            headword, definitions = match.groups()
            # References, surnames and variant annotations are not definitions.
            for definition in definitions.split('/'):
                if not re.match(r'^(?:variant of |surname |CL:|see also |abbr\. for )', definition):
                    senses[headword].add(english_key(definition))
                    for synonym in re.split(r'; |, ', definition):
                        senses[headword].add(english_key(synonym))
    return senses


def translation(record, reference):
    word, english = record['hanri'], record['english']
    if record['entry_type'] == 'number_pronunciation':
        return '', 'Input-only numeral pronunciation; Mandarin metadata not applicable'
    if not english:
        return '', 'Missing English/context; Mandarin sense requires review'
    if word in EQUIVALENTS:
        return EQUIVALENTS[word], 'Explicit Hokkien semantic equivalent'
    if record['entry_type'] == 'hangul_override' and english in OVERRIDE_GLOSSES:
        return OVERRIDE_GLOSSES[english], 'Explicit complete override gloss'
    glosses = [english_key(part) for part in english.split(';') if part.strip()]
    if glosses and all(part in reference.get(word, set()) for part in glosses):
        return word, 'Shared written word; every English sense confirmed in CC-CEDICT'
    return '', 'No complete semantic match; specialised, ambiguous or inconsistent source gloss'


def migrate(path, reference_path, report_path, fill_missing=False):
    original = list(csv.reader(io.StringIO(path.read_text(encoding='utf-8'), newline=''), delimiter='\t'))
    columns = tuple(original[0])
    if columns != PRE_MANDARIN_COLUMNS and not (fill_missing and columns == DICTIONARY_COLUMNS):
        raise ValueError('This one-time migration requires the original eight-column header')
    reference = reference_senses(reference_path)
    rows = [list(DICTIONARY_COLUMNS)]
    review, methods = [], Counter()
    counts = Counter()
    for line, values in enumerate(original[1:], start=2):
        if not values:
            rows.append(values)
            continue
        record = dict(zip(columns, values))
        if is_comment_record(record):
            rows.append([record.get(name, '') for name in DICTIONARY_COLUMNS])
            continue
        trad, method = translation(record, reference)
        if record.get('mandarin_trad'):
            existing_trad = record['hanri'] if record['mandarin_trad'] == '〃' else record['mandarin_trad']
            if trad != existing_trad:
                method = 'Preserved existing Mandarin value'
            trad = existing_trad
        trad = unicodedata.normalize('NFC', trad)
        simp = unicodedata.normalize('NFC', converter('t2s').convert(trad)) if trad else ''
        record['simplified'] = inherited_storage(record['simplified'], record['hanri'])
        record['mandarin_trad'] = record.get('mandarin_trad') or inherited_storage(trad, record['hanri'])
        record['mandarin_simp'] = record.get('mandarin_simp') or inherited_storage(simp, trad)
        rows.append([record.get(name, '') for name in DICTIONARY_COLUMNS])
        counts['rows'] += 1
        counts['mandarin_trad_populated'] += bool(trad)
        counts['mandarin_simp_populated'] += bool(simp)
        for name in ('simplified', 'mandarin_trad', 'mandarin_simp'):
            counts[name + '_ditto'] += record[name] == '〃'
        methods[method] += 1
        if not trad and record['entry_type'] != 'number_pronunciation':
            review.append([str(line), record['entry_id'], record['hanri'], record['reading'], record['entry_type'], record['english'], method])
    # Assert preservation by named fields, including comments at their positions.
    for before, after in zip(original[1:], rows[1:]):
        if not before:
            assert not after
            continue
        a, b = dict(zip(columns, before)), dict(zip(DICTIONARY_COLUMNS, after))
        assert all(a.get(name, '') == b.get(name, '') for name in PRE_MANDARIN_COLUMNS if name != 'simplified')
        assert b.get('simplified', '') == a.get('simplified', '') or (b.get('simplified') == '〃' and a.get('simplified') == a.get('hanri'))
    output = io.StringIO(newline='')
    csv.writer(output, delimiter='\t', lineterminator='\r\n').writerows(rows)
    path.write_bytes(output.getvalue().encode('utf-8'))
    counts['manual_review'] = len(review)
    lines = ['# Mandarin metadata review', '',
        'Uncertain fields remain blank. Numeral input-only rows are not applicable (10 rows), not translation failures.', '',
        'Shared-written-word matches require every existing semicolon-separated English sense to match a full CC-CEDICT sense. This conservative test may leave valid equivalents for review; it does not concatenate translations of individual Hanri characters.', '',
        'Reference: [CC-CEDICT, distributed by MDBG](https://www.mdbg.net/chinese/dictionary?page=cc-cedict), accessed 2026-10-04; CC BY-SA 4.0. Reference archive supplied to this migration is not a runtime dependency. Script conversion uses the existing pinned OpenCC t2s dictionaries.', '',
        '## Counts', '', *(f'- {key}: {value}' for key, value in counts.items()), '',
        '## Population methods', '', *(f'- {key}: {value}' for key, value in methods.items()), '',
        '## Rows requiring review', '',
        '| TSV line | entry_id | Headword | Reading | Type | Existing English | Reason |',
        '| --- | --- | --- | --- | --- | --- | --- |']
    lines.extend('| ' + ' | '.join(cell.replace('|', '\\|') for cell in row) + ' |' for row in review)
    report_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return dict(counts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'data/hokkien_hanri_dict.tsv')
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--fill-missing', action='store_true', help='Populate only blank Mandarin fields in the current ten-column TSV')
    parser.add_argument('--report', type=Path, default=ROOT / 'docs/mandarin-lookup-review.md')
    args = parser.parse_args()
    print(migrate(args.input, args.reference, args.report, args.fill_missing))
