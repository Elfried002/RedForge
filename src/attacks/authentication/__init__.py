#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques sur l'authentification pour RedForge
Contient tous les types d'attaques liées à l'authentification
Version APT avec mode furtif et sélection avancée
"""

import time
import random
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.attacks.authentication.brute_force import BruteForce
from src.attacks.authentication.credential_stuffing import CredentialStuffing
from src.attacks.authentication.password_spraying import PasswordSpraying
from src.attacks.authentication.mfa_bypass import MFABypass
from src.attacks.authentication.privilege_escalation import PrivilegeEscalation
from src.attacks.authentication.race_condition import RaceCondition


class AttackType(Enum):
    """Types d'attaques disponibles"""
    BRUTE_FORCE = "brute_force"
    CREDENTIAL_STUFFING = "credential_stuffing"
    PASSWORD_SPRAYING = "password_spraying"
    MFA_BYPASS = "mfa_bypass"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    RACE_CONDITION = "race_condition"


class StealthLevel(Enum):
    """Niveaux de furtivité"""
    LOW = "low"          # Rapide, peu discret
    MEDIUM = "medium"    # Équilibré
    HIGH = "high"        # Très discret, lent
    APT = "apt"          # Ultra discret, style APT


@dataclass
class APTConfig:
    """Configuration pour les opérations APT"""
    # Délais entre les attaques (secondes)
    delay_between_attacks: tuple = (30, 180)  # 30s à 3min
    # Jitter pour les délais
    jitter: float = 0.3  # 30% de variation
    # Pauses aléatoires pendant les attaques
    random_pauses: bool = True
    # Simulation d'activité humaine
    human_behavior: bool = True
    # Rotation d'IP (nécessite proxy/Tor)
    ip_rotation: bool = False
    # Périodes d'inactivité
    inactivity_periods: bool = True
    # Logging discret
    stealth_logging: bool = True


