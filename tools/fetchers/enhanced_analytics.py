"""
Enhanced Analytics Module
==========================
Adds percentile calculations, historical tracking, trend indicators,
and enhanced context to all dashboard metrics.
"""

import json
import sqlite3
import pathlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Paths
ROOT_DIR = pathlib.Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / 'data'
HISTORY_DB = DATA_DIR / 'history.db'

# Initialize history database
def init_history_db():
    """Initialize SQLite database for historical tracking"""
    HISTORY_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(HISTORY_DB))
    cursor = conn.cursor()
    
    # Create metrics history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            dashboard TEXT NOT NULL,
            metric_key TEXT NOT NULL,
            value REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, dashboard, metric_key)
        )
    ''')
    
    # Create dashboard scores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dashboard_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            dashboard TEXT NOT NULL,
            score REAL NOT NULL,
            metadata TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, dashboard)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ History database initialized")

# Initialize on import
init_history_db()

def get_percentile(value: float, historical_values: List[float]) -> float:
    """Calculate percentile rank of value in historical data"""
    if not historical_values or len(historical_values) < 2:
        return 50.0  # Default to median if no history
    
    sorted_vals = sorted(historical_values)
    count_below = sum(1 for v in sorted_vals if v < value)
    percentile = (count_below / len(sorted_vals)) * 100
    return round(percentile, 1)

def get_trend(current: float, previous: Optional[float], previous_week: Optional[float]) -> Dict:
    """Calculate trend indicators (↑↓→)"""
    if previous is None:
        return {'direction': '→', 'change_1d': 0, 'change_1w': 0, 'label': 'No data'}
    
    change_1d = current - previous
    change_1w = current - previous_week if previous_week else 0
    
    # Determine direction
    if abs(change_1d) < 0.01:  # Essentially no change
        direction = '→'
    elif change_1d > 0:
        direction = '↑'
    else:
        direction = '↓'
    
    return {
        'direction': direction,
        'change_1d': round(change_1d, 2),
        'change_1w': round(change_1w, 2),
        'label': f'{direction} {abs(change_1d):.2f} (1D)'
    }

def get_color_zone(value: float, thresholds: Dict[str, float], reverse: bool = False) -> Dict:
    """
    Get color zone (red/yellow/green) based on thresholds
    thresholds: {'red': max_red, 'yellow': max_yellow, 'green': max_green}
    reverse: if True, lower is better (e.g., for risk metrics)
    """
    if reverse:
        if value >= thresholds.get('red', 80):
            return {'zone': 'red', 'color': '#dc3545', 'label': 'HIGH RISK'}
        elif value >= thresholds.get('yellow', 50):
            return {'zone': 'yellow', 'color': '#ffc107', 'label': 'MODERATE'}
        else:
            return {'zone': 'green', 'color': '#28a745', 'label': 'LOW RISK'}
    else:
        if value >= thresholds.get('green', 70):
            return {'zone': 'green', 'color': '#28a745', 'label': 'STRONG'}
        elif value >= thresholds.get('yellow', 40):
            return {'zone': 'yellow', 'color': '#ffc107', 'label': 'MODERATE'}
        else:
            return {'zone': 'red', 'color': '#dc3545', 'label': 'WEAK'}

def save_metric_history(dashboard: str, metric_key: str, value: float):
    """Save metric value to history"""
    try:
        conn = sqlite3.connect(str(HISTORY_DB))
        cursor = conn.cursor()
        today = datetime.now(timezone.utc).date().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO metrics_history (date, dashboard, metric_key, value)
            VALUES (?, ?, ?, ?)
        ''', (today, dashboard, metric_key, value))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Failed to save metric history: {e}")

def get_metric_history(dashboard: str, metric_key: str, days: int = 90) -> List[float]:
    """Get historical values for a metric"""
    try:
        conn = sqlite3.connect(str(HISTORY_DB))
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
        
        cursor.execute('''
            SELECT value FROM metrics_history
            WHERE dashboard = ? AND metric_key = ? AND date >= ?
            ORDER BY date ASC
        ''', (dashboard, metric_key, cutoff_date))
        
        values = [row[0] for row in cursor.fetchall()]
        conn.close()
        return values
    except Exception as e:
        logger.warning(f"Failed to get metric history: {e}")
        return []

