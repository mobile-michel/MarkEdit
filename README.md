# MarkEdit

Éditeur et visualiseur Markdown pour Linux, avec rendu HTML en temps réel, écrit en Python (PyQt6 + QWebEngine).

![Version](https://img.shields.io/badge/version-3.3-blue)

## Fonctionnalités

- **Trois modes** : Affichage, Édition, Partagé (`F5` / `F6` / `F7`)
- **Cinq thèmes de présentation** dont un thème Sombre, cycle rapide avec `F9`
- **Largeurs de contenu** ajustables, cycle rapide avec `F10`
- **Aide au formatage Markdown** en mode Édition : raccourcis clavier (gras, italique, liens, listes…), mini barre d'outils, continuation automatique des listes, auto-fermeture des paires et des balises HTML, blocs de code avec choix du langage, indentation automatique
- **Cases à cocher interactives** dans les listes de tâches, cliquables directement en mode Affichage
- **Métadonnées** en tête de document (type, titre, description, auteur, tags, dates), éditables via un formulaire dédié et affichées dans un panneau latéral
- **Table des matières** générée automatiquement, navigable depuis le panneau latéral
- **Recherche et remplacement**, y compris dans le rendu HTML
- **Export** en HTML autonome et en PDF, ainsi que l'impression
- **Coloration syntaxique** des blocs de code via Pygments
- Prise en charge de tableaux, notes de bas de page, listes de définitions, attributs HTML, admonitions, texte surligné/barré, et plus — voir [markdown-reference.md](markdown-reference.md)

## Installation

```bash
git clone https://github.com/mobile-michel/MarkEdit.git
cd MarkEdit
./install.sh
```

Le script crée un environnement virtuel Python dédié, installe les dépendances (PyQt6, PyQt6-WebEngine, markdown, Pygments, pymdown-extensions), copie l'application et sa documentation, installe l'icône, et enregistre un lanceur dans le menu des applications.

Pour désinstaller :

```bash
./uninstall.sh
```

## Utilisation

Depuis le menu des applications (« MarkEdit »), ou en ligne de commande :

```bash
/home/michel/.local/opt/MarkEdit/.venv/bin/python3 /home/michel/.local/opt/MarkEdit/markdown_app.py [fichier.md]
```

## Documentation

- [tutoriel.md](tutoriel.md) — guide complet des fonctionnalités de l'application
- [markdown-reference.md](markdown-reference.md) — référence de toutes les syntaxes Markdown prises en charge

Ces deux documents sont aussi accessibles directement depuis le menu **Aide** de l'application.

## Prérequis

- Linux avec un environnement de bureau (testé sous KDE Plasma)
- Python 3.12+

## Auteur

Michel Maillard
