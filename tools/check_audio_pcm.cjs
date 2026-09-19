// Exercise the real player's fetch, processing, assembly and start path.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const fixtures = JSON.parse(fs.readFileSync(0, 'utf8'));

function buffer(channels, length, sampleRate) {
  const data = Array.from({ length: channels }, () => new Float32Array(length));
  return {
    numberOfChannels: channels, length, sampleRate,
    getChannelData: channel => data[channel],
    copyToChannel: (samples, channel) => data[channel].set(samples),
  };
}

function decode(wav) {
  let format;
  let samples;
  for (let offset = 12; offset + 8 <= wav.length;) {
    const name = wav.toString('ascii', offset, offset + 4);
    const length = wav.readUInt32LE(offset + 4);
    if (name === 'fmt ') format = wav.subarray(offset + 8, offset + 8 + length);
    if (name === 'data') samples = wav.subarray(offset + 8, offset + 8 + length);
    offset += 8 + length + (length % 2);
  }
  assert.equal(format.readUInt16LE(0), 1, 'PCM WAV');
  assert.equal(format.readUInt16LE(14), 16, '16-bit PCM');
  const channels = format.readUInt16LE(2);
  const result = buffer(channels, samples.length / (channels * 2), format.readUInt32LE(4));
  for (let i = 0; i < result.length; i += 1) {
    for (let channel = 0; channel < channels; channel += 1) {
      result.getChannelData(channel)[i] = samples.readInt16LE((i * channels + channel) * 2) / 32768;
    }
  }
  return result;
}

(async () => {
  let played;
  class AudioContext {
    async resume() {}
    async decodeAudioData(bytes) { return decode(bytes); }
    createBuffer(...args) { return buffer(...args); }
    createBufferSource() {
      let ended;
      return {
        connect() {}, stop() {},
        addEventListener(_event, callback) { ended = callback; },
        start() { played = this.buffer; ended(); },
      };
    }
  }
  const context = vm.createContext({
    AudioContext,
    fetch: async file => ({ok: true, arrayBuffer: async () => Buffer.from(fixtures.sources[file], 'base64')}),
  });
  context.window = context;
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../shared/web-audio-player.js'), 'utf8'), context);
  const player = context.TangliengimWebAudio.createPlayer();
  for (const fixture of fixtures.cases) {
    await player.play(fixture.segments);
    const expected = decode(Buffer.from(fixture.expected, 'base64'));
    assert.equal(played.sampleRate, expected.sampleRate, fixture.name);
    assert.equal(played.length, expected.length, `${fixture.name}: legacy frame count`);
    let maximumError = 0;
    for (let channel = 0; channel < expected.numberOfChannels; channel += 1) {
      const actual = played.getChannelData(channel);
      const reference = expected.getChannelData(channel);
      for (let i = 0; i < actual.length; i += 1) {
        maximumError = Math.max(maximumError, Math.abs(actual[i] - reference[i]));
      }
    }
    // Python rounds to PCM16 after each mix; Web Audio keeps floating-point samples.
    assert.ok(maximumError <= 4 / 32768, `${fixture.name}: sample error ${maximumError}`);
  }
  console.log(`OK: ${fixtures.cases.length} shared playback waveforms match desktop timing and samples.`);
})().catch(error => { console.error(error); process.exitCode = 1; });
