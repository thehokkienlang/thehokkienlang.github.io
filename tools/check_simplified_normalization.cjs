// Exercise dictionary matching and real controller state without a browser.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const fixture = JSON.parse(fs.readFileSync(path.join(root, 'tests/fixtures/simplified-normalization.json'), 'utf8'));

function element() {
  return {
    value: '', children: [], hidden: true, selectionStart: 0, selectionEnd: 0,
    handlers: new Map(), classList: { add() {}, remove() {}, toggle() {} },
    addEventListener(name, handler) { this.handlers.set(name, handler); },
    setAttribute() {}, focus() {},
    append(...nodes) { this.children.push(...nodes); },
    replaceChildren(...nodes) { this.children = nodes; },
    setSelectionRange(start, end) { this.selectionStart = start; this.selectionEnd = end; },
    setRangeText(value, start, end) {
      this.value = this.value.slice(0, start) + value + this.value.slice(end);
      this.setSelectionRange(start + value.length, start + value.length);
    },
  };
}
const context = vm.createContext({ console, setTimeout, clearTimeout, document: {
  addEventListener() {}, createElement: element, createDocumentFragment: element,
  createTextNode: text => ({ textContent: text }),
} });
context.window = context;
for (const file of ['shared/web-hangul-ime.js', 'shared/web-ime-core.js']) {
  vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context, { filename: file });
}
const core = context.TangliengimImeCore;
const plain = value => JSON.parse(JSON.stringify(value));
const summary = (session, text) => plain(session.matches.map(match => [
  match.source, match.targets.map(target => target.hanri), Array.from(text.slice(0, match.start)).length,
]));
for (const entries of [fixture.entries, [...fixture.entries].reverse()]) {
  const index = core.createSimplifiedNormalizationIndex(entries);
  assert.equal(index.ambiguousCount, 1);
  for (const test of fixture.cases) {
    const session = core.createSimplifiedNormalizationSession(index);
    session.update(test.text);
    assert.deepEqual(summary(session, test.text), test.matches, test.text);
  }
  assert.deepEqual(plain(index.matchAt('负责任', 0).targets[0].entryIds),
    ['U+8CA0_U+8CAC_U+4EFB_00', 'U+8CA0_U+8CAC_U+4EFB_01']);
}

const index = core.createSimplifiedNormalizationIndex(fixture.entries);
const session = core.createSimplifiedNormalizationSession(index);
let seed = 7351;
const random = limit => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed % limit; };
const chars = Array.from('负责任发动冲云뽀𤺪😀 x');
let text = '负责任 云云 发动';
for (let count = 0; count < 800; count += 1) {
  const units = Array.from(text);
  const start = random(units.length + 1);
  units.splice(start, random(4), ...Array.from({ length: random(5) }, () => chars[random(chars.length)]));
  text = units.join('');
  session.update(text);
  const fresh = core.createSimplifiedNormalizationSession(index);
  fresh.update(text);
  assert.deepEqual(plain(session.matches), plain(fresh.matches), `Incremental edit ${count}`);
}
const large = core.createSimplifiedNormalizationSession(index);
large.update('x'.repeat(20000) + '负责任' + 'x'.repeat(20000));
const originalMatchAt = index.matchAt;
let lookups = 0;
index.matchAt = (...args) => { lookups += 1; return originalMatchAt(...args); };
large.update(large.text + 'x');
assert.ok(lookups < index.maxLength * 3, 'Typing at the end must not rescan the entire document');
index.matchAt = originalMatchAt;

const control = element(), suggestions = element();
const learned = [];
const controller = core.createTextImeController({
  control, normalizationContainer: suggestions,
  dictionaryIndex: { candidatesByReading: new Map(), simplifiedNormalization: index },
  preferences: { record: (...args) => learned.push(args), setActiveIds() {}, reload: async () => {} },
});
const input = (value, inputType = 'insertFromPaste') => {
  control.value = value;
  control.setSelectionRange(value.length, value.length);
  controller.handleInput({ inputType });
};
const label = node => (node.textContent || '') + (node.children || []).map(label).join('');
const accept = (number = 0, alternative = 0) => {
  const match = controller.normalizationSession.matches[number];
  return controller.acceptNormalizationSuggestion(match, match.targets[alternative]);
};
input('负责任');
assert.equal(control.value, '负责任');
assert.equal(label(suggestions), 'Did you mean 負責任?');
assert.equal(suggestions.children[0].children[1].type, 'button');
assert.equal(accept(), true);
assert.equal(control.value, '負責任');
assert.equal(control.selectionStart, 3);
assert.equal(suggestions.hidden, true);
assert.equal(learned.length, 0);

input('ABC负责任XYZ 发动');
assert.equal(controller.normalizationSession.matches.length, 2);
accept();
assert.equal(control.value, 'ABC負責任XYZ 发动');
assert.equal(controller.normalizationSession.matches.length, 1);
accept();
assert.equal(control.value, 'ABC負責任XYZ 發動');

