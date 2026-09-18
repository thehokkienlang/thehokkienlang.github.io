const DATA_URL = "/public/data/hokkien-hanri-dict.json";
const RESULTS_PER_PAGE = 10;
const ImeCore = window.TangliengimImeCore;
const webAudio = window.TangliengimWebAudio;
const {
  createTextImeController,
  createDictionaryIndex,
  displayTextNode,
  headwordUnitAt,
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
} = ImeCore;

const state = {
  entries: [],
  dictionaryIndex: createDictionaryIndex([]),
  groups: [],
  categories: [],
  activeCategory: "",
  inputMode: "lomari",
  loaded: false,
  currentPage: 1,
};

const searchInput = document.querySelector("#searchInput");
const clearButton = document.querySelector("#clearButton");
const summaryBar = document.querySelector("#summaryBar");
const resultSummary = document.querySelector("#resultSummary");
const dataStatus = document.querySelector("#dataStatus");
const results = document.querySelector("#results");
const template = document.querySelector("#resultTemplate");
const pagination = document.querySelector("#pagination");
const hangulKeyboardToggle = document.querySelector("#hangulKeyboardToggle");
const imeCandidates = document.querySelector("#imeCandidates");
const categoryFilters = document.querySelector("#categoryFilters");
let searchImeController = null;
const audioPlayer = webAudio.createPlayer();
const normalizeAudioSegments = webAudio.normalizeAudioSegments;
const searchCandidatePopup = ImeCore.createCandidatePopupPositioner({
  control: searchInput,
  container: imeCandidates,
  placement: "below",
});

function visibleKind(kind) {
  const names = {
    plain_hanri: "Hanri",
    mixed_hanri: "Mixed",
    hangul_override: "Hangul",
    numeric_override: "Number",
    other: "Other",
  };
  return names[kind] || kind;
}


function groupKeyForEntry(entry) {
  const headword = entry.hanri || entry.reading;
  const reading = normalizeText(entry.readingBase || entry.reading || headword);
  return `${headword}\u0000${reading}`;
}

function visibleDictionaryEntry(entry) {
  return searchableEntry(entry) && !entry.correctedFrom && !entry.autoSandhi;
}

function groupEntries(entries) {
  const byHeadwordReading = new Map();
  for (const entry of entries.filter(visibleDictionaryEntry)) {
    const headword = entry.hanri || entry.reading;
    const key = groupKeyForEntry(entry);
    if (!byHeadwordReading.has(key)) {
      byHeadwordReading.set(key, {
        hanri: headword,
        kind: entry.kind,
        priority: entry.priority,
        row: entry.row,
        readings: [],
        categories: [],
        search: {
          hanri: normalizeText(headword),
          reading: "",
          readingBase: "",
          lomari: "",
          lomariAliases: "",
          english: "",
          all: "",
        },
      });
    }

    const group = byHeadwordReading.get(key);
    group.priority = Math.min(group.priority, entry.priority);
    group.row = Math.min(group.row, entry.row);
    group.readings.push(entry);
  }

  const groups = [...byHeadwordReading.values()];
  for (const group of groups) {
    group.readings.sort((a, b) =>
      a.priority - b.priority || a.row - b.row || a.reading.localeCompare(b.reading)
    );
    group.categories = [...new Set(group.readings.flatMap((item) => item.categories || []))];
    group.search.reading = normalizeText(group.readings.map((item) => item.reading).join(" "));
    group.search.readingBase = normalizeText(group.readings.map((item) => item.readingBase).join(" "));
    group.search.lomari = normalizeText(group.readings.map((item) => item.lomari).join(" "));
    group.search.lomariAliases = normalizeLomariSearchAliases(group.readings.map((item) => item.lomari).join(" "));
    group.search.english = normalizeEnglishSearch(group.readings.map((item) => item.english || "").join(" "));
    group.search.all = [
      group.search.hanri,
      group.search.reading,
      group.search.readingBase,
      group.search.lomari,
      group.search.lomariAliases,
      group.search.english,
      normalizeText(group.readings.map((item) => item.raw?.reading || "").join(" ")),
    ].join(" ");
  }

  return groups.sort((a, b) => a.priority - b.priority || a.row - b.row || a.hanri.localeCompare(b.hanri));
}

