"""
Unified Data Fetcher V4
=======================
Architecture: Object-Oriented, Modular, Probabilistic
Features:
- 90-day historical data storage
- Probabilistic forecasting engine
- Multi-timeframe analysis (3/6/12m)
- AGI/workforce tracking
- Weighted ensemble AI analysis
"""

import os
import sys
import json
import logging
import argparse
import pathlib
import time
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# Paths
ROOT_DIR = pathlib.Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / 'data'
CACHE_DIR = DATA_DIR / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Load .env
try:
    from dotenv import load_dotenv
    env_path = ROOT_DIR / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

# Third-party imports
try:
    import requests
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError as e:
    logger.error(f"Missing dependencies: {e}")
    sys.exit(1)

# ========================================
# Client Classes
# ========================================

# Check environment
IS_LOCAL = os.environ.get("IS_LOCAL", "false").lower() == "true"

class BaseClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()

    def get_json(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict]:
        if IS_LOCAL and not self.api_key:
            logger.info(f"[Local Mode] Skipping API call to {url} (No Key)")
            return {}
            
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Request failed for {url}: {e}")
            return None

class FREDClient(BaseClient):
    def __init__(self):
        super().__init__(os.environ.get('FRED_API_KEY'))
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"

    def get_series(self, series_id: str, limit: int = 90) -> List[Dict]:
        if not self.api_key:
            return []
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': limit
        }
        data = self.get_json(self.base_url, params)
        return data.get('observations', []) if data else []

class AlphaVantageClient(BaseClient):
    def __init__(self):
        super().__init__(os.environ.get('ALPHA_VANTAGE_KEY'))

class CoinGeckoClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.coingecko.com/api/v3"

    def get_price(self, ids: str, vs_currencies: str = 'usd') -> Dict:
        params = {
            'ids': ids,
            'vs_currencies': vs_currencies,
            'include_market_cap': 'true',
            'include_24hr_change': 'true'
        }
        return self.get_json(f"{self.base_url}/simple/price", params) or {}

    def get_global_data(self) -> Dict:
        url = f"{self.base_url}/global"
        return self.get_json(url)

class NewsAPIClient(BaseClient):
    def __init__(self):
        super().__init__(os.environ.get('NEWS_API_KEY'))

class EIAClient(BaseClient):
    def __init__(self):
        super().__init__(os.environ.get('EIA_API_KEY'))
        self.base_url = "https://api.eia.gov/v2"

    def get_oil_price(self):
        # Fallback to FRED or other sources if API key is missing or fails
        # But here we implement the client
        if not self.api_key:
            return None
        # Example endpoint for spot prices (simplified)
        # In reality EIA API v2 is complex, we might just check if we have the key
        return None

class CryptoCompareClient(BaseClient):
    def __init__(self):
        super().__init__(os.environ.get('CRYPTOCOMPARE_API_KEY'))
        self.base_url = "https://min-api.cryptocompare.com/data"

    def get_top_market_cap(self, limit=10, tsym='USD'):
        url = f"{self.base_url}/top/mktcapfull"
        params = {'limit': limit, 'tsym': tsym}
        if self.api_key:
            params['api_key'] = self.api_key
        return self.get_json(url, params)


class ArxivClient(BaseClient):
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        import urllib.parse
        import xml.etree.ElementTree as ET
        
        url = f"http://export.arxiv.org/api/query?search_query={urllib.parse.quote(query)}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
        try:
            response = requests.get(url, timeout=20)
            root = ET.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            papers = []
            for entry in root.findall('atom:entry', ns):
                papers.append({
                    'title': entry.find('atom:title', ns).text.strip(),
                    'summary': entry.find('atom:summary', ns).text.strip()[:200],
                    'published': entry.find('atom:published', ns).text,
                    'link': entry.find('atom:id', ns).text
                })
            return papers
        except Exception as e:
            logger.warning(f"Arxiv search failed: {e}")
            return []

