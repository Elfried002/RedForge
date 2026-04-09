Voici une version améliorée du fichier `user_guide.md` pour RedForge v2.0 :

```markdown
# Guide d'utilisation de RedForge v2.0

## Table des matières

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Premiers pas](#premiers-pas)
4. [Interface ligne de commande (CLI)](#interface-ligne-de-commande-cli)
5. [Interface graphique (GUI)](#interface-graphique-gui)
6. [Multi-Attaques](#multi-attaques)
7. [Mode Furtif](#mode-furtif)
8. [Opérations APT](#opérations-apt)
9. [Phases d'attaque](#phases-dattaque)
10. [Types d'attaques](#types-dattaques)
11. [Génération de rapports](#génération-de-rapports)
12. [Configuration](#configuration)
13. [Dépannage](#dépannage)
14. [FAQ](#faq)
15. [Sécurité et éthique](#sécurité-et-éthique)

---

## Introduction

### Qu'est-ce que RedForge v2.0 ?

RedForge est une plateforme d'orchestration de pentest web spécialement conçue pour les équipes Red Team. La version 2.0 introduit des fonctionnalités majeures :

- **Multi-Attaques** : Lancez plusieurs attaques simultanément ou séquentiellement
- **Mode Furtif** : Évitez la détection avec délais aléatoires, TOR et proxies
- **Opérations APT** : Simulez des attaques avancées avec persistance et exfiltration

### Philosophie

- **Orchestration** : Coordonne les outils existants plutôt que de les remplacer
- **Modularité** : Architecture extensible avec système de plugins
- **Accessibilité** : Interface moderne pour améliorer l'expérience utilisateur
- **Efficacité** : Automatisation des chaînes d'exploitation
- **Discrétion** : Mode furtif avancé pour opérations sensibles

### Fonctionnalités principales v2.0

| Catégorie | Fonctionnalités |
|-----------|-----------------|
| **Attaques** | 8 catégories, 46 types d'attaques |
| **Multi-Attaques** | Séquentiel, parallèle, mixte |
| **Mode Furtif** | 4 niveaux, TOR, proxies, user-agents aléatoires |
| **Opérations APT** | 6 phases, persistance, mouvement latéral, exfiltration |
| **Interfaces** | CLI française, GUI web, API REST, WebSocket |
| **Rapports** | HTML, PDF, JSON, CSV avec graphiques |

### Prérequis système v2.0

| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| OS | Kali Linux 2024.1 / Parrot OS 6.0 | Kali Linux 2024.1+ |
| RAM | 4 GB | 8 GB+ |
| CPU | 2 cœurs | 4 cœurs+ |
| Stockage | 10 GB | 20 GB+ |
| Python | 3.11 | 3.11+ |
| TOR | Optionnel | Pour mode furtif |

---

## Installation

### Installation sur Kali Linux / Parrot OS

```bash
# Cloner le dépôt
git clone https://github.com/Elfried002/RedForge.git
cd RedForge

# Lancer l'installation complète
sudo ./install.sh

# Vérifier l'installation
redforge --version
# Devrait afficher: RedForge v2.0.0
```

### Installation avec mode furtif (TOR)

```bash
# Installer TOR
sudo apt install tor

# Activer TOR au démarrage
sudo systemctl enable tor
sudo systemctl start tor

# Installer RedForge avec support TOR
sudo ./install.sh --with-tor
```

### Installation Docker

```bash
# Cloner le dépôt
git clone https://github.com/Elfried002/RedForge.git
cd RedForge

# Démarrer avec tous les services
docker-compose --profile full up -d

# Accéder à l'interface
# http://localhost:5000

# Voir les logs
docker-compose logs -f redforge
```

### Vérification de l'installation

```bash
# Vérifier la version
redforge --version

# Vérifier les dépendances
redforge --check-deps

# Tester le mode furtif
redforge --test-stealth --target example.com

# Tester les multi-attaques
redforge --test-multi --config examples/multi_config.json
```

---

## Premiers pas

### Démarrage rapide

```bash
# Lancer l'interface graphique (recommandé pour débuter)
sudo redforge -g

# Ou utiliser la ligne de commande
redforge --help
```

### Premier scan simple

```bash
# Scan de reconnaissance
redforge -t https://example.com -p footprint

# Scan complet avec rapport
redforge -t https://example.com -p all -o rapport.html
```

### Première multi-attaque

Créez un fichier `multi_config.json` :

```json
{
    "name": "Mon premier audit",
    "target": "https://example.com",
    "attacks": [
        {"category": "injection", "type": "sql"},
        {"category": "cross_site", "type": "xss"},
        {"category": "authentication", "type": "bruteforce"}
    ],
    "execution_mode": "sequential",
    "stealth_level": "medium"
}
```

Puis lancez :

```bash
redforge --multi multi_config.json
```

### Premier mode furtif

```bash
# Scan avec mode furtif niveau élevé
redforge -t https://example.com --stealth high

