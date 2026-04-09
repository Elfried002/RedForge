#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Web Flask pour RedForge
Interface graphique moderne pour la plateforme de pentest
Avec support multi-attaques, mode furtif et opérations APT
"""

import os
import json
import threading
import time
import random
import hashlib
from datetime import datetime, timedelta
from queue import Queue
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Import des modules RedForge
from src.core.orchestrator import RedForgeOrchestrator
from src.core.attack_chainer import AttackChainer
from src.core.session_manager import SessionManager
from src.attacks import AttackOrchestrator

# Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('REDFORGE_SECRET_KEY', 'redforge_secret_key_change_in_production')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Extensions
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Types de données
@dataclass
class AttackTask:
    """Représente une tâche d'attaque"""
    id: str
    target: str
    attacks: List[Dict[str, Any]]
    stealth_mode: bool
    operation_type: str  # 'single', 'multiple', 'apt'
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: int = 0
    current_attack: Optional[str] = None
    results: List[Dict] = None
    error: Optional[str] = None

@dataclass
class StealthConfig:
    """Configuration du mode furtif"""
    delay_between_requests: float = 1.0
    jitter: float = 0.3
    random_user_agents: bool = True
    rotate_proxies: bool = False
    proxy_list: List[str] = None
    use_tor: bool = False
    random_delays: bool = True
    max_concurrent_attacks: int = 1
    mimic_human_behavior: bool = True
    
    def get_delay(self) -> float:
        """Retourne un délai aléatoire pour les opérations furtives"""
        if not self.random_delays:
            return self.delay_between_requests
        jitter_range = self.delay_between_requests * self.jitter
        return self.delay_between_requests + random.uniform(-jitter_range, jitter_range)

@dataclass
class APTConfig:
    """Configuration pour les opérations APT"""
    name: str
    description: str
    phases: List[Dict[str, Any]]
    persistence: Dict[str, Any]
    evasion: Dict[str, Any]
    exfiltration: Dict[str, Any]
    cleanup: bool = True
    reporting: Dict[str, Any] = None

# Stockage des tâches en cours
active_tasks: Dict[str, AttackTask] = {}
task_results = {}
task_queue = Queue()
stealth_configs = {}
apt_operations = {}

# Modes furtifs prédéfinis
STEALTH_PROFILES = {
    'low': StealthConfig(delay_between_requests=0.5, jitter=0.1, max_concurrent_attacks=3),
    'medium': StealthConfig(delay_between_requests=1.5, jitter=0.3, max_concurrent_attacks=2),
    'high': StealthConfig(delay_between_requests=3.0, jitter=0.5, max_concurrent_attacks=1, use_tor=True),
    'paranoid': StealthConfig(delay_between_requests=5.0, jitter=0.7, max_concurrent_attacks=1, 
                              use_tor=True, rotate_proxies=True, mimic_human_behavior=True)
}

