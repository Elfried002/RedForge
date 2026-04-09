/**
 * RedForge - WebSocket Client Amélioré
 * Communication en temps réel avec le serveur
 * Version: 2.0.0
 * Support: Multi-Attacks, Stealth Mode, APT Operations
 */

// ========================================
// CONFIGURATION WEBSOCKET
// ========================================

let socket = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 10;
let reconnectDelay = 1000;
let heartbeatInterval = null;
let messageHandlers = {};
let eventQueue = [];
let isProcessingQueue = false;
let connectionStatusListeners = [];

// Configuration Socket.IO (support amélioré)
const WS_URL = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const WS_PORT = window.location.port || 5000;
const SOCKET_URL = `${WS_URL}${window.location.hostname}:${WS_PORT}`;

// Types d'événements supportés
const EVENT_TYPES = {
    // Scans et attaques
    SCAN_PROGRESS: 'scan_progress',
    SCAN_COMPLETED: 'scan_completed',
    ATTACK_STARTED: 'attack_started',
    ATTACK_PROGRESS: 'attack_progress',
    ATTACK_COMPLETED: 'attack_completed',
    
    // Multi-attaques
    MULTI_ATTACK_STARTED: 'multi_attack_started',
    MULTI_ATTACK_PROGRESS: 'multi_attack_progress',
    MULTI_ATTACK_COMPLETED: 'multi_attack_completed',
    
    // Opérations APT
    APT_STARTED: 'apt_started',
    APT_PHASE_START: 'apt_phase_start',
    APT_PHASE_PROGRESS: 'apt_phase_progress',
    APT_PHASE_COMPLETE: 'apt_phase_complete',
    APT_COMPLETED: 'apt_completed',
    
    // Mode furtif
    STEALTH_STATUS: 'stealth_status',
    STEALTH_ALERT: 'stealth_alert',
    STEALTH_METRICS: 'stealth_metrics',
    
    // Vulnérabilités
    VULNERABILITY_FOUND: 'vulnerability_found',
    VULNERABILITY_UPDATED: 'vulnerability_updated',
    
    // Sessions
    SESSION_CREATED: 'session_created',
    SESSION_CLOSED: 'session_closed',
    SESSION_UPDATED: 'session_updated',
    
    // Notifications
    NOTIFICATION: 'notification',
    SYSTEM_ALERT: 'system_alert',
    
    // Heartbeat
    HEARTBEAT: 'heartbeat',
    PING: 'ping',
    PONG: 'pong'
};

// ========================================
// INITIALISATION
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
    setupBeforeUnload();
});

function setupBeforeUnload() {
    window.addEventListener('beforeunload', () => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            sendMessage('client_disconnect', { timestamp: Date.now() });
        }
    });
}

// ========================================
// CONNEXION WEBSOCKET
// ========================================

function connectWebSocket() {
    try {
        // Tenter d'abord Socket.IO (recommandé)
        if (typeof io !== 'undefined') {
            connectSocketIO();
        } else {
            connectNativeWebSocket();
        }
    } catch (error) {
        console.error('Erreur de connexion WebSocket:', error);
        scheduleReconnect();
    }
}

function connectSocketIO() {
    const socketIO = io({
        reconnection: true,
        reconnectionAttempts: maxReconnectAttempts,
        reconnectionDelay: reconnectDelay,
        transports: ['websocket', 'polling']
    });
    
    socketIO.on('connect', () => {
        console.log('Socket.IO connecté');
        socket = socketIO;
        onSocketOpen();
    });
    
    socketIO.on('disconnect', (reason) => {
        console.log('Socket.IO déconnecté:', reason);
        onSocketClose({ code: reason === 'io server disconnect' ? 1000 : 1001, reason });
    });
    
    socketIO.on('error', (error) => {
        console.error('Socket.IO erreur:', error);
        onSocketError(error);
    });
    
    // Écouter tous les événements
    for (const eventType of Object.values(EVENT_TYPES)) {
        socketIO.on(eventType, (data) => {
            handleMessage({ type: eventType, data });
        });
    }
}

function connectNativeWebSocket() {
    socket = new WebSocket(`${SOCKET_URL}/ws`);
    
    socket.onopen = onSocketOpen;
    socket.onclose = onSocketClose;
    socket.onerror = onSocketError;
    socket.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            handleMessage(message);
        } catch (error) {
            console.error('Erreur parsing message:', error);
        }
    };
}

