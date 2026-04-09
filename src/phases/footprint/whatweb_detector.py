#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection de technologies web pour RedForge
Utilise WhatWeb, Wappalyzer et d'autres techniques pour identifier CMS, frameworks, etc.
Version avec support furtif, APT et détection avancée
"""

import subprocess
import re
import json
import time
import requests
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse
from collections import defaultdict

from src.core.stealth_engine import StealthEngine


class WhatWebDetector:
    """Détection avancée des technologies web avec support furtif"""
    
    def __init__(self):
        self.whatweb_path = self._find_whatweb()
        self.available = self.whatweb_path is not None
        self.stealth_mode = False
        self.apt_mode = False
        self.stealth_engine = StealthEngine()
        
        # Signatures pour détection HTML/Headers (fallback)
        self.cms_patterns = {
            'WordPress': [
                r'wp-content', r'wp-includes', r'wordpress', r'/wp-', r'wp-json',
                r'wp-login\.php', r'xmlrpc\.php', r'wp-cron\.php'
            ],
            'Joomla': [
                r'joomla', r'com_content', r'mosConfig', r'/media/system/js/',
                r'JFactory', r'JDatabase', r'index\.php\?option='
            ],
            'Drupal': [
                r'drupal', r'sites/all', r'drupal\.js', r'jquery\.ui\.drupal',
                r'core/misc', r'/sites/default/files'
            ],
            'Magento': [
                r'magento', r'skin/frontend', r'mage\.cookies', r'checkout',
                r'Magento_', r'static/version'
            ],
            'PrestaShop': [
                r'prestashop', r'ps\.googleanalytics', r'controllers/front',
                r'id_lang', r'id_currency'
            ],
            'Shopify': [
                r'shopify', r'myshopify\.com', r'cdn\.shopify', r'shopify-preview',
                r'/admin/'
            ],
            'Wix': [
                r'wix\.com', r'wixstatic\.com', r'wix-code', r'_wix'
            ],
            'Squarespace': [
                r'squarespace', r'static\.squarespace\.com', r'sqs'
            ]
        }
        
        self.js_libs_patterns = {
            'jQuery': r'jquery[.-]',
            'jQuery UI': r'jquery-ui',
            'React': r'react[.-]|react\.js|__REACT_DEVTOOLS_GLOBAL_HOOK__',
            'Vue.js': r'vue[.-]|vue\.js|data-v-',
            'Angular': r'angular[.-]|angular\.js|ng-',
            'Bootstrap': r'bootstrap[.-]|bootstrap\.css|bootstrap\.js',
            'Tailwind': r'tailwind|tw-',
            'FontAwesome': r'fontawesome|fa-',
            'Google Analytics': r'google-analytics|ga\.js|gtag',
            'Facebook SDK': r'connect\.facebook\.net|fb\.js',
            'Hotjar': r'hotjar\.com',
            'Matomo': r'matomo\.js|piwik\.js'
        }
        
        self.backend_patterns = {
            'Laravel': [r'laravel', r'csrf-token', r'_token'],
            'Django': [r'csrfmiddlewaretoken', r'django', r'csrftoken'],
            'Ruby on Rails': [r'csrf-param', r'rails', r'authenticity_token'],
            'ASP.NET': [r'__viewstate', r'__eventvalidation', r'asp\.net', r'ASP\.NET'],
            'Spring Boot': [r'x-application-context', r'spring', r'actuator'],
            'Flask': [r'flask', r'flask-session'],
            'Express': [r'express', r'x-powered-by: express']
        }
    
    def _find_whatweb(self) -> Optional[str]:
        """Trouve le chemin de WhatWeb"""
        import shutil
        return shutil.which("whatweb")
    
    def set_stealth_config(self, config: Dict[str, Any]):
        """
        Configure le mode furtif
        
        Args:
            config: Configuration de furtivité
        """
        self.stealth_mode = config.get('enabled', False)
        self.apt_mode = config.get('apt_mode', False)
        
        if self.stealth_mode:
            self.stealth_engine.set_delays(
                min_delay=config.get('delay_min', 1),
                max_delay=config.get('delay_max', 5),
                jitter=config.get('jitter', 0.3)
            )
            if self.apt_mode:
                self.stealth_engine.enable_apt_mode()
    
    def _apply_stealth_delay(self):
        """Applique un délai furtif"""
        if self.stealth_mode:
            self.stealth_engine.apply_delay()
    
    def _get_headers(self) -> Dict[str, str]:
        """Génère des headers furtifs"""
        if self.stealth_mode:
            return self.stealth_engine.get_headers()
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def detect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Détecte les technologies utilisées par le site web
        
        Args:
            target: URL cible
            **kwargs:
                - aggressive: Mode agressif
                - stealth: Mode furtif
                - custom_headers: Headers personnalisés
                - deep_scan: Scan approfondi
        """
        print(f"  → Détection des technologies sur {target}")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Détection discrète")
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        results = {
            "target": target,
            "technologies": [],
            "server": None,
            "framework": None,
            "cms": None,
            "javascript_libs": [],
            "headers": {},
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode
        }
        
        # Méthode 1: WhatWeb (si disponible et pas en mode APT)
        if self.available and not self.apt_mode:
            self._apply_stealth_delay()
            whatweb_results = self._scan_with_whatweb(target, **kwargs)
            results.update(whatweb_results)
        
        # Méthode 2: Analyse HTTP headers
        self._apply_stealth_delay()
        http_results = self._analyze_http_headers(target, **kwargs)
        results["headers"] = http_results.get("headers", {})
        
        if not results.get("server") and http_results.get("server"):
            results["server"] = http_results["server"]
        
        # Méthode 3: Analyse HTML
        self._apply_stealth_delay()
        html_results = self._analyze_html(target, **kwargs)
        results["javascript_libs"] = html_results.get("javascript_libs", [])
        
        # Fusionner les technologies détectées
        all_technologies = []
        if whatweb_results.get("technologies"):
            all_technologies.extend(whatweb_results["technologies"])
        if http_results.get("technologies"):
            all_technologies.extend(http_results["technologies"])
        if html_results.get("technologies"):
            all_technologies.extend(html_results["technologies"])
        
        # Dédupliquer et conserver la meilleure confiance
        tech_map = {}
        for tech in all_technologies:
            key = f"{tech['name']}_{tech.get('version', 'unknown')}"
            if key not in tech_map or tech.get('confidence', 0) > tech_map[key].get('confidence', 0):
                tech_map[key] = tech
        
        results["technologies"] = list(tech_map.values())
        
        # Identifier CMS et framework
        results["cms"] = self._identify_cms(results["technologies"])
        results["framework"] = self._identify_framework(results["technologies"])
        
        return results
    
    def _scan_with_whatweb(self, target: str, **kwargs) -> Dict[str, Any]:
        """Utilise WhatWeb pour scanner les technologies"""
        cmd = [self.whatweb_path]
        
        if kwargs.get('aggressive'):
            cmd.append('-a')
        
        if kwargs.get('stealth') or self.stealth_mode:
            cmd.append('-s')
        
        # Format JSON pour parsing facile
        cmd.extend(['-j'])
        
        cmd.append(target)
        
        try:
            timeout = kwargs.get('timeout', 60)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0 and result.stdout:
                return self._parse_whatweb_json(result.stdout)
            else:
                return self._parse_whatweb_text(result.stdout)
                
        except subprocess.TimeoutExpired:
            if not self.stealth_mode:
                print(f"    ⚠️ WhatWeb timeout")
            return {"technologies": []}
        except Exception as e:
            if not self.stealth_mode:
                print(f"    ⚠️ Erreur WhatWeb: {e}")
            return {"technologies": []}
    
    def _parse_whatweb_json(self, output: str) -> Dict[str, Any]:
        """Parse la sortie JSON de WhatWeb"""
        result = {
            "technologies": [],
            "server": None,
            "framework": None,
            "cms": None
        }
        
        try:
            data = json.loads(output)
            
            if isinstance(data, list) and len(data) > 0:
                target_data = data[0]
                
                for plugin, info in target_data.items():
                    if plugin in ['url', 'status', 'ip', 'title', 'port', 'method']:
                        continue
                    
                    tech = {
                        "name": plugin,
                        "version": "unknown",
                        "confidence": 100,
                        "source": "whatweb"
                    }
                    
                    if isinstance(info, dict):
                        tech["version"] = info.get('version', 'unknown')
                        tech["confidence"] = info.get('certainty', 100)
                    elif isinstance(info, str) and info and info != 'None':
                        tech["version"] = info
                    
                    result["technologies"].append(tech)
                    
                    # Identification spéciale
                    plugin_lower = plugin.lower()
                    if plugin_lower == 'server':
                        result["server"] = tech["version"] if tech["version"] != 'unknown' else None
                    elif plugin_lower in ['wordpress', 'joomla', 'drupal', 'magento', 'prestashop', 'shopify']:
                        result["cms"] = plugin
                    elif plugin_lower in ['laravel', 'rails', 'django', 'symfony', 'spring', 'express']:
                        result["framework"] = plugin
                        
        except json.JSONDecodeError:
            pass
        
        return result
    
    def _parse_whatweb_text(self, output: str) -> Dict[str, Any]:
        """Parse la sortie texte de WhatWeb"""
        result = {
            "technologies": []
        }
        
        # Pattern pour les technologies
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, output)
        
        for match in matches:
            parts = match.split()
            if parts:
                tech = {
                    "name": parts[0],
                    "version": parts[1] if len(parts) > 1 else 'unknown',
                    "confidence": 100,
                    "source": "whatweb"
                }
                result["technologies"].append(tech)
        
        return result
    
    def _analyze_http_headers(self, target: str, **kwargs) -> Dict[str, Any]:
        """Analyse les headers HTTP pour détecter des technologies"""
        result = {
            "headers": {},
            "server": None,
            "technologies": []
        }
        
        try:
            headers = kwargs.get('custom_headers', {})
            if self.stealth_mode:
                headers.update(self._get_headers())
            
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            result["headers"] = dict(response.headers)
            
            # Server header
            server = response.headers.get('Server', '')
            if server:
                result["server"] = server
                result["technologies"].append({
                    "name": "Server",
                    "version": server,
                    "confidence": 100,
                    "source": "headers"
                })
            
            # X-Powered-By
            powered_by = response.headers.get('X-Powered-By', '')
            if powered_by:
                result["technologies"].append({
                    "name": "Powered By",
                    "version": powered_by,
                    "confidence": 90,
                    "source": "headers"
                })
            
            # Framework detection via headers
            framework_headers = {
                'X-Powered-CMS': 'CMS',
                'X-Drupal-Cache': 'Drupal',
                'X-Drupal-Dynamic-Cache': 'Drupal',
                'X-Content-Encoded-By': 'Joomla',
                'X-Generator': 'Generator',
                'X-AspNet-Version': 'ASP.NET',
                'X-AspNetMvc-Version': 'ASP.NET MVC'
            }
            
            for header, tech_name in framework_headers.items():
                if header in response.headers:
                    result["technologies"].append({
                        "name": tech_name,
                        "version": response.headers[header],
                        "confidence": 85,
                        "source": "headers"
                    })
                    
        except Exception as e:
            if not self.stealth_mode:
                print(f"    ⚠️ Erreur analyse headers: {e}")
        
        return result
    
    def _analyze_html(self, target: str, **kwargs) -> Dict[str, Any]:
        """Analyse le HTML pour détecter des technologies"""
        result = {
            "technologies": [],
            "javascript_libs": []
        }
        
        try:
            headers = kwargs.get('custom_headers', {})
            if self.stealth_mode:
                headers.update(self._get_headers())
            
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            html = response.text.lower()
            
            # Détection de CMS
            for cms, patterns in self.cms_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, html):
                        result["technologies"].append({
                            "name": cms,
                            "version": "unknown",
                            "confidence": 80,
                            "source": "html"
                        })
                        break
            
            # Détection de frameworks JavaScript
            for lib, pattern in self.js_libs_patterns.items():
                if re.search(pattern, html, re.IGNORECASE):
                    result["javascript_libs"].append(lib)
                    result["technologies"].append({
                        "name": lib,
                        "version": "unknown",
                        "confidence": 75,
                        "source": "html"
                    })
            
            # Détection de frameworks backend
            for backend, patterns in self.backend_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, html, re.IGNORECASE):
                        result["technologies"].append({
                            "name": backend,
                            "version": "unknown",
                            "confidence": 70,
                            "source": "html"
                        })
                        break
                    
        except Exception as e:
            if not self.stealth_mode:
                print(f"    ⚠️ Erreur analyse HTML: {e}")
        
        return result
    
    def _identify_cms(self, technologies: List[Dict]) -> Optional[str]:
        """Identifie le CMS parmi les technologies détectées"""
        cms_list = ['WordPress', 'Joomla', 'Drupal', 'Magento', 'PrestaShop', 'Shopify', 'Wix', 'Squarespace']
        
        for tech in technologies:
            for cms in cms_list:
                if cms.lower() in tech['name'].lower():
                    return cms
        
        return None
    
    def _identify_framework(self, technologies: List[Dict]) -> Optional[str]:
        """Identifie le framework parmi les technologies détectées"""
        frameworks = ['Laravel', 'Django', 'Rails', 'Symfony', 'Spring', 'React', 'Vue.js', 'Angular', 'Express', 'Flask']
        
        for tech in technologies:
            for framework in frameworks:
                if framework.lower() in tech['name'].lower():
                    return framework
        
        return None
    
    def get_wappalyzer_results(self, target: str) -> Dict[str, Any]:
        """Alternative utilisant Wappalyzer (si disponible)"""
        try:
            from Wappalyzer import Wappalyzer, WebPage
            
            webpage = WebPage.new_from_url(target)
            wappalyzer = Wappalyzer.latest()
            results = wappalyzer.analyze(webpage)
            
            return {
                "success": True,
                "technologies": [{"name": name, "version": "unknown"} for name in results]
            }
        except ImportError:
            return {"success": False, "error": "Wappalyzer non installé"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_version_info(self) -> Dict[str, Any]:
        """Retourne les informations de version"""
        if self.available:
            return {
                "available": True,
                "tool": "whatweb",
                "path": self.whatweb_path
            }
        return {"available": False}


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de WhatWebDetector")
    print("=" * 60)
    
    detector = WhatWebDetector()
    
    # Configuration mode APT
    detector.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Test (simulé)
    # results = detector.detect("https://example.com")
    # print(f"Technologies détectées: {len(results['technologies'])}")
    
    print("\n✅ Module WhatWebDetector chargé avec succès")