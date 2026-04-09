#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques Man-in-the-Middle pour RedForge
Détection et exploitation des vulnérabilités MITM
Version avec support furtif, APT et techniques avancées
"""

import ssl
import socket
import threading
import time
import random
import requests
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class MITMConfig:
    """Configuration avancée pour les attaques MITM"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    timeout: int = 10
    check_ssl: bool = True
    check_hsts: bool = True
    check_dns: bool = True
    check_certificate: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    check_weak_ciphers: bool = True
    check_certificate_transparency: bool = True
    check_dnssec: bool = True
    max_proxy_connections: int = 100


class MITMAttacks:
    """Détection et exploitation avancée des attaques MITM"""
    
    def __init__(self, config: Optional[MITMConfig] = None):
        """
        Initialise le détecteur d'attaques MITM
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or MITMConfig()
        self.vulnerable_services = []
        self.intercepted_data = []
        self.is_listening = False
        self.proxy_server = None
        self.certificate_info = None
        
        # Ciphers faibles à détecter
        self.weak_ciphers = [
            'RC4', 'DES', '3DES', 'NULL', 'EXPORT', 'MD5', 'SHA1',
            'TLS_RSA_WITH_RC4_128_SHA', 'TLS_RSA_WITH_3DES_EDE_CBC_SHA',
            'TLS_RSA_WITH_AES_128_CBC_SHA', 'TLS_RSA_WITH_AES_256_CBC_SHA'
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
        Scanne les vulnérabilités MITM
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - check_ssl: Vérifier SSL/TLS
                - check_hsts: Vérifier HSTS
                - check_dns: Vérifier DNS
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test des vulnérabilités MITM sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        
        parsed = urlparse(target)
        hostname = parsed.hostname
        port = parsed.port or 443
        
        # Vérifier SSL/TLS
        if self.config.check_ssl:
            ssl_vulns = self._check_ssl_vulnerabilities_advanced(hostname, port)
            vulnerabilities.extend(ssl_vulns)
            self.vulnerabilities_found += len(ssl_vulns)
        
        # Vérifier HSTS
        if self.config.check_hsts:
            hsts_vuln = self._check_hsts_advanced(target)
            if hsts_vuln:
                vulnerabilities.append(hsts_vuln)
                self.vulnerabilities_found += 1
        
        # Vérifier les vulnérabilités DNS
        if self.config.check_dns:
            dns_vulns = self._check_dns_vulnerabilities_advanced(hostname)
            vulnerabilities.extend(dns_vulns)
            self.vulnerabilities_found += len(dns_vulns)
        
        # Vérifier les redirections HTTP vers HTTPS
        redirect_vuln = self._check_http_redirect_advanced(target)
        if redirect_vuln:
            vulnerabilities.append(redirect_vuln)
            self.vulnerabilities_found += 1
        
        # Vérifier les certificats
        if self.config.check_certificate:
            cert_vuln = self._check_certificate_security(hostname, port)
            if cert_vuln:
                vulnerabilities.append(cert_vuln)
                self.vulnerabilities_found += 1
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'check_ssl' in kwargs:
            self.config.check_ssl = kwargs['check_ssl']
        if 'check_hsts' in kwargs:
            self.config.check_hsts = kwargs['check_hsts']
        if 'check_dns' in kwargs:
            self.config.check_dns = kwargs['check_dns']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.delay_between_tests = (5, 15)
    
    def _check_ssl_vulnerabilities_advanced(self, hostname: str, port: int) -> List[Dict[str, Any]]:
        """
        Vérification avancée des vulnérabilités SSL/TLS
        
        Args:
            hostname: Nom d'hôte
            port: Port
        """
        vulnerabilities = []
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.config.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    self.certificate_info = cert
                    
                    # Vérifier la version SSL/TLS
                    version = ssock.version()
                    if version in ['SSLv3', 'TLSv1', 'TLSv1.0']:
                        vulnerabilities.append({
                            "type": "weak_ssl_protocol",
                            "version": version,
                            "severity": "HIGH",
                            "details": f"Protocole SSL/TLS faible: {version}",
                            "risk_score": 85
                        })
                        print(f"      ✓ Protocole SSL faible: {version}")
                    elif version in ['TLSv1.1']:
                        vulnerabilities.append({
                            "type": "deprecated_ssl_protocol",
                            "version": version,
                            "severity": "MEDIUM",
                            "details": f"Protocole SSL/TLS déprécié: {version}",
                            "risk_score": 65
                        })
                    
                    # Vérifier les cipher suites
                    if self.config.check_weak_ciphers:
                        cipher = ssock.cipher()
                        if cipher:
                            cipher_name = cipher[0]
                            for weak_cipher in self.weak_ciphers:
                                if weak_cipher.lower() in cipher_name.lower():
                                    vulnerabilities.append({
                                        "type": "weak_cipher",
                                        "cipher": cipher_name,
                                        "severity": "HIGH",
                                        "details": f"Cipher suite faible: {cipher_name}",
                                        "risk_score": 85
                                    })
                                    print(f"      ✓ Cipher faible: {cipher_name}")
                                    break
                    
                    # Vérifier la longueur de la clé
                    if 'subjectAltKey' in cert:
                        key_info = cert.get('subjectAltKey', '')
                        if 'RSA' in str(key_info):
                            # Vérifier la longueur de la clé RSA
                            vulnerabilities.append({
                                "type": "short_key",
                                "severity": "MEDIUM",
                                "details": "Clé RSA potentiellement faible (< 2048 bits)",
                                "risk_score": 70
                            })
                        
        except socket.timeout:
            pass
        except Exception as e:
            if not self.config.passive_detection:
                vulnerabilities.append({
                    "type": "ssl_error",
                    "severity": "MEDIUM",
                    "details": f"Erreur SSL: {str(e)[:100]}",
                    "risk_score": 50
                })
        
        return vulnerabilities
    
    def _check_hsts_advanced(self, target: str) -> Optional[Dict[str, Any]]:
        """
        Vérification avancée de HSTS
        
        Args:
            target: URL cible
        """
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=self.config.timeout, verify=False)
            self.tests_performed += 1
            
            hsts = response.headers.get('Strict-Transport-Security', '')
            
            if not hsts:
                return {
                    "type": "missing_hsts",
                    "severity": "MEDIUM",
                    "details": "HSTS (HTTP Strict Transport Security) manquant",
                    "recommendation": "Ajouter l'en-tête Strict-Transport-Security",
                    "risk_score": 65
                }
            else:
                # Analyser la valeur HSTS
                if 'max-age=0' in hsts:
                    return {
                        "type": "weak_hsts",
                        "severity": "MEDIUM",
                        "details": f"HSTS avec max-age=0: {hsts}",
                        "risk_score": 60
                    }
                elif 'includeSubDomains' not in hsts:
                    return {
                        "type": "hsts_no_subdomains",
                        "severity": "LOW",
                        "details": "HSTS sans includeSubDomains",
                        "risk_score": 40
                    }
                
        except Exception:
            pass
        
        return None
    
    def _check_dns_vulnerabilities_advanced(self, hostname: str) -> List[Dict[str, Any]]:
        """
        Vérification avancée des vulnérabilités DNS
        
        Args:
            hostname: Nom d'hôte
        """
        vulnerabilities = []
        
        try:
            import dns.resolver
            import dns.exception
            
            # Vérifier DNSSEC
            if self.config.check_dnssec:
                try:
                    dns.resolver.resolve(hostname, 'A', want_dnssec=True)
                except dns.resolver.NoAnswer:
                    vulnerabilities.append({
                        "type": "missing_dnssec",
                        "severity": "MEDIUM",
                        "details": "DNSSEC non activé - vulnérable au DNS spoofing",
                        "risk_score": 70
                    })
                    print(f"      ✓ DNSSEC manquant")
                except dns.exception.DNSException:
                    pass
            
            # Vérifier les enregistrements DNS
            try:
                answers = dns.resolver.resolve(hostname, 'A')
                for answer in answers:
                    ip = str(answer)
                    # Vérifier les IPs internes
                    if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
                        vulnerabilities.append({
                            "type": "internal_ip_disclosure",
                            "ip": ip,
                            "severity": "LOW",
                            "details": f"IP interne divulguée: {ip}",
                            "risk_score": 35
                        })
            except:
                pass
                
        except ImportError:
            pass
        except Exception:
            pass
        
        return vulnerabilities
    
    def _check_http_redirect_advanced(self, target: str) -> Optional[Dict[str, Any]]:
        """
        Vérification avancée de la redirection HTTP vers HTTPS
        
        Args:
            target: URL cible
        """
        http_url = target.replace('https://', 'http://')
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(http_url, headers=headers, timeout=self.config.timeout, 
                                  verify=False, allow_redirects=False)
            self.tests_performed += 1
            
            if response.status_code == 200:
                return {
                    "type": "http_accessible",
                    "severity": "HIGH",
                    "details": "Version HTTP accessible sans redirection HTTPS",
                    "recommendation": "Rediriger HTTP vers HTTPS",
                    "risk_score": 85
                }
            elif response.status_code not in [301, 302, 307, 308]:
                return {
                    "type": "missing_https_redirect",
                    "severity": "MEDIUM",
                    "details": f"Redirection HTTPS manquante (HTTP {response.status_code})",
                    "risk_score": 65
                }
                
        except Exception:
            pass
        
        return None
    
    def _check_certificate_security(self, hostname: str, port: int) -> Optional[Dict[str, Any]]:
        """
        Vérification avancée de la sécurité du certificat
        
        Args:
            hostname: Nom d'hôte
            port: Port
        """
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((hostname, port), timeout=self.config.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Vérifier l'expiration
                    import datetime
                    expiry_str = cert.get('notAfter', '')
                    if expiry_str:
                        expiry = datetime.datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                        days_left = (expiry - datetime.datetime.now()).days
                        
                        if days_left < 0:
                            return {
                                "type": "expired_certificate",
                                "severity": "CRITICAL",
                                "details": f"Certificat expiré depuis {-days_left} jours",
                                "risk_score": 95
                            }
                        elif days_left < 30:
                            return {
                                "type": "expiring_certificate",
                                "severity": "HIGH",
                                "details": f"Certificat expire dans {days_left} jours",
                                "risk_score": 85
                            }
                    
                    # Vérifier l'émetteur
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    subject = dict(x[0] for x in cert.get('subject', []))
                    
                    if issuer.get('organizationName') == subject.get('organizationName'):
                        return {
                            "type": "self_signed_cert",
                            "severity": "HIGH",
                            "details": "Certificat auto-signé détecté",
                            "recommendation": "Utiliser un certificat signé par une autorité reconnue",
                            "risk_score": 85
                        }
                    
                    # Vérifier le wildcard
                    common_name = subject.get('commonName', '')
                    if common_name.startswith('*.'):
                        return {
                            "type": "wildcard_certificate",
                            "severity": "MEDIUM",
                            "details": f"Certificat wildcard détecté: {common_name}",
                            "risk_score": 60
                        }
                        
        except Exception:
            pass
        
        return None
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "vulnerable": len(vulnerabilities) > 0,
            "count": len(vulnerabilities),
            "tests_performed": self.tests_performed,
            "scan_duration": duration,
            "tests_per_second": self.tests_performed / duration if duration > 0 else 0,
            "certificate_info": self.certificate_info,
            "config": {
                "apt_mode": self.config.apt_mode,
                "check_ssl": self.config.check_ssl,
                "check_hsts": self.config.check_hsts,
                "check_dns": self.config.check_dns
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité MITM détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_type": {
                "ssl_tls": len([v for v in vulnerabilities if 'ssl' in v['type'] or 'cipher' in v['type'] or 'certificate' in v['type']]),
                "hsts": len([v for v in vulnerabilities if 'hsts' in v['type']]),
                "dns": len([v for v in vulnerabilities if 'dns' in v['type']]),
                "http": len([v for v in vulnerabilities if 'http' in v['type']])
            },
            "critical": len([v for v in vulnerabilities if v.get('severity') == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v.get('severity') == 'HIGH']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type', '')
            
            if 'ssl' in vuln_type or 'protocol' in vuln_type:
                recommendations.add("Désactiver SSLv3, TLSv1.0 et TLSv1.1")
                recommendations.add("Utiliser TLS 1.2 ou supérieur")
            
            if 'cipher' in vuln_type:
                recommendations.add("Désactiver les cipher suites faibles (RC4, DES, 3DES)")
                recommendations.add("Utiliser des cipher suites fortes (AES-GCM, ChaCha20)")
            
            if 'hsts' in vuln_type:
                recommendations.add("Activer HSTS avec max-age long et includeSubDomains")
            
            if 'dns' in vuln_type:
                recommendations.add("Activer DNSSEC pour prévenir le DNS spoofing")
            
            if 'certificate' in vuln_type:
                recommendations.add("Utiliser des certificats signés par une autorité reconnue")
                recommendations.add("Renouveler les certificats avant expiration")
            
            if 'http' in vuln_type:
                recommendations.add("Rediriger tout le trafic HTTP vers HTTPS")
                recommendations.add("Utiliser HSTS preload")
        
        if not recommendations:
            recommendations.add("Auditer régulièrement la configuration TLS/SSL")
            recommendations.add("Utiliser des outils comme SSL Labs pour les tests")
        
        return list(recommendations)
    
    def start_interceptor(self, port: int = 8080, **kwargs):
        """
        Démarre un proxy d'interception MITM
        
        Args:
            port: Port d'écoute du proxy
            **kwargs: Options d'interception
        """
        class MITMProxy(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass
            
            def do_GET(self):
                self.intercept_request()
            
            def do_POST(self):
                self.intercept_request()
            
            def do_PUT(self):
                self.intercept_request()
            
            def do_DELETE(self):
                self.intercept_request()
            
            def intercept_request(self):
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length) if content_length > 0 else b''
                
                # Masquer les données sensibles dans les logs
                data_str = post_data.decode('utf-8', errors='ignore')[:500]
                if 'password' in data_str.lower() or 'token' in data_str.lower():
                    data_str = "*** MASQUÉ ***"
                
                intercepted = {
                    "method": self.command,
                    "path": self.path,
                    "headers": dict(self.headers),
                    "data": data_str,
                    "timestamp": time.time()
                }
                
                self.intercepted_data.append(intercepted)
                print(f"      📡 Requête interceptée: {self.command} {self.path[:100]}")
                
                # Forward la requête
                try:
                    target_url = f"https://{self.headers.get('Host', '')}{self.path}"
                    
                    forward_headers = {k: v for k, v in self.headers.items() 
                                      if k.lower() not in ['host', 'content-length']}
                    
                    if self.command == 'GET':
                        response = requests.get(target_url, headers=forward_headers, 
                                               timeout=self.config.timeout, verify=False)
                    elif self.command == 'POST':
                        response = requests.post(target_url, data=post_data, 
                                                headers=forward_headers, timeout=self.config.timeout, verify=False)
                    elif self.command == 'PUT':
                        response = requests.put(target_url, data=post_data, 
                                               headers=forward_headers, timeout=self.config.timeout, verify=False)
                    elif self.command == 'DELETE':
                        response = requests.delete(target_url, headers=forward_headers, 
                                                  timeout=self.config.timeout, verify=False)
                    else:
                        response = requests.request(self.command, target_url, data=post_data,
                                                   headers=forward_headers, timeout=self.config.timeout, verify=False)
                    
                    self.send_response(response.status_code)
                    for header, value in response.headers.items():
                        if header.lower() not in ['content-encoding', 'transfer-encoding']:
                            self.send_header(header, value)
                    self.end_headers()
                    self.wfile.write(response.content)
                    
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    print(f"      ✗ Erreur forwarding: {e}")
        
        # Attacher les données interceptées à la classe
        MITMProxy.intercepted_data = self.intercepted_data
        
        self.proxy_server = HTTPServer(('0.0.0.0', port), MITMProxy)
        self.is_listening = True
        
        thread = threading.Thread(target=self.proxy_server.serve_forever, daemon=True)
        thread.start()
        
        print(f"      Proxy MITM démarré sur port {port}")
        print(f"      Configurez votre navigateur pour utiliser localhost:{port} comme proxy")
    
    def stop_interceptor(self):
        """Arrête le proxy d'interception MITM"""
        if self.proxy_server:
            self.proxy_server.shutdown()
            self.proxy_server = None
            self.is_listening = False
            print("      Proxy MITM arrêté")
    
    def get_intercepted_data(self) -> List[Dict]:
        """Retourne les données interceptées"""
        return self.intercepted_data
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "tests_performed": self.tests_performed,
            "vulnerabilities_found": self.vulnerabilities_found,
            "success_rate": (self.vulnerabilities_found / max(1, self.tests_performed) * 100),
            "scan_duration": time.time() - self.start_time if self.start_time else 0,
            "intercepted_count": len(self.intercepted_data),
            "rate_limit_hits": self.rate_limit_hits
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    mitm = MITMAttacks()
    results = mitm.scan("https://example.com")
    print(f"Vulnérabilités MITM: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = MITMConfig(apt_mode=True, check_ssl=True, check_hsts=True)
    mitm_apt = MITMAttacks(config=apt_config)
    results_apt = mitm_apt.scan("https://example.com", apt_mode=True)
    print(f"Vulnérabilités MITM (APT): {results_apt['count']}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")