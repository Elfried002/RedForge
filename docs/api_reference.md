# API Reference - RedForge v2.0

## Table des matières

1. [Introduction](#introduction)
2. [Authentification](#authentification)
3. [Endpoints API](#endpoints-api)
   - [Cibles](#cibles)
   - [Scans](#scans)
   - [Attaques](#attaques)
   - [Multi-Attaques](#multi-attaques)
   - [Mode Furtif](#mode-furtif)
   - [Opérations APT](#opérations-apt)
   - [Résultats](#résultats)
   - [Sessions](#sessions)
   - [Rapports](#rapports)
   - [Configuration](#configuration)
4. [WebSocket](#websocket)
5. [Codes d'erreur](#codes-derreur)
6. [Rate Limiting](#rate-limiting)
7. [Exemples](#exemples)

---

## Introduction

L'API REST de RedForge v2.0 permet d'interagir programmatiquement avec la plateforme. Toutes les réponses sont au format JSON et utilisent les codes HTTP standards.

### Base URL

```
http://localhost:5000/api
```

### Version

```
/api/v2/
```

### Headers communs

```http
Content-Type: application/json
X-API-Key: votre_token_api
Authorization: Bearer <token>
```

---

## Authentification

### Obtenir un token API

```http
POST /api/auth/token
Content-Type: application/json
```

**Body :**
```json
{
    "username": "admin",
    "password": "mot_de_passe"
}
```

**Réponse :**
```json
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "token_type": "Bearer"
}
```

### Valider un token

```http
POST /api/auth/validate
Authorization: Bearer <token>
```

**Réponse :**
```json
{
    "success": true,
    "valid": true,
    "username": "admin",
    "expires_at": "2025-04-09T15:30:00Z"
}
```

### Rafraîchir un token

```http
POST /api/auth/refresh
Authorization: Bearer <token>
```

**Réponse :**
```json
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600
}
```

### Révoquer un token

```http
DELETE /api/auth/revoke
Authorization: Bearer <token>
```

**Réponse :**
```json
{
    "success": true,
    "message": "Token révoqué avec succès"
}
```

---

## Endpoints API

### Cibles

#### Liste des cibles

```http
GET /api/targets
```

**Paramètres :** Aucun

**Réponse :**
```json
{
    "targets": [
        "https://example.com",
        "https://test.com",
        "192.168.1.100"
    ],
    "count": 3,
    "total": 3
}
```

#### Ajouter une cible

```http
POST /api/targets
Content-Type: application/json
```

**Body :**
```json
{
    "target": "https://newexample.com",
    "tags": ["production", "web"],
    "description": "Site principal"
}
```

**Réponse :**
```json
{
    "success": true,
    "target": "https://newexample.com",
    "message": "Cible ajoutée avec succès",
    "id": "target_123"
}
```

#### Supprimer une cible

```http
DELETE /api/targets
Content-Type: application/json
```

**Body :**
```json
{
    "target": "https://example.com"
}
```

**Réponse :**
```json
{
    "success": true,
    "target": "https://example.com",
    "message": "Cible supprimée avec succès"
}
```

#### Détails d'une cible

```http
GET /api/targets/{target}
```

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| target | string | URL ou IP de la cible |

**Réponse :**
```json
{
    "target": "https://example.com",
    "status": "scanned",
    "last_scan": "2025-04-09T10:30:00Z",
    "vulnerabilities_count": 12,
    "open_ports": [80, 443, 8080],
    "technologies": [
        {"name": "nginx", "version": "1.18.0"},
        {"name": "php", "version": "7.4.33"},
        {"name": "mysql", "version": "5.7.44"}
    ],
    "tags": ["production", "web"],
    "notes": "Site critique"
}
```

---

### Scans

#### Lancer un scan

```http
POST /api/scan
Content-Type: application/json
```

**Body :**
```json
{
    "target": "https://example.com",
    "phase": "all",
    "stealth": true,
    "stealth_level": "high",
    "options": {
        "level": 3,
        "threads": 10,
        "timeout": 300,
        "ports": "80,443,8080"
    }
}
```

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| target | string | Cible à scanner |
| phase | string | Phase à exécuter (footprint, analysis, scan, exploit, all) |
| stealth | boolean | Activer mode furtif |
| stealth_level | string | low, medium, high, paranoid |
| options | object | Options supplémentaires |

**Réponse :**
```json
{
    "task_id": "scan_1234567890",
    "status": "started",
    "target": "https://example.com",
    "phase": "all",
    "estimated_duration": 120,
    "stealth_enabled": true,
    "stealth_level": "high"
}
```

#### Statut d'un scan

```http
GET /api/scan/{task_id}/status
```

**Réponse :**
```json
{
    "task_id": "scan_1234567890",
    "status": "running",
    "progress": 45,
    "current_phase": "scan",
    "current_attack": "SQL Injection",
    "message": "Scan XSS en cours...",
    "start_time": "2025-04-09T10:30:00Z",
    "estimated_remaining": 65,
    "stealth_score": 78
}
```

#### Arrêter un scan

```http
DELETE /api/scan/{task_id}
```

**Réponse :**
```json
{
    "success": true,
    "task_id": "scan_1234567890",
    "message": "Scan arrêté avec succès"
}
```

---

### Attaques

#### Lancer une attaque spécifique

```http
POST /api/attack
Content-Type: application/json
```

**Body :**
```json
{
    "target": "https://example.com",
    "category": "injection",
    "type": "sql",
    "stealth": true,
    "options": {
        "level": 3,
        "techniques": "BEUSTQ",
        "threads": 5,
        "timeout": 120
    }
}
```

**Catégories disponibles :**

| Category | Description | Types |
|----------|-------------|-------|
| injection | Injections | sql, nosql, command, ldap, xpath, html, template |
| session | Sessions | hijacking, fixation, cookie, jwt, oauth |
| cross_site | Cross-Site | xss, csrf, clickjacking, cors, postmessage |
| authentication | Authentification | bruteforce, credential_stuffing, password_spraying, mfa_bypass, priv_esc, race_condition |
| file_system | Système de fichiers | lfi_rfi, file_upload, dir_traversal, buffer_overflow, path_normalization, zip_slip |
| infrastructure | Infrastructure | waf_bypass, misconfig, load_balancer, host_header, cache_poisoning |
| integrity | Intégrité | data_tampering, info_leakage, mitm, param_pollution, business_logic |
| advanced | Avancées | api, graphql, websocket, deserialization, browser, microservices, chaining |

**Réponse :**
```json
{
    "success": true,
    "task_id": "attack_1234567890",
    "target": "https://example.com",
    "category": "injection",
    "type": "sql",
    "status": "started",
    "stealth_enabled": true
}
```

---

### Multi-Attaques

#### Lancer une multi-attaque

```http
POST /api/multi-attack
Content-Type: application/json
```

**Body :**
```json
{
    "name": "Audit complet",
    "target": "https://example.com",
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
            "options": {
                "users": ["admin"],
                "wordlist": "common_passwords.txt"
            }
        }
    ],
    "execution_mode": "sequential",
    "stealth_level": "high",
    "delay_between_attacks": 2,
    "stop_on_error": false,
    "timeout": 600
}
```

**Modes d'exécution :**

| Mode | Description |
|------|-------------|
| sequential | Exécution séquentielle (un par un) |
| parallel | Exécution parallèle (simultanée) |
| mixed | Mode mixte selon les priorités |

**Réponse :**
```json
{
    "success": true,
    "task_id": "multi_1234567890",
    "name": "Audit complet",
    "target": "https://example.com",
    "total_attacks": 3,
    "execution_mode": "sequential",
    "status": "started",
    "estimated_duration": 300
}
```

#### Statut d'une multi-attaque

```http
GET /api/multi-attack/{task_id}/status
```

**Réponse :**
```json
{
    "task_id": "multi_1234567890",
    "status": "running",
    "progress": 33,
    "current_attack": "SQL Injection",
    "completed_attacks": 1,
    "total_attacks": 3,
    "results": [
        {
            "attack": "SQL Injection",
            "status": "completed",
            "duration": 45,
            "vulnerabilities": 2
        },
        {
            "attack": "XSS",
            "status": "running",
            "duration": 12,
            "vulnerabilities": 0
        }
    ],
    "start_time": "2025-04-09T10:30:00Z",
    "estimated_remaining": 120
}
```

#### Arrêter une multi-attaque

```http
DELETE /api/multi-attack/{task_id}
```

**Réponse :**
```json
{
    "success": true,
    "task_id": "multi_1234567890",
    "message": "Multi-attaque arrêtée avec succès"
}
```

---

### Mode Furtif

#### Configurer le mode furtif

```http
POST /api/stealth/config
Content-Type: application/json
```

**Body :**
```json
{
    "enabled": true,
    "level": "high",
    "random_user_agents": true,
    "use_tor": true,
    "rotate_proxies": true,
    "proxy_list": [
        "socks5://127.0.0.1:9050",
        "http://proxy1:8080"
    ],
    "mimic_human": true,
    "random_delays": true,
    "min_delay": 1.0,
    "max_delay": 5.0,
    "jitter": 0.3,
    "slow_loris": false
}
```

**Niveaux de furtivité :**

| Niveau | Délai | Jitter | TOR | Proxies |
|--------|-------|--------|-----|---------|
| low | 0.5s | 10% | ❌ | ❌ |
| medium | 1.5s | 30% | ❌ | ❌ |
| high | 3.0s | 50% | ✅ | ❌ |
| paranoid | 5.0s | 70% | ✅ | ✅ |

**Réponse :**
```json
{
    "success": true,
    "message": "Configuration furtive appliquée",
    "config": {
        "enabled": true,
        "level": "high",
        "detection_risk": "low",
        "effectiveness": 85
    }
}
```

#### Obtenir le statut du mode furtif

```http
GET /api/stealth/status
```

**Réponse :**
```json
{
    "enabled": true,
    "level": "high",
    "detection_risk": "low",
    "effectiveness": 85,
    "tor_active": true,
    "proxy_rotation": true,
    "current_proxy": "socks5://127.0.0.1:9050",
    "avg_delay": 3.2,
    "alerts_avoided": 12,
    "start_time": "2025-04-09T10:30:00Z"
}
```

#### Tester la configuration furtive

```http
POST /api/stealth/test
Content-Type: application/json
```

**Body :**
```json
{
    "target": "https://example.com",
    "iterations": 10
}
```

**Réponse :**
```json
{
    "test_id": "stealth_test_123",
    "target": "https://example.com",
    "iterations": 10,
    "success_rate": 95,
    "detection_risk": "low",
    "avg_response_time": 3.2,
    "delays": [2.8, 3.1, 3.5, 2.9, 3.3],
    "recommendations": [
        "Augmenter le jitter à 50%",
        "Activer TOR pour plus de discrétion"
    ]
}
```

---

### Opérations APT

#### Lancer une opération APT

```http
POST /api/apt/execute
Content-Type: application/json
```

**Body :**
```json
{
    "target": "https://example.com",
    "operation_id": "recon_to_exfil",
    "stealth_level": "paranoid",
    "options": {
        "auto_cleanup": true,
        "log_all_phases": true,
        "phase_delay": 5,
        "persistence_dir": "/tmp/redforge_persistence",
        "exfil_method": "dns_tunneling",
        "exfil_server": "c2.example.com"
    }
}
```

**Opérations prédéfinies :**

| Operation ID | Description | Phases |
|--------------|-------------|--------|
| recon_to_exfil | Cycle complet APT | 6 phases |
| web_app_compromise | Compromission web | 4 phases |
| lateral_movement | Mouvement latéral | 3 phases |
| persistence | Persistance avancée | 2 phases |

**Réponse :**
```json
{
    "success": true,
    "task_id": "apt_1234567890",
    "operation_id": "recon_to_exfil",
    "target": "https://example.com",
    "total_phases": 6,
    "status": "started",
    "estimated_duration": 1800
}
```

#### Statut d'une opération APT

```http
GET /api/apt/{task_id}/status
```

**Réponse :**
```json
{
    "task_id": "apt_1234567890",
    "operation_id": "recon_to_exfil",
    "status": "running",
    "current_phase": "initial_access",
    "phase_progress": 60,
    "completed_phases": [
        {
            "name": "reconnaissance",
            "status": "completed",
            "duration": 120,
            "success_rate": 95,
            "findings": [
                "Open ports: 80,443",
                "Technologies: nginx, php"
            ]
        }
    ],
    "start_time": "2025-04-09T10:30:00Z",
    "estimated_remaining": 900
}
```

#### Créer une opération APT personnalisée

```http
POST /api/apt/custom
Content-Type: application/json
```

**Body :**
```json
{
    "name": "Mon opération personnalisée",
    "description": "Ciblage spécifique",
    "phases": [
        {
            "name": "Reconnaissance",
            "attacks": ["port_scan", "service_enum", "directory_bruteforce"],
            "options": {"stealth": true}
        },
        {
            "name": "Exploitation",
            "attacks": ["sql_injection", "file_upload"],
            "options": {"payloads": "custom"}
        }
    ],
    "cleanup": true,
    "persistence": {
        "type": "registry",
        "location": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    },
    "exfiltration": {
        "method": "https",
        "server": "c2.example.com",
        "chunk_size": 512
    }
}
```

**Réponse :**
```json
{
    "success": true,
    "operation_id": "custom_apt_123",
    "name": "Mon opération personnalisée",
    "message": "Opération APT créée avec succès"
}
```

#### Lister les opérations APT disponibles

```http
GET /api/apt/operations
```

**Réponse :**
```json
{
    "predefined": [
        "recon_to_exfil",
        "web_app_compromise",
        "lateral_movement",
        "persistence"
    ],
    "custom": [
        "Mon opération personnalisée",
        "Scan spécifique"
    ],
    "total": 6
}
```

---

### Résultats

#### Obtenir les résultats d'un scan

```http
GET /api/results/{target}
```

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| target | string | Cible cible |
| format | string | Format (json, html, csv) - optionnel |

**Réponse :**
```json
{
    "target": "https://example.com",
    "scan_date": "2025-04-09T10:30:00Z",
    "scan_duration": 120,
    "stealth_used": true,
    "stealth_level": "high",
    "summary": {
        "total_vulnerabilities": 12,
        "critical": 2,
        "high": 5,
        "medium": 3,
        "low": 2,
        "stealth_score": 85
    },
    "vulnerabilities": [
        {
            "id": "vuln_001",
            "type": "sql_injection",
            "severity": "CRITICAL",
            "cvss": 9.8,
            "parameter": "id",
            "details": "Injection SQL détectée sur le paramètre id",
            "evidence": "1' AND '1'='1",
            "recommendation": "Utiliser des requêtes paramétrées",
            "cwe": "CWE-89",
            "references": [
                "https://owasp.org/www-community/attacks/SQL_Injection"
            ]
        }
    ],
    "technologies": [
        {"name": "nginx", "version": "1.18.0"},
        {"name": "php", "version": "7.4.33"},
        {"name": "mysql", "version": "5.7.44"}
    ],
    "iocs": [
        "192.168.1.100",
        "malicious.exe"
    ]
}
```

#### Résumé global

```http
GET /api/results/summary
```

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| period | string | day, week, month, all |

**Réponse :**
```json
{
    "total_targets": 5,
    "total_vulnerabilities": 47,
    "total_scans": 12,
    "by_severity": {
        "critical": 8,
        "high": 15,
        "medium": 12,
        "low": 12
    },
    "by_type": {
        "sql_injection": 5,
        "xss": 12,
        "lfi": 3,
        "csrf": 4,
        "command_injection": 2,
        "others": 21
    },
    "by_target": {
        "https://example.com": 12,
        "https://test.com": 8,
        "192.168.1.100": 27
    },
    "stealth_stats": {
        "avg_stealth_score": 78,
        "total_alerts_avoided": 45
    }
}
```

#### Vulnérabilités récentes

```http
GET /api/vulnerabilities/recent
```

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| limit | integer | Nombre de résultats (défaut: 10) |
| severity | string | Filtrer par sévérité |
| type | string | Filtrer par type |

**Réponse :**
```json
{
    "vulnerabilities": [
        {
            "id": "vuln_001",
            "type": "sql_injection",
            "severity": "CRITICAL",
            "target": "https://example.com",
            "date": "2025-04-09T10:30:00Z",
            "parameter": "id",
            "status": "open"
        }
    ],
    "count": 10,
    "total": 47
}
```

---

### Sessions

#### Sessions actives

```http
GET /api/sessions
```

**Réponse :**
```json
{
    "sessions": [
        {
            "id": "session_001",
            "type": "meterpreter",
            "target": "192.168.1.100",
            "created_at": "2025-04-09T10:30:00Z",
            "last_active": "2025-04-09T10:35:00Z",
            "status": "active",
            "username": "root",
            "platform": "linux",
            "architecture": "x64",
            "privileges": "admin"
        }
    ],
    "count": 1,
    "total": 1
}
```

#### Exécuter une commande sur une session

```http
POST /api/session/{session_id}/command
Content-Type: application/json
```

**Body :**
```json
{
    "command": "whoami",
    "timeout": 30
}
```

**Réponse :**
```json
{
    "success": true,
    "session_id": "session_001",
    "command": "whoami",
    "output": "root\n",
    "execution_time": 0.05,
    "exit_code": 0
}
```

#### Fermer une session

```http
DELETE /api/session/{session_id}
```

**Réponse :**
```json
{
    "success": true,
    "session_id": "session_001",
    "message": "Session fermée avec succès"
}
```

---

### Rapports

#### Générer un rapport

```http
POST /api/report/generate
Content-Type: application/json
```

**Body :**
```json
{
    "target": "https://example.com",
    "format": "html",
    "template": "standard",
    "options": {
        "include_charts": true,
        "include_recommendations": true,
        "include_evidence": true,
        "include_stealth_metrics": true,
        "include_apt_timeline": true,
        "include_iocs": true,
        "comments": "Rapport de test",
        "language": "fr"
    }
}
```

**Formats disponibles :**

| Format | Description |
|--------|-------------|
| html | HTML web |
| pdf | PDF document |
| json | JSON data |
| csv | CSV spreadsheet |

**Templates disponibles :**

| Template | Description |
|----------|-------------|
| standard | Rapport complet standard |
| detailed | Rapport très détaillé |
| executive | Résumé pour la direction |
| technical | Rapport technique |
| apt | Spécifique opérations APT |
| stealth | Métriques furtives |

**Réponse :**
```json
{
    "success": true,
    "report_id": "report_1234567890",
    "file": "/reports/report_1234567890.html",
    "size": 245760,
    "pages": 12,
    "generated_at": "2025-04-09T10:30:00Z",
    "expires_at": "2025-05-09T10:30:00Z"
}
```

#### Télécharger un rapport

```http
GET /api/report/{report_id}/download
```

**Réponse :** Fichier binaire

#### Lister les rapports

```http
GET /api/reports/list
```

**Paramètres :**

| Paramètre | Type | Description |
|-----------|------|-------------|
| type | string | standard, multi, apt, stealth |
| limit | integer | Nombre de résultats |

**Réponse :**
```json
{
    "reports": [
        {
            "id": "report_1234567890",
            "name": "example_com_report.html",
            "target": "https://example.com",
            "type": "standard",
            "format": "html",
            "size": 245760,
            "pages": 12,
            "date": "2025-04-09T10:30:00Z",
            "downloads": 3
        }
    ],
    "count": 5,
    "total": 12
}
```

#### Supprimer un rapport

```http
DELETE /api/report/{report_id}
```

**Réponse :**
```json
{
    "success": true,
    "report_id": "report_1234567890",
    "message": "Rapport supprimé avec succès"
}
```

---

### Configuration

#### Obtenir la configuration

```http
GET /api/config
```

**Réponse :**
```json
{
    "version": "2.0.0",
    "language": "fr",
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
        "rotate_proxies": false
    },
    "multi_attack": {
        "default_mode": "sequential",
        "max_parallel": 5,
        "delay_between_attacks": 1,
        "stop_on_error": false
    },
    "apt": {
        "auto_cleanup": true,
        "phase_delay": 5,
        "log_all_phases": true
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
    "proxy": {
        "enabled": false,
        "type": "http",
        "host": "",
        "port": 0
    }
}
```

#### Mettre à jour la configuration

```http
POST /api/config
Content-Type: application/json
```

**Body :**
```json
{
    "language": "en",
    "theme": "light",
    "stealth": {
        "enabled": true,
        "default_level": "high"
    }
}
```

**Réponse :**
```json
{
    "success": true,
    "message": "Configuration mise à jour avec succès",
    "changes": ["language", "theme", "stealth.enabled"]
}
```

#### Réinitialiser la configuration

```http
POST /api/config/reset
```

**Réponse :**
```json
{
    "success": true,
    "message": "Configuration réinitialisée avec succès"
}
```

---

## WebSocket

### Connexion

```javascript
const socket = io('http://localhost:5000', {
    transports: ['websocket'],
    reconnection: true,
    reconnectionAttempts: 5
});
```

### Événements

#### Écouter les événements

```javascript
// Progression du scan
socket.on('scan_progress', (data) => {
    console.log(`Scan: ${data.progress}% - ${data.message}`);
    console.log(`Stealth score: ${data.stealth_score}`);
});

// Scan terminé
socket.on('scan_completed', (data) => {
    console.log(`Scan terminé: ${data.target}`);
    console.log(`Vulnérabilités: ${data.vulnerabilities_count}`);
    console.log(`Durée: ${data.duration}s`);
});

// Vulnérabilité trouvée
socket.on('vulnerability_found', (data) => {
    console.log(`[${data.severity}] ${data.type} sur ${data.target}`);
    console.log(`Confiance: ${data.confidence}%`);
});

// Progression multi-attaque
socket.on('multi_attack_progress', (data) => {
    console.log(`Multi-attaque: ${data.progress}%`);
    console.log(`Attaque courante: ${data.current_attack}`);
    console.log(`Réussies: ${data.completed}/${data.total}`);
});

// Phase APT démarrée
socket.on('apt_phase_start', (data) => {
    console.log(`Phase APT: ${data.phase} (${data.phase_number}/${data.total_phases})`);
    console.log(`Attaques: ${data.attacks_count}`);
});

// Phase APT terminée
socket.on('apt_phase_complete', (data) => {
    console.log(`Phase APT terminée: ${data.phase}`);
    console.log(`Succès: ${data.success_rate}%`);
});

// Alerte furtive
socket.on('stealth_alert', (data) => {
    console.log(`⚠️ Alerte: ${data.message}`);
    console.log(`Sévérité: ${data.severity}`);
    console.log(`Recommandation: ${data.recommendation}`);
});

// Session créée
socket.on('session_created', (data) => {
    console.log(`Session ${data.type} créée sur ${data.target}`);
});

// Attaque terminée
socket.on('attack_completed', (data) => {
    console.log(`Attaque ${data.attack_type} terminée en ${data.duration}s`);
    console.log(`Succès: ${data.success}`);
});

// Notification
socket.on('notification', (data) => {
    console.log(`[${data.type}] ${data.message}`);
    if (data.title) console.log(`Titre: ${data.title}`);
});
```

#### Émettre des événements

```javascript
// S'abonner aux événements
socket.emit('subscribe', {
    events: ['scan_progress', 'vulnerability_found', 'multi_attack_progress', 'apt_phase_start', 'stealth_alert']
});

// Se désabonner
socket.emit('unsubscribe', {
    events: ['scan_progress']
});

// Demander le statut
socket.emit('scan_status', { task_id: 'scan_1234567890' });
socket.emit('multi_attack_status', { task_id: 'multi_1234567890' });
socket.emit('apt_status', { task_id: 'apt_1234567890' });
socket.emit('stealth_status', {});
```

---

## Codes d'erreur

| Code | Description | Solution |
|------|-------------|----------|
| 200 | Succès | - |
| 201 | Créé | - |
| 400 | Requête invalide | Vérifier les paramètres |
| 401 | Non authentifié | Fournir un token valide |
| 403 | Accès interdit | Vérifier les permissions |
| 404 | Ressource non trouvée | Vérifier l'ID/URL |
| 409 | Conflit | Ressource déjà existante |
| 422 | Entité non traitable | Vérifier le format des données |
| 429 | Trop de requêtes | Attendre avant de réessayer |
| 500 | Erreur serveur | Contacter le support |
| 503 | Service indisponible | Réessayer plus tard |

### Format d'erreur

```json
{
    "error": true,
    "code": 400,
    "message": "Description de l'erreur",
    "details": {
        "field": "target",
        "reason": "Format invalide",
        "expected": "URL or IP address"
    },
    "timestamp": "2025-04-09T10:30:00Z",
    "request_id": "req_1234567890"
}
```

---

## Rate Limiting

L'API implémente un rate limiting pour éviter les abus.

### Limites par défaut

| Limite | Valeur |
|--------|--------|
| Requêtes par minute | 60 |
| Requêtes par heure | 1000 |
| Requêtes par jour | 10000 |
| Burst | 10 |

### Headers de rate limiting

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1642345678
X-RateLimit-Retry-After: 60
```

### Contourner les limites

Pour les utilisateurs authentifiés avec un token valide, les limites sont plus élevées :

| Type d'utilisateur | Requêtes/minute |
|-------------------|-----------------|
| Anonyme | 10 |
| Authentifié | 60 |
| Premium | 300 |

---

## Exemples

### cURL

#### Authentification

```bash
# Obtenir un token
curl -X POST http://localhost:5000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"mot_de_passe"}'

# Utiliser le token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### Lancer une multi-attaque

```bash
curl -X POST http://localhost:5000/api/multi-attack \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Test multi",
    "target": "https://example.com",
    "attacks": [
      {"category": "injection", "type": "sql"},
      {"category": "cross_site", "type": "xss"}
    ],
    "execution_mode": "sequential",
    "stealth_level": "high"
  }'
```

#### Configurer le mode furtif

```bash
curl -X POST http://localhost:5000/api/stealth/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "enabled": true,
    "level": "paranoid",
    "use_tor": true,
    "rotate_proxies": true
  }'
```

#### Lancer une opération APT

```bash
curl -X POST http://localhost:5000/api/apt/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "target": "https://example.com",
    "operation_id": "recon_to_exfil",
    "stealth_level": "paranoid"
  }'
```

### Python

```python
import requests
import time
import json

API_URL = "http://localhost:5000/api"
TOKEN = "votre_token_api"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

# Lancer une multi-attaque
multi_data = {
    "name": "Audit complet",
    "target": "https://example.com",
    "attacks": [
        {"category": "injection", "type": "sql"},
        {"category": "cross_site", "type": "xss"},
        {"category": "authentication", "type": "bruteforce"}
    ],
    "execution_mode": "sequential",
    "stealth_level": "high",
    "stop_on_error": False
}

response = requests.post(f"{API_URL}/multi-attack", json=multi_data, headers=headers)
task_id = response.json()["task_id"]
print(f"Multi-attaque lancée: {task_id}")

# Surveiller la progression
while True:
    response = requests.get(f"{API_URL}/multi-attack/{task_id}/status", headers=headers)
    status = response.json()
    
    print(f"Progression: {status['progress']}%")
    print(f"Attaque courante: {status.get('current_attack', 'N/A')}")
    
    if status['status'] == 'completed':
        print("Multi-attaque terminée!")
        break
    elif status['status'] == 'failed':
        print(f"Erreur: {status.get('error', 'Inconnue')}")
        break
    
    time.sleep(5)

# Configurer le mode furtif
stealth_config = {
    "enabled": True,
    "level": "paranoid",
    "use_tor": True,
    "rotate_proxies": True,
    "random_user_agents": True,
    "mimic_human": True
}

response = requests.post(f"{API_URL}/stealth/config", json=stealth_config, headers=headers)
print(response.json())

# Lancer une opération APT
apt_data = {
    "target": "https://example.com",
    "operation_id": "recon_to_exfil",
    "stealth_level": "paranoid",
    "options": {
        "auto_cleanup": True,
        "phase_delay": 10
    }
}

response = requests.post(f"{API_URL}/apt/execute", json=apt_data, headers=headers)
apt_task_id = response.json()["task_id"]
print(f"Opération APT lancée: {apt_task_id}")

# Générer un rapport
report_data = {
    "target": "https://example.com",
    "format": "pdf",
    "template": "apt",
    "options": {
        "include_charts": True,
        "include_stealth_metrics": True,
        "include_apt_timeline": True
    }
}

response = requests.post(f"{API_URL}/report/generate", json=report_data, headers=headers)
report_id = response.json()["report_id"]

# Télécharger le rapport
response = requests.get(f"{API_URL}/report/{report_id}/download", headers=headers)
with open("rapport_apt.pdf", "wb") as f:
    f.write(response.content)
print("Rapport téléchargé: rapport_apt.pdf")
```

### JavaScript (Node.js)

```javascript
const fetch = require('node-fetch');
const WebSocket = require('ws');

const API_URL = 'http://localhost:5000/api';
const TOKEN = 'votre_token_api';

const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${TOKEN}`
};

async function runMultiAttack() {
    // Lancer la multi-attaque
    const response = await fetch(`${API_URL}/multi-attack`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
            name: 'Test multi',
            target: 'https://example.com',
            attacks: [
                { category: 'injection', type: 'sql' },
                { category: 'cross_site', type: 'xss' }
            ],
            execution_mode: 'sequential',
            stealth_level: 'high'
        })
    });
    
    const { task_id } = await response.json();
    console.log(`Multi-attaque lancée: ${task_id}`);
    
    // WebSocket pour les mises à jour temps réel
    const ws = new WebSocket('ws://localhost:5000');
    
    ws.on('open', () => {
        ws.send(JSON.stringify({
            type: 'subscribe',
            events: ['multi_attack_progress', 'stealth_alert']
        }));
    });
    
    ws.on('message', (data) => {
        const event = JSON.parse(data);
        
        if (event.type === 'multi_attack_progress') {
            console.log(`Progression: ${event.data.progress}%`);
            console.log(`Attaque courante: ${event.data.current_attack}`);
        }
        
        if (event.type === 'stealth_alert') {
            console.log(`⚠️ Alerte: ${event.data.message}`);
            console.log(`Recommandation: ${event.data.recommendation}`);
        }
    });
    
    // Configurer le mode furtif
    await fetch(`${API_URL}/stealth/config`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
            enabled: true,
            level: 'paranoid',
            use_tor: true,
            rotate_proxies: true
        })
    });
    
    console.log('Mode furtif configuré');
}

runMultiAttack().catch(console.error);
```

### JavaScript (WebSocket)

```javascript
const socket = io('http://localhost:5000', {
    auth: { token: 'votre_token_api' }
});

socket.on('connect', () => {
    console.log('Connecté à RedForge v2.0');
    
    // S'abonner aux événements
    socket.emit('subscribe', {
        events: [
            'multi_attack_progress',
            'apt_phase_start',
            'apt_phase_complete',
            'stealth_alert',
            'vulnerability_found'
        ]
    });
});

// Multi-attaque
socket.on('multi_attack_progress', (data) => {
    console.log(`Multi-attaque: ${data.progress}%`);
    console.log(`Attaque: ${data.current_attack}`);
    console.log(`Statut: ${data.completed}/${data.total}`);
    
    // Mettre à jour l'interface
    document.getElementById('progress-bar').style.width = `${data.progress}%`;
    document.getElementById('current-attack').textContent = data.current_attack;
});

// Opération APT
socket.on('apt_phase_start', (data) => {
    console.log(`Phase APT: ${data.phase}`);
    console.log(`Attaques: ${data.attacks_count}`);
    
    // Ajouter à la timeline
    const timeline = document.getElementById('apt-timeline');
    const phase = document.createElement('div');
    phase.className = 'apt-phase';
    phase.innerHTML = `
        <div class="phase-name">${data.phase}</div>
        <div class="phase-status">En cours...</div>
        <div class="phase-progress">
            <div class="progress-bar" style="width: 0%"></div>
        </div>
    `;
    timeline.appendChild(phase);
});

socket.on('apt_phase_complete', (data) => {
    console.log(`Phase APT terminée: ${data.phase}`);
    console.log(`Succès: ${data.success_rate}%`);
    
    // Mettre à jour la timeline
    const phase = document.querySelector(`.apt-phase:last-child`);
    if (phase) {
        phase.querySelector('.phase-status').textContent = `Terminé (${data.success_rate}%)`;
        phase.querySelector('.progress-bar').style.width = '100%';
    }
});

// Alerte furtive
socket.on('stealth_alert', (data) => {
    console.log(`⚠️ ALERTE: ${data.message}`);
    console.log(`Sévérité: ${data.severity}`);
    
    // Afficher une notification
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${data.severity}`;
    alertDiv.innerHTML = `
        <strong>⚠️ Alerte furtive</strong>
        <p>${data.message}</p>
        <small>Recommandation: ${data.recommendation}</small>
    `;
    document.getElementById('alerts').prepend(alertDiv);
});

// Vulnérabilité trouvée
socket.on('vulnerability_found', (data) => {
    console.log(`[${data.severity}] ${data.type} sur ${data.target}`);
    
    // Ajouter à la liste
    const vulnList = document.getElementById('vulnerabilities');
    const item = document.createElement('li');
    item.className = `vuln vuln-${data.severity.toLowerCase()}`;
    item.innerHTML = `
        <span class="severity">${data.severity}</span>
        <span class="type">${data.type}</span>
        <span class="target">${data.target}</span>
        <span class="parameter">${data.parameter || ''}</span>
    `;
    vulnList.appendChild(item);
});
```

---

## Support

Pour toute question concernant l'API :

- 📧 Email : elfriedyouet@gmail.com
- 🐛 Signalement : https://github.com/Elfried002/RedForge/issues

---

## Licence

Cette API est sous licence **GNU General Public License v3.0**.
Voir le fichier [LICENSE](../LICENSE) pour plus de détails.

---

<div align="center">

*Documentation de la Version 2.0.0*

** RedForge - Forgez vos attaques, maîtrisez vos cibles**

</div>


## Résumé des mises à jour pour la v2.0.0

### Nouveaux endpoints ajoutés

| Catégorie | Endpoints |
|-----------|-----------|
| **Multi-Attaques** | POST /multi-attack, GET /multi-attack/{id}/status, DELETE /multi-attack/{id} |
| **Mode Furtif** | POST /stealth/config, GET /stealth/status, POST /stealth/test |
| **Opérations APT** | POST /apt/execute, GET /apt/{id}/status, POST /apt/custom, GET /apt/operations |
