/**
 * Data Layer Library
 * ===================
 * Re-exports unified-api functionality for backward compatibility.
 * Apps that previously imported from @monorepo/data-layer will continue to work.
 * 
 * NEW APPS SHOULD IMPORT FROM @monorepo/unified-api DIRECTLY.
 * 
 * DEPRECATED: This module is for backward compatibility only.
 */

// Re-export everything from unified-api
export * from '@monorepo/unified-api';

// For backward compatibility with existing code
import {
    fetchWithRetry,
    fetchNews,
    fetchCryptoPrices,
    fetchFearAndGreed,
    fetchTreasuryAuction,
    fetchFREDData,
    getCached,
    setCache,
    CACHE_TTL,
    createAppFetcher
} from '@monorepo/unified-api';

import { getApiKey, hasApiKey } from '@monorepo/shared-keys';

/**
 * @deprecated Use fetchWithRetry from @monorepo/unified-api
 */
export async function fetchData(url, options = {}) {
    console.warn('[DEPRECATED] fetchData is deprecated. Use fetchWithRetry from @monorepo/unified-api');
    return fetchWithRetry(url, options);
}

/**
 * @deprecated Use fetchCryptoPrices from @monorepo/unified-api
 */
export async function fetchCryptoData(coinId = 'bitcoin') {
    console.warn('[DEPRECATED] fetchCryptoData is deprecated. Use fetchCryptoPrices from @monorepo/unified-api');
    const result = await fetchCryptoPrices([coinId]);
    return result.prices?.[coinId] || {};
}

/**
 * @deprecated Use fetchNews from @monorepo/unified-api
 */
export async function fetchNewsData(params = {}) {
    console.warn('[DEPRECATED] fetchNewsData is deprecated. Use fetchNews from @monorepo/unified-api');
    return fetchNews(params);
}

/**
 * @deprecated Use fetchFREDData from @monorepo/unified-api
 */
export async function fetchEconomicData(seriesId) {
    console.warn('[DEPRECATED] fetchEconomicData is deprecated. Use fetchFREDData from @monorepo/unified-api');
    return fetchFREDData(seriesId);
}

/**
 * @deprecated Use fetchWithRetry from @monorepo/unified-api
 */
export async function fetchStockData(symbol) {
    console.warn('[DEPRECATED] fetchStockData is deprecated. Use unified-api market fetchers');
    const apiKey = getApiKey('ALPHA_VANTAGE_KEY');
    if (!apiKey) return null;

    const url = `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${apiKey}`;
    return fetchWithRetry(url);
}

/**
 * Cache wrapper - now delegates to unified-api cache
 * @deprecated Use memoize or getCached/setCache from @monorepo/unified-api
 */
export async function cachedFetch(key, fetchFn, ttl = 300000) {
    console.warn('[DEPRECATED] cachedFetch is deprecated. Use memoize from @monorepo/unified-api');

    const cached = getCached(key);
    if (cached !== null) {
        return cached;
    }

    const data = await fetchFn();
    setCache(key, data, ttl);
    return data;
}

/**
 * Batch fetch - delegates to unified-api
 */
export async function batchFetch(urls) {
    return Promise.all(urls.map(url => fetchWithRetry(url)));
}

// Default export for backward compatibility
export default {
    fetchData,
    fetchWithRetry,
    fetchNews,
    fetchNewsData,
    fetchStockData,
    fetchCryptoData,
    fetchCryptoPrices,
    fetchEconomicData,
    fetchFREDData,
    cachedFetch,
    batchFetch,
    createAppFetcher
};
