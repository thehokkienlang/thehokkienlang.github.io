"""Locate Node for desktop launches that do not inherit a terminal's PATH."""
from __future__ import annotations

import os
import shutil
from pathlib import Path


def node_environment(environ=None):
    env = dict(os.environ if environ is None else environ)
    configured = env.get('TANGLIENGIM_NODE', '').strip().strip('"')
    candidates = []
    if configured:
        candidates.append(Path(configured))
    else:
        on_path = shutil.which('node', path=env.get('PATH', ''))
        if on_path:
            candidates.append(Path(on_path))
        for key in ('ProgramFiles', 'ProgramFiles(x86)'):
            if env.get(key):
                candidates.append(Path(env[key]) / 'nodejs/node.exe')
        if env.get('LOCALAPPDATA'):
            candidates.append(Path(env['LOCALAPPDATA']) / 'Programs/nodejs/node.exe')
        home = Path(env.get('USERPROFILE') or str(Path.home()))
        candidates.append(home / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
    for candidate in candidates:
        if candidate.is_file():
            executable = candidate.resolve()
            env['TANGLIENGIM_NODE'] = str(executable)
            env['PATH'] = str(executable.parent) + os.pathsep + env.get('PATH', '')
            return str(executable), env
    raise FileNotFoundError(
        'Node.js was not found. Install Node.js LTS and reopen the Dictionary Editor, '
        'or set TANGLIENGIM_NODE to the full path of node.exe. '
        'Your local dictionary entries are still saved.'
    )
