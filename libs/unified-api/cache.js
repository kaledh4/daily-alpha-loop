/**
 * Unified Cache Layer
 * ====================
 * Provides in-memory and persistent caching to prevent redundant API calls.
 * All apps share this cache to avoid duplicate fetches.
 */

// In-memory cache with TTL
const memoryCache = new Map();

/**
 * Cache configuration for different data types
 */
export const CACHE_TTL = {
    // Market data - refreshes frequently
    PRICE: 60 * 1000,           // 1 minute
    QUOTES: 60 * 1000,          // 1 minute

    // Macro data - changes less frequently
    TREASURY: 5 * 60 * 1000,    // 5 minutes
    MACRO: 15 * 60 * 1000,      // 15 minutes

    // Static/slow-changing data
    NEWS: 10 * 60 * 1000,       // 10 minutes
    AI_ANALYSIS: 60 * 60 * 1000, // 1 hour

    // Historical data
    HISTORY: 24 * 60 * 60 * 1000 // 24 hours
};

/**
 * Get item from cache
 * @param {string} key - Cache key
 * @returns {any|null} Cached value or null if expired/missing
 */
export function getCached(key) {
    const item = memoryCache.get(key);

    if (!item) return null;

    if (Date.now() > item.expiresAt) {
        memoryCache.delete(key);
        return null;
    }

    return item.value;
}

/**
 * Set item in cache
 * @param {string} key - Cache key
 * @param {any} value - Value to cache
 * @param {number} ttl - Time to live in milliseconds
 */
export function setCache(key, value, ttl = CACHE_TTL.PRICE) {
    memoryCache.set(key, {
        value,
        expiresAt: Date.now() + ttl,
        cachedAt: Date.now()
    });
}

/**
 * Generate cache key from function name and args
 * @param {string} fn - Function name
 * @param  {...any} args - Arguments
 * @returns {string} Cache key
 */
export function cacheKey(fn, ...args) {
    return `${fn}:${args.map(a => JSON.stringify(a)).join(':')}`;
}

/**
 * Memoize async function with cache
 * @param {Function} fn - Async function to memoize
 * @param {number} ttl - Cache TTL
 * @returns {Function} Memoized function
 */
export function memoize(fn, ttl = CACHE_TTL.PRICE) {
    return async function (...args) {
        const key = cacheKey(fn.name, ...args);
        const cached = getCached(key);

        if (cached !== null) {
            console.log(`[CACHE HIT] ${fn.name}`);
            return cached;
        }

        console.log(`[CACHE MISS] ${fn.name}`);
        const result = await fn.apply(this, args);
        setCache(key, result, ttl);
        return result;
    };
}

/**
 * Clear all cache or specific prefix
 * @param {string} prefix - Optional prefix to clear
 */
export function clearCache(prefix = null) {
    if (prefix) {
        for (const key of memoryCache.keys()) {
            if (key.startsWith(prefix)) {
                memoryCache.delete(key);
            }
        }
    } else {
        memoryCache.clear();
    }
}

/**
 * Get cache statistics
 * @returns {Object} Cache stats
 */
export function getCacheStats() {
    const stats = {
        size: memoryCache.size,
        entries: []
    };

    for (const [key, item] of memoryCache.entries()) {
        stats.entries.push({
            key,
            expiresIn: Math.max(0, item.expiresAt - Date.now()),
            age: Date.now() - item.cachedAt
        });
    }

    return stats;
}

/**
 * localStorage-based persistent cache (for browser)
 */
export class PersistentCache {
    constructor(namespace = 'unified-api') {
        this.namespace = namespace;
    }

    _key(key) {
        return `${this.namespace}:${key}`;
    }

    get(key) {
        if (typeof localStorage === 'undefined') return null;

        try {
            const item = localStorage.getItem(this._key(key));
            if (!item) return null;

            const { value, expiresAt } = JSON.parse(item);

            if (Date.now() > expiresAt) {
                localStorage.removeItem(this._key(key));
                return null;
            }

            return value;
        } catch {
            return null;
        }
    }

    set(key, value, ttl = CACHE_TTL.NEWS) {
        if (typeof localStorage === 'undefined') return;

        try {
            localStorage.setItem(this._key(key), JSON.stringify({
                value,
                expiresAt: Date.now() + ttl
            }));
        } catch (e) {
            console.warn('PersistentCache set error:', e);
        }
    }

    clear() {
        if (typeof localStorage === 'undefined') return;

        const keys = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith(this.namespace)) {
                keys.push(key);
            }
        }
        keys.forEach(k => localStorage.removeItem(k));
    }
}

export default {
    getCached,
    setCache,
    cacheKey,
    memoize,
    clearCache,
    getCacheStats,
    PersistentCache,
    CACHE_TTL
};
