// The Android keyboard page, run headless: Space and Enter convert to the first candidate
// (docs/ime-phrase-conversion-plan.md, 5.3). Keys are pressed as pointer events, and a stand-in
// for the Android host records what reaches the focused app.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const { loadDictionaryData } = require('../tools/dictionary_data.cjs');
const data = loadDictionaryData(path.join(root, 'public/data/hokkien-hanri-dict.json'));
const fixture = JSON.parse(read('tests/fixtures/phrase-conversion-cases.json'));

// Enough of an element for the keyboard page and the IME's candidate strip.
function element() {
  const classes = new Set();
  const node = {
    value: '', textContent: '', selectionStart: 0, selectionEnd: 0, children: [], dataset: {},
    listeners: {}, parent: null,
    set className(value) { classes.clear(); for (const name of String(value).split(' ')) if (name) classes.add(name); },
    get className() { return [...classes].join(' '); },
    classList: {
      add: (...names) => names.forEach(name => classes.add(name)),
      remove: (...names) => names.forEach(name => classes.delete(name)),
      contains: name => classes.has(name),
      toggle(name, on = !classes.has(name)) { if (on) classes.add(name); else classes.delete(name); },
    },
    setAttribute() {}, focus() {}, setPointerCapture() {}, contains: () => false,
    addEventListener(name, listener) { (node.listeners[name] ||= []).push(listener); },
    setSelectionRange(start, end) { node.selectionStart = start; node.selectionEnd = end; },
    replaceChildren(...items) { node.children = []; node.append(...items); },
    append(...items) {
      for (const item of items) { if (typeof item === 'object') item.parent = node; node.children.push(item); }
    },
    after(item) {
      item.parent = node.parent;
      node.parent.children.splice(node.parent.children.indexOf(node) + 1, 0, item);
    },
    cloneNode() {
      const copy = element();
      copy.className = node.className;
      copy.textContent = node.textContent;
      copy.append(...node.children.map(child => (child.cloneNode ? child.cloneNode(true) : child)));
      return copy;
    },
    querySelectorAll(selector) {
      const name = selector.slice(1);
      return node.children.flatMap(child => (child.classList
        ? [...(child.classList.contains(name) ? [child] : []), ...child.querySelectorAll(selector)] : []));
    },
    querySelector(selector) { return node.querySelectorAll(selector)[0] || null; },
  };
  return node;
}

async function loadKeyboard() {
  const sent = [];
  const elements = new Map(['#buffer', '#candidates', '#keys'].map(selector => [selector, element()]));
  const context = vm.createContext({
    console: { log() {} }, setTimeout, clearTimeout, queueMicrotask,
    document: {
      body: element(), addEventListener() {}, createElement: element, createDocumentFragment: element,
      createTextNode: text => ({ textContent: text }), querySelector: selector => elements.get(selector),
    },
    fetch: async () => ({ json: async () => data }),
  });
  context.window = context;
  context.TliHost = {
    setComposing() {}, deleteBackward: () => sent.push('<delete>'), enter: () => sent.push('<enter>'),
    commit: text => sent.push(text), showKeyboardPicker() {},
  };
  for (const file of ['shared/web-hangul-ime.js', 'shared/web-ime-core.js']) vm.runInContext(read(file), context);
  let controller;
  const create = context.TangliengimImeCore.createTextImeController;
  context.TangliengimImeCore = { ...context.TangliengimImeCore,
    createTextImeController: options => (controller = create(options)) };
  vm.runInContext(read('android/keyboard/keyboard.js'), context);
  await new Promise(resolve => setImmediate(resolve));

  const keys = elements.get('#keys');
  const tap = key => {
    const button = element();
    button.dataset.key = key;
    const event = { target: { closest: () => button }, preventDefault() {}, stopPropagation() {}, pointerId: 1 };
    for (const type of ['pointerdown', 'pointerup']) for (const listener of keys.listeners[type]) listener(event);
  };
  const strip = elements.get('#candidates');
  return { context, controller, sent, tap, strip, buffer: elements.get('#buffer') };
}

