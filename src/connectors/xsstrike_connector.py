#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour XSStrike - Scan XSS avancé avec analyse de contexte
Version avec support furtif, APT et détection avancée
"""

import re
import json
import random
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.connectors.base_connector import BaseConnector


class XSStrikeConnector(BaseConnector):
    """Connecteur avancé pour XSStrike avec support furtif"""
    
    def __init__(self, tool_path: Optional[str] = None):
        """
        Initialise le connecteur XSStrike
        
        Args:
            tool_path: Chemin personnalisé vers l'exécutable XSStrike
        """
        super().__init__(tool_path)
        self.scan_levels = {
            1: "Low (basic payloads)",
            2: "Medium (common vectors)",
            3: "High (aggressive, more payloads)"
        }
    
    def _find_tool(self) -> Optional[str]:
        """Trouve l'exécutable XSStrike"""
        import shutil
        
        # XSStrike est généralement un script Python
        paths = [
            "xsstrike",
            "/usr/local/bin/xsstrike",
            "/opt/XSStrike/xsstrike.py",
            "/opt/xsstrike/xsstrike.py",
            "/usr/share/xsstrike/xsstrike.py"
        ]
        
        for path in paths:
            if path and shutil.which(path):
                return path
        
        # Chercher xsstrike.py
        python_path = shutil.which("python3")
        if python_path:
            import subprocess
            try:
                result = subprocess.run(
                    ["find", "/opt", "/usr", "-name", "xsstrike.py"], 
                    capture_output=True, text=True, timeout=5
                )
                if result.stdout.strip():
                    xsstrike_path = result.stdout.strip().split('\n')[0]
                    return f"{python_path} {xsstrike_path}"
            except:
                pass
        
        return None
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les XSS avec XSStrike
        
        Args:
            target: URL cible
            **kwargs:
                - data: Données POST
                - params: Paramètres à tester
                - level: Niveau de scan (1-3)
                - encode: Encodage des payloads
                - blind: Mode blind XSS
                - timeout: Timeout en secondes
                - proxy: Proxy à utiliser
                - headers: Headers personnalisés
                - cookies: Cookies à utiliser
        """
        if not self.available:
            return {
                "success": False,
                "error": "XSStrike non installé",
                "vulnerabilities": [],
                "apt_mode": self.apt_mode
            }
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        cmd = [self.tool_path, "-u", target]
        
        # Mode APT: réduire l'agressivité
        if self.apt_mode:
            kwargs.setdefault('level', 1)
            kwargs.setdefault('encode', False)
            kwargs.setdefault('verbose', False)
        
        # Données POST
        data = kwargs.get('data')
        if data:
            cmd.extend(["--data", data])
        
        # Paramètres spécifiques
        params = kwargs.get('params')
        if params:
            if isinstance(params, list):
                params = ','.join(params)
            cmd.extend(["--params", params])
        
        # Niveau de scan
        level = kwargs.get('level', 2)
        level = max(1, min(3, level))  # Entre 1 et 3
        cmd.extend(["--level", str(level)])
        
        # Options
        if kwargs.get('encode'):
            cmd.append("--encode")
        
        if kwargs.get('blind'):
            cmd.append("--blind")
        
        if kwargs.get('json'):
            cmd.append("--json")
        
        if kwargs.get('verbose'):
            cmd.append("--verbose")
        elif self.apt_mode:
            cmd.append("--quiet")
        
        if kwargs.get('skip_dom'):
            cmd.append("--skip-dom")
        
        if kwargs.get('skip_headers'):
            cmd.append("--skip-headers")
        
        if kwargs.get('skip_dom'):
            cmd.append("--skip-dom")
        
        # Headers personnalisés
        headers = kwargs.get('headers', {})
        if self.stealth_config.get('stealth', False):
            headers['User-Agent'] = self._get_random_user_agent()
        
        for key, value in headers.items():
            cmd.extend(["--headers", f"{key}: {value}"])
        
        # Cookies
        cookies = kwargs.get('cookies')
        if cookies:
            if isinstance(cookies, dict):
                cookie_str = '; '.join([f"{k}={v}" for k, v in cookies.items()])
            else:
                cookie_str = cookies
            cmd.extend(["--cookies", cookie_str])
        
        # Proxy
        proxy = kwargs.get('proxy')
        if proxy:
            cmd.extend(["--proxy", proxy])
        elif self.proxy_rotation:
            proxy = self._get_next_proxy()
            if proxy:
                cmd.extend(["--proxy", proxy])
        
        # Timeout
        cmd.extend(["--timeout", str(kwargs.get('timeout', 30))])
        
        # Threads
        threads = kwargs.get('threads', 10)
        if self.apt_mode:
            threads = min(threads, 3)
        cmd.extend(["--threads", str(threads)])
        
        # Delay (mode furtif)
        delay = kwargs.get('delay')
        if delay:
            cmd.extend(["--delay", str(delay)])
        elif self.stealth_config.get('random_delays', False):
            min_delay, max_delay = self.stealth_config.get('delay', (0.5, 1.5))
            avg_delay = (min_delay + max_delay) / 2
            cmd.extend(["--delay", str(round(avg_delay, 1))])
        
        # Sortie JSON
        if kwargs.get('json_output'):
            cmd.append("--json")
        
        timeout = kwargs.get('execution_timeout', 300)
        
        # Exécution
        result = self.execute_command(cmd, timeout=timeout)
        
        if result["success"]:
            vulnerabilities = self.parse_output(result["stdout"])
            return {
                "success": True,
                "target": target,
                "vulnerabilities": vulnerabilities,
                "count": len(vulnerabilities),
                "raw_output": result["stdout"],
                "execution_time": result.get("execution_time", 0),
                "command_used": ' '.join(cmd),
                "apt_mode": self.apt_mode,
                "level_used": level
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
        Parse la sortie de XSStrike
        
        Args:
            output: Sortie brute de XSStrike
            
        Returns:
            Liste des vulnérabilités XSS détectées
        """
        vulnerabilities = []
        
        # Pattern pour XSS détectés
        xss_pattern = r'\[XSS\] found in ([\w]+) parameter:\s+(.+)'
        dom_pattern = r'\[DOM XSS\] found in ([\w]+):\s+(.+)'
        
        # Pattern pour payloads
        payload_pattern = r'Payload:\s+(.+)'
        
        # Pattern pour contexte
        context_pattern = r'Context:\s+(.+)'
        
        current_vuln = {}
        
        for line in output.split('\n'):
            # XSS classique
            match = re.search(xss_pattern, line)
            if match:
                vuln = {
                    "type": "reflected_xss",
                    "parameter": match.group(1),
                    "payload": match.group(2),
                    "tool": "xsstrike",
                    "severity": "high",
                    "confidence": 85
                }
                vulnerabilities.append(vuln)
                continue
            
            # DOM XSS
            dom_match = re.search(dom_pattern, line)
            if dom_match:
                vuln = {
                    "type": "dom_xss",
                    "source": dom_match.group(1),
                    "payload": dom_match.group(2),
                    "tool": "xsstrike",
                    "severity": "medium",
                    "confidence": 70
                }
                vulnerabilities.append(vuln)
                continue
            
            # Payload (pour enrichir)
            payload_match = re.search(payload_pattern, line)
            if payload_match and current_vuln:
                current_vuln['payload_detail'] = payload_match.group(1)
            
            # Contexte
            context_match = re.search(context_pattern, line)
            if context_match and current_vuln:
                current_vuln['context'] = context_match.group(1)
                vulnerabilities.append(current_vuln)
                current_vuln = {}
        
        # Détection des headers vulnérables
        header_pattern = r'\[XSS\] found in header: (.+)'
        header_match = re.search(header_pattern, output)
        if header_match:
            vulnerabilities.append({
                "type": "header_xss",
                "header": header_match.group(1),
                "tool": "xsstrike",
                "severity": "high",
                "confidence": 80
            })
        
        return vulnerabilities
    
    def scan_post(self, target: str, data: str, **kwargs) -> Dict[str, Any]:
        """
        Scan XSS sur requête POST
        
        Args:
            target: URL cible
            data: Données POST
            **kwargs: Options supplémentaires
        """
        return self.scan(target, data=data, **kwargs)
    
    def scan_parameters(self, target: str, params: List[str], **kwargs) -> Dict[str, Any]:
        """
        Scan des paramètres spécifiques
        
        Args:
            target: URL cible
            params: Liste des paramètres à tester
            **kwargs: Options supplémentaires
        """
        return self.scan(target, params=params, **kwargs)
    
    def dom_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scan spécifique pour DOM XSS
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        kwargs['skip_dom'] = False
        return self.scan(target, **kwargs)
    
    def blind_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scan XSS aveugle
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        kwargs['blind'] = True
        return self.scan(target, **kwargs)
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de version de XSStrike
        
        Returns:
            Dictionnaire avec les informations de version
        """
        if not self.available:
            return {"available": False}
        
        # XSStrike n'a pas de flag --version standard
        result = self.execute_command([self.tool_path, "--help"], stealth=False)
        
        if result["success"]:
            return {
                "available": True,
                "version": "unknown",
                "tool": "xsstrike",
                "path": self.tool_path,
                "help_preview": result["stdout"][:200]
            }
        
        return {"available": False, "error": result.get("error")}
    
    def get_scan_levels(self) -> Dict[int, str]:
        """
        Retourne les niveaux de scan disponibles
        
        Returns:
            Dictionnaire des niveaux de scan
        """
        return self.scan_levels