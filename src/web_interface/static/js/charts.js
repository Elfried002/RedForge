/**
 * RedForge - Graphiques et Visualisations Améliorés
 * Création de graphiques pour le tableau de bord avec support multi-attaques et APT
 * Version: 2.0.0
 */

// ========================================
// INITIALISATION DES GRAPHIQUES
// ========================================

let charts = {};
let chartUpdateInterval = null;
let realTimeData = {
    timestamp: [],
    attacksPerMinute: [],
    stealthEffectiveness: [],
    aptProgress: []
};

document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    startRealTimeUpdates();
});

async function initCharts() {
    // Charger les données
    const data = await loadChartData();
    
    // Créer les graphiques
    createVulnerabilityChart(data);
    createSeverityChart(data);
    createTimelineChart(data);
    createAttackDistributionChart(data);
    createPerformanceChart(data);
    createMultiAttackChart(data);
    createStealthEffectivenessChart(data);
    createAPTTimelineChart(data);
    createAttackSuccessRateChart(data);
    
    // Initialiser les contrôles d'export
    initExportControls();
}

async function loadChartData() {
    try {
        // Tenter de charger les données depuis l'API
        const response = await fetch('/api/reports/summary');
        if (response.ok) {
            return await response.json();
        }
        
        // Tenter de charger depuis les résultats de scan
        const scanResponse = await fetch('/api/results/latest');
        if (scanResponse.ok) {
            const scanData = await scanResponse.json();
            return transformScanDataToChartData(scanData);
        }
    } catch (error) {
        console.error('Erreur chargement données graphiques:', error);
    }
    
    // Données par défaut étendues
    return getDefaultChartData();
}

function getDefaultChartData() {
    return {
        vulnerabilities: {
            sql: 5, xss: 8, lfi: 3, csrf: 4, command: 2, ssrf: 3, xxe: 1, deserialization: 2, others: 6
        },
        severity: {
            critical: 2, high: 5, medium: 8, low: 12
        },
        timeline: [
            { date: '2024-01', count: 3, stealth: 65 },
            { date: '2024-02', count: 5, stealth: 72 },
            { date: '2024-03', count: 7, stealth: 78 },
            { date: '2024-04', count: 4, stealth: 85 },
            { date: '2024-05', count: 9, stealth: 88 },
            { date: '2024-06', count: 6, stealth: 92 }
        ],
        attacks: {
            completed: 45,
            running: 3,
            pending: 12,
            failed: 5,
            multiAttacks: 8,
            aptOperations: 3
        },
        attackCategories: {
            injection: 15,
            session: 8,
            cross_site: 12,
            authentication: 10,
            file_system: 7,
            infrastructure: 5,
            integrity: 6,
            advanced: 4,
            stealth: 3,
            apt: 5
        },
        stealthMetrics: {
            detectionRisk: 25,
            avgDelay: 1.8,
            torUsage: 40,
            proxyRotation: 35,
            successRate: 88
        },
        aptPhases: [
            { phase: 'Reconnaissance', duration: 120, success: 95 },
            { phase: 'Initial Access', duration: 180, success: 85 },
            { phase: 'Persistence', duration: 90, success: 90 },
            { phase: 'Privilege Escalation', duration: 150, success: 75 },
            { phase: 'Lateral Movement', duration: 200, success: 70 },
            { phase: 'Data Exfiltration', duration: 100, success: 88 }
        ],
        attackSuccessRate: {
            sql: 75, xss: 82, lfi: 68, csrf: 72, bruteforce: 45,
            file_upload: 60, command_injection: 55, ssrf: 65
        }
    };
}

