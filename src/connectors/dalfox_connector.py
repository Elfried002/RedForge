#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour Dalfox - Outil de scan XSS rapide et efficace
Version avec support furtif, APT et intégration avancée
"""

import re
import json
import random
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from src.connectors.base_connector import BaseConnector


class DalfoxConnector(BaseConnector):
    """Connecteur avancé pour Dalfox avec support furtif"""
    
    def __init__(self, tool_path: Optional[str] = None):
        """
        Initialise le connecteur Dalfox
        
        Args:
            tool_path: Chemin personnalisé vers l'exécutable Dalfox
        """
        super().__init__(tool_path)
        self.supported_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        self.scan_modes = ['url', 'file', 'pipe']
    
    def _find_tool(self) -> Optional[str]:
        """Trouve l'exécutable Dalfox"""
        import shutil
        
        # Chemins possibles pour Dalfox
        paths = [
            "dalfox",
            "/usr/local/bin/dalfox",
            "/usr/bin/dalfox",
            "/opt/dalfox/dalfox",
            str(shutil.which("dalfox"))
        ]
        
        for path in paths:
            if path and shutil.which(path):
                return path
        
        return None
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les XSS avec Dalfox
        
        Args:
            target: URL cible
            **kwargs:
                - methods: Liste des méthodes HTTP (GET, POST)
                - depth: Profondeur de crawl
                - concurrency: Nombre de threads
                - blind: Mode blind XSS
                - blind_domain: Domaine pour blind XSS
                - custom_payloads: Payloads personnalisés
                - exclude: Patterns à exclure
                - include: Patterns à inclure
                - follow_redirect: Suivre les redirections
                - timeout: Timeout en secondes
                - output: Fichier de sortie
                - format: Format de sortie (json, html, txt)
        """
        if not self.available:
            return {
                "success": False,
                "error": "Dalfox non installé",
                "vulnerabilities": [],
                "apt_mode": self.apt_mode
            }
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        # Mode APT: ralentir le scan
        if self.apt_mode:
            kwargs.setdefault('concurrency', 3)
            kwargs.setdefault('delay', 2)
        
        cmd = [self.tool_path, "url", target]
        
        # Options de base
        if kwargs.get('methods'):
            methods = kwargs['methods']
            if isinstance(methods, list):
                methods = ','.join(methods)
            cmd.extend(['--method', methods])
        
        # Profondeur de crawl
        depth = kwargs.get('depth', 2)
        if self.apt_mode:
            depth = min(depth, 3)  # Limiter la profondeur en mode APT
        cmd.extend(['--depth', str(depth)])
        
        # Concurrency (threads)
        concurrency = kwargs.get('concurrency', 10)
        if self.apt_mode:
            concurrency = min(concurrency, 5)
        cmd.extend(['--concurrency', str(concurrency)])
        
        # Délai entre les requêtes (mode furtif)
        delay = kwargs.get('delay')
        if delay:
            cmd.extend(['--delay', str(delay)])
        elif self.stealth_config.get('random_delays', False):
            min_delay, max_delay = self.stealth_config.get('delay', (0.5, 1.5))
            avg_delay = (min_delay + max_delay) / 2
            cmd.extend(['--delay', str(round(avg_delay, 1))])
        
        # Mode blind XSS
        if kwargs.get('blind'):
            cmd.append('--blind')
            blind_domain = kwargs.get('blind_domain')
            if blind_domain:
                cmd.extend(['--blind-domain', blind_domain])
        
        # Filtres
        if kwargs.get('exclude'):
            excludes = kwargs['exclude']
            if isinstance(excludes, list):
                for ex in excludes:
                    cmd.extend(['--exclude', ex])
            else:
                cmd.extend(['--exclude', excludes])
        
        if kwargs.get('include'):
            includes = kwargs['include']
            if isinstance(includes, list):
                for inc in includes:
                    cmd.extend(['--include', inc])
            else:
                cmd.extend(['--include', includes])
        
        # Options supplémentaires
        if kwargs.get('follow_redirect'):
            cmd.append('--follow-redirect')
        
        if kwargs.get('verbose'):
            cmd.append('--verbose')
        
        if kwargs.get('quiet') or self.apt_mode:
            cmd.append('--quiet')
        
        if kwargs.get('silent'):
            cmd.append('--silent')
        
        # Format de sortie
        output_format = kwargs.get('format', 'json')
        if output_format == 'json':
            cmd.append('--json')
        elif output_format == 'html':
            cmd.extend(['--format', 'html'])
        
        # Fichier de sortie
        if kwargs.get('output'):
            cmd.extend(['--output', kwargs['output']])
        
        # Payloads personnalisés
        custom_payloads = kwargs.get('custom_payloads')
        if custom_payloads:
            if isinstance(custom_payloads, list):
                for payload in custom_payloads:
                    cmd.extend(['--custom-payload', payload])
            elif isinstance(custom_payloads, str):
                cmd.extend(['--custom-payload', custom_payloads])
        
        # User-Agent personnalisé (furtivité)
        if self.stealth_config.get('stealth', False):
            user_agent = self._get_random_user_agent()
            cmd.extend(['--user-agent', user_agent])
        
        # Proxy (si configuré)
        proxy = self._get_next_proxy()
        if proxy:
            cmd.extend(['--proxy', proxy])
        
        timeout = kwargs.get('timeout', 600)
        
        # Exécution
        result = self.execute_command(cmd, timeout=timeout)
        
        if result["success"]:
            vulnerabilities = self.parse_output(result["stdout"])
            
            # Ajouter les métadonnées APT
            return {
                "success": True,
                "target": target,
                "vulnerabilities": vulnerabilities,
                "count": len(vulnerabilities),
                "raw_output": result["stdout"],
                "execution_time": result.get("execution_time", 0),
                "command_used": ' '.join(cmd),
                "apt_mode": self.apt_mode,
                "stealth_config": self.stealth_config
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Erreur lors du scan"),
                "stderr": result.get("stderr", ""),
                "vulnerabilities": [],
                "apt_mode": self.apt_mode
            }
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse la sortie de Dalfox pour extraire les vulnérabilités XSS
        
        Args:
            output: Sortie brute de Dalfox
            
        Returns:
            Liste des vulnérabilités XSS détectées
        """
        vulnerabilities = []
        
        # Pattern Dalfox typique: [XSS] [url] param=value
        pattern = r'\[XSS\]\s+(https?://[^\s]+)\s+([^\s=]+)=([^\s]+)'
        
        # Pattern pour blind XSS
        blind_pattern = r'\[BLIND\]\s+(https?://[^\s]+)\s+([^\s=]+)=([^\s]+)'
        
        # Pattern pour les paramètres
        param_pattern = r'\[PARAM\]\s+(https?://[^\s]+)\s+([^\s=]+)'
        
        for line in output.split('\n'):
            # XSS normal
            match = re.search(pattern, line)
            if match:
                vuln = self._create_vulnerability(match, "xss")
                vulnerabilities.append(vuln)
                continue
            
            # Blind XSS
            match = re.search(blind_pattern, line)
            if match:
                vuln = self._create_vulnerability(match, "blind_xss")
                vuln["severity"] = "critical"
                vulnerabilities.append(vuln)
                continue
            
            # Paramètre trouvé
            match = re.search(param_pattern, line)
            if match:
                vulnerabilities.append({
                    "type": "parameter_discovery",
                    "url": match.group(1),
                    "parameter": match.group(2),
                    "tool": "dalfox",
                    "severity": "info"
                })
        
        return vulnerabilities
    
    def _create_vulnerability(self, match: re.Match, vuln_type: str) -> Dict[str, Any]:
        """
        Crée un dictionnaire de vulnérabilité à partir d'un match
        
        Args:
            match: Match regex
            vuln_type: Type de vulnérabilité
            
        Returns:
            Dictionnaire de vulnérabilité
        """
        url = match.group(1)
        parameter = match.group(2)
        payload = match.group(3) if len(match.groups()) > 2 else ""
        
        vuln = {
            "type": vuln_type,
            "url": url,
            "parameter": parameter,
            "payload": payload,
            "tool": "dalfox",
            "severity": self._determine_severity(payload)
        }
        
        # Ajouter le contexte si disponible
        if 'script' in payload.lower():
            vuln["context"] = "script"
        elif 'img' in payload.lower() or 'svg' in payload.lower():
            vuln["context"] = "html"
        elif 'onerror' in payload.lower() or 'onload' in payload.lower():
            vuln["context"] = "event_handler"
        else:
            vuln["context"] = "unknown"
        
        return vuln
    
    def _determine_severity(self, payload: str) -> str:
        """
        Détermine la sévérité d'un payload XSS
        
        Args:
            payload: Payload XSS
            
        Returns:
            Niveau de sévérité (critical, high, medium, low)
        """
        payload_lower = payload.lower()
        
        # Critères de haute sévérité
        if any(x in payload_lower for x in ['alert', 'prompt', 'confirm', 'eval']):
            return "high"
        
        # Critères de sévérité moyenne
        if any(x in payload_lower for x in ['script', 'img', 'iframe', 'svg', 'body']):
            return "medium"
        
        # Critères de basse sévérité
        if any(x in payload_lower for x in ['alert', 'xss', 'test']):
            return "low"
        
        return "info"
    
    def blind_scan(self, target: str, domain: str, **kwargs) -> Dict[str, Any]:
        """
        Scan XSS aveugle avec callback
        
        Args:
            target: URL cible
            domain: Domaine pour les callbacks
            **kwargs: Options supplémentaires pour scan()
        """
        kwargs['blind'] = True
        kwargs['blind_domain'] = domain
        return self.scan(target, **kwargs)
    
    def file_scan(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne une liste d'URLs depuis un fichier
        
        Args:
            file_path: Chemin du fichier contenant les URLs
            **kwargs: Options supplémentaires pour scan()
        """
        if not self.available:
            return {"success": False, "error": "Dalfox non installé"}
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        cmd = [self.tool_path, "file", file_path]
        
        # Concurrency
        concurrency = kwargs.get('concurrency', 10)
        if self.apt_mode:
            concurrency = min(concurrency, 5)
        cmd.extend(['--concurrency', str(concurrency)])
        
        # Délai entre les requêtes
        delay = kwargs.get('delay')
        if delay:
            cmd.extend(['--delay', str(delay)])
        
        # Mode blind
        if kwargs.get('blind'):
            cmd.append('--blind')
        
        # Format JSON
        if kwargs.get('format') == 'json':
            cmd.append('--json')
        
        # User-Agent personnalisé
        if self.stealth_config.get('stealth', False):
            user_agent = self._get_random_user_agent()
            cmd.extend(['--user-agent', user_agent])
        
        timeout = kwargs.get('timeout', 900)
        
        result = self.execute_command(cmd, timeout=timeout)
        
        if result["success"]:
            vulnerabilities = self.parse_output(result["stdout"])
            return {
                "success": True,
                "vulnerabilities": vulnerabilities,
                "count": len(vulnerabilities),
                "file": file_path,
                "execution_time": result.get("execution_time", 0)
            }
        
        return {
            "success": False,
            "error": result.get("error", "Erreur lors du scan"),
            "file": file_path
        }
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de version de Dalfox
        
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
                "tool": "dalfox",
                "path": self.tool_path
            }
        
        return {"available": False, "error": result.get("error")}
    
    def generate_payloads(self, count: int = 10) -> List[str]:
        """
        Génère des payloads XSS personnalisés pour Dalfox
        
        Args:
            count: Nombre de payloads à générer
            
        Returns:
            Liste de payloads XSS
        """
        base_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<iframe src='javascript:alert(\"XSS\")'>",
            "<a href='javascript:alert(\"XSS\")'>click</a>",
            "<div onmouseover='alert(\"XSS\")'>hover</div>",
            "javascript:alert('XSS')",
            "<ScRiPt>alert('XSS')</ScRiPt>"
        ]
        
        # Variations pour augmenter le nombre
        variations = []
        for payload in base_payloads[:count]:
            variations.append(payload)
            variations.append(payload.upper())
            variations.append(payload.lower())
            variations.append(payload.replace('alert', 'prompt'))
            variations.append(payload.replace('alert', 'confirm'))
        
        return list(set(variations))[:count]


# Fonction utilitaire pour créer un fichier d'URLs pour Dalfox
def create_url_file(urls: List[str], output_file: str) -> str:
    """
    Crée un fichier contenant une liste d'URLs pour Dalfox
    
    Args:
        urls: Liste des URLs
        output_file: Chemin du fichier de sortie
        
    Returns:
        Chemin du fichier créé
    """
    with open(output_file, 'w') as f:
        for url in urls:
            f.write(url + '\n')
    return output_file