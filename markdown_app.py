#!/usr/bin/env python3
"""Application Markdown Viewer/Editor/Printer avec PyQt6 et QWebEngine."""

import sys
import os
import tempfile

from PyQt6.QtCore import Qt, QUrl, QMarginsF, QSize
from PyQt6.QtGui import (
    QAction, QActionGroup, QKeySequence, QIcon, QPageLayout, QPageSize, QPainter,
    QTextCharFormat, QColor, QTextDocument,
)
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QPlainTextEdit,
    QFileDialog, QMessageBox, QToolBar, QStatusBar, QMenuBar,
    QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLabel, QCheckBox,
)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView

import markdown
from pygments.formatters import HtmlFormatter

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

MARKDOWN_EXTENSIONS = [
    "tables", "fenced_code", "codehilite", "toc", "nl2br",
    "sane_lists", "smarty", "attr_list", "def_list",
    "footnotes", "admonition", "meta",
]

MARKDOWN_EXT_CONFIGS = {
    "codehilite": {"css_class": "highlight", "guess_lang": True},
}

# CSS Pygments pour la coloration syntaxique
_PYGMENTS_CSS = HtmlFormatter(style="default").get_style_defs(".highlight")

DEFAULT_CSS = (
    """
/* --- Typographie générale --- */
body {
    font-family: "Segoe UI", "Noto Sans", Arial, Helvetica, sans-serif;
    font-size: 16px;
    line-height: 1.7;
    color: #1a1a1a;
    background: #ffffff;
    max-width: 860px;
    margin: 0 auto;
    padding: 30px 40px;
}

h1, h2, h3, h4, h5, h6 {
    margin-top: 1.4em;
    margin-bottom: 0.6em;
    font-weight: 600;
    line-height: 1.3;
    color: #111;
}
h1 { font-size: 2em; border-bottom: 2px solid #e0e0e0; padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid #e8e8e8; padding-bottom: 0.25em; }
h3 { font-size: 1.25em; }
h4 { font-size: 1.1em; }

p { margin: 0.8em 0; }

a { color: #0366d6; text-decoration: none; }
a:hover { text-decoration: underline; }

/* --- Listes --- */
ul, ol { padding-left: 2em; margin: 0.6em 0; }
li { margin: 0.25em 0; }

/* --- Tableaux --- */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}
th, td {
    border: 1px solid #d0d0d0;
    padding: 8px 12px;
    text-align: left;
}
th {
    background: #f0f0f0;
    font-weight: 600;
}
tr:nth-child(even) { background: #fafafa; }

/* --- Code --- */
code {
    font-family: "Fira Code", "Source Code Pro", "Consolas", monospace;
    font-size: 0.9em;
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
}
pre {
    background: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    line-height: 1.5;
    border: 1px solid #e1e4e8;
}
pre code {
    background: none;
    padding: 0;
    font-size: 0.88em;
}

/* --- Pygments --- */
"""
    + _PYGMENTS_CSS
    + """

/* --- Blockquotes --- */
blockquote {
    border-left: 4px solid #3b82f6;
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #eff6ff;
    color: #333;
}
blockquote p { margin: 0.4em 0; }

/* --- Admonitions --- */
.admonition {
    border-left: 4px solid #888;
    padding: 12px 16px;
    margin: 1em 0;
    border-radius: 4px;
    background: #f9f9f9;
}
.admonition-title {
    font-weight: 700;
    margin-bottom: 0.4em;
}
.admonition.note, .admonition.tip { border-left-color: #3b82f6; background: #eff6ff; }
.admonition.warning { border-left-color: #f59e0b; background: #fffbeb; }
.admonition.danger, .admonition.error { border-left-color: #ef4444; background: #fef2f2; }

/* --- Notes de bas de page --- */
.footnote {
    font-size: 0.85em;
    color: #555;
    border-top: 1px solid #ddd;
    margin-top: 2em;
    padding-top: 0.8em;
}

/* --- Règle horizontale --- */
hr {
    border: none;
    border-top: 2px solid #e0e0e0;
    margin: 2em 0;
}

/* --- Images --- */
img {
    max-width: 100%;
    height: auto;
}

/* --- Table des matières --- */
.toc {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 12px 20px;
    margin: 1em 0;
}
.toc ul { list-style: none; padding-left: 1.2em; }
.toc > ul { padding-left: 0; }

/* --- Listes de définitions --- */
dt { font-weight: 600; margin-top: 0.8em; }
dd { margin-left: 1.5em; margin-bottom: 0.5em; }

/* --- Impression --- */
@media print {
    body {
        font-size: 12pt;
        color: #000;
        background: #fff;
        max-width: none;
        margin: 0;
        padding: 0;
    }
    pre {
        white-space: pre-wrap;
        word-wrap: break-word;
        border: 1px solid #ccc;
    }
    a { color: #000; text-decoration: underline; }
    a[href^="http"]::after { content: " (" attr(href) ")"; font-size: 0.8em; color: #555; }
    blockquote { border-left-color: #000; background: none; }
    .admonition { background: none; }
    h1 { border-bottom-color: #000; }
    table, th, td { border-color: #000; }
    tr:nth-child(even) { background: none; }
}
"""
)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<style>
{css}
</style>
</head>
<body>
{body}
</body>
</html>"""


# ---------------------------------------------------------------------------
# Application principale
# ---------------------------------------------------------------------------

class MarkdownApp(QMainWindow):
    """Fenêtre principale : affichage, édition et impression Markdown."""

    def __init__(self, file_path=None):
        super().__init__()
        self._current_file = None
        self._current_css = DEFAULT_CSS
        self._custom_css_path = None
        self._modified = False

        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()

        self.resize(1000, 750)
        self._update_title()

        if file_path and os.path.isfile(file_path):
            self._open_file(file_path)
        else:
            self._new_file()

    # -----------------------------------------------------------------------
    # Mise en place de l'interface
    # -----------------------------------------------------------------------

    def _setup_ui(self):
        self._stack = QStackedWidget()

        # Index 0 : affichage
        self._web_view = QWebEngineView()
        self._stack.addWidget(self._web_view)

        # Index 1 : édition
        self._editor = QPlainTextEdit()
        self._editor.setTabStopDistance(32)
        font = self._editor.font()
        font.setFamily("Fira Code, Source Code Pro, Consolas, monospace")
        font.setPointSize(12)
        self._editor.setFont(font)
        self._stack.addWidget(self._editor)

        # Barre de recherche
        self._setup_search_bar()

        # Widget central : stack + barre de recherche
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._stack)
        layout.addWidget(self._search_bar)
        self.setCentralWidget(central)

    def _setup_menus(self):
        bar = self.menuBar()

        # --- Fichier ---
        file_menu = bar.addMenu("&Fichier")

        self._act_new = QAction("&Nouveau", self)
        self._act_new.setShortcut(QKeySequence.StandardKey.New)
        file_menu.addAction(self._act_new)

        self._act_open = QAction("&Ouvrir…", self)
        self._act_open.setShortcut(QKeySequence.StandardKey.Open)
        file_menu.addAction(self._act_open)

        file_menu.addSeparator()

        self._act_save = QAction("&Enregistrer", self)
        self._act_save.setShortcut(QKeySequence.StandardKey.Save)
        file_menu.addAction(self._act_save)

        self._act_save_as = QAction("Enregistrer &sous…", self)
        self._act_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        file_menu.addAction(self._act_save_as)

        file_menu.addSeparator()

        self._act_print = QAction("&Imprimer…", self)
        self._act_print.setShortcut(QKeySequence.StandardKey.Print)
        file_menu.addAction(self._act_print)

        file_menu.addSeparator()

        self._act_quit = QAction("&Quitter", self)
        self._act_quit.setShortcut(QKeySequence.StandardKey.Quit)
        file_menu.addAction(self._act_quit)

        # --- Édition ---
        edit_menu = bar.addMenu("&Édition")

        self._act_search = QAction("&Rechercher…", self)
        self._act_search.setShortcut(QKeySequence("Ctrl+F"))
        edit_menu.addAction(self._act_search)

        # --- Affichage ---
        view_menu = bar.addMenu("&Affichage")

        self._act_view = QAction("Mode &Affichage", self)
        self._act_view.setShortcut(QKeySequence("F5"))
        self._act_view.setCheckable(True)
        view_menu.addAction(self._act_view)

        self._act_edit = QAction("Mode &Édition", self)
        self._act_edit.setShortcut(QKeySequence("F6"))
        self._act_edit.setCheckable(True)
        view_menu.addAction(self._act_edit)

        self._mode_group = QActionGroup(self)
        self._mode_group.addAction(self._act_view)
        self._mode_group.addAction(self._act_edit)
        self._mode_group.setExclusive(True)

        # --- Outils ---
        tools_menu = bar.addMenu("&Outils")

        self._act_load_css = QAction("&Charger CSS…", self)
        tools_menu.addAction(self._act_load_css)

        self._act_reset_css = QAction("&Restaurer CSS par défaut", self)
        tools_menu.addAction(self._act_reset_css)

    def _setup_toolbar(self):
        tb = QToolBar("Barre d'outils")
        tb.setMovable(False)
        self.addToolBar(tb)

        tb.addAction(self._act_new)
        tb.addAction(self._act_open)
        tb.addAction(self._act_save)
        tb.addAction(self._act_save_as)
        tb.addSeparator()
        tb.addAction(self._act_print)
        tb.addSeparator()
        tb.addAction(self._act_search)
        tb.addSeparator()
        tb.addAction(self._act_view)
        tb.addAction(self._act_edit)
        tb.addSeparator()
        tb.addAction(self._act_load_css)
        tb.addAction(self._act_reset_css)

    def _setup_statusbar(self):
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)

    def _connect_signals(self):
        self._act_new.triggered.connect(self._new_file)
        self._act_open.triggered.connect(self._on_open)
        self._act_save.triggered.connect(self._on_save)
        self._act_save_as.triggered.connect(self._on_save_as)
        self._act_print.triggered.connect(self._on_print)
        self._act_quit.triggered.connect(self.close)

        self._act_view.triggered.connect(lambda: self._switch_mode("view"))
        self._act_edit.triggered.connect(lambda: self._switch_mode("edit"))

        self._act_load_css.triggered.connect(self._on_load_css)
        self._act_reset_css.triggered.connect(self._on_reset_css)

        self._act_search.triggered.connect(self._toggle_search)

        self._editor.textChanged.connect(self._on_text_changed)

    # -----------------------------------------------------------------------
    # Recherche
    # -----------------------------------------------------------------------

    def _setup_search_bar(self):
        """Crée la barre de recherche (initialement masquée)."""
        self._search_bar = QWidget()
        self._search_bar.setVisible(False)
        hl = QHBoxLayout(self._search_bar)
        hl.setContentsMargins(6, 4, 6, 4)
        hl.setSpacing(4)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Rechercher…")
        self._search_input.setClearButtonEnabled(True)
        hl.addWidget(self._search_input, 1)

        self._search_prev_btn = QPushButton("▲")
        self._search_prev_btn.setFixedWidth(32)
        self._search_prev_btn.setToolTip("Occurrence précédente (Shift+Entrée)")
        hl.addWidget(self._search_prev_btn)

        self._search_next_btn = QPushButton("▼")
        self._search_next_btn.setFixedWidth(32)
        self._search_next_btn.setToolTip("Occurrence suivante (Entrée)")
        hl.addWidget(self._search_next_btn)

        self._search_case_cb = QCheckBox("Respecter la casse")
        hl.addWidget(self._search_case_cb)

        self._search_count_label = QLabel()
        self._search_count_label.setMinimumWidth(60)
        hl.addWidget(self._search_count_label)

        self._search_close_btn = QPushButton("✕")
        self._search_close_btn.setFixedWidth(28)
        self._search_close_btn.setToolTip("Fermer (Échap)")
        hl.addWidget(self._search_close_btn)

        # Signaux de la barre de recherche
        self._search_input.textChanged.connect(self._on_search_text_changed)
        self._search_next_btn.clicked.connect(self._search_next)
        self._search_prev_btn.clicked.connect(self._search_prev)
        self._search_case_cb.toggled.connect(self._on_search_text_changed)
        self._search_close_btn.clicked.connect(self._close_search)

        # Entrée / Shift+Entrée dans le champ de recherche
        self._search_input.returnPressed.connect(self._search_next)

        # État interne de la recherche
        self._search_matches = []       # liste de QTextCursor pour le mode éditeur
        self._search_current_idx = -1   # index de l'occurrence courante

    def _toggle_search(self):
        """Affiche ou donne le focus à la barre de recherche."""
        self._search_bar.setVisible(True)
        self._search_input.setFocus()
        self._search_input.selectAll()
        # Relancer la recherche si du texte est déjà saisi
        if self._search_input.text():
            self._on_search_text_changed()

    def _close_search(self):
        """Masque la barre de recherche et efface le surlignage."""
        self._search_bar.setVisible(False)
        self._search_count_label.clear()
        self._search_matches.clear()
        self._search_current_idx = -1
        # Effacer le surlignage éditeur
        self._editor.setExtraSelections([])
        # Effacer la recherche WebEngine
        self._web_view.findText("")

    def _on_search_text_changed(self):
        """Relance la recherche à chaque modification du champ."""
        text = self._search_input.text()
        if not text:
            self._search_count_label.clear()
            self._search_matches.clear()
            self._search_current_idx = -1
            self._editor.setExtraSelections([])
            self._web_view.findText("")
            return

        if self._stack.currentIndex() == 1:
            # Mode édition
            self._find_all_in_editor(text)
        else:
            # Mode affichage
            self._find_in_webview(text)

    def _find_all_in_editor(self, text):
        """Trouve toutes les occurrences dans l'éditeur et surligne."""
        doc = self._editor.document()
        case_sensitive = self._search_case_cb.isChecked()

        flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            flags = QTextDocument.FindFlag.FindCaseSensitively

        self._search_matches.clear()
        cursor = QTextDocument.find(doc, text, 0, flags)
        while not cursor.isNull():
            self._search_matches.append(cursor)
            cursor = QTextDocument.find(doc, text, cursor, flags)

        if self._search_matches:
            # Positionner sur la première occurrence à partir du curseur actuel
            current_pos = self._editor.textCursor().position()
            self._search_current_idx = 0
            for i, c in enumerate(self._search_matches):
                if c.selectionStart() >= current_pos:
                    self._search_current_idx = i
                    break
            self._update_editor_highlights()
        else:
            self._search_current_idx = -1
            self._editor.setExtraSelections([])
            self._search_count_label.setText("0/0")

    def _find_in_webview(self, text):
        """Lance la recherche dans le QWebEngineView."""
        from PyQt6.QtWebEngineCore import QWebEnginePage
        flags = QWebEnginePage.FindFlag(0)
        if self._search_case_cb.isChecked():
            flags = QWebEnginePage.FindFlag.FindCaseSensitively
        self._web_view.findText(text, flags)
        self._search_count_label.setText("")

    def _search_next(self):
        """Aller à l'occurrence suivante."""
        if not self._search_input.text():
            return

        if self._stack.currentIndex() == 1:
            # Mode édition
            if not self._search_matches:
                return
            self._search_current_idx = (self._search_current_idx + 1) % len(self._search_matches)
            self._update_editor_highlights()
        else:
            # Mode affichage
            self._find_in_webview(self._search_input.text())

    def _search_prev(self):
        """Aller à l'occurrence précédente."""
        if not self._search_input.text():
            return

        if self._stack.currentIndex() == 1:
            # Mode édition
            if not self._search_matches:
                return
            self._search_current_idx = (self._search_current_idx - 1) % len(self._search_matches)
            self._update_editor_highlights()
        else:
            # Mode affichage – recherche en arrière
            from PyQt6.QtWebEngineCore import QWebEnginePage
            flags = QWebEnginePage.FindFlag.FindBackward
            if self._search_case_cb.isChecked():
                flags |= QWebEnginePage.FindFlag.FindCaseSensitively
            self._web_view.findText(self._search_input.text(), flags)

    def _update_editor_highlights(self):
        """Met à jour le surlignage des occurrences dans l'éditeur."""
        selections = []

        # Surlignage jaune pour toutes les occurrences
        fmt_all = QTextCharFormat()
        fmt_all.setBackground(QColor("#FFFF00"))  # jaune

        # Surlignage orange pour l'occurrence courante
        fmt_current = QTextCharFormat()
        fmt_current.setBackground(QColor("#FF8C00"))  # orange
        fmt_current.setForeground(QColor("#FFFFFF"))

        for i, cursor in enumerate(self._search_matches):
            sel = QPlainTextEdit.ExtraSelection()
            sel.cursor = cursor
            if i == self._search_current_idx:
                sel.format = fmt_current
            else:
                sel.format = fmt_all
            selections.append(sel)

        self._editor.setExtraSelections(selections)

        # Déplacer le curseur visible sur l'occurrence courante
        if 0 <= self._search_current_idx < len(self._search_matches):
            tc = self._search_matches[self._search_current_idx]
            visible_cursor = self._editor.textCursor()
            visible_cursor.setPosition(tc.selectionStart())
            self._editor.setTextCursor(visible_cursor)
            self._editor.centerCursor()

        # Mettre à jour le compteur
        total = len(self._search_matches)
        current = self._search_current_idx + 1 if total > 0 else 0
        self._search_count_label.setText(f"{current}/{total}")

    # -----------------------------------------------------------------------
    # Rendu Markdown
    # -----------------------------------------------------------------------

    def _render(self):
        """Convertit le texte Markdown en HTML et l'affiche dans le QWebEngineView."""
        source = self._editor.toPlainText()
        md = markdown.Markdown(
            extensions=MARKDOWN_EXTENSIONS,
            extension_configs=MARKDOWN_EXT_CONFIGS,
        )
        body = md.convert(source)
        html = HTML_TEMPLATE.format(css=self._current_css, body=body)

        base_url = QUrl("file:///")
        if self._current_file:
            base_url = QUrl.fromLocalFile(os.path.dirname(self._current_file) + "/")
        self._web_view.setHtml(html, base_url)

    # -----------------------------------------------------------------------
    # Modes affichage / édition
    # -----------------------------------------------------------------------

    def _switch_mode(self, mode):
        if mode == "view":
            self._render()
            self._stack.setCurrentIndex(0)
            self._act_view.setChecked(True)
            self._statusbar.showMessage("Mode : Affichage")
        else:
            self._stack.setCurrentIndex(1)
            self._act_edit.setChecked(True)
            self._statusbar.showMessage("Mode : Édition")
        # Relancer la recherche dans le nouveau mode si la barre est visible
        if self._search_bar.isVisible() and self._search_input.text():
            self._on_search_text_changed()

    # -----------------------------------------------------------------------
    # Opérations fichier
    # -----------------------------------------------------------------------

    def _new_file(self):
        if not self._maybe_save():
            return
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
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le fichier :\n{e}")
            return
        self._current_file = path
        self._editor.setPlainText(content)
        self._set_modified(False)
        self._switch_mode("view")
        self._update_title()

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
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._editor.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer :\n{e}")
            return
        self._current_file = path
        self._set_modified(False)
        self._update_title()
        self._statusbar.showMessage(f"Enregistré : {path}", 3000)

    # -----------------------------------------------------------------------
    # Impression
    # -----------------------------------------------------------------------

    def _on_print(self):
        """Lance l'impression via génération PDF puis rendu QPrinter."""
        # Connecter AVANT le rendu pour éviter la race condition
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
        # Générer le PDF en mémoire via WebEngine
        layout = QPageLayout(QPageSize(QPageSize.PageSizeId.A4),
                             QPageLayout.Orientation.Portrait,
                             QMarginsF(10, 10, 10, 10))
        self._web_view.page().printToPdf(self._on_pdf_ready, layout)

    def _on_pdf_ready(self, pdf_data):
        if not pdf_data:
            QMessageBox.warning(self, "Impression", "La génération PDF a échoué.")
            return

        # Écrire le PDF dans un fichier temporaire
        self._tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        self._tmp_pdf.write(bytes(pdf_data))
        self._tmp_pdf.close()

        # Charger le PDF avec QPdfDocument
        doc = QPdfDocument(self)
        doc.load(self._tmp_pdf.name)

        if doc.pageCount() == 0:
            QMessageBox.warning(self, "Impression", "Le PDF généré est vide.")
            os.unlink(self._tmp_pdf.name)
            return

        # Dialogue d'impression
        self._printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(self._printer, self)
        if dialog.exec() != QPrintDialog.DialogCode.Accepted:
            doc.close()
            os.unlink(self._tmp_pdf.name)
            return

        # Peindre chaque page du PDF sur l'imprimante
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
            img_size = QSize(int(page_size_pt.width() * dpi / 72.0),
                             int(page_size_pt.height() * dpi / 72.0))
            image = doc.render(i, img_size)
            target = painter.viewport()
            painter.drawImage(target, image)

        painter.end()
        doc.close()
        os.unlink(self._tmp_pdf.name)
        self._statusbar.showMessage("Impression terminée.", 3000)

    # -----------------------------------------------------------------------
    # Gestion CSS
    # -----------------------------------------------------------------------

    def _on_load_css(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Charger une feuille de style CSS", "",
            "Fichiers CSS (*.css);;Tous les fichiers (*)",
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._current_css = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger le CSS :\n{e}")
            return
        self._custom_css_path = path
        self._render()
        if self._stack.currentIndex() == 0:
            pass  # render already switches display
        self._statusbar.showMessage(f"CSS chargé : {os.path.basename(path)}", 4000)
        self._update_title()

    def _on_reset_css(self):
        self._current_css = DEFAULT_CSS
        self._custom_css_path = None
        self._render()
        self._statusbar.showMessage("CSS par défaut restauré", 3000)
        self._update_title()

    # -----------------------------------------------------------------------
    # Gestion d'état
    # -----------------------------------------------------------------------

    def _on_text_changed(self):
        if not self._modified:
            self._set_modified(True)

    def _set_modified(self, val):
        self._modified = val
        self._update_title()

    def _update_title(self):
        parts = []
        if self._current_file:
            name = os.path.basename(self._current_file)
        else:
            name = "Sans titre"
        if self._modified:
            name += " *"
        parts.append(name)
        parts.append("Markdown Viewer")
        if self._custom_css_path:
            parts.append(f"[CSS: {os.path.basename(self._custom_css_path)}]")
        self.setWindowTitle(" — ".join(parts))

    def _maybe_save(self):
        """Propose d'enregistrer si le document est modifié.
        Retourne True si on peut continuer, False si l'utilisateur annule.
        """
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
            return not self._modified  # False si l'enregistrement a échoué/été annulé
        if ret == QMessageBox.StandardButton.Cancel:
            return False
        return True  # Discard

    def keyPressEvent(self, event):
        # Échap ferme la barre de recherche si elle est visible
        if event.key() == Qt.Key.Key_Escape and self._search_bar.isVisible():
            self._close_search()
            return
        # Shift+Entrée dans le champ de recherche → occurrence précédente
        if (event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                and event.modifiers() & Qt.KeyboardModifier.ShiftModifier
                and self._search_input.hasFocus()):
            self._search_prev()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        if self._maybe_save():
            event.accept()
        else:
            event.ignore()


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown Viewer")

    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    window = MarkdownApp(file_path)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
