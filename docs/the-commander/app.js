// THE COMMANDER - Master Orchestrator
// Displays the Morning Brief and dashboard status

// ========================================
// Demo Data (Fallback)
// ========================================
function getDemoData() {
    return {
        timestamp: new Date().toISOString(),
        morning_brief: {
            weather_of_the_day: "Volatile",
            top_signal: "AI Infrastructure Boom",
            why_it_matters: "Major cloud providers announced $127B in AI spend. NVIDIA H200 chips sold out through Q2 2025. This confirms the AI supercycle is accelerating, not slowing.",
            cross_dashboard_convergence: "Risk is ELEVATED due to geopolitical tension, but Crypto is BULLISH and Strategy suggests ACCUMULATE Tech. The Frontier shows massive R&D throughput.",
            action_stance: "Accumulate Dips",
            optional_deep_insight: "While macro headwinds persist (inflation sticky at 3%), the technological deflationary force of AI is creating a bifurcated market. Capital is fleeing traditional value for growth. Watch for a rotation back to energy if oil breaks $80.",
            clarity_level: "High",
            summary_sentence: "Risk shows the environment, crypto shows sentiment, macro shows the wind, breakthroughs show the future, strategy shows the stance, and knowledge shows the long-term signal — combine all six to guide the user clearly through today."
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
        '../../data/the-commander/latest.json',
        '../data/the-commander/latest.json',
        './data/latest.json',
        './latest.json'
    ];

    let lastError = null;

    for (const dataPath of dataPaths) {
        try {
            const response = await fetch(`${dataPath}?t=${Date.now()}`);
            if (response.ok) {
                const data = await response.json();
                // Validate meaningful data
                if (data && data.morning_brief && data.morning_brief.weather_of_the_day) {
                    console.log(`✅ Data loaded from: ${dataPath}`);
                    return data;
                }
            }
        } catch (error) {
            lastError = error;
            console.debug(`Path ${dataPath} failed, trying next...`);
        }
    }

    console.warn('⚠️ Failed to load live data. Using DEMO data fallback.');
    return getDemoData();
}

async function updateDashboard() {
    const data = await fetchDashboardData();

    if (!data) {
        console.error('❌ Failed to load dashboard data');
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

            // Weather emoji mapping
            const weatherEmoji = {
                'Stormy': '⛈️',
                'Cloudy': '☁️',
                'Sunny': '☀️',
                'Volatile': '🌪️',
                'Foggy': '🌫️'
            };

            const weather = mb.weather_of_the_day || 'Cloudy';
            const emoji = weatherEmoji[weather.replace(/[⛈️☁️☀️🌪️🌫️]/g, '').trim()] || '☁️';

            overviewEl.innerHTML = `
                <div class="morning-brief-card">
                    <h2 class="brief-title">☕ Morning Brief - 30 Second Read</h2>
                    
                    <div class="mb-section weather">
                        <h3>🌤️ Weather of the Day</h3>
                        <div class="mb-value weather-badge">${emoji} ${weather}</div>
                    </div>
                    
                    <div class="mb-section">
                        <h3>📡 Top Signal</h3>
                        <div class="mb-value signal">${mb.top_signal || 'N/A'}</div>
                    </div>
                    
                    <div class="mb-section">
                        <h3>💡 Why It Matters</h3>
                        <div class="mb-text">${mb.why_it_matters || 'N/A'}</div>
                    </div>
                    
                    <div class="mb-section">
                        <h3>🔄 Cross-Dashboard Convergence</h3>
                        <div class="mb-text convergence">${mb.cross_dashboard_convergence || 'N/A'}</div>
                    </div>
                    
                    <div class="mb-section">
                        <h3>🎯 Action Stance</h3>
                        <div class="mb-value stance">${mb.action_stance || 'N/A'}</div>
                    </div>
                    
                    ${mb.optional_deep_insight ? `
                    <div class="mb-section deep-insight">
                        <h3>🧠 Deep Insight (Advanced)</h3>
                        <div class="mb-text">${mb.optional_deep_insight}</div>
                    </div>` : ''}
                    
                    <div class="mb-section">
                        <h3>🔮 Clarity Level</h3>
                        <div class="mb-value clarity ${(mb.clarity_level || '').toLowerCase()}">${mb.clarity_level || 'N/A'}</div>
                    </div>
                    
                    ${mb.summary_sentence ? `
                    <div class="mb-summary">
                        <strong>Summary:</strong> <em>"${mb.summary_sentence}"</em>
                    </div>` : ''}
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
                const statusNames = {
                    'the-shield': 'The Shield',
                    'the-coin': 'The Coin',
                    'the-map': 'The Map',
                    'the-frontier': 'The Frontier',
                    'the-strategy': 'The Strategy',
                    'the-library': 'The Library'
                };

                const statusItems = Object.entries(data.apps_status).map(([app, status]) => `
                    <div class="status-item">
                        <span class="status-indicator ${status}"></span>
                        <span class="status-name">${statusNames[app] || app}</span>
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
