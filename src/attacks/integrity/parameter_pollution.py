#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de pollution de paramètres pour RedForge
Détection des vulnérabilités de pollution de paramètres HTTP
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, quote, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class ParameterPollutionConfig:
    """Configuration avancée pour la pollution de paramètres"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_test_payloads: int = 20
    timeout: int = 10
    test_get: bool = True
    test_post: bool = True
    test_headers: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_parsing_behavior: bool = True
    test_nested_pollution: bool = True
    max_concurrent: int = 5


class ParameterPollution:
    """Détection avancée de pollution de paramètres HTTP"""
    
    def __init__(self, config: Optional[ParameterPollutionConfig] = None):
        """
        Initialise le détecteur de pollution de paramètres
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or ParameterPollutionConfig()
        
        # Payloads de test
        self.test_payloads = self._generate_payloads()
        
        # Indicateurs de succès
        self.success_indicators = [
            'admin', 'dashboard', 'welcome', 'success', 'updated',
            'modified', 'deleted', 'bypass', 'granted', 'authorized',
            'authenticated', 'approved', 'confirmed', 'verified'
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
    
    def _generate_payloads(self) -> List[Dict[str, Any]]:
        """Génère une liste complète de payloads de test"""
        payloads = [
            # Duplication simple
            {"param": "id", "values": ["1", "2"], "type": "numeric"},
            {"param": "page", "values": ["1", "admin"], "type": "path"},
            {"param": "user", "values": ["guest", "admin"], "type": "auth"},
            {"param": "role", "values": ["user", "admin"], "type": "privilege"},
            {"param": "action", "values": ["view", "edit"], "type": "action"},
            {"param": "mode", "values": ["normal", "debug"], "type": "debug"},
            
            # Valeurs spéciales
            {"param": "id", "values": ["1", "../../../etc/passwd"], "type": "lfi"},
            {"param": "q", "values": ["test", "<script>alert('XSS')</script>"], "type": "xss"},
            {"param": "search", "values": ["normal", "' OR '1'='1"], "type": "sqli"},
            {"param": "file", "values": ["index", "index.php", "index.html"], "type": "file"},
            {"param": "callback", "values": ["jsonp", "alert('XSS')"], "type": "jsonp"},
            
            # Encodage
            {"param": "id", "values": ["1", "%00admin"], "type": "nullbyte"},
            {"param": "file", "values": ["index", "index%00.php"], "type": "nullbyte"},
            {"param": "path", "values": ["/var/www", "/var/www%00"], "type": "nullbyte"},
            
            # Valeurs booléennes
            {"param": "admin", "values": ["false", "true"], "type": "boolean"},
            {"param": "debug", "values": ["0", "1"], "type": "boolean"},
            {"param": "test", "values": ["0", "1"], "type": "boolean"},
            
            # Valeurs négatives/limites
            {"param": "limit", "values": ["10", "-1"], "type": "boundary"},
            {"param": "offset", "values": ["0", "-1"], "type": "boundary"},
            {"param": "page", "values": ["1", "999999"], "type": "boundary"}
        ]
        
        return payloads[:self.config.max_test_payloads]
    
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
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités de pollution de paramètres
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - post_data: Données POST à tester
                - cookies: Cookies de session
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test de pollution de paramètres sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        cookies = kwargs.get('cookies', {})
        
        # Tester les paramètres GET
        if self.config.test_get:
            params_to_test = kwargs.get('params', [])
            if not params_to_test:
                params_to_test = self._extract_params(target)
            
            get_vulns = self._test_get_pollution_advanced(target, params_to_test, cookies)
            vulnerabilities.extend(get_vulns)
            self.vulnerabilities_found += len(get_vulns)
        
        # Tester les données POST
        if self.config.test_post:
            post_data = kwargs.get('post_data')
            if post_data:
                post_vulns = self._test_post_pollution_advanced(target, post_data, cookies)
                vulnerabilities.extend(post_vulns)
                self.vulnerabilities_found += len(post_vulns)
        
        # Tester les headers
        if self.config.test_headers:
            header_vulns = self._test_header_pollution_advanced(target, cookies)
            vulnerabilities.extend(header_vulns)
            self.vulnerabilities_found += len(header_vulns)
        
        # Tester la pollution imbriquée
        if self.config.test_nested_pollution:
            nested_vulns = self._test_nested_pollution(target, cookies)
            vulnerabilities.extend(nested_vulns)
            self.vulnerabilities_found += len(nested_vulns)
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'test_get' in kwargs:
            self.config.test_get = kwargs['test_get']
        if 'test_post' in kwargs:
            self.config.test_post = kwargs['test_post']
        if 'max_test_payloads' in kwargs:
            self.config.max_test_payloads = kwargs['max_test_payloads']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_test_payloads = min(self.config.max_test_payloads, 10)
            self.config.delay_between_tests = (5, 15)
    
    def _extract_params(self, target: str) -> List[str]:
        """Extrait les paramètres de l'URL"""
        parsed = urlparse(target)
        if parsed.query:
            return list(parse_qs(parsed.query).keys())
        return ['id', 'page', 'user', 'q', 'search', 'action', 'mode', 'type']
    
    def _test_get_pollution_advanced(self, target: str, params: List[str], 
                                      cookies: Dict) -> List[Dict[str, Any]]:
        """Test avancé de pollution de paramètres GET"""
        vulnerabilities = []
        
        for test in self.test_payloads:
            if test['param'] in params or not params:
                if self.config.random_delays:
                    time.sleep(random.uniform(0.3, 0.8))
                
                result = self._test_get_pollution(target, test['param'], 
                                                  test['values'], cookies)
                self.tests_performed += 1
                
                if result['vulnerable']:
                    vulnerabilities.append({
                        "parameter": test['param'],
                        "values": test['values'],
                        "method": "GET",
                        "severity": "MEDIUM",
                        "details": result['details'],
                        "behavior": result['behavior'],
                        "type": test.get('type', 'unknown'),
                        "risk_score": 70 if result['behavior'] == 'both_values_used' else 60
                    })
                    print(f"      ✓ Pollution GET: {test['param']} -> {test['values']}")
        
        return vulnerabilities
    
    def _test_get_pollution(self, target: str, param: str, values: List[str],
                            cookies: Dict) -> Dict[str, Any]:
        """Teste la pollution d'un paramètre GET"""
        result = {
            "vulnerable": False,
            "details": None,
            "behavior": None
        }
        
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        
        # Générer un identifiant unique pour éviter le cache
        cache_buster = f"_cb={int(time.time())}_{hashlib.md5(str(random.random()).encode()).hexdigest()[:8]}"
        
        # Requête originale (une seule valeur)
        original_params = query_params.copy()
        original_params[param] = [values[0]]
        original_params['_cb'] = [cache_buster]
        original_query = urlencode(original_params, doseq=True)
        original_url = urlunparse(parsed._replace(query=original_query))
        
        # Requête polluée (deux valeurs)
        polluted_params = query_params.copy()
        polluted_params[param] = values
        polluted_params['_cb'] = [cache_buster]
        polluted_query = urlencode(polluted_params, doseq=True)
        polluted_url = urlunparse(parsed._replace(query=polluted_query))
        
        try:
            headers = self._get_stealth_headers()
            original_response = requests.get(original_url, headers=headers, cookies=cookies, 
                                           timeout=self.config.timeout, verify=False)
            polluted_response = requests.get(polluted_url, headers=headers, cookies=cookies, 
                                           timeout=self.config.timeout, verify=False)
            
            # Analyser les différences
            if polluted_response.status_code != original_response.status_code:
                result["vulnerable"] = True
                result["behavior"] = "status_code_change"
                result["details"] = f"Code HTTP: {original_response.status_code} -> {polluted_response.status_code}"
                return result
            
            if len(polluted_response.text) != len(original_response.text):
                # Vérifier si la pollution a réussi
                for indicator in self.success_indicators:
                    if indicator in polluted_response.text.lower():
                        result["vulnerable"] = True
                        result["behavior"] = "content_change"
                        result["details"] = f"Indicateur '{indicator}' détecté"
                        return result
            
            # Vérifier si les deux valeurs sont utilisées
            values_present = [val for val in values if val in polluted_response.text]
            if len(values_present) >= 2:
                result["vulnerable"] = True
                result["behavior"] = "both_values_used"
                result["details"] = f"Les deux valeurs sont présentes dans la réponse: {values_present}"
                return result
            
            # Détection du comportement de parsing
            if self.config.detect_parsing_behavior:
                first_only = values[0] in polluted_response.text and values[1] not in polluted_response.text
                last_only = values[1] in polluted_response.text and values[0] not in polluted_response.text
                
                if first_only:
                    result["vulnerable"] = True
                    result["behavior"] = "first_value_only"
                    result["details"] = "Seule la première valeur est utilisée"
                elif last_only:
                    result["vulnerable"] = True
                    result["behavior"] = "last_value_only"
                    result["details"] = "Seule la dernière valeur est utilisée"
                    
        except Exception:
            pass
        
        return result
    
    def _test_post_pollution_advanced(self, target: str, post_data: str,
                                       cookies: Dict) -> List[Dict[str, Any]]:
        """Test avancé de pollution de paramètres POST"""
        vulnerabilities = []
        
        data_params = parse_qs(post_data)
        
        for test in self.test_payloads:
            if test['param'] in data_params:
                if self.config.random_delays:
                    time.sleep(random.uniform(0.3, 0.8))
                
                # Générer un identifiant unique
                cache_buster = f"_cb={int(time.time())}_{hashlib.md5(str(random.random()).encode()).hexdigest()[:8]}"
                
                # Requête originale
                original_data = data_params.copy()
                original_data[test['param']] = [test['values'][0]]
                original_data['_cb'] = [cache_buster]
                
                # Requête polluée
                polluted_data = data_params.copy()
                polluted_data[test['param']] = test['values']
                polluted_data['_cb'] = [cache_buster]
                
                try:
                    headers = self._get_stealth_headers()
                    original_response = requests.post(target, data=original_data, headers=headers,
                                                     cookies=cookies, timeout=self.config.timeout, verify=False)
                    polluted_response = requests.post(target, data=polluted_data, headers=headers,
                                                     cookies=cookies, timeout=self.config.timeout, verify=False)
                    self.tests_performed += 1
                    
                    if len(polluted_response.text) != len(original_response.text):
                        vulnerabilities.append({
                            "parameter": test['param'],
                            "values": test['values'],
                            "method": "POST",
                            "severity": "MEDIUM",
                            "details": "Différence de réponse détectée",
                            "type": test.get('type', 'unknown'),
                            "risk_score": 65
                        })
                        print(f"      ✓ Pollution POST: {test['param']}")
                        
                except Exception:
                    continue
        
        return vulnerabilities
    
    def _test_header_pollution_advanced(self, target: str, cookies: Dict) -> List[Dict[str, Any]]:
        """Test avancé de pollution de headers"""
        vulnerabilities = []
        
        # Headers à polluer
        test_headers = [
            ('X-Forwarded-For', ['127.0.0.1', 'evil.com']),
            ('X-Original-URL', ['/index', '/admin']),
            ('X-Rewrite-URL', ['/index', '/admin']),
            ('X-Forwarded-Host', ['example.com', 'evil.com']),
            ('X-Forwarded-Server', ['localhost', 'evil.com']),
            ('X-HTTP-Method-Override', ['GET', 'POST'])
        ]
        
        for header, values in test_headers:
            if self.config.random_delays:
                time.sleep(random.uniform(0.3, 0.8))
            
            try:
                headers = self._get_stealth_headers()
                
                # Requête originale
                original_headers = headers.copy()
                original_headers[header] = values[0]
                original_response = requests.get(target, headers=original_headers,
                                                cookies=cookies, timeout=self.config.timeout, verify=False)
                
                # Requête polluée
                polluted_headers = headers.copy()
                polluted_headers[header] = ','.join(values)
                polluted_response = requests.get(target, headers=polluted_headers,
                                                cookies=cookies, timeout=self.config.timeout, verify=False)
                self.tests_performed += 1
                
                if len(polluted_response.text) != len(original_response.text):
                    vulnerabilities.append({
                        "parameter": header,
                        "values": values,
                        "method": "Header",
                        "severity": "MEDIUM",
                        "details": "Pollution de header détectée",
                        "risk_score": 65
                    })
                    print(f"      ✓ Pollution Header: {header}")
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_nested_pollution(self, target: str, cookies: Dict) -> List[Dict[str, Any]]:
        """Teste la pollution de paramètres imbriqués (ex: JSON, arrays)"""
        vulnerabilities = []
        
        # Payloads pour pollution imbriquée
        nested_payloads = [
            {"param": "user[name]", "values": ["guest", "admin"]},
            {"param": "user[role]", "values": ["user", "admin"]},
            {"param": "data[id]", "values": ["1", "2"]},
            {"param": "filter[type]", "values": ["normal", "admin"]}
        ]
        
        for test in nested_payloads:
            if self.config.random_delays:
                time.sleep(random.uniform(0.3, 0.8))
            
            parsed = urlparse(target)
            query_params = parse_qs(parsed.query)
            
            # Requête originale
            original_params = query_params.copy()
            original_params[test['param']] = [test['values'][0]]
            original_query = urlencode(original_params, doseq=True)
            original_url = urlunparse(parsed._replace(query=original_query))
            
            # Requête polluée
            polluted_params = query_params.copy()
            polluted_params[test['param']] = test['values']
            polluted_query = urlencode(polluted_params, doseq=True)
            polluted_url = urlunparse(parsed._replace(query=polluted_query))
            
            try:
                headers = self._get_stealth_headers()
                original_response = requests.get(original_url, headers=headers, cookies=cookies,
                                               timeout=self.config.timeout, verify=False)
                polluted_response = requests.get(polluted_url, headers=headers, cookies=cookies,
                                               timeout=self.config.timeout, verify=False)
                self.tests_performed += 1
                
                if len(polluted_response.text) != len(original_response.text):
                    vulnerabilities.append({
                        "parameter": test['param'],
                        "values": test['values'],
                        "method": "Nested",
                        "severity": "MEDIUM",
                        "details": "Pollution de paramètre imbriqué détectée",
                        "risk_score": 70
                    })
                    print(f"      ✓ Pollution Nested: {test['param']}")
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "tests_performed": self.tests_performed,
            "scan_duration": duration,
            "tests_per_second": self.tests_performed / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "test_get": self.config.test_get,
                "test_post": self.config.test_post,
                "test_headers": self.config.test_headers
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune pollution de paramètre détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_method": {
                "GET": len([v for v in vulnerabilities if v['method'] == 'GET']),
                "POST": len([v for v in vulnerabilities if v['method'] == 'POST']),
                "Header": len([v for v in vulnerabilities if v['method'] == 'Header']),
                "Nested": len([v for v in vulnerabilities if v['method'] == 'Nested'])
            },
            "by_behavior": {
                "both_values_used": len([v for v in vulnerabilities if v.get('behavior') == 'both_values_used']),
                "first_value_only": len([v for v in vulnerabilities if v.get('behavior') == 'first_value_only']),
                "last_value_only": len([v for v in vulnerabilities if v.get('behavior') == 'last_value_only']),
                "content_change": len([v for v in vulnerabilities if v.get('behavior') == 'content_change'])
            },
            "medium": len([v for v in vulnerabilities if v['severity'] == 'MEDIUM']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            method = vuln.get('method', '')
            behavior = vuln.get('behavior', '')
            
            if method == 'GET':
                recommendations.add("Utiliser la première occurrence uniquement ou rejeter les paramètres dupliqués")
            
            if method == 'POST':
                recommendations.add("Valider et normaliser les paramètres POST dupliqués")
            
            if method == 'Header':
                recommendations.add("Ne pas utiliser les headers client pour la logique applicative")
                recommendations.add("Valider et normaliser les headers avant utilisation")
            
            if method == 'Nested':
                recommendations.add("Échapper correctement les paramètres imbriqués")
            
            if behavior == 'both_values_used':
                recommendations.add("Ne concaténer que des valeurs attendues et sécurisées")
            
            if behavior == 'first_value_only' or behavior == 'last_value_only':
                recommendations.add("Documenter et normaliser le comportement de parsing")
        
        if not recommendations:
            recommendations.add("Auditer régulièrement les mécanismes de parsing HTTP")
        
        return list(recommendations)
    
    def generate_pollution_exploit(self, target: str, param: str, 
                                   values: List[str]) -> str:
        """
        Génère une URL d'exploit pour la pollution de paramètres
        
        Args:
            target: URL cible
            param: Paramètre à polluer
            values: Valeurs à injecter
        """
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        query_params[param] = values
        new_query = urlencode(query_params, doseq=True)
        
        return urlunparse(parsed._replace(query=new_query))
    
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
    pp = ParameterPollution()
    results = pp.scan("https://example.com/page?id=1")
    print(f"Vulnérabilités de pollution: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = ParameterPollutionConfig(apt_mode=True, max_test_payloads=10)
    pp_apt = ParameterPollution(config=apt_config)
    results_apt = pp_apt.scan("https://example.com/page?id=1", apt_mode=True)
    print(f"Vulnérabilités de pollution (APT): {results_apt['count']}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")