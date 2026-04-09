#!/bin/bash
# ========================================
# RedForge - Script de mise à jour des outils
# Met à jour les outils utilisés par RedForge
# Version: 2.0.0 - Support Multi-Attaque, Stealth & APT
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
    echo -e "${CYAN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║           RedForge - Mise à jour des outils v2.0                ║
║        Support Multi-Attaque, Mode Furtif & APT                 ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Configuration
LOG_FILE="/tmp/redforge_update.log"
REDFORGE_DIR="/opt/RedForge"
BACKUP_DIR="/tmp/redforge_update_backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Nouvelles configurations
STEALTH_TOOLS=(
    "tor"
    "proxychains"
    "macchanger"
    "wireguard"
    "openssl"
    "stunnel4"
)

APT_TOOLS=(
    "metasploit-framework"
    "cobaltstrike"
    "empire"
    "bloodhound"
    "mimikatz"
    "psexec"
    "winexe"
)

MULTI_ATTACK_TOOLS=(
    "parallel"
    "tmux"
    "screen"
    "gnu-parallel"
)

# Fonctions
print_status() { echo -e "${BLUE}[*]${NC} $1"; }
print_success() { echo -e "${GREEN}[+]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[-]${NC} $1"; }
print_info() { echo -e "${MAGENTA}[i]${NC} $1"; }

# Logger
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Vérifier les droits root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Ce script doit être exécuté en tant que root"
        exit 1
    fi
}

# Vérifier la connexion Internet
check_internet() {
    print_status "Vérification de la connexion Internet..."
    if ! ping -c 1 google.com &> /dev/null; then
        print_error "Pas de connexion Internet"
        exit 1
    fi
    print_success "Connexion Internet OK"
}

# Sauvegarder la configuration avant mise à jour
backup_config() {
    print_status "Sauvegarde de la configuration..."
    
    mkdir -p "$BACKUP_DIR"
    
    if [ -d "/root/.RedForge" ]; then
        cp -r /root/.RedForge "$BACKUP_DIR/"
        print_success "Configuration sauvegardée dans $BACKUP_DIR"
        log_message "Configuration sauvegardée"
    fi
    
    if [ -f "$REDFORGE_DIR/config/local.json" ]; then
        cp "$REDFORGE_DIR/config/local.json" "$BACKUP_DIR/"
        print_success "Configuration locale sauvegardée"
    fi
    
    if [ -d "$REDFORGE_DIR/config/profiles" ]; then
        cp -r "$REDFORGE_DIR/config/profiles" "$BACKUP_DIR/"
        print_success "Profils sauvegardés"
    fi
}

# Mettre à jour le système
update_system() {
    print_status "Mise à jour du système..."
    
    apt update
    apt upgrade -y
    apt dist-upgrade -y
    apt autoremove -y
    
    print_success "Système mis à jour"
    log_message "Système mis à jour"
}

# Mettre à jour les outils APT standards
update_apt_tools() {
    print_status "Mise à jour des outils APT..."
    
    local tools=(
        "nmap"
        "metasploit-framework"
        "sqlmap"
        "hydra"
        "whatweb"
        "dirb"
        "nikto"
        "wpscan"
        "gobuster"
        "ffuf"
        "masscan"
        "zaproxy"
    )
    
    local updated=0
    local failed=0
    
    for tool in "${tools[@]}"; do
        if apt-cache policy "$tool" 2>/dev/null | grep -q "Installed"; then
            print_status "Mise à jour de $tool..."
            if apt install --only-upgrade -y "$tool"; then
                print_success "$tool mis à jour"
                ((updated++))
                log_message "$tool mis à jour"
            else
                print_warning "Échec mise à jour de $tool"
                ((failed++))
            fi
        else
            print_warning "$tool non installé, installation..."
            if apt install -y "$tool"; then
                print_success "$tool installé"
                ((updated++))
                log_message "$tool installé"
            else
                print_error "Échec installation de $tool"
                ((failed++))
            fi
        fi
    done
    
    print_info "APT: $updated outils mis à jour, $failed échecs"
}

# Mettre à jour les outils multi-attaque
update_multi_attack_tools() {
    print_status "Mise à jour des outils pour attaques multiples..."
    
    local updated=0
    local failed=0
    
    for tool in "${MULTI_ATTACK_TOOLS[@]}"; do
        if apt-cache policy "$tool" 2>/dev/null | grep -q "Installed"; then
            print_status "Mise à jour de $tool..."
            if apt install --only-upgrade -y "$tool"; then
                print_success "$tool mis à jour"
                ((updated++))
                log_message "$tool mis à jour"
            else
                print_warning "Échec mise à jour de $tool"
                ((failed++))
            fi
        else
            print_warning "$tool non installé, installation..."
            if apt install -y "$tool"; then
                print_success "$tool installé"
                ((updated++))
                log_message "$tool installé"
            else
                print_error "Échec installation de $tool"
                ((failed++))
            fi
        fi
    done
    
    print_info "Multi-Attaque: $updated outils mis à jour, $failed échecs"
}

