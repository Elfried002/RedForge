#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'installation d'outils pour RedForge
Installe automatiquement les outils manquants avec support furtif
Version avec installation en arrière-plan, vérification d'intégrité et mises à jour
"""

import subprocess
import sys
import os
import hashlib
import tempfile
import shutil
import platform
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.utils.color_output import console
from src.utils.dependency_checker import DependencyChecker


class ToolInstaller:
    """Installateur d'outils avancé pour RedForge"""
    
    # Commandes d'installation par outil
    INSTALL_COMMANDS = {
        'nmap': {
            'cmd': 'sudo apt update && sudo apt install nmap -y',
            'verify': 'nmap --version',
            'size_mb': 15,
            'priority': 1
        },
        'sqlmap': {
            'cmd': 'sudo apt update && sudo apt install sqlmap -y',
            'verify': 'sqlmap --version',
            'size_mb': 20,
            'priority': 1
        },
        'whatweb': {
            'cmd': 'sudo apt update && sudo apt install whatweb -y',
            'verify': 'whatweb --version',
            'size_mb': 5,
            'priority': 1
        },
        'metasploit-framework': {
            'cmd': 'sudo apt update && sudo apt install metasploit-framework -y',
            'verify': 'msfconsole --version',
            'size_mb': 500,
            'priority': 2
        },
        'hydra': {
            'cmd': 'sudo apt update && sudo apt install hydra -y',
            'verify': 'hydra -h',
            'size_mb': 10,
            'priority': 2
        },
        'dirb': {
            'cmd': 'sudo apt update && sudo apt install dirb -y',
            'verify': 'dirb -h',
            'size_mb': 1,
            'priority': 2
        },
        'gobuster': {
            'cmd': 'sudo apt update && sudo apt install gobuster -y',
            'verify': 'gobuster --version',
            'size_mb': 10,
            'priority': 2
        },
        'ffuf': {
            'cmd': 'go install github.com/ffuf/ffuf@latest',
            'verify': 'ffuf -V',
            'size_mb': 5,
            'priority': 2
        },
        'nikto': {
            'cmd': 'sudo apt update && sudo apt install nikto -y',
            'verify': 'nikto -Version',
            'size_mb': 20,
            'priority': 3
        },
        'wafw00f': {
            'cmd': 'pip3 install wafw00f',
            'verify': 'wafw00f --version',
            'size_mb': 1,
            'priority': 3
        },
        'xsstrike': {
            'cmd': 'pip3 install xsstrike',
            'verify': 'xsstrike --version',
            'size_mb': 1,
            'priority': 3
        },
        'dalfox': {
            'cmd': 'go install github.com/hahwul/dalfox/v2@latest',
            'verify': 'dalfox --version',
            'size_mb': 10,
            'priority': 3
        },
        'jwt_tool': {
            'cmd': 'pip3 install jwt_tool',
            'verify': 'jwt_tool --version',
            'size_mb': 1,
            'priority': 3
        }
    }
    
    # Packages Python requis
    PYTHON_PACKAGES = {
        'pymetasploit3': {
            'cmd': 'pip3 install pymetasploit3',
            'import_name': 'pymetasploit3',
            'priority': 1
        },
        'python-nmap': {
            'cmd': 'pip3 install python-nmap',
            'import_name': 'nmap',
            'priority': 1
        },
        'requests': {
            'cmd': 'pip3 install requests',
            'import_name': 'requests',
            'priority': 1
        },
        'beautifulsoup4': {
            'cmd': 'pip3 install beautifulsoup4',
            'import_name': 'bs4',
            'priority': 1
        },
        'cryptography': {
            'cmd': 'pip3 install cryptography',
            'import_name': 'cryptography',
            'priority': 1
        },
        'paramiko': {
            'cmd': 'pip3 install paramiko',
            'import_name': 'paramiko',
            'priority': 2
        },
        'dnspython': {
            'cmd': 'pip3 install dnspython',
            'import_name': 'dns',
            'priority': 2
        },
        'flask': {
            'cmd': 'pip3 install flask flask-socketio flask-cors',
            'import_name': 'flask',
            'priority': 2
        },
        'reportlab': {
            'cmd': 'pip3 install reportlab',
            'import_name': 'reportlab',
            'priority': 2
        },
        'openpyxl': {
            'cmd': 'pip3 install openpyxl',
            'import_name': 'openpyxl',
            'priority': 2
        },
        'rich': {
            'cmd': 'pip3 install rich',
            'import_name': 'rich',
            'priority': 2
        }
    }
    
    # URLs des wordlists
    WORDLISTS = {
        'french_passwords.txt': {
            'url': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common-french.txt',
            'size_mb': 0.5,
            'hash': None
        },
        'french_users.txt': {
            'url': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/top-usernames-shortlist.txt',
            'size_mb': 0.1,
            'hash': None
        },
        'common_directories.txt': {
            'url': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt',
            'size_mb': 2,
            'hash': None
        },
        'subdomains.txt': {
            'url': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt',
            'size_mb': 0.5,
            'hash': None
        },
        'parameters.txt': {
            'url': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt',
            'size_mb': 0.3,
            'hash': None
        }
    }
    
    def __init__(self):
        self.stealth_mode = False
        self.apt_mode = False
        self.install_log = []
        self.wordlist_dir = Path.home() / ".RedForge" / "wordlists"
        self.tools_dir = Path.home() / ".RedForge" / "tools"
    
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif"""
        self.stealth_mode = enabled
    
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT"""
        self.apt_mode = enabled
    
    def _log(self, message: str, level: str = "info"):
        """Enregistre un message dans le log d'installation"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.install_log.append(entry)
        
        if not self.stealth_mode:
            if level == "success":
                console.print_success(message)
            elif level == "error":
                console.print_error(message)
            elif level == "warning":
                console.print_warning(message)
            else:
                console.print_info(message)
    
    def install_all(self, interactive: bool = True, parallel: bool = False) -> Dict[str, Any]:
        """
        Installe tous les outils manquants
        
        Args:
            interactive: Mode interactif (demander confirmation)
            parallel: Installation parallèle
        """
        results = {
            'installed': [],
            'failed': [],
            'skipped': [],
            'duration': 0
        }
        
        start_time = datetime.now()
        
        # Vérifier les outils manquants
        missing = DependencyChecker.get_missing_tools()
        
        if not missing:
            self._log("Tous les outils sont déjà installés", "success")
            return results
        
        self._log(f"Outils manquants: {', '.join(missing)}", "warning")
        
        if interactive:
            response = input("\nVoulez-vous installer les outils manquants ? (O/n): ")
            if response.lower() not in ['o', 'oui', 'y', 'yes', '']:
                self._log("Installation annulée", "info")
                return results
        
        # Trier par priorité
        missing.sort(key=lambda x: self.INSTALL_COMMANDS.get(x, {}).get('priority', 99))
        
        if parallel and len(missing) > 1:
            # Installation parallèle
            with ThreadPoolExecutor(max_workers=min(len(missing), 3)) as executor:
                futures = {executor.submit(self.install_tool, tool): tool for tool in missing}
                for future in as_completed(futures):
                    tool = futures[future]
                    try:
                        success = future.result()
                        if success:
                            results['installed'].append(tool)
                            self._log(f"✅ {tool} installé avec succès", "success")
                        else:
                            results['failed'].append(tool)
                            self._log(f"❌ Échec de l'installation de {tool}", "error")
                    except Exception as e:
                        results['failed'].append(tool)
                        self._log(f"❌ Erreur installation {tool}: {e}", "error")
        else:
            # Installation séquentielle
            for tool in missing:
                self._log(f"📦 Installation de {tool}...", "info")
                success = self.install_tool(tool)
                
                if success:
                    results['installed'].append(tool)
                    self._log(f"✅ {tool} installé avec succès", "success")
                else:
                    results['failed'].append(tool)
                    self._log(f"❌ Échec de l'installation de {tool}", "error")
        
        results['duration'] = (datetime.now() - start_time).total_seconds()
        return results
    
    def install_tool(self, tool_name: str) -> bool:
        """
        Installe un outil spécifique
        
        Args:
            tool_name: Nom de l'outil
        """
        if tool_name not in self.INSTALL_COMMANDS:
            self._log(f"Aucune commande d'installation pour {tool_name}", "warning")
            return False
        
        tool_info = self.INSTALL_COMMANDS[tool_name]
        cmd = tool_info['cmd']
        
        # Vérifier l'espace disque
        if not self._check_disk_space(tool_info.get('size_mb', 10)):
            self._log(f"Espace disque insuffisant pour installer {tool_name}", "error")
            return False
        
        try:
            # Exécuter la commande d'installation
            process = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if process.returncode == 0:
                # Vérifier l'installation
                verify_cmd = tool_info.get('verify')
                if verify_cmd:
                    verify_process = subprocess.run(
                        verify_cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if verify_process.returncode != 0:
                        self._log(f"Vérification échouée pour {tool_name}", "warning")
                        return False
                return True
            else:
                self._log(f"Erreur: {process.stderr[:200]}", "error")
                return False
                
        except subprocess.TimeoutExpired:
            self._log("Timeout pendant l'installation", "error")
            return False
        except Exception as e:
            self._log(f"Erreur: {e}", "error")
            return False
    
    def _check_disk_space(self, required_mb: int) -> bool:
        """Vérifie l'espace disque disponible"""
        try:
            import shutil
            free_bytes = shutil.diskusage('/').free
            free_mb = free_bytes / (1024 * 1024)
            return free_mb > required_mb * 2  # 2x l'espace requis
        except:
            return True
    
    def install_python_package(self, package_name: str) -> bool:
        """
        Installe un package Python
        
        Args:
            package_name: Nom du package
        """
        if package_name not in self.PYTHON_PACKAGES:
            self._log(f"Aucune commande pour {package_name}", "warning")
            return False
        
        pkg_info = self.PYTHON_PACKAGES[package_name]
        cmd = pkg_info['cmd']
        
        try:
            process = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if process.returncode == 0:
                # Vérifier l'import
                import_name = pkg_info.get('import_name', package_name)
                try:
                    __import__(import_name)
                    return True
                except ImportError:
                    self._log(f"Package {package_name} installé mais non importable", "warning")
                    return True
            return False
            
        except Exception as e:
            self._log(f"Erreur installation {package_name}: {e}", "error")
            return False
    
    def install_all_python_packages(self, parallel: bool = False) -> Dict[str, bool]:
        """
        Installe tous les packages Python requis
        
        Args:
            parallel: Installation parallèle
            
        Returns:
            Dictionnaire des résultats par package
        """
        results = {}
        start_time = datetime.now()
        
        packages = list(self.PYTHON_PACKAGES.keys())
        
        if parallel and len(packages) > 1:
            with ThreadPoolExecutor(max_workers=min(len(packages), 3)) as executor:
                futures = {executor.submit(self.install_python_package, pkg): pkg for pkg in packages}
                for future in as_completed(futures):
                    pkg = futures[future]
                    try:
                        success = future.result()
                        results[pkg] = success
                        if success:
                            self._log(f"✅ {pkg} installé", "success")
                        else:
                            self._log(f"❌ Échec installation {pkg}", "error")
                    except Exception as e:
                        results[pkg] = False
                        self._log(f"❌ Erreur {pkg}: {e}", "error")
        else:
            for pkg in packages:
                self._log(f"Installation de {pkg}...", "info")
                success = self.install_python_package(pkg)
                results[pkg] = success
                if success:
                    self._log(f"✅ {pkg} installé", "success")
                else:
                    self._log(f"❌ Échec installation {pkg}", "error")
        
        self._log(f"Installation Python terminée en {(datetime.now() - start_time).total_seconds():.1f}s", "info")
        return results
    
    def install_wordlists(self, force: bool = False) -> bool:
        """
        Installe les wordlists françaises
        
        Args:
            force: Forcer le téléchargement même si existe
        """
        import requests
        
        self._log("Installation des wordlists...", "info")
        
        self.wordlist_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        total_count = len(self.WORDLISTS)
        
        for filename, info in self.WORDLISTS.items():
            filepath = self.wordlist_dir / filename
            
            if filepath.exists() and not force:
                self._log(f"  {filename} existe déjà", "info")
                success_count += 1
                continue
            
            url = info['url']
            self._log(f"  Téléchargement de {filename}...", "info")
            
            try:
                response = requests.get(url, timeout=60, stream=True)
                if response.status_code == 200:
                    # Vérifier la taille
                    content_length = int(response.headers.get('content-length', 0))
                    if content_length > 0:
                        size_mb = content_length / (1024 * 1024)
                        if size_mb > 50:  # Plus de 50 MB
                            self._log(f"    Fichier trop volumineux ({size_mb:.1f} MB)", "warning")
                            continue
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Vérifier l'intégrité
                    if info.get('hash'):
                        file_hash = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
                        if file_hash != info['hash']:
                            self._log(f"    Hash incorrect pour {filename}", "warning")
                            filepath.unlink()
                            continue
                    
                    self._log(f"  ✅ {filename} téléchargé", "success")
                    success_count += 1
                else:
                    self._log(f"  ❌ {filename} échec téléchargement (HTTP {response.status_code})", "error")
            except Exception as e:
                self._log(f"  ❌ {filename}: {e}", "error")
        
        self._log(f"Wordlists installées: {success_count}/{total_count}", "success" if success_count == total_count else "warning")
        return success_count == total_count
    
    def setup_metasploit_rpc(self) -> bool:
        """
        Configure le service RPC de Metasploit
        """
        self._log("Configuration de Metasploit RPC...", "info")
        
        # Vérifier si Metasploit est installé
        if not shutil.which('msfrpcd'):
            self._log("Metasploit non installé", "error")
            return False
        
        # Démarrer le service RPC
        cmd = 'msfrpcd -P RedForge2024 -S -p 55553'
        
        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self._log("Service RPC Metasploit démarré", "success")
            return True
        except Exception as e:
            self._log(f"Erreur démarrage RPC: {e}", "error")
            return False
    
    def setup_go_env(self) -> bool:
        """
        Configure l'environnement Go pour les outils Go
        """
        self._log("Configuration de l'environnement Go...", "info")
        
        # Vérifier si Go est installé
        if not shutil.which('go'):
            self._log("Go non installé. Installation...", "info")
            try:
                subprocess.run('sudo apt install golang-go -y', shell=True, timeout=120)
            except:
                self._log("Erreur installation Go", "error")
                return False
        
        # Configurer GOPATH
        go_path = Path.home() / "go"
        go_path.mkdir(exist_ok=True)
        
        # Ajouter au PATH
        bin_path = go_path / "bin"
        if str(bin_path) not in os.environ.get('PATH', ''):
            os.environ['PATH'] = f"{bin_path}:{os.environ.get('PATH', '')}"
        
        self._log("Environnement Go configuré", "success")
        return True
    
    def full_setup(self, parallel: bool = False, skip_python: bool = False) -> bool:
        """
        Installation complète de l'environnement RedForge
        
        Args:
            parallel: Installation parallèle
            skip_python: Ignorer l'installation des packages Python
        """
        start_time = datetime.now()
        
        self._log("=" * 60, "info")
        self._log("Installation complète de RedForge", "info")
        self._log("=" * 60, "info")
        
        # 1. Mise à jour du système
        self._log("\n📦 Mise à jour du système...", "info")
        try:
            subprocess.run('sudo apt update && sudo apt upgrade -y', shell=True, timeout=300)
            self._log("Système mis à jour", "success")
        except:
            self._log("Erreur mise à jour système", "warning")
        
        # 2. Configuration Go
        self.setup_go_env()
        
        # 3. Installation des outils
        self._log("\n📦 Installation des outils système...", "info")
        tool_results = self.install_all(interactive=False, parallel=parallel)
        
        # 4. Installation des packages Python
        if not skip_python:
            self._log("\n📦 Installation des packages Python...", "info")
            self.install_all_python_packages(parallel=parallel)
        
        # 5. Installation des wordlists
        self._log("\n📦 Installation des wordlists...", "info")
        self.install_wordlists()
        
        # 6. Configuration Metasploit
        self._log("\n📦 Configuration de Metasploit...", "info")
        self.setup_metasploit_rpc()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        self._log("\n" + "=" * 60, "info")
        self._log(f"✅ Installation complète terminée en {duration:.1f}s!", "success")
        self._log(f"   Outils installés: {len(tool_results.get('installed', []))}")
        self._log(f"   Outils échoués: {len(tool_results.get('failed', []))}")
        self._log("=" * 60, "info")
        
        self._log("RedForge est prêt à être utilisé.", "success")
        
        return len(tool_results.get('failed', [])) == 0
    
    def get_install_log(self) -> List[Dict]:
        """Retourne le log d'installation"""
        return self.install_log
    
    def save_install_log(self, output_file: str) -> bool:
        """
        Sauvegarde le log d'installation
        
        Args:
            output_file: Fichier de sortie
        """
        import json
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'logs': self.install_log
                }, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    def get_installation_status(self) -> Dict[str, Any]:
        """
        Retourne le statut de l'installation
        
        Returns:
            Dictionnaire des statuts
        """
        status = {
            'tools': {},
            'python_packages': {},
            'wordlists': {},
            'redforge_dir': str(Path.home() / ".RedForge"),
            'disk_free_gb': 0
        }
        
        # Espace disque
        try:
            import shutil
            free_bytes = shutil.diskusage('/').free
            status['disk_free_gb'] = round(free_bytes / (1024 ** 3), 2)
        except:
            pass
        
        # Outils
        for tool in self.INSTALL_COMMANDS:
            status['tools'][tool] = shutil.which(tool) is not None
        
        # Wordlists
        for filename in self.WORDLISTS:
            filepath = self.wordlist_dir / filename
            status['wordlists'][filename] = filepath.exists()
        
        return status


# Instance globale
installer = ToolInstaller()


if __name__ == "__main__":
    # Test installation des wordlists
    installer.install_wordlists()
    
    # Afficher le statut
    status = installer.get_installation_status()
    print(f"\n📊 Statut d'installation:")
    print(f"   Espace disque libre: {status['disk_free_gb']} GB")
    print(f"   Répertoire RedForge: {status['redforge_dir']}")