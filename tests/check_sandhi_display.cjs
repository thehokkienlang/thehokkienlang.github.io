// Song lyrics and titles shown with Singapore sandhi (shared/web-sandhi-display.js): an open
// syllable marked tone 1 and joined to the next becomes tone 4; everything else is unchanged.
const assert = require('node:assert/strict');
const path = require('node:path');

const {singaporeReading, singaporeLomari, lomariParts, variesIndexes} = require(path.resolve(__dirname, '../shared/web-sandhi-display.js'));

const readings = [
  // A lyric reading joined by "-" (講 겅ˆ-, 歹 팰ˆ-) or by a following syllable (啥物, 明仔載).
  ['겅ˆ-', {}, '겅ˊ-'],
  ['팰ˆ-', {}, '팰ˊ-'],
  ['샬ˆ밓ˆ', {}, '샬ˊ밓ˆ'],
  ['삔아ˆ재', {}, '삔아ˊ재'],
  ['주ˆ쟣ˆ', {}, '주ˊ쟣ˆ'],
  ['ᄀᅷˆ새ˋ', {}, 'ᄀᅷˊ새ˋ'],
  // Not joined: the end of a reading with no "-" (開 before ’됴, 薰 before a space).
  ['퀴ˆ', {}, '퀴ˆ'],
  ['훈ˆ', {}, '훈ˆ'],
  // Checked syllables keep tone 1 (1 <-> 3 in both varieties).
  ['갛ˆ-', {}, '갛ˆ-'],
  ['ᄃᅷᇂᄃᅷᇂ아ˆ-', {}, 'ᄃᅷᇂᄃᅷᇂ아ˊ-'],
  ['칟ˆ토ˊ', {}, '칟ˆ토ˊ'],
  // Other tones are never touched.
  ['태ˋ더ˉ', {}, '태ˋ더ˉ'],
  // A tone-only ruby: its syllable is the base, and what follows on the line decides.
  ['ꞈ', {base: '꽈', joinedAfter: true}, 'ˏ'],
  ['ꞈ', {base: '꽈', joinedAfter: false}, 'ꞈ'],
  ['ꞈ', {base: '곻', joinedAfter: true}, 'ꞈ'],
  // A title reading or bare title text: what follows decides.
  ['보ˆ', {joinedAfter: true}, '보ˊ'],
  ['보ˆ', {joinedAfter: false}, '보ˆ'],
  ['곻ˆ', {joinedAfter: true}, '곻ˆ'],
  // Stored dictionary readings in digits: only a joined open 1 changes.
  ['팰1세', {}, '팰4세'],
  ['팰1랑4', {}, '팰4랑4'],
  ['쇼1옿3셀1', {}, '쇼4옿3셀1'],
  ['진5호2', {}, '진5호2'],
  ['학3셀1', {}, '학3셀1'],
  ['갛1-', {}, '갛1-'],
];
for (const [taipei, options, singapore] of readings) {
  assert.equal(singaporeReading(taipei, options), singapore, `${taipei} ${JSON.stringify(options)}`);
}

const lomari = [
  ['goà ìn-kông-lông-si-goà m-tiôh', 'goà ìn-kóng-lóng-si-goà m-tiôh'],
  ['lì mng-goà si-siâ̰-mîh thài-tōr', 'lì mng-goà si-siá̰-mîh thài-tōr'],
  ['bin-â-jai', 'bin-á-jai'],
  ['jû-jiâh', 'jú-jiâh'],
  ['Pô-pi', 'Pó-pi'],
  // Not joined (neutral tone, space, end) or checked: unchanged.
  ['khûi’tio pat-â-phio', 'khûi’tio pat-á-phio'],
  ['khui--tiô', 'khui--tiô'],
  ['hûn mài-kôh-jiâh, jiù boe-kôh-tâ', 'hûn mài-kôh-jiâh, jiù boe-kôh-tâ'],
  ['Kôh-ài-lì', 'Kôh-ài-lì'],
];
for (const [taipei, singapore] of lomari) {
  assert.equal(singaporeLomari(taipei).normalize('NFC'), singapore.normalize('NFC'), taipei);
}

// The varying marks (coloured in both modes) are exactly the ones Singapore changes.
assert.deepEqual([...variesIndexes('삔아ˆ재', singaporeReading('삔아ˆ재'))], [2]);
assert.deepEqual([...variesIndexes('팰1세', singaporeReading('팰1세'))], [1]);
const parts = lomariParts('goà ìn-kông-lông', false);
assert.equal(parts.map(part => part.text).join(''), 'goà ìn-kông-lông');
assert.deepEqual(parts.filter(part => part.varies).map(part => part.text), ['ô']);
assert.equal(lomariParts('goà ìn-kông-lông', true).map(part => part.text).join('').normalize('NFC'), 'goà ìn-kóng-lông'.normalize('NFC'));

console.log(`Sandhi display: ${readings.length} readings and ${lomari.length} Lomari lines derive Singapore correctly.`);
