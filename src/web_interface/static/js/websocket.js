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
        case EVENT_TYPES.ATTACK_STARTED:
            handleAttackStarted(data);
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
        case EVENT_TYPES.VULNERABILITY_UPDATED:
            handleVulnerabilityUpdated(data);
            break;
        case EVENT_TYPES.SESSION_CREATED:
            handleSessionCreated(data);
            break;
        case EVENT_TYPES.SESSION_CLOSED:
            handleSessionClosed(data);
            break;
        case EVENT_TYPES.SESSION_UPDATED:
            handleSessionUpdated(data);
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
        case EVENT_TYPES.PONG:
            // Pong reçu, ne rien faire de spécial ici
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

function handleAttackStarted(data) {
    const { attackId, attackType, target } = data;
    
    showNotification(`Attaque ${attackType} lancée sur ${target}`, 'info');
    
    // Mettre à jour l'UI pour montrer le début de l'attaque
    addAttackToUI(attackId, data);
    dispatchCustomEvent('attackStarted', data);
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
    
    updateAttackUIComplete(attackId, data);
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
    
    showNotification(`Phase APT ${phase} terminée. Résultat: ${result.status}`, 
                    result.success ? 'success' : 'error');
    
    updateAPTTimelinePhase(taskId, phase, result.success ? 'success' : 'failure');
    dispatchCustomEvent('aptPhaseComplete', data);
}

function handleAPTCompleted(data) {
    const { taskId, operationName, duration, successfulPhases, totalPhases } = data;
    
    showNotification(`Opération APT "${operationName}" terminée. ${successfulPhases}/${totalPhases} phases réussies.`, 'success');
    
    updateAPTTimelineComplete(taskId, data);
    dispatchCustomEvent('aptCompleted', data);
}

// Mode furtif
function handleStealthStatus(data) {
    const { level, active, evasionTechniques } = data;
    updateStealthUI(level, active);
    dispatchCustomEvent('stealthStatus', data);
}

function handleStealthAlert(data) {
    const { detectionSource, confidence, timestamp } = data;
    showNotification(`Alerte de furtivité: Détection possible par ${detectionSource} (confiance: ${confidence})`, 'error');
    dispatchCustomEvent('stealthAlert', data);
}

function handleStealthMetrics(data) {
    const { networkNoise, anomalyScore } = data;
    updateStealthMetricsUI(networkNoise, anomalyScore);
    dispatchCustomEvent('stealthMetrics', data);
}

// Vulnérabilités et Sessions
function handleVulnerabilityFound(data) {
    const { cve, severity, target, component } = data;
    showNotification(`Nouvelle vulnérabilité trouvée: ${cve} (${severity}) sur ${target}`, 'warning');
    addVulnerabilityToTable(data);
    dispatchCustomEvent('vulnerabilityFound', data);
}

function handleVulnerabilityUpdated(data) {
    const { cve, status } = data;
    updateVulnerabilityInTable(cve, { status });
    dispatchCustomEvent('vulnerabilityUpdated', data);
}

function handleSessionCreated(data) {
    const { sessionId, type, target } = data;
    showNotification(`Session ${type} établie avec ${target}`, 'success');
    addSessionToList(data);
    dispatchCustomEvent('sessionCreated', data);
}

function handleSessionClosed(data) {
    const { sessionId, reason } = data;
    showNotification(`Session ${sessionId} fermée: ${reason}`, 'info');
    removeSessionFromList(sessionId);
    dispatchCustomEvent('sessionClosed', data);
}

function handleSessionUpdated(data) {
    const { sessionId, status } = data;
    updateSessionInList(sessionId, { status });
    dispatchCustomEvent('sessionUpdated', data);
}

// Notifications et système
function handleNotification(data) {
    const { message, type, duration } = data;
    showNotification(message, type, duration);
}

function handleSystemAlert(data) {
    const { message, level } = data;
    showNotification(`ALERTE SYSTÈME: ${message}`, level, 10000);
    // Potentiellement, afficher une modale pour les alertes critiques
    if (level === 'critical') {
        showCriticalAlertModal(message);
    }
    dispatchCustomEvent('systemAlert', data);
}

// Heartbeat
function handleHeartbeat(data) {
    // console.log('Heartbeat reçu', data.timestamp);
    // Peut être utilisé pour vérifier la latence
}

// ========================================
// COMMUNICATION AVEC LE SERVEUR
// ========================================

function sendMessage(type, data) {
    const message = { type, data };
    
    if (socket && (socket.readyState === WebSocket.OPEN || socket.connected)) {
        if (socket.emit) { // Socket.IO
            socket.emit(type, data);
        } else { // WebSocket Natif
            socket.send(JSON.stringify(message));
        }
    } else {
        console.warn('WebSocket non connecté. Message mis en file dattente:', message);
        eventQueue.push(message);
    }
}

function subscribeToEvents() {
    // Exemple: s'abonner à des canaux spécifiques si l'architecture le requiert
    sendMessage('subscribe', { channels: ['scans', 'attacks', 'system'] });
}

// ========================================
// RECONNEXION ET FIABILITÉ
// ========================================

