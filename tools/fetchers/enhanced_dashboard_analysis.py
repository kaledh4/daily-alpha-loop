"""
Enhanced Dashboard Analysis
===========================
Adds enhanced metrics, percentiles, trends, color coding, and cross-dashboard
convergence logic to all dashboard analyses.
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

# Import enhanced analytics
from .enhanced_analytics import (
    enhance_metric, save_dashboard_score, calculate_regime,
    get_dashboard_score_history
)

logger = logging.getLogger(__name__)

def enhance_shield_metrics(metrics: List[Dict], dashboard_name: str = 'the-shield') -> List[Dict]:
    """Enhance Shield metrics with percentiles, trends, and color coding"""
    enhanced = []
    
    # Thresholds for risk metrics (reverse=True means higher is worse)
    thresholds_map = {
        'VIX': {'red': 30, 'yellow': 20, 'green': 15, 'reverse': True},
        'MOVE': {'red': 120, 'yellow': 90, 'green': 80, 'reverse': True},
        'USD/JPY': {'red': 155, 'yellow': 150, 'green': 145, 'reverse': True},
        'USD/CNH': {'red': 7.4, 'yellow': 7.25, 'green': 7.15, 'reverse': True},
        '10Y Treasury Yield': {'red': 5.0, 'yellow': 4.5, 'green': 4.2, 'reverse': True},
        '10Y Treasury Bid-to-Cover': {'red': 2.0, 'yellow': 2.3, 'green': 2.5, 'reverse': True}
    }
    
    for metric in metrics:
        metric_name = metric.get('name', '')
        metric_key = metric_name.lower().replace(' ', '_').replace('/', '_')
        
        # Extract numeric value
        value_str = str(metric.get('value', '0')).replace('x', '').replace('%', '').replace('$', '')
        try:
            value = float(value_str)
        except:
            value = 0
        
        # Get thresholds
        thresholds = None
        reverse = False
        for key, config in thresholds_map.items():
            if key in metric_name:
                thresholds = {k: v for k, v in config.items() if k != 'reverse'}
                reverse = config.get('reverse', False)
                break
        
        # Enhance metric
        enhanced_metric = enhance_metric(
            metric, 
            dashboard_name, 
            metric_key,
            thresholds=thresholds,
            reverse=reverse
        )
        enhanced.append(enhanced_metric)
    
    return enhanced

def enhance_coin_metrics(data: Dict, dashboard_name: str = 'the-coin') -> Dict:
    """Enhance Coin metrics with momentum score and context"""
    enhanced = data.copy()
    
    # Calculate momentum score (0-100)
    rsi = data.get('rsi', 50)
    fng_value = data.get('fear_and_greed', {}).get('value', 50)
    trend = data.get('trend', 'Neutral')
    
    momentum_score = 50  # Base
    if trend == 'Bullish':
        momentum_score += 20
    elif trend == 'Bearish':
        momentum_score -= 20
    
    if rsi:
        if rsi > 70:
            momentum_score += 15  # Overbought but strong
        elif rsi > 60:
            momentum_score += 10
        elif rsi < 30:
            momentum_score -= 15  # Oversold
        elif rsi < 40:
            momentum_score -= 10
    
    if fng_value:
        momentum_score += (fng_value - 50) * 0.3  # Scale F&G to momentum
    
    momentum_score = max(0, min(100, momentum_score))
    
    # Add momentum score to scoring
    if 'scoring' not in enhanced:
        enhanced['scoring'] = {}
    enhanced['scoring']['momentum_score'] = round(momentum_score, 1)
    
    # Add RSI context
    if rsi:
        if rsi < 30:
            enhanced['rsi_context'] = {'zone': 'oversold', 'color': '#dc3545', 'label': 'OVERSOLD'}
        elif rsi > 70:
            enhanced['rsi_context'] = {'zone': 'overbought', 'color': '#ffc107', 'label': 'OVERBOUGHT'}
        else:
            enhanced['rsi_context'] = {'zone': 'neutral', 'color': '#28a745', 'label': 'NEUTRAL'}
    
    return enhanced

def enhance_map_metrics(data: Dict, dashboard_name: str = 'the-map') -> Dict:
    """Enhance Map metrics with regional heatmap context"""
    enhanced = data.copy()
    
    macro = data.get('macro', {})
    
    # Calculate regional macro scores
    regional_scores = {
        'US': 5,
        'EU': 5,
        'China': 5,
        'MENA': 5
    }
    
    # US score based on SP500, DXY, Treasury
    sp500 = macro.get('sp500', 0)
    dxy = macro.get('dxy', 0)
    treasury_10y = macro.get('treasury_10y', 0)
    
    if sp500 > 5000:
        regional_scores['US'] += 2
    if dxy > 105:
        regional_scores['US'] += 1
    if treasury_10y < 4.0:
        regional_scores['US'] += 1
    
    # MENA score based on TASI and Oil
    tasi = macro.get('tasi', 0)
    oil = macro.get('oil', 0)
    
    if tasi > 10000:
        regional_scores['MENA'] += 2
    if oil > 80:
        regional_scores['MENA'] += 1
    
    enhanced['regional_scores'] = regional_scores
    
    return enhanced

def build_conflict_matrix(dashboards_data: Dict) -> Dict:
    """
    Build conflict matrix showing convergence/divergence between dashboards
    """
    matrix = {
        'risk': {'signal': 'UNKNOWN', 'score': 0, 'color': '#718096'},
        'crypto': {'signal': 'UNKNOWN', 'score': 0, 'color': '#718096'},
        'macro': {'signal': 'UNKNOWN', 'score': 0, 'color': '#718096'},
        'tech': {'signal': 'UNKNOWN', 'score': 0, 'color': '#718096'},
        'net_signal': {'signal': 'WAIT', 'confidence': 0, 'color': '#718096'}
    }
    
    # Extract signals from each dashboard
    shield = dashboards_data.get('the-shield', {})
    coin = dashboards_data.get('the-coin', {})
    map_data = dashboards_data.get('the-map', {})
    frontier = dashboards_data.get('the-frontier', {})
    
    # Risk signal
    risk_level = shield.get('risk_assessment', {}).get('level', 'UNKNOWN')
    risk_score = shield.get('scoring', {}).get('risk_level', 0)
    if risk_level == 'CRITICAL' or risk_score >= 60:
        matrix['risk'] = {'signal': 'DEFENSIVE', 'score': risk_score, 'color': '#dc3545'}
    elif risk_level == 'ELEVATED' or risk_score >= 35:
        matrix['risk'] = {'signal': 'CAUTIOUS', 'score': risk_score, 'color': '#ffc107'}
    else:
        matrix['risk'] = {'signal': 'CALM', 'score': risk_score, 'color': '#28a745'}
    
    # Crypto signal
    momentum = coin.get('momentum', 'Neutral')
    momentum_score = coin.get('scoring', {}).get('momentum_score', 50)
    if momentum == 'Bullish' or momentum_score >= 70:
        matrix['crypto'] = {'signal': 'BULLISH', 'score': momentum_score, 'color': '#28a745'}
    elif momentum == 'Bearish' or momentum_score <= 30:
        matrix['crypto'] = {'signal': 'BEARISH', 'score': momentum_score, 'color': '#dc3545'}
    else:
        matrix['crypto'] = {'signal': 'NEUTRAL', 'score': momentum_score, 'color': '#ffc107'}
    
    # Macro signal
    tasi_mood = map_data.get('tasi_mood', 'Neutral')
    stance_strength = map_data.get('scoring', {}).get('stance_strength', 5)
    if tasi_mood == 'Positive' or stance_strength >= 7:
        matrix['macro'] = {'signal': 'POSITIVE', 'score': stance_strength * 10, 'color': '#28a745'}
    elif tasi_mood == 'Negative' or stance_strength <= 3:
        matrix['macro'] = {'signal': 'NEGATIVE', 'score': stance_strength * 10, 'color': '#dc3545'}
    else:
        matrix['macro'] = {'signal': 'NEUTRAL', 'score': stance_strength * 10, 'color': '#ffc107'}
    
    # Tech signal
    breakthrough_score = frontier.get('scoring', {}).get('breakthrough_score', 5)
    if breakthrough_score >= 8:
        matrix['tech'] = {'signal': 'BULLISH', 'score': breakthrough_score * 10, 'color': '#28a745'}
    elif breakthrough_score <= 3:
        matrix['tech'] = {'signal': 'BEARISH', 'score': breakthrough_score * 10, 'color': '#dc3545'}
    else:
        matrix['tech'] = {'signal': 'NEUTRAL', 'score': breakthrough_score * 10, 'color': '#ffc107'}
    
    # Calculate net signal
    signals = [matrix['risk']['signal'], matrix['crypto']['signal'], 
               matrix['macro']['signal'], matrix['tech']['signal']]
    
    defensive_count = sum(1 for s in signals if 'DEFENSIVE' in s or 'BEARISH' in s or 'NEGATIVE' in s)
    bullish_count = sum(1 for s in signals if 'BULLISH' in s or 'POSITIVE' in s)
    
    if defensive_count >= 3:
        matrix['net_signal'] = {'signal': 'DEFENSIVE', 'confidence': 0.8, 'color': '#dc3545'}
    elif bullish_count >= 3:
        matrix['net_signal'] = {'signal': 'BULLISH', 'confidence': 0.8, 'color': '#28a745'}
    elif defensive_count == 2 and bullish_count == 0:
        matrix['net_signal'] = {'signal': 'CAUTIOUS', 'confidence': 0.6, 'color': '#ffc107'}
    else:
        matrix['net_signal'] = {'signal': 'WAIT', 'confidence': 0.5, 'color': '#718096'}
    
    return matrix

def calculate_weighted_top_signal(dashboards_data: Dict) -> Dict:
    """
    Calculate weighted top signal using the scoring system:
    Risk Score × 0.3 + Crypto Score × 0.2 + Macro Score × 0.25 + Tech Score × 0.15 + Strategy Score × 0.1
    """
    shield = dashboards_data.get('the-shield', {})
    coin = dashboards_data.get('the-coin', {})
    map_data = dashboards_data.get('the-map', {})
    frontier = dashboards_data.get('the-frontier', {})
    strategy = dashboards_data.get('the-strategy', {})
    
    # Extract scores (normalize to 0-100)
    risk_score = shield.get('scoring', {}).get('risk_level', 0)  # Already 0-100
    crypto_score = coin.get('scoring', {}).get('momentum_score', 50)  # 0-100
    macro_score = map_data.get('scoring', {}).get('stance_strength', 5) * 10  # 0-100
    tech_score = frontier.get('scoring', {}).get('breakthrough_score', 5) * 10  # 0-100
    strategy_score = strategy.get('scoring', {}).get('stance_confidence', 5) * 10  # 0-100
    
    # Weighted calculation
    weighted_score = (
        risk_score * 0.3 +
        crypto_score * 0.2 +
        macro_score * 0.25 +
        tech_score * 0.15 +
        strategy_score * 0.1
    )
    
    # Determine top signal based on highest weighted component
    components = [
        ('Risk', risk_score, 0.3),
        ('Crypto', crypto_score, 0.2),
        ('Macro', macro_score, 0.25),
        ('Tech', tech_score, 0.15),
        ('Strategy', strategy_score, 0.1)
    ]
    
    # Find component with highest weighted contribution
    weighted_contributions = [(name, score * weight) for name, score, weight in components]
    top_component = max(weighted_contributions, key=lambda x: x[1])
    
    # Build signal description
    if top_component[0] == 'Risk':
        risk_level = shield.get('risk_assessment', {}).get('level', 'UNKNOWN')
        vix = shield.get('metrics', [])
        vix_metric = next((m for m in vix if 'VIX' in m.get('name', '')), None)
        if vix_metric:
            signal = f"VIX at {vix_metric.get('value')} ({risk_level} risk environment)"
        else:
            signal = f"Risk Level: {risk_level} ({risk_score}/100)"
    elif top_component[0] == 'Crypto':
        btc_price = coin.get('btc_price', 0)
        momentum = coin.get('momentum', 'Neutral')
        signal = f"BTC ${btc_price:,.0f} - {momentum} momentum"
    elif top_component[0] == 'Macro':
        tasi_mood = map_data.get('tasi_mood', 'Neutral')
        signal = f"Macro: {tasi_mood} (TASI mood)"
    elif top_component[0] == 'Tech':
        breakthroughs = frontier.get('breakthroughs', [])
        signal = f"Tech: {len(breakthroughs)} breakthroughs identified"
    else:
        stance = strategy.get('stance', 'Neutral')
        signal = f"Strategy: {stance} stance"
    
    return {
        'signal': signal,
        'weighted_score': round(weighted_score, 1),
        'top_component': top_component[0],
        'confidence': min(0.95, weighted_score / 100)
    }

def build_decision_tree(dashboards_data: Dict) -> Dict:
    """
    Build decision tree visualization for The Commander
    """
    shield = dashboards_data.get('the-shield', {})
    coin = dashboards_data.get('the-coin', {})
    map_data = dashboards_data.get('the-map', {})
    
    risk_score = shield.get('scoring', {}).get('risk_level', 0)
    crypto_score = coin.get('scoring', {}).get('momentum_score', 50)
    macro_score = map_data.get('scoring', {}).get('stance_strength', 5)
    
    # Decision tree logic
    decisions = []
    
    if risk_score > 15 and crypto_score < 60 and macro_score < 6:
        decisions.append({
            'condition': 'Risk > 15 AND Crypto < 60 AND Macro < 6',
            'action': 'Go Defensive',
            'confidence': 0.9,
            'reasoning': 'High risk with weak crypto and macro signals suggests defensive positioning'
        })
    elif risk_score < 10 and crypto_score > 70 and macro_score > 7:
        decisions.append({
            'condition': 'Risk < 10 AND Crypto > 70 AND Macro > 7',
            'action': 'Rotate to Growth',
            'confidence': 0.7,
            'reasoning': 'Low risk with strong crypto and macro momentum suggests growth opportunity'
        })
    elif risk_score > 20:
        decisions.append({
            'condition': 'Risk > 20',
            'action': 'Reduce Equity Exposure',
            'confidence': 0.85,
            'reasoning': 'Elevated risk levels suggest reducing equity exposure by 20-30%'
        })
    elif crypto_score < 30:
        decisions.append({
            'condition': 'Crypto < 30 (Oversold)',
            'action': 'Watch Support Levels',
            'confidence': 0.75,
            'reasoning': 'Crypto oversold - monitor key support levels for potential bounce'
        })
    else:
        decisions.append({
            'condition': 'Mixed Signals',
            'action': 'Wait for Clarity',
            'confidence': 0.6,
            'reasoning': 'Mixed signals across dashboards - wait for clearer directional bias'
        })
    
    return {
        'primary_decision': decisions[0] if decisions else None,
        'all_decisions': decisions
    }