function transformScanDataToChartData(scanData) {
    // Transformer les données de scan en format compatible avec les graphiques
    const vulnerabilities = {};
    const severity = { critical: 0, high: 0, medium: 0, low: 0 };
    
    if (scanData.results) {
        Object.values(scanData.results).forEach(result => {
            if (result.vulnerabilities) {
                result.vulnerabilities.forEach(vuln => {
                    const type = vuln.type?.toLowerCase() || 'others';
                    vulnerabilities[type] = (vulnerabilities[type] || 0) + 1;
                    
                    const sev = vuln.severity?.toLowerCase() || 'medium';
                    if (severity[sev] !== undefined) severity[sev]++;
                    else severity.medium++;
                });
            }
        });
    }
    
    return {
        vulnerabilities: vulnerabilities,
        severity: severity,
        timeline: getDefaultChartData().timeline,
        attacks: getDefaultChartData().attacks,
        attackCategories: getDefaultChartData().attackCategories,
        stealthMetrics: getDefaultChartData().stealthMetrics,
        aptPhases: getDefaultChartData().aptPhases,
        attackSuccessRate: getDefaultChartData().attackSuccessRate
    };
}

// ========================================
// GRAPHIQUE DES VULNÉRABILITÉS (amélioré)
// ========================================

function createVulnerabilityChart(data) {
    const canvas = document.getElementById('vulnerability-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const vulnerabilities = data.vulnerabilities || {};
    
    charts.vulnerability = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['SQLi', 'XSS', 'LFI/RFI', 'CSRF', 'Command', 'SSRF', 'XXE', 'Deserial.', 'Autres'],
            datasets: [{
                label: 'Nombre de vulnérabilités',
                data: [
                    vulnerabilities.sql || 0,
                    vulnerabilities.xss || 0,
                    vulnerabilities.lfi || 0,
                    vulnerabilities.csrf || 0,
                    vulnerabilities.command || 0,
                    vulnerabilities.ssrf || 0,
                    vulnerabilities.xxe || 0,
                    vulnerabilities.deserialization || 0,
                    vulnerabilities.others || 0
                ],
                backgroundColor: 'rgba(211, 47, 47, 0.8)',
                borderColor: '#fff',
                borderWidth: 2,
                borderRadius: 5,
                barPercentage: 0.7,
                categoryPercentage: 0.8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'top', labels: { font: { size: 12 } } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Nombre de vulnérabilités', font: { weight: 'bold' } },
                    grid: { color: 'rgba(0,0,0,0.1)' }
                },
                x: {
                    title: { display: true, text: 'Type de vulnérabilité', font: { weight: 'bold' } },
                    ticks: { rotation: -45, autoSkip: true, maxRotation: 45, minRotation: 45 }
                }
            }
        }
    });
}

// ========================================
// GRAPHIQUE DES SÉVÉRITÉS (amélioré)
// ========================================

function createSeverityChart(data) {
    const canvas = document.getElementById('severity-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const severity = data.severity || {};
    
    charts.severity = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Critique', 'Élevée', 'Moyenne', 'Basse'],
            datasets: [{
                data: [
                    severity.critical || 0,
                    severity.high || 0,
                    severity.medium || 0,
                    severity.low || 0
                ],
                backgroundColor: ['#7b1fa2', '#d32f2f', '#ff9800', '#4caf50'],
                borderColor: '#fff',
                borderWidth: 2,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'right', labels: { font: { size: 12, weight: 'bold' } } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const value = context.parsed;
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '60%'
        }
    });
}

// ========================================
// GRAPHIQUE D'ÉVOLUTION TEMPORELLE (avec mode furtif)
// ========================================

function createTimelineChart(data) {
    const canvas = document.getElementById('timeline-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const timeline = data.timeline || [];
    
    charts.timeline = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeline.map(t => t.date),
            datasets: [
                {
                    label: 'Vulnérabilités découvertes',
                    data: timeline.map(t => t.count),
                    borderColor: '#d32f2f',
                    backgroundColor: 'rgba(211, 47, 47, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#d32f2f',
                    pointBorderColor: '#fff',
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    yAxisID: 'y'
                },
                {
                    label: 'Efficacité furtive (%)',
                    data: timeline.map(t => t.stealth || 0),
                    borderColor: '#4caf50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#4caf50',
                    pointBorderColor: '#fff',
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'top' },
                tooltip: { mode: 'index', intersect: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Nombre de vulnérabilités', font: { weight: 'bold' } },
                    grid: { color: 'rgba(0,0,0,0.1)' }
                },
                y1: {
                    beginAtZero: true,
                    max: 100,
                    position: 'right',
                    title: { display: true, text: 'Efficacité furtive (%)', font: { weight: 'bold' } },
                    grid: { drawOnChartArea: false }
                },
                x: {
                    title: { display: true, text: 'Mois', font: { weight: 'bold' } }
                }
            }
        }
    });
}

