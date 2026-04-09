#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour Nmap - Scan réseau et découverte de services
Version avec support furtif, APT et détection avancée
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from src.connectors.base_connector import BaseConnector


class NmapConnector(BaseConnector):
    """Connecteur avancé pour Nmap avec support furtif"""
    
    def __init__(self, tool_path: Optional[str] = None):
        """
        Initialise le connecteur Nmap
        
        Args:
            tool_path: Chemin personnalisé vers l'exécutable Nmap
        """
        super().__init__(tool_path)
        self.common_ports = "22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080"
        self.timing_templates = {
            'paranoid': 0,
            'sneaky': 1,
            'polite': 2,
            'normal': 3,
            'aggressive': 4,
            'insane': 5
        }
    
    def _find_tool(self) -> Optional[str]:
        """Trouve l'exécutable Nmap"""
        import shutil
        
        paths = [
            "nmap",
            "/usr/bin/nmap",
            "/usr/local/bin/nmap",
            "/opt/nmap/bin/nmap"
        ]
        
        for path in paths:
            if path and shutil.which(path):
                return path
        
        return None
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute un scan Nmap sur la cible
        
        Args:
            target: Cible (IP, hostname, ou réseau)
            **kwargs:
                - ports: Ports à scanner (ex: '80,443' ou '1-1000')
                - scan_type: Type de scan ('syn', 'tcp', 'udp', 'ping')
                - service_detection: Détection des services (-sV)
                - os_detection: Détection OS (-O)
                - scripts: Scripts NSE à exécuter
                - aggressive: Mode agressif (-A)
                - timing: Timing template (0-5)
                - min_rate: Taux minimum de paquets par seconde
                - max_rate: Taux maximum de paquets par seconde
                - host_timeout: Timeout par hôte
                - scan_delay: Délai entre les probes
        """
        if not self.available:
            return {
                "success": False,
                "error": "Nmap non installé",
                "open_ports": [],
                "apt_mode": self.apt_mode
            }
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        cmd = [self.tool_path]
        
        # Mode APT: réduire l'agressivité
        if self.apt_mode:
            kwargs.setdefault('timing', 1)  # sneaky
            kwargs.setdefault('scan_delay', '1s')
            kwargs.setdefault('min_rate', 10)
            kwargs.setdefault('max_rate', 50)
            kwargs['verbose'] = False
        
        # Type de scan
        scan_type = kwargs.get('scan_type', 'syn')
        if scan_type == 'syn':
            cmd.append('-sS')
        elif scan_type == 'tcp':
            cmd.append('-sT')
        elif scan_type == 'udp':
            cmd.append('-sU')
        elif scan_type == 'ping':
            cmd.append('-sn')
        
        # Ports
        ports = kwargs.get('ports')
        if ports:
            cmd.extend(['-p', ports])
        else:
            cmd.extend(['-p', self.common_ports])
        
        # Détection de services
        if kwargs.get('service_detection', True):
            cmd.append('-sV')
            # Version intensity (mode furtif = moins intense)
            intensity = 7 if not self.apt_mode else 3
            cmd.extend(['--version-intensity', str(intensity)])
        
        # Détection OS
        if kwargs.get('os_detection'):
            cmd.append('-O')
            if self.apt_mode:
                cmd.append('--osscan-limit')  # Limiter l'analyse OS
        
        # Scripts NSE
        scripts = kwargs.get('scripts')
        if scripts:
            if isinstance(scripts, list):
                scripts = ','.join(scripts)
            cmd.extend(['--script', scripts])
        
        # Mode agressif (désactivé en mode APT)
        if kwargs.get('aggressive') and not self.apt_mode:
            cmd.append('-A')
        
        # Timing template
        timing = kwargs.get('timing', 3)
        if timing in self.timing_templates:
            cmd.extend(['-T', str(self.timing_templates[timing])])
        
        # Rate limiting (mode furtif)
        min_rate = kwargs.get('min_rate')
        if min_rate:
            cmd.extend(['--min-rate', str(min_rate)])
        
        max_rate = kwargs.get('max_rate')
        if max_rate:
            cmd.extend(['--max-rate', str(max_rate)])
        
        # Délai entre les probes
        scan_delay = kwargs.get('scan_delay')
        if scan_delay:
            cmd.extend(['--scan-delay', scan_delay])
        elif self.stealth_config.get('random_delays', False):
            min_delay, max_delay = self.stealth_config.get('delay', (0.5, 1.5))
            avg_delay = (min_delay + max_delay) / 2
            cmd.extend(['--scan-delay', f"{avg_delay}s"])
        
        # Timeout par hôte
        host_timeout = kwargs.get('host_timeout')
        if host_timeout:
            cmd.extend(['--host-timeout', host_timeout])
        elif self.apt_mode:
            cmd.extend(['--host-timeout', '300s'])
        
        # Verbosité (désactivée en mode APT)
        if kwargs.get('verbose') and not self.apt_mode:
            cmd.append('-v')
        elif self.apt_mode:
            cmd.append('-q')  # Mode silencieux
        
        # Désactivation de la résolution DNS (plus rapide et plus discret)
        if kwargs.get('no_dns', True):
            cmd.append('-n')
        
        # Sortie XML
        xml_output = kwargs.get('xml_output')
        temp_xml = None
        if not xml_output:
            temp_xml = self.create_temp_output_file(".xml")
            xml_output = temp_xml
        
        cmd.extend(['-oX', xml_output])
        
        # Cible
        cmd.append(target)
        
        timeout = kwargs.get('timeout', 600)
        
        # Exécution
        result = self.execute_command(cmd, timeout=timeout)
        
        # Parser la sortie XML
        if Path(xml_output).exists():
            parsed = self.parse_xml_output(xml_output)
        else:
            parsed = self.parse_output(result["stdout"])
        
        # Nettoyer le fichier XML temporaire
        if temp_xml:
            self.cleanup_temp_file(temp_xml)
        
        if result["success"] or (result["returncode"] == 0):
            return {
                "success": True,
                "target": target,
                "open_ports": parsed.get("open_ports", []),
                "services": parsed.get("services", []),
                "os": parsed.get("os", {}),
                "hostnames": parsed.get("hostnames", []),
                "count": len(parsed.get("open_ports", [])),
                "raw_output": result["stdout"],
                "execution_time": result.get("execution_time", 0),
                "command_used": ' '.join(cmd),
                "apt_mode": self.apt_mode
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Erreur lors du scan"),
                "stderr": result.get("stderr", ""),
                "open_ports": [],
                "apt_mode": self.apt_mode
            }
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        """
        Parse la sortie texte de Nmap
        
        Args:
            output: Sortie brute de Nmap
            
        Returns:
            Dictionnaire structuré des résultats
        """
        result = {
            "open_ports": [],
            "services": [],
            "os": {},
            "hostnames": []
        }
        
        # Pattern pour ports ouverts
        port_pattern = r'(\d+)/(tcp|udp)\s+open\s+(\S+)\s+(?:.+)'
        
        for line in output.split('\n'):
            # Ports ouverts
            match = re.search(port_pattern, line)
            if match:
                port_info = {
                    "port": int(match.group(1)),
                    "protocol": match.group(2),
                    "service": match.group(3)
                }
                result["open_ports"].append(port_info["port"])
                result["services"].append(port_info)
            
            # Détection OS
            if "OS details:" in line:
                os_info = line.split("OS details:")[1].strip()
                result["os"] = {"name": os_info, "accuracy": "unknown"}
            
            # Hostnames
            if "Nmap scan report for" in line:
                hostname_match = re.search(r'for\s+(\S+)', line)
                if hostname_match:
                    result["hostnames"].append(hostname_match.group(1))
        
        return result
    
    def parse_xml_output(self, xml_file: str) -> Dict[str, Any]:
        """
        Parse la sortie XML de Nmap
        
        Args:
            xml_file: Chemin du fichier XML
            
        Returns:
            Dictionnaire structuré des résultats
        """
        result = {
            "open_ports": [],
            "services": [],
            "os": {},
            "hostnames": [],
            "scan_info": {}
        }
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Informations de scan
            scan_info = root.find('scaninfo')
            if scan_info is not None:
                result["scan_info"] = {
                    "type": scan_info.get('type', ''),
                    "protocol": scan_info.get('protocol', ''),
                    "services": scan_info.get('services', '')
                }
            
            # Hostnames
            for hostname in root.findall(".//hostname"):
                result["hostnames"].append({
                    "name": hostname.get('name', ''),
                    "type": hostname.get('type', '')
                })
            
            # Ports ouverts
            for port in root.findall(".//port"):
                port_id = port.get('portid')
                protocol = port.get('protocol')
                state = port.find('state')
                
                if state is not None and state.get('state') == 'open':
                    port_num = int(port_id)
                    result["open_ports"].append(port_num)
                    
                    service = port.find('service')
                    service_info = {
                        "port": port_num,
                        "protocol": protocol,
                        "service": service.get('name') if service is not None else 'unknown'
                    }
                    
                    if service is not None:
                        if service.get('product'):
                            service_info["product"] = service.get('product')
                        if service.get('version'):
                            service_info["version"] = service.get('version')
                        if service.get('extrainfo'):
                            service_info["extra"] = service.get('extrainfo')
                    
                    # Script output
                    script_elem = port.find(".//script")
                    if script_elem is not None:
                        service_info["script_output"] = script_elem.get('output', '')[:500]
                    
                    result["services"].append(service_info)
            
            # OS détection
            os = root.find(".//os/osmatch")
            if os is not None:
                result["os"] = {
                    "name": os.get('name'),
                    "accuracy": os.get('accuracy'),
                    "line": os.get('line', '')
                }
            
            # Temps d'exécution
            run_stats = root.find('runstats')
            if run_stats is not None:
                finished = run_stats.find('finished')
                if finished is not None:
                    result["scan_time"] = finished.get('timestr', '')
                    result["scan_duration"] = finished.get('elapsed', '')
                
        except Exception as e:
            if not self.apt_mode:
                print(f"Erreur parsing XML: {e}")
        
        return result
    
    def quick_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """Scan rapide des ports les plus communs"""
        kwargs['ports'] = self.common_ports
        kwargs['service_detection'] = False
        kwargs['timing'] = 4  # aggressive
        return self.scan(target, **kwargs)
    
    def full_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """Scan complet avec détection avancée"""
        kwargs['ports'] = '1-65535'
        kwargs['service_detection'] = True
        kwargs['os_detection'] = True
        kwargs['aggressive'] = True
        kwargs['timing'] = 3
        return self.scan(target, **kwargs)
    
    def stealth_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """Scan furtif pour éviter la détection"""
        kwargs['scan_type'] = 'syn'
        kwargs['timing'] = 1  # sneaky
        kwargs['scan_delay'] = '2s'
        kwargs['min_rate'] = 10
        kwargs['max_rate'] = 50
        kwargs['no_dns'] = True
        kwargs['verbose'] = False
        return self.scan(target, **kwargs)
    
    def scan_network(self, network: str, **kwargs) -> Dict[str, Any]:
        """Scanne un réseau entier"""
        kwargs['scan_type'] = 'ping'
        kwargs['ports'] = ''
        return self.scan(network, **kwargs)
    
    def detect_os(self, target: str, **kwargs) -> Dict[str, Any]:
        """Détection d'OS uniquement"""
        kwargs['os_detection'] = True
        kwargs['service_detection'] = False
        kwargs['ports'] = '80,443'
        return self.scan(target, **kwargs)
    
    def scan_udp(self, target: str, **kwargs) -> Dict[str, Any]:
        """Scan UDP"""
        kwargs['scan_type'] = 'udp'
        kwargs['ports'] = kwargs.get('ports', '53,67,68,123,161,500,520,631,1434')
        return self.scan(target, **kwargs)
    
    def vulnerability_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """Scan de vulnérabilités avec scripts NSE"""
        vuln_scripts = [
            "vuln",
            "exploit",
            "malware",
            "auth",
            "dos"
        ]
        kwargs['scripts'] = vuln_scripts
        kwargs['service_detection'] = True
        return self.scan(target, **kwargs)
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de version de Nmap
        
        Returns:
            Dictionnaire avec les informations de version
        """
        if not self.available:
            return {"available": False}
        
        result = self.execute_command([self.tool_path, "--version"], stealth=False)
        
        if result["success"]:
            version_line = result["stdout"].split('\n')[0] if result["stdout"] else ""
            return {
                "available": True,
                "version": version_line,
                "tool": "nmap",
                "path": self.tool_path
            }
        
        return {"available": False, "error": result.get("error")}