function scoreField(value, query, boost) {
  if (!value) return 0;
  if (value === query) return 100 + boost;
  if (value.startsWith(query)) return 80 + boost;
  if (value.includes(query)) return 55 + boost;
  return 0;
}

function scoreGroup(group, queries, mode) {
  if (!queries.length) {
    return 0;
  }

  const fields = [
    { name: "hanri", boost: mode === "hanri-hangul" ? 6 : 0 },
    { name: "reading", boost: mode === "hanri-hangul" ? 6 : 0 },
    { name: "readingBase", boost: mode === "hanri-hangul" ? 6 : 0 },
    { name: "lomari", boost: mode === "lomari" ? 6 : 0 },
    { name: "english", boost: 0 },
  ];

  let best = 0;
  for (const query of queries) {
    for (const field of fields) {
      const value = field.name === "lomari"
        ? `${group.search.lomari || ""} ${group.search.lomariAliases || ""}`.trim()
        : group.search[field.name] || "";
      best = Math.max(best, scoreField(value, query, field.boost));
    }
  }

  return best;
}

function searchGroups() {
  const rawQuery = searchInput.value.trim();
  const queries = queryVariants(rawQuery);

  const matches = state.groups
    .filter((group) => !state.activeCategory || group.categories.includes(state.activeCategory))
    .map((group) => ({
      group,
      score: queries.length ? scoreGroup(group, queries, state.inputMode) : (state.activeCategory ? 1 : 0),
    }))
    .filter((item) => item.score > 0)
    .sort((a, b) =>
      b.score - a.score ||
      a.group.priority - b.group.priority ||
      a.group.row - b.group.row ||
      a.group.hanri.localeCompare(b.group.hanri)
    );

  const total = matches.length;
  const totalPages = Math.ceil(total / RESULTS_PER_PAGE);
  const page = totalPages
    ? Math.max(1, Math.min(state.currentPage, totalPages))
    : 1;
  const start = (page - 1) * RESULTS_PER_PAGE;

  return {
    rawQuery,
    shown: matches.slice(start, start + RESULTS_PER_PAGE).map((item) => item.group),
    total,
    page,
    totalPages,
  };
}

function activeCategoryLabel() {
  return state.categories.find((category) => category.id === state.activeCategory)?.label || "";
}

function renderCategoryFilters() {
  categoryFilters.replaceChildren();
  for (const category of state.categories) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "category-button";
    button.textContent = category.label;
    button.setAttribute("aria-pressed", String(state.activeCategory === category.id));
    button.addEventListener("click", () => {
      state.activeCategory = state.activeCategory === category.id ? "" : category.id;
      state.currentPage = 1;
      renderCategoryFilters();
      renderResults();
    });
    categoryFilters.append(button);
  }
}

function findReadingUnitStart(text, start, unitText) {
  let index = start;
  while (index < text.length) {
    const unit = readingUnitAt(text, index);
    if (!unit) break;
    if (unit.canCarryTone && unit.text === unitText) {
      return index;
    }
    index = readingUnitToneEnd(text, unit);
  }
  return -1;
}

function findNextMixedReadingBoundary(source, sourceIndex, reading, readingIndex) {
  let index = sourceIndex;
  while (index < source.length) {
    const unit = headwordUnitAt(source, index);
    if (!unit) break;

    if (unit.kind === "hangul") {
      const match = findReadingUnitStart(reading, readingIndex, unit.text);
      if (match >= 0) return match;
    } else if (unit.kind === "literal") {
      const match = reading.indexOf(unit.text, readingIndex);
      if (match >= 0) return match;
    }

    index = unit.end;
  }
  return reading.length;
}