// ========================================
// GRAPHIQUE DE DISTRIBUTION DES ATTAQUES (avec multi-attaques)
// ========================================

function createAttackDistributionChart(data) {
    const canvas = document.getElementById('attack-distribution-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const attacks = data.attacks || {};
    
    charts.attackDistribution = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: ['Terminées', 'En cours', 'En attente', 'Échouées', 'Multi-attaques', 'APT'],
            datasets: [{
                data: [
                    attacks.completed || 0,
                    attacks.running || 0,
                    attacks.pending || 0,
                    attacks.failed || 0,
                    attacks.multiAttacks || 0,
                    attacks.aptOperations || 0
                ],
                backgroundColor: [
                    '#4caf50', '#2196f3', '#ff9800', '#f44336', '#9c27b0', '#00bcd4'
                ],
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'right' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            return `${context.label}: ${value}`;
                        }
                    }
                }
            }
        }
    });
}

// ========================================
// GRAPHIQUE DES PERFORMANCES (amélioré)
// ========================================

function createPerformanceChart(data) {
    const canvas = document.getElementById('performance-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    charts.performance = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Rapidité', 'Précision', 'Couverture', 'Discrétion', 'Fiabilité', 'Furtivité', 'APT Readiness'],
            datasets: [
                {
                    label: 'Performance actuelle',
                    data: [85, 90, 75, 70, 95, 65, 80],
                    backgroundColor: 'rgba(211, 47, 47, 0.2)',
                    borderColor: '#d32f2f',
                    borderWidth: 2,
                    pointBackgroundColor: '#d32f2f',
                    pointBorderColor: '#fff',
                    pointRadius: 5
                },
                {
                    label: 'Objectif',
                    data: [95, 95, 85, 90, 98, 90, 95],
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderColor: '#4caf50',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointBackgroundColor: '#4caf50',
                    pointBorderColor: '#fff',
                    pointRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { stepSize: 20, backdropColor: 'transparent' },
                    grid: { color: 'rgba(0,0,0,0.1)' }
                }
            },
            plugins: {
                tooltip: { callbacks: { label: (context) => `${context.dataset.label}: ${context.parsed}%` } }
            }
        }
    });
}

// ========================================
// NOUVEAU: GRAPHIQUE DES ATTAQUES MULTIPLES
// ========================================

function createMultiAttackChart(data) {
    const canvas = document.getElementById('multi-attack-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const categories = data.attackCategories || {};
    
    charts.multiAttack = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Injection', 'Session', 'Cross-Site', 'Auth', 'File System', 'Infra', 'Integrity', 'Advanced', 'Stealth', 'APT'],
            datasets: [{
                label: 'Nombre d\'attaques par catégorie',
                data: [
                    categories.injection || 0,
                    categories.session || 0,
                    categories.cross_site || 0,
                    categories.authentication || 0,
                    categories.file_system || 0,
                    categories.infrastructure || 0,
                    categories.integrity || 0,
                    categories.advanced || 0,
                    categories.stealth || 0,
                    categories.apt || 0
                ],
                backgroundColor: 'rgba(156, 39, 176, 0.8)',
                borderColor: '#fff',
                borderWidth: 1,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'top' },
                tooltip: { callbacks: { label: (context) => `${context.dataset.label}: ${context.parsed.y}` } }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Nombre d\'attaques' } },
                x: { ticks: { rotation: -45, autoSkip: true } }
            }
        }
    });
}

// ========================================
// NOUVEAU: GRAPHIQUE D'EFFICACITÉ FURTIVE
// ========================================