# Avec TOR
redforge -t https://example.com --stealth high --tor

# Configuration complète
redforge -t https://example.com --stealth paranoid --tor --proxy-list proxies.txt
```

### Première opération APT

```bash
# Opération prédéfinie
redforge --apt recon_to_exfil -t https://example.com

# Avec mode furtif
redforge --apt recon_to_exfil -t https://example.com --stealth paranoid
```

---

## Interface ligne de commande (CLI)

### Syntaxe de base

```bash
redforge [OPTIONS] [ARGUMENTS]
```

### Options principales v2.0

| Option | Description | Exemple |
|--------|-------------|---------|
| `-t, --target` | Cible à analyser | `redforge -t example.com` |
| `-f, --file` | Fichier de cibles | `redforge -f cibles.txt` |
| `-p, --phase` | Phase à exécuter | `redforge -t example.com -p scan` |
| `-g, --gui` | Interface graphique | `sudo redforge -g` |
| `-o, --output` | Fichier de rapport | `redforge -t example.com -o rapport.pdf` |
| `--multi` | Fichier config multi-attaque | `redforge --multi config.json` |
| `--stealth` | Activer mode furtif | `redforge --stealth high` |
| `--apt` | Opération APT | `redforge --apt recon_to_exfil` |
| `--tor` | Utiliser TOR | `redforge --tor` |
| `--proxy-list` | Fichier de proxies | `redforge --proxy-list proxies.txt` |
| `--help` | Afficher l'aide | `redforge --help` |
| `--version` | Afficher la version | `redforge --version` |

### Phases disponibles

| Phase | Description | Commande |
|-------|-------------|----------|
| `footprint` | Reconnaissance | `redforge -t example.com -p footprint` |
| `analysis` | Analyse approfondie | `redforge -t example.com -p analysis` |
| `scan` | Scan de vulnérabilités | `redforge -t example.com -p scan` |
| `exploit` | Exploitation | `redforge -t example.com -p exploit` |
| `all` | Toutes les phases | `redforge -t example.com -p all` |

### Exemples d'utilisation v2.0

```bash
# Scan simple avec mode furtif
redforge -t https://example.com --stealth high

# Multi-attaque parallèle
redforge --multi config.json --mode parallel --max-parallel 5

# Opération APT complète
redforge --apt recon_to_exfil -t example.com --stealth paranoid

# Scan avec rotation de proxies
redforge -t example.com --stealth high --proxy-list proxies.txt

# Scan avec TOR
redforge -t example.com --stealth medium --tor

# Scanner plusieurs cibles en mode furtif
redforge -f cibles.txt --stealth high -o resultats.json

# Mode interactif
redforge -i
```

### Mode interactif v2.0

```bash
redforge -i
```

**Commandes disponibles :**

| Commande | Description |
|----------|-------------|
| `help` | Afficher l'aide |
| `scan <target>` | Scanner une cible |
| `multi <config>` | Lancer multi-attaque |
| `stealth [level]` | Configurer mode furtif |
| `apt <operation>` | Lancer opération APT |
| `attack <category> <type>` | Lancer une attaque spécifique |
| `list` | Lister les modules disponibles |
| `status` | Afficher le statut |
| `exit` | Quitter |

---

## Interface graphique (GUI)

### Lancement

```bash
sudo redforge -g
# ou
redforge --gui
```

L'interface est accessible sur `http://localhost:5000`

### Structure de l'interface v2.0

#### Tableau de bord
- Statistiques en temps réel (cibles, attaques, vulnérabilités)
- Graphiques interactifs (Chart.js)
- Métriques furtives (score, risque détection)
- Multi-attaques en cours
- Opérations APT en cours
- Alertes de détection
- Activités récentes

#### Onglet Attaques
- **Attaques simples** : 8 catégories, sélection par type
- **Multi-attaques** : Configuration avancée, modes séquentiel/parallèle
- **Mode Furtif** : Niveaux, TOR, proxies, user-agents
- **Opérations APT** : Prédéfinies et personnalisées

#### Onglet Rapports
- Génération multi-format (HTML, PDF, JSON, CSV)
- Templates (Standard, Direction, Technique, APT, Stealth)
- Aperçu avant téléchargement
- Programmation automatique
- Historique des rapports

#### Onglet Paramètres
- Configuration générale
- Mode furtif (niveaux, TOR, proxies)
- Multi-attaques (threads, délais)
- Opérations APT (persistance, exfiltration)
- Gestion des outils
- Wordlists personnalisées
- Notifications (email, webhook)

