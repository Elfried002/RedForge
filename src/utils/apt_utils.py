#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitaires APT pour RedForge
Fonctionnalités spécifiques pour les opérations de type Advanced Persistent Threat
Version avec support furtif, persistance et orchestration avancée
"""

import os
import sys
import time
import json
import random
import socket
import threading
import subprocess
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from collections import deque
import hashlib
import base64


class APTOperationPhase(Enum):
    """Phases d'une opération APT"""
    RECONNAISSANCE = "reconnaissance"
    INITIAL_ACCESS = "initial_access"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    LATERAL_MOVEMENT = "lateral_movement"
    DATA_EXFILTRATION = "data_exfiltration"
    COVER_TRACKS = "cover_tracks"


class APTOperationStatus(Enum):
    """Statuts d'une opération APT"""
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class APTOperation:
    """Définition d'une opération APT"""
    id: str
    name: str
    target: str
    phases: List[APTOperationPhase]
    status: APTOperationStatus = APTOperationStatus.PLANNED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_phase: int = 0
    results: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict] = field(default_factory=list)


@dataclass
class APTConfig:
    """Configuration pour les opérations APT"""
    # Délais
    phase_delay_min: int = 300      # 5 minutes
    phase_delay_max: int = 3600     # 1 heure
    action_delay_min: int = 30      # 30 secondes
    action_delay_max: int = 300     # 5 minutes
    
    # Jitter
    jitter: float = 0.3
    
    # Périodes d'inactivité (heures)
    inactivity_start: int = 0       # 0h
    inactivity_end: int = 6         # 6h
    
    # Périodes de travail (heures)
    work_start: int = 9             # 9h
    work_end: int = 17              # 17h
    
    # Rotation
    ip_rotation: bool = True
    proxy_list: List[str] = field(default_factory=list)
    user_agent_rotation: bool = True
    
    # Persistance
    persistence_methods: List[str] = field(default_factory=lambda: ["webshell", "cron_job", "scheduled_task"])
    
    # Exfiltration
    exfil_endpoint: Optional[str] = None
    exfil_interval: int = 3600      # 1 heure
    exfil_method: str = "https"     # https, dns, smtp, icmp
    
    # Logging
    verbose_logging: bool = False
    save_artifacts: bool = True
    stealth_logging: bool = True
    
    # Cleanup
    auto_cleanup: bool = True
    cleanup_delay: int = 3600       # 1 heure après la fin


