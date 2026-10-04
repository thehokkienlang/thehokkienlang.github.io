"""Apply the reviewed second-pass manifest to blank Mandarin metadata only.

This is a one-time data migration, not a translation or ranking engine. New or
changed lexical rows require fresh review rather than inheriting these decisions.
"""

import argparse
from collections import Counter
import csv
import io
import json
from pathlib import Path
import unicodedata

if __package__:
    from .dictionary_schema import DICTIONARY_COLUMNS, inherited_storage, is_comment_record
    from .simplified_lookup import converter
else:
    from dictionary_schema import DICTIONARY_COLUMNS, inherited_storage, is_comment_record
    from simplified_lookup import converter

ROOT = Path(__file__).resolve().parents[1]
GUARD_FIELDS = ('entry_id', 'hanri', 'reading', 'entry_type', 'english')
CONFIDENCE_LEVELS = ('HIGH', 'MEDIUM', 'LOW', 'NOT_APPLICABLE')


def completed_rows(rows, decisions):
    """Validate all decisions before returning a new, order-preserving row list."""
    if tuple(rows[0]) != DICTIONARY_COLUMNS:
        raise ValueError('Expected the current canonical ten-column dictionary')
    by_id = {item['entry_id']: item for item in decisions}
    if len(by_id) != len(decisions):
        raise ValueError('Duplicate entry ID in the review manifest')
    result = [list(rows[0])]
    seen = set()
    for values in rows[1:]:
        record = dict(zip(DICTIONARY_COLUMNS, values))
        decision = by_id.get(record.get('entry_id'))
        if not values or is_comment_record(record) or decision is None:
            result.append(list(values))
            continue
        if len(values) != len(DICTIONARY_COLUMNS):
            raise ValueError('Malformed dictionary row')
        entry_id = record['entry_id']
        if entry_id in seen:
            raise ValueError('Duplicate dictionary entry ID: ' + entry_id)
        seen.add(entry_id)
        for name in GUARD_FIELDS:
            if record[name] != decision[name]:
                raise ValueError(f'Reviewed source changed: {entry_id} {name}')
        confidence = decision['confidence']
        if confidence not in CONFIDENCE_LEVELS:
            raise ValueError('Unknown review confidence: ' + confidence)
        trad = decision['mandarin_trad']
        if confidence in ('LOW', 'NOT_APPLICABLE'):
            if trad:
                raise ValueError('Unresolved decision must not contain a translation')
            result.append(list(values))
            continue
        if not trad or '〃' in trad or unicodedata.normalize('NFC', trad) != trad:
            raise ValueError('Reviewed equivalent must be a nonempty NFC resolved value')
        simp = unicodedata.normalize('NFC', converter('t2s').convert(trad))
        wanted = dict(mandarin_trad=inherited_storage(trad, record['hanri']),
                      mandarin_simp=inherited_storage(simp, trad))
        for name, value in wanted.items():
            if record[name] and record[name] != value:
                raise ValueError(f'Refusing to overwrite populated {name}: {entry_id}')
            record[name] = record[name] or value
        result.append([record[name] for name in DICTIONARY_COLUMNS])
    missing = by_id.keys() - seen
    if missing:
        raise ValueError('Reviewed entries no longer exist: ' + ', '.join(sorted(missing)))
    return result


