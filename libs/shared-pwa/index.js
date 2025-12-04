/**
 * Shared PWA Library
 * 
 * Main entry point for the shared PWA functionality.
 * Exports service worker and manifest utilities.
 */

export {
    generateServiceWorker,
    registerServiceWorker,
    unregisterServiceWorkers
} from './service-worker.js';

export {
    generateManifest,
    getManifestForDashboard,
    DASHBOARD_MANIFESTS
} from './manifest-template.js';

// Re-export everything as default
import * as serviceWorker from './service-worker.js';
import * as manifest from './manifest-template.js';

export default {
    ...serviceWorker,
    ...manifest
};
