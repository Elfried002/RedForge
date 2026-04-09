#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedForge - Plateforme d'Orchestration de Pentest Web pour Red Team
Version: 2.0.0 - APT Ready
Copyright: Red Team
Licence: GPLv3
100% Français - Compatible Kali Linux & Parrot OS
"""

import sys
import os
import subprocess
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Ajouter le chemin du projet
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


@dataclass
class StealthConfig:
    """Configuration de furtivité"""
    enabled: bool = False
    apt_mode: bool = False
    delay_min: float = 1.0
    delay_max: float = 5.0
    jitter: float = 0.3
    user_agent_rotation: bool = True
    proxy: Optional[str] = None
    proxy_rotation: bool = False
    proxies: List[str] = field(default_factory=list)


class RedForgeOrchestrator:
    """Orchestrateur principal de RedForge"""
    
    VERSION = "2.0.0"
    
    def __init__(self, target: Optional[str] = None):
        """
        Initialise l'orchestrateur
        
        Args:
            target: Cible par défaut
        """
        self.target = target
        self.results = {}
        self.stealth_config = StealthConfig()
        self.start_time = None
        self.current_phase = None
        
        # Initialiser les composants
        self._init_components()
    
    def _init_components(self):
        """Initialise les composants internes"""
        # Importer les gestionnaires d'attaques
        try:
            from src.attacks.injection import InjectionAttackManager
            from src.attacks.session import SessionAttackManager
            from src.attacks.cross_site import CrossSiteAttackManager
            from src.attacks.authentication import AuthenticationAttackManager
            from src.attacks.file_system import FileSystemAttackManager
            from src.attacks.infrastructure import InfrastructureAttackManager
            from src.attacks.integrity import IntegrityAttackManager
            
            self.attack_managers = {
                'injection': InjectionAttackManager,
                'session': SessionAttackManager,
                'cross_site': CrossSiteAttackManager,
                'authentication': AuthenticationAttackManager,
                'file_system': FileSystemAttackManager,
                'infrastructure': InfrastructureAttackManager,
                'integrity': IntegrityAttackManager
            }
        except ImportError as e:
            print(f"⚠️ Erreur import modules d'attaque: {e}")
            self.attack_managers = {}
    
    def set_stealth_config(self, config: Dict[str, Any]):
        """
        Configure le mode furtif
        
        Args:
            config: Configuration de furtivité
        """
        self.stealth_config.enabled = config.get('enabled', False)
        self.stealth_config.apt_mode = config.get('apt_mode', False)
        self.stealth_config.delay_min = config.get('delay_min', 1.0)
        self.stealth_config.delay_max = config.get('delay_max', 5.0)
        self.stealth_config.jitter = config.get('jitter', 0.3)
        self.stealth_config.user_agent_rotation = config.get('user_agent_rotation', True)
        self.stealth_config.proxy = config.get('proxy')
        
        if self.stealth_config.apt_mode:
            print("🎭 Mode APT activé - Opération ultra discrète")
        elif self.stealth_config.enabled:
            print("🕵️ Mode furtif activé")
    
    def _apply_stealth_delay(self):
        """Applique un délai furtif"""
        if not self.stealth_config.enabled:
            return
        
        import random
        delay = random.uniform(self.stealth_config.delay_min, self.stealth_config.delay_max)
        
        # Ajouter du jitter
        if self.stealth_config.apt_mode:
            jitter = delay * self.stealth_config.jitter
            delay += random.uniform(-jitter, jitter)
        
        time.sleep(max(0, delay))
    
    def run_footprint(self, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Phase 1: Reconnaissance et énumération
        
        Args:
            target: Cible (utilise celle de l'instance par défaut)
            
        Returns:
            Résultats de la reconnaissance
        """
        target = target or self.target
        if not target:
            return {"error": "Aucune cible spécifiée"}
        
        self.current_phase = "footprint"
        print(f"\n📡 Phase 1: Reconnaissance sur {target}")
        print("=" * 50)
        
        results = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "phase": "footprint",
            "stealth_mode": self.stealth_config.enabled,
            "apt_mode": self.stealth_config.apt_mode
        }
        
        # 1. Scan de ports avec Nmap
        self._apply_stealth_delay()
        print("  🔍 Scan des ports ouverts...")
        
        try:
            from src.connectors.nmap_connector import NmapConnector
            nmap = NmapConnector()
            if self.stealth_config.enabled:
                nmap.set_apt_mode(self.stealth_config.apt_mode)
                nmap.set_stealth_config({
                    'delay': (self.stealth_config.delay_min, self.stealth_config.delay_max),
                    'stealth': True
                })
            
            scan_result = nmap.quick_scan(target)
            results["nmap"] = scan_result
            print(f"    ✓ {scan_result.get('count', 0)} ports ouverts trouvés")
        except Exception as e:
            print(f"    ⚠️ Erreur scan Nmap: {e}")
            results["nmap_error"] = str(e)
        
        # 2. Détection de technologies
        self._apply_stealth_delay()
        print("  🔧 Détection des technologies...")
        
        try:
            from src.connectors.whatweb_connector import WhatWebConnector
            whatweb = WhatWebConnector()
            if self.stealth_config.enabled:
                whatweb.set_apt_mode(self.stealth_config.apt_mode)
            
            tech_result = whatweb.quick_detect(target)
            results["technologies"] = tech_result
            print(f"    ✓ {tech_result.get('count', 0)} technologies détectées")
        except Exception as e:
            print(f"    ⚠️ Erreur détection technologies: {e}")
            results["tech_error"] = str(e)
        
        # 3. Détection WAF
        self._apply_stealth_delay()
        print("  🛡️ Détection WAF...")
        
        try:
            from src.connectors.wafw00f_connector import WafW00fConnector
            waf = WafW00fConnector()
            waf_result = waf.quick_detect(target)
            results["waf"] = waf_result
            if waf_result.get("waf_detected"):
                print(f"    ✓ WAF détecté: {waf_result.get('waf_name')}")
            else:
                print("    ✓ Aucun WAF détecté")
        except Exception as e:
            print(f"    ⚠️ Erreur détection WAF: {e}")
            results["waf_error"] = str(e)
        
        self.results["footprint"] = results
        return results
    
    def run_analysis(self, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Phase 2: Analyse approfondie
        
        Args:
            target: Cible (utilise celle de l'instance par défaut)
            
        Returns:
            Résultats de l'analyse
        """
        target = target or self.target
        if not target:
            return {"error": "Aucune cible spécifiée"}
        
        self.current_phase = "analysis"
        print(f"\n📊 Phase 2: Analyse approfondie sur {target}")
        print("=" * 50)
        
        results = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "phase": "analysis",
            "stealth_mode": self.stealth_config.enabled,
            "apt_mode": self.stealth_config.apt_mode
        }
        
        # 1. Énumération des répertoires
        self._apply_stealth_delay()
        print("  📁 Énumération des répertoires...")
        
        try:
            from src.connectors.dirb_connector import DirbConnector
            dirb = DirbConnector()
            if self.stealth_config.enabled:
                dirb.set_apt_mode(self.stealth_config.apt_mode)
            
            dir_result = dirb.test_common_paths(target)
            results["directories"] = dir_result
            print(f"    ✓ {dir_result.get('count', 0)} répertoires trouvés")
        except Exception as e:
            print(f"    ⚠️ Erreur énumération répertoires: {e}")
            results["dir_error"] = str(e)
        
        # 2. Analyse des paramètres
        self._apply_stealth_delay()
        print("  🔍 Analyse des paramètres...")
        
        # Analyse basique des paramètres depuis l'URL
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(target)
        if parsed.query:
            params = parse_qs(parsed.query)
            results["parameters"] = list(params.keys())
            print(f"    ✓ {len(params)} paramètres trouvés")
        else:
            results["parameters"] = []
            print("    ✓ Aucun paramètre détecté")
        
        # 3. Analyse des formulaires
        self._apply_stealth_delay()
        print("  📝 Analyse des formulaires...")
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {}
            if self.stealth_config.user_agent_rotation:
                headers['User-Agent'] = self._get_user_agent()
            
            response = requests.get(target, headers=headers, timeout=30, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form')
            
            forms_analysis = []
            for form in forms:
                form_info = {
                    "action": form.get('action', ''),
                    "method": form.get('method', 'GET'),
                    "inputs": len(form.find_all(['input', 'textarea', 'select']))
                }
                forms_analysis.append(form_info)
            
            results["forms"] = {
                "count": len(forms),
                "details": forms_analysis
            }
            print(f"    ✓ {len(forms)} formulaires analysés")
        except Exception as e:
            print(f"    ⚠️ Erreur analyse formulaires: {e}")
            results["forms_error"] = str(e)
        
        self.results["analysis"] = results
        return results
    
    def run_scanning(self, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Phase 3: Scan de vulnérabilités
        
        Args:
            target: Cible (utilise celle de l'instance par défaut)
            
        Returns:
            Résultats du scan
        """
        target = target or self.target
        if not target:
            return {"error": "Aucune cible spécifiée"}
        
        self.current_phase = "scan"
        print(f"\n🔍 Phase 3: Scan de vulnérabilités sur {target}")
        print("=" * 50)
        
        results = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "phase": "scan",
            "stealth_mode": self.stealth_config.enabled,
            "apt_mode": self.stealth_config.apt_mode,
            "vulnerabilities": []
        }
        
        # 1. Scan XSS
        self._apply_stealth_delay()
        print("  💉 Scan XSS...")
        
        try:
            from src.connectors.xsstrike_connector import XSStrikeConnector
            xsstrike = XSStrikeConnector()
            if self.stealth_config.enabled:
                xsstrike.set_apt_mode(self.stealth_config.apt_mode)
            
            xss_result = xsstrike.scan(target, level=2)
            if xss_result.get('vulnerabilities'):
                results["vulnerabilities"].extend(xss_result['vulnerabilities'])
                print(f"    ✓ {len(xss_result['vulnerabilities'])} vulnérabilités XSS trouvées")
            else:
                print("    ✓ Aucune vulnérabilité XSS détectée")
        except Exception as e:
            print(f"    ⚠️ Erreur scan XSS: {e}")
        
        # 2. Scan SQLi (optionnel - peut être long)
        if not self.stealth_config.apt_mode:
            self._apply_stealth_delay()
            print("  🗄️ Scan SQL injection...")
            
            try:
                from src.connectors.sqlmap_connector import SQLMapConnector
                sqlmap = SQLMapConnector()
                if self.stealth_config.enabled:
                    sqlmap.set_apt_mode(True)
                
                # Test simple avec paramètre id
                test_url = f"{target}?id=1"
                sql_result = sqlmap.scan(test_url, level=1, techniques='T')
                if sql_result.get('vulnerable'):
                    results["vulnerabilities"].append({
                        "type": "sql_injection",
                        "severity": "critical",
                        "details": "Injection SQL détectée"
                    })
                    print("    ✓ Vulnérabilité SQLi détectée")
                else:
                    print("    ✓ Aucune injection SQL détectée")
            except Exception as e:
                print(f"    ⚠️ Erreur scan SQLi: {e}")
        
        # 3. Scan LFI
        self._apply_stealth_delay()
        print("  📄 Scan LFI/RFI...")
        
        try:
            from src.attacks.file_system.lfi_rfi import LFIRFIAttack
            lfi = LFIRFIAttack()
            lfi_result = lfi.scan(target)
            if lfi_result.get('vulnerabilities'):
                results["vulnerabilities"].extend(lfi_result['vulnerabilities'])
                print(f"    ✓ {len(lfi_result['vulnerabilities'])} vulnérabilités LFI trouvées")
            else:
                print("    ✓ Aucune vulnérabilité LFI détectée")
        except Exception as e:
            print(f"    ⚠️ Erreur scan LFI: {e}")
        
        self.results["scan"] = results
        return results
    
    def run_exploitation(self, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Phase 4: Exploitation
        
        Args:
            target: Cible (utilise celle de l'instance par défaut)
            
        Returns:
            Résultats de l'exploitation
        """
        target = target or self.target
        if not target:
            return {"error": "Aucune cible spécifiée"}
        
        self.current_phase = "exploit"
        print(f"\n💣 Phase 4: Exploitation sur {target}")
        print("=" * 50)
        
        results = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "phase": "exploit",
            "stealth_mode": self.stealth_config.enabled,
            "apt_mode": self.stealth_config.apt_mode,
            "exploits": []
        }
        
        # Récupérer les vulnérabilités des phases précédentes
        previous_vulns = []
        for phase in ['footprint', 'analysis', 'scan']:
            if phase in self.results:
                vulns = self.results[phase].get('vulnerabilities', [])
                previous_vulns.extend(vulns)
        
        if not previous_vulns:
            print("  ℹ️ Aucune vulnérabilité trouvée dans les phases précédentes")
            print("  💡 Lancez d'abord les phases footprint, analysis et scan")
        
        # Exploitation des vulnérabilités trouvées
        for vuln in previous_vulns:
            vuln_type = vuln.get('type', '').lower()
            
            if 'xss' in vuln_type:
                self._apply_stealth_delay()
                print(f"  🎯 Exploitation XSS: {vuln.get('parameter', 'unknown')}")
                results["exploits"].append({
                    "type": "xss",
                    "status": "identified",
                    "parameter": vuln.get('parameter'),
                    "payload": vuln.get('payload')
                })
            
            elif 'sql' in vuln_type:
                self._apply_stealth_delay()
                print(f"  🎯 Exploitation SQLi: {vuln.get('parameter', 'unknown')}")
                results["exploits"].append({
                    "type": "sqli",
                    "status": "identified",
                    "parameter": vuln.get('parameter')
                })
            
            elif 'lfi' in vuln_type or 'rfi' in vuln_type:
                self._apply_stealth_delay()
                print(f"  🎯 Exploitation LFI/RFI")
                results["exploits"].append({
                    "type": "lfi",
                    "status": "identified"
                })
        
        # Tentative de reverse shell (en mode APT uniquement)
        if self.stealth_config.apt_mode and results["exploits"]:
            self._apply_stealth_delay()
            print("  🔌 Tentative d'obtention de reverse shell...")
            results["exploits"].append({
                "type": "reverse_shell",
                "status": "attempted",
                "note": "Reverse shell nécessite une configuration manuelle"
            })
        
        self.results["exploit"] = results
        return results
    
    def run_all(self, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Exécute toutes les phases
        
        Args:
            target: Cible (utilise celle de l'instance par défaut)
            
        Returns:
            Résultats complets
        """
        target = target or self.target
        if not target:
            return {"error": "Aucune cible spécifiée"}
        
        self.start_time = time.time()
        
        print("\n" + "=" * 60)
        print(f"🚀 Lancement de l'opération complète sur {target}")
        if self.stealth_config.apt_mode:
            print("🎭 Mode APT activé - Opération ultra discrète")
        elif self.stealth_config.enabled:
            print("🕵️ Mode furtif activé")
        print("=" * 60)
        
        results = {}
        
        # Exécuter chaque phase
        phases = [
            ("footprint", self.run_footprint),
            ("analysis", self.run_analysis),
            ("scan", self.run_scanning),
            ("exploit", self.run_exploitation)
        ]
        
        for phase_name, phase_func in phases:
            try:
                phase_result = phase_func(target)
                results[phase_name] = phase_result
            except Exception as e:
                print(f"❌ Erreur lors de la phase {phase_name}: {e}")
                results[phase_name] = {"error": str(e)}
            
            # Pause entre les phases en mode APT
            if self.stealth_config.apt_mode and phase_name != phases[-1][0]:
                pause = random.uniform(30, 120)
                print(f"💤 Pause APT: {pause:.0f}s")
                time.sleep(pause)
        
        # Résumé
        total_vulns = 0
        for phase in results.values():
            if isinstance(phase, dict):
                total_vulns += len(phase.get('vulnerabilities', []))
        
        duration = time.time() - self.start_time
        print("\n" + "=" * 60)
        print(f"✅ Opération terminée en {duration:.1f}s")
        print(f"⚠️ {total_vulns} vulnérabilité(s) détectée(s)")
        print("=" * 60)
        
        return results
    
    def _get_user_agent(self) -> str:
        """Retourne un User-Agent aléatoire"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        import random
        return random.choice(user_agents)
    
    def generate_report(self, output_file: str, format: str = "json") -> bool:
        """
        Génère un rapport des résultats
        
        Args:
            output_file: Fichier de sortie
            format: Format (json, html, txt)
            
        Returns:
            True si succès
        """
        report_data = {
            "target": self.target,
            "timestamp": datetime.now().isoformat(),
            "version": self.VERSION,
            "stealth_mode": self.stealth_config.enabled,
            "apt_mode": self.stealth_config.apt_mode,
            "results": self.results
        }
        
        try:
            if format == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=4, ensure_ascii=False)
            elif format == "txt":
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"RedForge Report - {self.target}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(json.dumps(report_data, indent=2, ensure_ascii=False))
            else:
                # HTML report
                html = self._generate_html_report(report_data)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html)
            
            print(f"✅ Rapport généré: {output_file}")
            return True
        except Exception as e:
            print(f"❌ Erreur génération rapport: {e}")
            return False
    
    def _generate_html_report(self, data: Dict) -> str:
        """Génère un rapport HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>RedForge Report - {data['target']}</title>
            <style>
                body {{ font-family: monospace; background: #1a202c; color: #68d391; padding: 20px; }}
                h1 {{ color: #f56565; }}
                .vulnerability {{ border-left: 3px solid #f56565; margin: 10px 0; padding: 10px; background: #2d3748; }}
                .critical {{ color: #f56565; }}
                .high {{ color: #ed8936; }}
                .medium {{ color: #ecc94b; }}
                .low {{ color: #48bb78; }}
            </style>
        </head>
        <body>
            <h1>🔴 RedForge - Rapport d'Analyse</h1>
            <p>Cible: {data['target']}</p>
            <p>Date: {data['timestamp']}</p>
            <p>Mode furtif: {data['stealth_mode']}</p>
            <p>Mode APT: {data['apt_mode']}</p>
            <h2>📊 Résultats</h2>
            <pre>{json.dumps(data['results'], indent=2, ensure_ascii=False)}</pre>
        </body>
        </html>
        """
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut actuel"""
        return {
            "target": self.target,
            "current_phase": self.current_phase,
            "stealth_enabled": self.stealth_config.enabled,
            "apt_mode": self.stealth_config.apt_mode,
            "results_available": bool(self.results),
            "start_time": self.start_time
        }


# Fonctions de compatibilité
def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3, 9):
        print("❌ RedForge nécessite Python 3.9 ou supérieur")
        print(f"   Version actuelle: {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)


def main():
    """Point d'entrée principal"""
    print("RedForge Orchestrator v2.0.0")
    print("=" * 40)
    
    # Exemple d'utilisation
    print("\n💡 Exemple d'utilisation:")
    print("  orchestrator = RedForgeOrchestrator('example.com')")
    print("  orchestrator.set_stealth_config({'enabled': True, 'apt_mode': True})")
    print("  results = orchestrator.run_all()")
    print("  orchestrator.generate_report('report.html')")


if __name__ == "__main__":
    main()