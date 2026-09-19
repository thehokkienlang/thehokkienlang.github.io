const TangliengimPhoneticOutput = (() => {
  const INITIALS = [
    "\u1100", "\u1101", "\u1102", "\u1103", "\u1104", "\u1105", "\u1106",
    "\u1107", "\u1108", "\u1109", "\u110a", "\u110b", "\u110c", "\u110d",
    "\u110e", "\u110f", "\u1110", "\u1111", "\u1112",
  ];
  const MEDIALS = [
    "\u1161", "\u1162", "\u1163", "\u1164", "\u1165", "\u1166", "\u1167",
    "\u1168", "\u1169", "\u116a", "\u116b", "\u116c", "\u116d", "\u116e",
    "\u116f", "\u1170", "\u1171", "\u1172", "\u1173", "\u1174", "\u1175",
  ];
  const FINALS = [
    "", "\u11a8", "\u11a9", "\u11aa", "\u11ab", "\u11ac", "\u11ad", "\u11ae",
    "\u11af", "\u11b0", "\u11b1", "\u11b2", "\u11b3", "\u11b4", "\u11b5",
    "\u11b6", "\u11b7", "\u11b8", "\u11b9", "\u11ba", "\u11bb", "\u11bc",
    "\u11bd", "\u11be", "\u11bf", "\u11c0", "\u11c1", "\u11c2",
  ];
  const INITIAL_ROMAN = {
    "\u110b": "", "\u1100": "k", "\u1101": "g", "\u1102": "n", "\u1103": "t",
    "\u1104": "r", "\u1105": "l", "\u1106": "m", "\u1107": "p", "\u1108": "b",
    "\u1109": "s", "\u110c": "j", "\u110d": "js", "\u110e": "ch", "\u110f": "kh",
    "\u1110": "th", "\u1111": "ph", "\u1112": "h", "\u1159": "ng",
  };
  const MEDIAL_ROMAN = {
    "\u1161": "a", "\u1162": "ai", "\u1163": "ia", "\u1165": "or", "\u1166": "e",
    "\u1167": "ior", "\u1168": "ie", "\u1169": "o", "\u116a": "oa", "\u116b": "oai",
    "\u116c": "oe", "\u116d": "io", "\u116e": "u", "\u1170": "ue", "\u1171": "ui",
    "\u1172": "iu", "\u1173": "", "\u1174": "i", "\u1175": "i", "\u1177": "au",
    "\u11a4": "iau", "\ud7fb": "er",
  };
  const FINAL_ROMAN = {
    "": "", "\u11a8": "k", "\u11ab": "n", "\u11ae": "t", "\u11af": "l",
    "\u11b7": "m", "\u11b8": "p", "\u11bc": "ng", "\u11ba": "", "\u11bd": "t",
    "\u11be": "h", "\u11c2": "h",
  };
  const L_CLUSTER_FINALS = {
    "\u11b6": "h", "\u11b0": "k", "\u11cd": "n", "\u11ce": "t",
    "\u11b1": "m", "\u11b2": "p", "\u11b4": "t",
  };
  const COMPAT_INITIAL = {
    "\u3131": "\u1100", "\u3132": "\u1101", "\u3134": "\u1102", "\u3137": "\u1103",
    "\u3138": "\u1104", "\u3139": "\u1105", "\u3141": "\u1106", "\u3142": "\u1107",
    "\u3143": "\u1108", "\u3145": "\u1109", "\u3147": "\u110b", "\u3148": "\u110c",
    "\u3149": "\u110d", "\u314a": "\u110e", "\u314b": "\u110f", "\u314c": "\u1110",
    "\u314d": "\u1111", "\u314e": "\u1112", "\u3186": "\u1159",
  };
  const COMPAT_MEDIAL = {
    "\u314f": "\u1161", "\u3150": "\u1162", "\u3151": "\u1163", "\u3153": "\u1165",
    "\u3154": "\u1166", "\u3155": "\u1167", "\u3156": "\u1168", "\u3157": "\u1169",
    "\u3158": "\u116a", "\u3159": "\u116b", "\u315a": "\u116c", "\u315b": "\u116d",
    "\u315c": "\u116e", "\u315e": "\u1170", "\u315f": "\u1171", "\u3160": "\u1172",
    "\u3161": "\u1173", "\u3162": "\u1174", "\u3163": "\u1175",
  };
  const TONE_DIGITS = {
    "1": "1", "\u02c6": "1", "\ua788": "1",
    "2": "2", "\u02cb": "2", "`": "2", "\u02ce": "2",
    "3": "3",
    "4": "4", "\u02ca": "4", "\u02cf": "4",
    "5": "5", "\u02c9": "5", "\u02cd": "5",
  };
  const TONE_MARKS = { 1: "\u0302", 2: "\u0300", 3: "", 4: "\u0301", 5: "\u0304" };
  const TONE_PRIORITY = ["a", "e", "o", "u", "i", "n", "m"];
  const CHECKED_FINALS = new Set(["\u11a8", "\u11ae", "\u11b8", "\u11c2", "\u11b6", "\u11bd", "\u11be"]);
  const OPEN_SANDHI = { 1: "5", 2: "1", 3: "2", 4: "3", 5: "3" };
  const CHECKED_SANDHI = { 1: "3", 3: "1" };
  const PUNCTUATION = /[\p{Punctuation}\p{Symbol}]/u;
  const AUDIO_PHRASE_BOUNDARIES = new Set([
    ",", "，", ".", "。", "!", "?", "！", "？", ":", "：", ";", "；",
    "-", "－", "—", "\n", "\r",
  ]);

  function toneDigit(char) {
    return TONE_DIGITS[char] || "";
  }

  function markTargetIndex(body) {
    const lower = body.toLowerCase();
    for (const letter of TONE_PRIORITY) {
      const indexes = [];
      for (let index = 0; index < lower.length; index += 1) {
        if (lower[index] === letter && !/\p{Mark}/u.test(lower[index])) indexes.push(index);
      }
      if (indexes.length) return letter === "n" || letter === "m" ? indexes[Math.min(1, indexes.length - 1)] : indexes[0];
    }
    return [...body].findIndex((char) => /[A-Za-z]/.test(char));
  }

  function addCombiningMark(body, mark) {
    if (!mark) return body;
    const normalized = String(body || "").normalize("NFD");
    const index = markTargetIndex(normalized);
    if (index < 0) return normalized;
    let end = index + 1;
    while (end < normalized.length && /\p{Mark}/u.test(normalized[end])) {
      if (normalized[end] === mark) return normalized;
      end += 1;
    }
    return `${normalized.slice(0, end)}${mark}${normalized.slice(end)}`;
  }

  function nasalize(rime) {
    return addCombiningMark(rime, "\u0330");
  }

  function applyTone(body, tone) {
    return addCombiningMark(body, TONE_MARKS[String(tone || "3")] || "");
  }

  function stripToneMarks(body) {
    return String(body || "").normalize("NFD").replace(/[\u0300\u0301\u0302\u0304]/g, "");
  }

  function decomposeSyllable(char) {
    const code = char?.codePointAt(0);
    if (code === undefined || code < 0xac00 || code > 0xd7a3) return null;
    const offset = code - 0xac00;
    return [
      INITIALS[Math.floor(offset / 588)],
      MEDIALS[Math.floor((offset % 588) / 28)],
      FINALS[offset % 28],
    ];
  }

  function glideNullInitial(initial, medial, rime) {
    if (initial !== "\u110b" || ["\u1175", "\u116e", "\u1174"].includes(medial)) return rime;
    if (rime.startsWith("i")) return `y${rime.slice(1)}`;
    if (rime.startsWith("u")) return `w${rime.slice(1)}`;
    return rime;
  }

  function specialOrRime(medial, final) {
    if (medial !== "\u1165" && medial !== "\u1167") return null;
    const base = medial === "\u1165" ? "or" : "ior";
    if (final === "\u11af") return nasalize(base);
    if (final === "\u11b6") return `${nasalize(base)}h`;
    if (!final) return base;
    if (final === "\u11c2") return `${base}h`;
    if (final === "\u11bc") return `${base.slice(0, -1)}ng`;
    return `${base}${FINAL_ROMAN[final] || ""}`;
  }

  function clusterToRoman(initial, medial, final = "") {
    const onset = INITIAL_ROMAN[initial] ?? "";
    if (medial === "\u1173" && final === "\u11ab") return `${onset}n`;

    const special = specialOrRime(medial, final);
    if (special !== null) return `${onset}${glideNullInitial(initial, medial, special)}`;

    const vowel = MEDIAL_ROMAN[medial] ?? "";
    let rime = vowel;
    if (final === "\u11af") rime = nasalize(vowel);
    else if (final in L_CLUSTER_FINALS) rime = `${nasalize(vowel)}${L_CLUSTER_FINALS[final]}`;
    else rime = `${vowel}${FINAL_ROMAN[final] || ""}`;
    return `${onset}${glideNullInitial(initial, medial, rime)}`;
  }

  function unitParts(unit) {
    const text = String(unit || "");
    const decomposed = text.length === 1 ? decomposeSyllable(text) : null;
    if (decomposed) return decomposed;
    if (text[0] === "\u115f" && text[1] in MEDIAL_ROMAN) return ["\u110b", text[1], ""];
    if ((text[0] in INITIAL_ROMAN) && (text[1] in MEDIAL_ROMAN)) {
      return [text[0], text[1], text[2] || ""];
    }
    return null;
  }

  function romanizeUnit(unit) {
    const text = String(unit || "");
    const parts = unitParts(text);
    if (parts) return clusterToRoman(parts[0], parts[1], parts[2]);
    if (text in COMPAT_INITIAL) return INITIAL_ROMAN[COMPAT_INITIAL[text]] ?? text;
    if (text in COMPAT_MEDIAL) return MEDIAL_ROMAN[COMPAT_MEDIAL[text]] ?? text;
    if (text === "\u3140") return "\u207fh";
    if (text in MEDIAL_ROMAN) return MEDIAL_ROMAN[text];
    return text;
  }

  function readingUnitAt(text, index, imeCore) {
    if (text[index] === "\u115f" && text[index + 1] in MEDIAL_ROMAN) {
      return { text: text.slice(index, index + 2), end: index + 2, canCarryTone: true };
    }
    return imeCore.readingUnitAt(text, index);
  }

  function readingSegments(reading, imeCore) {
    const segments = [];
    const text = String(reading || "");
    let index = 0;
    while (index < text.length) {
      const unit = readingUnitAt(text, index, imeCore);
      if (!unit?.canCarryTone) {
        index += String.fromCodePoint(text.codePointAt(index)).length;
        continue;
      }
      const marker = text[unit.end];
      segments.push({ unit: unit.text, tone: toneDigit(marker) || "3" });
      index = unit.end + (toneDigit(marker) ? 1 : 0);
    }
    return segments;
  }

  function entrySegments(entry, imeCore) {
    const written = readingSegments(entry?.reading || entry?.raw?.reading || "", imeCore);
    const audio = entry?.audio;
    const lomariParts = String(entry?.lomari || "").split("-");
    if (written.length && lomariParts.length === written.length) {
      const selectedTones = audio?.segments?.length === written.length
        ? audio.segments.map((segment) => String(segment.tone || "3"))
        : written.map((segment) => segment.tone);
      return written.map((segment, index) => ({
        unit: segment.unit,
        tone: selectedTones[index],
        roman: stripToneMarks(lomariParts[index]),
      }));
    }
    if (audio?.segments?.length) {
      if (written.length === audio.segments.length) {
        return written.map((segment, index) => ({
          unit: segment.unit,
          tone: String(audio.segments[index].tone || segment.tone || "3"),
          roman: "",
        }));
      }
      return audio.segments.map((segment) => ({
        unit: segment.unit,
        tone: String(segment.tone || "3"),
        roman: "",
      }));
    }
    return written;
  }

  function checkedUnit(unit) {
    const parts = unitParts(unit);
    return Boolean(parts && CHECKED_FINALS.has(parts[2]));
  }

  function sandhiTone(unit, tone) {
    const value = String(tone || "3");
    if (checkedUnit(unit)) return CHECKED_SANDHI[value] || value;
    return OPEN_SANDHI[value] || value;
  }

  function latinEnd(text, index) {
    let end = index;
    while (end < text.length && /[A-Za-z0-9]/.test(text[end])) end += 1;
    return end;
  }

  function createRenderer({
    imeCore,
    findHanriEntry,
    findHangulOverride,
    findHangulOverrideAt = () => null,
    findUnitRoman = () => "",
    findJamoLomari = () => "",
  }) {
    function syllablesForEntry(entry, protectFinal) {
      const segments = entrySegments(entry, imeCore);
      return segments.map((segment, index) => ({
        type: "syllable",
        unit: segment.unit,
        tone: segment.tone,
        roman: segment.roman || "",
        externalSandhi: !protectFinal && !entry.autoSandhi && index === segments.length - 1,
        fromTsv: true,
      }));
    }

    function tokenize(text) {
      const tokens = [];
      let index = 0;
      while (index < text.length) {
        const code = text.codePointAt(index);
        if (code === undefined) break;
        const char = String.fromCodePoint(code);

        const hanriEntry = findHanriEntry(text, index);
        if (hanriEntry) {
          tokens.push(...syllablesForEntry(hanriEntry, false));
          index += hanriEntry.hanri.length;
          continue;
        }

        const unit = readingUnitAt(text, index, imeCore);
        if (unit?.canCarryTone) {
          const marker = text[unit.end];
          const explicitTone = toneDigit(marker);
          if (explicitTone) {
            tokens.push({ type: "syllable", unit: unit.text, tone: explicitTone, externalSandhi: false, fromTsv: false });
            index = unit.end + 1;
            continue;
          }

          const overrideMatch = findHangulOverrideAt(text, index);
          if (overrideMatch?.entry) {
            tokens.push(...syllablesForEntry(overrideMatch.entry, false));
            index = overrideMatch.end;
            continue;
          }

          const override = findHangulOverride(unit.text);
          if (override) tokens.push(...syllablesForEntry(override, false));
          else tokens.push({ type: "syllable", unit: unit.text, tone: "3", externalSandhi: false, fromTsv: false });
          index = unit.end;
          continue;
        }

        const jamoLomari = findJamoLomari(char);
        if (jamoLomari) {
          tokens.push({ type: "word", text: jamoLomari });
          index += char.length;
          continue;
        }

        if (/[A-Za-z0-9]/.test(char)) {
          const end = latinEnd(text, index);
          tokens.push({ type: "word", text: text.slice(index, end) });
          index = end;
          continue;
        }

        if (char === "-") tokens.push({ type: "hyphen", text: char });
        else if (/\s/u.test(char)) tokens.push({ type: "separator", text: char });
        else if (PUNCTUATION.test(char)) tokens.push({ type: "separator", text: char });
        else tokens.push({ type: "literal", text: char });
        index += char.length;
      }
      return tokens;
    }

    function applyExternalSandhi(tokens) {
      return tokens.map((token, index) => {
        if (!token.externalSandhi) return token;
        const next = tokens[index + 1];
        if (!next || !["syllable", "word", "hyphen"].includes(next.type)) return token;
        return { ...token, tone: sandhiTone(token.unit, token.tone) };
      });
    }

    function render(text) {
      const normalizedText = imeCore.normalizeApostrophes(text);
      const tokens = applyExternalSandhi(tokenize(normalizedText));
      const output = [];
      let previousWasWord = false;
      for (const token of tokens) {
        if (token.type === "syllable") {
          if (previousWasWord) output.push("-");
          output.push(applyTone(token.roman || findUnitRoman(token.unit) || romanizeUnit(token.unit), token.tone));
          previousWasWord = true;
        } else if (token.type === "word") {
          if (previousWasWord) output.push("-");
          output.push(token.text);
          previousWasWord = true;
        } else if (token.type === "hyphen") {
          output.push("-");
          previousWasWord = false;
        } else {
          output.push(token.text);
          previousWasWord = false;
        }
      }
      return output.join("");
    }

    return { render };
  }

  function createAudioPlanner({
    imeCore,
    getSandhiMode = () => "taipei",
    findHanriEntry = () => null,
    findReadingEntry = () => null,
    findHangulOverrideAt = () => null,
    findJamoAudio = () => null,
    findRawHangulAudio = () => null,
    normalizeReadingToneKey = (value) => String(value || ""),
  }) {
    function normalizeAudioSegments(audio) {
      if (audio?.segments?.length) return audio.segments;
      return (audio?.files || []).map((file) => ({
        file,
        trimStart: false,
        trimEnd: false,
        speed: 1,
        lFinal: false,
        shortOverlapFinal: false,
        englishClusterHelper: false,
      }));
    }

    function audioForCurrentSandhiMode(audio) {
      if (getSandhiMode() === "singapore" && audio?.singapore) return audio.singapore;
      return audio;
    }

    function dictionaryAudioPath(file) {
      const value = String(file || "");
      if (!value || /^https?:\/\//i.test(value) || value.startsWith("/")) return value;
      return `/${value}`;
    }

    function appendAudioMetadata(audioMetadata, segments, missing) {
      const audio = audioForCurrentSandhiMode(audioMetadata);
      const audioSegments = normalizeAudioSegments(audio).map((segment) => ({
        ...segment,
        file: dictionaryAudioPath(segment.file),
      }));
      const start = segments.length;
      if (audioSegments.length) segments.push(...audioSegments);
      for (const item of audio?.missing || []) {
        if (!missing.includes(item)) missing.push(item);
      }
      return { start, end: segments.length };
    }

    function appendEntryAudio(entry, segments, missing) {
      const directAudio = audioForCurrentSandhiMode(entry?.audio);
      if (normalizeAudioSegments(directAudio).length || directAudio?.missing?.length) {
        return appendAudioMetadata(entry.audio, segments, missing);
      }

      const start = segments.length;
      const reading = String(entry?.reading || "");
      for (let index = 0; index < reading.length;) {
        const unit = imeCore.readingUnitAt(reading, index);
        if (!unit?.canCarryTone) {
          index += String.fromCodePoint(reading.codePointAt(index)).length;
          continue;
        }
        const end = imeCore.readingUnitToneEnd(reading, unit);
        const normalized = normalizeReadingToneKey(reading.slice(index, end));
        const tone = /[12345]$/u.test(normalized) ? normalized.at(-1) : "3";
        const audio = findRawHangulAudio(`${unit.text}${tone}`);
        if (audio) appendAudioMetadata(audio, segments, missing);
        else if (!missing.includes(reading.slice(index, end))) missing.push(reading.slice(index, end));
        index = end;
      }
      return { start, end: segments.length };
    }

    function withAudioTone(segment, tone) {
      const audio = audioForCurrentSandhiMode(findRawHangulAudio(`${segment.unit}${tone}`));
      const replacement = normalizeAudioSegments(audio)[0];
      if (!replacement) return { ...segment, tone: String(tone) };
      return {
        ...replacement,
        // Tone recordings are standalone; keep this occurrence's phrase timing.
        ...segment,
        unit: segment.unit,
        tone: String(tone),
        file: dictionaryAudioPath(replacement.file),
      };
    }

    function applyPendingSandhi(chunk, segments) {
      if (!chunk || chunk.end <= chunk.start) return;
      const finalIndex = chunk.end - 1;
      const finalSegment = segments[finalIndex];
      if (!finalSegment?.unit || !finalSegment?.tone) return;
      const sandhiTone = imeCore.citationToTaipeiSandhiTone(finalSegment.unit, finalSegment.tone);
      segments[finalIndex] = withAudioTone(finalSegment, sandhiTone);
    }

    function connectAudioChunk(previous, next, segments, connections) {
      if (!previous?.canSandhi || next.end <= next.start) return;
      applyPendingSandhi(previous, segments);
      connections.push({ previous, next });
    }

    function connectAudioTiming(previous, next, segments) {
      if (!previous || previous.end <= previous.start || next.end <= next.start) return;
      const previousIndex = previous.end - 1;
      segments[previousIndex] = { ...segments[previousIndex], trimEnd: true };
      segments[next.start] = { ...segments[next.start], trimStart: true };
    }

    function applySingaporeCrossChunkTones(connections, segments) {
      const linkedChunks = new Set(connections.map(({ previous }) => previous));
      for (let index = connections.length - 1; index >= 0; index -= 1) {
        const { previous, next } = connections[index];
        const segment = segments[previous.end - 1];
        const following = segments[next.start];
        if (!segment || !following || segment.tone !== "1" || imeCore.isCheckedFinalUnit(segment.unit)) continue;
        const tone = imeCore.singaporeTone1AudioReplacement(
          following.unit,
          following.tone,
          !linkedChunks.has(next)
        );
        segments[previous.end - 1] = withAudioTone(segment, tone);
      }
    }

    function plan(text) {
      const segments = [];
      const missing = [];
      let index = 0;
      let pendingChunk = null;
      let phraseChunk = null;
      const connections = [];

      function appendChunk(chunk, canSandhi) {
        if (chunk.end <= chunk.start) return;
        connectAudioChunk(pendingChunk, chunk, segments, connections);
        connectAudioTiming(phraseChunk, chunk, segments);
        phraseChunk = chunk;
        pendingChunk = canSandhi ? { ...chunk, canSandhi: true } : null;
      }

      while (index < text.length) {
        const code = text.codePointAt(index);
        if (code === undefined) break;
        const char = String.fromCodePoint(code);

        if (char === "-") {
          applyPendingSandhi(pendingChunk, segments);
          pendingChunk = null;
          phraseChunk = null;
          index += char.length;
          continue;
        }
        if (AUDIO_PHRASE_BOUNDARIES.has(char)) {
          pendingChunk = null;
          phraseChunk = null;
          index += char.length;
          continue;
        }
        if (/\s|\p{Punctuation}/u.test(char)) {
          pendingChunk = null;
          index += char.length;
          continue;
        }

        const jamoAudio = findJamoAudio(char);
        if (jamoAudio) {
          appendChunk(appendAudioMetadata(jamoAudio, segments, missing), false);
          index += char.length;
          continue;
        }

        const hanriEntry = findHanriEntry(text, index);
        if (hanriEntry) {
          appendChunk(appendEntryAudio(hanriEntry, segments, missing), !hanriEntry.autoSandhi);
          index += hanriEntry.hanri.length;
          continue;
        }

        const unit = imeCore.readingUnitAt(text, index);
        if (unit?.canCarryTone) {
          const end = imeCore.readingUnitToneEnd(text, unit);
          const raw = text.slice(index, end);
          const hasExplicitTone = end > unit.end;
          if (!hasExplicitTone) {
            const overrideMatch = findHangulOverrideAt(text, index);
            if (overrideMatch?.entry) {
              appendChunk(appendEntryAudio(overrideMatch.entry, segments, missing), true);
              index = overrideMatch.end;
              continue;
            }
          }

          const entry = findReadingEntry(raw) || findReadingEntry(unit.text);
          if (entry) {
            appendChunk(appendAudioMetadata(entry.audio, segments, missing), !hasExplicitTone);
          } else {
            const normalizedRaw = normalizeReadingToneKey(raw);
            const audioKey = /[12345]$/u.test(normalizedRaw) ? normalizedRaw : `${unit.text}3`;
            const rawAudio = findRawHangulAudio(audioKey);
            if (rawAudio) appendChunk(appendAudioMetadata(rawAudio, segments, missing), false);
            else {
              if (!missing.includes(raw)) missing.push(raw);
              pendingChunk = null;
            }
          }
          index = end;
          continue;
        }

        if (/[A-Za-z0-9]/.test(char)) {
          let end = index + char.length;
          while (end < text.length) {
            const next = String.fromCodePoint(text.codePointAt(end));
            if (!/[A-Za-z0-9]/.test(next)) break;
            end += next.length;
          }
          const word = text.slice(index, end);
          if (!missing.includes(word)) missing.push(word);
          applyPendingSandhi(pendingChunk, segments);
          pendingChunk = null;
          index = end;
          continue;
        }

        if (!missing.includes(char)) missing.push(char);
        pendingChunk = null;
        index += char.length;
      }

      if (getSandhiMode() === "singapore") {
        applySingaporeCrossChunkTones(connections, segments);
      }
      return { segments, missing };
    }

    return { plan };
  }

  return { applyTone, createAudioPlanner, createRenderer, romanizeUnit };
})();

window.TangliengimPhoneticOutput = TangliengimPhoneticOutput;