# Opérations APT prédéfinies
PREDEFINED_APT_OPERATIONS = {
    'recon_to_exfil': APTConfig(
        name="Reconnaissance à Exfiltration",
        description="Opération APT complète de la reconnaissance à l'exfiltration de données",
        phases=[
            {"name": "reconnaissance", "attacks": ["port_scan", "service_enum", "directory_bruteforce"]},
            {"name": "initial_access", "attacks": ["sql_injection", "xss", "file_upload"]},
            {"name": "persistence", "attacks": ["backdoor", "scheduled_task", "registry_persistence"]},
            {"name": "privilege_escalation", "attacks": ["sudo_abuse", "kernel_exploit", "win_priv_esc"]},
            {"name": "lateral_movement", "attacks": ["ssh_pivot", "smb_exec", "wmi_exec"]},
            {"name": "data_exfiltration", "attacks": ["dns_exfil", "http_exfil", "custom_protocol"]}
        ],
        persistence={"type": "registry", "location": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"},
        evasion={"disable_logging": True, "clear_events": True, "use_living_off_land": True},
        exfiltration={"method": "dns_tunneling", "server": "c2.example.com", "chunk_size": 512},
        reporting={"include_iocs": True, "include_ttps": True}
    ),
    'web_app_compromise': APTConfig(
        name="Compromission d'Application Web",
        description="Ciblage spécifique d'applications web avec persistance",
        phases=[
            {"name": "footprinting", "attacks": ["whatweb", "waf_detection", "tech_stack"]},
            {"name": "vulnerability_scan", "attacks": ["sql_injection", "xss", "csrf", "ssrf"]},
            {"name": "exploitation", "attacks": ["sqli_union", "xss_persistent", "rce"]},
            {"name": "post_exploit", "attacks": ["web_shell", "reverse_shell", "database_dump"]}
        ],
        persistence={"type": "web_shell", "location": "/uploads/.shell.php"},
        evasion={"encode_payloads": True, "slow_loris_style": True},
        exfiltration={"method": "http", "use_encryption": True},
        cleanup=True
    )
}

def create_app():
    """Crée et configure l'application Flask"""
    return app

@app.route('/')
def index():
    """Page d'accueil"""
    resp = make_response(render_template('index.html'))
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    return resp

@app.route('/dashboard')
def dashboard():
    """Tableau de bord principal"""
    return render_template('dashboard.html')

@app.route('/attacks')
def attacks_page():
    """Page de gestion des attaques"""
    return render_template('attacks.html')

@app.route('/apt')
def apt_page():
    """Page des opérations APT"""
    return render_template('apt.html')

@app.route('/stealth')
def stealth_page():
    """Page de configuration furtive"""
    return render_template('stealth.html')

@app.route('/reports')
def reports_page():
    """Page des rapports"""
    return render_template('reports.html')

@app.route('/settings')
def settings_page():
    """Page des paramètres"""
    return render_template('settings.html')

@app.route('/help')
def help_page():
    """Page d'aide"""
    return render_template('help.html')

# API pour les attaques multiples
@app.route('/api/multi-attack', methods=['POST'])
def api_multi_attack():
    """Lance plusieurs attaques simultanément ou séquentiellement"""
    data = request.get_json()
    target = data.get('target')
    attacks = data.get('attacks', [])
    stealth_level = data.get('stealth_level', 'medium')
    execution_mode = data.get('execution_mode', 'sequential')  # 'sequential' or 'parallel'
    
    if not target or not attacks:
        return jsonify({'error': 'Cible et attaques requises'}), 400
    
    # Créer la configuration furtive
    stealth_config = STEALTH_PROFILES.get(stealth_level, STEALTH_PROFILES['medium'])
    
    # Générer un ID de tâche
    task_id = hashlib.md5(f"{target}_{datetime.now().timestamp()}".encode()).hexdigest()
    
    # Créer la tâche
    task = AttackTask(
        id=task_id,
        target=target,
        attacks=attacks,
        stealth_mode=True,
        operation_type='multiple',
        status='pending',
        created_at=datetime.now().isoformat(),
        results=[]
    )
    
    active_tasks[task_id] = task
    stealth_configs[task_id] = stealth_config
    
    # Lancer l'exécution dans un thread
    thread = threading.Thread(
        target=_run_multi_attacks,
        args=(task_id, target, attacks, stealth_config, execution_mode)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'task_id': task_id,
        'status': 'started',
        'stealth_level': stealth_level,
        'execution_mode': execution_mode
    })

# API pour les opérations APT
@app.route('/api/apt/operations', methods=['GET'])
def api_apt_operations():
    """Liste les opérations APT disponibles"""
    return jsonify({
        'predefined': list(PREDEFINED_APT_OPERATIONS.keys()),
        'custom': list(apt_operations.keys())
    })

