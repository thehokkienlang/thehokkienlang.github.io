// The Translator's tone overlay marks must be absolutely positioned over their
// syllable (zero-size anchor + centred mark), not left as inline text.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const css = fs.readFileSync(path.join(__dirname, '..', 'apps', 'translate', 'styles.css'), 'utf8');
const rule = selector => {
  const found = [...css.matchAll(/([^{}@]+)\{([^{}]*)\}/g)]
    .filter(match => match[1].split(',').map(part => part.trim()).includes(selector));
  assert.ok(found.length, `apps/translate/styles.css must style ${selector}`);
  return found.map(match => match[2]).join(';');
};
const anchor = rule('.tone-overlay-anchor');
assert.match(anchor, /position\s*:\s*absolute/, 'overlay anchor must be absolutely positioned');
assert.match(anchor, /width\s*:\s*0/, 'overlay anchor must take no inline width');
const mark = rule('.tone-overlay-mark');
assert.match(mark, /position\s*:\s*absolute/, 'overlay mark must be absolutely positioned');
assert.match(mark, /transform\s*:\s*translateX\(-50%\)/, 'overlay mark must be centred on its syllable');
assert.match(mark, /top\s*:\s*calc\(-/, 'overlay mark must sit above the line');
console.log('PASS: Translator tone overlay marks are positioned above their syllables.');
