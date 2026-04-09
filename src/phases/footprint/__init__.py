#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1: Footprinting - Reconnaissance et collecte d'informations
Cette phase collecte un maximum d'informations sur la cible sans être intrusif
Version avec support furtif, APT et orchestration avancée
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from src.phases.footprint.nmap_scanner import NmapScanner
from src.phases.footprint.whatweb_detector import WhatWebDetector
from src.phases.footprint.dns_enum import DNSEnumerator
from src.phases.footprint.subdomain_finder import SubdomainFinder
from src.phases.footprint.os_detector import OSDetector
from src.phases.footprint.certificate_scanner import CertificateScanner
from src.phases.footprint.waf_detector import WAFDetector
from src.core.stealth_engine import StealthEngine


class FootprintPhase:
    """
    Orchestrateur de la phase de reconnaissance
    Combine tous les modules de footprinting
    Supporte le mode furtif et APT
    """
    
    def __init__(self, target: str):
        """
        Initialise la phase de reconnaissance
        
        Args:
            target: Cible à analyser
        """
        self.target = target
        self.results = {}
        self.start_time = None
        self.stealth_mode = False
        self.apt_mode = False
        self.stealth_config = {}
        self.stealth_engine = StealthEngine()
        
        # Initialiser les modules
        self.nmap_scanner = NmapScanner()
        self.whatweb_detector = WhatWebDetector()
        self.dns_enum = DNSEnumerator()
        self.subdomain_finder = SubdomainFinder()
        self.os_detector = OSDetector()
        self.certificate_scanner = CertificateScanner()
        self.waf_detector = WAFDetector()
    
    def set_stealth_config(self, config: Dict[str, Any]):
        """
        Configure le mode furtif pour la reconnaissance
        
        Args:
            config: Configuration de furtivité
        """
        self.stealth_mode = config.get('enabled', False)
        self.apt_mode = config.get('apt_mode', False)
        self.stealth_config = config
        
        # Configurer le moteur de furtivité
        if self.stealth_mode:
            self.stealth_engine.set_delays(
                min_delay=config.get('delay_min', 1),
                max_delay=config.get('delay_max', 5),
                jitter=config.get('jitter', 0.3)
            )
            if self.apt_mode:
                self.stealth_engine.enable_apt_mode()
        
        # Propager la configuration aux modules
        for module in [self.nmap_scanner, self.whatweb_detector, self.dns_enum, 
                       self.subdomain_finder, self.os_detector, self.certificate_scanner,
                       self.waf_detector]:
            if hasattr(module, 'set_stealth_config'):
                module.set_stealth_config(config)
    
    def _apply_stealth_delay(self):
        """Applique un délai furtif entre les modules"""
        if self.stealth_mode:
            self.stealth_engine.apply_delay()
    
    def run(self, **kwargs) -> dict:
        """
        Exécute toutes les étapes de la phase footprint
        
        Args:
            **kwargs: Options de configuration
                - quick: Mode rapide (peu d'étapes)
                - full: Mode complet (toutes les étapes)
                - ports: Ports à scanner (pour Nmap)
                - dns_enum: Activer DNS enum
                - subdomains: Activer recherche sous-domaines
                - certificate: Scanner les certificats SSL
                - waf_detection: Détecter les WAF
        """
        self.start_time = time.time()
        
        mode = kwargs.get('mode', 'full')
        if self.apt_mode:
            mode = 'stealth'
            print(f"  🕵️ Mode APT activé - Reconnaissance discrète")
        
        mode_text = "APT" if self.apt_mode else "furtif" if self.stealth_mode else "normal"
        print(f"\n🔍 PHASE 1: FOOTPRINTING - Reconnaissance sur {self.target}")
        print(f"🎭 Mode: {mode_text.upper()}")
        print("=" * 60)
        
        results = {}
        
        # Étape 1: Scan Nmap
        print("\n📡 Scan Nmap...")
        if self.apt_mode:
            print("   (Mode APT: scan lent avec timing furtif)")
        
        if mode == 'quick':
            nmap_result = self.nmap_scanner.quick_scan(self.target, **kwargs)
        else:
            nmap_result = self.nmap_scanner.full_scan(self.target, **kwargs)
        results['nmap'] = nmap_result
        self._print_port_summary(nmap_result)
        
        self._apply_stealth_delay()
        
        # Étape 2: Détection technologies
        print("\n🔧 Détection des technologies web...")
        tech_result = self.whatweb_detector.detect(self.target, deep=(mode != 'quick'))
        results['technologies'] = tech_result
        self._print_tech_summary(tech_result)
        
        self._apply_stealth_delay()
        
        # Étape 3: Énumération DNS
        if kwargs.get('dns_enum', True) or mode == 'full':
            print("\n🌐 Énumération DNS...")
            dns_result = self.dns_enum.enumerate(self.target)
            results['dns'] = dns_result
            self._print_dns_summary(dns_result)
            self._apply_stealth_delay()
        
        # Étape 4: Recherche sous-domaines
        if kwargs.get('subdomains', True) or mode == 'full':
            print("\n🔎 Recherche de sous-domaines...")
            subdomain_result = self.subdomain_finder.find(self.target)
            results['subdomains'] = subdomain_result
            self._print_subdomain_summary(subdomain_result)
            self._apply_stealth_delay()
        
        # Étape 5: Détection OS
        if kwargs.get('os_detection', False) or mode == 'full':
            print("\n💻 Détection du système d'exploitation...")
            os_result = self.os_detector.detect(self.target)
            results['os'] = os_result
            if os_result.get('os'):
                print(f"   ✓ OS détecté: {os_result['os']}")
            self._apply_stealth_delay()
        
        # Étape 6: Scanner les certificats SSL
        if kwargs.get('certificate', True) or mode == 'full':
            print("\n🔒 Scan des certificats SSL...")
            cert_result = self.certificate_scanner.scan(self.target)
            results['certificate'] = cert_result
            if cert_result.get('valid'):
                print(f"   ✓ Certificat valide jusqu'au {cert_result.get('expiry_date', 'unknown')}")
            self._apply_stealth_delay()
        
        # Étape 7: Détection WAF
        if kwargs.get('waf_detection', True):
            print("\n🛡️ Détection des WAF...")
            waf_result = self.waf_detector.detect(self.target)
            results['waf'] = waf_result
            if waf_result.get('waf_detected'):
                print(f"   ✓ WAF détecté: {waf_result.get('waf_name', 'Unknown')}")
            self._apply_stealth_delay()
        
        self.results = results
        self._print_summary()
        
        return results
    
    def _print_port_summary(self, nmap_result: Dict):
        """Affiche un résumé du scan Nmap"""
        open_ports = nmap_result.get('open_ports', [])
        if open_ports:
            print(f"   ✓ {len(open_ports)} port(s) ouvert(s) trouvé(s)")
            if not self.apt_mode:
                ports_str = ', '.join(str(p) for p in open_ports[:10])
                print(f"     Ports: {ports_str}")
                if len(open_ports) > 10:
                    print(f"     ... et {len(open_ports) - 10} autres")
        else:
            print("   ✓ Aucun port ouvert trouvé")
    
    def _print_tech_summary(self, tech_result: Dict):
        """Affiche un résumé des technologies détectées"""
        technologies = tech_result.get('technologies', [])
        if technologies:
            print(f"   ✓ {len(technologies)} technologie(s) détectée(s)")
            if not self.apt_mode:
                for tech in technologies[:5]:
                    version = f" v{tech['version']}" if tech.get('version') != 'unknown' else ''
                    print(f"     - {tech['name']}{version}")
                if len(technologies) > 5:
                    print(f"     ... et {len(technologies) - 5} autres")
        else:
            print("   ✓ Aucune technologie détectée")
    
    def _print_dns_summary(self, dns_result: Dict):
        """Affiche un résumé de l'énumération DNS"""
        records = dns_result.get('records', {})
        total = sum(len(v) for v in records.values())
        if total > 0:
            print(f"   ✓ {total} enregistrement(s) DNS trouvé(s)")
            if not self.apt_mode:
                for record_type, values in list(records.items())[:3]:
                    print(f"     - {record_type}: {', '.join(str(v) for v in values[:2])}")
        else:
            print("   ✓ Aucun enregistrement DNS trouvé")
    
    def _print_subdomain_summary(self, subdomain_result: Dict):
        """Affiche un résumé des sous-domaines trouvés"""
        subdomains = subdomain_result.get('subdomains', [])
        if subdomains:
            print(f"   ✓ {len(subdomains)} sous-domaine(s) trouvé(s)")
            if not self.apt_mode:
                for sub in subdomains[:5]:
                    print(f"     - {sub}")
                if len(subdomains) > 5:
                    print(f"     ... et {len(subdomains) - 5} autres")
        else:
            print("   ✓ Aucun sous-domaine trouvé")
    
    def _print_summary(self):
        """Affiche un résumé global de la reconnaissance"""
        duration = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE LA RECONNAISSANCE")
        print("=" * 60)
        
        # Ports ouverts
        nmap_result = self.results.get('nmap', {})
        open_ports = nmap_result.get('open_ports', [])
        print(f"\n🔓 Ports ouverts: {len(open_ports)}")
        
        # Technologies
        techs = self.results.get('technologies', {}).get('technologies', [])
        print(f"💻 Technologies: {len(techs)}")
        
        # DNS
        dns_result = self.results.get('dns', {})
        dns_records = dns_result.get('records', {})
        total_dns = sum(len(v) for v in dns_records.values())
        print(f"🌐 Enregistrements DNS: {total_dns}")
        
        # Sous-domaines
        subdomains = self.results.get('subdomains', {}).get('subdomains', [])
        print(f"🔎 Sous-domaines: {len(subdomains)}")
        
        # WAF
        waf_result = self.results.get('waf', {})
        if waf_result.get('waf_detected'):
            print(f"🛡️ WAF détecté: {waf_result.get('waf_name', 'Unknown')}")
        
        # Certificat
        cert_result = self.results.get('certificate', {})
        if cert_result.get('valid'):
            print(f"🔒 Certificat SSL: valide")
        
        # OS
        os_result = self.results.get('os', {})
        if os_result.get('os'):
            print(f"💻 OS détecté: {os_result['os']}")
        
        print(f"\n⏱️  Durée: {duration:.1f}s")
        print("\n✅ Phase footprint terminée")
    
    def get_results(self) -> Dict[str, Any]:
        """Retourne les résultats de la reconnaissance"""
        return self.results
    
    def save_results(self, output_file: str) -> bool:
        """
        Sauvegarde les résultats au format JSON
        
        Args:
            output_file: Chemin du fichier de sortie
            
        Returns:
            True si sauvegarde réussie
        """
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "target": self.target,
                    "timestamp": datetime.now().isoformat(),
                    "duration": time.time() - self.start_time if self.start_time else 0,
                    "stealth_mode": self.stealth_mode,
                    "apt_mode": self.apt_mode,
                    "results": self.results
                }, f, indent=4, ensure_ascii=False)
            
            print(f"\n💾 Résultats sauvegardés dans {output_file}")
            return True
        except Exception as e:
            print(f"\n❌ Erreur sauvegarde: {e}")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des résultats"""
        nmap_result = self.results.get('nmap', {})
        tech_result = self.results.get('technologies', {})
        subdomain_result = self.results.get('subdomains', {})
        waf_result = self.results.get('waf', {})
        
        return {
            "target": self.target,
            "duration": time.time() - self.start_time if self.start_time else 0,
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "open_ports_count": len(nmap_result.get('open_ports', [])),
            "open_ports": nmap_result.get('open_ports', [])[:20],
            "technologies_count": len(tech_result.get('technologies', [])),
            "technologies": tech_result.get('technologies', [])[:10],
            "subdomains_count": len(subdomain_result.get('subdomains', [])),
            "subdomains": subdomain_result.get('subdomains', [])[:20],
            "waf_detected": waf_result.get('waf_detected', False),
            "waf_name": waf_result.get('waf_name')
        }


# Export des classes principales
__all__ = [
    'FootprintPhase',
    'NmapScanner',
    'WhatWebDetector',
    'DNSEnumerator',
    'SubdomainFinder',
    'OSDetector',
    'CertificateScanner',
    'WAFDetector'
]


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de la phase Footprint")
    print("=" * 60)
    
    # Créer une instance
    footprint = FootprintPhase("https://example.com")
    
    # Configurer le mode furtif
    footprint.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Exécuter la reconnaissance (simulée)
    # results = footprint.run(mode='full')
    
    print("\n✅ Module Footprint chargé avec succès")
    print("\n📋 Modules disponibles:")
    print("   - NmapScanner: Scan de ports et services")
    print("   - WhatWebDetector: Détection de technologies")
    print("   - DNSEnumerator: Énumération DNS")
    print("   - SubdomainFinder: Découverte de sous-domaines")
    print("   - OSDetector: Détection de système d'exploitation")
    print("   - CertificateScanner: Scan des certificats SSL")
    print("   - WAFDetector: Détection de WAF")