"""Compressed audio copies for the published site (audit 1.3)."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_site
import compressed_audio


class CompressedAudioTests(unittest.TestCase):
    def test_player_prefers_opus_and_falls_back_to_wav(self):
        from node_runtime import node_environment
        node, env = node_environment()
        subprocess.run([node, str(ROOT / "tests/check_audio_fallback.cjs")], env=env, check=True)

    def test_build_enables_compressed_audio_in_the_built_player_only(self):
        source = (ROOT / "shared/web-audio-player.js").read_text(encoding="utf-8")
        self.assertEqual(len(build_site.AUDIO_FORMAT_LINE.findall(source)), 1)
        with tempfile.TemporaryDirectory() as directory:
            player = Path(directory) / "web-audio-player.js"
            player.write_text(source, encoding="utf-8")
            build_site.enable_compressed_audio(player, compressed_audio.EXTENSION)
            built = player.read_text(encoding="utf-8")
            self.assertIn('const COMPRESSED_AUDIO_EXTENSION = "opus";', built)
            self.assertNotIn('const COMPRESSED_AUDIO_EXTENSION = "";', built)

    def test_built_site_has_a_matching_opus_copy_for_every_wav(self):
        audio = ROOT / "_site/public/audio"
        if compressed_audio.ffmpeg() is None or not any(audio.rglob("*.opus")):
            self.skipTest("needs ffmpeg and a built site with compressed copies")
        wavs = sorted(audio.rglob("*.wav"))
        self.assertTrue(wavs)
        self.assertEqual([wav for wav in wavs if not wav.with_suffix(".opus").is_file()], [])
        player = (ROOT / "_site/shared/web-audio-player.js").read_text(encoding="utf-8")
        self.assertIn('const COMPRESSED_AUDIO_EXTENSION = "opus";', player)


if __name__ == "__main__":
    unittest.main()
