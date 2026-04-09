#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de race condition pour RedForge
Détecte les vulnérabilités de race condition dans l'authentification
Version avec support furtif, APT et techniques avancées
"""

import time
import random
import threading
import requests
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import re
import json

@dataclass
class RaceConditionConfig:
    """Configuration avancée pour la détection de race conditions"""
    # Délais
    delay_between_tests: Tuple[float, float] = (1, 3)
    request_spacing: Tuple[float, float] = (0.001, 0.01)  # Très court pour race conditions
    
    # Comportement
    threads: int = 10
    request_count: int = 20
    burst_mode: bool = True  # Mode rafale pour déclencher les races
    test_all_endpoints: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = False  # Pas de délais pour les races
    
    # APT
    apt_mode: bool = False
    slow_burst: bool = False  # Rafales plus lentes pour éviter détection
    
    # Techniques spécifiques
    test_token_reuse: bool = True
    test_balance_bypass: bool = True
    test_voucher_abuse: bool = True
    test_lock_bypass: bool = True
    
    # Timing
    timing_precision: float = 0.001  # Précision en secondes
    measure_response_time: bool = True


class RaceCondition:
    """Détection avancée de race conditions dans l'authentification"""
    
    def __init__(self, config: Optional[RaceConditionConfig] = None):
        """
        Initialise la détection de race conditions
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or RaceConditionConfig()
        
        # Endpoints sensibles
        self.endpoints_sensitive = [
            '/register', '/signup', '/login', '/reset-password',
            '/change-password', '/update-email', '/transfer', '/withdraw',
            '/api/register', '/api/login', '/api/reset-password',
            '/api/change-password', '/api/transfer', '/api/withdraw',
            '/v1/register', '/v1/login', '/auth/register', '/auth/login',
            '/user/register', '/account/transfer', '/payment/withdraw'
        ]
        
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
        self.race_detected_count = 0
        
        # Cache
        self.tested_endpoints: Set[str] = set()
        self.generated_tokens: Set[str] = set()
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités de race condition
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - endpoint: Endpoint spécifique à tester
                - threads: Nombre de threads
                - request_count: Nombre de requêtes simultanées
                - burst_mode: Mode rafale
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.test_count = 0
        self.success_count = 0
        self.race_detected_count = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        print(f"  → Test de race conditions sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Rafales contrôlées")
        
        vulnerabilities = []
        
        # Déterminer les endpoints à tester
        endpoint = kwargs.get('endpoint')
        if endpoint:
            endpoints = [endpoint]
        else:
            endpoints = self.endpoints_sensitive if self.config.test_all_endpoints else self.endpoints_sensitive[:3]
        
        for endpoint_url in endpoints:
            if endpoint_url in self.tested_endpoints:
                continue
            
            test_url = target.rstrip('/') + endpoint_url
            self.tested_endpoints.add(endpoint_url)
            
            print(f"    → Test endpoint: {endpoint_url}")
            
            # Pause APT entre les endpoints
            if self.config.apt_mode and self.config.slow_burst:
                time.sleep(random.uniform(5, 15))
            
            # Technique 1: Inscription simultanée
            register_result = self._test_concurrent_registration(test_url, **kwargs)
            if register_result['vulnerable']:
                vulnerabilities.append({
                    "type": "concurrent_registration",
                    "severity": "HIGH",
                    "endpoint": endpoint_url,
                    "details": register_result['details'],
                    "proof": register_result.get('proof'),
                    "risk_score": 85
                })
                print(f"      ✓ Race condition sur inscription: {endpoint_url}")
                self.race_detected_count += 1
            
            # Technique 2: Réinitialisation de mot de passe
            reset_result = self._test_concurrent_password_reset(test_url, **kwargs)
            if reset_result['vulnerable']:
                vulnerabilities.append({
                    "type": "concurrent_password_reset",
                    "severity": "CRITICAL",
                    "endpoint": endpoint_url,
                    "details": reset_result['details'],
                    "proof": reset_result.get('proof'),
                    "risk_score": 95
                })
                print(f"      ✓ Race condition sur reset password: {endpoint_url}")
                self.race_detected_count += 1
            
            # Technique 3: Contournement de rate limiting
            limit_result = self._test_rate_limit_bypass(test_url, **kwargs)
            if limit_result['vulnerable']:
                vulnerabilities.append({
                    "type": "rate_limit_bypass",
                    "severity": "MEDIUM",
                    "endpoint": endpoint_url,
                    "details": limit_result['details'],
                    "risk_score": 70
                })
                print(f"      ✓ Contournement de rate limiting: {endpoint_url}")
                self.race_detected_count += 1
            
            # Technique 4: Token reuse
            if self.config.test_token_reuse:
                token_result = self._test_token_reuse(test_url, **kwargs)
                if token_result['vulnerable']:
                    vulnerabilities.append({
                        "type": "token_reuse",
                        "severity": "HIGH",
                        "endpoint": endpoint_url,
                        "details": token_result['details'],
                        "risk_score": 85
                    })
                    print(f"      ✓ Token reuse possible: {endpoint_url}")
                    self.race_detected_count += 1
            
            # Technique 5: Balance bypass
            if self.config.test_balance_bypass and 'transfer' in endpoint_url or 'withdraw' in endpoint_url:
                balance_result = self._test_balance_bypass(test_url, **kwargs)
                if balance_result['vulnerable']:
                    vulnerabilities.append({
                        "type": "balance_bypass",
                        "severity": "CRITICAL",
                        "endpoint": endpoint_url,
                        "details": balance_result['details'],
                        "proof": balance_result.get('proof'),
                        "risk_score": 98
                    })
                    print(f"      ✓ Balance bypass détecté: {endpoint_url}")
                    self.race_detected_count += 1
            
            # Technique 6: Voucher abuse
            if self.config.test_voucher_abuse:
                voucher_result = self._test_voucher_abuse(test_url, **kwargs)
                if voucher_result['vulnerable']:
                    vulnerabilities.append({
                        "type": "voucher_abuse",
                        "severity": "HIGH",
                        "endpoint": endpoint_url,
                        "details": voucher_result['details'],
                        "risk_score": 90
                    })
                    print(f"      ✓ Voucher abuse possible: {endpoint_url}")
                    self.race_detected_count += 1
            
            # Technique 7: Lock bypass
            if self.config.test_lock_bypass:
                lock_result = self._test_lock_bypass(test_url, **kwargs)
                if lock_result['vulnerable']:
                    vulnerabilities.append({
                        "type": "lock_bypass",
                        "severity": "MEDIUM",
                        "endpoint": endpoint_url,
                        "details": lock_result['details'],
                        "risk_score": 75
                    })
                    print(f"      ✓ Lock bypass détecté: {endpoint_url}")
                    self.race_detected_count += 1
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'threads' in kwargs:
            self.config.threads = kwargs['threads']
        if 'request_count' in kwargs:
            self.config.request_count = kwargs['request_count']
        if 'burst_mode' in kwargs:
            self.config.burst_mode = kwargs['burst_mode']
        if 'test_all_endpoints' in kwargs:
            self.config.test_all_endpoints = kwargs['test_all_endpoints']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.slow_burst = True
            self.config.threads = min(self.config.threads, 5)
            self.config.request_count = min(self.config.request_count, 10)
            self.config.request_spacing = (0.05, 0.2)  # Plus lent pour éviter détection
        
        # Mode furtif
        if kwargs.get('stealth_mode', False):
            self.config.stealth_headers = True
            self.config.random_user_agents = True
    
    def _get_stealth_headers(self, additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Génère des headers furtifs"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        if self.config.random_user_agents:
            headers['User-Agent'] = random.choice(self.user_agents)
        
        if self.config.stealth_headers:
            headers['Cache-Control'] = 'no-cache'
            headers['Pragma'] = 'no-cache'
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _test_concurrent_registration(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Teste les inscriptions simultanées avec le même email
        
        Args:
            url: URL d'inscription
            **kwargs: Options supplémentaires
        """
        result = {
            "vulnerable": False,
            "details": None,
            "proof": None
        }
        
        test_email = f"race_{int(time.time()*1000)}@test.com"
        responses = []
        success_codes = []
        
        def register(thread_id):
            username = f"user_{int(time.time()*1000)}_{thread_id}"
            data = {
                'email': test_email,
                'username': username,
                'password': 'Test123!',
                'password_confirmation': 'Test123!'
            }
            
            try:
                headers = self._get_stealth_headers()
                response = requests.post(url, data=data, headers=headers, 
                                       timeout=5, verify=False)
                responses.append(response)
                return response.status_code
            except Exception as e:
                responses.append(None)
                return 0
        
        # Exécuter les requêtes en rafale
        if self.config.burst_mode:
            with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
                futures = [executor.submit(register, i) for i in range(self.config.request_count)]
                
                # Optionnel: ajouter un petit délai entre les submissions
                if self.config.request_spacing:
                    time.sleep(random.uniform(*self.config.request_spacing))
                
                for future in as_completed(futures):
                    status = future.result()
                    if status in [200, 201, 302]:
                        success_codes.append(status)
        else:
            # Mode séquentiel
            for i in range(self.config.request_count):
                status = register(i)
                if status in [200, 201, 302]:
                    success_codes.append(status)
        
        # Vérifier si plusieurs inscriptions ont réussi
        success_count = len(success_codes)
        
        if success_count > 1:
            result["vulnerable"] = True
            result["details"] = f"{success_count} inscriptions réussies avec le même email {test_email}"
            result["proof"] = f"Email: {test_email}, Success count: {success_count}"
            
            # Vérifier si des comptes ont vraiment été créés
            if self.config.measure_response_time and responses:
                response_times = [r.elapsed.total_seconds() for r in responses if r]
                if response_times:
                    result["avg_response_time"] = sum(response_times) / len(response_times)
        
        return result
    
    def _test_concurrent_password_reset(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Teste les demandes de réinitialisation de mot de passe simultanées
        
        Args:
            url: URL de reset password
            **kwargs: Options supplémentaires
        """
        result = {
            "vulnerable": False,
            "details": None,
            "proof": None
        }
        
        test_email = f"reset_{int(time.time()*1000)}@test.com"
        tokens = set()
        token_patterns = [
            r'token[=:][a-f0-9]{32,}',
            r'reset_token[=:][a-f0-9]+',
            r'code[=:][0-9]{6}',
            r'[a-f0-9]{32,40}'
        ]
        
        def request_reset(thread_id):
            data = {'email': test_email}
            try:
                headers = self._get_stealth_headers()
                response = requests.post(url, data=data, headers=headers,
                                       timeout=5, verify=False)
                
                # Extraire les tokens
                for pattern in token_patterns:
                    found_tokens = re.findall(pattern, response.text.lower())
                    for token in found_tokens:
                        tokens.add(token)
                
                return response.status_code
            except:
                return 0
        
        # Exécuter les requêtes
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = [executor.submit(request_reset, i) for i in range(self.config.request_count)]
            
            for future in as_completed(futures):
                future.result()
        
        # Vérifier si plusieurs tokens différents ont été générés
        if len(tokens) > 1:
            result["vulnerable"] = True
            result["details"] = f"{len(tokens)} tokens différents générés pour {test_email}"
            result["proof"] = f"Tokens: {list(tokens)[:3]}"
        
        return result
    
    def _test_rate_limit_bypass(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Teste le contournement du rate limiting via requêtes simultanées
        
        Args:
            url: URL cible
            **kwargs: Options supplémentaires
        """
        result = {
            "vulnerable": False,
            "details": None,
            "proof": None
        }
        
        successful_requests = 0
        rate_limited = 0
        
        def make_request(thread_id):
            nonlocal successful_requests, rate_limited
            try:
                headers = self._get_stealth_headers()
                response = requests.get(url, headers=headers, timeout=5, verify=False)
                
                if response.status_code == 200:
                    successful_requests += 1
                    return True
                elif response.status_code == 429 or 'too many' in response.text.lower():
                    rate_limited += 1
                    return False
            except:
                pass
            return False
        
        # Mode rafale pour bypass rate limit
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = [executor.submit(make_request, i) for i in range(self.config.request_count)]
            
            # Rafale quasi-simultanée
            if self.config.burst_mode:
                time.sleep(0.001)  # Délai minimal
            
            for future in as_completed(futures):
                future.result()
        
        # Vérifier si le rate limiting est inefficace
        success_rate = successful_requests / self.config.request_count if self.config.request_count > 0 else 0
        
        if success_rate > 0.7 and rate_limited < self.config.request_count * 0.3:
            result["vulnerable"] = True
            result["details"] = f"Rate limiting inefficace: {successful_requests}/{self.config.request_count} requêtes réussies"
            result["proof"] = f"Success rate: {success_rate:.1%}, Rate limited: {rate_limited}"
        
        return result
    
    def _test_token_reuse(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Teste la réutilisation de tokens de réinitialisation
        
        Args:
            url: URL de reset password
            **kwargs: Options supplémentaires
        """
        result = {
            "vulnerable": False,
            "details": None,
            "proof": None
        }
        
        test_email = f"token_reuse_{int(time.time()*1000)}@test.com"
        first_token = None
        
        # Demander un premier token
        try:
            headers = self._get_stealth_headers()
            data = {'email': test_email}
            response = requests.post(url, data=data, headers=headers, timeout=5, verify=False)
            
            # Extraire le token
            token_pattern = r'[a-f0-9]{32,40}'
            tokens = re.findall(token_pattern, response.text)
            if tokens:
                first_token = tokens[0]
        except:
            pass
        
        if first_token:
            # Demander un second token simultanément
            tokens_found = set()
            
            def request_token():
                try:
                    response = requests.post(url, data=data, headers=headers, timeout=5, verify=False)
                    tokens = re.findall(token_pattern, response.text)
                    for token in tokens:
                        tokens_found.add(token)
                except:
                    pass
            
            with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
                futures = [executor.submit(request_token) for _ in range(self.config.request_count)]
                
                for future in as_completed(futures):
                    future.result()
            
            # Vérifier si l'ancien token reste valide
            if first_token in tokens_found:
                result["vulnerable"] = True
                result["details"] = f"Token reuse possible: {first_token} reste valide"
                result["proof"] = f"Token: {first_token[:20]}..."
        
        return result
    
    def _test_balance_bypass(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Teste le contournement de solde via transactions simultanées
        
        Args:
            url: URL de transaction
            **kwargs: Options supplémentaires
        """
        result = {
            "vulnerable": False,
            "details": None,
            "proof": None
        }
        
        test_user = kwargs.get('test_user', 'test_user_1')
        test_amount = kwargs.get('test_amount', 10)
        
        successful_transactions = 0
        transaction_ids = set()
        
        def make_transaction(thread_id):
            nonlocal successful_transactions
            data = {
                'user_id': test_user,
                'amount': test_amount,
                'transaction_id': f"tx_{int(time.time()*1000)}_{thread_id}"
            }
            
            try:
                headers = self._get_stealth_headers()
                response = requests.post(url, data=data, headers=headers,
                                       timeout=5, verify=False)
                
                if response.status_code == 200:
                    successful_transactions += 1
                    # Extraire l'ID de transaction
                    tx_id_match = re.search(r'transaction[_\s]*id[=:][\s]*([a-f0-9]+)', 
                                           response.text, re.IGNORECASE)
                    if tx_id_match:
                        transaction_ids.add(tx_id_match.group(1))
                    return True
            except:
                pass
            return False
        
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = [executor.submit(make_transaction, i) for i in range(self.config.request_count)]
            
            for future in as_completed(futures):
                future.result()
        
        # Vérifier si plusieurs transactions ont réussi
        if successful_transactions > 1:
            result["vulnerable"] = True
            result["details"] = f"{successful_transactions} transactions réussies simultanément"
            result["proof"] = f"Total amount potentiel: {successful_transactions * test_amount}"
            
            if len(transaction_ids) > 1:
                result["details"] += f" - {len(transaction_ids)} IDs uniques"
        
        return result
    
    def _test_voucher_abuse(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Teste l'abus de codes promo/vouchers via race conditions
        
        Args:
            url: URL d'application de voucher
            **kwargs: Options supplémentaires
        """
        result = {
            "vulnerable": False,
            "details": None,
            "proof": None
        }
        
        test_voucher = kwargs.get('test_voucher', 'TEST2024')
        successful_applications = 0
        
        def apply_voucher(thread_id):
            nonlocal successful_applications
            data = {'voucher_code': test_voucher}
            
            try:
                headers = self._get_stealth_headers()
                response = requests.post(url, data=data, headers=headers,
                                       timeout=5, verify=False)
                
                if response.status_code == 200 and 'success' in response.text.lower():
                    successful_applications += 1
                    return True
            except:
                pass
            return False
        
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = [executor.submit(apply_voucher, i) for i in range(self.config.request_count)]
            
            for future in as_completed(futures):
                future.result()
        
        # Vérifier si le voucher a été appliqué plusieurs fois
        if successful_applications > 1:
            result["vulnerable"] = True
            result["details"] = f"Voucher {test_voucher} appliqué {successful_applications} fois"
            result["proof"] = f"Voucher: {test_voucher}, Applications: {successful_applications}"
        
        return result
    
    def _test_lock_bypass(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Teste le contournement de verrouillage de compte
        
        Args:
            url: URL de login
            **kwargs: Options supplémentaires
        """
        result = {
            "vulnerable": False,
            "details": None,
            "proof": None
        }
        
        test_user = f"lock_test_{int(time.time())}"
        failed_attempts = 0
        successes = 0
        
        def attempt_login(thread_id):
            nonlocal failed_attempts, successes
            data = {
                'username': test_user,
                'password': f'wrong_password_{thread_id}'
            }
            
            try:
                headers = self._get_stealth_headers()
                response = requests.post(url, data=data, headers=headers,
                                       timeout=5, verify=False)
                
                if response.status_code == 200 and 'locked' in response.text.lower():
                    failed_attempts += 1
                elif response.status_code == 200:
                    successes += 1
            except:
                pass
        
        # Tenter de dépasser la limite de tentatives
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = [executor.submit(attempt_login, i) for i in range(self.config.request_count)]
            
            for future in as_completed(futures):
                future.result()
        
        # Vérifier si le lockout n'a pas fonctionné
        if successes > 0 and failed_attempts > self.config.request_count * 0.5:
            result["vulnerable"] = True
            result["details"] = f"Lock bypass possible: {successes} succès après {failed_attempts} échecs"
            result["proof"] = f"Success rate: {successes/self.config.request_count:.1%}"
        
        return result
    
    def test_transaction_race(self, url: str, user_id: str, amount: int, 
                             request_count: int = 20) -> Dict[str, Any]:
        """
        Teste les race conditions sur les transactions (ex: retraits multiples)
        
        Args:
            url: URL de transaction
            user_id: ID utilisateur
            amount: Montant à retirer
            request_count: Nombre de requêtes
        """
        original_config = self.config.request_count
        self.config.request_count = request_count
        
        result = self._test_balance_bypass(url, test_user=user_id, test_amount=amount)
        
        self.config.request_count = original_config
        return result
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "race_conditions_detected": self.race_detected_count,
            "test_duration": duration,
            "tests_performed": self.test_count,
            "successful_tests": self.success_count,
            "config": {
                "apt_mode": self.config.apt_mode,
                "burst_mode": self.config.burst_mode,
                "threads": self.config.threads,
                "request_count": self.config.request_count
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune race condition détectée"}
        
        severities = {}
        types = {}
        max_risk = 0
        
        for v in vulnerabilities:
            sev = v.get('severity', 'MEDIUM')
            severities[sev] = severities.get(sev, 0) + 1
            
            vtype = v.get('type', 'unknown')
            types[vtype] = types.get(vtype, 0) + 1
            
            risk = v.get('risk_score', 0)
            max_risk = max(max_risk, risk)
        
        return {
            "total": len(vulnerabilities),
            "by_severity": severities,
            "by_type": types,
            "max_risk_score": max_risk,
            "critical_findings": len([v for v in vulnerabilities if v.get('severity') == 'CRITICAL'])
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        vuln_types = [v['type'] for v in vulnerabilities]
        
        if 'concurrent_registration' in vuln_types:
            recommendations.add("Implémenter des contraintes UNIQUE au niveau base de données")
            recommendations.add("Utiliser des verrous optimistes pour les inscriptions")
        
        if 'concurrent_password_reset' in vuln_types:
            recommendations.add("Invalider les anciens tokens lors d'une nouvelle demande")
            recommendations.add("Limiter le nombre de tokens actifs par utilisateur")
        
        if 'rate_limit_bypass' in vuln_types:
            recommendations.add("Implémenter un rate limiting au niveau applicatif")
            recommendations.add("Utiliser des buckets à tokens pour la limitation")
        
        if 'balance_bypass' in vuln_types:
            recommendations.add("Utiliser des transactions atomiques en base de données")
            recommendations.add("Implémenter des verrous pessimistes pour les opérations financières")
        
        if 'token_reuse' in vuln_types:
            recommendations.add("Marquer les tokens comme utilisés après une opération")
            recommendations.add("Implémenter une expiration courte pour les tokens")
        
        if not recommendations:
            recommendations.add("Auditer régulièrement les endpoints sensibles")
            recommendations.add("Implémenter des tests de race conditions dans le CI/CD")
        
        return list(recommendations)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de l'attaque"""
        return {
            "total_tests": self.test_count,
            "race_conditions_found": self.race_detected_count,
            "success_rate": (self.race_detected_count / self.test_count * 100) if self.test_count > 0 else 0,
            "duration_seconds": time.time() - self.start_time if self.start_time else 0
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    rc = RaceCondition()
    results = rc.scan("https://example.com")
    print(f"Race conditions détectées: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = RaceConditionConfig(apt_mode=True, slow_burst=True, threads=3)
    rc_apt = RaceCondition(config=apt_config)
    results_apt = rc_apt.scan(
        "https://example.com",
        test_all_endpoints=False,
        request_count=10
    )
    print(f"Race conditions trouvées (APT): {results_apt['count']}")
    
    # Test transaction spécifique
    if results_apt['vulnerabilities']:
        print("\n=== Recommandations ===")
        for rec in results_apt['recommendations']:
            print(f"  • {rec}")