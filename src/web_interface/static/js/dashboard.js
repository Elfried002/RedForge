/**
 * RedForge - Tableau de Bord Amélioré
 * Gestion et affichage du tableau de bord principal avec support multi-attaques et APT
 * Version: 2.0.0
 */

// ========================================
// INITIALISATION
// ========================================

let refreshInterval = null;
let dashboardData = {};
let socket = null;
let realTimeChart = null;

document.addEventListener('DOMContentLoaded', function() {
    initWebSocket();
    initDashboard();
    startAutoRefresh();
});

function initWebSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('WebSocket connecté pour le dashboard');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        console.log('WebSocket déconnecté');
        updateConnectionStatus(false);
    });
    
    socket.on('scan_completed', (data) => {
        handleScanCompleted(data);
    });
    
    socket.on('attack_progress', (data) => {
        updateAttackProgress(data);
    });
    
    socket.on('multi_attack_completed', (data) => {
        handleMultiAttackCompleted(data);
    });
    
    socket.on('apt_completed', (data) => {
        handleAPTCompleted(data);
    });
    
    socket.on('stats_update', (data) => {
        updateRealTimeStats(data);
    });
}

function initDashboard() {
    loadDashboardStats();
    loadRecentActivities();
    loadTopVulnerabilities();
    loadSessions();
    loadMultiAttackStats();
    loadAPTOperations();
    loadStealthMetrics();
    initRealTimeChart();
    
    // Configurer les boutons d'action
    const refreshBtn = document.getElementById('refresh-dashboard');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshDashboard);
    }
    
    const exportBtn = document.getElementById('export-report');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportDashboardReport);
    }
    
    const clearHistoryBtn = document.getElementById('clear-history');
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', clearActivityHistory);
    }
    
    const exportJSONBtn = document.getElementById('export-json');
    if (exportJSONBtn) {
        exportJSONBtn.addEventListener('click', exportJSONReport);
    }
}

function startAutoRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(refreshDashboard, 30000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

async function refreshDashboard() {
    await loadDashboardStats();
    await loadRecentActivities();
    await loadTopVulnerabilities();
    await loadSessions();
    await loadMultiAttackStats();
    await loadAPTOperations();
    await loadStealthMetrics();
    
    const lastUpdate = document.getElementById('last-update');
    if (lastUpdate) {
        lastUpdate.textContent = 'Dernière mise à jour: ' + new Date().toLocaleTimeString('fr-FR');
    }
    
    showNotification('Tableau de bord mis à jour', 'info', 2000);
}

function updateConnectionStatus(connected) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    
    if (statusDot) {
        statusDot.classList.toggle('active', connected);
    }
    if (statusText) {
        statusText.textContent = connected ? 'Connecté' : 'Déconnecté';
    }
}

// ========================================
// STATISTIQUES DU TABLEAU DE BORD (améliorées)
// ========================================

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        if (!response.ok) throw new Error('Erreur chargement statistiques');
        
        const stats = await response.json();
        dashboardData.stats = stats;
        
        updateStatCards(stats);
        updateProgressBars(stats);
        
    } catch (error) {
        console.error('Erreur chargement statistiques:', error);
        updateStatCards(getDefaultStats());
    }
}

function updateStatCards(stats) {
    const statElements = {
        'total-targets': stats.totalTargets || 0,
        'total-attacks': stats.totalAttacks || 0,
        'vulnerabilities-found': stats.vulnerabilitiesFound || 0,
        'active-sessions': stats.activeSessions || 0,
        'critical-vulns': stats.criticalVulns || 0,
        'high-vulns': stats.highVulns || 0,
        'medium-vulns': stats.mediumVulns || 0,
        'low-vulns': stats.lowVulns || 0,
        'scan-success-rate': stats.scanSuccessRate || '100%',
        'avg-scan-time': stats.avgScanTime || '0s',
        'multi-attacks': stats.multiAttacks || 0,
        'apt-operations': stats.aptOperations || 0,
        'stealth-score': stats.stealthScore || 0
    };
    
    for (const [id, value] of Object.entries(statElements)) {
        const element = document.getElementById(id);
        if (element) {
            const oldValue = element.textContent;
            element.textContent = value;
            if (!isNaN(parseInt(value))) {
                animateValue(element, oldValue, value);
            }
        }
    }
    
    // Mettre à jour le score furtif avec une jauge
    updateStealthGauge(stats.stealthScore || 0);
}

