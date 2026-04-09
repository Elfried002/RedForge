#!/bin/bash
# ========================================
# RedForge - Script de désinstallation v2.0
# Supprime complètement RedForge du système
# Support Multi-Attacks, Stealth Mode, APT Operations
# ========================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Bannière
show_banner() {
    echo -e "${RED}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║              DÉSINSTALLATION DE REDFORGE v2.0                    ║
║     Multi-Attacks | Mode Furtif | Opérations APT                 ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Variables
REDFORGE_HOME="/opt/RedForge"
REDFORGE_USER_HOME="${HOME}/.RedForge"
LOG_FILE="/tmp/redforge_uninstall.log"
BACKUP_DIR="${HOME}/RedForge_backup_$(date +%Y%m%d_%H%M%S)"
VENV_DIR="/opt/RedForge/venv"

# Nouveaux répertoires v2.0
STEALTH_DIR="${REDFORGE_USER_HOME}/stealth"
MULTI_ATTACK_DIR="${REDFORGE_USER_HOME}/multi_attack"
APT_OPERATIONS_DIR="${REDFORGE_USER_HOME}/apt_operations"
PERSISTENCE_DIR="${REDFORGE_USER_HOME}/persistence"
UPLOADS_DIR="${REDFORGE_USER_HOME}/uploads"
WORDLISTS_CUSTOM_DIR="${REDFORGE_USER_HOME}/wordlists/custom"

# Fonctions
log() {
    echo -e "${GREEN}[+]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[-]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1" >> "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[*]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" >> "$LOG_FILE"
}

# Vérification des droits root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Ce script doit être exécuté en tant que root"
        echo "Veuillez exécuter: sudo ./uninstall.sh"
        exit 1
    fi
}

# Confirmation améliorée
confirm_uninstall() {
    echo ""
    log_warning "⚠️  ATTENTION : Cette action va supprimer complètement RedForge v2.0"
    echo ""
    echo "Seront supprimés :"
    echo "  📁 ${REDFORGE_HOME} (application)"
    echo "  📁 ${REDFORGE_USER_HOME} (configuration, logs, rapports)"
    echo "  📁 ${STEALTH_DIR} (configuration furtive)"
    echo "  📁 ${MULTI_ATTACK_DIR} (données multi-attaques)"
    echo "  📁 ${APT_OPERATIONS_DIR} (opérations APT)"
    echo "  📁 ${PERSISTENCE_DIR} (persistance APT)"
    echo "  📁 ${UPLOADS_DIR} (fichiers uploadés)"
    echo "  📁 ${WORDLISTS_CUSTOM_DIR} (wordlists personnalisées)"
    echo "  🔗 /usr/local/bin/RedForge, /usr/local/bin/redforge, /usr/local/bin/redforge-python"
    echo "  🐍 Environnement virtuel Python"
    echo "  🖥️  Service systemd redforge.service"
    echo ""
    echo "Souhaitez-vous sauvegarder la configuration ?"
    echo "  1) Oui, sauvegarder la configuration complète"
    echo "  2) Sauvegarde sélective (choisir ce qui est important)"
    echo "  3) Non, supprimer définitivement"
    echo "  4) Annuler"
    echo ""
    read -p "Votre choix [1-4]: " choice
    
    case $choice in
        1)
            BACKUP=1
            BACKUP_SELECTIVE=0
            log "Sauvegarde complète dans ${BACKUP_DIR}"
            ;;
        2)
            BACKUP=1
            BACKUP_SELECTIVE=1
            log "Sauvegarde sélective"
            ;;
        3)
            BACKUP=0
            BACKUP_SELECTIVE=0
            log_warning "Suppression définitive sans sauvegarde"
            ;;
        4)
            log "Désinstallation annulée"
            exit 0
            ;;
        *)
            log_error "Choix invalide"
            exit 1
            ;;
    esac
    
    echo ""
    read -p "Êtes-vous sûr de vouloir continuer ? (o/N): " confirm
    if [[ ! "$confirm" =~ ^[oO]$ ]]; then
        log "Désinstallation annulée"
        exit 0
    fi
}

