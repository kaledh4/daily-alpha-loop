"""
Standardized Risk Metrics Module for Hyper Analytical
====================================================

This module provides standardized risk metrics calculation including:
- MVRV Z-Score
- Puell Multiple
- Risk Metric (logarithmic regression)
- Confidence scoring for each metric

Author: Hyper Analytical
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

class RiskMetricsCalculator:
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
    
    def calculate_mvrv_zscore(self) -> Dict[str, any]:
        """
        Calculate the MVRV Z-Score.
        
        Formula: (Market Cap - Realized Cap) / StdDev(Market Cap - Realized Cap)
        
        Note: This is a simplified implementation. In practice, you would need:
        - On-chain data for UTXO ages
        - Realized capitalization calculations
        - Historical MVRV data for standard deviation
        
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
                "value": 0,
                "error": f"Calculation error: {str(e)}",
                "confidence": "LOW"
            }
    
    def calculate_puell_multiple(self) -> Dict[str, any]:
        """
        Calculate the Puell Multiple.
        
        Formula: Daily Issuance USD Value / 365-day MA of Daily Issuance USD Value
        
        Note: This requires mining data which is not available in standard APIs.
        This is a simplified implementation for demonstration.
        
        Returns:
            dict: Puell Multiple with interpretation
        """
        try:
            # Simplified implementation - in practice would use actual mining data
            current_price = self.btc_data['Close'].iloc[-1]
            
            # Estimate daily issuance (simplified)
            # Bitcoin halves approximately every 210,000 blocks (~4 years)
            # Current block reward is 3.125 BTC per block
            # ~144 blocks per day
            daily_btc_mined = 3.125 * 144  # Simplified
            daily_issuance_usd = daily_btc_mined * current_price
            
            # 365-day moving average of daily issuance
            # In practice, this would be actual historical mining data
            ma_daily_issuance = daily_issuance_usd * 0.9  # Simplified assumption
            
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
                "value": round(puell_multiple, 2),
                "daily_issuance_usd": daily_issuance_usd,
                "ma_daily_issuance": ma_daily_issuance,
                "interpretation": interpretation,
                "confidence": "MEDIUM"  # Would be higher with real mining data
            }
            
        except Exception as e:
            return {
                "metric": "Puell Multiple",
                "value": 0,
                "error": f"Calculation error: {str(e)}",
                "confidence": "LOW"
            }
    
    def calculate_log_regression_risk(self) -> Dict[str, any]:
        """
        Calculate the Logarithmic Regression Risk Metric (our proprietary metric).
        
        This is the enhanced version of the existing risk metric with confidence scoring.
        
        Returns:
            dict: Log Regression Risk Metric with confidence
        """
        try:
            data = self.btc_data.copy().dropna()
            
            # Prepare logarithmic data
            data['log_price'] = np.log(data['Close'])
            data['time_idx'] = np.arange(1, len(data) + 1)
            data['log_time'] = np.log(data['time_idx'])
            
            # Fit Linear Regression on Log-Log data
            slope, intercept = np.polyfit(data['log_time'], data['log_price'], 1)
            data['fair_value'] = np.exp(intercept + slope * data['log_time'])
            
            # Calculate % Deviation from Fair Value
            data['deviation'] = (data['Close'] - data['fair_value']) / data['fair_value']
            
            # Normalize to 0-1 using rolling 200-week window (~4 years)
            roll_min = data['deviation'].rolling(window=200, min_periods=50).min()
            roll_max = data['deviation'].rolling(window=200, min_periods=50).max()
            
            data['risk'] = (data['deviation'] - roll_min) / (roll_max - roll_min)
            data['risk'] = data['risk'].clip(0, 1)  # Ensure 0-1 range
            
            current_risk = float(data['risk'].iloc[-1])
            previous_risk = float(data['risk'].iloc[-2])
            
            # Confidence scoring based on data quality and stability
            data_points = len(data)
            if data_points > 1000:
                data_quality = "HIGH"
            elif data_points > 500:
                data_quality = "MEDIUM"
            else:
                data_quality = "LOW"
            
            # Stability measure (standard deviation of recent risk values)
            recent_risk_std = data['risk'].tail(52).std()
            if recent_risk_std < 0.1:
                stability = "HIGH"
            elif recent_risk_std < 0.2:
                stability = "MEDIUM"
            else:
                stability = "LOW"
            
            # Overall confidence
            if data_quality == "HIGH" and stability == "HIGH":
                confidence = "VERY_HIGH"
                confidence_score = 95
            elif data_quality == "HIGH" or stability == "HIGH":
                confidence = "HIGH"
                confidence_score = 85
            elif data_quality == "MEDIUM" and stability == "MEDIUM":
                confidence = "MEDIUM"
                confidence_score = 70
            else:
                confidence = "LOW"
                confidence_score = 50
            
            # Interpretation
            if current_risk > 0.8:
                interpretation = "Very High Risk - Distribution Zone"
            elif current_risk > 0.7:
                interpretation = "High Risk - Elevated Valuations"
            elif current_risk > 0.4:
                interpretation = "Neutral - Balanced Market"
            elif current_risk > 0.2:
                interpretation = "Low Risk - Accumulation Zone"
            else:
                interpretation = "Very Low Risk - Deep Value"
            
            return {
                "metric": "Log Regression Risk",
                "value": round(current_risk, 2),
                "previous": round(previous_risk, 2),
                "trend": "Rising" if current_risk > previous_risk else "Falling",
                "interpretation": interpretation,
                "confidence": confidence,
                "confidence_score": confidence_score,
                "data_quality": data_quality,
                "stability": stability
            }
            
        except Exception as e:
            return {
                "metric": "Log Regression Risk",
                "value": 0.5,
                "error": f"Calculation error: {str(e)}",
                "confidence": "LOW"
            }
    
    def compare_risk_metrics(self) -> Dict[str, any]:
        """
        Compare all available risk metrics.
        
        Returns:
            dict: Comparison of all risk metrics with composite assessment
        """
        mvrv = self.calculate_mvrv_zscore()
        puell = self.calculate_puell_multiple()
        log_risk = self.calculate_log_regression_risk()
        
        metrics = {
            "mvrv_zscore": mvrv,
            "puell_multiple": puell,
            "log_regression_risk": log_risk
        }
        
        # Composite risk assessment
        risk_values = []
        confidences = []
        
        # Collect valid risk values and their confidences
        for metric in [mvrv, puell, log_risk]:
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
                else:
                    # Log Regression Risk is already 0-1
                    normalized_value = raw_value
                
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
    print("Risk Metrics Module Loaded")
    print("Use RiskMetricsCalculator to compute standardized risk metrics")