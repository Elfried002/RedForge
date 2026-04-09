# ========================================
# RedForge - Dockerfile
# Build de l'image Docker de RedForge
# Version: 2.0.0 - Support Multi-Attacks, Stealth Mode, APT Operations
# ========================================

# Stage 1: Build des dépendances
FROM python:3.11-slim AS builder

# Arguments de build
ARG REDFORGE_VERSION=2.0.0
ARG DEBIAN_FRONTEND=noninteractive
ARG BUILD_DATE
ARG VCS_REF

# Labels
LABEL maintainer="RedForge Team <support@redforge.io>"
LABEL version="${REDFORGE_VERSION}"
LABEL description="RedForge - Plateforme d'Orchestration de Pentest Web avec support Multi-Attacks, Mode Furtif et Opérations APT"
LABEL build_date="${BUILD_DATE}"
LABEL vcs_ref="${VCS_REF}"
LABEL vendor="RedForge"
LABEL name="redforge"

# Installation des dépendances système pour la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    gcc \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /build

# Copier les requirements
COPY requirements.txt requirements-dev.txt ./

# Installer les dépendances Python dans un répertoire dédié
RUN pip install --no-cache-dir --user -r requirements.txt && \
    pip install --no-cache-dir --user gunicorn gevent-websocket

# Stage 2: Final
FROM python:3.11-slim

# Arguments de build
ARG REDFORGE_VERSION=2.0.0
ARG DEBIAN_FRONTEND=noninteractive

# Labels
LABEL maintainer="RedForge Team <support@redforge.io>"
LABEL version="${REDFORGE_VERSION}"
LABEL description="RedForge - Plateforme d'Orchestration de Pentest Web v${REDFORGE_VERSION}"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    REDFORGE_HOME=/opt/RedForge \
    REDFORGE_VERSION=${REDFORGE_VERSION} \
    REDFORGE_ENV=production \
    REDFORGE_DEBUG=false \
    REDFORGE_SECRET_KEY=change_me_in_production \
    PATH="/home/redteam/.local/bin:${PATH}"

# Installation des dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    ca-certificates \
    nmap \
    netcat-openbsd \
    dnsutils \
    libssl3 \
    libffi8 \
    procps \
    sqlmap \
    hydra \
    john \
    dirb \
    whatweb \
    tor \
    proxychains \
    jq \
    vim-tiny \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Installation de wordlists supplémentaires
RUN mkdir -p /usr/share/wordlists && \
    # Télécharger rockyou.txt (décompressé)
    curl -L -o /usr/share/wordlists/rockyou.txt.gz https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt.gz && \
    gunzip /usr/share/wordlists/rockyou.txt.gz || true && \
    # Télécharger SecLists (version allégée)
    git clone --depth 1 https://github.com/danielmiessler/SecLists.git /usr/share/seclists || true

# Créer l'utilisateur redteam
RUN useradd -m -s /bin/bash redteam && \
    echo "redteam:redteam" | chpasswd && \
    echo "redteam ALL=(ALL) NOPASSWD: /usr/bin/nmap, /usr/bin/sqlmap, /usr/bin/hydra, /usr/bin/tor, /usr/bin/proxychains" >> /etc/sudoers

# Créer les répertoires nécessaires
RUN mkdir -p ${REDFORGE_HOME} \
    ${REDFORGE_HOME}/config \
    ${REDFORGE_HOME}/logs \
    ${REDFORGE_HOME}/reports \
    ${REDFORGE_HOME}/workspace \
    ${REDFORGE_HOME}/wordlists \
    ${REDFORGE_HOME}/data \
    ${REDFORGE_HOME}/src \
    ${REDFORGE_HOME}/stealth \
    ${REDFORGE_HOME}/multi_attack \
    ${REDFORGE_HOME}/apt_operations \
    ${REDFORGE_HOME}/persistence \
    ${REDFORGE_HOME}/uploads \
    && chown -R redteam:redteam ${REDFORGE_HOME}

# Copier les dépendances Python depuis le stage builder
COPY --from=builder --chown=redteam:redteam /root/.local /home/redteam/.local

# Copier le code source
COPY --chown=redteam:redteam . ${REDFORGE_HOME}

# Créer l'exécutable principal
RUN mkdir -p ${REDFORGE_HOME}/bin && \
    echo '#!/usr/bin/env python3' > ${REDFORGE_HOME}/bin/RedForge && \
    echo 'import sys' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo 'import os' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo 'sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo 'def main():' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '    try:' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '        from src.web_interface.app import create_app, socketio' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '        app = create_app()' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '        socketio.run(app, host="0.0.0.0", port=5000, debug=False)' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '    except ImportError as e:' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '        print(f"Erreur d\'import: {e}")' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '        sys.exit(1)' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '    except Exception as e:' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '        print(f"Erreur: {e}")' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '        sys.exit(1)' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo 'if __name__ == "__main__":' >> ${REDFORGE_HOME}/bin/RedForge && \
    echo '    main()' >> ${REDFORGE_HOME}/bin/RedForge && \
    chmod +x ${REDFORGE_HOME}/bin/RedForge

