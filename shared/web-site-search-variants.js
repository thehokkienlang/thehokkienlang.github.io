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
  // One tone can be written with several characters: the inline mark, the
  // above-syllable mark used in ruby, and the ASCII typing form. Search treats
  // them as the same tone. Keep in step with UPPER in tools/content_harmonisation.py.
  const toneMarkFold = Object.freeze({'`': 'ˋ', 'ˎ': 'ˋ', 'ꞈ': 'ˆ', 'ˏ': 'ˊ', 'ˍ': 'ˉ'});
  const api = {fold, match, toneMarkFold};
  if (typeof module !== 'undefined') module.exports = api;
  root.TliSiteSearchVariants = api;
})(typeof window !== 'undefined' ? window : globalThis);