// ========================================
// ÉVÉNEMENTS WEBSOCKET
// ========================================

function onSocketOpen() {
    console.log('WebSocket connecté');
    reconnectAttempts = 0;
    reconnectDelay = 1000;
    
    // Démarrer le heartbeat
    startHeartbeat();
    
    // S'abonner aux événements
    subscribeToEvents();
    
    // Traiter la file d'attente
    processEventQueue();
    
    // Notifier les listeners
    notifyConnectionStatusListeners(true);
    
    showNotification('Connexion temps réel établie', 'success', 3000);
}

function onSocketClose(event) {
    console.log('WebSocket déconnecté', event.code, event.reason);
    stopHeartbeat();
    
    notifyConnectionStatusListeners(false);
    
    if (event.code !== 1000) { // Fermeture normale
        scheduleReconnect();
    }
}

function onSocketError(error) {
    console.error('Erreur WebSocket:', error);
    notifyConnectionStatusListeners(false);
}

function onSocketMessage(event) {
    try {
        const data = JSON.parse(event.data);
        handleMessage(data);
    } catch (error) {
        console.error('Erreur parsing message:', error);
    }
}

// ========================================
// GESTION DES MESSAGES (améliorée)
// ========================================

function handleMessage(message) {
    const { type, data } = message;
    
    // Appeler les handlers enregistrés
    if (messageHandlers[type]) {
        messageHandlers[type].forEach(handler => {
            try {
                handler(data);
            } catch (error) {
                console.error(`Erreur dans handler pour ${type}:`, error);
            }
        });
    }
    
    // Traitement des types spécifiques
    switch (type) {
        case EVENT_TYPES.SCAN_PROGRESS:
            handleScanProgress(data);
            break;
        case EVENT_TYPES.SCAN_COMPLETED:
            handleScanCompleted(data);
            break;
        case EVENT_TYPES.ATTACK_PROGRESS:
            handleAttackProgress(data);
            break;
        case EVENT_TYPES.ATTACK_COMPLETED:
            handleAttackCompleted(data);
            break;
        case EVENT_TYPES.MULTI_ATTACK_STARTED:
            handleMultiAttackStarted(data);
            break;
        case EVENT_TYPES.MULTI_ATTACK_PROGRESS:
            handleMultiAttackProgress(data);
            break;
        case EVENT_TYPES.MULTI_ATTACK_COMPLETED:
            handleMultiAttackCompleted(data);
            break;
        case EVENT_TYPES.APT_STARTED:
            handleAPTStarted(data);
            break;
        case EVENT_TYPES.APT_PHASE_START:
            handleAPTPhaseStart(data);
            break;
        case EVENT_TYPES.APT_PHASE_PROGRESS:
            handleAPTPhaseProgress(data);
            break;
        case EVENT_TYPES.APT_PHASE_COMPLETE:
            handleAPTPhaseComplete(data);
            break;
        case EVENT_TYPES.APT_COMPLETED:
            handleAPTCompleted(data);
            break;
        case EVENT_TYPES.STEALTH_STATUS:
            handleStealthStatus(data);
            break;
        case EVENT_TYPES.STEALTH_ALERT:
            handleStealthAlert(data);
            break;
        case EVENT_TYPES.STEALTH_METRICS:
            handleStealthMetrics(data);
            break;
        case EVENT_TYPES.VULNERABILITY_FOUND:
            handleVulnerabilityFound(data);
            break;
        case EVENT_TYPES.SESSION_CREATED:
            handleSessionCreated(data);
            break;
        case EVENT_TYPES.SESSION_CLOSED:
            handleSessionClosed(data);
            break;
        case EVENT_TYPES.NOTIFICATION:
            handleNotification(data);
            break;
        case EVENT_TYPES.SYSTEM_ALERT:
            handleSystemAlert(data);
            break;
        case EVENT_TYPES.HEARTBEAT:
        case EVENT_TYPES.PING:
            handleHeartbeat(data);
            break;
        default:
            console.log('Message non traité:', type, data);
    }
}

// ========================================
// GESTIONNAIRES SPÉCIFIQUES (Multi-Attacks & APT)
// ========================================

function handleScanProgress(data) {
    const { taskId, progress, message, target } = data;
    
    updateProgressBar(`scan-progress-${taskId}`, progress);
    updateStatusText(`scan-status-${taskId}`, message);
    
    // Émettre un événement personnalisé
    dispatchCustomEvent('scanProgress', data);
}

