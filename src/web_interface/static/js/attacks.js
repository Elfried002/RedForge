/**
 * RedForge - Gestion des Attaques Améliorée
 * Interface pour lancer et monitorer les attaques simples, multiples et APT
 * Version: 2.0.0
 */

// ========================================
// ÉTAT DES ATTAQUES
// ========================================

let activeAttacks = {};
let attackCategories = {};
let attackResults = {};
let activeMultiAttacks = {};
let activeAPTOperations = {};
let currentStealthLevel = 'medium';
let socket = null;

// WebSocket connection
function initWebSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('WebSocket connecté');
        showNotification('Connecté au serveur', 'success');
    });
    
    socket.on('attack_progress', (data) => {
        updateAttackProgress(data.task_id, data.current_attack, data.progress);
    });
    
    socket.on('multi_attack_completed', (data) => {
        onMultiAttackCompleted(data.task_id, data);
    });
    
    socket.on('apt_started', (data) => {
        onAPTStarted(data);
    });
    
    socket.on('apt_phase_start', (data) => {
        onAPTPhaseStart(data);
    });
    
    socket.on('apt_phase_complete', (data) => {
        onAPTPhaseComplete(data);
    });
    
    socket.on('apt_completed', (data) => {
        onAPTCompleted(data);
    });
    
    socket.on('scan_completed', (data) => {
        onScanCompleted(data);
    });
}

// ========================================
// CATÉGORIES D'ATTAQUES ÉTENDUES
// ========================================

const ATTACK_CATEGORIES = {
    injection: {
        name: 'Injections',
        icon: '💉',
        description: 'Attaques par injection de code',
        attacks: ['sql', 'nosql', 'command', 'ldap', 'xpath', 'html', 'template']
    },
    session: {
        name: 'Sessions',
        icon: '🔐',
        description: 'Attaques sur les sessions utilisateur',
        attacks: ['hijacking', 'fixation', 'cookie', 'jwt', 'oauth']
    },
    cross_site: {
        name: 'Cross-Site',
        icon: '🌐',
        description: 'Attaques cross-site',
        attacks: ['xss', 'csrf', 'clickjacking', 'cors', 'postmessage']
    },
    authentication: {
        name: 'Authentification',
        icon: '🔑',
        description: 'Attaques sur l\'authentification',
        attacks: ['bruteforce', 'credential_stuffing', 'password_spraying', 'mfa_bypass', 'priv_esc', 'race_condition']
    },
    file_system: {
        name: 'Système de fichiers',
        icon: '📁',
        description: 'Attaques sur le système de fichiers',
        attacks: ['lfi_rfi', 'file_upload', 'dir_traversal', 'buffer_overflow', 'path_normalization', 'zip_slip']
    },
    infrastructure: {
        name: 'Infrastructure',
        icon: '🏗️',
        description: 'Attaques sur l\'infrastructure',
        attacks: ['waf_bypass', 'misconfig', 'load_balancer', 'host_header', 'cache_poisoning']
    },
    integrity: {
        name: 'Intégrité',
        icon: '🔒',
        description: 'Attaques sur l\'intégrité des données',
        attacks: ['data_tampering', 'info_leakage', 'mitm', 'param_pollution', 'business_logic']
    },
    advanced: {
        name: 'Avancées',
        icon: '🚀',
        description: 'Attaques avancées',
        attacks: ['api', 'graphql', 'websocket', 'deserialization', 'browser', 'microservices', 'chaining']
    },
    stealth: {
        name: 'Mode Furtif',
        icon: '🕵️',
        description: 'Attaques en mode furtif',
        attacks: ['slow_loris', 'low_and_slow', 'distributed', 'tor_routed']
    },
    apt: {
        name: 'APT',
        icon: '🎯',
        description: 'Opérations APT avancées',
        attacks: ['recon', 'persistence', 'lateral_movement', 'exfiltration']
    }
};