# Sauvegarde sélective
backup_selective() {
    echo ""
    log_info "Sauvegarde sélective - Choisissez les éléments à conserver:"
    echo ""
    
    # Configuration
    read -p "Sauvegarder la configuration ? (o/N): " save_config
    # Rapports
    read -p "Sauvegarder les rapports ? (o/N): " save_reports
    # Wordlists personnalisées
    read -p "Sauvegarder les wordlists personnalisées ? (o/N): " save_wordlists
    # Opérations APT personnalisées
    read -p "Sauvegarder les opérations APT personnalisées ? (o/N): " save_apt_ops
    # Configuration furtive
    read -p "Sauvegarder la configuration furtive ? (o/N): " save_stealth
    # Sessions
    read -p "Sauvegarder les sessions ? (o/N): " save_sessions
    
    mkdir -p "$BACKUP_DIR"
    
    if [[ "$save_config" =~ ^[oO]$ ]] && [ -d "$REDFORGE_USER_HOME" ]; then
        cp -r "$REDFORGE_USER_HOME" "$BACKUP_DIR/config"
        log "Configuration sauvegardée"
    fi
    
    if [[ "$save_reports" =~ ^[oO]$ ]] && [ -d "${REDFORGE_USER_HOME}/reports" ]; then
        cp -r "${REDFORGE_USER_HOME}/reports" "$BACKUP_DIR/reports"
        log "Rapports sauvegardés"
    fi
    
    if [[ "$save_wordlists" =~ ^[oO]$ ]] && [ -d "$WORDLISTS_CUSTOM_DIR" ]; then
        cp -r "$WORDLISTS_CUSTOM_DIR" "$BACKUP_DIR/wordlists"
        log "Wordlists personnalisées sauvegardées"
    fi
    
    if [[ "$save_apt_ops" =~ ^[oO]$ ]] && [ -d "$APT_OPERATIONS_DIR" ]; then
        cp -r "$APT_OPERATIONS_DIR" "$BACKUP_DIR/apt_operations"
        log "Opérations APT sauvegardées"
    fi
    
    if [[ "$save_stealth" =~ ^[oO]$ ]] && [ -d "$STEALTH_DIR" ]; then
        cp -r "$STEALTH_DIR" "$BACKUP_DIR/stealth"
        log "Configuration furtive sauvegardée"
    fi
    
    if [[ "$save_sessions" =~ ^[oO]$ ]] && [ -d "${REDFORGE_USER_HOME}/sessions" ]; then
        cp -r "${REDFORGE_USER_HOME}/sessions" "$BACKUP_DIR/sessions"
        log "Sessions sauvegardées"
    fi
    
    log "Sauvegarde sélective terminée dans $BACKUP_DIR"
}

# Sauvegarde complète
backup_full() {
    if [ $BACKUP -eq 1 ] && [ -d "$REDFORGE_USER_HOME" ]; then
        log_info "Sauvegarde complète de la configuration..."
        
        mkdir -p "$BACKUP_DIR"
        
        # Sauvegarder la configuration principale
        cp -r "$REDFORGE_USER_HOME" "$BACKUP_DIR/config"
        log "Configuration sauvegardée"
        
        # Sauvegarder les rapports
        if [ -d "${REDFORGE_USER_HOME}/reports" ]; then
            cp -r "${REDFORGE_USER_HOME}/reports" "$BACKUP_DIR/reports"
            log "Rapports sauvegardés"
        fi
        
        # Sauvegarder les wordlists personnalisées
        if [ -d "$WORDLISTS_CUSTOM_DIR" ]; then
            cp -r "$WORDLISTS_CUSTOM_DIR" "$BACKUP_DIR/wordlists"
            log "Wordlists personnalisées sauvegardées"
        fi
        
        # Sauvegarder les opérations APT personnalisées
        if [ -d "$APT_OPERATIONS_DIR" ]; then
            cp -r "$APT_OPERATIONS_DIR" "$BACKUP_DIR/apt_operations"
            log "Opérations APT sauvegardées"
        fi
        
        # Sauvegarder la configuration furtive
        if [ -d "$STEALTH_DIR" ]; then
            cp -r "$STEALTH_DIR" "$BACKUP_DIR/stealth"
            log "Configuration furtive sauvegardée"
        fi
        
        # Sauvegarder les sessions
        if [ -d "${REDFORGE_USER_HOME}/sessions" ]; then
            cp -r "${REDFORGE_USER_HOME}/sessions" "$BACKUP_DIR/sessions"
            log "Sessions sauvegardées"
        fi
        
        # Sauvegarder les logs (optionnel)
        if [ -d "${REDFORGE_USER_HOME}/logs" ]; then
            cp -r "${REDFORGE_USER_HOME}/logs" "$BACKUP_DIR/logs"
            log "Logs sauvegardés"
        fi
        
        log "Sauvegarde complète terminée dans $BACKUP_DIR"
    fi
}

