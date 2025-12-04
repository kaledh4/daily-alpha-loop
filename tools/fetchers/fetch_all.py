import os
import requests
import json
import datetime
import pathlib
import time

def write_snapshot(namespace, payload):
    outdir = pathlib.Path('data') / namespace
    outdir.mkdir(parents=True, exist_ok=True)
    iso = datetime.datetime.utcnow().isoformat(timespec='seconds').replace(':','-') + 'Z'
    (outdir / f"{iso}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    (outdir / "latest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')

def fetch_news():
    key = os.getenv('NEWS_API_KEY')
    if not key:
        print("NEWS_API_KEY not found, skipping news fetch")
        return None
    q = 'AI mathematician OR automated proof OR "LLM-generated"'
    url = f"https://newsapi.org/v2/everything?q={q}&pageSize=50"
    try:
        r = requests.get(url, headers={'X-Api-Key': key}, timeout=30)
        r.raise_for_status()
        raw = r.json()
        payload = {
            "meta": {"source":"newsapi", "fetched_at": datetime.datetime.utcnow().isoformat()+"Z"},
            "numbers": {"items_fetched": raw.get('totalResults', len(raw.get('articles', [])))},
            "top_items": [{"id":a.get('url'), "title":a.get('title'), "summary": a.get('description'), "url": a.get('url'), "published_at": a.get('publishedAt')} for a in raw.get('articles',[])[:10]],
            "raw": {"count": len(raw.get('articles',[]))}
        }
        write_snapshot('news', payload)
        print("News snapshot saved")
        return payload
    except Exception as e:
        print(f"Error fetching news: {e}")
        return None

def fetch_crypto():
    # Placeholder for CryptoCompare or CoinGecko
    # For now, we'll just create a dummy snapshot to test the flow
    payload = {
        "meta": {"source":"dummy-crypto", "fetched_at": datetime.datetime.utcnow().isoformat()+"Z"},
        "numbers": {"btc_price": 95000, "eth_price": 3500},
        "top_items": [],
        "raw": {}
    }
    write_snapshot('crypto', payload)
    print("Crypto snapshot saved (dummy)")
    return payload

if __name__ == '__main__':
    print("Starting data fetch...")
    fetch_news()
    fetch_crypto()
    print("Data fetch complete.")
