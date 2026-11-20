const DATA_URL = "/public/data/hokkien-hanri-dict.json";
// Filled with content hashes by tools/build_site.py; unbuilt checkouts revalidate.
const DATA_VERSIONS = {};

async function fetchDictionaryJson(url) {
  const version = DATA_VERSIONS[url];
  const response = await (version ? fetch(`${url}?v=${version}`) : fetch(url, { cache: "no-cache" }));
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}
const siteText = window.TliSiteLanguage?.text || (value => value);
const RESULTS_PER_PAGE = 10;
const ImeCore = window.TangliengimImeCore;
const webAudio = window.TangliengimWebAudio;
const {
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

const summaryBar = document.querySelector("#summaryBar");
const resultSummary = document.querySelector("#resultSummary");
const dataStatus = document.querySelector("#dataStatus");
const results = document.querySelector("#results");
const template = document.querySelector("#resultTemplate");
const pagination = document.querySelector("#pagination");
const categoryFilters = document.querySelector("#categoryFilters");
const audioPlayer = webAudio.createPlayer();
const normalizeAudioSegments = webAudio.normalizeAudioSegments;
// The search box (keyboard switch, clear button, candidate menu, IME and ?q=) is the shared one; this
// page learns of a change of query or of keyboard mode. It hands the box its dictionary once loaded.
let resolveDictionary;
const dictionaryLoaded = new Promise(resolve => { resolveDictionary = resolve; });
const searchBox = window.TliSearchBox.mount(document.querySelector(".search-panel [data-tli-search]"), {
  keyboardMode: "modes",
  queryParam: "q",
  entries: dictionaryLoaded,
  onChange: () => {
    state.currentPage = 1;
    renderResults();
  },
  onModeChange: mode => {
    state.inputMode = mode;
    state.currentPage = 1;
    renderResults();
  },
});
const searchInput = searchBox.input;
const imeCandidates = searchBox.candidates;
let searchImeController = null;
searchBox.ready.then(controller => { searchImeController = controller; }, () => {});

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
        canonicalEntry: entry,
        readings: [],
        categories: [],
        search: {
          hanri: normalizeText(headword),
          simplified: normalizeText(ImeCore.stripLegacyInlineToneMarks(entry.simplified || "")),
          simplifiedRaw: normalizeText(entry.simplified || ""),
          mandarinTrad: "",
          mandarinSimp: "",
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
    if (ImeCore.compareCanonicalEntries(entry,group.canonicalEntry)<0) group.canonicalEntry = entry;
    group.readings.push(entry);
  }

  const groups = [...byHeadwordReading.values()];
  for (const group of groups) {
    group.readings.sort((a, b) =>
      ImeCore.compareCanonicalEntries(a,b)
    );
    group.categories = [...new Set(group.readings.flatMap((item) => item.categories || []))];
    group.search.reading = normalizeText(group.readings.flatMap((item) => [item.reading, ...(item.readingAliases || [])]).join(" "));
    group.search.headwordAliases = normalizeText(group.readings.flatMap((item) => item.headwordAliases || []).join(" "));
    group.search.readingBase = normalizeText(group.readings.flatMap((item) => [item.readingBase,
      ...(item.readingAliases || []).map(value => TangliengimHangulIme.normalizeReadingBase(value))]).join(" "));
    group.search.lomari = normalizeText(group.readings.map((item) => item.lomari).join(" "));
    group.search.lomariAliases = normalizeLomariSearchAliases(group.readings.map((item) => item.lomari).join(" "));
    group.search.english = normalizeEnglishSearch(group.readings.map((item) => item.english || "").join(" "));
    group.search.mandarinTrad = normalizeText(group.readings.map((item) => item.mandarin_trad || "").join(" "));
    group.search.mandarinSimp = normalizeText(group.readings.map((item) => item.mandarin_simp || "").join(" "));
    group.search.all = [
      group.search.hanri,
      group.search.headwordAliases,
      group.search.simplified,
      group.search.simplifiedRaw,
      group.search.mandarinTrad,
      group.search.mandarinSimp,
      group.search.reading,
      group.search.readingBase,
      group.search.lomari,
      group.search.lomariAliases,
      group.search.english,
      normalizeText(group.readings.map((item) => item.raw?.reading || "").join(" ")),
    ].join(" ");
  }

  return groups.sort((a, b) => ImeCore.compareCanonicalEntries(a.canonicalEntry,b.canonicalEntry));
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
    { name: "headwordAliases", boost: 6 },
    { name: "simplified", boost: mode === "hanri-hangul" ? 6 : 0 },
    { name: "simplifiedRaw", boost: mode === "hanri-hangul" ? 6 : 0 },
    { name: "mandarinTrad", boost: 0 },
    { name: "mandarinSimp", boost: 0 },
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
      ImeCore.compareCanonicalEntries(a.group.canonicalEntry,b.group.canonicalEntry)
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
  return siteText(state.categories.find((category) => category.id === state.activeCategory)?.label || "");
}