function createStealthEffectivenessChart(data) {
    const canvas = document.getElementById('stealth-effectiveness-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const stealth = data.stealthMetrics || {};
    
    charts.stealthEffectiveness = new Chart(ctx, {
        type: 'gauge',
        data: {
            datasets: [{
                data: [stealth.successRate || 88],
                backgroundColor: ['#4caf50', '#ff9800', '#f44336'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: { callbacks: { label: () => `Taux de succès: ${stealth.successRate || 88}%` } }
            },
            cutout: '70%',
            rotation: -90,
            circumference: 180
        }
    });
    
    // Créer un graphique radar pour les métriques furtives
    const radarCanvas = document.getElementById('stealth-metrics-radar');
    if (radarCanvas) {
        const radarCtx = radarCanvas.getContext('2d');
        charts.stealthMetrics = new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: ['Délais aléatoires', 'User-Agents', 'Rotation proxies', 'Utilisation TOR', 'Mimétisme', 'Low & Slow'],
                datasets: [{
                    label: 'Configuration actuelle',
                    data: [
                        stealth.avgDelay ? Math.min(100, stealth.avgDelay * 20) : 70,
                        stealth.randomUserAgents ? 90 : 30,
                        stealth.proxyRotation || 35,
                        stealth.torUsage || 40,
                        stealth.mimicHuman ? 85 : 20,
                        60
                    ],
                    backgroundColor: 'rgba(76, 175, 80, 0.2)',
                    borderColor: '#4caf50',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                scales: { r: { beginAtZero: true, max: 100, ticks: { stepSize: 20 } } }
            }
        });
    }
}

// ========================================
// NOUVEAU: GRAPHIQUE DE TIMELINE APT
// ========================================

function createAPTTimelineChart(data) {
    const canvas = document.getElementById('apt-timeline-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const aptPhases = data.aptPhases || [];
    
    charts.aptTimeline = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: aptPhases.map(p => p.phase),
            datasets: [
                {
                    label: 'Durée (secondes)',
                    data: aptPhases.map(p => p.duration),
                    backgroundColor: 'rgba(0, 188, 212, 0.8)',
                    borderColor: '#fff',
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: 'Taux de succès (%)',
                    data: aptPhases.map(p => p.success),
                    backgroundColor: 'rgba(76, 175, 80, 0.8)',
                    borderColor: '#fff',
                    borderWidth: 1,
                    type: 'line',
                    yAxisID: 'y1'
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
                    title: { display: true, text: 'Durée (secondes)', font: { weight: 'bold' } }
                },
                y1: {
                    beginAtZero: true,
                    max: 100,
                    position: 'right',
                    title: { display: true, text: 'Taux de succès (%)', font: { weight: 'bold' } },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
}

// ========================================
// NOUVEAU: GRAPHIQUE DE TAUX DE SUCCÈS PAR ATTAQUE
// ========================================

function createAttackSuccessRateChart(data) {
    const canvas = document.getElementById('attack-success-rate-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const successRates = data.attackSuccessRate || {};
    
    charts.attackSuccessRate = new Chart(ctx, {
        type: 'horizontalBar',
        data: {
            labels: ['SQLi', 'XSS', 'LFI/RFI', 'CSRF', 'Force brute', 'Upload', 'Command injection', 'SSRF'],
            datasets: [{
                label: 'Taux de succès (%)',
                data: [
                    successRates.sql || 75,
                    successRates.xss || 82,
                    successRates.lfi || 68,
                    successRates.csrf || 72,
                    successRates.bruteforce || 45,
                    successRates.file_upload || 60,
                    successRates.command_injection || 55,
                    successRates.ssrf || 65
                ],
                backgroundColor: (context) => {
                    const value = context.raw;
                    if (value >= 80) return '#4caf50';
                    if (value >= 60) return '#ff9800';
                    return '#f44336';
                },
                borderColor: '#fff',
                borderWidth: 1,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: (context) => `Taux de succès: ${context.raw}%` } }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: 'Taux de succès (%)', font: { weight: 'bold' } }
                }
            }
        }
    });
}

// ========================================
// MISE À JOUR EN TEMPS RÉEL
// ========================================

function startRealTimeUpdates() {
    if (chartUpdateInterval) clearInterval(chartUpdateInterval);
    
    chartUpdateInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/status/realtime');
            if (response.ok) {
                const realTimeStats = await response.json();
                updateRealTimeCharts(realTimeStats);
            }
        } catch (error) {
            console.debug('Real-time update error:', error);
        }
    }, 5000);
}

