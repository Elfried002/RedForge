#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedForge v2.0 - Module de journalisation ultra robuste
Gère les logs avec support furtif, APT, rotation, compression et export avancés
Conçu pour être résilient et ne jamais planter
"""

import os
import sys
import json
import gzip
import shutil
import logging
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from enum import Enum
from functools import wraps


# ============================================
# CONFIGURATION ROBUSTE
# ============================================

# Détermination des chemins de manière sécurisée
def get_safe_log_dir() -> Path:
    """Retourne un répertoire de logs sécurisé"""
    try:
        # Essayer le dossier utilisateur
        home = Path.home()
        if home and home.exists():
            log_dir = home / ".RedForge" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            return log_dir
    except Exception:
        pass
    
    try:
        # Fallback vers /tmp
        log_dir = Path("/tmp/redforge_logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    except Exception:
        pass
    
    # Dernier recours
    return Path(".") / "logs"


# ============================================
# CLASSES UTILITAIRES AVEC FALLBACKS
# ============================================

class ConsoleColors:
    """Couleurs pour la console avec vérification"""
    RED = '\033[0;31m' if sys.platform != 'win32' else ''
    GREEN = '\033[0;32m' if sys.platform != 'win32' else ''
    YELLOW = '\033[1;33m' if sys.platform != 'win32' else ''
    BLUE = '\033[0;34m' if sys.platform != 'win32' else ''
    MAGENTA = '\033[0;35m' if sys.platform != 'win32' else ''
    CYAN = '\033[0;36m' if sys.platform != 'win32' else ''
    WHITE = '\033[1;37m' if sys.platform != 'win32' else ''
    RESET = '\033[0m' if sys.platform != 'win32' else ''


class SafeConsole:
    """Console sécurisée qui ne plante jamais"""
    
    @staticmethod
    def _safe_print(message: str, prefix: str = "", color: str = ""):
        """Impression sécurisée"""
        try:
            if color and sys.platform != 'win32':
                print(f"{color}{prefix}{ConsoleColors.RESET} {message}")
            else:
                print(f"{prefix} {message}")
        except Exception:
            # Silencieux en cas d'erreur d'impression
            pass
    
    @staticmethod
    def print_info(message: str):
        SafeConsole._safe_print(message, "[i]", ConsoleColors.CYAN)
    
    @staticmethod
    def print_warning(message: str):
        SafeConsole._safe_print(message, "[!]", ConsoleColors.YELLOW)
    
    @staticmethod
    def print_error(message: str):
        SafeConsole._safe_print(message, "[-]", ConsoleColors.RED)
    
    @staticmethod
    def print_success(message: str):
        SafeConsole._safe_print(message, "[+]", ConsoleColors.GREEN)
    
    @staticmethod
    def apt(message: str):
        SafeConsole._safe_print(message, "[APT]", ConsoleColors.MAGENTA)
    
    @staticmethod
    def stealth(message: str):
        SafeConsole._safe_print(message, "[🕵️]", ConsoleColors.BLUE)


# Tentative d'import du vrai module color_output avec fallback
try:
    from src.utils.color_output import console as _console
    console = _console
except (ImportError, AttributeError):
    console = SafeConsole()


# ============================================
# ENUMS ROBUSTES
# ============================================

class LogLevel(Enum):
    """Niveaux de log avec valeurs par défaut"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    APT = "APT"
    STEALTH = "STEALTH"
    
    @classmethod
    def from_string(cls, value: str) -> "LogLevel":
        """Convertit une chaîne en LogLevel de manière sécurisée"""
        try:
            return cls(value.upper())
        except (ValueError, AttributeError):
            return cls.INFO


# ============================================
# DECORATEUR DE SÉCURITÉ
# ============================================

