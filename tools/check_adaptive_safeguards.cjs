// Exodus II: deterministic fixtures and real shared-controller event paths.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const fixture = JSON.parse(fs.readFileSync(path.join(root, 'tests/fixtures/adaptive-safeguard-cases.json')));
const data = JSON.parse(fs.readFileSync(path.join(root, 'public/data/hokkien-hanri-dict.json')));
const namespace = 'tangliengim.candidatePreferences.v1';
const plain = value => JSON.parse(JSON.stringify(value));
const order = candidates => Array.from(candidates, c => c.entry.id);
const event=key=>({key,preventDefault(){}});
function element() {
  const listeners = {};
  return {value:'', selectionStart:0, selectionEnd:0, children:[], listeners,
    classList:{add(){},remove(){},toggle(){}}, setAttribute(){}, focus(){},
    addEventListener(name, fn){listeners[name]=fn;}, contains(node){return this === node || this.children.includes(node);},
    setSelectionRange(a,b){this.selectionStart=a;this.selectionEnd=b;},
    replaceChildren(...items){this.children=items;}, append(...items){this.children.push(...items);}};
}
function surface(shared = new Map(), failure = {}) {
  const listeners = {};
  const storage = {
    getItem(key){if(failure.read) throw Error('read denied');return shared.get(key) ?? null;},
    setItem(key,value){if(failure.write) throw Error('quota exceeded');shared.set(key,value);},
  };
  const context = vm.createContext({console, document:{addEventListener(name,fn){listeners[name]=fn;},
    createElement:element,createDocumentFragment:element,createTextNode:text=>({textContent:text})},
    addEventListener(name,fn){listeners[name]=fn;}});
  context.window=context;
  Object.defineProperty(context,'localStorage',{get(){if(failure.access) throw Error('access denied');return failure.absent ? undefined : storage;}});
  for(const file of ['shared/web-hangul-ime.js','shared/web-ime-core.js'])
    vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),context);
  return {context,core:context.TangliengimImeCore,listeners,shared};
}
const {core} = surface();
const active = new Set(fixture.ids);
for(const payload of fixture.malformed)
  assert.deepEqual(plain(core.sanitizeCandidatePreferences(payload,active)),{version:1,selections:{}});
assert.deepEqual(plain(core.sanitizeCandidatePreferences(fixture.mixed,active)),fixture.sanitized);
assert.deepEqual(plain(core.sanitizeCandidatePreferences(fixture.integral_numbers,active)),fixture.integral_expected);
assert.deepEqual(plain(core.sanitizeCandidatePreferences({version:1,selections:{x:{A:NaN,B:Infinity,C:true}}},active)),{version:1,selections:{}});
const menu = fixture.ids.map(id=>({entry:{id}}));
const largest=Math.max(...Array.from(core.createDictionaryIndex(data.entries).candidatesByReading.values(),items=>items.length));
assert.ok(Number.isSafeInteger(core.adaptiveScore(largest-1,255)));
function stored(payload) {
  const s=surface(new Map([[namespace,JSON.stringify(payload)]]));
  return s.core.createCandidatePreferences({activeIds:fixture.ids});
}
for(let position=1;position<menu.length;position++) {
  let previous=position;
  for(let count=0;count<=255;count++) {
    const p=stored({version:1,selections:{x:{[fixture.ids[position]]:count}}});
    const ranked=order(p.rank(menu,'x'));
    const current=ranked.indexOf(fixture.ids[position]);
    assert.ok(current<=previous,'Learning must be monotonic');previous=current;
    const expected=menu.map((c,i)=>({id:c.entry.id,i,score:i*2-(i===position?count:0)}))
      .sort((a,b)=>a.score-b.score||a.i-b.i).map(c=>c.id);
    assert.deepEqual(ranked,expected);
    assert.deepEqual(order(p.rank(menu,'x')),ranked);
  }
}
for(const test of fixture.mutation) {
  const p=stored({version:1,selections:{x:{B:3,stale:255}}});
  const before=plain(p.snapshot());
  assert.deepEqual(order(p.rank(test.entries.map(entry=>({entry})),'x')),test.expected,test.name);
  assert.deepEqual(plain(p.snapshot()),before,'Ranking may not rewrite history');
}
let seed=fixture.seed;
const next=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
for(let n=0;n<fixture.adversarial_cases;n++) {
  const counts=Object.fromEntries(fixture.ids.map(id=>[id,next()%256]));
  const p=stored({version:1,selections:{x:counts}});
  const reversed=stored({selections:{x:Object.fromEntries(Object.entries(counts).reverse())},version:1});
  const expected=menu.map((c,i)=>({id:c.entry.id,i,score:i*2-counts[c.entry.id]}))
    .sort((a,b)=>a.score-b.score||a.i-b.i).map(c=>c.id);
  assert.deepEqual(order(p.rank(menu,'x')),expected);
  assert.deepEqual(order(reversed.rank(menu,'x')),expected);
}
const isolated=core.createCandidatePreferences({activeIds:fixture.ids});
for(const key of fixture.contexts) {isolated.record(key,'A');assert.equal(isolated.count(key,'A'),1);}
assert.equal(isolated.count("'시",'A'),1);
assert.equal(isolated.count('시ˍ','A'),1); // Existing tone normalization, not a new identity rule.
assert.equal(isolated.count('시','B'),0);
const long='家'.repeat(4096);isolated.record(long,'B');assert.equal(isolated.count(long,'B'),1);
isolated.record('', 'A');isolated.record('unknown','stale');
assert.ok(!isolated.snapshot().selections.unknown);
const detached=isolated.snapshot();detached.selections['시'].A=NaN;
assert.equal(isolated.count('시','A'),1,'Snapshots cannot corrupt internal state');
isolated.setActiveIds(['B']);assert.equal(isolated.count('시','A'),0);

