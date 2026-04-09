#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de découverte de sous-domaines pour RedForge
Utilise DNS bruteforce, certificats SSL, API publiques et techniques avancées
Version avec support furtif, APT et détection avancée
"""

import subprocess
import re
import socket
import random
import string
import time
from typing import Dict, Any, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

import dns.resolver
import dns.query
import dns.zone
import dns.exception

from src.core.stealth_engine import StealthEngine


class SubdomainFinder:
    """Découverte avancée de sous-domaines avec support furtif"""
    
    def __init__(self):
        # Wordlist de base
        self.common_subdomains = [
            "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "webdisk",
            "ns2", "cpanel", "whm", "autodiscover", "autoconfig", "m", "imap", "test",
            "ns", "blog", "pop3", "dev", "www2", "admin", "forum", "news", "vpn", "ns3",
            "mail2", "new", "mysql", "old", "lists", "support", "mobile", "mx", "static",
            "docs", "beta", "shop", "sql", "secure", "demo", "cp", "calendar", "wiki",
            "web", "media", "email", "images", "img", "download", "dns", "piwik", "stats",
            "dashboard", "portal", "manage", "start", "info", "apps", "video", "sip",
            "dns2", "api", "cdn", "mssql", "remote", "server", "ftp2", "stage", "vps"
        ]
        
        # Wordlist étendue
        self.extended_subdomains = self.common_subdomains + [
            "app", "backup", "client", "config", "db", "exchange", "internal",
            "jenkins", "jira", "kibana", "log", "monitor", "owa", "pay", "payment",
            "private", "prod", "production", "redis", "repo", "staging", "status",
            "store", "staging2", "svn", "test2", "testing", "uat", "webapp", "worker",
            "git", "grafana", "elk", "kafka", "zookeeper", "spark", "hadoop",
            "k8s", "kubernetes", "docker", "registry", "nexus", "artifactory"
        ]
        
        # Moteur de furtivité
        self.stealth_mode = False
        self.apt_mode = False
        self.stealth_engine = StealthEngine()
        
        # Cache
        self.resolution_cache = {}
    
    def set_stealth_config(self, config: Dict[str, Any]):
        """
        Configure le mode furtif
        
        Args:
            config: Configuration de furtivité
        """
        self.stealth_mode = config.get('enabled', False)
        self.apt_mode = config.get('apt_mode', False)
        
        if self.stealth_mode:
            self.stealth_engine.set_delays(
                min_delay=config.get('delay_min', 1),
                max_delay=config.get('delay_max', 5),
                jitter=config.get('jitter', 0.3)
            )
            if self.apt_mode:
                self.stealth_engine.enable_apt_mode()
    
    def _apply_stealth_delay(self):
        """Applique un délai furtif"""
        if self.stealth_mode:
            self.stealth_engine.apply_delay()
    
    def find(self, domain: str, **kwargs) -> Dict[str, Any]:
        """
        Recherche les sous-domaines du domaine cible
        
        Args:
            domain: Domaine principal
            **kwargs:
                - wordlist: Wordlist personnalisée
                - threads: Nombre de threads
                - use_cert: Utiliser les certificats SSL
                - use_api: Utiliser les API publiques
                - deep_scan: Scan approfondi
        """
        print(f"  → Recherche de sous-domaines pour {domain}")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Détection discrète")
        
        # Nettoyer le domaine
        domain = domain.replace('http://', '').replace('https://', '').split('/')[0]
        
        all_subdomains: Set[str] = set()
        
        # Vérifier le wildcard DNS
        has_wildcard = self.check_wildcard_dns(domain)
        if has_wildcard:
            print(f"    ⚠️ Wildcard DNS détecté - Les résultats peuvent inclure des faux positifs")
        
        # Méthode 1: Bruteforce DNS
        wordlist = kwargs.get('wordlist', self.extended_subdomains)
        threads = min(kwargs.get('threads', 20), 5 if self.apt_mode else 20)
        
        # Limiter la wordlist en mode APT
        if self.apt_mode:
            wordlist = wordlist[:100]
        
        print(f"    → Bruteforce DNS ({len(wordlist)} entrées)...")
        brute_result = self._bruteforce_dns(domain, wordlist, threads, has_wildcard)
        all_subdomains.update(brute_result)
        
        # Méthode 2: Certificats SSL (Certificate Transparency)
        if kwargs.get('use_cert', True):
            print(f"    → Recherche via certificats SSL...")
            self._apply_stealth_delay()
            cert_subdomains = self._get_subdomains_from_cert(domain)
            all_subdomains.update(cert_subdomains)
        
        # Méthode 3: DNS records (AXFR, NSEC, etc.)
        print(f"    → Analyse des enregistrements DNS...")
        self._apply_stealth_delay()
        dns_subdomains = self._get_subdomains_from_dns(domain)
        all_subdomains.update(dns_subdomains)
        
        # Méthode 4: APIs publiques
        if kwargs.get('use_api', False) and not self.apt_mode:
            print(f"    → Consultation APIs publiques...")
            api_subdomains = self._get_subdomains_from_apis(domain)
            all_subdomains.update(api_subdomains)
        
        # Méthode 5: Scan approfondi (permutations)
        if kwargs.get('deep_scan', False) and not self.apt_mode:
            print(f"    → Permutations et variations...")
            perm_subdomains = self._generate_permutations(domain, list(all_subdomains))
            all_subdomains.update(perm_subdomains)
        
        # Résolution des sous-domaines trouvés
        print(f"    → Résolution des adresses IP...")
        resolved = self._resolve_subdomains(list(all_subdomains), domain, has_wildcard)
        
        return {
            "domain": domain,
            "subdomains": resolved,
            "count": len(resolved),
            "has_wildcard": has_wildcard,
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "method_summary": {
                "bruteforce": len(brute_result),
                "certificates": len(cert_subdomains) if kwargs.get('use_cert', True) else 0,
                "dns_records": len(dns_subdomains),
                "apis": len(api_subdomains) if kwargs.get('use_api', False) else 0,
                "permutations": len(perm_subdomains) if kwargs.get('deep_scan', False) else 0
            }
        }
    
    def _bruteforce_dns(self, domain: str, wordlist: List[str], threads: int, has_wildcard: bool) -> Set[str]:
        """Bruteforce DNS avec une wordlist"""
        found_subdomains: Set[str] = set()
        tested = 0
        
        def check_subdomain(sub):
            full_domain = f"{sub}.{domain}"
            try:
                resolver = dns.resolver.Resolver()
                resolver.timeout = 3
                resolver.lifetime = 5
                
                answers = resolver.resolve(full_domain, 'A')
                if answers:
                    return full_domain
            except:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(check_subdomain, sub): sub for sub in wordlist}
            
            for future in as_completed(futures):
                result = future.result()
                tested += 1
                if result:
                    found_subdomains.add(result)
                    if not self.stealth_mode:
                        print(f"      ✓ Trouvé: {result}")
                
                # Délai furtif entre les lots
                if self.apt_mode and tested % 20 == 0:
                    self._apply_stealth_delay()
        
        return found_subdomains
    
    def _get_subdomains_from_cert(self, domain: str) -> Set[str]:
        """Récupère les sous-domaines depuis les certificats SSL (crt.sh)"""
        subdomains: Set[str] = set()
        
        try:
            import requests
            
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    for entry in data[:100]:  # Limiter en mode APT
                        name = entry.get('name_value', '')
                        if name:
                            for sub in name.split('\n'):
                                sub = sub.strip().lower()
                                if sub.endswith(domain) and sub != domain:
                                    subdomains.add(sub)
                except:
                    pass
        except Exception as e:
            if not self.stealth_mode:
                print(f"      ⚠️ Erreur API crt.sh: {e}")
        
        return subdomains
    
    def _get_subdomains_from_dns(self, domain: str) -> Set[str]:
        """Récupère les sous-domaines depuis les enregistrements DNS"""
        subdomains: Set[str] = set()
        
        record_types = ['NS', 'MX', 'TXT', 'CNAME', 'SOA']
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                for answer in answers:
                    answer_str = str(answer).lower()
                    matches = re.findall(r'([a-zA-Z0-9-]+\.' + re.escape(domain) + r')', answer_str)
                    for match in matches:
                        if match != domain:
                            subdomains.add(match)
            except:
                pass
        
        # Tentative de transfert de zone
        try:
            ns_servers = dns.resolver.resolve(domain, 'NS')
            for ns in ns_servers:
                ns_str = str(ns)
                try:
                    zone = dns.query.xfr(ns_str, domain, timeout=5)
                    for record in zone:
                        if record.rdtype == dns.rdatatype.A:
                            sub = str(record.name).rstrip('.')
                            if sub != domain and sub.endswith(domain):
                                subdomains.add(sub)
                except:
                    pass
        except:
            pass
        
        return subdomains
    
    def _get_subdomains_from_apis(self, domain: str) -> Set[str]:
        """Utilise des APIs publiques pour trouver des sous-domaines"""
        subdomains: Set[str] = set()
        
        # API AlienVault OTX
        try:
            import requests
            url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('passive_dns', []):
                    hostname = item.get('hostname', '')
                    if hostname and hostname != domain and hostname.endswith(domain):
                        subdomains.add(hostname)
        except:
            pass
        
        return subdomains
    
    def _generate_permutations(self, domain: str, existing: List[str]) -> Set[str]:
        """Génère des permutations des sous-domaines existants"""
        permutations = set()
        
        prefixes = ['dev-', 'test-', 'stage-', 'prod-', 'backup-', 'old-', 'new-']
        suffixes = ['-dev', '-test', '-stage', '-prod', '-backup', '-old', '-new']
        
        for sub in existing:
            sub_name = sub.replace(f'.{domain}', '')
            
            # Ajouter des préfixes
            for prefix in prefixes:
                new_sub = f"{prefix}{sub_name}.{domain}"
                permutations.add(new_sub)
            
            # Ajouter des suffixes
            for suffix in suffixes:
                new_sub = f"{sub_name}{suffix}.{domain}"
                permutations.add(new_sub)
        
        return permutations
    
    def _resolve_subdomains(self, subdomains: List[str], domain: str, has_wildcard: bool) -> List[Dict[str, Any]]:
        """Résout les sous-domaines en adresses IP"""
        results = []
        
        def resolve(sub):
            # Vérifier le cache
            if sub in self.resolution_cache:
                return self.resolution_cache[sub]
            
            try:
                resolver = dns.resolver.Resolver()
                resolver.timeout = 3
                resolver.lifetime = 5
                
                answers = resolver.resolve(sub, 'A')
                ips = [str(answer) for answer in answers]
                
                result = {
                    "subdomain": sub,
                    "ips": ips,
                    "resolved": True,
                    "ip_count": len(ips)
                }
                self.resolution_cache[sub] = result
                return result
            except:
                result = {
                    "subdomain": sub,
                    "ips": [],
                    "resolved": False,
                    "ip_count": 0
                }
                self.resolution_cache[sub] = result
                return result
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(resolve, sub): sub for sub in subdomains}
            
            for future in as_completed(futures):
                result = future.result()
                if result["resolved"]:
                    results.append(result)
        
        return sorted(results, key=lambda x: x["subdomain"])
    
    def check_wildcard_dns(self, domain: str) -> bool:
        """Vérifie si le domaine utilise un DNS wildcard"""
        random_sub = ''.join(random.choices(string.ascii_lowercase, k=15))
        test_domain = f"{random_sub}.{domain}"
        
        try:
            dns.resolver.resolve(test_domain, 'A')
            return True
        except:
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du module"""
        return {
            "cache_size": len(self.resolution_cache),
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode,
            "wordlist_size": len(self.extended_subdomains)
        }
    
    def save_results(self, results: Dict[str, Any], output_file: str) -> bool:
        """Sauvegarde les résultats au format JSON"""
        import json
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
            return False


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de SubdomainFinder")
    print("=" * 60)
    
    finder = SubdomainFinder()
    
    # Configuration mode APT
    finder.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 1,
        'delay_max': 3
    })
    
    # Test (simulé)
    # results = finder.find("example.com")
    # print(f"Sous-domaines trouvés: {results['count']}")
    
    print("\n✅ Module SubdomainFinder chargé avec succès")