#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Système de plugins pour RedForge
Permet d'étendre les fonctionnalités de la plateforme
Version avec support furtif, APT et gestion avancée
"""

from typing import List, Dict, Any, Optional
from enum import Enum

from src.plugins.plugin_manager import (
    PluginManager,
    Plugin,
    PluginType,
    PluginStatus,
    PluginInfo
)

# Version du système de plugins
__version__ = "2.0.0"


class PluginCategory(Enum):
    """Catégories de plugins supplémentaires"""
    ATTACK = "attack"
    SCANNER = "scanner"
    EXPLOIT = "exploit"
    REPORT = "report"
    INTEGRATION = "integration"
    UTILITY = "utility"
    STEALTH = "stealth"
    APT = "apt"


# Instance globale du gestionnaire de plugins
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """
    Retourne l'instance globale du gestionnaire de plugins
    
    Returns:
        Instance du gestionnaire de plugins
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def load_plugin(plugin_path: str) -> bool:
    """
    Charge un plugin spécifique
    
    Args:
        plugin_path: Chemin vers le plugin
        
    Returns:
        True si le chargement a réussi
    """
    return get_plugin_manager().load_plugin(plugin_path)


def load_plugins_from_directory(directory: str) -> List[str]:
    """
    Charge tous les plugins d'un répertoire
    
    Args:
        directory: Répertoire contenant les plugins
        
    Returns:
        Liste des plugins chargés
    """
    return get_plugin_manager().load_plugins_from_directory(directory)


def unload_plugin(plugin_name: str) -> bool:
    """
    Décharge un plugin
    
    Args:
        plugin_name: Nom du plugin
        
    Returns:
        True si le déchargement a réussi
    """
    return get_plugin_manager().unload_plugin(plugin_name)


def get_plugin(plugin_name: str) -> Optional[Plugin]:
    """
    Récupère un plugin par son nom
    
    Args:
        plugin_name: Nom du plugin
        
    Returns:
        Instance du plugin ou None
    """
    return get_plugin_manager().get_plugin(plugin_name)


def list_plugins(status: Optional[PluginStatus] = None) -> List[PluginInfo]:
    """
    Liste tous les plugins
    
    Args:
        status: Filtrer par statut (optionnel)
        
    Returns:
        Liste des informations des plugins
    """
    return get_plugin_manager().list_plugins(status)


def execute_plugin(plugin_name: str, action: str, **kwargs) -> Dict[str, Any]:
    """
    Exécute une action sur un plugin
    
    Args:
        plugin_name: Nom du plugin
        action: Action à exécuter (scan, exploit, etc.)
        **kwargs: Arguments pour l'action
        
    Returns:
        Résultat de l'exécution
    """
    return get_plugin_manager().execute_plugin(plugin_name, action, **kwargs)


def get_plugins_by_type(plugin_type: PluginType) -> List[PluginInfo]:
    """
    Récupère les plugins par type
    
    Args:
        plugin_type: Type de plugin
        
    Returns:
        Liste des plugins du type spécifié
    """
    return get_plugin_manager().get_plugins_by_type(plugin_type)


def get_plugins_by_category(category: PluginCategory) -> List[PluginInfo]:
    """
    Récupère les plugins par catégorie
    
    Args:
        category: Catégorie de plugin
        
    Returns:
        Liste des plugins de la catégorie spécifiée
    """
    return get_plugin_manager().get_plugins_by_category(category)


def enable_stealth_mode(plugin_names: Optional[List[str]] = None) -> bool:
    """
    Active le mode furtif pour les plugins
    
    Args:
        plugin_names: Liste des plugins (None = tous)
        
    Returns:
        True si succès
    """
    return get_plugin_manager().enable_stealth_mode(plugin_names)


def enable_apt_mode(plugin_names: Optional[List[str]] = None) -> bool:
    """
    Active le mode APT pour les plugins
    
    Args:
        plugin_names: Liste des plugins (None = tous)
        
    Returns:
        True si succès
    """
    return get_plugin_manager().enable_apt_mode(plugin_names)


def get_plugin_statistics() -> Dict[str, Any]:
    """
    Retourne les statistiques des plugins
    
    Returns:
        Statistiques des plugins
    """
    return get_plugin_manager().get_statistics()


def reload_plugins() -> int:
    """
    Recharge tous les plugins
    
    Returns:
        Nombre de plugins rechargés
    """
    return get_plugin_manager().reload_all()


# Export des classes principales
__all__ = [
    # Gestionnaire
    'PluginManager',
    'get_plugin_manager',
    
    # Classes de base
    'Plugin',
    'PluginType',
    'PluginStatus',
    'PluginInfo',
    'PluginCategory',
    
    # Fonctions de gestion
    'load_plugin',
    'load_plugins_from_directory',
    'unload_plugin',
    'get_plugin',
    'list_plugins',
    'execute_plugin',
    'get_plugins_by_type',
    'get_plugins_by_category',
    'reload_plugins',
    
    # Modes furtif et APT
    'enable_stealth_mode',
    'enable_apt_mode',
    
    # Utilitaires
    'get_plugin_statistics',
    
    # Version
    '__version__'
]


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Système de plugins RedForge v{}".format(__version__))
    print("=" * 60)
    
    # Afficher les types de plugins disponibles
    print("\n📦 Types de plugins disponibles:")
    for plugin_type in PluginType:
        print(f"   - {plugin_type.value}")
    
    print("\n📂 Catégories de plugins disponibles:")
    for category in PluginCategory:
        print(f"   - {category.value}")
    
    # Créer une instance du gestionnaire
    manager = get_plugin_manager()
    
    print("\n✅ Système de plugins initialisé")
    print("\n💡 Exemples d'utilisation:")
    print("   load_plugin('/path/to/plugin.py')")
    print("   list_plugins()")
    print("   execute_plugin('MyPlugin', 'scan', target='example.com')")
    print("   enable_stealth_mode()")
    print("   get_plugin_statistics()")