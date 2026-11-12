// Offline support for the installed IME pad. Scope: /ime/ only.
// tools/build_site.py fills PRECACHE with the pad's versioned files; an unbuilt checkout
// has an empty list and simply caches what the page loads.
const PRECACHE = [];
const VERSION = "dev";
const PREFIX = "tli-ime-";
const CACHE = PREFIX + VERSION;

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(names => Promise.all(names.filter(name => name.startsWith(PREFIX) && name !== CACHE).map(name => caches.delete(name))))
      .then(() => self.clients.claim())
  );
});

function sameOrigin(url) {
  return new URL(url, self.location.href).origin === self.location.origin;
}

async function store(request, response) {
  // Partial (206) audio responses and errors must not replace a full copy.
  if (response.status === 200 && response.type === "basic") {
    const cache = await caches.open(CACHE);
    await cache.put(request, response.clone());
  }
  return response;
}

self.addEventListener("fetch", event => {
  const request = event.request;
  if (request.method !== "GET" || !sameOrigin(request.url) || request.headers.has("range")) return;
  if (request.mode === "navigate") {
    // Always prefer the newest page; fall back to the saved one with no connection.
    event.respondWith(
      fetch(request).then(response => store(request, response))
        .catch(() => caches.match(request, { ignoreSearch: true }).then(hit => hit || caches.match("/ime/")))
    );
    return;
  }
  // Scripts, styles and data carry content hashes and font names carry versions, so a saved copy is current.
  event.respondWith(caches.match(request).then(hit => hit || fetch(request).then(response => store(request, response))));
});

// The page sends what it loaded before this worker took control (fonts, imported styles, icons).
self.addEventListener("message", event => {
  const urls = Array.isArray(event.data?.cache) ? event.data.cache.filter(url => typeof url === "string" && sameOrigin(url)) : [];
  if (!urls.length) return;
  event.waitUntil(caches.open(CACHE).then(cache => Promise.all(urls.map(async url => {
    if (await cache.match(url)) return;
    try { await store(new Request(url), await fetch(url)); } catch {}
  }))));
});
