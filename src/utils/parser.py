#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de parsing pour RedForge
Parsing de différents formats de données avec support avancé
Version avec support APT, mode furtif et parsing intelligent
"""

import re
import json
import csv
import base64
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple, Union
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
from collections import defaultdict
import hashlib

class ParserUtils:
    """Utilitaires de parsing avancés"""
    
    def __init__(self):
        self.stealth_mode = False
        self.apt_mode = False
    
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif"""
        self.stealth_mode = enabled
    
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT"""
        self.apt_mode = enabled
    
    @staticmethod
    def parse_nmap_output(xml_content: str) -> Dict[str, Any]:
        """
        Parse la sortie XML de Nmap
        
        Args:
            xml_content: Contenu XML de Nmap
        """
        result = {
            'hosts': [],
            'open_ports': [],
            'services': [],
            'os': None,
            'scan_info': {}
        }
        
        try:
            root = ET.fromstring(xml_content)
            
            # Scan info
            scan_info = root.find('scaninfo')
            if scan_info is not None:
                result['scan_info'] = {
                    'type': scan_info.get('type'),
                    'protocol': scan_info.get('protocol'),
                    'services': scan_info.get('services')
                }
            
            for host in root.findall('host'):
                host_info = {
                    'ip': None,
                    'hostname': None,
                    'status': None,
                    'ports': []
                }
                
                # Adresse IP
                addr = host.find('address')
                if addr is not None:
                    host_info['ip'] = addr.get('addr')
                    host_info['addr_type'] = addr.get('addrtype')
                
                # Hostname
                hostnames = host.find('hostnames')
                if hostnames is not None:
                    hostname_elem = hostnames.find('hostname')
                    if hostname_elem is not None:
                        host_info['hostname'] = hostname_elem.get('name')
                        host_info['hostname_type'] = hostname_elem.get('type')
                
                # Statut
                status = host.find('status')
                if status is not None:
                    host_info['status'] = status.get('state')
                    host_info['reason'] = status.get('reason')
                
                # Ports
                ports = host.find('ports')
                if ports is not None:
                    for port in ports.findall('port'):
                        port_id = port.get('portid')
                        protocol = port.get('protocol')
                        state_elem = port.find('state')
                        service_elem = port.find('service')
                        
                        if state_elem is not None and state_elem.get('state') == 'open':
                            port_info = {
                                'port': int(port_id),
                                'protocol': protocol,
                                'state': 'open',
                                'reason': state_elem.get('reason')
                            }
                            
                            if service_elem is not None:
                                port_info['service'] = service_elem.get('name', 'unknown')
                                port_info['product'] = service_elem.get('product', '')
                                port_info['version'] = service_elem.get('version', '')
                                port_info['extra_info'] = service_elem.get('extrainfo', '')
                                port_info['service_tunnel'] = service_elem.get('tunnel', '')
                            
                            host_info['ports'].append(port_info)
                            result['open_ports'].append(int(port_id))
                            result['services'].append(port_info)
                
                result['hosts'].append(host_info)
            
            # OS détection
            os = root.find('.//os/osmatch')
            if os is not None:
                result['os'] = {
                    'name': os.get('name'),
                    'accuracy': int(os.get('accuracy', 0)),
                    'line': os.get('line')
                }
                
                # Détails OS
                osclass = os.find('osclass')
                if osclass is not None:
                    result['os']['family'] = osclass.get('osfamily')
                    result['os']['generation'] = osclass.get('osgen')
                    result['os']['vendor'] = osclass.get('vendor')
                    result['os']['type'] = osclass.get('type')
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    @staticmethod
    def parse_sqlmap_output(output: str) -> Dict[str, Any]:
        """
        Parse la sortie de SQLMap
        
        Args:
            output: Sortie texte de SQLMap
        """
        result = {
            'vulnerable': False,
            'database': None,
            'tables': [],
            'data': [],
            'technique': None,
            'payload': None
        }
        
        # Détection de vulnérabilité
        if 'vulnerable' in output.lower():
            result['vulnerable'] = True
            
            # Extraction base de données
            db_match = re.search(r'back-end DBMS:\s+(\w+)', output, re.IGNORECASE)
            if db_match:
                result['database'] = db_match.group(1)
            
            # Technique utilisée
            tech_match = re.search(r'Technique:\s+(\w+)', output)
            if tech_match:
                result['technique'] = tech_match.group(1)
            
            # Payload
            payload_match = re.search(r'Payload:\s+(.+?)(?:\n|$)', output)
            if payload_match:
                result['payload'] = payload_match.group(1).strip()
            
            # Extraction des tables
            table_pattern = r'\[\*\] (\w+) \('
            tables = re.findall(table_pattern, output)
            result['tables'] = tables
        
        return result
    
    @staticmethod
    def parse_url_params(url: str) -> Dict[str, List[str]]:
        """
        Parse les paramètres d'une URL
        
        Args:
            url: URL à parser
        """
        parsed = urlparse(url)
        return parse_qs(parsed.query)
    
    @staticmethod
    def extract_links(html: str, base_url: str = "") -> List[str]:
        """
        Extrait tous les liens d'une page HTML
        
        Args:
            html: Contenu HTML
            base_url: URL de base pour les liens relatifs
        """
        from urllib.parse import urljoin
        
        links = []
        patterns = [
            r'href=["\']([^"\']+)["\']',
            r'src=["\']([^"\']+)["\']',
            r'action=["\']([^"\']+)["\']',
            r'data-url=["\']([^"\']+)["\']',
            r'data-href=["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if base_url and not match.startswith(('http://', 'https://', '//', 'mailto:', 'tel:', '#')):
                    match = urljoin(base_url, match)
                if match and match not in links:
                    links.append(match)
        
        return links
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        Extrait les adresses email d'un texte
        
        Args:
            text: Texte à analyser
        """
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return list(set(re.findall(pattern, text)))
    
    @staticmethod
    def extract_ips(text: str) -> List[str]:
        """
        Extrait les adresses IP d'un texte
        
        Args:
            text: Texte à analyser
        """
        pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        return list(set(re.findall(pattern, text)))
    
    @staticmethod
    def extract_domains(text: str) -> List[str]:
        """
        Extrait les noms de domaine d'un texte
        
        Args:
            text: Texte à analyser
        """
        pattern = r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}'
        return list(set(re.findall(pattern, text)))
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        Extrait les URLs d'un texte
        
        Args:
            text: Texte à analyser
        """
        pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[-\w%!?=:@.+~#&//]*)??'
        return list(set(re.findall(pattern, text)))
    
    @staticmethod
    def extract_hashes(text: str) -> Dict[str, List[str]]:
        """
        Extrait les hashs d'un texte avec détection du type
        
        Args:
            text: Texte à analyser
        """
        hashes = {
            'md5': [],
            'sha1': [],
            'sha256': [],
            'sha512': [],
            'ntlm': []
        }
        
        patterns = {
            'md5': r'\b[a-fA-F0-9]{32}\b',
            'sha1': r'\b[a-fA-F0-9]{40}\b',
            'sha256': r'\b[a-fA-F0-9]{64}\b',
            'sha512': r'\b[a-fA-F0-9]{128}\b',
            'ntlm': r'\b[a-fA-F0-9]{32}\b'  # NTLM aussi 32 chars
        }
        
        for hash_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                hashes[hash_type] = list(set(matches))
        
        return hashes
    
    @staticmethod
    def parse_json_response(response: str) -> Optional[Dict]:
        """
        Parse une réponse JSON
        
        Args:
            response: Chaîne JSON
        """
        try:
            return json.loads(response)
        except:
            return None
    
    @staticmethod
    def parse_cookies(cookie_string: str) -> Dict[str, str]:
        """
        Parse une chaîne de cookies
        
        Args:
            cookie_string: Chaîne de cookies (ex: "name=value; name2=value2")
        """
        cookies = {}
        
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                name, value = item.split('=', 1)
                cookies[name] = value
        
        return cookies
    
    @staticmethod
    def parse_headers(header_string: str) -> Dict[str, str]:
        """
        Parse des headers HTTP
        
        Args:
            header_string: Chaîne de headers
        """
        headers = {}
        
        for line in header_string.strip().split('\n'):
            line = line.strip()
            if ': ' in line:
                name, value = line.split(': ', 1)
                headers[name] = value
        
        return headers
    
    @staticmethod
    def parse_command_output(output: str, separator: str = "=") -> Dict[str, str]:
        """
        Parse une sortie de commande clé=valeur
        
        Args:
            output: Sortie de commande
            separator: Séparateur clé-valeur
        """
        result = {}
        
        for line in output.split('\n'):
            line = line.strip()
            if separator in line:
                key, value = line.split(separator, 1)
                result[key.strip()] = value.strip()
        
        return result
    
    @staticmethod
    def parse_robots_txt(content: str) -> Dict[str, List[str]]:
        """
        Parse un fichier robots.txt
        
        Args:
            content: Contenu du robots.txt
        """
        result = {
            'allow': [],
            'disallow': [],
            'sitemap': [],
            'user_agents': []
        }
        
        current_user_agent = None
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            line_lower = line.lower()
            
            if line_lower.startswith('user-agent:'):
                current_user_agent = line[11:].strip()
                result['user_agents'].append(current_user_agent)
            elif line_lower.startswith('disallow:'):
                path = line[9:].strip()
                if path:
                    result['disallow'].append(path)
            elif line_lower.startswith('allow:'):
                path = line[6:].strip()
                if path:
                    result['allow'].append(path)
            elif line_lower.startswith('sitemap:'):
                sitemap = line[8:].strip()
                if sitemap:
                    result['sitemap'].append(sitemap)
        
        return result
    
    @staticmethod
    def parse_sitemap(content: str) -> List[Dict[str, Any]]:
        """
        Parse un fichier sitemap.xml
        
        Args:
            content: Contenu du sitemap
        """
        urls = []
        
        try:
            root = ET.fromstring(content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            for url_elem in root.findall('.//ns:url', namespaces=namespace):
                url_info = {'loc': None, 'lastmod': None, 'changefreq': None, 'priority': None}
                
                loc = url_elem.find('ns:loc', namespaces=namespace)
                if loc is not None and loc.text:
                    url_info['loc'] = loc.text
                
                lastmod = url_elem.find('ns:lastmod', namespaces=namespace)
                if lastmod is not None and lastmod.text:
                    url_info['lastmod'] = lastmod.text
                
                changefreq = url_elem.find('ns:changefreq', namespaces=namespace)
                if changefreq is not None and changefreq.text:
                    url_info['changefreq'] = changefreq.text
                
                priority = url_elem.find('ns:priority', namespaces=namespace)
                if priority is not None and priority.text:
                    url_info['priority'] = float(priority.text)
                
                urls.append(url_info)
        except:
            pass
        
        return urls
    
    @staticmethod
    def parse_csv(content: str, delimiter: str = ',') -> List[Dict[str, str]]:
        """
        Parse un fichier CSV
        
        Args:
            content: Contenu CSV
            delimiter: Délimiteur
        """
        rows = []
        
        try:
            reader = csv.DictReader(content.splitlines(), delimiter=delimiter)
            for row in reader:
                rows.append(row)
        except:
            pass
        
        return rows
    
    @staticmethod
    def parse_base64(content: str) -> Optional[str]:
        """
        Décode une chaîne base64
        
        Args:
            content: Chaîne base64
        """
        try:
            decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
            return decoded
        except:
            return None
    
    @staticmethod
    def parse_hex(content: str) -> Optional[str]:
        """
        Décode une chaîne hexadécimale
        
        Args:
            content: Chaîne hexadécimale
        """
        try:
            decoded = bytes.fromhex(content).decode('utf-8', errors='ignore')
            return decoded
        except:
            return None
    
    @staticmethod
    def parse_url_encoded(content: str) -> str:
        """
        Décode une chaîne encodée URL
        
        Args:
            content: Chaîne encodée URL
        """
        return unquote(content)
    
    @staticmethod
    def extract_jwt(token: str) -> Dict[str, Any]:
        """
        Parse un token JWT
        
        Args:
            token: Token JWT
        """
        result = {
            'valid': False,
            'header': None,
            'payload': None,
            'signature': None,
            'algorithm': None
        }
        
        parts = token.split('.')
        if len(parts) == 3:
            try:
                # Header
                header_json = base64.b64decode(parts[0] + '==').decode('utf-8')
                result['header'] = json.loads(header_json)
                result['algorithm'] = result['header'].get('alg')
                
                # Payload
                payload_json = base64.b64decode(parts[1] + '==').decode('utf-8')
                result['payload'] = json.loads(payload_json)
                
                # Signature
                result['signature'] = parts[2][:20] + '...'
                result['valid'] = True
                
            except:
                pass
        
        return result
    
    @staticmethod
    def extract_credentials(text: str) -> List[Dict[str, str]]:
        """
        Extrait des credentials (username:password) d'un texte
        
        Args:
            text: Texte à analyser
        """
        credentials = []
        
        # Pattern username:password
        pattern = r'([a-zA-Z0-9_\-\.]+):([a-zA-Z0-9_\-\.!@#$%^&*()]+)'
        matches = re.findall(pattern, text)
        
        for username, password in matches:
            credentials.append({
                'username': username,
                'password': password
            })
        
        return credentials
    
    @staticmethod
    def parse_apache_log(log_line: str) -> Dict[str, Any]:
        """
        Parse une ligne de log Apache
        
        Args:
            log_line: Ligne de log Apache
        """
        # Pattern Apache common log format
        pattern = r'(\S+) (\S+) (\S+) \[([^:]+):(\d+:\d+:\d+) ([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\d+)'
        match = re.match(pattern, log_line)
        
        if match:
            return {
                'ip': match.group(1),
                'ident': match.group(2),
                'user': match.group(3),
                'date': match.group(4),
                'time': match.group(5),
                'timezone': match.group(6),
                'method': match.group(7),
                'path': match.group(8),
                'protocol': match.group(9),
                'status': int(match.group(10)),
                'size': int(match.group(11)) if match.group(11) != '-' else 0
            }
        
        return {}
    
    @staticmethod
    def get_file_type(data: bytes) -> str:
        """
        Détermine le type d'un fichier à partir de ses bytes
        
        Args:
            data: Données du fichier
        """
        # Signatures de fichiers
        signatures = {
            b'\x89PNG\r\n\x1a\n': 'png',
            b'%PDF': 'pdf',
            b'GIF87a': 'gif',
            b'GIF89a': 'gif',
            b'\xff\xd8\xff': 'jpg',
            b'PK\x03\x04': 'zip',
            b'<?xml': 'xml',
            b'<html': 'html',
            b'<!DOCTYPE html': 'html'
        }
        
        for sig, file_type in signatures.items():
            if data.startswith(sig):
                return file_type
        
        return 'unknown'


# Instance globale
parser = ParserUtils()


if __name__ == "__main__":
    print("=" * 60)
    print("Test des utilitaires de parsing")
    print("=" * 60)
    
    # Test parsing URL
    params = parser.parse_url_params("https://example.com/page?id=1&name=test")
    print(f"Paramètres URL: {params}")
    
    # Test extraction
    text = "Contact: admin@example.com, 192.168.1.1, https://example.com, hash: 5d41402abc4b2a76b9719d911017c592"
    print(f"Emails: {parser.extract_emails(text)}")
    print(f"IPs: {parser.extract_ips(text)}")
    print(f"Domaines: {parser.extract_domains(text)}")
    print(f"URLs: {parser.extract_urls(text)}")
    print(f"Hashs: {parser.extract_hashes(text)}")
    
    # Test JWT
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    jwt_parsed = parser.extract_jwt(jwt)
    print(f"JWT: {jwt_parsed['algorithm']} - {jwt_parsed['payload']}")
    
    print("\n✅ Tests terminés")