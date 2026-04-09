```markdown
<div align="center">
  
# 🔴 RedForge v2.0

## Plateforme d'Orchestration de Pentest Web pour Red Team

[![Version](https://img.shields.io/badge/version-2.0.0-red.svg)](https://github.com/Elfried002/RedForge/releases)
[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![Kali](https://img.shields.io/badge/Kali-Linux-purple.svg)](https://www.kali.org/)
[![Parrot](https://img.shields.io/badge/Parrot-OS-blue.svg)](https://www.parrotsec.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Code style](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)
[![Multi-Attacks](https://img.shields.io/badge/Multi-Attacks-supported-green.svg)](#multi-attaques)
[![Stealth Mode](https://img.shields.io/badge/Stealth-Mode-available-purple.svg)](#mode-furtif)
[![APT](https://img.shields.io/badge/APT-Operations-ready-red.svg)](#opérations-apt)

*"Forgez vos attaques, maîtrisez vos cibles - Version 2.0 avec Multi-Attacks, Mode Furtif et Opérations APT"*

</div>

---

## 📖 Table des matières

- [🎯 Présentation](#-présentation)
- [✨ Nouveautés v2.0](#-nouveautés-v20)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Multi-Attaques](#-multi-attaques)
- [Mode Furtif](#-mode-furtif)
- [Opérations APT](#-opérations-apt)
- [Interface CLI](#interface-cli)
- [Interface graphique](#interface-graphique)
- [Types d'attaques](#types-dattaques)
- [Outils intégrés](#outils-intégrés)
- [Configuration](#configuration)
- [Génération de rapports](#génération-de-rapports)
- [Plugins](#plugins)
- [Docker](#docker)
- [API REST](#api-rest)
- [FAQ](#faq)
- [Contribution](#contribution)
- [Licence](#licence)
- [Avertissement légal](#avertissement-légal)
- [Contact](#contact)

---

## 🎯 Présentation

**RedForge v2.0** est une plateforme d'orchestration de pentest web spécialement conçue pour les équipes **Red Team**. Cette version majeure introduit des fonctionnalités avancées pour les tests d'intrusion professionnels.

### Philosophie

| Concept | Description |
|---------|-------------|
| **Orchestration** | Coordonne les outils existants plutôt que de les remplacer |
| **Modularité** | Architecture extensible avec système de plugins |
| **Accessibilité** | Interface moderne pour améliorer l'expérience utilisateur |
| **Efficacité** | Automatisation des chaînes d'exploitation |
| **Discrétion** | Mode furtif avancé pour éviter la détection |
| **100% Français** | Interface et documentation entièrement en français |

### Pourquoi RedForge v2.0 ?

- ✅ **Multi-Attaques** - Lancez plusieurs attaques simultanément ou séquentiellement
- ✅ **Mode Furtif** - Délais aléatoires, TOR, proxies, user-agents dynamiques
- ✅ **Opérations APT** - Persistance, mouvement latéral, exfiltration
- ✅ **Ne réinvente pas la roue** - Utilise les meilleurs outils existants
- ✅ **Interface moderne** - CLI puissante + GUI élégante
- ✅ **Chaînage intelligent** - Enchaînement automatique d'attaques complexes
- ✅ **Multi-outils** - Orchestration de 20+ outils spécialisés
- ✅ **Rapports professionnels** - HTML, PDF, JSON, CSV avec graphiques
- ✅ **Extensible** - Système de plugins personnalisables

---

## ✨ Nouveautés v2.0

### 📚 Multi-Attaques

| Mode | Description | Utilisation |
|------|-------------|-------------|
| **Séquentiel** | Attaques exécutées une par une | Idéal pour éviter la détection |
| **Parallèle** | Attaques exécutées simultanément | Rapide mais plus détectable |
| **Mixte** | Combinaison des deux modes | Équilibre performance/discrétion |

```bash
# Exemple de configuration multi-attaque
{
    "name": "Scan complet",
    "target": "example.com",
    "attacks": [
        {"category": "injection", "type": "sql"},
        {"category": "cross_site", "type": "xss"},
        {"category": "authentication", "type": "bruteforce"}
    ],
    "mode": "sequential",
    "stealth_level": "high"
}
```

### 🕵️ Mode Furtif

| Niveau | Délai | Détection | Utilisation |
|--------|-------|-----------|-------------|
| **Low** | 0.5s | Facile | Tests rapides |
| **Medium** | 1.5s | Moyenne | Usage standard |
| **High** | 3.0s | Difficile | Opérations sensibles |
| **Paranoid** | 5.0s | Très difficile | Maximum de discrétion |

**Techniques de furtivité** :
- Jitter (variation aléatoire des délais)
- User-Agents aléatoires (100+ agents)
- Rotation de proxies (HTTP/SOCKS)
- Routage TOR (anonymisation)
- Mimétisme humain (patterns naturels)
- Slow Loris (requêtes lentes)

### 🎭 Opérations APT

| Phase | Description | Techniques |
|-------|-------------|------------|
| **Reconnaissance** | Collecte d'informations | OSINT, scanning, énumération |
| **Initial Access** | Premier accès | Exploitation, phishing, supply chain |
| **Persistence** | Maintien de l'accès | Backdoors, scheduled tasks, registry |
| **Privilege Escalation** | Élévation de privilèges | Exploits locaux, abus de configuration |
| **Lateral Movement** | Déplacement réseau | Pass-the-hash, PSExec, WMI, SSH |
| **Data Exfiltration** | Extraction de données | DNS tunneling, HTTPS, custom protocol |

```bash
# Lancer une opération APT complète
redforge --apt recon_to_exfil -t example.com --stealth paranoid

