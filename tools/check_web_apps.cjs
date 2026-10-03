// Run the real shared engine and app bootstrap without browser dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const sourceMode = process.argv.includes('--source');
const root = sourceMode
  ? path.resolve(__dirname, '..')
  : path.resolve(__dirname, '..', '_site');
const appRoot = sourceMode ? 'apps' : '';
const data = JSON.parse(fs.readFileSync(path.join(root, 'public/data/hokkien-hanri-dict.json'), 'utf8'));
const legacyParity = JSON.parse(
  fs.readFileSync(path.resolve(__dirname, '..', 'tests/fixtures/legacy-ime-parity-reference.json'), 'utf8')
);
for (const [route, script] of [['dictionary', 'app.js'], ['ime', 'ime.js']]) {
  const source = fs.readFileSync(path.join(root, appRoot, route, script), 'utf8');
  assert.match(source, /TangliengimWebAudio/, `${route} must use the shared browser audio player`);
  assert.doesNotMatch(source, /function audioTrimFrames\(/, `${route} must not fork browser audio processing`);
  assert.match(source, /createCandidatePopupPositioner/, `${route} must use shared candidate placement`);
}

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
      addEventListener() {},
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
  const files = ['shared/web-hangul-ime.js', 'shared/web-ime-core.js', 'shared/web-audio-player.js'];
  if (route === 'ime') files.push('shared/web-phonetic-output.js');
  files.push(path.posix.join(appRoot, route, script));
  for (const file of files) {
    vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context, { filename: file });
  }
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(requests[0].url, '/public/data/hokkien-hanri-dict.json');
  assert.equal(requests[0].options.cache, 'no-cache');
  assert.ok(vm.runInContext('state.entries.length > 2000', context));
  const controllerName = route === 'ime' ? 'imeController' : 'searchImeController';
  assert.ok(vm.runInContext(`${controllerName}.candidatesByReading.size > 0`, context));
  assert.ok(vm.runInContext('typeof TangliengimImeCore.createCandidatePopupPositioner === "function"', context));
  assert.ok(vm.runInContext('typeof TangliengimWebAudio.createPlayer === "function"', context));
  assert.ok(vm.runInContext(`(() => {
    const index = TangliengimImeCore.createDictionaryIndex(state.entries);
    const kah = state.entries.find(entry => entry.id === 'U+5FA6_00');
    return kah?.hanri === '徦' && kah.reading === '갛' && kah.entryType === 'lexical'
      && index.findHanriEntry('徦', 0)?.id === kah.id
      && [...index.candidatesByReading.values()].some(entries => entries.some(entry => entry.id === kah.id))
      && !state.entries.some(entry => entry.id === 'U+AC00_00')
      && state.entries.find(entry => entry.id === 'U+5E95_00')?.reading === '되2'
      && state.entries.find(entry => entry.id === 'U+5E95_01')?.reading === '도2'
      && state.entries.find(entry => entry.id === 'U+54EA_U+88E1_00')?.english === 'where';
  })()`, context), `${route} must consume the approved v3.1 forms and active IDs`);
  assert.ok(vm.runInContext(`(() => {
    const fragment = TangliengimImeCore.renderToneOverlayMarks('칟토', [
      { start: 0, end: 1, hangul: '칟', reading: '칟1' },
      { start: 1, end: 2, hangul: '토', reading: '토4' },
    ]);
    const marks = [];
    let duplicatedReadingText = false;
    const visit = node => {
      if (node?.className === 'tone-overlay-mark') marks.push(node.textContent);
      if (node?.textContent === '칟' || node?.textContent === '토') duplicatedReadingText = true;
      for (const child of node?.children || []) visit(child);
    };
    visit(fragment);
    return !duplicatedReadingText && marks.join('') === 'ꞈˏ';
  })()`, context), 'IME tone overlay must keep marks out of the base Hangul text and inline width');
  assert.ok(vm.runInContext(`(() => {
    const composer = new TangliengimHangulIme.Composer();
    composer.setText('가ᄋᅷ나', 4);
    const positions = [];
    composer.moveLeft(); positions.push(composer.displayCursorPos());
    composer.moveLeft(); positions.push(composer.displayCursorPos());
    composer.moveLeft(); positions.push(composer.displayCursorPos());
    composer.moveRight(); positions.push(composer.displayCursorPos());
    composer.moveRight(); positions.push(composer.displayCursorPos());
    composer.moveRight(); positions.push(composer.displayCursorPos());
    return positions.join(',') === '3,1,0,1,3,4';
  })()`, context), 'Left and Right must cross each complete Hangul syllable in one step');
  assert.equal(
    vm.runInContext(`TangliengimWebAudio.legacyPlaybackSegments([
      { tone: '3' }, { tone: '4' }, { tone: '3' }, { tone: '3' },
    ]).map(segment => segment.speed).join(',')`, context),
    '1.1,1.03,1.1,1.1',
    'Web playback must use the legacy multi-syllable speed factors'
  );
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
  assert.ok(vm.runInContext(`(() => {
    const groups = state.groups.filter(group => group.search.simplified);
    return groups.length > 2500 && groups.every(group =>
      scoreGroup(group, [group.search.simplified], 'lomari') > 0
      && scoreGroup(group, [group.search.simplifiedRaw], 'lomari') > 0
      && group.readings.every(entry => entry.id && entry.hanri === group.hanri)
    );
  })()`, dictionary.context), 'Simplified aliases must search existing canonical entries');
  assert.ok(vm.runInContext(`(() => {
    const entry = state.entries.find(item => item.hanri === '台灣' && !item.autoSandhi);
    searchInput.value = '台湾';
    return entry && searchGroups().shown.some(group => group.readings.some(reading => reading.id === entry.id))
      && entry.hanri === '台灣';
  })()`, dictionary.context), '台湾 must find and display canonical 台灣');
  vm.runInContext("searchInput.value = ''", dictionary.context);
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
      searchImeController.onUpdate = () => {};
      searchImeController.handleInput({ inputType: 'insertText' });
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
  const imeMarkup = fs.readFileSync(path.join(root, appRoot, 'ime', 'index.html'), 'utf8');
  for (const attribute of [
    'autocorrect="off"',
    'spellcheck="false"',
    'autocomplete="off"',
    'writingsuggestions="false"',
  ]) {
    assert.ok(imeMarkup.includes(attribute), `Mobile IME input must include ${attribute}`);
  }
  assert.equal(elements.get('#statusLine').textContent, '');
  assert.equal(elements.get('#statusLine').hidden, true, 'Successful dictionary loading must stay visually quiet');
  assert.ok(
    vm.runInContext(
      'typeof TangliengimPhoneticOutput?.createRenderer === "function" && typeof TangliengimPhoneticOutput?.createAudioPlanner === "function"',
      context
    ),
    'Lomari rendering and audio planning must come from the shared phonetic engine'
  );
  assert.ok(
    vm.runInContext(
      `imeController.dictionaryIndex === dictionaryIndex && dictionaryIndex.findHanriEntry('用心肝', 0)?.hanri === '用'`,
      context
    ),
    'Web IME must consume the shared dictionary index for priority Hanri matching'
  );
  assert.equal(elements.get('#keyboardLayout').children.length, 5, 'IME keyboard guide must render five key rows');
  assert.equal(
    elements.has('#keyboardSwitchHint'),
    false,
    'Web IME must not render a prompt recommending a particular system keyboard'
  );
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
      const shortcuts = [
        ['앚', 'ᄋᅷ'], ['얒', 'ᄋᆤ'],
      ];
      const preserved = shortcuts.every(([input]) =>
        TangliengimHangulIme.normalizeDisallowedFinalInputText(input) === input
      );
      const continued = (() => {
        const composer = new TangliengimHangulIme.Composer();
        for (const jamo of 'ㅇㅏㅈ') composer.processNativeCompat(jamo);
        if (composer.text() !== '앚') return false;
        composer.processNativeCompat('ㅐ');
        return composer.text() === '아재';
      })();
      const candidateNormalized = [
        ['ㅏㅜ', 'ᅟᅷ'], ['ㅑㅜ', 'ᄋᆤ'],
        ['아ㅜ', 'ᄋᅷ'], ['앚', 'ᄋᅷ'], ['야ㅜ', 'ᄋᆤ'], ['얒', 'ᄋᆤ'],
      ].every(([input, expected]) =>
        TangliengimHangulIme.normalizeNativeCandidateInput(input) === expected
      );
      const composed = [['ㅏ', 'ㅜ', 'ᅟᅷ'], ['ㅑ', 'ㅜ', 'ᄋᆤ']].every(([first, second, expected]) => {
        const composer = new TangliengimHangulIme.Composer();
        composer.processNativeCompat(first);
        composer.processNativeCompat(second);
        return composer.text() === expected;
      });
      const initials = [...'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅇㅈㅉㅊㅋㅌㅍㅎㆆ'];
      const equivalent = initials.every(initial =>
        TangliengimHangulIme.normalizeNativeCandidateInput(initial + 'ㅏㅜ') ===
          TangliengimHangulIme.normalizeNativeCandidateInput(initial + 'ㅏㅈ') &&
        TangliengimHangulIme.normalizeNativeCandidateInput(initial + 'ㅑㅜ') ===
          TangliengimHangulIme.normalizeNativeCandidateInput(initial + 'ㅑㅈ')
      );
      return preserved && continued && candidateNormalized && composed && equivalent;
    })()`, context),
    'Unresolved vowel sequences and final-ㅈ shorthand must normalize to the same special-medial reading for every initial'
  );
  assert.ok(
    vm.runInContext(`(() => {
      const candidateRows = input => {
        imeController.clear();
        imeController.composer.setText(input, input.length);
        imeText.value = input;
        imeText.selectionStart = input.length;
        imeText.selectionEnd = input.length;
        return imeController.findCandidates().map(({ entry }) => entry.hanri + '|' + entry.reading);
      };
      const sameRows = inputs => {
        const rows = inputs.map(input => JSON.stringify(candidateRows(input)));
        return rows.length > 1 && rows[0] !== '[]' && rows.every(row => row === rows[0]);
      };
      const equivalent = sameRows(['아ㅜ', '앚', 'ᄋᅷ'])
        && sameRows(['야ㅜ', '얒', 'ᄋᆤ'])
        && sameRows(['가ㅜ', '갖', 'ᄀᅷ']);
      const tones = sameRows(['아ㅜ3', '앚3', 'ᄋᅷ3'])
        && sameRows(['야ㅜ3', '얒3', 'ᄋᆤ3']);
      imeController.clear();
      return equivalent && tones;
    })()`, context),
    'Candidate lookup must return the same dictionary candidates and tone choices for equivalent unresolved forms'
  );
  assert.ok(
    vm.runInContext(`(() => {
      imeController.recomposeNativeKoreanInput = true;
      const cases = [
        ['ㅏㅜ3', '\\u115fᅷ'],
        ['아ㅜ3', 'ᄋᅷ'],
        ['ㅑㅜ3', 'ᄋᆤ'],
        ['야ㅜ3', 'ᄋᆤ'],
      ];
      const commitNative = ([nativeText, expected]) => {
        imeController.clear();
        imeController.handleCompositionStart();
        imeText.value = nativeText;
        imeText.selectionStart = nativeText.length;
        imeText.selectionEnd = nativeText.length;
        imeController.handleCompositionEnd({ data: nativeText });
        return {
          text: imeText.value,
          expected,
          readings: imeController.getRememberedHangulReadings(),
          tones: imeController.getHangulToneReadingsForDisplay(),
        };
      };
      const results = cases.map(commitNative);
      imeController.recomposeNativeKoreanInput = false;
      const keepsToneState = result => {
        const unit = TangliengimImeCore.readingUnitAt(result.text, 0);
        const reading = result.expected + '3';
        return result.text === result.expected
          && unit?.canCarryTone
          && result.readings.some(span => span.reading === reading && span.explicit)
          && result.tones.some(tone => tone.start === 0 && tone.reading === reading);
      };
      return results.every(keepsToneState);
    })()`, context),
    'Mobile native composition must keep Tone 3 out of text and preserve each input path onset'
  );
  assert.ok(
    vm.runInContext(`(() => {
      imeController.clear();
      imeController.composer.setText('’에', 2);
      imeController.updateControlFromComposer();
      const chosen = imeController.activeCandidates.find(({ entry }) => entry.hanri === '’에');
      if (!chosen) return false;
      imeController.applyCandidate(chosen);
      return imeText.value === '’에' && chosen.start === 0;
    })()`, context),
    'A punctuation-prefixed candidate must own an identical punctuation mark immediately before its reading'
  );
  assert.ok(
    vm.runInContext(`(() => {
      const citation = lomariRenderer.resolvedHangulToneSpans('시');
      const sandhi = lomariRenderer.resolvedHangulToneSpans('시뎋');
      return citation[0]?.reading === '시5' && sandhi[0]?.reading === '시3';
    })()`, context),
    'Floating Hangul tones must follow the same resolved citation/sandhi state as Lomari'
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
    vm.runInContext(`(() => {
      imeController.clear();
      const defaultReading = findHanriEntry('情', 0)?.reading;
      const selectedReading = defaultReading === '쟐4' ? '졩4' : '쟐4';
      imeController.composer.setText(selectedReading, 2);
      imeController.updateControlFromComposer();
      const chosen = imeController.activeCandidates.find(
        ({ entry }) => entry.hanri === '情' && entry.reading === selectedReading && !entry.autoSandhi
      );
      if (!chosen) return false;
      imeController.applyCandidate(chosen);
      const selectedAtStart = findHanriEntry('情', 0)?.reading === selectedReading;
      const selectedLomari = lomariRenderer.render('情') === chosen.entry.lomari;
      const selectedAudio = audioPlanFromText('情').segments[0]?.unit === chosen.entry.audio.segments[0]?.unit;

      imeController.composer.setText('人情', 2);
      imeController.updateControlFromComposer();
      const followsEdit = findHanriEntry('人情', 1)?.reading === selectedReading;
      const followsEditOutput = lomariRenderer.render('人情').endsWith('-' + chosen.entry.lomari);

      imeController.composer.setText('情', 1);
      imeController.updateControlFromComposer();
      const followsUndo = findHanriEntry('情', 0)?.reading === selectedReading;

      imeController.clear();
      imeController.composer.setText('情', 1);
      imeController.updateControlFromComposer();
      const forgottenAfterDelete = findHanriEntry('情', 0)?.reading === defaultReading;
      return selectedAtStart && selectedLomari && selectedAudio && followsEdit && followsEditOutput && followsUndo && forgottenAfterDelete;
    })()`, context),
    'A selected Hanri reading must drive Lomari and audio until that Hanri is deleted'
  );
  const rememberedSandhi = JSON.parse(vm.runInContext(`(() => {
      imeController.clear();
      imeController.composer.setText('쟐3', 2);
      imeController.updateControlFromComposer();
      const chosen = imeController.activeCandidates.find(
        ({ entry }) => entry.hanri === '情' && entry.reading === '쟐3' && entry.autoSandhi
      );
      if (!chosen) return JSON.stringify({ chosen: false });
      imeController.applyCandidate(chosen);
      imeController.composer.setText('情人', 2);
      imeController.updateControlFromComposer();
      const lomari = lomariRenderer.render('情人');
      const audio = audioPlanFromText('情人');
      return JSON.stringify({
        chosen: true,
        remembered: findHanriEntry('情人', 0)?.reading || '',
        lomari,
        audioUnit: audio.segments[0]?.unit || '',
        audioTone: audio.segments[0]?.tone || '',
      });
    })()`, context));
  assert.deepEqual(
    rememberedSandhi,
    { chosen: true, remembered: '쟐3', lomari: 'jia̰-láng', audioUnit: '쟐', audioTone: '3' },
    'A remembered auto-sandhi reading must not be sandhied a second time'
  );
  assert.ok(
    vm.runInContext(`state.unitRoman.size > 0 && state.rawHangulAudio.size > 0 && state.jamoLomari.size > 0 && state.jamoAudio.size > 0`, context),
    'Web IME must load Local-IME-derived runtime pronunciation metadata'
  );
  assert.ok(
    vm.runInContext(`[
      ['ᄆᅷ', '/public/audio/ㅁ/mau3.wav'],
      ['ᄆᆤ', '/public/audio/ㅁ/miau3.wav'],
      ['ᄆힻ', '/public/audio/ㅁ/mer3.wav'],
    ].every(([text, file]) => {
      const audio = audioPlanFromText(text);
      return audio.missing.length === 0
        && audio.segments.length === 1
        && audio.segments[0].file === file;
    })`, context),
    'Initial plus special medial must resolve as one recorded syllable'
  );
  assert.ok(
    vm.runInContext(`(() => {
      const initial = audioPlanFromText('ᄆ');
      const vowel = audioPlanFromText('ᅷ');
      return initial.segments.length === 2
        && vowel.segments.length === 1
        && vowel.segments[0].file === '/public/audio/ㅇ/au1.wav';
    })()`, context),
    'Standalone jamo must retain their letter-name audio'
  );
  assert.ok(
    vm.runInContext(`[
      ['긍', 'kng'], ['능', 'nng'], ['등', 'tng'], ['믕', 'mng'],
      ['븡', 'png'], ['승', 'sng'], ['응', 'ng'], ['증', 'jng'], ['층', 'chng'],
      ['킁', 'khng'], ['틍', 'thng'], ['흥', 'hng'],
    ].every(([unit, stem]) => ['1', '2', '3', '4', '5'].every(tone => {
      const audio = state.rawHangulAudio.get(unit + tone);
      return audio?.missing?.length === 0
        && audio?.segments?.some(segment => segment.file.endsWith('/' + stem + tone + '.wav'));
    }))`, context),
    'Null-vowel -ng syllables must resolve their legacy ASCII audio filenames'
  );
  assert.ok(
    vm.runInContext(`(() => {
      const audio = state.rawHangulAudio.get('엏3');
      return audio?.missing?.length === 0
        && audio?.segments?.some(segment => segment.file.endsWith('/orh3.wav'));
    })()`, context),
    'Recorded standalone 엏3 must resolve to orh3.wav'
  );
  assert.ok(
    vm.runInContext(`(() => {
      const raw = state.rawHangulAudio.get('뽀3');
      const mixed = audioPlanFromText('뽀牙');
      return raw?.segments?.length === 1
        && raw.segments[0].tone === '3'
        && raw.segments[0].file === '/public/audio/ㅃ/bo3.wav'
        && mixed.missing.length === 0
        && mixed.segments.length === 2
        && mixed.segments[0].unit === '뽀'
        && mixed.segments[0].tone === '3'
        && mixed.segments[0].file === '/public/audio/ㅃ/bo3.wav'
        && mixed.segments[1].unit === '께'
        && mixed.segments[1].tone === '4';
    })()`, context),
    'Mixed Hangul-Hanri input must resolve the preceding syllable through its raw sandhi-tone audio key'
  );
  assert.ok(
    vm.runInContext(`[
      ['공', '겅'], ['꽁', '껑'], ['동', '덩'], ['똥', '떵'], ['롱', '렁'],
      ['몽', '멍'], ['봉', '벙'], ['뽕', '뻥'], ['송', '성'], ['옹', '엉'],
      ['종', '정'], ['쫑', '쩡'], ['총', '청'], ['콩', '컹'], ['통', '텅'],
      ['퐁', '펑'], ['홍', '헝'],
    ].every(([variant, canonical]) => ['1', '2', '3', '4', '5'].every(tone => {
      const variantAudio = state.rawHangulAudio.get(variant + tone);
      const canonicalAudio = state.rawHangulAudio.get(canonical + tone);
      if (!variantAudio && !canonicalAudio) return true;
      return Boolean(variantAudio && canonicalAudio)
        && JSON.stringify(variantAudio.files || []) === JSON.stringify(canonicalAudio.files || [])
        && JSON.stringify(variantAudio.missing || []) === JSON.stringify(canonicalAudio.missing || []);
    }))`, context),
    'Every ㅗ+ㅇ syllable must share the canonical ㅓ+ㅇ / ong audio asset'
  );
  assert.ok(
    vm.runInContext(`(() => {
      imeController.clear();
      const variant = audioPlanFromText('옹');
      const canonical = audioPlanFromText('엉');
      return variant.segments.length === 1
        && canonical.segments.length === 1
        && variant.segments[0].file === '/public/audio/ㅇ/ong3.wav'
        && canonical.segments[0].file === '/public/audio/ㅇ/ong3.wav'
        && variant.missing.length === 0
        && canonical.missing.length === 0;
    })()`, context),
    'Raw Web IME audio lookup must canonicalize 옹 to 엉 before resolution'
  );
  const explicitAnnotationResults = JSON.parse(vm.runInContext(`(() => {
    imeController.clear();
    return JSON.stringify(['[德뎩]', '[甲각]'].map(text => {
      const audio = audioPlanFromText(text);
      return {
        lomari: lomariRenderer.render(text),
        units: audio.segments.map(segment => segment.unit),
        tones: audio.segments.map(segment => segment.tone),
        missing: audio.missing,
      };
    }));
  })()`, context));
  assert.deepEqual(
    explicitAnnotationResults,
    [
      { lomari: 'tiek', units: ['뎩'], tones: ['3'], missing: [] },
      { lomari: 'kak', units: ['각'], tones: ['3'], missing: [] },
    ],
    'Explicit [Hanri+Hangul] annotations must use their supplied reading without a TSV mapping'
  );
  const rememberedAnnotationTones = JSON.parse(vm.runInContext(`(() => {
    const cases = [
      ['[德뎩]', '뎩', '1', 'tiêk'],
      ['[德뎩]', '뎩', '2', 'tièk'],
      ['[德뎩]', '뎩', '4', 'tiék'],
      ['[德뎩]', '뎩', '5', 'tiēk'],
      ['[德國뎩걱]', '뎩', '1', 'tiêk-kork'],
      ['[德國뎩걱]', '걱', '1', 'tiek-kôrk'],
    ];
    return JSON.stringify(cases.map(([text, unit, tone, expected]) => {
      imeController.clear();
      imeController.composer.setText(text, text.length);
      imeController.updateControlFromComposer();
      const start = text.lastIndexOf(unit);
      imeController.rememberHangulReading(start, start + unit.length, unit + tone, null, text, true);
      const audio = audioPlanFromText(text);
      return {
        expected, tone, unit, lomari: lomariRenderer.render(text),
        audioTone: audio.segments.find(segment => segment.unit === unit)?.tone,
        missing: audio.missing,
        visible: imeText.value,
      };
    }));
    })()`, context));
  for (const result of rememberedAnnotationTones) {
    assert.equal(result.lomari, result.expected, 'Bracketed Hangul must use its selected hidden tone in Lomari');
    assert.ok(
      result.audioTone === result.tone || result.missing.includes(result.unit + result.tone),
      'Bracketed Hangul audio must use its selected hidden tone even if its WAV is absent'
    );
    assert.ok(!/[12345]/u.test(result.visible), 'Hidden tone must stay out of the input text');
  }
  const selectedToneResults = JSON.parse(vm.runInContext(`(() => {
    const results = [];
    const press = key => {
      imeController.handleKeydown({ key, shiftKey: false, ctrlKey: false, metaKey: false,
        altKey: false, isComposing: false, preventDefault() {} });
      imeController.handleCursorChange({ type: 'keyup', key });
    };
    for (const sandhiMode of ['taipei', 'singapore']) {
      state.sandhiMode = sandhiMode;
      for (const [unit, forms] of [
        ['뎩', ['tiêk', 'tièk', 'tiek', 'tiék', 'tiēk']],
        ['아', ['â', 'à', 'a', 'á', 'ā']],
      ]) {
        for (const [index, expected] of forms.entries()) {
          const tone = String(index + 1);
          imeController.clear();
          imeController.composer.setText(unit + '호', unit.length);
          imeController.updateControlFromComposer();
          press(tone);
          const before = lomariPreview.textContent;
          const candidateIndex = imeController.activeCandidates.findIndex(({ entry }) =>
            ['hangul_plain', 'hangul_override'].includes(entry.kind)
            && TangliengimHangulIme.normalizeReadingToneKey(entry.reading) === unit + tone
          );
          if (candidateIndex < 0) throw new Error('No Hangul tone candidate for ' + unit + tone);
          while (imeController.activeCandidateIndex !== candidateIndex) press('Tab');
          press('Enter');
          const audio = audioPlanFromText(imeText.value);
          results.push({ unit, tone, sandhiMode, expected: expected + '-ho', before,
            after: lomariPreview.textContent, visible: imeText.value,
            menuClosed: candidateBar.hidden,
            audioTone: audio.segments.find(segment => segment.unit === unit)?.tone,
            expectedAudioTone: state.rawHangulAudio.get(unit + tone)?.segments[0]?.tone || tone,
            missing: audio.missing });
        }
      }
    }
    state.sandhiMode = 'taipei';
    return JSON.stringify(results);
  })()`, context));
  for (const result of selectedToneResults) {
    const label = `${result.unit}${result.tone} in ${result.sandhiMode}`;
    assert.equal(result.before, result.expected, `Typed tones must not be sandhied again: ${label}`);
    assert.equal(result.after, result.expected, `Candidate selection must retain the displayed tone: ${label}`);
    assert.equal(result.visible, result.unit + '호', 'Selected tones must remain hidden in the editor');
    assert.ok(result.menuClosed, 'Selecting a tone candidate must dismiss the menu');
    assert.ok(result.audioTone === result.expectedAudioTone || result.missing.includes(result.unit + result.tone),
      `Selected audio must not receive a second sandhi conversion: ${label}`);
  }
  const selectedAnnotationResults = JSON.parse(vm.runInContext(`(() => {
    return JSON.stringify([
      ['[遊玩칟토]', 'chit-thô'],
      ['[你好릐호]', 'li-hô'],
    ].map(([text, expected]) => {
      imeController.clear();
      imeController.composer.setText(text, text.length - 1);
      imeController.updateControlFromComposer();
      imeController.insertText('1');
      const before = lomariPreview.textContent;
      const candidate = imeController.activeCandidates.find(({ entry }) => entry.kind === 'hangul_plain');
      if (!candidate) throw new Error('No plain Hangul candidate for ' + text);
      imeController.applyCandidate(candidate);
      return { expected, before, after: lomariPreview.textContent };
    }));
  })()`, context));
  for (const result of selectedAnnotationResults) {
    assert.equal(result.before, result.expected);
    assert.equal(result.after, result.expected, 'A multi-syllable selection must retain every bracketed tone');
  }
  assert.equal(vm.runInContext(`(() => {
    imeController.clear();
    imeController.insertText('gh1');
    const selected = imeController.activeCandidates.find(({ entry }) =>
      ['hangul_plain', 'hangul_override'].includes(entry.kind) && entry.reading === '호1');
    if (!selected) throw new Error('Missing literal tone candidate');
    imeController.applyCandidate(selected);
    imeController.composer.setText('릐호', 2);
    imeController.updateControlFromComposer();
    return lomariPreview.textContent.endsWith('-hô');
  })()`, context), true, 'A longer dictionary match must not swallow a selected Hangul tone after a prefix edit');
  assert.ok(
    vm.runInContext(`(() => {
      imeController.clear();
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
      imeController.clear();
      imeController.composer.setText('랑', 1);
      imeController.updateControlFromComposer();
      if (!imeController.activeCandidates.length) return false;
      const cursorBefore = imeText.selectionStart;
      let prevented = false;
      const event = {
        key: 'ArrowRight', shiftKey: false, ctrlKey: false, metaKey: false, altKey: false,
        isComposing: false, preventDefault() { prevented = true; },
      };
      imeController.handleKeydown(event);
      imeController.handleCursorChange({ type: 'keyup', key: 'ArrowRight' });
      return prevented && imeController.activeCandidates.length === 0 && candidateBar.hidden &&
        imeText.selectionStart === cursorBefore;
    })()`, context),
    'Right Arrow at the end must dismiss the popup without creating a phantom caret stop'
  );
  assert.ok(
    vm.runInContext(`(() => {
      imeController.clear();
      imeController.composer.setText('가나다', 2);
      imeController.updateControlFromComposer();
      if (!imeController.activeCandidates.length) return false;
      const event = {
        key: 'ArrowRight', shiftKey: false, ctrlKey: false, metaKey: false, altKey: false,
        isComposing: false, preventDefault() {},
      };
      imeController.handleKeydown(event);
      return imeController.activeCandidates.length === 0
        && candidateBar.hidden
        && imeText.selectionStart === 3;
    })()`, context),
    'Right Arrow must dismiss an open popup and cross the next syllable in the same keypress'
  );
  assert.ok(
    vm.runInContext(`(() => {
      imeController.clear();
      imeController.composer.setText('랑', 1);
      imeController.updateControlFromComposer();
      if (!imeController.activeCandidates.length) return false;
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
      imeController.composer.setText('칟토', 2);
      imeController.updateControlFromComposer();
      const first = imeController.activeCandidates[0];
      const last = imeController.activeCandidates.at(-1);
      if (first?.entry?.kind !== 'hangul_override' || first.entry.reading !== '칟1토4' ||
        last?.entry?.kind !== 'hangul_plain' || last.entry.reading !== '칟토' ||
        !last.entry.generatedCandidate ||
        imeController.activeCandidates.slice(0, -1).some(({ entry }) => entry.generatedCandidate)) return false;
      let prevented = false;
      imeController.handleKeydown({
        key: 'Enter', shiftKey: false, ctrlKey: false, metaKey: false, altKey: false,
        isComposing: false, preventDefault() { prevented = true; },
      });
      return prevented && imeText.value === '칟토' && imeController.activeCandidates.length === 0 &&
        candidateBar.hidden && imeController.getRememberedHangulReadings()[0]?.reading === '칟1토4';
    })()`, context),
    'TSV candidates must precede the unrecorded toneless fallback and Enter must close the popup'
  );
  assert.ok(
    vm.runInContext(`(() => {
      imeController.clear();
      imeController.composer.setText('칟', 1);
      imeController.updateControlFromComposer();
      imeController.handleKeydown({
        key: '1', shiftKey: false, ctrlKey: false, metaKey: false, altKey: false,
        isComposing: false, preventDefault() {},
      });
      imeController.insertText('토');
      imeController.handleKeydown({
        key: '4', shiftKey: false, ctrlKey: false, metaKey: false, altKey: false,
        isComposing: false, preventDefault() {},
      });
      const cleanWhileChoosing = imeText.value === '칟토';
      const filtered = imeController.activeCandidates.some(
        ({ entry }) => entry.kind === 'hangul_override' && entry.reading === '칟1토4'
      ) && !imeController.activeCandidates.some(
        ({ entry }) => entry.kind === 'hangul_override' && entry.reading === '칟1토3'
      );
      imeController.backspace();
      const hiddenToneUndo = imeText.value === '칟토' &&
        imeController.getRememberedHangulReadings().every(span => span.reading !== '토4');
      imeController.handleKeydown({
        key: '4', shiftKey: false, ctrlKey: false, metaKey: false, altKey: false,
        isComposing: false, preventDefault() {},
      });
      imeController.applyCandidate(imeController.activeCandidates[0]);
      const remembered = imeController.findRememberedHangulEntryAt('칟토', 0)?.entry?.reading === '칟1토4';
      const lomari = lomariRenderer.render('칟토') === 'chît-thó';
      const tones = audioPlanFromText('칟토').segments.map(segment => segment.tone).join(',') === '1,4';
      imeController.handleCursorChange({ type: 'click' });
      const staysClosedOnClick = candidateBar.hidden && imeController.activeCandidates.length === 0;
      return cleanWhileChoosing && filtered && hiddenToneUndo && remembered && lomari && tones && staysClosedOnClick;
    })()`, context),
    'Typed tones must stay hidden while filtering and driving the selected occurrence output'
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
    ['릐 시뎋哭', 'lì si-têh-khau'],
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
  for (const [input, expected] of [
    ['릐 호', '2:0:1,3:1:0'],
    ['릐’호', '2:0:1,3:1:0'],
    ['릐, 호', '2:0:0,3:0:0'],
  ]) {
    const plan = vm.runInContext(`audioPlanFromText(${JSON.stringify(input)})`, context);
    const timing = plan.segments.map(segment => [
      segment.tone,
      Number(Boolean(segment.trimStart)),
      Number(Boolean(segment.trimEnd)),
    ].join(':')).join(',');
    assert.equal(timing, expected, `${input}: legacy phrase trimming and overlap`);
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
      imeController.onUpdate = () => {};
      imeController.handleInput({ inputType: 'insertText' });
      return JSON.stringify(imeController.activeCandidates
        .filter(({ entry }) => entry.kind !== 'hangul_plain')
        .map(({ entry }) => ({
        hanri: entry.hanri,
        reading: entry.reading,
      })));
    })()`, context));
    assert.deepEqual(actual, fixture.expected, `Legacy candidate parity: ${fixture.reading}`);
  }
  for (const mode of ['taipei', 'singapore']) {
    for (const phrase of ['시뎋哭', '릐 시뎋哭', '死死人', '릐호人']) {
      const plan = vm.runInContext(
        `imeController.clear(); setSandhiMode(${JSON.stringify(mode)}); audioPlanFromText(${JSON.stringify(phrase)})`,
        context
      );
      assert.equal(plan.missing.length, 0, `${phrase}: all audio must resolve`);
      assert.ok(plan.segments.length >= 3, `${phrase}: exercise repeated tone replacement`);
      for (const [index, segment] of plan.segments.entries()) {
        assert.equal(segment.trimStart, index > 0, `${phrase} (${mode}): preserve leading trim after sandhi`);
        assert.equal(segment.trimEnd, index < plan.segments.length - 1, `${phrase} (${mode}): preserve trailing trim after sandhi`);
      }
    }
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
