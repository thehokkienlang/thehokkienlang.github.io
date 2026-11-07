(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const token = document.querySelector('meta[name="editor-token"]').content;
  const state = {
    snapshot: null, dictionary: [], dictionaryIndex: null, controllers: [], titleController: null,
    file: '', revision: '', route: '', dirty: false, previewTimer: null, renderGeneration: 0,
    publishPaths: [], job: null,
  };

  async function request(action, payload = {}) {
    const response = await fetch('/desktop-api/website-editor/' + action, {
      method: 'POST', cache: 'no-store', signal: AbortSignal.timeout(60000),
      headers: {'Content-Type': 'application/json', 'X-Tangliengim-Editor': token},
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok || !result.ok) throw Object.assign(new Error(result.error || `HTTP ${response.status}`), result);
    return result;
  }
  function notice(message, error = false) {
    const node = $('songNotice'); node.textContent = message; node.hidden = !message;
    node.classList.toggle('error', error);
  }
  function markDirty() {
    state.dirty = true; $('songState').textContent = 'Unsaved'; schedulePreview();
  }
  function setControllerText(controller, value) {
    controller.composer.setText(value, value.length);
    controller.updateControlFromComposer({allowCandidateMenu: false});
    controller.dismissCandidates(false);
  }
  function attachIme(control, menu, onUpdate = markDirty) {
    const popup = window.TangliengimImeCore.createCandidatePopupPositioner({
      control, container: menu, boundary: control.parentElement,
    });
    const controller = window.TangliengimImeCore.createTextImeController({
      control, candidateContainer: menu, entries: state.dictionary,
      dictionaryIndex: state.dictionaryIndex, onUpdate, onCandidatesChanged: popup.schedule,
      enterBehavior: 'none',
    });
    state.controllers.push(controller);
    return controller;
  }
  function destroyLineControllers() {
    state.controllers.filter(controller => controller !== state.titleController).forEach(controller => controller.destroy?.());
    state.controllers = state.titleController ? [state.titleController] : [];
  }

  function lineDrafts() {
    return [...$('lyricRows').children].map(row => row.dataset.kind === 'break'
      ? {kind: 'break'}
      : {kind: 'line', text: row.querySelector('.lyric-input').value, grey: row.querySelector('.grey-input').checked});
  }
  function currentDraft() {
    return {
      version: 1,
      title: $('songTitle').value,
      titleSource: $('songTitleSource').value,
      videoUrl: $('songVideo').value,
      category: $('songCategory').value,
      lyrics: lineDrafts(),
    };
  }
  function newButton(label, title, action) {
    const button = document.createElement('button'); button.type = 'button'; button.textContent = label; button.title = title;
    button.setAttribute('aria-label', title); button.onclick = action; return button;
  }
  function moveRow(row, direction) {
    const sibling = direction < 0 ? row.previousElementSibling : row.nextElementSibling;
    if (!sibling) return;
    if (direction < 0) row.parentElement.insertBefore(row, sibling);
    else row.parentElement.insertBefore(sibling, row);
    renumberRows(); markDirty();
  }
  function removeRow(row) {
    row.remove();
    if (!$('lyricRows').querySelector('.lyric-row')) addLineRow({kind: 'line', text: '', grey: false});
    renumberRows(); markDirty();
  }
  function addLineRow(item = {kind: 'line', text: '', grey: false}, before = null) {
    const row = document.createElement('div'); row.className = 'lyric-row'; row.dataset.kind = 'line';
    const number = document.createElement('span'); number.className = 'lyric-row-number';
    const wrap = document.createElement('span'); wrap.className = 'lyric-input-wrap';
    const input = document.createElement('input'); input.className = 'lyric-input'; input.type = 'text';
    input.autocomplete = 'off'; input.spellcheck = false; input.setAttribute('aria-label', 'TLI lyric line');
    const menu = document.createElement('span'); menu.className = 'hanri-candidate-menu'; menu.role = 'listbox'; menu.hidden = true;
    wrap.append(input, menu);
    const grey = document.createElement('label'); grey.className = 'grey-toggle';
    const check = document.createElement('input'); check.type = 'checkbox'; check.className = 'grey-input'; check.checked = Boolean(item.grey);
    check.onchange = markDirty; grey.append(check, document.createTextNode('Grey out'));
    const tools = document.createElement('span'); tools.className = 'line-tools';
    tools.append(newButton('↑', 'Move line up', () => moveRow(row, -1)), newButton('↓', 'Move line down', () => moveRow(row, 1)), newButton('×', 'Remove line', () => removeRow(row)));
    row.append(number, wrap, grey, tools);
    if (before) $('lyricRows').insertBefore(row, before); else $('lyricRows').append(row);
    const controller = attachIme(input, menu);
    setControllerText(controller, item.text || '');
    input.addEventListener('input', markDirty);
    renumberRows();
    return row;
  }
  function addBreakRow(before = null) {
    const row = document.createElement('div'); row.className = 'verse-break'; row.dataset.kind = 'break';
    row.append(document.createTextNode('Verse break'), newButton('×', 'Remove verse break', () => removeRow(row)));
    if (before) $('lyricRows').insertBefore(row, before); else $('lyricRows').append(row);
    markDirty();
  }
  function renumberRows() {
    let line = 0;
    [...$('lyricRows').children].forEach(row => {
      if (row.dataset.kind === 'line') row.querySelector('.lyric-row-number').textContent = String(++line).padStart(2, '0');
    });
    $('lineCount').textContent = `${line} ${line === 1 ? 'line' : 'lines'}`;
  }
  function renderRows(lyrics) {
    destroyLineControllers(); $('lyricRows').replaceChildren();
    (lyrics?.length ? lyrics : [{kind: 'line', text: '', grey: false}]).forEach(item => {
      if (item.kind === 'break') addBreakRow(); else addLineRow(item);
    });
    state.dirty = false; $('songState').textContent = state.file ? 'Saved source loaded' : 'New song';
  }

  function previewDocument(body, titleHtml) {
    return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><base href="/"><link rel="stylesheet" href="/shared/web-title-reading.css"><link rel="stylesheet" href="/preview-assets/site.css"></head><body class="content-songs"><main class="content-shell content-songs"><h1 class="title-reading">${titleHtml}</h1><article class="imported-content">${body}</article></main><script src="/shared/web-ime-core.js"><\/script><script src="/preview-assets/site.js"><\/script></body></html>`;
  }
  async function renderPreview({loud = false} = {}) {
    const generation = ++state.renderGeneration;
    try {
      const result = await request('render-song', {draft: currentDraft(), route: state.route});
      if (generation !== state.renderGeneration) return null;
      $('songPreview').srcdoc = previewDocument(result.previewBody, result.titleHtml);
      $('songRoute').value = result.route;
      if (loud) notice('Preview refreshed from structured song data.');
      return result;
    } catch (error) {
      if (generation !== state.renderGeneration) return null;
      if (loud) notice(error.message, true);
      return null;
    }
  }
  function schedulePreview() {
    clearTimeout(state.previewTimer);
    state.previewTimer = setTimeout(() => renderPreview(), 450);
  }

  function setDraft(draft, {file = '', revision = '', route = ''} = {}) {
    state.file = file; state.revision = revision; state.route = route; state.publishPaths = [];
    $('songTitle').value = draft.title || '';
    setControllerText(state.titleController, draft.titleSource || '');
    $('songVideo').value = draft.videoUrl || '';
    $('songCategory').value = draft.category || state.snapshot.categories[0]?.id || '';
    $('songRoute').value = route || '';
    renderRows(draft.lyrics);
    $('openSong').hidden = !route; $('openSong').href = route ? '/preview-site' + route : '';
    renderSongList(); schedulePreview();
  }
  function newSong() {
    if (state.dirty && !confirm('Discard this unsaved song draft?')) return;
    setDraft({title: '', titleSource: '', videoUrl: '', category: state.snapshot.categories[0]?.id || '', lyrics: [{kind:'line', text:'', grey:false}]});
    $('songTitle').focus();
  }
  async function openSong(file) {
    if (state.dirty && !confirm('Discard this unsaved song draft?')) return;
    try {
      const result = await request('song-editor-song', {file});
      setDraft(result.draft, result);
      notice(`Loaded ${result.draft.title}.`);
    } catch (error) { notice(error.message, true); }
  }
  function renderSongList() {
    const query = $('songFilter').value.trim().toLocaleLowerCase();
    const songs = state.snapshot.songs.filter(song => !query || `${song.title} ${song.route}`.toLocaleLowerCase().includes(query));
    if (!songs.length) {
      const empty = document.createElement('div'); empty.className = 'song-list-empty';
      empty.textContent = state.snapshot.songs.length ? 'No matching songs.' : 'Songs created here will appear in this list.';
      $('songList').replaceChildren(empty); return;
    }
    $('songList').replaceChildren(...songs.map(song => {
      const button = document.createElement('button'); button.type = 'button'; button.classList.toggle('active', song.file === state.file);
      const title = document.createElement('span'); title.textContent = song.title;
      const route = document.createElement('small'); route.textContent = song.route;
      button.append(title, route); button.onclick = () => openSong(song.file); return button;
    }));
  }
  async function refreshSnapshot() {
    state.snapshot = await request('song-editor-snapshot');
    $('songCategory').replaceChildren(...state.snapshot.categories.map(category => new Option(category.label, category.id)));
    renderSongList();
  }
  async function saveSong({quiet = false} = {}) {
    const preview = await renderPreview({loud: !quiet});
    if (!preview) throw new Error('Fix the song fields before saving.');
    const result = await request('save-song', {
      file: state.file, revision: state.revision,
      categoryRevision: state.snapshot.categoryRevision,
      urlRevision: state.snapshot.urlRevision,
      manifestRevision: state.snapshot.manifestRevision,
      draft: currentDraft(),
    });
    state.file = result.file; state.revision = result.revision; state.route = result.route;
    state.publishPaths = result.publishPaths; state.dirty = false;
    state.snapshot.categoryRevision = result.categoryRevision;
    state.snapshot.urlRevision = result.urlRevision;
    state.snapshot.manifestRevision = result.manifestRevision;
    const listed = state.snapshot.songs.find(song => song.file === result.file);
    if (listed) Object.assign(listed, {title: result.draft.title, route: result.route, revision: result.revision});
    else state.snapshot.songs.unshift({file: result.file, title: result.draft.title, route: result.route, revision: result.revision});
    $('songState').textContent = 'Saved locally';
    $('openSong').hidden = false; $('openSong').href = '/preview-site' + result.route;
    renderSongList();
    if (!quiet) notice(result.message);
    return result;
  }
  async function watchJob(identity) {
    $('publishProgress').hidden = false;
    while (state.job === identity) {
      const job = await request('job', {id: identity});
      $('publishStatus').textContent = job.message; $('publishLog').textContent = job.log || '';
      if (job.status === 'running') { await new Promise(resolve => setTimeout(resolve, 1200)); continue; }
      state.job = null;
      if (job.status === 'failed') throw new Error(job.message);
      notice(job.result.message); $('songState').textContent = 'Published'; return;
    }
  }
  async function publishSong() {
    if (state.job) return;
    try {
      const saved = await saveSong({quiet: true});
      const result = await request('publish-song', {paths: saved.publishPaths, title: saved.draft.title});
      state.job = result.job; await watchJob(result.job);
    } catch (error) { state.job = null; notice(error.message, true); $('publishStatus').textContent = error.message; }
  }

  async function init() {
    try {
      const [snapshot, dictionary] = await Promise.all([
        request('song-editor-snapshot'),
        fetch('/public/data/hokkien-hanri-dict.json', {cache:'no-cache'}).then(response => {
          if (!response.ok) throw new Error('Dictionary could not load.'); return response.json();
        }),
      ]);
      state.snapshot = snapshot; state.dictionary = dictionary.entries;
      state.dictionaryIndex = window.TangliengimImeCore.createDictionaryIndex(state.dictionary);
      $('songCategory').replaceChildren(...snapshot.categories.map(category => new Option(category.label, category.id)));
      state.titleController = attachIme($('songTitleSource'), $('titleCandidates'));
      await state.titleController.preferences.ready;
      newSong(); renderSongList();
    } catch (error) { notice(error.message, true); }
  }

  $('newSong').onclick = newSong;
  $('songFilter').oninput = renderSongList;
  $('addLine').onclick = () => { addLineRow(); markDirty(); $('lyricRows').lastElementChild.querySelector('input').focus(); };
  $('addBreak').onclick = () => addBreakRow();
  $('previewSong').onclick = () => renderPreview({loud:true});
  $('saveSong').onclick = () => saveSong().catch(error => notice(error.message, true));
  $('publishSong').onclick = publishSong;
  $('songTitle').oninput = markDirty; $('songVideo').oninput = markDirty; $('songCategory').onchange = markDirty;
  window.addEventListener('beforeunload', event => { if (state.dirty || state.job) { event.preventDefault(); event.returnValue = ''; } });
  init();
})();
