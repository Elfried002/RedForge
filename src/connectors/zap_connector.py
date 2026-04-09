#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connecteur pour OWASP ZAP - Scanner de vulnérabilités web complet
Version avec support furtif, APT et intégration avancée
"""

import json
import time
import random
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from datetime import datetime
from dataclasses import dataclass, field

from src.connectors.base_connector import BaseConnector


@dataclass
class ZAPConfig:
    """Configuration pour OWASP ZAP"""
    host: str = "localhost"
    port: int = 8080
    api_key: Optional[str] = None
    auto_start: bool = True
    max_scan_time: int = 3600
    policy_name: str = "Default Policy"


class ZAPConnector(BaseConnector):
    """Connecteur avancé pour OWASP ZAP avec support furtif"""
    
    def __init__(self, config: Optional[ZAPConfig] = None):
        """
        Initialise le connecteur ZAP
        
        Args:
            config: Configuration ZAP
        """
        self.config = config or ZAPConfig()
        self.zap = None
        self.current_session = None
        super().__init__()
    
    def _find_tool(self) -> Optional[str]:
        """Trouve l'exécutable ZAP"""
        import shutil
        
        paths = [
            "zap-cli",
            "zap.sh",
            "/usr/bin/zap-cli",
            "/usr/local/bin/zap-cli",
            "/opt/zap/zap.sh"
        ]
        
        for path in paths:
            if path and shutil.which(path):
                return path
        
        return None
    
    def _connect_api(self) -> bool:
        """Établit la connexion avec l'API ZAP"""
        if self.zap:
            return True
        
        try:
            from zapv2 import ZAPv2
            
            self.zap = ZAPv2(
                proxies={'http': f'http://{self.config.host}:{self.config.port}', 
                        'https': f'http://{self.config.host}:{self.config.port}'},
                apikey=self.config.api_key
            )
            
            # Vérifier la connexion
            version = self.zap.core.version
            return True
        except ImportError:
            if not self.apt_mode:
                print("⚠️  python-owasp-zap-v2.4 non installé. Installation: pip install zapv2")
            return False
        except Exception as e:
            if not self.apt_mode:
                print(f"❌ Erreur connexion ZAP API: {e}")
            return False
    
    def start_zap_daemon(self) -> bool:
        """Démarre le démon ZAP en arrière-plan"""
        import subprocess
        
        if not self.available:
            return False
        
        try:
            cmd = [self.tool_path, "-daemon", "-port", str(self.config.port), 
                   "-host", self.config.host]
            
            if self.config.api_key:
                cmd.extend(["-config", f"api.key={self.config.api_key}"])
            
            # Mode silencieux en APT
            if self.apt_mode:
                cmd.append("-silent")
            
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Attendre le démarrage
            for _ in range(self.config.max_scan_time // 10):
                time.sleep(10)
                if self._connect_api():
                    return True
            
            return False
        except Exception as e:
            if not self.apt_mode:
                print(f"❌ Erreur démarrage ZAP: {e}")
            return False
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Lance un scan complet avec ZAP
        
        Args:
            target: URL cible
            **kwargs:
                - spider: Activer le spider
                - active_scan: Lancer un scan actif
                - ajax_spider: Utiliser le spider AJAX
                - policy: Politique de scan
                - context_name: Nom du contexte
                - max_duration: Durée max du scan
        """
        if not self._connect_api():
            if self.config.auto_start:
                if not self.start_zap_daemon():
                    return {
                        "success": False,
                        "error": "Impossible de démarrer ou connecter ZAP",
                        "alerts": [],
                        "apt_mode": self.apt_mode
                    }
            else:
                return {
                    "success": False,
                    "error": "Impossible de se connecter à ZAP",
                    "alerts": [],
                    "apt_mode": self.apt_mode
                }
        
        try:
            # Appliquer le délai furtif
            self._apply_stealth_delay()
            
            # URL cible
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
            
            # Démarrer une nouvelle session
            session_name = f"RedForge_{int(time.time())}"
            self.zap.core.new_session(name=session_name, overwrite=True)
            self.current_session = session_name
            
            # Créer un contexte
            context_name = kwargs.get('context_name', f"Context_{int(time.time())}")
            self.zap.context.new_context(context_name)
            self.zap.context.include_in_context(context_name, f"{target}.*")
            
            # Mode APT: réduire l'agressivité
            if self.apt_mode:
                kwargs.setdefault('max_duration', 1800)
                kwargs.setdefault('spider', True)
                kwargs.setdefault('active_scan', False)  # Pas de scan actif en APT
            
            results = {
                "success": True,
                "target": target,
                "alerts": [],
                "alerts_count": 0,
                "scan_time": time.time(),
                "context": context_name,
                "session": session_name,
                "apt_mode": self.apt_mode
            }
            
            # 1. Spidering
            if kwargs.get('spider', True):
                print("  → Spidering en cours...")
                spider_id = self.zap.spider.scan(target)
                max_duration = kwargs.get('max_duration', self.config.max_scan_time)
                start_time = time.time()
                
                while int(self.zap.spider.status(spider_id)) < 100:
                    if time.time() - start_time > max_duration:
                        self.zap.spider.stop(spider_id)
                        break
                    time.sleep(5)
                
                results["spider_completed"] = True
            
            # 2. AJAX Spider
            if kwargs.get('ajax_spider'):
                print("  → AJAX Spider en cours...")
                self.zap.ajaxSpider.scan(target)
                max_duration = kwargs.get('max_duration', 600)
                start_time = time.time()
                
                while self.zap.ajaxSpider.status() != 'stopped':
                    if time.time() - start_time > max_duration:
                        self.zap.ajaxSpider.stop()
                        break
                    time.sleep(3)
                
                results["ajax_spider_completed"] = True
            
            # 3. Scan actif
            if kwargs.get('active_scan', True):
                print("  → Scan actif en cours...")
                policy = kwargs.get('policy', self.config.policy_name)
                scan_id = self.zap.ascan.scan(target, scanpolicyname=policy)
                max_duration = kwargs.get('max_duration', self.config.max_scan_time)
                start_time = time.time()
                
                while int(self.zap.ascan.status(scan_id)) < 100:
                    if time.time() - start_time > max_duration:
                        self.zap.ascan.stop(scan_id)
                        break
                    time.sleep(10)
                
                results["active_scan_completed"] = True
            
            # 4. Récupérer les alertes
            alerts = self.zap.core.alerts(baseurl=target)
            results["alerts"] = self.parse_alerts(alerts)
            results["alerts_count"] = len(alerts)
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "alerts": [],
                "apt_mode": self.apt_mode
            }
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie (utilisé pour l'API)"""
        return self.parse_alerts(output)
    
    def parse_alerts(self, alerts: List) -> List[Dict[str, Any]]:
        """
        Parse les alertes ZAP en format structuré
        
        Args:
            alerts: Liste des alertes ZAP
            
        Returns:
            Liste structurée des alertes
        """
        parsed_alerts = []
        
        risk_map = {
            'High': 'critical',
            'Medium': 'high',
            'Low': 'medium',
            'Informational': 'info'
        }
        
        confidence_map = {
            'High': 90,
            'Medium': 70,
            'Low': 50,
            'Informational': 30
        }
        
        for alert in alerts:
            risk = alert.get('risk', 'Informational')
            parsed = {
                "name": alert.get('name', 'Unknown'),
                "risk": risk,
                "severity": risk_map.get(risk, 'medium'),
                "confidence": alert.get('confidence', 'Low'),
                "confidence_score": confidence_map.get(alert.get('confidence', 'Low'), 50),
                "url": alert.get('url', ''),
                "param": alert.get('param', ''),
                "attack": alert.get('attack', ''),
                "evidence": alert.get('evidence', ''),
                "description": alert.get('description', ''),
                "solution": alert.get('solution', ''),
                "reference": alert.get('reference', ''),
                "cwe_id": alert.get('cweid', ''),
                "wasc_id": alert.get('wascid', ''),
                "plugin_id": alert.get('pluginId', '')
            }
            parsed_alerts.append(parsed)
        
        return parsed_alerts
    
    def quick_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scan rapide (spider + scan actif basique)
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        kwargs['spider'] = True
        kwargs['active_scan'] = True
        kwargs['ajax_spider'] = False
        return self.scan(target, **kwargs)
    
    def passive_scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scan passif uniquement (pas d'attaques actives)
        
        Args:
            target: URL cible
            **kwargs: Options supplémentaires
        """
        kwargs['spider'] = True
        kwargs['active_scan'] = False
        kwargs['ajax_spider'] = False
        return self.scan(target, **kwargs)
    
    def api_scan(self, target: str, api_file: str = None, **kwargs) -> Dict[str, Any]:
        """
        Scan spécifique pour API
        
        Args:
            target: URL cible
            api_file: Fichier OpenAPI/Swagger
            **kwargs: Options supplémentaires
        """
        if api_file:
            # Importer la définition API
            self.zap.openapi.import_file(api_file, target)
        
        kwargs['spider'] = True
        kwargs['active_scan'] = True
        return self.scan(target, **kwargs)
    
    def generate_report(self, target: str, format: str = 'html') -> Optional[str]:
        """
        Génère un rapport au format spécifié
        
        Args:
            target: URL cible
            format: Format du rapport (html, json, xml, md)
            
        Returns:
            Contenu du rapport
        """
        if not self._connect_api():
            return None
        
        formats = {
            'html': self.zap.core.htmlreport,
            'json': self.zap.core.jsonreport,
            'xml': self.zap.core.xmlreport,
            'md': self._generate_markdown_report
        }
        
        report_func = formats.get(format.lower())
        if report_func:
            if format == 'md':
                return report_func(target)
            return report_func()
        
        return None
    
    def _generate_markdown_report(self, target: str) -> str:
        """
        Génère un rapport Markdown
        
        Args:
            target: URL cible
            
        Returns:
            Rapport en Markdown
        """
        alerts = self.zap.core.alerts(baseurl=target)
        parsed_alerts = self.parse_alerts(alerts)
        
        report = f"""# Rapport de Scan ZAP - RedForge

## Informations Générales
- **Cible**: {target}
- **Date**: {datetime.now().isoformat()}
- **Total Alertes**: {len(parsed_alerts)}

## Résumé des Alertes

| Sévérité | Nombre |
|----------|--------|
| Critique | {len([a for a in parsed_alerts if a['severity'] == 'critical'])} |
| Élevée | {len([a for a in parsed_alerts if a['severity'] == 'high'])} |
| Moyenne | {len([a for a in parsed_alerts if a['severity'] == 'medium'])} |
| Faible | {len([a for a in parsed_alerts if a['severity'] == 'low'])} |
| Info | {len([a for a in parsed_alerts if a['severity'] == 'info'])} |

## Détail des Alertes

"""
        for alert in parsed_alerts:
            report += f"""
### {alert['name']}
- **Sévérité**: {alert['severity'].upper()}
- **URL**: {alert['url']}
- **Paramètre**: {alert['param']}
- **Description**: {alert['description']}
- **Solution**: {alert['solution']}

"""
        
        return report
    
    def stop_scan(self) -> bool:
        """Arrête tous les scans en cours"""
        if not self._connect_api():
            return False
        
        try:
            # Arrêter le spider
            self.zap.spider.stop_all_scans()
            # Arrêter l'AJAX spider
            self.zap.ajaxSpider.stop()
            # Arrêter le scan actif
            self.zap.ascan.stop_all_scans()
            return True
        except:
            return False
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de version de ZAP
        
        Returns:
            Dictionnaire avec les informations de version
        """
        if not self._connect_api():
            return {"available": False}
        
        try:
            version = self.zap.core.version
            return {
                "available": True,
                "version": version,
                "tool": "owasp_zap",
                "api_version": self.zap.core.api_version
            }
        except:
            return {"available": False}
    
    def get_policies(self) -> List[str]:
        """
        Récupère la liste des politiques de scan disponibles
        
        Returns:
            Liste des politiques
        """
        if not self._connect_api():
            return []
        
        try:
            return self.zap.ascan.scan_policies()
        except:
            return ["Default Policy"]