function appendHanriRuby(fragment, hanriText, readingText) {
  if (!readingText) {
    fragment.append(displayTextNode(hanriText));
    return;
  }

  const ruby = document.createElement("ruby");
  ruby.className = "entry-headword-ruby";
  const base = document.createElement("span");
  base.className = "entry-headword-base";
  base.append(displayTextNode(hanriText));
  const rt = document.createElement("rt");
  rt.className = "entry-headword-reading";
  rt.append(renderInlineUpperToneReading(readingText));
  ruby.append(base, rt);
  fragment.append(ruby);
}

function renderMixedEntryHeadword(group, reading) {
  const fragment = document.createDocumentFragment();
  const source = String(group.hanri || "");
  let sourceIndex = 0;
  let readingIndex = 0;

  while (sourceIndex < source.length) {
    const unit = headwordUnitAt(source, sourceIndex);
    if (!unit) break;

    if (unit.kind === "hanri") {
      const boundary = findNextMixedReadingBoundary(source, unit.end, reading, readingIndex);
      appendHanriRuby(fragment, unit.text, reading.slice(readingIndex, boundary));
      readingIndex = boundary;
    } else if (unit.kind === "hangul") {
      const hangul = document.createElement("span");
      hangul.className = "entry-headword-hangul entry-headword-inline-hangul";
      hangul.append(renderToneMarkedReading(unit.raw));
      fragment.append(hangul);

      const readingUnit = readingUnitAt(reading, readingIndex);
      if (readingUnit?.canCarryTone && readingUnit.text === unit.text) {
        readingIndex = readingUnitToneEnd(reading, readingUnit);
      }
    } else {
      fragment.append(displayTextNode(unit.text));
      if (reading.startsWith(unit.text, readingIndex)) {
        readingIndex += unit.text.length;
      }
    }

    sourceIndex = unit.end;
  }

  return fragment;
}

function renderEntryHeadword(group) {
  const fragment = document.createDocumentFragment();
  const primaryReading = group.readings[0]?.reading || group.hanri || "";

  if (group.kind === "hangul_override") {
    const hangul = document.createElement("span");
    hangul.className = "entry-headword-hangul";
    hangul.append(renderToneMarkedReading(primaryReading));
    fragment.append(hangul);
    return fragment;
  }

  if (group.kind === "mixed_hanri") {
    fragment.append(renderMixedEntryHeadword(group, primaryReading));
    return fragment;
  }

  const ruby = document.createElement("ruby");
  ruby.className = "entry-headword-ruby";
  const base = document.createElement("span");
  base.className = "entry-headword-base";
  base.append(displayTextNode(group.hanri));
  const rt = document.createElement("rt");
  rt.className = "entry-headword-reading";
  rt.append(renderInlineUpperToneReading(primaryReading));
  ruby.append(base, rt);
  fragment.append(ruby);
  return fragment;
}

