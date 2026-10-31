const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const context = {window:{}, document:{
  createDocumentFragment:() => ({children:[], append(...nodes) { this.children.push(...nodes); }}),
  createTextNode:text => ({text}),
}};
vm.runInNewContext(fs.readFileSync(require.resolve('../shared/web-ime-core.js'), 'utf8'), context);
const core = context.window.TangliengimImeCore;
for (const char of ['𣍐', '𤆬', '𨑨', '𨘗']) {
  const unit = core.readingUnitAt(char, 0);
  assert.equal(unit.text, char);
  assert.equal(unit.end, 2);
  const rendered = core.renderToneMarkedReading(char);
  assert.equal(rendered.children.length, 1);
  assert.equal(rendered.children[0].children.length, 1);
  assert.equal(rendered.children[0].children[0].text, char);
}
assert.equal(core.readingUnitAt('가1', 0).end, 1);
assert.equal(core.readingUnitAt('가1', 0).canCarryTone, true);
console.log('PASS: supplementary Hanri remain whole text nodes; Hangul tone boundaries unchanged.');