// Storage failure must not block memory learning or actual candidate commits.
for(const failure of [{absent:true},{access:true},{read:true},{write:true},{}]) {
  const s=surface(new Map(),failure),p=s.core.createCandidatePreferences({activeIds:fixture.ids});
  if(!Object.keys(failure).length) vm.runInContext('JSON.stringify = () => {throw Error("serialization");}',s.context);
  p.record('x','B');assert.equal(p.count('x','B'),1);
  p.reset();assert.deepEqual(plain(p.snapshot()).selections,{});
  const ime=s.core.createTextImeController({control:element(),candidateContainer:element(),entries:data.entries,candidateLimit:10000});
  show(ime,'시');ime.candidateContainer.children[0].listeners.click();
  assert.ok(ime.control.value,'Storage failure must never lose the selected text');
}
for(const raw of ['', '{broken', 'null', '[]', '42', '{"version":999}', JSON.stringify(fixture.mixed)]) {
  const s=surface(new Map([[namespace,raw]]));
  const ime=s.core.createTextImeController({control:element(),candidateContainer:element(),entries:data.entries});
  show(ime,'시');assert.ok(ime.activeCandidates.length);ime.handleKeydown(event('Enter'));
  assert.ok(ime.control.value);
}
const shared=new Map(),a=surface(shared).core.createCandidatePreferences({activeIds:fixture.ids}),
  b=surface(shared).core.createCandidatePreferences({activeIds:fixture.ids});
a.record('x','B');b.record('x','B');a.record('x','A');
assert.equal(a.count('x','B'),2);assert.equal(b.count('x','A'),1);
b.reset();assert.deepEqual(plain(a.snapshot()).selections,{});
const failed={write:true},pending=surface(shared,failed).core.createCandidatePreferences({activeIds:fixture.ids});
pending.record('x','B');a.record('x','A');failed.write=false;pending.record('x','B');
assert.equal(a.count('x','A'),1);assert.equal(a.count('x','B'),2);
failed.read=true;pending.record('x','B');assert.equal(pending.count('x','B'),3);
assert.equal(JSON.parse(shared.get(namespace)).selections.x.B,2,'Never overwrite an unreadable store');
failed.read=false;pending.record('x','B');assert.equal(a.count('x','B'),4);
failed.write=true;for(let i=0;i<300;i++)pending.record('x','B');
failed.write=false;pending.record('x','B');assert.equal(a.count('x','B'),255);
a.reset();assert.deepEqual(plain(pending.snapshot()).selections,{});

