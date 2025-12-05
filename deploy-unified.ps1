#!/usr/bin/env pwsh
# Deploy Unified Dashboard System

Write-Host "🔄 Deploying Unified Dashboard System..." -ForegroundColor Cyan

$dashboards = @(
    "the-commander",
    "the-shield",
    "the-coin",
    "the-map",
    "the-frontier",
    "the-strategy",
    "the-library"
)

# Copy shared files to each dashboard for deployment
foreach ($dash in $dashboards) {
    $appPath = "apps/$dash"
    
    Write-Host "  📦 Processing $dash..." -ForegroundColor Yellow
    
    # Replace index.html
    if (Test-Path "$appPath/index-unified.html") {
        Copy-Item "$appPath/index-unified.html" "$appPath/index.html" -Force
        Write-Host "    ✅ Replaced index.html" -ForegroundColor Green
    }
    
    # Replace app.js
    if (Test-Path "$appPath/app-unified.js") {
        Copy-Item "$appPath/app-unified.js" "$appPath/app.js" -Force
        Write-Host "    ✅ Replaced app.js" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "All dashboards now use:" -ForegroundColor Cyan
Write-Host "  - shared/styles.css (unified design)" -ForegroundColor White
Write-Host "  - shared/navigation.js (cross-dashboard links)" -ForegroundColor White
Write-Host "  - Source attribution badges" -ForegroundColor White