// Noms d'affichage des attaques
const ATTACK_NAMES = {
    sql: 'Injection SQL',
    nosql: 'Injection NoSQL',
    command: 'Injection de commandes',
    ldap: 'Injection LDAP',
    xpath: 'Injection XPath',
    html: 'Injection HTML',
    template: 'Injection de templates',
    hijacking: 'Détournement de session',
    fixation: 'Fixation de session',
    cookie: 'Manipulation de cookies',
    jwt: 'Attaques JWT',
    oauth: 'Attaques OAuth',
    xss: 'Cross-Site Scripting',
    csrf: 'Cross-Site Request Forgery',
    clickjacking: 'Clickjacking',
    cors: 'CORS',
    postmessage: 'PostMessage',
    bruteforce: 'Force brute',
    credential_stuffing: 'Credential Stuffing',
    password_spraying: 'Password Spraying',
    mfa_bypass: 'Contournement MFA',
    priv_esc: 'Élévation de privilèges',
    race_condition: 'Race condition',
    lfi_rfi: 'LFI/RFI',
    file_upload: 'Upload de fichiers',
    dir_traversal: 'Directory traversal',
    buffer_overflow: 'Buffer overflow',
    path_normalization: 'Normalisation de chemin',
    zip_slip: 'Zip Slip',
    waf_bypass: 'Contournement WAF',
    misconfig: 'Mauvaises configurations',
    load_balancer: 'Load balancer',
    host_header: 'Host header',
    cache_poisoning: 'Empoisonnement de cache',
    data_tampering: 'Altération de données',
    info_leakage: 'Fuites d\'informations',
    mitm: 'Man-in-the-Middle',
    param_pollution: 'Pollution de paramètres',
    business_logic: 'Logique métier',
    api: 'API',
    graphql: 'GraphQL',
    websocket: 'WebSocket',
    deserialization: 'Désérialisation',
    browser: 'Exploitation navigateur',
    microservices: 'Microservices',
    chaining: 'Chaînage d\'attaques',
    slow_loris: 'Slow Loris',
    low_and_slow: 'Low and Slow',
    distributed: 'Attaque distribuée',
    tor_routed: 'Route via TOR',
    recon: 'Reconnaissance',
    persistence: 'Persistance',
    lateral_movement: 'Mouvement latéral',
    exfiltration: 'Exfiltration'
};

// ========================================
// INITIALISATION
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    initWebSocket();
    initAttacksPage();
    loadAttackCategories();
    bindAttackEvents();
    loadStealthProfiles();
    loadAPTOperations();
});

function initAttacksPage() {
    const container = document.querySelector('.attacks-container');
    if (!container) return;
    
    container.innerHTML = `
        <div class="attacks-header">
            <h1>🎯 Gestion des Attaques</h1>
            <p>Sélectionnez et lancez des attaques simples, multiples ou des opérations APT</p>
        </div>
        
        <!-- Onglets -->
        <div class="tabs">
            <button class="tab active" data-tab="simple">🔄 Attaques Simples</button>
            <button class="tab" data-tab="multi">📚 Attaques Multiples</button>
            <button class="tab" data-tab="apt">🎯 Opérations APT</button>
            <button class="tab" data-tab="stealth">🕵️ Mode Furtif</button>
        </div>
        
        <!-- Tab Simple -->
        <div class="tab-content active" id="tab-simple">
            ${getSimpleAttacksHTML()}
        </div>
        
        <!-- Tab Multi -->
        <div class="tab-content" id="tab-multi">
            ${getMultiAttacksHTML()}
        </div>
        
        <!-- Tab APT -->
        <div class="tab-content" id="tab-apt">
            ${getAPTHTML()}
        </div>
        
        <!-- Tab Stealth -->
        <div class="tab-content" id="tab-stealth">
            ${getStealthHTML()}
        </div>
        
        <!-- Sections communes -->
        <div class="active-attacks-section">
            <h2>⚡ Attaques en cours</h2>
            <div id="active-attacks-list" class="active-attacks-list"></div>
        </div>
        
        <div class="results-section">
            <h2>📊 Résultats</h2>
            <div id="attack-results" class="attack-results"></div>
        </div>
    `;
    
    loadTargets();
    bindTabEvents();
}

