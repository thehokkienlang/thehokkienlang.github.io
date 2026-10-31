(function (root) {
  'use strict';
  function fold(value, mapping) {
    return [...String(value || '')].map(char => mapping[char] || char).join('');
  }
  function match(value, term, mapping) {
    let folded = '';
    const starts = [], ends = [];
    let offset = 0;
    for (const char of value) {
      const part = fold(char.toLocaleLowerCase(), mapping);
      for (let i = 0; i < part.length; i++) { starts.push(offset); ends.push(offset + char.length); }
      folded += part;
      offset += char.length;
    }
    const index = folded.indexOf(fold(term.toLocaleLowerCase(), mapping));
    return index < 0 ? null : {index: starts[index], length: ends[index + fold(term.toLocaleLowerCase(), mapping).length - 1] - starts[index]};
  }
  const api = {fold, match};
  if (typeof module !== 'undefined') module.exports = api;
  root.TliSiteSearchVariants = api;
})(typeof window !== 'undefined' ? window : globalThis);
