#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection de mauvaises configurations pour RedForge
Détecte les mauvaises configurations sur l'infrastructure cible
Version avec support furtif, APT et détection avancée
"""

import re
import time
import random
import requests
import ssl
import socket
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class MisconfigConfig:
    """Configuration avancée pour la détection de mauvaises configurations"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    check_headers: bool = True
    check_paths: bool = True
    check_methods: bool = True
    check_ssl: bool = True
    check_server: bool = True
    check_cloud: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    max_paths: int = 50
    check_cors: bool = True
    check_open_redirect: bool = True
    check_rate_limiting: bool = True


class MisconfigDetector:
    """Détection avancée des mauvaises configurations d'infrastructure"""
    
    def __init__(self, config: Optional[MisconfigConfig] = None):
        """
        Initialise le détecteur de mauvaises configurations
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or MisconfigConfig()
        
        # Headers de sécurité
        self.security_headers = {
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-XSS-Protection": ["1; mode=block"],
            "X-Content-Type-Options": ["nosniff"],
            "Content-Security-Policy": [],
            "Strict-Transport-Security": [],
            "Referrer-Policy": ["strict-origin", "no-referrer", "same-origin"],
            "Permissions-Policy": [],
            "Cross-Origin-Embedder-Policy": ["require-corp", "credentialless"],
            "Cross-Origin-Opener-Policy": ["same-origin", "same-origin-allow-popups"],
            "Cross-Origin-Resource-Policy": ["same-origin", "same-site"]
        }
        
        # Headers de divulgation d'information
        self.disclosure_headers = [
            "Server", "X-Powered-By", "X-AspNet-Version", "X-AspNetMvc-Version",
            "X-Generator", "X-Drupal-Cache", "X-Drupal-Dynamic-Cache", "X-Varnish",
            "X-Backend", "X-Proxy-Cache", "X-Cache", "X-Cache-Hits"
        ]
        
        # Chemins sensibles
        self.sensitive_paths = self._generate_sensitive_paths()
        
        # Méthodes HTTP dangereuses
        self.dangerous_methods = ['PUT', 'DELETE', 'TRACE', 'CONNECT', 'PATCH']
        
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
    
    def _generate_sensitive_paths(self) -> List[str]:
        """Génère une liste complète de chemins sensibles"""
        paths = [
            # Version control
            "/.git/config", "/.git/HEAD", "/.svn/entries", "/.hg/", "/.bzr/",
            # Environment and config
            "/.env", "/.env.backup", "/.env.local", "/.env.production",
            "/.htaccess", "/.htpasswd", "/web.config", "/robots.txt",
            # PHP info and debug
            "/phpinfo.php", "/info.php", "/php_info.php", "/test.php",
            "/debug.php", "/info.php", "/php.php", "/status.php",
            # Server status
            "/server-status", "/server-info", "/status", "/health",
            "/metrics", "/healthz", "/ready", "/live",
            # API documentation
            "/api/swagger.json", "/swagger-ui.html", "/v2/api-docs",
            "/v3/api-docs", "/openapi.json", "/api-docs", "/docs",
            # Actuator endpoints (Spring Boot)
            "/actuator", "/actuator/env", "/actuator/health", "/actuator/info",
            "/actuator/metrics", "/actuator/httptrace", "/actuator/beans",
            "/actuator/configprops", "/actuator/mappings", "/actuator/scheduledtasks",
            # Debug tools
            "/_profiler", "/_phpinfo", "/_debug", "/_dev", "/_test",
            "/debugbar", "/debug/default", "/debug/", "/_debugbar",
            # Admin interfaces
            "/admin", "/administrator", "/wp-admin", "/phpmyadmin",
            "/mysql", "/sql", "/database", "/backup", "/console",
            # Common backup files
            "/backup.zip", "/backup.tar.gz", "/dump.sql", "/database.sql",
            "/db.sql", "/data.sql", "/backup.rar", "/backup.7z"
        ]
        return paths[:self.config.max_paths]
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les mauvaises configurations
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - check_headers: Vérifier les headers de sécurité
                - check_paths: Tester les chemins sensibles
                - check_ssl: Vérifier la configuration SSL/TLS
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Détection des mauvaises configurations sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Scan discret")
        
        vulnerabilities = []
        
        # Vérifier les headers de sécurité
        if self.config.check_headers:
            header_vulns = self._check_security_headers_advanced(target)
            vulnerabilities.extend(header_vulns)
        
        # Vérifier les chemins sensibles
        if self.config.check_paths:
            path_vulns = self._check_sensitive_paths_advanced(target)
            vulnerabilities.extend(path_vulns)
        
        # Vérifier les méthodes HTTP
        if self.config.check_methods:
            method_vulns = self._check_http_methods_advanced(target)
            vulnerabilities.extend(method_vulns)
        
        # Vérifier SSL/TLS
        if self.config.check_ssl:
            ssl_vulns = self._check_ssl_config_advanced(target)
            vulnerabilities.extend(ssl_vulns)
        
        # Vérifier les erreurs de configuration serveur
        if self.config.check_server:
            config_vulns = self._check_server_config_advanced(target)
            vulnerabilities.extend(config_vulns)
        
        # Vérifier les configurations cloud
        if self.config.check_cloud:
            cloud_vulns = self._check_cloud_config(target)
            vulnerabilities.extend(cloud_vulns)
        
        # Vérifier CORS
        if self.config.check_cors:
            cors_vulns = self._check_cors_config(target)
            vulnerabilities.extend(cors_vulns)
        
        # Vérifier open redirect
        if self.config.check_open_redirect:
            redirect_vulns = self._check_open_redirect(target)
            vulnerabilities.extend(redirect_vulns)
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'check_headers' in kwargs:
            self.config.check_headers = kwargs['check_headers']
        if 'check_paths' in kwargs:
            self.config.check_paths = kwargs['check_paths']
        if 'max_paths' in kwargs:
            self.config.max_paths = kwargs['max_paths']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_paths = min(self.config.max_paths, 20)
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
    
    def _check_security_headers_advanced(self, target: str) -> List[Dict[str, Any]]:
        """
        Vérification avancée des headers de sécurité
        
        Args:
            target: URL cible
        """
        vulnerabilities = []
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            self.tests_performed += 1
            
            for header, expected_values in self.security_headers.items():
                if header not in response.headers:
                    vulnerabilities.append({
                        "type": "missing_security_header",
                        "issue": f"Header de sécurité manquant: {header}",
                        "severity": "MEDIUM",
                        "risk_score": 60,
                        "recommendation": f"Ajouter l'en-tête {header}"
                    })
                elif expected_values:
                    value = response.headers[header]
                    if value not in expected_values and expected_values:
                        vulnerabilities.append({
                            "type": "weak_security_header",
                            "issue": f"Header {header} faible: {value}",
                            "severity": "MEDIUM",
                            "risk_score": 55,
                            "recommendation": f"Utiliser: {', '.join(expected_values)}"
                        })
            
            # Vérifier les headers de divulgation
            for header in self.disclosure_headers:
                if header in response.headers:
                    vulnerabilities.append({
                        "type": "information_disclosure",
                        "issue": f"Information divulguée: {header}: {response.headers[header]}",
                        "severity": "LOW",
                        "risk_score": 35,
                        "recommendation": f"Supprimer l'en-tête {header}"
                    })
                    
        except Exception as e:
            if not self.config.passive_detection:
                pass
        
        return vulnerabilities
    
    def _check_sensitive_paths_advanced(self, target: str) -> List[Dict[str, Any]]:
        """
        Vérification avancée des chemins sensibles
        
        Args:
            target: URL cible
        """
        vulnerabilities = []
        
        for idx, path in enumerate(self.sensitive_paths):
            # Pause APT
            if self.config.apt_mode and idx > 0 and idx % 5 == 0:
                self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(0.5, 1.5))
            
            test_url = target.rstrip('/') + path
            
            try:
                headers = self._get_stealth_headers()
                response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                self.tests_performed += 1
                
                if response.status_code == 200:
                    self.vulnerabilities_found += 1
                    vulnerabilities.append({
                        "type": "sensitive_path_exposed",
                        "issue": f"Chemin sensible exposé: {path}",
                        "severity": "HIGH",
                        "risk_score": 85,
                        "recommendation": "Restreindre l'accès à ce chemin",
                        "evidence": f"HTTP {response.status_code}"
                    })
                    print(f"      ✓ Chemin exposé: {path}")
                    
                elif response.status_code == 403:
                    vulnerabilities.append({
                        "type": "sensitive_path_restricted",
                        "issue": f"Chemin sensible restreint: {path} (403)",
                        "severity": "LOW",
                        "risk_score": 30,
                        "recommendation": "Vérifier que l'accès est bien bloqué"
                    })
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _check_http_methods_advanced(self, target: str) -> List[Dict[str, Any]]:
        """
        Vérification avancée des méthodes HTTP
        
        Args:
            target: URL cible
        """
        vulnerabilities = []
        
        for method in self.config_checks["http_methods"]:
            try:
                headers = self._get_stealth_headers()
                response = requests.request(method, target, headers=headers, timeout=10, verify=False)
                self.tests_performed += 1
                
                if method in self.dangerous_methods and response.status_code != 405:
                    vulnerabilities.append({
                        "type": "dangerous_http_method",
                        "issue": f"Méthode HTTP dangereuse autorisée: {method}",
                        "severity": "HIGH",
                        "risk_score": 80,
                        "recommendation": f"Désactiver la méthode {method}"
                    })
                    
            except Exception:
                continue
        
        # Vérification spéciale pour TRACE
        try:
            headers = self._get_stealth_headers()
            response = requests.request('TRACE', target, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                vulnerabilities.append({
                    "type": "trace_enabled",
                    "issue": "Méthode TRACE activée - vulnérable au Cross-Site Tracing",
                    "severity": "MEDIUM",
                    "risk_score": 70,
                    "recommendation": "Désactiver la méthode TRACE"
                })
        except:
            pass
        
        return vulnerabilities
    
    def _check_ssl_config_advanced(self, target: str) -> List[Dict[str, Any]]:
        """
        Vérification avancée de la configuration SSL/TLS
        
        Args:
            target: URL cible
        """
        vulnerabilities = []
        
        parsed = urlparse(target)
        hostname = parsed.hostname
        port = parsed.port or 443
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Vérifier l'expiration
                    import datetime
                    expiry = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_left = (expiry - datetime.datetime.now()).days
                    
                    if days_left < 0:
                        vulnerabilities.append({
                            "type": "ssl_expired",
                            "issue": "Certificat SSL expiré",
                            "severity": "HIGH",
                            "risk_score": 90,
                            "recommendation": "Renouveler le certificat SSL"
                        })
                    elif days_left < 30:
                        vulnerabilities.append({
                            "type": "ssl_expiring_soon",
                            "issue": f"Certificat SSL expire dans {days_left} jours",
                            "severity": "MEDIUM",
                            "risk_score": 65,
                            "recommendation": "Planifier le renouvellement du certificat"
                        })
                    
                    # Vérifier le protocole
                    version = ssock.version()
                    if version in ['TLSv1', 'TLSv1.0', 'SSLv3']:
                        vulnerabilities.append({
                            "type": "weak_ssl_protocol",
                            "issue": f"Protocole SSL/TLS faible: {version}",
                            "severity": "HIGH",
                            "risk_score": 85,
                            "recommendation": "Désactiver TLS 1.0/1.1 et versions inférieures"
                        })
                    
                    # Vérifier HSTS
                    # Note: HSTS est vérifié via les headers HTTP
                        
        except Exception as e:
            vulnerabilities.append({
                "type": "ssl_error",
                "issue": f"Erreur SSL/TLS: {str(e)[:100]}",
                "severity": "MEDIUM",
                "risk_score": 60,
                "recommendation": "Vérifier la configuration SSL/TLS"
            })
        
        return vulnerabilities
    
    def _check_server_config_advanced(self, target: str) -> List[Dict[str, Any]]:
        """
        Vérification avancée de la configuration serveur
        
        Args:
            target: URL cible
        """
        vulnerabilities = []
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            self.tests_performed += 1
            
            # Détection de directory listing
            if 'Index of /' in response.text or 'Parent Directory' in response.text:
                vulnerabilities.append({
                    "type": "directory_listing",
                    "issue": "Directory listing activé",
                    "severity": "MEDIUM",
                    "risk_score": 65,
                    "recommendation": "Désactiver l'indexation des répertoires"
                })
            
            # Détection de mode debug
            debug_indicators = ['debug', 'DEBUG', 'trace', 'TRACE', 'xdebug', 
                               'stack trace', 'exception', 'error reporting']
            for indicator in debug_indicators:
                if indicator in response.text.lower():
                    vulnerabilities.append({
                        "type": "debug_mode",
                        "issue": "Mode debug détecté",
                        "severity": "HIGH",
                        "risk_score": 85,
                        "recommendation": "Désactiver le mode debug en production"
                    })
                    break
            
            # Détection d'erreurs SQL
            sql_errors = ['SQL syntax', 'mysql_fetch', 'ORA-', 'PostgreSQL', 
                         'PDOException', 'SQLSTATE', 'mysql error']
            for error in sql_errors:
                if error.lower() in response.text.lower():
                    vulnerabilities.append({
                        "type": "sql_error_disclosure",
                        "issue": "Erreur SQL divulguée",
                        "severity": "HIGH",
                        "risk_score": 85,
                        "recommendation": "Désactiver l'affichage des erreurs SQL"
                    })
                    break
            
            # Détection de version PHP
            php_pattern = r'PHP\s+Version\s+[\d.]+'
            if re.search(php_pattern, response.text, re.IGNORECASE):
                vulnerabilities.append({
                    "type": "version_disclosure",
                    "issue": "Version PHP divulguée",
                    "severity": "LOW",
                    "risk_score": 25,
                    "recommendation": "Masquer la version PHP"
                })
                    
        except Exception:
            pass
        
        return vulnerabilities
    
    def _check_cloud_config(self, target: str) -> List[Dict[str, Any]]:
        """
        Vérifie les configurations cloud exposées
        
        Args:
            target: URL cible
        """
        vulnerabilities = []
        
        # Vérifier les buckets AWS exposés
        parsed = urlparse(target)
        bucket_patterns = [
            f"{parsed.netloc}.s3.amazonaws.com",
            f"s3.{parsed.netloc}",
            f"{parsed.netloc}.s3-website"
        ]
        
        for bucket in bucket_patterns:
            try:
                response = requests.get(f"https://{bucket}", timeout=10, verify=False)
                if response.status_code == 200:
                    vulnerabilities.append({
                        "type": "cloud_exposure",
                        "issue": f"Bucket S3 exposé: {bucket}",
                        "severity": "HIGH",
                        "risk_score": 85,
                        "recommendation": "Restreindre l'accès au bucket S3"
                    })
            except:
                pass
        
        return vulnerabilities
    
    def _check_cors_config(self, target: str) -> List[Dict[str, Any]]:
        """
        Vérifie la configuration CORS
        
        Args:
            target: URL cible
        """
        vulnerabilities = []
        
        test_origins = ["https://evil.com", "https://attacker.com", "*"]
        
        for origin in test_origins:
            try:
                headers = self._get_stealth_headers({'Origin': origin})
                response = requests.get(target, headers=headers, timeout=10, verify=False)
                
                acao = response.headers.get('Access-Control-Allow-Origin')
                acac = response.headers.get('Access-Control-Allow-Credentials')
                
                if acao == '*' or acao == origin:
                    severity = "HIGH" if acac and acac.lower() == 'true' else "MEDIUM"
                    vulnerabilities.append({
                        "type": "cors_misconfiguration",
                        "issue": f"CORS permissif: ACAO={acao}, ACAC={acac}",
                        "severity": severity,
                        "risk_score": 85 if 'true' in str(acac).lower() else 70,
                        "recommendation": "Restreindre les origines CORS"
                    })
            except:
                pass
        
        return vulnerabilities
    
    def _check_open_redirect(self, target: str) -> List[Dict[str, Any]]:
        """
        Vérifie les vulnérabilités d'open redirect
        
        Args:
            target: URL cible
        """
        vulnerabilities = []
        
        redirect_params = ['redirect', 'url', 'next', 'return', 'return_to', 
                          'goto', 'redirect_url', 'callback', 'dest']
        
        parsed = urlparse(target)
        query_params = parsed.query
        
        for param in redirect_params:
            test_url = f"{target}?{param}=https://evil.com"
            
            try:
                headers = self._get_stealth_headers()
                response = requests.get(test_url, headers=headers, timeout=10, verify=False, allow_redirects=False)
                
                location = response.headers.get('Location', '')
                if location and 'evil.com' in location:
                    vulnerabilities.append({
                        "type": "open_redirect",
                        "issue": f"Open redirect via paramètre {param}",
                        "severity": "MEDIUM",
                        "risk_score": 65,
                        "recommendation": "Valider les URLs de redirection"
                    })
                    break
            except:
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
        
        # Compter par sévérité
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for v in vulnerabilities:
            severity_counts[v.get('severity', 'LOW')] = severity_counts.get(v.get('severity', 'LOW'), 0) + 1
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "tests_performed": self.tests_performed,
            "scan_duration": duration,
            "severity_counts": severity_counts,
            "config": {
                "apt_mode": self.config.apt_mode,
                "check_headers": self.config.check_headers,
                "check_paths": self.config.check_paths,
                "check_ssl": self.config.check_ssl
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune mauvaise configuration détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_severity": {
                "HIGH": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
                "MEDIUM": len([v for v in vulnerabilities if v['severity'] == 'MEDIUM']),
                "LOW": len([v for v in vulnerabilities if v['severity'] == 'LOW'])
            },
            "by_type": {
                "security_headers": len([v for v in vulnerabilities if 'header' in v['type']]),
                "sensitive_paths": len([v for v in vulnerabilities if v['type'] == 'sensitive_path_exposed']),
                "http_methods": len([v for v in vulnerabilities if v['type'] == 'dangerous_http_method']),
                "ssl": len([v for v in vulnerabilities if 'ssl' in v['type']]),
                "cors": len([v for v in vulnerabilities if v['type'] == 'cors_misconfiguration'])
            },
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            if 'recommendation' in vuln:
                recommendations.add(vuln['recommendation'])
        
        if not recommendations:
            recommendations.add("Auditer régulièrement la configuration de l'infrastructure")
            recommendations.add("Utiliser des scanners de vulnérabilités automatisés")
        
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
    md = MisconfigDetector()
    results = md.scan("https://example.com")
    print(f"Mauvaises configurations: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = MisconfigConfig(apt_mode=True, max_paths=20)
    md_apt = MisconfigDetector(config=apt_config)
    results_apt = md_apt.scan("https://example.com", apt_mode=True)
    print(f"Mauvaises configurations (APT): {results_apt['count']}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")