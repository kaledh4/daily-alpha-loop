"""
Free API Integrations Module
============================
Integrates free APIs with rate limiting and caching to optimize free tier usage.
All APIs are rate-limited and cached to stay within free tier limits.
"""

import os
import json
import time
import logging
import pathlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import requests

logger = logging.getLogger(__name__)

# Paths
ROOT_DIR = pathlib.Path(__file__).parent.parent.parent
CACHE_DIR = ROOT_DIR / 'data' / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Rate limiting tracking
_rate_limits = defaultdict(lambda: {'count': 0, 'reset_time': 0})

# API Keys (from environment)
FRED_API_KEY = os.environ.get('FRED_API_KEY')
ALPHA_VANTAGE_KEY = os.environ.get('ALPHA_VANTAGE_KEY')

# ========================================
# FRED API (Federal Reserve Economic Data)
# ========================================
# Free tier: Unlimited for non-commercial use
# Rate limit: 120 requests/minute

def fetch_fred_series(series_id: str, days: int = 365) -> Optional[List[Dict]]:
    """Fetch FRED economic data series"""
    if not FRED_API_KEY:
        logger.warning("FRED_API_KEY not set, skipping FRED data")
        return None
    
    cache_file = CACHE_DIR / f'fred_{series_id}.json'
    
    # Check cache (refresh daily)
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text())
            cache_time = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))
            if (datetime.now(timezone.utc) - cache_time).total_seconds() < 86400:  # 24 hours
                logger.info(f"  Using cached FRED data for {series_id}")
                return cached.get('data')
        except:
            pass
    
    # Rate limiting
    if _rate_limits['fred']['count'] >= 100:  # Conservative limit
        logger.warning("FRED rate limit reached, using cache")
        return None
    
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': series_id,
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'limit': 10000,
            'sort_order': 'desc'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        observations = data.get('observations', [])
        _rate_limits['fred']['count'] += 1
        
        # Cache result
        cache_data = {
            'cached_at': datetime.now(timezone.utc).isoformat(),
            'data': observations[:days] if days else observations
        }
        cache_file.write_text(json.dumps(cache_data), encoding='utf-8')
        
        logger.info(f"  ✅ Fetched FRED {series_id}: {len(observations)} observations")
        return cache_data['data']
        
    except Exception as e:
        logger.warning(f"  Failed FRED {series_id}: {e}")
        return None

def get_fred_indicators() -> Dict:
    """Get key FRED indicators for risk monitoring"""
    indicators = {}
    
    # VIX (if not available from yfinance)
    vix_data = fetch_fred_series('VIXCLS', days=30)
    if vix_data:
        latest = next((obs for obs in vix_data if obs.get('value') != '.'), None)
        if latest:
            indicators['vix_fred'] = float(latest['value'])
    
    # 10Y Treasury Yield
    tnx_data = fetch_fred_series('DGS10', days=30)
    if tnx_data:
        latest = next((obs for obs in tnx_data if obs.get('value') != '.'), None)
        if latest:
            indicators['tnx_fred'] = float(latest['value'])
    
    # DXY (Dollar Index)
    dxy_data = fetch_fred_series('DTWEXBGS', days=30)
    if dxy_data:
        latest = next((obs for obs in dxy_data if obs.get('value') != '.'), None)
        if latest:
            indicators['dxy_fred'] = float(latest['value'])
    
    return indicators

# ========================================
# CoinGecko API
# ========================================
# Free tier: 50 calls/minute
# Rate limit: Conservative 40 calls/minute

def fetch_coingecko_data(coin_id: str = 'bitcoin') -> Optional[Dict]:
    """Fetch CoinGecko data for a cryptocurrency"""
    cache_file = CACHE_DIR / f'coingecko_{coin_id}.json'
    
    # Check cache (refresh hourly for crypto)
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text())
            cache_time = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))
            if (datetime.now(timezone.utc) - cache_time).total_seconds() < 3600:  # 1 hour
                logger.info(f"  Using cached CoinGecko data for {coin_id}")
                return cached.get('data')
        except:
            pass
    
    # Rate limiting
    if _rate_limits['coingecko']['count'] >= 40:
        logger.warning("CoinGecko rate limit reached, using cache")
        return None
    
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if coin_id in data:
            _rate_limits['coingecko']['count'] += 1
            
            result = {
                'price': data[coin_id].get('usd'),
                'market_cap': data[coin_id].get('usd_market_cap'),
                'volume_24h': data[coin_id].get('usd_24h_vol'),
                'change_24h': data[coin_id].get('usd_24h_change')
            }
            
            # Cache result
            cache_data = {
                'cached_at': datetime.now(timezone.utc).isoformat(),
                'data': result
            }
            cache_file.write_text(json.dumps(cache_data), encoding='utf-8')
            
            logger.info(f"  ✅ Fetched CoinGecko {coin_id}")
            return result
        
    except Exception as e:
        logger.warning(f"  Failed CoinGecko {coin_id}: {e}")
        return None

def get_crypto_metrics() -> Dict:
    """Get crypto metrics from CoinGecko"""
    metrics = {}
    
    # BTC
    btc_data = fetch_coingecko_data('bitcoin')
    if btc_data:
        metrics['btc'] = btc_data
    
    # ETH
    eth_data = fetch_coingecko_data('ethereum')
    if eth_data:
        metrics['eth'] = eth_data
    
    # BTC Dominance
    try:
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            metrics['btc_dominance'] = data.get('data', {}).get('market_cap_percentage', {}).get('btc', 0)
    except:
        pass
    
    return metrics

