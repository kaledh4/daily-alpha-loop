/**
 * Shared PWA Service Worker Template
 * 
 * This service worker provides offline caching capabilities for all dashboard applications.
 * Each app will have its own cache name based on the app name and version.
 */

/**
 * Generate a service worker for a specific app
 * @param {Object} config - Configuration object
 * @param {string} config.appName - The name of the application
 * @param {string} config.version - The version of the application
 * @param {string[]} config.assetsToCache - Array of assets to cache
 * @returns {string} The service worker code as a string
 */
export function generateServiceWorker(config) {
    const { appName, version = 'v1', assetsToCache = [] } = config;
    const cacheName = `${appName}-${version}`;

    const defaultAssets = [
        './',
        './index.html',
        './manifest.json'
    ];

    const allAssets = [...new Set([...defaultAssets, ...assetsToCache])];

    return `
const CACHE_NAME = '${cacheName}';
const ASSETS_TO_CACHE = ${JSON.stringify(allAssets, null, 2)};

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS_TO_CACHE))
      .catch((error) => {
        console.error('Failed to cache assets:', error);
      })
  );
  self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached response if found
        if (response) {
          return response;
        }
        // Otherwise fetch from network
        return fetch(event.request).then((response) => {
          // Don't cache non-successful responses
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }
          
          // Clone the response
          const responseToCache = response.clone();
          
          // Cache the fetched response for future use
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
          
          return response;
        });
      })
      .catch(() => {
        // Return a custom offline page if available
        return caches.match('./index.html');
      })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});
`;
}

/**
 * Register the service worker in the application
 * @param {string} serviceWorkerPath - Path to the service worker file
 * @returns {Promise} Promise that resolves when registration is complete
 */
export async function registerServiceWorker(serviceWorkerPath = '/sw.js') {
    if ('serviceWorker' in navigator) {
        try {
            const registration = await navigator.serviceWorker.register(serviceWorkerPath);
            console.log('Service Worker registered successfully:', registration);
            return registration;
        } catch (error) {
            console.error('Service Worker registration failed:', error);
            throw error;
        }
    } else {
        console.warn('Service Workers are not supported in this browser');
        return null;
    }
}

/**
 * Unregister all service workers
 * @returns {Promise} Promise that resolves when all workers are unregistered
 */
export async function unregisterServiceWorkers() {
    if ('serviceWorker' in navigator) {
        const registrations = await navigator.serviceWorker.getRegistrations();
        await Promise.all(registrations.map(reg => reg.unregister()));
        console.log('All service workers unregistered');
    }
}

export default {
    generateServiceWorker,
    registerServiceWorker,
    unregisterServiceWorkers
};
