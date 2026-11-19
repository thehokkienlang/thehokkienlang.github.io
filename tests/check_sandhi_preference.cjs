// The site-wide sandhi preference (shared/web-sandhi-preference.js): the default for a first visit,
// storage that can fail, unknown stored values, and change notifications.
const assert = require('node:assert/strict');
const path = require('node:path');

const preference = require(path.resolve(__dirname, '../shared/web-sandhi-preference.js'));
const {createPreference, defaultMode, inSingapore, STORAGE_KEY} = preference;

const memoryStore = (initial = {}) => {
  const values = {...initial};
  return {getItem: key => (key in values ? values[key] : null), setItem: (key, value) => { values[key] = String(value); }, values};
};
const brokenStore = () => ({
  getItem() { throw new Error('storage blocked'); },
  setItem() { throw new Error('storage blocked'); },
});
const taipeiVisitor = {languages: ['en-US', 'zh-TW'], timeZone: 'Asia/Taipei'};

// Who counts as "in Singapore": a region tag or the time zone, nothing else.
for (const languages of [['en-SG'], ['zh-SG'], ['ms-SG'], ['ta-SG'], ['en-US', 'zh-Hans-SG'], ['en-sg']]) {
  assert.ok(inSingapore({languages, timeZone: 'Asia/Taipei'}), `${languages} should count as Singapore`);
}
assert.ok(inSingapore({languages: ['en-US'], timeZone: 'Asia/Singapore'}));
for (const env of [taipeiVisitor, {languages: ['zh-CN'], timeZone: 'Asia/Shanghai'}, {languages: ['en'], timeZone: ''},
  {languages: ['en-GB', 'fr-CH'], timeZone: 'Europe/London'}, {languages: 'en-SG', timeZone: ''}, {}, null, undefined]) {
  assert.ok(!inSingapore(env), `${JSON.stringify(env)} should not count as Singapore`);
}
assert.equal(defaultMode({languages: ['en-SG'], timeZone: ''}), 'singapore');
assert.equal(defaultMode(taipeiVisitor), 'taipei');

// A first visit uses the default and stores nothing, so the default can change later.
const first = memoryStore();
assert.equal(createPreference({storage: first, env: taipeiVisitor, target: null}).get(), 'taipei');
assert.equal(createPreference({storage: first, env: {languages: ['en-SG'], timeZone: ''}, target: null}).get(), 'singapore');
assert.deepEqual(first.values, {}, 'reading the default must not write to storage');

// A stored choice wins over the default, in both directions.
assert.equal(createPreference({storage: memoryStore({[STORAGE_KEY]: 'taipei'}), env: {languages: ['en-SG'], timeZone: ''}, target: null}).get(), 'taipei');
assert.equal(createPreference({storage: memoryStore({[STORAGE_KEY]: 'singapore'}), env: taipeiVisitor, target: null}).get(), 'singapore');

// An unknown stored value is ignored.
for (const bad of ['', 'Singapore', 'both', '14', 'null']) {
  assert.equal(createPreference({storage: memoryStore({[STORAGE_KEY]: bad}), env: taipeiVisitor, target: null}).get(), 'taipei', `stored ${JSON.stringify(bad)}`);
}

// A blocked store falls back to the default, and a choice is still kept for this page.
const blocked = createPreference({storage: brokenStore(), env: taipeiVisitor, target: null});
assert.equal(blocked.get(), 'taipei');
assert.equal(blocked.set('singapore'), 'singapore');
assert.equal(blocked.get(), 'singapore');
assert.equal(createPreference({storage: null, env: taipeiVisitor, target: null}).get(), 'taipei');

// set() stores a valid mode, ignores an invalid one, and tells listeners only about real changes.
const store = memoryStore();
const live = createPreference({storage: store, env: taipeiVisitor, target: null});
const seen = [];
const stop = live.onChange(mode => seen.push(mode));
live.set('singapore');
live.set('singapore');
assert.equal(live.set('klingon'), 'singapore');
live.set('taipei');
assert.deepEqual(seen, ['singapore', 'taipei']);
assert.equal(store.values[STORAGE_KEY], 'taipei');
stop();
live.set('singapore');
assert.deepEqual(seen, ['singapore', 'taipei'], 'a removed listener hears nothing');

// A change made in another tab arrives as a storage event.
const shared = memoryStore();
const tab = createPreference({storage: shared, env: taipeiVisitor, target: null});
const heard = [];
tab.onChange(mode => heard.push(mode));
assert.equal(tab.get(), 'taipei');
shared.setItem(STORAGE_KEY, 'singapore');
tab.receiveStorageEvent({key: 'something-else'});
assert.deepEqual(heard, []);
tab.receiveStorageEvent({key: STORAGE_KEY});
assert.deepEqual(heard, ['singapore']);
assert.equal(tab.get(), 'singapore');

// The page dispatches a DOM event too, so scripts that don't import this module can listen.
const events = [];
const target = {dispatchEvent: event => { events.push(event.detail.mode); }};
globalThis.CustomEvent = class { constructor(type, init) { this.type = type; this.detail = init.detail; } };
const evented = createPreference({storage: memoryStore(), env: taipeiVisitor, target});
evented.set('singapore');
assert.deepEqual(events, ['singapore']);

// The labels exist for the three site languages.
for (const language of ['en', 'zh-Hant', 'zh-Hans']) {
  for (const key of ['sandhi', 'taipei', 'singapore', 'note']) assert.ok(preference.LABELS[language][key], `${language}.${key}`);
}

console.log('OK: the sandhi preference follows its default, storage, change and failure rules.');
