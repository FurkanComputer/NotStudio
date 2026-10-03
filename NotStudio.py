import sys
import os
import ast
import re
import shutil
import subprocess

from PyQt5.QtCore import (
    Qt,
    QRect,
    QSize,
    QProcess,
    pyqtSignal
)

from PyQt5.QtGui import (
    QColor,
    QFont,
    QPainter,
    QTextFormat,
    QTextCharFormat,
    QSyntaxHighlighter,
    QTextCursor,
    QKeySequence
)

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPlainTextEdit,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QTabWidget,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QFileDialog,
    QMessageBox,
    QFontDialog,
    QMenu,
    QAction,
    QInputDialog,
    QFrame,
    QHeaderView,
    QComboBox
)


# =========================================================
# DİL SİSTEMİ
# =========================================================

LANGUAGES = {
    ".py": "Python",
    ".c": "C",
    ".h": "C / Header",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++ / Header",
    ".cs": "C#",
    ".java": "Java",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".js": "JavaScript"
}


def detect_language(path):
    if not path:
        return "Python"

    ext = os.path.splitext(path)[1].lower()

    return LANGUAGES.get(ext, "Text")


# =========================================================
# SYNTAX HIGHLIGHTER
# =========================================================

class MultiLanguageHighlighter(QSyntaxHighlighter):

    def __init__(self, document, language="Python"):
        super().__init__(document)

        self.language = language

        self.keyword_format = self.make_format(
            "#c586c0",
            True
        )

        self.type_format = self.make_format(
            "#4ec9b0",
            True
        )

        self.string_format = self.make_format(
            "#ce9178"
        )

        self.comment_format = self.make_format(
            "#6a9955"
        )

        self.number_format = self.make_format(
            "#b5cea8"
        )

        self.function_format = self.make_format(
            "#dcdcaa"
        )

        self.tag_format = self.make_format(
            "#569cd6"
        )

        self.attribute_format = self.make_format(
            "#9cdcfe"
        )

        self.operator_format = self.make_format(
            "#d4d4d4"
        )

    def make_format(self, color, bold=False):

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))

        if bold:
            fmt.setFontWeight(QFont.Bold)

        return fmt

    def set_language(self, language):

        self.language = language
        self.rehighlight()

    def highlightBlock(self, text):

        if self.language == "Python":
            self.highlight_python(text)

        elif self.language in ("C", "C / Header"):
            self.highlight_c(text)

        elif self.language in ("C++", "C++ / Header"):
            self.highlight_cpp(text)

        elif self.language == "C#":
            self.highlight_csharp(text)

        elif self.language == "Java":
            self.highlight_java(text)

        elif self.language in ("HTML", "Bootstrap"):
            self.highlight_html(text)

        elif self.language == "CSS":
            self.highlight_css(text)

        elif self.language == "JavaScript":
            self.highlight_javascript(text)

    def apply_words(self, text, words, fmt):

        for word in words:

            pattern = rf"\b{re.escape(word)}\b"

            for match in re.finditer(
                pattern,
                text
            ):

                self.setFormat(
                    match.start(),
                    match.end() - match.start(),
                    fmt
                )

    def apply_strings(self, text):

        patterns = [
            r'"(?:\\.|[^"\\])*"',
            r"'(?:\\.|[^'\\])*'"
        ]

        for pattern in patterns:

            for match in re.finditer(
                pattern,
                text
            ):

                self.setFormat(
                    match.start(),
                    match.end() - match.start(),
                    self.string_format
                )

    def apply_numbers(self, text):

        for match in re.finditer(
            r"\b\d+(?:\.\d+)?\b",
            text
        ):

            self.setFormat(
                match.start(),
                match.end() - match.start(),
                self.number_format
            )

    def apply_functions(self, text):

        for match in re.finditer(
            r"\b[A-Za-z_]\w*(?=\s*\()",
            text
        ):

            self.setFormat(
                match.start(),
                match.end() - match.start(),
                self.function_format
            )

    def highlight_comment(self, text, marker="#"):

        index = text.find(marker)

        if index >= 0:

            self.setFormat(
                index,
                len(text) - index,
                self.comment_format
            )

    # -----------------------------------------------------
    # PYTHON
    # -----------------------------------------------------

    def highlight_python(self, text):

        keywords = [
            "and", "as", "assert", "async", "await",
            "break", "case", "class", "continue",
            "def", "del", "elif", "else", "except",
            "False", "finally", "for", "from", "global",
            "if", "import", "in", "is", "lambda",
            "match", "None", "nonlocal", "not", "or",
            "pass", "raise", "return", "True", "try",
            "while", "with", "yield"
        ]

        types = [
            "int", "float", "str", "list",
            "dict", "tuple", "set", "bool",
            "bytes", "object", "Exception",
            "ValueError", "RuntimeError"
        ]

        self.apply_words(
            text,
            keywords,
            self.keyword_format
        )

        self.apply_words(
            text,
            types,
            self.type_format
        )

        self.apply_strings(text)
        self.apply_numbers(text)
        self.apply_functions(text)
        self.highlight_comment(text)

    # -----------------------------------------------------
    # C / C++
    # -----------------------------------------------------

    def highlight_c(self, text):

        keywords = [
            "auto", "break", "case", "char",
            "const", "continue", "default",
            "do", "double", "else", "enum",
            "extern", "float", "for", "goto",
            "if", "int", "long", "register",
            "return", "short", "signed",
            "sizeof", "static", "struct",
            "switch", "typedef", "union",
            "unsigned", "void", "volatile",
            "while"
        ]

        types = [
            "int", "char", "float", "double",
            "long", "short", "void",
            "size_t", "FILE"
        ]

        self.apply_words(
            text,
            keywords,
            self.keyword_format
        )

        self.apply_words(
            text,
            types,
            self.type_format
        )

        self.apply_strings(text)
        self.apply_numbers(text)
        self.apply_functions(text)

        self.highlight_comment(text)

        index = text.find("//")

        if index >= 0:

            self.setFormat(
                index,
                len(text) - index,
                self.comment_format
            )

    # -----------------------------------------------------
    # C++
    # -----------------------------------------------------

    def highlight_cpp(self, text):

        self.highlight_c(text)

        keywords = [
            "class", "namespace", "template",
            "typename", "public", "private",
            "protected", "virtual", "override",
            "new", "delete", "this", "using",
            "try", "catch", "throw", "nullptr",
            "constexpr", "static_cast",
            "dynamic_cast", "const_cast"
        ]

        self.apply_words(
            text,
            keywords,
            self.keyword_format
        )

    # -----------------------------------------------------
    # C#
    # -----------------------------------------------------

    def highlight_csharp(self, text):

        keywords = [
            "abstract", "as", "base", "bool",
            "break", "byte", "case", "catch",
            "char", "class", "const", "continue",
            "decimal", "default", "delegate",
            "do", "double", "else", "enum",
            "event", "explicit", "extern",
            "false", "finally", "fixed",
            "float", "for", "foreach", "goto",
            "if", "implicit", "in", "int",
            "interface", "internal", "is",
            "lock", "long", "namespace", "new",
            "null", "object", "operator",
            "out", "override", "params",
            "private", "protected", "public",
            "readonly", "ref", "return",
            "sbyte", "sealed", "short",
            "sizeof", "stackalloc", "static",
            "string", "struct", "switch",
            "this", "throw", "true", "try",
            "typeof", "uint", "ulong", "unchecked",
            "unsafe", "ushort", "using",
            "virtual", "void", "volatile",
            "while", "async", "await",
            "var"
        ]

        self.apply_words(
            text,
            keywords,
            self.keyword_format
        )

        self.apply_strings(text)
        self.apply_numbers(text)
        self.apply_functions(text)

        self.highlight_comment(text)

        index = text.find("//")

        if index >= 0:

            self.setFormat(
                index,
                len(text) - index,
                self.comment_format
            )

    # -----------------------------------------------------
    # JAVA
    # -----------------------------------------------------

    def highlight_java(self, text):

        keywords = [
            "abstract", "assert", "boolean",
            "break", "byte", "case", "catch",
            "char", "class", "const",
            "continue", "default", "do",
            "double", "else", "enum",
            "extends", "final", "finally",
            "float", "for", "goto",
            "if", "implements", "import",
            "instanceof", "int", "interface",
            "long", "native", "new",
            "package", "private", "protected",
            "public", "return", "short",
            "static", "strictfp", "super",
            "switch", "synchronized", "this",
            "throw", "throws", "transient",
            "try", "void", "volatile",
            "while", "true", "false", "null"
        ]

        self.apply_words(
            text,
            keywords,
            self.keyword_format
        )

        self.apply_strings(text)
        self.apply_numbers(text)
        self.apply_functions(text)

        self.highlight_comment(text)

        index = text.find("//")

        if index >= 0:

            self.setFormat(
                index,
                len(text) - index,
                self.comment_format
            )

    # -----------------------------------------------------
    # HTML / BOOTSTRAP
    # -----------------------------------------------------

    def highlight_html(self, text):

        tag_pattern = r"</?[A-Za-z][^>]*>"

        for match in re.finditer(
            tag_pattern,
            text
        ):

            self.setFormat(
                match.start(),
                match.end() - match.start(),
                self.tag_format
            )

        attr_pattern = r"\b[A-Za-z_:][-A-Za-z0-9_:.]*(?=\s*=)"

        for match in re.finditer(
            attr_pattern,
            text
        ):

            self.setFormat(
                match.start(),
                match.end() - match.start(),
                self.attribute_format
            )

        self.apply_strings(text)

        index = text.find("<!--")

        if index >= 0:

            end = text.find(
                "-->",
                index
            )

            if end >= 0:
                length = end + 3 - index
            else:
                length = len(text) - index

            self.setFormat(
                index,
                length,
                self.comment_format
            )

    # -----------------------------------------------------
    # CSS
    # -----------------------------------------------------

    def highlight_css(self, text):

        selector_pattern = r"[.#]?[A-Za-z_-][\w-]*(?=\s*\{)"

        for match in re.finditer(
            selector_pattern,
            text
        ):

            self.setFormat(
                match.start(),
                match.end() - match.start(),
                self.tag_format
            )

        property_pattern = r"\b[A-Za-z-]+(?=\s*:)"

        for match in re.finditer(
            property_pattern,
            text
        ):

            self.setFormat(
                match.start(),
                match.end() - match.start(),
                self.attribute_format
            )

        self.apply_strings(text)
        self.apply_numbers(text)

        index = text.find("/*")

        if index >= 0:

            end = text.find(
                "*/",
                index
            )

            if end >= 0:
                length = end + 2 - index
            else:
                length = len(text) - index

            self.setFormat(
                index,
                length,
                self.comment_format
            )

    # -----------------------------------------------------
    # JAVASCRIPT
    # -----------------------------------------------------

    def highlight_javascript(self, text):

        keywords = [
            "break", "case", "catch", "class",
            "const", "continue", "debugger",
            "default", "delete", "do", "else",
            "export", "extends", "finally",
            "for", "function", "if", "import",
            "in", "instanceof", "let", "new",
            "return", "super", "switch",
            "this", "throw", "try", "typeof",
            "var", "void", "while", "with",
            "yield", "async", "await",
            "true", "false", "null", "undefined"
        ]

        self.apply_words(
            text,
            keywords,
            self.keyword_format
        )

        self.apply_strings(text)
        self.apply_numbers(text)
        self.apply_functions(text)

        self.highlight_comment(text)

        index = text.find("//")

        if index >= 0:

            self.setFormat(
                index,
                len(text) - index,
                self.comment_format
            )


