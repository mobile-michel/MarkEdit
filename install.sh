#!/bin/bash
# Script d'installation de MarkEdit
#
# L'application n'est pas copiée : elle est exécutée directement depuis ce
# dépôt, via un lanceur placé dans ~/.local/bin. Une mise à jour du dépôt
# (git pull) suffit donc, sans réinstallation.

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$HOME/venvs/markedit"
LAUNCHER="$HOME/.local/bin/markedit"
DESKTOP_FILE="$HOME/.local/share/applications/markedit.desktop"
OLD_DESKTOP_FILE="$HOME/.local/share/applications/markdown-viewer.desktop"
# Installations des versions précédentes, qui copiaient l'application.
LEGACY_DIRS=("$HOME/.local/opt/MarkEdit" "$HOME/.local/opt/markdown-viewer")

echo "================================"
echo "Installation de MarkEdit"
echo "================================"
echo "📂 Dépôt : $REPO_DIR"

if [ ! -f "$REPO_DIR/markdown_app.py" ]; then
    echo "❌ markdown_app.py est introuvable dans $REPO_DIR"
    exit 1
fi

# Environnement virtuel Python
if [ ! -x "$VENV_PATH/bin/python3" ]; then
    echo "🐍 Création de l'environnement virtuel ($VENV_PATH)..."
    mkdir -p "$(dirname "$VENV_PATH")"
    python3 -m venv "$VENV_PATH"

    echo "📦 Installation des dépendances Python..."
    "$VENV_PATH/bin/pip" install --upgrade pip setuptools wheel
    "$VENV_PATH/bin/pip" install \
        PyQt6 \
        PyQt6-WebEngine \
        markdown \
        pygments \
        pymdown-extensions
    echo "✅ Dépendances installées"
else
    echo "🐍 Environnement virtuel déjà présent"
    manquants=""
    for module in PyQt6.QtWebEngineWidgets markdown pygments pymdownx; do
        "$VENV_PATH/bin/python3" -c "import $module" 2>/dev/null || manquants="$manquants $module"
    done
    if [ -n "$manquants" ]; then
        echo "📦 Modules manquants, installation :$manquants"
        "$VENV_PATH/bin/pip" install \
            PyQt6 PyQt6-WebEngine markdown pygments pymdown-extensions
    fi
fi

# Bibliothèque Mermaid embarquée (diagrammes hors ligne)
if [ -f "$REPO_DIR/vendor/mermaid.min.js" ]; then
    echo "📐 Mermaid embarqué : présent"
else
    echo "⚠️  vendor/mermaid.min.js est absent : les diagrammes ne s'afficheront pas."
fi

# Lanceur en ligne de commande
echo "🚀 Création du lanceur ($LAUNCHER)..."
mkdir -p "$(dirname "$LAUNCHER")"
cat > "$LAUNCHER" << EOF
#!/bin/bash
exec "$VENV_PATH/bin/python3" "$REPO_DIR/markdown_app.py" "\$@"
EOF
chmod 755 "$LAUNCHER"
echo "✅ Lanceur créé"

case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) echo "ℹ️  ~/.local/bin n'est pas dans votre PATH ; ajoutez-le pour taper « markedit »." ;;
esac

# Icônes dans le thème de l'utilisateur
if [ -d "$REPO_DIR/icons" ]; then
    echo "🎨 Installation de l'icône..."
    for size in 16 22 24 32 48 64 128 256 512; do
        icon_dir="$HOME/.local/share/icons/hicolor/${size}x${size}/apps"
        mkdir -p "$icon_dir"
        cp "$REPO_DIR/icons/markedit-${size}.png" "$icon_dir/markedit.png"
    done
    mkdir -p "$HOME/.local/share/icons/hicolor/scalable/apps"
    cp "$REPO_DIR/icons/markedit.svg" "$HOME/.local/share/icons/hicolor/scalable/apps/markedit.svg"
    echo "✅ Icône installée"
fi

