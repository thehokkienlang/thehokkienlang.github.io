// Focused Exodus I checks; no browser or personal preference data is used.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'public/data/hokkien-hanri-dict.json')));
function element() {
  const listeners = {};
  return {
    value: '', selectionStart: 0, selectionEnd: 0, children: [], listeners,
    classList: { add() {}, toggle() {} }, setAttribute() {}, focus() {},
    addEventListener(name, fn) { listeners[name] = fn; },
    setSelectionRange(a, b) { this.selectionStart = a; this.selectionEnd = b; },
    replaceChildren(...items) { this.children = items; },
    append(...items) { this.children.push(...items); },
  };
}
const storage = new Map();
const context = vm.createContext({
  console,
  document: { addEventListener() {}, createElement: element, createDocumentFragment: element,
    createTextNode: text => ({textContent: text}) },
  localStorage: { getItem: key => storage.get(key) || null,
    setItem: (key, value) => storage.set(key, value) },
});
context.window = context;
for (const file of ['shared/web-hangul-ime.js', 'shared/web-ime-core.js']) {
  vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context);
}
const core = context.TangliengimImeCore;
const index = core.createDictionaryIndex(data.entries);
function controller() {
  return core.createTextImeController({control: element(), candidateContainer: element(),
    entries: data.entries, dictionaryIndex: index, candidateLimit: 10000});
}
function show(ime, text) {
  ime.control.value = text;
  ime.control.setSelectionRange(text.length, text.length);
  ime.unresolvedCandidateContext = ime.candidateContextKey();
  ime.renderCandidates();
  return ime.activeCandidates;
}
const signature = list => Array.from(list, c => [c.entry.id || null, c.entry.hanri, c.entry.reading, c.start, c.end]);
const menus = [];
const ime = controller();
for (const [key, entries] of index.candidatesByReading) {
  for (const text of new Set([key, ...entries.map(e => e.reading)])) {
    menus.push([text, signature(show(ime, text))]);
  }
}
const snapshot = {menus: menus.length,
  sha256: crypto.createHash('sha256').update(JSON.stringify(menus)).digest('hex')};
const baseline = path.join(root, 'tests/fixtures/adaptive-static-menu-baseline.json');
if (process.argv.includes('--capture-static')) {
  fs.writeFileSync(baseline, JSON.stringify(snapshot, null, 2) + '\n');
  console.log(snapshot);
  process.exit(0);
}
assert.deepEqual(snapshot, JSON.parse(fs.readFileSync(baseline)), 'Fresh-user menus differ from Pre-Exodus');
assert.deepEqual(JSON.parse(JSON.stringify(ime.preferences.snapshot())).selections, {}, 'Displaying menus must not learn');
const keyEvent = key => ({key, preventDefault() {}});
show(ime, '시');
const first = ime.activeCandidates[0];
assert.ok(first.entry.id);
ime.handleKeydown(keyEvent('Enter'));
assert.deepEqual(JSON.parse(JSON.stringify(ime.preferences.snapshot())).selections, {}, 'Passive Enter must not learn');
show(ime, '시');
ime.candidateContainer.children[0].listeners.click();
assert.equal(ime.preferences.count('시', first.entry.raw.entry_id), 1, 'First-candidate click learns once');
ime.applyCandidate(first, true);
assert.equal(ime.preferences.count('시', first.entry.raw.entry_id), 1, 'A stale duplicate commit cannot learn twice');
ime.preferences.reset();
show(ime, '시');
ime.handleKeydown(keyEvent('Tab'));
const second = ime.activeCandidates[1];
ime.renderCandidates(); // A rerender must retain deliberate navigation intent.
ime.handleKeydown(keyEvent('Enter'));
assert.equal(ime.preferences.count('시', second.entry.raw.entry_id), 1, 'Navigate then commit learns once');
ime.preferences.reset();
const ids = ['A', 'B', 'C'];
const preferences = core.createCandidatePreferences({activeIds: ids});
const candidates = ids.map(id => ({entry: {id}}));
const order = list => Array.from(list, c => c.entry.id);
for (let count = 1; count <= 3; count++) {
  preferences.record('lookup', 'B');
  assert.deepEqual(order(preferences.rank(candidates, 'lookup')), count < 3 ? ids : ['B', 'A', 'C']);
}
assert.deepEqual(order(preferences.rank(candidates, 'another')), ids);
assert.equal(preferences.count('lookup', 'A'), 0);
const reload = core.createCandidatePreferences({activeIds: ids});
assert.deepEqual(order(reload.rank(candidates, 'lookup')), ['B', 'A', 'C']);
for (let i = 0; i < 300; i++) reload.record('lookup', 'B');
assert.equal(reload.count('lookup', 'B'), 255);
const bounded = [...candidates, {entry: {kind: 'hangul_plain', generatedCandidate: true}}];
assert.equal(reload.rank(bounded, 'lookup').at(-1), bounded.at(-1));
const generated = [{entry:{id:'A'}}, {entry:{id:'A-sandhi',autoSandhi:true}}, {entry:{id:'B'}}];
assert.deepEqual(order(reload.rank(generated, 'lookup')), order(generated), 'Generated boundaries retain source precedence');
reload.reset();
assert.deepEqual(order(reload.rank(candidates, 'lookup')), ids);
assert.equal(core.adaptiveLookupKey("'시ˋ"), '’시2');
assert.notEqual(core.adaptiveLookupKey('앚'), core.adaptiveLookupKey('ᄋᅷ'));
const favorite = core.rankEntries(ids.map((id,i) => ({id, canonicalKey:[i],staticRanks:id==='C'?{x:1}:{}})), 'x');
const menu = favorite.map(entry => ({entry}));
for (let i = 0; i < 5; i++) reload.record('x', 'B');
assert.deepEqual(order(reload.rank(menu, 'x')), ['B', 'C', 'A'], 'Learning overtakes manual static favorite');
async function checkBackends() {
  const cases = JSON.parse(fs.readFileSync(path.join(root, 'tests/fixtures/adaptive-ranking-cases.json')));
  for (const test of cases) {
    const backend = {load: async () => ({version:1, selections:test.counts})};
    const fixturePreferences = core.createCandidatePreferences({activeIds:test.ids, backend});
    await fixturePreferences.ready;
    assert.deepEqual(order(fixturePreferences.rank(test.entries.map(entry => ({entry})), test.key)), test.expected, test.name);
  }
  const delayed = core.createCandidatePreferences({backend: {
    load: async () => ({version:1, selections:{x:{B:3}}}),
  }});
  await delayed.ready;
  delayed.setActiveIds(ids);
  assert.deepEqual(order(delayed.rank(candidates, 'x')), ['B', 'A', 'C'], 'Startup loads preference data before dictionary IDs arrive');
  console.log(`PASS: ${snapshot.menus} exact cold-start menus; explicit/passive events, contextual counts, gradual promotion, cap, reload, reset, ${cases.length} shared fixtures and fallback boundaries.`);
}
checkBackends().catch(error => { console.error(error); process.exitCode = 1; });