# =========================================================
# LINE NUMBER AREA
# =========================================================

class LineNumberArea(QWidget):

    def __init__(self, editor):

        super().__init__(editor)

        self.editor = editor

    def sizeHint(self):

        return QSize(
            self.editor.line_number_width(),
            0
        )

    def paintEvent(self, event):

        self.editor.paint_line_numbers(
            event
        )


# =========================================================
# CODE EDITOR
# =========================================================

class CodeEditor(QPlainTextEdit):

    cursor_position_changed = pyqtSignal()
    zoom_changed = pyqtSignal()

    def __init__(self):

        super().__init__()

        self.line_number_area = LineNumberArea(
            self
        )

        self.blockCountChanged.connect(
            self.update_line_number_width
        )

        self.updateRequest.connect(
            self.update_line_number_area
        )

        self.cursorPositionChanged.connect(
            self.highlight_current_line
        )

        self.cursorPositionChanged.connect(
            self.cursor_position_changed.emit
        )

        font = QFont(
            "DejaVu Sans Mono",
            11
        )

        self.setFont(font)

        self.setTabStopWidth(
            4 * self.fontMetrics().width(" ")
        )

        self.setStyleSheet("""
            QPlainTextEdit {
                background: #0f141a;
                color: #d4d4d4;
                border: none;
                padding: 8px;
                selection-background-color: #264f78;
                selection-color: white;
            }
        """)

        self.highlighter = MultiLanguageHighlighter(
            self.document(),
            "Python"
        )

        self.update_line_number_width(0)
        self.highlight_current_line()

    def set_language(self, language):

        self.highlighter.set_language(
            language
        )

    def line_number_width(self):

        digits = len(
            str(
                max(
                    1,
                    self.blockCount()
                )
            )
        )

        return (
            18 +
            self.fontMetrics().width("9") * digits
        )

    def update_line_number_width(self, _):

        self.setViewportMargins(
            self.line_number_width(),
            0,
            0,
            0
        )

    def update_line_number_area(
        self,
        rect,
        dy
    ):

        if dy:

            self.line_number_area.scroll(
                0,
                dy
            )

        else:

            self.line_number_area.update(
                0,
                rect.y(),
                self.line_number_area.width(),
                rect.height()
            )

        if rect.contains(
            self.viewport().rect()
        ):

            self.update_line_number_width(
                0
            )

    def resizeEvent(self, event):

        super().resizeEvent(event)

        cr = self.contentsRect()

        self.line_number_area.setGeometry(
            QRect(
                cr.left(),
                cr.top(),
                self.line_number_width(),
                cr.height()
            )
        )

    def paint_line_numbers(self, event):

        painter = QPainter(
            self.line_number_area
        )

        painter.fillRect(
            event.rect(),
            QColor("#111820")
        )

        block = self.firstVisibleBlock()

        block_number = block.blockNumber()

        top = int(
            self.blockBoundingGeometry(
                block
            ).translated(
                self.contentOffset()
            ).top()
        )

        bottom = (
            top +
            int(
                self.blockBoundingRect(
                    block
                ).height()
            )
        )

        while (
            block.isValid()
            and
            top <= event.rect().bottom()
        ):

            if (
                block.isVisible()
                and
                bottom >= event.rect().top()
            ):

                number = str(
                    block_number + 1
                )

                if (
                    block ==
                    self.textCursor().block()
                ):

                    painter.setPen(
                        QColor("#ffffff")
                    )

                else:

                    painter.setPen(
                        QColor("#64748b")
                    )

                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 8,
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    number
                )

            block = block.next()

            top = bottom

            bottom = (
                top +
                int(
                    self.blockBoundingRect(
                        block
                    ).height()
                )
            )

            block_number += 1

    def highlight_current_line(self):

        selection = QTextEdit.ExtraSelection()

        selection.format.setBackground(
            QColor("#151d26")
        )

        selection.format.setProperty(
            QTextFormat.FullWidthSelection,
            True
        )

        selection.cursor = self.textCursor()

        selection.cursor.clearSelection()

        self.setExtraSelections(
            [selection]
        )

    def keyPressEvent(self, event):

        key = event.key()

        # TAB
        if key == Qt.Key_Tab:

            self.insertPlainText(
                "    "
            )

            return

        # PARANTEZLER
        pairs = {
            Qt.Key_ParenLeft: ("(", ")"),
            Qt.Key_BracketLeft: ("[", "]"),
            Qt.Key_BraceLeft: ("{", "}")
        }

        if key in pairs:

            opening, closing = pairs[key]

            self.insertPlainText(
                opening + closing
            )

            cursor = self.textCursor()

            cursor.movePosition(
                QTextCursor.Left
            )

            self.setTextCursor(
                cursor
            )

            return

        # TIRNAK
        if event.text() in ['"', "'"]:

            quote = event.text()

            self.insertPlainText(
                quote + quote
            )

            cursor = self.textCursor()

            cursor.movePosition(
                QTextCursor.Left
            )

            self.setTextCursor(
                cursor
            )

            return

        # ENTER / AUTO INDENT
        if key in (
            Qt.Key_Return,
            Qt.Key_Enter
        ):

            cursor = self.textCursor()

            line = cursor.block().text()

            indentation = re.match(
                r"\s*",
                line
            ).group()

            extra = ""

            if line.strip().endswith(":"):

                extra = "    "

            super().keyPressEvent(
                event
            )

            self.insertPlainText(
                indentation + extra
            )

            return

        super().keyPressEvent(
            event
        )

    def zoom_in(self):

        self.zoomIn(1)
        self.zoom_changed.emit()

    def zoom_out(self):

        self.zoomOut(1)
        self.zoom_changed.emit()

    def reset_zoom(self):

        font = self.font()

        font.setPointSize(
            11
        )

        self.setFont(
            font
        )

        self.zoom_changed.emit()


