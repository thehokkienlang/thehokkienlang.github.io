"""Generate the human redirect log; --check verifies coverage, order and freshness."""
from __future__ import annotations
import argparse
import csv
import io
from pathlib import Path
from dictionary_schema import REDIRECT_COLUMNS, load_headword_aliases
from dictionary_ranking import read_records
from tangliengim_collation import reading_sort_key

ROOT = Path(__file__).resolve().parents[1]
TSV = ROOT / 'data/dictionary_redirects.tsv'
MARKDOWN = ROOT / 'docs/dictionary-redirects.md'


def render():
    records = read_records(ROOT / 'data/hokkien_hanri_dict.tsv')
    load_headword_aliases(ROOT / 'data/hokkien_hanri_dict.tsv', records)
    targets = {r['entry_id']: r for r in records if r['entry_type'] == 'lexical'}
    with TSV.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        if reader.fieldnames != REDIRECT_COLUMNS:
            raise ValueError('Invalid redirect log columns')
        rows = list(reader)
    seen = set()
    reading_links = set()
    for row in rows:
        if set(row) != set(REDIRECT_COLUMNS) or any(not value or value != value.strip() for value in row.values()):
            raise ValueError(f'Incomplete redirect log row: {row}')
        target = targets.get(row['target_entry_id'])
        if not target or row['kind'] not in ('headword', 'reading'):
            raise ValueError(f'Invalid redirect target or kind: {row}')
        key = (row['kind'], row['source'], row['target_entry_id'])
        if key in seen:
            raise ValueError(f'Duplicate redirect: {key}')
        seen.add(key)
        if row['kind'] == 'reading':
            if row['source'] != row['source_reading']:
                raise ValueError('Reading redirect source must match source_reading')
            reading_links.add((row['source'], target['hanri'], target['reading']))
    expected = {(r['reading'].rstrip('*'), r['hanri'], r['corrected'])
                for r in records if r['entry_type'] == 'correction_alias'}
    if reading_links != expected:
        raise ValueError(f'Redirect log differs from correction rows: {reading_links ^ expected}')
    rows.sort(key=lambda r: (reading_sort_key(r['source_reading']), r['source'], r['kind'], r['target_entry_id']))
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, REDIRECT_COLUMNS, delimiter='\t', lineterminator='\r\n')
    writer.writeheader(); writer.writerows(rows)
    def escape(value):
        return value.replace('|', '\\|').replace('\n', ' ')
    text = ['# Dictionary and IME redirect log', '',
            'Generated from [dictionary_redirects.tsv](../data/dictionary_redirects.tsv). Do not edit this Markdown file directly.', '',
            'Sorted by the original reading using the existing Tangliengim jamo collation (syllables, then tones). '
            'Headword links and nonstandard-reading corrections use the existing dictionary/IME lookup and candidate paths. '
            '“Unknown” dates and missing historical rationales are deliberately not inferred.', '',
            '| Original spelling / input | Original reading | Correct spelling | Correct reading | Type | Reason | Sources | Date | Target ID |',
            '|---|---|---|---|---|---|---|---|---|']
    for row in rows:
        target = targets[row['target_entry_id']]
        values = [row['source'], row['source_reading'], target['hanri'], target['reading'], row['kind'],
                  row['reason'], row['sources'], row['date'], row['target_entry_id']]
        text.append('| ' + ' | '.join(map(escape, values)) + ' |')
    text += ['', '## Updating redirects', '',
             '1. For a reading correction, add the existing `correction_alias` row in the dictionary TSV and a corresponding log row. '
             'For a headword correction, add a `headword` row here pointing to an existing lexical entry ID.',
             '2. Record the reason, sources, and decision date. The corrected spelling and reading are resolved from the target entry, so they cannot drift.',
             '3. Run `python tools/build_redirect_log.py` to sort the TSV and regenerate this log. '
             'The release gate runs `--check` and rejects stale logs, missing reading corrections, or invalid targets.', '']
    return stream.getvalue().encode('utf-8'), '\n'.join(text).encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    tsv, markdown = render()
    if args.check:
        if TSV.read_bytes() != tsv or not MARKDOWN.exists() or MARKDOWN.read_bytes() != markdown:
            raise SystemExit('Redirect log is stale or unsorted. Run python tools/build_redirect_log.py')
        print('Redirect log: coverage, targets, jamo order and Markdown are current.')
    else:
        TSV.write_bytes(tsv); MARKDOWN.write_bytes(markdown)
        print('Updated data/dictionary_redirects.tsv and docs/dictionary-redirects.md')

if __name__ == '__main__':
    main()