#### Onglet Aide
- Documentation intégrée
- Tutoriels interactifs
- FAQ
- Support
- Raccourcis clavier

---

## Multi-Attaques

### Configuration

Créez un fichier JSON de configuration :

```json
{
    "name": "Audit de sécurité complet",
    "target": "https://example.com",
    "description": "Scan complet de l'application web",
    "attacks": [
        {
            "category": "injection",
            "type": "sql",
            "options": {"level": 3, "techniques": "BEUSTQ"}
        },
        {
            "category": "cross_site",
            "type": "xss",
            "options": {"payloads": "all", "level": 3}
        },
        {
            "category": "authentication",
            "type": "bruteforce",
            "options": {
                "users": ["admin", "root"],
                "wordlist": "common_passwords.txt",
                "threads": 5
            }
        },
        {
            "category": "file_system",
            "type": "lfi_rfi",
            "options": {"depth": 5, "payloads": "all"}
        },
        {
            "category": "infrastructure",
            "type": "waf_bypass",
            "options": {"techniques": ["encoding", "case_swapping"]}
        }
    ],
    "execution_mode": "sequential",
    "stealth_level": "high",
    "delay_between_attacks": 2,
    "stop_on_error": false,
    "timeout": 600,
    "output": "rapport_multi.json"
}
```

### Modes d'exécution

| Mode | Description | Avantages | Inconvénients |
|------|-------------|-----------|---------------|
| **Séquentiel** | Attaques une par une | Discret, stable | Plus lent |
| **Parallèle** | Attaques simultanées | Rapide | Détectable |
| **Mixte** | Groupes parallèles | Équilibre | Configuration complexe |

### Lancement

```bash
# Mode séquentiel (recommandé pour discrétion)
redforge --multi config.json --mode sequential

# Mode parallèle (plus rapide)
redforge --multi config.json --mode parallel --max-parallel 5

# Avec niveau furtif spécifique
redforge --multi config.json --stealth paranoid

# Avec rapport personnalisé
redforge --multi config.json -o rapport_multi.html
```

### Surveillance

Pendant l'exécution, vous pouvez :

- Voir la progression en temps réel via l'interface web
- Suivre les logs : `tail -f ~/.RedForge/logs/multi_attack.log`
- Recevoir des notifications (email/webhook)
- Arrêter une multi-attaque : `redforge --multi-stop <task_id>`

---

## Mode Furtif

### Niveaux de furtivité

| Niveau | Délai | Jitter | TOR | Proxies | Détection |
|--------|-------|--------|-----|---------|-----------|
| **Low** | 0.5s | 10% | ❌ | ❌ | Facile |
| **Medium** | 1.5s | 30% | ❌ | ❌ | Moyenne |
| **High** | 3.0s | 50% | ✅ | ❌ | Difficile |
| **Paranoid** | 5.0s | 70% | ✅ | ✅ | Très difficile |

### Configuration avancée

Créez un fichier `stealth_config.json` :

```json
{
    "enabled": true,
    "level": "high",
    "random_user_agents": true,
    "user_agents_file": "/path/to/user_agents.txt",
    "use_tor": true,
    "tor_control_port": 9051,
    "tor_socks_port": 9050,
    "rotate_proxies": true,
    "proxy_list": [
        "socks5://127.0.0.1:9050",
        "http://proxy1.example.com:8080",
        "socks4://proxy2.example.com:1080"
    ],
    "mimic_human": true,
    "random_delays": true,
    "min_delay": 1.0,
    "max_delay": 5.0,
    "jitter": 0.3,
    "slow_loris": false,
    "dns_over_https": false
}
```

### Lancement

```bash
# Activer le mode furtif avec niveau medium (défaut)
redforge -t example.com --stealth

# Niveau spécifique
redforge -t example.com --stealth high

# Avec TOR
redforge -t example.com --stealth --tor

# Avec rotation de proxies
redforge -t example.com --stealth --proxy-list proxies.txt

# Configuration complète
redforge -t example.com --stealth paranoid --tor --proxy-list proxies.txt --user-agents ua.txt
```

### Commandes pendant l'exécution

| Commande | Action |
|----------|--------|
| `Ctrl+Shift+S` | Activer/désactiver mode furtif |
| `Ctrl+Shift+D` | Augmenter niveau furtif |
| `Ctrl+Shift+U` | Diminuer niveau furtif |
| `Ctrl+Shift+T` | Basculer TOR |
| `Ctrl+Shift+P` | Changer proxy |

### Métriques furtives

Le tableau de bord affiche en temps réel :

- **Score de furtivité** (0-100%) : Évalue la discrétion
- **Risque de détection** : Faible, Moyen, Élevé
- **Alertes évitées** : Nombre d'alertes contournées
- **Délai moyen** : Temps moyen entre requêtes
- **TOR actif** : Statut du routage TOR
- **Proxy actuel** : Proxy utilisé
- **User-Agent** : User-Agent courant

