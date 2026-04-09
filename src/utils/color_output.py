#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de sortie colorée pour RedForge
Améliore la lisibilité de la console avec support furtif
Version avec mode silencieux, APT et sortie avancée
"""

import sys
import time
import threading
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime


# Codes ANSI pour les couleurs
class Colors:
    """Codes couleur ANSI"""
    # Couleurs de base
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Couleurs claires
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Couleurs de fond
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_BRIGHT_BLACK = '\033[100m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_MAGENTA = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKE = '\033[9m'
    
    # Reset
    RESET = '\033[0m'


class SeverityColor:
    """Couleurs par sévérité de vulnérabilité"""
    CRITICAL = Colors.BRIGHT_RED + Colors.BOLD + Colors.BLINK
    HIGH = Colors.BRIGHT_RED + Colors.BOLD
    MEDIUM = Colors.BRIGHT_YELLOW + Colors.BOLD
    LOW = Colors.BRIGHT_BLUE
    INFO = Colors.BRIGHT_CYAN


class LogLevel:
    """Niveaux de log avec couleurs"""
    DEBUG = Colors.BRIGHT_BLACK + Colors.DIM
    INFO = Colors.BRIGHT_CYAN
    SUCCESS = Colors.BRIGHT_GREEN + Colors.BOLD
    WARNING = Colors.BRIGHT_YELLOW + Colors.BOLD
    ERROR = Colors.BRIGHT_RED + Colors.BOLD
    CRITICAL = Colors.BRIGHT_RED + Colors.BOLD + Colors.BLINK
    APT = Colors.BRIGHT_MAGENTA + Colors.BOLD + Colors.ITALIC
    STEALTH = Colors.BRIGHT_BLACK + Colors.ITALIC


class OutputMode(Enum):
    """Modes de sortie"""
    NORMAL = "normal"
    VERBOSE = "verbose"
    QUIET = "quiet"
    SILENT = "silent"
    APT = "apt"
    STEALTH = "stealth"


class Spinner:
    """Animation de chargement en console"""
    
    def __init__(self, message: str = "Chargement", delay: float = 0.1):
        self.message = message
        self.delay = delay
        self._running = False
        self._thread = None
        self._frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def start(self):
        """Démarre l'animation"""
        self._running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Arrête l'animation"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        # Effacer la ligne
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()
    
    def _animate(self):
        idx = 0
        while self._running:
            frame = self._frames[idx % len(self._frames)]
            sys.stdout.write(f'\r{Colors.BRIGHT_CYAN}{frame}{Colors.RESET} {self.message}...')
            sys.stdout.flush()
            time.sleep(self.delay)
            idx += 1


