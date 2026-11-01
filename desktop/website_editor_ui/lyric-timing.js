(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const file = new URLSearchParams(location.search).get('file');
  const token = document.querySelector('meta[name="editor-token"]').content;
  let snapshot, timing, selected = 0, dirty = false, connection, loading = false;
  let playbackGeneration = 0;
  let previewIndex = null;
  let scrubbing = false;
  const inputs = [];
  const undoHistory = [];
  let savedState = null;
  const sameTiming = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  function remember(before) {
    if (sameTiming(before, timing)) return;
    undoHistory.push({timing: before, selected});
    if (undoHistory.length > 100) undoHistory.shift();
    $('undoTiming').disabled = false;
  }
  let songs = [], hangulEnabled = true;
  const searchKey = value => String(value || '').normalize('NFKD').toLocaleLowerCase()
    .replace(/[\u0300-\u036fˆˋˊˉˇꞈˎˏˍ`’'\s-]/gu, '');
  function filterSongs() {
    const query = searchKey($('songSearch').value);
    const matches = songs.filter(song => searchKey(song.searchText || song.title).includes(query));
    const options = matches.map(song => {
      const option = document.createElement('option'); option.value = song.file; option.textContent = song.title; return option;
    });
    const placeholder = document.createElement('option'); placeholder.value = ''; placeholder.disabled = true;
    placeholder.textContent = matches.length ? 'Choose song...' : 'No matching songs';
    $('songChoice').replaceChildren(placeholder, ...options);
    $('songChoice').value = matches.some(song => song.file === file) ? file : '';
    $('songChoice').disabled = !matches.length;
    $('songSearchCount').textContent = matches.length + ' songs';
  }
  const candidatePopup = window.TangliengimImeCore.createCandidatePopupPositioner({
    control: $('songSearch'), container: $('songSearchCandidates'), boundary: $('songSearchBox'),
  });
  const searchIme = window.TangliengimImeCore.createTextImeController({
    control: $('songSearch'), entries: [], enabled: () => hangulEnabled,
    candidateContainer: $('songSearchCandidates'), onCandidatesChanged: candidatePopup.schedule,
    onUpdate: filterSongs, enterBehavior: 'none',
  });
  async function loadSearchCandidates() {
    try {
      const response = await fetch('/public/data/hokkien-hanri-dict.json', {cache: 'no-cache'});
      if (!response.ok) throw new Error('HTTP ' + response.status);
      const data = await response.json();
      if (!Array.isArray(data.entries)) throw new Error('Missing dictionary entries.');
      await searchIme.preferences.ready;
      searchIme.setEntries(data.entries, window.TangliengimImeCore.createDictionaryIndex(data.entries));
      $('songImeStatus').textContent = '';
    } catch (error) {
      $('songImeStatus').textContent = 'TLI candidates could not load. Refresh to retry. ' + error.message;
    }
  }
  $('songSearch').addEventListener('input', filterSongs);
  $('songHangulToggle').onclick = () => {
    hangulEnabled = !hangulEnabled;
    $('songHangulToggle').setAttribute('aria-pressed', String(hangulEnabled));
    searchIme.setEnabled(); $('songSearch').focus();
  };
  const tell = (message, error = false) => { $('timingNotice').textContent = message; $('timingNotice').classList.toggle('error', error); };
  async function request(action, payload) {
    const response = await fetch('/desktop-api/website-editor/' + action, { method:'POST', cache:'no-store',
      headers:{'Content-Type':'application/json', 'X-Tangliengim-Editor':token}, body:JSON.stringify(payload) });
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(data.error || 'Request failed.');
    return data;
  }
  async function loadSongs() {
    try {
      const result = await request('pages', {});
      songs = result.pages.filter(page => page.type === 'songs');
      songs.sort((a, b) => a.title.localeCompare(b.title));
      filterSongs();
    } catch (error) { tell('Could not load the song list: ' + error.message, true); }
  }
  $('songChoice').onchange = async event => {
    const next = event.target.value;
    if (!next || next === file) return;
    if (dirty && !confirm('Discard unsaved timing edits and switch songs?')) { event.target.value = file; return; }
    event.target.disabled = true;
    try { await connection?.destroy(); }
    catch (error) {
      event.target.value = file; event.target.disabled = false;
      tell('Could not close the previous YouTube window. ' + error.message, true);
      return;
    }
    dirty = false;
    const url = new URL(location.href);
    url.searchParams.set('file', next);
    location.assign(url);
  };
  function progress() {
    $('undoTiming').disabled = !undoHistory.length;
    $('completion').textContent = timing.cues.filter(c => Number.isFinite(c.start) && Number.isFinite(c.end)).length + ' / ' + timing.cues.length + ' timed' + (dirty ? ' · Unsaved' : '');
  }
  const edit = () => { dirty = savedState === null || !sameTiming(timing, savedState); progress(); };
  function clock(time) {
    if (!Number.isFinite(time)) return '';
    const milliseconds = Math.round(time * 1000);
    return `${String(Math.floor(milliseconds / 60000)).padStart(2, '0')}:${String(Math.floor(milliseconds / 1000) % 60).padStart(2, '0')}.${String(milliseconds % 1000).padStart(3, '0')}`;
  }
  function parseClock(value) {
    const text = value.trim();
    if (!text) return null;
    const match = /^(\d+):([0-5]\d)(?:\.(\d{1,3}))?$/.exec(text);
    const seconds = match ? Number(match[1]) * 60 + Number(match[2]) + Number('0.' + (match[3] || '0')) :
      /^\d+(?:\.\d{1,3})?$/.test(text) ? Number(text) : NaN;
    return seconds >= 0 && seconds <= 86400 ? seconds : NaN;
  }
  function select(index) {
    selected = index;
    document.querySelectorAll('.cue-row').forEach((row, i) => row.classList.toggle('selected', i === index));
    showPreview(index);
  }
  function showPreview(index, force = false) {
    if (index === previewIndex && !force) return;
    previewIndex = index;
    const parsed = new DOMParser().parseFromString(snapshot.lines[index].html, 'text/html');
    const paragraph = parsed.querySelector('p');
    paragraph.dataset.lyricId = snapshot.lines[index].id;
    paragraph.classList.toggle('lyric-active', $('previewHighlight').checked);
    const source = paragraph.outerHTML;
    $('lyricPreview').srcdoc = '<!doctype html><html><head><meta charset="utf-8"><base href="/"><link rel="stylesheet" href="/preview-assets/site.css"><link rel="stylesheet" href="/shared/web-title-reading.css"></head><body class="content-songs"><article class="imported-content" style="padding:28px 16px">' + source + '</article><script src="/shared/web-ime-core.js"><\/script><script src="/preview-assets/site.js"><\/script></body></html>';
  }
  function render() {
    previewIndex = null;
    inputs.length = 0;
    $('cueRows').replaceChildren(...snapshot.lines.map((line, index) => {
      const row = document.createElement('div'); row.className = 'cue-row';
      const choose = document.createElement('button'); choose.type = 'button';
      const number = document.createElement('small'); number.textContent = String(index+1).padStart(2,'0');
      choose.append(number, document.createTextNode(line.label));
      choose.title = 'Select sentence; double-click to seek to its saved start';
      choose.onclick = () => select(index);
      choose.ondblclick = () => { select(index); seekSelected(); };
      const pair = {};
      let committedStart = timing.cues[index].start;
      for (const key of ['start','end']) {
        let editRecorded = false;
        const input = document.createElement('input'); input.type = 'text'; input.placeholder = 'MM:SS.mmm'; input.spellcheck = false;
        input.setAttribute('aria-label', `${key} of sentence ${index+1}`);
        input.value = clock(timing.cues[index][key]);
        input.onfocus = () => { editRecorded = false; select(index); if (key === 'start') committedStart = timing.cues[index].start; };
        input.oninput = () => {
          const before = editRecorded ? null : structuredClone(timing);
          timing.cues[index][key] = parseClock(input.value);
          if (before && !sameTiming(before, timing)) { remember(before); editRecorded = true; }
          edit();
        };
        input.onchange = () => {
          if (Number.isNaN(timing.cues[index][key])) return tell('Enter a time such as 03:30.379 (MM:SS.mmm).', true);
          if (key === 'start') {
            if (!alignPreviousEnd(index, timing.cues[index].start)) {
              timing.cues[index].start = committedStart; progress();
            } else { repairFollowing(index); committedStart = timing.cues[index].start; }
          }
          input.value = clock(timing.cues[index][key]);
          editRecorded = false;
        };
        pair[key] = input;
      }
      inputs.push(pair); row.append(choose, pair.start, pair.end); return row;
    }));
    select(Math.min(selected, snapshot.lines.length - 1)); progress();
  }
  function alignPreviousEnd(index, start) {
    const previous = timing.cues[index - 1];
    if (!previous || !Number.isFinite(start) || start < 0 || start > 86400 ||
        !Number.isFinite(previous.start) || !Number.isFinite(previous.end)) return true;
    const end = Math.round((start - 0.1) * 1000) / 1000;
    if (end <= previous.start) {
      tell('Leave more than 0.1 seconds after the previous sentence\'s start. Timings were left unchanged.', true);
      return false;
    }
    if (previous.end === end) return true;
    previous.end = end; inputs[index - 1].end.value = clock(end); edit();
    tell('Previous sentence\'s end adjusted to ' + clock(end) + '.');
    return true;
  }
  function repairFollowing(index) {
    const rounded = value => Math.round(value * 1000) / 1000;
    for (let i = index; i < timing.cues.length; i++) {
      const cue = timing.cues[i];
      if (!Number.isFinite(cue.start) || !Number.isFinite(cue.end)) break;
      if (cue.end <= cue.start) {
        cue.end = rounded(cue.start + 0.1); inputs[i].end.value = clock(cue.end); edit();
      }
      const next = timing.cues[i + 1];
      if (!next || !Number.isFinite(next.start) || next.start > cue.end) break;
      next.start = rounded(cue.end + 0.1); inputs[i + 1].start.value = clock(next.start); edit();
    }
  }
  function repairTimeline() {
    let previous = null;
    const rounded = value => Math.round(value * 1000) / 1000;
    timing.cues.forEach((cue, index) => {
      if (!Number.isFinite(cue.start) || !Number.isFinite(cue.end) || cue.start < 0 || cue.end < 0) return;
      const oldStart = cue.start, oldEnd = cue.end;
      if (previous !== null) {
        const prior = timing.cues[previous];
        if (cue.start < rounded(prior.end + 0.1)) {
          // Preserve the authored start where possible; shorten the prior end first.
          if (rounded(cue.start - 0.1) <= prior.start) cue.start = rounded(prior.start + 0.2);
          prior.end = rounded(cue.start - 0.1);
          inputs[previous].end.value = clock(prior.end); edit();
        }
      }
      if (cue.end <= cue.start) cue.end = rounded(cue.start + 0.1);
      if (cue.start !== oldStart || cue.end !== oldEnd) {
        inputs[index].start.value = clock(cue.start); inputs[index].end.value = clock(cue.end); edit();
      }
      previous = index;
    });
  }
  async function markStart() {
    const active = connection, index = selected;
    let time;
    try { time = active?.sample ? await active.sample() : active?.time(); }
    catch (error) { return tell(error.message, true); }
    if (active !== connection || index !== selected) return;
    if (!Number.isFinite(time)) return tell('Wait for the YouTube player to be ready.', true);
    time = Math.max(0, time - 0.2);
    const cue = timing.cues[selected];
    const before = structuredClone(timing);
    if (!alignPreviousEnd(selected, Math.round(time*1000)/1000)) return;
    cue.start = Math.round(time*1000)/1000; inputs[selected].start.value = clock(cue.start); edit();
    repairFollowing(selected);
    remember(before);
    tell('Marked start at ' + clock(time) + '.');
  }
  function seekSelected(key = 'start') {
    const time = timing?.cues[selected][key];
    if (!Number.isFinite(time)) return tell('This sentence has no ' + key + ' time yet.');
    if (!Number.isFinite(connection?.time())) return tell('Connect the YouTube player and wait for any advertisement to finish before seeking.', true);
    connection.seek(time);
  }
  function playerStatus(message) {
    scrubbing = false; $('playbackSeek').disabled = true;
    $('togglePlayback').disabled = true;
    $('playerState').textContent = message;
    $('markStart').disabled = $('seekStart').disabled = $('seekEnd').disabled = true;
    document.querySelectorAll('.cue-row.playing').forEach(row => row.classList.remove('playing'));
  }
  function playerTime(time, state, duration) {
    const slider = $('playbackSeek');
    slider.disabled = !Number.isFinite(duration) || duration <= 0;
    if (!slider.disabled) slider.max = String(duration);
    if (!scrubbing) {
      slider.value = String(time);
      slider.setAttribute('aria-valuetext', clock(time));
    }
    $('togglePlayback').disabled = false;
    $('togglePlayback').textContent = state === 1 ? '\u23f8' : '\u25b6';
    $('togglePlayback').title = state === 1 ? 'Pause video' : 'Play video';
    $('togglePlayback').setAttribute('aria-label', state === 1 ? 'Pause video' : 'Play video');
    if (!scrubbing) $('clock').textContent = clock(time);
    $('markStart').disabled = $('seekStart').disabled = $('seekEnd').disabled = false;
    const cue = TliLyricPlayer.cueAt(timing.cues, time);
    document.querySelectorAll('.cue-row').forEach((row, i) => row.classList.toggle('playing', state !== 0 && timing.cues[i] === cue));
    if (cue && state !== 0) showPreview(timing.cues.indexOf(cue));
    $('playerState').textContent = ({0:'Ended',1:'Playing',2:'Paused',3:'Buffering'})[state] || 'Ready';
  }
  async function startPlayback() {
    const generation = ++playbackGeneration;
    await connection?.destroy(); connection = null;
    if (generation !== playbackGeneration) return;
    $('clock').textContent = clock(0);
    $('openYoutube').disabled = !snapshot;
    playerStatus('Waiting for YouTube');
    if (!snapshot) return;
    const onTime = (time, state, duration) => { if (generation === playbackGeneration) playerTime(time, state, duration); };
    const onStatus = message => { if (generation === playbackGeneration) playerStatus(message); };
    const onError = error => { if (generation === playbackGeneration) { playerStatus('Unavailable'); tell(error.message, true); } };
    connection = TliLyricCompanion.connect(snapshot.videoId, onTime, onError, onStatus);
    playerStatus('Open the YouTube window to connect');
  }
  async function load() {
    if (loading || (dirty && !confirm('Discard unsaved timing edits and reload?'))) return;
    if (!file) {
      tell('Choose a song to begin editing lyric timings.');
      $('reloadTiming').disabled = true;
      return;
    }
    loading = true;
    try {
      const result = await request('lyric-timing', {file});
      snapshot = result; timing = structuredClone(result.timing); dirty = Boolean(result.warning);
      savedState = result.warning ? null : structuredClone(timing);
      undoHistory.length = 0;
      $('timingTitle').textContent = result.title; $('timingStatus').value = timing.status;
      $('saveTiming').disabled = false;
      $('markStart').disabled = $('seekStart').disabled = $('seekEnd').disabled = true;
      $('clearCue').disabled = false;
      render(); tell(result.warning || 'Timings are separate from the lyrics. Save here never commits or pushes.', Boolean(result.warning));
      await startPlayback();
    } catch (error) { tell(error.message, true); }
    finally { loading = false; }
  }
  $('markStart').onclick = markStart;
  $('togglePlayback').onclick = () => connection?.toggle();
  $('playbackSeek').oninput = () => {
    if ($('playbackSeek').disabled) return;
    scrubbing = true;
    const time = Number($('playbackSeek').value);
    $('clock').textContent = clock(time);
    $('playbackSeek').setAttribute('aria-valuetext', clock(time));
  };
  $('playbackSeek').onchange = () => {
    scrubbing = false;
    if (!$('playbackSeek').disabled) connection?.seek(Number($('playbackSeek').value));
  };
  $('openYoutube').onclick = () => {
    connection?.open().catch(error => tell(error.message, true));
  };
  $('seekStart').onclick = () => seekSelected('start');
  $('seekEnd').onclick = () => seekSelected('end');
  $('undoTiming').onclick = () => {
    const previous = undoHistory.pop();
    if (!previous) return;
    timing = previous.timing; selected = previous.selected;
    $('timingStatus').value = timing.status;
    render(); edit(); tell('Timing edit undone. Save to keep this version.');
  };
  $('clearCue').onclick = () => {
    const before = structuredClone(timing);
    timing.cues[selected].start = timing.cues[selected].end = null;
    inputs[selected].start.value = inputs[selected].end.value = ''; remember(before); edit();
  };
  $('timingStatus').onchange = () => {
    const before = structuredClone(timing);
    timing.status = $('timingStatus').value; remember(before); edit();
  };
  $('reloadTiming').onclick = load;
  $('previewHighlight').onchange = () => { if (snapshot) showPreview(previewIndex ?? selected, true); };
  $('saveTiming').onclick = async () => {
    $('saveTiming').disabled = true;
    try {
      if (timing.cues.some(c => c.start !== null && !Number.isFinite(c.start) || c.end !== null && !Number.isFinite(c.end))) throw new Error('Enter valid numbers for the sentence times.');
      const before = structuredClone(timing);
      repairTimeline(); remember(before);
      const result = await request('save-lyric-timing', { file, sourceRevision:snapshot.sourceRevision, revision:snapshot.revision, timing });
      snapshot.revision = result.revision; timing = result.timing; savedState = structuredClone(timing); dirty = false; progress(); tell(result.message);
    } catch (error) { tell(error.message, true); }
    finally { $('saveTiming').disabled = false; }
  };
  window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
  window.addEventListener('pagehide', () => connection?.destroy().catch(() => {}));
  loadSongs();
  loadSearchCandidates();
  load();
})();