function getSimpleAttacksHTML() {
    return `
        <div class="attacks-controls">
            <div class="target-selector">
                <label>Cible:</label>
                <select id="attack-target" class="form-select">
                    <option value="">Sélectionner une cible</option>
                </select>
            </div>
            <div class="attack-options">
                <label>Niveau:</label>
                <select id="attack-level" class="form-select">
                    <option value="1">Bas (1)</option>
                    <option value="2" selected>Moyen (2)</option>
                    <option value="3">Élevé (3)</option>
                    <option value="4">Maximum (4)</option>
                </select>
            </div>
            <button id="run-selected-attacks" class="btn btn-primary" disabled>
                🚀 Lancer les attaques sélectionnées
            </button>
        </div>
        
        <div class="attacks-grid" id="attacks-grid"></div>
    `;
}

function getMultiAttacksHTML() {
    return `
        <div class="multi-attack-panel">
            <div class="attacks-controls">
                <div class="target-selector">
                    <label>Cible:</label>
                    <select id="multi-target" class="form-select">
                        <option value="">Sélectionner une cible</option>
                    </select>
                </div>
                <div class="execution-mode">
                    <label>Mode d'exécution:</label>
                    <select id="execution-mode" class="form-select">
                        <option value="sequential">Séquentiel</option>
                        <option value="parallel">Parallèle</option>
                    </select>
                </div>
                <div class="stealth-selector">
                    <label>Niveau furtif:</label>
                    <select id="multi-stealth-level" class="form-select">
                        <option value="low">Low</option>
                        <option value="medium" selected>Medium</option>
                        <option value="high">High</option>
                        <option value="paranoid">Paranoid</option>
                    </select>
                </div>
                <button id="run-multi-attacks" class="btn btn-primary" disabled>
                    🚀 Lancer les attaques multiples
                </button>
            </div>
            
            <div class="attacks-selection">
                <div class="selection-header">
                    <h3>Sélection des attaques</h3>
                    <div class="selection-actions">
                        <button id="select-all-attacks" class="btn btn-sm btn-secondary">Tout sélectionner</button>
                        <button id="deselect-all-attacks" class="btn btn-sm btn-secondary">Tout désélectionner</button>
                    </div>
                </div>
                <div class="attacks-grid multi-attacks-grid" id="multi-attacks-grid"></div>
            </div>
        </div>
    `;
}

function getAPTHTML() {
    return `
        <div class="apt-panel">
            <div class="attacks-controls">
                <div class="target-selector">
                    <label>Cible:</label>
                    <select id="apt-target" class="form-select">
                        <option value="">Sélectionner une cible</option>
                    </select>
                </div>
                <div class="operation-selector">
                    <label>Opération APT:</label>
                    <select id="apt-operation" class="form-select">
                        <option value="">Sélectionner une opération</option>
                        <option value="recon_to_exfil">Reconnaissance → Exfiltration</option>
                        <option value="web_app_compromise">Compromission d'Application Web</option>
                    </select>
                </div>
                <div class="stealth-selector">
                    <label>Niveau furtif:</label>
                    <select id="apt-stealth-level" class="form-select">
                        <option value="medium">Medium</option>
                        <option value="high" selected>High</option>
                        <option value="paranoid">Paranoid</option>
                    </select>
                </div>
                <button id="run-apt-operation" class="btn btn-danger" disabled>
                    🎯 Lancer l'opération APT
                </button>
            </div>
            
            <div class="apt-operations-list" id="apt-operations-list">
                <div class="loading-spinner"></div>
            </div>
            
            <div class="apt-timeline" id="apt-timeline" style="display: none;">
                <h3>📅 Timeline de l'opération</h3>
                <div class="timeline-container"></div>
            </div>
        </div>
    `;
}

function getStealthHTML() {
    return `
        <div class="stealth-config-panel">
            <h3>🕵️ Configuration du mode furtif</h3>
            
            <div class="stealth-level-selector">
                <div class="stealth-level-btn stealth-level-low" data-level="low">
                    🟢 Low
                    <small>Détection facile</small>
                </div>
                <div class="stealth-level-btn stealth-level-medium selected" data-level="medium">
                    🟡 Medium
                    <small>Équilibre</small>
                </div>
                <div class="stealth-level-btn stealth-level-high" data-level="high">
                    🔴 High
                    <small>Difficile à détecter</small>
                </div>
                <div class="stealth-level-btn stealth-level-paranoid" data-level="paranoid">
                    🟣 Paranoid
                    <small>Maximum</small>
                </div>
            </div>
            
            <div class="stealth-options">
                <div class="form-group">
                    <label>Délai entre les requêtes (secondes)</label>
                    <input type="range" id="delay-range" min="0.1" max="10" step="0.1" value="1.5">
                    <span id="delay-value" class="delay-value">1.5s</span>
                </div>
                
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="random-user-agents" checked>
                        User-Agents aléatoires
                    </label>
                </div>
                
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="use-tor">
                        Utiliser TOR
                    </label>
                </div>
                
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="rotate-proxies">
                        Rotation de proxies
                    </label>
                </div>
                
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="mimic-human" checked>
                        Mimétisme humain
                    </label>
                </div>
            </div>
            
            <button id="test-stealth-config" class="btn btn-secondary">
                🧪 Tester la configuration
            </button>
            
            <div id="stealth-test-results" class="stealth-test-results" style="display: none;"></div>
        </div>
    `;
}