# Entrée de menu
echo "🎯 Création du lanceur desktop..."
mkdir -p "$HOME/.local/share/applications"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=MarkEdit
Comment=Éditeur Markdown avec aperçu en temps réel
Exec=$LAUNCHER %f
Icon=markedit
Categories=Office;Utility;TextEditor;
Terminal=false
MimeType=text/markdown;text/x-markdown;text/plain;
EOF
chmod 644 "$DESKTOP_FILE"
echo "✅ Lanceur créé: $DESKTOP_FILE"

if [ -f "$OLD_DESKTOP_FILE" ]; then
    echo "🗑️  Suppression de l'ancien lanceur Markdown Viewer..."
    rm -f "$OLD_DESKTOP_FILE"
fi

# Restes des installations qui copiaient l'application
for ancien in "${LEGACY_DIRS[@]}"; do
    if [ -d "$ancien" ]; then
        echo "🗑️  Ancienne installation trouvée : $ancien"
        rm -rf "$ancien"
        echo "✅ Supprimée (l'application est maintenant lue depuis le dépôt)"
    fi
done

# Types MIME que MarkEdit doit ouvrir par défaut
MARKDOWN_MIMES="text/markdown text/x-markdown"

# xdg-mime et le fichier KDE écrivent tous deux dans ~/.config, qui n'existe
# pas forcément sur un compte neuf.
mkdir -p "$HOME/.config"

echo "🔗 Association de MarkEdit aux types Markdown..."
if command -v xdg-mime &> /dev/null; then
    for mime in $MARKDOWN_MIMES; do
        xdg-mime default markedit.desktop "$mime"
    done
fi

# Sous KDE, /usr/share/applications/kde-mimeapps.list (paquet plasma-desktop)
# impose text/markdown -> Kate. Seul un kde-mimeapps.list utilisateur, lu en
# premier, peut le neutraliser. La spec n'y autorise que [Default Applications].
KDE_MIMEAPPS="$HOME/.config/kde-mimeapps.list"
if [ ! -f "$KDE_MIMEAPPS" ]; then
    cat > "$KDE_MIMEAPPS" << 'EOF'
# Associations MIME spécifiques à KDE Plasma, lues avant ~/.config/mimeapps.list
# et avant /usr/share/applications/kde-mimeapps.list.

[Default Applications]
EOF
fi
if ! grep -q '^\[Default Applications\]' "$KDE_MIMEAPPS"; then
    printf '\n[Default Applications]\n' >> "$KDE_MIMEAPPS"
fi
for mime in $MARKDOWN_MIMES; do
    if grep -q "^${mime}=" "$KDE_MIMEAPPS"; then
        sed -i "s|^${mime}=.*|${mime}=markedit.desktop|" "$KDE_MIMEAPPS"
    else
        sed -i "/^\[Default Applications\]/a ${mime}=markedit.desktop" "$KDE_MIMEAPPS"
    fi
done
echo "✅ MarkEdit défini comme application par défaut pour le Markdown"

# Mettre à jour la base de données des applications
if command -v update-desktop-database &> /dev/null; then
    echo "🔄 Mise à jour de la base de données des applications..."
    update-desktop-database "$HOME/.local/share/applications"
fi

# Reconstruire le cache de services KDE (sinon Plasma garde l'ancienne association)
for kbuild in kbuildsycoca6 kbuildsycoca5; do
    if command -v "$kbuild" &> /dev/null; then
        echo "🔄 Reconstruction du cache KDE ($kbuild)..."
        "$kbuild" --noincremental &> /dev/null || true
        break
    fi
done

echo ""
echo "================================"
echo "✨ Installation terminée!"
echo "================================"
echo ""
echo "Pour lancer MarkEdit:"
echo "  • Depuis le menu application (cherchez 'MarkEdit')"
echo "  • Ou: markedit [fichier.md]"
echo ""
echo "L'application est lue depuis $REPO_DIR :"
echo "un « git pull » suffit à mettre à jour, sans relancer ce script."
echo ""
