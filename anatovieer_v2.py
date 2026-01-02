import sys
import os
import re
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsPixmapItem,
    QCheckBox,
    QSlider,
    QPushButton,
    QSplitter,
    QScrollArea,
    QFileDialog,
    QLineEdit,
    QLabel,
    QFrame,
    QMessageBox,
    QStackedWidget,
    QGridLayout,
    QSizePolicy,
)
from PyQt6.QtGui import (
    QPixmap,
    QPainter,
    QColor,
    QWheelEvent,
    QBrush,
    QCursor,
    QFont,
    QIcon,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QSettings, QTimer, QPoint


# --- HELPER FUNCTION: NATURAL SORT ---
def natural_sort_key(s):
    """
    Splits string into numbers and text so that:
    '-1-Body' comes before '-10-Body'
    """
    return [
        int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)
    ]


# --- CONFIGURATION ---
APP_NAME = "AnatoViewer Pro"
VALID_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp")
ORGANIZATION_NAME = "MedicalStudentApps"
DOMAIN_NAME = "AnatoViewer"

# --- THEME ENGINE ---
THEMES = {
    "Dark": {
        "bg_main": "#0f172a",  # Deep Slate
        "bg_side": "#020617",  # Black/Slate
        "bg_card": "#1e293b",  # Card Surface
        "text_main": "#f8fafc",  # White-ish
        "text_sub": "#94a3b8",  # Muted Gray
        "accent": "#6366f1",  # Indigo
        "accent_hover": "#818cf8",
        "folder": "#f59e0b",  # Amber
        "border": "#334155",
        "input": "#1e293b",
        "input_text": "#ffffff",
    },
    "Light": {
        "bg_main": "#f1f5f9",  # Slate 100
        "bg_side": "#ffffff",  # White
        "bg_card": "#ffffff",  # White
        "text_main": "#0f172a",  # Slate 900
        "text_sub": "#64748b",  # Slate 500
        "accent": "#4f46e5",  # Indigo 600
        "accent_hover": "#6366f1",
        "folder": "#d97706",  # Amber 600
        "border": "#e2e8f0",  # Slate 200
        "input": "#ffffff",
        "input_text": "#0f172a",
    },
}


