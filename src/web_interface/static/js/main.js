/**
 * RedForge - Script Principal Amélioré
 * Plateforme d'Orchestration de Pentest Web
 * Version: 2.0.0
 * Support: Multi-Attacks, Stealth Mode, APT Operations
 */

// ========================================
// INITIALISATION
// ========================================

let socket = null;
let globalState = {
    theme: 'light',
    sidebarCollapsed: false,
    stealthMode: false,
    currentStealthLevel: 'medium',
    notificationsEnabled: true,
    realTimeUpdates: true,
    activeAPTOperations: [],
    pendingMultiAttacks: []
};

document.addEventListener('DOMContentLoaded', function() {
    console.log('RedForge - Plateforme de Pentest Web v2.0.0 (Multi-Attacks & APT Support)');
    
    // Initialiser les composants
    initWebSocket();
    initTheme();
    initSidebar();
    initTooltips();
    initDropdowns();
    initModals();
    initForms();
    initNotifications();
    initKeyboardShortcuts();
    initGlobalSearch();
    initPerformanceMonitoring();
    
    // Charger les données initiales
    loadInitialData();
    
    // Démarrer les mises à jour en temps réel
    if (globalState.realTimeUpdates) {
        startRealTimeUpdates();
    }
});

// ========================================
// WEBSOCKET POUR COMMUNICATION TEMPS RÉEL
// ========================================

function initWebSocket() {
    socket = io({
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
    });
    
    socket.on('connect', () => {
        console.log('WebSocket connecté');
        updateConnectionStatus(true);
        showNotification('Connecté au serveur en temps réel', 'success', 2000);
    });
    
    socket.on('disconnect', () => {
        console.log('WebSocket déconnecté');
        updateConnectionStatus(false);
        showNotification('Connexion temps réel perdue', 'warning', 3000);
    });
    
    socket.on('reconnect', () => {
        console.log('WebSocket reconnecté');
        showNotification('Reconnexion établie', 'success', 2000);
    });
    
    socket.on('scan_status', (data) => {
        handleScanStatusUpdate(data);
    });
    
    socket.on('attack_progress', (data) => {
        handleAttackProgressUpdate(data);
    });
    
    socket.on('multi_attack_update', (data) => {
        handleMultiAttackUpdate(data);
    });
    
    socket.on('apt_phase_update', (data) => {
        handleAPTPhaseUpdate(data);
    });
    
    socket.on('stealth_alert', (data) => {
        handleStealthAlert(data);
    });
    
    socket.on('notification', (data) => {
        showNotification(data.message, data.type, data.duration);
    });
}

function updateConnectionStatus(connected) {
    const statusIndicator = document.querySelector('.connection-status');
    if (statusIndicator) {
        statusIndicator.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
        statusIndicator.title = connected ? 'Connecté en temps réel' : 'Déconnecté';
    }
}

function handleScanStatusUpdate(data) {
    const progressBar = document.getElementById(`scan-progress-${data.task_id}`);
    if (progressBar) {
        progressBar.style.width = `${data.progress}%`;
        progressBar.setAttribute('aria-valuenow', data.progress);
    }
    
    const statusText = document.getElementById(`scan-status-${data.task_id}`);
    if (statusText && data.message) {
        statusText.textContent = data.message;
    }
}

function handleAttackProgressUpdate(data) {
    const element = document.getElementById(`attack-${data.attack_id}`);
    if (element) {
        const progressBar = element.querySelector('.progress-bar');
        if (progressBar) progressBar.style.width = `${data.progress}%`;
        
        const statusIcon = element.querySelector('.attack-status');
        if (statusIcon && data.status) {
            statusIcon.className = `attack-status status-${data.status}`;
            statusIcon.textContent = getStatusIcon(data.status);
        }
    }
    
    // Mettre à jour le dashboard si nécessaire
    if (window.updateAttackProgress) {
        window.updateAttackProgress(data);
    }
}

function handleMultiAttackUpdate(data) {
    const container = document.getElementById('multi-attack-progress');
    if (container) {
        const attackElement = document.getElementById(`multi-${data.task_id}`);
        if (!attackElement) {
            addMultiAttackToUI(data);
        } else {
            updateMultiAttackUI(data);
        }
    }
    
    showNotification(`Multi-attaque: ${data.current_attack || 'En cours'} (${data.progress}%)`, 'info', 2000);
}

function handleAPTPhaseUpdate(data) {
    const timeline = document.getElementById('apt-timeline');
    if (timeline) {
        updateAPTTimeline(data);
    }
    
    showNotification(`Phase APT: ${data.phase_name} - ${data.status}`, 
                    data.status === 'completed' ? 'success' : 'info', 3000);
}

