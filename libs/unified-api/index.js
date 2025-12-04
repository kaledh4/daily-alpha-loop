/**
 * Unified API Library
 * ====================
 * Single entry point for all shared API functionality.
 * 
 * USAGE:
 * import { fetchNews, fetchCrypto, callAI } from '@monorepo/unified-api';
 * 
 * This library eliminates redundant code across apps by providing:
 * - Unified data fetching with caching
 * - Centralized AI/LLM integration
 * - Shared utilities and helpers
 */

// Re-export all fetchers
export {
    fetchWithRetry,
    fetchNews,
    fetchRSSNews,
    fetchCryptoPrices,
    fetchFearAndGreed,
    fetchTreasuryAuction,
    fetchFREDData,
    fetchArxivPapers,
    fetchAllData
} from './fetchers.js';

// Re-export AI service
export {
    AI_MODELS,
    PROMPT_TEMPLATES,
    callAI,
    parseAIJson,
    generateMarketAnalysis,
    generateResearchBriefing,
    generateCrashAnalysis,
    generateCryptoOutlook
} from './ai-service.js';

// Re-export cache utilities
export {
    getCached,
    setCache,
    cacheKey,
    memoize,
    clearCache,
    getCacheStats,
    PersistentCache,
    CACHE_TTL
} from './cache.js';

// ===========================================
// Unified Data Layer
// ===========================================

import * as fetchers from './fetchers.js';
import * as ai from './ai-service.js';
import * as cache from './cache.js';

/**
 * App-specific data fetcher factory
 * Returns a pre-configured fetcher for a specific app's needs
 */
export function createAppFetcher(appName, config = {}) {
    const appConfig = APP_CONFIGS[appName] || {};
    const mergedConfig = { ...appConfig, ...config };

    return {
        appName,
        config: mergedConfig,

        // Fetch all data this app needs
        async fetchAll() {
            return fetchers.fetchAllData(mergedConfig);
        },

        // Get AI analysis
        async getAnalysis(data, type = 'market') {
            const analysisFunc = {
                market: ai.generateMarketAnalysis,
                research: ai.generateResearchBriefing,
                crash: ai.generateCrashAnalysis,
                crypto: ai.generateCryptoOutlook
            }[type] || ai.generateMarketAnalysis;

            return analysisFunc(data, { appName });
        },

        // Clear this app's cache
        clearCache() {
            cache.clearCache(`${appName}:`);
        }
    };
}

/**
 * App-specific configurations
 */
const APP_CONFIGS = {
    'ai-race': {
        includeNews: false,
        includeCrypto: false,
        includeMacro: false,
        includeFNG: false,
        // Uses arXiv data primarily
    },

    'crash-detector': {
        includeNews: true,
        includeCrypto: true,
        includeMacro: true,
        includeFNG: true,
        newsQuery: 'treasury OR Fed OR financial crisis'
    },

    'economic-compass': {
        includeNews: true,
        includeCrypto: true,
        includeMacro: true,
        includeFNG: true,
        cryptoCoins: ['bitcoin', 'ethereum'],
        newsQuery: 'crypto OR bitcoin OR market'
    },

    'hyper-analytical': {
        includeNews: false,
        includeCrypto: true,
        includeMacro: true,
        includeFNG: true,
        cryptoCoins: ['bitcoin', 'ethereum']
    },

    'intelligence-platform': {
        includeNews: true,
        includeCrypto: true,
        includeMacro: true,
        includeFNG: true,
        newsQuery: 'AI OR technology OR market'
    },

    'free-knowledge': {
        includeNews: true,
        includeCrypto: false,
        includeMacro: false,
        includeFNG: false,
        newsQuery: 'AI research OR science'
    },

    'dashboard-orchestrator': {
        // Meta-dashboard - fetches from all
        includeNews: true,
        includeCrypto: true,
        includeMacro: true,
        includeFNG: true
    }
};

// ===========================================
// Report Generation Utilities
// ===========================================

/**
 * Generate unified report structure
 * All apps use this as their base data format
 */
export function createReport(appName, data, analysis = null) {
    return {
        meta: {
            app: appName,
            version: '1.0.0',
            generatedAt: new Date().toISOString(),
            source: 'unified-api'
        },
        data,
        analysis,
        // Standard timestamp for caching
        timestamp: Date.now()
    };
}

/**
 * Save report to JSON (for build-time data generation)
 */
export function serializeReport(report) {
    return JSON.stringify(report, null, 2);
}

// Default export
export default {
    // Fetchers
    ...fetchers,

    // AI
    ...ai,

    // Cache
    ...cache,

    // Utilities
    createAppFetcher,
    createReport,
    serializeReport
};
