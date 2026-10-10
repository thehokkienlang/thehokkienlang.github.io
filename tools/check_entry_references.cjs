// Exodus III: use real controller recovery/annotation paths, not display keys.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'public/data/hokkien-hanri-dict.json')));
function element() {
  return {
    value: '', selectionStart: 0, selectionEnd: 0, children: [],
    classList: { add() {}, toggle() {} }, setAttribute() {}, focus() {}, addEventListener() {},
    setSelectionRange(a, b) { this.selectionStart = a; this.selectionEnd = b; },
    replaceChildren(...items) { this.children = items; }, append(...items) { this.children.push(...items); },
  };
}
const context = vm.createContext({console, document: {
  addEventListener() {}, createElement: element, createDocumentFragment: element,
  createTextNode: text => ({textContent: text}),
}});
context.window = context;
for (const file of ['shared/web-hangul-ime.js', 'shared/web-ime-core.js']) {
  vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context);
}
const core = context.TangliengimImeCore;
const controller = () => core.createTextImeController({control: element(), candidateContainer: element(),
  entries: data.entries, dictionaryIndex: core.createDictionaryIndex(data.entries)});
const source = (id, variant = false) => ({id: id + (variant ? '-sandhi' : ''),
  raw: {entry_id: id}, hanri: '底', reading: '가', kind: 'hanri', autoSandhi: variant});
const range = entry => ({entry, start: 0, end: 1});
const ime = controller();
ime.control.value = '가';
ime.control.setSelectionRange(1, 1);
ime.unresolvedCandidateContext = ime.candidateContextKey();
let candidates = [range(source('U+5E95_00')), range(source('U+5E95_01'))];
ime.findCandidates = () => candidates;
ime.renderCandidates();
ime.setCandidateIndex(1, true);
candidates = [range({...source('U+5E95_01'), hanri: 'New display', reading: '다'}), range(source('U+5E95_00'))];
ime.renderCandidates();
assert.equal(ime.activeCandidateIndex, 0, 'Recovery uses exact ID despite new display/reading and row order');
assert.equal(ime.candidateSelectionExplicit, true);
candidates = [range(source('U+5E95_00')), range(source('U+5E95_02'))];
ime.renderCandidates();
assert.equal(ime.candidateSelectionExplicit, false, 'Missing selected ID must not silently recover same-looking record');
candidates = [range(source('U+5E95_00')), range(source('U+5E95_00', true))];
ime.renderCandidates();
ime.setCandidateIndex(1, true);
candidates = [...candidates].reverse();
ime.renderCandidates();
assert.equal(ime.activeCandidateIndex, 0, 'Source ID plus variant distinguish generated sandhi option');

const remembered = controller();
remembered.control.value = '底가';
remembered.rememberHanriReading(0, {...source('U+5E95_01'), reading: '도2'}, '底가');
remembered.rememberHangulReading(1, 2, '가1', {...source('U+AC00_00'), kind: 'hangul_override'}, '底가');
assert.equal(remembered.getRememberedHanriReadings()[0].entryId, 'U+5E95_01');
assert.equal(remembered.getRememberedHangulReadings()[0].entryId, 'U+AC00_00');
remembered.rememberHangulReading(1, 2, '가2', null, '底가', true);
assert.equal(Object.hasOwn(remembered.getRememberedHangulReadings()[0], 'entryId'), false,
  'Literal explicit pronunciation is content, not a guessed dictionary reference');

const recovery = controller();
recovery.control.value = '가';
recovery.control.setSelectionRange(1, 1);
recovery.rememberHangulReading(0, 1, '가', source('U+5E95_01'), '가');
recovery.unresolvedCandidateContext = recovery.candidateContextKey();
recovery.findCandidates = () => [range(source('U+5E95_00')), range(source('U+5E95_01'))];
recovery.renderCandidates();
assert.equal(recovery.activeCandidateIndex, 1, 'Remembered same-reading records remain independent');
const aliases = data.correctionAliases || [];
const ids = new Set(data.entries.map(entry => entry.raw.entry_id));
for (const alias of aliases) {
  assert.ok(ids.has(alias.aliasId) && ids.has(alias.canonicalId), 'Alias relationships target active source IDs');
}
console.log(`PASS: exact-ID candidate recovery, variant isolation, stale-ID omission, annotation transport, anonymous spans; ${aliases.length} ID-based correction relationships.`);
