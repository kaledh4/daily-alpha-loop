// THE FRONTIER - Silicon Frontier Watch

async function updateDashboard() {
    const frontierData = await loadDashboardData('the-frontier');
    if (!frontierData) return;

    const timestampEl = document.querySelector('.timestamp');
    if (timestampEl) timestampEl.textContent = formatTimestamp(frontierData.generated_at);

    const contentEl = document.getElementById('content');
    const domains = frontierData.domains || {};

    contentEl.innerHTML = `
        <div class="content-card">
            <h2>🚀 Research Domains</h2>
            
            <div class="data-grid">
                ${Object.entries(domains).map(([name, data]) => `
                    <div class="data-section">
                        <h3>${name}</h3>
                        <div class="data-value">${data.total_volume || 0}</div>
                        <p class="data-text" style="text-align: center; margin-top: 10px;">
                            ${data.recent_papers?.length || 0} recent papers
                        </p>
                    </div>
                `).join('')}
            </div>
            
            <h2 style="margin-top: 30px;">💡 Key Breakthroughs</h2>
            ${(frontierData.breakthroughs || []).map(b => `
                <div class="data-section">
                    <h3>${b.title}</h3>
                    <div class="data-text">${b.why_it_matters}</div>
                </div>
            `).join('') || '<p class="data-text">No breakthroughs identified yet</p>'}
            
            <div class="data-section" style="margin-top: 20px;">
                <h3>🤖 AI Frontier Analysis</h3>
                <div class="data-text">${frontierData.ai_analysis || frontierData.ai_briefing || 'Analysis temporarily unavailable'}</div>
            </div>
            
            <div class="summary-box">
                <strong>Integration:</strong><br>
                <em>See ${getSourceBadge('the-commander')} for how frontier breakthroughs impact overall strategy</em>
            </div>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('nav').innerHTML = renderNavigation('the-frontier');
    updateDashboard();
    setInterval(updateDashboard, 5 * 60 * 1000);
});
