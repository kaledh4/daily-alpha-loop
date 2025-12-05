// THE MAP - Macro & TASI Trendsetter

async function updateDashboard() {
    const mapData = await loadDashboardData('the-map');
    if (!mapData) return;

    const timestampEl = document.querySelector('.timestamp');
    if (timestampEl) timestampEl.textContent = formatTimestamp(mapData.timestamp);

    const contentEl = document.getElementById('content');
    const macro = mapData.macro || {};

    contentEl.innerHTML = `
        <div class="content-card">
            <h2>🗺️ Macro Overview</h2>
            
            <div class="data-grid">
                <div class="data-section">
                    <h3>Oil Price</h3>
                    <div class="data-value">$${(macro.oil || 0).toFixed(2)}</div>
                </div>
                
                <div class="data-section">
                    <h3>DXY (Dollar Index)</h3>
                    <div class="data-value">${(macro.dxy || 0).toFixed(2)}</div>
                </div>
                
                <div class="data-section">
                    <h3>Gold</h3>
                    <div class="data-value">$${(macro.gold || 0).toFixed(2)}</div>
                </div>
                
                <div class="data-section">
                    <h3>S&P 500</h3>
                    <div class="data-value">${(macro.sp500 || 0).toFixed(2)}</div>
                </div>
                
                <div class="data-section">
                    <h3>TASI</h3>
                    <div class="data-value">${(macro.tasi || 0).toFixed(2)}</div>
                </div>
                
                <div class="data-section">
                    <h3>10Y Treasury</h3>
                    <div class="data-value">${(macro.treasury_10y || 0).toFixed(2)}%</div>
                </div>
            </div>
            
            <div class="data-section" style="margin-top: 20px;">
                <h3>🎯 TASI Mood Prediction</h3>
                <div class="data-value stance">${mapData.tasi_mood || 'N/A'}</div>
            </div>
            
            <div class="data-section">
                <h3>📊 Key Drivers</h3>
                ${(mapData.drivers || []).map((d, i) => `
                    <p class="data-text">• ${d}</p>
                `).join('') || '<p class="data-text">No drivers available</p>'}
            </div>
            
            <div class="data-section">
                <h3>🤖 AI Analysis</h3>
                <div class="data-text">${mapData.ai_analysis || 'Analysis temporarily unavailable'}</div>
            </div>
            
            <div class="summary-box">
                <strong>Cross-Reference:</strong><br>
                <em>See ${getSourceBadge('the-commander')} for how macro trends converge with other signals</em>
            </div>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('nav').innerHTML = renderNavigation('the-map');
    updateDashboard();
    setInterval(updateDashboard, 5 * 60 * 1000);
});