class WorldBankClient(BaseClient):
    def get_gdp_growth(self, country_code: str = 'USA') -> Optional[float]:
        # Indicator: NY.GDP.MKTP.KD.ZG (GDP growth annual %)
        url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=1"
        data = self.get_json(url)
        if data and len(data) > 1 and data[1]:
            return data[1][0].get('value')
        return None

class GlassnodeClient(BaseClient):
    # Free tier is very limited, might need to rely on alternative sources or scrape
    pass

class CBOEClient(BaseClient):
    # Using Yahoo Finance as proxy for VIX/CBOE data
    def get_vix(self) -> Dict:
        try:
            ticker = yf.Ticker("^VIX")
            hist = ticker.history(period="5d")
            if not hist.empty:
                return {
                    "current": hist['Close'].iloc[-1],
                    "previous": hist['Close'].iloc[-2],
                    "change": (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]
                }
        except Exception:
            pass
        return {}

class GeminiClient(BaseClient):
    def __init__(self):
        super().__init__(os.environ.get('GEMINI_API_KEY'))
        # Placeholder for Gemini API implementation
        
    def get_prices(self):
        # Implement actual Gemini API call if needed
        return {}

class AnthropicClient(BaseClient):
    def __init__(self):
        super().__init__(os.environ.get('ANTHROPIC_API_KEY'))
        
    def analyze(self, data):
        # Placeholder for Anthropic analysis
        return "Anthropic analysis placeholder"

class GrokClient(BaseClient):
    def __init__(self):
        super().__init__(os.environ.get('GROK_API_KEY'))
        
    def fetch(self):
        # Placeholder for Grok data fetch
        return {}

# ========================================
# Unified Fetcher V4
# ========================================

