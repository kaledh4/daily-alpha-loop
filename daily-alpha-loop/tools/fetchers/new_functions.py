# New fetch functions to add to unified_fetcher_v3.py
# These add enhanced features for The Coin, The Shield, The Map, and The Frontier

def fetch_crypto_risk_metrics():
    """Calculate risk metrics and multipliers for crypto assets"""
    logger.info("=" * 50)
    logger.info("⚡ CALCULATING CRYPTO RISK METRICS")
    logger.info("=" * 50)
    
    if not PANDAS_AVAILABLE or not YFINANCE_AVAILABLE:
        return
    
    # Define crypto assets with baseline risk parameters
    crypto_assets = {
        'BTC': {'base_risk': 1.0, 'base_mult': 1.0},
        'ETH': {'base_risk': 0.4, 'base_mult': 2.0},
        'ETHBTC': {'base_risk': 0.1, 'base_mult': 2.0},
        'VXV': {'base_risk': 0.02, 'base_mult': 45.0},
        'APT': {'base_risk': 0.02, 'base_mult': 28.0},
        'ADA': {'base_risk': 0.025, 'base_mult': 12.0},
        'NEAR': {'base_risk': 0.022, 'base_mult': 19.0}
    }
    
    for asset, params in crypto_assets.items():
        try:
            price = store.get(f'market.{asset}')
            if price:
                # Calculate volatility-based risk adjustment
                if asset != 'ETHBTC':
                    ticker = yf.Ticker(f'{asset}-USD')
                    hist = ticker.history(period='30d')
                    if not hist.empty:
                        volatility = hist['Close'].pct_change().std()
                        risk_score = params['base_risk'] * (1 + volatility * 10)
                    else:
                        risk_score = params['base_risk']
                else:
                    # ETH/BTC ratio
                    btc = store.get('market.BTC')
                    eth = store.get('market.ETH')
                    if btc and eth:
                        ratio = eth / btc
                        store.set(f'market.{asset}', ratio)
                        risk_score = params['base_risk']
                
                store.set(f'crypto.{asset}.risk', round(risk_score, 3))
                store.set(f'crypto.{asset}.multiplier', params['base_mult'])
                logger.info(f"  {asset}: Risk={risk_score:.3f}, Mult={params['base_mult']}x")
        
        except Exception as e:
            logger.warning(f"  Failed risk calc for {asset}: {e}")
    
    # Calculate composite risk
    btc_risk = store.get(f'crypto.BTC.risk') or 1.0
    eth_risk = store.get(f'crypto.ETH.risk') or 0.4
    composite = (btc_risk + eth_risk) / 2
    store.set('crypto.composite_risk', round(composite, 2))
    
    # Determine risk level
    if composite > 0.8:
        risk_level = "High"
    elif composite > 0.4:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    store.set('crypto.risk_level', risk_level)
    logger.info(f"  Composite Risk: {composite:.2f} ({risk_level})")

def fetch_fed_rate():
    """Fetch current Federal Funds Rate"""
    logger.info("=" * 50)
    logger.info("🏦 FETCHING FED FUNDS RATE")
    logger.info("=" * 50)
    
    if not REQUESTS_AVAILABLE:
        return
    
    fred_key = API_KEYS.get('FRED')
    if not fred_key:
        logger.warning("  FRED API key not found, using fallback")
        store.set('rates.FED_FUNDS', 5.33)
        return
    
    try:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': 'FEDFUNDS',
            'api_key': fred_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'observations' in data and len(data['observations']) > 0:
            rate = float(data['observations'][0]['value'])
            store.set('rates.FED_FUNDS', rate)
            logger.info(f"  Fed Funds Rate: {rate:.2f}%")
        else:
            store.set('rates.FED_FUNDS', 5.33)
    
    except Exception as e:
        logger.warning(f"  Failed to fetch Fed rate: {e}")
        store.set('rates.FED_FUNDS', 5.33)

def fetch_price_changes():
    """Fetch historical price changes for macro assets"""
    logger.info("=" * 50)
    logger.info("📊 CALCULATING PRICE CHANGES")
    logger.info("=" * 50)
    
    if not YFINANCE_AVAILABLE or not PANDAS_AVAILABLE:
        return
    
    assets = {
        'TNX': '^TNX',      # 10Y Yield
        'GOLD': 'GC=F',     # Gold
        'SP500': '^GSPC',   # S&P 500
        'TASI': '^TASI.SR', # Saudi TASI
        'OIL': 'CL=F'       # Oil
    }
    
    for name, ticker in assets.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period='5d')
            
            if len(hist) >= 2:
                current = float(hist['Close'].iloc[-1])
                previous = float(hist['Close'].iloc[-2])
                pct_change = ((current - previous) / previous) * 100
                
                store.set(f'market.{name}_change_pct', round(pct_change, 2))
                logger.info(f"  {name}: {pct_change:+.2f}%")
            
        except Exception as e:
            logger.warning(f"  Failed price change for {name}: {e}")

