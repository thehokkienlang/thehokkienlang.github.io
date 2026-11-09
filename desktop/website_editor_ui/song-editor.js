(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const token = document.querySelector('meta[name="editor-token"]').content;
  const state = {
    snapshot: null, dictionary: [], dictionaryIndex: null, controllers: [], titleController: null, searchController: null,
    file: '', revision: '', route: '', dirty: false, previewTimer: null, renderGeneration: 0,
    publishPaths: [], job: null, legacyTitle: null, renderingRows: false,
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
    if (state.renderingRows) return;
    state.dirty = true; $('songState').textContent = 'Unsaved';
  }
  function setControllerText(controller, value) {
    controller.composer.setText(value, value.length);
    controller.updateControlFromComposer({allowCandidateMenu: false});
    controller.dismissCandidates(false);
  }
  function sourceToLyricPresentation(value) {
    const source = String(value || '');
    const hanri = [], hangul = [];
    let text = '', index = 0;
    while (index < source.length) {
      if (source[index] === '[') {
        const close = source.indexOf(']', index + 1);
        const inner = close >= 0 ? source.slice(index + 1, close) : '';
        const match = inner.match(/^([\p{Unified_Ideograph}\u3007]+)(.+)$/u);
        if (match) {
          const start = text.length;
          text += match[1];
          hanri.push({start, end: text.length, hanri: match[1], reading: match[2]});
          index = close + 1;
          continue;
        }
      }
      const unit = window.TangliengimImeCore.readingUnitAt(source, index);
      if (!unit) break;
      const start = text.length;
      text += unit.text;
      const tone = source[unit.end];
      if (unit.canCarryTone && window.TangliengimImeCore.isToneMark(tone)) {
        hangul.push({start, end: text.length, reading: `${unit.text}${tone}`});
        index = unit.end + 1;
      } else {
        index = unit.end;
      }
    }
    return {text, hanri, hangul};
  }
  function setLyricControllerSource(controller, source) {
    const parsed = sourceToLyricPresentation(source);
    controller.rememberedHanriReadings = [];
    controller.rememberedHangulReadings = [];
    controller.composer.setText(parsed.text, parsed.text.length);
    controller.internalUpdate = true;
    controller.control.value = parsed.text;
    controller.control.setSelectionRange(parsed.text.length, parsed.text.length);
    controller.internalUpdate = false;
    controller.rememberedTextSnapshot = parsed.text;
    parsed.hanri.forEach(span => controller.rememberHanriReading(span.start, {
      hanri: span.hanri, reading: span.reading, readingBase: span.reading,
      kind: 'lexical', generatedCandidate: true,
    }, parsed.text));
    parsed.hangul.forEach(span => controller.rememberHangulReading(
      span.start, span.end, span.reading, null, parsed.text, true
    ));
    controller.dismissCandidates(false);
  }
  function lyricControllerSource(controller) {
    const text = controller.control.value;
    const spans = [
      ...controller.getRememberedHanriReadings(text).map(span => ({...span, kind: 'hanri'})),
      ...controller.getRememberedHangulReadings(text).map(span => ({...span, kind: 'hangul'})),
    ].sort((left, right) => left.start - right.start || right.end - left.end);
    let source = '', cursor = 0;
    for (const span of spans) {
      if (span.start < cursor || span.end <= span.start || text.slice(span.start, span.end) !== (span.hanri || span.hangul)) continue;
      source += text.slice(cursor, span.start);
      source += span.kind === 'hanri' ? `[${span.hanri}${span.reading}]` : span.reading;
      cursor = span.end;
    }
    return source + text.slice(cursor);
  }
  function lyricRubyPresentation(controller) {
    const text = controller.control.value;
    const spans = controller.getRememberedHanriReadings(text)
      .sort((left, right) => left.start - right.start || left.end - right.end);
    const segments = [];
    let value = '', cursor = 0;
    for (const span of spans) {
      if (span.start < cursor || span.end <= span.start || text.slice(span.start, span.end) !== span.hanri) continue;
      value += text.slice(cursor, span.start);
      const start = value.length;
      value += span.reading;
      segments.push({start, end: value.length, span});
      cursor = span.end;
    }
    return {value: value + text.slice(cursor), segments};
  }
  function syncLyricRubyInput(controller, selection = null) {
    const rubyInput = controller.control.closest('.lyric-input-wrap')?.querySelector('.lyric-ruby-input');
    if (!rubyInput) return;
    const presentation = lyricRubyPresentation(controller);
    rubyInput.value = presentation.value;
    rubyInput.rubyPresentation = presentation;
    if (selection && document.activeElement === rubyInput) {
      const caret = Math.max(0, Math.min(presentation.value.length, selection.start));
      rubyInput.setSelectionRange(caret, caret);
    }
    rubyInput.imeController?.syncComposerFromControl();
  }
  function applyLyricRubyEdit(controller, rubyInput) {
    const previous = rubyInput.rubyPresentation || lyricRubyPresentation(controller);
    const before = previous.value;
    const after = rubyInput.value;
    if (before === after) return;

    let prefix = 0;
    while (prefix < before.length && prefix < after.length && before[prefix] === after[prefix]) prefix += 1;
    let suffix = 0;
    while (suffix < before.length - prefix && suffix < after.length - prefix &&
      before[before.length - 1 - suffix] === after[after.length - 1 - suffix]) suffix += 1;
    const oldEnd = before.length - suffix;
    const newEnd = after.length - suffix;
    const matchingSegments = previous.segments.filter(item => prefix >= item.start && oldEnd <= item.end);
    // A caret between adjacent ruby spans belongs to the span on its right.
    const segment = matchingSegments[matchingSegments.length - 1];
    if (!segment) {
      syncLyricRubyInput(controller);
      return;
    }

    const oldReading = before.slice(segment.start, segment.end);
    const replacement = after.slice(prefix, newEnd);
    const nextReading = oldReading.slice(0, prefix - segment.start) + replacement +
      oldReading.slice(oldEnd - segment.start);
    const text = controller.control.value;
    if (nextReading) {
      controller.rememberHanriReading(segment.span.start, {
        ...(segment.span.entry || {}),
        hanri: segment.span.hanri,
        reading: nextReading,
        readingBase: nextReading,
        kind: segment.span.entry?.kind || 'lexical',
        generatedCandidate: true,
      }, text);
    } else {
      controller.rememberedHanriReadings = controller.rememberedHanriReadings.filter(item =>
        item.start !== segment.span.start || item.end !== segment.span.end
      );
      controller.rememberedTextSnapshot = text;
    }
    renderLyricAnnotations(controller);
    syncLyricRubyInput(controller, {start: segment.start + nextReading.length});
    markDirty();
  }
  function syncLyricOverlayViewport(controller) {
    const overlay = controller.control.closest('.lyric-text-wrap')?.querySelector('.lyric-annotation-overlay');
    if (!overlay) return;
    overlay.style.width = `${controller.control.clientWidth}px`;
    overlay.style.height = `${controller.control.clientHeight}px`;
    const offset = `translate(${-controller.control.scrollLeft}px, ${-controller.control.scrollTop}px)`;
    for (const anchor of overlay.children) anchor.style.transform = offset;
  }
  function renderLyricAnnotations(controller) {
    const overlay = controller.control.closest('.lyric-text-wrap')?.querySelector('.lyric-annotation-overlay');
    if (!overlay) return;
    const text = controller.control.value;
    overlay.replaceChildren(
      window.TangliengimImeCore.renderToneOverlayMarks(
        text, controller.getHangulToneReadingsForDisplay(text), controller.control
      )
    );
    syncLyricOverlayViewport(controller);
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
  function attachRubyIme(control, onUpdate) {
    const controller = window.TangliengimImeCore.createTextImeController({
      control,
      candidateContainer: null,
      entries: [],
      dictionaryIndex: null,
      onUpdate,
      enterBehavior: 'none',
      toneInputStyle: 'symbols',
    });
    state.controllers.push(controller);
    return controller;
  }
  function destroyLineControllers() {
    const retained = new Set([state.titleController, state.searchController].filter(Boolean));
    state.controllers.filter(controller => !retained.has(controller)).forEach(controller => controller.destroy?.());
    state.controllers = state.controllers.filter(controller => retained.has(controller));
  }

  function lineDrafts() {
    return [...$('lyricRows').children].map(row => row.dataset.kind === 'break'
      ? {kind: 'break'}
      : {kind: 'line', text: lyricControllerSource(row.querySelector('.lyric-input').imeController), grey: row.querySelector('.grey-input').checked});
  }
  function currentDraft() {
    return {
      version: 1,
      title: $('songTitle').value,
      titleSource: $('songTitleSource').value,
      videoUrl: $('songVideo').value,
      category: $('songCategory').value,
      lyrics: lineDrafts(),
      ...(state.legacyTitle ? {legacyTitle: state.legacyTitle} : {}),
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
  let draggedLine = null;
  function clearDragState() {
    $('lyricRows').querySelectorAll('.lyric-row').forEach(row => {
      row.classList.remove('dragging', 'drop-before', 'drop-after');
    });
    draggedLine = null;
  }
  function dragLineOver(event, row) {
    if (!draggedLine || row === draggedLine) return;
    event.preventDefault();
    const bounds = row.getBoundingClientRect();
    const after = event.clientY >= bounds.top + bounds.height / 2;
    $('lyricRows').querySelectorAll('.lyric-row').forEach(item => item.classList.remove('drop-before', 'drop-after'));
    row.classList.add(after ? 'drop-after' : 'drop-before');
    if (event.dataTransfer) event.dataTransfer.dropEffect = 'move';
  }
  function dropLine(event, row) {
    if (!draggedLine || row === draggedLine) return clearDragState();
    event.preventDefault();
    const after = row.classList.contains('drop-after');
    $('lyricRows').insertBefore(draggedLine, after ? row.nextElementSibling : row);
    const moved = draggedLine;
    clearDragState();
    selectLineRow(moved);
    renumberRows();
    markDirty();
  }
  function selectLineRow(row) {
    $('lyricRows').querySelectorAll('.lyric-row.selected').forEach(item => {
      item.classList.remove('selected');
      item.setAttribute('aria-selected', 'false');
    });
    if (!row?.isConnected) return;
    row.classList.add('selected');
    row.setAttribute('aria-selected', 'true');
  }
  function removeRow(row) {
    row.remove();
    if (!$('lyricRows').querySelector('.lyric-row')) addLineRow({kind: 'line', text: '', grey: false});
    renumberRows(); markDirty();
  }
  function duplicateRow(row) {
    const copy = addLineRow({
      kind: 'line',
      text: lyricControllerSource(row.querySelector('.lyric-input').imeController),
      grey: row.querySelector('.grey-input').checked,
    }, row.nextElementSibling);
    markDirty();
    copy.querySelector('.lyric-input').focus();
  }
  function addLineRow(item = {kind: 'line', text: '', grey: false}, before = null) {
    const row = document.createElement('div'); row.className = 'lyric-row'; row.dataset.kind = 'line';
    row.setAttribute('aria-selected', 'false');
    row.addEventListener('pointerdown', () => selectLineRow(row));
    row.addEventListener('focusin', () => selectLineRow(row));
    row.addEventListener('dragover', event => dragLineOver(event, row));
    row.addEventListener('drop', event => dropLine(event, row));
    const number = document.createElement('span'); number.className = 'lyric-row-number';
    const wrap = document.createElement('span'); wrap.className = 'lyric-input-wrap';
    const rubyInput = document.createElement('input'); rubyInput.className = 'lyric-ruby-input'; rubyInput.type = 'text';
    rubyInput.autocomplete = 'off'; rubyInput.spellcheck = false; rubyInput.setAttribute('aria-label', 'Editable ruby readings');
    rubyInput.title = 'Edit the Hangul readings above their matching lyric text';
    const textWrap = document.createElement('span'); textWrap.className = 'lyric-text-wrap';
    const input = document.createElement('input'); input.className = 'lyric-input'; input.type = 'text';
    input.autocomplete = 'off'; input.spellcheck = false; input.setAttribute('aria-label', 'TLI lyric line');
    const menu = document.createElement('span'); menu.className = 'hanri-candidate-menu'; menu.role = 'listbox'; menu.hidden = true;
    const overlay = document.createElement('span'); overlay.className = 'lyric-annotation-overlay'; overlay.setAttribute('aria-hidden', 'true');
    textWrap.append(input, overlay, menu);
    wrap.append(rubyInput, textWrap);
    const grey = document.createElement('label'); grey.className = 'grey-toggle';
    const check = document.createElement('input'); check.type = 'checkbox'; check.className = 'grey-input'; check.checked = Boolean(item.grey);
    check.onchange = markDirty; grey.append(check, document.createTextNode('Grey out'));
    const tools = document.createElement('span'); tools.className = 'line-tools';
    const dragHandle = newButton('⠿', 'Drag line to reorder', () => {});
    dragHandle.className = 'line-drag-handle'; dragHandle.draggable = true;
    dragHandle.addEventListener('dragstart', event => {
      draggedLine = row;
      selectLineRow(row);
      row.classList.add('dragging');
      if (event.dataTransfer) {
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData('text/plain', 'lyric-line');
      }
    });
    dragHandle.addEventListener('dragend', clearDragState);
    tools.append(
      dragHandle,
      newButton('↑', 'Move line up', () => moveRow(row, -1)),
      newButton('↓', 'Move line down', () => moveRow(row, 1)),
      newButton('⧉', 'Duplicate line below', () => duplicateRow(row)),
      newButton('↵', 'Insert verse break above', () => addBreakRow(row)),
      newButton('×', 'Remove line', () => removeRow(row)),
    );
    row.append(number, wrap, grey, tools);
    if (before) $('lyricRows').insertBefore(row, before); else $('lyricRows').append(row);
    let controller;
    controller = attachIme(input, menu, () => {
      renderLyricAnnotations(controller);
      syncLyricRubyInput(controller);
      markDirty();
    });
    input.imeController = controller;
    const rubyController = attachRubyIme(rubyInput, () => applyLyricRubyEdit(controller, rubyInput));
    rubyInput.imeController = rubyController;
    setLyricControllerSource(controller, item.text || '');
    renderLyricAnnotations(controller);
    syncLyricRubyInput(controller);
    input.addEventListener('scroll', () => syncLyricOverlayViewport(controller));
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
    state.renderingRows = true;
    try {
      (lyrics?.length ? lyrics : [{kind: 'line', text: '', grey: false}]).forEach(item => {
        if (item.kind === 'break') addBreakRow(); else addLineRow(item);
      });
    } finally {
      state.renderingRows = false;
    }
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
    state.legacyTitle = draft.legacyTitle || null;
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
      notice(result.imported
        ? `Loaded ${result.draft.title}. Existing ruby lyrics were imported and are now editable.`
        : `Loaded ${result.draft.title}.`);
    } catch (error) { notice(error.message, true); }
  }
  function renderSongList() {
    const searchKey = value => String(value || '').normalize('NFKD').toLocaleLowerCase()
      .replace(/[\u0300-\u036fˆˋˊˉˇꞈˎˏˍ`’'\s\-1-5\[\]()]/gu, '');
    const query = searchKey($('songFilter').value);
    const songs = state.snapshot.songs.filter(song => !query || searchKey(song.searchText || `${song.title} ${song.route}`).includes(query));
    if (!songs.length) {
      const empty = document.createElement('div'); empty.className = 'song-list-empty';
      empty.textContent = state.snapshot.songs.length ? 'No matching songs.' : 'Songs created here will appear in this list.';
      $('songList').replaceChildren(empty); return;
    }
    $('songList').replaceChildren(...songs.map(song => {
      const button = document.createElement('button'); button.type = 'button'; button.classList.toggle('active', song.file === state.file);
      const title = document.createElement('span'); title.textContent = song.title;
      const route = document.createElement('small'); route.textContent = song.route;
      const mode = document.createElement('small'); mode.className = 'song-record-kind';
      mode.textContent = song.editable ? 'Editable song' : 'Existing song';
      button.append(title, route, mode);
      button.onclick = () => openSong(song.file);
      return button;
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
    if (listed) Object.assign(listed, {
      title: result.draft.title, route: result.route, revision: result.revision, editable: true,
      searchText: `${result.draft.title} ${result.route} ${result.draft.titleSource}`,
    });
    else state.snapshot.songs.unshift({
      file: result.file, title: result.draft.title, route: result.route, revision: result.revision,
      editable: true, searchText: `${result.draft.title} ${result.route} ${result.draft.titleSource}`,
    });
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
      state.searchController = attachIme($('songFilter'), $('songFilterCandidates'), renderSongList);
      state.titleController = attachIme($('songTitleSource'), $('titleCandidates'), () => {
        state.legacyTitle = null; markDirty();
      });
      await Promise.all([state.searchController.preferences.ready, state.titleController.preferences.ready]);
      newSong(); renderSongList();
    } catch (error) { notice(error.message, true); }
  }

  $('newSong').onclick = newSong;
  $('songFilter').addEventListener('input', renderSongList);
  $('addLine').onclick = () => { addLineRow(); markDirty(); $('lyricRows').lastElementChild.querySelector('input').focus(); };
  $('previewSong').onclick = () => renderPreview({loud:true});
  $('saveSong').onclick = () => saveSong().catch(error => notice(error.message, true));
  $('publishSong').onclick = publishSong;
  $('songTitle').oninput = () => { state.legacyTitle = null; markDirty(); };
  $('songVideo').oninput = markDirty; $('songCategory').onchange = markDirty;
  window.addEventListener('resize', () => state.controllers.forEach(controller => {
    if (controller.control.classList.contains('lyric-input')) renderLyricAnnotations(controller);
  }));
  window.addEventListener('beforeunload', event => { if (state.dirty || state.job) { event.preventDefault(); event.returnValue = ''; } });
  init();
})();
