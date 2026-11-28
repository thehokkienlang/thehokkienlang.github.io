// Phrase conversion in the web IME and the Android keyboard's engine
// (docs/ime-phrase-conversion-plan.md). The shared cases also run against the desktop engine in
// tests/test_phrase_conversion.py.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const { loadDictionaryData } = require('../tools/dictionary_data.cjs');
const data = loadDictionaryData(path.join(root, 'public/data/hokkien-hanri-dict.json'));
const { cases, afterApostrophe } = JSON.parse(read('tests/fixtures/phrase-conversion-cases.json'));

function element() {
  const listeners = {};
  return {
    value: '', textContent: '', className: '', selectionStart: 0, selectionEnd: 0, children: [], listeners,
    classList: { add() {}, toggle() {} }, setAttribute() {}, focus() {},
    addEventListener(name, fn) { listeners[name] = fn; },
    setSelectionRange(start, end) { this.selectionStart = start; this.selectionEnd = end; },
    replaceChildren(...items) { this.children = items; },
    append(...items) { this.children.push(...items); },
  };
}
const storage = new Map();
const context = vm.createContext({
  console,
  document: { addEventListener() {}, createElement: element, createDocumentFragment: element,
    createTextNode: text => ({ textContent: text, children: [] }) },
  localStorage: { getItem: key => storage.get(key) || null, setItem: (key, value) => storage.set(key, value) },
});
context.window = context;
for (const file of ['shared/web-hangul-ime.js', 'shared/web-ime-core.js']) vm.runInContext(read(file), context);
const core = context.TangliengimImeCore;
const index = core.createDictionaryIndex(data.entries);
const plain = value => JSON.parse(JSON.stringify(value));

function controller() {
  return core.createTextImeController({ control: element(), candidateContainer: element(),
    entries: data.entries, dictionaryIndex: index, candidateLimit: 9 });
}
// Type as the IME does: tone digits stay hidden and only pick candidates.
function type(ime, typed) {
  for (const char of typed) ime.insertText(char);
  return ime.activeCandidates;
}
const menu = list => Array.from(list, c => [c.entry.id || null, c.entry.hanri, c.entry.reading, c.start, c.end]);
const keyEvent = key => ({ key, preventDefault() {} });
function units(typed) {
  const result = [];
  for (let at = 0; at < typed.length;) {
    let { end } = core.readingUnitAt(typed, at);
    if (/[1-5]/.test(typed[end] || '')) end += 1;
    result.push(typed.slice(at, end));
    at = end;
  }
  return result;
}

// 1. The shared cases, against the pure engine functions and through the controller's menu.
for (const testCase of cases) {
  // The engine splits only what follows the last apostrophe, as the menu does, and offers no
  // phrase for text a typed apostrophe attaches.
  const typedUnits = units(testCase.typed.split('’').at(-1));
  const lookup = core.phraseSpanLookup(index.candidatesByReading, typedUnits);
  let suffix = 0;
  for (let length = typedUnits.length; length > 0 && !suffix; length -= 1) {
    if (lookup(typedUnits.length - length, typedUnits.length).length) suffix = length;
  }
  const result = core.followsApostrophe(testCase.typed, testCase.typed.length)
    ? null : core.phraseForRun(typedUnits, lookup, suffix);
  const segments = result && Array.from(result.segments, s => [s.startUnit, s.endUnit, s.entry?.id || null]);
  assert.deepEqual(plain(segments), testCase.phrase, `engine: ${testCase.name}`);

  const ime = controller();
  const list = type(ime, testCase.typed);
  const phrases = list.filter(c => c.entry.kind === 'phrase');
  assert.equal(phrases.length, testCase.phrase ? 1 : 0, `menu: ${testCase.name}`);
  if (testCase.phrase) {
    assert.equal(list[0].entry.kind, 'phrase', `the phrase is first: ${testCase.name}`);
    assert.deepEqual(plain(Array.from(list[0].segments, s => s.entry?.id || null)),
      testCase.phrase.map(([, , id]) => id), `menu words: ${testCase.name}`);
    assert.equal(list[0].entry.hanri, testCase.text, `menu text: ${testCase.name}`);
    assert.doesNotMatch(list[0].entry.hanri + list[0].entry.reading, /\s/u, `no added space: ${testCase.name}`);
    ime.applyCandidate(list[0]);
    const head = testCase.typed.slice(0, testCase.typed.lastIndexOf('’') + 1);
    assert.equal(ime.control.value, head.replace(/[1-5]/g, '') + testCase.text, `written: ${testCase.name}`);
  }
  // Without phrase conversion the rest of the menu is the same, in the same order.
  const shown = type(controller(), testCase.typed);
  const before = controller();
  before.findPhraseCandidate = () => null;
  const ordinary = menu(type(before, testCase.typed));
  const rest = menu(shown.filter(c => c.entry.kind !== 'phrase'));
  assert.deepEqual(rest, ordinary.slice(0, rest.length), `ordinary candidates unchanged: ${testCase.name}`);
  assert.equal(shown.length, Math.min(9, ordinary.length + phrases.length), `menu length: ${testCase.name}`);
}
assert.deepEqual(plain(controller().preferences.snapshot().selections), {}, 'Showing menus must not learn');