def review_report(decisions):
    counts = Counter(item['confidence'] for item in decisions)
    resolved = [item for item in decisions if item['confidence'] in ('HIGH', 'MEDIUM')]
    counts['examined'] = len(decisions)
    counts['new_trad_ditto'] = sum(item['mandarin_trad'] == item['hanri'] for item in resolved)
    counts['new_trad_explicit'] = len(resolved) - counts['new_trad_ditto']
    counts['new_simp_ditto'] = sum(converter('t2s').convert(item['mandarin_trad']) == item['mandarin_trad'] for item in resolved)
    counts['new_simp_explicit'] = len(resolved) - counts['new_simp_ditto']
    lines = ['# Mandarin lookup second-pass review', '',
        '## Method', '',
        'Reviewed the 1,698 formerly unresolved lexical/input entries and 10 non-lexical numeral rows. Existing populated Mandarin pairs were preserved.', '',
        'Primary reference: [English Wiktionary](https://en.wiktionary.org/), accessed 2026-10-04. Public MediaWiki revisions were checked for all 1,594 unique unresolved Hanri-only expressions (1,392 pages available; 202 missing). Existing Hokkien readings, English, entry types and related lexical context were also reviewed. No reference archive is a runtime dependency.', '',
        'Chinese etymology/pronunciation blocks were considered separately: Mandarin pronunciation in one block does not authenticate a Min-only sense in another. Dialect-only labels were not used as Mandarin attestation. Literary/regional Mandarin meanings remain eligible. Traditional/Simplified pointer pages or missing evidence were handled with lexical context, not automatically classified LOW.', '',
        'HIGH means a reviewed compatible shared Mandarin sense. MEDIUM includes clear Hokkien-to-Mandarin equivalents and shared expressions with coverage gaps, register differences, or noisy component-generated English. Those are populated and optional spot-checks, not failures. A compatible relevant sense is sufficient; unrelated secondary senses and exact English phrasing are not gates.', '',
        'The versioned manifest records reviewed decisions by existing entry_id, guarded by headword, reading, type and English. It is a one-time audit, not a general rule copying arbitrary future Hanri into Mandarin. Source links and revision IDs document the checked pages; missing/redirect-only coverage does not imply Mandarin attestation. Wiktionary text is not copied into the TSV.', '',
        'Mandarin Simplified uses the existing pinned OpenCC t2s converter. This completion tool changes only the two Mandarin columns. Separately, user-authorized English corrections and completed manual reviews are recorded with exact old/new values and references in [english-gloss-corrections.json](english-gloss-corrections.json). Completed review-sheet merges are logged in [mandarin-manual-review-completion.json](mandarin-manual-review-completion.json). The reviewed manifest guards the current English values. Hokkien simplified, IDs, order, Hanri/readings, correction aliases and priorities remain unchanged.', '',
        '## Counts', '', '| Metric | Rows |', '| --- | ---: |']
    lines.extend(f'| {name} | {value} |' for name, value in counts.items())
    for confidence, title in (
        ('HIGH', 'Automatically resolved - HIGH confidence'),
        ('MEDIUM', 'Automatically resolved - MEDIUM confidence (optional spot-check)'),
        ('LOW', 'Manual review - LOW confidence only'),
        ('NOT_APPLICABLE', 'Not applicable'),
    ):
        group = [item for item in decisions if item['confidence'] == confidence]
        lines.extend(['', f'## {title}', '', f'{len(group)} entries.', ''])
        if confidence == 'HIGH':
            columns = ('line', 'entry_id', 'hanri', 'mandarin_trad', 'source', 'revision')
        else:
            columns = ('line', 'entry_id', 'hanri', 'reading', 'english', 'mandarin_trad', 'reason', 'source', 'revision')
        lines.append('| ' + ' | '.join(columns) + ' |')
        lines.append('| ' + ' | '.join('---' for _ in columns) + ' |')
        for item in group:
            cells = []
            for name in columns:
                value = str(item.get(name) or '').replace('|', '\\|').replace('\n', ' ')
                if name == 'source' and value:
                    value = f'[Wiktionary]({value})'
                cells.append(value)
            lines.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(lines) + '\n', dict(counts)


def complete(path, manifest, report):
    original_bytes = path.read_bytes()
    rows = list(csv.reader(io.StringIO(original_bytes.decode('utf-8'), newline=''), delimiter='\t'))
    decisions = json.loads(manifest.read_text(encoding='utf-8'))['decisions']
    updated = completed_rows(rows, decisions)
    assert len(rows) == len(updated)
    immutable = [i for i, name in enumerate(DICTIONARY_COLUMNS) if name not in ('mandarin_trad', 'mandarin_simp')]
    for before, after in zip(rows, updated):
        assert len(before) == len(after)
        assert all(before[i] == after[i] for i in immutable if i < len(before))
        for name in ('mandarin_trad', 'mandarin_simp'):
            i = DICTIONARY_COLUMNS.index(name)
            if i < len(before) and before[i]:
                assert before[i] == after[i]
    output = io.StringIO(newline='')
    csv.writer(output, delimiter='\t', lineterminator='\r\n').writerows(updated)
    payload = output.getvalue().encode('utf-8')
    if payload != original_bytes:
        path.write_bytes(payload)
    text, counts = review_report(decisions)
    report.write_text(text, encoding='utf-8')
    return counts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'data/hokkien_hanri_dict.tsv')
    parser.add_argument('--manifest', type=Path, default=ROOT / 'docs/mandarin-second-pass-decisions.json')
    parser.add_argument('--report', type=Path, default=ROOT / 'docs/mandarin-lookup-review.md')
    args = parser.parse_args()
    print(complete(args.input, args.manifest, args.report))
