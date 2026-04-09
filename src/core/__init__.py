#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module core de RedForge
Contient les composants principaux de l'application
Version APT avec support furtif et orchestration avancée
"""

from typing import Dict, Any, List, Optional, Union
from enum import Enum

# Composants principaux
from src.core.cli import RedForgeCLI
from src.core.gui import RedForgeGUI
from src.core.orchestrator import RedForgeOrchestrator
from src.core.attack_chainer import AttackChainer
from src.core.session_manager import SessionManager
from src.core.config import RedForgeConfig

# Nouvelles fonctionnalités APT
from src.core.stealth_engine import StealthEngine
from src.core.apt_controller import APTController
from src.core.report_generator import ReportGenerator
from src.core.cache_manager import CacheManager
from src.core.metrics_collector import MetricsCollector
from src.core.attack_scheduler import AttackScheduler
from src.core.loot_manager import LootManager


class RedForgeMode(Enum):
    """Modes d'exécution de RedForge"""
    STANDARD = "standard"      # Mode standard
    STEALTH = "stealth"        # Mode furtif
    APT = "apt"                # Mode APT (Advanced Persistent Threat)
    TRAINING = "training"      # Mode formation
    DEMO = "demo"              # Mode démonstration


class RedForge:
    """
    Point d'entrée principal de RedForge
    Interface unifiée pour toutes les fonctionnalités
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialise l'instance principale de RedForge"""
        if self._initialized:
            return
        
        self.mode = RedForgeMode.STANDARD
        self.orchestrator = None
        self.stealth_engine = None
        self.apt_controller = None
        self.report_generator = None
        self.cache_manager = None
        self.metrics_collector = None
        self.scheduler = None
        self.loot_manager = None
        
        self._initialized = True
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialise tous les composants RedForge"""
        self.orchestrator = RedForgeOrchestrator()
        self.stealth_engine = StealthEngine()
        self.apt_controller = APTController()
        self.report_generator = ReportGenerator()
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.scheduler = AttackScheduler()
        self.loot_manager = LootManager()
    
    def set_mode(self, mode: RedForgeMode):
        """
        Définit le mode d'exécution
        
        Args:
            mode: Mode d'exécution
        """
        self.mode = mode
        
        if mode == RedForgeMode.APT:
            self.stealth_engine.enable_apt_mode()
            self.apt_controller.activate()
            self.scheduler.enable_apt_scheduling()
        
        elif mode == RedForgeMode.STEALTH:
            self.stealth_engine.enable()
            self.apt_controller.deactivate()
        
        else:
            self.stealth_engine.disable()
            self.apt_controller.deactivate()
    
    def run(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Lance l'exécution principale
        
        Args:
            target: Cible à attaquer
            **kwargs: Options de configuration
            
        Returns:
            Résultats de l'exécution
        """
        return self.orchestrator.execute(target, mode=self.mode, **kwargs)
    
    def plan_apt_operation(self, target: str, duration: int = 86400, **kwargs) -> Dict[str, Any]:
        """
        Planifie une opération APT complète
        
        Args:
            target: Cible
            duration: Durée de l'opération en secondes
            **kwargs: Options supplémentaires
            
        Returns:
            Plan de l'opération APT
        """
        self.set_mode(RedForgeMode.APT)
        return self.apt_controller.plan_operation(target, duration, **kwargs)
    
    def generate_report(self, format: str = "html", **kwargs) -> str:
        """
        Génère un rapport des résultats
        
        Args:
            format: Format du rapport (html, json, pdf, txt)
            **kwargs: Options supplémentaires
            
        Returns:
            Rapport généré
        """
        return self.report_generator.generate(
            self.orchestrator.results,
            format=format,
            **kwargs
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Récupère les métriques d'exécution
        
        Returns:
            Métriques collectées
        """
        return self.metrics_collector.get_metrics()
    
    def schedule_attack(self, target: str, schedule: str, **kwargs) -> str:
        """
        Planifie une attaque
        
        Args:
            target: Cible
            schedule: Expression cron ou intervalle
            **kwargs: Options d'attaque
            
        Returns:
            ID de la tâche planifiée
        """
        return self.scheduler.schedule(target, schedule, **kwargs)
    
    def list_scheduled_attacks(self) -> List[Dict[str, Any]]:
        """
        Liste les attaques planifiées
        
        Returns:
            Liste des attaques planifiées
        """
        return self.scheduler.list_jobs()
    
    def cancel_scheduled_attack(self, job_id: str) -> bool:
        """
        Annule une attaque planifiée
        
        Args:
            job_id: ID de la tâche
            
        Returns:
            True si annulée
        """
        return self.scheduler.cancel(job_id)
    
    def get_loot(self) -> Dict[str, Any]:
        """
        Récupère les données exfiltrées
        
        Returns:
            Données collectées
        """
        return self.loot_manager.get_all()
    
    def clear_loot(self):
        """Efface toutes les données collectées"""
        self.loot_manager.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du cache
        
        Returns:
            Statistiques du cache
        """
        return self.cache_manager.get_stats()
    
    def clear_cache(self):
        """Efface le cache"""
        self.cache_manager.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Récupère le statut global de RedForge
        
        Returns:
            Statut global
        """
        return {
            "mode": self.mode.value,
            "orchestrator": self.orchestrator.get_status(),
            "stealth_engine": self.stealth_engine.get_status(),
            "apt_controller": self.apt_controller.get_status(),
            "scheduler": self.scheduler.get_status(),
            "metrics": self.metrics_collector.get_summary(),
            "cache_stats": self.cache_manager.get_stats(),
            "loot_count": len(self.loot_manager.get_all())
        }
    
    def shutdown(self):
        """Arrête proprement RedForge"""
        self.scheduler.shutdown()
        self.apt_controller.shutdown()
        self.metrics_collector.finalize()
        self.cache_manager.persist()


# Instance globale pour un accès facile
redforge = RedForge()


# Fonctions de commodité
def run(target: str, **kwargs) -> Dict[str, Any]:
    """Point d'entrée rapide"""
    return redforge.run(target, **kwargs)


def apt(target: str, duration: int = 86400, **kwargs) -> Dict[str, Any]:
    """Lance une opération APT"""
    return redforge.plan_apt_operation(target, duration, **kwargs)


def schedule(target: str, schedule: str, **kwargs) -> str:
    """Planifie une attaque"""
    return redforge.schedule_attack(target, schedule, **kwargs)


def report(format: str = "html", **kwargs) -> str:
    """Génère un rapport"""
    return redforge.generate_report(format, **kwargs)


def status() -> Dict[str, Any]:
    """Récupère le statut"""
    return redforge.get_status()


# Exportations principales
__all__ = [
    # Classes principales
    'RedForge',
    'RedForgeCLI',
    'RedForgeGUI',
    'RedForgeOrchestrator',
    'AttackChainer',
    'SessionManager',
    'RedForgeConfig',
    'RedForgeMode',
    
    # Nouvelles fonctionnalités APT
    'StealthEngine',
    'APTController',
    'ReportGenerator',
    'CacheManager',
    'MetricsCollector',
    'AttackScheduler',
    'LootManager',
    
    # Instance globale
    'redforge',
    
    # Fonctions de commodité
    'run',
    'apt',
    'schedule',
    'report',
    'status'
]


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("RedForge - Framework de Tests d'Intrusion APT")
    print("Version 2.0 - APT Ready")
    print("=" * 60)
    
    # Créer l'instance
    rf = RedForge()
    
    # Afficher les modes disponibles
    print("\n🎭 Modes disponibles:")
    for mode in RedForgeMode:
        print(f"  - {mode.value}")
    
    # Afficher l'état
    status = rf.get_status()
    print(f"\n📊 Statut: Mode {status['mode']}")
    
    print("\n✅ RedForge chargé avec succès")
    print("\n💡 Exemples d'utilisation:")
    print("  redforge.run('https://cible.com')")
    print("  redforge.apt('https://cible.com', duration=3600)")
    print("  redforge.schedule('https://cible.com', '0 2 * * *')")
    print("  redforge.generate_report('html')")