#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedForge v2.0 - APT Controller
Gestionnaire d'opérations APT (Advanced Persistent Threat)
Support Multi-Attacks, Mode Furtif et Opérations APT
"""

import os
import sys
import json
import time
import random
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Configuration du logging
logger = logging.getLogger(__name__)


@dataclass
class APTPhase:
    """Structure d'une phase APT"""
    name: str
    attacks: List[str]
    status: str = "pending"
    progress: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None


@dataclass
class APTOperation:
    """Structure d'une opération APT complète"""
    id: str
    name: str
    description: str
    target: str
    phases: List[APTPhase]
    stealth_level: str
    status: str = "pending"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    current_phase: int = 0
    total_phases: int = 0
    results: Dict = None
    error: Optional[str] = None
    
    def __post_init__(self):
        self.total_phases = len(self.phases)
        if self.results is None:
            self.results = {}


class APTController:
    """
    Contrôleur pour les opérations APT.
    Gère l'exécution des opérations, les phases, la persistance,
    le mouvement latéral et l'exfiltration de données.
    """
    
    # Opérations APT prédéfinies
    PREDEFINED_OPERATIONS = {
        "recon_to_exfil": {
            "name": "Reconnaissance → Exfiltration",
            "description": "Opération APT complète de la reconnaissance à l'exfiltration de données",
            "phases": [
                {"name": "Reconnaissance", "attacks": ["port_scan", "service_enum", "subdomain_enum", "technology_detect"]},
                {"name": "Initial Access", "attacks": ["sql_injection", "xss", "file_upload", "command_injection"]},
                {"name": "Persistence", "attacks": ["backdoor", "scheduled_task", "registry_persistence", "ssh_key"]},
                {"name": "Privilege Escalation", "attacks": ["sudo_abuse", "kernel_exploit", "win_priv_esc"]},
                {"name": "Lateral Movement", "attacks": ["ssh_pivot", "smb_exec", "wmi_exec", "ps_exec"]},
                {"name": "Data Exfiltration", "attacks": ["dns_exfil", "http_exfil", "custom_protocol"]}
            ],
            "auto_cleanup": True,
            "persistence_type": "registry",
            "exfil_method": "dns_tunneling"
        },
        "web_app_compromise": {
            "name": "Compromission d'Application Web",
            "description": "Ciblage spécifique d'applications web avec persistance",
            "phases": [
                {"name": "Footprinting", "attacks": ["whatweb", "waf_detection", "tech_stack"]},
                {"name": "Vulnerability Scan", "attacks": ["sql_injection", "xss", "csrf", "ssrf"]},
                {"name": "Exploitation", "attacks": ["sqli_union", "xss_persistent", "rce"]},
                {"name": "Post Exploitation", "attacks": ["web_shell", "reverse_shell", "database_dump"]}
            ],
            "auto_cleanup": True,
            "persistence_type": "web_shell",
            "exfil_method": "http"
        },
        "lateral_movement": {
            "name": "Mouvement Latéral",
            "description": "Propagation sur le réseau interne",
            "phases": [
                {"name": "Network Discovery", "attacks": ["network_scan", "host_discovery", "service_enum"]},
                {"name": "Credential Dumping", "attacks": ["hash_dump", "mimikatz", "credential_theft"]},
                {"name": "Lateral Movement", "attacks": ["ssh_pivot", "smb_exec", "wmi_exec", "rdp"]}
            ],
            "auto_cleanup": True,
            "persistence_type": "none",
            "exfil_method": "none"
        },
        "persistence": {
            "name": "Persistance Avancée",
            "description": "Mise en place de mécanismes de persistance",
            "phases": [
                {"name": "Backdoor Installation", "attacks": ["backdoor", "webshell", "reverse_shell"]},
                {"name": "Scheduled Tasks", "attacks": ["cron_job", "schtasks", "systemd_service"]},
                {"name": "Registry Persistence", "attacks": ["registry_run", "login_hook", "startup_folder"]}
            ],
            "auto_cleanup": False,
            "persistence_type": "multi",
            "exfil_method": "none"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le contrôleur APT.
        
        Args:
            config_path: Chemin vers le fichier de configuration (optionnel)
        """
        self.operations: Dict[str, APTOperation] = {}
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Créer les dossiers nécessaires
        self._create_directories()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Charge la configuration APT"""
        default_config = {
            "persistence_dir": "/opt/redforge/persistence",
            "exfiltration_dir": "/opt/redforge/exfiltration",
            "logs_dir": "/opt/redforge/logs/apt",
            "default_stealth_level": "medium",
            "auto_cleanup": True,
            "phase_delay": 5,
            "max_retries": 3,
            "timeout_per_phase": 600,
            "chunk_size": 512,
            "encryption": "aes-256-gcm"
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Impossible de charger la configuration: {e}")
        
        return default_config
    
    def _create_directories(self):
        """Crée les dossiers nécessaires pour les opérations APT"""
        dirs = [
            self.config["persistence_dir"],
            self.config["exfiltration_dir"],
            self.config["logs_dir"]
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
    
    def list_operations(self) -> Dict[str, Any]:
        """
        Liste toutes les opérations APT disponibles.
        
        Returns:
            Dictionnaire contenant les opérations prédéfinies et personnalisées
        """
        custom_ops = {}
        custom_ops_dir = Path("/opt/redforge/apt_operations/custom")
        
        if custom_ops_dir.exists():
            for op_file in custom_ops_dir.glob("*.json"):
                try:
                    with open(op_file, 'r', encoding='utf-8') as f:
                        op_data = json.load(f)
                        custom_ops[op_file.stem] = op_data
                except Exception as e:
                    logger.warning(f"Erreur chargement opération {op_file}: {e}")
        
        return {
            "predefined": self.PREDEFINED_OPERATIONS,
            "custom": custom_ops,
            "total": len(self.PREDEFINED_OPERATIONS) + len(custom_ops)
        }
    
    def get_operation(self, operation_id: str) -> Optional[Dict]:
        """
        Récupère les détails d'une opération APT.
        
        Args:
            operation_id: Identifiant de l'opération
            
        Returns:
            Dictionnaire des détails de l'opération ou None
        """
        if operation_id in self.PREDEFINED_OPERATIONS:
            return self.PREDEFINED_OPERATIONS[operation_id]
        
        custom_path = Path(f"/opt/redforge/apt_operations/custom/{operation_id}.json")
        if custom_path.exists():
            try:
                with open(custom_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return None
    
    def create_custom_operation(self, name: str, description: str, phases: List[Dict],
                                 cleanup: bool = True, persistence_type: str = "none",
                                 exfil_method: str = "none") -> Dict[str, Any]:
        """
        Crée une opération APT personnalisée.
        
        Args:
            name: Nom de l'opération
            description: Description
            phases: Liste des phases avec leurs attaques
            cleanup: Nettoyage post-opération
            persistence_type: Type de persistance
            exfil_method: Méthode d'exfiltration
            
        Returns:
            Dictionnaire de résultat
        """
        operation_id = name.lower().replace(" ", "_")
        custom_dir = Path("/opt/redforge/apt_operations/custom")
        custom_dir.mkdir(parents=True, exist_ok=True)
        
        operation_data = {
            "name": name,
            "description": description,
            "phases": phases,
            "auto_cleanup": cleanup,
            "persistence_type": persistence_type,
            "exfil_method": exfil_method,
            "created_at": datetime.now().isoformat()
        }
        
        operation_file = custom_dir / f"{operation_id}.json"
        with open(operation_file, 'w', encoding='utf-8') as f:
            json.dump(operation_data, f, indent=4, ensure_ascii=False)
        
        return {
            "success": True,
            "operation_id": operation_id,
            "file": str(operation_file),
            "message": f"Opération {name} créée avec succès"
        }
    
    def run_operation(self, operation_id: str, target: str, 
                      stealth_level: str = "medium",
                      options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Exécute une opération APT complète.
        
        Args:
            operation_id: Identifiant de l'opération
            target: Cible de l'opération
            stealth_level: Niveau de furtivité (low, medium, high, paranoid)
            options: Options supplémentaires
            
        Returns:
            Dictionnaire des résultats
        """
        # Récupérer la configuration de l'opération
        operation_config = self.get_operation(operation_id)
        if not operation_config:
            return {
                "success": False,
                "error": f"Opération {operation_id} non trouvée",
                "available_operations": list(self.PREDEFINED_OPERATIONS.keys())
            }
        
        # Créer l'objet opération
        phases = []
        for i, phase_data in enumerate(operation_config.get("phases", [])):
            phase = APTPhase(
                name=phase_data.get("name", f"Phase {i+1}"),
                attacks=phase_data.get("attacks", [])
            )
            phases.append(phase)
        
        operation = APTOperation(
            id=operation_id,
            name=operation_config.get("name", operation_id),
            description=operation_config.get("description", ""),
            target=target,
            phases=phases,
            stealth_level=stealth_level,
            status="running",
            start_time=datetime.now().isoformat()
        )
        
        self.operations[operation_id] = operation
        
        # Exécuter les phases
        results = self._execute_phases(operation, options or {})
        
        operation.end_time = datetime.now().isoformat()
        operation.status = "completed" if not operation.error else "failed"
        operation.results = results
        
        # Nettoyage si demandé
        if operation_config.get("auto_cleanup", True) and options.get("cleanup", True):
            self._cleanup_operation(operation)
        
        return {
            "success": not bool(operation.error),
            "operation_id": operation_id,
            "operation_name": operation.name,
            "target": target,
            "status": operation.status,
            "phases": [asdict(p) for p in operation.phases],
            "results": results,
            "start_time": operation.start_time,
            "end_time": operation.end_time,
            "duration": self._calculate_duration(operation.start_time, operation.end_time),
            "stealth_level": stealth_level
        }
    
    def _execute_phases(self, operation: APTOperation, options: Dict) -> Dict:
        """
        Exécute les phases de l'opération.
        
        Args:
            operation: Opération APT
            options: Options supplémentaires
            
        Returns:
            Dictionnaire des résultats par phase
        """
        results = {}
        stealth_config = self._get_stealth_config(operation.stealth_level)
        
        for i, phase in enumerate(operation.phases):
            operation.current_phase = i
            phase.status = "running"
            phase.start_time = datetime.now().isoformat()
            
            logger.info(f"Exécution de la phase {i+1}/{len(operation.phases)}: {phase.name}")
            
            # Délai furtif
            if stealth_config["enabled"]:
                time.sleep(stealth_config["delay"])
            
            # Exécuter les attaques de la phase
            phase_results = []
            phase_success = True
            
            for attack in phase.attacks:
                attack_result = self._execute_attack(
                    operation.target, 
                    attack, 
                    stealth_config,
                    options
                )
                phase_results.append(attack_result)
                if not attack_result.get("success", False):
                    phase_success = False
            
            phase.end_time = datetime.now().isoformat()
            phase.status = "completed" if phase_success else "failed"
            phase.progress = 100
            phase.result = {
                "attacks": phase_results,
                "success_count": sum(1 for r in phase_results if r.get("success")),
                "total_count": len(phase.attacks),
                "success_rate": (sum(1 for r in phase_results if r.get("success")) / len(phase.attacks)) * 100
            }
            
            results[phase.name] = phase.result
            
            # Pause entre les phases
            if i < len(operation.phases) - 1:
                time.sleep(self.config.get("phase_delay", 5))
        
        return results
    
    def _execute_attack(self, target: str, attack_type: str, 
                        stealth_config: Dict, options: Dict) -> Dict:
        """
        Exécute une attaque spécifique.
        
        Args:
            target: Cible
            attack_type: Type d'attaque
            stealth_config: Configuration furtive
            options: Options supplémentaires
            
        Returns:
            Résultat de l'attaque
        """
        # Simuler l'exécution de l'attaque
        # Dans une implémentation réelle, cela appellerait les modules d'attaque
        
        import random
        
        # Simuler un délai d'exécution
        exec_time = random.uniform(1, 5)
        time.sleep(exec_time)
        
        # Simuler un taux de succès basé sur la furtivité
        stealth_bonus = {
            "low": 0.7,
            "medium": 0.8,
            "high": 0.85,
            "paranoid": 0.9
        }
        success_rate = stealth_bonus.get(stealth_config.get("level", "medium"), 0.8)
        success = random.random() < success_rate
        
        return {
            "attack": attack_type,
            "target": target,
            "success": success,
            "execution_time": round(exec_time, 2),
            "timestamp": datetime.now().isoformat(),
            "stealth_used": stealth_config.get("enabled", False),
            "stealth_level": stealth_config.get("level", "medium")
        }
    
    def _get_stealth_config(self, level: str) -> Dict:
        """
        Retourne la configuration furtive pour un niveau donné.
        
        Args:
            level: Niveau de furtivité
            
        Returns:
            Configuration furtive
        """
        configs = {
            "low": {"enabled": True, "delay": 0.5, "jitter": 0.1, "level": "low"},
            "medium": {"enabled": True, "delay": 1.5, "jitter": 0.3, "level": "medium"},
            "high": {"enabled": True, "delay": 3.0, "jitter": 0.5, "level": "high"},
            "paranoid": {"enabled": True, "delay": 5.0, "jitter": 0.7, "level": "paranoid"}
        }
        return configs.get(level, configs["medium"])
    
    def _cleanup_operation(self, operation: APTOperation):
        """
        Nettoie les traces de l'opération.
        
        Args:
            operation: Opération à nettoyer
        """
        logger.info(f"Nettoyage de l'opération {operation.id}")
        
        # Simuler le nettoyage
        # Dans une implémentation réelle, cela supprimerait les fichiers temporaires,
        # les backdoors, les logs, etc.
        
        pass
    
    def _calculate_duration(self, start_time: str, end_time: str) -> int:
        """
        Calcule la durée en secondes entre deux timestamps.
        
        Args:
            start_time: Timestamp de début
            end_time: Timestamp de fin
            
        Returns:
            Durée en secondes
        """
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            return int((end - start).total_seconds())
        except Exception:
            return 0
    
    def get_operation_status(self, operation_id: str) -> Optional[Dict]:
        """
        Récupère le statut d'une opération en cours.
        
        Args:
            operation_id: Identifiant de l'opération
            
        Returns:
            Statut de l'opération ou None
        """
        if operation_id in self.operations:
            op = self.operations[operation_id]
            return {
                "operation_id": op.id,
                "operation_name": op.name,
                "status": op.status,
                "current_phase": op.current_phase,
                "total_phases": op.total_phases,
                "start_time": op.start_time,
                "end_time": op.end_time,
                "error": op.error
            }
        return None
    
    def stop_operation(self, operation_id: str) -> Dict[str, Any]:
        """
        Arrête une opération en cours.
        
        Args:
            operation_id: Identifiant de l'opération
            
        Returns:
            Résultat de l'arrêt
        """
        if operation_id in self.operations:
            op = self.operations[operation_id]
            op.status = "stopped"
            op.end_time = datetime.now().isoformat()
            
            return {
                "success": True,
                "operation_id": operation_id,
                "message": f"Opération {op.name} arrêtée"
            }
        
        return {
            "success": False,
            "error": f"Opération {operation_id} non trouvée"
        }
    
    def cleanup_all(self) -> Dict[str, Any]:
        """
        Nettoie toutes les traces des opérations.
        
        Returns:
            Résultat du nettoyage
        """
        logger.info("Nettoyage global des traces APT")
        
        # Nettoyer les dossiers
        dirs_to_clean = [
            self.config["persistence_dir"],
            self.config["exfiltration_dir"],
            "/tmp/redforge_persistence"
        ]
        
        for d in dirs_to_clean:
            if os.path.exists(d):
                import shutil
                try:
                    shutil.rmtree(d)
                    os.makedirs(d, exist_ok=True)
                except Exception as e:
                    logger.warning(f"Erreur nettoyage {d}: {e}")
        
        return {
            "success": True,
            "message": "Nettoyage global terminé",
            "cleaned_dirs": dirs_to_clean
        }


# Point d'entrée pour les tests
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test du contrôleur APT
    controller = APTController()
    
    # Lister les opérations
    print("=== Opérations APT disponibles ===")
    ops = controller.list_operations()
    print(f"Prédéfinies: {list(ops['predefined'].keys())}")
    print(f"Total: {ops['total']}")
    
    # Exécuter une opération de test
    print("\n=== Exécution de l'opération recon_to_exfil ===")
    result = controller.run_operation("recon_to_exfil", "https://example.com", "high")
    print(f"Résultat: {result['status']}")
    print(f"Phases exécutées: {len(result['phases'])}")
    
    # Créer une opération personnalisée
    print("\n=== Création d'une opération personnalisée ===")
    custom_phases = [
        {"name": "Phase 1", "attacks": ["port_scan", "service_enum"]},
        {"name": "Phase 2", "attacks": ["sql_injection", "xss"]}
    ]
    custom_result = controller.create_custom_operation(
        name="Mon Opération Test",
        description="Test de création d'opération",
        phases=custom_phases,
        cleanup=True
    )
    print(f"Création: {custom_result['message']}")
    
    print("\n✅ APT Controller prêt à l'emploi !")