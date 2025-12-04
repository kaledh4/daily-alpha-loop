/**
 * Unified AI Service
 * ===================
 * Centralized AI/LLM integration for ALL dashboard applications.
 * Supports multiple models through OpenRouter.
 * 
 * ELIMINATES DUPLICATE:
 * - AI prompt building
 * - OpenRouter API calls
 * - Response parsing
 * - Error handling
 */

import { getApiKey, hasApiKey } from '@monorepo/shared-keys';
import { getCached, setCache, CACHE_TTL } from './cache.js';

// ===========================================
// Configuration
// ===========================================

/**
 * Available AI models (OpenRouter)
 */
export const AI_MODELS = {
    // Free tier models
    GROK_FAST: 'x-ai/grok-4.1-fast:free',
    GPT_OSS: 'openai/gpt-oss-20b:free',
    CHIMERA: 'tngtech/tng-r1t-chimera:free',

    // Premium models (if API key supports them)
    CLAUDE_SONNET: 'anthropic/claude-sonnet-4-20250514',
    GPT4_TURBO: 'openai/gpt-4-turbo',

    // Default
    DEFAULT: 'x-ai/grok-4.1-fast:free'
};

/**
 * Pre-built prompts for common analysis types
 */
export const PROMPT_TEMPLATES = {
    MARKET_ANALYSIS: (data) => `You are a professional market analyst. Analyze this data and provide actionable insights:

DATA:
${JSON.stringify(data, null, 2)}

Provide:
1. KEY TAKEAWAY (one sentence)
2. RISK ASSESSMENT (Low/Medium/High with reasoning)
3. ACTIONABLE RECOMMENDATIONS (3 bullet points)
4. WHAT TO WATCH NEXT (2-3 items)

Be specific with numbers. Avoid generic statements.`,

    RESEARCH_BRIEFING: (data) => `You are a research analyst. Synthesize this research data into an executive briefing:

RAW DATA:
${JSON.stringify(data, null, 2)}

FORMAT:
1. BLUF (Bottom Line Up Front) - one critical sentence
2. KEY FINDINGS (3-5 specific entities/discoveries)
3. CROSS-DOMAIN CONNECTIONS (if any)
4. PREDICTIONS with confidence scores (%)
5. RISKS & LIMITATIONS

Be data-driven. Extract specific names, formulas, version numbers.`,

    CRASH_ANALYSIS: (metrics, convergence) => `Analyze these market stress metrics for a financial fault-lines assessment:

METRICS:
${JSON.stringify(metrics, null, 2)}

CONVERGENCE DATA:
${JSON.stringify(convergence, null, 2)}

Provide:
1. OVERALL RISK LEVEL (1-10)
2. PRIMARY STRESS INDICATORS
3. POTENTIAL TRIGGER EVENTS
4. RECOMMENDED ACTIONS
5. TIMELINE ASSESSMENT

Return as JSON: { "crash_analysis": "HTML string", "risk_level": number, "summary": "string" }`,

    CRYPTO_OUTLOOK: (data) => `You are a crypto market strategist. Based on this data:

${JSON.stringify(data, null, 2)}

Provide a concise market outlook covering:
1. Current Position (relative to key levels)
2. Risk Assessment (0-1 scale interpretation)
3. Macro Factors impact
4. Short-term expectations (1-2 weeks)
5. Actionable verdict

Keep it under 500 words. Be specific with numbers.`
};

// ===========================================
// Core AI Service
// ===========================================

/**
 * Call OpenRouter AI API
 * @param {Object} options - Request options
 * @returns {Promise<string>} AI response content
 */
export async function callAI(options = {}) {
    const {
        prompt,
        systemPrompt = 'You are a helpful AI assistant.',
        model = AI_MODELS.DEFAULT,
        temperature = 0.7,
        maxTokens = 2000,
        responseFormat = null, // 'json_object' for JSON responses
        cacheKey = null,
        cacheTTL = CACHE_TTL.AI_ANALYSIS
    } = options;

    // Check cache first
    if (cacheKey) {
        const cached = getCached(cacheKey);
        if (cached) {
            console.log('[AI] Cache hit:', cacheKey);
            return cached;
        }
    }

    const apiKey = getApiKey('OPENROUTER_KEY');
    if (!apiKey) {
        console.warn('[AI] OpenRouter API key not configured');
        return { error: 'API key not configured', content: 'AI analysis unavailable.' };
    }

    try {
        const headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://kaledh4.github.io/monorepo/',
            'X-Title': 'Unified Dashboard AI'
        };

        const payload = {
            model,
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: prompt }
            ],
            temperature,
            max_tokens: maxTokens
        };

        if (responseFormat) {
            payload.response_format = { type: responseFormat };
        }

        const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
            method: 'POST',
            headers,
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`OpenRouter API error: ${response.status} - ${errorText}`);
        }

        const data = await response.json();
        const content = data.choices?.[0]?.message?.content || '';

        // Cache the result
        if (cacheKey && content) {
            setCache(cacheKey, content, cacheTTL);
        }

        return {
            content,
            model: data.model,
            usage: data.usage,
            timestamp: new Date().toISOString()
        };

    } catch (error) {
        console.error('[AI] Error:', error);
        return {
            error: error.message,
            content: 'AI analysis temporarily unavailable.',
            timestamp: new Date().toISOString()
        };
    }
}

