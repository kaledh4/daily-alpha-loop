# Daily Alpha Loop - Architecture V2

## 🎯 Philosophy: Simplicity, No Duplication, AI Power

### Core Principle
**Fetch Once, Use Everywhere, AI Analyzes Everything**

---

## 📐 System Architecture

### The Old Way ❌
- Each dashboard fetched its own data
- BTC price fetched 3 times
- SP500 fetched 2 times
- Duplicate API calls = wasted credits
- Complex data flow

### The New Way ✅
- **ONE** unified fetcher runs daily
- All data fetched ONCE and stored centrally
- AI analyzes each dashboard's data domain
- The Commander synthesizes everything into Morning Brief
- Zero duplicate API calls

---

## 🏗️ Component Structure

```
┌─────────────────────────────────────────────────────┐
│                UNIFIED FETCHER V2                   │
│         (tools/fetchers/unified_fetcher_v2.py)       │
└─────────────────────────┬───────────────────────────┘
                          │
                          │ Fetches ONCE:
                          │ - Market data (BTC, ETH, SP500, DXY, etc.)
                          │ - Crypto indicators (RSI, MA, etc.)
                          │ - Treasury auctions
                          │ - Fear & Greed Index
                          │ - News (RSS)
                          │ - arXiv papers
                          │
                          ↓
┌─────────────────────────────────────────────────────┐
│            CENTRALIZED DATA STORE                   │
│         (In-memory + cached to disk)                │
└───────┬─────┬─────┬─────┬─────┬─────┬─────┬────────┘
        │     │     │     │     │     │     │
        ↓     ↓     ↓     ↓     ↓     ↓     ↓
    ┌─────┐ ┌───┐ ┌─────┐ ┌───────┐ ┌────────┐ ┌────────┐
    │Shield│ │Coin│ │ Map │ │Frontier│ │Strategy│ │Library │
    └─────┘ └───┘ └─────┘ └───────┘ └────────┘ └────────┘
       │      │       │        │          │         │
       │  AI Analyzes each dashboard domain        │
       ↓      ↓       ↓        ↓          ↓         ↓
    JSON   JSON    JSON     JSON      JSON      JSON
       │      │       │        │          │         │
       └──────┴───────┴────────┴──────────┴─────────┘
                          │
                          ↓
              ┌────────────────────────┐
              │   THE COMMANDER        │
              │  (Morning Brief AI)    │
              └────────────────────────┘
                Reads ALL 6 JSONs
                Generates 30-sec brief
```

---

## 📊 The Seven Dashboards

### 1. **The Shield** 🛡️
- **Mission**: Market Fragility Monitor
- **Data Used**: JPY, CNH, TNX, MOVE, VIX, CBON, Treasury Auctions
- **AI Task**: Analyze systemic stress signals
- **Output**: `data/the-shield/latest.json`

### 2. **The Coin** 🪙
- **Mission**: Crypto Momentum Scanner
- **Data Used**: BTC, ETH (with RSI, MA), Fear & Greed
- **AI Task**: Identify momentum shifts (Bullish/Bearish/Neutral)
- **Output**: `data/the-coin/latest.json`

### 3. **The Map** 🗺️
- **Mission**: Macro & TASI Trendsetter
- **Data Used**: Oil, DXY, Gold, SP500, TASI, 10Y Yield
- **AI Task**: Predict TASI mood based on macro trends
- **Output**: `data/the-map/latest.json`

### 4. **The Frontier** 🚀
- **Mission**: Silicon Frontier Watch
- **Data Used**: arXiv papers (AI, Quantum, Biotech, etc.)
- **AI Task**: Identify real breakthroughs (not hype)
- **Output**: `data/the-frontier/latest.json`

### 5. **The Strategy** 🎯
- **Mission**: Unified Opportunity Radar
- **Data Used**: Reads ALL other dashboards
- **AI Task**: Synthesize cross-dashboard insights into one stance
- **Output**: `data/the-strategy/latest.json`

### 6. **The Library** 📚
- **Mission**: Alpha-Clarity Archive
- **Data Used**: News articles
- **AI Task**: Simplify complex articles (ELI5)
- **Output**: `data/the-library/latest.json`

### 7. **The Commander** ⭐
- **Mission**: Master Orchestrator - Morning Brief
- **Data Used**: Reads ALL 6 dashboards
- **AI Task**: Generate 30-second coffee read
- **Output**: `data/the-commander/latest.json`

---

## 🌊 Waterfall Loading (Free-Tier Safe)

To avoid hitting API rate limits, we use a **waterfall pattern**:

```python
# Wave 1: Risk + Macro (2 seconds pause)
analyze_the_shield()
analyze_the_map()
time.sleep(2)

# Wave 2: Crypto + Frontier (2 seconds pause)
analyze_the_coin()
analyze_the_frontier()
time.sleep(2)

# Wave 3: Library (2 seconds pause)
analyze_the_library()
time.sleep(2)

# Wave 4: Strategy (2 seconds pause)
analyze_the_strategy()
time.sleep(2)

# Wave 5: The Commander (Final)
analyze_the_commander()
```

**Total Time**: ~12 seconds (controlled, safe for free tier)

---

## 🤖 AI Model Assignment

Each dashboard uses specialized models with fallback:

| Dashboard | Primary Model | Fallback |
|-----------|---------------|----------|
| **The Shield** | llama-70b | olmo-32b |
| **The Coin** | mistral-24b | dolphin-24b |
| **The Map** | qwen-235b | glm-4 |
| **The Frontier** | tongyi-30b | nemotron-12b |
| **The Strategy** | chimera | kimi |
| **The Library** | longcat | gemma-2b |
| **The Commander** | llama-70b | olmo-32b |

