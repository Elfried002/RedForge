#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour wafw00f - Détection de WAF (Web Application Firewall)
Version avec support furtif, APT et détection avancée
"""

import re
import json
import random
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.connectors.base_connector import BaseConnector


class WafW00fConnector(BaseConnector):
    """Connecteur avancé pour wafw00f avec support furtif"""
    
    def __init__(self, tool_path: Optional[str] = None):
        """
        Initialise le connecteur wafw00f
        
        Args:
            tool_path: Chemin personnalisé vers l'exécutable wafw00f
        """
        super().__init__(tool_path)
        
        # Base de données des WAFs connus avec leurs fabricants
        self.waf_database = {
            'Cloudflare': {'manufacturer': 'Cloudflare, Inc.', 'bypass_difficulty': 'high'},
            'AWS WAF': {'manufacturer': 'Amazon Web Services', 'bypass_difficulty': 'high'},
            'ModSecurity': {'manufacturer': 'Trustwave', 'bypass_difficulty': 'medium'},
            'Imperva': {'manufacturer': 'Imperva', 'bypass_difficulty': 'high'},
            'F5 BIG-IP ASM': {'manufacturer': 'F5 Networks', 'bypass_difficulty': 'high'},
            'Akamai': {'manufacturer': 'Akamai Technologies', 'bypass_difficulty': 'high'},
            'Sucuri': {'manufacturer': 'Sucuri Inc.', 'bypass_difficulty': 'medium'},
            'Wordfence': {'manufacturer': 'Defiant Inc.', 'bypass_difficulty': 'medium'},
            'Barracuda': {'manufacturer': 'Barracuda Networks', 'bypass_difficulty': 'medium'},
            'Fortinet': {'manufacturer': 'Fortinet, Inc.', 'bypass_difficulty': 'high'},
            'Citrix NetScaler': {'manufacturer': 'Citrix Systems', 'bypass_difficulty': 'high'},
            'Radware': {'manufacturer': 'Radware Ltd.', 'bypass_difficulty': 'high'},
            'NSFocus': {'manufacturer': 'NSFocus', 'bypass_difficulty': 'medium'},
            'Reblaze': {'manufacturer': 'Reblaze', 'bypass_difficulty': 'medium'},
            'StackPath': {'manufacturer': 'StackPath', 'bypass_difficulty': 'medium'},
            'Baidu': {'manufacturer': 'Baidu, Inc.', 'bypass_difficulty': 'low'},
            'Safedog': {'manufacturer': 'Safedog', 'bypass_difficulty': 'low'},
            'Yundun': {'manufacturer': 'Yundun', 'bypass_difficulty': 'low'},
            'Unknown': {'manufacturer': 'Unknown', 'bypass_difficulty': 'unknown'}
        }
    
    def _find_tool(self) -> Optional[str]:
        """Trouve l'exécutable wafw00f"""
        import shutil
        
        paths = [
            "wafw00f",
            "/usr/local/bin/wafw00f",
            "/usr/bin/wafw00f",
            "/opt/wafw00f/wafw00f"
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
                    ["find", "/usr", "-name", "wafw00f.py"], 
                    capture_output=True, text=True, timeout=5
                )
                if result.stdout.strip():
                    return f"python3 {result.stdout.strip()}"
            except:
                pass
        
        return None
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Détecte la présence d'un WAF
        
        Args:
            target: URL cible
            **kwargs:
                - verbose: Mode verbeux
                - find_all: Chercher tous les WAFs possibles
                - timeout: Timeout en secondes
                - proxy: Proxy à utiliser
        """
        if not self.available:
            return {
                "success": False,
                "error": "wafw00f non installé",
                "waf_detected": False,
                "apt_mode": self.apt_mode
            }
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        cmd = [self.tool_path]
        
        # Mode APT: moins de bruit
        if self.apt_mode:
            kwargs['verbose'] = False
            kwargs['find_all'] = False
        
        if kwargs.get('find_all'):
            cmd.append('-a')
        
        if kwargs.get('verbose'):
            cmd.append('-v')
        elif self.apt_mode:
            cmd.append('-q')  # Mode silencieux
        
        # Proxy
        proxy = kwargs.get('proxy')
        if proxy:
            cmd.extend(['-p', proxy])
        elif self.proxy_rotation:
            proxy = self._get_next_proxy()
            if proxy:
                cmd.extend(['-p', proxy])
        
        cmd.append(target)
        
        timeout = kwargs.get('timeout', 60)
        
        # Exécution
        result = self.execute_command(cmd, timeout=timeout)
        
        if result["success"] or result["returncode"] == 0:
            parsed = self.parse_output(result["stdout"])
            return {
                "success": True,
                "target": target,
                "waf_detected": parsed.get("waf_detected", False),
                "waf_name": parsed.get("waf_name"),
                "waf_manufacturer": parsed.get("waf_manufacturer"),
                "bypass_difficulty": parsed.get("bypass_difficulty"),
                "raw_output": result["stdout"],
                "execution_time": result.get("execution_time", 0),
                "command_used": ' '.join(cmd),
                "apt_mode": self.apt_mode
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Erreur lors de la détection"),
                "stderr": result.get("stderr", ""),
                "waf_detected": False,
                "apt_mode": self.apt_mode
            }
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse la sortie de wafw00f
        
        Args:
            output: Sortie brute de wafw00f
            
        Returns:
            Dictionnaire structuré des résultats
        """
        result = {
            "waf_detected": False,
            "waf_name": None,
            "waf_manufacturer": None,
            "bypass_difficulty": None
        }
        
        # Pattern pour détection positive: [+] Web Application Firewall: Cloudflare
        positive_pattern = r'\[\+\]\s+Web Application Firewall:\s+(.+)'
        
        # Pattern pour détection négative: [-] Web Application Firewall: No
        negative_pattern = r'\[\-\]\s+Web Application Firewall:\s+(.+)'
        
        # Pattern pour détection multiple: [X] Web Application Firewall: Cloudflare
        multi_pattern = r'\[[Xx]\]\s+Web Application Firewall:\s+(.+)'
        
        for line in output.split('\n'):
            # Détection positive
            match = re.search(positive_pattern, line)
            if match:
                waf_info = match.group(1)
                result["waf_detected"] = True
                result["waf_name"] = waf_info
                break
            
            # Détection multiple
            match = re.search(multi_pattern, line)
            if match:
                waf_info = match.group(1)
                if waf_info != "No":
                    result["waf_detected"] = True
                    result["waf_name"] = waf_info
                    break
            
            # Détection négative
            match = re.search(negative_pattern, line)
            if match:
                waf_info = match.group(1)
                result["waf_detected"] = False
                result["waf_name"] = None
                break
        
        # Enrichir avec les informations de la base de données
        if result["waf_detected"] and result["waf_name"]:
            for known_waf, info in self.waf_database.items():
                if known_waf.lower() in result["waf_name"].lower():
                    result["waf_manufacturer"] = info['manufacturer']
                    result["bypass_difficulty"] = info['bypass_difficulty']
                    break
            else:
                result["waf_manufacturer"] = self.waf_database['Unknown']['manufacturer']
                result["bypass_difficulty"] = self.waf_database['Unknown']['bypass_difficulty']
        
        return result
    
    def detect_all(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Détecte tous les WAFs possibles
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        kwargs['find_all'] = True
        return self.scan(target, **kwargs)
    
    def get_bypass_techniques(self, waf_name: str) -> Dict[str, Any]:
        """
        Retourne les techniques de contournement pour un WAF spécifique
        
        Args:
            waf_name: Nom du WAF détecté
            
        Returns:
            Dictionnaire avec les techniques de bypass
        """
        bypass_techniques = {
            "Cloudflare": {
                "difficulty": "high",
                "techniques": [
                    "Utiliser l'adresse IP d'origine via Cloudflare Workers",
                    "Contournement via cache poisoning",
                    "Exploiter les vulnérabilités de Cloudflare Workers",
                    "Utiliser des requêtes HTTP/2 pour contourner les règles",
                    "Contourner les rate limits avec des IPs distribuées"
                ],
                "tools": ["cf-bypass", "cloudflare-bypass", "gofuckyourself"],
                "references": [
                    "https://github.com/Eloston/cloudflare-bypass",
                    "https://github.com/5cr1pt/cloudflare-bypass"
                ]
            },
            "ModSecurity": {
                "difficulty": "medium",
                "techniques": [
                    "Évasion par encodage multiple (double URL encoding)",
                    "Contournement des règles CRS (Core Rule Set)",
                    "Exploitation des regex mal configurées",
                    "Utilisation de caractères de tabulation ou newline",
                    "Fractionnement des payloads sur plusieurs lignes"
                ],
                "tools": ["modsec-bypass", "bypass-modsecurity"],
                "references": [
                    "https://github.com/SpiderLabs/owasp-modsecurity-crs",
                    "https://www.modsecurity.org/CRS/Documentation/"
                ]
            },
            "AWS WAF": {
                "difficulty": "high",
                "techniques": [
                    "Exploitation des limites de taille des requêtes",
                    "Contournement des patterns géographiques",
                    "Attaques par fragmentation TCP",
                    "Utilisation de headers malformés",
                    "Exploitation des règles d'IP autorisées"
                ],
                "tools": ["aws-waf-bypass"],
                "references": [
                    "https://aws.amazon.com/waf/",
                    "https://github.com/aws-samples/aws-waf-security-automations"
                ]
            },
            "Imperva": {
                "difficulty": "high",
                "techniques": [
                    "Exploitation des IPs autorisées",
                    "Contournement via API non protégées",
                    "Évasion des signatures avec des encodages exotiques",
                    "Utilisation de requêtes HTTP pipelining",
                    "Contournement des rate limits"
                ],
                "tools": ["imperva-bypass"],
                "references": [
                    "https://www.imperva.com/products/web-application-firewall-waf/"
                ]
            },
            "F5 BIG-IP ASM": {
                "difficulty": "high",
                "techniques": [
                    "Contournement des signatures par fragmentation",
                    "Exploitation des vulnérabilités de parsing",
                    "Utilisation de méthodes HTTP alternatives",
                    "Évasion des patterns de détection"
                ],
                "tools": ["f5-bypass"],
                "references": [
                    "https://www.f5.com/products/security/advanced-waf"
                ]
            },
            "Akamai": {
                "difficulty": "high",
                "techniques": [
                    "Contournement via Edge Workers",
                    "Exploitation des erreurs de configuration",
                    "Utilisation de requêtes malformées",
                    "Bypass des rate limits"
                ],
                "tools": ["akamai-bypass"],
                "references": [
                    "https://www.akamai.com/products/web-application-firewall"
                ]
            }
        }
        
        waf_found = None
        for known_waf in bypass_techniques:
            if known_waf.lower() in waf_name.lower():
                waf_found = known_waf
                break
        
        if waf_found:
            return {
                "waf_name": waf_name,
                "difficulty": bypass_techniques[waf_found]["difficulty"],
                "techniques": bypass_techniques[waf_found]["techniques"],
                "tools": bypass_techniques[waf_found].get("tools", []),
                "references": bypass_techniques[waf_found].get("references", [])
            }
        else:
            return {
                "waf_name": waf_name,
                "difficulty": "unknown",
                "techniques": [
                    "Tester les payloads encodés (URL, Unicode, Hex)",
                    "Utiliser des techniques de fragmentation",
                    "Contourner avec des paramètres malformés",
                    "Essayer différentes méthodes HTTP",
                    "Fractionner les attaques en plusieurs requêtes"
                ],
                "tools": [],
                "references": []
            }
    
    def get_waf_database(self) -> Dict[str, Any]:
        """
        Retourne la base de données des WAFs connus
        
        Returns:
            Dictionnaire des WAFs connus
        """
        return self.waf_database
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de version de wafw00f
        
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
                "tool": "wafw00f",
                "path": self.tool_path
            }
        
        return {"available": False, "error": result.get("error")}
    
    def quick_detect(self, target: str) -> Dict[str, Any]:
        """
        Détection rapide sans options supplémentaires
        
        Args:
            target: URL cible
            
        Returns:
            Résultat de la détection
        """
        return self.scan(target, find_all=False, verbose=False)