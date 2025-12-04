import os
import json
import requests
from datetime import datetime, timezone, timedelta
import logging
from typing import Optional, Dict, List, Tuple
import yfinance as yf
import feedparser
import pathlib

# --- Configuration ---
# We will write to data/crash-detector/
DATA_DIR = pathlib.Path('data/crash-detector')
DATA_FILE = DATA_DIR / 'latest.json'
HISTORY_FILE = DATA_DIR / 'history.json'

# Live URL to fetch previous history if not found locally
LIVE_HISTORY_URL = "https://kaledh4.github.io/monorepo/data/crash-detector/history.json"

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_KEY') or os.environ.get('OPENROUTER_API_KEY')

# Stress thresholds
JPY_STRESS_THRESHOLD = 150.0
JPY_CRITICAL_THRESHOLD = 155.0
CNH_STRESS_THRESHOLD = 7.25
CNH_CRITICAL_THRESHOLD = 7.4
MOVE_PROXY_HIGH = 90.0
MOVE_PROXY_CRITICAL = 120.0
AUCTION_BTC_STRESS = 2.3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_treasury_auction_data(term: str, security_type: str) -> Optional[Dict]:
    logging.info(f"Fetching {term} Treasury Auction data...")
    base_url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query"
    params = {
        "filter": f"security_term:eq:{term},security_type:eq:{security_type}",
        "sort": "-auction_date",
        "page[size]": 1
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            return data['data'][0]
        return None
    except Exception as e:
        logging.error(f"Treasury Auction fetch failed for {term}: {e}")
        return None

def fetch_market_data_yf(ticker: str) -> Optional[float]:
    logging.info(f"Fetching {ticker} via yfinance...")
    try:
        ticker_obj = yf.Ticker(ticker)
        price = None
        try:
            price = ticker_obj.fast_info.last_price
        except:
            pass
        if price is None:
            hist = ticker_obj.history(period="1d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
        if price is not None:
            logging.info(f"{ticker}: {price}")
            return float(price)
        logging.warning(f"No data found for {ticker}")
        return None
    except Exception as e:
        logging.error(f"yfinance failed for {ticker}: {e}")
        return None

def fetch_financial_news() -> List[Dict]:
    logging.info("Fetching financial news from RSS feeds...")
    rss_feeds = [
        "https://finance.yahoo.com/news/rssindex",
        "https://www.reuters.com/business/finance/rss",
        "https://www.marketwatch.com/rss/topstories",
    ]
    all_articles = []
    try:
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    all_articles.append({
                        "title": entry.get('title', 'No title'),
                        "source": feed.feed.get('title', 'Unknown'),
                        "publishedAt": entry.get('published', 'Unknown date')
                    })
            except Exception:
                continue
        return all_articles[:5]
    except Exception as e:
        logging.error(f"RSS fetch failed: {e}")
        return []

def load_historical_data() -> List[Dict]:
    # Try local first
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding='utf-8'))
        except:
            pass
    
    # Try fetch from live
    try:
        logging.info(f"Fetching history from {LIVE_HISTORY_URL}")
        r = requests.get(LIVE_HISTORY_URL, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        logging.warning(f"Could not fetch live history: {e}")
    
    return []

def save_historical_data(history: List[Dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    history = history[-30:]
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding='utf-8')

def calculate_convergence_score(current_metrics: List[Dict], history: List[Dict]) -> Dict:
    if not history or len(history) < 2:
        return {"score": 0, "status": "Insufficient History", "details": "Need more data points"}

    targets = ["10Y Treasury Yield", "USD/JPY", "USD/CNH", "MOVE Index"]
    oldest_entry = history[0]
    stress_count = 0
    details = []

    for m in current_metrics:
        if m['name'] in targets:
            try:
                curr_val = float(str(m['value']).replace('%', '').replace('x', '').replace('$', '').replace(',', ''))
                old_val = None
                for old_m in oldest_entry.get('metrics', []):
                    if old_m['name'] == m['name']:
                        old_val = float(str(old_m['value']).replace('%', '').replace('x', '').replace('$', '').replace(',', ''))
                        break
                
                if old_val:
                    change = ((curr_val - old_val) / old_val) * 100
                    if change > 2.0:
                        stress_count += 1
                        details.append(f"{m['name']} (+{change:.1f}%)")
                    elif change < -2.0:
                        details.append(f"{m['name']} ({change:.1f}%)")
                    else:
                        details.append(f"{m['name']} (Flat)")
            except:
                continue

    score = (stress_count / 4) * 100
    status = "Low Convergence"
    if score >= 75: status = "CRITICAL CONVERGENCE"
    elif score >= 50: status = "Moderate Convergence"
    elif score >= 25: status = "Early Signs"
    
    return {
        "score": round(score, 1), 
        "status": status, 
        "details": ", ".join(details)
    }

def determine_signal(metric_name: str, value: float) -> str:
    if value is None: return "DATA ERROR"
    if metric_name == "USD/JPY":
        if value >= JPY_CRITICAL_THRESHOLD: return "CRITICAL SHOCK"
        if value >= JPY_STRESS_THRESHOLD: return "HIGH STRESS"
        if value > 145.0: return "RISING STRESS"
    elif metric_name == "USD/CNH":
        if value >= CNH_CRITICAL_THRESHOLD: return "CRITICAL SHOCK"
        if value >= CNH_STRESS_THRESHOLD: return "HIGH STRESS"
        if value > 7.15: return "RISING STRESS"
    elif metric_name == "10Y Treasury Yield":
        if value >= 5.0: return "CRITICAL SHOCK"
        if value >= 4.5: return "HIGH STRESS"
        if value >= 4.2: return "RISING STRESS"
    elif metric_name == "MOVE Index":
        if value >= MOVE_PROXY_CRITICAL: return "CRITICAL SHOCK"
        if value >= MOVE_PROXY_HIGH: return "HIGH STRESS"
        if value > 80.0: return "RISING STRESS"
    elif metric_name == "10Y Auction Bid-to-Cover":
        if value < 2.0: return "CRITICAL SHOCK"
        if value < AUCTION_BTC_STRESS: return "HIGH STRESS"
        if value < 2.4: return "RISING STRESS"
    elif metric_name == "China Credit Proxy (CBON)":
        if value < 20.0: return "HIGH STRESS"
    return "NORMAL"

def calculate_composite_risk(metrics: List[Dict]) -> Dict:
    score = 0
    count = 0
    weights = {"CRITICAL SHOCK": 100, "HIGH STRESS": 75, "RISING STRESS": 40, "NORMAL": 0}
    for m in metrics:
        if m['signal'] in weights:
            score += weights[m['signal']]
            count += 1
    if count == 0: return {"score": 0, "level": "UNKNOWN", "color": "#6c757d"}
    avg = score / count
    if avg >= 60: return {"score": round(avg, 1), "level": "CRITICAL", "color": "#dc3545"}
    if avg >= 35: return {"score": round(avg, 1), "level": "ELEVATED", "color": "#ffc107"}
    return {"score": round(avg, 1), "level": "LOW", "color": "#28a745"}

def generate_ai_insights(metrics: List[Dict], convergence: Dict) -> Dict:
    if not OPENROUTER_API_KEY:
        return {"crash_analysis": "AI Key Missing", "news_summary": "AI Key Missing"}
        
    news = fetch_financial_news()
    news_text = "\n".join([f"- {n['title']}" for n in news])
    metrics_str = json.dumps(metrics, indent=2)
    convergence_str = json.dumps(convergence, indent=2)
    
    prompt = f"""
    Analyze these market metrics for a "Global Financial Fault Lines" convergence event.
    METRICS: {metrics_str}
    CONVERGENCE: {convergence_str}
    NEWS: {news_text}
    Return JSON: {{ "crash_analysis": "HTML string", "news_summary": "HTML string" }}
    """
    
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "tngtech/tng-r1t-chimera:free",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )
        content = resp.json()['choices'][0]['message']['content']
        start = content.find('{')
        end = content.rfind('}') + 1
        return json.loads(content[start:end])
    except Exception as e:
        logging.error(f"AI Error: {e}")
        return {"crash_analysis": "AI Analysis Failed", "news_summary": "Check Logs"}

def run_crash_detector():
    logging.info("Starting Crash Detector Fetch...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    usd_jpy = fetch_market_data_yf("JPY=X")
    usd_cnh = fetch_market_data_yf("CNH=X")
    yield_10y = fetch_market_data_yf("^TNX")
    move_index = fetch_market_data_yf("^MOVE")
    if not move_index:
        move_index = fetch_market_data_yf("^VIX")
        move_name = "VIX (Volatility Proxy)"
    else:
        move_name = "MOVE Index"
    cbon_etf = fetch_market_data_yf("CBON")
    
    auction_10y = fetch_treasury_auction_data("10-Year", "Note")
    auction_30y = fetch_treasury_auction_data("30-Year", "Bond")
    btc_10y = float(auction_10y['bid_to_cover_ratio']) if auction_10y else None
    
    tail_30y = None
    if auction_30y and 'high_yield' in auction_30y and 'average_median_yield' in auction_30y:
        try:
            tail_30y = (float(auction_30y['high_yield']) - float(auction_30y['average_median_yield'])) * 100
        except: pass

    metrics = [
        {"name": "10Y Treasury Auction Bid-to-Cover", "value": f"{btc_10y:.2f}x" if btc_10y else "N/A", "signal": determine_signal("10Y Auction Bid-to-Cover", btc_10y), "desc": "Demand strength"},
        {"name": "30Y Auction Tail", "value": f"{tail_30y:.1f} bps" if tail_30y is not None else "N/A", "signal": "NORMAL" if (tail_30y is None or tail_30y < 3.0) else "HIGH STRESS", "desc": "Dealer reluctance"},
        {"name": "USD/JPY", "value": f"{usd_jpy:.2f}" if usd_jpy else "N/A", "signal": determine_signal("USD/JPY", usd_jpy), "desc": "Carry-trade stress"},
        {"name": "USD/CNH", "value": f"{usd_cnh:.4f}" if usd_cnh else "N/A", "signal": determine_signal("USD/CNH", usd_cnh), "desc": "Yuan stability"},
        {"name": "China Credit Proxy (CBON)", "value": f"${cbon_etf:.2f}" if cbon_etf else "N/A", "signal": determine_signal("China Credit Proxy (CBON)", cbon_etf), "desc": "LGFV/Credit Stress"},
        {"name": "10Y Treasury Yield", "value": f"{yield_10y:.2f}%" if yield_10y else "N/A", "signal": determine_signal("10Y Treasury Yield", yield_10y), "desc": "Systemic risk trigger"},
        {"name": move_name, "value": f"{move_index:.2f}" if move_index else "N/A", "signal": determine_signal("MOVE Index", move_index), "desc": "Treasury volatility"}
    ]
    
    history = load_historical_data()
    convergence = calculate_convergence_score(metrics, history)
    risk = calculate_composite_risk(metrics)
    ai_insights = generate_ai_insights(metrics, convergence)
    
    final_data = {
        "last_update": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "risk_assessment": risk,
        "convergence_score": convergence,
        "metrics": metrics,
        "ai_insights": ai_insights,
        "days_remaining": (datetime(2026, 11, 28) - datetime.now()).days
    }
    
    DATA_FILE.write_text(json.dumps(final_data, indent=4), encoding='utf-8')
    history.append(final_data)
    save_historical_data(history)
    logging.info("Crash Detector Data Saved")

if __name__ == "__main__":
    run_crash_detector()