// After a typed apostrophe the menu offers only Hangul, whichever way a choice is made.
const isHangul = candidate => ['hangul_override', 'hangul_plain'].includes(candidate.entry.kind);
for (const [typed, written] of afterApostrophe) {
  const list = type(controller(), typed);
  assert.ok(list.length, `a menu is still offered: ${typed}`);
  assert.deepEqual(Array.from(list.filter(c => !isHangul(c)), c => c.entry.hanri), [], `no Hanri: ${typed}`);
  for (let position = 0; position < list.length; position += 1) {
    const ime = controller();
    ime.applyCandidate(type(ime, typed)[position]);
    assert.doesNotMatch(ime.control.value.slice(ime.control.value.lastIndexOf('’')), /\p{Script=Han}/u,
      `choice ${position + 1} writes Hangul: ${typed}`);
    assert.ok(ime.control.value.includes('’'), `the typed apostrophe stays: ${typed}`);
    if (!position) assert.equal(ime.control.value, written, `first choice: ${typed}`);
  }
}
// Directly after ’ the apostrophe form comes first, with its own reading: ’이 is not 이5.
{
  const ime = controller();
  const list = type(ime, '’이');
  assert.equal(list[0].entry.id, 'U+2019_U+C774_00');
  ime.applyCandidate(list[0]);
  assert.deepEqual(plain(ime.getRememberedHangulReadings().map(s => [s.hangul, s.reading])), [['’이', '’이']]);
}
// Without a typed apostrophe nothing changes, and choices made after ’ are learned apart.
{
  const first = typed => type(controller(), typed)[0].entry.hanri;
  assert.deepEqual([first('에'), first('킈')], ['會', '去']);
  const ime = controller();
  for (let times = 0; times < 5; times += 1) {
    ime.clear();
    type(ime, '꽈’에');
    ime.candidateContainer.children[0].listeners.click();
  }
  assert.deepEqual(Object.keys(ime.preferences.snapshot().selections), ['’에']);
  assert.equal(first('에'), '會', 'Choosing ’에 after an apostrophe does not move it above 會');
  ime.preferences.reset();
}
// A space ends the attachment: what follows converts again.
assert.equal(type(controller(), '꽈’에 킈쟣븡')[0].entry.hanri, '去食飯');

// 2. The plan's headline menu: the whole phrase first, the word it used to offer still below.
{
  const list = type(controller(), '킈쟣븡');
  assert.deepEqual(Array.from(list.slice(0, 3), c => c.entry.hanri), ['去食飯', '食飯', '쟣븡']);
  assert.equal(list[0].entry.reading, '킈쟣븡5', 'The reading line adds no space between the words');
  assert.equal(list[1].start, 1, '食飯 still replaces only 쟣븡');
}

// 3. segmentReadingRun on its own: the tie-breaks of section 4.3.
{
  const entry = (name, order) => ({ id: name, canonicalKey: [order] });
  const table = words => (i, j) => (words[`${i}-${j}`] ? [words[`${i}-${j}`]] : []);
  const split = (count, words) => Array.from(core.segmentReadingRun(Array(count).fill('x'), table(words)).segments,
    s => `${s.startUnit}-${s.endUnit}${s.entry ? `:${s.entry.id}` : ''}`);
  assert.deepEqual(split(3, { '0-1': entry('a', 1), '1-3': entry('bc', 2), '1-2': entry('b', 3), '2-3': entry('c', 4) }),
    ['0-1:a', '1-3:bc'], 'Fewest words');
  assert.deepEqual(split(3, { '0-2': entry('ab', 1), '2-3': entry('c', 2), '0-1': entry('a', 3), '1-3': entry('bc', 4) }),
    ['0-1:a', '1-3:bc'], 'Longest last word, although the other split sorts first');
  assert.deepEqual(split(3, { '0-2': entry('ab', 1), '1-3': entry('bc', 0) }),
    ['0-1', '1-3:bc'], 'With a syllable left over, the longest last word still wins');
  // Two splits ending in the same last word: the earlier words decide, left to right.
  const tie = {
    '0-1': entry('p', 5), '1-3': entry('q', 6), '0-2': entry('r', 1), '2-3': entry('s', 9), '3-4': entry('end', 1),
  };
  assert.deepEqual(split(4, tie), ['0-2:r', '2-3:s', '3-4:end'], 'Then canonical order from the left');
  assert.deepEqual(Array.from(core.segmentReadingRun(['x', 'x'], () => []).cost), [2, 0, 0]);
}

