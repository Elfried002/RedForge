#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de recherche de paramètres pour RedForge
Découvre les paramètres GET/POST cachés et non documentés
Version avec support furtif, APT et détection avancée
"""

import re
import time
import random
import requests
from typing import Dict, Any, List, Set, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

from src.core.stealth_engine import StealthEngine


class ParamFinder:
    """Recherche avancée de paramètres avec support furtif"""
    
    def __init__(self):
        # Wordlist de paramètres communs
        self.common_params = [
            "id", "page", "p", "q", "s", "search", "query", "keyword", "term",
            "user", "username", "login", "email", "mail", "name", "fullname",
            "password", "pass", "pwd", "secret", "token", "auth", "key", "api_key",
            "debug", "test", "dev", "local", "admin", "manage", "config", "setting",
            "file", "path", "dir", "folder", "url", "link", "redirect", "return",
            "action", "method", "type", "format", "callback", "jsonp",
            "lang", "language", "locale", "region", "country", "timezone",
            "limit", "offset", "page_size", "per_page", "sort", "order", "filter",
            "include", "exclude", "fields", "select", "expand", "embed",
            "version", "v", "api", "rest", "soap", "xml", "json", "html", "text",
            "download", "export", "import", "upload", "submit", "save", "delete",
            "create", "update", "modify", "edit", "remove", "add",
            "callback", "json", "xml", "format", "ext", "extension",
            "view", "template", "theme", "layout", "partial", "include"
        ]
        
        # Patterns de paramètres dans le HTML
        self.html_param_patterns = [
            (r'<input[^>]+name=["\']([^"\']+)["\'][^>]*>', 'input'),
            (r'<select[^>]+name=["\']([^"\']+)["\'][^>]*>', 'select'),
            (r'<textarea[^>]+name=["\']([^"\']+)["\'][^>]*>', 'textarea'),
            (r'<form[^>]+action=["\']([^"\']+)["\'][^>]*>', 'form'),
            (r'data-([a-zA-Z_][a-zA-Z0-9_]*)', 'data_attribute'),
            (r'v-bind:([a-zA-Z_][a-zA-Z0-9_]*)', 'vue_bind'),
            (r'ng-model=["\']([^"\']+)["\']', 'angular'),
            (r'@click\.([a-zA-Z_][a-zA-Z0-9_]*)', 'vue_click'),
            (r'\[([a-zA-Z_][a-zA-Z0-9_]*)\]', 'angular_bracket')
        ]
        
        # Patterns de réflexion
        self.reflection_patterns = [
            r'REFLECTION_TEST_123',
            r'XSS_TEST_123',
            r'SQL_TEST_123'
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
    
    def find(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Recherche des paramètres sur la cible
        
        Args:
            target: URL cible
            **kwargs:
                - wordlist: Wordlist personnalisée
                - methods: Méthodes HTTP à tester (GET, POST)
                - threads: Nombre de threads
                - crawl: Crawler l'application
                - bruteforce: Activer le bruteforce
        """
        print(f"  → Recherche de paramètres sur {target}")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Recherche discrète")
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        params_found = set()
        
        # Méthode 1: Extraire les paramètres des formulaires HTML
        print(f"    → Extraction des paramètres HTML...")
        self._apply_stealth_delay()
        html_params = self._extract_from_html(target)
        params_found.update(html_params)
        
        # Méthode 2: Analyser les requêtes existantes
        print(f"    → Analyse des requêtes existantes...")
        existing_params = self._analyze_existing_requests(target)
        params_found.update(existing_params)
        
        # Méthode 3: Bruteforce de paramètres
        if kwargs.get('bruteforce', True) and not self.apt_mode:
            wordlist = kwargs.get('wordlist', self.common_params)
            threads = min(kwargs.get('threads', 10), 5 if self.apt_mode else 10)
            print(f"    → Bruteforce de {len(wordlist)} paramètres...")
            brute_params = self._bruteforce_params(target, wordlist, threads)
            params_found.update(brute_params)
        elif self.apt_mode:
            # En mode APT, bruteforce limité
            wordlist = self.common_params[:30]
            print(f"    → Bruteforce limité de {len(wordlist)} paramètres...")
            brute_params = self._bruteforce_params(target, wordlist, threads=3)
            params_found.update(brute_params)
        
        # Méthode 4: Crawler l'application
        if kwargs.get('crawl', True) and not self.apt_mode:
            print(f"    → Crawling pour trouver plus de paramètres...")
            crawled_params = self._crawl_for_params(target)
            params_found.update(crawled_params)
        
        # Analyser chaque paramètre trouvé
        analyzed_params = []
        params_list = list(params_found)
        
        for idx, param in enumerate(params_list):
            if self.apt_mode and idx > 0:
                self._apply_stealth_delay()
            analysis = self._analyze_parameter(target, param)
            analyzed_params.append(analysis)
        
        # Détection de paramètres sensibles
        sensitive_params = [p for p in analyzed_params if p.get('sensitive', False)]
        
        return {
            "target": target,
            "parameters": analyzed_params,
            "total": len(analyzed_params),
            "sensitive_count": len(sensitive_params),
            "sensitive_parameters": sensitive_params,
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "summary": self._generate_summary(analyzed_params)
        }
    
    def _extract_from_html(self, target: str) -> Set[str]:
        """Extrait les paramètres des formulaires HTML"""
        params = set()
        
        try:
            headers = self._get_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            content = response.text
            
            for pattern, source in self.html_param_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Nettoyer le paramètre
                    param = match.split('?')[0].split('#')[0].strip()
                    if param and len(param) < 100 and not param.startswith('http'):
                        params.add(param)
            
            # Extraire les paramètres des URLs dans le HTML
            url_pattern = r'href=["\']([^"\']+\?[^"\']+)["\']'
            urls = re.findall(url_pattern, content)
            for url in urls:
                parsed = urlparse(url)
                if parsed.query:
                    query_params = parse_qs(parsed.query)
                    params.update(query_params.keys())
                    
        except Exception as e:
            print(f"      ⚠️ Erreur extraction HTML: {e}")
        
        return params
    
    def _analyze_existing_requests(self, target: str) -> Set[str]:
        """Analyse les requêtes existantes de la page"""
        params = set()
        
        # Analyser l'URL elle-même
        parsed = urlparse(target)
        if parsed.query:
            query_params = parse_qs(parsed.query)
            params.update(query_params.keys())
        
        # Chercher des liens avec paramètres
        try:
            headers = self._get_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            link_pattern = r'href=["\']([^"\']*\?[^"\']+)["\']'
            links = re.findall(link_pattern, response.text)
            
            for link in links:
                parsed_link = urlparse(link)
                if parsed_link.query:
                    query_params = parse_qs(parsed_link.query)
                    params.update(query_params.keys())
                    
        except Exception as e:
            print(f"      ⚠️ Erreur analyse requêtes: {e}")
        
        return params
    
    def _bruteforce_params(self, base_url: str, params: List[str], threads: int) -> Set[str]:
        """Bruteforce des paramètres en testant leur présence"""
        found_params = set()
        tested = 0
        
        # Nettoyer l'URL
        if '?' in base_url:
            base_url = base_url.split('?')[0]
        
        def test_param(param):
            test_url = f"{base_url}?{param}=REFLECTION_TEST_123"
            try:
                headers = self._get_headers()
                # Requête originale
                original_response = requests.get(base_url, headers=headers, timeout=5, verify=False)
                original_length = len(original_response.text)
                original_status = original_response.status_code
                
                # Requête avec paramètre
                test_response = requests.get(test_url, headers=headers, timeout=5, verify=False)
                test_length = len(test_response.text)
                test_status = test_response.status_code
                
                # Si la réponse change significativement, le paramètre est probablement utilisé
                if (abs(test_length - original_length) > 100 or 
                    test_status != original_status or
                    'REFLECTION_TEST_123' in test_response.text):
                    return param
                    
            except:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(test_param, param): param for param in params}
            
            for future in as_completed(futures):
                result = future.result()
                tested += 1
                if result:
                    found_params.add(result)
                    print(f"      ✓ Paramètre trouvé: {result}")
                
                # Délai furtif entre les lots
                if self.apt_mode and tested % 10 == 0:
                    self._apply_stealth_delay()
        
        return found_params
    
    def _crawl_for_params(self, base_url: str) -> Set[str]:
        """Crawl l'application pour trouver des paramètres"""
        params = set()
        visited = set()
        
        def crawl(url, depth):
            if depth > 2 or url in visited:
                return
            visited.add(url)
            
            try:
                headers = self._get_headers()
                response = requests.get(url, headers=headers, timeout=10, verify=False)
                
                # Extraire les paramètres de l'URL courante
                parsed = urlparse(url)
                if parsed.query:
                    query_params = parse_qs(parsed.query)
                    params.update(query_params.keys())
                
                # Trouver les liens à crawler
                link_pattern = r'href=["\']([^"\']+)["\']'
                links = re.findall(link_pattern, response.text)
                
                for link in links:
                    if link.startswith('/') or link.startswith(base_url):
                        if link.startswith('/'):
                            full_url = base_url.rstrip('/') + link
                        else:
                            full_url = link
                        
                        if full_url.startswith(base_url) and full_url not in visited:
                            self._apply_stealth_delay()
                            crawl(full_url, depth + 1)
                            
            except:
                pass
        
        crawl(base_url, 1)
        return params
    
    def _analyze_parameter(self, base_url: str, param: str) -> Dict[str, Any]:
        """Analyse un paramètre pour déterminer son type et sa sensibilité"""
        analysis = {
            "name": param,
            "type": "unknown",
            "sensitive": False,
            "reflected": False,
            "examples": [],
            "found_in": []
        }
        
        # Déterminer le type
        param_lower = param.lower()
        
        type_mapping = {
            ('id', 'page', 'p', 'q', 's', 'search', 'query'): 'identifier',
            ('password', 'pass', 'pwd', 'secret', 'token', 'api_key', 'auth'): 'credential',
            ('debug', 'test', 'dev', 'local', 'trace'): 'debug',
            ('file', 'path', 'dir', 'folder', 'filename'): 'path',
            ('url', 'link', 'redirect', 'return', 'next', 'goto'): 'redirect',
            ('callback', 'jsonp', 'json', 'xml', 'format'): 'format'
        }
        
        for keywords, type_name in type_mapping.items():
            if any(kw in param_lower for kw in keywords):
                analysis["type"] = type_name
                if type_name in ['credential', 'debug']:
                    analysis["sensitive"] = True
                break
        
        # Vérifier la réflexion
        test_url = f"{base_url.split('?')[0]}?{param}=REFLECTION_TEST_123"
        try:
            headers = self._get_headers()
            response = requests.get(test_url, headers=headers, timeout=5, verify=False)
            if 'REFLECTION_TEST_123' in response.text:
                analysis["reflected"] = True
        except:
            pass
        
        # Exemples de valeurs selon le type
        examples_by_type = {
            "identifier": ["1", "2", "3", "null", "0"],
            "path": ["/etc/passwd", "../../../config.php", "/", "index.php"],
            "redirect": ["https://evil.com", "//evil.com", "/admin", "javascript:alert(1)"],
            "callback": ["alert('XSS')", "evilFunction", "https://evil.com/callback"],
            "debug": ["1", "true", "yes", "on", "enable"],
            "credential": ["admin", "test", "password123", "token123"]
        }
        
        analysis["examples"] = examples_by_type.get(analysis["type"], ["test", "1", "true"])
        
        return analysis
    
    def _generate_summary(self, parameters: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des paramètres trouvés"""
        type_counts = defaultdict(int)
        for p in parameters:
            type_counts[p["type"]] += 1
        
        return {
            "total": len(parameters),
            "by_type": dict(type_counts),
            "reflected": len([p for p in parameters if p["reflected"]]),
            "sensitive": len([p for p in parameters if p["sensitive"]])
        }
    
    def find_sensitive_params(self, target: str) -> List[Dict]:
        """Recherche spécifiquement les paramètres sensibles"""
        results = self.find(target, bruteforce=True, crawl=False)
        return results.get("sensitive_parameters", [])
    
    def test_param_injection(self, target: str, param: str) -> Dict[str, Any]:
        """Teste si un paramètre est vulnérable aux injections"""
        injection_tests = [
            ("'", "SQL Injection"),
            ('"', "SQL Injection"),
            ("1' OR '1'='1", "SQL Injection"),
            ("<script>alert('XSS')</script>", "XSS"),
            ("<img src=x onerror=alert('XSS')>", "XSS"),
            ("../../../etc/passwd", "Path Traversal"),
            ("${7*7}", "Template Injection"),
            ("%00", "Null Byte Injection"),
            ("; ls", "Command Injection"),
            ("| cat /etc/passwd", "Command Injection")
        ]
        
        results = []
        base_url = target.split('?')[0]
        
        for payload, vuln_type in injection_tests:
            self._apply_stealth_delay()
            test_url = f"{base_url}?{param}={quote(payload)}"
            try:
                headers = self._get_headers()
                response = requests.get(test_url, headers=headers, timeout=5, verify=False)
                
                # Vérifier les signes d'injection
                if vuln_type == "SQL Injection" and any(err in response.text.lower() for err in 
                    ['syntax error', 'mysql', 'sql', 'database error', 'ora-', 'postgres']):
                    results.append({
                        "parameter": param,
                        "payload": payload,
                        "type": vuln_type,
                        "vulnerable": True
                    })
                elif vuln_type == "XSS" and payload in response.text:
                    results.append({
                        "parameter": param,
                        "payload": payload,
                        "type": vuln_type,
                        "vulnerable": True
                    })
                elif vuln_type == "Path Traversal" and ('root:' in response.text or 'etc/passwd' in response.text):
                    results.append({
                        "parameter": param,
                        "payload": payload,
                        "type": vuln_type,
                        "vulnerable": True
                    })
            except:
                pass
        
        return {
            "parameter": param,
            "tests": results,
            "is_vulnerable": len(results) > 0
        }
    
    def save_results(self, results: Dict[str, Any], output_file: str) -> bool:
        """Sauvegarde les résultats au format JSON"""
        import json
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"✓ Résultats sauvegardés: {output_file}")
            return True
        except Exception as e:
            print(f"✗ Erreur sauvegarde: {e}")
            return False


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de ParamFinder")
    print("=" * 60)
    
    finder = ParamFinder()
    
    # Configuration mode APT
    finder.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Test (simulé)
    # results = finder.find("https://example.com")
    # print(f"Paramètres trouvés: {results['total']}")
    
    print("\n✅ Module ParamFinder chargé avec succès")