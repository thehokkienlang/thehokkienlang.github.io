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