(async () => {
  const { context, controller, sent, tap, strip, buffer } = await loadKeyboard();
  const sentAfter = action => { sent.length = 0; action(); return [...sent]; };
  const typeText = text => controller.insertText(text);
  const learned = () => JSON.stringify(controller.preferences.snapshot().selections);

  // The plan's case, typed on the keyboard's own keys: 킈쟣븡 then Space sends 去食飯.
  assert.deepEqual(sentAfter(() => {
    for (const key of 'zmlwigqmd') tap(key);
    assert.equal(buffer.value, '킈쟣븡');
    tap('Space');
  }), ['去食飯 ']);
  assert.equal(buffer.value, '', 'The strip is empty after Space');

  // The desktop Pad's Space is held to the same list in tests/test_phrase_conversion.py.
  for (const [typed, written] of fixture.space) {
    assert.deepEqual(sentAfter(() => { typeText(typed); tap('Space'); }), [`${written} `], `Space: ${typed}`);
  }
  assert.equal(learned(), '{}', 'Space teaches nothing');

  // Enter converts too, then finishes the composition. With an empty strip it reaches the app.
  assert.deepEqual(sentAfter(() => { typeText('킈쟣븡'); tap('Enter'); }), ['去食飯']);
  assert.deepEqual(sentAfter(() => tap('Enter')), ['<enter>']);
  assert.deepEqual(sentAfter(() => tap('Space')), [' ']);
  assert.equal(learned(), '{}', 'Enter teaches nothing');

  // An empty strip commits the raw text.
  assert.deepEqual(sentAfter(() => {
    typeText('킈쟣븡');
    controller.dismissCandidates();
    tap('Space');
  }), ['킈쟣븡 ']);

  // Tapping the Hangul candidate keeps the Hangul.
  sent.length = 0;
  typeText('쟣븡');
  const hangulButton = strip.children[controller.activeCandidates.findIndex(c => c.entry.kind === 'hangul_plain')];
  const tapped = { target: { closest: () => hangulButton } };
  for (const listener of hangulButton.listeners.click) listener(tapped);
  for (const listener of strip.listeners.click) listener(tapped);
  await new Promise(resolve => setImmediate(resolve));
  tap('Space');
  assert.deepEqual(sent, ['쟣븡', ' ']);

  // A phrase with a Hanri the phone may not draw also offers that word in Hangul.
  sent.length = 0;
  const rare = data.entries.find(e => e.active && !e.autoSandhi && e.kind === 'plain_hanri' &&
    [...e.hanri].length > 1 && [...e.hanri].some(c => c.codePointAt(0) > 0xFFFF));
  assert.ok(rare, 'Missing a rare-Hanri word to test');
  typeText(`킈${rare.readingBase}`);
  assert.equal(controller.activeCandidates[0].entry.kind, 'phrase');
  const written = strip.children.find(child => child.classList.contains('candidate-written'));
  assert.equal(written, strip.children[1], 'The Hangul alternative follows the phrase');
  assert.ok(written.dataset.written.startsWith('去'));
  assert.ok(![...written.dataset.written].some(c => c.codePointAt(0) > 0xFFFF));
  const option = { target: { closest: () => written } };
  for (const listener of written.listeners.click) listener(option);
  for (const listener of strip.listeners.click) listener(option);
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(sent, [written.dataset.written]);

  // The setup screen's reset request clears what the keyboard has learned.
  controller.preferences.record('킈', 'U+53BB_00');
  assert.notEqual(learned(), '{}');
  assert.equal(context.TliKeyboard.resetLearned(), true);
  assert.equal(learned(), '{}');

  console.log(`OK: Android keyboard; Space and Enter convert, ${fixture.space.length} shared Space cases.`);
})().catch(error => { console.error(error); process.exitCode = 1; });
