#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de découverte d'API pour RedForge
Détecte les endpoints REST, GraphQL, SOAP et autres APIs
Version avec support furtif, APT et détection avancée
"""

import re
import json
import time
import random
import requests
from typing import Dict, Any, List, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from src.core.stealth_engine import StealthEngine


class APIDiscovery:
    """Découverte avancée d'endpoints API avec support furtif"""
    
    def __init__(self):
        # Chemins API communs
        self.common_api_paths = [
            # REST API
            "/api", "/api/v1", "/api/v2", "/api/v3", "/rest", "/rest/v1",
            "/v1/api", "/v2/api", "/api/v1.0", "/api/v2.0", "/apiv1", "/apiv2",
            "/api/rest", "/api/json", "/api/xml", "/api/data", "/api/service",
            "/api/public", "/api/private", "/api/internal", "/api/external",
            "/api/admin", "/api/user", "/api/auth", "/api/config",
            # GraphQL
            "/graphql", "/graphiql", "/gql", "/graph", "/v1/graphql",
            "/graphql/console", "/graphql/playground", "/graphql/explorer",
            # SOAP
            "/soap", "/wsdl", "/service.asmx", "/webservice", "/soap-api",
            "/services", "/Service", "/WebServices",
            # Swagger/OpenAPI
            "/swagger", "/swagger-ui", "/swagger.json", "/swagger.yaml",
            "/openapi", "/openapi.json", "/openapi.yaml", "/api-docs",
            "/docs", "/api/docs", "/documentation", "/redoc",
            "/swagger-ui.html", "/swagger-ui/index.html",
            # Admin/Management
            "/admin/api", "/manage/api", "/management/api", "/system/api",
            # Authentication
            "/auth", "/login", "/oauth", "/token", "/api/token",
            "/authenticate", "/api/auth", "/v1/auth", "/oauth2/token",
            "/oauth/authorize", "/oauth/callback",
            # Common endpoints
            "/users", "/user", "/profile", "/account", "/me",
            "/posts", "/comments", "/products", "/orders", "/items",
            "/search", "/query", "/filter", "/list", "/get", "/post",
            "/upload", "/download", "/file", "/files", "/media",
            "/config", "/settings", "/preferences", "/options",
            "/status", "/health", "/ping", "/version", "/info",
            "/metrics", "/stats", "/logs", "/debug", "/trace"
        ]
        
        # Patterns de détection
        self.api_patterns = {
            "graphql": [r'(query|mutation|subscription)\s*\{', r'__typename', r'__schema'],
            "rest": [r'/(?:api|rest|v\d+)/[a-z]+', r'"method":"(?:GET|POST|PUT|DELETE)"', r'"endpoint":"'],
            "json": [r'\.json$', r'application/json', r'{"data":', r'{"results":'],
            "xml": [r'\.xml$', r'application/xml', r'<\?xml', r'<soap:'],
            "swagger": [r'swagger', r'openapi', r'"swagger":"', r'"openapi":"']
        }
        
        # Headers d'API
        self.api_headers = [
            'application/json', 'application/xml', 'application/ld+json',
            'application/hal+json', 'application/vnd.api+json', 'application/graphql',
            'application/soap+xml', 'text/xml', 'text/plain'
        ]
        
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
    
    def discover(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Découvre les endpoints API sur la cible
        
        Args:
            target: URL cible
            **kwargs:
                - wordlist: Wordlist personnalisée
                - threads: Nombre de threads
                - spider: Crawler l'application
                - deep_scan: Scan approfondi
        """
        print(f"  → Découverte d'API sur {target}")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Scan lent et discret")
        
        # Nettoyer l'URL
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        target = target.rstrip('/')
        
        discovered_endpoints = set()
        
        # Méthode 1: Wordlist d'endpoints communs
        wordlist = kwargs.get('wordlist', self.common_api_paths)
        threads = min(kwargs.get('threads', 10), 5 if self.apt_mode else 10)
        
        print(f"    → Test de {len(wordlist)} endpoints communs...")
        wordlist_results = self._check_endpoints(target, wordlist, threads)
        discovered_endpoints.update(wordlist_results)
        
        # Méthode 2: Découverte via crawling
        if kwargs.get('spider', True):
            print(f"    → Crawling de l'application...")
            spider_results = self._crawl_for_apis(target)
            discovered_endpoints.update(spider_results)
        
        # Méthode 3: Détection via headers et réponses
        if kwargs.get('deep_scan', True):
            print(f"    → Analyse des réponses...")
            detected_results = self._detect_api_from_responses(target)
            discovered_endpoints.update(detected_results)
        
        # Analyser chaque endpoint trouvé
        analyzed_endpoints = []
        endpoints_list = list(discovered_endpoints)
        
        for idx, endpoint in enumerate(endpoints_list):
            if self.apt_mode and idx > 0:
                self._apply_stealth_delay()
            analysis = self._analyze_endpoint(target, endpoint)
            analyzed_endpoints.append(analysis)
        
        # Détection GraphQL spécifique
        graphql_endpoints = self._detect_graphql(target, discovered_endpoints)
        
        # Détection Swagger/OpenAPI
        swagger_endpoints = self._detect_swagger(target, discovered_endpoints)
        
        return {
            "target": target,
            "endpoints": analyzed_endpoints,
            "graphql_endpoints": graphql_endpoints,
            "swagger_endpoints": swagger_endpoints,
            "count": len(analyzed_endpoints),
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "summary": self._generate_summary(analyzed_endpoints)
        }
    
    def _check_endpoints(self, base_url: str, paths: List[str], threads: int) -> Set[str]:
        """Vérifie une liste d'endpoints"""
        found = set()
        tested = 0
        
        def check_path(path):
            url = urljoin(base_url, path)
            try:
                headers = self._get_headers()
                response = requests.get(url, headers=headers, timeout=5, allow_redirects=False, verify=False)
                if response.status_code not in [404, 410, 500, 502, 503]:
                    return (url, response.status_code)
            except:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(check_path, path): path for path in paths}
            
            for future in as_completed(futures):
                result = future.result()
                tested += 1
                if result:
                    url, status = result
                    found.add(url)
                    if status in [200, 201, 202, 203, 204]:
                        print(f"      ✓ API trouvée: {url} (HTTP {status})")
                
                # Délai furtif entre les lots
                if self.apt_mode and tested % 10 == 0:
                    self._apply_stealth_delay()
        
        return found
    
    def _crawl_for_apis(self, target: str) -> Set[str]:
        """Crawl l'application pour trouver des endpoints API"""
        found = set()
        
        try:
            headers = self._get_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            # Patterns d'URLs d'API
            url_patterns = [
                r'["\'](/(?:api|rest|v\d+)/[^"\']+)["\']',
                r'["\'](/(?:graphql|gql|graph)[^"\']*)["\']',
                r'["\'](/(?:swagger|openapi|api-docs)[^"\']*)["\']',
                r'href=["\']([^"\']+\.(?:json|yaml|yml))["\']',
                r'src=["\']([^"\']+\.js)["\']',
                r'url\s*:\s*["\']([^"\']+)["\']',
                r'endpoint\s*:\s*["\']([^"\']+)["\']',
                r'baseURL\s*:\s*["\']([^"\']+)["\']',
                r'apiUrl\s*:\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in url_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    full_url = urljoin(target, match)
                    found.add(full_url)
            
            # Chercher dans les fichiers JS
            js_files = re.findall(r'src=["\']([^"\']+\.js)["\']', response.text)
            max_js = 10 if not self.apt_mode else 3
            
            for js_file in js_files[:max_js]:
                js_url = urljoin(target, js_file)
                try:
                    self._apply_stealth_delay()
                    js_response = requests.get(js_url, headers=headers, timeout=10, verify=False)
                    
                    # Chercher des URLs d'API dans le JS
                    api_urls = re.findall(r'["\'](/(?:api|rest|v\d+|graphql)/[^"\']+)["\']', js_response.text)
                    for api_url in api_urls:
                        found.add(urljoin(target, api_url))
                    
                    # Chercher des endpoints dans le JS
                    endpoints = re.findall(r'["\'](/[a-zA-Z0-9_/.-]+)["\']', js_response.text)
                    for endpoint in endpoints:
                        if any(p in endpoint for p in ['api', 'rest', 'v1', 'v2', 'graphql']):
                            found.add(urljoin(target, endpoint))
                            
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"      ⚠️ Erreur crawling: {e}")
        
        return found
    
    def _detect_api_from_responses(self, target: str) -> Set[str]:
        """Détecte des API via l'analyse des réponses"""
        found = set()
        
        # Tester les chemins communs
        test_paths = ['/api', '/rest', '/graphql', '/swagger.json', '/openapi.json']
        
        for path in test_paths:
            self._apply_stealth_delay()
            url = urljoin(target, path)
            try:
                headers = self._get_headers()
                headers['Accept'] = 'application/json'
                response = requests.get(url, headers=headers, timeout=5, verify=False)
                
                # Vérifier le content-type
                content_type = response.headers.get('Content-Type', '')
                if any(api_type in content_type for api_type in self.api_headers):
                    found.add(url)
                    
                # Vérifier si la réponse est du JSON
                try:
                    data = response.json()
                    if isinstance(data, (dict, list)):
                        found.add(url)
                except:
                    pass
                    
            except:
                pass
        
        return found
    
    def _analyze_endpoint(self, base_url: str, endpoint: str) -> Dict[str, Any]:
        """Analyse un endpoint API pour déterminer son type et ses méthodes"""
        analysis = {
            "url": endpoint,
            "methods": [],
            "type": "unknown",
            "requires_auth": False,
            "parameters": [],
            "response_format": None,
            "status_code": None,
            "response_time": None
        }
        
        # Tester différentes méthodes HTTP
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        
        for method in methods:
            # En mode APT, tester moins de méthodes
            if self.apt_mode and method not in ['GET', 'POST']:
                continue
            
            try:
                headers = self._get_headers()
                start_time = time.time()
                
                if method == 'GET':
                    response = requests.get(endpoint, headers=headers, timeout=5, verify=False)
                elif method == 'POST':
                    response = requests.post(endpoint, headers=headers, timeout=5, verify=False)
                elif method == 'PUT':
                    response = requests.put(endpoint, headers=headers, timeout=5, verify=False)
                elif method == 'DELETE':
                    response = requests.delete(endpoint, headers=headers, timeout=5, verify=False)
                elif method == 'PATCH':
                    response = requests.patch(endpoint, headers=headers, timeout=5, verify=False)
                else:
                    response = requests.options(endpoint, headers=headers, timeout=5, verify=False)
                
                response_time = time.time() - start_time
                
                if response.status_code not in [404, 405, 410]:
                    analysis["methods"].append(method)
                    analysis["status_code"] = response.status_code
                    analysis["response_time"] = response_time
                    
                    # Détection de l'authentification
                    if response.status_code in [401, 403]:
                        analysis["requires_auth"] = True
                    
                    # Détection du format de réponse
                    content_type = response.headers.get('Content-Type', '')
                    if 'json' in content_type:
                        analysis["response_format"] = "json"
                        try:
                            data = response.json()
                            if isinstance(data, dict):
                                analysis["response_keys"] = list(data.keys())[:10]
                                # Détecter les patterns de pagination
                                if any(k in data for k in ['next', 'previous', 'offset', 'limit', 'page']):
                                    analysis["pagination"] = True
                        except:
                            pass
                    elif 'xml' in content_type:
                        analysis["response_format"] = "xml"
                        
            except Exception:
                pass
        
        # Déterminer le type d'API
        endpoint_lower = endpoint.lower()
        if '/graphql' in endpoint_lower or '/gql' in endpoint_lower:
            analysis["type"] = "graphql"
        elif any(word in endpoint_lower for word in ['soap', 'wsdl', 'asmx', 'webservice']):
            analysis["type"] = "soap"
        elif any(word in endpoint_lower for word in ['swagger', 'openapi', 'api-docs']):
            analysis["type"] = "documentation"
        else:
            analysis["type"] = "rest"
        
        return analysis
    
    def _detect_graphql(self, target: str, endpoints: Set[str]) -> List[Dict[str, Any]]:
        """Détection spécifique des endpoints GraphQL"""
        graphql_endpoints = []
        
        # URLs GraphQL potentielles
        graphql_urls = [url for url in endpoints if 'graphql' in url.lower() or 'gql' in url.lower()]
        
        # Si pas trouvé, tester les chemins communs
        if not graphql_urls:
            common_graphql = ['/graphql', '/gql', '/graph', '/v1/graphql', '/query']
            for path in common_graphql:
                url = urljoin(target, path)
                graphql_urls.append(url)
        
        for url in graphql_urls[:5]:  # Limiter pour performance
            self._apply_stealth_delay()
            
            # Tester une requête GraphQL simple
            query = '{"query": "{ __typename }"}'
            headers = self._get_headers()
            headers['Content-Type'] = 'application/json'
            
            try:
                response = requests.post(url, data=query, headers=headers, timeout=5, verify=False)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'data' in data and '__typename' in str(data):
                            introspection = self._test_graphql_introspection(url)
                            graphql_endpoints.append({
                                "url": url,
                                "type": "graphql",
                                "introspection": introspection,
                                "vulnerable": not introspection
                            })
                    except:
                        pass
            except:
                pass
        
        return graphql_endpoints
    
    def _test_graphql_introspection(self, url: str) -> bool:
        """Teste si l'introspection GraphQL est activée"""
        introspection_query = '''
        {
            __schema {
                types {
                    name
                    fields {
                        name
                    }
                }
            }
        }
        '''
        
        try:
            headers = self._get_headers()
            headers['Content-Type'] = 'application/json'
            response = requests.post(url, json={'query': introspection_query}, headers=headers, timeout=5, verify=False)
            if response.status_code == 200:
                data = response.json()
                if '__schema' in data.get('data', {}):
                    return True
        except:
            pass
        
        return False
    
    def _detect_swagger(self, target: str, endpoints: Set[str]) -> List[Dict[str, Any]]:
        """Détection des endpoints Swagger/OpenAPI"""
        swagger_endpoints = []
        
        swagger_paths = [
            '/swagger.json', '/swagger.yaml', '/openapi.json', '/openapi.yaml',
            '/api-docs', '/api-docs.json', '/api-docs.yaml', '/swagger-ui.json',
            '/v2/api-docs', '/v3/api-docs'
        ]
        
        for path in swagger_paths:
            self._apply_stealth_delay()
            url = urljoin(target, path)
            try:
                headers = self._get_headers()
                response = requests.get(url, headers=headers, timeout=5, verify=False)
                
                if response.status_code == 200:
                    swagger_data = None
                    if path.endswith(('.json', '.yaml', '.yml')):
                        try:
                            if path.endswith('.json'):
                                swagger_data = response.json()
                            else:
                                swagger_data = response.text
                        except:
                            pass
                    
                    swagger_endpoints.append({
                        "url": url,
                        "format": 'json' if path.endswith('.json') else 'yaml',
                        "has_data": swagger_data is not None,
                        "info": swagger_data.get('info', {}) if isinstance(swagger_data, dict) else {}
                    })
            except:
                pass
        
        return swagger_endpoints
    
    def _generate_summary(self, endpoints: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des découvertes"""
        return {
            "total": len(endpoints),
            "by_type": {
                "rest": len([e for e in endpoints if e["type"] == "rest"]),
                "graphql": len([e for e in endpoints if e["type"] == "graphql"]),
                "soap": len([e for e in endpoints if e["type"] == "soap"]),
                "documentation": len([e for e in endpoints if e["type"] == "documentation"])
            },
            "requires_auth": len([e for e in endpoints if e.get("requires_auth")]),
            "json_endpoints": len([e for e in endpoints if e.get("response_format") == "json"]),
            "graphql_introspection": len([e for e in endpoints if e.get("introspection")])
        }
    
    def generate_postman_collection(self, endpoints: List[Dict], output_file: str) -> bool:
        """
        Génère une collection Postman à partir des endpoints découverts
        
        Args:
            endpoints: Liste des endpoints analysés
            output_file: Fichier de sortie pour la collection
        """
        collection = {
            "info": {
                "name": "RedForge API Collection",
                "description": "Collection générée automatiquement par RedForge",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        for endpoint in endpoints:
            if not endpoint.get("methods"):
                continue
                
            item = {
                "name": endpoint["url"].split('/')[-1] or endpoint["url"].split('/')[-2],
                "request": {
                    "method": endpoint["methods"][0],
                    "header": [],
                    "url": {
                        "raw": endpoint["url"],
                        "protocol": "https",
                        "host": endpoint["url"].split('/')[2],
                        "path": endpoint["url"].split('/')[3:]
                    }
                }
            }
            collection["item"].append(item)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(collection, f, indent=2, ensure_ascii=False)
            print(f"✓ Collection Postman générée: {output_file}")
            return True
        except Exception as e:
            print(f"✗ Erreur génération collection: {e}")
            return False


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de la découverte d'API")
    print("=" * 60)
    
    discovery = APIDiscovery()
    
    # Configuration mode APT
    discovery.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Test (simulé)
    # results = discovery.discover("https://api.example.com")
    # print(f"Endpoints API trouvés: {results['count']}")
    
    print("\n✅ Module APIDiscovery chargé avec succès")