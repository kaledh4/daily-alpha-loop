// THE COMMANDER - With source attribution and unified navigation

async function updateDashboard() {
    // Load all dashboard data
    const [commanderData, shieldData, coinData, mapData, frontierData, strategyData, libraryData] = await Promise.all([
        loadDashboardData('the-commander'),
        loadDashboardData('the-shield'),
        loadDashboardData('the-coin'),
        loadDashboardData('the-map'),
        loadDashboardData('the-frontier'),
        loadDashboardData('the-strategy'),
        loadDashboardData('the-library')
    ]);

    if (!commanderData) return;

    // Update timestamp
    const timestampEl = document.querySelector('.timestamp');
    if (timestampEl) {
        timestampEl.textContent = formatTimestamp(commanderData.timestamp);
    }

    // Update Morning Brief with source attribution
    const brief = commanderData.morning_brief;
    if (brief) {
        const contentEl = document.getElementById('content');

        // Weather emoji mapping
        const weatherEmoji = {
            'Stormy': '⛈️',
            'Cloudy': '☁️',
            'Sunny': '☀️',
            'Volatile': '🌪️',
            'Foggy': '🌫️'
        };

        const weather = brief.weather_of_the_day || 'Cloudy';
        const emoji = weatherEmoji[weather.replace(/[⛈️☁️☀️🌪️🌫️]/g, '').trim()] || '☁️';

        contentEl.innerHTML = `
            <div class="content-card">
                <h2>☕ Morning Brief - 30 Second Read</h2>
                
                <div class="data-grid">
                    <div class="data-section">
                        <h3>🌤️ Weather of the Day ${getSourceBadge('the-shield')}</h3>
                        <div class="data-value weather-badge">${emoji} ${weather}</div>
                        <p class="data-text" style="font-size: 0.9rem; color: #a0aec0; margin-top: 10px;">
                            Based on ${shieldData?.risk_assessment?.level || 'N/A'} risk level
                        </p>
                    </div>
                    
                    <div class="data-section">
                        <h3>📡 Top Signal ${getSourceBadge('the-shield')}</h3>
                        <div class="data-value" style="color: #4299e1; font-size: 1.4rem;">${brief.top_signal || 'N/A'}</div>
                    </div>
                    
                    <div class="data-section">
                        <h3>🪙 Crypto Momentum ${getSourceBadge('the-coin')}</h3>
                        <div class="data-value">${coinData?.momentum || 'N/A'}</div>
                        <p class="data-text" style="font-size: 0.9rem; color: #a0aec0; margin-top: 10px;">
                            BTC: $${coinData?.btc_price?.toLocaleString() || 'N/A'}
                        </p>
                    </div>
                    
                    <div class="data-section">
                        <h3>🗺️ Macro Mood ${getSourceBadge('the-map')}</h3>
                        <div class="data-value">${mapData?.tasi_mood || 'N/A'}</div>
                    </div>
                    
                    <div class="data-section">
                        <h3>🚀 Breakthroughs ${getSourceBadge('the-frontier')}</h3>
                        <div class="data-value">${frontierData?.breakthroughs?.length || 0} Identified</div>
                    </div>
                    
                    <div class="data-section">
                        <h3>🎯 Strategy Stance ${getSourceBadge('the-strategy')}</h3>
                        <div class="data-value stance">${strategyData?.stance || 'N/A'}</div>
                    </div>
                </div>
                
                <div class="data-section" style="margin-top: 20px;">
                    <h3>💡 Why It Matters</h3>
                    <div class="data-text">${brief.why_it_matters || 'N/A'}</div>
                </div>
                
                <div class="data-section">
                    <h3>🔄 Cross-Dashboard Convergence</h3>
                    <div class="data-text" style="background: rgba(66, 153, 225, 0.05); padding: 15px; border-radius: 8px; border-left: 4px solid #4299e1;">
                        ${brief.cross_dashboard_convergence || 'N/A'}
                    </div>
                </div>
                
                <div class="data-section">
                    <h3>🎯 Action Stance</h3>
                    <div class="data-value stance">${brief.action_stance || 'N/A'}</div>
                </div>
                
                ${brief.optional_deep_insight ? `
                <div class="data-section" style="background: rgba(102, 126, 234, 0.1); border-color: rgba(102, 126, 234, 0.3);">
                    <h3>🧠 Deep Insight (Advanced)</h3>
                    <div class="data-text">${brief.optional_deep_insight}</div>
                </div>` : ''}
                
                <div class="data-section">
                    <h3>🔮 Clarity Level</h3>
                    <div class="data-value clarity ${(brief.clarity_level || '').toLowerCase()}">${brief.clarity_level || 'N/A'}</div>
                </div>
                
                ${brief.summary_sentence ? `
                <div class="summary-box">
                    <strong>System Philosophy:</strong><br>
                    <em>"${brief.summary_sentence}"</em>
                </div>` : ''}
            </div>
            
            <div class="content-card">
                <h2>📚 Knowledge Summaries ${getSourceBadge('the-library')}</h2>
                ${(libraryData?.summaries || []).map(s => `
                    <div class="data-section">
                        <h3>${s.title}</h3>
                        <p class="data-text"><strong>ELI5:</strong> ${s.eli5}</p>
                        <p class="data-text" style="margin-top: 10px;"><strong>Long-term:</strong> ${s.long_term}</p>
                    </div>
                `).join('') || '<p class="data-text">No summaries available</p>'}
            </div>
        `;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('nav').innerHTML = renderNavigation('the-commander');
    updateDashboard();
    setInterval(updateDashboard, 5 * 60 * 1000);
});
