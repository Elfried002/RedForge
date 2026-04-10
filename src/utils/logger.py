#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de journalisation pour RedForge
Gère les logs de l'application avec support furtif et APT
Version avec rotation, compression et export avancés
"""

import os
import sys
import json
import gzip
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from enum import Enum


# ============================================
# Classes utilitaires pour la console (fallback)
# ============================================

class ConsoleColors:
    """Couleurs pour la console"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    RESET = '\033[0m'


class SimpleConsole:
    """Console simple pour le logging (fallback si color_output n'existe pas)"""
    
    @staticmethod
    def print_info(message: str):
        print(f"{ConsoleColors.CYAN}[i]{ConsoleColors.RESET} {message}")
    
    @staticmethod
    def print_warning(message: str):
        print(f"{ConsoleColors.YELLOW}[!]{ConsoleColors.RESET} {message}")
    
    @staticmethod
    def print_error(message: str):
        print(f"{ConsoleColors.RED}[-]{ConsoleColors.RESET} {message}")
    
    @staticmethod
    def print_success(message: str):
        print(f"{ConsoleColors.GREEN}[+]{ConsoleColors.RESET} {message}")
    
    @staticmethod
    def apt(message: str):
        print(f"{ConsoleColors.MAGENTA}[APT]{ConsoleColors.RESET} {message}")
    
    @staticmethod
    def stealth(message: str):
        print(f"{ConsoleColors.BLUE}[🕵️]{ConsoleColors.RESET} {message}")


# Tentative d'import du vrai module color_output
try:
    from src.utils.color_output import console
except ImportError:
    console = SimpleConsole()


