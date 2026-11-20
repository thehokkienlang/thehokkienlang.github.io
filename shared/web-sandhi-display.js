(function (root) {
  'use strict';
  // Shows song lyrics and song titles with the reader's sandhi (docs/sandhi-toggle-plan.md).
  //
  // Song pages are baked with Taipei sandhi marks. Singapore differs in one step only (open
  // 2 -> 4 where Taipei has 2 -> 1), so its marks are derived from the Taipei ones: an open
  // syllable marked tone 1 that is joined to the next syllable becomes tone 4. Nothing stored
  // changes; the page only swaps the marks it shows (ˆ -> ˊ, ꞈ -> ˏ, Lomari â -> á).
  //
  // "Joined" follows how the pages are written:
  //   - inside one reading (삔아ˆ재), the next syllable follows directly;
  //   - at the end of a lyric reading, the converter writes "-" (겅ˆ-). A reading with no "-"
  //     ends its sandhi group (敢逽 갈ˆ나ˆ, or 開 퀴ˆ before a neutral-tone ’됴);
  //   - a tone-only ruby (꽈 with ꞈ) and title readings carry no "-", so the next character
  //     on the line decides: a syllable directly after it joins, a space or punctuation doesn't;
  //   - in Lomari, a syllable before a single "-" is joined ("--" and ’ precede a neutral tone).
  // Checked syllables (final ㄱ ㄷ ㅂ ㅎ ㅀ; Lomari -p -t -k -h) keep tone 1: their sandhi is
  // 1 <-> 3 in both varieties.

  const UPPER = Object.freeze({'ˆ': 'ˊ', 1: '4'}); // a stored digit reading (팰1세) keeps digits
  const LOWER = Object.freeze({'ꞈ': 'ˏ'});
  const TONE_ONE = new Set(['ˆ', 'ꞈ', '1']);
  const TONE_MARK = /[ˆˋˊˉˇˍˎˏˬꞈ1-5]/u;
  // Checked finals as written, plus ㅈ and ㅊ, which some spellings use for -t and -h.
  const CHECKED_FINALS = new Set(['ᆨ', 'ᆮ', 'ᆸ', 'ᇂ', 'ᆶ', 'ᆽ', 'ᆾ']);
  const SYLLABLE_START = /[가-힣ᄀ-ᅟꥠ-꥿㐀-鿿豈-﫿]|[\u{20000}-\u{3134f}]/u;

  const isFinalJamo = char => /[ᆨ-ᇿퟋ-ퟻ]/u.test(char || '');
  const isVowelJamo = char => /[ᅠ-ᆧힰ-ퟆ]/u.test(char || '');
  const isInitialJamo = char => /[ᄀ-ᅟꥠ-꥿]/u.test(char || '');

  // One written syllable starting at index: a precomposed syllable or an old-Hangul jamo cluster,
  // with any trailing final jamo. Returns {end, final} or null.
  function syllableAt(text, index) {
    const char = text[index];
    if (!char) return null;
    let end = index;
    let final = '';
    const code = char.codePointAt(0);
    if (code >= 0xac00 && code <= 0xd7a3) {
      const finalIndex = (code - 0xac00) % 28;
      final = finalIndex ? String.fromCodePoint(0x11a7 + finalIndex) : '';
      end = index + 1;
    } else if (isInitialJamo(char)) {
      end = index + 1;
      while (isInitialJamo(text[end])) end += 1;
      if (!isVowelJamo(text[end])) return null;
      while (isVowelJamo(text[end])) end += 1;
    } else {
      return null;
    }
    while (isFinalJamo(text[end])) { final = text[end]; end += 1; }
    return {end, final};
  }

  function startsSyllable(text) {
    const first = String(text || '').codePointAt(0);
    return first !== undefined && SYLLABLE_START.test(String.fromCodePoint(first));
  }

  // A Hangul reading as Singapore shows it. joinedAfter says whether whatever follows the text
  // joins its last syllable (used for tone-only rubies, titles and bare text). base is the ruby's
  // base, for a tone-only reading such as "ꞈ" whose syllable is the base itself.
  function singaporeReading(text, {joinedAfter = false, base = ''} = {}) {
    const source = String(text || '');
    if (!/[ˆꞈ1]/u.test(source)) return source;
    const chars = [...source];
    // A tone-only reading: its syllable is the ruby base.
    if (!/[가-힣ᄀ-ᅟꥠ-꥿]/u.test(source)) {
      const unit = syllableAt(String(base || ''), 0);
      const open = unit && !CHECKED_FINALS.has(unit.final);
      if (!open) return source;
      return chars.map((char, index) => {
        if (!TONE_ONE.has(char)) return char;
        const rest = chars.slice(index + 1).join('');
        const joined = rest.trim() === '' ? joinedAfter : /^-(?!-)/u.test(rest);
        return joined ? (UPPER[char] || LOWER[char]) : char;
      }).join('');
    }
    const flat = chars.join('');
    let output = '';
    let index = 0;
    while (index < flat.length) {
      const unit = syllableAt(flat, index);
      if (!unit) { output += flat[index]; index += 1; continue; }
      output += flat.slice(index, unit.end);
      index = unit.end;
      const mark = flat[index];
      if (!TONE_MARK.test(mark || '')) continue;
      index += 1;
      if (!TONE_ONE.has(mark) || CHECKED_FINALS.has(unit.final)) { output += mark; continue; }
      const rest = flat.slice(index);
      const joined = rest === '' ? joinedAfter
        : /^-(?!-)/u.test(rest) || syllableAt(rest, 0) !== null || (rest.trim() === '' && joinedAfter);
      output += joined ? (UPPER[mark] || LOWER[mark]) : mark;
    }
    return output;
  }

  // A Lomari line as Singapore says it: a circumflex (tone 1) on an open syllable before a single
  // hyphen becomes an acute (tone 4). Returns a list of [start, end] ranges of syllables to change,
  // so a caller can edit text that is split across nodes.
  const LOMARI_WORD = /[A-Za-zÀ-ɏḀ-ỿ̀-ͯ᷀-᷿ⁿ]+/gu;
  function lomariRanges(text) {
    const source = String(text || '');
    const ranges = [];
    for (const match of source.matchAll(LOMARI_WORD)) {
      const word = match[0];
      const decomposed = word.normalize('NFD');
      if (!decomposed.includes('̂')) continue;
      const letters = decomposed.replace(/[̀-ͯ᷀-᷿]/gu, '').toLowerCase();
      if (/[hptk]$/u.test(letters)) continue;
      const end = match.index + word.length;
      if (source[end] !== '-' || source[end + 1] === '-') continue;
      ranges.push([match.index, end]);
    }
    return ranges;
  }
  // Tone 1 to tone 4, keeping the text's own form: a precomposed vowel stays precomposed (â -> á),
  // and a separate U+0302 becomes a separate U+0301.
  const toAcute = text => [...String(text)].map(char => char === '̂' ? '́'
    : char.normalize('NFD').includes('̂') ? char.normalize('NFD').replace('̂', '́').normalize('NFC') : char).join('');
  function singaporeLomari(text) {
    const source = String(text || '');
    let output = '';
    let last = 0;
    for (const [start, end] of lomariRanges(source)) {
      output += source.slice(last, start) + toAcute(source.slice(start, end));
      last = end;
    }
    return output + source.slice(last);
  }

  // The indexes where two same-length forms differ: the tone marks that vary by sandhi.
  function variesIndexes(taipei, singapore) {
    const indexes = new Set();
    const a = String(taipei || '');
    const b = String(singapore || '');
    for (let index = 0; index < Math.min(a.length, b.length); index++) if (a[index] !== b[index]) indexes.add(index);
    return indexes;
  }

  // In decomposed text the circumflex is its own character after the vowel, possibly after other
  // marks (the nasal tilde below): the vowel is the last letter at or before index.
  const COMBINING = /[̀-ͯ᷀-᷿]/u;
  function baseLetterBefore(source, index) {
    let at = index;
    while (at > 0 && COMBINING.test(source[at])) at -= 1;
    return at;
  }
  // Whether a Lomari vowel is a capital: its accent sits higher, so the colour cut is higher.
  function toneUpper(cluster) {
    const letter = String.fromCodePoint(String(cluster).codePointAt(0) || 32);
    return letter !== letter.toLowerCase();
  }

  // The end of any marks that follow index (they belong to the same vowel).
  function marksAfter(source, index) {
    let at = index;
    while (at < source.length && COMBINING.test(source[at])) at += 1;
    return at;
  }

  // A Lomari string as parts [{text, varies}]: each vowel whose tone differs by variety is its own
  // part, shown with the circumflex (Taipei) or acute (Singapore).
  function lomariParts(text, singapore = false) {
    const source = String(text || '');
    const parts = [];
    let last = 0;
    for (const [from, to] of lomariRanges(source)) {
      let start = -1;
      for (let index = from; index < to; index++) {
        if (source[index].normalize('NFD').includes('̂')) { start = index; break; }
      }
      if (start < 0) continue;
      const vowelStart = baseLetterBefore(source, start);
      const vowelEnd = marksAfter(source, start + 1);
      const vowel = source.slice(vowelStart, vowelEnd);
      if (vowelStart > last) parts.push({text: source.slice(last, vowelStart), varies: false});
      parts.push({text: singapore ? toAcute(vowel) : vowel, varies: true});
      last = vowelEnd;
    }
    if (last < source.length) parts.push({text: source.slice(last), varies: false});
    return parts;
  }

  const api = {singaporeReading, singaporeLomari, lomariRanges, lomariParts, toneUpper, startsSyllable, variesIndexes};
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
    return;
  }

  // ---- In a page ---------------------------------------------------------------------------
  // Every mark that differs between Taipei and Singapore is coloured (.tli-sandhi-varies) in both
  // modes, so readers can see which tones vary by variety.
  //   - A plain reading (a lyric rt) and a Lomari vowel: the varying character is its own span
  //     with data-sandhi-taipei / data-sandhi-singapore and data-sandhi-kind="mark".
  //   - A title reading, drawn by site.js with positioned marks: the element keeps both whole
  //     forms and data-sandhi-varies (the mark indexes), and is drawn again on a change.
  // site.js copies an rt's attributes and children to the span that replaces it, so all of this
  // survives that.
  const document = root.document;
  const VARIES = 'tli-sandhi-varies';
  const LINES = '.lyric-line, .title-reading, .song-entry-title';
  const LOMARI = '.lyric-lomari, .song-entry-lomari, .home-songbook small';
  // Text in another dialect (a Teochew song's lyrics and title) keeps the marks it is written with.
  const FIXED = '[data-sandhi-fixed]';
  const mode = () => root.TliSandhiPreference?.get?.() === 'singapore' ? 'singapore' : 'taipei';

  // The first character on the line after node, skipping readings (rt) and rp.
  function nextCharacter(node, line) {
    const walker = document.createTreeWalker(line, root.NodeFilter.SHOW_TEXT, {
      acceptNode: text => text.parentElement.closest('rt, rp, .tli-rt')
        ? root.NodeFilter.FILTER_REJECT : root.NodeFilter.FILTER_ACCEPT,
    });
    let text;
    while ((text = walker.nextNode())) {
      if (node.contains(text)) continue;
      if (!(node.compareDocumentPosition(text) & root.Node.DOCUMENT_POSITION_FOLLOWING)) continue;
      if (text.nodeValue.length) return text.nodeValue;
    }
    return '';
  }

  function markSpan(taipei, singapore, singaporeNow) {
    const span = document.createElement('span');
    span.className = VARIES;
    span.dataset.sandhiTaipei = taipei;
    span.dataset.sandhiSingapore = singapore;
    span.dataset.sandhiKind = 'mark';
    span.textContent = singaporeNow ? singapore : taipei;
    return span;
  }

  // A Lomari vowel whose tone varies: its real text is kept (it is what a selection shows and a
  // copy takes) but drawn invisibly; CSS draws two copies of it in the same place, the letter
  // below the accent in the normal colour and the accent above in the accent colour, so nothing
  // overlaps (.tli-lomari-tone in shared/web-site-navigation.css).
  function setToneLayers(span) {
    span.dataset.toneText = span.textContent;
    if (toneUpper(span.textContent)) span.dataset.toneUpper = '';
    else delete span.dataset.toneUpper;
    return span;
  }
  function lomariToneSpan(text) {
    const span = document.createElement('span');
    span.className = 'tli-lomari-tone';
    span.textContent = text;
    return setToneLayers(span);
  }

  // A reading that is plain text: each varying mark becomes a coloured span.
  function wrapMarks(element, taipei, singapore, singaporeNow) {
    const varies = variesIndexes(taipei, singapore);
    const parts = [];
    let plain = '';
    for (let index = 0; index < taipei.length; index++) {
      if (!varies.has(index)) { plain += taipei[index]; continue; }
      if (plain) parts.push(plain);
      plain = '';
      parts.push(markSpan(taipei[index], singapore[index], singaporeNow));
    }
    if (plain) parts.push(plain);
    element.replaceChildren(...parts);
  }

  // A reading drawn by site.js (titles): keep both forms and where the marks vary.
  function remember(element, taipei, singapore, kind, singaporeNow) {
    element.dataset.sandhiTaipei = taipei;
    element.dataset.sandhiSingapore = singapore;
    element.dataset.sandhiKind = kind;
    element.dataset.sandhiVaries = [...variesIndexes(taipei, singapore)].join(',');
    if (singaporeNow) element.textContent = singapore;
  }

  // The varying mark indexes site.js passes to the tone renderers for an element (or none).
  function variesOf(element) {
    const value = element?.dataset?.sandhiVaries;
    return value ? new Set(value.split(',').map(Number)) : null;
  }

  // Hangul readings: run before site.js draws the titles' tone marks and turns ruby into spans,
  // while the "-" join marks are still in the readings.
  function prepare(scope = document) {
    const singaporeNow = mode() === 'singapore';
    scope.querySelectorAll?.(LINES).forEach(line => {
      if (line.closest(FIXED)) return;
      const title = !line.matches('.lyric-line');
      line.querySelectorAll('ruby > rt:not([data-sandhi-kind]):not([data-sandhi-done])').forEach(rt => {
        const ruby = rt.parentElement;
        const base = [...ruby.childNodes].filter(child => child.nodeName !== 'RT' && child.nodeName !== 'RP')
          .map(child => child.textContent).join('');
        const taipei = rt.textContent;
        if (!/[ˆꞈ]/u.test(taipei)) return;
        const toneOnly = !/[가-힣ᄀ-ᅟꥠ-꥿]/u.test(taipei);
        // A lyric reading says where it joins with "-"; a title or tone-only one goes by what follows.
        const joinedAfter = (title || toneOnly) && startsSyllable(nextCharacter(ruby, line));
        const singapore = singaporeReading(taipei, {joinedAfter, base});
        if (singapore === taipei) return;
        if (title && !toneOnly) remember(rt, taipei, singapore, 'title', singaporeNow);
        else { rt.dataset.sandhiDone = ''; wrapMarks(rt, taipei, singapore, singaporeNow); }
      });
      if (!title) return;
      // Bare Hangul in a title (곻ˆ愛…) carries its own marks.
      const walker = document.createTreeWalker(line, root.NodeFilter.SHOW_TEXT, {
        acceptNode: text => text.parentElement.closest('rt, rp, [data-sandhi-kind]')
          ? root.NodeFilter.FILTER_REJECT : root.NodeFilter.FILTER_ACCEPT,
      });
      const texts = [];
      while (walker.nextNode()) texts.push(walker.currentNode);
      texts.forEach(text => {
        if (!/[ˆꞈ]/u.test(text.nodeValue)) return;
        const taipei = text.nodeValue;
        const singapore = singaporeReading(taipei, {joinedAfter: startsSyllable(nextCharacter(text, line))});
        if (singapore === taipei) return;
        const holder = document.createElement('span');
        holder.className = 'tli-sandhi-text';
        text.replaceWith(holder);
        holder.append(text);
        remember(holder, taipei, singapore, 'bare', singaporeNow);
      });
    });
  }

  // The text node and offset holding character index of line's text.
  function locate(line, index) {
    const walker = document.createTreeWalker(line, root.NodeFilter.SHOW_TEXT);
    let offset = 0;
    let text;
    while ((text = walker.nextNode())) {
      if (index < offset + text.nodeValue.length) return {text, at: index - offset};
      offset += text.nodeValue.length;
    }
    return null;
  }

  // Lomari is plain text, but on the song list site.js redraws it with the title (each row is a
  // .title-reading link), so this runs after the titles are drawn. The vowel carrying a varying
  // tone (with its circumflex) becomes a coloured span.
  function prepareLomari(scope = document) {
    const singaporeNow = mode() === 'singapore';
    scope.querySelectorAll?.(LOMARI).forEach(line => {
      if (line.closest(FIXED) || line.dataset.sandhiDone !== undefined) return;
      line.dataset.sandhiDone = '';
      const source = line.textContent;
      // Last first, so splitting a text node never moves an earlier vowel.
      for (const [from, to] of lomariRanges(source).reverse()) {
        let start = -1;
        for (let index = from; index < to; index++) {
          if (source[index].normalize('NFD').includes('̂')) { start = index; break; }
        }
        if (start < 0) continue;
        const vowelStart = baseLetterBefore(source, start);
        const length = marksAfter(source, start + 1) - vowelStart;
        const found = locate(line, vowelStart);
        if (!found || found.at + length > found.text.nodeValue.length) continue;
        const middle = found.text.splitText(found.at);
        middle.splitText(length);
        const taipei = middle.nodeValue;
        const span = markSpan(taipei, toAcute(taipei), singaporeNow);
        span.className = 'tli-lomari-tone';
        middle.replaceWith(setToneLayers(span));
      }
    });
  }

  // On a change: show one sandhi or the other. Title readings are drawn with positioned marks,
  // so they are drawn again.
  function show(next = mode()) {
    const core = root.TangliengimImeCore;
    document.querySelectorAll('[data-sandhi-kind]').forEach(element => {
      const text = next === 'singapore' ? element.dataset.sandhiSingapore : element.dataset.sandhiTaipei;
      const kind = element.dataset.sandhiKind;
      if (kind === 'title' && core?.renderInlineUpperToneReading) element.replaceChildren(core.renderInlineUpperToneReading(text, variesOf(element)));
      else if (kind === 'bare' && core?.renderToneMarkedReading) element.replaceChildren(core.renderToneMarkedReading(text, variesOf(element)));
      else {
        element.textContent = text;
        if (element.classList.contains('tli-lomari-tone')) setToneLayers(element);
      }
    });
  }

  root.TliSandhiDisplay = {...api, prepare, prepareLomari, show, variesOf, lomariToneSpan};
  root.TliSandhiPreference?.onChange?.(next => show(next));
})(typeof window !== 'undefined' ? window : globalThis);
