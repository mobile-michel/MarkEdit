#!/bin/bash
src="/home/michel/NAS/web-projects/07-APPS-LINUX/markdown-viewer/markdown_app.py"
dst="/home/michel/.local/opt/markdown-viewer"

cp "$src" "$dst/" && \
rm -f "$dst/__pycache__/markdown_app.cpython-312.pyc" && \
echo "Déployé."
