Title: Bibliothèques embarquées
Author: MarkEdit
Description: Origine des fichiers tiers livrés avec l'application.

# Bibliothèques embarquées

## mermaid.min.js

- **Version** : 11.17.2
- **Origine** : <https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js>
- **Licence** : MIT
- **Rôle** : rendu des diagrammes des blocs ` ```mermaid ` dans l'aperçu.

Le fichier est embarqué pour que les diagrammes s'affichent sans connexion.
L'aperçu le charge depuis ce dossier ; l'**export HTML**, lui, référence le CDN
afin de ne pas alourdir chaque fichier exporté de 3,5 Mo — un document exporté
a donc besoin d'une connexion pour afficher ses diagrammes.

Pour mettre à jour la bibliothèque, remplacer le fichier par la version
souhaitée et corriger le numéro de version ci-dessus ainsi que celui du CDN
dans `MERMAID_CDN`, au début de `markdown_app.py`.
