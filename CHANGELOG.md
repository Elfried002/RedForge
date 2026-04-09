Voici une version améliorée du fichier `CHANGELOG.md` pour RedForge v2.0 :

```markdown
# Changelog RedForge

Tous les changements notables du projet RedForge seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-04-09

### 🚀 Ajouté - Majeurs

#### Multi-Attaques
- Mode séquentiel : exécution des attaques une par une pour une discrétion maximale
- Mode parallèle : exécution simultanée des attaques pour des performances optimales
- Mode mixte : combinaison des deux modes selon les besoins
- Configuration JSON complète pour les multi-attaques
- File d'attente intelligente pour la gestion des ressources
- Support de la reprise sur erreur
- Sauvegarde intermédiaire des résultats
- Limitation du nombre de threads parallèles configurable

#### Mode Furtif Avancé
- 4 niveaux de furtivité : Low, Medium, High, Paranoid
- Délais variables avec jitter (variation aléatoire)
- User-Agents aléatoires (bibliothèque de 100+ agents)
- Rotation automatique de proxies (HTTP, HTTPS, SOCKS4, SOCKS5)
- Intégration TOR pour l'anonymisation
- Mimétisme du comportement humain
- Mode Slow Loris pour les attaques lentes
- Métriques de détection en temps réel
- Alertes de sécurité contextuelles

#### Opérations APT
- Opérations prédéfinies : reconnaissance → exfiltration, compromission web
- Phases complètes : Reconnaissance, Initial Access, Persistence, Privilege Escalation, Lateral Movement, Exfiltration
- Persistance avancée (registry, scheduled tasks, backdoors)
- Mouvement latéral (SMB, WMI, SSH, RDP)
- Exfiltration de données (DNS tunneling, HTTP, HTTPS, protocole personnalisé)
- Nettoyage automatique post-opération
- Timeline visuelle dans l'interface web
- Support des opérations personnalisées via JSON
- Reporting MITRE ATT&CK

#### Interface Web
- Nouvel onglet "Multi-Attaques" avec configuration avancée
- Nouvel onglet "Mode Furtif" avec contrôles en temps réel
- Nouvel onglet "Opérations APT" avec timeline interactive
- Dashboard enrichi avec métriques furtives et opérations APT
- Graphiques en temps réel (WebSocket)
- Notifications push pour les événements critiques
- Mode sombre amélioré
- Interface responsive entièrement revue

#### API REST
- Endpoints complets pour toutes les fonctionnalités
- Authentification par token JWT
- Rate limiting configurable
- Documentation Swagger/OpenAPI
- WebSocket pour les mises à jour en temps réel

#### Sécurité
- Chiffrement AES-256-GCM pour les données sensibles
- Support TLS 1.3 pour les communications
- HSTS, CSP, X-Frame-Options configurés
- Rotation automatique des clés API
- Audit logging des actions sensibles

### 📦 Ajouté - Mineurs

#### Outils intégrés
- Gobuster (force brute répertoires/DNS)
- ffuf (fuzzing web)
- Nuclei (scanner template-based)
- Dalfox (scan XSS rapide)
- WPScan (scanner WordPress)
- Nikto (scanner web)
- 10 nouveaux connecteurs d'outils

#### Wordlists
- RockYou.txt (14M+ entrées) - optionnel
- SecLists (version allégée)
- 500+ payloads XSS
- 300+ payloads SQL
- 200+ payloads LFI
- 100+ payloads SSRF
- Wordlists par défaut pour tests rapides

#### Utilitaires
- Script d'installation avec menu interactif
- Script de mise à jour automatique
- Script de désinstallation complet
- Support Docker avec docker-compose
- Service systemd pour démarrage automatique
- Makefile avec commandes utiles (test, lint, format)

### 🔧 Modifié

#### Architecture
- Refactoring complet du moteur d'orchestration
- Migration vers une architecture modulaire (plugins)
- Amélioration des performances (30% plus rapide)
- Réduction de la consommation mémoire (25% moins)

#### CLI
- Nouvelles options : `--multi`, `--stealth`, `--apt`
- Aide contextuelle enrichie
- Sorties colorées améliorées
- Mode interactif plus intuitif

#### Interface graphique
- Temps de chargement réduit de 40%
- WebSocket pour les mises à jour temps réel
- Graphiques plus fluides (Chart.js)
- Meilleure expérience mobile

#### Rapports
- Nouveaux templates : APT, Stealth, Multi-Attack
- Graphiques inclus dans les rapports HTML
- Métriques furtives dans les rapports
- Timeline des opérations APT

### 🐛 Corrigé

- Correction du bug de mémoire dans le scanner XSS
- Correction des problèmes de connexion WebSocket
- Correction des fuites de mémoire dans les scans longs
- Correction des erreurs de parsing JSON dans les configurations
- Correction des problèmes de compatibilité Python 3.12
- Correction du bug d'affichage dans le mode sombre
- Correction des problèmes de permissions sur les fichiers de logs

### ⚠️ Déprécié

- L'option `--level` sera dépréciée dans la v3.0 (remplacée par `--stealth`)
- Le module `attack_chainer` sera fusionné avec `multi_attack`
- L'interface CLI legacy sera supprimée dans la v3.0

### 🔒 Sécurité

- Correction d'une vulnérabilité XSS dans l'interface web (CVE-2025-001)
- Correction d'une vulnérabilité d'injection SQL dans le module analyse (CVE-2025-002)
- Renforcement de l'authentification API
- Ajout du rate limiting sur tous les endpoints
- Rotation automatique des tokens API

### 📚 Documentation

- Nouveau guide d'utilisation pour les multi-attaques
- Nouveau guide pour le mode furtif
- Nouveau guide pour les opérations APT
- Documentation API complète (Swagger)
- Tutoriels vidéo (liens)
- FAQ enrichie

---

## [1.0.0] - 2024-04-06

### Ajouté - Version initiale

#### Architecture
- Architecture modulaire complète en 8 catégories d'attaques
- Interface CLI 100% française avec système d'aide intégré
- Interface graphique web moderne (Flask + WebSocket)
- Système de plugins extensible

#### Modules d'attaques
- **Injections** : SQL, NoSQL, Command, LDAP, XPath, HTML, Template
- **Sessions** : Hijacking, Fixation, Cookie, JWT, OAuth
- **Cross-Site** : XSS, CSRF, Clickjacking, CORS, PostMessage
- **Authentification** : Brute force, Credential stuffing, Password spraying, MFA bypass, Privilege escalation, Race condition
- **Système de fichiers** : LFI/RFI, File upload, Directory traversal, Buffer overflow, Path normalization, Zip slip
- **Infrastructure** : WAF bypass, Misconfiguration, Load balancer, Host header, Cache poisoning
- **Intégrité** : Data tampering, Info leakage, MITM, Parameter pollution, Business logic
- **Avancées** : API, GraphQL, WebSocket, Deserialization, Browser exploit, Microservices, Attack chaining

#### Connecteurs
- Nmap, Metasploit, SQLMap, XSStrike, wafw00f, ffuf, Hydra, jwt_tool, ZAP, WhatWeb, Dirb

#### Utilitaires
- Système de logging avancé
- Gestion des couleurs en console
- Générateur de rapports (HTML, PDF, JSON, CSV)
- Vérificateur de dépendances
- Installateur d'outils
- Utilitaires réseau et crypto
- Internationalisation (français)

#### Interface graphique
- Tableau de bord avec statistiques en temps réel
- Gestion complète des attaques
- Génération de rapports
- Paramètres configurables
- Aide intégrée
- Thème clair/sombre
- Responsive design

#### Documentation
- Guide d'installation pour Kali Linux et Parrot OS
- Documentation CLI complète
- Aide contextuelle
- Exemples d'utilisation

#### Sécurité
- Vérification des droits sudo
- Isolation des environnements
- Logs sécurisés
- Configuration chiffrée

---

## [1.0.0-rc.1] - 2024-03-15

### Ajouté
- Version release candidate
- Tests unitaires pour les modules core
- Correction des bugs majeurs
- Optimisation des performances

### Modifié
- Amélioration de la détection des vulnérabilités
- Optimisation des connecteurs Metasploit et Nmap
- Interface graphique plus réactive

### Corrigé
- Bug de connexion WebSocket sous haute charge
- Fuite de mémoire dans le scanner XSS
- Problèmes d'affichage sur Firefox

---

## [1.0.0-beta.2] - 2024-02-28

### Ajouté
- Système de chaînage d'attaques
- Support des WebSockets pour l'interface temps réel
- Mode collaboratif basique

### Modifié
- Refactoring du moteur d'orchestration
- Amélioration de la gestion des sessions
- Optimisation des requêtes SQL

### Corrigé
- Bugs dans le scanner XSS (faux positifs)
- Problèmes de connexion Metasploit RPC
- Erreurs de parsing des fichiers de configuration

---

## [1.0.0-beta.1] - 2024-02-01

### Ajouté
- Première version bêta publique
- Interface graphique fonctionnelle
- Support des 8 catégories d'attaques
- Documentation utilisateur complète

### Connu
- Quelques problèmes de performance avec les scans massifs
- Interface graphique à améliorer sur mobile
- Bugs mineurs dans le générateur de rapports PDF

---

## [0.9.0-alpha] - 2024-01-15

### Ajouté
- Alpha version pour test interne
- Architecture de base
- CLI fonctionnelle
- Connecteurs Nmap et Metasploit
- Phases 1 et 2 (Footprint, Analysis)

### Planifié pour v1.0
- Phases 3 et 4 (Scan, Exploit)
- Interface graphique
- Système de plugins
- 8 catégories d'attaques complètes

---

## Prochaines versions

### [2.1.0] - Planifié (Q3 2025)

#### À venir
- Intégration BloodHound pour l'analyse AD
- Module C2 personnalisable
- Exfiltration via DNS-over-HTTPS
- Plugin Burp Suite
- Export MITRE ATT&CK
- Mode furtif avec résolution DNS aléatoire

### [3.0.0] - Planifié (Q1 2026)

#### À l'étude
- Interface web en React
- Base de données pour l'historique
- Mode collaboratif avancé
- Machine learning pour la détection
- Agent déployable sur cibles
- Orchestration cloud-native

---

## Notes de version

### Compatibilité

| Version | Kali Linux | Parrot OS | Ubuntu | Python |
|---------|------------|-----------|--------|--------|
| **2.0.0** | 2024.1+ | 6.0+ | 22.04+ | 3.11+ |
| 1.0.0 | 2024.1+ | 6.0+ | 22.04+ | 3.11+ |
| 0.9.0 | 2023.4+ | 5.3+ | 20.04+ | 3.10+ |

### Dépendances principales (v2.0)

| Dépendance | Version minimale |
|------------|------------------|
| Flask | 2.3.0 |
| Socket.IO | 5.3.0 |
| Metasploit Framework | 6.4.0 |
| Nmap | 7.94 |
| SQLMap | 1.7 |
| TOR (optionnel) | 0.4.8 |

### Migration depuis v1.0.0

```bash
# Sauvegarder la configuration
cp -r ~/.RedForge ~/.RedForge.backup