# =========================================================
# PROBLEMS
# =========================================================

class ProblemsPanel(QTableWidget):

    def __init__(self):

        super().__init__(
            0,
            3
        )

        self.setHorizontalHeaderLabels([
            "Tür",
            "Satır",
            "Mesaj"
        ])

        self.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        self.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents
        )

        self.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.Stretch
        )

        self.verticalHeader().setVisible(
            False
        )

        self.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.setStyleSheet("""
            QTableWidget {
                background: #10161d;
                color: #d4d4d4;
                border: none;
                gridline-color: #202933;
            }

            QHeaderView::section {
                background: #161d25;
                color: #94a3b8;
                border: none;
                padding: 7px;
            }

            QTableWidget::item:selected {
                background: #1e3a5f;
            }
        """)

    def clear_problems(self):

        self.setRowCount(0)

    def add_problem(
        self,
        problem_type,
        line,
        message
    ):

        row = self.rowCount()

        self.insertRow(
            row
        )

        self.setItem(
            row,
            0,
            QTableWidgetItem(
                problem_type
            )
        )

        self.setItem(
            row,
            1,
            QTableWidgetItem(
                str(line)
            )
        )

        self.setItem(
            row,
            2,
            QTableWidgetItem(
                message
            )
        )


# =========================================================
# NOTSTUDIO
# =========================================================

