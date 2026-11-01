(() => {
  'use strict';
  if (!['127.0.0.1', 'localhost'].includes(location.hostname) ||
      location.pathname !== '/website-editor/lyric-timing.html' || window !== window.top) return;
  let session;
  const post = data => window.postMessage({source: 'tli-youtube-extension', ...data}, location.origin);
  window.addEventListener('message', async event => {
    if (event.source !== window || event.origin !== location.origin || event.data?.source !== 'tli-timing-editor') return;
    const data = event.data;
    if (!['hello', 'register', 'command', 'unregister'].includes(data.action) || typeof data.requestId !== 'string') return;
    try {
      const result = await chrome.runtime.sendMessage({action: data.action, session: data.session,
        videoId: data.videoId, command: data.command, time: data.time});
      if (result?.ok && data.action === 'register') session = data.session;
      if (data.action === 'unregister' && session === data.session) session = null;
      post({requestId: data.requestId, ...result});
    } catch (_) { post({requestId: data.requestId, ok: false, error: 'Reload this editor after installing or updating the companion extension.'}); }
  });
  chrome.runtime.onMessage.addListener((message, sender) => {
    if (sender.id === chrome.runtime.id && session && message.session === session &&
        ['clock', 'disconnected'].includes(message.kind)) post(message);
  });
  window.addEventListener('pagehide', () => {
    if (session) chrome.runtime.sendMessage({action: 'unregister', session}).catch(() => {});
  });
})();
