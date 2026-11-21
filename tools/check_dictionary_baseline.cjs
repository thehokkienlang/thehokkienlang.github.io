// Capture or check dictionary behaviour. Entries are named by their stable entry IDs
// (U+XXXX_NN, plus -sandhi for generated views), never by their position in the
// generated list: adding or sorting rows must not renumber unrelated candidates.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { loadDictionaryData } = require('./dictionary_data.cjs');

const root = path.resolve(__dirname, '..');
const jsonPath = path.join(root, 'public/data/hokkien-hanri-dict.json');
const fixturePath = path.join(root, 'tests/fixtures/dictionary-baseline.json');
const capture = process.argv.includes('--capture');
const digest = value => crypto.createHash('sha256').update(value).digest('hex');
const objectDigest = value => digest(JSON.stringify(value));

function stableEntry(entry) {
  return {
    kind: entry.kind,
    active: entry.active,
    hanri: entry.hanri,
    reading: entry.reading,
    readingBase: entry.readingBase,
    lomari: entry.lomari,
    lomariKey: entry.lomariKey,
    english: entry.english,
    englishKey: entry.englishKey,
    categories: entry.categories,
    audio: entry.audio,
    form: entry.form,
    raw: {
      reading: entry.raw.reading,
      hanri: entry.raw.hanri,
      corrected: entry.raw.corrected,
      english: entry.raw.english,
    },
    correctedFrom: entry.correctedFrom || null,
    skipReason: entry.skipReason || null,
    autoSandhi: Boolean(entry.autoSandhi),
    citationReading: entry.citationReading || null,
  };
}

function snapshot(data) {
  const known = new Set(data.entries.map(entry => entry.id));
  assert.equal(known.size, data.entries.length, 'Generated entry IDs must be unique');
  for (const [name, index] of Object.entries(data.indexes)) {
    for (const ids of Object.values(index)) {
      for (const id of ids) assert.ok(known.has(id), `Unknown entry ID in ${name}: ${id}`);
    }
  }

  const context = vm.createContext({ document: { addEventListener() {} } });
  context.window = context;
  for (const filename of ['shared/web-hangul-ime.js', 'shared/web-ime-core.js']) {
    vm.runInContext(fs.readFileSync(path.join(root, filename), 'utf8'), context, { filename });
  }
  const core = context.TangliengimImeCore;
  const index = core.createDictionaryIndex(data.entries);
  const control = {
    value: '', selectionStart: 0, selectionEnd: 0,
    addEventListener() {},
  };
  const controller = core.createTextImeController({
    control, dictionaryIndex: index, entries: data.entries,
  });
  const candidateOrder = [];
  const visibleMenuOrder = [];
  for (const [key, candidates] of index.candidatesByReading) {
    candidateOrder.push([key, candidates.map(entry => entry.id)]);
    control.value = key;
    control.selectionStart = key.length;
    control.selectionEnd = key.length;
    const menu = controller.findCandidates().map(({ entry }) => (
      entry.generatedCandidate
        ? ['fallback', entry.hanri, entry.reading]
        : [entry.id, entry.hanri, entry.reading]
    ));
    visibleMenuOrder.push([key, menu]);
  }

  return {
    formatVersion: 7,
    provenance: {
      sourceSha256: data.sourceSha256,
      categorySourceSha256: data.categorySourceSha256,
      entryCount: data.entries.length,
    },
    jsonSections: {
      entries: objectDigest(data.entries.map(stableEntry)),
      entryIdentity: objectDigest(data.entries.map(entry => ({
        id: entry.id,
        entryType: entry.entryType,
        sourceEntryId: entry.raw.entry_id,
        autoSandhi: Boolean(entry.autoSandhi),
      }))),
      indexes: objectDigest(data.indexes),
      categories: objectDigest(data.categories),
      runtime: objectDigest(data.runtime),
      counts: objectDigest(data.counts),
      skippedRows: objectDigest(data.skippedRows),
      lookupMetadata: objectDigest(data.entries.map(entry => ({
        id: entry.id, simplified: entry.simplified,
        mandarin_trad: entry.mandarin_trad, mandarin_simp: entry.mandarin_simp,
      }))),
      staticRanking: objectDigest(data.entries.map(entry => ({id:entry.id,canonicalKey:entry.canonicalKey,staticRanks:entry.staticRanks,staticOrder:entry.staticOrder}))),
    },
    candidateOrder,
    visibleMenuOrder,
  };
}

