#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'internationalisation pour RedForge
Gère les traductions et les textes multilingues
Version avec support APT et gestion avancée
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class I18nManager:
    """Gestionnaire d'internationalisation avec support multi-langues"""
    
    _instance = None
    _translations: Dict[str, Any] = {}
    _current_lang: str = "fr_FR"
    _available_languages: List[str] = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._translations:
            self._detect_available_languages()
            self.load_language(self._current_lang)
    
    def _detect_available_languages(self):
        """Détecte les langues disponibles dans le dossier i18n"""
        i18n_dir = Path(__file__).parent
        self._available_languages = []
        
        for item in i18n_dir.iterdir():
            if item.is_dir() and item.name != "__pycache__":
                # Vérifier si le dossier contient des fichiers JSON
                if any(item.glob("*.json")):
                    self._available_languages.append(item.name)
        
        # Trier par ordre alphabétique
        self._available_languages.sort()
    
    def load_language(self, lang: str = "fr_FR") -> bool:
        """
        Charge une langue spécifique
        
        Args:
            lang: Code de la langue (ex: fr_FR, en_US)
            
        Returns:
            True si chargement réussi
        """
        lang_dir = Path(__file__).parent / lang
        
        if not lang_dir.exists():
            print(f"❌ Langue {lang} non trouvée")
            return False
        
        self._translations = {}
        self._current_lang = lang
        
        # Liste des fichiers de traduction à charger
        translation_files = [
            "cli_messages.json",
            "gui_strings.json",
            "error_messages.json",
            "success_messages.json",
            "help_texts.json",
            "attack_descriptions.json"
        ]
        
        # Charger tous les fichiers JSON du dossier
        for json_file in lang_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    key = json_file.stem
                    self._translations[key] = json.load(f)
                    # print(f"✅ Chargé: {key}")
            except json.JSONDecodeError as e:
                print(f"❌ Erreur JSON dans {json_file.name}: {e}")
            except Exception as e:
                print(f"❌ Erreur chargement {json_file.name}: {e}")
        
        return len(self._translations) > 0
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """
        Retourne la liste des langues disponibles
        
        Returns:
            Liste des langues avec leur code et nom
        """
        languages = []
        lang_names = {
            "fr_FR": "Français",
            "en_US": "English",
            "es_ES": "Español",
            "de_DE": "Deutsch",
            "it_IT": "Italiano",
            "pt_BR": "Português",
            "ru_RU": "Русский",
            "zh_CN": "中文",
            "ja_JP": "日本語"
        }
        
        for lang_code in self._available_languages:
            languages.append({
                "code": lang_code,
                "name": lang_names.get(lang_code, lang_code)
            })
        
        return languages
    
    def get_current_language(self) -> str:
        """Retourne le code de la langue actuelle"""
        return self._current_lang
    
    def set_language(self, lang: str) -> bool:
        """
        Change la langue actuelle
        
        Args:
            lang: Code de la langue
            
        Returns:
            True si changement réussi
        """
        if lang == self._current_lang:
            return True
        
        if lang not in self._available_languages:
            print(f"❌ Langue {lang} non disponible")
            return False
        
        return self.load_language(lang)
    
    def get(self, key: str, category: str = "cli_messages", default: str = None) -> str:
        """
        Récupère un texte traduit
        
        Args:
            key: Clé du texte (supporte la notation pointée ex: "errors.no_target")
            category: Catégorie (cli_messages, gui_strings, etc.)
            default: Valeur par défaut si non trouvé
            
        Returns:
            Texte traduit ou clé si non trouvé
        """
        try:
            # Obtenir la catégorie
            category_data = self._translations.get(category, {})
            if not category_data:
                return default or key
            
            # Parcourir les clés imbriquées
            parts = key.split('.')
            value = category_data
            
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                    if value is None:
                        return default or key
                else:
                    return default or key
            
            if isinstance(value, str):
                return value
            return default or key
            
        except Exception:
            return default or key
    
    def get_help(self, topic: str) -> Optional[str]:
        """
        Récupère un texte d'aide
        
        Args:
            topic: Sujet d'aide (footprint, analysis, scan, exploit, xss, sql, lfi, command, upload)
            
        Returns:
            Texte d'aide ou None
        """
        help_data = self._translations.get("help_texts", {})
        return help_data.get(topic)
    
    def get_error(self, error_key: str, **kwargs) -> str:
        """
        Récupère un message d'erreur formaté
        
        Args:
            error_key: Clé de l'erreur
            **kwargs: Variables à insérer
            
        Returns:
            Message d'erreur formaté
        """
        text = self.get(error_key, "error_messages", f"Erreur: {error_key}")
        for key, value in kwargs.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text
    
    def get_success(self, success_key: str, **kwargs) -> str:
        """
        Récupère un message de succès formaté
        
        Args:
            success_key: Clé du message de succès
            **kwargs: Variables à insérer
            
        Returns:
            Message de succès formaté
        """
        text = self.get(success_key, "success_messages", f"Succès: {success_key}")
        for key, value in kwargs.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text
    
    def get_attack_description(self, attack_type: str) -> Dict[str, Any]:
        """
        Récupère la description d'un type d'attaque
        
        Args:
            attack_type: Type d'attaque (sql_injection, xss, etc.)
            
        Returns:
            Dictionnaire contenant la description de l'attaque
        """
        attack_data = self._translations.get("attack_descriptions", {})
        return attack_data.get(attack_type, {
            "name": attack_type,
            "description": f"Description non disponible pour {attack_type}",
            "severity": "UNKNOWN",
            "examples": [],
            "remediation": "Non disponible"
        })
    
    def get_gui_string(self, key: str, **kwargs) -> str:
        """
        Récupère une chaîne pour l'interface graphique
        
        Args:
            key: Clé de la chaîne
            **kwargs: Variables à insérer
            
        Returns:
            Chaîne formatée
        """
        text = self.get(key, "gui_strings", key)
        for key, value in kwargs.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text
    
    def get_cli_message(self, key: str, **kwargs) -> str:
        """
        Récupère un message CLI formaté
        
        Args:
            key: Clé du message
            **kwargs: Variables à insérer
            
        Returns:
            Message formaté
        """
        text = self.get(key, "cli_messages", key)
        for key, value in kwargs.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text
    
    def format(self, key: str, category: str = "cli_messages", **kwargs) -> str:
        """
        Récupère et formate un texte avec des variables
        
        Args:
            key: Clé du texte
            category: Catégorie
            **kwargs: Variables à insérer
        """
        text = self.get(key, category, key)
        for k, v in kwargs.items():
            text = text.replace(f"{{{k}}}", str(v))
        return text
    
    def get_phase_name(self, phase: str) -> str:
        """
        Récupère le nom d'une phase
        
        Args:
            phase: Nom de la phase (footprint, analysis, scan, exploit)
            
        Returns:
            Nom localisé de la phase
        """
        phases = self._translations.get("cli_messages", {}).get("phases", {})
        return phases.get(phase, phase.capitalize())
    
    def get_phase_description(self, phase: str) -> str:
        """
        Récupère la description d'une phase
        
        Args:
            phase: Nom de la phase
            
        Returns:
            Description localisée
        """
        descriptions = self._translations.get("cli_messages", {}).get("phase_descriptions", {})
        return descriptions.get(phase, f"Phase {phase}")
    
    def get_attack_option(self, option: str) -> str:
        """
        Récupère la description d'une option d'attaque
        
        Args:
            option: Nom de l'option (xss, sqlmap, etc.)
            
        Returns:
            Description localisée
        """
        options = self._translations.get("cli_messages", {}).get("attack_options", {})
        return options.get(option, f"Option {option}")
    
    def get_status_message(self, status_key: str, **kwargs) -> str:
        """
        Récupère un message de statut formaté
        
        Args:
            status_key: Clé du statut
            **kwargs: Variables à insérer
            
        Returns:
            Message de statut formaté
        """
        text = self.get(status_key, "cli_messages", status_key)
        for key, value in kwargs.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text
    
    def get_all_categories(self) -> List[str]:
        """
        Retourne la liste des catégories disponibles
        
        Returns:
            Liste des catégories
        """
        return list(self._translations.keys())
    
    def reload(self) -> bool:
        """Recharge la langue courante"""
        return self.load_language(self._current_lang)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du gestionnaire i18n
        
        Returns:
            Statistiques
        """
        stats = {
            "current_language": self._current_lang,
            "available_languages": self._available_languages,
            "categories_loaded": list(self._translations.keys()),
            "total_keys": sum(len(cat) for cat in self._translations.values())
        }
        
        # Compter les clés par catégorie
        for category, data in self._translations.items():
            stats[f"keys_{category}"] = len(data) if isinstance(data, dict) else 1
        
        return stats


# Instance globale
i18n = I18nManager()


# Fonctions de commodité
def t(key: str, category: str = "cli_messages", **kwargs) -> str:
    """
    Raccourci pour get text (translate)
    
    Args:
        key: Clé du texte
        category: Catégorie
        **kwargs: Variables à insérer
        
    Returns:
        Texte traduit
    """
    return i18n.format(key, category, **kwargs)


def error(key: str, **kwargs) -> str:
    """Raccourci pour les messages d'erreur"""
    return i18n.get_error(key, **kwargs)


