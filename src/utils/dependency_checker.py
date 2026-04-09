#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de vérification des dépendances pour RedForge
Vérifie que tous les outils requis sont installés
Version avec support furtif, APT et vérification avancée
"""

import subprocess
import shutil
import sys
import os
import re
import platform
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from src.utils.color_output import console


class DependencyChecker:
    """Vérificateur de dépendances système avancé avec support APT"""
    
    # Dépendances requises
    REQUIRED_TOOLS = {
        'nmap': {
            'cmd': 'nmap',
            'description': 'Scan réseau et ports',
            'min_version': '7.0',
            'install_cmd': 'sudo apt install nmap -y',
            'critical': True
        },
        'sqlmap': {
            'cmd': 'sqlmap',
            'description': 'Injection SQL',
            'min_version': '1.6',
            'install_cmd': 'sudo apt install sqlmap -y',
            'critical': True
        },
        'whatweb': {
            'cmd': 'whatweb',
            'description': 'Détection de technologies',
            'min_version': '0.5',
            'install_cmd': 'sudo apt install whatweb -y',
            'critical': True
        },
        'msfconsole': {
            'cmd': 'msfconsole',
            'description': 'Metasploit Framework',
            'min_version': '6.0',
            'install_cmd': 'sudo apt install metasploit-framework -y',
            'critical': False
        },
        'hydra': {
            'cmd': 'hydra',
            'description': 'Force brute',
            'min_version': '9.0',
            'install_cmd': 'sudo apt install hydra -y',
            'critical': False
        },
        'dirb': {
            'cmd': 'dirb',
            'description': 'Force brute de répertoires',
            'min_version': '2.22',
            'install_cmd': 'sudo apt install dirb -y',
            'critical': False
        },
        'wafw00f': {
            'cmd': 'wafw00f',
            'description': 'Détection WAF',
            'min_version': '2.1',
            'install_cmd': 'pip3 install wafw00f',
            'critical': False
        },
        'gobuster': {
            'cmd': 'gobuster',
            'description': 'Force brute de répertoires (Go)',
            'min_version': '3.0',
            'install_cmd': 'sudo apt install gobuster -y',
            'critical': False
        },
        'ffuf': {
            'cmd': 'ffuf',
            'description': 'Fuzzing web',
            'min_version': '1.5',
            'install_cmd': 'sudo apt install ffuf -y',
            'critical': False
        },
        'nikto': {
            'cmd': 'nikto',
            'description': 'Scan de vulnérabilités web',
            'min_version': '2.5',
            'install_cmd': 'sudo apt install nikto -y',
            'critical': False
        }
    }
    
    # Dépendances Python optionnelles
    OPTIONAL_PYTHON_PACKAGES = {
        'pymetasploit3': {
            'import_name': 'pymetasploit3',
            'description': 'Client Metasploit RPC',
            'install_cmd': 'pip3 install pymetasploit3',
            'critical': False
        },
        'python-nmap': {
            'import_name': 'nmap',
            'description': 'Wrapper Nmap Python',
            'install_cmd': 'pip3 install python-nmap',
            'critical': False
        },
        'requests': {
            'import_name': 'requests',
            'description': 'Requêtes HTTP',
            'install_cmd': 'pip3 install requests',
            'critical': True
        },
        'bs4': {
            'import_name': 'bs4',
            'description': 'Parsing HTML',
            'install_cmd': 'pip3 install beautifulsoup4',
            'critical': True
        },
        'cryptography': {
            'import_name': 'cryptography',
            'description': 'Cryptographie',
            'install_cmd': 'pip3 install cryptography',
            'critical': True
        },
        'paramiko': {
            'import_name': 'paramiko',
            'description': 'Client SSH',
            'install_cmd': 'pip3 install paramiko',
            'critical': False
        },
        'dnspython': {
            'import_name': 'dns',
            'description': 'DNS Python',
            'install_cmd': 'pip3 install dnspython',
            'critical': False
        },
        'flask': {
            'import_name': 'flask',
            'description': 'Framework web pour GUI',
            'install_cmd': 'pip3 install flask flask-socketio flask-cors',
            'critical': False
        }
    }
    
    @classmethod
    def check_all(cls, verbose: bool = True, quick: bool = False) -> Dict[str, Any]:
        """
        Vérifie toutes les dépendances
        
        Args:
            verbose: Afficher les résultats détaillés
            quick: Mode rapide (ignore les versions)
        """
        results = {
            'tools': {},
            'python_packages': {},
            'missing': [],
            'critical_missing': [],
            'all_ok': True,
            'timestamp': datetime.now().isoformat()
        }
        
        if verbose:
            console.print_header("Vérification des dépendances")
        
        # Vérifier les outils système
        for tool_name, tool_info in cls.REQUIRED_TOOLS.items():
            result = cls.check_tool(tool_name, tool_info, quick)
            results['tools'][tool_name] = result
            
            if not result['installed']:
                missing_entry = {
                    'type': 'tool',
                    'name': tool_name,
                    'install_cmd': tool_info['install_cmd'],
                    'critical': tool_info.get('critical', False)
                }
                results['missing'].append(missing_entry)
                
                if tool_info.get('critical', False):
                    results['critical_missing'].append(missing_entry)
                    results['all_ok'] = False
            
            if verbose:
                status = "✅" if result['installed'] else "❌" if tool_info.get('critical', False) else "⚠️"
                version_str = f" v{result['version']}" if result['version'] else ""
                console.print_info(f"{status} {tool_name}{version_str}: {tool_info['description']}")
        
        # Vérifier les packages Python
        for pkg_name, pkg_info in cls.OPTIONAL_PYTHON_PACKAGES.items():
            result = cls.check_python_package(pkg_name, pkg_info)
            results['python_packages'][pkg_name] = result
            
            if not result['installed']:
                missing_entry = {
                    'type': 'python',
                    'name': pkg_name,
                    'install_cmd': pkg_info['install_cmd'],
                    'critical': pkg_info.get('critical', False)
                }
                results['missing'].append(missing_entry)
                
                if pkg_info.get('critical', False):
                    results['critical_missing'].append(missing_entry)
                    results['all_ok'] = False
            
            if verbose:
                status = "✅" if result['installed'] else "❌" if pkg_info.get('critical', False) else "⚠️"
                version_str = f" v{result['version']}" if result['version'] else ""
                console.print_info(f"{status} {pkg_name}{version_str}: {pkg_info['description']}")
        
        if verbose:
            if results['all_ok']:
                console.print_success("Toutes les dépendances requises sont installées")
            elif results['critical_missing']:
                console.print_error("Des dépendances critiques sont manquantes")
                cls.print_install_instructions(results['critical_missing'])
            else:
                console.print_warning("Certaines dépendances optionnelles sont manquantes")
                cls.print_install_instructions(results['missing'], show_critical_only=False)
        
        return results
    
    @classmethod
    def check_tool(cls, tool_name: str, tool_info: Dict, quick: bool = False) -> Dict[str, Any]:
        """
        Vérifie si un outil système est installé
        
        Args:
            tool_name: Nom de l'outil
            tool_info: Informations sur l'outil
            quick: Mode rapide (ignore les versions)
        """
        result = {
            'installed': False,
            'version': None,
            'path': None,
            'min_version_ok': True,
            'error': None
        }
        
        # Trouver l'exécutable
        cmd = tool_info.get('cmd', tool_name)
        path = shutil.which(cmd)
        
        if path:
            result['installed'] = True
            result['path'] = path
            
            if not quick:
                # Récupérer la version
                try:
                    proc = subprocess.run(
                        [cmd, '--version'], 
                        capture_output=True, 
                        text=True, 
                        timeout=5
                    )
                    output = proc.stdout + proc.stderr
                    
                    # Extraire la version
                    version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', output)
                    if version_match:
                        result['version'] = version_match.group(1)
                        
                        # Vérifier la version minimale
                        if 'min_version' in tool_info:
                            result['min_version_ok'] = cls._compare_versions(
                                result['version'], 
                                tool_info['min_version']
                            )
                except subprocess.TimeoutExpired:
                    result['error'] = "Timeout"
                except Exception as e:
                    result['error'] = str(e)
        
        return result
    
    @classmethod
    def check_python_package(cls, package_name: str, 
                            package_info: Dict) -> Dict[str, Any]:
        """
        Vérifie si un package Python est installé
        
        Args:
            package_name: Nom du package
            package_info: Informations du package
        """
        result = {
            'installed': False,
            'version': None
        }
        
        import_name = package_info.get('import_name', package_name)
        
        try:
            module = __import__(import_name)
            result['installed'] = True
            
            # Récupérer la version si disponible
            if hasattr(module, '__version__'):
                result['version'] = module.__version__
            elif hasattr(module, 'version'):
                result['version'] = module.version
            elif hasattr(module, 'VERSION'):
                result['version'] = module.VERSION
        except ImportError:
            pass
        
        return result
    
    @classmethod
    def _compare_versions(cls, version1: str, version2: str) -> bool:
        """
        Compare deux versions
        
        Args:
            version1: Version installée
            version2: Version minimale requise
        """
        def normalize(v):
            return [int(x) for x in v.split('.')]
        
        try:
            v1 = normalize(version1)
            v2 = normalize(version2)
            
            for i in range(max(len(v1), len(v2))):
                v1_val = v1[i] if i < len(v1) else 0
                v2_val = v2[i] if i < len(v2) else 0
                
                if v1_val < v2_val:
                    return False
                elif v1_val > v2_val:
                    return True
            return True
        except:
            return True
    
    @classmethod
    def print_install_instructions(cls, missing: List[Dict], show_critical_only: bool = True):
        """
        Affiche les instructions d'installation
        
        Args:
            missing: Liste des dépendances manquantes
            show_critical_only: N'afficher que les dépendances critiques
        """
        if not missing:
            return
        
        to_install = missing if not show_critical_only else [m for m in missing if m.get('critical', False)]
        
        if not to_install:
            return
        
        console.print_warning("\n📦 Dépendances à installer :")
        
        # Grouper par type
        tools = [d for d in to_install if d['type'] == 'tool']
        python_pkgs = [d for d in to_install if d['type'] == 'python']
        
        if tools:
            console.print_info("\n  🛠️ Outils système:")
            for dep in tools:
                console.print_info(f"    {dep['name']}: {dep['install_cmd']}")
        
        if python_pkgs:
            console.print_info("\n  🐍 Packages Python:")
            for dep in python_pkgs:
                console.print_info(f"    {dep['name']}: {dep['install_cmd']}")
        
        console.print_info("\n💡 Installation automatique:")
        console.print_info("  sudo ./install.sh")
        console.print_info("  ou")
        console.print_info("  python3 setup.py install")
    
    @classmethod
    def get_missing_tools(cls, critical_only: bool = False) -> List[str]:
        """Retourne la liste des outils manquants"""
        missing = []
        for tool_name, tool_info in cls.REQUIRED_TOOLS.items():
            if critical_only and not tool_info.get('critical', False):
                continue
            result = cls.check_tool(tool_name, tool_info, quick=True)
            if not result['installed']:
                missing.append(tool_name)
        return missing
    
    @classmethod
    def get_missing_packages(cls, critical_only: bool = False) -> List[str]:
        """Retourne la liste des packages Python manquants"""
        missing = []
        for pkg_name, pkg_info in cls.OPTIONAL_PYTHON_PACKAGES.items():
            if critical_only and not pkg_info.get('critical', False):
                continue
            result = cls.check_python_package(pkg_name, pkg_info)
            if not result['installed']:
                missing.append(pkg_name)
        return missing
    
    @classmethod
    def is_metasploit_running(cls) -> bool:
        """Vérifie si le service Metasploit RPC est en cours d'exécution"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 55553))
            sock.close()
            return result == 0
        except:
            return False
    
    @classmethod
    def start_metasploit_rpc(cls) -> bool:
        """Démarre le service Metasploit RPC"""
        try:
            subprocess.Popen(
                ['msfrpcd', '-P', 'RedForge2024', '-S', '-p', '55553'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            import time
            time.sleep(5)
            return cls.is_metasploit_running()
        except:
            return False
    
    @classmethod
    def check_environment(cls) -> Dict[str, Any]:
        """
        Vérifie l'environnement global
        
        Returns:
            Dictionnaire avec les informations d'environnement
        """
        env_info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'python_version': sys.version,
            'python_executable': sys.executable,
            'is_kali': cls._is_kali(),
            'is_parrot': cls._is_parrot(),
            'is_debian': cls._is_debian(),
            'is_ubuntu': cls._is_ubuntu(),
            'is_root': cls._is_root(),
            'home_dir': str(Path.home()),
            'redforge_dir': str(Path.home() / '.RedForge'),
            'disk_free_gb': cls._get_disk_free_gb()
        }
        
        return env_info
    
    @classmethod
    def _is_kali(cls) -> bool:
        """Vérifie si le système est Kali Linux"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                return 'kali' in content
        except:
            return False
    
    @classmethod
    def _is_parrot(cls) -> bool:
        """Vérifie si le système est Parrot OS"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                return 'parrot' in content
        except:
            return False
    
    @classmethod
    def _is_debian(cls) -> bool:
        """Vérifie si le système est Debian"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                return 'debian' in content
        except:
            return False
    
    @classmethod
    def _is_ubuntu(cls) -> bool:
        """Vérifie si le système est Ubuntu"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                return 'ubuntu' in content
        except:
            return False
    
    @classmethod
    def _is_root(cls) -> bool:
        """Vérifie si l'utilisateur est root"""
        try:
            return os.geteuid() == 0
        except:
            return False
    
    @classmethod
    def _get_disk_free_gb(cls) -> float:
        """Retourne l'espace disque libre en GB"""
        try:
            import shutil
            free_bytes = shutil.diskusage(Path.home()).free
            return round(free_bytes / (1024 ** 3), 2)
        except:
            return 0.0
    
    @classmethod
    def check_network(cls) -> Dict[str, Any]:
        """
        Vérifie la connectivité réseau
        
        Returns:
            Dictionnaire avec les informations réseau
        """
        import socket
        
        result = {
            'internet': False,
            'dns': False,
            'local_ip': None,
            'gateway': None
        }
        
        # Vérifier la connexion Internet
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            result['internet'] = True
        except:
            pass
        
        # Vérifier DNS
        try:
            socket.gethostbyname('google.com')
            result['dns'] = True
        except:
            pass
        
        # Récupérer l'IP locale
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            result['local_ip'] = s.getsockname()[0]
            s.close()
        except:
            pass
        
        return result
    
    @classmethod
    def generate_report(cls) -> str:
        """
        Génère un rapport complet des dépendances
        
        Returns:
            Rapport formaté
        """
        env = cls.check_environment()
        network = cls.check_network()
        deps = cls.check_all(verbose=False)
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║                 RAPPORT DES DÉPENDANCES REDFORGE                 ║
╚══════════════════════════════════════════════════════════════════╝

📊 ENVIRONNEMENT:
  OS: {env['os']} {env['os_release']}
  Version: {env['os_version'][:50]}
  Python: {env['python_version'].split()[0]}
  Kali: {'Oui' if env['is_kali'] else 'Non'}
  Parrot: {'Oui' if env['is_parrot'] else 'Non'}
  Root: {'Oui' if env['is_root'] else 'Non'}
  Espace disque: {env['disk_free_gb']} GB

🌐 RÉSEAU:
  Internet: {'✅' if network['internet'] else '❌'}
  DNS: {'✅' if network['dns'] else '❌'}
  IP locale: {network['local_ip'] or 'N/A'}

🔧 OUTILS SYSTÈME:
"""
        for tool_name, tool_result in deps['tools'].items():
            status = "✅" if tool_result['installed'] else "❌"
            version = f" v{tool_result['version']}" if tool_result['version'] else ""
            report += f"  {status} {tool_name}{version}\n"
        
        report += f"""
🐍 PACKAGES PYTHON:
"""
        for pkg_name, pkg_result in deps['python_packages'].items():
            status = "✅" if pkg_result['installed'] else "⚠️"
            version = f" v{pkg_result['version']}" if pkg_result['version'] else ""
            report += f"  {status} {pkg_name}{version}\n"
        
        report += f"""
📊 STATUT GLOBAL:
  Dépendances critiques: {'✅ OK' if not deps['critical_missing'] else '❌ MANQUANTES'}
  Dépendances optionnelles: {len([m for m in deps['missing'] if not m.get('critical', False)])} manquante(s)

📅 Généré le: {deps['timestamp']}
"""
        return report


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test du vérificateur de dépendances")
    print("=" * 60)
    
    # Vérifier l'environnement
    env = DependencyChecker.check_environment()
    print(f"\n🌍 Environnement: {env['os']} {env['os_release']}")
    print(f"🐍 Python: {env['python_version'].split()[0]}")
    print(f"👤 Root: {'Oui' if env['is_root'] else 'Non'}")
    
    # Vérifier les dépendances
    results = DependencyChecker.check_all(verbose=True)
    
    # Générer un rapport
    report = DependencyChecker.generate_report()
    print(report)
    
    if results['all_ok']:
        print("\n✅ Environnement prêt pour RedForge")
    else:
        print("\n⚠️ Certaines dépendances critiques sont manquantes")