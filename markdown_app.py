#!/usr/bin/env python3
"""Application MarkEdit/Editor/Printer avec PyQt6 et QWebEngine."""

import sys
import os
import re
import html as html_lib
import tempfile
import subprocess
import urllib.parse
from datetime import date, datetime

from PyQt6.QtCore import (
    Qt, QUrl, QMarginsF, QSize, QTimer, QSettings, QRect, QFileSystemWatcher,
    QObject, QEvent, pyqtSlot,
)
from PyQt6.QtGui import (
    QAction, QActionGroup, QKeySequence, QIcon, QPageLayout, QPageSize, QPainter,
    QTextCharFormat, QColor, QTextDocument, QSyntaxHighlighter, QPalette, QTextFormat,
    QPixmap, QFont, QTextCursor,
)
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QPlainTextEdit, QTextEdit,
    QFileDialog, QMessageBox, QToolBar, QStatusBar, QMenuBar,
    QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLabel, QCheckBox,
    QDialog, QDialogButtonBox,
    QFormLayout, QDockWidget, QListWidget, QListWidgetItem, QMenu, QFrame, QTextBrowser,
    QStyle, QGraphicsOpacityEffect, QComboBox, QToolButton,
)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel

import markdown
from markdown.extensions.toc import slugify as _toc_slugify
from pygments.formatters import HtmlFormatter

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

MARKDOWN_EXTENSIONS = [
    "tables", "fenced_code", "codehilite", "toc", "nl2br",
    "sane_lists", "smarty", "attr_list", "def_list",
    "footnotes", "admonition", "meta",
    "pymdownx.mark", "pymdownx.tilde",
]

MARKDOWN_EXT_CONFIGS = {
    "codehilite": {"css_class": "highlight", "guess_lang": True},
    "pymdownx.tilde": {"subscript": False},
}

# Ordre canonique d'affichage des métadonnées et leurs libellés français.
# "updated" est conservé pour l'affichage des documents existants antérieurs
# au renommage du champ en "timestamp".
METADATA_ORDER = [
    "type", "title", "description", "author", "tags", "created",
    "timestamp", "updated",
]
METADATA_LABELS = {
    "type": "Type", "title": "Titre", "description": "Description",
    "author": "Auteur", "tags": "Tags", "created": "Créé",
    "timestamp": "Mis à jour", "updated": "Mis à jour",
}
METADATA_TYPES = ["note", "tâche", "journal", "référence"]

# Langages proposés pour l'insertion d'un bloc de code (libellé, identifiant fencé).
_RE_SOURCE_TASK = re.compile(r'^(\s*[-*+]\s+)\[([ xX])\](.*)$', re.MULTILINE)

CODE_LANGUAGES = [
    ("Texte", ""), ("Python", "python"), ("JavaScript", "javascript"),
    ("TypeScript", "typescript"), ("Bash", "bash"), ("JSON", "json"),
    ("YAML", "yaml"), ("HTML", "html"), ("CSS", "css"), ("SQL", "sql"),
    ("Markdown", "markdown"), ("C", "c"), ("C++", "cpp"), ("Java", "java"),
    ("Go", "go"), ("Rust", "rust"), ("PHP", "php"), ("Ruby", "ruby"),
]


def _sorted_meta_items(meta):
    def sort_key(item):
        key = item[0].lower()
        try:
            return (METADATA_ORDER.index(key), key)
        except ValueError:
            return (len(METADATA_ORDER), key)
    return sorted(meta.items(), key=sort_key)

_PYGMENTS_CSS       = HtmlFormatter(style="default").get_style_defs(".highlight")
_PYGMENTS_CSS_DARK  = HtmlFormatter(style="monokai").get_style_defs(".highlight")

MAX_RECENT_FILES = 10

# ---------------------------------------------------------------------------
# Largeurs de contenu
# ---------------------------------------------------------------------------

CONTENT_WIDTHS = {
    "Étroit":        "640px",
    "Normal":        "860px",
    "Large":         "1100px",
    "Pleine largeur": "none",
}
DEFAULT_WIDTH = "Normal"

# ---------------------------------------------------------------------------
# CSS commun à tous les thèmes clairs (utilitaires, impression)
# ---------------------------------------------------------------------------

_COMMON_LIGHT = """
ul.task-list { list-style: none; padding-left: 1.2em; }
ul.task-list li { padding-left: 0; }
ul.task-list input[type="checkbox"] { margin-right: 0.5em; cursor: pointer; accent-color: #1a73e8; width: 1em; height: 1em; }
img { max-width: 100%; height: auto; }
dt { font-weight: 600; margin-top: 0.8em; }
dd { margin-left: 1.5em; margin-bottom: 0.5em; }
.table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 1em 0; }
.table-scroll > table { margin: 0; }
th, td { word-wrap: break-word; overflow-wrap: break-word; }
@media print {
    body { font-size: 12pt; color: #000; background: #fff; max-width: none !important; margin: 0; padding: 0; }
    .table-scroll { overflow: visible; }
    pre { white-space: pre-wrap; word-wrap: break-word; }
    a { color: #000; text-decoration: underline; }
    a[href^="http"]::after { content: " (" attr(href) ")"; font-size: 0.8em; color: #555; }
}
"""

# ---------------------------------------------------------------------------
# Thèmes (placeholder %%MAX_WIDTH%% remplacé à l'affichage)
# ---------------------------------------------------------------------------

def _theme_classique():
    return ("""
body { font-family: "Segoe UI","Noto Sans",Arial,sans-serif; font-size: 16px; line-height: 1.7;
       color: #1a1a1a; background: #fff; max-width: %%MAX_WIDTH%%; margin: 0 auto; padding: 30px 40px; }
h1,h2,h3,h4,h5,h6 { margin-top:1.4em; margin-bottom:0.6em; font-weight:600; line-height:1.3; color:#111; }
h1 { font-size:2em;   border-bottom:2px solid #e0e0e0; padding-bottom:0.3em; }
h2 { font-size:1.5em; border-bottom:1px solid #e8e8e8; padding-bottom:0.25em; }
h3 { font-size:1.25em; } h4 { font-size:1.1em; }
p { margin:0.8em 0; }
a { color:#0366d6; text-decoration:none; } a:hover { text-decoration:underline; }
ul,ol { padding-left:2em; margin:0.6em 0; } li { margin:0.25em 0; }
table { border-collapse:collapse; width:100%; }
th,td { border:1px solid #d0d0d0; padding:8px 12px; text-align:left; }
th { background:#f0f0f0; font-weight:600; }
tr:nth-child(even) { background:#fafafa; }
code { font-family:"Fira Code","Consolas",monospace; font-size:0.9em;
       background:#f4f4f4; padding:2px 6px; border-radius:3px; }
pre { background:#f6f8fa; padding:16px; border-radius:6px; overflow-x:auto;
      line-height:1.5; border:1px solid #e1e4e8; }
pre code { background:none; padding:0; font-size:0.88em; }
""" + _PYGMENTS_CSS + """
.highlight .err { border:none; }
blockquote { border-left:4px solid #3b82f6; margin:1em 0; padding:0.5em 1em;
             background:#eff6ff; color:#333; }
blockquote p { margin:0.4em 0; }
.admonition { border-left:4px solid #888; padding:12px 16px; margin:1em 0; border-radius:4px; background:#f9f9f9; }
.admonition-title { font-weight:700; margin-bottom:0.4em; }
.admonition.note,.admonition.tip { border-left-color:#3b82f6; background:#eff6ff; }
.admonition.warning { border-left-color:#f59e0b; background:#fffbeb; }
.admonition.danger,.admonition.error { border-left-color:#ef4444; background:#fef2f2; }
.footnote { font-size:0.85em; color:#555; border-top:1px solid #ddd; margin-top:2em; padding-top:0.8em; }
hr { border:none; border-top:2px solid #e0e0e0; margin:2em 0; }
.toc { background:#f8f9fa; border:1px solid #e0e0e0; border-radius:6px; padding:12px 20px; margin:1em 0; }
.toc ul { list-style:none; padding-left:1.2em; } .toc > ul { padding-left:0; }
""" + _COMMON_LIGHT)


def _theme_minimaliste():
    return ("""
body { font-family: system-ui,"Helvetica Neue",Arial,sans-serif; font-size:16px; line-height:1.8;
       color:#2c2c2c; background:#fff; max-width:%%MAX_WIDTH%%; margin:0 auto; padding:40px 48px; }
h1,h2,h3,h4,h5,h6 { margin-top:2em; margin-bottom:0.5em; font-weight:500; line-height:1.25; color:#111; }
h1 { font-size:1.9em; font-weight:400; letter-spacing:-0.02em; }
h2 { font-size:1.35em; color:#444; }
h3 { font-size:1.1em; color:#555; }
h4 { font-size:1em; text-transform:uppercase; letter-spacing:0.05em; font-size:0.85em; color:#888; }
p { margin:1em 0; }
a { color:#333; text-decoration:underline; text-underline-offset:3px; }
a:hover { color:#000; }
ul,ol { padding-left:1.6em; margin:0.8em 0; } li { margin:0.3em 0; }
table { border-collapse:collapse; width:100%; }
th,td { border-bottom:1px solid #e8e8e8; padding:10px 14px; text-align:left; }
th { font-weight:500; color:#555; font-size:0.9em; text-transform:uppercase; letter-spacing:0.04em; border-bottom:2px solid #ccc; }
tr:last-child td { border-bottom:none; }
code { font-family:"Fira Code","Consolas",monospace; font-size:0.88em; color:#555; }
pre { background:#f9f9f9; padding:20px; border-radius:4px; overflow-x:auto; line-height:1.6; }
pre code { color:inherit; }
""" + HtmlFormatter(style="friendly").get_style_defs(".highlight") + """
.highlight .err { border:none; }
blockquote { border-left:2px solid #ccc; margin:1.5em 0; padding:0.2em 1.2em; color:#666; }
blockquote p { margin:0.5em 0; }
.admonition { border-left:3px solid #ccc; padding:10px 16px; margin:1em 0; background:none; }
.admonition-title { font-weight:600; font-size:0.9em; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.3em; }
.admonition.note,.admonition.tip { border-left-color:#aaa; }
.admonition.warning { border-left-color:#e6a817; }
.admonition.danger,.admonition.error { border-left-color:#c0392b; }
.footnote { font-size:0.82em; color:#888; border-top:1px solid #eee; margin-top:3em; padding-top:1em; }
hr { border:none; border-top:1px solid #e0e0e0; margin:2.5em 0; }
.toc { border-left:3px solid #ddd; padding:8px 0 8px 16px; margin:1.5em 0; }
.toc ul { list-style:none; padding-left:1em; } .toc > ul { padding-left:0; }
""" + _COMMON_LIGHT)


def _theme_serif():
    return ("""
body { font-family: Georgia,"Cambria","Times New Roman",serif; font-size:17px; line-height:1.8;
       color:#222; background:#faf8f4; max-width:%%MAX_WIDTH%%; margin:0 auto; padding:40px 48px; }
h1,h2,h3,h4,h5,h6 { font-family:Georgia,serif; margin-top:1.6em; margin-bottom:0.5em;
                     font-weight:700; line-height:1.2; color:#111; }
h1 { font-size:2.2em; text-align:center; border-bottom:none; padding-bottom:0; margin-bottom:0.2em; }
h2 { font-size:1.5em; border-bottom:1px solid #d8d0c8; padding-bottom:0.2em; }
h3 { font-size:1.2em; font-style:italic; font-weight:400; }
h4 { font-size:1em; font-variant:small-caps; letter-spacing:0.06em; }
p { margin:0.9em 0; text-align:justify; hyphens:auto; }
a { color:#7b4f00; text-decoration:underline; text-underline-offset:2px; }
a:hover { color:#4a2f00; }
ul,ol { padding-left:2em; margin:0.7em 0; } li { margin:0.3em 0; }
table { border-collapse:collapse; width:100%; }
th,td { border:1px solid #c8c0b0; padding:8px 14px; text-align:left; }
th { background:#f0ece4; font-weight:700; font-variant:small-caps; }
tr:nth-child(even) { background:#f7f4ef; }
code { font-family:"Fira Code","Consolas",monospace; font-size:0.88em; color:#5a3e00; }
pre { background:#f0ece4; padding:16px 20px; border-radius:0; overflow-x:auto;
      line-height:1.6; border-left:3px solid #c8b890; }
pre code { color:inherit; }
""" + HtmlFormatter(style="tango").get_style_defs(".highlight") + """
.highlight .err { border:none; }
blockquote { border-left:4px solid #c8b890; margin:1.2em 2em; padding:0.3em 1em;
             background:none; color:#555; font-style:italic; }
blockquote p { margin:0.4em 0; }
.admonition { border:1px solid #d8d0c8; padding:12px 16px; margin:1em 0; background:#f7f4ef; }
.admonition-title { font-weight:700; font-variant:small-caps; margin-bottom:0.3em; }
.admonition.warning { border-color:#d4a017; }
.admonition.danger,.admonition.error { border-color:#a83232; }
.footnote { font-size:0.85em; color:#666; border-top:1px solid #d0c8bc; margin-top:2.5em; padding-top:1em; }
hr { border:none; text-align:center; margin:2em 0; }
hr::after { content:"* * *"; color:#999; font-size:1.2em; letter-spacing:0.4em; }
.toc { background:#f0ece4; border:1px solid #d8d0c8; border-radius:2px; padding:12px 20px; margin:1.5em 0; }
.toc ul { list-style:none; padding-left:1.2em; } .toc > ul { padding-left:0; }
""" + _COMMON_LIGHT)


