#!/bin/bash
# Script de désinstallation de MarkEdit
#
# Retire le lanceur, l'entrée de menu, les icônes et les associations de
# fichiers. Le dépôt lui-même n'est jamais touché : l'application y réside et
# sa suppression reste à votre main.

set -e

VENV_PATH="$HOME/venvs/markedit"
LAUNCHER="$HOME/.local/bin/markedit"
DESKTOP_FILE="$HOME/.local/share/applications/markedit.desktop"
LEGACY_DIRS=("$HOME/.local/opt/MarkEdit" "$HOME/.local/opt/markdown-viewer")

echo "================================"
echo "Désinstallation de MarkEdit"
echo "================================"
echo ""
echo "Seront supprimés : le lanceur, l'entrée de menu, les icônes et les"
echo "associations Markdown. Le dépôt et vos documents ne sont pas touchés."
echo ""

# Lit une réponse d'un caractère, puis vide le reste de la ligne : sans cela,
# la touche Entrée tapée après la première réponse servirait de réponse à la
# question suivante.
demander() {
    read -p "$1" -n 1 -r REPONSE
    echo
    read -r -t 0.1 -n 10000 _ 2>/dev/null || true
    [[ $REPONSE =~ ^[Oo]$ ]]
}

if ! demander "Êtes-vous sûr de vouloir désinstaller MarkEdit ? (o/n) "; then
    echo "Désinstallation annulée."
    exit 0
fi

# Lanceur en ligne de commande
if [ -f "$LAUNCHER" ]; then
    echo "🗑️  Suppression du lanceur..."
    rm -f "$LAUNCHER"
    echo "✅ Lanceur supprimé"
else
    echo "ℹ️  Lanceur non trouvé"
fi

# Entrée de menu
if [ -f "$DESKTOP_FILE" ]; then
    echo "🗑️  Suppression du lanceur desktop..."
    rm -f "$DESKTOP_FILE"
    echo "✅ Lanceur desktop supprimé"
else
    echo "ℹ️  Lanceur desktop non trouvé"
fi

# Icônes
echo "🗑️  Suppression de l'icône..."
for size in 16 22 24 32 48 64 128 256 512; do
    rm -f "$HOME/.local/share/icons/hicolor/${size}x${size}/apps/markedit.png"
done
rm -f "$HOME/.local/share/icons/hicolor/scalable/apps/markedit.svg"
echo "✅ Icône supprimée"

# Restes des installations qui copiaient l'application
for ancien in "${LEGACY_DIRS[@]}"; do
    if [ -d "$ancien" ]; then
        echo "🗑️  Suppression d'une ancienne installation : $ancien"
        rm -rf "$ancien"
    fi
done

# Associations Markdown posées par l'installation
KDE_MIMEAPPS="$HOME/.config/kde-mimeapps.list"
if [ -f "$KDE_MIMEAPPS" ] && grep -q '=markedit.desktop$' "$KDE_MIMEAPPS"; then
    echo "🗑️  Suppression des associations Markdown (KDE)..."
    sed -i '/=markedit.desktop$/d' "$KDE_MIMEAPPS"
    echo "✅ Associations supprimées"
fi
MIMEAPPS="$HOME/.config/mimeapps.list"
if [ -f "$MIMEAPPS" ] && grep -q '=markedit.desktop$' "$MIMEAPPS"; then
    sed -i '/=markedit.desktop$/d' "$MIMEAPPS"
    echo "✅ Associations supprimées de mimeapps.list"
fi

# Environnement virtuel : il peut servir à d'autres usages, on demande.
if [ -d "$VENV_PATH" ]; then
    echo ""
    if demander "Supprimer aussi l'environnement virtuel $VENV_PATH ? (o/n) "; then
        rm -rf "$VENV_PATH"
        echo "✅ Environnement virtuel supprimé"
    else
        echo "ℹ️  Environnement virtuel conservé"
    fi
fi

# Mettre à jour la base de données des applications
if command -v update-desktop-database &> /dev/null; then
    echo "🔄 Mise à jour de la base de données des applications..."
    update-desktop-database "$HOME/.local/share/applications"
fi

# Reconstruire le cache de services KDE
for kbuild in kbuildsycoca6 kbuildsycoca5; do
    if command -v "$kbuild" &> /dev/null; then
        echo "🔄 Reconstruction du cache KDE ($kbuild)..."
        "$kbuild" --noincremental &> /dev/null || true
        break
    fi
done

echo ""
echo "================================"
echo "✅ Désinstallation terminée!"
echo "================================"
echo ""
echo "Le dépôt n'a pas été touché : supprimez-le vous-même si vous le souhaitez."
echo ""
