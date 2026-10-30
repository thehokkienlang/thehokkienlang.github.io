const assert = require('node:assert/strict');
const { cueAt } = require('../shared/web-lyric-player.js');
const cues = [{ id:'intro-gap', start:null, end:null }, { id:'first', start:10, end:15 },
  { id:'repeat', start:20, end:25 }];
assert.equal(cueAt(cues, 0), null);
assert.equal(cueAt(cues, 9.999), null);
assert.equal(cueAt(cues, 10).id, 'first');
assert.equal(cueAt(cues, 14.99).id, 'first');
assert.equal(cueAt(cues, 15), null);
assert.equal(cueAt(cues, 20).id, 'repeat');
assert.equal(cueAt(cues, 10).id, 'first'); // Backward seek uses the video clock.
assert.equal(cueAt(cues, NaN), null);
assert.equal(cueAt(cues, 25), null);
console.log('PASS: lyric boundaries, gaps, repeats and backward seeks.');

// Exercise the public UI without inventing timings for the real recording.
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync(require.resolve('../shared/web-lyric-sync.js'), 'utf8');
function fixture(status = 'reviewed', local = false) {
  const makeLine = () => ({ active:false, current:false, scrolled:0,
    classList:{ add() { this.owner.active = true; }, remove() { this.owner.active = false; } },
    setAttribute() { this.current = true; }, removeAttribute() { this.current = false; },
    scrollIntoView() { this.scrolled++; } });
  const lines = {first:makeLine(), repeat:makeLine()};
  Object.values(lines).forEach(line => line.classList.owner = line);
  let callback, connected = false;
  const label = {textContent:''}, follow = {checked:false};
  const controls = {hidden:true, querySelector: selector => selector === 'input' ? follow : label};
  const document = {getElementById: () => ({textContent:JSON.stringify({status,videoId:'HNYkSBkQ33Y',cues})}),
    querySelectorAll: () => [{src:'https://www.youtube.com/embed/HNYkSBkQ33Y'}],
    querySelector: selector => selector === '.lyric-sync-controls' ? controls : lines[selector.match(/"(.*?)"/)[1]]};
  const player = {cueAt, connect: (frame, cb) => { connected = true; callback = cb; return Promise.resolve({}); }};
  vm.runInNewContext(source, {document, window:{TliLyricPlayer:player}, TliLyricPlayer:player, URL, URLSearchParams,
    location:{hostname:local ? '127.0.0.1' : 'example.com', search:local ? '?lyric-preview=1' : ''},
    matchMedia: () => ({matches:true})});
  return {lines, controls, follow, label, connected, tick:(time,state=1) => callback(time,state)};
}
assert.equal(fixture('draft').connected, false);
assert.equal(fixture('draft', true).connected, true);
const ui = fixture();
ui.tick(10); assert.equal(ui.lines.first.active, true); assert.equal(ui.lines.first.scrolled, 0);
ui.tick(12,2); assert.equal(ui.lines.first.active, true); // Pause retains the current sentence.
ui.tick(17); assert.equal(ui.lines.first.active, false); // Instrumental gap.
ui.follow.checked = true;
ui.tick(20); assert.equal(ui.lines.repeat.active, true); assert.equal(ui.lines.repeat.scrolled, 1);
ui.tick(10,2); assert.equal(ui.lines.first.active, true); assert.equal(ui.lines.repeat.active, false);
ui.tick(25,0); assert.equal(ui.lines.first.active, false);
console.log('PASS: highlight states, pause/seek, opt-in scrolling and draft gate.');
