Voici une version améliorée du fichier `CONTRIBUTING.md` pour RedForge v2.0 :

```markdown
# Guide de contribution à RedForge v2.0

Merci de votre intérêt pour contribuer à RedForge ! Ce document fournit les lignes directrices pour contribuer au projet.

## Table des matières

1. [Code de conduite](#code-de-conduite)
2. [Comment contribuer](#comment-contribuer)
3. [Signalement de bugs](#signalement-de-bugs)
4. [Suggestions de fonctionnalités](#suggestions-de-fonctionnalités)
5. [Guide de développement](#guide-de-développement)
6. [Style de code](#style-de-code)
7. [Tests](#tests)
8. [Documentation](#documentation)
9. [Processus de Pull Request](#processus-de-pull-request)
10. [Domaines spécifiques](#domaines-spécifiques)

---

## Code de conduite

Ce projet adhère à un code de conduite. En participant, vous êtes tenu de respecter ce code.

### Principes fondamentaux

- ✅ Utilisez RedForge uniquement pour des tests **autorisés**
- ✅ Ne partagez pas d'informations sensibles (logs, credentials, rapports clients)
- ✅ Respectez la vie privée des autres
- ✅ Signalez les vulnébilités de manière **responsable** via `security@redforge.io`
- ✅ Soyez respectueux et constructif dans les échanges

### Signalement de sécurité

Pour les vulnérabilités de sécurité, **ne pas** ouvrir d'issue publique. Envoyez un email à `security@redforge.io`.

---

## Comment contribuer

### Types de contributions

| Type | Description | Difficulté |
|------|-------------|------------|
| 🐛 **Signalement de bugs** | Décrivez les problèmes rencontrés | Débutant |
| 💡 **Suggestions** | Proposez de nouvelles fonctionnalités | Débutant |
| 📝 **Documentation** | Améliorez la documentation existante | Débutant |
| 🔧 **Code - Bug fix** | Corrigez des bugs | Intermédiaire |
| 🚀 **Code - Feature** | Ajoutez des fonctionnalités | Avancé |
| 🌐 **Traductions** | Ajoutez des traductions (EN, ES, DE) | Intermédiaire |
| 🔒 **Sécurité** | Rapport de vulnérabilités | Expert |
| 🧪 **Tests** | Ajoutez des tests unitaires | Intermédiaire |

### Priorités actuelles

- [ ] Multi-attaques : amélioration du mode parallèle
- [ ] Mode furtif : ajout de techniques de rotation DNS
- [ ] Opérations APT : nouvelles phases (C2, reporting)
- [ ] Interface web : dark mode avancé
- [ ] Documentation : tutoriels vidéo
- [ ] Tests : couverture > 80%

---

## Signalement de bugs

### Avant de signaler

- [ ] Vérifiez que vous utilisez la **dernière version** (`redforge --version`)
- [ ] Recherchez si le bug n'a pas déjà été signalé dans les [issues](https://github.com/Elfried/RedForge/issues)
- [ ] Assurez-vous que c'est un bug et non une erreur d'utilisation
- [ ] Testez avec un environnement propre (Docker recommandé)

### Template de bug

```markdown
## Description du bug
Description claire et concise du problème.

## Reproduction
Étapes pour reproduire :
1. Lancer `redforge -t example.com --stealth high`
2. Exécuter `...`
3. Voir l'erreur

## Comportement attendu
Description de ce qui devrait se passer.

## Comportement actuel
Description de ce qui se passe actuellement.

## Environnement
- OS: [ex: Kali Linux 2024.1]
- Version RedForge: [ex: 2.0.0]
- Python version: [ex: 3.11.4]
- Docker version (si applicable): [ex: 24.0.7]
- Outils installés: [ex: Nmap 7.94, Metasploit 6.4]

## Logs/Output
```text
Copiez les logs ou la sortie d'erreur ici
```

## Configuration
```json
{
    "stealth": {
        "enabled": true,
        "level": "high"
    }
}
```

## Contexte supplémentaire
Ajoutez tout autre contexte pertinent.
```

---

## Suggestions de fonctionnalités

### Template de suggestion

```markdown
## Résumé
Description concise de la fonctionnalité.

## Problème actuel
Quel problème cette fonctionnalité résout-elle ?

## Solution proposée
Description détaillée de la solution.

## Impact utilisateur
Comment les utilisateurs bénéficieront-ils de cette fonctionnalité ?

## Alternatives envisagées
Autres approches considérées.

## Cas d'utilisation
Exemples d'utilisation de la fonctionnalité.

```bash
# Exemple de commande
redforge --new-feature --option value
```

## Implémentation technique
Détails sur l'implémentation (si connu).

