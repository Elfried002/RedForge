#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour scripts personnalisés
Permet d'intégrer n'importe quel script externe dans RedForge
Version avec support furtif, APT et gestion avancée
"""

import subprocess
import json
import os
import tempfile
import hashlib
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime

from src.connectors.base_connector import BaseConnector


class CustomScriptConnector(BaseConnector):
    """Connecteur avancé pour scripts personnalisés avec support furtif"""
    
    def __init__(self, script_path: Optional[str] = None):
        """
        Initialise le connecteur de scripts personnalisés
        
        Args:
            script_path: Chemin du script personnalisé
        """
        self.script_path = script_path
        self.script_hash = None
        self.script_info = {}
        self.script_cache = {}
        super().__init__(script_path)
        
        # Charger les informations du script
        if self.available:
            self._load_script_info()
    
    def _find_tool(self) -> Optional[str]:
        """Retourne le chemin du script personnalisé"""
        if self.script_path and Path(self.script_path).exists():
            return self.script_path
        return None
    
    def _load_script_info(self):
        """Charge les informations du script (hash, permissions, etc.)"""
        if not self.available:
            return
        
        try:
            script_file = Path(self.tool_path)
            self.script_info = {
                "name": script_file.name,
                "path": str(script_file.absolute()),
                "size": script_file.stat().st_size,
                "modified": datetime.fromtimestamp(script_file.stat().st_mtime).isoformat(),
                "executable": os.access(self.tool_path, os.X_OK),
                "hash": hashlib.md5(open(self.tool_path, 'rb').read()).hexdigest()
            }
            self.script_hash = self.script_info["hash"]
        except Exception as e:
            self.script_info = {"error": str(e)}
    
    def set_script(self, script_path: str) -> bool:
        """
        Définit le script à utiliser
        
        Args:
            script_path: Chemin du script
            
        Returns:
            True si le script existe
        """
        if Path(script_path).exists():
            self.tool_path = script_path
            self.script_path = script_path
            self.available = True
            self._load_script_info()
            return True
        return False
    
    def get_script_info(self) -> Dict[str, Any]:
        """
        Retourne les informations du script
        
        Returns:
            Dictionnaire avec les informations du script
        """
        return self.script_info
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute un script personnalisé sur la cible
        
        Args:
            target: Cible à analyser
            **kwargs: Arguments supplémentaires pour le script
                - script_args: Liste d'arguments supplémentaires
                - timeout: Timeout personnalisé
                - input_data: Données à envoyer en stdin
                - env_vars: Variables d'environnement supplémentaires
                - capture_output: Capturer la sortie (défaut: True)
                - parse_json: Parser la sortie comme JSON
        """
        if not self.available:
            return {
                "success": False,
                "error": "Script personnalisé non configuré",
                "vulnerabilities": [],
                "script_info": self.script_info
            }
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        # Construction de la commande
        cmd = [self.tool_path]
        
        # Ajouter la cible selon le format attendu
        target_format = kwargs.get('target_format', 'argument')
        if target_format == 'argument':
            cmd.append(target)
        elif target_format == 'stdin':
            # La cible sera envoyée via stdin
            pass
        elif target_format == 'file':
            # Créer un fichier temporaire avec la cible
            temp_file = self.create_temp_output_file(".txt")
            with open(temp_file, 'w') as f:
                f.write(target)
            cmd.append(temp_file)
        
        # Ajout des arguments personnalisés
        script_args = kwargs.get('script_args', [])
        if script_args:
            cmd.extend(script_args)
        
        # Ajout des options de furtivité si demandé
        if self.apt_mode or kwargs.get('stealth', False):
            cmd = self._add_stealth_options(cmd)
        
        # Ajout des options spécifiques
        if kwargs.get('verbose'):
            cmd.append('--verbose')
        
        if kwargs.get('quiet'):
            cmd.append('--quiet')
        
        timeout = kwargs.get('timeout', 300)
        
        # Variables d'environnement
        env_vars = kwargs.get('env_vars', {})
        env = os.environ.copy()
        env.update(env_vars)
        
        # Ajouter User-Agent pour les scripts HTTP
        if any('curl' in str(c).lower() or 'wget' in str(c).lower() for c in cmd):
            env['HTTP_USER_AGENT'] = self._get_random_user_agent()
        
        # Données stdin
        input_data = kwargs.get('input_data', None)
        if target_format == 'stdin':
            input_data = target if input_data is None else input_data
        
        # Nettoyer le fichier temporaire si créé
        temp_file_created = target_format == 'file'
        
        try:
            start_time = datetime.now()
            
            # Exécution
            result = subprocess.run(
                cmd,
                input=input_data.encode() if input_data else None,
                capture_output=kwargs.get('capture_output', True),
                text=True,
                timeout=timeout,
                env=env
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Enregistrer l'exécution
            self.execution_history.append({
                'timestamp': datetime.now().isoformat(),
                'command': ' '.join(cmd),
                'target': target,
                'execution_time': execution_time,
                'returncode': result.returncode
            })
            
            self.scans_count += 1
            self.total_execution_time += execution_time
            
            # Parser la sortie
            output = result.stdout
            parsed_output = self.parse_output(output, **kwargs)
            
            # Vérifier si la sortie doit être parsée comme JSON
            if kwargs.get('parse_json', False):
                try:
                    parsed_output = json.loads(output)
                except:
                    pass
            
            # Mettre en cache le résultat
            cache_key = self._get_cache_key(target, kwargs)
            if kwargs.get('cache_result', False):
                self.script_cache[cache_key] = {
                    'timestamp': datetime.now().isoformat(),
                    'result': parsed_output
                }
            
            return {
                "success": result.returncode == 0,
                "target": target,
                "output": output,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "execution_time": execution_time,
                "parsed": parsed_output,
                "script_info": self.script_info,
                "command_used": ' '.join(cmd),
                "apt_mode": self.apt_mode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Script timeout après {timeout}s",
                "target": target,
                "script_info": self.script_info,
                "apt_mode": self.apt_mode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "target": target,
                "script_info": self.script_info,
                "apt_mode": self.apt_mode
            }
        finally:
            # Nettoyer le fichier temporaire
            if temp_file_created and 'temp_file' in dir():
                self.cleanup_temp_file(temp_file)
    
    def _add_stealth_options(self, cmd: List[str]) -> List[str]:
        """
        Ajoute des options furtives à la commande
        
        Args:
            cmd: Commande originale
            
        Returns:
            Commande avec options furtives
        """
        # Options furtives génériques pour scripts personnalisés
        stealth_options = [
            '--delay', str(random.uniform(0.5, 2.0)),
            '--random-agent',
            '--quiet'
        ]
        
        # Éviter les doublons
        for opt in stealth_options:
            if opt not in cmd:
                cmd.insert(1, opt)
        
        return cmd
    
    def _get_cache_key(self, target: str, kwargs: Dict) -> str:
        """
        Génère une clé de cache pour le résultat
        
        Args:
            target: Cible
            kwargs: Arguments
            
        Returns:
            Clé de cache
        """
        key_data = f"{target}_{json.dumps(kwargs, sort_keys=True)}_{self.script_hash}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def parse_output(self, output: str, **kwargs) -> Dict[str, Any]:
        """
        Parse la sortie du script avec différents formats supportés
        
        Args:
            output: Sortie brute du script
            **kwargs: Options de parsing
                - format: Format de sortie (auto, json, xml, csv, text)
                - delimiter: Délimiteur pour CSV
                
        Returns:
            Structure JSON des résultats
        """
        import re
        import csv
        import xml.etree.ElementTree as ET
        
        output = output.strip()
        if not output:
            return {"empty": True}
        
        format_type = kwargs.get('format', 'auto')
        
        # Auto-détection du format
        if format_type == 'auto':
            if output.startswith('{') and output.endswith('}'):
                format_type = 'json'
            elif output.startswith('[') and output.endswith(']'):
                format_type = 'json'
            elif output.startswith('<') and 'xml' in output.lower():
                format_type = 'xml'
            elif ',' in output and '\n' in output:
                format_type = 'csv'
            else:
                format_type = 'text'
        
        # Parser selon le format
        if format_type == 'json':
            try:
                return json.loads(output)
            except:
                return {"raw_output": output, "parse_error": "Invalid JSON"}
        
        elif format_type == 'xml':
            try:
                root = ET.fromstring(output)
                return self._xml_to_dict(root)
            except:
                return {"raw_output": output, "parse_error": "Invalid XML"}
        
        elif format_type == 'csv':
            try:
                reader = csv.DictReader(output.splitlines())
                return {"rows": list(reader), "count": sum(1 for _ in reader)}
            except:
                delimiter = kwargs.get('delimiter', ',')
                rows = []
                for line in output.splitlines():
                    rows.append(line.split(delimiter))
                return {"rows": rows, "count": len(rows)}
        
        else:  # text
            lines = output.split('\n')
            return {
                "raw_output": output,
                "lines": lines,
                "line_count": len(lines),
                "first_line": lines[0] if lines else "",
                "last_line": lines[-1] if lines else ""
            }
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """
        Convertit un élément XML en dictionnaire
        
        Args:
            element: Élément XML
            
        Returns:
            Dictionnaire représentant le XML
        """
        result = {element.tag: {} if element.attrib else None}
        
        # Ajouter les attributs
        if element.attrib:
            result[element.tag]['@attributes'] = element.attrib
        
        # Ajouter les enfants
        children = list(element)
        if children:
            child_dict = {}
            for child in children:
                child_data = self._xml_to_dict(child)
                child_tag = list(child_data.keys())[0]
                if child_tag in child_dict:
                    if not isinstance(child_dict[child_tag], list):
                        child_dict[child_tag] = [child_dict[child_tag]]
                    child_dict[child_tag].append(child_data[child_tag])
                else:
                    child_dict[child_tag] = child_data[child_tag]
            
            if element.attrib:
                result[element.tag].update(child_dict)
            else:
                result[element.tag] = child_dict
        
        # Ajouter le texte
        if element.text and element.text.strip():
            if children or element.attrib:
                if element.attrib:
                    result[element.tag]['#text'] = element.text.strip()
                else:
                    result[element.tag] = element.text.strip()
            else:
                result[element.tag] = element.text.strip()
        
        return result
    
    def execute_custom(self, command: str, args: List[str] = None, 
                       **kwargs) -> Dict[str, Any]:
        """
        Exécute une commande personnalisée
        
        Args:
            command: Commande à exécuter
            args: Liste des arguments
            **kwargs: Arguments supplémentaires pour execute_command
            
        Returns:
            Résultat de l'exécution
        """
        if args is None:
            args = []
        
        cmd = [command] + args
        return self.execute_command(cmd, **kwargs)
    
    def batch_scan(self, targets: List[str], **kwargs) -> Dict[str, Any]:
        """
        Exécute le script sur une liste de cibles
        
        Args:
            targets: Liste des cibles
            **kwargs: Arguments pour scan
            
        Returns:
            Résultats groupés
        """
        results = {}
        
        for idx, target in enumerate(targets):
            if self.apt_mode and idx > 0:
                self._apply_stealth_delay()
            
            result = self.scan(target, **kwargs)
            results[target] = result
        
        return {
            "total_targets": len(targets),
            "successful": sum(1 for r in results.values() if r.get('success')),
            "results": results,
            "apt_mode": self.apt_mode
        }
    
    def get_script_cache(self) -> Dict[str, Any]:
        """
        Retourne le cache des résultats
        
        Returns:
            Cache des résultats
        """
        return self.script_cache
    
    def clear_cache(self):
        """Vide le cache des résultats"""
        self.script_cache = {}
    
    def validate_script(self) -> Dict[str, Any]:
        """
        Valide le script (syntaxe, permissions, etc.)
        
        Returns:
            Résultat de la validation
        """
        if not self.available:
            return {"valid": False, "error": "Script non trouvé"}
        
        validation = {
            "valid": True,
            "path": self.tool_path,
            "executable": os.access(self.tool_path, os.X_OK),
            "readable": os.access(self.tool_path, os.R_OK),
            "size": self.script_info.get("size", 0),
            "hash": self.script_hash
        }
        
        # Tester l'exécution avec --help ou --version
        try:
            result = self.execute_command([self.tool_path, "--help"], timeout=5, stealth=False)
            validation["has_help"] = result["success"]
        except:
            validation["has_help"] = False
        
        return validation


# Fonction utilitaire pour créer un script wrapper
def create_wrapper_script(script_content: str, script_name: str = "custom_script") -> str:
    """
    Crée un script wrapper temporaire
    
    Args:
        script_content: Contenu du script
        script_name: Nom du script
        
    Returns:
        Chemin du script créé
    """
    import tempfile
    
    fd, path = tempfile.mkstemp(suffix=f"_{script_name}.py", prefix="redforge_")
    os.close(fd)
    
    with open(path, 'w') as f:
        f.write(script_content)
    
    # Rendre exécutable
    os.chmod(path, 0o755)
    
    return path