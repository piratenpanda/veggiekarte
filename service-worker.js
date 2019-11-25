const CACHENAME = 'veggiekarte';

console.log(CACHENAME);

// List of files to cache here.
const FILES_TO_CACHE = [
 './index.html'
];


self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHENAME).then(cache => {
      return cache.addAll(FILES_TO_CACHE)
          .then(() => self.skipWaiting());
    })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.open(CACHENAME)
      .then(cache => cache.match(event.request, {ignoreSearch: true}))
      .then(response => {
      return response || fetch(event.request);
    })
  );
});