function show(ime,text) {
  ime.control.value=text;ime.control.setSelectionRange(text.length,text.length);
  ime.unresolvedCandidateContext=ime.candidateContextKey();ime.renderCandidates();return ime.activeCandidates;
}
function controller(options={}) {
  const s=surface();
  const ime=s.core.createTextImeController({control:element(),candidateContainer:element(),entries:data.entries,candidateLimit:10000,...options});
  return {ime,s};
}
for(const action of [
  ime=>ime.dismissCandidates(),ime=>ime.handleKeydown(event('Enter')),
  ime=>{ime.handleKeydown(event('Tab'));ime.handleKeydown(event('Escape'));},
  ime=>{ime.handleKeydown(event('ArrowDown'));ime.handleKeydown(event('ArrowRight'));},
  ime=>{ime.handleKeydown(event('Tab'));ime.handleKeydown(event('q'));},
  ime=>{ime.setCandidateIndex(1);ime.handleKeydown(event('Enter'));},
  ime=>{ime.handleKeydown(event('Tab'));ime.handleBeforeInput({inputType:'insertFromPaste',cancelable:false});},
  ime=>{ime.handleKeydown(event('Tab'));ime.handleInput({inputType:'insertText'});},
  ime=>{ime.handleKeydown(event('Tab'));ime.handleCompositionStart();},
  ime=>{ime.handleCompositionStart();ime.control.value='시먀';ime.control.setSelectionRange(2,2);
    ime.handleCompositionUpdate({data:'먀'});ime.handleCompositionEnd({data:'먀'});},
  ime=>ime.handleCursorChange({type:'click'}),
  ime=>{ime.onUpdate();ime.renderCandidates();},
]) {
  const {ime}=controller({recomposeNativeKoreanInput:true});show(ime,'시');action(ime);
  assert.deepEqual(plain(ime.preferences.snapshot()).selections,{},'Passive event learned');
}
for(const cancel of [ime=>ime.handleBeforeInput({inputType:'insertFromPaste',cancelable:false}),
  ime=>ime.handleInput({inputType:'insertText'})]) {
  const {ime}=controller();show(ime,'시');ime.handleKeydown(event('Tab'));cancel(ime);
  ime.handleKeydown(event('Enter'));assert.deepEqual(plain(ime.preferences.snapshot()).selections,{});
}
const {ime:outside,s:outsideSurface}=controller();show(outside,'시');
outside.handleKeydown(event('Tab'));
outsideSurface.listeners.pointerdown?.({target:element()});
assert.deepEqual(plain(outside.preferences.snapshot()).selections,{});
assert.equal(outside.activeCandidates.length,0,'Outside dismissal must close the active menu');
for(const select of ['click','Tab','ArrowUp','ArrowDown']) {
  const {ime}=controller();show(ime,'시');let candidate;
  if(select==='click') {
    candidate=ime.activeCandidates[0];const button=ime.candidateContainer.children[0];
    button.listeners.mousedown(event(''));button.listeners.click();button.listeners.click();
  } else {
    ime.handleKeydown(event(select));candidate=ime.activeCandidates[ime.activeCandidateIndex];
    ime.handleCursorChange({type:'keyup',key:select});ime.renderCandidates();
    ime.handleKeydown(event('Enter'));ime.handleCursorChange({type:'keyup',key:'Enter'});
  }
  ime.applyCandidate(candidate,true);
  if(candidate.entry.generatedCandidate) assert.deepEqual(plain(ime.preferences.snapshot()).selections,{});
  else assert.equal(ime.preferences.count(candidate.lookupKey,candidate.entry.raw.entry_id),1,select);
}
const {ime:reentrant}=controller();show(reentrant,'시');const choice=reentrant.activeCandidates[0];
const record=reentrant.preferences.record;
reentrant.preferences.record=(key,id)=>{reentrant.applyCandidate(choice,true);record(key,id);};
reentrant.applyCandidate(choice,true);assert.equal(reentrant.preferences.count(choice.lookupKey,choice.entry.raw.entry_id),1);

async function backends() {
  let disk={version:1,selections:{x:{B:3}}};
  const backend={load:async()=>disk,record:async(key,id)=>{
    const group=disk.selections[key] ||= {};group[id]=(group[id]||0)+1;
    return {preferences:plain(disk)};
  },reset:async()=>{disk={version:1,selections:{}};return {preferences:disk};}};
  const p=core.createCandidatePreferences({activeIds:fixture.ids,backend});await p.ready;
  p.record('x','B');p.record('x','B');await p.settled();assert.equal(p.count('x','B'),5);
  disk={version:1,selections:{x:{C:10}}};await p.reload();assert.equal(p.count('x','C'),10);
  p.record('x','B');p.reset();await p.settled();assert.deepEqual(plain(p.snapshot()).selections,{});
  const offline=core.createCandidatePreferences({activeIds:fixture.ids,backend:{
    load:async()=>{throw Error('offline');},record:async()=>{throw Error('offline');},reset:async()=>{throw Error('offline');}}});
  await offline.ready;offline.record('x','B');await offline.settled();assert.equal(offline.count('x','B'),1);
  offline.reset();await offline.settled();assert.deepEqual(plain(offline.snapshot()).selections,{});
  console.log('PASS: Exodus II Web safeguards; 1,024 monotonic counts, 160 seeded rankings, storage corruption/failures, multi-tab convergence, event exclusions, exactly-once commits, backend refresh/reset.');
}
backends().catch(error=>{console.error(error);process.exitCode=1;});