# ========================================
# Alpha Vantage API
# ========================================
# Free tier: 500 calls/day, 5 calls/minute
# Rate limit: Very conservative

def fetch_alpha_vantage(symbol: str, function: str = 'TIME_SERIES_DAILY') -> Optional[Dict]:
    """Fetch Alpha Vantage data"""
    if not ALPHA_VANTAGE_KEY:
        logger.warning("ALPHA_VANTAGE_KEY not set, skipping Alpha Vantage")
        return None
    
    cache_file = CACHE_DIR / f'av_{symbol}_{function}.json'
    
    # Check cache (refresh daily)
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text())
            cache_time = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))
            if (datetime.now(timezone.utc) - cache_time).total_seconds() < 86400:
                logger.info(f"  Using cached Alpha Vantage data for {symbol}")
                return cached.get('data')
        except:
            pass
    
    # Rate limiting (very conservative: 4 calls/minute)
    if _rate_limits['alpha_vantage']['count'] >= 4:
        wait_time = 60 - (time.time() - _rate_limits['alpha_vantage']['reset_time'])
        if wait_time > 0:
            logger.warning(f"Alpha Vantage rate limit, waiting {wait_time:.0f}s")
            time.sleep(wait_time)
            _rate_limits['alpha_vantage']['count'] = 0
            _rate_limits['alpha_vantage']['reset_time'] = time.time()
    
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_KEY,
            'outputsize': 'compact'
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if 'Error Message' in data or 'Note' in data:
            logger.warning(f"Alpha Vantage error for {symbol}: {data.get('Error Message', data.get('Note', 'Unknown'))}")
            return None
        
        _rate_limits['alpha_vantage']['count'] += 1
        if _rate_limits['alpha_vantage']['reset_time'] == 0:
            _rate_limits['alpha_vantage']['reset_time'] = time.time()
        
        # Cache result
        cache_data = {
            'cached_at': datetime.now(timezone.utc).isoformat(),
            'data': data
        }
        cache_file.write_text(json.dumps(cache_data), encoding='utf-8')
        
        logger.info(f"  ✅ Fetched Alpha Vantage {symbol}")
        return data
        
    except Exception as e:
        logger.warning(f"  Failed Alpha Vantage {symbol}: {e}")
        return None

# ========================================
# Hacker News API (Free, no key)
# ========================================

def fetch_hackernews_top() -> List[Dict]:
    """Fetch top stories from Hacker News"""
    cache_file = CACHE_DIR / 'hackernews.json'
    
    # Check cache (refresh every 30 minutes)
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text())
            cache_time = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))
            if (datetime.now(timezone.utc) - cache_time).total_seconds() < 1800:  # 30 min
                return cached.get('data', [])
        except:
            pass
    
    try:
        # Get top story IDs
        response = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json', timeout=10)
        story_ids = response.json()[:20]  # Top 20
        
        stories = []
        for story_id in story_ids[:10]:  # Limit to 10 to avoid rate limits
            story_response = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json', timeout=5)
            story = story_response.json()
            if story and story.get('type') == 'story':
                stories.append({
                    'title': story.get('title', ''),
                    'url': story.get('url', ''),
                    'score': story.get('score', 0),
                    'time': story.get('time', 0)
                })
        
        # Cache result
        cache_data = {
            'cached_at': datetime.now(timezone.utc).isoformat(),
            'data': stories
        }
        cache_file.write_text(json.dumps(cache_data), encoding='utf-8')
        
        logger.info(f"  ✅ Fetched {len(stories)} Hacker News stories")
        return stories
        
    except Exception as e:
        logger.warning(f"  Failed Hacker News: {e}")
        return []

# ========================================
# Alternative.me Crypto Fear & Greed (Free, no key)
# ========================================
# Already implemented in unified_fetcher_v2.py, but we can enhance it

def fetch_fear_greed_history(days: int = 30) -> List[Dict]:
    """Fetch historical Fear & Greed Index"""
    cache_file = CACHE_DIR / 'fear_greed_history.json'
    
    # Check cache (refresh daily)
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text())
            cache_time = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))
            if (datetime.now(timezone.utc) - cache_time).total_seconds() < 86400:
                return cached.get('data', [])
        except:
            pass
    
    try:
        response = requests.get(f'https://api.alternative.me/fng/?limit={days}', timeout=10)
        data = response.json()
        
        history = []
        for item in data.get('data', []):
            history.append({
                'value': int(item['value']),
                'classification': item['value_classification'],
                'timestamp': item['timestamp']
            })
        
        # Cache result
        cache_data = {
            'cached_at': datetime.now(timezone.utc).isoformat(),
            'data': history
        }
        cache_file.write_text(json.dumps(cache_data), encoding='utf-8')
        
        return history
        
    except Exception as e:
        logger.warning(f"  Failed Fear & Greed history: {e}")
        return []

# ========================================
# Reset rate limits (call at start of each run)
# ========================================

def reset_rate_limits():
    """Reset rate limit counters (call at start of daily run)"""
    for key in _rate_limits:
        _rate_limits[key]['count'] = 0
        _rate_limits[key]['reset_time'] = time.time()
    logger.info("✅ Rate limits reset")

