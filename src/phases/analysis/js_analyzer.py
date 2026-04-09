#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'analyse JavaScript pour RedForge
Analyse les fichiers JS pour trouver endpoints, secrets, etc.
Version avec support furtif, APT et détection avancée
"""

import re
import time
import random
import requests
import json
import hashlib
from typing import Dict, Any, List, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

from src.core.stealth_engine import StealthEngine


class JSAnalyzer:
    """Analyse avancée des fichiers JavaScript avec support furtif"""
    
    def __init__(self):
        # Patterns pour détecter des endpoints dans le JS
        self.endpoint_patterns = [
            (r'["\'](/(?:api|rest|v\d+)/[^"\']+)["\']', 'api_path'),
            (r'["\'](https?://[^"\']+\.(?:php|asp|aspx|jsp|do|action)[^"\']*)["\']', 'dynamic_url'),
            (r'url\s*:\s*["\']([^"\']+)["\']', 'url_field'),
            (r'path\s*:\s*["\']([^"\']+)["\']', 'path_field'),
            (r'endpoint\s*:\s*["\']([^"\']+)["\']', 'endpoint_field'),
            (r'fetch\(["\']([^"\']+)["\']', 'fetch_call'),
            (r'XMLHttpRequest\(["\']([^"\']+)["\']', 'xhr_call'),
            (r'\.get\(["\']([^"\']+)["\']', 'ajax_get'),
            (r'\.post\(["\']([^"\']+)["\']', 'ajax_post'),
            (r'\.put\(["\']([^"\']+)["\']', 'ajax_put'),
            (r'\.delete\(["\']([^"\']+)["\']', 'ajax_delete'),
            (r'axios\.(?:get|post|put|delete)\(["\']([^"\']+)["\']', 'axios_call'),
            (r'api\.(?:get|post|put|delete)\(["\']([^"\']+)["\']', 'api_call'),
            (r'baseURL\s*:\s*["\']([^"\']+)["\']', 'base_url'),
            (r'route\s*:\s*["\']([^"\']+)["\']', 'route_field')
        ]
        
        # Patterns pour détecter des secrets/API keys
        self.secret_patterns = [
            (r'api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9]{16,})["\']', 'API Key', 'high'),
            (r'token["\']?\s*[:=]\s*["\']([a-zA-Z0-9]{20,})["\']', 'Token', 'high'),
            (r'secret["\']?\s*[:=]\s*["\']([a-zA-Z0-9]{16,})["\']', 'Secret', 'critical'),
            (r'password["\']?\s*[:=]\s*["\']([^"\']{8,})["\']', 'Password', 'critical'),
            (r'authorization["\']?\s*[:=]\s*["\']Bearer\s+([a-zA-Z0-9._-]+)["\']', 'Bearer Token', 'critical'),
            (r'access_token["\']?\s*[:=]\s*["\']([a-zA-Z0-9._-]+)["\']', 'Access Token', 'high'),
            (r'refresh_token["\']?\s*[:=]\s*["\']([a-zA-Z0-9._-]+)["\']', 'Refresh Token', 'high'),
            (r'firebase', 'Firebase Config', 'medium'),
            (r'AIza[0-9A-Za-z\\-_]{35}', 'Google API Key', 'critical'),
            (r'SK-[0-9a-zA-Z]{48}', 'OpenAI API Key', 'critical'),
            (r'github_[a-zA-Z0-9]{36}', 'GitHub Token', 'critical'),
            (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Token', 'critical'),
            (r'xox[baprs]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}', 'Slack Token', 'critical'),
            (r'pk_live_[a-zA-Z0-9]{24}', 'Stripe Live Key', 'critical'),
            (r'sk_live_[a-zA-Z0-9]{24}', 'Stripe Secret Key', 'critical'),
            (r'mongodb(?:\+srv)?://[a-zA-Z0-9]+:[a-zA-Z0-9]+@', 'MongoDB URI', 'critical'),
            (r'redis://[a-zA-Z0-9]+:[a-zA-Z0-9]+@', 'Redis URI', 'critical')
        ]
        
        # Patterns pour détecter des domaines
        self.domain_pattern = r'(https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
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
    
    def analyze(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Analyse les fichiers JavaScript de la cible
        
        Args:
            target: URL cible
            **kwargs:
                - depth: Profondeur de crawl
                - fetch_external: Analyser les JS externes
                - save_files: Sauvegarder les fichiers JS
                - max_files: Nombre maximum de fichiers à analyser
        """
        print(f"  → Analyse JavaScript sur {target}")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Analyse discrète")
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        js_files = []
        
        # Étape 1: Trouver les fichiers JS dans la page principale
        print(f"    → Recherche de fichiers JS...")
        self._apply_stealth_delay()
        js_files.extend(self._find_js_files(target))
        
        # Étape 2: Crawler pour trouver plus de fichiers
        depth = kwargs.get('depth', 2)
        if depth > 1 and not self.apt_mode:  # Limiter en mode APT
            print(f"    → Crawling (profondeur {depth})...")
            js_files.extend(self._crawl_for_js(target, depth))
        
        # Limiter le nombre de fichiers en mode APT
        max_files = kwargs.get('max_files', 50 if not self.apt_mode else 15)
        js_files = list(set(js_files))[:max_files]
        
        # Étape 3: Analyser chaque fichier JS
        print(f"    → Analyse de {len(js_files)} fichiers JS...")
        analysis_results = []
        
        for idx, js_url in enumerate(js_files):
            if self.apt_mode and idx > 0:
                self._apply_stealth_delay()
            
            analysis = self._analyze_js_file(js_url, target)
            analysis_results.append(analysis)
            
            if kwargs.get('save_files'):
                self._save_js_file(js_url, analysis)
        
        # Compilation des résultats
        all_endpoints = []
        all_secrets = []
        all_domains = set()
        
        for result in analysis_results:
            all_endpoints.extend(result.get('endpoints', []))
            all_secrets.extend(result.get('secrets', []))
            all_domains.update(result.get('domains', []))
        
        return {
            "target": target,
            "js_files": analysis_results,
            "total_files": len(analysis_results),
            "total_endpoints": len(all_endpoints),
            "total_secrets": len(all_secrets),
            "all_endpoints": all_endpoints,
            "all_secrets": all_secrets,
            "all_domains": list(all_domains),
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "summary": self._generate_summary(analysis_results)
        }
    
    def _find_js_files(self, url: str) -> List[str]:
        """Trouve tous les fichiers JS dans une page"""
        js_files = []
        
        try:
            headers = self._get_headers()
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Script tags avec src
            for script in soup.find_all('script', src=True):
                src = script['src']
                if src.endswith('.js') or '.js?' in src:
                    full_url = urljoin(url, src)
                    js_files.append(full_url)
            
            # Liens vers des fichiers JS
            for link in soup.find_all('link', href=True):
                href = link['href']
                if href.endswith('.js') or '.js?' in href:
                    full_url = urljoin(url, href)
                    js_files.append(full_url)
                    
        except Exception as e:
            print(f"      ⚠️ Erreur récupération JS: {e}")
        
        return js_files
    
    def _crawl_for_js(self, base_url: str, depth: int) -> List[str]:
        """Crawl l'application pour trouver des fichiers JS"""
        js_files = set()
        visited = set()
        
        def crawl(url, current_depth):
            if current_depth > depth or url in visited:
                return
            visited.add(url)
            
            try:
                headers = self._get_headers()
                response = requests.get(url, headers=headers, timeout=10, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Trouver les JS dans cette page
                for script in soup.find_all('script', src=True):
                    src = script['src']
                    if src.endswith('.js') or '.js?' in src:
                        full_url = urljoin(base_url, src)
                        js_files.add(full_url)
                
                # Trouver les liens pour continuer le crawl (limité en mode APT)
                if current_depth < depth and (not self.apt_mode or current_depth < 2):
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('/') and not href.startswith('//'):
                            next_url = urljoin(base_url, href)
                            if next_url.startswith(base_url):
                                crawl(next_url, current_depth + 1)
                                
            except:
                pass
        
        crawl(base_url, 1)
        return list(js_files)
    
    def _analyze_js_file(self, js_url: str, base_target: str) -> Dict[str, Any]:
        """Analyse un fichier JavaScript spécifique"""
        analysis = {
            "url": js_url,
            "size": 0,
            "endpoints": [],
            "secrets": [],
            "domains": [],
            "functions": [],
            "variables": [],
            "imports": []
        }
        
        try:
            headers = self._get_headers()
            response = requests.get(js_url, headers=headers, timeout=15, verify=False)
            content = response.text
            analysis["size"] = len(content)
            
            # Détection des endpoints
            for pattern, source in self.endpoint_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match and not match.startswith('http'):
                        full_url = urljoin(base_target, match)
                    else:
                        full_url = match
                    analysis["endpoints"].append({
                        "url": full_url,
                        "source": source,
                        "line": self._find_line_number(content, match)
                    })
            
            # Détection des secrets
            for pattern, secret_type, severity in self.secret_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    analysis["secrets"].append({
                        "type": secret_type,
                        "severity": severity,
                        "value": match[:50] + "..." if len(match) > 50 else match,
                        "full_value": match,
                        "line": self._find_line_number(content, match)
                    })
            
            # Détection des domaines
            domains = re.findall(self.domain_pattern, content, re.IGNORECASE)
            analysis["domains"] = list(set(domains))
            
            # Détection des fonctions
            function_pattern = r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\('
            functions = re.findall(function_pattern, content)
            analysis["functions"] = list(set(functions))[:20]
            
            # Détection des variables globales
            var_pattern = r'(?:var|let|const)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*='
            variables = re.findall(var_pattern, content)
            analysis["variables"] = list(set(variables))[:20]
            
            # Détection des imports
            import_pattern = r'import\s+.*?from\s+["\']([^"\']+)["\']'
            imports = re.findall(import_pattern, content)
            analysis["imports"] = list(set(imports))[:20]
            
            # Nettoyer les doublons d'endpoints
            seen = set()
            unique_endpoints = []
            for ep in analysis["endpoints"]:
                ep_key = ep["url"]
                if ep_key not in seen:
                    seen.add(ep_key)
                    unique_endpoints.append(ep)
            analysis["endpoints"] = unique_endpoints
            
            # Nettoyer les doublons de secrets
            seen_secrets = set()
            unique_secrets = []
            for sec in analysis["secrets"]:
                sec_key = sec["value"]
                if sec_key not in seen_secrets:
                    seen_secrets.add(sec_key)
                    unique_secrets.append(sec)
            analysis["secrets"] = unique_secrets
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def _find_line_number(self, content: str, substring: str) -> int:
        """Trouve le numéro de ligne d'un substring dans le contenu"""
        if not substring:
            return 0
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if substring in line:
                return i
        return 0
    
    def _save_js_file(self, js_url: str, analysis: Dict[str, Any]) -> bool:
        """Sauvegarde l'analyse du fichier JS localement"""
        try:
            # Créer un nom de fichier unique
            hash_name = hashlib.md5(js_url.encode()).hexdigest()[:10]
            filename = f"js_analysis_{hash_name}.json"
            
            output_dir = Path("js_analysis")
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            return True
        except:
            return False
    
    def _generate_summary(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé de l'analyse"""
        total_secrets = sum(len(a.get('secrets', [])) for a in analyses)
        total_endpoints = sum(len(a.get('endpoints', [])) for a in analyses)
        
        secret_types = {}
        secret_severities = {}
        for analysis in analyses:
            for secret in analysis.get('secrets', []):
                secret_type = secret['type']
                secret_types[secret_type] = secret_types.get(secret_type, 0) + 1
                
                severity = secret.get('severity', 'medium')
                secret_severities[severity] = secret_severities.get(severity, 0) + 1
        
        return {
            "total_files": len(analyses),
            "total_secrets": total_secrets,
            "total_endpoints": total_endpoints,
            "secret_types": secret_types,
            "secret_severities": secret_severities,
            "has_secrets": total_secrets > 0
        }
    
    def extract_api_endpoints(self, target: str) -> List[str]:
        """Extrait spécifiquement les endpoints API"""
        results = self.analyze(target, depth=1)
        return [ep['url'] for ep in results.get('all_endpoints', []) if 'api' in ep['url'].lower()]
    
    def find_sensitive_data(self, target: str) -> List[Dict]:
        """Recherche spécifiquement les données sensibles"""
        results = self.analyze(target)
        return results.get('all_secrets', [])
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Génère un rapport d'analyse JavaScript"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("📜 RAPPORT D'ANALYSE JAVASCRIPT")
        report_lines.append("=" * 60)
        report_lines.append(f"Cible: {results.get('target', 'Unknown')}")
        report_lines.append(f"Mode furtif: {'Oui' if results.get('stealth_mode') else 'Non'}")
        report_lines.append(f"Mode APT: {'Oui' if results.get('apt_mode') else 'Non'}")
        report_lines.append(f"Fichiers analysés: {results.get('total_files', 0)}")
        report_lines.append(f"Endpoints trouvés: {results.get('total_endpoints', 0)}")
        report_lines.append(f"Secrets trouvés: {results.get('total_secrets', 0)}")
        report_lines.append("")
        
        if results.get('all_secrets'):
            report_lines.append("🔑 SECRETS DÉTECTÉS:")
            # Grouper par sévérité
            critical = [s for s in results['all_secrets'] if s.get('severity') == 'critical']
            high = [s for s in results['all_secrets'] if s.get('severity') == 'high']
            medium = [s for s in results['all_secrets'] if s.get('severity') == 'medium']
            
            if critical:
                report_lines.append("  🔴 CRITICAL:")
                for secret in critical[:5]:
                    report_lines.append(f"    - {secret['type']}: {secret['value']}")
            
            if high:
                report_lines.append("  🟠 HIGH:")
                for secret in high[:5]:
                    report_lines.append(f"    - {secret['type']}: {secret['value']}")
            
            if medium:
                report_lines.append("  🟡 MEDIUM:")
                for secret in medium[:5]:
                    report_lines.append(f"    - {secret['type']}: {secret['value']}")
        
        if results.get('all_endpoints'):
            report_lines.append("")
            report_lines.append("🔗 ENDPOINTS DÉTECTÉS:")
            for endpoint in results['all_endpoints'][:20]:
                report_lines.append(f"  - {endpoint['url']}")
        
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
    print("Test de JSAnalyzer")
    print("=" * 60)
    
    analyzer = JSAnalyzer()
    
    # Configuration mode APT
    analyzer.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Test (simulé)
    # results = analyzer.analyze("https://example.com")
    # print(f"Fichiers JS analysés: {results['total_files']}")
    # print(f"Secrets trouvés: {results['total_secrets']}")
    
    print("\n✅ Module JSAnalyzer chargé avec succès")