def get_stylesheet(theme_name):
    t = THEMES[theme_name]
    return f"""
    /* --- GLOBAL --- */
    QMainWindow {{ background-color: {t['bg_main']}; }}
    QWidget {{ font-family: 'Segoe UI', 'Roboto', sans-serif; color: {t['text_main']}; font-size: 14px; }}

    /* --- SIDEBAR --- */
    QFrame#Sidebar {{ background-color: {t['bg_side']}; border-right: 1px solid {t['border']}; }}
    QLabel#BrandLabel {{ color: {t['accent']}; font-weight: 900; font-size: 20px; letter-spacing: 1.5px; padding: 20px 10px; text-transform: uppercase; }}
    QLabel#SectionLabel {{ color: {t['text_sub']}; font-weight: 700; font-size: 11px; text-transform: uppercase; padding: 10px 15px; margin-top: 10px; }}

    /* --- BUTTONS --- */
    QPushButton#SidebarBtn {{ text-align: left; padding: 12px 20px; background-color: transparent; color: {t['text_sub']}; border-radius: 6px; margin: 2px 10px; font-weight: 500; border: none; }}
    QPushButton#SidebarBtn:hover {{ background-color: {t['accent']}1a; color: {t['text_main']}; }} /* 1a = 10% alpha */
    QPushButton#SidebarBtn:checked {{ background-color: {t['accent']}; color: white; font-weight: bold; }}

    QPushButton#NavIconBtn {{ background-color: {t['border']}; border-radius: 8px; color: {t['text_main']}; font-weight: bold; border: none; }}
    QPushButton#NavIconBtn:hover {{ background-color: {t['accent']}; color: white; }}
    
    QPushButton#ThemeToggle {{ background-color: transparent; border: 1px solid {t['border']}; border-radius: 15px; color: {t['text_sub']}; }}
    QPushButton#ThemeToggle:hover {{ border: 1px solid {t['accent']}; color: {t['accent']}; }}

    /* --- INPUTS --- */
    QLineEdit {{ background-color: {t['input']}; border: 1px solid {t['border']}; border-radius: 20px; padding: 8px 16px; color: {t['input_text']}; font-size: 13px; }}
    QLineEdit:focus {{ border: 1px solid {t['accent']}; }}
    QLabel#Breadcrumb {{ color: {t['text_sub']}; font-weight: 600; font-size: 14px; }}

    /* --- CARDS --- */
    QFrame#SchemaCard {{ background-color: {t['bg_card']}; border-radius: 12px; border: 1px solid {t['border']}; }}
    QFrame#SchemaCard:hover {{ border: 1px solid {t['accent']}; }}
    
    QFrame#FolderCard {{ background-color: {t['bg_card']}; border-radius: 12px; border: 1px solid {t['border']}; }}
    QFrame#FolderCard:hover {{ border: 1px solid {t['folder']}; }}

    QLabel#CardTitle {{ color: {t['text_main']}; font-weight: 600; font-size: 13px; }}
    QLabel#CardMeta {{ color: {t['text_sub']}; font-size: 11px; }}
    QLabel#CardPath {{ color: {t['text_sub']}; font-size: 10px; font-style: italic; }}

    /* --- EDITOR --- */
    QFrame#Toolbar {{ background-color: {t['bg_side']}; border-bottom: 1px solid {t['border']}; }}
    QPushButton#BackBtn {{ background-color: transparent; color: {t['accent']}; font-weight: bold; border: 1px solid {t['accent']}; border-radius: 4px; padding: 5px 15px; }}
    QPushButton#BackBtn:hover {{ background-color: {t['accent']}; color: white; }}
    
    /* --- SCROLL & SLIDER --- */
    QScrollBar:vertical {{ background: {t['bg_main']}; width: 10px; }}
    QScrollBar::handle:vertical {{ background: {t['border']}; border-radius: 5px; min-height: 40px; }}
    QScrollBar::handle:vertical:hover {{ background: {t['text_sub']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    
    QSlider::groove:horizontal {{ border: 1px solid {t['border']}; height: 4px; background: {t['bg_main']}; border-radius: 2px; }}
    QSlider::handle:horizontal {{ background: {t['accent']}; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }}
    """


# --- CUSTOM WIDGETS ---


class SchemaCard(QFrame):
    clicked = pyqtSignal(str, str, bool)  # Path, Name, Is_Folder

    def __init__(
        self, name, path, is_folder=False, width=160, parent=None, extra_info=None
    ):
        super().__init__(parent)
        self.path = path
        self.name = name
        self.is_folder = is_folder
        self.full_thumb = None
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        if self.is_folder:
            self.setObjectName("FolderCard")
        else:
            self.setObjectName("SchemaCard")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 1. Thumbnail
        self.thumb_container = QLabel()
        self.thumb_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_container.setStyleSheet(
            "background-color: transparent; border-top-left-radius: 12px; border-top-right-radius: 12px;"
        )

        if self.is_folder:
            icon = self.style().standardIcon(self.style().StandardPixmap.SP_DirIcon)
            self.thumb_container.setPixmap(icon.pixmap(64, 64))
        else:
            self.thumb_container.setText("Loading...")
            self.generate_composite_thumbnail()

        self.layout.addWidget(self.thumb_container, 1)

        # 2. Info
        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: transparent; border-top: 1px solid transparent;"
        )
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 8, 10, 8)
        info_layout.setSpacing(2)

        self.name_lbl = QLabel(name)
        self.name_lbl.setObjectName("CardTitle")
        self.name_lbl.setWordWrap(True)
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.name_lbl)

        type_text = "COLLECTION" if is_folder else "SCHEMA"
        self.meta_lbl = QLabel(type_text)
        self.meta_lbl.setObjectName("CardMeta")
        self.meta_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.meta_lbl)

        # Show path if searching (extra_info)
        if extra_info:
            path_lbl = QLabel(extra_info)
            path_lbl.setObjectName("CardPath")
            path_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            path_lbl.setWordWrap(True)
            info_layout.addWidget(path_lbl)

        self.layout.addWidget(info_frame)
        self.set_card_size(width)

    def generate_composite_thumbnail(self):
        try:
            files = [f for f in os.listdir(self.path) if f.lower().endswith(VALID_EXTS)]

            if not files:
                return

            # --- UPDATED SORTING LINE ---
            files.sort(key=natural_sort_key)
            # ----------------------------

            base = QPixmap(os.path.join(self.path, files[0]))
            if base.isNull():
                return

            comp = QPixmap(base.size())
            comp.fill(Qt.GlobalColor.transparent)
            p = QPainter(comp)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.drawPixmap(0, 0, base)

            for f in files[1:]:
                layer = QPixmap(os.path.join(self.path, f))
                if not layer.isNull():
                    p.drawPixmap(0, 0, layer)
            p.end()
            self.full_thumb = comp
            self.update_thumbnail_size()
        except:
            pass

    def set_card_size(self, width):
        height = int(width * 1.3)
        self.setFixedSize(width, height)
        self.update_thumbnail_size()

    def update_thumbnail_size(self):
        if self.is_folder:
            icon_size = int(self.width() * 0.4)
            self.thumb_container.setPixmap(
                self.style()
                .standardIcon(self.style().StandardPixmap.SP_DirIcon)
                .pixmap(icon_size, icon_size)
            )
        elif self.full_thumb:
            target_h = self.height() - 70
            if target_h > 0:
                scaled = self.full_thumb.scaled(
                    self.width() - 20,
                    target_h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.thumb_container.setPixmap(scaled)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.path, self.name, self.is_folder)