function scheduleReconnect() {
    if (reconnectAttempts >= maxReconnectAttempts) {
        console.error('Nombre maximum de tentatives de reconnexion atteint.');
        showNotification('Impossible de se reconnecter au serveur.', 'error', null);
        return;
    }
    
    reconnectAttempts++;
    const delay = Math.min(reconnectDelay * Math.pow(2, reconnectAttempts), 30000); // Backoff exponentiel
    console.log(`Tentative de reconnexion dans ${delay / 1000}s... (essai ${reconnectAttempts}/${maxReconnectAttempts})`);
    
    setTimeout(() => {
        connectWebSocket();
    }, delay);
}

function processEventQueue() {
    if (isProcessingQueue) return;
    isProcessingQueue = true;
    
    while (eventQueue.length > 0) {
        const message = eventQueue.shift();
        sendMessage(message.type, message.data);
    }
    
    isProcessingQueue = false;
}

// ========================================
// HEARTBEAT (maintien de la connexion)
// ========================================

function startHeartbeat() {
    stopHeartbeat(); // Assurer qu'il n'y a pas de doublons
    heartbeatInterval = setInterval(() => {
        sendMessage(EVENT_TYPES.PING, { timestamp: Date.now() });
    }, 25000);
}

function stopHeartbeat() {
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = null;
    }
}

// ========================================
// GESTIONNAIRES D'ÉVÉNEMENTS PUBLICS
// ========================================

/**
 * Permet à d'autres scripts d'écouter les messages WebSocket.
 * @param {string} eventType Le type d'événement (ex: 'scan_progress')
 * @param {function} callback La fonction à appeler avec les données
 */
function on(eventType, callback) {
    if (!messageHandlers[eventType]) {
        messageHandlers[eventType] = [];
    }
    messageHandlers[eventType].push(callback);
}

/**
 * Permet de ne plus écouter un événement.
 * @param {string} eventType Le type d'événement
 * @param {function} callback La fonction à retirer
 */
function off(eventType, callback) {
    if (messageHandlers[eventType]) {
        messageHandlers[eventType] = messageHandlers[eventType].filter(h => h !== callback);
    }
}

/**
 * Permet d'écouter les changements de statut de la connexion.
 * @param {function} listener Callback appelé avec true (connecté) or false (déconnecté)
 */
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
            console.error('Erreur dans un listener de statut de connexion:', error);
        }
    });
}

// ========================================
// UTILITAIRES UI (notifications, etc.)
// ========================================

/**
 * Affiche une notification à l'utilisateur.
 * Utilise une librairie comme Noty.js ou une implémentation custom.
 * @param {string} message Le message à afficher
 * @param {string} type 'success', 'error', 'warning', 'info'
 * @param {number} duration Durée en ms avant la fermeture auto
 */
function showNotification(message, type = 'info', duration = 5000) {
    if (typeof Noty === 'function') {
        new Noty({
            theme: 'mint',
            layout: 'topRight',
            text: message,
            type: type,
            timeout: duration,
            progressBar: true,
            killer: true
        }).show();
    } else {
        // Fallback simple
        const notif = document.createElement('div');
        notif.className = `fallback-notification notification-${type}`;
        const p = document.createElement('p');
        p.textContent = message;
        notif.appendChild(p);
        document.body.appendChild(notif);
        setTimeout(() => notif.remove(), duration);
    }
}

/**
 * Met à jour une barre de progression.
 * @param {string} elementId ID de l'élément de la barre de progression
 * @param {number} progress Pourcentage de progression (0-100)
 */
function updateProgressBar(elementId, progress) {
    const progressBar = document.getElementById(elementId);
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
        progressBar.textContent = `${Math.round(progress)}%`;
        progressBar.setAttribute('aria-valuenow', progress);
    }
}

/**
 * Met à jour un texte de statut.
 * @param {string} elementId ID de l'élément de texte
 * @param {string} text Le nouveau texte
 */
function updateStatusText(elementId, text) {
    const statusElement = document.getElementById(elementId);
    if (statusElement) {
        statusElement.textContent = text;
    }
}

/**
 * Met à jour une icône de statut.
 * @param {string} elementId ID de l'icône
 * @param {string} status Le nouveau statut (ex: 'running', 'success', 'failed')
 */
function updateStatusIcon(elementId, status) {
    const iconElement = document.getElementById(elementId);
    if (iconElement) {
        // Logique pour changer la classe de l'icône en fonction du statut
        iconElement.className = `status-icon icon-${status}`;
    }
}

/**
 * Crée un événement personnalisé et le distribue.
 * @param {string} eventName Nom de l'événement
 * @param {object} detail Données à attacher à l'événement
 */
function dispatchCustomEvent(eventName, detail) {
    const event = new CustomEvent(eventName, { detail });
    document.dispatchEvent(event);
}

// ========================================
// EXPORT (si utilisé comme module)
// ========================================

// Pourrait être exposé pour une utilisation dans d'autres parties de l'application
const RedForgeWebSocket = {
    connect: connectWebSocket,
    send: sendMessage,
    on: on,
    off: off,
    addConnectionStatusListener: addConnectionStatusListener,
    removeConnectionStatusListener: removeConnectionStatusListener,
    EVENT_TYPES
};

// Exposer globalement si pas de système de modules
if (typeof window.RedForgeWebSocket === 'undefined') {
    window.RedForgeWebSocket = RedForgeWebSocket;
}