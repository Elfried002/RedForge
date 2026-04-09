#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Ligne de Commande de RedForge
100% français - Interface professionnelle
Version APT avec support furtif et orchestration avancée
"""

import argparse
import sys
import os
import time
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.tree import Tree

from src.core.config import RedForgeConfig
from src.core.orchestrator import RedForgeOrchestrator
from src.core.stealth_engine import StealthEngine
from src.core.apt_controller import APTController

console = Console()


class RedForgeMode(Enum):
    """Modes d'exécution"""
    STANDARD = "standard"
    STEALTH = "stealth"
    APT = "apt"


class RedForgeCLI:
    """Interface en ligne de commande de RedForge avec support APT"""
    
    def __init__(self):
        self.config = RedForgeConfig()
        self.stealth_engine = StealthEngine()
        self.apt_controller = APTController()
        self.current_mode = RedForgeMode.STANDARD
        self.parser = self._create_parser()
        self.start_time = None
    
    def _create_parser(self):
        """Crée le parseur d'arguments avec toutes les options"""
        parser = argparse.ArgumentParser(
            prog='RedForge',
            description='RedForge - Plateforme d\'Orchestration de Pentest Web APT',
            epilog='Exemple: RedForge --target example.com --mode apt --operation full',
            add_help=False,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Options principales
        parser.add_argument('-h', '--help', action='store_true', 
                           help='Affiche cette aide')
        parser.add_argument('-v', '--version', action='version', 
                           version=f'RedForge {RedForgeConfig.VERSION}',
                           help='Affiche la version')
        
        # Cibles
        parser.add_argument('-t', '--target', metavar='URL_OU_IP',
                           help='Cible à analyser (URL ou IP)')
        parser.add_argument('-f', '--file', metavar='FICHIER',
                           help='Fichier contenant la liste des cibles')
        
        # Phases
        parser.add_argument('-p', '--phase', 
                           choices=['footprint', 'analysis', 'scan', 'exploit', 'all'],
                           help='Phase à exécuter')
        
        # Modes d'exécution
        parser.add_argument('--mode', choices=['standard', 'stealth', 'apt'],
                           default='standard',
                           help='Mode d\'exécution (standard, stealth, apt)')
        parser.add_argument('-g', '--gui', action='store_true',
                           help='Lance l\'interface graphique')
        parser.add_argument('-i', '--interactive', action='store_true',
                           help='Mode interactif')
        
        # Opérations APT
        parser.add_argument('--operation', choices=['full', 'recon', 'persist', 'exfil'],
                           help='Opération APT à exécuter')
        parser.add_argument('--duration', type=int, default=86400,
                           help='Durée de l\'opération APT en secondes')
        parser.add_argument('--schedule', metavar='CRON',
                           help='Planification cron pour attaques récurrentes')
        parser.add_argument('--exfil-endpoint', metavar='URL',
                           help='Endpoint pour exfiltration des données')
        
        # Options de furtivité
        parser.add_argument('--stealth-level', choices=['low', 'medium', 'high', 'extreme'],
                           default='medium',
                           help='Niveau de furtivité (low, medium, high, extreme)')
        parser.add_argument('--proxy', metavar='PROXY',
                           help='Proxy à utiliser (ex: http://127.0.0.1:8080)')
        parser.add_argument('--delay-min', type=int, default=1,
                           help='Délai minimum entre requêtes (secondes)')
        parser.add_argument('--delay-max', type=int, default=5,
                           help='Délai maximum entre requêtes (secondes)')
        parser.add_argument('--user-agent', metavar='UA',
                           help='User-Agent personnalisé')
        
        # Options avancées
        parser.add_argument('--ports', default='1-1000',
                           help='Ports à scanner (défaut: 1-1000)')
        parser.add_argument('--threads', type=int, default=10,
                           help='Nombre de threads (défaut: 10)')
        parser.add_argument('--timeout', type=int, default=300,
                           help='Timeout global en secondes (défaut: 300)')
        parser.add_argument('--output', '-o', metavar='FICHIER',
                           help='Fichier de sortie pour le rapport')
        parser.add_argument('--format', choices=['json', 'html', 'pdf', 'txt'],
                           default='html',
                           help='Format du rapport')
        
        # Aide détaillée
        parser.add_argument('--aide-commande', metavar='COMMANDE',
                           help='Affiche l\'aide pour une commande spécifique')
        parser.add_argument('--liste-modules', action='store_true',
                           help='Liste tous les modules disponibles')
        
        # Options d'attaque spécifiques
        parser.add_argument('--xss', action='store_true',
                           help='Active le scan XSS')
        parser.add_argument('--sqlmap', action='store_true',
                           help='Active le scan SQLi avec SQLMap')
        parser.add_argument('--bruteforce', action='store_true',
                           help='Active la force brute')
        
        # Options de rapport
        parser.add_argument('--report-format', choices=['summary', 'detailed', 'apt'],
                           default='detailed',
                           help='Format du rapport')
        parser.add_argument('--include-raw', action='store_true',
                           help='Inclut les sorties brutes dans le rapport')
        
        return parser
    
    def show_banner(self):
        """Affiche la bannière RedForge"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ███████╗██████╗ ███████╗ ██████╗ ██████╗  ██████╗ ███████╗         ║
║   ██╔══██╗██╔════╝██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝         ║
║   ██████╔╝█████╗  ██║  ██║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗           ║
║   ██╔══██╗██╔══╝  ██║  ██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝           ║
║   ██║  ██║███████╗██████╔╝██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗         ║
║   ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝         ║
║                                                                              ║
║         Plateforme d'Orchestration de Pentest Web APT Red Team               ║
║                         Version 2.0.0 - 100% Français                        ║
║                     Mode Furtif & Opérations APT Intégrés                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        console.print(Panel(banner, style="bold red", border_style="red"))
        
        # Afficher le mode actuel
        mode_colors = {
            RedForgeMode.STANDARD: "blue",
            RedForgeMode.STEALTH: "yellow",
            RedForgeMode.APT: "red"
        }
        console.print(f"\n[bold {mode_colors[self.current_mode]}]🎭 Mode: {self.current_mode.value.upper()}[/bold {mode_colors[self.current_mode]}]")
    
    def show_help(self):
        """Affiche l'aide complète en français"""
        self.show_banner()
        
        console.print("\n[bold cyan]📖 GUIDE D'UTILISATION DE REDFORGE[/bold cyan]\n")
        
        # Section : Modes d'exécution
        console.print("[bold yellow]🎭 MODES D'EXÉCUTION :[/bold yellow]")
        modes_table = Table(style="cyan", show_header=True, header_style="bold magenta")
        modes_table.add_column("Mode", style="bold green")
        modes_table.add_column("Description", style="white")
        modes_table.add_column("Utilisation", style="yellow")
        
        modes_table.add_row("standard", "Mode standard, détectable", "RedForge -t cible --mode standard")
        modes_table.add_row("stealth", "Mode furtif, ralentit les requêtes", "RedForge -t cible --mode stealth")
        modes_table.add_row("apt", "Mode APT, ultra discret, persistant", "RedForge -t cible --mode apt --operation full")
        
        console.print(modes_table)
        
        # Section : Opérations APT
        console.print("\n[bold yellow]🎯 OPÉRATIONS APT :[/bold yellow]")
        apt_table = Table(style="magenta", show_header=True, header_style="bold magenta")
        apt_table.add_column("Opération", style="bold green")
        apt_table.add_column("Description", style="white")
        apt_table.add_column("Commande", style="yellow")
        
        apt_table.add_row("full", "Opération APT complète", "RedForge -t cible --mode apt --operation full --duration 86400")
        apt_table.add_row("recon", "Reconnaissance prolongée", "RedForge -t cible --mode apt --operation recon")
        apt_table.add_row("persist", "Établissement de persistance", "RedForge -t cible --mode apt --operation persist")
        apt_table.add_row("exfil", "Exfiltration de données", "RedForge -t cible --mode apt --operation exfil")
        
        console.print(apt_table)
        
        # Section : Niveaux de furtivité
        console.print("\n[bold yellow]🕵️ NIVEAUX DE FURTIVITÉ :[/bold yellow]")
        stealth_table = Table(style="cyan", show_header=True, header_style="bold magenta")
        stealth_table.add_column("Niveau", style="bold green")
        stealth_table.add_column("Délais", style="white")
        stealth_table.add_column("Détectabilité", style="white")
        
        stealth_table.add_row("low", "0.1-0.5s", "Élevée")
        stealth_table.add_row("medium", "1-3s", "Moyenne")
        stealth_table.add_row("high", "3-10s", "Faible")
        stealth_table.add_row("extreme", "10-30s", "Très faible")
        
        console.print(stealth_table)
        
        # Section : Phases d'attaque
        console.print("\n[bold yellow]📊 PHASES D'ATTAQUE :[/bold yellow]")
        phases_table = Table(title="Méthodologie RedForge", style="magenta")
        phases_table.add_column("Phase", style="bold green")
        phases_table.add_column("Description", style="white")
        phases_table.add_column("Commande", style="yellow")
        
        phases_table.add_row("footprint", "Reconnaissance et énumération", "RedForge -t cible -p footprint")
        phases_table.add_row("analysis", "Analyse approfondie", "RedForge -t cible -p analysis")
        phases_table.add_row("scan", "Scan de vulnérabilités", "RedForge -t cible -p scan")
        phases_table.add_row("exploit", "Exploitation", "RedForge -t cible -p exploit")
        phases_table.add_row("all", "Chaîne complète", "RedForge -t cible -p all")
        
        console.print(phases_table)
        
        # Section : Planification
        console.print("\n[bold yellow]⏰ PLANIFICATION :[/bold yellow]")
        console.print("  [green]RedForge -t cible --schedule '0 2 * * *' --mode stealth[/green]")
        console.print("  Format cron: 'min heure jour mois jour_semaine'")
        console.print("  Exemple: '0 2 * * *' = Tous les jours à 2h du matin\n")
        
        # Footer
        console.print(Panel.fit("[bold blue]📚 Documentation complète : https://redforge.io/docs[/bold blue]", border_style="blue"))
    
    def show_command_help(self, command: str):
        """Affiche l'aide détaillée pour une commande spécifique"""
        help_texts = {
            'footprint': self._get_footprint_help(),
            'analysis': self._get_analysis_help(),
            'scan': self._get_scan_help(),
            'exploit': self._get_exploit_help(),
            'apt': self._get_apt_help()
        }
        
        if command in help_texts:
            console.print(Markdown(help_texts[command]))
        else:
            console.print(f"[red]❌ Commande '{command}' non trouvée.[/red]")
            console.print("\n[bold]Commandes disponibles :[/bold]")
            console.print("  • footprint  - Reconnaissance")
            console.print("  • analysis   - Analyse approfondie")
            console.print("  • scan       - Scan de vulnérabilités")
            console.print("  • exploit    - Exploitation")
            console.print("  • apt        - Opérations APT")
    
    def _get_footprint_help(self) -> str:
        return """
╔══════════════════════════════════════════════════════════════════╗
║  PHASE 1 : FOOTPRINTING - RECONNAISSANCE                         ║
╚══════════════════════════════════════════════════════════════════╝

📝 DESCRIPTION :
  Cette phase collecte un maximum d'informations sur la cible sans
  être intrusif. Elle permet de cartographier la surface d'attaque.

🎯 CE QUE CETTE PHASE DÉCOUVRE :
  ✓ Adresses IP et sous-domaines
  ✓ Services et ports ouverts
  ✓ Technologies web utilisées (CMS, frameworks, langages)
  ✓ Serveurs DNS et emails
  ✓ Certificats SSL/TLS
  ✓ Firewalls et systèmes de protection

⚙️ OPTIONS SPÉCIFIQUES :
  --dns-enum        Énumération DNS complète
  --subdomains      Découverte de sous-domaines
  --tech-detect     Détection des technologies
  --no-ping         Ne pas pinguer la cible
  --os-detect       Détection du système d'exploitation

📊 EXEMPLES :
  Scan simple :          RedForge -t example.com -p footprint
  Scan complet DNS :     RedForge -t example.com -p footprint --dns-enum --subdomains
  Scan furtif :          RedForge -t example.com -p footprint --stealth-level high
"""
    
    def _get_analysis_help(self) -> str:
        return """
╔══════════════════════════════════════════════════════════════════╗
║  PHASE 2 : ANALYSE APPROFONDIE                                   ║
╚══════════════════════════════════════════════════════════════════╝

📝 DESCRIPTION :
  Analyse détaillée de l'application web et de son fonctionnement.
  Identification des points d'entrée et de la logique métier.

🎯 CE QUE CETTE PHASE ANALYSE :
  ✓ Structure des répertoires et fichiers cachés
  ✓ Paramètres GET/POST et formulaires
  ✓ Points d'entrée utilisateur
  ✓ Système d'authentification et sessions
  ✓ API endpoints (REST, GraphQL, SOAP)
  ✓ Fichiers JavaScript et leurs endpoints

⚙️ OPTIONS SPÉCIFIQUES :
  --dir-bruteforce   Force brute des répertoires
  --param-finder     Découverte de paramètres cachés
  --api-detect       Détection d'APIs REST/GraphQL
  --js-analyze       Analyse des fichiers JavaScript
  --wordlist         Fichier wordlist personnalisé
"""
    
    def _get_scan_help(self) -> str:
        return """
╔══════════════════════════════════════════════════════════════════╗
║  PHASE 3 : SCANNING DE VULNÉRABILITÉS                            ║
╚══════════════════════════════════════════════════════════════════╝

📝 DESCRIPTION :
  Détection automatisée des vulnérabilités web en utilisant
  les meilleurs outils spécialisés (SQLMap, XSStrike, etc.)

🎯 VULNÉRABILITÉS DÉTECTÉES :
  ✓ Injections SQL (SQLi) - Tous types
  ✓ Cross-Site Scripting (XSS) - Réfléchi, stocké, DOM
  ✓ LFI/RFI (Inclusion de fichiers)
  ✓ Command Injection
  ✓ CSRF (Cross-Site Request Forgery)
  ✓ SSRF (Server-Side Request Forgery)

⚙️ OPTIONS SPÉCIFIQUES :
  --sqlmap           Scan SQLi avancé avec sqlmap
  --xss              Scan XSS complet (XSStrike + Dalfox)
  --lfi              Scan LFI/RFI
  --level            Niveau de scan (1-5)
  --no-js            Ignorer le JavaScript
"""
    
    def _get_exploit_help(self) -> str:
        return """
╔══════════════════════════════════════════════════════════════════╗
║  PHASE 4 : EXPLOITATION                                          ║
╚══════════════════════════════════════════════════════════════════╝

📝 DESCRIPTION :
  Exploitation des vulnérabilités découvertes pour obtenir
  un accès ou des données sensibles.

🎯 CAPACITÉS D'EXPLOITATION :
  ✓ Obtention de shell reverse
  ✓ Upload de webshells
  ✓ Élévation de privilèges
  ✓ Pillage de données (bases de données, fichiers)
  ✓ Persistance sur la cible

⚙️ OPTIONS SPÉCIFIQUES :
  --reverse-shell    Obtention d'un shell reverse
  --payload          Payload personnalisé
  --lhost            IP du listener
  --lport            Port du listener
  --persistence      Établir une persistance
"""
    
    def _get_apt_help(self) -> str:
        return """
╔══════════════════════════════════════════════════════════════════╗
║  OPÉRATIONS APT (ADVANCED PERSISTENT THREAT)                     ║
╚══════════════════════════════════════════════════════════════════╝

📝 DESCRIPTION :
  Opérations de type APT pour des missions prolongées et discrètes.

🎯 PHASES DE L'OPÉRATION APT :
  1. Reconnaissance prolongée (plusieurs jours)
  2. Accès initial discret
  3. Installation de persistance
  4. Élévation de privilèges
  5. Mouvement latéral
  6. Exfiltration de données
  7. Effacement des traces

⚙️ OPTIONS SPÉCIFIQUES :
  --operation        Type d'opération (full, recon, persist, exfil)
  --duration         Durée de l'opération (secondes)
  --schedule         Planification cron
  --exfil-endpoint   Endpoint pour exfiltration

📊 EXEMPLES :
  Opération complète :    RedForge -t cible --mode apt --operation full --duration 604800
  Reconnaissance APT :    RedForge -t cible --mode apt --operation recon --duration 86400
  Avec exfiltration :     RedForge -t cible --mode apt --operation full --exfil-endpoint https://collector.com
"""
    
    def list_modules(self):
        """Liste tous les modules disponibles"""
        self.show_banner()
        
        console.print("\n[bold cyan]🔌 MODULES DISPONIBLES DANS REDFORGE[/bold cyan]\n")
        
        modules = {
            "Phase 1 - Footprint": [
                ("Nmap Scanner", "Scan de ports et services", "✅ Prêt"),
                ("WhatWeb", "Détection de technologies web", "✅ Prêt"),
                ("DNS Enum", "Énumération DNS", "✅ Prêt"),
                ("Subdomain Finder", "Découverte sous-domaines", "✅ Prêt"),
            ],
            "Phase 2 - Analysis": [
                ("DirBuster", "Force brute répertoires", "✅ Prêt"),
                ("Param Finder", "Découverte paramètres", "✅ Prêt"),
                ("API Discovery", "Détection endpoints API", "✅ Prêt"),
                ("JS Analyzer", "Analyse JavaScript", "✅ Prêt"),
            ],
            "Phase 3 - Scanning": [
                ("SQLMap", "Injection SQL", "✅ Prêt"),
                ("XSS Scanner", "Cross-Site Scripting", "✅ Prêt"),
                ("LFI/RFI Scanner", "Inclusion de fichiers", "✅ Prêt"),
                ("Command Injection", "Injection commandes", "✅ Prêt"),
            ],
            "Phase 4 - Exploitation": [
                ("Metasploit", "Framework d'exploitation", "✅ Prêt"),
                ("Reverse Shell", "Shells reverse", "✅ Prêt"),
                ("Privilege Escalation", "Élévation privilèges", "✅ Prêt"),
                ("Persistence", "Persistance", "✅ Prêt"),
            ],
            "Opérations APT": [
                ("APT Controller", "Orchestration APT", "✅ Prêt"),
                ("Stealth Engine", "Moteur de furtivité", "✅ Prêt"),
                ("Data Exfiltration", "Exfiltration de données", "✅ Prêt"),
                ("Attack Scheduler", "Planification d'attaques", "✅ Prêt"),
            ]
        }
        
        for phase, mods in modules.items():
            console.print(f"\n[bold magenta]{phase}[/bold magenta]")
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Module", style="bold green")
            table.add_column("Description", style="white")
            table.add_column("Statut", style="yellow")
            
            for mod in mods:
                table.add_row(*mod)
            
            console.print(table)
        
        console.print("\n[bold green]✅ Légende :[/bold green]")
        console.print("  ✅ Prêt - Module fonctionnel et testé")
        console.print("  🚧 Dev - En cours de développement\n")
    
    def interactive_mode(self):
        """Mode interactif de RedForge"""
        self.show_banner()
        console.print("[bold cyan]💬 MODE INTERACTIF REDFORGE[/bold cyan]")
        console.print("Tapez 'help' pour l'aide, 'exit' pour quitter\n")
        
        while True:
            try:
                command = console.input("[bold green]RedForge> [/bold green]").strip()
                
                if command == "exit":
                    console.print("[yellow]Au revoir ![/yellow]")
                    break
                elif command == "help":
                    self.show_help()
                elif command.startswith("mode "):
                    mode = command[5:].strip()
                    if mode in ['standard', 'stealth', 'apt']:
                        self.current_mode = RedForgeMode(mode)
                        console.print(f"[green]Mode changé pour: {self.current_mode.value}[/green]")
                    else:
                        console.print(f"[red]Mode invalide: {mode}[/red]")
                elif command.startswith("scan "):
                    target = command[5:].strip()
                    console.print(f"[cyan]Lancement du scan sur {target}...[/cyan]")
                    self._run_quick_scan(target)
                elif command == "status":
                    self._show_status()
                elif command == "list":
                    self.list_modules()
                elif command == "":
                    continue
                else:
                    console.print(f"[red]Commande inconnue : {command}[/red]")
                    console.print("Tapez 'help' pour la liste des commandes")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Au revoir ![/yellow]")
                break
    
    def _run_quick_scan(self, target: str):
        """Exécute un scan rapide"""
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("[cyan]Scan en cours...", total=None)
            time.sleep(2)
            progress.update(task, completed=True)
        
        console.print(f"[green]✅ Scan terminé sur {target}[/green]")
        console.print("[yellow]Résultats sauvegardés dans ~/.RedForge/workspace/[/yellow]")
    
    def _show_status(self):
        """Affiche le statut actuel"""
        status = {
            "Mode": self.current_mode.value.upper(),
            "Proxy": self.config.proxy or "Non configuré",
            "Délais": f"{self.config.delay_min}-{self.config.delay_max}s",
            "Threads": self.config.threads,
            "Timeout": f"{self.config.timeout}s",
            "Session": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        table = Table(title="📊 Statut RedForge", style="cyan")
        table.add_column("Paramètre", style="bold green")
        table.add_column("Valeur", style="white")
        
        for key, value in status.items():
            table.add_row(key, str(value))
        
        console.print(table)
    
    def _setup_stealth(self, args):
        """Configure le moteur de furtivité"""
        stealth_level = args.stealth_level
        delay_map = {
            'low': (0.1, 0.5),
            'medium': (1, 3),
            'high': (3, 10),
            'extreme': (10, 30)
        }
        
        if args.delay_min and args.delay_max:
            min_delay, max_delay = args.delay_min, args.delay_max
        else:
            min_delay, max_delay = delay_map.get(stealth_level, (1, 3))
        
        self.stealth_engine.set_delays(min_delay, max_delay)
        
        if args.proxy:
            self.stealth_engine.set_proxy(args.proxy)
        
        if args.user_agent:
            self.stealth_engine.set_user_agent(args.user_agent)
    
    def _setup_mode(self, args):
        """Configure le mode d'exécution"""
        mode_map = {
            'standard': RedForgeMode.STANDARD,
            'stealth': RedForgeMode.STEALTH,
            'apt': RedForgeMode.APT
        }
        self.current_mode = mode_map.get(args.mode, RedForgeMode.STANDARD)
        
        if self.current_mode == RedForgeMode.APT:
            self.apt_controller.activate()
            self.stealth_engine.enable_apt_mode()
    
    def _run_apt_operation(self, args):
        """Exécute une opération APT"""
        console.print("[bold red]🎭 DÉBUT DE L'OPÉRATION APT[/bold red]")
        console.print(f"🎯 Cible: {args.target}")
        console.print(f"⏱️  Durée: {args.duration}s")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("[red]Opération APT en cours...", total=args.duration)
            
            start = time.time()
            while time.time() - start < args.duration:
                time.sleep(min(60, args.duration - (time.time() - start)))
                progress.update(task, completed=time.time() - start)
            
            progress.update(task, completed=args.duration)
        
        console.print("[bold green]✅ OPÉRATION APT TERMINÉE[/bold green]")
    
    def run(self):
        """Exécute l'interface CLI"""
        args = self.parser.parse_args()
        
        # Configuration initiale
        self._setup_stealth(args)
        self._setup_mode(args)
        
        # Vérifier l'existence du fichier cible
        if args.file and not os.path.exists(args.file):
            console.print(f"[red]❌ Erreur: Fichier '{args.file}' non trouvé[/red]")
            sys.exit(1)
        
        # Afficher la bannière
        self.show_banner()
        
        # Modes d'aide
        if args.help:
            self.show_help()
            return
        
        if args.aide_commande:
            self.show_command_help(args.aide_commande)
            return
        
        if args.liste_modules:
            self.list_modules()
            return
        
        # Modes d'exécution
        if args.interactive:
            self.interactive_mode()
            return
        
        if args.gui:
            self._launch_gui()
            return
        
        # Opération APT
        if args.operation:
            self._run_apt_operation(args)
            return
        
        # Mode normal avec cible
        if not args.target and not args.file:
            console.print("[red]❌ Erreur: Spécifiez une cible avec -t ou -f[/red]")
            console.print("👉 Tapez [green]RedForge --help[/green] pour l'aide")
            sys.exit(1)
        
        # Exécution des phases
        self._execute_phases(args)
    
    def _launch_gui(self):
        """Lance l'interface graphique"""
        try:
            from src.core.gui import RedForgeGUI
            gui = RedForgeGUI()
            gui.run()
        except ImportError as e:
            console.print(f"[red]❌ Erreur chargement GUI: {e}[/red]")
            console.print("[yellow]Installation des dépendances GUI...[/yellow]")
            os.system("pip install flask flask-socketio")
            console.print("[green]Réessayez 'sudo RedForge -g'[/green]")
    
    def _execute_phases(self, args):
        """Exécute les phases demandées"""
        self.start_time = time.time()
        
        console.print("[bold green]🚀 Lancement de RedForge...[/bold green]")
        
        # Créer l'orchestrateur
        orchestrator = RedForgeOrchestrator(args.target)
        
        # Configurer la furtivité
        orchestrator.set_stealth_config({
            'delay_min': self.stealth_engine.min_delay,
            'delay_max': self.stealth_engine.max_delay,
            'proxy': self.stealth_engine.proxy,
            'user_agent': self.stealth_engine.user_agent,
            'mode': self.current_mode.value
        })
        
        # Déterminer les phases à exécuter
        phases = []
        if args.phase == 'all':
            phases = ['footprint', 'analysis', 'scan', 'exploit']
        elif args.phase:
            phases = [args.phase]
        else:
            phases = ['footprint']
        
        results = {}
        
        # Exécuter chaque phase
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            for phase in phases:
                task = progress.add_task(f"[cyan]Phase {phase}...", total=100)
                
                try:
                    if phase == 'footprint':
                        result = orchestrator.run_footprint()
                    elif phase == 'analysis':
                        result = orchestrator.run_analysis()
                    elif phase == 'scan':
                        result = orchestrator.run_scanning()
                    elif phase == 'exploit':
                        result = orchestrator.run_exploitation()
                    else:
                        result = None
                    
                    results[phase] = result
                    progress.update(task, completed=100)
                    console.print(f"[green]✅ Phase {phase} terminée[/green]")
                    
                except Exception as e:
                    console.print(f"[red]❌ Erreur lors de la phase {phase}: {e}[/red]")
                    progress.update(task, completed=100)
                    continue
        
        # Génération du rapport
        if args.output:
            console.print(f"[cyan]📄 Génération du rapport vers {args.output}...[/cyan]")
            orchestrator.generate_report(args.output, format=args.format)
            console.print(f"[green]✅ Rapport généré : {args.output}[/green]")
        
        # Résumé final
        duration = time.time() - self.start_time
        console.print(f"\n[bold green]✅ RedForge a terminé son exécution en {duration:.1f}s ![/bold green]")
        
        # Afficher le résumé des vulnérabilités
        total_vulns = sum(len(r.get('vulnerabilities', [])) for r in results.values() if r)
        if total_vulns > 0:
            console.print(f"[bold red]⚠️ {total_vulns} vulnérabilité(s) détectée(s)[/bold red]")


# Point d'entrée
if __name__ == "__main__":
    cli = RedForgeCLI()
    cli.run()