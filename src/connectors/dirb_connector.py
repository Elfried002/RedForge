#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour Dirb - Outil de force brute de répertoires web
Version avec support furtif, APT et détection avancée
"""

import re
import random
from typing import Dict, Any, List, Optional
from pathlib import Path
from urllib.parse import urlparse

from src.connectors.base_connector import BaseConnector


class DirbConnector(BaseConnector):
    """Connecteur avancé pour Dirb avec support furtif"""
    
    def __init__(self, tool_path: Optional[str] = None):
        """
        Initialise le connecteur Dirb
        
        Args:
            tool_path: Chemin personnalisé vers l'exécutable Dirb
        """
        super().__init__(tool_path)
        self.default_wordlists = [
            "/usr/share/dirb/wordlists/common.txt",
            "/usr/share/wordlists/dirb/common.txt",
            "/usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt"
        ]
    
    def _find_tool(self) -> Optional[str]:
        """Trouve l'exécutable Dirb"""
        import shutil
        
        paths = [
            "dirb",
            "/usr/bin/dirb",
            "/usr/local/bin/dirb",
            "/opt/dirb/dirb"
        ]
        
        for path in paths:
            if path and shutil.which(path):
                return path
        
        return None
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les répertoires avec Dirb
        
        Args:
            target: URL cible
            **kwargs:
                - wordlist: Fichier wordlist personnalisé
                - extensions: Extensions à tester
                - recursive: Scan récursif
                - threads: Nombre de threads
                - delay: Délai entre les requêtes
                - user_agent: User-Agent personnalisé
                - cookie: Cookie à utiliser
                - proxy: Proxy à utiliser
                - exclude_codes: Codes HTTP à exclure
                - include_codes: Codes HTTP à inclure
        """
        if not self.available:
            return {
                "success": False,
                "error": "Dirb non installé",
                "directories": [],
                "apt_mode": self.apt_mode
            }
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        # Construction de l'URL complète
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target
        
        cmd = [self.tool_path, target]
        
        # Wordlist
        wordlist = kwargs.get('wordlist')
        if wordlist:
            if Path(wordlist).exists():
                cmd.append(wordlist)
            else:
                return {
                    "success": False,
                    "error": f"Wordlist non trouvée: {wordlist}",
                    "directories": []
                }
        else:
            # Trouver une wordlist par défaut
            default_wordlist = self._find_default_wordlist()
            if default_wordlist:
                cmd.append(default_wordlist)
            else:
                cmd.append(self.default_wordlists[0])
        
        # Extensions
        extensions = kwargs.get('extensions')
        if extensions:
            if isinstance(extensions, list):
                extensions = ','.join(extensions)
            cmd.extend(['-X', extensions])
        
        # Options de base
        if kwargs.get('recursive'):
            cmd.append('-r')
        
        # Threads et délais (mode furtif)
        threads = kwargs.get('threads', 10)
        if self.apt_mode:
            threads = min(threads, 3)
        
        delay = kwargs.get('delay')
        if delay:
            cmd.extend(['-z', str(delay)])
        elif self.stealth_config.get('random_delays', False):
            min_delay, max_delay = self.stealth_config.get('delay', (0.5, 1.5))
            avg_delay = (min_delay + max_delay) / 2
            cmd.extend(['-z', str(round(avg_delay, 1))])
        else:
            cmd.extend(['-z', str(threads)])
        
        # Filtres
        exclude_codes = kwargs.get('exclude_codes')
        if exclude_codes:
            if isinstance(exclude_codes, list):
                exclude_codes = ','.join(str(c) for c in exclude_codes)
            cmd.extend(['-N', exclude_codes])
        
        include_codes = kwargs.get('include_codes')
        if include_codes:
            if isinstance(include_codes, list):
                include_codes = ','.join(str(c) for c in include_codes)
            cmd.extend(['-R', include_codes])
        
        # Mode furtif
        if kwargs.get('verbose'):
            cmd.append('-v')
        elif self.apt_mode or kwargs.get('quiet'):
            cmd.append('-q')  # Mode silencieux
        
        if kwargs.get('ssl') or target.startswith('https://'):
            cmd.append('-S')
        
        # Authentification
        if kwargs.get('auth'):
            cmd.extend(['-a', kwargs['auth']])
        
        # User-Agent personnalisé
        user_agent = kwargs.get('user_agent')
        if user_agent:
            cmd.extend(['-A', user_agent])
        elif self.stealth_config.get('stealth', False):
            user_agent = self._get_random_user_agent()
            cmd.extend(['-A', user_agent])
        
        # Cookie
        cookie = kwargs.get('cookie')
        if cookie:
            cmd.extend(['-c', cookie])
        
        # Proxy
        proxy = kwargs.get('proxy')
        if proxy:
            cmd.extend(['-p', proxy])
        elif self.proxy_rotation:
            proxy = self._get_next_proxy()
            if proxy:
                cmd.extend(['-p', proxy])
        
        # Headers personnalisés
        headers = kwargs.get('headers')
        if headers:
            if isinstance(headers, dict):
                for key, value in headers.items():
                    cmd.extend(['-H', f"{key}: {value}"])
        
        timeout = kwargs.get('timeout', 600)
        
        # Exécution
        result = self.execute_command(cmd, timeout=timeout)
        
        if result["success"]:
            directories = self.parse_output(result["stdout"])
            return {
                "success": True,
                "target": target,
                "directories": directories,
                "count": len(directories),
                "raw_output": result["stdout"],
                "execution_time": result.get("execution_time", 0),
                "command_used": ' '.join(cmd),
                "apt_mode": self.apt_mode,
                "wordlist_used": wordlist or self._find_default_wordlist()
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Erreur lors du scan"),
                "stderr": result.get("stderr", ""),
                "directories": [],
                "apt_mode": self.apt_mode
            }
    
    def _find_default_wordlist(self) -> Optional[str]:
        """Trouve une wordlist par défaut disponible"""
        for wordlist in self.default_wordlists:
            if Path(wordlist).exists():
                return wordlist
        return None
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse la sortie de Dirb pour extraire les répertoires trouvés
        
        Args:
            output: Sortie brute de Dirb
            
        Returns:
            Liste des répertoires trouvés
        """
        directories = []
        
        # Pattern pour les résultats Dirb: + http://example.com/dir (CODE:200|SIZE:1234)
        pattern = r'\+\s+(https?://[^\s]+)\s+\(CODE:(\d+)\|SIZE:(\d+)\)'
        
        # Pattern pour les redirections
        redirect_pattern = r'\+\s+(https?://[^\s]+)\s+\(CODE:(\d+)\|SIZE:(\d+)\|Location:[^)]+\)'
        
        # Pattern pour les erreurs
        error_pattern = r'-\s+(https?://[^\s]+)\s+\(CODE:(\d+)\|SIZE:(\d+)\)'
        
        for line in output.split('\n'):
            # Redirections
            match = re.search(redirect_pattern, line)
            if match:
                url = match.group(1)
                code = int(match.group(2))
                size = int(match.group(3))
                
                dir_info = self._create_dir_info(url, code, size)
                dir_info["type"] = "redirect"
                directories.append(dir_info)
                continue
            
            # Résultats normaux
            match = re.search(pattern, line)
            if match:
                url = match.group(1)
                code = int(match.group(2))
                size = int(match.group(3))
                
                dir_info = self._create_dir_info(url, code, size)
                directories.append(dir_info)
                continue
            
            # Erreurs
            match = re.search(error_pattern, line)
            if match:
                url = match.group(1)
                code = int(match.group(2))
                size = int(match.group(3))
                
                dir_info = self._create_dir_info(url, code, size)
                dir_info["type"] = "error"
                directories.append(dir_info)
        
        return directories
    
    def _create_dir_info(self, url: str, code: int, size: int) -> Dict[str, Any]:
        """
        Crée un dictionnaire d'information de répertoire
        
        Args:
            url: URL du répertoire
            code: Code HTTP
            size: Taille de la réponse
            
        Returns:
            Dictionnaire avec les informations
        """
        # Extraire le chemin
        parsed = urlparse(url)
        path = parsed.path if parsed.path else '/'
        
        dir_info = {
            "url": url,
            "path": path,
            "status_code": code,
            "size": size,
            "type": self._classify_directory(code, path)
        }
        
        # Ajouter le niveau de sévérité
        if code == 200:
            dir_info["severity"] = "high"
        elif code == 301 or code == 302:
            dir_info["severity"] = "medium"
        elif code == 403:
            dir_info["severity"] = "low"
        else:
            dir_info["severity"] = "info"
        
        return dir_info
    
    def _classify_directory(self, code: int, path: str) -> str:
        """
        Classifie le type de répertoire
        
        Args:
            code: Code HTTP
            path: Chemin du répertoire
            
        Returns:
            Type de répertoire
        """
        if code == 200:
            return "accessible"
        elif code == 301 or code == 302:
            return "redirect"
        elif code == 403:
            return "forbidden"
        elif code == 401:
            return "unauthorized"
        elif code == 500:
            return "server_error"
        else:
            return "other"
    
    def scan_with_custom_wordlist(self, target: str, wordlist_path: str, **kwargs) -> Dict[str, Any]:
        """
        Scan avec une wordlist personnalisée
        
        Args:
            target: URL cible
            wordlist_path: Chemin vers la wordlist
            **kwargs: Options supplémentaires pour scan()
        """
        if not Path(wordlist_path).exists():
            return {
                "success": False,
                "error": f"Wordlist non trouvée: {wordlist_path}",
                "directories": []
            }
        
        return self.scan(target, wordlist=wordlist_path, **kwargs)
    
    def test_common_paths(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Teste les chemins les plus communs rapidement
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        import requests
        
        common_paths = [
            "/admin", "/login", "/wp-admin", "/administrator",
            "/backup", "/config", "/sql", "/old", "/temp",
            "/api", "/v1", "/v2", "/docs", "/swagger",
            "/phpmyadmin", "/mysql", "/database", "/db",
            "/backup.zip", "/backup.tar.gz", "/dump.sql",
            "/.git", "/.env", "/.htaccess", "/robots.txt",
            "/server-status", "/info.php", "/phpinfo.php"
        ]
        
        results = []
        
        for path in common_paths:
            # Appliquer le délai furtif
            if self.apt_mode:
                self._apply_stealth_delay()
            
            url = target.rstrip('/') + path
            
            try:
                # Utiliser requests pour plus de contrôle
                headers = {}
                if self.stealth_config.get('stealth', False):
                    headers['User-Agent'] = self._get_random_user_agent()
                
                response = requests.get(url, headers=headers, timeout=5, verify=False)
                
                if response.status_code != 404:
                    results.append({
                        "url": url,
                        "path": path,
                        "status_code": response.status_code,
                        "size": len(response.text),
                        "type": self._classify_directory(response.status_code, path)
                    })
                    
            except Exception:
                continue
        
        return {
            "success": True,
            "target": target,
            "directories": results,
            "count": len(results),
            "apt_mode": self.apt_mode
        }
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de version de Dirb
        
        Returns:
            Dictionnaire avec les informations de version
        """
        if not self.available:
            return {"available": False}
        
        result = self.execute_command([self.tool_path, "-v"], stealth=False)
        
        if result["success"]:
            version_line = result["stdout"].split('\n')[0] if result["stdout"] else ""
            return {
                "available": True,
                "version": version_line,
                "tool": "dirb",
                "path": self.tool_path
            }
        
        return {"available": False, "error": result.get("error")}
    
    def generate_wordlist(self, base_words: List[str], extensions: List[str] = None) -> List[str]:
        """
        Génère une wordlist personnalisée
        
        Args:
            base_words: Liste de mots de base
            extensions: Extensions à ajouter
            
        Returns:
            Liste des mots pour la wordlist
        """
        wordlist = set(base_words)
        
        # Ajouter des variations
        variations = [
            lambda w: w.upper(),
            lambda w: w.lower(),
            lambda w: w.capitalize(),
            lambda w: w + "_backup",
            lambda w: w + "_old",
            lambda w: w + "_new",
            lambda w: w + "1",
            lambda w: w + "2"
        ]
        
        for word in base_words:
            for var in variations:
                try:
                    wordlist.add(var(word))
                except:
                    pass
        
        # Ajouter les extensions
        if extensions:
            new_words = set()
            for word in wordlist:
                for ext in extensions:
                    new_words.add(f"{word}.{ext}")
            wordlist.update(new_words)
        
        return list(wordlist)