function handleStealthAlert(data) {
    const alertContainer = document.getElementById('stealth-alerts');
    if (alertContainer) {
        const alert = createStealthAlert(data);
        alertContainer.appendChild(alert);
        
        setTimeout(() => alert.remove(), 10000);
    }
    
    if (data.severity === 'high') {
        showNotification(`⚠️ Alerte furtive: ${data.message}`, 'warning', 5000);
    }
}

// ========================================
// GESTION DU THÈME (amélioré)
// ========================================

function initTheme() {
    // Récupérer le thème sauvegardé
    const savedTheme = localStorage.getItem('redforge-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.body.classList.add('dark-theme');
        globalState.theme = 'dark';
    }
    
    // Ajouter le bouton de basculement
    const themeToggle = createThemeToggle();
    
    const headerActions = document.querySelector('.header-actions');
    if (headerActions) {
        headerActions.appendChild(themeToggle);
    }
    
    // Ajouter le sélecteur de thème avancé
    addAdvancedThemeSelector();
}

function createThemeToggle() {
    const themeToggle = document.createElement('button');
    themeToggle.className = 'theme-toggle';
    themeToggle.innerHTML = globalState.theme === 'dark' ? '☀️' : '🌙';
    themeToggle.title = 'Changer de thème';
    themeToggle.onclick = toggleTheme;
    return themeToggle;
}

function addAdvancedThemeSelector() {
    const selector = document.createElement('div');
    selector.className = 'theme-selector dropdown';
    selector.innerHTML = `
        <button class="dropdown-toggle theme-settings" title="Paramètres d'affichage">
            ⚙️
        </button>
        <div class="dropdown-menu">
            <div class="theme-option" data-theme="light">☀️ Thème clair</div>
            <div class="theme-option" data-theme="dark">🌙 Thème sombre</div>
            <div class="theme-option" data-theme="auto">🔄 Auto (système)</div>
            <hr>
            <div class="theme-option" data-font="small">🔤 Police petite</div>
            <div class="theme-option" data-font="medium">🔤 Police moyenne</div>
            <div class="theme-option" data-font="large">🔤 Police grande</div>
            <hr>
            <div class="theme-option" data-density="compact">📐 Compact</div>
            <div class="theme-option" data-density="comfortable">📐 Confortable</div>
        </div>
    `;
    
    const headerActions = document.querySelector('.header-actions');
    if (headerActions) {
        headerActions.appendChild(selector);
        initThemeSelectorEvents(selector);
    }
}

function initThemeSelectorEvents(selector) {
    selector.querySelectorAll('.theme-option[data-theme]').forEach(option => {
        option.addEventListener('click', () => {
            const theme = option.dataset.theme;
            if (theme === 'auto') {
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                setTheme(prefersDark ? 'dark' : 'light');
                localStorage.removeItem('redforge-theme');
            } else {
                setTheme(theme);
                localStorage.setItem('redforge-theme', theme);
            }
        });
    });
    
    selector.querySelectorAll('[data-font]').forEach(option => {
        option.addEventListener('click', () => {
            const fontSize = option.dataset.font;
            document.body.style.fontSize = getFontSizeValue(fontSize);
            localStorage.setItem('redforge-font-size', fontSize);
        });
    });
    
    selector.querySelectorAll('[data-density]').forEach(option => {
        option.addEventListener('click', () => {
            const density = option.dataset.density;
            document.body.classList.toggle('compact-mode', density === 'compact');
            localStorage.setItem('redforge-density', density);
        });
    });
}

function getFontSizeValue(size) {
    const sizes = { small: '12px', medium: '14px', large: '16px' };
    return sizes[size] || '14px';
}

function setTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }
    globalState.theme = theme;
    
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'dark' ? '☀️' : '🌙';
    }
}

function toggleTheme() {
    const newTheme = globalState.theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('redforge-theme', newTheme);
    showNotification(`Thème ${newTheme === 'dark' ? 'sombre' : 'clair'} activé`, 'info', 1500);
}

// ========================================
// GESTION DE LA SIDEBAR (améliorée)
// ========================================

function initSidebar() {
    // Navigation active
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.sidebar-nav-item');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.includes(href)) {
            item.classList.add('active');
        }
    });
    
    // Sidebar collapsible
    initCollapsibleSidebar();
    
    // Menu mobile
    initMobileSidebar();
    
    // Ajouter des indicateurs de notification sur la sidebar
    addSidebarBadges();
}

function initCollapsibleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const collapseBtn = document.createElement('button');
    collapseBtn.className = 'sidebar-collapse-btn';
    collapseBtn.innerHTML = '◀';
    collapseBtn.title = 'Réduire la sidebar';
    collapseBtn.onclick = () => toggleSidebarCollapse();
    
    const sidebarHeader = document.querySelector('.sidebar-header');
    if (sidebarHeader) {
        sidebarHeader.appendChild(collapseBtn);
    }
    
    const savedState = localStorage.getItem('redforge-sidebar-collapsed');
    if (savedState === 'true') {
        toggleSidebarCollapse(true);
    }
}

function toggleSidebarCollapse(skipAnimation = false) {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
        globalState.sidebarCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('redforge-sidebar-collapsed', globalState.sidebarCollapsed);
        
        const collapseBtn = document.querySelector('.sidebar-collapse-btn');
        if (collapseBtn) {
            collapseBtn.innerHTML = globalState.sidebarCollapsed ? '▶' : '◀';
        }
        
        if (mainContent) {
            mainContent.classList.toggle('sidebar-collapsed', globalState.sidebarCollapsed);
        }
    }
}

function initMobileSidebar() {
    const menuToggle = document.createElement('button');
    menuToggle.className = 'menu-toggle show-on-mobile';
    menuToggle.innerHTML = '☰';
    menuToggle.onclick = toggleMobileSidebar;
    
    const header = document.querySelector('.header');
    if (header) {
        header.insertBefore(menuToggle, header.firstChild);
    }
    
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    overlay.onclick = closeMobileSidebar;
    document.body.appendChild(overlay);
}

function toggleMobileSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar) {
        sidebar.classList.toggle('mobile-open');
    }
    if (overlay) {
        overlay.classList.toggle('active');
        document.body.style.overflow = overlay.classList.contains('active') ? 'hidden' : '';
    }
}

function closeMobileSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar) {
        sidebar.classList.remove('mobile-open');
    }
    if (overlay) {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function addSidebarBadges() {
    const navItems = document.querySelectorAll('.sidebar-nav-item');
    
    navItems.forEach(item => {
        const badge = document.createElement('span');
        badge.className = 'sidebar-badge';
        
        // Ajouter des badges basés sur la page
        const href = item.getAttribute('href');
        if (href === '/attacks') {
            badge.textContent = getPendingAttacksCount();
        } else if (href === '/reports') {
            badge.textContent = getUnreadReportsCount();
        }
        
        if (badge.textContent && parseInt(badge.textContent) > 0) {
            item.appendChild(badge);
        }
    });
}

// ========================================
// RACCOURCIS CLAVIER
// ========================================

function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl + S : Sauvegarder
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            handleSaveShortcut();
        }
        
        // Ctrl + D : Dashboard
        if (e.ctrlKey && e.key === 'd') {
            e.preventDefault();
            window.location.href = '/dashboard';
        }
        
        // Ctrl + A : Attaques
        if (e.ctrlKey && e.key === 'a') {
            e.preventDefault();
            window.location.href = '/attacks';
        }
        
        // Ctrl + R : Rafraîchir
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            location.reload();
        }
        
        // Ctrl + Shift + S : Mode furtif
        if (e.ctrlKey && e.shiftKey && e.key === 'S') {
            e.preventDefault();
            toggleStealthMode();
        }
        
        // Ctrl + Shift + A : Arrêter toutes les attaques
        if (e.ctrlKey && e.shiftKey && e.key === 'A') {
            e.preventDefault();
            stopAllAttacks();
        }
        
        // Échap : Fermer modals
        if (e.key === 'Escape') {
            closeAllModals();
        }
        
        // F1 : Aide
        if (e.key === 'F1') {
            e.preventDefault();
            showHelp();
        }
    });
}

function handleSaveShortcut() {
    const activeForm = document.querySelector('form:focus-within');
    if (activeForm) {
        const saveBtn = activeForm.querySelector('[type="submit"]');
        if (saveBtn) saveBtn.click();
    }
}

function toggleStealthMode() {
    globalState.stealthMode = !globalState.stealthMode;
    showNotification(`Mode furtif ${globalState.stealthMode ? 'activé' : 'désactivé'}`, 
                    globalState.stealthMode ? 'warning' : 'info', 2000);
    
    const stealthIndicator = document.querySelector('.stealth-indicator');
    if (stealthIndicator) {
        stealthIndicator.style.display = globalState.stealthMode ? 'flex' : 'none';
    }
}

