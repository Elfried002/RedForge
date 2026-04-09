#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de manipulation de cookies pour RedForge
Détecte et exploite les vulnérabilités liées aux cookies
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import base64
import hashlib
import json
import requests
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, quote, unquote
from collections import Counter
import math

@dataclass
class CookieManipulationConfig:
    """Configuration avancée pour la manipulation de cookies"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    timeout: int = 10
    deep_analysis: bool = True
    test_injection: bool = True
    monitor_interval: int = 5
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_weak_signatures: bool = True
    analyze_entropy: bool = True
    test_cookie_flooding: bool = False


class CookieManipulation:
    """Détection et exploitation avancée des vulnérabilités de cookies"""
    
    def __init__(self, config: Optional[CookieManipulationConfig] = None):
        """
        Initialise le module de manipulation de cookies
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or CookieManipulationConfig()
        
        # Attributs de sécurité des cookies
        self.cookie_attributes = [
            'Secure', 'HttpOnly', 'SameSite', 'Path', 'Domain', 
            'Expires', 'Max-Age', 'Priority', 'Partitioned'
        ]
        
        # Patterns de vulnérabilité avancés
        self.vulnerability_patterns = {
            "missing_secure": {
                "pattern": r'^(?!.*Secure)',
                "severity": "HIGH",
                "description": "Cookie manquant l'attribut Secure",
                "risk_score": 85
            },
            "missing_httponly": {
                "pattern": r'^(?!.*HttpOnly)',
                "severity": "MEDIUM",
                "description": "Cookie manquant l'attribut HttpOnly",
                "risk_score": 65
            },
            "missing_samesite": {
                "pattern": r'^(?!.*SameSite)',
                "severity": "MEDIUM",
                "description": "Cookie manquant l'attribut SameSite",
                "risk_score": 60
            },
            "weak_hash": {
                "pattern": r'(md5|sha1)',
                "severity": "HIGH",
                "description": "Hash de cookie faible",
                "risk_score": 80
            },
            "predictable": {
                "pattern": r'^\d+$|^[a-z]+$|^[A-Z]+$',
                "severity": "CRITICAL",
                "description": "Cookie prévisible (entropie faible)",
                "risk_score": 95
            },
            "base64_encoded": {
                "pattern": r'^[A-Za-z0-9+/=]+$',
                "severity": "MEDIUM",
                "description": "Cookie encodé en base64 (potentiellement modifiable)",
                "risk_score": 70
            },
            "sequential": {
                "pattern": r'\d+',
                "severity": "HIGH",
                "description": "Cookie séquentiel (prédictible)",
                "risk_score": 85
            },
            "timestamp": {
                "pattern": r'\d{10,13}',
                "severity": "MEDIUM",
                "description": "Cookie contenant un timestamp",
                "risk_score": 60
            },
            "no_expiration": {
                "pattern": r'^(?!.*Expires)(?!.*Max-Age)',
                "severity": "LOW",
                "description": "Cookie sans expiration",
                "risk_score": 35
            }
        }
        
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
        Scanne les vulnérabilités liées aux cookies
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - cookie: Cookie spécifique à analyser
                - intercept: Intercepter les cookies en temps réel
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Analyse des cookies sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Analyse discrète")
        
        vulnerabilities = []
        cookies_analyzed = []
        
        # Récupérer les cookies de la cible
        cookies = self._get_cookies(target, **kwargs)
        
        for cookie_name, cookie_value in cookies.items():
            if self.config.random_delays:
                time.sleep(random.uniform(0.3, 0.8))
            
            analysis = self._analyze_cookie_advanced(cookie_name, cookie_value)
            self.tests_performed += 1
            cookies_analyzed.append(analysis)
            
            if analysis['vulnerabilities']:
                self.vulnerabilities_found += len(analysis['vulnerabilities'])
                for vuln in analysis['vulnerabilities']:
                    vulnerabilities.append({
                        "cookie": cookie_name,
                        "value": self._mask_value(cookie_value),
                        "vulnerability": vuln['type'],
                        "severity": vuln['severity'],
                        "description": vuln['description'],
                        "risk_score": vuln.get('risk_score', 50)
                    })
                    print(f"      ✓ Cookie vulnérable: {cookie_name} - {vuln['type']}")
            
            # Test d'injection
            if self.config.test_injection:
                injection_result = self.test_cookie_injection(target, cookie_name, 
                                                             "<script>alert('XSS')</script>", **kwargs)
                if injection_result['success']:
                    vulnerabilities.append({
                        "cookie": cookie_name,
                        "vulnerability": "cookie_injection",
                        "severity": "CRITICAL",
                        "description": "Injection XSS via cookie détectée",
                        "risk_score": 95
                    })
                    print(f"      ✓ Injection cookie détectée: {cookie_name}")
        
        return self._generate_results(target, vulnerabilities, cookies_analyzed)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'deep_analysis' in kwargs:
            self.config.deep_analysis = kwargs['deep_analysis']
        if 'monitor_interval' in kwargs:
            self.config.monitor_interval = kwargs['monitor_interval']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.delay_between_tests = (5, 15)
            self.config.monitor_interval = max(self.config.monitor_interval, 10)
    
    def _get_cookies(self, target: str, **kwargs) -> Dict[str, str]:
        """Récupère les cookies de la cible"""
        cookies = {}
        
        # Cookie spécifique fourni
        if kwargs.get('cookie'):
            cookie_str = kwargs['cookie']
            for item in cookie_str.split(';'):
                if '=' in item:
                    name, value = item.strip().split('=', 1)
                    cookies[name] = value
        
        # Récupérer les cookies via requête
        if not cookies:
            try:
                headers = self._get_stealth_headers()
                response = requests.get(target, headers=headers, timeout=self.config.timeout, verify=False)
                cookies = dict(response.cookies)
            except Exception as e:
                if not self.config.passive_detection:
                    print(f"    ⚠️ Erreur récupération cookies: {e}")
        
        return cookies
    
    def _analyze_cookie_advanced(self, name: str, value: str) -> Dict[str, Any]:
        """Analyse avancée d'un cookie spécifique"""
        analysis = {
            "name": name,
            "value": self._mask_value(value),
            "length": len(value),
            "vulnerabilities": [],
            "attributes": {},
            "entropy": self._calculate_entropy(value) if self.config.analyze_entropy else 0,
            "encoding": None,
            "hash_type": None,
            "is_json": False,
            "signature_weak": False
        }
        
        # Vérifier les patterns de vulnérabilité
        for vuln_type, vuln_info in self.vulnerability_patterns.items():
            if re.search(vuln_info["pattern"], value, re.IGNORECASE):
                analysis["vulnerabilities"].append({
                    "type": vuln_type,
                    "severity": vuln_info["severity"],
                    "description": vuln_info["description"],
                    "risk_score": vuln_info.get("risk_score", 50)
                })
        
        # Détection d'encodage base64
        if self._is_base64(value):
            analysis["encoding"] = "base64"
            try:
                decoded = base64.b64decode(value).decode('utf-8', errors='ignore')
                analysis["decoded_value"] = self._mask_value(decoded)
            except:
                pass
        
        # Détection de hash
        hash_type = self._detect_hash(value)
        if hash_type:
            analysis["hash_type"] = hash_type
            if hash_type in ['md5', 'sha1']:
                analysis["vulnerabilities"].append({
                    "type": "weak_hash",
                    "severity": "HIGH",
                    "description": f"Cookie contient un hash {hash_type} (faible)",
                    "risk_score": 80
                })
        
        # Détection de JSON
        if value.startswith('{') and value.endswith('}'):
            try:
                analysis["is_json"] = True
                analysis["json_content"] = json.loads(value)
            except:
                pass
        
        # Détection de signatures faibles
        if self.config.detect_weak_signatures:
            weak_signatures = ['admin', 'root', 'user', 'test', 'guest']
            if any(sig in value.lower() for sig in weak_signatures):
                analysis["signature_weak"] = True
                analysis["vulnerabilities"].append({
                    "type": "weak_signature",
                    "severity": "MEDIUM",
                    "description": "Cookie contient des valeurs prédictibles",
                    "risk_score": 70
                })
        
        return analysis
    
    def _mask_value(self, value: str) -> str:
        """Masque les valeurs sensibles pour l'affichage"""
        if len(value) <= 20:
            return value
        return value[:10] + '...' + value[-7:]
    
    def _calculate_entropy(self, value: str) -> float:
        """Calcule l'entropie du cookie (prédictibilité)"""
        if not value:
            return 0.0
        
        freq = Counter(value)
        length = len(value)
        
        entropy = -sum((count/length) * math.log2(count/length) 
                      for count in freq.values())
        return round(entropy, 2)
    
    def _is_base64(self, value: str) -> bool:
        """Vérifie si la valeur est encodée en base64"""
        pattern = r'^[A-Za-z0-9+/=]+$'
        if not re.match(pattern, value):
            return False
        
        try:
            base64.b64decode(value)
            return True
        except:
            return False
    
    def _detect_hash(self, value: str) -> Optional[str]:
        """Détecte le type de hash"""
        hash_patterns = {
            'md5': r'^[a-f0-9]{32}$',
            'sha1': r'^[a-f0-9]{40}$',
            'sha256': r'^[a-f0-9]{64}$',
            'sha512': r'^[a-f0-9]{128}$',
            'crc32': r'^[a-f0-9]{8}$'
        }
        
        for hash_type, pattern in hash_patterns.items():
            if re.match(pattern, value, re.IGNORECASE):
                return hash_type
        
        return None
    
    def test_cookie_injection(self, target: str, cookie_name: str, 
                              malicious_value: str, **kwargs) -> Dict[str, Any]:
        """
        Teste l'injection dans les cookies
        
        Args:
            target: URL cible
            cookie_name: Nom du cookie à tester
            malicious_value: Valeur malveillante à injecter
        """
        result = {
            "success": False,
            "injection": malicious_value,
            "reflected": False
        }
        
        try:
            headers = self._get_stealth_headers()
            cookies = {cookie_name: malicious_value}
            response = requests.get(target, cookies=cookies, headers=headers,
                                  timeout=self.config.timeout, verify=False)
            self.tests_performed += 1
            
            if malicious_value in response.text:
                result["reflected"] = True
                result["success"] = True
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def forge_cookie(self, original_value: str, modifications: Dict) -> str:
        """
        Tente de forger un cookie modifié
        
        Args:
            original_value: Valeur originale du cookie
            modifications: Modifications à appliquer
        """
        forged = original_value
        
        # Tentative de décodage base64
        if self._is_base64(original_value):
            try:
                decoded = base64.b64decode(original_value).decode('utf-8', errors='ignore')
                
                # Modifier la valeur décodée
                for key, value in modifications.items():
                    if isinstance(key, str):
                        decoded = decoded.replace(key, str(value))
                    else:
                        decoded = decoded.replace(str(key), str(value))
                
                # Re-encoder
                forged = base64.b64encode(decoded.encode()).decode()
            except:
                pass
        
        # Modifications directes
        for key, value in modifications.items():
            if isinstance(key, str):
                forged = forged.replace(key, str(value))
        
        return forged
    
    def start_monitor(self, target: str = None, **kwargs):
        """
        Démarre la surveillance des cookies en temps réel
        
        Args:
            target: URL cible (optionnel)
            **kwargs: Options de surveillance
        """
        if target is None:
            target = getattr(self, 'target', None)
        
        if not target:
            print("  ❌ Aucune cible spécifiée pour la surveillance")
            return
        
        print(f"  → Surveillance des cookies sur {target}")
        print(f"  (Intervalle: {self.config.monitor_interval}s - Ctrl+C pour arrêter)")
        
        try:
            previous_cookies = {}
            
            while True:
                try:
                    headers = self._get_stealth_headers()
                    response = requests.get(target, headers=headers, 
                                          timeout=self.config.timeout, verify=False)
                    current_cookies = dict(response.cookies)
                    
                    # Détecter les changements
                    if previous_cookies:
                        for name, value in current_cookies.items():
                            if name in previous_cookies:
                                if previous_cookies[name] != value:
                                    print(f"    [!] Cookie modifié: {name} = {self._mask_value(value)}")
                            else:
                                print(f"    [+] Nouveau cookie: {name} = {self._mask_value(value)}")
                        
                        for name in previous_cookies:
                            if name not in current_cookies:
                                print(f"    [-] Cookie supprimé: {name}")
                    
                    previous_cookies = current_cookies
                    time.sleep(self.config.monitor_interval)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    if not self.config.passive_detection:
                        print(f"    ⚠️ Erreur: {e}")
                    time.sleep(self.config.monitor_interval)
                    
        except KeyboardInterrupt:
            print("\n  ✓ Surveillance arrêtée")
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict], 
                         cookies_analyzed: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "cookies_analyzed": cookies_analyzed,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "tests_performed": self.tests_performed,
            "scan_duration": duration,
            "tests_per_second": self.tests_performed / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "deep_analysis": self.config.deep_analysis
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité de cookie détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_type": {
                "missing_secure": len([v for v in vulnerabilities if v['vulnerability'] == 'missing_secure']),
                "missing_httponly": len([v for v in vulnerabilities if v['vulnerability'] == 'missing_httponly']),
                "missing_samesite": len([v for v in vulnerabilities if v['vulnerability'] == 'missing_samesite']),
                "predictable": len([v for v in vulnerabilities if v['vulnerability'] == 'predictable']),
                "sequential": len([v for v in vulnerabilities if v['vulnerability'] == 'sequential']),
                "weak_hash": len([v for v in vulnerabilities if v['vulnerability'] == 'weak_hash']),
                "cookie_injection": len([v for v in vulnerabilities if v['vulnerability'] == 'cookie_injection'])
            },
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            vuln_type = vuln.get('vulnerability', '')
            
            if vuln_type == 'missing_secure':
                recommendations.add("Ajouter l'attribut 'Secure' aux cookies pour forcer HTTPS")
            
            if vuln_type == 'missing_httponly':
                recommendations.add("Ajouter l'attribut 'HttpOnly' pour empêcher l'accès JavaScript")
            
            if vuln_type == 'missing_samesite':
                recommendations.add("Ajouter l'attribut 'SameSite=Lax' ou 'SameSite=Strict'")
            
            if vuln_type in ['predictable', 'sequential']:
                recommendations.add("Utiliser des valeurs aléatoires non prédictibles pour les cookies")
                recommendations.add("Augmenter l'entropie des valeurs de session")
            
            if vuln_type == 'weak_hash':
                recommendations.add("Utiliser des algorithmes de hashage forts (SHA-256, SHA-512)")
            
            if vuln_type == 'cookie_injection':
                recommendations.add("Valider et échapper les données des cookies")
        
        if not recommendations:
            recommendations.add("Auditer régulièrement la configuration des cookies")
        
        return list(recommendations)
    
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
    manip = CookieManipulation()
    results = manip.scan("https://example.com")
    print(f"Vulnérabilités cookies: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = CookieManipulationConfig(apt_mode=True, deep_analysis=True)
    manip_apt = CookieManipulation(config=apt_config)
    results_apt = manip_apt.scan("https://example.com", apt_mode=True)
    print(f"Vulnérabilités cookies (APT): {results_apt['count']}")
    
    # Exemple de forgeage de cookie
    original = "eyJ1c2VyIjoiZ3Vlc3QiLCJyb2xlIjoidXNlciJ9"
    forged = manip_apt.forge_cookie(original, {"guest": "admin", "user": "admin"})
    print(f"Cookie forgé: {forged}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")