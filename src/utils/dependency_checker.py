#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedForge v2.0 - Module de vérification des dépendances ultra robuste
Vérifie que tous les outils requis sont installés
Version avec support furtif, APT et vérification avancée
"""

import subprocess
import shutil
import sys
import os
import re
import platform
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
from functools import wraps


# ============================================
# UTILITAIRES ROBUSTES
# ============================================

def safe_method(default_return=None):
    """Décorateur pour méthodes sécurisées (ne plantent jamais)"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                try:
                    print(f"[!] Erreur dans {func.__name__}: {e}", file=sys.stderr)
                except Exception:
                    pass
                return default_return
        return wrapper
    return decorator


class SafeConsole:
    """Console sécurisée qui ne plante jamais"""
    
    @staticmethod
    def _print_color(text: str, color: str = ""):
        try:
            if color and sys.platform != 'win32':
                print(f"{color}{text}")
            else:
                print(text)
        except Exception:
            pass
    
    @staticmethod
    def print_header(text: str):
        SafeConsole._print_color(f"\n{'=' * 60}\n{text}\n{'=' * 60}")
    
    @staticmethod
    def print_info(text: str):
        SafeConsole._print_color(text)
    
    @staticmethod
    def print_warning(text: str):
        SafeConsole._print_color(f"⚠️ {text}")
    
    @staticmethod
    def print_error(text: str):
        SafeConsole._print_color(f"❌ {text}")
    
    @staticmethod
    def print_success(text: str):
        SafeConsole._print_color(f"✅ {text}")


# Tentative d'import du vrai module color_output
try:
    from src.utils.color_output import console as _console
    console = _console
