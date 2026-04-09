#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection de fuites d'informations pour RedForge
Détecte les fuites d'informations sensibles
Version avec support furtif, APT et détection avancée
"""

import re
import time
import random
import json
import requests
import base64
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class InfoLeakageConfig:
    """Configuration avancée pour la détection de fuites d'informations"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_pattern_matches: int = 10
    timeout: int = 10
    deep_scan: bool = False
    check_headers: bool = True
    check_paths: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    check_js_files: bool = True
    check_source_comments: bool = True
    max_js_files: int = 10
    detect_version_info: bool = True


class InfoLeakage:
    """Détection avancée des fuites d'informations"""
    
    def __init__(self, config: Optional[InfoLeakageConfig] = None):
        """
        Initialise le détecteur de fuites d'informations
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or InfoLeakageConfig()
        
        # Patterns sensibles améliorés
        self.sensitive_patterns = {
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "ip_address": r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
            "phone": r'\+?[\d\s-]{10,}',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            "api_key": r'[A-Za-z0-9]{32,}',
            "jwt_token": r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
            "password": r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            "secret": r'secret["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            "token": r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            "aws_key": r'AKIA[0-9A-Z]{16}',
            "private_key": r'-----BEGIN (?:RSA|DSA|EC|OPENSSH) PRIVATE KEY-----',
            "database_url": r'(?:mysql|postgresql|mongodb|redis)://[^/\s]+',
            "internal_ip": r'\b(?:10|172\.(?:1[6-9]|2[0-9]|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b',
            "slack_token": r'xox[baprs]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}',
            "github_token": r'gh[pous]_[A-Za-z0-9]{36}',
            "aws_secret": r'[A-Za-z0-9/+=]{40}',
            "jdbc_url": r'jdbc:[a-zA-Z]+://[^/\s]+',
            "mongodb_uri": r'mongodb(?:\+srv)?://[^/\s]+',
            "redis_url": r'redis://[^/\s]+',
            "api_version": r'v\d+\.\d+\.\d+',
            "server_version": r'[A-Za-z]+/\d+\.\d+\.\d+'
        }
        
        # Headers sensibles
        self.sensitive_headers = [
            'Server', 'X-Powered-By', 'X-AspNet-Version', 'X-AspNetMvc-Version',
            'X-Drupal-Cache', 'X-Drupal-Dynamic-Cache', 'X-Generator',
            'X-Runtime', 'X-Version', 'X-Backend', 'X-Proxy-Cache',
            'X-Cache', 'X-Cache-Hits', 'X-Server-Name', 'X-Forwarded-For',
            'X-Real-IP', 'X-Originating-IP', 'X-Client-IP'
        ]
        
        # Chemins sensibles
        self.sensitive_paths = self._generate_sensitive_paths()
        
        # Patterns de réponse
        self.response_patterns = {
            "stack_trace": [r'at\s+[\w\.]+\([\w\.]+:\d+\)', r'Traceback', r'Stack Trace', r'Exception in thread'],
            "sql_error": [r'SQL syntax', r'mysql_fetch', r'ORA-\d+', r'PostgreSQL', r'SQLSTATE'],
            "debug_info": [r'DEBUG', r'DEVELOPMENT', r'debug_mode', r'development mode', r'APP_DEBUG'],
            "file_path": [r'[A-Z]:\\[\\\w\s]+', r'\/[\w\/]+\.(?:php|asp|jsp|py|rb)'],
            "internal_paths": [r'\/var\/www\/', r'\/home\/[\w]+\/public_html', r'C:\\inetpub\\'],
            "php_info": [r'PHP Version', r'PHP Extension', r'System', r'Build Date'],
            "environment": [r'APP_ENV', r'DATABASE_URL', r'REDIS_URL', r'SMTP_HOST']
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
    
    def _generate_sensitive_paths(self) -> List[str]:
        """Génère une liste de chemins sensibles"""
        return [
            # Version control
            '/.git/config', '/.git/HEAD', '/.svn/entries', '/.hg/', '/.bzr/',
            # Environment and config
            '/.env', '/.env.backup', '/.env.local', '/.env.production',
            '/.htaccess', '/.htpasswd', '/web.config', '/robots.txt',
            '/sitemap.xml', '/crossdomain.xml', '/clientaccesspolicy.xml',
            # PHP info and debug
            '/phpinfo.php', '/info.php', '/php_info.php', '/test.php',
            '/debug.php', '/info.php', '/php.php', '/status.php',
            '/phpinfo', '/info', '/phpinfo.phtml',
            # Server status
            '/server-status', '/server-info', '/status', '/health',
            '/metrics', '/healthz', '/ready', '/live', '/ping',
            # API documentation
            '/api/swagger.json', '/swagger-ui.html', '/v2/api-docs',
            '/v3/api-docs', '/openapi.json', '/api-docs', '/docs',
            '/swagger', '/api/swagger', '/swagger/v1/swagger.json',
            # Actuator endpoints
            '/actuator', '/actuator/env', '/actuator/health', '/actuator/info',
            '/actuator/metrics', '/actuator/httptrace', '/actuator/beans',
            '/actuator/configprops', '/actuator/mappings', '/actuator/scheduledtasks',
            # Debug tools
            '/_profiler', '/_phpinfo', '/_debug', '/_dev', '/_test',
            '/debugbar', '/debug/default', '/debug/', '/_debugbar',
            '/xdebug', '/xdebug_info', '/xdebug_info.php',
            # Backup files
            '/backup.zip', '/backup.tar.gz', '/dump.sql', '/database.sql',
            '/db.sql', '/data.sql', '/backup.rar', '/backup.7z',
            '/old/', '/backup/', '/temp/', '/tmp/'
        ]
    
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
        Scanne les fuites d'informations
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - deep_scan: Scan approfondi
                - check_headers: Vérifier les headers
                - check_paths: Vérifier les chemins sensibles
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Détection des fuites d'informations sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Scan discret")
        
        vulnerabilities = []
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=self.config.timeout, verify=False)
            content = response.text
            response_headers = response.headers
            
            # Vérifier les patterns sensibles
            pattern_vulns = self._check_sensitive_patterns(content)
            vulnerabilities.extend(pattern_vulns)
            self.vulnerabilities_found += len(pattern_vulns)
            
            # Vérifier les headers sensibles
            if self.config.check_headers:
                header_vulns = self._check_sensitive_headers(response_headers)
                vulnerabilities.extend(header_vulns)
                self.vulnerabilities_found += len(header_vulns)
            
            # Vérifier les patterns de réponse
            pattern_response_vulns = self._check_response_patterns(content)
            vulnerabilities.extend(pattern_response_vulns)
            self.vulnerabilities_found += len(pattern_response_vulns)
            
            # Vérifier les chemins sensibles
            if self.config.check_paths:
                path_vulns = self._check_sensitive_paths(target)
                vulnerabilities.extend(path_vulns)
                self.vulnerabilities_found += len(path_vulns)
            
            # Vérifier les fichiers JS
            if self.config.check_js_files:
                js_vulns = self._check_js_files(target, content)
                vulnerabilities.extend(js_vulns)
                self.vulnerabilities_found += len(js_vulns)
            
            # Scan approfondi
            if self.config.deep_scan:
                deep_vulns = self._deep_scan(target)
                vulnerabilities.extend(deep_vulns)
                self.vulnerabilities_found += len(deep_vulns)
                
        except Exception as e:
            if not self.config.passive_detection:
                print(f"    ⚠️ Erreur scan: {e}")
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'deep_scan' in kwargs:
            self.config.deep_scan = kwargs['deep_scan']
        if 'check_headers' in kwargs:
            self.config.check_headers = kwargs['check_headers']
        if 'check_paths' in kwargs:
            self.config.check_paths = kwargs['check_paths']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.deep_scan = False
            self.config.max_js_files = min(self.config.max_js_files, 5)
            self.config.delay_between_tests = (5, 15)
    
    def _check_sensitive_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Vérifie les patterns sensibles dans le contenu"""
        vulnerabilities = []
        
        for pattern_name, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Dédupliquer et limiter
                unique_matches = list(set(matches))[:self.config.max_pattern_matches]
                for match in unique_matches:
                    # Filtrer les faux positifs
                    if self._is_false_positive(pattern_name, match):
                        continue
                    
                    severity = "CRITICAL" if pattern_name in ['password', 'secret', 'private_key', 'aws_secret'] else "HIGH"
                    vulnerabilities.append({
                        "type": "sensitive_data",
                        "pattern": pattern_name,
                        "value": self._mask_sensitive_value(match) if len(match) > 20 else match,
                        "severity": severity,
                        "location": "response_body",
                        "risk_score": 95 if severity == "CRITICAL" else 85
                    })
                    
                    if not self.config.apt_mode:
                        print(f"      ✓ {pattern_name} trouvé: {self._mask_sensitive_value(match)[:50]}...")
        
        return vulnerabilities
    
    def _is_false_positive(self, pattern_name: str, match: str) -> bool:
        """Détecte les faux positifs"""
        # Exemples de faux positifs
        false_positives = {
            "email": ['example.com', 'test.com', 'domain.com'],
            "ip_address": ['0.0.0.0', '255.255.255.255', '127.0.0.1'],
            "api_key": ['XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX']
        }
        
        if pattern_name in false_positives:
            return any(fp in match for fp in false_positives[pattern_name])
        return False
    
    def _mask_sensitive_value(self, value: str) -> str:
        """Masque les valeurs sensibles"""
        if len(value) <= 10:
            return value
        return value[:6] + '...' + value[-4:]
    
    def _check_sensitive_headers(self, headers: Dict) -> List[Dict[str, Any]]:
        """Vérifie les headers sensibles"""
        vulnerabilities = []
        
        for header in self.sensitive_headers:
            if header in headers:
                vulnerabilities.append({
                    "type": "header_disclosure",
                    "header": header,
                    "value": headers[header],
                    "severity": "LOW",
                    "location": "response_header",
                    "risk_score": 30
                })
                print(f"      ✓ Header divulgué: {header}: {headers[header]}")
        
        return vulnerabilities
    
    def _check_response_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Vérifie les patterns de réponse"""
        vulnerabilities = []
        
        for pattern_type, patterns in self.response_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    severity = "HIGH" if pattern_type in ['stack_trace', 'sql_error', 'php_info'] else "MEDIUM"
                    vulnerabilities.append({
                        "type": pattern_type,
                        "severity": severity,
                        "location": "response_body",
                        "details": f"Pattern {pattern_type} détecté",
                        "risk_score": 80 if severity == "HIGH" else 60
                    })
                    print(f"      ✓ {pattern_type} détecté")
                    break
        
        return vulnerabilities
    
    def _check_sensitive_paths(self, target: str) -> List[Dict[str, Any]]:
        """Vérifie l'accès aux chemins sensibles"""
        vulnerabilities = []
        
        for idx, path in enumerate(self.sensitive_paths):
            if self.config.apt_mode and idx > 15:
                break
            
            if self.config.random_delays:
                time.sleep(random.uniform(0.3, 0.8))
            
            test_url = urljoin(target, path)
            
            try:
                headers = self._get_stealth_headers()
                response = requests.get(test_url, headers=headers, timeout=self.config.timeout, verify=False)
                self.tests_performed += 1
                
                if response.status_code == 200:
                    # Analyser le contenu pour trouver des données sensibles
                    content = response.text
                    found_sensitive = False
                    
                    for pattern_name, pattern in self.sensitive_patterns.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            vulnerabilities.append({
                                "type": "sensitive_path_exposed",
                                "path": path,
                                "severity": "HIGH",
                                "details": f"Chemin sensible exposé: {path} - Contient {pattern_name}",
                                "risk_score": 85
                            })
                            print(f"      ✓ Chemin sensible exposé: {path} (contient {pattern_name})")
                            found_sensitive = True
                            break
                    
                    if not found_sensitive and len(content) > 100:
                        vulnerabilities.append({
                            "type": "sensitive_path_exposed",
                            "path": path,
                            "severity": "MEDIUM",
                            "details": f"Chemin sensible accessible: {path}",
                            "risk_score": 65
                        })
                        print(f"      ✓ Chemin sensible accessible: {path}")
                        
            except Exception:
                continue
        
        return vulnerabilities
    
    def _check_js_files(self, target: str, html_content: str) -> List[Dict[str, Any]]:
        """Vérifie les fichiers JavaScript pour des fuites d'informations"""
        vulnerabilities = []
        
        # Extraire les URLs des fichiers JS
        js_pattern = r'<script[^>]+src=["\']([^"\']+\.js)["\']'
        js_urls = re.findall(js_pattern, html_content)
        
        for js_url in js_urls[:self.config.max_js_files]:
            if not js_url.startswith(('http://', 'https://')):
                js_url = urljoin(target, js_url)
            
            try:
                headers = self._get_stealth_headers()
                response = requests.get(js_url, headers=headers, timeout=self.config.timeout, verify=False)
                self.tests_performed += 1
                
                # Vérifier les patterns sensibles dans le JS
                for pattern_name, pattern in self.sensitive_patterns.items():
                    matches = re.findall(pattern, response.text, re.IGNORECASE)
                    if matches:
                        for match in set(matches)[:3]:
                            vulnerabilities.append({
                                "type": "js_leakage",
                                "pattern": pattern_name,
                                "value": self._mask_sensitive_value(match),
                                "severity": "HIGH",
                                "location": f"javascript:{js_url}",
                                "risk_score": 80
                            })
                            print(f"      ✓ {pattern_name} trouvé dans JS: {js_url}")
                            break
                            
            except Exception:
                continue
        
        return vulnerabilities
    
    def _deep_scan(self, target: str) -> List[Dict[str, Any]]:
        """Scan approfondi pour détecter plus de fuites"""
        vulnerabilities = []
        
        # Scanner les sous-domaines
        try:
            parsed = urlparse(target)
            domain = parsed.netloc.replace('www.', '')
            # Extraire le domaine principal
            domain_parts = domain.split('.')
            if len(domain_parts) > 2:
                main_domain = '.'.join(domain_parts[-2:])
            else:
                main_domain = domain
            
            common_subdomains = ['admin', 'dev', 'test', 'staging', 'api', 'backup',
                                 'mail', 'ftp', 'dashboard', 'portal', 'manage']
            
            for sub in common_subdomains:
                test_url = f"https://{sub}.{main_domain}"
                try:
                    headers = self._get_stealth_headers()
                    response = requests.get(test_url, headers=headers, timeout=5, verify=False)
                    self.tests_performed += 1
                    
                    if response.status_code == 200:
                        vulnerabilities.append({
                            "type": "subdomain_disclosure",
                            "subdomain": sub,
                            "severity": "MEDIUM",
                            "details": f"Sous-domaine accessible: {sub}.{main_domain}",
                            "risk_score": 60
                        })
                        print(f"      ✓ Sous-domaine trouvé: {sub}.{main_domain}")
                except:
                    pass
        except:
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
                "deep_scan": self.config.deep_scan,
                "check_headers": self.config.check_headers,
                "check_paths": self.config.check_paths
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune fuite d'information détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_type": {
                "sensitive_data": len([v for v in vulnerabilities if v['type'] == 'sensitive_data']),
                "header_disclosure": len([v for v in vulnerabilities if v['type'] == 'header_disclosure']),
                "sensitive_path": len([v for v in vulnerabilities if v['type'] == 'sensitive_path_exposed']),
                "js_leakage": len([v for v in vulnerabilities if v['type'] == 'js_leakage']),
                "subdomain_disclosure": len([v for v in vulnerabilities if v['type'] == 'subdomain_disclosure'])
            },
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type', '')
            
            if vuln_type == 'sensitive_data':
                recommendations.add("Ne jamais exposer de données sensibles dans les réponses HTTP")
                recommendations.add("Utiliser des variables d'environnement pour les secrets")
            
            if vuln_type == 'header_disclosure':
                recommendations.add("Désactiver les en-têtes divulguant des informations serveur")
            
            if vuln_type == 'sensitive_path_exposed':
                recommendations.add("Restreindre l'accès aux fichiers de configuration et de débogage")
                recommendations.add("Déplacer les fichiers sensibles hors du répertoire web")
            
            if vuln_type == 'js_leakage':
                recommendations.add("Ne pas inclure de clés API ou secrets dans les fichiers JavaScript")
                recommendations.add("Utiliser des variables d'environnement côté serveur")
            
            if vuln_type == 'subdomain_disclosure':
                recommendations.add("Configurer correctement les DNS pour éviter les sous-domaines non sécurisés")
        
        if not recommendations:
            recommendations.add("Auditer régulièrement les fuites d'informations")
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
    il = InfoLeakage()
    results = il.scan("https://example.com")
    print(f"Fuites d'informations: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = InfoLeakageConfig(apt_mode=True, deep_scan=False)
    il_apt = InfoLeakage(config=apt_config)
    results_apt = il_apt.scan("https://example.com", apt_mode=True)
    print(f"Fuites d'informations (APT): {results_apt['count']}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")