function stopAllAttacks() {
    if (confirm('Voulez-vous arrêter toutes les attaques en cours ?')) {
        fetch('/api/attacks/stop-all', { method: 'POST' })
            .then(() => showNotification('Toutes les attaques ont été arrêtées', 'success'))
            .catch(() => showNotification('Erreur lors de l\'arrêt des attaques', 'error'));
    }
}

function closeAllModals() {
    document.querySelectorAll('.modal.active').forEach(modal => {
        closeModal(modal);
    });
}

function showHelp() {
    const helpModal = document.getElementById('help-modal');
    if (helpModal) {
        openModal(helpModal);
    } else {
        window.location.href = '/help';
    }
}

// ========================================
// RECHERCHE GLOBALE
// ========================================

function initGlobalSearch() {
    const searchContainer = document.createElement('div');
    searchContainer.className = 'global-search';
    searchContainer.innerHTML = `
        <input type="text" id="global-search-input" placeholder="🔍 Rechercher... (Ctrl+K)" class="form-input">
        <div id="global-search-results" class="search-results"></div>
    `;
    
    const headerActions = document.querySelector('.header-actions');
    if (headerActions) {
        headerActions.insertBefore(searchContainer, headerActions.firstChild);
    }
    
    const searchInput = document.getElementById('global-search-input');
    if (searchInput) {
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'k' && e.ctrlKey) {
                e.preventDefault();
                searchInput.focus();
            }
        });
        
        searchInput.addEventListener('input', debounce(performGlobalSearch, 300));
        
        // Fermer les résultats en cliquant ailleurs
        document.addEventListener('click', (e) => {
            if (!searchContainer.contains(e.target)) {
                const results = document.getElementById('global-search-results');
                if (results) results.style.display = 'none';
            }
        });
    }
}

async function performGlobalSearch() {
    const searchInput = document.getElementById('global-search-input');
    const query = searchInput.value.trim();
    const resultsContainer = document.getElementById('global-search-results');
    
    if (!resultsContainer) return;
    
    if (query.length < 2) {
        resultsContainer.style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        
        displaySearchResults(results, resultsContainer);
        resultsContainer.style.display = 'block';
    } catch (error) {
        console.error('Erreur recherche:', error);
    }
}

function displaySearchResults(results, container) {
    if (!results.length) {
        container.innerHTML = '<div class="search-no-results">Aucun résultat trouvé</div>';
        return;
    }
    
    container.innerHTML = `
        <div class="search-results-header">
            <span>${results.length} résultat(s)</span>
        </div>
        ${results.map(result => `
            <div class="search-result-item" data-url="${result.url}">
                <div class="result-icon">${result.icon || '📄'}</div>
                <div class="result-content">
                    <div class="result-title">${escapeHtml(result.title)}</div>
                    <div class="result-description">${escapeHtml(result.description || '')}</div>
                </div>
            </div>
        `).join('')}
    `;
    
    container.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
            window.location.href = item.dataset.url;
        });
    });
}

// ========================================
// PERFORMANCES
// ========================================

function initPerformanceMonitoring() {
    if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'largest-contentful-paint') {
                    console.log(`LCP: ${entry.renderTime || entry.loadTime}ms`);
                }
            }
        });
        observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input'] });
    }
    
    // Monitorer les métriques personnalisées
    setInterval(() => {
        if (window.performance && window.performance.memory) {
            const memory = window.performance.memory;
            if (memory.usedJSHeapSize > memory.jsHeapSizeLimit * 0.8) {
                console.warn('Utilisation mémoire élevée');
                showNotification('Utilisation mémoire élevée, envisagez de rafraîchir la page', 'warning', 5000);
            }
        }
    }, 60000);
}

// ========================================
// MISE À JOUR EN TEMPS RÉEL
// ========================================

function startRealTimeUpdates() {
    setInterval(async () => {
        if (document.hidden) return; // Ne pas mettre à jour si l'onglet est inactif
        
        try {
            const response = await fetch('/api/status');
            if (response.ok) {
                const status = await response.json();
                updateRealTimeIndicators(status);
            }
        } catch (error) {
            console.debug('Erreur mise à jour temps réel:', error);
        }
    }, 10000);
}

function updateRealTimeIndicators(status) {
    const indicators = {
        'active-attacks-count': status.activeAttacks,
        'active-apt-count': status.activeAPTOperations,
        'stealth-score': status.stealthScore,
        'response-time': `${status.responseTime}ms`
    };
    
    for (const [id, value] of Object.entries(indicators)) {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    }
}

// ========================================
// GESTION DES NOTIFICATIONS (améliorée)
// ========================================