function updateStealthGauge(score) {
    const gauge = document.getElementById('stealth-gauge');
    const gaugeFill = document.getElementById('stealth-gauge-fill');
    const gaugeText = document.getElementById('stealth-gauge-text');
    
    if (gaugeFill) {
        gaugeFill.style.width = `${score}%`;
        gaugeFill.style.backgroundColor = getStealthColor(score);
    }
    if (gaugeText) {
        gaugeText.textContent = `${score}%`;
    }
}

function getStealthColor(score) {
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#ff9800';
    if (score >= 40) return '#ff5722';
    return '#f44336';
}

function animateValue(element, start, end) {
    const startNum = parseInt(start) || 0;
    const endNum = parseInt(end) || 0;
    if (startNum === endNum) return;
    
    const duration = 500;
    const step = (endNum - startNum) / (duration / 16);
    let current = startNum;
    
    const timer = setInterval(function() {
        current += step;
        if ((step > 0 && current >= endNum) || (step < 0 && current <= endNum)) {
            element.textContent = endNum;
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current);
        }
    }, 16);
}

function updateProgressBars(stats) {
    const progressElements = {
        'scan-progress': stats.scanProgress || 0,
        'coverage-progress': stats.coverageProgress || 0,
        'apt-progress': stats.aptProgress || 0
    };
    
    for (const [id, value] of Object.entries(progressElements)) {
        const element = document.getElementById(id);
        if (element) {
            element.style.width = value + '%';
            element.setAttribute('aria-valuenow', value);
            
            const textElement = element.parentElement ? element.parentElement.querySelector('.progress-text') : null;
            if (textElement) textElement.textContent = value + '%';
        }
    }
}

// ========================================
// STATISTIQUES DES ATTAQUES MULTIPLES
// ========================================

async function loadMultiAttackStats() {
    try {
        const response = await fetch('/api/multi-attack/stats');
        if (!response.ok) throw new Error('Erreur chargement stats multi-attaques');
        
        const stats = await response.json();
        dashboardData.multiAttackStats = stats;
        
        displayMultiAttackStats(stats);
        
    } catch (error) {
        console.error('Erreur chargement multi-attaques:', error);
        displayMultiAttackStats(getDefaultMultiAttackStats());
    }
}

function displayMultiAttackStats(stats) {
    const container = document.getElementById('multi-attack-stats');
    if (!container) return;
    
    container.innerHTML = `
        <div class="multi-attack-grid">
            <div class="stat-card-mini">
                <div class="stat-value-mini">${stats.totalMultiAttacks || 0}</div>
                <div class="stat-label-mini">Multi-attaques lancées</div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-value-mini">${stats.avgSuccessRate || 0}%</div>
                <div class="stat-label-mini">Taux de succès moyen</div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-value-mini">${stats.totalAttacksExecuted || 0}</div>
                <div class="stat-label-mini">Attaques exécutées</div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-value-mini">${stats.fastestExecution || 0}s</div>
                <div class="stat-label-mini">Exécution la plus rapide</div>
            </div>
        </div>
        <div class="recent-multi-attacks">
            <h4>Multi-attaques récentes</h4>
            <div class="recent-list">
                ${stats.recentMultiAttacks?.map(attack => `
                    <div class="recent-item">
                        <span class="recent-target">${escapeHtml(attack.target)}</span>
                        <span class="recent-count">${attack.attackCount} attaques</span>
                        <span class="recent-status status-${attack.status}">${attack.status}</span>
                        <span class="recent-time">${formatTimeAgo(attack.timestamp)}</span>
                    </div>
                `).join('') || '<div class="no-data">Aucune multi-attaque récente</div>'}
            </div>
        </div>
    `;
}

function getDefaultMultiAttackStats() {
    return {
        totalMultiAttacks: 0,
        avgSuccessRate: 0,
        totalAttacksExecuted: 0,
        fastestExecution: 0,
        recentMultiAttacks: []
    };
}

// ========================================
// OPÉRATIONS APT
// ========================================

async function loadAPTOperations() {
    try {
        const response = await fetch('/api/apt/operations');
        if (!response.ok) throw new Error('Erreur chargement opérations APT');
        
        const data = await response.json();
        dashboardData.aptOperations = data;
        
        displayAPTOperations(data);
        
    } catch (error) {
        console.error('Erreur chargement APT:', error);
        displayAPTOperations({ predefined: [], custom: [] });
    }
}

