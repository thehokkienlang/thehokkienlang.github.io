'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const read = relative => fs.readFileSync(path.join(root, relative), 'utf8');
const extension = 'desktop/youtube_companion/';
const session = 'a'.repeat(64), otherSession = 'b'.repeat(64), videoId = 'HNYkSBkQ33Y';

async function backgroundChecks() {
  const storage = {}, sent = [], tabs = new Map(), closed = [];
  let removed, failClose = false;
  const context = vm.createContext({URL, URLSearchParams, Date, chrome: {
    runtime: {id: 'test-extension', onMessage: {addListener() {}}},
    storage: {session: {
      async get(key) { return structuredClone(key === null ? storage : {[key]: storage[key]}); },
      async set(values) { Object.assign(storage, structuredClone(values)); },
      async remove(key) { delete storage[key]; },
    }},
    tabs: {async get(id) { return tabs.get(id); },
      async remove(id) { if (failClose) throw new Error('Close failed'); closed.push(id); tabs.delete(id); },
      async sendMessage(tabId, message) { sent.push({tabId, message}); return {ok: true, sample: {time: 64}}; },
      onRemoved: {addListener(fn) { removed = fn; }}},
  }});
  vm.runInContext(read(extension + 'background.js'), context);
  const handle = vm.runInContext('handle', context);
  const editor = {id: 'test-extension', frameId: 0, tab: {id: 1},
    url: 'http://127.0.0.1:61717/website-editor/lyric-timing.html?file=song'};
  const youtube = {...editor, tab: {id: 2}, url: `https://www.youtube.com/watch?v=${videoId}`};
  tabs.set(2, {url: youtube.url});
  assert.equal((await handle({action: 'hello'}, editor)).ok, true);
  await assert.rejects(handle({action: 'register', session, videoId}, {...editor, url: 'https://evil.example/website-editor/lyric-timing.html'}));
  await assert.rejects(handle({action: 'register', session, videoId}, {...editor, frameId: 1}));
  await assert.rejects(handle({action: 'register', session: 'short', videoId}, editor));
  await handle({action: 'register', session, videoId}, editor);
  await assert.rejects(handle({action: 'attach', session: otherSession}, youtube));
  await assert.rejects(handle({action: 'attach', session}, {...youtube, url: 'https://www.youtube.com/watch?v=xxxxxxxxxxx'}));
  await handle({action: 'attach', session}, youtube);
  await assert.rejects(handle({action: 'command', session, command: 'sample'}, {...editor, tab: {id: 99}}));
  await assert.rejects(handle({action: 'attach', session}, {...youtube, tab: {id: 3}}));
  await handle({action: 'time', session, sample: {videoId, time: 53.5}}, youtube);
  assert.equal(sent.at(-1).tabId, 1);
  assert.equal(sent.at(-1).message.kind, 'clock');
  await handle({action: 'command', session, command: 'seek', time: 53.5}, editor);
  assert.equal(sent.at(-1).tabId, 2);
  assert.equal(sent.at(-1).message.time, 53.5);
  await assert.rejects(handle({action: 'command', session, command: 'seek', time: -2}, editor));
  tabs.set(2, {url: 'https://www.youtube.com/watch?v=xxxxxxxxxxx'});
  await assert.rejects(handle({action: 'command', session, command: 'sample'}, editor));
  tabs.set(2, {url: youtube.url});
  await removed(2);
  assert.equal(storage['timing:' + session].youtubeTabId, null);
  assert.equal(sent.at(-1).message.kind, 'disconnected');
  await handle({action: 'attach', session}, {...youtube, tab: {id: 3}});
  // Reopen safely replaces even a window whose COOP policy severed its handle.
  await handle({action: 'register', session, videoId}, editor);
  assert.equal(storage['timing:' + session].youtubeTabId, null);
  assert.equal(sent.at(-1).message.kind, 'disconnect');
  await handle({action: 'register', session: otherSession, videoId}, editor);
  assert.equal(storage['timing:' + session], undefined);
  await removed(1);
  assert.equal(storage['timing:' + otherSession], undefined);
  await handle({action: 'register', session, videoId}, editor);
  tabs.set(2, {url: youtube.url});
  await handle({action: 'attach', session}, youtube);
  await handle({action: 'unregister', session}, editor);
  assert.deepEqual(closed, [2], 'Song switching closes the paired tab even after YouTube clears its fragment.');
  await handle({action: 'register', session, videoId}, editor);
  tabs.set(2, {url: 'https://www.youtube.com/watch?v=xxxxxxxxxxx'});
  await handle({action: 'attach', session}, youtube);
  await handle({action: 'unregister', session}, editor);
  assert.deepEqual(closed, [2], 'Do not close a tab navigated to unrelated content.');
  await handle({action: 'register', session, videoId}, editor);
  tabs.set(2, {url: youtube.url});
  await handle({action: 'attach', session}, youtube);
  failClose = true;
  await assert.rejects(handle({action: 'unregister', session}, editor), /Close failed/);
  assert.ok(storage['timing:' + session], 'Keep the pairing when closing fails so it can be retried.');
  failClose = false;
  assert.equal((await handle({action: 'unregister', session}, editor)).closed, true);
  assert.equal((await handle({action: 'unregister', session}, editor)).closed, true, 'Closing is idempotent.');
}

