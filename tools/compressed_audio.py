"""Compressed Opus copies of the recorded syllables for the published site (audit 1.3).

The WAV files in public/audio stay the masters: the desktop IME and every
check use them. The site build writes an .opus copy beside each WAV in
_site/public/audio, and web-audio-player.js uses the copy when the browser
can decode it, falling back to the WAV when it can't.

Opus was chosen over AAC after measuring both on real recordings: Opus copies
decode to exactly the WAV's length and alignment, which the player's fixed
start/end trims and overlap joins depend on, while AAC adds 2-19 ms of
encoder padding. A cache under .cache/ keyed by each WAV's content keeps
repeat builds fast. Run this file directly to check a built site.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTENSION = "opus"
# Changing these settings changes every cache key, so copies are re-encoded.
ENCODER_ARGS = ("-c:a", "libopus", "-b:a", "32k", "-vbr", "on", "-application", "audio")
SETTINGS_KEY = hashlib.sha256(" ".join(ENCODER_ARGS).encode()).hexdigest()[:8]
CACHE = ROOT / ".cache" / "audio-opus"
DECODE_RATE = 48000
MAX_LENGTH_DIFFERENCE_FRAMES = 48  # 1 ms at 48 kHz
MAX_ALIGNMENT_LAG_FRAMES = 2


def ffmpeg() -> str | None:
    executable = shutil.which("ffmpeg")
    if executable:
        return executable
    try:
        import imageio_ffmpeg
    except ImportError:
        return None
    bundled = Path(imageio_ffmpeg.get_ffmpeg_exe())
    return str(bundled) if bundled.is_file() else None


def _encode_one(executable: str, wav: Path, target: Path) -> None:
    key = hashlib.sha256(wav.read_bytes()).hexdigest()[:24]
    cached = CACHE / f"{key}-{SETTINGS_KEY}.{EXTENSION}"
    if not cached.is_file():
        temporary = cached.with_name(cached.name + f".{os.getpid()}.part.{EXTENSION}")
        subprocess.run([executable, "-nostdin", "-loglevel", "error", "-y", "-i", str(wav),
                        *ENCODER_ARGS, str(temporary)], check=True)
        os.replace(temporary, cached)
    shutil.copy2(cached, target)


def write_compressed_copies(audio_root: Path) -> int:
    """Write an .opus copy beside every WAV under audio_root; return how many.

    Returns 0, writing nothing, when ffmpeg is unavailable outside CI, so the
    site keeps serving WAVs. In CI a missing ffmpeg is an error.
    """
    executable = ffmpeg()
    if executable is None:
        if os.environ.get("CI"):
            raise RuntimeError("CI must install ffmpeg to build the compressed audio copies.")
        print("Notice: ffmpeg not found; the site will serve WAV audio only.")
        return 0
    CACHE.mkdir(parents=True, exist_ok=True)
    wavs = sorted(audio_root.rglob("*.wav"))
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        list(pool.map(lambda wav: _encode_one(executable, wav, wav.with_suffix(f".{EXTENSION}")), wavs))
    return len(wavs)


def _decode(executable: str, path: Path):
    import numpy as np
    raw = subprocess.run([executable, "-nostdin", "-loglevel", "error", "-i", str(path), "-f", "f32le",
                          "-ac", "1", "-ar", str(DECODE_RATE), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4")


def _alignment_lag(reference, copy) -> int:
    import numpy as np
    n = min(len(reference), len(copy), DECODE_RATE)  # first second is enough
    a, b = reference[:n], copy[:n]
    window = range(-8 * MAX_ALIGNMENT_LAG_FRAMES, 8 * MAX_ALIGNMENT_LAG_FRAMES + 1)
    return max(window, key=lambda lag: float(np.dot(a[max(0, lag):n + min(0, lag)], b[max(0, -lag):n - max(0, lag)])))


def check_compressed_copies(audio_root: Path) -> list[str]:
    """Every WAV has an Opus copy that decodes to the same length and alignment."""
    executable = ffmpeg()
    if executable is None:
        raise RuntimeError("ffmpeg is needed to check the compressed audio copies.")
    wavs = sorted(audio_root.rglob("*.wav"))
    problems = [f"missing copy: {wav.relative_to(audio_root)}" for wav in wavs
                if not wav.with_suffix(f".{EXTENSION}").is_file()]

    def compare(wav: Path) -> str | None:
        copy = wav.with_suffix(f".{EXTENSION}")
        if not copy.is_file():
            return None
        reference, decoded = _decode(executable, wav), _decode(executable, copy)
        difference = len(decoded) - len(reference)
        if abs(difference) > MAX_LENGTH_DIFFERENCE_FRAMES:
            return f"length differs by {difference} frames: {copy.relative_to(audio_root)}"
        lag = _alignment_lag(reference, decoded)
        if abs(lag) > MAX_ALIGNMENT_LAG_FRAMES:
            return f"shifted by {lag} frames: {copy.relative_to(audio_root)}"
        return None

    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        problems += [problem for problem in pool.map(compare, wavs) if problem]
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio-root", type=Path, default=ROOT / "_site" / "public" / "audio")
    args = parser.parse_args()
    wavs = list(args.audio_root.rglob("*.wav"))
    copies = list(args.audio_root.rglob(f"*.{EXTENSION}"))
    if not copies and ffmpeg() is None and not os.environ.get("CI"):
        print("Notice: no compressed copies and no ffmpeg; the site serves WAV audio only.")
        return 0
    problems = check_compressed_copies(args.audio_root)
    if problems:
        print("\n".join(problems[:20]))
        print(f"FAIL: {len(problems)} compressed audio problems.")
        return 1
    wav_bytes = sum(path.stat().st_size for path in wavs)
    opus_bytes = sum(path.stat().st_size for path in copies)
    print(f"OK: {len(copies)} Opus copies match their WAVs in length and alignment; "
          f"{opus_bytes / 2**20:.1f} MiB instead of {wav_bytes / 2**20:.1f} MiB.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