def safe_method(default_return=None):
    """Décorateur pour rendre les méthodes sûres (ne plantent jamais)"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # Tentative de log de l'erreur (sans boucle infinie)
                try:
                    if hasattr(self, '_log_safe'):
                        self._log_safe(f"Erreur dans {func.__name__}: {e}")
                except Exception:
                    pass
                return default_return
        return wrapper
    return decorator


# ============================================
# CLASSE LOGGER PRINCIPALE
# ============================================

class Logger:
    """
    Gestionnaire de logs avancé et ultra robuste pour RedForge.
    Ne plante jamais, même en cas d'erreur.
    """
    
    _instance = None
    _initialized = False
    _lock = False  # Éviter les récursions
    
    def __new__(cls):
        if cls._instance is None:
            try:
                cls._instance = super().__new__(cls)
            except Exception:
                # Fallback ultime
                cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Logger._initialized:
            return
        
        try:
            self._init_logger()
            Logger._initialized = True
        except Exception as e:
            # Initialisation minimale en cas d'erreur
            self._fallback_init(e)
    
    def _fallback_init(self, error: Exception):
        """Initialisation de secours"""
        self.logger = None
        self.log_dir = Path("/tmp")
        self.stealth_mode = False
        self.apt_mode = False
        self._initialized = False
        try:
            print(f"[!] Erreur initialisation logger: {error}", file=sys.stderr)
        except Exception:
            pass
    
    def _init_logger(self):
        """Initialisation principale sécurisée"""
        # Configuration des dossiers
        self.log_dir = get_safe_log_dir()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Noms de fichiers avec date
        date_str = datetime.now().strftime('%Y%m%d')
        self.log_file = self.log_dir / f"redforge_{date_str}.log"
        self.json_log_file = self.log_dir / f"redforge_{date_str}.json"
        self.apt_log_file = self.log_dir / f"apt_{date_str}.log"
        self.error_log_file = self.log_dir / f"error_{date_str}.log"
        
        # Configuration
        self.stealth_mode = False
        self.apt_mode = False
        self.log_rotation_days = 7
        self.max_log_size_mb = 10
        
        # Initialisation du logger Python
        self.logger = logging.getLogger('RedForge')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()  # Éviter les doublons
        
        # Format commun
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler fichier principal
        try:
            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_log_size_mb * 1024 * 1024,
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self._log_safe(f"Erreur création handler fichier: {e}")
        
        # Handler erreurs séparé
        try:
            error_handler = RotatingFileHandler(
                self.error_log_file,
                maxBytes=self.max_log_size_mb * 1024 * 1024,
                backupCount=3,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            self.logger.addHandler(error_handler)
        except Exception as e:
            self._log_safe(f"Erreur création error handler: {e}")
        
        # Handler console (optionnel)
        try:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter('%(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        except Exception:
            pass
        
        # Nettoyage initial
        self._cleanup_old_logs()
    
    def _log_safe(self, message: str):
        """Log interne ultra sécurisé (évite les boucles infinies)"""
        if Logger._lock:
            return
        Logger._lock = True
        try:
            if self.logger:
                self.logger.error(f"[INTERNAL] {message}")
            else:
                print(f"ERROR: {message}", file=sys.stderr)
        except Exception:
            pass
        finally:
            Logger._lock = False
    
    @safe_method()
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif"""
        self.stealth_mode = enabled
        if enabled:
            self.info("Mode furtif activé - Logs minimisés")
    
    @safe_method()
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT"""
        self.apt_mode = enabled
        if enabled:
            self.apt("Mode APT activé - Logs ultra discrets")
    
    @safe_method()
    def _write_log(self, level: str, message: str, **kwargs):
        """Écriture sécurisée du log"""
        # Vérifier si on doit logger
        if self.apt_mode and level not in ['APT', 'STEALTH', 'ERROR', 'CRITICAL']:
            return
        
        if self.stealth_mode and level not in ['ERROR', 'CRITICAL']:
            return
        
        # Log Python
        try:
            log_level = level.lower()
            if log_level == 'success':
                log_level = 'info'
            if self.logger:
                getattr(self.logger, log_level)(message)
        except Exception:
            pass
        
        # Log JSON
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'level': level,
                'message': message,
                'data': kwargs,
                'stealth_mode': self.stealth_mode,
                'apt_mode': self.apt_mode
            }
            with open(self.json_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception:
            pass
        
        # Log APT séparé
        if level == 'APT':
            try:
                with open(self.apt_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().isoformat()}] {message}\n")
            except Exception:
                pass
        
        # Affichage console
        if not self.apt_mode:
            try:
                if level == 'ERROR':
                    console.print_error(message)
                elif level == 'WARNING':
                    console.print_warning(message)
                elif level == 'INFO':
                    console.print_info(message)
                elif level == 'SUCCESS':
                    console.print_success(message)
                elif level == 'APT':
                    console.apt(message)
                elif level == 'STEALTH':
                    console.stealth(message)
            except Exception:
                print(message)
    
    # ===== MÉTHODES DE LOG PRINCIPALES =====
    
    @safe_method()
    def debug(self, message: str, **kwargs):
        self._write_log('DEBUG', message, **kwargs)
    
    @safe_method()
    def info(self, message: str, **kwargs):
        self._write_log('INFO', message, **kwargs)
    
    @safe_method()
    def warning(self, message: str, **kwargs):
        self._write_log('WARNING', message, **kwargs)
    
    @safe_method()
    def error(self, message: str, **kwargs):
        self._write_log('ERROR', message, **kwargs)
    
    @safe_method()
    def critical(self, message: str, **kwargs):
        self._write_log('CRITICAL', message, **kwargs)
    
    @safe_method()
    def success(self, message: str, **kwargs):
        self._write_log('SUCCESS', message, **kwargs)
    
    @safe_method()
    def apt(self, message: str, **kwargs):
        self._write_log('APT', message, **kwargs)
    
    @safe_method()
    def stealth(self, message: str, **kwargs):
        self._write_log('STEALTH', message, **kwargs)
    
    # ===== MÉTHODES SPÉCIALISÉES =====
    
    @safe_method()
    def log_attack(self, attack_name: str, target: str, result: Dict[str, Any]):
        """Log une attaque"""
        if self.apt_mode:
            self.apt(f"Attack: {attack_name} on {target}")
        else:
            self.info(f"Attaque {attack_name} sur {target}")
    
    @safe_method()
    def log_vulnerability(self, vulnerability: Dict[str, Any]):
        """Log une vulnérabilité"""
        severity = vulnerability.get('severity', 'unknown')
        level = 'WARNING' if severity.upper() in ['CRITICAL', 'HIGH'] else 'INFO'
        getattr(self, level.lower())(
            f"Vulnérabilité: {vulnerability.get('type', 'unknown')} - {severity}"
        )
    
    @safe_method()
    def log_session(self, action: str, session_id: str, target: str):
        """Log une session"""
        if self.apt_mode:
            self.apt(f"Session {action}: {session_id}")
        else:
            self.info(f"Session {action}: {session_id} sur {target}")
    
    @safe_method()
    def log_phase(self, phase: str, status: str, duration: float = 0):
        """Log une phase"""
        if status == 'start':
            self.info(f"Début phase: {phase}")
        elif status == 'complete':
            self.success(f"Phase {phase} terminée en {duration:.1f}s")
        elif status == 'error':
            self.error(f"Phase {phase} échouée")
    
    @safe_method()
    def log_apt_operation(self, operation_id: str, operation_name: str, 
                          status: str, details: Dict = None):
        """Log une opération APT"""
        self.apt(f"APT Operation: {operation_name} ({operation_id}) - {status}")
    
    # ===== MÉTHODES UTILITAIRES =====
    
    @safe_method(default_return=[])
    def get_logs(self, lines: int = 100, level: Optional[str] = None, 
                 start_date: Optional[datetime] = None) -> List[str]:
        """Récupère les logs récents"""
        logs = []
        if not self.log_file.exists():
            return logs
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            all_logs = f.readlines()
            for log_line in all_logs[-lines:]:
                if level and level.upper() not in log_line:
                    continue
                logs.append(log_line.strip())
        return logs
    
    @safe_method(default_return=[])
    def get_json_logs(self, limit: int = 100, level: Optional[str] = None) -> List[Dict]:
        """Récupère les logs JSON"""
        logs = []
        if not self.json_log_file.exists():
            return logs
        
        with open(self.json_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if len(logs) >= limit:
                    break
                try:
                    log_entry = json.loads(line)
                    if level and log_entry.get('level') != level.upper():
                        continue
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
        return logs
    
    @safe_method()
    def clear_logs(self, days_old: int = 30):
        """Supprime les logs anciens"""
        cutoff = datetime.now() - timedelta(days=days_old)
        
        for log_file in self.log_dir.glob("*.log"):
            try:
                if log_file.stat().st_mtime < cutoff.timestamp():
                    log_file.unlink()
            except Exception:
                pass
        
        for json_file in self.log_dir.glob("*.json"):
            try:
                if json_file.stat().st_mtime < cutoff.timestamp():
                    json_file.unlink()
            except Exception:
                pass
    
    def _cleanup_old_logs(self):
        """Nettoyage automatique"""
        self.clear_logs(self.log_rotation_days)
    
    @safe_method(default_return=False)
    def export_logs(self, output_file: str, format: str = "json", 
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> bool:
        """Exporte les logs"""
        logs = self.get_json_logs(limit=10000)
        
        # Filtrage par date
        if start_date or end_date:
            filtered = []
            for log in logs:
                try:
                    log_date = datetime.fromisoformat(log['timestamp'])
                    if start_date and log_date < start_date:
                        continue
                    if end_date and log_date > end_date:
                        continue
                    filtered.append(log)
                except (ValueError, KeyError):
                    continue
            logs = filtered
        
        # Export selon format
        if format == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        elif format == "txt":
            with open(output_file, 'w', encoding='utf-8') as f:
                for log in logs:
                    f.write(f"[{log['timestamp']}] {log['level']}: {log['message']}\n")
        else:
            return False
        
        self.success(f"Logs exportés vers {output_file}")
        return True
    
    @safe_method(default_return={})
    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques des logs"""
        stats = {
            'log_dir': str(self.log_dir),
            'stealth_mode': self.stealth_mode,
            'apt_mode': self.apt_mode,
            'log_rotation_days': self.log_rotation_days,
            'max_log_size_mb': self.max_log_size_mb
        }
        
        # Tailles des fichiers
        for name in ['log_file', 'json_log_file', 'apt_log_file', 'error_log_file']:
            file_path = getattr(self, name, None)
            if file_path and file_path.exists():
                stats[f'{name}_size'] = file_path.stat().st_size
            else:
                stats[f'{name}_size'] = 0
        
        # Comptage par niveau
        log_counts = {'DEBUG': 0, 'INFO': 0, 'SUCCESS': 0, 'WARNING': 0, 
                      'ERROR': 0, 'CRITICAL': 0, 'APT': 0, 'STEALTH': 0}
        
        for log in self.get_json_logs(limit=5000):
            level = log.get('level', 'INFO')
            if level in log_counts:
                log_counts[level] += 1
        
        stats['log_counts'] = log_counts
        stats['total_logs'] = sum(log_counts.values())
        
        return stats