---

## Opérations APT

### Opérations prédéfinies

| Opération | Description | Phases | Durée estimée |
|-----------|-------------|--------|---------------|
| **recon_to_exfil** | Cycle complet APT | 6 phases | 30-60 min |
| **web_app_compromise** | Compromission web | 4 phases | 15-30 min |
| **lateral_movement** | Mouvement latéral | 3 phases | 20-40 min |
| **persistence** | Persistance avancée | 2 phases | 10-20 min |

### Configuration personnalisée

Créez un fichier `apt_config.json` :

```json
{
    "name": "Opération personnalisée - Infrastructure critique",
    "description": "Simulation APT sur infrastructure sensible",
    "target": "https://example.com",
    "phases": [
        {
            "name": "Reconnaissance approfondie",
            "attacks": ["port_scan", "service_enum", "directory_bruteforce", "technology_detect", "dns_recon"],
            "options": {"stealth": true, "timeout": 300}
        },
        {
            "name": "Accès initial",
            "attacks": ["sql_injection", "xss", "file_upload", "command_injection"],
            "options": {"payloads": "custom", "level": 4}
        },
        {
            "name": "Persistance",
            "attacks": ["backdoor", "scheduled_task", "registry_persistence"],
            "options": {"method": "registry", "location": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"}
        },
        {
            "name": "Élévation de privilèges",
            "attacks": ["sudo_abuse", "kernel_exploit"],
            "options": {"techniques": ["cve-2021-3156", "cve-2022-0847"]}
        },
        {
            "name": "Mouvement latéral",
            "attacks": ["ssh_pivot", "smb_exec", "wmi_exec"],
            "options": {"targets": ["192.168.1.0/24"], "credentials": "credentials.txt"}
        },
        {
            "name": "Exfiltration de données",
            "attacks": ["dns_exfil"],
            "options": {"server": "c2.example.com", "chunk_size": 512, "encryption": "aes-256-gcm"}
        }
    ],
    "persistence": {
        "type": "registry",
        "location": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "key": "WindowsUpdate",
        "payload": "backdoor.exe"
    },
    "evasion": {
        "disable_logging": true,
        "clear_events": true,
        "use_living_off_land": true,
        "timestomp": true
    },
    "exfiltration": {
        "method": "dns_tunneling",
        "server": "c2.example.com",
        "port": 53,
        "protocol": "udp",
        "chunk_size": 512,
        "encryption": "aes-256-gcm",
        "compression": true
    },
    "cleanup": true,
    "reporting": {
        "include_iocs": true,
        "include_ttps": true,
        "include_mitre_attack": true,
        "include_timeline": true
    }
}
```

### Lancement

```bash
# Opération prédéfinie
redforge --apt recon_to_exfil -t example.com

# Opération personnalisée
redforge --apt custom -c apt_config.json -t example.com

# Avec mode furtif
redforge --apt recon_to_exfil -t example.com --stealth high

# Sans nettoyage (pour investigation)
redforge --apt recon_to_exfil -t example.com --no-cleanup

# Avec reporting détaillé
redforge --apt recon_to_exfil -t example.com --report-format pdf --report-template apt
```

### Surveillance en temps réel

Pendant l'exécution, l'interface web affiche :

- **Timeline interactive** : Progression des phases
- **Statut par phase** : Succès/échec, durée, attaques
- **Alertes de détection** : Niveau de risque
- **Métriques** : Score de furtivité, temps restant
- **IOCs générés** : Indicateurs de compromission
- **Logs détaillés** : Actions effectuées

### Nettoyage post-opération

```bash
# Nettoyage automatique (par défaut)
redforge --apt recon_to_exfil -t example.com

# Nettoyage manuel
redforge --apt-cleanup --operation-id apt_1234567890

# Forcer le nettoyage
redforge --apt-cleanup --force --operation-id apt_1234567890
```

---

## Phases d'attaque

### Phase 1: Footprinting (Reconnaissance)

**Objectif** : Collecter un maximum d'informations sur la cible sans être intrusif.

**Découvertes** :
- Adresses IP et sous-domaines
- Services et ports ouverts
- Technologies web utilisées
- Serveurs DNS et emails
- Certificats SSL/TLS
- Enregistrements DNS (A, AAAA, MX, TXT, NS)

**Commandes** :

```bash
# Scan simple
redforge -t example.com -p footprint

# Scan complet avec énumération DNS
redforge -t example.com -p footprint --dns-enum --subdomains

# Avec mode furtif
redforge -t example.com -p footprint --stealth medium
```

### Phase 2: Analysis (Analyse approfondie)

**Objectif** : Analyser en détail le fonctionnement de l'application.