function displayAPTOperations(data) {
    const container = document.getElementById('apt-operations');
    if (!container) return;
    
    const allOps = [...(data.predefined || []), ...(data.custom || [])];
    
    if (allOps.length === 0) {
        container.innerHTML = '<div class="no-data">Aucune opération APT disponible</div>';
        return;
    }
    
    container.innerHTML = `
        <div class="apt-stats">
            <div class="stat-card-mini">
                <div class="stat-value-mini">${data.totalExecutions || 0}</div>
                <div class="stat-label-mini">Opérations exécutées</div>
            </div>
            <div class="stat-card-mini">
                <div class="stat-value-mini">${data.avgSuccessRate || 0}%</div>
                <div class="stat-label-mini">Taux de succès APT</div>
            </div>
        </div>
        <div class="apt-operations-list">
            ${allOps.slice(0, 5).map(op => `
                <div class="apt-operation-item">
                    <div class="apt-operation-name">${escapeHtml(op)}</div>
                    <button class="btn btn-sm btn-primary" onclick="runAPTOperation('${escapeHtml(op)}')">
                        🎯 Lancer
                    </button>
                </div>
            `).join('')}
        </div>
        ${allOps.length > 5 ? '<div class="view-all"><button class="btn btn-link" onclick="viewAllAPTOperations()">Voir toutes les opérations →</button></div>' : ''}
    `;
}

// ========================================
// MÉTRIQUES FURTIVES
// ========================================

async function loadStealthMetrics() {
    try {
        const response = await fetch('/api/stealth/metrics');
        if (!response.ok) throw new Error('Erreur chargement métriques furtives');
        
        const metrics = await response.json();
        dashboardData.stealthMetrics = metrics;
        
        displayStealthMetrics(metrics);
        
    } catch (error) {
        console.error('Erreur chargement métriques furtives:', error);
        displayStealthMetrics(getDefaultStealthMetrics());
    }
}

function displayStealthMetrics(metrics) {
    const container = document.getElementById('stealth-metrics');
    if (!container) return;
    
    container.innerHTML = `
        <div class="stealth-metrics-grid">
            <div class="metric-item">
                <div class="metric-label">Niveau actuel</div>
                <div class="metric-value ${metrics.currentLevel}">${metrics.currentLevel?.toUpperCase() || 'MEDIUM'}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Délai moyen</div>
                <div class="metric-value">${metrics.avgDelay || 1.5}s</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">TOR actif</div>
                <div class="metric-value">${metrics.torActive ? '✅ Oui' : '❌ Non'}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">User-Agents aléatoires</div>
                <div class="metric-value">${metrics.randomUserAgents ? '✅ Oui' : '❌ Non'}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Rotation proxies</div>
                <div class="metric-value">${metrics.proxyRotation ? '✅ Oui' : '❌ Non'}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Risque détection</div>
                <div class="metric-value risk-${metrics.detectionRisk}">${metrics.detectionRisk?.toUpperCase() || 'MOYEN'}</div>
            </div>
        </div>
    `;
}

function getDefaultStealthMetrics() {
    return {
        currentLevel: 'medium',
        avgDelay: 1.5,
        torActive: false,
        randomUserAgents: true,
        proxyRotation: false,
        detectionRisk: 'medium'
    };
}

// ========================================
// GRAPHIQUE TEMPS RÉEL
// ========================================

function initRealTimeChart() {
    const canvas = document.getElementById('realtime-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    realTimeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Attaques/minute',
                    data: [],
                    borderColor: '#d32f2f',
                    backgroundColor: 'rgba(211, 47, 47, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Efficacité furtive',
                    data: [],
                    borderColor: '#4caf50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'top' },
                tooltip: { mode: 'index', intersect: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Nombre / Pourcentage' }
                }
            }
        }
    });
}

function updateRealTimeStats(stats) {
    if (!realTimeChart) return;
    
    const now = new Date().toLocaleTimeString();
    
    realTimeChart.data.labels.push(now);
    realTimeChart.data.datasets[0].data.push(stats.attacksPerMinute || 0);
    realTimeChart.data.datasets[1].data.push(stats.stealthEffectiveness || 0);
    
    if (realTimeChart.data.labels.length > 20) {
        realTimeChart.data.labels.shift();
        realTimeChart.data.datasets[0].data.shift();
        realTimeChart.data.datasets[1].data.shift();
    }
    
    realTimeChart.update();
}

// ========================================
// ACTIVITÉS RÉCENTES (améliorées)
// ========================================

