#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration de RedForge
Gestion des chemins, variables et vérifications système
Version APT avec support furtif et configuration avancée
"""

import os
import sys
import json
import platform
import shutil
import socket
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProxyConfig:
    """Configuration proxy"""
    enabled: bool = False
    http: str = ""
    https: str = ""
    no_proxy: List[str] = field(default_factory=lambda: ["localhost", "127.0.0.1"])
    username: str = ""
    password: str = ""
    rotation: bool = False
    proxies_list: List[str] = field(default_factory=list)


@dataclass
class NotificationConfig:
    """Configuration des notifications"""
    enabled: bool = True
    email: str = ""
    webhook: str = ""
    slack_webhook: str = ""
    discord_webhook: str = ""
    events: Dict[str, bool] = field(default_factory=lambda: {
        "scan_start": True,
        "scan_complete": True,
        "vulnerability_found": True,
        "session_created": True,
        "exploit_success": True,
        "data_exfiltrated": True
    })


@dataclass
class StealthConfig:
    """Configuration de furtivité"""
    enabled: bool = False
    apt_mode: bool = False
    delay_min: float = 1.0
    delay_max: float = 5.0
    jitter: float = 0.3
    user_agent_rotation: bool = True
    user_agents: List[str] = field(default_factory=list)
    proxy_rotation: bool = False
    request_spoofing: bool = True
    inactivity_hours_start: int = 0
    inactivity_hours_end: int = 6
    max_concurrent_requests: int = 3


@dataclass
class APTConfig:
    """Configuration APT"""
    enabled: bool = False
    operation_duration: int = 86400  # 24 heures
    phase_delay_min: int = 300
    phase_delay_max: int = 3600
    persistence_methods: List[str] = field(default_factory=lambda: ["webshell", "cron_job"])
    exfil_endpoint: str = ""
    exfil_interval: int = 3600
    cleanup_traces: bool = True
    use_tor: bool = False
    tor_proxy: str = "socks5://127.0.0.1:9050"


class RedForgeConfig:
    """Configuration centrale de RedForge avec support APT"""
    
    # Version
    VERSION = "2.0.0"
    
    # Chemins statiques
    BASE_DIR = Path(__file__).parent.parent.parent
    SRC_DIR = BASE_DIR / "src"
    DATA_DIR = BASE_DIR / "data"
    CONFIG_DIR = BASE_DIR / "config"
    
    # Chemins dynamiques (utilisateur)
    WORKSPACE_DIR = Path.home() / ".RedForge"
    LOGS_DIR = WORKSPACE_DIR / "logs"
    REPORTS_DIR = WORKSPACE_DIR / "reports"
    SESSIONS_DIR = WORKSPACE_DIR / "sessions"
    WORDLISTS_DIR = WORKSPACE_DIR / "wordlists"
    CACHE_DIR = WORKSPACE_DIR / "cache"
    LOOT_DIR = WORKSPACE_DIR / "loot"
    
    # Configuration par défaut
    DEFAULT_TIMEOUT = 300
    DEFAULT_THREADS = 10
    DEFAULT_LEVEL = 2
    DEFAULT_LANGUAGE = "fr_FR"
    DEFAULT_THEME = "auto"
    DEFAULT_OUTPUT_FORMAT = "html"
    
    # Configuration Metasploit
    METASPLOIT_RPC_HOST = "127.0.0.1"
    METASPLOIT_RPC_PORT = 55553
    METASPLOIT_RPC_PASSWORD = "RedForge2024"
    METASPLOIT_RPC_SSL = False
    METASPLOIT_AUTO_START = True
    
    # Configuration API
    API_HOST = "127.0.0.1"
    API_PORT = 5000
    API_DEBUG = False
    API_SECRET_KEY = ""
    
    # Configuration Database (SQLite)
    DB_PATH = WORKSPACE_DIR / "redforge.db"
    
    # Configuration logging
    LOG_LEVEL = "INFO"
    LOG_MAX_SIZE_MB = 10
    LOG_BACKUP_COUNT = 5
    
    # Chemins des outils (Kali/Parrot)
    TOOL_PATHS = {
        "nmap": "/usr/bin/nmap",
        "msfconsole": "/usr/bin/msfconsole",
        "msfrpcd": "/usr/bin/msfrpcd",
        "sqlmap": "/usr/bin/sqlmap",
        "whatweb": "/usr/bin/whatweb",
        "dirb": "/usr/bin/dirb",
        "hydra": "/usr/bin/hydra",
        "wafw00f": "/usr/local/bin/wafw00f",
        "gobuster": "/usr/bin/gobuster",
        "ffuf": "/usr/bin/ffuf",
        "nikto": "/usr/bin/nikto",
        "xsstrike": "/usr/local/bin/xsstrike",
        "dalfox": "/usr/local/bin/dalfox",
        "jwt_tool": "/usr/local/bin/jwt_tool",
        "zap-cli": "/usr/bin/zap-cli",
    }
    
    # Wordlists par défaut
    WORDLISTS = {
        "common": DATA_DIR / "wordlists" / "common.txt",
        "subdomains": DATA_DIR / "wordlists" / "subdomains.txt",
        "directories": DATA_DIR / "wordlists" / "directories.txt",
        "parameters": DATA_DIR / "wordlists" / "parameters.txt",
        "passwords": DATA_DIR / "wordlists" / "passwords.txt",
        "users": DATA_DIR / "wordlists" / "users.txt",
    }
    
    # Configuration chargée
    _config: Dict[str, Any] = {}
    _loaded = False
    
    # Configurations
    proxy: ProxyConfig = ProxyConfig()
    notifications: NotificationConfig = NotificationConfig()
    stealth: StealthConfig = StealthConfig()
    apt: APTConfig = APTConfig()
    
    @classmethod
    def initialize(cls) -> bool:
        """Initialise la configuration (à appeler au démarrage)"""
        if cls._loaded:
            return True
        
        # Créer les répertoires
        cls._create_directories()
        
        # Créer les wordlists par défaut
        cls._create_default_wordlists()
        
        # Charger la configuration
        cls.load_config()
        
        # Charger les sous-configurations
        cls._load_proxy_config()
        cls._load_notifications_config()
        cls._load_stealth_config()
        cls._load_apt_config()
        
        cls._loaded = True
        return True
    
    @classmethod
    def _create_directories(cls):
        """Crée tous les répertoires nécessaires"""
        directories = [
            cls.WORKSPACE_DIR,
            cls.LOGS_DIR,
            cls.REPORTS_DIR,
            cls.SESSIONS_DIR,
            cls.WORDLISTS_DIR,
            cls.CACHE_DIR,
            cls.LOOT_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def _create_default_wordlists(cls):
        """Crée les wordlists par défaut si elles n'existent pas"""
        # Wordlist users par défaut
        users_file = cls.WORDLISTS_DIR / "users.txt"
        if not users_file.exists():
            default_users = [
                "admin", "root", "user", "test", "guest", "administrator",
                "webmaster", "support", "info", "contact", "sales", "marketing",
                "admin1", "admin2", "user1", "test1", "demo", "backup"
            ]
            users_file.write_text("\n".join(default_users))
        
        # Wordlist passwords par défaut
        passwords_file = cls.WORDLISTS_DIR / "passwords.txt"
        if not passwords_file.exists():
            default_passwords = [
                "password", "123456", "12345678", "1234", "qwerty", "abc123",
                "admin", "letmein", "welcome", "monkey", "dragon", "master",
                "sunshine", "password123", "admin123", "passw0rd", "12345", "654321"
            ]
            passwords_file.write_text("\n".join(default_passwords))
        
        # Wordlist subdomains par défaut
        subdomains_file = cls.WORDLISTS_DIR / "subdomains.txt"
        if not subdomains_file.exists():
            default_subdomains = [
                "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "webdisk",
                "ns2", "cpanel", "whm", "autodiscover", "autoconfig", "test", "dev", "staging",
                "api", "app", "admin", "dashboard", "portal", "blog", "shop", "store", "support"
            ]
            subdomains_file.write_text("\n".join(default_subdomains))
    
    @classmethod
    def get_config_path(cls) -> Path:
        """Retourne le chemin du fichier de configuration"""
        return cls.WORKSPACE_DIR / "config.json"
    
    @classmethod
    def save_config(cls, config_file: Optional[Path] = None) -> bool:
        """Sauvegarde la configuration"""
        if config_file is None:
            config_file = cls.get_config_path()
        
        config_data = {
            "version": cls.VERSION,
            "platform": cls.get_platform(),
            "language": cls.DEFAULT_LANGUAGE,
            "theme": cls.DEFAULT_THEME,
            "timeout": cls.DEFAULT_TIMEOUT,
            "threads": cls.DEFAULT_THREADS,
            "level": cls.DEFAULT_LEVEL,
            "output_format": cls.DEFAULT_OUTPUT_FORMAT,
            "metasploit": {
                "host": cls.METASPLOIT_RPC_HOST,
                "port": cls.METASPLOIT_RPC_PORT,
                "password": cls.METASPLOIT_RPC_PASSWORD,
                "ssl": cls.METASPLOIT_RPC_SSL,
                "auto_start": cls.METASPLOIT_AUTO_START
            },
            "api": {
                "host": cls.API_HOST,
                "port": cls.API_PORT,
                "debug": cls.API_DEBUG,
                "secret_key": cls.API_SECRET_KEY
            },
            "database": {
                "path": str(cls.DB_PATH)
            },
            "logging": {
                "level": cls.LOG_LEVEL,
                "max_size_mb": cls.LOG_MAX_SIZE_MB,
                "backup_count": cls.LOG_BACKUP_COUNT
            },
            "tool_paths": cls.TOOL_PATHS,
            "wordlists": {k: str(v) for k, v in cls.WORDLISTS.items()},
            "proxy": {
                "enabled": cls.proxy.enabled,
                "http": cls.proxy.http,
                "https": cls.proxy.https,
                "no_proxy": cls.proxy.no_proxy,
                "username": cls.proxy.username,
                "password": cls.proxy.password,
                "rotation": cls.proxy.rotation,
                "proxies_list": cls.proxy.proxies_list
            },
            "notifications": {
                "enabled": cls.notifications.enabled,
                "email": cls.notifications.email,
                "webhook": cls.notifications.webhook,
                "slack_webhook": cls.notifications.slack_webhook,
                "discord_webhook": cls.notifications.discord_webhook,
                "events": cls.notifications.events
            },
            "stealth": {
                "enabled": cls.stealth.enabled,
                "apt_mode": cls.stealth.apt_mode,
                "delay_min": cls.stealth.delay_min,
                "delay_max": cls.stealth.delay_max,
                "jitter": cls.stealth.jitter,
                "user_agent_rotation": cls.stealth.user_agent_rotation,
                "user_agents": cls.stealth.user_agents,
                "proxy_rotation": cls.stealth.proxy_rotation,
                "request_spoofing": cls.stealth.request_spoofing,
                "inactivity_hours_start": cls.stealth.inactivity_hours_start,
                "inactivity_hours_end": cls.stealth.inactivity_hours_end,
                "max_concurrent_requests": cls.stealth.max_concurrent_requests
            },
            "apt": {
                "enabled": cls.apt.enabled,
                "operation_duration": cls.apt.operation_duration,
                "phase_delay_min": cls.apt.phase_delay_min,
                "phase_delay_max": cls.apt.phase_delay_max,
                "persistence_methods": cls.apt.persistence_methods,
                "exfil_endpoint": cls.apt.exfil_endpoint,
                "exfil_interval": cls.apt.exfil_interval,
                "cleanup_traces": cls.apt.cleanup_traces,
                "use_tor": cls.apt.use_tor,
                "tor_proxy": cls.apt.tor_proxy
            },
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            cls._config = config_data
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    @classmethod
    def load_config(cls, config_file: Optional[Path] = None) -> bool:
        """Charge la configuration depuis un fichier"""
        if config_file is None:
            config_file = cls.get_config_path()
        
        if not config_file.exists():
            # Créer une configuration par défaut
            return cls.save_config(config_file)
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                cls._config = json.load(f)
            
            # Appliquer les valeurs chargées
            cls.VERSION = cls._config.get("version", cls.VERSION)
            cls.DEFAULT_LANGUAGE = cls._config.get("language", cls.DEFAULT_LANGUAGE)
            cls.DEFAULT_THEME = cls._config.get("theme", cls.DEFAULT_THEME)
            cls.DEFAULT_TIMEOUT = cls._config.get("timeout", cls.DEFAULT_TIMEOUT)
            cls.DEFAULT_THREADS = cls._config.get("threads", cls.DEFAULT_THREADS)
            cls.DEFAULT_LEVEL = cls._config.get("level", cls.DEFAULT_LEVEL)
            cls.DEFAULT_OUTPUT_FORMAT = cls._config.get("output_format", cls.DEFAULT_OUTPUT_FORMAT)
            
            # Configuration Metasploit
            msf = cls._config.get("metasploit", {})
            cls.METASPLOIT_RPC_HOST = msf.get("host", cls.METASPLOIT_RPC_HOST)
            cls.METASPLOIT_RPC_PORT = msf.get("port", cls.METASPLOIT_RPC_PORT)
            cls.METASPLOIT_RPC_PASSWORD = msf.get("password", cls.METASPLOIT_RPC_PASSWORD)
            cls.METASPLOIT_RPC_SSL = msf.get("ssl", cls.METASPLOIT_RPC_SSL)
            cls.METASPLOIT_AUTO_START = msf.get("auto_start", cls.METASPLOIT_AUTO_START)
            
            # Configuration API
            api = cls._config.get("api", {})
            cls.API_HOST = api.get("host", cls.API_HOST)
            cls.API_PORT = api.get("port", cls.API_PORT)
            cls.API_DEBUG = api.get("debug", cls.API_DEBUG)
            cls.API_SECRET_KEY = api.get("secret_key", cls.API_SECRET_KEY)
            
            # Configuration Database
            db = cls._config.get("database", {})
            if db.get("path"):
                cls.DB_PATH = Path(db["path"])
            
            # Configuration Logging
            logging_cfg = cls._config.get("logging", {})
            cls.LOG_LEVEL = logging_cfg.get("level", cls.LOG_LEVEL)
            cls.LOG_MAX_SIZE_MB = logging_cfg.get("max_size_mb", cls.LOG_MAX_SIZE_MB)
            cls.LOG_BACKUP_COUNT = logging_cfg.get("backup_count", cls.LOG_BACKUP_COUNT)
            
            # Chemins des outils
            tool_paths = cls._config.get("tool_paths", {})
            for tool, path in tool_paths.items():
                if tool in cls.TOOL_PATHS:
                    cls.TOOL_PATHS[tool] = path
            
            # Wordlists
            wordlists = cls._config.get("wordlists", {})
            for name, path in wordlists.items():
                if name in cls.WORDLISTS:
                    cls.WORDLISTS[name] = Path(path)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            return False
    
    @classmethod
    def _load_proxy_config(cls):
        """Charge la configuration proxy depuis le fichier"""
        proxy_config = cls._config.get("proxy", {})
        cls.proxy.enabled = proxy_config.get("enabled", False)
        cls.proxy.http = proxy_config.get("http", "")
        cls.proxy.https = proxy_config.get("https", "")
        cls.proxy.no_proxy = proxy_config.get("no_proxy", ["localhost", "127.0.0.1"])
        cls.proxy.username = proxy_config.get("username", "")
        cls.proxy.password = proxy_config.get("password", "")
        cls.proxy.rotation = proxy_config.get("rotation", False)
        cls.proxy.proxies_list = proxy_config.get("proxies_list", [])
    
    @classmethod
    def _load_notifications_config(cls):
        """Charge la configuration des notifications"""
        notif_config = cls._config.get("notifications", {})
        cls.notifications.enabled = notif_config.get("enabled", True)
        cls.notifications.email = notif_config.get("email", "")
        cls.notifications.webhook = notif_config.get("webhook", "")
        cls.notifications.slack_webhook = notif_config.get("slack_webhook", "")
        cls.notifications.discord_webhook = notif_config.get("discord_webhook", "")
        cls.notifications.events = notif_config.get("events", cls.notifications.events)
    
    @classmethod
    def _load_stealth_config(cls):
        """Charge la configuration de furtivité"""
        stealth_config = cls._config.get("stealth", {})
        cls.stealth.enabled = stealth_config.get("enabled", False)
        cls.stealth.apt_mode = stealth_config.get("apt_mode", False)
        cls.stealth.delay_min = stealth_config.get("delay_min", 1.0)
        cls.stealth.delay_max = stealth_config.get("delay_max", 5.0)
        cls.stealth.jitter = stealth_config.get("jitter", 0.3)
        cls.stealth.user_agent_rotation = stealth_config.get("user_agent_rotation", True)
        cls.stealth.user_agents = stealth_config.get("user_agents", [])
        cls.stealth.proxy_rotation = stealth_config.get("proxy_rotation", False)
        cls.stealth.request_spoofing = stealth_config.get("request_spoofing", True)
        cls.stealth.inactivity_hours_start = stealth_config.get("inactivity_hours_start", 0)
        cls.stealth.inactivity_hours_end = stealth_config.get("inactivity_hours_end", 6)
        cls.stealth.max_concurrent_requests = stealth_config.get("max_concurrent_requests", 3)
    
    @classmethod
    def _load_apt_config(cls):
        """Charge la configuration APT"""
        apt_config = cls._config.get("apt", {})
        cls.apt.enabled = apt_config.get("enabled", False)
        cls.apt.operation_duration = apt_config.get("operation_duration", 86400)
        cls.apt.phase_delay_min = apt_config.get("phase_delay_min", 300)
        cls.apt.phase_delay_max = apt_config.get("phase_delay_max", 3600)
        cls.apt.persistence_methods = apt_config.get("persistence_methods", ["webshell", "cron_job"])
        cls.apt.exfil_endpoint = apt_config.get("exfil_endpoint", "")
        cls.apt.exfil_interval = apt_config.get("exfil_interval", 3600)
        cls.apt.cleanup_traces = apt_config.get("cleanup_traces", True)
        cls.apt.use_tor = apt_config.get("use_tor", False)
        cls.apt.tor_proxy = apt_config.get("tor_proxy", "socks5://127.0.0.1:9050")
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration par clé"""
        keys = key.split('.')
        value = cls._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    @classmethod
    def set(cls, key: str, value: Any) -> bool:
        """Définit une valeur de configuration"""
        keys = key.split('.')
        target = cls._config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        return cls.save_config()
    
    @classmethod
    def check_environment(cls) -> bool:
        """Vérifie si l'environnement est correctement configuré"""
        # Créer les dossiers
        cls._create_directories()
        
        # Vérifier les outils principaux
        required_tools = ["nmap", "sqlmap"]
        missing_tools = []
        
        for tool in required_tools:
            if not cls.check_tool(tool):
                missing_tools.append(tool)
                print(f"⚠️  Outil manquant : {tool}")
        
        # Vérifier Python
        if sys.version_info < (3, 9):
            print(f"⚠️  Python 3.9+ requis (actuel: {sys.version_info.major}.{sys.version_info.minor})")
            return False
        
        # Vérifier l'espace disque
        try:
            free_space = shutil.diskusage(cls.WORKSPACE_DIR).free
            if free_space < 1024 * 1024 * 100:  # 100 MB
                print("⚠️  Espace disque faible (< 100 MB)")
        except:
            pass
        
        return len(missing_tools) == 0
    
    @classmethod
    def check_tool(cls, tool_name: str) -> bool:
        """Vérifie si un outil est installé"""
        # Vérifier dans TOOL_PATHS
        tool_path = cls.TOOL_PATHS.get(tool_name)
        if tool_path and Path(tool_path).exists():
            return True
        
        # Vérifier dans le PATH
        return shutil.which(tool_name) is not None
    
    @classmethod
    def get_tool_path(cls, tool_name: str) -> Optional[str]:
        """Retourne le chemin d'un outil s'il existe"""
        if cls.check_tool(tool_name):
            tool_path = cls.TOOL_PATHS.get(tool_name)
            if tool_path and Path(tool_path).exists():
                return tool_path
            return shutil.which(tool_name)
        return None
    
    @classmethod
    def get_platform(cls) -> str:
        """Détecte la plateforme"""
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read().lower()
                if "kali" in content:
                    return "kali"
                elif "parrot" in content:
                    return "parrot"
                elif "debian" in content:
                    return "debian"
                elif "ubuntu" in content:
                    return "ubuntu"
        except:
            pass
        
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        
        return "unknown"
    
    @classmethod
    def is_kali(cls) -> bool:
        """Vérifie si le système est Kali Linux"""
        return cls.get_platform() == "kali"
    
    @classmethod
    def is_parrot(cls) -> bool:
        """Vérifie si le système est Parrot OS"""
        return cls.get_platform() == "parrot"
    
    @classmethod
    def is_root(cls) -> bool:
        """Vérifie si l'utilisateur est root"""
        return os.geteuid() == 0
    
    @classmethod
    def get_proxy_dict(cls) -> Dict[str, str]:
        """Retourne la configuration proxy pour requests"""
        if not cls.proxy.enabled:
            return {}
        
        proxies = {}
        if cls.proxy.http:
            proxies['http'] = cls.proxy.http
        if cls.proxy.https:
            proxies['https'] = cls.proxy.https
        
        return proxies
    
    @classmethod
    def get_next_proxy(cls) -> Optional[str]:
        """Retourne le prochain proxy pour rotation"""
        if not cls.proxy.rotation or not cls.proxy.proxies_list:
            return None
        
        if not hasattr(cls, '_proxy_index'):
            cls._proxy_index = 0
        
        proxy = cls.proxy.proxies_list[cls._proxy_index]
        cls._proxy_index = (cls._proxy_index + 1) % len(cls.proxy.proxies_list)
        
        return proxy
    
    @classmethod
    def get_user_agents(cls) -> List[str]:
        """Retourne la liste des User-Agents"""
        if cls.stealth.user_agents:
            return cls.stealth.user_agents
        
        # User-Agents par défaut
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        ]
    
    @classmethod
    def get_session_config(cls) -> Dict[str, Any]:
        """Retourne la configuration pour les sessions requests"""
        config = {
            "timeout": cls.DEFAULT_TIMEOUT,
            "verify": False,  # Désactiver la vérification SSL par défaut
            "proxies": cls.get_proxy_dict()
        }
        
        if cls.proxy.username and cls.proxy.password:
            config["auth"] = (cls.proxy.username, cls.proxy.password)
        
        return config
    
    @classmethod
    def reset_to_defaults(cls) -> bool:
        """Réinitialise la configuration aux valeurs par défaut"""
        cls.VERSION = "2.0.0"
        cls.DEFAULT_TIMEOUT = 300
        cls.DEFAULT_THREADS = 10
        cls.DEFAULT_LEVEL = 2
        cls.DEFAULT_LANGUAGE = "fr_FR"
        cls.DEFAULT_THEME = "auto"
        
        cls.METASPLOIT_RPC_HOST = "127.0.0.1"
        cls.METASPLOIT_RPC_PORT = 55553
        cls.METASPLOIT_RPC_PASSWORD = "RedForge2024"
        cls.METASPLOIT_RPC_SSL = False
        
        cls.proxy = ProxyConfig()
        cls.notifications = NotificationConfig()
        cls.stealth = StealthConfig()
        cls.apt = APTConfig()
        
        return cls.save_config()
    
    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        """Retourne un résumé de la configuration"""
        return {
            "version": cls.VERSION,
            "platform": cls.get_platform(),
            "is_root": cls.is_root(),
            "workspace": str(cls.WORKSPACE_DIR),
            "tools_available": {
                tool: cls.check_tool(tool) for tool in list(cls.TOOL_PATHS.keys())[:10]
            },
            "proxy_enabled": cls.proxy.enabled,
            "proxy_rotation": cls.proxy.rotation,
            "stealth_enabled": cls.stealth.enabled,
            "apt_mode": cls.apt.enabled,
            "notifications_enabled": cls.notifications.enabled,
            "api_endpoint": f"http://{cls.API_HOST}:{cls.API_PORT}",
            "cache_dir": str(cls.CACHE_DIR),
            "loot_dir": str(cls.LOOT_DIR)
        }
    
    @classmethod
    def get_workspace_info(cls) -> Dict[str, Any]:
        """Retourne les informations sur l'espace de travail"""
        info = {
            "workspace_dir": str(cls.WORKSPACE_DIR),
            "size_mb": 0,
            "file_count": 0
        }
        
        try:
            total_size = 0
            file_count = 0
            for path in cls.WORKSPACE_DIR.rglob("*"):
                if path.is_file():
                    total_size += path.stat().st_size
                    file_count += 1
            info["size_mb"] = round(total_size / (1024 * 1024), 2)
            info["file_count"] = file_count
        except:
            pass
        
        return info
    
    @classmethod
    def cleanup_workspace(cls, days_old: int = 30) -> int:
        """Nettoie l'espace de travail (fichiers anciens)"""
        import time
        deleted_count = 0
        cutoff_time = time.time() - (days_old * 86400)
        
        for path in cls.WORKSPACE_DIR.rglob("*"):
            if path.is_file():
                if path.stat().st_mtime < cutoff_time:
                    try:
                        path.unlink()
                        deleted_count += 1
                    except:
                        pass
        
        return deleted_count


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de la configuration RedForge")
    print("=" * 60)
    
    # Initialiser
    RedForgeConfig.initialize()
    
    # Afficher le résumé
    summary = RedForgeConfig.get_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Afficher les informations workspace
    print("\n" + "=" * 40)
    print("Espace de travail")
    print("=" * 40)
    workspace_info = RedForgeConfig.get_workspace_info()
    for key, value in workspace_info.items():
        print(f"{key}: {value}")
    
    # Tester les get/set
    print("\n" + "=" * 40)
    print("Test des get/set")
    print("=" * 40)
    
    RedForgeConfig.set("test.value", 42)
    print(f"test.value = {RedForgeConfig.get('test.value')}")
    
    # Sauvegarder
    RedForgeConfig.save_config()
    print("\n✅ Configuration sauvegardée")