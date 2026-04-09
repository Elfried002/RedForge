#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques sur l'intégrité pour RedForge
Contient tous les types d'attaques liées à l'intégrité des données
Version APT avec mode furtif et sélection avancée
"""

import time
import random
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from src.attacks.integrity.data_tampering import DataTampering
from src.attacks.integrity.info_leakage import InfoLeakage
from src.attacks.integrity.mitm_attacks import MITMAttacks
from src.attacks.integrity.parameter_pollution import ParameterPollution
from src.attacks.integrity.business_logic import BusinessLogicFlaws


class IntegrityAttackType(Enum):
    """Types d'attaques sur l'intégrité disponibles"""
    DATA_TAMPERING = "data_tampering"
    INFO_LEAKAGE = "info_leakage"
    MITM_ATTACKS = "mitm_attacks"
    PARAMETER_POLLUTION = "parameter_pollution"
    BUSINESS_LOGIC = "business_logic"


class StealthLevel(Enum):
    """Niveaux de furtivité"""
    LOW = "low"          # Rapide, peu discret
    MEDIUM = "medium"    # Équilibré
    HIGH = "high"        # Très discret, lent
    APT = "apt"          # Ultra discret, style APT


@dataclass
class IntegrityAPTConfig:
    """Configuration pour les opérations APT sur l'intégrité"""
    # Délais entre les attaques (secondes)
    delay_between_attacks: tuple = (30, 180)
    # Jitter pour les délais
    jitter: float = 0.3
    # Pauses aléatoires pendant les scans
    random_pauses: bool = True
    # Analyse progressive (du moins au plus intrusif)
    progressive_analysis: bool = True
    # Éviter les patterns de détection
    avoid_detection_patterns: bool = True
    # Vérification d'intégrité en arrière-plan
    background_integrity_check: bool = False
    # Logging discret
    stealth_logging: bool = True
    # Rotation des signatures
    signature_rotation: bool = True


