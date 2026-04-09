#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques de RedForge
Centralise tous les types d'attaques disponibles dans la plateforme
Version APT avec mode furtif et orchestration avancée
"""

import time
import json
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, field

# Injection Attacks
from src.attacks.injection import (
    InjectionAttackManager,
    InjectionAttackType,
    StealthLevel as InjectionStealthLevel,
    SQLInjection,
    NoSQLInjection,
    CommandInjection,
    LDAPInjection,
    XPathInjection,
    HTMLInjection,
    TemplateInjection
)

# Session Attacks
from src.attacks.session import (
    SessionAttackManager,
    SessionAttackType,
    StealthLevel as SessionStealthLevel,
    SessionHijacking,
    SessionFixation,
    CookieManipulation,
    JWTAattacks,
    OAuthAttacks
)

# Cross-Site Attacks
from src.attacks.cross_site import (
    CrossSiteAttackManager,
    CrossSiteAttackType,
    StealthLevel as CrossSiteStealthLevel,
    XSSEngine,
    CSRFGenerator,
    ClickjackingDetector,
    CORMisconfigurationDetector,
    PostMessageAttacks
)

# Authentication Attacks
from src.attacks.authentication import (
    AuthenticationAttackManager,
    AttackType as AuthAttackType,
    StealthLevel as AuthStealthLevel,
    BruteForce,
    CredentialStuffing,
    PasswordSpraying,
    MFABypass,
    PrivilegeEscalation,
    RaceCondition
)

# File System Attacks
from src.attacks.file_system import (
    FileSystemAttackManager,
    FileSystemAttackType,
    StealthLevel as FSStealthLevel,
    LFIRFIAttack,
    FileUploadAttack,
    DirectoryTraversal,
    BufferOverflow,
    PathNormalization,
    ZipSlipAttack
)

# Infrastructure Attacks
from src.attacks.infrastructure import (
    InfrastructureAttackManager,
    InfrastructureAttackType,
    StealthLevel as InfraStealthLevel,
    WAFBypass,
    MisconfigDetector,
    LoadBalancerAttack,
    HostHeaderInjection,
    CachePoisoning
)

# Integrity Attacks
from src.attacks.integrity import (
    IntegrityAttackManager,
    IntegrityAttackType,
    StealthLevel as IntegrityStealthLevel,
    DataTampering,
    InfoLeakage,
    MITMAttacks,
    ParameterPollution,
    BusinessLogicFlaws
)

# Advanced Attacks
from src.attacks.advanced import (
    AdvancedAttackManager,
    AdvancedAttackType,
    StealthLevel as AdvancedStealthLevel,
    APIAttacks,
    GraphQLAttacks,
    WebSocketAttacks,
    DeserializationAttack,
    BrowserExploit,
    MicroservicesAttack,
    AttackChaining
)


class GlobalStealthLevel(Enum):
    """Niveaux de furtivité globaux"""
    LOW = "low"          # Rapide, peu discret
    MEDIUM = "medium"    # Équilibré
    HIGH = "high"        # Très discret, lent
    APT = "apt"          # Ultra discret, style APT


@dataclass
class GlobalAPTConfig:
    """Configuration globale pour les opérations APT"""
    # Délais entre les catégories d'attaques (secondes)
    delay_between_categories: tuple = (60, 300)
    # Jitter pour les délais
    jitter: float = 0.3
    # Pauses aléatoires pendant les scans
    random_pauses: bool = True
    # Ordre d'attaque intelligent (du moins au plus intrusif)
    intelligent_ordering: bool = True
    # Mode parallèle intelligent (limité pour APT)
    smart_parallel: bool = False
    # Rotation des signatures
    signature_rotation: bool = True
    # Logging discret
    stealth_logging: bool = True
    # Rapport APT (détaillé mais discret)
    apt_reporting: bool = True


class AttackOrchestrator:
    """
    Orchestrateur central de toutes les attaques RedForge
    Supporte le mode furtif, les opérations APT et l'orchestration avancée
    """
    
    def __init__(self, target: str, stealth_level: GlobalStealthLevel = GlobalStealthLevel.LOW):
        """
        Initialise l'orchestrateur d'attaques
        
        Args:
            target: Cible des attaques (URL, IP, etc.)
            stealth_level: Niveau de furtivité global
        """
        self.target = target
        self.stealth_level = stealth_level
        self.results = {}
        self.attack_logs = []
        self.start_time = None
        
        # Mapping des niveaux de furtivité par catégorie
        stealth_mapping = {
            GlobalStealthLevel.LOW: {
                'injection': InjectionStealthLevel.LOW,
                'session': SessionStealthLevel.LOW,
                'cross_site': CrossSiteStealthLevel.LOW,
                'authentication': AuthStealthLevel.LOW,
                'file_system': FSStealthLevel.LOW,
                'infrastructure': InfraStealthLevel.LOW,
                'integrity': IntegrityStealthLevel.LOW,
                'advanced': AdvancedStealthLevel.LOW
            },
            GlobalStealthLevel.MEDIUM: {
                'injection': InjectionStealthLevel.MEDIUM,
                'session': SessionStealthLevel.MEDIUM,
                'cross_site': CrossSiteStealthLevel.MEDIUM,
                'authentication': AuthStealthLevel.MEDIUM,
                'file_system': FSStealthLevel.MEDIUM,
                'infrastructure': InfraStealthLevel.MEDIUM,
                'integrity': IntegrityStealthLevel.MEDIUM,
                'advanced': AdvancedStealthLevel.MEDIUM
            },
            GlobalStealthLevel.HIGH: {
                'injection': InjectionStealthLevel.HIGH,
                'session': SessionStealthLevel.HIGH,
                'cross_site': CrossSiteStealthLevel.HIGH,
                'authentication': AuthStealthLevel.HIGH,
                'file_system': FSStealthLevel.HIGH,
                'infrastructure': InfraStealthLevel.HIGH,
                'integrity': IntegrityStealthLevel.HIGH,
                'advanced': AdvancedStealthLevel.HIGH
            },
            GlobalStealthLevel.APT: {
                'injection': InjectionStealthLevel.APT,
                'session': SessionStealthLevel.APT,
                'cross_site': CrossSiteStealthLevel.APT,
                'authentication': AuthStealthLevel.APT,
                'file_system': FSStealthLevel.APT,
                'infrastructure': InfraStealthLevel.APT,
                'integrity': IntegrityStealthLevel.APT,
                'advanced': AdvancedStealthLevel.APT
            }
        }
        
        self.category_stealth = stealth_mapping[stealth_level]
        
        # Initialiser les gestionnaires avec leur niveau de furtivité
        self.managers = {
            'injection': InjectionAttackManager(target, self.category_stealth['injection']),
            'session': SessionAttackManager(target, self.category_stealth['session']),
            'cross_site': CrossSiteAttackManager(target, self.category_stealth['cross_site']),
            'authentication': AuthenticationAttackManager(target, self.category_stealth['authentication']),
            'file_system': FileSystemAttackManager(target, self.category_stealth['file_system']),
            'infrastructure': InfrastructureAttackManager(target, self.category_stealth['infrastructure']),
            'integrity': IntegrityAttackManager(target, self.category_stealth['integrity']),
            'advanced': AdvancedAttackManager(target, self.category_stealth['advanced'])
        }
        
        # Configuration APT globale
        self.apt_config = GlobalAPTConfig()
    
    def _log_stealth_setup(self):
        """Enregistre la configuration de furtivité"""
        log_entry = {
            'timestamp': time.time(),
            'event': 'orchestrator_stealth_setup',
            'global_level': self.stealth_level.value,
            'category_levels': {k: v.value for k, v in self.category_stealth.items()}
        }
        self.attack_logs.append(log_entry)
        
        if not self.apt_config.stealth_logging:
            return
            
        print(f"\n🕵️ Orchestrateur mode furtif: {self.stealth_level.value.upper()}")
        print(f"   - Délai entre catégories: {self.apt_config.delay_between_categories}s")
        print(f"   - Ordre intelligent: {self.apt_config.intelligent_ordering}")
        print(f"   - Rapport APT: {self.apt_config.apt_reporting}")
    
    def _apply_delay_between_categories(self, category_index: int, total: int):
        """Applique un délai entre les catégories d'attaques"""
        if category_index >= total - 1:
            return
        
        if self.stealth_level == GlobalStealthLevel.APT and self.apt_config.random_pauses:
            delay = random.uniform(*self.apt_config.delay_between_categories)
            jitter = delay * self.apt_config.jitter
            delay += random.uniform(-jitter, jitter)
            print(f"\n💤 Pause APT entre catégories: {delay:.0f}s")
            time.sleep(max(0, delay))
    
    def _get_intelligent_order(self) -> List[str]:
        """
        Retourne l'ordre intelligent des attaques (du moins au plus intrusif)
        """
        if not self.apt_config.intelligent_ordering:
            return list(self.managers.keys())
        
        # Ordre progressif (passif → actif)
        return [
            'infrastructure',   # Scan passif d'infrastructure
            'integrity',        # Vérification d'intégrité
            'cross_site',       # Tests cross-site (XSS, CSRF)
            'authentication',   # Tests d'authentification
            'session',          # Tests de session
            'injection',        # Injections (SQL, Command)
            'file_system',      # Attaques système de fichiers
            'advanced'          # Attaques avancées
        ]
    
    def run_all(self, **kwargs) -> dict:
        """
        Exécute TOUS les types d'attaques disponibles avec orchestration intelligente
        
        Args:
            **kwargs: Options de configuration globales
        """
        self.start_time = time.time()
        self._log_stealth_setup()
        
        print("\n" + "=" * 70)
        print(f"🎯 REDFORGE - LANCEMENT DE TOUTES LES ATTAQUES")
        print(f"🎯 Cible: {self.target}")
        print(f"🎭 Mode furtif: {self.stealth_level.value.upper()}")
        print("=" * 70)
        
        # Ajouter la configuration furtive aux kwargs
        kwargs['stealth_level'] = self.stealth_level.value
        kwargs['apt_mode'] = (self.stealth_level == GlobalStealthLevel.APT)
        
        # Obtenir l'ordre intelligent des attaques
        attack_order = self._get_intelligent_order()
        
        for idx, attack_type in enumerate(attack_order):
            manager = self.managers.get(attack_type)
            if not manager:
                continue
            
            print(f"\n{'=' * 50}")
            print(f"🔴 ATTAQUES {attack_type.upper()}")
            print(f"{'=' * 50}")
            
            try:
                start_cat_time = time.time()
                self.results[attack_type] = manager.run_all(**kwargs)
                duration = time.time() - start_cat_time
                
                # Logging
                self.attack_logs.append({
                    'timestamp': start_cat_time,
                    'category': attack_type,
                    'duration': duration,
                    'status': 'success'
                })
                
            except Exception as e:
                print(f"❌ Erreur lors des attaques {attack_type}: {e}")
                self.results[attack_type] = {"error": str(e)}
                self.attack_logs.append({
                    'timestamp': time.time(),
                    'category': attack_type,
                    'error': str(e),
                    'status': 'error'
                })
            
            # Délai entre les catégories
            self._apply_delay_between_categories(idx, len(attack_order))
        
        self._print_global_summary()
        
        return self.results
    
    def run_category(self, category: str, **kwargs) -> dict:
        """
        Exécute une catégorie d'attaques spécifique
        
        Args:
            category: Catégorie d'attaques (injection, session, cross_site, etc.)
            **kwargs: Options de configuration
        """
        if category not in self.managers:
            available = ', '.join(self.managers.keys())
            raise ValueError(f"Catégorie inconnue: {category}. Disponibles: {available}")
        
        print(f"\n{'=' * 50}")
        print(f"🔴 ATTAQUES {category.upper()}")
        print(f"🎭 Mode: {self.stealth_level.value.upper()}")
        print(f"{'=' * 50}")
        
        kwargs['stealth_level'] = self.stealth_level.value
        kwargs['apt_mode'] = (self.stealth_level == GlobalStealthLevel.APT)
        
        start_time = time.time()
        self.results[category] = self.managers[category].run_all(**kwargs)
        duration = time.time() - start_time
        
        self.attack_logs.append({
            'timestamp': start_time,
            'category': category,
            'duration': duration,
            'status': 'success'
        })
        
        return self.results[category]
    
    def run_selected_categories(self, categories: List[str], **kwargs) -> dict:
        """
        Exécute une sélection de catégories d'attaques
        
        Args:
            categories: Liste des catégories à exécuter
            **kwargs: Options de configuration
        """
        results = {}
        
        for idx, category in enumerate(categories):
            if category not in self.managers:
                print(f"⚠️ Catégorie ignorée: {category} (non trouvée)")
                continue
            
            result = self.run_category(category, **kwargs)
            results[category] = result
            
            # Délai entre les catégories
            if idx < len(categories) - 1:
                self._apply_delay_between_categories(idx, len(categories))
        
        return results
    
    def run_specific_attack(self, category: str, attack_name: str, **kwargs) -> dict:
        """
        Exécute une attaque spécifique
        
        Args:
            category: Catégorie d'attaques
            attack_name: Nom de l'attaque spécifique
            **kwargs: Options de configuration
        """
        # Mapping des attaques spécifiques avec leurs types
        specific_attacks = {
            'injection': {
                'sql': (SQLInjection, None),
                'nosql': (NoSQLInjection, None),
                'command': (CommandInjection, None),
                'ldap': (LDAPInjection, None),
                'xpath': (XPathInjection, None),
                'html': (HTMLInjection, None),
                'template': (TemplateInjection, None)
            },
            'session': {
                'hijacking': (SessionHijacking, None),
                'fixation': (SessionFixation, None),
                'cookie': (CookieManipulation, None),
                'jwt': (JWTAattacks, None),
                'oauth': (OAuthAttacks, None)
            },
            'cross_site': {
                'xss': (XSSEngine, None),
                'csrf': (CSRFGenerator, None),
                'clickjacking': (ClickjackingDetector, None),
                'cors': (CORMisconfigurationDetector, None),
                'postmessage': (PostMessageAttacks, None)
            },
            'authentication': {
                'bruteforce': (BruteForce, None),
                'credential_stuffing': (CredentialStuffing, None),
                'password_spraying': (PasswordSpraying, None),
                'mfa_bypass': (MFABypass, None),
                'priv_esc': (PrivilegeEscalation, None),
                'race_condition': (RaceCondition, None)
            },
            'file_system': {
                'lfi_rfi': (LFIRFIAttack, None),
                'file_upload': (FileUploadAttack, None),
                'dir_traversal': (DirectoryTraversal, None),
                'buffer_overflow': (BufferOverflow, None),
                'path_normalization': (PathNormalization, None),
                'zip_slip': (ZipSlipAttack, None)
            },
            'infrastructure': {
                'waf_bypass': (WAFBypass, None),
                'misconfig': (MisconfigDetector, None),
                'load_balancer': (LoadBalancerAttack, None),
                'host_header': (HostHeaderInjection, None),
                'cache_poisoning': (CachePoisoning, None)
            },
            'integrity': {
                'data_tampering': (DataTampering, None),
                'info_leakage': (InfoLeakage, None),
                'mitm': (MITMAttacks, None),
                'param_pollution': (ParameterPollution, None),
                'business_logic': (BusinessLogicFlaws, None)
            },
            'advanced': {
                'api': (APIAttacks, None),
                'graphql': (GraphQLAttacks, None),
                'websocket': (WebSocketAttacks, None),
                'deserialization': (DeserializationAttack, None),
                'browser': (BrowserExploit, None),
                'microservices': (MicroservicesAttack, None),
                'chaining': (AttackChaining, None)
            }
        }
        
        if category not in specific_attacks:
            raise ValueError(f"Catégorie inconnue: {category}")
        
        if attack_name not in specific_attacks[category]:
            available = ', '.join(specific_attacks[category].keys())
            raise ValueError(f"Attaque inconnue: {attack_name}. Disponibles: {available}")
        
        attack_class, _ = specific_attacks[category][attack_name]
        attack_instance = attack_class()
        
        print(f"\n🎯 Lancement de l'attaque: {category}.{attack_name}")
        print(f"🎯 Cible: {self.target}")
        print(f"🎭 Mode: {self.stealth_level.value.upper()}")
        
        # Ajouter la configuration furtive
        kwargs['stealth_level'] = self.stealth_level.value
        kwargs['apt_mode'] = (self.stealth_level == GlobalStealthLevel.APT)
        
        start_time = time.time()
        result = attack_instance.scan(self.target, **kwargs)
        duration = time.time() - start_time
        
        self.attack_logs.append({
            'timestamp': start_time,
            'category': category,
            'attack': attack_name,
            'duration': duration,
            'status': 'success'
        })
        
        return result
    
    def run_apt_operation(self, categories: Optional[List[str]] = None, **kwargs) -> dict:
        """
        Exécute une opération APT complète avec orchestration avancée
        
        Args:
            categories: Catégories à inclure (None = toutes)
            **kwargs: Options de configuration
        """
        print("\n" + "=" * 70)
        print("🎭 DÉBUT DE L'OPÉRATION APT - REDFORGE")
        print(f"🎯 Cible: {self.target}")
        print("=" * 70)
        
        # Configuration APT
        original_stealth = self.stealth_level
        self.stealth_level = GlobalStealthLevel.APT
        self._log_stealth_setup()
        
        # Catégories à exécuter
        if categories is None:
            categories = self._get_intelligent_order()
        
        # Journal APT
        apt_log = {
            'operation_start': time.time(),
            'target': self.target,
            'stealth_level': 'APT',
            'categories': categories,
            'intelligent_ordering': self.apt_config.intelligent_ordering
        }
        
        # Exécuter les catégories sélectionnées
        results = self.run_selected_categories(categories, **kwargs)
        
        # Ajouter les métadonnées APT
        total_vulns = 0
        for r in results.values():
            if isinstance(r, dict):
                total_vulns += r.get('count', 0)
        
        results['apt_metadata'] = {
            'operation_duration': time.time() - apt_log['operation_start'],
            'total_categories': len(categories),
            'total_vulnerabilities': total_vulns,
            'stealth_level': 'APT',
            'intelligent_ordering': self.apt_config.intelligent_ordering,
            'signature_rotation': self.apt_config.signature_rotation
        }
        
        # Restaurer le niveau de furtivité original
        self.stealth_level = original_stealth
        
        print("\n🎭 OPÉRATION APT TERMINÉE")
        self._print_apt_summary(results['apt_metadata'])
        
        return results
    
    def _print_global_summary(self):
        """Affiche un résumé global de toutes les attaques"""
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ GLOBAL DES ATTAQUES REDFORGE")
        print("=" * 70)
        
        total_vulnerabilities = 0
        category_summary = {}
        
        for attack_type, result in self.results.items():
            if isinstance(result, dict):
                count = result.get('count', 0)
                if count > 0:
                    total_vulnerabilities += count
                    category_summary[attack_type] = count
                    print(f"\n🔴 {attack_type.upper()}: {count} vulnérabilité(s)")
        
        if total_vulnerabilities == 0:
            print("\n✅ Aucune vulnérabilité détectée")
        else:
            print(f"\n⚠️ TOTAL: {total_vulnerabilities} vulnérabilité(s) détectée(s)")
            
            if self.apt_config.apt_reporting:
                print("\n📈 Détail par catégorie:")
                for cat, count in sorted(category_summary.items(), key=lambda x: x[1], reverse=True):
                    print(f"   - {cat}: {count}")
    
    def _print_apt_summary(self, apt_metadata: Dict):
        """Affiche le résumé de l'opération APT"""
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ DE L'OPÉRATION APT - REDFORGE")
        print("=" * 70)
        print(f"⏱️  Durée totale: {apt_metadata['operation_duration']:.1f}s")
        print(f"🎯 Catégories exécutées: {apt_metadata['total_categories']}")
        print(f"✅ Vulnérabilités trouvées: {apt_metadata['total_vulnerabilities']}")
        print(f"🕵️ Niveau furtif: {apt_metadata['stealth_level']}")
        print(f"📊 Ordre intelligent: {apt_metadata['intelligent_ordering']}")
        print(f"🔄 Rotation signatures: {apt_metadata['signature_rotation']}")
    
    def save_results(self, output_file: str, include_logs: bool = False):
        """
        Sauvegarde tous les résultats au format JSON
        
        Args:
            output_file: Fichier de sortie
            include_logs: Inclure les logs d'attaque
        """
        output_data = {
            'target': self.target,
            'timestamp': time.time(),
            'stealth_level': self.stealth_level.value,
            'results': self.results
        }
        
        if include_logs:
            output_data['attack_logs'] = self.attack_logs
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        
        print(f"\n💾 Résultats sauvegardés dans {output_file}")
    
    def get_summary(self) -> dict:
        """
        Retourne un résumé des résultats
        
        Returns:
            Dictionnaire contenant le résumé des vulnérabilités
        """
        summary = {
            "target": self.target,
            "stealth_level": self.stealth_level.value,
            "categories": {},
            "total_vulnerabilities": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "scan_duration": time.time() - self.start_time if self.start_time else 0
        }
        
        for attack_type, result in self.results.items():
            if isinstance(result, dict):
                vulnerabilities = result.get('vulnerabilities', [])
                
                category_summary = {
                    "count": len(vulnerabilities),
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0
                }
                
                for vuln in vulnerabilities:
                    severity = vuln.get('severity', 'MEDIUM').upper()
                    if severity == 'CRITICAL':
                        category_summary['critical'] += 1
                        summary['critical_count'] += 1
                    elif severity == 'HIGH':
                        category_summary['high'] += 1
                        summary['high_count'] += 1
                    elif severity == 'MEDIUM':
                        category_summary['medium'] += 1
                        summary['medium_count'] += 1
                    else:
                        category_summary['low'] += 1
                        summary['low_count'] += 1
                
                summary['categories'][attack_type] = category_summary
                summary['total_vulnerabilities'] += len(vulnerabilities)
        
        return summary
    
    def generate_apt_report(self, output_file: str = "apt_report.json") -> Dict:
        """
        Génère un rapport APT détaillé
        
        Args:
            output_file: Fichier de sortie pour le rapport
        """
        report = {
            "operation": {
                "target": self.target,
                "stealth_level": self.stealth_level.value,
                "timestamp": time.time(),
                "duration": time.time() - self.start_time if self.start_time else 0
            },
            "summary": self.get_summary(),
            "attack_logs": self.attack_logs,
            "recommendations": self._generate_global_recommendations()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        
        print(f"\n📋 Rapport APT généré: {output_file}")
        return report
    
    def _generate_global_recommendations(self) -> List[str]:
        """Génère des recommandations globales basées sur tous les résultats"""
        recommendations = set()
        
        for attack_type, result in self.results.items():
            if isinstance(result, dict) and 'recommendations' in result:
                for rec in result['recommendations']:
                    recommendations.add(rec)
        
        return list(recommendations)[:20]  # Limiter à 20 recommandations


# Fonctions utilitaires
def create_apt_session(target: str) -> AttackOrchestrator:
    """Crée une session APT complète"""
    return AttackOrchestrator(target, stealth_level=GlobalStealthLevel.APT)


def quick_assessment(target: str) -> AttackOrchestrator:
    """Évaluation rapide (peu discret)"""
    return AttackOrchestrator(target, stealth_level=GlobalStealthLevel.LOW)


def stealth_assessment(target: str) -> AttackOrchestrator:
    """Évaluation discrète"""
    return AttackOrchestrator(target, stealth_level=GlobalStealthLevel.HIGH)


# Exports principaux
__all__ = [
    # Orchestrateur principal
    'AttackOrchestrator',
    'GlobalStealthLevel',
    'GlobalAPTConfig',
    'create_apt_session',
    'quick_assessment',
    'stealth_assessment',
    
    # Injection
    'InjectionAttackManager',
    'InjectionAttackType',
    'SQLInjection',
    'NoSQLInjection',
    'CommandInjection',
    'LDAPInjection',
    'XPathInjection',
    'HTMLInjection',
    'TemplateInjection',
    
    # Session
    'SessionAttackManager',
    'SessionAttackType',
    'SessionHijacking',
    'SessionFixation',
    'CookieManipulation',
    'JWTAattacks',
    'OAuthAttacks',
    
    # Cross-Site
    'CrossSiteAttackManager',
    'CrossSiteAttackType',
    'XSSEngine',
    'CSRFGenerator',
    'ClickjackingDetector',
    'CORMisconfigurationDetector',
    'PostMessageAttacks',
    
    # Authentication
    'AuthenticationAttackManager',
    'AuthAttackType',
    'BruteForce',
    'CredentialStuffing',
    'PasswordSpraying',
    'MFABypass',
    'PrivilegeEscalation',
    'RaceCondition',
    
    # File System
    'FileSystemAttackManager',
    'FileSystemAttackType',
    'LFIRFIAttack',
    'FileUploadAttack',
    'DirectoryTraversal',
    'BufferOverflow',
    'PathNormalization',
    'ZipSlipAttack',
    
    # Infrastructure
    'InfrastructureAttackManager',
    'InfrastructureAttackType',
    'WAFBypass',
    'MisconfigDetector',
    'LoadBalancerAttack',
    'HostHeaderInjection',
    'CachePoisoning',
    
    # Integrity
    'IntegrityAttackManager',
    'IntegrityAttackType',
    'DataTampering',
    'InfoLeakage',
    'MITMAttacks',
    'ParameterPollution',
    'BusinessLogicFlaws',
    
    # Advanced
    'AdvancedAttackManager',
    'AdvancedAttackType',
    'APIAttacks',
    'GraphQLAttacks',
    'WebSocketAttacks',
    'DeserializationAttack',
    'BrowserExploit',
    'MicroservicesAttack',
    'AttackChaining'
]


# Point d'entrée pour tests
if __name__ == "__main__":
    import random
    
    print("=" * 60)
    print("RedForge - Module d'Attaques APT")
    print("=" * 60)
    
    # Créer l'orchestrateur
    orchestrator = AttackOrchestrator("https://example.com", GlobalStealthLevel.APT)
    
    # Afficher les catégories disponibles
    print("\n📦 Catégories d'attaques disponibles:")
    for category in orchestrator.managers.keys():
        print(f"  - {category}")
    
    print("\n🎭 Modes de furtivité disponibles:")
    for mode in GlobalStealthLevel:
        print(f"  - {mode.value}")
    
    print("\n✅ Module d'attaques chargé avec succès")
    print("\n💡 Exemples d'utilisation:")
    print("   orchestrator = create_apt_session('https://cible.com')")
    print("   results = orchestrator.run_apt_operation()")
    print("   orchestrator.generate_apt_report('rapport_apt.json')")