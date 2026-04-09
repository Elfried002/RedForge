#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour Hydra - Outil de force brute
Version avec support furtif, APT et techniques avancées
"""

import re
import random
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass

from src.connectors.base_connector import BaseConnector


@dataclass
class HydraConfig:
    """Configuration spécifique pour Hydra"""
    service: str = "ssh"
    threads: int = 16
    timeout: int = 30
    retries: int = 3
    exit_on_find: bool = False
    use_ssl: bool = False
    verbose: bool = False


class HydraConnector(BaseConnector):
    """Connecteur avancé pour Hydra avec support furtif"""
    
    def __init__(self, tool_path: Optional[str] = None):
        """
        Initialise le connecteur Hydra
        
        Args:
            tool_path: Chemin personnalisé vers l'exécutable Hydra
        """
        super().__init__(tool_path)
        self.supported_services = [
            "ssh", "ftp", "http-get", "http-post", "https-get", "https-post",
            "mysql", "postgresql", "redis", "mongodb", "smb", "rdp", "telnet",
            "pop3", "imap", "smtp", "snmp", "ldap", "vnc"
        ]
        
        self.default_wordlists = {
            "users": "/usr/share/wordlists/users.txt",
            "passwords": "/usr/share/wordlists/passwords.txt",
            "common": "/usr/share/wordlists/common.txt"
        }
    
    def _find_tool(self) -> Optional[str]:
        """Trouve l'exécutable Hydra"""
        import shutil
        
        paths = [
            "hydra",
            "/usr/bin/hydra",
            "/usr/local/bin/hydra",
            "/opt/hydra/hydra"
        ]
        
        for path in paths:
            if path and shutil.which(path):
                return path
        
        return None
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute une attaque de force brute avec Hydra
        
        Args:
            target: Cible (IP ou hostname)
            **kwargs:
                - service: Service à attaquer (ssh, ftp, http-get, etc.)
                - username: Nom d'utilisateur unique
                - userlist: Fichier de liste d'utilisateurs
                - password: Mot de passe unique
                - passlist: Fichier de liste de mots de passe
                - port: Port personnalisé
                - threads: Nombre de threads
                - delay: Délai entre les tentatives
                - timeout: Timeout de connexion
                - retries: Nombre de tentatives
                - exit_on_find: Arrêter à la première trouvaille
        """
        if not self.available:
            return {
                "success": False,
                "error": "Hydra non installé",
                "credentials": [],
                "apt_mode": self.apt_mode
            }
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        cmd = [self.tool_path]
        
        # Mode APT: réduire les threads et augmenter les délais
        if self.apt_mode:
            kwargs.setdefault('threads', 4)
            kwargs.setdefault('delay', 2)
            kwargs.setdefault('retries', 1)
        
        # Service
        service = kwargs.get('service', 'ssh')
        if service not in self.supported_services:
            return {
                "success": False,
                "error": f"Service non supporté: {service}. Supportés: {', '.join(self.supported_services)}",
                "credentials": []
            }
        
        cmd.extend(['-s', service])
        
        # Authentification
        username = kwargs.get('username')
        userlist = kwargs.get('userlist')
        
        if username:
            cmd.extend(['-l', username])
        elif userlist:
            if not Path(userlist).exists():
                return {
                    "success": False,
                    "error": f"Fichier utilisateur non trouvé: {userlist}",
                    "credentials": []
                }
            cmd.extend(['-L', userlist])
        else:
            # Wordlist par défaut
            default_userlist = self.default_wordlists.get('users')
            if default_userlist and Path(default_userlist).exists():
                cmd.extend(['-L', default_userlist])
            else:
                # Utilisateurs communs par défaut
                common_users = ['admin', 'root', 'user', 'test', 'guest']
                temp_userlist = self._create_temp_wordlist(common_users, "users")
                cmd.extend(['-L', temp_userlist])
        
        password = kwargs.get('password')
        passlist = kwargs.get('passlist')
        
        if password:
            cmd.extend(['-p', password])
        elif passlist:
            if not Path(passlist).exists():
                return {
                    "success": False,
                    "error": f"Fichier mots de passe non trouvé: {passlist}",
                    "credentials": []
                }
            cmd.extend(['-P', passlist])
        else:
            # Wordlist par défaut
            default_passlist = self.default_wordlists.get('passwords')
            if default_passlist and Path(default_passlist).exists():
                cmd.extend(['-P', default_passlist])
            else:
                # Mots de passe communs par défaut
                common_passwords = ['password', '123456', 'admin', 'root', 'toor']
                temp_passlist = self._create_temp_wordlist(common_passwords, "passwords")
                cmd.extend(['-P', temp_passlist])
        
        # Port
        port = kwargs.get('port')
        if port:
            cmd.extend(['-s', str(port)])
        
        # Threads (limités en mode APT)
        threads = kwargs.get('threads', 16)
        if self.apt_mode:
            threads = min(threads, 4)
        cmd.extend(['-t', str(threads)])
        
        # Délai entre les tentatives (mode furtif)
        delay = kwargs.get('delay')
        if delay:
            cmd.extend(['-w', str(delay)])
        elif self.stealth_config.get('random_delays', False):
            min_delay, max_delay = self.stealth_config.get('delay', (0.5, 1.5))
            avg_delay = (min_delay + max_delay) / 2
            cmd.extend(['-w', str(round(avg_delay, 1))])
        
        # Timeout
        timeout = kwargs.get('timeout', 30)
        cmd.extend(['-W', str(timeout)])
        
        # Retries
        retries = kwargs.get('retries', 3)
        if retries > 1:
            cmd.extend(['-r', str(retries)])
        
        # Options
        if kwargs.get('exit_on_find') or self.apt_mode:
            cmd.append('-f')  # Exit on first find
        
        if kwargs.get('verbose'):
            cmd.append('-V')
        
        if kwargs.get('use_ssl') or kwargs.get('ssl'):
            cmd.append('-S')
        
        if kwargs.get('quiet') or self.apt_mode:
            cmd.append('-q')  # Mode silencieux
        
        # Headers HTTP personnalisés
        if service in ['http-get', 'http-post', 'https-get', 'https-post']:
            headers = kwargs.get('headers', {})
            for key, value in headers.items():
                cmd.extend(['-H', f"{key}: {value}"])
        
        # Cookies
        cookies = kwargs.get('cookies')
        if cookies:
            if isinstance(cookies, dict):
                cookie_str = '; '.join([f"{k}={v}" for k, v in cookies.items()])
            else:
                cookie_str = cookies
            cmd.extend(['-b', cookie_str])
        
        # Cible
        cmd.append(target)
        
        # Protocole spécifique
        if service in ['http-get', 'http-post', 'https-get', 'https-post']:
            path = kwargs.get('path', '/')
            cmd.append(path)
            
            # Paramètres pour formulaire
            user_param = kwargs.get('user_param', 'username')
            pass_param = kwargs.get('pass_param', 'password')
            fail_string = kwargs.get('fail_string', 'incorrect')
            
            if service in ['http-post', 'https-post']:
                service = f"{service}-form://{target}{path}:{user_param}=^USER^&{pass_param}=^PASS^:F={fail_string}"
            else:
                service = f"{service}://{target}{path}:{user_param}=^USER^&{pass_param}=^PASS^:F={fail_string}"
            
            cmd[-2] = service
        
        timeout_sec = kwargs.get('execution_timeout', 600)
        
        # Proxy
        proxy = kwargs.get('proxy')
        if proxy:
            cmd.extend(['-X', proxy])
        elif self.proxy_rotation:
            proxy = self._get_next_proxy()
            if proxy:
                cmd.extend(['-X', proxy])
        
        # Exécution
        result = self.execute_command(cmd, timeout=timeout_sec)
        
        # Nettoyer les fichiers temporaires
        self._cleanup_temp_files()
        
        if result["success"] or result["returncode"] == 0:
            credentials = self.parse_output(result["stdout"])
            return {
                "success": True,
                "target": target,
                "service": service,
                "credentials": credentials,
                "count": len(credentials),
                "raw_output": result["stdout"],
                "execution_time": result.get("execution_time", 0),
                "command_used": ' '.join(cmd),
                "apt_mode": self.apt_mode
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Erreur lors de l'attaque"),
                "stderr": result.get("stderr", ""),
                "credentials": [],
                "apt_mode": self.apt_mode
            }
    
    def _create_temp_wordlist(self, words: List[str], prefix: str) -> str:
        """
        Crée un fichier wordlist temporaire
        
        Args:
            words: Liste des mots
            prefix: Préfixe du fichier
            
        Returns:
            Chemin du fichier temporaire
        """
        temp_file = self.create_temp_output_file(f"_{prefix}.txt")
        with open(temp_file, 'w') as f:
            for word in words:
                f.write(word + '\n')
        self._temp_files.append(temp_file)
        return temp_file
    
    def _cleanup_temp_files(self):
        """Nettoie les fichiers temporaires créés"""
        for file in getattr(self, '_temp_files', []):
            self.cleanup_temp_file(file)
        self._temp_files = []
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse la sortie de Hydra pour extraire les credentials trouvés
        
        Args:
            output: Sortie brute de Hydra
            
        Returns:
            Liste des credentials trouvés
        """
        credentials = []
        
        # Pattern Hydra: [PORT][service] host: 192.168.1.1   login: admin   password: secret
        pattern = r'\[(\d+)\]\[(\w+)\]\s+([^:]+):\s+([^\s]+)\s+login:\s+([^\s]+)\s+password:\s+(.+)'
        
        for line in output.split('\n'):
            match = re.search(pattern, line)
            if match:
                cred = {
                    "port": match.group(1),
                    "service": match.group(2),
                    "host": match.group(3).strip(),
                    "username": match.group(5),
                    "password": match.group(6),
                    "type": "success",
                    "severity": "critical"
                }
                credentials.append(cred)
            
            # Format alternatif
            alt_pattern = r'login:\s+(\S+)\s+password:\s+(\S+)'
            alt_match = re.search(alt_pattern, line)
            if alt_match and not match:
                cred = {
                    "username": alt_match.group(1),
                    "password": alt_match.group(2),
                    "type": "success",
                    "severity": "critical"
                }
                credentials.append(cred)
            
            # Format pour les échecs
            fail_pattern = r'\[ATTEMPT\] target (\S+) - login "([^"]+)" - pass "([^"]+)"'
            fail_match = re.search(fail_pattern, line)
            if fail_match:
                cred = {
                    "host": fail_match.group(1),
                    "username": fail_match.group(2),
                    "password": fail_match.group(3),
                    "type": "attempt",
                    "severity": "info"
                }
                credentials.append(cred)
        
        return credentials
    
    def brute_force_http_form(self, target: str, form_url: str, **kwargs) -> Dict[str, Any]:
        """
        Force brute sur formulaire HTTP
        
        Args:
            target: Cible
            form_url: URL du formulaire
            **kwargs:
                - user_param: Nom du paramètre utilisateur
                - pass_param: Nom du paramètre mot de passe
                - fail_string: Chaîne indiquant un échec
                - method: Méthode HTTP (GET ou POST)
        """
        method = kwargs.get('method', 'POST').lower()
        service = f"http-{method}" if method == 'post' else "http-get"
        
        return self.scan(
            target,
            service=service,
            path=form_url,
            user_param=kwargs.get('user_param', 'username'),
            pass_param=kwargs.get('pass_param', 'password'),
            fail_string=kwargs.get('fail_string', 'incorrect'),
            **kwargs
        )
    
    def brute_force_ssh(self, target: str, **kwargs) -> Dict[str, Any]:
        """Force brute SSH"""
        return self.scan(target, service='ssh', **kwargs)
    
    def brute_force_ftp(self, target: str, **kwargs) -> Dict[str, Any]:
        """Force brute FTP"""
        return self.scan(target, service='ftp', **kwargs)
    
    def brute_force_mysql(self, target: str, **kwargs) -> Dict[str, Any]:
        """Force brute MySQL"""
        return self.scan(target, service='mysql', **kwargs)
    
    def brute_force_postgresql(self, target: str, **kwargs) -> Dict[str, Any]:
        """Force brute PostgreSQL"""
        return self.scan(target, service='postgresql', **kwargs)
    
    def brute_force_rdp(self, target: str, **kwargs) -> Dict[str, Any]:
        """Force brute RDP"""
        return self.scan(target, service='rdp', **kwargs)
    
    def brute_force_smb(self, target: str, **kwargs) -> Dict[str, Any]:
        """Force brute SMB"""
        return self.scan(target, service='smb', **kwargs)
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de version de Hydra
        
        Returns:
            Dictionnaire avec les informations de version
        """
        if not self.available:
            return {"available": False}
        
        result = self.execute_command([self.tool_path, "-h"], stealth=False)
        
        if result["success"]:
            version_line = result["stdout"].split('\n')[0] if result["stdout"] else ""
            return {
                "available": True,
                "version": version_line,
                "tool": "hydra",
                "path": self.tool_path
            }
        
        return {"available": False, "error": result.get("error")}
    
    def generate_wordlist_combinations(self, users: List[str], passwords: List[str]) -> str:
        """
        Génère une wordlist de combinaisons username:password
        
        Args:
            users: Liste des utilisateurs
            passwords: Liste des mots de passe
            
        Returns:
            Chemin du fichier de combinaisons
        """
        temp_file = self.create_temp_output_file("_combinations.txt")
        with open(temp_file, 'w') as f:
            for user in users:
                for password in passwords:
                    f.write(f"{user}:{password}\n")
        return temp_file