async function loadRecentActivities() {
    try {
        const response = await fetch('/api/activities/recent?limit=15');
        if (!response.ok) throw new Error('Erreur chargement activités');
        
        const activities = await response.json();
        dashboardData.activities = activities;
        
        displayRecentActivities(activities);
        
    } catch (error) {
        console.error('Erreur chargement activités:', error);
        displayRecentActivities(getDefaultActivities());
    }
}

function displayRecentActivities(activities) {
    const container = document.getElementById('recent-activities');
    if (!container) return;
    
    if (!activities || activities.length === 0) {
        container.innerHTML = '<div class="no-data">Aucune activité récente</div>';
        return;
    }
    
    container.innerHTML = activities.map(function(activity) {
        return `
            <div class="activity-item fade-in" data-id="${activity.id || ''}">
                <div class="activity-icon ${activity.type}">
                    ${getActivityIcon(activity.type)}
                </div>
                <div class="activity-content">
                    <div class="activity-title">${escapeHtml(activity.title)}</div>
                    <div class="activity-description">${escapeHtml(activity.description || '')}</div>
                    <div class="activity-meta">
                        <span class="activity-time">${formatTimeAgo(activity.timestamp)}</span>
                        ${activity.duration ? `<span class="activity-duration">Durée: ${activity.duration}s</span>` : ''}
                    </div>
                </div>
                ${activity.status ? '<div class="activity-status status-' + activity.status + '">' + getStatusIcon(activity.status) + '</div>' : ''}
            </div>
        `;
    }).join('');
}

function getActivityIcon(type) {
    const icons = {
        'scan': '🔍',
        'attack': '🎯',
        'multi_attack': '📚',
        'apt': '🎯',
        'vulnerability': '⚠️',
        'session': '🔌',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'stealth': '🕵️'
    };
    return icons[type] || '📌';
}

function getStatusIcon(status) {
    const icons = {
        'success': '✓',
        'failed': '✗',
        'running': '⟳',
        'pending': '⏳',
        'completed': '✅'
    };
    return icons[status] || '●';
}

// ========================================
// GESTION DES ÉVÉNEMENTS WEBSOCKET
// ========================================

function handleScanCompleted(data) {
    showNotification(`Scan terminé pour ${data.target}`, 'success');
    refreshDashboard();
}

function updateAttackProgress(data) {
    const progressElement = document.getElementById(`progress-${data.task_id}`);
    if (progressElement) {
        progressElement.style.width = `${data.progress}%`;
    }
}

function handleMultiAttackCompleted(data) {
    showNotification(`Multi-attaque terminée: ${data.successful}/${data.total_attacks} réussies`, 'info');
    refreshDashboard();
}

function handleAPTCompleted(data) {
    showNotification(`Opération APT complétée! Succès global: ${data.overall_success}%`, 'warning');
    refreshDashboard();
}

// ========================================
// EXPORTATION ET RAPPORTS (améliorée)
// ========================================

async function exportDashboardReport() {
    try {
        showNotification('Génération du rapport en cours...', 'info');
        
        const response = await fetch('/api/report/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                format: 'html',
                includeCharts: true,
                includeActivities: true,
                includeMultiAttack: true,
                includeAPT: true,
                includeStealth: true
            })
        });
        
        if (!response.ok) throw new Error('Erreur génération rapport');
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `redforge_report_${new Date().toISOString().slice(0, 19)}.html`;
        a.click();
        URL.revokeObjectURL(url);
        
        showNotification('Rapport généré avec succès', 'success');
        
    } catch (error) {
        console.error('Erreur exportation:', error);
        showNotification('Erreur lors de la génération du rapport', 'error');
    }
}

