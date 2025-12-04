"""
Data Validator Module for Hyper Analytical
==========================================

This module provides functions to validate and correct market data
to ensure the analysis is based on accurate, up-to-date information.

Features:
- Data validation against external sources
- Technical indicator recalculation
- Risk metric standardization
- Data quality reporting

Author: Hyper Analytical
"""

import pandas as pd
import numpy as np
import yfinance as yf
import pandas_datareader.data as web
from datetime import datetime, timedelta

class BMSBCalculator:
    """
    Bull Market Support Band Calculator
    
    Calculates the 20-Week SMA and 21-Week EMA for Bitcoin pricing data.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with pricing data.
        
        Args:
            data: DataFrame with 'Close' column containing price data
        """
        self.data = data.copy()
        
    def calculate_sma(self, period: int = 20) -> float:
        """
        Calculate Simple Moving Average for specified period.
        
        Args:
            period: Number of periods for SMA calculation (default: 20)
            
        Returns:
            float: SMA value for the latest period
        """
        if len(self.data) < period:
            raise ValueError(f"Insufficient data for {period}-week SMA calculation")
        
        # Calculate SMA for the last 'period' weeks
        sma = self.data['Close'].tail(period).mean()
        return float(sma)
    
    def calculate_ema(self, period: int = 21) -> float:
        """
        Calculate Exponential Moving Average for specified period.
        
        Args:
            period: Number of periods for EMA calculation (default: 21)
            
        Returns:
            float: EMA value for the latest period
        """
        if len(self.data) < period:
            raise ValueError(f"Insufficient data for {period}-week EMA calculation")
        
        # Calculate EMA using pandas ewm function
        ema = self.data['Close'].ewm(span=period, adjust=False).mean().iloc[-1]
        return float(ema)
    
    def get_bmsb(self) -> tuple:
        """
        Calculate the complete Bull Market Support Band.
        
        Returns:
            tuple: (SMA_20, EMA_21) values
        """
        sma_20 = self.calculate_sma(20)
        ema_21 = self.calculate_ema(21)
        return (sma_20, ema_21)

def fetch_live_data():
    """
    Fetch live market data for validation purposes.
    
    Returns:
        dict: Dictionary containing current market data
    """
    try:
        # Fetch current Bitcoin price (using daily data for more accuracy)
        btc = yf.Ticker("BTC-USD")
        btc_info = btc.history(period="1d")
        btc_price = float(btc_info['Close'].iloc[-1])
        
        # Fetch current DXY data
        dxy = yf.Ticker("DX-Y.NYB")
        dxy_info = dxy.history(period="1d")
        dxy_value = float(dxy_info['Close'].iloc[-1])
        
        # Note: For Fed Funds Rate, we would typically use FRED API
        # For this implementation, we'll return placeholder values
        # In a production system, this would connect to FRED API
        
        return {
            "btc_price": btc_price,
            "dxy": dxy_value,
            "fed_funds_rate": None,  # Would be fetched from FRED in production
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"⚠️ Error fetching live data: {e}")
        return None

def validate_analysis_data(analysis_data: dict, live_data: dict) -> dict:
    """
    Validate analysis data against live market data.
    
    Args:
        analysis_data: Data from the analysis JSON
        live_data: Current market data
        
    Returns:
        dict: Validation report with discrepancies
    """
    if not live_data:
        return {"error": "No live data available for validation"}
    
    report = {
        "validation_timestamp": datetime.now().isoformat(),
        "discrepancies": {}
    }
    
    # Validate Bitcoin price
    analysis_btc = analysis_data.get("btc_price", 0)
    live_btc = live_data.get("btc_price", 0)
    
    if live_btc > 0:
        price_diff_pct = abs(analysis_btc - live_btc) / live_btc * 100
        report["discrepancies"]["btc_price"] = {
            "analysis_value": analysis_btc,
            "live_value": live_btc,
            "difference_percent": round(price_diff_pct, 2),
            "status": "VALID" if price_diff_pct < 2 else "INVALID"
        }
    
    # Validate DXY
    analysis_dxy = analysis_data.get("macro", {}).get("dxy", 0)
    live_dxy = live_data.get("dxy", 0)
    
    if live_dxy > 0:
        dxy_diff_pct = abs(analysis_dxy - live_dxy) / live_dxy * 100
        report["discrepancies"]["dxy"] = {
            "analysis_value": analysis_dxy,
            "live_value": live_dxy,
            "difference_percent": round(dxy_diff_pct, 2),
            "status": "VALID" if dxy_diff_pct < 5 else "INVALID"
        }
    
    return report

def calculate_mvrv_zscore(market_cap: float, realized_cap: float, historical_window: int = 365) -> float:
    """
    Calculate the MVRV Z-Score, a standardized risk metric.
    
    Formula: (Market Cap - Realized Cap) / StdDev(Market Cap - Realized Cap)
    
    Args:
        market_cap: Current market capitalization
        realized_cap: Realized capitalization (sum of coin values at time of last movement)
        historical_window: Number of days to calculate standard deviation over
        
    Returns:
        float: MVRV Z-Score value
    """
    # Difference between market cap and realized cap
    mvrv_diff = market_cap - realized_cap
    
    # In a real implementation, we would calculate the standard deviation
    # over a historical window. For this example, we'll use a simplified approach.
    # In practice, you would need historical data for this calculation.
    
    # Placeholder standard deviation (would be calculated from historical data)
    std_dev = market_cap * 0.15  # Assumed 15% volatility
    
    if std_dev > 0:
        z_score = mvrv_diff / std_dev
        return round(z_score, 2)
    else:
        return 0.0

def generate_validation_report(analysis_data: dict) -> str:
    """
    Generate a human-readable validation report.
    
    Args:
        analysis_data: Data from the analysis JSON
        
    Returns:
        str: Formatted validation report
    """
    live_data = fetch_live_data()
    validation_result = validate_analysis_data(analysis_data, live_data)
    
    if "error" in validation_result:
        return f"Validation Error: {validation_result['error']}"
    
    report = "## 📊 Data Validation Report\n"
    report += "-" * 40 + "\n\n"
    
    discrepancies = validation_result.get("discrepancies", {})
    
    if not discrepancies:
        report += "No data discrepancies found.\n"
        return report
    
    # Bitcoin Price Validation
    if "btc_price" in discrepancies:
        btc_data = discrepancies["btc_price"]
        report += f"**Bitcoin Price Validation:**\n"
        report += f"- Analysis Value: ${btc_data['analysis_value']:,.2f}\n"
        report += f"- Live Value: ${btc_data['live_value']:,.2f}\n"
        report += f"- Difference: {btc_data['difference_percent']}%\n"
        report += f"- Status: {btc_data['status']}\n\n"
    
    # DXY Validation
    if "dxy" in discrepancies:
        dxy_data = discrepancies["dxy"]
        report += f"**DXY Index Validation:**\n"
        report += f"- Analysis Value: {dxy_data['analysis_value']:.2f}\n"
        report += f"- Live Value: {dxy_data['live_value']:.2f}\n"
        report += f"- Difference: {dxy_data['difference_percent']}%\n"
        report += f"- Status: {dxy_data['status']}\n\n"
    
    return report

# Example usage
if __name__ == "__main__":
    # This would typically be called from the main analysis script
    print("Data Validator Module Loaded")
    print("Use validate_analysis_data() to check data consistency")