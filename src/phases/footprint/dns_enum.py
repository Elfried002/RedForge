#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'énumération DNS pour RedForge
Collecte les enregistrements DNS et informations sur les serveurs de noms
Version avec support furtif, APT et détection avancée
"""

import subprocess
import re
import socket
import dns.resolver
import dns.query
import dns.zone
import dns.exception
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from src.core.stealth_engine import StealthEngine


@dataclass
class DNSRecord:
    """Structure pour un enregistrement DNS"""
    type: str
    value: str
    ttl: Optional[int] = None
    priority: Optional[int] = None


class DNSEnumerator:
    """Énumération avancée des enregistrements DNS avec support furtif"""
    
    def __init__(self):
        self.results = {
            "a_records": [],
            "aaaa_records": [],
            "mx_records": [],
            "ns_records": [],
            "txt_records": [],
            "cname_records": [],
            "soa_record": None,
            "srv_records": [],
            "ptr_records": [],
            "cAA_records": []
        }
        self.stealth_mode = False
        self.apt_mode = False
        self.stealth_engine = StealthEngine()
        self.domain = None
        
        # Types d'enregistrements à interroger
        self.record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SRV', 'PTR', 'CAA']
    
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
    
    def enumerate(self, domain: str) -> Dict[str, Any]:
        """
        Énumération DNS complète
        
        Args:
            domain: Nom de domaine à analyser
            
        Returns:
            Dictionnaire contenant tous les enregistrements DNS
        """
        self.domain = domain
        print(f"  → Énumération DNS pour {domain}")
        if self.apt_mode:
            print(f"  🕵️ Mode APT activé - Requêtes discrètes")
        
        # Nettoyer le domaine
        domain = domain.replace('http://', '').replace('https://', '').split('/')[0]
        
        # Utiliser dnspython pour tous les types d'enregistrements
        for record_type in self.record_types:
            self._query_dns(domain, record_type)
            self._apply_stealth_delay()
        
        # Tentative de transfert de zone
        zone_transfer = self._attempt_zone_transfer(domain)
        
        # Énumération des sous-domaines communs
        common_subdomains = self._enumerate_common_subdomains(domain)
        
        # Reverse lookup pour les IPs trouvées
        reverse_lookups = self._reverse_lookup_ips()
        
        return {
            "domain": domain,
            "records": self.results,
            "zone_transfer": zone_transfer,
            "common_subdomains": common_subdomains,
            "reverse_lookups": reverse_lookups,
            "summary": self._generate_summary(),
            "stealth_mode": self.stealth_mode,
            "apt_mode": self.apt_mode
        }
    
    def _query_dns(self, domain: str, record_type: str):
        """Interroge un type d'enregistrement DNS"""
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 10
            
            # En mode APT, utiliser un resolver différent
            if self.apt_mode:
                resolver.nameservers = ['8.8.8.8', '1.1.1.1']  # DNS publics
            
            answers = resolver.resolve(domain, record_type)
            
            for answer in answers:
                record = DNSRecord(
                    type=record_type,
                    value=str(answer),
                    ttl=answer.ttl if hasattr(answer, 'ttl') else None
                )
                
                # Traitement spécial pour MX (priorité)
                if record_type == 'MX' and hasattr(answer, 'preference'):
                    record.priority = answer.preference
                    self.results["mx_records"].append({
                        "priority": answer.preference,
                        "server": str(answer.exchange),
                        "ttl": answer.ttl
                    })
                elif record_type == 'SRV' and hasattr(answer, 'port'):
                    self.results["srv_records"].append({
                        "service": str(answer.target),
                        "port": answer.port,
                        "priority": answer.priority,
                        "weight": answer.weight,
                        "ttl": answer.ttl
                    })
                else:
                    self.results[f"{record_type.lower()}_records"].append(record.value)
                    
        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            pass
        except dns.exception.Timeout:
            if not self.stealth_mode:
                print(f"    ⚠️ Timeout pour {record_type}")
        except Exception as e:
            if not self.stealth_mode:
                print(f"    ⚠️ Erreur {record_type}: {e}")
    
    def _attempt_zone_transfer(self, domain: str) -> Dict[str, Any]:
        """Tente un transfert de zone DNS"""
        result = {
            "success": False,
            "records": [],
            "message": "",
            "server": None
        }
        
        # Récupérer les serveurs NS
        ns_servers = self.results["ns_records"]
        
        for ns in ns_servers:
            try:
                zone = dns.zone.from_xfr(dns.query.xfr(ns, domain, timeout=10))
                records = []
                for name, node in zone.nodes.items():
                    for rdataset in node.rdatasets:
                        for rdata in rdataset:
                            records.append({
                                "name": str(name),
                                "type": dns.rdatatype.to_text(rdataset.rdtype),
                                "value": str(rdata)
                            })
                
                if records:
                    result["success"] = True
                    result["records"] = records[:100]  # Limiter pour performance
                    result["message"] = f"Transfert réussi depuis {ns}"
                    result["server"] = ns
                    break
                    
            except dns.exception.TransferError:
                continue
            except Exception as e:
                continue
        
        if not result["success"]:
            result["message"] = "Transfert de zone non autorisé"
        
        return result
    
    def _enumerate_common_subdomains(self, domain: str) -> List[str]:
        """Énumère les sous-domaines communs"""
        common_subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'test', 'dev', 'staging',
            'api', 'app', 'admin', 'dashboard', 'portal', 'blog', 'shop', 'store', 'support',
            'help', 'docs', 'static', 'media', 'cdn', 'assets', 'download', 'upload',
            'backup', 'secure', 'vpn', 'remote', 'exchange', 'owa', 'remote', 'cloud'
        ]
        
        found = []
        
        for sub in common_subdomains:
            self._apply_stealth_delay()
            test_domain = f"{sub}.{domain}"
            try:
                dns.resolver.resolve(test_domain, 'A')
                found.append(test_domain)
                if not self.stealth_mode:
                    print(f"      ✓ Sous-domaine trouvé: {test_domain}")
            except:
                pass
        
        return found
    
    def _reverse_lookup_ips(self) -> List[Dict[str, str]]:
        """Effectue une recherche DNS inversée pour les IPs trouvées"""
        results = []
        ips = set()
        
        # Collecter toutes les IPs
        for ip in self.results["a_records"]:
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                ips.add(ip)
        
        for ip in ips:
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                results.append({
                    "ip": ip,
                    "hostname": hostname
                })
            except:
                pass
        
        return results
    
    def reverse_lookup(self, ip_address: str) -> Optional[str]:
        """Recherche DNS inversée pour une IP spécifique"""
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
            return hostname
        except socket.herror:
            return None
    
    def get_all_ips(self) -> List[str]:
        """Récupère toutes les adresses IP associées au domaine"""
        ips = []
        
        # A records
        for record in self.results["a_records"]:
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', record):
                ips.append(record)
        
        # Si pas d'A records, résolution directe
        if not ips and self.domain:
            try:
                ips = [addr[4][0] for addr in socket.getaddrinfo(self.domain, 80)]
            except:
                pass
        
        return ips
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Génère un résumé des découvertes DNS"""
        return {
            "has_mx": len(self.results["mx_records"]) > 0,
            "has_ns": len(self.results["ns_records"]) > 0,
            "has_txt": len(self.results["txt_records"]) > 0,
            "has_soa": self.results["soa_record"] is not None,
            "has_srv": len(self.results["srv_records"]) > 0,
            "ipv4_count": len(self.results["a_records"]),
            "ipv6_count": len(self.results["aaaa_records"]),
            "mx_count": len(self.results["mx_records"]),
            "ns_count": len(self.results["ns_records"]),
            "txt_count": len(self.results["txt_records"]),
            "cname_count": len(self.results["cname_records"])
        }
    
    def get_mail_servers(self) -> List[Dict[str, str]]:
        """Extrait les serveurs mail avec leurs priorités"""
        return sorted(self.results["mx_records"], key=lambda x: x['priority'])
    
    def get_spf_record(self) -> Optional[str]:
        """Extrait l'enregistrement SPF des TXT records"""
        for record in self.results["txt_records"]:
            if 'v=spf' in record.lower():
                return record
        return None
    
    def get_dmarc_record(self) -> Optional[str]:
        """Tente de récupérer l'enregistrement DMARC"""
        if not self.domain:
            return None
        
        try:
            dmarc_domain = f"_dmarc.{self.domain}"
            answers = dns.resolver.resolve(dmarc_domain, 'TXT')
            for answer in answers:
                return str(answer)
        except:
            pass
        return None
    
    def get_dkim_records(self, selector: str = "default") -> List[str]:
        """Récupère les enregistrements DKIM"""
        records = []
        if not self.domain:
            return records
        
        try:
            dkim_domain = f"{selector}._domainkey.{self.domain}"
            answers = dns.resolver.resolve(dkim_domain, 'TXT')
            for answer in answers:
                records.append(str(answer))
        except:
            pass
        
        return records
    
    def get_bimi_record(self) -> Optional[str]:
        """Récupère l'enregistrement BIMI"""
        if not self.domain:
            return None
        
        try:
            bimi_domain = f"default._bimi.{self.domain}"
            answers = dns.resolver.resolve(bimi_domain, 'TXT')
            for answer in answers:
                return str(answer)
        except:
            pass
        return None
    
    def get_mta_sts_record(self) -> Optional[str]:
        """Récupère l'enregistrement MTA-STS"""
        if not self.domain:
            return None
        
        try:
            mta_sts_domain = f"_mta-sts.{self.domain}"
            answers = dns.resolver.resolve(mta_sts_domain, 'TXT')
            for answer in answers:
                return str(answer)
        except:
            pass
        return None
    
    def get_tlsa_records(self, port: int = 443, protocol: str = "tcp") -> List[str]:
        """Récupère les enregistrements TLSA pour DANE"""
        records = []
        if not self.domain:
            return records
        
        try:
            tlsa_domain = f"_{port}._{protocol}.{self.domain}"
            answers = dns.resolver.resolve(tlsa_domain, 'TLSA')
            for answer in answers:
                records.append(str(answer))
        except:
            pass
        
        return records
    
    def get_all_subdomains(self, wordlist: List[str] = None) -> List[str]:
        """Énumère les sous-domaines à partir d'une wordlist"""
        if wordlist is None:
            wordlist = [
                'www', 'mail', 'ftp', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
                'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'test', 'dev',
                'staging', 'api', 'app', 'admin', 'dashboard', 'portal', 'blog',
                'shop', 'store', 'support', 'help', 'docs', 'static', 'media'
            ]
        
        found = []
        
        for sub in wordlist:
            test_domain = f"{sub}.{self.domain}"
            try:
                dns.resolver.resolve(test_domain, 'A')
                found.append(test_domain)
            except:
                pass
        
        return found
    
    def save_results(self, output_file: str) -> bool:
        """Sauvegarde les résultats au format JSON"""
        import json
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "domain": self.domain,
                    "results": self.results,
                    "summary": self._generate_summary()
                }, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
            return False


# Point d'entrée pour tests
if __name__ == "__main__":
    print("=" * 60)
    print("Test de DNSEnumerator")
    print("=" * 60)
    
    enumerator = DNSEnumerator()
    
    # Configuration mode APT
    enumerator.set_stealth_config({
        'enabled': True,
        'apt_mode': True,
        'delay_min': 1,
        'delay_max': 3
    })
    
    # Test (simulé)
    # results = enumerator.enumerate("example.com")
    # print(f"Enregistrements A: {len(results['records']['a_records'])}")
    
    print("\n✅ Module DNSEnumerator chargé avec succès")