"""
Unified Data Fetcher V5
=======================
The definitive, all-encompassing data fetcher for Daily Alpha Loop.
Integrates the "Master Prompt" and "Strategic Stand" logic.

Features:
- Smart reuse of free_apis.py for FRED, EIA, and Alpha Vantage.
- Integrated "Master Prompt" for high-conviction portfolio guidance.
- 90-day historical data tracking.
- Multi-model AI fallback (OpenRouter).
"""

import os
import sys
import json
import logging
import pathlib
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# Add current directory to sys.path for local imports
sys.path.insert(0, str(pathlib.Path(__file__).parent))

# Import free_apis
try:
    import free_apis
    import requests
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError as e:
    logger.error(f"Missing dependencies: {e}")
    sys.exit(1)

# ========================================
# Configuration
# ========================================

IS_LOCAL = os.environ.get("IS_LOCAL", "false").lower() == "true"

# Master Prompt for "The Commander"
COMMANDER_MASTER_PROMPT = """
Role: You are the Commander, the Master Orchestrator of the Daily Alpha Loop. Your goal is to provide a high-conviction "Morning Brief" that tells me exactly what to Increase, Decrease, or Hold in my portfolio based on the 7 Dashboards and my "Old Stand."

Current Strategic "Stand" (The Baseline):
    Target Core Split: 90% Crypto / 10% Gold.
    Macro View: Rates are trending 5.4%→3%. Risk is toggling between On/Off.
    Current Inquiry: 
        1. Should Crypto be BTC-heavy or Alt/ETH-heavy? 
        2. Should the 10% Gold shift into Silver? 
        3. Which Banking sub-sectors are emerging? 
        4. Should I be "Defensive" on The Frontier (AI/Tech) or aggressive?

Input Data Sources (The 7 Dashboards):
    The Shield: Market stress/fragility. If Stress is High → Increase Gold, Decrease Alts.
    The Coin: BTC/ETH momentum. Use this for the "Crypto 90%" internal allocation.
    The Map: Global Macro (FRED/EIA) + Saudi Markets (TASI). Identify regional sector strengths.
    The Frontier: AI/Tech breakthroughs. Validate if "Defensive" stance is still right.
    The Strategy: Cross-context synthesis.
    The Library: Historical precedents.
    The Commander: Your current synthesis engine.

Your Analysis Task: Analyze the JSON data from all fetchers (using FRED for rates, EIA for energy, Alpha Vantage for stocks/crypto). Provide an "Educated Guess" on portfolio weightings.

Output Format:
1. Daily Sentiment & Risk Toggle
    Current Status: [Risk-On / Risk-Off / Transition]
    Rate Path Impact: How the 5.4→3 shift is affecting today's liquidity.

2. Portfolio Guidance (The "Increase/Decrease" List)
    Crypto (90% Bucket): [e.g., "Decrease Alts, Increase BTC" or "Rotation to ETH"] — Why?
    Metals (10% Bucket): [e.g., "Hold Gold" or "Pivot 5% to Silver"] — Why?
    Sectors/Banking: [Specific Banking sectors or energy sectors based on EIA data].
    The Frontier: [e.g., "Move from Defensive to Neutral"] — Based on latest AI breakthrough frequency.

3. The "Old Stand" Comparison
    Review my whiteboard logic. Tell me if my current "Defensive" stance on the Frontier is Valid or Outdated based on today's telemetry.

4. 12-Minute Alpha Loop (Actionable IF/THEN)
    IF [Metric X] hits [Value], THEN [Action].

**CRITICAL**: Return ONLY valid JSON matching the required schema.
"""

# ========================================
# Data Fetching
# ========================================

