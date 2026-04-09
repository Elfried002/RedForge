#!/bin/bash
# ========================================
# RedForge - Script de mise à jour v2.0
# Met à jour RedForge vers la dernière version
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
    echo -e "${BLUE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║              MISE À JOUR DE REDFORGE v2.0                        ║
║     Multi-Attacks | Mode Furtif | Opérations APT                 ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Variables
REDFORGE_DIR="/opt/RedForge"
BACKUP_DIR="${HOME}/RedForge_backup_pre_update_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="/tmp/redforge_update.log"
CURRENT_VERSION=""
LATEST_VERSION=""
REDFORGE_HOME="${HOME}/.RedForge"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Nouveaux répertoires v2.0
STEALTH_DIR="${REDFORGE_HOME}/stealth"
MULTI_ATTACK_DIR="${REDFORGE_HOME}/multi_attack"
APT_OPERATIONS_DIR="${REDFORGE_HOME}/apt_operations"
PERSISTENCE_DIR="${REDFORGE_HOME}/persistence"
UPLOADS_DIR="${REDFORGE_HOME}/uploads"

# Fonctions
log() { echo -e "${GREEN}[+]${NC} $1"; echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }
log_error() { echo -e "${RED}[-]${NC} $1"; echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1" >> "$LOG_FILE"; }
log_info() { echo -e "${BLUE}[*]${NC} $1"; echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" >> "$LOG_FILE"; }

# Vérification des droits root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Ce script doit être exécuté en tant que root"
        echo "Veuillez exécuter: sudo ./update.sh"
        exit 1
    fi
}

# Vérification de l'installation
check_installation() {
    if [ ! -d "$REDFORGE_DIR" ]; then
        log_error "RedForge n'est pas installé dans $REDFORGE_DIR"
        echo "Veuillez d'abord installer RedForge: sudo ./install.sh"
        exit 1
    fi
}

# Récupération des versions
get_versions() {
    # Version actuelle
    if [ -f "$REDFORGE_DIR/bin/RedForge" ]; then
        CURRENT_VERSION=$(grep -oP "Version: \K[0-9.]+" "$REDFORGE_DIR/bin/RedForge" 2>/dev/null || echo "1.0.0")
    elif [ -f "$REDFORGE_DIR/src/__init__.py" ]; then
        CURRENT_VERSION=$(grep -oP "__version__ = ['\"]\K[0-9.]+" "$REDFORGE_DIR/src/__init__.py" 2>/dev/null || echo "1.0.0")
    else
        CURRENT_VERSION="1.0.0"
    fi
    
    # Dernière version sur GitHub
    log_info "Vérification de la dernière version..."
    if command -v curl &> /dev/null; then
        LATEST_VERSION=$(curl -s https://api.github.com/repos/Elfried002/RedForge/releases/latest 2>/dev/null | grep -oP '"tag_name": "\K[^"]+' | sed 's/v//')
    fi
    
    if [ -z "$LATEST_VERSION" ]; then
        LATEST_VERSION="2.0.0"
        log_warning "Impossible de vérifier la dernière version en ligne, utilisation de la version 2.0.0"
    fi
    
    log "Version actuelle: $CURRENT_VERSION"
    log "Dernière version: $LATEST_VERSION"
}

# Sauvegarde améliorée
backup() {
    log_info "Sauvegarde de la configuration actuelle..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Sauvegarder la configuration utilisateur
    if [ -d "$REDFORGE_HOME" ]; then
        cp -r "$REDFORGE_HOME" "$BACKUP_DIR/config"
        log "Configuration utilisateur sauvegardée"
    fi
    
    # Sauvegarder les opérations APT personnalisées
    if [ -d "$APT_OPERATIONS_DIR" ]; then
        cp -r "$APT_OPERATIONS_DIR" "$BACKUP_DIR/apt_operations"
        log "Opérations APT personnalisées sauvegardées"
    fi
    
    # Sauvegarder la configuration furtive
    if [ -d "$STEALTH_DIR" ]; then
        cp -r "$STEALTH_DIR" "$BACKUP_DIR/stealth"
        log "Configuration furtive sauvegardée"
    fi
    
    # Sauvegarder les données multi-attaques
    if [ -d "$MULTI_ATTACK_DIR" ]; then
        cp -r "$MULTI_ATTACK_DIR" "$BACKUP_DIR/multi_attack"
        log "Données multi-attaques sauvegardées"
    fi
    
    # Sauvegarder les wordlists personnalisées
    if [ -d "${REDFORGE_HOME}/wordlists/custom" ]; then
        cp -r "${REDFORGE_HOME}/wordlists/custom" "$BACKUP_DIR/wordlists"
        log "Wordlists personnalisées sauvegardées"
    fi
    
    # Sauvegarder l'environnement virtuel
    if [ -d "$REDFORGE_DIR/venv" ]; then
        cp -r "$REDFORGE_DIR/venv" "$BACKUP_DIR/venv"
        log "Environnement virtuel sauvegardé"
    fi
    
    # Sauvegarder les plugins personnalisés
    if [ -d "$REDFORGE_DIR/plugins/custom" ]; then
        cp -r "$REDFORGE_DIR/plugins/custom" "$BACKUP_DIR/plugins"
        log "Plugins personnalisés sauvegardés"
    fi
    
    log "Sauvegarde terminée dans $BACKUP_DIR"
}

# Arrêt des services
stop_services() {
    log_info "Arrêt des services..."
    
    # Arrêter le service systemd
    if systemctl is-active --quiet redforge 2>/dev/null; then
        systemctl stop redforge
        log "Service redforge arrêté"
    fi
    
    # Arrêter les processus Python liés à RedForge
    for proc in redforge python3.*RedForge; do
        if pgrep -f "$proc" > /dev/null 2>&1; then
            pkill -f "$proc"
            log "Processus $proc arrêté"
        fi
    done
    
    # Arrêter les services optionnels si nécessaire
    if systemctl is-active --quiet tor 2>/dev/null; then
        if [ -f "/etc/tor/torrc.redforge" ]; then
            systemctl stop tor
            log "Service TOR arrêté"
        fi
    fi
}

# Mise à jour du code
update_code() {
    log_info "Mise à jour du code source vers v2.0..."
    
    cd "$REDFORGE_DIR"
    
    # Sauvegarder la configuration locale
    if [ -f "$REDFORGE_DIR/config/local.json" ]; then
        cp "$REDFORGE_DIR/config/local.json" /tmp/redforge_local_config.json
    fi
    
    # Supprimer l'ancien code (sauf venv, config et dossiers spéciaux)
    find "$REDFORGE_DIR" -maxdepth 1 -type d ! -name "venv" ! -name "config" ! -name "redforge" ! -name "stealth" ! -name "multi_attack" ! -name "apt_operations" -exec rm -rf {} \; 2>/dev/null || true
    
    # Copier le nouveau code depuis le répertoire source
    if [ -d "$SCRIPT_DIR" ]; then
        # Copier la structure src complète
        cp -r "$SCRIPT_DIR/src" "$REDFORGE_DIR/" 2>/dev/null || true
        cp -r "$SCRIPT_DIR/bin" "$REDFORGE_DIR/" 2>/dev/null || true
        cp -r "$SCRIPT_DIR/data" "$REDFORGE_DIR/" 2>/dev/null || true
        cp -r "$SCRIPT_DIR/config" "$REDFORGE_DIR/" 2>/dev/null || true
        cp "$SCRIPT_DIR/requirements.txt" "$REDFORGE_DIR/" 2>/dev/null || true
        cp "$SCRIPT_DIR/requirements-dev.txt" "$REDFORGE_DIR/" 2>/dev/null || true
        log "Code mis à jour depuis le répertoire local"
    else
        log_error "Répertoire source non trouvé"
        exit 1
    fi
    
    # Créer les nouveaux répertoires v2.0
    mkdir -p "$REDFORGE_DIR"/{stealth,multi_attack,apt_operations,persistence,uploads}
    
    # Restaurer la configuration locale
    if [ -f "/tmp/redforge_local_config.json" ]; then
        cp /tmp/redforge_local_config.json "$REDFORGE_DIR/config/local.json"
        rm /tmp/redforge_local_config.json
    fi
    
    # Rendre l'exécutable exécutable
    chmod +x "$REDFORGE_DIR/bin/RedForge" 2>/dev/null || true
    
    # Créer les fichiers __init__.py manquants
    find "$REDFORGE_DIR/src" -type d -exec touch {}/__init__.py \; 2>/dev/null || true
    
    log "Code mis à jour vers v2.0"
}

# Mise à jour des dépendances
update_dependencies() {
    log_info "Mise à jour des dépendances Python..."
    
    cd "$REDFORGE_DIR"
    
    # Activer l'environnement virtuel
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        log "Environnement virtuel activé"
    else
        log_warning "Environnement virtuel non trouvé, création..."
        python3 -m venv venv
        source venv/bin/activate
    fi
    
    # Mettre à jour pip
    pip install --upgrade pip
    
    # Installer/mettre à jour les dépendances
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt --upgrade
        log "Dépendances Python mises à jour"
    else
        # Dépendances essentielles v2.0
        pip install --upgrade flask flask-socketio flask-cors flask-login
        pip install --upgrade gunicorn gevent gevent-websocket
        pip install --upgrade requests httpx aiohttp
        pip install --upgrade beautifulsoup4 lxml selenium playwright
        pip install --upgrade cryptography pyjwt bcrypt passlib
        pip install --upgrade rich colorama pyyaml click tqdm
        pip install --upgrade python-dateutil pytz sqlalchemy
        pip install --upgrade reportlab markdown tabulate
        pip install --upgrade matplotlib pandas
        pip install --upgrade dnspython netaddr ipaddress python-nmap paramiko
        pip install --upgrade openpyxl xlsxwriter psutil python-magic
        pip install --upgrade pydantic loguru prompt-toolkit pygments
        pip install --upgrade websockets pysocks stem requests-tor proxy-py
        pip install --upgrade celery redis pymongo schedule
        log "Dépendances Python v2.0 mises à jour"
    fi
}

# Migration de la configuration vers v2.0
migrate_config() {
    log_info "Migration de la configuration vers v2.0..."
    
    # Créer la nouvelle configuration si elle n'existe pas
    if [ ! -f "$REDFORGE_HOME/config.json" ]; then
        cat > "$REDFORGE_HOME/config.json" << EOF
{
    "version": "2.0.0",
    "language": "fr_FR",
    "theme": "dark",
    "timeout": 300,
    "threads": 10,
    "workspace": "$REDFORGE_HOME/workspace",
    "logs": "$REDFORGE_HOME/logs",
    "reports": "$REDFORGE_HOME/reports",
    "stealth": {
        "enabled": false,
        "default_level": "medium",
        "random_user_agents": true,
        "use_tor": false,
        "rotate_proxies": false,
        "mimic_human": true,
        "random_delays": true,
        "slow_loris": false
    },
    "multi_attack": {
        "default_mode": "sequential",
        "max_parallel": 5,
        "delay": 1,
        "timeout": 300,
        "stop_on_error": false,
        "save_intermediate": true,
        "auto_retry": false
    },
    "apt": {
        "auto_cleanup": true,
        "phase_delay": 5,
        "log_all_phases": true,
        "require_confirmation": false,
        "persistence_dir": "$REDFORGE_HOME/persistence",
        "exfil_method": "http",
        "chunk_size": 512
    },
    "notifications": {
        "scan_complete": true,
        "vulnerability": true,
        "session": true,
        "report": true,
        "multi_complete": true,
        "apt_complete": true,
        "stealth_alert": true
    }
}
EOF
        log "Nouvelle configuration v2.0 créée"
    fi
    
    # Créer les nouveaux répertoires utilisateur
    for dir in stealth multi_attack apt_operations persistence uploads; do
        mkdir -p "$REDFORGE_HOME/$dir"
        log "Répertoire créé: $dir"
    done
    
    # Créer le fichier user_agents.txt par défaut
    if [ ! -f "$REDFORGE_HOME/stealth/user_agents.txt" ]; then
        cat > "$REDFORGE_HOME/stealth/user_agents.txt" << EOF
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Firefox/121.0
Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15
Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0
EOF
        log "Fichier user_agents.txt créé"
    fi
}

# Mise à jour des outils système
update_tools() {
    log_info "Mise à jour des outils système..."
    
    echo ""
    echo "Souhaitez-vous mettre à jour les outils système ?"
    echo "  1) Oui, mettre à jour les outils"
    echo "  2) Non, ignorer"
    echo ""
    read -p "Votre choix [1-2]: " choice
    
    if [ "$choice" = "1" ]; then
        apt update
        
        tools=(
            "nmap" "sqlmap" "whatweb" "dirb" "wfuzz"
            "gobuster" "ffuf" "xsstrike" "dalfox" "wafw00f"
            "dnsrecon" "theharvester" "hydra" "john" "tor"
        )
        
        for tool in "${tools[@]}"; do
            if dpkg -l | grep -q "^ii.*$tool" 2>/dev/null; then
                apt install --only-upgrade -y "$tool"
                log "$tool mis à jour"
            fi
        done
        
        log "Outils système mis à jour"
    else
        log "Mise à jour des outils système ignorée"
    fi
}

# Installation des wordlists (optionnel)
install_wordlists() {
    echo ""
    read -p "Souhaitez-vous installer/télécharger les wordlists ? (o/N): " install_wl
    
    if [[ "$install_wl" =~ ^[oO]$ ]]; then
        log_info "Installation des wordlists..."
        
        # RockYou
        if [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
            if [ -f "/usr/share/wordlists/rockyou.txt.gz" ]; then
                gunzip /usr/share/wordlists/rockyou.txt.gz
                log "RockYou décompressé"
            else
                curl -L -o /tmp/rockyou.txt.gz https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt.gz
                gunzip /tmp/rockyou.txt.gz
                cp /tmp/rockyou.txt /usr/share/wordlists/
                log "RockYou téléchargé"
            fi
        fi
        
        # SecLists
        if [ ! -d "/usr/share/seclists" ]; then
            git clone --depth 1 https://github.com/danielmiessler/SecLists.git /usr/share/seclists
            log "SecLists installé"
        fi
        
        log "Wordlists installées"
    fi
}

# Restauration des éléments personnalisés
restore_custom() {
    log_info "Restauration des éléments personnalisés..."
    
    # Restaurer les opérations APT personnalisées
    if [ -d "$BACKUP_DIR/apt_operations" ]; then
        cp -r "$BACKUP_DIR/apt_operations"/* "$APT_OPERATIONS_DIR/" 2>/dev/null || true
        log "Opérations APT personnalisées restaurées"
    fi
    
    # Restaurer la configuration furtive
    if [ -d "$BACKUP_DIR/stealth" ]; then
        cp -r "$BACKUP_DIR/stealth"/* "$STEALTH_DIR/" 2>/dev/null || true
        log "Configuration furtive restaurée"
    fi
    
    # Restaurer les données multi-attaques
    if [ -d "$BACKUP_DIR/multi_attack" ]; then
        cp -r "$BACKUP_DIR/multi_attack"/* "$MULTI_ATTACK_DIR/" 2>/dev/null || true
        log "Données multi-attaques restaurées"
    fi
    
    # Restaurer les wordlists
    if [ -d "$BACKUP_DIR/wordlists" ]; then
        mkdir -p "${REDFORGE_HOME}/wordlists/custom"
        cp -r "$BACKUP_DIR/wordlists"/* "${REDFORGE_HOME}/wordlists/custom/" 2>/dev/null || true
        log "Wordlists personnalisées restaurées"
    fi
    
    # Restaurer les plugins
    if [ -d "$BACKUP_DIR/plugins" ]; then
        mkdir -p "$REDFORGE_DIR/plugins/custom"
        cp -r "$BACKUP_DIR/plugins"/* "$REDFORGE_DIR/plugins/custom/" 2>/dev/null || true
        log "Plugins personnalisés restaurés"
    fi
}

# Mise à jour des liens symboliques
update_links() {
    log_info "Mise à jour des liens symboliques..."
    
    # Créer les liens symboliques
    ln -sf "$REDFORGE_DIR/venv/bin/python" /usr/local/bin/redforge-python
    ln -sf "$REDFORGE_DIR/bin/RedForge" /usr/local/bin/redforge
    ln -sf "$REDFORGE_DIR/bin/RedForge" /usr/local/bin/RedForge
    
    # Script de lancement
    cat > "$REDFORGE_DIR/run.sh" << EOF
#!/bin/bash
cd $REDFORGE_DIR
source venv/bin/activate
python bin/RedForge "\$@"
EOF
    chmod +x "$REDFORGE_DIR/run.sh"
    
    # Script de lancement web
    cat > "$REDFORGE_DIR/run-web.sh" << EOF
#!/bin/bash
cd $REDFORGE_DIR
source venv/bin/activate
python bin/RedForge -g
EOF
    chmod +x "$REDFORGE_DIR/run-web.sh"
    
    log "Liens symboliques mis à jour"
}

# Nettoyage
cleanup() {
    log_info "Nettoyage..."
    
    # Supprimer les fichiers temporaires
    rm -rf /tmp/redforge_* 2>/dev/null || true
    
    # Nettoyer pip cache
    pip cache purge 2>/dev/null || true
    
    # Nettoyer apt cache
    apt clean 2>/dev/null || true
    
    # Nettoyer les anciens logs
    find "$REDFORGE_HOME/logs" -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    log "Nettoyage terminé"
}

# Message de fin
show_completion() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ MISE À JOUR VERS REDFORGE v2.0 TERMINÉE          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "Version: ${GREEN}${LATEST_VERSION}${NC} (précédemment ${YELLOW}${CURRENT_VERSION}${NC})"
    echo ""
    echo -e "${CYAN}📖 Nouveautés de la version 2.0 :${NC}"
    echo -e "  • 🎯 Attaques multiples (séquentielles et parallèles)"
    echo -e "  • 🕵️ Mode furtif avancé (TOR, proxies, user-agents aléatoires)"
    echo -e "  • 🎭 Opérations APT complètes (persistance, mouvement latéral, exfiltration)"
    echo -e "  • 📊 Rapports enrichis avec graphiques"
    echo -e "  • 🌐 Interface web moderne"
    echo ""
    echo -e "${CYAN}📖 Pour tester :${NC}"
    echo -e "  ${GREEN}redforge --version${NC}"
    echo -e "  ${GREEN}redforge --help${NC}"
    echo -e "  ${GREEN}sudo redforge -g${NC} (interface web)"
    echo -e "  ${GREEN}redforge --stealth${NC} (mode furtif)"
    echo -e "  ${GREEN}redforge --apt recon_to_exfil${NC} (opération APT)"
    echo ""
    echo -e "${YELLOW}📁 Sauvegarde disponible dans: ${BACKUP_DIR}${NC}"
    echo "  En cas de problème, restaurez avec: sudo ./uninstall.sh puis sudo ./install.sh"
    echo ""
    echo -e "${GREEN}🚀 RedForge v2.0 est prêt à être utilisé !${NC}"
    echo ""
}

# Comparaison des versions
compare_versions() {
    if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ] && [ "$LATEST_VERSION" != "1.0.0" ]; then
        log "RedForge est déjà à jour (v$CURRENT_VERSION)"
        echo ""
        read -p "Voulez-vous quand même réinstaller/mettre à jour ? (o/N): " reinstall
        if [[ ! "$reinstall" =~ ^[oO]$ ]]; then
            exit 0
        fi
    fi
}

# Main
main() {
    show_banner
    check_root
    check_installation
    get_versions
    compare_versions
    
    echo ""
    log_info "Préparation de la mise à jour de v$CURRENT_VERSION vers v$LATEST_VERSION"
    echo ""
    echo -e "${YELLOW}⚠️  Cette mise à jour va installer RedForge v2.0 avec de nouvelles fonctionnalités :${NC}"
    echo "  - Multi-attaques"
    echo "  - Mode furtif"
    echo "  - Opérations APT"
    echo ""
    read -p "Continuer la mise à jour ? (O/n): " confirm
    if [[ ! "$confirm" =~ ^[oO]$ ]] && [ -n "$confirm" ]; then
        log "Mise à jour annulée"
        exit 0
    fi
    
    backup
    stop_services
    update_code
    update_dependencies
    migrate_config
    update_tools
    install_wordlists
    restore_custom
    update_links
    cleanup
    show_completion
}

# Exécution
main "$@"