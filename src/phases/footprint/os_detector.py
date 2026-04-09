#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection de système d'exploitation pour RedForge
Utilise Nmap et d'autres techniques pour identifier l'OS cible
Version avec support furtif, APT et détection avancée
"""

import subprocess
import re
import time
from typing import Dict, Any, Optional, List, Tuple
from collections import Counter
from dataclasses import dataclass

from src.core.stealth_engine import StealthEngine


@dataclass
class OSFingerprint:
    """Empreinte OS"""
    name: str
    family: str
    confidence: int
    indicators: List[str]
    ports: List[int]
    ttl_range: Tuple[int, int]


class OSDetector:
    """Détection avancée du système d'exploitation avec support furtif"""
    
    def __init__(self):
        self.nmap_path = self._find_nmap()
        self.available = self.nmap_path is not None
        self.stealth_mode = False
        self.apt_mode = False
        self.stealth_engine = StealthEngine()
        
        # Signatures OS pour bannières
        self.os_signatures = {
            "Windows": {
                "indicators": [
                    "microsoft-iis", "windows", "win32", "iis", "asp.net",
                    "ntlm", "windows server", "exchange", "iis/", "ms-wbt-server",
                    "microsoft-ds", "netbios-ssn", "rdp", "ssl/ms-wbt-server"
                ],
                "ports": [135, 139, 445, 3389, 49152, 5985, 5986],
                "ttl_range": (128, 255),
                "weight": 2
            },
            "Linux": {
                "indicators": [
                    "ubuntu", "debian", "centos", "red hat", "fedora", "linux",
                    "apache/", "nginx", "openssh", "vsftpd", "proftpd", "postfix",
                    "sendmail", "mysql", "mariadb", "php-fpm"
                ],
                "ports": [22, 111, 2049, 6000, 3306, 5432, 8080],
                "ttl_range": (64, 128),
                "weight": 1
            },
            "macOS": {
                "indicators": [
                    "mac os", "darwin", "xnu", "apple", "macos", "os x",
                    "airport", "bonjour", "afp", "netatalk"
                ],
                "ports": [22, 88, 548, 631, 3689, 5000, 7000],
                "ttl_range": (64, 128),
                "weight": 1
            },
            "FreeBSD": {
                "indicators": [
                    "freebsd", "openbsd", "netbsd", "bsd", "pf/",
                    "ipfw", "pfctl"
                ],
                "ports": [22, 111, 2049, 8080],
                "ttl_range": (64, 128),
                "weight": 1
            },
            "Solaris": {
                "indicators": [
                    "solaris", "sunos", "sun microsystems", "illumos",
                    "openindiana"
                ],
                "ports": [22, 111, 4045, 32771],
                "ttl_range": (255, 255),
                "weight": 2
            },
            "AIX": {
                "indicators": [
                    "aix", "ibm aix", "rs6000"
                ],
                "ports": [22, 23, 79, 111],
                "ttl_range": (64, 128),
                "weight": 2
            },
            "Network Device": {
                "indicators": [
                    "cisco", "juniper", "hp", "brocade", "arista",
                    "ios", "junos", "nx-os"
                ],
                "ports": [23, 161, 179, 520, 22],
                "ttl_range": (255, 255),
                "weight": 3
            }
        }
    
    def _find_nmap(self) -> Optional[str]:
        """Trouve le chemin de Nmap"""
        import shutil
        return shutil.which("nmap")
    
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
    
    def detect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Détecte le système d'exploitation de la cible
        
        Args:
            target: Cible (IP ou hostname)
            **kwargs: Options de détection
        """
        print(f"  → Détection OS sur {target}")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Détection passive")
        
        results = {
            "success": True,
            "os": "unknown",
            "family": "unknown",
            "accuracy": 0,
            "method": "unknown",
            "indicators": [],
            "confidence_scores": {}
        }
        
        # Méthodes de détection (de la plus précise à la moins précise)
        detection_methods = [
            ("nmap", self._detect_with_nmap),
            ("ttl", self._detect_with_ping),
            ("banner", lambda t: self._detect_with_banners(t, kwargs.get('banners', []))),
            ("ports", lambda t: self._detect_with_ports(t, kwargs.get('open_ports', [])))
        ]
        
        for method_name, method_func in detection_methods:
            self._apply_stealth_delay()
            try:
                method_result = method_func(target)
                if method_result.get('success') and method_result.get('os') != 'unknown':
                    results.update(method_result)
                    results['method'] = method_name
                    results['confidence_scores'][method_name] = method_result.get('accuracy', 0)
                    break
            except Exception as e:
                if not self.stealth_mode:
                    print(f"    ⚠️ Erreur détection {method_name}: {e}")
        
        # Si toujours inconnu, utiliser la détection par ports si disponible
        if results['os'] == 'unknown' and kwargs.get('open_ports'):
            port_result = self._detect_with_ports(target, kwargs['open_ports'])
            if port_result.get('os') != 'unknown':
                results.update(port_result)
                results['method'] = 'ports'
        
        return results
    
    def _detect_with_nmap(self, target: str) -> Dict[str, Any]:
        """Détection OS via Nmap"""
        if not self.available:
            return {"success": False, "os": "unknown", "accuracy": 0}
        
        try:
            cmd = [self.nmap_path, "-O", "--osscan-guess", target]
            
            # Mode furtif: timing plus lent
            if self.stealth_mode:
                cmd.insert(1, "-T2")
                cmd.insert(2, "--osscan-limit")
            
            timeout = 90 if self.apt_mode else 60
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                return self._parse_nmap_os(result.stdout)
            else:
                return {"success": False, "os": "unknown", "accuracy": 0}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout", "os": "unknown", "accuracy": 0}
        except Exception as e:
            return {"success": False, "error": str(e), "os": "unknown", "accuracy": 0}
    
    def _parse_nmap_os(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Nmap pour l'OS"""
        result = {
            "success": True,
            "os": "unknown",
            "family": "unknown",
            "accuracy": 0,
            "details": {},
            "guesses": []
        }
        
        # Pattern pour OS détecté
        os_pattern = r'Running:\s+(.+)$'
        os_match = re.search(os_pattern, output, re.MULTILINE)
        if os_match:
            result["os"] = os_match.group(1).strip()
            result["accuracy"] = 70
        
        # Pattern pour la précision
        accuracy_pattern = r'OS CPE:\s+(.+)$'
        accuracy_match = re.search(accuracy_pattern, output, re.MULTILINE)
        if accuracy_match:
            result["details"]["cpe"] = accuracy_match.group(1)
            result["accuracy"] = 85
        
        # Pattern pour les guesses
        guess_pattern = r'OS guesses:\s+(.+)$'
        guess_match = re.search(guess_pattern, output, re.MULTILINE)
        if guess_match:
            guesses = guess_match.group(1).split(',')
            result["guesses"] = [g.strip() for g in guesses]
            result["accuracy"] = 60
        
        # Pattern pour l'agressivité
        if "OSScan" in output:
            result["method"] = "nmap_os_scan"
        
        # Classification par famille
        result["family"] = self._classify_os_family(result["os"])
        
        return result
    
    def _detect_with_ping(self, target: str) -> Dict[str, Any]:
        """Détection basique via ping (TTL)"""
        result = {
            "success": True,
            "os": "unknown",
            "family": "unknown",
            "method": "ttl_analysis",
            "accuracy": 40,
            "indicators": []
        }
        
        try:
            import platform
            if platform.system() == "Windows":
                cmd = ["ping", "-n", "1", target]
            else:
                cmd = ["ping", "-c", "1", target]
            
            ping_result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            # Extraire le TTL
            ttl_pattern = r'ttl[=\s](\d+)'
            ttl_match = re.search(ttl_pattern, ping_result.stdout.lower())
            
            if ttl_match:
                ttl = int(ttl_match.group(1))
                result["ttl"] = ttl
                result["indicators"].append(f"ttl={ttl}")
                
                # Détection basée sur le TTL initial
                for os_name, signature in self.os_signatures.items():
                    ttl_min, ttl_max = signature.get("ttl_range", (0, 255))
                    if ttl_min <= ttl <= ttl_max:
                        result["os"] = os_name
                        result["family"] = self._classify_os_family(os_name)
                        result["accuracy"] = 50
                        break
                else:
                    if ttl <= 64:
                        result["os"] = "Linux/Unix"
                        result["family"] = "Unix-like"
                    elif ttl <= 128:
                        result["os"] = "Windows"
                        result["family"] = "Windows"
                    elif ttl <= 255:
                        result["os"] = "Solaris/AIX"
                        result["family"] = "Unix-like"
            else:
                result["error"] = "No TTL found"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _detect_with_banners(self, target: str, banners: List[str]) -> Dict[str, Any]:
        """Détection OS via bannières de services"""
        result = {
            "success": True,
            "os": "unknown",
            "family": "unknown",
            "accuracy": 0,
            "indicators": []
        }
        
        if not banners:
            return result
        
        scores = {}
        for os_name, signature in self.os_signatures.items():
            score = 0
            for banner in banners:
                banner_lower = banner.lower()
                for indicator in signature["indicators"]:
                    if indicator in banner_lower:
                        score += 1
                        result["indicators"].append(f"{os_name}:{indicator}")
            if score > 0:
                scores[os_name] = score
        
        if scores:
            best_os = max(scores, key=scores.get)
            result["os"] = best_os
            result["family"] = self._classify_os_family(best_os)
            result["accuracy"] = min(100, scores[best_os] * 25)
        
        return result
    
    def _detect_with_ports(self, target: str, open_ports: List[int]) -> Dict[str, Any]:
        """Détection OS basée sur les ports ouverts typiques"""
        result = {
            "success": True,
            "os": "unknown",
            "family": "unknown",
            "accuracy": 0,
            "matches": []
        }
        
        if not open_ports:
            return result
        
        scores = {}
        for os_name, signature in self.os_signatures.items():
            score = 0
            for port in signature["ports"]:
                if port in open_ports:
                    score += signature["weight"]
            if score > 0:
                scores[os_name] = score
                result["matches"].append({"os": os_name, "score": score})
        
        if scores:
            best_os = max(scores, key=scores.get)
            result["os"] = best_os
            result["family"] = self._classify_os_family(best_os)
            result["accuracy"] = min(100, scores[best_os] * 20)
        
        return result
    
    def _classify_os_family(self, os_name: str) -> str:
        """Classifie l'OS par famille"""
        os_lower = os_name.lower()
        if any(x in os_lower for x in ['windows', 'microsoft', 'win']):
            return "Windows"
        elif any(x in os_lower for x in ['linux', 'ubuntu', 'debian', 'centos', 'red hat', 'fedora']):
            return "Linux"
        elif any(x in os_lower for x in ['mac', 'os x', 'darwin', 'apple']):
            return "macOS"
        elif any(x in os_lower for x in ['freebsd', 'openbsd', 'netbsd', 'bsd']):
            return "BSD"
        elif any(x in os_lower for x in ['solaris', 'sunos', 'aix', 'hp-ux']):
            return "Unix"
        elif any(x in os_lower for x in ['cisco', 'juniper', 'network']):
            return "Network Device"
        else:
            return "Unknown"
    
    def detect_by_banner(self, banner: str) -> Dict[str, Any]:
        """
        Détection OS via une seule bannière
        
        Args:
            banner: Bannière de service (SSH, HTTP, FTP, etc.)
        """
        return self._detect_with_banners("", [banner])
    
    def detect_by_ports(self, open_ports: List[int]) -> Dict[str, Any]:
        """
        Détection OS basée sur les ports ouverts
        
        Args:
            open_ports: Liste des ports ouverts
        """
        return self._detect_with_ports("", open_ports)
    
    def get_os_vulnerabilities(self, os_name: str) -> List[Dict[str, Any]]:
        """Retourne les vulnérabilités connues pour l'OS détecté"""
        vulns_db = {
            "Windows": [
                {"name": "EternalBlue (MS17-010)", "cve": "CVE-2017-0144", "severity": "critical", "year": 2017},
                {"name": "BlueKeep (CVE-2019-0708)", "cve": "CVE-2019-0708", "severity": "critical", "year": 2019},
                {"name": "PrintNightmare", "cve": "CVE-2021-34527", "severity": "high", "year": 2021},
                {"name": "Zerologon", "cve": "CVE-2020-1472", "severity": "critical", "year": 2020},
                {"name": "PetitPotam", "cve": "CVE-2021-36942", "severity": "medium", "year": 2021}
            ],
            "Linux": [
                {"name": "Dirty COW", "cve": "CVE-2016-5195", "severity": "high", "year": 2016},
                {"name": "Shellshock", "cve": "CVE-2014-6271", "severity": "critical", "year": 2014},
                {"name": "Heartbleed", "cve": "CVE-2014-0160", "severity": "high", "year": 2014},
                {"name": "Dirty Pipe", "cve": "CVE-2022-0847", "severity": "high", "year": 2022},
                {"name": "Polkit (PwnKit)", "cve": "CVE-2021-4034", "severity": "critical", "year": 2021}
            ],
            "macOS": [
                {"name": "Shrootless", "cve": "CVE-2021-30892", "severity": "high", "year": 2021},
                {"name": "Powerdir", "cve": "CVE-2022-26706", "severity": "medium", "year": 2022},
                {"name": "Migraine", "cve": "CVE-2023-32369", "severity": "high", "year": 2023}
            ],
            "Network Device": [
                {"name": "Cisco IOS RCE", "cve": "CVE-2018-0151", "severity": "critical", "year": 2018},
                {"name": "Juniper Backdoor", "cve": "CVE-2015-7755", "severity": "critical", "year": 2015}
            ]
        }
        
        os_lower = os_name.lower()
        for known_os, vulns in vulns_db.items():
            if known_os.lower() in os_lower:
                return vulns
        
        return []
    
    def get_os_recommendations(self, os_name: str) -> List[str]:
        """Retourne des recommandations pour l'OS détecté"""
        recommendations = {
            "Windows": [
                "Activer Windows Defender et les mises à jour automatiques",
                "Désactiver SMBv1 et les services inutiles",
                "Configurer le pare-feu pour bloquer les ports non essentiels",
                "Utiliser LAPS pour la gestion des mots de passe administrateur",
                "Activer la protection contre les exploits (Exploit Guard)"
            ],
            "Linux": [
                "Maintenir le noyau et les paquets à jour",
                "Désactiver les services inutiles",
                "Configurer SSH avec clés et désactiver l'authentification par mot de passe",
                "Utiliser SELinux ou AppArmor",
                "Configurer fail2ban pour prévenir les attaques par force brute"
            ],
            "macOS": [
                "Activer FileVault pour le chiffrement du disque",
                "Maintenir le système à jour",
                "Désactiver les services de partage inutiles",
                "Utiliser Gatekeeper et XProtect"
            ]
        }
        
        os_lower = os_name.lower()
        for known_os, recs in recommendations.items():
            if known_os.lower() in os_lower:
                return recs
        
        return [
            "Maintenir le système d'exploitation à jour",
            "Désactiver les services et ports inutiles",
            "Configurer un pare-feu",
            "Surveiller les logs système"
        ]
    
    def get_version_info(self) -> Dict[str, Any]:
        """Retourne la version de l'outil de détection OS"""
        if self.available:
            return {
                "available": True,
                "tool": "nmap",
                "path": self.nmap_path,
                "detection_methods": ["nmap", "ttl", "banner", "ports"]
            }
        return {
            "available": False,
            "detection_methods": ["ttl", "banner", "ports"]
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de OSDetector")
    print("=" * 60)
    
    detector = OSDetector()
    
    # Configuration mode APT
    detector.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Test (simulé)
    # result = detector.detect("localhost")
    # print(f"OS détecté: {result['os']}")
    
    print("\n✅ Module OSDetector chargé avec succès")