# Créer le script de lancement Gunicorn (production)
RUN echo '#!/bin/bash' > ${REDFORGE_HOME}/run-gunicorn.sh && \
    echo 'cd ${REDFORGE_HOME}' >> ${REDFORGE_HOME}/run-gunicorn.sh && \
    echo 'export PATH="/home/redteam/.local/bin:${PATH}"' >> ${REDFORGE_HOME}/run-gunicorn.sh && \
    echo 'gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker' >> ${REDFORGE_HOME}/run-gunicorn.sh && \
    echo '  --bind 0.0.0.0:5000' >> ${REDFORGE_HOME}/run-gunicorn.sh && \
    echo '  --workers 4' >> ${REDFORGE_HOME}/run-gunicorn.sh && \
    echo '  --timeout 120' >> ${REDFORGE_HOME}/run-gunicorn.sh && \
    echo '  --access-logfile ${REDFORGE_HOME}/logs/access.log' >> ${REDFORGE_HOME}/run-gunicorn.sh && \
    echo '  --error-logfile ${REDFORGE_HOME}/logs/error.log' >> ${REDFORGE_HOME}/run-gunicorn.sh && \
    echo '  --log-level info' >> ${REDFORGE_HOME}/run-gunicorn.sh && \
    echo '  "src.web_interface.app:create_app()"' >> ${REDFORGE_HOME}/run-gunicorn.sh && \
    chmod +x ${REDFORGE_HOME}/run-gunicorn.sh

# Créer les fichiers __init__.py manquants
RUN find ${REDFORGE_HOME}/src -type d -exec touch {}/__init__.py \; 2>/dev/null || true

# Créer le fichier de configuration par défaut (v2.0)
RUN mkdir -p /home/redteam/.RedForge && \
    echo '{' > /home/redteam/.RedForge/config.json && \
    echo '    "version": "2.0.0",' >> /home/redteam/.RedForge/config.json && \
    echo '    "language": "fr_FR",' >> /home/redteam/.RedForge/config.json && \
    echo '    "theme": "dark",' >> /home/redteam/.RedForge/config.json && \
    echo '    "timeout": 300,' >> /home/redteam/.RedForge/config.json && \
    echo '    "threads": 10,' >> /home/redteam/.RedForge/config.json && \
    echo '    "workspace": "/home/redteam/.RedForge/workspace",' >> /home/redteam/.RedForge/config.json && \
    echo '    "logs": "/home/redteam/.RedForge/logs",' >> /home/redteam/.RedForge/config.json && \
    echo '    "reports": "/home/redteam/.RedForge/reports",' >> /home/redteam/.RedForge/config.json && \
    echo '    "stealth": {' >> /home/redteam/.RedForge/config.json && \
    echo '        "enabled": false,' >> /home/redteam/.RedForge/config.json && \
    echo '        "default_level": "medium",' >> /home/redteam/.RedForge/config.json && \
    echo '        "random_user_agents": true,' >> /home/redteam/.RedForge/config.json && \
    echo '        "use_tor": false,' >> /home/redteam/.RedForge/config.json && \
    echo '        "mimic_human": true' >> /home/redteam/.RedForge/config.json && \
    echo '    },' >> /home/redteam/.RedForge/config.json && \
    echo '    "multi_attack": {' >> /home/redteam/.RedForge/config.json && \
    echo '        "default_mode": "sequential",' >> /home/redteam/.RedForge/config.json && \
    echo '        "max_parallel": 5,' >> /home/redteam/.RedForge/config.json && \
    echo '        "stop_on_error": false' >> /home/redteam/.RedForge/config.json && \
    echo '    },' >> /home/redteam/.RedForge/config.json && \
    echo '    "apt": {' >> /home/redteam/.RedForge/config.json && \
    echo '        "auto_cleanup": true,' >> /home/redteam/.RedForge/config.json && \
    echo '        "phase_delay": 5,' >> /home/redteam/.RedForge/config.json && \
    echo '        "log_all_phases": true' >> /home/redteam/.RedForge/config.json && \
    echo '    }' >> /home/redteam/.RedForge/config.json && \
    echo '}' >> /home/redteam/.RedForge/config.json && \
    chown -R redteam:redteam /home/redteam/.RedForge

# Créer les répertoires utilisateur
RUN mkdir -p /home/redteam/.RedForge/workspace \
    /home/redteam/.RedForge/logs \
    /home/redteam/.RedForge/reports \
    /home/redteam/.RedForge/sessions \
    /home/redteam/.RedForge/wordlists \
    /home/redteam/.RedForge/stealth \
    /home/redteam/.RedForge/apt_operations \
    /home/redteam/.RedForge/persistence && \
    chown -R redteam:redteam /home/redteam/.RedForge

# Configuration TOR (optionnel)
RUN mkdir -p /etc/tor && \
    echo "SocksPort 0.0.0.0:9050" >> /etc/tor/torrc && \
    echo "ControlPort 0.0.0.0:9051" >> /etc/tor/torrc && \
    echo "CookieAuthentication 0" >> /etc/tor/torrc && \
    chmod 644 /etc/tor/torrc

# Exposer les ports (sans commentaires sur la même ligne)
EXPOSE 5000
EXPOSE 8080
EXPOSE 5001
EXPOSE 9050
EXPOSE 4443
EXPOSE 5353/udp

# Healthcheck amélioré
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Changer d'utilisateur
USER redteam
WORKDIR ${REDFORGE_HOME}

# Créer le script d'entrée
RUN echo '#!/bin/bash' > ${REDFORGE_HOME}/entrypoint.sh && \
    echo 'set -e' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo '' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo '# Démarrer TOR si configuré' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo 'if [ "${STEALTH_TOR_ENABLED}" = "true" ]; then' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo '    sudo service tor start' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo '    echo "TOR démarré sur port 9050"' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo 'fi' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo '' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo '# Lancer RedForge' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo 'if [ "${REDFORGE_ENV}" = "production" ]; then' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo '    exec ./run-gunicorn.sh' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo 'else' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo '    exec python bin/RedForge "$@"' >> ${REDFORGE_HOME}/entrypoint.sh && \
    echo 'fi' >> ${REDFORGE_HOME}/entrypoint.sh && \
    chmod +x ${REDFORGE_HOME}/entrypoint.sh

# Point d'entrée
ENTRYPOINT ["/opt/RedForge/entrypoint.sh"]

# Commande par défaut
CMD []