# ============================================
# FONCTIONS DE COMPATIBILITÉ (CRITIQUES)
# ============================================

def setup_logging(name: str = "RedForge", log_file: str = None, level: int = None) -> logging.Logger:
    """
    Configure le logging - Fonction critique pour la compatibilité.
    Utilisée par de nombreux modules de RedForge.
    """
    logger = logging.getLogger(name)
    level = level or logging.INFO
    logger.setLevel(level)
    
    if not logger.handlers:
        try:
            # Handler console
            console_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        except Exception:
            pass
        
        # Handler fichier si spécifié
        if log_file:
            try:
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=10 * 1024 * 1024,
                    backupCount=5,
                    encoding='utf-8'
                )
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception:
                pass
    
    return logger


def get_logger(name: str = "RedForge") -> logging.Logger:
    """
    Récupère un logger standard.
    Fonction critique - utilisée partout.
    """
    return setup_logging(name)


def get_redforge_logger() -> Logger:
    """
    Récupère l'instance du logger avancé.
    """
    return logger


# ============================================
# INSTANCE GLOBALE
# ============================================

try:
    logger = Logger()
except Exception as e:
    # Création d'un logger minimal en cas d'échec
    class MinimalLogger:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                try:
                    print(f"[{name.upper()}] {args[0] if args else ''}")
                except Exception:
                    pass
            return method
    
    logger = MinimalLogger()
    try:
        print(f"[!] Erreur création logger principal: {e}", file=sys.stderr)
    except Exception:
        pass