---

## 📝 Morning Brief Structure

The Commander generates a **30-Second Coffee Read** with these exact fields:

```json
{
  "weather_of_the_day": "Stormy / Cloudy / Sunny / Volatile / Foggy",
  "top_signal": "The single most important data point today",
  "why_it_matters": "2 sentences",
  "cross_dashboard_convergence": "How risk + crypto + macro + breakthroughs connect",
  "action_stance": "Sit tight / Accumulate / Cautious / Aggressive / Review markets",
  "optional_deep_insight": "One optional paragraph for advanced users",
  "clarity_level": "High / Medium / Low",
  "summary_sentence": "Risk shows the environment, crypto shows sentiment, macro shows the wind, breakthroughs show the future, strategy shows the stance, and knowledge shows the long-term signal — combine all six to guide the user clearly through today."
}
```

---

## 🚀 Running the System

### 1. Install Dependencies
```bash
cd tools
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export OPENROUTER_API_KEY="your_key"
export NEWS_API_KEY="your_key"      # Optional
export FRED_API_KEY="your_key"      # Optional
export ALPHA_VANTAGE_KEY="your_key" # Optional
```

### 3. Run Unified Fetcher V2
```bash
python tools/fetchers/unified_fetcher_v2.py
```

**Output**: 
- `data/the-shield/latest.json`
- `data/the-coin/latest.json`
- `data/the-map/latest.json`
- `data/the-frontier/latest.json`
- `data/the-strategy/latest.json`
- `data/the-library/latest.json`
- `data/the-commander/latest.json`

### 4. View The Commander
Open `apps/the-commander/index.html` in your browser to see the Morning Brief.

---

## 📁 File Structure

```
daily-alpha-loop/
├── tools/
│   └── fetchers/
│       ├── unified_fetcher.py          # Old version
│       └── unified_fetcher_v2.py       # 🆕 New version
├── data/
│   ├── cache/                          # Market data cache
│   ├── the-shield/
│   │   └── latest.json
│   ├── the-coin/
│   │   └── latest.json
│   ├── the-map/
│   │   └── latest.json
│   ├── the-frontier/
│   │   └── latest.json
│   ├── the-strategy/
│   │   └── latest.json
│   ├── the-library/
│   │   └── latest.json
│   └── the-commander/
│       └── latest.json                 # 🎯 Morning Brief
├── apps/
│   ├── the-shield/
│   ├── the-coin/
│   ├── the-map/
│   ├── the-frontier/
│   ├── the-strategy/
│   ├── the-library/
│   └── the-commander/                  # 🏛️ Master Dashboard
│       ├── index.html
│       ├── app.js                      # Updated
│       └── styles.css
└── .github/
    └── workflows/
        └── daily_alpha_loop.yml        # Daily automation
```

---

## ⏰ Automation (GitHub Actions)

The workflow runs daily at **4 AM UTC**:

```yaml
on:
  schedule:
    - cron: '0 4 * * *'  # Daily at 4 AM UTC
  workflow_dispatch:      # Manual trigger
```

**Steps**:
1. Checkout code
2. Install Python dependencies
3. Run `unified_fetcher_v2.py`
4. Commit generated JSON files
5. Deploy to GitHub Pages

---

## 🎨 Frontend Display

Each dashboard HTML file reads its corresponding JSON:
- `the-shield` → reads `data/the-shield/latest.json`
- `the-coin` → reads `data/the-coin/latest.json`
- etc.

**The Commander** displays the full Morning Brief with:
- Weather badge (with emoji)
- Top Signal (highlighted)
- Why It Matters
- Cross-Dashboard Convergence
- Action Stance (bold)
- Deep Insight (optional, collapsible)
- Clarity Level (color-coded)
- Summary sentence

---

## 🔑 Key Benefits

1. **Zero Duplication**: Each API endpoint called exactly once
2. **AI Everywhere**: Every dashboard gets AI-analyzed insights
3. **Modular**: Update one dashboard without affecting others
4. **Scalable**: Easy to add new dashboards
5. **Free-Tier Safe**: Waterfall pattern respects rate limits
6. **Rich Output**: Full JSON for each dashboard (not just summaries)
7. **Morning Brief**: One place to see everything
8. **Offline Ready**: All data pre-generated, no client-side API calls

---

## 📌 Summary-of-the-Summary

> **"Risk shows the environment, crypto shows sentiment, macro shows the wind, breakthroughs show the future, strategy shows the stance, and knowledge shows the long-term signal — combine all six to guide the user clearly through today."**

This one sentence is the philosophical core of the entire system.

---

## 🛠️ Development Notes

### Adding a New Dashboard

1. Add fetch function in `unified_fetcher_v2.py`:
   ```python
   def analyze_new_dashboard() -> Dict:
       # Your logic here
       return {
           'dashboard': 'new-dashboard',
           'name': 'New Dashboard',
           'mission': 'Your mission',
           'ai_analysis': 'AI insights'
       }
   ```

2. Add to waterfall in `main()`:
   ```python
   new_dash = analyze_new_dashboard()
   (DATA_DIR / 'new-dashboard').mkdir(parents=True, exist_ok=True)
   (DATA_DIR / 'new-dashboard' / 'latest.json').write_text(json.dumps(new_dash, indent=2))
   ```

3. Create frontend in `apps/new-dashboard/`

4. Update The Commander to read the new JSON

---

**Built for clarity, focus, and smarter decision-making.** 🚀
