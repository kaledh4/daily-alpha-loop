/**
 * Unified Data Fetchers
 * ======================
 * Centralized data fetching for ALL dashboard applications.
 * Eliminates duplicate API calls by using shared cache and reusable functions.
 * 
 * DATA SOURCES:
 * - Market Data: yfinance (via Python), Yahoo Finance API
 * - News: NewsAPI, RSS feeds
 * - Economic: FRED (Federal Reserve), Treasury API
 * - Crypto: CoinGecko, Fear & Greed Index
 * - AI: OpenRouter (multiple models)
 */

import { getApiKey, hasApiKey } from '@monorepo/shared-keys';
import { getCached, setCache, CACHE_TTL, memoize } from './cache.js';

// ===========================================
// Base Fetch Utilities
// ===========================================

/**
 * Fetch with retry, timeout, and error handling
 */
export async function fetchWithRetry(url, options = {}, retries = 3, timeout = 10000) {
    for (let attempt = 0; attempt < retries; attempt++) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);

            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.warn(`[FETCH] Attempt ${attempt + 1}/${retries} failed for ${url}:`, error.message);

            if (attempt === retries - 1) {
                throw error;
            }

            // Exponential backoff
            await new Promise(r => setTimeout(r, 1000 * Math.pow(2, attempt)));
        }
    }
}

// ===========================================
// NEWS FETCHERS (Shared across: ai-race, crash-detector, economic-compass)
// ===========================================

/**
 * Fetch news from NewsAPI - UNIFIED for all apps
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Normalized news data
 */
export async function fetchNews(params = {}) {
    const cacheKey = `news:${JSON.stringify(params)}`;
    const cached = getCached(cacheKey);
    if (cached) return cached;

    const apiKey = getApiKey('NEWS_API_KEY');
    if (!apiKey) {
        console.warn('[NEWS] API key not configured');
        return { articles: [], source: 'cache', error: 'API key missing' };
    }

    const {
        query = 'finance OR crypto OR AI',
        language = 'en',
        pageSize = 10,
        sortBy = 'publishedAt'
    } = params;

    try {
        const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(query)}&language=${language}&pageSize=${pageSize}&sortBy=${sortBy}`;

        const data = await fetchWithRetry(url, {
            headers: { 'X-Api-Key': apiKey }
        });

        // Normalize to unified format
        const result = {
            articles: (data.articles || []).map(a => ({
                id: a.url,
                title: a.title,
                summary: a.description,
                source: a.source?.name || 'Unknown',
                url: a.url,
                publishedAt: a.publishedAt,
                imageUrl: a.urlToImage
            })),
            totalResults: data.totalResults,
            fetchedAt: new Date().toISOString(),
            source: 'newsapi'
        };

        setCache(cacheKey, result, CACHE_TTL.NEWS);
        return result;
    } catch (error) {
        console.error('[NEWS] Fetch error:', error);
        return { articles: [], source: 'error', error: error.message };
    }
}

/**
 * Fetch news from RSS feeds - backup/alternative source
 */
export async function fetchRSSNews(feeds = []) {
    const defaultFeeds = [
        'https://cointelegraph.com/rss',
        'https://finance.yahoo.com/news/rssindex',
        'https://www.coindesk.com/arc/outboundfeeds/rss/'
    ];

    const feedUrls = feeds.length ? feeds : defaultFeeds;
    const cacheKey = `rss:${feedUrls.join(',')}`;
    const cached = getCached(cacheKey);
    if (cached) return cached;

    // RSS parsing would need server-side implementation
    // Return placeholder for client-side
    return {
        articles: [],
        source: 'rss',
        note: 'RSS feeds require server-side parsing'
    };
}

// ===========================================
// CRYPTO FETCHERS (Shared across: crash-detector, economic-compass, hyper-analytical)
// ===========================================

/**
 * Fetch crypto prices from CoinGecko - UNIFIED
 */
export async function fetchCryptoPrices(coins = ['bitcoin', 'ethereum']) {
    const cacheKey = `crypto:prices:${coins.join(',')}`;
    const cached = getCached(cacheKey);
    if (cached) return cached;

    try {
        const ids = coins.join(',');
        const url = `https://api.coingecko.com/api/v3/simple/price?ids=${ids}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true`;

        const data = await fetchWithRetry(url);

        const result = {
            prices: data,
            fetchedAt: new Date().toISOString(),
            source: 'coingecko'
        };

        setCache(cacheKey, result, CACHE_TTL.PRICE);
        return result;
    } catch (error) {
        console.error('[CRYPTO] Price fetch error:', error);
        return { prices: {}, error: error.message };
    }
}

/**
 * Fetch Fear & Greed Index - UNIFIED
 */
