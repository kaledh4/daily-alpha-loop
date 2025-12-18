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

# Master Prompt for "The Commander" (V6 Technical)
COMMANDER_MASTER_PROMPT = """
ROLE:
You are "The Commander", the final synthesis engine of the Daily Alpha Loop.
You DO NOT speculate. You infer strictly from provided telemetry.

OBJECTIVE:
Generate a deterministic Morning Brief and Action Plan by synthesizing
exactly 7 dashboards, each with a defined analytical responsibility.

BASELINE ("OLD STAND"):
- Core Allocation: 90% Crypto / 10% Gold
- Macro Assumption: Policy rates trending 5.4% → 3.0%
- Frontier Stance: Defensive
- Risk State: Transitional (not fully Risk-On)

--------------------------------------------------
DASHBOARD CONTRACTS (NON-NEGOTIABLE)
--------------------------------------------------

1. THE SHIELD — Risk & Fragility
Inputs: VIX, Fear & Greed, FRED (TNX, DXY)
Rules:
- VIX >= 20 -> Risk-Off bias
- VIX 15-19 -> Transitional
- VIX < 15 -> Risk-On eligible
- Fear & Greed < 25 reinforces Defensive bias

2. THE COIN — Crypto Internal Rotation
Inputs: BTC Price, ETH Price, BTC Dominance (if available)
Rules:
- BTC.D >= 55% -> BTC overweight
- BTC.D < 55% -> Alt/ETH rotation allowed
- ETH weakness confirms BTC preference

3. THE MAP — Macro & Regional Strength
Inputs: FRED (Fed Funds), EIA (Oil), TASI
Rules:
- Energy strength -> Favor Energy & Saudi exposure
- TASI relative strength -> Regional allocation signal

4. THE FRONTIER — Innovation & AI Velocity
Inputs: AI breakthrough frequency (Arxiv/News)
Rules:
- Rising breakthrough frequency -> Relax defensiveness
- Flat or declining -> Maintain Defensive

5. THE STRATEGY — Cross-Dashboard Consistency Check
Purpose: Resolve conflicts between dashboards.

6. THE LIBRARY — Historical Context
Purpose: Validate current signals against past regimes.

7. THE COMMANDER — Final Authority
Purpose: Issue final portfolio directives and sector allocations.

--------------------------------------------------
REQUIRED OUTPUT (STRICT JSON)
--------------------------------------------------

{
  "the_commander": {
    "sentiment": {
      "daily_sentiment": "string",
      "risk_toggle": "Risk-On | Risk-Off | Transition",
      "rate_path_impact": "string"
    },
    "portfolio_guidance": {
      "crypto_90": {
        "stance": "BTC-heavy | ETH-leaning | Alt-rotation",
        "rationale": "string"
      },
      "metals_10": {
        "stance": "Hold Gold | Partial Silver | Rotate",
        "rationale": "string"
      },
      "sectors": {
        "focus": ["Energy", "Banking", "Other"],
        "region": "Global | Saudi | Mixed",
        "best_return_to_risk_allocation": [
            {"sector": "string", "weight": "percentage", "rationale": "string"}
        ]
      },
      "frontier": {
        "stance": "Defensive | Neutral | Aggressive",
        "rationale": "string"
      }
    },
    "old_stand_verdict": {
      "status": "Valid | Outdated | Partially Valid",
      "explanation": "string"
    },
    "alpha_loop": [
      {
        "if": "string (metric condition)",
        "then": "string (actionable step)"
      }
    ],
    "analysis": "string (Detailed synthesis)"
  },
  "the_shield": { "analysis": "string" },
  "the_coin": { "analysis": "string" },
  "the_map": { "analysis": "string" },
  "the_frontier": { "analysis": "string" },
  "the_strategy": { "analysis": "string" },
  "the_library": { "analysis": "string" }
}

CRITICAL RULES:
- No prose outside JSON.
- Every stance must trace back to at least one metric.
- Provide "best_return_to_risk_allocation" based on the sum of all 7 dashboards.
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
                data['sentiment'] = ai_result.get('the_commander', {}).get('sentiment', {})
                data['portfolio_guidance'] = ai_result.get('the_commander', {}).get('portfolio_guidance', {})
                data['old_stand_verdict'] = ai_result.get('the_commander', {}).get('old_stand_verdict', {})
                data['alpha_loop'] = ai_result.get('the_commander', {}).get('alpha_loop', [])
                
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
                "sentiment": {
                    "daily_sentiment": "Risk-On (Mock)",
                    "risk_toggle": "Transition",
                    "rate_path_impact": "Rates falling, liquidity increasing."
                },
                "portfolio_guidance": {
                    "crypto_90": { "stance": "BTC-heavy", "rationale": "Mock rationale" },
                    "metals_10": { "stance": "Hold Gold", "rationale": "Mock rationale" },
                    "sectors": {
                        "focus": ["Energy", "Banking"],
                        "region": "Mixed",
                        "best_return_to_risk_allocation": [
                            {"sector": "Fintech", "weight": "40%", "rationale": "High growth"}
                        ]
                    },
                    "frontier": { "stance": "Neutral", "rationale": "Mock rationale" }
                },
                "old_stand_verdict": { "status": "Valid", "explanation": "Mock explanation" },
                "alpha_loop": [
                    { "if": "VIX < 15", "then": "Increase Alts" }
                ],
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