async function youtubeChecks() {
  let listener, ad = false;
  const sent = [];
  const video = {currentTime: 53.5, duration: 260, readyState: 4, paused: true, ended: false};
  video.play = async () => { video.paused = false; };
  video.pause = () => { video.paused = true; };
  const location = {href: `https://www.youtube.com/watch?v=${videoId}#tli-timing=${session}`,
    pathname: '/watch', hash: '#tli-timing=' + session};
  const window = {addEventListener() {}}; window.top = window;
  const context = vm.createContext({window, location, URL, URLSearchParams,
    setInterval() { return 1; }, clearInterval() {},
    document: {getElementById() { return {classList: {contains() { return ad; }}, querySelector() { return video; }}; }},
    chrome: {runtime: {id: 'test-extension', onMessage: {addListener(fn) { listener = fn; }},
      async sendMessage(message) { sent.push(message); return {ok: true}; }}},
  });
  vm.runInContext(read(extension + 'youtube.js'), context);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(sent[0].action, 'attach');
  assert.equal(sent[1].sample.time, 53.5);
  function command(name, time, token = session) {
    let result;
    listener({kind: 'command', session: token, command: name, time}, {id: 'test-extension'}, value => { result = value; });
    return result;
  }
  assert.equal(command('sample').sample.time, 53.5);
  assert.equal(command('seek', 64).sample.time, 64);
  assert.equal(video.paused, true, 'Seeking must not initiate playback.');
  command('toggle');
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(video.paused, false);
  command('toggle'); assert.equal(video.paused, true);
  assert.equal(command('seek', 999).ok, false);
  assert.equal(command('sample', null, otherSession), undefined);
  ad = true;
  assert.equal(command('sample').ok, false);
  assert.equal(command('seek', 20).ok, false);
  assert.equal(video.currentTime, 64, 'Do not seek an advertisement.');
  ad = false; location.href = 'https://www.youtube.com/watch?v=xxxxxxxxxxx';
  assert.equal(command('sample').ok, false);
}