class LogLevel(Enum):
    """Niveaux de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    APT = "APT"
    STEALTH = "STEALTH"


class Logger:
    """Gestionnaire de logs avancé pour RedForge avec support furtif"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Logger._initialized:
            return
        Logger._initialized = True
        
        self.log_dir = Path.home() / ".RedForge" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.log_dir / f"redforge_{datetime.now().strftime('%Y%m%d')}.log"
        self.json_log_file = self.log_dir / f"redforge_{datetime.now().strftime('%Y%m%d')}.json"
        self.apt_log_file = self.log_dir / f"apt_{datetime.now().strftime('%Y%m%d')}.log"
        self.error_log_file = self.log_dir / f"error_{datetime.now().strftime('%Y%m%d')}.log"
        
        self.stealth_mode = False
        self.apt_mode = False
        self.log_rotation_days = 7
        self.max_log_size_mb = 10
        
        self.setup_logger()
        self._cleanup_old_logs()
    
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif (logs minimisés)"""
        self.stealth_mode = enabled
        if enabled:
            self.info("Mode furtif activé - Logs minimisés")
    
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT (logs discrets)"""
        self.apt_mode = enabled
        if enabled:
            self.apt("Mode APT activé - Logs ultra discrets")
    
    def setup_logger(self):
        """Configure le logger avec rotation"""
        self.logger = logging.getLogger('RedForge')
        self.logger.setLevel(logging.DEBUG)
        
        # Éviter les doublons de handlers
        if self.logger.handlers:
            return
        
        # Format pour les logs texte
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler pour fichier texte avec rotation
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_log_size_mb * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler pour erreurs séparé
        error_handler = RotatingFileHandler(
            self.error_log_file,
            maxBytes=self.max_log_size_mb * 1024 * 1024,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
    
    def _log(self, level: str, message: str, console_output: bool = True, **kwargs):
        """
        Log interne
        
        Args:
            level: Niveau de log
            message: Message
            console_output: Afficher dans la console
            **kwargs: Données supplémentaires
        """
        # Ne pas logger en mode silencieux
        if self.apt_mode and level not in ['APT', 'STEALTH', 'ERROR', 'CRITICAL']:
            console_output = False
        
        if not self.stealth_mode or level in ['ERROR', 'CRITICAL']:
            log_level = level.lower()
            if log_level == 'success':
                log_level = 'info'
            getattr(self.logger, log_level)(message)
        
        # Log JSON pour analyse
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'data': kwargs,
            'stealth_mode': self.stealth_mode,
            'apt_mode': self.apt_mode
        }
        
        try:
            with open(self.json_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except:
            pass
        
        # Log APT séparé
        if level == 'APT' and self.apt_mode:
            try:
                with open(self.apt_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{log_entry['timestamp']}] {message}\n")
            except:
                pass
        
        # Affichage console coloré
        if console_output and not self.apt_mode:
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
    
    def debug(self, message: str, **kwargs):
        self._log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log('ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log('CRITICAL', message, **kwargs)
    
    def success(self, message: str, **kwargs):
        self._log('SUCCESS', message, **kwargs)
    
    def apt(self, message: str, **kwargs):
        """Log pour opérations APT (discret)"""
        self._log('APT', message, console_output=False, **kwargs)
    
    def stealth(self, message: str, **kwargs):
        """Log pour mode furtif (très discret)"""
        self._log('STEALTH', message, console_output=False, **kwargs)
    
    def log_attack(self, attack_name: str, target: str, result: Dict[str, Any]):
        """
        Log une attaque
        
        Args:
            attack_name: Nom de l'attaque
            target: Cible
            result: Résultat de l'attaque
        """
        if self.apt_mode:
            self.apt(f"Attack: {attack_name} on {target}", event_type='attack')
        else:
            self.info(
                f"Attaque {attack_name} sur {target}",
                event_type='attack',
                attack=attack_name,
                target=target,
                result=result
            )
    
    def log_vulnerability(self, vulnerability: Dict[str, Any]):
        """
        Log une vulnérabilité trouvée
        
        Args:
            vulnerability: Détails de la vulnérabilité
        """
        severity = vulnerability.get('severity', 'unknown')
        
        if severity.upper() in ['CRITICAL', 'HIGH']:
            level = 'WARNING'
        else:
            level = 'INFO'
        
        getattr(self, level.lower())(
            f"Vulnérabilité: {vulnerability.get('type', 'unknown')} - {severity}",
            event_type='vulnerability',
            vulnerability=vulnerability
        )
    
    def log_session(self, action: str, session_id: str, target: str):
        """
        Log une action de session
        
        Args:
            action: Action (create, close, interact)
            session_id: ID de session
            target: Cible
        """
        if self.apt_mode:
            self.apt(f"Session {action}: {session_id}", event_type='session')
        else:
            self.info(
                f"Session {action}: {session_id} sur {target}",
                event_type='session',
                action=action,
                session_id=session_id,
                target=target
            )
    
    def log_phase(self, phase: str, status: str, duration: float = 0):
        """
        Log une phase d'exécution
        
        Args:
            phase: Nom de la phase
            status: Statut (start, complete, error)
            duration: Durée en secondes
        """
        if status == 'start':
            self.info(f"Début phase: {phase}", event_type='phase', phase=phase, status=status)
        elif status == 'complete':
            self.success(f"Phase {phase} terminée en {duration:.1f}s", event_type='phase', phase=phase, status=status, duration=duration)
        elif status == 'error':
            self.error(f"Phase {phase} échouée", event_type='phase', phase=phase, status=status)
    
    def log_apt_operation(self, operation_id: str, operation_name: str, 
                          status: str, details: Dict = None):
        """
        Log une opération APT
        
        Args:
            operation_id: ID de l'opération
            operation_name: Nom de l'opération
            status: Statut
            details: Détails supplémentaires
        """
        self.apt(
            f"APT Operation: {operation_name} ({operation_id}) - {status}",
            event_type='apt_operation',
            operation_id=operation_id,
            operation_name=operation_name,
            status=status,
            details=details or {}
        )
    
    def get_logs(self, lines: int = 100, level: Optional[str] = None, 
                 start_date: Optional[datetime] = None) -> List[str]:
        """
        Récupère les logs récents
        
        Args:
            lines: Nombre de lignes
            level: Niveau de log filtré
            start_date: Date de début
        """
        logs = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_logs = f.readlines()
                
                for log_line in all_logs[-lines:]:
                    if level and level.upper() not in log_line:
                        continue
                    
                    if start_date:
                        try:
                            log_date_str = log_line.split(' - ')[0]
                            log_date = datetime.strptime(log_date_str, '%Y-%m-%d %H:%M:%S')
                            if log_date < start_date:
                                continue
                        except:
                            pass
                    
                    logs.append(log_line.strip())
        except:
            pass
        
        return logs
    
    def get_json_logs(self, limit: int = 100, level: Optional[str] = None) -> List[Dict]:
        """
        Récupère les logs JSON récents
        
        Args:
            limit: Nombre maximum de logs
            level: Niveau de log filtré
        """
        logs = []
        
        try:
            with open(self.json_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if len(logs) >= limit:
                        break
                    try:
                        log_entry = json.loads(line)
                        if level and log_entry.get('level') != level.upper():
                            continue
                        logs.append(log_entry)
                    except:
                        continue
        except:
            pass
        
        return logs
    
    def get_apt_logs(self, limit: int = 100) -> List[str]:
        """
        Récupère les logs APT
        
        Args:
            limit: Nombre maximum de logs
        """
        logs = []
        
        try:
            with open(self.apt_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if len(logs) >= limit:
                        break
                    logs.append(line.strip())
        except:
            pass
        
        return logs
    
    def clear_logs(self, days_old: int = 30):
        """
        Efface les logs anciens
        
        Args:
            days_old: Âge maximum des logs à conserver
        """
        try:
            cutoff = datetime.now() - timedelta(days=days_old)
            
            for log_file in self.log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff.timestamp():
                    # Compresser avant suppression
                    if log_file.stat().st_size > 0:
                        with open(log_file, 'rb') as f_in:
                            with gzip.open(f"{log_file}.gz", 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                    log_file.unlink()
            
            for json_file in self.log_dir.glob("*.json"):
                if json_file.stat().st_mtime < cutoff.timestamp():
                    json_file.unlink()
            
            print(f"[i] Logs antérieurs à {days_old} jours nettoyés")
        except Exception as e:
            self.error(f"Erreur nettoyage logs: {e}")
    
    def _cleanup_old_logs(self):
        """Nettoie les logs trop anciens"""
        self.clear_logs(self.log_rotation_days)
    
    def export_logs(self, output_file: str, format: str = "json", 
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> bool:
        """
        Exporte les logs vers un fichier
        
        Args:
            output_file: Fichier de sortie
            format: Format (json, csv, txt)
            start_date: Date de début
            end_date: Date de fin
        """
        try:
            logs = self.get_json_logs(limit=10000)
            
            # Filtrer par date
            if start_date or end_date:
                filtered_logs = []
                for log in logs:
                    try:
                        log_date = datetime.fromisoformat(log['timestamp'])
                        if start_date and log_date < start_date:
                            continue
                        if end_date and log_date > end_date:
                            continue
                        filtered_logs.append(log)
                    except:
                        continue
                logs = filtered_logs
            
            if format == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
            
            elif format == "csv":
                import csv
                with open(output_file, 'w', encoding='utf-8', newline='') as f:
                    if logs:
                        writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                        writer.writeheader()
                        writer.writerows(logs)
            
            elif format == "txt":
                with open(output_file, 'w', encoding='utf-8') as f:
                    for log in logs:
                        f.write(f"[{log['timestamp']}] {log['level']}: {log['message']}\n")
            
            self.success(f"Logs exportés vers {output_file}")
            return True
            
        except Exception as e:
            self.error(f"Erreur export logs: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques des logs
        
        Returns:
            Dictionnaire des statistiques
        """
        stats = {
            'log_dir': str(self.log_dir),
            'log_file_size': self.log_file.stat().st_size if self.log_file.exists() else 0,
            'json_log_file_size': self.json_log_file.stat().st_size if self.json_log_file.exists() else 0,
            'apt_log_file_size': self.apt_log_file.stat().st_size if self.apt_log_file.exists() else 0,
            'error_log_file_size': self.error_log_file.stat().st_size if self.error_log_file.exists() else 0,
            'stealth_mode': self.stealth_mode,
            'apt_mode': self.apt_mode,
            'log_rotation_days': self.log_rotation_days,
            'max_log_size_mb': self.max_log_size_mb
        }
        
        # Compter les logs par niveau
        log_counts = {'DEBUG': 0, 'INFO': 0, 'SUCCESS': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0, 'APT': 0, 'STEALTH': 0}
        
        try:
            with open(self.json_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log = json.loads(line)
                        level = log.get('level', 'INFO')
                        if level in log_counts:
                            log_counts[level] += 1
                    except:
                        pass
        except:
            pass
        
        stats['log_counts'] = log_counts
        stats['total_logs'] = sum(log_counts.values())
        
        return stats


# ============================================
# FONCTIONS D'EXPORT POUR COMPATIBILITÉ
# ============================================

def get_logger(name: str = "RedForge") -> logging.Logger:
    """
    Récupère un logger standard (compatible avec l'ancien code).
    
    Args:
        name: Nom du logger
    
    Returns:
        Instance du logger logging.Logger
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def get_redforge_logger() -> Logger:
    """
    Récupère l'instance du logger RedForge avancé.
    
    Returns:
        Instance du logger RedForge
    """
    return logger


# Instance globale
logger = Logger()


# ============================================
# TESTS
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Test du logger RedForge v2.0")
    print("=" * 60)
    
    # Test du logger standard
    std_logger = get_logger("Test")
    std_logger.info("Test logger standard")
    
    # Test du logger avancé
    logger.info("Test d'information")
    logger.warning("Test d'avertissement")
    logger.error("Test d'erreur")
    logger.success("Test de succès")
    
    logger.log_attack("SQL Injection", "example.com", {"success": True})
    logger.log_vulnerability({"type": "XSS", "severity": "HIGH"})
    logger.log_phase("footprint", "start")
    logger.log_phase("footprint", "complete", duration=5.5)
    
    # Mode APT
    logger.set_apt_mode(True)
    logger.apt("Message APT discret")
    logger.log_apt_operation("op_123", "Target Recon", "started")
    logger.set_apt_mode(False)
    
    # Statistiques
    stats = logger.get_statistics()
    print(f"\n📊 Statistiques: {stats['total_logs']} logs, mode APT: {stats['apt_mode']}")
    
    # Export
    logger.export_logs("/tmp/logs_export.json", format="json")
    
    print("\n✅ Tests terminés")