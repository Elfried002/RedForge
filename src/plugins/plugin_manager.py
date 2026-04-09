#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de plugins pour RedForge
Charge, gère et exécute les plugins
Version avec support furtif, APT et gestion avancée
"""

import os
import sys
import json
import importlib
import inspect
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

# Imports internes (avec fallback pour tests)
try:
    from src.utils.logger import logger
    from src.utils.color_output import console
except ImportError:
    # Fallback pour tests
    import logging
    logger = logging.getLogger(__name__)
    
    class ConsoleMock:
        def print_success(self, msg): print(f"✅ {msg}")
        def print_error(self, msg): print(f"❌ {msg}")
        def print_warning(self, msg): print(f"⚠️ {msg}")
        def print_info(self, msg): print(f"ℹ️ {msg}")
        def print_header(self, msg): print(f"\n{'='*60}\n{msg}\n{'='*60}")
    console = ConsoleMock()


class PluginType(Enum):
    """Types de plugins supportés"""
    ATTACK = "attack"           # Nouveau type d'attaque
    SCANNER = "scanner"         # Nouveau scanner
    CONNECTOR = "connector"     # Nouveau connecteur d'outil
    REPORT = "report"           # Générateur de rapport
    UTILITY = "utility"         # Utilitaire
    HOOK = "hook"               # Hook d'événement
    STEALTH = "stealth"         # Plugin de furtivité
    APT = "apt"                 # Plugin APT


class PluginStatus(Enum):
    """Statuts possibles d'un plugin"""
    LOADED = "loaded"
    UNLOADED = "unloaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class PluginInfo:
    """Informations sur un plugin"""
    name: str
    version: str
    author: str
    description: str
    type: PluginType
    path: Path
    status: PluginStatus = PluginStatus.UNLOADED
    enabled: bool = True
    module: Any = None
    instance: Any = None
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    config: Dict[str, Any] = field(default_factory=dict)
    stealth_mode: bool = False
    apt_mode: bool = False
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    error_count: int = 0


class Plugin:
    """
    Classe de base pour tous les plugins RedForge
    Les plugins doivent hériter de cette classe
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise le plugin
        
        Args:
            config: Configuration du plugin
        """
        self.config = config or {}
        self.logger = logger
        self.name = self.get_name()
        self.version = self.get_version()
        self.author = self.get_author()
        self.description = self.get_description()
        self.type = self.get_type()
        self.stealth_mode = False
        self.apt_mode = False
        self._lock = threading.Lock()
    
    def get_name(self) -> str:
        """Retourne le nom du plugin"""
        return self.__class__.__name__
    
    def get_version(self) -> str:
        """Retourne la version du plugin"""
        return "1.0.0"
    
    def get_author(self) -> str:
        """Retourne l'auteur du plugin"""
        return "RedForge Community"
    
    def get_description(self) -> str:
        """Retourne la description du plugin"""
        return "Plugin RedForge"
    
    def get_type(self) -> PluginType:
        """Retourne le type du plugin"""
        return PluginType.UTILITY
    
    def get_dependencies(self) -> List[str]:
        """Retourne la liste des dépendances"""
        return []
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Retourne le schéma de configuration"""
        return {}
    
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif pour le plugin"""
        self.stealth_mode = enabled
    
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT pour le plugin"""
        self.apt_mode = enabled
    
    def on_load(self) -> bool:
        """
        Appelé lors du chargement du plugin
        Retourne True si le chargement est réussi
        """
        return True
    
    def on_unload(self) -> bool:
        """
        Appelé lors du déchargement du plugin
        Retourne True si le déchargement est réussi
        """
        return True
    
    def on_enable(self) -> bool:
        """
        Appelé lors de l'activation du plugin
        Retourne True si l'activation est réussie
        """
        return True
    
    def on_disable(self) -> bool:
        """
        Appelé lors de la désactivation du plugin
        Retourne True si la désactivation est réussie
        """
        return True
    
    def execute(self, **kwargs) -> Any:
        """
        Méthode principale d'exécution du plugin
        À surcharger dans les plugins
        """
        with self._lock:
            self.execution_count += 1
            self.last_execution = datetime.now()
            try:
                result = self._execute(**kwargs)
                return result
            except Exception as e:
                self.error_count += 1
                raise
    
    def _execute(self, **kwargs) -> Any:
        """Méthode interne d'exécution (à surcharger)"""
        raise NotImplementedError("La méthode execute doit être implémentée")
    
    def get_help(self) -> str:
        """Retourne l'aide du plugin"""
        mode_info = "APT" if self.apt_mode else ("Stealth" if self.stealth_mode else "Normal")
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║  {self.name} v{self.version} - Mode: {mode_info}                    ║
╚══════════════════════════════════════════════════════════════════╝