## Contexte supplémentaire
Toute information additionnelle.
```

### Idées de fonctionnalités recherchées

| Fonctionnalité | Complexité | Priorité |
|----------------|------------|----------|
| Intégration BloodHound | Élevée | Haute |
| Module C2 personnalisé | Élevée | Haute |
| Export MITRE ATT&CK | Moyenne | Moyenne |
| Plugin Burp Suite | Moyenne | Moyenne |
| Mode furtif DNS-over-HTTPS | Faible | Basse |

---

## Guide de développement

### Prérequis

| Outil | Version | Commande vérification |
|-------|---------|----------------------|
| Python | 3.11+ | `python3 --version` |
| Git | 2.40+ | `git --version` |
| Docker (optionnel) | 24.0+ | `docker --version` |
| Make | 4.0+ | `make --version` |

### Configuration de l'environnement

```bash
# Cloner le dépôt
git clone https://github.com/Elfried002/RedForge.git
cd RedForge

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Installer RedForge en mode développement
pip install -e .

# Vérifier l'installation
redforge --version

# Lancer les tests
make test
```

### Structure du projet v2.0

```
RedForge/
├── bin/                        # Exécutables
│   └── RedForge               # Point d'entrée principal
├── src/
│   ├── core/                  # Cœur de l'application
│   │   ├── cli.py            # Interface CLI
│   │   ├── orchestrator.py   # Moteur d'orchestration
│   │   ├── attack_chainer.py # Chaînage d'attaques
│   │   ├── stealth_manager.py # Mode furtif (NOUVEAU)
│   │   ├── apt_manager.py     # Opérations APT (NOUVEAU)
│   │   └── session_manager.py # Gestion des sessions
│   ├── attacks/               # 8 catégories d'attaques
│   │   ├── injection/        # 7 types
│   │   ├── session/          # 5 types
│   │   ├── cross_site/       # 5 types
│   │   ├── authentication/   # 6 types
│   │   ├── file_system/      # 6 types
│   │   ├── infrastructure/   # 5 types
│   │   ├── integrity/        # 5 types
│   │   └── advanced/         # 7 types
│   ├── connectors/            # 20 connecteurs d'outils
│   ├── stealth/               # Module furtif (NOUVEAU)
│   │   ├── tor_manager.py    # Gestion TOR
│   │   ├── proxy_rotator.py  # Rotation proxies
│   │   ├── user_agent.py     # User-Agents aléatoires
│   │   └── delay_jitter.py   # Délais variables
│   ├── multi_attack/          # Multi-attaques (NOUVEAU)
│   │   ├── sequential.py     # Mode séquentiel
│   │   ├── parallel.py       # Mode parallèle
│   │   └── queue_manager.py  # Gestion des files
│   ├── apt/                   # Opérations APT (NOUVEAU)
│   │   ├── phases/           # Phases APT
│   │   ├── persistence/      # Mécanismes de persistance
│   │   ├── lateral_movement/ # Mouvement latéral
│   │   └── exfiltration/     # Exfiltration de données
│   ├── web_interface/         # Interface web (Flask)
│   │   ├── templates/        # Templates HTML
│   │   ├── static/           # CSS, JS, images
│   │   └── app.py            # Application Flask
│   └── i18n/                 # Internationalisation
├── tests/                     # Tests unitaires
│   ├── test_core/
│   ├── test_attacks/
│   ├── test_stealth/         # Tests mode furtif (NOUVEAU)
│   ├── test_multi_attack/    # Tests multi-attaques (NOUVEAU)
│   └── test_apt/             # Tests opérations APT (NOUVEAU)
├── docs/                      # Documentation
├── examples/                  # Exemples d'utilisation
└── scripts/                   # Scripts utilitaires
```

---

## Style de code

### Python (PEP 8)

| Règle | Description |
|-------|-------------|
| **Indentation** | 4 espaces (pas de tabulations) |
| **Longueur ligne** | Maximum 100 caractères |
| **Docstrings** | Obligatoires pour classes et fonctions publiques |
| **Nommage** | `snake_case` pour fonctions/variables, `PascalCase` pour classes |
| **Imports** | Un par ligne, groupés (standard → tiers → local) |
| **Typage** | Annotations de type recommandées |

#### Exemple

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de gestion du mode furtif.

Ce module fournit les classes et fonctions pour le mode furtif avancé.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

import requests
from src.core.config import Config


@dataclass
class StealthConfig:
    """Configuration du mode furtif."""
    
    enabled: bool = False
    level: str = "medium"
    random_user_agents: bool = True
    use_tor: bool = False
    min_delay: float = 0.5
    max_delay: float = 3.0
    
    def get_delay(self) -> float:
        """
        Calcule un délai aléatoire entre min_delay et max_delay.
        
        Returns:
            Délai en secondes.
        """
        import random
        return random.uniform(self.min_delay, self.max_delay)
```