# Mettre à jour les outils furtifs (Stealth)
update_stealth_tools() {
    print_status "Mise à jour des outils furtifs (Stealth)..."
    
    local updated=0
    local failed=0
    
    for tool in "${STEALTH_TOOLS[@]}"; do
        if apt-cache policy "$tool" 2>/dev/null | grep -q "Installed"; then
            print_status "Mise à jour de $tool..."
            if apt install --only-upgrade -y "$tool"; then
                print_success "$tool mis à jour"
                ((updated++))
                log_message "$tool mis à jour"
            else
                print_warning "Échec mise à jour de $tool"
                ((failed++))
            fi
        else
            print_warning "$tool non installé, installation..."
            if apt install -y "$tool"; then
                print_success "$tool installé"
                ((updated++))
                log_message "$tool installé"
            else
                print_error "Échec installation de $tool"
                ((failed++))
            fi
        fi
    done
    
    print_info "Stealth: $updated outils mis à jour, $failed échecs"
}

# Mettre à jour les outils APT
update_apt_advanced_tools() {
    print_status "Mise à jour des outils APT avancés..."
    
    local updated=0
    local failed=0
    
    for tool in "${APT_TOOLS[@]}"; do
        if apt-cache policy "$tool" 2>/dev/null | grep -q "Installed"; then
            print_status "Mise à jour de $tool..."
            if apt install --only-upgrade -y "$tool"; then
                print_success "$tool mis à jour"
                ((updated++))
                log_message "$tool mis à jour"
            else
                print_warning "Échec mise à jour de $tool"
                ((failed++))
            fi
        else
            print_warning "$tool non installé, installation..."
            if apt install -y "$tool"; then
                print_success "$tool installé"
                ((updated++))
                log_message "$tool installé"
            else
                print_error "Échec installation de $tool"
                ((failed++))
            fi
        fi
    done
    
    print_info "APT avancé: $updated outils mis à jour, $failed échecs"
}

# Mettre à jour les outils Python
update_python_tools() {
    print_status "Mise à jour des outils Python..."
    
    local python_tools=(
        "sqlmap"
        "xsstrike"
        "wafw00f"
        "jwt_tool"
        "pwntools"
        "requests"
        "beautifulsoup4"
        "paramiko"
        "scapy"
        "impacket"
        "stem"  # Pour Tor
        "fake-useragent"  # Pour rotation UA
        "cloudscraper"  # Pour contournement Cloudflare
    )
    
    local updated=0
    local failed=0
    
    # Mettre à jour pip d'abord
    pip3 install --upgrade pip
    
    for tool in "${python_tools[@]}"; do
        print_status "Mise à jour de $tool..."
        if pip3 install --upgrade "$tool"; then
            print_success "$tool mis à jour"
            ((updated++))
            log_message "$tool mis à jour"
        else
            print_warning "Échec mise à jour de $tool"
            ((failed++))
        fi
    done
    
    print_info "Python: $updated outils mis à jour, $failed échecs"
}

# Mettre à jour les outils Python furtifs
update_stealth_python_tools() {
    print_status "Mise à jour des outils Python furtifs..."
    
    local stealth_python_tools=(
        "selenium"
        "undetected-chromedriver"
        "pysocks"
        "requests[socks]"
        "pycryptodome"
        "pycryptodomex"
        "steganography"
        "dnslib"
    )
    
    local updated=0
    local failed=0
    
    for tool in "${stealth_python_tools[@]}"; do
        print_status "Mise à jour de $tool..."
        if pip3 install --upgrade "$tool"; then
            print_success "$tool mis à jour"
            ((updated++))
            log_message "$tool mis à jour"
        else
            print_warning "Échec mise à jour de $tool"
            ((failed++))
        fi
    done
    
    print_info "Stealth Python: $updated outils mis à jour, $failed échecs"
}