📝 DESCRIPTION:
  {self.description}

👤 AUTEUR:
  {self.author}

📦 TYPE:
  {self.type.value}

📊 STATISTIQUES:
  Exécutions: {getattr(self, 'execution_count', 0)}
  Erreurs: {getattr(self, 'error_count', 0)}
  Dernière exécution: {getattr(self, 'last_execution', 'Jamais')}

⚙️ CONFIGURATION:
  Mode furtif: {self.stealth_mode}
  Mode APT: {self.apt_mode}
"""
    
    def update_config(self, config: Dict[str, Any]):
        """Met à jour la configuration du plugin"""
        self.config.update(config)
        self.save_config()
    
    def save_config(self) -> bool:
        """Sauvegarde la configuration du plugin"""
        plugin_dir = Path(__file__).parent / "config"
        plugin_dir.mkdir(exist_ok=True)
        config_file = plugin_dir / f"{self.name}.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde config {self.name}: {e}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """Charge la configuration du plugin"""
        plugin_dir = Path(__file__).parent / "config"
        config_file = plugin_dir / f"{self.name}.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.error(f"Erreur chargement config {self.name}: {e}")
        
        return self.config


class AttackPlugin(Plugin):
    """Plugin d'attaque"""
    
    def get_type(self) -> PluginType:
        return PluginType.ATTACK
    
    def get_attack_name(self) -> str:
        """Nom de l'attaque"""
        raise NotImplementedError
    
    def get_attack_description(self) -> str:
        """Description de l'attaque"""
        raise NotImplementedError
    
    def get_attack_severity(self) -> str:
        """Sévérité de l'attaque (CRITICAL, HIGH, MEDIUM, LOW)"""
        return "MEDIUM"
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """Scanne la cible pour détecter la vulnérabilité"""
        raise NotImplementedError
    
    def exploit(self, target: str, **kwargs) -> Dict[str, Any]:
        """Exploite la vulnérabilité"""
        raise NotImplementedError
    
    def _execute(self, **kwargs) -> Any:
        """Exécute l'attaque"""
        action = kwargs.get('action', 'scan')
        target = kwargs.get('target')
        
        if not target:
            return {"error": "Aucune cible spécifiée"}
        
        if action == 'scan':
            return self.scan(target, **kwargs)
        elif action == 'exploit':
            return self.exploit(target, **kwargs)
        else:
            return {"error": f"Action inconnue: {action}"}


class ScannerPlugin(Plugin):
    """Plugin de scanner"""
    
    def get_type(self) -> PluginType:
        return PluginType.SCANNER
    
    def get_scanner_name(self) -> str:
        """Nom du scanner"""
        raise NotImplementedError
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """Exécute le scan"""
        raise NotImplementedError
    
    def _execute(self, **kwargs) -> Any:
        """Exécute le scanner"""
        target = kwargs.get('target')
        
        if not target:
            return {"error": "Aucune cible spécifiée"}
        
        return self.scan(target, **kwargs)


class ConnectorPlugin(Plugin):
    """Plugin de connecteur d'outil"""
    
    def get_type(self) -> PluginType:
        return PluginType.CONNECTOR
    
    def get_tool_name(self) -> str:
        """Nom de l'outil connecté"""
        raise NotImplementedError
    
    def get_tool_path(self) -> Optional[str]:
        """Chemin de l'outil"""
        return None
    
    def execute_tool(self, command: str, **kwargs) -> Dict[str, Any]:
        """Exécute l'outil"""
        raise NotImplementedError
    
    def _execute(self, **kwargs) -> Any:
        """Exécute le connecteur"""
        command = kwargs.get('command')
        
        if not command:
            return {"error": "Aucune commande spécifiée"}
        
        return self.execute_tool(command, **kwargs)