### JavaScript (ES6)

| Règle | Description |
|-------|-------------|
| **Indentation** | 2 espaces |
| **Variables** | `const` et `let` (pas de `var`) |
| **Fonctions** | Arrow functions quand approprié |
| **Nommage** | `camelCase` pour variables/fonctions, `PascalCase` pour classes |
| **Semi-colons** | Obligatoires |

#### Exemple

```javascript
// dashboard.js
class Dashboard {
    constructor() {
        this.refreshInterval = null;
        this.data = {};
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/dashboard/stats');
            const stats = await response.json();
            this.updateStats(stats);
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    updateStats(stats) {
        const elements = ['total-targets', 'total-attacks'];
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.textContent = stats[id] || 0;
        });
    }
}
```

### CSS

| Règle | Description |
|-------|-------------|
| **Indentation** | 2 espaces |
| **Méthodologie** | BEM (Block Element Modifier) |
| **Organisation** | Par composant |
| **Variables** | Utiliser les variables CSS |

#### Exemple

```css
/* Stealth panel */
.stealth-panel {
    --panel-bg: var(--gray-100);
    --panel-border: var(--gray-300);
}

.stealth-panel__header {
    padding: 1rem;
    border-bottom: 1px solid var(--panel-border);
}

.stealth-panel__content {
    padding: 1rem;
}

.stealth-panel--active {
    --panel-bg: rgba(156, 39, 176, 0.1);
    --panel-border: #9c27b0;
}
```

---

## Tests

### Types de tests

| Type | Description | Framework |
|------|-------------|-----------|
| **Unitaires** | Test des fonctions individuelles | `pytest` |
| **Intégration** | Test des interactions entre modules | `pytest` |
| **Fonctionnels** | Test des fonctionnalités complètes | `pytest` |
| **Performance** | Test des performances | `pytest-benchmark` |
| **Sécurité** | Test des vulnérabilités | `bandit`, `safety` |

### Exécution des tests

```bash
# Tous les tests
make test

# Tests spécifiques
pytest tests/test_stealth/
pytest tests/test_multi_attack/test_sequential.py

# Avec couverture
make test-cov
# ou
pytest --cov=src --cov-report=html --cov-report=term tests/

# Tests de performance
pytest tests/test_performance.py --benchmark-only

# Tests de sécurité
bandit -r src/
safety check -r requirements.txt
```

### Écrire des tests

```python
import pytest
from src.stealth.stealth_manager import StealthManager


class TestStealthManager:
    """Tests pour le module de mode furtif."""
    
    @pytest.fixture
    def stealth_manager(self):
        """Fixture pour StealthManager."""
        return StealthManager()
    
    def test_initialization(self, stealth_manager):
        """Test l'initialisation du mode furtif."""
        assert stealth_manager.enabled is False
        assert stealth_manager.level == "medium"
    
    def test_enable_stealth(self, stealth_manager):
        """Test l'activation du mode furtif."""
        stealth_manager.enable(level="high")
        assert stealth_manager.enabled is True
        assert stealth_manager.level == "high"
    
    @pytest.mark.parametrize("level,expected_delay", [
        ("low", (0.1, 1.0)),
        ("medium", (0.5, 2.0)),
        ("high", (1.0, 5.0)),
        ("paranoid", (2.0, 10.0)),
    ])
    def test_delay_ranges(self, stealth_manager, level, expected_delay):
        """Test les plages de délais pour chaque niveau."""
        stealth_manager.enable(level=level)
        for _ in range(10):
            delay = stealth_manager.get_delay()
            assert expected_delay[0] <= delay <= expected_delay[1]
    
    @pytest.mark.asyncio
    async def test_async_operations(self, stealth_manager):
        """Test les opérations asynchrones."""
        await stealth_manager.start()
        assert stealth_manager.running is True
        await stealth_manager.stop()
        assert stealth_manager.running is False
```

---

## Documentation

### Types de documentation

| Type | Format | Outil |
|------|--------|-------|
| **Docstrings** | Google style | Sphinx |
| **README** | Markdown | - |
| **User Guide** | Markdown/HTML | MkDocs |
| **API Reference** | RST | Sphinx |
| **Tutoriels** | Markdown | - |

### Génération de documentation

```bash
# Installer les outils
pip install sphinx sphinx-rtd-theme mkdocs

# Générer la documentation Sphinx
cd docs
make html

# Générer la documentation MkDocs
mkdocs build

# Serveur de documentation local
mkdocs serve
```

