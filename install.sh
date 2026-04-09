#!/bin/bash
# ========================================
# RedForge - Script d'installation v2.0
# Installe RedForge avec support Multi-Attacks, Mode Furtif et Opérations APT
# Compatible Kali Linux / Parrot OS / Debian / Ubuntu
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

# Bannière v2.0
show_banner() {
    echo -e "${RED}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ███████╗██████╗ ███████╗ ██████╗ ██████╗  ██████╗ ███████╗         ║
║   ██╔══██╗██╔════╝██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝         ║
║   ██████╔╝█████╗  ██║  ██║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗           ║
║   ██╔══██╗██╔══╝  ██║  ██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝           ║
║   ██║  ██║███████╗██████╔╝██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗         ║
║   ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝         ║
║                                                                              ║
║         Plateforme d'Orchestration de Pentest Web pour Red Team              ║
║              Version 2.0.0 - Support Multi-Attacks & APT                     ║
║                     Compatible Kali Linux & Parrot OS                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Variables
REDFORGE_HOME="/opt/RedForge"
REDFORGE_USER_HOME="${HOME}/.RedForge"
LOG_FILE="/tmp/redforge_install.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_TYPE="full"

# Fonction de logging
log() { echo -e "${GREEN}[+]${NC} $1"; echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }
log_error() { echo -e "${RED}[-]${NC} $1"; echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1" >> "$LOG_FILE"; }
log_info() { echo -e "${BLUE}[*]${NC} $1"; echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" >> "$LOG_FILE"; }

# Vérification des droits root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Ce script doit être exécuté en tant que root"
        echo "Veuillez exécuter: sudo ./install.sh"
        exit 1
    fi
}

# Détection de l'OS
detect_os() {
    log_info "Détection du système d'exploitation..."
    
    if grep -qi "kali" /etc/os-release 2>/dev/null; then
        OS="Kali Linux"
        log "OS détecté: $OS"
    elif grep -qi "parrot" /etc/os-release 2>/dev/null; then
        OS="Parrot OS"
        log "OS détecté: $OS"
    elif grep -qi "debian" /etc/os-release 2>/dev/null; then
        OS="Debian"
        log "OS détecté: $OS"
    elif grep -qi "ubuntu" /etc/os-release 2>/dev/null; then
        OS="Ubuntu"
        log "OS détecté: $OS"
    else
        OS="Linux"
        log_warning "OS détecté: $OS - Compatibilité non garantie"
    fi
}

# Création de l'exécutable principal
create_executable() {
    log_info "Création de l'exécutable principal..."
    
    mkdir -p "${SCRIPT_DIR}/bin"
    
    cat > "${SCRIPT_DIR}/bin/RedForge" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedForge v2.0 - Point d'entrée principal
Support Multi-Attacks, Mode Furtif et Opérations APT
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

def main():
    try:
        # Vérifier si on lance l'interface web ou CLI
        if len(sys.argv) > 1 and sys.argv[1] in ['-g', '--gui']:
            from src.web_interface.app import create_app, socketio
            app = create_app()
            print("🔴 RedForge Web Interface démarrée")
            print("📍 http://localhost:5000")
            socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        else:
            from src.core.cli import RedForgeCLI
            RedForgeCLI().run()
    except ImportError as e:
        print(f"Erreur: {e}")
        print("Installez les dépendances: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption utilisateur.")
        sys.exit(0)

if __name__ == "__main__":
    main()
EOF

    chmod +x "${SCRIPT_DIR}/bin/RedForge"
    log "Exécutable créé: ${SCRIPT_DIR}/bin/RedForge"
}

# Création des fichiers __init__.py
create_init_files() {
    log_info "Création des fichiers __init__.py..."
    
    # Créer la structure des dossiers
    mkdir -p "${SCRIPT_DIR}/src"/{core,attacks,web_interface,utils,modules,stealth,multi_attack,apt}
    mkdir -p "${SCRIPT_DIR}/src/web_interface"/{templates,static/{css,js,images}}
    
    # Fichier principal __init__.py
    cat > "${SCRIPT_DIR}/src/__init__.py" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RedForge v2.0 - Plateforme d'Orchestration de Pentest Web"""
__version__ = '2.0.0'
__author__ = 'RedForge Team'
__license__ = 'GPLv3'
EOF

    # Créer tous les __init__.py
    find "${SCRIPT_DIR}/src" -type d 2>/dev/null | while read dir; do
        if [ ! -f "${dir}/__init__.py" ]; then
            echo "# Module ${dir##*/}" > "${dir}/__init__.py"
        fi
    done
    
    log "Fichiers __init__.py créés"
}

# Installation des dépendances système complètes
install_system_deps() {
    log_info "Installation des dépendances système..."
    
    apt update
    
    local packages=(
        # Python et outils de base
        python3 python3-pip python3-venv python3-dev
        build-essential libssl-dev libffi-dev
        curl wget git unzip zip
        
        # Outils de pentest
        nmap sqlmap whatweb dirb wfuzz
        hydra john medusa
        metasploit-framework
        tor proxychains
        gobuster ffuf
        xsstrike dalfox
        wafw00f
        dnsrecon theharvester
        
        # Utilitaires
        jq vim-tiny htop
        netcat-openbsd dnsutils
        tcpdump wireshark
    )
    
    for package in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii.*$package" 2>/dev/null; then
            apt install -y "$package" 2>/dev/null || log_warning "Impossible d'installer $package"
            log "$package installé"
        else
            log "$package déjà installé"
        fi
    done
    
    log "Dépendances système installées"
}

# Création de l'environnement virtuel
create_venv() {
    log_info "Création de l'environnement virtuel..."
    
    cd "$SCRIPT_DIR"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log "Environnement virtuel créé"
    else
        log "Environnement virtuel existant"
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
}

# Installation des dépendances Python complètes
install_python_deps() {
    log_info "Installation des dépendances Python..."
    
    source venv/bin/activate
    
    # Framework web
    pip install flask flask-socketio flask-cors flask-login
    pip install gunicorn gevent gevent-websocket
    
    # Requêtes HTTP
    pip install requests httpx aiohttp
    pip install beautifulsoup4 lxml html5lib
    pip install selenium playwright
    
    # Sécurité
    pip install cryptography pyjwt bcrypt passlib
    pip install pycryptodome
    
    # Analyse
    pip install nmap python-nmap
    pip install sqlmap
    pip install paramiko
    pip install dnspython netaddr ipaddress
    
    # Base de données
    pip install sqlalchemy redis pymongo
    
    # Reporting
    pip install reportlab markdown tabulate
    pip install matplotlib pandas seaborn
    pip install jinja2 weasyprint
    pip install openpyxl xlsxwriter
    
    # CLI et UI
    pip install rich colorama pyyaml click tqdm
    pip install python-dateutil pytz
    pip install prompt-toolkit pygments
    
    # Utilitaires
    pip install psutil python-magic
    pip install pydantic loguru
    pip install websockets pysocks
    pip install schedule
    
    # Mode furtif
    pip install stem requests-tor
    pip install proxy-py
    
    # Multi-attaques
    pip install concurrent-futures
    pip install celery redis
    
    log "Dépendances Python installées"
}

# Copie des fichiers
copy_files() {
    log_info "Copie des fichiers vers $REDFORGE_HOME..."
    
    mkdir -p "$REDFORGE_HOME"/{src,bin,config,logs,data,venv,wordlists,stealth,multi_attack,apt_operations,persistence,uploads}
    mkdir -p "$REDFORGE_USER_HOME"/{workspace,logs,reports,sessions,wordlists,stealth,apt_operations}
    
    # Copier le code source
    cp -r "$SCRIPT_DIR/src"/* "$REDFORGE_HOME/src/" 2>/dev/null || true
    cp -r "$SCRIPT_DIR/config"/* "$REDFORGE_HOME/config/" 2>/dev/null || true
    cp -r "$SCRIPT_DIR/data"/* "$REDFORGE_HOME/data/" 2>/dev/null || true
    cp -r "$SCRIPT_DIR/wordlists"/* "$REDFORGE_HOME/wordlists/" 2>/dev/null || true
    cp "$SCRIPT_DIR/bin/RedForge" "$REDFORGE_HOME/bin/"
    
    # Copier l'environnement virtuel
    cp -r "$SCRIPT_DIR/venv" "$REDFORGE_HOME/"
    
    # Copier les fichiers web
    cp -r "$SCRIPT_DIR/src/web_interface/templates" "$REDFORGE_HOME/src/web_interface/" 2>/dev/null || true
    cp -r "$SCRIPT_DIR/src/web_interface/static" "$REDFORGE_HOME/src/web_interface/" 2>/dev/null || true
    
    chmod +x "$REDFORGE_HOME/bin/RedForge"
    chmod +x "$REDFORGE_HOME/venv/bin/activate"
    
    log "Fichiers copiés"
}

# Installation des wordlists
install_wordlists() {
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
    
    # SecLists (version allégée)
    if [ ! -d "/usr/share/seclists" ]; then
        git clone --depth 1 https://github.com/danielmiessler/SecLists.git /usr/share/seclists
        log "SecLists installé"
    fi
    
    # Wordlists spécifiques RedForge
    mkdir -p "$REDFORGE_HOME/wordlists"/{passwords,usernames,directories,subdomains}
    
    # Créer une wordlist de base pour les tests
    cat > "$REDFORGE_HOME/wordlists/passwords/common.txt" << EOF
admin
password
123456
admin123
root
toor
test
qwerty
abc123
letmein
welcome
monkey
dragon
master
sunshine
EOF
    
    cat > "$REDFORGE_HOME/wordlists/usernames/common.txt" << EOF
admin
root
user
test
guest
administrator
webmaster
support
info
contact
EOF
    
    cat > "$REDFORGE_HOME/wordlists/directories/common.txt" << EOF
admin
wp-admin
login
dashboard
cpanel
phpmyadmin
backup
uploads
images
css
js
assets
EOF
    
    log "Wordlists installées"
}

# Configuration TOR
configure_tor() {
    log_info "Configuration de TOR pour le mode furtif..."
    
    cat > /etc/tor/torrc << EOF
SocksPort 0.0.0.0:9050
ControlPort 0.0.0.0:9051
CookieAuthentication 0
ExitNodes {fr}
StrictNodes 1
EOF
    
    systemctl enable tor 2>/dev/null || true
    systemctl restart tor 2>/dev/null || true
    log "TOR configuré"
}

# Configuration de l'environnement
configure_environment() {
    log_info "Configuration de l'environnement..."
    
    # Lien symbolique global
    ln -sf "$REDFORGE_HOME/venv/bin/python" /usr/local/bin/redforge-python
    ln -sf "$REDFORGE_HOME/bin/RedForge" /usr/local/bin/redforge
    ln -sf "$REDFORGE_HOME/bin/RedForge" /usr/local/bin/RedForge
    
    # Script de lancement
    cat > "$REDFORGE_HOME/run.sh" << EOF
#!/bin/bash
cd $REDFORGE_HOME
source venv/bin/activate
python bin/RedForge "\$@"
EOF
    chmod +x "$REDFORGE_HOME/run.sh"
    
    # Script de lancement web
    cat > "$REDFORGE_HOME/run-web.sh" << EOF
#!/bin/bash
cd $REDFORGE_HOME
source venv/bin/activate
python bin/RedForge -g
EOF
    chmod +x "$REDFORGE_HOME/run-web.sh"
    
    # Configuration par défaut v2.0
    cat > "$REDFORGE_USER_HOME/config.json" << EOF
{
    "version": "2.0.0",
    "language": "fr_FR",
    "theme": "dark",
    "timeout": 300,
    "threads": 10,
    "workspace": "$REDFORGE_USER_HOME/workspace",
    "logs": "$REDFORGE_USER_HOME/logs",
    "reports": "$REDFORGE_USER_HOME/reports",
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
        "persistence_dir": "$REDFORGE_USER_HOME/persistence",
        "exfil_method": "http"
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
    
    # Créer les dossiers supplémentaires
    mkdir -p "$REDFORGE_USER_HOME"/{stealth,apt_operations,persistence,multi_attack}
    
    log "Environnement configuré"
}

# Création du service systemd
create_systemd_service() {
    log_info "Création du service systemd..."
    
    cat > /etc/systemd/system/redforge.service << EOF
[Unit]
Description=RedForge Pentest Platform
After=network.target tor.service
Wants=tor.service

[Service]
Type=simple
User=root
WorkingDirectory=$REDFORGE_HOME
ExecStart=$REDFORGE_HOME/venv/bin/python $REDFORGE_HOME/bin/RedForge -g
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    log "Service systemd créé (redforge.service)"
}

# Désinstallation
uninstall() {
    log_warning "Désinstallation de RedForge..."
    
    read -p "Êtes-vous sûr de vouloir désinstaller RedForge ? (o/N): " confirm
    if [[ ! "$confirm" =~ ^[oO]$ ]]; then
        log "Désinstallation annulée"
        exit 0
    fi
    
    # Arrêter le service
    systemctl stop redforge.service 2>/dev/null || true
    systemctl disable redforge.service 2>/dev/null || true
    
    # Supprimer les liens symboliques
    rm -f /usr/local/bin/redforge /usr/local/bin/RedForge /usr/local/bin/redforge-python
    
    # Supprimer l'application
    rm -rf "$REDFORGE_HOME"
    
    read -p "Supprimer la configuration utilisateur ? (o/N): " del_config
    if [[ "$del_config" =~ ^[oO]$ ]]; then
        rm -rf "$REDFORGE_USER_HOME"
        log "Configuration utilisateur supprimée"
    fi
    
    read -p "Supprimer les wordlists téléchargées ? (o/N): " del_wordlists
    if [[ "$del_wordlists" =~ ^[oO]$ ]]; then
        rm -rf /usr/share/seclists
        rm -f /usr/share/wordlists/rockyou.txt
        log "Wordlists supprimées"
    fi
    
    log "RedForge désinstallé"
}

# Installation complète
full_install() {
    log_info "Démarrage de l'installation complète de RedForge v2.0..."
    
    check_root
    detect_os
    install_system_deps
    create_executable
    create_init_files
    create_venv
    install_python_deps
    copy_files
    install_wordlists
    configure_tor
    configure_environment
    create_systemd_service
    
    show_completion
}

# Installation minimal (sans outils externes)
minimal_install() {
    log_info "Démarrage de l'installation minimale..."
    
    check_root
    detect_os
    install_system_deps
    create_executable
    create_init_files
    create_venv
    install_python_deps
    copy_files
    configure_environment
    
    show_completion
}

# Menu d'installation
show_menu() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                     TYPE D'INSTALLATION                          ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "1. Installation complète (recommandée) - Avec wordlists et outils"
    echo "2. Installation minimale - Sans outils externes"
    echo "3. Installation avec service systemd"
    echo "4. Désinstallation"
    echo "5. Quitter"
    echo ""
    read -p "Votre choix [1-5]: " choice
    
    case $choice in
        1) full_install ;;
        2) minimal_install ;;
        3) full_install && create_systemd_service && log "Service systemd activé" ;;
        4) uninstall ;;
        5) echo "Au revoir!"; exit 0 ;;
        *) log_error "Choix invalide"; exit 1 ;;
    esac
}

# Message de fin
show_completion() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    ✅ INSTALLATION RÉUSSIE !                    ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}📖 Pour commencer :${NC}"
    echo -e "  ${GREEN}redforge --help${NC}                    - Afficher l'aide"
    echo -e "  ${GREEN}redforge -t example.com${NC}            - Scan rapide"
    echo -e "  ${GREEN}sudo redforge -g${NC}                   - Lancer l'interface graphique"
    echo -e "  ${GREEN}redforge --stealth${NC}                 - Mode furtif"
    echo -e "  ${GREEN}redforge --multi config.json${NC}       - Multi-attaque"
    echo -e "  ${GREEN}redforge --apt recon_to_exfil${NC}      - Opération APT"
    echo ""
    echo -e "${CYAN}🌐 Interface web :${NC}"
    echo -e "  ${GREEN}http://localhost:5000${NC}"
    echo ""
    echo -e "${CYAN}📂 Dossiers créés :${NC}"
    echo -e "  • Application : ${GREEN}$REDFORGE_HOME${NC}"
    echo -e "  • Configuration : ${GREEN}$REDFORGE_USER_HOME${NC}"
    echo -e "  • Wordlists : ${GREEN}$REDFORGE_HOME/wordlists${NC}"
    echo ""
    echo -e "${CYAN}🔧 Commandes utiles :${NC}"
    echo -e "  ${GREEN}redforge --version${NC}                 - Version"
    echo -e "  ${GREEN}redforge --check-deps${NC}              - Vérifier les dépendances"
    echo -e "  ${GREEN}systemctl start redforge${NC}           - Démarrer le service"
    echo ""
    echo -e "${YELLOW}⚠️  Note : RedForge nécessite les droits sudo pour les fonctionnalités avancées${NC}"
    echo ""
    echo -e "${BLUE}Merci d'utiliser RedForge v2.0 ! 🔴${NC}"
    echo ""
}

# Main
main() {
    show_banner
    
    if [ "$1" = "--unattended" ]; then
        full_install
    elif [ "$1" = "--minimal" ]; then
        minimal_install
    else
        show_menu
    fi
}

# Exécution
main "$@"