function handleScanCompleted(data) {
    const { taskId, target, duration, results } = data;
    
    showNotification(`Scan de ${target} terminé en ${duration}`, 'success');
    
    // Mettre à jour le dashboard
    if (typeof window.refreshDashboard === 'function') {
        window.refreshDashboard();
    }
    
    dispatchCustomEvent('scanCompleted', data);
}

function handleAttackProgress(data) {
    const { attackId, progress, status, currentStep } = data;
    
    updateProgressBar(`attack-progress-${attackId}`, progress);
    updateStatusIcon(`attack-status-${attackId}`, status);
    
    if (currentStep) {
        updateStatusText(`attack-step-${attackId}`, currentStep);
    }
    
    dispatchCustomEvent('attackProgress', data);
}

function handleAttackCompleted(data) {
    const { attackId, attackType, result, duration } = data;
    
    const status = result.success ? 'réussie' : 'échouée';
    const notifType = result.success ? 'success' : 'error';
    showNotification(`Attaque ${attackType} ${status} en ${duration}`, notifType);
    
    dispatchCustomEvent('attackCompleted', data);
}

// Multi-attaques
function handleMultiAttackStarted(data) {
    const { taskId, target, attackCount, stealthLevel } = data;
    
    showNotification(`Multi-attaque lancée sur ${target} (${attackCount} attaques, furtivité: ${stealthLevel})`, 'info');
    
    addMultiAttackToUI(taskId, data);
    dispatchCustomEvent('multiAttackStarted', data);
}

function handleMultiAttackProgress(data) {
    const { taskId, currentAttack, progress, completedCount, totalCount } = data;
    
    updateProgressBar(`multi-progress-${taskId}`, progress);
    updateStatusText(`multi-current-${taskId}`, currentAttack);
    updateStatusText(`multi-count-${taskId}`, `${completedCount}/${totalCount}`);
    
    dispatchCustomEvent('multiAttackProgress', data);
}

function handleMultiAttackCompleted(data) {
    const { taskId, successful, totalAttacks, duration } = data;
    
    showNotification(`Multi-attaque terminée: ${successful}/${totalAttacks} réussies en ${duration}`, 
                    successful === totalAttacks ? 'success' : 'warning');
    
    updateMultiAttackUIComplete(taskId, data);
    dispatchCustomEvent('multiAttackCompleted', data);
}

// Opérations APT
function handleAPTStarted(data) {
    const { taskId, operationName, totalPhases, stealthLevel } = data;
    
    showNotification(`Opération APT "${operationName}" démarrée (niveau furtif: ${stealthLevel})`, 'warning');
    
    createAPTTimeline(taskId, operationName, totalPhases);
    dispatchCustomEvent('aptStarted', data);
}

function handleAPTPhaseStart(data) {
    const { taskId, phase, phaseNumber, totalPhases, attacksCount } = data;
    
    showNotification(`Phase APT ${phaseNumber}/${totalPhases}: ${phase} (${attacksCount} attaques)`, 'info');
    
    updateAPTTimelinePhase(taskId, phase, 'running');
    dispatchCustomEvent('aptPhaseStart', data);
}

function handleAPTPhaseProgress(data) {
    const { taskId, phase, progress, currentAttack } = data;
    
    updateAPTTimelineProgress(taskId, phase, progress);
    if (currentAttack) {
        updateStatusText(`apt-phase-${taskId}-${phase}`, currentAttack);
    }
    
    dispatchCustomEvent('aptPhaseProgress', data);
}

function handleAPTPhaseComplete(data) {
    const { taskId, phase, successRate, duration } = data;
    
    showNotification(`Phase APT "${phase}" terminée (${successRate}% succès) en ${duration}`, 
                    successRate > 70 ? 'success' : 'warning');
    
    updateAPTTimelinePhase(taskId, phase, 'completed', successRate);
    dispatchCustomEvent('aptPhaseComplete', data);
}

function handleAPTCompleted(data) {
    const { taskId, totalPhases, overallSuccess, duration } = data;
    
    showNotification(`Opération APT complétée! Succès global: ${overallSuccess}% en ${duration}`, 
                    overallSuccess > 70 ? 'success' : 'warning');
    
    updateAPTTimelineComplete(taskId, overallSuccess);
    dispatchCustomEvent('aptCompleted', data);
}

// Mode furtif
function handleStealthStatus(data) {
    const { enabled, level, metrics } = data;
    
    updateStealthIndicator(enabled, level);
    
    if (metrics) {
        updateStealthMetrics(metrics);
    }
    
    dispatchCustomEvent('stealthStatus', data);
}

