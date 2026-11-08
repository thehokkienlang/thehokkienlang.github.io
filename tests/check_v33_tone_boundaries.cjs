const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const context = { window: {} };
for (const file of ['web-ime-core.js', 'web-phonetic-output.js']) {
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../shared', file), 'utf8'), context);
}
const core = context.window.TangliengimImeCore;
const phonetic = context.window.TangliengimPhoneticOutput;
const entries = [
  { hanri: '가가’가', reading: '가1가1가1' },
  { hanri: '甲', reading: '가1' },
  { hanri: '’ᄅᆤ', reading: '’ᄅᆤ2' },
  { hanri: '’뽀', reading: '’뽀4' },
  { hanri: '’나', reading: '’나5' }, // Explicit dictionary overrides follow desktop rules.
];
const apostropheEntries = [
  { hanri: '轉’래', reading: '등2’래' },
  { hanri: '有影’뽀', reading: '우1얄2’뽀4' },
];
const findHanriEntry = (text, index) => entries.find(e => e.hanri === text[index])
  || apostropheEntries.find(e => text.startsWith(e.hanri, index)) || null;
const findHangulOverrideAt = (text, index) => {
  const entry = entries.find(e => e.hanri.includes('’') && text.startsWith(e.hanri, index));
  return entry ? { entry, end: index + entry.hanri.length } : null;
};
const rawAudio = key => {
  const tone = key.at(-1), unit = key.slice(0, -1);
  return { segments: [{ unit, tone, file: unit + tone + '.wav' }] };
};
const renderer = phonetic.createRenderer({ imeCore: core, findHanriEntry,
  findHangulOverride: () => null, findHangulOverrideAt });
const planner = mode => phonetic.createAudioPlanner({ imeCore: core, findHanriEntry,
  findHangulOverrideAt, findRawHangulAudio: rawAudio, getSandhiMode: () => mode });
const tones = (text, mode = 'taipei') => Array.from(planner(mode).plan(text).segments, s => s.tone);
const rendered = text => renderer.render(text).normalize('NFC');
// Dictionary entries written with their own apostrophe stay whole.
assert.deepEqual(tones('轉’래'), ['2', '3']);
assert.deepEqual(tones('轉’래가2'), ['2', '3', '3']);
assert.deepEqual(tones('轉’래 가2'), ['2', '3', '2']);
assert.deepEqual(tones('有影’뽀'), ['1', '2', '4']);
assert.ok(!planner('taipei').plan('轉’래').missing.length, 'apostrophe entry has audio');
assert.equal(rendered('轉’래'), 'tǹg’lai'.normalize('NFC'));
assert.equal(rendered('轉’래 가2'), 'tǹg’lai kà'.normalize('NFC'));
assert.equal(rendered('有影’뽀'), 'û-yà̰’bó'.normalize('NFC'));
for (const mark of ['-', '—', '…']) {
  assert.equal(rendered('甲' + mark), ('kā' + mark).normalize('NFC'), mark);
  assert.deepEqual(tones('甲' + mark), ['5'], mark);
  assert.equal(rendered('[甲가]' + mark), 'kà' + mark, 'untoned annotation ' + mark);
  assert.deepEqual(tones('[甲가]' + mark), ['2'], 'untoned annotation ' + mark);
}
for (const mark of ['——', '……', '———', '………']) {
  assert.equal(rendered('甲' + mark), 'kâ' + mark, mark);
  assert.deepEqual(tones('甲' + mark), ['1'], mark);
}
for (const apostrophe of ["'", '’']) {
  const text = '가1' + apostrophe + '가2가4';
  assert.equal(rendered(text), 'kâ’ka-ka');
  assert.deepEqual(tones(text), ['1', '3', '3']);
  assert.deepEqual(tones(text, 'singapore'), ['1', '3', '3']);
}
for (const boundary of [' ', ',', '，', '.', '/', '(', '‘', '—', '——', '…', '……']) {
  const text = '가1’가2' + boundary + '가2';
  assert.deepEqual(tones(text), ['1', '3', '2'], boundary);
  assert.equal(rendered(text), 'kâ’ka' + boundary + 'kà', boundary);
}
for (const [unit, tone] of [['ᄅᆤ', '2'], ['뽀', '4'], ['나', '5']]) {
  assert.deepEqual(tones('가1’' + unit + '가2'), ['1', tone, '3']);
  assert.equal(rendered('가1’' + unit + '가2'),
    ('kâ’' + phonetic.applyTone(phonetic.romanizeUnit(unit), tone) + '-ka').normalize('NFC'));
}
for (const mark of ['—', '——']) {
  const segments = planner('taipei').plan('가1' + mark + '가2').segments;
  assert.deepEqual(Array.from(segments, s => [!!s.trimStart, !!s.trimEnd]), [[false, false], [false, false]]);
}
for (const mark of ['…', '……']) {
  const segments = planner('taipei').plan('가1' + mark + '가2').segments;
  assert.deepEqual(Array.from(segments, s => [!!s.trimStart, !!s.trimEnd]), [[false, true], [true, false]]);
}
assert.deepEqual(Array.from(renderer.resolvedHangulToneSpans('가1’가2,가2'), s => s.reading), ['가1', '가3', '가2']);
assert.deepEqual(Array.from(renderer.resolvedHangulToneSpans('가1’뽀가2'), s => s.reading), ['가1', '뽀4', '가3']);
assert.deepEqual(tones('가가’가'), ['3', '3', '3']);
assert.equal(rendered('가가’가'), 'ka-ka’ka');
assert.deepEqual(tones('가1‘가2'), ['1', '2']);
assert.equal(rendered('가1‘가2'), 'kâ‘kà');
assert.deepEqual(tones('가1‘뽀'), ['1', '3']);
assert.deepEqual(tones('가1’가2’가4'), ['1', '3', '3']);
console.log('PASS: v3.3 browser punctuation, neutral domains, exceptions and opening quotes.');
