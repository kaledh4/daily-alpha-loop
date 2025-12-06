# Daily Alpha Loop - Feature Integration Plan

## Overview
Massive refactoring to incorporate new features across 4 dashboards with ~8 minute read time each.

## 1. THE COIN - Enhanced Crypto Markets
### New Data Requirements
- **Dollar Strength**: DXY Index (98.97)
- **Interest Rates**: Fed Funds Rate (5.33%)
- **Extended Crypto Coverage**:
  - BTC: Price, Risk metric, Multiplier
  - ETH: Price, Risk metric, Multiplier
  - ETH/BTC: Ratio, Risk metric, Multiplier
  - VXV: Price, Risk metric, Multiplier
  - APT: Price, Risk metric, Multiplier
  - ADA: Price, Risk metric, Multiplier
  - NEAR: Price, Risk metric, Multiplier

### Risk Metrics
- Composite Risk calculation
- Bitcoin Risk Metric status (High/Medium/Low)
- Market Structure indicators
- Bull Market Support Band (20W SMA, 21W EMA)

### Implementation
- Extend `fetch_market_data()` to include alt-coins
- Add `fetch_crypto_risk_metrics()` function
- Update `build_coin_data()` with comprehensive crypto analysis
- Calculate risk scores and multipliers based on volatility

---

## 2. THE FRONTIER - Critical Timeline
### New Data Requirements
- **LIVE Day Counter**: Current day (Day 12)
- **Critical Milestones**:
  - Resource ID: 78 days
  - Data Assets: 108 days
  - Robotics Integration: 228 days
  - Operating Capability: 258 days

### Implementation
- Add `calculate_frontier_timeline()` function
- Store timeline data in frontier dashboard
- Add countdown timers to frontend  
- Visual timeline representation

---

## 3. THE MAP - Market Intelligence Hub
### New Data Requirements
- **Fear & Greed Index**: Value + classification
- **BTC Trend Analysis**:
  - Current price
  - RSI (14)
  - Trend (Bullish/Bearish)
- **Macro Pulse**:
  - 10Y Yield with % change
  - Gold price with % change
  - S&P 500 with % change
  - TASI with % change
- **Daily Market Intelligence**:
  - Community sentiment
  - Investor mode guidance
  - Macro view analysis
  - BTC market structure analysis
  - TASI & global markets
  - Actionable verdict (DE-RISK/ACCUMULATE/etc)
- **Weekly Watchlist**: 5 key events to monitor

### Implementation
- Extend `fetch_market_data()` with historical data for % changes
- Add `build_market_intelligence()` function
- Enhanced AI prompts for deeper analysis
- 4-5 sentence comprehensive macro synthesis

---

## 4. THE SHIELD - Crash Detector System
### New Data Requirements
- **Composite Risk Level**: LOW/ELEVATED/CRITICAL
- **Risk Score**: X/100 calculation
- **Key Stress Indicators**:
  - 10Y Treasury Bid-to-Cover (threshold: < 2.3x stress)
  - 30Y Auction Tail (threshold: > 3bps stress)
  - USD/JPY carry trade stress
  - USD/CNH yuan stability
  - China Credit Proxy (CBON ETF)
  - 10Y Treasury Yield (systemic trigger)
  - MOVE Index (threshold: > 90 stress)
- **AI Crash Prediction Analysis**
- **Latest Financial News Summary**

### Implementation
- Add `calculate_crash_risk_score()` function
- Implement stress level thresholds
- Add historical treasury auction data
- Enhanced crash prediction AI prompts
- Create comprehensive risk scoring system

---

## 5. THE COMMANDER - Update Integration
All new data automatically flows to Commander via unified data store.
Enhanced morning brief generation with cross-dashboard synthesis.

---

## 6. Unified Fetcher Updates (unified_fetcher_v3.py)

### New Functions to Add
1. `fetch_alt_coins()` - VXV, APT, ADA, NEAR
2. `fetch_fed_rate()` - Current Fed Funds rate
3. `calculate_crypto_risk_metrics()` - Risk scores and multipliers
4. `fetch_price_changes()` - Historical % changes for macro assets
5. `calculate_frontier_timeline()` - Timeline calculations
6. `fetch_treasury_auction_details()` - Enhanced auction data
7. `calculate_crash_risk_score()` - Composite crash risk

### Enhanced AI Prompts
- Increase context for each dashboard (4-minute read ~ 800-1000 words)
- More specific, actionable analysis
- Cross-asset correlations
- Professional trader-grade insights

### Data Store Additions
```python
# Coin additions
store.set('market.VXV', price)
store.set('market.APT', price)
store.set('market.ADA', price)
store.set('market.NEAR', price)
store.set('rates.FED_FUNDS', rate)
store.set('crypto.risk_composite', score)

# Frontier additions
store.set('frontier.current_day', 12)
store.set('frontier.milestones', {...})

# Map additions
store.set('market.GOLD_change_pct', ...)
store.set('market.SP500_change_pct', ...)
store.set('intelligence.verdict', 'DE-RISK')

# Shield additions
store.set('shield.crash_risk_score', 10.7)
store.set('shield.stress_indicators', [...])
```

---

## 7. Frontend Updates

### Each Dashboard Needs
- Enhanced data display components
- Visual risk indicators
- Timeline visualizations (Frontier)
- Stress gauge (Shield)
- Market pulse animation (Map)
- Crypto risk matrix (Coin)

---

## 8. Daily Loop Testing

After implementation:
1. Run `python tools/fetchers/unified_fetcher_v3.py --all`
2. Verify all JSON outputs updated
3. Check each dashboard displays correctly
4. Verify Commander synthesis includes new data
5. Confirm ~8 minute read time per dashboard

---

## Timeline
- Phase 1: Backend data fetching (2-3 hours)
- Phase 2: Dashboard builders update (1-2 hours)
- Phase 3: Frontend integration (2-3 hours)
- Phase 4: AI prompt enhancement (1 hour)
- Phase 5: Testing & refinement (1-2 hours)

**Total Estimate**: 7-11 hours of focused work

---

## Success Criteria
✅ All 4 dashboards display new data correctly
✅ ~8 minute read time per dashboard  
✅ Daily loop runs without errors
✅ Commander aggregates all new insights
✅ Professional-grade analysis quality
✅ No data fetching errors
✅ Mobile responsive
✅ PWA functionality maintained
