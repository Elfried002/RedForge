#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Web de RedForge
Serveur Flask pour l'interface graphique
Version avec support furtif, APT et interface avancée
"""

from flask import Flask
from typing import Optional, Dict, Any

# Version du module
__version__ = "2.0.0"

# Instance globale de l'application
_app_instance: Optional[Flask] = None


def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Crée et configure l'application Flask
    
    Args:
        config: Configuration personnalisée
        
    Returns:
        Application Flask configurée
    """
    global _app_instance
    
    if _app_instance is not None:
        return _app_instance
    
    from flask import Flask
    from flask_cors import CORS
    from flask_socketio import SocketIO
    
    # Créer l'application
    app = Flask(__name__)
    
    # Configuration par défaut
    app.config['SECRET_KEY'] = 'redforge_secret_key_change_me_2024'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 heure
    
    # Configuration personnalisée
    if config:
        app.config.update(config)
    
    # Configuration CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Importer les routes et événements
    from src.web_interface.routes import register_routes
    from src.web_interface.socket_events import register_socket_events
    from src.web_interface.api import register_api
    
    # Enregistrer les routes
    register_routes(app)
    register_api(app)
    register_socket_events(socketio)
    
    # Stocker l'instance
    _app_instance = app
    app.socketio = socketio
    
    return app


def get_app() -> Optional[Flask]:
    """
    Retourne l'instance de l'application Flask
    
    Returns:
        Application Flask ou None
    """
    return _app_instance


def run_server(host: str = "127.0.0.1", port: int = 5000, 
               debug: bool = False, stealth: bool = False,
               apt: bool = False) -> None:
    """
    Lance le serveur web
    
    Args:
        host: Hôte d'écoute
        port: Port d'écoute
        debug: Mode debug
        stealth: Mode furtif (logs minimisés)
        apt: Mode APT (ultra discret)
    """
    import webbrowser
    
    app = create_app()
    
    # Configurer les modes
    if stealth:
        app.config['STEALTH_MODE'] = True
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    
    if apt:
        app.config['APT_MODE'] = True
        import logging
        logging.getLogger('werkzeug').disabled = True
    
    # Ouvrir le navigateur
    if not stealth and not apt:
        webbrowser.open(f"http://{host}:{port}")
    
    # Démarrer le serveur
    print(f"\n🌐 Interface Web RedForge v{__version__}")
    print(f"📍 URL: http://{host}:{port}")
    print(f"🎭 Mode: {'APT' if apt else 'Stealth' if stealth else 'Normal'}")
    print("⚠️  Appuyez sur Ctrl+C pour arrêter\n")
    
    try:
        app.socketio.run(app, host=host, port=port, debug=debug, 
                        allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")


# Point d'entrée pour lancement direct
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Interface Web RedForge")
    parser.add_argument("--host", default="127.0.0.1", help="Hôte d'écoute")
    parser.add_argument("--port", type=int, default=5000, help="Port d'écoute")
    parser.add_argument("--debug", action="store_true", help="Mode debug")
    parser.add_argument("--stealth", action="store_true", help="Mode furtif")
    parser.add_argument("--apt", action="store_true", help="Mode APT")
    
    args = parser.parse_args()
    
    run_server(
        host=args.host,
        port=args.port,
        debug=args.debug,
        stealth=args.stealth,
        apt=args.apt
    )