# Mettre à jour les outils Go
update_go_tools() {
    print_status "Mise à jour des outils Go..."
    
    if ! command -v go &> /dev/null; then
        print_warning "Go non installé, installation..."
        apt install -y golang-go
        print_success "Go installé"
    fi
    
    local go_tools=(
        "github.com/hahwul/dalfox/v2@latest"
        "github.com/ffuf/ffuf@latest"
        "github.com/tomnomnom/waybackurls@latest"
        "github.com/tomnomnom/assetfinder@latest"
        "github.com/projectdiscovery/httpx/cmd/httpx@latest"
        "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
        "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
        "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
        "github.com/projectdiscovery/katana/cmd/katana@latest"
        "github.com/projectdiscovery/chaos-client/cmd/chaos@latest"
        "github.com/projectdiscovery/notify/cmd/notify@latest"
    )
    
    local updated=0
    local failed=0
    
    for tool in "${go_tools[@]}"; do
        print_status "Mise à jour de $(basename "$tool")..."
        if go install "$tool"; then
            print_success "$(basename "$tool") mis à jour"
            ((updated++))
            log_message "$(basename "$tool") mis à jour"
        else
            print_warning "Échec mise à jour de $(basename "$tool")"
            ((failed++))
        fi
    done
    
    print_info "Go: $updated outils mis à jour, $failed échecs"
}

# Mettre à jour les wordlists
update_wordlists() {
    print_status "Mise à jour des wordlists..."
    
    local WORDLIST_DIR="/usr/share/wordlists"
    mkdir -p "$WORDLIST_DIR"
    
    # SecLists
    if [ -d "$WORDLIST_DIR/SecLists" ]; then
        print_status "Mise à jour de SecLists..."
        cd "$WORDLIST_DIR/SecLists"
        git pull
        print_success "SecLists mis à jour"
        log_message "SecLists mis à jour"
    else
        print_status "Téléchargement de SecLists..."
        git clone --depth 1 https://github.com/danielmiessler/SecLists.git "$WORDLIST_DIR/SecLists"
        print_success "SecLists téléchargé"
        log_message "SecLists téléchargé"
    fi
    
    # Wordlists furtives
    local STEALTH_WORDLIST_DIR="$WORDLIST_DIR/stealth_wordlists"
    mkdir -p "$STEALTH_WORDLIST_DIR"
    
    if [ ! -f "$STEALTH_WORDLIST_DIR/small_passwords.txt" ]; then
        print_status "Création de wordlists furtives..."
        cat > "$STEALTH_WORDLIST_DIR/small_passwords.txt" << EOF
password
123456
admin
user
test
guest
welcome
qwerty
abc123
letmein
monkey
dragon
master
shadow
EOF
        print_success "Wordlist furtive créée"
    fi
    
    # Wordlists pour attaques multiples
    local MULTI_ATTACK_WORDLIST_DIR="$WORDLIST_DIR/multi_attack_wordlists"
    mkdir -p "$MULTI_ATTACK_WORDLIST_DIR"
    
    if [ ! -f "$MULTI_ATTACK_WORDLIST_DIR/combinations.txt" ]; then
        print_status "Création de wordlists pour attaques multiples..."
        cat > "$MULTI_ATTACK_WORDLIST_DIR/combinations.txt" << EOF
admin:admin
admin:password
admin:123456
root:root
root:toor
user:user
user:password
test:test
guest:guest
EOF
        print_success "Wordlist multi-attaque créée"
    fi
    
    # RockYou
    if [ ! -f "$WORDLIST_DIR/rockyou.txt" ]; then
        if [ -f /usr/share/wordlists/rockyou.txt.gz ]; then
            gunzip /usr/share/wordlists/rockyou.txt.gz
            print_success "RockYou décompressé"
        elif [ -f "$WORDLIST_DIR/rockyou.txt.gz" ]; then
            gunzip "$WORDLIST_DIR/rockyou.txt.gz"
            print_success "RockYou décompressé"
        else
            print_status "Téléchargement de RockYou..."
            wget -O "$WORDLIST_DIR/rockyou.txt.gz" \
                "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt.gz"
            gunzip "$WORDLIST_DIR/rockyou.txt.gz"
            print_success "RockYou téléchargé et décompressé"
            log_message "RockYou téléchargé"
        fi
    fi
    
    print_success "Wordlists mises à jour"
    log_message "Wordlists mises à jour"
}

