#!/bin/bash
src="/home/michel/NAS/web-projects/07-APPS-LINUX/MarkEdit/markdown_app.py"
dst="/home/michel/.local/opt/MarkEdit"

cp "$src" "$dst/" && \
rm -f "$dst/__pycache__/markdown_app.cpython-312.pyc" && \
echo "Déployé."
