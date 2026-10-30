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
  status.textContent = 'Loading synchronized lyrics…';
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
    if (follow.checked) active.scrollIntoView({ block: 'center', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }, fail).catch(fail);
})();
