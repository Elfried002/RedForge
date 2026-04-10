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
║                Plateforme de Pentest Web pour Red Team                       ║
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

# ============================================
# INSTALLATION DE TOR (OBLIGATOIRE - EN PREMIER)
# ============================================
install_tor() {
    log_info "Installation de TOR pour le mode furtif..."
    
    # Vérifier si TOR est déjà installé
    if ! command -v tor &> /dev/null; then
        apt install -y tor
        log "TOR installé avec succès"
    else
        log "TOR déjà installé"
    fi
    
    # Créer le dossier de configuration
    mkdir -p /etc/tor
    
    # Configurer TOR
    cat > /etc/tor/torrc << 'EOF'
# RedForge - Configuration TOR pour mode furtif
SocksPort 0.0.0.0:9050
ControlPort 0.0.0.0:9051
CookieAuthentication 0
ExitNodes {fr}
StrictNodes 1
DataDirectory /var/lib/tor
Log notice file /var/log/tor/notices.log
RunAsDaemon 1
EOF
    
    # Démarrer et activer TOR
    systemctl enable tor 2>/dev/null || true
    systemctl restart tor 2>/dev/null || true
    
    # Attendre que TOR démarre
    sleep 3
    
    # Vérifier que TOR fonctionne
    if systemctl is-active --quiet tor 2>/dev/null; then
        log "✅ TOR est actif sur le port 9050"
        
        # Tester la connexion TOR
        if command -v curl &> /dev/null; then
            TOR_TEST=$(curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip -s 2>/dev/null | grep -o '"IsTor":true' || echo "")
            if [ -n "$TOR_TEST" ]; then
                log "✅ TOR fonctionne correctement"
            else
                log_warning "⚠️ TOR est démarré mais le test de connexion a échoué"
            fi
        fi
    else
        log_warning "⚠️ TOR n'a pas pu démarrer automatiquement"
        log_info "Démarrage manuel: sudo systemctl start tor"
    fi
    
    # Configurer proxychains
    if [ -f "/etc/proxychains.conf" ]; then
        if ! grep -q "socks5 127.0.0.1 9050" /etc/proxychains.conf; then
            echo "" >> /etc/proxychains.conf
            echo "# RedForge - TOR proxy" >> /etc/proxychains.conf
            echo "socks5 127.0.0.1 9050" >> /etc/proxychains.conf
            log "Proxychains configuré pour TOR"
        fi
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

# Déterminer le chemin d'installation
if os.path.exists("/opt/RedForge"):
    PROJECT_ROOT = "/opt/RedForge"
else:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, PROJECT_ROOT)

