#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Attack Selector pour RedForge
Sélection intelligente des attaques en fonction du contexte et de la cible
Version avec support APT, scoring et adaptabilité
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import random
from collections import defaultdict


class AttackCategory(Enum):
    """Catégories d'attaques"""
    INJECTION = "injection"
    SESSION = "session"
    CROSS_SITE = "cross_site"
    AUTHENTICATION = "authentication"
    FILE_SYSTEM = "file_system"
    INFRASTRUCTURE = "infrastructure"
    INTEGRITY = "integrity"
    ADVANCED = "advanced"


class AttackSeverity(Enum):
    """Sévérité des attaques"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AttackComplexity(Enum):
    """Complexité d'exécution"""
    SIMPLE = "simple"       # Requête unique
    MODERATE = "moderate"   # Plusieurs requêtes
    COMPLEX = "complex"     # Multi-étapes
    ADVANCED = "advanced"   # Très complexe


class DetectionRisk(Enum):
    """Risque de détection"""
    VERY_LOW = "very_low"    # Quasi indétectable
    LOW = "low"              # Faible risque
    MEDIUM = "medium"        # Risque modéré
    HIGH = "high"            # Risque élevé
    VERY_HIGH = "very_high"  # Très risqué


@dataclass
class Attack:
    """Définition d'une attaque"""
    id: str
    name: str
    category: AttackCategory
    severity: AttackSeverity
    complexity: AttackComplexity
    detection_risk: DetectionRisk
    prerequisites: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    weight: int = 1  # Poids pour la sélection
    apt_optimized: bool = False  # Optimisé pour APT


