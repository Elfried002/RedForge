#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques avancées pour RedForge
Contient tous les types d'attaques avancées (API, GraphQL, WebSocket, etc.)
Version: 2.0.0 - Support Multi-Attaque, Stealth & APT
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Imports conditionnels pour éviter les erreurs si les modules n'existent pas
try:
    from src.attacks.advanced.api_attacks import APIAttacks
except ImportError:
    APIAttacks = None

try:
    from src.attacks.advanced.graphql_attacks import GraphQLAttacks
except ImportError:
    GraphQLAttacks = None

try:
    from src.attacks.advanced.websocket_attacks import WebSocketAttacks
except ImportError:
    WebSocketAttacks = None

try:
    from src.attacks.advanced.deserialization import DeserializationAttack
except ImportError:
    DeserializationAttack = None

try:
    from src.attacks.advanced.browser_exploit import BrowserExploit
except ImportError:
    BrowserExploit = None

try:
    from src.attacks.advanced.microservices import MicroservicesAttack
except ImportError:
    MicroservicesAttack = None

try:
    from src.attacks.advanced.attack_chaining import AttackChaining
except ImportError:
    AttackChaining = None

# Import du module de couleurs
try:
    from src.utils.color_output import console
except ImportError:
    # Fallback si le module n'existe pas
    class Console:
        def print_header(self, msg): print(f"\n{'='*60}\n{msg}\n{'='*60}")
        def print_info(self, msg): print(f"[*] {msg}")
        def print_success(self, msg): print(f"[+] {msg}")
        def print_warning(self, msg): print(f"[!] {msg}")
        def print_error(self, msg): print(f"[-] {msg}")
    console = Console()


class AttackMode(Enum):
    """Modes d'attaque disponibles"""
    STANDARD = "standard"
    STEALTH = "stealth"
    AGGRESSIVE = "aggressive"
    APT = "apt"
    MULTI = "multi"


@dataclass
class AttackConfig:
    """Configuration d'une attaque"""
    enabled: bool = True
    stealth: bool = False
    timeout: int = 300
    threads: int = 10
    level: int = 2
    parameters: Dict[str, Any] = field(default_factory=dict)