function firstDifference(expected, actual) {
  for (let index = 0; index < Math.max(expected.length, actual.length); index += 1) {
    if (JSON.stringify(expected[index]) !== JSON.stringify(actual[index])) {
      return `at key ${JSON.stringify(expected[index]?.[0] || actual[index]?.[0])}:\n` +
        `expected ${JSON.stringify(expected[index])}\nactual   ${JSON.stringify(actual[index])}`;
    }
  }
  return '';
}

// The reading keys that were added, removed or changed, so a failure names exactly
// what an edit affected.
function keyedDifferences(expected, actual, limit = 20) {
  const before = new Map(expected.map(([key, value]) => [key, JSON.stringify(value)]));
  const after = new Map(actual.map(([key, value]) => [key, JSON.stringify(value)]));
  const lines = [];
  for (const [key, value] of after) {
    if (!before.has(key)) lines.push(`+ ${JSON.stringify(key)} ${value}`);
    else if (before.get(key) !== value) lines.push(`~ ${JSON.stringify(key)}\n    expected ${before.get(key)}\n    actual   ${value}`);
  }
  for (const [key, value] of before) {
    if (!after.has(key)) lines.push(`- ${JSON.stringify(key)} ${value}`);
  }
  if (!lines.length) return '';
  const shown = lines.slice(0, limit).join('\n');
  return lines.length > limit ? `${shown}\n… and ${lines.length - limit} more keys` : shown;
}

function main() {
  const data = loadDictionaryData(jsonPath);
  for (const [source, hash] of [
    [data.source, data.sourceSha256],
    [data.idRegistrySource, data.idRegistrySourceSha256],
    [data.categorySource, data.categorySourceSha256],
    [data.prioritySource, data.prioritySourceSha256],
  ]) {
    assert.equal(digest(fs.readFileSync(path.join(root, source))), hash,
      `Generated JSON is stale for ${source}; rebuild it first`);
  }
  const actual = snapshot(data);
  const beforeIndex = process.argv.indexOf('--compare-before');
  if (beforeIndex !== -1) {
    const before = loadDictionaryData(process.argv[beforeIndex + 1]);
    const previous = snapshot(before);
    for (const name of ['entries', 'entryIdentity', 'categories', 'runtime', 'counts', 'skippedRows']) {
      assert.equal(actual.jsonSections[name], previous.jsonSections[name], `Unrelated migration regression: ${name}`);
    }
    for (const [name, index] of Object.entries(before.indexes)) {
      if (name === 'byMandarinTrad' || name === 'byMandarinSimp') {
        for (const [key, ids] of Object.entries(index)) {
          const previousIds = new Set(ids);
          assert.deepEqual(data.indexes[name][key]?.filter(id => previousIds.has(id)), ids,
            `Existing Mandarin mappings lost or reordered: ${name} ${key}`);
        }
      } else {
        assert.deepEqual(data.indexes[name], index, `Existing lookup index changed: ${name}`);
      }
    }
    const current = new Map(data.entries.map(entry => [entry.id, entry]));
    for (const entry of before.entries) {
      const now = current.get(entry.id);
      assert.ok(now, `Entry disappeared: ${entry.id}`);
      assert.equal(now.simplified, entry.simplified, `Hokkien Simplified changed: ${entry.id}`);
      for (const name of ['mandarin_trad', 'mandarin_simp']) {
        if (entry[name]) assert.equal(now[name], entry[name], `Populated Mandarin value changed: ${entry.id}`);
      }
    }
    assert.equal(firstDifference(previous.candidateOrder, actual.candidateOrder), '', 'Candidate order changed');
    assert.equal(firstDifference(previous.visibleMenuOrder, actual.visibleMenuOrder), '', 'Visible candidate order changed');
    console.log('Pre-migration lexical, identity, lookup, audio/runtime and candidate snapshots match.');
  }
  if (capture) {
    fs.mkdirSync(path.dirname(fixturePath), { recursive: true });
    fs.writeFileSync(fixturePath, JSON.stringify(actual, null, 2) + '\n');
    console.log(`Captured ${actual.candidateOrder.length} candidate keys and ${data.entries.length} JSON entries.`);
    return;
  }

  const expected = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
  assert.equal(expected.formatVersion, actual.formatVersion,
    'Baseline format changed; verify the migration before capturing a new baseline');
  for (const [name, digestValue] of Object.entries(expected.jsonSections)) {
    assert.equal(actual.jsonSections[name], digestValue, `Semantic JSON changed: ${name}`);
  }
  for (const section of ['candidateOrder', 'visibleMenuOrder']) {
    const difference = keyedDifferences(expected[section], actual[section]);
    assert.equal(difference, '', `${section} changed\n${difference}`);
  }
  console.log(`Baseline matched: ${actual.candidateOrder.length} candidate keys, ${data.entries.length} JSON entries.`);
}

main();
