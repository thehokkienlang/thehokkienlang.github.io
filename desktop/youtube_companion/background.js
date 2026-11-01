'use strict';

const PREFIX = 'timing:';
const validSession = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
const validVideo = value => typeof value === 'string' && /^[A-Za-z0-9_-]{11}$/.test(value);
function editorUrl(value) {
  const url = new URL(value);
  return url.protocol === 'http:' && ['127.0.0.1', 'localhost'].includes(url.hostname) &&
    url.pathname === '/website-editor/lyric-timing.html';
}
function watchUrl(value, videoId) {
  const url = new URL(value);
  return url.origin === 'https://www.youtube.com' && url.pathname === '/watch' &&
    url.searchParams.get('v') === videoId;
}
async function notify(tabId, message) {
  try { await chrome.tabs.sendMessage(tabId, message, {frameId: 0}); } catch (_) { /* Tab closed or reloading. */ }
}
async function closePairedVideo(pair, session) {
  if (pair.youtubeTabId === null) return;
  let tab;
  try { tab = await chrome.tabs.get(pair.youtubeTabId); }
  catch (_) { return; } // The paired tab already closed.
  // Pairing already authenticated this tab. YouTube may clear its URL fragment.
  if (watchUrl(tab.url, pair.videoId)) await chrome.tabs.remove(pair.youtubeTabId);
  else await notify(pair.youtubeTabId, {kind: 'disconnect', session});
}
async function handle(message, sender) {
  if (sender.id !== chrome.runtime.id || sender.frameId !== 0 || !Number.isInteger(sender.tab?.id))
    throw new Error('This connection must come from a companion tab.');
  const isEditor = editorUrl(sender.url);
  if (message.action === 'hello' && isEditor) return {ok: true, version: '1.0.2'};
  if (!validSession(message.session)) throw new Error('Invalid timing connection.');
  const key = PREFIX + message.session;
  const stored = await chrome.storage.session.get(key);
  let pair = stored[key];
  if (message.action === 'register' && isEditor) {
    if (!validVideo(message.videoId)) throw new Error('Invalid video.');
    if (pair && (pair.editorTabId !== sender.tab.id || pair.videoId !== message.videoId))
      throw new Error('This connection already belongs to another editor.');
    // Session storage survives service-worker suspension, but not a browser restart.
    const all = await chrome.storage.session.get(null);
    for (const [oldKey, old] of Object.entries(all)) {
      if (oldKey.startsWith(PREFIX) && oldKey !== key &&
          (old.editorTabId === sender.tab.id || Date.now() - old.created > 8 * 3600000)) {
        await chrome.storage.session.remove(oldKey);
        await closePairedVideo(old, oldKey.slice(PREFIX.length));
      }
    }
    pair = pair || {editorTabId: sender.tab.id, editorUrl: sender.url,
      videoId: message.videoId, youtubeTabId: null, created: Date.now()};
    if (pair.youtubeTabId !== null) await notify(pair.youtubeTabId, {kind: 'disconnect', session: message.session});
    pair.youtubeTabId = null;
    await chrome.storage.session.set({[key]: pair});
    return {ok: true};
  }
  if (!pair && message.action === 'unregister' && isEditor) return {ok: true, closed: true};
  if (!pair) throw new Error('Reopen the YouTube window from the timing editor.');
  if (message.action === 'attach' && watchUrl(sender.url, pair.videoId)) {
    if (pair.youtubeTabId !== null && pair.youtubeTabId !== sender.tab.id)
      throw new Error('Another YouTube window already uses this connection.');
    pair.youtubeTabId = sender.tab.id;
    await chrome.storage.session.set({[key]: pair});
    return {ok: true, videoId: pair.videoId};
  }
  if (message.action === 'time' && pair.youtubeTabId === sender.tab.id && watchUrl(sender.url, pair.videoId)) {
    await notify(pair.editorTabId, {kind: 'clock', session: message.session, sample: message.sample});
    return {ok: true};
  }
  if (!isEditor || sender.tab.id !== pair.editorTabId || sender.url !== pair.editorUrl)
    throw new Error('This editor does not own the connection.');
  if (message.action === 'unregister') {
    await closePairedVideo(pair, message.session);
    await chrome.storage.session.remove(key);
    return {ok: true, closed: true};
  }
  if (message.action === 'command' && ['sample', 'seek'].includes(message.command)) {
    if (pair.youtubeTabId === null) throw new Error('Open the companion YouTube window first.');
    const tab = await chrome.tabs.get(pair.youtubeTabId);
    if (!watchUrl(tab.url, pair.videoId)) throw new Error('The YouTube window is on a different video.');
    if (message.command === 'seek' && (!Number.isFinite(message.time) || message.time < 0 || message.time > 86400))
      throw new Error('Invalid seek time.');
    return chrome.tabs.sendMessage(pair.youtubeTabId, {kind: 'command', session: message.session,
      command: message.command, time: message.time}, {frameId: 0});
  }
  throw new Error('Unsupported companion action.');
}
chrome.runtime.onMessage.addListener((message, sender, respond) => {
  handle(message, sender).then(respond, error => respond({ok: false, error: error.message}));
  return true;
});
chrome.tabs.onRemoved.addListener(async tabId => {
  const all = await chrome.storage.session.get(null);
  for (const [key, pair] of Object.entries(all)) {
    if (!key.startsWith(PREFIX)) continue;
    if (pair.editorTabId === tabId) {
      await chrome.storage.session.remove(key);
      await closePairedVideo(pair, key.slice(PREFIX.length));
    } else if (pair.youtubeTabId === tabId) {
      pair.youtubeTabId = null;
      await chrome.storage.session.set({[key]: pair});
      await notify(pair.editorTabId, {kind: 'disconnected', session: key.slice(PREFIX.length)});
    }
  }
});
