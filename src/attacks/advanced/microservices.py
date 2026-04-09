#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'attaques microservices pour RedForge
Détection et exploitation des vulnérabilités dans les architectures microservices
Version: 2.0.0 - Support Multi-Attaque, Stealth & APT
"""

import re
import json
import time
import random
import socket
import requests
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from src.utils.color_output import console


@dataclass
class MicroservicesConfig:
    """Configuration des attaques microservices"""
    stealth_mode: bool = False
    aggressive_mode: bool = False
    timeout: int = 10
    threads: int = 5
    delay_min: float = 0.5
    delay_max: float = 2.0
    scan_ports: bool = True
    ports: List[int] = field(default_factory=lambda: [8080, 8081, 8082, 8083, 8084, 8090, 8091, 8092, 8761, 8500, 9090])


class MicroservicesAttack:
    """Attaques sur les architectures microservices avec support stealth et APT"""
    
    def __init__(self):
        self.config = MicroservicesConfig()
        
        self.service_discovery_paths = [
            "/eureka/apps", "/actuator", "/health", "/info", "/metrics",
            "/env", "/config", "/service-registry", "/discovery",
            "/v2/catalog", "/v1/registration", "/services",
            "/consul/v1/agent/services", "/v1/catalog/services"
        ]
        
        self.api_gateway_paths = [
            "/api", "/gateway", "/router", "/proxy", "/edge",
            "/zuul", "/spring-cloud-gateway", "/kong",
            "/apisix", "/traefik", "/envoy"
        ]
        
        self.sensitive_endpoints = [
            "/actuator/env", "/actuator/health", "/actuator/info",
            "/actuator/metrics", "/actuator/trace", "/actuator/dump",
            "/actuator/heapdump", "/actuator/logfile", "/actuator/configprops",
            "/actuator/mappings", "/actuator/beans", "/actuator/conditions"
        ]
        
        # Endpoints furtifs pour mode stealth
        self.stealth_endpoints = [
            "/actuator/health", "/actuator/info", "/health", "/info"
        ]
        
        # Endpoints APT pour mode agressif
        self.apt_endpoints = [
            "/actuator/env", "/actuator/heapdump", "/actuator/trace",
            "/actuator/logfile", "/actuator/configprops"
        ]
    
    def set_stealth_mode(self, enabled: bool = True):
        """Active le mode furtif"""
        self.config.stealth_mode = enabled
        console.print_info(f"🕵️ Mode furtif {'activé' if enabled else 'désactivé'} pour microservices")
    
    def set_aggressive_mode(self, enabled: bool = True):
        """Active le mode agressif"""
        self.config.aggressive_mode = enabled
        console.print_info(f"⚡ Mode agressif {'activé' if enabled else 'désactivé'} pour microservices")
    
    def _random_delay(self):
        """Ajoute un délai aléatoire pour le mode furtif"""
        if self.config.stealth_mode:
            delay = random.uniform(self.config.delay_min, self.config.delay_max)
            time.sleep(delay)
    
    def _get_endpoints(self) -> List[str]:
        """Retourne les endpoints selon le mode"""
        if self.config.stealth_mode:
            return self.stealth_endpoints
        elif self.config.aggressive_mode:
            return self.sensitive_endpoints + self.apt_endpoints
        return self.sensitive_endpoints
    
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scanne les vulnérabilités dans les microservices
        
        Args:
            target: URL cible
            **kwargs:
                - scan_ports: Scanner les ports supplémentaires
                - service_discovery: Détecter service discovery
                - jwt_secret: Secret JWT pour tests
                - stealth: Mode furtif
                - aggressive: Mode agressif
        """
        console.print_info("🏗️ Test des attaques microservices")
        
        # Appliquer les modes
        if kwargs.get('stealth'):
            self.set_stealth_mode(True)
        if kwargs.get('aggressive'):
            self.set_aggressive_mode(True)
        
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        vulnerabilities = []
        
        # Détection de service discovery
        discovery_vulns = self._test_service_discovery(target)
        vulnerabilities.extend(discovery_vulns)
        
        # Détection d'API gateway
        gateway_vulns = self._test_api_gateway(target)
        vulnerabilities.extend(gateway_vulns)
        
        # Détection d'actuators Spring Boot
        actuator_vulns = self._test_spring_actuators(target)
        vulnerabilities.extend(actuator_vulns)
        
        # Détection de service mesh
        mesh_vulns = self._test_service_mesh(target)
        vulnerabilities.extend(mesh_vulns)
        
        # Détection de ports additionnels
        if kwargs.get('scan_ports', self.config.scan_ports):
            port_vulns = self._scan_additional_ports(target)
            vulnerabilities.extend(port_vulns)
        
        # Test d'authentification entre services
        auth_vulns = self._test_service_auth(target, kwargs.get('jwt_secret'))
        vulnerabilities.extend(auth_vulns)
        
        # Test de configuration
        config_vulns = self._test_configuration(target)
        vulnerabilities.extend(config_vulns)
        
        # Test de circuit breaker (mode agressif)
        if self.config.aggressive_mode:
            circuit_vulns = self._test_circuit_breaker(target)
            vulnerabilities.extend(circuit_vulns)
        
        return {
            "target": target,
            "stealth_mode": self.config.stealth_mode,
            "aggressive_mode": self.config.aggressive_mode,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "summary": self._generate_summary(vulnerabilities)
        }
    
    def _test_service_discovery(self, target: str) -> List[Dict[str, Any]]:
        """Teste les endpoints de service discovery"""
        vulnerabilities = []
        
        for path in self.service_discovery_paths:
            test_url = target.rstrip('/') + path
            
            try:
                response = requests.get(test_url, timeout=self.config.timeout, 
                                       verify=False)
                self._random_delay()
                
                if response.status_code == 200:
                    # Vérifier si des services sont exposés
                    if any(keyword in response.text.lower() for keyword in 
                          ['applications', 'services', 'instances', 'registered']):
                        vulnerabilities.append({
                            "type": "service_discovery",
                            "endpoint": path,
                            "severity": "HIGH",
                            "details": f"Service discovery exposé: {path}",
                            "data_preview": response.text[:200]
                        })
                        console.print_warning(f"      ✓ Service discovery exposé: {path}")
                        
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_api_gateway(self, target: str) -> List[Dict[str, Any]]:
        """Teste les vulnérabilités d'API gateway"""
        vulnerabilities = []
        
        for path in self.api_gateway_paths:
            test_url = target.rstrip('/') + path
            
            try:
                response = requests.get(test_url, timeout=self.config.timeout, 
                                       verify=False)
                self._random_delay()
                
                if response.status_code != 404:
                    # Tester les routes internes
                    route_tests = ['/admin', '/internal', '/private', '/debug', 
                                  '/actuator', '/metrics', '/health']
                    
                    for route in route_tests:
                        route_url = test_url.rstrip('/') + route
                        route_response = requests.get(route_url, timeout=self.config.timeout, 
                                                     verify=False)
                        
                        if route_response.status_code == 200:
                            vulnerabilities.append({
                                "type": "gateway_route",
                                "endpoint": path,
                                "route": route,
                                "severity": "HIGH",
                                "details": f"Route interne exposée via gateway: {route}"
                            })
                            console.print_warning(f"      ✓ Route interne exposée: {route}")
                            break
                            
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_spring_actuators(self, target: str) -> List[Dict[str, Any]]:
        """Teste les endpoints Spring Boot Actuator"""
        vulnerabilities = []
        endpoints = self._get_endpoints()
        
        for endpoint in endpoints:
            test_url = target.rstrip('/') + endpoint
            
            try:
                response = requests.get(test_url, timeout=self.config.timeout, 
                                       verify=False)
                self._random_delay()
                
                if response.status_code == 200:
                    vuln = {
                        "type": "spring_actuator",
                        "endpoint": endpoint,
                        "severity": "HIGH",
                        "details": f"Spring Boot Actuator exposé: {endpoint}"
                    }
                    vulnerabilities.append(vuln)
                    console.print_warning(f"      ✓ Actuator exposé: {endpoint}")
                    
                    # Extraire des informations sensibles
                    if 'env' in endpoint:
                        try:
                            data = response.json()
                            sensitive_keys = ['db.password', 'spring.datasource.password',
                                            'jdbc.password', 'redis.password', 'api.key']
                            for key in sensitive_keys:
                                if key in str(data):
                                    vulnerabilities.append({
                                        "type": "credentials_exposed",
                                        "endpoint": endpoint,
                                        "severity": "CRITICAL",
                                        "details": f"Credentials exposés dans Actuator: {key}"
                                    })
                                    console.print_error(f"      ⚠️ Credentials exposés: {key}")
                                    break
                        except:
                            pass
                            
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_service_mesh(self, target: str) -> List[Dict[str, Any]]:
        """Teste les vulnérabilités de service mesh"""
        vulnerabilities = []
        
        # Endpoints Istio
        istio_endpoints = ['/istio', '/mesh', '/service-mesh', '/sidecar']
        
        for endpoint in istio_endpoints:
            test_url = target.rstrip('/') + endpoint
            
            try:
                response = requests.get(test_url, timeout=self.config.timeout, 
                                       verify=False)
                self._random_delay()
                
                if response.status_code == 200:
                    vulnerabilities.append({
                        "type": "service_mesh_exposed",
                        "endpoint": endpoint,
                        "severity": "HIGH",
                        "details": f"Service mesh endpoint exposé: {endpoint}"
                    })
                    console.print_warning(f"      ✓ Service mesh exposé: {endpoint}")
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _scan_additional_ports(self, target: str) -> List[Dict[str, Any]]:
        """Scanne les ports additionnels pour découvrir des services"""
        vulnerabilities = []
        parsed = urlparse(target)
        hostname = parsed.hostname
        
        if not hostname:
            return vulnerabilities
        
        console.print_info(f"      Scan des ports supplémentaires...")
        
        for port in self.config.ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((hostname, port))
                sock.close()
                
                if result == 0:
                    # Identifier le service potentiel
                    service = self._identify_service(port)
                    vulnerabilities.append({
                        "type": "additional_service",
                        "port": port,
                        "service": service,
                        "severity": "MEDIUM",
                        "details": f"Service additionnel sur port {port} ({service})"
                    })
                    console.print_info(f"      ✓ Port ouvert: {port} ({service})")
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _identify_service(self, port: int) -> str:
        """Identifie le service potentiel sur un port"""
        services = {
            8080: "HTTP Alternative",
            8081: "HTTP Alternative",
            8761: "Eureka Server",
            8500: "Consul",
            9090: "Prometheus",
            3000: "Grafana",
            5601: "Kibana",
            9200: "Elasticsearch",
            6379: "Redis",
            27017: "MongoDB",
            5432: "PostgreSQL",
            3306: "MySQL",
            5672: "RabbitMQ",
            9092: "Kafka",
            2181: "Zookeeper",
            9411: "Zipkin"
        }
        return services.get(port, "Unknown Service")
    
    def _test_service_auth(self, target: str, 
                           jwt_secret: Optional[str]) -> List[Dict[str, Any]]:
        """Teste l'authentification entre services"""
        vulnerabilities = []
        
        test_endpoints = ['/internal', '/private', '/services', '/api/internal',
                         '/admin', '/manage', '/system', '/health/internal']
        
        for endpoint in test_endpoints:
            test_url = target.rstrip('/') + endpoint
            
            try:
                response = requests.get(test_url, timeout=self.config.timeout, 
                                       verify=False)
                self._random_delay()
                
                if response.status_code == 200:
                    vulnerabilities.append({
                        "type": "missing_service_auth",
                        "endpoint": endpoint,
                        "severity": "CRITICAL",
                        "details": f"Service interne accessible sans authentification"
                    })
                    console.print_warning(f"      ✓ Service interne sans auth: {endpoint}")
                    
            except Exception:
                continue
        
        # Test avec JWT forgé (si secret fourni)
        if jwt_secret:
            jwt_vulns = self._test_jwt_bypass(target, jwt_secret)
            vulnerabilities.extend(jwt_vulns)
        
        return vulnerabilities
    
    def _test_jwt_bypass(self, target: str, secret: str) -> List[Dict[str, Any]]:
        """Teste le contournement JWT entre services"""
        vulnerabilities = []
        
        import jwt
        import time
        
        # Créer un token JWT forgé
        payload = {
            "sub": "admin",
            "role": "admin",
            "exp": int(time.time()) + 3600,
            "iss": "microservice"
        }
        
        try:
            forged_token = jwt.encode(payload, secret, algorithm="HS256")
            headers = {'Authorization': f'Bearer {forged_token}'}
            
            response = requests.get(target, headers=headers, timeout=self.config.timeout,
                                   verify=False)
            
            if response.status_code == 200:
                vulnerabilities.append({
                    "type": "jwt_bypass",
                    "severity": "CRITICAL",
                    "details": "Contournement JWT possible avec secret connu"
                })
                console.print_warning(f"      ✓ JWT bypass possible")
                
        except Exception:
            pass
        
        return vulnerabilities
    
    def _test_configuration(self, target: str) -> List[Dict[str, Any]]:
        """Teste les mauvaises configurations"""
        vulnerabilities = []
        
        config_files = [
            '/config.json', '/configuration.json', '/settings.json', '/appsettings.json',
            '/bootstrap.yml', '/application.yml', '/application.properties',
            '/env.json', '/.env', '/config.yml'
        ]
        
        for config in config_files:
            test_url = target.rstrip('/') + config
            
            try:
                response = requests.get(test_url, timeout=self.config.timeout, 
                                       verify=False)
                self._random_delay()
                
                if response.status_code == 200:
                    vulnerabilities.append({
                        "type": "config_exposed",
                        "file": config,
                        "severity": "CRITICAL",
                        "details": f"Fichier de configuration exposé: {config}"
                    })
                    console.print_warning(f"      ✓ Configuration exposée: {config}")
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _test_circuit_breaker(self, target: str) -> List[Dict[str, Any]]:
        """Teste les vulnérabilités de circuit breaker"""
        vulnerabilities = []
        
        # Endpoints Hystrix
        hystrix_endpoints = ['/hystrix', '/hystrix.stream', '/actuator/hystrix',
                            '/metrics/hystrix']
        
        for endpoint in hystrix_endpoints:
            test_url = target.rstrip('/') + endpoint
            
            try:
                response = requests.get(test_url, timeout=self.config.timeout, 
                                       verify=False)
                
                if response.status_code == 200:
                    vulnerabilities.append({
                        "type": "circuit_breaker_exposed",
                        "endpoint": endpoint,
                        "severity": "MEDIUM",
                        "details": f"Circuit breaker dashboard exposé: {endpoint}"
                    })
                    console.print_info(f"      ✓ Circuit breaker exposé: {endpoint}")
                    
            except Exception:
                continue
        
        return vulnerabilities
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des vulnérabilités"""
        return {
            "total": len(vulnerabilities),
            "stealth_mode": self.config.stealth_mode,
            "aggressive_mode": self.config.aggressive_mode,
            "by_type": {
                "service_discovery": len([v for v in vulnerabilities if v['type'] == 'service_discovery']),
                "actuator": len([v for v in vulnerabilities if v['type'] == 'spring_actuator']),
                "gateway_route": len([v for v in vulnerabilities if v['type'] == 'gateway_route']),
                "missing_auth": len([v for v in vulnerabilities if v['type'] == 'missing_service_auth']),
                "config_exposed": len([v for v in vulnerabilities if v['type'] == 'config_exposed']),
                "credentials_exposed": len([v for v in vulnerabilities if v['type'] == 'credentials_exposed']),
                "jwt_bypass": len([v for v in vulnerabilities if v['type'] == 'jwt_bypass'])
            },
            "critical": len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
            "high": len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
            "medium": len([v for v in vulnerabilities if v['severity'] == 'MEDIUM'])
        }


# Point d'entrée pour tests
if __name__ == "__main__":
    ms = MicroservicesAttack()
    
    # Test mode standard
    print("=== Mode Standard ===")
    results = ms.scan("https://example.com")
    print(f"Vulnérabilités microservices: {results['count']}")
    
    # Test mode furtif
    print("\n=== Mode Furtif ===")
    ms.set_stealth_mode(True)
    results = ms.scan("https://example.com")
    print(f"Vulnérabilités microservices (stealth): {results['count']}")
    
    # Test mode agressif
    print("\n=== Mode Agressif ===")
    ms.set_aggressive_mode(True)
    results = ms.scan("https://example.com", jwt_secret="test_secret")
    print(f"Vulnérabilités microservices (aggressive): {results['count']}")