class ColorOutput:
    """Gestionnaire de sortie colorée pour la console avec support furtif"""
    
    def __init__(self, enabled: bool = True, mode: OutputMode = OutputMode.NORMAL):
        """
        Initialise le gestionnaire de couleurs
        
        Args:
            enabled: Activer/désactiver les couleurs
            mode: Mode de sortie
        """
        self.enabled = enabled and sys.stdout.isatty()
        self.mode = mode
        self.spinner = None
        self._log_buffer = []
        self._last_output_time = 0
        self._min_output_delay = 0.5  # Délai minimum entre les sorties en mode furtif
    
    def set_mode(self, mode: OutputMode):
        """Change le mode de sortie"""
        self.mode = mode
    
    def is_quiet(self) -> bool:
        """Vérifie si le mode est silencieux"""
        return self.mode in [OutputMode.QUIET, OutputMode.SILENT, OutputMode.APT, OutputMode.STEALTH]
    
    def _should_output(self) -> bool:
        """Vérifie si on doit afficher la sortie (rate limiting en mode furtif)"""
        if self.mode == OutputMode.SILENT:
            return False
        
        if self.mode in [OutputMode.APT, OutputMode.STEALTH]:
            now = time.time()
            if now - self._last_output_time < self._min_output_delay:
                return False
            self._last_output_time = now
        
        return True
    
    def _colorize(self, text: str, color: str, style: str = "") -> str:
        """Applique une couleur à un texte"""
        if not self.enabled or self.mode == OutputMode.SILENT:
            return text
        return f"{style}{color}{text}{Colors.RESET}"
    
    # Méthodes pour les couleurs de base
    def black(self, text: str) -> str:
        return self._colorize(text, Colors.BLACK)
    
    def red(self, text: str) -> str:
        return self._colorize(text, Colors.RED)
    
    def green(self, text: str) -> str:
        return self._colorize(text, Colors.GREEN)
    
    def yellow(self, text: str) -> str:
        return self._colorize(text, Colors.YELLOW)
    
    def blue(self, text: str) -> str:
        return self._colorize(text, Colors.BLUE)
    
    def magenta(self, text: str) -> str:
        return self._colorize(text, Colors.MAGENTA)
    
    def cyan(self, text: str) -> str:
        return self._colorize(text, Colors.CYAN)
    
    def white(self, text: str) -> str:
        return self._colorize(text, Colors.WHITE)
    
    # Couleurs claires
    def bright_black(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_BLACK)
    
    def bright_red(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_RED)
    
    def bright_green(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_GREEN)
    
    def bright_yellow(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_YELLOW)
    
    def bright_blue(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_BLUE)
    
    def bright_magenta(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_MAGENTA)
    
    def bright_cyan(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_CYAN)
    
    def bright_white(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_WHITE)
    
    # Styles
    def bold(self, text: str) -> str:
        return self._colorize(text, "", Colors.BOLD)
    
    def dim(self, text: str) -> str:
        return self._colorize(text, "", Colors.DIM)
    
    def italic(self, text: str) -> str:
        return self._colorize(text, "", Colors.ITALIC)
    
    def underline(self, text: str) -> str:
        return self._colorize(text, "", Colors.UNDERLINE)
    
    def strike(self, text: str) -> str:
        return self._colorize(text, "", Colors.STRIKE)
    
    # Sévérité
    def critical(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_RED, Colors.BOLD)
    
    def high(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_RED)
    
    def medium(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_YELLOW)
    
    def low(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_BLUE)
    
    def info(self, text: str) -> str:
        return self._colorize(text, Colors.BRIGHT_CYAN)
    
    # Niveaux de log
    def debug(self, text: str) -> str:
        if self.mode == OutputMode.VERBOSE and self._should_output():
            return self._colorize(f"[DEBUG] {text}", Colors.BRIGHT_BLACK, Colors.DIM)
        return ""
    
    def success(self, text: str) -> str:
        if self._should_output():
            return self._colorize(f"[✓] {text}", Colors.BRIGHT_GREEN, Colors.BOLD)
        return ""
    
    def warning(self, text: str) -> str:
        if self._should_output():
            return self._colorize(f"[!] {text}", Colors.BRIGHT_YELLOW, Colors.BOLD)
        return ""
    
    def error(self, text: str) -> str:
        if self._should_output():
            return self._colorize(f"[✗] {text}", Colors.BRIGHT_RED, Colors.BOLD)
        return ""
    
    def apt(self, text: str) -> str:
        """Message APT (mode discret)"""
        if self.mode == OutputMode.APT and self._should_output():
            return self._colorize(f"[APT] {text}", Colors.BRIGHT_MAGENTA, Colors.ITALIC)
        return ""
    
    def stealth(self, text: str) -> str:
        """Message furtif (presque invisible)"""
        if self.mode == OutputMode.STEALTH and self._should_output():
            return self._colorize(f"[*] {text}", Colors.BRIGHT_BLACK, Colors.DIM)
        return ""
    
    # Méthodes d'affichage direct
    def print_success(self, text: str):
        """Affiche un message de succès"""
        msg = self.success(text)
        if msg:
            print(msg)
            self._log_buffer.append(("SUCCESS", text))
    
    def print_error(self, text: str):
        """Affiche un message d'erreur"""
        msg = self.error(text)
        if msg:
            print(msg)
            self._log_buffer.append(("ERROR", text))
    
    def print_warning(self, text: str):
        """Affiche un message d'avertissement"""
        msg = self.warning(text)
        if msg:
            print(msg)
            self._log_buffer.append(("WARNING", text))
    
    def print_info(self, text: str):
        """Affiche un message d'information"""
        msg = self.info(f"[i] {text}")
        if msg and self._should_output():
            print(msg)
            self._log_buffer.append(("INFO", text))
    
    def print_header(self, text: str):
        """Affiche un en-tête"""
        if self._should_output():
            print(self.bold(self.cyan(f"\n{'=' * 60}")))
            print(self.bold(self.cyan(text)))
            print(self.bold(self.cyan(f"{'=' * 60}")))
            self._log_buffer.append(("HEADER", text))
    
    def print_apt_header(self, text: str):
        """Affiche un en-tête APT"""
        if self.mode == OutputMode.APT and self._should_output():
            print(self.apt(f"\n{'=' * 50}"))
            print(self.apt(text))
            print(self.apt(f"{'=' * 50}"))
    
    def print_table(self, headers: List[str], rows: List[List[Any]], 
                   border: bool = True, title: str = None):
        """
        Affiche un tableau formaté
        
        Args:
            headers: En-têtes des colonnes
            rows: Lignes du tableau
            border: Afficher les bordures
            title: Titre du tableau
        """
        if not rows or not self._should_output():
            return
        
        if title:
            print(self.bold(self.cyan(f"\n{title}")))
            print(self.dim("─" * len(title)))
        
        # Calculer les largeurs des colonnes
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Ajouter une marge
        col_widths = [w + 2 for w in col_widths]
        
        # Ligne de séparation
        if border:
            separator = "+" + "+".join("-" * w for w in col_widths) + "+"
            print(self.dim(separator))
        
        # En-têtes
        header_line = "|"
        for i, header in enumerate(headers):
            header_line += f" {self.bold(self.cyan(header))}{' ' * (col_widths[i] - len(header) - 1)}|"
        print(header_line)
        
        if border:
            print(self.dim(separator))
        
        # Lignes
        for row in rows:
            line = "|"
            for i, cell in enumerate(row):
                cell_str = str(cell)
                if i < len(col_widths):
                    line += f" {cell_str}{' ' * (col_widths[i] - len(cell_str) - 1)}|"
            print(line)
        
        if border:
            print(self.dim(separator))
    
    def print_progress(self, current: int, total: int, prefix: str = "",
                       bar_length: int = 50, show_percent: bool = True):
        """
        Affiche une barre de progression
        
        Args:
            current: Progression actuelle
            total: Total
            prefix: Texte avant la barre
            bar_length: Longueur de la barre
            show_percent: Afficher le pourcentage
        """
        if not self._should_output():
            return
        
        percent = current / total
        filled = int(round(percent * bar_length))
        arrow = '█' * filled
        spaces = '░' * (bar_length - filled)
        
        bar = f"[{self.green(arrow)}{self.dim(spaces)}]"
        
        if show_percent:
            bar += f" {percent * 100:.1f}%"
        
        if prefix:
            print(f"\r{prefix} {bar}", end='')
        else:
            print(f"\r{bar}", end='')
        
        if current == total:
            print()
    
    def start_spinner(self, message: str = "Chargement"):
        """Démarre un spinner de chargement"""
        if self.mode in [OutputMode.QUIET, OutputMode.SILENT]:
            return
        self.spinner = Spinner(message)
        self.spinner.start()
    
    def stop_spinner(self):
        """Arrête le spinner de chargement"""
        if self.spinner:
            self.spinner.stop()
            self.spinner = None
    
    def print_vulnerability(self, vuln: Dict[str, Any]):
        """
        Affiche une vulnérabilité formatée
        
        Args:
            vuln: Dictionnaire de vulnérabilité
        """
        if not self._should_output():
            return
        
        severity = vuln.get('severity', 'MEDIUM').upper()
        severity_color = getattr(self, severity.lower(), self.medium)
        
        print(f"\n{severity_color('▶')} {self.bold(vuln.get('name', 'Unknown'))}")
        print(f"   {self.dim('Type:')} {vuln.get('type', 'Unknown')}")
        print(f"   {self.dim('Sévérité:')} {severity_color(severity)}")
        print(f"   {self.dim('Paramètre:')} {vuln.get('parameter', 'N/A')}")
        print(f"   {self.dim('Description:')} {vuln.get('description', vuln.get('details', 'N/A'))}")
        
        if vuln.get('solution'):
            print(f"   {self.dim('Solution:')} {self.green(vuln['solution'])}")
    
    def get_log_buffer(self) -> List[tuple]:
        """Retourne le buffer de logs"""
        return self._log_buffer.copy()
    
    def clear_log_buffer(self):
        """Efface le buffer de logs"""
        self._log_buffer = []
    
    def save_logs(self, filename: str):
        """Sauvegarde les logs dans un fichier"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for level, msg in self._log_buffer:
                    f.write(f"[{level}] {msg}\n")
            return True
        except:
            return False


# Instance globale pour utilisation facile
console = ColorOutput()

# Fonctions de commodité
def print_success(text: str):
    console.print_success(text)

def print_error(text: str):
    console.print_error(text)

def print_warning(text: str):
    console.print_warning(text)

def print_info(text: str):
    console.print_info(text)

def print_header(text: str):
    console.print_header(text)

def print_apt(text: str):
    console.apt(text)

def set_output_mode(mode: Union[str, OutputMode]):
    """Change le mode de sortie"""
    if isinstance(mode, str):
        mode = OutputMode(mode)
    console.set_mode(mode)

def is_quiet() -> bool:
    """Vérifie si le mode est silencieux"""
    return console.is_quiet()


if __name__ == "__main__":
    # Test des couleurs
    print_header("Test des couleurs RedForge")
    
    console.print_success("Test de succès")
    console.print_error("Test d'erreur")
    console.print_warning("Test d'avertissement")
    console.print_info("Test d'information")
    
    print(console.critical("Message critique"))
    print(console.high("Haute sévérité"))
    print(console.medium("Sévérité moyenne"))
    print(console.low("Basse sévérité"))
    
    # Test tableau
    console.print_table(
        headers=["ID", "Nom", "Statut"],
        rows=[
            [1, "Test 1", "Succès"],
            [2, "Test 2", "Échec"],
            [3, "Test 3", "En cours"]
        ],
        title="Tableau de test"
    )
    
    # Test progression
    for i in range(0, 101, 20):
        console.print_progress(i, 100, "Scan en cours:")
        time.sleep(0.2)
    
    # Test mode APT
    console.set_mode(OutputMode.APT)
    console.print_apt_header("Mode APT activé")
    console.apt("Opération discrète en cours")
    
    # Test vulnérabilité
    console.set_mode(OutputMode.NORMAL)
    console.print_vulnerability({
        "name": "Injection SQL",
        "type": "SQL Injection",
        "severity": "CRITICAL",
        "parameter": "id",
        "description": "Injection SQL dans le paramètre id",
        "solution": "Utiliser des requêtes paramétrées"
    })