class UnifiedFetcherV5:
    def __init__(self):
        self.metrics = {}
        self.historical = {}
        self.ai_models = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "mistralai/mistral-small-3.1-24b-instruct:free",
            "google/gemma-2-9b-it:free",
            "microsoft/phi-3-medium-128k-instruct:free",
        ]

    def fetch_all_data(self):
        logger.info("🚀 Starting Data Fetching Phase")
        
        # 1. Market Data (yfinance)
        self.fetch_market_data()
        
        # 2. FRED Data (via free_apis)
        logger.info("🏛️ Fetching FRED Indicators")
        self.metrics['fred'] = free_apis.get_fred_indicators()
        
        # 3. EIA Data (via free_apis)
        logger.info("🛢️ Fetching EIA Energy Metrics")
        self.metrics['eia'] = free_apis.get_energy_metrics()
        
        # 4. Crypto Metrics (via free_apis)
        logger.info("🪙 Fetching Crypto Metrics")
        self.metrics['crypto'] = free_apis.get_crypto_metrics()
        
        # 5. Fear & Greed
        logger.info("😱 Fetching Fear & Greed")
        self.metrics['fng'] = free_apis.fetch_fear_greed_history(days=1)[0] if free_apis.fetch_fear_greed_history(days=1) else {}
        
        # 6. News & Arxiv
        logger.info("📰 Fetching News & Arxiv")
        self.metrics['news'] = free_apis.fetch_hackernews_top()
        
        # 7. Alpha Vantage (Specific Stocks if needed)
        # For now, we'll just ensure it's available
        
    def fetch_market_data(self):
        tickers = {
            'SPY': 'SPY', 'QQQ': 'QQQ', 'IWM': 'IWM', 'VIX': '^VIX',
            'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'GOLD': 'GC=F', 'SILVER': 'SI=F',
            'OIL': 'CL=F', 'TNX': '^TNX', 'DXY': 'DX-Y.NYB', 'TASI': '^TASI.SR'
        }
        
        def fetch_ticker(name, symbol):
            try:
                t = yf.Ticker(symbol)
                hist = t.history(period='5d')
                if not hist.empty:
                    return name, {
                        'price': float(hist['Close'].iloc[-1]),
                        'change': float((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) if len(hist) > 1 else 0
                    }
                return name, None
            except:
                return name, None

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_ticker, name, symbol) for name, symbol in tickers.items()]
            for future in as_completed(futures):
                name, data = future.result()
                if data:
                    self.metrics[name] = data

    async def run_analysis(self):
        logger.info("🤖 Starting AI Analysis Phase")
        
        if IS_LOCAL:
            logger.info("[Local Mode] Skipping AI call, using mock data.")
            return self.get_mock_result()

        data_summary = {
            "metrics": self.metrics,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        prompt = f"""
        {COMMANDER_MASTER_PROMPT}
        
        DATA SUMMARY:
        {json.dumps(data_summary, indent=2)}
        
        REQUIRED JSON SCHEMA:
        {{
            "the_commander": {{
                "morning_brief": {{
                    "daily_sentiment": "string",
                    "risk_toggle": "string",
                    "rate_path_impact": "string",
                    "portfolio_guidance": {{
                        "crypto": "string",
                        "metals": "string",
                        "sectors_banking": "string",
                        "the_frontier": "string"
                    }},
                    "old_stand_comparison": "string",
                    "alpha_loop_if_then": "string"
                }},
                "analysis": "string"
            }},
            "the_shield": {{ "analysis": "string" }},
            "the_coin": {{ "analysis": "string" }},
            "the_map": {{ "analysis": "string" }},
            "the_frontier": {{ "analysis": "string" }},
            "the_strategy": {{ "analysis": "string" }},
            "the_library": {{ "analysis": "string" }}
        }}
        """
        
        api_key = os.environ.get('OPENROUTER_API_KEY')
        if not api_key:
            logger.error("OPENROUTER_API_KEY not found!")
            return {}

        for model in self.ai_models:
            try:
                logger.info(f"  Attempting {model}...")
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are the Commander. Output strictly valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "response_format": {"type": "json_object"}
                    },
                    timeout=90
                )
                if resp.status_code == 200:
                    content = resp.json()['choices'][0]['message']['content']
                    return json.loads(content)
            except Exception as e:
                logger.warning(f"  Failed {model}: {e}")
                
        return {}

    def save_dashboards(self, ai_result: Dict):
        logger.info("💾 Saving Dashboards")
        
        dashboards = ['the-commander', 'the-shield', 'the-coin', 'the-map', 'the-frontier', 'the-strategy', 'the-library']
        
        for db in dashboards:
            db_key = db.replace('-', '_')
            data = {
                "name": db.replace('-', ' ').title(),
                "last_update": datetime.now(timezone.utc).isoformat(),
                "meta": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "version": "5.0"
                },
                "ai_analysis": ai_result.get(db_key, {}).get('analysis', 'Analysis unavailable')
            }
            
            # Special handling for Commander
            if db == 'the-commander':
                data['morning_brief'] = ai_result.get('the_commander', {}).get('morning_brief', {})
                # Add metrics for display
                data['metrics'] = [
                    {"name": "BTC", "value": f"${self.metrics.get('BTC', {}).get('price', 0):,.0f}", "signal": "NORMAL"},
                    {"name": "VIX", "value": f"{self.metrics.get('VIX', {}).get('price', 0):.2f}", "signal": "NORMAL"},
                    {"name": "Fed Rate", "value": f"{self.metrics.get('fred', {}).get('fed_funds', 0):.2f}%", "signal": "NORMAL"}
                ]

            path = DATA_DIR / db
            path.mkdir(parents=True, exist_ok=True)
            
            with open(path / 'latest.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            with open(path / 'data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"  ✅ Saved {db}")

    def get_mock_result(self):
        return {
            "the_commander": {
                "morning_brief": {
                    "daily_sentiment": "Risk-On (Mock)",
                    "risk_toggle": "Transitioning to On",
                    "rate_path_impact": "Rates falling, liquidity increasing.",
                    "portfolio_guidance": {
                        "crypto": "Increase BTC, Hold ETH",
                        "metals": "Hold Gold",
                        "sectors_banking": "Focus on Fintech",
                        "the_frontier": "Neutral"
                    },
                    "old_stand_comparison": "Defensive stance is valid but nearing pivot.",
                    "alpha_loop_if_then": "IF VIX < 15 THEN Increase Alts"
                },
                "analysis": "Mock analysis for local testing."
            }
        }

async def main():
    fetcher = UnifiedFetcherV5()
    fetcher.fetch_all_data()
    ai_result = await fetcher.run_analysis()
    if ai_result:
        fetcher.save_dashboards(ai_result)
    logger.info("🎉 Daily Alpha Loop V5 Complete")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
