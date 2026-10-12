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
import ipaddress
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
    
    def _is_private_ip(self, ip_str: str) -> bool:
        """Vérifie si une adresse IP est privée, réservée ou de loopback pour prévenir le SSRF."""
        try:
            ip = ipaddress.ip_address(ip_str)
            return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
        except ValueError:
            return False

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

        if not hostname:
            return self._generate_results(target, [{
                "type": "invalid_target",
                "severity": "INFO",
                "details": "Hostname invalide ou manquant dans la cible.",
            }])

        try:
            ip_address = socket.gethostbyname(hostname)
            if self._is_private_ip(ip_address):
                return self._generate_results(target, [{
                    "type": "ssrf_protection",
                    "severity": "CRITICAL",
                    "details": f"La cible '{hostname}' ({ip_address}) est une adresse interne ou réservée. "
                               "L'analyse est bloquée pour prévenir une attaque de type SSRF (Server-Side Request Forgery).",
                    "risk_score": 100
                }])
        except socket.gaierror:
            return self._generate_results(target, [{
                "type": "dns_error",
                "severity": "HIGH",
                "details": f"Impossible de résoudre le nom d'hôte : '{hostname}'.",
                "risk_score": 75
            }])

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
                    