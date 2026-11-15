const assert = require('node:assert/strict');
const {fold, match} = require('../shared/web-site-search-variants.js');
const mapping = {'愛':'爱', '學':'学', '習':'习', '後':'后', '𠢕':'𫝈'};
assert.equal(fold('愛學習', mapping), '爱学习');
assert.equal(fold('爱学习', mapping), '爱学习');
assert.deepEqual(match('愛學習和後', '爱学习', mapping), {index:0, length:3});
assert.deepEqual(match('爱学习和后', '愛學習', mapping), {index:0, length:3});
assert.deepEqual(match('𠢕後見', '𫝈后', mapping), {index:0, length:3});
assert.equal(match('Hokkien', '福建', mapping), null);
// Tone marks: the inline, above-syllable and ASCII typing forms of a tone match each other.
const {toneMarkFold} = require('../shared/web-site-search-variants.js');
const tones = {...mapping, ...toneMarkFold};
assert.deepEqual(match('水쉬` 好', '쉬ˋ', tones), {index:1, length:2});
assert.deepEqual(match('水쉬ˋ 好', '쉬`', tones), {index:1, length:2});
assert.deepEqual(match('덩ꞈ', '덩ˆ', tones), {index:0, length:2});
assert.deepEqual(match('덩ˏ 덩ˍ', '덩ˉ', tones), {index:3, length:2});
assert.equal(match('덩ˊ', '덩ˉ', tones), null, 'different tones must not match');
assert.equal(match('쉬ˋ', '쉬', tones)?.index, 0, 'a bare syllable still finds marked text');
// The shared rule: separators and Lomari diacritics fold away, tone marks stay.
const {normalise} = require('../shared/web-site-search-variants.js');
assert.equal(normalise('Siêng’e  Kâh-loh', mapping), 'sieng' + 'e' + 'kah' + 'loh');
assert.equal(normalise('덩ꞈ'), normalise('덩ˆ'), 'two spellings of one tone are equal');
assert.ok(normalise('맘ˉ 맘ˆ').includes(normalise('맘')), 'a bare syllable finds every tone');
assert.ok(normalise('맘ˉ').includes(normalise('맘ˉ')));
assert.ok(!normalise('맘ˆ').includes(normalise('맘ˉ')), 'a marked query finds only that tone');
assert.equal(normalise('愛學習', mapping), '爱学习');
console.log('PASS: Traditional/Simplified search folding and original-text offsets.');
