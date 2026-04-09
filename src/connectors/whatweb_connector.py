#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour WhatWeb - Détection de technologies web
Version avec support furtif, APT et détection avancée
"""

import re
import json
import random
from typing import Dict, Any, List, Optional
from pathlib import Path
from collections import defaultdict

from src.connectors.base_connector import BaseConnector


class WhatWebConnector(BaseConnector):
    """Connecteur avancé pour WhatWeb avec support furtif"""
    
    def __init__(self, tool_path: Optional[str] = None):
        """
        Initialise le connecteur WhatWeb
        
        Args:
            tool_path: Chemin personnalisé vers l'exécutable WhatWeb
        """
        super().__init__(tool_path)
        
        # Catégories de technologies
        self.tech_categories = {
            'cms': ['WordPress', 'Joomla', 'Drupal', 'Magento', 'PrestaShop', 'Shopify',
                    'WooCommerce', 'Ghost', 'OctoberCMS', 'Concrete5', 'Textpattern'],
            'framework': ['Laravel', 'Django', 'Rails', 'Spring', 'Symfony', 'CodeIgniter',
                          'CakePHP', 'Yii', 'Zend', 'Flask', 'Express', 'Next.js', 'Nuxt'],
            'frontend': ['React', 'Vue.js', 'Angular', 'jQuery', 'Bootstrap', 'Tailwind',
                         'Svelte', 'Backbone', 'Ember', 'Alpine.js', 'HTMX'],
            'server': ['Apache', 'Nginx', 'IIS', 'Tomcat', 'Node.js', 'Gunicorn',
                       'Caddy', 'Lighttpd', 'OpenResty'],
            'database': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'MariaDB', 'SQLite',
                         'Elasticsearch', 'Cassandra'],
            'language': ['PHP', 'Python', 'Ruby', 'Java', 'JavaScript', 'Go', 'Rust',
                         'C#', 'Perl'],
            'analytics': ['Google Analytics', 'Matomo', 'Hotjar', 'Segment', 'Mixpanel',
                          'Amplitude'],
            'security': ['Cloudflare', 'Sucuri', 'ModSecurity', 'Akamai', 'Incapsula',
                         'Wordfence', 'reCAPTCHA', 'hCaptcha']
        }
        
        # Patterns pour reconnaissance rapide (sans scan complet)
        self.quick_patterns = {
            'WordPress': r'wp-content|wp-includes|WordPress',
            'Drupal': r'Drupal|drupal.js|sites/default/files',
            'Joomla': r'Joomla|media/system/js',
            'Laravel': r'laravel|csrf-token|_token',
            'Django': r'csrftoken|django',
            'React': r'react|__REACT_DEVTOOLS_GLOBAL_HOOK__',
            'Vue.js': r'vue|data-v-',
            'Angular': r'ng-|angular',
            'Apache': r'Apache',
            'Nginx': r'nginx',
            'Cloudflare': r'cloudflare|cf-ray'
        }
    
    def _find_tool(self) -> Optional[str]:
        """Trouve l'exécutable WhatWeb"""
        import shutil
        
        paths = [
            "whatweb",
            "/usr/bin/whatweb",
            "/usr/local/bin/whatweb",
            "/opt/whatweb/whatweb"
        ]
        
        for path in paths:
            if path and shutil.which(path):
                return path
        
        # Vérifier le script Ruby
        ruby_script = shutil.which("ruby")
        if ruby_script:
            import subprocess
            try:
                result = subprocess.run(
                    ["find", "/usr", "-name", "whatweb"], 
                    capture_output=True, text=True, timeout=5
                )
                if result.stdout.strip():
                    return result.stdout.strip()
            except:
                pass
        
        return None
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Détecte les technologies web utilisées
        
        Args:
            target: URL cible
            **kwargs:
                - aggressive: Mode agressif (plus de tests)
                - verbose: Mode verbeux
                - stealth: Mode furtif (moins de requêtes)
                - timeout: Timeout en secondes
                - proxy: Proxy à utiliser
                - user_agent: User-Agent personnalisé
                - cookie: Cookie à utiliser
        """
        if not self.available:
            return {
                "success": False,
                "error": "WhatWeb non installé",
                "technologies": [],
                "apt_mode": self.apt_mode
            }
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        cmd = [self.tool_path]
        
        # Mode APT: réduire l'agressivité
        if self.apt_mode:
            kwargs['aggressive'] = False
            kwargs['stealth'] = True
            kwargs['verbose'] = False
        
        # Niveau d'agressivité
        if kwargs.get('aggressive'):
            cmd.append('-a')
        elif kwargs.get('stealth') or self.apt_mode:
            cmd.append('-s')  # Mode furtif
        
        if kwargs.get('verbose'):
            cmd.append('-v')
        elif self.apt_mode:
            cmd.append('-q')  # Mode silencieux
        
        # Format JSON (toujours)
        cmd.extend(['-j'])
        
        # User-Agent personnalisé
        user_agent = kwargs.get('user_agent')
        if user_agent:
            cmd.extend(['-U', user_agent])
        elif self.stealth_config.get('stealth', False):
            user_agent = self._get_random_user_agent()
            cmd.extend(['-U', user_agent])
        
        # Cookie
        cookie = kwargs.get('cookie')
        if cookie:
            cmd.extend(['-C', cookie])
        
        # Proxy
        proxy = kwargs.get('proxy')
        if proxy:
            cmd.extend(['-p', proxy])
        elif self.proxy_rotation:
            proxy = self._get_next_proxy()
            if proxy:
                cmd.extend(['-p', proxy])
        
        # Headers personnalisés
        headers = kwargs.get('headers', {})
        for key, value in headers.items():
            cmd.extend(['-H', f"{key}: {value}"])
        
        # Timeout
        cmd.extend(['-t', str(kwargs.get('timeout', 30))])
        
        # Follow redirects
        if kwargs.get('follow_redirect', True):
            cmd.append('-f')
        
        # Cible
        cmd.append(target)
        
        timeout = kwargs.get('execution_timeout', 60)
        
        # Exécution
        result = self.execute_command(cmd, timeout=timeout)
        
        if result["success"]:
            technologies = self.parse_output(result["stdout"])
            categorized = self._categorize_technologies(technologies)
            
            return {
                "success": True,
                "target": target,
                "technologies": technologies,
                "categorized": categorized,
                "count": len(technologies),
                "raw_output": result["stdout"],
                "execution_time": result.get("execution_time", 0),
                "command_used": ' '.join(cmd),
                "apt_mode": self.apt_mode
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Erreur lors de la détection"),
                "stderr": result.get("stderr", ""),
                "technologies": [],
                "apt_mode": self.apt_mode
            }
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse la sortie JSON de WhatWeb
        
        Args:
            output: Sortie brute de WhatWeb
            
        Returns:
            Liste des technologies détectées
        """
        technologies = []
        
        try:
            # WhatWeb peut sortir du JSON
            data = json.loads(output)
            
            if isinstance(data, list) and len(data) > 0:
                target_data = data[0]
                
                for plugin, info in target_data.items():
                    # Ignorer les métadonnées
                    if plugin in ['url', 'status', 'ip', 'port', 'method']:
                        continue
                    
                    tech = {
                        "name": plugin,
                        "version": self._extract_version(info),
                        "confidence": self._extract_confidence(info),
                        "certainty": self._extract_certainty(info),
                        "categories": self._find_categories(plugin)
                    }
                    
                    # Ajouter les détails supplémentaires
                    if isinstance(info, dict):
                        if 'strings' in info:
                            tech['evidence'] = info['strings'][:100] if info['strings'] else None
                        if 'account' in info:
                            tech['account'] = info['account']
                        if 'module' in info:
                            tech['module'] = info['module']
                        if 'poweredby' in info:
                            tech['powered_by'] = info['poweredby']
                    
                    technologies.append(tech)
                    
        except json.JSONDecodeError:
            # Si ce n'est pas du JSON, parser le texte
            technologies = self._parse_text_output(output)
        
        # Dédupliquer par nom
        unique_tech = {}
        for tech in technologies:
            name = tech['name'].lower()
            if name not in unique_tech or tech['confidence'] > unique_tech[name]['confidence']:
                unique_tech[name] = tech
        
        return list(unique_tech.values())
    
    def _extract_version(self, info: Any) -> str:
        """Extrait la version des informations"""
        if isinstance(info, dict):
            return info.get('version', 'unknown')
        elif isinstance(info, str) and re.search(r'\d+\.\d+', info):
            version_match = re.search(r'[\d\.]+', info)
            return version_match.group(0) if version_match else 'unknown'
        return 'unknown'
    
    def _extract_confidence(self, info: Any) -> int:
        """Extrait le niveau de confiance"""
        if isinstance(info, dict):
            return info.get('certainty', 100)
        return 100
    
    def _extract_certainty(self, info: Any) -> int:
        """Extrait le niveau de certitude"""
        if isinstance(info, dict):
            return info.get('certainty', 100)
        return 100
    
    def _find_categories(self, plugin: str) -> List[str]:
        """Trouve les catégories d'une technologie"""
        categories = []
        plugin_lower = plugin.lower()
        
        for category, techs in self.tech_categories.items():
            for tech in techs:
                if tech.lower() in plugin_lower or plugin_lower in tech.lower():
                    categories.append(category)
                    break
        
        return list(set(categories)) or ['other']
    
    def _categorize_technologies(self, technologies: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Catégorise les technologies détectées
        
        Args:
            technologies: Liste des technologies
            
        Returns:
            Dictionnaire des technologies par catégorie
        """
        categorized = defaultdict(list)
        
        for tech in technologies:
            for category in tech.get('categories', ['other']):
                categorized[category].append(tech)
        
        return dict(categorized)
    
    def _parse_text_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse la sortie texte de WhatWeb"""
        technologies = []
        
        # Pattern: [WordPress 5.8] [PHP 7.4] [Apache]
        pattern = r'\[([^\]]+)\]'
        
        for line in output.split('\n'):
            matches = re.findall(pattern, line)
            for match in matches:
                # Séparer le nom et la version
                parts = match.split()
                if parts:
                    name = parts[0]
                    version = parts[1] if len(parts) > 1 else 'unknown'
                    
                    technologies.append({
                        "name": name,
                        "version": version,
                        "confidence": 100,
                        "certainty": 100,
                        "categories": self._find_categories(name)
                    })
        
        return technologies
    
    def detect_cms(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Détection spécifique de CMS
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        result = self.scan(target, **kwargs)
        
        cms_detected = []
        for tech in result.get('technologies', []):
            if 'cms' in tech.get('categories', []):
                cms_detected.append(tech)
        
        return {
            "target": target,
            "cms_detected": len(cms_detected) > 0,
            "cms": cms_detected,
            "count": len(cms_detected)
        }
    
    def detect_frameworks(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Détection des frameworks frontend/backend
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        result = self.scan(target, **kwargs)
        
        frameworks = []
        for tech in result.get('technologies', []):
            if 'framework' in tech.get('categories', []) or 'frontend' in tech.get('categories', []):
                frameworks.append(tech)
        
        return {
            "target": target,
            "frameworks_detected": frameworks,
            "count": len(frameworks)
        }
    
    def quick_detect(self, target: str) -> Dict[str, Any]:
        """
        Détection rapide sans scan complet (basée sur headers et patterns)
        
        Args:
            target: URL cible
            
        Returns:
            Technologies détectées rapidement
        """
        import requests
        
        technologies = []
        
        try:
            headers = {}
            if self.stealth_config.get('stealth', False):
                headers['User-Agent'] = self._get_random_user_agent()
            
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            # Vérifier les patterns
            for tech, pattern in self.quick_patterns.items():
                if re.search(pattern, response.text, re.IGNORECASE):
                    technologies.append({
                        "name": tech,
                        "version": "unknown",
                        "confidence": 70,
                        "certainty": 70,
                        "categories": self._find_categories(tech),
                        "method": "quick_detect"
                    })
            
            # Vérifier les headers
            server = response.headers.get('Server', '')
            if server:
                technologies.append({
                    "name": server.split('/')[0] if '/' in server else server,
                    "version": server.split('/')[1] if '/' in server else 'unknown',
                    "confidence": 80,
                    "certainty": 80,
                    "categories": self._find_categories(server),
                    "method": "header"
                })
            
            x_powered = response.headers.get('X-Powered-By', '')
            if x_powered:
                technologies.append({
                    "name": x_powered.split('/')[0] if '/' in x_powered else x_powered,
                    "version": x_powered.split('/')[1] if '/' in x_powered else 'unknown',
                    "confidence": 85,
                    "certainty": 85,
                    "categories": self._find_categories(x_powered),
                    "method": "header"
                })
            
        except Exception as e:
            if not self.apt_mode:
                print(f"Erreur quick_detect: {e}")
        
        return {
            "target": target,
            "technologies": technologies,
            "count": len(technologies),
            "method": "quick_detect"
        }
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de version de WhatWeb
        
        Returns:
            Dictionnaire avec les informations de version
        """
        if not self.available:
            return {"available": False}
        
        result = self.execute_command([self.tool_path, "--version"], stealth=False)
        
        if result["success"]:
            version_line = result["stdout"].split('\n')[0] if result["stdout"] else ""
            return {
                "available": True,
                "version": version_line,
                "tool": "whatweb",
                "path": self.tool_path
            }
        
        return {"available": False, "error": result.get("error")}
    
    def get_tech_categories(self) -> Dict[str, List[str]]:
        """
        Retourne les catégories de technologies
        
        Returns:
            Dictionnaire des catégories
        """
        return self.tech_categories