function handleStealthAlert(data) {
    const { severity, message, recommendation } = data;
    
    const alertClass = severity === 'high' ? 'error' : severity === 'medium' ? 'warning' : 'info';
    showNotification(`⚠️ Alerte furtive: ${message}`, alertClass, 8000);
    
    if (recommendation) {
        console.log(`Recommandation: ${recommendation}`);
    }
    
    addStealthAlertToUI(data);
    dispatchCustomEvent('stealthAlert', data);
}

function handleStealthMetrics(data) {
    const { detectionRisk, avgDelay, torActive, randomUserAgents } = data;
    
    updateStealthMetricsDisplay(data);
    dispatchCustomEvent('stealthMetrics', data);
}

// Vulnérabilités
function handleVulnerabilityFound(data) {
    const { vulnerability, target, severity, details, confidence } = data;
    
    const severityNames = {
        critical: 'Critique',
        high: 'Élevée',
        medium: 'Moyenne',
        low: 'Basse'
    };
    
    const notifType = (severity === 'critical' || severity === 'high') ? 'error' : 'warning';
    const confidenceText = confidence ? ` (confiance: ${confidence}%)` : '';
    
    showNotification(`[${severityNames[severity] || severity}] ${vulnerability} sur ${target}${confidenceText}`, notifType);
    
    addVulnerabilityToList(data);
    dispatchCustomEvent('vulnerabilityFound', data);
}

// Sessions
function handleSessionCreated(data) {
    const { sessionId, target, type, userId } = data;
    
    showNotification(`Nouvelle session ${type} créée sur ${target}`, 'success');
    
    if (typeof window.loadSessions === 'function') {
        window.loadSessions();
    }
    
    dispatchCustomEvent('sessionCreated', data);
}

function handleSessionClosed(data) {
    const { sessionId, reason } = data;
    
    showNotification(`Session ${sessionId} fermée: ${reason}`, 'info');
    
    if (typeof window.loadSessions === 'function') {
        window.loadSessions();
    }
    
    dispatchCustomEvent('sessionClosed', data);
}

function handleNotification(data) {
    const { message, type, duration = 5000, title } = data;
    showNotification(title ? `${title}: ${message}` : message, type, duration);
}

function handleSystemAlert(data) {
    const { level, message, timestamp, source } = data;
    
    console.warn(`[SYSTEM ${level.toUpperCase()}] ${message} (source: ${source})`);
    showNotification(`⚠️ Système: ${message}`, level === 'error' ? 'error' : 'warning', 10000);
    
    addSystemAlertToUI(data);
    dispatchCustomEvent('systemAlert', data);
}

function handleHeartbeat(data) {
    // Répondre au heartbeat
    if (socket && isSocketOpen()) {
        sendMessage(EVENT_TYPES.PONG, { timestamp: Date.now(), clientTime: data.timestamp });
    }
}

// ========================================
// FONCTIONS D'ENVOI (améliorées)
// ========================================

function sendMessage(type, data) {
    if (!isSocketOpen()) {
        queueEvent(type, data);
        return false;
    }
    
    try {
        const message = JSON.stringify({ type, data });
        
        if (socket.send) {
            socket.send(message);
        } else if (socket.emit) {
            socket.emit(type, data);
        }
        
        return true;
    } catch (error) {
        console.error('Erreur envoi message:', error);
        queueEvent(type, data);
        return false;
    }
}

function queueEvent(type, data) {
    eventQueue.push({ type, data, timestamp: Date.now() });
    
    if (!isProcessingQueue && isSocketOpen()) {
        processEventQueue();
    }
}

async function processEventQueue() {
    if (isProcessingQueue || !isSocketOpen()) return;
    
    isProcessingQueue = true;
    
    while (eventQueue.length > 0 && isSocketOpen()) {
        const event = eventQueue.shift();
        const success = sendMessage(event.type, event.data);
        
        if (!success) {
            // Remettre en queue si échec
            eventQueue.unshift(event);
            break;
        }
        
        // Petit délai entre les envois
        await new Promise(resolve => setTimeout(resolve, 10));
    }
    
    isProcessingQueue = false;
}

function subscribeToEvents() {
    const events = Object.values(EVENT_TYPES);
    sendMessage('subscribe', { events, client: 'web_interface', version: '2.0.0' });
}