class APTUtils:
    """
    Utilitaires pour les opérations APT
    Gère les délais, la persistance, l'exfiltration et les techniques furtives
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        self.config = APTConfig()
        self.operations: Dict[str, APTOperation] = {}
        self.active_operation: Optional[APTOperation] = None
        self.operation_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.is_running = False
        
        # File d'attente
        self.action_queue = deque()
        
        # Métriques
        self.metrics = {
            "operations_count": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "total_actions": 0,
            "total_delay_time": 0,
            "data_exfiltrated": 0
        }
    
    def set_config(self, config: Dict[str, Any]):
        """
        Met à jour la configuration APT
        
        Args:
            config: Configuration à appliquer
        """
        for key, value in config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def create_operation(self, name: str, target: str, 
                        phases: List[APTOperationPhase] = None,
                        config: Dict[str, Any] = None) -> str:
        """
        Crée une nouvelle opération APT
        
        Args:
            name: Nom de l'opération
            target: Cible
            phases: Phases à exécuter (None = toutes)
            config: Configuration personnalisée
            
        Returns:
            ID de l'opération
        """
        if phases is None:
            phases = list(APTOperationPhase)
        
        operation_id = hashlib.md5(
            f"{name}_{target}_{time.time()}".encode()
        ).hexdigest()[:16]
        
        operation = APTOperation(
            id=operation_id,
            name=name,
            target=target,
            phases=phases,
            config=config or {},
            status=APTOperationStatus.PLANNED
        )
        
        self.operations[operation_id] = operation
        self.metrics["operations_count"] += 1
        
        if not self.config.stealth_logging:
            print(f"✅ Opération APT créée: {name} (ID: {operation_id})")
        
        return operation_id
    
    def start_operation(self, operation_id: str) -> bool:
        """
        Démarre une opération APT
        
        Args:
            operation_id: ID de l'opération
            
        Returns:
            True si démarrée
        """
        if operation_id not in self.operations:
            return False
        
        if self.active_operation:
            if not self.config.stealth_logging:
                print("⚠️ Une opération est déjà active")
            return False
        
        operation = self.operations[operation_id]
        operation.status = APTOperationStatus.ACTIVE
        operation.start_time = datetime.now()
        self.active_operation = operation
        
        # Démarrer le thread d'exécution
        self.stop_event.clear()
        self.operation_thread = threading.Thread(
            target=self._run_operation,
            args=(operation_id,),
            daemon=True
        )
        self.operation_thread.start()
        
        if not self.config.stealth_logging:
            print(f"🚀 Opération APT démarrée: {operation.name}")
        
        return True
    
    def pause_operation(self) -> bool:
        """Met en pause l'opération active"""
        if not self.active_operation:
            return False
        
        self.active_operation.status = APTOperationStatus.PAUSED
        if not self.config.stealth_logging:
            print(f"⏸️ Opération APT mise en pause: {self.active_operation.name}")
        return True
    
    def resume_operation(self) -> bool:
        """Reprend l'opération active"""
        if not self.active_operation:
            return False
        
        self.active_operation.status = APTOperationStatus.ACTIVE
        if not self.config.stealth_logging:
            print(f"▶️ Opération APT reprise: {self.active_operation.name}")
        return True
    
    def stop_operation(self) -> bool:
        """Arrête l'opération active"""
        if not self.active_operation:
            return False
        
        self.stop_event.set()
        if self.operation_thread:
            self.operation_thread.join(timeout=30)
        
        self.active_operation.status = APTOperationStatus.COMPLETED
        self.active_operation.end_time = datetime.now()
        self.metrics["successful_operations"] += 1
        
        if not self.config.stealth_logging:
            print(f"✅ Opération APT terminée: {self.active_operation.name}")
        
        # Nettoyage automatique
        if self.config.auto_cleanup:
            self.cleanup_traces()
        
        self.active_operation = None
        
        return True
    
    def _run_operation(self, operation_id: str):
        """
        Exécute l'opération APT (thread principal)
        
        Args:
            operation_id: ID de l'opération
        """
        operation = self.operations[operation_id]
        self.is_running = True
        
        for idx, phase in enumerate(operation.phases):
            if self.stop_event.is_set():
                break
            
            if operation.status != APTOperationStatus.ACTIVE:
                while operation.status != APTOperationStatus.ACTIVE:
                    time.sleep(5)
                    if self.stop_event.is_set():
                        break
            
            operation.current_phase = idx
            
            # Vérifier la période d'inactivité
            if not self._is_work_hours():
                self._wait_for_work_hours()
            
            # Appliquer le délai entre phases
            if idx > 0:
                self._apply_phase_delay()
            
            # Exécuter la phase
            self._execute_phase(operation, phase)
            
            if self.stop_event.is_set():
                break
        
        self.is_running = False
    
    def _execute_phase(self, operation: APTOperation, phase: APTOperationPhase):
        """
        Exécute une phase spécifique de l'opération
        
        Args:
            operation: Opération en cours
            phase: Phase à exécuter
        """
        if not self.config.stealth_logging:
            print(f"📊 Début phase: {phase.value}")
        
        phase_start = time.time()
        
        # Dispatch vers la méthode appropriée
        phase_handlers = {
            APTOperationPhase.RECONNAISSANCE: self._phase_reconnaissance,
            APTOperationPhase.INITIAL_ACCESS: self._phase_initial_access,
            APTOperationPhase.PERSISTENCE: self._phase_persistence,
            APTOperationPhase.PRIVILEGE_ESCALATION: self._phase_privilege_escalation,
            APTOperationPhase.LATERAL_MOVEMENT: self._phase_lateral_movement,
            APTOperationPhase.DATA_EXFILTRATION: self._phase_data_exfiltration,
            APTOperationPhase.COVER_TRACKS: self._phase_cover_tracks
        }
        
        handler = phase_handlers.get(phase)
        if handler:
            result = handler(operation)
            operation.results[phase.value] = {
                "timestamp": datetime.now().isoformat(),
                "duration": time.time() - phase_start,
                "result": result
            }
            
            self.metrics["total_actions"] += 1
        
        if not self.config.stealth_logging:
            print(f"✅ Phase terminée: {phase.value} ({time.time() - phase_start:.1f}s)")
    
    def _phase_reconnaissance(self, operation: APTOperation) -> Dict[str, Any]:
        """
        Phase de reconnaissance
        
        Args:
            operation: Opération en cours
            
        Returns:
            Résultats de la reconnaissance
        """
        import socket
        import subprocess
        
        results = {
            "ip": None,
            "open_ports": [],
            "services": [],
            "technologies": []
        }
        
        # Résolution DNS
        try:
            results["ip"] = socket.gethostbyname(operation.target)
        except:
            pass
        
        # Scan de ports basique
        common_ports = [22, 80, 443, 8080, 3306, 5432, 3389, 445]
        for port in common_ports:
            if self._is_port_open(results.get("ip") or operation.target, port):
                results["open_ports"].append(port)
                self._apply_action_delay()
        
        return results
    
    def _phase_initial_access(self, operation: APTOperation) -> Dict[str, Any]:
        """
        Phase d'accès initial
        
        Args:
            operation: Opération en cours
            
        Returns:
            Résultats de l'accès initial
        """
        results = {
            "access_granted": False,
            "method": None,
            "credentials": None
        }
        
        # Tentatives d'accès (simulées)
        methods = ["ssh", "ftp", "web", "api"]
        
        for method in methods:
            self._apply_action_delay()
            # Simulation de tentative d'accès
            if random.random() < 0.3:  # 30% de chance de succès
                results["access_granted"] = True
                results["method"] = method
                break
        
        return results
    
    def _phase_persistence(self, operation: APTOperation) -> Dict[str, Any]:
        """
        Phase d'installation persistante
        
        Args:
            operation: Opération en cours
            
        Returns:
            Résultats de la persistance
        """
        results = {
            "persistence_established": False,
            "methods": []
        }
        
        for method in self.config.persistence_methods:
            self._apply_action_delay()
            
            if method == "webshell":
                # Installation de webshell
                results["methods"].append("webshell")
                results["persistence_established"] = True
            elif method == "cron_job":
                # Installation de cron job
                results["methods"].append("cron_job")
                results["persistence_established"] = True
            elif method == "scheduled_task":
                # Installation de tâche planifiée
                results["methods"].append("scheduled_task")
                results["persistence_established"] = True
        
        return results
    
    def _phase_privilege_escalation(self, operation: APTOperation) -> Dict[str, Any]:
        """
        Phase d'élévation de privilèges
        
        Args:
            operation: Opération en cours
            
        Returns:
            Résultats de l'élévation
        """
        results = {
            "escalated": False,
            "methods": [],
            "privilege_level": "user"
        }
        
        # Techniques d'élévation (simulées)
        techniques = ["sudo", "suid", "kernel_exploit", "docker"]
        
        for technique in techniques:
            self._apply_action_delay()
            if random.random() < 0.2:  # 20% de chance de succès
                results["escalated"] = True
                results["methods"].append(technique)
                results["privilege_level"] = "root"
                break
        
        return results
    
    def _phase_lateral_movement(self, operation: APTOperation) -> Dict[str, Any]:
        """
        Phase de mouvement latéral
        
        Args:
            operation: Opération en cours
            
        Returns:
            Résultats du mouvement latéral
        """
        results = {
            "targets": [],
            "compromised": []
        }
        
        # Détection de cibles internes (simulée)
        internal_targets = ["10.0.0.2", "10.0.0.3", "192.168.1.2"]
        
        for target in internal_targets:
            self._apply_action_delay()
            if random.random() < 0.3:
                results["targets"].append(target)
                if random.random() < 0.5:
                    results["compromised"].append(target)
        
        return results
    
    def _phase_data_exfiltration(self, operation: APTOperation) -> Dict[str, Any]:
        """
        Phase d'exfiltration de données
        
        Args:
            operation: Opération en cours
            
        Returns:
            Résultats de l'exfiltration
        """
        results = {
            "exfiltrated": False,
            "method": self.config.exfil_method,
            "data_size": 0,
            "endpoint": self.config.exfil_endpoint
        }
        
        if self.config.exfil_endpoint:
            self._apply_action_delay()
            
            # Simulation d'exfiltration
            data_size = random.randint(1024, 10485760)  # 1KB à 10MB
            results["data_size"] = data_size
            results["exfiltrated"] = True
            self.metrics["data_exfiltrated"] += data_size
        
        return results
    
    def _phase_cover_tracks(self, operation: APTOperation) -> Dict[str, Any]:
        """
        Phase d'effacement des traces
        
        Args:
            operation: Opération en cours
            
        Returns:
            Résultats du nettoyage
        """
        results = {
            "logs_cleared": True,
            "artifacts_removed": True,
            "actions": []
        }
        
        # Simulation de nettoyage
        actions = ["cleared_auth_logs", "removed_temp_files", "cleaned_history"]
        
        for action in actions:
            self._apply_action_delay()
            results["actions"].append(action)
        
        return results
    
    def _apply_phase_delay(self):
        """Applique un délai entre les phases"""
        delay = random.randint(self.config.phase_delay_min, self.config.phase_delay_max)
        
        # Ajouter du jitter
        jitter = delay * self.config.jitter
        delay += random.uniform(-jitter, jitter)
        delay = max(0, delay)
        
        self.metrics["total_delay_time"] += delay
        
        if not self.config.stealth_logging:
            print(f"💤 Pause inter-phase: {delay:.0f}s")
        
        # Découpage en petites pauses
        while delay > 0 and not self.stop_event.is_set():
            sleep_time = min(10, delay)
            time.sleep(sleep_time)
            delay -= sleep_time
    
    def _apply_action_delay(self):
        """Applique un délai entre les actions"""
        delay = random.uniform(self.config.action_delay_min, self.config.action_delay_max)
        
        # Ajouter du jitter
        jitter = delay * self.config.jitter
        delay += random.uniform(-jitter, jitter)
        delay = max(0, delay)
        
        self.metrics["total_delay_time"] += delay
        time.sleep(delay)
    
    def _is_work_hours(self) -> bool:
        """
        Vérifie si on est en période de travail
        
        Returns:
            True si période de travail
        """
        current_hour = datetime.now().hour
        
        if self.config.work_start <= self.config.work_end:
            return (self.config.work_start <= current_hour < self.config.work_end)
        else:
            return (current_hour >= self.config.work_start or 
                   current_hour < self.config.work_end)
    
    def _wait_for_work_hours(self):
        """Attend que la période de travail commence"""
        now = datetime.now()
        current_hour = now.hour
        
        if current_hour < self.config.work_start:
            target_hour = self.config.work_start
        else:
            target_hour = self.config.work_end
        
        target_time = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        if target_time <= now:
            target_time += timedelta(days=1)
        
        wait_seconds = (target_time - now).total_seconds()
        
        if not self.config.stealth_logging:
            print(f"💤 Pause jusqu'à {target_time.strftime('%H:%M')}")
        
        while wait_seconds > 0 and not self.stop_event.is_set():
            sleep_time = min(60, wait_seconds)
            time.sleep(sleep_time)
            wait_seconds -= sleep_time
    
    def _is_port_open(self, host: str, port: int) -> bool:
        """
        Vérifie si un port est ouvert
        
        Args:
            host: Hôte
            port: Port
            
        Returns:
            True si ouvert
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def cleanup_traces(self) -> bool:
        """
        Nettoie les traces de l'opération
        
        Returns:
            True si succès
        """
        if not self.config.stealth_logging:
            print("🧹 Nettoyage des traces...")
        
        # Simulation de nettoyage
        time.sleep(2)
        
        return True
    
    def get_operation_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le statut d'une opération
        
        Args:
            operation_id: ID de l'opération
            
        Returns:
            Statut de l'opération
        """
        if operation_id not in self.operations:
            return None
        
        op = self.operations[operation_id]
        return {
            "id": op.id,
            "name": op.name,
            "target": op.target,
            "status": op.status.value,
            "current_phase": op.current_phase,
            "total_phases": len(op.phases),
            "start_time": op.start_time.isoformat() if op.start_time else None,
            "end_time": op.end_time.isoformat() if op.end_time else None,
            "results": op.results,
            "logs": op.logs[-10:] if op.logs else []
        }
    
    def list_operations(self) -> List[Dict[str, Any]]:
        """
        Liste toutes les opérations
        
        Returns:
            Liste des opérations
        """
        return [
            {
                "id": op.id,
                "name": op.name,
                "target": op.target,
                "status": op.status.value,
                "created": op.start_time.isoformat() if op.start_time else "pending"
            }
            for op in self.operations.values()
        ]
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Récupère les métriques d'exécution
        
        Returns:
            Métriques collectées
        """
        return {
            **self.metrics,
            "is_running": self.is_running,
            "active_operation": self.active_operation.id if self.active_operation else None,
            "total_operations": len(self.operations),
            "config": {
                "phase_delay_min": self.config.phase_delay_min,
                "phase_delay_max": self.config.phase_delay_max,
                "action_delay_min": self.config.action_delay_min,
                "action_delay_max": self.config.action_delay_max,
                "stealth_logging": self.config.stealth_logging,
                "auto_cleanup": self.config.auto_cleanup
            }
        }
    
    def generate_report(self, operation_id: str, format: str = "json") -> Optional[str]:
        """
        Génère un rapport pour une opération
        
        Args:
            operation_id: ID de l'opération
            format: Format du rapport (json, text)
            
        Returns:
            Rapport formaté
        """
        if operation_id not in self.operations:
            return None
        
        op = self.operations[operation_id]
        
        if format == "json":
            return json.dumps({
                "operation": {
                    "id": op.id,
                    "name": op.name,
                    "target": op.target,
                    "status": op.status.value,
                    "start_time": op.start_time.isoformat() if op.start_time else None,
                    "end_time": op.end_time.isoformat() if op.end_time else None,
                    "duration": (op.end_time - op.start_time).total_seconds() if op.start_time and op.end_time else 0
                },
                "phases": op.results,
                "metrics": self.metrics
            }, indent=2, ensure_ascii=False)
        else:
            report = f"""
