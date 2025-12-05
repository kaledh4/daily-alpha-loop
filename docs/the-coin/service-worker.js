const CACHE_NAME = 'daily-alpha-loop-v2';
const ASSETS_TO_CACHE = [
    './',
    './index.html',
    './manifest.json',
    '../shared/styles.css',
    '../shared/navigation.js',
    '../shared/dashboard-core.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(ASSETS_TO_CACHE))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
    return self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    // Skip for API requests if needed, or cache them with a different strategy
    if (event.request.url.includes('openrouter.ai')) return;

    event.respondWith(
        caches.match(event.request)
            .then((response) => response || fetch(event.request))
    );
});