**Analyses** :
- Structure des répertoires
- Paramètres GET/POST
- Points d'entrée utilisateur
- Système d'authentification
- Endpoints API
- Workflows et logique métier

**Commandes** :

```bash
# Analyse basique
redforge -t example.com -p analysis

# Force brute des répertoires
redforge -t example.com -p analysis --dir-bruteforce

# Analyse des paramètres
redforge -t example.com -p analysis --param-analysis
```

### Phase 3: Scanning (Scan de vulnérabilités)

**Objectif** : Détecter automatiquement les vulnérabilités.

**Vulnérabilités détectées** :
- Injections SQL (SQLi)
- Cross-Site Scripting (XSS)
- LFI/RFI
- Command Injection
- CSRF, SSRF, XXE
- Path Traversal
- Buffer Overflow

**Commandes** :

```bash
# Scan complet
redforge -t example.com -p scan

# Scan SQLi + XSS
redforge -t example.com -p scan --sqlmap --xss

# Scan niveau élevé
redforge -t example.com -p scan --level 4

# Scan avec mode furtif
redforge -t example.com -p scan --stealth high
```

### Phase 4: Exploitation

**Objectif** : Exploiter les vulnérabilités découvertes.

**Capacités** :
- Obtention de shell reverse
- Upload de webshells
- Élévation de privilèges
- Pillage de données
- Persistance
- Mouvement latéral

**Commandes** :

```bash
# Exploitation automatique
redforge -t example.com -p exploit

# Shell reverse
redforge -t example.com -p exploit --reverse-shell --lport 4444

# Upload de webshell
redforge -t example.com -p exploit --upload-webshell --shell-type php

# Élévation de privilèges
redforge -t example.com -p exploit --privesc
```

---

## Types d'attaques

### Injections (7 types)

| Attaque | Description | Sévérité | CVSS |
|---------|-------------|----------|------|
| SQL Injection | Injection de requêtes SQL | CRITICAL | 9.8 |
| NoSQL Injection | Injection sur bases NoSQL | HIGH | 8.5 |
| Command Injection | Exécution de commandes système | CRITICAL | 9.8 |
| LDAP Injection | Manipulation de requêtes LDAP | HIGH | 8.2 |
| XPath Injection | Manipulation de requêtes XPath | HIGH | 8.2 |
| HTML Injection | Injection de code HTML | MEDIUM | 6.5 |
| Template Injection | Injection dans moteurs de templates | CRITICAL | 9.0 |

### Sessions (5 types)

| Attaque | Description | Sévérité | CVSS |
|---------|-------------|----------|------|
| Session Hijacking | Détournement de session | CRITICAL | 9.0 |
| Session Fixation | Fixation d'ID de session | HIGH | 7.5 |
| Cookie Manipulation | Altération de cookies | HIGH | 7.5 |
| JWT Attacks | Attaques sur tokens JWT | HIGH | 8.0 |
| OAuth Attacks | Attaques sur OAuth | HIGH | 8.0 |

### Cross-Site (5 types)

| Attaque | Description | Sévérité | CVSS |
|---------|-------------|----------|------|
| XSS (Reflected) | Script reflété | HIGH | 7.5 |
| XSS (Stored) | Script stocké | HIGH | 8.0 |
| XSS (DOM) | Script DOM | HIGH | 7.5 |
| CSRF | Falsification de requête | HIGH | 7.5 |
| Clickjacking | Détournement de clic | MEDIUM | 6.5 |
| CORS | Mauvaise configuration CORS | HIGH | 7.5 |

### Authentification (6 types)

| Attaque | Description | Sévérité | CVSS |
|---------|-------------|----------|------|
| Brute Force | Force brute | MEDIUM | 6.5 |
| Credential Stuffing | Réutilisation de credentials | HIGH | 8.0 |
| Password Spraying | Pulvérisation de mots de passe | MEDIUM | 6.5 |
| MFA Bypass | Contournement 2FA | HIGH | 8.5 |
| Privilege Escalation | Élévation de privilèges | CRITICAL | 9.0 |
| Race Condition | Condition de concurrence | MEDIUM | 6.0 |

---

## Génération de rapports

### Formats supportés v2.0

| Format | Description | Utilisation |
|--------|-------------|-------------|
| HTML | Rapport web interactif | Navigation, partage |
| PDF | Document professionnel | Clients, archives |
| JSON | Données structurées | API, intégration |
| CSV | Tableau de données | Excel, analyse |

### Templates v2.0

| Template | Description | Public cible |
|----------|-------------|--------------|
| **Standard** | Rapport complet | Tous publics |
| **Direction** | Résumé exécutif | Management |
| **Technique** | Détails techniques | Équipes techniques |
| **APT** | Opérations APT | Red Team |
| **Stealth** | Métriques furtives | Tests discrets |
| **Multi-Attack** | Résultats multi-attaques | Auditeurs |

