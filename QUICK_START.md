# Quick Start Guide - Daily Alpha Loop V2

## 🚀 5-Minute Setup

### Prerequisites
- Python 3.8+
- OpenRouter API key (for AI analysis)

### Step 1: Install Dependencies (1 min)
```bash
cd c:\Users\Administrator\Downloads\daily-alpha-loop\tools
pip install requests yfinance feedparser pandas numpy
```

### Step 2: Set API Key (30 sec)
```bash
# Windows PowerShell
$env:OPENROUTER_API_KEY="your_key_here"

# Or set permanently in Windows Environment Variables
```

### Step 3: Run the Fetcher (2 min)
```bash
cd c:\Users\Administrator\Downloads\daily-alpha-loop
python tools/fetchers/unified_fetcher_v2.py
```

**You'll see**:
```
====================================
🚀 DAILY ALPHA LOOP - UNIFIED FETCHER V2
📅 2025-12-05 09:58:10 UTC
====================================

STEP 1: CENTRALIZED DATA FETCHING
====================================
📈 FETCHING MARKET DATA (ONCE for all dashboards)
  Fetching BTC (BTC-USD)...
  Fetching ETH (ETH-USD)...
  ...
📦 Stored: market.BTC
📦 Stored: market.ETH
...

STEP 2: DASHBOARD ANALYSES (WATERFALL)
====================================

📊 Wave 1: Risk + Macro
🛡️ ANALYZING: THE SHIELD
  🤖 Calling llama-70b...
  ✅ Success!
🗺️ ANALYZING: THE MAP
  🤖 Calling qwen-235b...
  ✅ Success!

📊 Wave 2: Crypto + Frontier
...

📊 GENERATION COMPLETE
====================================
✅ The Shield: Market Fragility Monitor
✅ The Coin: Crypto Momentum Scanner
✅ The Map: Macro & TASI Trendsetter
✅ The Frontier: Silicon Frontier Watch
✅ The Strategy: Unified Opportunity Radar
✅ The Library: Alpha-Clarity Archive
✅ The Commander: Master Orchestrator - Morning Brief

🎉 DAILY ALPHA LOOP - COMPLETE
```

### Step 4: View The Commander (1 min)
1. Navigate to: `c:\Users\Administrator\Downloads\daily-alpha-loop\apps\the-commander`
2. Open `index.html` in your browser
3. See the Morning Brief! ☕

---

## 📁 What Gets Created

After running, you'll have:

```
data/
├── the-shield/latest.json        ✅ Risk analysis
├── the-coin/latest.json          ✅ Crypto momentum
├── the-map/latest.json           ✅ Macro & TASI trends
├── the-frontier/latest.json      ✅ AI breakthroughs
├── the-strategy/latest.json      ✅ Unified stance
├── the-library/latest.json       ✅ Knowledge summaries
└── the-commander/latest.json     ⭐ MORNING BRIEF
```

---

## 🔍 Quick Checks

### Check if it worked:
```bash
# See all generated files
dir data\the-*\latest.json

# View The Commander's Morning Brief
type data\the-commander\latest.json
```

### Verify AI worked:
Look for `"ai_analysis"` fields in the JSON files - they should have actual content, not "AI analysis unavailable".

---

## 🎯 The Morning Brief

Open `data/the-commander/latest.json` and you'll see:

```json
{
  "morning_brief": {
    "weather_of_the_day": "Volatile",
    "top_signal": "Tech stocks surge 3%",
    "why_it_matters": "Major capital rotation into growth...",
    "cross_dashboard_convergence": "Risk is LOW, Crypto BULLISH, Macro positive...",
    "action_stance": "Accumulate",
    "optional_deep_insight": "While short-term volatility persists...",
    "clarity_level": "High",
    "summary_sentence": "Risk shows the environment, crypto shows sentiment..."
  }
}
```

---

## 📊 View in Browser

To see the beautiful Morning Brief display:

1. Open in browser: `apps/the-commander/index.html`
2. You'll see:
   - ☕ Morning Brief title
   - 🌤️ Weather badge (with emoji)
   - 📡 Top Signal (highlighted)
   - 💡 Why It Matters
   - 🔄 Cross-Dashboard Convergence
   - 🎯 Action Stance (green, bold)
   - 🧠 Deep Insight (optional)
   - 🔮 Clarity Level (color-coded: green/orange/red)
   - Summary sentence

---

## ⚠️ Troubleshooting

### "AI analysis unavailable" in JSON?
- **Cause**: Missing or invalid OpenRouter API key
- **Fix**: Set `OPENROUTER_API_KEY` environment variable

### No JSON files created?
- **Cause**: Python dependencies missing
- **Fix**: Run `pip install -r tools/requirements.txt`

### Rate limit errors?
- **Cause**: Too many requests to free tier API
- **Fix**: The waterfall pattern should prevent this, but you can increase the `time.sleep()` values if needed

---

## 🔄 Automate It

### Windows Task Scheduler
```powershell
# Create a daily task at 4 AM
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\Administrator\Downloads\daily-alpha-loop\tools\fetchers\unified_fetcher_v2.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 4am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "DailyAlphaLoop"
```

### Or use GitHub Actions (already set up)
Just push your code to GitHub and it will run automatically at 4 AM UTC.

---

## 📚 Documentation

- **`ARCHITECTURE_V2.md`**: Full system architecture
- **`REFACTORING_SUMMARY.md`**: What changed and why
- **`tools/system_diagram.py`**: Visual system diagram
- **`README.md`**: Original project README

---

## 🎯 Next Steps

1. ✅ Test the fetcher locally
2. ✅ View The Commander in browser
3. ✅ Push to GitHub
4. ✅ Set GitHub Secrets (`OPENROUTER_API_KEY`)
5. ✅ Watch it run automatically daily

---

## 💡 Tips

- **Each dashboard is independent**: Update one without breaking others
- **The Commander ties everything together**: It's the "summary of summaries"
- **No duplicate API calls**: BTC fetched once, used by 3 dashboards
- **AI everywhere**: Every dashboard gets AI insights
- **Free-tier safe**: Waterfall pattern respects rate limits

---

## 🚨 Important

- Use `unified_fetcher_v2.py` (NEW) not `unified_fetcher.py` (OLD)
- The Commander reads ALL 6 dashboard JSONs
- Each dashboard has its own AI model for specialization

---

**You're all set!** 🎉

Run the fetcher, view The Commander, and enjoy your daily intelligence briefing.

Built for clarity. 💪
