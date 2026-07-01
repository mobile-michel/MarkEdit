#!/bin/bash
# Script de désinstallation de MarkEdit

set -e

INSTALL_DIR="/home/michel/.local/opt/MarkEdit"
DESKTOP_FILE="$HOME/.local/share/applications/markedit.desktop"

echo "================================"
echo "Désinstallation de MarkEdit"
echo "================================"
echo ""

# Confirmation
read -p "Êtes-vous sûr de vouloir désinstaller MarkEdit ? (o/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Oo]$ ]]; then
    echo "Désinstallation annulée."
    exit 0
fi

# Supprimer le répertoire d'installation
if [ -d "$INSTALL_DIR" ]; then
    echo "🗑️  Suppression du répertoire d'installation..."
    rm -rf "$INSTALL_DIR"
    echo "✅ Application supprimée"
else
    echo "ℹ️  Répertoire d'installation non trouvé"
fi

# Supprimer le fichier .desktop
if [ -f "$DESKTOP_FILE" ]; then
    echo "🗑️  Suppression du lanceur desktop..."
    rm -f "$DESKTOP_FILE"
    echo "✅ Lanceur supprimé"
else
    echo "ℹ️  Lanceur non trouvé"
fi

# Supprimer l'icône
echo "🗑️  Suppression de l'icône..."
for size in 16 22 24 32 48 64 128 256 512; do
    rm -f "$HOME/.local/share/icons/hicolor/${size}x${size}/apps/markedit.png"
done
rm -f "$HOME/.local/share/icons/hicolor/scalable/apps/markedit.svg"
echo "✅ Icône supprimée"

# Mettre à jour la base de données des applications
if command -v update-desktop-database &> /dev/null; then
    echo "🔄 Mise à jour de la base de données des applications..."
    update-desktop-database "$HOME/.local/share/applications"
fi

echo ""
echo "================================"
echo "✅ Désinstallation terminée!"
echo "================================"
