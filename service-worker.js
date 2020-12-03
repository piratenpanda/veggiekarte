let CACHE_NAME = 'veggiekarte';

console.log(CACHE_NAME);

// List of files to cache here.
const FILES_TO_CACHE = [
 'index.html',
 'data/places.min.json'
];


self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(FILES_TO_CACHE))
      .then(self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

// Service Worker Caching Strategy: Stale-While-Revalidate
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.match(event.request, {ignoreSearch: true})
         .then(response => {
           var fetchPromise = fetch(event.request)
             .then(networkResponse => {
               cache.put(event.request, networkResponse.clone());
             return networkResponse;
           })
        return response || fetchPromise;
      })
    })
  );
});