function copyText(text) {
  if (navigator.clipboard?.writeText) {
    return navigator.clipboard.writeText(text);
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.append(textarea);
  textarea.select();
  document.execCommand("copy");
  textarea.remove();
  return Promise.resolve();
}

function showToast(message) {
  let toast = document.querySelector(".toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "toast";
    toast.setAttribute("role", "status");
    toast.setAttribute("aria-live", "polite");
    document.body.append(toast);
  }

  toast.textContent = message;
  toast.classList.add("visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("visible"), 1500);
}

async function playAudioSequence(audio, button) {
  button.classList.add("playing");
  button.disabled = true;
  try {
    await audioPlayer.play(audio);
  } finally {
    button.classList.remove("playing");
    button.disabled = false;
  }
}

function renderReading(entry) {
  const wrapper = document.createElement("div");
  wrapper.className = "reading";

  const lomariField = document.createElement("div");
  lomariField.className = "reading-field";
  const lomariLabel = document.createElement("span");
  lomariLabel.className = "field-label";
  lomariLabel.textContent = "Lomari";
  const lomari = document.createElement("span");
  lomari.className = "lomari";
  lomari.textContent = normalizeApostrophes(entry.lomari || " ");
  lomariField.append(lomariLabel, lomari);

  const englishField = document.createElement("div");
  englishField.className = "reading-field english-field";
  const englishLabel = document.createElement("span");
  englishLabel.className = "field-label";
  englishLabel.textContent = "English";
  const english = document.createElement("span");
  english.className = "english-gloss";
  english.textContent = entry.english || " ";
  englishField.append(englishLabel, english);

  const actions = document.createElement("div");
  actions.className = "reading-actions";

  const audioSegments = normalizeAudioSegments(entry.audio);
  const missingAudio = entry.audio?.missing || [];
  const playButton = document.createElement("button");
  playButton.className = "audio-reading";
  playButton.type = "button";
  playButton.textContent = "Listen";
  playButton.setAttribute("aria-label", `Listen to ${normalizeApostrophes(entry.reading)}`);
  if (!audioSegments.length) {
    playButton.disabled = true;
    playButton.title = missingAudio.length ? `No audio for ${missingAudio.join(", ")}` : "No audio for this reading";
  }
  playButton.addEventListener("click", async () => {
    if (!audioSegments.length) {
      showToast(playButton.title);
      return;
    }
    try {
      await playAudioSequence(entry.audio, playButton);
      if (missingAudio.length) {
        showToast(`Missing audio: ${missingAudio.join(", ")}`);
      }
    } catch {
      playButton.classList.remove("playing");
      playButton.disabled = false;
      showToast("Could not play audio");
    }
  });

  const copyButton = document.createElement("button");
  copyButton.className = "copy-reading";
  copyButton.type = "button";
  copyButton.textContent = "Copy";
  copyButton.setAttribute("aria-label", `Copy ${normalizeApostrophes(entry.reading)} ${normalizeApostrophes(entry.lomari || "")}`.trim());
  copyButton.addEventListener("click", async () => {
    const value = entry.lomari
      ? `${normalizeApostrophes(entry.reading)}\t${normalizeApostrophes(entry.lomari)}`
      : normalizeApostrophes(entry.reading);
    try {
      await copyText(value);
      showToast("Reading copied");
    } catch {
      showToast("Could not copy reading");
    }
  });

  actions.append(playButton, copyButton);
  wrapper.append(lomariField, englishField, actions);
  return wrapper;
}

function paginationItems(page, totalPages) {
  if (totalPages <= 7) {
    return Array.from({ length: totalPages }, (_, index) => index + 1);
  }

  if (page <= 4) {
    return [1, 2, 3, 4, 5, "ellipsis", totalPages];
  }

  if (page >= totalPages - 3) {
    return [1, "ellipsis", totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages];
  }

  return [1, "ellipsis-before", page - 1, page, page + 1, "ellipsis-after", totalPages];
}

function renderPagination(page, totalPages) {
  pagination.replaceChildren();
  pagination.hidden = totalPages <= 1;
  if (totalPages <= 1) return;

  const makeButton = (label, nextPage, options = {}) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "page-button";
    button.textContent = label;
    button.disabled = options.disabled || false;
    if (options.current) {
      button.classList.add("current");
      button.setAttribute("aria-current", "page");
    }
    button.addEventListener("click", () => {
      state.currentPage = nextPage;
      renderResults();
      if (searchInput.value) searchInput.focus();
    });
    return button;
  };

  pagination.append(makeButton("<", Math.max(1, page - 1), { disabled: page === 1 }));
  for (const item of paginationItems(page, totalPages)) {
    if (typeof item === "number") {
      pagination.append(makeButton(String(item), item, { current: item === page }));
    } else {
      const ellipsis = document.createElement("span");
      ellipsis.className = "page-ellipsis";
      ellipsis.textContent = "...";
      pagination.append(ellipsis);
    }
  }
  pagination.append(makeButton(">", Math.min(totalPages, page + 1), { disabled: page === totalPages }));
}

function renderResults() {
  if (!state.loaded) return;

  const { rawQuery, shown, total, page, totalPages } = searchGroups();
  results.replaceChildren();
  clearButton.hidden = !searchInput.value;
  searchImeController?.renderCandidates();

  if (!rawQuery && !state.activeCategory) {
    summaryBar.hidden = true;
    pagination.hidden = true;
    pagination.replaceChildren();
    resultSummary.textContent = "";
    return;
  }

  summaryBar.hidden = false;

  if (!shown.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    const title = document.createElement("strong");
    title.textContent = "No matching entries yet";
    const note = document.createElement("span");
    note.textContent = state.activeCategory
      ? `No entries in ${activeCategoryLabel()} match this search.`
      : "Try Hanri, Tangliengim Hangul, Lomari, or English meanings.";
    empty.append(title, note);
    results.append(empty);
    resultSummary.textContent = "0 results";
    pagination.hidden = true;
    pagination.replaceChildren();
    return;
  }

  for (const group of shown) {
    const node = template.content.firstElementChild.cloneNode(true);
    const hanri = node.querySelector(".hanri");
    hanri.replaceChildren(renderEntryHeadword(group));
    node.querySelector(".entry-meta").textContent = `${visibleKind(group.kind)} · ${group.readings.length} reading${group.readings.length === 1 ? "" : "s"}`;
    const readings = node.querySelector(".readings");
    group.readings.slice(0, 8).forEach((entry) => readings.append(renderReading(entry)));
    if (group.readings.length > 8) {
      const more = document.createElement("div");
      more.className = "more-readings";
      more.textContent = `+${group.readings.length - 8} more readings`;
      readings.append(more);
    }
    results.append(node);
  }

  const rangeStart = (page - 1) * RESULTS_PER_PAGE + 1;
  const rangeEnd = rangeStart + shown.length - 1;
  const categoryPrefix = state.activeCategory ? `${activeCategoryLabel()} · ` : "";
  resultSummary.textContent = `${categoryPrefix}${total} result${total === 1 ? "" : "s"} · showing ${rangeStart}-${rangeEnd}`;
  renderPagination(page, totalPages);
}

function setInputMode(mode) {
  state.inputMode = mode === "lomari" ? "lomari" : "hanri-hangul";
  if (hangulKeyboardToggle) {
    hangulKeyboardToggle.setAttribute("aria-pressed", String(state.inputMode === "hanri-hangul"));
  }
  searchInput.placeholder = "Type 漢字, 한글, Lomari, or English...";
  searchInput.classList.toggle("hangul-ime-active", state.inputMode === "hanri-hangul");
  searchImeController?.setEnabled();
  state.currentPage = 1;
  renderResults();
}

async function loadDictionary() {
  try {
    const response = await fetch(DATA_URL, { cache: "no-cache" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    state.entries = data.entries || [];
    state.dictionaryIndex = createDictionaryIndex(state.entries);
    state.categories = data.categories || [];
    state.groups = groupEntries(state.entries);
    searchImeController?.setEntries(state.entries, state.dictionaryIndex);
    state.loaded = true;
    dataStatus.textContent = `${data.counts?.active_entries || state.entries.length} active TSV entries`;
    renderCategoryFilters();
    renderResults();
  } catch (error) {
    state.loaded = true;
    dataStatus.textContent = "Dictionary failed to load";
    summaryBar.hidden = false;
    pagination.hidden = true;
    resultSummary.textContent = "The dictionary could not load. Please refresh and try again.";
    results.replaceChildren();
    const empty = document.createElement("div");
    empty.className = "empty-state error";
    empty.textContent = `Could not load dictionary data: ${error.message}`;
    results.append(empty);
  }
}

searchImeController = createTextImeController({
  control: searchInput,
  candidateContainer: imeCandidates,
  dictionaryIndex: state.dictionaryIndex,
  enabled: () => state.inputMode === "hanri-hangul",
  onUpdate: () => {
    state.currentPage = 1;
    renderResults();
  },
  onCandidatesChanged: searchCandidatePopup.schedule,
  enterBehavior: "none",
});

clearButton.addEventListener("click", () => {
  searchImeController?.clear();
  state.currentPage = 1;
  renderResults();
});
hangulKeyboardToggle?.addEventListener("click", () => {
  setInputMode(state.inputMode === "hanri-hangul" ? "lomari" : "hanri-hangul");
  searchInput.focus();
});

loadDictionary();
setInputMode("lomari");