class NotStudio(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "NotStudio - Multi Language IDE"
        )

        self.resize(
            1500,
            900
        )

        self.current_project = None

        self.process = None

        self.build_ui()

        self.create_menus()

        self.apply_theme()

        self.new_file()

        self.statusBar().showMessage(
            "NotStudio hazır"
        )

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):

        central = QWidget()

        main_layout = QVBoxLayout(
            central
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(
            0
        )

        # -------------------------------------------------
        # TOP BAR
        # -------------------------------------------------

        top_bar = QFrame()

        top_bar.setFixedHeight(
            48
        )

        top_layout = QHBoxLayout(
            top_bar
        )

        top_layout.setContentsMargins(
            10,
            6,
            10,
            6
        )

        actions = [
            ("Yeni", self.new_file),
            ("Aç", self.open_file),
            ("Kaydet", self.save_file),
            ("Proje", self.open_project),
            ("Çalıştır", self.run_file),
            ("Durdur", self.stop_process),
            ("Syntax", self.check_syntax)
        ]

        for text, function in actions:

            button = QPushButton(
                text
            )

            button.clicked.connect(
                function
            )

            top_layout.addWidget(
                button
            )

        top_layout.addStretch()

        self.language_selector = QComboBox()

        self.language_selector.addItems([
            "Python",
            "C",
            "C++",
            "C#",
            "Java",
            "HTML",
            "CSS",
            "JavaScript",
            "Bootstrap"
        ])

        self.language_selector.currentTextChanged.connect(
            self.manual_language_change
        )

        top_layout.addWidget(
            QLabel("Dil:")
        )

        top_layout.addWidget(
            self.language_selector
        )

        main_layout.addWidget(
            top_bar
        )

        # -------------------------------------------------
        # MAIN SPLITTER
        # -------------------------------------------------

        horizontal = QSplitter(
            Qt.Horizontal
        )

        # =================================================
        # EXPLORER
        # =================================================

        explorer = QFrame()

        explorer_layout = QVBoxLayout(
            explorer
        )

        explorer_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        explorer_title = QLabel(
            "  PROJE GEZGİNİ"
        )

        explorer_title.setObjectName(
            "panelTitle"
        )

        explorer_layout.addWidget(
            explorer_title
        )

        self.project_label = QLabel(
            "  Proje seçilmedi"
        )

        self.project_label.setWordWrap(
            True
        )

        explorer_layout.addWidget(
            self.project_label
        )

        self.tree = QTreeWidget()

        self.tree.setHeaderHidden(
            True
        )

        self.tree.itemDoubleClicked.connect(
            self.tree_open_file
        )

        self.tree.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.tree.customContextMenuRequested.connect(
            self.explorer_context_menu
        )

        explorer_layout.addWidget(
            self.tree
        )

        horizontal.addWidget(
            explorer
        )

        # =================================================
        # EDITOR
        # =================================================

        editor_container = QWidget()

        editor_layout = QVBoxLayout(
            editor_container
        )

        editor_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.tabs = QTabWidget()

        self.tabs.setTabsClosable(
            True
        )

        self.tabs.setMovable(
            True
        )

        self.tabs.tabCloseRequested.connect(
            self.close_tab
        )

        self.tabs.currentChanged.connect(
            self.tab_changed
        )

        editor_layout.addWidget(
            self.tabs
        )

        horizontal.addWidget(
            editor_container
        )

        # =================================================
        # INSPECTOR
        # =================================================

        inspector = QFrame()

        inspector_layout = QVBoxLayout(
            inspector
        )

        inspector_layout.setContentsMargins(
            10,
            0,
            10,
            10
        )

        title = QLabel(
            "INSPECTOR"
        )

        title.setObjectName(
            "panelTitle"
        )

        inspector_layout.addWidget(
            title
        )

        self.info_name = QLabel(
            "Dosya: -"
        )

        self.info_path = QLabel(
            "Yol: -"
        )

        self.info_language = QLabel(
            "Dil: -"
        )

        self.info_lines = QLabel(
            "Satır: -"
        )

        self.info_size = QLabel(
            "Boyut: -"
        )

        self.info_runtime = QLabel(
            "Çalıştırıcı: -"
        )

        for label in [
            self.info_name,
            self.info_path,
            self.info_language,
            self.info_lines,
            self.info_size,
            self.info_runtime
        ]:

            label.setWordWrap(
                True
            )

            inspector_layout.addWidget(
                label
            )

        inspector_layout.addStretch()

        horizontal.addWidget(
            inspector
        )

        horizontal.setSizes([
            250,
            950,
            250
        ])

        main_layout.addWidget(
            horizontal,
            1
        )

        # =================================================
        # BOTTOM
        # =================================================

        self.bottom_tabs = QTabWidget()

        self.output = QTextEdit()

        self.output.setReadOnly(
            True
        )

        self.output.setFont(
            QFont(
                "DejaVu Sans Mono",
                10
            )
        )

        self.output.setPlaceholderText(
            "Program çıktısı burada..."
        )

        self.terminal = QTextEdit()

        self.terminal.setReadOnly(
            True
        )

        self.terminal.setFont(
            QFont(
                "DejaVu Sans Mono",
                10
            )
        )

        self.terminal.setPlainText(
            "$ NotStudio Terminal\n"
            "$ Çok dilli geliştirme ortamı hazır.\n"
        )

        self.problems = ProblemsPanel()

        self.bottom_tabs.addTab(
            self.output,
            "Output"
        )

        self.bottom_tabs.addTab(
            self.terminal,
            "Terminal"
        )

        self.bottom_tabs.addTab(
            self.problems,
            "Problems"
        )

        self.bottom_tabs.setMaximumHeight(
            230
        )

        main_layout.addWidget(
            self.bottom_tabs
        )

        self.setCentralWidget(
            central
        )

    # =====================================================
    # MENUS
    # =====================================================

    def create_menus(self):

        # DOSYA

        file_menu = self.menuBar().addMenu(
            "Dosya"
        )

        self.add_action(
            file_menu,
            "Yeni",
            self.new_file,
            "Ctrl+N"
        )

        self.add_action(
            file_menu,
            "Aç",
            self.open_file,
            "Ctrl+O"
        )

        self.add_action(
            file_menu,
            "Kaydet",
            self.save_file,
            "Ctrl+S"
        )

        self.add_action(
            file_menu,
            "Farklı Kaydet",
            self.save_file_as,
            "Ctrl+Shift+S"
        )

        self.add_action(
            file_menu,
            "Sekmeyi Kapat",
            self.close_current_tab,
            "Ctrl+W"
        )

        file_menu.addSeparator()

        self.add_action(
            file_menu,
            "Çıkış",
            self.close
        )

        # DÜZEN

        edit_menu = self.menuBar().addMenu(
            "Düzen"
        )

        self.add_action(
            edit_menu,
            "Geri Al",
            lambda: self.current_editor().undo(),
            "Ctrl+Z"
        )

        self.add_action(
            edit_menu,
            "Yinele",
            lambda: self.current_editor().redo(),
            "Ctrl+Y"
        )

        edit_menu.addSeparator()

        self.add_action(
            edit_menu,
            "Kes",
            lambda: self.current_editor().cut(),
            "Ctrl+X"
        )

        self.add_action(
            edit_menu,
            "Kopyala",
            lambda: self.current_editor().copy(),
            "Ctrl+C"
        )

        self.add_action(
            edit_menu,
            "Yapıştır",
            lambda: self.current_editor().paste(),
            "Ctrl+V"
        )

        self.add_action(
            edit_menu,
            "Ara",
            self.find_text,
            "Ctrl+F"
        )

        # GÖRÜNÜM

        view_menu = self.menuBar().addMenu(
            "Görünüm"
        )

        self.add_action(
            view_menu,
            "Zoom +",
            self.zoom_in,
            "Ctrl++"
        )

        self.add_action(
            view_menu,
            "Zoom -",
            self.zoom_out,
            "Ctrl+-"
        )

        self.add_action(
            view_menu,
            "Zoom Sıfırla",
            self.zoom_reset
        )

        # ÇALIŞTIR

        run_menu = self.menuBar().addMenu(
            "Çalıştır"
        )

        self.add_action(
            run_menu,
            "Çalıştır",
            self.run_file,
            "F5"
        )

        self.add_action(
            run_menu,
            "Durdur",
            self.stop_process,
            "Shift+F5"
        )

        self.add_action(
            run_menu,
            "Syntax Kontrolü",
            self.check_syntax
        )

        # ARAÇLAR

        tools_menu = self.menuBar().addMenu(
            "Araçlar"
        )

        self.add_action(
            tools_menu,
            "Font Ayarları",
            self.change_font
        )

        self.add_action(
            tools_menu,
            "Derleyicileri Kontrol Et",
            self.check_compilers
        )

        self.add_action(
            tools_menu,
            "Proje Aç",
            self.open_project
        )

    def add_action(
        self,
        menu,
        text,
        function,
        shortcut=None
    ):

        action = QAction(
            text,
            self
        )

        if shortcut:
            action.setShortcut(
                QKeySequence(
                    shortcut
                )
            )

        action.triggered.connect(
            function
        )

        menu.addAction(
            action
        )

    # =====================================================
    # THEME
    # =====================================================

    def apply_theme(self):

        self.setStyleSheet("""
            QMainWindow {
                background: #0b1015;
                color: #d4d4d4;
            }

            QMenuBar {
                background: #0d1319;
                color: #cbd5e1;
                border-bottom: 1px solid #202933;
            }

            QMenuBar::item {
                padding: 7px 12px;
            }

            QMenuBar::item:selected {
                background: #1b2633;
            }

            QMenu {
                background: #111820;
                color: #d4d4d4;
                border: 1px solid #263241;
            }

            QMenu::item:selected {
                background: #1e3a5f;
            }

            QFrame {
                background: #0d1319;
                color: #d4d4d4;
            }

            QLabel {
                color: #94a3b8;
            }

            QLabel#panelTitle {
                color: #e2e8f0;
                font-weight: bold;
                padding: 12px 0;
                border-bottom: 1px solid #202933;
            }

            QPushButton {
                background: #16202b;
                color: #d4d4d4;
                border: 1px solid #263241;
                border-radius: 4px;
                padding: 6px 14px;
            }

            QPushButton:hover {
                background: #1d2a38;
                border-color: #3b82f6;
            }

            QPushButton:pressed {
                background: #1e3a5f;
            }

            QComboBox {
                background: #111820;
                color: #d4d4d4;
                border: 1px solid #263241;
                padding: 5px 10px;
            }

            QComboBox QAbstractItemView {
                background: #111820;
                color: #d4d4d4;
                selection-background-color: #1e3a5f;
            }

            QTreeWidget {
                background: #0d1319;
                color: #cbd5e1;
                border: none;
                outline: none;
            }

            QTreeWidget::item {
                padding: 5px;
            }

            QTreeWidget::item:hover {
                background: #16202b;
            }

            QTreeWidget::item:selected {
                background: #1e3a5f;
                color: white;
            }

            QTabWidget::pane {
                border: none;
                background: #0f141a;
            }

            QTabBar::tab {
                background: #111820;
                color: #7f8c9d;
                padding: 9px 18px;
                border-right: 1px solid #202933;
            }

            QTabBar::tab:selected {
                background: #0f141a;
                color: #ffffff;
                border-top: 2px solid #3b82f6;
            }

            QSplitter::handle {
                background: #202933;
            }

            QStatusBar {
                background: #111820;
                color: #94a3b8;
                border-top: 1px solid #202933;
            }

            QScrollBar:vertical {
                background: #0d1319;
                width: 10px;
            }

            QScrollBar::handle:vertical {
                background: #263241;
                border-radius: 4px;
            }
        """)

    # =====================================================
    # EDITOR
    # =====================================================

    def current_editor(self):

        widget = self.tabs.currentWidget()

        if isinstance(
            widget,
            CodeEditor
        ):

            return widget

        return None

    def new_file(self):

        editor = CodeEditor()

        editor.setProperty(
            "file_path",
            None
        )

        editor.setProperty(
            "language",
            "Python"
        )

        editor.document().modificationChanged.connect(
            lambda changed, e=editor:
            self.update_tab_title(
                e,
                changed
            )
        )

        editor.cursor_position_changed.connect(
            self.update_status
        )

        editor.textChanged.connect(
            self.update_inspector
        )

        index = self.tabs.addTab(
            editor,
            "Untitled.py"
        )

        self.tabs.setCurrentIndex(
            index
        )

        self.language_selector.setCurrentText(
            "Python"
        )

        self.update_inspector()

    # =====================================================
    # OPEN
    # =====================================================

    def open_file(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Dosya Aç",
            "",
            "Kod Dosyaları (*.py *.c *.h *.cpp *.cc *.cxx *.hpp *.cs *.java *.html *.htm *.css *.js);;Tüm Dosyalar (*)"
        )

        if path:

            self.open_path(
                path
            )

    def open_path(self, path):

        for i in range(
            self.tabs.count()
        ):

            editor = self.tabs.widget(
                i
            )

            if (
                editor.property(
                    "file_path"
                )
                == path
            ):

                self.tabs.setCurrentIndex(
                    i
                )

                return

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                content = file.read()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Açma Hatası",
                str(e)
            )

            return

        language = detect_language(
            path
        )

        editor = CodeEditor()

        editor.setPlainText(
            content
        )

        editor.setProperty(
            "file_path",
            path
        )

        editor.setProperty(
            "language",
            language
        )

        editor.set_language(
            language
        )

        editor.document().setModified(
            False
        )

        editor.document().modificationChanged.connect(
            lambda changed, e=editor:
            self.update_tab_title(
                e,
                changed
            )
        )

        editor.cursor_position_changed.connect(
            self.update_status
        )

        editor.textChanged.connect(
            self.update_inspector
        )

        index = self.tabs.addTab(
            editor,
            os.path.basename(path)
        )

        self.tabs.setCurrentIndex(
            index
        )

        self.language_selector.setCurrentText(
            language
            if language != "C / Header"
            and language != "C++ / Header"
            else (
                "C"
                if language == "C / Header"
                else "C++"
            )
        )

        self.update_project_tree()
        self.update_inspector()

        self.statusBar().showMessage(
            f"Açıldı: {path}"
        )

    # =====================================================
    # SAVE
    # =====================================================

    def save_file(self):

        editor = self.current_editor()

        if not editor:
            return False

        path = editor.property(
            "file_path"
        )

        if not path:

            return self.save_file_as()

        try:

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    editor.toPlainText()
                )

            editor.document().setModified(
                False
            )

            self.update_project_tree()

            self.statusBar().showMessage(
                f"Kaydedildi: {path}"
            )

            return True

        except Exception as e:

            QMessageBox.critical(
                self,
                "Kaydetme Hatası",
                str(e)
            )

            return False

    def save_file_as(self):

        editor = self.current_editor()

        if not editor:
            return False

        language = editor.property(
            "language"
        )

        filters = {
            "Python": "Python (*.py)",
            "C": "C (*.c)",
            "C++": "C++ (*.cpp)",
            "C#": "C# (*.cs)",
            "Java": "Java (*.java)",
            "HTML": "HTML (*.html)",
            "CSS": "CSS (*.css)",
            "JavaScript": "JavaScript (*.js)"
        }

        selected_filter = filters.get(
            language,
            "All Files (*)"
        )

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Dosyayı Kaydet",
            "",
            selected_filter
        )

        if not path:
            return False

        editor.setProperty(
            "file_path",
            path
        )

        detected = detect_language(
            path
        )

        editor.setProperty(
            "language",
            detected
        )

        editor.set_language(
            detected
        )

        result = self.save_file()

        self.update_tab_title(
            editor,
            False
        )

        return result

    # =====================================================
    # TAB
    # =====================================================

    def update_tab_title(
        self,
        editor,
        modified
    ):

        index = self.tabs.indexOf(
            editor
        )

        if index < 0:
            return

        path = editor.property(
            "file_path"
        )

        name = (
            os.path.basename(path)
            if path
            else "Untitled.py"
        )

        if modified:
            name = "*" + name

        self.tabs.setTabText(
            index,
            name
        )

    def close_current_tab(self):

        index = self.tabs.currentIndex()

        if index >= 0:

            self.close_tab(
                index
            )

    def close_tab(self, index):

        editor = self.tabs.widget(
            index
        )

        if editor.document().isModified():

            answer = QMessageBox.question(
                self,
                "Kaydedilmemiş Değişiklik",
                "Bu dosyada kaydedilmemiş değişiklikler var.\n"
                "Kaydetmek istiyor musunuz?",
                QMessageBox.Save |
                QMessageBox.Discard |
                QMessageBox.Cancel
            )

            if answer == QMessageBox.Cancel:
                return

            if answer == QMessageBox.Save:

                self.tabs.setCurrentIndex(
                    index
                )

                if not self.save_file():
                    return

        self.tabs.removeTab(
            index
        )

        editor.deleteLater()

        if self.tabs.count() == 0:
            self.new_file()

    def tab_changed(self, _):

        self.update_status()
        self.update_inspector()

    # =====================================================
    # LANGUAGE
    # =====================================================

    def manual_language_change(
        self,
        language
    ):

        editor = self.current_editor()

        if not editor:
            return

        editor.setProperty(
            "language",
            language
        )

        editor.set_language(
            language
        )

        self.update_inspector()

    # =====================================================
    # PROJECT
    # =====================================================

    def open_project(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Proje Klasörü Seç"
        )

        if not folder:
            return

        self.current_project = folder

        self.project_label.setText(
            "  " + folder
        )

        self.update_project_tree()

        self.terminal.append(
            f"\n$ Proje: {folder}"
        )

        self.statusBar().showMessage(
            f"Proje açıldı: {folder}"
        )

    def update_project_tree(self):

        self.tree.clear()

        if not self.current_project:
            return

        root = QTreeWidgetItem([
            os.path.basename(
                self.current_project
            )
            or self.current_project
        ])

        root.setData(
            0,
            Qt.UserRole,
            self.current_project
        )

        self.tree.addTopLevelItem(
            root
        )

        self.add_directory(
            root,
            self.current_project
        )

        root.setExpanded(
            True
        )

    def add_directory(
        self,
        parent,
        directory
    ):

        try:

            entries = sorted(
                os.listdir(
                    directory
                ),
                key=lambda x: (
                    not os.path.isdir(
                        os.path.join(
                            directory,
                            x
                        )
                    ),
                    x.lower()
                )
            )

        except PermissionError:
            return

        for name in entries:

            if name.startswith("."):
                continue

            path = os.path.join(
                directory,
                name
            )

            if os.path.isdir(path):

                item = QTreeWidgetItem([
                    name
                ])

                item.setData(
                    0,
                    Qt.UserRole,
                    path
                )

                parent.addChild(
                    item
                )

                self.add_directory(
                    item,
                    path
                )

            elif os.path.splitext(
                name
            )[1].lower() in LANGUAGES:

                item = QTreeWidgetItem([
                    name
                ])

                item.setData(
                    0,
                    Qt.UserRole,
                    path
                )

                parent.addChild(
                    item
                )

    def tree_open_file(
        self,
        item,
        column
    ):

        path = item.data(
            0,
            Qt.UserRole
        )

        if (
            path
            and
            os.path.isfile(path)
        ):

            self.open_path(
                path
            )

    def explorer_context_menu(
        self,
        position
    ):

        item = self.tree.itemAt(
            position
        )

        if not item:
            return

        path = item.data(
            0,
            Qt.UserRole
        )

        if not path:
            return

        menu = QMenu(
            self
        )

        open_action = menu.addAction(
            "Aç"
        )

        refresh_action = menu.addAction(
            "Yenile"
        )

        action = menu.exec_(
            self.tree.viewport().mapToGlobal(
                position
            )
        )

        if action == open_action:

            if os.path.isfile(path):
                self.open_path(path)

        elif action == refresh_action:

            self.update_project_tree()

    # =====================================================
    # ÇALIŞTIRMA SİSTEMİ
    # =====================================================

    def get_runtime(self, path):

        ext = os.path.splitext(
            path
        )[1].lower()

        directory = os.path.dirname(
            path
        )

        filename = os.path.basename(
            path
        )

        name_without_ext = os.path.splitext(
            filename
        )[0]

        if ext == ".py":

            return (
                sys.executable,
                [path],
                directory,
                "Python"
            )

        if ext == ".c":

            gcc = shutil.which("gcc")

            if not gcc:
                return None

            output = os.path.join(
                directory,
                name_without_ext
            )

            return (
                gcc,
                [path, "-o", output],
                directory,
                "GCC"
            )

        if ext in (
            ".cpp",
            ".cc",
            ".cxx"
        ):

            gpp = shutil.which("g++")

            if not gpp:
                return None

            output = os.path.join(
                directory,
                name_without_ext
            )

            return (
                gpp,
                [path, "-o", output],
                directory,
                "G++"
            )

        if ext == ".cs":

            dotnet = shutil.which(
                "dotnet"
            )

            if not dotnet:
                return None

            return (
                dotnet,
                [
                    "run",
                    "--project",
                    directory
                ],
                directory,
                ".NET"
            )

        if ext == ".java":

            javac = shutil.which(
                "javac"
            )

            java = shutil.which(
                "java"
            )

            if not javac or not java:
                return None

            return (
                javac,
                [path],
                directory,
                "Java Compiler"
            )

        if ext == ".js":

            node = shutil.which(
                "node"
            )

            if not node:
                return None

            return (
                node,
                [path],
                directory,
                "Node.js"
            )

        if ext in (
            ".html",
            ".htm"
        ):

            browser = self.find_browser()

            if browser:
                return (
                    browser,
                    [path],
                    directory,
                    "Web Browser"
                )

        if ext == ".css":

            return (
                None,
                [],
                directory,
                "CSS"
            )

        return None

    def find_browser(self):

        browsers = [
            "xdg-open",
            "firefox",
            "google-chrome",
            "chromium",
            "chromium-browser"
        ]

        for browser in browsers:

            found = shutil.which(
                browser
            )

            if found:
                return found

        return None

    def run_file(self):

        editor = self.current_editor()

        if not editor:
            return

        path = editor.property(
            "file_path"
        )

        if not path:

            if not self.save_file_as():
                return

            path = editor.property(
                "file_path"
            )

        else:

            if editor.document().isModified():

                if not self.save_file():
                    return

        language = detect_language(
            path
        )

        # Python syntax
        if language == "Python":

            if not self.check_syntax(
                show_panel=False
            ):

                self.bottom_tabs.setCurrentWidget(
                    self.problems
                )

                return

        if self.process:

            QMessageBox.information(
                self,
                "Çalışıyor",
                "Zaten çalışan bir işlem var."
            )

            return

        ext = os.path.splitext(
            path
        )[1].lower()

        # CSS doğrudan çalıştırılamaz
        if ext == ".css":

            self.output.clear()

            self.output.append(
                "CSS dosyası tek başına çalıştırılamaz.\n"
                "HTML projesi içerisinde kullanılmalıdır."
            )

            self.bottom_tabs.setCurrentWidget(
                self.output
            )

            return

        runtime = self.get_runtime(
            path
        )

        if not runtime:

            self.output.clear()

            self.output.append(
                f"{language} için gerekli çalıştırıcı/derleyici bulunamadı.\n\n"
                "Kurulumları kontrol etmek için:\n"
                "Araçlar > Derleyicileri Kontrol Et"
            )

            self.bottom_tabs.setCurrentWidget(
                self.output
            )

            return

        program, arguments, cwd, runtime_name = runtime

        self.output.clear()

        self.output.append(
            f">>> Dil: {language}\n"
            f">>> Çalıştırıcı: {runtime_name}\n"
            f">>> Dosya: {path}\n"
            f">>> Başlatılıyor...\n\n"
        )

        self.bottom_tabs.setCurrentWidget(
            self.output
        )

        # Java compile özel durumu
        if ext == ".java":

            self.compile_java_then_run(
                path,
                cwd
            )

            return

        # C / C++ compile özel durumu
        if ext in (
            ".c",
            ".cpp",
            ".cc",
            ".cxx"
        ):

            self.compile_native_then_run(
                program,
                arguments,
                cwd,
                path
            )

            return

        self.start_process(
            program,
            arguments,
            cwd
        )

    # =====================================================
    # NATIVE COMPILE
    # =====================================================

    def compile_native_then_run(
        self,
        compiler,
        arguments,
        cwd,
        source
    ):

        self.process = QProcess(
            self
        )

        self.process.setProgram(
            compiler
        )

        self.process.setArguments(
            arguments
        )

        self.process.setWorkingDirectory(
            cwd
        )

        self.process.readyReadStandardOutput.connect(
            self.read_stdout
        )

        self.process.readyReadStandardError.connect(
            self.read_stderr
        )

        self.native_source = source

        self.native_cwd = cwd

        self.native_process_stage = True

        self.process.finished.connect(
            self.native_compile_finished
        )

        self.process.start()

    def native_compile_finished(
        self,
        exit_code,
        exit_status
    ):

        if exit_code != 0:

            self.output.append(
                "\n>>> Derleme başarısız."
            )

            self.statusBar().showMessage(
                "Derleme başarısız"
            )

            self.process.deleteLater()

            self.process = None

            return

        self.output.append(
            "\n>>> Derleme başarılı."
        )

        source = self.native_source

        name = os.path.splitext(
            os.path.basename(source)
        )[0]

        executable = os.path.join(
            self.native_cwd,
            name
        )

        if not os.path.exists(
            executable
        ):

            self.output.append(
                "Çalıştırılabilir dosya bulunamadı."
            )

            self.process.deleteLater()

            self.process = None

            return

        self.process.deleteLater()

        self.process = None

        if os.path.isfile(executable):

            self.start_process(
                executable,
                [],
                self.native_cwd
            )

    # =====================================================
    # JAVA
    # =====================================================

    def compile_java_then_run(
        self,
        path,
        cwd
    ):

        javac = shutil.which(
            "javac"
        )

        if not javac:
            return

        self.process = QProcess(
            self
        )

        self.process.setProgram(
            javac
        )

        self.process.setArguments([
            path
        ])

        self.process.setWorkingDirectory(
            cwd
        )

        self.java_path = path
        self.java_cwd = cwd

        self.process.readyReadStandardOutput.connect(
            self.read_stdout
        )

        self.process.readyReadStandardError.connect(
            self.read_stderr
        )

        self.process.finished.connect(
            self.java_compile_finished
        )

        self.process.start()

    def java_compile_finished(
        self,
        exit_code,
        exit_status
    ):

        if exit_code != 0:

            self.output.append(
                "\n>>> Java derleme başarısız."
            )

            self.process.deleteLater()

            self.process = None

            return

        class_name = os.path.splitext(
            os.path.basename(
                self.java_path
            )
        )[0]

        java = shutil.which(
            "java"
        )

        self.output.append(
            "\n>>> Java derleme başarılı."
        )

        self.process.deleteLater()

        self.process = None

        self.start_process(
            java,
            [class_name],
            self.java_cwd
        )

    # =====================================================
    # PROCESS
    # =====================================================

    def start_process(
        self,
        program,
        arguments,
        cwd
    ):

        self.process = QProcess(
            self
        )

        self.process.setProgram(
            program
        )

        self.process.setArguments(
            arguments
        )

        self.process.setWorkingDirectory(
            cwd
        )

        self.process.readyReadStandardOutput.connect(
            self.read_stdout
        )

        self.process.readyReadStandardError.connect(
            self.read_stderr
        )

        self.process.finished.connect(
            self.process_finished
        )

        self.process.errorOccurred.connect(
            self.process_error
        )

        self.process.start()

        self.statusBar().showMessage(
            "Program çalışıyor..."
        )

    def read_stdout(self):

        if not self.process:
            return

        data = self.process.readAllStandardOutput()

        text = bytes(
            data
        ).decode(
            "utf-8",
            errors="replace"
        )

        self.output.insertPlainText(
            text
        )

        self.output.moveCursor(
            QTextCursor.End
        )

    def read_stderr(self):

        if not self.process:
            return

        data = self.process.readAllStandardError()

        text = bytes(
            data
        ).decode(
            "utf-8",
            errors="replace"
        )

        self.output.insertPlainText(
            text
        )

        self.output.moveCursor(
            QTextCursor.End
        )

        self.parse_runtime_errors(
            text
        )

    def parse_runtime_errors(
        self,
        text
    ):

        patterns = [
            r'File ".*?", line (\d+)',
            r':(\d+):',
            r'line (\d+)'
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text
            )

            if match:

                self.problems.clear_problems()

                self.problems.add_problem(
                    "Runtime",
                    match.group(1),
                    text.strip()
                )

                break

    def process_finished(
        self,
        exit_code,
        exit_status
    ):

        self.output.append(
            f"\n\n>>> Program sonlandı."
            f"\n>>> Çıkış kodu: {exit_code}"
        )

        self.statusBar().showMessage(
            f"Program sonlandı: {exit_code}"
        )

        self.process.deleteLater()

        self.process = None

    def process_error(
        self,
        error
    ):

        self.output.append(
            f"\n>>> İşlem hatası: {error}"
        )

    def stop_process(self):

        if self.process:

            self.process.terminate()

            if not self.process.waitForFinished(
                1000
            ):

                self.process.kill()

            self.output.append(
                "\n>>> Program durduruldu."
            )

            self.statusBar().showMessage(
                "Program durduruldu"
            )

    # =====================================================
    # SYNTAX
    # =====================================================

    def check_syntax(
        self,
        show_panel=True
    ):

        editor = self.current_editor()

        if not editor:
            return True

        language = editor.property(
            "language"
        )

        self.problems.clear_problems()

        code = editor.toPlainText()

        # Python
        if language == "Python":

            try:

                ast.parse(
                    code
                )

                self.problems.add_problem(
                    "OK",
                    "-",
                    "Python syntax kontrolü başarılı."
                )

                if show_panel:
                    self.bottom_tabs.setCurrentWidget(
                        self.problems
                    )

                return True

            except SyntaxError as e:

                self.problems.add_problem(
                    "SyntaxError",
                    e.lineno or "-",
                    e.msg
                )

                if show_panel:
                    self.bottom_tabs.setCurrentWidget(
                        self.problems
                    )

                return False

        # Diğer diller
        self.problems.add_problem(
            "INFO",
            "-",
            f"{language} için temel syntax renklendirmesi aktif."
        )

        if show_panel:
            self.bottom_tabs.setCurrentWidget(
                self.problems
            )

        return True

    # =====================================================
    # SEARCH
    # =====================================================

    def find_text(self):

        editor = self.current_editor()

        if not editor:
            return

        text, ok = QInputDialog.getText(
            self,
            "Kod Ara",
            "Aranacak ifade:"
        )

        if not ok or not text:
            return

        if not editor.find(text):

            QMessageBox.information(
                self,
                "Arama",
                "Aranan ifade bulunamadı."
            )

    # =====================================================
    # FONT
    # =====================================================

    def change_font(self):

        editor = self.current_editor()

        if not editor:
            return

        font, ok = QFontDialog.getFont(
            editor.font(),
            self,
            "Editör Fontu"
        )

        if ok:

            editor.setFont(
                font
            )

            editor.setTabStopWidth(
                4 * editor.fontMetrics().width(" ")
            )

            editor.update_line_number_width(
                0
            )

    def zoom_in(self):

        editor = self.current_editor()

        if editor:
            editor.zoom_in()

    def zoom_out(self):

        editor = self.current_editor()

        if editor:
            editor.zoom_out()

    def zoom_reset(self):

        editor = self.current_editor()

        if editor:
            editor.reset_zoom()

    # =====================================================
    # COMPILER CHECK
    # =====================================================

    def check_compilers(self):

        programs = {
            "Python": sys.executable,
            "GCC": "gcc",
            "G++": "g++",
            "C# / .NET": "dotnet",
            "Java Compiler": "javac",
            "Java Runtime": "java",
            "Node.js": "node"
        }

        self.output.clear()

        self.output.append(
            "=== NotStudio Geliştirme Ortamı ===\n"
        )

        for name, program in programs.items():

            if (
                program == sys.executable
                or shutil.which(program)
            ):

                self.output.append(
                    f"[OK] {name}"
                )

            else:

                self.output.append(
                    f"[YOK] {name}"
                )

        self.bottom_tabs.setCurrentWidget(
            self.output
        )

    # =====================================================
    # INSPECTOR
    # =====================================================

    def update_inspector(self):

        editor = self.current_editor()

        if not editor:
            return

        path = editor.property(
            "file_path"
        )

        language = editor.property(
            "language"
        )

        self.info_language.setText(
            f"Dil: {language}"
        )

        self.info_lines.setText(
            f"Satır: {editor.blockCount()}"
        )

        if path:

            self.info_name.setText(
                f"Dosya: {os.path.basename(path)}"
            )

            self.info_path.setText(
                f"Yol: {path}"
            )

            try:

                size = os.path.getsize(
                    path
                )

                self.info_size.setText(
                    f"Boyut: {size:,} byte"
                )

            except OSError:

                self.info_size.setText(
                    "Boyut: -"
                )

            runtime = self.get_runtime(
                path
            )

            if runtime:

                self.info_runtime.setText(
                    f"Çalıştırıcı: {runtime[3]}"
                )

            else:

                self.info_runtime.setText(
                    "Çalıştırıcı: Bulunamadı"
                )

        else:

            self.info_name.setText(
                "Dosya: Untitled"
            )

            self.info_path.setText(
                "Yol: Kaydedilmedi"
            )

            self.info_size.setText(
                "Boyut: -"
            )

            self.info_runtime.setText(
                "Çalıştırıcı: -"
            )

    # =====================================================
    # STATUS
    # =====================================================

    def update_status(self):

        editor = self.current_editor()

        if not editor:
            return

        cursor = editor.textCursor()

        line = cursor.blockNumber() + 1

        column = cursor.columnNumber() + 1

        language = editor.property(
            "language"
        )

        font_size = editor.font().pointSize()

        self.statusBar().showMessage(
            f"Satır {line} | "
            f"Sütun {column} | "
            f"{language} | "
            f"UTF-8 | "
            f"{font_size}pt"
        )

        self.update_inspector()

    # =====================================================
    # CLOSE
    # =====================================================

    def closeEvent(self, event):

        for i in range(
            self.tabs.count() - 1,
            -1,
            -1
        ):

            editor = self.tabs.widget(
                i
            )

            if editor.document().isModified():

                self.tabs.setCurrentIndex(
                    i
                )

                answer = QMessageBox.question(
                    self,
                    "Kaydedilmemiş Dosya",
                    "Kaydedilmemiş değişiklikler var.\n"
                    "Kaydetmek istiyor musunuz?",
                    QMessageBox.Save |
                    QMessageBox.Discard |
                    QMessageBox.Cancel
                )

                if answer == QMessageBox.Cancel:

                    event.ignore()
                    return

                if answer == QMessageBox.Save:

                    if not self.save_file():

                        event.ignore()
                        return

        if self.process:

            self.stop_process()

        event.accept()


# =========================================================
# MAIN
# =========================================================

def main():

    QApplication.setAttribute(
        Qt.AA_EnableHighDpiScaling
    )

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "NotStudio"
    )

    app.setStyle(
        "Fusion"
    )

    window = NotStudio()

    window.show()

    sys.exit(
        app.exec_()
    )


if __name__ == "__main__":
    main()