async function exportJSONReport() {
    try {
        const response = await fetch('/api/report/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                format: 'json',
                includeCharts: true,
                includeActivities: true,
                includeMultiAttack: true,
                includeAPT: true,
                includeStealth: true
            })
        });
        
        if (!response.ok) throw new Error('Erreur génération rapport JSON');
        
        const data = await response.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `redforge_report_${new Date().toISOString().slice(0, 19)}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        showNotification('Rapport JSON généré avec succès', 'success');
        
    } catch (error) {
        console.error('Erreur exportation JSON:', error);
        showNotification('Erreur lors de la génération du rapport JSON', 'error');
    }
}

async function clearActivityHistory() {
    if (confirm('Voulez-vous vraiment effacer tout l\'historique des activités ?')) {
        try {
            await fetch('/api/activities/clear', { method: 'DELETE' });
            showNotification('Historique effacé', 'success');
            loadRecentActivities();
        } catch (error) {
            showNotification('Erreur lors de l\'effacement', 'error');
        }
    }
}

// ========================================
// TOP VULNÉRABILITÉS (amélioré)
// ========================================

async function loadTopVulnerabilities() {
    try {
        const response = await fetch('/api/vulnerabilities/top?limit=10');
        if (!response.ok) throw new Error('Erreur chargement vulnérabilités');
        
        const vulnerabilities = await response.json();
        dashboardData.topVulnerabilities = vulnerabilities;
        
        displayTopVulnerabilities(vulnerabilities);
        
    } catch (error) {
        console.error('Erreur chargement vulnérabilités:', error);
        displayTopVulnerabilities(getDefaultVulnerabilities());
    }
}

function displayTopVulnerabilities(vulnerabilities) {
    const container = document.getElementById('top-vulnerabilities');
    if (!container) return;
    
    if (!vulnerabilities || vulnerabilities.length === 0) {
        container.innerHTML = '<div class="no-data">Aucune vulnérabilité détectée</div>';
        return;
    }
    
    container.innerHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Sévérité</th>
                    <th>Cible</th>
                    <th>Date</th>
                    <th>Statut</th>
                </tr>
            </thead>
            <tbody>
                ${vulnerabilities.map(v => `
                    <tr class="vuln-row severity-${v.severity?.toLowerCase() || 'medium'}">
                        <td>${escapeHtml(v.type)}</td>
                        <td><span class="badge badge-${v.severity?.toLowerCase() || 'medium'}">${v.severity || 'N/A'}</span></td>
                        <td>${escapeHtml(v.target)}</td>
                        <td>${formatDate(v.date)}</td>
                        <td><span class="status-badge status-${v.status || 'open'}">${v.status || 'Ouvert'}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        ${vulnerabilities.length > 5 ? '<div class="view-all"><a href="/reports">Voir toutes les vulnérabilités →</a></div>' : ''}
    `;
}

// ========================================
// UTILITAIRES
// ========================================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('fr-FR');
}

function formatTimeAgo(timestamp) {
    const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
    
    if (seconds < 60) return `il y a ${seconds} seconde${seconds > 1 ? 's' : ''}`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `il y a ${minutes} minute${minutes > 1 ? 's' : ''}`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `il y a ${hours} heure${hours > 1 ? 's' : ''}`;
    const days = Math.floor(hours / 24);
    return `il y a ${days} jour${days > 1 ? 's' : ''}`;
}

function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-title">${getNotificationTitle(type)}</div>
        <div class="notification-message">${escapeHtml(message)}</div>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

function getNotificationTitle(type) {
    const titles = {
        success: '✅ Succès',
        error: '❌ Erreur',
        warning: '⚠️ Attention',
        info: 'ℹ️ Info'
    };
    return titles[type] || 'ℹ️ Info';
}

function getDefaultStats() {
    return {
        totalTargets: 0,
        totalAttacks: 0,
        vulnerabilitiesFound: 0,
        activeSessions: 0,
        criticalVulns: 0,
        highVulns: 0,
        mediumVulns: 0,
        lowVulns: 0,
        scanSuccessRate: '0%',
        avgScanTime: '0s',
        scanProgress: 0,
        coverageProgress: 0,
        multiAttacks: 0,
        aptOperations: 0,
        stealthScore: 0
    };
}

function getDefaultVulnerabilities() {
    return [];
}

function getDefaultActivities() {
    return [
        {
            type: 'info',
            title: 'Bienvenue sur RedForge',
            description: 'Plateforme prête à l\'emploi avec support multi-attaques et APT',
            timestamp: new Date().toISOString(),
            status: 'success'
        }
    ];
}

// ========================================
// EXPORTS
// ========================================

window.runAPTOperation = function(operationName) {
    // Cette fonction sera implémentée dans le module attacks.js
    if (typeof window.runAPTOperationFromDashboard === 'function') {
        window.runAPTOperationFromDashboard(operationName);
    } else {
        showNotification('Veuillez aller dans l\'onglet APT pour lancer une opération', 'info');
    }
};

window.viewAllAPTOperations = function() {
    const aptTab = document.querySelector('.tab[data-tab="apt"]');
    if (aptTab) {
        aptTab.click();
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        refreshDashboard,
        loadDashboardStats,
        loadRecentActivities,
        exportDashboardReport,
        exportJSONReport,
        handleScanCompleted,
        handleMultiAttackCompleted,
        handleAPTCompleted
    };
}