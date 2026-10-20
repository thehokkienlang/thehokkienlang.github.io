"""Dictionary-only Simplified Hokkien suggestions for the classic Tk editor.

Matching and incremental segmentation share fixtures with web-ime-core.js.
No Mandarin fields, transliteration tables, or ranking preferences are used.
"""

from __future__ import annotations

from dictionary_schema import canonical_entry_headword


class SimplifiedNormalizationIndex:
    def __init__(self, entries):
        forms = {}
        canonical_forms = set()
        self.trie = {}
        self.max_length = 0
        for entry in entries:
            if not entry.get('active') or entry.get('kind') == 'numeric_override':
                continue
            if entry.get('autoSandhi') or entry.get('auto_sandhi'):
                continue
            source_hanri = entry.get('raw', {}).get('hanri') or entry.get('hanri') or ''
            hanri = canonical_entry_headword(entry.get('hanri') or '')
            source = entry.get('simplified') or ''
            if source == '〃':
                source = source_hanri
            identity = entry.get('raw', {}).get('entry_id') or entry.get('entry_id') or entry.get('id')
            if not hanri or not identity:
                continue
            canonical_forms.add(hanri)
            if not source:
                continue
            targets = forms.setdefault(source, {})
            if source != source_hanri:
                targets.setdefault(hanri, set()).add(identity)
        # Canonical words block conversion; longer Simplified matches still win.
        for hanri in canonical_forms:
            forms[hanri] = {}
        for source, targets in forms.items():
            node = self.trie
            for char in source:
                node = node.setdefault(char, {})
            node[None] = [{'hanri': hanri, 'entryIds': sorted(ids)}
                          for hanri, ids in sorted(targets.items())]
            self.max_length = max(self.max_length, len(source))
        self.size = sum(bool(targets) for targets in forms.values())
        self.ambiguous_count = sum(len(targets) > 1 for targets in forms.values())

    @classmethod
    def from_tsv(cls, path):
        from dictionary_ranking import read_records
        from dictionary_schema import canonical_entry_headword, resolve_dictionary_record
        entries = []
        for raw in read_records(path):
            row = resolve_dictionary_record(raw)
            reading = row.get('corrected') or row.get('reading') or ''
            entries.append({
                'hanri': canonical_entry_headword(row['hanri']),
                'raw': {'hanri': row['hanri']},
                'simplified': row['simplified'],
                'id': row['entry_id'],
                'active': bool(reading and row['hanri']) and not (
                    row.get('corrected') and row['reading'][:1].isdigit()),
                'kind': 'numeric_override' if row['entry_type'] == 'number_pronunciation' else '',
            })
        return cls(entries)

    def match_at(self, text, start):
        node, match = self.trie, None
        for position in range(start, len(text)):
            node = node.get(text[position])
            if node is None:
                break
            if None in node:
                match = {'start': start, 'end': position + 1, 'source': text[start:position + 1],
                         'targets': node[None]}
        return match


class SimplifiedNormalizationSession:
    def __init__(self, index):
        self.index = index
        self.text = ''
        self.matches = []
        self.segments = []

    def update(self, text):
        if text == self.text:
            return False
        previous = self.text
        start = 0
        while start < min(len(previous), len(text)) and previous[start] == text[start]:
            start += 1
        suffix = 0
        while suffix < min(len(previous) - start, len(text) - start) and previous[-1 - suffix] == text[-1 - suffix]:
            suffix += 1
        old_end, new_end = len(previous) - suffix, len(text) - suffix
        offset = new_end - old_end
        cursor = max(0, start - self.index.max_length + 1)
        stable_suffix_start = new_end
        for match in self.segments:
            if match['start'] < cursor < match['end']:
                cursor = match['start']
            if match['start'] < old_end < match['end']:
                stable_suffix_start = max(stable_suffix_start, match['end'] + offset)
        matches = [match for match in self.segments if match['end'] <= cursor]
        unchanged = [{**match, 'start': match['start'] + offset, 'end': match['end'] + offset}
                     for match in self.segments if match['start'] >= old_end]
        next_unchanged = 0
        while cursor < len(text) and self.index.max_length:
            if cursor >= stable_suffix_start:
                while next_unchanged < len(unchanged) and unchanged[next_unchanged]['end'] <= cursor:
                    next_unchanged += 1
                if next_unchanged == len(unchanged) or unchanged[next_unchanged]['start'] >= cursor:
                    matches.extend(unchanged[next_unchanged:])
                    break
            match = self.index.match_at(text, cursor)
            if match:
                matches.append(match)
                cursor = match['end']
            else:
                cursor += 1
        self.text, self.segments = text, matches
        self.matches = [match for match in matches if match['targets']]
        return True

    def replacement(self, match, target, text):
        if (not any(item is match for item in self.matches) or
                not any(item is target for item in match['targets']) or
                text != self.text or text[match['start']:match['end']] != match['source']):
            return None
        return (text[:match['start']] + target['hanri'] + text[match['end']:],
                match['start'] + len(target['hanri']))
