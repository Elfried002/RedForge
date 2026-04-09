#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phases méthodologiques de RedForge
Définit les 4 phases principales du pentest web
Version avec support furtif, APT et orchestration avancée
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import time

from src.phases.footprint import FootprintPhase
from src.phases.analysis import AnalysisPhase
from src.phases.scanning import ScanningPhase
from src.phases.exploitation import ExploitationPhase
from src.core.stealth_engine import StealthEngine


class PhaseType(Enum):
    """Types de phases disponibles"""
    FOOTPRINT = "footprint"
    ANALYSIS = "analysis"
    SCANNING = "scanning"
    EXPLOITATION = "exploitation"


class PhaseStatus(Enum):
    """Statuts possibles d'une phase"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PhaseOrchestrator:
    """
    Orchestrateur des phases méthodologiques
    Gère l'exécution séquentielle ou sélective des phases
    Supporte le mode furtif et APT
    """
    
    def __init__(self, target: str):
        """
        Initialise l'orchestrateur de phases
        
        Args:
            target: Cible des attaques
        """
        self.target = target
        self.phases = {}
        self.results = {}
        self.status = {}
        self.start_time = None
        self.stealth_mode = False
        self.apt_mode = False
        self.stealth_config = {}
        self.stealth_engine = StealthEngine()
        
        # Initialiser les phases
        self._init_phases()
    
    def _init_phases(self):
        """Initialise toutes les phases avec la cible"""
        self.phases = {
            PhaseType.FOOTPRINT: FootprintPhase(self.target),
            PhaseType.ANALYSIS: AnalysisPhase(self.target),
            PhaseType.SCANNING: ScanningPhase(self.target),
            PhaseType.EXPLOITATION: ExploitationPhase(self.target)
        }
        
        # Initialiser les statuts
        for phase in PhaseType:
            self.status[phase] = PhaseStatus.PENDING
    
    def set_stealth_config(self, config: Dict[str, Any]):
        """
        Configure le mode furtif pour toutes les phases
        
        Args:
            config: Configuration de furtivité
        """
        self.stealth_mode = config.get('enabled', False)
        self.apt_mode = config.get('apt_mode', False)
        self.stealth_config = config
        
        # Configurer le moteur de furtivité
        if self.stealth_mode:
            self.stealth_engine.set_delays(
                min_delay=config.get('delay_min', 1),
                max_delay=config.get('delay_max', 5),
                jitter=config.get('jitter', 0.3)
            )
            if self.apt_mode:
                self.stealth_engine.enable_apt_mode()
        
        # Propager la configuration à toutes les phases
        for phase in self.phases.values():
            if hasattr(phase, 'set_stealth_config'):
                phase.set_stealth_config(config)
    
    def _apply_stealth_delay(self):
        """Applique un délai furtif entre les phases"""
        if self.stealth_mode:
            self.stealth_engine.apply_delay()
    
    def run_phase(self, phase_type: PhaseType, **kwargs) -> Dict[str, Any]:
        """
        Exécute une phase spécifique
        
        Args:
            phase_type: Type de phase à exécuter
            **kwargs: Options pour la phase
            
        Returns:
            Résultats de la phase
        """
        if phase_type not in self.phases:
            raise ValueError(f"Phase inconnue: {phase_type}")
        
        phase = self.phases[phase_type]
        self.status[phase_type] = PhaseStatus.RUNNING
        
        print(f"\n{'=' * 60}")
        print(f"🎯 Exécution de la phase: {phase_type.value.upper()}")
        print(f"{'=' * 60}")
        
        try:
            start_time = time.time()
            result = phase.run(**kwargs)
            duration = time.time() - start_time
            
            self.status[phase_type] = PhaseStatus.COMPLETED
            self.results[phase_type.value] = {
                "result": result,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            
            print(f"\n✅ Phase {phase_type.value} terminée en {duration:.1f}s")
            return result
            
        except Exception as e:
            self.status[phase_type] = PhaseStatus.FAILED
            self.results[phase_type.value] = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            }
            print(f"\n❌ Phase {phase_type.value} échouée: {e}")
            raise
    
    def run_sequence(self, phases: List[PhaseType], **kwargs) -> Dict[str, Any]:
        """
        Exécute une séquence de phases dans l'ordre donné
        
        Args:
            phases: Liste des phases à exécuter
            **kwargs: Options pour les phases
            
        Returns:
            Résultats de toutes les phases
        """
        results = {}
        
        for idx, phase_type in enumerate(phases):
            if idx > 0:
                self._apply_stealth_delay()
            
            result = self.run_phase(phase_type, **kwargs)
            results[phase_type.value] = result
        
        return results
    
    def run_full_methodology(self, **kwargs) -> Dict[str, Any]:
        """
        Exécute la méthodologie complète dans l'ordre recommandé
        
        Args:
            **kwargs: Options pour les phases
            
        Returns:
            Résultats de toutes les phases
        """
        print(f"\n{'=' * 70}")
        print(f"🚀 MÉTHODOLOGIE COMPLÈTE - Cible: {self.target}")
        if self.apt_mode:
            print(f"🎭 Mode APT activé - Opération ultra discrète")
        elif self.stealth_mode:
            print(f"🕵️ Mode furtif activé")
        print(f"{'=' * 70}")
        
        self.start_time = time.time()
        
        # Ordre méthodologique standard
        methodology_order = [
            PhaseType.FOOTPRINT,
            PhaseType.ANALYSIS,
            PhaseType.SCANNING,
            PhaseType.EXPLOITATION
        ]
        
        results = self.run_sequence(methodology_order, **kwargs)
        
        duration = time.time() - self.start_time
        print(f"\n{'=' * 70}")
        print(f"✅ MÉTHODOLOGIE COMPLÈTE TERMINÉE en {duration:.1f}s")
        print(f"{'=' * 70}")
        
        # Afficher le résumé global
        self._print_global_summary()
        
        return results
    
    def run_apt_operation(self, **kwargs) -> Dict[str, Any]:
        """
        Exécute une opération APT complète avec pauses et discrétion
        
        Args:
            **kwargs: Options pour les phases
            
        Returns:
            Résultats de l'opération APT
        """
        # Forcer le mode APT
        original_apt = self.apt_mode
        self.apt_mode = True
        self.set_stealth_config({
            'enabled': True,
            'apt_mode': True,
            'delay_min': kwargs.get('delay_min', 5),
            'delay_max': kwargs.get('delay_max', 15),
            'jitter': 0.3
        })
        
        print(f"\n{'=' * 70}")
        print(f"🎭 OPÉRATION APT - Cible: {self.target}")
        print(f"⏱️  Durée estimée: Opération prolongée")
        print(f"{'=' * 70}")
        
        # Ordre APT (peut être différent selon le contexte)
        apt_order = [
            PhaseType.FOOTPRINT,
            PhaseType.ANALYSIS,
            PhaseType.SCANNING,
            PhaseType.EXPLOITATION
        ]
        
        # Exécuter avec pauses prolongées
        results = {}
        for idx, phase_type in enumerate(apt_order):
            if idx > 0:
                # Pause APT plus longue
                pause = kwargs.get('phase_pause', 60)
                print(f"\n💤 Pause APT: {pause}s avant la phase suivante")
                time.sleep(pause)
            
            result = self.run_phase(phase_type, **kwargs)
            results[phase_type.value] = result
        
        # Restaurer le mode original
        self.apt_mode = original_apt
        self.set_stealth_config(self.stealth_config)
        
        print(f"\n{'=' * 70}")
        print(f"🎭 OPÉRATION APT TERMINÉE")
        print(f"{'=' * 70}")
        
        return results
    
    def run_selected(self, phases: List[str], **kwargs) -> Dict[str, Any]:
        """
        Exécute des phases sélectionnées par leur nom
        
        Args:
            phases: Liste des noms de phases ('footprint', 'analysis', etc.)
            **kwargs: Options pour les phases
            
        Returns:
            Résultats des phases sélectionnées
        """
        phase_map = {
            'footprint': PhaseType.FOOTPRINT,
            'analysis': PhaseType.ANALYSIS,
            'scanning': PhaseType.SCANNING,
            'exploitation': PhaseType.EXPLOITATION,
            'exploit': PhaseType.EXPLOITATION
        }
        
        selected_phases = []
        for phase_name in phases:
            if phase_name in phase_map:
                selected_phases.append(phase_map[phase_name])
            else:
                print(f"⚠️ Phase ignorée: {phase_name} (non reconnue)")
        
        if not selected_phases:
            print("❌ Aucune phase valide sélectionnée")
            return {}
        
        return self.run_sequence(selected_phases, **kwargs)
    
    def get_phase_result(self, phase_type: PhaseType) -> Optional[Dict]:
        """Récupère le résultat d'une phase spécifique"""
        return self.results.get(phase_type.value)
    
    def get_phase_status(self, phase_type: PhaseType) -> PhaseStatus:
        """Récupère le statut d'une phase"""
        return self.status.get(phase_type, PhaseStatus.PENDING)
    
    def get_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de toutes les phases"""
        summary = {
            "target": self.target,
            "start_time": self.start_time,
            "duration": time.time() - self.start_time if self.start_time else 0,
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "phases": {}
        }
        
        for phase_type, status in self.status.items():
            phase_result = self.results.get(phase_type.value, {})
            summary["phases"][phase_type.value] = {
                "status": status.value,
                "duration": phase_result.get('duration', 0),
                "timestamp": phase_result.get('timestamp'),
                "has_results": 'result' in phase_result
            }
        
        return summary
    
    def _print_global_summary(self):
        """Affiche un résumé global de toutes les phases"""
        print("\n📊 RÉSUMÉ GLOBAL DES PHASES")
        print("=" * 60)
        
        for phase_type, status in self.status.items():
            phase_result = self.results.get(phase_type.value, {})
            status_icon = "✅" if status == PhaseStatus.COMPLETED else "❌" if status == PhaseStatus.FAILED else "⏳"
            duration = phase_result.get('duration', 0)
            print(f"  {status_icon} {phase_type.value.upper()}: {status.value} ({duration:.1f}s)")
        
        # Compter les vulnérabilités totales
        total_vulns = 0
        for phase_result in self.results.values():
            result = phase_result.get('result', {})
            if isinstance(result, dict):
                total_vulns += len(result.get('vulnerabilities', []))
        
        if total_vulns > 0:
            print(f"\n⚠️ TOTAL: {total_vulns} vulnérabilité(s) détectée(s)")
        else:
            print("\n✅ Aucune vulnérabilité détectée")
    
    def save_results(self, output_file: str) -> bool:
        """
        Sauvegarde tous les résultats au format JSON
        
        Args:
            output_file: Chemin du fichier de sortie
            
        Returns:
            True si sauvegarde réussie
        """
        import json
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "target": self.target,
                    "timestamp": datetime.now().isoformat(),
                    "stealth_mode": self.stealth_mode,
                    "apt_mode": self.apt_mode,
                    "results": self.results,
                    "summary": self.get_summary()
                }, f, indent=4, ensure_ascii=False)
            print(f"\n💾 Résultats sauvegardés dans {output_file}")
            return True
        except Exception as e:
            print(f"\n❌ Erreur sauvegarde: {e}")
            return False


# Fonctions de commodité
def run_full_assessment(target: str, stealth: bool = False, apt: bool = False, **kwargs) -> Dict[str, Any]:
    """
    Lance une évaluation complète de la cible
    
    Args:
        target: Cible à analyser
        stealth: Mode furtif
        apt: Mode APT
        **kwargs: Options supplémentaires
        
    Returns:
        Résultats complets
    """
    orchestrator = PhaseOrchestrator(target)
    
    stealth_config = {
        'enabled': stealth or apt,
        'apt_mode': apt,
        'delay_min': kwargs.get('delay_min', 2 if stealth else 1),
        'delay_max': kwargs.get('delay_max', 5 if stealth else 2)
    }
    
    orchestrator.set_stealth_config(stealth_config)
    
    if apt:
        return orchestrator.run_apt_operation(**kwargs)
    else:
        return orchestrator.run_full_methodology(**kwargs)


def quick_assessment(target: str, **kwargs) -> Dict[str, Any]:
    """Évaluation rapide (footprint + scan)"""
    orchestrator = PhaseOrchestrator(target)
    return orchestrator.run_selected(['footprint', 'scanning'], **kwargs)


def deep_assessment(target: str, **kwargs) -> Dict[str, Any]:
    """Évaluation approfondie (toutes les phases)"""
    return run_full_assessment(target, stealth=False, apt=False, **kwargs)


def stealth_assessment(target: str, **kwargs) -> Dict[str, Any]:
    """Évaluation discrète (mode furtif)"""
    return run_full_assessment(target, stealth=True, apt=False, **kwargs)


def apt_assessment(target: str, **kwargs) -> Dict[str, Any]:
    """Évaluation APT (ultra discret)"""
    return run_full_assessment(target, stealth=True, apt=True, **kwargs)


# Export des classes principales
__all__ = [
    'PhaseOrchestrator',
    'PhaseType',
    'PhaseStatus',
    'FootprintPhase',
    'AnalysisPhase',
    'ScanningPhase',
    'ExploitationPhase',
    'run_full_assessment',
    'quick_assessment',
    'deep_assessment',
    'stealth_assessment',
    'apt_assessment'
]


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de l'orchestrateur de phases")
    print("=" * 60)
    
    # Créer l'orchestrateur
    orchestrator = PhaseOrchestrator("https://example.com")
    
    # Configurer le mode APT
    orchestrator.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    print("\n✅ Module Phases chargé avec succès")
    print("\n📋 Phases disponibles:")
    for phase in PhaseType:
        print(f"   - {phase.value}")
    
    print("\n💡 Exemples d'utilisation:")
    print("   orchestrator.run_full_methodology()")
    print("   orchestrator.run_phase(PhaseType.FOOTPRINT)")
    print("   orchestrator.run_selected(['footprint', 'scanning'])")
    print("   apt_assessment('target.com')")