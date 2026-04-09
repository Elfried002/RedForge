#!/bin/bash
# ========================================
# RedForge - Script d'installation environnement développement
# Configure l'environnement de développement
# Version: 2.0.0 - Support Multi-Attaque, Stealth & APT
# ========================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Bannière
show_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║     RedForge - Configuration environnement développement v2.0    ║
║        Support Multi-Attaque, Mode Furtif & APT                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${PROJECT_DIR}/venv"
REQUIREMENTS_DEV="${PROJECT_DIR}/requirements-dev.txt"
REQUIREMENTS_STEALTH="${PROJECT_DIR}/requirements-stealth.txt"
REQUIREMENTS_APT="${PROJECT_DIR}/requirements-apt.txt"
PYTHON_VERSION="3.11"
NODE_VERSION="18"

# Nouvelles configurations
STEALTH_TOOLS=("tor" "proxychains" "macchanger" "wireguard")
APT_TOOLS=("metasploit-framework" "cobaltstrike" "empire" "bloodhound" "mimikatz")

# Fonctions
print_status() { echo -e "${BLUE}[*]${NC} $1"; }
print_success() { echo -e "${GREEN}[+]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[-]${NC} $1"; }
print_info() { echo -e "${MAGENTA}[i]${NC} $1"; }

# Logger
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "${PROJECT_DIR}/dev_setup.log"
}

# Vérifier les prérequis
check_prerequisites() {
    print_status "Vérification des prérequis..."
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 n'est pas installé"
        exit 1
    fi
    PYTHON_VER=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    if [[ "$PYTHON_VER" < "$PYTHON_VERSION" ]]; then
        print_warning "Python $PYTHON_VERSION+ recommandé (actuel: $PYTHON_VER)"
    fi
    print_success "Python 3: $(python3 --version)"
    
    # Vérifier pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 n'est pas installé"
        exit 1
    fi
    print_success "pip3: $(pip3 --version)"
    
    # Vérifier git
    if ! command -v git &> /dev/null; then
        print_error "git n'est pas installé"
        exit 1
    fi
    print_success "git: $(git --version)"
    
    # Vérifier make
    if ! command -v make &> /dev/null; then
        print_warning "make non installé (optionnel)"
    else
        print_success "make: $(make --version | head -1)"
    fi
    
    log_message "Prérequis vérifiés"
}

# Créer l'environnement virtuel
create_venv() {
    print_status "Création de l'environnement virtuel..."
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Environnement virtuel existant. Suppression..."
        rm -rf "$VENV_DIR"
        log_message "Ancien environnement virtuel supprimé"
    fi
    
    python3 -m venv "$VENV_DIR"
    print_success "Environnement virtuel créé: $VENV_DIR"
    log_message "Environnement virtuel créé"
}

# Activer l'environnement virtuel
activate_venv() {
    print_status "Activation de l'environnement virtuel..."
    source "$VENV_DIR/bin/activate"
    print_success "Environnement virtuel activé"
    log_message "Environnement virtuel activé"
}

# Installer les dépendances de développement
install_dependencies() {
    print_status "Installation des dépendances Python..."
    
    # Mettre à jour pip
    pip install --upgrade pip
    print_success "pip mis à jour"
    
    # Installer les dépendances de développement
    if [ -f "$REQUIREMENTS_DEV" ]; then
        pip install -r "$REQUIREMENTS_DEV"
        print_success "Dépendances de développement installées"
        log_message "Dépendances de développement installées"
    else
        print_warning "Fichier requirements-dev.txt non trouvé"
        print_info "Installation des dépendances par défaut..."
        
        # Dépendances de base pour le développement
        pip install pytest pytest-cov pytest-xdist pytest-mock pytest-asyncio
        pip install black flake8 pylint mypy isort
        pip install pre-commit
        pip install tox
        pip install sphinx sphinx-rtd-theme myst-parser
        pip install ipython ipdb
        pip install bandit safety
        pip install wheel twine
        pip install coverage
        pip install hypothesis
        pip install factory-boy faker
        
        log_message "Dépendances de développement par défaut installées"
    fi
    
    # Vérifier les installations
    print_status "Vérification des installations:"
    pip list 2>/dev/null | grep -E "pytest|black|flake8|sphinx|pre-commit|coverage" || print_warning "Certains packages peuvent manquer"
}