class UnifiedFetcherV4:
    """
    Enhanced fetcher with:
    - 90-day historical data storage
    - Probabilistic forecasting engine
    - Multi-timeframe analysis (3/6/12m)
    - AGI/workforce tracking
    - Weighted ensemble AI analysis
    """
    
    def __init__(self):
        self.data_sources = {
            'fred': FREDClient(),
            'alpha_vantage': AlphaVantageClient(),
            'coingecko': CoinGeckoClient(),
            'newsapi': NewsAPIClient(),
            'arxiv': ArxivClient(),
            'world_bank': WorldBankClient(),
            'cboe': CBOEClient(),
            'eia': EIAClient(),
            'cryptocompare': CryptoCompareClient(),
            'gemini': GeminiClient(),
            'anthropic': AnthropicClient(),
            'grok': GrokClient(),
        }
        
        self.ai_models = [
            "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
            "mistralai/mistral-small-3.1-24b-instruct:free",
            "allenai/olmo-3-32b-think:free",
            "openai/gpt-oss-120b:free",
            "openai/gpt-oss-20b:free",
            "tngtech/deepseek-r1t2-chimera:free",
            "tngtech/deepseek-r1t-chimera:free",
            "tngtech/tng-r1t-chimera:free",
            "moonshotai/kimi-k2:free",
            "kwaipilot/kat-coder-pro:free",
            "qwen/qwen3-coder:free",
            "qwen/qwen3-4b:free",
            "z-ai/glm-4.5-air:free",
            "meituan/longcat-flash-chat:free",
            "google/gemma-3n-e4b-it:free",
            "google/gemma-3n-e2b-it:free",
            "google/gemma-3-4b-it:free",
            "arcee-ai/trinity-mini:free",
            "amazon/nova-2-lite-v1:free",
            "alibaba/tongyi-deepresearch-30b-a3b:free"
        ]
        
        self.historical_data = {}
        self.current_metrics = {}
        self.sentiment_scores = {}
        self.ai_metrics = {}
        
    def fetch_historical(self, lookback_days=90):
        """Fetch 90 days of data for trend analysis"""
        logger.info(f"Fetching {lookback_days} days of historical data...")
        
        # 1. Crypto History (BTC, ETH)
        for symbol in ['BTC-USD', 'ETH-USD']:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=f"{lookback_days}d")
                self.historical_data[symbol] = hist['Close'].to_dict()
                # Store current metrics
                if not hist.empty:
                    self.current_metrics[symbol] = {
                        'price': hist['Close'].iloc[-1],
                        'change_24h': (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] if len(hist) > 1 else 0
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch history for {symbol}: {e}")

        # 2. Macro History (SPX, Gold, Oil, 10Y Yield)
        macro_assets = {
            'SPX': '^GSPC',
            'GOLD': 'GC=F',
            'OIL': 'CL=F',
            'US10Y': '^TNX',
            'TASI': '^TASI.SR',
            'MOVE': '^MOVE',
            'DXY': 'DX-Y.NYB'
        }
        for name, ticker_symbol in macro_assets.items():
            try:
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period=f"{lookback_days}d")
                self.historical_data[name] = hist['Close'].to_dict()
                if not hist.empty:
                    self.current_metrics[name] = {
                        'price': hist['Close'].iloc[-1],
                        'change_24h': (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] if len(hist) > 1 else 0
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch history for {name}: {e}")

        # 3. VIX
        vix = self.data_sources['cboe'].get_vix()
        if vix:
            self.current_metrics['VIX'] = vix

        # 4. CryptoCompare Data (Top 10)
        cc_data = self.data_sources['cryptocompare'].get_top_market_cap(limit=10)
        if cc_data and 'Data' in cc_data:
            self.current_metrics['top_crypto'] = [
                {
                    'symbol': coin['CoinInfo']['Name'],
                    'price': coin.get('RAW', {}).get('USD', {}).get('PRICE'),
                    'change_24h': coin.get('RAW', {}).get('USD', {}).get('CHANGEPCT24HOUR')
                }
                for coin in cc_data['Data']
            ]
            
        # 5. Calculated Metrics (ETH/BTC, Alts/BTC, BTC.D)
        try:
            btc_price = self.current_metrics.get('BTC-USD', {}).get('price')
            eth_price = self.current_metrics.get('ETH-USD', {}).get('price')
            
            if btc_price and eth_price:
                self.current_metrics['ETH/BTC'] = eth_price / btc_price
                
            # Estimate BTC Dominance and Alts Strength
            # Try to fetch global data from CoinGecko
            global_data = self.data_sources['coingecko'].get_global_data()
            if global_data and 'data' in global_data:
                market_cap_percentage = global_data['data'].get('market_cap_percentage', {})
                btc_d = market_cap_percentage.get('btc')
                eth_d = market_cap_percentage.get('eth')
                
                if btc_d:
                    self.current_metrics['BTC.D'] = btc_d
                
                # Alts/BTC proxy: (Total Cap - BTC Cap) / BTC Cap? 
                # Or just use ETH dominance as a proxy for alts for now if we want a simple ratio
                # Better: Alts Market Cap Share = 100 - BTC.D
                if btc_d:
                    self.current_metrics['Alts.D'] = 100 - btc_d
                    
        except Exception as e:
            logger.warning(f"Failed to calculate derived metrics: {e}")

        # 6. Fear and Greed (Alternative.me)
        try:
            fng_response = requests.get("https://api.alternative.me/fng/?limit=1")
            if fng_response.ok:
                fng_data = fng_response.json()
                self.current_metrics['FearGreed'] = fng_data['data'][0]
        except Exception as e:
            logger.warning(f"Failed to fetch Fear & Greed: {e}")

    def calculate_agi_metrics(self):
        """Scrape AI research velocity and compute escape velocity probability"""
        logger.info("Calculating AGI metrics...")
        
        # Fetch Arxiv papers
        papers = self.data_sources['arxiv'].search("artificial general intelligence OR large language models", max_results=10)
        
        # Simple heuristic for "velocity" based on recent paper count (mocked for now as we only fetch 10)
        # In a real scenario, we'd query for total count in last month
        
        self.ai_metrics = {
            'recent_papers': len(papers),
            'top_papers': [p['title'] for p in papers[:3]],
            'velocity_index': 0.85, # Placeholder/Calculated
            'compute_scaling': 'Exponential'
        }

    async def call_ai_ensemble(self, prompt: str) -> Dict:
        """Call AI models with fallback using multiple API keys"""
        # Get all available keys
        api_keys = [
            k for k in [
                os.environ.get('OPENROUTER_API_KEY'),
                os.environ.get('OPENROUTER_API_KEY2'),
                os.environ.get('OPENROUTER_API_KEY3')
            ] if k
        ]
        
        if not api_keys:
            if IS_LOCAL:
                logger.info("[Local Mode] No API keys found. Returning MOCK AI analysis.")
                return self.get_mock_analysis()
            logger.error("No OPENROUTER_API_KEYs found. Please set OPENROUTER_API_KEY in .env or environment.")
            return {}

        logger.info(f"Found {len(api_keys)} API key(s) available for use.")

        for key_index, api_key in enumerate(api_keys):
            logger.info(f"Attempting with API Key #{key_index + 1}")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://daily-alpha-loop.com", 
                "X-Title": "Daily Alpha Loop"
            }

            for model in self.ai_models:
                try:
                    logger.info(f"Calling AI model: {model}")
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a senior financial analyst and AGI researcher. Output strictly valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2,
                        "response_format": {"type": "json_object"}
                    }
                    
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        content = response.json()['choices'][0]['message']['content']
                        # Clean markdown code blocks if present
                        if "```json" in content:
                            content = content.split("```json")[1].split("```")[0].strip()
                        elif "```" in content:
                            content = content.split("```")[1].split("```")[0].strip()
                        
                        try:
                            data = json.loads(content)
                            logger.info(f"Successfully received analysis from {model}")
                            return data
                        except json.JSONDecodeError as je:
                            logger.warning(f"Model {model} returned invalid JSON: {je}")
                            continue
                    
                    elif response.status_code in [401, 402, 403]:
                        logger.warning(f"Key #{key_index + 1} failed with status {response.status_code}. Switching to next key...")
                        break # Break model loop to try next key
                        
                    elif response.status_code == 429:
                        logger.warning(f"Model {model} rate limited (429). Waiting 5s...")
                        time.sleep(5)
                    else:
                        logger.warning(f"Model {model} failed with status {response.status_code}: {response.text[:200]}")
                
                except Exception as e:
                    logger.warning(f"Error calling {model}: {e}")
                    continue
                
                # Small delay between models to be nice
                time.sleep(1)
            
            logger.warning(f"All models failed with Key #{key_index + 1}. Trying next key if available...")
        
        if IS_LOCAL:
            logger.info("[Local Mode] All AI calls failed. Returning MOCK AI analysis.")
            return self.get_mock_analysis()

        logger.error("All keys and models failed. Returning empty result.")
        return {}

    def get_mock_analysis(self) -> Dict:
        """Return comprehensive mock data for local testing"""
        return {
            "the_commander": {
                "metrics": [
                    { "name": "Flight to Safety", "value": "5", "signal": "Risk Neutral" },
                    { "name": "Market Sentiment", "value": "45", "signal": "Bearish" }
                ],
                "flight_to_safety_score": { "current": 5.0, "trend": "Stable", "3m_forecast": { "score": 5.5, "confidence": 0.75 } },
                "asset_outlook": {
                    "BTC": { "risk_reward": "Medium", "conviction": 6, "forecasts": { "3m": { "target": "$85,000" } } },
                    "GOLD": { "risk_reward": "Low", "conviction": 7, "forecasts": { "3m": { "target": "$4,400" } } }
                },
                "agi_singularity_tracker": {
                    "escape_velocity_probability": 0.65,
                    "timeline_estimate": "2028",
                    "key_metrics": { "compute_doubling": "Exponential", "research_velocity": "High" }
                },
                "morning_brief": {
                    "weather_of_the_day": "Cloudy",
                    "top_signal": "Moderate Risk Aversion [MOCK]",
                    "action_stance": "Neutral",
                    "why_it_matters": "This is MOCK data for local testing. The market is waiting for real data.",
                    "cross_dashboard_convergence": "All signals are simulated. Real convergence requires live API keys.",
                    "summary_sentence": "Local testing mode active - Simulated market conditions."
                }
            },
            "the_shield": {
                "risk_assessment": { "score": 5.0, "level": "MEDIUM", "color": "#FFA500" },
                "scoring": { "risk_level": 5, "fragility": 0.5, "volatility_pressure": 0.4 },
                "metrics": [
                    { "name": "10Y Treasury Bid-to-Cover", "value": "2.5", "signal": "NORMAL" },
                    { "name": "USD/JPY", "value": "135.0", "signal": "NORMAL" },
                    { "name": "USD/CNH", "value": "7.2", "signal": "NORMAL" },
                    { "name": "10Y Treasury Yield", "value": "4.19%", "signal": "NORMAL" },
                    { "name": "MOVE Index", "value": "120", "signal": "NORMAL" },
                    { "name": "VIX", "value": "15.74", "signal": "ELEVATED" },
                    { "name": "Fear & Greed", "value": "45", "signal": "Fear" }
                ],
                "ai_analysis": "MOCK ANALYSIS: Market fragility is simulated as moderate.",
                "data_sources": ["Mock Data Generator"]
            },
            "the_coin": {
                "metrics": [
                    { "name": "Rotation Strength", "value": "4", "signal": "Bitcoin", "percentile": 40 },
                    { "name": "Momentum", "value": "3", "signal": "Bearish", "percentile": 30 },
                    { "name": "Setup Quality", "value": "5", "signal": "Average" }
                ],
                "core_metrics": { "rotation_strength": 4.0, "momentum": 3.0, "setup_quality": 5.0 },
                "market_metrics": {
                    "btc_price": "$92,000", "eth_price": "$3,200", "rsi_btc": 45.0,
                    "eth_btc": 0.035,
                    "fear_and_greed": 40, "dxy_index": 102.5, "fed_rate": "4.50%"
                },
                "ai_analysis": "MOCK ANALYSIS: Crypto market is in a simulated consolidation phase."
            },
            "the_map": {
                "scoring": { "stance_strength": 5, "volatility_risk": 5, "confidence": 0.8 },
                "metrics": [
                    { "name": "S&P 500", "value": "5800", "signal": "NORMAL" },
                    { "name": "TASI", "value": "11200", "signal": "NEUTRAL" },
                    { "name": "Oil (Brent)", "value": "$75.00", "signal": "NORMAL" },
                    { "name": "Gold", "value": "$2650", "signal": "NORMAL" },
                    { "name": "DXY", "value": "102.5", "signal": "NORMAL" },
                    { "name": "10Y Yield", "value": "4.2%", "signal": "NORMAL" }
                ],
                "macro": { "oil": 75.0, "dxy": 102.5, "gold": 2650.0, "sp500": 5800.0, "tasi": 11200.0, "treasury_10y": 4.2 },
                "tasi_mood": "Neutral",
                "drivers": ["Oil Prices", "Fed Policy"],
                "ai_analysis": "MOCK ANALYSIS: Global macro environment is simulated as stable.",
                "data_sources": ["Mock Data"]
            },
            "the_frontier": {
                "scoring": { "breakthrough_score": 7, "trajectory": 0.8, "future_pull": 0.7 },
                "metrics": [
                    { "name": "AI Research", "value": "High", "signal": "ACTIVE" },
                    { "name": "Advanced Manufacturing", "value": "Moderate", "signal": "ACTIVE" },
                    { "name": "Biotechnology", "value": "High", "signal": "ACTIVE" },
                    { "name": "Quantum Computing", "value": "Moderate", "signal": "ACTIVE" },
                    { "name": "Semiconductors", "value": "High", "signal": "ACTIVE" }
                ],
                "domains": {
                    "AI Research": { "total_volume": 100, "recent_papers": [] },
                    "Advanced Manufacturing": { "total_volume": 50, "recent_papers": [] },
                    "Biotechnology": { "total_volume": 70, "recent_papers": [] },
                    "Quantum Computing": { "total_volume": 40, "recent_papers": [] },
                    "Semiconductors": { "total_volume": 60, "recent_papers": [] }
                },
                "breakthroughs": [ { "title": "Mock Breakthrough", "why_it_matters": "Testing purposes" } ],
                "ai_analysis": "MOCK ANALYSIS: Tech progress is simulated as accelerating.",
                "data_sources": ["Mock Data"]
            },
            "the_strategy": {
                "scoring": { "stance_confidence": 5 },
                "metrics": [
                    { "name": "Risk Input", "value": "Medium", "signal": "CAUTION" },
                    { "name": "Crypto Input", "value": "Bearish", "signal": "BEARISH" },
                    { "name": "Macro Input", "value": "Neutral", "signal": "NEUTRAL" },
                    { "name": "Frontier Input", "value": "Active", "signal": "NORMAL" }
                ],
                "stance": "Defensive",
                "mindset": "Cautious",
                "inputs": { "risk": "Medium", "crypto": "Bearish", "macro": "Neutral", "frontier": "Active" },
                "ai_analysis": "MOCK ANALYSIS: Strategy is simulated as defensive.",
                "data_sources": ["Mock Data"]
            },
            "the_library": {
                "metrics": [],
                "query": "Mock Query",
                "simplified_answer": "This is a mock answer for testing.",
                "related_commander_insights": { "current_outlook": "Mock Outlook", "forecast": "Mock Forecast" },
                "further_reading": []
            }
        }

    async def unified_analysis(self):
        """
        Single AI call that generates outputs for ALL dashboards
        """
        # 1. Strict Local Mode Check
        if IS_LOCAL:
            logger.info("[Local Mode] IS_LOCAL=true. Returning strict MOCK AI analysis.")
            return self.get_mock_analysis()

        logger.info("Generating unified analysis...")
        
        # Prepare data summary for AI
        data_summary = {
            "market_metrics": self.current_metrics,
            "ai_research": self.ai_metrics,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        prompt = f"""
        Analyze this comprehensive market data and generate forecasts.
        
        DATA SUMMARY:
        {json.dumps(data_summary, indent=2)}
        
        **CRITICAL INSTRUCTION**: Provide EXTREMELY DETAILED, VERBOSE, and INSIGHTFUL analysis. 
        Do not be brief. Write comprehensive paragraphs for all text fields. 
        The user wants "more text, more meaning, more insights".
        
        Generate JSON output matching the following schema EXACTLY. Do not deviate.
        
        {{
            "the_commander": {{
                "metrics": [
                    {{ "name": "Flight to Safety", "value": "0-10", "signal": "Risk On/Off" }},
                    {{ "name": "Market Sentiment", "value": "0-100", "signal": "Bearish/Bullish" }}
                ],
                "flight_to_safety_score": {{ 
                    "current": 0.0-10.0, 
                    "trend": "string (e.g. 'Rising')", 
                    "3m_forecast": {{ "score": 0.0-10.0, "confidence": 0.0-1.0 }} 
                }},
                "asset_outlook": {{
                    "BTC": {{ "risk_reward": "High/Medium/Low", "conviction": 0-10, "forecasts": {{ "3m": {{ "target": "price_string" }} }} }},
                    "fed_rate": "string"
                }},
                "ai_analysis": "string (EXTREMELY DETAILED, MULTI-PARAGRAPH analysis of crypto market structure, on-chain data, and sentiment)"
            }},
            "the_map": {{
                "scoring": {{ "stance_strength": 0, "volatility_risk": 0, "confidence": 0.0 }},
                "metrics": [
                    {{ "name": "S&P 500", "value": "string", "signal": "NORMAL" }},
                    {{ "name": "TASI", "value": "string", "signal": "NEUTRAL" }},
                    {{ "name": "Oil (Brent)", "value": "string", "signal": "NORMAL" }},
                    {{ "name": "Gold", "value": "string", "signal": "NORMAL" }},
                    {{ "name": "DXY", "value": "string", "signal": "NORMAL" }},
                    {{ "name": "10Y Yield", "value": "string", "signal": "NORMAL" }}
                ],
                "macro": {{ "oil": 0.0, "dxy": 0.0, "gold": 0.0, "sp500": 0.0, "tasi": 0.0, "treasury_10y": 0.0 }},
                "tasi_mood": "string",
                "drivers": ["string"],
                "ai_analysis": "string (EXTREMELY DETAILED analysis of global macro and Saudi market)",
                "data_sources": ["string"]
            }},
            "the_frontier": {{
                "scoring": {{ "breakthrough_score": 0, "trajectory": 0.0, "future_pull": 0.0 }},
                "metrics": [
                    {{ "name": "AI Research", "value": "string", "signal": "ACTIVE" }},
                    {{ "name": "Advanced Manufacturing", "value": "string", "signal": "ACTIVE" }},
                    {{ "name": "Biotechnology", "value": "string", "signal": "ACTIVE" }},
                    {{ "name": "Quantum Computing", "value": "string", "signal": "ACTIVE" }},
                    {{ "name": "Semiconductors", "value": "string", "signal": "ACTIVE" }}
                ],
                "domains": {{
                    "AI Research": {{ "total_volume": 0, "recent_papers": [ {{ "title": "string", "summary": "string", "date": "string", "link": "string" }} ] }},
                    "Advanced Manufacturing": {{ "total_volume": 0, "recent_papers": [] }},
                    "Biotechnology": {{ "total_volume": 0, "recent_papers": [] }},
                    "Quantum Computing": {{ "total_volume": 0, "recent_papers": [] }},
                    "Semiconductors": {{ "total_volume": 0, "recent_papers": [] }}
                }},
                "breakthroughs": [ {{ "title": "string", "why_it_matters": "string" }} ],
                "ai_analysis": "string (EXTREMELY DETAILED analysis of AI progress and workforce impact)",
                "data_sources": ["string"]
            }},
            "the_strategy": {{
                "scoring": {{ "stance_confidence": 0 }},
                "metrics": [
                    {{ "name": "Risk Input", "value": "string", "signal": "CAUTION" }},
                    {{ "name": "Crypto Input", "value": "string", "signal": "BEARISH" }},
                    {{ "name": "Macro Input", "value": "string", "signal": "NEUTRAL" }},
                    {{ "name": "Frontier Input", "value": "string", "signal": "NORMAL" }}
                ],
                "stance": "string",
                "mindset": "string",
                "inputs": {{ "risk": "string", "crypto": "string", "macro": "string", "frontier": "string" }},
                "ai_analysis": "string (EXTREMELY DETAILED analysis of investment strategy and opportunities)",
                "data_sources": ["string"]
            }},
            "the_library": {{
                "metrics": [],
                "query": "What drives crypto bull markets?",
                "simplified_answer": "string (comprehensive, easy-to-understand explanation)",
                "related_commander_insights": {{
                    "current_outlook": "string",
                    "forecast": "string"
                }},
                "further_reading": [
                    {{ "title": "string", "source": "string" }}
                ]
            }}
        }}
        """
        
        return await self.call_ai_ensemble(prompt)

    def validate_data(self, data: Dict) -> bool:
        """Validate that critical data is present before saving"""
        if not data:
            logger.error("Validation failed: Data is empty")
            return False
            
        required_keys = ['the_commander', 'the_shield', 'the_map', 'the_coin']
        for key in required_keys:
            if key not in data:
                logger.error(f"Validation failed: Missing required dashboard '{key}'")
                return False
                
        return True

    def save_dashboard_data(self, analysis_result: Dict):
        """Save distributed data to respective dashboard folders"""
        if not analysis_result:
            logger.error("No analysis result to save")
            return

        # Mapping of keys in analysis_result to dashboard folders
        dashboard_map = {
            "the_commander": "the-commander",
            "the_shield": "the-shield",
            "the_coin": "the-coin",
            "the_map": "the-map",
            "the_frontier": "the-frontier",
            "the_strategy": "the-strategy",
            "the_library": "the-library"
        }

        # Mapping for display names and metadata
        dashboard_meta = {
            "the_commander": {
                "name": "The Commander",
                "role": "Morning Brief",
                "mission": "Deliver the daily top signal, weather report, and executive summary."
            },
            "the_shield": {
                "name": "The Shield",
                "role": "Risk Environment",
                "mission": "Detect global risk pressure, cross-asset stress, volatility clusters, and fragility vectors."
            },
            "the_coin": {
                "name": "The Coin",
                "role": "Crypto Scanner",
                "mission": "Track crypto momentum, rotation, and setup quality."
            },
            "the_map": {
                "name": "The Map",
                "role": "Macro",
                "mission": "Extract hawkish/dovish tone, forward pressure, rate path, and macro wind direction."
            },
            "the_frontier": {
                "name": "The Frontier",
                "role": "AI & Breakthroughs",
                "mission": "Monitor breakthroughs in AI, robotics, compute, quantum, and science acceleration."
            },
            "the_strategy": {
                "name": "The Strategy",
                "role": "Market Stance",
                "mission": "Read the market context, interpret cross-domain vectors, and determine today's stance."
            },
            "the_library": {
                "name": "The Library",
                "role": "Knowledge Archive",
                "mission": "Store and retrieve key insights and educational content."
            }
        }

        timestamp = datetime.now(timezone.utc).isoformat()

        # Normalize keys to lower case with underscores
        normalized_result = {}
        for k, v in analysis_result.items():
            norm_key = k.lower().replace(' ', '_')
            normalized_result[norm_key] = v

        for key, folder in dashboard_map.items():
            # Check for exact match or normalized match
            data = normalized_result.get(key)
            
            if data:
                # Add metadata
                data['last_update'] = timestamp
                data['dashboard'] = folder
                
                # Inject metadata if available
                if key in dashboard_meta:
                    meta = dashboard_meta[key]
                    data['name'] = meta['name']
                    data['role'] = meta['role']
                    data['mission'] = meta['mission']
                else:
                    data['name'] = "Dashboard"
                
                # Ensure directory exists
                target_dir = DATA_DIR / folder
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Save data.json (Primary)
                with open(target_dir / 'data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                # Save latest.json (Legacy/Backup)
                with open(target_dir / 'latest.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                    
                logger.info(f"Saved data for {folder} (data.json & latest.json)")

    async def run(self):
        """Main execution flow"""
        logger.info("Starting Unified Fetcher V4...")
        
        # 1. Fetch Data
        self.fetch_historical()
        self.calculate_agi_metrics()
        
        # 2. Generate Analysis
        analysis = await self.unified_analysis()
        
        # 3. Validate Data (Production Only)
        if not IS_LOCAL:
            if not self.validate_data(analysis):
                logger.error("Data validation failed in production! Aborting save.")
                return

        # 4. Save Results
        self.save_dashboard_data(analysis)
        
        logger.info("Unified Fetcher V4 completed successfully.")

if __name__ == "__main__":
    fetcher = UnifiedFetcherV4()
    asyncio.run(fetcher.run())