function bindTabEvents() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            
            // Update active tab
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Update active content
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(`tab-${tabId}`).classList.add('active');
            
            // Load specific data
            if (tabId === 'multi') {
                loadMultiAttacksGrid();
                loadTargetsForSelect('multi-target');
            } else if (tabId === 'apt') {
                loadAPTOperationsList();
                loadTargetsForSelect('apt-target');
            } else if (tabId === 'simple') {
                loadTargets();
            }
        });
    });
}

function loadMultiAttacksGrid() {
    const grid = document.getElementById('multi-attacks-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    for (const [key, category] of Object.entries(ATTACK_CATEGORIES)) {
        const categoryDiv = createMultiCategoryDiv(key, category);
        grid.appendChild(categoryDiv);
    }
    
    bindMultiAttackEvents();
}

function createMultiCategoryDiv(categoryKey, category) {
    const div = document.createElement('div');
    div.className = 'attack-category-card';
    div.innerHTML = `
        <div class="card-header">
            <span class="attack-icon">${category.icon}</span>
            <h4>${category.name}</h4>
            <label class="select-all">
                <input type="checkbox" class="select-all-category-multi" data-category="${categoryKey}">
                <span>Tout</span>
            </label>
        </div>
        <div class="card-body">
            ${category.attacks.map(attack => `
                <label class="attack-item">
                    <input type="checkbox" class="multi-attack-checkbox" 
                           data-category="${categoryKey}" 
                           data-attack="${attack}">
                    <span>${ATTACK_NAMES[attack] || attack}</span>
                </label>
            `).join('')}
        </div>
    `;
    
    return div;
}

function bindMultiAttackEvents() {
    // Select all by category
    document.querySelectorAll('.select-all-category-multi').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const category = this.dataset.category;
            const checkboxes = document.querySelectorAll(`.multi-attack-checkbox[data-category="${category}"]`);
            checkboxes.forEach(cb => cb.checked = this.checked);
            updateMultiRunButton();
        });
    });
    
    // Individual selection
    document.addEventListener('change', function(e) {
        if (e.target.classList && e.target.classList.contains('multi-attack-checkbox')) {
            updateMultiRunButton();
        }
    });
    
    // Select all / deselect all
    const selectAllBtn = document.getElementById('select-all-attacks');
    const deselectAllBtn = document.getElementById('deselect-all-attacks');
    
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            document.querySelectorAll('.multi-attack-checkbox').forEach(cb => cb.checked = true);
            updateMultiRunButton();
        });
    }
    
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', () => {
            document.querySelectorAll('.multi-attack-checkbox').forEach(cb => cb.checked = false);
            updateMultiRunButton();
        });
    }
    
    // Run multi attacks
    const runBtn = document.getElementById('run-multi-attacks');
    if (runBtn) {
        runBtn.addEventListener('click', runMultiAttacks);
    }
}

function updateMultiRunButton() {
    const runBtn = document.getElementById('run-multi-attacks');
    const targetSelect = document.getElementById('multi-target');
    const selectedAttacks = document.querySelectorAll('.multi-attack-checkbox:checked');
    
    if (runBtn) {
        runBtn.disabled = !(targetSelect && targetSelect.value && selectedAttacks.length > 0);
    }
}

