"""
Example Enhanced Analysis Script
===============================

This script demonstrates the enhanced functionality of the Hyper Analytical system
including data validation, correction, and standardized risk metrics.

Author: Hyper Analytical
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Import our enhanced modules
try:
    from data_validator import BMSBCalculator, fetch_live_data, validate_analysis_data
    from data_corrector import DataCorrector
    from risk_metrics import RiskMetricsCalculator
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Required modules not available: {e}")
    MODULES_AVAILABLE = False

def demonstrate_enhanced_analysis():
    """Demonstrate the enhanced analysis capabilities."""
    if not MODULES_AVAILABLE:
        print("❌ Required modules not available. Please ensure all modules are installed.")
        return
    
    print("=" * 60)
    print("🚀 HYPER ANALYTICAL - Enhanced Analysis Demo")
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
    
    # 2. Demonstrate BMSB Calculator
    print("\n🧮 Demonstrating BMSB Calculator...")
    try:
        calculator = BMSBCalculator(btc)
        sma_20, ema_21 = calculator.get_bmsb()
        current_price = btc['Close'].iloc[-1]
        
        print(f"   Current BTC Price: ${current_price:,.2f}")
        print(f"   20-Week SMA: ${sma_20:,.2f}")
        print(f"   21-Week EMA: ${ema_21:,.2f}")
        
        # Determine position relative to BMSB
        band_top = max(sma_20, ema_21)
        band_bottom = min(sma_20, ema_21)
        
        if current_price > band_top:
            position = "ABOVE SUPPORT BAND (Bullish)"
        elif current_price < band_bottom:
            position = "BELOW SUPPORT BAND (Bearish)"
        else:
            position = "WITHIN SUPPORT BAND (Neutral)"
        
        print(f"   Position: {position}")
    except Exception as e:
        print(f"❌ BMSB calculation error: {e}")
    
    # 3. Demonstrate Data Validator
    print("\n🔍 Demonstrating Data Validator...")
    try:
        live_data = fetch_live_data()
        if live_data:
            print("   Live Data Fetch:")
            print(f"     BTC Price: ${live_data.get('btc_price', 'N/A'):,.2f}")
            print(f"     DXY Index: {live_data.get('dxy', 'N/A'):.2f}")
            print(f"     Timestamp: {live_data.get('timestamp', 'N/A')}")
        else:
            print("   ⚠️ Unable to fetch live data")
    except Exception as e:
        print(f"❌ Data validation error: {e}")
    
    # 4. Demonstrate Data Corrector
    print("\n🔧 Demonstrating Data Corrector...")
    try:
        corrector = DataCorrector()
        
        # Simulate analysis data that might be outdated
        analysis_btc_price = current_price * 1.05  # 5% higher than current
        analysis_dxy = 105.0  # Higher than typical
        
        print(f"   Analysis BTC Price: ${analysis_btc_price:,.2f}")
        print(f"   Analysis DXY: {analysis_dxy}")
        
        # Apply corrections
        btc_correction = corrector.correct_bitcoin_data(analysis_btc_price)
        dxy_correction = corrector.correct_dxy_data(analysis_dxy)
        
        print("\n   Correction Results:")
        print(f"     BTC - Original: ${btc_correction['original_value']:,.2f}")
        print(f"     BTC - Live: ${btc_correction['live_value'] or 'N/A':,.2f}")
        print(f"     BTC - Corrected: ${btc_correction['corrected_value']:,.2f}")
        print(f"     BTC - Difference: {btc_correction['confidence']['difference_percent']}%")
        print(f"     BTC - Confidence: {btc_correction['confidence']['level']}")
        
        print(f"     DXY - Original: {dxy_correction['original_value']:.2f}")
        print(f"     DXY - Live: {dxy_correction['live_value'] or 'N/A':.2f}")
        print(f"     DXY - Corrected: {dxy_correction['corrected_value']:.2f}")
        print(f"     DXY - Difference: {dxy_correction['confidence']['difference_percent']}%")
        print(f"     DXY - Confidence: {dxy_correction['confidence']['level']}")
    except Exception as e:
        print(f"❌ Data correction error: {e}")
    
    # 5. Demonstrate Risk Metrics Calculator
    print("\n📊 Demonstrating Risk Metrics Calculator...")
    try:
        risk_calculator = RiskMetricsCalculator(btc)
        risk_comparison = risk_calculator.compare_risk_metrics()
        
        print("   Risk Metrics Comparison:")
        print(f"     Composite Risk: {risk_comparison['composite_risk']}")
        print(f"     Overall Confidence: {risk_comparison['overall_confidence']}")
        print(f"     Interpretation: {risk_comparison['composite_interpretation']}")
        
        # Show individual metrics
        metrics = risk_comparison['metrics']
        for metric_name, metric_data in metrics.items():
            if 'value' in metric_data:
                print(f"     {metric_data['metric']}: {metric_data['value']}")
                print(f"       Interpretation: {metric_data['interpretation']}")
                print(f"       Confidence: {metric_data['confidence']}")
            else:
                print(f"     {metric_name}: Error - {metric_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Risk metrics error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Enhanced Analysis Demo Complete")
    print("=" * 60)

if __name__ == "__main__":
    demonstrate_enhanced_analysis()