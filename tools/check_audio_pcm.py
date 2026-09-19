"""Compare the shared player's assembled samples with the desktop WAV routine."""

import argparse
import ast
import base64
import json
import math
import struct
import subprocess
import tempfile
import wave
from array import array
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, default=ROOT / 'desktop/Hokkien Tangliengim IME Pad.py')
    args = parser.parse_args()
    # Load only the original DSP functions and constants, without starting Tk.
    names = {'crossfade_pcm16', 'fade_out_pcm16', 'speed_up_pcm_frames',
             'overlap_pcm16_audio_units', 'concatenate_wav_segments'}
    tree = ast.parse(args.reference.read_text(encoding='utf-8-sig'))
    nodes = [node for node in tree.body if (
        isinstance(node, ast.FunctionDef) and node.name in names
    ) or (
        isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and any(
            isinstance(target, ast.Name) and target.id.startswith('AUDIO_') for target in node.targets
        )
    )]
    reference = {'array': array, 'sys': sys, 'wave': wave, 'Path': Path}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(args.reference), 'exec'), reference)
    cases = []
    with tempfile.TemporaryDirectory(prefix='tangliengim-pcm-') as folder:
        scratch = Path(folder)
        sources = {}
        for rate, channels in [(22050, 1), (44100, 1), (48000, 2)]:
            source = scratch / f'{rate}-{channels}.wav'
            samples = [int(12000 * math.sin(frame * (channel + 1) * 0.073))
                       for frame in range(int(rate * 0.913)) for channel in range(channels)]
            with wave.open(str(source), 'wb') as output:
                output.setparams((channels, 2, rate, 0, 'NONE', 'not compressed'))
                output.writeframes(struct.pack(f'<{len(samples)}h', *samples))
            sources[source.name] = source
            cases.extend([
                (f'{rate}-single', [{'file': source.name, 'tone': '3'}]),
                (f'{rate}-connected', [
                    {'file': source.name, 'tone': '3', 'trimEnd': True},
                    {'file': source.name, 'tone': '4', 'trimStart': True, 'trimEnd': True, 'shortOverlapFinal': True},
                    {'file': source.name, 'tone': '3', 'trimStart': True},
                ]),
                (f'{rate}-nasal', [
                    {'file': source.name, 'tone': '3', 'lFinal': True, 'trimEnd': True},
                    {'file': source.name, 'tone': '3', 'lFinal': True, 'trimStart': True},
                ]),
                (f'{rate}-cluster', [
                    {'file': source.name, 'tone': '3', 'englishClusterHelper': True, 'trimEnd': True},
                    {'file': source.name, 'tone': '3', 'trimStart': True},
                ]),
                (f'{rate}-punctuation', [
                    {'file': source.name, 'tone': '3'}, {'file': source.name, 'tone': '4'},
                ]),
            ])
        for stem in ['li2', 'si3', 'teh1', 'khau3']:
            matches = list((ROOT / 'public/audio').rglob(stem + '.wav'))
            assert len(matches) == 1, stem
            sources[stem] = matches[0]
        cases.append(('recorded-phrase', [
            {'file': stem, 'tone': tone, 'trimStart': i > 0, 'trimEnd': i < 3,
             'shortOverlapFinal': stem == 'teh1'}
            for i, (stem, tone) in enumerate([('li2', '2'), ('si3', '3'), ('teh1', '1'), ('khau3', '3')])
        ]))
        fixtures = []
        for name, segments in cases:
            native = []
            for i, segment in enumerate(segments):
                speed = 1.0
                if len(segments) > 1 and not segment.get('englishClusterHelper'):
                    if segment['tone'] == '4':
                        speed = reference['AUDIO_TONE4_SPEED_FACTOR']
                    elif segment.get('lFinal') and (
                        (i > 0 and segments[i - 1].get('lFinal')) or
                        (i + 1 < len(segments) and segments[i + 1].get('lFinal'))
                    ):
                        speed = reference['AUDIO_L_FINAL_SPEED_FACTOR']
                    else:
                        speed = reference['AUDIO_MULTI_SYLLABLE_SPEED_FACTOR']
                native.append((sources[segment['file']], segment.get('trimStart', False),
                               segment.get('trimEnd', False), speed, segment.get('lFinal', False),
                               segment.get('shortOverlapFinal', False), segment.get('englishClusterHelper', False)))
            output_path = scratch / 'expected.wav'
            assert reference['concatenate_wav_segments'](native, output_path), name
            fixtures.append({'name': name, 'segments': segments,
                             'expected': base64.b64encode(output_path.read_bytes()).decode('ascii')})
        payload = {'sources': {key: base64.b64encode(path.read_bytes()).decode('ascii')
                               for key, path in sources.items()}, 'cases': fixtures}
        subprocess.run(['node', str(ROOT / 'tools/check_audio_pcm.cjs')],
                       input=json.dumps(payload), text=True, check=True, cwd=ROOT)


if __name__ == '__main__':
    main()