/**
 * Parse JSON from AI response (handles markdown code blocks)
 */
export function parseAIJson(content) {
    try {
        // Try direct parse first
        return JSON.parse(content);
    } catch {
        // Try to extract JSON from markdown code block
        const jsonMatch = content.match(/```(?:json)?\s*([\s\S]*?)```/);
        if (jsonMatch) {
            return JSON.parse(jsonMatch[1].trim());
        }

        // Try to find JSON object in text
        const start = content.indexOf('{');
        const end = content.lastIndexOf('}') + 1;
        if (start !== -1 && end > start) {
            return JSON.parse(content.slice(start, end));
        }

        throw new Error('Could not parse JSON from AI response');
    }
}

// ===========================================
// Specialized Analysis Functions
// ===========================================

/**
 * Generate market analysis - UNIFIED
 * Used by: crash-detector, economic-compass, hyper-analytical
 */
export async function generateMarketAnalysis(data, options = {}) {
    const { model = AI_MODELS.GROK_FAST, appName = 'Unknown' } = options;

    return callAI({
        prompt: PROMPT_TEMPLATES.MARKET_ANALYSIS(data),
        systemPrompt: `You are a senior market analyst at ${appName}. Provide data-driven, actionable insights.`,
        model,
        cacheKey: `analysis:market:${JSON.stringify(data).slice(0, 100)}`,
        cacheTTL: CACHE_TTL.AI_ANALYSIS
    });
}

/**
 * Generate research briefing - UNIFIED
 * Used by: ai-race, free-knowledge
 */
export async function generateResearchBriefing(domains, options = {}) {
    const {
        model = AI_MODELS.GROK_FAST,
        includeArabic = false,
        includeStocks = true
    } = options;

    let prompt = PROMPT_TEMPLATES.RESEARCH_BRIEFING(domains);

    if (includeStocks) {
        prompt += `\n\n6. STOCK PICKS (5 companies that benefit from these trends with tickers)`;
    }

    if (includeArabic) {
        prompt += `\n\n<<<ARABIC_TRANSLATION>>>\nProvide a full Arabic translation of all sections above.`;
    }

    return callAI({
        prompt,
        systemPrompt: 'You are a strategic research analyst synthesizing cutting-edge research into actionable intelligence.',
        model,
        maxTokens: includeArabic ? 4000 : 2000,
        cacheKey: `analysis:research:${Object.keys(domains).join(',')}`,
        cacheTTL: CACHE_TTL.AI_ANALYSIS
    });
}

/**
 * Generate crash/stress analysis - UNIFIED
 * Used by: crash-detector
 */
export async function generateCrashAnalysis(metrics, convergence, options = {}) {
    const { model = AI_MODELS.CHIMERA } = options;

    return callAI({
        prompt: PROMPT_TEMPLATES.CRASH_ANALYSIS(metrics, convergence),
        systemPrompt: 'You are a financial risk analyst specializing in systemic risk and market stress indicators.',
        model,
        responseFormat: 'json_object',
        cacheKey: `analysis:crash:${metrics.length}:${convergence.score}`,
        cacheTTL: 30 * 60 * 1000 // 30 min for crash analysis
    });
}

/**
 * Generate crypto outlook - UNIFIED
 * Used by: hyper-analytical, economic-compass
 */
export async function generateCryptoOutlook(data, options = {}) {
    const { model = AI_MODELS.GPT_OSS } = options;

    return callAI({
        prompt: PROMPT_TEMPLATES.CRYPTO_OUTLOOK(data),
        systemPrompt: 'You are a professional crypto market analyst. Be data-driven and specific.',
        model,
        temperature: 0.4, // Lower for more consistent analysis
        cacheKey: `analysis:crypto:${data.btc_price}:${data.risk_metric}`,
        cacheTTL: CACHE_TTL.AI_ANALYSIS
    });
}

export default {
    AI_MODELS,
    PROMPT_TEMPLATES,
    callAI,
    parseAIJson,
    generateMarketAnalysis,
    generateResearchBriefing,
    generateCrashAnalysis,
    generateCryptoOutlook
};
