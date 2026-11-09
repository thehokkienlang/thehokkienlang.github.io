(() => {
  'use strict';
  const first = document.getElementById('lyric-timing-data');
  if (!first || !window.TliLyricPlayer) return;
  // A song with several versions has one timed recording per tab panel; each syncs on its own.
  if (first.closest?.('[role="tabpanel"]')) {
    document.querySelectorAll('[role="tabpanel"]').forEach(panel => {
      const data = panel.querySelector('#lyric-timing-data');
      if (data) start(data, panel);
    });
  } else {
    start(first, document);
  }

  function start(data, scope) {
  const timing = JSON.parse(data.textContent);
  if (!timing.cues.some(cue => Number.isFinite(cue.start) && Number.isFinite(cue.end))) return;
  let iframe = [...scope.querySelectorAll('iframe')].find(frame => {
    try { return new URL(frame.src).pathname === '/embed/' + timing.videoId; } catch { return false; }
  });
  if (!iframe) return;
  const controls = scope.querySelector('.lyric-sync-controls');
  const status = controls.querySelector('[data-lyric-status]');
  const follow = controls.querySelector('input');
  (scope.querySelector('.song-script-heading') || iframe.closest('figure') || iframe).insertAdjacentElement('afterend', controls);
  follow.checked = matchMedia('(max-width: 700px)').matches;
  controls.hidden = false;
  let active = null;
  let controller = null, pendingSeek = null, connecting = false, playerFailed = false;
  function releasePlayer(player) {
    if (!player?.destroy) return;
    const replacement = iframe.cloneNode(false);
    iframe.replaceWith(replacement);
    player.destroy();
    iframe = replacement;
  }
  const fail = error => {
    playerFailed = true;
    releasePlayer(controller); controller = null;
    active?.classList.remove('lyric-active'); active?.removeAttribute('aria-current'); active = null;
    status.textContent = error.message;
  };
  const seekLine = time => {
    if (controller) controller.seek(time, true);
    else {
      pendingSeek = time;
      if (!connecting) connectPlayer();
    }
  };
  for (const cue of timing.cues) {
    if (!Number.isFinite(cue.start) || !Number.isFinite(cue.end)) continue;
    const line = scope.querySelector(`[data-lyric-id="${cue.id}"]`);
    if (!line) continue;
    const main = line.querySelector(':scope > span');
    if (!main) continue;
    line.setAttribute('data-lyric-seek', '');
    const walker = document.createTreeWalker(line, NodeFilter.SHOW_TEXT, {
      acceptNode: node => node.parentElement.closest('rt, rp, .tli-rt, .tone-mark, a, .lyric-seek-base') || !node.textContent.trim()
        ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT,
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    const seekTargets = nodes.map((node, index) => {
      const target = document.createElement('span');
      target.className = 'lyric-seek-base';
      target.setAttribute('data-lyric-seek', '');
      if (index === 0) {
        target.setAttribute('tabindex', '0');
        target.setAttribute('role', 'button');
      }
      node.replaceWith(target);
      target.append(node);
      return target;
    });
    line.addEventListener('click', event => {
      if (event.target.closest('rt, rp, .tli-rt, .tone-mark, a')) return;
      const selection = window.getSelection();
      if (selection?.toString() && (line.contains(selection.anchorNode) || line.contains(selection.focusNode))) return;
      seekLine(cue.start);
    });
    const keyboardTarget = seekTargets[0];
    if (!keyboardTarget) continue;
    keyboardTarget.addEventListener('keydown', event => {
      if (event.target !== keyboardTarget || !['Enter', ' '].includes(event.key)) return;
      event.preventDefault();
      seekLine(cue.start);
    });
  }
  function connectPlayer() {
    if (connecting) return;
    connecting = true; playerFailed = false;
    TliLyricPlayer.connect(iframe, (time, state) => {
    status.textContent = '';
    const cue = state === 0 ? null : TliLyricPlayer.cueAt(timing.cues, time);
    const next = cue ? scope.querySelector(`[data-lyric-id="${cue.id}"]`) : null;
    if (next === active) return;
    active?.classList.remove('lyric-active');
    active?.removeAttribute('aria-current');
    active = next;
    if (!active) return;
    active.classList.add('lyric-active'); active.setAttribute('aria-current', 'true');
    if (follow.checked) active.scrollIntoView({ block: 'center', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }, fail).then(player => {
    if (playerFailed) { releasePlayer(player); return; }
    controller = player;
    if (pendingSeek !== null) { controller.seek(pendingSeek, true); pendingSeek = null; }
  }).catch(fail).finally(() => { connecting = false; });
  }
  // A hidden tab's player connects when that tab is first shown.
  if (scope.hidden) scope.addEventListener('song-version-shown', connectPlayer, { once: true });
  else connectPlayer();
  }
})();
