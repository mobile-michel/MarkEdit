---
title: Référence Markdown
author: MarkEdit
date: 2026-07-01
tags: référence, markdown, syntaxe
---

# Référence Markdown

Ce document recense toutes les syntaxes prises en charge par **MarkEdit**, basé sur la bibliothèque **Python-Markdown 3.10.2** et **PyMdown Extensions 11.0** avec les extensions activées listées ci-dessous.

---

## Variante de Markdown la plus proche

Ce viewer se rapproche le plus de **Markdown Extra** (PHP Markdown Extra, Michel Fortin), dont il partage les fonctionnalités centrales : tableaux, blocs de code délimités, notes de bas de page, listes de définitions et attributs HTML. Il emprunte également à **GFM** (GitHub Flavored Markdown) les cases à cocher et la conversion des sauts de ligne.

### Comparaison avec les principales variantes

| Fonctionnalité                     | Ce viewer | Markdown Extra | GFM (GitHub) | CommonMark | Pandoc |
|------------------------------------|:---------:|:--------------:|:------------:|:----------:|:------:|
| Syntaxe de base (Gruber)           | ✅        | ✅             | ✅           | ✅         | ✅     |
| Tableaux                           | ✅        | ✅             | ✅           | ❌         | ✅     |
| Blocs de code ` ``` `              | ✅        | ✅             | ✅           | ✅         | ✅     |
| Coloration syntaxique              | ✅        | ❌             | ✅           | ❌         | ✅     |
| Notes de bas de page               | ✅        | ✅             | ❌           | ❌         | ✅     |
| Listes de définitions              | ✅        | ✅             | ❌           | ❌         | ✅     |
| Attributs HTML `{#id .classe}`     | ✅        | ✅             | ❌           | ❌         | ✅     |
| Métadonnées (en-tête)              | ✅        | ❌             | ❌           | ❌         | ✅     |
| Cases à cocher `[ ]` / `[x]`      | ✅        | ❌             | ✅           | ❌         | ✅     |
| Blocs d'avertissement (admonition) | ✅        | ❌             | ❌           | ❌         | ❌     |
| Table des matières `[TOC]`         | ✅        | ✅             | ❌           | ❌         | ✅     |
| Sauts de ligne → `<br>`            | ✅        | ❌             | ✅           | ❌         | ❌     |
| Typographie (`--`, `"..."`)        | ✅        | ❌             | ❌           | ❌         | ✅     |
| Texte surligné `==texte==`         | ✅        | ❌             | ❌           | ❌         | ✅     |
| ~~Texte barré~~                    | ✅        | ❌             | ✅           | ❌         | ✅     |
| Abréviations `*[HTML]: ...`        | ❌        | ✅             | ❌           | ❌         | ❌     |
| Autolinks bruts `https://...`      | ❌        | ❌             | ✅           | ✅         | ✅     |
| Formules mathématiques LaTeX       | ❌        | ❌             | ❌           | ❌         | ✅     |
| Citations bibliographiques         | ❌        | ❌             | ❌           | ❌         | ✅     |
| Tableaux en grille (grid tables)   | ❌        | ❌             | ❌           | ❌         | ✅     |
| Émojis `:smile:`                   | ❌        | ❌             | ✅           | ❌         | ❌     |

### Ce que chaque variante apporte en plus

**GFM (GitHub Flavored Markdown)**
- Texte barré : `~~barré~~`
- Autolinks bruts : une URL seule est cliquable sans crochets
- Émojis shortcodes : `:smile:` `:warning:`
- Mentions `@utilisateur` et références `#123` (spécifiques à GitHub)

**CommonMark**
- Spécification stricte et sans ambiguïté (règles de précédence précises)
- Autolinks étendus
- Comportement garanti identique entre toutes les implémentations conformes

**Pandoc Markdown**
- Formules mathématiques inline `$E = mc^2$` et en bloc `$$...$$`
- Citations bibliographiques `[@auteur2020]` avec génération de bibliographie
- Tableaux en grille (cellules multi-lignes)
- Métadonnées YAML complètes (listes, objets imbriqués)
- Blocs `<div>` via syntaxe `:::` (équivalent des admonitions mais plus général)
- Texte barré, exposant `x^2^`, indice `H~2~O`
- Conversion vers des dizaines de formats (PDF, DOCX, EPUB, LaTeX…)

**Markdown Extra** (fonctionnalité absente ici)
- Abréviations : `*[HTML]: HyperText Markup Language` — toutes les occurrences dans le texte deviennent des `<abbr>`

---

## Extensions activées

| Extension       | Rôle                                              |
|-----------------|---------------------------------------------------|
| `tables`        | Tableaux GFM                                      |
| `fenced_code`   | Blocs de code délimités par ` ``` `               |
| `codehilite`    | Coloration syntaxique (Pygments)                  |
| `toc`           | Table des matières automatique                    |
| `nl2br`         | Saut de ligne = `<br>` (comme GFM)                |
| `sane_lists`    | Listes cohérentes (mélange ordonné/non-ordonné)   |
| `smarty`        | Guillemets typographiques et tirets               |
| `attr_list`     | Attributs HTML sur les éléments (`{#id .classe}`) |
| `def_list`      | Listes de définitions                             |
| `footnotes`     | Notes de bas de page                             |
| `admonition`    | Blocs d'avertissement (`note`, `warning`…)        |
| `meta`          | Métadonnées YAML en tête de fichier               |
| `pymdownx.mark` | Texte surligné `==texte==`                        |
| `pymdownx.tilde`| Texte barré `~~texte~~`                           |

En plus des extensions, l'application convertit automatiquement les **cases à cocher** (`[ ]` / `[x]`) en listes de tâches interactives.

---

## Syntaxe de base

### Titres

```
# Titre 1
## Titre 2
### Titre 3
#### Titre 4
##### Titre 5
###### Titre 6
```

### Emphase

```
*italique*       ou   _italique_
**gras**         ou   __gras__
***gras italique***
~~texte barré~~
==texte surligné==
```

*italique*, **gras**, ***gras italique***, ~~texte barré~~, ==texte surligné==

### Liens et images

```
[Texte du lien](https://exemple.com)
[Lien avec titre](https://exemple.com "Titre au survol")
![Texte alternatif](image.png)
![Image avec titre](image.png "Titre")
```

Les **liens externes** (`http://`, `https://`, `mailto:`) s'ouvrent dans le navigateur par défaut du système.

### Séparateur horizontal

```
---
***
___
```

---

## Listes

### Liste non ordonnée

```
- Élément A
- Élément B
  - Sous-élément B1
  - Sous-élément B2
- Élément C
```

### Liste ordonnée

```
1. Premier
2. Deuxième
3. Troisième
```

### Liste de tâches (cases à cocher)

Rendu automatiquement en cases à cocher. En mode Affichage ou Partagé, cliquer sur une case bascule directement `[ ]` / `[x]` dans le document source.

```
- [ ] Tâche à faire
- [x] Tâche accomplie
- [ ] Autre tâche
```

- [ ] Tâche à faire
- [x] Tâche accomplie
- [ ] Autre tâche

### Liste de définitions (`def_list`)

```
Terme 1
:   Définition du terme 1.

Terme 2
:   Première définition.
:   Deuxième définition.
```

Terme 1
:   Définition du terme 1.

Terme 2
:   Première définition.
:   Deuxième définition.

---

## Blocs de code

### Code inline

```
Utilisez la fonction `print()` pour afficher du texte.
```

### Bloc délimité avec coloration syntaxique (`fenced_code` + `codehilite`)

La langue est détectée automatiquement ou spécifiée explicitement :

````
```python
def bonjour(nom):
    return f"Bonjour, {nom} !"
```
````

```python
def bonjour(nom):
    return f"Bonjour, {nom} !"
```

````
```javascript
const salut = (nom) => `Bonjour, ${nom} !`;
```
````

```javascript
const salut = (nom) => `Bonjour, ${nom} !`;
```

````
```bash
#!/bin/bash
echo "Hello World"
```
````

```bash
#!/bin/bash
echo "Hello World"
```

---

## Tableaux (`tables`)

```
| Colonne 1   | Colonne 2   | Colonne 3   |
|-------------|:-----------:|------------:|
| Gauche      | Centre      | Droite      |
| Valeur A    | Valeur B    | Valeur C    |
```

| Colonne 1   | Colonne 2   | Colonne 3   |
|-------------|:-----------:|------------:|
| Gauche      | Centre      | Droite      |
| Valeur A    | Valeur B    | Valeur C    |

---

## Citations

```
> Ceci est une citation.
> Elle peut s'étendre sur plusieurs lignes.

> Citation imbriquée :
>> Niveau 2
>>> Niveau 3
```

> Ceci est une citation.
> Elle peut s'étendre sur plusieurs lignes.

> Citation imbriquée :
>> Niveau 2
>>> Niveau 3

---

## Notes de bas de page (`footnotes`)

```
Voici un texte avec une note[^1] et une autre[^note].

[^1]: Contenu de la première note.
[^note]: Contenu de la deuxième note.
```

Voici un texte avec une note[^1] et une autre[^note].

[^1]: Contenu de la première note.
[^note]: Contenu de la deuxième note.

---

## Blocs d'avertissement (`admonition`)

Types disponibles : `note`, `info`, `tip`, `warning`, `danger`, `error`, `success`, `hint`, `important`, `caution`.

```
!!! note "Titre personnalisé"
    Contenu de la note. Le contenu doit être indenté de 4 espaces.

!!! warning
    Avertissement sans titre personnalisé.

!!! tip "Astuce"
    Un conseil utile ici.
```

!!! note "Titre personnalisé"
    Contenu de la note. Le contenu doit être indenté de 4 espaces.

!!! warning
    Avertissement sans titre personnalisé.

!!! tip "Astuce"
    Un conseil utile ici.

---

## Attributs HTML (`attr_list`)

Permet d'ajouter un `id`, des classes CSS ou des attributs à n'importe quel élément :

```
## Titre avec ID {#mon-ancre}

[Lien stylisé](https://exemple.com){.bouton target="_blank"}

![Image](photo.png){width="200" height="100"}
```

---

## Table des matières (`toc`)

L'extension `toc` génère automatiquement les ancres sur tous les titres. Le panneau latéral de l'application (F9) exploite ces ancres pour permettre la navigation.

Pour insérer la table des matières dans le document lui-même :

```
[TOC]
```

---

## Typographie intelligente (`smarty`)

Conversion automatique :

| Source          | Rendu        |
|-----------------|--------------|
| `"guillemets"`  | "guillemets" |
| `'apostrophe'`  | 'apostrophe' |
| `--`            | --           |
| `---`           | ---          |
| `...`           | ...          |

---

## Métadonnées (`meta`)

Lignes `Clé: valeur` en tout début de fichier, avant tout autre contenu :

```
Type: note
Title: Mon document
Description: Résumé du contenu.
Author: Prénom Nom
Tags: exemple, markdown
Created: 2026-01-15
Timestamp: 2026-07-01
```

### Champs reconnus et ordre d'affichage

| Champ         | Libellé affiché | Description                                    |
|---------------|-----------------|-------------------------------------------------|
| `type`        | Type            | note / tâche / journal / référence (liste fermée)|
| `title`       | Titre           | Titre du document                               |
| `description` | Description     | Résumé en une phrase                            |
| `author`      | Auteur          | Nom de l'auteur                                 |
| `tags`        | Tags            | Liste de mots-clés séparés par des virgules      |
| `created`     | Créé            | Date de création                                |
| `timestamp`   | Mis à jour      | Date de dernière modification                   |

Le champ `updated` (ancien nom de `timestamp`) reste reconnu et affiché sous le même libellé « Mis à jour », pour les documents créés avant ce changement.

Les métadonnées s'affichent, dans cet ordre, dans le panneau latéral de l'application (F8) et dans la boîte de dialogue **Outils → Modifier les métadonnées…** (`Ctrl+Shift+M`), qui permet de les créer ou de les éditer via un formulaire (le champ Type y est une liste déroulante fermée).

---

## HTML brut

Du HTML peut être inclus directement dans le document :

```html
<kbd>Ctrl</kbd> + <kbd>S</kbd>

<mark>Texte surligné</mark>

<details>
<summary>Cliquer pour développer</summary>
Contenu masqué par défaut.
</details>
```

<kbd>Ctrl</kbd> + <kbd>S</kbd>

<mark>Texte surligné</mark>

<details>
<summary>Cliquer pour développer</summary>
Contenu masqué par défaut.
</details>

---

## Raccourcis clavier de l'application

### Fichier

| Raccourci          | Action                          |
|--------------------|---------------------------------|
| `Ctrl+N`           | Nouveau fichier                 |
| `Ctrl+O`           | Ouvrir un fichier               |
| `Ctrl+S`           | Enregistrer                     |
| `Ctrl+Shift+S`     | Enregistrer sous                |
| `Ctrl+E`           | Exporter en HTML                |
| `Ctrl+Shift+E`     | Exporter en PDF                 |
| `Ctrl+P`           | Imprimer                        |
| `Ctrl+Q`           | Quitter                         |

### Édition et recherche

| Raccourci          | Action                          |
|--------------------|---------------------------------|
| `Ctrl+F`           | Rechercher                      |
| `Ctrl+H`           | Remplacer                       |
| `Ctrl+B`           | Gras                            |
| `Ctrl+I`           | Italique                        |
| `Ctrl+Shift+X`     | Barré                           |
| `Ctrl+Shift+C`     | Code                            |
| `Ctrl+Shift+H`     | Surligné                        |
| `Ctrl+K`           | Lien                            |
| `Ctrl+Shift+8`     | Liste à puces                   |
| `Ctrl+Shift+7`     | Liste numérotée                 |
| `Ctrl+Shift+T`     | Liste de tâches                 |
| `Ctrl+Shift+9`     | Citation                        |

Ces raccourcis de formatage entourent la sélection (ou l'insèrent au point du curseur) et fonctionnent comme des interrupteurs : les appliquer une seconde fois retire le formatage. Le bloc de code fencé avec choix du langage n'a pas de raccourci dédié — utiliser le bouton « Code ▾ » de la mini barre d'outils au-dessus de l'éditeur.

### Affichage

| Raccourci          | Action                          |
|--------------------|---------------------------------|
| `F5`               | Mode Affichage                  |
| `F6`               | Mode Édition                    |
| `F7`               | Mode Partagé                    |
| `F8`               | Afficher/masquer panneau latéral|
| `F9`               | Thème suivant (dont Sombre)     |
| `F10`              | Largeur de contenu suivante     |
| `Ctrl++`           | Zoom avant                      |
| `Ctrl+-`           | Zoom arrière                    |
| `Ctrl+0`           | Zoom normal                     |

### Outils

| Raccourci          | Action                          |
|--------------------|---------------------------------|
| `Ctrl+Shift+M`     | Modifier les métadonnées        |
