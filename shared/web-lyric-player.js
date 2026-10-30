/* Shared YouTube clock: no guessed elapsed-time counter and no automatic play. */
(function (root) {
  'use strict';
  let apiPromise;
  function api() {
    if (root.YT?.Player) return Promise.resolve(root.YT);
    if (!apiPromise) apiPromise = new Promise((resolve, reject) => {
      const previous = root.onYouTubeIframeAPIReady;
      const timeout = setTimeout(() => reject(new Error('YouTube did not load. Lyrics remain readable.')), 15000);
      root.onYouTubeIframeAPIReady = () => {
        clearTimeout(timeout);
        try { previous?.(); } finally { resolve(root.YT); }
      };
      const script = document.createElement('script');
      script.src = 'https://www.youtube.com/iframe_api';
      script.onerror = () => { clearTimeout(timeout); reject(new Error('YouTube could not load.')); };
      document.head.append(script);
    });
    return apiPromise;
  }
  function cueAt(cues, time) {
    if (!Number.isFinite(time)) return null;
    return cues.find(cue => Number.isFinite(cue.start) && Number.isFinite(cue.end) && cue.start <= time && time < cue.end) || null;
  }
  async function connect(iframe, onTime, onError = () => {}) {
    const YT = await api();
    const src = new URL(iframe.src, location.href);
    src.searchParams.set('enablejsapi', '1');
    src.searchParams.set('origin', location.origin);
    src.searchParams.set('playsinline', '1');
    iframe.src = src.href;
    let player, timer, ready = false, destroyed = false, failed = false;
    function tick() {
      if (ready && !document.hidden) onTime(player.getCurrentTime(), player.getPlayerState());
    }
    player = new YT.Player(iframe, { events: {
      onReady() { if (!failed) { ready = true; tick(); timer = setInterval(tick, 200); } },
      onStateChange: tick,
      onError(event) {
        failed = true; ready = false; clearInterval(timer);
        const reasons = {100:'The video is unavailable or private.', 101:'The owner does not allow embedded playback.',
          150:'The owner does not allow embedded playback.', 153:'YouTube did not receive a valid player referrer.'};
        onError(new Error((reasons[event.data] || 'This YouTube video cannot be played here.') + ` (YouTube ${event.data})`));
      },
    } });
    const visibility = () => tick();
    document.addEventListener('visibilitychange', visibility);
    const destroy = () => {
      if (destroyed) return;
      destroyed = true; clearInterval(timer); document.removeEventListener('visibilitychange', visibility);
      window.removeEventListener('pagehide', destroy); player.destroy();
    };
    window.addEventListener('pagehide', destroy);
    return { time: () => ready ? player.getCurrentTime() : null,
      duration: () => ready ? player.getDuration() : null,
      seek: time => { if (ready) { player.seekTo(time, true); tick(); } }, destroy };
  }
  const exports = { cueAt, connect };
  if (typeof module !== 'undefined') module.exports = exports;
  root.TliLyricPlayer = exports;
})(typeof window !== 'undefined' ? window : globalThis);
