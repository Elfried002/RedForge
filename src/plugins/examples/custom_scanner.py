#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin de scanner personnalisé pour RedForge
Exemple de scanner pour une technologie spécifique
Version avec support furtif, APT et détection avancée
"""

import re
import time
import random
import json
import requests
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

from src.plugins.plugin_manager import ScannerPlugin, PluginType


class CustomScanner(ScannerPlugin):
    """
    Scanner personnalisé pour WordPress avec support furtif
    Détecte les vulnérabilités, plugins, thèmes et configurations sensibles
    """
    
    def __init__(self):
        super().__init__()
        self.stealth_mode = False
        self.apt_mode = False
        self.stealth_config = {
            'delay_min': 1,
            'delay_max': 3,
            'random_delays': True,
            'jitter': 0.3
        }
        self.session = None
    
    def get_name(self) -> str:
        return "CustomWordPressScanner"
    
    def get_version(self) -> str:
        return "2.0.0"
    
    def get_author(self) -> str:
        return "RedForge Team"
    
    def get_description(self) -> str:
        return "Scanner avancé pour WordPress avec support furtif et APT"
    
    def get_type(self) -> PluginType:
        return PluginType.SCANNER
    
    def get_scanner_name(self) -> str:
        return "Advanced WordPress Vulnerability Scanner"
    
    def get_dependencies(self) -> List[str]:
        return ["beautifulsoup4"]
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "timeout": {
                "type": "integer",
                "default": 15,
                "description": "Timeout en secondes"
            },
            "threads": {
                "type": "integer",
                "default": 5,
                "description": "Nombre de threads"
            },
            "check_plugins": {
                "type": "boolean",
                "default": True,
                "description": "Vérifier les plugins"
            },
            "check_themes": {
                "type": "boolean",
                "default": True,
                "description": "Vérifier les thèmes"
            },
            "check_users": {
                "type": "boolean",
                "default": True,
                "description": "Énumérer les utilisateurs"
            },
            "deep_scan": {
                "type": "boolean",
                "default": False,
                "description": "Scan approfondi"
            },
            "stealth_mode": {
                "type": "boolean",
                "default": False,
                "description": "Activer le mode furtif"
            },
            "apt_mode": {
                "type": "boolean",
                "default": False,
                "description": "Activer le mode APT"
            },
            "delay_min": {
                "type": "integer",
                "default": 1,
                "description": "Délai minimum entre requêtes"
            },
            "delay_max": {
                "type": "integer",
                "default": 5,
                "description": "Délai maximum entre requêtes"
            }
        }
    
    def on_load(self) -> bool:
        """Initialisation du scanner"""
        self.logger.info(f"Chargement du scanner {self.get_name()} v{self.get_version()}")
        
        # Charger la configuration
        self.load_config()
        
        # Initialiser les modes
        self.stealth_mode = self.config.get('stealth_mode', False)
        self.apt_mode = self.config.get('apt_mode', False)
        
        # Initialiser la session
        self.session = requests.Session()
        
        # Initialiser les bases de données
        self.init_vulnerability_db()
        self.init_plugin_list()
        self.init_theme_list()
        
        self.logger.success(f"Scanner chargé - Mode furtif: {self.stealth_mode}, APT: {self.apt_mode}")
        return True
    
    def on_unload(self) -> bool:
        """Nettoyage du scanner"""
        if self.session:
            self.session.close()
        self.logger.info(f"Déchargement du scanner {self.get_name()}")
        return True
    
    def _apply_stealth_delay(self):
        """Applique un délai furtif"""
        if self.stealth_mode:
            min_delay = self.config.get('delay_min', 1)
            max_delay = self.config.get('delay_max', 5)
            delay = random.uniform(min_delay, max_delay)
            
            if self.apt_mode:
                jitter = delay * 0.3
                delay += random.uniform(-jitter, jitter)
            
            time.sleep(max(0, delay))
    
    def _get_headers(self) -> Dict[str, str]:
        """Génère des headers furtifs"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        if self.stealth_mode:
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0'
            ]
            headers['User-Agent'] = random.choice(user_agents)
        
        return headers
    
    def init_vulnerability_db(self):
        """Initialise la base de données des vulnérabilités"""
        self.vulnerabilities = {
            'wordpress': {
                'core': [
                    {
                        'id': 'CVE-2023-5360',
                        'title': 'Vulnérabilité XSS dans WordPress core',
                        'versions': ['<6.3.2'],
                        'severity': 'HIGH',
                        'description': 'Cross-Site Scripting dans le core WordPress',
                        'cwe': 'CWE-79'
                    },
                    {
                        'id': 'CVE-2023-2745',
                        'title': 'Injection SQL dans WordPress',
                        'versions': ['<6.2.1'],
                        'severity': 'CRITICAL',
                        'description': 'Injection SQL dans les commentaires',
                        'cwe': 'CWE-89'
                    },
                    {
                        'id': 'CVE-2023-22622',
                        'title': 'XSS dans le composant de médias',
                        'versions': ['<6.1.2'],
                        'severity': 'MEDIUM',
                        'description': 'Cross-Site Scripting dans la bibliothèque de médias',
                        'cwe': 'CWE-79'
                    }
                ],
                'plugins': {},
                'themes': {}
            }
        }
    
    def init_plugin_list(self):
        """Initialise la liste des plugins populaires"""
        self.popular_plugins = {
            'woocommerce': {
                'name': 'WooCommerce',
                'vulnerabilities': [
                    {
                        'id': 'CVE-2023-28121',
                        'title': 'Injection SQL dans WooCommerce',
                        'versions': ['<7.5.0'],
                        'severity': 'CRITICAL',
                        'description': 'Injection SQL dans la gestion des commandes'
                    }
                ]
            },
            'elementor': {
                'name': 'Elementor',
                'vulnerabilities': [
                    {
                        'id': 'CVE-2023-32243',
                        'title': 'RCE dans Elementor Pro',
                        'versions': ['<3.12.0'],
                        'severity': 'CRITICAL',
                        'description': 'Exécution de code à distance via Elementor'
                    }
                ]
            },
            'yoast-seo': {
                'name': 'Yoast SEO',
                'vulnerabilities': [
                    {
                        'id': 'CVE-2023-25041',
                        'title': 'XSS dans Yoast SEO',
                        'versions': ['<20.4'],
                        'severity': 'MEDIUM',
                        'description': 'Cross-Site Scripting dans l\'interface admin'
                    }
                ]
            },
            'contact-form-7': {
                'name': 'Contact Form 7',
                'vulnerabilities': [
                    {
                        'id': 'CVE-2023-24416',
                        'title': 'File Upload dans Contact Form 7',
                        'versions': ['<5.7.4'],
                        'severity': 'HIGH',
                        'description': 'Upload de fichiers non restreint'
                    }
                ]
            },
            'wp-rocket': {
                'name': 'WP Rocket',
                'vulnerabilities': []
            },
            'wordfence': {
                'name': 'Wordfence Security',
                'vulnerabilities': []
            }
        }
    
    def init_theme_list(self):
        """Initialise la liste des thèmes populaires"""
        self.popular_themes = {
            'astra': {
                'name': 'Astra',
                'vulnerabilities': []
            },
            'oceanwp': {
                'name': 'OceanWP',
                'vulnerabilities': []
            },
            'generatepress': {
                'name': 'GeneratePress',
                'vulnerabilities': []
            },
            'neve': {
                'name': 'Neve',
                'vulnerabilities': []
            },
            'kadence': {
                'name': 'Kadence',
                'vulnerabilities': []
            },
            'blocksy': {
                'name': 'Blocksy',
                'vulnerabilities': []
            }
        }
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute le scan WordPress
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
            
        Returns:
            Résultats du scan
        """
        self.logger.info(f"Scan WordPress de {target}")
        if self.apt_mode:
            self.logger.info("Mode APT activé - Scan discret")
        
        results = {
            "target": target,
            "is_wordpress": False,
            "version": None,
            "vulnerabilities": [],
            "plugins": [],
            "themes": [],
            "users": [],
            "files": [],
            "recommendations": [],
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode
        }
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        # Détection de WordPress
        self._apply_stealth_delay()
        detection = self._detect_wordpress(target)
        
        if not detection['is_wordpress']:
            results["message"] = "WordPress non détecté"
            return results
        
        results["is_wordpress"] = True
        results["version"] = detection['version']
        
        # Vérification des vulnérabilités core
        if results["version"]:
            core_vulns = self._check_core_vulnerabilities(results["version"])
            results["vulnerabilities"].extend(core_vulns)
        
        # Scan des plugins
        if self.config.get('check_plugins', True):
            self._apply_stealth_delay()
            plugins = self._scan_plugins(target)
            results["plugins"] = plugins
            
            for plugin in plugins:
                if plugin.get('vulnerabilities'):
                    results["vulnerabilities"].extend(plugin['vulnerabilities'])
        
        # Scan des thèmes
        if self.config.get('check_themes', True):
            self._apply_stealth_delay()
            themes = self._scan_themes(target)
            results["themes"] = themes
            
            for theme in themes:
                if theme.get('vulnerabilities'):
                    results["vulnerabilities"].extend(theme['vulnerabilities'])
        
        # Énumération des utilisateurs
        if self.config.get('check_users', True):
            self._apply_stealth_delay()
            results["users"] = self._enumerate_users(target)
        
        # Scan des fichiers sensibles
        results["files"] = self._scan_sensitive_files(target)
        
        # Scan approfondi
        if self.config.get('deep_scan', False) and not self.apt_mode:
            self._apply_stealth_delay()
            deep_results = self._deep_scan(target)
            results["deep_scan"] = deep_results
        
        # Génération des recommandations
        results["recommendations"] = self._generate_recommendations(results)
        
        # Résumé
        results["summary"] = self._generate_summary(results)
        
        return results
    
    def _detect_wordpress(self, target: str) -> Dict[str, Any]:
        """Détecte la présence de WordPress"""
        result = {
            'is_wordpress': False,
            'version': None
        }
        
        # Vérifier les fichiers caractéristiques
        wp_paths = [
            '/wp-content/',
            '/wp-includes/',
            '/wp-admin/',
            '/wp-login.php',
            '/xmlrpc.php',
            '/wp-json/',
            '/readme.html',
            '/license.txt'
        ]
        
        for path in wp_paths:
            test_url = urljoin(target, path)
            try:
                headers = self._get_headers()
                response = self.session.get(
                    test_url,
                    headers=headers,
                    timeout=self.config.get('timeout', 15),
                    verify=False
                )
                
                if response.status_code == 200:
                    result['is_wordpress'] = True
                    break
                    
            except Exception:
                continue
        
        if result['is_wordpress']:
            result['version'] = self._detect_wordpress_version(target)
        
        return result
    
    def _detect_wordpress_version(self, target: str) -> Optional[str]:
        """Détecte la version de WordPress"""
        # Méthode 1: readme.html
        readme_url = urljoin(target, '/readme.html')
        try:
            headers = self._get_headers()
            response = self.session.get(readme_url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                match = re.search(r'Version\s+([0-9.]+)', response.text, re.IGNORECASE)
                if match:
                    return match.group(1)
        except:
            pass
        
        # Méthode 2: générateur meta
        try:
            headers = self._get_headers()
            response = self.session.get(target, headers=headers, timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            generator = soup.find('meta', {'name': 'generator'})
            if generator and 'WordPress' in generator.get('content', ''):
                match = re.search(r'([0-9.]+)', generator.get('content', ''))
                if match:
                    return match.group(1)
        except:
            pass
        
        # Méthode 3: fichiers CSS/JS
        css_url = urljoin(target, '/wp-content/themes/twentytwentyfour/style.css')
        try:
            headers = self._get_headers()
            response = self.session.get(css_url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                match = re.search(r'Version:\s+([0-9.]+)', response.text, re.IGNORECASE)
                if match:
                    return match.group(1)
        except:
            pass
        
        return None
    
    def _check_core_vulnerabilities(self, version: str) -> List[Dict[str, Any]]:
        """Vérifie les vulnérabilités du core WordPress"""
        vulnerabilities = []
        
        for vuln in self.vulnerabilities['wordpress']['core']:
            for affected_range in vuln['versions']:
                if self._version_in_range(version, affected_range):
                    vulnerabilities.append({
                        "type": "wordpress_core",
                        "id": vuln['id'],
                        "title": vuln['title'],
                        "severity": vuln['severity'],
                        "description": vuln['description'],
                        "affected_version": version,
                        "fixed_in": affected_range.replace('<', ''),
                        "cwe": vuln.get('cwe', 'N/A')
                    })
                    break
        
        return vulnerabilities
    
    def _version_in_range(self, version: str, version_range: str) -> bool:
        """Vérifie si une version est dans une plage"""
        if version_range.startswith('<'):
            target = version_range[1:]
            return self._compare_versions(version, target) < 0
        elif version_range.startswith('<='):
            target = version_range[2:]
            return self._compare_versions(version, target) <= 0
        elif version_range.startswith('>'):
            target = version_range[1:]
            return self._compare_versions(version, target) > 0
        elif version_range.startswith('>='):
            target = version_range[2:]
            return self._compare_versions(version, target) >= 0
        elif '-' in version_range:
            low, high = version_range.split('-')
            return (self._compare_versions(version, low) >= 0 and 
                    self._compare_versions(version, high) <= 0)
        else:
            return version == version_range
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare deux versions"""
        def normalize(v):
            return [int(x) for x in v.split('.')]
        
        try:
            v1_parts = normalize(v1)
            v2_parts = normalize(v2)
            
            for i in range(max(len(v1_parts), len(v2_parts))):
                v1_val = v1_parts[i] if i < len(v1_parts) else 0
                v2_val = v2_parts[i] if i < len(v2_parts) else 0
                
                if v1_val < v2_val:
                    return -1
                elif v1_val > v2_val:
                    return 1
            return 0
        except:
            return 0
    
    def _scan_plugins(self, target: str) -> List[Dict[str, Any]]:
        """Scanne les plugins WordPress installés"""
        plugins = []
        
        # Limiter les plugins en mode APT
        plugin_list = list(self.popular_plugins.items())
        if self.apt_mode:
            plugin_list = plugin_list[:5]
        
        for plugin_slug, plugin_info in plugin_list:
            self._apply_stealth_delay()
            
            plugin_path = f'/wp-content/plugins/{plugin_slug}/'
            test_url = urljoin(target, plugin_path)
            
            try:
                headers = self._get_headers()
                response = self.session.get(
                    test_url,
                    headers=headers,
                    timeout=self.config.get('timeout', 15),
                    verify=False
                )
                
                if response.status_code != 404:
                    plugin_data = {
                        "name": plugin_info['name'],
                        "slug": plugin_slug,
                        "path": plugin_path,
                        "detected": True,
                        "version": self._detect_plugin_version(target, plugin_slug),
                        "vulnerabilities": []
                    }
                    
                    # Vérifier les vulnérabilités
                    for vuln in plugin_info.get('vulnerabilities', []):
                        if plugin_data['version'] != 'unknown':
                            if self._version_in_range(plugin_data['version'], vuln['versions'][0]):
                                plugin_data["vulnerabilities"].append({
                                    "id": vuln['id'],
                                    "title": vuln['title'],
                                    "severity": vuln['severity'],
                                    "description": vuln.get('description', '')
                                })
                    
                    plugins.append(plugin_data)
                    if not self.stealth_mode:
                        self.logger.info(f"Plugin détecté: {plugin_info['name']}")
                    
            except Exception:
                continue
        
        return plugins
    
    def _detect_plugin_version(self, target: str, plugin_slug: str) -> str:
        """Détecte la version d'un plugin"""
        # Lire le fichier readme.txt
        readme_url = urljoin(target, f'/wp-content/plugins/{plugin_slug}/readme.txt')
        try:
            headers = self._get_headers()
            response = self.session.get(readme_url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                match = re.search(r'Stable tag:\s+([0-9.]+)', response.text, re.IGNORECASE)
                if match:
                    return match.group(1)
        except:
            pass
        
        # Lire le fichier du plugin
        plugin_file = urljoin(target, f'/wp-content/plugins/{plugin_slug}/{plugin_slug}.php')
        try:
            headers = self._get_headers()
            response = self.session.get(plugin_file, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                match = re.search(r'Version:\s+([0-9.]+)', response.text, re.IGNORECASE)
                if match:
                    return match.group(1)
        except:
            pass
        
        return "unknown"
    
    def _scan_themes(self, target: str) -> List[Dict[str, Any]]:
        """Scanne les thèmes WordPress installés"""
        themes = []
        
        # Limiter les thèmes en mode APT
        theme_list = list(self.popular_themes.items())
        if self.apt_mode:
            theme_list = theme_list[:3]
        
        for theme_slug, theme_info in theme_list:
            self._apply_stealth_delay()
            
            theme_path = f'/wp-content/themes/{theme_slug}/'
            test_url = urljoin(target, theme_path)
            
            try:
                headers = self._get_headers()
                response = self.session.get(
                    test_url,
                    headers=headers,
                    timeout=self.config.get('timeout', 15),
                    verify=False
                )
                
                if response.status_code != 404:
                    theme_data = {
                        "name": theme_info['name'],
                        "slug": theme_slug,
                        "path": theme_path,
                        "detected": True,
                        "version": self._detect_theme_version(target, theme_slug),
                        "vulnerabilities": theme_info.get('vulnerabilities', [])
                    }
                    
                    themes.append(theme_data)
                    if not self.stealth_mode:
                        self.logger.info(f"Thème détecté: {theme_info['name']}")
                    
            except Exception:
                continue
        
        return themes
    
    def _detect_theme_version(self, target: str, theme_slug: str) -> str:
        """Détecte la version d'un thème"""
        style_url = urljoin(target, f'/wp-content/themes/{theme_slug}/style.css')
        try:
            headers = self._get_headers()
            response = self.session.get(style_url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                match = re.search(r'Version:\s+([0-9.]+)', response.text, re.IGNORECASE)
                if match:
                    return match.group(1)
        except:
            pass
        
        return "unknown"
    
    def _enumerate_users(self, target: str) -> List[Dict[str, Any]]:
        """Énumère les utilisateurs WordPress"""
        users = []
        
        # Méthode 1: API REST
        rest_url = urljoin(target, '/wp-json/wp/v2/users')
        try:
            headers = self._get_headers()
            response = self.session.get(rest_url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                data = response.json()
                for user in data[:10]:  # Limiter
                    users.append({
                        "id": user.get('id'),
                        "name": user.get('name'),
                        "slug": user.get('slug'),
                        "link": user.get('link')
                    })
        except:
            pass
        
        # Méthode 2: Auteur des articles
        if not users:
            try:
                headers = self._get_headers()
                response = self.session.get(target, headers=headers, timeout=10, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')
                author_links = soup.find_all('a', href=re.compile(r'/author/'))
                for link in author_links[:10]:
                    username = link.get('href', '').split('/')[-2]
                    if username and username not in [u.get('slug') for u in users]:
                        users.append({
                            "name": link.text,
                            "slug": username,
                            "link": link.get('href')
                        })
            except:
                pass
        
        return users
    
    def _scan_sensitive_files(self, target: str) -> List[Dict[str, Any]]:
        """Scanne les fichiers sensibles WordPress"""
        sensitive_files = [
            '/wp-config.php',
            '/wp-config.php.bak',
            '/wp-config.php.save',
            '/wp-config.old',
            '/.htaccess',
            '/wp-content/debug.log',
            '/wp-content/uploads/',
            '/wp-admin/install.php',
            '/wp-admin/setup-config.php',
            '/wp-content/backup-db/',
            '/backup/',
            '/old/'
        ]
        
        found_files = []
        
        for file_path in sensitive_files:
            self._apply_stealth_delay()
            test_url = urljoin(target, file_path)
            try:
                headers = self._get_headers()
                response = self.session.get(
                    test_url,
                    headers=headers,
                    timeout=self.config.get('timeout', 15),
                    verify=False
                )
                
                if response.status_code == 200:
                    found_files.append({
                        "path": file_path,
                        "status": "accessible",
                        "size": len(response.content)
                    })
                    if not self.stealth_mode:
                        self.logger.warning(f"Fichier sensible accessible: {file_path}")
                    
                elif response.status_code == 403:
                    found_files.append({
                        "path": file_path,
                        "status": "restricted",
                        "message": "Accès interdit mais existe"
                    })
                    
            except Exception:
                continue
        
        return found_files
    
    def _deep_scan(self, target: str) -> Dict[str, Any]:
        """Scan approfondi supplémentaire"""
        deep_results = {
            "xmlrpc_enabled": False,
            "directory_listing": [],
            "admin_users": [],
            "login_page": None
        }
        
        # Vérifier XML-RPC
        xmlrpc_url = urljoin(target, '/xmlrpc.php')
        try:
            headers = self._get_headers()
            data = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>'
            response = self.session.post(
                xmlrpc_url,
                data=data,
                headers=headers,
                timeout=10,
                verify=False
            )
            if response.status_code == 200 and 'methodResponse' in response.text:
                deep_results["xmlrpc_enabled"] = True
        except:
            pass
        
        # Vérifier le directory listing
        dirs_to_check = ['/wp-content/uploads/', '/wp-content/plugins/', '/wp-content/themes/']
        for dir_path in dirs_to_check:
            test_url = urljoin(target, dir_path)
            try:
                headers = self._get_headers()
                response = self.session.get(test_url, headers=headers, timeout=10, verify=False)
                if 'Index of' in response.text or 'Parent Directory' in response.text:
                    deep_results["directory_listing"].append(dir_path)
            except:
                continue
        
        # Vérifier la page de login
        login_url = urljoin(target, '/wp-login.php')
        try:
            headers = self._get_headers()
            response = self.session.get(login_url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                deep_results["login_page"] = login_url
        except:
            pass
        
        return deep_results
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur les résultats"""
        recommendations = []
        
        # Recommandations core
        if results.get('version'):
            for vuln in results.get('vulnerabilities', []):
                if vuln.get('type') == 'wordpress_core':
                    recommendations.append(
                        f"Mettre à jour WordPress vers la version {vuln.get('fixed_in')} "
                        f"pour corriger {vuln.get('id')} ({vuln.get('title')})"
                    )
        
        # Recommandations plugins
        for plugin in results.get('plugins', []):
            if plugin.get('vulnerabilities'):
                for vuln in plugin.get('vulnerabilities', []):
                    recommendations.append(
                        f"Mettre à jour le plugin {plugin.get('name')} vers la dernière version "
                        f"pour corriger {vuln.get('id')}"
                    )
        
        # Recommandations fichiers sensibles
        for file in results.get('files', []):
            if file.get('status') == 'accessible':
                recommendations.append(
                    f"Restreindre l'accès au fichier {file.get('path')}"
                )
        
        # Recommandations générales
        deep_scan = results.get('deep_scan', {})
        if deep_scan.get('xmlrpc_enabled'):
            recommendations.append("Désactiver XML-RPC si non utilisé (ajouter au fichier .htaccess)")
        
        if deep_scan.get('directory_listing'):
            recommendations.append("Désactiver l'indexation des répertoires (Options -Indexes)")
        
        if results.get('users'):
            recommendations.append("Implémenter une politique de mots de passe forts")
        
        return list(set(recommendations))
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un résumé des résultats"""
        return {
            "is_wordpress": results.get('is_wordpress', False),
            "version": results.get('version'),
            "vulnerabilities_count": len(results.get('vulnerabilities', [])),
            "plugins_count": len(results.get('plugins', [])),
            "themes_count": len(results.get('themes', [])),
            "users_count": len(results.get('users', [])),
            "sensitive_files_count": len(results.get('files', [])),
            "critical_vulns": len([v for v in results.get('vulnerabilities', []) 
                                   if v.get('severity') == 'CRITICAL']),
            "high_vulns": len([v for v in results.get('vulnerabilities', []) 
                              if v.get('severity') == 'HIGH']),
            "stealth_mode": results.get('stealth_mode', False),
            "apt_mode": results.get('apt_mode', False)
        }
    
    def get_help(self) -> str:
        """Retourne l'aide du scanner"""
        mode_info = "APT" if self.apt_mode else ("Stealth" if self.stealth_mode else "Normal")
        
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║  {self.get_name()} v{self.get_version()} - Mode: {mode_info}          ║
╚══════════════════════════════════════════════════════════════════╝

📝 DESCRIPTION:
  {self.get_description()}

🎯 TYPE DE SCANNER:
  {self.get_scanner_name()}

⚙️ CONFIGURATION ACTUELLE:
  timeout: {self.config.get('timeout', 15)} secondes
  threads: {self.config.get('threads', 5)}
  check_plugins: {self.config.get('check_plugins', True)}
  check_themes: {self.config.get('check_themes', True)}
  check_users: {self.config.get('check_users', True)}
  deep_scan: {self.config.get('deep_scan', False)}
  stealth_mode: {self.stealth_mode}
  apt_mode: {self.apt_mode}
  delay_min: {self.config.get('delay_min', 1)}s
  delay_max: {self.config.get('delay_max', 5)}s

📊 FONCTIONNALITÉS:
  - Détection de WordPress
  - Vérification des vulnérabilités core (CVE)
  - Scan des plugins populaires
  - Scan des thèmes populaires
  - Énumération des utilisateurs
  - Détection de fichiers sensibles
  - Scan approfondi (XML-RPC, directory listing)

📋 EXEMPLES D'UTILISATION:

  # Scan standard
  plugin.scan(target="https://example.com")

  # Scan discret (mode furtif)
  plugin.set_config({{"stealth_mode": True}})
  plugin.scan(target="https://example.com")

  # Scan APT (ultra discret)
  plugin.set_config({{"apt_mode": True, "delay_min": 3, "delay_max": 10}})
  plugin.scan(target="https://example.com", deep_scan=False)

  # Scan avec plugins uniquement
  plugin.scan(target="https://example.com", check_plugins=True, check_themes=False)

  # Scan approfondi
  plugin.scan(target="https://example.com", deep_scan=True)

👤 AUTEUR:
  {self.get_author()}

📦 DÉPENDANCES:
  {', '.join(self.get_dependencies()) if self.get_dependencies() else 'Aucune'}
"""


# Point d'entrée pour tests
if __name__ == "__main__":
    scanner = CustomScanner()
    
    # Configurer le mode APT
    scanner.set_config({
        "stealth_mode": True,
        "apt_mode": True,
        "delay_min": 2,
        "delay_max": 5
    })
    
    print(scanner.get_help())
    
    # Test de chargement
    if scanner.on_load():
        print("✅ Scanner chargé avec succès")
    
    # Test du scan (simulé)
    # result = scanner.scan("https://example.com")
    # print(f"Scan result: {result}")