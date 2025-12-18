/**
 * SHARED DASHBOARD CORE - V6 DESIGN SYSTEM
 * Renders the unified theme for all dashboards.
 */

function renderHeader(data) {
    const header = document.querySelector('.header');
    if (!header) return;

    const dashId = window.DASHBOARD_NAME || data.dashboard;
    const dashClass = dashId.replace('the-', '');

    header.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            <h1 style="margin: 0;">${data.name || 'Dashboard'}</h1>
        </div>
        <p style="font-size: 1.4rem; color: var(--taupe); font-weight: 600; margin-bottom: 10px;">${data.role || ''}</p>
        <p style="max-width: 800px; margin: 0 auto; color: var(--charcoal); opacity: 0.8;">${data.mission || ''}</p>
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
        if (k === 'confidence' || k === 'uncertainty') return '';
        return '/ 10';
    };

    return `
        <div class="dashboard-card ${window.DASHBOARD_NAME.replace('the-', '')}">
            <div class="card-header">
                <h3>Core Metrics</h3>
            </div>
            <div class="data-grid">
                ${Object.entries(scoring).map(([key, value]) => `
                    <div class="data-section">
                        <h3>${key.replace(/_/g, ' ').toUpperCase()}</h3>
                        <div class="data-value">
                            ${value} <span style="font-size: 0.8rem; color: var(--taupe);">${getScale(key, value)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderDataSources(sources) {
    if (!sources || sources.length === 0) return '';

    return `
        <div class="dashboard-card ${window.DASHBOARD_NAME.replace('the-', '')}" style="margin-top: 20px;">
            <div class="card-header">
                <h3>Data Sources</h3>
            </div>
            <div class="signals">
                ${sources.map(source => `
                    <span class="signal taupe">${source.split('/').pop()}</span>
                `).join('')}
            </div>
        </div>
    `;
}

function renderFlightToSafety(score) {
    if (!score) return '';
    return `
        <div class="dashboard-card shield" style="margin-top: 20px;">
            <div class="card-header">
                <h3>Flight to Safety Score</h3>
            </div>
            <div class="data-grid">
                <div class="data-section">
                    <h3>Current Score</h3>
                    <div class="data-value" style="color: var(--sand-gold);">${score.current} <span style="font-size: 0.8rem; color: var(--taupe);">/ 10</span></div>
                </div>
                <div class="data-section">
                    <h3>Trend</h3>
                    <div class="data-value" style="font-size: 1.2rem;">${score.trend}</div>
                </div>
                <div class="data-section">
                    <h3>3M Forecast</h3>
                    <div class="data-value">${score['3m_forecast'].score}</div>
                    <div style="font-size: 0.8rem; color: var(--taupe);">Conf: ${(score['3m_forecast'].confidence * 100).toFixed(0)}%</div>
                </div>
            </div>
        </div>
    `;
}

function renderAgiTracker(tracker) {
    if (!tracker) return '';
    return `
        <div class="dashboard-card frontier" style="margin-top: 20px;">
            <div class="card-header">
                <h3>AGI Singularity Tracker</h3>
            </div>
            <div class="data-grid">
                <div class="data-section">
                    <h3>Escape Velocity Prob</h3>
                    <div class="data-value" style="color: var(--sage-green);">${(tracker.escape_velocity_probability * 100).toFixed(1)}%</div>
                </div>
                <div class="data-section">
                    <h3>Timeline Estimate</h3>
                    <div class="data-value" style="font-size: 1.2rem;">${tracker.timeline_estimate}</div>
                </div>
            </div>
            <div style="margin-top: 15px;">
                <h3 style="margin-bottom: 8px; color: var(--taupe); font-size: 0.85rem; text-transform: uppercase;">Key Metrics</h3>
                ${Object.entries(tracker.key_metrics).map(([k, v]) => `
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; border-bottom: 1px solid var(--glass-border); padding-bottom: 2px;">
                        <span style="color: var(--charcoal); font-weight: 500;">${k.replace(/_/g, ' ')}</span>
                        <span style="color: var(--sand-gold); font-weight: 700;">${v}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderAssetOutlook(outlook) {
    if (!outlook) return '';
    return `
        <div class="dashboard-card strategy" style="margin-top: 20px;">
            <div class="card-header">
                <h3>Asset Outlook</h3>
            </div>
            <div class="data-grid">
                ${Object.entries(outlook).map(([asset, data]) => `
                    <div class="data-section">
                        <h3>${asset.toUpperCase()}</h3>
                        <div class="data-value" style="font-size: 1.2rem;">${data.risk_reward.toUpperCase()}</div>
                        <div style="font-size: 0.9rem; color: var(--taupe); margin-top: 4px;">Conviction: ${data.conviction}</div>
                        <div class="signals">
                            <span class="signal sage">${data.forecasts['3m'].target}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderAIAnalysis(analysis) {
    return `
        <div class="dashboard-card ${window.DASHBOARD_NAME.replace('the-', '')}" style="margin-top: 20px;">
            <div class="card-header">
                <h3>AI Analysis</h3>
            </div>
            <div class="analysis">
                ${analysis || 'Analysis temporarily unavailable. The system is gathering more data.'}
            </div>
        </div>
    `;
}

function renderMorningBrief(data) {
    const brief = data.sentiment;
    const guidance = data.portfolio_guidance;
    const verdict = data.old_stand_verdict;
    const alphaLoop = data.alpha_loop;

    if (!brief && !data.morning_brief) return '';

    // Support for V6 fields
    if (brief) {
        const toggleClass = brief.risk_toggle.toLowerCase().includes('on') ? 'risk-on' : (brief.risk_toggle.toLowerCase().includes('off') ? 'risk-off' : 'transition');
        return `
            <div class="dashboard-card commander">
                <div class="card-header">
                    <h3>The Commander</h3>
                    <span class="status ${toggleClass}">${brief.risk_toggle}</span>
                </div>
                
                <p class="analysis">${brief.daily_sentiment}</p>

                <div class="data-grid">
                    <div class="data-section">
                        <h3>Rate Path Impact</h3>
                        <div class="data-value" style="font-size: 1.1rem;">${brief.rate_path_impact}</div>
                    </div>
                </div>

                <div class="dashboard-card" style="margin-top: 20px; background: rgba(255,255,255,0.2);">
                    <div class="card-header">
                        <h3>Portfolio Guidance (V6)</h3>
                    </div>
                    <div class="data-grid">
                        <div class="data-section">
                            <h3>Crypto (90%)</h3>
                            <div style="font-weight: 800; color: var(--charcoal);">${guidance.crypto_90.stance}</div>
                            <p style="font-size: 0.85rem; color: var(--taupe); margin-top: 5px;">${guidance.crypto_90.rationale}</p>
                        </div>
                        <div class="data-section">
                            <h3>Metals (10%)</h3>
                            <div style="font-weight: 800; color: var(--charcoal);">${guidance.metals_10.stance}</div>
                            <p style="font-size: 0.85rem; color: var(--taupe); margin-top: 5px;">${guidance.metals_10.rationale}</p>
                        </div>
                        <div class="data-section">
                            <h3>Frontier</h3>
                            <div style="font-weight: 800; color: var(--charcoal);">${guidance.frontier.stance}</div>
                            <p style="font-size: 0.85rem; color: var(--taupe); margin-top: 5px;">${guidance.frontier.rationale}</p>
                        </div>
                        <div class="data-section">
                            <h3>Sectors Focus</h3>
                            <div style="font-weight: 800; color: var(--charcoal);">${guidance.sectors.focus.join(', ')}</div>
                            <p style="font-size: 0.85rem; color: var(--taupe); margin-top: 5px;">Region: ${guidance.sectors.region}</p>
                        </div>
                    </div>
                </div>

                <div class="dashboard-card" style="margin-top: 20px; background: rgba(255,255,255,0.15);">
                    <div class="card-header">
                        <h3>Best Return-to-Risk Sector Allocation</h3>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        ${guidance.sectors.best_return_to_risk_allocation.map(alloc => `
                            <div style="padding: 12px; background: var(--glass-bg); border-radius: 12px; border: 1px solid var(--glass-border);">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-weight: 800; color: var(--charcoal);">${alloc.sector}</span>
                                    <span class="signal sage">${alloc.weight}</span>
                                </div>
                                <p style="font-size: 0.85rem; color: var(--charcoal); margin-top: 5px; opacity: 0.8;">${alloc.rationale}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="data-section" style="margin-top: 20px;">
                    <h3>"Old Stand" Verdict: ${verdict.status}</h3>
                    <p class="analysis" style="font-style: italic; margin-bottom: 0;">${verdict.explanation}</p>
                </div>

                <div class="data-section" style="margin-top: 20px; border: 1px dashed var(--sage-green);">
                    <h3>Actionable IF/THEN Loop</h3>
                    <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 10px;">
                        ${alphaLoop.map(item => `
                            <div style="font-size: 1rem; color: var(--charcoal);">
                                <span style="color: var(--sand-gold); font-weight: 800;">IF</span> ${item.if} 
                                <span style="color: var(--sage-green); font-weight: 800;">THEN</span> ${item.then}
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    // Fallback for V4/V5
    const v5Brief = data.morning_brief;
    if (!v5Brief) return '';

    return `
        <div class="dashboard-card commander">
            <div class="card-header">
                <h3>Morning Brief</h3>
            </div>
            
            <div class="data-grid">
                <div class="data-section">
                    <h3>TOP SIGNAL</h3>
                    <div class="data-value" style="font-size: 1.2rem;">${v5Brief.top_signal}</div>
                </div>
                <div class="data-section">
                    <h3>ACTION STANCE</h3>
                    <div class="data-value" style="color: var(--sage-green);">${v5Brief.action_stance}</div>
                </div>
            </div>

            <div class="data-section" style="margin-top: 20px;">
                <h3>Why It Matters</h3>
                <p class="analysis">${v5Brief.why_it_matters}</p>
            </div>

            <div class="data-section" style="margin-top: 20px;">
                <h3>Cross-Dashboard Convergence</h3>
                <p class="analysis">${v5Brief.cross_dashboard_convergence}</p>
            </div>

            <div class="data-section" style="margin-top: 20px;">
                <h3>The Commander's Summary</h3>
                <p class="analysis" style="font-style: italic;">"${v5Brief.summary_sentence}"</p>
            </div>
        </div>
    `;
}

async function initDashboard(dashboardName) {
    const data = await loadDashboardData(dashboardName);

    if (window.renderNavigation) {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('mode') !== 'seamless') {
            document.getElementById('nav').innerHTML = window.renderNavigation(dashboardName);
        } else {
            const navEl = document.getElementById('nav');
            if (navEl) navEl.style.display = 'none';
        }
    }

    if (!data) {
        document.getElementById('content').innerHTML = `
            <div class="dashboard-card">
                <h2>Loading Data...</h2>
                <p>Please wait while we fetch the latest intelligence.</p>
            </div>
        `;
        return;
    }

    renderHeader(data);

    const contentEl = document.getElementById('content');

    if (dashboardName === 'the-commander') {
        let html = renderMorningBrief(data);
        if (data.flight_to_safety_score) html += renderFlightToSafety(data.flight_to_safety_score);
        if (data.asset_outlook) html += renderAssetOutlook(data.asset_outlook);
        if (data.agi_singularity_tracker) html += renderAgiTracker(data.agi_singularity_tracker);
        if (data.ai_analysis) html += renderAIAnalysis(data.ai_analysis);
        contentEl.innerHTML = html;
    } else {
        let html = '';
        if (data.regime) {
            html += `
                <div class="dashboard-card ${dashboardName.replace('the-', '')}">
                    <div class="card-header">
                        <h3>Market Regime</h3>
                        <span class="status" style="background: ${data.regime.color}20; color: ${data.regime.color};">${data.regime.regime}</span>
                    </div>
                    <p class="analysis">Confidence: ${(data.regime.confidence * 100).toFixed(0)}%</p>
                </div>
            `;
        }
        html += renderScoring(data.scoring);
        if (data.metrics && Array.isArray(data.metrics) && data.metrics.length > 0) {
            html += `
                <div class="dashboard-card ${dashboardName.replace('the-', '')}" style="margin-top: 20px;">
                    <div class="card-header">
                        <h3>Market Metrics</h3>
                    </div>
                    <div class="data-grid">
                        ${data.metrics.map(m => `
                            <div class="data-section">
                                <h3>${m.name}</h3>
                                <div class="data-value">${m.value}</div>
                                <div class="signals">
                                    <span class="signal taupe">${m.signal}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        html += renderAIAnalysis(data.ai_analysis);
        html += renderDataSources(data.data_sources);
        html += `
            <div style="margin-top: 40px; text-align: center; padding-bottom: 20px; border-top: 1px solid var(--glass-border); padding-top: 20px;">
                <a href="../read_all/index.html" style="color: var(--taupe); text-decoration: none; font-size: 0.9rem;">Read All Data (Debug)</a>
            </div>
        `;
        contentEl.innerHTML = html;
    }
}

// Register Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('service-worker.js')
            .then(reg => console.log('SW registered'))
            .catch(err => console.log('SW failed', err));
    });
}

// Auto-initialize
if (window.DASHBOARD_NAME) {
    document.addEventListener('DOMContentLoaded', () => {
        initDashboard(window.DASHBOARD_NAME);
        setInterval(() => initDashboard(window.DASHBOARD_NAME), 5 * 60 * 1000);
    });
}

// PWA Install
let deferredPrompt;
const installBtn = document.getElementById('install-app-btn');
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBtn) {
        installBtn.style.display = 'block';
        installBtn.addEventListener('click', () => {
            installBtn.style.display = 'none';
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then(res => {
                console.log('User choice:', res.outcome);
                deferredPrompt = null;
            });
        });
    }
});