def main():
    try:
        # Activer l'environnement virtuel si présent
        venv_python = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")
        if os.path.exists(venv_python) and sys.executable != venv_python:
            os.execv(venv_python, [venv_python] + sys.argv)
            return
        
        # Vérifier si on lance l'interface web ou CLI
        if len(sys.argv) > 1 and sys.argv[1] in ['-g', '--gui']:
            from src.web_interface.app import create_app, socketio
            app = create_app()
            print("RedForge Web Interface démarrée")
            print("http://localhost:5000")
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
    
    mkdir -p "${SCRIPT_DIR}/src"/{core,attacks,web_interface,utils,modules,stealth,multi_attack,apt}
    mkdir -p "${SCRIPT_DIR}/src/web_interface"/{templates,static/{css,js,images}}
    
    cat > "${SCRIPT_DIR}/src/__init__.py" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RedForge v2.0 - Plateforme de Pentest Web"""
__version__ = '2.0.0'
__author__ = 'Elfried YOBOUET'
__license__ = 'GPLv3'
EOF

    find "${SCRIPT_DIR}/src" -type d 2>/dev/null | while read dir; do
        if [ ! -f "${dir}/__init__.py" ]; then
            echo "# Module ${dir##*/}" > "${dir}/__init__.py"
        fi
    done
    
    log "Fichiers __init__.py créés"
}

# ============================================
# INSTALLATION DES DÉPENDANCES SYSTÈME (COMPLÈTE)
# ============================================
install_system_deps() {
    log_info "Installation des dépendances système..."
    
    apt update
    
    # Paquets système essentiels
    local base_packages=(
        python3 python3-pip python3-venv python3-dev
        build-essential libssl-dev libffi-dev
        curl wget git unzip zip
        jq vim-tiny htop
        netcat-openbsd dnsutils
        tcpdump wireshark
    )
    
    # Outils de pentest
    local pentest_packages=(
        nmap sqlmap whatweb dirb wfuzz
        hydra john medusa
        metasploit-framework
        gobuster ffuf
        xsstrike
        wafw00f
        dnsrecon theharvester
    )
    
    # Mode furtif - proxychains
    local stealth_packages=(
        proxychains
        proxychains4
    )
    
    # Installation de tous les paquets
    all_packages=("${base_packages[@]}" "${pentest_packages[@]}" "${stealth_packages[@]}")
    
    for package in "${all_packages[@]}"; do
        if ! dpkg -l | grep -q "^ii.*$package" 2>/dev/null; then
            apt install -y "$package" 2>/dev/null || log_warning "Impossible d'installer $package"
            log "$package installé"
        else
            log "$package déjà installé"
        fi
    done
    
    # Installation de dalfox via Go
    if ! command -v dalfox &> /dev/null; then
        log_info "Installation de dalfox via Go..."
        if ! command -v go &> /dev/null; then
            apt install -y golang-go
        fi
        go install github.com/hahwul/dalfox/v2@latest
        if [ -f "$HOME/go/bin/dalfox" ]; then
            cp "$HOME/go/bin/dalfox" /usr/local/bin/
        elif [ -f "/root/go/bin/dalfox" ]; then
            cp /root/go/bin/dalfox /usr/local/bin/
        fi
        chmod +x /usr/local/bin/dalfox 2>/dev/null || true
        log "dalfox installé"
    else
        log "dalfox déjà installé"
    fi
    
    log "Dépendances système installées"
}

# Création de l'environnement virtuel
create_venv() {
    log_info "Création de l'environnement virtuel..."
    
    cd "$SCRIPT_DIR"
    
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        log "Environnement virtuel créé"
    else
        log "Environnement virtuel existant"
    fi
    
    source .venv/bin/activate
    pip install --upgrade pip
}

# Installation des dépendances Python
install_python_deps() {
    log_info "Installation des dépendances Python..."
    
    source .venv/bin/activate
    
    pip install flask flask-socketio flask-cors flask-login
    pip install gunicorn gevent gevent-websocket
    pip install requests httpx aiohttp
    pip install beautifulsoup4 lxml html5lib
    pip install selenium playwright
    pip install cryptography pyjwt bcrypt passlib
    pip install pycryptodome
    pip install python-nmap paramiko dnspython netaddr ipaddress
    pip install sqlalchemy redis pymongo
    pip install reportlab markdown tabulate
    pip install matplotlib pandas seaborn
    pip install jinja2 weasyprint
    pip install openpyxl xlsxwriter
    pip install rich colorama pyyaml click tqdm
    pip install python-dateutil pytz
    pip install prompt-toolkit pygments
    pip install psutil python-magic
    pip install pydantic loguru
    pip install websockets pysocks
    pip install schedule
    pip install stem requests-tor
    pip install proxy-py
    pip install celery
    
    log "Dépendances Python installées"
}

# ============================================
# COPIE ROBUSTE DES FICHIERS
# ============================================
copy_files() {
    log_info "Copie des fichiers vers $REDFORGE_HOME..."
    
    # Créer les dossiers de destination
    mkdir -p "$REDFORGE_HOME"/{src,bin,config,logs,data,.venv,wordlists,stealth,multi_attack,apt_operations,persistence,uploads}
    mkdir -p "$REDFORGE_USER_HOME"/{workspace,logs,reports,sessions,wordlists,stealth,apt_operations}
    
    # Copie avec préservation de la structure
    log_info "Copie du code source..."
    cd "$SCRIPT_DIR"
    
    for item in src bin config data .venv; do
        if [ -e "$item" ]; then
            tar cf - "$item" 2>/dev/null | (cd "$REDFORGE_HOME" && tar xf -) || true
        fi
    done
    
    # Copier les fichiers web
    if [ -d "src/web_interface/templates" ]; then
        mkdir -p "$REDFORGE_HOME/src/web_interface/templates"
        cp -r src/web_interface/templates/* "$REDFORGE_HOME/src/web_interface/templates/" 2>/dev/null || true
    fi
    
    if [ -d "src/web_interface/static" ]; then
        mkdir -p "$REDFORGE_HOME/src/web_interface/static"
        cp -r src/web_interface/static/* "$REDFORGE_HOME/src/web_interface/static/" 2>/dev/null || true
    fi
    
    # Copier report_generator.py au bon endroit
    if [ -f "$REDFORGE_HOME/src/utils/report_generator.py" ]; then
        cp "$REDFORGE_HOME/src/utils/report_generator.py" "$REDFORGE_HOME/src/core/"
        log "report_generator.py copié dans core"
    fi
    
    # Créer tous les __init__.py
    find "$REDFORGE_HOME/src" -type d -exec touch {}/__init__.py \; 2>/dev/null
    
    chmod +x "$REDFORGE_HOME/bin/RedForge"
    
    log "Fichiers copiés avec succès"
}

# ============================================
# CRÉATION DES MODULES MANQUANTS
# ============================================
create_missing_modules() {
    log_info "Vérification et création des modules manquants..."
    
    mkdir -p "$REDFORGE_HOME/src/core"
    mkdir -p "$REDFORGE_HOME/src/utils"
    
    # Modules core requis
    local core_modules=(
        "attack_chainer" "apt_controller" "stealth_engine"
        "orchestrator" "cli" "gui" "config" "session_manager" "report_generator"
    )
    
    for module in "${core_modules[@]}"; do
        if [ ! -f "$REDFORGE_HOME/src/core/${module}.py" ]; then
            cat > "$REDFORGE_HOME/src/core/${module}.py" << EOF
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module ${module} - RedForge Core"""