### Génération depuis la CLI

```bash
# Rapport HTML standard
redforge -t example.com -p all -o rapport.html

# Rapport PDF pour la direction
redforge -t example.com -p all -o rapport.pdf --template executive

# Rapport APT
redforge --apt recon_to_exfil -t example.com -o rapport_apt.pdf

# Rapport avec métriques furtives
redforge -t example.com --stealth high -o rapport_stealth.html

# Rapport multi-attaque
redforge --multi config.json -o rapport_multi.html
```

### Génération depuis l'interface graphique

1. Allez dans la page "Rapports"
2. Sélectionnez la cible
3. Choisissez le format et le template
4. Configurez les options (graphiques, recommandations, preuves)
5. Cliquez sur "Générer le rapport"

### Structure du rapport HTML v2.0

```
📊 Résumé exécutif
├── Score de sécurité (0-100)
├── Vulnérabilités par sévérité
├── Métriques clés
└── Recommandations prioritaires

🎯 Détails des vulnérabilités
├── Critiques (avec preuves)
├── Élevées
├── Moyennes
└── Faibles

🕵️ Métriques furtives (si applicable)
├── Score de furtivité
├── Risque de détection
├── Alertes évitées
└── Configuration utilisée

📚 Multi-attaques (si applicable)
├── Mode d'exécution
├── Attaques réussies/échouées
├── Durée totale
└── Détails par attaque

🎭 Opérations APT (si applicable)
├── Timeline interactive
├── Phases réussies/échouées
├── Persistance installée
├── Mouvement latéral
└── Données exfiltrées

📈 Graphiques
├── Évolution temporelle
├── Distribution par type
├── Sévérité
└── Performance

💡 Recommandations
├── Correctifs prioritaires
├── Bonnes pratiques
├── Mesures de sécurité
└── Plan d'action

📎 Annexes
├── Logs
├── Payloads
├── Preuves techniques
└── IoCs (Indicators of Compromise)
```

---

## Configuration

### Fichier de configuration v2.0

Le fichier de configuration se trouve à : `~/.RedForge/config.json`

```json
{
    "version": "2.0.0",
    "language": "fr_FR",
    "theme": "dark",
    "timeout": 300,
    "threads": 10,
    "auto_save": true,
    "verify_ssl": true,
    "stealth": {
        "enabled": false,
        "default_level": "medium",
        "random_user_agents": true,
        "use_tor": false,
        "rotate_proxies": false,
        "mimic_human": true,
        "random_delays": true,
        "min_delay": 0.5,
        "max_delay": 3.0,
        "jitter": 0.3
    },
    "multi_attack": {
        "default_mode": "sequential",
        "max_parallel": 5,
        "delay_between_attacks": 1,
        "stop_on_error": false,
        "save_intermediate": true
    },
    "apt": {
        "auto_cleanup": true,
        "phase_delay": 5,
        "log_all_phases": true,
        "require_confirmation": false,
        "persistence_dir": "/tmp/redforge_persistence",
        "exfil_method": "http",
        "chunk_size": 512
    },
    "proxy": {
        "enabled": false,
        "type": "http",
        "host": "",
        "port": 8080,
        "username": "",
        "password": ""
    },
    "notifications": {
        "scan_complete": true,
        "vulnerability": true,
        "session": false,
        "report": true,
        "multi_complete": true,
        "apt_complete": true,
        "stealth_alert": true,
        "email": "",
        "webhook": ""
    },
    "tools": {
        "nmap": "/usr/bin/nmap",
        "metasploit": "/usr/bin/msfconsole",
        "sqlmap": "/usr/bin/sqlmap",
        "tor": "/usr/bin/tor",
        "proxychains": "/usr/bin/proxychains"
    }
}
```

### Variables d'environnement v2.0

```bash
# Configuration générale
export REDFORGE_HOME=~/.RedForge
export REDFORGE_LOG_LEVEL=INFO
export REDFORGE_LANGUAGE=fr_FR
export REDFORGE_ENV=production

# Mode furtif
export STEALTH_ENABLED=false
export STEALTH_LEVEL=medium
export STEALTH_TOR_ENABLED=false
export STEALTH_PROXY_LIST=/path/to/proxies.txt
export STEALTH_USER_AGENTS=/path/to/user_agents.txt

# Multi-attaques
export MULTI_ATTACK_MAX_PARALLEL=10
export MULTI_ATTACK_DEFAULT_MODE=sequential
export MULTI_ATTACK_TIMEOUT=600

# Opérations APT
export APT_AUTO_CLEANUP=true
export APT_PHASE_DELAY=10
export APT_PERSISTENCE_DIR=/opt/redforge/persistence
export APT_C2_SERVER=https://c2.example.com
export APT_EXFIL_METHOD=dns

# Metasploit
export METASPLOIT_RPC_HOST=127.0.0.1
export METASPLOIT_RPC_PORT=55553
export METASPLOIT_RPC_PASSWORD=RedForge2024

# Proxy
export HTTP_PROXY=http://proxy:8080
export HTTPS_PROXY=http://proxy:8080
export SOCKS5_PROXY=socks5://127.0.0.1:9050
export NO_PROXY=localhost,127.0.0.1

# Notifications
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=alerts@redforge.io
export SMTP_PASSWORD=secure_password
export NOTIFICATION_WEBHOOK=https://hooks.slack.com/services/xxx
```

