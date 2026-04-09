#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection de failles de logique métier pour RedForge
Détecte les vulnérabilités dans la logique applicative
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class BusinessLogicConfig:
    """Configuration avancée pour la détection de failles logiques"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_test_requests: int = 50
    timeout: int = 10
    test_price: bool = True
    test_workflow: bool = True
    test_ratelimit: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_race_conditions: bool = True
    test_bulk_operations: bool = True
    max_concurrent: int = 5


class BusinessLogicFlaws:
    """Détection avancée des failles de logique métier"""
    
    def __init__(self, config: Optional[BusinessLogicConfig] = None):
        """
        Initialise le détecteur de failles de logique métier
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or BusinessLogicConfig()
        
        # Scénarios de test
        self.test_scenarios = self._generate_scenarios()
        
        # Workflow steps
        self.workflow_steps = [
            "checkout", "payment", "confirm", "complete", "shipping",
            "billing", "review", "submit", "validate", "process",
            "finalize", "approve", "authorize", "capture", "settle"
        ]
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Indicateurs de succès
        self.success_indicators = [
            'success', 'updated', 'modified', 'changed', 'ok',
            'added', 'created', 'processed', 'completed', 'approved',
            'authorized', 'captured', 'settled', 'confirmed'
        ]
        
        # Métriques
        self.start_time = None
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        self.rate_limit_hits = 0
    
    def _generate_scenarios(self) -> Dict[str, Dict]:
        """Génère les scénarios de test avancés"""
        return {
            "price_manipulation": {
                "params": ["price", "amount", "total", "cost", "value", "prix",
                          "subtotal", "grand_total", "unit_price", "item_price"],
                "test_values": [-1, 0, 0.01, 999999, "null", "false", "NaN",
                               "0.001", "-0.01", "1e-10", "999999999"],
                "description": "Manipulation des prix/montants",
                "severity": "CRITICAL"
            },
            "quantity_manipulation": {
                "params": ["quantity", "qty", "count", "nb", "number", "qte",
                          "items", "units", "pieces", "volume"],
                "test_values": [-1, 0, 9999, 1000000, "null", "NaN", "1e10",
                               "-100", "999999999", "0.5", "1.5"],
                "description": "Manipulation des quantités",
                "severity": "HIGH"
            },
            "workflow_bypass": {
                "params": ["step", "stage", "phase", "status", "state",
                          "transition", "action", "command"],
                "test_values": ["complete", "done", "finished", "skip", "bypass",
                               "final", "approved", "confirmed", "skip_step"],
                "description": "Contournement de workflow",
                "severity": "HIGH"
            },
            "id_manipulation": {
                "params": ["id", "user_id", "order_id", "transaction_id",
                          "account_id", "profile_id", "item_id", "product_id"],
                "test_values": ["1", "2", "0", "-1", "null", "admin",
                               "999999", "1000000", "' OR '1'='1"],
                "description": "Manipulation d'identifiants",
                "severity": "CRITICAL"
            },
            "discount_abuse": {
                "params": ["discount", "coupon", "promo", "code", "voucher",
                          "promotion", "offer", "deal", "reduction"],
                "test_values": ["100", "100%", "FREE", "ADMIN", "SUPER",
                               "UNLIMITED", "9999", "-50", "INFINITE"],
                "description": "Abus de réductions/codes promo",
                "severity": "HIGH"
            },
            "rate_limit_bypass": {
                "params": ["limit", "offset", "page", "per_page", "skip",
                          "take", "top", "max_results", "page_size"],
                "test_values": ["999999", "1000000", "null", "NaN", "-1",
                               "0", "999999999", "1e10"],
                "description": "Contournement de limites",
                "severity": "MEDIUM"
            },
            "gift_card_abuse": {
                "params": ["gift_card", "giftcard", "card_code", "voucher_code",
                          "redemption_code", "coupon_code"],
                "test_values": ["INVALID", "EXPIRED", "USED", "STOLEN",
                               "000000", "111111", "999999"],
                "description": "Abus de cartes cadeaux",
                "severity": "HIGH"
            },
            "shipping_abuse": {
                "params": ["shipping", "delivery", "shipping_cost", "delivery_fee",
                          "shipping_method", "delivery_option"],
                "test_values": ["0", "free", "NULL", "none", "pickup",
                               "0.00", "-1", "FREE_SHIPPING"],
                "description": "Manipulation des frais de livraison",
                "severity": "MEDIUM"
            }
        }
    
    def _get_stealth_headers(self, additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Génère des headers furtifs"""
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'
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
        Scanne les failles de logique métier
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - test_price: Tester la manipulation de prix
                - test_workflow: Tester le contournement de workflow
                - auth_cookie: Cookie d'authentification
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tests_performed = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test des failles de logique métier sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        auth_cookie = kwargs.get('auth_cookie')
        cookies = {'session': auth_cookie} if auth_cookie else {}
        
        # Tester chaque scénario
        for scenario_name, scenario in self.test_scenarios.items():
            if not kwargs.get(f'test_{scenario_name}', self.config.__dict__.get(f'test_{scenario_name.split("_")[0]}', True)):
                continue
            
            scenario_vulns = self._test_scenario(target, scenario_name, scenario, cookies)
            vulnerabilities.extend(scenario_vulns)
            
            if scenario_vulns:
                self.vulnerabilities_found += len(scenario_vulns)
        
        # Tester le contournement de workflow
        if self.config.test_workflow:
            workflow_vulns = self._test_workflow_bypass_advanced(target, cookies)
            vulnerabilities.extend(workflow_vulns)
            self.vulnerabilities_found += len(workflow_vulns)
        
        # Tester les limites de taux
        if self.config.test_ratelimit:
            rate_vulns = self._test_rate_limits_advanced(target, cookies)
            vulnerabilities.extend(rate_vulns)
            self.vulnerabilities_found += len(rate_vulns)
        
        # Tester les race conditions
        if self.config.detect_race_conditions:
            race_vulns = self._test_race_conditions(target, cookies)
            vulnerabilities.extend(race_vulns)
            self.vulnerabilities_found += len(race_vulns)
        
        # Tester les opérations bulk
        if self.config.test_bulk_operations:
            bulk_vulns = self._test_bulk_operations(target, cookies)
            vulnerabilities.extend(bulk_vulns)
            self.vulnerabilities_found += len(bulk_vulns)
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'test_price' in kwargs:
            self.config.test_price = kwargs['test_price']
        if 'test_workflow' in kwargs:
            self.config.test_workflow = kwargs['test_workflow']
        if 'max_test_requests' in kwargs:
            self.config.max_test_requests = kwargs['max_test_requests']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_test_requests = min(self.config.max_test_requests, 20)
            self.config.delay_between_tests = (5, 15)
    
    def _test_scenario(self, target: str, scenario_name: str, 
                       scenario: Dict, cookies: Dict) -> List[Dict[str, Any]]:
        """Teste un scénario spécifique"""
        vulnerabilities = []
        
        for idx, param in enumerate(scenario['params']):
            if self.config.apt_mode and idx > 3:
                break
            
            for test_value in scenario['test_values'][:self.config.max_test_requests]:
                if self.config.random_delays:
                    time.sleep(random.uniform(0.3, 0.8))
                
                result = self._test_parameter_advanced(target, param, test_value, cookies)
                self.tests_performed += 1
                
                if result['vulnerable']:
                    vulnerabilities.append({
                        "scenario": scenario_name,
                        "parameter": param,
                        "test_value": str(test_value),
                        "severity": scenario.get('severity', 'HIGH'),
                        "details": result['details'],
                        "response_preview": result.get('response_preview', ''),
                        "risk_score": self._get_risk_score(scenario.get('severity', 'HIGH')),
                        "original_response_length": result.get('original_length', 0),
                        "modified_response_length": result.get('modified_length', 0)
                    })
                    print(f"      ✓ {scenario['description']}: {param}={test_value}")
                    break  # Un suffit par paramètre
        
        return vulnerabilities
    
    def _test_parameter_advanced(self, target: str, param: str, test_value: Any,
                                  cookies: Dict) -> Dict[str, Any]:
        """Teste un paramètre avec analyse avancée"""
        result = {
            "vulnerable": False,
            "details": None,
            "response_preview": None,
            "original_length": 0,
            "modified_length": 0
        }
        
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        
        # Sauvegarder la valeur originale
        original_value = query_params.get(param, [None])[0]
        
        # Modifier le paramètre
        query_params[param] = [str(test_value)]
        new_query = urlencode(query_params, doseq=True)
        test_url = urlunparse(parsed._replace(query=new_query))
        
        try:
            headers = self._get_stealth_headers()
            
            # Requête originale
            original_response = requests.get(target, headers=headers, cookies=cookies,
                                           timeout=self.config.timeout, verify=False)
            
            # Requête modifiée
            test_response = requests.get(test_url, headers=headers, cookies=cookies,
                                       timeout=self.config.timeout, verify=False)
            
            result["original_length"] = len(original_response.text)
            result["modified_length"] = len(test_response.text)
            
            # Vérifier les différences de statut
            if test_response.status_code != original_response.status_code:
                result["vulnerable"] = True
                result["details"] = f"Code HTTP différent: {original_response.status_code} -> {test_response.status_code}"
                result["response_preview"] = test_response.text[:200]
                return result
            
            # Vérifier les indicateurs de succès
            for indicator in self.success_indicators:
                if indicator in test_response.text.lower():
                    # Vérifier que ce n'est pas une erreur
                    if 'error' not in test_response.text.lower() and 'invalid' not in test_response.text.lower():
                        result["vulnerable"] = True
                        result["details"] = f"Réponse indiquant un succès avec valeur {test_value}"
                        result["response_preview"] = test_response.text[:200]
                        return result
            
            # Vérifier les différences de longueur significatives
            if abs(len(test_response.text) - len(original_response.text)) > 100:
                result["vulnerable"] = True
                result["details"] = f"Différence de taille de réponse: {len(original_response.text)} -> {len(test_response.text)}"
                
        except Exception as e:
            if not self.config.passive_detection:
                pass
        
        return result
    
    def _test_workflow_bypass_advanced(self, target: str, cookies: Dict) -> List[Dict[str, Any]]:
        """Test avancé de contournement de workflow"""
        vulnerabilities = []
        
        # Tester les URLs de workflow
        workflow_urls = [
            f"{target.rstrip('/')}/{step}"
            for step in self.workflow_steps
        ]
        
        # Ajouter des variantes avec paramètres
        workflow_urls.extend([
            f"{target}?step={step}",
            f"{target}?stage={step}",
            f"{target}?phase={step}"
        ])
        
        for test_url in workflow_urls[:self.config.max_test_requests]:
            if self.config.random_delays:
                time.sleep(random.uniform(0.5, 1.0))
            
            try:
                headers = self._get_stealth_headers()
                response = requests.get(test_url, headers=headers, cookies=cookies,
                                      timeout=self.config.timeout, verify=False)
                
                # Vérifier l'accès sans prérequis
                if response.status_code == 200:
                    # Vérifier les indicateurs d'accès autorisé
                    unauthorized_indicators = ['login', 'unauthorized', 'forbidden', 'access denied']
                    if not any(ind in response.text.lower() for ind in unauthorized_indicators):
                        vulnerabilities.append({
                            "scenario": "workflow_bypass",
                            "step": test_url,
                            "severity": "HIGH",
                            "details": f"Étape de workflow accessible directement: {test_url}",
                            "risk_score": 85
                        })
                        print(f"      ✓ Étape de workflow accessible: {test_url}")
                        
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_rate_limits_advanced(self, target: str, cookies: Dict) -> List[Dict[str, Any]]:
        """Test avancé des limites de taux"""
        vulnerabilities = []
        success_count = 0
        response_times = []
        
        # Effectuer une série de requêtes
        for i in range(min(self.config.max_test_requests, 30)):
            try:
                headers = self._get_stealth_headers()
                start_time = time.time()
                response = requests.get(target, headers=headers, cookies=cookies,
                                      timeout=self.config.timeout, verify=False)
                elapsed = time.time() - start_time
                response_times.append(elapsed)
                
                if response.status_code == 200:
                    success_count += 1
                
                # Délai variable
                if self.config.random_delays:
                    time.sleep(random.uniform(0.1, 0.3))
                    
            except Exception:
                pass
        
        success_rate = success_count / min(self.config.max_test_requests, 30) * 100
        
        if success_rate > 80:
            vulnerabilities.append({
                "scenario": "rate_limit_bypass",
                "severity": "MEDIUM",
                "details": f"Absence de rate limiting: {success_count}/{min(self.config.max_test_requests, 30)} requêtes réussies ({success_rate:.1f}%)",
                "risk_score": 65,
                "avg_response_time": sum(response_times) / len(response_times) if response_times else 0
            })
        
        return vulnerabilities
    
    def _test_race_conditions(self, target: str, cookies: Dict) -> List[Dict[str, Any]]:
        """Teste les race conditions dans les opérations critiques"""
        vulnerabilities = []
        
        # Payloads pour tester les race conditions
        race_payloads = [
            {"action": "redeem", "amount": 100},
            {"action": "transfer", "amount": 50},
            {"action": "claim", "value": "unlimited"}
        ]
        
        for payload in race_payloads:
            try:
                headers = self._get_stealth_headers({'Content-Type': 'application/json'})
                
                # Envoyer des requêtes simultanées
                def send_request():
                    return requests.post(target, json=payload, headers=headers,
                                       cookies=cookies, timeout=5, verify=False)
                
                with ThreadPoolExecutor(max_workers=self.config.max_concurrent) as executor:
                    futures = [executor.submit(send_request) for _ in range(5)]
                    responses = [f.result() for f in futures]
                
                # Vérifier si des opérations ont réussi en double
                success_count = sum(1 for r in responses if r.status_code == 200)
                
                if success_count > 1:
                    vulnerabilities.append({
                        "scenario": "race_condition",
                        "severity": "CRITICAL",
                        "details": f"Race condition détectée: {success_count} opérations réussies simultanément",
                        "payload": payload,
                        "risk_score": 95
                    })
                    print(f"      ✓ Race condition détectée: {success_count} succès simultanés")
                    break
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_bulk_operations(self, target: str, cookies: Dict) -> List[Dict[str, Any]]:
        """Teste les opérations en masse"""
        vulnerabilities = []
        
        # Tester les paramètres de pagination
        pagination_params = ['limit', 'per_page', 'page_size', 'take']
        
        for param in pagination_params:
            for test_value in [1000, 10000, 100000]:
                test_url = f"{target}?{param}={test_value}"
                
                try:
                    headers = self._get_stealth_headers()
                    response = requests.get(test_url, headers=headers, cookies=cookies,
                                          timeout=self.config.timeout, verify=False)
                    
                    if response.status_code == 200:
                        # Vérifier si la réponse est anormalement grande
                        if len(response.text) > 100000:  # Plus de 100KB
                            vulnerabilities.append({
                                "scenario": "bulk_operation",
                                "severity": "MEDIUM",
                                "details": f"Opération bulk possible: {param}={test_value} (réponse: {len(response.text)} bytes)",
                                "parameter": param,
                                "value": test_value,
                                "risk_score": 70
                            })
                            print(f"      ✓ Bulk operation: {param}={test_value}")
                            break
                            
                except Exception:
                    continue
        
        return vulnerabilities
    
    def _get_risk_score(self, severity: str) -> int:
        """Retourne le score de risque basé sur la sévérité"""
        scores = {
            'CRITICAL': 95,
            'HIGH': 85,
            'MEDIUM': 65,
            'LOW': 40
        }
        return scores.get(severity, 50)
    
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
                "test_price": self.config.test_price,
                "test_workflow": self.config.test_workflow
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune faille de logique métier détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_scenario": {
                "price_manipulation": len([v for v in vulnerabilities if v['scenario'] == 'price_manipulation']),
                "workflow_bypass": len([v for v in vulnerabilities if v['scenario'] == 'workflow_bypass']),
                "rate_limit_bypass": len([v for v in vulnerabilities if v['scenario'] == 'rate_limit_bypass']),
                "race_condition": len([v for v in vulnerabilities if v['scenario'] == 'race_condition']),
                "bulk_operation": len([v for v in vulnerabilities if v['scenario'] == 'bulk_operation'])
            },
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            scenario = vuln.get('scenario', '')
            
            if scenario == 'price_manipulation':
                recommendations.add("Ne jamais faire confiance aux paramètres de prix envoyés par le client")
                recommendations.add("Vérifier et valider les prix côté serveur")
            elif scenario == 'workflow_bypass':
                recommendations.add("Implémenter une machine à états pour valider les transitions")
                recommendations.add("Vérifier les prérequis avant chaque étape")
            elif scenario == 'rate_limit_bypass':
                recommendations.add("Implémenter un rate limiting basé sur IP et utilisateur")
                recommendations.add("Utiliser des buckets à tokens ou leaky buckets")
            elif scenario == 'race_condition':
                recommendations.add("Utiliser des verrous ou transactions atomiques")
                recommendations.add("Implémenter des mécanismes d'idempotence")
            elif scenario == 'bulk_operation':
                recommendations.add("Limiter la taille des résultats et implémenter la pagination")
                recommendations.add("Valider les paramètres de limite")
            elif scenario == 'id_manipulation':
                recommendations.add("Utiliser des IDs non séquentiels (UUID)")
                recommendations.add("Vérifier les autorisations pour chaque ressource")
            elif scenario == 'discount_abuse':
                recommendations.add("Valider les codes promo côté serveur")
                recommendations.add("Limiter l'utilisation des codes promo")
        
        if not recommendations:
            recommendations.add("Auditer régulièrement la logique métier")
            recommendations.add("Implémenter des tests de sécurité automatisés")
        
        return list(recommendations)
    
    def test_price_manipulation(self, product_url: str, original_price: float,
                                cookie: str = None) -> Dict[str, Any]:
        """
        Teste spécifiquement la manipulation de prix
        
        Args:
            product_url: URL du produit
            original_price: Prix original
            cookie: Cookie de session
        """
        result = {
            "vulnerable": False,
            "successful_prices": [],
            "details": []
        }
        
        test_prices = [0, 0.01, 1, original_price / 2, original_price * 0.1,
                      -1, original_price * 2, original_price * 10]
        cookies = {'session': cookie} if cookie else {}
        
        for price in test_prices:
            parsed = urlparse(product_url)
            query_params = parse_qs(parsed.query)
            query_params['price'] = [str(price)]
            new_query = urlencode(query_params, doseq=True)
            test_url = urlunparse(parsed._replace(query=new_query))
            
            try:
                headers = self._get_stealth_headers()
                response = requests.get(test_url, headers=headers, cookies=cookies,
                                      timeout=self.config.timeout, verify=False)
                
                if any(ind in response.text.lower() for ind in self.success_indicators):
                    if 'error' not in response.text.lower() and 'invalid' not in response.text.lower():
                        result["vulnerable"] = True
                        result["successful_prices"].append(price)
                        result["details"].append(f"Prix {price} accepté")
                        print(f"      ✓ Prix {price} accepté")
                        
            except Exception:
                continue
        
        return result
    
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
    bl = BusinessLogicFlaws()
    results = bl.scan("https://example.com/product?id=1")
    print(f"Failles de logique métier: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = BusinessLogicConfig(apt_mode=True, max_test_requests=20)
    bl_apt = BusinessLogicFlaws(config=apt_config)
    results_apt = bl_apt.scan("https://example.com/product?id=1", apt_mode=True)
    print(f"Failles de logique métier (APT): {results_apt['count']}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")