class LayerRow(QWidget):
    opacityChanged = pyqtSignal(float)
    visibilityChanged = pyqtSignal(bool)

    def __init__(self, name, pixmap, parent=None):
        super().__init__(parent)
        self.full_pixmap = pixmap

        # --- THE FIX: Correct way to set popup flags ---
        self.preview = QLabel(self)
        self.preview.setWindowFlags(Qt.WindowType.ToolTip)
        self.preview.setStyleSheet(
            "border: 2px solid #6366f1; background-color: black;"
        )
        self.preview.setScaledContents(True)
        self.preview.hide()

        self.thumbnail = None
        if self.full_pixmap and not self.full_pixmap.isNull():
            self.thumbnail = self.full_pixmap.scaled(
                400,
                400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)
        self.checkbox.toggled.connect(self.visibilityChanged.emit)
        layout.addWidget(self.checkbox)

        self.label = QLabel(name)
        layout.addWidget(self.label, 1)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(100)
        self.slider.setFixedWidth(80)
        self.slider.valueChanged.connect(self.update_opacity)
        layout.addWidget(self.slider)

        self.pct_label = QLabel("100%")
        self.pct_label.setFixedWidth(35)
        layout.addWidget(self.pct_label)

    def update_opacity(self, value):
        self.pct_label.setText(f"{value}%")
        self.opacityChanged.emit(value / 100.0)

    def enterEvent(self, event):
        if not self.thumbnail:
            return
        self.preview.setPixmap(self.thumbnail)
        self.preview.resize(self.thumbnail.size())

        # Calculate Position (Left of cursor)
        gp = self.mapToGlobal(QPoint(0, 0))
        self.preview.move(gp.x() - self.thumbnail.width() - 15, gp.y())
        self.preview.show()

    def leaveEvent(self, event):
        self.preview.hide()


class AnatomyCanvas(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        # Background handled by CSS mainly, but for canvas specific:
        self.setBackgroundBrush(QBrush(QColor("#000000")))

    def wheelEvent(self, event: QWheelEvent):
        zoom_in = 1.15
        zoom_out = 1 / 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_in, zoom_in)
        else:
            self.scale(zoom_out, zoom_out)


# --- SCREENS ---


