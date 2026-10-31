const INDEX_URL = "/public/data/site-search-index.json";
const RESULTS_PER_PAGE = 10;
const language = document.documentElement.lang || "en";

const localizedMessages = {
  en: {
    all: "All", page: "Pages", guide: "Learning", song: "Songs", story: "Stories", tool: "Tools",
    initial: "Enter a word or phrase to search the website.", loading: "Loading website search...",
    noResults: "No matching pages found.", result: "result", results: "results", showing: "showing",
    error: "Website search could not load. Please refresh and try again.", previous: "Previous page", next: "Next page",
  },
  "zh-Hant": {
    all: "全部", page: "頁面", guide: "學習", song: "歌曲", story: "故事", tool: "工具",
    initial: "輸入詞語或句子以搜尋網站。", loading: "正在載入網站搜尋…",
    noResults: "找不到相符頁面。", result: "個結果", results: "個結果", showing: "顯示",
    error: "無法載入網站搜尋，請重新整理後再試。", previous: "上一頁", next: "下一頁",
  },
  "zh-Hans": {
    all: "全部", page: "页面", guide: "学习", song: "歌曲", story: "故事", tool: "工具",
    initial: "输入词语或句子以搜索网站。", loading: "正在加载网站搜索…",
    noResults: "找不到匹配页面。", result: "个结果", results: "个结果", showing: "显示",
    error: "无法加载网站搜索，请刷新后重试。", previous: "上一页", next: "下一页",
  },
};
const messages = localizedMessages[language] || localizedMessages.en;

const state = { documents: [], hanriFold: {}, kind: "all", page: 1, loaded: false };
const variants = window.TliSiteSearchVariants;
const input = document.querySelector("#siteSearchInput");
const clear = document.querySelector("#siteSearchClear");
const hangulKeyboardToggle = document.querySelector("#hangulKeyboardToggle");
const filters = document.querySelector("#siteSearchFilters");
const summary = document.querySelector("#siteSearchSummary");
const results = document.querySelector("#siteSearchResults");
const pagination = document.querySelector("#siteSearchPagination");
let hangulKeyboardEnabled = false;
const searchImeController = window.TangliengimImeCore.createTextImeController({
  control: input,
  entries: [],
  enabled: () => hangulKeyboardEnabled,
  onUpdate: () => {
    state.page = 1;
    render();
  },
  enterBehavior: "none",
});

function normalized(value, loose = false) {
  const text = String(value || "").normalize("NFKC").toLocaleLowerCase()
    .replace(/[’‘ʼ]/g, "'").replace(/\s+/g, " ").trim();
  return loose ? text.normalize("NFD").replace(/[\u0300-\u036f]/g, "") : text;
}

function terms(value) {
  return normalized(value).split(" ").filter(Boolean);
}

function score(document, queryTerms) {
  const title = normalized(document.titleSearch);
  const body = normalized(document.content);
  const looseTitle = normalized(document.titleSearch, true);
  const looseBody = normalized(document.content, true);
  let total = 0;
  for (const term of queryTerms) {
    const looseTerm = normalized(term, true);
    if (title === term) total += 320;
    else if (title.startsWith(term)) total += 240;
    else if (title.includes(term)) total += 180;
    else if (body.includes(term)) total += 80;
    else if (looseTitle.includes(looseTerm)) total += 130;
    else if (looseBody.includes(looseTerm)) total += 55;
    else if (document.foldedTitle.includes(variants.fold(term, state.hanriFold))) total += 125;
    else if (document.foldedContent.includes(variants.fold(term, state.hanriFold))) total += 50;
    else return 0;
  }
  return total;
}

function matches() {
  const queryTerms = terms(input.value);
  if (!queryTerms.length) return [];
  return state.documents
    .filter(document => state.kind === "all" || document.kind === state.kind)
    .map(document => ({ document, score: score(document, queryTerms) }))
    .filter(match => match.score > 0)
    .sort((a, b) => b.score - a.score || a.document.title.localeCompare(b.document.title, language));
}

function excerpt(value, queryTerms) {
  const collapsed = String(value || "").replace(/\s+/g, " ").trim();
  const lower = collapsed.toLocaleLowerCase();
  const positions = queryTerms.map(term => {
    const exact = lower.indexOf(term.toLocaleLowerCase());
    return exact >= 0 ? exact : (variants.match(collapsed, term, state.hanriFold)?.index ?? -1);
  }).filter(index => index >= 0);
  const center = positions.length ? Math.min(...positions) : 0;
  const start = Math.max(0, center - 85);
  const end = Math.min(collapsed.length, Math.max(center + 155, start + 240));
  return { text: collapsed.slice(start, end), before: start > 0, after: end < collapsed.length };
}

function highlightedText(value, queryTerms) {
  const fragment = document.createDocumentFragment();
  const candidates = [...new Set(queryTerms)].sort((a, b) => b.length - a.length);
  let offset = 0;
  while (offset < value.length) {
    let found = null;
    for (const term of candidates) {
      const part = value.slice(offset);
      const index = part.toLocaleLowerCase().indexOf(term.toLocaleLowerCase());
      const hit = index >= 0 ? {index, length:term.length} : variants.match(part, term, state.hanriFold);
      if (hit && (!found || offset + hit.index < found.index || offset + hit.index === found.index && hit.length > found.length)) {
        found = { index:offset + hit.index, length:hit.length };
      }
    }
    if (!found) {
      fragment.append(document.createTextNode(value.slice(offset)));
      break;
    }
    if (found.index > offset) fragment.append(document.createTextNode(value.slice(offset, found.index)));
    const mark = document.createElement("mark");
    mark.textContent = value.slice(found.index, found.index + found.length);
    fragment.append(mark);
    offset = found.index + found.length;
  }
  return fragment;
}