except (ImportError, AttributeError):
    console = SafeConsole()


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
        'tor': {
            'cmd': 'tor',
            'description': 'Anonymisation (mode furtif)',
            'min_version': '0.4',
            'install_cmd': 'sudo apt install tor -y',
            'critical': False
        },
        'proxychains': {
            'cmd': 'proxychains',
            'description': 'Proxy chains (mode furtif)',
            'min_version': '4.0',
            'install_cmd': 'sudo apt install proxychains -y',
            'critical': False
        }
    }
    
    # Outils optionnels
    OPTIONAL_TOOLS = {
        'gobuster': {
            'cmd': 'gobuster',
            'description': 'Force brute de répertoires',
            'install_cmd': 'sudo apt install gobuster -y'
        },
        'ffuf': {
            'cmd': 'ffuf',
            'description': 'Fuzzing web',
            'install_cmd': 'sudo apt install ffuf -y'
        },
        'xsstrike': {
            'cmd': 'xsstrike',
            'description': 'Détection XSS',
            'install_cmd': 'sudo apt install xsstrike -y'
        },
        'wafw00f': {
            'cmd': 'wafw00f',
            'description': 'Détection WAF',
            'install_cmd': 'pip3 install wafw00f'
        },
        'dnsrecon': {
            'cmd': 'dnsrecon',
            'description': 'Énumération DNS',
            'install_cmd': 'sudo apt install dnsrecon -y'
        },
        'theharvester': {
            'cmd': 'theharvester',
            'description': 'OSINT',
            'install_cmd': 'sudo apt install theharvester -y'
        }
    }
    
    # Dépendances Python
    PYTHON_PACKAGES = {
        'flask': {
            'import_name': 'flask',
            'description': 'Framework web',
            'install_cmd': 'pip install flask',
            'critical': True
        },
        'flask_socketio': {
            'import_name': 'flask_socketio',
            'description': 'WebSocket',
            'install_cmd': 'pip install flask-socketio',
            'critical': True
        },
        'requests': {
            'import_name': 'requests',
            'description': 'Requêtes HTTP',
            'install_cmd': 'pip install requests',
            'critical': True
        },
        'beautifulsoup4': {
            'import_name': 'bs4',
            'description': 'Parsing HTML',
            'install_cmd': 'pip install beautifulsoup4',
            'critical': True
        },
        'lxml': {
            'import_name': 'lxml',
            'description': 'Parsing XML/HTML',
            'install_cmd': 'pip install lxml',
            'critical': True
        },
        'cryptography': {
            'import_name': 'cryptography',
            'description': 'Cryptographie',
            'install_cmd': 'pip install cryptography',
            'critical': True
        },
        'paramiko': {
            'import_name': 'paramiko',
            'description': 'Client SSH',
            'install_cmd': 'pip install paramiko',
            'critical': False
        },
        'dnspython': {
            'import_name': 'dns',
            'description': 'DNS Python',
            'install_cmd': 'pip install dnspython',
            'critical': False
        },
        'rich': {
            'import_name': 'rich',
            'description': 'Interface CLI enrichie',
            'install_cmd': 'pip install rich',
            'critical': False
        },
        'click': {
            'import_name': 'click',
            'description': 'Parseur CLI',
            'install_cmd': 'pip install click',
            'critical': False
        },
        'tqdm': {
            'import_name': 'tqdm',
            'description': 'Barres de progression',
            'install_cmd': 'pip install tqdm',
            'critical': False
        },
        'pyyaml': {
            'import_name': 'yaml',
            'description': 'Parsing YAML',
            'install_cmd': 'pip install pyyaml',
            'critical': False
        }
    }
    
    @classmethod
    @safe_method(default_return={})
    def check_dependencies(cls, verbose: bool = True, quick: bool = False) -> Dict[str, Any]:
        """
        Vérifie toutes les dépendances (fonction principale).
        
        Args:
            verbose: Afficher les résultats détaillés
            quick: Mode rapide (ignore les versions)
        
        Returns:
            Dictionnaire avec les résultats
        """
        results = {
            'system_tools': {},
            'optional_tools': {},
            'python_packages': {},
            'status': 'ok',
            'missing': [],
            'critical_missing': [],
            'warnings': [],
            'all_ok': True,
            'timestamp': datetime.now().isoformat()
        }
        
        if verbose:
            console.print_header("🔍 Vérification des dépendances RedForge")
        
        # Vérifier les outils requis
        for tool_name, tool_info in cls.REQUIRED_TOOLS.items():
            result = cls._check_system_tool(tool_name, tool_info, quick)
            results['system_tools'][tool_name] = result
            
            if not result.get('installed', False):
                missing_entry = {
                    'type': 'tool',
                    'name': tool_name,
                    'description': tool_info['description'],
                    'install_cmd': tool_info['install_cmd'],
                    'critical': tool_info.get('critical', False)
                }
                results['missing'].append(missing_entry)
                
                if tool_info.get('critical', False):
                    results['critical_missing'].append(missing_entry)
                    results['all_ok'] = False
                    results['status'] = 'error'
            
            if verbose:
                cls._print_tool_status(tool_name, result, tool_info)
        
        # Vérifier les outils optionnels
        for tool_name, tool_info in cls.OPTIONAL_TOOLS.items():
            result = cls._check_system_tool(tool_name, tool_info, quick)
            results['optional_tools'][tool_name] = result
            
            if not result.get('installed', False) and verbose:
                console.print_info(f"  ⚠️ {tool_name}: optionnel - {tool_info['description']}")
        
        # Vérifier les packages Python
        for pkg_name, pkg_info in cls.PYTHON_PACKAGES.items():
            result = cls._check_python_package(pkg_name, pkg_info)
            results['python_packages'][pkg_name] = result
            
            if not result.get('installed', False):
                missing_entry = {
                    'type': 'python',
                    'name': pkg_name,
                    'description': pkg_info['description'],
                    'install_cmd': pkg_info['install_cmd'],
                    'critical': pkg_info.get('critical', False)
                }
                results['missing'].append(missing_entry)
                
                if pkg_info.get('critical', False):
                    results['critical_missing'].append(missing_entry)
                    results['all_ok'] = False
                    results['status'] = 'error'
            
            if verbose:
                cls._print_package_status(pkg_name, result, pkg_info)
        
        # Vérification de l'environnement
        env_check = cls._check_environment()
        results['environment'] = env_check
        
        if not env_check.get('is_kali', False) and not env_check.get('is_parrot', False):
            results['warnings'].append("Système non officiellement supporté (Kali/Parrot recommandé)")
        
        if verbose:
            cls._print_summary(results)
        
        return results
    
    @classmethod
    @safe_method(default_return={})
    def _check_system_tool(cls, tool_name: str, tool_info: Dict, quick: bool = False) -> Dict[str, Any]:
        """Vérifie un outil système"""
        result = {
            'installed': False,
            'version': None,
            'path': None,
            'min_version_ok': True,
            'error': None
        }
        
        cmd = tool_info.get('cmd', tool_name)
        path = shutil.which(cmd)
        
        if path:
            result['installed'] = True
            result['path'] = path
            
            if not quick:
                try:
                    proc = subprocess.run(
                        [cmd, '--version'], 
                        capture_output=True, 
                        text=True, 
                        timeout=5
                    )
                    output = proc.stdout + proc.stderr
                    
                    version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', output)
                    if version_match:
                        result['version'] = version_match.group(1)
                        
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
    @safe_method(default_return={})
    def _check_python_package(cls, package_name: str, package_info: Dict) -> Dict[str, Any]:
        """Vérifie un package Python"""
        result = {
            'installed': False,
            'version': None
        }
        
        import_name = package_info.get('import_name', package_name)
        
        try:
            module = __import__(import_name)
            result['installed'] = True
            
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
        """Compare deux versions"""
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
    def _print_tool_status(cls, tool_name: str, result: Dict, tool_info: Dict):
        """Affiche le statut d'un outil"""
        if result.get('installed', False):
            version_str = f" v{result['version']}" if result['version'] else ""
            console.print_success(f"  ✅ {tool_name}{version_str}: {tool_info['description']}")
        else:
            critical = tool_info.get('critical', False)
            icon = "❌" if critical else "⚠️"
            console.print_info(f"  {icon} {tool_name}: {tool_info['description']} - {tool_info['install_cmd']}")
    
    @classmethod
    def _print_package_status(cls, pkg_name: str, result: Dict, pkg_info: Dict):
        """Affiche le statut d'un package"""
        if result.get('installed', False):
            version_str = f" v{result['version']}" if result['version'] else ""
            console.print_success(f"  ✅ {pkg_name}{version_str}: {pkg_info['description']}")
        else:
            critical = pkg_info.get('critical', False)
            icon = "❌" if critical else "⚠️"
            console.print_info(f"  {icon} {pkg_name}: {pkg_info['description']} - {pkg_info['install_cmd']}")
    
    @classmethod
    def _print_summary(cls, results: Dict):
        """Affiche le résumé"""
        print()
        console.print_header("📊 RÉSUMÉ")
        
        if results['all_ok']:
            console.print_success("✅ Toutes les dépendances critiques sont installées")
        else:
            console.print_error(f"❌ {len(results['critical_missing'])} dépendance(s) critique(s) manquante(s)")
        
        if results['missing']:
            console.print_warning(f"⚠️ {len(results['missing'])} dépendance(s) manquante(s) au total")
        
        # Instructions d'installation
        if results['critical_missing']:
            console.print_warning("\n📦 Pour installer les dépendances manquantes:")
            console.print_info("  sudo apt update")
            
            tools = [m for m in results['critical_missing'] if m['type'] == 'tool']
            for tool in tools:
                console.print_info(f"  {tool['install_cmd']}")
            
            packages = [m for m in results['critical_missing'] if m['type'] == 'python']
            if packages:
                console.print_info("  pip install -r requirements.txt")
    
    @classmethod
    @safe_method(default_return={})
    def _check_environment(cls) -> Dict[str, Any]:
        """Vérifie l'environnement"""
        env_info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'python_version': sys.version.split()[0],
            'python_executable': sys.executable,
            'is_kali': cls._is_kali(),
            'is_parrot': cls._is_parrot(),
            'is_debian': cls._is_debian(),
            'is_ubuntu': cls._is_ubuntu(),
            'is_root': cls._is_root(),
            'home_dir': str(Path.home()),
            'redforge_dir': str(Path.home() / '.RedForge'),
            'disk_free_gb': cls._get_disk_free_gb(),
            'in_venv': hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        }
        
        return env_info
    
    @classmethod
    def _is_kali(cls) -> bool:
        try:
            with open('/etc/os-release', 'r') as f:
                return 'kali' in f.read().lower()
        except:
            return False
    
    @classmethod
    def _is_parrot(cls) -> bool:
        try:
            with open('/etc/os-release', 'r') as f:
                return 'parrot' in f.read().lower()
        except:
            return False
    
    @classmethod
    def _is_debian(cls) -> bool:
        try:
            with open('/etc/os-release', 'r') as f:
                return 'debian' in f.read().lower()
        except:
            return False
    
    @classmethod
    def _is_ubuntu(cls) -> bool:
        try:
            with open('/etc/os-release', 'r') as f:
                return 'ubuntu' in f.read().lower()
        except:
            return False
    
    @classmethod
    def _is_root(cls) -> bool:
        try:
            return os.geteuid() == 0
        except:
            return False
    
    @classmethod
    def _get_disk_free_gb(cls) -> float:
        try:
            import shutil
            free_bytes = shutil.diskusage(Path.home()).free
            return round(free_bytes / (1024 ** 3), 2)
        except:
            return 0.0
    
    @classmethod
    @safe_method(default_return={})
    def check_network(cls) -> Dict[str, Any]:
        """Vérifie la connectivité réseau"""
        import socket
        
        result = {
            'internet': False,
            'dns': False,
            'local_ip': None,
            'gateway': None
        }
        
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            result['internet'] = True
        except:
            pass
        
        try:
            socket.gethostbyname('google.com')
            result['dns'] = True
        except:
            pass
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            result['local_ip'] = s.getsockname()[0]
            s.close()
        except:
            pass
        
        return result
    
    @classmethod
    @safe_method(default_return=False)
    def is_metasploit_running(cls) -> bool:
        """Vérifie si Metasploit RPC tourne"""
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
    @safe_method(default_return={})
    def generate_report(cls) -> str:
        """Génère un rapport complet"""
        deps = cls.check_dependencies(verbose=False)
        env = deps.get('environment', {})
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║                 RAPPORT DES DÉPENDANCES REDFORGE                 ║
╚══════════════════════════════════════════════════════════════════╝