async function companionChecks() {
  const listeners = new Set(), timeouts = new Map(), statuses = [], clocks = [], sent = [];
  let timer = 0, now = 1000, popupBlocked = false, failRegister = false;
  const popup = {closed: false, opener: {}, location: {}, focus() {}, close() { this.closed = true; }};
  const location = {origin: 'http://127.0.0.1:61717'};
  const dispatch = data => { for (const fn of [...listeners]) fn({source: window, origin: location.origin, data}); };
  const window = {
    addEventListener(type, fn) { if (type === 'message') listeners.add(fn); },
    removeEventListener(type, fn) { listeners.delete(fn); },
    open() { if (popupBlocked) return null; popup.closed = false; return popup; },
    postMessage(message) {
      sent.push(message);
      const ok = !(failRegister && message.action === 'register');
      dispatch({source: 'tli-youtube-extension', requestId: message.requestId, ok, closed: message.action === 'unregister',
        error: 'Missing extension', sample: {videoId, ready: true, time: 53.5, state: 2}});
    },
  };
  const context = vm.createContext({window, location, crypto: require('node:crypto').webcrypto,
    Uint8Array, Date: {now: () => now}, setTimeout(fn) { const id = ++timer; timeouts.set(id, fn); return id; },
    clearTimeout(id) { timeouts.delete(id); }, setInterval() { return ++timer; }, clearInterval() {},
  });
  vm.runInContext(read('desktop/website_editor_ui/lyric-companion.js'), context);
  const player = window.TliLyricCompanion.connect(videoId, (time, state) => clocks.push({time, state}),
    error => { throw error; }, text => statuses.push(text));
  await player.open();
  assert.equal(popup.opener, null);
  assert.match(popup.location.href, /^https:\/\/www.youtube.com\/watch\?v=HNYkSBkQ33Y#tli-timing=[a-f0-9]{64}$/);
  const token = sent[0].session;
  dispatch({source: 'tli-youtube-extension', kind: 'clock', session: otherSession,
    sample: {videoId, ready: true, time: 123, state: 1}});
  assert.equal(clocks.length, 0);
  dispatch({source: 'tli-youtube-extension', kind: 'clock', session: token,
    sample: {videoId, ready: true, time: 59.3, state: 1}});
  assert.equal(player.time(), 59.3);
  assert.equal(await player.sample(), 53.5, 'Marking reads a fresh time, not the last heartbeat.');
  dispatch({source: 'tli-youtube-extension', kind: 'clock', session: token,
    sample: {videoId, ready: false, ad: true, time: null}});
  assert.equal(player.time(), null);
  assert.match(statuses.at(-1), /Advertisement/);
  await player.seek(64);
  assert.equal(sent.at(-1).command, 'seek');
  now = 4000;
  assert.equal(player.time(), null, 'A stale clock must not be used.');
  await player.destroy();
  assert.equal(popup.closed, true, 'Destroy closes the popup handle too.');
  await assert.rejects(player.sample(), /song changed/);
  const blocked = window.TliLyricCompanion.connect(videoId, () => {}, () => {}, () => {});
  popupBlocked = true;
  await assert.rejects(blocked.open(), /popup/);
  popupBlocked = false; failRegister = true;
  await assert.rejects(blocked.open(), /Missing extension/);
  assert.equal(popup.closed, true);
  await blocked.destroy();
}

async function sharedCandidateChecks() {
  const node = () => ({value: '', children: [], hidden: true, selectionStart: 0, selectionEnd: 0,
    style: {}, classList: {toggle() {}, add() {}, remove() {}},
    append(...children) { this.children.push(...children); }, replaceChildren(...children) { this.children = children; },
    setAttribute() {}, removeAttribute() {}, addEventListener() {}, focus() {},
    setSelectionRange(start, end) { this.selectionStart = start; this.selectionEnd = end; }});
  const control = node(), menu = node();
  const document = {activeElement: control, addEventListener() {}, createElement: node,
    createTextNode: text => ({textContent: text}), createDocumentFragment: node};
  const context = vm.createContext({document, window: {addEventListener() {}},
    localStorage: {getItem() { return null; }, setItem() {}}, console, setTimeout, clearTimeout});
  vm.runInContext(read('shared/web-hangul-ime.js'), context);
  vm.runInContext(read('shared/web-ime-core.js'), context);
  const entries = JSON.parse(read('public/data/hokkien-hanri-dict.json')).entries;
  const core = context.window.TangliengimImeCore;
  const ime = core.createTextImeController({control, candidateContainer: menu, entries,
    dictionaryIndex: core.createDictionaryIndex(entries)});
  await ime.preferences.ready;
  const entry = entries.find(entry => entry.hanri === '世界' && entry.active !== false);
  assert.ok(entry);
  const reading = context.window.TangliengimHangulIme.normalizeReadingBase(entry.reading);
  ime.composer.setText(reading, reading.length);
  ime.updateControlFromComposer();
  assert.equal(menu.hidden, false, 'The real shared TLI controller displays its candidate menu.');
  assert.ok(ime.activeCandidates.some(candidate => candidate.entry.hanri === '世界'));
}

async function editorClickChecks() {
  const elements = new Map(), seeks = [];
  const classes = () => {
    const values = new Set();
    return {toggle(name, enabled) { if (enabled) values.add(name); else values.delete(name); },
      remove(name) { values.delete(name); }, contains(name) { return values.has(name); }};
  };
  const element = () => ({value: '', checked: false, disabled: false, children: [], dataset: {},
    listeners: {}, addEventListener(name, fn) { this.listeners[name] = fn; }, focus() {},
    classList: classes(), setAttribute() {}, append(...children) { this.children.push(...children); },
    replaceChildren(...children) { this.children = children; }});
  const get = id => { if (!elements.has(id)) elements.set(id, element()); return elements.get(id); };
  let ready = true, destroyed = false, navigated, tick, rejectClose = false, imeOptions, loadedEntries, savedTiming;
  const dictionaryEntries = [{entry_id: 'entry-test', hanri: '歌', reading: '과1', active: true}];
  const player = {time: () => ready ? 10 : null, seek: time => seeks.push(time), async destroy() {
    if (rejectClose) throw new Error('Reload the extension'); destroyed = true;
  }};
  const fixture = {ok: true, title: 'Test', videoId, lines: [0, 1, 2].map(i => ({id: 'line-' + i, label: 'Line ' + i, html: '<p>Line ' + i + '</p>'})),
    timing: {status: 'draft', cues: [{start: 0, end: 5}, {start: 20, end: 25}, {start: null, end: null}]}};
  const document = {getElementById: get, createElement: element, createTextNode: text => ({textContent: text}),
    querySelector: () => ({content: 'test-token'}),
    querySelectorAll: () => get('cueRows').children};
  const context = {document, location: {search: '?file=test', href: 'http://127.0.0.1:61717/website-editor/lyric-timing.html?file=test',
      assign(url) { assert.equal(destroyed, true); navigated = url; }}, URL, URLSearchParams,
    window: {addEventListener() {}, TangliengimImeCore: {
      createCandidatePopupPositioner() { return {schedule() {}}; },
      createDictionaryIndex(entries) { return {entries}; },
      createTextImeController(options) { imeOptions = options; return {setEnabled() {}, preferences: {ready: Promise.resolve()},
        setEntries(entries, index) { assert.equal(entries, index.entries); loadedEntries = entries; }}; }
    }}, structuredClone, confirm: () => true,
    DOMParser: class {parseFromString(html) { return {querySelector: () => ({...element(), outerHTML: html})}; }},
    fetch: async (url, options) => ({ok: true, json: async () => url.endsWith('save-lyric-timing') ?
      (savedTiming = JSON.parse(options.body).timing, {ok: true, timing: savedTiming, message: 'Saved'}) :
      url.endsWith('hokkien-hanri-dict.json') ? {entries: dictionaryEntries} : url.endsWith('/pages') ? {ok: true, pages: [
      {type: 'songs', file: 'test', title: 'Maybe Maybe', searchText: 'Maybe Maybe 메ˉ삐ˆ'},
      {type: 'songs', file: 'other-song', title: 'Other Song', searchText: 'Other Song'},
    ]} : fixture}),
    TliLyricPlayer: require('../shared/web-lyric-player.js'),
    TliLyricCompanion: {connect: (video, onTime) => { tick = onTime; return player; }},
  };
  vm.runInNewContext(read('desktop/website_editor_ui/lyric-timing.js'), context);
  await new Promise(resolve => setImmediate(resolve));
  const rows = get('cueRows').children;
  assert.equal(get('undoTiming').disabled, true, 'Undo starts empty for each song load.');
  assert.equal(imeOptions.candidateContainer, get('songSearchCandidates'), 'Use a real candidate container, not only a bare composer.');
  assert.equal(loadedEntries, dictionaryEntries, 'Load the shared website dictionary into the candidate controller.');
  assert.equal(get('songImeStatus').textContent, '');
  assert.equal(imeOptions.enabled(), true, 'Hangul keyboard is on by default.');
  get('songHangulToggle').onclick(); assert.equal(imeOptions.enabled(), false);
  get('songHangulToggle').onclick(); assert.equal(imeOptions.enabled(), true);
  get('songSearch').value = '메삐'; imeOptions.onUpdate();
  assert.equal(get('songChoice').children.length, 2, 'Hangul searches match tone-marked title readings.');
  get('songSearch').value = 'maybe'; get('songSearch').listeners.input();
  assert.equal(get('songChoice').children.length, 2, 'English titles are case insensitive.');
  get('songSearch').value = 'not-a-song'; imeOptions.onUpdate();
  assert.equal(get('songChoice').disabled, true);
  get('songSearch').value = ''; imeOptions.onUpdate();
  assert.equal(get('songChoice').children.length, 3, 'Clearing search restores all songs.');
  assert.equal(rows.length, 3);
  rows[1].children[0].onclick();
  assert.deepEqual(seeks, [], 'Single click selects without changing playback time.');
  assert.equal(rows[1].classList.contains('selected'), true);
  rows[1].children[0].ondblclick();
  assert.deepEqual(seeks, [20], 'Double click seeks to the saved start.');
  rows[0].children[0].onclick();
  assert.deepEqual(seeks, [20], 'Selecting a different sentence still must not seek.');
  get('seekStart').onclick();
  assert.deepEqual(seeks, [20, 0], 'The first sentence can seek to zero.');
  get('seekEnd').onclick();
  assert.deepEqual(seeks, [20, 0, 5], 'Go to end seeks to the selected sentence end.');
  rows[1].children[1].onfocus();
  assert.equal(seeks.length, 3, 'Focusing timestamp inputs must not seek.');
  rows[2].children[0].onclick();
  assert.equal(seeks.length, 3, 'Untimed sentences select without seeking.');
  get('seekEnd').onclick();
  assert.match(get('timingNotice').textContent, /no end time/);
  rows[2].children[0].ondblclick();
  assert.match(get('timingNotice').textContent, /no start time/);
  ready = false;
  rows[1].children[0].onclick();
  rows[1].children[0].ondblclick();
  assert.equal(seeks.length, 3, 'Do not seek while disconnected or during ads.');
  get('seekEnd').onclick();
  assert.equal(seeks.length, 3, 'Go to end does not seek during ads or disconnection.');
  const startInput = rows[1].children[1], previousEnd = rows[0].children[2];
  startInput.onfocus(); startInput.value = '4'; startInput.valueAsNumber = 4;
  startInput.oninput();
  assert.equal(previousEnd.value, '00:05.000', 'Do not trim while a start time is still being typed.');
  startInput.onchange();
  assert.equal(previousEnd.value, '00:03.900', 'Committing an overlapping start leaves a 0.1-second gap.');
  startInput.value = '6'; startInput.valueAsNumber = 6; startInput.oninput(); startInput.onchange();
  assert.equal(previousEnd.value, '00:05.900', 'A later start fills the gap to 0.1 seconds before it.');
  startInput.value = '0'; startInput.valueAsNumber = 0; startInput.oninput(); startInput.onchange();
  assert.equal(startInput.value, '00:06.000', 'Reject an edit that would give the previous sentence zero duration.');
  assert.equal(previousEnd.value, '00:05.900');
  startInput.value = '0.1'; startInput.valueAsNumber = 0.1; startInput.oninput(); startInput.onchange();
  assert.equal(startInput.value, '00:06.000', 'The 0.1-second gap must not collapse the previous duration.');
  previousEnd.value = ''; previousEnd.oninput(); previousEnd.onchange();
  assert.equal(previousEnd.value, '00:05.900', 'An empty end is filled from the next start.');
  rows[1].children[2].value = '7'; rows[1].children[2].oninput(); rows[1].children[2].onchange();
  assert.equal(rows[1].children[2].value, '00:07.000', 'An entered end stays unchanged.');
  ready = true;
  rows[0].children[2].value = '12'; rows[0].children[2].valueAsNumber = 12; rows[0].children[2].oninput();
  rows[1].children[0].onclick();
  const beforeMark = seeks.length;
  await get('markStart').onclick();
  assert.equal(seeks.length, beforeMark, 'Selecting and marking a sentence must not seek first.');
  assert.equal(rows[1].children[1].value, '00:09.800', 'Mark start uses the current playback time with a 0.2-second reaction-time lead.');
  assert.equal(previousEnd.value, '00:09.700', 'Mark start also leaves the same 0.1-second gap.');
  tick(0, 1);
  assert.equal(get('togglePlayback').textContent, '\u23f8');
  assert.equal(rows[0].classList.contains('playing'), true);
  assert.equal(rows[1].classList.contains('selected'), true, 'Playback must not redirect the editing selection.');
  assert.match(get('lyricPreview').srcdoc, /Line 0/);
  const preview = get('lyricPreview').srcdoc;
  tick(1, 1);
  assert.equal(get('lyricPreview').srcdoc, preview, 'The preview stays stable within a sentence.');
  tick(10, 1);
  assert.equal(rows[0].classList.contains('playing'), false);
  assert.equal(rows[1].classList.contains('playing'), true);
  assert.match(get('lyricPreview').srcdoc, /Line 1/);
  tick(0, 2);
  assert.equal(get('togglePlayback').textContent, '\u25b6');
  assert.match(get('lyricPreview').srcdoc, /Line 0/, 'Backward seeking updates the preview while paused too.');
  get('previewHighlight').onchange();
  assert.match(get('lyricPreview').srcdoc, /Line 0/, 'Preview settings must not jump back to the editing selection.');
  tick(30, 0);
  assert.equal(rows[1].classList.contains('playing'), false);
  tick(10, 1, 260);
  assert.equal(get('playbackSeek').max, '260');
  assert.equal(get('playbackSeek').disabled, false);
  get('playbackSeek').value = '125.5'; get('playbackSeek').oninput();
  assert.equal(get('clock').textContent, '02:05.500');
  tick(11, 1, 260);
  assert.equal(get('playbackSeek').value, '125.5', 'Playback ticks must not move the thumb while dragging.');
  get('playbackSeek').onchange();
  assert.equal(seeks.at(-1), 125.5);
  tick(125.5, 2, 260);
  assert.equal(get('playbackSeek').value, '125.5');
  rejectClose = true;
  const firstStart = rows[0].children[1];
  firstStart.onfocus(); firstStart.value = '30'; firstStart.valueAsNumber = 30;
  firstStart.oninput(); firstStart.onchange();
  assert.equal(rows[0].children[2].value, '00:30.100');
  assert.equal(rows[1].children[1].value, '00:30.200');
  assert.equal(rows[1].children[2].value, '00:30.300');
  assert.equal(rows[2].children[1].value, '', 'Do not invent timings for an untimed line.');
  function draft(index, key, value) {
    const input = rows[index].children[key === 'start' ? 1 : 2];
    input.onfocus();
    input.value = String(value); input.valueAsNumber = value; input.oninput();
  }
  draft(0, 'start', 0); draft(0, 'end', 15);
  draft(1, 'start', 10); draft(1, 'end', 9);
  await get('saveTiming').onclick();
  assert.equal(savedTiming.cues[0].end, 9.9);
  assert.equal(savedTiming.cues[1].start, 10);
  assert.equal(savedTiming.cues[1].end, 10.1);
  assert.equal(savedTiming.cues[2].start, null);
  draft(1, 'start', 210.379);
  rows[1].children[1].value = '03:30.379'; rows[1].children[1].oninput(); rows[1].children[1].onchange();
  assert.equal(rows[1].children[1].value, '03:30.379');
  await get('saveTiming').onclick();
  assert.equal(savedTiming.cues[1].start, 210.379);
  get('undoTiming').onclick();
  let restored = get('cueRows').children;
  assert.equal(restored[0].children[2].value, '00:09.900');
  assert.equal(restored[1].children[1].value, '00:10.000');
  assert.equal(restored[1].children[2].value, '00:10.100', 'Undo restores the automatic cascade as one edit.');
  assert.match(get('completion').textContent, /Unsaved/, 'Undoing a saved edit creates an unsaved draft.');
  const seekCount = seeks.length;
  restored[1].children[0].onclick(); get('clearCue').onclick();
  assert.equal(restored[1].children[1].value, '');
  get('undoTiming').onclick(); restored = get('cueRows').children;
  assert.equal(restored[1].children[1].value, '00:10.000');
  assert.equal(restored[1].children[2].value, '00:10.100');
  assert.equal(seeks.length, seekCount, 'Undo never moves video playback.');
  const choice = {value: 'other-song'};
  await get('songChoice').onchange({target: choice});
  assert.equal(navigated, undefined, 'Do not switch songs silently if closing fails.');
  assert.equal(choice.value, 'test');
  assert.equal(choice.disabled, false);
  assert.match(get('timingNotice').textContent, /Could not close/);
  rejectClose = false;
  await get('songChoice').onchange({target: {value: 'other-song'}});
  assert.equal(navigated.searchParams.get('file'), 'other-song');
  assert.equal(read('desktop/website_editor_ui/lyric-timing.html').includes('id="playbackMode"'), false);
}

(async () => {
  const manifest = JSON.parse(read(extension + 'manifest.json'));
  assert.deepEqual(manifest.permissions, ['storage']);
  assert.deepEqual(manifest.host_permissions, ['https://www.youtube.com/*']);
  assert.equal(manifest.content_scripts.some(script => script.matches.includes('<all_urls>')), false);
  await backgroundChecks(); await youtubeChecks(); await companionChecks(); await sharedCandidateChecks(); await editorClickChecks();
  console.log('PASS: local pairing, tab isolation, seek/sample, ads, stale clocks, popup failure and cleanup.');
})().catch(error => { console.error(error); process.exitCode = 1; });
