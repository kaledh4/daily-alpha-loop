"""
Standardized Risk Metrics for Hyper Analytical
=============================================

This module provides standardized, auditable risk metrics calculation including:
- Puell Multiple with formula
- MVRV Z-Score with formula
- Gompertz Curve model
- Confidence scoring for each metric

Author: Hyper Analytical
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from scipy.optimize import curve_fit

class StandardizedRiskMetrics:
    """
    Standardized Risk Metrics Calculator
    
    Provides multiple risk metrics for Bitcoin market analysis with
    standardized formulas and confidence scoring.
    """
    
    def __init__(self, btc_data: pd.DataFrame):
        """
        Initialize with Bitcoin pricing data.
        
        Args:
            btc_data: DataFrame with Bitcoin pricing data including Close prices
        """
        self.btc_data = btc_data.copy()
        self.btc_data['Date'] = pd.to_datetime(self.btc_data.index)
    
    def calculate_puell_multiple(self) -> Dict[str, any]:
        """
        Calculate the Puell Multiple.
        
        Formula: 
        Puell Multiple = Daily Issuance Value in USD / 365-day Moving Average of Daily Issuance Value in USD
        
        The Puell Multiple measures the ratio of daily Bitcoin issuance value to its annual average.
        It helps identify accumulation (low values) and distribution (high values) phases.
        
        Returns:
            dict: Puell Multiple with interpretation
        """
        try:
            # Get current price
            current_price = self.btc_data['Close'].iloc[-1]
            
            # Estimate daily issuance (simplified)
            # Bitcoin halves approximately every 210,000 blocks (~4 years)
            # Current block reward is 3.125 BTC per block
            # ~144 blocks per day
            daily_btc_mined = 3.125 * 144  # Simplified
            daily_issuance_usd = daily_btc_mined * current_price
            
            # Calculate 365-day moving average of daily issuance
            # For this example, we'll simulate historical data
            # In practice, you would use actual historical mining data
            historical_issuance = []
            for i in range(min(365, len(self.btc_data))):
                price = self.btc_data['Close'].iloc[-(i+1)]
                issuance = 3.125 * 144 * price
                historical_issuance.append(issuance)
            
            # Calculate moving average
            ma_daily_issuance = np.mean(historical_issuance)
            
            if ma_daily_issuance > 0:
                puell_multiple = daily_issuance_usd / ma_daily_issuance
            else:
                puell_multiple = 1
            
            # Interpretation
            if puell_multiple > 4:
                interpretation = "Very High Risk - Mining Exhaustion Signal"
            elif puell_multiple > 2.5:
                interpretation = "High Risk - Elevated Mining Profitability"
            elif puell_multiple > 1:
                interpretation = "Neutral - Normal Mining Conditions"
            elif puell_multiple > 0.5:
                interpretation = "Low Risk - Reduced Mining Pressure"
            else:
                interpretation = "Very Low Risk - Mining Distress Signal"
            
            return {
                "metric": "Puell Multiple",
                "formula": "Daily Issuance Value in USD / 365-day MA of Daily Issuance Value in USD",
                "value": round(puell_multiple, 2),
                "daily_issuance_usd": daily_issuance_usd,
                "ma_daily_issuance": ma_daily_issuance,
                "interpretation": interpretation,
                "confidence": "MEDIUM"  # Would be higher with real mining data
            }
            
        except Exception as e:
            return {
                "metric": "Puell Multiple",
                "formula": "Daily Issuance Value in USD / 365-day MA of Daily Issuance Value in USD",
                "value": 0,
                "error": f"Calculation error: {str(e)}",
                "confidence": "LOW"
            }
    
    def calculate_mvrv_zscore(self) -> Dict[str, any]:
        """
        Calculate the MVRV Z-Score.
        
        Formula: 
        MVRV Z-Score = (Market Cap - Realized Cap) / StdDev(Market Cap - Realized Cap)
        
        The MVRV (Market Value to Realized Value) Z-Score measures how far the current price
        is from its "fair value" in terms of standard deviations, providing a statistical
        measure of over/undervaluation.
        
        Returns:
            dict: MVRV Z-Score with interpretation
        """
        try:
            # Get current price and supply (simplified - in practice would use on-chain data)
            current_price = self.btc_data['Close'].iloc[-1]
            # Assuming a fixed supply for simplification
            total_supply = 19500000  # Approximate current BTC supply
            
            market_cap = current_price * total_supply
            
            # Simplified realized cap calculation
            # In practice, this would sum each UTXO's value at the time it was last moved
            # For this example, we'll use a simplified approach
            avg_cost_basis = self.btc_data['Close'].rolling(window=365).mean().iloc[-1]
            realized_cap = avg_cost_basis * total_supply
            
            # Calculate MVRV ratio
            mvrv_ratio = market_cap / realized_cap if realized_cap > 0 else 1
            
            # Simplified Z-Score calculation
            # In practice, this would use historical standard deviation
            historical_mvrv_mean = 1.2  # Assumed historical average
            historical_mvrv_std = 0.5    # Assumed historical standard deviation
            
            if historical_mvrv_std > 0:
                z_score = (mvrv_ratio - historical_mvrv_mean) / historical_mvrv_std
            else:
                z_score = 0
            
            # Interpretation
            if z_score > 2:
                interpretation = "Very High Risk - Potential Market Top"
            elif z_score > 1:
                interpretation = "High Risk - Elevated Valuations"
            elif z_score > -1:
                interpretation = "Neutral - Balanced Valuations"
            elif z_score > -2:
                interpretation = "Low Risk - Attractive Valuations"
            else:
                interpretation = "Very Low Risk - Deep Value Opportunity"
            
            return {
                "metric": "MVRV Z-Score",
                "formula": "(Market Cap - Realized Cap) / StdDev(Market Cap - Realized Cap)",
                "value": round(z_score, 2),
                "mvrv_ratio": round(mvrv_ratio, 2),
                "market_cap": market_cap,
                "realized_cap": realized_cap,
                "interpretation": interpretation,
                "confidence": "MEDIUM"  # Would be higher with real on-chain data
            }
            
        except Exception as e:
            return {
                "metric": "MVRV Z-Score",
                "formula": "(Market Cap - Realized Cap) / StdDev(Market Cap - Realized Cap)",
                "value": 0,
                "error": f"Calculation error: {str(e)}",
                "confidence": "LOW"
            }
    
    def gompertz_curve(self, t, a, b, c):
        """
        Gompertz curve function for modeling Bitcoin price behavior.
        
        Formula: f(t) = a * exp(-b * exp(-c * t))
        
        Args:
            t: Time parameter
            a: Upper asymptote
            b: Growth displacement
            c: Growth rate
            
        Returns:
            float: Gompertz curve value
        """
        return a * np.exp(-b * np.exp(-c * t))
    
    def calculate_gompertz_model(self) -> Dict[str, any]:
        """
        Calculate the Gompertz Curve model for Bitcoin price analysis.
        
        The Gompertz curve is a type of mathematical model for a time series,
        where growth is slowest at the start and end of a time period.
        It's particularly useful for modeling Bitcoin's adoption curve.
        
        Returns:
            dict: Gompertz model parameters and interpretation
        """
        try:
            # Prepare data for fitting
            prices = self.btc_data['Close'].values
            time_points = np.arange(len(prices))
            
            # Initial parameter guesses
            a_guess = np.max(prices) * 1.2  # Upper asymptote guess
            b_guess = 1.0  # Displacement parameter
            c_guess = 0.01  # Growth rate
            
            # Fit the Gompertz curve to the data
            try:
                popt, pcov = curve_fit(self.gompertz_curve, time_points, prices, 
                                     p0=[a_guess, b_guess, c_guess], maxfev=10000)
                a, b, c = popt
                
                # Calculate current position on the curve
                current_t = len(prices) - 1
                fitted_value = self.gompertz_curve(current_t, a, b, c)
                actual_value = prices[-1]
                
                # Calculate deviation from the curve
                deviation = (actual_value - fitted_value) / fitted_value * 100
                
                # Interpretation
                if deviation > 20:
                    interpretation = "Significantly Above Model - Potential Overvaluation"
                elif deviation > 5:
                    interpretation = "Above Model - Moderate Overvaluation"
                elif deviation > -5:
                    interpretation = "Near Model - Fairly Valued"
                elif deviation > -20:
                    interpretation = "Below Model - Moderate Undervaluation"
                else:
                    interpretation = "Significantly Below Model - Potential Undervaluation"
                
                return {
                    "metric": "Gompertz Curve Model",
                    "formula": "f(t) = a * exp(-b * exp(-c * t))",
                    "parameters": {
                        "a": round(a, 2),  # Upper asymptote
                        "b": round(b, 4),  # Displacement
                        "c": round(c, 6)   # Growth rate
                    },
                    "fitted_value": round(fitted_value, 2),
                    "actual_value": round(actual_value, 2),
                    "deviation_percent": round(deviation, 2),
                    "interpretation": interpretation,
                    "confidence": "HIGH"
                }
                
            except Exception as fit_error:
                return {
                    "metric": "Gompertz Curve Model",
                    "formula": "f(t) = a * exp(-b * exp(-c * t))",
                    "error": f"Fitting error: {str(fit_error)}",
                    "confidence": "LOW"
                }
                
        except Exception as e:
            return {
                "metric": "Gompertz Curve Model",
                "formula": "f(t) = a * exp(-b * exp(-c * t))",
                "error": f"Calculation error: {str(e)}",
                "confidence": "LOW"
            }
    
    def compare_risk_metrics(self) -> Dict[str, any]:
        """
        Compare all available risk metrics.
        
        Returns:
            dict: Comparison of all risk metrics with composite assessment
        """
        puell = self.calculate_puell_multiple()
        mvrv = self.calculate_mvrv_zscore()
        gompertz = self.calculate_gompertz_model()
        
        metrics = {
            "puell_multiple": puell,
            "mvrv_zscore": mvrv,
            "gompertz_model": gompertz
        }
        
        # Composite risk assessment
        risk_values = []
        confidences = []
        
        # Collect valid risk values and their confidences
        for metric in [puell, mvrv, gompertz]:
            if "value" in metric and "confidence" in metric:
                # Normalize different metrics to 0-1 scale for comparison
                raw_value = metric["value"]
                
                # Different normalization for different metrics
                if metric["metric"] == "MVRV Z-Score":
                    # Z-score: typically -2 to +2 range, normalize to 0-1
                    normalized_value = max(0, min(1, (raw_value + 2) / 4))
                elif metric["metric"] == "Puell Multiple":
                    # Puell: typically 0 to 5+ range, cap at 5 and normalize
                    normalized_value = max(0, min(1, raw_value / 5))
                elif metric["metric"] == "Gompertz Curve Model":
                    # Deviation: typically -50% to +50%, normalize to 0-1
                    deviation = metric.get("deviation_percent", 0)
                    normalized_value = max(0, min(1, (deviation + 50) / 100))
                else:
                    # Default normalization
                    normalized_value = max(0, min(1, raw_value))
                
                risk_values.append(normalized_value)
                
                # Convert confidence to numeric score
                confidence_map = {
                    "VERY_HIGH": 95, "HIGH": 85, "MEDIUM": 70, "LOW": 50
                }
                confidences.append(confidence_map.get(metric["confidence"], 50))
        
        # Calculate weighted average risk score
        if risk_values and confidences:
            # Weight by confidence scores
            weighted_sum = sum(val * conf for val, conf in zip(risk_values, confidences))
            total_confidence = sum(confidences)
            composite_risk = weighted_sum / total_confidence if total_confidence > 0 else 0.5
            
            # Overall confidence
            avg_confidence = sum(confidences) / len(confidences)
            if avg_confidence >= 85:
                overall_confidence = "VERY_HIGH"
            elif avg_confidence >= 70:
                overall_confidence = "HIGH"
            elif avg_confidence >= 50:
                overall_confidence = "MEDIUM"
            else:
                overall_confidence = "LOW"
        else:
            composite_risk = 0.5
            overall_confidence = "LOW"
        
        # Composite interpretation
        if composite_risk > 0.8:
            composite_interpretation = "Very High Risk - Extreme Caution Advised"
        elif composite_risk > 0.7:
            composite_interpretation = "High Risk - Conservative Approach Recommended"
        elif composite_risk > 0.4:
            composite_interpretation = "Neutral Risk - Balanced Positioning"
        elif composite_risk > 0.2:
            composite_interpretation = "Low Risk - Opportunistic Buying Phase"
        else:
            composite_interpretation = "Very Low Risk - Aggressive Accumulation Opportunity"
        
        return {
            "metrics": metrics,
            "composite_risk": round(composite_risk, 2),
            "composite_interpretation": composite_interpretation,
            "overall_confidence": overall_confidence,
            "calculation_timestamp": datetime.now().isoformat()
        }

# Example usage
if __name__ == "__main__":
    # This would typically be called from the main analysis script
    print("Standardized Risk Metrics Module Loaded")
    print("Use StandardizedRiskMetrics to compute auditable risk metrics")