📊 ENVIRONNEMENT:
  OS: {env.get('os', 'Inconnu')} {env.get('os_release', '')}
  Python: {env.get('python_version', 'Inconnu')}
  Environnement virtuel: {'✅ Actif' if env.get('in_venv') else '❌ Inactif'}
  Root: {'✅ Oui' if env.get('is_root') else '❌ Non'}
  Kali/Parrot: {'✅ Oui' if env.get('is_kali') or env.get('is_parrot') else '⚠️ Non recommandé'}
  Espace disque: {env.get('disk_free_gb', 0)} GB libre

🔧 OUTILS SYSTÈME:
"""
        for tool_name, tool_result in deps.get('system_tools', {}).items():
            status = "✅" if tool_result.get('installed') else "❌"
            version = f" v{tool_result.get('version', '')}" if tool_result.get('version') else ""
            report += f"  {status} {tool_name}{version}\n"
        
        report += f"""
🐍 PACKAGES PYTHON:
"""
        for pkg_name, pkg_result in deps.get('python_packages', {}).items():
            status = "✅" if pkg_result.get('installed') else "❌"
            version = f" v{pkg_result.get('version', '')}" if pkg_result.get('version') else ""
            report += f"  {status} {pkg_name}{version}\n"
        
        report += f"""
📊 STATUT GLOBAL:
  Statut: {deps.get('status', 'inconnu')}
  Dépendances critiques manquantes: {len(deps.get('critical_missing', []))}
  Dépendances totales manquantes: {len(deps.get('missing', []))}

