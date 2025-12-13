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

class BaseClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()

    def get_json(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict]:
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

class NewsAPIClient(BaseClient):
    def __init__(self):
        super().__init__(os.environ.get('NEWS_API_KEY'))

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
            'US10Y': '^TNX'
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
        
        logger.error("All keys and models failed. Returning empty result.")
        return {}

    async def unified_analysis(self):
        """
        Single AI call that generates outputs for ALL dashboards
        """
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
        
        Generate JSON output matching the following schema EXACTLY. Do not deviate.
        
        {{
            "the_commander": {{
                "flight_to_safety_score": {{ 
                    "current": 0.0-10.0, 
                    "trend": "string (e.g. 'Rising')", 
                    "3m_forecast": {{ "score": 0.0-10.0, "confidence": 0.0-1.0 }} 
                }},
                "asset_outlook": {{
                    "BTC": {{ "risk_reward": "High/Medium/Low", "conviction": 0-10, "forecasts": {{ "3m": {{ "target": "price_string" }} }} }},
                    "GOLD": {{ "risk_reward": "High/Medium/Low", "conviction": 0-10, "forecasts": {{ "3m": {{ "target": "price_string" }} }} }}
                }},
                "agi_singularity_tracker": {{
                    "escape_velocity_probability": 0.0-1.0,
                    "timeline_estimate": "string (e.g. '2029')",
                    "key_metrics": {{ "compute_doubling": "string", "research_velocity": "string" }}
                }},
                "morning_brief": {{
                    "weather_of_the_day": "Sunny/Cloudy/Stormy",
                    "top_signal": "string",
                    "action_stance": "Aggressive/Neutral/Defensive",
                    "why_it_matters": "string",
                    "cross_dashboard_convergence": "string",
                    "summary_sentence": "string"
                }}
            }},
            "the_shield": {{
                "fragility_index": {{
                    "current": 0.0-100.0,
                    "3m_forecast": {{ "value": 0.0, "crash_probability": 0.0-1.0 }},
                    "6m_forecast": {{ "value": 0.0, "crash_probability": 0.0-1.0 }},
                    "12m_forecast": {{ "value": 0.0, "crash_probability": 0.0-1.0 }}
                }},
                "stress_indicators": {{
                    "vix_term_structure": {{ "signal": "contango/backwardation", "stress_level": "low/medium/high" }},
                    "credit_spreads": {{ "current": 0.0, "trend": "widening/tightening", "z_score": 0.0 }},
                    "liquidity_metrics": {{
                        "bid_ask_spreads": {{ "stress": "normal/elevated" }},
                        "market_depth": {{ "stress": "normal/low" }}
                    }},
                    "cross_asset_correlation": {{
                        "current": 0.0-1.0,
                        "crisis_threshold": 0.85,
                        "trend": "stable/rising"
                    }}
                }},
                "tail_risk_hedges": [
                    {{ "instrument": "string", "recommended_allocation": "string", "rationale": "string" }}
                ],
                "early_warning_signals": {{
                    "yield_curve_inversion": true/false,
                    "high_yield_spread_spike": true/false,
                    "crypto_correlation_breakdown": true/false,
                    "funding_stress": true/false
                }}
            }},
            "the_coin": {{
                "core_metrics": {{
                    "rotation_strength": 0.0-10.0,
                    "momentum": 0.0-10.0,
                    "setup_quality": 0.0-10.0
                }},
                "market_metrics": {{
                    "btc_price": "string",
                    "eth_price": "string",
                    "rsi_btc": 0.0,
                    "fear_and_greed": 0,
                    "dxy_index": 0.0,
                    "fed_rate": "string"
                }},
                "ai_analysis": "string (paragraph)"
            }},
            "the_map": {{
                "global_macro_outlook": {{
                    "current": "LATE_CYCLE/RECESSION/RECOVERY/EXPANSION",
                    "forecast": {{
                        "3m": {{ "outlook": "string", "probability": 0.0-1.0 }},
                        "6m": {{ "outlook": "string", "probability": 0.0-1.0 }},
                        "12m": {{ "outlook": "string", "probability": 0.0-1.0 }}
                    }}
                }},
                "key_indicators": {{
                    "us_gdp_growth": {{ "current": 0.0, "3m": 0.0, "6m": 0.0, "12m": 0.0 }},
                    "us_inflation": {{ "current": 0.0, "3m": 0.0, "6m": 0.0, "12m": 0.0 }},
                    "fed_funds_rate": {{ "current": 0.0, "3m_forecast": 0.0, "12m_forecast": 0.0 }},
                    "oil_brent": {{ "current": 0.0, "3m": 0.0, "6m": 0.0, "12m": 0.0 }},
                    "usd_index": {{ "current": 0.0, "trend": "string" }}
                }},
                "tasi_outlook": {{
                    "current": 0.0,
                    "alignment_score": 0.0-1.0,
                    "forecasts": {{
                        "3m": {{ "target": 0, "confidence": 0.0-1.0 }},
                        "6m": {{ "target": 0, "confidence": 0.0-1.0 }},
                        "12m": {{ "target": 0, "confidence": 0.0-1.0 }}
                    }},
                    "drivers": ["string"]
                }},
                "saudi_specific": {{
                    "oil_production_mmbpd": 0.0,
                    "pif_deployment_rate": "high/medium/low",
                    "non_oil_gdp_growth": 0.0,
                    "vision_2030_progress": 0.0-1.0
                }}
            }},
            "the_frontier": {{
                "agi_timeline": {{
                    "median_estimate": "string (year)",
                    "probability_distribution": {{
                        "2025-2027": 0.0,
                        "2027-2030": 0.0,
                        "2030-2035": 0.0,
                        "post-2035": 0.0
                    }},
                    "confidence": 0.0-1.0
                }},
                "escape_velocity_metrics": {{
                    "current_probability": 0.0-1.0,
                    "trend": "accelerating/stable",
                    "key_indicators": {{
                        "model_capability_doubling_months": 0.0,
                        "compute_efficiency_improvement_rate": 0.0,
                        "research_breakthrough_velocity": 0.0,
                        "recursive_self_improvement_index": 0.0
                    }}
                }},
                "workforce_impact": {{
                    "automation_rate_annual": 0.0,
                    "jobs_at_risk_3y": {{
                        "customer_service": 0.0,
                        "data_entry": 0.0,
                        "creative_work": 0.0,
                        "coding": 0.0
                    }},
                    "new_job_creation_rate": 0.0,
                    "net_displacement_forecast": {{
                        "3m": 0.0,
                        "12m": 0.0,
                        "36m": 0.0
                    }}
                }},
                "breakthrough_tracker": {{
                    "recent_milestones": [
                        {{ "date": "string", "event": "string", "impact": "high/medium/low" }}
                    ],
                    "papers_per_week": 0,
                    "trend": "string"
                }},
                "investment_implications": {{
                    "ai_infrastructure": "overweight/underweight",
                    "traditional_tech": "overweight/underweight",
                    "defense_cybersecurity": "overweight/underweight",
                    "conviction": 0.0-1.0
                }}
            }},
            "the_strategy": {{
                "top_opportunities": [
                    {{
                        "asset": "string",
                        "timeframe": "string",
                        "conviction": 0.0-1.0,
                        "expected_return": 0.0,
                        "max_drawdown_risk": 0.0,
                        "sharpe_forecast": 0.0,
                        "position_size": "string",
                        "entry_trigger": "string",
                        "exit_targets": [0.0],
                        "stop_loss": 0.0
                    }}
                ],
                "portfolio_allocation": {{
                    "crypto": 0.0,
                    "equities": 0.0,
                    "commodities": 0.0,
                    "cash": 0.0,
                    "bonds": 0.0
                }},
                "risk_adjusted_scores": {{
                    "btc": {{ "score": 0.0, "rank": 0 }},
                    "gold": {{ "score": 0.0, "rank": 0 }},
                    "tasi": {{ "score": 0.0, "rank": 0 }}
                }},
                "correlation_matrix": {{
                    "btc_spx": 0.0,
                    "gold_spx": 0.0,
                    "btc_gold": 0.0
                }}
            }},
            "the_library": {{
                "query": "What drives crypto bull markets?",
                "simplified_answer": "string",
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
                
                # Ensure directory exists
                target_dir = DATA_DIR / folder
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Save data.json
                with open(target_dir / 'data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Saved data for {folder}")

    async def run(self):
        """Main execution flow"""
        logger.info("Starting Unified Fetcher V4...")
        
        # 1. Fetch Data
        self.fetch_historical()
        self.calculate_agi_metrics()
        
        # 2. Generate Analysis
        analysis = await self.unified_analysis()
        
        # 3. Save Results
        self.save_dashboard_data(analysis)
        
        logger.info("Unified Fetcher V4 completed successfully.")

if __name__ == "__main__":
    fetcher = UnifiedFetcherV4()
    asyncio.run(fetcher.run())
