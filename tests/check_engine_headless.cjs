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

assert.equal(engine.citationReadingToTaipeiSandhi('졍4'), '졍',
  'Open Tone 4 must surface as unmarked Tone 3 before a following unit');
assert.equal(engine.citationReadingToTaipeiSandhi('졍ˊ'), '졍',
  'Visible Tone 4 symbols must use the same surface-sandhi conversion');
assert.equal(engine.citationReadingToTaipeiSandhi('짇구'), '짇구2',
  'An omitted final tone must resolve from implicit Tone 3 to surface Tone 2');
assert.equal(core.citationReadingToTaipeiSandhi('졍4'), '졍',
  'Browser and headless contextual-reading conversion must match');

// A typed non-final open 4 reads as Taipei's 1 (docs/sandhi-toggle-plan.md, step 7); the same cases are
// in tests/test_typed_sandhi.py for the Python engine.
for (const [typed, expected] of [
  ['정4래5', '정1래5'], ['삐4훈4궤2', '삐1훈1궤2'],
  ['정ˊ래ˉ', '정ˆ래ˉ'], ['정ˏ래ˍ', '정ꞈ래ˍ'], ['정4래ˉ', '정1래ˉ'],
  ['정4', '정4'], ['심5래5', '심5래5'], ['정4 래5', '정4 래5'], ['정4,래5', '정4,래5'],
  ['정4’래5', '정4’래5'], ['정4-래5', '정4-래5'], ['정4*', '정4*'], ['', ''],
  ['뎍4호1', '뎍4호1'], ['뎓4호1', '뎓4호1'], ['뎝4호1', '뎝4호1'], ['뎧4호1', '뎧4호1'], ['뎛4호1', '뎛4호1'],
  ['정1래5정2래3', '정1래5정2래3'], ['歹勢 4', '歹勢 4'], ['정4래5정4래5', '정1래5정1래5'],
]) {
  assert.equal(engine.typedSandhiToTaipei(typed), expected, `typed sandhi: ${typed}`);
  assert.equal(core.typedSandhiToTaipei(typed), expected, `typed sandhi (browser core): ${typed}`);
}

// Phrase conversion runs with no browser too, and splits a run as the browser core does.
const split = (api, dictionary) => {
  const units = ['킈', '쟣', '븡'];
  const result = api.segmentReadingRun(units, api.phraseSpanLookup(dictionary.candidatesByReading, units));
  return JSON.stringify(Array.from(result.segments, s => [s.startUnit, s.endUnit, s.entry?.id || null]));
};
assert.equal(split(engine, headless), '[[0,1,"U+53BB_00"],[1,3,"U+98DF_U+98EF_00"]]', 'Headless phrase split');
assert.equal(split(core, reference), split(engine, headless), 'Headless phrase split differs');

console.log(`OK: the TLI engine runs with no browser; ${headless.candidatesByReading.size} reading keys match the browser core.`);