function unsubscribeFromEvents(events) {
    sendMessage('unsubscribe', { events });
}

// ========================================
// HEARTBEAT (amélioré)
// ========================================

function startHeartbeat() {
    if (heartbeatInterval) clearInterval(heartbeatInterval);
    
    heartbeatInterval = setInterval(() => {
        if (isSocketOpen()) {
            sendMessage(EVENT_TYPES.PING, { 
                timestamp: Date.now(),
                clientInfo: {
                    userAgent: navigator.userAgent,
                    screenSize: `${window.innerWidth}x${window.innerHeight}`,
                    language: navigator.language
                }
            });
        }
    }, 25000); // Toutes les 25 secondes
}

function stopHeartbeat() {
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = null;
    }
}

// ========================================
// RECONNEXION (améliorée)
// ========================================

function scheduleReconnect() {
    if (reconnectAttempts >= maxReconnectAttempts) {
        console.error('Nombre maximum de tentatives de reconnexion atteint');
        showNotification('Impossible de se reconnecter au serveur. Veuillez rafraîchir la page.', 'error', 10000);
        return;
    }
    
    reconnectAttempts++;
    const delay = reconnectDelay * Math.pow(1.5, reconnectAttempts - 1);
    
    console.log(`Tentative de reconnexion dans ${delay}ms (${reconnectAttempts}/${maxReconnectAttempts})`);
    
    setTimeout(() => {
        connectWebSocket();
    }, delay);
}

// ========================================
// GESTION DES HANDLERS
// ========================================

function on(eventType, handler) {
    if (!messageHandlers[eventType]) {
        messageHandlers[eventType] = [];
    }
    messageHandlers[eventType].push(handler);
}

function off(eventType, handler) {
    if (messageHandlers[eventType]) {
        const index = messageHandlers[eventType].indexOf(handler);
        if (index !== -1) {
            messageHandlers[eventType].splice(index, 1);
        }
    }
}

function once(eventType, handler) {
    const wrappedHandler = (data) => {
        handler(data);
        off(eventType, wrappedHandler);
    };
    on(eventType, wrappedHandler);
}

function onConnectionStatus(callback) {
    connectionStatusListeners.push(callback);
}

function notifyConnectionStatusListeners(connected) {
    connectionStatusListeners.forEach(callback => {
        try {
            callback(connected);
        } catch (error) {
            console.error('Erreur dans listener de statut:', error);
        }
    });
}

// ========================================
// FONCTIONS UTILITAIRES
// ========================================

function isSocketOpen() {
    if (!socket) return false;
    
    if (socket.readyState !== undefined) {
        return socket.readyState === WebSocket.OPEN;
    }
    
    return socket.connected !== false;
}

function getConnectionStatus() {
    if (!socket) return 'disconnected';
    
    if (socket.readyState !== undefined) {
        switch (socket.readyState) {
            case WebSocket.CONNECTING: return 'connecting';
            case WebSocket.OPEN: return 'connected';
            case WebSocket.CLOSING: return 'closing';
            case WebSocket.CLOSED: return 'disconnected';
            default: return 'unknown';
        }
    }
    
    return socket.connected ? 'connected' : 'disconnected';
}

function disconnect() {
    if (socket) {
        if (socket.close) {
            socket.close(1000, 'Client disconnect');
        } else if (socket.disconnect) {
            socket.disconnect();
        }
        socket = null;
    }
    stopHeartbeat();
}

function updateProgressBar(elementId, progress) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.width = `${progress}%`;
        element.setAttribute('aria-valuenow', progress);
    }
}

function updateStatusText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element && text) {
        element.textContent = text;
    }
}

function updateStatusIcon(elementId, status) {
    const element = document.getElementById(elementId);
    if (element) {
        const icon = getStatusIcon(status);
        element.textContent = icon;
        element.className = `attack-status status-${status}`;
    }
}

function getStatusIcon(status) {
    const icons = {
        running: '⟳',
        completed: '✓',
        failed: '✗',
        pending: '⏳',
        success: '✓',
        error: '✗'
    };
    return icons[status] || '●';
}

function dispatchCustomEvent(eventName, detail) {
    const event = new CustomEvent(`redforge:${eventName}`, { detail });
    document.dispatchEvent(event);
}