input('冲');
assert.equal(control.value, '冲');
assert.equal(label(suggestions), 'Did you mean 沖 or 衝?');
accept(0, 1);
assert.equal(control.value, '衝');
input('负뽀');
accept();
assert.equal(control.value, '負뽀');
input('𠮟负责任');
accept();
assert.equal(control.value, '叱负责任');
assert.equal(controller.normalizationSession.matches[0].start, 1);
accept();
assert.equal(control.value, '叱負責任');
input('世界 自己');
assert.equal(suggestions.hidden, true);

input('负责任');
const stale = controller.normalizationSession.matches[0];
input('unchanged');
assert.equal(controller.acceptNormalizationSuggestion(stale, stale.targets[0]), false);
assert.equal(control.value, 'unchanged');
controller.clear();
assert.equal(suggestions.hidden, true);

// Composition must be tracked even on desktop, where Korean recomposition is off.
assert.equal(control.handlers.has('compositionstart'), true);
controller.handleCompositionStart();
control.value = '负责任';
controller.handleInput({ isComposing: true, inputType: 'insertCompositionText' });
assert.equal(suggestions.hidden, true);
controller.handleCompositionEnd({ data: '负责任' });
assert.equal(control.value, '负责任');
assert.equal(label(suggestions), 'Did you mean 負責任?');
controller.handleInput({ inputType: 'insertFromComposition' });
assert.equal(suggestions.children.length, 1, 'Final input event must not duplicate suggestions');

// The user explicitly clarified that ordinary committed edits are eligible too.
input('负责任', 'insertText');
assert.equal(suggestions.hidden, false);
const savedRows = suggestions.children;
controller.handleCursorChange({ type: 'click' });
assert.equal(suggestions.children, savedRows, 'Caret movement must not recreate suggestions');
assert.equal(learned.length, 0);

const mobileControl = element(), mobileSuggestions = element();
const mobile = core.createTextImeController({
  control: mobileControl, normalizationContainer: mobileSuggestions,
  dictionaryIndex: { candidatesByReading: new Map(), simplifiedNormalization: index },
  recomposeNativeKoreanInput: true,
  preferences: { record: (...args) => learned.push(args), setActiveIds() {}, reload: async () => {} },
});
mobile.handleCompositionStart();
mobileControl.value = '负责任';
mobileControl.setSelectionRange(3, 3);
mobile.handleInput({ isComposing: true, inputType: 'insertCompositionText' });
assert.equal(mobileSuggestions.hidden, true);
mobile.handleCompositionEnd({ data: '负责任' });
assert.equal(mobileControl.value, '负责任');
assert.equal(label(mobileSuggestions), 'Did you mean 負責任?');

const dataPath = process.env.TANGLIENGIM_NORMALIZATION_DATA || path.join(root, 'public/data/hokkien-hanri-dict.json');
// Windows Pinyin emits keyup during preedit. Synchronizing the control there
// rewrites ASCII separators, terminates composition, and commits partial copies.
for (const [preedits, committed] of [
  [['fu', "fu'ze", "fu'ze'ren"], '负责任'],
  [['ㄈㄨˋ', 'ㄈㄨˋㄗㄜˊ', 'ㄈㄨˋㄗㄜˊㄖㄣˋ'], '負責任'],
]) {
  const field = element(), container = element();
  const composing = core.createTextImeController({
    control: field, normalizationContainer: container,
    dictionaryIndex: { candidatesByReading: new Map(), simplifiedNormalization: index },
    preferences: { record: (...args) => learned.push(args), setActiveIds() {}, reload: async () => {} },
  });
  let prevented = false;
  composing.handleKeydown({ key: 'f', keyCode: 229, preventDefault() { prevented = true; } });
  assert.equal(prevented, false, 'The first native IME keystroke must be left to the OS');
  composing.handleCompositionStart();
  for (const preedit of preedits) {
    field.value = preedit;
    field.setSelectionRange(preedit.length, preedit.length);
    composing.handleInput({ isComposing: true, inputType: 'insertCompositionText' });
    composing.handleCursorChange({ type: 'keyup', key: 'e', isComposing: false });
    composing.handleCursorChange({ type: 'click' });
    assert.equal(field.value, preedit, 'Preedit must retain its exact native spelling');
    assert.equal(composing.composer.text(), '', 'Preedit must never enter the committed composer state');
    assert.equal(container.hidden, true);
  }
  field.value = committed;
  field.setSelectionRange(committed.length, committed.length);
  composing.handleCompositionEnd({ data: committed });
  composing.handleInput({ inputType: 'insertFromComposition' });
  assert.equal(field.value, committed, 'Only the final Chinese text should be committed once');
  assert.equal(container.hidden, committed === '負責任');
}
assert.equal(learned.length, 0);

const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
const real = core.createDictionaryIndex(data.entries).simplifiedNormalization;
const realMatch = real.matchAt('负责任', 0);
assert.deepEqual(plain(realMatch.targets), [{ hanri: '負責任', entryIds: ['U+8CA0_U+8CAC_U+4EFB_00'] }]);
assert.equal(real.ambiguousCount, 1);
assert.deepEqual(plain(real.matchAt('冲', 0).targets.map(target => target.hanri)), ['沖', '衝']);
console.log(`OK: Simplified Hokkien matching, 800 incremental edits, composition, replacements, and learning isolation; ${real.size} real mappings, ${real.ambiguousCount} ambiguous.`);
