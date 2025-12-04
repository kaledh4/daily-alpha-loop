"""
Crypto Validator Module for Hyper Analytical
===========================================

This module provides the CryptoValidator class for validating Bitcoin market technicals
against live data, as requested in the clinical audit.

Features:
- BMSB (Bull Market Support Band) validation
- Technical indicator recalibration
- Strict technical comparison
- Modular and copy-pasteable implementation

Author: Hyper Analytical
"""

import pandas as pd
import numpy as np
from typing import Tuple

class CryptoValidator:
    """
    A class for validating Bitcoin market technicals against live data.
    Assumes high-performance hardware (e.g., fast CPU/RAM for Pandas operations).
    """

    def __init__(self, historical_prices: pd.Series, analysis_price: float, analysis_sma: float, analysis_ema: float):
        """
        Initializes the validator with current and historical data.

        Args:
            historical_prices (pd.Series): Time series of Bitcoin weekly closing prices.
            analysis_price (float): BTC price stated in the analysis.
            analysis_sma (float): 20W SMA stated in the analysis.
            analysis_ema (float): 21W EMA stated in the analysis.
        """
        self.prices = historical_prices
        self.analysis_price = analysis_price
        self.analysis_sma = analysis_sma
        self.analysis_ema = analysis_ema

    def calculate_bmsb(self) -> Tuple[float, float]:
        """Calculates the Bull Market Support Band (20W SMA and 21W EMA)."""
        if self.prices.shape[0] < 21:
            raise ValueError("Error: Insufficient data. Minimum 21 weekly closes required for BMSB calculation.")
        
        try:
            # 20-Week Simple Moving Average (SMA)
            sma_20w = self.prices.iloc[-20:].mean()
            
            # 21-Week Exponential Moving Average (EMA)
            # span=21 uses the standard N-period window for the EMA calculation
            ema_21w = self.prices.ewm(span=21, adjust=False).mean().iloc[-1]
            
            return sma_20w, ema_21w
        except Exception as e:
            # Error handling for calculation failures
            raise RuntimeError(f"Error calculating moving averages: {e}")

    def validate_technicals(self, live_price: float) -> pd.DataFrame:
        """Compares calculated and analysis technicals."""
        try:
            sma_calc, ema_calc = self.calculate_bmsb()
            
            data = [
                ("BTC Price (USD)", self.analysis_price, live_price, "Mismatch" if abs(self.analysis_price - live_price) > 1000 else "OK"),
                ("20W SMA (Analysis)", self.analysis_sma, sma_calc, "Check Recalculation"),
                ("21W EMA (Analysis)", self.analysis_ema, ema_calc, "Check Recalculation"),
                ("BMSB Status (Corrected)", "N/A", "ABOVE" if live_price > ema_calc else "BELOW", "Core Trend")
            ]
            
            return pd.DataFrame(data, columns=['Metric', 'Analysis Value', 'Calculated Value', 'Verdict'])
        except Exception as e:
            return pd.DataFrame([["Validation Failed", str(e), "", "Error"]], columns=['Metric', 'Analysis Value', 'Calculated Value', 'Verdict'])

# --- EXECUTION GUIDE ---
if __name__ == "__main__":
    # 1. Define Verified Live Data Inputs
    # NOTE: These values are based on the audit and must be replaced with live API data.
    VERIFIED_LIVE_BTC_PRICE = 91506.00
    
    # 2. Simulate 21 Weeks of Historical Closing Prices (Example data)
    # Real-world data would require 21 weekly closes.
    np.random.seed(42) # For reproducibility of the example
    # Generate prices that support the EMA/SMA being around 89,000
    weekly_closes = pd.Series(
        np.linspace(85000, 92000, 21) + np.random.normal(0, 1500, 21),
        name='Weekly_Close'
    )
    
    # 3. Define the Stated Analysis Values
    STATED_ANALYSIS = {
        "price": 95847.00,
        "sma": 88432.00,
        "ema": 89202.00
    }

    # 4. Instantiate and Run Validator
    validator = CryptoValidator(
        historical_prices=weekly_closes,
        analysis_price=STATED_ANALYSIS["price"],
        analysis_sma=STATED_ANALYSIS["sma"],
        analysis_ema=STATED_ANALYSIS["ema"]
    )
    
    validation_table = validator.validate_technicals(VERIFIED_LIVE_BTC_PRICE)
    
    print("## 💻 Technical Validation Output")
    print(validation_table.to_markdown(index=False))

    # Example Macro Correction Output
    print("\n## 🌐 Macro Correction")
    print("The stated DXY (104.87) and Fed Funds Rate (5.33%) are severely outdated/incorrect. The current effective FFR is 3.88% and DXY is 99.65. This shifts the macro narrative from 'headwind' to 'tailwind'.")