// UI Helpers pour Multi-Attacks et APT
function addMultiAttackToUI(taskId, data) {
    const container = document.getElementById('active-multi-attacks');
    if (!container) return;
    
    const element = document.createElement('div');
    element.id = `multi-${taskId}`;
    element.className = 'multi-attack-item';
    element.innerHTML = `
        <div class="multi-header">
            <span class="multi-target">${escapeHtml(data.target)}</span>
            <span class="multi-status running">En cours</span>
        </div>
        <div class="multi-progress">
            <div class="progress">
                <div id="multi-progress-${taskId}" class="progress-bar" style="width: 0%"></div>
            </div>
        </div>
        <div class="multi-info">
            <span id="multi-current-${taskId}">Initialisation...</span>
            <span id="multi-count-${taskId}">0/${data.attackCount}</span>
        </div>
    `;
    
    container.appendChild(element);
}

function updateMultiAttackUIComplete(taskId, data) {
    const element = document.getElementById(`multi-${taskId}`);
    if (element) {
        const statusSpan = element.querySelector('.multi-status');
        if (statusSpan) {
            statusSpan.textContent = 'Terminé';
            statusSpan.className = `multi-status ${data.successful === data.totalAttacks ? 'success' : 'warning'}`;
        }
        
        setTimeout(() => {
            element.style.opacity = '0';
            setTimeout(() => element.remove(), 300);
        }, 5000);
    }
}

function createAPTTimeline(taskId, operationName, totalPhases) {
    const container = document.getElementById('apt-timeline-container');
    if (!container) return;
    
    const timeline = document.createElement('div');
    timeline.id = `apt-timeline-${taskId}`;
    timeline.className = 'apt-timeline';
    timeline.innerHTML = `
        <div class="timeline-header">
            <h4>${escapeHtml(operationName)}</h4>
            <span class="timeline-status running">En cours</span>
        </div>
        <div class="timeline-phases" id="timeline-phases-${taskId}"></div>
    `;
    
    container.appendChild(timeline);
}

function updateAPTTimelinePhase(taskId, phase, status, successRate = null) {
    const phasesContainer = document.getElementById(`timeline-phases-${taskId}`);
    if (!phasesContainer) return;
    
    let phaseElement = document.querySelector(`#timeline-phases-${taskId} .phase-item[data-phase="${phase}"]`);
    
    if (!phaseElement) {
        phaseElement = document.createElement('div');
        phaseElement.className = 'phase-item';
        phaseElement.setAttribute('data-phase', phase);
        phaseElement.innerHTML = `
            <div class="phase-name">${escapeHtml(phase)}</div>
            <div class="phase-status"></div>
            <div class="phase-progress">
                <div class="progress">
                    <div class="progress-bar phase-progress-bar" style="width: 0%"></div>
                </div>
            </div>
        `;
        phasesContainer.appendChild(phaseElement);
    }
    
    const statusDiv = phaseElement.querySelector('.phase-status');
    const progressBar = phaseElement.querySelector('.phase-progress-bar');
    
    if (status === 'running') {
        statusDiv.innerHTML = '<span class="badge badge-info">En cours...</span>';
    } else if (status === 'completed') {
        const successClass = successRate > 70 ? 'success' : 'warning';
        statusDiv.innerHTML = `<span class="badge badge-${successClass}">Terminé (${successRate}%)</span>`;
        if (progressBar) progressBar.style.width = '100%';
    }
}

function updateAPTTimelineProgress(taskId, phase, progress) {
    const progressBar = document.querySelector(`#timeline-phases-${taskId} .phase-item[data-phase="${phase}"] .phase-progress-bar`);
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
    }
}

function updateAPTTimelineComplete(taskId, overallSuccess) {
    const timeline = document.getElementById(`apt-timeline-${taskId}`);
    if (timeline) {
        const statusSpan = timeline.querySelector('.timeline-status');
        if (statusSpan) {
            statusSpan.textContent = `Terminé (${overallSuccess}%)`;
            statusSpan.className = `timeline-status ${overallSuccess > 70 ? 'success' : 'warning'}`;
        }
    }
}

function updateStealthIndicator(enabled, level) {
    const indicator = document.getElementById('stealth-indicator');
    if (indicator) {
        indicator.style.display = enabled ? 'flex' : 'none';
        if (enabled) {
            indicator.className = `stealth-indicator level-${level}`;
            indicator.title = `Mode furtif: ${level.toUpperCase()}`;
        }
    }
}

