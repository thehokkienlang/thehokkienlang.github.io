// Run the real shared engine and app bootstrap without browser dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..', '_site');
const data = JSON.parse(fs.readFileSync(path.join(root, 'public/data/hokkien-hanri-dict.json'), 'utf8'));

function element() {
  return {
    value: '', textContent: '', selectionStart: 0, selectionEnd: 0, hidden: false,
    style: {}, children: [],
    classList: { add() {}, remove() {}, toggle() {} },
    addEventListener() {}, setAttribute() {}, focus() {},
    setSelectionRange(start, end) { this.selectionStart = start; this.selectionEnd = end; },
    replaceChildren(...items) { this.children = items; },
    append(...items) { this.children.push(...items); },
  };
}

async function loadApp(route, script) {
  const elements = new Map();
  const requests = [];
  const context = vm.createContext({
    console, setTimeout, clearTimeout,
    document: {
      querySelector(selector) {
        if (!elements.has(selector)) elements.set(selector, element());
        return elements.get(selector);
      },
      createElement: element,
      createDocumentFragment: element,
      createTextNode: text => ({ textContent: text }),
    },
    async fetch(url, options) {
      requests.push({ url, options });
      const parsed = new URL(url, `https://example.test/${route}/`);
      const file = path.join(root, decodeURIComponent(parsed.pathname));
      assert.ok(fs.existsSync(file), `Missing fetched resource: ${parsed.pathname}`);
      return { ok: true, json: async () => JSON.parse(fs.readFileSync(file, 'utf8')) };
    },
  });
  context.window = context;
  for (const file of ['shared/web-hangul-ime.js', 'shared/web-ime-core.js', `${route}/${script}`]) {
    vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context, { filename: file });
  }
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(requests[0].url, '/public/data/hokkien-hanri-dict.json');
  assert.equal(requests[0].options.cache, 'no-cache');
  assert.ok(vm.runInContext('state.entries.length > 2000', context));
  const controllerName = route === 'ime' ? 'imeController' : 'searchImeController';
  assert.ok(vm.runInContext(`${controllerName}.candidatesByReading.size > 0`, context));
  assert.equal(vm.runInContext(`(() => {
    const composer = new TangliengimHangulIme.Composer();
    for (const key of 'rksk') composer.processChar(key);
    return composer.text();
  })()`, context), '\uac00\ub098');
  return { context, elements };
}

(async () => {
  const dictionary = await loadApp('dictionary', 'app.js');
  assert.equal(dictionary.elements.get('#results').children.length, 0, 'Empty search must stay empty');
  assert.ok(!dictionary.elements.get('#dataStatus').textContent.includes('failed'));
  assert.deepEqual(
    vm.runInContext('state.categories.map(category => category.id).join(",")', dictionary.context),
    'food,place-names'
  );
  for (const category of ['food', 'place-names']) {
    assert.ok(
      vm.runInContext(`(() => {
        state.activeCategory = ${JSON.stringify(category)};
        const result = searchGroups();
        const expected = state.categories.find(item => item.id === ${JSON.stringify(category)}).entryCount;
        return result.rawQuery === '' && result.total === expected && result.shown.length === Math.min(10, expected);
      })()`, dictionary.context),
      `${category} must browse all categorised entries with ten-entry pagination`
    );
  }
  vm.runInContext('state.activeCategory = ""', dictionary.context);
  assert.equal(
    vm.runInContext('TangliengimImeCore.normalizeEnglishSearch("neighbor")', dictionary.context),
    'neighbour',
    'American spellings must normalize to the British dictionary spelling'
  );
  assert.ok(
    vm.runInContext(`(() => {
      const group = state.groups.find(item => item.readings.some(reading => reading.english === 'neighbour'));
      return group && scoreGroup(group, queryVariants('neighbor'), 'lomari') > 0;
    })()`, dictionary.context),
    'American neighbor must find the British-only neighbour entry'
  );
  assert.ok(
    vm.runInContext(`state.groups.some(group => group.readings.some(reading => reading.english === 'neighbour'))`, dictionary.context),
    'The dictionary must display neighbour'
  );
  assert.ok(
    !vm.runInContext(`state.groups.some(group => group.readings.some(reading => /(^|;\\s*)neighbor($|;)/.test(reading.english || '')))`, dictionary.context),
    'The dictionary must not display neighbor as a separate spelling variant'
  );
  assert.ok(
    vm.runInContext(`state.entries.some(entry => entry.correctedFrom && entry.raw?.reading?.endsWith('*'))`, dictionary.context),
    'Typo-correction rows must remain loaded for the IME'
  );
  assert.ok(
    vm.runInContext(`state.groups.every(group => group.readings.every(reading => !reading.correctedFrom))`, dictionary.context),
    'Typo-correction rows must not appear as dictionary entries'
  );
  assert.ok(
    vm.runInContext(`(() => {
      const key = TangliengimImeCore.normalizeText(
        TangliengimHangulIme.normalizeReadingBase('능잡1*')
      );
      return searchImeController.candidatesByReading.get(key)?.some(entry => entry.correctedFrom === '능잡1');
    })()`, dictionary.context),
    'The starred 능잡 typo must remain available to the IME candidate index'
  );
  const { context, elements } = await loadApp('ime', 'ime.js');
  assert.ok(elements.get('#statusLine').textContent.includes('entries loaded'));
  for (const [word, taipei, singapore] of [
    ['\u7e3d\u7d71', '1,2', '4,2'],
    ['\u7e3d\u7763', '1,3', '4,3'],
    ['\u7c73\u7c89\u7cbf', null, '5,4,2'],
  ]) {
    assert.ok(data.entries.some(entry => entry.hanri === word), `Missing sandhi fixture: ${word}`);
    for (const [mode, expected] of [['taipei', taipei], ['singapore', singapore]]) {
      if (!expected) continue;
      const plan = vm.runInContext(`setSandhiMode(${JSON.stringify(mode)}); audioPlanFromText(${JSON.stringify(word)})`, context);
      assert.equal(plan.segments.map(segment => segment.tone).join(','), expected, `${word}: ${mode}`);
      assert.ok(plan.segments.every(segment => segment.file.startsWith('/public/audio/')));
    }
  }
  console.log('OK: both app bootstraps load shared data, shared Hangul composition works, Taipei/Singapore audio paths and tones match.');
})().catch(error => { console.error(error); process.exitCode = 1; });