@app.route('/api/apt/operation/<operation_id>', methods=['GET'])
def api_apt_get_operation(operation_id):
    """Récupère une opération APT spécifique"""
    if operation_id in PREDEFINED_APT_OPERATIONS:
        op = PREDEFINED_APT_OPERATIONS[operation_id]
        return jsonify(asdict(op))
    elif operation_id in apt_operations:
        return jsonify(apt_operations[operation_id])
    else:
        return jsonify({'error': 'Opération non trouvée'}), 404

@app.route('/api/apt/execute', methods=['POST'])
def api_apt_execute():
    """Exécute une opération APT complète"""
    data = request.get_json()
    target = data.get('target')
    operation_id = data.get('operation_id')
    stealth_level = data.get('stealth_level', 'high')
    custom_phases = data.get('custom_phases', None)
    
    if not target or not operation_id:
        return jsonify({'error': 'Cible et opération requises'}), 400
    
    # Récupérer la configuration APT
    if operation_id in PREDEFINED_APT_OPERATIONS:
        apt_config = PREDEFINED_APT_OPERATIONS[operation_id]
    elif operation_id in apt_operations:
        apt_config = apt_operations[operation_id]
    else:
        return jsonify({'error': 'Opération APT non trouvée'}), 404
    
    # Surcharger les phases si fournies
    if custom_phases:
        apt_config.phases = custom_phases
    
    # Configuration furtive
    stealth_config = STEALTH_PROFILES.get(stealth_level, STEALTH_PROFILES['high'])
    
    # Générer un ID de tâche
    task_id = hashlib.md5(f"apt_{target}_{operation_id}_{datetime.now().timestamp()}".encode()).hexdigest()
    
    # Créer la tâche
    task = AttackTask(
        id=task_id,
        target=target,
        attacks=[],  # Les attaques sont gérées par phases
        stealth_mode=True,
        operation_type='apt',
        status='pending',
        created_at=datetime.now().isoformat(),
        results=[]
    )
    
    active_tasks[task_id] = task
    stealth_configs[task_id] = stealth_config
    
    # Lancer l'opération APT
    thread = threading.Thread(
        target=_run_apt_operation,
        args=(task_id, target, apt_config, stealth_config)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'task_id': task_id,
        'status': 'started',
        'operation': operation_id,
        'stealth_level': stealth_level,
        'total_phases': len(apt_config.phases)
    })

@app.route('/api/apt/custom', methods=['POST'])
def api_apt_create_custom():
    """Crée une opération APT personnalisée"""
    data = request.get_json()
    operation_name = data.get('name')
    description = data.get('description')
    phases = data.get('phases', [])
    persistence = data.get('persistence', {})
    evasion = data.get('evasion', {})
    exfiltration = data.get('exfiltration', {})
    
    if not operation_name or not phases:
        return jsonify({'error': 'Nom et phases requis'}), 400
    
    custom_apt = APTConfig(
        name=operation_name,
        description=description,
        phases=phases,
        persistence=persistence,
        evasion=evasion,
        exfiltration=exfiltration,
        cleanup=data.get('cleanup', True),
        reporting=data.get('reporting', {})
    )
    
    apt_operations[operation_name] = asdict(custom_apt)
    
    return jsonify({'success': True, 'operation_id': operation_name})

# API pour le mode furtif
@app.route('/api/stealth/profiles', methods=['GET'])
def api_stealth_profiles():
    """Liste les profils furtifs disponibles"""
    return jsonify({
        'profiles': list(STEALTH_PROFILES.keys()),
        'current_configs': {k: asdict(v) for k, v in STEALTH_PROFILES.items()}
    })

