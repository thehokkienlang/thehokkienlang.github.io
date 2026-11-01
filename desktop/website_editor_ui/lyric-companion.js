/* Local-only clock bridge to a normal YouTube watch window. */
(() => {
  'use strict';
  const pending = new Map();
  let counter = 0;
  function request(payload) {
    return new Promise((resolve, reject) => {
      const requestId = String(++counter);
      const timeout = setTimeout(() => { pending.delete(requestId); reject(new Error('Install the TLI companion extension in this browser, then reload the editor.')); }, 3000);
      pending.set(requestId, {resolve, reject, timeout});
      window.postMessage({source: 'tli-timing-editor', requestId, ...payload}, location.origin);
    });
  }
  window.addEventListener('message', event => {
    if (event.source !== window || event.origin !== location.origin || event.data?.source !== 'tli-youtube-extension') return;
    const item = pending.get(event.data.requestId);
    if (!item) return;
    clearTimeout(item.timeout); pending.delete(event.data.requestId);
    if (event.data.ok) item.resolve(event.data);
    else item.reject(new Error(event.data.error || 'The companion connection failed.'));
  });
  function connect(videoId, onTime, onError, onStatus) {
    const session = Array.from(crypto.getRandomValues(new Uint8Array(32)), x => x.toString(16).padStart(2, '0')).join('');
    let last, received = 0, destroyed = false, popup, cleanup, registered = false;
    const valid = sample => sample?.videoId === videoId && sample.ready && !sample.ad &&
      Number.isFinite(sample.time) && sample.time >= 0 && sample.time <= 86400;
    function accept(sample) {
      last = sample; received = Date.now();
      if (valid(sample)) onTime(sample.time, sample.state, sample.duration);
      else onStatus(sample?.ad ? 'Advertisement - timing paused' : 'Waiting for the song');
    }
    const listen = event => {
      if (event.source !== window || event.origin !== location.origin || event.data?.source !== 'tli-youtube-extension' ||
          event.data.session !== session || destroyed) return;
      if (event.data.kind === 'clock') accept(event.data.sample);
      if (event.data.kind === 'disconnected') { last = null; onStatus('YouTube window closed'); }
    };
    window.addEventListener('message', listen);
    const watchdog = setInterval(() => {
      if (received && Date.now() - received > 2500) { last = null; received = 0; onStatus('YouTube disconnected - reopen its window'); }
    }, 1000);
    async function command(name, time) {
      const result = await request({action: 'command', session, command: name, time});
      if (destroyed) throw new Error('The song changed.');
      accept(result.sample);
      if (!valid(result.sample)) throw new Error('Wait for the song to be ready.');
      return result.sample.time;
    }
    return {
      async open() {
        // Open synchronously in the click handler to avoid popup blocking.
        if (!popup || popup.closed) {
          popup = window.open('about:blank', 'tli-youtube-' + session, 'popup,width=720,height=560');
          if (popup) popup.opener = null;
        }
        if (!popup) throw new Error('Allow the YouTube popup for this local editor, then try again.');
        try {
          await request({action: 'register', session, videoId});
          registered = true;
          if (destroyed) { popup.close(); await request({action: 'unregister', session}); return; }
          popup.location.href = `https://www.youtube.com/watch?v=${videoId}#tli-timing=${session}`;
          popup.focus(); onStatus('Waiting for the YouTube window');
        } catch (error) { popup.close(); popup = null; throw error; }
      },
      time: () => valid(last) && Date.now() - received <= 2500 ? last.time : null,
      sample: () => command('sample'),
      toggle: () => command('toggle').catch(onError),
      seek: time => command('seek', time).catch(onError),
      destroy() {
        if (cleanup) return cleanup;
        destroyed = true; clearInterval(watchdog); window.removeEventListener('message', listen);
        last = null;
        try { if (popup && !popup.closed) popup.close(); } catch (_) { /* The extension also closes the paired tab. */ }
        if (!registered) return Promise.resolve();
        cleanup = request({action: 'unregister', session}).then(result => {
          if (!result.closed) throw new Error('Reload TLI Lyric Timing Companion at edge://extensions, then refresh this editor to enable popup cleanup.');
          registered = false;
        }).catch(error => { cleanup = null; throw error; });
        return cleanup;
      },
    };
  }
  window.TliLyricCompanion = {connect};
})();
