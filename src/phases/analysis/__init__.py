#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2: Analysis - Analyse approfondie de l'application web
Cette phase analyse en détail le fonctionnement de l'application
Version avec support furtif et APT
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Import des modules d'analyse
from src.phases.analysis.dirbuster import DirBuster
from src.phases.analysis.param_finder import ParamFinder
from src.phases.analysis.tech_detector import TechDetector
from src.phases.analysis.api_discovery import APIDiscovery
from src.phases.analysis.js_analyzer import JSAnalyzer
from src.phases.analysis.form_analyzer import FormAnalyzer
from src.phases.analysis.session_analyzer import SessionAnalyzer


class AnalysisPhase:
    """
    Orchestrateur de la phase d'analyse
    Combine tous les modules d'analyse approfondie
    Supporte le mode furtif et APT
    """
    
    def __init__(self, target: str):
        """
        Initialise la phase d'analyse
        
        Args:
            target: Cible à analyser
        """
        self.target = target
        self.results = {}
        self.start_time = None
        self.stealth_mode = False
        self.apt_mode = False
        self.stealth_config = {}
        
        # Initialiser les modules
        self.dirbuster = DirBuster()
        self.param_finder = ParamFinder()
        self.tech_detector = TechDetector()
        self.api_discovery = APIDiscovery()
        self.js_analyzer = JSAnalyzer()
        self.form_analyzer = FormAnalyzer()
        self.session_analyzer = SessionAnalyzer()
    
    def set_stealth_config(self, config: Dict[str, Any]):
        """
        Configure le mode furtif pour l'analyse
        
        Args:
            config: Configuration de furtivité
        """
        self.stealth_mode = config.get('enabled', False)
        self.apt_mode = config.get('apt_mode', False)
        self.stealth_config = config
        
        # Propager la configuration aux modules
        for module in [self.dirbuster, self.param_finder, self.api_discovery, self.js_analyzer]:
            if hasattr(module, 'set_stealth_config'):
                module.set_stealth_config(config)
    
    def run(self, **kwargs) -> dict:
        """
        Exécute toutes les étapes de la phase analysis
        
        Args:
            **kwargs: Options de configuration
                - dir_bruteforce: Activer la force brute des répertoires
                - param_finding: Activer la recherche de paramètres
                - api_detect: Activer la détection d'API
                - js_analyze: Activer l'analyse JavaScript
                - form_analyze: Activer l'analyse des formulaires
                - session_analyze: Activer l'analyse des sessions
                - wordlist: Wordlist personnalisée
                - threads: Nombre de threads
                - recursive: Scan récursif des répertoires
                - depth: Profondeur de scan
        """
        self.start_time = time.time()
        
        mode_text = "APT" if self.apt_mode else "furtif" if self.stealth_mode else "normal"
        print(f"\n🔬 PHASE 2: ANALYSIS - Analyse approfondie sur {self.target}")
        print(f"🎭 Mode: {mode_text.upper()}")
        print("=" * 60)
        
        results = {}
        
        # Étape 1: Force brute des répertoires
        if kwargs.get('dir_bruteforce', True):
            print("\n📁 Force brute des répertoires...")
            if self.apt_mode:
                print("   (Mode APT: scan lent et discret)")
            
            dir_result = self.dirbuster.scan(
                self.target, 
                wordlist=kwargs.get('wordlist'),
                threads=kwargs.get('threads', 10),
                recursive=kwargs.get('recursive', False),
                depth=kwargs.get('depth', 3),
                extensions=kwargs.get('extensions')
            )
            results['directories'] = dir_result
            self._print_finding_summary("Répertoires", dir_result.get('directories', []), 10)
        
        # Étape 2: Recherche de paramètres
        if kwargs.get('param_finding', True):
            print("\n🔍 Recherche de paramètres cachés...")
            param_result = self.param_finder.find(
                self.target,
                wordlist=kwargs.get('param_wordlist'),
                threads=kwargs.get('threads', 10),
                methods=kwargs.get('methods', ['GET', 'POST'])
            )
            results['parameters'] = param_result
            self._print_finding_summary("Paramètres", param_result.get('parameters', []), 15)
        
        # Étape 3: Détection des technologies
        print("\n💻 Détection avancée des technologies...")
        tech_result = self.tech_detector.detect(
            self.target,
            deep_scan=kwargs.get('deep_tech_detect', True)
        )
        results['technologies'] = tech_result
        self._print_tech_summary(tech_result)
        
        # Étape 4: Découverte d'API
        if kwargs.get('api_detect', True):
            print("\n🔌 Découverte d'endpoints API...")
            api_result = self.api_discovery.discover(
                self.target,
                patterns=kwargs.get('api_patterns'),
                threads=kwargs.get('threads', 5)
            )
            results['api_endpoints'] = api_result
            self._print_finding_summary("Endpoints API", api_result.get('endpoints', []), 15)
        
        # Étape 5: Analyse JavaScript
        if kwargs.get('js_analyze', True):
            print("\n📜 Analyse des fichiers JavaScript...")
            js_result = self.js_analyzer.analyze(
                self.target,
                extract_endpoints=kwargs.get('js_extract_endpoints', True),
                extract_secrets=kwargs.get('js_extract_secrets', True),
                max_files=kwargs.get('max_js_files', 20)
            )
            results['javascript'] = js_result
            self._print_js_summary(js_result)
        
        # Étape 6: Analyse des formulaires
        if kwargs.get('form_analyze', True):
            print("\n📝 Analyse des formulaires...")
            form_result = self.form_analyzer.analyze(
                self.target,
                extract_inputs=kwargs.get('extract_form_inputs', True),
                detect_csrf=kwargs.get('detect_csrf', True)
            )
            results['forms'] = form_result
            self._print_finding_summary("Formulaires", form_result.get('forms', []), 10)
        
        # Étape 7: Analyse des sessions
        if kwargs.get('session_analyze', True):
            print("\n🔐 Analyse des sessions...")
            session_result = self.session_analyzer.analyze(
                self.target,
                cookie_analysis=kwargs.get('cookie_analysis', True),
                session_patterns=kwargs.get('session_patterns', True)
            )
            results['sessions'] = session_result
        
        self.results = results
        self._print_summary()
        
        return results
    
    def _print_finding_summary(self, title: str, items: List, max_items: int = 10):
        """Affiche un résumé des découvertes"""
        count = len(items)
        if count == 0:
            print(f"   Aucun {title.lower()} trouvé")
        else:
            print(f"   ✓ {count} {title.lower()} trouvé(s)")
            if not self.apt_mode:  # En mode APT, moins de détails
                for item in items[:max_items]:
                    if isinstance(item, dict):
                        name = item.get('name') or item.get('path') or item.get('url') or str(item)
                    else:
                        name = str(item)
                    print(f"     - {name[:80]}")
                if count > max_items:
                    print(f"     ... et {count - max_items} autres")
    
    def _print_tech_summary(self, tech_result: Dict):
        """Affiche un résumé des technologies détectées"""
        technologies = tech_result.get('technologies', [])
        if not technologies:
            print("   Aucune technologie détectée")
            return
        
        # Grouper par catégorie
        categories = {}
        for tech in technologies:
            cat = tech.get('category', 'other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tech)
        
        print(f"   ✓ {len(technologies)} technologie(s) détectée(s)")
        
        if not self.apt_mode:
            for cat, techs in categories.items():
                print(f"     [{cat.upper()}] {len(techs)} technologie(s)")
                for tech in techs[:3]:
                    version = f" v{tech.get('version')}" if tech.get('version') else ""
                    print(f"       - {tech.get('name')}{version}")
                if len(techs) > 3:
                    print(f"       ... et {len(techs) - 3} autres")
    
    def _print_js_summary(self, js_result: Dict):
        """Affiche un résumé de l'analyse JavaScript"""
        js_files = js_result.get('js_files', [])
        endpoints = js_result.get('endpoints', [])
        secrets = js_result.get('secrets', [])
        
        print(f"   ✓ {len(js_files)} fichier(s) JS analysé(s)")
        if endpoints:
            print(f"   ✓ {len(endpoints)} endpoint(s) trouvé(s) dans JS")
        if secrets:
            print(f"   ⚠️ {len(secrets)} secret(s) potentiel(s) trouvé(s)")
    
    def _print_summary(self):
        """Affiche un résumé global de l'analyse"""
        duration = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE L'ANALYSE")
        print("=" * 60)
        
        # Répertoires
        dirs = self.results.get('directories', {}).get('directories', [])
        print(f"\n📁 Répertoires trouvés: {len(dirs)}")
        
        # Paramètres
        params = self.results.get('parameters', {}).get('parameters', [])
        print(f"🔧 Paramètres trouvés: {len(params)}")
        
        # Technologies
        techs = self.results.get('technologies', {}).get('technologies', [])
        print(f"💻 Technologies détectées: {len(techs)}")
        
        # Endpoints API
        apis = self.results.get('api_endpoints', {}).get('endpoints', [])
        print(f"🔌 Endpoints API: {len(apis)}")
        
        # Fichiers JS
        js_files = self.results.get('javascript', {}).get('js_files', [])
        print(f"📜 Fichiers JavaScript: {len(js_files)}")
        
        # Formulaires
        forms = self.results.get('forms', {}).get('forms', [])
        print(f"📝 Formulaires: {len(forms)}")
        
        # Sessions
        sessions = self.results.get('sessions', {})
        cookies = sessions.get('cookies', [])
        print(f"🔐 Cookies de session: {len(cookies)}")
        
        print(f"\n⏱️  Durée: {duration:.1f}s")
        print("\n✅ Phase analysis terminée")
    
    def get_results(self) -> Dict[str, Any]:
        """Retourne les résultats de l'analyse"""
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
        return {
            "target": self.target,
            "duration": time.time() - self.start_time if self.start_time else 0,
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "directories_count": len(self.results.get('directories', {}).get('directories', [])),
            "parameters_count": len(self.results.get('parameters', {}).get('parameters', [])),
            "technologies_count": len(self.results.get('technologies', {}).get('technologies', [])),
            "api_endpoints_count": len(self.results.get('api_endpoints', {}).get('endpoints', [])),
            "js_files_count": len(self.results.get('javascript', {}).get('js_files', [])),
            "forms_count": len(self.results.get('forms', {}).get('forms', [])),
            "cookies_count": len(self.results.get('sessions', {}).get('cookies', []))
        }


# Export des classes principales
__all__ = [
    'AnalysisPhase',
    'DirBuster',
    'ParamFinder',
    'TechDetector',
    'APIDiscovery',
    'JSAnalyzer',
    'FormAnalyzer',
    'SessionAnalyzer'
]


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de la phase Analysis")
    print("=" * 60)
    
    # Créer une instance
    analysis = AnalysisPhase("https://example.com")
    
    # Configurer le mode furtif
    analysis.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 2,
        'delay_max': 5
    })
    
    # Exécuter l'analyse (simulée)
    # results = analysis.run(dir_bruteforce=True, param_finding=True)
    
    print("\n✅ Module Analysis chargé avec succès")
    print("\n📋 Modules disponibles:")
    print("   - DirBuster: Force brute des répertoires")
    print("   - ParamFinder: Découverte de paramètres")
    print("   - TechDetector: Détection de technologies")
    print("   - APIDiscovery: Découverte d'API")
    print("   - JSAnalyzer: Analyse JavaScript")
    print("   - FormAnalyzer: Analyse de formulaires")
    print("   - SessionAnalyzer: Analyse de sessions")