# Opération personnalisée
redforge --apt custom -c apt_config.json -t example.com
```

---

## Fonctionnalités

### 🔴 Par catégorie

<details>
<summary><b>Injections</b> (7 types)</summary>

- SQL Injection (Error, Union, Boolean, Time, Out-of-band)
- NoSQL Injection (MongoDB, CouchDB)
- Command Injection
- LDAP Injection
- XPath Injection
- HTML Injection
- Template Injection (SSTI)
</details>

<details>
<summary><b>Sessions</b> (5 types)</summary>

- Session Hijacking
- Session Fixation
- Cookie Manipulation
- JWT Attacks (alg none, brute force, kid injection)
- OAuth Attacks
</details>

<details>
<summary><b>Cross-Site</b> (5 types)</summary>

- XSS (Reflected, Stored, DOM-based)
- CSRF
- Clickjacking
- CORS Misconfiguration
- PostMessage Attacks
</details>

<details>
<summary><b>Authentification</b> (6 types)</summary>

- Brute Force
- Credential Stuffing
- Password Spraying
- MFA Bypass
- Privilege Escalation
- Race Condition
</details>

<details>
<summary><b>Système de fichiers</b> (6 types)</summary>

- LFI/RFI
- File Upload (avec bypass)
- Directory Traversal
- Buffer Overflow
- Path Normalization
- Zip Slip
</details>

<details>
<summary><b>Infrastructure</b> (5 types)</summary>

- WAF Bypass
- Misconfiguration Detection
- Load Balancer Attack
- Host Header Injection
- Cache Poisoning
</details>

<details>
<summary><b>Intégrité</b> (5 types)</summary>

- Data Tampering
- Information Leakage
- MITM Attacks
- Parameter Pollution
- Business Logic Flaws
</details>

<details>
<summary><b>Avancées</b> (7 types)</summary>

- API Attacks (REST, SOAP)
- GraphQL Attacks
- WebSocket Attacks
- Deserialization
- Browser Exploitation
- Microservices Attacks
- Attack Chaining
</details>

### 🛠️ Interface

| Interface | Caractéristiques |
|-----------|------------------|
| **CLI** | 100% française, aide contextuelle, mode interactif, couleurs |
| **GUI** | Dashboard temps réel, WebSocket, graphiques, terminal intégré |
| **API REST** | Endpoints complets, authentification par token, rate limiting |

### 📊 Rapports

| Format | Utilisation |
|--------|-------------|
| **HTML** | Navigation interactive, graphiques |
| **PDF** | Documents professionnels |
| **JSON** | Intégration API, traitement automatisé |
| **CSV** | Analyse Excel, tableaux de bord |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            RedForge v2.0 Platform                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    CLI      │  │    GUI      │  │    API      │  │  WebSocket  │        │
│  │  (Rich)     │  │  (Flask)    │  │  (REST)     │  │  (Socket.IO)│        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│         └────────────────┼────────────────┼────────────────┘               │
│                          ▼                ▼                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Orchestrateur Central v2.0                     │   │
│  │         (Attack Chaining, Multi-Attacks, Stealth Mode, APT)         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                       │
│         ┌──────────┬───────────────┼───────────────┬──────────┬──────────┐ │
│         ▼          ▼               ▼               ▼          ▼          ▼ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐
│  │ Attaques │ │Connectors│ │  Phases  │ │  Utils   │ │ Stealth  │ │    APT     │
│  │ (8 cats) │ │(20 tools)│ │  (4)     │ │(12 mods) │ │  Module  │ │ Operations │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────────┘
│         │          │               │               │          │          │    │
│         └──────────┴───────────────┴───────────────┴──────────┴──────────┘    │
│                                    │                                         │
│                              ┌─────▼─────┐                                   │
│                              │  Tools    │                                   │
│                              │(Nmap, MSF,│                                   │
│                              │ SQLMap...)│                                   │
│                              └───────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Structure du projet

```
RedForge/
├── bin/                        # Exécutables
│   └── RedForge               # Point d'entrée principal
├── src/
│   ├── core/                  # Cœur de l'application
│   │   ├── cli.py            # Interface CLI
│   │   ├── orchestrator.py   # Moteur d'orchestration
│   │   ├── attack_chainer.py # Chaînage d'attaques
│   │   ├── stealth_manager.py # Mode furtif
│   │   ├── apt_manager.py     # Opérations APT
│   │   └── session_manager.py # Gestion des sessions
│   ├── attacks/               # 8 catégories d'attaques
│   ├── connectors/            # 20 connecteurs d'outils
│   ├── stealth/               # Module furtif
│   │   ├── tor_manager.py    # Gestion TOR
│   │   ├── proxy_rotator.py  # Rotation proxies
│   │   ├── user_agent.py     # User-Agents aléatoires
│   │   └── delay_jitter.py   # Délais variables
│   ├── multi_attack/          # Multi-attaques
│   │   ├── sequential.py     # Mode séquentiel
│   │   ├── parallel.py       # Mode parallèle
│   │   └── queue_manager.py  # Gestion des files
│   ├── apt/                   # Opérations APT
│   │   ├── phases/           # Phases APT
│   │   ├── persistence/      # Mécanismes de persistance
│   │   ├── lateral_movement/ # Mouvement latéral
│   │   └── exfiltration/     # Exfiltration de données
│   ├── web_interface/         # Interface web (Flask)
│   │   ├── templates/        # Templates HTML
│   │   ├── static/           # CSS, JS, images
│   │   └── app.py            # Application Flask
│   └── i18n/                 # Internationalisation (fr_FR)
├── config/                    # Configuration
├── data/                      # Wordlists et signatures
├── docs/                      # Documentation
├── tests/                     # Tests unitaires
├── plugins/                   # Système de plugins
└── requirements.txt           # Dépendances Python
```

---

## 🚀 Installation

### Prérequis

| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| **OS** | Kali Linux 2024.1 / Parrot OS 6.0 | Kali Linux 2024.1+ |
| **RAM** | 4 GB | 8 GB+ |
| **CPU** | 2 cœurs | 4 cœurs+ |
| **Stockage** | 10 GB | 20 GB+ |
| **Python** | 3.11 | 3.11+ |
| **TOR** | Optionnel | Pour mode furtif |

### Installation rapide

```bash
# Cloner le dépôt
git clone https://github.com/Elfried002/RedForge.git
cd RedForge