class AttackSelector:
    """
    Sélecteur intelligent d'attaques
    Choisit les attaques les plus pertinentes selon le contexte
    """
    
    def __init__(self):
        """Initialise le sélecteur d'attaques"""
        self.attacks: Dict[str, Attack] = {}
        self._load_attacks()
        self.selection_history: List[Dict] = []
        self.context_cache: Dict[str, Any] = {}
    
    def _load_attacks(self):
        """Charge la base de données des attaques"""
        
        # Injection Attacks
        self._register_attack(Attack(
            id="sql_injection_error",
            name="SQL Injection (Error Based)",
            category=AttackCategory.INJECTION,
            severity=AttackSeverity.CRITICAL,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.MEDIUM,
            tags=["sql", "database", "error_based"],
            parameters={"level": 3, "risk": 2},
            weight=10
        ))
        
        self._register_attack(Attack(
            id="sql_injection_blind",
            name="SQL Injection (Blind)",
            category=AttackCategory.INJECTION,
            severity=AttackSeverity.CRITICAL,
            complexity=AttackComplexity.COMPLEX,
            detection_risk=DetectionRisk.LOW,
            tags=["sql", "database", "time_based"],
            parameters={"level": 2, "risk": 1, "techniques": "T"},
            apt_optimized=True,
            weight=8
        ))
        
        self._register_attack(Attack(
            id="nosql_injection",
            name="NoSQL Injection",
            category=AttackCategory.INJECTION,
            severity=AttackSeverity.HIGH,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.MEDIUM,
            tags=["nosql", "mongodb", "json"],
            parameters={"level": 2},
            weight=7
        ))
        
        self._register_attack(Attack(
            id="command_injection",
            name="Command Injection",
            category=AttackCategory.INJECTION,
            severity=AttackSeverity.CRITICAL,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.HIGH,
            tags=["rce", "os", "shell"],
            parameters={},
            weight=9
        ))
        
        # XSS Attacks
        self._register_attack(Attack(
            id="xss_reflected",
            name="XSS Reflected",
            category=AttackCategory.CROSS_SITE,
            severity=AttackSeverity.HIGH,
            complexity=AttackComplexity.SIMPLE,
            detection_risk=DetectionRisk.MEDIUM,
            tags=["xss", "reflected", "client_side"],
            parameters={"level": 2},
            weight=7
        ))
        
        self._register_attack(Attack(
            id="xss_stored",
            name="XSS Stored",
            category=AttackCategory.CROSS_SITE,
            severity=AttackSeverity.CRITICAL,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.LOW,
            tags=["xss", "stored", "persistent"],
            parameters={"level": 3},
            apt_optimized=True,
            weight=9
        ))
        
        self._register_attack(Attack(
            id="xss_dom",
            name="DOM XSS",
            category=AttackCategory.CROSS_SITE,
            severity=AttackSeverity.HIGH,
            complexity=AttackComplexity.COMPLEX,
            detection_risk=DetectionRisk.LOW,
            tags=["xss", "dom", "client_side"],
            parameters={"level": 2},
            apt_optimized=True,
            weight=6
        ))
        
        # CSRF Attacks
        self._register_attack(Attack(
            id="csrf",
            name="CSRF",
            category=AttackCategory.CROSS_SITE,
            severity=AttackSeverity.HIGH,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.LOW,
            tags=["csrf", "state_changing"],
            parameters={},
            apt_optimized=True,
            weight=7
        ))
        
        # Session Attacks
        self._register_attack(Attack(
            id="session_hijacking",
            name="Session Hijacking",
            category=AttackCategory.SESSION,
            severity=AttackSeverity.CRITICAL,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.MEDIUM,
            prerequisites=["valid_session"],
            tags=["session", "cookie", "stealing"],
            parameters={},
            weight=8
        ))
        
        self._register_attack(Attack(
            id="session_fixation",
            name="Session Fixation",
            category=AttackCategory.SESSION,
            severity=AttackSeverity.HIGH,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.MEDIUM,
            tags=["session", "fixation"],
            parameters={},
            weight=6
        ))
        
        self._register_attack(Attack(
            id="jwt_attack",
            name="JWT Attack",
            category=AttackCategory.SESSION,
            severity=AttackSeverity.CRITICAL,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.LOW,
            tags=["jwt", "token", "authentication"],
            parameters={},
            apt_optimized=True,
            weight=8
        ))
        
        # Authentication Attacks
        self._register_attack(Attack(
            id="bruteforce",
            name="Bruteforce",
            category=AttackCategory.AUTHENTICATION,
            severity=AttackSeverity.HIGH,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.HIGH,
            tags=["bruteforce", "password", "rate_limiting"],
            parameters={"threads": 10, "delay": 1},
            weight=6
        ))
        
        self._register_attack(Attack(
            id="password_spraying",
            name="Password Spraying",
            category=AttackCategory.AUTHENTICATION,
            severity=AttackSeverity.HIGH,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.LOW,
            tags=["password", "spraying", "stealth"],
            parameters={"delay": 5},
            apt_optimized=True,
            weight=7
        ))
        
        self._register_attack(Attack(
            id="mfa_bypass",
            name="MFA Bypass",
            category=AttackCategory.AUTHENTICATION,
            severity=AttackSeverity.CRITICAL,
            complexity=AttackComplexity.ADVANCED,
            detection_risk=DetectionRisk.LOW,
            tags=["mfa", "2fa", "bypass"],
            parameters={},
            apt_optimized=True,
            weight=9
        ))
        
        # File System Attacks
        self._register_attack(Attack(
            id="lfi",
            name="Local File Inclusion",
            category=AttackCategory.FILE_SYSTEM,
            severity=AttackSeverity.HIGH,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.MEDIUM,
            tags=["lfi", "file_inclusion", "path_traversal"],
            parameters={"depth": 5},
            weight=7
        ))
        
        self._register_attack(Attack(
            id="rfi",
            name="Remote File Inclusion",
            category=AttackCategory.FILE_SYSTEM,
            severity=AttackSeverity.CRITICAL,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.HIGH,
            tags=["rfi", "file_inclusion", "remote"],
            parameters={},
            weight=8
        ))
        
        self._register_attack(Attack(
            id="file_upload",
            name="Malicious File Upload",
            category=AttackCategory.FILE_SYSTEM,
            severity=AttackSeverity.CRITICAL,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.HIGH,
            tags=["upload", "webshell", "bypass"],
            parameters={"extensions": ["php", "jsp", "asp"]},
            weight=8
        ))
        
        # Infrastructure Attacks
        self._register_attack(Attack(
            id="port_scan",
            name="Port Scan",
            category=AttackCategory.INFRASTRUCTURE,
            severity=AttackSeverity.INFO,
            complexity=AttackComplexity.SIMPLE,
            detection_risk=DetectionRisk.MEDIUM,
            tags=["scan", "discovery", "recon"],
            parameters={"ports": "1-1000"},
            weight=5
        ))
        
        self._register_attack(Attack(
            id="waf_detection",
            name="WAF Detection",
            category=AttackCategory.INFRASTRUCTURE,
            severity=AttackSeverity.INFO,
            complexity=AttackComplexity.SIMPLE,
            detection_risk=DetectionRisk.LOW,
            tags=["waf", "detection", "bypass"],
            parameters={},
            apt_optimized=True,
            weight=4
        ))
        
        self._register_attack(Attack(
            id="subdomain_enum",
            name="Subdomain Enumeration",
            category=AttackCategory.INFRASTRUCTURE,
            severity=AttackSeverity.INFO,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.LOW,
            tags=["subdomain", "enumeration", "recon"],
            parameters={},
            apt_optimized=True,
            weight=6
        ))
        
        # Advanced Attacks
        self._register_attack(Attack(
            id="ssti",
            name="Server-Side Template Injection",
            category=AttackCategory.ADVANCED,
            severity=AttackSeverity.CRITICAL,
            complexity=AttackComplexity.ADVANCED,
            detection_risk=DetectionRisk.MEDIUM,
            tags=["ssti", "template", "rce"],
            parameters={"level": 3},
            weight=9
        ))
        
        self._register_attack(Attack(
            id="xxe",
            name="XXE Injection",
            category=AttackCategory.ADVANCED,
            severity=AttackSeverity.HIGH,
            complexity=AttackComplexity.MODERATE,
            detection_risk=DetectionRisk.MEDIUM,
            tags=["xxe", "xml", "entity"],
            parameters={},
            weight=7
        ))
        
        self._register_attack(Attack(
            id="ssrf",
            name="Server-Side Request Forgery",
            category=AttackCategory.ADVANCED,
            severity=AttackSeverity.HIGH,
            complexity=AttackComplexity.COMPLEX,
            detection_risk=DetectionRisk.LOW,
            tags=["ssrf", "request_forgery", "internal"],
            parameters={},
            apt_optimized=True,
            weight=7
        ))
    
    def _register_attack(self, attack: Attack):
        """Enregistre une attaque dans la base"""
        self.attacks[attack.id] = attack
    
    def select_attacks(self, context: Dict[str, Any], 
                       max_attacks: int = 10,
                       stealth_mode: bool = False,
                       apt_mode: bool = False) -> List[Attack]:
        """
        Sélectionne les attaques les plus pertinentes
        
        Args:
            context: Contexte de la cible
            max_attacks: Nombre maximum d'attaques
            stealth_mode: Mode furtif (favorise les attaques discrètes)
            apt_mode: Mode APT (favorise les attaques optimisées)
            
        Returns:
            Liste des attaques sélectionnées
        """
        scored_attacks = []
        
        for attack in self.attacks.values():
            score = self._calculate_score(attack, context, stealth_mode, apt_mode)
            if score > 0:
                scored_attacks.append((attack, score))
        
        # Trier par score décroissant
        scored_attacks.sort(key=lambda x: x[1], reverse=True)
        
        # Limiter le nombre
        selected = [attack for attack, _ in scored_attacks[:max_attacks]]
        
        # Enregistrer la sélection
        self.selection_history.append({
            "timestamp": time.time(),
            "context": context,
            "selected": [a.id for a in selected],
            "stealth_mode": stealth_mode,
            "apt_mode": apt_mode
        })
        
        return selected
    
    def _calculate_score(self, attack: Attack, context: Dict[str, Any],
                        stealth_mode: bool, apt_mode: bool) -> float:
        """
        Calcule le score de pertinence d'une attaque
        
        Args:
            attack: Attaque à évaluer
            context: Contexte
            stealth_mode: Mode furtif
            apt_mode: Mode APT
            
        Returns:
            Score de pertinence
        """
        score = attack.weight
        
        # Facteur de sévérité
        severity_factors = {
            AttackSeverity.CRITICAL: 1.5,
            AttackSeverity.HIGH: 1.2,
            AttackSeverity.MEDIUM: 1.0,
            AttackSeverity.LOW: 0.7,
            AttackSeverity.INFO: 0.5
        }
        score *= severity_factors.get(attack.severity, 1.0)
        
        # Mode furtif
        if stealth_mode:
            detection_factors = {
                DetectionRisk.VERY_LOW: 1.5,
                DetectionRisk.LOW: 1.3,
                DetectionRisk.MEDIUM: 1.0,
                DetectionRisk.HIGH: 0.7,
                DetectionRisk.VERY_HIGH: 0.4
            }
            score *= detection_factors.get(attack.detection_risk, 1.0)
        
        # Mode APT
        if apt_mode:
            if attack.apt_optimized:
                score *= 1.5
            # Favoriser les attaques à faible risque de détection
            if attack.detection_risk in [DetectionRisk.VERY_LOW, DetectionRisk.LOW]:
                score *= 1.3
            # Désavantager les attaques complexes en APT (plus de temps)
            if attack.complexity == AttackComplexity.COMPLEX:
                score *= 0.9
            elif attack.complexity == AttackComplexity.ADVANCED:
                score *= 0.8
        
        # Tags matching avec le contexte
        context_tags = context.get('tags', [])
        if context_tags:
            matching_tags = set(attack.tags) & set(context_tags)
            score *= (1 + len(matching_tags) * 0.2)
        
        # Technologies détectées
        technologies = context.get('technologies', [])
        tech_mapping = {
            'php': ['sql_injection', 'lfi', 'rfi', 'file_upload'],
            'python': ['ssti', 'command_injection'],
            'java': ['xxe', 'ssrf', 'jwt_attack'],
            'nodejs': ['ssti', 'command_injection'],
            'ruby': ['ssti'],
            'mysql': ['sql_injection_error', 'sql_injection_blind'],
            'postgresql': ['sql_injection_error', 'sql_injection_blind'],
            'mongodb': ['nosql_injection'],
            'wordpress': ['file_upload', 'lfi', 'xss_stored'],
            'drupal': ['sql_injection_error', 'xss_stored'],
            'joomla': ['lfi', 'xss_stored']
        }
        
        for tech in technologies:
            tech_lower = tech.lower()
            for key, attack_ids in tech_mapping.items():
                if key in tech_lower and attack.id in attack_ids:
                    score *= 1.3
                    break
        
        return round(score, 2)
    
    def select_by_category(self, category: AttackCategory, 
                          max_attacks: int = 5) -> List[Attack]:
        """
        Sélectionne les attaques d'une catégorie spécifique
        
        Args:
            category: Catégorie d'attaque
            max_attacks: Nombre maximum
            
        Returns:
            Liste des attaques
        """
        category_attacks = [
            a for a in self.attacks.values() 
            if a.category == category
        ]
        
        # Trier par poids
        category_attacks.sort(key=lambda x: x.weight, reverse=True)
        
        return category_attacks[:max_attacks]
    
    def select_by_tags(self, tags: List[str], max_attacks: int = 10) -> List[Attack]:
        """
        Sélectionne les attaques par tags
        
        Args:
            tags: Tags à rechercher
            max_attacks: Nombre maximum
            
        Returns:
            Liste des attaques
        """
        scored = []
        tag_set = set(tags)
        
        for attack in self.attacks.values():
            match_count = len(set(attack.tags) & tag_set)
            if match_count > 0:
                scored.append((attack, match_count))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [a for a, _ in scored[:max_attacks]]
    
    def get_attack(self, attack_id: str) -> Optional[Attack]:
        """
        Récupère une attaque par son ID
        
        Args:
            attack_id: ID de l'attaque
            
        Returns:
            Attaque ou None
        """
        return self.attacks.get(attack_id)
    
    def get_attacks_by_severity(self, severity: AttackSeverity) -> List[Attack]:
        """
        Récupère les attaques par sévérité
        
        Args:
            severity: Niveau de sévérité
            
        Returns:
            Liste des attaques
        """
        return [a for a in self.attacks.values() if a.severity == severity]
    
    def get_attacks_by_detection_risk(self, risk: DetectionRisk) -> List[Attack]:
        """
        Récupère les attaques par risque de détection
        
        Args:
            risk: Niveau de risque
            
        Returns:
            Liste des attaques
        """
        return [a for a in self.attacks.values() if a.detection_risk == risk]
    
    def get_apt_optimized(self) -> List[Attack]:
        """
        Récupère les attaques optimisées pour APT
        
        Returns:
            Liste des attaques APT
        """
        return [a for a in self.attacks.values() if a.apt_optimized]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du sélecteur
        
        Returns:
            Statistiques
        """
        stats = {
            "total_attacks": len(self.attacks),
            "by_category": defaultdict(int),
            "by_severity": defaultdict(int),
            "by_complexity": defaultdict(int),
            "by_detection_risk": defaultdict(int),
            "apt_optimized_count": 0,
            "selections_count": len(self.selection_history)
        }
        
        for attack in self.attacks.values():
            stats["by_category"][attack.category.value] += 1
            stats["by_severity"][attack.severity.value] += 1
            stats["by_complexity"][attack.complexity.value] += 1
            stats["by_detection_risk"][attack.detection_risk.value] += 1
            
            if attack.apt_optimized:
                stats["apt_optimized_count"] += 1
        
        return dict(stats)
    
    def suggest_for_target(self, target_info: Dict[str, Any]) -> List[Attack]:
        """
        Suggère des attaques pour une cible spécifique
        
        Args:
            target_info: Informations sur la cible
            
        Returns:
            Liste des attaques suggérées
        """
        context = {
            "tags": [],
            "technologies": target_info.get('technologies', []),
            "open_ports": target_info.get('open_ports', []),
            "has_login": target_info.get('has_login', False),
            "has_api": target_info.get('has_api', False),
            "has_forms": target_info.get('has_forms', False)
        }
        
        # Ajouter des tags basés sur les infos
        if target_info.get('has_login'):
            context['tags'].append('authentication')
        if target_info.get('has_api'):
            context['tags'].append('api')
        if target_info.get('has_forms'):
            context['tags'].append('forms')
        
        ports = target_info.get('open_ports', [])
        if 80 in ports or 443 in ports:
            context['tags'].append('web')
        if 22 in ports:
            context['tags'].append('ssh')
        if 3306 in ports:
            context['tags'].append('mysql')
        if 5432 in ports:
            context['tags'].append('postgresql')
        
        return self.select_attacks(context, max_attacks=15, apt_mode=True)
    
    def get_attack_chain(self, target_info: Dict[str, Any]) -> List[Attack]:
        """
        Génère une chaîne d'attaques logique
        
        Args:
            target_info: Informations sur la cible
            
        Returns:
            Chaîne d'attaques ordonnée
        """
        # Ordre logique des attaques
        suggested = self.suggest_for_target(target_info)
        
        # Trier par ordre d'exécution logique
        execution_order = [
            AttackCategory.INFRASTRUCTURE,   # Reconnaissance
            AttackCategory.AUTHENTICATION,   # Accès
            AttackCategory.INJECTION,        # Exploitation
            AttackCategory.SESSION,          # Session
            AttackCategory.CROSS_SITE,       # Client-side
            AttackCategory.FILE_SYSTEM,      # Fichiers
            AttackCategory.ADVANCED,         # Avancé
            AttackCategory.INTEGRITY         # Intégrité
        ]
        
        ordered = []
        for category in execution_order:
            category_attacks = [a for a in suggested if a.category == category]
            ordered.extend(category_attacks)
        
        return ordered


# Fonction utilitaire
def create_attack_plan(target_info: Dict[str, Any], 
                       stealth_level: str = "medium") -> List[Dict[str, Any]]:
    """
    Crée un plan d'attaque structuré
    
    Args:
        target_info: Informations sur la cible
        stealth_level: Niveau de furtivité (low, medium, high, apt)
        
    Returns:
        Plan d'attaque
    """
    selector = AttackSelector()
    
    apt_mode = (stealth_level == "apt")
    stealth_mode = (stealth_level in ["high", "apt"])
    
    attacks = selector.get_attack_chain(target_info)
    
    plan = []
    for attack in attacks:
        plan.append({
            "id": attack.id,
            "name": attack.name,
            "category": attack.category.value,
            "severity": attack.severity.value,
            "complexity": attack.complexity.value,
            "detection_risk": attack.detection_risk.value,
            "parameters": attack.parameters,
            "recommended": apt_mode and attack.apt_optimized
        })
    
    return plan


# Pour les tests
if __name__ == "__main__":
    import time
    
    selector = AttackSelector()
    
    # Statistiques
    stats = selector.get_statistics()
    print(f"Total attaques: {stats['total_attacks']}")
    print(f"Attaques APT: {stats['apt_optimized_count']}")
    
    # Sélection pour une cible
    target_info = {
        "technologies": ["PHP", "MySQL", "WordPress"],
        "open_ports": [80, 443, 22],
        "has_login": True,
        "has_forms": True
    }
    
    plan = create_attack_plan(target_info, stealth_level="apt")
    print(f"\nPlan d'attaque ({len(plan)} attaques):")
    for attack in plan[:10]:
        print(f"  - {attack['name']} ({attack['category']}) - {attack['detection_risk']}")