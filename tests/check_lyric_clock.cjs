const assert = require('node:assert/strict');
const { cueAt } = require('../shared/web-lyric-player.js');
const cues = [{ id:'intro-gap', start:null, end:null }, { id:'first', start:10, end:15 },
  { id:'repeat', start:20, end:25 }];
assert.equal(cueAt(cues, 0), null);
assert.equal(cueAt(cues, 9.999), null);
assert.equal(cueAt(cues, 10).id, 'first');
assert.equal(cueAt(cues, 14.99).id, 'first');
assert.equal(cueAt(cues, 15).id, 'first');
assert.equal(cueAt(cues, 19.999).id, 'first');
assert.equal(cueAt(cues, 20).id, 'repeat');
assert.equal(cueAt(cues, 10).id, 'first'); // Backward seek uses the video clock.
assert.equal(cueAt(cues, NaN), null);
assert.equal(cueAt(cues, 25).id, 'repeat');
console.log('PASS: lyric boundaries, gaps, repeats and backward seeks.');

// Exercise the public UI without inventing timings for the real recording.
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync(require.resolve('../shared/web-lyric-sync.js'), 'utf8');
function fixture(status = 'reviewed', mobile = true, wrapped = true, hasHeading = true) {
  const makeLine = () => {
    const line = { active:false, current:false, scrolled:0, attributes:{}, listeners:{},
    classList:{ add() { this.owner.active = true; }, remove() { this.owner.active = false; } },
    setAttribute(name, value) { this.attributes[name] = value; if (name === 'aria-current') this.current = true; },
    removeAttribute(name) { delete this.attributes[name]; if (name === 'aria-current') this.current = false; },
    addEventListener(name, handler) { this.listeners[name] = handler; },
    append() {},
    querySelector() { return this.main; },
    scrollIntoView() { this.scrolled++; }, contains(node) { return node === this; } };
    line.seekTargets = [];
    const text = {textContent:'字', parentElement:{closest:() => null}, replaceWith:target => { line.seekTargets.push(target); line.seekTarget ||= target; }};
    const lomari = {textContent:'ji', parentElement:{closest:() => null}, replaceWith:target => { line.seekTargets.push(target); }};
    line.main = {childNodes:[text]};
    line.childNodes = [text, lomari];
    return line;
  };
  const lines = {first:makeLine(), repeat:makeLine()};
  Object.values(lines).forEach(line => line.classList.owner = line);
  let callback, errorCallback, connected = false, connections = 0, replacements = 0;
  let placement = '';
  const heading = {insertAdjacentElement(position) { placement = 'heading:' + position; }};
  const figure = {insertAdjacentElement(position) { placement = 'figure:' + position; }};
  const frame = {src:'https://www.youtube.com/embed/HNYkSBkQ33Y',
    closest() { return wrapped ? figure : null; },
    insertAdjacentElement(position) { placement = 'iframe:' + position; },
    cloneNode() { return {...this}; }, replaceWith() { replacements++; }};
  const label = {textContent:''}, follow = {checked:false};
  const controls = {hidden:true, querySelector: selector => selector === 'input' ? follow : label};
  const document = {getElementById: () => ({textContent:JSON.stringify({status,videoId:'HNYkSBkQ33Y',cues})}),
    createElement: () => makeLine(),
    createTreeWalker: main => { let index = -1; return {get currentNode() { return main.childNodes[index]; }, nextNode() { return ++index < main.childNodes.length; }}; },
    querySelectorAll: () => [frame],
    querySelector: selector => selector === '.lyric-sync-controls' ? controls : selector === '.song-tone-guide' ? null : selector === '.song-script-heading' ? (hasHeading ? heading : null) : lines[selector.match(/"(.*?)"/)[1]]};
  const seeks = [];
  let selection = '', selectionNode;
  const player = {cueAt, connect: (frame, cb, fail) => { connected = true; connections++; callback = cb; errorCallback = fail; return Promise.resolve({seek:(...args) => seeks.push(args), destroy() {}}); }};
  vm.runInNewContext(source, {document, NodeFilter:{SHOW_TEXT:4, FILTER_REJECT:2, FILTER_ACCEPT:1}, window:{TliLyricPlayer:player, getSelection:() => ({toString:() => selection, anchorNode:selectionNode, focusNode:selectionNode})}, TliLyricPlayer:player, URL, URLSearchParams,
    location:{hostname:'example.com', search:''},
    matchMedia: query => ({matches:query === '(max-width: 700px)' ? mobile : true})});
  return {lines, controls, follow, label, connected, seeks, placement, get connections() { return connections; }, get replacements() { return replacements; },
    fail:() => errorCallback(new Error('Temporary player error')),
    select:(value, outside = false) => { selection = value; selectionNode = outside ? {} : lines.first; }, tick:(time,state=1) => callback(time,state)};
}
assert.equal(fixture('draft').connected, true);
const ui = fixture();
assert.equal(ui.placement, 'heading:afterend');
assert.equal(fixture('draft', true, true, false).placement, 'figure:afterend');
assert.equal(fixture('draft', true, false, false).placement, 'iframe:afterend');
assert.equal(ui.follow.checked, true);
ui.tick(10); assert.equal(ui.lines.first.active, true); assert.equal(ui.lines.first.scrolled, 1);
ui.tick(12,2); assert.equal(ui.lines.first.active, true); // Pause retains the current sentence.
ui.tick(17); assert.equal(ui.lines.first.active, true); // Keep the line through the gap.
ui.follow.checked = true;
ui.tick(20); assert.equal(ui.lines.repeat.active, true); assert.equal(ui.lines.repeat.scrolled, 1);
ui.tick(10,2); assert.equal(ui.lines.first.active, true); assert.equal(ui.lines.repeat.active, false);
ui.tick(25,0); assert.equal(ui.lines.first.active, false);
const desktop = fixture('draft', false);
assert.equal(desktop.follow.checked, false);
desktop.tick(10);
assert.equal(desktop.lines.first.scrolled, 0);
desktop.follow.checked = true;
desktop.tick(20);
assert.equal(desktop.lines.repeat.active, true);
assert.equal(desktop.lines.repeat.scrolled, 1);
console.log('PASS: highlight states, pause/seek, responsive follow defaults and draft playback.');
const early = fixture();
early.lines.repeat.listeners.click({target:{closest:() => null}});
assert.equal(early.seeks.length, 0);
Promise.resolve().then(async () => {
  assert.deepEqual(early.seeks, [[20, true]]);
  assert.equal(typeof ui.lines.first.listeners.click, 'function', 'Both lyric rows share the paragraph seek handler');
  assert.equal(ui.lines.first.seekTargets.length, 2, 'Mixed text and Lomari get text cursor wrappers');
  assert.equal(ui.lines.first.attributes.tabindex, undefined);
  const line = ui.lines.first.seekTarget;
  const target = {closest:() => null};
  ui.lines.first.listeners.click({target});
  assert.deepEqual(ui.seeks, [[10, true]]);
  for (const tag of ['rt', 'rp', '.tli-rt', '.tone-mark', 'a']) {
    ui.lines.first.listeners.click({target:{closest:selector => selector.includes(tag) ? {} : null}});
  }
  assert.equal(ui.seeks.length, 1, 'Ruby, tone annotations and links must not seek');
  ui.select('selected lyrics');
  ui.lines.first.listeners.click({target});
  assert.equal(ui.seeks.length, 1);
  ui.select('Text selected elsewhere', true);
  ui.lines.first.listeners.click({target});
  assert.deepEqual(ui.seeks[1], [10, true]);
  let prevented = false;
  line.listeners.keydown({target:line, key:'Enter', preventDefault:() => { prevented = true; }});
  assert.equal(prevented, true);
  assert.deepEqual(ui.seeks[1], [10, true]);
  assert.equal(line.attributes.tabindex, '0');
  // A failed connection must be recoverable by another explicit lyric click.
  await new Promise(resolve => setImmediate(resolve));
  ui.fail();
  ui.lines.first.listeners.click({target});
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(ui.connections, 2);
  assert.equal(ui.replacements, 1);
  assert.deepEqual(ui.seeks.at(-1), [10, true]);
  console.log('PASS: click/keyboard seeking, nested links and text selection.');
  let events;
  const calls = [];
  const fakePlayer = {seekTo:(...args) => calls.push(['seek', ...args]), playVideo:() => calls.push(['play']),
    getCurrentTime:() => 20, getPlayerState:() => 1, destroy() {}};
  const window = {YT:{Player:function(frame, options) { events = options.events; return fakePlayer; }},
    addEventListener() {}, removeEventListener() {}};
  const context = {window, URL, location:{href:'https://example.com/songs/', origin:'https://example.com'},
    document:{hidden:false, addEventListener() {}, removeEventListener() {}},
    setInterval:() => 1, clearInterval() {}};
  vm.runInNewContext(fs.readFileSync(require.resolve('../shared/web-lyric-player.js'), 'utf8'), context);
  const frame = {src:'https://www.youtube.com/embed/HNYkSBkQ33Y'};
  const controller = await window.TliLyricPlayer.connect(frame, () => {});
  controller.seek(10, true);
  controller.seek(20, true);
  assert.equal(calls.length, 0);
  events.onReady();
  assert.deepEqual(calls, [['seek', 20, true], ['play']]);
  assert.equal(frame.loading, 'eager');
  controller.seek(10, true);
  assert.deepEqual(calls.slice(2), [['seek', 10, true], ['play']]);
  controller.destroy();
  console.log('PASS: clicks before API/player readiness are queued; latest seek wins.');
}).catch(error => { console.error(error); process.exitCode = 1; });