function initNotifications() {
    const container = document.createElement('div');
    container.className = 'notification-container';
    document.body.appendChild(container);
    
    // Demander la permission pour les notifications push
    if ('Notification' in window && Notification.permission === 'default') {
        setTimeout(() => {
            Notification.requestPermission();
        }, 5000);
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    const container = document.querySelector('.notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">${getNotificationIcon(type)}</div>
            <div class="notification-message">${escapeHtml(message)}</div>
            <button class="notification-close">×</button>
        </div>
        <div class="notification-progress" style="animation-duration: ${duration}ms"></div>
    `;
    
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.onclick = () => notification.remove();
    
    container.appendChild(notification);
    
    // Notification push si autorisée et page cachée
    if (document.hidden && 'Notification' in window && Notification.permission === 'granted') {
        new Notification('RedForge', { body: message, icon: '/static/favicon.ico' });
    }
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

// ========================================
// UTILITAIRES (conservés et améliorés)
// ========================================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
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

function getNotificationIcon(type) {
    const icons = {
        success: '✓',
        error: '✗',
        warning: '⚠',
        info: 'ℹ'
    };
    return icons[type] || 'ℹ';
}

// ========================================
// CHARGEMENT DES DONNÉES INITIALES (amélioré)
// ========================================

async function loadInitialData() {
    try {
        const [config, targets, stealthConfig, aptOps] = await Promise.all([
            fetch('/api/config').then(r => r.json()).catch(() => ({})),
            fetch('/api/targets').then(r => r.json()).catch(() => ({ targets: [] })),
            fetch('/api/stealth/profiles').then(r => r.json()).catch(() => ({ profiles: {} })),
            fetch('/api/apt/operations').then(r => r.json()).catch(() => ({ predefined: [] }))
        ]);
        
        window.redforgeConfig = config;
        window.redforgeTargets = targets.targets || [];
        window.redforgeStealthProfiles = stealthConfig.profiles || {};
        window.redforgeAPTOperations = aptOps.predefined || [];
        
        console.log(`Données initiales chargées: ${window.redforgeTargets.length} cibles, ${window.redforgeAPTOperations.length} opérations APT`);
        
    } catch (error) {
        console.error('Erreur chargement données initiales:', error);
    }
}

// ========================================
// EXPORTS
// ========================================

window.showNotification = showNotification;
window.toggleStealthMode = toggleStealthMode;
window.stopAllAttacks = stopAllAttacks;
window.globalState = globalState;

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showNotification,
        toggleStealthMode,
        stopAllAttacks,
        globalState
    };
}

// Ajouter les styles dynamiques
const dynamicStyles = document.createElement('style');
dynamicStyles.textContent = `
    .connection-status {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    .connection-status.connected {
        background-color: #4caf50;
        box-shadow: 0 0 5px #4caf50;
    }
    .connection-status.disconnected {
        background-color: #f44336;
    }
    
    .sidebar-badge {
        background-color: #f44336;
        color: white;
        border-radius: 10px;
        padding: 2px 6px;
        font-size: 10px;
        margin-left: auto;
    }
    
    .global-search {
        position: relative;
        margin-right: 10px;
    }
    
    .global-search input {
        width: 200px;
        padding: 6px 10px;
        font-size: 12px;
    }
    
    .search-results {
        position: absolute;
        top: 100%;
        right: 0;
        width: 400px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 1000;
        display: none;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .dark-theme .search-results {
        background: #2d2d2d;
        color: #e0e0e0;
    }
    
    .search-result-item {
        padding: 10px;
        cursor: pointer;
        display: flex;
        gap: 10px;
        border-bottom: 1px solid #eee;
    }
    
    .search-result-item:hover {
        background: #f5f5f5;
    }
    
    .dark-theme .search-result-item:hover {
        background: #3d3d3d;
    }
    
    .notification-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .notification {
        min-width: 300px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        overflow: hidden;
        animation: slideInRight 0.3s ease;
    }
    
    .dark-theme .notification {
        background: #2d2d2d;
        color: #e0e0e0;
    }
    
    .notification-content {
        padding: 12px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .notification-progress {
        height: 3px;
        background: #4caf50;
        animation: progressBar linear forwards;
    }
    
    @keyframes progressBar {
        from { width: 100%; }
        to { width: 0%; }
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification-close {
        margin-left: auto;
        background: none;
        border: none;
        cursor: pointer;
        font-size: 18px;
        opacity: 0.6;
    }
    
    .notification-close:hover {
        opacity: 1;
    }
`;
document.head.appendChild(dynamicStyles);