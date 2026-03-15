const CACHE = 'rebsam-v4';
const ASSETS = ['/','index.html','manifest.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).catch(()=>{}));
  self.skipWaiting();
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  // Ignorer les URLs non-http (chrome-extension://, etc.)
  const url = e.request.url;
  if (!url.startsWith('http://') && !url.startsWith('https://')) return;
  // Pour les requêtes cross-origin (CDN, API tierces) : passer directement sans cache
  const isSameOrigin = url.startsWith(self.location.origin);
  if (!isSameOrigin) {
    e.respondWith(fetch(e.request));
    return;
  }
  // Network-first pour les requêtes same-origin : réseau, cache en fallback offline
  e.respondWith(
    fetch(e.request).then(resp => {
      const clone = resp.clone();
      caches.open(CACHE).then(c => c.put(e.request, clone));
      return resp;
    }).catch(() =>
      caches.match(e.request).then(cached => cached || caches.match('/'))
    )
  );
});
