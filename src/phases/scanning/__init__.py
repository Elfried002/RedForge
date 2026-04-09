#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3: Scanning - Scan de vulnérabilités
Cette phase détecte les vulnérabilités de l'application web
Version avec support furtif, APT et orchestration avancée
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from src.phases.scanning.sqlmap_wrapper import SQLMapWrapper
from src.phases.scanning.xss_scanner import XSSScanner
from src.phases.scanning.lfi_scanner import LFIScanner
from src.phases.scanning.command_injection import CommandInjectionScanner
from src.phases.scanning.ssrf_scanner import SSRFScanner
from src.phases.scanning.xxe_scanner import XXEScanner
from src.phases.scanning.open_redirect import OpenRedirectScanner
from src.phases.scanning.csrf_scanner import CSRFScanner
from src.phases.scanning.idor_scanner import IDORScanner
from src.core.stealth_engine import StealthEngine


class ScanningPhase:
    """
    Orchestrateur de la phase de scan de vulnérabilités
    Combine tous les scanners de vulnérabilités
    Supporte le mode furtif et APT
    """
    
    def __init__(self, target: str):
        """
        Initialise la phase de scanning
        
        Args:
            target: Cible à scanner
        """
        self.target = target
        self.results = {}
        self.start_time = None
        self.stealth_mode = False
        self.apt_mode = False
        self.stealth_config = {}
        self.stealth_engine = StealthEngine()
        
        # Initialiser les scanners
        self.sql_scanner = SQLMapWrapper()
        self.xss_scanner = XSSScanner()
        self.lfi_scanner = LFIScanner()
        self.cmd_scanner = CommandInjectionScanner()
        self.ssrf_scanner = SSRFScanner()
        self.xxe_scanner = XXEScanner()
        self.redirect_scanner = OpenRedirectScanner()
        self.csrf_scanner = CSRFScanner()
        self.idor_scanner = IDORScanner()
    
    def set_stealth_config(self, config: Dict[str, Any]):
        """
        Configure le mode furtif pour le scanning
        
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
        
        # Propager la configuration aux scanners
        for scanner in [self.sql_scanner, self.xss_scanner, self.lfi_scanner, 
                       self.cmd_scanner, self.ssrf_scanner, self.xxe_scanner,
                       self.redirect_scanner, self.csrf_scanner, self.idor_scanner]:
            if hasattr(scanner, 'set_stealth_config'):
                scanner.set_stealth_config(config)
    
    def _apply_stealth_delay(self):
        """Applique un délai furtif entre les scanners"""
        if self.stealth_mode:
            self.stealth_engine.apply_delay()
    
    def run(self, **kwargs) -> dict:
        """
        Exécute toutes les étapes de la phase scanning
        
        Args:
            **kwargs: Options de configuration
                - sql_scan: Activer scan SQLi
                - xss_scan: Activer scan XSS
                - lfi_scan: Activer scan LFI/RFI
                - cmd_scan: Activer scan command injection
                - ssrf_scan: Activer scan SSRF
                - xxe_scan: Activer scan XXE
                - redirect_scan: Activer scan open redirect
                - csrf_scan: Activer scan CSRF
                - idor_scan: Activer scan IDOR
                - level: Niveau d'agressivité (1-5)
        """
        self.start_time = time.time()
        
        mode_text = "APT" if self.apt_mode else "furtif" if self.stealth_mode else "normal"
        print(f"\n🔍 PHASE 3: SCANNING - Scan de vulnérabilités sur {self.target}")
        print(f"🎭 Mode: {mode_text.upper()}")
        print("=" * 60)
        
        level = kwargs.get('level', 3)
        if self.apt_mode:
            level = min(level, 2)  # Niveau réduit en mode APT
        
        results = {}
        
        # Définir l'ordre des scans (du moins intrusif au plus intrusif)
        scan_order = [
            ("csrf_scan", self.csrf_scanner, "CSRF"),
            ("redirect_scan", self.redirect_scanner, "Open Redirect"),
            ("idor_scan", self.idor_scanner, "IDOR"),
            ("xss_scan", self.xss_scanner, "XSS"),
            ("lfi_scan", self.lfi_scanner, "LFI/RFI"),
            ("cmd_scan", self.cmd_scanner, "Command Injection"),
            ("ssrf_scan", self.ssrf_scanner, "SSRF"),
            ("xxe_scan", self.xxe_scanner, "XXE"),
            ("sql_scan", self.sql_scanner, "SQL Injection")
        ]
        
        for scan_key, scanner, scan_name in scan_order:
            if kwargs.get(scan_key, True) and not (self.apt_mode and scan_key == "sql_scan"):
                print(f"\n🔍 Scan {scan_name}...")
                if self.apt_mode:
                    print(f"   (Mode APT: scan discret)")
                
                self._apply_stealth_delay()
                
                try:
                    if scan_key == "sql_scan":
                        scan_result = scanner.scan(self.target, level=level, **kwargs)
                    else:
                        scan_result = scanner.scan(self.target, level=level, **kwargs)
                    
                    results[scan_key.replace('_scan', '')] = scan_result
                    
                except Exception as e:
                    print(f"   ⚠️ Erreur scan {scan_name}: {e}")
                    results[scan_key.replace('_scan', '')] = {"error": str(e), "vulnerabilities": []}
        
        self.results = results
        self._print_summary()
        
        return results
    
    def _print_summary(self):
        """Affiche un résumé des vulnérabilités trouvées"""
        duration = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES VULNÉRABILITÉS DÉTECTÉES")
        print("=" * 60)
        
        all_vulnerabilities = []
        severity_counts = defaultdict(int)
        
        # Collecter toutes les vulnérabilités
        for scan_name, scan_result in self.results.items():
            if not isinstance(scan_result, dict):
                continue
            
            vulnerabilities = scan_result.get('vulnerabilities', [])
            if scan_result.get('vulnerable'):
                vulnerabilities.append({
                    "type": scan_name.upper(),
                    "severity": scan_result.get('severity', 'HIGH'),
                    "details": scan_result.get('details', 'Détecté')
                })
            
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'MEDIUM').upper()
                severity_counts[severity] += 1
                all_vulnerabilities.append({
                    "type": vuln.get('type', scan_name.upper()),
                    "severity": severity,
                    "parameter": vuln.get('parameter', vuln.get('details', '')),
                    "details": vuln.get('details', '')
                })
        
        if all_vulnerabilities:
            print(f"\n⚠️  {len(all_vulnerabilities)} vulnérabilité(s) détectée(s):")
            print(f"   🔴 CRITICAL: {severity_counts.get('CRITICAL', 0)}")
            print(f"   🟠 HIGH: {severity_counts.get('HIGH', 0)}")
            print(f"   🟡 MEDIUM: {severity_counts.get('MEDIUM', 0)}")
            print(f"   🔵 LOW: {severity_counts.get('LOW', 0)}")
            
            print("\nDétails:")
            for vuln in all_vulnerabilities[:15]:
                icon = "🔴" if vuln['severity'] == "CRITICAL" else "🟠" if vuln['severity'] == "HIGH" else "🟡" if vuln['severity'] == "MEDIUM" else "🔵"
                param_info = f" ({vuln['parameter']})" if vuln['parameter'] else ""
                print(f"   {icon} [{vuln['severity']}] {vuln['type']}{param_info}: {vuln['details'][:60]}")
            
            if len(all_vulnerabilities) > 15:
                print(f"   ... et {len(all_vulnerabilities) - 15} autres")
        else:
            print("\n✅ Aucune vulnérabilité détectée")
        
        print(f"\n⏱️  Durée: {duration:.1f}s")
        print("\n✅ Phase scanning terminée")
    
    def get_results(self) -> Dict[str, Any]:
        """Retourne les résultats du scanning"""
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
        total_vulns = 0
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        
        for scan_name, scan_result in self.results.items():
            if not isinstance(scan_result, dict):
                continue
            
            vulnerabilities = scan_result.get('vulnerabilities', [])
            if scan_result.get('vulnerable'):
                total_vulns += 1
                by_type[scan_name.upper()] += 1
                by_severity[scan_result.get('severity', 'HIGH').upper()] += 1
            
            for vuln in vulnerabilities:
                total_vulns += 1
                vuln_type = vuln.get('type', scan_name.upper())
                severity = vuln.get('severity', 'MEDIUM').upper()
                by_type[vuln_type] += 1
                by_severity[severity] += 1
        
        return {
            "target": self.target,
            "duration": time.time() - self.start_time if self.start_time else 0,
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "total_vulnerabilities": total_vulns,
            "by_type": dict(by_type),
            "by_severity": dict(by_severity)
        }


# Export des classes principales
__all__ = [
    'ScanningPhase',
    'SQLMapWrapper',
    'XSSScanner',
    'LFIScanner',
    'CommandInjectionScanner',
    'SSRFScanner',
    'XXEScanner',
    'OpenRedirectScanner',
    'CSRFScanner',
    'IDORScanner'
]


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de la phase Scanning")
    print("=" * 60)
    
    # Créer une instance
    scanning = ScanningPhase("https://example.com")
    
    # Configurer le mode furtif
    scanning.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    print("\n✅ Module Scanning chargé avec succès")
    print("\n📋 Scanners disponibles:")
    print("   - SQLMapWrapper: Injection SQL")
    print("   - XSSScanner: Cross-Site Scripting")
    print("   - LFIScanner: LFI/RFI")
    print("   - CommandInjectionScanner: Injection de commandes")
    print("   - SSRFScanner: Server-Side Request Forgery")
    print("   - XXEScanner: XML External Entity")
    print("   - OpenRedirectScanner: Redirections ouvertes")
    print("   - CSRFScanner: Cross-Site Request Forgery")
    print("   - IDORScanner: Insecure Direct Object Reference")