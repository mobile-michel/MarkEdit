Title: Guide complet — Markdown Viewer
Author: Michel Maillard
Created: 2026-04-27
Updated: 2026-04-27
Tags: tutoriel, guide, markdown, référence
Description: Documentation complète de toutes les fonctionnalités de l'application.

# Guide complet — Markdown Viewer

Markdown Viewer est un éditeur et visualiseur de fichiers Markdown avec rendu HTML en temps réel, gestion des métadonnées, export et impression.

## Modes d'affichage

L'application propose trois modes accessibles depuis la barre d'outils ou le menu **Affichage** :

| Mode | Raccourci | Description |
|------|-----------|-------------|
| Affichage | `F5` | Rendu HTML uniquement |
| Édition | `F6` | Éditeur de texte uniquement |
| Partagé | `F7` | Éditeur et rendu côte à côte |

En mode **Partagé**, le rendu se met à jour automatiquement 300 ms après chaque frappe.

## Gestion des fichiers

### Opérations de base

- **Nouveau** `Ctrl+N` — crée un document vide
- **Ouvrir** `Ctrl+O` — ouvre un fichier `.md`, `.markdown`, `.mkd` ou `.txt`
- **Enregistrer** `Ctrl+S` — enregistre le fichier courant
- **Enregistrer sous** `Ctrl+Shift+S` — enregistre sous un nouveau nom
- **Quitter** `Ctrl+Q` — ferme l'application (propose d'enregistrer si nécessaire)

### Fichiers récents

Le menu **Fichier → Fichiers récents** conserve les 10 derniers fichiers ouverts. Un clic ouvre directement le fichier. L'option *Effacer l'historique* vide la liste.

### Glisser-déposer

Il est possible de faire glisser un fichier Markdown depuis le gestionnaire de fichiers directement dans la fenêtre pour l'ouvrir.

### Rechargement automatique

Si le fichier est modifié par un autre programme pendant qu'il est ouvert, l'application propose de le recharger.

## Export et impression

| Action | Raccourci | Description |
|--------|-----------|-------------|
| Exporter en HTML | `Ctrl+E` | Fichier HTML autonome (CSS intégré) |
| Exporter en PDF | `Ctrl+Shift+E` | Fichier PDF prêt à diffuser |
| Imprimer | `Ctrl+P` | Impression via le dialogue système |

L'export HTML produit un fichier utilisable dans n'importe quel navigateur, avec la feuille de style du thème actif intégrée.

## Recherche et remplacement

### Rechercher `Ctrl+F`

La barre de recherche s'affiche en bas de la fenêtre :

- Les occurrences sont surlignées en **jaune**, l'occurrence courante en **orange**
- `Entrée` ou `▼` — occurrence suivante
- `Shift+Entrée` ou `▲` — occurrence précédente
- Case **Casse** — recherche sensible à la casse
- `Échap` — ferme la barre

En mode Affichage ou Partagé, la recherche opère dans le rendu HTML via le moteur WebEngine.

### Remplacer `Ctrl+H`

La ligne de remplacement apparaît sous la barre de recherche :

- **Remplacer** — remplace l'occurrence courante
- **Tout remplacer** — remplace toutes les occurrences dans le document

## Panneau latéral `F9`

Le panneau latéral (ancrable à gauche ou à droite) regroupe deux sections :

### Métadonnées

Affiche les métadonnées présentes en tête du fichier (voir section *Métadonnées* ci-dessous). Les valeurs sont mises à jour automatiquement pendant la frappe. Les tags s'affichent sous forme de **badges** colorés.

### Table des matières

Liste les titres de niveau 1 (`#`) et 2 (`##`) du document. Un clic sur un titre :

- déplace le curseur dans l'**éditeur** (tous modes)
- fait défiler la **vue rendue** jusqu'au titre (modes Affichage et Partagé)

## Thèmes et présentation

### Thèmes `Outils → Thème`

Quatre thèmes de présentation pour le mode Affichage :

| Thème | Police | Fond | Usage |
|-------|--------|------|-------|
| **Classique** | Segoe UI | Blanc | Usage général |
| **Minimaliste** | System UI | Blanc | Documents épurés |
| **Sérif** | Georgia | Papier chaud | Articles, prose |
| **Compact** | Segoe UI | Blanc | Documents denses |

### Largeur du contenu `Outils → Largeur`

| Option | Valeur | Usage |
|--------|--------|-------|
| Étroit | 640 px | Lecture sur petit écran |
| Normal | 860 px | Largeur par défaut |
| Large | 1100 px | Tableaux et contenus larges |
| Pleine largeur | Aucune limite | Dashboards, données |

Les tableaux et blocs de code trop larges défilent horizontalement quel que soit le réglage de largeur.

