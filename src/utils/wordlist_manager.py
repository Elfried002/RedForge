#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de wordlists pour RedForge
Gère les wordlists pour la force brute, le fuzzing et l'énumération
Version avec support furtif, APT et gestion avancée
"""

import os
import gzip
import json
import hashlib
import random
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set, Iterator
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter
import requests


@dataclass
class WordlistInfo:
    """Informations sur une wordlist"""
    name: str
    path: Path
    size: int
    lines: int
    hash: str
    created_at: datetime
    last_used: Optional[datetime] = None
    times_used: int = 0
    compressed: bool = False
    source: str = "local"


class WordlistManager:
    """
    Gestionnaire avancé de wordlists
    Supporte le téléchargement, la génération, la fusion et l'optimisation
    """
    
    # URLs des wordlists par défaut
    DEFAULT_WORDLISTS = {
        "rockyou.txt": {
            "url": "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt",
            "compressed": True,
            "size_mb": 139,
            "lines": 14344391
        },
        "common_passwords.txt": {
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt",
            "compressed": False,
            "size_mb": 0.5,
            "lines": 10000
        },
        "common_users.txt": {
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/top-usernames-shortlist.txt",
            "compressed": False,
            "size_mb": 0.1,
            "lines": 100
        },
        "directories.txt": {
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt",
            "compressed": False,
            "size_mb": 2,
            "lines": 9594
        },
        "subdomains.txt": {
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt",
            "compressed": False,
            "size_mb": 0.5,
            "lines": 5000
        },
        "parameters.txt": {
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt",
            "compressed": False,
            "size_mb": 0.3,
            "lines": 6450
        },
        "extensions.txt": {
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/web-extensions.txt",
            "compressed": False,
            "size_mb": 0.1,
            "lines": 50
        }
    }
    
    def __init__(self, wordlist_dir: Optional[Path] = None):
        """
        Initialise le gestionnaire de wordlists
        
        Args:
            wordlist_dir: Répertoire personnalisé pour les wordlists
        """
        if wordlist_dir is None:
            wordlist_dir = Path.home() / ".RedForge" / "wordlists"
        
        self.wordlist_dir = wordlist_dir
        self.wordlist_dir.mkdir(parents=True, exist_ok=True)
        
        self.wordlists: Dict[str, WordlistInfo] = {}
        self.stealth_mode = False
        self.apt_mode = False
        
        # Charger les wordlists existantes
        self._scan_wordlists()
    
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif"""
        self.stealth_mode = enabled
    
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT"""
        self.apt_mode = enabled
    
    def _scan_wordlists(self):
        """Scanne le répertoire des wordlists"""
        for file_path in self.wordlist_dir.iterdir():
            if file_path.is_file():
                name = file_path.name
                if name.endswith('.gz'):
                    name = name[:-3]
                    compressed = True
                else:
                    compressed = False
                
                # Compter les lignes
                lines = self._count_lines(file_path)
                
                # Calculer le hash
                file_hash = self._compute_hash(file_path)
                
                self.wordlists[name] = WordlistInfo(
                    name=name,
                    path=file_path,
                    size=file_path.stat().st_size,
                    lines=lines,
                    hash=file_hash,
                    created_at=datetime.fromtimestamp(file_path.stat().st_ctime),
                    compressed=compressed
                )
    
    def _count_lines(self, file_path: Path) -> int:
        """Compte le nombre de lignes dans un fichier"""
        try:
            if str(file_path).endswith('.gz'):
                import gzip
                with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                    return sum(1 for _ in f)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return sum(1 for _ in f)
        except:
            return 0
    
    def _compute_hash(self, file_path: Path) -> str:
        """Calcule le hash MD5 d'un fichier"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return ""
    
    def list_wordlists(self) -> List[Dict[str, Any]]:
        """
        Liste toutes les wordlists disponibles
        
        Returns:
            Liste des informations des wordlists
        """
        return [
            {
                'name': info.name,
                'size_mb': round(info.size / (1024 * 1024), 2),
                'lines': info.lines,
                'compressed': info.compressed,
                'created_at': info.created_at.isoformat(),
                'times_used': info.times_used
            }
            for info in self.wordlists.values()
        ]
    
    def download_wordlist(self, name: str, force: bool = False) -> bool:
        """
        Télécharge une wordlist par défaut
        
        Args:
            name: Nom de la wordlist
            force: Forcer le téléchargement même si existe
        """
        if name not in self.DEFAULT_WORDLISTS:
            if not self.stealth_mode:
                print(f"Wordlist inconnue: {name}")
            return False
        
        info = self.DEFAULT_WORDLISTS[name]
        file_path = self.wordlist_dir / name
        
        if file_path.exists() and not force:
            if not self.stealth_mode:
                print(f"Wordlist {name} existe déjà")
            return True
        
        if not self.stealth_mode:
            print(f"Téléchargement de {name}...")
        
        try:
            response = requests.get(info['url'], stream=True, timeout=300)
            response.raise_for_status()
            
            if info.get('compressed', False):
                # Sauvegarder le fichier compressé
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:
                # Sauvegarder et potentiellement compresser
                with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(response.text)
            
            # Mettre à jour les informations
            self._scan_wordlists()
            
            if not self.stealth_mode:
                print(f"✅ Wordlist {name} téléchargée")
            return True
            
        except Exception as e:
            if not self.stealth_mode:
                print(f"❌ Erreur téléchargement {name}: {e}")
            return False
    
    def download_all_default(self) -> Dict[str, bool]:
        """
        Télécharge toutes les wordlists par défaut
        
        Returns:
            Dictionnaire des résultats par wordlist
        """
        results = {}
        for name in self.DEFAULT_WORDLISTS:
            results[name] = self.download_wordlist(name)
        return results
    
    def create_wordlist(self, name: str, words: List[str], compress: bool = False) -> bool:
        """
        Crée une wordlist à partir d'une liste de mots
        
        Args:
            name: Nom de la wordlist
            words: Liste des mots
            compress: Compresser le fichier
        """
        file_path = self.wordlist_dir / name
        if compress:
            file_path = file_path.with_suffix('.txt.gz')
        
        try:
            if compress:
                import gzip
                with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                    for word in words:
                        f.write(word + '\n')
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for word in words:
                        f.write(word + '\n')
            
            self._scan_wordlists()
            return True
        except Exception as e:
            if not self.stealth_mode:
                print(f"Erreur création wordlist: {e}")
            return False
    
    def generate_from_pattern(self, name: str, pattern: str, 
                              min_len: int = 1, max_len: int = 8) -> bool:
        """
        Génère une wordlist à partir d'un pattern
        
        Args:
            name: Nom de la wordlist
            pattern: Pattern (ex: "admin{num}" ou "user{letter}")
            min_len: Longueur minimale
            max_len: Longueur maximale
        """
        words = set()
        
        # Pattern avec numéros
        if '{num}' in pattern:
            for i in range(min_len, max_len + 1):
                words.add(pattern.replace('{num}', str(i)))
        
        # Pattern avec lettres
        if '{letter}' in pattern:
            import string
            for letter in string.ascii_lowercase[:max_len]:
                words.add(pattern.replace('{letter}', letter))
        
        # Pattern avec année
        if '{year}' in pattern:
            from datetime import datetime
            current_year = datetime.now().year
            for year in range(current_year - 5, current_year + 1):
                words.add(pattern.replace('{year}', str(year)))
        
        # Pattern avec mois
        if '{month}' in pattern:
            for month in range(1, 13):
                words.add(pattern.replace('{month}', str(month).zfill(2)))
        
        return self.create_wordlist(name, list(words))
    
    def merge_wordlists(self, name: str, sources: List[str], 
                        deduplicate: bool = True) -> bool:
        """
        Fusionne plusieurs wordlists
        
        Args:
            name: Nom de la wordlist de sortie
            sources: Liste des noms des wordlists sources
            deduplicate: Dédupliquer les entrées
        """
        all_words = set() if deduplicate else []
        
        for source in sources:
            if source not in self.wordlists:
                if not self.stealth_mode:
                    print(f"Wordlist source non trouvée: {source}")
                return False
            
            words = self.load_wordlist(source)
            if deduplicate:
                all_words.update(words)
            else:
                all_words.extend(words)
        
        return self.create_wordlist(name, list(all_words) if deduplicate else all_words)
    
    def filter_wordlist(self, name: str, source: str, 
                        min_len: int = 0, max_len: int = 0,
                        contains: Optional[str] = None,
                        starts_with: Optional[str] = None,
                        ends_with: Optional[str] = None) -> bool:
        """
        Filtre une wordlist selon des critères
        
        Args:
            name: Nom de la wordlist de sortie
            source: Nom de la wordlist source
            min_len: Longueur minimale
            max_len: Longueur maximale
            contains: Doit contenir cette chaîne
            starts_with: Doit commencer par cette chaîne
            ends_with: Doit finir par cette chaîne
        """
        if source not in self.wordlists:
            if not self.stealth_mode:
                print(f"Wordlist source non trouvée: {source}")
            return False
        
        words = self.load_wordlist(source)
        filtered = []
        
        for word in words:
            if min_len and len(word) < min_len:
                continue
            if max_len and len(word) > max_len:
                continue
            if contains and contains not in word:
                continue
            if starts_with and not word.startswith(starts_with):
                continue
            if ends_with and not word.endswith(ends_with):
                continue
            filtered.append(word)
        
        return self.create_wordlist(name, filtered)
    
    def split_wordlist(self, name: str, source: str, num_parts: int) -> List[str]:
        """
        Divise une wordlist en plusieurs parties
        
        Args:
            name: Préfixe du nom des wordlists
            source: Nom de la wordlist source
            num_parts: Nombre de parties
            
        Returns:
            Liste des noms des wordlists créées
        """
        if source not in self.wordlists:
            if not self.stealth_mode:
                print(f"Wordlist source non trouvée: {source}")
            return []
        
        words = self.load_wordlist(source)
        part_size = len(words) // num_parts
        
        created = []
        for i in range(num_parts):
            start = i * part_size
            end = start + part_size if i < num_parts - 1 else len(words)
            part_words = words[start:end]
            part_name = f"{name}_part{i+1}.txt"
            if self.create_wordlist(part_name, part_words):
                created.append(part_name)
        
        return created
    
    def sample_wordlist(self, source: str, sample_size: int) -> List[str]:
        """
        Extrait un échantillon aléatoire d'une wordlist
        
        Args:
            source: Nom de la wordlist source
            sample_size: Taille de l'échantillon
            
        Returns:
            Liste des mots échantillonnés
        """
        if source not in self.wordlists:
            if not self.stealth_mode:
                print(f"Wordlist source non trouvée: {source}")
            return []
        
        words = self.load_wordlist(source)
        if sample_size >= len(words):
            return words
        
        return random.sample(words, sample_size)
    
    def load_wordlist(self, name: str, max_lines: int = 0) -> List[str]:
        """
        Charge une wordlist en mémoire
        
        Args:
            name: Nom de la wordlist
            max_lines: Nombre maximum de lignes à charger (0 = tout)
            
        Returns:
            Liste des mots
        """
        if name not in self.wordlists:
            if not self.stealth_mode:
                print(f"Wordlist non trouvée: {name}")
            return []
        
        info = self.wordlists[name]
        info.times_used += 1
        info.last_used = datetime.now()
        
        words = []
        try:
            if info.compressed:
                import gzip
                with gzip.open(info.path, 'rt', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        if max_lines and i >= max_lines:
                            break
                        words.append(line.strip())
            else:
                with open(info.path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        if max_lines and i >= max_lines:
                            break
                        words.append(line.strip())
        except Exception as e:
            if not self.stealth_mode:
                print(f"Erreur chargement wordlist {name}: {e}")
        
        return words
    
    def load_wordlist_lazy(self, name: str) -> Iterator[str]:
        """
        Charge une wordlist paresseusement (générateur)
        
        Args:
            name: Nom de la wordlist
            
        Yields:
            Mots un par un
        """
        if name not in self.wordlists:
            if not self.stealth_mode:
                print(f"Wordlist non trouvée: {name}")
            return
        
        info = self.wordlists[name]
        info.times_used += 1
        info.last_used = datetime.now()
        
        try:
            if info.compressed:
                import gzip
                with gzip.open(info.path, 'rt', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        yield line.strip()
            else:
                with open(info.path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        yield line.strip()
        except Exception as e:
            if not self.stealth_mode:
                print(f"Erreur lecture wordlist {name}: {e}")
    
    def get_wordlist_stats(self, name: str) -> Dict[str, Any]:
        """
        Obtient des statistiques sur une wordlist
        
        Args:
            name: Nom de la wordlist
            
        Returns:
            Dictionnaire des statistiques
        """
        if name not in self.wordlists:
            return {}
        
        words = self.load_wordlist(name)
        
        if not words:
            return {}
        
        lengths = [len(w) for w in words]
        length_counter = Counter(lengths)
        
        return {
            'name': name,
            'total_words': len(words),
            'unique_words': len(set(words)),
            'avg_length': sum(lengths) / len(lengths),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'length_distribution': dict(length_counter.most_common(10)),
            'most_common': Counter(words).most_common(10),
            'size_mb': self.wordlists[name].size / (1024 * 1024)
        }
    
    def optimize_wordlist(self, name: str, min_len: int = 3, 
                          max_len: int = 32) -> bool:
        """
        Optimise une wordlist (supprime les mots trop courts/longs)
        
        Args:
            name: Nom de la wordlist
            min_len: Longueur minimale
            max_len: Longueur maximale
        """
        return self.filter_wordlist(f"{name}_optimized", name, 
                                    min_len=min_len, max_len=max_len)
    
    def delete_wordlist(self, name: str) -> bool:
        """
        Supprime une wordlist
        
        Args:
            name: Nom de la wordlist
        """
        if name not in self.wordlists:
            return False
        
        try:
            self.wordlists[name].path.unlink()
            del self.wordlists[name]
            return True
        except Exception as e:
            if not self.stealth_mode:
                print(f"Erreur suppression {name}: {e}")
            return False
    
    def compress_wordlist(self, name: str) -> bool:
        """
        Compresse une wordlist (gzip)
        
        Args:
            name: Nom de la wordlist
        """
        if name not in self.wordlists:
            return False
        
        info = self.wordlists[name]
        if info.compressed:
            if not self.stealth_mode:
                print(f"Wordlist {name} déjà compressée")
            return True
        
        words = self.load_wordlist(name)
        new_name = f"{name}.gz"
        
        return self.create_wordlist(new_name, words, compress=True)
    
    def export_wordlist(self, name: str, output_file: str) -> bool:
        """
        Exporte une wordlist vers un fichier
        
        Args:
            name: Nom de la wordlist
            output_file: Fichier de sortie
        """
        if name not in self.wordlists:
            return False
        
        words = self.load_wordlist(name)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for word in words:
                    f.write(word + '\n')
            return True
        except Exception as e:
            if not self.stealth_mode:
                print(f"Erreur export: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du gestionnaire
        
        Returns:
            Dictionnaire des statistiques
        """
        total_size = sum(info.size for info in self.wordlists.values())
        total_lines = sum(info.lines for info in self.wordlists.values())
        
        return {
            'total_wordlists': len(self.wordlists),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_lines': total_lines,
            'wordlists': self.list_wordlists(),
            'stealth_mode': self.stealth_mode,
            'apt_mode': self.apt_mode,
            'directory': str(self.wordlist_dir)
        }


# Instance globale
wordlist_manager = WordlistManager()


if __name__ == "__main__":
    print("=" * 60)
    print("Test du gestionnaire de wordlists")
    print("=" * 60)
    
    # Lister les wordlists
    print("\n📋 Wordlists disponibles:")
    for wl in wordlist_manager.list_wordlists():
        print(f"  - {wl['name']}: {wl['lines']} lignes, {wl['size_mb']} MB")
    
    # Télécharger une wordlist
    print("\n📥 Téléchargement de common_passwords.txt...")
    wordlist_manager.download_wordlist("common_passwords.txt")
    
    # Générer une wordlist
    print("\n🔨 Génération d'une wordlist pattern...")
    wordlist_manager.generate_from_pattern("admin_years", "admin{year}", min_len=2020, max_len=2024)
    
    # Statistiques
    print("\n📊 Statistiques:")
    stats = wordlist_manager.get_statistics()
    print(f"  Total wordlists: {stats['total_wordlists']}")
    print(f"  Taille totale: {stats['total_size_mb']} MB")
    print(f"  Lignes totales: {stats['total_lines']}")
    
    # Analyse d'une wordlist
    if "common_passwords.txt" in wordlist_manager.wordlists:
        print("\n🔍 Analyse de common_passwords.txt:")
        analysis = wordlist_manager.get_wordlist_stats("common_passwords.txt")
        print(f"  Mots: {analysis['total_words']}")
        print(f"  Longueur moyenne: {analysis['avg_length']:.1f}")
        print(f"  Top 10: {analysis['most_common'][:5]}")
    
    print("\n✅ Tests terminés")