// 4. Committing writes every word and remembers each reading, as single choices would.
{
  const ime = controller();
  type(ime, '킈쟣븡');
  ime.handleKeydown(keyEvent('Enter'));
  assert.equal(ime.control.value, '去食飯');
  assert.equal(ime.control.selectionStart, 3);
  assert.deepEqual(plain(ime.getRememberedHanriReadings().map(s => [s.start, s.end, s.hanri, s.reading, s.entryId])),
    [[0, 1, '去', '킈', 'U+53BB_00'], [1, 3, '食飯', '쟣븡5', 'U+98DF_U+98EF_00']]);
  assert.deepEqual(plain(ime.preferences.snapshot().selections), {}, 'A passive phrase commit learns nothing');

  // Backspace removes one character and keeps the other word's reading; retyping restores it.
  ime.backspace();
  assert.equal(ime.control.value, '去食');
  assert.deepEqual(plain(ime.getRememberedHanriReadings().map(s => s.hanri)), ['去']);
  ime.backspace();
  type(ime, '쟣븡');
  assert.equal(ime.activeCandidates[0].entry.hanri, '食飯', 'No phrase for the word typed after 去');
}

// 5. A clicked phrase also learns nothing, so no single-word menu moves.
{
  const ime = controller();
  type(ime, '킈쟣븡');
  ime.candidateContainer.children[0].listeners.click();
  assert.equal(ime.control.value, '去食飯');
  assert.deepEqual(plain(ime.preferences.snapshot().selections), {}, 'A clicked phrase learns nothing');
}

// 6. Hanri already written is never split again or changed.
{
  const ime = controller();
  type(ime, '킈쟣븡');
  ime.applyCandidate(ime.activeCandidates[0]);
  const kept = plain(ime.getRememberedHanriReadings());
  const list = type(ime, '킈감샤');
  assert.equal(list[0].entry.hanri, '去感謝');
  assert.equal(list[0].start, 3, 'The phrase starts after the written Hanri');
  ime.applyCandidate(list[0]);
  assert.equal(ime.control.value, '去食飯去感謝');
  assert.deepEqual(plain(ime.getRememberedHanriReadings()).slice(0, 2), kept);
}

// 7. A word already chosen in Hangul is not split again either.
{
  const ime = controller();
  const list = type(ime, '쟣븡');
  ime.applyCandidate(list.find(c => c.entry.kind === 'hangul_plain'));
  assert.equal(ime.control.value, '쟣븡');
  const next = type(ime, '킈');
  assert.ok(!next.some(c => c.entry.kind === 'phrase'), 'Chosen Hangul ends the stretch');
}

// 8. Text after the cursor stays; Hangul words and unknown syllables keep their typed tones.
{
  const ime = controller();
  ime.control.value = '。';
  ime.control.setSelectionRange(0, 0);
  const list = type(ime, '꽈킈뷁2쟣븡');
  assert.equal(list[0].entry.hanri, '꽈去뷁食飯');
  ime.applyCandidate(list[0]);
  assert.equal(ime.control.value, '꽈去뷁食飯。');
  assert.equal(ime.control.selectionStart, 5);
  assert.deepEqual(plain(ime.getRememberedHangulReadings().map(s => [s.start, s.end, s.hangul, s.reading, s.explicit])),
    [[0, 1, '꽈', '꽈2', false], [2, 3, '뷁', '뷁2', true]]);
  assert.deepEqual(plain(ime.getRememberedHanriReadings().map(s => [s.start, s.hanri, s.reading])),
    [[1, '去', '킈'], [3, '食飯', '쟣븡5']]);
  const tones = ime.getHangulToneReadingsForDisplay().map(s => [s.start, s.reading]);
  assert.deepEqual(plain(tones), [[0, '꽈2'], [2, '뷁2']], 'Tone marks follow the words to their new places');
}

// 9. With visible tone marks (the dictionary editor's style) the marks leave with their words.
{
  const ime = controller();
  ime.toneInputStyle = 'digits';
  const list = type(ime, '킈쟣븡5');
  assert.equal(list[0].entry.hanri, '去食飯');
  ime.applyCandidate(list[0]);
  assert.equal(ime.control.value, '去食飯');
}

// 10. The reading shown for an unknown syllable is what was typed.
assert.equal(type(controller(), '킈뷁쟣븡')[0].entry.reading, '킈뷁쟣븡5');

console.log(`OK: phrase conversion; ${cases.length} shared cases, tie-breaks and controller commits.`);