def get_previous_values(dashboard: str, metric_key: str) -> Tuple[Optional[float], Optional[float]]:
    """Get previous day and week values"""
    try:
        conn = sqlite3.connect(str(HISTORY_DB))
        cursor = conn.cursor()
        
        # Get previous day
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat()
        cursor.execute('''
            SELECT value FROM metrics_history
            WHERE dashboard = ? AND metric_key = ? AND date = ?
        ''', (dashboard, metric_key, yesterday))
        prev_day = cursor.fetchone()
        prev_day_value = prev_day[0] if prev_day else None
        
        # Get previous week
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
        cursor.execute('''
            SELECT value FROM metrics_history
            WHERE dashboard = ? AND metric_key = ? AND date = ?
        ''', (dashboard, metric_key, week_ago))
        prev_week = cursor.fetchone()
        prev_week_value = prev_week[0] if prev_week else None
        
        conn.close()
        return prev_day_value, prev_week_value
    except Exception as e:
        logger.warning(f"Failed to get previous values: {e}")
        return None, None

def enhance_metric(metric: Dict, dashboard: str, metric_key: str, 
                   thresholds: Optional[Dict] = None, reverse: bool = False) -> Dict:
    """
    Enhance a metric with percentile, trend, and color coding
    """
    try:
        value = float(metric.get('value', 0))
        
        # Save to history
        save_metric_history(dashboard, metric_key, value)
        
        # Get historical data
        history = get_metric_history(dashboard, metric_key)
        percentile = get_percentile(value, history)
        
        # Get previous values for trend
        prev_day, prev_week = get_previous_values(dashboard, metric_key)
        trend = get_trend(value, prev_day, prev_week)
        
        # Get color zone
        if thresholds:
            color_zone = get_color_zone(value, thresholds, reverse)
        else:
            # Default thresholds based on percentile
            if percentile >= 80:
                color_zone = {'zone': 'red', 'color': '#dc3545', 'label': 'HIGH'} if reverse else {'zone': 'green', 'color': '#28a745', 'label': 'STRONG'}
            elif percentile >= 50:
                color_zone = {'zone': 'yellow', 'color': '#ffc107', 'label': 'MODERATE'}
            else:
                color_zone = {'zone': 'green', 'color': '#28a745', 'label': 'LOW'} if reverse else {'zone': 'red', 'color': '#dc3545', 'label': 'WEAK'}
        
        # Enhanced metric
        enhanced = metric.copy()
        enhanced['percentile'] = percentile
        enhanced['trend'] = trend
        enhanced['color_zone'] = color_zone
        enhanced['historical_count'] = len(history)
        
        return enhanced
    except Exception as e:
        logger.warning(f"Failed to enhance metric {metric_key}: {e}")
        return metric

def save_dashboard_score(dashboard: str, score: float, metadata: Optional[Dict] = None):
    """Save dashboard composite score"""
    try:
        conn = sqlite3.connect(str(HISTORY_DB))
        cursor = conn.cursor()
        today = datetime.now(timezone.utc).date().isoformat()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO dashboard_scores (date, dashboard, score, metadata)
            VALUES (?, ?, ?, ?)
        ''', (today, dashboard, score, metadata_json))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Failed to save dashboard score: {e}")

def get_dashboard_score_history(dashboard: str, days: int = 30) -> List[Dict]:
    """Get historical dashboard scores"""
    try:
        conn = sqlite3.connect(str(HISTORY_DB))
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
        
        cursor.execute('''
            SELECT date, score, metadata FROM dashboard_scores
            WHERE dashboard = ? AND date >= ?
            ORDER BY date ASC
        ''', (dashboard, cutoff_date))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'date': row[0],
                'score': row[1],
                'metadata': json.loads(row[2]) if row[2] else {}
            })
        
        conn.close()
        return results
    except Exception as e:
        logger.warning(f"Failed to get dashboard score history: {e}")
        return []

def calculate_regime(metrics: List[Dict]) -> Dict:
    """
    Detect market regime: Calm / Rising Vol / Crisis
    Based on VIX, MOVE, and other volatility indicators
    """
    vix_metric = next((m for m in metrics if 'VIX' in m.get('name', '')), None)
    move_metric = next((m for m in metrics if 'MOVE' in m.get('name', '')), None)
    
    if not vix_metric or not move_metric:
        return {'regime': 'Unknown', 'confidence': 0, 'color': '#718096'}
    
    try:
        vix_value = float(vix_metric.get('value', 0))
        move_value = float(move_metric.get('value', 0))
        
        # Regime detection logic
        if vix_value >= 30 or move_value >= 120:
            regime = 'Crisis'
            color = '#dc3545'
            confidence = 0.9
        elif vix_value >= 20 or move_value >= 90:
            regime = 'Rising Volatility'
            color = '#ffc107'
            confidence = 0.75
        else:
            regime = 'Calm'
            color = '#28a745'
            confidence = 0.8
        
        return {
            'regime': regime,
            'confidence': confidence,
            'color': color,
            'vix': vix_value,
            'move': move_value
        }
    except:
        return {'regime': 'Unknown', 'confidence': 0, 'color': '#718096'}