function renderCategoryFilters() {
  categoryFilters.replaceChildren();
  for (const category of state.categories) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "category-button";
    button.textContent = siteText(category.label);
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

function appendHanriRuby(fragment, hanriText, readingText, varies = null) {
  if (!readingText) {
    fragment.append(displayTextNode(hanriText));
    return;
  }

  const ruby = document.createElement("span");
  ruby.className = "entry-headword-ruby";
  const base = document.createElement("span");
  base.className = "entry-headword-base";
  base.append(displayTextNode(hanriText));
  const rt = document.createElement("span");
  rt.className = "entry-headword-reading";
  rt.append(renderInlineUpperToneReading(readingText, varies));
  ruby.append(base, rt);
  fragment.append(ruby);
}

function renderMixedEntryHeadword(group, reading, varies = null) {
  const fragment = document.createDocumentFragment();
  const source = String(group.hanri || "");
  let sourceIndex = 0;
  let readingIndex = 0;

  while (sourceIndex < source.length) {
    const unit = headwordUnitAt(source, sourceIndex);
    if (!unit) break;

    if (unit.kind === "hanri") {
      const boundary = findNextMixedReadingBoundary(source, unit.end, reading, readingIndex);
      appendHanriRuby(fragment, unit.text, reading.slice(readingIndex, boundary), variesFrom(varies, readingIndex, boundary));
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
  const storedReading = group.readings[0]?.reading || group.hanri || "";
  const primaryReading = shownReading(storedReading);
  const varies = readingVaries(storedReading);

  if (group.kind === "hangul_override") {
    const hangul = document.createElement("span");
    hangul.className = "entry-headword-hangul";
    hangul.append(renderToneMarkedReading(primaryReading, varies));
    fragment.append(hangul);
    return fragment;
  }

  if (group.kind === "mixed_hanri") {
    fragment.append(renderMixedEntryHeadword(group, primaryReading, varies));
    return fragment;
  }

  const ruby = document.createElement("span");
  ruby.className = "entry-headword-ruby";
  const base = document.createElement("span");
  base.className = "entry-headword-base";
  base.append(displayTextNode(group.hanri));
  const rt = document.createElement("span");
  rt.className = "entry-headword-reading";
  rt.append(renderInlineUpperToneReading(primaryReading, varies));
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

  toast.textContent = siteText(message);
  toast.classList.add("visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("visible"), 1500);
}

// The site-wide Taipei/Singapore preference (shared/web-sandhi-preference.js). Stored readings keep
// Taipei sandhi digits; with Singapore, a reading and its Lomari are shown (and copied) with an open
// sandhi tone 1 as 4 (shared/web-sandhi-display.js), and the entry's Singapore clips play.
const singaporeShown = () => window.TliSandhiPreference?.get() === "singapore" && window.TliSandhiDisplay;
function shownReading(reading) {
  return singaporeShown() ? window.TliSandhiDisplay.singaporeReading(reading) : reading;
}
// The tone marks that differ between Taipei and Singapore, coloured in both modes.
function readingVaries(reading) {
  const display = window.TliSandhiDisplay;
  return display ? display.variesIndexes(reading, display.singaporeReading(reading)) : null;
}
function variesFrom(varies, start, end) {
  if (!varies) return null;
  return new Set([...varies].filter(index => index >= start && index < end).map(index => index - start));
}
function lomariShownParts(lomari) {
  const text = normalizeApostrophes(lomari);
  const display = window.TliSandhiDisplay;
  if (!display) return [text];
  return display.lomariParts(text, Boolean(singaporeShown())).map(part => {
    if (!part.varies) return part.text;
    return display.lomariToneSpan(part.text); // only the tone accent is coloured
  });
}
function shownLomari(lomari) {
  return singaporeShown() ? window.TliSandhiDisplay.singaporeLomari(lomari).normalize("NFC") : lomari;
}

function audioForPreference(entry) {
  return TangliengimPhoneticOutput.audioForSandhiMode(entry.audio, window.TliSandhiPreference?.get());
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
  lomariLabel.textContent = siteText("Lomari");
  const lomari = document.createElement("span");
  lomari.className = "lomari";
  lomari.replaceChildren(...lomariShownParts(entry.lomari || " "));
  lomariField.append(lomariLabel, lomari);

  const englishField = document.createElement("div");
  englishField.className = "reading-field english-field";
  const englishLabel = document.createElement("span");
  englishLabel.className = "field-label";
  englishLabel.textContent = siteText("English");
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
  playButton.textContent = siteText("Listen");
  const reading = shownReading(entry.reading);
  const lomariText = shownLomari(entry.lomari || "");
  playButton.setAttribute("aria-label", `${siteText("Listen to")} ${normalizeApostrophes(reading)}`);
  if (!audioSegments.length) {
    playButton.disabled = true;
    playButton.title = missingAudio.length ? `${siteText("No audio for")} ${missingAudio.join(", ")}` : siteText("No audio for this reading");
  }
  playButton.addEventListener("click", async () => {
    if (!audioSegments.length) {
      showToast(playButton.title);
      return;
    }
    try {
      await playAudioSequence(audioForPreference(entry), playButton);
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
  copyButton.textContent = siteText("Copy");
  copyButton.setAttribute("aria-label", `${siteText("Copy")} ${normalizeApostrophes(reading)} ${normalizeApostrophes(lomariText)}`.trim());
  copyButton.addEventListener("click", async () => {
    const value = lomariText
      ? `${normalizeApostrophes(reading)}\t${normalizeApostrophes(lomariText)}`
      : normalizeApostrophes(reading);
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
  searchBox.renderCandidates();

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
    title.textContent = siteText("No matching entries yet");
    const note = document.createElement("span");
    note.textContent = state.activeCategory
      ? siteText(`No entries in ${activeCategoryLabel()} match this search.`)
      : siteText("Try Hanri, Tangliengim Hangul, Lomari, or English meanings.");
    empty.append(title, note);
    results.append(empty);
    resultSummary.textContent = siteText("0 results");
    pagination.hidden = true;
    pagination.replaceChildren();
    return;
  }

  for (const group of shown) {
    const node = template.content.firstElementChild.cloneNode(true);
    const hanri = node.querySelector(".hanri");
    hanri.replaceChildren(renderEntryHeadword(group));
    node.querySelector(".entry-meta").textContent = siteText(`${visibleKind(group.kind)} · ${group.readings.length} reading${group.readings.length === 1 ? "" : "s"}`);
    const readings = node.querySelector(".readings");
    group.readings.slice(0, 8).forEach((entry) => readings.append(renderReading(entry)));
    if (group.readings.length > 8) {
      const more = document.createElement("div");
      more.className = "more-readings";
      more.textContent = siteText(`+${group.readings.length - 8} more readings`);
      readings.append(more);
    }
    results.append(node);
  }

  const rangeStart = (page - 1) * RESULTS_PER_PAGE + 1;
  const rangeEnd = rangeStart + shown.length - 1;
  const categoryPrefix = state.activeCategory ? `${activeCategoryLabel()} · ` : "";
  resultSummary.textContent = siteText(`${categoryPrefix}${total} result${total === 1 ? "" : "s"} · showing ${rangeStart}-${rangeEnd}`);
  renderPagination(page, totalPages);
}

// Readings follow the Taipei/Singapore preference, so a change redraws them.
window.TliSandhiPreference?.onChange(() => renderResults());

function setInputMode(mode) {
  searchBox.setMode(mode === "lomari" ? "lomari" : "hanri-hangul");
}

async function loadDictionary() {
  try {
    const data = await fetchDictionaryJson(DATA_URL);
    state.entries = data.entries || [];
    state.dictionaryIndex = createDictionaryIndex(state.entries);
    state.categories = data.categories || [];
    state.groups = groupEntries(state.entries);
    resolveDictionary({ entries: state.entries, index: state.dictionaryIndex });
    state.loaded = true;
    dataStatus.textContent = siteText(`${data.counts?.active_entries || state.entries.length} active TSV entries`);
    renderCategoryFilters();
    renderResults();
  } catch (error) {
    resolveDictionary({ entries: [], index: null });
    state.loaded = true;
    dataStatus.textContent = siteText("Dictionary failed to load");
    summaryBar.hidden = false;
    pagination.hidden = true;
    resultSummary.textContent = siteText("The dictionary could not load. Please refresh and try again.");
    results.replaceChildren();
    const empty = document.createElement("div");
    empty.className = "empty-state error";
    empty.textContent = `Could not load dictionary data: ${error.message}`;
    results.append(empty);
  }
}

loadDictionary();