# Lancer l'installation (nécessite sudo)
sudo ./install.sh

# Vérifier l'installation
redforge --version
```

### Installation manuelle

```bash
# Installer les dépendances système
sudo apt update
sudo apt install -y python3 python3-pip nmap metasploit-framework sqlmap hydra whatweb dirb tor

# Installer les dépendances Python
pip3 install -r requirements.txt

# Créer les répertoires
mkdir -p ~/.RedForge/{logs,reports,workspace,stealth,multi_attack,apt_operations}

# Installer l'exécutable
sudo cp bin/RedForge /usr/local/bin/
sudo chmod +x /usr/local/bin/redforge
```

### Installation Docker

```bash
# Construire l'image
docker build -t redforge:latest .

# Démarrer avec docker-compose
docker-compose up -d

# Accéder à l'interface
# http://localhost:5000
```

### Vérification

```bash
# Vérifier la version
redforge --version

# Vérifier les dépendances
redforge --check-deps

# Tester un scan rapide
redforge -t example.com -p footprint
```

---

## 🎮 Démarrage rapide

### Premier scan

```bash
# Scan de reconnaissance (le moins intrusif)
redforge -t https://example.com -p footprint

# Scan complet avec rapport
redforge -t https://example.com -p all -o rapport.html

# Interface graphique (recommandé pour débuter)
sudo redforge -g
```

### Exemples d'utilisation

```bash
# Multi-attaque séquentielle
redforge --multi config.json -t example.com --mode sequential

# Mode furtif niveau élevé
redforge -t example.com --stealth high

# Opération APT complète
redforge --apt recon_to_exfil -t example.com --stealth paranoid

# Scan XSS spécifique
redforge -t example.com -p scan --xss

# Scan SQLi avec SQLMap
redforge -t example.com -p scan --sqlmap

# Force brute formulaire login
redforge -t example.com -p exploit --bruteforce --username admin --wordlist passwords.txt

# Scanner plusieurs cibles
redforge -f cibles.txt -p footprint -o resultats.json

# Mode interactif
redforge -i
```

---

## 📚 Multi-Attaques

### Configuration

Créez un fichier JSON de configuration pour vos multi-attaques :

```json
{
    "name": "Audit complet",
    "target": "example.com",
    "description": "Scan complet de l'application web",
    "attacks": [
        {
            "category": "injection",
            "type": "sql",
            "options": {"level": 3}
        },
        {
            "category": "cross_site",
            "type": "xss",
            "options": {"payloads": "all"}
        },
        {
            "category": "authentication",
            "type": "bruteforce",
            "options": {"users": ["admin"], "wordlist": "common_passwords.txt"}
        },
        {
            "category": "file_system",
            "type": "lfi_rfi",
            "options": {"depth": 5}
        }
    ],
    "mode": "sequential",
    "stealth_level": "high",
    "delay_between_attacks": 2,
    "stop_on_error": false,
    "output": "rapport_multi.json"
}
```

### Lancement

```bash
# Mode séquentiel (recommandé pour la discrétion)
redforge --multi config.json --mode sequential

# Mode parallèle (plus rapide mais plus détectable)
redforge --multi config.json --mode parallel --max-parallel 5

# Avec niveau furtif spécifique
redforge --multi config.json --stealth paranoid