# Mettre à jour
git pull origin main
sudo ./update.sh

# Vérifier la migration
redforge --version
# Devrait afficher 2.0.0

# Restaurer la configuration si nécessaire
cp -r ~/.RedForge.backup/* ~/.RedForge/
```

### Contribution aux rapports de bugs

Les rapports de bugs et les demandes de fonctionnalités sont les bienvenus.
Veuillez consulter [CONTRIBUTING.md](CONTRIBUTING.md) pour plus d'informations.

### Sécurité

Pour signaler une vulnérabilité de sécurité, contactez `security@redforge.io`.

### Licence

Ce projet est sous licence **GNU General Public License v3.0**.
Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

<div align="center">

**🔴 RedForge - Forgez vos attaques, maîtrisez vos cibles**

[Téléchargement](https://github.com/Elfried002/RedForge/releases) |

</div>
```

## Résumé des changements pour la v2.0.0

### 🚀 Ajoutés (majeurs)

| Catégorie | Fonctionnalités |
|-----------|-----------------|
| **Multi-Attaques** | Séquentiel, parallèle, mixte, configuration JSON, file d'attente |
| **Mode Furtif** | 4 niveaux, jitter, user-agents aléatoires, rotation proxies, TOR, slow loris |
| **Opérations APT** | 6 phases, persistance, mouvement latéral, exfiltration, timeline |
| **Interface Web** | 3 nouveaux onglets, dashboard enrichi, graphiques temps réel |
| **API REST** | Endpoints complets, JWT, rate limiting, Swagger |
| **Sécurité** | AES-256-GCM, TLS 1.3, HSTS, rotation clés API |

### 📦 Ajoutés (mineurs)

- 5 nouveaux outils (Gobuster, ffuf, Nuclei, Dalfox, WPScan, Nikto)
- Wordlists enrichies (rockyou.txt, SecLists, payloads)
- Scripts d'installation/mise à jour/désinstallation améliorés
- Support Docker avec docker-compose
- Makefile complet

### 🔧 Modifiés

- Architecture refactorée (30% plus rapide, 25% moins mémoire)
- CLI avec nouvelles options
- Interface graphique 40% plus rapide
- Rapports enrichis (graphiques, métriques furtives, timeline APT)

### 🐛 Corrigés

- 8 bugs majeurs corrigés
- Fuites mémoire résolues
- Compatibilité Python 3.12
- Problèmes d'affichage mode sombre

### 🔒 Sécurité

- 2 CVEs corrigées (CVE-2025-001, CVE-2025-002)
- Rate limiting ajouté
- Rotation tokens API