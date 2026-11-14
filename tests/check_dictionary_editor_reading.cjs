const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const context = vm.createContext({document: {addEventListener() {}}});
context.window = context;
for (const file of ['shared/web-hangul-ime.js', 'shared/web-ime-core.js']) vm.runInContext(read(file), context);
const source = read('desktop/dictionary_editor_ui/editor.js');
const helpers = source.slice(source.indexOf('  function generatedReading('), source.indexOf('  function scheduleSimplifiedFields('));
vm.runInContext(`
const core = TangliengimImeCore;
const state = {selectedDefunct: false};
let readingIndex, readingManual = false, generatingReading = false, headwordComposing = false;
const controls = {hanri: {value: ''}, reading: {value: ''}};
const $ = name => controls[name];
const composers = [{getRememberedHanriReadings: () => []}, {
  composer: {setText(value) {controls.reading.value = value;}},
  updateControlFromComposer() {},
}];
${helpers}
globalThis.test = {generatedReading, updateAutomaticReading, controls, state,
  manual(value) {readingManual = value;}, composing(value) {headwordComposing = value;},
  index(value) {readingIndex = value;}};
`, context);
const {test, TangliengimImeCore: core} = context;
const entry = (hanri, reading, id) => ({hanri, reading, active: true, kind: 'plain_hanri', entry_id: id, raw: {reading}});
const index = core.createDictionaryIndex([
  entry('家', '가1', 'U+5BB6_00'), entry('己', '기2', 'U+5DF1_00'),
  entry('家己', '가1디5', 'U+5BB6_U+5DF1_00'),
  entry('食', '짇1', 'U+98DF_00'),
]);
assert.equal(test.generatedReading('家己', index), '가1디5', 'whole-word reading wins');
assert.equal(test.generatedReading('己家', index), '기1가1', 'preceding word receives shared Taipei sandhi');
assert.equal(test.generatedReading('己 家', index), '기2 가1', 'spaces stop sandhi');
assert.equal(test.generatedReading('己’家', index), '기2’가1', 'apostrophe remains a boundary');
assert.equal(test.generatedReading('食家', index), '짇가1', 'checked syllables use the shared checked-tone rule');
assert.equal(test.generatedReading('己-家', index), '기1-가1', 'hyphen joins words');
assert.equal(test.generatedReading('己', index), '기2', 'removing the following word restores the citation');
assert.equal(test.generatedReading('家己家', index), '가1디가1', 'only the whole-word final changes');
assert.equal(test.generatedReading('己家', index), '기1가1', 'repeated generation does not sandhi twice');
assert.equal(test.generatedReading('家未知', index), '', 'unknown characters never create partial readings');
assert.equal(test.generatedReading('家릐2', index), '가5릐2', 'mixed Hangul receives contextual sandhi');
assert.equal(test.generatedReading('家', index, [{start: 0, end: 1, hanri: '家', reading: '게1'}]), '게1', 'selected reading wins');
test.index(index);
test.controls.hanri.value = '家己';
test.updateAutomaticReading();
assert.equal(test.controls.reading.value, '가1디5');
test.manual(true);
test.controls.reading.value = '가1기5';
test.controls.hanri.value = '己家';
test.updateAutomaticReading();
assert.equal(test.controls.reading.value, '가1기5', 'manual override is preserved');
test.manual(false);
test.composing(true);
test.updateAutomaticReading();
assert.equal(test.controls.reading.value, '가1기5', 'unfinished composition is ignored');
test.composing(false);
test.updateAutomaticReading();
assert.equal(test.controls.reading.value, '기1가1');
test.state.selectedDefunct = true;
test.controls.hanri.value = '家己';
test.updateAutomaticReading();
assert.equal(test.controls.reading.value, '기1가1', 'defunct entries are not edited');
assert.ok(source.includes('readingManual = Boolean(entry?.reading)'), 'existing readings are protected');
console.log('PASS: dictionary reading autofill, whole words, mixed script, selected readings, manual edits, composition, and defunct entries.');
