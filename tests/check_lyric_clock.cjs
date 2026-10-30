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
function fixture(status = 'reviewed', mobile = true) {
  const makeLine = () => ({ active:false, current:false, scrolled:0, attributes:{}, listeners:{},
    classList:{ add() { this.owner.active = true; }, remove() { this.owner.active = false; } },
    setAttribute(name, value) { this.attributes[name] = value; if (name === 'aria-current') this.current = true; },
    removeAttribute(name) { delete this.attributes[name]; if (name === 'aria-current') this.current = false; },
    addEventListener(name, handler) { this.listeners[name] = handler; },
    scrollIntoView() { this.scrolled++; } });
  const lines = {first:makeLine(), repeat:makeLine()};
  Object.values(lines).forEach(line => line.classList.owner = line);
  let callback, connected = false;
  const label = {textContent:''}, follow = {checked:false};
  const controls = {hidden:true, querySelector: selector => selector === 'input' ? follow : label};
  const document = {getElementById: () => ({textContent:JSON.stringify({status,videoId:'HNYkSBkQ33Y',cues})}),
    querySelectorAll: () => [{src:'https://www.youtube.com/embed/HNYkSBkQ33Y'}],
    querySelector: selector => selector === '.lyric-sync-controls' ? controls : lines[selector.match(/"(.*?)"/)[1]]};
  const seeks = [];
  let selection = '';
  const player = {cueAt, connect: (frame, cb) => { connected = true; callback = cb; return Promise.resolve({seek:(...args) => seeks.push(args)}); }};
  vm.runInNewContext(source, {document, window:{TliLyricPlayer:player, getSelection:() => ({toString:() => selection})}, TliLyricPlayer:player, URL, URLSearchParams,
    location:{hostname:'example.com', search:''},
    matchMedia: query => ({matches:query === '(max-width: 700px)' ? mobile : true})});
  return {lines, controls, follow, label, connected, seeks, select:value => { selection = value; }, tick:(time,state=1) => callback(time,state)};
}
assert.equal(fixture('draft').connected, true);
const ui = fixture();
ui.tick(10); assert.equal(ui.lines.first.active, true); assert.equal(ui.lines.first.scrolled, 0);
ui.tick(12,2); assert.equal(ui.lines.first.active, true); // Pause retains the current sentence.
ui.tick(17); assert.equal(ui.lines.first.active, true); // Keep the line through the gap.
ui.follow.checked = true;
ui.tick(20); assert.equal(ui.lines.repeat.active, true); assert.equal(ui.lines.repeat.scrolled, 1);
ui.tick(10,2); assert.equal(ui.lines.first.active, true); assert.equal(ui.lines.repeat.active, false);
ui.tick(25,0); assert.equal(ui.lines.first.active, false);
const desktop = fixture('draft', false);
desktop.follow.checked = true;
desktop.tick(10);
assert.equal(desktop.lines.first.active, true);
assert.equal(desktop.lines.first.scrolled, 0);
console.log('PASS: highlight states, pause/seek, mobile-only opt-in scrolling and draft playback.');
const early = fixture();
early.lines.repeat.listeners.click({target:{closest:() => null}});
assert.equal(early.seeks.length, 0);
Promise.resolve().then(async () => {
  assert.deepEqual(early.seeks, [[20, true]]);
  const line = ui.lines.first;
  const target = {closest:() => null};
  line.listeners.click({target});
  assert.deepEqual(ui.seeks, [[10, true]]);
  line.listeners.click({target:{closest:() => ({})}});
  ui.select('selected lyrics');
  line.listeners.click({target});
  assert.equal(ui.seeks.length, 1);
  let prevented = false;
  line.listeners.keydown({target:line, key:'Enter', preventDefault:() => { prevented = true; }});
  assert.equal(prevented, true);
  assert.deepEqual(ui.seeks[1], [10, true]);
  assert.equal(line.attributes.tabindex, '0');
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