function renderFilters() {
  filters.replaceChildren();
  for (const kind of ["all", "page", "guide", "song", "story", "tool"]) {
    const count = kind === "all" ? state.documents.length : state.documents.filter(item => item.kind === kind).length;
    if (!count) continue;
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `${messages[kind]} ${count}`;
    button.setAttribute("aria-pressed", String(state.kind === kind));
    button.addEventListener("click", () => {
      state.kind = kind;
      state.page = 1;
      renderFilters();
      render();
    });
    filters.append(button);
  }
}

function pageButton(label, page, options = {}) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  if (options.label) button.setAttribute("aria-label", options.label);
  if (options.current) button.setAttribute("aria-current", "page");
  button.disabled = options.disabled || false;
  button.addEventListener("click", () => {
    state.page = page;
    render();
    document.querySelector("#siteSearchSummary").scrollIntoView({ behavior: "smooth", block: "start" });
  });
  return button;
}

function renderPagination(totalPages) {
  pagination.replaceChildren();
  pagination.hidden = totalPages <= 1;
  if (totalPages <= 1) return;
  pagination.append(pageButton("‹", state.page - 1, { label: messages.previous, disabled: state.page === 1 }));
  const pages = new Set([1, totalPages, state.page - 1, state.page, state.page + 1].filter(page => page >= 1 && page <= totalPages));
  let previous = 0;
  for (const page of [...pages].sort((a, b) => a - b)) {
    if (page - previous > 1) {
      const ellipsis = document.createElement("span");
      ellipsis.textContent = "…";
      ellipsis.setAttribute("aria-hidden", "true");
      pagination.append(ellipsis);
    }
    pagination.append(pageButton(String(page), page, { current: page === state.page }));
    previous = page;
  }
  pagination.append(pageButton("›", state.page + 1, { label: messages.next, disabled: state.page === totalPages }));
}

function setQueryUrl() {
  const url = new URL(location.href);
  if (input.value.trim()) url.searchParams.set("q", input.value.trim());
  else url.searchParams.delete("q");
  if (state.kind !== "all") url.searchParams.set("type", state.kind);
  else url.searchParams.delete("type");
  if (state.page > 1) url.searchParams.set("page", String(state.page));
  else url.searchParams.delete("page");
  history.replaceState(null, "", url.pathname + url.search);
}

function render() {
  results.replaceChildren();
  clear.hidden = !input.value;
  if (!state.loaded) return;
  const queryTerms = terms(input.value);
  if (!queryTerms.length) {
    summary.textContent = messages.initial;
    pagination.hidden = true;
    setQueryUrl();
    return;
  }
  const found = matches();
  const totalPages = Math.ceil(found.length / RESULTS_PER_PAGE);
  state.page = totalPages ? Math.min(Math.max(state.page, 1), totalPages) : 1;
  const start = (state.page - 1) * RESULTS_PER_PAGE;
  const shown = found.slice(start, start + RESULTS_PER_PAGE);
  if (!found.length) summary.textContent = messages.noResults;
  else {
    const unit = found.length === 1 ? messages.result : messages.results;
    summary.textContent = `${found.length} ${unit} · ${messages.showing} ${start + 1}–${start + shown.length}`;
  }
  for (const { document: item } of shown) {
    const article = document.createElement("article");
    article.className = "site-search-result";
    const meta = document.createElement("span");
    meta.className = "site-search-result-kind";
    meta.textContent = messages[item.kind] || item.kind;
    const heading = document.createElement("h2");
    const link = document.createElement("a");
    link.href = item.url;
    link.append(highlightedText(item.title, queryTerms));
    heading.append(link);
    const snippet = excerpt(item.content, queryTerms);
    const paragraph = document.createElement("p");
    if (snippet.before) paragraph.append("…");
    paragraph.append(highlightedText(snippet.text, queryTerms));
    if (snippet.after) paragraph.append("…");
    article.append(meta, heading, paragraph);
    results.append(article);
  }
  renderPagination(totalPages);
  setQueryUrl();
}

input.addEventListener("input", () => { state.page = 1; render(); });
document.querySelector("#siteSearchForm").addEventListener("submit", event => { event.preventDefault(); render(); });
clear.addEventListener("click", () => { state.page = 1; searchImeController.clear(); });
hangulKeyboardToggle.addEventListener("click", () => {
  hangulKeyboardEnabled = !hangulKeyboardEnabled;
  hangulKeyboardToggle.setAttribute("aria-pressed", String(hangulKeyboardEnabled));
  input.classList.toggle("hangul-ime-active", hangulKeyboardEnabled);
  searchImeController.setEnabled();
  input.focus();
});

async function load() {
  summary.textContent = messages.loading;
  try {
    const response = await fetch(INDEX_URL);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const index = await response.json();
    state.hanriFold = index.hanriFold || {};
    state.documents = (index.languages[language] || []).map(document => ({
      ...document,
      foldedTitle: variants.fold(normalized(document.titleSearch), state.hanriFold),
      foldedContent: variants.fold(normalized(document.content), state.hanriFold),
    }));
    const params = new URLSearchParams(location.search);
    input.value = params.get("q") || "";
    searchImeController.composer.setText(input.value, input.value.length);
    searchImeController.updateControlFromComposer({ allowCandidateMenu: false });
    const requestedKind = params.get("type") || "all";
    state.kind = ["all", "page", "guide", "song", "story", "tool"].includes(requestedKind) ? requestedKind : "all";
    state.page = Math.max(1, Number.parseInt(params.get("page"), 10) || 1);
    state.loaded = true;
    renderFilters();
    render();
  } catch (error) {
    console.error(error);
    summary.textContent = messages.error;
  }
}

load();
