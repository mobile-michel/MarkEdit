#!/bin/bash
# Script d'installation de MarkEdit

set -e

VENV_PATH="$HOME/venvs/markedit"
INSTALL_DIR="/home/michel/.local/opt/MarkEdit"
OLD_INSTALL_DIR="/home/michel/.local/opt/markdown-viewer"
DESKTOP_FILE="$HOME/.local/share/applications/markedit.desktop"
OLD_DESKTOP_FILE="$HOME/.local/share/applications/markdown-viewer.desktop"
SOURCE_APP="$(pwd)/markdown_app.py"

echo "================================"
echo "Installation de MarkEdit"
echo "================================"

# Créer le répertoire d'installation
if [ ! -d "$INSTALL_DIR" ]; then
    echo "📁 Création du répertoire $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
else
    echo "📁 Le répertoire $INSTALL_DIR existe déjà"
fi

# Désinstaller Markdown Viewer si présent
if [ -d "$OLD_INSTALL_DIR" ]; then
    echo "🗑️  Désinstallation de Markdown Viewer..."
    rm -rf "$OLD_INSTALL_DIR"
    echo "✅ Markdown Viewer supprimé"
fi

# Créer ou utiliser le venv
if [ ! -d "$INSTALL_DIR/.venv" ]; then
    echo "🐍 Création de l'environnement virtuel Python..."
    python3 -m venv "$INSTALL_DIR/.venv"

    echo "📦 Installation des dépendances Python..."
    "$INSTALL_DIR/.venv/bin/pip" install --upgrade pip setuptools wheel
    "$INSTALL_DIR/.venv/bin/pip" install \
        PyQt6 \
        PyQt6-WebEngine \
        markdown \
        pygments \
        pymdown-extensions
    echo "✅ Dépendances installées"
else
    echo "🐍 Environnement virtuel déjà présent"
fi

# Copier l'application
echo "📋 Copie de l'application MarkEdit..."
cp "$SOURCE_APP" "$INSTALL_DIR/"
echo "✅ Application copiée"

# Copier la documentation intégrée (menu Aide)
echo "📋 Copie de la documentation..."
cp "$(pwd)/TUTORIEL.md" "$(pwd)/MARKDOWN-REFERENCE.md" "$INSTALL_DIR/"
echo "✅ Documentation copiée"

# Installer l'icône dans le thème d'icônes de l'utilisateur
if [ -d "icons" ]; then
    echo "🎨 Installation de l'icône..."
    for size in 16 22 24 32 48 64 128 256 512; do
        icon_dir="$HOME/.local/share/icons/hicolor/${size}x${size}/apps"
        mkdir -p "$icon_dir"
        cp "icons/markedit-${size}.png" "$icon_dir/markedit.png"
    done
    mkdir -p "$HOME/.local/share/icons/hicolor/scalable/apps"
    cp "icons/markedit.svg" "$HOME/.local/share/icons/hicolor/scalable/apps/markedit.svg"
    echo "✅ Icône installée"
fi

# Créer le fichier .desktop
echo "🎯 Création du lanceur desktop..."
mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=MarkEdit
Comment=Éditeur Markdown avec aperçu en temps réel
Exec=/home/michel/.local/opt/MarkEdit/.venv/bin/python3 /home/michel/.local/opt/MarkEdit/markdown_app.py %f
Icon=markedit
Categories=Office;Utility;TextEditor;
Terminal=false
MimeType=text/markdown;text/x-markdown;text/plain;
EOF

chmod 644 "$DESKTOP_FILE"
echo "✅ Lanceur créé: $DESKTOP_FILE"

# Supprimer l'ancien fichier .desktop
if [ -f "$OLD_DESKTOP_FILE" ]; then
    echo "🗑️  Suppression de l'ancien lanceur Markdown Viewer..."
    rm -f "$OLD_DESKTOP_FILE"
    echo "✅ Ancien lanceur supprimé"
fi

# Types MIME que MarkEdit doit ouvrir par défaut
MARKDOWN_MIMES="text/markdown text/x-markdown"

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
echo "  • Ou: $INSTALL_DIR/.venv/bin/python3 $INSTALL_DIR/markdown_app.py [fichier.md]"
echo ""