def calculate_crash_risk_score():
    """Calculate comprehensive crash risk score for The Shield"""
    logger.info("=" * 50)
    logger.info("🛡️ CALCULATING CRASH RISK SCORE")
    logger.info("=" * 50)
    
    stress_scores = []
    stress_indicators = []
    
    # 1. Treasury Bid-to-Cover
    btc = store.get('treasury.10y_bid_to_cover')
    if btc:
        if btc < 2.0:
            score = 100
            signal = "CRITICAL SHOCK"
        elif btc < 2.3:
            score = 60
            signal = "HIGH STRESS"
        else:
            score = 0
            signal = "NORMAL"
        stress_scores.append(score)
        stress_indicators.append({
            'name': '10Y Treasury Auction Bid-to-Cover',
            'value': f'{btc:.2f}x',
            'status': signal,
            'note': 'Demand strength (Stress < 2.3x)'
        })
    
    # 2. USD/JPY
    jpy = store.get('market.JPY')
    if jpy:
        if jpy >= 155:
            score = 100
            signal = "HIGH STRESS"
        elif jpy >= 150:
            score = 50
            signal = "ELEVATED"
        else:
            score = 0
            signal = "NORMAL"
        stress_scores.append(score)
        stress_indicators.append({
            'name': 'USD/JPY',
            'value': f'{jpy:.2f}',
            'status': signal,
            'note': 'Carry-trade stress'
        })
    
    # 3. USD/CNH
    cnh = store.get('market.CNH')
    if cnh:
        if cnh >= 7.4:
            score = 100
        elif cnh >= 7.25:
            score = 60
        elif cnh > 7.15:
            score = 30
        else:
            score = 0
        signal = "NORMAL" if score == 0 else "STRESS"
        stress_scores.append(score)
        stress_indicators.append({
            'name': 'USD/CNH',
            'value': f'{cnh:.4f}',
            'status': signal,
            'note': 'Yuan stability'
        })
    
    # 4. 10Y Treasury Yield
    tnx = store.get('market.TNX')
    if tnx:
        if tnx >= 5.0:
            score = 80
        elif tnx >= 4.5:
            score = 40
        elif tnx >= 4.2:
            score = 20
        else:
            score = 0
        signal = "NORMAL" if score == 0 else "ELEVATED"
        stress_scores.append(score)
        stress_indicators.append({
            'name': '10Y Treasury Yield',
            'value': f'{tnx:.2f}%',
            'status': signal,
            'note': 'Systemic risk trigger'
        })
    
    # 5. MOVE Index
    move = store.get('market.MOVE')
    if move:
        if move >= 90:
            score = 80
            signal = "HIGH STRESS"
        elif move >= 80:
            score = 40
            signal = "ELEVATED"
        else:
            score = 0
            signal = "NORMAL"
        stress_scores.append(score)
        stress_indicators.append({
            'name': 'MOVE Index',
            'value': f'{move:.2f}',
            'status': signal,
            'note': 'Treasury volatility (Stress > 90)'
        })
    
    # Calculate composite
    if stress_scores:
        composite_score = sum(stress_scores) / len(stress_scores)
    else:
        composite_score = 0
    
    # Determine risk level
    if composite_score >= 60:
        risk_level = "CRITICAL"
    elif composite_score >= 30:
        risk_level = "ELEVATED"
    else:
        risk_level = "LOW"
    
    store.set('shield.crash_risk_score', round(composite_score, 1))
    store.set('shield.crash_risk_level', risk_level)
    store.set('shield.stress_indicators', stress_indicators)
    
    logger.info(f"  Crash Risk Score: {composite_score:.1f}/100 ({risk_level})")

def calculate_frontier_timeline():
    """Calculate timeline milestones for The Frontier"""
    logger.info("=" * 50)
    logger.info("🚀 CALCULATING FRONTIER TIMELINE")
    logger.info("=" * 50)
    
    # Reference date: Assuming project start was on 2025-11-24 (Day 1)
    from datetime import timedelta
    
    reference_date = datetime(2025, 11, 24, tzinfo=timezone.utc)
    current_date = datetime.now(timezone.utc)
    
    # Calculate current day
    days_elapsed = (current_date - reference_date).days + 1
    
    milestones = {
        'Resource ID': {
            'days_from_start': 78,
            'days_remaining': max(0, 78 - days_elapsed),
            'target_date': (reference_date + timedelta(days=78)).strftime('%Y-%m-%d')
        },
        'Data Assets': {
            'days_from_start': 108,
            'days_remaining': max(0, 108 - days_elapsed),
            'target_date': (reference_date + timedelta(days=108)).strftime('%Y-%m-%d')
        },
        'Robotics Integration': {
            'days_from_start': 228,
            'days_remaining': max(0, 228 - days_elapsed),
            'target_date': (reference_date + timedelta(days=228)).strftime('%Y-%m-%d')
        },
        'Operating Capability': {
            'days_from_start': 258,
            'days_remaining': max(0, 258 - days_elapsed),
            'target_date': (reference_date + timedelta(days=258)).strftime('%Y-%m-%d')
        }
    }
    
    store.set('frontier.current_day', days_elapsed)
    store.set('frontier.milestones', milestones)
    store.set('frontier.days_remaining', max(0, 258 - days_elapsed))
    
    logger.info(f"  Current Day: {days_elapsed}")
    for name, data in milestones.items():
        logger.info(f"  {name}: {data['days_remaining']} days remaining")
