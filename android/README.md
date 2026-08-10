# MarkEdit — Android (Kotlin / Jetpack Compose)

Portage Android de MarkEdit. Même principe de rendu que la version Linux : le
Markdown est converti en **HTML** puis affiché dans une **WebView**, avec une
feuille de style reprenant les thèmes « Classique » et « Sombre » du bureau,
retaillés pour un écran de téléphone.

## Pile technique

| Élément | Choix |
|---|---|
| Langage | Kotlin |
| UI | Jetpack Compose (Material 3) |
| Rendu Markdown | [CommonMark-java](https://github.com/commonmark/commonmark-java) (tables, barré, ancres de titres) |
| Affichage | `WebView` via `AndroidView`, HTML + CSS |
| Fichiers | Storage Access Framework (`ACTION_OPEN_DOCUMENT`, `ACTION_OPEN_DOCUMENT_TREE`) |
| Build | Gradle (Kotlin DSL), AGP 8.13, Kotlin 2.1 |

Équivalences avec la version Linux :

| Bureau (`markdown_app.py`) | Android |
|---|---|
| `python-markdown` | `org.commonmark` (parser + HtmlRenderer) |
| `THEMES["Classique"]` / `DARK_CSS` | `MarkdownRenderer.LIGHT_CSS` / `DARK_CSS` |
| `QWebEngineView` | `android.webkit.WebView` |
| `ExternalLinkPage.acceptNavigationRequest` | `WebViewClient.shouldOverrideUrlLoading` |
| `QFileDialog` + chemins | Storage Access Framework (URI) |

## Fonctionnalités

- **Aperçu** et **Édition** en onglets ; l'aperçu se resynchronise en y entrant
- Ouvrir un **fichier** ou un **dossier** ; enregistrer, enregistrer sous
- Ouverture depuis une autre app (intents `VIEW` et `EDIT`)
- **Sommaire** dans un tiroir ; un appui fait défiler l'aperçu jusqu'au titre
- **Recherche** dans l'aperçu (`WebView.findAllAsync`)
- **Export HTML**
- Thème clair/sombre suivant le système
- **Routage des liens**, identique à la version Linux :
  - ancre `#section` → défilement dans l'aperçu ;
  - fichier Markdown local → ouverture **dans la même fenêtre**, avec
    historique (bouton Précédent et bouton retour du système) ;
  - tout le reste → application système, via une intent `ACTION_VIEW`.

### La navigation entre fichiers demande un dossier autorisé

Le Storage Access Framework n'expose pas de chemins de fichiers : un document
ouvert seul (`Ouvrir un fichier…`) ne permet pas d'atteindre ses voisins, donc
les liens `.md` relatifs ne peuvent pas être résolus — l'app le signale.
Ouvrez le **dossier** (`Ouvrir un dossier…`) une fois : l'autorisation est
persistée, et les liens entre fichiers fonctionnent ensuite, y compris vers des
sous-dossiers et avec `..`.

### Écarts assumés avec la version Linux

Non portés : export PDF et impression, métadonnées, barre de formatage,
coloration syntaxique des blocs de code (nécessiterait d'embarquer un moteur
JS), fichiers récents, thèmes multiples et largeurs de colonne, rechargement
automatique (sans chemin stable, peu pertinent avec le SAF).

## Structure

```
android/
├── settings.gradle.kts
├── build.gradle.kts
├── gradle.properties
├── gradle/wrapper/gradle-wrapper.properties
└── app/
    ├── build.gradle.kts
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/li/maillard/markedit/
        │   ├── MainActivity.kt       # UI Compose, routage des liens, historique
        │   ├── MarkdownRenderer.kt   # Markdown -> HTML + CSS + sommaire
        │   └── Documents.kt          # Storage Access Framework, liens relatifs
        └── res/values/
            ├── strings.xml
            └── themes.xml
```

## Compilation

Ouvrir le dossier `android/` dans **Android Studio**, puis `Run`, ou en ligne
de commande une fois le wrapper généré :

```bash
./gradlew assembleDebug      # APK debug dans app/build/outputs/apk/debug/
./gradlew installDebug       # installe sur l'appareil connecté
```

> **JDK requis : 17 à 24.** Le JBR livré avec Android Studio annonce sa version
> sous la forme `25.0.2+-15348964-b329.117`, que le compilateur Kotlin embarqué
> par Gradle 8.13 ne sait pas analyser — la compilation échoue alors sur un
> `IllegalArgumentException: 25.0.2` avant même de lire les sources. Dans
> Android Studio : *Settings → Build → Build Tools → Gradle → Gradle JDK*, puis
> choisir (ou télécharger) un JDK 21.

> Le binaire `gradle-wrapper.jar` et les scripts `gradlew` ne sont pas
> versionnés ici ; Android Studio les crée à la première synchronisation, ou
> `gradle wrapper --gradle-version 8.13`.
