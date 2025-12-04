# 📊 Dashboard Monorepo

A high-performance Nx monorepo containing 6 independent dashboard applications with shared libraries for API key management, PWA functionality, and data fetching.

## 🏗️ Architecture

### Applications (`apps/`)

| App Name | Description | Port | Deployment URL |
|----------|-------------|------|----------------|
| **ai-race** | AI Race Tracker - Track global AI development race | 4200 | `/ai-race` |
| **crash-detector** | Market Crash Detector - Real-time market crash detection | 4201 | `/crash-detector` |
| **dashboard-orchestrator** | Dashboard Orchestrator Pro - Unified dashboard platform | 4202 | `/dashboard-orchestrator` |
| **economic-compass** | Economic Compass - Global economic indicators | 4203 | `/economic-compass` |
| **intelligence-platform** | Intelligence Platform - Market intelligence and analysis | 4204 | `/intelligence-platform` |
| **hyper-analytical** | Hyper Analytical Dashboard - Advanced market analytics | 4205 | `/hyper-analytical` |

### Shared Libraries (`libs/`)

| Library | Purpose | Dependencies |
|---------|---------|--------------|
| **shared-keys** | Centralized API key management | None |
| **shared-pwa** | PWA service worker and manifest templates | None |
| **data-layer** | Common data-fetching utilities | shared-keys |

## 🚀 Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm (v9 or higher)
- Git

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd nx-monorepo

# Install dependencies
npm install
```

### API Keys Configuration

This monorepo uses **GitHub Secrets** for API key management. All keys are configured in your repository settings and automatically injected during GitHub Actions builds.

**For Production (GitHub Actions):**
- See [SECRETS_SETUP.md](./SECRETS_SETUP.md) for detailed instructions on configuring GitHub Secrets

**For Local Development:**
- Set environment variables manually before running commands
- See [SECRETS_SETUP.md](./SECRETS_SETUP.md) for local development options

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

# Or use Nx directly
nx serve ai-race
```

### Building Applications

```bash
# Build all apps
npm run build

# Build a specific app
npm run build:ai-race
npm run build:crash-detector
# ... etc

# Or use Nx directly
nx build ai-race
```

### Deploying Applications

Each application can be deployed independently to GitHub Pages or other hosting platforms:

```bash
# Deploy all apps
npm run deploy:all

# Deploy specific app (requires configuration)
nx deploy ai-race
```

## 🔍 Dependency Graph

Visualize the dependency graph of all projects:

```bash
npm run graph
```

This will open an interactive dependency graph showing how all apps and libraries are connected.

## 📚 Shared Libraries Usage

### Using `shared-keys`

```javascript
import { getApiKey, hasApiKey } from '@monorepo/shared-keys';

// Get an API key
const newsApiKey = getApiKey('NEWS_API_KEY');

// Check if a key is configured
if (hasApiKey('ALPHA_VANTAGE_KEY')) {
  // Use the key
}
```

### Using `shared-pwa`

```javascript
import { registerServiceWorker, generateManifest } from '@monorepo/shared-pwa';

// Register service worker
registerServiceWorker('/sw.js');

// Generate manifest for your app
const manifest = generateManifest({
  name: 'My Dashboard',
  shortName: 'Dashboard',
  themeColor: '#1a1a1a'
});
```

### Using `data-layer`

```javascript
import { fetchNews, fetchStockData, fetchCryptoData } from '@monorepo/data-layer';

// Fetch news
const news = await fetchNews({ query: 'finance', pageSize: 10 });

// Fetch stock data
const stockData = await fetchStockData('AAPL');

// Fetch crypto data
const btcData = await fetchCryptoData('bitcoin');
```

## 🔧 Nx Commands

```bash
# Run affected tests
nx affected:test

# Run affected builds
nx affected:build

# Lint all projects
nx run-many --target=lint --all

# Format all files
nx format:write

# Clear Nx cache
nx reset
```

## 📁 Project Structure

```
nx-monorepo/
├── apps/
│   ├── ai-race/
│   ├── crash-detector/
│   ├── dashboard-orchestrator/
│   ├── economic-compass/
│   ├── intelligence-platform/
│   └── hyper-analytical/
├── libs/
│   ├── shared-keys/
│   ├── shared-pwa/
│   └── data-layer/
├── dist/                    # Build outputs
├── node_modules/
├── .env                     # Environment variables (not in git)
├── .env.example            # Environment variables template
├── nx.json                 # Nx configuration
├── package.json            # Root package.json
└── README.md              # This file
```

## 🌐 Deployment

### GitHub Pages Deployment

Each app can be deployed to GitHub Pages with separate repositories or as subdirectories:

1. **Separate Repositories** (Recommended for independent URLs):
   ```bash
   # Configure each app's deploy target in project.json
   # Then deploy
   nx deploy ai-race
   ```

2. **Monorepo Deployment** (All apps in one repo):
   ```bash
   # Build all apps
   npm run build
   
   # Deploy to GitHub Pages (configure gh-pages branch)
   npm run deploy:all
   ```

### Scheduled Builds

Configure GitHub Actions to run builds on a schedule (1 AM - 6 AM):

```yaml
# .github/workflows/scheduled-build.yml
name: Scheduled Build
on:
  schedule:
    - cron: '0 1-6 * * *'  # Run every hour from 1 AM to 6 AM UTC
```

## 🔐 Security

- Never commit `.env` files
- Use GitHub Secrets for CI/CD API keys
- Rotate API keys regularly
- Review dependency vulnerabilities: `npm audit`

## 📊 Monitoring

Each dashboard includes:
- PWA offline support
- Service worker caching
- Performance monitoring
- Error tracking

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests: `nx affected:test`
4. Build: `nx affected:build`
5. Submit a pull request

## 📝 License

MIT

## 🆘 Support

For issues and questions:
- Check the [Nx documentation](https://nx.dev)
- Review individual app READMEs in `apps/*/README.md`
- Open an issue in this repository

---

**Built with ❤️ using Nx**