### Personnalisation des wordlists

Les wordlists se trouvent dans `~/.RedForge/wordlists/`

```bash
# Structure des wordlists
~/.RedForge/wordlists/
├── passwords/          # Mots de passe
│   ├── common.txt
│   └── rockyou.txt
├── usernames/          # Utilisateurs
│   └── common.txt
├── directories/        # Répertoires
│   └── common.txt
├── subdomains/         # Sous-domaines
│   └── common.txt
└── custom/             # Wordlists personnalisées
    └── ma_wordlist.txt

# Ajouter une wordlist
cp ma_wordlist.txt ~/.RedForge/wordlists/passwords/

# Utiliser une wordlist personnalisée
redforge -t example.com --bruteforce --wordlist ~/.RedForge/wordlists/custom/mots.txt
```

---

## Dépannage

### Erreurs courantes v2.0

#### 1. Mode furtif : TOR non trouvé

```bash
# Solution
sudo apt install tor
sudo systemctl enable tor
sudo systemctl start tor

# Vérifier
tor --version
systemctl status tor
```

#### 2. Mode furtif : Proxies non fonctionnels

```bash
# Tester un proxy
redforge --test-proxy socks5://127.0.0.1:9050

# Formater correctement les proxies
# HTTP: http://user:pass@host:port
# SOCKS4: socks4://host:port
# SOCKS5: socks5://host:port
```

#### 3. Multi-attaque : Timeout

```bash
# Augmenter le timeout
export MULTI_ATTACK_TIMEOUT=900

# Ou dans la configuration
"multi_attack": {"timeout": 900}
```

#### 4. Opération APT : Permission denied

```bash
# Vérifier les permissions
ls -la ~/.RedForge/apt_operations/

# Corriger
chmod 755 ~/.RedForge/apt_operations/
chown -R $USER:$USER ~/.RedForge/
```

#### 5. WebSocket déconnecté

```bash
# Vérifier le serveur
systemctl status redforge

# Redémarrer
sudo systemctl restart redforge

# Vérifier les ports
netstat -tlnp | grep 5000
netstat -tlnp | grep 5001
```

### Logs v2.0

Les logs sont stockés dans `~/.RedForge/logs/`

```bash
# Log principal
tail -f ~/.RedForge/logs/redforge.log

# Log mode furtif
tail -f ~/.RedForge/logs/stealth.log

# Log multi-attaques
tail -f ~/.RedForge/logs/multi_attack.log

# Log opérations APT
tail -f ~/.RedForge/logs/apt.log

# Logs JSON analysables
cat ~/.RedForge/logs/redforge_*.json | jq '.'

# Logs avec filtre
grep "ERROR" ~/.RedForge/logs/redforge.log
grep "stealth" ~/.RedForge/logs/redforge.log
```

### Debug mode v2.0

```bash
# Mode debug complet
export REDFORGE_DEBUG=true
redforge -t example.com --stealth high

# Debug spécifique au mode furtif
export STEALTH_DEBUG=true
redforge -t example.com --stealth high

# Debug multi-attaques
export MULTI_ATTACK_DEBUG=true
redforge --multi config.json

# Debug opérations APT
export APT_DEBUG=true
redforge --apt recon_to_exfil -t example.com
```

### Diagnostic v2.0

```bash
# Vérification complète
redforge --check-all

# Tester le mode furtif
redforge --test-stealth --target example.com

# Tester les multi-attaques
redforge --test-multi --config examples/multi_config.json

# Tester les opérations APT
redforge --test-apt --operation recon_to_exfil --target example.com

# Benchmark des performances
redforge --benchmark --mode all
```

---

## FAQ

### Général

**Q: RedForge v2.0 est-il gratuit ?**  
R: Oui, RedForge est open source sous licence GPLv3.

**Q: Quelles sont les principales nouveautés de la v2.0 ?**  
R: Multi-attaques, mode furtif avancé (TOR, proxies), opérations APT complètes.

**Q: Quels systèmes d'exploitation sont supportés ?**  
R: Kali Linux et Parrot OS sont officiellement supportés.