class AuthenticationAttackManager:
    """
    Gestionnaire central des attaques sur l'authentification
    Supporte la sélection multiple, le mode furtif et les opérations APT
    """
    
    def __init__(self, target: str, stealth_level: StealthLevel = StealthLevel.LOW):
        """
        Initialise le gestionnaire d'attaques
        
        Args:
            target: Cible des attaques
            stealth_level: Niveau de furtivité à utiliser
        """
        self.target = target
        self.stealth_level = stealth_level
        self.results = {}
        self.attack_logs = []
        
        # Initialiser les différents moteurs d'attaque
        self.attacks = {
            AttackType.BRUTE_FORCE: BruteForce(),
            AttackType.CREDENTIAL_STUFFING: CredentialStuffing(),
            AttackType.PASSWORD_SPRAYING: PasswordSpraying(),
            AttackType.MFA_BYPASS: MFABypass(),
            AttackType.PRIVILEGE_ESCALATION: PrivilegeEscalation(),
            AttackType.RACE_CONDITION: RaceCondition()
        }
        
        # Configurer la furtivité
        self._setup_stealth()
        
        # Configuration APT par défaut
        self.apt_config = APTConfig()
    
    def _setup_stealth(self):
        """Configure les paramètres de furtivité"""
        stealth_configs = {
            StealthLevel.LOW: {
                'delay_between_requests': (0.1, 0.3),
                'delay_between_attacks': (1, 5),
                'max_threads': 20,
                'random_delays': False,
                'stealth_headers': False
            },
            StealthLevel.MEDIUM: {
                'delay_between_requests': (0.5, 1.5),
                'delay_between_attacks': (5, 15),
                'max_threads': 10,
                'random_delays': True,
                'stealth_headers': True
            },
            StealthLevel.HIGH: {
                'delay_between_requests': (2, 5),
                'delay_between_attacks': (15, 45),
                'max_threads': 3,
                'random_delays': True,
                'stealth_headers': True
            },
            StealthLevel.APT: {
                'delay_between_requests': (5, 15),
                'delay_between_attacks': (30, 180),
                'max_threads': 1,
                'random_delays': True,
                'stealth_headers': True
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
            
        print(f"\n🕵️ Mode furtif activé: {self.stealth_level.value.upper()}")
        print(f"   - Délai entre requêtes: {self.stealth_config['delay_between_requests']}s")
        print(f"   - Délai entre attaques: {self.stealth_config['delay_between_attacks']}s")
        print(f"   - Threads max: {self.stealth_config['max_threads']}")
    
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
    
    def select_attacks(self, attack_types: List[AttackType]) -> List[AttackType]:
        """
        Sélectionne les attaques à exécuter
        
        Args:
            attack_types: Liste des types d'attaques à exécuter
            
        Returns:
            Liste des attaques sélectionnées
        """
        available = [at for at in attack_types if at in self.attacks]
        
        if not available:
            print("⚠️ Aucune attaque valide sélectionnée")
            return []
        
        print(f"\n🎯 Attaques sélectionnées: {len(available)}")
        for attack in available:
            print(f"   - {attack.value.replace('_', ' ').title()}")
        
        return available
    
    def run_selected(self, attack_types: List[AttackType], **kwargs) -> Dict[str, Any]:
        """
        Exécute les types d'attaques sélectionnés
        
        Args:
            attack_types: Liste des attaques à exécuter
            **kwargs: Options de configuration
        """
        selected = self.select_attacks(attack_types)
        
        if not selected:
            return {'error': 'No attacks selected'}
        
        print(f"\n🔐 ATTAQUES SUR L'AUTHENTIFICATION sur {self.target}")
        print(f"🎭 Mode: {self.stealth_level.value.upper()}")
        print("=" * 60)
        
        # Exécuter les attaques séquentiellement avec délais
        for idx, attack_type in enumerate(selected):
            attack_name = attack_type.value.replace('_', ' ').title()
            print(f"\n🎯 [{idx+1}/{len(selected)}] Exécution: {attack_name}")
            
            # Pause APT avant l'attaque
            if idx > 0 and self.stealth_level == StealthLevel.APT:
                if self.apt_config.inactivity_periods:
                    inactivity = random.uniform(60, 300)  # 1-5 minutes
                    print(f"💤 Pause d'inactivité: {inactivity:.0f}s (mode APT)")
                    time.sleep(inactivity)
                else:
                    self._apply_stealth_delay(self.stealth_config['delay_between_attacks'])
            
            # Exécuter l'attaque
            attack_result = self._run_single_attack(attack_type, **kwargs)
            self.results[attack_type.value] = attack_result
            
            # Délai entre les attaques
            if idx < len(selected) - 1:
                self._apply_stealth_delay(self.stealth_config['delay_between_attacks'])
        
        # Résumé
        self._print_summary()
        
        return self.results
    
    def _run_single_attack(self, attack_type: AttackType, **kwargs) -> Dict[str, Any]:
        """Exécute une attaque unique avec les paramètres de furtivité"""
        attack = self.attacks[attack_type]
        
        # Injecter la configuration furtive
        stealth_kwargs = {
            'delay_between_requests': self.stealth_config['delay_between_requests'],
            'max_threads': self.stealth_config['max_threads'],
            'stealth_headers': self.stealth_config.get('stealth_headers', False),
            'random_delays': self.stealth_config['random_delays']
        }
        
        # Ajouter la configuration APT
        if self.stealth_level == StealthLevel.APT:
            stealth_kwargs.update({
                'human_behavior': self.apt_config.human_behavior,
                'ip_rotation': self.apt_config.ip_rotation,
                'apt_mode': True
            })
        
        # Fusionner avec les kwargs existants
        kwargs.update(stealth_kwargs)
        
        start_time = time.time()
        
        try:
            result = attack.scan(self.target, **kwargs)
            duration = time.time() - start_time
            
            # Logging discret
            if self.apt_config.stealth_logging:
                print(f"   ✓ Terminé en {duration:.1f}s")
            
            result['duration'] = duration
            result['stealth_level'] = self.stealth_level.value
            
            # Ajouter au journal
            self.attack_logs.append({
                'timestamp': start_time,
                'attack_type': attack_type.value,
                'duration': duration,
                'success': result.get('vulnerable', False) or bool(result.get('found_credentials'))
            })
            
            return result
            
        except Exception as e:
            print(f"   ✗ Erreur: {str(e)}")
            return {'error': str(e), 'vulnerable': False}
    
    def run_all(self, **kwargs) -> Dict[str, Any]:
        """
        Exécute tous les types d'attaques
        
        Args:
            **kwargs: Options de configuration
        """
        all_attacks = list(AttackType)
        return self.run_selected(all_attacks, **kwargs)
    
    def run_apt_operation(self, **kwargs) -> Dict[str, Any]:
        """
        Exécute une opération complète style APT
        Combine plusieurs attaques avec un comportement furtif avancé
        """
        print("\n🎭 DÉBUT DE L'OPÉRATION APT")
        print("=" * 60)
        
        # Configuration APT
        original_stealth = self.stealth_level
        self.stealth_level = StealthLevel.APT
        self._setup_stealth()
        
        # Stratégie d'attaque APT typique
        apt_attack_order = [
            AttackType.PASSWORD_SPRAYING,      # D'abord discret
            AttackType.BRUTE_FORCE,            # Plus agressif
            AttackType.CREDENTIAL_STUFFING,    # Utiliser les credentials trouvés
            AttackType.MFA_BYPASS,             # Contourner MFA
            AttackType.PRIVILEGE_ESCALATION,   # Élévation
            AttackType.RACE_CONDITION          # Exploitation finale
        ]
        
        # Journal APT
        apt_log = {
            'operation_start': time.time(),
            'target': self.target,
            'stealth_level': 'APT',
            'attack_order': [at.value for at in apt_attack_order]
        }
        
        # Exécuter les attaques
        results = self.run_selected(apt_attack_order, **kwargs)
        
        # Ajouter les métadonnées APT
        results['apt_metadata'] = {
            'operation_duration': time.time() - apt_log['operation_start'],
            'total_attacks': len(apt_attack_order),
            'successful_attacks': sum(1 for r in results.values() if r.get('vulnerable')),
            'stealth_level': 'APT'
        }
        
        # Restaurer le niveau de furtivité original
        self.stealth_level = original_stealth
        self._setup_stealth()
        
        print("\n🎭 OPÉRATION APT TERMINÉE")
        self._print_apt_summary(results['apt_metadata'])
        
        return results
    
    def _print_summary(self):
        """Affiche un résumé des vulnérabilités trouvées"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES ATTAQUES SUR L'AUTHENTIFICATION")
        print("=" * 60)
        
        total_found = 0
        critical_findings = []
        
        for attack_type, result in self.results.items():
            if not result:
                continue
                
            # Credentials trouvés
            for cred_key in ['found_credentials', 'compromised_credentials']:
                if cred_key in result and result[cred_key]:
                    creds = result[cred_key]
                    total_found += len(creds)
                    critical_findings.append({
                        'type': attack_type,
                        'severity': 'CRITICAL',
                        'details': f"{len(creds)} credentials compromis"
                    })
                    print(f"\n🔴 CRITICAL - {attack_type.replace('_', ' ').title()}: {len(creds)} credentials")
                    for cred in creds[:3]:
                        print(f"   - {cred.get('username', 'unknown')}:{cred.get('password', 'unknown')}")
            
            # Vulnérabilités
            if result.get('vulnerable'):
                total_found += 1
                severity = result.get('severity', 'HIGH')
                critical_findings.append({
                    'type': attack_type,
                    'severity': severity,
                    'details': result.get('description', 'Vulnérabilité détectée')
                })
                icon = "🔴" if severity == "CRITICAL" else "🟠"
                print(f"\n{icon} {severity} - {attack_type.replace('_', ' ').title()}: {result.get('description', 'Vulnérabilité détectée')}")
        
        if total_found == 0:
            print("\n✅ Aucune vulnérabilité d'authentification détectée")
        else:
            print(f"\n📈 Total vulnérabilités: {total_found}")
            print(f"⚠️  Criticités: {len([f for f in critical_findings if f['severity'] == 'CRITICAL'])}")
    
    def _print_apt_summary(self, apt_metadata: Dict):
        """Affiche le résumé de l'opération APT"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE L'OPÉRATION APT")
        print("=" * 60)
        print(f"⏱️  Durée totale: {apt_metadata['operation_duration']:.1f}s")
        print(f"🎯 Attaques exécutées: {apt_metadata['total_attacks']}")
        print(f"✅ Succès: {apt_metadata['successful_attacks']}")
        print(f"🕵️ Niveau furtif: {apt_metadata['stealth_level']}")
    
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
        return {
            'target': self.target,
            'stealth_level': self.stealth_level.value,
            'total_attacks': len(self.results),
            'vulnerabilities_found': sum(1 for r in self.results.values() if r.get('vulnerable')),
            'compromised_credentials': sum(
                len(r.get('found_credentials', [])) 
                for r in self.results.values()
            ),
            'attack_details': self.results,
            'logs': self.attack_logs
        }


# Fonctions utilitaires pour l'utilisation du module
def create_apt_session(target: str) -> AuthenticationAttackManager:
    """Crée une session APT complète"""
    return AuthenticationAttackManager(target, stealth_level=StealthLevel.APT)


def quick_assessment(target: str) -> AuthenticationAttackManager:
    """Évaluation rapide (peu discret)"""
    return AuthenticationAttackManager(target, stealth_level=StealthLevel.LOW)


def stealth_assessment(target: str) -> AuthenticationAttackManager:
    """Évaluation discrète"""
    return AuthenticationAttackManager(target, stealth_level=StealthLevel.HIGH)


__all__ = [
    'AuthenticationAttackManager',
    'AttackType',
    'StealthLevel',
    'APTConfig',
    'BruteForce',
    'CredentialStuffing',
    'PasswordSpraying',
    'MFABypass',
    'PrivilegeEscalation',
    'RaceCondition',
    'create_apt_session',
    'quick_assessment',
    'stealth_assessment'
]