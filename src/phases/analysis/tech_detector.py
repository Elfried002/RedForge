#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection avancée de technologies pour RedForge
Identifie les technologies serveur, frameworks, librairies, etc.
Version avec support furtif, APT et détection avancée
"""

import re
import json
import time
import random
import requests
from typing import Dict, Any, List, Optional, Set, Tuple
from urllib.parse import urlparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.stealth_engine import StealthEngine


class TechDetector:
    """Détection avancée des technologies web avec support furtif"""
    
    def __init__(self):
        # Signatures pour détection des technologies
        self.technologies = {
            "Web Servers": {
                "Apache": [r'Apache(?:/(\d+\.\d+))?', r'Apache'],
                "Nginx": [r'nginx(?:/(\d+\.\d+))?', r'nginx'],
                "IIS": [r'Microsoft-IIS(?:/(\d+\.\d+))?', r'IIS'],
                "Tomcat": [r'Apache-Coyote', r'Tomcat'],
                "Node.js": [r'Node\.js', r'Express'],
                "Gunicorn": [r'gunicorn'],
                "Caddy": [r'Caddy'],
                "Lighttpd": [r'lighttpd']
            },
            "Programming Languages": {
                "PHP": [r'PHP(?:/(\d+\.\d+))?', r'\.php$', r'X-Powered-By: PHP'],
                "Python": [r'Python(?:/(\d+\.\d+))?', r'\.py$', r'wsgi'],
                "Ruby": [r'Ruby(?:/(\d+\.\d+))?', r'\.rb$', r'rails'],
                "Java": [r'Java(?:/(\d+\.\d+))?', r'\.jsp$', r'\.do$', r'JSESSIONID'],
                "ASP.NET": [r'ASP\.NET', r'\.aspx$', r'__VIEWSTATE', r'__EVENTVALIDATION'],
                "Go": [r'Go(?:/(\d+\.\d+))?', r'\.go$'],
                "Perl": [r'Perl', r'\.pl$', r'\.cgi$']
            },
            "Frameworks": {
                "Laravel": [r'laravel', r'X-Powered-By: Laravel', r'/laravel-'],
                "Django": [r'django', r'csrftoken', r'__admin_media_prefix__'],
                "Rails": [r'rails', r'csrf-param', r'rails'],
                "Spring Boot": [r'spring-boot', r'X-Application-Context', r'actuator'],
                "Express": [r'express', r'x-powered-by: express'],
                "Flask": [r'flask', r'flask-session'],
                "Symfony": [r'symfony', r'_sf2_'],
                "CodeIgniter": [r'CodeIgniter', r'CI_SESSION'],
                "CakePHP": [r'CakePHP', r'CAKEPHP'],
                "Yii": [r'yii', r'Yii Framework'],
                "Zend": [r'Zend Framework', r'Zend_']
            },
            "CMS": {
                "WordPress": [r'wp-content', r'wp-includes', r'wp-json', r'wordpress', r'/wp-'],
                "Joomla": [r'joomla', r'com_content', r'mosConfig', r'/media/system/js/'],
                "Drupal": [r'drupal', r'sites/all', r'drupal.js', r'jquery.ui.drupal'],
                "Magento": [r'magento', r'skin/frontend', r'mage.cookies'],
                "PrestaShop": [r'prestashop', r'ps.googleanalytics', r'controllers/front'],
                "Shopify": [r'shopify', r'myshopify.com', r'cdn.shopify'],
                "WooCommerce": [r'woocommerce', r'/wp-content/plugins/woocommerce'],
                "Wix": [r'wix', r'wix.com', r'wixstatic.com'],
                "Squarespace": [r'squarespace', r'static.squarespace.com']
            },
            "JavaScript Libraries": {
                "jQuery": [r'jquery(?:-([\d.]+))?', r'jQuery'],
                "React": [r'react(?:-([\d.]+))?', r'react\.js', r'ReactDOM', r'__REACT_DEVTOOLS_GLOBAL_HOOK__'],
                "Vue.js": [r'vue(?:-([\d.]+))?', r'vue\.js', r'v-bind', r'v-model', r'data-v-'],
                "Angular": [r'angular(?:-([\d.]+))?', r'angular\.js', r'ng-app', r'ng-'],
                "Bootstrap": [r'bootstrap(?:-([\d.]+))?', r'bootstrap\.css', r'bootstrap\.js'],
                "FontAwesome": [r'fontawesome(?:-([\d.]+))?', r'fa-'],
                "Google Analytics": [r'google-analytics', r'ga\.js', r'gtag'],
                "Facebook SDK": [r'connect\.facebook\.net', r'FB\.init'],
                "Tailwind": [r'tailwind', r'tw-'],
                "Svelte": [r'svelte', r'__svelte']
            },
            "Databases": {
                "MySQL": [r'MySQL', r'mysql', r'SQLSTATE'],
                "PostgreSQL": [r'PostgreSQL', r'pgsql'],
                "MongoDB": [r'MongoDB', r'mongodb'],
                "Redis": [r'Redis', r'redis'],
                "Elasticsearch": [r'elasticsearch', r'elastic'],
                "SQLite": [r'SQLite', r'sqlite']
            },
            "CDN & Security": {
                "Cloudflare": [r'cloudflare', r'__cfduid', r'cf-ray', r'cf-'],
                "Akamai": [r'Akamai', r'akamai'],
                "Sucuri": [r'Sucuri', r'sucuri'],
                "AWS CloudFront": [r'CloudFront', r'x-amz-cf'],
                "ModSecurity": [r'ModSecurity', r'mod_security'],
                "Imperva": [r'Imperva', r'incapsula'],
                "Fastly": [r'Fastly', r'fastly']
            },
            "Analytics": {
                "Google Analytics": [r'google-analytics', r'ga\.js', r'gtag\.js', r'UA-\d+'],
                "Facebook Pixel": [r'facebook\.com/tr', r'fbq\('],
                "Hotjar": [r'hotjar\.com', r'hj'],
                "Matomo": [r'matomo\.js', r'piwik\.js']
            }
        }
        
        # Signatures pour les headers
        self.header_signatures = {
            "Server": "web_servers",
            "X-Powered-By": "programming_languages",
            "X-Generator": "cms",
            "X-Drupal-Cache": "cms",
            "X-Content-Encoded-By": "cms",
            "X-Framework": "frameworks",
            "X-Laravel-Version": "frameworks",
            "X-Django-Version": "frameworks",
            "X-AspNet-Version": "programming_languages",
            "X-AspNetMvc-Version": "frameworks"
        }
        
        # Moteur de furtivité
        self.stealth_engine = StealthEngine()
        self.stealth_mode = False
        self.apt_mode = False
    
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
        Détecte toutes les technologies utilisées
        
        Args:
            target: URL cible
            **kwargs:
                - deep: Analyse approfondie (plus de requêtes)
                - headers: Headers personnalisés
        """
        print(f"  → Détection avancée des technologies sur {target}")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Détection discrète")
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        results = {
            "target": target,
            "technologies": [],
            "web_servers": [],
            "programming_languages": [],
            "frameworks": [],
            "cms": [],
            "javascript_libs": [],
            "databases": [],
            "cdn_security": [],
            "analytics": [],
            "headers": {},
            "confidence": {},
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode
        }
        
        # Récupérer les headers
        self._apply_stealth_delay()
        try:
            headers = self._get_headers()
            if kwargs.get('headers'):
                headers.update(kwargs['headers'])
            
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            results["headers"] = dict(response.headers)
            results["status_code"] = response.status_code
            results["html"] = response.text[:10000]  # Limiter pour la performance
            
            # Analyser les headers
            self._analyze_headers(results["headers"], results)
            
            # Analyser le HTML
            self._analyze_html(results["html"], results)
            
            # Analyse approfondie (requêtes supplémentaires)
            if kwargs.get('deep', True) and not self.apt_mode:
                self._deep_analysis(target, results)
                
        except Exception as e:
            print(f"    ⚠️ Erreur détection: {e}")
            results["error"] = str(e)
        
        # Organiser les résultats
        categories = ["web_servers", "programming_languages", "frameworks", "cms", 
                     "javascript_libs", "databases", "cdn_security", "analytics"]
        
        for category in categories:
            for tech in results[category]:
                results["technologies"].append({
                    "name": tech["name"],
                    "version": tech.get("version", "unknown"),
                    "category": category.replace("_", " ").title(),
                    "confidence": tech.get("confidence", 70),
                    "source": tech.get("source", "unknown")
                })
        
        # Dédupliquer
        seen = set()
        unique_techs = []
        for tech in results["technologies"]:
            key = f"{tech['name']}_{tech['version']}"
            if key not in seen:
                seen.add(key)
                unique_techs.append(tech)
        results["technologies"] = unique_techs
        
        # Générer le résumé
        results["summary"] = self._generate_summary(results)
        
        return results
    
    def _analyze_headers(self, headers: Dict[str, str], results: Dict):
        """Analyse les headers HTTP"""
        for header, value in headers.items():
            # Vérifier les signatures de headers
            for sig_header, category in self.header_signatures.items():
                if sig_header.lower() == header.lower():
                    self._add_technology(category, value, results, 90, header=header)
                    break
            
            # Détection spécifique
            if header.lower() == 'server':
                self._add_technology('web_servers', value, results, 100, source='header')
            elif header.lower() == 'x-powered-by':
                self._add_technology('programming_languages', value, results, 95, source='header')
            elif 'cloudflare' in value.lower():
                self._add_technology('cdn_security', 'Cloudflare', results, 100, source='header')
            elif 'sucuri' in value.lower():
                self._add_technology('cdn_security', 'Sucuri', results, 100, source='header')
    
    def _analyze_html(self, html: str, results: Dict):
        """Analyse le HTML pour détecter des technologies"""
        # Parcourir toutes les catégories et signatures
        for category, techs in self.technologies.items():
            category_key = category.lower().replace(" ", "_")
            for tech_name, patterns in techs.items():
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        version = None
                        if match.groups():
                            version = match.group(1)
                        
                        self._add_technology(category_key, tech_name, results, 85, version, source='html')
                        break
        
        # Détection spéciale des frameworks JS via data-attributes
        if 'data-react' in html:
            self._add_technology('javascript_libs', 'React', results, 80, source='html')
        if 'data-v-' in html:
            self._add_technology('javascript_libs', 'Vue.js', results, 80, source='html')
        if 'ng-' in html:
            self._add_technology('javascript_libs', 'Angular', results, 80, source='html')
        if 'data-svelte' in html:
            self._add_technology('javascript_libs', 'Svelte', results, 80, source='html')
    
    def _deep_analysis(self, target: str, results: Dict):
        """Analyse approfondie avec requêtes supplémentaires"""
        # Tester des chemins communs pour identifier les technologies
        test_paths = [
            ("/wp-content", "WordPress", "cms", 90),
            ("/wp-admin", "WordPress", "cms", 85),
            ("/joomla", "Joomla", "cms", 90),
            ("/sites/default/files", "Drupal", "cms", 90),
            ("/skin/frontend", "Magento", "cms", 90),
            ("/modules", "PrestaShop", "cms", 90),
            ("/api/", "API", "other", 50),
            ("/actuator", "Spring Boot", "frameworks", 95),
            ("/actuator/health", "Spring Boot", "frameworks", 90),
            ("/swagger-ui.html", "Swagger", "documentation", 85),
            ("/graphql", "GraphQL", "api", 85)
        ]
        
        for path, tech_name, category, confidence in test_paths:
            self._apply_stealth_delay()
            test_url = target.rstrip('/') + path
            try:
                headers = self._get_headers()
                response = requests.get(test_url, headers=headers, timeout=5, verify=False)
                if response.status_code in [200, 301, 302, 403]:
                    self._add_technology(category, tech_name, results, confidence, source='deep_scan')
            except:
                pass
        
        # Tester les fichiers robots.txt et sitemap
        robots_url = target.rstrip('/') + '/robots.txt'
        self._apply_stealth_delay()
        try:
            headers = self._get_headers()
            response = requests.get(robots_url, headers=headers, timeout=5, verify=False)
            if response.status_code == 200:
                if 'wp-admin' in response.text:
                    self._add_technology('cms', 'WordPress', results, 85, source='robots.txt')
                elif 'Joomla' in response.text:
                    self._add_technology('cms', 'Joomla', results, 85, source='robots.txt')
        except:
            pass
    
    def _add_technology(self, category: str, tech: str, results: Dict, confidence: int, 
                        version: str = None, source: str = None):
        """Ajoute une technologie aux résultats"""
        # Nettoyer le nom
        tech_name = tech.split('/')[0].split(' ')[0].strip()
        
        tech_dict = {
            "name": tech_name,
            "confidence": confidence,
            "source": source or "unknown"
        }
        if version:
            tech_dict["version"] = version
        
        # Vérifier si déjà présent
        existing = results.get(category, [])
        for existing_tech in existing:
            if existing_tech["name"] == tech_name:
                if confidence > existing_tech["confidence"]:
                    existing_tech["confidence"] = confidence
                if version and existing_tech.get("version") == "unknown":
                    existing_tech["version"] = version
                if source and source not in existing_tech.get("sources", []):
                    existing_tech.setdefault("sources", []).append(source)
                return
        
        results.setdefault(category, []).append(tech_dict)
    
    def _generate_summary(self, results: Dict) -> Dict[str, Any]:
        """Génère un résumé des technologies détectées"""
        return {
            "total_technologies": len(results.get("technologies", [])),
            "web_servers": len(results.get("web_servers", [])),
            "programming_languages": len(results.get("programming_languages", [])),
            "frameworks": len(results.get("frameworks", [])),
            "cms": len(results.get("cms", [])),
            "javascript_libs": len(results.get("javascript_libs", [])),
            "databases": len(results.get("databases", [])),
            "cdn_security": len(results.get("cdn_security", [])),
            "analytics": len(results.get("analytics", [])),
            "has_cms": len(results.get("cms", [])) > 0,
            "has_framework": len(results.get("frameworks", [])) > 0,
            "stealth_mode": results.get("stealth_mode", False),
            "apt_mode": results.get("apt_mode", False)
        }
    
    def get_cms_details(self, target: str) -> Dict[str, Any]:
        """Détail spécifique sur le CMS détecté"""
        results = self.detect(target)
        
        cms_info = {
            "cms_detected": results.get("cms", []),
            "is_wordpress": False,
            "is_joomla": False,
            "is_drupal": False,
            "is_magento": False,
            "is_prestashop": False,
            "plugins": [],
            "themes": [],
            "version": None
        }
        
        for cms in results.get("cms", []):
            cms_name = cms["name"].lower()
            if "wordpress" in cms_name:
                cms_info["is_wordpress"] = True
                cms_info["version"] = cms.get("version")
                if not self.apt_mode:
                    cms_info["plugins"] = self._detect_wordpress_plugins(target)
                    cms_info["themes"] = self._detect_wordpress_theme(target)
            elif "joomla" in cms_name:
                cms_info["is_joomla"] = True
            elif "drupal" in cms_name:
                cms_info["is_drupal"] = True
            elif "magento" in cms_name:
                cms_info["is_magento"] = True
            elif "prestashop" in cms_name:
                cms_info["is_prestashop"] = True
        
        return cms_info
    
    def _detect_wordpress_plugins(self, target: str) -> List[str]:
        """Détecte les plugins WordPress installés"""
        plugins = []
        
        common_plugins = [
            "woocommerce", "yoast", "elementor", "contact-form-7", "jetpack",
            "acf", "wp-rocket", "wordfence", "wpforms", "all-in-one-seo",
            "wp-smushit", "google-analytics", "monsterinsights", "wp-mail-smtp",
            "redux-framework", "visual-composer", "revslider", "gravityforms"
        ]
        
        for plugin in common_plugins:
            self._apply_stealth_delay()
            plugin_path = f"/wp-content/plugins/{plugin}/"
            test_url = target.rstrip('/') + plugin_path
            try:
                headers = self._get_headers()
                response = requests.get(test_url, headers=headers, timeout=3, verify=False)
                if response.status_code in [200, 301, 302, 403]:
                    plugins.append(plugin)
                    print(f"      ✓ Plugin WordPress trouvé: {plugin}")
            except:
                pass
        
        return plugins
    
    def _detect_wordpress_theme(self, target: str) -> List[str]:
        """Détecte le thème WordPress actif"""
        themes = []
        
        # Tenter de lire le style.css du thème
        try:
            headers = self._get_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            # Chercher le thème dans le code source
            theme_pattern = r'/wp-content/themes/([^/]+)/'
            matches = re.findall(theme_pattern, response.text)
            themes = list(set(matches))
            
            if themes:
                print(f"      ✓ Thème WordPress trouvé: {themes[0]}")
        except:
            pass
        
        return themes
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Génère un rapport de détection des technologies"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("📊 RAPPORT DE DÉTECTION DES TECHNOLOGIES")
        report_lines.append("=" * 60)
        report_lines.append(f"Cible: {results.get('target', 'Unknown')}")
        report_lines.append(f"Mode furtif: {'Oui' if results.get('stealth_mode') else 'Non'}")
        report_lines.append(f"Mode APT: {'Oui' if results.get('apt_mode') else 'Non'}")
        report_lines.append(f"Technologies détectées: {results.get('summary', {}).get('total_technologies', 0)}")
        report_lines.append("")
        
        categories = [
            ("web_servers", "🌐 Serveurs Web"),
            ("programming_languages", "💻 Langages"),
            ("frameworks", "⚙️ Frameworks"),
            ("cms", "📝 CMS"),
            ("javascript_libs", "📜 JavaScript"),
            ("databases", "🗄️ Bases de données"),
            ("cdn_security", "🛡️ CDN/Sécurité"),
            ("analytics", "📊 Analytics")
        ]
        
        for cat_key, cat_name in categories:
            techs = results.get(cat_key, [])
            if techs:
                report_lines.append(f"\n{cat_name}:")
                for tech in techs:
                    version = f" v{tech['version']}" if tech.get('version') != 'unknown' else ''
                    report_lines.append(f"  - {tech['name']}{version} (confiance: {tech['confidence']}%)")
        
        # Headers intéressants
        if results.get("headers"):
            report_lines.append("\n🔧 HEADERS REMARQUABLES:")
            important_headers = ['server', 'x-powered-by', 'x-frame-options', 
                                'content-security-policy', 'strict-transport-security']
            for header, value in results["headers"].items():
                if header.lower() in important_headers:
                    report_lines.append(f"  - {header}: {value}")
        
        return "\n".join(report_lines)
    
    def save_results(self, results: Dict[str, Any], output_file: str) -> bool:
        """Sauvegarde les résultats au format JSON"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"✓ Résultats sauvegardés: {output_file}")
            return True
        except Exception as e:
            print(f"✗ Erreur sauvegarde: {e}")
            return False


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de TechDetector")
    print("=" * 60)
    
    detector = TechDetector()
    
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
    
    print("\n✅ Module TechDetector chargé avec succès")