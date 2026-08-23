Title: Guide complet — MarkEdit
Author: Michel Maillard
Created: 2026-04-27
Updated: 2026-07-01
Tags: tutoriel, guide, markdown, référence
Description: Documentation complète de toutes les fonctionnalités de l'application.

# Guide complet — MarkEdit

MarkEdit est un éditeur et visualiseur de fichiers Markdown avec rendu HTML en temps réel, gestion des métadonnées, export et impression.

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

### Navigation entre fichiers liés

Dans l'aperçu, un lien pointant vers un fichier Markdown local (`.md`, `.markdown`, `.mkd`) l'ouvre directement dans la fenêtre. Si le lien comporte une ancre — `guide.md#installation` —, l'aperçu se positionne sur la section correspondante.

**Fichier → Précédent** `Alt+Left` revient au fichier précédemment ouvert ; les retours successifs remontent tout l'historique de la session.

Les autres liens ne sont pas concernés : les ancres `#section` défilent dans l'aperçu, et tout le reste — adresses web, `mailto:`, PDF, images — s'ouvre dans l'application système associée.

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

## Panneau latéral `F8`

Le panneau latéral (ancrable à gauche ou à droite) regroupe deux sections :

### Métadonnées

Affiche les métadonnées présentes en tête du fichier (voir section *Métadonnées* ci-dessous). Les valeurs sont mises à jour automatiquement pendant la frappe. Les tags s'affichent sous forme de **badges** colorés.

### Table des matières

Liste les titres de niveau 1 (`#`) et 2 (`##`) du document. Un clic sur un titre :

- déplace le curseur dans l'**éditeur** (tous modes)
- fait défiler la **vue rendue** jusqu'au titre (modes Affichage et Partagé)

## Thèmes et présentation

### Thèmes `Outils → Thème`

Cinq thèmes de présentation, sélectionnables comme un groupe exclusif (un seul actif à la fois) :

| Thème | Police | Fond | Usage |
|-------|--------|------|-------|
| **Classique** | Segoe UI | Blanc | Usage général |
| **Minimaliste** | System UI | Blanc | Documents épurés |
| **Sérif** | Georgia | Papier chaud | Articles, prose |
| **Compact** | Segoe UI | Blanc | Documents denses |
| **Sombre** | Segoe UI | Sombre (Catppuccin Mocha) | Travail en faible luminosité |

Sélectionner **Sombre** bascule l'ensemble de l'interface (fenêtre, éditeur, panneau latéral) et le rendu vers ce thème sombre ; la coloration syntaxique de l'éditeur s'adapte également. `F9` passe au thème suivant dans cette liste (y compris Sombre), pratique pour basculer rapidement au clavier sans ouvrir le menu.

### Largeur du contenu `Outils → Largeur`

| Option | Valeur | Usage |
|--------|--------|-------|
| Étroit | 640 px | Lecture sur petit écran |
| Normal | 860 px | Largeur par défaut |
| Large | 1100 px | Tableaux et contenus larges |
| Pleine largeur | Aucune limite | Dashboards, données |

`F10` passe à la largeur suivante dans cette liste. Les tableaux et blocs de code trop larges défilent horizontalement quel que soit le réglage de largeur.

Un changement de thème ou de largeur préserve la position de défilement actuelle dans la vue rendue.

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

## Aide au formatage Markdown

En mode Édition ou Partagé, une mini barre d'icônes apparaît au-dessus de l'éditeur ; chaque icône affiche son raccourci entre parenthèses au survol.

### Raccourcis de formatage

| Raccourci | Action |
|-----------|--------|
| `Ctrl+B` | Gras |
| `Ctrl+I` | Italique |
| `Ctrl+Shift+X` | Barré |
| `Ctrl+Shift+C` | Code inline |
| `Ctrl+Shift+H` | Surligné (`==texte==`) |
| `Ctrl+K` | Lien |
| `Ctrl+Shift+8` | Liste à puces |
| `Ctrl+Shift+7` | Liste numérotée |
| `Ctrl+Shift+T` | Liste de tâches |
| `Ctrl+Shift+9` | Citation |

Ces actions entourent le texte sélectionné (ou l'insèrent au point du curseur si rien n'est sélectionné) et fonctionnent comme des **interrupteurs** : les réappliquer sur une sélection déjà formatée retire le formatage.

### Bloc de code avec choix du langage

Le bouton **Code ▾** de la mini barre d'outils ouvre un menu de langages (Python, JavaScript, Bash, JSON, HTML, CSS, SQL…). En sélectionner un insère un bloc fencé avec la balise ouvrante et fermante, curseur prêt à taper le code (ou le contenu sélectionné y est déplacé).

### Continuation automatique des listes

