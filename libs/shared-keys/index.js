/**
 * Centralized API Key Management
 * 
 * This module provides secure access to API keys and secrets for all dashboard applications.
 * Keys are loaded from GitHub Actions environment variables (set from GitHub Secrets during build).
 * 
 * For local development, keys can be passed via environment variables.
 * For production builds via GitHub Actions, keys are automatically injected from GitHub Secrets.
 */

// API Key storage - populated from GitHub Actions environment variables
const API_KEYS = {
  // News APIs
  NEWS_API_KEY: process.env.NEWS_API_KEY || '',

  // Financial Data APIs
  ALPHA_VANTAGE_KEY: process.env.ALPHA_VANTAGE_KEY || '',
  FINNHUB_KEY: process.env.FINNHUB_KEY || '',
  FRED_API_KEY: process.env.FRED_API_KEY || '',

  // Crypto APIs
  COINMARKETCAP_KEY: process.env.COINMARKETCAP_KEY || '',
  COINGECKO_KEY: process.env.COINGECKO_KEY || '',

  // AI/ML APIs
  OPENAI_KEY: process.env.OPENAI_KEY || '',
  ANTHROPIC_KEY: process.env.ANTHROPIC_KEY || '',
  GIGA_AI_KEY: process.env.GIGA_AI_KEY || '',
  OPENROUTER_KEY: process.env.OPENROUTER_KEY || '',

  // Macro Economic Data
  MACRO_KEY: process.env.MACRO_KEY || '',
  WORLD_BANK_KEY: process.env.WORLD_BANK_KEY || '',

  // Market Data
  POLYGON_KEY: process.env.POLYGON_KEY || '',
  TWELVE_DATA_KEY: process.env.TWELVE_DATA_KEY || '',
};

/**
 * Get an API key by name
 * @param {string} keyName - The name of the API key to retrieve
 * @returns {string} The API key value
 * @throws {Error} If the key is not found or is empty
 */
export function getApiKey(keyName) {
  const key = API_KEYS[keyName];

  if (!key) {
    console.warn(`API key "${keyName}" is not configured`);
    return '';
  }

  return key;
}

/**
 * Check if an API key is configured
 * @param {string} keyName - The name of the API key to check
 * @returns {boolean} True if the key is configured and not empty
 */
export function hasApiKey(keyName) {
  return !!(API_KEYS[keyName] && API_KEYS[keyName].length > 0);
}

/**
 * Get all configured API keys (for debugging/validation)
 * @returns {Object} Object with key names and boolean indicating if they're configured
 */
export function getConfiguredKeys() {
  const configured = {};
  for (const [keyName, value] of Object.entries(API_KEYS)) {
    configured[keyName] = !!(value && value.length > 0);
  }
  return configured;
}

/**
 * Set an API key programmatically (useful for testing or runtime configuration)
 * @param {string} keyName - The name of the API key
 * @param {string} value - The API key value
 */
export function setApiKey(keyName, value) {
  if (API_KEYS.hasOwnProperty(keyName)) {
    API_KEYS[keyName] = value;
  } else {
    console.warn(`Unknown API key: ${keyName}`);
  }
}

// Export all keys for direct access if needed
export { API_KEYS };

// Default export
export default {
  getApiKey,
  hasApiKey,
  getConfiguredKeys,
  setApiKey,
  API_KEYS
};
