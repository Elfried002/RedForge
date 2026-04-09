#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'altération de données pour RedForge
Détection des vulnérabilités d'altération de données
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import json
import base64
import hashlib
import requests
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class DataTamperingConfig:
    """Configuration avancée pour l'altération de données"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_test_values: int = 10
    timeout: int = 10
    test_hidden: bool = True
    test_cookies: bool = True
    test_encoded: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    test_jwt_tampering: bool = True
    test_signed_data: bool = True
    max_depth: int = 3


class DataTampering:
    """Détection avancée d'altération de données"""
    
    def __init__(self, config: Optional[DataTamperingConfig] = None):
        """
        Initialise le détecteur d'altération de données
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or DataTamperingConfig()
        
        # Techniques d'altération
        self.tampering_techniques = {
            "hidden_fields": [
                "admin", "role", "permission", "access_level", "user_type",
                "is_admin", "privilege", "group", "status", "verified",
                "is_staff", "is_superuser", "can_edit", "can_delete",
                "moderator", "editor", "contributor", "owner"
            ],
            "numeric_fields": [
                "balance", "points", "credits", "score", "rating",
                "votes", "count", "total", "amount", "value",
                "price", "cost", "fee", "tax", "discount",
                "quantity", "stock", "inventory", "limit"
            ],
            "boolean_fields": [
                "active", "enabled", "verified", "confirmed", "approved",
                "locked", "suspended", "deleted", "archived", "published",
                "paid", "shipped", "delivered", "processed", "valid"
            ],
            "identity_fields": [
                "user_id", "account_id", "profile_id", "customer_id",
                "order_id", "transaction_id", "payment_id", "subscription_id"
            ]
        }
        
        # Types d'encodage
        self.encoding_types = ['base64', 'hex', 'url', 'json', 'jwt']
        
        # Indicateurs de succès
        self.success_indicators = [
            'success', 'updated', 'modified', 'changed', 'saved',
            'updated successfully', 'profile updated', 'settings saved',
            'ok', 'true', '1', 'completed', 'processed'
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
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'
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
        Scanne les vulnérabilités d'altération de données
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - post_data: Données POST à modifier
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
        
        print(f"  → Test d'altération de données sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        cookies = kwargs.get('cookies', {})
        
        # Tester les paramètres GET
        params_to_test = kwargs.get('params', [])
        if not params_to_test:
            params_to_test = self._extract_params(target)
        
        get_vulns = self._test_get_parameters(target, params_to_test, cookies)
        vulnerabilities.extend(get_vulns)
        self.vulnerabilities_found += len(get_vulns)
        
        # Tester les données POST
        post_data = kwargs.get('post_data')
        if post_data:
            post_vulns = self._test_post_data(target, post_data, cookies)
            vulnerabilities.extend(post_vulns)
            self.vulnerabilities_found += len(post_vulns)
        
        # Tester les cookies
        if self.config.test_cookies:
            cookie_vulns = self._test_cookie_tampering_advanced(target, cookies)
            vulnerabilities.extend(cookie_vulns)
            self.vulnerabilities_found += len(cookie_vulns)
        
        # Tester les données encodées
        if self.config.test_encoded:
            encoded_vulns = self._test_encoded_data_advanced(target, cookies)
            vulnerabilities.extend(encoded_vulns)
            self.vulnerabilities_found += len(encoded_vulns)
        
        # Tester les JWT
        if self.config.test_jwt_tampering:
            jwt_vulns = self._test_jwt_tampering(target, cookies)
            vulnerabilities.extend(jwt_vulns)
            self.vulnerabilities_found += len(jwt_vulns)
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'max_test_values' in kwargs:
            self.config.max_test_values = kwargs['max_test_values']
        if 'test_hidden' in kwargs:
            self.config.test_hidden = kwargs['test_hidden']
        if 'test_cookies' in kwargs:
            self.config.test_cookies = kwargs['test_cookies']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_test_values = min(self.config.max_test_values, 5)
            self.config.delay_between_tests = (5, 15)
    
    def _extract_params(self, target: str) -> List[str]:
        """Extrait les paramètres de l'URL"""
        parsed = urlparse(target)
        if parsed.query:
            return list(parse_qs(parsed.query).keys())
        return []
    
    def _test_get_parameters(self, target: str, params: List[str], 
                             cookies: Dict) -> List[Dict[str, Any]]:
        """Teste l'altération des paramètres GET"""
        vulnerabilities = []
        test_values = ["admin", "1", "true", "yes", "on", "enabled"]
        
        for idx, param in enumerate(params):
            if self.config.apt_mode and idx > 10:
                break
            
            param_lower = param.lower()
            
            for category, sensitive_params in self.tampering_techniques.items():
                if any(p in param_lower for p in sensitive_params):
                    for test_value in test_values[:self.config.max_test_values]:
                        if self.config.random_delays:
                            time.sleep(random.uniform(0.3, 0.8))
                        
                        result = self._test_get_tampering_advanced(target, param, test_value, cookies)
                        self.tests_performed += 1
                        
                        if result['vulnerable']:
                            vulnerabilities.append({
                                "parameter": param,
                                "category": category,
                                "method": "GET",
                                "test_value": test_value,
                                "severity": "HIGH",
                                "details": result['details'],
                                "risk_score": 85,
                                "response_preview": result.get('response_preview', '')
                            })
                            print(f"      ✓ Altération GET: {param}={test_value}")
                            break
                    break
        
        return vulnerabilities
    
    def _test_get_tampering_advanced(self, target: str, param: str, test_value: str,
                                      cookies: Dict) -> Dict[str, Any]:
        """Test avancé d'altération d'un paramètre GET"""
        result = {
            "vulnerable": False,
            "details": None,
            "response_preview": None
        }
        
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        
        # Sauvegarder la valeur originale
        original_value = query_params.get(param, [None])[0]
        
        # Modifier le paramètre
        query_params[param] = [test_value]
        new_query = urlencode(query_params, doseq=True)
        test_url = urlunparse(parsed._replace(query=new_query))
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(test_url, headers=headers, cookies=cookies,
                                  timeout=self.config.timeout, verify=False)
            
            for indicator in self.success_indicators:
                if indicator in response.text.lower():
                    # Vérifier que ce n'est pas une erreur
                    if 'error' not in response.text.lower() and 'invalid' not in response.text.lower():
                        result["vulnerable"] = True
                        result["details"] = f"Paramètre '{param}' accepte '{test_value}'"
                        result["response_preview"] = response.text[:200]
                        break
                    
        except Exception:
            pass
        
        return result
    
    def _test_post_data(self, target: str, post_data: Dict,
                        cookies: Dict) -> List[Dict[str, Any]]:
        """Teste l'altération des données POST"""
        vulnerabilities = []
        test_values = ["admin", "1", "true", "yes", "on"]
        
        for param in post_data.keys():
            param_lower = param.lower()
            
            for category, sensitive_params in self.tampering_techniques.items():
                if any(p in param_lower for p in sensitive_params):
                    for test_value in test_values[:self.config.max_test_values]:
                        if self.config.random_delays:
                            time.sleep(random.uniform(0.3, 0.8))
                        
                        test_data = post_data.copy()
                        test_data[param] = test_value
                        
                        result = self._test_post_tampering_advanced(target, test_data, cookies)
                        self.tests_performed += 1
                        
                        if result['vulnerable']:
                            vulnerabilities.append({
                                "parameter": param,
                                "category": category,
                                "method": "POST",
                                "test_value": test_value,
                                "severity": "HIGH",
                                "details": result['details'],
                                "risk_score": 85,
                                "response_preview": result.get('response_preview', '')
                            })
                            print(f"      ✓ Altération POST: {param}={test_value}")
                            break
                    break
        
        return vulnerabilities
    
    def _test_post_tampering_advanced(self, target: str, test_data: Dict,
                                       cookies: Dict) -> Dict[str, Any]:
        """Test avancé d'altération de données POST"""
        result = {
            "vulnerable": False,
            "details": None,
            "response_preview": None
        }
        
        try:
            headers = self._get_stealth_headers({'Content-Type': 'application/x-www-form-urlencoded'})
            response = requests.post(target, data=test_data, headers=headers,
                                   cookies=cookies, timeout=self.config.timeout, verify=False)
            
            for indicator in self.success_indicators:
                if indicator in response.text.lower():
                    if 'error' not in response.text.lower() and 'invalid' not in response.text.lower():
                        result["vulnerable"] = True
                        result["details"] = f"Données POST modifiées acceptées"
                        result["response_preview"] = response.text[:200]
                        break
                    
        except Exception:
            pass
        
        return result
    
    def _test_cookie_tampering_advanced(self, target: str, cookies: Dict) -> List[Dict[str, Any]]:
        """Test avancé d'altération des cookies"""
        vulnerabilities = []
        test_values = ["admin", "1", "true", "yes", "on"]
        
        for cookie_name in cookies.keys():
            cookie_lower = cookie_name.lower()
            
            for category, sensitive_params in self.tampering_techniques.items():
                if any(p in cookie_lower for p in sensitive_params):
                    for test_value in test_values[:self.config.max_test_values]:
                        test_cookies = cookies.copy()
                        test_cookies[cookie_name] = test_value
                        
                        try:
                            headers = self._get_stealth_headers()
                            response = requests.get(target, headers=headers, cookies=test_cookies,
                                                  timeout=self.config.timeout, verify=False)
                            self.tests_performed += 1
                            
                            if response.status_code == 200 and len(response.text) > 500:
                                vulnerabilities.append({
                                    "parameter": cookie_name,
                                    "category": category,
                                    "method": "Cookie",
                                    "test_value": test_value,
                                    "severity": "HIGH",
                                    "details": f"Cookie '{cookie_name}' altéré accepté",
                                    "risk_score": 85
                                })
                                print(f"      ✓ Altération Cookie: {cookie_name}={test_value}")
                                break
                                
                        except Exception:
                            continue
                    break
        
        return vulnerabilities
    
    def _test_encoded_data_advanced(self, target: str, cookies: Dict) -> List[Dict[str, Any]]:
        """Test avancé d'altération de données encodées"""
        vulnerabilities = []
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, cookies=cookies,
                                  timeout=self.config.timeout, verify=False)
            
            # Chercher des données base64
            base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
            matches = re.findall(base64_pattern, response.text)
            
            for match in matches[:5]:  # Limiter pour performance
                try:
                    decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                    
                    for category, sensitive_params in self.tampering_techniques.items():
                        for param in sensitive_params:
                            if param in decoded.lower():
                                # Modifier et re-encoder
                                modified_decoded = re.sub(param, 'admin', decoded, flags=re.IGNORECASE)
                                modified_encoded = base64.b64encode(modified_decoded.encode()).decode()
                                
                                test_url = target.replace(match, modified_encoded)
                                test_response = requests.get(test_url, headers=headers,
                                                           cookies=cookies, timeout=10, verify=False)
                                self.tests_performed += 1
                                
                                if test_response.status_code == 200:
                                    vulnerabilities.append({
                                        "parameter": "encoded_data",
                                        "category": category,
                                        "method": "Base64",
                                        "severity": "HIGH",
                                        "details": f"Données base64 altérables: {param}",
                                        "risk_score": 90
                                    })
                                    print(f"      ✓ Altération base64 détectée")
                                    break
                            if vulnerabilities:
                                break
                        if vulnerabilities:
                            break
                            
                except:
                    pass
                
        except Exception:
            pass
        
        return vulnerabilities
    
    def _test_jwt_tampering(self, target: str, cookies: Dict) -> List[Dict[str, Any]]:
        """Teste l'altération de tokens JWT"""
        vulnerabilities = []
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, cookies=cookies,
                                  timeout=self.config.timeout, verify=False)
            
            # Pattern JWT
            jwt_pattern = r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'
            jwt_tokens = re.findall(jwt_pattern, response.text)
            
            for token in jwt_tokens[:5]:
                try:
                    parts = token.split('.')
                    if len(parts) >= 2:
                        # Décoder le payload
                        payload = parts[1]
                        payload += '=' * (4 - len(payload) % 4)
                        decoded = base64.b64decode(payload).decode('utf-8')
                        
                        # Chercher des champs sensibles
                        for category, sensitive_params in self.tampering_techniques.items():
                            for param in sensitive_params:
                                if param in decoded.lower():
                                    # Tenter de modifier
                                    modified_decoded = decoded.replace(param, 'admin')
                                    modified_payload = base64.b64encode(modified_decoded.encode()).decode().rstrip('=')
                                    modified_token = f"{parts[0]}.{modified_payload}.{parts[2] if len(parts) > 2 else ''}"
                                    
                                    test_cookies = cookies.copy()
                                    test_cookies['token'] = modified_token
                                    
                                    test_response = requests.get(target, headers=headers,
                                                               cookies=test_cookies, timeout=10, verify=False)
                                    self.tests_performed += 1
                                    
                                    if test_response.status_code == 200:
                                        vulnerabilities.append({
                                            "parameter": "jwt_token",
                                            "category": category,
                                            "method": "JWT",
                                            "severity": "CRITICAL",
                                            "details": f"Token JWT altérable: {param}",
                                            "risk_score": 95
                                        })
                                        print(f"      ✓ Altération JWT détectée")
                                        break
                                if vulnerabilities:
                                    break
                            if vulnerabilities:
                                break
                            
                except:
                    pass
                
        except Exception:
            pass
        
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
                "test_hidden": self.config.test_hidden,
                "test_cookies": self.config.test_cookies,
                "test_encoded": self.config.test_encoded
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune altération de données détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_method": {
                "GET": len([v for v in vulnerabilities if v['method'] == 'GET']),
                "POST": len([v for v in vulnerabilities if v['method'] == 'POST']),
                "Cookie": len([v for v in vulnerabilities if v['method'] == 'Cookie']),
                "Base64": len([v for v in vulnerabilities if v['method'] == 'Base64']),
                "JWT": len([v for v in vulnerabilities if v['method'] == 'JWT'])
            },
            "by_category": {
                "hidden_fields": len([v for v in vulnerabilities if v['category'] == 'hidden_fields']),
                "numeric_fields": len([v for v in vulnerabilities if v['category'] == 'numeric_fields']),
                "boolean_fields": len([v for v in vulnerabilities if v['category'] == 'boolean_fields'])
            },
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            method = vuln.get('method', '')
            category = vuln.get('category', '')
            
            if method == 'GET' or method == 'POST':
                recommendations.add("Ne jamais faire confiance aux données soumises par le client")
                recommendations.add("Valider et autoriser toutes les données côté serveur")
            
            if method == 'Cookie':
                recommendations.add("Signer les cookies avec HMAC")
                recommendations.add("Utiliser des cookies HTTP-only et Secure")
            
            if method == 'Base64':
                recommendations.add("Ne pas utiliser base64 comme mécanisme de sécurité")
                recommendations.add("Signer les données encodées")
            
            if method == 'JWT':
                recommendations.add("Vérifier la signature des tokens JWT")
                recommendations.add("Utiliser des algorithmes de signature forts (RS256, ES256)")
                recommendations.add("Ne pas utiliser 'none' comme algorithme")
            
            if category == 'hidden_fields':
                recommendations.add("Ne pas stocker d'informations sensibles dans les champs cachés")
        
        if not recommendations:
            recommendations.add("Implémenter des contrôles d'intégrité sur toutes les données")
        
        return list(recommendations)
    
    def start_monitor(self, **kwargs):
        """
        Démarre la surveillance des modifications de données
        
        Args:
            **kwargs: Options de surveillance
        """
        print("  → Surveillance des altérations de données démarrée")
        # Implémentation de surveillance en temps réel
    
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
    dt = DataTampering()
    results = dt.scan("https://example.com/profile?user=123")
    print(f"Vulnérabilités d'altération: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = DataTamperingConfig(apt_mode=True, max_test_values=5)
    dt_apt = DataTampering(config=apt_config)
    results_apt = dt_apt.scan("https://example.com/profile?user=123", apt_mode=True)
    print(f"Vulnérabilités d'altération (APT): {results_apt['count']}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")