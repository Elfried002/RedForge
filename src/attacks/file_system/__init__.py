#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques sur le système de fichiers pour RedForge
Contient tous les types d'attaques liées aux fichiers (LFI, RFI, upload, etc.)
Version APT avec mode furtif et sélection avancée
"""

import time
import random
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.attacks.file_system.lfi_rfi import LFIRFIAttack
from src.attacks.file_system.file_upload import FileUploadAttack
from src.attacks.file_system.directory_traversal import DirectoryTraversal
from src.attacks.file_system.buffer_overflow import BufferOverflow
from src.attacks.file_system.path_normalization import PathNormalization
from src.attacks.file_system.zip_slip import ZipSlipAttack


class FileSystemAttackType(Enum):
    """Types d'attaques sur le système de fichiers disponibles"""
    LFI_RFI = "lfi_rfi"
    FILE_UPLOAD = "file_upload"
    DIRECTORY_TRAVERSAL = "directory_traversal"
    BUFFER_OVERFLOW = "buffer_overflow"
    PATH_NORMALIZATION = "path_normalization"
    ZIP_SLIP = "zip_slip"


class StealthLevel(Enum):
    """Niveaux de furtivité"""
    LOW = "low"          # Rapide, peu discret
    MEDIUM = "medium"    # Équilibré
    HIGH = "high"        # Très discret, lent
    APT = "apt"          # Ultra discret, style APT


@dataclass
class FileSystemAPTConfig:
    """Configuration pour les opérations APT sur le système de fichiers"""
    # Délais entre les attaques (secondes)
    delay_between_attacks: tuple = (30, 180)
    # Jitter pour les délais
    jitter: float = 0.3
    # Pauses aléatoires pendant les scans
    random_pauses: bool = True
    # Éviter les patterns de détection
    avoid_detection_patterns: bool = True
    # Scan progressif (du moins au plus agressif)
    progressive_scanning: bool = True
    # Logging discret
    stealth_logging: bool = True
    # Rotation des User-Agents
    rotate_user_agents: bool = True
    # Taille maximale des fichiers pour les tests (octets)
    max_test_file_size: int = 1024 * 1024  # 1MB


