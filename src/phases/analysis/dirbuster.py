#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de force brute de répertoires pour RedForge
Découvre les répertoires et fichiers cachés sur le serveur web
Version avec support furtif, APT et détection avancée
"""

import re
import time
import random
import requests
from typing import Dict, Any, List, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from pathlib import Path
from collections import defaultdict

from src.core.stealth_engine import StealthEngine


class DirBuster:
    """Force brute avancée des répertoires et fichiers avec support furtif"""
    
    def __init__(self):
        # Wordlist par défaut (répertoires communs)
        self.common_directories = [
            "admin", "administrator", "backup", "backups", "cache", "cgi-bin",
            "css", "data", "db", "download", "downloads", "error", "images",
            "img", "include", "includes", "js", "log", "logs", "media", "old",
            "phpmyadmin", "plugins", "private", "sql", "stats", "temp", "test",
            "tmp", "upload", "uploads", "user", "users", "web", "webmail", "www",
            "api", "rest", "v1", "v2", "v3", "app", "public", "static", "assets",
            "resources", "templates", "themes", "modules", "controllers", "models",
            "views", "helpers", "libraries", "vendor", "node_modules", "bower_components"
        ]
        
        # Fichiers sensibles communs
        self.common_files = [
            "index.php", "index.html", "index.htm", "default.php", "default.html",
            "wp-config.php", "config.php", "settings.php", "config.inc.php",
            ".htaccess", ".git/config", ".env", "robots.txt", "sitemap.xml",
            "crossdomain.xml", "clientaccesspolicy.xml", "security.txt",
            "phpinfo.php", "info.php", "test.php", "debug.php", "backup.php",
            "README.md", "LICENSE", "CHANGELOG", "composer.json", "package.json",
            "yarn.lock", "package-lock.json", "Dockerfile", "docker-compose.yml",
            "Makefile", "Vagrantfile", ".travis.yml", ".gitlab-ci.yml"
        ]
        
        # Extensions à tester
        self.extensions = ['', '.php', '.html', '.htm', '.asp', '.aspx', '.jsp', 
                          '.do', '.action', '.js', '.json', '.xml', '.txt', '.md',
                          '.yml', '.yaml', '.ini', '.conf', '.config', '.sql']
        
        # Codes HTTP à inclure
        self.include_status = [200, 201, 202, 203, 204, 301, 302, 307, 308, 403, 401]
        
        # Moteur de furtivité
        self.stealth_engine = StealthEngine()
        self.stealth_mode = False
        self.apt_mode = False
        self.delay_between_requests = (0.5, 1.5)
    
    def set_stealth_config(self, config: Dict[str, Any]):
        """
        Configure le mode furtif
        
        Args:
            config: Configuration de furtivité
        """
        self.stealth_mode = config.get('enabled', False)
        self.apt_mode = config.get('apt_mode', False)
        
        if self.stealth_mode:
            self.delay_between_requests = (
                config.get('delay_min', 1),
                config.get('delay_max', 5)
            )
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
            if self.apt_mode:
                self.stealth_engine.apply_delay()
            else:
                delay = random.uniform(*self.delay_between_requests)
                time.sleep(delay)
    
    def _get_headers(self) -> Dict[str, str]:
        """Génère des headers furtifs"""
        if self.stealth_mode:
            return self.stealth_engine.get_headers()
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les répertoires et fichiers
        
        Args:
            target: URL cible
            **kwargs:
                - wordlist: Wordlist personnalisée
                - extensions: Extensions à tester
                - threads: Nombre de threads
                - recursive: Scan récursif
                - max_depth: Profondeur maximale pour le scan récursif
                - status_codes: Codes HTTP à inclure
        """
        print(f"  → Force brute des répertoires sur {target}")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Scan lent et discret")
        
        # Nettoyer l'URL
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        target = target.rstrip('/')
        
        # Récupérer les paramètres
        wordlist = kwargs.get('wordlist', self.common_directories + self.common_files)
        extensions = kwargs.get('extensions', self.extensions)
        threads = min(kwargs.get('threads', 20), 3 if self.apt_mode else 20)
        recursive = kwargs.get('recursive', False)
        max_depth = kwargs.get('max_depth', 3)
        include_status = kwargs.get('status_codes', self.include_status)
        
        found_items = []
        
        # Scanner avec wordlist
        print(f"    → Test de {len(wordlist)} entrées...")
        items = self._bruteforce_paths(target, wordlist, extensions, threads, include_status)
        found_items.extend(items)
        
        # Scan récursif
        if recursive and not self.apt_mode:  # En mode APT, éviter le scan récursif
            print(f"    → Scan récursif (profondeur max: {max_depth})...")
            for item in found_items[:10]:  # Limiter pour éviter l'explosion
                if item['type'] == 'directory' and item.get('depth', 0) < max_depth:
                    sub_path = item['path']
                    sub_target = urljoin(target, sub_path)
                    print(f"      → Scan de {sub_path}")
                    sub_items = self.scan(
                        sub_target, 
                        recursive=recursive, 
                        max_depth=max_depth,
                        threads=threads,
                        wordlist=wordlist[:50]  # Wordlist réduite pour récursif
                    )
                    for sub_item in sub_items.get('directories', []):
                        sub_item['path'] = f"{sub_path}/{sub_item['path']}"
                        sub_item['depth'] = item.get('depth', 0) + 1
                        found_items.append(sub_item)
                    for sub_item in sub_items.get('files', []):
                        sub_item['path'] = f"{sub_path}/{sub_item['path']}"
                        found_items.append(sub_item)
        
        # Filtrer et organiser
        directories = [i for i in found_items if i['type'] == 'directory']
        files = [i for i in found_items if i['type'] == 'file']
        
        return {
            "target": target,
            "directories": directories,
            "files": files,
            "total": len(found_items),
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "summary": {
                "directories_count": len(directories),
                "files_count": len(files),
                "by_status": self._group_by_status(found_items),
                "by_depth": self._group_by_depth(directories)
            }
        }
    
    def _bruteforce_paths(self, base_url: str, paths: List[str], extensions: List[str], 
                          threads: int, include_status: List[int]) -> List[Dict[str, Any]]:
        """Bruteforce les chemins avec multi-threading"""
        found = []
        tested = set()
        tested_count = 0
        
        def test_path(path):
            nonlocal tested_count
            if path in tested:
                return None
            tested.add(path)
            tested_count += 1
            
            results = []
            
            # Tester sans extension
            url = urljoin(base_url + '/', path)
            try:
                headers = self._get_headers()
                response = requests.get(url, headers=headers, timeout=5, allow_redirects=False, verify=False)
                if response.status_code in include_status:
                    item_type = 'directory' if self._is_directory(response, path) else 'file'
                    results.append({
                        "path": path.rstrip('/'),
                        "full_url": url,
                        "status_code": response.status_code,
                        "content_length": len(response.content),
                        "content_type": response.headers.get('Content-Type', ''),
                        "type": item_type,
                        "depth": path.count('/')
                    })
            except:
                pass
            
            # Tester avec extensions pour les fichiers
            if not path.endswith('/') and '.' not in path:
                for ext in extensions:
                    if ext:
                        test_path_ext = path + ext
                        if test_path_ext not in tested:
                            tested.add(test_path_ext)
                            url_ext = urljoin(base_url + '/', test_path_ext)
                            try:
                                headers = self._get_headers()
                                response = requests.get(url_ext, headers=headers, timeout=5, allow_redirects=False, verify=False)
                                if response.status_code in include_status:
                                    results.append({
                                        "path": test_path_ext,
                                        "full_url": url_ext,
                                        "status_code": response.status_code,
                                        "content_length": len(response.content),
                                        "content_type": response.headers.get('Content-Type', ''),
                                        "type": 'file',
                                        "depth": test_path_ext.count('/')
                                    })
                            except:
                                pass
            
            return results if results else None
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(test_path, path): path for path in paths}
            
            for future in as_completed(futures):
                results = future.result()
                if results:
                    for result in results:
                        found.append(result)
                        status = result['status_code']
                        path = result['path']
                        if status in [200, 201, 202, 203, 204]:
                            print(f"      ✓ Trouvé: {path} (HTTP {status})")
                
                # Délai furtif entre les lots
                if self.apt_mode and tested_count % 10 == 0:
                    self._apply_stealth_delay()
        
        return found
    
    def _is_directory(self, response: requests.Response, path: str) -> bool:
        """Détermine si la réponse indique un répertoire"""
        # Vérifier les headers
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type:
            # Vérifier le contenu pour des indices de directory listing
            content = response.text.lower()
            if any(indicator in content for indicator in ['index of', 'parent directory', 'directory listing']):
                return True
        
        # Si l'URL se termine par /, c'est probablement un répertoire
        if response.url.endswith('/') or path.endswith('/'):
            return True
        
        # Vérifier la présence de slash dans le chemin
        if '/' in path and not '.' in path.split('/')[-1]:
            return True
        
        return False
    
    def _group_by_status(self, items: List[Dict]) -> Dict[int, int]:
        """Groupe les items par code de statut HTTP"""
        groups = defaultdict(int)
        for item in items:
            groups[item['status_code']] += 1
        return dict(groups)
    
    def _group_by_depth(self, directories: List[Dict]) -> Dict[int, int]:
        """Groupe les répertoires par profondeur"""
        groups = defaultdict(int)
        for item in directories:
            groups[item.get('depth', 0)] += 1
        return dict(groups)
    
    def scan_with_wordlist_file(self, target: str, wordlist_file: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne avec une wordlist personnalisée depuis un fichier
        
        Args:
            target: URL cible
            wordlist_file: Chemin du fichier wordlist
        """
        try:
            with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
                wordlist = [line.strip() for line in f if line.strip()]
            return self.scan(target, wordlist=wordlist, **kwargs)
        except FileNotFoundError:
            return {"error": f"Fichier wordlist non trouvé: {wordlist_file}"}
        except Exception as e:
            return {"error": f"Erreur lecture wordlist: {e}"}
    
    def detect_common_dirs(self, target: str) -> Dict[str, Any]:
        """Scan rapide des répertoires les plus communs"""
        return self.scan(target, wordlist=self.common_directories, recursive=False, threads=10)
    
    def detect_sensitive_files(self, target: str) -> Dict[str, Any]:
        """Détection de fichiers sensibles"""
        sensitive_files = [
            ".git/config", ".env", "wp-config.php", "config.php",
            "phpinfo.php", "info.php", "debug.php", "backup.sql",
            "database.sql", "dump.sql", "credentials.txt", "passwords.txt",
            ".htaccess", ".htpasswd", "web.config", "robots.txt",
            "composer.json", "package.json", "yarn.lock", "Dockerfile"
        ]
        return self.scan(target, wordlist=sensitive_files, recursive=False, threads=5)
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Génère un rapport texte des découvertes
        
        Args:
            results: Résultats du scan
            
        Returns:
            Rapport formaté
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("📁 RAPPORT DE FORCE BRUTE - DIRBUSTER")
        report_lines.append("=" * 60)
        report_lines.append(f"Cible: {results.get('target', 'Unknown')}")
        report_lines.append(f"Mode furtif: {'Oui' if results.get('stealth_mode') else 'Non'}")
        report_lines.append(f"Mode APT: {'Oui' if results.get('apt_mode') else 'Non'}")
        report_lines.append(f"Total découvert: {results.get('total', 0)}")
        report_lines.append("")
        
        if results.get('directories'):
            report_lines.append("📁 RÉPERTOIRES TROUVÉS:")
            for d in results['directories'][:30]:
                report_lines.append(f"  [{d['status_code']}] {d['path']} ({d['content_length']} octets)")
            if len(results['directories']) > 30:
                report_lines.append(f"  ... et {len(results['directories']) - 30} autres")
        
        if results.get('files'):
            report_lines.append("")
            report_lines.append("📄 FICHIERS TROUVÉS:")
            for f in results['files'][:30]:
                report_lines.append(f"  [{f['status_code']}] {f['path']} ({f['content_length']} octets)")
            if len(results['files']) > 30:
                report_lines.append(f"  ... et {len(results['files']) - 30} autres")
        
        if results.get('summary', {}).get('by_status'):
            report_lines.append("")
            report_lines.append("📊 STATISTIQUES PAR CODE HTTP:")
            for status, count in results['summary']['by_status'].items():
                report_lines.append(f"  HTTP {status}: {count}")
        
        return "\n".join(report_lines)
    
    def save_results(self, results: Dict[str, Any], output_file: str) -> bool:
        """
        Sauvegarde les résultats au format JSON
        
        Args:
            results: Résultats du scan
            output_file: Fichier de sortie
            
        Returns:
            True si sauvegarde réussie
        """
        import json
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            print(f"✓ Résultats sauvegardés: {output_file}")
            return True
        except Exception as e:
            print(f"✗ Erreur sauvegarde: {e}")
            return False


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de DirBuster")
    print("=" * 60)
    
    dirbuster = DirBuster()
    
    # Configuration mode APT
    dirbuster.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Test (simulé)
    # results = dirbuster.scan("https://example.com", recursive=False)
    # print(f"Répertoires trouvés: {len(results['directories'])}")
    
    print("\n✅ Module DirBuster chargé avec succès")