async function runMultiAttacks() {
    const target = document.getElementById('multi-target').value;
    const executionMode = document.getElementById('execution-mode').value;
    const stealthLevel = document.getElementById('multi-stealth-level').value;
    const selectedAttacks = Array.from(document.querySelectorAll('.multi-attack-checkbox:checked')).map(cb => ({
        category: cb.dataset.category,
        type: cb.dataset.attack,
        options: {}
    }));
    
    if (!target || selectedAttacks.length === 0) return;
    
    const runBtn = document.getElementById('run-multi-attacks');
    runBtn.disabled = true;
    runBtn.textContent = '⏳ Lancement...';
    
    try {
        const response = await fetch('/api/multi-attack', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target: target,
                attacks: selectedAttacks,
                execution_mode: executionMode,
                stealth_level: stealthLevel
            })
        });
        
        const result = await response.json();
        
        if (result.task_id) {
            showNotification(`Attaques multiples lancées (${selectedAttacks.length} attaques)`, 'success');
            addMultiAttackToActive(result.task_id, target, selectedAttacks.length);
        } else {
            showNotification('Erreur lors du lancement', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur réseau', 'error');
    } finally {
        runBtn.disabled = false;
        runBtn.textContent = '🚀 Lancer les attaques multiples';
    }
}

function addMultiAttackToActive(taskId, target, attackCount) {
    const container = document.getElementById('active-attacks-list');
    if (!container) return;
    
    const attackElement = document.createElement('div');
    attackElement.id = taskId;
    attackElement.className = 'active-attack-item multi-attack';
    attackElement.innerHTML = `
        <div class="attack-info">
            <span class="attack-status running">⏳</span>
            <span>Multi-Attack: ${target} (${attackCount} attaques)</span>
        </div>
        <div class="attack-progress">
            <div class="progress">
                <div class="progress-bar" style="width: 0%"></div>
            </div>
        </div>
        <div class="current-attack"></div>
    `;
    
    container.appendChild(attackElement);
    activeMultiAttacks[taskId] = { attackElement };
}

async function runAPTOperation() {
    const target = document.getElementById('apt-target').value;
    const operationId = document.getElementById('apt-operation').value;
    const stealthLevel = document.getElementById('apt-stealth-level').value;
    
    if (!target || !operationId) return;
    
    const runBtn = document.getElementById('run-apt-operation');
    runBtn.disabled = true;
    runBtn.textContent = '⏳ Démarrage de l\'opération APT...';
    
    try {
        const response = await fetch('/api/apt/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target: target,
                operation_id: operationId,
                stealth_level: stealthLevel
            })
        });
        
        const result = await response.json();
        
        if (result.task_id) {
            showNotification(`Opération APT lancée: ${operationId}`, 'warning');
            showAPTTimeline(result.task_id);
        } else {
            showNotification('Erreur lors du lancement', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur réseau', 'error');
    } finally {
        runBtn.disabled = false;
        runBtn.textContent = '🎯 Lancer l\'opération APT';
    }
}

function showAPTTimeline(taskId) {
    const timeline = document.getElementById('apt-timeline');
    if (timeline) {
        timeline.style.display = 'block';
        timeline.dataset.taskId = taskId;
    }
}

function updateAttackProgress(taskId, currentAttack, progress) {
    const element = document.getElementById(taskId);
    if (element) {
        const progressBar = element.querySelector('.progress-bar');
        if (progressBar) progressBar.style.width = `${progress}%`;
        
        const currentAttackDiv = element.querySelector('.current-attack');
        if (currentAttackDiv && currentAttack) {
            currentAttackDiv.textContent = `En cours: ${currentAttack}`;
        }
    }
}

function onMultiAttackCompleted(taskId, data) {
    const element = document.getElementById(taskId);
    if (element) {
        const statusSpan = element.querySelector('.attack-status');
        if (statusSpan) {
            statusSpan.textContent = '✅';
            statusSpan.classList.remove('running');
        }
        
        setTimeout(() => {
            element.remove();
            delete activeMultiAttacks[taskId];
        }, 3000);
    }
    
    showNotification(`Multi-attaque terminée: ${data.successful}/${data.total_attacks} réussies`, 'info');
}

function onAPTStarted(data) {
    showNotification(`Opération APT démarrée: ${data.operation_name}`, 'warning');
}

function onAPTPhaseStart(data) {
    console.log(`Phase APT démarrée: ${data.phase}`);
    updateAPTTimeline(data.phase, 'running');
}