class ${module^}:
    def __init__(self, *args, **kwargs):
        self.initialized = True
    def run(self, *args, **kwargs):
        return {"success": True, "module": "${module}"}
EOF
            log "Module $module créé"
        fi
    done
    
    # Vérification
    log_info "Vérification des modules..."
    for module in "${core_modules[@]}"; do
        if [ -f "$REDFORGE_HOME/src/core/${module}.py" ]; then
            log "  ✅ $module.py présent"
        fi
    done
}

# Installation des wordlists
install_wordlists() {
    log_info "Installation des wordlists..."
    
    if [ -f "$SCRIPT_DIR/src/data/wordlists/common_passwords.txt" ]; then
        log "common_passwords.txt déjà présent (133MB)"
    else
        log_warning "common_passwords.txt non trouvé, téléchargement..."
        mkdir -p "$SCRIPT_DIR/src/data/wordlists/"
        curl -L -o "$SCRIPT_DIR/src/data/wordlists/common_passwords.txt" \
            "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt"
        log "common_passwords.txt téléchargé"
    fi
    
    if [ ! -d "/usr/share/seclists" ]; then
        git clone --depth 1 https://github.com/danielmiessler/SecLists.git /usr/share/seclists
        log "SecLists installé"
    fi
    
    mkdir -p "$REDFORGE_HOME/wordlists"/{passwords,usernames,directories,subdomains}
    cp "$SCRIPT_DIR/src/data/wordlists/common_passwords.txt" "$REDFORGE_HOME/wordlists/passwords/common_passwords.txt" 2>/dev/null || true
    
    log "Wordlists installées"
}

# Configuration de l'environnement
configure_environment() {
    log_info "Configuration de l'environnement..."
    
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
        "use_tor": true,
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
    
    mkdir -p "$REDFORGE_USER_HOME"/{stealth,apt_operations,persistence,multi_attack}
    log "Environnement configuré"
}

# ============================================
# CRÉATION DES LIENS SYMBOLIQUES GLOBAUX
# ============================================
create_global_symlinks() {
    log_info "Création des liens symboliques globaux..."
    
    mkdir -p /usr/local/bin
    rm -f /usr/local/bin/redforge /usr/local/bin/RedForge
    
    cat > /usr/local/bin/redforge << 'WRAPPER'
#!/bin/bash
REDFORGE_HOME="/opt/RedForge"

if [ ! -d "$REDFORGE_HOME" ]; then
    echo "❌ RedForge n'est pas installé dans $REDFORGE_HOME"
    exit 1
fi

cd "$REDFORGE_HOME"
source .venv/bin/activate
export PYTHONPATH="$REDFORGE_HOME:$PYTHONPATH"
python bin/RedForge "$@"
deactivate
WRAPPER

    chmod +x /usr/local/bin/redforge
    ln -sf /usr/local/bin/redforge /usr/local/bin/RedForge
    
    if [ -f "/usr/local/bin/redforge" ]; then
        log "✅ Lien symbolique créé: /usr/local/bin/redforge"
    else
        log_error "❌ Échec de création des liens symboliques"
    fi
    
    if [[ ":$PATH:" != *":/usr/local/bin:"* ]]; then
        echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
    fi
}

