"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const token = document.querySelector('meta[name="editor-token"]').content;
  const state = { screen: "dashboard", pages: [], page: null, pageDirty: false, tables: null,
    entries: [], entryById: new Map(), changes: null, validation: null, picker: null, job: null };

  async function request(action, payload = {}) {
    const response = await fetch("/desktop-api/website-editor/" + action, {
      method: "POST", cache: "no-store", signal: AbortSignal.timeout(60000),
      headers: { "Content-Type": "application/json", "X-Tangliengim-Editor": token },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok || !result.ok) throw Object.assign(new Error(result.error || `HTTP ${response.status}`), result);
    return result;
  }
  function notice(message, error = false) {
    const node = $("notice"); node.textContent = message; node.hidden = !message; node.classList.toggle("error", error);
  }
  function text(tag, value, className = "") {
    const node = document.createElement(tag); node.textContent = value; if (className) node.className = className; return node;
  }
  function input(value = "", type = "text") { const node = document.createElement("input"); node.type = type; node.value = value; return node; }
  function button(label, action, className = "") {
    const node = document.createElement("button"); node.type = "button"; node.textContent = label; node.className = className;
    node.addEventListener("click", action); return node;
  }
  function currentPageDraft() { return { title: $("pageTitle").value, body: $("pageBody").value }; }
  function mayLeavePage() { return !state.pageDirty || window.confirm("Discard the unsaved page draft?"); }

  async function showScreen(name) {
    if (state.screen === "pages" && name !== "pages" && !mayLeavePage()) return;
    state.screen = name;
    document.querySelectorAll(".screen").forEach(node => node.classList.toggle("active", node.id === "screen-" + name));
    document.querySelectorAll(".nav-item").forEach(node => node.classList.toggle("active", node.dataset.screen === name));
    if (name === "dashboard") await loadDashboard();
    if (name === "pages" && !state.pages.length) await loadPages();
    if (name === "dictionary" && !$("dictionaryFrame").src) $("dictionaryFrame").src = $("dictionaryFrame").dataset.src;
    if (["references", "priority"].includes(name) && !state.tables) await loadTables();
    if (name === "changes") await loadChanges();
  }

  async function loadDashboard() {
    try {
      const result = await request("summary");
      $("pageCount").textContent = result.pages;
      $("entryCount").textContent = result.entries.toLocaleString();
      $("changeCount").textContent = result.changes;
      $("branchStatus").textContent = result.branch || "Repository ready";
      state.validation = result.validation;
      $("validationMark").textContent = result.validation ? "✓" : "?";
    } catch (error) { notice(error.message, true); }
  }

  async function loadPages() {
    try {
      const result = await request("pages"); state.pages = result.pages;
      const types = [...new Set(state.pages.map(page => page.type))].sort();
      $("pageType").replaceChildren(new Option("All content", ""), ...types.map(value => new Option(value, value)));
      renderPageList();
    } catch (error) { notice(error.message, true); }
  }
  function renderPageList() {
    const query = $("pageSearch").value.trim().toLocaleLowerCase(); const type = $("pageType").value;
    const pages = state.pages.filter(page => (!type || page.type === type) &&
      (!query || `${page.title} ${page.route} ${page.language}`.toLocaleLowerCase().includes(query)));
    $("pageList").replaceChildren(...pages.map(page => {
      const node = button("", () => selectPage(page.file)); node.classList.toggle("active", state.page?.file === page.file);
      node.append(text("span", page.title), text("small", `${page.language} · ${page.route || page.file}`)); return node;
    }));
  }
  async function selectPage(file) {
    if (state.pageDirty && !mayLeavePage()) return;
    try {
      const result = await request("page", { file }); state.page = result; state.pageDirty = false;
      $("pageEmpty").hidden = true; $("pageForm").hidden = false; $("savePage").disabled = false;
      $("pageTitle").value = result.page.title || ""; $("pageRoute").value = result.page.route || "";
      $("pageBody").value = result.page.body || ""; $("pageLanguage").textContent = result.page.language || "en";
      $("pageKind").textContent = result.page.type || "page"; $("pageFile").textContent = result.file;
      $("openBuiltPreview").disabled = !result.page.route;
      $("editLyricTiming").hidden = result.page.type !== 'songs';
      renderPageList(); updatePreview();
    } catch (error) { notice(error.message, true); }
  }
  function escapeHtml(value) { return String(value).replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[char]); }
  function updatePreview() {
    if (!state.page) { $("pagePreview").srcdoc = ""; return; }
    const draft = currentPageDraft(); const kind = state.page.page.type || "pages";
    $("pagePreview").srcdoc = `<!doctype html><html lang="${escapeHtml(state.page.page.language || "en")}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><base href="/"><link rel="stylesheet" href="/shared/web-title-reading.css"><link rel="stylesheet" href="/preview-assets/site.css"></head><body data-site-section="${escapeHtml(kind)}"><main class="content-shell content-${escapeHtml(kind)}"><h1 class="title-reading">${escapeHtml(draft.title)}</h1><article class="imported-content">${draft.body}</article></main><script src="/shared/web-ime-core.js"><\/script><script src="/preview-assets/site.js"><\/script></body></html>`;
  }
  async function validatePage() {
    if (!state.page) return;
    try { const result = await request("validate-page", currentPageDraft()); notice(result.message); updatePreview(); }
    catch (error) { notice(error.message, true); }
  }
  async function savePage() {
    if (!state.page) return;
    try {
      const result = await request("save-page", { file: state.page.file, revision: state.page.revision, ...currentPageDraft() });
      state.page.revision = result.revision; state.page.page = result.page; state.pageDirty = false;
      const listed = state.pages.find(page => page.file === state.page.file); if (listed) listed.title = result.page.title;
      renderPageList(); notice(result.message);
    } catch (error) { notice(error.message, true); }
  }

  async function loadTables() {
    try {
      state.tables = await request("tables"); state.entries = state.tables.entries;
      state.entryById = new Map(state.entries.map(entry => [entry.entry_id, entry]));
      renderCategories(); renderReferences(); renderPriorities();
    } catch (error) { notice(error.message, true); }
  }
  function entryLabel(identity) {
    const entry = state.entryById.get(identity); return entry ? `${entry.hanri} · ${entry.reading}` : identity || "Choose entry";
  }
  function chooseEntry(callback, selected = "") {
    state.picker = callback; $("entryPickerSearch").value = entryLabel(selected); renderPicker(); $("entryPicker").showModal();
    setTimeout(() => { $("entryPickerSearch").select(); }, 0);
  }
  function renderPicker() {
    const query = $("entryPickerSearch").value.trim().toLocaleLowerCase();
    const matches = state.entries.filter(entry => !query || `${entry.hanri} ${entry.reading} ${entry.english} ${entry.entry_id}`.toLocaleLowerCase().includes(query)).slice(0, 80);
    $("entryPickerResults").replaceChildren(...matches.map(entry => {
      const node = button("", () => { state.picker?.(entry.entry_id); $("entryPicker").close(); });
      node.append(text("strong", entry.hanri), text("span", entry.reading), text("small", entry.english || "No English gloss"), text("small", entry.entry_id)); return node;
    }));
  }

  function renderCategories() {
    const data = state.tables.categories;
    $("categoryLabels").replaceChildren(...data.labels.map((row, index) => {
      const line = document.createElement("div"); line.className = "data-row";
      const key = input(row.category); key.readOnly = row.count > 0; key.title = row.count ? "Used category keys remain stable" : "Category key";
      key.addEventListener("input", () => row.category = key.value);
      const label = input(row.label); label.addEventListener("input", () => row.label = label.value);
      line.append(key, label, button("Remove", () => { if (row.count && !confirm(`Remove ${row.count} memberships too?`)) return; data.memberships = data.memberships.filter(item => item.category !== row.category); data.labels.splice(index, 1); renderCategories(); })); return line;
    }));
    $("categoryMemberships").replaceChildren(...data.memberships.map((row, index) => {
      const line = document.createElement("div"); line.className = "data-row membership-row";
      const category = document.createElement("select"); data.labels.forEach(item => category.add(new Option(item.label, item.category)));
      category.value = row.category; category.addEventListener("change", () => row.category = category.value);
      const target = button(entryLabel(row.entry_id), () => chooseEntry(id => { row.entry_id = id; target.textContent = entryLabel(id); })); target.className = "entry-choice";
      line.append(category, target, text("code", row.entry_id), button("Remove", () => { data.memberships.splice(index, 1); renderCategories(); })); return line;
    }));
  }
  function renderReferences() {
    const rows = state.tables.references.rows;
    $("referenceRows").replaceChildren(...rows.map((row, index) => {
      const line = document.createElement("div"); line.className = "structured-row reference-row";
      const main = document.createElement("div"); main.className = "reference-main";
      const metadata = document.createElement("div"); metadata.className = "reference-metadata";
      const kind = document.createElement("select"); kind.add(new Option("Headword", "headword")); kind.add(new Option("Reading", "reading")); kind.value = row.kind; kind.onchange = () => row.kind = kind.value;
      const source = input(row.source); source.placeholder = "Source form"; source.oninput = () => row.source = source.value;
      const reading = input(row.source_reading); reading.placeholder = "Source reading"; reading.oninput = () => row.source_reading = reading.value;
      const target = button(entryLabel(row.target_entry_id), () => chooseEntry(id => { row.target_entry_id = id; target.textContent = entryLabel(id); })); target.className = "entry-choice";
      const reason = input(row.reason); reason.placeholder = "Reason"; reason.oninput = () => row.reason = reason.value;
      const sources = input(row.sources); sources.placeholder = "Sources"; sources.oninput = () => row.sources = sources.value;
      const date = input(row.date); date.placeholder = "Date"; date.oninput = () => row.date = date.value;
      main.append(kind, source, reading, target, reason, button("Remove", () => { rows.splice(index, 1); renderReferences(); }));
      metadata.append(text("span", "Reference details"), sources, date);
      line.append(main, metadata); return line;
    }));
  }
  function renderPriorities() {
    const rows = state.tables.priorities.rows;
    $("priorityRows").replaceChildren(...rows.map((row, index) => {
      const line = document.createElement("div"); line.className = "structured-row";
      const key = input(row.lookup_key); key.placeholder = "Lookup key"; key.oninput = () => row.lookup_key = key.value;
      const target = button(entryLabel(row.entry_id), () => chooseEntry(id => { row.entry_id = id; target.textContent = entryLabel(id); })); target.className = "entry-choice";
      const identity = text("code", row.entry_id);
      const rank = input(row.rank, "number"); rank.min = "1"; rank.oninput = () => row.rank = rank.value;
      line.append(key, target, identity, rank, button("Remove", () => { rows.splice(index, 1); renderPriorities(); })); return line;
    }));
  }
  async function saveTable(action, payload, refreshMessage) {
    try { const result = await request(action, payload); notice(result.message); state.tables = null; await loadTables(); notice(refreshMessage || result.message); }
    catch (error) { notice(error.message, true); }
  }

  async function loadChanges() {
    try {
      state.changes = await request("changes"); $("branchStatus").textContent = state.changes.branch || "Repository ready";
      const files = state.changes.files; $("changeFiles").replaceChildren(...files.map((file, index) => {
        const row = document.createElement("label"); row.className = "change-file"; row.dataset.index = index;
        const check = document.createElement("input"); check.type = "checkbox"; check.checked = !file.generated;
        check.addEventListener("click", event => event.stopPropagation());
        row.append(check, text("span", file.status, "change-status"), text("code", file.path + (file.generated ? " (generated)" : "")));
        row.addEventListener("click", () => showDiff(index)); return row;
      }));
      if (files.length) showDiff(0); else { $("diffTitle").textContent = "Working tree is clean"; $("diffContent").textContent = "No uncommitted changes."; }
    } catch (error) { notice(error.message, true); }
  }
  function showDiff(index) {
    document.querySelectorAll(".change-file").forEach((node, position) => node.classList.toggle("active", position === index));
    const file = state.changes.files[index]; $("diffTitle").textContent = `${file.status} ${file.path}`; $("diffContent").textContent = file.diff || "No textual diff available.";
  }
  async function commitChanges() {
    if (!state.changes) return;
    const paths = [...document.querySelectorAll(".change-file")].filter(node => node.querySelector("input").checked).map(node => state.changes.files[Number(node.dataset.index)].path);
    try {
      const result = await request("commit", { message: $("commitMessage").value, paths });
      $("commitMessage").value = ""; notice(result.message); await loadChanges(); await loadDashboard();
    } catch (error) { notice(error.message, true); }
  }

  async function startJob(action, payload = {}) {
    if (state.job) return;
    try {
      const result = await request(action, payload); state.job = result.job; $("jobSpinner").hidden = false;
      if (state.screen !== "validation") await showScreen("validation");
      await watchJob(result.job);
    } catch (error) { notice(error.message, true); }
  }
  async function watchJob(identity) {
    while (state.job === identity) {
      try {
        const job = await request("job", { id: identity }); $("validationStatus").textContent = job.message;
        if (job.log) $("validationLog").textContent = job.log;
        if (job.status === "running") { await new Promise(resolve => setTimeout(resolve, 1200)); continue; }
        state.job = null; $("jobSpinner").hidden = true;
        if (job.status === "failed") { notice(job.message, true); return; }
        notice(job.result?.message || job.message); await loadChanges(); await loadDashboard(); return;
      } catch (error) { state.job = null; $("jobSpinner").hidden = true; notice(error.message, true); return; }
    }
  }

  document.querySelectorAll(".nav-item").forEach(node => node.addEventListener("click", () => showScreen(node.dataset.screen)));
  document.querySelectorAll("[data-go]").forEach(node => node.addEventListener("click", () => showScreen(node.dataset.go)));
  $("refreshDashboard").onclick = loadDashboard;
  $("pageSearch").oninput = renderPageList; $("pageType").onchange = renderPageList;
  $("pageForm").addEventListener("input", () => { state.pageDirty = true; updatePreview(); });
  $("validatePage").onclick = validatePage; $("savePage").onclick = savePage;
  $("editLyricTiming").onclick = () => {
    if (state.pageDirty) return notice('Save the lyric text before editing its timings.', true);
    window.open('/website-editor/lyric-timing.html?file=' + encodeURIComponent(state.page.file), '_blank', 'noopener');
  };
  $("openBuiltPreview").onclick = () => { if (state.page?.page.route) window.open("/preview-site" + state.page.page.route, "_blank", "noopener"); };
  document.querySelectorAll("[data-reference-tab]").forEach(node => node.onclick = () => {
    document.querySelectorAll("[data-reference-tab]").forEach(button => button.classList.toggle("active", button === node));
    $("categoryPanel").hidden = node.dataset.referenceTab !== "categories"; $("redirectPanel").hidden = node.dataset.referenceTab !== "redirects";
  });
  $("addCategory").onclick = () => { state.tables.categories.labels.push({ category:"", label:"", count:0 }); renderCategories(); };
  $("addMembership").onclick = () => { if (!state.tables.categories.labels.length) return notice("Create a category first.", true); chooseEntry(id => { state.tables.categories.memberships.push({ category:state.tables.categories.labels[0].category, entry_id:id }); renderCategories(); }); };
  $("saveCategories").onclick = () => saveTable("save-categories", { revision:state.tables.categories.revision, labels:state.tables.categories.labels, memberships:state.tables.categories.memberships }, "Categories saved locally.");
  $("addReference").onclick = () => chooseEntry(id => { state.tables.references.rows.push({ kind:"headword", source:"", source_reading:"", target_entry_id:id, reason:"", sources:"", date:"" }); renderReferences(); });
  $("saveReferences").onclick = () => saveTable("save-references", { revision:state.tables.references.revision, rows:state.tables.references.rows }, "References saved locally.");
  $("addPriority").onclick = () => chooseEntry(id => { state.tables.priorities.rows.push({ lookup_key:"", entry_id:id, rank:"1" }); renderPriorities(); });
  $("savePriorities").onclick = () => saveTable("save-priorities", { revision:state.tables.priorities.revision, rows:state.tables.priorities.rows }, "Static priorities saved locally.");
  $("entryPickerSearch").oninput = renderPicker; $("closePicker").onclick = () => $("entryPicker").close();
  $("refreshChanges").onclick = loadChanges; $("commitButton").onclick = commitChanges; $("pushButton").onclick = () => startJob("push");
  document.querySelectorAll("[data-validation]").forEach(node => node.onclick = () => startJob("validate", { kind:node.dataset.validation }));
  window.addEventListener("beforeunload", event => { if (state.pageDirty) { event.preventDefault(); event.returnValue = ""; } });
  loadDashboard();
})();
