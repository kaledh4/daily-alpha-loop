"""
Comprehensive Example Script for Hyper Analytical System
======================================================

This script demonstrates all the enhanced functionality of the Hyper Analytical system
including data validation, correction, standardized risk metrics, and macro data correction.

Author: Hyper Analytical
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import our enhanced modules
try:
    from crypto_validator import CryptoValidator
    from macro_data_corrector import MacroDataCorrector
    from standardized_risk_metrics import StandardizedRiskMetrics
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Required modules not available: {e}")
    MODULES_AVAILABLE = False

def demonstrate_comprehensive_analysis():
    """Demonstrate the comprehensive analysis capabilities."""
    if not MODULES_AVAILABLE:
        print("❌ Required modules not available. Please ensure all modules are installed.")
        return
    
    print("=" * 60)
    print("🚀 HYPER ANALYTICAL - Comprehensive Analysis Demo")
    print("=" * 60)
    
    # 1. Fetch sample data for demonstration
    print("\n📥 Fetching sample Bitcoin data...")
    try:
        # Fetch 5 years of weekly Bitcoin data
        btc = yf.download("BTC-USD", period="5y", interval="1wk")
        if isinstance(btc.columns, pd.MultiIndex):
            btc = btc.xs("BTC-USD", axis=1, level=1)
        
        # Remove incomplete current week
        btc = btc[:-1]
        print(f"✅ Fetched {len(btc)} weeks of Bitcoin data")
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return
    
    # 2. Demonstrate Crypto Validator (Technical Validation)
    print("\n🔍 Demonstrating Crypto Validator (Technical Validation)...")
    try:
        # Simulate the clinical audit scenario
        analysis_btc_price = 95847.00
        analysis_sma = 88432.00
        analysis_ema = 89202.00
        live_btc_price = 91506.00  # From audit
        
        # Use last 21 weeks of actual data
        weekly_closes = btc['Close'].tail(21)
        
        # Create validator
        validator = CryptoValidator(
            historical_prices=weekly_closes,
            analysis_price=analysis_btc_price,
            analysis_sma=analysis_sma,
            analysis_ema=analysis_ema
        )
        
        # Run validation
        validation_results = validator.validate_technicals(live_btc_price)
        print("   Technical Validation Results:")
        for _, row in validation_results.iterrows():
            print(f"     {row['Metric']}: {row['Verdict']}")
            if row['Analysis Value'] != "N/A":
                print(f"       Analysis: {row['Analysis Value']}")
                print(f"       Calculated: {row['Calculated Value']}")
    except Exception as e:
        print(f"❌ Crypto validation error: {e}")
    
    # 3. Demonstrate Macro Data Corrector
    print("\n🌐 Demonstrating Macro Data Corrector...")
    try:
        macro_corrector = MacroDataCorrector()
        
        # Simulate analysis data that's incorrect per audit
        analysis_dxy = 104.87  # Incorrect value from audit
        analysis_fed_rate = 5.33  # Incorrect value from audit
        
        print(f"   Analysis DXY: {analysis_dxy}")
        print(f"   Analysis Fed Rate: {analysis_fed_rate}%")
        
        # Apply corrections
        dxy_correction = macro_corrector.correct_dxy_data(analysis_dxy)
        fed_correction = macro_corrector.correct_fed_rate_data(analysis_fed_rate)
        
        print("\n   Macro Correction Results:")
        print(f"     DXY - Original: {dxy_correction['original_value']:.2f}")
        print(f"     DXY - Live: {dxy_correction['live_value'] or 'N/A':.2f}")
        print(f"     DXY - Corrected: {dxy_correction['corrected_value']:.2f}")
        print(f"     DXY - Difference: {dxy_correction['confidence']['difference_percent']}%")
        print(f"     DXY - Confidence: {dxy_correction['confidence']['level']}")
        
        print(f"     Fed Rate - Original: {fed_correction['original_value']:.2f}%")
        print(f"     Fed Rate - Live: {fed_correction['live_value'] or 'N/A':.2f}%")
        print(f"     Fed Rate - Corrected: {fed_correction['corrected_value']:.2f}%")
        print(f"     Fed Rate - Difference: {fed_correction['confidence']['difference_percent']}%")
        print(f"     Fed Rate - Confidence: {fed_correction['confidence']['level']}")
    except Exception as e:
        print(f"❌ Macro correction error: {e}")
    
    # 4. Demonstrate Standardized Risk Metrics
    print("\n📊 Demonstrating Standardized Risk Metrics...")
    try:
        risk_calculator = StandardizedRiskMetrics(btc)
        risk_comparison = risk_calculator.compare_risk_metrics()
        
        print("   Standardized Risk Metrics:")
        print(f"     Composite Risk: {risk_comparison['composite_risk']}")
        print(f"     Overall Confidence: {risk_comparison['overall_confidence']}")
        print(f"     Interpretation: {risk_comparison['composite_interpretation']}")
        
        # Show individual metrics with formulas
        metrics = risk_comparison['metrics']
        for metric_name, metric_data in metrics.items():
            if 'value' in metric_data:
                print(f"     {metric_data['metric']}: {metric_data['value']}")
                print(f"       Formula: {metric_data['formula']}")
                print(f"       Interpretation: {metric_data['interpretation']}")
                print(f"       Confidence: {metric_data['confidence']}")
            else:
                print(f"     {metric_name}: Error - {metric_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Risk metrics error: {e}")
    
    # 5. Demonstrate Probability Adjustment Based on Macro Factors
    print("\n📈 Demonstrating Probability Adjustment...")
    try:
        # Original probabilities from analysis
        original_bullish = 40  # %
        original_bearish = 25  # %
        original_neutral = 35  # %
        
        # Adjusted probabilities based on corrected macro data
        # Audit shows supportive macro environment (tailwinds)
        adjusted_bullish = 55  # %
        adjusted_bearish = 15  # %
        adjusted_neutral = 30  # %
        
        print("   Probability Distribution Adjustment:")
        print(f"     Original - Bullish: {original_bullish}%, Bearish: {original_bearish}%, Neutral: {original_neutral}%")
        print(f"     Adjusted - Bullish: {adjusted_bullish}%, Bearish: {adjusted_bearish}%, Neutral: {adjusted_neutral}%")
        print("     Reason: Corrected macro data shows tailwinds (weaker dollar, lower rates)")
        
        # Risk/Reward adjustment
        print("\n   Risk/Reward Adjustment:")
        print("     Original - 3:1 ratio (Stop-loss: $88K, Target: $108K)")
        print("     Adjusted - 5:1 ratio (Stop-loss: $87K, Target: $112K)")
        print("     Reason: Increased bullish probability justifies higher target")
    except Exception as e:
        print(f"❌ Probability adjustment error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Comprehensive Analysis Demo Complete")
    print("=" * 60)

def demonstrate_flask_api_integration():
    """Demonstrate how to integrate with the Flask API."""
    print("\n🔌 Demonstrating Flask API Integration...")
    print("   To use the Flask API, send a POST request to /validate_technicals")
    print("   with the following JSON payload:")
    print("""
   {
       "historical_prices": [91000, 91500, 92000, ...],
       "analysis_price": 95847.00,
       "analysis_sma": 88432.00,
       "analysis_ema": 89202.00,
       "live_price": 91506.00
   }
   """)
    print("   Start the API server with: python flask_validator_api.py")
    print("   The API will be available at: http://localhost:5000/validate_technicals")

if __name__ == "__main__":
    demonstrate_comprehensive_analysis()
    demonstrate_flask_api_integration()