# RedForge v2.0

## Plateforme de Pentest Web pour Red Team

[![Version](https://img.shields.io/badge/version-2.0.0-red.svg)](https://github.com/Elfried002/RedForge/releases)
[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![Kali](https://img.shields.io/badge/Kali-Linux-purple.svg)](https://www.kali.org/)
[![Parrot](https://img.shields.io/badge/Parrot-OS-blue.svg)](https://www.parrotsec.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

*"Forgez vos attaques, maîtrisez vos cibles"*

</div>

---

## 📋 Table des matières

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Multi-Attaques](#multi-attaques)
- [Mode Furtif](#mode-furtif)
- [Opérations APT](#opérations-apt)
- [Dépannage](#dépannage)
- [Documentation](#documentation)
- [Licence](#licence)

---

## 🎯 Présentation

**RedForge v2.0** est un outil de pentest web spécialement conçue pour les équipes **Red Team**. Cette version majeure introduit des fonctionnalités avancées pour les tests d'intrusion professionnels.

### Philosophie

| Concept | Description |
|---------|-------------|
| **Orchestration** | Coordonne les outils existants plutôt que de les remplacer |
| **Modularité** | Architecture extensible avec système de plugins |
| **Accessibilité** | Interface moderne pour améliorer l'expérience utilisateur |
| **Discrétion** | Mode furtif avancé pour éviter la détection |
| **100% Français** | Interface et documentation entièrement en français |

---

## ✨ Fonctionnalités v2.0

### 📚 Multi-Attaques
- **Séquentiel** - Attaques une par une (discret)
- **Parallèle** - Attaques simultanées (rapide)
- **Mixte** - Combinaison des deux modes

### 🕵️ Mode Furtif
- 4 niveaux : Low, Medium, High, Paranoid
- User-Agents aléatoires
- Rotation de proxies (HTTP/SOCKS)
- Routage TOR intégré
- Mimétisme du comportement humain

### 🎭 Opérations APT
- 6 phases complètes
- Persistance avancée
- Mouvement latéral
- Exfiltration de données
- Nettoyage automatique

### 🌐 Interface Web
- Dashboard temps réel
- Graphiques interactifs
- WebSocket pour mises à jour live
- Mode sombre/clair
- Interface responsive

### 📊 Rapports
- HTML, PDF, JSON, CSV
- Templates personnalisables
- Graphiques inclus
- Métriques furtives

---

## 📋 Prérequis

| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| **OS** | Kali Linux 2024.1+ / Parrot OS 6.0+ | Kali Linux 2024.1+ |
| **RAM** | 4 GB | 8 GB+ |
| **CPU** | 2 cœurs | 4 cœurs+ |
| **Stockage** | 10 GB | 20 GB+ |
| **Python** | 3.11 | 3.11+ |
| **TOR** | Optionnel | Pour mode furtif |

### Outils requis (installés automatiquement)
- Nmap, SQLMap, Hydra, Metasploit
- Gobuster, FFUF, Wfuzz
- XSStrike, Dalfox, wafw00f
- WhatWeb, Dirb

---

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/Elfried002/RedForge.git
cd RedForge
```

### 2. Rendre les scripts exécutables

```bash
chmod +x scripts/*.sh
chmod +x install.sh uninstall.sh update.sh
```

### 3. Télécharger les wordlists (fichiers volumineux exclus du dépôt)

```bash
./scripts/download_wordlists.sh
```

> **Note :** Les wordlists sont exclues du dépôt GitHub car elles dépassent la limite de taille (100 MB). Le script les télécharge automatiquement depuis les sources officielles.

### 4. Installer RedForge

#### Option A : Installation automatique (recommandée)

```bash
sudo ./install.sh
```

#### Option B : Installation manuelle

```bash
# Créer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Installer Playwright (optionnel)
playwright install chromium
```

#### Option C : Installation Docker

```bash
docker-compose up -d
# Interface disponible sur http://localhost:5000
```

### 5. Vérifier l'installation

```bash
redforge --version
# Devrait afficher: RedForge v2.0.0
```
## 🎮 Démarrage rapide

### Lancer l'interface graphique (recommandé)

```bash
sudo redforge -g
# OU
redforge --gui
```

Puis ouvrez votre navigateur sur `http://localhost:5000`

### Lancer un scan simple

```bash
# Scan de reconnaissance
redforge -t https://example.com -p footprint

# Scan complet avec rapport
redforge -t https://example.com -p all -o rapport.html
```

### Lancer une multi-attaque

```bash
redforge --multi config.json -t example.com --mode sequential
```

### Activer le mode furtif

```bash
redforge -t example.com --stealth high

# Avec TOR
redforge -t example.com --stealth high --tor
```

### Lancer une opération APT

```bash
redforge --apt recon_to_exfil -t example.com --stealth paranoid
```
## 📚 Multi-Attaques

### Configuration

Créez un fichier `multi_config.json` :

```json
{
    "name": "Audit complet",
    "target": "https://example.com",
    "attacks": [
        {"category": "injection", "type": "sql"},
        {"category": "cross_site", "type": "xss"},
        {"category": "authentication", "type": "bruteforce"}
    ],
    "execution_mode": "sequential",
    "stealth_level": "high"
}
```

### Lancement

```bash
redforge --multi multi_config.json
```
## 🕵️ Mode Furtif

### Niveaux disponibles

| Niveau | Délai | TOR | Proxies | Risque détection |
|--------|-------|-----|---------|------------------|
| **Low** | 0.5s | ❌ | ❌ | Élevé |
| **Medium** | 1.5s | ❌ | ❌ | Moyen |
| **High** | 3.0s | ✅ | ❌ | Faible |
| **Paranoid** | 5.0s | ✅ | ✅ | Très faible |

### Configuration avancée

```bash
# Avec TOR
redforge -t example.com --stealth high --tor

# Avec rotation de proxies
redforge -t example.com --stealth high --proxy-list proxies.txt

# Configuration complète
redforge -t example.com --stealth paranoid --tor --proxy-list proxies.txt
```
## 🎭 Opérations APT

### Opérations prédéfinies

| Opération | Description | Phases |
|-----------|-------------|--------|
| `recon_to_exfil` | Cycle complet APT | 6 phases |
| `web_app_compromise` | Compromission web | 4 phases |
| `lateral_movement` | Mouvement latéral | 3 phases |
| `persistence` | Persistance avancée | 2 phases |

### Lancement

```bash
# Opération prédéfinie
redforge --apt recon_to_exfil -t example.com

# Opération personnalisée
redforge --apt custom -c apt_config.json -t example.com

# Avec mode furtif
redforge --apt recon_to_exfil -t example.com --stealth paranoid
```

## 🔧 Dépannage

### Erreurs courantes

#### 1. `permission non accordée`

```bash
chmod +x scripts/*.sh install.sh uninstall.sh update.sh
```

#### 2. `command not found`

```bash
# Ajouter au PATH
export PATH="$PATH:$HOME/.local/bin"
# OU réinstaller
pip install --user -r requirements.txt
```

#### 3. `Module not found`

```bash
# Activer l'environnement virtuel
source .venv/bin/activate
# OU réinstaller
pip install -r requirements.txt --force-reinstall
```

#### 4. `Metasploit non trouvé`

```bash
sudo apt install metasploit-framework
```

#### 5. `TOR non trouvé` (mode furtif)

```bash
sudo apt install tor
sudo systemctl enable tor
sudo systemctl start tor
```

### Logs

```bash
# Voir les logs
tail -f ~/.RedForge/logs/redforge.log

# Logs spécifiques
tail -f ~/.RedForge/logs/stealth.log
tail -f ~/.RedForge/logs/apt.log
```


## 🐳 Docker

```bash
# Démarrer avec docker-compose
docker-compose up -d

# Démarrer avec monitoring
docker-compose --profile monitoring up -d

# Arrêter
docker-compose down

# Accéder à l'interface
# http://localhost:5000
```

## 📖 Documentation

- [Guide utilisateur](docs/user_guide.md)
- [API Reference](docs/api_reference.md)
- [Guide technique](docs/technical_guide.md)
- [Contribuer](CONTRIBUTING.md)
- [Sécurité](SECURITY.md)

## 🤝 Contribution

Les contributions sont les bienvenues !

```bash
# Fork le projet
# Puis
git clone https://github.com/Elfried002/RedForge.git
cd RedForge
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## 📝 Licence

Ce projet est sous licence **GNU General Public License v3.0**.


## ⚠️ Avertissement légal

**RedForge est un outil professionnel pour les tests d'intrusion autorisés.**

- ✅ **Autorisé** : Tests sur vos propres systèmes
- ✅ **Autorisé** : Tests avec autorisation écrite
- ❌ **Interdit** : Tests sans autorisation
- ❌ **Interdit** : Utilisation malveillante

**L'utilisateur est seul responsable de l'usage de cet outil.**

## 📞 Support

- **Documentation** : https://docs.redforge.io
- **Issues** : https://github.com/Elfried002/RedForge/issues
- **Email** : elfriedyobouet@gmail.com

---

<div align="center">

**🔴 RedForge - Forgez vos attaques, maîtrisez vos cibles**

*"L'orchestration au service de la Red Team"*

</div>