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
                <button id="run-apt-operation" class="btn btn-primary" disabled>
                    🎯 Lancer l'opération APT
                </button>
            </div>
            
            <div class="apt-operation-details">
                <h3>Phases de l'Opération</h3>
                <div id="apt-phases-list"></div>
            </div>
        </div>
    `;
}

function getStealthHTML() {
    return `
        <div class="stealth-panel">
            <h2>Paramètres du Mode Furtif</h2>
            <div class="stealth-controls">
                <div class="form-group">
                    <label>Profil furtif:</label>
                    <select id="stealth-profile" class="form-select">
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="paranoid">Paranoid</option>
                        <option value="custom">Personnalisé</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Délai entre les requêtes (ms):</label>
                    <input type="number" id="request-delay" class="form-control" value="100">
                </div>
                <div class="form-group">
                    <label>Variation du délai (%):</label>
                    <input type="number" id="delay-variation" class="form-control" value="20">
                </div>
                <div class="form-group">
                    <label>User-Agent:</label>
                    <select id="user-agent" class="form-select">
                        <option value="default">Défaut</option>
                        <option value="random">Aléatoire</option>
                        <option value="custom">Personnalisé</option>
                    </select>
                </div>
                <div class="form-group">
                    <input type="text" id="custom-user-agent" class="form-control" placeholder="Votre User-Agent personnalisé" style="display:none;">
                </div>
                <button id="save-stealth-settings" class="btn btn-primary">Enregistrer les paramètres</button>
            </div>
        </div>
    `;
}

// ========================================
// CHARGEMENT DES DONNÉES
// ========================================

function loadAttackCategories() {
    const grid = document.getElementById('attacks-grid');
    const multiGrid = document.getElementById('multi-attacks-grid');
    if (!grid || !multiGrid) return;
    
    grid.innerHTML = '';
    multiGrid.innerHTML = '';

    for (const [key, category] of Object.entries(ATTACK_CATEGORIES)) {
        const categoryCard = createCategoryCard(key, category, false);
        const multiCategoryCard = createCategoryCard(key, category, true);
        grid.appendChild(categoryCard);
        multiGrid.appendChild(multiCategoryCard);
    }
}

function createCategoryCard(key, category, isMulti) {
    const card = document.createElement('div');
    card.className = 'attack-category-card';
    card.innerHTML = `
        <div class="category-header">
            <h3>${category.icon} ${category.name}</h3>
            <p>${category.description}</p>
        </div>
        <div class="attacks-list"></div>
    `;

    const list = card.querySelector('.attacks-list');
    category.attacks.forEach(attackId => {
        const attackName = ATTACK_NAMES[attackId] || attackId;
        const attackEl = document.createElement('div');
        attackEl.className = 'attack-item';
        attackEl.dataset.attackId = attackId;
        
        const inputId = `${isMulti ? 'multi-' : ''}attack-${attackId}`;
        attackEl.innerHTML = `
            <input type="checkbox" id="${inputId}" data-attack-id="${attackId}">
            <label for="${inputId}">${attackName}</label>
        `;
        list.appendChild(attackEl);
    });

    return card;
}

async function loadTargets() {
    try {
        const response = await fetch('/api/targets');
        const targets = await response.json();
        
        ['attack-target', 'multi-target', 'apt-target'].forEach(selectId => {
            const select = document.getElementById(selectId);
            if (!select) return;
            const currentValue = select.value;
            select.innerHTML = '<option value="">Sélectionner une cible</option>';
            targets.forEach(target => {
                const option = document.createElement('option');
                option.value = target.id;
                option.textContent = target.name;
                select.appendChild(option);
            });
            if (currentValue) {
                select.value = currentValue;
            }
        });
    } catch (error) {
        console.error('Erreur lors du chargement des cibles:', error);
        showNotification('Erreur de chargement des cibles', 'error');
    }
}

function loadStealthProfiles() {
    // Logique pour charger les profils de furtivité
}

function loadAPTOperations() {
    // Logique pour charger les opérations APT
}

// ========================================
// GESTION DES ÉVÉNEMENTS
// ========================================

function bindTabEvents() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            
            document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
        });
    });
}

function bindAttackEvents() {
    // Sélection d'attaques
    document.body.addEventListener('change', event => {
        if (event.target.matches('#attacks-grid input[type="checkbox"], #multi-attacks-grid input[type="checkbox"]')) {
            updateRunButtonsState();
        }
    });
    
    // Lancement d'attaques simples
    const runSimpleBtn = document.getElementById('run-selected-attacks');
    if (runSimpleBtn) {
        runSimpleBtn.addEventListener('click', runSelectedAttacks);
    }
    
    // Lancement d'attaques multiples
    const runMultiBtn = document.getElementById('run-multi-attacks');
    if (runMultiBtn) {
        runMultiBtn.addEventListener('click', runMultiAttacks);
    }
    
    // Sélection/Désélection de toutes les attaques
    const selectAllBtn = document.getElementById('select-all-attacks');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => toggleAllMultiAttacks(true));
    }
    const deselectAllBtn = document.getElementById('deselect-all-attacks');
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', () => toggleAllMultiAttacks(false));
    }
    
    // Lancement d'opérations APT
    const runAPTBtn = document.getElementById('run-apt-operation');
    if (runAPTBtn) {
        runAPTBtn.addEventListener('click', runAPTOperation);
    }
}

function updateRunButtonsState() {
    const selectedSimple = document.querySelectorAll('#attacks-grid input:checked').length > 0;
    document.getElementById('run-selected-attacks').disabled = !selectedSimple;

    const selectedMulti = document.querySelectorAll('#multi-attacks-grid input:checked').length > 0;
    document.getElementById('run-multi-attacks').disabled = !selectedMulti;
}

function toggleAllMultiAttacks(select) {
    const checkboxes = document.querySelectorAll('#multi-attacks-grid input[type="checkbox"]');
    checkboxes.forEach(cb => cb.checked = select);
    updateRunButtonsState();
}

// ========================================
// EXÉCUTION DES ATTAQUES
// ========================================

function runSelectedAttacks() {
    const target = document.getElementById('attack-target').value;
    if (!target) {
        showNotification('Veuillez sélectionner une cible', 'warning');
        return;
    }
    
    const selectedAttacks = Array.from(document.querySelectorAll('#attacks-grid input:checked'))
        .map(cb => cb.dataset.attackId);
    
    if (selectedAttacks.length === 0) {
        showNotification('Veuillez sélectionner au moins une attaque', 'warning');
        return;
    }
    
    const attackLevel = document.getElementById('attack-level').value;
    
    selectedAttacks.forEach(attackType => {
        const taskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const attackData = {
            task_id: taskId,
            attack_type: attackType,
            target_id: target,
            attack_level: attackLevel
        };
        
        socket.emit('start_attack', attackData);
        addActiveAttack(taskId, `Attaque ${ATTACK_NAMES[attackType]} sur ${target}`);
    });
}

function runMultiAttacks() {
    const target = document.getElementById('multi-target').value;
    if (!target) {
        showNotification('Veuillez sélectionner une cible', 'warning');
        return;
    }
    
    const selectedAttacks = Array.from(document.querySelectorAll('#multi-attacks-grid input:checked'))
        .map(cb => cb.dataset.attackId);
        
    if (selectedAttacks.length === 0) {
        showNotification('Veuillez sélectionner au moins une attaque', 'warning');
        return;
    }
    
    const executionMode = document.getElementById('execution-mode').value;
    const stealthLevel = document.getElementById('multi-stealth-level').value;
    const taskId = `multi_${Date.now()}`;
    
    const multiAttackData = {
        task_id: taskId,
        target_id: target,
        attacks: selectedAttacks,
        mode: executionMode,
        stealth: stealthLevel
    };
    
    socket.emit('start_multi_attack', multiAttackData);
    addActiveMultiAttack(taskId, `Attaques multiples sur ${target} (${selectedAttacks.length})`);
}

function runAPTOperation() {
    const target = document.getElementById('apt-target').value;
    if (!target) {
        showNotification('Veuillez sélectionner une cible', 'warning');
        return;
    }
    
    const operation = document.getElementById('apt-operation').value;
    if (!operation) {
        showNotification('Veuillez sélectionner une opération APT', 'warning');
        return;
    }
    
    const stealthLevel = document.getElementById('apt-stealth-level').value;
    const taskId = `apt_${Date.now()}`;
    
    const aptData = {
        task_id: taskId,
        target_id: target,
        operation: operation,
        stealth: stealthLevel
    };
    
    socket.emit('start_apt', aptData);
    addActiveAPTOperation(taskId, `Opération APT sur ${target}`);
}

// ========================================
// AFFICHAGE DE L'ÉTAT
// ========================================

function addActiveAttack(taskId, description) {
    activeAttacks[taskId] = { description, progress: 0 };
    renderActiveAttacks();
}

function addActiveMultiAttack(taskId, description) {
    activeMultiAttacks[taskId] = { description, progress: 0, current_attack: 'Initialisation' };
    renderActiveAttacks();
}

function addActiveAPTOperation(taskId, description) {
    activeAPTOperations[taskId] = { description, phases: {} };
    renderActiveAttacks();
}

function renderActiveAttacks() {
    const list = document.getElementById('active-attacks-list');
    list.innerHTML = '';
    
    // Attaques simples
    for (const [id, attack] of Object.entries(activeAttacks)) {
        const item = document.createElement('div');
        item.className = 'active-attack-item';
        item.innerHTML = `
            <span>${attack.description}</span>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: ${attack.progress}%;"></div>
            </div>
            <span>${attack.progress}%</span>
        `;
        list.appendChild(item);
    }
    
    // Attaques multiples
    for (const [id, attack] of Object.entries(activeMultiAttacks)) {
        const item = document.createElement('div');
        item.className = 'active-attack-item multi-attack';
        item.innerHTML = `
            <span>${attack.description}</span>
            <small>Actuellement: ${attack.current_attack}</small>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: ${attack.progress}%;"></div>
            </div>
            <span>${attack.progress}%</span>
        `;
        list.appendChild(item);
    }
    
    // Opérations APT
    for (const [id, operation] of Object.entries(activeAPTOperations)) {
        const item = document.createElement('div');
        item.className = 'active-attack-item apt-operation';
        let phasesHTML = '<ul>';
        for (const [phase, status] of Object.entries(operation.phases)) {
            phasesHTML += `<li class="${status.toLowerCase()}">${phase}: ${status}</li>`;
        }
        phasesHTML += '</ul>';
        item.innerHTML = `
            <span>${operation.description}</span>
            <div class="apt-phases">${phasesHTML}</div>
        `;
        list.appendChild(item);
    }
}

function updateAttackProgress(taskId, currentAttack, progress) {
    if (activeMultiAttacks[taskId]) {
        activeMultiAttacks[taskId].progress = progress;
        activeMultiAttacks[taskId].current_attack = ATTACK_NAMES[currentAttack] || currentAttack;
        renderActiveAttacks();
    }
}

function onMultiAttackCompleted(taskId, data) {
    delete activeMultiAttacks[taskId];
    renderActiveAttacks();
    addAttackResult('Attaques multiples', data);
    showNotification(`Attaques multiples terminées (ID: ${taskId})`, 'success');
}

function onAPTStarted(data) {
    const taskId = data.task_id;
    if (activeAPTOperations[taskId]) {
        activeAPTOperations[taskId].phases = {};
        data.phases.forEach(phase => {
            activeAPTOperations[taskId].phases[phase] = 'En attente';
        });
        renderActiveAttacks();
    }
}

function onAPTPhaseStart(data) {
    const taskId = data.task_id;
    if (activeAPTOperations[taskId]) {
        activeAPTOperations[taskId].phases[data.phase] = 'En cours';
        renderActiveAttacks();
    }
}

function onAPTPhaseComplete(data) {
    const taskId = data.task_id;
    if (activeAPTOperations[taskId]) {
        activeAPTOperations[taskId].phases[data.phase] = 'Terminé';
        renderActiveAttacks();
    }
}

function onAPTCompleted(data) {
    const taskId = data.task_id;
    delete activeAPTOperations[taskId];
    renderActiveAttacks();
    addAttackResult('Opération APT', data);
    showNotification(`Opération APT terminée (ID: ${taskId})`, 'success');
}

function onScanCompleted(data) {
    const taskId = data.task_id;
    const resultDivId = `scan-result-${taskId}`;
    let resultDiv = document.getElementById(resultDivId);

    if (!resultDiv) {
        // Create result area if it doesn't exist
        const resultsContainer = document.getElementById('attack-results');
        const resultCard = document.createElement('div');
        resultCard.className = 'result-card';
        resultCard.innerHTML = `
            <div class="result-header">
                <h3>Résultat du Scan (ID: ${taskId})</h3>
                <span class="timestamp">${new Date().toLocaleString()}</span>
            </div>
            <div id="${resultDivId}" class="result-content"></div>
        `;
        resultsContainer.prepend(resultCard);
        resultDiv = document.getElementById(resultDivId);
    }
    
    const pre = document.createElement('pre');
    pre.textContent = data.output;
    resultDiv.replaceChildren(pre);
    
    showNotification(`Scan terminé (ID: ${taskId})`, 'info');
    
    // Mettre à jour la liste des cibles si un scan a été effectué
    if(data.targets_updated) {
        loadTargets();
    }
}

function addAttackResult(title, data) {
    const resultsContainer = document.getElementById('attack-results');
    const resultCard = document.createElement('div');
    resultCard.className = 'result-card';
    
    let contentHTML = '<dl>';
    for (const [key, value] of Object.entries(data.results)) {
        contentHTML += `<dt>${key}</dt><dd><pre>${JSON.stringify(value, null, 2)}</pre></dd>`;
    }
    contentHTML += '</dl>';
    
    resultCard.innerHTML = `
        <div class="result-header">
            <h3>${title} (ID: ${data.task_id})</h3>
            <span class="timestamp">${new Date().toLocaleString()}</span>
        </div>
        <div class="result-content">
            ${contentHTML}
        </div>
    `;
    
    resultsContainer.prepend(resultCard);
}

// ========================================
// NOTIFICATIONS
// ========================================

function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container') || createNotificationContainer();
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            container.removeChild(notification);
        }, 500);
    }, 5000);
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    document.body.appendChild(container);
    return container;
}
