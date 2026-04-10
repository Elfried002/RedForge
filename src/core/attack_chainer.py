#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedForge v2.0 - Attack Chainer
Module de chaînage d'attaques pour orchestrer des séquences d'exploitation complexes
Support Multi-Attacks, Mode Furtif et Opérations APT
"""

import time
import random
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Configuration du logging
logger = logging.getLogger(__name__)


class ChainMode(Enum):
    """Modes d'exécution des chaînes d'attaques"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ADAPTIVE = "adaptive"


class AttackStatus(Enum):
    """Statuts possibles d'une attaque dans la chaîne"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"


@dataclass
class AttackStep:
    """Représente une étape d'attaque dans la chaîne"""
    id: str
    name: str
    category: str
    attack_type: str
    options: Dict[str, Any] = field(default_factory=dict)
    status: AttackStatus = AttackStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[str] = None


@dataclass
class AttackChain:
    """Représente une chaîne d'attaques complète"""
    id: str
    name: str
    description: str
    steps: List[AttackStep]
    mode: ChainMode = ChainMode.SEQUENTIAL
    status: str = "pending"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    current_step: int = 0
    results: Dict = field(default_factory=dict)
    error: Optional[str] = None


class AttackChainer:
    """
    Gestionnaire de chaînage d'attaques.
    Permet de créer et d'exécuter des séquences d'attaques complexes.
    """
    
    # Chaînes d'attaques prédéfinies
    PREDEFINED_CHAINS = {
        "full_web_pentest": {
            "name": "Pentest Web Complet",
            "description": "Chaîne complète pour pentest d'application web",
            "steps": [
                {"name": "Reconnaissance", "category": "footprint", "attack_type": "whatweb"},
                {"name": "Scan des ports", "category": "infrastructure", "attack_type": "port_scan"},
                {"name": "Découverte des répertoires", "category": "analysis", "attack_type": "dirbuster"},
                {"name": "Scan XSS", "category": "cross_site", "attack_type": "xss"},
                {"name": "Scan SQLi", "category": "injection", "attack_type": "sql"},
                {"name": "Exploitation", "category": "exploit", "attack_type": "auto"},
                {"name": "Post-exploitation", "category": "exploit", "attack_type": "post"}
            ]
        },
        "sqli_to_rce": {
            "name": "SQLi → RCE",
            "description": "Chaîne d'attaque de l'injection SQL à l'exécution de code",
            "steps": [
                {"name": "Détection SQLi", "category": "injection", "attack_type": "sql", 
                 "options": {"detection_only": True}},
                {"name": "Extraction de données", "category": "injection", "attack_type": "sql",
                 "options": {"technique": "union"}},
                {"name": "Écriture de fichier", "category": "injection", "attack_type": "sql",
                 "options": {"technique": "into_outfile"}},
                {"name": "Exécution de code", "category": "advanced", "attack_type": "rce",
                 "options": {"shell_type": "webshell"}}
            ]
        },
        "xss_to_hijack": {
            "name": "XSS → Hijacking",
            "description": "Chaîne d'attaque du XSS au détournement de session",
            "steps": [
                {"name": "Détection XSS", "category": "cross_site", "attack_type": "xss"},
                {"name": "Payload XSS", "category": "cross_site", "attack_type": "xss",
                 "options": {"payload_type": "steal_cookie"}},
                {"name": "Récupération session", "category": "session", "attack_type": "hijacking"},
                {"name": "Prise de contrôle", "category": "exploit", "attack_type": "session"}
            ]
        },
        "lfi_to_rce": {
            "name": "LFI → RCE",
            "description": "Chaîne d'attaque du LFI à l'exécution de code",
            "steps": [
                {"name": "Détection LFI", "category": "file_system", "attack_type": "lfi_rfi"},
                {"name": "Lecture de fichiers", "category": "file_system", "attack_type": "lfi_rfi",
                 "options": {"action": "read"}},
                {"name": "Upload de shell", "category": "file_system", "attack_type": "file_upload"},
                {"name": "Exécution de code", "category": "advanced", "attack_type": "rce"}
            ]
        },
        "ssrf_to_internal": {
            "name": "SSRF → Internal Scan",
            "description": "Chaîne d'attaque du SSRF au scan interne",
            "steps": [
                {"name": "Détection SSRF", "category": "advanced", "attack_type": "ssrf"},
                {"name": "Scan interne", "category": "infrastructure", "attack_type": "port_scan",
                 "options": {"internal": True}},
                {"name": "Exploitation services", "category": "exploit", "attack_type": "internal"}
            ]
        },
        "api_breach": {
            "name": "API Breach",
            "description": "Chaîne d'attaque pour API REST/GraphQL",
            "steps": [
                {"name": "Découverte API", "category": "analysis", "attack_type": "api_discovery"},
                {"name": "Test injection", "category": "advanced", "attack_type": "api"},
                {"name": "Exploitation", "category": "advanced", "attack_type": "graphql"},
                {"name": "Exfiltration", "category": "advanced", "attack_type": "data_exfil"}
            ]
        }
    }
    
    def __init__(self, target: Optional[str] = None, stealth_level: str = "medium"):
        """
        Initialise le gestionnaire de chaînage.
        
        Args:
            target: Cible par défaut
            stealth_level: Niveau de furtivité par défaut
        """
        self.target = target
        self.stealth_level = stealth_level
        self.chains: Dict[str, AttackChain] = {}
        self.results: List[Dict] = []
        self.logger = logging.getLogger(__name__)
    
    def get_stealth_delay(self) -> float:
        """Retourne le délai en fonction du niveau furtif"""
        delays = {
            "low": 0.5,
            "medium": 1.5,
            "high": 3.0,
            "paranoid": 5.0
        }
        base_delay = delays.get(self.stealth_level, 1.5)
        jitter = random.uniform(0.8, 1.2)
        return base_delay * jitter
    
    def list_chains(self) -> Dict[str, Any]:
        """
        Liste toutes les chaînes d'attaques disponibles.
        
        Returns:
            Dictionnaire des chaînes prédéfinies et personnalisées
        """
        custom_chains = {}
        for chain_id, chain in self.chains.items():
            custom_chains[chain_id] = {
                "name": chain.name,
                "description": chain.description,
                "steps_count": len(chain.steps),
                "mode": chain.mode.value
            }
        
        return {
            "predefined": self.PREDEFINED_CHAINS,
            "custom": custom_chains,
            "total": len(self.PREDEFINED_CHAINS) + len(custom_chains)
        }
    
    def get_chain(self, chain_id: str) -> Optional[Dict]:
        """
        Récupère une chaîne d'attaque par son ID.
        
        Args:
            chain_id: Identifiant de la chaîne
            
        Returns:
            Dictionnaire de la chaîne ou None
        """
        if chain_id in self.PREDEFINED_CHAINS:
            return self.PREDEFINED_CHAINS[chain_id]
        
        if chain_id in self.chains:
            chain = self.chains[chain_id]
            return {
                "name": chain.name,
                "description": chain.description,
                "steps": [
                    {
                        "name": step.name,
                        "category": step.category,
                        "attack_type": step.attack_type,
                        "options": step.options
                    }
                    for step in chain.steps
                ],
                "mode": chain.mode.value
            }
        
        return None
    
    def create_chain(self, name: str, description: str, steps: List[Dict],
                     mode: str = "sequential") -> str:
        """
        Crée une chaîne d'attaque personnalisée.
        
        Args:
            name: Nom de la chaîne
            description: Description
            steps: Liste des étapes
            mode: Mode d'exécution (sequential, parallel, conditional, adaptive)
            
        Returns:
            ID de la chaîne créée
        """
        chain_id = name.lower().replace(" ", "_")
        
        attack_steps = []
        for i, step_data in enumerate(steps):
            step = AttackStep(
                id=f"{chain_id}_step_{i}",
                name=step_data.get("name", f"Étape {i+1}"),
                category=step_data.get("category", "advanced"),
                attack_type=step_data.get("attack_type", "unknown"),
                options=step_data.get("options", {}),
                depends_on=step_data.get("depends_on", []),
                condition=step_data.get("condition"),
                max_retries=step_data.get("max_retries", 3)
            )
            attack_steps.append(step)
        
        chain = AttackChain(
            id=chain_id,
            name=name,
            description=description,
            steps=attack_steps,
            mode=ChainMode(mode)
        )
        
        self.chains[chain_id] = chain
        return chain_id
    
    def run_chain(self, chain_id: str, target: Optional[str] = None,
                  options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Exécute une chaîne d'attaque.
        
        Args:
            chain_id: Identifiant de la chaîne
            target: Cible (si différente de celle par défaut)
            options: Options supplémentaires
            
        Returns:
            Résultats de l'exécution
        """
        target = target or self.target
        if not target:
            return {
                "success": False,
                "error": "Aucune cible spécifiée"
            }
        
        # Récupérer la chaîne
        chain_config = self.get_chain(chain_id)
        if not chain_config:
            return {
                "success": False,
                "error": f"Chaîne {chain_id} non trouvée",
                "available_chains": list(self.PREDEFINED_CHAINS.keys())
            }
        
        # Créer la chaîne si elle n'existe pas déjà
        if chain_id not in self.chains:
            self.create_chain(
                name=chain_config.get("name", chain_id),
                description=chain_config.get("description", ""),
                steps=chain_config.get("steps", []),
                mode=options.get("mode", "sequential") if options else "sequential"
            )
        
        chain = self.chains[chain_id]
        chain.status = "running"
        chain.start_time = datetime.now().isoformat()
        
        results = []
        
        # Exécuter selon le mode
        if chain.mode == ChainMode.SEQUENTIAL:
            results = self._execute_sequential(chain, target, options)
        elif chain.mode == ChainMode.PARALLEL:
            results = self._execute_parallel(chain, target, options)
        elif chain.mode == ChainMode.CONDITIONAL:
            results = self._execute_conditional(chain, target, options)
        else:
            results = self._execute_adaptive(chain, target, options)
        
        chain.end_time = datetime.now().isoformat()
        chain.status = "completed" if not chain.error else "failed"
        chain.results = {"steps": results}
        
        return {
            "success": not bool(chain.error),
            "chain_id": chain_id,
            "chain_name": chain.name,
            "target": target,
            "mode": chain.mode.value,
            "status": chain.status,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status.value,
                    "duration": self._calculate_duration(step.start_time, step.end_time),
                    "result": step.result,
                    "error": step.error
                }
                for step in chain.steps
            ],
            "start_time": chain.start_time,
            "end_time": chain.end_time,
            "duration": self._calculate_duration(chain.start_time, chain.end_time),
            "stealth_level": self.stealth_level
        }
    
    def _execute_sequential(self, chain: AttackChain, target: str,
                            options: Optional[Dict]) -> List[Dict]:
        """Exécute les étapes séquentiellement"""
        results = []
        
        for i, step in enumerate(chain.steps):
            chain.current_step = i
            step.status = AttackStatus.RUNNING
            step.start_time = datetime.now().isoformat()
            
            # Appliquer le délai furtif
            time.sleep(self.get_stealth_delay())
            
            # Vérifier les dépendances
            if not self._check_dependencies(step, chain.steps):
                step.status = AttackStatus.SKIPPED
                step.error = "Dépendances non satisfaites"
                results.append({
                    "step": step.name,
                    "status": step.status.value,
                    "error": step.error
                })
                continue
            
            # Exécuter l'attaque
            result = self._execute_attack(target, step, options)
            
            step.end_time = datetime.now().isoformat()
            
            if result.get("success", False):
                step.status = AttackStatus.SUCCESS
                step.result = result
            else:
                if step.retry_count < step.max_retries:
                    step.retry_count += 1
                    step.status = AttackStatus.RETRY
                    # Réexécuter
                    time.sleep(self.get_stealth_delay() * 2)
                    result = self._execute_attack(target, step, options)
                    if result.get("success", False):
                        step.status = AttackStatus.SUCCESS
                        step.result = result
                    else:
                        step.status = AttackStatus.FAILED
                        step.error = result.get("error", "Échec de l'attaque")
                else:
                    step.status = AttackStatus.FAILED
                    step.error = result.get("error", "Échec de l'attaque")
            
            results.append({
                "step": step.name,
                "status": step.status.value,
                "duration": self._calculate_duration(step.start_time, step.end_time),
                "result": step.result,
                "error": step.error
            })
            
            # Si une étape échoue et qu'on ne continue pas, arrêter
            if step.status == AttackStatus.FAILED and not options.get("continue_on_error", False):
                chain.error = f"Échec à l'étape {step.name}"
                break
        
        return results
    
    def _execute_parallel(self, chain: AttackChain, target: str,
                          options: Optional[Dict]) -> List[Dict]:
        """Exécute les étapes en parallèle"""
        import concurrent.futures
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=options.get("max_workers", 5)) as executor:
            futures = {}
            
            for step in chain.steps:
                step.status = AttackStatus.RUNNING
                step.start_time = datetime.now().isoformat()
                future = executor.submit(self._execute_attack, target, step, options)
                futures[future] = step
            
            for future in concurrent.futures.as_completed(futures):
                step = futures[future]
                result = future.result()
                
                step.end_time = datetime.now().isoformat()
                
                if result.get("success", False):
                    step.status = AttackStatus.SUCCESS
                    step.result = result
                else:
                    step.status = AttackStatus.FAILED
                    step.error = result.get("error", "Échec de l'attaque")
                
                results.append({
                    "step": step.name,
                    "status": step.status.value,
                    "duration": self._calculate_duration(step.start_time, step.end_time),
                    "result": step.result,
                    "error": step.error
                })
        
        return results
    
    def _execute_conditional(self, chain: AttackChain, target: str,
                             options: Optional[Dict]) -> List[Dict]:
        """Exécute les étapes avec conditions"""
        results = []
        
        for i, step in enumerate(chain.steps):
            chain.current_step = i
            step.start_time = datetime.now().isoformat()
            
            # Vérifier la condition
            if step.condition and not self._evaluate_condition(step.condition, results):
                step.status = AttackStatus.SKIPPED
                step.end_time = datetime.now().isoformat()
                results.append({
                    "step": step.name,
                    "status": step.status.value,
                    "reason": "Condition non satisfaite"
                })
                continue
            
            step.status = AttackStatus.RUNNING
            time.sleep(self.get_stealth_delay())
            
            result = self._execute_attack(target, step, options)
            
            step.end_time = datetime.now().isoformat()
            
            if result.get("success", False):
                step.status = AttackStatus.SUCCESS
                step.result = result
            else:
                step.status = AttackStatus.FAILED
                step.error = result.get("error", "Échec de l'attaque")
            
            results.append({
                "step": step.name,
                "status": step.status.value,
                "duration": self._calculate_duration(step.start_time, step.end_time),
                "result": step.result,
                "error": step.error
            })
        
        return results
    
    def _execute_adaptive(self, chain: AttackChain, target: str,
                          options: Optional[Dict]) -> List[Dict]:
        """Exécute les étapes de manière adaptative (ajustement dynamique)"""
        results = []
        
        for i, step in enumerate(chain.steps):
            chain.current_step = i
            step.start_time = datetime.now().isoformat()
            step.status = AttackStatus.RUNNING
            
            # Adapter les options en fonction des résultats précédents
            adapted_options = self._adapt_options(step.options, results)
            
            time.sleep(self.get_stealth_delay())
            
            result = self._execute_attack(target, step, adapted_options)
            
            step.end_time = datetime.now().isoformat()
            
            if result.get("success", False):
                step.status = AttackStatus.SUCCESS
                step.result = result
            else:
                step.status = AttackStatus.FAILED
                step.error = result.get("error", "Échec de l'attaque")
            
            results.append({
                "step": step.name,
                "status": step.status.value,
                "duration": self._calculate_duration(step.start_time, step.end_time),
                "result": step.result,
                "error": step.error
            })
        
        return results
    
    def _execute_attack(self, target: str, step: AttackStep,
                        options: Optional[Dict]) -> Dict:
        """
        Exécute une attaque individuelle.
        
        Args:
            target: Cible
            step: Étape à exécuter
            options: Options supplémentaires
            
        Returns:
            Résultat de l'attaque
        """
        # Simulation d'exécution d'attaque
        # Dans une implémentation réelle, cela appellerait les modules d'attaque
        
        import random
        
        # Simuler un délai d'exécution
        exec_time = random.uniform(0.5, 3)
        time.sleep(exec_time)
        
        # Simuler un taux de succès (90% pour les démos)
        success_rate = 0.9
        success = random.random() < success_rate
        
        return {
            "success": success,
            "attack": step.attack_type,
            "category": step.category,
            "target": target,
            "execution_time": round(exec_time, 2),
            "timestamp": datetime.now().isoformat(),
            "stealth_level": self.stealth_level,
            "options_used": step.options,
            "result": f"Attack {step.attack_type} {'succeeded' if success else 'failed'}"
        }
    
    def _check_dependencies(self, step: AttackStep, all_steps: List[AttackStep]) -> bool:
        """Vérifie si les dépendances de l'étape sont satisfaites"""
        if not step.depends_on:
            return True
        
        for dep_id in step.depends_on:
            dep_step = next((s for s in all_steps if s.id == dep_id), None)
            if dep_step and dep_step.status != AttackStatus.SUCCESS:
                return False
        return True
    
    def _evaluate_condition(self, condition: str, results: List[Dict]) -> bool:
        """Évalue une condition basée sur les résultats précédents"""
        # Simplification: dans un vrai système, on évaluerait la condition
        return True
    
    def _adapt_options(self, original_options: Dict, results: List[Dict]) -> Dict:
        """Adapte les options en fonction des résultats précédents"""
        adapted = original_options.copy()
        
        # Adapter le niveau en fonction des succès/échecs
        if results:
            success_count = sum(1 for r in results if r.get("status") == "success")
            if success_count / len(results) < 0.5:
                adapted["level"] = min(adapted.get("level", 2) + 1, 4)
        
        return adapted
    
    def _calculate_duration(self, start_time: Optional[str], end_time: Optional[str]) -> int:
        """Calcule la durée en secondes"""
        if not start_time or not end_time:
            return 0
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            return int((end - start).total_seconds())
        except Exception:
            return 0
    
    def stop_chain(self, chain_id: str) -> Dict[str, Any]:
        """
        Arrête une chaîne en cours d'exécution.
        
        Args:
            chain_id: Identifiant de la chaîne
            
        Returns:
            Résultat de l'arrêt
        """
        if chain_id in self.chains:
            chain = self.chains[chain_id]
            chain.status = "stopped"
            chain.end_time = datetime.now().isoformat()
            
            return {
                "success": True,
                "chain_id": chain_id,
                "message": f"Chaîne {chain.name} arrêtée"
            }
        
        return {
            "success": False,
            "error": f"Chaîne {chain_id} non trouvée"
        }
    
    def delete_chain(self, chain_id: str) -> Dict[str, Any]:
        """
        Supprime une chaîne personnalisée.
        
        Args:
            chain_id: Identifiant de la chaîne
            
        Returns:
            Résultat de la suppression
        """
        if chain_id in self.chains:
            del self.chains[chain_id]
            return {
                "success": True,
                "message": f"Chaîne {chain_id} supprimée"
            }
        return {
            "success": False,
            "error": f"Chaîne {chain_id} non trouvée"
        }
    
    def get_chain_status(self, chain_id: str) -> Optional[Dict]:
        """
        Récupère le statut d'une chaîne.
        
        Args:
            chain_id: Identifiant de la chaîne
            
        Returns:
            Statut de la chaîne
        """
        if chain_id in self.chains:
            chain = self.chains[chain_id]
            return {
                "chain_id": chain.id,
                "chain_name": chain.name,
                "status": chain.status,
                "current_step": chain.current_step,
                "total_steps": len(chain.steps),
                "start_time": chain.start_time,
                "end_time": chain.end_time,
                "error": chain.error
            }
        return None


# Point d'entrée pour les tests
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test du chainer
    chainer = AttackChainer(target="https://example.com", stealth_level="medium")
    
    # Lister les chaînes disponibles
    print("=== Chaînes d'attaques disponibles ===")
    chains = chainer.list_chains()
    print(f"Prédéfinies: {list(chains['predefined'].keys())}")
    print(f"Total: {chains['total']}")
    
    # Exécuter une chaîne
    print("\n=== Exécution de la chaîne full_web_pentest ===")
    result = chainer.run_chain("full_web_pentest")
    print(f"Résultat: {result['status']}")
    print(f"Étapes exécutées: {len(result['steps'])}")
    
    # Créer une chaîne personnalisée
    print("\n=== Création d'une chaîne personnalisée ===")
    custom_steps = [
        {"name": "Scan", "category": "infrastructure", "attack_type": "port_scan"},
        {"name": "Exploit", "category": "exploit", "attack_type": "auto"}
    ]
    chain_id = chainer.create_chain(
        name="Mon Scan Personnalisé",
        description="Scan personnalisé pour test",
        steps=custom_steps,
        mode="sequential"
    )
    print(f"Chaîne créée: {chain_id}")
    
    print("\n✅ Attack Chainer prêt à l'emploi !")