# Installer les dépendances pour le mode furtif
install_stealth_dependencies() {
    print_status "Installation des dépendances pour le mode furtif..."
    
    if [ -f "$REQUIREMENTS_STEALTH" ]; then
        pip install -r "$REQUIREMENTS_STEALTH"
        print_success "Dépendances furtives installées"
        log_message "Dépendances furtives installées"
    else
        print_info "Installation des packages furtifs par défaut..."
        
        pip install requests[socks]
        pip install stem  # Pour Tor
        pip install PySocks
        pip install fake-useragent
        pip install selenium
        pip install undetected-chromedriver
        pip install cloudscraper
        
        log_message "Packages furtifs installés"
    fi
    
    # Vérifier les outils furtifs système
    for tool in "${STEALTH_TOOLS[@]}"; do
        if command -v "$tool" &> /dev/null; then
            print_success "$tool disponible"
        else
            print_warning "$tool non installé (optionnel pour le mode furtif)"
        fi
    done
}

# Installer les dépendances APT
install_apt_dependencies() {
    print_status "Installation des dépendances pour les opérations APT..."
    
    if [ -f "$REQUIREMENTS_APT" ]; then
        pip install -r "$REQUIREMENTS_APT"
        print_success "Dépendances APT installées"
        log_message "Dépendances APT installées"
    else
        print_info "Installation des packages APT par défaut..."
        
        pip install impacket
        pip install pycryptodome
        pip install paramiko
        pip install scp
        pip install pyminizip
        pip install steganography
        pip install dnslib
        pip install pycryptodomex
        
        log_message "Packages APT installés"
    fi
    
    # Vérifier les outils APT système
    for tool in "${APT_TOOLS[@]}"; do
        if command -v "$tool" &> /dev/null; then
            print_success "$tool disponible"
        else
            print_warning "$tool non installé (optionnel pour les opérations APT)"
        fi
    done
}

# Installer Node.js (optionnel)
install_nodejs() {
    print_status "Vérification de Node.js..."
    
    if ! command -v node &> /dev/null; then
        print_warning "Node.js non installé (optionnel pour la documentation)"
        read -p "Voulez-vous installer Node.js $NODE_VERSION ? (o/N): " install_node
        if [[ "$install_node" =~ ^[oO]$ ]]; then
            print_info "Installation de Node.js $NODE_VERSION..."
            curl -fsSL "https://deb.nodesource.com/setup_${NODE_VERSION}.x" | bash -
            apt install -y nodejs
            print_success "Node.js installé: $(node --version)"
            log_message "Node.js installé"
        fi
    else
        print_success "Node.js: $(node --version)"
    fi
}

# Configurer pre-commit avec hooks supplémentaires
setup_precommit() {
    print_status "Configuration de pre-commit..."
    
    if command -v pre-commit &> /dev/null; then
        cat > "${PROJECT_DIR}/.pre-commit-config.yaml" << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: detect-private-key
      - id: check-case-conflict
  
  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
      - id: black
        language_version: python3
        args: [--line-length=100]
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100, --extend-ignore=E203,W503]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black", "--line-length=100"]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
        args: [--ignore-missing-imports]
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.8
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        additional_dependencies: ["bandit[toml]"]
  
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.3
    hooks:
      - id: prettier
        types_or: [javascript, css, html, json]
EOF
        
        pre-commit install
        print_success "pre-commit configuré"
        log_message "pre-commit configuré"
    else
        print_warning "pre-commit non installé"
    fi
}

# Configurer les hooks git
setup_git_hooks() {
    print_status "Configuration des hooks git..."
    
    mkdir -p "${PROJECT_DIR}/.git/hooks"
    
    # Hook post-commit
    cat > "${PROJECT_DIR}/.git/hooks/post-commit" << 'EOF'
#!/bin/bash
# Hook post-commit RedForge
echo "✅ Commit effectué"
EOF
    chmod +x "${PROJECT_DIR}/.git/hooks/post-commit"
    
    # Hook pre-commit (si pre-commit n'est pas utilisé)
    if ! command -v pre-commit &> /dev/null; then
        cat > "${PROJECT_DIR}/.git/hooks/pre-commit" << 'EOF'
#!/bin/bash
# Hook pre-commit RedForge
echo "🔍 Vérification du code avant commit..."
black --check src/ || exit 1
flake8 src/ || exit 1
echo "✅ Code valide"
EOF
        chmod +x "${PROJECT_DIR}/.git/hooks/pre-commit"
    fi
    
    # Hook pre-push
    cat > "${PROJECT_DIR}/.git/hooks/pre-push" << 'EOF'
#!/bin/bash
# Hook pre-push RedForge
echo "🔍 Exécution des tests avant push..."
if [ -d "venv" ]; then
    source venv/bin/activate
fi
pytest tests/ -v --cov=src --cov-report=term
if [ $? -ne 0 ]; then
    echo "❌ Tests échoués, push annulé"
    exit 1
fi
echo "✅ Tests passés, push autorisé"
EOF
    chmod +x "${PROJECT_DIR}/.git/hooks/pre-push"
    
    print_success "Hooks git configurés"
    log_message "Hooks git configurés"
}

