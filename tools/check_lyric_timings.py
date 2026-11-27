"""Fail when a lyric timing file no longer matches its song page (read-only).

The build leaves the follow-lyrics player out of such a page with only a warning,
so that local previews keep working. This check stops that reaching the site.
"""

from __future__ import annotations

import json
from pathlib import Path

from lyric_timing import blank_timing, validate_timing

ROOT = Path(__file__).resolve().parents[1]

REPAIR = """To repair a song:
  1. Run `npm run editor` and open the Website Editor.
  2. Under Website Pages, select the song and choose Lyric timing.
     The editor carries the saved times over to the current lyric lines.
  3. Check the times, especially if lines or the video were added, removed,
     reordered or replaced: a time can land on the wrong line.
  4. Choose Save timings locally, then run this check again."""


def first_mismatched_line(record, data):
    """The first line ID whose cue is missing, extra, misplaced or out of date."""
    expected = blank_timing(record)['cues']
    stored = data.get('cues') if isinstance(data, dict) else None
    if not isinstance(stored, list):
        return None
    for index, line in enumerate(expected):
        cue = stored[index] if index < len(stored) else None
        if not isinstance(cue, dict) or any(cue.get(key) != line[key] for key in ('id', 'fingerprint')):
            return line['id']
    if len(stored) > len(expected):
        extra = stored[len(expected)]
        return extra.get('id') if isinstance(extra, dict) else None
    return None


def timing_problems(root=ROOT):
    """One message for every timing file the build would not use."""
    songs = {}
    for path in sorted((root / 'content' / 'songs').glob('*.json')):
        record = json.loads(path.read_text(encoding='utf-8'))
        songs[record.get('id')] = (path.relative_to(root).as_posix(), record)
    problems = []
    for path in sorted((root / 'data' / 'lyric-timings').glob('*.json')):
        sidecar = path.relative_to(root).as_posix()
        # The build looks a timing file up by the song's ID.
        if path.stem not in songs:
            problems.append(f'{sidecar}: no song page has the ID "{path.stem}".')
            continue
        page, record = songs[path.stem]
        data = line = None
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            validate_timing(record, data)
        except ValueError as error:
            if data is not None:
                try:
                    line = first_mismatched_line(record, data)
                except ValueError:
                    pass  # the page itself cannot be timed; the error already says why
            where = f'\n  first mismatched line: {line}' if line else ''
            problems.append(f'{record.get("title")} ({page})\n  timing file: {sidecar}{where}\n  {error}')
    return problems


def main(root=ROOT):
    problems = timing_problems(root)
    if problems:
        print(f'{len(problems)} lyric timing file(s) do not match, so the site would lose the follow-lyrics player:\n')
        print('\n\n'.join(problems))
        print('\n' + REPAIR)
        return 1
    count = len(list((root / 'data' / 'lyric-timings').glob('*.json')))
    print(f'OK: {count} lyric timing files match their song pages.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
