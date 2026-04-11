#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedForge v2.0 - Module de gestion d'aide ultra robuste
Gère la documentation et l'aide contextuelle avec support APT, mode furtif
Version avec fallbacks et compatibilité maximale
"""

import json
import os
import sys
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
from enum import Enum
from functools import wraps


# ============================================
# UTILITAIRES ROBUSTES
# ============================================

def safe_method(default_return=None):
    """Décorateur pour méthodes sécurisées (ne plantent jamais)"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                try:
                    print(f"[!] Erreur dans {func.__name__}: {e}", file=sys.stderr)
                except Exception:
                    pass
                return default_return
        return wrapper
    return decorator


# ============================================
# CLASSES PRINCIPALES
# ============================================

class HelpTopic:
    """Classe représentant un sujet d'aide"""
    
    def __init__(self, topic_id: str, title: str, content: str, category: str = "general", 
                 subcategory: str = "", level: str = "beginner"):
        """
        Initialise un sujet d'aide
        
        Args:
            topic_id: Identifiant unique du sujet
            title: Titre du sujet
            content: Contenu du sujet (texte ou HTML)
            category: Catégorie principale
            subcategory: Sous-catégorie
            level: Niveau (beginner, intermediate, advanced, expert)
        """
        self.id = topic_id
        self.title = title
        self.content = content
        self.category = category
        self.subcategory = subcategory
        self.level = level
        self.subtopics: List['HelpTopic'] = []
        self.examples: List[str] = []
        self.related_topics: List[str] = []
        self.tags: List[str] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @safe_method()
    def add_subtopic(self, subtopic: 'HelpTopic'):
        """Ajoute un sous-sujet"""
        self.subtopics.append(subtopic)
    
    @safe_method()
    def add_example(self, example: str):
        """Ajoute un exemple"""
        self.examples.append(example)
    
    @safe_method()
    def add_related_topic(self, topic_id: str):
        """Ajoute un sujet lié"""
        if topic_id not in self.related_topics:
            self.related_topics.append(topic_id)
    
    @safe_method()
    def add_tag(self, tag: str):
        """Ajoute un tag"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    @safe_method()
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "subcategory": self.subcategory,
            "level": self.level,
            "subtopics": [s.to_dict() if hasattr(s, 'to_dict') else str(s) for s in self.subtopics],
            "examples": self.examples,
            "related_topics": self.related_topics,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HelpTopic':
        """Crée un sujet depuis un dictionnaire"""
        topic = cls(
            topic_id=data.get('id', 'unknown'),
            title=data.get('title', 'Sans titre'),
            content=data.get('content', ''),
            category=data.get('category', 'general'),
            subcategory=data.get('subcategory', ''),
            level=data.get('level', 'beginner')
        )
        topic.examples = data.get('examples', [])
        topic.related_topics = data.get('related_topics', [])
        topic.tags = data.get('tags', [])
        return topic
    
    def __str__(self) -> str:
        return f"HelpTopic({self.id}: {self.title})"


class ConsoleColors:
    """Couleurs pour la console avec vérification"""
    RED = '\033[0;31m' if sys.platform != 'win32' else ''
    GREEN = '\033[0;32m' if sys.platform != 'win32' else ''
    YELLOW = '\033[1;33m' if sys.platform != 'win32' else ''
    BLUE = '\033[0;34m' if sys.platform != 'win32' else ''
    MAGENTA = '\033[0;35m' if sys.platform != 'win32' else ''
    CYAN = '\033[0;36m' if sys.platform != 'win32' else ''
    WHITE = '\033[1;37m' if sys.platform != 'win32' else ''
    RESET = '\033[0m' if sys.platform != 'win32' else ''


class SafeConsole:
    """Console sécurisée qui ne plante jamais"""
    
    @staticmethod
    def _print_color(text: str, color: str = ""):
        try:
            if color and sys.platform != 'win32':
                print(f"{color}{text}{ConsoleColors.RESET}")
            else:
                print(text)
        except Exception:
            pass
    
    @staticmethod
    def print_header(text: str):
        SafeConsole._print_color(f"\n{'=' * 60}\n{text}\n{'=' * 60}", ConsoleColors.CYAN)
    
    @staticmethod
    def print_info(text: str):
        SafeConsole._print_color(text, ConsoleColors.GREEN)
    
    @staticmethod
    def print_warning(text: str):
        SafeConsole._print_color(text, ConsoleColors.YELLOW)
    
    @staticmethod
    def print_error(text: str):
        SafeConsole._print_color(text, ConsoleColors.RED)
    
    @staticmethod
    def print_success(text: str):
        SafeConsole._print_color(text, ConsoleColors.GREEN)
    
    @staticmethod
    def print_table(headers: List[str], rows: List[List[str]]):
        """Affiche un tableau formaté"""
        try:
            # Calcul des largeurs
            col_widths = [len(h) for h in headers]
            for row in rows:
                for i, cell in enumerate(row):
                    if i < len(col_widths):
                        col_widths[i] = max(col_widths[i], len(str(cell)))
            
            # Ligne d'en-tête
            header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
            SafeConsole._print_color(header_line, ConsoleColors.CYAN)
            SafeConsole._print_color("-" * len(header_line), ConsoleColors.CYAN)
            
            # Lignes de données
            for row in rows:
                line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
                SafeConsole._print_color(line, ConsoleColors.WHITE)
        except Exception:
            pass


# Tentative d'import du vrai module color_output
try:
    from src.utils.color_output import console as _console
    console = _console
    print_header = getattr(console, 'print_header', SafeConsole.print_header)
    print_info = getattr(console, 'print_info', SafeConsole.print_info)
    print_warning = getattr(console, 'print_warning', SafeConsole.print_warning)
    print_error = getattr(console, 'print_error', SafeConsole.print_error)
    print_success = getattr(console, 'print_success', SafeConsole.print_success)
    print_table = getattr(console, 'print_table', SafeConsole.print_table)
except (ImportError, AttributeError):
    console = SafeConsole()
    print_header = SafeConsole.print_header
    print_info = SafeConsole.print_info
    print_warning = SafeConsole.print_warning
    print_error = SafeConsole.print_error
    print_success = SafeConsole.print_success
    print_table = SafeConsole.print_table


class HelpManager:
    """Gestionnaire d'aide et de documentation ultra robuste"""
    
    def __init__(self, lang: str = "fr"):
        """
        Initialise le gestionnaire d'aide
        
        Args:
            lang: Langue (fr, en)
        """
        self.lang = lang
        self.help_data: Dict[str, Any] = {}
        self.topics: Dict[str, HelpTopic] = {}
        self.stealth_mode = False
        self.apt_mode = False
        self._initialized = False
        
        self._init_topics()
        self._load_help_data()
    
    def _init_topics(self):
        """Initialise les sujets d'aide par défaut"""
        # Sujets principaux
        topics_data = [
            # Catégorie: general
            ("installation", "Installation", "Guide d'installation complet de RedForge", "general", "setup", "beginner"),
            ("usage", "Utilisation", "Guide d'utilisation de base", "general", "usage", "beginner"),
            ("cli", "Ligne de commande", "Documentation de la CLI", "general", "cli", "intermediate"),
            
            # Catégorie: attacks
            ("xss", "Cross-Site Scripting (XSS)", "Guide complet sur les attaques XSS", "attacks", "injection", "intermediate"),
            ("sql", "SQL Injection", "Guide complet sur les injections SQL", "attacks", "injection", "intermediate"),
            ("lfi", "LFI/RFI", "Inclusion de fichiers locaux/distants", "attacks", "file_inclusion", "intermediate"),
            ("command", "Command Injection", "Injection de commandes système", "attacks", "injection", "advanced"),
            ("csrf", "CSRF", "Cross-Site Request Forgery", "attacks", "request_forgery", "intermediate"),
            ("ssrf", "SSRF", "Server-Side Request Forgery", "attacks", "request_forgery", "advanced"),
            ("xxe", "XXE", "XML External Entity", "attacks", "xml", "advanced"),
            ("upload", "File Upload", "Téléversement de fichiers malveillants", "attacks", "file_upload", "intermediate"),
            
            # Catégorie: phases
            ("footprint", "Phase 1: Footprinting", "Reconnaissance et collecte d'informations", "phases", "footprint", "beginner"),
            ("analysis", "Phase 2: Analysis", "Analyse approfondie de l'application", "phases", "analysis", "intermediate"),
            ("scan", "Phase 3: Scanning", "Scan de vulnérabilités", "phases", "scan", "intermediate"),
            ("exploit", "Phase 4: Exploitation", "Exploitation des vulnérabilités", "phases", "exploit", "advanced"),
            
            # Catégorie: features
            ("stealth", "Mode Furtif", "Configuration et utilisation du mode furtif", "features", "stealth", "intermediate"),
            ("multi_attack", "Multi-attaques", "Guide des attaques multiples", "features", "multi", "advanced"),
            ("apt", "Opérations APT", "Guide des opérations APT avancées", "features", "apt", "expert"),
            ("reporting", "Génération de rapports", "Création de rapports professionnels", "features", "reports", "intermediate"),
            ("api", "API Reference", "Documentation de l'API REST", "features", "api", "advanced"),
            
            # Catégorie: tools
            ("nmap", "Nmap Scanner", "Guide d'utilisation de Nmap", "tools", "scanner", "beginner"),
            ("sqlmap", "SQLMap", "Guide d'utilisation de SQLMap", "tools", "injection", "intermediate"),
            ("metasploit", "Metasploit", "Intégration avec Metasploit", "tools", "framework", "advanced"),
            ("hydra", "Hydra", "Force brute avec Hydra", "tools", "bruteforce", "intermediate"),
            ("xsstrike", "XSStrike", "Détection XSS avancée", "tools", "xss", "intermediate"),
            
            # Catégorie: troubleshooting
            ("common_errors", "Erreurs courantes", "Résolution des problèmes fréquents", "troubleshooting", "errors", "beginner"),
            ("debug", "Debug mode", "Guide de débogage", "troubleshooting", "debug", "advanced"),
            ("logs", "Logs", "Analyse des logs", "troubleshooting", "logs", "intermediate")
        ]
        
        for tid, title, content, category, subcat, level in topics_data:
            topic = HelpTopic(tid, title, content, category, subcat, level)
            self.topics[tid] = topic
        
        # Ajout des exemples pour certains sujets
        self._add_examples()
    
    def _add_examples(self):
        """Ajoute des exemples aux sujets"""
        # XSS examples
        if 'xss' in self.topics:
            self.topics['xss'].add_example("<script>alert('XSS')</script>")
            self.topics['xss'].add_example("<img src=x onerror=alert('XSS')>")
            self.topics['xss'].add_related_topic('csrf')
            self.topics['xss'].add_tag('xss')
            self.topics['xss'].add_tag('injection')
        
        # SQL examples
        if 'sql' in self.topics:
            self.topics['sql'].add_example("' OR '1'='1")
            self.topics['sql'].add_example("1' UNION SELECT NULL--")
            self.topics['sql'].add_related_topic('command')
            self.topics['sql'].add_tag('sql')
            self.topics['sql'].add_tag('injection')
        
        # Stealth examples
        if 'stealth' in self.topics:
            self.topics['stealth'].add_example("RedForge --stealth")
            self.topics['stealth'].add_example("RedForge --stealth-level high")
            self.topics['stealth'].add_related_topic('apt')
            self.topics['stealth'].add_tag('stealth')
            self.topics['stealth'].add_tag('evasion')
    
    @safe_method()
    def _load_help_data(self):
        """Charge les données d'aide depuis les fichiers JSON"""
        # Chemins possibles
        paths = [
            Path(__file__).parent.parent / "i18n" / self.lang / "help_texts.json",
            Path(__file__).parent.parent / "i18n" / "fr_FR" / "help_texts.json",
            Path(__file__).parent.parent / "i18n" / "fr" / "help_texts.json",
            Path(__file__).parent.parent / "data" / "help" / f"help_{self.lang}.json"
        ]
        
        for path in paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.help_data = json.load(f)
                        break
                except (json.JSONDecodeError, IOError):
                    continue
        
        # Si aucun fichier trouvé, créer des données par défaut
        if not self.help_data:
            self._create_default_help_data()
    
    def _create_default_help_data(self):
        """Crée des données d'aide par défaut"""
        self.help_data = {
            "welcome": {
                "title": "Bienvenue sur RedForge",
                "description": "Plateforme d'orchestration de pentest web",
                "content": "RedForge est un outil complet pour les tests d'intrusion web."
            },
            "quick_start": {
                "title": "Démarrage rapide",
                "description": "Premiers pas avec RedForge",
                "content": "Utilisez 'RedForge -t cible -p footprint' pour commencer."
            }
        }
    
    @safe_method()
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif"""
        self.stealth_mode = enabled
    
    @safe_method()
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT"""
        self.apt_mode = enabled
    
    @safe_method()
    def show_help(self, topic: Optional[str] = None, section: Optional[str] = None):
        """
        Affiche l'aide
        
        Args:
            topic: Sujet spécifique (optionnel)
            section: Section spécifique (optionnel)
        """
        if self.apt_mode:
            self._show_apt_help()
        elif topic:
            self._show_topic_help(topic, section)
        else:
            self._show_general_help()
    
    def _show_general_help(self):
        """Affiche l'aide générale"""
        print_header("RedForge - Aide Générale v2.0")
        
        print_info("\n📖 SYNTAXE DE BASE")
        print_info("  RedForge [OPTIONS] [ARGUMENTS]\n")
        
        print_info("🔧 OPTIONS PRINCIPALES")
        table_data = [
            ("-t, --target", "Cible à analyser", "RedForge -t example.com"),
            ("-f, --file", "Fichier de cibles", "RedForge -f cibles.txt"),
            ("-p, --phase", "Phase à exécuter", "RedForge -t example.com -p scan"),
            ("-g, --gui", "Interface graphique", "sudo RedForge -g"),
            ("-o, --output", "Fichier de rapport", "RedForge -t example.com -o rapport.html"),
            ("--stealth", "Mode furtif", "RedForge --stealth"),
            ("--apt", "Mode APT", "RedForge --apt"),
            ("--multi", "Multi-attaque", "RedForge --multi config.json"),
            ("--help", "Afficher l'aide", "RedForge --help")
        ]
        
        print_table(["Option", "Description", "Exemple"], table_data)
        
        print_info("\n📚 PHASES DISPONIBLES")
        phases = [
            ("footprint", "Reconnaissance", "Collecte d'informations"),
            ("analysis", "Analyse", "Analyse approfondie"),
            ("scan", "Scan", "Détection de vulnérabilités"),
            ("exploit", "Exploitation", "Exploitation des vulnérabilités"),
            ("all", "Complet", "Toutes les phases")
        ]
        
        print_table(["Phase", "Description", "Détails"], phases)
        
        print_info("\n💡 EXEMPLES")
        examples = [
            "Scan rapide : RedForge -t https://example.com -p footprint",
            "Scan complet : RedForge -t 192.168.1.100 -p all -o rapport.html",
            "Mode furtif : RedForge -t example.com --stealth -p scan",
            "Multi-attaque : RedForge --multi config.json -t example.com",
            "Opération APT : RedForge --apt recon_to_exfil -t example.com",
            "Interface web : sudo RedForge -g"
        ]
        
        for ex in examples:
            print_info(f"  {ex}")
        
        print_info("\n❓ POUR PLUS D'AIDE")
        print_info("  RedForge --aide-commande footprint")
        print_info("  RedForge --aide-commande xss")
        print_info("  RedForge --aide-commande stealth")
        print_info("  RedForge --liste-modules")
    
    def _show_apt_help(self):
        """Affiche l'aide pour le mode APT (discret)"""
        print_info("\n" + "=" * 50)
        print_info("APT Mode - Aide discrète")
        print_info("=" * 50)
        
        print_info("\n🎭 OPÉRATIONS APT DISPONIBLES")
        operations = [
            ("recon_to_exfil", "Reconnaissance → Exfiltration", "Cycle APT complet"),
            ("web_app_compromise", "Compromission Web", "Ciblage d'application web"),
            ("lateral_movement", "Mouvement Latéral", "Propagation sur le réseau"),
            ("persistence", "Persistance", "Maintien de l'accès")
        ]
        
        for op_id, name, desc in operations:
            print_info(f"  • {op_id:<20} {name:<25} {desc}")
        
        print_info("\n⏱️ OPTIONS")
        print_info("  --stealth <level>    Niveau de furtivité (low/medium/high/paranoid)")
        print_info("  --no-cleanup         Désactiver le nettoyage post-opération")
        print_info("  --report             Générer un rapport détaillé")
    
    @safe_method()
    def _show_topic_help(self, topic: str, section: Optional[str] = None):
        """
        Affiche l'aide pour un sujet spécifique
        
        Args:
            topic: Sujet demandé
            section: Section spécifique
        """
        # Map des sujets vers leurs méthodes
        topic_methods = {
            'footprint': self._show_footprint_help,
            'analysis': self._show_analysis_help,
            'scan': self._show_scan_help,
            'exploit': self._show_exploit_help,
            'apt': self._show_apt_detailed_help,
            'stealth': self._show_stealth_help,
            'xss': self._show_xss_help,
            'sql': self._show_sql_help,
            'lfi': self._show_lfi_help,
            'command': self._show_command_help,
            'upload': self._show_upload_help,
            'csrf': self._show_csrf_help,
            'ssrf': self._show_ssrf_help,
            'xxe': self._show_xxe_help,
            'multi_attack': self._show_multi_attack_help,
            'reporting': self._show_reporting_help,
            'api': self._show_api_help
        }
        
        if topic in topic_methods:
            topic_methods[topic]()
        elif topic in self.topics:
            self._show_topic_from_data(topic)
        else:
            print_warning(f"Sujet '{topic}' non trouvé")
            self._list_available_topics()
    
    def _show_topic_from_data(self, topic_id: str):
        """Affiche un sujet depuis les données"""
        topic = self.topics.get(topic_id)
        if topic:
            print_header(topic.title)
            print_info(f"\n📝 {topic.content}")
            
            if topic.examples:
                print_info("\n💡 EXEMPLES")
                for ex in topic.examples:
                    print_info(f"  • {ex}")
            
            if topic.related_topics:
                print_info("\n🔗 SUJETS LIÉS")
                for rel in topic.related_topics:
                    print_info(f"  • {rel}")
            
            if topic.tags:
                print_info(f"\n🏷️ TAGS: {', '.join(topic.tags)}")
        else:
            print_warning(f"Sujet '{topic_id}' non trouvé")
    
    def _show_footprint_help(self):
        print_header("Phase 1: Footprinting - Reconnaissance")
        print_info("📝 Collecte d'informations sur la cible sans être intrusif.")
        print_info("\n🎯 CE QUE CETTE PHASE DÉCOUVRE")
        discoveries = [
            "Adresses IP et sous-domaines",
            "Services et ports ouverts",
            "Technologies web utilisées",
            "Serveurs DNS et emails",
            "Certificats SSL/TLS"
        ]
        for d in discoveries:
            print_info(f"  • {d}")
    
    def _show_analysis_help(self):
        print_header("Phase 2: Analysis - Analyse Approfondie")
        print_info("📝 Analyse détaillée de l'application web.")
        print_info("\n🎯 ANALYSES EFFECTUÉES")
        analyses = [
            "Structure des répertoires",
            "Paramètres GET/POST",
            "Points d'entrée utilisateur",
            "Système d'authentification",
            "Endpoints API"
        ]
        for a in analyses:
            print_info(f"  • {a}")
    
    def _show_scan_help(self):
        print_header("Phase 3: Scanning - Scan de Vulnérabilités")
        print_info("📝 Détection automatisée des vulnérabilités web.")
        print_info("\n🎯 VULNÉRABILITÉS DÉTECTÉES")
        vulns = [
            "Injections SQL (SQLi)",
            "Cross-Site Scripting (XSS)",
            "LFI/RFI",
            "Command Injection",
            "CSRF, SSRF, XXE"
        ]
        for v in vulns:
            print_info(f"  • {v}")
    
    def _show_exploit_help(self):
        print_header("Phase 4: Exploitation")
        print_info("📝 Exploitation des vulnérabilités découvertes.")
        print_info("\n🎯 CAPACITÉS")
        caps = [
            "Shell reverse/bind",
            "Upload de webshells",
            "Élévation de privilèges",
            "Persistance",
            "Exfiltration de données"
        ]
        for c in caps:
            print_info(f"  • {c}")
    
    def _show_apt_detailed_help(self):
        print_header("Opérations APT - Advanced Persistent Threat")
        print_info("📝 Simulation d'attaques avancées avec persistance.")
        print_info("\n🎯 OPÉRATIONS DISPONIBLES")
        ops = [
            ("recon_to_exfil", "Cycle APT complet (6 phases)"),
            ("web_app_compromise", "Compromission d'application web"),
            ("lateral_movement", "Mouvement latéral"),
            ("persistence", "Persistance avancée")
        ]
        for op_id, desc in ops:
            print_info(f"  • {op_id:<20} {desc}")
    
    def _show_stealth_help(self):
        print_header("Mode Furtif - Stealth Mode")
        print_info("📝 Mode discret qui ralentit les requêtes pour éviter la détection.")
        print_info("\n🎯 NIVEAUX DE FURTIVITÉ")
        levels = [
            ("low", "0.5s", "Détection facile"),
            ("medium", "1.5s", "Détection moyenne"),
            ("high", "3.0s", "Difficile à détecter"),
            ("paranoid", "5.0s", "Très difficile")
        ]
        print_table(["Niveau", "Délai", "Risque"], levels)
    
    def _show_xss_help(self):
        print_header("Cross-Site Scripting (XSS)")
        print_info("📝 Injection de scripts malveillants dans les pages web.")
        print_info("\n🎯 TYPES DE XSS")
        types = [
            ("Réfléchi", "Le payload est réfléchi dans la réponse"),
            ("Stocké", "Le payload est stocké sur le serveur"),
            ("DOM-based", "Le payload modifie le DOM")
        ]
        print_table(["Type", "Description"], types)
        
        print_info("\n🎯 PAYLOADS DE TEST")
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        for p in payloads:
            print_info(f"  {p}")
    
    def _show_sql_help(self):
        print_header("SQL Injection")
        print_info("📝 Injection de requêtes SQL malveillantes.")
        print_info("\n🎯 TYPES D'INJECTION SQL")
        types = [
            ("Error-based", "Via messages d'erreur"),
            ("Union-based", "Utilisation de UNION SELECT"),
            ("Boolean-based", "Différences de réponse"),
            ("Time-based", "Délais de réponse")
        ]
        print_table(["Type", "Principe"], types)
        
        print_info("\n🎯 PAYLOADS DE TEST")
        payloads = [
            "' OR '1'='1",
            "1' UNION SELECT NULL--",
            "1' AND SLEEP(5)--"
        ]
        for p in payloads:
            print_info(f"  {p}")
    
    def _show_lfi_help(self):
        print_header("LFI/RFI - Inclusion de Fichiers")
        print_info("📝 Inclusion de fichiers locaux ou distants.")
        print_info("\n🎯 PAYLOADS LFI")
        payloads = [
            "../../../etc/passwd",
            "....//....//etc/passwd",
            "php://filter/convert.base64-encode/resource=index.php"
        ]
        for p in payloads:
            print_info(f"  {p}")
    
    def _show_command_help(self):
        print_header("Command Injection")
        print_info("📝 Injection de commandes système.")
        print_info("\n🎯 SÉPARATEURS")
        separators = [";", "|", "||", "&", "&&", "$()", "``"]
        for s in separators:
            print_info(f"  {s}")
        
        print_info("\n🎯 PAYLOADS")
        payloads = [
            "; ls",
            "| cat /etc/passwd",
            "& whoami"
        ]
        for p in payloads:
            print_info(f"  {p}")
    
    def _show_upload_help(self):
        print_header("File Upload")
        print_info("📝 Téléversement de fichiers malveillants.")
        print_info("\n🎯 TECHNIQUES DE BYPASS")
        bypasses = [
            ("Double extension", "shell.php.jpg"),
            ("Null byte", "shell.php%00.jpg"),
            ("MIME spoofing", "Content-Type: image/jpeg"),
            ("Magic bytes", "GIF89a<?php ... ?>")
        ]
        for tech, example in bypasses:
            print_info(f"  • {tech:<20} {example}")
    
    def _show_csrf_help(self):
        print_header("CSRF - Cross-Site Request Forgery")
        print_info("📝 Force un utilisateur authentifié à exécuter des actions.")
        print_info("\n🎯 PAYLOADS")
        print_info("  • <img src='http://target.com/delete?id=1'>")
        print_info("  • <form action='http://target.com/delete' method='POST'>")
    
    def _show_ssrf_help(self):
        print_header("SSRF - Server-Side Request Forgery")
        print_info("📝 Force le serveur à faire des requêtes non autorisées.")
        print_info("\n🎯 PAYLOADS")
        print_info("  • http://127.0.0.1")
        print_info("  • http://169.254.169.254/latest/meta-data/")
        print_info("  • file:///etc/passwd")
    
    def _show_xxe_help(self):
        print_header("XXE - XML External Entity")
        print_info("📝 Exploite les parsers XML pour lire des fichiers.")
        print_info("\n🎯 PAYLOADS")
        print_info("  <?xml version=\"1.0\"?>")
        print_info("  <!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>")
        print_info("  <root>&xxe;</root>")
    
    def _show_multi_attack_help(self):
        print_header("Multi-attaques")
        print_info("📝 Exécution de plusieurs attaques simultanément ou séquentiellement.")
        print_info("\n🎯 MODES")
        modes = [
            ("sequential", "Attaques une par une", "Discret"),
            ("parallel", "Attaques simultanées", "Rapide"),
            ("mixed", "Groupes parallèles", "Équilibré")
        ]
        print_table(["Mode", "Description", "Caractéristique"], modes)
        
        print_info("\n📝 CONFIGURATION")
        print_info("  Créez un fichier JSON avec vos attaques")
        print_info("  Exemple: redforge --multi config.json -t example.com")
    
    def _show_reporting_help(self):
        print_header("Génération de rapports")
        print_info("📝 Création de rapports professionnels.")
        print_info("\n🎯 FORMATS SUPPORTÉS")
        formats = ["HTML", "PDF", "JSON", "CSV"]
        for f in formats:
            print_info(f"  • {f}")
        
        print_info("\n📝 EXEMPLES")
        print_info("  redforge -t example.com -p all -o rapport.html")
        print_info("  redforge -t example.com -p all -o rapport.pdf --template executive")
    
    def _show_api_help(self):
        print_header("API Reference")
        print_info("📝 Documentation de l'API REST.")
        print_info("\n🎯 ENDPOINTS PRINCIPAUX")
        endpoints = [
            ("GET", "/api/targets", "Liste des cibles"),
            ("POST", "/api/scan", "Lancer un scan"),
            ("GET", "/api/results/{target}", "Récupérer les résultats"),
            ("POST", "/api/multi-attack", "Lancer une multi-attaque"),
            ("POST", "/api/apt/execute", "Exécuter une opération APT"),
            ("POST", "/api/stealth/config", "Configurer mode furtif")
        ]
        for method, endpoint, desc in endpoints:
            print_info(f"  {method:<6} {endpoint:<40} {desc}")
    
    def _list_available_topics(self):
        """Liste les sujets disponibles"""
        categories = {}
        for topic_id, topic in self.topics.items():
            cat = topic.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(topic_id)
        
        print_info("\n📚 SUJETS DISPONIBLES")
        for cat, topics in categories.items():
            print_info(f"\n  {cat.upper()}:")
            for t in topics:
                print_info(f"    • {t}")
    
    @safe_method(default_return=[])
    def search_help(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Recherche dans l'aide
        
        Args:
            keyword: Mot-clé à rechercher
        
        Returns:
            Liste des résultats
        """
        results = []
        keyword_lower = keyword.lower()
        
        for topic_id, topic in self.topics.items():
            score = 0
            if keyword_lower in topic.title.lower():
                score += 10
            if keyword_lower in topic.content.lower():
                score += 5
            for tag in topic.tags:
                if keyword_lower in tag.lower():
                    score += 3
            for example in topic.examples:
                if keyword_lower in example.lower():
                    score += 2
            
            if score > 0:
                results.append({
                    "id": topic_id,
                    "title": topic.title,
                    "score": score,
                    "category": topic.category
                })
        
        # Trier par score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    @safe_method()
    def show_search_results(self, keyword: str):
        """Affiche les résultats de recherche"""
        results = self.search_help(keyword)
        
        print_header(f"Recherche: {keyword}")
        
        if results:
            print_info(f"📚 {len(results)} résultat(s) trouvé(s):\n")
            for r in results:
                print_info(f"  • {r['title']} [{r['category']}]")
            print_info("\n👉 Tapez 'RedForge --aide-commande <sujet>' pour plus de détails")
        else:
            print_warning("Aucun résultat trouvé")
    
    @safe_method()
    def get_topic(self, topic_id: str) -> Optional[HelpTopic]:
        """Récupère un sujet par son ID"""
        return self.topics.get(topic_id)
    
    @safe_method()
    def get_topics_by_category(self, category: str) -> List[HelpTopic]:
        """Récupère les sujets par catégorie"""
        return [t for t in self.topics.values() if t.category == category]
    
    @safe_method()
    def get_all_categories(self) -> List[str]:
        """Récupère toutes les catégories"""
        return list(set(t.category for t in self.topics.values()))
    
    @safe_method()
    def add_topic(self, topic: HelpTopic):
        """Ajoute un sujet personnalisé"""
        self.topics[topic.id] = topic
    
    @safe_method()
    def remove_topic(self, topic_id: str) -> bool:
        """Supprime un sujet"""
        if topic_id in self.topics:
            del self.topics[topic_id]
            return True
        return False
    
    @safe_method(default_return={})
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du gestionnaire d'aide"""
        return {
            "total_topics": len(self.topics),
            "categories": self.get_all_categories(),
            "topics_by_category": {cat: len(self.get_topics_by_category(cat)) for cat in self.get_all_categories()},
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "language": self.lang
        }


# ============================================
# FONCTIONS DE COMPATIBILITÉ
# ============================================

help_manager = HelpManager()


def get_help_manager() -> HelpManager:
    """Récupère l'instance du gestionnaire d'aide"""
    return help_manager


def get_help_topic(topic_id: str) -> Optional[Dict[str, Any]]:
    """Récupère un sujet d'aide"""
    topic = help_manager.get_topic(topic_id)
    return topic.to_dict() if topic else None


def search_help(keyword: str) -> List[Dict[str, Any]]:
    """Recherche dans l'aide"""
    return help_manager.search_help(keyword)


# ============================================
# TESTS
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Test du Help Manager v2.0 - Ultra Robuste")
    print("=" * 60)
    
    # Test des fonctionnalités
    hm = get_help_manager()
    
    print(f"\n📊 Statistiques: {hm.get_statistics()}")
    print(f"📚 Sujets disponibles: {list(hm.topics.keys())[:10]}...")
    
    # Test d'affichage
    hm.show_help("xss")
    
    # Test de recherche
    hm.show_search_results("injection")
    
    # Test de récupération de sujet
    topic = hm.get_topic("stealth")
    if topic:
        print(f"\n✅ Sujet trouvé: {topic.title}")
    
    print("\n✅ Help Manager fonctionnel")#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedForge v2.0 - Module de gestion d'aide ultra robuste
Gère la documentation et l'aide contextuelle avec support APT, mode furtif
Version avec fallbacks et compatibilité maximale
"""

import json
import os
import sys
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
from enum import Enum
from functools import wraps


# ============================================
# UTILITAIRES ROBUSTES
# ============================================

def safe_method(default_return=None):
    """Décorateur pour méthodes sécurisées (ne plantent jamais)"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                try:
                    print(f"[!] Erreur dans {func.__name__}: {e}", file=sys.stderr)
                except Exception:
                    pass
                return default_return
        return wrapper
    return decorator


# ============================================
# CLASSES PRINCIPALES
# ============================================

class HelpTopic:
    """Classe représentant un sujet d'aide"""
    
    def __init__(self, topic_id: str, title: str, content: str, category: str = "general", 
                 subcategory: str = "", level: str = "beginner"):
        """
        Initialise un sujet d'aide
        
        Args:
            topic_id: Identifiant unique du sujet
            title: Titre du sujet
            content: Contenu du sujet (texte ou HTML)
            category: Catégorie principale
            subcategory: Sous-catégorie
            level: Niveau (beginner, intermediate, advanced, expert)
        """
        self.id = topic_id
        self.title = title
        self.content = content
        self.category = category
        self.subcategory = subcategory
        self.level = level
        self.subtopics: List['HelpTopic'] = []
        self.examples: List[str] = []
        self.related_topics: List[str] = []
        self.tags: List[str] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @safe_method()
    def add_subtopic(self, subtopic: 'HelpTopic'):
        """Ajoute un sous-sujet"""
        self.subtopics.append(subtopic)
    
    @safe_method()
    def add_example(self, example: str):
        """Ajoute un exemple"""
        self.examples.append(example)
    
    @safe_method()
    def add_related_topic(self, topic_id: str):
        """Ajoute un sujet lié"""
        if topic_id not in self.related_topics:
            self.related_topics.append(topic_id)
    
    @safe_method()
    def add_tag(self, tag: str):
        """Ajoute un tag"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    @safe_method()
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "subcategory": self.subcategory,
            "level": self.level,
            "subtopics": [s.to_dict() if hasattr(s, 'to_dict') else str(s) for s in self.subtopics],
            "examples": self.examples,
            "related_topics": self.related_topics,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HelpTopic':
        """Crée un sujet depuis un dictionnaire"""
        topic = cls(
            topic_id=data.get('id', 'unknown'),
            title=data.get('title', 'Sans titre'),
            content=data.get('content', ''),
            category=data.get('category', 'general'),
            subcategory=data.get('subcategory', ''),
            level=data.get('level', 'beginner')
        )
        topic.examples = data.get('examples', [])
        topic.related_topics = data.get('related_topics', [])
        topic.tags = data.get('tags', [])
        return topic
    
    def __str__(self) -> str:
        return f"HelpTopic({self.id}: {self.title})"


class ConsoleColors:
    """Couleurs pour la console avec vérification"""
    RED = '\033[0;31m' if sys.platform != 'win32' else ''
    GREEN = '\033[0;32m' if sys.platform != 'win32' else ''
    YELLOW = '\033[1;33m' if sys.platform != 'win32' else ''
    BLUE = '\033[0;34m' if sys.platform != 'win32' else ''
    MAGENTA = '\033[0;35m' if sys.platform != 'win32' else ''
    CYAN = '\033[0;36m' if sys.platform != 'win32' else ''
    WHITE = '\033[1;37m' if sys.platform != 'win32' else ''
    RESET = '\033[0m' if sys.platform != 'win32' else ''


class SafeConsole:
    """Console sécurisée qui ne plante jamais"""
    
    @staticmethod
    def _print_color(text: str, color: str = ""):
        try:
            if color and sys.platform != 'win32':
                print(f"{color}{text}{ConsoleColors.RESET}")
            else:
                print(text)
        except Exception:
            pass
    
    @staticmethod
    def print_header(text: str):
        SafeConsole._print_color(f"\n{'=' * 60}\n{text}\n{'=' * 60}", ConsoleColors.CYAN)
    
    @staticmethod
    def print_info(text: str):
        SafeConsole._print_color(text, ConsoleColors.GREEN)
    
    @staticmethod
    def print_warning(text: str):
        SafeConsole._print_color(text, ConsoleColors.YELLOW)
    
    @staticmethod
    def print_error(text: str):
        SafeConsole._print_color(text, ConsoleColors.RED)
    
    @staticmethod
    def print_success(text: str):
        SafeConsole._print_color(text, ConsoleColors.GREEN)
    
    @staticmethod
    def print_table(headers: List[str], rows: List[List[str]]):
        """Affiche un tableau formaté"""
        try:
            # Calcul des largeurs
            col_widths = [len(h) for h in headers]
            for row in rows:
                for i, cell in enumerate(row):
                    if i < len(col_widths):
                        col_widths[i] = max(col_widths[i], len(str(cell)))
            
            # Ligne d'en-tête
            header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
            SafeConsole._print_color(header_line, ConsoleColors.CYAN)
            SafeConsole._print_color("-" * len(header_line), ConsoleColors.CYAN)
            
            # Lignes de données
            for row in rows:
                line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
                SafeConsole._print_color(line, ConsoleColors.WHITE)
        except Exception:
            pass


# Tentative d'import du vrai module color_output
try:
    from src.utils.color_output import console as _console
    console = _console
    print_header = getattr(console, 'print_header', SafeConsole.print_header)
    print_info = getattr(console, 'print_info', SafeConsole.print_info)
    print_warning = getattr(console, 'print_warning', SafeConsole.print_warning)
    print_error = getattr(console, 'print_error', SafeConsole.print_error)
    print_success = getattr(console, 'print_success', SafeConsole.print_success)
    print_table = getattr(console, 'print_table', SafeConsole.print_table)
except (ImportError, AttributeError):
    console = SafeConsole()
    print_header = SafeConsole.print_header
    print_info = SafeConsole.print_info
    print_warning = SafeConsole.print_warning
    print_error = SafeConsole.print_error
    print_success = SafeConsole.print_success
    print_table = SafeConsole.print_table


class HelpManager:
    """Gestionnaire d'aide et de documentation ultra robuste"""
    
    def __init__(self, lang: str = "fr"):
        """
        Initialise le gestionnaire d'aide
        
        Args:
            lang: Langue (fr, en)
        """
        self.lang = lang
        self.help_data: Dict[str, Any] = {}
        self.topics: Dict[str, HelpTopic] = {}
        self.stealth_mode = False
        self.apt_mode = False
        self._initialized = False
        
        self._init_topics()
        self._load_help_data()
    
    def _init_topics(self):
        """Initialise les sujets d'aide par défaut"""
        # Sujets principaux
        topics_data = [
            # Catégorie: general
            ("installation", "Installation", "Guide d'installation complet de RedForge", "general", "setup", "beginner"),
            ("usage", "Utilisation", "Guide d'utilisation de base", "general", "usage", "beginner"),
            ("cli", "Ligne de commande", "Documentation de la CLI", "general", "cli", "intermediate"),
            
            # Catégorie: attacks
            ("xss", "Cross-Site Scripting (XSS)", "Guide complet sur les attaques XSS", "attacks", "injection", "intermediate"),
            ("sql", "SQL Injection", "Guide complet sur les injections SQL", "attacks", "injection", "intermediate"),
            ("lfi", "LFI/RFI", "Inclusion de fichiers locaux/distants", "attacks", "file_inclusion", "intermediate"),
            ("command", "Command Injection", "Injection de commandes système", "attacks", "injection", "advanced"),
            ("csrf", "CSRF", "Cross-Site Request Forgery", "attacks", "request_forgery", "intermediate"),
            ("ssrf", "SSRF", "Server-Side Request Forgery", "attacks", "request_forgery", "advanced"),
            ("xxe", "XXE", "XML External Entity", "attacks", "xml", "advanced"),
            ("upload", "File Upload", "Téléversement de fichiers malveillants", "attacks", "file_upload", "intermediate"),
            
            # Catégorie: phases
            ("footprint", "Phase 1: Footprinting", "Reconnaissance et collecte d'informations", "phases", "footprint", "beginner"),
            ("analysis", "Phase 2: Analysis", "Analyse approfondie de l'application", "phases", "analysis", "intermediate"),
            ("scan", "Phase 3: Scanning", "Scan de vulnérabilités", "phases", "scan", "intermediate"),
            ("exploit", "Phase 4: Exploitation", "Exploitation des vulnérabilités", "phases", "exploit", "advanced"),
            
            # Catégorie: features
            ("stealth", "Mode Furtif", "Configuration et utilisation du mode furtif", "features", "stealth", "intermediate"),
            ("multi_attack", "Multi-attaques", "Guide des attaques multiples", "features", "multi", "advanced"),
            ("apt", "Opérations APT", "Guide des opérations APT avancées", "features", "apt", "expert"),
            ("reporting", "Génération de rapports", "Création de rapports professionnels", "features", "reports", "intermediate"),
            ("api", "API Reference", "Documentation de l'API REST", "features", "api", "advanced"),
            
            # Catégorie: tools
            ("nmap", "Nmap Scanner", "Guide d'utilisation de Nmap", "tools", "scanner", "beginner"),
            ("sqlmap", "SQLMap", "Guide d'utilisation de SQLMap", "tools", "injection", "intermediate"),
            ("metasploit", "Metasploit", "Intégration avec Metasploit", "tools", "framework", "advanced"),
            ("hydra", "Hydra", "Force brute avec Hydra", "tools", "bruteforce", "intermediate"),
            ("xsstrike", "XSStrike", "Détection XSS avancée", "tools", "xss", "intermediate"),
            
            # Catégorie: troubleshooting
            ("common_errors", "Erreurs courantes", "Résolution des problèmes fréquents", "troubleshooting", "errors", "beginner"),
            ("debug", "Debug mode", "Guide de débogage", "troubleshooting", "debug", "advanced"),
            ("logs", "Logs", "Analyse des logs", "troubleshooting", "logs", "intermediate")
        ]
        
        for tid, title, content, category, subcat, level in topics_data:
            topic = HelpTopic(tid, title, content, category, subcat, level)
            self.topics[tid] = topic
        
        # Ajout des exemples pour certains sujets
        self._add_examples()
    
    def _add_examples(self):
        """Ajoute des exemples aux sujets"""
        # XSS examples
        if 'xss' in self.topics:
            self.topics['xss'].add_example("<script>alert('XSS')</script>")
            self.topics['xss'].add_example("<img src=x onerror=alert('XSS')>")
            self.topics['xss'].add_related_topic('csrf')
            self.topics['xss'].add_tag('xss')
            self.topics['xss'].add_tag('injection')
        
        # SQL examples
        if 'sql' in self.topics:
            self.topics['sql'].add_example("' OR '1'='1")
            self.topics['sql'].add_example("1' UNION SELECT NULL--")
            self.topics['sql'].add_related_topic('command')
            self.topics['sql'].add_tag('sql')
            self.topics['sql'].add_tag('injection')
        
        # Stealth examples
        if 'stealth' in self.topics:
            self.topics['stealth'].add_example("RedForge --stealth")
            self.topics['stealth'].add_example("RedForge --stealth-level high")
            self.topics['stealth'].add_related_topic('apt')
            self.topics['stealth'].add_tag('stealth')
            self.topics['stealth'].add_tag('evasion')
    
    @safe_method()
    def _load_help_data(self):
        """Charge les données d'aide depuis les fichiers JSON"""
        # Chemins possibles
        paths = [
            Path(__file__).parent.parent / "i18n" / self.lang / "help_texts.json",
            Path(__file__).parent.parent / "i18n" / "fr_FR" / "help_texts.json",
            Path(__file__).parent.parent / "i18n" / "fr" / "help_texts.json",
            Path(__file__).parent.parent / "data" / "help" / f"help_{self.lang}.json"
        ]
        
        for path in paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.help_data = json.load(f)
                        break
                except (json.JSONDecodeError, IOError):
                    continue
        
        # Si aucun fichier trouvé, créer des données par défaut
        if not self.help_data:
            self._create_default_help_data()
    
    def _create_default_help_data(self):
        """Crée des données d'aide par défaut"""
        self.help_data = {
            "welcome": {
                "title": "Bienvenue sur RedForge",
                "description": "Plateforme d'orchestration de pentest web",
                "content": "RedForge est un outil complet pour les tests d'intrusion web."
            },
            "quick_start": {
                "title": "Démarrage rapide",
                "description": "Premiers pas avec RedForge",
                "content": "Utilisez 'RedForge -t cible -p footprint' pour commencer."
            }
        }
    
    @safe_method()
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif"""
        self.stealth_mode = enabled
    
    @safe_method()
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT"""
        self.apt_mode = enabled
    
    @safe_method()
    def show_help(self, topic: Optional[str] = None, section: Optional[str] = None):
        """
        Affiche l'aide
        
        Args:
            topic: Sujet spécifique (optionnel)
            section: Section spécifique (optionnel)
        """
        if self.apt_mode:
            self._show_apt_help()
        elif topic:
            self._show_topic_help(topic, section)
        else:
            self._show_general_help()
    
    def _show_general_help(self):
        """Affiche l'aide générale"""
        print_header("RedForge - Aide Générale v2.0")
        
        print_info("\n📖 SYNTAXE DE BASE")
        print_info("  RedForge [OPTIONS] [ARGUMENTS]\n")
        
        print_info("🔧 OPTIONS PRINCIPALES")
        table_data = [
            ("-t, --target", "Cible à analyser", "RedForge -t example.com"),
            ("-f, --file", "Fichier de cibles", "RedForge -f cibles.txt"),
            ("-p, --phase", "Phase à exécuter", "RedForge -t example.com -p scan"),
            ("-g, --gui", "Interface graphique", "sudo RedForge -g"),
            ("-o, --output", "Fichier de rapport", "RedForge -t example.com -o rapport.html"),
            ("--stealth", "Mode furtif", "RedForge --stealth"),
            ("--apt", "Mode APT", "RedForge --apt"),
            ("--multi", "Multi-attaque", "RedForge --multi config.json"),
            ("--help", "Afficher l'aide", "RedForge --help")
        ]
        
        print_table(["Option", "Description", "Exemple"], table_data)
        
        print_info("\n📚 PHASES DISPONIBLES")
        phases = [
            ("footprint", "Reconnaissance", "Collecte d'informations"),
            ("analysis", "Analyse", "Analyse approfondie"),
            ("scan", "Scan", "Détection de vulnérabilités"),
            ("exploit", "Exploitation", "Exploitation des vulnérabilités"),
            ("all", "Complet", "Toutes les phases")
        ]
        
        print_table(["Phase", "Description", "Détails"], phases)
        
        print_info("\n💡 EXEMPLES")
        examples = [
            "Scan rapide : RedForge -t https://example.com -p footprint",
            "Scan complet : RedForge -t 192.168.1.100 -p all -o rapport.html",
            "Mode furtif : RedForge -t example.com --stealth -p scan",
            "Multi-attaque : RedForge --multi config.json -t example.com",
            "Opération APT : RedForge --apt recon_to_exfil -t example.com",
            "Interface web : sudo RedForge -g"
        ]
        
        for ex in examples:
            print_info(f"  {ex}")
        
        print_info("\n❓ POUR PLUS D'AIDE")
        print_info("  RedForge --aide-commande footprint")
        print_info("  RedForge --aide-commande xss")
        print_info("  RedForge --aide-commande stealth")
        print_info("  RedForge --liste-modules")
    
    def _show_apt_help(self):
        """Affiche l'aide pour le mode APT (discret)"""
        print_info("\n" + "=" * 50)
        print_info("APT Mode - Aide discrète")
        print_info("=" * 50)
        
        print_info("\n🎭 OPÉRATIONS APT DISPONIBLES")
        operations = [
            ("recon_to_exfil", "Reconnaissance → Exfiltration", "Cycle APT complet"),
            ("web_app_compromise", "Compromission Web", "Ciblage d'application web"),
            ("lateral_movement", "Mouvement Latéral", "Propagation sur le réseau"),
            ("persistence", "Persistance", "Maintien de l'accès")
        ]
        
        for op_id, name, desc in operations:
            print_info(f"  • {op_id:<20} {name:<25} {desc}")
        
        print_info("\n⏱️ OPTIONS")
        print_info("  --stealth <level>    Niveau de furtivité (low/medium/high/paranoid)")
        print_info("  --no-cleanup         Désactiver le nettoyage post-opération")
        print_info("  --report             Générer un rapport détaillé")
    
    @safe_method()
    def _show_topic_help(self, topic: str, section: Optional[str] = None):
        """
        Affiche l'aide pour un sujet spécifique
        
        Args:
            topic: Sujet demandé
            section: Section spécifique
        """
        # Map des sujets vers leurs méthodes
        topic_methods = {
            'footprint': self._show_footprint_help,
            'analysis': self._show_analysis_help,
            'scan': self._show_scan_help,
            'exploit': self._show_exploit_help,
            'apt': self._show_apt_detailed_help,
            'stealth': self._show_stealth_help,
            'xss': self._show_xss_help,
            'sql': self._show_sql_help,
            'lfi': self._show_lfi_help,
            'command': self._show_command_help,
            'upload': self._show_upload_help,
            'csrf': self._show_csrf_help,
            'ssrf': self._show_ssrf_help,
            'xxe': self._show_xxe_help,
            'multi_attack': self._show_multi_attack_help,
            'reporting': self._show_reporting_help,
            'api': self._show_api_help
        }
        
        if topic in topic_methods:
            topic_methods[topic]()
        elif topic in self.topics:
            self._show_topic_from_data(topic)
        else:
            print_warning(f"Sujet '{topic}' non trouvé")
            self._list_available_topics()
    
    def _show_topic_from_data(self, topic_id: str):
        """Affiche un sujet depuis les données"""
        topic = self.topics.get(topic_id)
        if topic:
            print_header(topic.title)
            print_info(f"\n📝 {topic.content}")
            
            if topic.examples:
                print_info("\n💡 EXEMPLES")
                for ex in topic.examples:
                    print_info(f"  • {ex}")
            
            if topic.related_topics:
                print_info("\n🔗 SUJETS LIÉS")
                for rel in topic.related_topics:
                    print_info(f"  • {rel}")
            
            if topic.tags:
                print_info(f"\n🏷️ TAGS: {', '.join(topic.tags)}")
        else:
            print_warning(f"Sujet '{topic_id}' non trouvé")
    
    def _show_footprint_help(self):
        print_header("Phase 1: Footprinting - Reconnaissance")
        print_info("📝 Collecte d'informations sur la cible sans être intrusif.")
        print_info("\n🎯 CE QUE CETTE PHASE DÉCOUVRE")
        discoveries = [
            "Adresses IP et sous-domaines",
            "Services et ports ouverts",
            "Technologies web utilisées",
            "Serveurs DNS et emails",
            "Certificats SSL/TLS"
        ]
        for d in discoveries:
            print_info(f"  • {d}")
    
    def _show_analysis_help(self):
        print_header("Phase 2: Analysis - Analyse Approfondie")
        print_info("📝 Analyse détaillée de l'application web.")
        print_info("\n🎯 ANALYSES EFFECTUÉES")
        analyses = [
            "Structure des répertoires",
            "Paramètres GET/POST",
            "Points d'entrée utilisateur",
            "Système d'authentification",
            "Endpoints API"
        ]
        for a in analyses:
            print_info(f"  • {a}")
    
    def _show_scan_help(self):
        print_header("Phase 3: Scanning - Scan de Vulnérabilités")
        print_info("📝 Détection automatisée des vulnérabilités web.")
        print_info("\n🎯 VULNÉRABILITÉS DÉTECTÉES")
        vulns = [
            "Injections SQL (SQLi)",
            "Cross-Site Scripting (XSS)",
            "LFI/RFI",
            "Command Injection",
            "CSRF, SSRF, XXE"
        ]
        for v in vulns:
            print_info(f"  • {v}")
    
    def _show_exploit_help(self):
        print_header("Phase 4: Exploitation")
        print_info("📝 Exploitation des vulnérabilités découvertes.")
        print_info("\n🎯 CAPACITÉS")
        caps = [
            "Shell reverse/bind",
            "Upload de webshells",
            "Élévation de privilèges",
            "Persistance",
            "Exfiltration de données"
        ]
        for c in caps:
            print_info(f"  • {c}")
    
    def _show_apt_detailed_help(self):
        print_header("Opérations APT - Advanced Persistent Threat")
        print_info("📝 Simulation d'attaques avancées avec persistance.")
        print_info("\n🎯 OPÉRATIONS DISPONIBLES")
        ops = [
            ("recon_to_exfil", "Cycle APT complet (6 phases)"),
            ("web_app_compromise", "Compromission d'application web"),
            ("lateral_movement", "Mouvement latéral"),
            ("persistence", "Persistance avancée")
        ]
        for op_id, desc in ops:
            print_info(f"  • {op_id:<20} {desc}")
    
    def _show_stealth_help(self):
        print_header("Mode Furtif - Stealth Mode")
        print_info("📝 Mode discret qui ralentit les requêtes pour éviter la détection.")
        print_info("\n🎯 NIVEAUX DE FURTIVITÉ")
        levels = [
            ("low", "0.5s", "Détection facile"),
            ("medium", "1.5s", "Détection moyenne"),
            ("high", "3.0s", "Difficile à détecter"),
            ("paranoid", "5.0s", "Très difficile")
        ]
        print_table(["Niveau", "Délai", "Risque"], levels)
    
    def _show_xss_help(self):
        print_header("Cross-Site Scripting (XSS)")
        print_info("📝 Injection de scripts malveillants dans les pages web.")
        print_info("\n🎯 TYPES DE XSS")
        types = [
            ("Réfléchi", "Le payload est réfléchi dans la réponse"),
            ("Stocké", "Le payload est stocké sur le serveur"),
            ("DOM-based", "Le payload modifie le DOM")
        ]
        print_table(["Type", "Description"], types)
        
        print_info("\n🎯 PAYLOADS DE TEST")
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        for p in payloads:
            print_info(f"  {p}")
    
    def _show_sql_help(self):
        print_header("SQL Injection")
        print_info("📝 Injection de requêtes SQL malveillantes.")
        print_info("\n🎯 TYPES D'INJECTION SQL")
        types = [
            ("Error-based", "Via messages d'erreur"),
            ("Union-based", "Utilisation de UNION SELECT"),
            ("Boolean-based", "Différences de réponse"),
            ("Time-based", "Délais de réponse")
        ]
        print_table(["Type", "Principe"], types)
        
        print_info("\n🎯 PAYLOADS DE TEST")
        payloads = [
            "' OR '1'='1",
            "1' UNION SELECT NULL--",
            "1' AND SLEEP(5)--"
        ]
        for p in payloads:
            print_info(f"  {p}")
    
    def _show_lfi_help(self):
        print_header("LFI/RFI - Inclusion de Fichiers")
        print_info("📝 Inclusion de fichiers locaux ou distants.")
        print_info("\n🎯 PAYLOADS LFI")
        payloads = [
            "../../../etc/passwd",
            "....//....//etc/passwd",
            "php://filter/convert.base64-encode/resource=index.php"
        ]
        for p in payloads:
            print_info(f"  {p}")
    
    def _show_command_help(self):
        print_header("Command Injection")
        print_info("📝 Injection de commandes système.")
        print_info("\n🎯 SÉPARATEURS")
        separators = [";", "|", "||", "&", "&&", "$()", "``"]
        for s in separators:
            print_info(f"  {s}")
        
        print_info("\n🎯 PAYLOADS")
        payloads = [
            "; ls",
            "| cat /etc/passwd",
            "& whoami"
        ]
        for p in payloads:
            print_info(f"  {p}")
    
    def _show_upload_help(self):
        print_header("File Upload")
        print_info("📝 Téléversement de fichiers malveillants.")
        print_info("\n🎯 TECHNIQUES DE BYPASS")
        bypasses = [
            ("Double extension", "shell.php.jpg"),
            ("Null byte", "shell.php%00.jpg"),
            ("MIME spoofing", "Content-Type: image/jpeg"),
            ("Magic bytes", "GIF89a<?php ... ?>")
        ]
        for tech, example in bypasses:
            print_info(f"  • {tech:<20} {example}")
    
    def _show_csrf_help(self):
        print_header("CSRF - Cross-Site Request Forgery")
        print_info("📝 Force un utilisateur authentifié à exécuter des actions.")
        print_info("\n🎯 PAYLOADS")
        print_info("  • <img src='http://target.com/delete?id=1'>")
        print_info("  • <form action='http://target.com/delete' method='POST'>")
    
    def _show_ssrf_help(self):
        print_header("SSRF - Server-Side Request Forgery")
        print_info("📝 Force le serveur à faire des requêtes non autorisées.")
        print_info("\n🎯 PAYLOADS")
        print_info("  • http://127.0.0.1")
        print_info("  • http://169.254.169.254/latest/meta-data/")
        print_info("  • file:///etc/passwd")
    
    def _show_xxe_help(self):
        print_header("XXE - XML External Entity")
        print_info("📝 Exploite les parsers XML pour lire des fichiers.")
        print_info("\n🎯 PAYLOADS")
        print_info("  <?xml version=\"1.0\"?>")
        print_info("  <!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>")
        print_info("  <root>&xxe;</root>")
    
    def _show_multi_attack_help(self):
        print_header("Multi-attaques")
        print_info("📝 Exécution de plusieurs attaques simultanément ou séquentiellement.")
        print_info("\n🎯 MODES")
        modes = [
            ("sequential", "Attaques une par une", "Discret"),
            ("parallel", "Attaques simultanées", "Rapide"),
            ("mixed", "Groupes parallèles", "Équilibré")
        ]
        print_table(["Mode", "Description", "Caractéristique"], modes)
        
        print_info("\n📝 CONFIGURATION")
        print_info("  Créez un fichier JSON avec vos attaques")
        print_info("  Exemple: redforge --multi config.json -t example.com")
    
    def _show_reporting_help(self):
        print_header("Génération de rapports")
        print_info("📝 Création de rapports professionnels.")
        print_info("\n🎯 FORMATS SUPPORTÉS")
        formats = ["HTML", "PDF", "JSON", "CSV"]
        for f in formats:
            print_info(f"  • {f}")
        
        print_info("\n📝 EXEMPLES")
        print_info("  redforge -t example.com -p all -o rapport.html")
        print_info("  redforge -t example.com -p all -o rapport.pdf --template executive")
    
    def _show_api_help(self):
        print_header("API Reference")
        print_info("📝 Documentation de l'API REST.")
        print_info("\n🎯 ENDPOINTS PRINCIPAUX")
        endpoints = [
            ("GET", "/api/targets", "Liste des cibles"),
            ("POST", "/api/scan", "Lancer un scan"),
            ("GET", "/api/results/{target}", "Récupérer les résultats"),
            ("POST", "/api/multi-attack", "Lancer une multi-attaque"),
            ("POST", "/api/apt/execute", "Exécuter une opération APT"),
            ("POST", "/api/stealth/config", "Configurer mode furtif")
        ]
        for method, endpoint, desc in endpoints:
            print_info(f"  {method:<6} {endpoint:<40} {desc}")
    
    def _list_available_topics(self):
        """Liste les sujets disponibles"""
        categories = {}
        for topic_id, topic in self.topics.items():
            cat = topic.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(topic_id)
        
        print_info("\n📚 SUJETS DISPONIBLES")
        for cat, topics in categories.items():
            print_info(f"\n  {cat.upper()}:")
            for t in topics:
                print_info(f"    • {t}")
    
    @safe_method(default_return=[])
    def search_help(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Recherche dans l'aide
        
        Args:
            keyword: Mot-clé à rechercher
        
        Returns:
            Liste des résultats
        """
        results = []
        keyword_lower = keyword.lower()
        
        for topic_id, topic in self.topics.items():
            score = 0
            if keyword_lower in topic.title.lower():
                score += 10
            if keyword_lower in topic.content.lower():
                score += 5
            for tag in topic.tags:
                if keyword_lower in tag.lower():
                    score += 3
            for example in topic.examples:
                if keyword_lower in example.lower():
                    score += 2
            
            if score > 0:
                results.append({
                    "id": topic_id,
                    "title": topic.title,
                    "score": score,
                    "category": topic.category
                })
        
        # Trier par score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    @safe_method()
    def show_search_results(self, keyword: str):
        """Affiche les résultats de recherche"""
        results = self.search_help(keyword)
        
        print_header(f"Recherche: {keyword}")
        
        if results:
            print_info(f"📚 {len(results)} résultat(s) trouvé(s):\n")
            for r in results:
                print_info(f"  • {r['title']} [{r['category']}]")
            print_info("\n👉 Tapez 'RedForge --aide-commande <sujet>' pour plus de détails")
        else:
            print_warning("Aucun résultat trouvé")
    
    @safe_method()
    def get_topic(self, topic_id: str) -> Optional[HelpTopic]:
        """Récupère un sujet par son ID"""
        return self.topics.get(topic_id)
    
    @safe_method()
    def get_topics_by_category(self, category: str) -> List[HelpTopic]:
        """Récupère les sujets par catégorie"""
        return [t for t in self.topics.values() if t.category == category]
    
    @safe_method()
    def get_all_categories(self) -> List[str]:
        """Récupère toutes les catégories"""
        return list(set(t.category for t in self.topics.values()))
    
    @safe_method()
    def add_topic(self, topic: HelpTopic):
        """Ajoute un sujet personnalisé"""
        self.topics[topic.id] = topic
    
    @safe_method()
    def remove_topic(self, topic_id: str) -> bool:
        """Supprime un sujet"""
        if topic_id in self.topics:
            del self.topics[topic_id]
            return True
        return False
    
    @safe_method(default_return={})
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du gestionnaire d'aide"""
        return {
            "total_topics": len(self.topics),
            "categories": self.get_all_categories(),
            "topics_by_category": {cat: len(self.get_topics_by_category(cat)) for cat in self.get_all_categories()},
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "language": self.lang
        }


# ============================================
# FONCTIONS DE COMPATIBILITÉ
# ============================================

help_manager = HelpManager()


def get_help_manager() -> HelpManager:
    """Récupère l'instance du gestionnaire d'aide"""
    return help_manager


def get_help_topic(topic_id: str) -> Optional[Dict[str, Any]]:
    """Récupère un sujet d'aide"""
    topic = help_manager.get_topic(topic_id)
    return topic.to_dict() if topic else None


def search_help(keyword: str) -> List[Dict[str, Any]]:
    """Recherche dans l'aide"""
    return help_manager.search_help(keyword)


# ============================================
# TESTS
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Test du Help Manager v2.0 - Ultra Robuste")
    print("=" * 60)
    
    # Test des fonctionnalités
    hm = get_help_manager()
    
    print(f"\n📊 Statistiques: {hm.get_statistics()}")
    print(f"📚 Sujets disponibles: {list(hm.topics.keys())[:10]}...")
    
    # Test d'affichage
    hm.show_help("xss")
    
    # Test de recherche
    hm.show_search_results("injection")
    
    # Test de récupération de sujet
    topic = hm.get_topic("stealth")
    if topic:
        print(f"\n✅ Sujet trouvé: {topic.title}")
    
    print("\n✅ Help Manager fonctionnel")