class FileSystemAttackManager:
    """
    Gestionnaire central des attaques sur le système de fichiers
    Supporte la sélection multiple, le mode furtif et les opérations APT
    """
    
    def __init__(self, target: str, stealth_level: StealthLevel = StealthLevel.LOW):
        """
        Initialise le gestionnaire d'attaques sur le système de fichiers
        
        Args:
            target: Cible des attaques (URL ou chemin)
            stealth_level: Niveau de furtivité à utiliser
        """
        self.target = target
        self.stealth_level = stealth_level
        self.results = {}
        self.attack_logs = []
        
        # Initialiser les différents moteurs d'attaque
        self.attacks = {
            FileSystemAttackType.LFI_RFI: LFIRFIAttack(),
            FileSystemAttackType.FILE_UPLOAD: FileUploadAttack(),
            FileSystemAttackType.DIRECTORY_TRAVERSAL: DirectoryTraversal(),
            FileSystemAttackType.BUFFER_OVERFLOW: BufferOverflow(),
            FileSystemAttackType.PATH_NORMALIZATION: PathNormalization(),
            FileSystemAttackType.ZIP_SLIP: ZipSlipAttack()
        }
        
        # Configurer la furtivité
        self._setup_stealth()
        
        # Configuration APT par défaut
        self.apt_config = FileSystemAPTConfig()
        
        # User agents pour rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        ]
    
    def _setup_stealth(self):
        """Configure les paramètres de furtivité"""
        stealth_configs = {
            StealthLevel.LOW: {
                'delay_between_requests': (0.1, 0.3),
                'delay_between_attacks': (1, 5),
                'max_threads': 20,
                'random_delays': False,
                'stealth_headers': False,
                'max_payloads': 100,
                'depth': 'full'
            },
            StealthLevel.MEDIUM: {
                'delay_between_requests': (0.5, 1.5),
                'delay_between_attacks': (5, 15),
                'max_threads': 10,
                'random_delays': True,
                'stealth_headers': True,
                'max_payloads': 50,
                'depth': 'standard'
            },
            StealthLevel.HIGH: {
                'delay_between_requests': (2, 5),
                'delay_between_attacks': (15, 45),
                'max_threads': 3,
                'random_delays': True,
                'stealth_headers': True,
                'max_payloads': 25,
                'depth': 'light'
            },
            StealthLevel.APT: {
                'delay_between_requests': (5, 15),
                'delay_between_attacks': (30, 180),
                'max_threads': 1,
                'random_delays': True,
                'stealth_headers': True,
                'max_payloads': 15,
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
            
        print(f"\n🕵️ Mode furtif système de fichiers: {self.stealth_level.value.upper()}")
        print(f"   - Délai entre requêtes: {self.stealth_config['delay_between_requests']}s")
        print(f"   - Délai entre attaques: {self.stealth_config['delay_between_attacks']}s")
        print(f"   - Threads max: {self.stealth_config['max_threads']}")
        print(f"   - Payloads max: {self.stealth_config['max_payloads']}")
        print(f"   - Profondeur scan: {self.stealth_config['depth']}")
    
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
    
    def _get_stealth_headers(self) -> Dict[str, str]:
        """Génère des headers furtifs pour les requêtes"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        if self.apt_config.rotate_user_agents:
            headers['User-Agent'] = random.choice(self.user_agents)
        
        if self.stealth_config.get('stealth_headers'):
            headers['Cache-Control'] = 'no-cache'
            headers['Pragma'] = 'no-cache'
        
        return headers
    
    def select_attacks(self, attack_types: List[FileSystemAttackType]) -> List[FileSystemAttackType]:
        """
        Sélectionne les attaques à exécuter
        
        Args:
            attack_types: Liste des types d'attaques à exécuter
            
        Returns:
            Liste des attaques sélectionnées
        """
        available = [at for at in attack_types if at in self.attacks]
        
        if not available:
            print("⚠️ Aucune attaque sur le système de fichiers valide sélectionnée")
            return []
        
        print(f"\n🎯 Attaques sur le système de fichiers sélectionnées: {len(available)}")
        for attack in available:
            print(f"   - {attack.value.replace('_', ' ').title()}")
        
        return available
    
    def run_selected(self, attack_types: List[FileSystemAttackType], **kwargs) -> Dict[str, Any]:
        """
        Exécute les types d'attaques sélectionnés sur le système de fichiers
        
        Args:
            attack_types: Liste des attaques à exécuter
            **kwargs: Options de configuration
                - params: Paramètres à tester pour LFI
                - upload_url: URL d'upload de fichiers
                - traversal_depth: Profondeur de traversal
                - depth: Profondeur du scan
        """
        selected = self.select_attacks(attack_types)
        
        if not selected:
            return {'error': 'No attacks selected'}
        
        print(f"\n📁 ATTAQUES SUR LE SYSTÈME DE FICHIERS sur {self.target}")
        print(f"🎭 Mode: {self.stealth_level.value.upper()}")
        print("=" * 60)
        
        # Ajouter les headers furtifs aux kwargs
        kwargs['stealth_headers'] = self._get_stealth_headers()
        kwargs['stealth_config'] = self.stealth_config
        kwargs['apt_mode'] = (self.stealth_level == StealthLevel.APT)
        kwargs['max_payloads'] = self.stealth_config['max_payloads']
        
        # Exécuter les attaques selon la stratégie
        if self.apt_config.progressive_scanning and self.stealth_level == StealthLevel.APT:
            results = self._run_progressive_scan(selected, **kwargs)
        else:
            results = self._run_sequential_scan(selected, **kwargs)
        
        # Résumé
        self._print_summary()
        
        return results
    
    def _run_sequential_scan(self, selected: List[FileSystemAttackType], **kwargs) -> Dict[str, Any]:
        """Exécute les attaques séquentiellement"""
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
    
    def _run_progressive_scan(self, selected: List[FileSystemAttackType], **kwargs) -> Dict[str, Any]:
        """
        Exécute un scan progressif pour mode APT
        Commence par les attaques passives, puis actives
        """
        results = {}
        
        # Classification des attaques par agressivité
        passive_attacks = [
            FileSystemAttackType.DIRECTORY_TRAVERSAL,
            FileSystemAttackType.PATH_NORMALIZATION
        ]
        
        semi_active_attacks = [
            FileSystemAttackType.LFI_RFI,
            FileSystemAttackType.ZIP_SLIP
        ]
        
        active_attacks = [
            FileSystemAttackType.FILE_UPLOAD,
            FileSystemAttackType.BUFFER_OVERFLOW
        ]
        
        layers = [
            ("Passive", passive_attacks),
            ("Semi-active", semi_active_attacks),
            ("Active", active_attacks)
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
    
    def _run_single_attack(self, attack_type: FileSystemAttackType, **kwargs) -> Dict[str, Any]:
        """Exécute une attaque unique avec les paramètres de furtivité"""
        attack = self.attacks[attack_type]
        
        # Ajuster les paramètres selon le niveau de furtivité
        scan_kwargs = kwargs.copy()
        scan_kwargs['level'] = self._get_attack_level()
        scan_kwargs['depth'] = self.stealth_config['depth']
        scan_kwargs['max_payloads'] = self.stealth_config['max_payloads']
        
        if self.stealth_config.get('stealth_headers'):
            scan_kwargs['headers'] = self._get_stealth_headers()
        
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
        Exécute tous les types d'attaques sur le système de fichiers
        
        Args:
            **kwargs: Options de configuration
        """
        all_attacks = list(FileSystemAttackType)
        return self.run_selected(all_attacks, **kwargs)
    
    def run_apt_operation(self, **kwargs) -> Dict[str, Any]:
        """
        Exécute une opération complète style APT pour les attaques sur le système de fichiers
        """
        print("\n🎭 DÉBUT DE L'OPÉRATION APT - SYSTÈME DE FICHIERS")
        print("=" * 60)
        
        # Configuration APT
        original_stealth = self.stealth_level
        self.stealth_level = StealthLevel.APT
        self._setup_stealth()
        
        # Stratégie d'attaque APT typique pour système de fichiers
        apt_attack_order = [
            FileSystemAttackType.DIRECTORY_TRAVERSAL,  # D'abord passif
            FileSystemAttackType.PATH_NORMALIZATION,   # Détection de failles
            FileSystemAttackType.LFI_RFI,              # Inclusion de fichiers
            FileSystemAttackType.ZIP_SLIP,             # Extraction malveillante
            FileSystemAttackType.FILE_UPLOAD,          # Upload de fichiers
            FileSystemAttackType.BUFFER_OVERFLOW       # Exploitation avancée
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
        total_vulns = 0
        for r in results.values():
            if isinstance(r, dict):
                total_vulns += len(r.get('vulnerabilities', []))
        
        results['apt_metadata'] = {
            'operation_duration': time.time() - apt_log['operation_start'],
            'total_attacks': len(apt_attack_order),
            'total_vulnerabilities': total_vulns,
            'stealth_level': 'APT',
            'progressive_scan': self.apt_config.progressive_scanning
        }
        
        # Restaurer le niveau de furtivité original
        self.stealth_level = original_stealth
        self._setup_stealth()
        
        print("\n🎭 OPÉRATION APT - SYSTÈME DE FICHIERS TERMINÉE")
        self._print_apt_summary(results['apt_metadata'])
        
        return results
    
    def _print_summary(self):
        """Affiche un résumé des vulnérabilités trouvées"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES ATTAQUES SUR LE SYSTÈME DE FICHIERS")
        print("=" * 60)
        
        total_vulnerabilities = []
        critical_count = 0
        high_count = 0
        medium_count = 0
        
        for attack_type, result in self.results.items():
            if not result or 'vulnerabilities' not in result:
                continue
            
            vulnerabilities = result.get('vulnerabilities', [])
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'MEDIUM')
                if severity == 'CRITICAL':
                    critical_count += 1
                elif severity == 'HIGH':
                    high_count += 1
                else:
                    medium_count += 1
                
                total_vulnerabilities.append({
                    'type': attack_type.replace('_', ' ').upper(),
                    'details': vuln.get('details', vuln.get('parameter', 'unknown')),
                    'severity': severity
                })
        
        if total_vulnerabilities:
            print(f"\n⚠️  {len(total_vulnerabilities)} vulnérabilité(s) sur le système de fichiers détectée(s):")
            print(f"   🔴 CRITICAL: {critical_count}")
            print(f"   🟠 HIGH: {high_count}")
            print(f"   🟡 MEDIUM: {medium_count}")
            
            print("\nDétails:")
            for vuln in total_vulnerabilities[:10]:
                icon = "🔴" if vuln['severity'] == "CRITICAL" else "🟠" if vuln['severity'] == "HIGH" else "🟡"
                print(f"   {icon} [{vuln['severity']}] {vuln['type']}: {vuln['details'][:80]}")
            
            if len(total_vulnerabilities) > 10:
                print(f"   ... et {len(total_vulnerabilities) - 10} autres")
        else:
            print("\n✅ Aucune vulnérabilité sur le système de fichiers détectée")
    
    def _print_apt_summary(self, apt_metadata: Dict):
        """Affiche le résumé de l'opération APT"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE L'OPÉRATION APT - SYSTÈME DE FICHIERS")
        print("=" * 60)
        print(f"⏱️  Durée totale: {apt_metadata['operation_duration']:.1f}s")
        print(f"🎯 Attaques exécutées: {apt_metadata['total_attacks']}")
        print(f"✅ Vulnérabilités trouvées: {apt_metadata['total_vulnerabilities']}")
        print(f"🕵️ Niveau furtif: {apt_metadata['stealth_level']}")
        print(f"📊 Scan progressif: {apt_metadata['progressive_scan']}")
    
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
    
    def generate_exploits(self, output_dir: str = "./exploits"):
        """
        Génère des fichiers d'exploit pour les vulnérabilités trouvées
        
        Args:
            output_dir: Répertoire de sortie pour les exploits
        """
        os.makedirs(output_dir, exist_ok=True)
        
        exploits_generated = []
        
        # Générer exploits LFI/RFI
        lfi_result = self.results.get('lfi_rfi', {})
        if lfi_result.get('vulnerabilities'):
            if hasattr(self.attacks[FileSystemAttackType.LFI_RFI], 'generate_exploit'):
                exploit = self.attacks[FileSystemAttackType.LFI_RFI].generate_exploit()
                with open(f"{output_dir}/lfi_exploit.txt", 'w') as f:
                    f.write(exploit)
                exploits_generated.append("lfi_exploit.txt")
        
        # Générer exploits d'upload
        upload_result = self.results.get('file_upload', {})
        if upload_result.get('vulnerabilities'):
            if hasattr(self.attacks[FileSystemAttackType.FILE_UPLOAD], 'generate_malicious_file'):
                malicious_file = self.attacks[FileSystemAttackType.FILE_UPLOAD].generate_malicious_file()
                with open(f"{output_dir}/malicious.php", 'wb') as f:
                    f.write(malicious_file)
                exploits_generated.append("malicious.php")
        
        # Générer rapport détaillé
        if exploits_generated:
            print(f"\n💾 Exploits générés dans {output_dir}:")
            for exploit in exploits_generated:
                print(f"   - {exploit}")
        else:
            print(f"\nℹ️ Aucun exploit généré (aucune vulnérabilité trouvée)")


# Fonctions utilitaires pour l'utilisation du module
def create_apt_file_system_session(target: str) -> FileSystemAttackManager:
    """Crée une session APT pour les attaques sur le système de fichiers"""
    return FileSystemAttackManager(target, stealth_level=StealthLevel.APT)


def quick_file_system_assessment(target: str) -> FileSystemAttackManager:
    """Évaluation rapide du système de fichiers (peu discret)"""
    return FileSystemAttackManager(target, stealth_level=StealthLevel.LOW)


def stealth_file_system_assessment(target: str) -> FileSystemAttackManager:
    """Évaluation discrète du système de fichiers"""
    return FileSystemAttackManager(target, stealth_level=StealthLevel.HIGH)


__all__ = [
    'FileSystemAttackManager',
    'FileSystemAttackType',
    'StealthLevel',
    'FileSystemAPTConfig',
    'LFIRFIAttack',
    'FileUploadAttack',
    'DirectoryTraversal',
    'BufferOverflow',
    'PathNormalization',
    'ZipSlipAttack',
    'create_apt_file_system_session',
    'quick_file_system_assessment',
    'stealth_file_system_assessment'
]