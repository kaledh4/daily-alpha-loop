# 🚀 Quick Setup Guide

This is a quick reference for setting up your Market Intelligence Dashboard!

## Step-by-Step Setup

### 1️⃣ Get Your OpenRouter API Key

1. Visit: https://openrouter.ai/
2. Sign up (free tier available)
3. Go to: https://openrouter.ai/keys
4. Create a new API key
5. Copy it (you'll need it in step 3)

### 2️⃣ Create GitHub Repository

```bash
# If you haven't initialized git yet
git init
git add .
git commit -m "Initial commit: Market Intelligence Dashboard"
git branch -M main

# Create new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/MARKET_K.git
git push -u origin main
```

### 3️⃣ Add API Key to GitHub Secrets

1. Go to your repo: `https://github.com/YOUR_USERNAME/MARKET_K`
2. Click: **Settings** → **Secrets and variables** → **Actions**
3. Click: **New repository secret**
4. Name: `OPENROUTER_API_KEY`
5. Value: Paste your OpenRouter API key
6. Click: **Add secret**

### 4️⃣ Enable GitHub Pages

1. In repo settings, click: **Pages** (left sidebar)
2. Under **Source**, select: **GitHub Actions**
3. Click: **Save**

### 5️⃣ Run the Workflow

**Option A: Automatic (wait for scheduled run)**
- Workflow runs daily at 6 AM UTC automatically

**Option B: Manual (get started now)**
1. Go to: **Actions** tab
2. Click: **Daily AI Updates & Deploy to GitHub Pages**
3. Click: **Run workflow** (green button)
4. Click: **Run workflow** again to confirm

### 6️⃣ Access Your Dashboard

After workflow completes (2-3 minutes):
- Your site will be live at: `https://YOUR_USERNAME.github.io/MARKET_K/`

## 🔧 Quick Commands

### Test Locally
```bash
# Simple HTTP server
python -m http.server 8000
# OR
npx serve
```

Then visit: `http://localhost:8000`

### Update Repository
```bash
git add .
git commit -m "Update dashboard"
git push
```

## ✅ Verification Checklist

- [ ] OpenRouter account created with API key
- [ ] GitHub repository created and pushed
- [ ] `OPENROUTER_API_KEY` added to GitHub Secrets
- [ ] GitHub Pages enabled (source: GitHub Actions)
- [ ] First workflow run completed successfully
- [ ] Site accessible at GitHub Pages URL
- [ ] PWA install prompt appears on site

## 🎯 What to Expect

After setup, your dashboard will:
- ✅ Update automatically every 24 hours
- ✅ Generate fresh AI insights using Grok
- ✅ Work offline after first visit (PWA)
- ✅ Be installable on mobile and desktop
- ✅ Load instantly with caching

## 🆘 Common Issues

### Issue: Workflow fails
**Solution**: Check that `OPENROUTER_API_KEY` secret is set correctly

### Issue: Site not accessible
**Solution**: Wait 2-3 minutes after first workflow run, then check Settings → Pages for the URL

### Issue: PWA not installing
**Solution**: Visit via HTTPS (GitHub Pages URL), not localhost

### Issue: No daily updates
**Solution**: Verify GitHub Actions is enabled in Settings → Actions

## 📞 Need Help?

- Read full docs: `README.md`
- Check workflow logs: **Actions** tab on GitHub
- Verify configuration: Check all files are committed

## 🎨 Quick Customizations

### Change Update Time
Edit `.github/workflows/deploy.yml`:
```yaml
schedule:
  - cron: '0 18 * * *'  # 6 PM UTC instead
```

### Change App Name
Edit `manifest.json`:
```json
{
  "name": "Your Custom Name",
  "short_name": "Custom"
}
```

### Change Colors
Edit `styles.css`:
```css
:root {
    --color-accent-primary: #ff0000;  /* Your color */
}
```

---

**That's it! You're all set! 🎉**

Your AI-powered dashboard is now live and will update daily automatically.
