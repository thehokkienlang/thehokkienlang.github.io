"""Sentence cues kept outside audited song bodies; used by build and local CMS."""
from __future__ import annotations

import hashlib
import json
import math
import re
import warnings
from html.parser import HTMLParser
from urllib.parse import urlsplit


class LyricParser(HTMLParser):
    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.body = body
        self.offsets = [0]
        for match in re.finditer('\n', body):
            self.offsets.append(match.end())
        self.lines, self.videos, self.stack = [], [], []
        self.skip_depth = 0
        self.current = None
        self.feed(body)

    def source_offset(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == 'iframe':
            url = urlsplit(attrs.get('src', ''))
            if url.hostname in ('www.youtube.com', 'www.youtube-nocookie.com', 'youtube.com'):
                match = re.fullmatch(r'/embed/([A-Za-z0-9_-]{11})', url.path)
                if match:
                    self.videos.append(match[1])
        # A column marked data-no-lyric-timing (a translation, say) is not part of the recording.
        if tag == 'div' and (self.skip_depth or 'data-no-lyric-timing' in attrs):
            self.skip_depth += 1
        if tag == 'p' and not self.skip_depth:
            self.current = {'start': self.source_offset(), 'text': [], 'label': [], 'lomari': False, 'main': None, 'foundMain': False}
            self.stack = []
        if self.current is None or tag in ('br', 'img', 'hr', 'wbr', 'input', 'source', 'meta', 'link'):
            return
        self.stack.append(tag)
        if tag == 'span':
            # Lines are marked by class since the semantic-markup migration (audit B4);
            # older or pasted markup still uses the WordPress inline styles.
            style = attrs.get('style', '')
            classes = (attrs.get('class') or '').split()
            # A few lines keep hand-sized Lomari (0.61-0.65em), so the size alone cannot identify it.
            if 'lyric-lomari' in classes or re.search(r'font-size\s*:\s*0?\.7em|font-family\s*:\s*calibri', style, re.I):
                self.current['lomari'] = True
            block = {'lyric-line', 'lyric-lomari'} & set(classes) or re.search(r'display\s*:\s*block', style)
            if block and not self.current['foundMain']:
                self.current['main'] = len(self.stack)
                self.current['foundMain'] = True

    def handle_endtag(self, tag):
        if tag == 'div' and self.skip_depth:
            self.skip_depth -= 1
        if self.current is None:
            return
        if tag == 'p':
            end = self.source_offset() + len('</p>')
            if self.current['lomari'] and self.current['label']:
                fingerprint = hashlib.sha256(' '.join(''.join(self.current['text']).split()).encode()).hexdigest()
                self.lines.append({'id': f'line-{len(self.lines) + 1:03d}', 'fingerprint': fingerprint,
                                   'label': ' '.join(''.join(self.current['label']).split()),
                                   'html': self.body[self.current['start']:end],
                                   'startOffset': self.current['start'], 'endOffset': end})
            self.current = None
            self.stack = []
            return
        if self.current['main'] == len(self.stack) and tag == 'span':
            self.current['main'] = None
        if tag in self.stack:
            self.stack = self.stack[:len(self.stack) - 1 - self.stack[::-1].index(tag)]

    def handle_data(self, data):
        if self.current is not None:
            self.current['text'].append(data)
            if self.current['main'] is not None and not self.current['lomari'] and not {'rt', 'rp'} & set(self.stack):
                self.current['label'].append(data)


def song_lines(record):
    if record.get('type') != 'songs':
        raise ValueError('Lyric timing is available for song pages only.')
    parsed = LyricParser(record.get('body', ''))
    if len(parsed.videos) != 1 or not parsed.lines:
        raise ValueError('A timed song needs exactly one YouTube video and lyric paragraphs with Lomari.')
    return parsed.videos[0], parsed.lines


def timing_path(root, record):
    identity = str(record.get('id', ''))
    if not re.fullmatch(r'[A-Za-z0-9_-]+', identity):
        raise ValueError('Invalid song identity.')
    return root / 'data' / 'lyric-timings' / (identity + '.json')


def blank_timing(record):
    video, lines = song_lines(record)
    return {'schemaVersion': 1, 'songId': record['id'], 'videoId': video, 'status': 'draft',
            'cues': [{'id': line['id'], 'fingerprint': line['fingerprint'], 'start': None, 'end': None} for line in lines]}


def reconcile_timing(record, data):
    """Carry authored times onto the current lyric structure without discarding them."""
    expected = blank_timing(record)
    if not isinstance(data, dict) or data.get('schemaVersion') != expected['schemaVersion'] or data.get('songId') != expected['songId']:
        raise ValueError('The timing file does not belong to this song.')
    stored = data.get('cues')
    if not isinstance(stored, list) or any(not isinstance(cue, dict) for cue in stored):
        raise ValueError('The timing file has no recoverable sentence timings.')

    unused = set(range(len(stored)))
    reconciled = []
    for index, line in enumerate(expected['cues']):
        def find(match):
            return next((candidate for candidate in sorted(unused) if match(stored[candidate])), None)

        source_index = find(lambda cue: cue.get('id') == line['id'] and cue.get('fingerprint') == line['fingerprint'])
        if source_index is None:
            source_index = find(lambda cue: cue.get('fingerprint') == line['fingerprint'])
        if source_index is None:
            source_index = find(lambda cue: cue.get('id') == line['id'])
        if source_index is None and index in unused:
            source_index = index

        source = stored[source_index] if source_index is not None else {}
        if source_index is not None:
            unused.remove(source_index)
        reconciled.append({**line, 'start': source.get('start'), 'end': source.get('end')})

    status = data.get('status') if data.get('status') in ('draft', 'reviewed') else 'draft'
    if status == 'reviewed' and any(cue['start'] is None or cue['end'] is None for cue in reconciled):
        status = 'draft'
    return {**expected, 'status': status, 'cues': reconciled}


def validate_timing(record, data):
    expected = blank_timing(record)
    if not isinstance(data, dict) or any(data.get(key) != expected[key] for key in ('schemaVersion', 'songId', 'videoId')):
        raise ValueError('The timing file does not match this song/video.')
    if data.get('status') not in ('draft', 'reviewed'):
        raise ValueError('Choose draft or reviewed timing status.')
    cues = data.get('cues')
    if not isinstance(cues, list) or len(cues) != len(expected['cues']):
        raise ValueError('The lyric line count changed. Reload and review the timing assignments.')
    previous_end, complete = 0, True
    clean = {**expected, 'status': data['status'], 'cues': []}
    for cue, line in zip(cues, expected['cues']):
        if not isinstance(cue, dict) or any(cue.get(key) != line[key] for key in ('id', 'fingerprint')):
            raise ValueError('A lyric line changed. Reload and review its timing before saving.')
        start, end = cue.get('start'), cue.get('end')
        values = [value for value in (start, end) if value is not None]
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) for value in values):
            raise ValueError(f'{cue["id"]}: enter valid sentence times.')
        if start is None or end is None:
            complete = False
        if (any(not 0 <= value <= 86400 for value in values)
                or (start is not None and end is not None and start >= end)
                or (values and values[0] < previous_end)):
            raise ValueError(f'{cue["id"]}: times must increase, with end after start and no overlapping sentences.')
        if values:
            previous_end = values[-1]
        clean['cues'].append({**line, 'start': start, 'end': end})
    if data['status'] == 'reviewed' and not complete:
        raise ValueError('Time every lyric line before marking the song reviewed.')
    return clean


def decorate_lyrics(root, record, body):
    """Only generated markup changes; sidecars cannot contain executable HTML."""
    path = timing_path(root, record)
    if not path.is_file():
        return body
    try:
        data = validate_timing(record, json.loads(path.read_text(encoding='utf-8')))
    except ValueError as error:
        warnings.warn(f'{path.name}: synchronized lyrics omitted: {error}', stacklevel=2)
        return body
    parsed = LyricParser(body)
    _, original = song_lines(record)
    if len(parsed.lines) != len(original):
        raise ValueError('Song presentation changed the lyric line count.')
    for line in reversed(parsed.lines):
        pos = line['startOffset']
        # Add an attribute rather than a wrapper so paragraph/ruby layout is unchanged.
        body = body[:pos] + body[pos:].replace('<p', f'<p data-lyric-id="{line["id"]}"', 1)
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    return ('<div class="lyric-sync-controls" hidden><label><input type="checkbox" role="switch" data-follow-lyrics> '
            '<span data-site-text="Follow lyrics">Follow lyrics</span></label><span data-lyric-status role="status"></span></div>' + body +
            f'<script type="application/json" id="lyric-timing-data">{payload}</script>')
