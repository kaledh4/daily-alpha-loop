// SHARED NAVIGATION COMPONENT - Used by all dashboards

const DASHBOARDS = [
    { id: 'the-commander', name: 'The Commander', mission: 'Morning Brief', emoji: '⭐' },
    { id: 'the-shield', name: 'The Shield', mission: 'Risk Monitor', emoji: '🛡️' },
    { id: 'the-coin', name: 'The Coin', mission: 'Crypto Scanner', emoji: '🪙' },
    { id: 'the-map', name: 'The Map', mission: 'Macro Trends', emoji: '🗺️' },
    { id: 'the-frontier', name: 'The Frontier', mission: 'AI Breakthroughs', emoji: '🚀' },
    { id: 'the-strategy', name: 'The Strategy', mission: 'Opportunity Radar', emoji: '🎯' },
    { id: 'the-library', name: 'The Library', mission: 'Knowledge Archive', emoji: '📚' }
];

function renderNavigation(currentDashboard) {
    const navHTML = DASHBOARDS.map(dash => {
        const isActive = dash.id === currentDashboard;
        const url = dash.id === 'the-commander' ? '../the-commander/' : `../${dash.id}/`;

        return `
      <a href="${url}" class="nav-card ${isActive ? 'active' : ''}">
        <h3>${dash.emoji} ${dash.name}</h3>
        <p>${dash.mission}</p>
      </a>
    `;
    }).join('');

    return `<div class="dashboard-nav">${navHTML}</div>`;
}

function getSourceBadge(dashboardId) {
    const dash = DASHBOARDS.find(d => d.id === dashboardId);
    if (!dash) return '';

    const url = dashboardId === 'the-commander' ? '../the-commander/' : `../${dashboardId}/`;

    return `<a href="${url}" class="source-badge" title="View ${dash.name}">${dash.emoji} ${dash.name}</a>`;
}

function formatTimestamp(timestamp) {
    if (!timestamp) return 'Loading...';
    const date = new Date(timestamp);
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'UTC'
    };
    return date.toLocaleDateString('en-US', options) + ' UTC';
}

async function loadDashboardData(dashboardId) {
    const paths = [
        `../../data/${dashboardId}/latest.json`,
        `../data/${dashboardId}/latest.json`,
        `./data/latest.json`
    ];

    for (const path of paths) {
        try {
            const response = await fetch(`${path}?t=${Date.now()}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (e) {
            console.debug(`Failed to load from ${path}`);
        }
    }

    return null;
}