class IntegrityAttackManager:
    """
    Gestionnaire central des attaques sur l'intégrité
    Supporte la sélection multiple, le mode furtif et les opérations APT
    """
    
    def __init__(self, target: str, stealth_level: StealthLevel = StealthLevel.LOW):
        """
        Initialise le gestionnaire d'attaques sur l'intégrité
        
        Args:
            target: Cible (URL ou IP)
            stealth_level: Niveau de furtivité à utiliser
        """
        self.target = target
        self.stealth_level = stealth_level
        self.results = {}
        self.attack_logs = []
        
        # Initialiser les différents moteurs d'attaque
        self.attacks = {
            IntegrityAttackType.DATA_TAMPERING: DataTampering(),
            IntegrityAttackType.INFO_LEAKAGE: InfoLeakage(),
            IntegrityAttackType.MITM_ATTACKS: MITMAttacks(),
            IntegrityAttackType.PARAMETER_POLLUTION: ParameterPollution(),
            IntegrityAttackType.BUSINESS_LOGIC: BusinessLogicFlaws()
        }
        
        # Configurer la furtivité
        self._setup_stealth()
        
        # Configuration APT par défaut
        self.apt_config = IntegrityAPTConfig()
    
    def _setup_stealth(self):
        """Configure les paramètres de furtivité"""
        stealth_configs = {
            StealthLevel.LOW: {
                'delay_between_requests': (0.1, 0.3),
                'delay_between_attacks': (1, 5),
                'max_threads': 20,
                'random_delays': False,
                'stealth_headers': False,
                'depth': 'full',
                'intercept_level': 'none'
            },
            StealthLevel.MEDIUM: {
                'delay_between_requests': (0.5, 1.5),
                'delay_between_attacks': (5, 15),
                'max_threads': 10,
                'random_delays': True,
                'stealth_headers': True,
                'depth': 'standard',
                'intercept_level': 'passive'
            },
            StealthLevel.HIGH: {
                'delay_between_requests': (2, 5),
                'delay_between_attacks': (15, 45),
                'max_threads': 3,
                'random_delays': True,
                'stealth_headers': True,
                'depth': 'light',
                'intercept_level': 'passive'
            },
            StealthLevel.APT: {
                'delay_between_requests': (5, 15),
                'delay_between_attacks': (30, 180),
                'max_threads': 1,
                'random_delays': True,
                'stealth_headers': True,
                'depth': 'stealth',
                'intercept_level': 'background'
            }
        }
        
        self.stealth_config = stealth_configs[self.stealth_level]
        self._log_stealth_setup()
    
    def _log_stealth_setup(self):
        """Enregistre la configuration de furtivité"""
        log_entry = {
            'timestamp': time.time(),
            'event': 'stealth_setup',
            'level': self.stealth_level.value,
            'config': self.stealth_config
        }
        self.attack_logs.append(log_entry)
        
        if not self.apt_config.stealth_logging:
            return
            
        print(f"\n🕵️ Mode furtif intégrité: {self.stealth_level.value.upper()}")
        print(f"   - Délai entre requêtes: {self.stealth_config['delay_between_requests']}s")
        print(f"   - Délai entre attaques: {self.stealth_config['delay_between_attacks']}s")
        print(f"   - Threads max: {self.stealth_config['max_threads']}")
        print(f"   - Profondeur scan: {self.stealth_config['depth']}")
        print(f"   - Interception: {self.stealth_config['intercept_level']}")
    
    def _apply_stealth_delay(self, delay_range: tuple):
        """Applique un délai furtif"""
        if not self.stealth_config['random_delays']:
            delay = delay_range[1]
        else:
            delay = random.uniform(delay_range[0], delay_range[1])
        
        # Ajouter du jitter pour le mode APT
        if self.stealth_level == StealthLevel.APT:
            jitter = delay * self.apt_config.jitter
            delay += random.uniform(-jitter, jitter)
        
        time.sleep(max(0, delay))
    
    def select_attacks(self, attack_types: List[IntegrityAttackType]) -> List[IntegrityAttackType]:
        """
        Sélectionne les attaques à exécuter
        
        Args:
            attack_types: Liste des types d'attaques à exécuter
            
        Returns:
            Liste des attaques sélectionnées
        """
        available = [at for at in attack_types if at in self.attacks]
        
        if not available:
            print("⚠️ Aucune attaque sur l'intégrité valide sélectionnée")
            return []
        
        print(f"\n🎯 Attaques sur l'intégrité sélectionnées: {len(available)}")
        for attack in available:
            print(f"   - {attack.value.replace('_', ' ').title()}")
        
        return available
    
    def run_selected(self, attack_types: List[IntegrityAttackType], **kwargs) -> Dict[str, Any]:
        """
        Exécute les types d'attaques sélectionnés sur l'intégrité
        
        Args:
            attack_types: Liste des attaques à exécuter
            **kwargs: Options de configuration
                - intercept: Intercepter les requêtes
                - test_params: Tester la pollution de paramètres
                - deep_scan: Scan approfondi
                - depth: Profondeur du scan
        """
        selected = self.select_attacks(attack_types)
        
        if not selected:
            return {'error': 'No attacks selected'}
        
        print(f"\n🔐 ATTAQUES SUR L'INTÉGRITÉ sur {self.target}")
        print(f"🎭 Mode: {self.stealth_level.value.upper()}")
        print("=" * 60)
        
        # Ajouter les paramètres furtifs
        kwargs['stealth_config'] = self.stealth_config
        kwargs['stealth_level'] = self.stealth_level.value
        kwargs['apt_mode'] = (self.stealth_level == StealthLevel.APT)
        kwargs['intercept_level'] = self.stealth_config['intercept_level']
        kwargs['depth'] = self.stealth_config['depth']
        
        # Exécuter les attaques selon la stratégie
        if self.apt_config.progressive_analysis and self.stealth_level == StealthLevel.APT:
            results = self._run_progressive_analysis(selected, **kwargs)
        else:
            results = self._run_sequential_analysis(selected, **kwargs)
        
        # Résumé
        self._print_summary()
        
        return results
    
    def _run_sequential_analysis(self, selected: List[IntegrityAttackType], **kwargs) -> Dict[str, Any]:
        """Exécute les analyses séquentiellement"""
        results = {}
        
        for idx, attack_type in enumerate(selected):
            attack_name = attack_type.value.replace('_', ' ').title()
            print(f"\n🎯 [{idx+1}/{len(selected)}] Exécution: {attack_name}")
            
            # Pause APT avant l'attaque
            if idx > 0 and self.stealth_level == StealthLevel.APT:
                if self.apt_config.random_pauses:
                    inactivity = random.uniform(30, 120)
                    print(f"💤 Pause APT: {inactivity:.0f}s")
                    time.sleep(inactivity)
                else:
                    self._apply_stealth_delay(self.stealth_config['delay_between_attacks'])
            
            # Exécuter l'attaque
            attack_result = self._run_single_attack(attack_type, **kwargs)
            results[attack_type.value] = attack_result
            
            # Délai entre les attaques
            if idx < len(selected) - 1:
                self._apply_stealth_delay(self.stealth_config['delay_between_attacks'])
        
        self.results = results
        return results
    
    def _run_progressive_analysis(self, selected: List[IntegrityAttackType], **kwargs) -> Dict[str, Any]:
        """
        Exécute une analyse progressive pour mode APT
        Commence par les analyses passives, puis actives
        """
        results = {}
        
        # Classification des analyses par intrusivité
        passive_analysis = [
            IntegrityAttackType.INFO_LEAKAGE,
            IntegrityAttackType.BUSINESS_LOGIC
        ]
        
        semi_active_analysis = [
            IntegrityAttackType.PARAMETER_POLLUTION,
            IntegrityAttackType.DATA_TAMPERING
        ]
        
        active_analysis = [
            IntegrityAttackType.MITM_ATTACKS
        ]
        
        layers = [
            ("Passive", passive_analysis),
            ("Semi-active", semi_active_analysis),
            ("Active", active_analysis)
        ]
        
        for layer_name, layer_attacks in layers:
            applicable = [at for at in layer_attacks if at in selected]
            if not applicable:
                continue
            
            print(f"\n📊 Couche {layer_name}:")
            
            for attack_type in applicable:
                attack_name = attack_type.value.replace('_', ' ').title()
                print(f"   → Test: {attack_name}")
                
                # Pause entre les attaques de la couche
                if self.apt_config.random_pauses:
                    time.sleep(random.uniform(10, 30))
                
                result = self._run_single_attack(attack_type, **kwargs)
                results[attack_type.value] = result
                
                # Si vulnérabilité critique trouvée, passer à la couche suivante
                if result.get('critical_found', False):
                    print(f"   ⚠️ Vulnérabilité critique trouvée, passage couche suivante")
                    break
            
            # Pause entre les couches
            if self.apt_config.random_pauses:
                pause = random.uniform(60, 180)
                print(f"💤 Pause entre couches: {pause:.0f}s")
                time.sleep(pause)
        
        self.results = results
        return results
    
    def _run_single_attack(self, attack_type: IntegrityAttackType, **kwargs) -> Dict[str, Any]:
        """Exécute une attaque unique avec les paramètres de furtivité"""
        attack = self.attacks[attack_type]
        
        # Ajuster les paramètres selon le niveau de furtivité
        scan_kwargs = kwargs.copy()
        scan_kwargs['threads'] = self.stealth_config['max_threads']
        scan_kwargs['delay'] = self.stealth_config['delay_between_requests'][0]
        scan_kwargs['intercept'] = self.stealth_config['intercept_level'] != 'none'
        
        start_time = time.time()
        
        try:
            result = attack.scan(self.target, **scan_kwargs)
            duration = time.time() - start_time
            
            # Logging discret
            if self.apt_config.stealth_logging:
                vuln_count = len(result.get('vulnerabilities', [])) if isinstance(result, dict) else 0
                if vuln_count > 0:
                    print(f"   ✓ {vuln_count} vulnérabilité(s) trouvée(s) en {duration:.1f}s")
                else:
                    print(f"   ✓ Scan terminé en {duration:.1f}s")
            
            result['duration'] = duration
            result['stealth_level'] = self.stealth_level.value
            
            # Ajouter au journal
            self.attack_logs.append({
                'timestamp': start_time,
                'attack_type': attack_type.value,
                'duration': duration,
                'vulnerabilities_found': len(result.get('vulnerabilities', [])) if isinstance(result, dict) else 0
            })
            
            return result
            
        except Exception as e:
            print(f"   ✗ Erreur: {str(e)}")
            return {'error': str(e), 'vulnerabilities': []}
    
    def run_all(self, **kwargs) -> Dict[str, Any]:
        """
        Exécute tous les types d'attaques sur l'intégrité
        
        Args:
            **kwargs: Options de configuration
        """
        all_attacks = list(IntegrityAttackType)
        return self.run_selected(all_attacks, **kwargs)
    
    def run_apt_operation(self, **kwargs) -> Dict[str, Any]:
        """
        Exécute une opération complète style APT pour l'intégrité
        """
        print("\n🎭 DÉBUT DE L'OPÉRATION APT - INTÉGRITÉ")
        print("=" * 60)
        
        # Configuration APT
        original_stealth = self.stealth_level
        self.stealth_level = StealthLevel.APT
        self._setup_stealth()
        
        # Stratégie APT typique pour l'intégrité
        apt_analysis_order = [
            IntegrityAttackType.INFO_LEAKAGE,      # D'abord passif
            IntegrityAttackType.BUSINESS_LOGIC,    # Analyse logique
            IntegrityAttackType.PARAMETER_POLLUTION, # Pollution paramètres
            IntegrityAttackType.DATA_TAMPERING,    # Altération données
            IntegrityAttackType.MITM_ATTACKS       # Interception active
        ]
        
        # Journal APT
        apt_log = {
            'operation_start': time.time(),
            'target': self.target,
            'stealth_level': 'APT',
            'attack_order': [at.value for at in apt_analysis_order]
        }
        
        # Exécuter les attaques
        results = self.run_selected(apt_analysis_order, **kwargs)
        
        # Ajouter les métadonnées APT
        total_vulns = 0
        for r in results.values():
            if isinstance(r, dict):
                total_vulns += len(r.get('vulnerabilities', []))
        
        results['apt_metadata'] = {
            'operation_duration': time.time() - apt_log['operation_start'],
            'total_attacks': len(apt_analysis_order),
            'total_vulnerabilities': total_vulns,
            'stealth_level': 'APT',
            'progressive_analysis': self.apt_config.progressive_analysis,
            'background_check': self.apt_config.background_integrity_check
        }
        
        # Restaurer le niveau de furtivité original
        self.stealth_level = original_stealth
        self._setup_stealth()
        
        print("\n🎭 OPÉRATION APT - INTÉGRITÉ TERMINÉE")
        self._print_apt_summary(results['apt_metadata'])
        
        return results
    
    def _print_summary(self):
        """Affiche un résumé des vulnérabilités trouvées"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES ATTAQUES SUR L'INTÉGRITÉ")
        print("=" * 60)
        
        total_vulnerabilities = []
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        
        for attack_type, result in self.results.items():
            if not result or not isinstance(result, dict):
                continue
            
            vulnerabilities = result.get('vulnerabilities', [])
            if not vulnerabilities:
                continue
            
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'MEDIUM')
                if severity == 'CRITICAL':
                    critical_count += 1
                elif severity == 'HIGH':
                    high_count += 1
                elif severity == 'MEDIUM':
                    medium_count += 1
                else:
                    low_count += 1
                
                total_vulnerabilities.append({
                    'type': attack_type.replace('_', ' ').upper(),
                    'details': vuln.get('details', vuln.get('description', 'unknown')),
                    'severity': severity
                })
        
        if total_vulnerabilities:
            print(f"\n⚠️  {len(total_vulnerabilities)} vulnérabilité(s) d'intégrité détectée(s):")
            print(f"   🔴 CRITICAL: {critical_count}")
            print(f"   🟠 HIGH: {high_count}")
            print(f"   🟡 MEDIUM: {medium_count}")
            print(f"   🔵 LOW: {low_count}")
            
            print("\nDétails:")
            for vuln in total_vulnerabilities[:15]:
                icon = "🔴" if vuln['severity'] == "CRITICAL" else "🟠" if vuln['severity'] == "HIGH" else "🟡" if vuln['severity'] == "MEDIUM" else "🔵"
                print(f"   {icon} [{vuln['severity']}] {vuln['type']}: {vuln['details'][:80]}")
            
            if len(total_vulnerabilities) > 15:
                print(f"   ... et {len(total_vulnerabilities) - 15} autres")
        else:
            print("\n✅ Aucune vulnérabilité d'intégrité détectée")
    
    def _print_apt_summary(self, apt_metadata: Dict):
        """Affiche le résumé de l'opération APT"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE L'OPÉRATION APT - INTÉGRITÉ")
        print("=" * 60)
        print(f"⏱️  Durée totale: {apt_metadata['operation_duration']:.1f}s")
        print(f"🎯 Attaques exécutées: {apt_metadata['total_attacks']}")
        print(f"✅ Vulnérabilités trouvées: {apt_metadata['total_vulnerabilities']}")
        print(f"🕵️ Niveau furtif: {apt_metadata['stealth_level']}")
        print(f"📊 Analyse progressive: {apt_metadata['progressive_analysis']}")
        print(f"🔍 Vérification arrière-plan: {apt_metadata['background_check']}")
    
    def intercept_traffic(self, **kwargs):
        """
        Intercepte le trafic pour analyse en temps réel
        
        Args:
            **kwargs: Options d'interception
        """
        print("\n📡 Interception du trafic...")
        
        # Utiliser les paramètres furtifs
        kwargs['stealth'] = (self.stealth_level == StealthLevel.APT)
        kwargs['background'] = self.apt_config.background_integrity_check
        
        if hasattr(self.mitm_attacks, 'start_interceptor'):
            self.mitm_attacks.start_interceptor(**kwargs)
        
        if hasattr(self.data_tampering, 'start_monitor'):
            self.data_tampering.start_monitor(**kwargs)
    
    def save_results(self, output_file: str, include_logs: bool = False):
        """
        Sauvegarde les résultats au format JSON
        
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
    
    def get_attack_report(self) -> Dict:
        """Génère un rapport détaillé des attaques"""
        total_vulns = 0
        for r in self.results.values():
            if isinstance(r, dict):
                total_vulns += len(r.get('vulnerabilities', []))
        
        return {
            'target': self.target,
            'stealth_level': self.stealth_level.value,
            'total_attacks': len(self.results),
            'total_vulnerabilities': total_vulns,
            'vulnerabilities_by_type': {
                at: len(r.get('vulnerabilities', [])) if isinstance(r, dict) else 0
                for at, r in self.results.items()
            },
            'attack_details': self.results,
            'logs': self.attack_logs
        }
    
    def start_background_monitoring(self, duration: int = 3600):
        """
        Démarre une surveillance de fond de l'intégrité
        
        Args:
            duration: Durée de surveillance en secondes
        """
        print(f"\n🔍 Surveillance d'intégrité en arrière-plan pendant {duration}s")
        
        # Démarrer la surveillance en arrière-plan
        if hasattr(self.data_tampering, 'start_background_monitor'):
            self.data_tampering.start_background_monitor(duration)
        
        if hasattr(self.info_leakage, 'start_background_monitor'):
            self.info_leakage.start_background_monitor(duration)


# Fonctions utilitaires pour l'utilisation du module
def create_apt_integrity_session(target: str) -> IntegrityAttackManager:
    """Crée une session APT pour les attaques sur l'intégrité"""
    return IntegrityAttackManager(target, stealth_level=StealthLevel.APT)


def quick_integrity_assessment(target: str) -> IntegrityAttackManager:
    """Évaluation rapide de l'intégrité (peu discret)"""
    return IntegrityAttackManager(target, stealth_level=StealthLevel.LOW)


def stealth_integrity_assessment(target: str) -> IntegrityAttackManager:
    """Évaluation discrète de l'intégrité"""
    return IntegrityAttackManager(target, stealth_level=StealthLevel.HIGH)


__all__ = [
    'IntegrityAttackManager',
    'IntegrityAttackType',
    'StealthLevel',
    'IntegrityAPTConfig',
    'DataTampering',
    'InfoLeakage',
    'MITMAttacks',
    'ParameterPollution',
    'BusinessLogicFlaws',
    'create_apt_integrity_session',
    'quick_integrity_assessment',
    'stealth_integrity_assessment'
]