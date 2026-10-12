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

/**
 * Nettoie une chaîne de caractères pour prévenir les attaques XSS en échappant les caractères HTML.
 * @param {*} str La chaîne à nettoyer.
 * @returns {*} La chaîne nettoyée, ou la valeur originale si ce n'est pas une chaîne.
 */
function escapeHTML(str) {
    if (typeof str !== 'string') {
        return str;
    }
    const p = document.createElement('p');
    p.textContent = str;
    return p.innerHTML;
}

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
    updateStatusText(`scan-status-${taskId}`, escapeHTML(message));
    
    // Émettre un événement personnalisé
    dispatchCustomEvent('scanProgress', data);
}

function handleScanCompleted(data) {
    const { taskId, target, duration, results } = data;
    
    showNotification(`Scan de ${escapeHTML(target)} terminé en ${escapeHTML(duration)}`, 'success');
    
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
        updateStatusText(`attack-step-${attackId}`, escapeHTML(currentStep));
    }
    
    dispatchCustomEvent('attackProgress', data);
}

function handleAttackCompleted(data) {
    const { attackId, attackType, result, duration } = data;
    
    const status = result.success ? 'réussie' : 'échouée';
    const notifType = result.success ? 'success' : 'error';
    showNotification(`Attaque ${escapeHTML(attackType)} ${status} en ${escapeHTML(duration)}`, notifType);
    
    dispatchCustomEvent('attackCompleted', data);
}

// Multi-attaques
function handleMultiAttackStarted(data) {
    const { taskId, target, attackCount, stealthLevel } = data;
    
    showNotification(`Multi-attaque lancée sur ${escapeHTML(target)} (${escapeHTML(attackCount)} attaques, furtivité: ${escapeHTML(stealthLevel)})`, 'info');
    
    addMultiAttackToUI(taskId, data);
    dispatchCustomEvent('multiAttackStarted', data);
}

function handleMultiAttackProgress(data) {
    const { taskId, currentAttack, progress, completedCount, totalCount } = data;
    
    updateProgressBar(`multi-progress-${taskId}`, progress);
    updateStatusText(`multi-current-${taskId}`, escapeHTML(currentAttack));
    updateStatusText(`multi-count-${taskId}`, `${escapeHTML(completedCount)}/${escapeHTML(totalCount)}`);
    
    dispatchCustomEvent('multiAttackProgress', data);
}

function handleMultiAttackCompleted(data) {
    const { taskId, successful, totalAttacks, duration } = data;
    
    showNotification(`Multi-attaque terminée: ${escapeHTML(successful)}/${escapeHTML(totalAttacks)} réussies en ${escapeHTML(duration)}`, 
                    successful === totalAttacks ? 'success' : 'warning');
    
    updateMultiAttackUIComplete(taskId, data);
    dispatchCustomEvent('multiAttackCompleted', data);
}

// Opérations APT
function handleAPTStarted(data) {
    const { taskId, operationName, totalPhases, stealthLevel } = data;
    
    showNotification(`Opération APT \"${escapeHTML(operationName)}\" démarrée (niveau furtif: ${escapeHTML(stealthLevel)})`, 'warning');
    
    createAPTTimeline(taskId, operationName, totalPhases);
    dispatchCustomEvent('aptStarted', data);
}

function handleAPTPhaseStart(data) {
    const { taskId, phase, phaseNumber, totalPhases, attacksCount } = data;
    
    showNotification(`Phase APT ${escapeHTML(phaseNumber)}/${escapeHTML(totalPhases)}: ${escapeHTML(phase)} (${escapeHTML(attacksCount)} attaques)`, 'info');
    
    updateAPTTimelinePhase(taskId, phase, 'running');
    dispatchCustomEvent('aptPhaseStart', data);
}

function handleAPTPhaseProgress(data) {
    const { taskId, phase, progress, currentAttack } = data;
    
    updateAPTTimelineProgress(taskId, phase, progress);
    if (currentAttack) {
        updateStatusText(`apt-phase-${taskId}-${phase}`, escapeHTML(currentAttack));
    }
    
    dispatchCusto