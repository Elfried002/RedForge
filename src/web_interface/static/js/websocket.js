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
    
    showNotification(`Opération APT \"${operationName}\" démarrée (niveau furtif: ${stealthLevel})`, 'warning');
    
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
    const { taskId, phase, phaseNumber, totalPhases, duration, result } = data;

    showNotification(`Phase APT ${phaseNumber}/${totalPhases} (${phase}) terminée en ${duration}`,
                     result.success ? 'success' : 'error');

    updateAPTTimelinePhase(taskId, phase, result.success ? 'completed' : 'failed');

    dispatchCustomEvent('aptPhaseComplete', data);
}

function handleAPTCompleted(data) {
    const { taskId, operationName, duration, successfulPhases, totalPhases } = data;

    showNotification(`Opération APT \"${operationName}\" terminée en ${duration}`, 'success');

    updateAPTTimelineComplete(taskId, successfulPhases, totalPhases);

    dispatchCustomEvent('aptCompleted', data);
}

// Furtivité
function handleStealthStatus(data) {
    const { level, evasiveness, detectability } = data;

    updateStealthUI(level, evasiveness, detectability);
    dispatchCustomEvent('stealthStatus', data);
}

function handleStealthAlert(data) {
    const { detectionSource, confidence, timestamp } = data;

    showNotification(`Alerte de furtivité: Détection par ${detectionSource} (confiance: ${confidence}%)`, 'danger');

    addStealthAlertToLog(data);
    dispatchCustomEvent('stealthAlert', data);
}

function handleStealthMetrics(data) {
    updateStealthMetricsChart(data);
    dispatchCustomEvent('stealthMetrics', data);
}

function handleVulnerabilityFound(data) {
    const { vulnerability, target } = data;
    showNotification(`Nouvelle vulnérabilité trouvée sur ${target}: ${vulnerability.name}`, 'warning');

    if (typeof window.addVulnerability === 'function') {
        window.addVulnerability(vulnerability, target);
    }

    dispatchCustomEvent('vulnerabilityFound', data);
}

function handleSessionCreated(data) {
    showNotification(`Nouvelle session: ${data.session.user_ip}`, 'info');
    dispatchCustomEvent('sessionCreated', data);
}

function handleSessionClosed(data) {
    showNotification(`Session fermée: ${data.session_id}`, 'info');
    dispatchCustomEvent('sessionClosed', data);
}

function handleNotification(data) {
    showNotification(data.message, data.type, data.duration);
}

function handleSystemAlert(data) {
    const alertModal = document.getElementById('system-alert-modal');
    if (alertModal) {
        const title = alertModal.querySelector('.modal-title');
        const body = alertModal.querySelector('.modal-body');
        
        if (title) title.textContent = data.title || 'Alerte Système';
        if (body) body.textContent = data.message;
        
        // Afficher la modale (nécessite Bootstrap)
        const modal = new bootstrap.Modal(alertModal);
        modal.show();
    }
}

function handleHeartbeat(data) {
    console.log('Heartbeat reçu:', data.timestamp);
    // Optionnel: mettre à jour un indicateur de statut de connexion
}

// ========================================
// FONCTIONS D'ENVOI DE MESSAGES
// ========================================

function sendMessage(type, data = {}) {
    const message = JSON.stringify({ type, data });
    
    if (socket && (socket.readyState === WebSocket.OPEN || (socket.connected && socket.send))) {
        try {
            socket.send(message);
        } catch (error) {
            console.error('Erreur envoi message:', error);
            enqueueEvent(message);
        }
    } else {
        console.warn('WebSocket non connecté. Message mis en file d'attente.');
        enqueueEvent(message);
    }
}

function subscribeToEvents() {
    sendMessage('subscribe', { events: Object.values(EVENT_TYPES) });
}

// ========================================
// RECONNEXION ET HEARTBEAT
// ========================================

function scheduleReconnect() {
    if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        setTimeout(() => {
            console.log(`Tentative de reconnexion ${reconnectAttempts}/${maxReconnectAttempts}...`);
            connectWebSocket();
        }, reconnectDelay);
        reconnectDelay *= 2; // Backoff exponentiel
    } else {
        console.error('Nombre maximum de tentatives de reconnexion atteint.');
        showNotification('Déconnecté du serveur. Veuillez rafraîchir la page.', 'error');
    }
}

function startHeartbeat() {
    stopHeartbeat();
    heartbeatInterval = setInterval(() => {
        sendMessage('ping', { timestamp: Date.now() });
    }, 30000); // Toutes les 30 secondes
}

function stopHeartbeat() {
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = null;
    }
}

// ========================================
// FILE D'ATTENTE (QUEUE)
// ========================================

function enqueueEvent(message) {
    eventQueue.push(message);
}

function processEventQueue() {
    if (isProcessingQueue) return;
    isProcessingQueue = true;
    
    while (eventQueue.length > 0) {
        const message = eventQueue.shift();
        if (socket && (socket.readyState === WebSocket.OPEN || (socket.connected && socket.send))) {
            socket.send(message);
        } else {
            // Remettre le message dans la file si la connexion est perdue pendant le traitement
            eventQueue.unshift(message);
            break;
        }
    }
    
    isProcessingQueue = false;
}

// ========================================
// GESTIONNAIRES D'ÉVÉNEMENTS PUBLICS
// ========================================

function on(eventType, handler) {
    if (!messageHandlers[eventType]) {
        messageHandlers[eventType] = [];
    }
    messageHandlers[eventType].push(handler);
}

function off(eventType, handler) {
    if (messageHandlers[eventType]) {
        messageHandlers[eventType] = messageHandlers[eventType].filter(h => h !== handler);
    }
}

function addConnectionStatusListener(listener) {
    connectionStatusListeners.push(listener);
}

function removeConnectionStatusListener(listener) {
    connectionStatusListeners = connectionStatusListeners.filter(l => l !== listener);
}

function notifyConnectionStatusListeners(isConnected) {
    connectionStatusListeners.forEach(listener => {
        try {
            listener(isConnected);
        } catch (error) {
            console.error('Erreur dans listener de statut de connexion:', error);
        }
    });
}

// ========================================
// UTILITAIRES
// ========================================

function dispatchCustomEvent(name, detail) {
    const event = new CustomEvent(name, { detail });
    document.dispatchEvent(event);
}

// Exposition de l'API WebSocket au niveau global (si nécessaire)
window.RedForgeSocket = {
    on,
    off,
    sendMessage,
    addConnectionStatusListener,
    removeConnectionStatusListener,
    EVENT_TYPES
};
