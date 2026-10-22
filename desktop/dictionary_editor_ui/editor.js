"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const fields = ["hanri", "reading", "english", "mandarin_trad", "mandarin_simp", "simplified", "corrected", "entry_id"];
  const typeLabels = { lexical: "Word", hangul_override: "Hangul override",
    correction_alias: "Correction alias", number_pronunciation: "Number pronunciation" };
  const state = { entries: [], defunctEntries: [], recentIds: [], source: "", selectedDefunct: false, statusFilter: "all",
    categories: {}, revision: null, page: 0, selected: null,
    dirty: false, saving: false, publishing: false, deploying: false, searchHangul: false,
    batch: [], job: null, jobKind: null, preview: null, resolutions: {} };
  const pageSize = 30;
  const audioPlayer = window.TangliengimWebAudio.createPlayer();
  const token = document.querySelector('meta[name="editor-token"]').content;
  const channel = typeof BroadcastChannel === "function" ? new BroadcastChannel("tangliengim-dictionary-updates") : null;
  const simplifiedPairs = [
    { source: "hanri", target: "simplified", manual: false },
    { source: "mandarin_trad", target: "mandarin_simp", manual: false },
  ];
  let simplifiedTimer, simplifiedVersion = 0;

  async function request(action, payload = {}) {
    const response = await fetch("/desktop-api/editor/" + action, { method: "POST", cache: "no-store",
      signal: AbortSignal.timeout(["save", "publish", "retire", "restore"].includes(action) ? 60000 : 10000),
      headers: { "Content-Type": "application/json", "X-Tangliengim-Editor": token }, body: JSON.stringify(payload) });
    const result = await response.json();
    if (!response.ok || !result.ok) throw Object.assign(new Error(result.error || `HTTP ${response.status}`), result);
    return result;
  }
  function notice(message, error = false) {
    $("notice").textContent = message;
    $("notice").hidden = !message;
    $("notice").classList.toggle("error", error);
  }
  function pretty(reading, type) {
    if (type === "number_pronunciation") return reading;
    return reading.replace(/[12345]/g, digit => ({ 1: "ˆ", 2: "ˋ", 3: "", 4: "ˊ", 5: "ˉ" })[digit]);
  }
  function setDirty(value) {
    state.dirty = value;
    $("unsaved").hidden = !value;
    if (value) $("preview").hidden = true;
  }
  function formEntry() {
    const entry = Object.fromEntries(fields.map(field => [field, $(field).value]));
    entry.categories = [...$("categoryChoices").querySelectorAll("input:checked")].map(input => input.value);
    return entry;
  }
  function rememberNewEntries(ids) {
    state.recentIds = [...new Set([...ids].reverse().concat(state.recentIds))];
    try { localStorage.setItem("tangliengim-editor-recent:" + state.source, JSON.stringify(state.recentIds)); }
    catch { /* Entries remain saved if browser storage is unavailable. */ }
  }
  function scheduleSimplifiedFields() {
    clearTimeout(simplifiedTimer);
    simplifiedVersion++;
    simplifiedTimer = setTimeout(() => {
      updateSimplifiedFields().catch(error => notice(error.message, true));
    }, 180);
  }
  async function updateSimplifiedFields() {
    clearTimeout(simplifiedTimer);
    const version = ++simplifiedVersion;
    const sources = Object.fromEntries(simplifiedPairs.map(pair => [pair.source, $(pair.source).value]));
    for (const name of ["reading", "corrected", "entry_id"]) sources[name] = $(name).value;
    let result;
    try {
      result = sources.hanri || sources.mandarin_trad
        ? await request("simplify", sources) : { simplified: "", mandarin_simp: "", entry_type: "" };
    } catch (error) {
      if (version !== simplifiedVersion) return false;
      throw error;
    }
    // A reply must never overwrite a newer edit or a different entry's form.
    if (version !== simplifiedVersion) return false;
    for (const pair of simplifiedPairs) if (!pair.manual) $(pair.target).value = result[pair.target];
    $("entry_type").value = typeLabels[result.entry_type] || "";
    return true;
  }
  async function flushSimplifiedFields() {
    while (!await updateSimplifiedFields()) { /* Finish the latest Traditional edit before saving. */ }
  }
  function mayDiscard() {
    return !state.dirty || window.confirm("Discard the unsaved changes in this form?");
  }
  function fill(entry = null) {
    audioPlayer.stop();
    for (const composer of composers) composer.clear();
    state.selectedDefunct = Boolean(entry?.defunct);
    for (const field of fields) $(field).value = entry?.[field] || "";
    $("entry_type").value = typeLabels[entry?.entry_type] || "";
    for (const pair of simplifiedPairs) {
      pair.manual = Boolean(entry?.[pair.target] && entry[pair.target] !== "〃");
    }
    if (!state.selectedDefunct) scheduleSimplifiedFields();
    else { clearTimeout(simplifiedTimer); simplifiedVersion++; }
    for (const input of $("categoryChoices").querySelectorAll("input")) input.checked = Boolean(entry?.categories?.includes(input.value));
    state.selected = entry?.entry_id || null;
    for (const field of fields) {
      if ($(field).tagName === "SELECT") $(field).disabled = state.selectedDefunct;
      else $(field).readOnly = field === "entry_id" || state.selectedDefunct;
    }
    for (const input of $("categoryChoices").querySelectorAll("input")) input.disabled = state.selectedDefunct;
    $("keyboard").disabled = state.selectedDefunct;
    $("saveButton").disabled = state.selectedDefunct || state.saving || Boolean(state.job && state.jobKind === "publish");
    $("retireButton").hidden = !state.selected || state.selectedDefunct;
    $("restoreButton").hidden = !state.selectedDefunct;
    $("restoreButton").disabled = state.saving || Boolean(state.job && state.jobKind === "publish");
    $("retireButton").disabled = state.saving || Boolean(state.job && state.jobKind === "publish");
    $("formTitle").textContent = state.selectedDefunct ? "Defunct entry" : entry ? "Edit entry" : "New entry";
    $("entryStatus").hidden = !state.selectedDefunct;
    $("entryStatus").textContent = state.selectedDefunct
      ? entry.replacement_entry_id ? `Replaced by ${entry.replacement_entry_id}` : "Defunct entry; no replacement." : "";
    $("preview").hidden = true;
    state.preview = null;
    $("saveFeedback").hidden = true;
    setDirty(false);
    renderEntries();
  }
  function filtered() {
    const query = $("search").value.normalize("NFC").toLocaleLowerCase().trim();
    const readingQuery = /[\u1100-\u11ff\u3130-\u318f\uac00-\ud7a3]/u.test(query)
      ? window.TangliengimHangulIme.normalizeReadingBase(query) : "";
    const status = $("statusFilter").value;
    const entries = status === "defunct" ? state.defunctEntries
      : status === "active" ? state.entries : [...state.entries, ...state.defunctEntries];
    const recent = new Map(state.recentIds.map((id, index) => [id, index]));
    return entries.filter(entry => (!$("typeFilter").value || entry.entry_type === $("typeFilter").value)
      && (!$("categoryFilter").value || entry.categories.includes($("categoryFilter").value))
      && (!query || [entry.hanri, entry.reading, entry.english, entry.mandarin_trad, entry.simplified, entry.entry_id]
        .some(value => value.toLocaleLowerCase().includes(query))
        || readingQuery && [entry.hanri, entry.reading, entry.corrected]
          .some(value => window.TangliengimHangulIme.normalizeReadingBase(value).includes(readingQuery))))
      .sort((a, b) => (recent.get(a.entry_id) ?? Number.MAX_SAFE_INTEGER) - (recent.get(b.entry_id) ?? Number.MAX_SAFE_INTEGER));
  }
  function renderEntries() {
    const entries = filtered();
    const pages = Math.max(1, Math.ceil(entries.length / pageSize));
    state.page = Math.min(state.page, pages - 1);
    $("entryCount").textContent = `${entries.length.toLocaleString()} entries`;
    $("entryRows").replaceChildren();
    for (const entry of entries.slice(state.page * pageSize, (state.page + 1) * pageSize)) {
      const tr = document.createElement("tr");
      tr.classList.toggle("selected", entry.entry_id === state.selected);
      tr.classList.toggle("recent-entry", !entry.defunct && state.recentIds.includes(entry.entry_id));
      tr.classList.toggle("defunct-entry", Boolean(entry.defunct));
      const headword = document.createElement("td");
      const select = document.createElement("button");
      select.type = "button";
      select.className = "script";
      select.textContent = entry.hanri;
      headword.append(select);
      if (entry.defunct) {
        const status = document.createElement("span");
        status.className = "entry-status-label";
        status.textContent = "Defunct";
        headword.append(status);
      }
      const reading = document.createElement("td");
      reading.className = "script reading";
      reading.textContent = pretty(entry.reading, entry.entry_type);
      const english = document.createElement("td");
      english.textContent = entry.english;
      tr.append(headword, reading, english);
      tr.addEventListener("click", () => { if (mayDiscard()) fill(entry); });
      $("entryRows").append(tr);
    }
    $("empty").hidden = entries.length > 0;
    $("pageLabel").textContent = `${state.page + 1} / ${pages}`;
    $("previous").disabled = !state.page;
    $("next").disabled = state.page >= pages - 1;
  }
  function renderCategories() {
    const selectedFilter = $("categoryFilter").value;
    const checked = new Set([...$("categoryChoices").querySelectorAll("input:checked")].map(input => input.value));
    $("categoryFilter").replaceChildren(new Option("All categories", ""));
    $("categoryChoices").replaceChildren();
    for (const [key, name] of Object.entries(state.categories)) {
      $("categoryFilter").add(new Option(name, key));
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.value = key;
      input.checked = checked.has(key);
      label.append(input, document.createTextNode(name));
      $("categoryChoices").append(label);
    }
    $("categoryFilter").value = selectedFilter;
  }
  async function load({ preserveForm = false } = {}) {
    const result = await request("snapshot");
    state.entries = result.entries;
    state.defunctEntries = result.defunctEntries || [];
    state.source = result.source;
    try {
      const ids = JSON.parse(localStorage.getItem("tangliengim-editor-recent:" + state.source) || "[]");
      if (Array.isArray(ids)) state.recentIds = ids.filter(id => typeof id === "string" && state.entries.some(entry => entry.entry_id === id));
    } catch { /* Keep this session's recent entries if storage is unavailable. */ }
    state.categories = result.categories;
    state.revision = result.revision;
    $("sourcePath").textContent = result.source;
    renderCategories();
    if (!preserveForm) {
      const selected = [...state.entries, ...state.defunctEntries].find(entry => entry.entry_id === state.selected);
      fill(selected);
    } else renderEntries();
    return result;
  }
  async function writeEntries(action, payload) {
    try { return await request(action, payload); }
    catch (error) {
      if (error.code !== "alternative") throw error;
      const existing = (error.details || []).map(entry => `${entry.hanri}: ${pretty(entry.reading)} ${entry.english}`).join("\n");
      if (!window.confirm(`${error.error}\n\n${existing}\n\nAdd the batch / entry as additional readings or senses?`)) return null;
      return request(action, { ...payload, allowAlternative: true });
    }
  }
  function resetAfterSave(result, batch = false) {
    rememberNewEntries(result.newEntryIds || []);
    if (result.newEntryIds?.length) {
      state.statusFilter = $("statusFilter").value = "all";
      $("typeFilter").value = $("categoryFilter").value = "";
      searchImeController.clear();
      state.page = 0;
    }
    fill();
    if (batch) {
      state.batch = [];
      $("batchText").value = "";
      renderBatch();
      $("batchDialog").close();
    }
    state.revision = result.revision || state.revision;
    const saved = result.saved || [];
    const skipped = result.skipped || [];
    const message = saved.length === 1
      ? `Saved “${saved[0].hanri}” locally. Ready for the next entry.`
      : saved.length ? `Saved ${saved.length} entries locally. Ready for the next entry.`
        : skipped.length ? "Identical entry already exists. Ready for a new entry."
          : "Publishing saved dictionary entries.";
    $("saveFeedback").textContent = message;
    $("saveFeedback").hidden = false;
    document.querySelector(".entry-detail").scrollTop = 0;
    $("hanri").focus();
  }
  async function save(entries = null, batch = false) {
    if (!batch && state.selectedDefunct) return;
    if (state.saving) return;
    state.saving = true;
    busy(Boolean(state.job), state.jobKind);
    try {
      if (!batch) {
        await flushSimplifiedFields();
        entries = [formEntry()];
      }
      const payload = { entries, revision: state.revision };
      const result = await writeEntries("save", payload);
      if (!result) return;
      resetAfterSave(result, batch);
      notice(result.message);
      if (result.job) watchJob(result.job);
      state.saving = false;
      busy(Boolean(state.job), state.jobKind);
      await load({ preserveForm: true });
      notice(result.message);
      if (!state.job) $("publishState").textContent = "Waiting to publish";
    } catch (error) {
      const text = error.code === "stale" ? `${error.message}\nCopy any unsaved text before using Reload.` : error.message;
      notice(text, true);
      if (batch) $("batchStatus").textContent = text;
    } finally {
      state.saving = false;
      busy(Boolean(state.job), state.jobKind);
    }
  }
  function updatePublishProgress() {
    const active = state.publishing || state.deploying || Boolean(state.job && state.jobKind === "publish");
    $("publishSpinner").hidden = !active;
    $("publishStatus").setAttribute("aria-busy", String(active));
  }
  function busy(value, kind = "publish") {
    for (const id of ["saveButton", "saveBatch", "parseBatch"]) $(id).disabled = state.saving || value && kind === "publish";
    $("saveButton").disabled ||= state.selectedDefunct;
    $("retireButton").disabled = state.saving || Boolean(value && kind === "publish");
    $("restoreButton").disabled = state.saving || Boolean(value && kind === "publish");
    $("publishButton").disabled = state.saving || value;
    $("saveBatch").disabled ||= !state.batch.length;
    updatePublishProgress();
  }
  async function watchJob(identity, kind = "refresh") {
    if (state.job === identity) return;
    state.job = identity;
    state.jobKind = kind;
    busy(true, kind);
    try {
      while (true) {
        const job = await request("job", { id: identity });
        state.jobKind = job.kind;
        busy(job.status === "running", job.kind);
        $("publishState").textContent = job.message;
        if (job.status === "failed") {
          if (job.code === "conflict") showConflicts(job.details || []);
          throw new Error(job.message);
        }
        if (job.status === "done") {
          notice(job.message);
          await refreshComposers();
          channel?.postMessage({ type: "dictionary-updated" });
          if (!state.dirty) await load({ preserveForm: true });
          if (job.kind === "publish") await checkDeployment();
          else $("publishState").textContent = "Waiting to publish";
          break;
        }
        await new Promise(resolve => setTimeout(resolve, 1100));
      }
    } catch (error) { notice(error.message, true); }
    finally { state.job = null; state.jobKind = null; busy(false); }
  }
  async function publish(resolutions = {}) {
    if (state.saving) return;
    if (state.dirty && !$("entryForm").reportValidity()) return;
    state.saving = true;
    state.publishing = true;
    state.deploying = false;
    clearTimeout(deploymentTimer);
    deploymentCheck++;
    $("publishState").textContent = "Preparing dictionary updates...";
    busy(Boolean(state.job), state.jobKind);
    try {
      if (state.dirty) await flushSimplifiedFields();
      const payload = { resolutions, ...(state.dirty ? { entries: [formEntry()], revision: state.revision } : {}) };
      const result = await writeEntries("publish", payload);
      if (!result) return;
      resetAfterSave(result);
      await load({ preserveForm: true });
      watchJob(result.job, "publish");
    } catch (error) { notice(error.message, true); }
    finally { state.saving = false; state.publishing = false; busy(Boolean(state.job), state.jobKind); }
  }
  let deploymentTimer, deploymentCheck = 0;
  async function checkDeployment(attempt = 0, version = deploymentCheck) {
    if (version !== deploymentCheck) return;
    clearTimeout(deploymentTimer);
    state.deploying = true;
    updatePublishProgress();
    try {
      const result = await request("deployment");
      if (version !== deploymentCheck) return;
      $("publishState").textContent = result.message;
      state.deploying = result.status === "published";
      if (result.status === "deployment_failed") notice(result.message + (result.url ? "\n" + result.url : ""), true);
      if (state.deploying && attempt < 60) deploymentTimer = setTimeout(() => checkDeployment(attempt + 1, version), 15000);
      else if (state.deploying) {
        state.deploying = false;
        $("publishState").textContent = "Published; check deployment in GitHub Actions.";
      }
    } catch {
      if (version === deploymentCheck) {
        state.deploying = false;
        $("publishState").textContent = "Published; deployment status unavailable.";
      }
    } finally { updatePublishProgress(); }
  }
  function showConflicts(conflicts) {
    $("conflicts").replaceChildren();
    state.resolutions = {};
    for (const conflict of conflicts) {
      const section = document.createElement("section");
      section.className = "conflict-item";
      const heading = document.createElement("h3");
      heading.textContent = `${conflict.entry} / ${conflict.field} (${conflict.file})`;
      section.append(heading);
      for (const choice of ["local", "remote"]) {
        const label = document.createElement("label");
        const input = document.createElement("input");
        input.type = "radio";
        input.name = conflict.token;
        input.value = choice;
        input.required = true;
        input.addEventListener("change", () => { state.resolutions[conflict.token] = choice; });
        const title = document.createElement("span");
        title.textContent = choice === "local" ? "Local" : "GitHub";
        const value = document.createElement("pre");
        value.textContent = typeof conflict[choice] === "string" ? conflict[choice] : JSON.stringify(conflict[choice], null, 2);
        label.append(input, title, value);
        section.append(label);
      }
      $("conflicts").append(section);
    }
    $("conflictDialog").showModal();
  }
  function renderBatch() {
    $("batchRows").replaceChildren();
    state.batch.forEach((entry, index) => {
      const tr = document.createElement("tr");
      for (const field of ["hanri", "reading", "english", "mandarin_trad"]) {
        const td = document.createElement("td");
        const input = document.createElement("input");
        input.value = entry[field] || "";
        input.setAttribute("aria-label", `Row ${index + 1} ${field}`);
        input.addEventListener("input", () => {
          entry[field] = input.value;
          if (field === "hanri") entry.simplified = "";
          if (field === "mandarin_trad") entry.mandarin_simp = "";
        });
        td.append(input); tr.append(td);
      }
      const td = document.createElement("td");
      const remove = document.createElement("button");
      remove.type = "button"; remove.textContent = "Remove";
      remove.addEventListener("click", () => { state.batch.splice(index, 1); renderBatch(); });
      td.append(remove); tr.append(td);
      $("batchRows").append(tr);
    });
    $("batchTable").hidden = !state.batch.length;
    $("saveBatch").disabled = !state.batch.length || Boolean(state.job);
    $("batchStatus").textContent = `${state.batch.length} entries ready for review`;
  }

  const core = window.TangliengimImeCore;
  const searchCandidatePopup = core.createCandidatePopupPositioner({ control: $("search"),
    container: $("searchCandidates"), placement: "below" });
  const searchImeController = core.createTextImeController({ control: $("search"),
    candidateContainer: $("searchCandidates"), enabled: () => state.searchHangul,
    onUpdate: () => { state.page = 0; renderEntries(); },
    onCandidatesChanged: searchCandidatePopup.schedule, enterBehavior: "none" });
  function setSearchKeyboard(enabled) {
    state.searchHangul = Boolean(enabled);
    $("searchKeyboardToggle").setAttribute("aria-pressed", String(state.searchHangul));
    $("search").classList.toggle("hangul-ime-active", state.searchHangul);
    searchImeController.setEnabled();
    state.page = 0;
    renderEntries();
  }
  $("searchKeyboardToggle").addEventListener("click", () => {
    setSearchKeyboard(!state.searchHangul);
    $("search").focus({ preventScroll: true });
  });
  const composers = [
    core.createTextImeController({ control: $("hanri"), candidateContainer: $("headwordCandidates"),
      enabled: () => $("keyboard").checked && !state.selectedDefunct, onUpdate: () => { setDirty(true); scheduleSimplifiedFields(); }, enterBehavior: "commit", toneInputStyle: "symbols" }),
    core.createTextImeController({ control: $("reading"), candidateContainer: $("readingCandidates"),
      enabled: () => $("keyboard").checked && !state.selectedDefunct, onUpdate: () => { setDirty(true); scheduleSimplifiedFields(); }, enterBehavior: "commit", toneInputStyle: "digits" }),
  ];
  async function refreshComposers() {
    const response = await fetch("/public/data/hokkien-hanri-dict.json", { cache: "no-store", signal: AbortSignal.timeout(15000) });
    if (!response.ok) return;
    const data = await response.json();
    const index = core.createDictionaryIndex(data.entries || []);
    composers[0].setEntries(data.entries || [], index);
    composers[1].setEntries([], core.createDictionaryIndex([]));
    searchImeController.setEntries(data.entries || [], index);
  }
  channel?.addEventListener("message", () => refreshComposers().catch(() => {}));
  $("entryForm").addEventListener("input", event => { if (event.target.id !== "keyboard") setDirty(true); });
  $("entryForm").addEventListener("change", event => { if (event.target.id !== "keyboard") setDirty(true); });
  $("entryForm").addEventListener("submit", event => { event.preventDefault(); save(); });
  for (const name of ["reading", "corrected"]) {
    $(name).addEventListener("input", event => { if (!event.isComposing) scheduleSimplifiedFields(); });
    $(name).addEventListener("compositionend", scheduleSimplifiedFields);
  }
  for (const pair of simplifiedPairs) {
    $(pair.source).addEventListener("input", event => { if (!event.isComposing) scheduleSimplifiedFields(); });
    $(pair.source).addEventListener("compositionend", scheduleSimplifiedFields);
    $(pair.target).addEventListener("input", () => {
      pair.manual = Boolean($(pair.target).value);
      scheduleSimplifiedFields();
    });
  }
  $("newButton").addEventListener("click", () => { if (mayDiscard()) { state.statusFilter = $("statusFilter").value = "all"; fill(); $("hanri").focus(); } });
  $("retireButton").addEventListener("click", async () => {
    if (!state.selected || state.selectedDefunct || state.saving) return;
    const entry = state.entries.find(entry => entry.entry_id === state.selected);
    if (!entry) return;
    const message = `Make “${entry.hanri}” defunct? It will remain visible in grey and leave IME results.`
      + (state.dirty ? " Unsaved form changes will be discarded." : "");
    if (!window.confirm(message)) return;
    state.saving = true;
    busy(Boolean(state.job), state.jobKind);
    try {
      const result = await request("retire", { entry_id: entry.entry_id, revision: state.revision });
      state.statusFilter = $("statusFilter").value = "all";
      $("typeFilter").value = $("categoryFilter").value = "";
      searchImeController.clear();
      await load({ preserveForm: true });
      state.page = Math.max(0, Math.floor(filtered().findIndex(row => row.entry_id === entry.entry_id) / pageSize));
      fill(state.defunctEntries.find(row => row.entry_id === entry.entry_id));
      document.querySelector("#entryRows tr.selected")?.scrollIntoView({ block: "nearest" });
      notice(result.message);
      $("publishState").textContent = "Waiting to publish";
      if (result.job) watchJob(result.job);
    } catch (error) { notice(error.message, true); }
    finally { state.saving = false; busy(Boolean(state.job), state.jobKind); }
  });
  $("restoreButton").addEventListener("click", async () => {
    if (!state.selectedDefunct || state.saving) return;
    const identity = state.selected;
    state.saving = true;
    busy(Boolean(state.job), state.jobKind);
    try {
      const result = await request("restore", { entry_id: identity, revision: state.revision });
      state.statusFilter = $("statusFilter").value = "all";
      $("typeFilter").value = $("categoryFilter").value = "";
      searchImeController.clear();
      await load({ preserveForm: true });
      state.page = Math.max(0, Math.floor(filtered().findIndex(row => row.entry_id === identity) / pageSize));
      fill(state.entries.find(row => row.entry_id === identity));
      document.querySelector("#entryRows tr.selected")?.scrollIntoView({ block: "nearest" });
      notice(result.message);
      $("publishState").textContent = "Waiting to publish";
      if (result.job) watchJob(result.job);
    } catch (error) { notice(error.message, true); }
    finally { state.saving = false; busy(Boolean(state.job), state.jobKind); }
  });
  $("reloadButton").addEventListener("click", async () => {
    if (!mayDiscard()) return;
    try { await load(); notice(""); } catch (error) { notice(error.message, true); }
  });
  for (const id of ["typeFilter", "categoryFilter"]) $(id).addEventListener("change", () => { state.page = 0; renderEntries(); });
  $("statusFilter").addEventListener("change", () => {
    if (!mayDiscard()) { $("statusFilter").value = state.statusFilter; return; }
    state.statusFilter = $("statusFilter").value;
    state.page = 0;
    fill();
  });
  $("previous").addEventListener("click", () => { state.page--; renderEntries(); });
  $("next").addEventListener("click", () => { state.page++; renderEntries(); });
  $("publishButton").addEventListener("click", () => publish());
  $("previewButton").addEventListener("click", async () => {
    try {
      await flushSimplifiedFields();
      const result = await request("preview", { entry: formEntry() });
      state.preview = result;
      $("previewHeadword").textContent = result.entry.hanri;
      $("previewReading").textContent = pretty(result.entry.corrected || result.entry.reading, result.entry.entry_type);
      $("previewRoman").textContent = result.lomari;
      $("previewEnglish").textContent = result.entry.english;
      $("audioMissing").textContent = result.audio.missing.length ? "Missing audio: " + result.audio.missing.join(", ") : "";
      $("listen").disabled = !result.audio.segments.length;
      $("preview").hidden = false;
      notice("");
    } catch (error) { notice(error.message, true); }
  });
  $("listen").addEventListener("click", async () => {
    try { await audioPlayer.play(state.preview.audio.segments); }
    catch (error) { notice("Audio could not be played: " + error.message, true); }
  });
  $("batchButton").addEventListener("click", () => { if (mayDiscard()) $("batchDialog").showModal(); });
  $("closeBatch").addEventListener("click", () => $("batchDialog").close());
  $("parseBatch").addEventListener("click", async () => {
    try { const result = await request("import", { text: $("batchText").value }); state.batch = result.entries; renderBatch(); }
    catch (error) { $("batchStatus").textContent = error.message; }
  });
  $("saveBatch").addEventListener("click", () => save(state.batch, true));
  $("cancelConflicts").addEventListener("click", () => $("conflictDialog").close());
  $("conflictForm").addEventListener("submit", event => { event.preventDefault(); $("conflictDialog").close(); publish(state.resolutions); });
  $("restartButton").addEventListener("click", async () => {
    $("restartButton").disabled = true;
    try { await window.TangliengimDesktopRestart.restart(); }
    catch (error) { notice(error.message, true); }
    finally { $("restartButton").disabled = false; }
  });
  window.addEventListener("beforeunload", event => {
    if (window.TangliengimDesktopRestart?.isReloading()) return;
    if (state.dirty || state.batch.length) { event.preventDefault(); event.returnValue = ""; }
  });
  let restartDraft = null;
  const restartAttachment = window.TangliengimDesktopRestart?.attach({
        notify: message => notice(message),
        canRestart: () => state.saving || state.job ? "Wait for the save or publication to finish before restarting."
          : $("conflictDialog").open ? "Finish resolving the dictionary conflict before restarting." : null,
        capture: () => restartDraft || ({ entry: state.selectedDefunct ? state.defunctEntries.find(entry => entry.entry_id === state.selected) : formEntry(), dirty: state.dirty, selected: state.selected, page: state.page,
          manual: simplifiedPairs.map(pair => pair.manual), keyboard: $("keyboard").checked,
          advanced: $("advanced").open, batch: state.batch, batchText: $("batchText").value,
          batchOpen: $("batchDialog").open, search: $("search").value,
          searchHangul: state.searchHangul,
          typeFilter: $("typeFilter").value, categoryFilter: $("categoryFilter").value, statusFilter: $("statusFilter").value }),
        restore: draft => { restartDraft = draft; },
      }).catch(error => notice("Could not restore editor draft: " + error.message, true));
  (async () => {
    try {
      await restartAttachment;
      const result = await load({ preserveForm: state.dirty });
      await refreshComposers();
      if (restartDraft) {
        const draft = restartDraft;
        fill(draft.entry);
        state.selected = draft.selected;
        if (!state.selectedDefunct) $("formTitle").textContent = draft.selected ? "Edit entry" : "New entry";
        setDirty(Boolean(draft.dirty));
        simplifiedPairs.forEach((pair, index) => { pair.manual = Boolean(draft.manual?.[index]); });
        $("keyboard").checked = draft.keyboard;
        $("advanced").open = draft.advanced;
        state.batch = draft.batch || [];
        $("batchText").value = draft.batchText || "";
        renderBatch();
        if (draft.batchOpen) $("batchDialog").showModal();
        for (const field of ["search", "typeFilter", "categoryFilter"]) $(field).value = draft[field] || "";
        state.statusFilter = $("statusFilter").value = draft.statusFilter || "all";
        setSearchKeyboard(draft.searchHangul);
        state.page = draft.page || 0;
        renderEntries();
        restartDraft = null;
      }
      const params = new URLSearchParams(location.search);
      const job = params.get("job") || result.activeJob;
      if (job) watchJob(job);
      else if (params.has("publish")) publish();
      else if (result.tsvPending) $("publishState").textContent = "Waiting to publish";
      else if (result.hasPublication) checkDeployment();
    } catch (error) { notice(error.message, true); }
  })();
})();
