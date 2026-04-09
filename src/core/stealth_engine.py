#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moteur de furtivité pour RedForge
Gère les délais, la randomisation, les proxies et les techniques d'évasion
Version APT avec support avancé pour opérations discrètes
"""

import time
import random
import threading
import socket
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from urllib.parse import urlparse


@dataclass
class StealthConfig:
    """Configuration du moteur de furtivité"""
    # Délais
    min_delay: float = 1.0
    max_delay: float = 5.0
    jitter: float = 0.3
    enable_random_delays: bool = True
    
    # Comportement
    apt_mode: bool = False
    respect_robots: bool = True
    respect_rate_limits: bool = True
    
    # Réseau
    proxy_list: List[str] = field(default_factory=list)
    proxy_rotation: bool = False
    user_agent_list: List[str] = field(default_factory=list)
    user_agent_rotation: bool = True
    
    # Timing
    inactivity_start_hour: int = 0
    inactivity_end_hour: int = 6
    work_start_hour: int = 9
    work_end_hour: int = 17
    
    # Évasion
    request_spoofing: bool = True
    randomize_request_order: bool = True
    add_random_parameters: bool = True
    
    # Limites
    max_requests_per_minute: int = 60
    max_concurrent_requests: int = 3
    request_timeout: int = 30


class StealthEngine:
    """
    Moteur de furtivité pour les opérations discrètes
    Gère les délais, la rotation, et les techniques d'évasion
    """
    
    # User-Agents par défaut
    DEFAULT_USER_AGENTS = [
        # Chrome Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        
        # Firefox Windows
        'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/120.0',
        
        # Safari Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        
        # Chrome Linux
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        
        # Edge Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        
        # Mobile
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    ]
    
    # Patterns de délai par niveau
    DELAY_PATTERNS = {
        'low': (0.1, 0.5),      # Très rapide, détectable
        'medium': (0.5, 2.0),   # Normal
        'high': (2.0, 5.0),     # Lent, discret
        'extreme': (5.0, 15.0), # Très lent, ultra discret
        'apt': (10.0, 30.0)     # APT, très lent
    }
    
    def __init__(self, config: Optional[StealthConfig] = None):
        """
        Initialise le moteur de furtivité
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or StealthConfig()
        self._proxy_index = 0
        self._request_count = 0
        self._minute_start = time.time()
        self._last_request_time = 0
        self._request_timestamps: List[float] = []
        self._is_inactive_period = False
        self._current_delay_pattern = 'medium'
        
        # Initialiser les listes si vides
        if not self.config.user_agent_list:
            self.config.user_agent_list = self.DEFAULT_USER_AGENTS.copy()
        
        # État
        self._running = True
        self._stats = {
            "total_delays": 0,
            "total_delay_time": 0,
            "proxy_switches": 0,
            "user_agent_switches": 0,
            "requests_delayed": 0,
            "rate_limit_hits": 0
        }
        
        # Démarrer le thread de gestion des pauses
        self._monitor_thread = threading.Thread(target=self._monitor_inactivity, daemon=True)
        self._monitor_thread.start()
    
    def set_delay_pattern(self, pattern: str):
        """
        Définit le pattern de délai
        
        Args:
            pattern: low, medium, high, extreme, apt
        """
        if pattern in self.DELAY_PATTERNS:
            self._current_delay_pattern = pattern
            min_delay, max_delay = self.DELAY_PATTERNS[pattern]
            self.config.min_delay = min_delay
            self.config.max_delay = max_delay
            
            # En mode APT, activer les options supplémentaires
            if pattern == 'apt':
                self.config.apt_mode = True
                self.config.randomize_request_order = True
                self.config.add_random_parameters = True
    
    def set_delays(self, min_delay: float, max_delay: float, jitter: float = 0.3):
        """
        Définit les délais personnalisés
        
        Args:
            min_delay: Délai minimum en secondes
            max_delay: Délai maximum en secondes
            jitter: Facteur de variation (0-1)
        """
        self.config.min_delay = min_delay
        self.config.max_delay = max_delay
        self.config.jitter = jitter
    
    def apply_delay(self) -> float:
        """
        Applique un délai furtif avant la prochaine requête
        
        Returns:
            Délai appliqué en secondes
        """
        if not self.config.enable_random_delays:
            return 0.0
        
        # Vérifier la période d'inactivité
        if self._is_inactive_period:
            # Pendant l'inactivité, délai plus long
            delay = random.uniform(30, 120)
            time.sleep(delay)
            return delay
        
        # Calculer le délai de base
        base_delay = random.uniform(self.config.min_delay, self.config.max_delay)
        
        # Ajouter du jitter
        jitter = base_delay * self.config.jitter
        delay = base_delay + random.uniform(-jitter, jitter)
        delay = max(0.1, delay)
        
        # Vérifier le rate limiting
        if self.config.respect_rate_limits:
            delay = self._apply_rate_limiting(delay)
        
        # Vérifier le temps depuis la dernière requête
        elapsed = time.time() - self._last_request_time
        if elapsed < delay:
            sleep_time = delay - elapsed
            time.sleep(sleep_time)
            self._stats["total_delay_time"] += sleep_time
        else:
            self._stats["total_delay_time"] += 0
        
        self._last_request_time = time.time()
        self._stats["total_delays"] += 1
        self._stats["requests_delayed"] += 1
        
        return delay
    
    def _apply_rate_limiting(self, base_delay: float) -> float:
        """
        Applique une logique de rate limiting
        
        Args:
            base_delay: Délai de base
            
        Returns:
            Délai ajusté
        """
        now = time.time()
        
        # Nettoyer les timestamps anciens
        self._request_timestamps = [ts for ts in self._request_timestamps if now - ts < 60]
        
        # Vérifier le nombre de requêtes dans la dernière minute
        if len(self._request_timestamps) >= self.config.max_requests_per_minute:
            self._stats["rate_limit_hits"] += 1
            # Attendre que la minute soit écoulée
            oldest = min(self._request_timestamps)
            wait_time = 60 - (now - oldest) + 1
            return max(base_delay, wait_time)
        
        self._request_timestamps.append(now)
        return base_delay
    
    def get_next_proxy(self) -> Optional[str]:
        """
        Retourne le prochain proxy en rotation
        
        Returns:
            URL du proxy ou None
        """
        if not self.config.proxy_list or not self.config.proxy_rotation:
            return None
        
        proxy = self.config.proxy_list[self._proxy_index]
        self._proxy_index = (self._proxy_index + 1) % len(self.config.proxy_list)
        self._stats["proxy_switches"] += 1
        
        return proxy
    
    def get_random_user_agent(self) -> str:
        """
        Retourne un User-Agent aléatoire
        
        Returns:
            User-Agent
        """
        if not self.config.user_agent_rotation:
            return self.config.user_agent_list[0] if self.config.user_agent_list else self.DEFAULT_USER_AGENTS[0]
        
        ua = random.choice(self.config.user_agent_list)
        self._stats["user_agent_switches"] += 1
        return ua
    
    def get_headers(self, additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """
        Génère des headers HTTP furtifs
        
        Args:
            additional_headers: Headers supplémentaires
            
        Returns:
            Dictionnaire de headers
        """
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        if self.config.request_spoofing:
            headers['Cache-Control'] = 'no-cache'
            headers['Pragma'] = 'no-cache'
            
            # Ajouter des headers de referer aléatoires
            referers = [
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://duckduckgo.com/',
                'https://www.reddit.com/',
                'https://twitter.com/'
            ]
            headers['Referer'] = random.choice(referers)
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def add_random_parameters(self, url: str) -> str:
        """
        Ajoute des paramètres aléatoires à l'URL pour éviter le cache
        
        Args:
            url: URL originale
            
        Returns:
            URL avec paramètres aléatoires
        """
        if not self.config.add_random_parameters:
            return url
        
        import urllib.parse
        
        parsed = urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        # Ajouter un paramètre de cache buster
        params['_'] = [str(int(time.time() * 1000))]
        
        # Ajouter un paramètre aléatoire
        random_key = f"r{random.randint(1000, 9999)}"
        params[random_key] = [hashlib.md5(str(time.time()).encode()).hexdigest()[:8]]
        
        new_query = urllib.parse.urlencode(params, doseq=True)
        return parsed._replace(query=new_query).geturl()
    
    def wait_for_active_hours(self) -> bool:
        """
        Attend que la période active commence
        
        Returns:
            True si on doit continuer, False si interruption
        """
        now = datetime.now()
        current_hour = now.hour
        
        # Déterminer si on est en période d'inactivité
        if self.config.inactivity_start_hour <= self.config.inactivity_end_hour:
            is_inactive = (self.config.inactivity_start_hour <= current_hour < self.config.inactivity_end_hour)
        else:
            is_inactive = (current_hour >= self.config.inactivity_start_hour or 
                          current_hour < self.config.inactivity_end_hour)
        
        if is_inactive:
            # Calculer le temps jusqu'à la prochaine période active
            if current_hour < self.config.inactivity_end_hour:
                target_hour = self.config.inactivity_end_hour
            else:
                target_hour = self.config.inactivity_start_hour
            
            target_time = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
            if target_time <= now:
                target_time += timedelta(days=1)
            
            wait_seconds = (target_time - now).total_seconds()
            
            # Attendre par tranches de 60 secondes pour être réactif
            while wait_seconds > 0 and self._running:
                sleep_time = min(60, wait_seconds)
                time.sleep(sleep_time)
                wait_seconds -= sleep_time
            
            return True
        
        return True
    
    def _monitor_inactivity(self):
        """Monitore les périodes d'inactivité"""
        while self._running:
            self._is_inactive_period = self._is_inactive_time()
            time.sleep(60)  # Vérifier toutes les minutes
    
    def _is_inactive_time(self) -> bool:
        """
        Vérifie si on est en période d'inactivité
        
        Returns:
            True si période inactive
        """
        now = datetime.now()
        current_hour = now.hour
        
        if self.config.inactivity_start_hour <= self.config.inactivity_end_hour:
            return (self.config.inactivity_start_hour <= current_hour < self.config.inactivity_end_hour)
        else:
            return (current_hour >= self.config.inactivity_start_hour or 
                   current_hour < self.config.inactivity_end_hour)
    
    def random_sleep(self, min_seconds: float = 1.0, max_seconds: float = 5.0):
        """
        Pause aléatoire entre deux actions
        
        Args:
            min_seconds: Minimum en secondes
            max_seconds: Maximum en secondes
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def micro_sleep(self):
        """
        Micro-pause pour les opérations rapides (100-500ms)
        """
        delay = random.uniform(0.1, 0.5)
        time.sleep(delay)
    
    def should_pause(self) -> bool:
        """
        Détermine si une pause doit être effectuée
        
        Returns:
            True si pause recommandée
        """
        # En mode APT, pauses fréquentes
        if self.config.apt_mode:
            return random.random() < 0.3  # 30% de chance
        
        return random.random() < 0.1  # 10% de chance
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du moteur
        
        Returns:
            Dictionnaire des statistiques
        """
        return {
            **self._stats,
            "current_delay_pattern": self._current_delay_pattern,
            "min_delay": self.config.min_delay,
            "max_delay": self.config.max_delay,
            "jitter": self.config.jitter,
            "proxy_rotation": self.config.proxy_rotation,
            "proxy_count": len(self.config.proxy_list),
            "user_agent_count": len(self.config.user_agent_list),
            "user_agent_rotation": self.config.user_agent_rotation,
            "apt_mode": self.config.apt_mode,
            "is_inactive_period": self._is_inactive_period
        }
    
    def reset_stats(self):
        """Réinitialise les statistiques"""
        self._stats = {
            "total_delays": 0,
            "total_delay_time": 0,
            "proxy_switches": 0,
            "user_agent_switches": 0,
            "requests_delayed": 0,
            "rate_limit_hits": 0
        }
    
    def add_proxy(self, proxy_url: str):
        """
        Ajoute un proxy à la liste
        
        Args:
            proxy_url: URL du proxy (ex: http://127.0.0.1:8080)
        """
        if proxy_url not in self.config.proxy_list:
            self.config.proxy_list.append(proxy_url)
    
    def remove_proxy(self, proxy_url: str):
        """Supprime un proxy de la liste"""
        if proxy_url in self.config.proxy_list:
            self.config.proxy_list.remove(proxy_url)
    
    def add_user_agent(self, user_agent: str):
        """
        Ajoute un User-Agent à la liste
        
        Args:
            user_agent: User-Agent à ajouter
        """
        if user_agent not in self.config.user_agent_list:
            self.config.user_agent_list.append(user_agent)
    
    def enable_apt_mode(self):
        """Active le mode APT complet"""
        self.config.apt_mode = True
        self.set_delay_pattern('apt')
        self.config.randomize_request_order = True
        self.config.add_random_parameters = True
        self.config.request_spoofing = True
        self.config.respect_rate_limits = True
    
    def disable_apt_mode(self):
        """Désactive le mode APT"""
        self.config.apt_mode = False
        self.set_delay_pattern('medium')
    
    def stop(self):
        """Arrête le moteur de furtivité"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)


# Alias pour compatibilité
StealthEngine = StealthEngine


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test du Stealth Engine")
    print("=" * 60)
    
    # Créer une instance
    stealth = StealthEngine()
    
    # Configurer le mode APT
    stealth.enable_apt_mode()
    
    print(f"\n📊 Configuration:")
    print(f"   Min delay: {stealth.config.min_delay}s")
    print(f"   Max delay: {stealth.config.max_delay}s")
    print(f"   Jitter: {stealth.config.jitter}")
    print(f"   APT Mode: {stealth.config.apt_mode}")
    
    # Tester les délais
    print("\n⏱️ Test des délais:")
    for i in range(3):
        start = time.time()
        stealth.apply_delay()
        elapsed = time.time() - start
        print(f"   Délai {i+1}: {elapsed:.2f}s")
    
    # Tester les headers
    print("\n📋 Headers générés:")
    headers = stealth.get_headers()
    for key, value in headers.items():
        print(f"   {key}: {value}")
    
    # Statistiques
    print("\n📈 Statistiques:")
    stats = stealth.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Arrêter
    stealth.stop()
    print("\n✅ Test terminé")