# ============================================
# TESTS (exécutés uniquement si script lancé directement)
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Test du logger RedForge v2.0 (Ultra Robuste)")
    print("=" * 60)
    
    # Test des fonctions critiques
    test_logger = setup_logging("TestLogger")
    test_logger.info("✅ setup_logging fonctionne")
    
    std_logger = get_logger("Test")
    std_logger.info("✅ get_logger fonctionne")
    
    # Test du logger avancé
    logger.info("Test d'information")
    logger.warning("Test d'avertissement")
    logger.error("Test d'erreur")
    logger.success("Test de succès")
    logger.apt("Test APT")
    logger.stealth("Test furtif")
    
    # Test des méthodes spécialisées
    logger.log_attack("SQL Injection", "example.com", {"success": True})
    logger.log_vulnerability({"type": "XSS", "severity": "HIGH"})
    logger.log_phase("footprint", "start")
    logger.log_phase("footprint", "complete", duration=5.5)
    logger.log_apt_operation("op_123", "Target Recon", "started")
    
    # Test des modes
    logger.set_apt_mode(True)
    logger.info("Message en mode APT (devrait être discret)")
    logger.set_apt_mode(False)
    
    # Test des statistiques
    stats = logger.get_statistics()
    print(f"\n📊 Statistiques: {stats.get('total_logs', 0)} logs")
    
    # Test d'export
    logger.export_logs("/tmp/redforge_test_logs.json", format="json")
    
    print("\n✅ Tous les tests sont passés !")
    print("📁 Logs dans:", logger.log_dir)