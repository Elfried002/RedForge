#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedForge - Plateforme d'Orchestration de Pentest Web pour Red Team
Version: 1.0.0
"""

__version__ = '1.0.0'
__author__ = 'RedForge Team'
__license__ = 'GPLv3'

# Import des modules principaux
from src.core import (
    RedForgeOrchestrator,
    AttackChainer,
    SessionManager,
    RedForgeCLI,
    RedForgeConfig
)

from src.attacks import (
    AttackOrchestrator,
    # Injection
    SQLInjection,
    NoSQLInjection,
    CommandInjection,
    LDAPInjection,
    XPathInjection,
    HTMLInjection,
    TemplateInjection,
    # Session
    SessionHijacking,
    SessionFixation,
    CookieManipulation,
    JWTAattacks,
    OAuthAttacks,
    # Cross-Site
    XSSEngine,
    CSRFGenerator,
    ClickjackingDetector,
    CORMisconfigurationDetector,
    PostMessageAttacks,
    # Authentication
    BruteForce,
    CredentialStuffing,
    PasswordSpraying,
    MFABypass,
    PrivilegeEscalation,
    RaceCondition,
    # File System
    LFIRFIAttack,
    FileUploadAttack,
    DirectoryTraversal,
    BufferOverflow,
    PathNormalization,
    ZipSlipAttack,
    # Infrastructure
    WAFBypass,
    MisconfigDetector,
    LoadBalancerAttack,
    HostHeaderInjection,
    CachePoisoning,
    # Integrity
    DataTampering,
    InfoLeakage,
    MITMAttacks,
    ParameterPollution,
    BusinessLogicFlaws,
    # Advanced
    APIAttacks,
    GraphQLAttacks,
    WebSocketAttacks,
    DeserializationAttack,
    BrowserExploit,
    MicroservicesAttack,
    AttackChaining
)

from src.connectors import (
    BaseConnector,
    NmapConnector,
    MetasploitConnector,
    SQLMapConnector,
    XSStrikeConnector,
    DalfoxConnector,
    WafW00fConnector,
    FfufConnector,
    HydraConnector,
    JWTToolConnector,
    ZAPConnector,
    WhatWebConnector,
    DirbConnector,
    CustomScriptConnector
)

from src.phases import (
    FootprintPhase,
    AnalysisPhase,
    ScanningPhase,
    ExploitationPhase
)

from src.web_interface import create_app


def get_version():
    """Retourne la version de RedForge"""
    return __version__


def get_info():
    """Retourne les informations sur RedForge"""
    return {
        'name': 'RedForge',
        'version': __version__,
        'description': 'Plateforme d\'Orchestration de Pentest Web pour Red Team',
        'author': __author__,
        'license': __license__
    }


# Export de tout
__all__ = [
    # Version
    'get_version',
    'get_info',
    
    # Core
    'RedForgeOrchestrator',
    'AttackChainer',
    'SessionManager',
    'RedForgeCLI',
    'RedForgeConfig',
    
    # Attacks
    'AttackOrchestrator',
    # Injection
    'SQLInjection',
    'NoSQLInjection',
    'CommandInjection',
    'LDAPInjection',
    'XPathInjection',
    'HTMLInjection',
    'TemplateInjection',
    # Session
    'SessionHijacking',
    'SessionFixation',
    'CookieManipulation',
    'JWTAattacks',
    'OAuthAttacks',
    # Cross-Site
    'XSSEngine',
    'CSRFGenerator',
    'ClickjackingDetector',
    'CORMisconfigurationDetector',
    'PostMessageAttacks',
    # Authentication
    'BruteForce',
    'CredentialStuffing',
    'PasswordSpraying',
    'MFABypass',
    'PrivilegeEscalation',
    'RaceCondition',
    # File System
    'LFIRFIAttack',
    'FileUploadAttack',
    'DirectoryTraversal',
    'BufferOverflow',
    'PathNormalization',
    'ZipSlipAttack',
    # Infrastructure
    'WAFBypass',
    'MisconfigDetector',
    'LoadBalancerAttack',
    'HostHeaderInjection',
    'CachePoisoning',
    # Integrity
    'DataTampering',
    'InfoLeakage',
    'MITMAttacks',
    'ParameterPollution',
    'BusinessLogicFlaws',
    # Advanced
    'APIAttacks',
    'GraphQLAttacks',
    'WebSocketAttacks',
    'DeserializationAttack',
    'BrowserExploit',
    'MicroservicesAttack',
    'AttackChaining',
    
    # Connectors
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
    
    # Phases
    'FootprintPhase',
    'AnalysisPhase',
    'ScanningPhase',
    'ExploitationPhase',
    
    # Web Interface
    'create_app'
]


# Point d'entrée pour les tests
if __name__ == "__main__":
    print("=" * 60)
    print("RedForge - Plateforme d'Orchestration de Pentest Web")
    print(f"Version: {__version__}")
    print(f"Licence: {__license__}")
    print("=" * 60)
    
    print("\n📦 Modules disponibles:")
    print("  - Core: Orchestrator, AttackChainer, SessionManager")
    print("  - Attacks: 8 catégories d'attaques")
    print("  - Connectors: 15 connecteurs d'outils")
    print("  - Phases: 4 phases méthodologiques")
    print("  - Web Interface: Interface graphique Flask")
    
    print("\n🚀 Pour lancer l'interface web:")
    print("  from src.web_interface import create_app")
    print("  app = create_app()")
    print("  app.run()")
    
    print("\n✅ RedForge chargé avec succès")