function updateRealTimeCharts(stats) {
    // Mettre à jour les données en temps réel
    const now = new Date();
    realTimeData.timestamp.push(now.toLocaleTimeString());
    realTimeData.attacksPerMinute.push(stats.attacksPerMinute || 0);
    realTimeData.stealthEffectiveness.push(stats.stealthEffectiveness || 0);
    
    // Limiter à 20 points
    if (realTimeData.timestamp.length > 20) {
        realTimeData.timestamp.shift();
        realTimeData.attacksPerMinute.shift();
        realTimeData.stealthEffectiveness.shift();
    }
    
    // Mettre à jour le graphique temps réel si existant
    if (charts.realtime) {
        charts.realtime.data.labels = realTimeData.timestamp;
        charts.realtime.data.datasets[0].data = realTimeData.attacksPerMinute;
        charts.realtime.update();
    }
}

// ========================================
// EXPORT DES GRAPHIQUES
// ========================================

function initExportControls() {
    const exportBtn = document.getElementById('export-charts');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => exportAllCharts());
    }
    
    const formatSelect = document.getElementById('export-format');
    if (formatSelect) {
        formatSelect.addEventListener('change', (e) => {
            window.exportFormat = e.target.value;
        });
    }
}

async function exportChartAsImage(chartId, format = 'png') {
    const canvas = document.getElementById(chartId);
    if (!canvas) {
        console.warn(`Canvas ${chartId} not found`);
        return;
    }
    
    const link = document.createElement('a');
    link.download = `redforge_chart_${chartId}_${new Date().toISOString().slice(0, 19)}.${format}`;
    link.href = canvas.toDataURL(`image/${format}`);
    link.click();
}

async function exportAllCharts() {
    const chartIds = [
        'vulnerability-chart',
        'severity-chart', 
        'timeline-chart',
        'attack-distribution-chart',
        'performance-chart',
        'multi-attack-chart',
        'stealth-effectiveness-chart',
        'apt-timeline-chart',
        'attack-success-rate-chart'
    ];
    
    const format = window.exportFormat || 'png';
    
    for (const id of chartIds) {
        await exportChartAsImage(id, format);
        // Petit délai entre les exports pour éviter les problèmes
        await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    showNotification('Tous les graphiques ont été exportés avec succès', 'success');
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-title">${type === 'success' ? '✅ Succès' : 'ℹ️ Info'}</div>
        <div class="notification-message">${message}</div>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// ========================================
// MISE À JOUR DES GRAPHIQUES (améliorée)
// ========================================

function updateCharts(newData) {
    // Mettre à jour le graphique des vulnérabilités
    if (charts.vulnerability && newData.vulnerabilities) {
        const vulns = newData.vulnerabilities;
        charts.vulnerability.data.datasets[0].data = [
            vulns.sql || 0, vulns.xss || 0, vulns.lfi || 0,
            vulns.csrf || 0, vulns.command || 0, vulns.ssrf || 0,
            vulns.xxe || 0, vulns.deserialization || 0, vulns.others || 0
        ];
        charts.vulnerability.update();
    }
    
    // Mettre à jour le graphique des sévérités
    if (charts.severity && newData.severity) {
        const sev = newData.severity;
        charts.severity.data.datasets[0].data = [
            sev.critical || 0, sev.high || 0, sev.medium || 0, sev.low || 0
        ];
        charts.severity.update();
    }
    
    // Mettre à jour le graphique temporel
    if (charts.timeline && newData.timeline) {
        charts.timeline.data.labels = newData.timeline.map(t => t.date);
        charts.timeline.data.datasets[0].data = newData.timeline.map(t => t.count);
        if (charts.timeline.data.datasets[1]) {
            charts.timeline.data.datasets[1].data = newData.timeline.map(t => t.stealth || 0);
        }
        charts.timeline.update();
    }
    
    // Mettre à jour le graphique des performances
    if (charts.performance && newData.performance) {
        charts.performance.data.datasets[0].data = newData.performance;
        charts.performance.update();
    }
    
    console.log('Graphiques mis à jour avec succès');
}

// ========================================
// EXPORTS
// ========================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        updateCharts,
        exportChartAsImage,
        exportAllCharts,
        initCharts
    };
}