@app.route('/api/stealth/custom', methods=['POST'])
def api_stealth_custom():
    """Crée une configuration furtive personnalisée"""
    data = request.get_json()
    
    custom_config = StealthConfig(
        delay_between_requests=data.get('delay_between_requests', 1.0),
        jitter=data.get('jitter', 0.3),
        random_user_agents=data.get('random_user_agents', True),
        rotate_proxies=data.get('rotate_proxies', False),
        proxy_list=data.get('proxy_list', []),
        use_tor=data.get('use_tor', False),
        random_delays=data.get('random_delays', True),
        max_concurrent_attacks=data.get('max_concurrent_attacks', 1),
        mimic_human_behavior=data.get('mimic_human_behavior', True)
    )
    
    profile_id = data.get('profile_id', 'custom_' + hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8])
    STEALTH_PROFILES[profile_id] = custom_config
    
    return jsonify({'success': True, 'profile_id': profile_id, 'config': asdict(custom_config)})

@app.route('/api/stealth/test', methods=['POST'])
def api_stealth_test():
    """Teste la configuration furtive"""
    data = request.get_json()
    target = data.get('target')
    stealth_config = data.get('config', {})
    
    if not target:
        return jsonify({'error': 'Cible requise'}), 400
    
    # Simuler un test furtif
    results = {
        'test_id': hashlib.md5(f"{target}_{datetime.now().timestamp()}".encode()).hexdigest(),
        'target': target,
        'delays_tested': [],
        'success_rate': 0,
        'detection_risk': 'unknown',
        'recommendations': []
    }
    
    # Analyser la configuration
    config = StealthConfig(**stealth_config) if stealth_config else STEALTH_PROFILES['medium']
    
    # Simuler quelques délais
    for _ in range(5):
        results['delays_tested'].append(config.get_delay())
    
    # Évaluer le risque de détection
    if config.delay_between_requests < 0.5:
        results['detection_risk'] = 'high'
        results['recommendations'].append("Augmentez les délais entre les requêtes")
    elif config.delay_between_requests < 1.5:
        results['detection_risk'] = 'medium'
    else:
        results['detection_risk'] = 'low'
    
    if config.use_tor:
        results['success_rate'] = 85
        results['recommendations'].append("Utilisez des proxies additionnels pour plus de fiabilité")
    else:
        results['success_rate'] = 95
    
    if config.max_concurrent_attacks > 2:
        results['recommendations'].append("Réduisez les attaques concurrentes pour un meilleur camouflage")
    
    return jsonify(results)