### Template de docstring

```python
def scan_target(target: str, stealth: bool = False) -> Dict[str, Any]:
    """
    Scanne une cible pour détecter les vulnérabilités.
    
    Args:
        target: URL ou IP de la cible.
        stealth: Active le mode furtif si True.
    
    Returns:
        Dictionnaire contenant les vulnérabilités détectées.
    
    Raises:
        ConnectionError: Si la cible est inaccessible.
        ValueError: Si le format de la cible est invalide.
    
    Example:
        >>> result = scan_target("https://example.com", stealth=True)
        >>> print(result["vulnerabilities"])
        [{"type": "XSS", "severity": "high"}]
    """
    # Implémentation
    pass
```

---

## Processus de Pull Request

### Étapes

1. **Fork** le dépôt sur GitHub
2. **Clone** votre fork : `git clone https://github.com/votre-username/RedForge.git`
3. **Créez une branche** : `git checkout -b feature/ma-fonctionnalite`
4. **Faites vos modifications** en suivant les règles de style
5. **Testez** : `make test`
6. **Committez** avec un message clair
7. **Pushez** : `git push origin feature/ma-fonctionnalite`
8. **Créez une Pull Request** sur GitHub

### Convention de commits

```
type(scope): description courte

Description détaillée si nécessaire.
Corps du message expliquant le quoi et le pourquoi.

Fixes #123
```

**Types :**

| Type | Description |
|------|-------------|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `docs` | Documentation |
| `style` | Formatage (espace, virgules, etc.) |
| `refactor` | Refactorisation du code |
| `test` | Ajout ou modification de tests |
| `chore` | Maintenance (dépendances, config) |
| `security` | Correction de sécurité |

**Exemples :**

```text
feat(stealth): ajout de la rotation de proxies

Ajoute la fonctionnalité de rotation automatique de proxies
pour le mode furtif. Supporte HTTP, HTTPS et SOCKS5.

Ajoute la classe ProxyRotator avec les méthodes :
- add_proxy()
- rotate()
- get_current()

Closes #456
```

```text
fix(multi-attack): correction du mode parallèle

Corrige un bug où les threads ne s'arrêtaient pas correctement
en cas d'erreur.

Ajoute un timeout global de 300 secondes.
```

### Checklist PR

Avant de soumettre une PR, vérifiez :

- [ ] Le code suit le style du projet
- [ ] Des tests ont été ajoutés pour les nouvelles fonctionnalités
- [ ] Tous les tests passent (`make test`)
- [ ] La documentation a été mise à jour
- [ ] Le commit message est clair et suit la convention
- [ ] La PR cible la branche `develop` (pas `main`)
- [ ] La PR n'introduit pas de breaking changes (ou est documentée)
- [ ] Les dépendances ajoutées sont compatibles avec la licence GPLv3

### Relecture de code

Les PR seront relues par les mainteneurs. Soyez prêt à :

- ✅ Répondre aux questions dans les commentaires
- ✅ Faire des modifications si nécessaire
- ✅ Discuter des implémentations alternatives
- ✅ Rester courtois et constructif

---

## Domaines spécifiques

### Contribution au mode furtif

```bash
# Zone du code
src/stealth/
tests/test_stealth/

# Technologies à maîtriser
- TOR / SOCKS
- Rotation de proxies
- User-Agents
- Délais et jitter
- DNS-over-HTTPS
```

### Contribution aux multi-attaques

```bash
# Zone du code
src/multi_attack/
tests/test_multi_attack/

# Technologies à maîtriser
- Programmation concurrente
- Threading / Async
- Files d'attente
- Gestion des erreurs
```

### Contribution aux opérations APT

```bash
# Zone du code
src/apt/
tests/test_apt/

# Technologies à maîtriser
- MITRE ATT&CK framework
- Persistance Windows/Linux
- Mouvement latéral (SMB, WMI, SSH)
- Exfiltration (DNS, HTTP, custom)
```

### Contribution à l'interface web

```bash
# Zone du code
src/web_interface/
src/web_interface/templates/
src/web_interface/static/

# Technologies à maîtriser
- Flask
- Socket.IO
- JavaScript (ES6)
- CSS (Flexbox, Grid)
- Chart.js
```

---

## Questions ?

| Canal | Adresse |
|-------|---------|
| **Issues** | https://github.com/Elfried002/RedForge/issues |
| **Email** | elfriedyobouet@gmail.com |

---

**Merci de contribuer à RedForge v2.0 ! 🔴**

---

<div align="center">

*"Forgez vos attaques, maîtrisez vos cibles"*

Made with ❤️ by the RedForge Team

</div>
```