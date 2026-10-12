#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques PostMessage pour RedForge
Détecte et exploite les vulnérabilités liées à l'API PostMessage
Version avec support furtif, APT et analyse avancée
"""

import re
import time
import random
import requests
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from collections import defaultdict

@dataclass
class PostMessageConfig:
    """Configuration avancée pour la détection PostMessage"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_scripts: Tuple[float, float] = (1, 3)
    
    # Comportement
    deep_scan: bool = True
    extract_external_scripts: bool = True
    analyze_event_handlers: bool = True
    max_scripts: int = 50
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_csrf_via_postmessage: bool = True
    analyze_message_chains: bool = True
    test_origin_validation: bool = True
    detect_dom_based_vulnerabilities: bool = True


class PostMessageAttacks:
    """Détection et exploitation avancée des vulnérabilités PostMessage"""
    
    def __init__(self, config: Optional[PostMessageConfig] = None):
        """
        Initialise le détecteur de vulnérabilités PostMessage
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or PostMessageConfig()
        
        # Patterns PostMessage
        self.postmessage_patterns = [
            r'\.postMessage\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)',
            r'window\.parent\.postMessage',
            r'window\.opener\.postMessage',
            r'addEventListener\s*\(\s*[\'"]message[\'"]',
            r'onmessage\s*=',
            r'contentWindow\.postMessage',
            r'\.postMessage\s*\(\s*([^,]+)\s*,\s*\[',
            r'postMessage\s*\(\s*\{[^}]+\}\s*,\s*[\'"]',
            r'parent\.postMessage'
        ]
        
        # Patterns dangereux
        self.dangerous_patterns = [
            (r'\.postMessage\s*\(\s*[^,]+,\s*[\'"]\*[\'"]', 'wildcard_target_origin', 'CRITICAL'),
            (r'\.postMessage\s*\(\s*[^,]+,\s*[^/\'"]', 'no_origin_validation', 'HIGH'),
            (r'ev\.origin\s*===\s*[\'"]http://', 'weak_origin_check_http', 'HIGH'),
            (r'ev\.origin\s*\.indexOf\s*\(\s*[\'"]', 'partial_origin_check', 'MEDIUM'),
            (r'eval\s*\(\s*data', 'eval_of_message_data', 'CRITICAL'),
            (r'innerHTML\s*=\s*data', 'html_injection', 'HIGH'),
            (r'document\.write\s*\(\s*data', 'document_write_injection', 'HIGH'),
            (r'new\s+Function\s*\(\s*data', 'function_constructor', 'CRITICAL'),
            (r'setTimeout\s*\(\s*data', 'settimeout_string', 'HIGH'),
            (r'setInterval\s*\(\s*data', 'setinterval_string', 'HIGH'),
            (r'ev\.origin\s*===', 'origin_validation_present', 'INFO'),
            (r'ev\.origin\s*!==', 'origin_mismatch_handling', 'INFO')
        ]
        
        # Patterns d'origines
        self.origin_patterns = [
            r'\.postMessage\s*\(\s*[^,]+,\s*[\'"]([^\'"]+)[\'"]',
            r'targetOrigin\s*:\s*[\'"]([^\'"]+)[\'"]',
            r'if\s*\(\s*ev\.origin\s*===\s*[\'"]([^\'"]+)[\'"]',
            r'if\s*\(\s*ev\.origin\s*\.indexOf\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'allowedOrigins\.includes\s*\(\s*ev\.origin\s*\)',
            r'origin\s*===\s*[\'"]([^\'"]+)[\'"]'
        ]
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        # Métriques
        self.start_time = None
        self.scripts_analyzed = 0
        self.vulnerabilities_found = 0
        self.postmessage_usages = 0
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités PostMessage
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - deep: Analyse approfondie du JavaScript
                - intercept: Intercepter les messages
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.scripts_analyzed = 0
        self.vulnerabilities_found = 0
        self.postmessage_usages = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Analyse des vulnérabilités PostMessage sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Analyse discrète")
        
        vulnerabilities = []
        postmessage_found = []
        message_listeners = []
        
        # Récupérer le code JavaScript de la page
        js_code, scripts = self._extract_javascript(target, **kwargs)
        
        # Rechercher les utilisations de postMessage
        for pattern in self.postmessage_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE | re.DOTALL)
            for match in matches:
                self.postmessage_usages += 1
                postmessage_found.append({
                    "pattern": pattern,
                    "code": match if isinstance(match, str) else str(match)[:500]
                })
        
        # Analyser les vulnérabilités
        for item in postmessage_found:
            for pattern, vuln_type, severity in self.dangerous_patterns:
                if re.search(pattern, item['code'], re.IGNORECASE):
                    self.vulnerabilities_found += 1
                    vulnerabilities.append({
                        "type": vuln_type,
                        "severity": severity,
                        "details": f"Pattern détecté: {pattern}",
                        "code": item['code'][:300],
                        "risk_score": self._get_risk_score(severity)
                    })
                    print(f"      ✓ PostMessage vulnérable: {vuln_type}")
        
        # Extraire les origines autorisées
        origins = self._extract_allowed_origins(js_code)
        if '*' in origins:
            self.vulnerabilities_found += 1
            vulnerabilities.append({
                "type": "wildcard_origin",
                "severity": "CRITICAL",
                "details": "Target origin '*' - Accepte tout domaine",
                "origins": origins,
                "risk_score": 95
            })
            print(f"      ✓ Wildcard origin dans postMessage")
        
        # Analyser les écouteurs de messages
        if self.config.analyze_event_handlers:
            listeners = self._analyze_message_listeners(js_code)
            message_listeners = listeners
            for listener in listeners:
                if listener.get('vulnerable'):
                    self.vulnerabilities_found += 1
                    vulnerabilities.append(listener)
                    print(f"      ✓ Écouteur vulnérable: {listener['details'][:50]}")
        
        # Détection CSRF via PostMessage
        if self.config.detect_csrf_via_postmessage:
            csrf_vulns = self._detect_csrf_via_postmessage(js_code, target)
            for vuln in csrf_vulns:
                self.vulnerabilities_found += 1
                vulnerabilities.append(vuln)
                print(f"      ✓ CSRF via PostMessage: {vuln['details'][:50]}")
        
        # Analyser les chaînes de messages
        if self.config.analyze_message_chains:
            chains = self._analyze_message_chains(js_code)
            if chains:
                vulnerabilities.append({
                    "type": "message_chains",
                    "severity": "MEDIUM",
                    "details": f"Chaînes de messages détectées: {len(chains)}",
                    "chains": chains[:3],
                    "risk_score": 65
                })
        
        return self._generate_results(target, vulnerabilities, postmessage_found, 
                                     origins, message_listeners)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'deep' in kwargs:
            self.config.deep_scan = kwargs['deep']
        if 'extract_external_scripts' in kwargs:
            self.config.extract_external_scripts = kwargs['extract_external_scripts']
        if 'max_scripts' in kwargs:
            self.config.max_scripts = kwargs['max_scripts']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.delay_between_scripts = (5, 15)
            self.config.max_scripts = 20  # Limiter en mode APT
    
    def _get_stealth_headers(self, additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Génère des headers furtifs"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        if self.config.random_user_agents:
            headers['User-Agent'] = random.choice(self.user_agents)
        
        if self.config.stealth_headers:
            headers['Cache-Control'] = 'no-cache'
            headers['Pragma'] = 'no-cache'
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _extract_javascript(self, target: str, **kwargs) -> Tuple[str, List[Dict]]:
        """
        Extrait le code JavaScript de la page
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        js_code = ""
        scripts_info = []
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Scripts inline
            for script in soup.find_all('script'):
                if script.string:
                    js_code += script.string + "\n"
                    self.scripts_analyzed += 1
                    scripts_info.append({
                        "type": "inline",
                        "size": len(script.string)
                    })
            
            # Scripts externes
            if self.config.extract_external_scripts:
                external_scripts = soup.find_all('script', src=True)
                for idx, script in enumerate(external_scripts[:self.config.max_scripts]):
                    src = script['src']
                    if not src.startswith(('http://', 'https://')):
                        src = urljoin(target, src)
                    
                    # Pause APT
                    if self.config.apt_mode and idx > 0:
                        self._apt_pause()
                    elif self.config.random_delays and idx > 0:
                        time.sleep(random.uniform(*self.config.delay_between_scripts))
                    
                    try:
    