class LibraryScreen(QWidget):
    schemaSelected = pyqtSignal(str, str)
    themeChanged = pyqtSignal(str)  # Emit 'Dark' or 'Light'

    def __init__(self):
        super().__init__()
        self.root_path = ""
        self.current_path = ""
        self.settings = QSettings(ORGANIZATION_NAME, DOMAIN_NAME)
        self.current_theme = self.settings.value("theme", "Dark")
        self.card_size = 180
        self.setup_ui()

        saved_path = self.settings.value("root_path")
        if saved_path and os.path.exists(saved_path):
            self.set_root_library(saved_path)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(15, 30, 15, 30)
        side_layout.setSpacing(5)

        lbl_brand = QLabel("ANATO VIEWER")
        lbl_brand.setObjectName("BrandLabel")
        side_layout.addWidget(lbl_brand)

        lbl_main = QLabel("LIBRARY")
        lbl_main.setObjectName("SectionLabel")
        side_layout.addWidget(lbl_main)

        self.btn_home = self.create_nav_btn("All Content (Root)")
        self.btn_alami = self.create_nav_btn("Prof. Alami")
        self.btn_hammoud = self.create_nav_btn("Prof. Hammoud")
        side_layout.addWidget(self.btn_home)
        side_layout.addWidget(self.btn_alami)
        side_layout.addWidget(self.btn_hammoud)

        side_layout.addStretch()

        # Theme Toggle
        self.btn_theme = QPushButton(f"Theme: {self.current_theme}")
        self.btn_theme.setObjectName("ThemeToggle")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.setFixedHeight(30)
        self.btn_theme.clicked.connect(self.toggle_theme)
        side_layout.addWidget(self.btn_theme)

        # Settings
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #334155;")
        side_layout.addWidget(sep)

        btn_folder = QPushButton("Switch Library Folder")
        btn_folder.setObjectName("SidebarBtn")
        btn_folder.clicked.connect(self.select_root_folder)
        side_layout.addWidget(btn_folder)
        main_layout.addWidget(self.sidebar)

        # 2. Content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 0)
        content_layout.setSpacing(20)

        header_layout = QHBoxLayout()
        self.btn_back = QPushButton("←")
        self.btn_back.setObjectName("NavIconBtn")
        self.btn_back.setFixedSize(36, 36)
        self.btn_back.clicked.connect(self.go_up_level)
        header_layout.addWidget(self.btn_back)

        self.lbl_path = QLabel("Select a Root Folder")
        self.lbl_path.setObjectName("Breadcrumb")
        header_layout.addWidget(self.lbl_path)
        header_layout.addStretch()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Universal Search...")
        self.search_bar.setFixedWidth(280)
        self.search_bar.textChanged.connect(self.on_search_text_changed)
        header_layout.addWidget(self.search_bar)

        header_layout.addSpacing(10)
        btn_zoom_out = QPushButton("−")
        btn_zoom_out.setObjectName("NavIconBtn")
        btn_zoom_out.setFixedSize(36, 36)
        btn_zoom_out.clicked.connect(lambda: self.change_zoom(-20))
        header_layout.addWidget(btn_zoom_out)
        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setObjectName("NavIconBtn")
        btn_zoom_in.setFixedSize(36, 36)
        btn_zoom_in.clicked.connect(lambda: self.change_zoom(20))
        header_layout.addWidget(btn_zoom_in)
        content_layout.addLayout(header_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self.grid_layout.setSpacing(25)
        scroll.setWidget(self.grid_container)
        content_layout.addWidget(scroll)
        main_layout.addWidget(content_widget)

    def create_nav_btn(self, text):
        btn = QPushButton(text)
        btn.setObjectName("SidebarBtn")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.handle_sidebar_click(text))
        return btn

    def toggle_theme(self):
        new_theme = "Light" if self.current_theme == "Dark" else "Dark"
        self.current_theme = new_theme
        self.settings.setValue("theme", new_theme)
        self.btn_theme.setText(f"Theme: {new_theme}")
        self.themeChanged.emit(new_theme)

    def set_root_library(self, path):
        self.root_path = path
        self.settings.setValue("root_path", path)
        self.navigate_to(path)

    def select_root_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Root")
        if folder:
            self.set_root_library(folder)

    def handle_sidebar_click(self, text):
        self.search_bar.clear()  # Clear search when nav button clicked
        self.btn_home.setChecked(False)
        self.btn_alami.setChecked(False)
        self.btn_hammoud.setChecked(False)
        sender = self.sender()
        if sender:
            sender.setChecked(True)

        if text == "All Content (Root)":
            self.navigate_to(self.root_path)
        elif text == "Prof. Alami":
            p = os.path.join(self.root_path, "Partie Prof Alami")
            if os.path.exists(p):
                self.navigate_to(p)
        elif text == "Prof. Hammoud":
            p = os.path.join(self.root_path, "Partie Prof Hammoud")
            if os.path.exists(p):
                self.navigate_to(p)

    def navigate_to(self, path):
        self.current_path = path
        if not self.root_path:
            return
        rel = os.path.relpath(path, self.root_path)
        disp = "Root Library" if rel == "." else f"Root > {rel.replace(os.sep, ' > ')}"
        self.lbl_path.setText(disp)
        self.btn_back.setEnabled(path != self.root_path)
        self.btn_back.setStyleSheet(
            "opacity: 1;" if path != self.root_path else "opacity: 0.3;"
        )
        self.populate_grid(path)

    def on_search_text_changed(self, text):
        if not text:
            # Revert to normal view of current path
            self.navigate_to(self.current_path)
            return

        # SEARCH MODE
        self.lbl_path.setText(f"Searching for '{text}' in entire library...")
        self.btn_back.setEnabled(False)
        self.perform_universal_search(text)

    def perform_universal_search(self, query):
        """Recursive deep dive search."""
        query = query.lower()
        results = []

        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Walk entire root
        for root, dirs, files in os.walk(self.root_path):
            folder_name = os.path.basename(root)

            # 1. Check if the FOLDER itself matches and is a Schema or Collection
            # Logic: If folder name matches query
            if query in folder_name.lower():
                # Is it a schema?
                has_images = any(f.lower().endswith(VALID_EXTS) for f in files)
                if has_images:
                    results.append(
                        (folder_name, root, False)
                    )  # Name, Path, IsFolder=False (It's a schema)
                elif any(os.path.isdir(os.path.join(root, d)) for d in dirs):
                    results.append(
                        (folder_name, root, True)
                    )  # Name, Path, IsFolder=True (It's a collection)

        # Create cards for results
        cards = []
        for name, path, is_folder in results:
            # Calculate relative path for context
            rel_path = os.path.relpath(path, self.root_path)
            card = SchemaCard(
                name,
                path,
                is_folder=is_folder,
                width=self.card_size,
                extra_info=rel_path,
            )
            card.clicked.connect(self.on_card_clicked)
            cards.append(card)

        self.current_cards = cards
        self.reflow_grid(cards)

    def go_up_level(self):
        if self.current_path != self.root_path:
            self.navigate_to(os.path.dirname(self.current_path))

    def on_card_clicked(self, path, name, is_folder):
        if is_folder:
            self.search_bar.clear()  # Clear search to enter folder normally
            self.navigate_to(path)
        else:
            self.schemaSelected.emit(path, name)

    def populate_grid(self, folder_path):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            entries = list(os.scandir(folder_path))
        except:
            return

        # --- UPDATED SORTING LINE ---
        # Sorts by name using the natural number logic
        entries.sort(key=lambda e: natural_sort_key(e.name))
        # ----------------------------

        cards = []
        for entry in entries:
            if not entry.is_dir():
                continue
            # ... (rest of logic remains exactly the same) ...
            sub_files = os.listdir(entry.path)
            has_images = any(f.lower().endswith(VALID_EXTS) for f in sub_files)
            has_subdirs = any(
                os.path.isdir(os.path.join(entry.path, x)) for x in sub_files
            )

            card = None
            if has_images:
                card = SchemaCard(
                    entry.name, entry.path, is_folder=False, width=self.card_size
                )
            elif has_subdirs:
                card = SchemaCard(
                    entry.name, entry.path, is_folder=True, width=self.card_size
                )

            if card:
                card.clicked.connect(self.on_card_clicked)
                cards.append(card)

        self.current_cards = cards
        self.reflow_grid(cards)

    def change_zoom(self, amount):
        self.card_size = max(120, min(400, self.card_size + amount))
        for i in range(self.grid_layout.count()):
            w = self.grid_layout.itemAt(i).widget()
            if isinstance(w, SchemaCard):
                w.set_card_size(self.card_size)
        self.reflow_grid(self.current_cards)

    def reflow_grid(self, cards):
        while self.grid_layout.count():
            self.grid_layout.takeAt(0)
        container_width = self.width() - 320
        max_cols = max(1, int(container_width / (self.card_size + 25)))
        row, col = 0, 0
        for card in cards:
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def resizeEvent(self, event):
        if hasattr(self, "current_cards"):
            self.reflow_grid(self.current_cards)
        super().resizeEvent(event)