class AdvancedAttackManager:
    """
    Gestionnaire central des attaques avancées
    Coordonne tous les types d'attaques avancées avec support multi-attaque, stealth et APT
    """
    
    def __init__(self, target: str):
        """
        Initialise le gestionnaire d'attaques avancées
        
        Args:
            target: Cible des attaques
        """
        self.target = target
        self.results: Dict[str, Any] = {}
        self.start_time = datetime.now()
        self.mode = AttackMode.STANDARD
        self.selected_attacks: List[str] = []
        
        # Initialiser les différents moteurs d'attaque (uniquement si disponibles)
        self.api_attacks = APIAttacks() if APIAttacks else None
        self.graphql_attacks = GraphQLAttacks() if GraphQLAttacks else None
        self.websocket_attacks = WebSocketAttacks() if WebSocketAttacks else None
        self.deserialization = DeserializationAttack() if DeserializationAttack else None
        self.browser_exploit = BrowserExploit() if BrowserExploit else None
        self.microservices = MicroservicesAttack() if MicroservicesAttack else None
        self.attack_chaining = AttackChaining() if AttackChaining else None
    
    def set_mode(self, mode: AttackMode):
        """
        Définit le mode d'attaque
        
        Args:
            mode: Mode d'attaque (standard, stealth, aggressive, apt, multi)
        """
        self.mode = mode
        console.print_info(f"Mode d'attaque: {mode.value}")
        
        # Ajuster la configuration selon le mode
        if mode == AttackMode.STEALTH:
            self._apply_stealth_config()
        elif mode == AttackMode.AGGRESSIVE:
            self._apply_aggressive_config()
        elif mode == AttackMode.APT:
            self._apply_apt_config()
    
    def select_attacks(self, attacks: List[str]):
        """
        Sélectionne les attaques à exécuter
        
        Args:
            attacks: Liste des attaques (format: "category.attack")
        """
        self.selected_attacks = attacks
        console.print_info(f"Attaques sélectionnées: {len(attacks)}")
        for attack in attacks[:5]:
            console.print_info(f"  - {attack}")
        if len(attacks) > 5:
            console.print_info(f"  ... et {len(attacks) - 5} autres")
    
    def _apply_stealth_config(self):
        """Applique la configuration du mode furtif"""
        console.print_info("🕵️ Activation du mode furtif")
        # Désactiver les scans agressifs
        # Ajouter des délais aléatoires
        # Rotation des User-Agents
        # Utiliser Tor/proxy si configuré
    
    def _apply_aggressive_config(self):
        """Applique la configuration du mode agressif"""
        console.print_info("⚡ Activation du mode agressif")
        # Augmenter les threads
        # Réduire les timeouts
        # Activer tous les scanners
    
    def _apply_apt_config(self):
        """Applique la configuration du mode APT"""
        console.print_info("🎯 Activation du mode APT")
        # Activer la persistance
        # Activer le mouvement latéral
        # Configurer les canaux C2
    
    def run_all(self, **kwargs) -> dict:
        """
        Exécute tous les types d'attaques avancées
        
        Args:
            **kwargs: Options de configuration
                - api_endpoints: Endpoints API à tester
                - graphql_endpoint: Endpoint GraphQL
                - websocket_url: URL WebSocket
                - chain_file: Fichier de configuration pour chaînage
                - deep_scan: Scan approfondi
                - timeout: Timeout global
                - mode: Mode d'attaque
                - selected_attacks: Liste des attaques sélectionnées
        """
        # Appliquer le mode si spécifié
        if kwargs.get('mode'):
            try:
                mode = AttackMode(kwargs['mode'])
                self.set_mode(mode)
            except ValueError:
                console.print_warning(f"Mode inconnu: {kwargs['mode']}")
        
        # Sélectionner les attaques si spécifiées
        if kwargs.get('selected_attacks'):
            self.select_attacks(kwargs['selected_attacks'])
        
        console.print_header(f"🚀 ATTAQUES AVANCÉES sur {self.target}")
        console.print_info(f"Mode: {self.mode.value}")
        
        # Filtrer les attaques selon la sélection
        selected = self.selected_attacks
        
        # API Attacks
        if self.api_attacks and (not selected or any(a.startswith('advanced.api') for a in selected)):
            console.print_info("🔌 Test des attaques API...")
            self.results['api_attacks'] = self.api_attacks.scan(
                self.target, **kwargs
            )
        else:
            if not selected or 'advanced.api' in selected:
                console.print_warning("🔌 Module API non disponible")
            self.results['api_attacks'] = {"error": "Module non disponible", "vulnerabilities": []}
        
        # GraphQL Attacks
        if self.graphql_attacks and kwargs.get('graphql_endpoint'):
            if not selected or any(a.startswith('advanced.graphql') for a in selected):
                console.print_info("📊 Test des attaques GraphQL...")
                self.results['graphql_attacks'] = self.graphql_attacks.scan(
                    kwargs['graphql_endpoint'], **kwargs
                )
            else:
                self.results['graphql_attacks'] = {"vulnerabilities": []}
        else:
            if kwargs.get('graphql_endpoint'):
                console.print_warning("📊 Module GraphQL non disponible")
            self.results['graphql_attacks'] = {"vulnerabilities": []}
        
        # WebSocket Attacks
        if self.websocket_attacks and kwargs.get('websocket_url'):
            if not selected or any(a.startswith('advanced.websocket') for a in selected):
                console.print_info("🔌 Test des attaques WebSocket...")
                self.results['websocket_attacks'] = self.websocket_attacks.scan(
                    kwargs['websocket_url'], **kwargs
                )
            else:
                self.results['websocket_attacks'] = {"vulnerabilities": []}
        else:
            if kwargs.get('websocket_url'):
                console.print_warning("🔌 Module WebSocket non disponible")
            self.results['websocket_attacks'] = {"vulnerabilities": []}
        
        # Deserialization Attacks
        if self.deserialization and (not selected or any(a.startswith('advanced.deserialization') for a in selected)):
            console.print_info("📦 Test des attaques de désérialisation...")
            self.results['deserialization'] = self.deserialization.scan(
                self.target, **kwargs
            )
        else:
            if not selected or 'advanced.deserialization' in selected:
                console.print_warning("📦 Module désérialisation non disponible")
            self.results['deserialization'] = {"vulnerable": False}
        
        # Browser Exploitation
        if self.browser_exploit and (not selected or any(a.startswith('advanced.browser') for a in selected)):
            console.print_info("🌐 Test de l'exploitation navigateur...")
            self.results['browser_exploit'] = self.browser_exploit.scan(
                self.target, **kwargs
            )
        else:
            if not selected or 'advanced.browser' in selected:
                console.print_warning("🌐 Module browser exploit non disponible")
            self.results['browser_exploit'] = {"vulnerable": False}
        
        # Microservices Attacks
        if self.microservices and (not selected or any(a.startswith('advanced.microservices') for a in selected)):
            console.print_info("🏗️ Test des attaques microservices...")
            self.results['microservices'] = self.microservices.scan(
                self.target, **kwargs
            )
        else:
            if not selected or 'advanced.microservices' in selected:
                console.print_warning("🏗️ Module microservices non disponible")
            self.results['microservices'] = {"vulnerabilities": []}
        
        # Attack Chaining
        if self.attack_chaining and (not selected or any(a.startswith('advanced.chaining') for a in selected)):
            console.print_info("⛓️ Test du chaînage d'attaques...")
            self.results['attack_chaining'] = self.attack_chaining.scan(
                self.target, **kwargs
            )
        else:
            if not selected or 'advanced.chaining' in selected:
                console.print_warning("⛓️ Module attack chaining non disponible")
            self.results['attack_chaining'] = {"chains": []}
        
        # Résumé
        self._print_summary()
        
        # Ajouter les métadonnées
        self.results['_metadata'] = {
            'target': self.target,
            'mode': self.mode.value,
            'selected_attacks': self.selected_attacks,
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration': str(datetime.now() - self.start_time),
            'modules_available': {
                'api': self.api_attacks is not None,
                'graphql': self.graphql_attacks is not None,
                'websocket': self.websocket_attacks is not None,
                'deserialization': self.deserialization is not None,
                'browser_exploit': self.browser_exploit is not None,
                'microservices': self.microservices is not None,
                'attack_chaining': self.attack_chaining is not None
            }
        }
        
        return self.results
    
    def run_selected(self, **kwargs) -> dict:
        """
        Exécute uniquement les attaques sélectionnées
        
        Args:
            **kwargs: Options de configuration
        """
        return self.run_all(**kwargs)
    
    def _print_summary(self):
        """Affiche un résumé des vulnérabilités trouvées"""
        console.print_header("📊 RÉSUMÉ DES ATTAQUES AVANCÉES")
        
        total_found = 0
        vulnerabilities_by_severity = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0,
            'INFO': 0
        }
        
        # API Attacks
        api_result = self.results.get('api_attacks', {})
        api_vulns = api_result.get('vulnerabilities', [])
        api_count = len(api_vulns)
        if api_count > 0:
            total_found += api_count
            console.print_success(f"🔌 API vulnérabilités: {api_count}")
            for vuln in api_vulns[:3]:
                severity = vuln.get('severity', 'MEDIUM').upper()
                if severity in vulnerabilities_by_severity:
                    vulnerabilities_by_severity[severity] += 1
                console.print_info(f"   - {vuln.get('type', 'Unknown')} ({severity})")
        
        # GraphQL
        gql_result = self.results.get('graphql_attacks', {})
        gql_vulns = gql_result.get('vulnerabilities', [])
        gql_count = len(gql_vulns)
        if gql_count > 0:
            total_found += gql_count
            console.print_success(f"📊 GraphQL vulnérabilités: {gql_count}")
            for vuln in gql_vulns[:3]:
                severity = vuln.get('severity', 'MEDIUM').upper()
                if severity in vulnerabilities_by_severity:
                    vulnerabilities_by_severity[severity] += 1
                console.print_info(f"   - {vuln.get('type', 'Unknown')} ({severity})")
        
        # WebSocket
        ws_result = self.results.get('websocket_attacks', {})
        ws_vulns = ws_result.get('vulnerabilities', [])
        ws_count = len(ws_vulns)
        if ws_count > 0:
            total_found += ws_count
            console.print_success(f"🔌 WebSocket vulnérabilités: {ws_count}")
            for vuln in ws_vulns[:3]:
                severity = vuln.get('severity', 'MEDIUM').upper()
                if severity in vulnerabilities_by_severity:
                    vulnerabilities_by_severity[severity] += 1
                console.print_info(f"   - {vuln.get('type', 'Unknown')} ({severity})")
        
        # Deserialization
        deser_result = self.results.get('deserialization', {})
        if deser_result.get('vulnerable'):
            total_found += 1
            vulnerabilities_by_severity['CRITICAL'] += 1
            console.print_warning("📦 Désérialisation vulnérable (CRITICAL)")
        
        # Browser Exploit
        browser_result = self.results.get('browser_exploit', {})
        if browser_result.get('vulnerable'):
            total_found += 1
            vulnerabilities_by_severity['HIGH'] += 1
            console.print_warning("🌐 Exploitation navigateur possible (HIGH)")
        
        # Microservices
        ms_result = self.results.get('microservices', {})
        ms_vulns = ms_result.get('vulnerabilities', [])
        ms_count = len(ms_vulns)
        if ms_count > 0:
            total_found += ms_count
            console.print_success(f"🏗️ Microservices vulnérabilités: {ms_count}")
            for vuln in ms_vulns[:3]:
                severity = vuln.get('severity', 'MEDIUM').upper()
                if severity in vulnerabilities_by_severity:
                    vulnerabilities_by_severity[severity] += 1
                console.print_info(f"   - {vuln.get('type', 'Unknown')} ({severity})")
        
        # Attack Chaining
        chain_result = self.results.get('attack_chaining', {})
        chain_count = len(chain_result.get('chains', []))
        if chain_count > 0:
            total_found += chain_count
            console.print_success(f"⛓️ Chaînes d'attaque possibles: {chain_count}")
            for chain in chain_result.get('chains', [])[:3]:
                console.print_info(f"   - {chain.get('name', 'Unknown')}")
        
        if total_found == 0:
            console.print_success("✅ Aucune vulnérabilité avancée détectée")
        else:
            console.print_warning(f"⚠️ TOTAL: {total_found} vulnérabilité(s) avancée(s) détectée(s)")
            console.print_info(f"   Par sévérité: CRITICAL={vulnerabilities_by_severity['CRITICAL']}, "
                             f"HIGH={vulnerabilities_by_severity['HIGH']}, "
                             f"MEDIUM={vulnerabilities_by_severity['MEDIUM']}, "
                             f"LOW={vulnerabilities_by_severity['LOW']}")
    
    def save_results(self, output_file: str) -> bool:
        """
        Sauvegarde les résultats au format JSON
        
        Args:
            output_file: Chemin du fichier de sortie
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=4, ensure_ascii=False, default=str)
            console.print_success(f"💾 Résultats sauvegardés dans {output_file}")
            return True
        except Exception as e:
            console.print_error(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé des résultats
        
        Returns:
            Dictionnaire contenant le résumé des vulnérabilités
        """
        summary = {
            "target": self.target,
            "mode": self.mode.value,
            "selected_attacks": self.selected_attacks,
            "total_vulnerabilities": 0,
            "by_category": {},
            "by_severity": {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
                "INFO": 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        for category, result in self.results.items():
            if category.startswith('_'):
                continue
            
            if isinstance(result, dict):
                vulns = result.get('vulnerabilities', [])
                if vulns:
                    summary['by_category'][category] = len(vulns)
                    summary['total_vulnerabilities'] += len(vulns)
                    
                    for vuln in vulns:
                        severity = vuln.get('severity', 'MEDIUM').upper()
                        if severity in summary['by_severity']:
                            summary['by_severity'][severity] += 1
                
                if result.get('vulnerable'):
                    summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
                    summary['total_vulnerabilities'] += 1
                    summary['by_severity']['HIGH'] += 1
        
        return summary
    
    def get_vulnerabilities_list(self) -> List[Dict[str, Any]]:
        """
        Retourne la liste de toutes les vulnérabilités trouvées
        
        Returns:
            Liste des vulnérabilités
        """
        vulnerabilities = []
        
        for category, result in self.results.items():
            if category.startswith('_'):
                continue
            
            if isinstance(result, dict):
                for vuln in result.get('vulnerabilities', []):
                    vuln['category'] = category
                    vulnerabilities.append(vuln)
                
                if result.get('vulnerable'):
                    vulnerabilities.append({
                        'category': category,
                        'type': 'vulnerable',
                        'severity': 'HIGH',
                        'details': result.get('details', 'Vulnérabilité détectée')
                    })
        
        return vulnerabilities


# Exports conditionnels
__all__ = [
    'AdvancedAttackManager',
    'AttackMode',
    'AttackConfig',
]

# Ajouter les classes uniquement si elles sont disponibles
if APIAttacks:
    __all__.append('APIAttacks')
if GraphQLAttacks:
    __all__.append('GraphQLAttacks')
if WebSocketAttacks:
    __all__.append('WebSocketAttacks')
if DeserializationAttack:
    __all__.append('DeserializationAttack')
if BrowserExploit:
    __all__.append('BrowserExploit')
if MicroservicesAttack:
    __all__.append('MicroservicesAttack')
if AttackChaining:
    __all__.append('AttackChaining')


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test rapide
    manager = AdvancedAttackManager("https://example.com")
    print("✅ Module d'attaques avancées chargé")
    
    # Test de sélection d'attaques
    manager.select_attacks(["advanced.api", "advanced.graphql", "advanced.deserialization"])
    
    # Test de changement de mode
    manager.set_mode(AttackMode.STEALTH)
    
    print(f"📦 Modules disponibles: {[m for m in [APIAttacks, GraphQLAttacks, WebSocketAttacks, DeserializationAttack, BrowserExploit, MicroservicesAttack, AttackChaining] if m]}")