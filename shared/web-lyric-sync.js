(() => {
  'use strict';
  const data = document.getElementById('lyric-timing-data');
  if (!data || !window.TliLyricPlayer) return;
  const timing = JSON.parse(data.textContent);
  if (!timing.cues.some(cue => Number.isFinite(cue.start) && Number.isFinite(cue.end))) return;
  const iframe = [...document.querySelectorAll('iframe')].find(frame => {
    try { return new URL(frame.src).pathname === '/embed/' + timing.videoId; } catch { return false; }
  });
  if (!iframe) return;
  const controls = document.querySelector('.lyric-sync-controls');
  const status = controls.querySelector('[data-lyric-status]');
  const follow = controls.querySelector('input');
  controls.hidden = false;
  let active = null;
  const fail = error => {
    active?.classList.remove('lyric-active'); active?.removeAttribute('aria-current'); active = null;
    status.textContent = error.message;
  };
  TliLyricPlayer.connect(iframe, (time, state) => {
    status.textContent = '';
    const cue = state === 0 ? null : TliLyricPlayer.cueAt(timing.cues, time);
    const next = cue ? document.querySelector(`[data-lyric-id="${cue.id}"]`) : null;
    if (next === active) return;
    active?.classList.remove('lyric-active');
    active?.removeAttribute('aria-current');
    active = next;
    if (!active) return;
    active.classList.add('lyric-active'); active.setAttribute('aria-current', 'true');
    if (follow.checked && matchMedia('(max-width: 700px)').matches) active.scrollIntoView({ block: 'center', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }, fail).then(player => {
    for (const cue of timing.cues) {
      if (!Number.isFinite(cue.start) || !Number.isFinite(cue.end)) continue;
      const line = document.querySelector(`[data-lyric-id="${cue.id}"]`);
      if (!line) continue;
      line.setAttribute('tabindex', '0');
      line.setAttribute('role', 'button');
      line.setAttribute('data-lyric-seek', '');
      line.addEventListener('click', event => {
        if (event.target.closest('a, button, input') || window.getSelection()?.toString()) return;
        player.seek(cue.start, true);
      });
      line.addEventListener('keydown', event => {
        if (event.target !== line || !['Enter', ' '].includes(event.key)) return;
        event.preventDefault();
        player.seek(cue.start, true);
      });
    }
  }).catch(fail);
})();
