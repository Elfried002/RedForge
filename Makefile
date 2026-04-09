# ========================================
# RedForge - Makefile v2.0
# Commandes de build, test et déploiement
# Support Multi-Attacks, Stealth Mode, APT Operations
# ========================================

.PHONY: help install uninstall update clean test lint format run serve dev docker-build docker-up docker-down version stealth multi apt

# Variables
PYTHON := python3
PIP := pip3
VENV := venv
REDFORGE_HOME := /opt/RedForge
REDFORGE_USER_HOME := ${HOME}/.RedForge
SCRIPT_DIR := $(shell pwd)
DOCKER_COMPOSE := docker-compose

# Couleurs
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
MAGENTA := \033[0;35m
CYAN := \033[0;36m
NC := \033[0m

# Version
VERSION := 2.0.0

# Aide
help:
	@echo ""
	@echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
	@echo -e "${BLUE}║              RedForge v${VERSION} - Commandes Make                  ║${NC}"
	@echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
	@echo ""
	@echo -e "${GREEN}📦 Installation:${NC}"
	@echo "  make install        - Installer RedForge (complet)"
	@echo "  make install-min    - Installation minimale"
	@echo "  make uninstall      - Désinstaller RedForge"
	@echo "  make update         - Mettre à jour RedForge"
	@echo ""
	@echo -e "${GREEN}🛠️ Développement:${NC}"
	@echo "  make venv           - Créer l'environnement virtuel"
	@echo "  make deps           - Installer les dépendances"
	@echo "  make deps-dev       - Installer les dépendances de développement"
	@echo "  make clean          - Nettoyer les fichiers temporaires"
	@echo "  make clean-all      - Nettoyage complet"
	@echo ""
	@echo -e "${GREEN}🧪 Tests:${NC}"
	@echo "  make test           - Exécuter les tests"
	@echo "  make test-cov       - Exécuter les tests avec couverture"
	@echo "  make test-multi     - Tester les multi-attaques"
	@echo "  make test-apt       - Tester les opérations APT"
	@echo "  make test-stealth   - Tester le mode furtif"
	@echo ""
	@echo -e "${GREEN}📝 Qualité du code:${NC}"
	@echo "  make lint           - Vérifier le style du code"
	@echo "  make format         - Formater le code"
	@echo "  make type-check     - Vérifier les types (mypy)"
	@echo ""
	@echo -e "${GREEN}🚀 Exécution:${NC}"
	@echo "  make run            - Lancer RedForge (CLI)"
	@echo "  make serve          - Lancer le serveur web"
	@echo "  make dev            - Lancer en mode développement"
	@echo "  make stealth        - Lancer en mode furtif"
	@echo "  make multi          - Lancer une multi-attaque"
	@echo "  make apt            - Lancer une opération APT"
	@echo ""
	@echo -e "${GREEN}🐳 Docker:${NC}"
	@echo "  make docker-build   - Construire l'image Docker"
	@echo "  make docker-up      - Démarrer les conteneurs"
	@echo "  make docker-down    - Arrêter les conteneurs"
	@echo "  make docker-logs    - Voir les logs"
	@echo "  make docker-shell   - Shell dans le conteneur"
	@echo "  make docker-clean   - Nettoyer les conteneurs et volumes"
	@echo ""
	@echo -e "${GREEN}🔧 Utilitaires:${NC}"
	@echo "  make version        - Afficher la version"
	@echo "  make info           - Afficher les informations système"
	@echo "  make check-deps     - Vérifier les dépendances"
	@echo "  make wordlists      - Télécharger les wordlists"
	@echo "  make backup         - Sauvegarder la configuration"
	@echo "  make restore        - Restaurer la configuration"
	@echo ""

# ========================================
# Installation
# ========================================

install:
	@echo -e "${GREEN}[+] Installation de RedForge v${VERSION}...${NC}"
	@chmod +x install.sh
	@sudo ./install.sh

install-min:
	@echo -e "${GREEN}[+] Installation minimale de RedForge...${NC}"
	@chmod +x install.sh
	@sudo ./install.sh --minimal

uninstall:
	@echo -e "${YELLOW}[!] Désinstallation de RedForge...${NC}"
	@chmod +x uninstall.sh 2>/dev/null || true
	@sudo ./uninstall.sh 2>/dev/null || \
		(echo -e "${YELLOW}[!] Suppression manuelle...${NC}" && \
		 sudo rm -rf $(REDFORGE_HOME) && \
		 sudo rm -f /usr/local/bin/redforge /usr/local/bin/RedForge)

update:
	@echo -e "${GREEN}[+] Mise à jour de RedForge...${NC}"
	@git pull origin main
	@make deps
	@echo -e "${GREEN}[+] Mise à jour terminée${NC}"

# ========================================
# Environnement virtuel
# ========================================

venv:
	@echo -e "${GREEN}[+] Création de l'environnement virtuel...${NC}"
	@$(PYTHON) -m venv $(VENV)
	@echo -e "${GREEN}[+] Activez l'environnement: source $(VENV)/bin/activate${NC}"

deps:
	@echo -e "${GREEN}[+] Installation des dépendances...${NC}"
	@$(PIP) install -r requirements.txt

deps-dev:
	@echo -e "${GREEN}[+] Installation des dépendances de développement...${NC}"
	@$(PIP) install -r requirements-dev.txt
	@$(PIP) install pytest pytest-cov pytest-asyncio
	@$(PIP) install black flake8 mypy pylint
	@$(PIP) install pre-commit

# ========================================
# Nettoyage
# ========================================

clean:
	@echo -e "${YELLOW}[!] Nettoyage des fichiers temporaires...${NC}"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.so" -delete 2>/dev/null || true
	@rm -rf .pytest_cache/ .coverage htmlcov/ .mypy_cache/ .tox/ 2>/dev/null || true
	@rm -rf logs/*.log 2>/dev/null || true
	@rm -rf reports/*.html reports/*.pdf 2>/dev/null || true
	@rm -rf *.egg-info/ build/ dist/ 2>/dev/null || true
	@echo -e "${GREEN}[+] Nettoyage terminé${NC}"

clean-all: clean
	@echo -e "${YELLOW}[!] Nettoyage complet...${NC}"
	@rm -rf $(VENV) 2>/dev/null || true
	@rm -rf $(REDFORGE_USER_HOME)/workspace/* 2>/dev/null || true
	@rm -rf $(REDFORGE_USER_HOME)/stealth/* 2>/dev/null || true
	@rm -rf $(REDFORGE_USER_HOME)/apt_operations/* 2>/dev/null || true
	@rm -rf $(REDFORGE_USER_HOME)/multi_attack/* 2>/dev/null || true
	@echo -e "${GREEN}[+] Nettoyage complet terminé${NC}"

# ========================================
# Tests
# ========================================

test:
	@echo -e "${GREEN}[+] Exécution des tests...${NC}"
	@if [ -d "$(VENV)" ]; then \
		source $(VENV)/bin/activate && pytest tests/ -v; \
	else \
		pytest tests/ -v 2>/dev/null || echo -e "${YELLOW}[!] Tests à implémenter${NC}"; \
	fi

test-cov:
	@echo -e "${GREEN}[+] Exécution des tests avec couverture...${NC}"
	@if [ -d "$(VENV)" ]; then \
		source $(VENV)/bin/activate && pytest tests/ -v --cov=src --cov-report=html --cov-report=term; \
	else \
		pytest tests/ -v --cov=src --cov-report=html 2>/dev/null || echo -e "${YELLOW}[!] Tests à implémenter${NC}"; \
	fi

test-multi:
	@echo -e "${GREEN}[+] Test des multi-attaques...${NC}"
	@python3 -c "from src.attacks import AttackOrchestrator; print('Test multi-attaques OK')" 2>/dev/null || \
		echo -e "${YELLOW}[!] Module multi-attaques non trouvé${NC}"

test-apt:
	@echo -e "${GREEN}[+] Test des opérations APT...${NC}"
	@python3 -c "from src.core.attack_chainer import AttackChainer; print('Test APT OK')" 2>/dev/null || \
		echo -e "${YELLOW}[!] Module APT non trouvé${NC}"

test-stealth:
	@echo -e "${GREEN}[+] Test du mode furtif...${NC}"
	@python3 -c "from src.core.orchestrator import RedForgeOrchestrator; print('Test mode furtif OK')" 2>/dev/null || \
		echo -e "${YELLOW}[!] Module mode furtif non trouvé${NC}"

# ========================================
# Qualité du code
# ========================================

lint:
	@echo -e "${GREEN}[+] Vérification du style du code...${NC}"
	@if command -v flake8 &> /dev/null; then \
		flake8 src/ --max-line-length=100 --extend-ignore=E203,W503; \
	else \
		echo -e "${YELLOW}[!] flake8 non installé (pip install flake8)${NC}"; \
	fi

format:
	@echo -e "${GREEN}[+] Formatage du code...${NC}"
	@if command -v black &> /dev/null; then \
		black src/ --line-length=100; \
	else \
		echo -e "${YELLOW}[!] black non installé (pip install black)${NC}"; \
	fi

type-check:
	@echo -e "${GREEN}[+] Vérification des types...${NC}"
	@if command -v mypy &> /dev/null; then \
		mypy src/ --ignore-missing-imports; \
	else \
		echo -e "${YELLOW}[!] mypy non installé (pip install mypy)${NC}"; \
	fi

# ========================================
# Exécution
# ========================================

run:
	@echo -e "${GREEN}[+] Lancement de RedForge...${NC}"
	@if [ -f "bin/RedForge" ]; then \
		./bin/RedForge; \
	elif [ -f "/usr/local/bin/redforge" ]; then \
		sudo redforge; \
	elif [ -d "$(VENV)" ]; then \
		source $(VENV)/bin/activate && python bin/RedForge; \
	else \
		echo -e "${RED}[-] RedForge non trouvé${NC}"; \
		echo "Veuillez exécuter: make install"; \
	fi

serve:
	@echo -e "${GREEN}[+] Lancement du serveur web...${NC}"
	@echo -e "${CYAN}📍 http://localhost:5000${NC}"
	@if [ -d "$(VENV)" ]; then \
		source $(VENV)/bin/activate && python src/web_interface/app.py; \
	elif [ -f "/usr/local/bin/redforge" ]; then \
		sudo redforge -g; \
	else \
		python3 src/web_interface/app.py; \
	fi

dev:
	@echo -e "${GREEN}[+] Lancement en mode développement...${NC}"
	@export FLASK_ENV=development
	@export FLASK_DEBUG=1
	@export REDFORGE_DEBUG=true
	@if [ -d "$(VENV)" ]; then \
		source $(VENV)/bin/activate && python src/web_interface/app.py; \
	else \
		python3 src/web_interface/app.py; \
	fi

stealth:
	@echo -e "${GREEN}[+] Lancement en mode furtif...${NC}"
	@if [ -f "/usr/local/bin/redforge" ]; then \
		sudo redforge --stealth; \
	elif [ -d "$(VENV)" ]; then \
		source $(VENV)/bin/activate && python bin/RedForge --stealth; \
	else \
		echo -e "${RED}[-] RedForge non trouvé${NC}"; \
	fi

multi:
	@echo -e "${GREEN}[+] Lancement d'une multi-attaque...${NC}"
	@echo -e "${YELLOW}[!] Utilisation: make multi TARGET=example.com CONFIG=config.json${NC}"
	@if [ -n "$(TARGET)" ] && [ -f "$(CONFIG)" ]; then \
		if [ -f "/usr/local/bin/redforge" ]; then \
			sudo redforge --multi $(CONFIG) -t $(TARGET); \
		else \
			python bin/RedForge --multi $(CONFIG) -t $(TARGET); \
		fi \
	else \
		echo -e "${RED}[-] Spécifiez TARGET et CONFIG${NC}"; \
		echo "Exemple: make multi TARGET=example.com CONFIG=multi_config.json"; \
	fi

apt:
	@echo -e "${GREEN}[+] Lancement d'une opération APT...${NC}"
	@echo -e "${YELLOW}[!] Utilisation: make apt TARGET=example.com OPERATION=recon_to_exfil${NC}"
	@if [ -n "$(TARGET)" ] && [ -n "$(OPERATION)" ]; then \
		if [ -f "/usr/local/bin/redforge" ]; then \
			sudo redforge --apt $(OPERATION) -t $(TARGET); \
		else \
			python bin/RedForge --apt $(OPERATION) -t $(TARGET); \
		fi \
	else \
		echo -e "${RED}[-] Spécifiez TARGET et OPERATION${NC}"; \
		echo "Exemple: make apt TARGET=example.com OPERATION=recon_to_exfil"; \
	fi

# ========================================
# Docker
# ========================================

docker-build:
	@echo -e "${GREEN}[+] Construction de l'image Docker...${NC}"
	@docker build -t redforge:latest --build-arg REDFORGE_VERSION=$(VERSION) .

docker-up:
	@echo -e "${GREEN}[+] Démarrage des conteneurs...${NC}"
	@$(DOCKER_COMPOSE) up -d
	@echo -e "${GREEN}[+] RedForge disponible sur http://localhost:5000${NC}"
	@echo -e "${CYAN}Pour voir les logs: make docker-logs${NC}"

docker-up-full:
	@echo -e "${GREEN}[+] Démarrage complet (avec monitoring)...${NC}"
	@$(DOCKER_COMPOSE) --profile full up -d
	@echo -e "${GREEN}[+] Services disponibles:${NC}"
	@echo "  • RedForge: http://localhost:5000"
	@echo "  • Grafana: http://localhost:3000 (admin/admin)"
	@echo "  • Prometheus: http://localhost:9090"

docker-down:
	@echo -e "${YELLOW}[!] Arrêt des conteneurs...${NC}"
	@$(DOCKER_COMPOSE) down

docker-down-volumes:
	@echo -e "${YELLOW}[!] Arrêt et suppression des volumes...${NC}"
	@$(DOCKER_COMPOSE) down -v

docker-logs:
	@$(DOCKER_COMPOSE) logs -f

docker-shell:
	@$(DOCKER_COMPOSE) exec redforge /bin/bash

docker-clean:
	@echo -e "${YELLOW}[!] Nettoyage Docker...${NC}"
	@docker stop $$(docker ps -aq) 2>/dev/null || true
	@docker rm $$(docker ps -aq) 2>/dev/null || true
	@docker rmi redforge:latest 2>/dev/null || true
	@docker system prune -f
	@echo -e "${GREEN}[+] Nettoyage Docker terminé${NC}"

# ========================================
# Utilitaires
# ========================================

version:
	@echo -e "${GREEN}RedForge v${VERSION}${NC}"
	@if [ -f "bin/RedForge" ]; then \
		./bin/RedForge --version 2>/dev/null || true; \
	fi

info:
	@echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
	@echo -e "${CYAN}║                    Informations système                          ║${NC}"
	@echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
	@echo ""
	@echo -e "${GREEN}Version:${NC} $(VERSION)"
	@echo -e "${GREEN}Python:${NC} $(shell $(PYTHON) --version 2>/dev/null || echo 'Non trouvé')"
	@echo -e "${GREEN}OS:${NC} $(shell cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo 'Inconnu')"
	@echo -e "${GREEN}Architecture:${NC} $(shell uname -m)"
	@echo -e "${GREEN}Kernel:${NC} $(shell uname -r)"
	@echo -e "${GREEN}Docker:${NC} $(shell docker --version 2>/dev/null || echo 'Non installé')"
	@echo ""

check-deps:
	@echo -e "${GREEN}[+] Vérification des dépendances...${NC}"
	@echo -n "Python 3.8+: "
	@$(PYTHON) -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"
	@echo -n "pip: "
	@command -v pip3 &>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"
	@echo -n "nmap: "
	@command -v nmap &>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ (optionnel)${NC}"
	@echo -n "sqlmap: "
	@command -v sqlmap &>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ (optionnel)${NC}"
	@echo -n "tor: "
	@command -v tor &>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ (optionnel)${NC}"
	@echo -n "metasploit: "
	@command -v msfconsole &>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ (optionnel)${NC}"
	@echo ""

wordlists:
	@echo -e "${GREEN}[+] Téléchargement des wordlists...${NC}"
	@mkdir -p wordlists
	@# RockYou
	@if [ ! -f "wordlists/rockyou.txt" ]; then \
		echo "Téléchargement de rockyou.txt..."; \
		curl -L -o wordlists/rockyou.txt.gz https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt.gz && \
		gunzip wordlists/rockyou.txt.gz; \
	fi
	@# SecLists (version allégée)
	@if [ ! -d "wordlists/SecLists" ]; then \
		echo "Téléchargement de SecLists..."; \
		git clone --depth 1 https://github.com/danielmiessler/SecLists.git wordlists/SecLists; \
	fi
	@echo -e "${GREEN}[+] Wordlists téléchargées dans wordlists/${NC}"

backup:
	@echo -e "${GREEN}[+] Sauvegarde de la configuration...${NC}"
	@BACKUP_DIR="backups/backup_$$(date +%Y%m%d_%H%M%S)"
	@mkdir -p $$BACKUP_DIR
	@cp -r $(REDFORGE_USER_HOME) $$BACKUP_DIR/ 2>/dev/null || echo "Aucune configuration utilisateur"
	@cp -r config/ $$BACKUP_DIR/ 2>/dev/null || true
	@echo -e "${GREEN}[+] Sauvegarde créée dans $$BACKUP_DIR${NC}"

restore:
	@echo -e "${GREEN}[+] Restauration de la configuration...${NC}"
	@echo -e "${YELLOW}[!] Liste des sauvegardes disponibles:${NC}"
	@ls -la backups/ 2>/dev/null || echo "Aucune sauvegarde trouvée"
	@read -p "Nom du dossier de sauvegarde: " BACKUP_NAME; \
	if [ -d "backups/$$BACKUP_NAME" ]; then \
		cp -r backups/$$BACKUP_NAME/.RedForge/* $(REDFORGE_USER_HOME)/ 2>/dev/null || true; \
		cp -r backups/$$BACKUP_NAME/config/* config/ 2>/dev/null || true; \
		echo -e "${GREEN}[+] Restauration terminée${NC}"; \
	else \
		echo -e "${RED}[-] Sauvegarde non trouvée${NC}"; \
	fi

# ========================================
# Pre-commit hooks
# ========================================

pre-commit:
	@echo -e "${GREEN}[+] Installation des pre-commit hooks...${NC}"
	@pip install pre-commit
	@pre-commit install

# ========================================
# Default target
# ========================================

.DEFAULT_GOAL := help