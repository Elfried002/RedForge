#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de scan Nmap pour RedForge
Découverte des ports ouverts, services et vulnérabilités réseau
Version avec support furtif, APT et détection avancée
"""

import subprocess
import re
import xml.etree.ElementTree as ET
import tempfile
import time
import random
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from src.core.stealth_engine import StealthEngine


class NmapScanner:
    """Scanner Nmap avancé pour la reconnaissance réseau avec support furtif"""
    
    def __init__(self):
        self.nmap_path = self._find_nmap()
        self.available = self.nmap_path is not None
        self.stealth_mode = False
        self.apt_mode = False
        self.stealth_engine = StealthEngine()
    
    def _find_nmap(self) -> Optional[str]:
        """Trouve le chemin de l'exécutable Nmap"""
        import shutil
        
        paths = ["nmap", "/usr/bin/nmap", "/usr/local/bin/nmap", "/opt/nmap/bin/nmap"]
        
        for path in paths:
            if shutil.which(path):
                return path
        
        return None
    
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
    
    def quick_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scan rapide des ports les plus communs
        
        Args:
            target: Cible (IP, hostname)
            **kwargs: Options supplémentaires
        """
        ports = kwargs.get('ports', '22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080')
        return self._run_nmap(target, ports=ports, service_detection=False, **kwargs)
    
    def stealth_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scan furtif avec timing lent pour éviter la détection
        
        Args:
            target: Cible
            **kwargs: Options supplémentaires
        """
        kwargs['timing'] = 1  # Sneaky
        kwargs['scan_type'] = 'syn'
        kwargs['no_dns'] = True
        kwargs['min_rate'] = 10
        kwargs['max_rate'] = 50
        kwargs['host_timeout'] = '10m'
        return self._run_nmap(target, **kwargs)
    
    def full_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scan complet avec détection de services et OS
        
        Args:
            target: Cible
            **kwargs: Options supplémentaires
        """
        ports = kwargs.get('ports', '1-10000')
        return self._run_nmap(
            target, 
            ports=ports,
            service_detection=True,
            os_detection=True,
            script_scan=True,
            **kwargs
        )
    
    def _run_nmap(self, target: str, **options) -> Dict[str, Any]:
        """
        Exécute un scan Nmap avec les options spécifiées
        
        Args:
            target: Cible à scanner
            **options: Options Nmap
        """
        if not self.available:
            return {
                "success": False,
                "error": "Nmap non installé",
                "open_ports": [],
                "apt_mode": self.apt_mode
            }
        
        # Appliquer délai furtif
        self._apply_stealth_delay()
        
        cmd = [self.nmap_path]
        
        # Mode APT: timing très lent
        if self.apt_mode:
            options['timing'] = 0  # Paranoid
            options['no_dns'] = True
            options['min_rate'] = 5
            options['max_rate'] = 20
            options['host_timeout'] = '30m'
        
        # Type de scan
        scan_type = options.get('scan_type', 'syn')
        if scan_type == 'syn':
            cmd.append('-sS')
        elif scan_type == 'tcp':
            cmd.append('-sT')
        elif scan_type == 'udp':
            cmd.append('-sU')
        elif scan_type == 'ping':
            cmd.append('-sn')
        
        # Ports
        ports = options.get('ports')
        if ports:
            cmd.extend(['-p', ports])
        elif options.get('all_ports', False):
            cmd.extend(['-p-'])  # Tous les ports (1-65535)
        
        # Détection de services
        if options.get('service_detection', True):
            cmd.append('-sV')
            # Réduire l'intensité en mode furtif
            if self.stealth_mode:
                cmd.extend(['--version-intensity', '5'])
        
        # Détection OS
        if options.get('os_detection') and not self.apt_mode:  # OS detection trop bruyante en APT
            cmd.append('-O')
            if self.stealth_mode:
                cmd.append('--osscan-limit')
        
        # Scan de scripts
        if options.get('script_scan'):
            scripts = options.get('scripts', 'default')
            cmd.extend(['--script', scripts])
        
        # Timing template (0-5, 0=paranoid, 5=insane)
        timing = options.get('timing', 3)
        if self.apt_mode:
            timing = 0
        elif self.stealth_mode:
            timing = min(timing, 2)
        cmd.extend(['-T', str(timing)])
        
        # Rate limiting (mode furtif)
        min_rate = options.get('min_rate')
        if min_rate:
            cmd.extend(['--min-rate', str(min_rate)])
        
        max_rate = options.get('max_rate')
        if max_rate:
            cmd.extend(['--max-rate', str(max_rate)])
        
        # Délai entre les probes
        scan_delay = options.get('scan_delay')
        if scan_delay:
            cmd.extend(['--scan-delay', scan_delay])
        elif self.stealth_mode:
            cmd.extend(['--scan-delay', '1s'])
        
        # Host timeout
        host_timeout = options.get('host_timeout')
        if host_timeout:
            cmd.extend(['--host-timeout', host_timeout])
        elif self.apt_mode:
            cmd.extend(['--host-timeout', '30m'])
        
        # Désactiver la résolution DNS inversée (plus rapide et plus discret)
        if options.get('no_dns', True):
            cmd.append('-n')
        
        # Sortie XML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp:
            xml_file = tmp.name
        cmd.extend(['-oX', xml_file])
        
        # Verbosité (désactivée en mode furtif)
        if options.get('verbose') and not self.stealth_mode:
            cmd.append('-v')
        elif self.apt_mode:
            cmd.append('-q')  # Mode silencieux
        
        # Cible
        cmd.append(target)
        
        timeout = options.get('timeout', 600)
        if self.apt_mode:
            timeout = 1800  # 30 minutes pour APT
        
        print(f"    → Scan Nmap sur {target} (timing: T{timing})...")
        
        # Exécution
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            execution_time = time.time() - start_time
            
            if result.returncode == 0 or result.returncode == 1:
                parsed = self._parse_xml_output(xml_file)
                
                # Nettoyer le fichier temporaire
                Path(xml_file).unlink(missing_ok=True)
                
                return {
                    "success": True,
                    "target": target,
                    "open_ports": parsed.get("open_ports", []),
                    "services": parsed.get("services", []),
                    "os": parsed.get("os", {}),
                    "host_status": parsed.get("host_status", "down"),
                    "scan_time": parsed.get("scan_time", ""),
                    "execution_time": execution_time,
                    "command_used": ' '.join(cmd[:10]) + '...',
                    "stealth_mode": self.stealth_mode,
                    "apt_mode": self.apt_mode,
                    "raw_output": result.stdout[:1000] if result.stdout else ""
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "open_ports": [],
                    "apt_mode": self.apt_mode
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Scan timeout après {timeout}s",
                "open_ports": [],
                "apt_mode": self.apt_mode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "open_ports": [],
                "apt_mode": self.apt_mode
            }
    
    def _parse_xml_output(self, xml_file: str) -> Dict[str, Any]:
        """Parse la sortie XML de Nmap"""
        result = {
            "open_ports": [],
            "services": [],
            "os": {},
            "host_status": "unknown",
            "scan_time": ""
        }
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Heure du scan
            scan_info = root.find('scaninfo')
            if scan_info is not None:
                result["scan_time"] = scan_info.get('starttime', '')
            
            # Host
            host = root.find('host')
            if host is not None:
                # Status
                status = host.find('status')
                if status is not None:
                    result["host_status"] = status.get('state', 'unknown')
                
                # Ports ouverts
                ports = host.find('ports')
                if ports is not None:
                    for port in ports.findall('port'):
                        port_id = port.get('portid')
                        protocol = port.get('protocol')
                        state_elem = port.find('state')
                        
                        if state_elem is not None and state_elem.get('state') == 'open':
                            result["open_ports"].append(int(port_id))
                            
                            service_elem = port.find('service')
                            service_info = {
                                "port": int(port_id),
                                "protocol": protocol,
                                "service": service_elem.get('name', 'unknown') if service_elem is not None else 'unknown'
                            }
                            
                            if service_elem is not None:
                                service_info["product"] = service_elem.get('product', '')
                                service_info["version"] = service_elem.get('version', '')
                                service_info["extra_info"] = service_elem.get('extrainfo', '')
                                service_info["service_tunnel"] = service_elem.get('tunnel', '')
                            
                            result["services"].append(service_info)
                
                # OS détection
                os_elem = host.find('os')
                if os_elem is not None:
                    osmatch = os_elem.find('osmatch')
                    if osmatch is not None:
                        result["os"] = {
                            "name": osmatch.get('name', 'unknown'),
                            "accuracy": int(osmatch.get('accuracy', '0')),
                            "type": osmatch.get('osclass', '')
                        }
                        
                        # Plus de détails OS
                        osclass = osmatch.find('osclass')
                        if osclass is not None:
                            result["os"]["family"] = osclass.get('osfamily', '')
                            result["os"]["generation"] = osclass.get('osgen', '')
                            result["os"]["vendor"] = osclass.get('vendor', '')
        
        except Exception as e:
            if not self.stealth_mode:
                print(f"    ⚠️ Erreur parsing XML: {e}")
        
        return result
    
    def scan_network(self, network: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne un réseau entier pour découvrir les hôtes actifs
        
        Args:
            network: Réseau au format CIDR (ex: 192.168.1.0/24)
        """
        kwargs['scan_type'] = 'ping'
        kwargs['ports'] = ''
        return self._run_nmap(network, **kwargs)
    
    def scan_udp_ports(self, target: str, ports: str = '1-1000') -> Dict[str, Any]:
        """Scan spécifique des ports UDP"""
        return self._run_nmap(target, ports=ports, scan_type='udp', service_detection=True)
    
    def detect_vulners(self, target: str) -> Dict[str, Any]:
        """Détecte les vulnérabilités connues avec le script vulners"""
        return self._run_nmap(target, script_scan='vulners', service_detection=True)
    
    def get_services_info(self, target: str) -> List[Dict[str, Any]]:
        """Retourne des informations détaillées sur les services"""
        result = self.full_scan(target)
        return result.get('services', [])
    
    def scan_with_fingerprinting(self, target: str) -> Dict[str, Any]:
        """Scan avec fingerprinting avancé (-A)"""
        return self._run_nmap(target, service_detection=True, os_detection=True, 
                              script_scan=True, timing=3)
    
    def get_version_info(self) -> Dict[str, Any]:
        """Retourne la version de Nmap"""
        if not self.available:
            return {"available": False}
        
        try:
            result = subprocess.run([self.nmap_path, "--version"], 
                                   capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                return {
                    "available": True,
                    "version": version_line,
                    "path": self.nmap_path
                }
        except:
            pass
        
        return {"available": False}


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de NmapScanner")
    print("=" * 60)
    
    scanner = NmapScanner()
    
    # Configuration mode APT
    scanner.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Test (simulé)
    # result = scanner.quick_scan("localhost")
    # print(f"Ports ouverts: {result['open_ports']}")
    
    print("\n✅ Module NmapScanner chargé avec succès")