// Check static order, identity-based migration parity, and contextual defaults.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname,'..');
const data = JSON.parse(fs.readFileSync(path.join(root,'public/data/hokkien-hanri-dict.json')));
const context = vm.createContext({document:{addEventListener(){}}});
context.window = context;
for (const file of ['shared/web-hangul-ime.js','shared/web-ime-core.js']) vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),context);
const core = context.TangliengimImeCore;
const index = core.createDictionaryIndex(data.entries);
const reversed = core.createDictionaryIndex([...data.entries].reverse().map((e,i) => ({...e,row:100000-i})));
for (const [key,list] of index.candidatesByReading) assert.deepEqual(list.map(e=>e.id),reversed.candidatesByReading.get(key).map(e=>e.id),`Row-dependent candidates: ${key}`);
const defaults = JSON.parse(fs.readFileSync(path.join(root,'tests/fixtures/static-reading-defaults.json')));
for (const expected of defaults.defaults) {
  const actual = index.findHanriEntry(expected.key);
  assert.equal(actual?.hanri || null,expected.hanri,`Segmentation changed: ${expected.key}`);
  assert.equal(actual?.reading || null,expected.reading,`Default reading changed: ${expected.key}`);
  const reordered = reversed.findHanriEntry(expected.key);
  assert.equal(actual?.id,reordered?.id,`Row-dependent reading: ${expected.key}`);
}
for (const expected of defaults.hangulDefaults) assert.equal(index.findHangulOverride(expected.key)?.id || null,expected.id,`Hangul default: ${expected.key}`);
const examples = ['A','B','C','D'].map((id,i)=>({id,hanri:id,reading:id,canonicalKey:[i],staticRanks:{}}));
const ids = items => Array.from(items,e=>e.id);
assert.deepEqual(ids(core.rankEntries(examples.map(e=>({...e,staticRanks:e.id==='C'?{x:1}:{}})),'x')),['C','A','B','D']);
assert.deepEqual(ids(core.rankEntries(examples.map(e=>({...e,staticRanks:e.id==='D'?{x:2}:{}})),'x')),['A','D','B','C']);
assert.deepEqual(ids(core.rankEntries([...examples].reverse(),'y')),['A','B','C','D']);
const beforeFlag = process.argv.indexOf('--before');
if (beforeFlag !== -1) {
  const dir = process.argv[beforeFlag+1];
  const before = JSON.parse(fs.readFileSync(path.join(dir,'public/data/hokkien-hanri-dict.json')));
  const snapshot = JSON.parse(fs.readFileSync(path.join(dir,'static-snapshot.json')));
  const prior = new Map(before.entries.map(e=>[e.id,e]));
  assert.equal(data.entries.length,prior.size);
  const preservedFields = ['id','entryType','active','kind','hanri','reading','readingBase','lomari','lomariKey','english','englishKey','simplified','mandarin_trad','mandarin_simp','correctedFrom','citationReading','autoSandhi','audio','categories'];
  for (const entry of data.entries) {
    const old = prior.get(entry.id);
    assert.ok(old,`Identity changed: ${entry.id}`);
    for (const key of preservedFields) assert.deepEqual(entry[key],old[key],`Unrelated field ${key}: ${entry.id}`);
    assert.ok(!('priority' in entry) && !('priority' in entry.raw));
  }
  assert.deepEqual(data.runtime,before.runtime,'Audio/Lomari runtime changed');
  for (const name of Object.keys(before.indexes)) {
    const asSets = index => Object.fromEntries(Object.entries(index).sort(([a],[b])=>a.localeCompare(b)).map(([key,ids])=>[key,[...ids].sort()]));
    assert.deepEqual(asSets(data.indexes[name]),asSets(before.indexes[name]),`Lookup membership changed: ${name}`);
  }
  const changes = [];
  for (const [key,oldIds] of snapshot.candidates) {
    const current = Array.from(index.candidatesByReading.get(key),e=>e.id);
    if (JSON.stringify(oldIds)===JSON.stringify(current)) continue;
    assert.deepEqual([...oldIds].sort(),[...current].sort(),`Candidate membership changed: ${key}`);
    // Every inversion of a genuinely unequal legacy priority is unexpected.
    for (let i=0;i<current.length;i++) for (let j=i+1;j<current.length;j++) {
      const a = prior.get(current[i]), b = prior.get(current[j]);
      assert.ok(a.priority<=b.priority,`Lost legacy priority tier: ${key} ${a.id} / ${b.id}`);
    }
    changes.push({lookup_key:core.rankingLookupKey(key),before:oldIds,after:current,classification:'C: equal legacy-priority row ties replaced by canonical ordering'});
  }
  const reportPath = path.join(root,'docs/static-priority-migration.json');
  const report = JSON.parse(fs.readFileSync(reportPath));
  report.rowTieGroupsChanged = changes.length;
  report.rowTieChanges = changes;
  report.unexpectedDifferences = [];
  fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');
  console.log(`Migration parity: ${changes.length} tied-order groups changed; 0 unexpected changes; runtime/lexical/index membership unchanged.`);
}
console.log(`PASS: ${index.candidatesByReading.size} row-independent candidate groups; ${defaults.defaults.length} Hanri contexts and ${defaults.hangulDefaults.length} Hangul defaults preserved; sparse absolute-rank examples pass.`);
