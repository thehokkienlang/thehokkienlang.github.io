"""Record exact, reversible post-v3.2 edits already authored in Git and v3.2.1."""
import difflib
import json
import subprocess
from pathlib import Path
from content_harmonisation import apply_edits, digest, replay_followups, restore_body

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True).stdout.decode('utf-8')


def difference(before, after, reason):
    old, new = before.splitlines(keepends=True), after.splitlines(keepends=True)
    positions = [0]
    for line in old:
        positions.append(positions[-1] + len(line))
    edits = [{"start": positions[a], "end": positions[b], "before": ''.join(old[a:b]),
              "after": ''.join(new[c:d]), "rule": reason}
             for kind, a, b, c, d in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes()
             if kind != 'equal']
    assert apply_edits(before, edits) == after
    return {"beforeSha256": digest(before), "afterSha256": digest(after), "reason": reason, "edits": edits}


def main():
    path = ROOT / 'docs/harmonisation-3.2-audit.json'
    audit = json.loads(path.read_text(encoding='utf-8'))
    patch = json.loads((ROOT / 'docs/harmonisation-3.2.1-audit.json').read_text(encoding='utf-8'))
    changed = []
    for file, entry in audit['records'].items():
        current = json.loads((ROOT / file).read_text(encoding='utf-8'))['body']
        expected = entry.get('followUps', [{}])[-1].get('afterSha256', entry['afterSha256'])
        if digest(current) == expected:
            continue
        previous = json.loads(git('show', 'HEAD:' + file))['body']
        if digest(previous) != expected:
            for revision in git('log', '--format=%H', '--', file).splitlines():
                original = json.loads(git('show', revision + ':' + file))['body']
                if digest(original) == expected:
                    break
            else:
                raise ValueError('Cannot find the exact historical reviewed body: ' + file)
            entry.setdefault('followUps', []).append(difference(original, previous, 'Authored post-v3.2 edits already committed before the v3.2.1 patch'))
        if current != previous:
            reviewed = patch['records'][file]
            assert digest(previous) == reviewed['beforeSha256']
            entry.setdefault('followUps', []).append({key: reviewed[key] for key in ('beforeSha256', 'afterSha256', 'edits')})
            entry['followUps'][-1]['reason'] = 'Author-confirmed Hanri assignments; docs/harmonisation-3.2.1-audit.json'
        restore_body(current, entry)
        changed.append(file)
    path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    patch_changes = []
    for file, entry in patch['records'].items():
        current = json.loads((ROOT / file).read_text(encoding='utf-8'))['body']
        expected = entry.get('followUps', [{}])[-1].get('afterSha256', entry['afterSha256'])
        if digest(current) == expected:
            continue
        for revision in git('log', '--format=%H', '--', file).splitlines():
            original = json.loads(git('show', revision + ':' + file))['body']
            if digest(original) == expected:
                break
        else:
            raise ValueError('Cannot find the exact historical reviewed v3.2.1 body: ' + file)
        entry.setdefault('followUps', []).append(difference(
            original, current, 'Author-approved post-v3.2.1 spelling and reading corrections'))
        from harmonise_content_v321 import restore
        restore(current, entry)
        patch_changes.append(file)
    if patch_changes:
        (ROOT / 'docs/harmonisation-3.2.1-audit.json').write_text(
            json.dumps(patch, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Recorded reversible follow-ups for', len(changed), 'pages')
    print('Recorded reversible v3.2.1 follow-ups for', len(patch_changes), 'pages')


if __name__ == '__main__':
    main()