# Configurer les outils de développement
setup_dev_tools() {
    print_status "Configuration des outils de développement..."
    
    # Black configuration
    cat > "${PROJECT_DIR}/pyproject.toml" << EOF
[tool.black]
line-length = 100
target-version = ['py311', 'py312']
include = '\.pyi?$'
extend-exclude = '''
/(
    \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --cov=src --cov-report=html --cov-report=term --cov-report=xml"
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
asyncio_mode = "auto"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
strict_optional = true

[tool.flake8]
max-line-length = 100
extend-ignore = "E203,W503"
exclude = [
    ".git",
    "__pycache__",
    "build",
    "dist",
    "venv",
    ".venv",
    "docs",
    "tests"
]

[tool.bandit]
exclude_dirs = ["tests", "docs", "venv"]
skids = ["B101", "B601"]
severity = "medium"
confidence = "medium"

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/venv/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:"
]
fail_under = 70

[tool.pylint]
max-line-length = 100
disable = ["C0111", "C0103", "R0903", "R0201"]
EOF
    
    print_success "Fichiers de configuration créés"
    log_message "Outils de développement configurés"
}

# Créer la structure des tests
setup_tests() {
    print_status "Création de la structure des tests..."
    
    mkdir -p "${PROJECT_DIR}/tests"/{unit,integration,fixtures,performance,security}
    
    # Fichier __init__.py
    cat > "${PROJECT_DIR}/tests/__init__.py" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests unitaires pour RedForge."""
EOF
    
    # Conftest.py pour les fixtures
    cat > "${PROJECT_DIR}/tests/conftest.py" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fixtures partagées pour les tests."""

import pytest
import tempfile
import json
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Crée un répertoire temporaire pour les tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """Retourne une configuration d'exemple."""
    return {
        "version": "1.0.0",
        "language": "fr_FR",
        "timeout": 300,
        "threads": 10,
        "stealth": {"enabled": False},
        "apt": {"enabled": False}
    }


@pytest.fixture
def sample_target():
    """Retourne une cible d'exemple."""
    return "https://example.com"


@pytest.fixture
def mock_stealth_engine():
    """Mock du moteur furtif."""
    class MockStealth:
        def random_delay(self): return 0.5
        def rotate_ua(self): return "Mozilla/5.0"
    return MockStealth()


@pytest.fixture
def mock_apt_manager():
    """Mock du gestionnaire APT."""
    class MockAPT:
        def persist(self): return True
        def lateral_move(self): return True
    return MockAPT()
EOF
    
    # Exemple de test unitaire
    cat > "${PROJECT_DIR}/tests/unit/test_example.py" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exemple de test unitaire."""

import pytest


class TestExample:
    """Test example."""
    
    def test_example(self):
        """Example test."""
        assert True
    
    def test_addition(self):
        """Test addition."""
        assert 1 + 1 == 2
    
    @pytest.mark.parametrize("a,b,expected", [
        (1, 2, 3),
        (5, 5, 10),
        (0, 0, 0),
    ])
    def test_addition_params(self, a, b, expected):
        """Test addition with parameters."""
        assert a + b == expected
    
    def test_string_concatenation(self):
        """Test string concatenation."""
        assert "Hello" + " " + "World" == "Hello World"
EOF
    
    # Exemple de test d'intégration
    cat > "${PROJECT_DIR}/tests/integration/test_integration.py" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exemple de test d'intégration."""

import pytest


class TestIntegration:
    """Integration tests."""
    
    def test_config_loading(self, sample_config):
        """Test configuration loading."""
        assert sample_config["version"] == "1.0.0"
        assert sample_config["language"] == "fr_FR"
    
    def test_target_format(self, sample_target):
        """Test target format."""
        assert sample_target.startswith("https://")
        assert "example.com" in sample_target
    
    def test_stealth_config(self, sample_config):
        """Test stealth configuration."""
        assert "stealth" in sample_config
        assert isinstance(sample_config["stealth"], dict)
    
    def test_apt_config(self, sample_config):
        """Test APT configuration."""
        assert "apt" in sample_config
        assert isinstance(sample_config["apt"], dict)
EOF
    
    # Exemple de test de performance
    cat > "${PROJECT_DIR}/tests/performance/test_performance.py" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests de performance."""

import pytest
import time


class TestPerformance:
    """Performance tests."""
    
    def test_response_time(self):
        """Test response time under load."""
        start = time.time()
        time.sleep(0.1)  # Simuler une opération
        end = time.time()
        assert (end - start) < 0.5
    
    @pytest.mark.performance
    def test_multi_attack_performance(self):
        """Test multi-attack performance."""
        import asyncio
        import time
        
        async def mock_attack():
            await asyncio.sleep(0.1)
            return True
        
        start = time.time()
        loop = asyncio.new_event_loop()
        tasks = [mock_attack() for _ in range(10)]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        end = time.time()
        
        assert all(results)
        assert (end - start) < 2.0
EOF
    
    # Exemple de test de sécurité
    cat > "${PROJECT_DIR}/tests/security/test_security.py" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests de sécurité."""

import pytest


class TestSecurity:
    """Security tests."""
    
    def test_no_hardcoded_secrets(self):
        """Test that no secrets are hardcoded."""
        import os
        import re
        
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']'
        ]
        
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r') as f:
                        content = f.read()
                        for pattern in secret_patterns:
                            assert not re.search(pattern, content), f"Secret found in {filepath}"
    
    def test_input_validation(self):
        """Test input validation."""
        from src.utils.validator import validate_target
        
        valid_targets = ["example.com", "192.168.1.1", "https://example.com"]
        invalid_targets = ["", "javascript:alert(1)", "../../../etc/passwd"]
        
        for target in valid_targets:
            assert validate_target(target) is True
        
        for target in invalid_targets:
            assert validate_target(target) is False
EOF
    
    print_success "Structure des tests créée"
    log_message "Structure des tests créée"
}

# Configurer la documentation
setup_docs() {
    print_status "Configuration de la documentation..."
    
    mkdir -p "${PROJECT_DIR}/docs/source"
    mkdir -p "${PROJECT_DIR}/docs/build"
    
    # Configuration Sphinx
    cat > "${PROJECT_DIR}/docs/source/conf.py" << 'EOF'
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath('../../src'))

project = 'RedForge'
copyright = f'{datetime.now().year}, RedForge Team'
author = 'RedForge Team'
release = '1.0.0'
version = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'flask': ('https://flask.palletsprojects.com/', None),
}

todo_include_todos = True
autodoc_member_order = 'bysource'
napoleon_google_docstring = True
napoleon_numpy_docstring = False
EOF
    
    # Index de documentation
    cat > "${PROJECT_DIR}/docs/source/index.rst" << 'EOF'
RedForge Documentation
======================

Bienvenue dans la documentation de RedForge.

.. toctree::
   :maxdepth: 2
   :caption: Contenu:

   getting_started
   multi_attack
   stealth_mode
   apt_operations
   api_reference
   modules

Indices et tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
EOF
    
    # Guide de démarrage
    cat > "${PROJECT_DIR}/docs/source/getting_started.rst" << 'EOF'
Guide de démarrage
==================

Installation
------------

.. code-block:: bash

    git clone https://github.com/redteam/RedForge.git
    cd RedForge
    ./install.sh

Première utilisation
--------------------

.. code-block:: bash

    RedForge --help
    RedForge -t example.com -p footprint
    sudo RedForge -g
EOF
    
    # Documentation multi-attaque
    cat > "${PROJECT_DIR}/docs/source/multi_attack.rst" << 'EOF'
Attaques Multiples
==================

Sélection d'attaques
--------------------

.. code-block:: bash

    RedForge -t example.com -a injection.sql xss.reflected
    RedForge -t example.com -c cross_site
    RedForge --list-attacks

Configuration
-------------

Les profils d'attaque sont définis dans `config/profiles/`.
EOF
    
    # Documentation mode furtif
    cat > "${PROJECT_DIR}/docs/source/stealth_mode.rst" << 'EOF'
Mode Furtif (Stealth)
=====================

Activation
----------

.. code-block:: bash

    sudo RedForge -t example.com --stealth
    sudo RedForge -t example.com --stealth --stealth-level 3

Configuration
-------------

Le mode furtif utilise :
- Délais aléatoires
- Rotation des User-Agents
- DNS over HTTPS
- Contournement WAF
EOF
    
    # Documentation APT
    cat > "${PROJECT_DIR}/docs/source/apt_operations.rst" << 'EOF'
Opérations APT
==============

Activation
----------

.. code-block:: bash

    sudo RedForge -t example.com --apt
    sudo RedForge -t example.com --apt --persistence --c2-server https://c2.domain.com

Fonctionnalités
---------------

- Persistance avancée
- Mouvement latéral
- Canaux C2
- Exfiltration de données
- Anti-forensics
EOF
    
    # Makefile pour Sphinx
    cat > "${PROJECT_DIR}/docs/Makefile" << 'EOF'
# Minimal makefile for Sphinx documentation

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
EOF
    
    print_success "Documentation configurée"
    log_message "Documentation configurée"
}

# Installer les outils de développement supplémentaires
install_extra_tools() {
    print_status "Installation des outils supplémentaires..."
    
    # Vérifier et installer Docker (optionnel)
    if ! command -v docker &> /dev/null; then
        print_warning "Docker non installé (optionnel)"
        read -p "Voulez-vous installer Docker ? (o/N): " install_docker
        if [[ "$install_docker" =~ ^[oO]$ ]]; then
            print_info "Installation de Docker..."
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            rm get-docker.sh
            print_success "Docker installé"
            log_message "Docker installé"
        fi
    else
        print_success "Docker: $(docker --version)"
    fi
    
    # Vérifier et installer docker-compose (optionnel)
    if ! command -v docker-compose &> /dev/null; then
        print_warning "docker-compose non installé (optionnel)"
    else
        print_success "docker-compose: $(docker-compose --version)"
    fi
}

# Afficher les informations
show_info() {
    echo ""
    echo "=========================================="
    echo "✅ Environnement de développement prêt !"
    echo "=========================================="
    echo "📁 Environnement virtuel: $VENV_DIR"
    echo ""
    echo "📝 Commandes utiles:"
    echo "  source venv/bin/activate        # Activer l'environnement"
    echo "  deactivate                      # Désactiver l'environnement"
    echo ""
    echo "🧪 Tests:"
    echo "  pytest                          # Exécuter tous les tests"
    echo "  pytest tests/unit/              # Tests unitaires"
    echo "  pytest tests/integration/       # Tests d'intégration"
    echo "  pytest tests/performance/       # Tests de performance"
    echo "  pytest tests/security/          # Tests de sécurité"
    echo "  pytest --cov=src                # Tests avec couverture"
    echo ""
    echo "🎨 Qualité du code:"
    echo "  black src/                      # Formater le code"
    echo "  flake8 src/                     # Vérifier le style"
    echo "  mypy src/                       # Vérifier les types"
    echo "  pre-commit run --all-files      # Exécuter pre-commit"
    echo "  bandit -r src/                  # Analyse de sécurité"
    echo ""
    echo "📚 Documentation:"
    echo "  cd docs && make html            # Générer la documentation"
    echo "  cd docs/build/html && python -m http.server 8000  # Servir la doc"
    echo ""
    echo "🕵️ Mode Furtif (Stealth):"
    echo "  pip install -r requirements-stealth.txt  # Dépendances furtives"
    echo "  sudo apt install tor proxychains         # Outils furtifs système"
    echo ""
    echo "🎯 Mode APT:"
    echo "  pip install -r requirements-apt.txt      # Dépendances APT"
    echo "  sudo apt install metasploit-framework    # Outils APT système"
    echo ""
    echo "🐳 Docker:"
    echo "  docker build -t redforge:dev .  # Construire l'image"
    echo "  docker-compose up -d            # Démarrer les conteneurs"
    echo "=========================================="
}

# Main
main() {
    show_banner
    print_status "🚀 Démarrage de la configuration de l'environnement de développement"
    log_message "Début de la configuration"
    
    check_prerequisites
    create_venv
    activate_venv
    install_dependencies
    install_stealth_dependencies
    install_apt_dependencies
    install_nodejs
    setup_precommit
    setup_git_hooks
    setup_dev_tools
    setup_tests
    setup_docs
    install_extra_tools
    
    show_info
    
    print_success "✅ Configuration terminée !"
    log_message "Configuration terminée avec succès"
}

# Exécution
main "$@"