function onAPTPhaseComplete(data) {
    updateAPTTimeline(data.phase, 'completed', data.success_rate);
    showNotification(`Phase APT terminée: ${data.phase} (${data.success_rate}% succès)`, 'info');
}

function onAPTCompleted(data) {
    showNotification(`Opération APT complétée! Succès global: ${data.overall_success}%`, 'success');
    
    const timeline = document.getElementById('apt-timeline');
    if (timeline) {
        setTimeout(() => {
            timeline.style.display = 'none';
        }, 5000);
    }
}

function updateAPTTimeline(phase, status, successRate = null) {
    const timelineContainer = document.querySelector('.timeline-container');
    if (!timelineContainer) return;
    
    let phaseElement = document.querySelector(`.timeline-item[data-phase="${phase}"]`);
    if (!phaseElement) {
        phaseElement = document.createElement('div');
        phaseElement.className = 'timeline-item';
        phaseElement.setAttribute('data-phase', phase);
        phaseElement.innerHTML = `
            <div class="timeline-marker"></div>
            <div class="timeline-content">
                <strong>${phase}</strong>
                <div class="timeline-status"></div>
            </div>
        `;
        timelineContainer.appendChild(phaseElement);
    }
    
    const statusDiv = phaseElement.querySelector('.timeline-status');
    if (status === 'running') {
        statusDiv.innerHTML = '<span class="badge badge-info">En cours...</span>';
    } else if (status === 'completed') {
        statusDiv.innerHTML = `<span class="badge badge-${successRate > 70 ? 'success' : 'warning'}">Terminé (${successRate}%)</span>`;
    }
}

function loadStealthProfiles() {
    // Stealth level selection
    document.querySelectorAll('.stealth-level-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const level = this.dataset.level;
            currentStealthLevel = level;
            
            // Update UI
            document.querySelectorAll('.stealth-level-btn').forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');
            
            // Update config based on level
            updateStealthConfig(level);
        });
    });
    
    // Delay slider
    const delayRange = document.getElementById('delay-range');
    const delayValue = document.getElementById('delay-value');
    
    if (delayRange && delayValue) {
        delayRange.addEventListener('input', function() {
            delayValue.textContent = `${this.value}s`;
        });
    }
    
    // Test button
    const testBtn = document.getElementById('test-stealth-config');
    if (testBtn) {
        testBtn.addEventListener('click', testStealthConfig);
    }
}

function updateStealthConfig(level) {
    const configs = {
        low: { delay: 0.5, jitter: 0.1, tor: false, proxies: false },
        medium: { delay: 1.5, jitter: 0.3, tor: false, proxies: false },
        high: { delay: 3.0, jitter: 0.5, tor: true, proxies: false },
        paranoid: { delay: 5.0, jitter: 0.7, tor: true, proxies: true }
    };
    
    const config = configs[level];
    if (config) {
        const delayRange = document.getElementById('delay-range');
        const torCheckbox = document.getElementById('use-tor');
        const proxiesCheckbox = document.getElementById('rotate-proxies');
        
        if (delayRange) delayRange.value = config.delay;
        if (torCheckbox) torCheckbox.checked = config.tor;
        if (proxiesCheckbox) proxiesCheckbox.checked = config.proxies;
        
        const delayValue = document.getElementById('delay-value');
        if (delayValue) delayValue.textContent = `${config.delay}s`;
    }
}

async function testStealthConfig() {
    const target = document.getElementById('attack-target')?.value;
    if (!target) {
        showNotification('Veuillez sélectionner une cible d\'abord', 'warning');
        return;
    }
    
    const config = {
        delay_between_requests: parseFloat(document.getElementById('delay-range')?.value || 1.5),
        random_user_agents: document.getElementById('random-user-agents')?.checked || false,
        use_tor: document.getElementById('use-tor')?.checked || false,
        rotate_proxies: document.getElementById('rotate-proxies')?.checked || false,
        mimic_human_behavior: document.getElementById('mimic-human')?.checked || false
    };
    
    const testBtn = document.getElementById('test-stealth-config');
    testBtn.disabled = true;
    testBtn.textContent = '⏳ Test en cours...';
    
    try {
        const response = await fetch('/api/stealth/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target: target, config: config })
        });
        
        const results = await response.json();
        displayStealthTestResults(results);
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur lors du test', 'error');
    } finally {
        testBtn.disabled = false;
        testBtn.textContent = '🧪 Tester la configuration';
    }
}