📅 Généré le: {deps.get('timestamp', datetime.now().isoformat())}
"""
        return report


# ============================================
# FONCTIONS DE COMPATIBILITÉ (CRITIQUES)
# ============================================

def check_dependencies(verbose: bool = True, quick: bool = False) -> Dict[str, Any]:
    """
    Fonction principale de vérification des dépendances.
    Utilisée par de nombreux modules de RedForge.
    
    Args:
        verbose: Afficher les détails
        quick: Mode rapide
    
    Returns:
        Dictionnaire des résultats
    """
    return DependencyChecker.check_dependencies(verbose=verbose, quick=quick)


def check_all_dependencies() -> Dict[str, Any]:
    """Alias pour check_dependencies"""
    return check_dependencies(verbose=True)


def get_missing_dependencies() -> List[str]:
    """Retourne la liste des dépendances manquantes"""
    result = check_dependencies(verbose=False)
    return [m.get('name', '') for m in result.get('missing', [])]


def is_dependency_installed(name: str) -> bool:
    """Vérifie si une dépendance spécifique est installée"""
    result = check_dependencies(verbose=False)
    
    # Vérifier dans les outils système
    for tool_name, tool_result in result.get('system_tools', {}).items():
        if tool_name == name and tool_result.get('installed'):
            return True
    
    # Vérifier dans les packages Python
    for pkg_name, pkg_result in result.get('python_packages', {}).items():
        if pkg_name == name and pkg_result.get('installed'):
            return True
    
    return False


def print_dependency_report() -> None:
    """Affiche le rapport des dépendances"""
    report = DependencyChecker.generate_report()
    print(report)


# Instance globale pour compatibilité
dependency_checker = DependencyChecker()


# ============================================
# TESTS
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Test du vérificateur de dépendances v2.0")
    print("=" * 60)
    
    # Test de la fonction principale
    results = check_dependencies(verbose=True)
    
    # Test des fonctions de compatibilité
    print("\n" + "=" * 60)
    print("Test des fonctions de compatibilité")
    print("=" * 60)
    
    missing = get_missing_dependencies()
    print(f"Dépendances manquantes: {missing}")
    
    # Génération du rapport
    print("\n" + DependencyChecker.generate_report())
    
    # Test de la fonction is_dependency_installed
    print("\nTest is_dependency_installed():")
    test_tools = ["nmap", "sqlmap", "tool_inexistant"]
    for tool in test_tools:
        installed = is_dependency_installed(tool)
        print(f"  {tool}: {'✅' if installed else '❌'}")
    
    print("\n✅ Vérificateur de dépendances fonctionnel")