def _theme_compact():
    return ("""
body { font-family: "Segoe UI","Noto Sans",Arial,sans-serif; font-size:14px; line-height:1.55;
       color:#1a1a1a; background:#fff; max-width:%%MAX_WIDTH%%; margin:0 auto; padding:20px 28px; }
h1,h2,h3,h4,h5,h6 { margin-top:1.1em; margin-bottom:0.35em; font-weight:600; line-height:1.25; color:#111; }
h1 { font-size:1.6em; border-bottom:2px solid #e0e0e0; padding-bottom:0.2em; }
h2 { font-size:1.25em; border-bottom:1px solid #eee; padding-bottom:0.15em; }
h3 { font-size:1.1em; } h4 { font-size:1em; color:#444; }
p { margin:0.5em 0; }
a { color:#0366d6; text-decoration:none; } a:hover { text-decoration:underline; }
ul,ol { padding-left:1.8em; margin:0.4em 0; } li { margin:0.15em 0; }
table { border-collapse:collapse; width:100%; font-size:0.92em; }
th,td { border:1px solid #d0d0d0; padding:5px 9px; text-align:left; }
th { background:#f0f0f0; font-weight:600; }
tr:nth-child(even) { background:#fafafa; }
code { font-family:"Fira Code","Consolas",monospace; font-size:0.88em;
       background:#f4f4f4; padding:1px 5px; border-radius:3px; }
pre { background:#f6f8fa; padding:10px 14px; border-radius:4px; overflow-x:auto;
      line-height:1.45; border:1px solid #e1e4e8; font-size:0.88em; }
pre code { background:none; padding:0; }
""" + _PYGMENTS_CSS + """
.highlight .err { border:none; }
blockquote { border-left:3px solid #3b82f6; margin:0.8em 0; padding:0.3em 0.8em;
             background:#eff6ff; color:#333; }
blockquote p { margin:0.2em 0; }
.admonition { border-left:3px solid #888; padding:8px 12px; margin:0.7em 0; background:#f9f9f9; }
.admonition-title { font-weight:700; margin-bottom:0.2em; font-size:0.9em; }
.admonition.note,.admonition.tip { border-left-color:#3b82f6; background:#eff6ff; }
.admonition.warning { border-left-color:#f59e0b; background:#fffbeb; }
.admonition.danger,.admonition.error { border-left-color:#ef4444; background:#fef2f2; }
.footnote { font-size:0.82em; color:#555; border-top:1px solid #ddd; margin-top:1.5em; padding-top:0.6em; }
hr { border:none; border-top:1px solid #e0e0e0; margin:1.2em 0; }
.toc { background:#f8f9fa; border:1px solid #e0e0e0; border-radius:4px; padding:8px 14px; margin:0.8em 0;
       font-size:0.92em; }
.toc ul { list-style:none; padding-left:1em; } .toc > ul { padding-left:0; }
""" + _COMMON_LIGHT)


THEMES = {
    "Classique":    _theme_classique,
    "Minimaliste":  _theme_minimaliste,
    "Sérif":        _theme_serif,
    "Compact":      _theme_compact,
}
DEFAULT_THEME = "Classique"

# ---------------------------------------------------------------------------
# CSS mode sombre (avec placeholder largeur)
# ---------------------------------------------------------------------------

DARK_CSS = ("""
body { font-family:"Segoe UI","Noto Sans",Arial,sans-serif; font-size:16px; line-height:1.7;
       color:#cdd6f4; background:#1e1e2e; max-width:%%MAX_WIDTH%%; margin:0 auto; padding:30px 40px; }
h1,h2,h3,h4,h5,h6 { margin-top:1.4em; margin-bottom:0.6em; font-weight:600; line-height:1.3; color:#e6edf3; }
h1 { font-size:2em;   border-bottom:2px solid #313244; padding-bottom:0.3em; }
h2 { font-size:1.5em; border-bottom:1px solid #313244; padding-bottom:0.25em; }
h3 { font-size:1.25em; } h4 { font-size:1.1em; }
p { margin:0.8em 0; }
a { color:#89b4fa; text-decoration:none; } a:hover { text-decoration:underline; }
ul,ol { padding-left:2em; margin:0.6em 0; } li { margin:0.25em 0; }
table { border-collapse:collapse; width:100%; }
th,td { border:1px solid #45475a; padding:8px 12px; text-align:left; }
th { background:#313244; font-weight:600; }
tr:nth-child(even) { background:#181825; }
code { font-family:"Fira Code","Consolas",monospace; font-size:0.9em;
       background:#313244; color:#f38ba8; padding:2px 6px; border-radius:3px; }
pre { background:#181825; padding:16px; border-radius:6px; overflow-x:auto;
      line-height:1.5; border:1px solid #313244; }
pre code { background:none; padding:0; font-size:0.88em; color:inherit; }
""" + _PYGMENTS_CSS_DARK + """
.highlight .err { border:none; }
blockquote { border-left:4px solid #89b4fa; margin:1em 0; padding:0.5em 1em; background:#181825; color:#a6adc8; }
blockquote p { margin:0.4em 0; }
.admonition { border-left:4px solid #585b70; padding:12px 16px; margin:1em 0; border-radius:4px; background:#181825; }
.admonition-title { font-weight:700; margin-bottom:0.4em; }
.admonition.note,.admonition.tip { border-left-color:#89b4fa; background:#1e1e2e; }
.admonition.warning { border-left-color:#f9e2af; background:#1e1e2e; }
.admonition.danger,.admonition.error { border-left-color:#f38ba8; background:#1e1e2e; }
.footnote { font-size:0.85em; color:#a6adc8; border-top:1px solid #313244; margin-top:2em; padding-top:0.8em; }
hr { border:none; border-top:2px solid #313244; margin:2em 0; }
ul.task-list { list-style:none; padding-left:1.2em; }
ul.task-list li { padding-left:0; }
ul.task-list input[type="checkbox"] { margin-right:0.5em; cursor:pointer; accent-color:#89b4fa; width:1em; height:1em; }
img { max-width:100%; height:auto; }
dt { font-weight:600; margin-top:0.8em; }
dd { margin-left:1.5em; margin-bottom:0.5em; }
.toc { background:#181825; border:1px solid #313244; border-radius:6px; padding:12px 20px; margin:1em 0; }
.toc ul { list-style:none; padding-left:1.2em; } .toc > ul { padding-left:0; }
.table-scroll { overflow-x:auto; -webkit-overflow-scrolling:touch; margin:1em 0; }
.table-scroll > table { margin:0; }
th, td { word-wrap:break-word; overflow-wrap:break-word; }
@media print { body { max-width:none !important; } .table-scroll { overflow:visible; } }
""")

THEMES["Sombre"] = lambda: DARK_CSS


def _icon(theme_name, fallback=None):
    icon = QIcon.fromTheme(theme_name)
    if icon.isNull() and fallback is not None:
        return QApplication.style().standardIcon(fallback)
    return icon


def _width_icon(fraction: float) -> QIcon:
    """Icône colonne : fraction = proportion de la largeur occupée par le contenu."""
    S = 20
    pix = QPixmap(S, S)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    # Page
    p.setPen(QColor("#bbb"))
    p.setBrush(QColor("#f5f5f5"))
    p.drawRoundedRect(0, 0, S - 1, S - 1, 2, 2)
    # Colonne de contenu
    margin = max(1, int((S * (1.0 - fraction)) / 2))
    col_w = S - 2 * margin
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#3b82f6"))
    y = 3
    for h in (2, 2, 2, 2):
        if y + h > S - 2:
            break
        p.drawRect(margin, y, col_w, h)
        y += h + 3
    p.end()
    return QIcon(pix)


def _theme_icon(accent: str, serif: bool = False, dense: bool = False, dark: bool = False) -> QIcon:
    """Icône thème : page miniature avec lignes stylisées."""
    S = 20
    pix = QPixmap(S, S)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    # Fond page
    p.setPen(QColor("#585b70" if dark else "#bbb"))
    p.setBrush(QColor("#1e1e2e" if dark else "#fafafa"))
    p.drawRoundedRect(0, 0, S - 1, S - 1, 2, 2)
    p.setPen(Qt.PenStyle.NoPen)
    # Titre (barre colorée, plus épaisse si serif)
    title_h = 3 if serif else 2
    p.setBrush(QColor(accent))
    p.drawRect(2, 3, S - 4, title_h)
    # Lignes de texte
    gap = 2 if dense else 3
    line_h = 1
    y = 3 + title_h + gap
    p.setBrush(QColor("#45475a" if dark else "#ccc"))
    while y + line_h <= S - 3:
        p.drawRect(2, y, S - 4, line_h)
        y += line_h + gap
    p.end()
    return QIcon(pix)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<script src="qrc:/qtwebchannel/qwebchannel.js"></script>