export async function fetchFearAndGreed() {
    const cacheKey = 'crypto:fng';
    const cached = getCached(cacheKey);
    if (cached) return cached;

    try {
        const data = await fetchWithRetry('https://api.alternative.me/fng/?limit=1');

        const result = {
            value: parseInt(data.data[0].value),
            classification: data.data[0].value_classification,
            timestamp: data.data[0].timestamp,
            fetchedAt: new Date().toISOString(),
            source: 'alternative.me'
        };

        setCache(cacheKey, result, CACHE_TTL.MACRO);
        return result;
    } catch (error) {
        console.error('[FNG] Fetch error:', error);
        return { value: 50, classification: 'Neutral', error: error.message };
    }
}

// ===========================================
// MACRO FETCHERS (Shared across: crash-detector, economic-compass, hyper-analytical)
// ===========================================

/**
 * Fetch Treasury Auction Data - UNIFIED
 */
export async function fetchTreasuryAuction(term = '10-Year', securityType = 'Note') {
    const cacheKey = `treasury:auction:${term}:${securityType}`;
    const cached = getCached(cacheKey);
    if (cached) return cached;

    try {
        const baseUrl = 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query';
        const params = new URLSearchParams({
            filter: `security_term:eq:${term},security_type:eq:${securityType}`,
            sort: '-auction_date',
            'page[size]': '1'
        });

        const data = await fetchWithRetry(`${baseUrl}?${params}`);

        const result = data.data?.[0] || null;
        if (result) {
            setCache(cacheKey, result, CACHE_TTL.TREASURY);
        }
        return result;
    } catch (error) {
        console.error('[TREASURY] Auction fetch error:', error);
        return null;
    }
}

/**
 * Fetch FRED Economic Data - UNIFIED
 */
export async function fetchFREDData(seriesId) {
    const cacheKey = `fred:${seriesId}`;
    const cached = getCached(cacheKey);
    if (cached) return cached;

    const apiKey = getApiKey('FRED_API_KEY');
    if (!apiKey) {
        console.warn('[FRED] API key not configured');
        return null;
    }

    try {
        const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${seriesId}&api_key=${apiKey}&file_type=json&sort_order=desc&limit=1`;
        const data = await fetchWithRetry(url);

        const result = data.observations?.[0] || null;
        if (result) {
            setCache(cacheKey, result, CACHE_TTL.MACRO);
        }
        return result;
    } catch (error) {
        console.error('[FRED] Fetch error:', error);
        return null;
    }
}

// ===========================================
// RESEARCH FETCHERS (Shared across: ai-race, free-knowledge)
// ===========================================

/**
 * Fetch arXiv papers - UNIFIED
 */
export async function fetchArxivPapers(query, maxResults = 10) {
    const cacheKey = `arxiv:${query}:${maxResults}`;
    const cached = getCached(cacheKey);
    if (cached) return cached;

    try {
        const params = new URLSearchParams({
            search_query: query,
            start: 0,
            max_results: maxResults,
            sortBy: 'submittedDate',
            sortOrder: 'descending'
        });

        const response = await fetch(`http://export.arxiv.org/api/query?${params}`);
        const xmlText = await response.text();

        // Parse XML (basic implementation - full parsing would need DOMParser)
        const result = {
            query,
            rawXml: xmlText,
            fetchedAt: new Date().toISOString(),
            source: 'arxiv'
        };

        setCache(cacheKey, result, CACHE_TTL.HISTORY);
        return result;
    } catch (error) {
        console.error('[ARXIV] Fetch error:', error);
        return { query, papers: [], error: error.message };
    }
}

// ===========================================
// BATCH FETCHER - Fetch all data at once
// ===========================================

/**
 * Fetch all common data sources at once - prevents duplicate calls
 * Returns unified data structure usable by all apps
 */
export async function fetchAllData(options = {}) {
    const {
        includeNews = true,
        includeCrypto = true,
        includeMacro = true,
        includeFNG = true,
        cryptoCoins = ['bitcoin', 'ethereum'],
        newsQuery = 'finance OR crypto'
    } = options;

    const results = {
        fetchedAt: new Date().toISOString(),
        data: {}
    };

    const fetches = [];

    if (includeNews) {
        fetches.push(
            fetchNews({ query: newsQuery }).then(d => results.data.news = d)
        );
    }

    if (includeCrypto) {
        fetches.push(
            fetchCryptoPrices(cryptoCoins).then(d => results.data.crypto = d)
        );
    }

    if (includeFNG) {
        fetches.push(
            fetchFearAndGreed().then(d => results.data.fearAndGreed = d)
        );
    }

    if (includeMacro) {
        fetches.push(
            fetchTreasuryAuction('10-Year', 'Note').then(d => results.data.treasury10Y = d),
            fetchTreasuryAuction('30-Year', 'Bond').then(d => results.data.treasury30Y = d)
        );
    }

    await Promise.allSettled(fetches);

    return results;
}

export default {
    fetchWithRetry,
    fetchNews,
    fetchRSSNews,
    fetchCryptoPrices,
    fetchFearAndGreed,
    fetchTreasuryAuction,
    fetchFREDData,
    fetchArxivPapers,
    fetchAllData
};
