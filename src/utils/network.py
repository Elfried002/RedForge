#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module réseau pour RedForge
Utilitaires pour les opérations réseau avec support furtif et APT
Version avec proxy, rotation IP, et analyses avancées
"""

import socket
import ipaddress
import subprocess
import random
import time
import threading
from typing import List, Tuple, Optional, Dict, Any, Union
from urllib.parse import urlparse
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class ProxyConfig:
    """Configuration proxy"""
    http: Optional[str] = None
    https: Optional[str] = None
    socks: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    rotation_list: List[str] = None


class NetworkUtils:
    """Utilitaires réseau avancés avec support furtif"""
    
    def __init__(self):
        self.stealth_mode = False
        self.apt_mode = False
        self.proxy_config = ProxyConfig()
        self.proxy_index = 0
        self.session = None
        self._setup_session()
    
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif"""
        self.stealth_mode = enabled
        if enabled:
            self._setup_stealth_session()
    
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT"""
        self.apt_mode = enabled
        if enabled:
            self._setup_stealth_session()
    
    def set_proxy(self, proxy_url: str, proxy_type: str = "http"):
        """Configure un proxy"""
        if proxy_type == "http":
            self.proxy_config.http = proxy_url
        elif proxy_type == "https":
            self.proxy_config.https = proxy_url
        elif proxy_type == "socks":
            self.proxy_config.socks = proxy_url
        
        self._setup_session()
    
    def set_proxy_rotation(self, proxies: List[str]):
        """Configure une rotation de proxies"""
        self.proxy_config.rotation_list = proxies
        self.proxy_index = 0
    
    def _get_next_proxy(self) -> Optional[str]:
        """Retourne le prochain proxy en rotation"""
        if self.proxy_config.rotation_list:
            proxy = self.proxy_config.rotation_list[self.proxy_index]
            self.proxy_index = (self.proxy_index + 1) % len(self.proxy_config.rotation_list)
            return proxy
        return None
    
    def _setup_session(self):
        """Configure la session requests"""
        self.session = requests.Session()
        
        # Configuration des retries
        retries = Retry(total=2, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Configuration du proxy
        proxies = {}
        if self.proxy_config.http:
            proxies['http'] = self.proxy_config.http
        if self.proxy_config.https:
            proxies['https'] = self.proxy_config.https
        if self.proxy_config.socks:
            proxies['socks'] = self.proxy_config.socks
        
        if proxies:
            self.session.proxies.update(proxies)
    
    def _setup_stealth_session(self):
        """Configure la session pour le mode furtif"""
        self._setup_session()
        
        # User-Agent aléatoire
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        self.session.headers.update({'User-Agent': random.choice(user_agents)})
        
        # Headers supplémentaires en mode furtif
        if self.stealth_mode:
            self.session.headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
    
    def _apply_stealth_delay(self):
        """Applique un délai furtif"""
        if self.stealth_mode:
            delay = random.uniform(0.5, 2.0)
            time.sleep(delay)
    
    @staticmethod
    def get_local_ip() -> str:
        """Récupère l'adresse IP locale"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    @staticmethod
    def get_public_ip() -> Optional[str]:
        """Récupère l'adresse IP publique"""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
        except:
            try:
                response = requests.get('https://icanhazip.com', timeout=5)
                return response.text.strip()
            except:
                return None
    
    def get_public_ip_stealth(self) -> Optional[str]:
        """Récupère l'IP publique en mode furtif (via proxy)"""
        if self.proxy_config.rotation_list:
            proxy = self._get_next_proxy()
            if proxy:
                try:
                    response = requests.get('https://api.ipify.org', proxies={'http': proxy, 'https': proxy}, timeout=10)
                    return response.text.strip()
                except:
                    pass
        return self.get_public_ip()
    
    @staticmethod
    def is_port_open(host: str, port: int, timeout: float = 3) -> bool:
        """
        Vérifie si un port est ouvert
        
        Args:
            host: Hôte cible
            port: Port à vérifier
            timeout: Timeout en secondes
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    @staticmethod
    def scan_ports(host: str, ports: List[int], timeout: float = 3, threads: int = 10) -> List[int]:
        """
        Scanne une liste de ports avec multi-threading
        
        Args:
            host: Hôte cible
            ports: Liste des ports à scanner
            timeout: Timeout par port
            threads: Nombre de threads
        """
        open_ports = []
        
        def scan_port(port):
            if NetworkUtils.is_port_open(host, port, timeout):
                return port
            return None
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(scan_port, port): port for port in ports}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    open_ports.append(result)
        
        return sorted(open_ports)
    
    @staticmethod
    def resolve_hostname(hostname: str) -> List[str]:
        """
        Résout un nom d'hôte en adresses IP
        
        Args:
            hostname: Nom d'hôte à résoudre
        """
        try:
            return list(set([addr[4][0] for addr in socket.getaddrinfo(hostname, 80)]))
        except:
            return []
    
    @staticmethod
    def reverse_dns(ip: str) -> Optional[str]:
        """
        Résolution DNS inverse
        
        Args:
            ip: Adresse IP
        """
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return None
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """
        Vérifie si une chaîne est une adresse IP valide
        
        Args:
            ip: Chaîne à vérifier
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except:
            return False
    
    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """
        Vérifie si une chaîne est un domaine valide
        
        Args:
            domain: Chaîne à vérifier
        """
        import re
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return re.match(pattern, domain) is not None
    
    @staticmethod
    def get_network_range(ip: str, cidr: int = 24) -> str:
        """
        Obtient la plage réseau
        
        Args:
            ip: Adresse IP
            cidr: Masque CIDR
        """
        network = ipaddress.ip_network(f"{ip}/{cidr}", strict=False)
        return str(network)
    
    @staticmethod
    def get_all_ips_in_range(network: str) -> List[str]:
        """
        Liste toutes les IPs d'une plage réseau
        
        Args:
            network: Plage réseau (ex: 192.168.1.0/24)
        """
        try:
            return [str(ip) for ip in ipaddress.IPv4Network(network, strict=False)]
        except:
            return []
    
    @staticmethod
    def ping(host: str, count: int = 1, timeout: float = 3) -> bool:
        """
        Ping un hôte
        
        Args:
            host: Hôte cible
            count: Nombre de paquets
            timeout: Timeout
        """
        import platform
        
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        cmd = ['ping', param, str(count), '-W', str(int(timeout)), host]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout + 2)
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def ping_stealth(host: str, count: int = 1) -> bool:
        """
        Ping discret (ICMP avec délai aléatoire)
        
        Args:
            host: Hôte cible
            count: Nombre de paquets
        """
        import platform
        
        # Délai aléatoire pour éviter la détection
        time.sleep(random.uniform(0.1, 0.5))
        
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        cmd = ['ping', param, str(count), '-W', '2', host]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def traceroute(host: str, max_hops: int = 30) -> List[str]:
        """
        Trace la route vers un hôte
        
        Args:
            host: Hôte cible
            max_hops: Nombre maximal de sauts
        """
        import platform
        
        cmd = ['traceroute', '-m', str(max_hops), host]
        if platform.system().lower() == 'windows':
            cmd = ['tracert', '-h', str(max_hops), host]
        
        hops = []
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('traceroute'):
                    hops.append(line.strip())
        except:
            pass
        
        return hops
    
    def get_http_headers(self, url: str) -> Dict[str, str]:
        """
        Récupère les headers HTTP d'une URL
        
        Args:
            url: URL cible
        """
        try:
            self._apply_stealth_delay()
            response = self.session.head(url, timeout=10, verify=False)
            return dict(response.headers)
        except:
            return {}
    
    def get_http_headers_stealth(self, url: str) -> Dict[str, str]:
        """
        Récupère les headers HTTP en mode furtif
        
        Args:
            url: URL cible
        """
        if self.proxy_config.rotation_list:
            proxy = self._get_next_proxy()
            if proxy:
                try:
                    time.sleep(random.uniform(0.5, 1.5))
                    response = requests.head(url, proxies={'http': proxy, 'https': proxy}, timeout=15, verify=False)
                    return dict(response.headers)
                except:
                    pass
        return self.get_http_headers(url)
    
    @staticmethod
    def get_ssl_info(hostname: str, port: int = 443) -> Dict[str, Any]:
        """
        Récupère les informations SSL/TLS
        
        Args:
            hostname: Nom d'hôte
            port: Port SSL
        """
        import ssl
        from datetime import datetime
        
        info = {
            'valid': False,
            'issuer': None,
            'subject': None,
            'expiry': None,
            'protocol': None,
            'cipher': None,
            'san': []
        }
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    info['valid'] = True
                    info['protocol'] = ssock.version()
                    info['cipher'] = ssock.cipher()[0]
                    
                    for key in ['issuer', 'subject']:
                        if key in cert:
                            info[key] = dict(x[0] for x in cert[key])
                    
                    if 'notAfter' in cert:
                        info['expiry'] = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    
                    if 'subjectAltName' in cert:
                        info['san'] = [san[1] for san in cert['subjectAltName'] if san[0] == 'DNS']
                        
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    @staticmethod
    def get_asn_info(ip: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations ASN d'une IP
        
        Args:
            ip: Adresse IP
        """
        try:
            response = requests.get(f'https://ipinfo.io/{ip}/json', timeout=10)
            data = response.json()
            
            if 'org' in data:
                return {
                    'asn': data.get('org', '').split(' ')[0],
                    'organization': data.get('org', ''),
                    'country': data.get('country', ''),
                    'city': data.get('city', ''),
                    'loc': data.get('loc', '')
                }
        except:
            pass
        
        return None
    
    @staticmethod
    def get_geolocation(ip: str) -> Optional[Dict[str, Any]]:
        """
        Récupère la géolocalisation d'une IP
        
        Args:
            ip: Adresse IP
        """
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=10)
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'country': data.get('country'),
                    'country_code': data.get('countryCode'),
                    'region': data.get('region'),
                    'city': data.get('city'),
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'isp': data.get('isp'),
                    'org': data.get('org'),
                    'as': data.get('as')
                }
        except:
            pass
        
        return None
    
    def get_route_info(self, target: str) -> Dict[str, Any]:
        """
        Récupère les informations de route vers une cible
        
        Args:
            target: Hôte cible
        """
        info = {
            'target': target,
            'ip': None,
            'hops': [],
            'response_time': None
        }
        
        # Résolution DNS
        ips = self.resolve_hostname(target)
        if ips:
            info['ip'] = ips[0]
        
        # Traceroute
        info['hops'] = self.traceroute(target)
        
        # Ping
        start = time.time()
        reachable = self.ping(target)
        info['response_time'] = time.time() - start if reachable else None
        info['reachable'] = reachable
        
        return info
    
    def tcp_connect(self, host: str, port: int, timeout: float = 5) -> Optional[socket.socket]:
        """
        Établit une connexion TCP
        
        Args:
            host: Hôte cible
            port: Port
            timeout: Timeout
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            return sock
        except:
            return None
    
    def send_raw_packet(self, host: str, port: int, data: bytes, timeout: float = 5) -> Optional[bytes]:
        """
        Envoie un paquet raw TCP
        
        Args:
            host: Hôte cible
            port: Port
            data: Données à envoyer
            timeout: Timeout
        """
        sock = self.tcp_connect(host, port, timeout)
        if sock:
            try:
                sock.send(data)
                response = sock.recv(4096)
                sock.close()
                return response
            except:
                sock.close()
        return None


# Instance globale
network = NetworkUtils()


if __name__ == "__main__":
    print("=" * 60)
    print("Test des utilitaires réseau")
    print("=" * 60)
    
    print(f"IP locale: {network.get_local_ip()}")
    print(f"IP publique: {network.get_public_ip()}")
    print(f"Port 80 ouvert sur google.com: {network.is_port_open('google.com', 80)}")
    print(f"Résolution example.com: {network.resolve_hostname('example.com')}")
    
    # Test mode furtif
    print("\n🕵️ Mode furtif activé")
    network.set_stealth_mode(True)
    print(f"IP publique (furtif): {network.get_public_ip_stealth()}")
    
    # Scan de ports
    print("\n🔍 Scan de ports (80, 443, 8080) sur google.com")
    open_ports = network.scan_ports('google.com', [80, 443, 8080])
    print(f"Ports ouverts: {open_ports}")
    
    # Route info
    print("\n🌐 Route vers google.com")
    route = network.get_route_info('google.com')
    print(f"IP: {route['ip']}")
    print(f"Atteignable: {route['reachable']}")
    print(f"Temps réponse: {route['response_time']:.3f}s" if route['response_time'] else "N/A")
    
    # Géolocalisation
    geo = network.get_geolocation('8.8.8.8')
    if geo:
        print(f"\n📍 Géolocalisation 8.8.8.8: {geo['city']}, {geo['country']} ({geo['isp']})")
    
    print("\n✅ Tests terminés")