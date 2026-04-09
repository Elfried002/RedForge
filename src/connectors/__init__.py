#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteurs RedForge - Interface unifiée vers les outils externes
Version: 2.0.0 - APT Ready
"""

import time
import json
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, field

from src.connectors.base_connector import BaseConnector
from src.connectors.nmap_connector import NmapConnector
from src.connectors.metasploit_connector import MetasploitConnector
from src.connectors.sqlmap_connector import SQLMapConnector
from src.connectors.xsstrike_connector import XSStrikeConnector
from src.connectors.dalfox_connector import DalfoxConnector
from src.connectors.wafw00f_connector import WafW00fConnector
from src.connectors.ffuf_connector import FfufConnector
from src.connectors.hydra_connector import HydraConnector
from src.connectors.jwt_tool_connector import JWTToolConnector
from src.connectors.zap_connector import ZAPConnector
from src.connectors.whatweb_connector import WhatWebConnector
from src.connectors.dirb_connector import DirbConnector
from src.connectors.custom_script_connector import CustomScriptConnector


class ConnectorType(Enum):
    """Types de connecteurs disponibles"""
    NMAP = "nmap"
    METASPLOIT = "metasploit"
    SQLMAP = "sqlmap"
    XSSTRIKE = "xsstrike"
    DALFOX = "dalfox"
    WAFW00F = "wafw00f"
    FFUF = "ffuf"
    HYDRA = "hydra"
    JWT_TOOL = "jwt_tool"
    ZAP = "zap"
    WHATWEB = "whatweb"
    DIRB = "dirb"
    CUSTOM = "custom"


class StealthLevel(Enum):
    """Niveaux de furtivité pour les connecteurs"""
    LOW = "low"          # Rapide, peu discret
    MEDIUM = "medium"    # Équilibré
    HIGH = "high"        # Très discret, lent
    APT = "apt"          # Ultra discret, style APT


@dataclass
class ConnectorAPTConfig:
    """Configuration APT pour les connecteurs"""
    # Délais entre les connecteurs (secondes)
    delay_between_connectors: tuple = (30, 180)
    # Jitter pour les délais
    jitter: float = 0.3
    # Pauses aléatoires pendant l'exécution
    random_pauses: bool = True
    # Exécution parallèle intelligente
    smart_parallel: bool = False
    # Rotation des User-Agents
    rotate_user_agents: bool = True
    # Proxy rotation
    proxy_rotation: bool = False
    # Logging discret
    stealth_logging: bool = True
    # Timeout global (secondes)
    global_timeout: int = 300
    # Nombre max de connecteurs simultanés
    max_concurrent: int = 3


class ConnectorOrchestrator:
    """
    Orchestrateur central des connecteurs RedForge
    Supporte la sélection multiple, le mode furtif et les opérations APT
    """
    
    def __init__(self, stealth_level: StealthLevel = StealthLevel.MEDIUM):
        """
        Initialise l'orchestrateur de connecteurs
        
        Args:
            stealth_level: Niveau de furtivité global
        """
        self.stealth_level = stealth_level
        self.results = {}
        self.connector_logs = []
        self.active_connectors = {}
        
        # Configuration APT
        self.apt_config = ConnectorAPTConfig()
        
        # Mapping des connecteurs
        self.connectors = {
            ConnectorType.NMAP: NmapConnector(),
            ConnectorType.METASPLOIT: MetasploitConnector(),
            ConnectorType.SQLMAP: SQLMapConnector(),
            ConnectorType.XSSTRIKE: XSStrikeConnector(),
            ConnectorType.DALFOX: DalfoxConnector(),
            ConnectorType.WAFW00F: WafW00fConnector(),
            ConnectorType.FFUF: FfufConnector(),
            ConnectorType.HYDRA: HydraConnector(),
            ConnectorType.JWT_TOOL: JWTToolConnector(),
            ConnectorType.ZAP: ZAPConnector(),
            ConnectorType.WHATWEB: WhatWebConnector(),
            ConnectorType.DIRB: DirbConnector(),
            ConnectorType.CUSTOM: CustomScriptConnector()
        }
        
        # Configurer la furtivité pour chaque connecteur
        self._configure_connectors_stealth()
    
    def _configure_connectors_stealth(self):
        """Configure les paramètres de furtivité pour tous les connecteurs"""
        stealth_config = {
            StealthLevel.LOW: {
                'delay': (0.1, 0.3),
                'threads': 20,
                'timeout': 10,
                'stealth': False
            },
            StealthLevel.MEDIUM: {
                'delay': (0.5, 1.5),
                'threads': 10,
                'timeout': 15,
                'stealth': True
            },
            StealthLevel.HIGH: {
                'delay': (2, 5),
                'threads': 3,
                'timeout': 30,
                'stealth': True
            },
            StealthLevel.APT: {
                'delay': (5, 15),
                'threads': 1,
                'timeout': 60,
                'stealth': True
            }
        }
        
        config = stealth_config[self.stealth_level]
        
        for connector in self.connectors.values():
            if hasattr(connector, 'set_stealth_config'):
                connector.set_stealth_config(config)
    
    def _apply_stealth_delay(self, connector_index: int, total: int):
        """Applique un délai furtif entre les connecteurs"""
        if connector_index >= total - 1:
            return
        
        if self.stealth_level == StealthLevel.APT and self.apt_config.random_pauses:
            import random
            delay = random.uniform(*self.apt_config.delay_between_connectors)
            jitter = delay * self.apt_config.jitter
            delay += random.uniform(-jitter, jitter)
            print(f"💤 Pause APT: {delay:.0f}s")
            time.sleep(max(0, delay))
    
    def run_connector(self, connector_type: ConnectorType, target: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute un connecteur spécifique
        
        Args:
            connector_type: Type de connecteur à exécuter
            target: Cible (URL, IP, etc.)
            **kwargs: Options spécifiques au connecteur
        """
        if connector_type not in self.connectors:
            raise ValueError(f"Connecteur inconnu: {connector_type}")
        
        print(f"\n🔌 Exécution de {connector_type.value.upper()} sur {target}")
        
        # Ajouter la configuration furtive
        kwargs['stealth_level'] = self.stealth_level.value
        kwargs['apt_mode'] = (self.stealth_level == StealthLevel.APT)
        
        start_time = time.time()
        connector = self.connectors[connector_type]
        
        try:
            result = connector.scan(target, **kwargs)
            duration = time.time() - start_time
            
            self.connector_logs.append({
                'timestamp': start_time,
                'connector': connector_type.value,
                'target': target,
                'duration': duration,
                'status': 'success'
            })
            
            self.results[connector_type.value] = result
            return result
            
        except Exception as e:
            self.connector_logs.append({
                'timestamp': start_time,
                'connector': connector_type.value,
                'target': target,
                'error': str(e),
                'status': 'error'
            })
            raise
    
    def run_multiple(self, connectors: List[ConnectorType], target: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute plusieurs connecteurs séquentiellement
        
        Args:
            connectors: Liste des connecteurs à exécuter
            target: Cible
            **kwargs: Options communes
        """
        results = {}
        
        for idx, connector_type in enumerate(connectors):
            print(f"\n{'=' * 50}")
            print(f"🔌 Connecteur {idx+1}/{len(connectors)}: {connector_type.value.upper()}")
            print(f"{'=' * 50}")
            
            try:
                result = self.run_connector(connector_type, target, **kwargs)
                results[connector_type.value] = result
            except Exception as e:
                print(f"❌ Erreur: {e}")
                results[connector_type.value] = {'error': str(e)}
            
            # Délai entre les connecteurs
            self._apply_stealth_delay(idx, len(connectors))
        
        return results
    
    def run_all(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute tous les connecteurs disponibles
        
        Args:
            target: Cible
            **kwargs: Options communes
        """
        all_connectors = list(self.connectors.keys())
        return self.run_multiple(all_connectors, target, **kwargs)
    
    def run_apt_operation(self, target: str, 
                          connectors: Optional[List[ConnectorType]] = None,
                          **kwargs) -> Dict[str, Any]:
        """
        Exécute une opération APT avec orchestration intelligente
        
        Args:
            target: Cible
            connectors: Liste des connecteurs (None = tous)
            **kwargs: Options communes
        """
        print("\n" + "=" * 70)
        print("🎭 DÉBUT DE L'OPÉRATION APT - CONNECTEURS")
        print(f"🎯 Cible: {target}")
        print("=" * 70)
        
        # Configuration APT
        original_stealth = self.stealth_level
        self.stealth_level = StealthLevel.APT
        self._configure_connectors_stealth()
        
        # Ordre APT intelligent (du moins au plus intrusif)
        if connectors is None:
            apt_order = [
                ConnectorType.WHATWEB,      # Reconnaissance passive
                ConnectorType.WAFW00F,      # Détection WAF
                ConnectorType.NMAP,         # Scan ports
                ConnectorType.DIRB,         # Découverte répertoires
                ConnectorType.FFUF,         # Fuzzing
                ConnectorType.XSSTRIKE,     # XSS
                ConnectorType.DALFOX,       # XSS avancé
                ConnectorType.SQLMAP,       # SQL injection
                ConnectorType.HYDRA,        # Bruteforce
                ConnectorType.JWT_TOOL,     # JWT attacks
                ConnectorType.ZAP,          # Scan complet
                ConnectorType.METASPLOIT,   # Exploitation
                ConnectorType.CUSTOM        # Scripts personnalisés
            ]
        else:
            apt_order = connectors
        
        # Journal APT
        apt_log = {
            'operation_start': time.time(),
            'target': target,
            'stealth_level': 'APT',
            'connectors': [c.value for c in apt_order]
        }
        
        # Exécuter les connecteurs
        results = self.run_multiple(apt_order, target, **kwargs)
        
        # Ajouter les métadonnées APT
        results['apt_metadata'] = {
            'operation_duration': time.time() - apt_log['operation_start'],
            'total_connectors': len(apt_order),
            'successful_connectors': sum(1 for r in results.values() if 'error' not in r),
            'stealth_level': 'APT'
        }
        
        # Restaurer le niveau de furtivité original
        self.stealth_level = original_stealth
        self._configure_connectors_stealth()
        
        print("\n🎭 OPÉRATION APT TERMINÉE")
        self._print_apt_summary(results['apt_metadata'])
        
        return results
    
    def _print_apt_summary(self, apt_metadata: Dict):
        """Affiche le résumé de l'opération APT"""
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ DE L'OPÉRATION APT - CONNECTEURS")
        print("=" * 70)
        print(f"⏱️  Durée totale: {apt_metadata['operation_duration']:.1f}s")
        print(f"🔌 Connecteurs exécutés: {apt_metadata['total_connectors']}")
        print(f"✅ Connecteurs réussis: {apt_metadata['successful_connectors']}")
        print(f"🕵️ Niveau furtif: {apt_metadata['stealth_level']}")
    
    def get_connector_status(self, connector_type: Optional[ConnectorType] = None) -> Dict:
        """
        Vérifie le statut d'un ou plusieurs connecteurs
        
        Args:
            connector_type: Type de connecteur (None = tous)
        """
        if connector_type:
            connector = self.connectors.get(connector_type)
            if connector and hasattr(connector, 'check_availability'):
                return {connector_type.value: connector.check_availability()}
            return {connector_type.value: {'available': False, 'error': 'Not implemented'}}
        
        status = {}
        for ctype, connector in self.connectors.items():
            if hasattr(connector, 'check_availability'):
                status[ctype.value] = connector.check_availability()
            else:
                status[ctype.value] = {'available': True, 'info': 'Status check not available'}
        
        return status
    
    def save_results(self, output_file: str, include_logs: bool = False):
        """
        Sauvegarde les résultats au format JSON
        
        Args:
            output_file: Fichier de sortie
            include_logs: Inclure les logs
        """
        output_data = {
            'timestamp': time.time(),
            'stealth_level': self.stealth_level.value,
            'results': self.results
        }
        
        if include_logs:
            output_data['logs'] = self.connector_logs
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        
        print(f"\n💾 Résultats sauvegardés dans {output_file}")


# Fonctions utilitaires
def create_apt_connector_session(stealth_level: StealthLevel = StealthLevel.APT) -> ConnectorOrchestrator:
    """Crée une session APT pour les connecteurs"""
    return ConnectorOrchestrator(stealth_level=stealth_level)


def quick_connector_run(target: str, connector_type: ConnectorType, **kwargs) -> Dict:
    """Exécution rapide d'un connecteur"""
    orchestrator = ConnectorOrchestrator(stealth_level=StealthLevel.LOW)
    return orchestrator.run_connector(connector_type, target, **kwargs)


# Exports
__all__ = [
    'ConnectorOrchestrator',
    'ConnectorType',
    'StealthLevel',
    'ConnectorAPTConfig',
    'BaseConnector',
    'NmapConnector',
    'MetasploitConnector',
    'SQLMapConnector',
    'XSStrikeConnector',
    'DalfoxConnector',
    'WafW00fConnector',
    'FfufConnector',
    'HydraConnector',
    'JWTToolConnector',
    'ZAPConnector',
    'WhatWebConnector',
    'DirbConnector',
    'CustomScriptConnector',
    'create_apt_connector_session',
    'quick_connector_run'
]


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("RedForge - Connecteurs")
    print("=" * 60)
    
    # Créer l'orchestrateur
    orchestrator = ConnectorOrchestrator(stealth_level=StealthLevel.MEDIUM)
    
    # Afficher les connecteurs disponibles
    print("\n🔌 Connecteurs disponibles:")
    for connector in ConnectorType:
        print(f"  - {connector.value}")
    
    print("\n🎭 Modes de furtivité disponibles:")
    for mode in StealthLevel:
        print(f"  - {mode.value}")
    
    # Vérifier le statut des connecteurs
    print("\n📊 Statut des connecteurs:")
    status = orchestrator.get_connector_status()
    for name, info in status.items():
        available = "✅" if info.get('available') else "❌"
        print(f"  {available} {name}")
    
    print("\n✅ Module connecteurs chargé avec succès")
    print("\n💡 Exemples d'utilisation:")
    print("  orchestrator = create_apt_connector_session()")
    print("  results = orchestrator.run_apt_operation('https://cible.com')")
    print("  nmap_result = orchestrator.run_connector(ConnectorType.NMAP, '192.168.1.1')")