# Mettre à jour RedForge lui-même
update_redforge() {
    print_status "Mise à jour de RedForge..."
    
    if [ ! -d "$REDFORGE_DIR" ]; then
        print_error "RedForge non trouvé dans $REDFORGE_DIR"
        return 1
    fi
    
    cd "$REDFORGE_DIR"
    
    # Sauvegarder la configuration
    backup_config
    
    # Mise à jour via git
    if [ -d ".git" ]; then
        git fetch --all
        git reset --hard origin/main
        git pull
        print_success "Code mis à jour"
        log_message "Code mis à jour"
    else
        print_warning "Dépôt git non trouvé, téléchargement..."
        cd /tmp
        wget "https://github.com/Elfried002/RedForge/archive/refs/heads/main.zip" -O redforge.zip
        unzip -q redforge.zip
        rm -rf "$REDFORGE_DIR"/*
        cp -r RedForge-main/* "$REDFORGE_DIR/"
        rm -rf RedForge-main redforge.zip
        print_success "RedForge téléchargé"
        log_message "RedForge téléchargé"
    fi
    
    # Réinstaller les dépendances Python
    if [ -f "$REDFORGE_DIR/requirements.txt" ]; then
        pip3 install -r "$REDFORGE_DIR/requirements.txt" --upgrade
        print_success "Dépendances Python mises à jour"
        log_message "Dépendances Python mises à jour"
    fi
    
    # Installer les dépendances furtives si disponibles
    if [ -f "$REDFORGE_DIR/requirements-stealth.txt" ]; then
        pip3 install -r "$REDFORGE_DIR/requirements-stealth.txt" --upgrade
        print_success "Dépendances furtives mises à jour"
    fi
    
    # Installer les dépendances APT si disponibles
    if [ -f "$REDFORGE_DIR/requirements-apt.txt" ]; then
        pip3 install -r "$REDFORGE_DIR/requirements-apt.txt" --upgrade
        print_success "Dépendances APT mises à jour"
    fi
    
    # Restaurer la configuration
    if [ -d "$BACKUP_DIR/.RedForge" ]; then
        cp -r "$BACKUP_DIR/.RedForge"/* /root/.RedForge/ 2>/dev/null || true
        print_success "Configuration restaurée"
    fi
    
    if [ -d "$BACKUP_DIR/profiles" ]; then
        cp -r "$BACKUP_DIR/profiles"/* "$REDFORGE_DIR/config/profiles/" 2>/dev/null || true
        print_success "Profils restaurés"
    fi
    
    print_success "RedForge mis à jour"
    log_message "RedForge mis à jour"
}

# Vérifier les versions
check_versions() {
    print_status "Vérification des versions..."
    
    echo ""
    echo "=========================================="
    echo "📊 Versions des outils"
    echo "=========================================="
    
    # Nmap
    if command -v nmap &> /dev/null; then
        echo "🔍 Nmap: $(nmap --version | head -1)"
    fi
    
    # Metasploit
    if command -v msfconsole &> /dev/null; then
        echo "🎯 Metasploit: $(msfconsole --version 2>&1 | head -1)"
    fi
    
    # SQLMap
    if command -v sqlmap &> /dev/null; then
        echo "💾 SQLMap: $(sqlmap --version | head -1)"
    fi
    
    # Hydra
    if command -v hydra &> /dev/null; then
        echo "🔐 Hydra: $(hydra -h 2>&1 | head -1)"
    fi
    
    # WhatWeb
    if command -v whatweb &> /dev/null; then
        echo "🌐 WhatWeb: $(whatweb --version 2>&1 | head -1)"
    fi
    
    # Tor
    if command -v tor &> /dev/null; then
        echo "🕵️ Tor: $(tor --version 2>&1 | head -1)"
    fi
    
    # Go
    if command -v go &> /dev/null; then
        echo "🐹 Go: $(go version)"
    fi
    
    # Python
    echo "🐍 Python: $(python3 --version)"
    echo "📦 Pip: $(pip3 --version)"
    
    echo "=========================================="
}

# Nettoyer les caches
cleanup() {
    print_status "Nettoyage des caches..."
    
    # Nettoyer pip cache
    pip3 cache purge 2>/dev/null || true
    
    # Nettoyer apt cache
    apt clean
    apt autoremove -y
    
    # Nettoyer les logs anciens
    find /var/log -name "*.log" -type f -size +100M -exec truncate -s 0 {} \; 2>/dev/null || true
    
    # Supprimer les fichiers temporaires
    rm -rf /tmp/redforge_* 2>/dev/null || true
    rm -rf "$BACKUP_DIR" 2>/dev/null || true
    
    print_success "Nettoyage terminé"
    log_message "Nettoyage effectué"
}

# Afficher le menu
show_menu() {
    echo ""
    echo "=========================================="
    echo "🔧 RedForge - Mise à jour des outils v2.0"
    echo "=========================================="
    echo "1. 📦 Mise à jour complète"
    echo "2. 🐧 Mettre à jour le système"
    echo "3. 📦 Mettre à jour les outils APT"
    echo "4. 🎯 Mettre à jour les outils multi-attaque"
    echo "5. 🕵️ Mettre à jour les outils furtifs (Stealth)"
    echo "6. 🚀 Mettre à jour les outils APT avancés"
    echo "7. 🐍 Mettre à jour les outils Python"
    echo "8. 🕵️ Mettre à jour les outils Python furtifs"
    echo "9. 🐹 Mettre à jour les outils Go"
    echo "10. 📖 Mettre à jour les wordlists"
    echo "11. 🔴 Mettre à jour RedForge"
    echo "12. 📊 Vérifier les versions"
    echo "13. 🧹 Nettoyer les caches"
    echo "14. ❌ Quitter"
    echo "=========================================="
    read -p "Votre choix [1-14]: " choice
}

# Afficher le résumé
show_summary() {
    echo ""
    echo "=========================================="
    echo "✅ Mise à jour terminée"
    echo "=========================================="
    echo "📁 Logs: $LOG_FILE"
    echo "🕐 Date: $(date)"
    echo "=========================================="
}

# Main
main() {
    show_banner
    check_root
    check_internet
    
    if [ $# -gt 0 ]; then
        case "$1" in
            --full|-f)
                update_system
                update_apt_tools
                update_multi_attack_tools
                update_stealth_tools
                update_apt_advanced_tools
                update_python_tools
                update_stealth_python_tools
                update_go_tools
                update_wordlists
                update_redforge
                check_versions
                cleanup
                show_summary
                print_success "✅ Mise à jour complète terminée!"
                ;;
            --system|-s)
                update_system
                ;;
            --apt|-a)
                update_apt_tools
                ;;
            --multi|-m)
                update_multi_attack_tools
                ;;
            --stealth|-st)
                update_stealth_tools
                update_stealth_python_tools
                ;;
            --apt-advanced|-aa)
                update_apt_advanced_tools
                ;;
            --python|-p)
                update_python_tools
                ;;
            --python-stealth|-ps)
                update_stealth_python_tools
                ;;
            --go|-g)
                update_go_tools
                ;;
            --wordlists|-w)
                update_wordlists
                ;;
            --redforge|-r)
                update_redforge
                ;;
            --versions|-v)
                check_versions
                ;;
            --clean|-c)
                cleanup
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --full, -f          Mise à jour complète"
                echo "  --system, -s        Mettre à jour le système"
                echo "  --apt, -a           Mettre à jour les outils APT"
                echo "  --multi, -m         Mettre à jour les outils multi-attaque"
                echo "  --stealth, -st      Mettre à jour les outils furtifs"
                echo "  --apt-advanced, -aa Mettre à jour les outils APT avancés"
                echo "  --python, -p        Mettre à jour les outils Python"
                echo "  --python-stealth, -ps Mettre à jour les outils Python furtifs"
                echo "  --go, -g            Mettre à jour les outils Go"
                echo "  --wordlists, -w     Mettre à jour les wordlists"
                echo "  --redforge, -r      Mettre à jour RedForge"
                echo "  --versions, -v      Vérifier les versions"
                echo "  --clean, -c         Nettoyer les caches"
                echo "  --help, -h          Afficher cette aide"
                echo ""
                echo "Exemples:"
                echo "  $0 --full                    # Mise à jour complète"
                echo "  $0 --stealth --python       # Mise à jour outils furtifs"
                echo "  $0 --apt-advanced           # Mise à jour outils APT"
                exit 0
                ;;
            *)
                print_error "Option inconnue: $1"
                echo "Utilisez --help pour plus d'informations"
                exit 1
                ;;
        esac
    else
        while true; do
            show_menu
            case $choice in
                1)
                    update_system
                    update_apt_tools
                    update_multi_attack_tools
                    update_stealth_tools
                    update_apt_advanced_tools
                    update_python_tools
                    update_stealth_python_tools
                    update_go_tools
                    update_wordlists
                    update_redforge
                    check_versions
                    cleanup
                    show_summary
                    print_success "✅ Mise à jour complète terminée!"
                    break
                    ;;
                2) update_system ;;
                3) update_apt_tools ;;
                4) update_multi_attack_tools ;;
                5) update_stealth_tools ;;
                6) update_apt_advanced_tools ;;
                7) update_python_tools ;;
                8) update_stealth_python_tools ;;
                9) update_go_tools ;;
                10) update_wordlists ;;
                11) update_redforge ;;
                12) check_versions ;;
                13) cleanup ;;
                14) echo "Au revoir!"; exit 0 ;;
                *) print_error "Choix invalide" ;;
            esac
        done
    fi
}

# Exécution
main "$@"