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
Icon=text-editor
Categories=Office;Utility;TextEditor;
Terminal=false
MimeType=text/markdown;text/plain;
EOF

chmod 644 "$DESKTOP_FILE"
echo "✅ Lanceur créé: $DESKTOP_FILE"

# Supprimer l'ancien fichier .desktop
if [ -f "$OLD_DESKTOP_FILE" ]; then
    echo "🗑️  Suppression de l'ancien lanceur Markdown Viewer..."
    rm -f "$OLD_DESKTOP_FILE"
    echo "✅ Ancien lanceur supprimé"
fi

# Mettre à jour la base de données des applications
if command -v update-desktop-database &> /dev/null; then
    echo "🔄 Mise à jour de la base de données des applications..."
    update-desktop-database "$HOME/.local/share/applications"
fi

# Créer un lien symbolique pour le script d'installation
if [ -f "markedit.sh" ]; then
    echo "🔗 Création du lien symbolique pour markedit.sh..."
    cp "markedit.sh" "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/markedit.sh"
fi

echo ""
echo "================================"
echo "✨ Installation terminée!"
echo "================================"
echo ""
echo "Pour lancer MarkEdit:"
echo "  • Depuis le menu application (cherchez 'MarkEdit')"
echo "  • Ou: $INSTALL_DIR/.venv/bin/python3 $INSTALL_DIR/markdown_app.py [fichier.md]"
echo ""