function displayStealthTestResults(results) {
    const container = document.getElementById('stealth-test-results');
    if (!container) return;
    
    const riskColors = {
        low: '#4caf50',
        medium: '#ff9800',
        high: '#f44336'
    };
    
    container.style.display = 'block';
    container.innerHTML = `
        <h4>Résultats du test</h4>
        <div class="test-result">
            <p><strong>Risque de détection:</strong> 
                <span style="color: ${riskColors[results.detection_risk]}">${results.detection_risk.toUpperCase()}</span>
            </p>
            <p><strong>Taux de succès estimé:</strong> ${results.success_rate}%</p>
            <p><strong>Délais testés:</strong> ${results.delays_tested.map(d => d.toFixed(2) + 's').join(', ')}</p>
            ${results.recommendations.length > 0 ? `
                <div class="recommendations">
                    <strong>Recommandations:</strong>
                    <ul>
                        ${results.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
    
    setTimeout(() => {
        container.style.opacity = '0';
        setTimeout(() => {
            container.style.display = 'none';
            container.style.opacity = '1';
        }, 3000);
    }, 10000);
}

function loadAPTOperations() {
    const select = document.getElementById('apt-operation');
    if (!select) return;
    
    fetch('/api/apt/operations')
        .then(res => res.json())
        .then(data => {
            const predefined = data.predefined || [];
            const custom = data.custom || [];
            
            select.innerHTML = '<option value="">Sélectionner une opération</option>';
            
            if (predefined.length > 0) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = 'Prédéfinies';
                predefined.forEach(op => {
                    const option = document.createElement('option');
                    option.value = op;
                    option.textContent = op.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    optgroup.appendChild(option);
                });
                select.appendChild(optgroup);
            }
            
            if (custom.length > 0) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = 'Personnalisées';
                custom.forEach(op => {
                    const option = document.createElement('option');
                    option.value = op;
                    option.textContent = op;
                    optgroup.appendChild(option);
                });
                select.appendChild(optgroup);
            }
            
            const runBtn = document.getElementById('run-apt-operation');
            if (runBtn) {
                select.addEventListener('change', () => {
                    runBtn.disabled = !select.value;
                });
            }
        })
        .catch(error => console.error('Erreur chargement APT:', error));
}

function loadAPTOperationsList() {
    const container = document.getElementById('apt-operations-list');
    if (!container) return;
    
    fetch('/api/apt/operations')
        .then(res => res.json())
        .then(data => {
            const allOps = [...(data.predefined || []), ...(data.custom || [])];
            
            if (allOps.length === 0) {
                container.innerHTML = '<p>Aucune opération APT disponible</p>';
                return;
            }
            
            container.innerHTML = allOps.map(op => `
                <div class="apt-operation-card" data-operation="${op}">
                    <div class="apt-operation-header">
                        <div class="apt-operation-title">${op.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                        <div class="apt-operation-description">Opération APT ${data.predefined?.includes(op) ? 'prédéfinie' : 'personnalisée'}</div>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Erreur:', error);
            container.innerHTML = '<p>Erreur lors du chargement des opérations APT</p>';
        });
}

// Helper functions
function loadTargetsForSelect(selectId) {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    fetch('/api/targets')
        .then(res => res.json())
        .then(data => {
            const targets = data.targets || [];
            select.innerHTML = '<option value="">Sélectionner une cible</option>' +
                targets.map(t => `<option value="${t}">${t}</option>`).join('');
        })
        .catch(error => console.error('Erreur chargement cibles:', error));
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type} fade-in`;
    notification.innerHTML = `
        <div class="notification-title">${type === 'success' ? '✅ Succès' : type === 'error' ? '❌ Erreur' : type === 'warning' ? '⚠️ Attention' : 'ℹ️ Info'}</div>
        <div class="notification-message">${message}</div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function onScanCompleted(data) {
    showNotification(`Scan terminé pour ${data.target}`, 'success');
    displayAttackResult('scan', data.results_summary);
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        runAttack,
        getAttackResults: () => attackResults,
        runMultiAttacks,
        runAPTOperation
    };
}