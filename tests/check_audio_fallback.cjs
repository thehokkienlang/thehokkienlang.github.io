// The built player prefers Opus copies and falls back to the WAV masters (audit 1.3).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../shared/web-audio-player.js'), 'utf8');
assert.equal((source.match(/^\s*const COMPRESSED_AUDIO_EXTENSION = "";$/gm) || []).length, 1,
  'the source player must stay WAV-only until the build enables compressed audio');

function buffer(channels, length, sampleRate) {
  const data = Array.from({ length: channels }, () => new Float32Array(length));
  return { numberOfChannels: channels, length, sampleRate, getChannelData: c => data[c],
    copyToChannel: (samples, c) => data[c].set(samples) };
}

async function scenario({ extension, opusDecodes, missingOpus = [] }) {
  const requests = [];
  class AudioContext {
    async resume() {}
    async decodeAudioData(bytes) {
      const kind = Buffer.from(bytes).toString();
      if (kind === 'opus' && !opusDecodes) throw new Error('EncodingError');
      return buffer(1, 4800, 48000);
    }
    createBuffer(...args) { return buffer(...args); }
    createBufferSource() {
      let ended;
      return { connect() {}, stop() {}, addEventListener(_e, callback) { ended = callback; },
        start() { ended(); } };
    }
  }
  const context = vm.createContext({
    AudioContext,
    fetch: async url => {
      requests.push(url);
      const kind = url.endsWith('.opus') ? 'opus' : 'wav';
      if (kind === 'opus' && missingOpus.some(name => url.includes(name))) return { ok: false, status: 404 };
      return { ok: true, arrayBuffer: async () => Uint8Array.from(Buffer.from(kind)).buffer };
    },
  });
  context.window = context;
  const built = source.replace('const COMPRESSED_AUDIO_EXTENSION = "";', `const COMPRESSED_AUDIO_EXTENSION = "${extension}";`);
  vm.runInContext(built, context);
  const player = context.TangliengimWebAudio.createPlayer();
  for (const file of ['/public/audio/ㄱ/ka1.wav', '/public/audio/ㄱ/ka2.wav', '/public/audio/ㄱ/ka3.wav']) {
    await player.play([{ file, tone: '1' }]);
  }
  return requests.map(url => decodeURI(url).replace('/public/audio/ㄱ/', ''));
}

(async () => {
  assert.deepEqual(await scenario({ extension: '', opusDecodes: true }),
    ['ka1.wav', 'ka2.wav', 'ka3.wav'], 'unbuilt pages load WAVs only');
  assert.deepEqual(await scenario({ extension: 'opus', opusDecodes: true }),
    ['ka1.opus', 'ka2.opus', 'ka3.opus'], 'built pages load Opus copies');
  assert.deepEqual(await scenario({ extension: 'opus', opusDecodes: false }),
    ['ka1.opus', 'ka1.wav', 'ka2.wav', 'ka3.wav'], 'a browser that cannot decode Opus switches to WAV after one try');
  assert.deepEqual(await scenario({ extension: 'opus', opusDecodes: true, missingOpus: ['ka2'] }),
    ['ka1.opus', 'ka2.opus', 'ka2.wav', 'ka3.opus'], 'one missing copy falls back for that file only');
  console.log('PASS: Opus preferred on built pages, WAV fallback per browser and per file.');
})().catch(error => { console.error(error); process.exitCode = 1; });