# Fonctions d'exécution améliorées
def _run_multi_attacks(task_id, target, attacks, stealth_config, execution_mode):
    """Exécute de multiples attaques avec mode furtif"""
    task = active_tasks.get(task_id)
    if not task:
        return
    
    task.status = 'running'
    task.started_at = datetime.now().isoformat()
    
    results = []
    total_attacks = len(attacks)
    
    for idx, attack in enumerate(attacks):
        attack_category = attack.get('category')
        attack_type = attack.get('type')
        options = attack.get('options', {})
        
        if not attack_category or not attack_type:
            continue
        
        task.current_attack = f"{attack_category}/{attack_type}"
        task.progress = int((idx / total_attacks) * 100)
        
        # Appliquer les délais furtifs
        if stealth_config.mimic_human_behavior:
            time.sleep(stealth_config.get_delay())
        
        # Émettre la progression
        socketio.emit('attack_progress', {
            'task_id': task_id,
            'current_attack': task.current_attack,
            'progress': task.progress,
            'remaining': total_attacks - idx - 1
        })
        
        try:
            # Exécuter l'attaque
            orchestrator = AttackOrchestrator(target)
            
            # Appliquer les en-têtes furtifs si nécessaire
            if stealth_config.random_user_agents:
                options['user_agent'] = _get_random_user_agent()
            
            result = orchestrator.run_specific_attack(attack_category, attack_type, **options)
            
            results.append({
                'attack': f"{attack_category}/{attack_type}",
                'success': True,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            results.append({
                'attack': f"{attack_category}/{attack_type}",
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        
        # Mode parallèle non implémenté pour simplifier
        if execution_mode == 'parallel' and idx < total_attacks - 1:
            # Dans un vrai scénario, on utiliserait ThreadPoolExecutor
            pass
    
    task.results = results
    task.status = 'completed'
    task.completed_at = datetime.now().isoformat()
    task.progress = 100
    
    task_results[task_id] = {
        'target': target,
        'attacks': attacks,
        'results': results,
        'stealth_config': asdict(stealth_config),
        'completed_at': task.completed_at
    }
    
    # Nettoyer
    if task_id in stealth_configs:
        del stealth_configs[task_id]
    
    socketio.emit('multi_attack_completed', {
        'task_id': task_id,
        'total_attacks': total_attacks,
        'successful': sum(1 for r in results if r['success']),
        'failed': sum(1 for r in results if not r['success'])
    })

def _run_apt_operation(task_id, target, apt_config, stealth_config):
    """Exécute une opération APT complète"""
    task = active_tasks.get(task_id)
    if not task:
        return
    
    task.status = 'running'
    task.started_at = datetime.now().isoformat()
    
    phase_results = []
    total_phases = len(apt_config.phases)
    
    socketio.emit('apt_started', {
        'task_id': task_id,
        'operation_name': apt_config.name,
        'total_phases': total_phases,
        'stealth_level': 'high'  # Par défaut pour APT
    })
    
    for idx, phase in enumerate(apt_config.phases):
        phase_name = phase.get('name')
        attacks = phase.get('attacks', [])
        
        task.current_attack = f"Phase {idx+1}/{total_phases}: {phase_name}"
        task.progress = int((idx / total_phases) * 100)
        
        socketio.emit('apt_phase_start', {
            'task_id': task_id,
            'phase': phase_name,
            'phase_number': idx + 1,
            'total_phases': total_phases,
            'attacks_count': len(attacks)
        })
        
        phase_result = {
            'phase': phase_name,
            'attacks': [],
            'started_at': datetime.now().isoformat()
        }
        
        # Exécuter les attaques de la phase
        for attack_type in attacks:
            # Délai furtif
            time.sleep(stealth_config.get_delay())
            
            try:
                # Simuler l'exécution de l'attaque (à adapter avec vos modules réels)
                orchestrator = AttackOrchestrator(target)
                
                # Appliquer les techniques d'évasion APT
                if apt_config.evasion.get('encode_payloads'):
                    # Encoder les payloads
                    pass
                
                if apt_config.evasion.get('disable_logging'):
                    # Désactiver le logging
                    pass
                
                result = orchestrator.run_specific_attack(phase_name, attack_type)
                
                phase_result['attacks'].append({
                    'type': attack_type,
                    'success': True,
                    'result': result
                })
                
                socketio.emit('apt_attack_complete', {
                    'task_id': task_id,
                    'phase': phase_name,
                    'attack': attack_type,
                    'success': True
                })
                
            except Exception as e:
                phase_result['attacks'].append({
                    'type': attack_type,
                    'success': False,
                    'error': str(e)
                })
                
                socketio.emit('apt_attack_complete', {
                    'task_id': task_id,
                    'phase': phase_name,
                    'attack': attack_type,
                    'success': False,
                    'error': str(e)
                })
        
        phase_result['completed_at'] = datetime.now().isoformat()
        phase_result['success_rate'] = sum(1 for a in phase_result['attacks'] if a['success']) / len(attacks) * 100
        phase_results.append(phase_result)
        
        socketio.emit('apt_phase_complete', {
            'task_id': task_id,
            'phase': phase_name,
            'success_rate': phase_result['success_rate']
        })
        
        # Délai entre les phases
        time.sleep(stealth_config.get_delay() * 3)
    
    # Nettoyage post-opération
    if apt_config.cleanup:
        socketio.emit('apt_cleanup', {'task_id': task_id})
        # Implémenter le nettoyage ici
        time.sleep(2)
    
    task.results = phase_results
    task.status = 'completed'
    task.completed_at = datetime.now().isoformat()
    task.progress = 100
    
    # Sauvegarder les résultats
    task_results[task_id] = {
        'target': target,
        'operation': apt_config.name,
        'phases': phase_results,
        'persistence': apt_config.persistence,
        'exfiltration': apt_config.exfiltration,
        'stealth_config': asdict(stealth_config),
        'completed_at': task.completed_at
    }
    
    socketio.emit('apt_completed', {
        'task_id': task_id,
        'total_phases': total_phases,
        'overall_success': sum(p['success_rate'] for p in phase_results) / total_phases
    })

def _get_random_user_agent() -> str:
    """Retourne un user-agent aléatoire"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
    ]
    return random.choice(user_agents)

# Routes existantes conservées et améliorées
@app.route('/api/targets', methods=['GET', 'POST', 'DELETE'])
def api_targets():
    """API de gestion des cibles avec validation améliorée"""
    if request.method == 'GET':
        targets = session.get('targets', [])
        return jsonify({'targets': targets})
    
    elif request.method == 'POST':
        data = request.get_json()
        target = data.get('target')
        
        if not target:
            return jsonify({'error': 'Cible requise'}), 400
        
        # Validation basique de la cible
        if not target.replace('.', '').replace(':', '').replace('/', '').isalnum():
            return jsonify({'error': 'Format de cible invalide'}), 400
        
        targets = session.get('targets', [])
        if target not in targets:
            targets.append(target)
            session['targets'] = targets
        
        return jsonify({'success': True, 'target': target})
    
    elif request.method == 'DELETE':
        data = request.get_json()
        target = data.get('target')
        
        targets = session.get('targets', [])
        if target in targets:
            targets.remove(target)
            session['targets'] = targets
        
        return jsonify({'success': True})

@app.route('/api/task/<task_id>', methods=['GET'])
def api_task_status(task_id):
    """Récupère le statut d'une tâche avec plus de détails"""
    if task_id in active_tasks:
        task = active_tasks[task_id]
        return jsonify({
            'task_id': task_id,
            'status': task.status,
            'target': task.target,
            'operation_type': task.operation_type,
            'progress': task.progress,
            'current_attack': task.current_attack,
            'started_at': task.started_at,
            'created_at': task.created_at
        })
    elif task_id in task_results:
        return jsonify({
            'task_id': task_id,
            'status': 'completed',
            'results': task_results[task_id]
        })
    else:
        return jsonify({'error': 'Tâche non trouvée'}), 404

@app.route('/api/active-tasks', methods=['GET'])
def api_active_tasks():
    """Liste toutes les tâches actives"""
    tasks = []
    for task_id, task in active_tasks.items():
        tasks.append({
            'task_id': task_id,
            'target': task.target,
            'status': task.status,
            'operation_type': task.operation_type,
            'progress': task.progress,
            'started_at': task.started_at
        })
    return jsonify({'active_tasks': tasks})

# WebSocket events améliorés
@socketio.on('connect')
def handle_connect():
    print(f"Client connecté: {request.sid}")
    emit('connected', {'message': 'Connecté à RedForge', 'timestamp': datetime.now().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client déconnecté: {request.sid}")

@socketio.on('subscribe_task')
def handle_subscribe_task(data):
    """S'abonner aux mises à jour d'une tâche"""
    task_id = data.get('task_id')
    if task_id:
        join_room(task_id)
        emit('subscribed', {'task_id': task_id})

# Point d'entrée
if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    
    print("🔴 RedForge Web Interface démarrée")
    print(f"📍 Interface disponible sur http://localhost:5000")
    print(f"🛡️ Mode furtif disponible avec {len(STEALTH_PROFILES)} profils")
    print(f"🎯 {len(PREDEFINED_APT_OPERATIONS)} opérations APT prédéfinies")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)