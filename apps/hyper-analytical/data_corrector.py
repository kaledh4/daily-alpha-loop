"""
Data Corrector Module for Hyper Analytical
=========================================

This module provides functions to correct market data based on live information
to ensure the analysis reflects current market conditions.

Features:
- Live data fetching and comparison
- Data correction algorithms
- Confidence scoring for corrected data
- Integration with existing analysis pipeline

Author: Hyper Analytical
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

class DataCorrector:
    """
    Data Corrector for Hyper Analytical Analysis
    
    This class provides methods to fetch live data and correct analysis data
    based on current market conditions.
    """
    
    def __init__(self):
        """Initialize the DataCorrector."""
        self.live_data_cache = {}
        self.last_fetch_time = None
    
    def fetch_live_bitcoin_data(self) -> Optional[float]:
        """
        Fetch current Bitcoin price from multiple sources for accuracy.
        
        Returns:
            float: Current Bitcoin price in USD, or None if fetch fails
        """
        try:
            # Primary source: Yahoo Finance
            btc = yf.Ticker("BTC-USD")
            hist = btc.history(period="1d", interval="1h")
            
            if not hist.empty:
                # Get the most recent closing price
                current_price = float(hist['Close'].iloc[-1])
                return current_price
            
            return None
        except Exception as e:
            print(f"⚠️ Error fetching Bitcoin data: {e}")
            return None
    
    def fetch_live_dxy_data(self) -> Optional[float]:
        """
        Fetch current DXY (US Dollar Index) data.
        
        Returns:
            float: Current DXY value, or None if fetch fails
        """
        try:
            # Fetch DXY data from Yahoo Finance
            dxy = yf.Ticker("DX-Y.NYB")
            hist = dxy.history(period="1d", interval="1h")
            
            if not hist.empty:
                # Get the most recent closing price
                current_dxy = float(hist['Close'].iloc[-1])
                return current_dxy
            
            return None
        except Exception as e:
            print(f"⚠️ Error fetching DXY data: {e}")
            return None
    
    def calculate_confidence_score(self, analysis_value: float, live_value: float) -> Dict[str, any]:
        """
        Calculate confidence score based on the difference between analysis and live data.
        
        Args:
            analysis_value: Value from the analysis
            live_value: Current live value
            
        Returns:
            dict: Confidence score and assessment
        """
        if live_value == 0:
            return {"score": 0, "level": "NONE", "assessment": "No live data available"}
        
        # Calculate percentage difference
        diff_pct = abs(analysis_value - live_value) / live_value * 100
        
        # Determine confidence level based on difference
        if diff_pct <= 1:
            confidence = {"score": 95, "level": "VERY_HIGH", "assessment": "Excellent match"}
        elif diff_pct <= 3:
            confidence = {"score": 85, "level": "HIGH", "assessment": "Good match"}
        elif diff_pct <= 5:
            confidence = {"score": 70, "level": "MEDIUM", "assessment": "Acceptable match"}
        elif diff_pct <= 10:
            confidence = {"score": 50, "level": "LOW", "assessment": "Significant discrepancy"}
        else:
            confidence = {"score": 20, "level": "VERY_LOW", "assessment": "Major discrepancy"}
        
        confidence["difference_percent"] = round(diff_pct, 2)
        return confidence
    
    def correct_bitcoin_data(self, analysis_btc_price: float) -> Dict[str, any]:
        """
        Correct Bitcoin price data based on live information.
        
        Args:
            analysis_btc_price: Bitcoin price from analysis
            
        Returns:
            dict: Corrected data with confidence score
        """
        live_btc = self.fetch_live_bitcoin_data()
        
        if live_btc is None:
            return {
                "original_value": analysis_btc_price,
                "corrected_value": analysis_btc_price,
                "live_value": None,
                "confidence": {"score": 0, "level": "NONE", "assessment": "No live data"},
                "correction_applied": False
            }
        
        confidence = self.calculate_confidence_score(analysis_btc_price, live_btc)
        
        # Apply correction if discrepancy is significant
        correction_threshold = 5  # 5% threshold for correction
        if confidence["difference_percent"] > correction_threshold:
            corrected_value = live_btc
            correction_applied = True
        else:
            corrected_value = analysis_btc_price
            correction_applied = False
        
        return {
            "original_value": analysis_btc_price,
            "corrected_value": corrected_value,
            "live_value": live_btc,
            "confidence": confidence,
            "correction_applied": correction_applied
        }
    
    def correct_dxy_data(self, analysis_dxy: float) -> Dict[str, any]:
        """
        Correct DXY data based on live information.
        
        Args:
            analysis_dxy: DXY value from analysis
            
        Returns:
            dict: Corrected data with confidence score
        """
        live_dxy = self.fetch_live_dxy_data()
        
        if live_dxy is None:
            return {
                "original_value": analysis_dxy,
                "corrected_value": analysis_dxy,
                "live_value": None,
                "confidence": {"score": 0, "level": "NONE", "assessment": "No live data"},
                "correction_applied": False
            }
        
        confidence = self.calculate_confidence_score(analysis_dxy, live_dxy)
        
        # Apply correction if discrepancy is significant
        correction_threshold = 3  # 3% threshold for correction
        if confidence["difference_percent"] > correction_threshold:
            corrected_value = live_dxy
            correction_applied = True
        else:
            corrected_value = analysis_dxy
            correction_applied = False
        
        return {
            "original_value": analysis_dxy,
            "corrected_value": corrected_value,
            "live_value": live_dxy,
            "confidence": confidence,
            "correction_applied": correction_applied
        }
    
    def generate_correction_report(self, corrections: Dict[str, any]) -> str:
        """
        Generate a human-readable correction report.
        
        Args:
            corrections: Dictionary of corrections applied
            
        Returns:
            str: Formatted correction report
        """
        report = "## 📊 Data Correction Report\n"
        report += "-" * 40 + "\n\n"
        
        for key, correction in corrections.items():
            report += f"**{key.replace('_', ' ').title()}**\n"
            report += f"- Original: {correction['original_value']:,}\n"
            
            if correction['live_value']:
                report += f"- Live: {correction['live_value']:,}\n"
                report += f"- Corrected: {correction['corrected_value']:,}\n"
                report += f"- Difference: {correction['confidence']['difference_percent']}%\n"
                report += f"- Confidence: {correction['confidence']['level']} ({correction['confidence']['score']}%)\n"
                report += f"- Correction Applied: {'Yes' if correction['correction_applied'] else 'No'}\n"
            else:
                report += "- Live data: Not available\n"
                report += "- Corrected: No change (no live data)\n"
            
            report += "\n"
        
        return report

# Example usage
if __name__ == "__main__":
    corrector = DataCorrector()
    
    # Example corrections
    btc_correction = corrector.correct_bitcoin_data(95847.23)
    dxy_correction = corrector.correct_dxy_data(104.87)
    
    corrections = {
        "bitcoin_price": btc_correction,
        "dxy_index": dxy_correction
    }
    
    print(corrector.generate_correction_report(corrections))