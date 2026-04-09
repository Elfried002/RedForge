#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Graphique de RedForge
Utilise Flask pour le serveur web avec intégration backend complète
Version APT avec support furtif et interface moderne
"""

import sys
import os
import json
import webbrowser
import threading
import subprocess
import time
import queue
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from src.core.orchestrator import RedForgeOrchestrator
from src.core.config import RedForgeConfig
from src.core.stealth_engine import StealthEngine
from src.core.apt_controller import APTController


class RedForgeGUI:
    """Interface graphique via Flask avec intégration backend complète"""
    
    def __init__(self):
        self.port = 5000
        self.host = "127.0.0.1"
        self.app = None
        self.socketio = None
        self.current_task = None
        self.task_results = {}
        self.task_queue = queue.Queue()
        self.stealth_engine = StealthEngine()
        self.apt_controller = APTController()
        self.scan_history = []
        
    def run(self):
        """Lance l'interface graphique"""
        print("=" * 60)
        print("🔴 Lancement de l'interface graphique RedForge")
        print("=" * 60)
        print(f"🌐 Interface disponible sur : http://{self.host}:{self.port}")
        print("⚠️  Ne fermez pas ce terminal")
        print("👉 Appuyez sur Ctrl+C pour arrêter\n")
        
        try:
            self._start_flask_server()
        except KeyboardInterrupt:
            print("\n✅ Arrêt de l'interface graphique")
        except ImportError as e:
            print(f"❌ Module manquant: {e}")
            print("👉 Installez les dépendances: pip install flask flask-socketio flask-cors")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            sys.exit(1)
    
    def _start_flask_server(self):
        """Démarre le serveur Flask complet"""
        from flask import Flask, render_template_string, request, jsonify, session
        from flask_socketio import SocketIO, emit
        from flask_cors import CORS
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'redforge_secret_key_change_me_2024'
        CORS(app)
        socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
        
        # Stockage des tâches en cours
        active_tasks = {}
        task_results = {}
        terminal_history = []
        
        # ========================================
        # TEMPLATES HTML INTÉGRÉS
        # ========================================
        
        BASE_TEMPLATE = '''
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RedForge - Plateforme de Pentest APT</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
                    color: #fff;
                    min-height: 100vh;
                }
                .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
                
                /* Header */
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px 0;
                    border-bottom: 1px solid rgba(255,255,255,0.1);
                    margin-bottom: 30px;
                    flex-wrap: wrap;
                    gap: 15px;
                }
                .logo { font-size: 32px; font-weight: bold; }
                .logo-red { color: #ff4444; }
                .logo-white { color: #fff; }
                .status {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 8px 15px;
                    background: rgba(0,0,0,0.3);
                    border-radius: 20px;
                    font-size: 14px;
                }
                .status-dot {
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    background: #4caf50;
                    animation: pulse 2s infinite;
                }
                .status-dot.apt { background: #ff4444; }
                .status-dot.stealth { background: #ff9800; }
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
                
                /* Mode selector */
                .mode-selector {
                    display: flex;
                    gap: 10px;
                    background: rgba(0,0,0,0.3);
                    padding: 5px;
                    border-radius: 25px;
                }
                .mode-btn {
                    padding: 8px 20px;
                    border: none;
                    border-radius: 20px;
                    cursor: pointer;
                    background: transparent;
                    color: #fff;
                    transition: all 0.3s;
                }
                .mode-btn.active {
                    background: #ff4444;
                    color: white;
                }
                .mode-btn.apt.active { background: #ff4444; }
                .mode-btn.stealth.active { background: #ff9800; }
                
                /* Grid */
                .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
                .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
                .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
                
                /* Cards */
                .card {
                    background: rgba(255,255,255,0.05);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 20px;
                    border: 1px solid rgba(255,255,255,0.1);
                    transition: transform 0.3s, box-shadow 0.3s;
                }
                .card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }
                .card-title {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid rgba(255,255,255,0.1);
                    color: #ff4444;
                }
                
                /* Stats */
                .stat-card {
                    text-align: center;
                    padding: 20px;
                }
                .stat-value { font-size: 36px; font-weight: bold; color: #ff4444; }
                .stat-label { font-size: 14px; opacity: 0.8; margin-top: 5px; }
                
                /* Forms */
                .form-group { margin-bottom: 15px; }
                label { display: block; margin-bottom: 5px; font-size: 14px; opacity: 0.8; }
                input, select, textarea {
                    width: 100%;
                    padding: 12px;
                    background: rgba(0,0,0,0.3);
                    border: 1px solid rgba(255,255,255,0.2);
                    border-radius: 8px;
                    color: #fff;
                    font-size: 14px;
                    transition: all 0.3s;
                }
                input:focus, select:focus, textarea:focus {
                    outline: none;
                    border-color: #ff4444;
                    box-shadow: 0 0 10px rgba(255,68,68,0.3);
                }
                
                /* Buttons */
                .btn {
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: bold;
                    transition: all 0.3s;
                    margin: 5px;
                }
                .btn-primary {
                    background: linear-gradient(135deg, #ff4444, #cc0000);
                    color: white;
                }
                .btn-primary:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 20px rgba(255,68,68,0.4);
                }
                .btn-secondary {
                    background: rgba(255,255,255,0.2);
                    color: white;
                }
                .btn-secondary:hover {
                    background: rgba(255,255,255,0.3);
                }
                .btn-success {
                    background: linear-gradient(135deg, #4caf50, #2e7d32);
                    color: white;
                }
                
                /* Progress bar */
                .progress {
                    height: 8px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 4px;
                    overflow: hidden;
                    margin: 10px 0;
                }
                .progress-bar {
                    height: 100%;
                    background: linear-gradient(90deg, #ff4444, #ff8888);
                    width: 0%;
                    transition: width 0.3s;
                }
                
                /* Terminal */
                .terminal {
                    background: #0a0a0a;
                    border-radius: 10px;
                    padding: 15px;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                    color: #00ff00;
                    height: 400px;
                    overflow-y: auto;
                }
                .terminal-line { margin-bottom: 5px; font-family: monospace; }
                .terminal-prompt { color: #00ff00; }
                .terminal-error { color: #ff4444; }
                .terminal-warning { color: #ff9800; }
                
                /* Alert */
                .alert {
                    padding: 12px 20px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                }
                .alert-success { background: rgba(76,175,80,0.2); border-left: 4px solid #4caf50; }
                .alert-danger { background: rgba(244,67,54,0.2); border-left: 4px solid #f44336; }
                .alert-warning { background: rgba(255,152,0,0.2); border-left: 4px solid #ff9800; }
                .alert-info { background: rgba(33,150,243,0.2); border-left: 4px solid #2196f3; }
                
                /* Tabs */
                .tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); flex-wrap: wrap; }
                .tab {
                    padding: 10px 20px;
                    cursor: pointer;
                    border-bottom: 2px solid transparent;
                    transition: all 0.3s;
                }
                .tab:hover { color: #ff4444; }
                .tab.active { color: #ff4444; border-bottom-color: #ff4444; }
                .tab-content { display: none; }
                .tab-content.active { display: block; }
                
                /* Vulnerabilities */
                .vuln-item {
                    padding: 12px;
                    margin: 10px 0;
                    background: rgba(0,0,0,0.2);
                    border-radius: 8px;
                    border-left: 4px solid;
                }
                .vuln-critical { border-left-color: #7b1fa2; }
                .vuln-high { border-left-color: #f44336; }
                .vuln-medium { border-left-color: #ff9800; }
                .vuln-low { border-left-color: #4caf50; }
                .vuln-info { border-left-color: #2196f3; }
                
                /* Responsive */
                @media (max-width: 768px) {
                    .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
                    .container { padding: 10px; }
                    .header { flex-direction: column; text-align: center; }
                }
                
                /* Scrollbar */
                ::-webkit-scrollbar { width: 8px; height: 8px; }
                ::-webkit-scrollbar-track { background: rgba(255,255,255,0.1); border-radius: 4px; }
                ::-webkit-scrollbar-thumb { background: #ff4444; border-radius: 4px; }
                ::-webkit-scrollbar-thumb:hover { background: #cc0000; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">
                        <span class="logo-red">🔴 Red</span><span class="logo-white">Forge</span>
                    </div>
                    <div class="mode-selector">
                        <button class="mode-btn standard" data-mode="standard">🎭 Standard</button>
                        <button class="mode-btn stealth" data-mode="stealth">🕵️ Stealth</button>
                        <button class="mode-btn apt" data-mode="apt">🎯 APT</button>
                    </div>
                    <div class="status">
                        <div class="status-dot" id="status-dot"></div>
                        <span id="status-text">Connecté</span>
                    </div>
                </div>
                
                <div class="grid-4" id="stats-container">
                    <div class="card stat-card"><div class="stat-value" id="stat-targets">0</div><div class="stat-label">Cibles</div></div>
                    <div class="card stat-card"><div class="stat-value" id="stat-attacks">0</div><div class="stat-label">Attaques</div></div>
                    <div class="card stat-card"><div class="stat-value" id="stat-vulns">0</div><div class="stat-label">Vulnérabilités</div></div>
                    <div class="card stat-card"><div class="stat-value" id="stat-sessions">0</div><div class="stat-label">Sessions</div></div>
                </div>
                
                <div class="card">
                    <div class="card-title">🎯 Configuration de la cible</div>
                    <div class="form-group">
                        <input type="text" id="target" placeholder="URL ou IP cible (ex: example.com)">
                    </div>
                    <div class="form-group">
                        <select id="phase">
                            <option value="footprint">Phase 1: Reconnaissance</option>
                            <option value="analysis">Phase 2: Analyse approfondie</option>
                            <option value="scan">Phase 3: Scan vulnérabilités</option>
                            <option value="exploit">Phase 4: Exploitation</option>
                            <option value="all">⚡ Toutes les phases</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <select id="stealth-level">
                            <option value="low">Niveau furtivité: Faible</option>
                            <option value="medium" selected>Niveau furtivité: Moyen</option>
                            <option value="high">Niveau furtivité: Élevé</option>
                            <option value="extreme">Niveau furtivité: Extrême (APT)</option>
                        </select>
                    </div>
                    <button class="btn btn-primary" onclick="startScan()">🚀 Lancer l'attaque</button>
                    <button class="btn btn-secondary" onclick="clearResults()">🗑️ Effacer</button>
                    <button class="btn btn-success" onclick="exportReport()">📄 Exporter rapport</button>
                </div>
                
                <div class="card">
                    <div class="card-title">📊 Progression</div>
                    <div class="progress"><div class="progress-bar" id="progress-bar"></div></div>
                    <div id="status-message">Prêt</div>
                    <div id="current-phase" style="font-size:12px; opacity:0.7; margin-top:5px;"></div>
                </div>
                
                <div class="tabs">
                    <div class="tab active" data-tab="results">📝 Résultats</div>
                    <div class="tab" data-tab="vulns">⚠️ Vulnérabilités</div>
                    <div class="tab" data-tab="terminal">💻 Terminal</div>
                    <div class="tab" data-tab="history">📜 Historique</div>
                    <div class="tab" data-tab="settings">⚙️ Configuration</div>
                </div>
                
                <div id="tab-results" class="tab-content active">
                    <div class="card">
                        <pre id="results" style="background:#0a0a0a; padding:15px; border-radius:10px; overflow-x:auto; height:400px; font-family:monospace; font-size:12px;">En attente d'action...</pre>
                    </div>
                </div>
                
                <div id="tab-vulns" class="tab-content">
                    <div class="card" id="vulns-container">
                        <p>Aucune vulnérabilité détectée</p>
                    </div>
                </div>
                
                <div id="tab-terminal" class="tab-content">
                    <div class="terminal" id="terminal">
                        <div class="terminal-line">$ RedForge Terminal v2.0.0</div>
                        <div class="terminal-line">$ Mode APT disponible</div>
                        <div class="terminal-line">$ Tapez 'help' pour la liste des commandes</div>
                    </div>
                    <div style="margin-top: 10px; display: flex; gap: 10px;">
                        <input type="text" id="terminal-input" style="flex:1;" placeholder="Entrez une commande...">
                        <button class="btn btn-secondary" onclick="sendCommand()">Exécuter</button>
                    </div>
                </div>
                
                <div id="tab-history" class="tab-content">
                    <div class="card">
                        <div id="history-list">
                            <p>Aucun historique</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-settings" class="tab-content">
                    <div class="card">
                        <div class="card-title">⚙️ Configuration</div>
                        <div class="form-group">
                            <label>Proxy HTTP</label>
                            <input type="text" id="proxy-http" placeholder="http://127.0.0.1:8080">
                        </div>
                        <div class="form-group">
                            <label>Délai minimum (secondes)</label>
                            <input type="number" id="delay-min" value="1" step="0.5">
                        </div>
                        <div class="form-group">
                            <label>Délai maximum (secondes)</label>
                            <input type="number" id="delay-max" value="5" step="0.5">
                        </div>
                        <button class="btn btn-primary" onclick="saveSettings()">💾 Sauvegarder</button>
                    </div>
                </div>
            </div>
            
            <script>
                let socket = null;
                let currentMode = 'standard';
                let scanHistory = [];
                
                function connectWebSocket() {
                    socket = new WebSocket('ws://' + window.location.hostname + ':' + window.location.port + '/socket.io/?EIO=4&transport=websocket');
                    socket.onopen = function() { console.log('WebSocket connecté'); };
                    socket.onmessage = function(event) { handleMessage(event.data); };
                    socket.onclose = function() { setTimeout(connectWebSocket, 3000); };
                }
                
                function handleMessage(data) {
                    try {
                        const msg = JSON.parse(data);
                        if (msg.type === 'progress') {
                            document.getElementById('progress-bar').style.width = msg.progress + '%';
                            document.getElementById('status-message').innerText = msg.message;
                            if (msg.phase) document.getElementById('current-phase').innerText = 'Phase: ' + msg.phase;
                        } else if (msg.type === 'result') {
                            const results = document.getElementById('results');
                            const newLine = msg.output + '\\n';
                            results.innerText = newLine + results.innerText;
                        } else if (msg.type === 'vulnerability') {
                            addVulnerability(msg.vulnerability);
                        } else if (msg.type === 'terminal') {
                            addTerminalLine(msg.line, msg.level || 'info');
                        }
                    } catch(e) {}
                }
                
                function addVulnerability(vuln) {
                    const container = document.getElementById('vulns-container');
                    if (container.querySelector('.no-vulns')) container.innerHTML = '';
                    const div = document.createElement('div');
                    div.className = 'vuln-item vuln-' + (vuln.severity || 'medium').toLowerCase();
                    div.innerHTML = '<strong>' + (vuln.type || 'Vulnérabilité') + '</strong><br>' + (vuln.details || 'Aucun détail') + '<br><small>' + new Date().toLocaleString() + '</small>';
                    container.insertBefore(div, container.firstChild);
                    document.getElementById('stat-vulns').innerText = parseInt(document.getElementById('stat-vulns').innerText || 0) + 1;
                }
                
                function addTerminalLine(line, level) {
                    const terminal = document.getElementById('terminal');
                    const className = level === 'error' ? 'terminal-error' : (level === 'warning' ? 'terminal-warning' : '');
                    terminal.innerHTML += '<div class="terminal-line ' + className + '">' + line + '</div>';
                    terminal.scrollTop = terminal.scrollHeight;
                }
                
                function startScan() {
                    const target = document.getElementById('target').value;
                    const phase = document.getElementById('phase').value;
                    const stealthLevel = document.getElementById('stealth-level').value;
                    if (!target) { alert('Veuillez entrer une cible'); return; }
                    
                    document.getElementById('results').innerText = 'Lancement du scan sur ' + target + '...\\nMode: ' + currentMode.toUpperCase() + '\\nFurtivité: ' + stealthLevel + '\\n';
                    document.getElementById('progress-bar').style.width = '0%';
                    document.getElementById('status-message').innerText = 'Scan en cours...';
                    
                    fetch('/api/scan', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            target: target, 
                            phase: phase, 
                            mode: currentMode,
                            stealth_level: stealthLevel
                        })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.task_id) { checkStatus(data.task_id); }
                        else if (data.error) { alert('Erreur: ' + data.error); }
                    });
                }
                
                function checkStatus(taskId) {
                    fetch('/api/task/' + taskId)
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === 'running') {
                                setTimeout(() => checkStatus(taskId), 2000);
                            } else if (data.status === 'completed') {
                                document.getElementById('progress-bar').style.width = '100%';
                                document.getElementById('status-message').innerText = 'Scan terminé !';
                                if (data.results) {
                                    document.getElementById('results').innerText = JSON.stringify(data.results, null, 2);
                                    if (data.results.vulnerabilities) {
                                        data.results.vulnerabilities.forEach(v => addVulnerability(v));
                                    }
                                    scanHistory.unshift({ target: document.getElementById('target').value, timestamp: new Date().toLocaleString(), results: data.results });
                                    updateHistory();
                                }
                            } else if (data.status === 'failed') {
                                document.getElementById('status-message').innerText = 'Erreur: ' + (data.error || 'Scan échoué');
                                addTerminalLine('Erreur: ' + (data.error || 'Scan échoué'), 'error');
                            }
                        });
                }
                
                function updateHistory() {
                    const container = document.getElementById('history-list');
                    if (scanHistory.length === 0) {
                        container.innerHTML = '<p>Aucun historique</p>';
                        return;
                    }
                    container.innerHTML = scanHistory.map(item => 
                        '<div class="alert alert-info" style="margin:10px 0; cursor:pointer;" onclick="loadHistoryResult(' + JSON.stringify(item).replace(/"/g, '&quot;') + ')">' +
                        '<strong>' + item.target + '</strong> - ' + item.timestamp +
                        '</div>'
                    ).join('');
                }
                
                function loadHistoryResult(item) {
                    document.getElementById('target').value = item.target;
                    document.getElementById('results').innerText = JSON.stringify(item.results, null, 2);
                    if (item.results.vulnerabilities) {
                        item.results.vulnerabilities.forEach(v => addVulnerability(v));
                    }
                }
                
                function clearResults() {
                    document.getElementById('results').innerText = 'En attente d\'action...';
                    document.getElementById('vulns-container').innerHTML = '<p>Aucune vulnérabilité détectée</p>';
                    document.getElementById('stat-vulns').innerText = '0';
                    document.getElementById('progress-bar').style.width = '0%';
                    document.getElementById('status-message').innerText = 'Prêt';
                }
                
                function exportReport() {
                    const target = document.getElementById('target').value;
                    if (!target) { alert('Aucune cible à exporter'); return; }
                    window.location.href = '/api/export?target=' + encodeURIComponent(target);
                }
                
                function sendCommand() {
                    const input = document.getElementById('terminal-input');
                    const cmd = input.value;
                    if (!cmd) return;
                    
                    addTerminalLine('$ ' + cmd);
                    input.value = '';
                    
                    fetch('/api/command', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command: cmd })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.output) {
                            data.output.split('\\n').forEach(line => {
                                if (line.trim()) addTerminalLine(line);
                            });
                        }
                    });
                }
                
                function saveSettings() {
                    const settings = {
                        proxy_http: document.getElementById('proxy-http').value,
                        delay_min: parseFloat(document.getElementById('delay-min').value),
                        delay_max: parseFloat(document.getElementById('delay-max').value)
                    };
                    fetch('/api/settings', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(settings)
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) { addTerminalLine('Configuration sauvegardée', 'success'); }
                        else { addTerminalLine('Erreur: ' + data.error, 'error'); }
                    });
                }
                
                // Mode selector
                document.querySelectorAll('.mode-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
                        this.classList.add('active');
                        currentMode = this.dataset.mode;
                        const dot = document.getElementById('status-dot');
                        if (currentMode === 'apt') { dot.classList.add('apt'); dot.classList.remove('stealth'); }
                        else if (currentMode === 'stealth') { dot.classList.add('stealth'); dot.classList.remove('apt'); }
                        else { dot.classList.remove('apt', 'stealth'); }
                        addTerminalLine('Mode changé: ' + currentMode.toUpperCase());
                    });
                });
                
                // Tabs
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.addEventListener('click', function() {
                        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                        this.classList.add('active');
                        document.getElementById('tab-' + this.dataset.tab).classList.add('active');
                    });
                });
                
                // Enter dans le terminal
                document.getElementById('terminal-input').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') sendCommand();
                });
                
                // Load settings
                fetch('/api/settings')
                    .then(res => res.json())
                    .then(data => {
                        if (data.proxy_http) document.getElementById('proxy-http').value = data.proxy_http;
                        if (data.delay_min) document.getElementById('delay-min').value = data.delay_min;
                        if (data.delay_max) document.getElementById('delay-max').value = data.delay_max;
                    });
                
                connectWebSocket();
                addTerminalLine('RedForge GUI prêt - Mode ' + currentMode.toUpperCase());
            </script>
        </body>
        </html>
        '''
        
        # ========================================
        # ROUTES API
        # ========================================
        
        @app.route('/')
        def index():
            return render_template_string(BASE_TEMPLATE)
        
        @app.route('/api/scan', methods=['POST'])
        def api_scan():
            data = request.get_json()
            target = data.get('target')
            phase = data.get('phase', 'all')
            mode = data.get('mode', 'standard')
            stealth_level = data.get('stealth_level', 'medium')
            
            if not target:
                return jsonify({'error': 'Cible requise'}), 400
            
            import uuid
            task_id = str(uuid.uuid4())
            
            def run_scan():
                try:
                    active_tasks[task_id] = {'status': 'running'}
                    
                    # Configurer le mode
                    if mode == 'apt':
                        stealth_config = {'enabled': True, 'apt_mode': True, 'delay_min': 5, 'delay_max': 15}
                    elif mode == 'stealth':
                        stealth_config = {'enabled': True, 'apt_mode': False, 'delay_min': 2, 'delay_max': 8}
                    else:
                        stealth_config = {'enabled': False}
                    
                    orchestrator = RedForgeOrchestrator(target)
                    orchestrator.set_stealth_config(stealth_config)
                    
                    # Exécuter selon la phase
                    results = {}
                    
                    def send_progress(progress, message, phase_name=None):
                        socketio.emit('progress', {
                            'task_id': task_id,
                            'progress': progress,
                            'message': message,
                            'phase': phase_name
                        })
                    
                    send_progress(10, 'Début de la reconnaissance', 'footprint')
                    
                    if phase in ['footprint', 'all']:
                        results['footprint'] = orchestrator.run_footprint()
                        send_progress(30, 'Reconnaissance terminée', 'footprint')
                    
                    if phase in ['analysis', 'all']:
                        results['analysis'] = orchestrator.run_analysis()
                        send_progress(50, 'Analyse terminée', 'analysis')
                    
                    if phase in ['scan', 'all']:
                        results['scan'] = orchestrator.run_scanning()
                        send_progress(70, 'Scan terminé', 'scan')
                    
                    if phase in ['exploit', 'all']:
                        results['exploit'] = orchestrator.run_exploitation()
                        send_progress(90, 'Exploitation terminée', 'exploit')
                    
                    send_progress(100, 'Opération terminée', None)
                    
                    task_results[task_id] = {'status': 'completed', 'results': results}
                    active_tasks[task_id]['status'] = 'completed'
                    
                    socketio.emit('scan_complete', {'task_id': task_id, 'results': results})
                    
                except Exception as e:
                    active_tasks[task_id]['status'] = 'failed'
                    task_results[task_id] = {'status': 'failed', 'error': str(e)}
                    socketio.emit('error', {'task_id': task_id, 'error': str(e)})
            
            thread = threading.Thread(target=run_scan)
            thread.daemon = True
            thread.start()
            
            return jsonify({'task_id': task_id, 'status': 'started'})
        
        @app.route('/api/task/<task_id>')
        def api_task(task_id):
            if task_id in task_results:
                return jsonify(task_results[task_id])
            elif task_id in active_tasks:
                return jsonify(active_tasks[task_id])
            return jsonify({'status': 'not_found'}), 404
        
        @app.route('/api/command', methods=['POST'])
        def api_command():
            data = request.get_json()
            command = data.get('command', '')
            
            # Commandes spéciales
            if command.lower() == 'help':
                help_text = """
Commandes disponibles:
  help          - Affiche cette aide
  clear         - Efface le terminal
  status        - Affiche le statut
  mode [mode]   - Change le mode (standard/stealth/apt)
  target [url]  - Définit la cible
  scan          - Lance un scan rapide
  exit          - Quitte le terminal
                """
                return jsonify({'output': help_text, 'success': True})
            
            if command.lower() == 'clear':
                return jsonify({'output': '', 'clear': True, 'success': True})
            
            if command.lower() == 'status':
                status = f"""
RedForge Status
===============
Mode: {currentMode}
Statut: Actif
Cible: {active_tasks.get('current_target', 'Non définie')}
Tâches actives: {len(active_tasks)}
Vulnérabilités: {len(task_results)}
                """
                return jsonify({'output': status, 'success': True})
            
            if command.lower().startswith('mode '):
                new_mode = command.split()[1].lower()
                if new_mode in ['standard', 'stealth', 'apt']:
                    currentMode = new_mode
                    return jsonify({'output': f'Mode changé pour: {new_mode.upper()}', 'success': True})
                return jsonify({'output': f'Mode invalide: {new_mode}. Modes: standard, stealth, apt', 'success': False})
            
            if command.lower().startswith('target '):
                new_target = command[7:].strip()
                active_tasks['current_target'] = new_target
                return jsonify({'output': f'Cible définie: {new_target}', 'success': True})
            
            if command.lower() == 'scan':
                target = active_tasks.get('current_target')
                if not target:
                    return jsonify({'output': 'Aucune cible définie. Utilisez "target [url]"', 'success': False})
                # Lancer un scan rapide
                threading.Thread(target=lambda: socketio.emit('scan_start', {'target': target})).start()
                return jsonify({'output': f'Scan lancé sur {target}', 'success': True})
            
            # Commande système
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                return jsonify({'output': result.stdout + result.stderr, 'success': result.returncode == 0})
            except subprocess.TimeoutExpired:
                return jsonify({'output': 'Timeout après 30 secondes', 'success': False})
            except Exception as e:
                return jsonify({'output': str(e), 'success': False})
        
        @app.route('/api/export')
        def api_export():
            target = request.args.get('target', '')
            if not target:
                return jsonify({'error': 'Cible requise'}), 400
            
            # Générer un rapport
            report = {
                'target': target,
                'timestamp': datetime.now().isoformat(),
                'mode': currentMode,
                'results': task_results
            }
            
            response = jsonify(report)
            response.headers['Content-Disposition'] = f'attachment; filename=redforge_report_{target}.json'
            return response
        
        @app.route('/api/settings', methods=['GET', 'POST'])
        def api_settings():
            if request.method == 'GET':
                return jsonify({
                    'proxy_http': RedForgeConfig.proxy.http,
                    'delay_min': RedForgeConfig.stealth.delay_min,
                    'delay_max': RedForgeConfig.stealth.delay_max
                })
            
            data = request.get_json()
            if 'proxy_http' in data:
                RedForgeConfig.proxy.http = data['proxy_http']
                RedForgeConfig.proxy.enabled = bool(data['proxy_http'])
            if 'delay_min' in data:
                RedForgeConfig.stealth.delay_min = data['delay_min']
            if 'delay_max' in data:
                RedForgeConfig.stealth.delay_max = data['delay_max']
            
            RedForgeConfig.save_config()
            return jsonify({'success': True})
        
        @socketio.on('connect')
        def handle_connect():
            emit('connected', {'message': 'Connecté à RedForge', 'version': '2.0.0'})
        
        # Démarrer le serveur
        webbrowser.open(f"http://{self.host}:{self.port}")
        socketio.run(app, host=self.host, port=self.port, debug=False, allow_unsafe_werkzeug=True)


# Point d'entrée
if __name__ == "__main__":
    gui = RedForgeGUI()
    gui.run()