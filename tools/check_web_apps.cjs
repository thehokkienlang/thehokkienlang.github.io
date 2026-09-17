// Run the real shared engine and app bootstrap without browser dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..', '_site');
const data = JSON.parse(fs.readFileSync(path.join(root, 'public/data/hokkien-hanri-dict.json'), 'utf8'));
const legacyParity = JSON.parse(
  fs.readFileSync(path.resolve(__dirname, '..', 'tests/fixtures/legacy-ime-parity-reference.json'), 'utf8')
);

function element() {
  return {
    value: '', textContent: '', selectionStart: 0, selectionEnd: 0, hidden: false,
    style: {}, children: [], scrollTop: 0, scrollHeight: 0,
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
  const files = ['shared/web-hangul-ime.js', 'shared/web-ime-core.js'];
  if (route === 'ime') files.push('ime/lomari-preview.js');
  files.push(`${route}/${script}`);
  for (const file of files) {
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
  assert.equal(vm.runInContext(`(() => {
    const composer = new TangliengimHangulIme.Composer();
    composer.processChar("'");
    return composer.text();
  })()`, context), '’');
  assert.ok(vm.runInContext(`(() => {
    const composer = new TangliengimHangulIme.Composer({ shouldAutocorrectEToYe: () => true });
    for (const key of 'dpd') composer.processChar(key);
    const corrected = composer.text() === '옝';
    composer.processChar('k');
    return corrected && composer.text() === '에아';
  })()`, context), 'Local TSV-guarded ㅔ/ㅖ correction and onset undo must be shared');
  assert.ok(vm.runInContext(`(() => {
    const composer = new TangliengimHangulIme.Composer();
    for (const key of 'dkn') composer.processChar(key);
    composer.processChar('1');
    const toned = composer.text() === 'ᄋᅷˆ';
    composer.setText('ᄋᅷ', 1);
    const snapped = composer.displayCursorPos() === 2;
    composer.backspace();
    return toned && snapped && composer.text() === '';
  })()`, context), 'Decomposed Hokkien syllables must edit atomically like the Local IME');
  return { context, elements };
}

(async () => {
  const dictionary = await loadApp('dictionary', 'app.js');
  assert.equal(dictionary.elements.get('#results').children.length, 0, 'Empty search must stay empty');
  assert.ok(!dictionary.elements.get('#dataStatus').textContent.includes('failed'));
  assert.ok(
    vm.runInContext(`(() => {
      const index = TangliengimImeCore.createDictionaryIndex(state.entries);
      return searchImeController.dictionaryIndex === state.dictionaryIndex
        && index.findHanriEntry('用心肝', 0)?.hanri === '用'
        && index.findHangulOverrideAt('릐호', 0)?.entry?.reading === '릐1호2';
    })()`, dictionary.context),
    'Dictionary candidates and shared priority/override lookup must use one shared index'
  );
  assert.ok(
    vm.runInContext(`(() => {
      setInputMode('hanri-hangul');
      const entry = state.entries.find(item => item.hanri && item.kind !== 'hangul_override');
      searchInput.value = entry.readingBase;
      searchInput.selectionStart = entry.readingBase.length;
      searchInput.selectionEnd = entry.readingBase.length;
      searchImeController.composer.setText(entry.readingBase, entry.readingBase.length);
      searchImeController.renderCandidates();
      return searchImeController.activeCandidates.length > 0 && imeCandidates.children.length > 0 && !imeCandidates.hidden;
    })()`, dictionary.context),
    'Dictionary Hanri candidates must render as a visible popup list'
  );
  vm.runInContext(`searchInput.value = ''; searchImeController.composer.setText('', 0); setInputMode('lomari')`, dictionary.context);
  assert.equal(
    vm.runInContext(`(() => {
      searchImeController.onUpdate = () => {};
      searchImeController.renderCandidates = () => {};
      searchInput.value = "lang'";
      searchInput.selectionStart = 5;
      searchInput.selectionEnd = 5;
      searchImeController.handleInput();
      return searchInput.value;
    })()`, dictionary.context),
    'lang’',
    'Dictionary input must normalize a pasted straight apostrophe in Lomari mode'
  );
  vm.runInContext(`searchInput.value = ''; searchInput.selectionStart = 0; searchInput.selectionEnd = 0`, dictionary.context);
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
    vm.runInContext('TangliengimImeCore.normalizeEnglishSearch("neighbors")', dictionary.context),
    'neighbours',
    'American spellings must normalize to the British dictionary spelling'
  );
  assert.ok(
    vm.runInContext(`(() => {
      const group = state.groups.find(item => item.readings.some(reading => /(^|;\\s*)neighbours($|;)/.test(reading.english || '')));
      return group && scoreGroup(group, queryVariants('neighbors'), 'lomari') > 0;
    })()`, dictionary.context),
    'American neighbors must find the British-only neighbours entry'
  );
  assert.ok(
    vm.runInContext(`state.groups.some(group => group.readings.some(reading => /(^|;\\s*)neighbours($|;)/.test(reading.english || '')))`, dictionary.context),
    'The dictionary must display neighbours'
  );
  assert.ok(
    !vm.runInContext(`state.groups.some(group => group.readings.some(reading => /(^|;\\s*)neighbors($|;)/.test(reading.english || '')))`, dictionary.context),
    'The dictionary must not display neighbors as a separate spelling variant'
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
  assert.equal(elements.get('#statusLine').textContent, '');
  assert.equal(elements.get('#statusLine').hidden, true, 'Successful dictionary loading must stay visually quiet');
  assert.ok(
    vm.runInContext(
      `imeController.dictionaryIndex === dictionaryIndex && dictionaryIndex.findHanriEntry('用心肝', 0)?.hanri === '用'`,
      context
    ),
    'Web IME must consume the shared dictionary index for priority Hanri matching'
  );
  assert.equal(elements.get('#keyboardLayout').children.length, 5, 'IME keyboard guide must render five key rows');
  assert.equal(
    vm.runInContext('JSON.stringify(GUIDE_ROWS)', context),
    JSON.stringify([
      ['1', '2', '4', '5', 'Backspace'],
      [...'qwertyuiop'],
      [...'asdfghjkl'],
      ['Shift', ...'zxcvbnm', '’'],
      ['Space'],
    ]),
    'IME keyboard guide must keep special keys in the shared layout'
  );
  assert.equal(
    vm.runInContext(`(() => {
      imeController.clear();
      imeController.insertText('rk');
      return imeText.value;
    })()`, context),
    '가',
    'Clickable keyboard input must use the shared Hangul composer'
  );
  assert.equal(
    vm.runInContext(`(() => {
      imeController.clear();
      imeController.insertText("랑'");
      return imeText.value;
    })()`, context),
    '랑’',
    'Web IME input must normalize straight apostrophes'
  );
  assert.ok(
    vm.runInContext(`(() => {
      const entry = state.entries.find(item => item.hanri && item.kind !== 'hangul_override');
      imeController.composer.setText(entry.readingBase, entry.readingBase.length);
      imeController.updateControlFromComposer();
      return imeController.activeCandidates.length > 0 && candidateBar.children.length > 0 && !candidateBar.hidden;
    })()`, context),
    'IME Hanri candidates must render as a visible popup list'
  );
  assert.equal(
    vm.runInContext(`findHanriEntry('用心肝', 0)?.hanri || ''`, context),
    '用',
    'Web Hanri segmentation must honour the Local IME priority path'
  );
  assert.ok(
    vm.runInContext(`state.unitRoman.size > 0 && state.rawHangulAudio.size > 0 && state.jamoLomari.size > 0 && state.jamoAudio.size > 0`, context),
    'Web IME must load Local-IME-derived runtime pronunciation metadata'
  );
  assert.ok(
    vm.runInContext(`(() => {
      imeController.composer.setText('랑', 1);
      imeController.updateControlFromComposer();
      if (imeController.activeCandidates.length < 2) return false;
      let prevented = false;
      const event = {
        key: 'Tab', shiftKey: false, ctrlKey: false, metaKey: false, altKey: false,
        isComposing: false, preventDefault() { prevented = true; },
      };
      imeController.handleKeydown(event);
      imeController.handleCursorChange({ type: 'keyup', key: 'Tab' });
      return prevented && imeController.activeCandidateIndex === 1;
    })()`, context),
    'Tab must advance the candidate highlight without accepting it'
  );
  assert.ok(
    vm.runInContext(`(() => {
      let prevented = false;
      const event = {
        key: 'Escape', shiftKey: false, ctrlKey: false, metaKey: false, altKey: false,
        isComposing: false, preventDefault() { prevented = true; },
      };
      imeController.handleKeydown(event);
      imeController.handleCursorChange({ type: 'keyup', key: 'Escape' });
      return prevented && imeController.activeCandidates.length === 0 && candidateBar.hidden;
    })()`, context),
    'Escape must dismiss the popup while keeping the typed Hangul'
  );
  assert.ok(
    vm.runInContext(`(() => {
      imeController.clear();
      let prevented = false;
      imeController.handleKeydown({
        key: 'Tab', shiftKey: false, ctrlKey: false, metaKey: false, altKey: false,
        isComposing: false, preventDefault() { prevented = true; },
      });
      return !prevented;
    })()`, context),
    'Tab must retain normal browser focus navigation when no candidate menu is open'
  );
  for (const [input, expected] of [
    ['愛릐', 'ài-lì'],
    ['릐호', 'lî-hò'],
    ['到尾仔 來到CMPB', 'kàu-buê-à lai-kàu-CMPB'],
    ['賣票', 'boe-phio'],
    ['廈門', 'e-mńg'],
    ['十殿閻君', 'jap-tien-giam-kûn'],
    ['ㅏ', 'â'],
    ['ㄱ', 'kī-yôrk'],
  ]) {
    vm.runInContext(`imeText.value = ${JSON.stringify(input)}; updateLomariPreview()`, context);
    assert.equal(elements.get('#lomariPreview').textContent, expected, `Lomari preview: ${input}`);
  }
  vm.runInContext(`imeText.value = '米粉粿'; setSandhiMode('taipei')`, context);
  const taipeiLomari = elements.get('#lomariPreview').textContent;
  vm.runInContext(`setSandhiMode('singapore')`, context);
  assert.equal(elements.get('#lomariPreview').textContent, taipeiLomari, 'Singapore must not alter the Lomari preview');
  vm.runInContext('imeController.clear()', context);
  assert.equal(elements.get('#lomariPreview').textContent, '', 'Clear must empty the Lomari preview');
  for (const [input, tones] of [['ㅏ', '1'], ['ㄱ', '5,1'], ['시', '5'], ['시4', '4']]) {
    const plan = vm.runInContext(`audioPlanFromText(${JSON.stringify(input)})`, context);
    assert.equal(plan.segments.map(segment => segment.tone).join(','), tones, `${input}: Local audio reading`);
    assert.equal(plan.missing.join(','), '', `${input}: no false missing-audio warning`);
  }
  vm.runInContext(`setSandhiMode('taipei')`, context);
  for (const [input, tones] of [['릐', '2'], ['릐호', '1,2']]) {
    const plan = vm.runInContext(`audioPlanFromText(${JSON.stringify(input)})`, context);
    assert.equal(plan.segments.map(segment => segment.tone).join(','), tones, `${input}: longest Hangul override audio`);
    assert.equal(plan.missing.join(','), '', `${input}: Hangul override audio is available`);
  }
  for (const fixture of legacyParity.lomari) {
    vm.runInContext(`imeText.value = ${JSON.stringify(fixture.reading)}; updateLomariPreview()`, context);
    assert.equal(
      elements.get('#lomariPreview').textContent,
      fixture.expected,
      `Legacy Lomari parity: ${fixture.reading}`
    );
  }
  for (const fixture of legacyParity.citationSandhi) {
    const actual = vm.runInContext(`(() => {
      const text = ${JSON.stringify(fixture.reading)};
      let output = "";
      for (let index = 0; index < text.length;) {
        const unit = TangliengimImeCore.readingUnitAt(text, index);
        if (!unit?.canCarryTone) {
          output += text[index];
          index += 1;
          continue;
        }
        const end = TangliengimImeCore.readingUnitToneEnd(text, unit);
        const tone = TangliengimHangulIme.normalizeReadingToneKey(text.slice(index, end)).at(-1);
        output += unit.text + TangliengimImeCore.citationToTaipeiSandhiTone(unit.text, tone);
        index = end;
      }
      return output;
    })()`, context);
    assert.equal(actual, fixture.expected, `Legacy citation-to-sandhi parity: ${fixture.reading}`);
  }
  for (const fixture of legacyParity.overrides) {
    const actual = vm.runInContext(`(() => {
      const text = ${JSON.stringify(fixture.text)};
      let output = "";
      for (let index = 0; index < text.length;) {
        const override = findHangulOverrideAt(text, index);
        if (override?.entry) {
          output += override.entry.reading;
          index = override.end;
          continue;
        }
        const unit = TangliengimImeCore.readingUnitAt(text, index);
        if (unit?.canCarryTone) {
          output += text.slice(index, TangliengimImeCore.readingUnitToneEnd(text, unit));
          index = TangliengimImeCore.readingUnitToneEnd(text, unit);
          continue;
        }
        output += text[index];
        index += 1;
      }
      return output;
    })()`, context);
    assert.equal(actual, fixture.expected, `Legacy Hangul-override parity: ${fixture.text}`);
  }
  for (const fixture of legacyParity.composition || []) {
    const actual = vm.runInContext(`(() => {
      const composer = new TangliengimHangulIme.Composer({
        shouldAutocorrectEToYe: (reading) => {
          const key = TangliengimImeCore.normalizeText(
            TangliengimHangulIme.normalizeReadingBase(reading)
          );
          return Boolean(dictionaryIndex.candidatesByReading.get(key)?.length);
        },
      });
      for (const step of ${JSON.stringify(fixture.steps)}) {
        for (const key of step.keys || '') composer.processChar(key);
        for (let count = 0; count < (step.backspace || 0); count += 1) composer.backspace();
        for (let count = 0; count < (step.left || 0); count += 1) composer.moveLeft();
        for (let count = 0; count < (step.right || 0); count += 1) composer.moveRight();
      }
      return composer.text();
    })()`, context);
    assert.equal(actual, fixture.expected, `Legacy composition parity: ${JSON.stringify(fixture.steps)}`);
  }
  for (const fixture of legacyParity.candidates || []) {
    const actual = JSON.parse(vm.runInContext(`(() => {
      const reading = ${JSON.stringify(fixture.reading)};
      imeText.value = reading;
      imeText.selectionStart = reading.length;
      imeText.selectionEnd = reading.length;
      imeController.composer.setText(reading, reading.length);
      imeController.renderCandidates();
      return JSON.stringify(imeController.activeCandidates.map(({ entry }) => ({
        hanri: entry.hanri,
        reading: entry.reading,
      })));
    })()`, context));
    assert.deepEqual(actual, fixture.expected, `Legacy candidate parity: ${fixture.reading}`);
  }
  for (const fixture of legacyParity.audio) {
    for (const [mode, expected] of Object.entries(fixture.expected)) {
      const plan = vm.runInContext(
        `setSandhiMode(${JSON.stringify(mode)}); audioPlanFromText(${JSON.stringify(fixture.input)})`,
        context
      );
      const actual = JSON.parse(JSON.stringify({
        segments: plan.segments.map((segment) => ({
          unit: segment.unit,
          tone: String(segment.tone),
          trimStart: Boolean(segment.trimStart),
          trimEnd: Boolean(segment.trimEnd),
          englishClusterHelper: Boolean(segment.englishClusterHelper),
        })),
        unknown: plan.missing,
      }));
      assert.deepEqual(actual, expected, `Legacy audio parity: ${fixture.input} (${mode})`);
    }
  }
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
  console.log('OK: both app bootstraps load shared data; composition, candidates, and Taipei/Singapore audio match the desktop reference.');
})().catch(error => { console.error(error); process.exitCode = 1; });
