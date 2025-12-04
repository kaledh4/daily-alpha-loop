/**
 * Data Layer - Common Data Fetching Utilities
 * 
 * Provides reusable data fetching functions and utilities for all dashboard applications.
 */

import { getApiKey } from '@monorepo/shared-keys';

/**
 * Base fetch wrapper with error handling
 * @param {string} url - URL to fetch
 * @param {Object} options - Fetch options
 * @returns {Promise<any>} Parsed JSON response
 */
export async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

/**
 * Fetch with retry logic
 * @param {string} url - URL to fetch
 * @param {Object} options - Fetch options
 * @param {number} retries - Number of retries
 * @returns {Promise<any>} Parsed JSON response
 */
export async function fetchWithRetry(url, options = {}, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            return await fetchData(url, options);
        } catch (error) {
            if (i === retries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
    }
}

/**
 * Fetch news data from NewsAPI
 * @param {Object} params - Query parameters
 * @returns {Promise<any>} News data
 */
export async function fetchNews(params = {}) {
    const apiKey = getApiKey('NEWS_API_KEY');
    const { query = 'finance', language = 'en', pageSize = 10 } = params;

    const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(query)}&language=${language}&pageSize=${pageSize}&apiKey=${apiKey}`;

    return fetchWithRetry(url);
}

/**
 * Fetch stock data from Alpha Vantage
 * @param {string} symbol - Stock symbol
 * @returns {Promise<any>} Stock data
 */
export async function fetchStockData(symbol) {
    const apiKey = getApiKey('ALPHA_VANTAGE_KEY');
    const url = `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${apiKey}`;

    return fetchWithRetry(url);
}

/**
 * Fetch crypto data from CoinGecko
 * @param {string} coinId - Coin ID
 * @returns {Promise<any>} Crypto data
 */
export async function fetchCryptoData(coinId = 'bitcoin') {
    const url = `https://api.coingecko.com/api/v3/simple/price?ids=${coinId}&vs_currencies=usd&include_24hr_change=true`;

    return fetchWithRetry(url);
}

/**
 * Fetch economic data from FRED
 * @param {string} seriesId - FRED series ID
 * @returns {Promise<any>} Economic data
 */
export async function fetchEconomicData(seriesId) {
    const apiKey = getApiKey('FRED_API_KEY');
    const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${seriesId}&api_key=${apiKey}&file_type=json`;

    return fetchWithRetry(url);
}

/**
 * Cache wrapper for data fetching
 * @param {string} key - Cache key
 * @param {Function} fetchFn - Fetch function
 * @param {number} ttl - Time to live in milliseconds
 * @returns {Promise<any>} Cached or fresh data
 */
export async function cachedFetch(key, fetchFn, ttl = 300000) {
    const cached = localStorage.getItem(key);

    if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        if (Date.now() - timestamp < ttl) {
            return data;
        }
    }

    const data = await fetchFn();
    localStorage.setItem(key, JSON.stringify({ data, timestamp: Date.now() }));

    return data;
}

/**
 * Batch fetch multiple URLs
 * @param {Array<string>} urls - Array of URLs to fetch
 * @returns {Promise<Array>} Array of responses
 */
export async function batchFetch(urls) {
    return Promise.all(urls.map(url => fetchData(url)));
}

export default {
    fetchData,
    fetchWithRetry,
    fetchNews,
    fetchStockData,
    fetchCryptoData,
    fetchEconomicData,
    cachedFetch,
    batchFetch
};
