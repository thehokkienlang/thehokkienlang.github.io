(() => {
  "use strict";
  const DATA_URL = "/public/data/hokkien-hanri-dict.json";
  const RUNTIME_URL = "/public/data/hokkien-hanri-dict-runtime.json";
  // Filled with content hashes by tools/build_site.py; unbuilt checkouts revalidate.
  const DATA_VERSIONS = {};
  async function fetchDictionaryJson(url) {
    const version = DATA_VERSIONS[url];
    const response = await (version ? fetch(`${url}?v=${version}`) : fetch(url, { cache: "no-cache" }));
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
  const LIMIT = 2000;
  const ImeCore = window.TangliengimImeCore;
  const phoneticCore = window.TangliengimPhoneticOutput;
  const webAudio = window.TangliengimWebAudio;

  const translator = document.querySelector("#translator");
  const englishPane = document.querySelector("#englishPane");
  const hokkienPane = document.querySelector("#hokkienPane");
  const englishText = document.querySelector("#englishText");
  const hokkienText = document.querySelector("#hokkienText");
  const candidates = document.querySelector("#hokkienCandidates");
  const hokkienWrap = document.querySelector(".hokkien-input-wrap");
  const toneOverlay = document.querySelector("#hokkienToneOverlay");
  const lomariPreview = document.querySelector("#lomariPreview");
  const keyboardToggle = document.querySelector("#hangulKeyboardToggle");
  const englishRole = document.querySelector("#englishRole");
  const hokkienRole = document.querySelector("#hokkienRole");
  const alternatives = document.querySelector("#alternatives");
  const alternativeList = document.querySelector("#alternativeList");
  const sandhiMode = document.querySelector("#sandhiMode");
  const audioButton = document.querySelector("#listenHokkien");
  const toast = document.querySelector("#toast");

  const state = {
    direction: "en-hok",
    entries: [],
    index: ImeCore.createDictionaryIndex([]),
    englishMap: new Map(),
    exactHanri: new Map(),
    exactReading: new Map(),
    maxEnglishWords: 1,
    unitRoman: new Map(), rawHangulAudio: new Map(), jamoLomari: new Map(), jamoAudio: new Map(),
  };

  const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent || "") || navigator.maxTouchPoints > 1;
  const popup = ImeCore.createCandidatePopupPositioner({ control: hokkienText, container: candidates, boundary: hokkienWrap, placement: "caret" });
  let translateTimer = 0;
  const ime = ImeCore.createTextImeController({
    control: hokkienText,
    candidateContainer: candidates,
    enabled: () => keyboardToggle.checked,
    onUpdate: () => { updateHokkienPresentation(); updateCounts(); if (state.direction === "hok-en") scheduleTranslation(); },
    onCandidatesChanged: popup.schedule,
    enterBehavior: "newline",
    recomposeNativeKoreanInput: isMobile,
  });

  function canonicalEntries(entries) {
    return entries.filter(entry => ImeCore.searchableEntry(entry) && !entry.autoSandhi && !entry.correctedFrom);
  }

  function addMap(map, key, entry) {
    if (!key) return;
    if (!map.has(key)) map.set(key, []);
    const values = map.get(key);
    if (!values.some(item => item.id === entry.id)) values.push(entry);
  }

  function displayHokkien(entry) {
    const hanri = ImeCore.stripLegacyInlineToneMarks(entry.hanri || "");
    if (entry.kind !== "hangul_override" && hanri) return hanri;
    return TangliengimHangulIme.normalizeReadingBase(entry.readingBase || entry.reading || hanri);
  }

  function firstEnglish(entry) {
    return String(entry.english || "").split(";").map(value => value.trim()).find(Boolean) || "";
  }

  function buildTranslationIndexes(entries) {
    state.englishMap.clear(); state.exactHanri.clear(); state.exactReading.clear(); state.maxEnglishWords = 1;
    for (const entry of canonicalEntries(entries)) {
      const senses = String(entry.english || "").split(";").map(value => value.trim()).filter(Boolean);
      for (const sense of senses) {
        const key = ImeCore.normalizeEnglishSearch(sense);
        addMap(state.englishMap, key, entry);
        state.maxEnglishWords = Math.max(state.maxEnglishWords, sense.split(/\s+/).length);
      }
      const hanri = ImeCore.normalizeText(ImeCore.stripLegacyInlineToneMarks(entry.hanri || ""));
      const reading = ImeCore.normalizeText(TangliengimHangulIme.normalizeReadingBase(entry.readingBase || entry.reading || ""));
      addMap(state.exactHanri, hanri, entry); addMap(state.exactReading, reading, entry);
    }
    for (const map of [state.englishMap, state.exactHanri, state.exactReading]) {
      for (const [key, values] of map) map.set(key, ImeCore.rankEntries(values, key));
    }
  }

  function exactEnglishMatches(text) { return state.englishMap.get(ImeCore.normalizeEnglishSearch(text)) || []; }
  function exactHokkienMatches(text) {
    const key = ImeCore.normalizeText(text);
    return [...new Map([...(state.exactHanri.get(key) || []), ...(state.exactReading.get(key) || [])].map(entry => [entry.id, entry])).values()];
  }

  function translateEnglish(text) {
    const exact = exactEnglishMatches(text);
    if (exact.length) return { text: displayHokkien(exact[0]), alternatives: exact };
    const tokens = text.match(/[A-Za-z]+(?:[’'][A-Za-z]+)*|\s+|[^\sA-Za-z]+/g) || [];
    const output = []; const used = [];
    for (let index = 0; index < tokens.length;) {
      if (!/^[A-Za-z]/.test(tokens[index])) { output.push(tokens[index++]); continue; }
      let match = null;
      for (let words = Math.min(state.maxEnglishWords, 8); words >= 1; words -= 1) {
        let cursor = index, count = 0, end = index;
        while (cursor < tokens.length && count < words) {
          if (!/^[A-Za-z]/.test(tokens[cursor])) break;
          count += 1; end = cursor + 1; cursor += 1;
          if (count < words) {
            if (cursor >= tokens.length || !/^\s+$/.test(tokens[cursor])) break;
            cursor += 1; end = cursor;
          }
        }
        if (count !== words) continue;
        const entries = exactEnglishMatches(tokens.slice(index, end).join(""));
        if (entries.length) { match = { entries, end }; break; }
      }
      if (!match) { output.push(tokens[index++]); continue; }
      output.push(displayHokkien(match.entries[0])); used.push(...match.entries); index = match.end;
    }
    return { text: output.join(""), alternatives: [...new Map(used.map(entry => [entry.id, entry])).values()].slice(0, 12) };
  }

  function translateHokkien(text) {
    const exact = exactHokkienMatches(text);
    if (exact.length) return { text: firstEnglish(exact[0]), alternatives: exact };
    const output = []; const used = [];
    for (let index = 0; index < text.length;) {
      const char = String.fromCodePoint(text.codePointAt(index));
      if (/\s/u.test(char)) { output.push(char); index += char.length; continue; }
      let entry = state.index.findHanriEntry(text, index);
      let end = entry ? index + entry.hanri.length : index;
      if (!entry) {
        const hangul = state.index.findHangulOverrideAt(text, index);
        entry = hangul?.entry || null; end = hangul?.end || index;
      }
      if (!entry) { output.push(char); index += char.length; continue; }
      const english = firstEnglish(entry);
      output.push(english || displayHokkien(entry)); used.push(entry); index = Math.max(end, index + char.length);
      const next = String.fromCodePoint(text.codePointAt(index));
      if (next && !/[\s\p{P}]/u.test(next)) output.push(" ");
    }
    return { text: output.join("").replace(/\s+([,.!?;:])/g, "$1"), alternatives: [...new Map(used.map(entry => [entry.id, entry])).values()].slice(0, 12) };
  }

  function setHokkienText(value) {
    const text = String(value || "").slice(0, LIMIT);
    ime.composer.setText(text, text.length); ime.updateControlFromComposer({ allowCandidateMenu: false }); updateHokkienPresentation();
  }

  function performTranslation() {
    if (!state.entries.length) return;
    const source = state.direction === "en-hok" ? englishText.value : hokkienText.value;
    if (!source.trim()) {
      if (state.direction === "en-hok") setHokkienText(""); else englishText.value = "";
      renderAlternatives([]); updateCounts(); return;
    }
    const result = state.direction === "en-hok" ? translateEnglish(source) : translateHokkien(source);
    if (state.direction === "en-hok") setHokkienText(result.text); else englishText.value = result.text.slice(0, LIMIT);
    renderAlternatives(result.alternatives); updateCounts();
  }

  function scheduleTranslation() { clearTimeout(translateTimer); translateTimer = setTimeout(performTranslation, 280); }

  function renderAlternatives(entries) {
    alternativeList.replaceChildren(); alternatives.hidden = !entries.length;
    for (const [index, entry] of entries.slice(0, 12).entries()) {
      const button = document.createElement("button"); button.type = "button"; button.className = "alternative";
      if (index === 0) button.classList.add("selected");
      const headword = document.createElement("strong"); headword.textContent = displayHokkien(entry);
      const lomari = document.createElement("span"); lomari.className = "alternative-lomari"; lomari.textContent = entry.lomari || "";
      const meaning = document.createElement("span"); meaning.textContent = entry.english || "Meaning not yet recorded";
      button.append(headword, lomari, meaning);
      button.addEventListener("click", () => {
        alternativeList.querySelectorAll(".selected").forEach(node => node.classList.remove("selected")); button.classList.add("selected");
        if (state.direction === "en-hok") setHokkienText(displayHokkien(entry)); else englishText.value = firstEnglish(entry);
        updateCounts();
      });
      alternativeList.append(button);
    }
  }

  function findHanriEntry(text, index) { return ime.findRememberedHanriEntry(text, index) || state.index.findHanriEntry(text, index, ime.nextRememberedHanriStart(text, index)); }
  function findHangulOverrideAt(text, index) { return ime.findRememberedHangulEntryAt(text, index) || state.index.findHangulOverrideAt(text, index, ime.nextRememberedHangulStart(text, index)); }
  const lomariRenderer = phoneticCore.createRenderer({
    imeCore: ImeCore, findHanriEntry, findHangulOverride: reading => state.index.findHangulOverride(reading), findHangulOverrideAt,
    findRememberedHangulEntryAt: (text, index) => ime.findRememberedHangulEntryAt(text, index),
    findUnitRoman: unit => state.unitRoman.get(unit) || "", findJamoLomari: unit => state.jamoLomari.get(unit) || "",
  });
  const audioPlanner = phoneticCore.createAudioPlanner({
    imeCore: ImeCore, getSandhiMode: () => sandhiMode.value, findHanriEntry,
    findReadingEntry: reading => state.index.findReadingEntry(reading), findHangulOverrideAt,
    findRememberedHangulEntryAt: (text, index) => ime.findRememberedHangulEntryAt(text, index),
    findJamoAudio: unit => state.jamoAudio.get(unit), findRawHangulAudio: key => state.rawHangulAudio.get(key),
    normalizeReadingToneKey: TangliengimHangulIme.normalizeReadingToneKey,
  });
  const audioPlayer = webAudio.createPlayer();

  function updateToneOverlay() {
    const spans = new Map(ime.getHangulToneReadingsForDisplay(hokkienText.value).map(span => [span.start, span]));
    for (const span of lomariRenderer.resolvedHangulToneSpans(hokkienText.value)) spans.set(span.start, span);
    toneOverlay.replaceChildren(ImeCore.renderToneOverlayMarks(hokkienText.value, [...spans.values()], hokkienText));
    toneOverlay.style.width = `${hokkienText.clientWidth}px`; toneOverlay.style.height = `${hokkienText.clientHeight}px`;
    for (const anchor of toneOverlay.children) anchor.style.transform = `translate(${-hokkienText.scrollLeft}px, ${-hokkienText.scrollTop}px)`;
  }
  function updateHokkienPresentation() { lomariPreview.textContent = lomariRenderer.render(hokkienText.value); updateToneOverlay(); }
  function updateCounts() { document.querySelector("#englishCount").textContent = `${englishText.value.length} / ${LIMIT}`; document.querySelector("#hokkienCount").textContent = `${hokkienText.value.length} / ${LIMIT}`; }
  function showToast(message) { toast.textContent = message; toast.classList.add("visible"); clearTimeout(showToast.timer); showToast.timer = setTimeout(() => toast.classList.remove("visible"), 1500); }
  async function copy(value) { await navigator.clipboard.writeText(value); showToast("Copied"); }

  async function playHokkien() {
    if (audioPlayer.isPlaying()) { audioPlayer.stop(); audioButton.classList.remove("playing"); return; }
    const plan = audioPlanner.plan(hokkienText.value); if (!plan.segments.length) { showToast("No audio available"); return; }
    audioButton.classList.add("playing"); try { await audioPlayer.play(plan.segments); } catch { showToast("Could not play audio"); } finally { audioButton.classList.remove("playing"); }
  }

  function updateDirection() {
    const reverse = state.direction === "hok-en"; translator.classList.toggle("reverse", reverse);
    englishRole.textContent = reverse ? "Translation" : "Source"; hokkienRole.textContent = reverse ? "Source" : "Translation";
    englishPane.classList.toggle("is-output", reverse);
    hokkienPane.classList.toggle("is-output", !reverse);
    englishText.readOnly = reverse;
    hokkienText.readOnly = !reverse;
    englishText.placeholder = reverse ? "" : "Enter English…";
    hokkienText.placeholder = reverse ? "輸入閩南語…" : "";
    keyboardToggle.disabled = !reverse;
    (reverse ? hokkienText : englishText).focus(); performTranslation();
  }

  async function loadDictionary() {
    try {
      const [data, runtimeData] = await Promise.all([fetchDictionaryJson(DATA_URL), fetchDictionaryJson(RUNTIME_URL)]);
      const runtime = runtimeData.runtime || {}; state.entries = canonicalEntries(data.entries || []); state.index = ImeCore.createDictionaryIndex(data.entries || []);
      state.unitRoman = new Map(Object.entries(runtime.unitRoman || {})); state.rawHangulAudio = new Map(Object.entries(runtime.rawHangulAudio || {}));
      state.jamoLomari = new Map(Object.entries(runtime.jamoLomari || {})); state.jamoAudio = new Map(Object.entries(runtime.jamoAudio || {}));
      buildTranslationIndexes(state.entries); await ime.preferences.ready; ime.setEntries(state.index.entries, state.index);
      performTranslation();
    } catch (error) { showToast(`Dictionary unavailable: ${error.message}`); }
  }

  englishText.addEventListener("input", () => { englishText.value = englishText.value.slice(0, LIMIT); updateCounts(); if (state.direction === "en-hok") scheduleTranslation(); });
  hokkienText.addEventListener("scroll", updateToneOverlay);
  document.querySelector("#swapDirection").addEventListener("click", () => { state.direction = state.direction === "en-hok" ? "hok-en" : "en-hok"; updateDirection(); });
  document.querySelector("#clearEnglish").addEventListener("click", () => { englishText.value = ""; updateCounts(); if (state.direction === "en-hok") performTranslation(); });
  document.querySelector("#clearHokkien").addEventListener("click", () => { ime.clear(); updateCounts(); if (state.direction === "hok-en") performTranslation(); });
  document.querySelector("#copyEnglish").addEventListener("click", () => copy(englishText.value).catch(() => showToast("Could not copy")));
  document.querySelector("#copyHokkien").addEventListener("click", () => copy(hokkienText.value).catch(() => showToast("Could not copy")));
  audioButton.addEventListener("click", playHokkien); keyboardToggle.addEventListener("change", () => hokkienText.focus());
  new ResizeObserver(updateToneOverlay).observe(hokkienText);
  updateCounts(); updateDirection(); loadDictionary();
})();