# Arrêt des services
stop_services() {
    log_info "Arrêt des services..."
    
    # Arrêter le service systemd
    if systemctl is-active --quiet redforge 2>/dev/null; then
        systemctl stop redforge
        log "Service redforge arrêté"
    fi
    
    # Désactiver le service
    if systemctl is-enabled --quiet redforge 2>/dev/null; then
        systemctl disable redforge
        log "Service redforge désactivé"
    fi
    
    # Arrêter les processus liés à RedForge
    for proc in redforge python3.*RedForge; do
        if pgrep -f "$proc" > /dev/null 2>&1; then
            pkill -f "$proc"
            log "Processus $proc arrêté"
        fi
    done
    
    # Arrêter les services optionnels
    if systemctl is-active --quiet tor 2>/dev/null; then
        # Vérifier si TOR a été installé uniquement pour RedForge
        if [ -f "/etc/tor/torrc.redforge" ]; then
            systemctl stop tor
            log "Service TOR arrêté"
        fi
    fi
}

# Suppression des fichiers
remove_files() {
    log_info "Suppression des fichiers..."
    
    # Supprimer l'application
    if [ -d "$REDFORGE_HOME" ]; then
        rm -rf "$REDFORGE_HOME"
        log "Application supprimée: $REDFORGE_HOME"
    fi
    
    # Supprimer l'environnement virtuel
    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
        log "Environnement virtuel supprimé"
    fi
    
    # Supprimer la configuration utilisateur
    if [ $BACKUP -eq 0 ] && [ -d "$REDFORGE_USER_HOME" ]; then
        rm -rf "$REDFORGE_USER_HOME"
        log "Configuration utilisateur supprimée"
    elif [ $BACKUP -eq 1 ]; then
        log_info "Configuration conservée dans $BACKUP_DIR (non supprimée)"
    fi
    
    # Supprimer les liens symboliques
    for link in /usr/local/bin/RedForge /usr/local/bin/redforge /usr/local/bin/redforge-python; do
        if [ -L "$link" ] || [ -f "$link" ]; then
            rm -f "$link"
            log "Lien supprimé: $link"
        fi
    done
    
    # Supprimer le script de lancement
    if [ -f "$REDFORGE_HOME/run.sh" ]; then
        rm -f "$REDFORGE_HOME/run.sh"
        log "Script de lancement supprimé"
    fi
    
    # Supprimer le service systemd
    if [ -f "/etc/systemd/system/redforge.service" ]; then
        rm -f "/etc/systemd/system/redforge.service"
        systemctl daemon-reload
        log "Service systemd supprimé"
    fi
    
    # Supprimer les logs système
    if [ -d "/var/log/redforge" ]; then
        rm -rf "/var/log/redforge"
        log "Logs système supprimés"
    fi
    
    # Supprimer la configuration TOR spécifique à RedForge
    if [ -f "/etc/tor/torrc.redforge" ]; then
        rm -f "/etc/tor/torrc.redforge"
        log "Configuration TOR RedForge supprimée"
    fi
}

# Nettoyage des dépendances (optionnel)
clean_dependencies() {
    log_info "Nettoyage des dépendances..."
    
    echo ""
    echo "Souhaitez-vous supprimer les packages Python installés par RedForge ?"
    echo "  ⚠️  Attention: D'autres applications peuvent les utiliser"
    echo "  1) Oui, désinstaller les packages"
    echo "  2) Non, conserver les packages (recommandé)"
    echo ""
    read -p "Votre choix [1-2]: " choice
    
    if [ "$choice" = "1" ]; then
        log_warning "Désinstallation des packages Python..."
        
        packages=(
            "flask" "flask-socketio" "flask-cors" "flask-login"
            "requests" "httpx" "aiohttp"
            "beautifulsoup4" "lxml" "selenium" "playwright"
            "cryptography" "pyjwt" "bcrypt" "passlib"
            "rich" "colorama" "pyyaml" "click" "tqdm"
            "python-dateutil" "pytz" "sqlalchemy"
            "reportlab" "markdown" "tabulate" "matplotlib" "pandas"
            "dnspython" "netaddr" "ipaddress" "python-nmap" "paramiko"
            "openpyxl" "xlsxwriter" "psutil" "python-magic"
            "pydantic" "loguru" "prompt-toolkit" "pygments"
            "websockets" "pysocks" "stem" "requests-tor" "proxy-py"
            "celery" "redis" "pymongo" "schedule"
        )
        
        for package in "${packages[@]}"; do
            pip3 uninstall -y "$package" 2>/dev/null && log "$package désinstallé" || true
        done
        
        log "Packages Python désinstallés"
    else
        log "Packages Python conservés"
    fi
    
    echo ""
    echo "Souhaitez-vous supprimer les outils système installés par RedForge ?"
    echo "  ⚠️  Attention: Ces outils peuvent être utilisés par d'autres applications"
    echo "  1) Oui, supprimer les outils (non recommandé)"
    echo "  2) Non, conserver les outils (recommandé)"
    echo ""
    read -p "Votre choix [1-2]: " choice
    
    if [ "$choice" = "1" ]; then
        log_warning "Suppression des outils système..."
        
        tools=(
            "nmap" "sqlmap" "whatweb" "dirb" "wfuzz"
            "gobuster" "ffuf" "xsstrike" "dalfox" "wafw00f"
            "dnsrecon" "theharvester" "hydra" "john"
        )
        
        for tool in "${tools[@]}"; do
            if dpkg -l | grep -q "^ii.*$tool" 2>/dev/null; then
                apt remove -y "$tool"
                log "$tool supprimé"
            fi
        done
        
        # TOR (demander confirmation car utilisé par d'autres applications)
        read -p "Supprimer TOR ? (o/N): " remove_tor
        if [[ "$remove_tor" =~ ^[oO]$ ]]; then
            apt remove -y tor
            log "TOR supprimé"
        fi
        
        log_info "Metasploit n'a pas été supprimé (utilisé par d'autres outils)"
    else
        log "Outils système conservés"
    fi
}

