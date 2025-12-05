// Dashboard Orchestrator Dynamic Data Loading
// Unified fetcher pattern for loading dashboard metrics

// ========================================
// Demo Data (Fallback)
// ========================================
function getDemoData() {
    return {
        timestamp: new Date().toISOString(),
        morning_brief: {
            weather_of_the_day: "Volatile ⛈️",
            top_signal: "AI Infrastructure Boom",
            why_it_matters: "Major cloud providers announced $127B in AI spend. NVIDIA H200 chips sold out through Q2 2025. This confirms the AI supercycle is accelerating, not slowing.",
            cross_dashboard_convergence: "Risk is ELEVATED due to geopolitical tension, but Crypto is BULLISH and Strategy suggests ACCUMULATE Tech. The Frontier shows massive R&D throughput.",
            action_stance: "Accumulate Dips",
            optional_deep_insight: "While macro headwinds persist (inflation sticky at 3%), the technological deflationary force of AI is creating a bifurcated market. Capital is fleeing traditional value for growth. Watch for a rotation back to energy if oil breaks $80.",
            clarity_level: "High",
            summary_sentence: "Volatility is the price of entry for this AI-driven growth phase. Stay long innovation, hedge with energy."
        },
        overview: {
            BTC: 47850,
            ETH: 2450,
            SP500: 4785,
            DXY: 102.4,
            Gold: 2045
        },
        apps_status: {
            "the-shield": "active",
            "the-coin": "active",
            "the-map": "active",
            "the-frontier": "active",
            "the-strategy": "active",
            "the-library": "active"
        }
    };
}

async function fetchDashboardData() {
    const dataPaths = [
        './data/latest.json',
        './latest.json',
        '../data/the-commander/latest.json',
        '../../data/the-commander/latest.json'
    ];

    let lastError = null;

    for (const dataPath of dataPaths) {
        try {
            const response = await fetch(`${dataPath}?t=${Date.now()}`);
            if (response.ok) {
                const data = await response.json();
                // Basic validation: check if it has meaningful data
                if (data && data.morning_brief && data.morning_brief.weather_of_the_day && data.morning_brief.weather_of_the_day !== "Cloudy") {
                    console.log(`Dashboard data loaded from: ${dataPath}`);
                    return data;
                }
            }
        } catch (error) {
            lastError = error;
            console.debug(`Path ${dataPath} failed, trying next...`);
        }
    }

    console.warn('Failed to load valid live data. Using DEMO data fallback.');
    return getDemoData();
}

async function updateDashboard() {
    const data = await fetchDashboardData();

    if (!data) {
        console.error('Failed to load dashboard data');
        return;
    }

    // Update timestamp
    const timestampEl = document.querySelector('.timestamp');
    if (timestampEl && data.timestamp) {
        const date = new Date(data.timestamp);
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZone: 'UTC'
        };
        timestampEl.textContent = date.toLocaleDateString('en-US', options) + ' UTC';
    }

    // Update Morning Brief
    if (data.morning_brief) {
        const overviewEl = document.getElementById('market-overview');
        if (overviewEl) {
            const mb = data.morning_brief;
            overviewEl.innerHTML = `
                <div class="morning-brief-card">
                    <div class="mb-section">
                        <h3>🌤️ Weather of the Day</h3>
                        <div class="mb-value">${mb.weather_of_the_day || 'N/A'}</div>
                    </div>
                    <div class="mb-section">
                        <h3>📡 Top Signal</h3>
                        <div class="mb-value">${mb.top_signal || 'N/A'}</div>
                    </div>
                    <div class="mb-section">
                        <h3>💡 Why It Matters</h3>
                        <div class="mb-text">${mb.why_it_matters || 'N/A'}</div>
                    </div>
                    <div class="mb-section">
                        <h3>🔄 Convergence</h3>
                        <div class="mb-text">${mb.cross_dashboard_convergence || 'N/A'}</div>
                    </div>
                    <div class="mb-section">
                        <h3>🎯 Action Stance</h3>
                        <div class="mb-value highlight">${mb.action_stance || 'N/A'}</div>
                    </div>
                    ${mb.optional_deep_insight ? `
                    <div class="mb-section">
                        <h3>🧠 Deep Insight</h3>
                        <div class="mb-text">${mb.optional_deep_insight}</div>
                    </div>` : ''}
                    <div class="mb-section">
                        <h3>🔮 Clarity Level</h3>
                        <div class="mb-value">${mb.clarity_level || 'N/A'}</div>
                    </div>
                    <div class="mb-summary">
                        <em>"${mb.summary_sentence || ''}"</em>
                    </div>
                </div>
            `;
        }
    }

    // Update dashboard status
    if (data.apps_status) {
        const statusEl = document.getElementById('dashboard-status');
        if (statusEl) {
            const statusGrid = statusEl.querySelector('.status-grid');
            if (statusGrid) {
                const statusItems = Object.entries(data.apps_status).map(([app, status]) => `
                    <div class="status-item">
                        <span class="status-indicator ${status}"></span>
                        <span class="status-name">${app}</span>
                        <span class="status-label">${status}</span>
                    </div>
                `).join('');
                statusGrid.innerHTML = statusItems;
            }
        }
    }
}

// Load data when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateDashboard);
} else {
    updateDashboard();
}

// Refresh data every 5 minutes
setInterval(updateDashboard, 5 * 60 * 1000);