**Q: Puis-je utiliser RedForge sur Windows ?**  
R: Non, RedForge est optimisé pour Linux. Une version Windows est à l'étude.

### Mode furtif

**Q: TOR est-il obligatoire pour le mode furtif ?**  
R: Non, TOR est optionnel mais recommandé pour les niveaux High et Paranoid.

**Q: Comment configurer mes propres proxies ?**  
R: Créez un fichier avec un proxy par ligne : `socks5://127.0.0.1:9050`

**Q: Le mode furtif ralentit-il les attaques ?**  
R: Oui, volontairement. Le niveau Paranoid peut être jusqu'à 10x plus lent.

### Multi-attaques

**Q: Quelle est la différence entre séquentiel et parallèle ?**  
R: Séquentiel = discret mais lent. Parallèle = rapide mais détectable.

**Q: Puis-je mélanger les deux modes ?**  
R: Oui, avec le mode "mixed" vous pouvez grouper les attaques.

**Q: Combien d'attaques maximum ?**  
R: Théoriquement illimité, mais 10-20 recommandé pour des raisons de performance.

### Opérations APT

**Q: Les opérations APT sont-elles réversibles ?**  
R: Oui, le mode cleanup est activé par défaut pour nettoyer les traces.

**Q: Puis-je créer mes propres opérations ?**  
R: Oui, via des fichiers JSON personnalisés.

**Q: Combien de temps dure une opération APT ?**  
R: De 15 minutes à plusieurs heures selon la complexité.

### Techniques

**Q: RedForge est-il détectable ?**  
R: Les attaques standards peuvent être détectées. Le mode furtif réduit la détection.

**Q: Comment améliorer les performances ?**  
R: Utilisez le mode parallèle, augmentez les threads, réduisez le mode furtif.

**Q: Puis-je ajouter mes propres outils ?**  
R: Oui, via le système de plugins ou les connecteurs personnalisés.

---

## Sécurité et éthique

### Avertissement légal

RedForge est un outil professionnel pour les tests d'intrusion autorisés. L'utilisation sans autorisation explicite est **ILLÉGALE** et peut entraîner des poursuites judiciaires.

### Bonnes pratiques

1. **Obtenez une autorisation écrite** avant tout test
2. **Définissez un périmètre** clair avec le client
3. **Documentez toutes les actions** effectuées
4. **Ne causez pas de dommages** aux systèmes testés
5. **Ne conservez pas les données** après la mission
6. **Utilisez le mode furtif** uniquement sur autorisation
7. **Signalez les vulnérabilités** de manière responsable

### Responsabilités

L'utilisateur est seul responsable de l'usage de RedForge. Les développeurs ne peuvent être tenus responsables des dommages causés par une utilisation inappropriée.

### Recommandations

- Utilisez RedForge uniquement sur vos propres systèmes
- Ou avec une autorisation explicite du propriétaire
- Respectez les lois en vigueur dans votre pays
- Signalez les vulnérabilités de manière responsable
- Ne partagez pas les résultats sensibles

---

## Support

### Obtenir de l'aide

```bash
# Aide générale
redforge --help

# Aide spécifique
redforge --aide-commande footprint
redforge --aide-commande stealth
redforge --aide-commande multi
redforge --aide-commande apt

# Liste des modules
redforge --liste-modules

# Liste des plugins
redforge --plugin list
```

### Liens utiles

- **GitHub** : https://github.com/Elfried002/RedForge
- **Issues** : https://github.com/Elfried002/RedForge/issues

### Contact

- **Email support** : support@redforge.io
- **Email sécurité** : security@redforge.io
- **Email commercial** : sales@redforge.io

---

## Conclusion

RedForge v2.0 est un outil puissant pour les tests d'intrusion web modernes. Avec ses nouvelles fonctionnalités (multi-attaques, mode furtif, opérations APT), il permet aux équipes Red Team d'être plus efficaces et plus discrètes dans leurs missions.

N'oubliez pas : **avec de grands pouvoirs viennent de grandes responsabilités**. Utilisez RedForge de manière éthique et légale.

---

<div align="center">

*Documentation utilisateur - Version 2.0.0*

**🔴 RedForge - Forgez vos attaques, maîtrisez vos cibles**

*Dernière mise à jour : 9 Avril 2025*

</div>
```

## Résumé des mises à jour pour la v2.0.0

### Nouvelles sections ajoutées

| Section | Contenu |
|---------|---------|
| **Multi-Attaques** | Configuration, modes (séquentiel/parallèle), lancement, surveillance |
| **Mode Furtif** | Niveaux, configuration avancée, commandes, métriques |
| **Opérations APT** | Opérations prédéfinies, configuration personnalisée, surveillance, nettoyage |
