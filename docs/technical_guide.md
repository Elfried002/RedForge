# Guide Technique RedForge v2.0

## Table des matières

1. [Architecture du système](#architecture-du-système)
2. [Modules et composants](#modules-et-composants)
3. [Multi-Attaques](#multi-attaques)
4. [Mode Furtif](#mode-furtif)
5. [Opérations APT](#opérations-apt)
6. [API et interfaces](#api-et-interfaces)
7. [Base de données et stockage](#base-de-données-et-stockage)
8. [Sécurité](#sécurité)
9. [Performance](#performance)
10. [Déploiement](#déploiement)
11. [Dépannage](#dépannage)
12. [Extensions et plugins](#extensions-et-plugins)
13. [Références](#références)

---

## Architecture du système

### Vue d'ensemble

RedForge v2.0 est construit sur une architecture modulaire en couches, conçue pour la flexibilité, l'extensibilité et les performances.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Interface Utilisateur                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  CLI (argparse)  │  GUI (Flask + Socket.IO)  │  API REST  │  WebSocket      │
├─────────────────────────────────────────────────────────────────────────────┤
│                         Orchestrateur Central v2.0                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  Attacks  │  Connectors  │  Phases  │  Utils  │  Stealth  │  Multi  │  APT  │
├─────────────────────────────────────────────────────────────────────────────┤
│                              Outils Externes                                │
│  Nmap │ Metasploit │ SQLMap │ Hydra │ XSStrike │ TOR │ Proxychains │ ...    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Diagramme de séquence - Multi-attaque

```
Utilisateur → GUI/CLI → Orchestrateur → MultiAttackManager → Queue → Workers
                    ↓                      ↓                ↓
                Attack Chainer      ParallelExecutor    Results
                    ↓                      ↓                ↓
              Session Manager        ProgressTracker   Aggregator
                    ↓                      ↓                ↓
              Report Generator      WebSocket Events   Storage
```

### Diagramme de séquence - Mode furtif

```
Utilisateur → StealthConfig → StealthManager → ProxyRotator → TorManager
                    ↓              ↓                ↓
              DelayJitter    UserAgentPool    RequestHandler
                    ↓              ↓                ↓
              WebSocket      MetricsTracker   AlertManager
```

### Diagramme de séquence - Opération APT

```
Utilisateur → APTManager → PhaseOrchestrator → PhaseExecutor
                    ↓              ↓                  ↓
              Phase1(Recon)   Phase2(Access)   Phase3(Persistence)
                    ↓              ↓                  ↓
              Phase4(Escalate) Phase5(Movement) Phase6(Exfiltration)
                    ↓              ↓                  ↓
              Cleanup         ReportGen         WebSocket
```

### Composants principaux v2.0

| Composant | Rôle | Technologies | Nouveautés |
|-----------|------|--------------|------------|
| Core | Orchestration centrale | Python, asyncio | APT, Multi-attaque |
| CLI | Interface ligne de commande | argparse, rich | Nouvelles options |
| GUI | Interface graphique | Flask, Socket.IO | 3 nouveaux onglets |
| Stealth | Mode furtif | TOR, proxies | 4 niveaux |
| MultiAttack | Multi-attaques | threading, queue | Parallèle/séquentiel |
| APT | Opérations APT | asyncio | 6 phases |

---

## Modules et composants

### 1. Core (`src/core/`)

#### Orchestrator (`orchestrator.py`)

```python
class RedForgeOrchestrator:
    """Moteur d'orchestration principal v2.0"""
    
    def __init__(self, target: str, stealth: bool = False):
        self.target = target
        self.stealth = stealth
        self.phases = ['footprint', 'analysis', 'scan', 'exploit']
        self.stealth_manager = StealthManager() if stealth else None
    
    def run_phase(self, phase: str, stealth_level: str = "medium") -> Dict:
        """Exécute une phase spécifique avec mode furtif"""
        
    def run_all(self, multi_attack: bool = False) -> Dict:
        """Exécute toutes les phases (simple ou multi-attaque)"""
        
    def run_with_stealth(self, config: StealthConfig) -> Dict:
        """Exécute avec configuration furtive personnalisée"""
```

#### Attack Chainer (`attack_chainer.py`)

```python
class AttackChainer:
    """Chaînage intelligent d'attaques v2.0"""
    
    def create_chain(self, vulnerabilities: List, stealth: bool = False) -> List:
        """Crée une chaîne d'attaque optimisée"""
        
    def execute_chain(self, chain: List, mode: str = "sequential") -> Dict:
        """Exécute la chaîne (séquentiel ou parallèle)"""
        
    def get_optimal_chain(self, target: str) -> List:
        """Détermine la chaîne optimale basée sur la cible"""
```

**Chaînes prédéfinies v2.0 :**
- SQLi → RCE → Persistance
- XSS → Session Hijacking → Lateral Movement
- LFI → RCE → Data Exfiltration
- SSRF → Internal Scan → Pivot
- File Upload → Web Shell → Privilege Escalation

#### Session Manager (`session_manager.py`)

```python
class SessionManager:
    """Gestionnaire de sessions v2.0"""
    
    def create_session(self, session_type: str, target: str, stealth: bool = False) -> str:
        """Crée une nouvelle session (supporte mode furtif)"""
        
    def execute_command(self, session_id: str, command: str, timeout: int = 30) -> Dict:
        """Exécute une commande sur une session"""
        
    def list_sessions(self) -> List[Dict]:
        """Liste toutes les sessions actives"""
        
    def close_session(self, session_id: str, cleanup: bool = True) -> bool:
        """Ferme une session avec nettoyage optionnel"""
```

### 2. Multi-Attaques (`src/multi_attack/`)

#### MultiAttackManager (`multi_attack/manager.py`)

```python
class MultiAttackManager:
    """Gestionnaire de multi-attaques"""
    
    def __init__(self, max_workers: int = 5):
        self.queue = Queue()
        self.workers = max_workers
        self.results = []
    
    def add_attack(self, attack: Dict) -> None:
        """Ajoute une attaque à la file"""
        
    def execute_sequential(self) -> List[Dict]:
        """Exécute les attaques séquentiellement"""
        
    def execute_parallel(self) -> List[Dict]:
        """Exécute les attaques en parallèle"""
        
    def get_progress(self) -> Dict:
        """Retourne la progression en temps réel"""
```

**Modes d'exécution :**

| Mode | Description | Utilisation |
|------|-------------|-------------|
| `sequential` | Une attaque après l'autre | Discrétion |
| `parallel` | Toutes en même temps | Performance |
| `mixed` | Groupes parallèles | Équilibre |
| `adaptive` | Ajustement dynamique | Optimisation |

#### Queue Manager (`multi_attack/queue_manager.py`)

```python
class QueueManager:
    """Gestionnaire de file d'attente"""
    
    def __init__(self):
        self.queue = PriorityQueue()
        self.pending = []
        self.completed = []
        self.failed = []
    
    def enqueue(self, attack: Dict, priority: int = 5) -> None:
        """Ajoute une attaque avec priorité"""
        
    def dequeue(self) -> Optional[Dict]:
        """Récupère la prochaine attaque"""
        
    def get_status(self) -> Dict:
        """Statut de la file"""
```

### 3. Mode Furtif (`src/stealth/`)

#### StealthManager (`stealth/stealth_manager.py`)

```python
class StealthManager:
    """Gestionnaire du mode furtif v2.0"""
    
    LEVELS = {
        "low": {"delay": 0.5, "jitter": 0.1, "tor": False, "proxies": False},
        "medium": {"delay": 1.5, "jitter": 0.3, "tor": False, "proxies": False},
        "high": {"delay": 3.0, "jitter": 0.5, "tor": True, "proxies": False},
        "paranoid": {"delay": 5.0, "jitter": 0.7, "tor": True, "proxies": True}
    }
    
    def __init__(self, level: str = "medium"):
        self.level = level
        self.config = self.LEVELS[level]
        self.tor = TorManager() if self.config["tor"] else None
        self.proxies = ProxyRotator() if self.config["proxies"] else None
        self.user_agents = UserAgentPool()
    
    def get_delay(self) -> float:
        """Retourne un délai avec jitter"""
        base = self.config["delay"]
        jitter = base * self.config["jitter"]
        return random.uniform(base - jitter, base + jitter)
    
    def get_user_agent(self) -> str:
        """Retourne un user-agent aléatoire"""
        return self.user_agents.random()
    
    def get_proxy(self) -> str:
        """Retourne un proxy aléatoire (rotation)"""
        return self.proxies.rotate() if self.proxies else None
    
    def get_stealth_score(self) -> int:
        """Calcule le score de furtivité (0-100)"""
```

#### TorManager (`stealth/tor_manager.py`)

```python
class TorManager:
    """Gestionnaire TOR pour l'anonymisation"""
    
    def __init__(self, control_port: int = 9051, socks_port: int = 9050):
        self.control_port = control_port
        self.socks_port = socks_port
        self.session = None
    
    def start(self) -> bool:
        """Démarre le service TOR"""
        
    def stop(self) -> bool:
        """Arrête le service TOR"""
        
    def renew_identity(self) -> bool:
        """Renouvelle l'identité TOR"""
        
    def is_running(self) -> bool:
        """Vérifie si TOR est actif"""
```

#### ProxyRotator (`stealth/proxy_rotator.py`)

```python
class ProxyRotator:
    """Rotateur de proxies"""
    
    def __init__(self, proxy_file: Optional[str] = None):
        self.proxies = self.load_proxies(proxy_file)
        self.current_index = 0
    
    def rotate(self) -> str:
        """Change de proxy (round-robin)"""
        
    def random(self) -> str:
        """Retourne un proxy aléatoire"""
        
    def add_proxy(self, proxy: str) -> None:
        """Ajoute un proxy à la liste"""
        
    def remove_proxy(self, proxy: str) -> None:
        """Supprime un proxy de la liste"""
        
    def test_proxy(self, proxy: str) -> bool:
        """Teste si le proxy est fonctionnel"""
```

### 4. Opérations APT (`src/apt/`)

#### APTManager (`apt/apt_manager.py`)

```python
class APTManager:
    """Gestionnaire d'opérations APT"""
    
    OPERATIONS = {
        "recon_to_exfil": {
            "phases": ["reconnaissance", "initial_access", "persistence", 
                      "privilege_escalation", "lateral_movement", "data_exfiltration"],
            "cleanup": True
        },
        "web_app_compromise": {
            "phases": ["footprinting", "vulnerability_scan", "exploitation", "post_exploit"],
            "cleanup": True
        }
    }
    
    def __init__(self, target: str, stealth: StealthManager = None):
        self.target = target
        self.stealth = stealth
        self.phases = []
        self.results = []
    
    def load_operation(self, operation_id: str) -> bool:
        """Charge une opération prédéfinie"""
        
    def load_custom_operation(self, config_file: str) -> bool:
        """Charge une opération personnalisée"""
        
    def execute_phase(self, phase: Dict) -> Dict:
        """Exécute une phase spécifique"""
        
    def run(self) -> Dict:
        """Exécute l'opération complète"""
        
    def cleanup(self) -> bool:
        """Nettoie les traces de l'opération"""
```

#### PhaseExecutor (`apt/phase_executor.py`)

```python
class PhaseExecutor:
    """Exécuteur de phases APT"""
    
    PHASES = {
        "reconnaissance": ["port_scan", "service_enum", "directory_bruteforce", "technology_detect"],
        "initial_access": ["sql_injection", "xss", "file_upload", "command_injection"],
        "persistence": ["backdoor", "scheduled_task", "registry_persistence", "ssh_key"],
        "privilege_escalation": ["sudo_abuse", "kernel_exploit", "win_priv_esc", "docker_escape"],
        "lateral_movement": ["ssh_pivot", "smb_exec", "wmi_exec", "ps_exec"],
        "data_exfiltration": ["dns_exfil", "http_exfil", "custom_protocol", "cloud_exfil"]
    }
    
    def __init__(self, target: str, stealth: StealthManager = None):
        self.target = target
        self.stealth = stealth
    
    def execute(self, phase_name: str, options: Dict = None) -> Dict:
        """Exécute une phase avec les options"""
        
    def get_phase_status(self) -> Dict:
        """Retourne le statut de la phase en cours"""
```

#### Persistence (`apt/persistence/`)

```python
class PersistenceManager:
    """Gestionnaire de persistance"""
    
    METHODS = {
        "windows": ["registry", "scheduled_task", "service", "startup_folder", "wmi"],
        "linux": ["cron", "systemd", "bashrc", "ssh_authorized_keys", "ld_preload"]
    }
    
    def install(self, method: str, target: str) -> bool:
        """Installe un mécanisme de persistance"""
        
    def remove(self, method: str, target: str) -> bool:
        """Supprime un mécanisme de persistance"""
        
    def list_installed(self, target: str) -> List[str]:
        """Liste les mécanismes installés"""
```

#### Lateral Movement (`apt/lateral_movement/`)

```python
class LateralMovement:
    """Gestionnaire de mouvement latéral"""
    
    TECHNIQUES = {
        "windows": ["smb", "wmi", "ps_exec", "winrm", "rdp"],
        "linux": ["ssh", "rsync", "scp", "reverse_tunnel"]
    }
    
    def move(self, technique: str, source: str, target: str, credential: Dict) -> bool:
        """Effectue un mouvement latéral"""
        
    def discover_hosts(self, network: str) -> List[str]:
        """Découvre les hôtes sur le réseau"""
        
    def propagate(self, source: str, credentials: Dict) -> List[Dict]:
        """Propagation automatique sur le réseau"""
```

#### Data Exfiltration (`apt/exfiltration/`)

```python
class ExfiltrationManager:
    """Gestionnaire d'exfiltration de données"""
    
    METHODS = {
        "dns": {"port": 53, "protocol": "udp", "chunk_size": 512},
        "http": {"port": 80, "protocol": "tcp", "chunk_size": 8192},
        "https": {"port": 443, "protocol": "tls", "chunk_size": 8192},
        "custom": {"port": 4443, "protocol": "tcp", "chunk_size": 4096}
    }
    
    def exfiltrate(self, data: bytes, method: str, server: str) -> bool:
        """Exfiltre des données vers un serveur C2"""
        
    def chunk_data(self, data: bytes, chunk_size: int) -> List[bytes]:
        """Découpe les données en chunks"""
        
    def encrypt_data(self, data: bytes, key: bytes) -> bytes:
        """Chiffre les données avant exfiltration"""
```

---

## API et interfaces

### API REST v2.0

#### Nouveaux endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/multi-attack` | Lancer une multi-attaque |
| GET | `/api/multi-attack/{id}/status` | Statut multi-attaque |
| DELETE | `/api/multi-attack/{id}` | Arrêter multi-attaque |
| POST | `/api/stealth/config` | Configurer mode furtif |
| GET | `/api/stealth/status` | Statut mode furtif |
| POST | `/api/stealth/test` | Tester configuration |
| POST | `/api/apt/execute` | Lancer opération APT |
| GET | `/api/apt/{id}/status` | Statut opération APT |
| POST | `/api/apt/custom` | Créer opération personnalisée |
| GET | `/api/apt/operations` | Lister opérations |

### WebSocket v2.0

#### Nouveaux événements

| Événement | Direction | Description |
|-----------|-----------|-------------|
| `multi_attack_progress` | Server → Client | Progression multi-attaque |
| `multi_attack_completed` | Server → Client | Multi-attaque terminée |
| `apt_phase_start` | Server → Client | Phase APT démarrée |
| `apt_phase_progress` | Server → Client | Progression phase APT |
| `apt_phase_complete` | Server → Client | Phase APT terminée |
| `apt_completed` | Server → Client | Opération APT terminée |
| `stealth_status` | Server → Client | Statut mode furtif |
| `stealth_alert` | Server → Client | Alerte furtive |
| `stealth_metrics` | Server → Client | Métriques furtives |

### Interface CLI v2.0

#### Nouvelles options

| Option | Description | Exemple |
|--------|-------------|---------|
| `--multi` | Fichier config multi-attaque | `redforge --multi config.json` |
| `--stealth` | Activer mode furtif | `redforge --stealth high` |
| `--apt` | Opération APT | `redforge --apt recon_to_exfil` |
| `--tor` | Utiliser TOR | `redforge --tor` |
| `--proxy-list` | Fichier de proxies | `redforge --proxy-list proxies.txt` |

---

## Base de données et stockage

### Structure des fichiers v2.0

```
~/.RedForge/
├── workspace/           # Espace de travail
│   ├── targets/        # Cibles sauvegardées
│   ├── results/        # Résultats des scans
│   └── sessions/       # Sessions sauvegardées
├── stealth/            # Configuration furtive
│   ├── proxies.txt     # Liste des proxies
│   ├── user_agents.txt # User-Agents personnalisés
│   └── torrc          # Configuration TOR
├── multi_attack/       # Données multi-attaques
│   ├── queue/          # Files d'attente
│   ├── results/        # Résultats intermédiaires
│   └── templates/      # Templates JSON
├── apt_operations/     # Opérations APT
│   ├── custom/         # Opérations personnalisées
│   ├── persistence/    # Données de persistance
│   └── exfiltration/   # Données exfiltrées
├── logs/               # Logs
│   ├── redforge.log    # Log principal
│   ├── stealth.log     # Log mode furtif
│   └── apt.log         # Log opérations APT
├── reports/            # Rapports générés
├── wordlists/          # Wordlists personnalisées
└── config.json         # Configuration v2.0
```

### Format des résultats v2.0

```json
{
    "version": "2.0.0",
    "target": "example.com",
    "timestamp": "2025-04-09T12:00:00Z",
    "stealth": {
        "enabled": true,
        "level": "high",
        "score": 85,
        "alerts_avoided": 12
    },
    "multi_attack": {
        "mode": "sequential",
        "total_attacks": 5,
        "successful": 4,
        "duration": 360
    },
    "phases": {
        "reconnaissance": {...},
        "analysis": {...},
        "scanning": {...},
        "exploitation": {...}
    },
    "vulnerabilities": [...],
    "apt_phases": [...],
    "iocs": [...],
    "summary": {...}
}
```

---

## Sécurité

### Authentification v2.0

#### API Token

```python
# Génération
token = secrets.token_urlsafe(32)

# Validation
def validate_token(token: str) -> bool:
    return token in valid_tokens and not is_expired(token)

# Rotation automatique (30 jours)
def rotate_tokens():
    for token in tokens:
        if token.age > timedelta(days=30):
            revoke_token(token)
            generate_new_token()
```

#### Rate Limiting

```python
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.limit = requests_per_minute
        self.requests = {}
    
    def is_allowed(self, client_id: str) -> bool:
        # Implémentation avec Redis ou mémoire
        pass
```

### Chiffrement v2.0

#### AES-256-GCM

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_data(data: bytes, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext

def decrypt_data(encrypted: bytes, key: bytes) -> bytes:
    nonce = encrypted[:12]
    ciphertext = encrypted[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)
```

---

## Performance

### Optimisations v2.0

#### Multi-threading pour multi-attaques

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def execute_parallel(attacks: List[Dict], max_workers: int = 5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(execute_attack, attack): attack for attack in attacks}
        results = []
        for future in as_completed(futures):
            results.append(future.result())
    return results
```

#### Cache pour mode furtif

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_stealth_delay(level: str) -> float:
    configs = {
        "low": 0.5,
        "medium": 1.5,
        "high": 3.0,
        "paranoid": 5.0
    }
    return configs.get(level, 1.5) + random.uniform(0, 0.5)
```

#### Asyncio pour opérations APT

```python
import asyncio

async def execute_apt_phases(phases: List[Dict], stealth: StealthManager):
    results = []
    for phase in phases:
        result = await execute_phase(phase, stealth)
        results.append(result)
        await asyncio.sleep(stealth.get_delay())
    return results
```

### Métriques v2.0

| Opération | v1.0 | v2.0 | Amélioration |
|-----------|------|------|--------------|
| Scan footprint | 30s | 25s | +17% |
| Multi-attaque (5 attaques) | N/A | 180s | - |
| Mode furtif overhead | N/A | +20% | - |
| Opération APT (6 phases) | N/A | 600s | - |
| Mémoire (base) | 100MB | 80MB | +20% |

---

## Déploiement

### Installation v2.0

```bash
# Cloner le dépôt
git clone https://github.com/Elfried002/RedForge.git
cd RedForge

# Choisir la version
git checkout v2.0.0

# Installation complète
sudo ./install.sh

# Installation avec mode furtif (TOR)
sudo ./install.sh --with-tor

# Installation Docker
docker-compose --profile full up -d
```

### Configuration v2.0

```json
{
    "version": "2.0.0",
    "stealth": {
        "enabled": false,
        "default_level": "medium",
        "tor_enabled": false,
        "proxy_rotation": false,
        "random_user_agents": true
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
        "log_all_phases": true,
        "persistence_dir": "/tmp/redforge_persistence"
    }
}
```

### Variables d'environnement v2.0

```bash
# Mode furtif
export STEALTH_ENABLED=true
export STEALTH_LEVEL=high
export STEALTH_TOR_ENABLED=true
export STEALTH_PROXY_LIST=/path/to/proxies.txt

# Multi-attaques
export MULTI_ATTACK_MAX_PARALLEL=10
export MULTI_ATTACK_DEFAULT_MODE=parallel

# Opérations APT
export APT_AUTO_CLEANUP=true
export APT_PHASE_DELAY=10
export APT_PERSISTENCE_DIR=/opt/redforge/persistence
export APT_C2_SERVER=https://c2.example.com
```

---

## Dépannage

### Problèmes courants v2.0

#### 1. Mode furtif non fonctionnel

```bash
# Vérifier TOR
systemctl status tor
tor --version

# Tester les proxies
redforge --test-proxy socks5://127.0.0.1:9050

# Logs spécifiques
tail -f ~/.RedForge/logs/stealth.log
```

#### 2. Multi-attaque bloquée

```bash
# Vérifier la file
redforge --multi-status

# Nettoyer la queue
redforge --multi-clear

# Augmenter le timeout
export MULTI_ATTACK_TIMEOUT=600
```

#### 3. Opération APT échouée

```bash
# Vérifier les permissions
ls -la ~/.RedForge/apt_operations/

# Logs détaillés
tail -f ~/.RedForge/logs/apt.log

# Nettoyage manuel
redforge --apt-cleanup --force
```

### Logs de débogage v2.0

```bash
# Mode debug complet
redforge --debug --stealth --multi config.json

# Logs spécifiques au mode furtif
tail -f ~/.RedForge/logs/stealth.log

# Logs spécifiques aux opérations APT
tail -f ~/.RedForge/logs/apt.log

# Logs JSON analysables
cat ~/.RedForge/logs/redforge.json | jq 'select(.module=="stealth")'
```

### Diagnostic v2.0

```bash
# Vérification complète
redforge --check-all

# Tester le mode furtif
redforge --test-stealth --target example.com

# Tester les multi-attaques
redforge --test-multi --config test_config.json

# Tester les opérations APT
redforge --test-apt --operation recon_to_exfil --target example.com

# Benchmark
redforge --benchmark --mode all
```

---

## Extensions et plugins v2.0

### Architecture des plugins v2.0

```python
from src.plugins import Plugin, PluginType, Hook

class CustomStealthPlugin(Plugin):
    """Plugin de technique furtive personnalisée"""
    
    def get_info(self) -> Dict:
        return {
            "name": "CustomStealth",
            "version": "1.0.0",
            "type": PluginType.STEALTH,
            "author": "Your Name"
        }
    
    @Hook('stealth_before_request')
    def before_request(self, request: Dict) -> Dict:
        """Modifie la requête avant envoi"""
        request['headers']['X-Custom'] = 'value'
        return request
    
    @Hook('stealth_after_response')
    def after_response(self, response: Dict) -> Dict:
        """Traite la réponse reçue"""
        response['stealth_processed'] = True
        return response

class CustomMultiAttackPlugin(Plugin):
    """Plugin d'orchestration multi-attaque"""
    
    def get_info(self) -> Dict:
        return {
            "name": "CustomMultiAttack",
            "version": "1.0.0",
            "type": PluginType.MULTI_ATTACK,
            "author": "Your Name"
        }
    
    def optimize_order(self, attacks: List[Dict]) -> List[Dict]:
        """Optimise l'ordre des attaques"""
        # Logique personnalisée
        return sorted(attacks, key=lambda x: x['priority'])

class CustomAPTPlugin(Plugin):
    """Plugin de phase APT personnalisée"""
    
    def get_info(self) -> Dict:
        return {
            "name": "CustomAPTPhase",
            "version": "1.0.0",
            "type": PluginType.APT,
            "author": "Your Name"
        }
    
    def execute_phase(self, target: str, options: Dict) -> Dict:
        """Exécute une phase APT personnalisée"""
        # Logique personnalisée
        return {"success": True, "data": "result"}
```

### Installation d'un plugin v2.0

```bash
# Copier dans le dossier plugins
cp my_plugin.py /opt/RedForge/plugins/

# Activer le plugin
redforge --plugin enable my_plugin

# Configurer le plugin
redforge --plugin config my_plugin --set option=value

# Voir les hooks
redforge --plugin hooks my_plugin

# Désactiver
redforge --plugin disable my_plugin
```

---

## Références

### Liens utiles

- [GitHub](https://github.com/Elfried002/RedForge)
- [MITRE ATT&CK](https://attack.mitre.org)

### Bibliographie

1. Metasploit Framework Documentation
2. OWASP Testing Guide v4.2
3. MITRE ATT&CK Framework
4. PTES Technical Guidelines
5. Nmap Network Scanning
6. TOR Project Documentation

### Outils intégrés v2.0

| Outil | Version | Documentation | Utilisation |
|-------|---------|---------------|-------------|
| Nmap | 7.94+ | [nmap.org](https://nmap.org) | Scan réseau |
| Metasploit | 6.4+ | [metasploit.com](https://metasploit.com) | Exploitation |
| SQLMap | 1.7+ | [sqlmap.org](http://sqlmap.org) | Injection SQL |
| TOR | 0.4.8+ | [torproject.org](https://torproject.org) | Anonymisation |
| Proxychains | 4.0+ | [github.com](https://github.com/rofl0r/proxychains-ng) | Rotation proxies |

---

<div align="center">

*Documentation technique - Version 2.0.0*

** RedForge - Forgez vos attaques, maîtrisez vos cibles**

*Dernière mise à jour : 9 Avril 2025*

</div>

## Résumé des mises à jour pour la v2.0.0

### Nouvelles sections ajoutées

| Section | Contenu |
|---------|---------|
| **Multi-Attaques** | MultiAttackManager, QueueManager, modes d'exécution |
| **Mode Furtif** | StealthManager, TorManager, ProxyRotator, UserAgentPool |
| **Opérations APT** | APTManager, PhaseExecutor, PersistenceManager, LateralMovement, ExfiltrationManager |