# Nettoyage des wordlists (optionnel)
clean_wordlists() {
    echo ""
    read -p "Supprimer les wordlists téléchargées (rockyou.txt, SecLists) ? (o/N): " remove_wordlists
    
    if [[ "$remove_wordlists" =~ ^[oO]$ ]]; then
        log_info "Suppression des wordlists..."
        
        # RockYou
        if [ -f "/usr/share/wordlists/rockyou.txt" ]; then
            rm -f "/usr/share/wordlists/rockyou.txt"
            log "rockyou.txt supprimé"
        fi
        
        # SecLists
        if [ -d "/usr/share/seclists" ]; then
            rm -rf "/usr/share/seclists"
            log "SecLists supprimé"
        fi
        
        # Wordlists RedForge
        if [ -d "$REDFORGE_HOME/wordlists" ] && [ $BACKUP -eq 0 ]; then
            rm -rf "$REDFORGE_HOME/wordlists"
            log "Wordlists RedForge supprimées"
        fi
    else
        log "Wordlists conservées"
    fi
}

# Nettoyage des fichiers temporaires
cleanup_temp() {
    log_info "Nettoyage des fichiers temporaires..."
    
    rm -rf /tmp/redforge_* 2>/dev/null || true
    rm -f /tmp/redforge_install.log 2>/dev/null || true
    rm -f "$LOG_FILE" 2>/dev/null || true
    
    log "Fichiers temporaires nettoyés"
}

# Message de fin amélioré
show_completion() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ DÉSINSTALLATION DE REDFORGE v2.0 TERMINÉE        ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [ $BACKUP -eq 1 ]; then
        echo -e "${YELLOW}📁 Sauvegarde disponible dans: ${BACKUP_DIR}${NC}"
        echo ""
        echo "Pour restaurer votre configuration :"
        echo "  cp -r ${BACKUP_DIR}/config/* ~/.RedForge/"
        echo ""
        
        if [ -d "$BACKUP_DIR/apt_operations" ]; then
            echo "Pour restaurer les opérations APT :"
            echo "  cp -r ${BACKUP_DIR}/apt_operations/* ~/.RedForge/apt_operations/"
            echo ""
        fi
        
        if [ -d "$BACKUP_DIR/stealth" ]; then
            echo "Pour restaurer la configuration furtive :"
            echo "  cp -r ${BACKUP_DIR}/stealth/* ~/.RedForge/stealth/"
            echo ""
        fi
    fi
    
    echo -e "${BLUE}📖 Pour réinstaller RedForge v2.0 :${NC}"
    echo "  ./install.sh"
    echo ""
    echo -e "${BLUE}Merci d'avoir utilisé RedForge v2.0 ! 🔴${NC}"
    echo ""
}

# Main
main() {
    show_banner
    check_root
    confirm_uninstall
    
    if [ $BACKUP -eq 1 ]; then
        if [ $BACKUP_SELECTIVE -eq 1 ]; then
            backup_selective
        else
            backup_full
        fi
    fi
    
    stop_services
    remove_files
    clean_dependencies
    clean_wordlists
    cleanup_temp
    show_completion
}

# Exécution
main "$@"