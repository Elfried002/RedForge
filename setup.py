#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for RedForge v2.0
Installation et configuration du package avec support Multi-Attacks, Stealth Mode, APT Operations
"""

import os
import sys
from pathlib import Path

# Tentative d'import de setuptools avec fallback
try:
    from setuptools import setup, find_packages
except ImportError:
    print("⚠️ setuptools non trouvé, installation...")
    os.system(f"{sys.executable} -m pip install setuptools wheel")
    from setuptools import setup, find_packages

# Lecture du README
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    long_description = """# RedForge v2.0

Plateforme d'Orchestration de Pentest Web pour Red Team avec support:
- 🎯 Attaques simples et multiples
- 🕵️ Mode furtif avancé (TOR, proxies, user-agents aléatoires)
- 🎭 Opérations APT complètes
- 📊 Rapports détaillés
- 🌐 Interface web moderne"""

# Dépendances principales
requirements = [
    # Web Framework
    "flask>=2.3.0",
    "flask-socketio>=5.3.0",
    "flask-cors>=4.0.0",
    "flask-login>=0.6.0",
    "gunicorn>=21.2.0",
    "gevent>=23.9.0",
    "gevent-websocket>=0.10.1",
    
    # HTTP & Web
    "requests>=2.31.0",
    "httpx>=0.26.0",
    "aiohttp>=3.9.0",
    "beautifulsoup4>=4.12.0",
    "lxml>=5.1.0",
    "selenium>=4.15.0",
    "playwright>=1.40.0",
    
    # Sécurité
    "cryptography>=42.0.0",
    "pyjwt>=2.8.0",
    "bcrypt>=4.1.0",
    "passlib>=1.7.4",
    "pycryptodome>=3.19.0",
    
    # Analyse
    "python-nmap>=0.7.1",
    "paramiko>=3.4.0",
    "dnspython>=2.6.0",
    "netaddr>=0.9.0",
    "ipaddress>=1.0.23",
    
    # CLI & UI
    "rich>=13.7.0",
    "colorama>=0.4.6",
    "pyyaml>=6.0.0",
    "click>=8.1.0",
    "tqdm>=4.66.0",
    "prompt-toolkit>=3.0.43",
    "pygments>=2.17.0",
    
    # Base de données
    "sqlalchemy>=2.0.0",
    "redis>=5.0.0",
    "pymongo>=4.6.0",
    
    # Reporting
    "reportlab>=4.1.0",
    "markdown>=3.5.0",
    "tabulate>=0.9.0",
    "matplotlib>=3.8.0",
    "pandas>=2.2.0",
    "jinja2>=3.1.0",
    "weasyprint>=60.0",
    "openpyxl>=3.1.0",
    "xlsxwriter>=3.1.0",
    
    # Utilitaires
    "python-dateutil>=2.8.0",
    "pytz>=2023.3",
    "psutil>=5.9.0",
    "python-magic>=0.4.27",
    "pydantic>=2.6.0",
    "loguru>=0.7.0",
    
    # WebSocket
    "websockets>=12.0",
    "pysocks>=1.7.0",
    
    # Mode furtif
    "stem>=1.8.0",
    "requests-tor>=0.1.3",
    "proxy-py>=2.3.0",
    
    # Multi-attaques
    "concurrent-futures>=3.1.1",
    "celery>=5.3.0",
    
    # APT Operations
    "cryptography>=42.0.0",
    "steganography>=0.1.2",
    
    # Scheduling
    "schedule>=1.2.0",
]

# Dépendances de développement
dev_requirements = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.12.0",
    "black>=23.12.0",
    "flake8>=7.0.0",
    "mypy>=1.8.0",
    "pylint>=3.0.0",
    "pre-commit>=3.6.0",
    "tox>=4.11.0",
    "sphinx>=7.2.0",
    "sphinx-rtd-theme>=1.3.0",
]

# Dépendances Docker
docker_requirements = [
    "docker>=7.0.0",
    "docker-compose>=1.29.0",
]

# Dépendances Windows
windows_requirements = [
    "pywin32>=306",
    "wmi>=1.5.1",
]

setup(
    name="redforge",
    version="2.0.0",
    author="RedForge Team",
    author_email="support@redforge.io",
    description="Plateforme d'Orchestration de Pentest Web pour Red Team - Multi-Attacks, Stealth Mode, APT Operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Elfried002/RedForge",
    project_urls={
        "Source": "https://github.com/Elfried002/RedForge",
        "Issues": "https://github.com/Elfried002/RedForge/issues",
    },
    license="GPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    keywords="pentest, security, redteam, hacking, cybersecurity, orchestration, multi-attacks, stealth, apt",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "redforge": [
            # Wordlists
            "data/wordlists/*.txt",
            "data/wordlists/**/*.txt",
            "data/signatures/*.json",
            "data/payloads/*.txt",
            
            # Internationalisation
            "i18n/fr_FR/*.json",
            "i18n/en_US/*.json",
            
            # Templates web
            "web_interface/templates/*.html",
            "web_interface/templates/partials/*.html",
            
            # Assets web
            "web_interface/static/css/*.css",
            "web_interface/static/js/*.js",
            "web_interface/static/images/*.png",
            "web_interface/static/images/*.ico",
            
            # Configurations
            "config/*.json",
            "config/*.yaml",
            
            # Stealth
            "stealth/user_agents.txt",
            "stealth/proxies.txt",
            
            # Multi-attacks
            "multi_attack/templates/*.json",
            
            # APT Operations
            "apt_operations/templates/*.json",
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "docker": docker_requirements,
        "windows": windows_requirements,
        "all": dev_requirements + docker_requirements + windows_requirements,
    },
    entry_points={
        "console_scripts": [
            "redforge=src.core.cli:main",
            "RedForge=src.core.cli:main",
            "rf=src.core.cli:main",
        ],
    },
    python_requires=">=3.11",
    zip_safe=False,
    platforms=["Linux", "Darwin"],
    scripts=[
        "bin/RedForge",
    ],
)


def post_install():
    """Actions post-installation améliorées pour v2.0"""
    print("\n" + "=" * 60)
    print("🔧 Configuration post-installation de RedForge v2.0")
    print("=" * 60)
    
    home_dir = Path.home()
    redforge_dir = home_dir / ".RedForge"
    
    # Créer les répertoires utilisateur
    subdirs = [
        "logs",
        "reports",
        "workspace",
        "sessions",
        "wordlists",
        "stealth",
        "multi_attack",
        "apt_operations",
        "persistence",
        "uploads",
        "cache"
    ]
    
    for subdir in subdirs:
        (redforge_dir / subdir).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Répertoire créé: {subdir}")
    
    # Créer le fichier de configuration par défaut v2.0
    config_file = redforge_dir / "config.json"
    if not config_file.exists():
        import json
        default_config = {
            "version": "2.0.0",
            "language": "fr_FR",
            "theme": "dark",
            "timeout": 300,
            "threads": 10,
            "workspace": str(redforge_dir / "workspace"),
            "logs": str(redforge_dir / "logs"),
            "reports": str(redforge_dir / "reports"),
            "stealth": {
                "enabled": False,
                "default_level": "medium",
                "random_user_agents": True,
                "use_tor": False,
                "rotate_proxies": False,
                "mimic_human": True,
                "random_delays": True,
                "slow_loris": False,
                "min_delay": 0.5,
                "max_delay": 3.0,
                "jitter": 0.3
            },
            "multi_attack": {
                "default_mode": "sequential",
                "max_parallel": 5,
                "delay": 1,
                "timeout": 300,
                "stop_on_error": False,
                "save_intermediate": True,
                "auto_retry": False
            },
            "apt": {
                "auto_cleanup": True,
                "phase_delay": 5,
                "log_all_phases": True,
                "require_confirmation": False,
                "persistence_dir": str(redforge_dir / "persistence"),
                "exfil_method": "http",
                "chunk_size": 512
            },
            "notifications": {
                "scan_complete": True,
                "vulnerability": True,
                "session": True,
                "report": True,
                "multi_complete": True,
                "apt_complete": True,
                "stealth_alert": True,
                "email": "",
                "webhook": "",
                "threshold": 5
            },
            "api": {
                "enabled": True,
                "token": None,
                "rate_limit": 100
            }
        }
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        print("  ✅ Configuration v2.0 créée")
    
    # Créer les fichiers d'exemple pour les wordlists
    wordlists_dir = redforge_dir / "wordlists"
    default_wordlists = {
        "passwords": ["admin", "password", "123456", "root", "toor"],
        "usernames": ["admin", "root", "user", "test", "guest"],
        "directories": ["admin", "wp-admin", "login", "dashboard", "backup"],
        "subdomains": ["www", "mail", "admin", "dev", "test"]
    }
    
    for category, words in default_wordlists.items():
        wl_file = wordlists_dir / f"{category}_default.txt"
        if not wl_file.exists():
            with open(wl_file, "w") as f:
                f.write("\n".join(words))
            print(f"  ✅ Wordlist par défaut créée: {category}_default.txt")
    
    # Créer le fichier user_agents.txt pour le mode furtif
    user_agents_file = redforge_dir / "stealth" / "user_agents.txt"
    if not user_agents_file.exists():
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Firefox/121.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        with open(user_agents_file, "w") as f:
            f.write("\n".join(user_agents))
        print("  ✅ User-Agents pour mode furtif créés")
    
    print("\n" + "=" * 60)
    print("✅ Configuration post-installation terminée")
    print("=" * 60)
    
    print("\n📖 Pour commencer avec RedForge v2.0:")
    print("  " + "-" * 50)
    print("  🖥️  Interface web:   sudo redforge -g")
    print("  🎯  Aide:            redforge --help")
    print("  🕵️  Mode furtif:      redforge --stealth")
    print("  📚  Multi-attaque:    redforge --multi config.json")
    print("  🎭  Opération APT:    redforge --apt recon_to_exfil")
    print("  " + "-" * 50)
    
    print("\n📂 Dossiers créés:")
    print(f"  • Configuration: {redforge_dir}")
    print(f"  • Wordlists:     {redforge_dir / 'wordlists'}")
    print(f"  • Stealth:       {redforge_dir / 'stealth'}")
    print(f"  • Multi-attacks: {redforge_dir / 'multi_attack'}")
    print(f"  • APT:           {redforge_dir / 'apt_operations'}")
    
    print("\n🌐 Interface web disponible sur: http://localhost:5000")
    print("\n🔴 RedForge v2.0 est prêt à l'emploi !\n")


def check_dependencies():
    """Vérifie les dépendances système requises"""
    print("\n🔍 Vérification des dépendances système...")
    
    import shutil
    missing = []
    
    # Outils optionnels recommandés
    tools = {
        "nmap": "scan réseau",
        "sqlmap": "injection SQL",
        "tor": "mode furtif",
        "msfconsole": "framework Metasploit",
        "hydra": "force brute",
        "john": "cassage de mots de passe",
        "whatweb": "reconnaissance web"
    }
    
    for tool, desc in tools.items():
        if shutil.which(tool):
            print(f"  ✅ {tool} trouvé ({desc})")
        else:
            print(f"  ⚠️ {tool} non trouvé ({desc} - optionnel)")
            missing.append(tool)
    
    if missing:
        print(f"\n📦 Pour installer les outils manquants sur Kali/Parrot:")
        print(f"   sudo apt install {' '.join(missing)}")
    
    print("\n✅ Vérification terminée")


# Exécution post-installation
if __name__ == "__main__":
    setup()
    
    # Exécuter les actions post-installation
    if "install" in sys.argv or "develop" in sys.argv:
        try:
            post_install()
            check_dependencies()
        except Exception as e:
            print(f"⚠️ Erreur post-installation: {e}")