// The site-wide sandhi preference (shared/web-sandhi-preference.js): the default for a first visit,
// storage that can fail, unknown stored values, and change notifications.
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const vm = require('node:vm');

const preference = require(path.resolve(__dirname, '../shared/web-sandhi-preference.js'));
const {createPreference, STORAGE_KEY} = preference;

const memoryStore = (initial = {}) => {
  const values = {...initial};
  return {getItem: key => (key in values ? values[key] : null), setItem: (key, value) => { values[key] = String(value); }, values};
};
const brokenStore = () => ({
  getItem() { throw new Error('storage blocked'); },
  setItem() { throw new Error('storage blocked'); },
});
// A visitor in Singapore starts in Taipei mode and can explicitly switch to Singapore.
const first = memoryStore();
const script = fs.readFileSync(require.resolve('../shared/web-sandhi-preference.js'), 'utf8');
const visit = () => {
  const browser = {
    navigator: {languages: ['en-SG']},
    Intl: {DateTimeFormat: () => ({resolvedOptions: () => ({timeZone: 'Asia/Singapore'})})},
    localStorage: first,
  };
  vm.runInNewContext(script, browser);
  return browser.TliSandhiPreference;
};
assert.equal(visit().get(), 'taipei');
assert.deepEqual(first.values, {}, 'reading the default must not write to storage');
visit().set('singapore');
assert.equal(visit().get(), 'singapore');
visit().set('taipei');
assert.equal(visit().get(), 'taipei');

// An unknown stored value is ignored.
for (const bad of ['', 'Singapore', 'both', '14', 'null']) {
  assert.equal(createPreference({storage: memoryStore({[STORAGE_KEY]: bad}), target: null}).get(), 'taipei', `stored ${JSON.stringify(bad)}`);
}

// A blocked store falls back to the default, and a choice is still kept for this page.
const blocked = createPreference({storage: brokenStore(), target: null});
assert.equal(blocked.get(), 'taipei');
assert.equal(blocked.set('singapore'), 'singapore');
assert.equal(blocked.get(), 'singapore');
assert.equal(createPreference({storage: null, target: null}).get(), 'taipei');

// set() stores a valid mode, ignores an invalid one, and tells listeners only about real changes.
const store = memoryStore();
const live = createPreference({storage: store, target: null});
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
const tab = createPreference({storage: shared, target: null});
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
const evented = createPreference({storage: memoryStore(), target});
evented.set('singapore');
assert.deepEqual(events, ['singapore']);

// The labels exist for the three site languages.
for (const language of ['en', 'zh-Hant', 'zh-Hans']) {
  for (const key of ['sandhi', 'taipei', 'singapore', 'note']) assert.ok(preference.LABELS[language][key], `${language}.${key}`);
}

console.log('OK: the sandhi preference follows its default, storage, change and failure rules.');