Appuyer sur `Entrée` dans une liste à puces, numérotée ou de tâches insère automatiquement le bon préfixe sur la ligne suivante (en incrémentant les listes numérotées). Appuyer sur `Entrée` sur un élément de liste vide en sort proprement (le préfixe est retiré au lieu d'ajouter une nouvelle puce).

### Auto-fermeture

- Taper `*`, `_`, `` ` ``, `[` ou `(` insère automatiquement le caractère de fermeture correspondant (ou entoure la sélection existante).
- Taper `>` pour fermer une balise HTML ouverte (ex. `<div>`) insère automatiquement la balise fermante correspondante ; les éléments auto-fermants (`<br>`, `<img>`…) et les balises déjà auto-fermées (`<img/>`) ne sont pas affectés.

### Indentation automatique

Appuyer sur `Entrée` conserve l'indentation de la ligne précédente, utile notamment pour l'édition de YAML. Dans un bloc de code (ex. ` ```css `), taper `{` insère une ligne indentée avec `}` en dessous, sans affecter la syntaxe d'attributs Markdown (`{#id .classe}`) en dehors des blocs de code.

## Cases à cocher interactives

En mode Affichage ou Partagé, cliquer sur une case à cocher d'une liste de tâches bascule directement `[ ]` / `[x]` dans le document source — pas besoin de repasser en mode Édition.

## Métadonnées

Le format de métadonnées est celui de l'extension `meta` de Python-Markdown : des lignes `Clé: valeur` en tête du fichier, avant tout contenu, séparées du reste par une ligne vide.

### Champs reconnus et ordre d'affichage

| Champ | Libellé affiché | Description |
|-------|------------------|-------------|
| `type` | Type | note / tâche / journal / référence (liste fermée) |
| `title` | Titre | Titre du document |
| `description` | Description | Résumé en une phrase |
| `author` | Auteur | Nom de l'auteur |
| `tags` | Tags | Liste de mots-clés séparés par des virgules |
| `created` | Créé | Date de création |
| `timestamp` | Mis à jour | Date de dernière modification |

L'ancien champ `updated` reste reconnu et affiché sous le même libellé « Mis à jour », pour les documents créés avant l'introduction de `timestamp`.

### Exemple de bloc de métadonnées

```
Type: note
Title: Mon document
Description: Résumé du contenu.
Author: Prénom Nom
Tags: rapport, projet, draft
Created: 2026-01-15
Timestamp: 2026-07-01

# Premier titre
...
```

### Modifier les métadonnées `Ctrl+Shift+M`

Ouvre un formulaire pré-rempli, dans l'ordre du tableau ci-dessus :

| Champ | Source par défaut |
|-------|-------------------|
| Type | Liste déroulante fermée (note / tâche / journal / référence), vide par défaut |
| Titre | Nom du fichier (reformaté) |
| Description | Vide |
| Auteur | Dernier auteur saisi ou `git config user.name` |
| Tags | Vide (virgule-séparés) |
| Créé le | Date de création du fichier (`st_birthtime` si disponible, sinon date de modification) |
| Mis à jour le | Date de dernière modification du fichier (`st_mtime`), ou valeur existante de `timestamp`/`updated` |

Si un bloc de métadonnées existe déjà, ses valeurs sont reprises dans le formulaire. À la validation, il est remplacé.

L'auteur saisi est mémorisé pour les sessions suivantes.

## Menu Aide

- **Tutoriel…** — ouvre ce guide directement dans l'application
- **Référence Markdown…** — ouvre le document de référence des syntaxes prises en charge
- **À propos de MarkEdit…** — affiche le nom, la version et l'auteur de l'application

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
| Saut de ligne | deux espaces en fin de ligne |
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
| `Alt+Left` | Fichier précédent |
| `Ctrl+S` | Enregistrer |
| `Ctrl+Shift+S` | Enregistrer sous |
| `Ctrl+E` | Exporter HTML |
| `Ctrl+Shift+E` | Exporter PDF |
| `Ctrl+P` | Imprimer |
| `Ctrl+Q` | Quitter |
| `Ctrl+F` | Rechercher |
| `Ctrl+H` | Remplacer |
| `Ctrl+B` | Gras |
| `Ctrl+I` | Italique |
| `Ctrl+Shift+X` | Barré |
| `Ctrl+Shift+C` | Code |
| `Ctrl+Shift+H` | Surligné |
| `Ctrl+K` | Lien |
| `Ctrl+Shift+8` | Liste à puces |
| `Ctrl+Shift+7` | Liste numérotée |
| `Ctrl+Shift+T` | Liste de tâches |
| `Ctrl+Shift+9` | Citation |
| `F5` | Mode Affichage |
| `F6` | Mode Édition |
| `F7` | Mode Partagé |
| `F8` | Panneau latéral |
| `F9` | Thème suivant |
| `F10` | Largeur suivante |
| `Ctrl+Shift+M` | Modifier les métadonnées |
| `Ctrl++` | Zoom avant |
| `Ctrl+-` | Zoom arrière |
| `Ctrl+0` | Zoom normal |
| `Échap` | Fermer la recherche |

Chaque icône de la barre d'outils affiche son raccourci entre parenthèses au survol.