<style>
{css}
</style>
</head>
<body>
{body}
<script>
if (typeof qt !== 'undefined' && qt.webChannelTransport) {{
    new QWebChannel(qt.webChannelTransport, function(channel) {{
        window.bridge = channel.objects.bridge;
    }});
}}
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Numéros de ligne
# ---------------------------------------------------------------------------

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self):
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """QPlainTextEdit avec numéros de ligne et surbrillance de la ligne courante."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._line_number_area = LineNumberArea(self)
        self._search_selections = []
        self._current_line_color = QColor("#93c5fd")

        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._refresh_selections)
        self._update_line_number_area_width(0)

    # --- Numéros de ligne ---

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 8 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_line_number_area_width(self, _=None):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect, dy):
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(
                0, rect.y(), self._line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        painter = QPainter(self._line_number_area)
        bg = self.palette().color(QPalette.ColorRole.Window)
        painter.fillRect(event.rect(), bg)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        line_h = self.fontMetrics().height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor("#888"))
                painter.drawText(
                    0, top,
                    self._line_number_area.width() - 4, line_h,
                    Qt.AlignmentFlag.AlignRight,
                    str(block_number + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    # --- Surbrillance ---

    def set_current_line_color(self, color: QColor):
        self._current_line_color = color
        self._refresh_selections()

    def set_search_selections(self, selections):
        self._search_selections = selections
        self._refresh_selections()

    def _refresh_selections(self):
        combined = list(self._search_selections)
        if not self._search_selections:
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(self._current_line_color)
            sel.format.setProperty(
                QTextFormat.Property.FullWidthSelection, True
            )
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            combined.append(sel)
        super().setExtraSelections(combined)

    def setExtraSelections(self, selections):
        self._search_selections = selections
        self._refresh_selections()

    # --- Formatage Markdown ---

    _PAIRS = {"*": "*", "_": "_", "`": "`", "[": "]", "(": ")"}
    _RE_TASK = re.compile(r'^(\s*)([-*+])\s+\[([ xX])\]\s*(.*)$')
    _RE_BULLET = re.compile(r'^(\s*)([-*+])\s+(.*)$')
    _RE_NUMBERED = re.compile(r'^(\s*)(\d+)([.)])\s+(.*)$')
    _RE_LINK = re.compile(r'\[([^\[\]]*)\]\(([^()]*)\)')
    _RE_OPEN_TAG = re.compile(r"<([a-zA-Z][a-zA-Z0-9]*)((?:\s+[^<>]*)?)$")
    _VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    def wrap_selection(self, prefix, suffix=None):
        suffix = prefix if suffix is None else suffix
        cursor = self.textCursor()
        if not cursor.hasSelection():
            pos = cursor.position()
            cursor.insertText(f"{prefix}{suffix}")
            cursor.setPosition(pos + len(prefix))
            self.setTextCursor(cursor)
            return

        start, end = cursor.selectionStart(), cursor.selectionEnd()
        text = cursor.selectedText()
        full = self.document().toPlainText()

        # Bascule : la sélection inclut déjà les marqueurs -> on les retire.
        if (
            len(text) >= len(prefix) + len(suffix)
            and text.startswith(prefix) and text.endswith(suffix)
        ):
            inner = text[len(prefix):len(text) - len(suffix)]
            cursor.insertText(inner)
            cursor.setPosition(start)
            cursor.setPosition(start + len(inner), QTextCursor.MoveMode.KeepAnchor)
            self.setTextCursor(cursor)
            return

        # Bascule : les marqueurs entourent la sélection -> on les retire.
        before = full[max(0, start - len(prefix)):start]
        after = full[end:end + len(suffix)]
        if before == prefix and after == suffix:
            cursor.setPosition(start - len(prefix))
            cursor.setPosition(end + len(suffix), QTextCursor.MoveMode.KeepAnchor)
            cursor.insertText(text)
            cursor.setPosition(start - len(prefix))
            cursor.setPosition(start - len(prefix) + len(text), QTextCursor.MoveMode.KeepAnchor)
            self.setTextCursor(cursor)
            return

        # Pas encore formaté -> on entoure.
        cursor.insertText(f"{prefix}{text}{suffix}")
        cursor.setPosition(start + len(prefix))
        cursor.setPosition(end + len(prefix), QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    def insert_link(self):
        cursor = self.textCursor()
        full = self.document().toPlainText()
        sel_start = cursor.selectionStart()
        sel_end = cursor.selectionEnd()
        probe_pos = sel_start if cursor.hasSelection() else cursor.position()

        # Bascule : le curseur/la sélection se trouve dans un lien existant,
        # quel que soit ce qui est exactement sélectionné (texte, url, tout).
        for m in self._RE_LINK.finditer(full):
            if m.start() <= probe_pos <= m.end() and sel_end <= m.end():
                inner = m.group(1)
                unwrap = QTextCursor(self.document())
                unwrap.setPosition(m.start())
                unwrap.setPosition(m.end(), QTextCursor.MoveMode.KeepAnchor)
                unwrap.insertText(inner)
                unwrap.setPosition(m.start())
                unwrap.setPosition(m.start() + len(inner), QTextCursor.MoveMode.KeepAnchor)
                self.setTextCursor(unwrap)
                return

        if not cursor.hasSelection():
            pos = cursor.position()
            cursor.insertText("[texte](url)")
            cursor.setPosition(pos + 1)
            cursor.setPosition(pos + 1 + len("texte"), QTextCursor.MoveMode.KeepAnchor)
            self.setTextCursor(cursor)
            return

        text = cursor.selectedText()
        cursor.insertText(f"[{text}](url)")
        url_pos = sel_start + len(text) + 3
        cursor.setPosition(url_pos)
        cursor.setPosition(url_pos + 3, QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    def _selected_block_range(self):
        cursor = self.textCursor()
        doc = self.document()
        start = doc.findBlock(cursor.selectionStart()).blockNumber()
        end = doc.findBlock(cursor.selectionEnd()).blockNumber()
        return start, end

    def apply_list_prefix(self, kind):
        start, end = self._selected_block_range()
        doc = self.document()
        edit_cursor = self.textCursor()
        edit_cursor.beginEditBlock()
        counter = 1
        for bn in range(start, end + 1):
            block = doc.findBlockByNumber(bn)
            text = block.text()
            bcur = QTextCursor(block)
            if kind == "task":
                m = re.match(r'^(\s*)[-*+]\s+\[[ xX]\]\s+', text)
            elif kind == "numbered":
                m = re.match(r'^(\s*)\d+[.)]\s+', text)
            else:
                m = re.match(r'^(\s*)[-*+]\s+', text)
            if m:
                bcur.setPosition(block.position())
                bcur.setPosition(block.position() + m.end(), QTextCursor.MoveMode.KeepAnchor)
                bcur.removeSelectedText()
            else:
                bcur.setPosition(block.position())
                if kind == "task":
                    bcur.insertText("- [ ] ")
                elif kind == "numbered":
                    bcur.insertText(f"{counter}. ")
                    counter += 1
                else:
                    bcur.insertText("- ")
        edit_cursor.endEditBlock()

    def format_quote(self):
        start, end = self._selected_block_range()
        doc = self.document()
        edit_cursor = self.textCursor()
        edit_cursor.beginEditBlock()
        for bn in range(start, end + 1):
            block = doc.findBlockByNumber(bn)
            text = block.text()
            bcur = QTextCursor(block)
            if text.startswith("> "):
                strip_len = 2
            elif text.startswith(">"):
                strip_len = 1
            else:
                strip_len = 0
            if strip_len:
                bcur.setPosition(block.position())
                bcur.setPosition(block.position() + strip_len, QTextCursor.MoveMode.KeepAnchor)
                bcur.removeSelectedText()
            else:
                bcur.setPosition(block.position())
                bcur.insertText("> ")
        edit_cursor.endEditBlock()

    def format_bold(self):
        self.wrap_selection("**")

    def format_italic(self):
        self.wrap_selection("*")

    def format_strikethrough(self):
        self.wrap_selection("~~")

    def format_code(self):
        self.wrap_selection("`")

    def format_mark(self):
        self.wrap_selection("==")

    def format_link(self):
        self.insert_link()

    def format_bullet_list(self):
        self.apply_list_prefix("bullet")

    def format_numbered_list(self):
        self.apply_list_prefix("numbered")

    def format_task_list(self):
        self.apply_list_prefix("task")

    def insert_code_block(self, language=""):
        cursor = self.textCursor()
        fence = "```"
        doc = self.document()
        start = cursor.selectionStart()
        at_line_start = doc.findBlock(start).position() == start
        prefix_nl = "" if at_line_start else "\n"

        if cursor.hasSelection():
            text = cursor.selectedText().replace(" ", "\n")
            cursor.insertText(f"{prefix_nl}{fence}{language}\n{text}\n{fence}\n")
            self.setTextCursor(cursor)
        else:
            header = f"{prefix_nl}{fence}{language}\n"
            cursor.insertText(f"{header}\n{fence}\n")
            cursor.setPosition(start + len(header))
            self.setTextCursor(cursor)

    # --- Continuation automatique des listes ---

    def _clear_current_line(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()

    def _auto_indent_newline(self):
        cursor = self.textCursor()
        indent = re.match(r"[ \t]*", cursor.block().text()).group(0)
        cursor.insertText("\n" + indent)
        self.setTextCursor(cursor)

    def _in_fenced_code_block(self):
        current = self.textCursor().block()
        count = 0
        block = self.document().firstBlock()
        while block.isValid() and block.blockNumber() < current.blockNumber():
            if block.text().startswith("```"):
                count += 1
            block = block.next()
        return count % 2 == 1

    def _open_brace_block(self):
        cursor = self.textCursor()
        base_indent = re.match(r"[ \t]*", cursor.block().text()).group(0)
        inner_indent = base_indent + "    "
        start = cursor.position()
        cursor.insertText(f"{{\n{inner_indent}\n{base_indent}}}")
        cursor.setPosition(start + 2 + len(inner_indent))
        self.setTextCursor(cursor)

    def _try_continue_list(self):
        cursor = self.textCursor()
        block_text = cursor.block().text()

        m = self._RE_TASK.match(block_text)
        if m:
            indent, marker, _, content = m.groups()
            if not content.strip():
                self._clear_current_line()
                return True
            cursor.insertText(f"\n{indent}{marker} [ ] ")
            return True

        m = self._RE_BULLET.match(block_text)
        if m:
            indent, marker, content = m.groups()
            if not content.strip():
                self._clear_current_line()
                return True
            cursor.insertText(f"\n{indent}{marker} ")
            return True

        m = self._RE_NUMBERED.match(block_text)
        if m:
            indent, num, punct, content = m.groups()
            if not content.strip():
                self._clear_current_line()
                return True
            cursor.insertText(f"\n{indent}{int(num) + 1}{punct} ")
            return True

        return False

    # --- Fermeture automatique des balises HTML ---

    def _try_close_html_tag(self):
        cursor = self.textCursor()
        pos = cursor.position()
        before = self.document().toPlainText()[:pos]
        m = self._RE_OPEN_TAG.search(before)
        if not m:
            return False
        tag, attrs = m.group(1), m.group(2)
        if tag.lower() in self._VOID_TAGS or attrs.rstrip().endswith("/"):
            return False
        cursor.insertText(">")
        close_pos = cursor.position()
        cursor.insertText(f"</{tag}>")
        cursor.setPosition(close_pos)
        self.setTextCursor(cursor)
        return True

    # --- Auto-fermeture des paires ---

    def _try_pair_char(self, char):
        closing = self._PAIRS[char]
        cursor = self.textCursor()
        if cursor.hasSelection():
            start, end = cursor.selectionStart(), cursor.selectionEnd()
            text = cursor.selectedText()
            cursor.insertText(f"{char}{text}{closing}")
            cursor.setPosition(start + 1)
            cursor.setPosition(end + 1, QTextCursor.MoveMode.KeepAnchor)
            self.setTextCursor(cursor)
            return

        if char == closing:
            probe = QTextCursor(cursor)
            probe.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
            if probe.selectedText() == closing:
                cursor.movePosition(QTextCursor.MoveOperation.Right)
                self.setTextCursor(cursor)
                return

        pos = cursor.position()
        cursor.insertText(f"{char}{closing}")
        cursor.setPosition(pos + 1)
        self.setTextCursor(cursor)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if not self.textCursor().hasSelection():
                if self._try_continue_list():
                    return
                self._auto_indent_newline()
                return
            super().keyPressEvent(event)
            return

        text = event.text()
        if text == ">" and not self.textCursor().hasSelection():
            if self._try_close_html_tag():
                return

        if text == "{" and not self.textCursor().hasSelection() and self._in_fenced_code_block():
            self._open_brace_block()
            return

        if (
            text in self._PAIRS
            and not event.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier)
        ):
            self._try_pair_char(text)
            return

        super().keyPressEvent(event)


# ---------------------------------------------------------------------------
# Coloration syntaxique Markdown
# ---------------------------------------------------------------------------

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, document, dark=False):
        super().__init__(document)
        self._dark = dark
        self._build_rules()

    def _build_rules(self):
        self._rules = []

        def fmt(color, bold=False, italic=False, bg=None, mono=False):
            f = QTextCharFormat()
            f.setForeground(QColor(color))
            if bold:
                f.setFontWeight(700)
            if italic:
                f.setFontItalic(True)
            if bg:
                f.setBackground(QColor(bg))
            if mono:
                f.setFontFamilies(["Fira Code", "Consolas", "monospace"])
            return f

        if self._dark:
            h_color, bold_color, italic_color = "#89b4fa", "#cdd6f4", "#a6e3a1"
            code_fg = "#f38ba8"
            link_color, quote_color, meta_color = "#89dceb", "#a6adc8", "#f9e2af"
        else:
            h_color, bold_color, italic_color = "#0550ae", "#1a1a1a", "#116329"
            code_fg = "#b06000"
            link_color, quote_color, meta_color = "#0366d6", "#6a737d", "#b08800"

        # Titres
        for i in range(1, 7):
            hfmt = fmt(h_color, bold=True)
            self._rules.append((re.compile(r"^" + "#" * i + r"(?!#)\s.*$"), hfmt))

        # Gras
        self._rules.append((re.compile(r"\*\*[^*\n]+\*\*|__[^_\n]+__"), fmt(bold_color, bold=True)))
        # Italique
        self._rules.append((re.compile(r"\*[^*\n]+\*|_[^_\n]+_"), fmt(italic_color, italic=True)))
        # Code inline — police monospace + couleur sobre, sans fond
        self._rules.append((re.compile(r"`[^`\n]+`"), fmt(code_fg, mono=True)))
        # Liens
        self._rules.append((re.compile(r"\[([^\]\n]+)\]\([^\)\n]+\)"), fmt(link_color)))
        # Blockquotes
        self._rules.append((re.compile(r"^>.*$"), fmt(quote_color, italic=True)))
        # Listes
        self._rules.append((re.compile(r"^(\s*[-*+]|\s*\d+\.)\s"), fmt(meta_color)))
        # Métadonnées (en-tête)
        self._rules.append((re.compile(r"^\w[\w\s]*:\s.+$"), fmt(meta_color)))
        # Règle horizontale
        self._rules.append((re.compile(r"^[-*_]{3,}\s*$"), fmt(quote_color)))

        # Blocs de code fencés — police monospace + couleur sobre, sans fond
        self._fenced_fmt = fmt(code_fg, mono=True)

    def set_dark(self, dark):
        self._dark = dark
        self._build_rules()
        self.rehighlight()

    def highlightBlock(self, text):
        if text.startswith("```"):
            in_fenced = self.previousBlockState() == 1
            self.setFormat(0, len(text), self._fenced_fmt)
            self.setCurrentBlockState(0 if in_fenced else 1)
            return
        if self.previousBlockState() == 1:
            self.setFormat(0, len(text), self._fenced_fmt)
            self.setCurrentBlockState(1)
            return
        self.setCurrentBlockState(0)
        for pattern, f in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), f)


# ---------------------------------------------------------------------------
# Page web avec ouverture des liens externes dans le navigateur système
# ---------------------------------------------------------------------------

class ExternalLinkPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            scheme = url.scheme()
            if scheme in ("http", "https", "mailto"):
                import webbrowser
                webbrowser.open(url.toString())
                return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


# ---------------------------------------------------------------------------
# Pont JS ↔ Python pour la bascule des cases à cocher en aperçu
# ---------------------------------------------------------------------------

class TaskBridge(QObject):
    def __init__(self, on_toggle, parent=None):
        super().__init__(parent)
        self._on_toggle = on_toggle

    @pyqtSlot(int)
    def toggleTask(self, idx):
        self._on_toggle(idx)


# ---------------------------------------------------------------------------
# Filtre de scroll pour la synchronisation webview → éditeur
# ---------------------------------------------------------------------------

class _WebScrollFilter(QObject):
    """Intercepte les wheel events sur le webview (et ses enfants internes Qt6)."""

    def __init__(self, owner):
        super().__init__(owner)
        self._owner = owner

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel:
            w = obj
            while w is not None:
                if w is self._owner._web_view:
                    app = self._owner
                    if (app._mode == "split"
                            and not app._typing_active
                            and not event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                        delta = event.angleDelta().y()
                        sb = app._editor.verticalScrollBar()
                        app._scroll_sync_lock = True
                        sb.setValue(sb.value() - delta * 3 // 120)
                        app._scroll_sync_lock = False
                    break
                w = w.parent() or None
        return False  # laisser l'événement se propager normalement


# ---------------------------------------------------------------------------
# Item de liste pour le dialogue de personnalisation de la toolbar
# ---------------------------------------------------------------------------

class _ToolbarItem(QListWidgetItem):
    def __init__(self, label: str, name: str, icon: QIcon):
        super().__init__(icon, label)
        self.setData(Qt.ItemDataRole.UserRole, name)


# ---------------------------------------------------------------------------
# Application principale
# ---------------------------------------------------------------------------

class MarkdownApp(QMainWindow):

    def __init__(self, file_path=None):
        super().__init__()
        self._current_file = None
        self._modified = False
        self._mode = "edit"
        self._dark_mode = False
        self._zoom_factor = 1.0
        self._saving = False
        self._current_theme = DEFAULT_THEME
        self._current_width = DEFAULT_WIDTH
        self._scroll_sync_lock = False
        self._typing_active = False

        self._setup_ui()
        self._setup_menus()
        self._setup_format_toolbar()
        self._setup_toolbar()
        self._apply_shortcut_tooltips()
        self._setup_statusbar()
        self._connect_signals()
        self._setup_watcher()

        self._restore_geometry()
        self._update_title()

        if file_path and os.path.isfile(file_path):
            self._open_file(file_path)
        else:
            self._new_file()

    # -----------------------------------------------------------------------
    # Interface
    # -----------------------------------------------------------------------

    def _setup_ui(self):
        self._web_view = QWebEngineView()
        self._web_view.setPage(ExternalLinkPage(self._web_view))
        self._task_bridge = TaskBridge(self._on_task_checkbox_toggled, self)
        self._web_channel = QWebChannel(self._web_view.page())
        self._web_channel.registerObject("bridge", self._task_bridge)
        self._web_view.page().setWebChannel(self._web_channel)
        self._web_view.wheelEvent = self._web_wheel_event
        self._web_scroll_filter = _WebScrollFilter(self)
        QApplication.instance().installEventFilter(self._web_scroll_filter)

        self._editor = CodeEditor()
        self._editor.setTabStopDistance(32)
        font = self._editor.font()
        font.setFamily("Fira Code, Source Code Pro, Consolas, monospace")
        font.setPointSize(12)
        self._editor.setFont(font)

        self._highlighter = MarkdownHighlighter(self._editor.document(), dark=False)

        self._editor_container = QWidget()
        self._editor_layout = QVBoxLayout(self._editor_container)
        self._editor_layout.setContentsMargins(0, 0, 0, 0)
        self._editor_layout.setSpacing(0)
        self._editor_layout.addWidget(self._editor)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.addWidget(self._web_view)
        self._splitter.addWidget(self._editor_container)
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 1)

        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.setInterval(300)
        self._render_timer.timeout.connect(self._render)

        self._stats_timer = QTimer(self)
        self._stats_timer.setSingleShot(True)
        self._stats_timer.setInterval(400)
        self._stats_timer.timeout.connect(self._update_stats)

        self._typing_timer = QTimer(self)
        self._typing_timer.setSingleShot(True)
        self._typing_timer.setInterval(1500)
        self._typing_timer.timeout.connect(self._on_typing_idle)

        self._setup_search_bar()
        self._setup_toc_dock()

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._splitter)
        layout.addWidget(self._search_bar)
        self.setCentralWidget(central)

        self.setAcceptDrops(True)

    def _setup_toc_dock(self):
        container = QWidget()
        vl = QVBoxLayout(container)
        vl.setContentsMargins(4, 4, 4, 0)
        vl.setSpacing(0)

        # Métadonnées — toujours présent, jamais masqué/démasqué
        self._side_meta_browser = QTextBrowser()
        self._side_meta_browser.setOpenLinks(False)
        self._side_meta_browser.setFrameShape(QFrame.Shape.NoFrame)
        self._side_meta_browser.setMaximumHeight(160)
        self._side_meta_browser.setStyleSheet(
            "QTextBrowser { background: transparent; border: none; }"
        )
        vl.addWidget(self._side_meta_browser)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        vl.addWidget(sep)

        toc_label = QLabel("Table des matières")
        toc_label.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #666; padding: 4px 4px 2px 4px;"
        )
        vl.addWidget(toc_label)

        self._toc_list = QListWidget()
        vl.addWidget(self._toc_list, 1)
        self._apply_toc_style()

        dock = QDockWidget("Panneau", self)
        dock.setObjectName("toc_dock")
        dock.setWidget(container)
        dock.setMinimumWidth(200)
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        dock.hide()
        self._toc_dock = dock

    def _apply_toc_style(self):
        if self._dark_mode:
            bg    = "#181825"
            hover = "#585b70"
            text  = "#cdd6f4"
        else:
            bg    = "#ffffff"
            hover = "#b8cef8"
            text  = "#1a1a1a"
        self._toc_list.setStyleSheet(
            f"QListWidget {{ border: none; font-size: 12px;"
            f" background: {bg}; color: {text}; }}"
            f"QListWidget::item {{ padding: 2px 4px; color: {text}; }}"
            f"QListWidget::item:hover {{ background: {hover}; color: {text}; }}"
        )

    def _setup_menus(self):
        bar = self.menuBar()

        # --- Fichier ---
        file_menu = bar.addMenu("&Fichier")

        self._act_new = QAction("&Nouveau", self)
        self._act_new.setShortcut(QKeySequence.StandardKey.New)
        self._act_new.setIcon(_icon("document-new", QStyle.StandardPixmap.SP_FileIcon))
        self._act_new.setObjectName("new")
        file_menu.addAction(self._act_new)

        self._act_open = QAction("&Ouvrir…", self)
        self._act_open.setShortcut(QKeySequence.StandardKey.Open)
        self._act_open.setIcon(_icon("document-open", QStyle.StandardPixmap.SP_DirOpenIcon))
        self._act_open.setObjectName("open")
        file_menu.addAction(self._act_open)

        self._recent_menu = QMenu("Fichiers &récents", self)
        self._recent_menu.setIcon(_icon("document-open-recent"))
        file_menu.addMenu(self._recent_menu)

        file_menu.addSeparator()

        self._act_save = QAction("&Enregistrer", self)
        self._act_save.setShortcut(QKeySequence.StandardKey.Save)
        self._act_save.setIcon(_icon("document-save", QStyle.StandardPixmap.SP_DialogSaveButton))
        self._act_save.setObjectName("save")
        file_menu.addAction(self._act_save)

        self._act_save_as = QAction("Enregistrer &sous…", self)
        self._act_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self._act_save_as.setIcon(_icon("document-save-as"))
        self._act_save_as.setObjectName("save_as")
        file_menu.addAction(self._act_save_as)

        file_menu.addSeparator()

        self._act_export_html = QAction("Exporter en &HTML…", self)
        self._act_export_html.setShortcut(QKeySequence("Ctrl+E"))
        self._act_export_html.setIcon(_icon("text-html"))
        self._act_export_html.setObjectName("export_html")
        file_menu.addAction(self._act_export_html)

        self._act_export_pdf = QAction("Exporter en &PDF…", self)
        self._act_export_pdf.setShortcut(QKeySequence("Ctrl+Shift+E"))
        self._act_export_pdf.setIcon(_icon("application-pdf"))
        self._act_export_pdf.setObjectName("export_pdf")
        file_menu.addAction(self._act_export_pdf)

        file_menu.addSeparator()

        self._act_print = QAction("&Imprimer…", self)
        self._act_print.setShortcut(QKeySequence.StandardKey.Print)
        self._act_print.setIcon(_icon("document-print", QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self._act_print.setObjectName("print")
        file_menu.addAction(self._act_print)

        file_menu.addSeparator()

        self._act_quit = QAction("&Quitter", self)
        self._act_quit.setShortcut(QKeySequence.StandardKey.Quit)
        self._act_quit.setIcon(_icon("application-exit", QStyle.StandardPixmap.SP_DialogCloseButton))
        self._act_quit.setObjectName("quit")
        file_menu.addAction(self._act_quit)

        # --- Édition ---
        edit_menu = bar.addMenu("&Édition")

        self._act_search = QAction("&Rechercher…", self)
        self._act_search.setShortcut(QKeySequence("Ctrl+F"))
        self._act_search.setIcon(_icon("edit-find"))
        self._act_search.setObjectName("search")
        edit_menu.addAction(self._act_search)

        self._act_replace = QAction("&Remplacer…", self)
        self._act_replace.setShortcut(QKeySequence("Ctrl+H"))
        self._act_replace.setIcon(_icon("edit-find-replace"))
        self._act_replace.setObjectName("replace")
        edit_menu.addAction(self._act_replace)

        edit_menu.addSeparator()

        # Formatage Markdown
        self._act_bold = QAction("&Gras", self)
        self._act_bold.setShortcut(QKeySequence("Ctrl+B"))
        self._act_bold.setIcon(_icon("format-text-bold"))
        self._act_bold.setObjectName("bold")
        edit_menu.addAction(self._act_bold)

        self._act_italic = QAction("&Italique", self)
        self._act_italic.setShortcut(QKeySequence("Ctrl+I"))
        self._act_italic.setIcon(_icon("format-text-italic"))
        self._act_italic.setObjectName("italic")
        edit_menu.addAction(self._act_italic)

        self._act_strike = QAction("&Barré", self)
        self._act_strike.setShortcut(QKeySequence("Ctrl+Shift+X"))
        self._act_strike.setIcon(_icon("format-text-strikethrough"))
        self._act_strike.setObjectName("strike")
        edit_menu.addAction(self._act_strike)

        self._act_code = QAction("&Code", self)
        self._act_code.setShortcut(QKeySequence("Ctrl+Shift+C"))
        self._act_code.setIcon(_icon("format-text-code"))
        self._act_code.setObjectName("code")
        edit_menu.addAction(self._act_code)

        self._act_mark = QAction("Sur&ligné", self)
        self._act_mark.setShortcut(QKeySequence("Ctrl+Shift+H"))
        self._act_mark.setIcon(_icon("format-text-highlight"))
        self._act_mark.setObjectName("mark")
        edit_menu.addAction(self._act_mark)

        self._act_link = QAction("&Lien…", self)
        self._act_link.setShortcut(QKeySequence("Ctrl+K"))
        self._act_link.setIcon(_icon("insert-link"))
        self._act_link.setObjectName("link")
        edit_menu.addAction(self._act_link)

        self._act_bullet_list = QAction("Liste à &puces", self)
        self._act_bullet_list.setShortcut(QKeySequence("Ctrl+Shift+8"))
        self._act_bullet_list.setIcon(_icon("format-list-unordered"))
        self._act_bullet_list.setObjectName("bullet_list")
        edit_menu.addAction(self._act_bullet_list)

        self._act_numbered_list = QAction("Liste &numérotée", self)
        self._act_numbered_list.setShortcut(QKeySequence("Ctrl+Shift+7"))
        self._act_numbered_list.setIcon(_icon("format-list-ordered"))
        self._act_numbered_list.setObjectName("numbered_list")
        edit_menu.addAction(self._act_numbered_list)

        self._act_task_list = QAction("Liste de &tâches", self)
        self._act_task_list.setShortcut(QKeySequence("Ctrl+Shift+T"))
        self._act_task_list.setIcon(_icon("checkbox"))
        self._act_task_list.setObjectName("task_list")
        edit_menu.addAction(self._act_task_list)

        self._act_quote = QAction("Ci&tation", self)
        self._act_quote.setShortcut(QKeySequence("Ctrl+Shift+9"))
        self._act_quote.setIcon(_icon("format-text-blockquote"))
        self._act_quote.setObjectName("quote")
        edit_menu.addAction(self._act_quote)

        code_menu = edit_menu.addMenu("&Bloc de code")
        code_menu.setIcon(_icon("code-context"))
        self._code_lang_actions = []
        for label, lang in CODE_LANGUAGES:
            act = QAction(label, self)
            act.setData(lang)
            act.setObjectName(f"codeblock_{lang or 'texte'}")
            code_menu.addAction(act)
            self._code_lang_actions.append(act)

        # --- Affichage ---
        view_menu = bar.addMenu("&Affichage")

        self._act_view = QAction("Mode &Affichage", self)
        self._act_view.setShortcut(QKeySequence("F5"))
        self._act_view.setCheckable(True)
        self._act_view.setIcon(_icon("view-preview", QStyle.StandardPixmap.SP_FileDialogContentsView))
        self._act_view.setObjectName("view")
        view_menu.addAction(self._act_view)

        self._act_edit = QAction("Mode &Édition", self)
        self._act_edit.setShortcut(QKeySequence("F6"))
        self._act_edit.setCheckable(True)
        self._act_edit.setIcon(_icon("document-edit", QStyle.StandardPixmap.SP_FileIcon))
        self._act_edit.setObjectName("edit")
        view_menu.addAction(self._act_edit)

        self._act_split = QAction("Mode &Partagé", self)
        self._act_split.setShortcut(QKeySequence("F7"))
        self._act_split.setCheckable(True)
        self._act_split.setIcon(_icon("view-split-left-right", QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self._act_split.setObjectName("split")
        view_menu.addAction(self._act_split)

        self._mode_group = QActionGroup(self)
        self._mode_group.addAction(self._act_view)
        self._mode_group.addAction(self._act_edit)
        self._mode_group.addAction(self._act_split)
        self._mode_group.setExclusive(True)

        view_menu.addSeparator()

        self._act_zoom_in = QAction("Zoom &avant", self)
        self._act_zoom_in.setShortcut(QKeySequence("Ctrl++"))
        self._act_zoom_in.setIcon(_icon("zoom-in"))
        self._act_zoom_in.setObjectName("zoom_in")
        view_menu.addAction(self._act_zoom_in)

        self._act_zoom_out = QAction("Zoom &arrière", self)
        self._act_zoom_out.setShortcut(QKeySequence("Ctrl+-"))
        self._act_zoom_out.setIcon(_icon("zoom-out"))
        self._act_zoom_out.setObjectName("zoom_out")
        view_menu.addAction(self._act_zoom_out)

        self._act_zoom_reset = QAction("Zoom &normal", self)
        self._act_zoom_reset.setShortcut(QKeySequence("Ctrl+0"))
        self._act_zoom_reset.setIcon(_icon("zoom-original"))
        self._act_zoom_reset.setObjectName("zoom_reset")
        view_menu.addAction(self._act_zoom_reset)

        view_menu.addSeparator()

        self._act_toc = QAction("Panneau &latéral", self)
        self._act_toc.setShortcut(QKeySequence("F8"))
        self._act_toc.setCheckable(True)
        self._act_toc.setIcon(_icon("view-list-tree", QStyle.StandardPixmap.SP_FileDialogListView))
        self._act_toc.setObjectName("toc")
        view_menu.addAction(self._act_toc)

        view_menu.addSeparator()

        self._act_customize_tb = QAction("Personnaliser la barre d'outils…", self)
        self._act_customize_tb.setIcon(_icon("configure-toolbars", QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self._act_customize_tb.setObjectName("customize_tb")
        view_menu.addAction(self._act_customize_tb)

        # --- Outils ---
        tools_menu = bar.addMenu("&Outils")

        self._act_gen_metadata = QAction("&Modifier les métadonnées…", self)
        self._act_gen_metadata.setShortcut(QKeySequence("Ctrl+Shift+M"))
        self._act_gen_metadata.setIcon(_icon("document-properties"))
        self._act_gen_metadata.setObjectName("gen_metadata")
        tools_menu.addAction(self._act_gen_metadata)

        tools_menu.addSeparator()

        # Thèmes de présentation
        themes_menu = tools_menu.addMenu("&Thème")
        themes_menu.setIcon(_icon("preferences-desktop-theme", QStyle.StandardPixmap.SP_DesktopIcon))
        self._theme_actions = {}
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        _theme_icons = {
            "Classique":   _theme_icon("#3b82f6"),
            "Minimaliste": _theme_icon("#6b7280"),
            "Sérif":       _theme_icon("#92400e", serif=True),
            "Compact":     _theme_icon("#0e7490", dense=True),
            "Sombre":      _theme_icon("#89b4fa", dark=True),
        }
        _theme_objnames = {
            "Classique": "theme_classique", "Minimaliste": "theme_minimaliste",
            "Sérif": "theme_serif",         "Compact": "theme_compact",
            "Sombre": "dark",
        }
        for name in THEMES:
            act = QAction(name, self)
            act.setCheckable(True)
            act.setChecked(name == DEFAULT_THEME)
            act.setData(name)
            act.setIcon(_theme_icons.get(name, QIcon()))
            act.setObjectName(_theme_objnames.get(name, f"theme_{name}"))
            act.triggered.connect(self._on_set_theme)
            theme_group.addAction(act)
            themes_menu.addAction(act)
            self._theme_actions[name] = act

        self._act_cycle_theme = QAction("Thème &suivant", self)
        self._act_cycle_theme.setShortcut(QKeySequence("F9"))
        self._act_cycle_theme.setObjectName("cycle_theme")
        themes_menu.addSeparator()
        themes_menu.addAction(self._act_cycle_theme)

        # Largeurs de contenu
        widths_menu = tools_menu.addMenu("&Largeur")
        widths_menu.setIcon(_icon("zoom-fit-width", QStyle.StandardPixmap.SP_TitleBarMaxButton))
        self._width_actions = {}
        width_group = QActionGroup(self)
        width_group.setExclusive(True)
        _width_icons = {
            "Étroit":         _width_icon(0.35),
            "Normal":         _width_icon(0.60),
            "Large":          _width_icon(0.80),
            "Pleine largeur": _width_icon(1.00),
        }
        _width_objnames = {
            "Étroit": "width_etroit", "Normal": "width_normal",
            "Large":  "width_large",  "Pleine largeur": "width_pleine",
        }
        for name in CONTENT_WIDTHS:
            act = QAction(name, self)
            act.setCheckable(True)
            act.setChecked(name == DEFAULT_WIDTH)
            act.setData(name)
            act.setIcon(_width_icons.get(name, QIcon()))
            act.setObjectName(_width_objnames.get(name, f"width_{name}"))
            act.triggered.connect(self._on_set_width)
            width_group.addAction(act)
            widths_menu.addAction(act)
            self._width_actions[name] = act

        self._act_cycle_width = QAction("Largeur &suivante", self)
        self._act_cycle_width.setShortcut(QKeySequence("F10"))
        self._act_cycle_width.setObjectName("cycle_width")
        widths_menu.addSeparator()
        widths_menu.addAction(self._act_cycle_width)

    # Ordre par défaut de la toolbar (noms d'objectName, "---" = séparateur)
    _DEFAULT_TOOLBAR = [
        "new", "open", "save", "---",
        "print", "---",
        "search", "---",
        "view", "edit", "split", "---",
        "dark",
    ]

    def _all_toolbar_actions(self):
        """Dictionnaire nom → QAction pour toutes les actions plaçables en toolbar."""
        d = {
            "new":          self._act_new,
            "open":         self._act_open,
            "save":         self._act_save,
            "save_as":      self._act_save_as,
            "export_html":  self._act_export_html,
            "export_pdf":   self._act_export_pdf,
            "print":        self._act_print,
            "search":       self._act_search,
            "replace":      self._act_replace,
            "view":         self._act_view,
            "edit":         self._act_edit,
            "split":        self._act_split,
            "zoom_in":      self._act_zoom_in,
            "zoom_out":     self._act_zoom_out,
            "zoom_reset":   self._act_zoom_reset,
            "toc":          self._act_toc,
            "gen_metadata": self._act_gen_metadata,
            "cycle_theme":  self._act_cycle_theme,
            "cycle_width":  self._act_cycle_width,
            "bold":         self._act_bold,
            "italic":       self._act_italic,
            "strike":       self._act_strike,
            "code":         self._act_code,
            "mark":         self._act_mark,
            "link":         self._act_link,
            "bullet_list":  self._act_bullet_list,
            "numbered_list": self._act_numbered_list,
            "task_list":    self._act_task_list,
            "quote":        self._act_quote,
        }
        # Thèmes
        _theme_objnames = {
            "Classique": "theme_classique", "Minimaliste": "theme_minimaliste",
            "Sérif": "theme_serif",         "Compact": "theme_compact",
            "Sombre": "dark",
        }
        for name, act in self._theme_actions.items():
            d[_theme_objnames[name]] = act
        # Largeurs
        _width_objnames = {
            "Étroit": "width_etroit", "Normal": "width_normal",
            "Large":  "width_large",  "Pleine largeur": "width_pleine",
        }
        for name, act in self._width_actions.items():
            d[_width_objnames[name]] = act
        return d

    def _setup_format_toolbar(self):
        """Barre d'icônes de formatage Markdown, affichée au-dessus de l'éditeur."""
        tb = QToolBar("Formatage")
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        for act in (
            self._act_bold, self._act_italic, self._act_strike, self._act_code,
            self._act_mark,
        ):
            tb.addAction(act)
        tb.addSeparator()
        tb.addAction(self._act_link)
        tb.addSeparator()
        for act in (
            self._act_bullet_list, self._act_numbered_list,
            self._act_task_list, self._act_quote,
        ):
            tb.addAction(act)
        tb.addSeparator()

        code_btn = QToolButton()
        code_btn.setText("Code")
        code_btn.setToolTip("Insérer un bloc de code")
        code_btn.setIcon(_icon("code-context"))
        code_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        code_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        code_menu = QMenu(code_btn)
        for act in self._code_lang_actions:
            code_menu.addAction(act)
        code_btn.setMenu(code_menu)
        tb.addWidget(code_btn)

        self._format_toolbar = tb
        self._editor_layout.insertWidget(0, tb)

    def _apply_shortcut_tooltips(self):
        """Ajoute le raccourci clavier entre parenthèses à l'infobulle de
        chaque action, affiché au survol des icônes."""
        for act in self.findChildren(QAction):
            text = act.text().replace("&", "")
            shortcut = act.shortcut()
            if not shortcut.isEmpty():
                act.setToolTip(f"{text} ({shortcut.toString()})")
            else:
                act.setToolTip(text)

    def _setup_toolbar(self):
        self._toolbar = QToolBar("Barre d'outils")
        self._toolbar.setMovable(False)
        self._toolbar.setStyleSheet(
            "QToolBar::separator {"
            "  width: 1px; margin: 4px 6px;"
            "  background: palette(mid);"
            "}"
        )
        self.addToolBar(self._toolbar)
        self._rebuild_toolbar()

    def _rebuild_toolbar(self):
        self._toolbar.clear()
        settings = QSettings("maillard.li", "MarkdownViewer")
        items = settings.value("toolbarItems", self._DEFAULT_TOOLBAR)
        actions = self._all_toolbar_actions()
        for name in items:
            if name == "---":
                self._toolbar.addSeparator()
            elif name in actions:
                self._toolbar.addAction(actions[name])

    def _setup_statusbar(self):
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._stats_label = QLabel()
        self._stats_label.setStyleSheet("margin-right: 8px;")
        opacity = QGraphicsOpacityEffect(self._stats_label)
        opacity.setOpacity(0.7)
        self._stats_label.setGraphicsEffect(opacity)
        self._statusbar.addPermanentWidget(self._stats_label)

    def _connect_signals(self):
        self._act_new.triggered.connect(self._new_file)
        self._act_open.triggered.connect(self._on_open)
        self._act_save.triggered.connect(self._on_save)
        self._act_save_as.triggered.connect(self._on_save_as)
        self._act_export_html.triggered.connect(self._on_export_html)
        self._act_export_pdf.triggered.connect(self._on_export_pdf)
        self._act_print.triggered.connect(self._on_print)
        self._act_quit.triggered.connect(self.close)

        self._act_view.triggered.connect(lambda: self._switch_mode("view"))
        self._act_edit.triggered.connect(lambda: self._switch_mode("edit"))
        self._act_split.triggered.connect(lambda: self._switch_mode("split"))

        self._act_zoom_in.triggered.connect(self._on_zoom_in)
        self._act_zoom_out.triggered.connect(self._on_zoom_out)
        self._act_zoom_reset.triggered.connect(self._on_zoom_reset)
        self._act_toc.triggered.connect(self._toggle_toc)
        self._act_cycle_theme.triggered.connect(self._cycle_theme)
        self._act_cycle_width.triggered.connect(self._cycle_width)

        self._act_gen_metadata.triggered.connect(self._on_generate_metadata)

        self._act_search.triggered.connect(self._toggle_search)
        self._act_replace.triggered.connect(self._toggle_replace)
        self._act_customize_tb.triggered.connect(self._on_customize_toolbar)

        self._act_bold.triggered.connect(self._editor.format_bold)
        self._act_italic.triggered.connect(self._editor.format_italic)
        self._act_strike.triggered.connect(self._editor.format_strikethrough)
        self._act_code.triggered.connect(self._editor.format_code)
        self._act_mark.triggered.connect(self._editor.format_mark)
        for act in self._code_lang_actions:
            act.triggered.connect(self._on_insert_code_block)
        self._act_link.triggered.connect(self._editor.format_link)
        self._act_bullet_list.triggered.connect(self._editor.format_bullet_list)
        self._act_numbered_list.triggered.connect(self._editor.format_numbered_list)
        self._act_task_list.triggered.connect(self._editor.format_task_list)
        self._act_quote.triggered.connect(self._editor.format_quote)

        self._editor.textChanged.connect(self._on_text_changed)
        self._editor.verticalScrollBar().valueChanged.connect(self._on_editor_scrolled)
        self._toc_list.itemClicked.connect(self._on_toc_click)
        self._toc_dock.visibilityChanged.connect(self._on_dock_visibility_changed)

        self._refresh_recent_menu()

    def _setup_watcher(self):
        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._on_file_changed)

    # -----------------------------------------------------------------------
    # Barre de recherche / remplacement
    # -----------------------------------------------------------------------

    def _setup_search_bar(self):
        self._search_bar = QWidget()
        self._search_bar.setVisible(False)
        vl = QVBoxLayout(self._search_bar)
        vl.setContentsMargins(6, 4, 6, 2)
        vl.setSpacing(2)

        # Ligne recherche
        find_row = QWidget()
        hl = QHBoxLayout(find_row)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(4)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Rechercher…")
        self._search_input.setClearButtonEnabled(True)
        hl.addWidget(self._search_input, 1)

        self._search_prev_btn = QPushButton("▲")
        self._search_prev_btn.setFixedWidth(32)
        self._search_prev_btn.setToolTip("Précédent (Shift+Entrée)")
        hl.addWidget(self._search_prev_btn)

        self._search_next_btn = QPushButton("▼")
        self._search_next_btn.setFixedWidth(32)
        self._search_next_btn.setToolTip("Suivant (Entrée)")
        hl.addWidget(self._search_next_btn)

        self._search_case_cb = QCheckBox("Casse")
        hl.addWidget(self._search_case_cb)

        self._search_count_label = QLabel()
        self._search_count_label.setMinimumWidth(60)
        hl.addWidget(self._search_count_label)

        self._search_close_btn = QPushButton("✕")
        self._search_close_btn.setFixedWidth(28)
        hl.addWidget(self._search_close_btn)

        vl.addWidget(find_row)

        # Ligne remplacement (masquée par défaut)
        self._replace_row = QWidget()
        rl = QHBoxLayout(self._replace_row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(4)

        self._replace_input = QLineEdit()
        self._replace_input.setPlaceholderText("Remplacer par…")
        rl.addWidget(self._replace_input, 1)

        self._replace_btn = QPushButton("Remplacer")
        rl.addWidget(self._replace_btn)

        self._replace_all_btn = QPushButton("Tout remplacer")
        rl.addWidget(self._replace_all_btn)

        self._replace_row.setVisible(False)
        vl.addWidget(self._replace_row)

        # Signaux
        self._search_input.textChanged.connect(self._on_search_text_changed)
        self._search_next_btn.clicked.connect(self._search_next)
        self._search_prev_btn.clicked.connect(self._search_prev)
        self._search_case_cb.toggled.connect(self._on_search_text_changed)
        self._search_close_btn.clicked.connect(self._close_search)
        self._search_input.returnPressed.connect(self._search_next)
        self._replace_btn.clicked.connect(self._on_replace)
        self._replace_all_btn.clicked.connect(self._on_replace_all)

        self._search_matches = []
        self._search_current_idx = -1

    def _toggle_search(self):
        self._replace_row.setVisible(False)
        self._search_bar.setVisible(True)
        self._search_input.setFocus()
        self._search_input.selectAll()
        if self._search_input.text():
            self._on_search_text_changed()

    def _toggle_replace(self):
        self._search_bar.setVisible(True)
        self._replace_row.setVisible(True)
        self._search_input.setFocus()
        self._search_input.selectAll()
        if self._search_input.text():
            self._on_search_text_changed()

    def _close_search(self):
        self._search_bar.setVisible(False)
        self._replace_row.setVisible(False)
        self._search_count_label.clear()
        self._search_matches.clear()
        self._search_current_idx = -1
        self._editor.set_search_selections([])
        self._web_view.findText("")

    def _on_search_text_changed(self):
        text = self._search_input.text()
        if not text:
            self._search_count_label.clear()
            self._search_matches.clear()
            self._search_current_idx = -1
            self._editor.set_search_selections([])
            self._web_view.findText("")
            return
        if self._mode == "edit":
            self._find_all_in_editor(text)
        else:
            self._find_in_webview(text)

    def _find_all_in_editor(self, text):
        doc = self._editor.document()
        flags = QTextDocument.FindFlag(0)
        if self._search_case_cb.isChecked():
            flags = QTextDocument.FindFlag.FindCaseSensitively

        self._search_matches.clear()
        cursor = QTextDocument.find(doc, text, 0, flags)
        while not cursor.isNull():
            self._search_matches.append(cursor)
            cursor = QTextDocument.find(doc, text, cursor, flags)

        if self._search_matches:
            current_pos = self._editor.textCursor().position()
            self._search_current_idx = 0
            for i, c in enumerate(self._search_matches):
                if c.selectionStart() >= current_pos:
                    self._search_current_idx = i
                    break
            self._update_editor_highlights()
        else:
            self._search_current_idx = -1
            self._editor.set_search_selections([])
            self._search_count_label.setText("0/0")

    def _find_in_webview(self, text):
        from PyQt6.QtWebEngineCore import QWebEnginePage
        flags = QWebEnginePage.FindFlag(0)
        if self._search_case_cb.isChecked():
            flags = QWebEnginePage.FindFlag.FindCaseSensitively
        self._web_view.findText(text, flags)
        self._search_count_label.setText("")

    def _search_next(self):
        if not self._search_input.text():
            return
        if self._mode == "edit":
            if not self._search_matches:
                return
            self._search_current_idx = (self._search_current_idx + 1) % len(self._search_matches)
            self._update_editor_highlights()
        else:
            self._find_in_webview(self._search_input.text())

    def _search_prev(self):
        if not self._search_input.text():
            return
        if self._mode == "edit":
            if not self._search_matches:
                return
            self._search_current_idx = (self._search_current_idx - 1) % len(self._search_matches)
            self._update_editor_highlights()
        else:
            from PyQt6.QtWebEngineCore import QWebEnginePage
            flags = QWebEnginePage.FindFlag.FindBackward
            if self._search_case_cb.isChecked():
                flags |= QWebEnginePage.FindFlag.FindCaseSensitively
            self._web_view.findText(self._search_input.text(), flags)

    def _update_editor_highlights(self):
        selections = []
        fmt_all = QTextCharFormat()
        fmt_all.setBackground(QColor("#FFFF00"))
        fmt_current = QTextCharFormat()
        fmt_current.setBackground(QColor("#FF8C00"))
        fmt_current.setForeground(QColor("#FFFFFF"))

        for i, cursor in enumerate(self._search_matches):
            sel = QTextEdit.ExtraSelection()
            sel.cursor = cursor
            sel.format = fmt_current if i == self._search_current_idx else fmt_all
            selections.append(sel)

        self._editor.set_search_selections(selections)

        if 0 <= self._search_current_idx < len(self._search_matches):
            tc = self._search_matches[self._search_current_idx]
            vc = self._editor.textCursor()
            vc.setPosition(tc.selectionStart())
            self._editor.setTextCursor(vc)
            self._editor.centerCursor()

        total = len(self._search_matches)
        current = self._search_current_idx + 1 if total > 0 else 0
        self._search_count_label.setText(f"{current}/{total}")

    def _on_replace(self):
        if not self._search_matches or self._search_current_idx < 0:
            return
        replacement = self._replace_input.text()
        cursor = self._search_matches[self._search_current_idx]
        cursor.insertText(replacement)
        self._find_all_in_editor(self._search_input.text())

    def _on_replace_all(self):
        text = self._search_input.text()
        replacement = self._replace_input.text()
        if not text:
            return
        source = self._editor.toPlainText()
        flags = 0 if self._search_case_cb.isChecked() else re.IGNORECASE
        new_source, count = re.subn(re.escape(text), replacement, source, flags=flags)
        if count:
            self._editor.setPlainText(new_source)
            self._statusbar.showMessage(f"{count} remplacement(s) effectué(s).", 3000)
        self._find_all_in_editor(text)

    # -----------------------------------------------------------------------
    # Table des matières
    # -----------------------------------------------------------------------

    def _on_dock_visibility_changed(self, visible):
        self._act_toc.setChecked(visible)
        if visible:
            QTimer.singleShot(0, self._update_toc)

    def _toggle_toc(self, checked):
        self._toc_dock.setVisible(checked)

    def _update_toc(self):
        self._update_side_meta()
        self._toc_list.clear()
        source = self._editor.toPlainText()
        code_blocks = [
            (m.start(), m.end())
            for m in re.finditer(r"^```.*?^```[ \t]*$", source,
                                 flags=re.MULTILINE | re.DOTALL)
        ]
        heading_idx = 0
        for m in re.finditer(r"^(#{1,2})\s+(.+)$", source, re.MULTILINE):
            if any(s <= m.start() < e for s, e in code_blocks):
                continue
            level = len(m.group(1))
            title = m.group(2).strip()
            item = QListWidgetItem("  " * (level - 1) + title)
            item.setData(Qt.ItemDataRole.UserRole, m.start())
            item.setData(Qt.ItemDataRole.UserRole + 1, heading_idx)
            self._toc_list.addItem(item)
            heading_idx += 1

    def _update_side_meta(self):
        source = self._editor.toPlainText()
        md = markdown.Markdown(extensions=["meta"])
        md.convert(source)
        meta = md.Meta

        if not meta:
            self._side_meta_browser.setHtml(
                "<p style='color:#aaa;font-size:11px;padding:4px 2px;'>"
                "Aucune métadonnée</p>"
            )
            return

        rows = []
        for key, raw_values in _sorted_meta_items(meta):
            label = METADATA_LABELS.get(key.lower(), key.capitalize())
            tokens = self._split_meta_values(raw_values)
            if key.lower() == "tags" and len(tokens) > 1:
                val_html = " ".join(
                    f'<span style="background:#e0e7ff;color:#3730a3;border-radius:8px;'
                    f'padding:1px 7px;font-size:10px;font-weight:600;">{t}</span>'
                    for t in tokens
                )
            else:
                val_html = ", ".join(tokens)
            rows.append(
                f'<tr>'
                f'<td style="color:#888;font-size:10px;padding:2px 8px 2px 2px;'
                f'white-space:nowrap;vertical-align:top;">{label}</td>'
                f'<td style="font-size:11px;padding:2px 0;">{val_html}</td>'
                f'</tr>'
            )

        html = (
            '<table style="width:100%;border-collapse:collapse;">'
            + "".join(rows)
            + "</table>"
        )
        self._side_meta_browser.setHtml(html)

    def _on_toc_click(self, item):
        pos   = item.data(Qt.ItemDataRole.UserRole)
        title = item.data(Qt.ItemDataRole.UserRole + 1)

        # Toujours synchroniser l'éditeur (utile en mode split)
        if pos is not None:
            cursor = self._editor.textCursor()
            cursor.setPosition(pos)
            self._editor.setTextCursor(cursor)
            self._editor.centerCursor()

        # Faire défiler la webview si elle est visible
        if self._mode in ("view", "split"):
            idx = item.data(Qt.ItemDataRole.UserRole + 1)
            js = (
                f"var els = document.querySelectorAll('h1,h2');"
                f"if ({idx} < els.length) els[{idx}].scrollIntoView({{block:'start'}});"
            )
            self._web_view.page().runJavaScript(js)
        elif self._mode == "edit":
            self._editor.setFocus()

    # -----------------------------------------------------------------------
    # Rendu Markdown
    # -----------------------------------------------------------------------

    def _get_css(self):
        width_val = CONTENT_WIDTHS[self._current_width]
        return THEMES[self._current_theme]().replace("%%MAX_WIDTH%%", width_val)

    @staticmethod
    def _render_task_lists(html):
        counter = [0]

        def _repl(m):
            idx = counter[0]
            counter[0] += 1
            checked_attr = "checked " if m.group(1).lower() == "x" else ""
            return (
                f'<li><input type="checkbox" {checked_attr}data-idx="{idx}" '
                f'onclick="event.preventDefault(); '
                f'if(window.bridge) window.bridge.toggleTask({idx});"> '
            )

        html = re.sub(r"<li>\[([ xX])\][ \t]", _repl, html)
        html = re.sub(r'<ul>\s*(<li><input type="checkbox")',
                      r'<ul class="task-list">\n\1', html)
        return html

    @staticmethod
    def _wrap_tables(html):
        return re.sub(
            r'(<table\b[^>]*>.*?</table>)',
            r'<div class="table-scroll">\1</div>',
            html, flags=re.DOTALL,
        )

    @staticmethod
    def _fix_internal_links(html, toc_tokens):
        """Réécrit les liens internes (#Titre) vers l'ancre réellement générée
        par l'extension toc, qui supprime accents et caractères spéciaux."""
        ids = set()

        def collect(tokens):
            for t in tokens:
                ids.add(t["id"])
                collect(t.get("children", []))

        collect(toc_tokens)
        if not ids:
            return html

        def repl(m):
            fragment = m.group(1)
            if fragment in ids:
                return m.group(0)
            decoded = html_lib.unescape(urllib.parse.unquote(fragment))
            slug = _toc_slugify(decoded, "-")
            if slug in ids:
                return f'href="#{slug}"'
            return m.group(0)

        return re.sub(r'href="#([^"]*)"', repl, html)

    def _on_task_checkbox_toggled(self, idx):
        source = self._editor.toPlainText()
        matches = list(_RE_SOURCE_TASK.finditer(source))
        if idx < 0 or idx >= len(matches):
            return
        m = matches[idx]
        new_mark = " " if m.group(2).lower() == "x" else "x"
        cursor = self._editor.textCursor()
        cursor.setPosition(m.start(2))
        cursor.setPosition(m.end(2), QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(new_mark)
        if self._mode != "edit":
            self._render_preserving_scroll()

    def _render(self):
        source = self._editor.toPlainText()
        md = markdown.Markdown(
            extensions=MARKDOWN_EXTENSIONS,
            extension_configs=MARKDOWN_EXT_CONFIGS,
        )
        body = md.convert(source)
        body = self._fix_internal_links(body, getattr(md, "toc_tokens", []))
        body = self._render_task_lists(body)
        body = self._wrap_tables(body)
        html = HTML_TEMPLATE.format(css=self._get_css(), body=body)

        base_url = QUrl("file:///")
        if self._current_file:
            base_url = QUrl.fromLocalFile(os.path.dirname(self._current_file) + "/")

        if self._mode == "split" and self._typing_active:
            self._web_view.page().loadFinished.connect(self._scroll_web_to_cursor_once)

        self._web_view.setHtml(html, base_url)

    def _render_preserving_scroll(self):
        """Comme _render(), mais restaure la position de défilement de la vue
        rendue (utile lors d'un changement de thème ou de largeur)."""
        query = (
            "(function(){"
            "  var h = document.documentElement.scrollHeight - window.innerHeight;"
            "  return h > 0 ? window.scrollY / h : 0;"
            "})();"
        )

        def _restore(_ok):
            try:
                self._web_view.page().loadFinished.disconnect(_restore)
            except RuntimeError:
                pass
            js = (
                "(function(){"
                f"  var h = document.documentElement.scrollHeight - window.innerHeight;"
                f"  if (h > 0) window.scrollTo(0, {ratio} * h);"
                "})();"
            )
            self._web_view.page().runJavaScript(js)

        def _got_ratio(value):
            nonlocal ratio
            ratio = value or 0.0
            self._render()
            if ratio:
                self._web_view.page().loadFinished.connect(_restore)

        ratio = 0.0
        self._web_view.page().runJavaScript(query, _got_ratio)

    def _scroll_web_to_cursor_once(self, _ok):
        try:
            self._web_view.page().loadFinished.disconnect(self._scroll_web_to_cursor_once)
        except RuntimeError:
            pass
        if self._mode != "split":
            return
        cursor = self._editor.textCursor()
        total = max(self._editor.document().blockCount() - 1, 1)
        ratio = cursor.blockNumber() / total
        js = (
            "(function(){"
            f"  var h = document.documentElement.scrollHeight - window.innerHeight;"
            f"  if (h > 0) window.scrollTo(0, {ratio:.6f} * h);"
            "})();"
        )
        self._web_view.page().runJavaScript(js)

    def _on_typing_idle(self):
        self._typing_active = False

    def _on_editor_scrolled(self, value):
        if self._scroll_sync_lock or self._mode != "split" or self._typing_active:
            return
        sb = self._editor.verticalScrollBar()
        maximum = sb.maximum()
        ratio = value / maximum if maximum > 0 else 0.0
        js = (
            "(function(){"
            f"  var h = document.documentElement.scrollHeight - window.innerHeight;"
            f"  if (h > 0) window.scrollTo(0, {ratio:.6f} * h);"
            "})();"
        )
        self._web_view.page().runJavaScript(js)

    def _build_html(self):
        source = self._editor.toPlainText()
        md = markdown.Markdown(
            extensions=MARKDOWN_EXTENSIONS,
            extension_configs=MARKDOWN_EXT_CONFIGS,
        )
        body = md.convert(source)
        body = self._fix_internal_links(body, getattr(md, "toc_tokens", []))
        body = self._render_task_lists(body)
        body = self._wrap_tables(body)
        return HTML_TEMPLATE.format(css=self._get_css(), body=body)

    # -----------------------------------------------------------------------
    # Modes
    # -----------------------------------------------------------------------

    def _switch_mode(self, mode):
        self._mode = mode
        if mode == "view":
            self._render()
            self._web_view.setVisible(True)
            self._editor_container.setVisible(False)
            self._act_view.setChecked(True)
            self._statusbar.showMessage("Mode : Affichage")
        elif mode == "edit":
            self._render_timer.stop()
            self._web_view.setVisible(False)
            self._editor_container.setVisible(True)
            self._act_edit.setChecked(True)
            self._statusbar.showMessage("Mode : Édition")
            self._editor.setFocus()
        else:  # split
            self._render()
            self._web_view.setVisible(True)
            self._editor_container.setVisible(True)
            self._act_split.setChecked(True)
            self._statusbar.showMessage("Mode : Partagé")
            self._editor.setFocus()
        if self._search_bar.isVisible() and self._search_input.text():
            self._on_search_text_changed()

    # -----------------------------------------------------------------------
    # Thèmes (dont le thème sombre)
    # -----------------------------------------------------------------------

    def _apply_theme_effects(self, dark):
        self._dark_mode = dark
        self._highlighter.set_dark(dark)
        self._editor.set_current_line_color(
            QColor("#14141f") if dark else QColor("#93c5fd")
        )
        self._apply_toc_style()
        if dark:
            QApplication.instance().setPalette(self._make_dark_palette())
            p = self._editor.palette()
            p.setColor(QPalette.ColorRole.Base, QColor("#1e1e2e"))
            p.setColor(QPalette.ColorRole.Text, QColor("#cdd6f4"))
            self._editor.setPalette(p)
            self._editor.setStyleSheet("")
        else:
            QApplication.instance().setPalette(QApplication.style().standardPalette())
            self._editor.setPalette(QApplication.style().standardPalette())

    def _on_insert_code_block(self):
        self._editor.insert_code_block(self.sender().data())

    def _select_theme(self, name):
        self._current_theme = name
        self._theme_actions[name].setChecked(True)
        self._apply_theme_effects(name == "Sombre")
        if self._mode != "edit":
            self._render_preserving_scroll()

    def _on_set_theme(self):
        self._select_theme(self.sender().data())

    def _cycle_theme(self):
        names = list(THEMES)
        idx = (names.index(self._current_theme) + 1) % len(names)
        self._select_theme(names[idx])

    def _select_width(self, name):
        self._current_width = name
        self._width_actions[name].setChecked(True)
        if self._mode != "edit":
            self._render_preserving_scroll()

    def _on_set_width(self):
        self._select_width(self.sender().data())

    def _cycle_width(self):
        names = list(CONTENT_WIDTHS)
        idx = (names.index(self._current_width) + 1) % len(names)
        self._select_width(names[idx])

    @staticmethod
    def _make_dark_palette():
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window,          QColor("#1e1e2e"))
        p.setColor(QPalette.ColorRole.WindowText,      QColor("#cdd6f4"))
        p.setColor(QPalette.ColorRole.Base,            QColor("#181825"))
        p.setColor(QPalette.ColorRole.AlternateBase,   QColor("#1e1e2e"))
        p.setColor(QPalette.ColorRole.ToolTipBase,     QColor("#1e1e2e"))
        p.setColor(QPalette.ColorRole.ToolTipText,     QColor("#cdd6f4"))
        p.setColor(QPalette.ColorRole.Text,            QColor("#cdd6f4"))
        p.setColor(QPalette.ColorRole.Button,          QColor("#313244"))
        p.setColor(QPalette.ColorRole.ButtonText,      QColor("#cdd6f4"))
        p.setColor(QPalette.ColorRole.BrightText,      QColor("#f38ba8"))
        p.setColor(QPalette.ColorRole.Link,            QColor("#89b4fa"))
        p.setColor(QPalette.ColorRole.Highlight,       QColor("#89b4fa"))
        p.setColor(QPalette.ColorRole.HighlightedText, QColor("#1e1e2e"))
        return p

    # -----------------------------------------------------------------------
    # Zoom
    # -----------------------------------------------------------------------

    def _on_zoom_in(self):
        self._zoom_factor = min(self._zoom_factor + 0.1, 3.0)
        self._web_view.setZoomFactor(self._zoom_factor)

    def _on_zoom_out(self):
        self._zoom_factor = max(self._zoom_factor - 0.1, 0.3)
        self._web_view.setZoomFactor(self._zoom_factor)

    def _on_zoom_reset(self):
        self._zoom_factor = 1.0
        self._web_view.setZoomFactor(1.0)

    def _web_wheel_event(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self._on_zoom_in()
            elif delta < 0:
                self._on_zoom_out()
            event.accept()
        else:
            QWebEngineView.wheelEvent(self._web_view, event)

    # -----------------------------------------------------------------------
    # Glisser-déposer
    # -----------------------------------------------------------------------

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(u.toLocalFile().lower().endswith(
                    (".md", ".markdown", ".mkd", ".txt")) for u in urls):
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith((".md", ".markdown", ".mkd", ".txt")):
                if self._maybe_save():
                    self._open_file(path)
                break

    # -----------------------------------------------------------------------
    # Statistiques
    # -----------------------------------------------------------------------

    def _update_stats(self):
        text = self._editor.toPlainText()
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        minutes = max(1, round(words / 200))
        self._stats_label.setText(f"{words} mots · {chars} car. · ~{minutes} min")
        if self._toc_dock.isVisible():
            self._update_toc()

    # -----------------------------------------------------------------------
    # Rechargement automatique
    # -----------------------------------------------------------------------

    def _on_file_changed(self, path):
        if self._saving:
            return
        if not os.path.exists(path):
            return
        ret = QMessageBox.question(
            self, "Fichier modifié",
            f"Le fichier a été modifié en dehors de l'application.\n"
            f"Recharger ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if ret == QMessageBox.StandardButton.Yes:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self._editor.setPlainText(content)
                self._set_modified(False)
                if self._mode != "edit":
                    self._render()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de recharger :\n{e}")
        # QFileSystemWatcher peut cesser de surveiller après modification
        if path not in self._watcher.files():
            self._watcher.addPath(path)

    # -----------------------------------------------------------------------
    # Fichiers récents
    # -----------------------------------------------------------------------

    def _load_recent_files(self):
        settings = QSettings("maillard.li", "MarkdownViewer")
        return settings.value("recentFiles", []) or []

    def _save_recent_files(self, files):
        settings = QSettings("maillard.li", "MarkdownViewer")
        settings.setValue("recentFiles", files)

    def _add_to_recent(self, path):
        files = self._load_recent_files()
        if path in files:
            files.remove(path)
        files.insert(0, path)
        self._save_recent_files(files[:MAX_RECENT_FILES])
        self._refresh_recent_menu()

    def _refresh_recent_menu(self):
        self._recent_menu.clear()
        files = self._load_recent_files()
        if not files:
            act = QAction("(aucun)", self)
            act.setEnabled(False)
            self._recent_menu.addAction(act)
            return
        for path in files:
            act = QAction(os.path.basename(path), self)
            act.setToolTip(path)
            act.setData(path)
            act.triggered.connect(self._open_recent)
            self._recent_menu.addAction(act)
        self._recent_menu.addSeparator()
        clear_act = QAction("Effacer l'historique", self)
        clear_act.triggered.connect(self._clear_recent)
        self._recent_menu.addAction(clear_act)

    def _open_recent(self):
        path = self.sender().data()
        if not os.path.isfile(path):
            QMessageBox.warning(self, "Fichier introuvable", f"Le fichier n'existe plus :\n{path}")
            files = self._load_recent_files()
            if path in files:
                files.remove(path)
                self._save_recent_files(files)
                self._refresh_recent_menu()
            return
        if self._maybe_save():
            self._open_file(path)

    def _clear_recent(self):
        self._save_recent_files([])
        self._refresh_recent_menu()

    # -----------------------------------------------------------------------
    # Opérations fichier
    # -----------------------------------------------------------------------

    def _new_file(self):
        if not self._maybe_save():
            return
        if self._current_file and self._current_file in self._watcher.files():
            self._watcher.removePath(self._current_file)
        self._current_file = None
        self._editor.clear()
        self._set_modified(False)
        self._switch_mode("edit")
        self._update_title()

    def _on_open(self):
        if not self._maybe_save():
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un fichier Markdown", "",
            "Fichiers Markdown (*.md *.markdown *.mkd *.txt);;Tous les fichiers (*)",
        )
        if path:
            self._open_file(path)

    def _open_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir :\n{e}")
            return
        if self._current_file and self._current_file in self._watcher.files():
            self._watcher.removePath(self._current_file)
        self._current_file = path
        self._editor.setPlainText(content)
        self._set_modified(False)
        self._switch_mode("view")
        self._update_title()
        self._add_to_recent(path)
        self._watcher.addPath(path)
        self._update_toc()
        self._update_stats()

    def _on_save(self):
        if self._current_file:
            self._save_file(self._current_file)
        else:
            self._on_save_as()

    def _on_save_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer sous", "",
            "Fichiers Markdown (*.md *.markdown);;Tous les fichiers (*)",
        )
        if path:
            self._save_file(path)

    def _save_file(self, path):
        self._saving = True
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._editor.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer :\n{e}")
            self._saving = False
            return
        # Délai pour laisser le signal du QFileSystemWatcher arriver avant de
        # réinitialiser _saving — sans ça, le signal arrive après et déclenche
        # faussement la boîte de dialogue "Fichier modifié en dehors de l'app".
        QTimer.singleShot(500, lambda: setattr(self, "_saving", False))
        if self._current_file != path:
            if self._current_file and self._current_file in self._watcher.files():
                self._watcher.removePath(self._current_file)
            self._watcher.addPath(path)
        self._current_file = path
        self._set_modified(False)
        self._update_title()
        self._add_to_recent(path)
        self._statusbar.showMessage(f"Enregistré : {path}", 3000)

    # -----------------------------------------------------------------------
    # Export HTML / PDF
    # -----------------------------------------------------------------------

    def _on_export_html(self):
        default = ""
        if self._current_file:
            default = os.path.splitext(self._current_file)[0] + ".html"
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter en HTML", default,
            "Fichiers HTML (*.html *.htm);;Tous les fichiers (*)",
        )
        if not path:
            return
        html = self._build_html()
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            self._statusbar.showMessage(f"HTML exporté : {path}", 4000)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'exporter :\n{e}")

    def _on_export_pdf(self):
        default = ""
        if self._current_file:
            default = os.path.splitext(self._current_file)[0] + ".pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter en PDF", default,
            "Fichiers PDF (*.pdf);;Tous les fichiers (*)",
        )
        if not path:
            return
        self._pdf_export_path = path
        self._web_view.page().loadFinished.connect(self._on_page_ready_for_export_pdf)
        self._render()

    def _on_page_ready_for_export_pdf(self, ok):
        try:
            self._web_view.page().loadFinished.disconnect(self._on_page_ready_for_export_pdf)
        except TypeError:
            pass
        if not ok:
            QMessageBox.warning(self, "Export PDF", "Le rendu de la page a échoué.")
            return
        layout = QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4),
            QPageLayout.Orientation.Portrait,
            QMarginsF(15, 15, 15, 15),
        )
        self._web_view.page().printToPdf(self._on_export_pdf_ready, layout)

    def _on_export_pdf_ready(self, pdf_data):
        if not pdf_data:
            QMessageBox.warning(self, "Export PDF", "La génération PDF a échoué.")
            return
        try:
            with open(self._pdf_export_path, "wb") as f:
                f.write(bytes(pdf_data))
            self._statusbar.showMessage(f"PDF exporté : {self._pdf_export_path}", 4000)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'écrire le PDF :\n{e}")

    # -----------------------------------------------------------------------
    # Impression
    # -----------------------------------------------------------------------

    def _on_print(self):
        self._web_view.page().loadFinished.connect(self._on_page_ready_for_pdf)
        self._render()

    def _on_page_ready_for_pdf(self, ok):
        try:
            self._web_view.page().loadFinished.disconnect(self._on_page_ready_for_pdf)
        except TypeError:
            pass
        if not ok:
            QMessageBox.warning(self, "Impression", "Le rendu de la page a échoué.")
            return
        layout = QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4),
            QPageLayout.Orientation.Portrait,
            QMarginsF(10, 10, 10, 10),
        )
        self._web_view.page().printToPdf(self._on_pdf_ready, layout)

    def _on_pdf_ready(self, pdf_data):
        if not pdf_data:
            QMessageBox.warning(self, "Impression", "La génération PDF a échoué.")
            return
        self._tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        self._tmp_pdf.write(bytes(pdf_data))
        self._tmp_pdf.close()

        doc = QPdfDocument(self)
        doc.load(self._tmp_pdf.name)
        if doc.pageCount() == 0:
            QMessageBox.warning(self, "Impression", "Le PDF généré est vide.")
            os.unlink(self._tmp_pdf.name)
            return

        self._printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(self._printer, self)
        if dialog.exec() != QPrintDialog.DialogCode.Accepted:
            doc.close()
            os.unlink(self._tmp_pdf.name)
            return

        dpi = self._printer.resolution()
        painter = QPainter()
        if not painter.begin(self._printer):
            QMessageBox.warning(self, "Impression", "Impossible d'initialiser l'imprimante.")
            doc.close()
            os.unlink(self._tmp_pdf.name)
            return

        for i in range(doc.pageCount()):
            if i > 0:
                self._printer.newPage()
            page_size_pt = doc.pagePointSize(i)
            img_size = QSize(
                int(page_size_pt.width() * dpi / 72.0),
                int(page_size_pt.height() * dpi / 72.0),
            )
            image = doc.render(i, img_size)
            painter.drawImage(painter.viewport(), image)

        painter.end()
        doc.close()
        os.unlink(self._tmp_pdf.name)
        self._statusbar.showMessage("Impression terminée.", 3000)

    # -----------------------------------------------------------------------
    # Métadonnées
    # -----------------------------------------------------------------------

    def _default_author(self):
        settings = QSettings("maillard.li", "MarkdownViewer")
        saved = settings.value("lastAuthor", "")
        if saved:
            return saved
        try:
            result = subprocess.run(
                ["git", "config", "user.name"],
                capture_output=True, text=True, timeout=2,
            )
            return result.stdout.strip()
        except Exception:
            return ""

    @staticmethod
    def _strip_meta_block(text):
        lines = text.split("\n")
        if not lines or not re.match(r"^\w[\w\s]*\s*:", lines[0]):
            return text
        for i, line in enumerate(lines):
            if not line.strip():
                return "\n".join(lines[i + 1:])
        return text

    def _on_generate_metadata(self):
        source = self._editor.toPlainText()
        md_parser = markdown.Markdown(extensions=["meta"])
        md_parser.convert(source)
        existing = md_parser.Meta

        def _get(*keys, default=""):
            for key in keys:
                vals = existing.get(key, [])
                if vals:
                    return ", ".join(v.strip() for v in vals)
            return default

        if self._current_file:
            base = os.path.splitext(os.path.basename(self._current_file))[0]
            default_title = base.replace("-", " ").replace("_", " ").title()
        else:
            default_title = ""

        default_created = date.today().isoformat()
        default_timestamp = date.today().isoformat()
        if self._current_file and os.path.exists(self._current_file):
            st = os.stat(self._current_file)
            default_timestamp = datetime.fromtimestamp(st.st_mtime).date().isoformat()
            try:
                default_created = datetime.fromtimestamp(st.st_birthtime).date().isoformat()
            except AttributeError:
                default_created = default_timestamp

        dlg = QDialog(self)
        dlg.setWindowTitle("Modifier les métadonnées")
        dlg.setMinimumWidth(440)
        vl = QVBoxLayout(dlg)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        vl.addLayout(form)

        f_type = QComboBox()
        f_type.setStyleSheet(
            "QComboBox QAbstractItemView { border: 1px solid #d0d0d0; }"
        )
        f_type.addItem("sélectionner…", "")
        italic_font = QFont()
        italic_font.setItalic(True)
        f_type.setItemData(0, italic_font, Qt.ItemDataRole.FontRole)
        for t in METADATA_TYPES:
            f_type.addItem(t.capitalize(), t)
        existing_type = _get("type").strip().lower()
        idx = f_type.findData(existing_type)
        f_type.setCurrentIndex(idx if idx >= 0 else 0)

        f_title       = QLineEdit(_get("title", default=default_title))
        f_description = QLineEdit(_get("description"))
        f_description.setPlaceholderText("(optionnel)")
        f_author      = QLineEdit(_get("author", default=self._default_author()))
        f_tags        = QLineEdit(_get("tags"))
        f_tags.setPlaceholderText("tag1, tag2, tag3")
        f_created     = QLineEdit(_get("created", default=default_created))
        f_timestamp   = QLineEdit(_get("timestamp", "updated", default=default_timestamp))

        form.addRow("Type :",          f_type)
        form.addRow("Titre :",         f_title)
        form.addRow("Description :",   f_description)
        form.addRow("Auteur :",        f_author)
        form.addRow("Tags :",          f_tags)
        form.addRow("Créé le :",       f_created)
        form.addRow("Mis à jour le :", f_timestamp)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        vl.addWidget(buttons)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        author_val = f_author.text().strip()
        if author_val:
            QSettings("maillard.li", "MarkdownViewer").setValue("lastAuthor", author_val)

        fields = [
            ("Type",        f_type.currentData() or ""),
            ("Title",       f_title.text().strip()),
            ("Description", f_description.text().strip()),
            ("Author",      author_val),
            ("Tags",        f_tags.text().strip()),
            ("Created",     f_created.text().strip()),
            ("Timestamp",   f_timestamp.text().strip()),
        ]
        meta_lines = [f"{k}: {v}" for k, v in fields if v]
        if not meta_lines:
            return
        body = self._strip_meta_block(source)
        self._editor.setPlainText("\n".join(meta_lines) + "\n\n" + body)
        self._statusbar.showMessage("Métadonnées mises à jour.", 3000)

    @staticmethod
    def _split_meta_values(values):
        tokens = []
        for v in values:
            tokens.extend(t.strip() for t in v.split(",") if t.strip())
        return tokens

    # -----------------------------------------------------------------------
    # Personnalisation de la barre d'outils
    # -----------------------------------------------------------------------

    def _on_customize_toolbar(self):
        settings = QSettings("maillard.li", "MarkdownViewer")
        current_items = list(settings.value("toolbarItems", self._DEFAULT_TOOLBAR))
        all_actions = self._all_toolbar_actions()

        dlg = QDialog(self)
        dlg.setWindowTitle("Personnaliser la barre d'outils")
        dlg.setMinimumSize(560, 420)

        main_layout = QHBoxLayout()

        # --- Panneau gauche : actions disponibles ---
        left_layout = QVBoxLayout()
        left_label = QLabel("Actions disponibles :")
        left_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(left_label)
        available_list = QListWidget()
        available_list.addItem(_ToolbarItem("--- Séparateur ---", "---", QIcon()))
        for name, act in all_actions.items():
            available_list.addItem(_ToolbarItem(act.text().replace("&", ""), name, act.icon()))
        left_layout.addWidget(available_list)

        # --- Boutons du milieu ---
        mid_layout = QVBoxLayout()
        mid_layout.addStretch()
        btn_add = QPushButton("→")
        btn_add.setFixedWidth(36)
        btn_remove = QPushButton("←")
        btn_remove.setFixedWidth(36)
        mid_layout.addWidget(btn_add)
        mid_layout.addWidget(btn_remove)
        mid_layout.addStretch()

        # --- Panneau droit : barre actuelle ---
        right_layout = QVBoxLayout()
        right_label = QLabel("Barre d'outils :")
        right_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(right_label)
        current_list = QListWidget()
        for name in current_items:
            if name == "---":
                current_list.addItem(_ToolbarItem("--- Séparateur ---", "---", QIcon()))
            elif name in all_actions:
                act = all_actions[name]
                current_list.addItem(_ToolbarItem(act.text().replace("&", ""), name, act.icon()))
        right_layout.addWidget(current_list)

        # --- Boutons haut/bas ---
        updown_layout = QHBoxLayout()
        btn_up = QPushButton("↑ Monter")
        btn_down = QPushButton("↓ Descendre")
        btn_reset = QPushButton("Réinitialiser")
        updown_layout.addWidget(btn_up)
        updown_layout.addWidget(btn_down)
        updown_layout.addStretch()
        updown_layout.addWidget(btn_reset)
        right_layout.addLayout(updown_layout)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(mid_layout)
        main_layout.addLayout(right_layout)

        vl = QVBoxLayout(dlg)
        vl.addLayout(main_layout)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        vl.addWidget(buttons)

        def add_item():
            item = available_list.currentItem()
            if item:
                current_list.addItem(_ToolbarItem(item.text(), item.data(Qt.ItemDataRole.UserRole), item.icon()))

        def remove_item():
            row = current_list.currentRow()
            if row >= 0:
                current_list.takeItem(row)

        def move_up():
            row = current_list.currentRow()
            if row > 0:
                item = current_list.takeItem(row)
                current_list.insertItem(row - 1, item)
                current_list.setCurrentRow(row - 1)

        def move_down():
            row = current_list.currentRow()
            if row < current_list.count() - 1:
                item = current_list.takeItem(row)
                current_list.insertItem(row + 1, item)
                current_list.setCurrentRow(row + 1)

        def reset_default():
            current_list.clear()
            for name in self._DEFAULT_TOOLBAR:
                if name == "---":
                    current_list.addItem(_ToolbarItem("--- Séparateur ---", "---", QIcon()))
                elif name in all_actions:
                    act = all_actions[name]
                    current_list.addItem(_ToolbarItem(act.text().replace("&", ""), name, act.icon()))

        btn_add.clicked.connect(add_item)
        btn_remove.clicked.connect(remove_item)
        btn_up.clicked.connect(move_up)
        btn_down.clicked.connect(move_down)
        btn_reset.clicked.connect(reset_default)
        available_list.itemDoubleClicked.connect(lambda _: add_item())
        current_list.itemDoubleClicked.connect(lambda _: remove_item())

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new_items = [
            current_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(current_list.count())
        ]
        settings.setValue("toolbarItems", new_items)
        self._rebuild_toolbar()

    # -----------------------------------------------------------------------
    # Gestion d'état
    # -----------------------------------------------------------------------

    def _on_text_changed(self):
        if not self._modified:
            self._set_modified(True)
        if self._mode == "split":
            self._typing_active = True
            self._typing_timer.start()
            self._render_timer.start()
        self._stats_timer.start()

    def _set_modified(self, val):
        self._modified = val
        self._update_title()

    def _update_title(self):
        name = os.path.basename(self._current_file) if self._current_file else "Sans titre"
        if self._modified:
            name += " *"
        self.setWindowTitle(f"{name} — MarkEdit")

    def _maybe_save(self):
        if not self._modified:
            return True
        ret = QMessageBox.question(
            self, "Document modifié",
            "Le document a été modifié. Voulez-vous enregistrer les modifications ?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )
        if ret == QMessageBox.StandardButton.Save:
            self._on_save()
            return not self._modified
        if ret == QMessageBox.StandardButton.Cancel:
            return False
        return True

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self._search_bar.isVisible():
            self._close_search()
            return
        if (event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                and event.modifiers() & Qt.KeyboardModifier.ShiftModifier
                and self._search_input.hasFocus()):
            self._search_prev()
            return
        super().keyPressEvent(event)

    # -----------------------------------------------------------------------
    # Géométrie / persistance
    # -----------------------------------------------------------------------

    def _restore_geometry(self):
        settings = QSettings("maillard.li", "MarkdownViewer")
        geometry = settings.value("windowGeometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1000, 750)
        splitter_state = settings.value("splitterState")
        if splitter_state:
            self._splitter.restoreState(splitter_state)
        zoom = settings.value("zoomFactor", 1.0)
        try:
            self._zoom_factor = float(zoom)
        except (TypeError, ValueError):
            self._zoom_factor = 1.0
        self._web_view.setZoomFactor(self._zoom_factor)
        theme = settings.value("theme", DEFAULT_THEME)
        # Migration : l'ancien réglage "darkMode" (mode sombre indépendant
        # du thème) prévaut si présent, et sélectionne désormais le thème
        # "Sombre".
        if settings.value("darkMode", False, type=bool):
            theme = "Sombre"
        if theme in THEMES:
            self._current_theme = theme
            self._theme_actions[theme].setChecked(True)
            self._apply_theme_effects(theme == "Sombre")
        width = settings.value("contentWidth", DEFAULT_WIDTH)
        if width in CONTENT_WIDTHS:
            self._current_width = width
            self._width_actions[width].setChecked(True)
        panel_visible = settings.value("panelVisible", False, type=bool)
        if panel_visible:
            self._toc_dock.show()
            self._act_toc.setChecked(True)
            QTimer.singleShot(0, self._update_toc)

    def _save_geometry(self):
        settings = QSettings("maillard.li", "MarkdownViewer")
        settings.setValue("windowGeometry", self.saveGeometry())
        settings.setValue("splitterState", self._splitter.saveState())
        settings.setValue("zoomFactor", self._zoom_factor)
        settings.setValue("theme", self._current_theme)
        settings.setValue("contentWidth", self._current_width)
        settings.setValue("panelVisible", self._toc_dock.isVisible())
        settings.remove("darkMode")

    def closeEvent(self, event):
        if self._maybe_save():
            self._save_geometry()
            event.accept()
        else:
            event.ignore()


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MarkEdit")

    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    window = MarkdownApp(file_path)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