class ReportPlugin(Plugin):
    """Plugin de générateur de rapport"""
    
    def get_type(self) -> PluginType:
        return PluginType.REPORT
    
    def get_format_name(self) -> str:
        """Nom du format de rapport"""
        raise NotImplementedError
    
    def generate(self, data: Dict[str, Any], output_file: str) -> bool:
        """Génère le rapport"""
        raise NotImplementedError
    
    def _execute(self, **kwargs) -> Any:
        """Génère le rapport"""
        data = kwargs.get('data', {})
        output_file = kwargs.get('output_file')
        
        if not output_file:
            return {"error": "Aucun fichier de sortie spécifié"}
        
        success = self.generate(data, output_file)
        return {"success": success, "output_file": output_file}


class HookPlugin(Plugin):
    """Plugin de hook d'événement"""
    
    def get_type(self) -> PluginType:
        return PluginType.HOOK
    
    def get_hook_name(self) -> str:
        """Nom du hook"""
        raise NotImplementedError
    
    def on_event(self, event: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Traite un événement"""
        raise NotImplementedError
    
    def _execute(self, **kwargs) -> Any:
        """Traite l'événement"""
        event = kwargs.get('event')
        data = kwargs.get('data', {})
        
        if not event:
            return {"error": "Aucun événement spécifié"}
        
        return self.on_event(event, data)


class PluginManager:
    """Gestionnaire de plugins avec support furtif et APT"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        self.plugins: Dict[str, PluginInfo] = {}
        self.plugins_dir = Path(__file__).parent / "plugins"
        self.plugins_dir.mkdir(exist_ok=True)
        
        self.hooks: Dict[str, List[Callable]] = defaultdict(list)
        self.stealth_mode = False
        self.apt_mode = False
        
        # Charger la configuration
        self.load_config()
    
    def load_config(self):
        """Charge la configuration des plugins"""
        config_file = self.plugins_dir / "config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.stealth_mode = config.get('stealth_mode', False)
                self.apt_mode = config.get('apt_mode', False)
                
                for name, plugin_config in config.get('plugins', {}).items():
                    if name in self.plugins:
                        self.plugins[name].enabled = plugin_config.get('enabled', True)
                        self.plugins[name].config = plugin_config.get('config', {})
                        self.plugins[name].stealth_mode = plugin_config.get('stealth_mode', False)
                        self.plugins[name].apt_mode = plugin_config.get('apt_mode', False)
                        
            except Exception as e:
                console.print_error(f"Erreur chargement config plugins: {e}")
    
    def save_config(self) -> bool:
        """Sauvegarde la configuration des plugins"""
        config = {
            'stealth_mode': self.stealth_mode,
            'apt_mode': self.apt_mode,
            'plugins': {}
        }
        
        for name, plugin_info in self.plugins.items():
            config['plugins'][name] = {
                'enabled': plugin_info.enabled,
                'config': plugin_info.config,
                'stealth_mode': plugin_info.stealth_mode,
                'apt_mode': plugin_info.apt_mode
            }
        
        try:
            with open(self.plugins_dir / "config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            console.print_error(f"Erreur sauvegarde config plugins: {e}")
            return False
    
    def enable_stealth_mode(self, plugin_names: Optional[List[str]] = None) -> bool:
        """
        Active le mode furtif pour les plugins
        
        Args:
            plugin_names: Liste des plugins (None = tous)
        """
        if plugin_names is None:
            self.stealth_mode = True
            for plugin_info in self.plugins.values():
                plugin_info.stealth_mode = True
                if plugin_info.instance:
                    plugin_info.instance.set_stealth_mode(True)
        else:
            for name in plugin_names:
                if name in self.plugins:
                    self.plugins[name].stealth_mode = True
                    if self.plugins[name].instance:
                        self.plugins[name].instance.set_stealth_mode(True)
        
        self.save_config()
        console.print_success("Mode furtif activé")
        return True
    
    def enable_apt_mode(self, plugin_names: Optional[List[str]] = None) -> bool:
        """
        Active le mode APT pour les plugins
        
        Args:
            plugin_names: Liste des plugins (None = tous)
        """
        if plugin_names is None:
            self.apt_mode = True
            for plugin_info in self.plugins.values():
                plugin_info.apt_mode = True
                if plugin_info.instance:
                    plugin_info.instance.set_apt_mode(True)
        else:
            for name in plugin_names:
                if name in self.plugins:
                    self.plugins[name].apt_mode = True
                    if self.plugins[name].instance:
                        self.plugins[name].instance.set_apt_mode(True)
        
        self.save_config()
        console.print_success("Mode APT activé")
        return True
    
    def disable_stealth_mode(self, plugin_names: Optional[List[str]] = None) -> bool:
        """Désactive le mode furtif"""
        if plugin_names is None:
            self.stealth_mode = False
            for plugin_info in self.plugins.values():
                plugin_info.stealth_mode = False
                if plugin_info.instance:
                    plugin_info.instance.set_stealth_mode(False)
        else:
            for name in plugin_names:
                if name in self.plugins:
                    self.plugins[name].stealth_mode = False
                    if self.plugins[name].instance:
                        self.plugins[name].instance.set_stealth_mode(False)
        
        self.save_config()
        console.print_info("Mode furtif désactivé")
        return True
    
    def disable_apt_mode(self, plugin_names: Optional[List[str]] = None) -> bool:
        """Désactive le mode APT"""
        if plugin_names is None:
            self.apt_mode = False
            for plugin_info in self.plugins.values():
                plugin_info.apt_mode = False
                if self.plugins[name].instance:
                    self.plugins[name].instance.set_apt_mode(False)
        else:
            for name in plugin_names:
                if name in self.plugins:
                    self.plugins[name].apt_mode = False
                    if self.plugins[name].instance:
                        self.plugins[name].instance.set_apt_mode(False)
        
        self.save_config()
        console.print_info("Mode APT désactivé")
        return True
    
    def discover_plugins(self) -> List[str]:
        """Découvre les plugins dans le dossier plugins"""
        discovered = []
        
        for item in self.plugins_dir.iterdir():
            if item.is_dir():
                init_file = item / "__init__.py"
                if init_file.exists():
                    discovered.append(item.name)
            
            elif item.is_file() and item.suffix == '.py' and item.name != '__init__.py':
                discovered.append(item.stem)
        
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Charge un plugin spécifique"""
        if plugin_name in self.plugins and self.plugins[plugin_name].status == PluginStatus.LOADED:
            console.print_warning(f"Plugin {plugin_name} déjà chargé")
            return True
        
        try:
            if str(self.plugins_dir) not in sys.path:
                sys.path.insert(0, str(self.plugins_dir))
            
            module = importlib.import_module(plugin_name)
            
            # Trouver la classe Plugin
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Plugin) and 
                    obj != Plugin and
                    obj != AttackPlugin and
                    obj != ScannerPlugin and
                    obj != ConnectorPlugin and
                    obj != ReportPlugin and
                    obj != HookPlugin):
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                console.print_error(f"Aucune classe Plugin trouvée dans {plugin_name}")
                return False
            
            # Créer une instance
            config = {}
            stealth_mode = self.stealth_mode
            apt_mode = self.apt_mode
            
            if plugin_name in self.plugins:
                config = self.plugins[plugin_name].config
                stealth_mode = self.plugins[plugin_name].stealth_mode
                apt_mode = self.plugins[plugin_name].apt_mode
            
            instance = plugin_class(config)
            instance.set_stealth_mode(stealth_mode)
            instance.set_apt_mode(apt_mode)
            
            # Vérifier les dépendances
            dependencies = instance.get_dependencies()
            for dep in dependencies:
                if dep not in self.plugins or self.plugins[dep].status != PluginStatus.LOADED:
                    console.print_error(f"Dépendance manquante: {dep} pour {plugin_name}")
                    return False
            
            # Appeler on_load
            if not instance.on_load():
                console.print_error(f"Échec du chargement du plugin {plugin_name}")
                return False
            
            # Enregistrer le plugin
            plugin_info = PluginInfo(
                name=instance.get_name(),
                version=instance.get_version(),
                author=instance.get_author(),
                description=instance.get_description(),
                type=instance.get_type(),
                path=self.plugins_dir / plugin_name,
                status=PluginStatus.LOADED,
                enabled=self.plugins.get(plugin_name, PluginInfo(
                    name=plugin_name, version="", author="", description="",
                    type=PluginType.UTILITY, path=self.plugins_dir / plugin_name
                )).enabled if plugin_name in self.plugins else True,
                module=module,
                instance=instance,
                dependencies=dependencies,
                config=config,
                stealth_mode=stealth_mode,
                apt_mode=apt_mode
            )
            
            self.plugins[plugin_name] = plugin_info
            
            console.print_success(f"Plugin chargé: {plugin_name} v{instance.get_version()}")
            return True
            
        except ImportError as e:
            console.print_error(f"Erreur import plugin {plugin_name}: {e}")
            return False
        except Exception as e:
            console.print_error(f"Erreur chargement plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Décharge un plugin"""
        if plugin_name not in self.plugins:
            console.print_warning(f"Plugin {plugin_name} non trouvé")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.status != PluginStatus.LOADED:
            console.print_warning(f"Plugin {plugin_name} déjà déchargé")
            return True
        
        try:
            if not plugin_info.instance.on_unload():
                console.print_warning(f"Échec du déchargement du plugin {plugin_name}")
                return False
            
            # Supprimer les hooks
            for hook_name in list(self.hooks.keys()):
                self.hooks[hook_name] = [cb for cb in self.hooks[hook_name] 
                                        if getattr(cb, '__self__', None) != plugin_info.instance]
            
            plugin_info.status = PluginStatus.UNLOADED
            plugin_info.instance = None
            plugin_info.module = None
            
            console.print_success(f"Plugin déchargé: {plugin_name}")
            return True
            
        except Exception as e:
            console.print_error(f"Erreur déchargement plugin {plugin_name}: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Active un plugin"""
        if plugin_name not in self.plugins:
            console.print_warning(f"Plugin {plugin_name} non trouvé")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.enabled:
            console.print_warning(f"Plugin {plugin_name} déjà activé")
            return True
        
        if plugin_info.status != PluginStatus.LOADED:
            if not self.load_plugin(plugin_name):
                return False
            plugin_info = self.plugins[plugin_name]
        
        try:
            if not plugin_info.instance.on_enable():
                console.print_error(f"Échec activation plugin {plugin_name}")
                return False
            
            plugin_info.enabled = True
            self.save_config()
            
            console.print_success(f"Plugin activé: {plugin_name}")
            return True
            
        except Exception as e:
            console.print_error(f"Erreur activation plugin {plugin_name}: {e}")
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Désactive un plugin"""
        if plugin_name not in self.plugins:
            console.print_warning(f"Plugin {plugin_name} non trouvé")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        if not plugin_info.enabled:
            console.print_warning(f"Plugin {plugin_name} déjà désactivé")
            return True
        
        try:
            if plugin_info.status == PluginStatus.LOADED:
                if not plugin_info.instance.on_disable():
                    console.print_warning(f"Échec désactivation plugin {plugin_name}")
                    return False
            
            plugin_info.enabled = False
            self.save_config()
            
            console.print_success(f"Plugin désactivé: {plugin_name}")
            return True
            
        except Exception as e:
            console.print_error(f"Erreur désactivation plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """Charge tous les plugins découverts"""
        results = {}
        discovered = self.discover_plugins()
        
        console.print_info(f"Découverte de {len(discovered)} plugin(s)")
        
        for plugin_name in discovered:
            results[plugin_name] = self.load_plugin(plugin_name)
        
        return results
    
    def unload_all_plugins(self) -> Dict[str, bool]:
        """Décharge tous les plugins chargés"""
        results = {}
        
        for plugin_name in list(self.plugins.keys()):
            if self.plugins[plugin_name].status == PluginStatus.LOADED:
                results[plugin_name] = self.unload_plugin(plugin_name)
        
        return results
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        """Récupère les informations d'un plugin"""
        return self.plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInfo]:
        """Récupère les plugins d'un type spécifique"""
        return [p for p in self.plugins.values() if p.type == plugin_type and p.enabled]
    
    def get_enabled_plugins(self) -> List[PluginInfo]:
        """Récupère les plugins activés"""
        return [p for p in self.plugins.values() if p.enabled]
    
    def get_loaded_plugins(self) -> List[PluginInfo]:
        """Récupère les plugins chargés"""
        return [p for p in self.plugins.values() if p.status == PluginStatus.LOADED]
    
    def execute_plugin(self, plugin_name: str, **kwargs) -> Any:
        """Exécute un plugin"""
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin {plugin_name} non trouvé")
        
        plugin_info = self.plugins[plugin_name]
        
        if not plugin_info.enabled:
            raise ValueError(f"Plugin {plugin_name} désactivé")
        
        if plugin_info.status != PluginStatus.LOADED:
            if not self.load_plugin(plugin_name):
                raise RuntimeError(f"Impossible de charger le plugin {plugin_name}")
        
        try:
            return plugin_info.instance.execute(**kwargs)
        except Exception as e:
            console.print_error(f"Erreur exécution plugin {plugin_name}: {e}")
            raise
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Enregistre un hook"""
        self.hooks[hook_name].append(callback)
    
    def unregister_hook(self, hook_name: str, callback: Callable):
        """Désenregistre un hook"""
        if hook_name in self.hooks:
            self.hooks[hook_name] = [cb for cb in self.hooks[hook_name] if cb != callback]
    
    def trigger_hook(self, hook_name: str, data: Dict[str, Any] = None) -> List[Any]:
        """Déclenche un hook"""
        results = []
        
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    result = callback(data or {})
                    results.append(result)
                except Exception as e:
                    console.print_error(f"Erreur hook {hook_name}: {e}")
        
        return results
    
    def get_plugins_info(self) -> List[Dict[str, Any]]:
        """Retourne les informations de tous les plugins"""
        return [{
            'name': info.name,
            'version': info.version,
            'author': info.author,
            'description': info.description,
            'type': info.type.value,
            'status': info.status.value,
            'enabled': info.enabled,
            'stealth_mode': info.stealth_mode,
            'apt_mode': info.apt_mode,
            'dependencies': info.dependencies,
            'created_at': info.created_at.isoformat()
        } for info in self.plugins.values()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques des plugins"""
        total = len(self.plugins)
        loaded = len([p for p in self.plugins.values() if p.status == PluginStatus.LOADED])
        enabled = len([p for p in self.plugins.values() if p.enabled])
        by_type = defaultdict(int)
        
        for p in self.plugins.values():
            by_type[p.type.value] += 1
        
        return {
            "total_plugins": total,
            "loaded_plugins": loaded,
            "enabled_plugins": enabled,
            "by_type": dict(by_type),
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode
        }
    
    def reload_all(self) -> int:
        """Recharge tous les plugins"""
        self.unload_all_plugins()
        results = self.load_all_plugins()
        return sum(1 for success in results.values() if success)
    
    def get_plugin_help(self, plugin_name: str) -> str:
        """Récupère l'aide d'un plugin"""
        if plugin_name not in self.plugins:
            return f"Plugin {plugin_name} non trouvé"
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.status != PluginStatus.LOADED:
            if not self.load_plugin(plugin_name):
                return f"Impossible de charger le plugin {plugin_name}"
        
        return plugin_info.instance.get_help()


# Instance globale
plugin_manager = PluginManager()


# Point d'entrée pour tests
if __name__ == "__main__":
    console.print_header("Test du gestionnaire de plugins")
    
    # Créer un plugin d'exemple
    example_plugin_dir = plugin_manager.plugins_dir / "example_plugin"
    example_plugin_dir.mkdir(exist_ok=True)
    
    # Créer le fichier __init__.py
    init_content = '''
from src.plugins.plugin_manager import Plugin, PluginType

class ExamplePlugin(Plugin):
    def get_name(self):
        return "ExamplePlugin"
    
    def get_version(self):
        return "1.0.0"
    
    def get_author(self):
        return "RedForge Team"
    
    def get_description(self):
        return "Plugin d'exemple"
    
    def get_type(self):
        return PluginType.UTILITY
    
    def _execute(self, **kwargs):
        return {"success": True, "message": "Plugin exécuté", "data": kwargs}
'''
    
    with open(example_plugin_dir / "__init__.py", 'w', encoding='utf-8') as f:
        f.write(init_content)
    
    # Découvrir et charger les plugins
    discovered = plugin_manager.discover_plugins()
    console.print_info(f"Plugins découverts: {discovered}")
    
    for plugin_name in discovered:
        plugin_manager.load_plugin(plugin_name)
    
    # Lister les plugins
    plugins = plugin_manager.get_plugins_info()
    for info in plugins:
        console.print_info(f"  {info['name']} v{info['version']} - {info['description']}")
    
    # Exécuter un plugin
    if 'example_plugin' in plugin_manager.plugins:
        result = plugin_manager.execute_plugin('example_plugin', test="value")
        console.print_success(f"Résultat: {result}")
    
    # Activer le mode APT
    plugin_manager.enable_apt_mode()
    
    # Afficher les statistiques
    stats = plugin_manager.get_statistics()
    console.print_info(f"Statistiques: {stats}")
    
    console.print_success("Test terminé")