# Création du service systemd (avec dépendance TOR)
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
ExecStart=$REDFORGE_HOME/.venv/bin/python $REDFORGE_HOME/bin/RedForge -g
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    log "Service systemd créé (redforge.service) avec dépendance TOR"
}

# Désinstallation
uninstall() {
    log_warning "Désinstallation de RedForge..."
    
    read -p "Êtes-vous sûr de vouloir désinstaller RedForge ? (o/N): " confirm
    if [[ ! "$confirm" =~ ^[oO]$ ]]; then
        log "Désinstallation annulée"
        exit 0
    fi
    
    systemctl stop redforge.service 2>/dev/null || true
    systemctl disable redforge.service 2>/dev/null || true
    
    rm -f /usr/local/bin/redforge /usr/local/bin/RedForge
    rm -rf "$REDFORGE_HOME"
    
    read -p "Supprimer la configuration utilisateur ? (o/N): " del_config
    if [[ "$del_config" =~ ^[oO]$ ]]; then
        rm -rf "$REDFORGE_USER_HOME"
        log "Configuration utilisateur supprimée"
    fi
    
    read -p "Supprimer les wordlists téléchargées ? (o/N): " del_wordlists
    if [[ "$del_wordlists" =~ ^[oO]$ ]]; then
        rm -rf /usr/share/seclists
        log "Wordlists supprimées"
    fi
    
    read -p "Supprimer TOR ? (o/N): " del_tor
    if [[ "$del_tor" =~ ^[oO]$ ]]; then
        apt remove -y tor
        log "TOR désinstallé"
    fi
    
    log "RedForge désinstallé"
}

# Installation complète
full_install() {
    log_info "Démarrage de l'installation complète de RedForge v2.0..."
    
    check_root
    detect_os
    install_system_deps
    install_tor
    create_executable
    create_init_files
    create_venv
    install_python_deps
    copy_files
    create_missing_modules
    install_wordlists
    configure_environment
    create_global_symlinks
    create_systemd_service
    
    show_completion
}

# Installation minimale
minimal_install() {
    log_info "Démarrage de l'installation minimale..."
    
    check_root
    detect_os
    install_system_deps
    install_tor
    create_executable
    create_init_files
    create_venv
    install_python_deps
    copy_files
    create_missing_modules
    configure_environment
    create_global_symlinks
    
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
        3) full_install ;;
        4) uninstall ;;
        5) echo "Au revoir!"; exit 0 ;;
        *) log_error "Choix invalide"; exit 1 ;;
    esac
}

# Message de fin
show_completion() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                      INSTALLATION RÉUSSIE !                      ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}📖 Pour commencer :${NC}"
    echo -e "  ${GREEN}redforge --help${NC}                    - Afficher l'aide"
    echo -e "  ${GREEN}redforge -t example.com${NC}            - Scan rapide"
    echo -e "  ${GREEN}redforge -g${NC}                        - Lancer l'interface graphique"
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
    echo ""
    echo -e "${CYAN}🔧 Commandes disponibles :${NC}"
    echo -e "  ${GREEN}redforge --version${NC}                 - Version"
    echo -e "  ${GREEN}redforge --check-deps${NC}              - Vérifier les dépendances"
    echo -e "  ${GREEN}systemctl start redforge${NC}           - Démarrer le service"
    echo ""
    echo -e "${GREEN}💡 Vous pouvez maintenant lancer redforge depuis n'importe quel dossier !${NC}"
    echo -e "${GREEN}🕵️ TOR est installé et configuré pour le mode furtif !${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Note : RedForge nécessite les droits sudo pour les fonctionnalités avancées${NC}"
    echo ""
    echo -e "${BLUE}Merci d'utiliser RedForge v2.0 ! ${NC}"
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