# Avec rapport personnalisé
redforge --multi config.json -o rapport_multi.html
```

### Résultats

Les résultats des multi-attaques sont disponibles :
- En temps réel via l'interface web
- Dans les logs (`~/.RedForge/logs/`)
- Sous forme de rapport consolidé
- Via l'API REST

---

## 🕵️ Mode Furtif

### Configuration

```json
{
    "stealth": {
        "enabled": true,
        "level": "high",
        "random_user_agents": true,
        "use_tor": true,
        "rotate_proxies": true,
        "proxy_list": [
            "socks5://127.0.0.1:9050",
            "http://proxy1:8080",
            "socks4://proxy2:1080"
        ],
        "mimic_human": true,
        "random_delays": true,
        "min_delay": 1.0,
        "max_delay": 5.0,
        "jitter": 0.3,
        "slow_loris": false
    }
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

# Mode paranoïaque (max discrétion)
redforge -t example.com --stealth paranoid
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
- Score de furtivité (0-100%)
- Niveau de risque de détection
- Nombre d'alertes évitées
- Délai moyen entre requêtes
- Utilisation TOR/proxies

---

## 🎭 Opérations APT

### Opérations prédéfinies

| Opération | Description | Phases |
|-----------|-------------|--------|
| **recon_to_exfil** | Cycle complet APT | Recon → Accès → Persistance → Élévation → Mouvement → Exfiltration |
| **web_app_compromise** | Compromission web | Footprinting → Scan vulns → Exploitation → Post-exploitation |
| **lateral_movement** | Mouvement latéral | Découverte → Credential dumping → Propagation |
| **persistence** | Persistance avancée | Backdoors → Scheduled tasks → Registry |

### Configuration personnalisée

```json
{
    "name": "Opération personnalisée",
    "description": "Ciblage spécifique",
    "phases": [
        {
            "name": "Reconnaissance",
            "attacks": ["port_scan", "service_enum", "directory_bruteforce"],
            "options": {"stealth": true}
        },
        {
            "name": "Initial Access",
            "attacks": ["sql_injection", "file_upload"],
            "options": {"payloads": "custom"}
        },
        {
            "name": "Persistence",
            "attacks": ["backdoor", "scheduled_task"],
            "options": {"method": "registry"}
        },
        {
            "name": "Lateral Movement",
            "attacks": ["ssh_pivot", "wmi_exec"],
            "options": {"targets": ["192.168.1.0/24"]}
        },
        {
            "name": "Data Exfiltration",
            "attacks": ["dns_exfil"],
            "options": {"server": "c2.example.com"}
        }
    ],
    "persistence": {
        "type": "registry",
        "location": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "key": "WindowsUpdate"
    },
    "evasion": {
        "disable_logging": true,
        "clear_events": true,
        "use_living_off_land": true
    },
    "exfiltration": {
        "method": "dns_tunneling",
        "server": "c2.example.com",
        "chunk_size": 512,
        "encryption": "aes-256-gcm"
    },
    "cleanup": true,
    "reporting": {
        "include_iocs": true,
        "include_ttps": true,
        "include_mitre_attack": true
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
```

### Timeline et monitoring

L'interface web affiche en temps réel :
- Progression des phases
- Succès/échec par étape
- Durée d'exécution
- Alertes de détection
- IOC générés

---

## 💻 Interface CLI

### Syntaxe

```bash
redforge [OPTIONS] [ARGUMENTS]
```

### Options principales

| Option | Description | Exemple |
|--------|-------------|---------|
| `-t, --target` | Cible à analyser | `redforge -t example.com` |
| `-f, --file` | Fichier de cibles | `redforge -f cibles.txt` |
| `-p, --phase` | Phase à exécuter | `redforge -t example.com -p scan` |
| `-g, --gui` | Interface graphique | `sudo redforge -g` |
| `-i, --interactive` | Mode interactif | `redforge -i` |
| `-o, --output` | Fichier de rapport | `redforge -t example.com -o rapport.pdf` |
| `--multi` | Fichier config multi-attaque | `redforge --multi config.json` |
| `--stealth` | Activer mode furtif | `redforge --stealth high` |
| `--apt` | Opération APT | `redforge --apt recon_to_exfil` |
| `--tor` | Utiliser TOR | `redforge --tor` |
| `--proxy-list` | Fichier de proxies | `redforge --proxy-list proxies.txt` |
| `--ports` | Ports à scanner | `--ports 80,443,8080` |
| `--threads` | Nombre de threads | `--threads 20` |
| `--level` | Niveau d'agressivité | `--level 3` |
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

### Mode interactif

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

## 🖥️ Interface graphique

### Lancement

```bash
sudo redforge -g
# ou
redforge --gui
```

Puis ouvrez votre navigateur sur `http://localhost:5000`

### Structure

#### 📊 Tableau de bord
- Statistiques en temps réel
- Graphiques des vulnérabilités
- Activités récentes
- Sessions actives
- Multi-attaques en cours
- Opérations APT en cours
- Métriques furtives

#### 🎯 Attaques
- **Attaques simples** : Sélection par catégorie
- **Multi-attaques** : Configuration avancée, modes séquentiel/parallèle
- **Opérations APT** : Prédéfinies et personnalisées
- **Mode furtif** : Configuration complète

#### 📄 Rapports
- Génération multi-format
- Templates personnalisables
- Rapports multi-attaques
- Rapports opérations APT
- Métriques furtives

#### ⚙️ Paramètres
- Configuration générale
- Mode furtif (niveaux, TOR, proxies)
- Multi-attaques (threads, délais)
- Opérations APT (persistance, exfiltration)
- Gestion des outils
- Wordlists personnalisées

#### ❓ Aide
- Documentation intégrée
- Tutoriels interactifs
- FAQ
- Support

---

## 🎯 Types d'attaques

### Injections (7 types)

| Attaque | Description | Sévérité |
|---------|-------------|----------|
| **SQL Injection** | Injection de requêtes SQL | CRITICAL |
| **NoSQL Injection** | Injection sur bases NoSQL | HIGH |
| **Command Injection** | Exécution de commandes système | CRITICAL |
| **LDAP Injection** | Manipulation de requêtes LDAP | HIGH |
| **XPath Injection** | Manipulation de requêtes XPath | HIGH |
| **HTML Injection** | Injection de code HTML | MEDIUM |
| **Template Injection** | Injection dans moteurs de templates | CRITICAL |

### Sessions (5 types)

| Attaque | Description | Sévérité |
|---------|-------------|----------|
| **Session Hijacking** | Détournement de session | CRITICAL |
| **Session Fixation** | Fixation d'ID de session | HIGH |
| **Cookie Manipulation** | Altération de cookies | HIGH |
| **JWT Attacks** | Attaques sur tokens JWT | HIGH |
| **OAuth Attacks** | Attaques sur OAuth | HIGH |

### Cross-Site (5 types)

| Attaque | Description | Sévérité |
|---------|-------------|----------|
| **XSS (Reflected)** | Script reflété | HIGH |
| **XSS (Stored)** | Script stocké | HIGH |
| **XSS (DOM)** | Script DOM | HIGH |
| **CSRF** | Falsification de requête | HIGH |
| **Clickjacking** | Détournement de clic | MEDIUM |
| **CORS** | Mauvaise configuration CORS | HIGH |

### Authentification (6 types)

| Attaque | Description | Sévérité |
|---------|-------------|----------|
| **Brute Force** | Force brute | MEDIUM |
| **Credential Stuffing** | Réutilisation de credentials | HIGH |
| **Password Spraying** | Pulvérisation de mots de passe | MEDIUM |
| **MFA Bypass** | Contournement 2FA | HIGH |
| **Privilege Escalation** | Élévation de privilèges | CRITICAL |
| **Race Condition** | Condition de concurrence | MEDIUM |

### Système de fichiers (6 types)

| Attaque | Description | Sévérité |
|---------|-------------|----------|
| **LFI/RFI** | Inclusion de fichiers | HIGH |
| **File Upload** | Téléversement malveillant | CRITICAL |
| **Directory Traversal** | Traversal de répertoires | HIGH |
| **Buffer Overflow** | Dépassement de tampon | CRITICAL |
| **Path Normalization** | Normalisation de chemin | MEDIUM |
| **Zip Slip** | Extraction ZIP malveillante | HIGH |

### Infrastructure (5 types)

| Attaque | Description | Sévérité |
|---------|-------------|----------|
| **WAF Bypass** | Contournement de WAF | HIGH |
| **Misconfiguration** | Mauvaises configurations | MEDIUM |
| **Load Balancer** | Attaques sur load balancer | MEDIUM |
| **Host Header** | Injection Host Header | HIGH |
| **Cache Poisoning** | Empoisonnement de cache | HIGH |

### Intégrité (5 types)

| Attaque | Description | Sévérité |
|---------|-------------|----------|
| **Data Tampering** | Altération de données | HIGH |
| **Info Leakage** | Fuites d'informations | HIGH |
| **MITM** | Homme du milieu | HIGH |
| **Parameter Pollution** | Pollution de paramètres | MEDIUM |
| **Business Logic** | Failles métier | HIGH |

### Avancées (7 types)

| Attaque | Description | Sévérité |
|---------|-------------|----------|
| **API** | Attaques sur API | HIGH |
| **GraphQL** | Attaques GraphQL | HIGH |
| **WebSocket** | Attaques WebSocket | MEDIUM |
| **Deserialization** | Désérialisation | CRITICAL |
| **Browser Exploit** | Exploitation navigateur | HIGH |
| **Microservices** | Attaques microservices | HIGH |
| **Attack Chaining** | Chaînage d'attaques | VARIES |

---

## 🛠️ Outils intégrés

### Connecteurs disponibles

| Outil | Version minimale | Description |
|-------|-----------------|-------------|
| **Nmap** | 7.0+ | Scan réseau et ports |
| **Metasploit** | 6.0+ | Framework d'exploitation |
| **SQLMap** | 1.6+ | Injection SQL |
| **Hydra** | 9.0+ | Force brute |
| **WhatWeb** | 0.5+ | Détection de technologies |
| **Dirb** | 2.22+ | Force brute de répertoires |
| **Gobuster** | 3.0+ | Force brute de répertoires/DNS |
| **ffuf** | 1.5+ | Fuzzing web |
| **wafw00f** | 2.1+ | Détection WAF |
| **XSStrike** | 3.1+ | Détection XSS avancée |
| **Dalfox** | 2.8+ | Scan XSS rapide |
| **jwt_tool** | 2.0+ | Attaques JWT |
| **Nikto** | 2.5+ | Scanner web |
| **WPScan** | 3.8+ | Scanner WordPress |
| **Nuclei** | 3.0+ | Scanner template-based |
| **TOR** | 0.4+ | Anonymisation |
| **Proxychains** | 4.0+ | Rotation proxies |
| **John** | 1.9+ | Cracking mots de passe |
| **Hashcat** | 6.0+ | Cracking avancé |
| **Burp Suite** | 2023+ | Proxy d'analyse (optionnel) |

### Wordlists intégrées

| Wordlist | Source | Taille |
|----------|--------|--------|
| rockyou.txt | RockYou | 14M+ entrées |
| common_passwords.txt | SecLists | 1M+ entrées |
| common_usernames.txt | SecLists | 10k+ entrées |
| common_directories.txt | SecLists | 10k+ entrées |
| common_subdomains.txt | SecLists | 5k+ entrées |
| common_parameters.txt | SecLists | 2k+ entrées |
| xss_payloads.txt | Personnalisée | 1000+ payloads |
| sql_payloads.txt | Personnalisée | 500+ payloads |
| lfi_payloads.txt | Personnalisée | 200+ payloads |
| ssrf_payloads.txt | Personnalisée | 100+ payloads |

---

## ⚙️ Configuration

### Fichier de configuration

`~/.RedForge/config.json`

```json
{
    "version": "2.0.0",
    "language": "fr_FR",
    "theme": "dark",
    "timeout": 300,
    "threads": 10,
    "workspace": "/home/user/.RedForge/workspace",
    "logs": "/home/user/.RedForge/logs",
    "reports": "/home/user/.RedForge/reports",
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
        "persistence_dir": "/home/user/.RedForge/persistence",
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
        "stealth_alert": true,
        "email": "",
        "webhook": ""
    },
    "network": {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "verify_ssl": false,
        "proxy": {
            "enabled": false,
            "http": "",
            "https": "",
            "socks5": ""
        }
    },
    "scanning": {
        "default_level": 2,
        "concurrent_scans": 3,
        "ports": "1-1000"
    },
    "reports": {
        "default_format": "html",
        "default_template": "standard",
        "auto_generate": true,
        "include_charts": true,
        "include_recommendations": true,
        "include_evidence": true
    }
}
```

### Variables d'environnement

```bash
# Configuration
export REDFORGE_HOME=~/.RedForge
export REDFORGE_LOG_LEVEL=INFO
export REDFORGE_LANGUAGE=fr_FR
export REDFORGE_ENV=production

# Mode furtif
export STEALTH_TOR_ENABLED=false
export STEALTH_DEFAULT_LEVEL=medium
export STEALTH_PROXY_LIST=/path/to/proxies.txt

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

### Profils

Plusieurs profils sont fournis :

- **Red Team** (`config/profiles/red_team.json`) : Profil standard pour opérations Red Team
- **Stealth** (`config/profiles/stealth.json`) : Optimisé pour la discrétion
- **Aggressive** (`config/profiles/aggressive.json`) : Maximise la vitesse
- **APT** (`config/profiles/apt.json`) : Configuré pour opérations APT

```bash
# Charger un profil
redforge --profile red_team

# Créer un profil personnalisé
redforge --create-profile mon_profil

# Lister les profils disponibles
redforge --list-profiles
```

---

## 📄 Génération de rapports

### Formats supportés

| Format | Commande | Utilisation |
|--------|----------|-------------|
| HTML | `-o rapport.html` | Navigation interactive |
| PDF | `-o rapport.pdf` | Documents professionnels |
| JSON | `-o rapport.json` | Intégration API |
| CSV | `-o rapport.csv` | Analyse Excel |

### Templates

| Template | Description |
|----------|-------------|
| **Standard** | Rapport complet avec toutes les sections |
| **Direction** | Version simplifiée pour la direction |
| **Technique** | Détails techniques approfondis |
| **APT** | Spécifique aux opérations APT |
| **Stealth** | Métriques de discrétion |
| **Multi-Attack** | Détails des multi-attaques |

### Exemples

```bash
# Rapport HTML standard
redforge -t example.com -p all -o rapport.html

# Rapport PDF pour la direction
redforge -t example.com -p all -o rapport.pdf --template executive

# Rapport JSON pour traitement automatisé
redforge -t example.com -p all -o rapport.json

# Rapport avec métriques furtives
redforge -t example.com --stealth high -o rapport_stealth.html

# Rapport multi-attaque
redforge --multi config.json -o rapport_multi.html

# Rapport opération APT
redforge --apt recon_to_exfil -t example.com -o rapport_apt.pdf
```

### Structure du rapport HTML

```
📊 Résumé exécutif
├── Score de sécurité
├── Vulnérabilités par sévérité
└── Métriques clés

🎯 Détails des vulnérabilités
├── Critiques (avec preuves)
├── Élevées
├── Moyennes
└── Faibles

🛠️ Méthodologie
├── Outils utilisés
├── Configuration
└── Chronologie

📈 Graphiques
├── Évolution temporelle
├── Distribution par type
└── Sévérité

💡 Recommandations
├── Correctifs prioritaires
├── Bonnes pratiques
└── Mesures de sécurité

📎 Annexes
├── Logs
├── Payloads
└── Preuves techniques
```

---

## 🔌 Plugins

### Types de plugins

| Type | Description |
|------|-------------|
| **Attack** | Nouveau type d'attaque |
| **Scanner** | Nouveau scanner |
| **Connector** | Nouveau connecteur d'outil |
| **Report** | Nouveau générateur de rapport |
| **Hook** | Hook d'événement |
| **Stealth** | Technique de furtivité |
| **APT** | Phase d'opération APT |

### Création d'un plugin

```python
from src.plugins.plugin_manager import AttackPlugin

class MyCustomAttack(AttackPlugin):
    """Plugin d'attaque personnalisé"""
    
    def get_info(self):
        return {
            "name": "MyCustomAttack",
            "version": "1.0.0",
            "author": "Your Name",
            "description": "Description de l'attaque"
        }
    
    def get_attack_type(self):
        return "custom_injection"
    
    def get_severity(self):
        return "HIGH"
    
    def scan(self, target, **kwargs):
        """Phase de scan"""
        # Logique de détection
        vulnerabilities = []
        
        # Analyse de la cible
        if self.check_vulnerability(target):
            vulnerabilities.append({
                "type": "custom_vuln",
                "severity": "HIGH",
                "details": "Détails de la vulnérabilité",
                "proof": "Preuve de concept"
            })
        
        return {"vulnerabilities": vulnerabilities}
    
    def exploit(self, target, **kwargs):
        """Phase d'exploitation"""
        # Logique d'exploitation
        result = self.execute_exploit(target)
        
        return {
            "success": result,
            "output": "Résultat de l'exploitation"
        }
    
    def check_vulnerability(self, target):
        """Vérification personnalisée"""
        # Implémentation
        return True
    
    def execute_exploit(self, target):
        """Exécution de l'exploit"""
        # Implémentation
        return True
```

### Installation d'un plugin

```bash
# Copier le plugin
cp mon_plugin.py /opt/RedForge/plugins/

# Activer le plugin
redforge --plugin enable mon_plugin

# Désactiver le plugin
redforge --plugin disable mon_plugin

# Lister les plugins
redforge --plugin list

# Installer depuis un dépôt
redforge --plugin install https://github.com/user/redforge-plugin.git
```

---

## 🐳 Docker

### Build

```bash
# Construire l'image
docker build -t redforge:latest .

# Build avec docker-compose
docker-compose build

# Build avec arguments
docker build \
  --build-arg REDFORGE_VERSION=2.0.0 \
  --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  -t redforge:latest .
```

### Exécution

```bash
# Démarrer les services
docker-compose up -d

# Démarrer avec profiling spécifique
docker-compose --profile stealth up -d  # Avec TOR
docker-compose --profile monitoring up -d  # Avec Prometheus/Grafana
docker-compose --profile full up -d  # Tous les services

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### Accès

- Interface web : `http://localhost:5000`
- WebSocket : `ws://localhost:5001`
- Metasploit RPC : `localhost:55553`
- Callback XSS : `localhost:8080`
- C2 Server (APT) : `localhost:4443`
- DNS Exfiltration : `localhost:5353/udp`
- Grafana (monitoring) : `http://localhost:3000` (admin/admin)
- Prometheus : `http://localhost:9090`

---

## 🔌 API REST

### Authentification

```bash
# Générer un token
redforge --api generate-token

# Utiliser le token
export REDFORGE_API_TOKEN="votre_token"
```

### Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/targets` | Lister les cibles |
| `POST` | `/api/targets` | Ajouter une cible |
| `DELETE` | `/api/targets` | Supprimer une cible |
| `POST` | `/api/scan` | Lancer un scan |
| `GET` | `/api/results/{target}` | Obtenir les résultats |
| `POST` | `/api/multi-attack` | Lancer multi-attaque |
| `POST` | `/api/apt/execute` | Exécuter opération APT |
| `POST` | `/api/stealth/config` | Configurer mode furtif |
| `GET` | `/api/stealth/status` | Statut mode furtif |
| `POST` | `/api/report/generate` | Générer rapport |
| `GET` | `/api/health` | Health check |

### Exemples

```bash
# Lancer un scan
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $REDFORGE_API_TOKEN" \
  -d '{"target":"example.com","phase":"all"}'

# Multi-attaque
curl -X POST http://localhost:5000/api/multi-attack \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $REDFORGE_API_TOKEN" \
  -d '{
    "target": "example.com",
    "attacks": [
      {"category": "injection", "type": "sql"},
      {"category": "cross_site", "type": "xss"}
    ],
    "execution_mode": "sequential",
    "stealth_level": "high"
  }'

# Opération APT
curl -X POST http://localhost:5000/api/apt/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $REDFORGE_API_TOKEN" \
  -d '{
    "target": "example.com",
    "operation_id": "recon_to_exfil",
    "stealth_level": "paranoid"
  }'
```

---

## ❓ FAQ

<details>
<summary><b>RedForge v2.0 est-il gratuit ?</b></summary>

Oui, RedForge est totalement gratuit et open source sous licence GPLv3.
</details>

<details>
<summary><b>Quelles sont les principales nouveautés de la v2.0 ?</b></summary>

- Multi-attaques (séquentielles et parallèles)
- Mode furtif avancé (TOR, proxies, user-agents aléatoires)
- Opérations APT complètes (persistance, mouvement latéral, exfiltration)
- Interface web modernisée
- Rapports enrichis avec graphiques
- API REST complète
- WebSocket pour temps réel
</details>

<details>
<summary><b>Comment activer le mode furtif ?</b></summary>

```bash
# Via CLI
redforge -t example.com --stealth high

# Via interface web
# Onglet "Mode Furtif" -> Activer -> Choisir niveau

# Raccourci clavier
Ctrl+Shift+S
```
</details>

<details>
<summary><b>TOR est-il requis pour le mode furtif ?</b></summary>

Non, TOR est optionnel. Le mode furtif fonctionne sans, mais l'utilisation de TOR augmente considérablement la discrétion.
</details>

<details>
<summary><b>Comment créer une opération APT personnalisée ?</b></summary>

Créez un fichier JSON avec vos phases et attaques, puis :
```bash
redforge --apt custom -c ma_config.json -t example.com
```
</details>

<details>
<summary><b>Les multi-attaques sont-elles plus lentes ?</b></summary>

Le mode séquentiel est plus lent mais plus discret. Le mode parallèle est plus rapide mais plus détectable. À vous de choisir selon vos besoins.
</details>

<details>
<summary><b>RedForge est-il compatible avec Windows ?</b></summary>

Non, RedForge est optimisé pour Kali Linux et Parrot OS. Une version Windows est à l'étude.
</details>

<details>
<summary><b>Comment signaler une vulnérabilité ?</b></summary>

Envoyez un email à `security@redforge.io` avec les détails. Voir [SECURITY.md](SECURITY.md) pour plus d'informations.
</details>

---

## 🤝 Contribution

Les contributions sont les bienvenues !

### Comment contribuer

1. **Fork** le projet
2. **Créez votre branche** (`git checkout -b feature/amazing-feature`)
3. **Committez vos changements** (`git commit -m 'Add amazing feature'`)
4. **Pushez vers la branche** (`git push origin feature/amazing-feature`)
5. **Ouvrez une Pull Request**

### Types de contributions

- 🐛 **Signalement de bugs**
- 💡 **Suggestions de fonctionnalités**
- 📝 **Documentation**
- 🔧 **Code**
- 🌐 **Traductions**
- 🔒 **Rapports de sécurité**

### Développement

```bash
# Cloner le dépôt
git clone https://github.com/Elfried002/RedForge.git
cd RedForge

# Installer les dépendances de développement
pip install -r requirements-dev.txt

# Exécuter les tests
make test
make test-cov

# Vérifier le style
make lint

# Formater le code
make format

# Type checking
make type-check

# Pre-commit hooks
make pre-commit
```

### Guidelines

- Suivez PEP 8 pour le code Python
- Documentez les nouvelles fonctionnalités
- Ajoutez des tests pour les nouvelles fonctionnalités
- Mettez à jour la documentation si nécessaire
- Respectez les conventions de nommage existantes
- Commentez le code complexe

---

## 📝 Licence

Ce projet est sous licence **GNU General Public License v3.0**.

```
RedForge - Plateforme d'Orchestration de Pentest Web pour Red Team
Copyright (C) 2024-2025 RedForge Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## ⚠️ Avertissement légal

**RedForge est un outil professionnel pour les tests d'intrusion autorisés.**

L'utilisation sans autorisation explicite est **ILLÉGALE** et peut entraîner des poursuites judiciaires.

### Utilisation autorisée

✅ **Tests autorisés** :
- Sur vos propres systèmes (propriété ou bail)
- Avec autorisation écrite du propriétaire
- Dans le cadre d'un contrat de pentest
- Pour la recherche académique en cybersécurité
- Dans des environnements de formation contrôlés

### Utilisation interdite

❌ **Actions illégales** :
- Tests sans autorisation
- Accès non autorisé à des systèmes tiers
- Vol, modification ou destruction de données
- Perturbation de services (DoS/DDoS)
- Espionnage industriel ou commercial
- Activités criminelles ou malveillantes

**L'utilisateur est seul responsable de l'usage de cet outil.**

---

## 📞 Contact

### Liens utiles

- **GitHub** : https://github.com/Elfried002/RedForge
- **Issues** : https://github.com/Elfried002/RedForge/issues
- **Email** : elfriedyobouet@gmail.com

### Statistiques

[![GitHub stars](https://img.shields.io/github/stars/Elfried002/RedForge)](https://github.com/Elfried002/RedForge/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Elfried002/RedForge)](https://github.com/Elfried002/RedForge/network)
[![GitHub issues](https://img.shields.io/github/issues/Elfried002/RedForge)](https://github.com/Elfried002/RedForge/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/Elfried002/RedForge)](https://github.com/Elfried002/RedForge/pulls)
[![Downloads](https://img.shields.io/github/downloads/Elfried002/RedForge/total)](https://github.com/Elfried002/RedForge/releases)

---

<div align="center">

**🔴 RedForge v2.0 - Forgez vos attaques, maîtrisez vos cibles**

*"L'orchestration au service de la Red Team - Multi-Attacks, Mode Furtif, Opérations APT"*

Made with ❤️ by the RedForge Team

**Dernière mise à jour : 9 Avril 2025**

</div>
```