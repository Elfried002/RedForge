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
    const { taskId, phase, result } = data;
    
    updateAPTTimelinePhase(taskId, phase, result.success ? 'success' : 'failure');
    dispatchCustomEvent('aptPhaseComplete', data);
}

function handleAPTCompleted(data) {
    const { taskId, operationName, duration, successfulPhases, totalPhases } = data;
    
    showNotification(`Opération APT "${operationName}" terminée en ${duration}`, 
                    successfulPhases === totalPhases ? 'success' : 'error');
    
    dispatchCustomEvent('aptCompleted', data);
}


// Mode furtif
function handleStealthStatus(data) {
    const { taskId, enabled, level, evasionTechniques } = data;
    
    updateStealthUI(taskId, enabled, level, evasionTechniques);
    dispatchCustomEvent('stealthStatus', data);
}

function handleStealthAlert(data) {
    const { taskId, alertType, message, riskLevel } = data;
    
    showStealthAlert(taskId, alertType, message, riskLevel);
    dispatchCustomEvent('stealthAlert', data);
}

function handleStealthMetrics(data) {
    const { taskId, detectionRate, networkFootprint } = data;
    
    updateStealthMetrics(taskId, detectionRate, networkFootprint);
    dispatchCustomEvent('stealthMetrics', data);
}

// Vulnérabilités & Sessions
function handleVulnerabilityFound(data) {
    showNotification(`Nouvelle vulnérabilité trouvée: ${data.name}`, 'warning');
    
    if (typeof window.addVulnerability === 'function') {
        window.addVulnerability(data);
    }
    
    dispatchCustomEvent('vulnerabilityFound', data);
}

function handleSessionCreated(data) {
    showNotification(`Nouvelle session interactive: ${data.type} sur ${data.target}`, 'info');
    dispatchCustomEvent('sessionCreated', data);
}

function handleSessionClosed(data) {
    showNotification(`Session ${data.sessionId} fermée`, 'info');
    dispatchCustomEvent('sessionClosed', data);
}

// Notifications & Alertes
function handleNotification(data) {
    const { message, type, duration } = data;
    showNotification(message, type, duration);
}

function handleSystemAlert(data) {
    const container = document.getElementById('system-alert-container');
    if (!container) return;
    
    const alertType = data.type || 'info';
    const icon = getIconForAlertType(alertType);
    
    container.className = `system-alert alert-${alertType}`;

    const iconEl = document.createElement('i');
    iconEl.className = `${icon} mr-2`;
    
    container.textContent = ` ${data.message}`;
    container.prepend(iconEl);

    container.style.display = 'block';
    
    setTimeout(() => {
        container.style.display = 'none';
    }, data.duration || 5000);
}

function handleHeartbeat() {
    // Rien à faire côté client, juste confirmer la connexion
}


// ========================================
// FONCTIONS UTILITAIRES
// ========================================

function scheduleReconnect() {
    if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        setTimeout(() => {
            console.log(`Tentative de reconnexion #${reconnectAttempts}...`);
            connectWebSocket();
        }, reconnectDelay);
        reconnectDelay *= 2; // Backoff exponentiel
    } else {
        console.error('Nombre maximum de tentatives de reconnexion atteint.');
        showNotification('Déconnecté du serveur. Veuillez rafraîchir la page.', 'error', 0);
    }
}

function startHeartbeat() {
    stopHeartbeat(); // Assurer qu'il n'y en a pas d'autre
    heartbeatInterval = setInterval(() => {
        sendMessage('heartbeat', { timestamp: Date.now() });
    }, 30000);
}

function stopHeartbeat() {
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = null;
    }
}

function sendMessage(type, data = {}) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.warn('WebSocket non connecté. Message mis en file d\'attente:', { type, data });
        eventQueue.push({ type, data });
        return;
    }
    
    const message = JSON.stringify({ type, data });
    
    if (socket.send) { // WebSocket natif
        socket.send(message);
    } else if (socket.emit) { // Socket.IO
        socket.emit(type, data);
    }
}

function subscribeToEvents(events = Object.keys(EVENT_TYPES)) {
    sendMessage('subscribe', { events });
}

function processEventQueue() {
    if (isProcessingQueue || eventQueue.length === 0) return;
    
    isProcessingQueue = true;
    while (eventQueue.length > 0) {
        const { type, data } = eventQueue.shift();
        sendMessage(type, data);
    }
    isProcessingQueue = false;
}

function registerMessageHandler(type, handler) {
    if (!messageHandlers[type]) {
        messageHandlers[type] = [];
    }
    messageHandlers[type].push(handler);
}

function unregisterMessageHandler(type, handler) {
    if (messageHandlers[type]) {
        messageHandlers[type] = messageHandlers[type].filter(h => h !== handler);
    }
}

function addConnectionStatusListener(listener) {
    connectionStatusListeners.push(listener);
}

function notifyConnectionStatusListeners(isConnected) {
    connectionStatusListeners.forEach(listener => listener(isConnected));
}

function dispatchCustomEvent(eventName, detail) {
    const event = new CustomEvent(eventName, { detail });
    document.dispatchEvent(event);
}

// Fonctions de mise à jour de l'UI (exemples)
function updateProgressBar(id, progress) {
    const bar = document.getElementById(id);
    if (bar) {
        bar.style.width = `${progress}%`;
        bar.textContent = `${progress}%`;
    }
}

function updateStatusText(id, text) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = text;
    }
}

function updateStatusIcon(id, status) {
    // Logique pour changer une icône de statut
}

function showNotification(message, type = 'info', duration = 5000) {
    // Utiliser une librairie comme Toastify, Noty, etc.
    console.log(`[${type.toUpperCase()}] ${message}`);
    // Exemple simple:
    const notifContainer = document.getElementById('notification-container');
    if (notifContainer) {
        const notif = document.createElement('div');
        notif.className = `notification notification-${type}`;
        notif.textContent = message;
        notifContainer.appendChild(notif);
        if (duration > 0) {
            setTimeout(() => notif.remove(), duration);
        }
    }
}

function getIconForAlertType(type) {
    switch (type) {
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-triangle';
        case 'warning': return 'fas fa-exclamation-circle';
        default: return 'fas fa-info-circle';
    }
}

// ... autres fonctions UI spécifiques (addMultiAttackToUI, etc.)

// Exporter les fonctions pour une utilisation globale si nécessaire
window.redforge = {
    connect: connectWebSocket,
    send: sendMessage,
    on: registerMessageHandler,
    off: unregisterMessageHandler,
    onConnectionStatusChange: addConnectionStatusListener,
    EVENT_TYPES
};