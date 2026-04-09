#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitaires RedForge
Modules de support pour la plateforme
Version avec support furtif, APT et utilitaires avancés
"""

from typing import Dict, Any, Optional, List

# Logging
from src.utils.logger import Logger, get_logger, setup_logging

# Output coloré
from src.utils.color_output import ColorOutput, console, print_success, print_error, print_warning, print_info

# Génération de rapports
from src.utils.report_generator import ReportGenerator, ReportFormat

# Gestion d'aide
from src.utils.help_manager import HelpManager, HelpTopic

# Vérification des dépendances
from src.utils.dependency_checker import DependencyChecker, check_dependencies, install_dependency

# Installation d'outils
from src.utils.tool_installer import ToolInstaller, install_tool, check_tool

# Utilitaires réseau
from src.utils.network import NetworkUtils, is_port_open, get_local_ip, resolve_hostname

# Utilitaires de parsing
from src.utils.parser import ParserUtils, parse_url, extract_params, parse_headers

# Utilitaires cryptographiques
from src.utils.crypto import CryptoUtils, hash_password, verify_hash, generate_token

# Utilitaires de furtivité
from src.utils.stealth_utils import StealthUtils, StealthConfig, random_delay, rotate_user_agent

# Utilitaires de fichiers
from src.utils.file_utils import FileUtils, read_file, write_file, list_files

# Utilitaires de validation
from src.utils.validator import Validator, is_valid_url, is_valid_ip, is_valid_domain

# Configuration
from src.utils.config_utils import ConfigUtils, load_config, save_config, get_config_value

# Métriques
from src.utils.metrics import MetricsCollector, timing_decorator, log_execution

# Cache
from src.utils.cache import CacheManager, cached

# Threading
from src.utils.threading_utils import ThreadPool, TaskManager, parallel_execute

# API client
from src.utils.api_client import APIClient, APIRequest, APIResponse


# Version du module utils
__version__ = "2.0.0"


# Instance globale du logger
logger = get_logger()


# Fonctions de commodité
def init_utils(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Initialise tous les utilitaires RedForge
    
    Args:
        config: Configuration optionnelle
        
    Returns:
        True si l'initialisation a réussi
    """
    if config:
        # Configurer le logging
        log_level = config.get('log_level', 'INFO')
        setup_logging(level=log_level)
        
        # Configurer le mode furtif
        if config.get('stealth_mode', False):
            StealthUtils.enable_stealth_mode()
        
        if config.get('apt_mode', False):
            StealthUtils.enable_apt_mode()
    
    logger.info(f"Utilitaires RedForge v{__version__} initialisés")
    return True


def get_utils_info() -> Dict[str, Any]:
    """
    Retourne les informations sur les utilitaires
    
    Returns:
        Dictionnaire d'informations
    """
    return {
        "version": __version__,
        "modules": [
            "logger", "color_output", "report_generator", "help_manager",
            "dependency_checker", "tool_installer", "network", "parser",
            "crypto", "stealth_utils", "file_utils", "validator",
            "config_utils", "metrics", "cache", "threading_utils", "api_client"
        ],
        "stealth_enabled": StealthUtils.is_stealth_enabled(),
        "apt_enabled": StealthUtils.is_apt_enabled()
    }


# Export des classes principales
__all__ = [
    # Version
    '__version__',
    'init_utils',
    'get_utils_info',
    'logger',
    
    # Logging
    'Logger',
    'get_logger',
    'setup_logging',
    
    # Color output
    'ColorOutput',
    'console',
    'print_success',
    'print_error',
    'print_warning',
    'print_info',
    
    # Report
    'ReportGenerator',
    'ReportFormat',
    
    # Help
    'HelpManager',
    'HelpTopic',
    
    # Dependencies
    'DependencyChecker',
    'check_dependencies',
    'install_dependency',
    
    # Tools
    'ToolInstaller',
    'install_tool',
    'check_tool',
    
    # Network
    'NetworkUtils',
    'is_port_open',
    'get_local_ip',
    'resolve_hostname',
    
    # Parser
    'ParserUtils',
    'parse_url',
    'extract_params',
    'parse_headers',
    
    # Crypto
    'CryptoUtils',
    'hash_password',
    'verify_hash',
    'generate_token',
    
    # Stealth
    'StealthUtils',
    'StealthConfig',
    'random_delay',
    'rotate_user_agent',
    
    # Files
    'FileUtils',
    'read_file',
    'write_file',
    'list_files',
    
    # Validator
    'Validator',
    'is_valid_url',
    'is_valid_ip',
    'is_valid_domain',
    
    # Config
    'ConfigUtils',
    'load_config',
    'save_config',
    'get_config_value',
    
    # Metrics
    'MetricsCollector',
    'timing_decorator',
    'log_execution',
    
    # Cache
    'CacheManager',
    'cached',
    
    # Threading
    'ThreadPool',
    'TaskManager',
    'parallel_execute',
    
    # API
    'APIClient',
    'APIRequest',
    'APIResponse'
]


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print(f"Utilitaires RedForge v{__version__}")
    print("=" * 60)
    
    # Initialiser
    init_utils({'log_level': 'INFO'})
    
    # Afficher les informations
    info = get_utils_info()
    print(f"\n📦 Modules disponibles: {len(info['modules'])}")
    print(f"🕵️ Mode furtif: {info['stealth_enabled']}")
    print(f"🎭 Mode APT: {info['apt_enabled']}")
    
    # Tester la console
    print("\n🎨 Test de la console colorée:")
    print_success("Message de succès")
    print_error("Message d'erreur")
    print_warning("Message d'avertissement")
    print_info("Message d'information")
    
    print("\n✅ Module utils chargé avec succès")
    print("\n💡 Utilitaires disponibles:")
    print("   - Logging, console colorée, génération de rapports")
    print("   - Vérification des dépendances, installation d'outils")
    print("   - Utilitaires réseau, parsing, crypto")
    print("   - Mode furtif, APT, cache, threading, API client")