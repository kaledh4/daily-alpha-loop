# 📊 Dashboard Monorepo

A high-performance Nx monorepo containing **7 independent dashboard applications** with shared libraries for API key management, PWA functionality, unified data fetching, and AI integration.

> 🔗 **Live Dashboards:** [https://kaledh4.github.io/monorepo/](https://kaledh4.github.io/monorepo/)

## 🏗️ Architecture

### Applications (`apps/`)

| App | Description | Live Link |
|-----|-------------|-----------|
| 🤖 **[AI Race](https://kaledh4.github.io/monorepo/ai-race/)** | Track global AI development & research breakthroughs via arXiv | [Open →](https://kaledh4.github.io/monorepo/ai-race/) |
| 💥 **[Crash Detector](https://kaledh4.github.io/monorepo/crash-detector/)** | Real-time market crash detection & risk analysis | [Open →](https://kaledh4.github.io/monorepo/crash-detector/) |
| 🎛️ **[Dashboard Hub](https://kaledh4.github.io/monorepo/dashboard-orchestrator/)** | Unified dashboard platform - central hub for all apps | [Open →](https://kaledh4.github.io/monorepo/dashboard-orchestrator/) |
| 🧭 **[Economic Compass](https://kaledh4.github.io/monorepo/economic-compass/)** | Global economic indicators & macro analysis | [Open →](https://kaledh4.github.io/monorepo/economic-compass/) |
| 🧠 **[Intelligence Platform](https://kaledh4.github.io/monorepo/intelligence-platform/)** | Market intelligence and AI-powered analysis | [Open →](https://kaledh4.github.io/monorepo/intelligence-platform/) |
| 📈 **[Hyper Analytical](https://kaledh4.github.io/monorepo/hyper-analytical/)** | Advanced crypto market analytics & risk metrics | [Open →](https://kaledh4.github.io/monorepo/hyper-analytical/) |
| 📚 **[Free Knowledge](https://kaledh4.github.io/monorepo/free-knowledge/)** | Open research and knowledge aggregator | [Open →](https://kaledh4.github.io/monorepo/free-knowledge/) |

### Shared Libraries (`libs/`)

| Library | Purpose | Usage |
|---------|---------|-------|
| 🔑 **[shared-keys](./libs/shared-keys/)** | Centralized API key management | `import { getApiKey } from '@monorepo/shared-keys'` |
| 📱 **[shared-pwa](./libs/shared-pwa/)** | PWA service worker and manifest templates | `import { registerServiceWorker } from '@monorepo/shared-pwa'` |
| 🔄 **[unified-api](./libs/unified-api/)** | **Centralized data fetching, caching & AI** | `import { fetchNews, callAI } from '@monorepo/unified-api'` |
| 📊 **[data-layer](./libs/data-layer/)** | Legacy data utilities (re-exports unified-api) | Backward compatible |

### Unified Data System (`tools/fetchers/`)

| Tool | Purpose | Usage |
|------|---------|-------|
| 🐍 **[unified_fetcher.py](./tools/fetchers/unified_fetcher.py)** | Single Python script that fetches data for ALL 7 apps | `python unified_fetcher.py --all` |

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BUILD & DEPLOY FLOW                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   GitHub Actions Trigger                                                 │
│            │                                                             │
│            ▼                                                             │
│   ┌─────────────────┐                                                    │
│   │  FETCH-DATA JOB │  ← Runs ONCE for all apps                         │
│   │  unified_fetcher│                                                    │
│   │     --all       │                                                    │
│   └────────┬────────┘                                                    │
│            │                                                             │
│            ▼                                                             │
│   ┌─────────────────┐                                                    │
│   │  Upload Artifact│  data/ folder shared                              │
│   │  (fetched-data) │                                                    │
│   └────────┬────────┘                                                    │
│            │                                                             │
│            ▼                                                             │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    BUILD JOBS (Parallel)                         │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │   │
│   │  │ ai-race  │ │ crash-   │ │ economic │ │ hyper-   │  ...       │   │
│   │  │          │ │ detector │ │ compass  │ │analytical│            │   │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│            │                                                             │
│            ▼                                                             │
│   ┌─────────────────┐                                                    │
│   │  DEPLOY TO      │                                                    │
│   │  GITHUB PAGES   │  → kaledh4.github.io/monorepo/                    │
│   └─────────────────┘                                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm (v9 or higher)
- Python 3.11+ (for data fetching)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/kaledh4/monorepo.git
cd monorepo

# Install dependencies
npm install

# Install Python dependencies (for data fetching)
pip install requests yfinance feedparser pandas numpy
```

### API Keys Configuration

This monorepo uses **GitHub Secrets** for API key management. All keys are configured in your repository settings and automatically injected during GitHub Actions builds.

**Required Secrets:**
| Secret | Purpose |
|--------|---------|
| `OPENROUTER_KEY` | AI/LLM analysis via OpenRouter |
| `NEWS_API_KEY` | News API for headlines |
| `FRED_API_KEY` | Federal Reserve economic data |

**Optional Secrets:**
| Secret | Purpose |
|--------|---------|
| `ALPHA_VANTAGE_KEY` | Stock market data |
| `COINMARKETCAP_KEY` | Crypto market data |
| `COINGECKO_KEY` | Crypto prices |

## 📦 Development

### Running Applications

```bash
# Serve a specific app
npm run serve:ai-race
npm run serve:crash-detector
npm run serve:dashboard-orchestrator
npm run serve:economic-compass
npm run serve:intelligence-platform
npm run serve:hyper-analytical
npm run serve:free-knowledge
```

### Building Applications

```bash
# Build all apps
npm run build

# Build a specific app
npm run build:ai-race
npm run build:crash-detector
# ... etc
```

### Fetching Data Locally

```bash
# Fetch data for all apps
python tools/fetchers/unified_fetcher.py --all

# Fetch for specific app
python tools/fetchers/unified_fetcher.py --app crash-detector

# Dry run (see what would be fetched)
python tools/fetchers/unified_fetcher.py --dry-run
```

## 📚 Using the Unified API

### JavaScript (Frontend)

```javascript
import { 
    fetchNews, 
    fetchCryptoPrices, 
    callAI,
    createAppFetcher 
} from '@monorepo/unified-api';

// Fetch news with caching
const news = await fetchNews({ query: 'crypto market' });

// Fetch crypto prices
const prices = await fetchCryptoPrices(['bitcoin', 'ethereum']);

// Call AI for analysis
const analysis = await callAI(
    'Analyze current market conditions',
    { model: 'grok', systemPrompt: 'You are a market analyst' }
);

// App-specific pre-configured fetcher
const fetcher = createAppFetcher('crash-detector');
const data = await fetcher.fetchAll();
```

### Python (Build Time)

```python
# All data fetching is handled by:
python tools/fetchers/unified_fetcher.py --all

# Outputs to:
# - data/{app-name}/latest.json (for all apps)
# - apps/ai-race/.../mission_data.json
# - apps/hyper-analytical/dashboard_data.json
# - apps/intelligence-platform/market_analysis.json
```

## 📁 Project Structure

```
monorepo/
├── apps/
│   ├── ai-race/              # AI research tracker
│   ├── crash-detector/       # Market crash detection
│   ├── dashboard-orchestrator/ # Central hub
│   ├── economic-compass/     # Macro economics
│   ├── intelligence-platform/ # Market intelligence
│   ├── hyper-analytical/     # Crypto analytics
│   └── free-knowledge/       # Knowledge aggregator
├── libs/
│   ├── shared-keys/          # API key management
│   ├── shared-pwa/           # PWA utilities
│   ├── unified-api/          # ⭐ Centralized fetching & AI
│   └── data-layer/           # Legacy (re-exports unified-api)
├── tools/
│   └── fetchers/
│       └── unified_fetcher.py # ⭐ Python data fetcher for all apps
├── data/                     # Generated data (gitignored)
│   ├── ai-race/
│   ├── crash-detector/
│   └── .../
├── .github/workflows/
│   └── build-deploy.yml      # Unified CI/CD workflow
└── README.md
```

## 🌐 Deployment

### Automatic (GitHub Actions)

Pushes to `master` trigger:
1. **Fetch Data** - `unified_fetcher.py --all` runs once
2. **Build All Apps** - 7 apps build in parallel with shared data
3. **Deploy** - All apps deployed to GitHub Pages

### Manual Trigger

Go to **Actions** → **Build and Deploy All Dashboards** → **Run workflow**

### Scheduled Builds

Runs automatically every hour from **1 AM to 6 AM UTC** to update data.

## 🔐 Security

- ✅ API keys stored in GitHub Secrets
- ✅ No `.env` files committed
- ✅ Data fetched server-side (no exposed keys in frontend)
- ✅ All API calls go through unified_fetcher.py

## 📊 Features

| Feature | Description |
|---------|-------------|
| 📱 PWA | All apps work offline with service workers |
| 🔄 Auto-refresh | Data updates automatically via scheduled builds |
| 🤖 AI Analysis | OpenRouter integration for market insights |
| 📈 Real-time Data | yfinance, CoinGecko, Treasury API, FRED, arXiv |
| 💾 Caching | In-memory + persistent caching at both JS & Python layers |
| 🎨 Modern UI | Glass morphism, animations, dark themes |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test: `npm run build`
5. Push: `git push origin feature/my-feature`
6. Open a Pull Request

## 📝 License

MIT

## 🆘 Support

- 📖 [Nx Documentation](https://nx.dev)
- 📁 Individual app READMEs in `apps/*/README.md`
- 📚 [Unified API Documentation](./libs/unified-api/README.md)
- 🐛 [Open an Issue](https://github.com/kaledh4/monorepo/issues)

---

**Built with ❤️ using Nx, Python, and AI**
