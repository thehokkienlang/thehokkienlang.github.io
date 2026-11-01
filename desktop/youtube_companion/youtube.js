(() => {
  'use strict';
  if (window !== window.top) return;
  const session = new URLSearchParams(location.hash.slice(1)).get('tli-timing');
  if (!session || !/^[a-f0-9]{64}$/.test(session) || location.pathname !== '/watch') return;
  const videoId = new URL(location.href).searchParams.get('v');
  let timer, stopped = false;
  function sample() {
    const player = document.getElementById('movie_player');
    const video = player?.querySelector('video');
    const ad = Boolean(player?.classList.contains('ad-showing') || player?.classList.contains('ad-interrupting'));
    const sameVideo = new URL(location.href).searchParams.get('v') === videoId && location.pathname === '/watch';
    const ready = Boolean(sameVideo && video && video.readyState >= 2 && !ad &&
      Number.isFinite(video.currentTime) && Number.isFinite(video.duration) && video.duration > 0);
    return {videoId, ready, ad, time: ready ? video.currentTime : null,
      duration: ready ? video.duration : null, state: video?.ended ? 0 : video?.paused ? 2 : 1};
  }
  function stop() { stopped = true; clearInterval(timer); }
  chrome.runtime.onMessage.addListener((message, sender, respond) => {
    if (sender.id !== chrome.runtime.id || message.session !== session) return;
    if (message.kind === 'disconnect') { stop(); return; }
    if (message.kind !== 'command') return;
    const current = sample();
    if (stopped || !current.ready) { respond({ok: false, error: current.ad ? 'Wait for the YouTube advertisement to finish.' : 'Wait for the matching YouTube video to be ready.'}); return; }
    if (message.command === 'seek') {
      if (!Number.isFinite(message.time) || message.time < 0 || message.time > current.duration) {
        respond({ok: false, error: 'That time is outside this video.'}); return;
      }
      document.getElementById('movie_player').querySelector('video').currentTime = message.time;
    } else if (message.command !== 'sample') return;
    respond({ok: true, sample: sample()});
  });
  chrome.runtime.sendMessage({action: 'attach', session}).then(result => {
    if (!result?.ok) return;
    let sending = false;
    const tick = async () => {
      if (sending || stopped) return;
      sending = true;
      try {
        const result = await chrome.runtime.sendMessage({action: 'time', session, sample: sample()});
        if (!result?.ok) stop();
      } catch (_) { stop(); }
      finally { sending = false; }
    };
    tick(); timer = setInterval(tick, 250);
  }).catch(stop);
  window.addEventListener('pagehide', stop, {once: true});
})();
