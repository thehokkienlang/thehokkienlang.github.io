const TangliengimImeCore = (() => {
  const HANGUL_TONE_MARKS = {
    1: "ꞈ",
    "ˆ": "ꞈ",
    "ꞈ": "ꞈ",
    2: "ˎ",
    "ˋ": "ˎ",
    "`": "ˎ",
    "ˎ": "ˎ",
    4: "ˏ",
    "ˊ": "ˏ",
    "ˏ": "ˏ",
    5: "ˍ",
    "ˉ": "ˍ",
    "ˍ": "ˍ",
  };

  const UPPER_HANGUL_TONE_MARKS = {
    1: "ˆ",
    "ˆ": "ˆ",
    "ꞈ": "ˆ",
    2: "ˋ",
    "ˋ": "ˋ",
    "`": "ˋ",
    "ˎ": "ˋ",
    3: "",
    4: "ˊ",
    "ˊ": "ˊ",
    "ˏ": "ˊ",
    5: "ˉ",
    "ˉ": "ˉ",
    "ˍ": "ˉ",
  };

  const HANGUL_TONE_CHARS = new Set([...Object.keys(HANGUL_TONE_MARKS), "3"]);
  const INPUT_TONE_DIGITS = Object.freeze({
    1: "1", "ˆ": "1", "ꞈ": "1",
    2: "2", "ˋ": "2", "`": "2", "ˎ": "2",
    3: "3",
    4: "4", "ˊ": "4", "ˏ": "4",
    5: "5", "ˉ": "5", "ˍ": "5",
  });
  const CHECKED_FINAL_JAMO = new Set(["ᆨ", "ᆮ", "ᆸ", "ᇂ", "ᆶ", "ᆽ", "ᆾ"]);
  const OPEN_TAIPEI_SANDHI = Object.freeze({ 1: "5", 2: "1", 3: "2", 4: "3", 5: "3" });
  const CHECKED_TAIPEI_SANDHI = Object.freeze({ 1: "3", 3: "1" });
  const LATIN_WIDTH_APOSTROPHES = new Set(["’", "‘"]);
  const AMERICAN_TO_BRITISH_ENGLISH = Object.freeze({
    airplane: "aeroplane",
    airplanes: "aeroplanes",
    apologize: "apologise",
    apologized: "apologised",
    apologizes: "apologises",
    apologizing: "apologising",
    behavior: "behaviour",
    behaviors: "behaviours",
    center: "centre",
    centers: "centres",
    color: "colour",
    colored: "coloured",
    coloring: "colouring",
    colors: "colours",
    favor: "favour",
    favorable: "favourable",
    favored: "favoured",
    favoring: "favouring",
    favors: "favours",
    gray: "grey",
    harbor: "harbour",
    harbors: "harbours",
    honor: "honour",
    honorable: "honourable",
    honors: "honours",
    kilometer: "kilometre",
    kilometers: "kilometres",
    labor: "labour",
    labors: "labours",
    neighbor: "neighbour",
    neighbors: "neighbours",
    organization: "organisation",
    organizations: "organisations",
    organize: "organise",
    organized: "organised",
    organizes: "organises",
    organizing: "organising",
    rancor: "rancour",
    realize: "realise",
    realized: "realised",
    realizes: "realises",
    realizing: "realising",
    realization: "realisation",
    realizations: "realisations",
    recognize: "recognise",
    recognized: "recognised",
    recognizes: "recognises",
    recognizing: "recognising",
    romanization: "romanisation",
    shriveled: "shrivelled",
    socialize: "socialise",
    socialized: "socialised",
    socializes: "socialises",
    socializing: "socialising",
    theater: "theatre",
    theaters: "theatres",
    traveler: "traveller",
    travelers: "travellers",
    traveling: "travelling",
  });

  function normalizeApostrophes(value) {
    return String(value ?? "").replaceAll("'", "’");
  }

  function normalizeText(value) {
    return normalizeApostrophes(value)
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^\p{Letter}\p{Number}\u1100-\u11FF\u3130-\u318F\u3400-\u4DBF\u4E00-\u9FFF\u{20000}-\u{2EBEF}]+/gu, "")
      .toLowerCase();
  }

  function normalizeEnglishSearch(value) {
    const british = String(value || "").replace(/[A-Za-z]+/g, (word) =>
      AMERICAN_TO_BRITISH_ENGLISH[word.toLowerCase()] || word
    );
    return normalizeText(british);
  }

  function normalizeNasalAlias(value, nasalMarker) {
    let output = "";
    let canMarkPrevious = false;
    for (const char of [...String(value || "").normalize("NFKD").toLowerCase()]) {
      if (char === "\u0330" || char === "~") {
        if (canMarkPrevious && !output.endsWith(nasalMarker)) {
          output += nasalMarker;
        }
      } else if (/[\u0300-\u036f]/u.test(char)) {
        continue;
      } else if (/[\p{Letter}\p{Number}\u1100-\u11FF\u3130-\u318F\u3400-\u4DBF\u4E00-\u9FFF\u{20000}-\u{2EBEF}]/u.test(char)) {
        output += char;
        canMarkPrevious = true;
      } else {
        canMarkPrevious = false;
      }
    }
    return output;
  }

  function normalizeLomariSearchAliases(value) {
    const aliases = new Set([
      normalizeText(value),
      normalizeNasalAlias(value, "l"),
      normalizeNasalAlias(value, "~"),
    ].filter(Boolean));
    return [...aliases].join(" ");
  }

  function queryVariants(rawQuery) {
    const variants = new Set([
      normalizeText(rawQuery),
      normalizeEnglishSearch(rawQuery),
      normalizeNasalAlias(rawQuery, "l"),
      normalizeNasalAlias(rawQuery, "~"),
    ].filter(Boolean));

    if (String(rawQuery || "").includes("~")) {
      variants.delete(normalizeText(rawQuery));
    }

    return [...variants];
  }

  function searchableEntry(entry) {
    return entry.active && entry.kind !== "numeric_override";
  }

  function isToneMark(char) {
    return HANGUL_TONE_CHARS.has(char);
  }

  function inputToneDigit(char) {
    return INPUT_TONE_DIGITS[char] || "";
  }

  function displayTextNode(text) {
    const fragment = document.createDocumentFragment();
    for (const char of [...normalizeApostrophes(text)]) {
      if (LATIN_WIDTH_APOSTROPHES.has(char)) {
        const span = document.createElement("span");
        span.className = "latin-apostrophe";
        span.textContent = char;
        fragment.append(span);
      } else {
        fragment.append(document.createTextNode(char));
      }
    }
    return fragment;
  }

  function isPrecomposedHangul(char) {
    if (!char) return false;
    const code = char.codePointAt(0);
    return code >= 0xac00 && code <= 0xd7a3;
  }

  function isInitialJamo(char) {
    if (!char) return false;
    const code = char.codePointAt(0);
    return (code >= 0x1100 && code <= 0x1112) || char === "ᅙ";
  }

  function isVowelJamo(char) {
    if (!char) return false;
    const code = char.codePointAt(0);
    return (code >= 0x1161 && code <= 0x1175) || char === "ᅷ" || char === "ᆤ" || char === "ힻ";
  }

  function isFinalJamo(char) {
    if (!char || isVowelJamo(char)) return false;
    const code = char.codePointAt(0);
    return code >= 0x11a8 && code <= 0x11ff;
  }

  function hangulFinalJamo(unit) {
    const text = String(unit || "");
    const code = text.codePointAt(0);
    if (text.length === 1 && code >= 0xac00 && code <= 0xd7a3) {
      const finalIndex = (code - 0xac00) % 28;
      return finalIndex ? String.fromCodePoint(0x11a7 + finalIndex) : "";
    }
    const final = text.at(-1);
    return isFinalJamo(final) ? final : "";
  }

  function citationToTaipeiSandhiTone(unit, tone) {
    const value = String(tone || "3");
    const table = isCheckedFinalUnit(unit)
      ? CHECKED_TAIPEI_SANDHI
      : OPEN_TAIPEI_SANDHI;
    return table[value] || value;
  }

  function isCheckedFinalUnit(unit) {
    return CHECKED_FINAL_JAMO.has(hangulFinalJamo(unit));
  }

  function singaporeTone1AudioReplacement(nextUnit, nextTone, nextIsCitationFinal = false) {
    if (nextIsCitationFinal) return "4";
    const tone = String(nextTone || "3");
    if (isCheckedFinalUnit(nextUnit)) {
      if (tone === "1") return "4";
      if (tone === "3") return "5";
      return "1";
    }
    if (["3", "5"].includes(tone)) return "4";
    if (["1", "2", "4"].includes(tone)) return "5";
    return "1";
  }

  function codePointAtInfo(text, index) {
    const code = text.codePointAt(index);
    if (code === undefined) return null;
    const char = String.fromCodePoint(code);
    return { char, code, end: index + char.length };
  }

  function isHanriChar(char) {
    const code = char?.codePointAt(0);
    if (code === undefined) return false;
    return (
      (code >= 0x3400 && code <= 0x4dbf) ||
      (code >= 0x4e00 && code <= 0x9fff) ||
      (code >= 0x20000 && code <= 0x2ebef)
    );
  }

  function readingUnitAt(text, index) {
    const char = text[index];
    if (!char) return null;

    if (isPrecomposedHangul(char)) {
      return { text: char, end: index + 1, canCarryTone: true };
    }

    if (isInitialJamo(char) && isVowelJamo(text[index + 1])) {
      let end = index + 2;
      if (isFinalJamo(text[end])) {
        end += 1;
      }
      return { text: text.slice(index, end), end, canCarryTone: true };
    }

    return { text: char, end: index + 1, canCarryTone: false };
  }

  function headwordUnitAt(text, index) {
    const hangulUnit = readingUnitAt(text, index);
    if (hangulUnit?.canCarryTone) {
      const tone = text[hangulUnit.end];
      const end = isToneMark(tone) ? hangulUnit.end + 1 : hangulUnit.end;
      return {
        kind: "hangul",
        text: hangulUnit.text,
        raw: text.slice(index, end),
        end,
      };
    }

    const first = codePointAtInfo(text, index);
    if (!first) return null;

    if (isHanriChar(first.char)) {
      let end = first.end;
      while (end < text.length) {
        const next = codePointAtInfo(text, end);
        if (!next || !isHanriChar(next.char)) break;
        end = next.end;
      }
      return { kind: "hanri", text: text.slice(index, end), end };
    }

    return { kind: "literal", text: first.char, end: first.end };
  }

  function readingUnitToneEnd(text, unit) {
    const tone = text[unit.end];
    return unit.canCarryTone && isToneMark(tone) ? unit.end + 1 : unit.end;
  }

  function tonedHangulNode(unit, tone) {
    const mark = HANGUL_TONE_MARKS[tone];
    if (!mark) {
      return document.createTextNode(unit);
    }

    const ruby = document.createElement("ruby");
    ruby.className = "hangul-tone";
    ruby.setAttribute("aria-label", `${unit}${tone}`);
    ruby.append(document.createTextNode(unit));

    const rt = document.createElement("rt");
    rt.textContent = mark;
    ruby.append(rt);
    return ruby;
  }

  function renderToneMarkedReading(reading) {
    const fragment = document.createDocumentFragment();
    const text = normalizeApostrophes(reading);
    let index = 0;

    while (index < text.length) {
      const unit = readingUnitAt(text, index);
      if (!unit) break;

      const tone = text[unit.end];
      if (unit.canCarryTone && isToneMark(tone)) {
        fragment.append(tonedHangulNode(unit.text, tone));
        index = unit.end + 1;
      } else {
        fragment.append(displayTextNode(unit.text));
        index = unit.end;
      }
    }

    return fragment;
  }

  function renderInlineUpperToneReading(reading) {
    const fragment = document.createDocumentFragment();
    const text = normalizeApostrophes(reading);
    let index = 0;

    while (index < text.length) {
      const unit = readingUnitAt(text, index);
      if (!unit) break;

      const tone = text[unit.end];
      if (unit.canCarryTone) {
        const unitNode = document.createElement("span");
        unitNode.className = "hangul-reading-unit";
        unitNode.textContent = unit.text;
        fragment.append(unitNode);
      } else {
        fragment.append(displayTextNode(unit.text));
      }
      if (unit.canCarryTone && isToneMark(tone)) {
        const mark = UPPER_HANGUL_TONE_MARKS[tone] || "";
        if (mark) {
          const toneNode = document.createElement("span");
          toneNode.className = "inline-upper-tone";
          toneNode.textContent = mark;
          fragment.append(toneNode);
        }
        index = unit.end + 1;
      } else {
        index = unit.end;
      }
    }

    return fragment;
  }

  function buildReadingCandidateMap(entries) {
    const byReading = new Map();
    for (const entry of entries.filter(searchableEntry)) {
      const readingKeys = [
        entry.readingBase,
        entry.reading,
        entry.raw?.reading,
      ].map((value) => normalizeText(TangliengimHangulIme.normalizeReadingBase(value)));

      for (const key of new Set(readingKeys.filter(Boolean))) {
        if (!byReading.has(key)) byReading.set(key, []);
        byReading.get(key).push(entry);
      }
    }

    for (const candidates of byReading.values()) {
      candidates.sort((a, b) =>
        a.priority - b.priority || a.row - b.row || a.hanri.localeCompare(b.hanri)
      );
    }
    return byReading;
  }

  function tonesByBasePosition(reading) {
    const base = [];
    const tones = new Map();
    const normalized = TangliengimHangulIme.normalizeReadingToneKey(String(reading || ""));

    for (const char of normalized) {
      if ("12345".includes(char)) {
        if (base.length) tones.set(base.length - 1, char);
        continue;
      }
      if (char === "*") continue;
      base.push(char);
    }

    return { base: base.join(""), tones };
  }

  function typedTonesAreCompatibleWithEntry(typedForm, entryReading) {
    const typed = tonesByBasePosition(typedForm);
    const entry = tonesByBasePosition(entryReading);
    if (normalizeText(typed.base) !== normalizeText(entry.base)) return false;
    if (!typed.tones.size) return true;

    for (const [position, tone] of typed.tones) {
      if (entry.tones.get(position) !== tone) return false;
    }
    return true;
  }

  function filterCandidateEntries(typedForm, entries) {
    const candidates = entries || [];
    const typed = tonesByBasePosition(typedForm);
    if (!typed.tones.size) {
      return candidates.filter((entry) => !entry.autoSandhi);
    }

    const compatible = candidates.filter((entry) =>
      typedTonesAreCompatibleWithEntry(typedForm, entry.reading || entry.readingBase)
    );
    if (compatible.length) return compatible;

    // A TSV row may deliberately omit tone digits. Keep that desktop fallback
    // available when typed tones do not distinguish a stored reading.
    return candidates.filter((entry) =>
      !entry.autoSandhi &&
      normalizeText(TangliengimHangulIme.normalizeReadingBase(entry.reading || entry.readingBase)) ===
        normalizeText(typed.base)
    );
  }

  function createDictionaryIndex(entries) {
    const activeEntries = (entries || []).filter(searchableEntry);
    const hanriEntries = activeEntries
      .filter((entry) => entry.hanri && entry.kind !== "hangul_override")
      .sort((a, b) =>
        [...b.hanri].length - [...a.hanri].length ||
        a.priority - b.priority ||
        a.row - b.row
      );
    const mixedHanriEntries = hanriEntries.filter((entry) => entry.kind === "mixed_hanri");
    const plainHanriByFirst = new Map();
    const exactReadingEntries = new Map();
    const hangulOverrides = new Map();
    const hangulOverrideKeys = [];
    const hanriMatchCache = new Map();

    for (const entry of hanriEntries) {
      if (entry.kind !== "plain_hanri") continue;
      const first = String.fromCodePoint(entry.hanri.codePointAt(0));
      if (!plainHanriByFirst.has(first)) plainHanriByFirst.set(first, []);
      plainHanriByFirst.get(first).push(entry);
    }

    function addExactReading(key, entry) {
      if (!key || !/[1245ˆˋ`ˊˉꞈˎˏˍ]/u.test(key)) return;
      const normalized = TangliengimHangulIme.normalizeReadingToneKey(key);
      if (!exactReadingEntries.has(normalized)) exactReadingEntries.set(normalized, []);
      exactReadingEntries.get(normalized).push(entry);
    }

    for (const entry of activeEntries) {
      addExactReading(entry.reading, entry);
      addExactReading(entry.raw?.reading, entry);
      if (entry.kind !== "hangul_override") continue;
      const visibleKey = TangliengimHangulIme.normalizeReadingBase(entry.readingBase).normalize("NFC");
      const key = normalizeText(visibleKey);
      if (key && !hangulOverrides.has(key)) {
        hangulOverrides.set(key, entry);
        hangulOverrideKeys.push(visibleKey);
      }
    }

    hangulOverrideKeys.sort((a, b) => [...b].length - [...a].length || b.length - a.length);
    for (const candidates of exactReadingEntries.values()) {
      candidates.sort((a, b) => a.priority - b.priority || a.row - b.row);
    }

    function compareScore(left, right) {
      for (let index = 0; index < left.length; index += 1) {
        if (left[index] !== right[index]) return left[index] - right[index];
      }
      return 0;
    }

    function priorityHanriMatch(text, index, maximumEnd = text.length) {
      const cacheKey = `${text}\u0000${index}\u0000${maximumEnd}`;
      if (hanriMatchCache.has(cacheKey)) return hanriMatchCache.get(cacheKey);

      let runEnd = index;
      while (runEnd < text.length) {
        const char = String.fromCodePoint(text.codePointAt(runEnd));
        if (!isHanriChar(char)) break;
        runEnd += char.length;
      }

      runEnd = Math.min(runEnd, maximumEnd);
      const memo = new Map();
      function bestAt(position) {
        if (position >= runEnd) return { score: [0, 0, 0], first: null };
        if (memo.has(position)) return memo.get(position);

        let best = { score: [1_000_000, 1_000_000, 1_000_000], first: null };
        const currentChar = String.fromCodePoint(text.codePointAt(position));
        for (const entry of plainHanriByFirst.get(currentChar) || []) {
          const key = String(entry.hanri || "");
          if (!key || !text.startsWith(key, position) || position + key.length > runEnd) continue;
          const rest = bestAt(position + key.length);
          const candidate = {
            score: [rest.score[0], Number(entry.priority) + rest.score[1], 1 + rest.score[2]],
            first: entry,
          };
          if (compareScore(candidate.score, best.score) < 0) best = candidate;
        }

        const char = String.fromCodePoint(text.codePointAt(position));
        const rest = bestAt(position + char.length);
        const unmatched = {
          score: [1 + rest.score[0], 9999 + rest.score[1], 1 + rest.score[2]],
          first: null,
        };
        if (compareScore(unmatched.score, best.score) < 0) best = unmatched;
        memo.set(position, best);
        return best;
      }

      const match = bestAt(index).first;
      if (hanriMatchCache.size > 3000) hanriMatchCache.clear();
      hanriMatchCache.set(cacheKey, match);
      return match;
    }

    function findHanriEntry(text, index = 0, maximumEnd = text.length) {
      for (const entry of mixedHanriEntries) {
        if (text.startsWith(entry.hanri, index) && index + entry.hanri.length <= maximumEnd) return entry;
      }
      const code = text.codePointAt(index);
      const char = code === undefined ? "" : String.fromCodePoint(code);
      return isHanriChar(char) ? priorityHanriMatch(text, index, maximumEnd) : null;
    }

    function findHangulOverride(reading) {
      const key = normalizeText(TangliengimHangulIme.normalizeReadingBase(reading));
      return hangulOverrides.get(key) || null;
    }

    function findReadingEntry(reading) {
      const exactKey = TangliengimHangulIme.normalizeReadingToneKey(reading);
      if (/[1245]/u.test(exactKey)) {
        const exact = exactReadingEntries.get(exactKey)?.[0];
        if (exact) return exact;
      }
      return findHangulOverride(reading);
    }

    function findHangulOverrideAt(text, index = 0, maximumEnd = text.length) {
      for (const key of hangulOverrideKeys) {
        if (!text.startsWith(key, index) || index + key.length > maximumEnd) continue;
        const normalized = normalizeText(key);
        let end = index + key.length;
        while (end < text.length && isToneMark(text[end])) end += 1;
        return { entry: hangulOverrides.get(normalized), end };
      }
      return null;
    }

    return {
      entries: activeEntries,
      candidatesByReading: buildReadingCandidateMap(activeEntries),
      findHanriEntry,
      findHangulOverride,
      findHangulOverrideAt,
      findReadingEntry,
    };
  }

  function isImeCandidateChar(char) {
    if (!char) return false;
    return /[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7A3ˆˋ`ˊˉꞈˎˏˍ12345]/u.test(char);
  }

  function textControlCaretPosition(control) {
    if (!document.body || typeof getComputedStyle !== "function") return null;
    const style = getComputedStyle(control);
    const mirror = document.createElement("div");
    const properties = [
      "boxSizing", "fontFamily", "fontSize", "fontWeight", "fontStyle", "letterSpacing", "lineHeight",
      "textTransform", "textIndent", "paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
      "borderTopWidth", "borderRightWidth", "borderBottomWidth", "borderLeftWidth",
    ];
    mirror.style.position = "fixed";
    mirror.style.visibility = "hidden";
    mirror.style.pointerEvents = "none";
    mirror.style.whiteSpace = "pre-wrap";
    mirror.style.overflowWrap = "break-word";
    mirror.style.width = `${control.offsetWidth}px`;
    for (const property of properties) mirror.style[property] = style[property];
    const cursor = control.selectionStart ?? 0;
    mirror.textContent = control.value.slice(0, cursor);
    const marker = document.createElement("span");
    marker.textContent = control.value.slice(cursor, cursor + 1) || "\u200b";
    mirror.append(marker);
    document.body.append(mirror);
    const position = {
      left: marker.offsetLeft - control.scrollLeft,
      top: marker.offsetTop - control.scrollTop,
      height: Number.parseFloat(style.lineHeight) || Number.parseFloat(style.fontSize) * 1.4,
    };
    mirror.remove();
    return position;
  }

  function createCandidatePopupPositioner({
    control,
    container,
    boundary = control.parentElement || control,
    placement = "below",
    gap = 4,
    padding = 8,
  }) {
    let scheduled = false;

    function position() {
      scheduled = false;
      if (!container || container.hidden || !container.children.length) return;
      const boundaryWidth = Number(boundary?.clientWidth) || Number(control.offsetWidth) || 0;
      const maximumLeft = Math.max(padding, boundaryWidth - (Number(container.offsetWidth) || 0) - padding);

      if (placement !== "caret") {
        const left = Number(control.offsetLeft) || 0;
        const top = (Number(control.offsetTop) || 0) + (Number(control.offsetHeight) || 0) + gap;
        container.style.left = `${Math.max(0, Math.min(left, maximumLeft))}px`;
        container.style.top = `${top}px`;
        return;
      }

      const caret = textControlCaretPosition(control);
      if (!caret) return;
      container.style.left = `${Math.max(padding, Math.min(caret.left, maximumLeft))}px`;
      let top = caret.top + caret.height + gap;
      if (
        top + (Number(container.offsetHeight) || 0) > (Number(control.clientHeight) || 0) &&
        caret.top > (Number(container.offsetHeight) || 0) + padding
      ) {
        top = caret.top - (Number(container.offsetHeight) || 0) - gap;
      }
      container.style.top = `${Math.max(gap, top)}px`;
    }

    function schedule() {
      if (scheduled) return;
      scheduled = true;
      const enqueue = typeof window.requestAnimationFrame === "function"
        ? window.requestAnimationFrame.bind(window)
        : (callback) => window.setTimeout(callback, 0);
      enqueue(position);
    }

    control.addEventListener("scroll", schedule);
    control.addEventListener("click", schedule);
    if (typeof window.addEventListener === "function") window.addEventListener("resize", schedule);
    return { position, schedule };
  }

  class TextImeController {
    constructor({
      control,
      candidateContainer,
      entries = [],
      dictionaryIndex = null,
      enabled = () => true,
      onUpdate = () => {},
      onCandidatesChanged = () => {},
      enterBehavior = "none",
      candidateLimit = 9,
    }) {
      this.control = control;
      this.candidateContainer = candidateContainer;
      this.enabled = enabled;
      this.onUpdate = onUpdate;
      this.onCandidatesChanged = onCandidatesChanged;
      this.enterBehavior = enterBehavior;
      this.candidateLimit = candidateLimit;
      this.dictionaryIndex = dictionaryIndex;
      this.candidatesByReading = dictionaryIndex?.candidatesByReading || buildReadingCandidateMap(entries);
      this.composer = new TangliengimHangulIme.Composer({
        shouldAutocorrectEToYe: (reading) => {
          const key = normalizeText(TangliengimHangulIme.normalizeReadingBase(reading));
          return Boolean(this.candidatesByReading.get(key)?.length);
        },
      });
      this.activeCandidates = [];
      this.activeCandidateIndex = 0;
      this.dismissedCandidateContext = null;
      this.internalUpdate = false;
      this.rememberedHanriReadings = [];
      this.rememberedHangulReadings = [];
      this.rememberedTextSnapshot = normalizeApostrophes(control.value || "");

      this.handleKeydown = this.handleKeydown.bind(this);
      this.handleBeforeInput = this.handleBeforeInput.bind(this);
      this.handleInput = this.handleInput.bind(this);
      this.handleCursorChange = this.handleCursorChange.bind(this);

      control.addEventListener("keydown", this.handleKeydown);
      control.addEventListener("beforeinput", this.handleBeforeInput);
      control.addEventListener("input", this.handleInput);
      control.addEventListener("click", this.handleCursorChange);
      control.addEventListener("keyup", this.handleCursorChange);
      this.renderCandidates();
    }

    isEnabled() {
      return Boolean(this.enabled());
    }

    setEntries(entries, dictionaryIndex = null) {
      this.dictionaryIndex = dictionaryIndex;
      this.candidatesByReading = dictionaryIndex?.candidatesByReading || buildReadingCandidateMap(entries || []);
      this.renderCandidates();
    }

    setEnabled() {
      this.syncComposerFromControl();
      this.renderCandidates();
    }

    clear() {
      this.composer.setText("", 0);
      this.updateControlFromComposer();
      this.control.focus();
    }

    syncRememberedReadings(nextText = this.control.value) {
      const current = normalizeApostrophes(nextText || "");
      const previous = this.rememberedTextSnapshot;
      if (current === previous) return;
      if (!this.rememberedHanriReadings.length && !this.rememberedHangulReadings.length) {
        this.rememberedTextSnapshot = current;
        return;
      }

      let prefix = 0;
      while (prefix < previous.length && prefix < current.length && previous[prefix] === current[prefix]) {
        prefix += 1;
      }
      let suffix = 0;
      while (
        suffix < previous.length - prefix &&
        suffix < current.length - prefix &&
        previous[previous.length - 1 - suffix] === current[current.length - 1 - suffix]
      ) {
        suffix += 1;
      }

      const previousChangeEnd = previous.length - suffix;
      const currentChangeEnd = current.length - suffix;
      const offset = currentChangeEnd - previousChangeEnd;
      const updateSpans = (spans, textKey) => {
        const updated = [];
        for (const span of spans) {
          let start = span.start;
          let end = span.end;
          if (end <= prefix) {
            // The edit follows this remembered span.
          } else if (start >= previousChangeEnd) {
            start += offset;
            end += offset;
          } else {
            continue;
          }
          if (current.slice(start, end) !== span[textKey]) continue;
          updated.push({ ...span, start, end });
        }
        return updated;
      };
      this.rememberedHanriReadings = updateSpans(this.rememberedHanriReadings, "hanri");
      this.rememberedHangulReadings = updateSpans(this.rememberedHangulReadings, "hangul");
      this.rememberedTextSnapshot = current;
    }

    syncRememberedHanriReadings(nextText = this.control.value) {
      this.syncRememberedReadings(nextText);
    }

    rememberHanriReading(start, entry, text = this.composer.text()) {
      const hanri = String(entry?.hanri || "");
      const reading = String(entry?.reading || "");
      if (!hanri || !reading) return;
      this.syncRememberedReadings(text);
      const end = start + hanri.length;
      if (text.slice(start, end) !== hanri) return;
      this.rememberedHanriReadings = this.rememberedHanriReadings.filter(
        (span) => span.end <= start || span.start >= end
      );
      this.rememberedHanriReadings.push({ start, end, hanri, reading, entry });
      this.rememberedHanriReadings.sort((left, right) => left.start - right.start || left.end - right.end);
      this.rememberedTextSnapshot = text;
    }

    rememberHangulReading(start, end, reading, entry, text = this.composer.text(), explicit = false) {
      const hangul = text.slice(start, end);
      const normalizedReading = TangliengimHangulIme.normalizeReadingToneKey(String(reading || ""));
      if (!hangul || !normalizedReading || TangliengimHangulIme.normalizeReadingBase(normalizedReading) !== hangul) return;
      this.syncRememberedReadings(text);
      this.rememberedHangulReadings = this.rememberedHangulReadings.filter(
        (span) => span.end <= start || span.start >= end
      );
      this.rememberedHangulReadings.push({
        start,
        end,
        hangul,
        reading: normalizedReading,
        entry: entry || {
          hanri: hangul,
          reading: normalizedReading,
          readingBase: hangul,
          kind: "hangul_override",
        },
        explicit: Boolean(explicit),
      });
      this.rememberedHangulReadings.sort((left, right) => left.start - right.start || left.end - right.end);
      this.rememberedTextSnapshot = text;
    }

    findRememberedHanriEntry(text, index) {
      this.syncRememberedReadings(text);
      const span = this.rememberedHanriReadings.find(
        (item) => item.start === index && text.slice(item.start, item.end) === item.hanri
      );
      return span?.entry || null;
    }

    nextRememberedHanriStart(text, index) {
      this.syncRememberedReadings(text);
      return this.rememberedHanriReadings.find((span) => span.start > index)?.start ?? text.length;
    }

    getRememberedHanriReadings(text = this.control.value) {
      this.syncRememberedReadings(text);
      return this.rememberedHanriReadings.map(({ start, end, hanri, reading, entry }) => ({
        start,
        end,
        hanri,
        reading,
        autoSandhi: Boolean(entry?.autoSandhi),
      }));
    }

    findRememberedHangulEntryAt(text, index) {
      this.syncRememberedReadings(text);
      const span = this.rememberedHangulReadings.find(
        (item) => item.start === index && text.slice(item.start, item.end) === item.hangul
      );
      // Remembered Hangul carries the user's displayed tones, not a fresh citation reading.
      return span ? { entry: span.entry, end: span.end, preserveTones: true } : null;
    }

    nextRememberedHangulStart(text, index) {
      this.syncRememberedReadings(text);
      return this.rememberedHangulReadings.find((span) => span.start > index)?.start ?? text.length;
    }

    getRememberedHangulReadings(text = this.control.value) {
      this.syncRememberedReadings(text);
      return this.rememberedHangulReadings.map(({ start, end, hangul, reading, explicit }) => ({
        start,
        end,
        hangul,
        reading,
        explicit: Boolean(explicit),
      }));
    }

    previousHangulUnit(text, cursor) {
      let index = 0;
      let previous = null;
      while (index < cursor) {
        const unit = readingUnitAt(text, index);
        if (!unit) break;
        if (unit.end > cursor) break;
        if (unit.canCarryTone) previous = { ...unit, start: index };
        else previous = null;
        index = unit.end;
      }
      return previous?.end === cursor ? previous : null;
    }

    applyHiddenTone(char) {
      const digit = inputToneDigit(char);
      if (!digit) return false;
      this.composer.commit();
      const text = this.composer.text();
      const cursor = this.composer.displayCursorPos();
      const unit = this.previousHangulUnit(text, cursor);
      if (!unit) return false;
      this.rememberHangulReading(
        unit.start,
        unit.end,
        `${unit.text}${digit}`,
        null,
        text,
        true
      );
      return true;
    }

    removePreviousHiddenTone() {
      this.composer.commit();
      const text = this.composer.text();
      const cursor = this.composer.displayCursorPos();
      const unit = this.previousHangulUnit(text, cursor);
      if (!unit) return false;
      const index = this.rememberedHangulReadings.findIndex(
        (span) => span.explicit && span.start === unit.start && span.end === unit.end
      );
      if (index < 0) return false;
      this.rememberedHangulReadings.splice(index, 1);
      this.rememberedTextSnapshot = text;
      return true;
    }

    insertText(text) {
      this.syncComposerFromControl();
      this.replaceSelectionBeforeImeKey();
      for (const char of [...normalizeApostrophes(text)]) {
        if (!this.applyHiddenTone(char)) this.composer.processChar(char);
      }
      this.updateControlFromComposer();
      this.control.focus();
    }

    backspace() {
      this.syncComposerFromControl();
      this.replaceSelectionBeforeImeKey();
      if (!this.removePreviousHiddenTone()) this.composer.backspace();
      this.updateControlFromComposer();
      this.control.focus();
    }

    syncComposerFromControl() {
      const text = this.composer.text();
      const normalizedValue = normalizeApostrophes(this.control.value);
      if (normalizedValue !== this.control.value) {
        this.control.value = normalizedValue;
      }
      const cursor = this.control.selectionStart ?? this.control.value.length;
      const selectionEnd = this.control.selectionEnd ?? cursor;

      if (normalizedValue !== text || cursor !== selectionEnd) {
        this.composer.setText(normalizedValue, cursor);
        return;
      }

      if (cursor !== this.composer.displayCursorPos()) {
        this.composer.commit();
        this.composer.cursorPos = TangliengimHangulIme.normalizeAtomicSelection(
          this.composer.output,
          cursor,
          cursor
        )[0];
        this.composer.keyHistory = [];
      }
    }

    normalizeControlSelection() {
      const start = this.control.selectionStart ?? this.control.value.length;
      const end = this.control.selectionEnd ?? start;
      const [normalizedStart, normalizedEnd] = TangliengimHangulIme.normalizeAtomicSelection(
        this.control.value,
        start,
        end
      );
      if (normalizedStart !== start || normalizedEnd !== end) {
        this.control.setSelectionRange(normalizedStart, normalizedEnd);
      }
      return [normalizedStart, normalizedEnd];
    }

    replaceSelectionBeforeImeKey() {
      const [start, end] = this.normalizeControlSelection();
      if (start === end) return start;
      const next = `${this.control.value.slice(0, start)}${this.control.value.slice(end)}`;
      this.composer.setText(next, start);
      return start;
    }

    updateControlFromComposer() {
      const nextText = this.composer.text();
      this.syncRememberedReadings(nextText);
      this.internalUpdate = true;
      this.control.value = nextText;
      const cursor = this.composer.displayCursorPos();
      this.control.setSelectionRange(cursor, cursor);
      this.internalUpdate = false;
      this.onUpdate();
      this.renderCandidates();
    }

    shouldHandleKey(event) {
      if (!this.isEnabled()) return false;
      if (event.ctrlKey || event.metaKey || event.altKey || event.isComposing) return false;
      if (event.key.length === 1) return true;
      if (this.activeCandidates.length && ["ArrowUp", "ArrowDown", "Tab", "Escape"].includes(event.key)) return true;
      return ["Backspace", "ArrowLeft", "ArrowRight", "Home", "End", "Enter"].includes(event.key);
    }

    handleKeydown(event) {
      if (!this.shouldHandleKey(event)) return;

      if (this.activeCandidates.length) {
        if (["Escape", "ArrowRight"].includes(event.key)) {
          event.preventDefault();
          this.dismissCandidates();
          return;
        }
        if (["ArrowUp", "ArrowDown", "Tab"].includes(event.key)) {
          event.preventDefault();
          const backwards = event.key === "ArrowUp" || (event.key === "Tab" && event.shiftKey);
          this.setCandidateIndex(this.activeCandidateIndex + (backwards ? -1 : 1));
          return;
        }
        if (event.key === "Enter") {
          event.preventDefault();
          this.applyCandidate(this.activeCandidates[this.activeCandidateIndex]);
          return;
        }
      }

      if (event.key === "Enter" && this.enterBehavior !== "newline") {
        this.renderCandidates();
        return;
      }

      event.preventDefault();
      this.syncComposerFromControl();
      this.replaceSelectionBeforeImeKey();

      if (event.key === "Backspace") {
        if (!this.removePreviousHiddenTone()) this.composer.backspace();
      } else if (event.key === "ArrowLeft") {
        this.composer.moveLeft();
      } else if (event.key === "ArrowRight") {
        this.composer.moveRight();
      } else if (event.key === "Home") {
        this.composer.commit();
        this.composer.cursorPos = 0;
        this.composer.keyHistory = [];
      } else if (event.key === "End") {
        this.composer.commit();
        this.composer.cursorPos = this.composer.output.length;
        this.composer.keyHistory = [];
      } else if (event.key === "Enter") {
        this.composer.insertLiteral("\n");
      } else if (event.key.length === 1) {
        if (!this.applyHiddenTone(event.key)) this.composer.processChar(event.key);
      }

      this.updateControlFromComposer();
    }

    handleBeforeInput(event) {
      if (!this.isEnabled() || event.isComposing || !event.cancelable) return;

      if (event.inputType === "insertText" && event.data) {
        event.preventDefault();
        this.syncComposerFromControl();
        this.replaceSelectionBeforeImeKey();
        for (const char of [...event.data]) {
          if (!this.applyHiddenTone(char)) this.composer.processChar(char);
        }
        this.updateControlFromComposer();
      } else if (event.inputType === "deleteContentBackward") {
        event.preventDefault();
        this.syncComposerFromControl();
        this.replaceSelectionBeforeImeKey();
        if (!this.removePreviousHiddenTone()) this.composer.backspace();
        this.updateControlFromComposer();
      } else if (event.inputType === "insertLineBreak" || event.inputType === "insertParagraph") {
        if (this.enterBehavior !== "newline") return;
        event.preventDefault();
        this.syncComposerFromControl();
        this.replaceSelectionBeforeImeKey();
        this.composer.insertLiteral("\n");
        this.updateControlFromComposer();
      }
    }

    handleInput() {
      if (this.internalUpdate) return;
      const normalizedValue = normalizeApostrophes(this.control.value);
      if (normalizedValue !== this.control.value) {
        const start = this.control.selectionStart ?? normalizedValue.length;
        const end = this.control.selectionEnd ?? start;
        this.control.value = normalizedValue;
        this.control.setSelectionRange?.(start, end);
      }
      this.syncRememberedReadings(normalizedValue);
      if (this.isEnabled()) {
        this.composer.setText(normalizedValue, this.control.selectionStart ?? normalizedValue.length);
      }
      this.onUpdate();
      this.renderCandidates();
    }

    handleCursorChange(event) {
      if (
        event?.type === "keyup" &&
        this.activeCandidates.length &&
        ["ArrowUp", "ArrowDown", "Tab"].includes(event.key)
      ) {
        return;
      }
      if (this.isEnabled()) {
        this.normalizeControlSelection();
        this.syncComposerFromControl();
      }
      if (event?.type === "click") this.dismissedCandidateContext = null;
      this.renderCandidates();
    }

    activeCandidateRange() {
      if (!this.isEnabled()) return null;
      const text = this.control.value;
      const cursor = this.control.selectionStart ?? text.length;
      const selectionEnd = this.control.selectionEnd ?? cursor;
      if (cursor !== selectionEnd) {
        const segment = text.slice(cursor, selectionEnd);
        if (!segment || ![...segment].every(isImeCandidateChar)) return null;
        return { text, start: cursor, end: selectionEnd, segment };
      }

      let start = cursor;
      while (start > 0 && isImeCandidateChar(text[start - 1])) start -= 1;
      if (start === cursor) return null;
      return { text, start, end: cursor, segment: text.slice(start, cursor) };
    }

    typedCandidateForm(start, end) {
      const text = this.control.value;
      this.syncRememberedReadings(text);
      let output = "";
      let index = start;
      while (index < end) {
        const remembered = this.rememberedHangulReadings.find(
          (span) => span.explicit && span.start === index && span.end <= end
        );
        if (remembered) {
          output += remembered.reading;
          index = remembered.end;
          continue;
        }
        const unit = readingUnitAt(text, index);
        if (!unit || unit.end > end) {
          output += text[index];
          index += 1;
          continue;
        }
        output += unit.text;
        index = unit.end;
      }
      return output;
    }

    findCandidates() {
      const range = this.activeCandidateRange();
      if (!range) return [];

      const chars = [...range.segment];
      const starts = [];
      let offset = range.start;
      for (const char of chars) {
        starts.push(offset);
        offset += char.length;
      }

      const found = [];
      for (let index = 0; index < chars.length; index += 1) {
        const suffix = chars.slice(index).join("");
        const key = normalizeText(TangliengimHangulIme.normalizeReadingBase(suffix));
        const entries = this.candidatesByReading.get(key);
        if (!entries?.length) continue;
        const start = starts[index];
        const typedForm = this.typedCandidateForm(start, range.end);
        const filteredEntries = filterCandidateEntries(typedForm, entries);
        const exactHangulOverride = filteredEntries.some(
          (entry) => entry.kind === "hangul_override" &&
            TangliengimHangulIme.normalizeReadingToneKey(entry.reading) ===
              TangliengimHangulIme.normalizeReadingToneKey(typedForm)
        );
        for (const entry of filteredEntries) {
          found.push({
            entry,
            start,
            end: range.end,
            length: suffix.length,
          });
        }
        if (!exactHangulOverride) {
          found.push({
            entry: {
              hanri: key ? TangliengimHangulIme.normalizeReadingBase(suffix) : suffix,
              reading: typedForm,
              readingBase: TangliengimHangulIme.normalizeReadingBase(suffix),
              kind: "hangul_plain",
              generatedCandidate: true,
            },
            start,
            end: range.end,
            length: suffix.length,
          });
        }
        if (found.length) break;
      }

      const seen = new Set();
      const uniqueCandidates = found
        .filter(({ entry }) => {
          const key = `${entry.hanri}\u0000${entry.reading}`;
          if (seen.has(key)) return false;
          seen.add(key);
          return true;
        });
      return uniqueCandidates
        .sort((left, right) =>
          Number(Boolean(left.entry.generatedCandidate)) - Number(Boolean(right.entry.generatedCandidate))
        )
        .slice(0, this.candidateLimit);
    }

    renderCandidates() {
      if (!this.candidateContainer) return;
      this.candidateContainer.replaceChildren();

      if (!this.isEnabled()) {
        this.activeCandidates = [];
        this.candidateContainer.hidden = true;
        this.onCandidatesChanged(this);
        return;
      }

      const context = this.candidateContextKey();
      if (this.dismissedCandidateContext === context) {
        this.activeCandidates = [];
        this.activeCandidateIndex = 0;
        this.candidateContainer.hidden = true;
        this.onCandidatesChanged(this);
        return;
      }
      this.dismissedCandidateContext = null;

      this.activeCandidates = this.findCandidates();
      this.activeCandidateIndex = 0;
      const range = this.activeCandidates[0];
      if (range) {
        const remembered = this.rememberedHangulReadings.find(
          (span) => span.start === range.start && span.end === range.end
        );
        if (remembered && !remembered.explicit) {
          const selected = this.activeCandidates.findIndex(
            ({ entry, start, end }) => start === range.start && end === range.end &&
              entry.reading === remembered.reading
          );
          if (selected >= 0) this.activeCandidateIndex = selected;
        }
      }
      this.candidateContainer.hidden = !this.activeCandidates.length;
      if (!this.activeCandidates.length) {
        this.onCandidatesChanged(this);
        return;
      }

      for (const [index, candidate] of this.activeCandidates.entries()) {
        const button = document.createElement("button");
        button.type = "button";
        button.tabIndex = -1;
        button.className = "ime-candidate";
        button.setAttribute("role", "option");
        button.setAttribute("aria-selected", String(index === this.activeCandidateIndex));
        button.classList.toggle("selected", index === this.activeCandidateIndex);

        const number = document.createElement("span");
        number.className = "candidate-number";
        number.textContent = String(index + 1);

        const hanri = document.createElement("span");
        hanri.className = "candidate-hanri";
        if (["hangul_override", "hangul_plain"].includes(candidate.entry.kind)) {
          hanri.classList.add("candidate-hangul");
          hanri.append(renderToneMarkedReading(candidate.entry.reading));
        } else {
          hanri.textContent = candidate.entry.hanri;
        }

        const reading = document.createElement("span");
        reading.className = "candidate-reading";
        if (!["hangul_override", "hangul_plain"].includes(candidate.entry.kind)) {
          reading.append(renderToneMarkedReading(candidate.entry.reading));
        }

        button.append(number, hanri);
        if (!["hangul_override", "hangul_plain"].includes(candidate.entry.kind)) {
          button.append(reading);
        }
        button.addEventListener("mousedown", (event) => event.preventDefault());
        button.addEventListener("mouseenter", () => this.setCandidateIndex(index));
        button.addEventListener("click", () => this.applyCandidate(candidate));
        this.candidateContainer.append(button);
      }
      this.onCandidatesChanged(this);
    }

    candidateContextKey() {
      return `${this.control.value}\u0000${this.control.selectionStart ?? 0}\u0000${this.control.selectionEnd ?? 0}`;
    }

    dismissCandidates() {
      this.dismissedCandidateContext = this.candidateContextKey();
      this.activeCandidates = [];
      this.activeCandidateIndex = 0;
      this.candidateContainer.replaceChildren();
      this.candidateContainer.hidden = true;
      this.onCandidatesChanged(this);
      this.control.focus();
    }

    setCandidateIndex(index) {
      if (!this.activeCandidates.length) return;
      this.activeCandidateIndex = (index + this.activeCandidates.length) % this.activeCandidates.length;
      for (const [candidateIndex, button] of [...this.candidateContainer.children].entries()) {
        const selected = candidateIndex === this.activeCandidateIndex;
        button.classList.toggle("selected", selected);
        button.setAttribute("aria-selected", String(selected));
        if (selected && typeof button.scrollIntoView === "function") {
          button.scrollIntoView({ block: "nearest" });
        }
      }
    }

    applyCandidate(candidate) {
      const text = this.control.value;
      const isHangul = ["hangul_override", "hangul_plain"].includes(candidate.entry.kind);
      const replacement = isHangul
        ? TangliengimHangulIme.normalizeReadingBase(candidate.entry.reading || candidate.entry.hanri)
        : candidate.entry.hanri;
      const next = `${text.slice(0, candidate.start)}${replacement}${text.slice(candidate.end)}`;
      this.syncRememberedReadings(next);
      this.composer.setText(next, candidate.start + replacement.length);
      if (isHangul) {
        this.rememberHangulReading(
          candidate.start,
          candidate.start + replacement.length,
          candidate.entry.reading || replacement,
          candidate.entry.kind === "hangul_plain" ? null : candidate.entry,
          next,
          false
        );
      } else {
        this.rememberHanriReading(candidate.start, candidate.entry, next);
      }
      this.updateControlFromComposer();
      this.dismissCandidates();
    }
  }

  function createTextImeController(options) {
    return new TextImeController(options);
  }

  return {
    buildReadingCandidateMap,
    citationToTaipeiSandhiTone,
    createCandidatePopupPositioner,
    createDictionaryIndex,
    createTextImeController,
    displayTextNode,
    headwordUnitAt,
    isToneMark,
    isCheckedFinalUnit,
    normalizeEnglishSearch,
    normalizeApostrophes,
    normalizeLomariSearchAliases,
    normalizeText,
    queryVariants,
    readingUnitAt,
    readingUnitToneEnd,
    renderInlineUpperToneReading,
    renderToneMarkedReading,
    searchableEntry,
    singaporeTone1AudioReplacement,
    tonesByBasePosition,
    typedTonesAreCompatibleWithEntry,
  };
})();

window.TangliengimImeCore = TangliengimImeCore;
