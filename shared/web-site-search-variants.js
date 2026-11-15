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

  // The one matching rule for every public search box (decided 2026-11-15). Folds case,
  // Lomari diacritics, spaces, hyphens and apostrophes, writes each tone in a single form,
  // and maps Hanri variants to one spelling. Tone marks are kept: a query without one finds
  // every tone (`맘` finds `맘ˉ` and `맘ˆ`), a query with one finds only that tone.
  const SEPARATORS = /[\s\-’'‘ʼ]/u;
  function normalise(text, hanriFold) {
    const mapping = hanriFold || {};
    return [...String(text || '').normalize('NFKD').replace(/[̀-ͯ]/gu, '').toLowerCase().normalize('NFC')]
      .filter(char => !SEPARATORS.test(char))
      .map(char => toneMarkFold[char] || mapping[char] || char)
      .join('');
  }

  // The Hanri variant table (Traditional/Simplified and related spellings), shared by every
  // search box. Fetched once per page.
  let hanriFoldRequest = null;
  function loadHanriFold(url) {
    hanriFoldRequest ||= fetch(url || '/public/data/hanri-fold.json', {cache: 'no-cache'})
      .then(response => {
        if (!response.ok) throw new Error(`Hanri fold request failed: ${response.status}`);
        return response.json();
      })
      .then(data => data.hanriFold || {});
    return hanriFoldRequest;
  }
  const api = {fold, match, toneMarkFold, normalise, loadHanriFold};
  if (typeof module !== 'undefined') module.exports = api;
  root.TliSiteSearchVariants = api;
})(typeof window !== 'undefined' ? window : globalThis);
