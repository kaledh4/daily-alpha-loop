/**
 * SHARED DASHBOARD CORE
 * Renders the unified theme for all dashboards.
 * Relies on navigation.js for loadDashboardData and renderNavigation.
 */

function renderHeader(data) {
    const header = document.querySelector('.header');
    if (!header) return;

    // Find the dashboard config to get the icon
    // We assume DASHBOARDS is available from navigation.js
    const dashConfig = typeof DASHBOARDS !== 'undefined'
        ? DASHBOARDS.find(d => d.id === (window.DASHBOARD_NAME || data.dashboard))
        : null;

    const iconHtml = dashConfig && dashConfig.icon
        ? `<img src="${dashConfig.icon}" alt="${data.name}" style="width: 48px; height: 48px; vertical-align: middle; margin-right: 10px;">`
        : '';

    header.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            ${iconHtml}
            <h1 style="margin: 0;">${data.name || 'Dashboard'}</h1>
        </div>
        <p style="font-size: 1.4rem; color: #90cdf4; font-weight: 600; margin-bottom: 10px;">${data.role || ''}</p>
        <p style="max-width: 800px; margin: 0 auto; color: #cbd5e0;">${data.mission || ''}</p>
        <div class="timestamp">Updated: ${(() => {
            const ts = data.last_update || data.timestamp;
            if (!ts) return 'Just now';
            try {
                const date = new Date(ts);
                const yyyy = date.getFullYear();
                const mm = String(date.getMonth() + 1).padStart(2, '0');
                const dd = String(date.getDate()).padStart(2, '0');
                const hh = String(date.getHours()).padStart(2, '0');
                const min = String(date.getMinutes()).padStart(2, '0');
                return `${yyyy}-${mm}-${dd} | ${hh}:${min}`;
            } catch (e) {
                return ts;
            }
        })()}</div>
    `;
}

function renderScoring(scoring) {
    if (!scoring) return '';

    const getScale = (key, value) => {
        const k = key.toLowerCase();
        if (k.includes('rate') || k.includes('percent') || k === 'risk_level') return '/ 100';
        if (k === 'confidence' || k === 'uncertainty') return ''; // Usually 0-1
        return '/ 10';
    };

    return `
        <div class="content-card">
            <h2><img src="../static/icons/icons8-metrics-58.png" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> Core Metrics</h2>
            <div class="data-grid">
                ${Object.entries(scoring).map(([key, value]) => `
                    <div class="data-section">
                        <h3>${key.replace(/_/g, ' ').toUpperCase()}</h3>
                        <div class="data-value" style="color: #63b3ed;">
                            ${value} <span style="font-size: 0.8rem; color: #718096;">${getScale(key, value)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderEnhancedMetrics(metrics) {
    if (!metrics || !Array.isArray(metrics)) return '';

    return `
        <div class="content-card" style="margin-top: 20px;">
            <h2><img src="../static/icons/icons8-map-48.png" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> Enhanced Metrics</h2>
            <div class="data-grid">
                ${metrics.map(metric => {
        const percentile = metric.percentile || null;
        const trend = metric.trend || null;
        const colorZone = metric.color_zone || null;

        let trendHtml = '';
        if (trend) {
            const trendColor = trend.direction === '↑' ? '#28a745' : trend.direction === '↓' ? '#dc3545' : '#718096';
            trendHtml = `<span style="color: ${trendColor}; font-size: 1.2rem; margin-left: 8px;">${trend.direction}</span>`;
        }

        let percentileHtml = '';
        if (percentile !== null) {
            percentileHtml = `<div style="font-size: 0.85rem; color: #718096; margin-top: 4px;">${percentile}th percentile</div>`;
        }

        let zoneHtml = '';
        if (colorZone) {
            zoneHtml = `<div style="display: inline-block; padding: 4px 8px; background: ${colorZone.color}20; color: ${colorZone.color}; border-radius: 4px; font-size: 0.85rem; margin-left: 8px;">${colorZone.label}</div>`;
        }

        return `
                        <div class="data-section" style="border-left: 3px solid ${colorZone ? colorZone.color : '#718096'}; padding-left: 12px;">
                            <h3 style="display: flex; align-items: center; justify-content: space-between;">
                                <span>${metric.name}</span>
                                ${trendHtml}
                            </h3>
                            <div class="data-value" style="color: ${colorZone ? colorZone.color : '#63b3ed'};">
                                ${metric.value} ${zoneHtml}
                            </div>
                            ${percentileHtml}
                            ${trend && trend.label ? `<div style="font-size: 0.85rem; color: #718096; margin-top: 4px;">${trend.label}</div>` : ''}
                        </div>
                    `;
    }).join('')}
            </div>
        </div>
    `;
}

function renderDataSources(sources) {
    if (!sources || sources.length === 0) return '';

    return `
        <div class="content-card" style="margin-top: 20px;">
            <h2><img src="../static/icons/icons8-map-48.png" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> Data Sources</h2>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                ${sources.map(source => `
                    <span class="source-badge">${source.split('/').pop()}</span>
                `).join('')}
            </div>
        </div>
    `;
}

function renderFlightToSafety(score) {
    if (!score) return '';
    return `
        <div class="content-card" style="margin-top: 20px;">
            <h2>🛡️ Flight to Safety Score</h2>
            <div class="data-grid">
                <div class="data-section">
                    <h3>Current Score</h3>
                    <div class="data-value" style="color: #fc8181;">${score.current} <span style="font-size: 0.8rem; color: #718096;">/ 10</span></div>
                </div>
                <div class="data-section">
                    <h3>Trend</h3>
                    <div class="data-value" style="font-size: 1.2rem;">${score.trend}</div>
                </div>
                <div class="data-section">
                    <h3>3M Forecast</h3>
                    <div class="data-value" style="color: #63b3ed;">${score['3m_forecast'].score}</div>
                    <div style="font-size: 0.8rem; color: #718096;">Conf: ${(score['3m_forecast'].confidence * 100).toFixed(0)}%</div>
                </div>
            </div>
        </div>
    `;
}

function renderAgiTracker(tracker) {
    if (!tracker) return '';
    return `
        <div class="content-card" style="margin-top: 20px; border-color: #9f7aea;">
            <h2 style="color: #9f7aea;"><img src="../static/icons/AGI-Singularity-Tracker.png" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> AGI Singularity Tracker</h2>
            <div class="data-grid">
                <div class="data-section">
                    <h3>Escape Velocity Prob</h3>
                    <div class="data-value" style="color: #9f7aea;">${(tracker.escape_velocity_probability * 100).toFixed(1)}%</div>
                </div>
                <div class="data-section">
                    <h3>Timeline Estimate</h3>
                    <div class="data-value" style="font-size: 1.2rem;">${tracker.timeline_estimate}</div>
                </div>
            </div>
            <div style="margin-top: 15px;">
                <h3 style="margin-bottom: 8px;">Key Metrics</h3>
                ${Object.entries(tracker.key_metrics).map(([k, v]) => `
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; border-bottom: 1px solid #2d3748; padding-bottom: 2px;">
                        <span style="color: #cbd5e0;">${k.replace(/_/g, ' ')}</span>
                        <span style="color: #63b3ed;">${v}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderAssetOutlook(outlook) {
    if (!outlook) return '';
    return `
        <div class="content-card" style="margin-top: 20px;">
            <h2><img src="../static/icons/Asset_Outlook.png" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> Asset Outlook</h2>
            <div class="data-grid">
                ${Object.entries(outlook).map(([asset, data]) => `
                    <div class="data-section">
                        <h3>${asset.toUpperCase()}</h3>
                        <div class="data-value" style="font-size: 1.2rem;">${data.risk_reward.toUpperCase()}</div>
                        <div style="font-size: 0.9rem; color: #718096; margin-top: 4px;">Conviction: ${data.conviction}</div>
                        <div style="margin-top: 8px; font-size: 0.85rem;">
                            3M Target: <span style="color: #48bb78;">${data.forecasts['3m'].target}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderAIAnalysis(analysis) {
    return `
        <div class="content-card" style="margin-top: 20px; border-color: #48bb78;">
            <h2 style="color: #48bb78; border-color: #48bb78;"><img src="../static/icons/icons8-ai-48.png" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> AI Analysis</h2>
            <div class="data-text" style="font-size: 1.2rem; white-space: pre-line;">
                ${analysis || 'Analysis temporarily unavailable. The system is gathering more data.'}
            </div>
        </div>
    `;
}

function renderMorningBrief(brief) {
    if (!brief) return '';

    const getWeatherIcon = (weather) => {
        const w = weather.toLowerCase();
        // Prioritize specific matches
        if (w.includes('cloud')) return '../static/icons/icons8-cloudy.gif';
        if (w.includes('storm') || w.includes('rain')) return '../static/icons/icons8-stormy-48.png';
        if (w.includes('sun') || w.includes('clear')) return '../static/icons/icons8-sunny-48.png';
        if (w.includes('fog')) return '../static/icons/icons8-foggy-48.png';
        if (w.includes('volat')) return '../static/icons/icons8-volatile-48.png';
        return '../static/icons/icons8-sunny-48.png';
    };

    return `
        <div class="content-card">
            <div class="weather-badge" style="text-align: center; font-size: 1.5rem; display: flex; align-items: center; justify-content: center; gap: 10px;">
                <span>Weather: ${brief.weather_of_the_day}</span>
                <img src="${getWeatherIcon(brief.weather_of_the_day)}" alt="${brief.weather_of_the_day}" style="width: 48px; height: 48px;">
            </div>
            
            <div class="data-grid" style="margin-top: 20px;">
                <div class="data-section">
                    <h3>TOP SIGNAL</h3>
                    <div class="data-value" style="font-size: 1.2rem; text-align: left;">${brief.top_signal}</div>
                </div>
                <div class="data-section">
                    <h3>ACTION STANCE</h3>
                    <div class="stance" style="text-align: center;">${brief.action_stance}</div>
                </div>
            </div>

            <div class="summary-box" style="margin-top: 20px; text-align: left;">
                <h3 style="color: #90cdf4; margin-bottom: 10px;">Why It Matters</h3>
                <p>${brief.why_it_matters}</p>
            </div>

            <div class="data-section" style="margin-top: 20px;">
                <h3>Cross-Dashboard Convergence</h3>
                <p class="data-text">${brief.cross_dashboard_convergence}</p>
            </div>

            <div class="data-section" style="margin-top: 20px;">
                <h3>The Commander's Summary</h3>
                <p class="data-text" style="font-style: italic;">"${brief.summary_sentence}"</p>
            </div>
        </div>
    `;
}

async function initDashboard(dashboardName) {
    const data = await loadDashboardData(dashboardName);

    // Render Navigation (assuming navigation.js is loaded)
    if (window.renderNavigation) {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('mode') !== 'seamless') {
            document.getElementById('nav').innerHTML = window.renderNavigation(dashboardName);
        } else {
            // In seamless mode, hide the nav container to avoid spacing issues
            const navEl = document.getElementById('nav');
            if (navEl) navEl.style.display = 'none';
        }
    }

    if (!data) {
        document.getElementById('content').innerHTML = `
            <div class="content-card">
                <h2>Loading Data...</h2>
                <p>Please wait while we fetch the latest intelligence.</p>
            </div>
        `;
        return;
    }

    renderHeader(data);

    const contentEl = document.getElementById('content');

    if (dashboardName === 'the-commander') {
        let html = renderMorningBrief(data.morning_brief);

        // Add Flight to Safety
        html += renderFlightToSafety(data.flight_to_safety_score);

        // Add Asset Outlook
        html += renderAssetOutlook(data.asset_outlook);

        // Add AGI Tracker
        html += renderAgiTracker(data.agi_singularity_tracker);

        // Add conflict matrix if available
        if (data.conflict_matrix) {
            const matrix = data.conflict_matrix;
            html += `
                <div class="content-card" style="margin-top: 20px;">
                    <h2>📊 Dashboard Convergence</h2>
                    <div class="data-grid">
                        <div class="data-section">
                            <h3>Risk</h3>
                            <div style="color: ${matrix.risk.color}; font-weight: bold;">${matrix.risk.signal} (${matrix.risk.score}/100)</div>
                        </div>
                        <div class="data-section">
                            <h3>Crypto</h3>
                            <div style="color: ${matrix.crypto.color}; font-weight: bold;">${matrix.crypto.signal} (${matrix.crypto.score}/100)</div>
                        </div>
                        <div class="data-section">
                            <h3>Macro</h3>
                            <div style="color: ${matrix.macro.color}; font-weight: bold;">${matrix.macro.signal} (${matrix.macro.score}/100)</div>
                        </div>
                        <div class="data-section">
                            <h3>Tech</h3>
                            <div style="color: ${matrix.tech.color}; font-weight: bold;">${matrix.tech.signal} (${matrix.tech.score}/100)</div>
                        </div>
                    </div>
                    <div style="margin-top: 20px; padding: 15px; background: ${matrix.net_signal.color}20; border-radius: 8px; border-left: 4px solid ${matrix.net_signal.color};">
                        <h3 style="color: ${matrix.net_signal.color}; margin-bottom: 8px;">Net Signal: ${matrix.net_signal.signal}</h3>
                        <div style="color: #718096;">Confidence: ${(matrix.net_signal.confidence * 100).toFixed(0)}%</div>
                    </div>
                </div>
            `;
        }

        // Add decision tree if available
        if (data.decision_tree && data.decision_tree.primary_decision) {
            const decision = data.decision_tree.primary_decision;
            html += `
                <div class="content-card" style="margin-top: 20px; border-color: #48bb78;">
                    <h2 style="color: #48bb78;">🎯 Decision Tree</h2>
                    <div style="padding: 15px; background: #1a202c; border-radius: 8px; margin-top: 10px;">
                        <div style="color: #90cdf4; font-weight: bold; margin-bottom: 8px;">IF ${decision.condition}</div>
                        <div style="color: #48bb78; font-size: 1.2rem; font-weight: bold; margin-bottom: 8px;">→ ${decision.action}</div>
                        <div style="color: #718096; font-size: 0.9rem;">Confidence: ${(decision.confidence * 100).toFixed(0)}%</div>
                        <div style="color: #cbd5e0; margin-top: 8px; font-style: italic;">${decision.reasoning}</div>
                    </div>
                </div>
            `;
        }

        contentEl.innerHTML = html + renderFooter();
    } else if (dashboardName === 'the-shield') {
        contentEl.innerHTML = renderTheShield(data) + renderFooter();
    } else {
        let html = '';

        // 1. Regime detection (for The Shield - Legacy/Fallback)
        if (data.regime) {
            html += `
                <div class="content-card">
                    <h2>🎯 Market Regime</h2>
                    <div style="padding: 15px; background: ${data.regime.color}20; border-radius: 8px; border-left: 4px solid ${data.regime.color};">
                        <div style="color: ${data.regime.color}; font-size: 1.3rem; font-weight: bold;">${data.regime.regime}</div>
                        <div style="color: #718096; margin-top: 4px;">Confidence: ${(data.regime.confidence * 100).toFixed(0)}%</div>
                    </div>
                </div>
            `;
        }

        // 2. Scoring Metrics
        html += renderScoring(data.scoring);

        // 3. Metrics Section
        console.log('[DashboardCore] Checking metrics for:', data.dashboard);
        if (data.metrics && Array.isArray(data.metrics) && data.metrics.length > 0) {
            console.log('[DashboardCore] Metrics found:', data.metrics.length);
            // Check if metrics are enhanced (have percentile)
            const isEnhanced = data.metrics[0].percentile !== undefined;

            if (isEnhanced) {
                console.log('[DashboardCore] Rendering enhanced metrics');
                html += renderEnhancedMetrics(data.metrics);
            } else {
                console.log('[DashboardCore] Rendering basic metrics');
                // Render basic metrics
                html += `
                    <div class="content-card" style="margin-top: 20px;">
                        <h2><img src="../static/icons/icons8-chart-48.png" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> Market Metrics</h2>
                        <div class="data-grid">
                            ${data.metrics.map(m => `
                                <div class="data-section">
                                    <h3>${m.name}</h3>
                                    <div class="data-value" style="color: #63b3ed;">${m.value}</div>
                                    <div style="font-size: 0.85rem; color: #718096; margin-top: 4px;">${m.signal}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
        } else {
            console.warn('[DashboardCore] No metrics found for dashboard:', data.dashboard);
        }

        // 4. AI Analysis
        html += renderAIAnalysis(data.ai_analysis);

        // 5. Data Sources
        html += renderDataSources(data.data_sources);

        contentEl.innerHTML = html + renderFooter();
    }
}

function renderFooter() {
    return `
        <div style="margin-top: 40px; text-align: center; padding-bottom: 20px; border-top: 1px solid #2d3748; padding-top: 20px;">
            <a href="../read_all/index.html" style="color: #718096; text-decoration: none; font-size: 0.9rem;">
                Debug: Read All Data
            </a>
        </div>
    `;
}

function renderTheShield(data) {
    let html = '';

    // 1. Risk Assessment
    if (data.risk_assessment) {
        const ra = data.risk_assessment;
        html += `
            <div class="content-card">
                <h2>🛡️ Risk Assessment</h2>
                <div style="padding: 20px; background: ${ra.color}20; border-radius: 8px; border-left: 5px solid ${ra.color}; text-align: center;">
                    <div style="font-size: 3rem; font-weight: bold; color: ${ra.color};">${ra.score}</div>
                    <div style="font-size: 1.5rem; color: #e2e8f0; margin-top: 5px;">${ra.level}</div>
                </div>
            </div>
        `;
    }

    // 2. Metrics
    if (data.metrics && data.metrics.length > 0) {
        html += `
            <div class="content-card" style="margin-top: 20px;">
                <h2><img src="../static/icons/icons8-chart-48.png" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> Key Metrics</h2>
                <div class="data-grid">
                    ${data.metrics.map(m => `
                        <div class="data-section">
                            <h3>${m.name}</h3>
                            <div class="data-value" style="color: #63b3ed;">${m.value}</div>
                            <div style="font-size: 0.85rem; color: ${m.signal === 'NORMAL' ? '#48bb78' : '#fc8181'}; margin-top: 4px;">${m.signal}</div>
                            <div style="font-size: 0.8rem; color: #718096; margin-top: 2px;">${m.desc}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // 3. AI Insights
    if (data.ai_insights) {
        html += `
            <div class="content-card" style="margin-top: 20px; border-color: #fc8181;">
                <h2 style="color: #fc8181;"><img src="../static/icons/icons8-ai-48.png" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"> AI Risk Analysis</h2>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #cbd5e0; margin-bottom: 10px;">Crash Analysis</h3>
                    <div class="data-text">${data.ai_insights.crash_analysis}</div>
                </div>

                <div>
                    <h3 style="color: #cbd5e0; margin-bottom: 10px;">News Summary</h3>
                    <div class="data-text">${data.ai_insights.news_summary}</div>
                </div>
            </div>
        `;
    }

    // 4. Days Remaining
    if (data.days_remaining !== undefined) {
        html += `
            <div class="content-card" style="margin-top: 20px; text-align: center;">
                <div style="font-size: 1.2rem; color: #718096;">Days Remaining in Year</div>
                <div style="font-size: 2rem; font-weight: bold; color: #e2e8f0;">${data.days_remaining}</div>
            </div>
        `;
    }

    return html;
}

// Register Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            })
            .catch(err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}

// Auto-initialize if dashboard name is provided in global scope
if (window.DASHBOARD_NAME) {
    document.addEventListener('DOMContentLoaded', () => {
        initDashboard(window.DASHBOARD_NAME);
        // Refresh every 5 minutes
        setInterval(() => initDashboard(window.DASHBOARD_NAME), 5 * 60 * 1000);
    });
}

// PWA Install Logic
let deferredPrompt;
const installBtn = document.getElementById('install-app-btn');

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later.
    deferredPrompt = e;
    // Update UI to notify the user they can add to home screen
    if (installBtn) {
        installBtn.style.display = 'block';

        installBtn.addEventListener('click', (e) => {
            // Hide our user interface that shows our A2HS button
            installBtn.style.display = 'none';
            // Show the prompt
            deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the A2HS prompt');
                } else {
                    console.log('User dismissed the A2HS prompt');
                }
                deferredPrompt = null;
            });
        });
    }
});
