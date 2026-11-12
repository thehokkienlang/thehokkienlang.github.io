// The TLI engine must run with no browser: a mobile keyboard embeds exactly these sources.
// Loads web-hangul-ime.js and the engine section of web-ime-core.js into a context that has
// no window or document, then checks the results against the full browser core.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const { loadDictionaryData } = require('../tools/dictionary_data.cjs');
const data = loadDictionaryData(path.join(root, 'public/data/hokkien-hanri-dict.json'));

const MARKER = '// END TLI ENGINE (browser-free)';
const coreSource = read('shared/web-ime-core.js');
assert.equal(coreSource.split(MARKER).length, 2, 'web-ime-core.js needs exactly one engine end marker');
const engineSource = coreSource.slice(0, coreSource.indexOf(MARKER));
const code = engineSource.split('\n').filter(line => !line.trim().startsWith('//')).join('\n');
assert.doesNotMatch(code, /\bdocument\b|\bnavigator\b|\bgetComputedStyle\b|\brequestAnimationFrame\b/,
  'The engine section must not use browser APIs');

// A bare context: the language built-ins only.
const bare = vm.createContext({});
vm.runInContext(read('shared/web-hangul-ime.js'), bare);
vm.runInContext(engineSource, bare);
vm.runInContext('globalThis.engine = TangliengimEngine; globalThis.hangul = TangliengimHangulIme;', bare);
for (const name of ['window', 'document']) {
  assert.equal(vm.runInContext(`typeof ${name}`, bare), 'undefined', `${name} leaked into the bare context`);
}
const { engine, hangul } = bare;

// The browser core, loaded the way the other checks load it.
const browser = vm.createContext({ document: { addEventListener() {} } });
browser.window = browser;
for (const file of ['shared/web-hangul-ime.js', 'shared/web-ime-core.js']) vm.runInContext(read(file), browser);
const core = browser.TangliengimImeCore;

// The browser core must be a superset of the engine, sharing its behaviour.
for (const name of Object.keys(engine)) {
  if (name in core) assert.equal(typeof core[name], typeof engine[name], `Type differs: ${name}`);
}

const headless = engine.createDictionaryIndex(data.entries);
const reference = core.createDictionaryIndex(data.entries);
const ids = map => JSON.stringify([...map].map(([key, list]) => [key, list.map(entry => entry.id)]));
assert.ok(headless.candidatesByReading.size > 1000, 'The headless index is unexpectedly small');
assert.equal(ids(headless.candidatesByReading), ids(reference.candidatesByReading),
  'Headless candidates differ from the browser core');

// Typing through the composer, then looking up and ranking, works with no browser.
const composer = new hangul.Composer({ shouldAutocorrectEToYe: () => false });
const sample = [...headless.candidatesByReading].find(([, list]) => list.length > 1);
composer.setText(sample[1][0].readingBase || '');
assert.equal(typeof composer.text(), 'string');
const wrap = list => list.map(entry => ({ entry, lookupKey: sample[0] }));
const activeIds = data.entries.map(entry => entry.raw?.entry_id || entry.id);
const ranked = engine.createCandidatePreferences({ activeIds }).rank(wrap(sample[1]), sample[0]);
assert.equal(ranked.length, sample[1].length, 'Ranking dropped candidates');
const referenceRanked = core.createCandidatePreferences({ activeIds })
  .rank(wrap(reference.candidatesByReading.get(sample[0])), sample[0]);
// Arrays from two VM contexts have different prototypes, so compare their JSON.
assert.equal(JSON.stringify(ranked.map(item => item.entry.id)),
  JSON.stringify(referenceRanked.map(item => item.entry.id)), 'Headless ranking differs');

console.log(`OK: the TLI engine runs with no browser; ${headless.candidatesByReading.size} reading keys match the browser core.`);
