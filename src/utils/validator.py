#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de validation pour RedForge
Validation des entrées, URLs, IPs, domaines, etc.
Version avec support furtif, APT et validation avancée
"""

import re
import ipaddress
import socket
from typing import Union, Optional, List, Tuple, Dict, Any
from urllib.parse import urlparse, urljoin
from datetime import datetime
import hashlib


class Validator:
    """Utilitaires de validation avancée"""
    
    def __init__(self):
        self.stealth_mode = False
        self.apt_mode = False
    
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif"""
        self.stealth_mode = enabled
    
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT"""
        self.apt_mode = enabled
    
    # ========================================
    # Validation d'URL
    # ========================================
    
    @staticmethod
    def is_valid_url(url: str, require_http: bool = True) -> bool:
        """
        Vérifie si une chaîne est une URL valide
        
        Args:
            url: Chaîne à vérifier
            require_http: Exige le protocole http:// ou https://
        """
        if not url:
            return False
        
        if require_http and not url.startswith(('http://', 'https://')):
            return False
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False
            
            # Vérifier le format général
            pattern = r'^https?://[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?$'
            return re.match(pattern, url, re.IGNORECASE) is not None
        except:
            return False
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """
        Vérifie si une chaîne est une adresse IP valide (IPv4 ou IPv6)
        
        Args:
            ip: Chaîne à vérifier
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_ipv4(ip: str) -> bool:
        """
        Vérifie si une chaîne est une adresse IPv4 valide
        
        Args:
            ip: Chaîne à vérifier
        """
        try:
            ipaddress.IPv4Address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_ipv6(ip: str) -> bool:
        """
        Vérifie si une chaîne est une adresse IPv6 valide
        
        Args:
            ip: Chaîne à vérifier
        """
        try:
            ipaddress.IPv6Address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_cidr(cidr: str) -> bool:
        """
        Vérifie si une chaîne est un CIDR valide
        
        Args:
            cidr: Chaîne à vérifier (ex: 192.168.1.0/24)
        """
        try:
            ipaddress.ip_network(cidr, strict=False)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """
        Vérifie si une chaîne est un nom de domaine valide
        
        Args:
            domain: Chaîne à vérifier
        """
        if not domain or len(domain) > 253:
            return False
        
        # Pattern RFC 1035
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return re.match(pattern, domain) is not None
    
    @staticmethod
    def is_valid_hostname(hostname: str) -> bool:
        """
        Vérifie si une chaîne est un hostname valide
        
        Args:
            hostname: Chaîne à vérifier
        """
        if len(hostname) > 255:
            return False
        
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        return re.match(pattern, hostname) is not None
    
    # ========================================
    # Validation de ports
    # ========================================
    
    @staticmethod
    def is_valid_port(port: int) -> bool:
        """
        Vérifie si un numéro de port est valide
        
        Args:
            port: Numéro de port
        """
        return 1 <= port <= 65535
    
    @staticmethod
    def is_valid_port_range(port_range: str) -> bool:
        """
        Vérifie si une chaîne de ports est valide (ex: 80,443 ou 1-1000)
        
        Args:
            port_range: Chaîne à vérifier
        """
        if not port_range:
            return False
        
        parts = port_range.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                try:
                    start_port = int(start)
                    end_port = int(end)
                    if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535 and start_port <= end_port):
                        return False
                except ValueError:
                    return False
            else:
                try:
                    port = int(part)
                    if not (1 <= port <= 65535):
                        return False
                except ValueError:
                    return False
        return True
    
    # ========================================
    # Validation de fichiers et chemins
    # ========================================
    
    @staticmethod
    def is_valid_path(path: str) -> bool:
        """
        Vérifie si un chemin est valide
        
        Args:
            path: Chemin à vérifier
        """
        import os
        try:
            # Vérifier les caractères interdits
            forbidden = ['\\', ':', '*', '?', '"', '<', '>', '|']
            for char in forbidden:
                if char in path:
                    return False
            return True
        except:
            return False
    
    @staticmethod
    def is_safe_path(path: str, base_dir: str = None) -> bool:
        """
        Vérifie si un chemin est sûr (pas de path traversal)
        
        Args:
            path: Chemin à vérifier
            base_dir: Répertoire de base (optionnel)
        """
        import os
        from pathlib import Path
        
        try:
            if base_dir:
                base_path = Path(base_dir).resolve()
                target_path = (base_path / path).resolve()
                return str(target_path).startswith(str(base_path))
            else:
                # Vérifier les patterns dangereux
                dangerous = ['..', './', '.\\', '~', '%2e%2e']
                return not any(d in path.lower() for d in dangerous)
        except:
            return False
    
    @staticmethod
    def is_valid_filename(filename: str) -> bool:
        """
        Vérifie si un nom de fichier est valide
        
        Args:
            filename: Nom de fichier à vérifier
        """
        if not filename or len(filename) > 255:
            return False
        
        # Caractères interdits dans les noms de fichiers
        forbidden = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return not any(c in filename for c in forbidden)
    
    @staticmethod
    def is_valid_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """
        Vérifie si l'extension d'un fichier est autorisée
        
        Args:
            filename: Nom de fichier
            allowed_extensions: Liste des extensions autorisées
        """
        import os
        ext = os.path.splitext(filename)[1].lower()
        return ext in allowed_extensions
    
    # ========================================
    # Validation d'emails
    # ========================================
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Vérifie si une chaîne est une adresse email valide
        
        Args:
            email: Chaîne à vérifier
        """
        if not email:
            return False
        
        # Pattern RFC 5322 simplifié
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    # ========================================
    # Validation de hashs
    # ========================================
    
    @staticmethod
    def is_valid_md5(hash_string: str) -> bool:
        """Vérifie si une chaîne est un hash MD5 valide"""
        return bool(re.match(r'^[a-fA-F0-9]{32}$', hash_string))
    
    @staticmethod
    def is_valid_sha1(hash_string: str) -> bool:
        """Vérifie si une chaîne est un hash SHA1 valide"""
        return bool(re.match(r'^[a-fA-F0-9]{40}$', hash_string))
    
    @staticmethod
    def is_valid_sha256(hash_string: str) -> bool:
        """Vérifie si une chaîne est un hash SHA256 valide"""
        return bool(re.match(r'^[a-fA-F0-9]{64}$', hash_string))
    
    @staticmethod
    def is_valid_sha512(hash_string: str) -> bool:
        """Vérifie si une chaîne est un hash SHA512 valide"""
        return bool(re.match(r'^[a-fA-F0-9]{128}$', hash_string))
    
    @staticmethod
    def detect_hash_type(hash_string: str) -> Optional[str]:
        """
        Détecte le type de hash
        
        Args:
            hash_string: Hash à analyser
        """
        hash_string = hash_string.strip()
        length = len(hash_string)
        
        if length == 32 and re.match(r'^[a-fA-F0-9]{32}$', hash_string):
            return 'md5'
        elif length == 40 and re.match(r'^[a-fA-F0-9]{40}$', hash_string):
            return 'sha1'
        elif length == 64 and re.match(r'^[a-fA-F0-9]{64}$', hash_string):
            return 'sha256'
        elif length == 128 and re.match(r'^[a-fA-F0-9]{128}$', hash_string):
            return 'sha512'
        elif length == 32:  # NTLM
            return 'ntlm'
        elif length == 16:  # MySQL
            return 'mysql'
        
        return None
    
    # ========================================
    # Validation de dates
    # ========================================
    
    @staticmethod
    def is_valid_date(date_string: str, format: str = "%Y-%m-%d") -> bool:
        """
        Vérifie si une chaîne est une date valide
        
        Args:
            date_string: Chaîne à vérifier
            format: Format de la date
        """
        try:
            datetime.strptime(date_string, format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_datetime(datetime_string: str) -> bool:
        """
        Vérifie si une chaîne est une datetime ISO valide
        
        Args:
            datetime_string: Chaîne à vérifier
        """
        try:
            datetime.fromisoformat(datetime_string)
            return True
        except ValueError:
            return False
    
    # ========================================
    # Validation de nombres
    # ========================================
    
    @staticmethod
    def is_valid_integer(value: str) -> bool:
        """Vérifie si une chaîne est un entier valide"""
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_float(value: str) -> bool:
        """Vérifie si une chaîne est un float valide"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_hex(value: str) -> bool:
        """Vérifie si une chaîne est une valeur hexadécimale valide"""
        try:
            int(value, 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_base64(value: str) -> bool:
        """Vérifie si une chaîne est du base64 valide"""
        import base64
        try:
            base64.b64decode(value)
            return True
        except:
            return False
    
    # ========================================
    # Validation de données
    # ========================================
    
    @staticmethod
    def is_valid_json(value: str) -> bool:
        """Vérifie si une chaîne est du JSON valide"""
        import json
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False
    
    @staticmethod
    def is_valid_xml(value: str) -> bool:
        """Vérifie si une chaîne est du XML valide"""
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(value)
            return True
        except:
            return False
    
    @staticmethod
    def is_valid_html(value: str) -> bool:
        """Vérifie si une chaîne est du HTML valide"""
        # Vérification simple de la présence de balises
        return bool(re.search(r'<[^>]+>', value))
    
    # ========================================
    # Validation de sécurité
    # ========================================
    
    @staticmethod
    def is_safe_sql(value: str) -> bool:
        """
        Vérifie si une chaîne est potentiellement sûre pour SQL
        (détection basique d'injection SQL)
        """
        dangerous = [
            '--', ';', '/*', '*/', '@@', 'xp_', 'sp_',
            ' UNION ', ' SELECT ', ' INSERT ', ' UPDATE ',
            ' DELETE ', ' DROP ', ' CREATE ', ' ALTER '
        ]
        value_upper = value.upper()
        return not any(d.upper() in value_upper for d in dangerous)
    
    @staticmethod
    def is_safe_xss(value: str) -> bool:
        """
        Vérifie si une chaîne est potentiellement sûre pour XSS
        (détection basique de scripts)
        """
        dangerous = [
            '<script', '</script>', 'javascript:', 'onerror=', 'onload=',
            'onclick=', 'onmouseover=', 'alert(', 'prompt(', 'confirm('
        ]
        value_lower = value.lower()
        return not any(d in value_lower for d in dangerous)
    
    @staticmethod
    def is_safe_path_traversal(value: str) -> bool:
        """
        Vérifie si une chaîne contient des tentatives de path traversal
        """
        dangerous = ['../', '..\\', '%2e%2e%2f', '%2e%2e%5c', '..;/']
        value_lower = value.lower()
        return not any(d in value_lower for d in dangerous)
    
    # ========================================
    # Validation de certificats
    # ========================================
    
    @staticmethod
    def is_valid_ssl_cert(hostname: str, port: int = 443) -> bool:
        """
        Vérifie si un certificat SSL est valide
        
        Args:
            hostname: Nom d'hôte
            port: Port SSL
        """
        import ssl
        import socket
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    return cert is not None
        except:
            return False
    
    # ========================================
    # Validation de résolution DNS
    # ========================================
    
    @staticmethod
    def resolves(hostname: str) -> bool:
        """
        Vérifie si un nom d'hôte résout en IP
        
        Args:
            hostname: Nom d'hôte à vérifier
        """
        try:
            socket.gethostbyname(hostname)
            return True
        except socket.gaierror:
            return False
    
    # ========================================
    # Validation de plages
    # ========================================
    
    @staticmethod
    def is_in_range(value: Union[int, float], min_val: Union[int, float], 
                    max_val: Union[int, float]) -> bool:
        """
        Vérifie si une valeur est dans une plage
        
        Args:
            value: Valeur à vérifier
            min_val: Valeur minimale
            max_val: Valeur maximale
        """
        return min_val <= value <= max_val
    
    @staticmethod
    def is_in_list(value: str, allowed_list: List[str]) -> bool:
        """
        Vérifie si une valeur est dans une liste autorisée
        
        Args:
            value: Valeur à vérifier
            allowed_list: Liste des valeurs autorisées
        """
        return value in allowed_list
    
    # ========================================
    # Validation complète d'URL
    # ========================================
    
    @staticmethod
    def validate_url_full(url: str) -> Dict[str, Any]:
        """
        Validation complète d'une URL
        
        Args:
            url: URL à valider
            
        Returns:
            Dictionnaire avec les résultats de validation
        """
        result = {
            'valid': False,
            'scheme': None,
            'hostname': None,
            'port': None,
            'path': None,
            'query': None,
            'fragment': None,
            'errors': []
        }
        
        if not url:
            result['errors'].append("URL vide")
            return result
        
        try:
            parsed = urlparse(url)
            
            # Vérifier le schéma
            if parsed.scheme not in ['http', 'https']:
                result['errors'].append(f"Schéma invalide: {parsed.scheme}")
            else:
                result['scheme'] = parsed.scheme
            
            # Vérifier le hostname
            if not parsed.hostname:
                result['errors'].append("Hostname manquant")
            elif not Validator.is_valid_hostname(parsed.hostname) and not Validator.is_valid_ip(parsed.hostname):
                result['errors'].append(f"Hostname invalide: {parsed.hostname}")
            else:
                result['hostname'] = parsed.hostname
            
            # Vérifier le port
            if parsed.port:
                if not Validator.is_valid_port(parsed.port):
                    result['errors'].append(f"Port invalide: {parsed.port}")
                else:
                    result['port'] = parsed.port
            
            result['path'] = parsed.path
            result['query'] = parsed.query
            result['fragment'] = parsed.fragment
            
            result['valid'] = len(result['errors']) == 0
            
        except Exception as e:
            result['errors'].append(str(e))
        
        return result


# Instance globale
validator = Validator()


if __name__ == "__main__":
    print("=" * 60)
    print("Test des utilitaires de validation")
    print("=" * 60)
    
    # Test URLs
    print("\n🔗 Validation d'URLs:")
    test_urls = [
        "https://example.com",
        "http://google.com",
        "ftp://example.com",
        "not a url",
        "example.com"
    ]
    for url in test_urls:
        print(f"  {url}: {Validator.is_valid_url(url)}")
    
    # Test IPs
    print("\n🌐 Validation d'IPs:")
    test_ips = [
        "192.168.1.1",
        "256.256.256.256",
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "invalid"
    ]
    for ip in test_ips:
        print(f"  {ip}: {Validator.is_valid_ip(ip)}")
    
    # Test domaines
    print("\n🏠 Validation de domaines:")
    test_domains = [
        "example.com",
        "sub.domain.co.uk",
        "-invalid.com",
        "invalid..com"
    ]
    for domain in test_domains:
        print(f"  {domain}: {Validator.is_valid_domain(domain)}")
    
    # Test hashs
    print("\n🔐 Validation de hashs:")
    test_hashes = [
        ("5d41402abc4b2a76b9719d911017c592", "md5"),
        ("aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d", "sha1"),
        ("9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", "sha256"),
        ("invalid", "unknown")
    ]
    for hash_str, expected in test_hashes:
        detected = Validator.detect_hash_type(hash_str)
        print(f"  {hash_str[:20]}... -> {detected} (attendu: {expected})")
    
    # Test sécurité
    print("\n🛡️ Validation de sécurité:")
    test_inputs = [
        ("1' OR '1'='1", "SQL"),
        ("<script>alert('XSS')</script>", "XSS"),
        ("../../../etc/passwd", "Path Traversal"),
        ("normal input", "Safe")
    ]
    for inp, test_type in test_inputs:
        sql_safe = Validator.is_safe_sql(inp)
        xss_safe = Validator.is_safe_xss(inp)
        path_safe = Validator.is_safe_path_traversal(inp)
        print(f"  {test_type}: '{inp[:30]}...'")
        print(f"    SQL safe: {sql_safe}, XSS safe: {xss_safe}, Path safe: {path_safe}")
    
    print("\n✅ Tests terminés")