function updateStealthMetrics(metrics) {
    const container = document.getElementById('stealth-metrics-display');
    if (!container) return;
    
    container.innerHTML = `
        <div class="metric">Risque détection: <span class="risk-${metrics.detectionRisk}">${metrics.detectionRisk}</span></div>
        <div class="metric">Délai moyen: ${metrics.avgDelay}s</div>
        <div class="metric">TOR: ${metrics.torActive ? '✓' : '✗'}</div>
        <div class="metric">User-Agents aléatoires: ${metrics.randomUserAgents ? '✓' : '✗'}</div>
    `;
}

function addVulnerabilityToList(data) {
    const container = document.getElementById('live-vulnerabilities');
    if (!container) return;
    
    const { vulnerability, target, severity, details, timestamp } = data;
    
    const item = document.createElement('div');
    item.className = `vulnerability-item severity-${severity} fade-in`;
    item.innerHTML = `
        <div class="vuln-header">
            <span class="vuln-type">${escapeHtml(vulnerability)}</span>
            <span class="badge badge-${severity}">${severity.toUpperCase()}</span>
        </div>
        <div class="vuln-target">${escapeHtml(target)}</div>
        <div class="vuln-details">${escapeHtml(details || '')}</div>
        <div class="vuln-time">${new Date(timestamp || Date.now()).toLocaleTimeString('fr-FR')}</div>
    `;
    
    container.insertBefore(item, container.firstChild);
    
    // Limiter à 100 éléments
    while (container.children.length > 100) {
        container.removeChild(container.lastChild);
    }
}

function addStealthAlertToUI(data) {
    const container = document.getElementById('stealth-alerts-container');
    if (!container) return;
    
    const { severity, message, timestamp } = data;
    
    const alert = document.createElement('div');
    alert.className = `stealth-alert severity-${severity}`;
    alert.innerHTML = `
        <div class="alert-icon">${severity === 'high' ? '🔴' : severity === 'medium' ? '🟡' : '🔵'}</div>
        <div class="alert-content">
            <div class="alert-message">${escapeHtml(message)}</div>
            <div class="alert-time">${new Date(timestamp).toLocaleTimeString('fr-FR')}</div>
        </div>
        <button class="alert-close">×</button>
    `;
    
    const closeBtn = alert.querySelector('.alert-close');
    closeBtn.onclick = () => alert.remove();
    
    container.insertBefore(alert, container.firstChild);
    
    setTimeout(() => alert.remove(), 15000);
}

function addSystemAlertToUI(data) {
    const container = document.getElementById('system-alerts');
    if (!container) return;
    
    const { level, message, timestamp, source } = data;
    
    const alert = document.createElement('div');
    alert.className = `system-alert level-${level}`;
    alert.innerHTML = `
        <div class="alert-header">
            <span class="alert-source">${escapeHtml(source || 'Système')}</span>
            <span class="alert-time">${new Date(timestamp).toLocaleTimeString('fr-FR')}</span>
        </div>
        <div class="alert-message">${escapeHtml(message)}</div>
    `;
    
    container.appendChild(alert);
    
    setTimeout(() => alert.remove(), 10000);
}