╔══════════════════════════════════════════════════════════════════╗
║  RAPPORT OPÉRATION APT - {op.name}                               ║
╚══════════════════════════════════════════════════════════════════╝

📋 INFORMATIONS GÉNÉRALES:
  ID: {op.id}
  Cible: {op.target}
  Statut: {op.status.value}
  Début: {op.start_time.isoformat() if op.start_time else 'N/A'}
  Fin: {op.end_time.isoformat() if op.end_time else 'N/A'}
  Durée: {(op.end_time - op.start_time).total_seconds() if op.start_time and op.end_time else 0:.1f}s

📊 PHASES EXÉCUTÉES:
"""
            for phase_name, phase_result in op.results.items():
                report += f"""
  📍 {phase_name.upper()}:
     Durée: {phase_result.get('duration', 0):.1f}s
     Résultat: {json.dumps(phase_result.get('result', {}), indent=2)[:200]}...
"""
            
            report += f"""
📈 MÉTRIQUES:
  Opérations totales: {self.metrics['operations_count']}
  Opérations réussies: {self.metrics['successful_operations']}
  Actions totales: {self.metrics['total_actions']}
  Temps de délai total: {self.metrics['total_delay_time']:.1f}s
  Données exfiltrées: {self.metrics['data_exfiltrated'] / 1024:.2f} KB
