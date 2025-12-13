# Daily Alpha Loop

**Powered by [TOON](docs/TOON_INTEGRATION.md) for 40% Token Savings**

Daily Alpha Loop is an automated market intelligence system that aggregates data from 7 distinct dashboards.

🚀 **[Launch Dashboard](https://kaledh4.github.io/daily-alpha-loop/)**

## 🎯 The Seven Dashboards

| Dashboard | Mission | Focus | Link |
|-----------|---------|-------|------|
| **The Commander** | Master Orchestrator | Generate daily "Morning Brief" | [🔗 Launch](https://kaledh4.github.io/daily-alpha-loop/) |
| **The Shield** | Market Fragility Monitor | Detect systemic stress before crashes | [🔗 Launch](https://kaledh4.github.io/daily-alpha-loop/the-shield/) |
| **The Coin** | Crypto Momentum Scanner | Track BTC/ETH momentum shifts | [🔗 Launch](https://kaledh4.github.io/daily-alpha-loop/the-coin/) |
| **The Map** | Macro & TASI Trendsetter | Align global macro with Saudi markets | [🔗 Launch](https://kaledh4.github.io/daily-alpha-loop/the-map/) |
| **The Frontier** | Silicon Frontier Watch | Identify AI/tech breakthroughs | [🔗 Launch](https://kaledh4.github.io/daily-alpha-loop/the-frontier/) |
| **The Strategy** | Unified Opportunity Radar | Synthesize cross-dashboard insights | [🔗 Launch](https://kaledh4.github.io/daily-alpha-loop/the-strategy/) |
| **The Library** | Alpha-Clarity Archive | Simplify complex market knowledge | [🔗 Launch](https://kaledh4.github.io/daily-alpha-loop/the-library/) |

## 🚀 Quick Start

### Install dependencies

```bash
cd tools
pip install -r requirements.txt
```

### Run data fetcher

```bash
# Run for all dashboards
python fetchers/unified_fetcher_v3.py --all

# Or run for specific dashboard
python fetchers/unified_fetcher_v3.py --app the-shield
```

## 📦 Architecture

```
daily-alpha-loop/
├── apps/               # 7 dashboard applications
│   ├── the-shield/
│   ├── the-coin/
│   ├── the-map/
│   ├── the-frontier/
│   ├── the-strategy/
│   ├── the-library/
│   └── the-commander/
├── data/              # Generated JSON data
├── tools/             # Unified fetcher script
│   └── fetchers/
│       ├── unified_fetcher_v3.py
│       ├── enhanced_analytics.py
│       ├── free_apis.py
│       └── enhanced_dashboard_analysis.py
├── static/            # Shared icons and assets
└── .github/workflows/ # Daily automation
```

## 🔧 Configuration

Set environment variables:

```bash
export OPENROUTER_API_KEY="your_key"
export NEWS_API_KEY="your_key"
export FRED_API_KEY="your_key"
export EIA_API_KEY="your_key"     # NEW: For Energy Data
export ALPHA_VANTAGE_KEY="your_key"
export GROK_API_KEY="your_key"    # Optional: For Grok (Priority 1)
export GEMINI_API_KEY="your_key"  # Optional: For Gemini (Priority 2)

# Or create a .env file in the root directory
```

## ⏰ Automation

The system runs automatically daily at 4 AM UTC via GitHub Actions (`daily_alpha_loop.yml`).

## 📊 Data Flow

1. **Unified Fetcher runs daily**
2. Fetches data from multiple sources (FRED, EIA, Alpha Vantage, NewsAPI, arXiv)
3. **Cross-Dashboard Synergy**: Calculates global risk multipliers and injects cross-context
4. AI models analyze data (via OpenRouter) with **12-minute brief** depth
5. Generates JSON outputs for each dashboard
6. **The Commander** synthesizes all data into Morning Brief
7. Dashboards update automatically

## 🤖 AI Models

The system uses OpenRouter's free tier models with intelligent fallback:

- **Primary**: `meta-llama/llama-3.3-70b-instruct:free`
- **Fallbacks**: 20+ free models including Mistral, Qwen, Dolphin, and more
- **Unified AI Call**: Single comprehensive analysis for all 7 dashboards

## 📱 PWA Support

All dashboards are Progressive Web Apps with:
*   Offline support
*   Install to home screen
*   Custom icons per dashboard
*   Service worker caching

## 🛠️ Tools

*   `generate-icons.py` - Generate PWA icons from static assets
*   `rename-dashboards.ps1` - Batch rename dashboard folders
*   `tools/fetchers/unified_fetcher_v3.py` - Central data fetching
*   `tools/fetchers/bc_processor.py` - Benjamin Cowen Cycle Analysis

## 🌟 Features

*   **Strategic Intelligence System**: Upgraded AI engine with cross-dashboard synergy.
*   **Morning Brief**: **12-minute** deep dive daily intelligence summary.
*   **Flight to Safety Score**: Real-time risk metric with 3-month forecast.
*   **AGI Singularity Tracker**: Monitoring the timeline to AGI escape velocity.
*   **Asset Outlook**: Risk/Reward and Conviction scores for BTC and Gold.
*   **Cross-Dashboard Synthesis**: Unified insights across all data sources.
*   **Free-Tier Optimization**: Efficient API usage with model fallbacks.
*   **Enhanced Metrics**: Percentiles, trends, and color-coded zones.
*   **Regime Detection**: Market regime identification (Calm/Rising Vol/Crisis).
*   **Conflict Matrix**: Visual convergence analysis across dashboards.
*   **Decision Trees**: Actionable IF/THEN logic for trading decisions.
*   **Mobile-First**: Responsive PWA design.

## 📄 License

MIT License - See individual dashboard folders for specific licensing.

---

**Built for clarity, focus, and smarter decision-making.**