### Mode sombre `F8`

Bascule l'interface et le rendu vers un thème sombre (Catppuccin Mocha). La coloration syntaxique de l'éditeur s'adapte également.

## Zoom

Applicable à la vue rendue :

| Action | Raccourci |
|--------|-----------|
| Zoom avant | `Ctrl++` |
| Zoom arrière | `Ctrl+-` |
| Zoom normal (100 %) | `Ctrl+0` |
| Zoom molette | `Ctrl+Molette` |

Le niveau de zoom est mémorisé entre les sessions.

## Éditeur

### Fonctionnalités

- **Numéros de ligne** affichés dans la marge gauche
- **Coloration syntaxique Markdown** : titres, gras, italique, code, liens, citations, listes — adaptée au mode sombre
- **Surbrillance de la ligne courante** (fond légèrement coloré)
- Tabulation réglée à 4 espaces

### Statistiques

La barre de statut affiche en permanence :

```
N mots · N car. · ~N min
```

Le temps de lecture est estimé à 200 mots par minute.

## Métadonnées

Le format de métadonnées est celui de l'extension `meta` de Python-Markdown : des lignes `Clé: valeur` en tête du fichier, avant tout contenu, séparées du reste par une ligne vide.

### Exemple de bloc de métadonnées

```
Title: Mon document
Author: Prénom Nom
Created: 2026-01-15
Updated: 2026-04-27
Tags: rapport, projet, draft
Description: Résumé du contenu.

# Premier titre
...
```

### Générer les métadonnées `Ctrl+Shift+M`

Ouvre un formulaire pré-rempli :

| Champ | Source par défaut |
|-------|-------------------|
| Titre | Nom du fichier (reformaté) |
| Auteur | Dernier auteur saisi ou `git config user.name` |
| Créé le | Date de création du fichier (`st_birthtime` si disponible, sinon date de modification) |
| Mis à jour le | Date de dernière modification du fichier (`st_mtime`) |
| Tags | Vide (virgule-séparés) |
| Description | Vide |

Si un bloc de métadonnées existe déjà, ses valeurs sont reprises dans le formulaire. À la validation, il est remplacé.

L'auteur saisi est mémorisé pour les sessions suivantes.

### Voir les métadonnées `Ctrl+M`

Affiche un tableau de toutes les métadonnées du document. Les champs avec plusieurs valeurs (ex. tags) sont présentés sous forme de **badges** colorés.

## Persistance entre sessions

L'application mémorise automatiquement :

- Taille et position de la fenêtre
- Position du séparateur en mode Partagé
- Niveau de zoom
- Thème et largeur de contenu sélectionnés
- Dernier auteur saisi dans le formulaire de métadonnées
- Liste des fichiers récents

## Syntaxe Markdown supportée

| Élément | Syntaxe |
|---------|---------|
| Titres | `# H1` `## H2` `### H3` … |
| Gras | `**texte**` ou `__texte__` |
| Italique | `*texte*` ou `_texte_` |
| Code inline | `` `code` `` |
| Bloc de code | ```` ``` ```` (avec langue optionnelle) |
| Lien | `[texte](url)` |
| Image | `![alt](url)` |
| Tableau | Syntaxe GFM (pipes) |
| Citation | `> texte` |
| Liste à puces | `- item` ou `* item` |
| Liste numérotée | `1. item` |
| Case à cocher | `- [ ] tâche` / `- [x] faite` |
| Note de bas de page | `[^1]` / `[^1]: note` |
| Ligne horizontale | `---` |
| Table des matières | `[TOC]` |

La coloration syntaxique des blocs de code utilise **Pygments** et supporte des dizaines de langages.

## Raccourcis clavier — récapitulatif

| Raccourci | Action |
|-----------|--------|
| `Ctrl+N` | Nouveau fichier |
| `Ctrl+O` | Ouvrir |
| `Ctrl+S` | Enregistrer |
| `Ctrl+Shift+S` | Enregistrer sous |
| `Ctrl+E` | Exporter HTML |
| `Ctrl+Shift+E` | Exporter PDF |
| `Ctrl+P` | Imprimer |
| `Ctrl+Q` | Quitter |
| `Ctrl+F` | Rechercher |
| `Ctrl+H` | Remplacer |
| `F5` | Mode Affichage |
| `F6` | Mode Édition |
| `F7` | Mode Partagé |
| `F8` | Mode sombre |
| `F9` | Panneau latéral |
| `Ctrl+M` | Voir les métadonnées |
| `Ctrl+Shift+M` | Générer les métadonnées |
| `Ctrl++` | Zoom avant |
| `Ctrl+-` | Zoom arrière |
| `Ctrl+0` | Zoom normal |
| `Échap` | Fermer la recherche |