"""
            return report
    
    def shutdown(self):
        """Arrête proprement le gestionnaire APT"""
        if self.active_operation:
            self.stop_operation()
        
        self.is_running = False
        if not self.config.stealth_logging:
            print("🛑 APT Utils arrêté")


# Instance globale
apt_utils = APTUtils()


# Fonctions de commodité
def create_apt_operation(name: str, target: str, **kwargs) -> str:
    """Crée une opération APT"""
    phases = kwargs.get('phases')
    if phases:
        phases = [APTOperationPhase(p) for p in phases]
    return apt_utils.create_operation(name, target, phases, kwargs.get('config'))


def start_apt_operation(operation_id: str) -> bool:
    """Démarre une opération APT"""
    return apt_utils.start_operation(operation_id)


def stop_apt_operation() -> bool:
    """Arrête l'opération APT active"""
    return apt_utils.stop_operation()


def get_apt_status() -> Dict[str, Any]:
    """Retourne le statut APT"""
    return apt_utils.get_metrics()


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test des utilitaires APT")
    print("=" * 60)
    
    # Configuration
    apt_utils.set_config({
        'stealth_logging': False,
        'phase_delay_min': 5,
        'phase_delay_max': 10,
        'action_delay_min': 1,
        'action_delay_max': 2
    })
    
    # Créer une opération
    op_id = create_apt_operation(
        "Test Operation",
        "example.com",
        phases=["reconnaissance", "initial_access"]
    )
    
    print(f"✅ Opération créée: {op_id}")
    
    # Démarrer l'opération (simulée)
    # start_apt_operation(op_id)
    # time.sleep(5)
    # stop_apt_operation()
    
    # Afficher les métriques
    metrics = get_apt_status()
    print(f"\n📊 Métriques: {metrics}")
    
    print("\n✅ Module APT Utils chargé avec succès")