def success(key: str, **kwargs) -> str:
    """Raccourci pour les messages de succès"""
    return i18n.get_success(key, **kwargs)


def help_text(topic: str) -> Optional[Dict]:
    """Raccourci pour les textes d'aide"""
    return i18n.get_help(topic)


def attack_desc(attack_type: str) -> Dict:
    """Raccourci pour les descriptions d'attaques"""
    return i18n.get_attack_description(attack_type)


def gui(key: str, **kwargs) -> str:
    """Raccourci pour les chaînes GUI"""
    return i18n.get_gui_string(key, **kwargs)


def cli(key: str, **kwargs) -> str:
    """Raccourci pour les messages CLI"""
    return i18n.get_cli_message(key, **kwargs)


def phase_name(phase: str) -> str:
    """Raccourci pour le nom des phases"""
    return i18n.get_phase_name(phase)


def phase_desc(phase: str) -> str:
    """Raccourci pour la description des phases"""
    return i18n.get_phase_description(phase)


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test du module d'internationalisation")
    print("=" * 60)
    
    # Afficher les langues disponibles
    print(f"\n🌐 Langues disponibles:")
    for lang in i18n.get_available_languages():
        print(f"   - {lang['name']} ({lang['code']})")
    
    print(f"\n📊 Statistiques:")
    stats = i18n.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Tester les traductions
    print(f"\n🔤 Tests de traduction:")
    print(f"   Bienvenue: {t('welcome', version='2.0.0')}")
    print(f"   Erreur: {error('cli.no_target')}")
    print(f"   Succès: {success('cli.phase_complete', phase='footprint')}")
    print(f"   Phase: {phase_name('scan')}")
    
    # Tester une description d'attaque
    print(f"\n🎯 Description d'attaque (SQL Injection):")
    sql_desc = attack_desc('sql_injection')
    print(f"   Nom: {sql_desc.get('name')}")
    print(f"   Sévérité: {sql_desc.get('severity')}")
    print(f"   Exemple: {sql_desc.get('examples', [''])[0]}")
    
    print("\n✅ Tests terminés")