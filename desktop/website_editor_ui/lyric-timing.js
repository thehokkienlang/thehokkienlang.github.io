(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const file = new URLSearchParams(location.search).get('file');
  const token = document.querySelector('meta[name="editor-token"]').content;
  let snapshot, timing, selected = 0, dirty = false, connection, loading = false;
  const inputs = [];
  const tell = (message, error = false) => { $('timingNotice').textContent = message; $('timingNotice').classList.toggle('error', error); };
  async function request(action, payload) {
    const response = await fetch('/desktop-api/website-editor/' + action, { method:'POST', cache:'no-store',
      headers:{'Content-Type':'application/json', 'X-Tangliengim-Editor':token}, body:JSON.stringify(payload) });
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(data.error || 'Request failed.');
    return data;
  }
  function progress() {
    $('completion').textContent = timing.cues.filter(c => Number.isFinite(c.start) && Number.isFinite(c.end)).length + ' / ' + timing.cues.length + ' timed' + (dirty ? ' · Unsaved' : '');
  }
  const edit = () => { dirty = true; progress(); };
  function clock(time) {
    return `${String(Math.floor(time/60)).padStart(2,'0')}:${(time%60).toFixed(3).padStart(6,'0')}`;
  }
  function select(index) {
    selected = index;
    document.querySelectorAll('.cue-row').forEach((row, i) => row.classList.toggle('selected', i === index));
    const parsed = new DOMParser().parseFromString(snapshot.lines[index].html, 'text/html');
    const paragraph = parsed.querySelector('p');
    paragraph.dataset.lyricId = snapshot.lines[index].id;
    paragraph.classList.toggle('lyric-active', $('previewHighlight').checked);
    const source = paragraph.outerHTML;
    $('lyricPreview').srcdoc = '<!doctype html><html><head><meta charset="utf-8"><base href="/"><link rel="stylesheet" href="/preview-assets/site.css"><link rel="stylesheet" href="/shared/web-title-reading.css"></head><body class="content-songs"><article class="imported-content" style="padding:28px 16px">' + source + '</article><script src="/shared/web-ime-core.js"><\/script><script src="/preview-assets/site.js"><\/script></body></html>';
  }
  function render() {
    inputs.length = 0;
    $('cueRows').replaceChildren(...snapshot.lines.map((line, index) => {
      const row = document.createElement('div'); row.className = 'cue-row';
      const choose = document.createElement('button'); choose.type = 'button';
      const number = document.createElement('small'); number.textContent = String(index+1).padStart(2,'0');
      choose.append(number, document.createTextNode(line.label)); choose.onclick = () => select(index);
      const pair = {};
      for (const key of ['start','end']) {
        const input = document.createElement('input'); input.type = 'number'; input.min = '0'; input.max = '86400'; input.step = '0.01';
        input.setAttribute('aria-label', `${key} of sentence ${index+1}`);
        input.value = timing.cues[index][key] ?? '';
        input.onfocus = () => select(index);
        input.oninput = () => { timing.cues[index][key] = input.value === '' ? null : input.valueAsNumber; edit(); };
        pair[key] = input;
      }
      inputs.push(pair); row.append(choose, pair.start, pair.end); return row;
    }));
    select(Math.min(selected, snapshot.lines.length - 1)); progress();
  }
  function mark(key) {
    const time = connection?.time();
    if (!Number.isFinite(time)) return tell('Wait for the YouTube player to be ready.', true);
    const cue = timing.cues[selected];
    if (key === 'end' && (!Number.isFinite(cue.start) || time <= cue.start)) return tell('Mark a start before the end of this sentence.', true);
    cue[key] = Math.round(time*100)/100; inputs[selected][key].value = cue[key]; edit();
    if (key === 'end' && $('advanceAfterEnd').checked && selected+1 < timing.cues.length) select(selected+1);
    tell('Marked ' + key + ' at ' + clock(time) + '.');
  }
  async function load() {
    if (loading || (dirty && !confirm('Discard unsaved timing edits and reload?'))) return;
    loading = true;
    try {
      const result = await request('lyric-timing', {file});
      connection?.destroy(); connection = null;
      snapshot = result; timing = structuredClone(result.timing); dirty = Boolean(result.warning);
      $('timingTitle').textContent = result.title; $('timingStatus').value = timing.status;
      $('saveTiming').disabled = false;
      $('markStart').disabled = $('markEnd').disabled = $('seekStart').disabled = true;
      $('clearCue').disabled = false;
      render(); tell(result.warning || 'Timings are separate from the lyrics. Save here never commits or pushes.', Boolean(result.warning));
      const frame = document.createElement('iframe'); frame.title = 'Song timing player'; frame.allowFullscreen = true;
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.allow = 'encrypted-media; fullscreen; picture-in-picture';
      frame.src = 'https://www.youtube.com/embed/' + result.videoId;
      $('videoHost').replaceChildren(frame);
      connection = await TliLyricPlayer.connect(frame, (time, state) => {
        $('clock').textContent = clock(time);
        $('markStart').disabled = $('markEnd').disabled = $('seekStart').disabled = false;
        const cue = TliLyricPlayer.cueAt(timing.cues, time);
        document.querySelectorAll('.cue-row').forEach((row, i) => row.classList.toggle('playing', state !== 0 && timing.cues[i] === cue));
        $('playerState').textContent = ({0:'Ended',1:'Playing',2:'Paused',3:'Buffering'})[state] || 'Ready';
      }, error => {
        $('markStart').disabled = $('markEnd').disabled = $('seekStart').disabled = true;
        $('playerState').textContent = 'Unavailable';
        tell(error.message + ' You can still enter timestamps manually.', true);
      });
    } catch (error) { tell(error.message, true); }
    finally { loading = false; }
  }
  $('markStart').onclick = () => mark('start'); $('markEnd').onclick = () => mark('end');
  $('seekStart').onclick = () => { const start = timing?.cues[selected].start; if (Number.isFinite(start)) connection?.seek(start); };
  $('clearCue').onclick = () => { timing.cues[selected].start = timing.cues[selected].end = null; inputs[selected].start.value = inputs[selected].end.value = ''; edit(); };
  $('timingStatus').onchange = () => { timing.status = $('timingStatus').value; edit(); };
  $('reloadTiming').onclick = load;
  $('previewHighlight').onchange = () => { if (snapshot) select(selected); };
  $('saveTiming').onclick = async () => {
    $('saveTiming').disabled = true;
    try {
      if (timing.cues.some(c => c.start !== null && !Number.isFinite(c.start) || c.end !== null && !Number.isFinite(c.end))) throw new Error('Enter valid numbers for the sentence times.');
      const result = await request('save-lyric-timing', { file, sourceRevision:snapshot.sourceRevision, revision:snapshot.revision, timing });
      snapshot.revision = result.revision; timing = result.timing; dirty = false; progress(); tell(result.message);
    } catch (error) { tell(error.message, true); }
    finally { $('saveTiming').disabled = false; }
  };
  window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
  load();
})();