function updateStealthMetricsDisplay(metrics) {
    const container = document.getElementById('stealth-metrics');
    if (!container) return;
    
    const detectionRiskColors = {
        low: '#4caf50',
        medium: '#ff9800',
        high: '#f44336'
    };
    
    container.innerHTML = `
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Risque détection</div>
                <div class="metric-value" style="color: ${detectionRiskColors[metrics.detectionRisk]}">
                    ${metrics.detectionRisk?.toUpperCase()}
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Délai moyen</div>
                <div class="metric-value">${metrics.avgDelay || 1.5}s</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Efficacité</div>
                <div class="metric-value">${metrics.effectiveness || 0}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Alertes évitées</div>
                <div class="metric-value">${metrics.alertsAvoided || 0}</div>
            </div>
        </div>
    `;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info', duration = 5000) {
    // Utiliser la fonction globale si disponible
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type, duration);
    } else {
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // Fallback simple
        const notif = document.createElement('div');
        notif.className = `temp-notification ${type}`;
        notif.textContent = message;
        notif.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'error' ? '#f44336' : type === 'success' ? '#4caf50' : '#2196f3'};
            color: white;
            border-radius: 8px;
            z-index: 10000;
            animation: slideInRight 0.3s ease;
        `;
        document.body.appendChild(notif);
        setTimeout(() => notif.remove(), duration);
    }
}

// ========================================
// EXPORTS
// ========================================

window.redforgeWebSocket = {
    connect: connectWebSocket,
    disconnect,
    send: sendMessage,
    on,
    off,
    once,
    onConnectionStatus,
    getStatus: getConnectionStatus,
    EVENT_TYPES
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        connectWebSocket,
        disconnect,
        sendMessage,
        on,
        off,
        once,
        onConnectionStatus,
        getConnectionStatus,
        EVENT_TYPES
    };
}

// ========================================
// STYLES DYNAMIQUES
// ========================================

const wsStyles = document.createElement('style');
wsStyles.textContent = `
    .multi-attack-item {
        background: var(--card-bg, white);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #2196f3;
        transition: opacity 0.3s ease;
    }
    
    .multi-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    
    .multi-target {
        font-weight: bold;
    }
    
    .multi-status {
        font-size: 0.85em;
        padding: 2px 8px;
        border-radius: 12px;
    }
    
    .multi-status.running {
        background: #2196f3;
        color: white;
    }
    
    .multi-status.success {
        background: #4caf50;
        color: white;
    }
    
    .multi-status.warning {
        background: #ff9800;
        color: white;
    }
    
    .multi-info {
        display: flex;
        justify-content: space-between;
        font-size: 0.85em;
        color: var(--text-secondary, #666);
        margin-top: 8px;
    }
    
    .apt-timeline {
        background: var(--card-bg, white);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .timeline-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border-color, #eee);
    }
    
    .timeline-header h4 {
        margin: 0;
    }
    
    .timeline-status {
        font-size: 0.85em;
        padding: 2px 8px;
        border-radius: 12px;
    }
    
    .timeline-status.running {
        background: #2196f3;
        color: white;
    }
    
    .timeline-status.success {
        background: #4caf50;
        color: white;
    }
    
    .phase-item {
        margin-bottom: 12px;
        padding: 8px;
        background: var(--bg-secondary, #f5f5f5);
        border-radius: 6px;
    }
    
    .phase-name {
        font-weight: bold;
        margin-bottom: 6px;
    }
    
    .phase-status {
        margin-bottom: 6px;
    }
    
    .stealth-alert {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px;
        margin-bottom: 8px;
        background: var(--card-bg, white);
        border-radius: 6px;
        border-left: 4px solid;
        animation: slideInRight 0.3s ease;
    }
    
    .stealth-alert.severity-high {
        border-left-color: #f44336;
    }
    
    .stealth-alert.severity-medium {
        border-left-color: #ff9800;
    }
    
    .stealth-alert.severity-low {
        border-left-color: #4caf50;
    }
    
    .alert-content {
        flex: 1;
    }
    
    .alert-message {
        font-size: 0.9em;
    }
    
    .alert-time {
        font-size: 0.75em;
        color: var(--text-muted, #999);
    }
    
    .alert-close {
        background: none;
        border: none;
        cursor: pointer;
        font-size: 18px;
        opacity: 0.6;
    }
    
    .alert-close:hover {
        opacity: 1;
    }
    
    .system-alert {
        padding: 10px;
        margin-bottom: 8px;
        background: var(--card-bg, white);
        border-radius: 6px;
        border-left: 4px solid #ff9800;
    }
    
    .system-alert.level-error {
        border-left-color: #f44336;
    }
    
    .alert-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
        font-size: 0.8em;
    }
    
    .alert-source {
        font-weight: bold;
    }
    
    .stealth-indicator {
        display: none;
        align-items: center;
        gap: 6px;
        padding: 4px 8px;
        border-radius: 16px;
        font-size: 0.8em;
    }
    
    .stealth-indicator.level-low {
        background: rgba(76, 175, 80, 0.2);
        color: #4caf50;
    }
    
    .stealth-indicator.level-medium {
        background: rgba(255, 152, 0, 0.2);
        color: #ff9800;
    }
    
    .stealth-indicator.level-high {
        background: rgba(244, 67, 54, 0.2);
        color: #f44336;
    }
    
    .stealth-indicator.level-paranoid {
        background: rgba(156, 39, 176, 0.2);
        color: #9c27b0;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 12px;
    }
    
    .metric-card {
        text-align: center;
        padding: 10px;
        background: var(--bg-secondary, #f5f5f5);
        border-radius: 6px;
    }
    
    .metric-label {
        font-size: 0.75em;
        color: var(--text-secondary, #666);
        margin-bottom: 4px;
    }
    
    .metric-value {
        font-size: 1.25em;
        font-weight: bold;
    }
`;
document.head.appendChild(wsStyles);