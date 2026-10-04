// Capture or check dictionary behaviour without depending on row-derived IDs.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

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
  const position = new Map(data.entries.map((entry, index) => [entry.id, index]));
  assert.equal(position.size, data.entries.length, 'Generated entry IDs must be unique');
  const indexesByPosition = Object.fromEntries(Object.entries(data.indexes).map(([name, index]) => [
    name,
    Object.fromEntries(Object.entries(index).map(([key, ids]) => [
      key,
      ids.map(id => {
        assert.ok(position.has(id), `Unknown entry ID in ${name}: ${id}`);
        return position.get(id);
      }),
    ])),
  ]));

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
    candidateOrder.push([key, candidates.map(entry => position.get(entry.id))]);
    control.value = key;
    control.selectionStart = key.length;
    control.selectionEnd = key.length;
    const menu = controller.findCandidates().map(({ entry }) => (
      entry.generatedCandidate
        ? ['fallback', entry.hanri, entry.reading]
        : [position.get(entry.id), entry.hanri, entry.reading]
    ));
    visibleMenuOrder.push([key, menu]);
  }

  return {
    formatVersion: 6,
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
      indexes: objectDigest(indexesByPosition),
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

function main() {
  const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
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
    const before = JSON.parse(fs.readFileSync(process.argv[beforeIndex + 1], 'utf8'));
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
    for (const [i, entry] of before.entries.entries()) {
      assert.equal(data.entries[i].simplified, entry.simplified, 'Hokkien Simplified changed');
      for (const name of ['mandarin_trad', 'mandarin_simp']) {
        if (entry[name]) assert.equal(data.entries[i][name], entry[name], `Populated Mandarin value changed: ${entry.id}`);
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
  if (expected.formatVersion < actual.formatVersion) {
    for (const [name, digestValue] of Object.entries(expected.jsonSections)) {
      if (name === 'entryIdentity') continue;
      assert.equal(actual.jsonSections[name], digestValue, `Behavior section changed during stable-ID migration: ${name}`);
    }
  } else {
    assert.equal(actual.formatVersion, expected.formatVersion, 'Baseline format changed');
    assert.deepEqual(actual.jsonSections, expected.jsonSections, 'Semantic JSON changed');
  }
  for (const section of ['candidateOrder', 'visibleMenuOrder']) {
    const difference = firstDifference(expected[section], actual[section]);
    assert.equal(difference, '', `${section} changed ${difference}`);
  }
  if (expected.formatVersion !== actual.formatVersion) {
    throw new Error('Baseline schema changed; verify the migration before capturing the new metadata baseline');
  }
  console.log(`Baseline matched: ${actual.candidateOrder.length} candidate keys, ${data.entries.length} JSON entries.`);
}

main();
