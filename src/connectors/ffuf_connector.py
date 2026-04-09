#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour ffuf - Outil de fuzzing web rapide
Version avec support furtif, APT et fuzzing avancé
"""

import re
import json
import random
from typing import Dict, Any, List, Optional
from pathlib import Path
from urllib.parse import urlparse

from src.connectors.base_connector import BaseConnector


class FfufConnector(BaseConnector):
    """Connecteur avancé pour ffuf avec support furtif"""
    
    def __init__(self, tool_path: Optional[str] = None):
        """
        Initialise le connecteur ffuf
        
        Args:
            tool_path: Chemin personnalisé vers l'exécutable ffuf
        """
        super().__init__(tool_path)
        self.default_wordlists = {
            "directory": "/usr/share/wordlists/dirb/common.txt",
            "subdomain": "/usr/share/wordlists/subdomains.txt",
            "parameter": "/usr/share/wordlists/parameters.txt",
            "extension": "/usr/share/wordlists/extensions.txt"
        }
    
    def _find_tool(self) -> Optional[str]:
        """Trouve l'exécutable ffuf"""
        import shutil
        
        paths = [
            "ffuf",
            "/usr/bin/ffuf",
            "/usr/local/bin/ffuf",
            "/opt/ffuf/ffuf",
            "/opt/ffuf/ffuf_linux"
        ]
        
        for path in paths:
            if path and shutil.which(path):
                return path
        
        return None
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute un fuzzing sur la cible
        
        Args:
            target: URL cible avec mot-clé FUZZ
            **kwargs:
                - wordlist: Fichier wordlist
                - extensions: Extensions à tester
                - threads: Nombre de threads
                - delay: Délai entre les requêtes
                - recursion: Scan récursif
                - recursion_depth: Profondeur de récursion
                - headers: Headers HTTP personnalisés
                - cookies: Cookies à utiliser
                - methods: Méthodes HTTP à tester
                - data: Données POST pour fuzzing
                - filter_status: Codes à filtrer
                - filter_size: Tailles à filtrer
                - filter_words: Nombre de mots à filtrer
                - filter_lines: Nombre de lignes à filtrer
                - match_status: Codes à matcher
                - match_size: Tailles à matcher
                - output: Fichier de sortie
                - format: Format de sortie (json, csv, html)
        """
        if not self.available:
            return {
                "success": False,
                "error": "ffuf non installé",
                "results": [],
                "apt_mode": self.apt_mode
            }
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        cmd = [self.tool_path]
        
        # Mode APT: ralentir et limiter
        if self.apt_mode:
            kwargs.setdefault('threads', 5)
            kwargs.setdefault('delay', 1)
        
        # URL cible (doit contenir FUZZ)
        if 'FUZZ' not in target:
            # Détection du type de fuzzing
            if kwargs.get('fuzz_type') == 'directory':
                target = target.rstrip('/') + '/FUZZ'
            elif kwargs.get('fuzz_type') == 'parameter':
                if '?' in target:
                    target += '&FUZZ=FUZZ'
                else:
                    target += '?FUZZ=FUZZ'
            else:
                target = target.rstrip('/') + '/FUZZ'
        
        cmd.extend(['-u', target])
        
        # Wordlist
        wordlist = kwargs.get('wordlist')
        if wordlist:
            if not Path(wordlist).exists():
                return {
                    "success": False,
                    "error": f"Wordlist non trouvée: {wordlist}",
                    "results": []
                }
            cmd.extend(['-w', wordlist])
        else:
            # Wordlist par défaut selon le type
            fuzz_type = kwargs.get('fuzz_type', 'directory')
            default_wordlist = self.default_wordlists.get(fuzz_type)
            if default_wordlist and Path(default_wordlist).exists():
                cmd.extend(['-w', default_wordlist])
            else:
                cmd.extend(['-w', self.default_wordlists['directory']])
        
        # Threads (limités en mode APT)
        threads = kwargs.get('threads', 40)
        if self.apt_mode:
            threads = min(threads, 5)
        cmd.extend(['-t', str(threads)])
        
        # Délai entre les requêtes (mode furtif)
        delay = kwargs.get('delay')
        if delay:
            cmd.extend(['-delay', str(delay)])
        elif self.stealth_config.get('random_delays', False):
            min_delay, max_delay = self.stealth_config.get('delay', (0.5, 1.5))
            avg_delay = (min_delay + max_delay) / 2
            cmd.extend(['-delay', str(round(avg_delay, 1))])
        
        # Extensions
        extensions = kwargs.get('extensions')
        if extensions:
            if isinstance(extensions, list):
                extensions = ','.join(extensions)
            cmd.extend(['-e', extensions])
        
        # Recursion
        if kwargs.get('recursion'):
            cmd.append('-recursion')
            recursion_depth = kwargs.get('recursion_depth', 3)
            if recursion_depth:
                cmd.extend(['-recursion-depth', str(recursion_depth)])
        
        # Méthodes HTTP
        methods = kwargs.get('methods')
        if methods:
            if isinstance(methods, list):
                methods = ','.join(methods)
            cmd.extend(['-X', methods])
        
        # Données POST
        data = kwargs.get('data')
        if data:
            cmd.extend(['-d', data])
        
        # Headers
        headers = kwargs.get('headers', {})
        if self.stealth_config.get('stealth', False):
            headers['User-Agent'] = self._get_random_user_agent()
        
        for key, value in headers.items():
            cmd.extend(['-H', f"{key}: {value}"])
        
        # Cookies
        cookies = kwargs.get('cookies', {})
        if cookies:
            cookie_str = '; '.join([f"{k}={v}" for k, v in cookies.items()])
            cmd.extend(['-b', cookie_str])
        
        # Filtres
        if kwargs.get('filter_status'):
            filter_status = kwargs['filter_status']
            if isinstance(filter_status, list):
                filter_status = ','.join(str(s) for s in filter_status)
            cmd.extend(['-fc', str(filter_status)])
        
        if kwargs.get('filter_size'):
            filter_size = kwargs['filter_size']
            if isinstance(filter_size, list):
                filter_size = ','.join(str(s) for s in filter_size)
            cmd.extend(['-fs', str(filter_size)])
        
        if kwargs.get('filter_words'):
            cmd.extend(['-fw', str(kwargs['filter_words'])])
        
        if kwargs.get('filter_lines'):
            cmd.extend(['-fl', str(kwargs['filter_lines'])])
        
        # Matchs
        if kwargs.get('match_status'):
            match_status = kwargs['match_status']
            if isinstance(match_status, list):
                match_status = ','.join(str(s) for s in match_status)
            cmd.extend(['-mc', str(match_status)])
        
        if kwargs.get('match_size'):
            cmd.extend(['-ms', str(kwargs['match_size'])])
        
        # Timeout
        if kwargs.get('timeout'):
            cmd.extend(['-timeout', str(kwargs['timeout'])])
        
        # Mode silencieux (furtif)
        if self.apt_mode or kwargs.get('quiet'):
            cmd.append('-s')
        
        # Sortie
        output_file = kwargs.get('output')
        output_format = kwargs.get('format', 'json')
        
        if output_file:
            cmd.extend(['-o', output_file, '-of', output_format])
        
        timeout = kwargs.get('execution_timeout', 600)
        
        # Proxy
        proxy = kwargs.get('proxy')
        if proxy:
            cmd.extend(['-p', proxy])
        elif self.proxy_rotation:
            proxy = self._get_next_proxy()
            if proxy:
                cmd.extend(['-p', proxy])
        
        # Exécution
        result = self.execute_command(cmd, timeout=timeout)
        
        if result["success"]:
            # Si sortie JSON, parser directement
            if output_file and output_format == 'json' and Path(output_file).exists():
                with open(output_file, 'r') as f:
                    json_results = json.load(f)
                return {
                    "success": True,
                    "target": target,
                    "results": self._parse_json_results(json_results),
                    "count": len(json_results.get('results', [])),
                    "execution_time": result.get("execution_time", 0),
                    "command_used": ' '.join(cmd),
                    "apt_mode": self.apt_mode
                }
            
            # Sinon, parser la sortie texte
            results = self.parse_output(result["stdout"])
            return {
                "success": True,
                "target": target,
                "results": results,
                "count": len(results),
                "raw_output": result["stdout"],
                "execution_time": result.get("execution_time", 0),
                "apt_mode": self.apt_mode
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Erreur lors du fuzzing"),
                "stderr": result.get("stderr", ""),
                "results": [],
                "apt_mode": self.apt_mode
            }
    
    def _parse_json_results(self, json_results: Dict) -> List[Dict[str, Any]]:
        """
        Parse les résultats JSON de ffuf
        
        Args:
            json_results: Résultats JSON bruts
            
        Returns:
            Liste structurée des résultats
        """
        results = []
        
        for item in json_results.get('results', []):
            result = {
                "url": item.get('url', ''),
                "status_code": item.get('status', 0),
                "content_length": item.get('length', 0),
                "words": item.get('words', 0),
                "lines": item.get('lines', 0),
                "duration": item.get('duration', 0),
                "redirect_location": item.get('redirectlocation', ''),
                "result_file": item.get('resultfile', '')
            }
            
            # Classification
            if result["status_code"] == 200:
                result["type"] = "accessible"
                result["severity"] = "high"
            elif result["status_code"] in [301, 302, 307, 308]:
                result["type"] = "redirect"
                result["severity"] = "medium"
            elif result["status_code"] == 403:
                result["type"] = "forbidden"
                result["severity"] = "low"
            elif result["status_code"] == 401:
                result["type"] = "unauthorized"
                result["severity"] = "medium"
            else:
                result["type"] = "other"
                result["severity"] = "info"
            
            results.append(result)
        
        return results
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse la sortie texte de ffuf
        
        Args:
            output: Sortie brute de ffuf
            
        Returns:
            Liste des résultats
        """
        results = []
        
        # Pattern pour les résultats ffuf
        pattern = r'(\S+)\s+\[Status: (\d+), Size: (\d+), Words: (\d+), Lines: (\d+)\]'
        
        for line in output.split('\n'):
            match = re.search(pattern, line)
            if match:
                result = {
                    "url": match.group(1),
                    "status_code": int(match.group(2)),
                    "content_length": int(match.group(3)),
                    "words": int(match.group(4)),
                    "lines": int(match.group(5)),
                    "type": self._classify_result(int(match.group(2))),
                    "severity": self._determine_severity(int(match.group(2)))
                }
                results.append(result)
        
        return results
    
    def _classify_result(self, status_code: int) -> str:
        """
        Classifie le résultat selon le code HTTP
        
        Args:
            status_code: Code HTTP
            
        Returns:
            Type de résultat
        """
        if status_code == 200:
            return "accessible"
        elif status_code in [301, 302, 307, 308]:
            return "redirect"
        elif status_code == 403:
            return "forbidden"
        elif status_code == 401:
            return "unauthorized"
        elif status_code == 404:
            return "not_found"
        elif status_code >= 500:
            return "server_error"
        else:
            return "other"
    
    def _determine_severity(self, status_code: int) -> str:
        """
        Détermine la sévérité selon le code HTTP
        
        Args:
            status_code: Code HTTP
            
        Returns:
            Niveau de sévérité
        """
        if status_code == 200:
            return "high"
        elif status_code in [301, 302, 307, 308, 401]:
            return "medium"
        elif status_code == 403:
            return "low"
        else:
            return "info"
    
    def fuzz_directory(self, target: str, wordlist: str = None, **kwargs) -> Dict[str, Any]:
        """
        Fuzzing spécifique pour les répertoires
        
        Args:
            target: URL cible
            wordlist: Wordlist personnalisée
            **kwargs: Options supplémentaires pour scan()
        """
        kwargs['fuzz_type'] = 'directory'
        return self.scan(target, wordlist=wordlist, **kwargs)
    
    def fuzz_parameters(self, target: str, wordlist: str = None, **kwargs) -> Dict[str, Any]:
        """
        Fuzzing pour les paramètres GET
        
        Args:
            target: URL cible
            wordlist: Wordlist personnalisée
            **kwargs: Options supplémentaires pour scan()
        """
        kwargs['fuzz_type'] = 'parameter'
        return self.scan(target, wordlist=wordlist, **kwargs)
    
    def fuzz_subdomains(self, domain: str, wordlist: str = None, **kwargs) -> Dict[str, Any]:
        """
        Fuzzing pour les sous-domaines
        
        Args:
            domain: Domaine cible
            wordlist: Wordlist personnalisée
            **kwargs: Options supplémentaires pour scan()
        """
        target = f"http://FUZZ.{domain}"
        kwargs['fuzz_type'] = 'subdomain'
        
        # Wordlist par défaut pour sous-domaines
        if not wordlist:
            wordlist = self.default_wordlists.get('subdomain')
        
        return self.scan(target, wordlist=wordlist, **kwargs)
    
    def fuzz_extensions(self, target: str, extensions: List[str], **kwargs) -> Dict[str, Any]:
        """
        Fuzzing pour les extensions de fichiers
        
        Args:
            target: URL cible
            extensions: Liste des extensions à tester
            **kwargs: Options supplémentaires pour scan()
        """
        kwargs['extensions'] = extensions
        kwargs['fuzz_type'] = 'extension'
        return self.fuzz_directory(target, **kwargs)
    
    def fuzz_post_parameters(self, target: str, wordlist: str = None, **kwargs) -> Dict[str, Any]:
        """
        Fuzzing pour les paramètres POST
        
        Args:
            target: URL cible
            wordlist: Wordlist personnalisée
            **kwargs: Options supplémentaires pour scan()
        """
        kwargs['fuzz_type'] = 'parameter'
        kwargs['methods'] = ['POST']
        kwargs['data'] = 'FUZZ=FUZZ'
        return self.scan(target, wordlist=wordlist, **kwargs)
    
    def fuzz_headers(self, target: str, wordlist: str = None, **kwargs) -> Dict[str, Any]:
        """
        Fuzzing pour les en-têtes HTTP
        
        Args:
            target: URL cible
            wordlist: Wordlist personnalisée
            **kwargs: Options supplémentaires pour scan()
        """
        kwargs['fuzz_type'] = 'header'
        kwargs['headers'] = {'FUZZ': 'FUZZ'}
        return self.scan(target, wordlist=wordlist, **kwargs)
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de version de ffuf
        
        Returns:
            Dictionnaire avec les informations de version
        """
        if not self.available:
            return {"available": False}
        
        result = self.execute_command([self.tool_path, "-V"], stealth=False)
        
        if result["success"]:
            version_line = result["stdout"].split('\n')[0] if result["stdout"] else ""
            return {
                "available": True,
                "version": version_line,
                "tool": "ffuf",
                "path": self.tool_path
            }
        
        return {"available": False, "error": result.get("error")}
    
    def generate_wordlist(self, base: List[str], prefixes: List[str] = None,
                          suffixes: List[str] = None) -> List[str]:
        """
        Génère une wordlist personnalisée pour ffuf
        
        Args:
            base: Liste de mots de base
            prefixes: Préfixes à ajouter
            suffixes: Suffixes à ajouter
            
        Returns:
            Liste des mots générés
        """
        wordlist = set(base)
        
        # Ajouter des préfixes
        if prefixes:
            for word in base:
                for prefix in prefixes:
                    wordlist.add(f"{prefix}{word}")
        
        # Ajouter des suffixes
        if suffixes:
            for word in base:
                for suffix in suffixes:
                    wordlist.add(f"{word}{suffix}")
        
        # Ajouter des variations
        variations = [
            lambda w: w.upper(),
            lambda w: w.lower(),
            lambda w: w.capitalize(),
            lambda w: w + "_",
            lambda w: w + "-",
            lambda w: w + "1",
            lambda w: w + "2"
        ]
        
        for word in base:
            for var in variations:
                try:
                    wordlist.add(var(word))
                except:
                    pass
        
        return list(wordlist)