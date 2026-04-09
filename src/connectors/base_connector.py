#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe de base abstraite pour tous les connecteurs RedForge
Définit l'interface standard que chaque outil doit implémenter
Version avec support furtif, APT et gestion avancée
"""

import subprocess
import json
import time
import random
import tempfile
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import shutil
import hashlib

class BaseConnector(ABC):
    """Classe abstraite pour tous les connecteurs d'outils avec support furtif"""
    
    def __init__(self, tool_path: Optional[str] = None):
        """
        Initialise le connecteur
        
        Args:
            tool_path: Chemin personnalisé vers l'exécutable de l'outil
        """
        self.tool_name = self.__class__.__name__.replace('Connector', '').lower()
        self.tool_path = tool_path or self._find_tool()
        self.available = self.tool_path is not None
        self.stealth_config = {
            'delay': (0.5, 1.5),
            'threads': 10,
            'timeout': 30,
            'stealth': False,
            'random_delays': True,
            'jitter': 0.3
        }
        self.apt_mode = False
        self.last_execution_time = 0
        self.execution_history = []
        
        # Configuration de proxy (pour mode furtif)
        self.proxies = []
        self.current_proxy_index = 0
        self.proxy_rotation = False
        
        # User agents pour rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Métriques
        self.scans_count = 0
        self.total_execution_time = 0
    
    @abstractmethod
    def _find_tool(self) -> Optional[str]:
        """Trouve le chemin de l'exécutable de l'outil"""
        pass
    
    @abstractmethod
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute un scan sur la cible
        
        Args:
            target: Cible à scanner (URL, IP, etc.)
            **kwargs: Paramètres spécifiques à l'outil
            
        Returns:
            Dictionnaire contenant les résultats du scan
        """
        pass
    
    @abstractmethod
    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse la sortie brute de l'outil en structure JSON
        
        Args:
            output: Sortie brute de l'outil
            
        Returns:
            Dictionnaire structuré des résultats
        """
        pass
    
    def set_stealth_config(self, config: Dict[str, Any]):
        """
        Configure les paramètres de furtivité
        
        Args:
            config: Dictionnaire de configuration
                - delay: Tuple (min, max) en secondes
                - threads: Nombre de threads
                - timeout: Timeout global
                - stealth: Mode furtif actif
                - random_delays: Délais aléatoires
                - jitter: Facteur de variation
        """
        self.stealth_config.update(config)
    
    def set_apt_mode(self, enabled: bool = True):
        """
        Active/désactive le mode APT
        
        Args:
            enabled: État du mode APT
        """
        self.apt_mode = enabled
        if enabled:
            self.stealth_config['random_delays'] = True
            self.stealth_config['stealth'] = True
            self.stealth_config['delay'] = (5, 15)
    
    def set_proxy_rotation(self, proxies: List[str], enabled: bool = True):
        """
        Configure la rotation de proxies
        
        Args:
            proxies: Liste des proxies (format: 'http://host:port')
            enabled: Activer la rotation
        """
        self.proxies = proxies
        self.proxy_rotation = enabled
        self.current_proxy_index = 0
    
    def _get_next_proxy(self) -> Optional[str]:
        """Retourne le prochain proxy pour rotation"""
        if not self.proxy_rotation or not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy
    
    def _apply_stealth_delay(self):
        """Applique un délai furtif avant l'exécution"""
        if not self.stealth_config.get('random_delays', True):
            return
        
        min_delay, max_delay = self.stealth_config.get('delay', (0.5, 1.5))
        delay = random.uniform(min_delay, max_delay)
        
        # Ajouter du jitter en mode APT
        if self.apt_mode:
            jitter = delay * self.stealth_config.get('jitter', 0.3)
            delay += random.uniform(-jitter, jitter)
        
        # Assurer un délai minimum entre les exécutions
        elapsed = time.time() - self.last_execution_time
        if elapsed < delay:
            time.sleep(max(0, delay - elapsed))
        
        self.last_execution_time = time.time()
    
    def _get_random_user_agent(self) -> str:
        """Retourne un User-Agent aléatoire"""
        if not self.stealth_config.get('stealth', False):
            return self.user_agents[0]
        return random.choice(self.user_agents)
    
    def execute_command(self, cmd: List[str], timeout: int = 300, 
                       stealth: bool = True) -> Dict[str, Any]:
        """
        Exécute une commande système de manière sécurisée avec options furtives
        
        Args:
            cmd: Liste des arguments de la commande
            timeout: Timeout en secondes
            stealth: Appliquer les mesures furtives
            
        Returns:
            Dictionnaire avec stdout, stderr et code de retour
        """
        if not self.available:
            return {
                "success": False,
                "error": f"Outil {self.tool_name} non disponible",
                "stdout": "",
                "stderr": "",
                "execution_time": 0
            }
        
        # Appliquer le délai furtif
        if stealth:
            self._apply_stealth_delay()
        
        # Ajouter les options furtives si nécessaire
        if self.stealth_config.get('stealth', False) and stealth:
            cmd = self._add_stealth_options(cmd)
        
        start_time = time.time()
        
        try:
            env = os.environ.copy()
            
            # Ajouter User-Agent pour les commandes HTTP
            if any('curl' in str(c).lower() or 'wget' in str(c).lower() for c in cmd):
                env['HTTP_USER_AGENT'] = self._get_random_user_agent()
            
            # Configurer le proxy si nécessaire
            proxy = self._get_next_proxy()
            if proxy:
                env['HTTP_PROXY'] = proxy
                env['HTTPS_PROXY'] = proxy
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            
            execution_time = time.time() - start_time
            
            # Enregistrer l'exécution
            self.execution_history.append({
                'timestamp': datetime.now().isoformat(),
                'command': ' '.join(cmd),
                'execution_time': execution_time,
                'returncode': result.returncode
            })
            
            self.scans_count += 1
            self.total_execution_time += execution_time
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "execution_time": execution_time
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Commande timeout après {timeout}s",
                "stdout": "",
                "stderr": "",
                "execution_time": timeout
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
                "execution_time": time.time() - start_time
            }
    
    def _add_stealth_options(self, cmd: List[str]) -> List[str]:
        """
        Ajoute des options furtives à la commande
        
        Args:
            cmd: Commande originale
            
        Returns:
            Commande avec options furtives
        """
        # Options communes pour différents outils
        stealth_options = {
            'nmap': ['-T2', '--randomize-hosts', '--scan-delay', '1s'],
            'sqlmap': ['--random-agent', '--delay=1', '--time-sec=2'],
            'nikto': ['-maxtime', '60', '-Tuning', '123'],
            'dirb': ['-z', '1000'],
            'gobuster': ['-q', '--delay', '1s'],
            'ffuf': ['-ac', '-t', '10', '-s']
        }
        
        # Identifier l'outil par le nom de la commande
        cmd_base = os.path.basename(cmd[0]).lower()
        
        for tool, options in stealth_options.items():
            if tool in cmd_base:
                # Éviter les doublons
                for opt in options:
                    if opt not in cmd:
                        cmd.insert(1, opt)
                break
        
        return cmd
    
    def is_available(self) -> bool:
        """Vérifie si l'outil est disponible"""
        return self.available
    
    def get_version(self) -> Optional[str]:
        """Récupère la version de l'outil"""
        if not self.available:
            return None
        
        try:
            result = self.execute_command([self.tool_path, "--version"], stealth=False)
            if result["success"]:
                return result["stdout"].split('\n')[0]
        except:
            pass
        return None
    
    def _safe_path(self, path: str) -> Path:
        """Nettoie et sécurise un chemin de fichier"""
        return Path(path).resolve()
    
    def save_results(self, results: Dict[str, Any], output_file: str) -> bool:
        """Sauvegarde les résultats dans un fichier JSON"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'exécution"""
        return {
            "tool_name": self.tool_name,
            "available": self.available,
            "scans_count": self.scans_count,
            "total_execution_time": self.total_execution_time,
            "avg_execution_time": self.total_execution_time / self.scans_count if self.scans_count > 0 else 0,
            "apt_mode": self.apt_mode,
            "stealth_config": self.stealth_config,
            "last_execution": self.execution_history[-1] if self.execution_history else None
        }
    
    def create_temp_output_file(self, suffix: str = ".txt") -> str:
        """
        Crée un fichier temporaire pour la sortie de l'outil
        
        Args:
            suffix: Suffixe du fichier
            
        Returns:
            Chemin du fichier temporaire
        """
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=f"redforge_{self.tool_name}_")
        os.close(fd)
        return path
    
    def cleanup_temp_file(self, path: str):
        """
        Supprime un fichier temporaire
        
        Args:
            path: Chemin du fichier à supprimer
        """
        try:
            if os.path.exists(path):
                os.unlink(path)
        except Exception as e:
            pass  # Ignorer les erreurs de nettoyage
    
    def hash_target(self, target: str) -> str:
        """
        Génère un hash de la cible pour éviter les doublons
        
        Args:
            target: Cible
            
        Returns:
            Hash MD5
        """
        return hashlib.md5(target.encode()).hexdigest()[:16]
    
    def should_skip_scan(self, target: str, cache_duration: int = 3600) -> bool:
        """
        Vérifie si le scan doit être sauté (cache)
        
        Args:
            target: Cible
            cache_duration: Durée de cache en secondes
            
        Returns:
            True si le scan doit être sauté
        """
        # Implémentation à surcharger pour le caching
        return False
    
    def generate_report(self, results: Dict[str, Any], format: str = "json") -> str:
        """
        Génère un rapport dans différents formats
        
        Args:
            results: Résultats à formater
            format: Format de sortie (json, html, text)
            
        Returns:
            Rapport formaté
        """
        if format == "json":
            return json.dumps(results, indent=2, ensure_ascii=False)
        elif format == "html":
            return self._generate_html_report(results)
        else:
            return self._generate_text_report(results)
    
    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """Génère un rapport HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>RedForge - Rapport {self.tool_name}</title>
            <style>
                body {{ font-family: monospace; background: #1a202c; color: #68d391; padding: 20px; }}
                h1 {{ color: #f56565; }}
                .vulnerability {{ border-left: 3px solid #f56565; margin: 10px 0; padding: 10px; background: #2d3748; }}
                .critical {{ color: #f56565; }}
                .high {{ color: #ed8936; }}
                .medium {{ color: #ecc94b; }}
                .low {{ color: #48bb78; }}
            </style>
        </head>
        <body>
            <h1>🔴 Rapport {self.tool_name}</h1>
            <p>Cible: {results.get('target', 'N/A')}</p>
            <p>Date: {datetime.now().isoformat()}</p>
            <p>Mode furtif: {self.apt_mode}</p>
        </body>
        </html>
        """
        return html
    
    def _generate_text_report(self, results: Dict[str, Any]) -> str:
        """Génère un rapport texte"""
        import json
        return json.dumps(results, indent=2, ensure_ascii=False)


# Fonction utilitaire pour vérifier l'installation des outils
def check_tool_installation(tool_name: str, paths: List[str]) -> Optional[str]:
    """
    Vérifie si un outil est installé
    
    Args:
        tool_name: Nom de l'outil
        paths: Chemins possibles
        
    Returns:
        Chemin de l'outil ou None
    """
    # Vérifier dans le PATH
    which_path = shutil.which(tool_name)
    if which_path:
        return which_path
    
    # Vérifier dans les chemins spécifiques
    for path in paths:
        full_path = Path(path) / tool_name
        if full_path.exists() and full_path.is_file():
            return str(full_path)
        
        # Avec extension .exe sur Windows
        if os.name == 'nt':
            full_path_exe = Path(path) / f"{tool_name}.exe"
            if full_path_exe.exists():
                return str(full_path_exe)
    
    return None