class EditorScreen(QWidget):
    backClicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        toolbar = QFrame()
        toolbar.setObjectName("Toolbar")
        toolbar.setFixedHeight(60)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(20, 0, 20, 0)
        btn_back = QPushButton("← Back")
        btn_back.setObjectName("BackBtn")
        btn_back.clicked.connect(self.backClicked.emit)
        tb_layout.addWidget(btn_back)
        self.lbl_title = QLabel("Editor")
        self.lbl_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-left: 20px;"
        )
        tb_layout.addWidget(self.lbl_title)
        tb_layout.addStretch()
        layout.addWidget(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #334155; }")
        self.scene = QGraphicsScene()
        self.view = AnatomyCanvas(self.scene)
        splitter.addWidget(self.view)

        layers_panel = QFrame()
        layers_panel.setObjectName("Sidebar")
        layers_panel.setFixedWidth(300)
        lp_layout = QVBoxLayout(layers_panel)
        lp_layout.addWidget(QLabel("LAYERS", objectName="SectionLabel"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        self.layers_container = QWidget()
        self.layers_layout = QVBoxLayout(self.layers_container)
        self.layers_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.layers_container)
        lp_layout.addWidget(scroll)
        btn_reset = QPushButton("Reset View")
        btn_reset.setObjectName("SidebarBtn")
        btn_reset.clicked.connect(self.reset_view)
        lp_layout.addWidget(btn_reset)
        splitter.addWidget(layers_panel)
        layout.addWidget(splitter)

    def load_schema(self, path, name):
        self.lbl_title.setText(name)
        self.scene.clear()

        while self.layers_layout.count():
            child = self.layers_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        files = [f for f in os.listdir(path) if f.lower().endswith(VALID_EXTS)]

        # --- UPDATED SORTING LINE ---
        files.sort(key=natural_sort_key)
        # ----------------------------

        for i, filename in enumerate(files):
            full_path = os.path.join(path, filename)
            pixmap = QPixmap(full_path)
            if pixmap.isNull():
                continue

            # Z-Value: Lower Number (-1-) gets lower Z (Background)
            item = QGraphicsPixmapItem(pixmap)
            item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            item.setZValue(i)
            self.scene.addItem(item)

            clean_name = os.path.splitext(filename)[0].replace("_", " ").title()

            row = LayerRow(clean_name, pixmap)
            row.visibilityChanged.connect(lambda v, itm=item: itm.setVisible(v))
            row.opacityChanged.connect(lambda o, itm=item: itm.setOpacity(o))

            # Insert at 0 (Top of List) so higher numbers (Top Layers) appear at top of sidebar
            self.layers_layout.insertWidget(0, row)

        self.reset_view()

    def reset_view(self):
        if self.scene.items():
            # Get the bounding rect of all items in the scene
            rect = self.scene.itemsBoundingRect()
            # Fit the view to this rect, keeping aspect ratio
            self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
            # Zoom out slightly (90%) so it's not touching the edges
            self.view.scale(0.9, 0.9)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 850)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.library = LibraryScreen()
        self.editor = EditorScreen()
        self.stack.addWidget(self.library)
        self.stack.addWidget(self.editor)

        self.library.schemaSelected.connect(self.open_editor)
        self.editor.backClicked.connect(self.open_library)
        self.library.themeChanged.connect(self.apply_theme)

        # Initial Theme Apply
        self.apply_theme(self.library.current_theme)

    def apply_theme(self, theme_name):
        app = QApplication.instance()
        app.setStyleSheet(get_stylesheet(theme_name))

        # Hack to force update specific colors that might lag
        bg = THEMES[theme_name]["bg_side"]
        if self.stack.currentIndex() == 1:
            self.editor.view.setBackgroundBrush(
                QBrush(QColor(THEMES[theme_name]["bg_main"]))
            )

    def open_editor(self, path, name):
        self.editor.load_schema(path, name)
        self.stack.setCurrentIndex(1)
        # Ensure canvas background matches theme
        self.editor.view.setBackgroundBrush(
            QBrush(QColor(THEMES[self.library.current_theme]["bg_main"]))
        )

    def open_library(self):
        self.stack.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
